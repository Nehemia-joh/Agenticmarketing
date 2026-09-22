#!/usr/bin/env python3
"""Link, score and classify the consolidated welfare research (offline, deterministic).

Reads runtime/welfare/<run-id>/{consolidated.json, nis_classified.json}, the run's links.json and the company master
(read-only, for IDs and warm paths). Writes runtime/welfare/<run-id>/final.json.
- NGO register rows link to researched records by exact registration number, exact name or a reviewed manual link;
  unmatched child-welfare NGOs are added as register-only records; similar names go to review.
- Contacts merge only on exact person/role or email within one organisation; personal-domain emails of named people
  are always pdpa_risk "risky".
- Scores and proposed tracks follow plans/b2b-welfare-leads-plan.md section 5.4.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sqlite3
from collections import Counter, defaultdict

import welfare_lib as W

OTHER_SECTOR = re.compile(r"water|rain|conservation|environment|legal|paralegal|sheria|travel|library|books|\bict\b|technology|digital|"
                          r"wildlife|climate|farm|agri|entrepreneur|stroke|elderly|aged|widow|human rights", re.I)


def segment_from_text(text: str) -> tuple[str, str, str]:
    t = text.lower()
    if re.search(r"street child|watoto wa mitaani|mitaani", t):
        return "Welfare specialised centre", "street-children centre", "specialised"
    if re.search(r"disab|ulemavu|deaf|blind|autis|albin|rehabilitat|special needs|mental", t):
        return "Welfare specialised centre", "disability or rehabilitation centre", "specialised"
    if re.search(r"rescue|safe house|nyumba salama", t):
        return "Welfare specialised centre", "rescue or safe house", "specialised"
    if re.search(r"orphanage|children'?s home|childrens home|baby home|makao|children'?s village|\bhome\b|kituo cha kulelea", t):
        return "Welfare residential care", "children's home or orphanage (registry name)", "residential"
    if re.search(r"sponsor|ovc|vulnerable|orphan|yatima|foster|kinship|needy", t):
        return "Welfare family-based programme", "orphans and vulnerable children support", "family_based"
    return "Welfare (unclassified child-focused NGO)", "child-focused NGO", ""


def score(org: dict) -> tuple[int, int, str]:
    """Plan rubric (plans/b2b-welfare-leads-plan.md section 5.4). Returns (score, factors_known_of_6, tier)."""
    pts, known = 0, 0
    n = org.get("children_served_published")
    try:
        n = int(str(n).split()[0]) if n not in (None, "") else None
    except ValueError:
        n = None
    if n is not None:
        known += 1
        base = 30 if n >= 50 else 22 if n >= 20 else 15 if n >= 10 else 8
        evidence = str(org.get("children_served_evidence", "")).lower()
        if re.search(r"national|nationwide|across tanzania|countrywide|\bcountry\b", evidence):
            base = 10  # a national total says little about places near a campus
        elif re.search(r"cumulative|since \d{4}|have benefited|has benefited|to date|in total|over the years|since (founding|inception)|\d[\d,]*\+? since", evidence):
            base = base // 2  # a cumulative count is not current capacity
        pts += base
    sched = f"{org.get('schooling_arrangement_published', '')} {org.get('runs_own_school', '')}".lower()
    if org.get("runs_own_school") == "yes":
        known += 1
    elif re.search(r"private|english[- ]medium|boarding school|sponsor|fees", sched):
        known += 1
        pts += 20
    elif re.search(r"public|government|local (primary|school)|nearby school|community school", sched):
        known += 1
        pts += 10
    ages = str(org.get("age_range_published", "")).lower()
    if ages:
        known += 1
        nums = [int(x) for x in re.findall(r"\d+", ages)]
        if "baby" in ages or "infant" in ages or (nums and min(nums) <= 6):
            pts += 15
        elif nums and min(nums) <= 14:
            pts += 8
    km = org.get("distance_km")
    if km is not None and org.get("geocode_precision") not in ("", "town", None):
        known += 1
        pts += 15 if km <= 5 else 12 if km <= 10 else 9 if km <= 15 else 6 if km <= 20 else 3 if km <= 25 else 0
    if org.get("_named_contacts"):
        known += 1
        pts += 10
    elif org.get("public_emails") or org.get("public_phones"):
        known += 1
        pts += 5
    if org.get("_warm_path"):
        known += 1
        pts += 10
    elif org.get("known_funders_or_partners"):
        known += 1
        pts += 5
    return pts, known, "P1" if pts >= 60 else "P2" if pts >= 40 else "P3" if pts >= 20 else "P4"


def proposed_track(org: dict) -> tuple[str, str]:
    reasons = []
    if org.get("segment", "").startswith("Out of scope"):
        return "Excluded", "Out of scope: " + (org.get("notes") or org.get("subtype") or "")[:120]
    if org.get("verification_status") in ("unverified", "historical"):
        reasons.append(f"evidence {org.get('verification_status')}")
    if not (org.get("public_emails") or org.get("public_phones") or org.get("website") or org.get("social_media")):
        reasons.append("no published contact route")
    km = org.get("distance_km")
    if org.get("segment") == "Welfare funder":
        if not org.get("_funds_in_catchment"):
            reasons.append("no verified link to an institution or children in the catchment")
    elif km is None:
        reasons.append("location unresolved")
    elif km > 25:
        reasons.append("outside 25 km catchment")
    elif org.get("geocode_precision") == "town" and km + 8 > 25:
        reasons.append("location known only to town level and the town straddles the 25 km line")
    if org.get("red_flags"):
        reasons.append("red flags to review")
    if reasons:
        return "WA00 Hold", "; ".join(reasons)
    return "WA01 Routing", "Route usable; decision-maker and licence status still to confirm (WA02 needs authority licence confirmation)"


def reg_tokens(text: str) -> set[str]:
    return {re.sub(r"\s+", "", t).upper().replace("NG0", "NGO") for t in re.findall(r"(?:\d{2}|I-|N-)\s*NG[O0]\s*/[\w/]+", str(text or ""), re.I)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    work, today = cfg["paths"]["work"], cfg["research_date"]
    data = json.loads((work / "consolidated.json").read_text(encoding="utf-8"))
    orgs, contacts, relations, enquiries, reviews = (data[k] for k in ("organisations", "contacts", "relationships", "enquiries", "reviews"))
    nis = json.loads((work / "nis_classified.json").read_text(encoding="utf-8")) if (work / "nis_classified.json").exists() else []
    links = W.load_links(cfg)
    campuses = W.load_campuses()
    con = sqlite3.connect(f"file:{W.MASTER.as_posix()}?mode=ro", uri=True)
    master = {W.name_key(n): (oid, n, seg) for oid, n, seg in con.execute("SELECT organisation_id, name, segment FROM organisations")}
    con.close()
    corporate_funders = {W.name_key(n) for n in links.get("corporate_funders_in_master", [])}

    by_key = {}
    for o in orgs:
        by_key[W.name_key(o["organisation_name"])] = o
        for a in o.get("alternative_names", []):
            by_key.setdefault(W.name_key(a), o)
    for alias, target in links.get("org_aliases", {}).items():
        if W.name_key(target) in by_key:
            by_key[W.name_key(alias)] = by_key[W.name_key(target)]

    # NGO register: exact registration number, exact name or reviewed manual link; otherwise add child-welfare NGOs
    by_reg = {}
    for o in orgs:
        for t in reg_tokens(o.get("registration_published")) | reg_tokens(o.get("notes")):
            by_reg.setdefault(t, o)
    nis_rows = []
    for r in nis:
        key = W.name_key(r["name"])
        reg = next(iter(reg_tokens(r.get("reg_no"))), "")
        target = (by_reg.get(reg) if reg else None) or by_key.get(key) or by_key.get(W.name_key(links.get("nis_to_org", {}).get(str(r["nis_id"]), "")))
        r["matched_organisation"] = target["organisation_name"] if target else ""
        other_sector = bool(OTHER_SECTOR.search(r["name"])) and r["welfare_relevance"] != "strong"
        r["welfare_fit"] = "likely" if r["welfare_relevance"] == "strong" else "possible" if r["welfare_relevance"] == "medium" and not other_sector else "unlikely"
        if target:
            target.setdefault("nis", []).append(r)
        elif r["welfare_fit"] in ("likely", "possible") and str(r["nis_id"]) not in links.get("nis_exclude", []):
            seg, sub, model = segment_from_text(f"{r['name']} {r['vision']}")
            new = {"organisation_name": r["name"].strip(), "alternative_names": [], "segment": seg, "subtype": sub, "care_model": model,
                   "description": r["vision"][:300], "registration_published": r["reg_no"], "district": r["district"], "region": r["region"],
                   "latitude": float(r["latitude"]) if r.get("latitude") else None, "longitude": float(r["longitude"]) if r.get("longitude") else None,
                   "geocode_basis": "NGO register map pin (self-reported)", "public_emails": [], "public_phones": [], "social_media": {},
                   "services": [], "red_flags": [], "known_funders_or_partners": [], "foreign_charity_registrations": [],
                   "sources": [{"url": r["profile_url"], "title": "NGOs Information System profile", "source_date": r.get("reg_date", ""),
                                "accessed_on": today, "evidence_basis": "official", "fetched": r["profile_fetched"],
                                "facts_supported": ["name", "registration", "district", "vision"],
                                "evidence_excerpt": f"Registered NGO {r['reg_no']} ({r['level']}), {r['district']} district; registry vision mentions {r['relevance_signal']}."}],
                   "verification_status": "needs_review", "pdpa_risk": "low", "pdpa_risk_reason": "Organisation-level registry data only.",
                   "notes": f"Found only in the NGO register (relevance {r['welfare_relevance']}: '{r['relevance_signal']}'). Confirm it runs a child-welfare programme and find a published route.",
                   "latest_activity_date": r.get("latest_project_end", ""), "latest_activity_evidence": "Latest project end date listed in the NGO register" if r.get("latest_project_end") else "",
                   "runs_own_school": "unknown", "volunteer_programme": "unknown", "slices": ["NIS"], "members": [f"nis:{r['nis_id']}"], "nis": [r],
                   "welfare_fit": r["welfare_fit"], "conflicts": {}}
            orgs.append(new)
            by_key[key] = new
            r["matched_organisation"] = new["organisation_name"] + " (added from register)"
        nis_rows.append(r)

    researched = [o for o in orgs if not set(o.get("slices", [])) <= {"NIS", "OSM"}]
    for o in orgs:
        if set(o.get("slices", [])) != {"NIS"}:
            continue
        k = W.name_key(o["organisation_name"])
        for other in researched:
            k2 = W.name_key(other["organisation_name"])
            ta, tb = set(k.split()), set(k2.split())
            ratio = difflib.SequenceMatcher(None, k, k2).ratio()
            if ratio >= 0.85 or ((ta & tb) - W.GENERIC_TOKENS and ratio >= 0.6):
                reviews.append({"kind": "possible_duplicate_registry", "entity": o["organisation_name"], "related": other["organisation_name"],
                                "detail": {"sequence_ratio": round(ratio, 2), "nis_reg_no": o.get("registration_published", ""),
                                           "researched_registration": other.get("registration_published", "")},
                                "action": "Register entry may be the researched organisation under another name; link via links.json nis_to_org only on a supported match."})

    # OpenStreetMap features (reviewed links in links.json; unmatched welfare features added)
    for key_name, osm in links.get("osm", {}).items():
        target = by_key.get(W.name_key(osm.get("organisation") or key_name))
        source = {"url": f"https://www.openstreetmap.org/{osm['osm_id']}", "title": f"OpenStreetMap: {key_name}", "source_date": osm.get("check_date", ""),
                  "accessed_on": today, "evidence_basis": "directory", "fetched": True, "facts_supported": ["location"], "evidence_excerpt": osm.get("tags", "")[:140]}
        if target:
            if target.get("geocode_precision") != "point":
                target["latitude"], target["longitude"] = osm["lat"], osm["lon"]
                target["geocode_basis"], target["geocode_precision"] = f"OpenStreetMap {osm['osm_id']} ({key_name})", "point"
            target["osm_id"] = osm["osm_id"]
            target.setdefault("sources", []).append(source)
        elif osm.get("add_if_missing"):
            seg, sub, model = segment_from_text(key_name + " " + osm.get("tags", ""))
            new = {"organisation_name": key_name, "alternative_names": [], "segment": seg, "subtype": sub, "care_model": model, "description": "",
                   "latitude": osm["lat"], "longitude": osm["lon"], "geocode_basis": f"OpenStreetMap {osm['osm_id']}", "geocode_precision": "point",
                   "osm_id": osm["osm_id"], "operator_or_umbrella": osm.get("operator", ""), "public_emails": [], "public_phones": [], "social_media": {},
                   "services": [], "red_flags": [], "known_funders_or_partners": [], "foreign_charity_registrations": [],
                   "sources": [{**source, "facts_supported": ["name", "location"]}], "verification_status": "unverified", "pdpa_risk": "low",
                   "pdpa_risk_reason": "Organisation-level map data only.", "notes": "Found only on OpenStreetMap; confirm it operates and find a route.",
                   "runs_own_school": "unknown", "volunteer_programme": "unknown", "slices": ["OSM"], "members": [f"osm:{osm['osm_id']}"], "conflicts": {}}
            orgs.append(new)
            by_key[W.name_key(key_name)] = new

    # geography, identifiers and master cross-reference
    for o in orgs:
        lat, lon = o.get("latitude"), o.get("longitude")
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            lat = lon = None
        if lat is not None and not (-4.5 < lat < -2.0 and 35.0 < lon < 38.5) and o.get("segment") != "Welfare funder":
            reviews.append({"kind": "geocode_outlier", "entity": o["organisation_name"], "detail": {"lat": lat, "lon": lon},
                            "action": "Check the location; coordinates fall outside northern Tanzania."})
        if lat is not None:
            dists = {c: round(W.hav(lat, lon, *xy), 1) for c, xy in campuses.items()}
            nearest = min(dists, key=dists.get)
            prim = min((c for c in dists if c in W.PRIMARY_CAMPUSES), key=dists.get)
            o.update({"latitude": lat, "longitude": lon, "nearest_campus": nearest, "distance_km": dists[nearest], "nearest_campus_levels": W.LEVELS.get(nearest, ""),
                      "nearest_primary_campus": prim, "distance_to_primary_km": dists[prim], "transport_band": W.band(dists[nearest]), "km_by_campus": dists})
            if not o.get("geocode_precision"):
                o["geocode_precision"] = "registry" if "register" in str(o.get("geocode_basis", "")) else "reported"
        else:
            o.update({"nearest_campus": "", "distance_km": None, "nearest_campus_levels": "", "nearest_primary_campus": "", "distance_to_primary_km": None,
                      "transport_band": "unknown", "km_by_campus": {}})
        o["record_key"] = "WORG_" + re.sub(r"[^a-z0-9]+", "_", W.name_key(o["organisation_name"]))[:48].strip("_")
        mk = master.get(W.name_key(o["organisation_name"])) or next((master.get(W.name_key(a)) for a in o.get("alternative_names", []) if master.get(W.name_key(a))), None)
        o["master_organisation_id"] = links.get("master_ids", {}).get(o["organisation_name"]) or (mk[0] if mk else "")
        if o.get("nis"):
            first = o["nis"][0]
            o.update({"nis_id": first["nis_id"], "nis_reg_no": first["reg_no"], "nis_reg_date": first["reg_date"], "nis_level": first["level"],
                      "nis_district": first["district"], "nis_profile_url": first["profile_url"], "nis_latest_project_end": first.get("latest_project_end", "")})

    # contacts: link to organisations, merge exact duplicates, enforce the risk rubric, flag similar names
    contact_rows = []
    for c in contacts:
        target = by_key.get(W.name_key(c.get("organisation_name")))
        if not target:
            cands = difflib.get_close_matches(W.name_key(c.get("organisation_name")), list(by_key), n=1, cutoff=0.8)
            target = by_key.get(cands[0]) if cands else None
            reviews.append({"kind": "contact_organisation_match", "entity": c.get("contact_name") or c.get("role"), "related": c.get("organisation_name"),
                            "detail": {"closest": target["organisation_name"] if target else ""}, "action": "Confirm which organisation this contact belongs to."})
        c["organisation_key"] = target["record_key"] if target else ""
        c["linked_organisation"] = target["organisation_name"] if target else c.get("organisation_name")
        if target and c.get("contact_name") and c.get("role_certainty") in ("confirmed", "role_desk", None, ""):
            target["_named_contacts"] = True
        c["emails"] = sorted({e for e in map(W.norm_email, W.as_list(c.get("emails"))) if e})
        c["phones"] = sorted({W.norm_phone(p) for p in W.as_list(c.get("phones")) if W.norm_phone(p)})
        contact_rows.append(c)
    merged_contacts, index = [], {}
    for c in contact_rows:
        keys = [(c["organisation_key"], "who", W.name_key(c.get("contact_name")) or "role:" + W.name_key(c.get("role")))]
        keys += [(c["organisation_key"], "email", e) for e in c["emails"]]
        hit = next((index[k] for k in keys if k in index), None)
        if hit is None:
            merged_contacts.append(c)
            for k in keys:
                index[k] = c
            continue
        hit["emails"] = sorted(set(hit["emails"]) | set(c["emails"]))
        hit["phones"] = sorted(set(hit["phones"]) | set(c["phones"]))
        hit["sources"] = W.as_list(hit.get("sources")) + [s for s in W.as_list(c.get("sources")) if s not in W.as_list(hit.get("sources"))]
        hit["verification_status"] = W.best_verification([hit.get("verification_status"), c.get("verification_status")])
        hit["pdpa_risk"] = max((hit.get("pdpa_risk") or "medium", c.get("pdpa_risk") or "medium"), key=lambda r: W.RISK_RANK.get(r, 1))
        hit["notes"] = " | ".join(x for x in (hit.get("notes"), c.get("notes")) if x)
        for field in ("contact_name", "role", "profile_url", "channel_attribution", "email_type", "phone_type"):
            hit[field] = hit.get(field) or c.get(field)
        for k in keys:
            index.setdefault(k, hit)
    contact_rows = merged_contacts
    for c in contact_rows:
        if c.get("contact_name") and any(W.PERSONAL_EMAIL.search(e) for e in c["emails"]) and c.get("pdpa_risk") != "risky":
            c["pdpa_risk"] = "risky"
            c["pdpa_risk_reason"] = "Named individual on a personal email domain (" + ", ".join(e for e in c["emails"] if W.PERSONAL_EMAIL.search(e)) + "); rubric sets risky."
    by_org = defaultdict(list)
    for c in contact_rows:
        if c.get("contact_name"):
            by_org[c["organisation_key"]].append(c)
    for people in by_org.values():
        for i in range(len(people)):
            for j in range(i + 1, len(people)):
                a, b = W.name_key(people[i]["contact_name"]), W.name_key(people[j]["contact_name"])
                ta, tb = set(a.split()), set(b.split())
                if ta and tb and (ta <= tb or tb <= ta or difflib.SequenceMatcher(None, a, b).ratio() >= 0.85):
                    reviews.append({"kind": "possible_duplicate_contact", "entity": people[i]["contact_name"], "related": people[j]["contact_name"],
                                    "detail": {"organisation": people[i].get("linked_organisation")},
                                    "action": "Likely the same person; keep one contact and merge the routes after checking the source."})

    # relationships: warm paths from company leads and funders active in the catchment
    for r in relations:
        src, dst = W.name_key(r.get("from_organisation")), W.name_key(r.get("to_organisation"))
        r["from_key"] = by_key[src]["record_key"] if src in by_key else ""
        r["to_key"] = by_key[dst]["record_key"] if dst in by_key else ""
        r["from_in_master"] = master.get(src, ("",))[0]
        if dst in by_key and (src in corporate_funders or r["from_in_master"]):
            by_key[dst]["_warm_path"] = True
        if src in by_key and dst in by_key:
            d = by_key[dst]
            if d.get("segment") != "Welfare funder" and d.get("distance_km") is not None and d["distance_km"] <= 25:
                by_key[src]["_funds_in_catchment"] = True

    for o in orgs:
        o.setdefault("welfare_fit", "out of scope" if str(o.get("segment", "")).startswith("Out of scope") else "likely")
        o["priority_score"], o["factors_known"], o["priority_band"] = score(o)
        o["proposed_track"], o["track_reason"] = proposed_track(o)
        o["licence_status"] = "not_checked"
    for e in enquiries:
        e["enquiry_key"] = "WENQ_" + re.sub(r"[^a-z0-9]+", "_", (W.name_key(e.get("enquiry_author_display")) or "anon") + "_" + str(e.get("enquiry_date", "")))[:48]
        e["pdpa_risk"] = "risky"

    orgs.sort(key=lambda o: (o["proposed_track"] == "Excluded", -o["priority_score"], o.get("distance_km") or 99, o["organisation_name"]))
    (work / "final.json").write_text(json.dumps({"organisations": orgs, "contacts": contact_rows, "relationships": relations, "enquiries": enquiries,
                                                  "reviews": reviews, "nis": nis_rows}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"organisations": len(orgs), "contacts": len(contact_rows), "relationships": len(relations), "enquiries": len(enquiries),
                      "reviews": len(reviews), "nis_rows": len(nis_rows), "by_segment": Counter(o["segment"] for o in orgs),
                      "by_track": Counter(o["proposed_track"] for o in orgs), "by_tier": Counter(o["priority_band"] for o in orgs)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
