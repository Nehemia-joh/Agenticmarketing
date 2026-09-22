#!/usr/bin/env python3
"""Export the built welfare run to the shared intake contract, interim tables and the raw-evidence manifest.

Reads runtime/welfare/<run-id>/final.json. Writes:
- data/runs/<run-id>/intake.csv (every contract column plus welfare extra columns; the create skill's validator
  accepts extra columns and the initializer keeps them in source_records.payload_json)
- data/interim/welfare-leads/*.tsv (organisations, contacts, relationships, NGO register)
- runtime/welfare/<run-id>/review_items.json (loaded into the run database by augment_run_db.py)
- data/raw/welfare-research/MANIFEST.md (hashes of every raw evidence file)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter

import welfare_lib as W

ALLOWED_BASIS = {"official", "published", "public_profile", "public_post", "directory", "reference_file", "research_note"}
PRECISION = {"point": "address", "locality": "locality", "registry": "estimated", "town": "estimated", "reported": "estimated", "": ""}
EXTRA = ["lead_track", "record_key", "welfare_fit", "care_model", "pdpa_risk", "pdpa_risk_reason", "proposed_welfare_track", "track_reason",
         "priority_score", "factors_known", "children_served_published", "children_served_as_of", "age_range_published", "gender_served",
         "schooling_arrangement_published", "runs_own_school", "funding_model_published", "registration_published", "nis_reg_no",
         "nis_reg_date", "nis_profile_url", "licence_status", "operator_or_umbrella", "religious_affiliation_published", "services",
         "known_funders_or_partners", "foreign_charity_registrations", "social_media", "all_emails", "all_phones", "volunteer_programme",
         "volunteer_fee_published", "safeguarding_policy_url", "staff_count_published", "latest_activity_date", "red_flags",
         "catchment_note", "master_organisation_id", "nearest_primary_campus", "distance_to_primary_km", "all_sources_json",
         "email_type", "phone_type", "author_type_stated", "locality_text"]
MANIFEST_NOTES = {"research_": "Research-agent records (organisations, contacts, relationships, enquiries) with per-fact sources",
                  "coverage/": "Queries, blocked sources and gaps for one research slice",
                  "nis_catchment_profiles": "NGOs Information System profiles for every NGO pinned within the register radius",
                  "nis_catchment_": "NGOs Information System map entries (name, pin, vision) within the register radius",
                  "nis_mapping": "Provenance of the NGOs Information System map extract",
                  "osm_welfare": "OpenStreetMap Overpass extract (tags or names) and its query"}


def iso(value: str) -> tuple[str, str]:
    v = str(value or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return v, "exact"
    if re.fullmatch(r"\d{4}-\d{2}", v):
        return v + "-01", "month_only"
    if re.fullmatch(r"\d{4}", v):
        return v + "-01-01", "year_only"
    return "", "unknown"


def primary_source(sources: list[dict]) -> dict:
    rank = {"official": 0, "published": 1, "public_profile": 2, "public_post": 3, "directory": 4, "research_note": 5}
    good = [s for s in sources if isinstance(s, dict) and s.get("url")]
    good.sort(key=lambda s: (not s.get("fetched"), rank.get(s.get("evidence_basis"), 9)))
    return good[0] if good else {}


def write_manifest(raw, run_id: str) -> None:
    lines = ["# Welfare-lead raw evidence", "",
             f"Evidence behind the welfare runs, most recently `{run_id}`. Research files follow the brief in "
             "`skills/silverleaf-welfare-leads/references/research-brief.md`; collectors are in `skills/silverleaf-welfare-leads/scripts/`.", "",
             "| File | SHA-256 | Contents |", "|---|---|---|"]
    for path in sorted(p for p in raw.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
        rel = path.relative_to(raw).as_posix()
        note = next((v for k, v in MANIFEST_NOTES.items() if rel.startswith(k)), "")
        lines.append(f"| `{rel}` | `{W.sha256_file(path)[:16]}…` | {note} |")
    (raw / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    today, work, interim = cfg["research_date"], cfg["paths"]["work"], cfg["paths"]["interim"]
    final = json.loads((work / "final.json").read_text(encoding="utf-8"))
    orgs, contacts, relations, enquiries, reviews, nis = (final[k] for k in ("organisations", "contacts", "relationships", "enquiries", "reviews", "nis"))
    headers = next(csv.reader(open(W.TEMPLATE, encoding="utf-8-sig")))
    rows = []

    domain_count = Counter(W.own_domain(o.get("website")) for o in orgs if W.own_domain(o.get("website")))
    for dom, n in domain_count.items():
        if n > 1:  # a domain shared by several organisations cannot be an identity key
            reviews.append({"kind": "shared_domain", "entity": dom, "detail": [o["organisation_name"] for o in orgs if W.own_domain(o.get("website")) == dom],
                            "action": "A domain shared by several organisations cannot be an identity key; confirm the relationship."})
    org_rows = {}
    for o in orgs:
        src = primary_source(o.get("sources", []))
        dom = W.own_domain(o.get("website"))
        dom = dom if domain_count.get(dom) == 1 else ""
        sdate, _ = iso(src.get("source_date"))
        row = {h: "" for h in headers}
        row.update({
            "record_type": "organisation", "source_url": src.get("url", ""), "source_location": (src.get("title") or "web page")[:180],
            "source_date": sdate, "acquired_on": today, "verified_on": today,
            "verification_status": o.get("verification_status") if o.get("verification_status") in W.VERIFICATION_RANK else "unverified",
            "evidence_basis": src.get("evidence_basis") if src.get("evidence_basis") in ALLOWED_BASIS else "research_note",
            "evidence_excerpt": (src.get("evidence_excerpt") or o.get("description") or o["organisation_name"])[:300],
            "notes": W.norm_text(o.get("notes"))[:900], "organisation_name": o["organisation_name"], "organisation_domain": dom,
            "segment": o.get("segment", ""), "subtype": o.get("subtype", ""),
            "priority": {"P1": "High", "P2": "Medium", "P3": "Low", "P4": "Low"}.get(o.get("priority_band"), ""),
            "campus": o.get("nearest_campus", ""), "distance_km": "" if o.get("distance_km") is None else o["distance_km"],
            "radius_tier": o.get("transport_band", ""), "geocode_precision": PRECISION.get(o.get("geocode_precision") or "", "estimated"),
            "latitude": "" if o.get("latitude") is None else round(float(o["latitude"]), 6),
            "longitude": "" if o.get("longitude") is None else round(float(o["longitude"]), 6),
            "locality": W.norm_text(o.get("locality") or o.get("ward") or o.get("district")), "address": W.norm_text(o.get("address")),
            "website": o.get("website", "") if str(o.get("website", "")).startswith("http") else (("https://" + o["website"]) if o.get("website") else ""),
            "public_email": (o.get("public_emails") or [""])[0], "public_phone": (o.get("public_phones") or [""])[0],
            "size_evidence": W.norm_text(o.get("children_served_evidence")), "education_angle": W.norm_text(o.get("schooling_arrangement_published")),
            "founded": W.norm_text(o.get("founded")), "licence_class": W.norm_text(o.get("nis_reg_no") or o.get("registration_published"))[:120],
            "osm_id": o.get("osm_id", ""), "desk_tier": o.get("priority_band", ""), "desk_score": o.get("priority_score", ""),
            "transport_band": o.get("transport_band", ""), "review_status": "research_only", "missing_information": o.get("track_reason", ""),
            "lead_track": "welfare_customer", "record_key": o["record_key"], "welfare_fit": o.get("welfare_fit", ""), "care_model": o.get("care_model", ""),
            "pdpa_risk": o.get("pdpa_risk") or "low", "pdpa_risk_reason": o.get("pdpa_risk_reason", ""),
            "proposed_welfare_track": o.get("proposed_track", ""), "track_reason": o.get("track_reason", ""),
            "priority_score": o.get("priority_score", ""), "factors_known": o.get("factors_known", ""),
            "children_served_published": W.js(o.get("children_served_published")), "children_served_as_of": W.js(o.get("children_served_as_of")),
            "age_range_published": W.js(o.get("age_range_published")), "gender_served": W.js(o.get("gender_served")),
            "schooling_arrangement_published": W.js(o.get("schooling_arrangement_published")), "runs_own_school": o.get("runs_own_school", "unknown"),
            "funding_model_published": W.js(o.get("funding_model_published")), "registration_published": W.js(o.get("registration_published")),
            "nis_reg_no": o.get("nis_reg_no", ""), "nis_reg_date": o.get("nis_reg_date", ""), "nis_profile_url": o.get("nis_profile_url", ""),
            "licence_status": o.get("licence_status", "not_checked"), "operator_or_umbrella": W.js(o.get("operator_or_umbrella")),
            "religious_affiliation_published": W.js(o.get("religious_affiliation_published")), "services": W.js(o.get("services")),
            "known_funders_or_partners": W.js(o.get("known_funders_or_partners")), "foreign_charity_registrations": W.js(o.get("foreign_charity_registrations")),
            "social_media": W.js(o.get("social_media")), "all_emails": W.js(o.get("public_emails")), "all_phones": W.js(o.get("public_phones")),
            "volunteer_programme": o.get("volunteer_programme", ""), "volunteer_fee_published": W.js(o.get("volunteer_fee_published")),
            "safeguarding_policy_url": W.js(o.get("safeguarding_policy_url")), "staff_count_published": W.js(o.get("staff_count_published")),
            "latest_activity_date": W.js(o.get("latest_activity_date") or o.get("nis_latest_project_end")), "red_flags": W.js(o.get("red_flags")),
            "catchment_note": W.js(o.get("catchment_note")), "master_organisation_id": o.get("master_organisation_id", ""),
            "nearest_primary_campus": o.get("nearest_primary_campus", ""),
            "distance_to_primary_km": "" if o.get("distance_to_primary_km") is None else o["distance_to_primary_km"],
            "all_sources_json": W.js(o.get("sources")), "locality_text": W.js(o.get("locality")),
        })
        rows.append(row)
        org_rows[o["record_key"]] = row

    for c in contacts:
        org = org_rows.get(c.get("organisation_key")) or {}
        src = primary_source(c.get("sources", []))
        sdate, _ = iso(src.get("source_date"))
        emails, phones = c.get("emails") or [], c.get("phones") or []
        etype, ptype = c.get("email_type") or "", c.get("phone_type") or ""
        row = {h: "" for h in headers}
        row.update({
            "record_type": "contact", "source_url": src.get("url", "") or org.get("source_url", ""),
            "source_location": (src.get("title") or "web page")[:180], "source_date": sdate, "acquired_on": today, "verified_on": today,
            "verification_status": c.get("verification_status") if c.get("verification_status") in W.VERIFICATION_RANK else "unverified",
            "evidence_basis": src.get("evidence_basis") if src.get("evidence_basis") in ALLOWED_BASIS else "research_note",
            "evidence_excerpt": (src.get("evidence_excerpt") or f"{c.get('contact_name', '')} {c.get('role', '')}")[:300],
            "notes": W.norm_text(c.get("notes"))[:600], "organisation_name": org.get("organisation_name") or c.get("organisation_name", ""),
            "organisation_domain": org.get("organisation_domain", ""), "locality": org.get("locality", ""),
            "contact_name": W.norm_text(c.get("contact_name")), "role": W.norm_text(c.get("role")),
            "role_certainty": c.get("role_certainty") if c.get("role_certainty") in ("confirmed", "role_desk", "inferred_role", "unknown") else "unknown",
            "contact_route": "email" if emails else "phone" if phones else "linkedin" if "linkedin" in str(c.get("profile_url", "")) else "website",
            "named_email": emails[0] if emails and etype in ("named", "personal_domain") else "",
            "published_role_email": emails[0] if emails and etype == "role" else "",
            "shared_email": emails[0] if emails and etype not in ("named", "personal_domain", "role") else "",
            "organisation_phone": phones[0] if phones and ptype == "office" else "", "role_phone": phones[0] if phones and ptype != "office" else "",
            "profile_url": c.get("profile_url", "") if str(c.get("profile_url", "")).startswith("http") else "",
            "channel_attribution": W.norm_text(c.get("channel_attribution"))[:300], "review_status": "research_only",
            "lead_track": "welfare_customer",
            "record_key": "WCON_" + re.sub(r"[^a-z0-9]+", "_", W.name_key(f"{org.get('organisation_name') or c.get('organisation_name', '')} {W.norm_text(c.get('contact_name')) or W.norm_text(c.get('role'))}"))[:56],
            "pdpa_risk": c.get("pdpa_risk") or "medium", "pdpa_risk_reason": c.get("pdpa_risk_reason", ""), "all_emails": W.js(emails),
            "all_phones": W.js(phones), "email_type": etype, "phone_type": ptype, "all_sources_json": W.js(c.get("sources")),
        })
        rows.append(row)

    skipped = 0
    for e in enquiries:
        edate, qual = iso(e.get("enquiry_date"))
        if not edate or not e.get("source_url") or not e.get("request"):
            skipped += 1
            reviews.append({"kind": "enquiry_not_loaded", "entity": e.get("enquiry_author_display"), "detail": {"date": e.get("enquiry_date"), "url": e.get("source_url")},
                            "action": "Enquiry kept in the research file but not loaded to the run database: date, URL or request missing."})
            continue
        src = primary_source(e.get("sources", [])) or {"url": e.get("source_url"), "evidence_basis": "public_post"}
        published = e.get("contact_published_in_post") if isinstance(e.get("contact_published_in_post"), dict) else {}
        row = {h: "" for h in headers}
        row.update({
            "record_type": "enquiry", "source_url": e.get("source_url", ""), "source_location": (src.get("title") or e.get("platform") or "public post")[:180],
            "source_date": edate, "acquired_on": today, "verified_on": today,
            "verification_status": e.get("verification_status") if e.get("verification_status") in W.VERIFICATION_RANK else "unverified",
            "evidence_basis": "public_post", "evidence_excerpt": (src.get("evidence_excerpt") or e.get("request"))[:300],
            "notes": W.norm_text(e.get("notes"))[:600], "locality": W.norm_text(e.get("locality")),
            "enquiry_author": W.norm_text(e.get("enquiry_author_display")) or "anonymous", "enquiry_type": W.norm_text(e.get("enquiry_type")),
            "enquiry_date": edate, "date_qualification": e.get("date_qualification") if e.get("date_qualification") in ("exact", "month_only", "year_only", "unknown") else qual,
            "request": W.norm_text(e.get("request"))[:600], "platform": W.norm_text(e.get("platform")), "contact_attribution": W.norm_text(e.get("contact_attribution")),
            "current_relevance": e.get("current_relevance") if e.get("current_relevance") in ("current", "recent", "historical", "unknown") else "unknown",
            "campus_fit": W.norm_text(e.get("campus_fit")) or "Unknown", "enquiry_phone": W.norm_text(published.get("phone")),
            "enquiry_email": W.norm_email(published.get("email")), "review_status": "research_only",
            "lead_track": "welfare_customer", "record_key": e.get("enquiry_key", ""), "pdpa_risk": "risky",
            "pdpa_risk_reason": e.get("pdpa_risk_reason") or "Private individual; household circumstances; possible children's data.",
            "author_type_stated": e.get("author_type_stated", ""), "all_sources_json": W.js(e.get("sources")),
        })
        rows.append(row)

    fieldnames = headers + [h for h in EXTRA if h not in headers]
    with open(cfg["paths"]["intake"], "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    def write_tsv(name, records, fields):
        with open(interim / name, "w", encoding="utf-8", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
            w.writeheader()
            for r in records:
                w.writerow({k: W.js(r.get(k)) if isinstance(r.get(k), (list, dict)) else r.get(k, "") for k in fields})
    write_tsv("welfare_organisations.tsv", [r for r in rows if r["record_type"] == "organisation"], fieldnames)
    write_tsv("welfare_contacts.tsv", [r for r in rows if r["record_type"] == "contact"], fieldnames)
    write_tsv("welfare_relationships.tsv", relations, ["from_organisation", "to_organisation", "relationship_type", "from_key", "to_key", "from_in_master",
                                                        "verification_status", "pdpa_risk", "notes", "sources"])
    write_tsv("ngo_register_catchment.tsv", nis, ["nis_id", "name", "welfare_relevance", "welfare_fit", "relevance_signal", "matched_organisation", "reg_no",
                                                  "reg_date", "level", "region", "district", "years_experience", "latest_project_end",
                                                  "nearest_campus_registry_coords", "distance_km_registry_coords", "latitude", "longitude", "profile_url",
                                                  "profile_fetched", "vision", "projects"])
    (work / "review_items.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    write_manifest(cfg["paths"]["raw"], args.run_id)
    print(json.dumps({"intake_rows": len(rows), "by_type": Counter(r["record_type"] for r in rows), "enquiries_not_loaded": skipped,
                      "reviews": len(reviews), "intake": str(cfg["paths"]["intake"].relative_to(W.ROOT))}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
