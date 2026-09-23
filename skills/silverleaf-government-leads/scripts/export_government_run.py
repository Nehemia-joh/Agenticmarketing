#!/usr/bin/env python3
"""Export the built government run to the shared intake contract, interim tables and the raw-evidence manifest.

Reads runtime/government/<run-id>/final.json. Writes:
- data/runs/<run-id>/intake.csv: offices as organisation rows and official posts as contact rows, with every shared
  contract column plus the government extra columns (the create skill's validator accepts extra columns and its
  initializer keeps them in source_records.payload_json). Proposed GA tracks and value modules stay in extra
  columns: the shared contract only accepts AQ tracks and VM01-VM07, and no outreach is planned in a research run.
- data/interim/government-leads/*.tsv: administrative units, offices, posts, office triage, master triage, signals.
- data/raw/government-research/MANIFEST.md: SHA-256 of every raw evidence file.
"""
from __future__ import annotations

import argparse
import csv
import json

import gov_lib as G

W = G.W
EXTRA = ["lead_track", "record_key", "office_level", "admin_unit_level", "admin_unit_name", "parent_admin_unit", "council_name", "region",
         "census_2022_population", "census_source_location", "catchment_wards", "catchment_population_2022", "office_title", "office_title_sw",
         "appointment_type", "holder_name", "holder_verified_on", "tenure_source_url", "b2g_check_required", "convening_role", "convening_forum",
         "protocol_status", "protocol_ref", "pdpa_risk", "pdpa_risk_reason", "proposed_government_track", "track_reason", "proposed_value_modules",
         "ward_score", "ward_tier", "score_factors", "factors_known", "rank_in_cluster", "campus_cluster", "nearest_primary_campus",
         "distance_to_primary_km", "primary_band", "location_source", "location_note", "po_box", "master_organisation_id", "all_sources_json"]
MANIFEST_NOTES = {"nbs_2022_wards": "2022 census ward populations for the run's councils, with table, PDF page and row locators",
                  "nbs_2022_councils": "Council totals, table references and the ward-sum reconciliation; report SHA-256",
                  "wikipedia_wards": "Wikipedia ward articles: title, revision, coordinates and first sentence (CC BY-SA 4.0)",
                  "osm_places": "OpenStreetMap place nodes in the bounding box, with the query",
                  "osm_admin_level5": "OpenStreetMap district boundaries (admin_level 5), simplified, with the query",
                  "osm_named_facilities": "OpenStreetMap schools and health facilities named after catchment wards, with the query; "
                                          "used only through reviewed ward_locations overrides",
                  "osm_government_offices": "OpenStreetMap government offices (tags and names), with both queries",
                  "council_sites/": "Council or regional website captured through its public API; CMS editor data, photos and biographies removed",
                  "transcriptions/": "Transcription of a scanned official document, with page and row locators"}
MODULES = {"council": "VM14|VM15|VM16|VM17", "ward": "VM14|VM15|VM16|VM17", "village": "VM14|VM15|VM16|VM17", "district": "", "region": ""}
PRIORITY = {"P1": "High", "P2": "Medium", "P3": "Low", "P4": "Low"}


