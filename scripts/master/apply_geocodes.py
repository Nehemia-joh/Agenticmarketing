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

Reviewed corrections (--replace, master only; decided 2026-10-11). A corrections file
(data/raw/geocode-research/geocodes_corrections_<date>.jsonl, named with --file) replaces an estimated master point with
the organisation's own pin. Each line carries the fields above plus replace: true and the stored point it replaces
(old_latitude, old_longitude, old_precision, old_location_source, old_record_id). Only the organisation_ids named in the file
are touched, and a line is applied only when:
- the master still holds exactly that old point;
- the stored point is an estimate: precision address, locality or city, and its location_source fact is the NGO register's
  address text or the offline gazetteer (REPLACEABLE); anything else (an OpenStreetMap point, an own-site embed) is skipped;
- the new point does not take a lead that was inside the 25 km catchment beyond it (a correction never removes a lead; such a
  line is refused until a reviewed catchment record exists for it).
In one transaction it registers the file and one source record per line, sets the new point with precision from the line,
records the new facts and keeps the old point as a fact (superseded_location, with its source), and adds a review item
'Location corrected' with both points. Then run recompute_campus_distances.py --apply (with its own --report),
rank_employer_reach.py --apply, draft_master_messages.py (drafts that name the nearest campus), the workbook and verify_master.py.
Without --replace nothing here changes: the default run never overwrites a point.
Since 13 October 2026 (a draft states a campus distance only from a point) --replace also takes a stored estimate from Nominatim,
own-site text placed with the gazetteer, a shared site or an OpenStreetMap address-level point, and an importer's point with no
precision or source recorded (the line's old_location_source then reads NO_SOURCE). A correction that takes a lead beyond the
catchment is applied only when its line carries a reviewed beyond_catchment note: the lead is kept and gets the review item
'Beyond the catchment after geolocation' (the default fill path adds the same item). A line's geocode_source and confidence are
kept as the facts geocode_source and geocode_confidence.
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
# --replace: the stored point must be one of these estimates (location_source fact prefix, geocode_precision).
# Widened 13 October 2026 (drafts state a distance only from a point): a Nominatim street or locality result, the own-site text
# placed with the gazetteer, a shared site's point and an OpenStreetMap address-level point are estimates too, and so is an
# importer's point with no precision or source recorded (NO_SOURCE), whose line must say so.
REPLACEABLE = ("NGO register", "offline gazetteer", "Nominatim", "own site text + repository gazetteer", "shared site", "OpenStreetMap")
REPLACEABLE_PRECISION = ("address", "locality", "city", "town", "")
NO_SOURCE = "none recorded (the importer's point)"
REPLACE_REQUIRED = ("old_latitude", "old_longitude", "old_location_source")
CATCHMENT_KM = 25.0
EXTRA_FACTS = ("geocode_source", "confidence")   # recorded as facts when a line carries them (geocode_confidence for confidence)


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
    campuses = {c["name"]: (c["latitude"], c["longitude"]) for c in con.execute("SELECT name, latitude, longitude FROM campuses")}
    todo, skipped = [], []
    for r in rows:
        o = con.execute("SELECT organisation_id, name, latitude, longitude, osm_id, campus, distance_km FROM organisations WHERE organisation_id=?",
                        (r["organisation_id"],)).fetchone()
        if o is None:
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": "no such organisation"})
        elif o["name"] != r["organisation_name"]:
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": f"name differs from the master ('{o['name']}')"})
        elif str(o["latitude"] or "").strip() or str(o["longitude"] or "").strip():
            skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": f"already has coordinates ({o['latitude']}, {o['longitude']})"})
        else:
            osm = r.get("osm_id") if r["source_type"] == "OpenStreetMap" and not (o["osm_id"] or "").strip() else ""
            before = float(o["distance_km"]) if str(o["distance_km"] or "").replace(".", "", 1).isdigit() else None
            campus, km = nearest_km(campuses, float(r["latitude"]), float(r["longitude"]))
            beyond = ((o["campus"], before), (campus, km)) if before is not None and before <= CATCHMENT_KM < km else None
            todo.append({**r, "_osm": osm, "_beyond": beyond})
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
            for field, value in (("latitude", str(lat)), ("longitude", str(lon)), ("geocode_precision", r["precision"]), ("location_source", where),
                                 *extra_facts(r)):
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", oid, field, value, today), "organisation", oid, field, value, record))
            if r.get("_beyond"):
                beyond_review(con, oid, r, path, *r["_beyond"])
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def nearest_km(campuses: dict, lat: float, lon: float) -> tuple[str, float]:
    from recompute_campus_distances import hav  # same directory; the distance the recompute will store
    dists = {c: round(hav(lat, lon, *xy), 1) for c, xy in campuses.items()}
    near = min(dists, key=dists.get)
    return near, dists[near]


def stored_source(con, o) -> str | None:
    """The location_source fact recorded with the organisation's stored latitude, or None when none was recorded."""
    row = con.execute(
        "SELECT value FROM facts WHERE entity_type='organisation' AND entity_id=? AND field='location_source' AND record_id IN "
        "(SELECT record_id FROM facts WHERE entity_type='organisation' AND entity_id=? AND field='latitude' AND value=?)",
        (o["organisation_id"], o["organisation_id"], str(o["latitude"]))).fetchone()
    return row[0] if row else None


def extra_facts(r: dict) -> list[tuple[str, str]]:
    return [("geocode_confidence" if k == "confidence" else k, str(r[k])) for k in EXTRA_FACTS if r.get(k)]


def beyond_review(con, oid: str, r: dict, path: Path, before, after) -> None:
    """A lead the new point takes beyond the catchment is kept and labelled (user instruction, 13 October 2026)."""
    con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                (hid("D", "beyond-catchment", oid, path.name), "Beyond the catchment after geolocation", oid, "", "distance_km",
                 f"{before[0]} {before[1]} km -> {after[0]} {after[1]} km ({r['source_type']})",
                 f"Kept and labelled: its own point ({path.relative_to(ROOT).as_posix()} line {r['_line']}) lies beyond the "
                 f"{CATCHMENT_KM:g} km catchment. Distance never removes a lead; review its priority."))


