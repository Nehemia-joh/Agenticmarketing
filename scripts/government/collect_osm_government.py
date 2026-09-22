#!/usr/bin/env python3
"""Collect OpenStreetMap government offices in the catchment, politely, for the convening-office list.

Two small queries rather than one broad one (a broad regex query returned HTTP 504 in the welfare run): tagged
offices (office=government, amenity=townhall, government=*) and offices found by name (ofisi ya kata/kijiji/mtaa,
ward or village office, halmashauri, district or regional commissioner). Queries run one at a time through
gov_lib.overpass (>= 5 s apart, backoff, mirror fallback). OpenStreetMap tagging is mixed, so the build step
classifies every element and logs each exclusion (party offices, courts, police, prisons, military, health
facilities, schools, religious sites) with its reason.

Output: data/raw/government-research/osm_government_offices_<date>.json with both queries. Reused unless --refresh.
"""
from __future__ import annotations

import argparse
import json

import gov_lib as G


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    raw, date = cfg["paths"]["raw"], cfg["research_date"]
    out = raw / f"osm_government_offices_{date}.json"
    if out.exists() and not args.refresh:
        print(f"reuse {out.relative_to(G.ROOT)}")
        return 0
    s, w, n, e = cfg["bbox"]
    bbox = f"({s},{w},{n},{e})"
    queries = {
        "tags": f"""[out:json][timeout:120];
(
  nwr["office"="government"]{bbox};
  nwr["amenity"="townhall"]{bbox};
  nwr["government"]{bbox};
);
out center tags;""",
        "names": f"""[out:json][timeout:150];
(
  nwr["name"~"ofisi ya (kata|kijiji|mtaa|tarafa|wilaya|mkoa|mtendaji|serikali)|office ya (kata|kijiji|mtaa)|ward office|ward building|village office|mtendaji|halmashauri|district commissioner|regional commissioner|serikali ya (kijiji|mtaa)",i]{bbox};
);
out center tags;""",
    }
    elements: dict[str, dict] = {}
    runs = []
    for key, query in queries.items():
        body, endpoint = G.overpass(query)
        found = json.loads(body)["elements"]
        runs.append({"query_key": key, "endpoint": endpoint, "elements": len(found), "query": query})
        for el in found:
            lat = el.get("lat", (el.get("center") or {}).get("lat"))
            lon = el.get("lon", (el.get("center") or {}).get("lon"))
            osm_id = f"{el['type']}/{el['id']}"
            entry = elements.setdefault(osm_id, {"osm_id": osm_id, "lat": lat, "lon": lon, "tags": el.get("tags", {}), "found_by": []})
            entry["found_by"].append(key)
        print(f"{key}: {len(found)} elements via {endpoint}", flush=True)
    out.write_text(json.dumps({"retrieved": date, "queries": runs, "elements": sorted(elements.values(), key=lambda x: x["osm_id"])},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(elements)} unique elements -> {out.relative_to(G.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
