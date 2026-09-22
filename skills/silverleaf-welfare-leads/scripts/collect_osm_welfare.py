#!/usr/bin/env python3
"""Collect welfare-related OpenStreetMap features for the catchment bounding box, politely.

Two small queries instead of one broad one: a single regex query over the whole catchment returned HTTP 504 in the
2026-09 run. Each query goes through welfare_lib.polite_request (>= 5 s apart, retries with backoff) and falls back
to Overpass mirrors. Existing extracts for the research date are reused unless --refresh is given.
Outputs: data/raw/welfare-research/osm_welfare_{tags,names}_<date>.json plus the query text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse

import welfare_lib as W

ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
             "https://overpass.private.coffee/api/interpreter"]


def queries(bbox: str) -> dict:
    return {
        "tags": f"""[out:json][timeout:120];
(
  nwr["amenity"="social_facility"]{bbox};
  nwr["social_facility"]{bbox};
  nwr["social_facility:for"]{bbox};
  nwr["amenity"="orphanage"]{bbox};
  nwr["amenity"="childcare"]["name"~"orphan|yatima|home|rescue|centre|center",i]{bbox};
  nwr["office"="ngo"]{bbox};
  nwr["office"="charity"]{bbox};
  nwr["office"="foundation"]{bbox};
);
out center tags;""",
        "names": f"""[out:json][timeout:170];
(
  nwr["name"~"orphan|yatima|makao|rescue|street child|vulnerable|children'?s home|children'?s village|children'?s centre|children'?s center|baby home|kituo cha",i]{bbox};
);
out center tags;""",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    s, w, n, e = cfg["bbox"]
    bbox = f"({s},{w},{n},{e})"
    raw, date = cfg["paths"]["raw"], cfg["research_date"]
    for key, query in queries(bbox).items():
        out = raw / f"osm_welfare_{key}_{date}.json"
        if out.exists() and not args.refresh:
            print(f"reuse {out.relative_to(W.ROOT)}")
            continue
        last = None
        for endpoint in ENDPOINTS:
            try:
                body = W.polite_request(endpoint, data=urllib.parse.urlencode({"data": query}), retries=2, backoff=10.0)
                elements = json.loads(body)["elements"]
                out.write_bytes(body)
                (raw / f"osm_welfare_{key}_{date}.query.txt").write_text(f"endpoint: {endpoint}\nretrieved: {date}\n\n{query}", encoding="utf-8")
                print(f"{key}: {len(elements)} elements via {endpoint} (sha256 {hashlib.sha256(body).hexdigest()[:16]})")
                break
            except Exception as exc:  # noqa: BLE001 - try the next mirror
                last = exc
                print(f"{key}: {endpoint} failed ({exc!r:.100}); trying the next mirror")
        else:
            raise SystemExit(f"All Overpass endpoints failed for {key}: {last!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