def write_manifest(raw, run_id: str) -> None:
    lines = ["# Government-lead raw evidence", "",
             f"Evidence behind the government runs, most recently `{run_id}`. Collectors and the build are in `scripts/government/`; "
             "the method is in `skills/silverleaf-government-leads/SKILL.md`. Council-site captures never keep CMS editor names or emails.", "",
             "| File | SHA-256 | Contents |", "|---|---|---|"]
    for path in sorted(p for p in raw.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
        rel = path.relative_to(raw).as_posix()
        note = next((v for k, v in MANIFEST_NOTES.items() if rel.startswith(k)), "")
        lines.append(f"| `{rel}` | `{W.sha256_file(path)[:16]}…` | {note} |")
    (raw / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def tsv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def fmt(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".") if abs(value) < 1000 else str(value)
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    date, work, interim, raw = cfg["research_date"], cfg["paths"]["work"], cfg["paths"]["interim"], cfg["paths"]["raw"]
    final = json.loads((work / "final.json").read_text(encoding="utf-8"))
    headers = next(csv.reader(open(W.TEMPLATE, encoding="utf-8-sig")))
    rows = []
    for o in final["offices"]:
        tier = o.get("ward_tier") or ""
        priority = "High" if o["proposed_government_track"].startswith("GA01") else PRIORITY.get(tier, "Low")
        excerpt = o["all_sources"][0].get("evidence_excerpt") or f"{o['name']}: {o['convening_forum']}"
        row = {h: "" for h in headers}
        row.update({
            "record_type": "organisation", "source_path": o.get("source_path", ""), "source_location": o.get("source_location") or o["record_key"],
            "source_url": o.get("source_url", ""), "acquired_on": date, "verified_on": date, "verification_status": o["verification_status"],
            "evidence_basis": o["evidence_basis"], "evidence_excerpt": G.W.norm_text(excerpt)[:300],
            "notes": o.get("location_note", ""), "organisation_name": o["name"], "organisation_domain": o.get("domain", ""),
            "segment": o["segment"], "subtype": o["office_level"], "priority": priority, "campus": o.get("campus", ""),
            "distance_km": fmt(o.get("distance_km")), "radius_tier": o.get("transport_band", ""), "geocode_precision": o.get("geocode_precision", ""),
            "latitude": fmt(o.get("lat")), "longitude": fmt(o.get("lon")), "locality": o.get("locality", ""), "address": o.get("po_box", ""),
            "website": o.get("website", ""), "public_email": o.get("public_email", ""), "public_phone": o.get("public_phone", ""),
            "size_evidence": o.get("size_evidence", ""), "osm_id": o.get("osm_id", ""), "desk_tier": tier, "desk_score": fmt(o.get("ward_score")),
            "transport_band": o.get("transport_band", ""), "review_status": "research_only", "missing_information": o.get("missing_information", ""),
        })
        row.update({
            "lead_track": "government_convener", "record_key": o["record_key"], "office_level": o["office_level"],
            "admin_unit_level": o.get("admin_unit_level", ""), "admin_unit_name": o.get("admin_unit_name", ""),
            "parent_admin_unit": o.get("parent_admin_unit", ""), "council_name": o.get("council_name", ""), "region": o.get("region", ""),
            "census_2022_population": fmt(o.get("census_2022_population")), "census_source_location": o.get("census_source_location", ""),
            "catchment_wards": fmt(o.get("catchment_wards")), "catchment_population_2022": fmt(o.get("catchment_population_2022")),
            "convening_forum": o.get("convening_forum", ""), "protocol_status": "none", "pdpa_risk": o["pdpa_risk"],
            "pdpa_risk_reason": o["pdpa_risk_reason"], "proposed_government_track": o["proposed_government_track"], "track_reason": o["track_reason"],
            "proposed_value_modules": MODULES.get(o["office_level"], "") if not o["proposed_government_track"].startswith("GA00") else "",
            "ward_score": fmt(o.get("ward_score")), "ward_tier": tier, "score_factors": o.get("score_factors", ""), "factors_known": o.get("factors_known", ""),
            "rank_in_cluster": fmt(o.get("rank_in_cluster")), "campus_cluster": o.get("campus_cluster", ""),
            "nearest_primary_campus": o.get("nearest_primary_campus", ""), "distance_to_primary_km": fmt(o.get("distance_to_primary_km")),
            "primary_band": o.get("primary_band", ""), "location_source": o.get("location_source", ""), "location_note": o.get("location_note", ""),
            "po_box": o.get("po_box", ""), "master_organisation_id": o.get("master_organisation_id", ""),
            "all_sources_json": json.dumps(o["all_sources"], ensure_ascii=False),
        })
        rows.append(row)
    for p in final["posts"]:
        row = {h: "" for h in headers}
        row.update({
            "record_type": "contact", "source_path": p.get("source_path", ""), "source_location": p.get("source_location") or p["record_key"],
            "source_url": p["source_url"], "acquired_on": date, "verified_on": date, "verification_status": p["verification_status"],
            "evidence_basis": p["evidence_basis"], "evidence_excerpt": G.W.norm_text(p["evidence_excerpt"])[:300], "notes": p.get("notes", ""),
            "organisation_name": p["organisation_name"], "organisation_domain": p.get("organisation_domain", ""), "locality": p.get("locality", ""),
            "contact_name": p.get("holder_name", ""), "role": p["role"], "role_certainty": p["role_certainty"], "contact_route": p["contact_route"],
            "published_role_email": p.get("published_role_email", ""), "organisation_phone": p.get("organisation_phone", ""),
            "role_phone": p.get("role_phone", ""), "channel_attribution": p.get("channel_attribution", ""), "review_status": "research_only",
        })
        row.update({
            "lead_track": "government_convener", "record_key": p["record_key"], "office_level": p["office_level"],
            "council_name": p.get("council_name", ""), "office_title": p["office_title"], "office_title_sw": p["office_title_sw"],
            "appointment_type": p["appointment_type"], "holder_name": p.get("holder_name", ""), "holder_verified_on": p.get("holder_verified_on", ""),
            "tenure_source_url": p.get("tenure_source_url", ""), "b2g_check_required": p["b2g_check_required"], "convening_role": p["convening_role"],
            "protocol_status": "none", "pdpa_risk": p["pdpa_risk"], "pdpa_risk_reason": p["pdpa_risk_reason"],
            "proposed_government_track": p["proposed_government_track"], "all_sources_json": json.dumps(p["all_sources"], ensure_ascii=False),
        })
        rows.append(row)
    fields = headers + [c for c in EXTRA if c not in headers]
    intake = cfg["paths"]["intake"]
    intake.parent.mkdir(parents=True, exist_ok=True)
    with open(intake, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    unit_fields = ["record_key", "level", "name", "council", "region", "admin_district", "core_council", "population_2022", "male_2022", "female_2022",
                   "households_2022", "avg_household_size_2022", "census_source_location", "lat", "lon", "geocode_precision", "location_source",
                   "location_ref", "location_note", "campus", "distance_km", "transport_band", "nearest_primary_campus", "distance_to_primary_km",
                   "primary_band", "campus_cluster", "in_catchment", "ward_score", "ward_tier", "rank_in_cluster", "factors_known", "score_factors"]
    tsv(interim / "admin_units.tsv", final["admin_units"], unit_fields)
    tsv(interim / "offices.tsv", final["offices"], ["record_key", "name", "office_level", "council_name", "region", "admin_unit_name", "parent_admin_unit",
                                                    "proposed_government_track", "track_reason", "ward_score", "ward_tier", "campus", "distance_km",
                                                    "transport_band", "lat", "lon", "geocode_precision", "location_source", "osm_id", "master_organisation_id",
                                                    "verification_status", "missing_information"])
    tsv(interim / "posts.tsv", final["posts"], ["record_key", "office_key", "organisation_name", "post_key", "office_title", "office_title_sw",
                                                "appointment_type", "holder_name", "holder_verified_on", "tenure_source_url", "role_phone",
                                                "published_role_email", "b2g_check_required", "pdpa_risk", "verification_status", "source_url"])
    tsv(interim / "office_triage.tsv", final["office_triage"], ["source", "source_id", "name", "category", "detail", "tags", "osm_district", "lat", "lon",
                                                                "campus", "distance_km", "linked_office", "note"])
    tsv(interim / "master_triage.tsv", final["master_triage"], ["master_organisation_id", "name", "master_campus", "master_distance_km", "category",
                                                                "detail", "group", "proposed_treatment", "matched_osm_id", "linked_office"])
    tsv(interim / "convening_signals.tsv", final["signals"], ["organisation", "host", "kind", "item_id", "date", "title", "tags", "listing_url"])
    write_manifest(raw, args.run_id)
    counts = {"organisation_rows": sum(1 for r in rows if r["record_type"] == "organisation"),
              "contact_rows": sum(1 for r in rows if r["record_type"] == "contact"), "admin_units": len(final["admin_units"])}
    print(json.dumps({"intake": str(intake.relative_to(G.ROOT)), **counts, "interim": str(interim.relative_to(G.ROOT))}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
