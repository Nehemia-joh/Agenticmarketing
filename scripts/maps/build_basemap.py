#!/usr/bin/env python3
"""Build the offline basemap for the lead map from OpenStreetMap (Overpass), simplified and attributed.

Writes data/reference/maps/arusha-catchment-basemap.geojson: one FeatureCollection whose features carry a `layer` property
  road        major roads (trunk, primary, secondary, tertiary), `class` = the OSM highway class
  road_minor  residential and unclassified streets, only inside the three town boxes (Arusha, Usa River-Tengeru, Moshi)
  water       lakes and reservoirs (polygons)          river   rivers (lines; streams are left out)
  park        national parks, forest and nature reserves (polygons, `name`); park_label one point per large one
  district    district (admin_level 5) boundaries as lines, `region_edge` when the line also separates two regions
  district_label  one point per district, `name`
  place       towns, villages, suburbs and neighbourhoods (points, `name`, `class`)
  peak        the summits of Kilimanjaro and Mount Meru (points, `name`, `ele`)
  poi         named hotels, lodges, hospitals, clinics, colleges, universities and offices (points, `name`, `kind`); used only
              by build_lead_map.py to place a lead whose name matches exactly one feature, and not drawn

The box is the repository's catchment box (scripts/welfare/welfare_lib.py in_catchment_box): 3.75 to 2.95 S, 36.30 to 37.55 E,
which runs from west of Arusha city past Moshi and Boma Ng'ombe to Marangu.

Overpass rules (skills/silverleaf-create-lead-list/references/research-rate-limits.md): one query at a time, at least 6 seconds
apart, [timeout:180], the repository's User-Agent, retries with backoff and the mirror fallback (gov_lib.overpass). Raw answers
are cached in runtime/maps/overpass/ (git-ignored) and reused; --refresh fetches again.

Data (c) OpenStreetMap contributors, available under the Open Database License (ODbL 1.0).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from shapely.geometry import LineString, MultiLineString, Point, Polygon, box, mapping
from shapely.ops import linemerge, polygonize, unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "government"))
import gov_lib  # noqa: E402  (polite Overpass client with mirror fallback)

SOUTH, WEST, NORTH, EAST = -3.75, 36.30, -2.95, 37.55
BBOX = f"{SOUTH},{WEST},{NORTH},{EAST}"
CLIP = box(WEST, SOUTH, EAST, NORTH)
# Town boxes for residential streets (south, west, north, east).
TOWNS = {"arusha": (-3.45, 36.60, -3.30, 36.78), "usa-tengeru": (-3.41, 36.78, -3.33, 36.90), "moshi": (-3.39, 37.29, -3.30, 37.38)}
CACHE = ROOT / "runtime" / "maps" / "overpass"
OUT = ROOT / "data" / "reference" / "maps" / "arusha-catchment-basemap.geojson"
ATTRIBUTION = "Map data (c) OpenStreetMap contributors, ODbL 1.0 (openstreetmap.org/copyright)"

QUERIES = {
    "roads": f"""[out:json][timeout:180];
way["highway"~"^(motorway|trunk|primary|secondary|tertiary)(_link)?$"]({BBOX});
out geom;""",
    "streets": "[out:json][timeout:180];\n(\n" + "".join(
        f'  way["highway"~"^(residential|unclassified|living_street)$"]({s},{w},{n},{e});\n' for s, w, n, e in TOWNS.values()) + ");\nout geom;",
    "places": f"""[out:json][timeout:180];
(
  node["place"~"^(city|town|village|suburb|neighbourhood|quarter)$"]({BBOX});
  node["natural"="peak"]["name"]["ele"]({BBOX});
);
out body;""",
    "summits": f"""[out:json][timeout:180];
node["natural"~"^(peak|volcano)$"]["name"]({BBOX});
out body;""",
    "water": f"""[out:json][timeout:180];
(
  way["natural"="water"]({BBOX});
  relation["natural"="water"]({BBOX});
  way["landuse"="reservoir"]({BBOX});
  way["waterway"="river"]({BBOX});
);
out geom;""",
    "parks": f"""[out:json][timeout:180];
(
  way["boundary"~"^(national_park|protected_area)$"]({BBOX});
  relation["boundary"~"^(national_park|protected_area)$"]({BBOX});
  relation["leisure"="nature_reserve"]({BBOX});
);
out geom;""",
    "districts": f"""[out:json][timeout:180];
