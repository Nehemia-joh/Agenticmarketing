#!/usr/bin/env python3
"""Collect the reference points used to place wards on the map, politely and without web search.

OpenStreetMap has no ward boundaries in the catchment (only regions at admin_level 4 and districts at level 5, checked
23 September 2026), so ward locations are estimated from three public sources:
- Wikipedia ward articles in the run's categories: coordinates and the district named in the first sentence
  (API: one request every 2 s, after an HTTP 429 at 1 per second; only titles, coordinates, revision IDs and the first sentence are kept);
- OpenStreetMap place nodes (towns, villages, suburbs, neighbourhoods, hamlets) inside the bounding box;
- OpenStreetMap district boundaries (admin_level 5), simplified to points about 150 m apart, used to check that a
  point lies in the right council.
Overpass queries run one at a time, at least 5 s apart, with mirror fallback (gov_lib.overpass).

Outputs in data/raw/government-research/: wikipedia_wards_<date>.json, osm_places_<date>.json,
osm_admin_level5_<date>.json, each with its query or request parameters. Existing files are reused unless --refresh.
"""
from __future__ import annotations

import argparse
import json
import urllib.parse

import gov_lib as G

W = G.W


def wiki_api(cache, **params) -> dict:
    params.update(format="json", formatversion=2)
    return json.loads(W.polite_request("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params), cache_dir=cache, retries=2))


def collect_wikipedia(cfg: dict, out) -> None:
    cache = cfg["paths"]["cache"]
    titles: dict[str, str] = {}
    for category in cfg["wikipedia_categories"]:
        cont: dict = {}
        while True:
            data = wiki_api(cache, action="query", list="categorymembers", cmtitle=category, cmlimit=500, cmtype="page", **cont)
            for member in data.get("query", {}).get("categorymembers", []):
                titles.setdefault(member["title"], category)
            if "continue" not in data:
                break
            cont = {"cmcontinue": data["continue"]["cmcontinue"]}
    pages = []
    names = sorted(titles)
    for start in range(0, len(names), 20):  # the extracts module returns at most 20 intros per request
        batch = names[start:start + 20]
        data = wiki_api(cache, action="query", prop="coordinates|extracts|info", titles="|".join(batch), exintro=1, explaintext=1,
                        exsentences=1, exlimit=20, inprop="url", colimit=50, redirects=1)
        for page in data.get("query", {}).get("pages", []):
            coords = (page.get("coordinates") or [{}])[0]
            first = " ".join(str(page.get("extract", "")).split())
            district = G.DISTRICT_IN_TEXT.search(first)
            pages.append({"title": page.get("title"), "pageid": page.get("pageid"), "url": page.get("fullurl"),
                          "lastrevid": page.get("lastrevid"), "category": titles.get(page.get("title"), ""),
                          "lat": coords.get("lat"), "lon": coords.get("lon"), "first_sentence": first[:300],
                          "district_text": district.group(1) if district else ""})
    out.write_text(json.dumps({"retrieved": cfg["research_date"], "source": "https://en.wikipedia.org/w/api.php",
                               "categories": cfg["wikipedia_categories"], "licence_note": "Coordinates and one sentence per article, "
                               "kept as evidence with the article URL and revision ID (Wikipedia text is CC BY-SA 4.0).",
                               "pages": sorted(pages, key=lambda p: p["title"])}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    located = sum(1 for p in pages if p["lat"] is not None)
    print(f"wikipedia: {len(pages)} ward articles, {located} with coordinates -> {out.relative_to(G.ROOT)}")


def simplify(points: list[dict], min_step: float = 0.0014) -> list[dict]:
    """Keep a point only when it is about 150 m or more from the last kept one (plus the final point)."""
    kept = []
    for p in points:
        if not kept or abs(p["lat"] - kept[-1]["lat"]) + abs(p["lon"] - kept[-1]["lon"]) >= min_step:
            kept.append({"lat": round(p["lat"], 5), "lon": round(p["lon"], 5)})
    if points and kept[-1] != {"lat": round(points[-1]["lat"], 5), "lon": round(points[-1]["lon"], 5)}:
        kept.append({"lat": round(points[-1]["lat"], 5), "lon": round(points[-1]["lon"], 5)})
    return kept


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    raw, date = cfg["paths"]["raw"], cfg["research_date"]
    s, w, n, e = cfg["bbox"]
    bbox = f"({s},{w},{n},{e})"

    wiki_out = raw / f"wikipedia_wards_{date}.json"
    if wiki_out.exists() and not args.refresh:
        print(f"reuse {wiki_out.relative_to(G.ROOT)}")
    else:
        collect_wikipedia(cfg, wiki_out)

    places_out = raw / f"osm_places_{date}.json"
    places_query = f"""[out:json][timeout:120];
node["place"~"^(city|town|village|suburb|neighbourhood|quarter|hamlet|locality)$"]["name"]{bbox};
out body;"""
    if places_out.exists() and not args.refresh:
        print(f"reuse {places_out.relative_to(G.ROOT)}")
    else:
        body, endpoint = G.overpass(places_query)
        elements = json.loads(body)["elements"]
        slim = [{"type": "node", "id": el["id"], "lat": el["lat"], "lon": el["lon"],
                 "tags": {k: v for k, v in el.get("tags", {}).items() if k in ("name", "name:en", "name:sw", "alt_name", "old_name", "place", "is_in")}}
                for el in elements]
        places_out.write_text(json.dumps({"retrieved": date, "endpoint": endpoint, "query": places_query, "elements": slim},
                                         ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"osm places: {len(slim)} nodes via {endpoint} -> {places_out.relative_to(G.ROOT)}")

    admin_out = raw / f"osm_admin_level5_{date}.json"
    admin_query = f"""[out:json][timeout:180];
relation["boundary"="administrative"]["admin_level"="5"]{bbox};
out geom;"""
    if admin_out.exists() and not args.refresh:
        print(f"reuse {admin_out.relative_to(G.ROOT)}")
    else:
        body, endpoint = G.overpass(admin_query)
        elements = []
        for el in json.loads(body)["elements"]:
            if el.get("type") != "relation":
                continue
            members = [{"type": "way", "role": m.get("role", ""), "geometry": simplify(m["geometry"])}
                       for m in el.get("members", []) if m.get("type") == "way" and m.get("geometry") and m.get("role") in ("outer", "")]
            elements.append({"type": "relation", "id": el["id"],
                             "tags": {k: v for k, v in el.get("tags", {}).items() if k in ("name", "name:en", "name:sw", "admin_level", "boundary", "ref", "is_in")},
                             "members": members})
        admin_out.write_text(json.dumps({"retrieved": date, "endpoint": endpoint, "query": admin_query,
                                         "note": "Outer ways only, simplified to points about 150 m apart for point-in-district checks.",
                                         "elements": elements}, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"osm districts: {[e['tags'].get('name') for e in elements]} via {endpoint} -> {admin_out.relative_to(G.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
