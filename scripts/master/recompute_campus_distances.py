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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--database", default=str(MASTER))
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
    updates, stats, moved = [], Counter(), []
    for o in con.execute("SELECT organisation_id, name, campus, distance_km, transport_band, radius_tier, latitude, longitude, locality, address FROM organisations"):
        stored = float(o["distance_km"]) if str(o["distance_km"] or "").replace(".", "", 1).isdigit() else None
        point, basis = None, ""
        f = facts.get(o["organisation_id"], {})
        for lat, lon in ((o["latitude"], o["longitude"]), (f.get("latitude"), f.get("longitude"))):
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
    report = {"stats": dict(stats), "nearest_campus_changed": moved, "campuses": campuses}
    print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
    if args.apply:
        with con:
            con.executemany("UPDATE organisations SET campus=?, distance_km=?, transport_band=?, radius_tier=? WHERE organisation_id=?", updates)
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print("applied", len(updates))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
