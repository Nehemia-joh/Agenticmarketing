#!/usr/bin/env python3
"""Add the campus gap census's new employers to the company master (one transaction), with their kind, campus and band.

Reads data/raw/gap-census/master_intake_<date>.csv, the shared-contract intake written by scripts/collection/build_gap_census.py.
Run the create skill's validate_intake.py and the update skill's preflight_update.py on it first (CLAUDE.md, 'Required order').

For every row:
- matches the master by exact normalised name, OpenStreetMap ID or website domain; a match is reported and skipped, never duplicated;
- inserts a new organisation: its segment (the map-style segment draft_master_messages.py files under a kind of employer), its proposed
  kind in subtype, campus, distance, transport band and radius tier, locality, address, website, published email and phone,
  OpenStreetMap ID and the source; verification starts with 'Raw OSM' for an OpenStreetMap-only record, so its draft is held until it
  is matched to a curated organisation (draft_master_messages.py);
- registers the intake file in source_files with one source record per row, links it through entity_sources, and records each
  published field as a fact;
- adds a review item for rows marked needs_review, and one 'Gap census: map lookup' item for rows without a phone or street address
  (the coordinator checks Google Maps for those).
Coordinates are not written here: --geocodes writes data/raw/gap-census/geocodes_gap_census_<date>.jsonl in the format of
scripts/master/apply_geocodes.py, which then fills latitude, longitude and geocode_precision with their facts and source records.
Preview by default (runtime/master/gap-census-preview.json); --apply writes. Afterwards run, in order:
  python scripts/master/apply_geocodes.py --file data/raw/gap-census/geocodes_gap_census_<date>.jsonl --db master --apply
  python scripts/master/recompute_campus_distances.py --apply --report outputs/reports/campus-distance-recompute-gap-census-<date>.json
  python scripts/messaging/draft_master_messages.py; python scripts/master/refresh_acquisition_metadata.py
  python scripts/master/rank_employer_reach.py --apply; python scripts/master/export_master_workbook_data.py; npm run build:workbook
  python scripts/master/verify_master.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "gap-census"
PREVIEW = ROOT / "runtime" / "master" / "gap-census-preview.json"
FACT_FIELDS = ("website", "public_email", "public_phone", "address", "locality", "subtype", "osm_id")


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def domain(url: str) -> str:
    m = re.search(r"(?:https?://)?(?:www\.)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)+)", str(url or "").lower())
    return m.group(1) if m else ""


def verification(row: dict, date: str) -> str:
    src = row.get("candidate_source", "")
    if src == "openstreetmap":
        return f"Raw OSM (gap census {date}): {row['source_url']}"
    label = {"google_maps": "Google Maps place pin read in the browser", "targeted": "official page or member directory, fetched",
             "ngo_register": "NGOs Information System register entry"}.get(src, "research")
    return f"Gap census {date}: {label} ({row['verification_status']})"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default="2026-10-11")
    parser.add_argument("--intake", type=Path)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--geocodes", action="store_true", help="write the apply_geocodes.py file for the organisations this run adds")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    intake = args.intake or RAW / f"master_intake_{args.date}.csv"
    rows = list(csv.DictReader(intake.open(encoding="utf-8-sig", newline="")))
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    by_name = {norm(r["name"]): r["organisation_id"] for r in con.execute("SELECT organisation_id, name FROM organisations")}
    by_osm = {r["osm_id"]: r["organisation_id"] for r in con.execute("SELECT organisation_id, osm_id FROM organisations WHERE COALESCE(osm_id,'')<>''")}
    by_domain = {}
    for r in con.execute("SELECT organisation_id, website FROM organisations"):
        if domain(r["website"]):
            by_domain.setdefault(domain(r["website"]), r["organisation_id"])
    plan, matched = [], []
    for i, row in enumerate(rows, 2):
        if row["record_type"] != "organisation":
            continue
        hit = by_name.get(norm(row["organisation_name"])) or (row["osm_id"] and by_osm.get(row["osm_id"])) or \
            (row["organisation_domain"] and by_domain.get(row["organisation_domain"]))
        if hit:
            matched.append({"line": i, "name": row["organisation_name"], "master_id": hit})
            continue
        oid = hid("O", "gap-census", norm(row["organisation_name"]), row["osm_id"] or row["candidate_id"])
        plan.append({"line": i, "organisation_id": oid, "row": row})
    summary = {"intake": intake.relative_to(ROOT).as_posix(), "rows": len(rows), "new_organisations": len(plan), "matched_existing": matched,
               "by_kind": {}, "by_segment": {}, "with_coordinates": sum(1 for p in plan if p["row"]["latitude"]),
               "map_lookup": sum(1 for p in plan if p["row"].get("maps_lookup") == "yes"),
               "needs_review": sum(1 for p in plan if p["row"]["verification_status"] == "needs_review")}
    for p in plan:
        summary["by_kind"][p["row"]["subtype"]] = summary["by_kind"].get(p["row"]["subtype"], 0) + 1
        summary["by_segment"][p["row"]["segment"]] = summary["by_segment"].get(p["row"]["segment"], 0) + 1
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps({"summary": summary, "organisations": [{"organisation_id": p["organisation_id"], "name": p["row"]["organisation_name"],
                                                                          "kind": p["row"]["subtype"], "campus": p["row"]["campus"]} for p in plan]},
                                  indent=1, ensure_ascii=False), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({k: (v if k != "matched_existing" else len(v)) for k, v in summary.items()}, indent=1, ensure_ascii=False))
    if args.geocodes:
        path = RAW / f"geocodes_gap_census_{args.date}.jsonl"
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            for p in plan:
                r = p["row"]
                if not r["latitude"]:
                    continue
                precision = {"rooftop": "point", "address": "address", "locality": "locality"}.get(r["geocode_precision"], "locality")
                src = {"openstreetmap": "OpenStreetMap", "google_maps": "Google Maps", "ngo_register": "NGO register"}.get(r["candidate_source"], "official site")
                how = "the location recorded with the lead"
                if "offline gazetteer" in r["notes"]:
                    src, how = "offline gazetteer (data/reference/lead-gazetteer.txt)", "the published locality placed with the offline gazetteer"
                elif "Coordinates of the site it shares" in r["notes"]:
                    src, how = "shared site", "the point of the site it shares (see notes)"
                fh.write(json.dumps({"db": "master", "organisation_id": p["organisation_id"], "organisation_name": r["organisation_name"], "key": "",
                                     "status": "placed", "latitude": float(r["latitude"]), "longitude": float(r["longitude"]), "precision": precision,
                                     "source_type": src, "source_url": r["source_url"], "fetched_on": r["acquired_on"],
                                     "as_found": f"{r['latitude']},{r['longitude']}", "osm_id": r["osm_id"],
                                     "basis": f"Gap census {args.date}: {how} ({r['geocode_precision']})."},
                                    ensure_ascii=False) + "\n")
        print(f"Wrote {path.relative_to(ROOT)}")
    if not args.apply:
        print(f"Preview only: {PREVIEW.relative_to(ROOT)}")
        return 0
    payload = intake.read_bytes()
    try:
        con.execute("BEGIN")
        sid = hid("F", "gap-census", intake.name)
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (sid, intake.relative_to(ROOT).as_posix(), hashlib.sha256(payload).hexdigest(), len(payload), "csv", "utf-8", payload))
        for p in plan:
            r, oid = p["row"], p["organisation_id"]
            record = hid("R", "gap-census", intake.name, oid)
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, sid, f"line {p['line']}: {r['organisation_name']}", json.dumps(r, ensure_ascii=False)))
            notes = " ".join(x for x in [f"Gap census {args.date} ({r['candidate_id']}). {r['fit_reason']}", r["notes"],
                                         f"Google Maps: {r['google_maps_url']}." if r.get("google_maps_url") else "",
                                         "Map lookup: phone or street address still to find." if r.get("maps_lookup") == "yes" else ""] if x)
            con.execute("""INSERT INTO organisations (organisation_id, name, segment, priority, campus, distance_km, size_evidence, address, education_angle,
                           source_url, verification, email, phone, subtype, radius_tier, website, notes, transport_band, locality, osm_id)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (oid, r["organisation_name"], r["segment"], "", r["campus"], float(r["distance_km"]) if r["distance_km"] else None, "",
                         r["address"], "Employer: a staff education benefit for its employees' children", r["source_url"], verification(r, args.date),
                         r["public_email"], r["public_phone"], r["subtype"], r["radius_tier"], r["website"], notes[:2000], r["transport_band"],
                         r["locality"], r["osm_id"]))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))
            for field in FACT_FIELDS:
                if r.get(field):
                    con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                                (hid("X", oid, field, r[field]), "organisation", oid, {"public_email": "email", "public_phone": "phone",
                                                                                        "subtype": "kind_of_employer"}.get(field, field), r[field], record))
            if r["verification_status"] == "needs_review":
                con.execute("INSERT OR IGNORE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("V", "gap-census-verify", oid), "Gap census: verify new lead", oid, "", "", r["notes"][:500],
                             "Confirm the organisation operates at this place and find its route before any message."))
            if r.get("maps_lookup") == "yes":
                con.execute("INSERT OR IGNORE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("V", "gap-census-maps", oid), "Gap census: map lookup", oid, "", "phone; address", r["missing_information"][:500],
                             "Look the organisation up on Google Maps for its phone and street address (enrichment round)."))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    print("Applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
