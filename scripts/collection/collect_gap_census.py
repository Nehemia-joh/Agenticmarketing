#!/usr/bin/env python3
"""Collect what OpenStreetMap records around Silverleaf's campuses, by category, for the campus gap census.

One Overpass query per category over the catchment box (the government run's box, -3.62..-3.10 S, 36.42..37.40 E, which holds
every point within 25 km of the five campuses). Categories:
  offices      every office=* feature (company, NGO, government, international, insurance, ...)
  industrial   factories and works: landuse=industrial, man_made=works, industrial=*, building=industrial with a name, craft=brewery etc.
  farms        landuse=farmyard/orchard/plant_nursery/greenhouse_horticulture/vineyard, place=farm, named farmland, crop/produce tags
  health       amenity=hospital/clinic/doctors/dentist, healthcare=hospital/clinic/centre/laboratory
  education    amenity=college/university, office=educational_institution, research institutes
  tourism      tourism=hotel/guest_house/hostel/motel/camp_site/chalet/apartment/resort, leisure=resort
  retail       shop=supermarket/mall/department_store/wholesale
  banks        amenity=bank, office=financial/insurance, amenity=bureau_de_change is left out
  aviation     aeroway=aerodrome/terminal/hangar/heliport, office=airline, airline offices and cargo
  worship      amenity=place_of_worship
  social       amenity=social_facility/childcare/kindergarten/orphanage, social_facility=*
  places       place=village/hamlet/neighbourhood/suburb/quarter (nodes, ways and relations; centres for areas)

Rate limits (skills/silverleaf-create-lead-list/references/research-rate-limits.md): one query at a time, at least 10 seconds apart,
[timeout:180], the repository's User-Agent, retries with backoff and the mirror fallback (gov_lib.overpass). The full answers are
cached in runtime/gap-census/overpass/ (git-ignored) and reused; --refresh fetches again. A slim extract of each answer (type, id,
point, the tags the census uses) is written to data/raw/gap-census/osm_<category>_<date>.json with the query and endpoint.

Data (c) OpenStreetMap contributors, ODbL 1.0.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "government"))
import gov_lib  # noqa: E402  (polite Overpass client with mirror fallback)

BBOX = "-3.62,36.42,-3.10,37.40"
# A whole-box query for every office timed out on all three endpoints (11 October 2026), so each category is asked in three
# boxes (Arusha, Usa River-Tengeru-KIA, Hai-Moshi) and the answers are merged.
BOXES = {"west": "-3.62,36.42,-3.10,36.78", "mid": "-3.62,36.78,-3.10,37.05", "east": "-3.62,37.05,-3.10,37.40"}
CACHE = ROOT / "runtime" / "gap-census" / "overpass"
RAW = ROOT / "data" / "raw" / "gap-census"
KEEP_TAGS = ("name", "name:en", "name:sw", "alt_name", "official_name", "short_name", "operator", "brand", "amenity", "office", "shop",
             "tourism", "leisure", "landuse", "industrial", "craft", "man_made", "product", "produce", "crop", "aeroway", "religion",
             "denomination", "social_facility", "social_facility:for", "healthcare", "building", "place", "is_in", "website", "url",
             "contact:website", "phone", "contact:phone", "contact:mobile", "email", "contact:email", "addr:street", "addr:housenumber",
             "addr:city", "addr:suburb", "addr:place", "addr:postcode", "addr:full", "postal_code", "disused", "disused:amenity",
             "abandoned", "operational_status", "opening_hours", "description", "government", "start_date", "iata", "icao",
             "isced:level", "school", "capacity", "beds", "stars", "rooms", "employees", "wikidata", "wikipedia", "fixme")


def q(*lines: str) -> str:
    """The query with a {bbox} placeholder, filled per box."""
    body = "".join(f"  {line}({{bbox}});\n" for line in lines)
    return f"[out:json][timeout:180];\n(\n{body});\nout center tags;"


QUERIES = {
    "offices": q('nwr["office"]'),
    "industrial": q('nwr["landuse"="industrial"]', 'nwr["man_made"="works"]', 'nwr["industrial"]', 'nwr["building"~"^(industrial|factory|warehouse)$"]["name"]',
                    'nwr["craft"~"^(brewery|winery|distillery|beverages|dairy|bakery|tailor|sawmill|metal_construction|printer)$"]["name"]'),
    "farms": q('nwr["landuse"~"^(farmyard|orchard|plant_nursery|greenhouse_horticulture|vineyard)$"]', 'nwr["place"="farm"]',
               'nwr["landuse"="farmland"]["name"]', 'nwr["crop"]["name"]', 'nwr["produce"]["name"]', 'nwr["building"~"^(greenhouse|farm|barn)$"]["name"]'),
    "health": q('nwr["amenity"~"^(hospital|clinic|doctors|dentist)$"]', 'nwr["healthcare"~"^(hospital|clinic|centre|laboratory|rehabilitation)$"]'),
    "education": q('nwr["amenity"~"^(college|university|research_institute)$"]', 'nwr["office"~"^(educational_institution|research)$"]'),
    "tourism": q('nwr["tourism"~"^(hotel|guest_house|hostel|motel|camp_site|chalet|apartment|resort)$"]', 'nwr["leisure"="resort"]'),
    "retail": q('nwr["shop"~"^(supermarket|mall|department_store|wholesale)$"]'),
    "banks": q('nwr["amenity"="bank"]', 'nwr["office"~"^(financial|insurance|accountant|tax_advisor)$"]'),
    "aviation": q('nwr["aeroway"~"^(aerodrome|terminal|hangar|heliport)$"]', 'nwr["office"="airline"]', 'nwr["name"~"cargo|airways|airline|aviation",i]["office"]'),
    "worship": q('nwr["amenity"="place_of_worship"]'),
    "social": q('nwr["amenity"~"^(social_facility|childcare|kindergarten|orphanage)$"]', 'nwr["social_facility"]'),
    "places": q('nwr["place"~"^(village|hamlet|neighbourhood|suburb|quarter)$"]'),
}


def fetch(name: str, box: str, refresh: bool, last: list) -> tuple[dict, str]:
    path = CACHE / f"{name}_{box}.json"
    meta = CACHE / f"{name}_{box}.meta.json"
    if path.exists() and not refresh:
        endpoint = json.loads(meta.read_text(encoding="utf-8"))["endpoint"] if meta.exists() else "cache"
        return json.loads(path.read_text(encoding="utf-8")), endpoint
    wait = last[0] + 10.0 - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    print(f"Overpass: {name} ({box}) ...", flush=True)
    body, endpoint = gov_lib.overpass(QUERIES[name].replace("{bbox}", BOXES[box]))
    last[0] = time.monotonic()
    data = json.loads(body)
    if data.get("remark") and ("error" in data["remark"].lower() or "timed out" in data["remark"].lower()):
        raise SystemExit(f"Overpass {name} failed: {data['remark']}")
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    meta.write_text(json.dumps({"endpoint": endpoint, "retrieved": date.today().isoformat()}), encoding="utf-8")
    print(f"  {len(data.get('elements', []))} elements from {endpoint}", flush=True)
    return data, endpoint


def slim(el: dict) -> dict | None:
    lat = el.get("lat", (el.get("center") or {}).get("lat"))
    lon = el.get("lon", (el.get("center") or {}).get("lon"))
    if lat is None or lon is None:
        return None
    tags = {k: v for k, v in (el.get("tags") or {}).items() if k in KEEP_TAGS}
    return {"osm_id": f"{el['type']}/{el['id']}", "lat": round(lat, 7), "lon": round(lon, 7), "tags": tags}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="date stamp for the raw extracts (default today)")
    parser.add_argument("--only", nargs="*", choices=sorted(QUERIES), help="collect only these categories")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache and query Overpass again")
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    last = [0.0]
    for name in args.only or QUERIES:
        seen, elements, endpoints, base = set(), [], {}, ""
        for box in BOXES:
            data, endpoint = fetch(name, box, args.refresh, last)
            endpoints[box] = endpoint
            base = max(base, (data.get("osm3s") or {}).get("timestamp_osm_base", ""))
            for s in (slim(e) for e in data.get("elements", [])):
                if s and s["osm_id"] not in seen:
                    seen.add(s["osm_id"])
                    elements.append(s)
        out = {"category": name, "retrieved": args.date, "endpoints": endpoints, "bbox": BBOX, "boxes": BOXES, "query": QUERIES[name],
               "osm_base": base,
               "attribution": "(c) OpenStreetMap contributors, ODbL 1.0", "elements": elements}
        path = RAW / f"osm_{name}_{args.date}.json"
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(out, ensure_ascii=False, separators=(",", ":")).replace('},{"osm_id"', '},\n{"osm_id"') + "\n")
        print(f"{name}: {len(elements)} features -> {path.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
