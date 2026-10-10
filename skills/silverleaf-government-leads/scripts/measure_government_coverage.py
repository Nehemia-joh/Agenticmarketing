#!/usr/bin/env python3
"""Count the data points a government run holds per office, stratified by office level. No network calls.

Reads runtime/government/<run-id>/final.json (build_government_run.py) and prints a Markdown table, or writes it with
--out. Strata: region; district; council, pilot (core) and other; ward by distance to the nearest campus (up to 10 km,
10 to 20 km, over 20 km, not located); village. Data points per stratum, as offices with the point:

- holder: the office's lead post (Regional Commissioner, District Commissioner, Council Director, WEO, VEO) has a
  named holder with a source date; "verified" counts the ones the build marks verified
- quick: at least one quick-decision post named (regional: RAS or education; district: DAS; council: education,
  community development or social welfare head; ward: ward community development officer; village: chair);
  quick_posts counts those named posts
- email, phone, postal: the office's official email (or a role inbox on one of its posts), office phone, P.O. box
- physical: a physical address in words; point: an office point at address precision (official map or mapped office)
- geocode: the precision counts
- census: 2022 census population on the office (councils and wards)
- signals: official news or notices with a convening tag that name the office (council and region: their own site's
  items; district, ward and village: items on the parent council's or region's site whose title names the unit)
Use it before and after an enrichment round, so the coverage log can show both.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict

import gov_lib as G

LEAD = {"region": "regional_commissioner", "district": "district_commissioner", "council": "council_director",
        "ward": "ward_executive_officer", "village": "village_executive_officer"}
QUICK = {"region": {"regional_administrative_secretary", "regional_education", "regional_community_development"},
         "district": {"district_administrative_secretary"},
         "council": {"primary_education_head", "community_development_head", "social_welfare_officer"},
         "ward": {"ward_community_development_officer"}, "village": {"village_chair"}}
COLUMNS = ["offices", "holder", "verified", "quick", "quick_posts", "email", "phone", "postal", "physical", "point", "census", "signals"]


def stratum(o: dict) -> str:
    level = o["office_level"]
    if level == "council":
        return "3a council: pilot" if o.get("core_council") else "3b council: other"
    if level == "ward":
        d = o.get("distance_km")
        if d is None:
            return "4d ward: not located"
        return "4a ward: up to 10 km" if d <= 10 else ("4b ward: 10-20 km" if d <= 20 else "4c ward: over 20 km")
    return {"region": "1 region", "district": "2 district", "village": "5 village"}[level]


def measure(final: dict, cfg: dict) -> tuple[dict, dict]:
    posts = defaultdict(list)
    for p in final["posts"]:
        posts[p["office_key"]].append(p)
    host_of = {c["name"]: c["host"] for c in cfg["councils"]}
    region_host = {r["region"]: r["host"] for r in cfg["regions"]}
    signals_by_host = defaultdict(list)
    for s in final.get("signals", []):
        signals_by_host[s["host"]].append(s)
    rows, precision = defaultdict(Counter), defaultdict(Counter)
    for o in final["offices"]:
        level, key = o["office_level"], stratum(o)
        mine = posts[o["record_key"]]
        row = rows[key]
        row["offices"] += 1
        lead = next((p for p in mine if p["post_key"] == LEAD[level]), None)
        if lead and lead.get("holder_name") and lead.get("holder_source_date"):
            row["holder"] += 1
            row["verified"] += lead.get("verification_status") == "verified"
        quick = sum(1 for p in mine if p["post_key"] in QUICK[level] and p.get("holder_name"))
        row["quick"] += quick > 0
        row["quick_posts"] += quick
        row["email"] += bool(o.get("public_email") or any(p.get("published_role_email") for p in mine))
        row["phone"] += bool(o.get("public_phone"))
        row["postal"] += bool(o.get("po_box"))
        row["physical"] += bool(o.get("physical_address"))
        row["point"] += o.get("geocode_precision") == "address"
        row["census"] += bool(o.get("census_2022_population"))
        precision[key][o.get("geocode_precision") or "none"] += 1
        if level in ("council", "region"):
            host = host_of.get(o.get("council_name")) if level == "council" else region_host.get(o["region"])
            row["signals"] += bool(signals_by_host.get(host))
        else:
            hosts = [host_of.get(o.get("council_name"), ""), region_host.get(o.get("region"), "")]
            if level == "district":
                hosts += [c["host"] for c in cfg["councils"] if c["admin_district"] == o["admin_unit_name"]]
            unit = re.escape(o["admin_unit_name"])
            row["signals"] += any(re.search(rf"\b{unit}\b", s["title"], re.I) for h in hosts for s in signals_by_host.get(h, []))
    return rows, precision


def table(rows: dict, precision: dict) -> str:
    out = ["| Stratum | " + " | ".join(COLUMNS) + " | geocode precision |", "|---|" + "---:|" * len(COLUMNS) + "---|"]
    total = Counter()
    for key in sorted(rows):
        total.update(rows[key])
        geo = ", ".join(f"{k} {v}" for k, v in sorted(precision[key].items()))
        out.append(f"| {key} | " + " | ".join(str(rows[key][c]) for c in COLUMNS) + f" | {geo} |")
    out.append("| **all** | " + " | ".join(f"**{total[c]}**" for c in COLUMNS) + " | |")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--out", help="write the table to this file (Markdown) instead of printing it")
    parser.add_argument("--final", help="measure this final.json instead of the run's (for example a copy kept from before a round)")
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    final = json.loads(open(args.final or cfg["paths"]["work"] / "final.json", encoding="utf-8").read())
    text = table(*measure(final, cfg))
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
