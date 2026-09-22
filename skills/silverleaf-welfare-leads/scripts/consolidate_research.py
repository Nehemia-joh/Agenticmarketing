#!/usr/bin/env python3
"""Merge research-agent records into one record per institution and geocode them (offline, deterministic).

Reads the research files listed in data/runs/<run-id>/run-config.json (research_files globs) and the run's links.json
(geo_overrides). Writes runtime/welfare/<run-id>/consolidated.json.
Rules: exact name, alias or own-domain matches merge, but only between records of the same kind (funder with funder,
institution with institution); similar names, conflicting material facts and shared domains go to review.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import defaultdict

import welfare_lib as W

SCALAR_FIELDS = ["organisation_name", "segment", "subtype", "care_model", "description", "operator_or_umbrella",
                 "religious_affiliation_published", "founded", "registration_published", "licence_claim", "address",
                 "locality", "ward", "district", "region", "latitude", "longitude", "geocode_basis", "website",
                 "children_served_published", "children_served_evidence", "children_served_as_of", "age_range_published",
                 "gender_served", "schooling_arrangement_published", "runs_own_school", "funding_model_published",
                 "volunteer_programme", "volunteer_fee_published", "safeguarding_policy_url", "staff_count_published",
                 "latest_activity_date", "latest_activity_evidence", "catchment_note", "pdpa_risk", "pdpa_risk_reason"]


def is_funder(org: dict) -> bool:
    return str(org.get("segment", "")).startswith("Welfare funder")


def merge_organisations(orgs: list[dict]) -> tuple[list[dict], list[dict]]:
    parent = list(range(len(orgs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(i)] = find(j)

    by_key, by_domain, reviews = {}, {}, []
    for i, org in enumerate(orgs):
        keys = {W.name_key(org.get("organisation_name"))} | {W.name_key(a) for a in W.as_list(org.get("alternative_names"))}
        for k in keys - {""}:
            if k in by_key and is_funder(orgs[by_key[k]]) == is_funder(org):
                union(i, by_key[k])
            elif k not in by_key:
                by_key[k] = i
        dom = W.own_domain(org.get("website"))
        if dom:
            if dom in by_domain and is_funder(orgs[by_domain[dom]]) == is_funder(org):
                union(i, by_domain[dom])
            elif dom in by_domain:
                reviews.append({"kind": "shared_domain_funder_and_institution", "entity": org.get("organisation_name"),
                                "related": orgs[by_domain[dom]].get("organisation_name"), "detail": {"domain": dom},
                                "action": "A funder and an institution cite the same website; kept separate. Confirm which organisation the site belongs to."})
            else:
                by_domain[dom] = i
    groups = defaultdict(list)
    for i in range(len(orgs)):
        groups[find(i)].append(orgs[i])
    merged = []
    for members in groups.values():
        members.sort(key=lambda o: (W.VERIFICATION_RANK.get(o.get("verification_status"), 9), -len(W.as_list(o.get("sources")))))
        base = {"members": [f"{m['_file']}:{m['_line']}" for m in members], "slices": sorted({str(m.get("slice", "")) for m in members})}
        conflicts = {}
        for field in SCALAR_FIELDS:
            values = [m.get(field) for m in members if m.get(field) not in (None, "", "unknown", [])]
            base[field] = values[0] if values else ("unknown" if field in ("runs_own_school", "volunteer_programme") else "")
            if field in W.MATERIAL_FIELDS and len({W.material_value(field, v) for v in values} - {""}) > 1:
                conflicts[field] = sorted({W.norm_text(v) for v in values})
            elif len({W.norm_text(v).lower() for v in values}) > 1:
                base.setdefault("wording_variants", {})[field] = sorted({W.norm_text(v) for v in values})
        if base.get("latest_activity_date"):
            base["latest_activity_date"] = sorted({str(m.get("latest_activity_date")) for m in members if m.get("latest_activity_date")})[-1]
        base["alternative_names"] = sorted({W.norm_text(n) for m in members for n in [m.get("organisation_name")] + W.as_list(m.get("alternative_names")) if n}
                                           - {W.norm_text(base["organisation_name"])})
        base["public_emails"] = sorted({e for m in members for e in map(W.norm_email, W.as_list(m.get("public_emails"))) if e})
        phones = {}
        for m in members:
            for p in W.as_list(m.get("public_phones")):
                if W.norm_phone(p):
                    phones.setdefault(W.norm_phone(p), W.norm_text(p))
        base["public_phones"] = sorted(phones)
        social = {}
        for m in members:
            for k, v in (m.get("social_media") or {}).items() if isinstance(m.get("social_media"), dict) else []:
                for url in W.as_list(v):
                    social.setdefault(k, [])
                    if url not in social[k]:
                        social[k].append(url)
        base["social_media"] = social
        for field in ("services", "red_flags"):
            base[field] = sorted({W.norm_text(v) for m in members for v in W.as_list(m.get(field)) if v})
        funders, charities, sources = [], [], []
        for m in members:
            for f in W.as_list(m.get("known_funders_or_partners")):
                if isinstance(f, dict) and f.get("name") and f not in funders:
                    funders.append(f)
            for c in W.as_list(m.get("foreign_charity_registrations")):
                if isinstance(c, dict) and (c.get("number") or c.get("register")) and c not in charities:
                    charities.append(c)
            for s in W.as_list(m.get("sources")):
                if isinstance(s, dict) and s.get("url") and s.get("url") not in [x.get("url") for x in sources]:
                    sources.append(s)
        base["known_funders_or_partners"], base["foreign_charity_registrations"], base["sources"] = funders, charities, sources
        base["verification_status"] = W.best_verification([m.get("verification_status") for m in members])
        base["pdpa_risk"] = max((m.get("pdpa_risk") or "low" for m in members), key=lambda r: W.RISK_RANK.get(r, 0))
        base["notes"] = " | ".join(sorted({W.norm_text(m.get("notes")) for m in members if m.get("notes")}))
        base["conflicts"] = conflicts
        merged.append(base)
        if conflicts:
            reviews.append({"kind": "field_conflict", "entity": base["organisation_name"], "detail": conflicts,
                            "action": "Confirm the current value from the strongest source; keep the other as a fact."})
    keys = [(W.name_key(o["organisation_name"]), o["organisation_name"]) for o in merged]
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i][0], keys[j][0]
            if not a or not b:
                continue
            ratio = difflib.SequenceMatcher(None, a, b).ratio()
            ta, tb = set(a.split()), set(b.split())
            if ratio >= 0.85 or ((ta & tb) - W.GENERIC_TOKENS and ratio >= 0.6):
                reviews.append({"kind": "possible_duplicate", "entity": keys[i][1], "related": keys[j][1],
                                "detail": {"sequence_ratio": round(ratio, 2), "token_jaccard": round(len(ta & tb) / max(1, len(ta | tb)), 2)},
                                "action": "Check whether these are the same institution; merge only on an exact supported match."})
    return merged, reviews


def geocode(merged: list[dict], gaz: dict, campuses: dict, overrides: dict) -> None:
    for o in merged:
        lat, lon, basis = o.get("latitude"), o.get("longitude"), o.get("geocode_basis") or ""
        try:
            lat, lon = float(lat), float(lon)
            precision = "point" if basis and "locality" not in basis.lower() else "reported"
        except (TypeError, ValueError):
            lat = lon = None
            precision = ""
        override = overrides.get(o["organisation_name"])
        if override:
            lat, lon, precision, basis = override["lat"], override["lon"], override.get("precision", "locality"), "manual: " + override.get("basis", "")
        if lat is None:
            best = None
            for field in ("ward", "locality", "address", "district"):  # most specific field first
                hay = str(o.get(field) or "").lower()
                hits = []
                for n in gaz:
                    if len(n) <= 3:
                        continue
                    for m in re.finditer(r"\b" + re.escape(n) + r"\b", hay):
                        after, before = hay[m.end():m.end() + 9], hay[max(0, m.start() - 2):m.start()]
                        if re.match(r"\s*(road|rd\b|highway|street|avenue)", after) or re.search(r"[–—-]\s*$", before) or re.match(r"\s*[–—-]\s*\w", after):
                            continue  # part of a road name such as "Arusha–Nairobi highway" or "Dodoma road"
                        hits.append((m.start(), n))
                        break
                if not hits:
                    continue
                in_region = [(pos, n) for pos, n in hits if W.in_catchment_box(*gaz[n][:2])]
                pool = in_region or hits
                specific = [(pos, n) for pos, n in pool if n not in W.COARSE_PLACES]
                best = min(specific or pool)[1]  # earliest mention wins; specific places before coarse ones
                break
            if best and best not in W.COARSE_PLACES:
                lat, lon, precision, basis = gaz[best][0], gaz[best][1], "locality", f"gazetteer: {best}"
            elif best:
                lat, lon, precision, basis = gaz[best][0], gaz[best][1], "town", f"gazetteer (coarse): {best}"
        o["latitude"], o["longitude"], o["geocode_precision"], o["geocode_basis"] = lat, lon, precision, basis
        o["record_key"] = "WORG_" + re.sub(r"[^a-z0-9]+", "_", W.name_key(o["organisation_name"]))[:48]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    work = cfg["paths"]["work"]
    campuses = W.load_campuses()
    gaz = W.build_gazetteer(work)
    links = W.load_links(cfg)
    records = []
    for path in W.resolve_globs(cfg["research_files"]):
        recs = W.read_jsonl(path)
        print(f"{path.relative_to(W.ROOT)}: {len(recs)} records")
        records += recs
    orgs = [r for r in records if r.get("record_type") == "organisation"]
    contacts = [r for r in records if r.get("record_type") == "contact"]
    relations = [r for r in records if r.get("record_type") == "relationship"]
    enquiries = [r for r in records if r.get("record_type") == "enquiry"]
    merged, reviews = merge_organisations(orgs)
    print(f"organisations: {len(orgs)} raw -> {len(merged)} merged; contacts {len(contacts)}; relationships {len(relations)}; enquiries {len(enquiries)}")
    for coll in (merged, contacts, enquiries):  # child-data guard: anything that looks like a child's identity goes to review
        for r in coll:
            blob = json.dumps({k: v for k, v in r.items() if k not in ("sources", "members")}, ensure_ascii=False)
            hit = W.CHILD_ID_PATTERN.search(blob)
            if hit:
                reviews.append({"kind": "possible_child_identifier", "entity": r.get("organisation_name") or r.get("enquiry_author_display"),
                                "detail": hit.group(0), "action": "Remove any child identifier before release."})
    geocode(merged, gaz, campuses, links.get("geo_overrides", {}))
    out = {"organisations": merged, "contacts": contacts, "relationships": relations, "enquiries": enquiries, "reviews": reviews}
    (work / "consolidated.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(f"reviews: {len(reviews)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
