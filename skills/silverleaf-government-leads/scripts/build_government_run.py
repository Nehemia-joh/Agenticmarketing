#!/usr/bin/env python3
"""Build a government run from the collected evidence. No network calls.

Reads data/raw/government-research/ (census wards, Wikipedia ward points, OpenStreetMap places, districts and
offices, council-site captures, transcriptions), the run config, links.json (reviewed curation) and the company
master read-only (campus coordinates and its office:government records).

Produces, in runtime/government/<run-id>/final.json:
- admin_units: every census ward of the configured councils, with an estimated location, campus distances and
  the ward score, plus one row per council;
- offices: the convening offices in scope (regions, districts, councils, catchment wards, mapped village offices);
- posts: official posts as role desks, with holder names only where an official roster or profile publishes them;
- office_triage and master_triage: every OpenStreetMap office and master office:government record, classified,
  with each exclusion and its reason;
- signals: council news and notices that mention public meetings, events or elections;
- reviews: decisions for a person.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import gov_lib as G

W = G.W
BAND_WEIGHT = {"0-5 km": 1.0, "6-10 km": 0.8, "11-15 km": 0.6, "16-20 km": 0.4, "21-25 km": 0.2}
PLACE_RANK = {"city": 0, "town": 1, "suburb": 2, "village": 3, "quarter": 4, "neighbourhood": 5, "hamlet": 6, "locality": 7}
ACT_DISTRICT = "https://tanzlii.org/akn/tz/act/1982/7/eng@2002-07-31/source"
ACT_URBAN = "https://media.tanzlii.org/media/legislation/316204/source_file/77e1e9a6b6ecb9fb/1982-8.pdf"

# Official posts by office level (plans/b2b-government-leads-plan.md §5.1). Holders are recorded only where an
# official roster or profile publishes them; otherwise the post is a role desk.
POSTS = {
    "region": [
        ("regional_commissioner", "Regional Commissioner", "Mkuu wa Mkoa", "political_appointee", False,
         "Regional public meetings and events; not a v1 target (plan §1)."),
        ("regional_administrative_secretary", "Regional Administrative Secretary", "Katibu Tawala wa Mkoa", "civil_service", False,
         "Regional administration and protocol for regional events."),
        ("regional_community_development", "Community Development Unit, Regional Secretariat", "Kitengo cha Maendeleo ya Jamii, Sekretarieti ya Mkoa",
         "civil_service", False, "Oversees council community development work; guidance only."),
        ("regional_education", "Education and Vocational Training Section, Regional Secretariat", "Sehemu ya Elimu, Sekretarieti ya Mkoa",
         "civil_service", True, "Check with the B2G owner before any contact (plan §1)."),
    ],
    "district": [
        ("district_commissioner", "District Commissioner", "Mkuu wa Wilaya", "political_appointee", False,
         "District public meetings (mikutano ya hadhara); not a v1 target (plan §1)."),
        ("district_administrative_secretary", "District Administrative Secretary", "Katibu Tawala wa Wilaya", "civil_service", False,
         "District administration and protocol."),
    ],
    "council": [
        ("council_director", "Council Director", "Mkurugenzi wa Halmashauri", "civil_service", False,
         "City Director, Municipal Director or District Executive Director. GA01: formal introduction, guidance on wards and meeting "
         "calendars, and a letter introducing Silverleaf to ward executive officers."),
        ("council_chair", "Council Chairperson or Mayor", "Mwenyekiti wa Halmashauri / Meya", "elected", False,
         "Chairs the full council. Engage only through the council's official process (plan §3)."),
        ("community_development_head", "Head of Community Development Division", "Mkuu wa Divisheni ya Maendeleo ya Jamii", "civil_service", False,
         "Community development groups and ward community development officers."),
        ("social_welfare_officer", "Council Social Welfare Officer", "Afisa Ustawi wa Jamii wa Halmashauri", "civil_service", False,
         "Guidance on family forums; also licenses children's homes (welfare track)."),
        ("primary_education_head", "Head of Pre-Primary and Primary Education Division", "Mkuu wa Divisheni ya Elimu ya Awali na Msingi", "civil_service", True,
         "Check with the B2G owner before any contact (plan §1). Public-school parent meetings are excluded."),
    ],
    "ward": [
        ("ward_executive_officer", "Ward Executive Officer (WEO)", "Afisa Mtendaji wa Kata", "civil_service", False,
         "Convenes ward public meetings; secretary to the Ward Development Committee, which meets at least four times a year."),
        ("ward_councillor", "Ward Councillor", "Diwani wa Kata", "elected", False,
         "Chairs the Ward Development Committee. Engage only through the official forum they chair (plan §3); decision 7 is open."),
        ("ward_community_development_officer", "Ward Community Development Officer", "Afisa Maendeleo ya Jamii wa Kata", "civil_service", False,
         "Women's, youth and savings groups. Savings groups go to corporate campaign C02."),
    ],
    "village": [
        ("village_executive_officer", "Village Executive Officer (VEO)", "Afisa Mtendaji wa Kijiji", "civil_service", False,
         "Secretary to the village assembly (all residents aged 18 and over; at least quarterly)."),
        ("village_chair", "Village Chairperson", "Mwenyekiti wa Kijiji", "elected", False, "Chairs the village assembly."),
    ],
}
FORUMS = {
    "region": "Regional public meetings and government events (not a v1 target)",
    "district": "District public meetings (mkutano wa hadhara), run with formal protocol (not a v1 target)",
    "council": "Introductions and guidance; council-organised public events where institutions can take stalls",
    "ward": "Ward public meeting (WEO with the councillor); Ward Development Committee at least four times a year",
    "village": "Village assembly (mkutano mkuu wa kijiji): all residents 18+, at least quarterly",
}
PROFILE_RULES = [
    (r"mayor|meya|chair|mwenyekiti", "council_chair"),
    (r"director|mkurugenzi", "council_director"),
    (r"regional commissioner|mkuu wa mkoa", "regional_commissioner"),
    (r"administrative secretary|regional secretary|katibu tawala", "regional_administrative_secretary"),
]
DEPARTMENT_SLUGS = {
    "community_development_head": r"community-development(?!-services)|department-of-community-development|^community$|community-development-divison",
    "social_welfare_officer": r"social-welfare|social-walfare|^healthy$",
    "primary_education_head": r"pre-?(and-)?primary|pre-and-primary",
    "regional_community_development": r"community-development-unit",
    "regional_education": r"education-and-vocational-training",
}


def short(text: str, words: int = 25) -> str:
    parts = str(text or "").split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", G.ward_key(text)).strip("-")


def source(url, title, basis, date, facts, excerpt="", fetched=True) -> dict:
    return {"url": url, "title": title, "evidence_basis": basis, "accessed_on": date, "fetched": fetched,
            "facts_supported": facts, "evidence_excerpt": short(excerpt)}


class Reviews:
    def __init__(self):
        self.items = []

    def add(self, kind, entity, detail, action, related=""):
        self.items.append({"kind": kind, "entity": entity, "related": related, "detail": detail, "action": action})


# ------------------------------------------------------------------ loading
def load_inputs(cfg):
    raw, date = cfg["paths"]["raw"], cfg["research_date"]
    with open(raw / f"nbs_2022_wards_{date}.csv", encoding="utf-8") as handle:
        census = list(csv.DictReader(handle))
    for row in census:
        for k in ("population", "male", "female", "households", "ward_no", "pdf_page", "sex_ratio"):
            row[k] = int(row[k])
        row["avg_household_size"] = float(row["avg_household_size"])
    totals = json.loads((raw / f"nbs_2022_councils_{date}.json").read_text(encoding="utf-8"))
    wiki = json.loads((raw / f"wikipedia_wards_{date}.json").read_text(encoding="utf-8"))["pages"]
    places = json.loads((raw / f"osm_places_{date}.json").read_text(encoding="utf-8"))["elements"]
    offices = json.loads((raw / f"osm_government_offices_{date}.json").read_text(encoding="utf-8"))["elements"]
    sites = {}
    for path in sorted((raw / "council_sites").glob(f"*_{date}.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["_file"] = path.relative_to(G.ROOT).as_posix()
        sites[data["host"]] = data
    transcriptions = []
    for path in sorted((raw / "transcriptions").glob("*.csv")):
        with open(path, encoding="utf-8") as handle:
            for n, row in enumerate(csv.DictReader(handle), 2):
                row["_file"], row["_line"] = path.relative_to(G.ROOT).as_posix(), n
                transcriptions.append(row)
    return census, totals, wiki, places, offices, sites, transcriptions


def master_government_records() -> list[dict]:
    con = sqlite3.connect(f"file:{W.MASTER.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT organisation_id, name, segment, campus, distance_km, source_url, notes FROM organisations "
        "WHERE segment = 'office:government' ORDER BY distance_km")]
    con.close()
    return rows


# ------------------------------------------------------------------ geography
def valid_point(lat, lon) -> bool:
    return lat is not None and lon is not None and -12.5 <= float(lat) <= -0.9 and 29.0 <= float(lon) <= 41.0


def campus_fields(lat, lon, campuses, clusters) -> dict:
    if not valid_point(lat, lon):
        return {"campus": "", "distance_km": None, "transport_band": "unknown", "nearest_primary_campus": "",
                "distance_to_primary_km": None, "primary_band": "unknown", "campus_cluster": ""}
    dist = {name: W.hav(lat, lon, c[0], c[1]) for name, c in campuses.items()}
    near = min(dist, key=dist.get)
    prim = min((n for n in dist if n in W.PRIMARY_CAMPUSES), key=dist.get)
    return {"campus": near, "distance_km": round(dist[near], 1), "transport_band": W.band(dist[near]),
            "nearest_primary_campus": prim, "distance_to_primary_km": round(dist[prim], 1), "primary_band": W.band(dist[prim]),
            "campus_cluster": clusters.get(near, near)}


def zone_function(cfg):
    """The OpenStreetMap districts a council's points may fall in: its own, plus its joint-zone partner's."""
    councils = {c["name"]: c for c in cfg["councils"]}
    partners = defaultdict(set)
    for a, b in cfg.get("joint_zones", {}).get("pairs", []):
        partners[a].add(b)
        partners[b].add(a)
    return lambda council: {councils[c]["osm_district"] for c in {council} | partners[council]}


def alias_keys(links) -> defaultdict:
    """(council, census ward) -> squashed alternative spellings, as reviewed in links.json ward_aliases."""
    aliases = defaultdict(set)
    for council, mapping in links.get("ward_aliases", {}).items():
        if not council.startswith("_"):
            for alias, ward in mapping.items():
                aliases[(council, ward)].add(G.squash(alias))
    return aliases


def match_ward_offices(osm_offices, census, cfg, links, districts) -> dict:
    """Ward offices mapped in OpenStreetMap, matched to a census ward by name inside the council's zone or by a
    reviewed link in links.json osm_office_links. Returns {(council, ward): {...point...}}."""
    zone, aliases = zone_function(cfg), alias_keys(links)
    out = {}
    for el in osm_offices:
        name = el["tags"].get("name", "")
        link = links.get("osm_office_links", {}).get(el["osm_id"], {})
        point = {"lat": el["lat"], "lon": el["lon"], "osm_id": el["osm_id"], "name": name}
        if link.get("council") and link.get("ward"):
            out[(link["council"], link["ward"])] = {**point, "how": "reviewed link (links.json): " + link.get("note", "")}
            continue
        category, level = G.classify_office(name, el["tags"])
        if category != "convener" or level != "ward" or not valid_point(el["lat"], el["lon"]):
            continue
        key = G.squash(re.sub(r"(?i)\b(ofisi|office|ya|kata|ward|building)\b", " ", name))
        where = G.district_of(el["lat"], el["lon"], districts)
        hits = [w for w in census if where in zone(w["council"]) and (G.squash(w["ward"]) == key or key in aliases[(w["council"], w["ward"])])]
        if len(hits) == 1:
            out[(hits[0]["council"], hits[0]["ward"])] = {**point, "how": "office name matches the ward inside the council's district"}
    return out


def locate_wards(cfg, census, wiki, places, districts, gaz, links, reviews, office_points=None):
    """Estimate one reference point per ward from mapped ward offices, Wikipedia, OpenStreetMap and the gazetteer.

    Candidates must lie in the council's OpenStreetMap district (or its joint zone) and, for Wikipedia, the article
    must not name another district or share its coordinates with another article. Order of preference:
    a reviewed override in links.json; the ward office itself where OpenStreetMap maps it; a Wikipedia point
    corroborated by OpenStreetMap within location_disagreement_km; otherwise the OpenStreetMap evidence (a place named
    like the ward, then the centre of places listed under an area named like the ward, e.g. "Uswaa, Machame Uroki");
    an uncorroborated Wikipedia point; the repository gazetteer. When Wikipedia and OpenStreetMap disagree, strong
    OpenStreetMap evidence (a town or village of that name, or three or more listed places) wins; otherwise Wikipedia
    does. A point that matches wards of the same name in two councils is left for review.
    """
    councils = {c["name"]: c for c in cfg["councils"]}
    zone = zone_function(cfg)
    office_points = office_points or {}
    name_owner = Counter(n.casefold() for c in councils.values() for n in c.get("wikipedia_district_names", []))
    aliases = alias_keys(links)
    coord_count = Counter((round(p["lat"], 3), round(p["lon"], 3)) for p in wiki if p.get("lat") is not None)
    wiki_by_key = defaultdict(list)
    for p in wiki:
        wiki_by_key[G.squash(re.split(r",|\(", p["title"])[0])].append(p)
    named, prefixed, listed_under = defaultdict(list), defaultdict(list), defaultdict(list)
    for el in places:
        for tag in ("name", "name:en", "name:sw", "alt_name", "old_name"):
            for part in str(el["tags"].get(tag) or "").split(";"):
                pieces = [x.strip() for x in part.split(",") if x.strip()]
                if len(pieces) == 1:
                    named[G.squash(pieces[0])].append(el)
                elif len(pieces) > 1:
                    prefixed[G.squash(pieces[0])].append(el)
                    listed_under[G.squash(pieces[-1])].append(el)
    gaz_by_key = {G.squash(k): v for k, v in gaz.items()}
    overrides = links.get("ward_locations", {})
    # Schools and health facilities named after a ward (collect_ward_locations.py): used only through a reviewed override.
    facilities_path = cfg["paths"]["raw"] / f"osm_named_facilities_{cfg['research_date']}.json"
    facilities = json.loads(facilities_path.read_text(encoding="utf-8"))["elements"] if facilities_path.exists() else []

    cand, claims = {}, defaultdict(list)
    for w in census:
        council, ward = w["council"], w["ward"]
        ident = (council, ward)
        keys = {G.squash(ward)} | aliases[ident]
        allowed = {n.casefold() for n in councils[council].get("wikipedia_district_names", [])}
        own = councils[council]["osm_district"]
        c = {"keys": keys, "wiki": [], "wiki_rejected": [], "place": [], "group": [], "gaz": []}
        # The census spelling first, then aliases in a fixed order: the first matching evidence is used, so a set's
        # arbitrary order would make the ward location differ between runs.
        for key in [G.squash(ward), *sorted(keys - {G.squash(ward)})]:
            for p in wiki_by_key.get(key, []):
                if p.get("lat") is None:
                    continue
                text = str(p.get("district_text") or "").casefold()
                where = G.district_of(p["lat"], p["lon"], districts)
                reasons = []
                if text and text not in allowed:
                    reasons.append(f"article names {p['district_text']}")
                if where not in zone(council):
                    reasons.append(f"coordinates fall in OSM district '{where or 'none'}'")
                if coord_count[(round(p["lat"], 3), round(p["lon"], 3))] > 1:
                    reasons.append("coordinates shared with another article")
                if reasons:
                    c["wiki_rejected"].append((p, reasons))
                elif ("wiki", p["title"]) not in [x[0] for x in c["wiki"]]:
                    strong = (bool(text) and name_owner[text] == 1) or where == own
                    c["wiki"].append((("wiki", p["title"]), p, strong))
            for rank_offset, pool in ((0, named), (10, prefixed)):
                for el in pool.get(key, []):
                    where = G.district_of(el["lat"], el["lon"], districts)
                    if where in zone(council) and ("osm", el["id"]) not in [x[0] for x in c["place"]]:
                        c["place"].append((("osm", el["id"]), el, where == own, PLACE_RANK.get(el["tags"].get("place"), 9) + rank_offset))
            group = [el for el in listed_under.get(key, []) if G.district_of(el["lat"], el["lon"], districts) in zone(council)]
            if group:
                c["group"].append((("group", key), group))
            if key in gaz_by_key:
                hit = gaz_by_key[key]
                if G.district_of(hit[0], hit[1], districts) in zone(council):
                    c["gaz"].append((("gaz", key), hit))
        cand[ident] = c
        for bucket in ("wiki", "place", "group", "gaz"):
            for entry in c[bucket]:
                strong = entry[2] if bucket in ("wiki", "place") else False
                claims[entry[0]].append((ident, strong))

    def mine(claim_id, ident):
        """True if this ward owns the evidence, False if another ward does, None if two wards contest it."""
        entries = claims[claim_id]
        if len(entries) == 1:
            return True
        strong = [e[0] for e in entries if e[1]]
        if len(strong) == 1:
            return strong[0] == ident
        return None

    located = {}
    for w in census:
        council, ward = w["council"], w["ward"]
        ident, label = (council, ward), f"{ward} ({council})"
        c = cand[ident]
        for p, reasons in c["wiki_rejected"]:
            reviews.add("wikipedia_point_rejected", label, {"article": p["title"], "url": p["url"], "reasons": reasons, "lat": p["lat"], "lon": p["lon"]},
                        "Not used for the ward location. Correct the article or record a reviewed override in links.json.")
        contested = [str(x[0][1]) for bucket in ("wiki", "place", "group", "gaz") for x in c[bucket] if mine(x[0], ident) is None]
        if contested:
            reviews.add("location_claimed_by_two_wards", label, {"evidence": contested},
                        "The same evidence matches wards of the same name in neighbouring councils. Record the right point in links.json ward_locations.")
        wp = next((p for cid, p, _ in c["wiki"] if mine(cid, ident)), None)
        op = min((x for x in c["place"] if mine(x[0], ident)), key=lambda x: x[3], default=None)
        gp = next((g for cid, g in c["group"] if mine(cid, ident)), None)
        gz = next((h for cid, h in c["gaz"] if mine(cid, ident)), None)
        osm_point = None
        if op:
            el = op[1]
            osm_point = {"lat": el["lat"], "lon": el["lon"], "location_source": "osm_place", "location_ref": f"node/{el['id']}",
                         "location_url": f"https://www.openstreetmap.org/node/{el['id']}", "strong": op[3] <= PLACE_RANK["village"],
                         "what": f"OpenStreetMap {el['tags'].get('place')} '{el['tags'].get('name')}'"}
        elif gp:
            lat = sum(e["lat"] for e in gp) / len(gp)
            lon = sum(e["lon"] for e in gp) / len(gp)
            spread = max(W.hav(lat, lon, e["lat"], e["lon"]) for e in gp)
            parent = gp[0]["tags"].get("name", "").split(",")[-1].strip()
            if spread <= 10:
                osm_point = {"lat": round(lat, 6), "lon": round(lon, 6), "location_source": "osm_places_listed_under_ward_name",
                             "location_ref": "; ".join(f"node/{e['id']}" for e in gp[:12]),
                             "location_url": f"https://www.openstreetmap.org/node/{gp[0]['id']}", "strong": len(gp) >= 3,
                             "what": (f"centre of {len(gp)} OpenStreetMap places listed under '{parent}' (spread {spread:.1f} km)" if len(gp) > 1
                                      else f"OpenStreetMap place '{gp[0]['tags'].get('name')}', listed under '{parent}'")}
            else:
                reviews.add("osm_places_too_spread", label, {"places": [e["tags"].get("name") for e in gp], "spread_km": round(spread, 1)},
                            "Places listed under this name are too far apart to estimate the ward centre.")
        chosen = None
        override = overrides.get(f"{council}|{ward}")
        if override:
            src, ref = override.get("source"), override.get("ref")
            if src == "wikipedia":
                page = next((p for p in wiki if p["title"] == ref and p.get("lat") is not None), None)
                if page:
                    chosen = {"lat": page["lat"], "lon": page["lon"], "location_source": "wikipedia", "location_ref": page["title"], "location_url": page["url"]}
            elif src == "osm_place":
                el = next((e for e in places if f"node/{e['id']}" == ref), None)
                if el:
                    chosen = {"lat": el["lat"], "lon": el["lon"], "location_source": "osm_place", "location_ref": ref,
                              "location_url": f"https://www.openstreetmap.org/{ref}"}
            elif src == "osm_facility":
                el = next((e for e in facilities if f"{e['type']}/{e['id']}" == ref and e.get("lat") is not None), None)
                if el:
                    chosen = {"lat": el["lat"], "lon": el["lon"], "location_source": "osm_facility", "location_ref": ref,
                              "location_url": f"https://www.openstreetmap.org/{ref}"}
            elif src == "none":
                chosen = {"lat": None, "lon": None, "location_source": "none", "location_ref": "", "location_url": ""}
            if chosen is None:
                reviews.add("override_not_applied", label, override, "The reviewed override points at evidence that is not in this run's raw files.")
            else:
                chosen["location_note"] = "Reviewed override (links.json): " + override.get("note", "")
        if chosen is None and ident in office_points:
            o = office_points[ident]
            chosen = {"lat": o["lat"], "lon": o["lon"], "location_source": "osm_ward_office", "location_ref": o["osm_id"],
                      "location_url": f"https://www.openstreetmap.org/{o['osm_id']}", "geocode_precision": "address",
                      "location_note": f"The ward office as mapped in OpenStreetMap ('{o['name']}'; {o['how']})."}
        if chosen is None and wp and osm_point:
            gap = W.hav(wp["lat"], wp["lon"], osm_point["lat"], osm_point["lon"])
            if gap <= cfg.get("location_disagreement_km", 5):
                chosen = {"lat": wp["lat"], "lon": wp["lon"], "location_source": "wikipedia", "location_ref": wp["title"], "location_url": wp["url"],
                          "location_note": f"Wikipedia ward point, corroborated by the {osm_point['what']} {gap:.1f} km away."}
            else:
                use_osm = osm_point["strong"]
                if use_osm:
                    chosen = {k: v for k, v in osm_point.items() if k not in ("what", "strong")}
                    chosen["location_note"] = f"{osm_point['what'][0].upper()}{osm_point['what'][1:]}; the Wikipedia point is {gap:.1f} km away (see Review Queue)."
                else:
                    chosen = {"lat": wp["lat"], "lon": wp["lon"], "location_source": "wikipedia", "location_ref": wp["title"], "location_url": wp["url"],
                              "location_note": f"Wikipedia ward point; the weaker {osm_point['what']} is {gap:.1f} km away (see Review Queue)."}
                reviews.add("location_sources_disagree", label, {"wikipedia": [wp["title"], wp["lat"], wp["lon"]],
                            "openstreetmap": [osm_point["location_ref"][:60], osm_point["lat"], osm_point["lon"]], "km_apart": round(gap, 1),
                            "used": "openstreetmap" if use_osm else "wikipedia"},
                            "Check which point lies in the ward and record an override in links.json if needed.")
        if chosen is None and osm_point:
            chosen = {k: v for k, v in osm_point.items() if k not in ("what", "strong")}
            chosen["location_note"] = f"{osm_point['what'][0].upper()}{osm_point['what'][1:]}" + ("; no Wikipedia ward point." if not wp else ".")
        if chosen is None and wp:
            chosen = {"lat": wp["lat"], "lon": wp["lon"], "location_source": "wikipedia", "location_ref": wp["title"], "location_url": wp["url"],
                      "location_note": "Wikipedia ward point; no OpenStreetMap evidence to corroborate it."}
        if chosen is None and gz:
            chosen = {"lat": gz[0], "lon": gz[1], "location_source": "gazetteer", "location_ref": gz[2], "location_url": "",
                      "location_note": f"Repository gazetteer ({gz[2]}); no Wikipedia or OpenStreetMap point."}
        if chosen is None:
            chosen = {"lat": None, "lon": None, "location_source": "none", "location_ref": "", "location_url": "",
                      "location_note": "No reference point found in Wikipedia, OpenStreetMap or the gazetteer."}
        chosen.setdefault("geocode_precision", "estimated" if chosen["lat"] is not None else "")
        located[f"{council}|{ward}"] = chosen
    return located


# ------------------------------------------------------------------ rosters
def parse_rosters(sites, transcriptions, census, cfg, links, reviews):
    """Ward councillors from official rosters: page lines ('<ward> Ward – Councilor: <name>') and transcriptions."""
    councils_by_host = {c["host"]: c["name"] for c in cfg["councils"]}
    wards = defaultdict(list)
    for w in census:
        wards[w["council"]].append(w)
    alias_map = {c: {G.squash(a): wd for a, wd in m.items()} for c, m in links.get("ward_aliases", {}).items() if not c.startswith("_")}

    def match(council, text):
        key = G.squash(text)
        for w in wards[council]:
            if G.squash(w["ward"]) == key:
                return w, "exact"
        if key in alias_map.get(council, {}):
            target = alias_map[council][key]
            return next((w for w in wards[council] if w["ward"] == target), None), "reviewed alias (links.json)"
        scored = sorted(((SequenceMatcher(None, key, G.squash(w["ward"])).ratio(), w) for w in wards[council]), key=lambda t: -t[0])
        if scored and scored[0][0] >= 0.85 and (len(scored) == 1 or scored[1][0] < scored[0][0]):
            return scored[0][1], f"similar spelling ({scored[0][0]:.2f})"
        return None, "unmatched"

    out = []
    line_rule = re.compile(r"^(?P<ward>.+?)\s+Ward\s*[–—-]\s*Councill?or:\s*(?P<name>.+)$", re.I)
    for host, site in sites.items():
        council = councils_by_host.get(host)
        if not council:
            continue
        for page in site.get("pages") or []:
            if not re.search(r"counc?il+or|concilor|madiwani", page["slug"] + " " + page["menu_path"], re.I):
                continue
            for line in page["text_en"].splitlines():
                if re.match(r"special seats", line, re.I):
                    break
                m = line_rule.match(line.strip())
                if not m:
                    continue
                ward, how = match(council, m.group("ward"))
                entry = {"council": council, "ward_as_published": m.group("ward"), "name_as_published": m.group("name").strip(),
                         "phone_as_published": "", "source_url": page["api_url"], "source_title": f"{site['organisation']}: {page['title']}",
                         "source_path": site["_file"], "source_location": f"page '{page['slug']}' (menu: {page['menu_path']})",
                         "published_on": str(page.get("updatedAt") or "")[:10], "match": how, "ward": ward["ward"] if ward else "",
                         "note": "", "evidence_basis": "official"}
                out.append(entry)
    for row in transcriptions:
        ward, how = match(row["council"], row["ward_as_published"])
        out.append({"council": row["council"], "ward_as_published": row["ward_as_published"], "name_as_published": row["name_as_published"],
                    "phone_as_published": row["phone_as_published"], "source_url": row["source_url"], "source_title": row["document_title"],
                    "source_path": row["_file"], "source_location": f"line {row['_line']} (PDF page {row['pdf_page']}, row {row['row_sn']})",
                    "published_on": "", "match": how, "ward": ward["ward"] if ward else "", "note": row.get("note", ""),
                    "evidence_basis": "official", "transcribed": True})
    for e in out:
        if not e["ward"]:
            reviews.add("roster_ward_unmatched", f"{e['name_as_published']} ({e['council']})", {"ward_as_published": e["ward_as_published"]},
                        "Add the census spelling to ward_aliases in links.json.")
        elif e["match"].startswith("similar"):
            reviews.add("roster_ward_similar_spelling", f"{e['ward']} ({e['council']})", {"published": e["ward_as_published"], "match": e["match"]},
                        "Confirm the ward and add the spelling to ward_aliases in links.json.")
    return out


# ------------------------------------------------------------------ main build
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    date, work, raw = cfg["research_date"], cfg["paths"]["work"], cfg["paths"]["raw"]
    links = G.load_links(cfg)
    reviews = Reviews()
    census, totals, wiki, places, osm_offices, sites, transcriptions = load_inputs(cfg)
    districts = G.load_districts(raw, date)
    campuses = W.load_campuses()
    clusters = cfg.get("campus_clusters", {})
    gaz = W.build_gazetteer(work)
    councils = {c["name"]: c for c in cfg["councils"]}
    regions = {r["region"]: r for r in cfg["regions"]}
    census_path = f"data/raw/government-research/nbs_2022_wards_{date}.csv"
    census_url = cfg["census"]["report_url"]

    # ---- wards: location, distances, catchment
    office_points = match_ward_offices(osm_offices, census, cfg, links, districts)
    office_by_osm = {v["osm_id"]: k for k, v in office_points.items()}
    located = locate_wards(cfg, census, wiki, places, districts, gaz, links, reviews, office_points)
    units = []
    for i, w in enumerate(census, 2):
        loc = located[f"{w['council']}|{w['ward']}"]
        fields = campus_fields(loc["lat"], loc["lon"], campuses, clusters)
        in_catchment = "unknown" if fields["distance_km"] is None else ("yes" if fields["distance_km"] <= cfg["catchment_km"] else "no")
        c = councils[w["council"]]
        units.append({"record_key": f"AU_ward_{slug(w['council'])}_{slug(w['ward'])}", "level": "ward", "name": w["ward"], "council": w["council"],
                      "region": c["region"], "admin_district": c["admin_district"], "core_council": c["core"],
                      "population_2022": w["population"], "male_2022": w["male"], "female_2022": w["female"], "households_2022": w["households"],
                      "avg_household_size_2022": w["avg_household_size"], "census_table": w["table"], "census_pdf_page": w["pdf_page"],
                      "census_printed_page": w["printed_page"], "census_row": w["ward_no"],
                      "census_source_location": f"{w['table']}, PDF page {w['pdf_page']} (printed page {w['printed_page']}), row {w['ward_no']}",
                      "census_url": census_url, "source_path": census_path, "source_line": i, **loc, **fields, "in_catchment": in_catchment})
    for name, check in totals["reconciliation"].items():
        c = councils[name]
        t = check["council_total"]
        units.append({"record_key": f"AU_council_{slug(name)}", "level": "council", "name": name, "council": name, "region": c["region"],
                      "admin_district": c["admin_district"], "core_council": c["core"], "population_2022": t["population"], "male_2022": t["male"],
                      "female_2022": t["female"], "households_2022": t["households"], "avg_household_size_2022": t["avg_household_size"],
                      "census_table": totals["tables"][name]["table"], "census_pdf_page": totals["tables"][name]["pdf_pages"][0],
                      "census_printed_page": totals["tables"][name]["printed_pages"][0], "census_row": 0,
                      "census_source_location": f"{totals['tables'][name]['table']}, PDF page {totals['tables'][name]['pdf_pages'][0]}: council total "
                                                f"(wards reconcile: {check['reconciles']})",
                      "census_url": census_url, "source_path": f"data/raw/government-research/nbs_2022_councils_{date}.json", "source_line": 0,
                      "lat": None, "lon": None, "location_source": "", "location_ref": "", "location_url": "", "location_note": "", "geocode_precision": "",
                      **campus_fields(None, None, campuses, clusters), "in_catchment": "", "wards_total": check["wards"]})
    ward_units = [u for u in units if u["level"] == "ward"]
    catch = [u for u in ward_units if u["in_catchment"] == "yes"]
    relevant = {f"{u['name']} ({u['council']})" for u in ward_units if u["core_council"] or u["in_catchment"] == "yes"}
    location_kinds = {"wikipedia_point_rejected", "location_sources_disagree", "location_claimed_by_two_wards", "osm_places_too_spread"}
    reviews.items = [r for r in reviews.items if r["kind"] not in location_kinds or r["entity"] in relevant]
    # ---- ward score (plan §5.5): population 30, transport 25, access 20, convening 15, yield 10
    pops = sorted(u["population_2022"] for u in catch)
    for u in ward_units:
        if u["in_catchment"] != "yes":
            u.update(ward_score=None, ward_tier="", factors_known="", score_factors="")
            continue
        below = sum(1 for p in pops if p < u["population_2022"])
        pct = below / (len(pops) - 1) if len(pops) > 1 else 1.0
        population_pts = round(30 * pct, 1)
        transport_pts = round(25 * (0.5 * BAND_WEIGHT.get(u["transport_band"], 0) + 0.5 * BAND_WEIGHT.get(u["primary_band"], 0)), 1)
        factors = {"population_2022_relative": population_pts, "transport_band": transport_pts, "access_readiness": 0,
                   "convening_opportunity": 0, "observed_yield": 0}
        u["ward_score"] = round(sum(factors.values()), 1)
        u["score_factors"] = json.dumps(factors)
        u["factors_known"] = "2 of 5"
        u["ward_tier"] = "P1" if u["ward_score"] >= 40 else "P2" if u["ward_score"] >= 30 else "P3" if u["ward_score"] >= 20 else "P4"
    for cluster in {u["campus_cluster"] for u in catch}:
        ranked = sorted((u for u in catch if u["campus_cluster"] == cluster), key=lambda u: (-u["ward_score"], -u["population_2022"]))
        for rank, u in enumerate(ranked, 1):
            u["rank_in_cluster"] = rank
    for u in ward_units:
        if u["in_catchment"] == "unknown" and u["core_council"]:
            reviews.add("ward_location_unknown", f"{u['name']} ({u['council']})", {"tried": "Wikipedia, OpenStreetMap places, gazetteer"},
                        "Find the ward office or a settlement in the ward and record it in links.json ward_locations.")

    # ---- which councils, districts and regions are in scope
    catch_by_council = Counter(u["council"] for u in catch)
    council_scope = [c for c in cfg["councils"] if c["core"] or catch_by_council[c["name"]]]
    region_scope = sorted({c["region"] for c in council_scope})
    district_scope = sorted({(c["region"], c["admin_district"]) for c in council_scope})

    # ---- rosters and profiles
    roster = parse_rosters(sites, transcriptions, census, cfg, links, reviews)
    roster_by_ward = defaultdict(list)
    for e in roster:
        if e["ward"]:
            roster_by_ward[(e["council"], e["ward"])].append(e)
    for (council, ward), entries in roster_by_ward.items():
        names = {G.ward_key(e["name_as_published"].replace("Hon.", "").replace("MHE.", "")) for e in entries}
        if len(names) > 1:
            reviews.add("roster_conflict", f"{ward} ({council})", {"names": [e["name_as_published"] for e in entries]},
                        "Two official sources name different councillors. Check the council's current roster.")

    offices, posts = [], []
    site_for = {c["name"]: sites.get(c["host"]) for c in cfg["councils"]}
    site_for.update({r["name"]: sites.get(r["host"]) for r in cfg["regions"]})

    def dept_page(site, post_key):
        pattern = DEPARTMENT_SLUGS.get(post_key)
        if not site or not pattern:
            return None
        return next((p for p in site.get("pages") or [] if re.search(pattern, p["slug"])), None)

    def make_posts(office, level, site=None, holders=None, extra_sources=None):
        for post_key, title, title_sw, appointment, b2g, role_note in POSTS[level]:
            holder = (holders or {}).get(post_key)
            page = dept_page(site, post_key)
            sources = list(extra_sources or [])
            if page:
                sources.insert(0, source(page["api_url"], f"{site['organisation']}: {page['title']}", "official", date,
                                         ["post exists", "division functions"], page["text_en"] or page["text_sw"]))
            if holder:
                sources.insert(0, source(holder["source_url"], holder["source_title"], holder.get("evidence_basis", "official"), date,
                                         ["holder name as published"] + (["phone as published"] if holder.get("phone") else []), holder.get("excerpt", "")))
            if not sources:
                act = ACT_URBAN if level in ("ward",) and office.get("urban") else ACT_DISTRICT
                sources.append(source(act, "Local Government Acts, 1982 (TanzLII)", "published", date, ["post defined by law"], "", fetched=False))
            phone = W.norm_phone(holder.get("phone")) if holder and holder.get("phone") else ""
            risk, reason = ("medium", "Named official as published by the office for its public role.") if holder else (
                "low", "Role desk; no personal data.")
            if phone:
                reason = ("Named elected official; mobile number published by the council on its official website so that residents "
                          "can reach councillors. Use only in the official role, after the council introduction (GA01).")
            posts.append({
                "record_key": f"GPOST_{office['slug']}_{post_key}", "office_key": office["record_key"], "organisation_name": office["name"],
                "organisation_domain": office.get("domain", ""), "locality": office.get("locality", ""), "office_level": level,
                "post_key": post_key, "office_title": title, "office_title_sw": title_sw, "role": f"{title_sw} ({title})",
                "appointment_type": appointment, "b2g_check_required": "yes" if b2g else "no", "convening_role": role_note,
                "holder_name": holder["name"] if holder else "", "holder_verified_on": date if holder else "",
                "tenure_source_url": holder["source_url"] if holder else "", "role_certainty": "confirmed" if holder else "role_desk",
                "role_phone": phone, "contact_route": "role_phone" if phone else ("published_role_email" if office.get("role_email") and post_key == "council_director" else "source_url"),
                "published_role_email": office.get("role_email", "") if post_key == "council_director" else "",
                "organisation_phone": office.get("public_phone", "") if post_key == "council_director" else "",
                "channel_attribution": holder.get("attribution", "") if holder else (office.get("route_attribution", "") if post_key == "council_director" else ""),
                "pdpa_risk": risk, "pdpa_risk_reason": reason,
                "verification_status": ("needs_review" if holder and holder.get("transcribed") else "verified") if holder else "needs_review",
                "source_url": sources[0]["url"], "evidence_basis": sources[0]["evidence_basis"], "evidence_excerpt": sources[0]["evidence_excerpt"] or f"{title_sw}: {role_note}",
                "source_path": holder.get("source_path", "") if holder else office["source_path"],
                "source_location": holder.get("source_location", "") if holder else f"post template for {level} offices (build_government_run.POSTS)",
                "all_sources": sources, "notes": holder.get("note", "") if holder else "Holder not published online; confirm with the office before any request.",
                "proposed_government_track": office["proposed_government_track"], "council_name": office.get("council_name", ""),
            })

    def profile_holders(site):
        found = {}
        for p in (site or {}).get("profiles") or []:
            text = f"{p.get('title') or ''} {p.get('titleSwahili') or ''}".lower()
            for pattern, post_key in PROFILE_RULES:
                if re.search(pattern, text) and post_key not in found:
                    found[post_key] = {"name": " ".join(str(p.get("name") or "").split()), "source_url": f"{site['base_url']}/api/profiles",
                                       "source_title": f"{site['organisation']}: leadership profiles", "source_path": site["_file"],
                                       "source_location": f"profiles[id={p.get('id')}] (updated {str(p.get('updatedAt') or '')[:10]})",
                                       "excerpt": f"{p.get('name')}: {p.get('title')} / {p.get('titleSwahili') or ''}",
                                       "attribution": "Official website leadership profile"}
                    break
        return found

    def footer_point(site):
        m = ((site or {}).get("footer") or {}).get("map") or {}
        lat, lon = m.get("lat"), m.get("lng")
        return (lat, lon) if valid_point(lat, lon) else (None, None)

    def footer_contact(site):
        found = {}

        def walk(o):
            if isinstance(o, dict):
                if any(o.get(k) for k in ("email", "phone", "poBox")):
                    found.update({k: o[k] for k in ("email", "phone", "poBox") if o.get(k)})
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk((site or {}).get("footer") or {})
        return found

    # regions
    for region in region_scope:
        r = regions[region]
        site = sites.get(r["host"])
        lat, lon = footer_point(site)
        rec = {"record_key": f"GOFF_region_{slug(region)}", "slug": f"region-{slug(region)}", "name": f"{r['name_sw']} ({r['name']})",
               "office_level": "region", "segment": "Local government office: region", "region": region, "council_name": "",
               "admin_unit_level": "region", "admin_unit_name": region, "parent_admin_unit": "Tanzania Mainland", "domain": r["host"],
               "website": f"https://{r['host']}", "locality": region, "lat": lat, "lon": lon,
               "geocode_precision": "address" if lat is not None else "", "location_source": "official website map" if lat is not None else "",
               "source_url": f"https://{r['host']}/api/profiles", "source_path": site["_file"] if site else "",
               "source_location": "profiles, statistics and footer", "evidence_basis": "official",
               "verification_status": "verified" if site and site.get("status") == "captured" else "needs_review",
               "proposed_government_track": "GA00 Hold", "track_reason": "Regional offices are not a v1 target (plan §1); keep for protocol and B2G coordination.",
               "size_evidence": "; ".join(f"{s['label']}: {s['value']}" for s in (site or {}).get("statistics") or []),
               "convening_forum": FORUMS["region"], "pdpa_risk": "low", "pdpa_risk_reason": "Public office; organisation-level facts only.",
               "missing_information": "Published phone, email and postal address (not in the site's API)."}
        rec["all_sources"] = [source(rec["source_url"], f"{r['name']} website (API)", "official", date, ["leadership", "statistics", "office map"])]
        offices.append(rec)
        make_posts(rec, "region", site, profile_holders(site))

    # districts (District Commissioner's offices)
    triage_links = {}
    for region, district in district_scope:
        r = regions[region]
        rsite = sites.get(r["host"])
        menu = next((m for m in (rsite or {}).get("menus") or [] if re.search(rf"\b{re.escape(district.lower())}\b", m["path"].lower()) and "district" in m["path"].lower()), None)
        rec = {"record_key": f"GOFF_district_{slug(district)}", "slug": f"district-{slug(district)}",
               "name": f"Ofisi ya Mkuu wa Wilaya ya {district} ({district} District Commissioner's Office)", "office_level": "district",
               "segment": "Local government office: council or district", "region": region, "council_name": "",
               "admin_unit_level": "district", "admin_unit_name": district, "parent_admin_unit": region, "domain": "", "website": "",
               "locality": district, "lat": None, "lon": None, "geocode_precision": "", "location_source": "",
               "source_url": f"https://{r['host']}/api/menus", "source_path": rsite["_file"] if rsite else "",
               "source_location": f"menu item: {menu['path']}" if menu else "district listed for its councils in the run config",
               "evidence_basis": "official" if menu else "research_note", "verification_status": "needs_review",
               "proposed_government_track": "GA00 Hold",
               "track_reason": "District public meetings are not a v1 target (plan §1). Holder and office route are not published online.",
               "size_evidence": ", ".join(c["name"] for c in council_scope if c["admin_district"] == district),
               "convening_forum": FORUMS["district"], "pdpa_risk": "low", "pdpa_risk_reason": "Public office; organisation-level facts only.",
               "missing_information": "Office address, phone and the current District Commissioner (not on the regional site; its district pages are empty)."}
        rec["all_sources"] = [source(rec["source_url"], f"{r['name']} website menu", rec["evidence_basis"], date, ["district exists"], menu["path"] if menu else "")]
        offices.append(rec)
        make_posts(rec, "district", None, {})

    # councils
    council_offices = {}
    for c in council_scope:
        site = site_for.get(c["name"])
        lat, lon = footer_point(site)
        contact = footer_contact(site)
        raw_map = ((site or {}).get("footer") or {}).get("map") or {}
        if raw_map and lat is None:
            reviews.add("official_map_point_invalid", c["name"], {"lat": raw_map.get("lat"), "lng": raw_map.get("lng")},
                        "The council website's map point is malformed, so it was not used. Ask the council or use the OpenStreetMap office.")
        stats = "; ".join(f"{s['label']}: {s['value']}" for s in (site or {}).get("statistics") or [])
        total = next(u for u in units if u["level"] == "council" and u["name"] == c["name"])
        site_pop = next((s["value"] for s in (site or {}).get("statistics") or []
                         if re.search(r"^(population|idadi ya watu|watu)$", str(s.get("label") or "").strip(), re.I) and isinstance(s.get("value"), (int, float))), None)
        if site_pop and abs(site_pop - total["population_2022"]) > 0.01 * total["population_2022"]:
            reviews.add("council_population_differs", c["name"], {"website": site_pop, "census_2022": total["population_2022"]},
                        "The council website shows a different population from the 2022 census (perhaps a projection). The run uses the census.")
        rec = {"record_key": f"GOFF_council_{slug(c['name'])}", "slug": f"council-{slug(c['name'])}", "name": f"{c['name_sw']} ({c['name']})",
               "unit_key": total["record_key"],
               "office_level": "council", "segment": "Local government office: council or district", "region": c["region"],
               "council_name": c["name"], "admin_unit_level": "council", "admin_unit_name": c["name"], "parent_admin_unit": c["admin_district"],
               "domain": c["host"], "website": f"https://{c['host']}", "locality": c["admin_district"], "lat": lat, "lon": lon,
               "geocode_precision": "address" if lat is not None else "", "location_source": "official website map" if lat is not None else "",
               "public_email": W.norm_email(contact.get("email")), "public_phone": contact.get("phone", ""), "po_box": contact.get("poBox", ""),
               "role_email": W.norm_email(contact.get("email")),
               "route_attribution": "Official website footer (keyServices contact block)" if contact else "",
               "source_url": f"https://{c['host']}/api/profiles", "source_path": site["_file"] if site else "",
               "source_location": "profiles, statistics, footer and menus", "evidence_basis": "official",
               "verification_status": "verified" if site and site.get("status") == "captured" else "needs_review",
               "census_2022_population": total["population_2022"], "census_source_location": total["census_source_location"],
               "catchment_wards": catch_by_council[c["name"]], "wards_total": total.get("wards_total"),
               "catchment_population_2022": sum(u["population_2022"] for u in catch if u["council"] == c["name"]),
               "size_evidence": stats, "convening_forum": FORUMS["council"], "core_council": c["core"],
               "pdpa_risk": "low", "pdpa_risk_reason": "Public office; organisation-level facts only.", "urban": c.get("urban", False)}
        route_known = bool(lat is not None or contact)
        if c["core"] and route_known:
            rec["proposed_government_track"], rec["track_reason"] = "GA01 Protocol introduction", (
                "Core council (plan §5.1) with its office published on its official website. Send the Kiswahili letter by hand, call after 5 working days, then visit.")
        elif c["core"]:
            rec["proposed_government_track"], rec["track_reason"] = "GA00 Hold", "Core council, but no office location or contact is published; find the route first."
        else:
            rec["proposed_government_track"], rec["track_reason"] = "GA00 Hold", (
                f"Outside the v1 pilot councils (plan §5.10); {catch_by_council[c['name']]} of its wards fall within {cfg['catchment_km']} km of a campus.")
        missing = []
        if not contact.get("phone"):
            missing.append("published phone")
        if not contact.get("email"):
            missing.append("published email")
        if not contact.get("poBox"):
            missing.append("postal address")
        rec["missing_information"] = ("Not in the site's API: " + ", ".join(missing) + ".") if missing else ""
        rec["all_sources"] = [source(rec["source_url"], f"{c['name']} website (API)", "official", date, ["leadership", "statistics", "office map", "contact block"]),
                              source(census_url, cfg["census"]["report_title"], "official", date, ["2022 population", "ward list"])]
        offices.append(rec)
        council_offices[c["name"]] = rec
        make_posts(rec, "council", site, profile_holders(site))

    # wards (catchment wards, plus core-council wards whose location is unknown)
    ward_offices = {}
    for u in ward_units:
        if not (u["in_catchment"] == "yes" or (u["in_catchment"] == "unknown" and u["core_council"])):
            continue
        c = councils[u["council"]]
        parent = council_offices.get(u["council"])
        rec = {"record_key": f"GOFF_ward_{slug(u['council'])}_{slug(u['name'])}", "slug": f"ward-{slug(u['council'])}-{slug(u['name'])}",
               "unit_key": u["record_key"],
               "name": f"Ofisi ya Kata ya {u['name']} ({u['council']})", "office_level": "ward",
               "segment": "Local government office: ward, village or mtaa", "region": u["region"], "council_name": u["council"],
               "admin_unit_level": "ward", "admin_unit_name": u["name"], "parent_admin_unit": u["council"], "domain": "", "website": "",
               "locality": u["name"], "lat": u["lat"], "lon": u["lon"], "geocode_precision": u["geocode_precision"],
               "location_source": u["location_source"], "location_ref": u["location_ref"], "location_note": u["location_note"],
               "source_url": census_url, "source_path": census_path, "source_location": f"line {u['source_line']}: {u['census_source_location']}",
               "evidence_basis": "official", "verification_status": "needs_review",
               "census_2022_population": u["population_2022"], "census_source_location": u["census_source_location"],
               "ward_score": u["ward_score"], "ward_tier": u["ward_tier"], "score_factors": u["score_factors"], "factors_known": u["factors_known"],
               "rank_in_cluster": u.get("rank_in_cluster"), "size_evidence": f"2022 census: {u['population_2022']:,} residents, {u['households_2022']:,} households",
               "convening_forum": FORUMS["ward"], "pdpa_risk": "low", "pdpa_risk_reason": "Public office; organisation-level facts only.",
               "proposed_government_track": "GA00 Hold",
               "track_reason": "Reach through the council introduction (GA01) first. GA02 needs that introduction and a post verified within 90 days.",
               "missing_information": "Ward office location and phone, WEO name (ask the council after GA01)" + ("" if roster_by_ward.get((u["council"], u["name"])) else "; councillor not published online") + ".",
               "urban": c.get("urban", False), "core_council": c["core"]}
        rec.update({k: u[k] for k in ("campus", "distance_km", "transport_band", "nearest_primary_campus", "distance_to_primary_km", "primary_band", "campus_cluster")})
        rec["all_sources"] = [source(census_url, cfg["census"]["report_title"], "official", date, ["ward exists", "2022 population", "households"],
                                     f"{u['name']} {u['population_2022']:,} ({u['census_source_location']})")]
        if u["location_url"]:
            rec["all_sources"].append(source(u["location_url"], f"{u['location_source']}: {u['location_ref']}",
                                             "published" if u["location_source"] == "wikipedia" else "directory", date, ["estimated ward location"], u["location_note"]))
        if parent:
            rec["all_sources"].append(source(parent["source_url"], f"{u['council']} website (API)", "official", date, ["council leadership and structure"]))
        offices.append(rec)
        ward_offices[(u["council"], u["name"])] = rec
        holders = {}
        entries = roster_by_ward.get((u["council"], u["name"]), [])
        if entries:
            e = sorted(entries, key=lambda e: (not e.get("phone_as_published"), e.get("transcribed", False)))[0]
            attribution = f"{e['source_title']} ({e['source_location']})"
            holders["ward_councillor"] = {"name": e["name_as_published"], "phone": e.get("phone_as_published", ""), "source_url": e["source_url"],
                                          "source_title": e["source_title"], "source_path": e["source_path"], "source_location": e["source_location"],
                                          "excerpt": f"{e['ward_as_published']}: {e['name_as_published']}", "attribution": attribution,
                                          "transcribed": e.get("transcribed", False),
                                          "note": "; ".join(x for x in (e.get("note"), f"ward matched: {e['match']}" if e["match"] != "exact" else "",
                                                                        "Transcribed from a scanned official list; check against the scan." if e.get("transcribed") else "") if x)}
        make_posts(rec, "ward", site_for.get(u["council"]), holders)

    # ---- published office routes found by contact research (scripts/contacts/export_run_contact_research.py)
    for path in sorted(raw.glob("office_contacts_*.json")):
        found = json.loads(path.read_text(encoding="utf-8")).get("offices", {})
        for rec in offices:
            info = found.get(rec["name"])
            if not info or rec["office_level"] not in ("council", "region", "district"):
                continue
            email = next((e["email"] for e in info["emails"] if e["type"] in ("role", "general")), "")
            phone = next((p["phone"] for p in info["phones"]), "")
            if email and not rec.get("public_email"):
                rec["public_email"] = rec["role_email"] = email
            if phone and not rec.get("public_phone"):
                rec["public_phone"] = phone
            if info["postal"] and not rec.get("po_box"):
                rec["po_box"] = info["postal"][0]
            if email or phone or info["postal"]:
                rec["route_attribution"] = rec.get("route_attribution") or f"Official route found by contact research ({path.name})"
                rec["missing_information"] = ("; ".join(x for x, known in (("published phone", rec.get("public_phone")), ("published email", rec.get("public_email")),
                                                                            ("postal address", rec.get("po_box"))) if not known))
                rec["missing_information"] = f"Not found: {rec['missing_information']}." if rec["missing_information"] else ""
                # The director's post was built before this research was read; give it the office routes too.
                for post in posts:
                    if post["office_key"] == rec["record_key"] and post["post_key"] == "council_director":
                        post["published_role_email"] = post["published_role_email"] or rec.get("role_email", "")
                        post["organisation_phone"] = post["organisation_phone"] or rec.get("public_phone", "")
                        post["channel_attribution"] = post["channel_attribution"] or rec["route_attribution"]
                        if post["contact_route"] == "source_url" and post["published_role_email"]:
                            post["contact_route"] = "published_role_email"
            for s in info["sources"][:4]:
                rec["all_sources"].append(source(s["url"], s.get("title", ""), "official" if ".go.tz" in s["url"] else "published", date,
                                                 ["office contact route"], s.get("excerpt", ""), fetched=bool(s.get("fetched"))))

    # ---- OpenStreetMap offices: classify, log exclusions, link conveners
    office_links = links.get("osm_office_links", {})
    triage = []
    unnamed = Counter()
    for el in osm_offices:
        name = el["tags"].get("name", "")
        if not name:
            unnamed[el["tags"].get("government") or el["tags"].get("office") or el["tags"].get("amenity") or "untagged"] += 1
            continue
        category, detail = G.classify_office(name, el["tags"])
        district = G.district_of(el["lat"], el["lon"], districts) if valid_point(el["lat"], el["lon"]) else ""
        fields = campus_fields(el["lat"], el["lon"], campuses, clusters)
        entry = {"source": "openstreetmap", "source_id": el["osm_id"], "name": name, "category": category, "detail": detail,
                 "tags": json.dumps({k: v for k, v in el["tags"].items() if k in ("office", "amenity", "government", "operator", "building")}),
                 "osm_district": district, "lat": el["lat"], "lon": el["lon"], "campus": fields["campus"], "distance_km": fields["distance_km"],
                 "linked_office": "", "note": ""}
        link = office_links.get(el["osm_id"], {})
        if link.get("category"):
            entry["note"] = f"Reviewed decision (links.json): {link.get('note', '')}"
            category = entry["category"] = link["category"]
            detail = entry["detail"] = link.get("detail", detail)
        if category == "convener":
            target = None
            ward_ident = office_by_osm.get(el["osm_id"])
            if ward_ident:
                target = ward_offices.get(ward_ident)
            elif detail == "council":
                target = next((v for k, v in council_offices.items() if G.squash(councils[k]["name_sw"]).replace("halmashauriyawilayaya", "") in G.squash(name)), None)
            elif detail == "district":
                target = next((o for o in offices if o["office_level"] == "district" and G.squash(o["admin_unit_name"]) in G.squash(name)), None)
            elif detail == "region":
                target = next((o for o in offices if o["office_level"] == "region" and G.squash(o["admin_unit_name"]) in G.squash(name)), None)
            if detail == "village" and fields["distance_km"] is not None and fields["distance_km"] <= cfg["catchment_km"]:
                council_name = link.get("council") or next((cn for cn, cc in councils.items() if cc["osm_district"] == district), "")
                ward_name = link.get("ward", "")
                village = re.sub(r"(?i)village office|office ya kijiji|ofisi ya kijiji|ofisi|office", " ", name).strip()
                if not ward_name and council_name:
                    same_name = [u["name"] for u in ward_units if u["council"] == council_name and G.squash(u["name"]) == G.squash(village)]
                    near = sorted((W.hav(el["lat"], el["lon"], u["lat"], u["lon"]), u["name"]) for u in ward_units
                                  if u["council"] == council_name and u["lat"] is not None)
                    ward_name, basis = (same_name[0], "the village shares the ward's name") if same_name else (
                        (near[0][1], "nearest ward reference point") if near else ("", "no ward reference point"))
                    reviews.add("village_office_ward_estimated", name, {"osm_id": el["osm_id"], "council": council_name, "ward": ward_name, "basis": basis},
                                "Confirm which ward this village belongs to and record it in links.json osm_office_links.")
                rec = {"record_key": f"GOFF_village_{slug(el['osm_id'])}", "slug": f"village-{slug(el['osm_id'])}",
                       "name": f"Ofisi ya Kijiji cha {' '.join(village.split())} ({council_name or 'council unconfirmed'})", "office_level": "village",
                       "segment": "Local government office: ward, village or mtaa", "region": councils[council_name]["region"] if council_name else "",
                       "council_name": council_name, "admin_unit_level": "village", "admin_unit_name": " ".join(village.split()),
                       "parent_admin_unit": ward_name, "domain": "", "website": "", "locality": " ".join(village.split()),
                       "lat": el["lat"], "lon": el["lon"], "geocode_precision": "address", "location_source": "openstreetmap office",
                       "location_ref": el["osm_id"], "osm_id": el["osm_id"], "source_url": f"https://www.openstreetmap.org/{el['osm_id']}",
                       "source_path": f"data/raw/government-research/osm_government_offices_{date}.json", "source_location": el["osm_id"],
                       "evidence_basis": "directory", "verification_status": "needs_review", "convening_forum": FORUMS["village"],
                       "pdpa_risk": "low", "pdpa_risk_reason": "Public office; organisation-level facts only.", "proposed_government_track": "GA00 Hold",
                       "track_reason": "Reach through the council introduction (GA01) and the ward executive officer first.",
                       "missing_information": "Village executive officer and chairperson; village assembly calendar; confirm the ward.",
                       **{k: fields[k] for k in ("campus", "distance_km", "transport_band", "nearest_primary_campus", "distance_to_primary_km", "primary_band", "campus_cluster")}}
                rec["all_sources"] = [source(rec["source_url"], f"OpenStreetMap: {name}", "directory", date, ["office exists", "office location"])]
                offices.append(rec)
                make_posts(rec, "village", None, {})
                target = rec
            if target:
                entry["linked_office"] = target["record_key"]
                if target["office_level"] in ("ward", "district", "region") and not target.get("osm_id"):
                    target["osm_id"] = el["osm_id"]
                    if target["office_level"] != "ward" or target.get("location_source") != "openstreetmap office":
                        target.update(lat=el["lat"], lon=el["lon"], geocode_precision="address", location_source="openstreetmap office",
                                      location_note=f"OpenStreetMap office {el['osm_id']}.")
                        target.update({k: fields[k] for k in ("campus", "distance_km", "transport_band", "nearest_primary_campus",
                                                              "distance_to_primary_km", "primary_band", "campus_cluster")})
                    target["all_sources"].append(source(f"https://www.openstreetmap.org/{el['osm_id']}", f"OpenStreetMap: {name}", "directory", date, ["office location"]))
                elif target["office_level"] == "council":
                    entry["note"] = (entry["note"] + " " if entry["note"] else "") + "Council location taken from its official website; OpenStreetMap point kept for reference."
            elif detail != "village":
                reviews.add("convener_office_unlinked", name, {"osm_id": el["osm_id"], "level": detail, "osm_district": district},
                            "Link it to its ward, council or district office in links.json osm_office_links, or confirm it is outside the scope.")
        if category == "excluded" and detail == "religious" and G.office_level(name):
            reviews.add("exclusion_conflicts_with_name", name, {"osm_id": el["osm_id"], "tags": entry["tags"]},
                        "Name says it is an administrative office but the map tags it as a place of worship. It stays excluded until a documented review decision.")
        triage.append(entry)
    for kind, count in unnamed.items():
        triage.append({"source": "openstreetmap", "source_id": f"{count} unnamed elements", "name": "", "category": "unidentified",
                       "detail": f"government={kind}" if kind != "untagged" else "", "tags": "", "osm_district": "", "lat": None, "lon": None,
                       "campus": "", "distance_km": None, "linked_office": "",
                       "note": "Unnamed office points cannot be identified as conveners; not imported."})

    for o in offices:
        if valid_point(o.get("lat"), o.get("lon")) and o.get("distance_km") is None:
            o.update(campus_fields(o["lat"], o["lon"], campuses, clusters))
        if o["office_level"] == "village" and councils.get(o.get("council_name"), {}).get("urban"):
            reviews.add("village_office_in_urban_council", o["name"], {"council": o["council_name"], "osm_id": o.get("osm_id")},
                        "Urban councils have mitaa, not villages. Check whether this is a mtaa office, a former village office, or mapped in the wrong place.")

    # ---- company master office:government records (read-only triage)
    master_rows = master_government_records()
    osm_by_name = {G.squash(t["name"]): t for t in triage if t["name"]}
    master_triage = []
    group_for = {"convener": "Local administration office", "excluded": "Excluded", "not_government": "Tagged as government but is not",
                 "agency": "Agency or parastatal", "unclassified": "Unclassified"}
    treatment = {"convener": "Move to government_convener after verification (through silverleaf-update-lead-list)",
                 "excluded": "Exclude from convening; never contact for this track",
                 "not_government": "Reclassify through review (silverleaf-update-lead-list)",
                 "agency": "Remains a corporate employer (corporate track)", "unclassified": "Review"}
    for m in master_rows:
        category, detail = G.classify_office(m["name"])
        group = group_for[category]
        if category == "excluded" and detail == "religious":
            group, category = "Tagged as government but is not", "not_government"
        osm = osm_by_name.get(G.squash(m["name"]))
        master_triage.append({"master_organisation_id": m["organisation_id"], "name": m["name"], "master_campus": m["campus"],
                              "master_distance_km": m["distance_km"], "category": category, "detail": detail, "group": group,
                              "proposed_treatment": treatment[category], "matched_osm_id": osm["source_id"] if osm else "",
                              "linked_office": osm["linked_office"] if osm else ""})
        if osm and osm["linked_office"]:
            office = next(o for o in offices if o["record_key"] == osm["linked_office"])
            office["master_organisation_id"] = m["organisation_id"]
        if category in ("excluded", "not_government"):
            reviews.add("master_correction", m["name"], {"master_organisation_id": m["organisation_id"], "group": group, "detail": detail},
                        f"{treatment[category]}. Apply to the master only through silverleaf-update-lead-list.")

    # ---- convening signals from council news and notices
    signals = []
    scope_hosts = {c["host"] for c in council_scope} | {regions[r]["host"] for r in region_scope}
    for host, site in sites.items():
        if host not in scope_hosts:
            continue
        owner = next((c["name"] for c in cfg["councils"] if c["host"] == host), next((r["name"] for r in cfg["regions"] if r["host"] == host), host))
        for key in ("news", "announcements"):
            for n in site.get(key) or []:
                tags = [t for t in n.get("convening_tags") or [] if t != "parents_or_education"]
                if not tags:
                    continue
                signals.append({"organisation": owner, "host": host, "kind": key, "item_id": n["id"], "date": n["date"], "title": n["title"],
                                "tags": ", ".join(n["convening_tags"]), "listing_url": n["listing_url"], "source_path": site["_file"]})
    signals.sort(key=lambda s: s["date"], reverse=True)

    # ---- master campus note and generic gaps
    for c in council_scope:
        if not any(e["council"] == c["name"] for e in roster):
            reviews.add("roster_not_published", c["name"], {"host": c["host"]},
                        "No ward-by-ward councillor list is published online. Ask the council for the current list after the GA01 introduction.")
    track_counts = Counter(o["proposed_government_track"] for o in offices)
    final = {"run_id": args.run_id, "research_date": date, "admin_units": units, "offices": offices, "posts": posts, "office_triage": triage,
             "master_triage": master_triage, "signals": signals, "roster": roster,
             "summary": {"wards": len(ward_units), "catchment_wards": len(catch), "ward_locations": dict(Counter(u["location_source"] for u in ward_units)),
                         "offices": dict(Counter(o["office_level"] for o in offices)), "posts": len(posts),
                         "named_holders": sum(1 for p in posts if p["holder_name"]), "tracks": dict(track_counts),
                         "councils_in_scope": [c["name"] for c in council_scope], "reviews": len(reviews.items),
                         "triage": dict(Counter(t["category"] for t in triage)), "signals": len(signals)}}
    (work / "final.json").write_text(json.dumps(final, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    (work / "review_items.json").write_text(json.dumps(reviews.items, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(final["summary"], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
