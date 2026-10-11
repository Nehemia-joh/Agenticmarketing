#!/usr/bin/env python3
"""Campus gap census: what OpenStreetMap and the directories record around each campus, against what the three lead lists hold.

Reads (no network):
- data/raw/gap-census/osm_<category>_<date>.json            OpenStreetMap features by category (collect_gap_census.py)
- data/raw/gap-census/google_maps_named_<date>.jsonl         Google Maps place pins found in the browser (coordinator)
- data/raw/gap-census/research_targeted_<date>.jsonl         targeted known gaps from official pages and directories
- the welfare run's NGO register table (registry_ngos): international NGOs registered inside the catchment
- the master (organisations, campuses), the welfare run and the government run databases, read-only
Matches every feature to the existing leads: OpenStreetMap ID, website domain, then name plus distance (a similar name within
0.5 km is a match; the same name farther away is a second site to review; a lead without coordinates matches on a near-exact
name only). Junk is kept out with a reason: closed or disused places, unnamed features, generic names, schools and kindergartens
(competitors, or not an employer target), single-person practices and workshops, airstrips, industrial zones, party offices,
police, courts and prisons.

Writes:
- data/raw/gap-census/candidates_<date>.jsonl                every new or review candidate within 25 km, one per organisation
- data/raw/gap-census/master_intake_<date>.csv               new employers in the shared intake contract (validate_intake.py)
- data/raw/gap-census/research_GC_welfare_<date>.jsonl       new welfare candidates in the welfare research format
- data/raw/gap-census/government_subward_units_<date>.json   villages and mitaa in the pilot councils, with their ward
- data/raw/gap-census/faith_candidates_<date>.json           places of worship by campus (candidate list only)
- outputs/reports/campus-gap-census-<date>.md                the census per campus and category, and the largest gaps
Distances and bands come from the master's campuses table. Nothing is written to any database.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "government"))
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import gov_lib as G  # noqa: E402  (office classification, districts)
import recompute_campus_distances as RC  # noqa: E402  (band, tier, campus_key)

RAW = ROOT / "data" / "raw" / "gap-census"
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE_RUN, GOVERNMENT_RUN = "arusha-welfare-2026-09", "arusha-government-2026-09"
WELFARE_DB = ROOT / "outputs" / "runs" / WELFARE_RUN / "lead-database.sqlite"
GOVERNMENT_DB = ROOT / "outputs" / "runs" / GOVERNMENT_RUN / "lead-database.sqlite"
TEMPLATE = ROOT / "skills" / "silverleaf-create-lead-list" / "assets" / "lead-intake-template.csv"
REPORTS = ROOT / "outputs" / "reports"
CATCHMENT_KM = 25.0
CAMPUS_ORDER = ["Arusha City", "Ilboru", "Kijenge", "Usa River", "Boma Ngombe"]
CAMPUS_LABEL = {"Arusha City": "Arusha City (Sakina)", "Ilboru": "Ilboru", "Kijenge": "Kijenge", "Usa River": "Usa River", "Boma Ngombe": "Boma Ng'ombe"}
# A feature in several category files is counted once, in the first category of this order.
CATEGORY_ORDER = ["aviation", "banks", "education", "health", "social", "tourism", "retail", "farms", "industrial", "offices", "worship", "places"]
CATEGORY_LABEL = {"offices": "Offices (company, NGO, government, international, ...)", "industrial": "Industrial and factory sites",
                  "farms": "Farms, estates and nurseries", "health": "Hospitals and clinics", "education": "Colleges, universities and research",
                  "tourism": "Hotels, lodges and camps", "retail": "Supermarkets and malls", "banks": "Banks, insurers and finance",
                  "aviation": "Airport and aviation", "worship": "Places of worship",
                  "social": "Social facilities, kindergartens and daycares", "places": "Villages, hamlets and neighbourhoods"}
PILOT_COUNCILS = ["Arusha City Council", "Arusha District Council", "Meru District Council", "Hai District Council"]
# Employer kinds: the existing seven (build_company_audience_profile.kind_of) and the five proposed here.
NEW_KINDS = {"International organisations": 4, "Manufacturing": 3, "Farms and estates": 2, "Aviation": 3, "Retail": 2}
FIT = {
    "Safari operators and travel agencies": "a tour or travel business with office and field staff",
    "Hotels, lodges and camps": "a hotel, lodge or camp with resident staff",
    "Banks and other companies": "a company office with salaried staff",
    "Hospitals and clinics": "a health facility with clinical and support staff",
    "Colleges and universities": "a college or university with academic and support staff",
    "Public bodies": "a public body with civil-service staff (HR route only, after a compliance check)",
    "NGOs and research bodies": "an NGO or research body with local staff",
    "International organisations": "an international organisation with national and international staff",
    "Manufacturing": "a factory or industrial site with a permanent workforce",
    "Farms and estates": "a farm, estate or seed/flower operation with a permanent workforce",
    "Aviation": "an airport or aviation operator with salaried technical and ground staff",
    "Retail": "a supermarket or mall with permanent shop-floor and management staff",
}
WELFARE_SEGMENT = {"Residential care (children's homes)": ("Welfare residential care", "residential"),
                   "Specialised centres": ("Welfare specialised centre", "specialised"),
                   "Family-based and sponsorship programmes": ("Welfare family-based programme", "family_based"),
                   "Unclassified child-focused": ("Welfare (unclassified child-focused NGO)", "")}

SCHOOL = re.compile(r"\b(school|academy|shule|nursery|pre-?school|pre-?primary|kindergarten|kinder|day ?care|chekechea|montessori|sekondari|secondary|primary|"
                    r"elimu ya awali|awali)\b", re.I)
NOT_SCHOOL = re.compile(r"college|universit|institute|chuo|polytechnic|training cent|veta", re.I)
CLOSED = re.compile(r"\b(closed|zamani|former|defunct|abandoned)\b|\(old\)", re.I)
SILVERLEAF = re.compile(r"silver ?leaf", re.I)
CHILD = re.compile(r"orphan|yatima|child|watoto|kids|baby|babies|rescue|street|girls|boys|youth home|makao|vulnerable|malaika|neema|upendo|tumaini", re.I)
GENERIC = {"farm", "shamba", "office", "ofisi", "hotel", "lodge", "church", "kanisa", "mosque", "msikiti", "supermarket", "clinic", "hospital",
           "zahanati", "bank", "atm", "factory", "kiwanda", "industry", "industries", "warehouse", "store", "godown", "greenhouse", "nursery",
           "camp", "campsite", "guest house", "guesthouse", "orchard", "plantation", "estate", "company", "ngo"}
NAME_STOP = {"the", "ltd", "limited", "co", "company", "plc", "tz", "tanzania", "t", "inc", "and", "of", "for", "a", "na", "ya", "wa", "la", "cha"}
WEAK = {"arusha", "moshi", "kilimanjaro", "meru", "usa", "river", "tengeru", "hai", "hotel", "lodge", "camp", "camps", "safari", "safaris", "tours",
        "tour", "travel", "travels", "hospital", "clinic", "centre", "center", "health", "medical", "bank", "office", "group", "east", "africa",
        "african", "international", "services", "service", "tanzanian", "branch", "house", "guest", "resort", "suites", "inn", "lutheran",
        "church", "kanisa", "catholic", "foundation", "organisation", "organization", "trust", "regional", "zone", "northern", "national",
        "mount", "airport", "united", "community", "grand", "royal", "white", "home", "homes", "park", "garden", "view", "star", "green",
        "new", "city", "golden", "villa", "villas", "hostel", "backpackers", "limited", "dispensary", "saccos", "staff", "workers", "lodges",
        "investment", "investments", "enterprises", "company", "general", "union", "institute", "college", "university", "school", "orphanage",
        "orphan", "orphans", "children", "child", "care", "village", "rescue", "mission", "missions", "ministries", "ministry", "initiative",
        "initiatives", "project", "projects", "development", "supermarket", "market", "store", "stores", "shop", "farm", "farms", "estate"}
OSM_URL = "https://www.openstreetmap.org/{}"
JUNK_NAME = re.compile(r"^(new |girls |boys |main |public )?(hostel|campsite|campsite \d+|public campsite \d+|building|house|canteen|cafe|market\??|"
                       r"agricultural area|farming spot|wareshed|granja|dispens[ae]ry|medical shop|staff office|head ?master office)$|"
                       r"\bstreet\b|\broad\b|\(approximate\)|real lacation|correct location|10\.000ts|parking|vor/dme|\bils\b|outer marker|navigation aid|help desk|"
                       r"admnistration|administration block|^departures$|^arrivals$|^@", re.I)
PART_OF_SITE = re.compile(r"\b(class ?hall|lecture ?hall|class(es)?\b|new classes|canteen|main (cafe|get|gate)|\bgate\b|\bget\b|cyber|computer room|"
                          r"stationer|stionaries|library|block [a-z0-9]|\(ch\d|toilet|new building|main house)\b", re.I)
SMALL_WORKS = re.compile(r"posho|milling machine|mill milling|\bmills?\.|machine\b|workshop|garage|welding|carpentry|matofali|brick|vibrated|"
                         r"godoro|juakali|cooperative", re.I)
CORPORATE = re.compile(r"\b(ltd|limited|company|co\.|industr\w*|factory|brewer\w*|bottl\w*|textiles?|plant|works|kiwanda|enterprises?|group|"
                       r"manufactur\w*|packag\w*|plastics?|steel|cement|dairy|meat|foods?|beverages?|oils?|millers|tannery|packers|printing|"
                       r"foam|paints?|pharma\w*|chemicals?)\b", re.I)
FARM_CUE = re.compile(r"farms?\b|estate|flower|flora|maua|seeds?\b|horti|plantation|zaden|cuttings?|\bltd|limited|dairy|poultry|coffee|kahawa|"
                      r"orchard|green ?houses?|nursery ltd", re.I)


# ------------------------------------------------------------------ helpers
def hav(a, b, c, d) -> float:
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin(math.radians(c - a) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def num(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def key(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s).replace("&", " and ").replace("'s", "s")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = s.replace("centre", "center").replace("childrens", "children")
    return " ".join(w for w in s.split() if w not in NAME_STOP)


def strong_tokens(k: str) -> set[str]:
    return {w for w in k.split() if w not in WEAK and len(w) > 2}


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    ta, tb = strong_tokens(a), strong_tokens(b)
    if ta and tb:
        small, big = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
        # every distinctive word of the shorter name appears in the longer: two words, or one long word when both names have one
        if small <= big and (len(small) >= 2 or (len(big) == 1 and len(next(iter(small))) >= 6)):
            ratio = max(ratio, 0.9)
        elif not (ta & tb):
            ratio = min(ratio, 0.6)  # no distinctive word in common: never a match
        elif (ta - tb) and (tb - ta):
            ratio = min(ratio, 0.8)  # each name has a distinctive word the other lacks ('Moshi ... MUWSA' and 'Arusha ... AUWSA')
    return ratio


FAMILIES = [("saccos", r"savings group|saccos"), ("tourism", r"hotel|lodge|camp|guest|tourism|safari|tour|travel|resort|hostel"),
            ("health", r"hospital|clinic|health|dispensary|medical"), ("finance", r"bank|insurance|financial"),
            ("education", r"college|universit|educational"), ("welfare", r"welfare|children|orphan"), ("government", r"government|public")]


def family(text: str) -> str:
    low = str(text or "").lower()
    return next((f for f, pat in FAMILIES if re.search(pat, low)), "")


def domain(url: str) -> str:
    u = str(url or "").strip().lower()
    if not u or "@" in u and "://" not in u:
        return ""
    u = re.sub(r"^[a-z]+://", "", u).split("/")[0].split(":")[0]
    u = u[4:] if u.startswith("www.") else u
    shared = ("facebook.com", "instagram.com", "google.com", "goo.gl", "wixsite.com", "blogspot.com", "wordpress.com", "linkedin.com", "tripadvisor",
              "booking.com", "openstreetmap.org", "twitter.com", "x.com", "youtube.com", "tatotz.org", "ushirika.go.tz")
    return "" if not u or "." not in u or any(s in u for s in shared) else u


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()] if path.exists() else []


def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


# ------------------------------------------------------------------ the existing leads
def load_campuses() -> dict[str, tuple[float, float]]:
    con = ro(MASTER)
    out = {RC.campus_key(r["name"]): (r["latitude"], r["longitude"]) for r in con.execute("SELECT name, latitude, longitude FROM campuses")}
    con.close()
    return out


def nearest(campuses, lat, lon):
    best = min(((hav(lat, lon, *pt), c) for c, pt in campuses.items()), key=lambda x: x[0])
    return best[1], round(best[0], 1)


def load_leads() -> tuple[list[dict], dict[str, dict]]:
    """Every organisation the three lists hold, plus the OpenStreetMap IDs the welfare and government runs already reviewed."""
    leads, osm_reviewed = [], {}
    con = ro(MASTER)
    for r in con.execute("SELECT organisation_id, name, segment, latitude, longitude, osm_id, website, email, locality FROM organisations"):
        leads.append({"db": "master", "id": r["organisation_id"], "name": r["name"], "segment": r["segment"] or "", "lat": num(r["latitude"]),
                      "lon": num(r["longitude"]), "osm_id": r["osm_id"] or "", "domain": domain(r["website"]) or domain((r["email"] or "").split("@")[-1])})
    con.close()
    con = ro(WELFARE_DB)
    for r in con.execute("SELECT organisation_id, name, segment, latitude, longitude, osm_id, website FROM organisations"):
        leads.append({"db": "welfare", "id": r["organisation_id"], "name": r["name"], "segment": r["segment"] or "", "lat": num(r["latitude"]),
                      "lon": num(r["longitude"]), "osm_id": r["osm_id"] or "", "domain": domain(r["website"])})
    for r in con.execute("SELECT nis_id, name, matched_organisation_id, welfare_fit, level FROM registry_ngos"):
        if r["matched_organisation_id"]:
            leads.append({"db": "welfare", "id": r["matched_organisation_id"], "name": r["name"], "segment": "NGO register entry", "lat": None,
                          "lon": None, "osm_id": "", "domain": ""})
    con.close()
    # the welfare run's alternative names ('Kafika House' was 'The Plaster House'), from its last build
    final = ROOT / "runtime" / "welfare" / WELFARE_RUN / "final.json"
    if final.exists():
        for o in json.loads(final.read_text(encoding="utf-8")).get("organisations", []):
            for alt in o.get("alternative_names") or []:
                leads.append({"db": "welfare", "id": o["organisation_name"], "name": alt, "segment": o.get("segment") or "", "lat": num(o.get("latitude")),
                              "lon": num(o.get("longitude")), "osm_id": "", "domain": ""})
    links = json.loads((ROOT / "data" / "runs" / WELFARE_RUN / "links.json").read_text(encoding="utf-8"))
    for name, v in (links.get("osm") or {}).items():
        if isinstance(v, dict) and v.get("osm_id"):
            osm_reviewed[v["osm_id"]] = {"db": "welfare", "id": v.get("organisation") or name, "name": name, "basis": "reviewed by the welfare run (links.json osm)"}
    con = ro(GOVERNMENT_DB)
    for r in con.execute("SELECT organisation_id, name, segment, latitude, longitude, osm_id, website FROM organisations"):
        leads.append({"db": "government", "id": r["organisation_id"], "name": r["name"], "segment": r["segment"] or "", "lat": num(r["latitude"]),
                      "lon": num(r["longitude"]), "osm_id": r["osm_id"] or "", "domain": ""})
    for r in con.execute("SELECT source_id, name, category, detail, linked_organisation_id AS linked_office FROM office_triage"):
        if r["source_id"]:
            osm_reviewed.setdefault(r["source_id"], {"db": "government", "id": r["linked_office"] or "", "name": r["name"],
                                                     "basis": f"triaged by the government run ({r['category']} {r['detail'] or ''})".strip()})
    con.close()
    for lead in leads:
        lead["key"] = key(lead["name"])
        lead["tokens"] = strong_tokens(lead["key"])
    return leads, osm_reviewed


class Matcher:
    def __init__(self, leads: list[dict], osm_reviewed: dict):
        self.leads = leads
        self.by_osm = {l["osm_id"]: l for l in leads if l["osm_id"]}
        self.by_domain = defaultdict(list)
        for l in leads:
            if l["domain"]:
                self.by_domain[l["domain"]].append(l)
        self.by_token = defaultdict(list)
        for l in leads:
            for t in l["tokens"] or set(l["key"].split()[:1]):
                self.by_token[t].append(l)
        self.osm_reviewed = osm_reviewed

    def match(self, name: str, lat, lon, osm_id: str = "", site: str = "", alt_names=(), kind: str = "") -> dict:
        """{'status': captured|review|new, 'lead': ..., 'basis': ..., 'score': ..., 'saccos': staff savings group of the same name}"""
        res = self._match(name, lat, lon, osm_id, site, alt_names, kind)
        saccos = ""
        for nm in [name, *alt_names]:
            k = key(nm)
            for l in {id(l): l for t in strong_tokens(k) for l in self.by_token.get(t, [])}.values():
                if family(l["segment"]) == "saccos" and similarity(k, key(re.sub(r"(?i)\b(staff|workers|employees?)?\s*saccos\b.*", "", l["name"]))) >= 0.85:
                    saccos = l["name"]
        res["saccos"] = saccos
        return res

    def _match(self, name, lat, lon, osm_id, site, alt_names, kind):
        if osm_id and osm_id in self.by_osm:
            l = self.by_osm[osm_id]
            return {"status": "captured", "lead": l, "basis": "same OpenStreetMap ID", "score": 1.0}
        d = domain(site)
        if d and self.by_domain.get(d):
            l = self.by_domain[d][0]
            return {"status": "captured", "lead": l, "basis": f"same website domain ({d})", "score": 1.0}
        best = None
        for nm in [name, *alt_names]:
            k = key(nm)
            pool = {id(l): l for t in (strong_tokens(k) or set(k.split()[:1])) for l in self.by_token.get(t, [])}
            for l in pool.values():
                if family(l["segment"]) == "saccos":
                    continue
                s = similarity(k, l["key"])
                if s < 0.7:
                    continue
                fl, fk = family(l["segment"] + " " + l["name"]), family(kind)
                if fl and fk and fl != fk and SequenceMatcher(None, k, l["key"]).ratio() < 0.9:
                    continue
                if fl == fk == "finance" and (set(k.split()) - WEAK) & (set(l["key"].split()) - WEAK):
                    s = max(s, 0.92)  # 'NMB' and 'NMB Bank': a bank or insurer's branch shares its brand with the lead
                dist = hav(lat, lon, l["lat"], l["lon"]) if None not in (lat, lon, l["lat"], l["lon"]) else None
                if dist is not None and dist <= 0.5 and s >= 0.85:
                    res = {"status": "captured", "lead": l, "basis": f"name {s:.2f} within {dist:.2f} km", "score": s + 1}
                elif dist is None and s >= 0.92:
                    res = {"status": "captured", "lead": l, "basis": f"name {s:.2f} (the lead has no coordinates)", "score": s + 0.5}
                elif dist is not None and dist > 0.5 and s >= 0.92:
                    res = {"status": "review", "lead": l, "basis": f"same name {dist:.1f} km away: a second site or branch, or a misplaced lead", "score": s}
                elif dist is not None and dist <= 0.5:
                    res = {"status": "review", "lead": l, "basis": f"similar name ({s:.2f}) within {dist:.2f} km", "score": s}
                elif dist is None and s >= 0.85:
                    res = {"status": "review", "lead": l, "basis": f"similar name ({s:.2f}); the lead has no coordinates", "score": s - 0.1}
                else:
                    continue
                if best is None or res["score"] > best["score"]:
                    best = res
        if best:
            return best
        if osm_id and osm_id in self.osm_reviewed:
            r = self.osm_reviewed[osm_id]
            return {"status": "captured", "lead": {"db": r["db"], "id": r["id"], "name": r["name"]}, "basis": r["basis"], "score": 1.0}
        return {"status": "new", "lead": None, "basis": "", "score": 0.0}


# ------------------------------------------------------------------ classification of OpenStreetMap features
def employer(sub: str, org_segment: str, note: str = "") -> dict:
    return {"segment": "employer", "subsegment": sub, "org_segment": org_segment, "note": note}


def welfare(sub: str, note: str = "") -> dict:
    return {"segment": "welfare", "subsegment": sub, "org_segment": WELFARE_SEGMENT[sub][0], "note": note}


def excluded(reason: str) -> dict:
    return {"segment": "excluded", "subsegment": "", "org_segment": "", "note": reason}


def classify(cat: str, tags: dict) -> dict:
    name = (tags.get("name") or tags.get("name:en") or tags.get("official_name") or "").strip()
    low = name.lower()
    if cat == "places":
        return {"segment": "government", "subsegment": tags.get("place", ""), "org_segment": "", "note": ""}
    if not name:
        return excluded("unnamed feature")
    if any(tags.get(k) for k in ("disused", "abandoned", "disused:amenity")) or tags.get("operational_status") in ("closed", "abandoned") or CLOSED.search(name):
        return excluded("closed or disused")
    if SILVERLEAF.search(name):
        return excluded("a Silverleaf campus")
    if low in GENERIC or len(key(name)) < 3 or JUNK_NAME.search(name):
        return excluded("generic name, no organisation named")
    if PART_OF_SITE.search(name) and cat in ("education", "tourism", "offices", "banks", "health"):
        return excluded("a building or room of a larger site")
    if cat == "worship" or tags.get("amenity") == "place_of_worship" or tags.get("office") == "religion":
        return {"segment": "faith-candidate", "subsegment": tags.get("religion", "") or "unknown", "org_segment": "", "note": ""}
    school = SCHOOL.search(name) and not NOT_SCHOOL.search(name)
    if cat == "social":
        sf, sf_for = tags.get("social_facility", ""), tags.get("social_facility:for", "")
        if tags.get("amenity") in ("kindergarten", "childcare") and not re.search(r"orphan|yatima|children'?s home|rescue|makao", low):
            return excluded("kindergarten or daycare: a competitor, not an outreach target")
        if re.search(r"senior|elderly|wazee|aged", sf_for + " " + low):
            return excluded("care for older people: outside the welfare scope")
        if re.search(r"disab|rehab|deaf|blind|albin|street|rescue|special", sf_for + " " + low):
            return welfare("Specialised centres")
        if sf in ("group_home", "shelter", "orphanage") or tags.get("amenity") == "orphanage" or re.search(r"orphan|yatima|children'?s home|children'?s village|baby home|makao", low) \
                or sf_for in ("orphan", "child", "juvenile"):
            return welfare("Residential care (children's homes)")
        if CHILD.search(low) or sf_for in ("child", "orphan", "juvenile", "underprivileged"):
            return welfare("Unclassified child-focused")
        if school:
            return excluded("school (a competitor or not an employer target)")
        return excluded("social facility not for children (or unknown purpose)")
    if school:
        return excluded("school (a competitor or not an employer target)")
    if cat == "aviation":
        if re.search(r"airstrip|air ?strip|helipad", low) or tags.get("aeroway") == "heliport":
            return excluded("airstrip or helipad: no staff on site")
        return employer("Aviation", f"aeroway:{tags.get('aeroway') or tags.get('office') or 'aviation'}")
    if cat == "banks":
        if tags.get("amenity") == "bank":
            return employer("Banks and other companies", "amenity:bank")
        if tags.get("office") in ("accountant", "tax_advisor"):
            return employer("Banks and other companies", f"office:{tags['office']}", "small professional office")
        return employer("Banks and other companies", f"office:{tags.get('office', 'financial')}")
    if cat == "education":
        if re.search(r"police|military|jeshi|prison|magereza", low):
            return excluded("police, military or prison college")
        if not re.search(r"college|universit|univerisity|institut|chuo|seminary|polytechnic|school of|academy of|cent(re|er)|training|research|campus|vyuo", low):
            return excluded("a building or room of a larger site")
        if tags.get("amenity") == "research_institute" or tags.get("office") == "research":
            return employer("NGOs and research bodies", "office:research")
        return employer("Colleges and universities", f"amenity:{tags.get('amenity') or 'college'}")
    if cat == "health":
        if re.search(r"traditional|medical shop|duka la dawa|pharmacy", low):
            return excluded("traditional healer or shop")
        if tags.get("amenity") in ("doctors", "dentist") and not re.search(r"hospital|clinic|medical|health|polyclinic|cent|kituo|zahanati|dispensary", low):
            return excluded("single practitioner's practice")
        kind = tags.get("amenity") or tags.get("healthcare") or "clinic"
        return employer("Hospitals and clinics", f"amenity:{'hospital' if kind == 'hospital' else 'clinic'}",
                        "government dispensary or health centre (public staff)" if re.search(r"zahanati|kituo cha afya|dispensary|health cent", low) else "")
    if cat == "tourism":
        t = tags.get("tourism") or tags.get("leisure") or "hotel"
        if t == "apartment" and not re.search(r"hotel|lodge|resort|suites|serviced", low):
            return excluded("private apartments")
        if re.search(r"restaurant|hall|traditional", low) and not re.search(r"hotel|lodge|resort|inn", low):
            return excluded("not a hotel (restaurant or hall)")
        if not re.search(r"hotel|lodge|camp|resort|\binn\b|motel|suites|villas?\b|cottages?|guest ?house|g\u00e4stehaus|backpacker|chalets?|tented|"
                         r"retreat|safari", low):
            return {"segment": "employer", "subsegment": "Hotels, lodges and camps", "org_segment": "tourism:guest_house", "weak": True,
                    "note": "no hotel or lodge word in the name (a homestay, hostel or private house?): confirm it is a business with staff"}
        seg = {"camp_site": "tourism:camp_site", "guest_house": "tourism:guest_house", "hostel": "tourism:guest_house (hostel)", "chalet": "tourism:lodge"}.get(t, "tourism:hotel")
        return employer("Hotels, lodges and camps", seg)
    if cat == "retail":
        if tags.get("shop") == "mall" or re.search(r"complex|plaza|centre|center|mall\b", low) and not re.search(r"supermarket", low):
            return excluded("mall or commercial complex: its tenants are the employers")
        if re.search(r"\bmini\b|minimart|mini-?market|\bduka\b|kiosk|genge|convenien|grocery|campus shop|\bmarket\b(?! basket)|cinema", low):
            return excluded("small shop or open market")
        if not re.search(r"supermarket|super market|shoppers|food lover|mr ?price|\bgame\b|shoprite|wholesale|cash ?(and|&|n) ?carry|jumla|market basket|"
                         r"hypermarket|department|stores? (ltd|limited)", low):
            return excluded("small shop or open market")
        return employer("Retail", f"shop:{tags.get('shop', 'supermarket')}")
    if cat == "farms":
        if re.search(r"college|school|hospital|church", low):
            return excluded("farm plot of another institution")
        if not FARM_CUE.search(name):
            return excluded("small farm or plot with no business named")
        return employer("Farms and estates", "farm:estate")
    if cat == "industrial":
        if re.search(r"airport|aerodrome|terminal", low):
            return employer("Aviation", "aeroway:aerodrome")
        if re.search(r"industrial area|industrial estate|industrial park|eneo la viwanda|\bsido\b|export processing zone|\bepz\b|\bsez\b", low) and not re.search(r"ltd|limited", low):
            return excluded("industrial zone (an area, not one employer)")
        if SMALL_WORKS.search(name) and not re.search(r"\b(ltd|limited|company|factory|industries)\b", low):
            return excluded("small workshop or mill (no company named)")
        if tags.get("craft") and tags["craft"] not in ("brewery", "winery", "distillery", "beverages", "dairy", "sawmill") and not CORPORATE.search(name):
            return excluded("small workshop or mill (no company named)")
        if re.search(r"farm|estate|flower|seed|horti|plantation|coffee|green ?house|zaden|cutting", low) and not re.search(r"factory|mill|brewer", low):
            return employer("Farms and estates", "farm:estate")
        if not CORPORATE.search(name) and not tags.get("operator") and not tags.get("website"):
            return {"segment": "employer", "subsegment": "Manufacturing", "org_segment": "industrial:manufacturing",
                    "note": "industrial site with no company named in the map: confirm the operator", "weak": True}
        return employer("Manufacturing", "industrial:manufacturing")
    # offices
    office = tags.get("office", "")
    if office == "political_party":
        return excluded("political party office")
    if office == "government" or tags.get("government"):
        if re.search(r"region offce|disctict council office", low):
            return {"segment": "government", "subsegment": "office:unclear", "org_segment": "",
                    "note": "bulk-mapped label ('region offce', 'disctict council office'): confirm what office this is"}
        category, detail = G.classify_office(tags.get("name:sw") or name, tags)
        if category != "convener":
            category, detail = G.classify_office(name, tags) if G.classify_office(name, tags)[0] == "convener" else (category, detail)
        if category == "convener":
            return {"segment": "government", "subsegment": f"office:{detail}", "org_segment": "", "note": "local government office"}
        if category == "excluded":
            return excluded(f"government office excluded from outreach ({detail})")
        if re.search(r"\beac\b|east african|african union|united nations|\bun\b|tribunal|court of human|residual mechanism|\bau\b", low):
            return employer("International organisations", "International organisation")
        return employer("Public bodies", "office:government", "public body or agency (HR route only)")
    if office in ("diplomatic", "international_organization", "un", "international") or re.search(
            r"united nations|\bunicef\b|\bundp\b|\bwfp\b|\biom\b|\bunhcr\b|\bwho\b|african union|east african community|\beac\b|residual mechanism|irmct|unmict|african court|ecsa|esami|postal union", low):
        return employer("International organisations", "International organisation")
    if office in ("ngo", "charity", "foundation", "association", "non_profit", "union", "cooperative"):
        if CHILD.search(low):
            return welfare("Unclassified child-focused", "an office whose name names children; welfare review")
        if office == "cooperative" or re.search(r"\bsaccos?\b|\bvicoba\b", low):
            return excluded("savings or co-operative group (the master's savings-group list covers them)")
        return employer("NGOs and research bodies", "office:ngo")
    if office in ("research", "educational_institution"):
        return employer("NGOs and research bodies" if office == "research" else "Colleges and universities",
                        "office:research" if office == "research" else "office:educational_institution")
    if office == "airline" or re.search(r"airlines?\b|airways|aviation|air cargo", low):
        return employer("Aviation", "aeroway:airline office")
    if re.search(r"\bseeds?\b|zaden|horti|flowers?\b|cuttings", low):
        return employer("Farms and estates", "farm:seed or flower company")
    if office in ("travel_agent", "tour_operator", "guide") or re.search(r"safari|tours?\b|travel|expedition|adventure", low):
        return employer("Safari operators and travel agencies", "office:travel_agent")
    if office == "airline":
        return employer("Aviation", "aeroway:airline office")
    if office in ("insurance", "financial"):
        return employer("Banks and other companies", f"office:{office}")
    if office in ("lawyer", "notary", "accountant", "tax_advisor", "estate_agent", "architect", "surveyor", "therapist", "physician", "coworking"):
        return excluded("small professional office")
    if CHILD.search(low) and re.search(r"home|orphan|centre|center|foundation", low):
        return welfare("Unclassified child-focused", "an office whose name names children; welfare review")
    return employer("Banks and other companies", f"office:{office or 'company'}")


# ------------------------------------------------------------------ government offices mapped in OpenStreetMap
UNIT_WORDS = re.compile(r"(?i)\b(sub ?ward village office|sub ?ward office|ward office|ward building|village office|office|ofisi ya afisa mtendaji( wa)?|"
                        r"ofisi ya (kata|kijiji|mtaa|kanda)( ya| cha| wa| la)?|ofis ya kata ya|ofsi ya kata( ya)?|ofisi( ya)?|kata ya|kijiji cha|mtaa wa)\b")


class GovIndex:
    """The government run's councils, districts and wards, to recognise the offices OpenStreetMap maps."""

    def __init__(self, gconf: dict):
        con = ro(GOVERNMENT_DB)
        self.wards = [dict(r) for r in con.execute("SELECT name, council, latitude, longitude, office_organisation_id, geocode_precision, location_source "
                                                  "FROM admin_units WHERE level='ward'")]
        self.offices = [dict(r) for r in con.execute("SELECT o.organisation_id, o.name, o.osm_id FROM organisations o")]
        con.close()
        self.council_names = {}
        for c in gconf["councils"]:
            self.council_names[G.squash(c["name"])] = c["name"]
            self.council_names[G.squash(c["name_sw"])] = c["name"]

    def match_office(self, f: dict, name: str, cls: dict, campus: str, dist) -> dict:
        tags = f["tags"]
        level = cls["subsegment"].split(":", 1)[-1]
        both = name + " " + tags.get("name:sw", "")
        unit = " ".join(UNIT_WORDS.sub(" ", tags.get("name:en") or name).split()) or " ".join(UNIT_WORDS.sub(" ", tags.get("name:sw", "")).split())
        if re.search(r"(?i)sub ?ward village office|ofisi ya kijiji", both):
            level = "village"
        elif re.search(r"(?i)sub ?ward office|ofisi ya mtaa", both):
            level = "mtaa"
        rec = {"osm_id": f["osm_id"], "name": name, "name_sw": tags.get("name:sw", ""), "level": level, "unit": unit, "latitude": f["lat"],
               "longitude": f["lon"], "precision": "point", "source_url": OSM_URL.format(f["osm_id"]), "campus": campus, "distance_km": dist,
               "status": "new", "matched": "", "matched_id": "", "current_reference": "", "moves_km": None, "note": cls.get("note", "")}
        hit = next((o for o in self.offices if o["osm_id"] == f["osm_id"]), None)
        if hit:
            rec.update(status="captured", matched=hit["name"], matched_id=hit["organisation_id"], note="already linked in the government run")
            return rec
        if level == "ward":
            same = [w for w in self.wards if G.squash(w["name"]) == G.squash(unit)]
            near = sorted(((hav(f["lat"], f["lon"], w["latitude"], w["longitude"]) if w["latitude"] is not None else 99.0), i) for i, w in enumerate(same))
            if near and near[0][0] <= 15:
                w = same[near[0][1]]
                rec.update(status="captured", matched=f"{w['council']}|{w['name']}", matched_id=w["office_organisation_id"] or "",
                           current_reference=f"{w['geocode_precision'] or ''} ({w['location_source'] or ''})", moves_km=round(near[0][0], 2),
                           note="ward office point: the government run places this ward at an estimate; propose links.json osm_office_links")
            elif near:
                rec.update(status="review", matched=f"{same[near[0][1]]['council']}|{same[near[0][1]]['name']}",
                           note=f"same ward name {near[0][0]:.1f} km away: check the council")
            else:
                rec.update(status="review", note="no ward of this name in the census list: check the spelling or the council")
            return rec
        if level in ("council", "district", "region"):
            sq = G.squash(re.sub(r"(?i)district council|city council|municipal council", "", name))
            for k, v in self.council_names.items():
                if sq and (sq in k or k.startswith(sq)):
                    rec.update(status="captured", matched=v, note="council office point")
                    return rec
            rec.update(status="review", note="council or district office not matched to the run's councils")
            return rec
        rec.update(status="new" if level in ("village", "mtaa") else "review")
        return rec


