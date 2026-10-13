#!/usr/bin/env python3
"""Recompute the company master's nearest campus, distance, transport band and radius tier from the campuses table.

Run after the campus points change (on 2026-10-11 they moved from Nominatim centroids to the map pins on Silverleaf's own
website, 0.1-1.2 km). The master stores coordinates for only some organisations; the rest were placed at import by their
locality (scripts/collection/build_partner_leads.py, data/reference/lead-gazetteer.txt). For each organisation:
- its own coordinates (organisations.latitude/longitude, else latitude/longitude facts) are used when present;
- otherwise its locality or address is placed with the importer's gazetteer, and the point is used only when it reproduces
  the stored distance from the stored campus under the previous campus points (to 0.2 km): proof it is the point the
  importer used;
- otherwise the stored distance is kept, and only its band and tier are recomputed from it (fixing stale bands).
Ward precision (geocode_precision 'ward', VICOBA savings groups, decided 13 October 2026): the point is the ward's reference point in
the government run (admin_units latitude/longitude), found by the group's linked ward CDO office (fact linked_introducer_ref) or by
its council and ward facts; the campus, distance, band and tier are computed from it, and a stored point that differs from the
ward's current reference point is replaced by it (the precision stays 'ward'). A ward the government run does not place keeps the
stored point. A ward-precision distance is an estimate: drafts never state it (scripts/messaging/, T4). --government-db names a
copy of the run (default outputs/runs/arusha-government-2026-09/lead-database.sqlite, read only).
Bands: 0-5, 6-10, 11-15, 16-20, 21-25, 26-40, >40 km. Tiers: Core (<=10 km), Outer (<=25 km), >25 km.
Distance never removes a company from the master: the reach rank reads the band (scripts/master/rank_employer_reach.py).
Preview by default; --apply writes in one transaction and records outputs/reports/campus-distance-recompute.json.
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
REPORT = ROOT / "outputs" / "reports" / "campus-distance-recompute.json"
# The campus points every stored distance was computed from until 2026-10-11 (Nominatim centroids).
PREVIOUS = {"Usa River": (-3.3645, 36.8632), "Arusha City": (-3.3528, 36.6613), "Ilboru": (-3.3465, 36.6922),
            "Kijenge": (-3.3837, 36.7100), "Boma Ngombe": (-3.3342, 37.1383)}


def hav(a, b, c, d) -> float:
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin(math.radians(c - a) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def campus_key(name) -> str:
    """'Arusha City (Sakina)' -> 'Arusha City'; "Boma Ng'ombe" -> 'Boma Ngombe'."""
    n = re.sub(r"\s*\(.*\)", "", str(name or "")).replace("'", "").strip()
    return n


def band(km: float) -> str:
    for limit, label in ((5, "0-5 km"), (10, "6-10 km"), (15, "11-15 km"), (20, "16-20 km"), (25, "21-25 km"), (40, "26-40 km")):
        if km <= limit:
            return label
    return ">40 km"


def tier(km: float) -> str:
    return "Core (≤10 km)" if km <= 10 else "Outer (≤25 km)" if km <= 25 else ">25 km"


def gazetteer() -> dict:
    """The importer's gazetteer: data/reference/lead-gazetteer.txt plus the overrides in build_partner_leads.py."""
    gaz = {}
    for line in (ROOT / "data" / "reference" / "lead-gazetteer.txt").read_text(encoding="utf-8").splitlines():
        p = line.split("|")
        if len(p) >= 3 and p[1] and p[1] != "ERR":
            gaz[p[0].split(",")[0].strip().lower()] = (float(p[1]), float(p[2]))
    tree = ast.parse((ROOT / "scripts" / "collection" / "build_partner_leads.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "update" and getattr(node.func.value, "id", "") == "GAZ":
            gaz.update(ast.literal_eval(node.args[0]))
    return gaz


def candidates(text: str, gaz: dict) -> list:
    """Gazetteer points the importer's locate() could have chosen for this text, most specific first."""
    t = " " + re.sub(r"\s+", " ", re.sub(r"[^a-z' ]", " ", text.lower())) + " "
    keys = sorted((k for k in gaz if k not in ("arusha", "kilimanjaro region", "moshi")), key=len, reverse=True)
    out = [gaz[k] for k in keys if gaz[k] and (" " + k + " " in t or (len(k) > 5 and k in t))]
    for k, words in (("moshi", (" moshi ",)), ("usa river", (" usa river ",)), ("arusha", (" arusha ",))):
        if gaz.get(k) and any(w in t for w in words):
            out.append(gaz[k])
    return out


def ward_points(con: sqlite3.Connection, government_db: str | None) -> tuple[dict, Counter]:
    """organisation_id -> (lat, lon, admin unit key) for ward-precision organisations, from the government run's ward reference points."""
    ward = [r["organisation_id"] for r in con.execute("SELECT organisation_id FROM organisations WHERE geocode_precision='ward'")]
    stats, out = Counter(), {}
    if not ward:
        return out, stats
    import sys
    sys.path.insert(0, str(ROOT / "scripts" / "master"))
    import link_vicoba_introducers as L  # noqa: E402  (the government-run reader shared with the introducer links)
    facts: dict[str, dict] = {}
    marks = ",".join("?" * len(ward))
    for r in con.execute(f"SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' AND entity_id IN ({marks}) "
                         "AND field IN ('council','ward','linked_introducer_kind','linked_introducer_ref') ORDER BY rowid", ward):
        facts.setdefault(r["entity_id"], {})[r["field"]] = r["value"]  # the last value recorded
    runs = L.parse_gov(government_db)
    run = next(iter(runs), L.DEFAULT_RUN)
    gov = L.GovRuns(runs)
    for oid in ward:
        f = facts.get(oid, {})
        unit = None
        if f.get("linked_introducer_kind") == "cdo_ward":
            office, _ = gov.office(f.get("linked_introducer_ref", ""))
            unit = office["unit"] if office else None
        if unit is None:
            unit = gov.ward_unit(run, f.get("council", ""), f.get("ward", ""))
        if gov.con(run) is None:
            stats["government run not found (stored points kept)"] += 1
        elif unit and unit.get("latitude") is not None and unit.get("longitude") is not None:
            out[oid] = (float(unit["latitude"]), float(unit["longitude"]), unit["unit_key"])
            stats["from ward reference point"] += 1
        elif unit:
            stats["ward has no reference point yet (stored point kept)"] += 1
        else:
            stats["ward not found in the government run"] += 1
    return out, stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--database", default=str(MASTER))
    ap.add_argument("--government-db", help="a copy of the government run for ward reference points: <path> or <run-id>=<path> (read only)")
    ap.add_argument("--report", default=str(REPORT), help="where --apply records the run (keep the campus-correction record of "
                                                          "2026-10-11 by giving a later run its own file)")
    args = ap.parse_args()
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    campuses = {r["name"]: (r["latitude"], r["longitude"]) for r in con.execute("SELECT name, latitude, longitude FROM campuses")}
    facts = {}
    for r in con.execute("SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' AND field IN ('latitude','longitude')"):
        facts.setdefault(r["entity_id"], {})[r["field"]] = r["value"]
    gaz = gazetteer()
    wards, ward_stats = ward_points(con, args.government_db)
    updates, stats, moved, ward_moves = [], Counter(), [], []
    for o in con.execute("SELECT organisation_id, name, campus, distance_km, transport_band, radius_tier, latitude, longitude, locality, address FROM organisations"):
        stored = float(o["distance_km"]) if str(o["distance_km"] or "").replace(".", "", 1).isdigit() else None
        point, basis = None, ""
        f = facts.get(o["organisation_id"], {})
        if o["organisation_id"] in wards:
            lat, lon, unit_key = wards[o["organisation_id"]]
            point, basis = (lat, lon), "ward reference point"
            if o["latitude"] is None or o["longitude"] is None or abs(o["latitude"] - lat) > 1e-6 or abs(o["longitude"] - lon) > 1e-6:
                ward_moves.append((lat, lon, o["organisation_id"]))
        for lat, lon in (() if point else ((o["latitude"], o["longitude"]), (f.get("latitude"), f.get("longitude")))):
            try:
                point, basis = (float(lat), float(lon)), "coordinates"
                break
            except (TypeError, ValueError):
                continue
        if point is None and stored is not None and campus_key(o["campus"]) in PREVIOUS:
            old = PREVIOUS[campus_key(o["campus"])]
            for p in candidates(f"{o['locality'] or ''} {o['address'] or ''}", gaz):
                if abs(round(hav(*p, *old), 1) - stored) <= 0.2:
                    point, basis = p, "gazetteer point reproduced"
                    break
        if point:
            dists = {c: round(hav(*point, *xy), 1) for c, xy in campuses.items()}
            near = min(dists, key=dists.get)
            km = dists[near]
        elif stored is not None:
            near, km, basis = campus_key(o["campus"]) or o["campus"], stored, "stored distance kept"
        else:
            stats["no location"] += 1
            continue
        stats[basis] += 1
        label = o["campus"] if campus_key(o["campus"]) == near else near  # an unchanged campus keeps its stored label
        new = (label, km, band(km), tier(km))
        if (o["campus"], stored, o["transport_band"], o["radius_tier"]) != new:
            updates.append((*new, o["organisation_id"]))
            if campus_key(o["campus"]) != near:
                moved.append(f"{o['name']}: {o['campus']} -> {near} ({km} km)")
            if stored is not None and stored <= 25 < km:
                stats["moved beyond 25 km (kept; distance never removes a company)"] += 1
    stats["records to update"] = len(updates)
    stats["nearest campus changed"] = len(moved)
    ward_stats["stored point replaced by the ward reference point"] = len(ward_moves)
    report = {"stats": dict(stats), "nearest_campus_changed": moved, "campuses": campuses,
              "ward_precision": {**dict(ward_stats), "note": "ward-precision distances are estimates: drafts never state them"}}
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if args.apply:
        with con:
            con.executemany("UPDATE organisations SET campus=?, distance_km=?, transport_band=?, radius_tier=? WHERE organisation_id=?", updates)
            con.executemany("UPDATE organisations SET latitude=?, longitude=? WHERE organisation_id=? AND geocode_precision='ward'", ward_moves)
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("applied", len(updates))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
