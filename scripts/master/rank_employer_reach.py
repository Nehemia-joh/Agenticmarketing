#!/usr/bin/env python3
"""Rank the company master's employers by likely reach: how many staff a staff education benefit could reach, and how close they are.

A staff benefit is worth as much as the staff it reaches, so enrichment and outreach go deep on the top tier. The score uses only what
the master records:
- kind of employer: hospital or clinic 4, college or university 4, hotel, lodge or camp 3, bank or other company 3, NGO 2, public body 1,
  safari operator or travel agency 1;
- published staff numbers (headcount): 100 or more +4, 30 or more +3, 10 or more +1;
- a verified workforce or staff-welfare fact (hook) +2;
- named people on file: 5 or more +1;
- distance to the nearest campus: 0-5 km +2, 6-10 km +1, over 40 km -3;
- desk-research tier A +1.
Tiers: P1 the top 100 by score, P2 the next 150, P3 the rest; X for plans held as outside the catchment or not an employer.
Writes the table employer_reach (organisation_id, score, tier, factors, ranked_on) for every company with a chosen draft (savings groups
are left out). Preview by default; --apply replaces the table in one transaction. Afterwards run export_master_workbook_data.py,
npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
HOSPITALITY = re.compile(r"hotel|lodge|guest|camp|resort|villa", re.I)
KIND_POINTS = {"Healthcare employers": 4, "Education employers": 4, "Corporate employers": 3, "NGO employers": 2, "Public-sector employers": 1}
P1, P2 = 100, 150


def score_of(plan: dict, org: dict, hooked: set, people: Counter) -> tuple[float, list[str]]:
    factors = []
    if plan["segment"] == "Tourism employers":
        hotel = bool(HOSPITALITY.search(f"{org['name']} {org['segment'] or ''}"))
        points = 3 if hotel else 1
        factors.append(f"{'hotel or lodge' if hotel else 'safari operator'} {points}")
    else:
        points = KIND_POINTS.get(plan["segment"], 1)
        factors.append(f"{plan['segment'].replace(' employers', '').lower()} {points}")
    score = float(points)
    try:
        head = float(org["headcount"] or 0)
    except ValueError:
        head = 0
    if head:
        bonus = 4 if head >= 100 else 3 if head >= 30 else 1 if head >= 10 else 0
        if bonus:
            score += bonus
            factors.append(f"{int(head)} staff published +{bonus}")
    if org["organisation_id"] in hooked:
        score += 2
        factors.append("verified workforce or staff-welfare fact +2")
    if people[org["organisation_id"]] >= 5:
        score += 1
        factors.append(f"{people[org['organisation_id']]} named people on file +1")
    band = org["transport_band"] or ""
    bonus = {"0-5 km": 2, "6-10 km": 1, ">40 km": -3}.get(band, 0)
    if bonus:
        score += bonus
        factors.append(f"{band} from a campus {'+' if bonus > 0 else ''}{bonus}")
    if org["desk_tier"] == "A":
        score += 1
        factors.append("desk tier A +1")
    return score, factors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    hooked = {r[0] for r in con.execute("SELECT DISTINCT organisation_id FROM outreach_plans WHERE hook_type IN ('workforce','staff_welfare') "
                                        "AND hook_status LIKE 'Verified%' AND COALESCE(hook,'')<>''")}
    people = Counter(r[0] for r in con.execute("SELECT organisation_id FROM contacts WHERE COALESCE(name,'')<>''"))
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review' AND segment NOT IN ('SACCOS members','Introducers')")]
    ranked = []
    for p in plans:
        org = orgs[p["organisation_id"]]
        score, factors = score_of(p, org, hooked, people)
        held = "Outside the Arusha-Kilimanjaro catchment or not an employer" in (p["missing_information"] or "")
        ranked.append({"organisation_id": p["organisation_id"], "name": org["name"], "score": score, "factors": "; ".join(factors), "held": held,
                       "distance": float(org["distance_km"]) if str(org["distance_km"] or "").replace(".", "", 1).isdigit() else 999.0})
    ranked.sort(key=lambda r: (r["held"], -r["score"], r["distance"], r["name"]))
    position = 0
    for r in ranked:
        if r["held"]:
            r["tier"] = "X"
            continue
        position += 1
        r["tier"] = "P1" if position <= P1 else "P2" if position <= P1 + P2 else "P3"
    summary = {"companies": len(ranked), "tiers": dict(Counter(r["tier"] for r in ranked)),
               "P1 lowest score": min((r["score"] for r in ranked if r["tier"] == "P1"), default=None)}
    print(json.dumps(summary, indent=1))
    if not args.apply:
        for r in ranked[:15]:
            print(f"  {r['tier']} {r['score']:>4} {r['name'][:40]} | {r['factors']}")
        print("Preview only.")
        return 0
    today = date.today().isoformat()
    try:
        con.execute("BEGIN")
        con.execute("CREATE TABLE IF NOT EXISTS employer_reach (organisation_id TEXT PRIMARY KEY REFERENCES organisations(organisation_id), score REAL, "
                    "tier TEXT, factors TEXT, ranked_on TEXT)")
        con.execute("DELETE FROM employer_reach")
        con.executemany("INSERT INTO employer_reach VALUES (?,?,?,?,?)", [(r["organisation_id"], r["score"], r["tier"], r["factors"], today) for r in ranked])
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
