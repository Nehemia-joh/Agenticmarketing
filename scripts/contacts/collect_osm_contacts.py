#!/usr/bin/env python3
"""Collect OpenStreetMap contact tags (phone, email, website, Facebook) for named places in the catchment, politely.

Two small Overpass queries (a broad one times out), one at a time, at least 5 s apart, with mirror fallback. The
build step matches the results to organisations by exact normalised name, so organisations without a website can
still gain a published phone, email or site. Output: data/raw/contact-research/osm_contacts_<date>.json with the
queries. Reused unless --refresh.
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
from datetime import date

import contact_lib as C

W = C.W
ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
             "https://overpass.private.coffee/api/interpreter"]
KEEP = ("name", "name:en", "alt_name", "operator", "brand", "amenity", "office", "tourism", "healthcare", "shop", "phone", "contact:phone",
        "mobile", "contact:mobile", "email", "contact:email", "website", "contact:website", "url", "contact:facebook", "facebook",
        "contact:instagram", "addr:street", "addr:city", "addr:postcode", "addr:full")


def overpass(query: str):
    last = None
    for endpoint in ENDPOINTS:
        try:
            return json.loads(W.polite_request(endpoint, data=urllib.parse.urlencode({"data": query}), retries=2, backoff=10.0))["elements"], endpoint
        except Exception as exc:  # noqa: BLE001 - try the next mirror
            last = exc
            print(f"  {endpoint} failed ({exc!r:.100}); trying the next mirror", flush=True)
    raise SystemExit(f"All Overpass endpoints failed: {last!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--bbox", default="-3.62,36.42,-3.10,37.40", help="south,west,north,east")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    out = C.RAW / f"osm_contacts_{args.date}.json"
    if out.exists() and not args.refresh:
        print(f"reuse {out.relative_to(C.ROOT)}")
        return 0
    bbox = f"({args.bbox})"
    queries = {
        "phone_email": f'[out:json][timeout:150];(nwr["name"]["phone"]{bbox};nwr["name"]["contact:phone"]{bbox};nwr["name"]["email"]{bbox};'
                       f'nwr["name"]["contact:email"]{bbox};nwr["name"]["mobile"]{bbox};);out center tags;',
        "web_social": f'[out:json][timeout:150];(nwr["name"]["website"]{bbox};nwr["name"]["contact:website"]{bbox};nwr["name"]["contact:facebook"]{bbox};'
                      f'nwr["name"]["url"]{bbox};);out center tags;',
    }
    elements, runs = {}, []
    for key, query in queries.items():
        found, endpoint = overpass(query)
        runs.append({"query_key": key, "endpoint": endpoint, "elements": len(found), "query": query})
        for el in found:
            osm_id = f"{el['type']}/{el['id']}"
            elements[osm_id] = {"osm_id": osm_id, "lat": el.get("lat", (el.get("center") or {}).get("lat")),
                                "lon": el.get("lon", (el.get("center") or {}).get("lon")),
                                "tags": {k: v for k, v in el.get("tags", {}).items() if k in KEEP}}
        print(f"{key}: {len(found)} elements via {endpoint}", flush=True)
    C.RAW.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"retrieved": args.date, "queries": runs, "elements": sorted(elements.values(), key=lambda e: e["osm_id"])},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(elements)} named places with contact tags -> {out.relative_to(C.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
