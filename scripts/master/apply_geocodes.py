#!/usr/bin/env python3
"""Merge reviewed lead locations from data/raw/geocode-research/geocodes_<date>.jsonl into the three lead lists.

Each line is one lead (scripts/maps/collect_geocodes.py gathers the candidates; a reviewer writes the accepted ones here):
  db                 master | welfare | government
  organisation_id    the lead's id in its database (master: organisations.organisation_id)
  organisation_name  the lead's name as its database holds it
  key                welfare: the run's organisation name (links.json geo_overrides key);
                     government: 'Council|Ward' for a ward (links.json ward_locations) or the office record key
                     ('GOFF_district_hai', links.json office_locations) for any other office
  status             placed | outside_confirmed | not_found (only 'placed' lines change anything)
  latitude, longitude
  precision          point (an exact building or pin) | address (a geocoded street address) | locality | city (only the
                     town is known: the lead map draws locality and city points as estimates)
  source_type        own site embed | OpenStreetMap | Nominatim | NGO register | official site | Wikidata | web search
  source_url, fetched_on, as_found (the excerpt or coordinates string as found), basis (why this point is this lead)
  place_text         the best address text found (for a lead left for a browser lookup)

What each list takes, through its own process:
- master (one transaction, --apply): fills only empty organisations.latitude/longitude, sets geocode_precision, fills an
  empty osm_id for an OpenStreetMap point, and records the facts latitude, longitude, geocode_precision and location_source
  tied to one source record per lead (source file: the geocodes file itself). A lead that already has coordinates is
  skipped and reported. Then run recompute_campus_distances.py --apply, rank_employer_reach.py --apply, the workbook export
  and build, and verify_master.py.
- welfare (--apply writes data/runs/<welfare run>/links.json): a geo_overrides entry per lead (lat, lon, precision 'point'
  for point and address, else 'locality', basis, url, fetched, as_found). Then run scripts/welfare/run_pipeline.py.
- government (--apply writes data/runs/<government run>/links.json): a ward_locations entry with source 'point', or an
  office_locations entry keyed by record key. Then run scripts/government/run_pipeline.py.
Every point must lie in Tanzania; a point outside the lead map's box is refused unless the line says allow_outside_box.
Existing entries are never overwritten; a changed entry for the same key is reported as a conflict and left alone.
Preview by default (runtime/geocode/apply-preview.json).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "geocode-research"
RUNS = {"welfare": "arusha-welfare-2026-09", "government": "arusha-government-2026-09"}
PREVIEW = ROOT / "runtime" / "geocode" / "apply-preview.json"
SOUTH, WEST, NORTH, EAST = -3.75, 36.30, -2.95, 37.55
REQUIRED = ("db", "organisation_id", "organisation_name", "status", "latitude", "longitude", "precision", "source_type", "source_url",
            "fetched_on", "as_found", "basis")


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def load(path: Path) -> tuple[list[dict], list[str]]:
    rows, problems = [], []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        r["_line"] = i
        rows.append(r)
        if r.get("status") != "placed":
            continue
        missing = [k for k in REQUIRED if r.get(k) in (None, "")]
        if missing:
            problems.append(f"line {i} ({r.get('organisation_name')}): missing {', '.join(missing)}")
            continue
        lat, lon = float(r["latitude"]), float(r["longitude"])
        if not (-12 < lat < -0.9 and 29 < lon < 41):
            problems.append(f"line {i} ({r['organisation_name']}): point {lat},{lon} is not in Tanzania")
        elif not (SOUTH <= lat <= NORTH and WEST <= lon <= EAST) and not r.get("allow_outside_box"):
            problems.append(f"line {i} ({r['organisation_name']}): point {lat},{lon} is outside the lead map's box")
        if r["precision"] not in ("point", "address", "locality", "city"):
            problems.append(f"line {i} ({r['organisation_name']}): precision must be point, address, locality or city")
        if r["db"] in ("welfare", "government") and not r.get("key"):
            problems.append(f"line {i} ({r['organisation_name']}): a {r['db']} line needs its key")
    return rows, problems


def plan_master(con, rows) -> tuple[list[dict], list[dict]]:
    todo, skipped = [], []
    for r in rows:
        o = con.execute("SELECT organisation_id, name, latitude, longitude, osm_id FROM organisations WHERE organisation_id=?", (r["organisation_id"],)).fetchone()
        if o is None:
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": "no such organisation"})
        elif o["name"] != r["organisation_name"]:
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": f"name differs from the master ('{o['name']}')"})
        elif str(o["latitude"] or "").strip() or str(o["longitude"] or "").strip():
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": f"already has coordinates ({o['latitude']}, {o['longitude']})"})
        else:
            osm = r.get("osm_id") if r["source_type"] == "OpenStreetMap" and not (o["osm_id"] or "").strip() else ""
            todo.append({**r, "_osm": osm})
    return todo, skipped


def apply_master(path: Path, todo: list[dict]) -> None:
    con = sqlite3.connect(MASTER)
    today = date.today().isoformat()
    payload = path.read_bytes()
    try:
        con.execute("BEGIN")
        source = hid("F", "geocodes", path.name)
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (source, path.relative_to(ROOT).as_posix(), hashlib.sha256(payload).hexdigest(), len(payload), "jsonl", "utf-8", payload))
        for r in todo:
            oid = r["organisation_id"]
            record = hid("R", "geocode", path.name, oid)
            keep = {k: v for k, v in r.items() if not k.startswith("_")}
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source, f"line {r['_line']}: {r['organisation_name']}", json.dumps(keep, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))
            lat, lon = round(float(r["latitude"]), 6), round(float(r["longitude"]), 6)
            con.execute("UPDATE organisations SET latitude=?, longitude=?, geocode_precision=? WHERE organisation_id=?", (lat, lon, r["precision"], oid))
            if r["_osm"]:
                con.execute("UPDATE organisations SET osm_id=? WHERE organisation_id=?", (r["_osm"], oid))
            where = f"{r['source_type']}: {r['source_url']} (fetched {r['fetched_on']})"
            for field, value in (("latitude", str(lat)), ("longitude", str(lon)), ("geocode_precision", r["precision"]), ("location_source", where)):
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", oid, field, value, today), "organisation", oid, field, value, record))
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def entry_for(r: dict, db: str) -> dict:
    lat, lon = round(float(r["latitude"]), 6), round(float(r["longitude"]), 6)
    basis = f"{r['basis']} Source: {r['source_type']}, {r['source_url']} (fetched {r['fetched_on']}); as found: {r['as_found']}"
    if db == "welfare":
        welfare_precision = {"point": "point", "address": "point", "locality": "locality", "city": "town"}[r["precision"]]
        return {"lat": lat, "lon": lon, "precision": welfare_precision, "basis": basis,
                "url": r["source_url"], "fetched": r["fetched_on"], "as_found": r["as_found"], "source_type": r["source_type"]}
    return {"source": "point", "lat": lat, "lon": lon, "precision": r["precision"], "url": r["source_url"], "fetched": r["fetched_on"],
            "as_found": r["as_found"], "source_type": r["source_type"], "note": f"Reviewed point ({date.today().isoformat()}): {basis}"}


def plan_links(rows, db: str) -> tuple[dict, dict, list[dict], list[dict]]:
    path = ROOT / "data" / "runs" / RUNS[db] / "links.json"
    links = json.loads(path.read_text(encoding="utf-8"))
    adds, conflicts = [], []
    for r in rows:
        if db == "welfare":
            section = "geo_overrides"
        else:
            section = "ward_locations" if "|" in r["key"] else "office_locations"
        new = entry_for(r, db)
        old = links.get(section, {}).get(r["key"])
        if old is None:
            adds.append((section, r["key"], new))
        elif (old.get("lat"), old.get("lon")) != (new["lat"], new["lon"]):
            conflicts.append({"key": r["key"], "section": section, "existing": old, "proposed": new})
    return links, path, adds, conflicts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", type=Path, help="default: the newest data/raw/geocode-research/geocodes_*.jsonl")
    parser.add_argument("--db", choices=["master", "welfare", "government"], action="append", help="default: all three")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    path = args.file or max(RAW.glob("geocodes_*.jsonl"))
    rows, problems = load(path)
    if problems:
        print("Refused: fix these lines first:\n  " + "\n  ".join(problems))
        return 1
    dbs = args.db or ["master", "welfare", "government"]
    placed = [r for r in rows if r.get("status") == "placed"]
    report = {"file": path.relative_to(ROOT).as_posix(), "lines": len(rows), "placed": len(placed),
              "not_placed": {s: sum(1 for r in rows if r.get("status") == s) for s in ("outside_confirmed", "not_found")}}
    if "master" in dbs:
        con = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        todo, skipped = plan_master(con, [r for r in placed if r["db"] == "master"])
        con.close()
        report["master"] = {"to_fill": len(todo), "skipped": skipped, "by_source": {}}
        for r in todo:
            report["master"]["by_source"][r["source_type"]] = report["master"]["by_source"].get(r["source_type"], 0) + 1
        # A revised file (a line held back or added) also refreshes the stored copy that the earlier source records cite.
        con = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
        stored = con.execute("SELECT sha256 FROM source_files WHERE source_id=?", (hid("F", "geocodes", path.name),)).fetchone()
        con.close()
        changed = bool(stored) and stored[0] != hashlib.sha256(path.read_bytes()).hexdigest()
        if args.apply and (todo or changed):
            apply_master(path, todo)
            report["master"]["applied"] = len(todo)
            report["master"]["source_file_refreshed"] = changed
    for db in ("welfare", "government"):
        if db not in dbs:
            continue
        links, lpath, adds, conflicts = plan_links([r for r in placed if r["db"] == db], db)
        report[db] = {"to_add": [f"{s}: {k}" for s, k, _ in adds], "conflicts": conflicts}
        if args.apply and adds:
            for section, key, entry in adds:
                links.setdefault(section, {})[key] = entry
            lpath.write_text(json.dumps(links, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            report[db]["applied"] = len(adds)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: (vv if not isinstance(vv, list) else len(vv)) for kk, vv in v.items()})
                      for k, v in report.items()}, ensure_ascii=False, indent=1))
    print(("Applied." if args.apply else "Preview only; --apply writes.") + f" Details: {PREVIEW.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