relation["boundary"="administrative"]["admin_level"~"^(4|5)$"]({BBOX});
out geom;""",
    "pois": f"""[out:json][timeout:180];
(
  nwr["name"]["tourism"~"^(hotel|guest_house|hostel|motel|camp_site|chalet|apartment|resort)$"]({BBOX});
  nwr["name"]["amenity"~"^(hospital|clinic|doctors|university|college|bank)$"]({BBOX});
  nwr["name"]["office"]({BBOX});
);
out center tags;""",
}


def fetch(name: str, refresh: bool, last: list) -> dict:
    path = CACHE / f"{name}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    wait = last[0] + 6.0 - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    print(f"Overpass: {name} ...", flush=True)
    body, endpoint = gov_lib.overpass(QUERIES[name])
    last[0] = time.monotonic()
    data = json.loads(body)
    if data.get("remark") and "error" in data["remark"].lower():
        raise SystemExit(f"Overpass {name} failed: {data['remark']}")
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    print(f"  {len(data.get('elements', []))} elements from {endpoint}", flush=True)
    return data


def rnd(geom, digits=5):
    """GeoJSON geometry with coordinates rounded (5 decimals is about 1 m)."""
    def r(c):
        if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
            return [round(c[0], digits), round(c[1], digits)]
        return [r(x) for x in c]
    g = mapping(geom)
    return {"type": g["type"], "coordinates": r(g["coordinates"])}


def line_of(el) -> LineString | None:
    pts = [(p["lon"], p["lat"]) for p in el.get("geometry") or [] if p]
    return LineString(pts) if len(pts) >= 2 else None


def relation_polygon(el):
    """Polygon(s) from a multipolygon or boundary relation's member ways (outer minus inner)."""
    outers, inners = [], []
    for m in el.get("members", []):
        if m.get("type") != "way" or not m.get("geometry"):
            continue
        pts = [(p["lon"], p["lat"]) for p in m["geometry"] if p]
        if len(pts) >= 2:
            (inners if m.get("role") == "inner" else outers).append(LineString(pts))
    if not outers:
        return None
    outer = unary_union(list(polygonize(unary_union(outers))))
    if inners:
        outer = outer.difference(unary_union(list(polygonize(unary_union(inners)))))
    return outer if not outer.is_empty else None


def way_polygon(el):
    pts = [(p["lon"], p["lat"]) for p in el.get("geometry") or [] if p]
    if len(pts) >= 4 and pts[0] == pts[-1]:
        poly = Polygon(pts)
        return poly if poly.is_valid else poly.buffer(0)
    return None


def feature(layer: str, geom, **props) -> dict | None:
    if geom is None or geom.is_empty:
        return None
    return {"type": "Feature", "properties": {"layer": layer, **{k: v for k, v in props.items() if v not in (None, "")}}, "geometry": rnd(geom)}


def clip_simplify(geom, tolerance):
    g = geom.intersection(CLIP)
    if g.is_empty:
        return None
    g = g.simplify(tolerance, preserve_topology=True)
    return None if g.is_empty else g