# ------------------------------------------------------------------ sources
def osm_candidates(date: str, campuses) -> tuple[list[dict], dict]:
    feats, seen, meta = [], set(), {}
    for cat in CATEGORY_ORDER:
        path = RAW / f"osm_{cat}_{date}.json"
        if not path.exists():
            meta[cat] = {"missing": True}
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        meta[cat] = {"endpoints": data.get("endpoints"), "osm_base": data.get("osm_base"), "file": path.relative_to(ROOT).as_posix(), "elements": len(data["elements"])}
        for el in data["elements"]:
            if el["osm_id"] in seen:
                continue
            seen.add(el["osm_id"])
            dists = {c: hav(el["lat"], el["lon"], *pt) for c, pt in campuses.items()}
            if min(dists.values()) > CATCHMENT_KM:
                continue
            feats.append({"category": cat, "osm_id": el["osm_id"], "lat": el["lat"], "lon": el["lon"], "tags": el["tags"], "dists": dists, "path": meta[cat]["file"]})
    return feats, meta


def address_of(tags: dict) -> str:
    if tags.get("addr:full"):
        return tags["addr:full"]
    parts = [" ".join(p for p in (tags.get("addr:housenumber", ""), tags.get("addr:street", "")) if p), tags.get("addr:suburb", ""), tags.get("addr:place", ""),
             tags.get("addr:city", "")]
    return ", ".join(p for p in parts if p)


