#!/usr/bin/env python3
"""Record each lead's Google Maps status, the corroborating listings and the location discrepancies of a round in the master.

The user's rule of 13 October 2026: coordinates found another way are never lost; a lead Google Maps does not list keeps its
point and is flagged "not registered on Google Maps"; where Google Maps and another source disagree, nobody chooses alone.
This script never changes a point. Points change only through scripts/master/apply_geocodes.py (the fills, and --replace for
the corrections that scripts/maps/build_gmaps_round.py wrote under the location precedence).

  python scripts/maps/apply_gmaps_status.py --round 2026-10-13d              # preview (runtime/geocode/gmaps-status-preview.json)
  python scripts/maps/apply_gmaps_status.py --round 2026-10-13d --apply      # one transaction
  python scripts/maps/apply_gmaps_status.py --round 2026-10-11 --round 2026-10-11b ...   # several rounds; earlier rounds take status only

For each round <date><tag> it reads:
- data/raw/gap-census/google_maps_enrich_<date><tag>.jsonl: one status per lead, stored as the fact google_maps_status with
  its date, tied to one source record per line of the enrich file:
    listed <date>: '<listing>' <Maps URL>                 an accepted listing;
    not_found <date>: not registered on Google Maps ...   no matching listing (the lead keeps whatever point it has);
    review <date>: <reason>                               default pin, wrong place, name unconfirmed ...
  The workbook shows the latest status per lead in the Organisations sheet's google_maps column.
  A listed lead whose listing lies within the agreement distance of its stored point reads "listed <date>: confirmed at
  stored point; ..." (from the location checks file). Same-name listings that build_gmaps_round.py recorded as other offices
  (the enrich line's candidates with role 'other office') become the facts other_office: name, point, URL and distance.
- data/raw/geocode-research/location_checks_gmaps_<date><tag>.jsonl (when it exists): each 'corroborates' line becomes the fact
  location_corroboration (the listing, its point and its distance from the kept point).
- data/raw/geocode-research/location_discrepancies_<date>.jsonl (the round's lines): the review item
  "Location discrepancy: <website | OpenStreetMap | Google Maps | estimate> vs Google Maps" with both points, both sources and the
  distance, and the fact location_discrepancy. The point is not changed; the user and the orchestrator decide.
--discrepancies <file> takes discrepancy lines from another file (for example a reviewed list from build_gmaps_round.py --retro).
Master only. Afterwards: export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_gmaps_round as B  # noqa: E402  (status_of: the one mapping from verdict to status)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
ENRICH = ROOT / "data" / "raw" / "gap-census"
GEO = ROOT / "data" / "raw" / "geocode-research"
PREVIEW = ROOT / "runtime" / "geocode" / "gmaps-status-preview.json"
LABEL = re.compile(r"^(\d{4}-\d\d-\d\d)([a-z]*)$")


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def lines(path: Path) -> list[tuple[int, dict]]:
    return [(n, json.loads(x)) for n, x in enumerate(path.read_text(encoding="utf-8").splitlines(), 1) if x.strip()]


def plan(con, rounds: list[str], extra_disc: list[Path]) -> dict:
    names = {r[0]: r[1] for r in con.execute("SELECT organisation_id, name FROM organisations")}
    files, statuses, corroborations, discrepancies, missing, offices = {}, [], [], [], [], []
    for label in rounds:
        m = LABEL.match(label)
        if not m:
            raise SystemExit(f"--round {label}: expected <date><tag>, for example 2026-10-13d")
        day = m.group(1)
        enrich = ENRICH / f"google_maps_enrich_{label}.jsonl"
        if not enrich.exists():
            raise SystemExit(f"no {enrich.relative_to(ROOT)}")
        files[enrich] = None
        checks = GEO / f"location_checks_gmaps_{label}.jsonl"
        confirmed = {c["organisation_id"] for _, c in lines(checks) if c.get("match") == "confirmed at stored point"} if checks.exists() else set()
        for n, e in lines(enrich):
            oid = e.get("organisation_id")
            if oid not in names:
                missing.append(f"{enrich.name} line {n}: {oid} {e.get('organisation_name')}")
                continue
            status, detail = B.status_of(e)
            if status == "listed" and oid in confirmed:
                detail = f"confirmed at stored point; {detail}"
            if status == "listed":
                offices += [{"file": enrich, "line": n, "organisation_id": oid, "name": names[oid], "date": e.get("fetched_on") or day, **c}
                            for c in e.get("candidates", []) if c.get("role") == "other office"]
            statuses.append({"file": enrich, "line": n, "organisation_id": oid, "name": names[oid], "status": status,
                             "value": f"{status} {e.get('fetched_on') or day}: {detail}", "payload": e})
        if checks.exists():
            files[checks] = None
            for n, c in lines(checks):
                if c["outcome"] == "corroborates" and c["organisation_id"] in names:
                    corroborations.append({"file": checks, "line": n, **c})
        disc = GEO / f"location_discrepancies_{day}.jsonl"
        if disc.exists():
            mine = [(n, d) for n, d in lines(disc) if d.get("round") == label]
            if mine:
                files[disc] = None
                discrepancies += [{"file": disc, "line": n, **d} for n, d in mine if d["organisation_id"] in names]
    for path in extra_disc:
        files[path.resolve()] = None
        discrepancies += [{"file": path.resolve(), "line": n, **d} for n, d in lines(path)
                          if d.get("outcome", "discrepancy") == "discrepancy" and d["organisation_id"] in names]
    return {"files": list(files), "statuses": statuses, "corroborations": corroborations, "discrepancies": discrepancies, "missing": missing,
            "offices": offices}


def fact(con, oid, field, value, record) -> None:
    con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                (hid("X", oid, field, value), "organisation", oid, field, value, record))


def link(con, oid, record) -> None:
    if not con.execute("SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?", (oid, record)).fetchone():
        con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def apply(database: Path, p: dict) -> None:
    con = sqlite3.connect(database)
    try:
        con.execute("BEGIN")
        source = {}
        for path in p["files"]:
            payload = path.read_bytes()
            source[path] = hid("F", "gmaps-status", path.name)
            con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                        (source[path], rel(path), hashlib.sha256(payload).hexdigest(), len(payload), "jsonl", "utf-8", payload))

        def record(kind, item, payload):
            rid = hid("R", kind, item["file"].name, item["line"], item["organisation_id"])
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (rid, source[item["file"]], f"line {item['line']}: {item.get('name') or item.get('organisation_name')}",
                         json.dumps(payload, ensure_ascii=False)))
            link(con, item["organisation_id"], rid)
            return rid

        for s in p["statuses"]:
            fact(con, s["organisation_id"], "google_maps_status", s["value"], record("gmaps-status", s, s["payload"]))
        for f in p["offices"]:
            value = (f"Google Maps listing '{f['name']}' at {f['latitude']}, {f['longitude']} ({f['address'] or 'no address'}); {f['url']}"
                     + (f"; {f['distance_m']} m from the stored point" if f.get("distance_m") is not None else "") + f" ({f['date']})")
            rid = hid("R", "gmaps-status", f["file"].name, f["line"], f["organisation_id"])  # the status record of the same enrich line
            fact(con, f["organisation_id"], "other_office", value, rid)
        for c in p["corroborations"]:
            payload = {k: v for k, v in c.items() if k not in ("file", "line")}
            value = (f"Google Maps listing '{c['google_listing']}' at {c['google_latitude']}, {c['google_longitude']} is {c['distance_m']} m from the "
                     f"kept {c['stored_source_label']} point {c['stored_latitude']}, {c['stored_longitude']} ({c['stored_source']}); {c['google_url']} "
                     f"({c['date']}, agreement {c['agreement_m']} m)")
            fact(con, c["organisation_id"], "location_corroboration", value, record("gmaps-corroboration", c, payload))
        for d in p["discrepancies"]:
            payload = {k: v for k, v in d.items() if k not in ("file", "line")}
            rid = record("gmaps-discrepancy", d, payload)
            both = (f"{d['stored_source_label']} {d['stored_latitude']}, {d['stored_longitude']} ({d['stored_precision']}; {d['stored_source']}) vs "
                    f"Google Maps '{d['google_listing']}' {d['google_latitude']}, {d['google_longitude']} ({d['google_url']}): {d['distance_m']} m apart")
            if d.get("candidates"):
                both += ("; every same-name listing (a second office or a wrong point?): "
                         + "; ".join(f"#{c['index']} '{c['name']}' {c['latitude']}, {c['longitude']}, {c.get('distance_m')} m" for c in d["candidates"]))
            fact(con, d["organisation_id"], "location_discrepancy", f"{both} ({d.get('date') or d.get('file').name})", rid)
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "location-discrepancy", d["organisation_id"], d["google_latitude"], d["google_longitude"]),
                         f"Location discrepancy: {d['stored_source_label']} vs Google Maps", d["organisation_id"], "", "latitude; longitude", both,
                         f"Not changed. Beyond the {d.get('agreement_m', 500)} m agreement distance, so the user and the orchestrator decide which "
                         f"point to keep (rule of 13 October 2026). Source: {rel(d['file'])} line {d['line']}."))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--round", action="append", required=True, help="<date><tag>, for example 2026-10-13d (repeat for several)")
    parser.add_argument("--discrepancies", type=Path, action="append", default=[], help="extra discrepancy lines (a reviewed retro list)")
    parser.add_argument("--database", type=Path, default=MASTER, help="the master (default) or a trial copy")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    con = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    p = plan(con, args.round, args.discrepancies)
    con.close()
    report = {"rounds": args.round, "files": [rel(f) for f in p["files"]],
              "google_maps_status": dict(Counter(s["status"] for s in p["statuses"])),
              "corroborations": len(p["corroborations"]), "other_offices": len(p["offices"]), "discrepancies": len(p["discrepancies"]),
              "not_in_master": p["missing"],
              "discrepancy_list": [f"{d['organisation_name']} ({d['organisation_id']}): {d['stored_source_label']} vs Google Maps, {d['distance_m']} m"
                                   for d in p["discrepancies"]]}
    if args.apply:
        apply(args.database, p)
        report["applied"] = True
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print(("Applied. Then export_master_workbook_data.py, npm run build:workbook and verify_master.py." if args.apply
           else "Preview only; --apply writes.") + f" {rel(PREVIEW)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