def build(refresh: bool) -> dict:
    last = [0.0]
    raw = {name: fetch(name, refresh, last) for name in QUERIES}
    feats = []

    # Roads: merge by class so the file holds a few long lines rather than thousands of short ways.
    by_class = {}
    for el in raw["roads"]["elements"]:
        line = line_of(el)
        if line is not None:
            cls = el["tags"]["highway"].replace("_link", "").replace("motorway", "trunk")
            by_class.setdefault(cls, []).append(line)
    tol = {"trunk": 0.00005, "primary": 0.00005, "secondary": 0.00008, "tertiary": 0.00015}
    for cls, lines in by_class.items():
        feats.append(feature("road", clip_simplify(linemerge(lines), tol[cls]), **{"class": cls}))
    streets = [line_of(el) for el in raw["streets"]["elements"]]
    feats.append(feature("road_minor", clip_simplify(linemerge([s for s in streets if s is not None]), 0.00012)))

    # Water and rivers.
    waters, rivers = [], []
    for el in raw["water"]["elements"]:
        tags = el.get("tags", {})
        if tags.get("waterway") == "river":
            line = line_of(el)
            if line is not None:
                rivers.append(line)
            continue
        poly = relation_polygon(el) if el["type"] == "relation" else way_polygon(el)
        if poly is not None and poly.area > 2e-6:  # about 2.5 hectares; smaller ponds are noise at this scale
            waters.append((poly, tags.get("name")))
    feats.append(feature("river", clip_simplify(linemerge(rivers), 0.0003)))
    for poly, name in waters:
        feats.append(feature("water", clip_simplify(poly, 0.0002), name=name))

    # Protected areas: national parks, forest and nature reserves (large ones only).
    for el in raw["parks"]["elements"]:
        tags = el.get("tags", {})
        poly = relation_polygon(el) if el["type"] == "relation" else way_polygon(el)
        if poly is None or poly.area < 1e-4:  # about 1.2 km2
            continue
        kind = "national_park" if tags.get("boundary") == "national_park" or "national park" in (tags.get("name") or "").lower() else "reserve"
        shape = clip_simplify(poly, 0.0005)
        feats.append(feature("park", shape, name=tags.get("name"), kind=kind))
        if shape is not None and tags.get("name") and shape.area > 0.004:  # about 50 km2 inside the box
            feats.append(feature("park_label", shape.representative_point(), name=tags.get("name:en") or tags["name"], kind=kind))

    # Districts (admin_level 5) as lines; a line shared with a region boundary (admin_level 4) is a region edge.
    regions, districts = [], []
    for el in raw["districts"]["elements"]:
        poly = relation_polygon(el)
        if poly is None:
            continue
        (regions if el["tags"].get("admin_level") == "4" else districts).append((poly, el["tags"].get("name:en") or el["tags"].get("name")))
    region_lines = unary_union([p.boundary for p, _ in regions]) if regions else None
    district_lines = unary_union([p.boundary for p, _ in districts])
    if region_lines is not None:
        edge = region_lines.intersection(CLIP)
        feats.append(feature("district", clip_simplify(edge, 0.0005), region_edge=1))
        inner = district_lines.difference(region_lines.buffer(0.0005))
    else:
        inner = district_lines
    feats.append(feature("district", clip_simplify(inner, 0.0005)))
    for poly, name in districts:
        part = poly.intersection(CLIP)
        if part.is_empty or part.area < 0.004 or not name:
            continue
        feats.append(feature("district_label", part.representative_point(), name=re.sub(r"\s+District$", "", name)))

    # Places and the two summits (Kilimanjaro and Mount Meru: named summits of 4,500 m or more, or a named volcano).
    peaks = {}
    for el in raw["places"]["elements"] + raw["summits"]["elements"]:
        tags = el.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name:
            continue
        if tags.get("natural") in ("peak", "volcano"):
            try:
                ele = float(str(tags.get("ele")).split()[0].replace(",", "."))
            except ValueError:
                ele = 0.0
            if (ele >= 4500 or tags.get("natural") == "volcano") and not re.search(r"tower|point|crater|krater", name, re.I):
                peaks.setdefault(name, feature("peak", Point(el["lon"], el["lat"]), name=name, ele=int(round(ele)) or None))
            continue
        if tags.get("place"):
            feats.append(feature("place", Point(el["lon"], el["lat"]), name=name, **{"class": tags["place"]}))
    feats += list(peaks.values())

    # Named points of interest (for name matching only).
    for el in raw["pois"]["elements"]:
        tags = el.get("tags", {})
        lat, lon = (el.get("lat"), el.get("lon")) if el["type"] == "node" else ((el.get("center") or {}).get("lat"), (el.get("center") or {}).get("lon"))
        if lat is None or not tags.get("name"):
            continue
        kind = tags.get("tourism") or tags.get("amenity") or ("office:" + tags.get("office", ""))
        feats.append(feature("poi", Point(lon, lat), name=tags["name"], kind=kind, osm=f"{el['type']}/{el['id']}"))

    feats = [f for f in feats if f]
    return {"type": "FeatureCollection", "attribution": ATTRIBUTION, "bbox": [WEST, SOUTH, EAST, NORTH],
            "built_from": "Overpass API extract, " + time.strftime("%Y-%m-%d"), "features": feats}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true", help="fetch from Overpass again instead of reusing runtime/maps/overpass/")
    args = parser.parse_args()
    data = build(args.refresh)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    counts = {}
    for f in data["features"]:
        counts[f["properties"]["layer"]] = counts.get(f["properties"]["layer"], 0) + 1
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size / 1e6:.2f} MB; features by layer: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