def plan_replace(con, rows) -> tuple[list[dict], list[dict]]:
    """--replace: the lines whose stored master point is still the estimate they name (see the module docstring)."""
    campuses = {r["name"]: (r["latitude"], r["longitude"]) for r in con.execute("SELECT name, latitude, longitude FROM campuses")}
    todo, skipped = [], []
    for r in rows:
        why = ""
        o = con.execute("SELECT * FROM organisations WHERE organisation_id=?", (r["organisation_id"],)).fetchone()
        missing = [k for k in REPLACE_REQUIRED if r.get(k) in (None, "")]
        if missing:
            why = f"a correction line needs {', '.join(missing)}"
        elif o is None:
            why = "no such organisation"
        elif o["name"] != r["organisation_name"]:
            why = f"name differs from the master ('{o['name']}')"
        else:
            try:
                stored = (float(o["latitude"]), float(o["longitude"]))
            except (TypeError, ValueError):
                stored = None
            if stored is None:
                why = "has no stored point to replace (use the default run, which fills empty points)"
            elif abs(stored[0] - float(r["old_latitude"])) > 1e-6 or abs(stored[1] - float(r["old_longitude"])) > 1e-6:
                why = f"the stored point ({stored[0]}, {stored[1]}) is not the old point the line names"
            elif (o["geocode_precision"] or "") not in REPLACEABLE_PRECISION:
                why = f"the stored point has precision '{o['geocode_precision']}', not an estimate"
            elif (o["geocode_precision"] or "") != (r.get("old_precision") or ""):
                why = f"the stored precision '{o['geocode_precision']}' is not the line's old_precision '{r.get('old_precision')}'"
            else:
                source = stored_source(con, o)
                if source is None:
                    if r["old_location_source"] != NO_SOURCE:
                        why = f"the stored point has no location_source fact; the line must name it '{NO_SOURCE}'"
                elif not source.startswith(REPLACEABLE):
                    why = f"the stored point's source is not an estimate this path replaces ({source})"
                elif source != r["old_location_source"]:
                    why = f"the stored point's source differs from the line's old_location_source ({source})"
        if not why:
            before = float(o["distance_km"]) if str(o["distance_km"] or "").replace(".", "", 1).isdigit() else None
            campus, km = nearest_km(campuses, float(r["latitude"]), float(r["longitude"]))
            if before is not None and before <= CATCHMENT_KM < km and not r.get("beyond_catchment"):
                why = (f"the new point is {km} km from {campus}, beyond the {CATCHMENT_KM:g} km catchment the lead was in ({before} km): "
                       "a correction never removes a lead, so the line must carry a reviewed beyond_catchment note (the lead is kept and labelled)")
            else:
                todo.append({**r, "_before": (o["campus"], before, o["transport_band"]), "_after": (campus, km)})
                continue
        skipped.append({"line": r["_line"], "name": r["organisation_name"], "why": why})
    return todo, skipped