def phone_of(tags: dict) -> str:
    return (tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or "").split(";")[0].strip()


def site_of(tags: dict) -> str:
    s = (tags.get("website") or tags.get("contact:website") or tags.get("url") or "").split(";")[0].strip()
    if s and "://" not in s:
        s = "https://" + s
    return s


def email_of(tags: dict) -> str:
    e = (tags.get("email") or tags.get("contact:email") or "").split(";")[0].strip()
    return e if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", e) else ""


# ------------------------------------------------------------------ main build
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default="2026-10-11", help="date stamp of the raw files and outputs")
    args = parser.parse_args()
    date = args.date
    campuses = load_campuses()
    leads, osm_reviewed = load_leads()
    matcher = Matcher(leads, osm_reviewed)
    feats, meta = osm_candidates(date, campuses)
    gconf = json.loads((ROOT / "data" / "runs" / GOVERNMENT_RUN / "run-config.json").read_text(encoding="utf-8"))
    districts = G.load_districts(ROOT / "data" / "raw" / "government-research", "2026-09-23")
    district_council = {c["osm_district"]: c["name"] for c in gconf["councils"]}

    gov = GovIndex(gconf)
    gov_points = []
    census = defaultdict(Counter)          # (campus, category) -> counter
    census_all = defaultdict(Counter)      # category -> counter (unique features)
    excluded_reasons = defaultdict(Counter)
    candidates: dict[str, dict] = {}       # candidate_id -> record
    faith = []
    places = []

    def campus_counts(f, field):
        for c, d in f["dists"].items():
            if d <= CATCHMENT_KM:
                census[(c, f["category"])][field] += 1
        census_all[f["category"]][field] += 1

    # 1. OpenStreetMap features
    osm_new = []
    for f in feats:
        tags = f["tags"]
        name = (tags.get("name") or tags.get("name:en") or tags.get("official_name") or "").strip()
        cls = classify(f["category"], tags)
        campus_counts(f, "osm")
        if name:
            campus_counts(f, "named")
        campus, dist = nearest(campuses, f["lat"], f["lon"])
        if cls["segment"] == "excluded":
            campus_counts(f, "excluded")
            excluded_reasons[f["category"]][cls["note"]] += 1
            continue
        if cls["segment"] == "government" and f["category"] == "places":
            places.append({**f, "name": name, "campus": campus, "distance_km": dist})
            continue
        if cls["segment"] == "government":
            point = gov.match_office(f, name, cls, campus, dist)
            gov_points.append(point)
            campus_counts(f, point["status"])
            continue
        if cls["segment"] == "faith-candidate":
            m = matcher.match(name, f["lat"], f["lon"], f["osm_id"])
            if m["status"] == "captured":
                campus_counts(f, "captured")
            else:
                campus_counts(f, "new")
            faith.append({"name": name, "religion": tags.get("religion", ""), "denomination": tags.get("denomination", ""), "latitude": f["lat"],
                          "longitude": f["lon"], "precision": "point", "osm_id": f["osm_id"], "source_url": OSM_URL.format(f["osm_id"]), "campus": campus,
                          "distance_km": dist, "in_lists": m["status"] == "captured", "matched": (m["lead"] or {}).get("name", "")})
            continue
        m = matcher.match(name, f["lat"], f["lon"], f["osm_id"], site_of(tags), (), cls["subsegment"] + " " + cls["org_segment"])
        if m["status"] == "captured":
            campus_counts(f, "captured")
            continue
        if cls.get("weak") and m["status"] == "new":
            m = {**m, "status": "review", "basis": cls["note"]}
        campus_counts(f, "new" if m["status"] == "new" else "review")
        osm_new.append({"feature": f, "name": name, "cls": cls, "match": m, "campus": campus, "distance_km": dist})

    # 2. curated sources (Google Maps pins from the coordinator, targeted directory records) - preferred over OpenStreetMap
    curated = []
    google = [(g, False) for g in read_jsonl(RAW / f"google_maps_named_{date}.jsonl")] + \
             [(g, True) for g in read_jsonl(RAW / f"google_maps_user_named_{date}.jsonl")]
    for g, user_named in google:
        curated.append({"candidate_source": "google_maps", "user_named": user_named, "name": g["name"], "alt_names": [], "segment": g["segment"],
                        "subsegment": g["proposed_subsegment"],
                        "org_segment": {"International organisations": "International organisation", "Manufacturing": "industrial:manufacturing",
                                        "Aviation": "aeroway:aerodrome", "Farms and estates": "farm:flowers",
                                        "Safari operators and travel agencies": "office:travel_agent",
                                        "Hotels, lodges and camps": "tourism:hotel"}.get(g["proposed_subsegment"], "office:company"),
                        "latitude": g["latitude"], "longitude": g["longitude"], "precision": g["precision"], "coord_source_url": g["source_url"],
                        "locality": "", "address": g.get("address", ""), "website": g.get("website", ""), "phone": g.get("phone", ""), "email": "",
                        "google_maps_url": g["source_url"] if "google." in g["source_url"] else "", "google_category": g.get("google_category", ""),
                        "evidence": [{"url": g["source_url"], "fetched_on": g["fetched"], "fetched": True, "evidence_basis": "directory", "source_date": "",
                                      "excerpt": (f"Google Maps listing '{g['name']}' ({g.get('google_category', '')}), {g.get('address', '')}" if g.get('google_category') else f"{g.get('source', '')}: '{g['name']}', {g.get('address', '')}").strip()}],
                        "reason": "", "verification_status": "verified", "notes": " ".join(x for x in (g.get("source", ""), g.get("note", "")) if x), "search_ref": "",
                        "raw_file": f"data/raw/gap-census/google_maps_{'user_' if user_named else ''}named_{date}.jsonl"})
    for t in read_jsonl(RAW / f"research_targeted_{date}.jsonl"):
        if t.get("supplements"):  # official details for a record found elsewhere (a Google Maps pin): merge, never a second record
            base = next((c for c in curated if c["name"] == t["supplements"]), None)
            if base is not None:
                for f in ("address", "website", "phone", "email"):
                    base[f] = base.get(f) or t.get(f, "")
                base["evidence"] = base["evidence"] + t["evidence"]
                base["search_ref"] = base.get("search_ref") or t.get("search_ref", "")
                base["notes"] = " ".join(x for x in (base.get("notes", ""), t.get("notes", "")) if x)
            continue
        curated.append({**t, "raw_file": f"data/raw/gap-census/research_targeted_{date}.jsonl"})
    # The welfare run's NGO register: international NGOs inside the catchment that no list holds and that are active.
    wcon = ro(WELFARE_DB)
    for r in wcon.execute("SELECT * FROM registry_ngos WHERE level='International' AND COALESCE(matched_organisation_id,'')=''"):
        lat, lon = num(r["latitude"]), num(r["longitude"])
        if lat is None or r["welfare_fit"] in ("likely",):
            continue
        active = (r["latest_project_end"] or "") >= "2024-01-01" or (r["reg_date"] or "") >= "2023-01-01"
        if not active:
            continue
        nm = " ".join(str(r["name"]).split())
        if SCHOOL.search(nm) and not NOT_SCHOOL.search(nm):
            continue
        child = r["welfare_fit"] == "possible" or bool(CHILD.search(nm))
        curated.append({"candidate_source": "ngo_register", "name": nm.title() if nm.isupper() else nm, "alt_names": [nm], "segment": "employer",
                        "subsegment": "NGOs and research bodies", "org_segment": "office:ngo", "latitude": lat, "longitude": lon, "precision": "address",
                        "coord_source_url": r["profile_url"], "locality": r["district"] or "", "address": "", "website": "", "phone": "", "email": "",
                        "google_maps_url": "",
                        "evidence": [{"url": r["profile_url"], "fetched_on": "2026-09-22", "fetched": True, "evidence_basis": "official", "source_date": r["reg_date"] or "",
                                      "excerpt": f"International NGO registered {r['reg_no']} ({r['reg_date']}); latest project to {r['latest_project_end'] or 'n/a'}; {r['region']}, {r['district']}"}],
                        "reason": "", "verification_status": "needs_review" if child else "verified",
                        "notes": ("The register entry names children: check whether it belongs in the welfare run instead. " if child else "")
                                 + "Location is the register's own map pin.", "search_ref": "", "raw_file": "data/raw/welfare-research/nis_catchment_profiles_2026-09-22.jsonl"})
    wcon.close()

    # Attach coordinates to curated records that have none: an OpenStreetMap feature of the same organisation, else none (map lookup).
    osm_by_name = defaultdict(list)
    for f in feats:
        n = (f["tags"].get("name") or "").strip()
        if n:
            osm_by_name[key(n)].append(f)
    consumed = set()
    gaz = RC.gazetteer()
    for c in curated:
        names = [c["name"], *c.get("alt_names", [])]
        for n in (list(names) if c["candidate_source"] == "google_maps" else []):  # 'AtoZ Group Limited (A to Z Textile Mills)'
            inner = re.findall(r"\(([^)]+)\)", n)
            names += [i for i in inner if len(key(i)) > 3] + ([re.sub(r"\s*\([^)]*\)", "", n).strip()] if inner else [])
        names += [re.split(r" [–-] ", n)[0] for n in names if re.search(r" [–-] ", n)]
        c["alt_names"] = list(dict.fromkeys(a for a in names[1:] if a and a != c["name"]))
        if c.get("coords_from_osm_name"):
            hit = next((f for f in feats if key(f["tags"].get("name", "")) == key(c["coords_from_osm_name"])), None)
            g = next((o for o in curated if o is not c and o.get("latitude") is not None and o["candidate_source"] == "google_maps"
                      and similarity(key(o["name"]), key(c["coords_from_osm_name"])) >= 0.9), None)
            if g is not None:
                c.update(latitude=g["latitude"], longitude=g["longitude"], precision="address", coord_source_url=g["coord_source_url"],
                         notes=(c.get("notes", "") + f" Coordinates of the site it shares ({g['name']}, Google Maps pin).").strip())
            elif hit is None:
                hit = next((l for l in leads if key(l["name"]) == key(c["coords_from_osm_name"]) and l["lat"] is not None), None)
                if hit:
                    c.update(latitude=hit["lat"], longitude=hit["lon"], precision="address", coord_source_url=f"lead {hit['db']}:{hit['id']}",
                             notes=(c.get("notes", "") + f" Coordinates of the site it shares ({hit['name']}).").strip())
            else:
                c.update(latitude=hit["lat"], longitude=hit["lon"], precision="address", coord_source_url=OSM_URL.format(hit["osm_id"]),
                         notes=(c.get("notes", "") + f" Coordinates of the site it shares ({hit['tags'].get('name')}, OpenStreetMap).").strip())
        # the same organisation in OpenStreetMap: use its point when the record has none, and drop it from the OSM list either way
        best = None
        for f in feats:
            n = (f["tags"].get("name") or "").strip()
            if not n:
                continue
            s = max(similarity(key(a), key(n)) for a in names)
            if s < 0.85:
                continue
            if c.get("latitude") is not None and hav(c["latitude"], c["longitude"], f["lat"], f["lon"]) > 3:
                continue
            if best is None or s > best[0]:
                best = (s, f)
        if best:
            consumed.add(best[1]["osm_id"])
            c["osm_id"] = best[1]["osm_id"]
            if c.get("latitude") is None:
                c.update(latitude=best[1]["lat"], longitude=best[1]["lon"], precision="point", coord_source_url=OSM_URL.format(best[1]["osm_id"]))
            t = best[1]["tags"]
            c["phone"] = c.get("phone") or phone_of(t)
            c["website"] = c.get("website") or site_of(t)
            c["address"] = c.get("address") or address_of(t)
        if c.get("latitude") is None and c.get("locality"):
            for cand in [c["locality"].split(",")[0], *re.split(r"[ ,]+", c["locality"])]:
                k = cand.strip().lower()
                if k and k not in ("arusha", "moshi", "road", "the", "near", "of") and k in gaz:
                    lat, lon = gaz[k]
                    c.update(latitude=lat, longitude=lon, precision="locality", coord_source_url="data/reference/lead-gazetteer.txt",
                             notes=(c.get("notes", "") + f" Placed at the locality '{cand.strip()}' (offline gazetteer).").strip())
                    break
    osm_new = [o for o in osm_new if o["feature"]["osm_id"] not in consumed]

    # 3. one candidate record per organisation
    def put(rec):
        cid = rec["candidate_id"]
        if cid in candidates:
            return
        candidates[cid] = rec

    for c in curated:
        lat, lon = c.get("latitude"), c.get("longitude")
        m = matcher.match(c["name"], lat, lon, c.get("osm_id", ""), c.get("website", ""), c.get("alt_names", []), c["subsegment"] + " " + c.get("org_segment", ""))
        campus, dist = nearest(campuses, lat, lon) if lat is not None else ("", None)
        if dist is not None and dist > CATCHMENT_KM:
            continue
        status = m["status"]
        if c.get("user_named") and status != "new":
            # the user named these as missing; the coordinator checked the master. A similar name is noted, never a reason to drop.
            c["notes"] = (c.get("notes", "") + f" Similar lead in the lists: {m['lead']['name']} ({m['basis']}); checked as a different business.").strip()
            status, m = "new", {"status": "new", "lead": None, "basis": "", "score": 0.0, "saccos": m.get("saccos", "")}
        if status == "captured":
            continue
        put(record(c, m, status, campus, dist, date))

    for o in osm_new:
        f, cls = o["feature"], o["cls"]
        t = f["tags"]
        c = {"candidate_source": "openstreetmap", "name": o["name"], "alt_names": [], "segment": cls["segment"], "subsegment": cls["subsegment"],
             "org_segment": cls["org_segment"], "latitude": f["lat"], "longitude": f["lon"], "precision": "point", "coord_source_url": OSM_URL.format(f["osm_id"]),
             "locality": t.get("addr:suburb") or t.get("addr:city") or "", "address": address_of(t), "website": site_of(t), "phone": phone_of(t),
             "email": email_of(t), "google_maps_url": "", "osm_id": f["osm_id"], "osm_tags": t,
             "evidence": [{"url": OSM_URL.format(f["osm_id"]), "fetched_on": date, "fetched": True, "evidence_basis": "directory", "source_date": "",
                           "excerpt": f"OpenStreetMap {f['osm_id']}: {o['name']} (" + "; ".join(f"{k}={v}" for k, v in t.items()
                                                                                                 if k in ("amenity", "office", "shop", "tourism", "landuse", "industrial", "craft", "aeroway", "healthcare", "social_facility", "social_facility:for", "operator")) + ")"}],
             "reason": "", "verification_status": "needs_review" if o["match"]["status"] == "review" else "unverified",
             "notes": cls.get("note", ""), "search_ref": "", "raw_file": f["path"]}
        put(record(c, o["match"], o["match"]["status"], o["campus"], o["distance_km"], date))

    cands = sorted(candidates.values(), key=lambda r: (r["candidate_source"] == "openstreetmap", r["segment"], r["name"]))
    # the same organisation twice among the candidates (a curated record and an OpenStreetMap site, or two sites): keep the first, review the rest
    for i, a in enumerate(cands):
        if a["status"] != "new":
            continue
        ka = [key(n) for n in [a["name"], *a["alt_names"]]]
        for b in cands[:i]:
            if b["status"] == "dropped" or b["segment"] != a["segment"]:
                continue
            sim = max(similarity(x, key(n)) for x in ka for n in [b["name"], *b["alt_names"]])
            if sim >= 0.9:
                far = None if None in (a["latitude"], b["latitude"]) else hav(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
                if far is not None and far <= 0.3 and (sim >= 0.99 or a["candidate_source"] == "openstreetmap" and b["candidate_source"] != "openstreetmap"):
                    a["status"] = "dropped"
                    a["possible_match"] = {"db": "candidates", "id": b["candidate_id"], "name": b["name"], "basis": "mapped twice"}
                    break
                a["status"] = "review"
                a["possible_match"] = {"db": "candidates", "id": b["candidate_id"], "name": b["name"],
                                       "basis": f"same organisation as another candidate ({sim:.2f}" + (f", {far:.1f} km apart)" if far is not None else ")")
                                                + ": a second site, or a duplicate pin"}
                break
    dropped = [c for c in cands if c["status"] == "dropped"]
    cands = [c for c in cands if c["status"] != "dropped"]
    print(f"dropped {len(dropped)} features mapped twice")
    cands.sort(key=lambda r: (r["segment"], r["subsegment"], r["distance_km"] if r["distance_km"] is not None else 999, r["name"]))
    write_outputs(date, cands, census, census_all, excluded_reasons, faith, places, campuses, districts, district_council, gconf, meta, leads, gov_points)
    return 0


def record(c: dict, m: dict, status: str, campus: str, dist, date: str) -> dict:
    sub = c["subsegment"]
    if sub == "Unclassified child-focused" and status == "new":
        status = "review"  # a child-focused name of unknown kind: the welfare reviewer decides
    if c["segment"] == "employer":
        reason = (c.get("reason") or "").strip() or f"{FIT.get(sub, 'an employer with local staff').capitalize()}"
        reason += f"; {dist} km from the {CAMPUS_LABEL.get(campus, campus)} campus." if dist is not None else "; location still to place."
        reason += " A staff education benefit could reach its employees; no family facts are inferred."
    elif c["segment"] == "welfare":
        reason = (c.get("reason") or "").strip() or "A children's home, centre or child-focused programme"
        reason += f"; {dist} km from the {CAMPUS_LABEL.get(campus, campus)} campus." if dist is not None else "."
    else:
        reason = c.get("reason", "")
    missing = []
    if not c.get("phone") and not c.get("email"):
        missing.append("phone or email")
    if not c.get("address"):
        missing.append("street address")
    if not c.get("website"):
        missing.append("website")
    if c.get("latitude") is None:
        missing.append("location")
    cid = "GC_" + re.sub(r"[^a-z0-9]+", "_", key(c["name"]))[:60] + ("_" + c["osm_id"].replace("/", "") if c.get("osm_id") and c["candidate_source"] == "openstreetmap" else "")
    lead = m.get("lead") or {}
    return {
        "candidate_id": cid, "status": status, "name": c["name"], "alt_names": c.get("alt_names", []), "segment": c["segment"], "subsegment": sub,
        "org_segment": c.get("org_segment", ""), "latitude": c.get("latitude"), "longitude": c.get("longitude"), "precision": c.get("precision") or "",
        "coord_source_url": c.get("coord_source_url", ""), "campus": campus, "distance_km": dist,
        "transport_band": RC.band(dist) if dist is not None else "", "radius_tier": RC.tier(dist) if dist is not None else "",
        "locality": c.get("locality", ""), "address": c.get("address", ""), "website": c.get("website", ""), "phone": c.get("phone", ""), "email": c.get("email", ""),
        "osm_id": c.get("osm_id", ""), "google_maps_url": c.get("google_maps_url", ""), "google_maps_found": bool(c.get("google_maps_url")),
        "maps_lookup": bool(not c.get("phone") or not c.get("address")), "evidence": c["evidence"], "reason": reason,
        "verification_status": c.get("verification_status", "unverified"), "possible_match": {"db": lead.get("db", ""), "id": lead.get("id", ""), "name": lead.get("name", ""),
                                                                                                  "basis": m.get("basis", "")} if lead else None,
        "missing": missing, "notes": (c.get("notes", "") + (f" Its staff savings group is in the master ({m['saccos']})." if m.get("saccos") else "")).strip(), "candidate_source": c["candidate_source"], "search_ref": c.get("search_ref", ""), "raw_file": c.get("raw_file", ""),
        "osm_tags": c.get("osm_tags", {}),
    }


# ------------------------------------------------------------------ outputs
def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def intake_rows(cands: list[dict], date: str) -> list[dict]:
    headers = TEMPLATE.read_text(encoding="utf-8").splitlines()[0].split(",")
    extra = ["candidate_id", "subsegment", "candidate_source", "google_maps_url", "maps_lookup", "fit_reason"]
    rows = []
    for c in cands:
        if c["segment"] != "employer" or c["status"] != "new":
            continue
        ev = c["evidence"][0]
        row = {h: "" for h in headers + extra}
        email = c["email"]
        row.update({
            "record_type": "organisation", "source_path": c["raw_file"], "source_location": c["osm_id"] or c["candidate_id"], "source_url": ev["url"],
            "source_date": ev.get("source_date", ""), "acquired_on": ev.get("fetched_on") or date, "verified_on": date,
            "verification_status": c["verification_status"] if c["verification_status"] in ("verified", "needs_review", "unverified") else "unverified",
            "evidence_basis": ev["evidence_basis"], "evidence_excerpt": ev["excerpt"][:400],
            "notes": "; ".join(x for x in (c["notes"], ("Other sources: " + " | ".join(e["url"] for e in c["evidence"][1:])) if len(c["evidence"]) > 1 else "") if x),
            "organisation_name": c["name"], "organisation_domain": domain(c["website"]), "segment": c["org_segment"], "subtype": c["subsegment"],
            "campus": CAMPUS_LABEL.get(c["campus"], c["campus"]), "distance_km": "" if c["distance_km"] is None else str(c["distance_km"]),
            "radius_tier": c["radius_tier"], "geocode_precision": {"point": "rooftop", "address": "address", "locality": "locality"}.get(c["precision"], ""),
            "latitude": "" if c["latitude"] is None else f"{c['latitude']:.7f}", "longitude": "" if c["longitude"] is None else f"{c['longitude']:.7f}",
            "locality": c["locality"], "address": c["address"], "website": c["website"] if re.match(r"https?://", c["website"] or "") else "",
            "public_email": email, "public_phone": c["phone"], "osm_id": c["osm_id"], "transport_band": c["transport_band"],
            "relevance_reason": c["reason"], "acquisition_track_id": "AQ00_RESEARCH_ONLY", "review_status": "research_only",
            "missing_information": ("Find: " + ", ".join(c["missing"]) + ". ") if c["missing"] else "",
            "candidate_id": c["candidate_id"], "subsegment": c["subsegment"], "candidate_source": c["candidate_source"], "google_maps_url": c["google_maps_url"],
            "maps_lookup": "yes" if c["maps_lookup"] else "", "fit_reason": c["reason"],
        })
        row["missing_information"] += "Named decision-maker (contact round)."
        rows.append(row)
    return rows


def welfare_records(cands: list[dict], date: str) -> list[dict]:
    out = []
    for c in cands:
        # Only clear homes and centres go to the welfare run; a child-focused name of unknown kind stays a review candidate.
        if c["segment"] != "welfare" or c["status"] != "new" or c["subsegment"] == "Unclassified child-focused":
            continue
        seg, model = WELFARE_SEGMENT[c["subsegment"]]
        out.append({"record_type": "organisation", "slice": "GC", "organisation_name": c["name"], "alternative_names": [a for a in c["alt_names"] if a != c["name"]],
                    "segment": seg, "subtype": c["subsegment"], "care_model": model, "description": "", "operator_or_umbrella": "", "religious_affiliation_published": "",
                    "founded": "", "registration_published": "", "licence_claim": "", "address": c["address"], "locality": c["locality"], "ward": "", "district": "",
                    "region": "", "latitude": c["latitude"], "longitude": c["longitude"],
                    "geocode_basis": f"{c['precision']}: {c['coord_source_url']}" if c["latitude"] is not None else "", "website": c["website"],
                    "public_emails": [c["email"]] if c["email"] else [], "public_phones": [c["phone"]] if c["phone"] else [],
                    "social_media": {"facebook": "", "instagram": "", "x": "", "youtube": "", "linkedin": "", "other": ""}, "children_served_published": None,
                    "children_served_evidence": "", "children_served_as_of": "", "age_range_published": "", "gender_served": "", "services": [],
                    "schooling_arrangement_published": "", "runs_own_school": "unknown", "funding_model_published": "", "known_funders_or_partners": [],
                    "foreign_charity_registrations": [], "volunteer_programme": "unknown", "volunteer_fee_published": "", "safeguarding_policy_url": "",
                    "staff_count_published": "", "latest_activity_date": "", "latest_activity_evidence": "", "red_flags": [],
                    "catchment_note": f"{c['distance_km']} km from {CAMPUS_LABEL.get(c['campus'], c['campus'])} (gap census {date})",
                    "sources": [{"url": e["url"], "title": e["excerpt"][:120], "source_date": e.get("source_date", ""), "accessed_on": e.get("fetched_on") or date,
                                 "evidence_basis": e["evidence_basis"], "fetched": e.get("fetched", True), "facts_supported": ["name", "location"],
                                 "evidence_excerpt": " ".join(e["excerpt"].split()[:25])} for e in c["evidence"]],
                    "verification_status": "needs_review" if c["subsegment"] == "Unclassified child-focused" else ("verified" if c["verification_status"] == "verified" else "needs_review"),
                    "pdpa_risk": "low", "pdpa_risk_reason": "Organisation-level facts only.",
                    "notes": ("Gap census candidate; " + c["notes"]).strip("; ")})
    return out


def government_units(places, districts, district_council, gconf, date, leads, gov_points=()) -> list[dict]:
    gcon = ro(GOVERNMENT_DB)
    wards = [dict(r) for r in gcon.execute("SELECT name, council, latitude, longitude FROM admin_units WHERE level='ward'")]
    villages = {r["osm_id"]: r["name"] for r in gcon.execute("SELECT osm_id, name FROM organisations WHERE osm_id<>''")}
    gcon.close()
    urban = {c["name"] for c in gconf["councils"] if c.get("urban")}
    out = []
    # village and mtaa offices that OpenStreetMap maps as offices: an office point, better than a place centre
    for g in gov_points:
        if g["level"] not in ("village", "mtaa") or g["status"] != "new":
            continue
        places = list(places) + [{"lat": g["latitude"], "lon": g["longitude"], "osm_id": g["osm_id"], "name": g["unit"] or g["name"],
                                  "tags": {"place": "village" if g["level"] == "village" else "neighbourhood"}, "campus": g["campus"],
                                  "distance_km": g["distance_km"], "office": True}]
    for p in places:
        district = G.district_of(p["lat"], p["lon"], districts)
        council = district_council.get(district, "")
        if council not in PILOT_COUNCILS:
            continue
        ptype = p["tags"].get("place", "")
        same = [w["name"] for w in wards if w["council"] == council and G.squash(w["name"]) == G.squash(p["name"])]
        near = sorted((hav(p["lat"], p["lon"], w["latitude"], w["longitude"]), w["name"]) for w in wards if w["council"] == council and w["latitude"] is not None)
        ward, basis = (same[0], "the place shares the ward's name") if same else ((near[0][1], f"nearest ward reference point ({near[0][0]:.1f} km)") if near else ("", "no ward point"))
        if council in urban:
            unit = "mtaa" if ptype in ("neighbourhood", "suburb", "quarter", "village") else "kitongoji (hamlet)"
        else:
            unit = "village" if ptype == "village" else ("mtaa (township)" if ptype in ("neighbourhood", "suburb", "quarter") else "kitongoji (hamlet)")
        out.append({"record_key": f"GOFF_{unit.split()[0]}_{p['osm_id'].replace('/', '_')}", "unit_level": unit, "osm_place": ptype, "name": p["name"],
                    "location_kind": "office point" if p.get("office") else "place centre",
                    "council": council, "ward": ward, "ward_basis": basis, "ward_confirmed": False, "latitude": p["lat"], "longitude": p["lon"], "precision": "point",
                    "osm_id": p["osm_id"], "source_url": OSM_URL.format(p["osm_id"]),
                    "source_path": f"data/raw/gap-census/osm_{'offices' if p.get('office') else 'places'}_{date}.json",
                    "campus": p["campus"], "distance_km": p["distance_km"], "in_government_run": p["osm_id"] in villages,
                    # An unnamed place point (place=village and no name) cannot be addressed: listed, never proposed (fixed 11 October 2026).
                    "proposed": unit in ("village", "mtaa") and bool(str(p.get("name") or "").strip()),
                    "note": ("OpenStreetMap neighbourhood: confirm it is an official mtaa. " if unit.startswith("mtaa") else "")
                            + ("Sub-village: listed, not proposed as an office. " if unit.startswith("kitongoji") else "")
                            + ("Unnamed place point: not proposed until its name is known. " if not str(p.get("name") or "").strip() else "")})
    # one unit per council and name: an office point first, then the nearest place point of that name
    best = {}
    for u in sorted(out, key=lambda r: (r["location_kind"] != "office point", not r["proposed"], r["distance_km"] or 99)):
        best.setdefault((u["council"], G.squash(u["name"]), u["unit_level"].split()[0]), u)
    return sorted(best.values(), key=lambda r: (r["council"], r["ward"], r["name"]))


def write_outputs(date, cands, census, census_all, excluded_reasons, faith, places, campuses, districts, district_council, gconf, meta, leads, gov_points):
    RAW.mkdir(parents=True, exist_ok=True)
    write_jsonl(RAW / f"candidates_{date}.jsonl", cands)
    rows = intake_rows(cands, date)
    path = RAW / f"master_intake_{date}.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else TEMPLATE.read_text(encoding="utf-8").splitlines()[0].split(","), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    write_jsonl(RAW / f"research_GC_welfare_{date}.jsonl", welfare_records(cands, date))
    units = government_units(places, districts, district_council, gconf, date, leads, gov_points)
    (RAW / f"government_subward_units_{date}.json").write_text(json.dumps(
        {"retrieved": date, "source": f"OpenStreetMap place points (data/raw/gap-census/osm_places_{date}.json); wards from the government run's admin_units",
         "councils": PILOT_COUNCILS, "units": units}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    gov_points.sort(key=lambda r: (r["level"], r["status"], r["distance_km"] or 99, r["name"]))
    (RAW / f"government_office_points_{date}.json").write_text(json.dumps(
        {"retrieved": date, "source": f"OpenStreetMap government offices (data/raw/gap-census/osm_offices_{date}.json), including those mapped with only name:en and name:sw, "
                                      "which the government run's collector (it asks for 'name') did not read",
         "proposal": "Add the captured ward-office points to data/runs/arusha-government-2026-09/links.json osm_office_links (a ward office at a point instead of an estimate), "
                     "and the village and mtaa offices to the sub-ward units.", "offices": gov_points}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    faith.sort(key=lambda r: (CAMPUS_ORDER.index(r["campus"]), r["distance_km"], r["name"]))
    (RAW / f"faith_candidates_{date}.json").write_text(json.dumps(
        {"retrieved": date, "note": "Candidate list only: a segment the user has not set up. No drafts or plans.", "places_of_worship": faith},
        ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    report(date, cands, census, census_all, excluded_reasons, faith, units, rows, meta)


def report(date, cands, census, census_all, excluded_reasons, faith, units, intake, meta):
    L = [f"# Campus gap census — {date}", "",
         "*What OpenStreetMap and the directories record within 25 km of each campus, against what the company master, the welfare run and the government run already hold. "
         "Built by `scripts/collection/build_gap_census.py` from `data/raw/gap-census/`; nothing was written to any database.*", "",
         "## How to read it", "",
         "- **OSM**: every feature of the category within 25 km of the campus (the circles overlap: the three Arusha campuses share most features).",
         "- **Captured**: matched to a lead the lists already hold (same OpenStreetMap ID, same website, or a similar name within 0.5 km; a lead without coordinates matches on a near-exact name).",
         "- **New**: a named organisation no list holds. **Review**: a similar name nearby, or the same name elsewhere (a second site or branch).",
         "- **Excluded**: unnamed features, closed places, generic names, schools and kindergartens (competitors), single practitioners and small workshops, airstrips, industrial zones, party offices, police, courts and prisons.",
         "- Villages and neighbourhoods are counted, not matched; places of worship are a candidate list only.", ""]
    cats = [c for c in CATEGORY_ORDER]
    order = ["offices", "industrial", "farms", "health", "education", "tourism", "retail", "banks", "aviation", "worship", "social", "places"]
    L += ["## Census per campus", ""]
    for campus in CAMPUS_ORDER:
        L += [f"### {CAMPUS_LABEL[campus]}", "", "| Category | OSM | Named | Captured | New | Review | Excluded |", "|---|---:|---:|---:|---:|---:|---:|"]
        for cat in order:
            c = census[(campus, cat)]
            L.append(f"| {CATEGORY_LABEL[cat]} | {c['osm']} | {c['named']} | {c['captured']} | {c['new']} | {c['review']} | {c['excluded']} |")
        L.append("")
    L += ["### All five campuses (each feature once)", "", "| Category | OSM | Named | Captured | New | Review | Excluded |", "|---|---:|---:|---:|---:|---:|---:|"]
    for cat in order:
        c = census_all[cat]
        L.append(f"| {CATEGORY_LABEL[cat]} | {c['osm']} | {c['named']} | {c['captured']} | {c['new']} | {c['review']} | {c['excluded']} |")
    L.append("")
    # candidates by segment and subsegment per campus
    seg_rows = Counter((c["segment"], c["subsegment"], c["campus"] or "unplaced", c["status"]) for c in cands)
    L += ["## Candidates by segment and subsegment, per nearest campus", "", "New candidates (review candidates in brackets).", "",
          "| Segment | Subsegment | " + " | ".join(CAMPUS_LABEL[c] for c in CAMPUS_ORDER) + " | Unplaced | Total |", "|---|---|" + "---:|" * (len(CAMPUS_ORDER) + 2)]
    for seg, sub in sorted({(s, b) for s, b, _, _ in seg_rows}):
        cells, tn, tr = [], 0, 0
        for campus in CAMPUS_ORDER + ["unplaced"]:
            n, r = seg_rows[(seg, sub, campus, "new")], seg_rows[(seg, sub, campus, "review")]
            tn, tr = tn + n, tr + r
            cells.append(f"{n}" + (f" ({r})" if r else ""))
        L.append(f"| {seg} | {sub} | " + " | ".join(cells) + f" | {tn}" + (f" ({tr})" if tr else "") + " |")
    L.append("")
    # largest gaps
    gaps = sorted(((census_all[c]["new"], c) for c in order if c not in ("places", "worship")), reverse=True)
    L += ["## Largest gaps", ""]
    for n, cat in gaps[:6]:
        top = [c for c in cands if c["status"] == "new" and c["raw_file"].endswith(f"osm_{cat}_{date}.json")]
        L.append(f"- **{CATEGORY_LABEL[cat]}**: {n} new named features, {census_all[cat]['captured']} captured. Nearest new: "
                 + ", ".join(f"{c['name']} ({c['distance_km']} km, {CAMPUS_LABEL.get(c['campus'], c['campus'])})" for c in sorted(top, key=lambda x: x["distance_km"] or 99)[:5]) + ".")
    curated = [c for c in cands if c["candidate_source"] in ("google_maps", "targeted")]
    L += [f"- **Targeted known gaps** (official pages, the ATE employer directory, the coordinator's Google Maps pins): {sum(c['status'] == 'new' for c in curated)} new, "
          f"{sum(c['status'] == 'review' for c in curated)} to review.",
          f"- **International NGOs on the NGO register** inside the catchment and active since 2024, held by no list: {sum(c['candidate_source'] == 'ngo_register' for c in cands)}.", ""]
    L += ["## Excluded, by reason", "", "| Category | Reason | Features |", "|---|---|---:|"]
    for cat in order:
        for reason, n in excluded_reasons[cat].most_common():
            L.append(f"| {CATEGORY_LABEL[cat]} | {reason} | {n} |")
    L.append("")
    by_unit = Counter((u["council"], u["unit_level"], u["in_government_run"]) for u in units)
    L += ["## Villages and mitaa in the pilot councils", "", "| Council | Unit | From OpenStreetMap | Already in the government run |", "|---|---|---:|---:|"]
    for council in PILOT_COUNCILS:
        for unit in sorted({u for c, u, _ in by_unit if c == council}):
            L.append(f"| {council} | {unit} | {by_unit[(council, unit, False)] + by_unit[(council, unit, True)]} | {by_unit[(council, unit, True)]} |")
    L += ["", "Official totals for comparison (council websites, captured 2026-10-10): Arusha City 154 mitaa; Arusha District 67 villages and 256 vitongoji; "
          "Hai 62 villages; Meru publishes no total on its site. Ward assignment is estimated (nearest ward reference point) unless the place shares the ward's name.", ""]
    rel = Counter((f["campus"], f["religion"] or "unknown") for f in faith)
    L += ["## Places of worship (candidate list only)", "", "| Nearest campus | Christian | Muslim | Other or untagged | Total |", "|---|---:|---:|---:|---:|"]
    for campus in CAMPUS_ORDER:
        ch, mu = rel[(campus, "christian")], rel[(campus, "muslim")]
        tot = sum(v for (c, _), v in rel.items() if c == campus)
        L.append(f"| {CAMPUS_LABEL[campus]} | {ch} | {mu} | {tot - ch - mu} | {tot} |")
    L += ["", "## Proposed new employer kinds and reach weights", "",
          "`rank_employer_reach.py` scores kind of employer on a 1–4 scale (hospital or clinic 4, college 4, hotel 3, bank or other company 3, NGO 2, public body 1, safari operator 1).", "",
          "| Kind | Weight | Why |", "|---|---:|---|",
          "| International organisations | 4 | Large salaried professional workforces (UN, AU and EAC organs, ECSA-HC, ESAMI) with stable tenure; many already pay staff education allowances, so a staff education benefit is familiar. Approach through HR, like a public body, but they are not government offices. |",
          "| Manufacturing | 3 | Large permanent on-site workforces with shift supervisors and managers, like the corporate employers. |",
          "| Aviation | 3 | Salaried technical, ground and cargo staff concentrated at KIA and Arusha airport. |",
          "| Farms and estates | 2 | Large but often seasonal workforces; the benefit reaches mainly permanent and supervisory staff, and many workers live in estate villages. |",
          "| Retail | 2 | Many staff, but branch-level decisions and lower wages; the chain's head office decides. |", "",
          "## Sources and files", ""]
    for cat in order:
        m = meta.get(cat, {})
        L.append(f"- `{m.get('file', f'osm_{cat}_{date}.json (missing)')}`: {m.get('elements', 0)} features, OpenStreetMap data as of {m.get('osm_base', '')}")
    L += [f"- `data/raw/gap-census/candidates_{date}.jsonl`: {len(cands)} candidates ({sum(c['status'] == 'new' for c in cands)} new, {sum(c['status'] == 'review' for c in cands)} review)",
          f"- `data/raw/gap-census/master_intake_{date}.csv`: {len(intake)} new employers in the shared intake contract",
          f"- `data/raw/gap-census/research_GC_welfare_{date}.jsonl`, `government_subward_units_{date}.json`, `faith_candidates_{date}.json`",
          f"- `data/raw/gap-census/coverage_{date}.md`: queries, searches and blocks", "",
          "Map data © OpenStreetMap contributors, ODbL 1.0."]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / f"campus-gap-census-{date}.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"candidates": len(cands), "new": sum(c["status"] == "new" for c in cands), "review": sum(c["status"] == "review" for c in cands),
                      "intake_rows": len(intake), "faith": len(faith), "subward_units": len(units),
                      "by_segment": Counter(f"{c['segment']}|{c['subsegment']}|{c['status']}" for c in cands)}, indent=1, default=str))


if __name__ == "__main__":
    sys.exit(main())