def apply_replace(path: Path, todo: list[dict]) -> None:
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
            record = hid("R", "geocode-correction", path.name, oid)
            keep = {k: v for k, v in r.items() if not k.startswith("_")}
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source, f"line {r['_line']}: {r['organisation_name']}", json.dumps(keep, ensure_ascii=False)))
            if not con.execute("SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?", (oid, record)).fetchone():
                con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))
            lat, lon = round(float(r["latitude"]), 6), round(float(r["longitude"]), 6)
            con.execute("UPDATE organisations SET latitude=?, longitude=?, geocode_precision=? WHERE organisation_id=?", (lat, lon, r["precision"], oid))
            where = f"{r['source_type']}: {r['source_url']} (fetched {r['fetched_on']})"
            old = (f"{r['old_latitude']}, {r['old_longitude']} ({r['old_precision']}; {r['old_location_source']}; record {r.get('old_record_id') or 'not named'}), "
                   f"replaced {today} by {where}, {r.get('km_moved', '')} km away")
            for field, value in (("latitude", str(lat)), ("longitude", str(lon)), ("geocode_precision", r["precision"]), ("location_source", where),
                                 ("superseded_location", old), *extra_facts(r)):
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", oid, field, value, today), "organisation", oid, field, value, record))
            if r.get("beyond_catchment"):
                beyond_review(con, oid, r, path, r["_before"], r["_after"])
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "location-correction", oid, path.name), "Location corrected", oid, "", "latitude; longitude",
                         f"{r['old_latitude']}, {r['old_longitude']} ({r['old_precision']}, {r['old_location_source'].split(':')[0]}) -> {lat}, {lon} "
                         f"({r['precision']}, {r['source_type']} '{r.get('listing_name') or r['organisation_name']}'), {r.get('km_moved', '')} km",
                         f"Applied from {path.relative_to(ROOT).as_posix()} line {r['_line']}: {r['basis']} The old point is kept as the fact "
                         "superseded_location. Check drafts that name the nearest campus."))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
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
    parser.add_argument("--replace", action="store_true",
                        help="apply a reviewed corrections file (named with --file): replace estimated master points; see the docstring")
    args = parser.parse_args()
    if args.replace and not args.file:
        parser.error("--replace needs --file data/raw/geocode-research/geocodes_corrections_<date>.jsonl")
    path = args.file or max(p for p in RAW.glob("geocodes_*.jsonl") if not p.name.startswith("geocodes_corrections_"))
    path = path.resolve()
    rows, problems = load(path)
    if problems:
        print("Refused: fix these lines first:\n  " + "\n  ".join(problems))
        return 1
    if args.replace:
        lines = [r for r in rows if r.get("status") == "placed" and r.get("replace") is True]
        others = [r["_line"] for r in rows if r not in lines]
        if others or any(r["db"] != "master" for r in lines):
            print(f"Refused: a corrections file holds only master lines with status 'placed' and replace: true (lines {others or 'db'}).")
            return 1
        con = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        todo, skipped = plan_replace(con, lines)
        con.close()
        report = {"file": path.relative_to(ROOT).as_posix(), "mode": "replace", "lines": len(rows), "to_replace": len(todo), "skipped": skipped,
                  "changes": [{"line": r["_line"], "organisation_id": r["organisation_id"], "name": r["organisation_name"],
                               "old": [r["old_latitude"], r["old_longitude"], r["old_precision"]], "new": [r["latitude"], r["longitude"], r["precision"]],
                               "km_moved": r.get("km_moved"), "campus_before": r["_before"], "nearest_after": r["_after"]} for r in todo]}
        if args.apply and todo:
            apply_replace(path, todo)
            report["applied"] = len(todo)
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        PREVIEW.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "changes"}, ensure_ascii=False, indent=1))
        for c in report["changes"]:
            print(f"  {c['name'][:40]:40} {c['km_moved']:>5} km  {c['campus_before'][0]} {c['campus_before'][1]} km -> {c['nearest_after'][0]} {c['nearest_after'][1]} km")
        print((f"Applied {report.get('applied', 0)}." if args.apply else "Preview only; --apply writes.") + f" Details: {PREVIEW.relative_to(ROOT)}")
        return 0
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
