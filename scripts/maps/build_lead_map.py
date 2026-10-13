#!/usr/bin/env python3
"""Build the Silverleaf lead map: every lead from the three databases, placed relative to the five campuses, in one page.

Read-only on the databases. Writes outputs/maps/Silverleaf Lead Map.html, a self-contained page (MapLibre GL JS from a CDN,
everything else embedded: the leads, the campuses and an OpenStreetMap basemap from data/reference/maps/, built by
build_basemap.py). Nothing is fetched at runtime apart from the MapLibre script.

Leads and their segments follow outputs/messages/Silverleaf Core Segments - <date>.md:
- employers: the master's chosen first messages (outreach_plans selection 'Candidate for review', one per business), companies
  and savings groups; subsegments kind (build_company_audience_profile.kind_of), variant A/B, reach tier (employer_reach);
- VICOBA savings groups (decision 7 of docs/plans/vicoba-integration-plan.md): employer subsegment 'Savings groups (VICOBA)', one
  marker per ward at the government run's ward reference point (estimated), with counts by subtype and band (the exporter's
  vicoba_rows), the group names and the introducer kinds. No meeting place, officer, phone or group point; a group name that embeds
  a person's name (an honorific followed by a name, or a contact name on file) is shown as 'VICOBA group (name withheld)'. A group
  with no ward, or a ward without a reference point, is listed. The marker's confidence is its groups' best band;
- introducers: the master's introducer plans; subsegment kind (the organisation's 'Introducer: ...' segment), with the
  'VICOBA introducers' plans as 'Savings-group introducers' (their confidence from the exporter's vicoba_export);
- welfare: the welfare run's organisation plans (in scope); subsegments kind and priority;
- government: the government run's offices; subsegments office level and ward wave (distance band).
Confidence comes from scripts/messaging/export_resend_contacts.py (company_rows, welfare_rows, dedupe, government_rows), not
re-derived here: high-direct, high-indirect, medium, low, or no email (no email row: phone only or no route); government high or low.
An organisation whose inbox another lead shares is exported once by the exporter (dedupe); it is shown, with the confidence
'shared inbox', so the other levels match the exporter and the segments document.
Excluded records (master duplicates and shared-inbox records collapsed for sending, master records with no plan, and welfare
'Out of scope' entries) are a separate layer, off by default.

Location: the record's own coordinates first; then a duplicate record's coordinates; then a unique exact name match to a named
OpenStreetMap feature in the basemap; then the locality or address against the offline gazetteers (data/reference/lead-gazetteer.txt,
collect_partner_leads.js and the basemap's place names). Everything after the first two steps is marked estimated. Leads at one
spot are spread on a small spiral so each can be clicked. A lead whose own point lies in Tanzania but outside the map area (well
beyond 25 km) is drawn as a muted pin outside the catchment area: under the other pins, behind its own layer toggle, and outside the
campus filters and counts (the user's decision of 2026-10-11). Leads with no point, or only a town outside the map area, are listed.

The page carries no person's name, email address or phone number: only organisation names, roles and reasons. The script fails
if any contact name, address or number reaches the page data, and if its counts differ from the databases or the exporter.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
sys.path.insert(0, str(ROOT / "scripts" / "welfare"))
import export_resend_contacts as E  # noqa: E402  (confidence rules, dedupe)
import build_company_audience_profile as P  # noqa: E402  (kind of employer, route kind)
import welfare_lib as W  # noqa: E402  (offline gazetteer, catchment box)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE_RUN, GOVERNMENT_RUN = "arusha-welfare-2026-09", "arusha-government-2026-09"
BASEMAP = ROOT / "data" / "reference" / "maps" / "arusha-catchment-basemap.geojson"
TEMPLATE = HERE / "lead_map_template.html"
OUT = ROOT / "outputs" / "maps" / "Silverleaf Lead Map.html"
WORK = ROOT / "runtime" / "maps"
SOUTH, WEST, NORTH, EAST = -3.75, 36.30, -2.95, 37.55   # the basemap box (welfare_lib.in_catchment_box)
CAMPUS_LABEL = {"Arusha City": "Arusha City (Sakina)", "Kijenge": "Kijenge", "Ilboru": "Ilboru", "Usa River": "Usa River",
                "Boma Ngombe": "Boma Ng'ombe"}
CAMPUS_ORDER = ["Arusha City", "Kijenge", "Ilboru", "Usa River", "Boma Ngombe"]
# Places the two gazetteers miss, as build_partner_leads.py sets them (approximate, locality level).
ALIASES = {"themi": (-3.3900, 36.7000), "unga limited": (-3.3760, 36.6780), "kia": (-3.4290, 37.0745),
           "kilimanjaro international airport": (-3.4290, 37.0745), "hai": (-3.3342, 37.1383), "arumeru": (-3.3714, 36.8582)}
OUTSIDE = re.compile(r"dar es salaam|\bdsm\b|mwanza|nairobi|nanyuki|zanzibar|dodoma|tanga|iringa|morogoro|mbeya|kigoma|babati|karatu|"
                     r"mto wa mbu|monduli|loliondo|serengeti|ngorongoro|kinondoni|ilala|national", re.I)
# Roads in Arusha named after other towns ('Dodoma Road', 'Nairobi Rd') say nothing about where a lead is.
TOWN_ROADS = re.compile(r"\b(?:dodoma|nairobi|namanga|babati)\s*[-–]?\s*(?:road|rd)\b\.?", re.I)
EMAIL = re.compile(r"[^\s;,/<>()]+@[^\s;,/<>()]+\.[a-z]{2,}", re.I)
PHONE = re.compile(r"(?:\+|\b0)\d[\d\s-]{7,}\d")   # +255 ... or 07..., not ISO dates


# ------------------------------------------------------------------ helpers
def hav(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def norm(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s).replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    stop = {"the", "ltd", "limited", "co", "company", "t", "tz", "tanzania", "and", "plc", "of"}
    return " ".join(w for w in s.split() if w not in stop)


def drop_notes(text: str) -> str:
    """Without bracketed notes (nested or left open): in roles and reasons they quote the source page and can name people."""
    t = str(text or "")
    while re.search(r"\([^()]*\)", t):
        t = re.sub(r"\s*\([^()]*\)", "", t)
    t = re.sub(r"\s*[()].*?(?=;|$)", "", t)
    return " ".join(t.split()).strip(" ;,")


def red_flags(text: str) -> str:
    """The welfare run's red-flag lists, as a count: the flags themselves stay in the run database."""
    def count(m):
        try:
            n = len(json.loads(m.group(1)))
            return f"{n} red flag{'s' if n != 1 else ''} recorded in the welfare run; review them before any contact"
        except ValueError:  # the exporter cuts long held reasons at 160 characters, so the list can be open
            return "red flags recorded in the welfare run; review them before any contact"
    return re.sub(r"Review the recorded red flags before any contact:\s*(\[[^\]]*(?:\]|$))\.?", count, text, flags=re.S)


def scrub(text: str, names: list[str], notes: bool = True) -> str:
    """A reason for the page: no address, number or person's name. notes=False also drops bracketed notes."""
    t = red_flags(str(text or ""))
    t = re.sub(r"\b(inbox|address)\s+" + EMAIL.pattern, r"\1", t, flags=re.I)
    t = EMAIL.sub("the inbox", t)
    if not notes:
        t = drop_notes(t)
    t = PHONE.sub("the number", t)
    for n in names:
        if n and len(n.split()) >= 2 and n.lower() in t.lower():
            t = re.sub(re.escape(n), "the named person", t, flags=re.I)
    t = re.sub(r"held by [^;(]*\(", "held by the named holder (", t)
    t = re.sub(r"addressed to [^;]*? but ", "addressed to the named person but ", t)
    return t


def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


# ------------------------------------------------------------------ geocoding
class Locator:
    def __init__(self, basemap: dict):
        WORK.mkdir(parents=True, exist_ok=True)
        self.gaz = {k: (v[0], v[1]) for k, v in W.build_gazetteer(WORK).items()}
        for k, v in ALIASES.items():
            self.gaz.setdefault(k, v)
        self.places = {}
        pois = defaultdict(list)
        for f in basemap["features"]:
            p, g = f["properties"], f["geometry"]
            if p["layer"] == "place" and len(p["name"]) >= 4:
                self.places.setdefault(p["name"].lower(), (g["coordinates"][1], g["coordinates"][0]))
            elif p["layer"] == "poi":
                key = norm(p["name"])
                if len(key) >= 8 and len(key.split()) >= 2:
                    pois[key].append((g["coordinates"][1], g["coordinates"][0], p["kind"]))
        self.pois = {k: v[0] for k, v in pois.items() if len(v) == 1}  # a name two features share is a chain: never matched
        keys = {k: v for k, v in self.places.items()}
        keys.update(self.gaz)
        keys.pop("arusha", None)
        self.keys = sorted(keys, key=len, reverse=True)
        self.lookup = keys

    def poi(self, name: str):
        hit = self.pois.get(norm(name))
        return (hit[0], hit[1]) if hit else None

    def text(self, *values, specific_only: bool = False) -> tuple | None:
        """(lat, lon, place, precision) from a locality or address, most specific name first. A gazetteer name of three letters
        (Hai) counts; a basemap place name needs four. specific_only skips the town fallbacks (Arusha, Moshi, Usa River)."""
        raw = TOWN_ROADS.sub(" ", " ".join(str(v or "") for v in values))
        t = " " + re.sub(r"\s+", " ", re.sub(r"[^a-z' ]", " ", raw.lower().replace("-", " "))) + " "
        first = None
        for k in self.keys:
            if (len(k) >= 4 or k in self.gaz) and f" {k} " in t:
                lat, lon = self.lookup[k]
                if in_box(lat, lon):  # a place in the map area wins over a longer name elsewhere ('Njiro, Arusha' before 'Dar es Salaam')
                    return lat, lon, k.title(), "locality"
                first = first or (lat, lon, k.title(), "locality")
        if first:
            return first
        if specific_only:
            return None
        if " moshi " in t:
            return (*self.gaz["moshi"], "Moshi", "town")
        if " usa river " in t or "usariver" in t.replace(" ", ""):
            return (*self.gaz["usa river"], "Usa River", "town")
        if " arusha " in t:
            return (*self.gaz["arusha"], "Arusha city centre", "city")
        return None


def in_box(lat, lon) -> bool:
    return SOUTH <= lat <= NORTH and WEST <= lon <= EAST


def in_tanzania(lat, lon) -> bool:
    """The rough national box apply_geocodes.py also uses: a point beyond it (a funder's office abroad) is listed, not drawn."""
    return -12 < lat < -0.9 and 29 < lon < 41


# ------------------------------------------------------------------ leads
def master_leads(con, loc: Locator, today: str):
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    reach = {r["organisation_id"]: r["tier"] for r in con.execute("SELECT organisation_id, tier FROM employer_reach")}
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review'")]
    by_plan = {p["message_id"]: p for p in plans}
    rows, skipped = E.company_rows(con)
    con.row_factory = sqlite3.Row
    # Duplicate records: their coordinates can place the primary record.
    dup_of = defaultdict(list)
    for r in con.execute("SELECT entity_id, related_id, kind FROM review WHERE kind LIKE 'Duplicate organisation%' OR kind LIKE 'Shared inbox%'"):
        dup_of[r["related_id"]].append(r["entity_id"])
    return orgs, contacts, reach, plans, by_plan, rows, skipped, dup_of


CITY_UNSPECIFIED = "Arusha (city centre, unspecified)"
IN_REGION = re.compile(r"arusha|moshi|kilimanjaro|usa river|\bhai\b", re.I)


def place_master(org, orgs, dup_of, loc: Locator):
    """(lat, lon, precision, how) for a master organisation; precision exact, estimated, outside or none."""
    lat, lon = num(org.get("latitude")), num(org.get("longitude"))
    if lat is not None and lon is not None:
        prec = str(org.get("geocode_precision") or "").lower()
        if prec != "point":  # only a point is exact (13 October 2026): a geocoded street, locality, town or city is an estimate
            return lat, lon, "estimated", f"the record's own point, placed to the {prec or 'unstated precision'}"
        return lat, lon, "exact", "the record's own map point"
    for d in dup_of.get(org["organisation_id"], []):
        o = orgs.get(d) or {}
        lat, lon = num(o.get("latitude")), num(o.get("longitude"))
        if lat is not None and lon is not None:
            return lat, lon, "exact", "a duplicate record's map point"
    locality, address = org.get("locality") or "", org.get("address") or ""
    away = bool(OUTSIDE.search(locality))
    hit = loc.poi(org["name"])
    if hit and not away:
        return hit[0], hit[1], "exact", "matched by name to an OpenStreetMap feature"
    found = None
    if locality and locality != CITY_UNSPECIFIED and not away:
        found = loc.text(locality, specific_only=True)
    if not found and (not away or IN_REGION.search(address)):
        # A place in the catchment named in the address wins over an outside locality only when the address also names the region.
        found = loc.text(address, specific_only=True)
    if not found and (away or OUTSIDE.search(TOWN_ROADS.sub(" ", address))):
        return None, None, "outside", f"located outside the map area ({locality or 'address'})"
    if not found:
        found = loc.text(locality if locality != CITY_UNSPECIFIED else "", address)
    if not found and locality == CITY_UNSPECIFIED:
        found = (*loc.gaz["arusha"], "Arusha city centre", "city")
    if found:
        return found[0], found[1], "estimated", f"estimated from the {'locality' if found[3] == 'locality' else found[3]} ({found[2]})"
    return None, None, "none", "no address or locality on file"


INTRO_KIND = {"chamber": "Chambers of commerce", "employers' association": "Employers' associations", "sector association": "Sector associations",
              "hr professional body": "HR body", "other": "Other"}
VICOBA_INTRO_KIND = "Savings-group introducers"
SAVINGS_KIND = {"SACCOS members": "Savings groups (SACCOS)", "VICOBA members": "Savings groups (VICOBA)"}
VICOBA_KIND = SAVINGS_KIND["VICOBA members"]
BAND_ORDER = ("high-direct", "high-indirect", "medium", "low")  # first_touch.VICOBA_BANDS, best first
WITHHELD = "VICOBA group (name withheld)"
# A group name that embeds a person's name: an honorific followed by a name ('Mama Neema Group'), never 'Akina Mama' or 'Kina Mama'
# (women, not a person), or a contact name on file (decision 7).
HONORIFIC = re.compile(r"(?<![a-z])(?<!akina )(?<!kina )(mama|baba|mzee|bibi|bwana|babu|mwalimu|dada|kaka)\s+([a-z']{3,})", re.I)
NOT_A_NAME = {"group", "women", "wanawake", "vicoba", "vikoba", "kikundi", "savings", "club", "chama", "and", "wa", "ya", "na", "mama", "baba"}


def withhold_name(name: str, person_names) -> bool:
    """True when a VICOBA group's name embeds a person's name, so the map shows WITHHELD instead."""
    if any(m.group(2).lower() not in NOT_A_NAME for m in HONORIFIC.finditer(name or "")):
        return True
    low = " ".join(str(name or "").lower().split())
    return any(len(n.split()) >= 2 and " ".join(n.lower().split()) in low for n in person_names)


WELFARE_KIND = {"Welfare residential care": "Residential care", "Welfare family-based programme": "Family-based and sponsorship programmes",
                "Welfare specialised centre": "Specialised centres", "Welfare funder": "Funders", "Welfare network (introducer)": "Welfare networks"}


def build_leads(loc: Locator, today: str):
    leads, excluded, person_names = [], [], set()

    # --- master: employers and introducers
    m = ro(MASTER)
    campuses = [dict(r) for r in m.execute("SELECT name, latitude, longitude, geocode_basis FROM campuses")]
    orgs, contacts, reach, plans, by_plan, c_rows, c_skip, dup_of = master_leads(m, loc, today)
    for c in contacts.values():
        person_names.add(c["name"] or "")
    w = ro(ROOT / "outputs" / "runs" / WELFARE_RUN / "lead-database.sqlite")
    wplans = {r["message_id"]: dict(r) for r in w.execute(
        "SELECT p.*, o.name AS org_name, o.segment, o.priority, o.latitude, o.longitude, o.geocode_precision, o.locality, o.address "
        "FROM outreach_plans p JOIN organisations o USING(organisation_id) WHERE p.target_type='organisation'")}
    for c in w.execute("SELECT name FROM contacts"):
        person_names.add(c["name"] or "")
    w_rows, w_skip = E.welfare_rows(w)
    w.row_factory = sqlite3.Row
    kept, dropped_strings = E.dedupe(c_rows + w_rows)
    kept_ids = {id(r) for r in kept}
    kept_by_email = {r["email"].lower(): r for r in kept}
    for r in c_rows + w_rows:
        person_names.update([f"{r['first_name']} {r['last_name']}".strip(), r["escalation_recipient"] or ""])
        if r["recipient"] and "(" in r["recipient"]:
            person_names.add(r["recipient"].split("(")[0].strip())

    def conf_of(row):
        if row is None:
            return "no-email", "no email address: phone only or no route; on the call sheet"
        if id(row) not in kept_ids:
            other = kept_by_email[row["email"].lower()]
            own = row["confidence"] + (f"-{row['high_route']}" if row["confidence"] == "high" else "")
            return "shared", f"shares its inbox with {other['organisation']}, which carries the one message; on its own it would be {own.replace('-', ' ')}"
        c = row["confidence"]
        return (f"high-{row['high_route']}" if c == "high" else c), row["confidence_reason"]

    row_by_plan = {r["plan_id"]: r for r in c_rows}
    # VICOBA (export_resend_contacts.vicoba_export): groups are drawn per ward below; their introducers are introducer leads here.
    vx = E.vicoba_export(m, c_rows, w_rows, today)
    m.row_factory = sqlite3.Row
    v_row = {r["plan_id"]: r for r in vx["intro"]}
    v_shared = {r["plan_id"]: r for r in vx["dropped_rows"]}
    for p in plans:
        if p["segment"] == E.L.VICOBA_GROUP_SEGMENT:
            continue  # one marker per ward, not one per group (vicoba_ward_leads)
        org = orgs[p["organisation_id"]]
        vicoba_intro = p["segment"] == E.L.VICOBA_INTRODUCER_SEGMENT
        if vicoba_intro:
            row = v_row.get(p["message_id"])
            if p["message_id"] in v_shared:
                conf, why = "shared", ("the organisation's own company or welfare row carries the one conversation (one conversation per "
                                       "organisation); the savings-group introduction is raised there")
            elif row is not None:
                conf, why = row["confidence"], row["confidence_reason"]
            else:
                conf, why = conf_of(None)
        else:
            row = row_by_plan.get(p["message_id"])
            conf, why = conf_of(row)
        is_intro = p["segment"] == "Introducers" or vicoba_intro
        seg = "int" if is_intro else "emp"
        contact = contacts.get(p["target_id"]) if p["target_type"] == "contact" else None
        role = drop_notes((contact or {}).get("role") or p.get("recipient_role") or "") or "Named contact (role not recorded)"
        if not contact:
            role = "Organisation team (no named person)" if is_intro else "Company team (no named person)"
        if row is not None or conf == "shared":
            route = "email"
        else:
            route = {"phone only": "phone only", "email": "email", "no route yet": "none"}[P.route_kind(p)]
        if is_intro:
            kind = VICOBA_INTRO_KIND if vicoba_intro else INTRO_KIND.get((org["segment"] or "").split(":", 1)[-1].strip().lower(), "Other")
            sub = {"kind": kind}
            tier = ""
        else:
            savings = p["segment"] in E.L.SAVINGS_SEGMENTS
            kind = SAVINGS_KIND.get(p["segment"], P.kind_of(p, org)) if savings else P.kind_of(p, org)
            tier = reach.get(p["organisation_id"], "")
            sub = {"kind": kind, "variant": (p["message_variant"] if p["message_variant"] in ("A", "B") else "none"),
                   "tier": tier or "unranked"}
        lat, lon, prec, how = place_master(org, orgs, dup_of, loc)
        leads.append({"seg": seg, "name": E.L.display_name(org["name"], org["organisation_id"]), "sub": sub, "conf": conf,
                      "why": why, "names": [contact["name"]] if contact else [], "route": route, "role": role,
                      "draft": "Draft ready for review" if p["review_status"] == "Draft review" else (p["review_status"] or ""),
                      "tier": tier, "lat": lat, "lon": lon, "prec": prec, "how": how, "key": ("master", p["organisation_id"])})

    # Master records with no chosen plan: excluded layer.
    chosen = {p["organisation_id"] for p in plans}
    dup_reason = {}
    for r in m.execute("SELECT entity_id, related_id, kind FROM review WHERE kind LIKE 'Duplicate organisation%' OR kind LIKE 'Shared inbox%' "
                       "OR kind LIKE 'Branch of%'"):
        primary = orgs.get(r["related_id"]) or {}
        label = ("duplicate of" if r["kind"].startswith("Duplicate") else "branch, at another site, of" if r["kind"].startswith("Branch")
                 else "shares an inbox with")
        dup_reason.setdefault(r["entity_id"], f"{label} {E.L.display_name(primary.get('name', ''), r['related_id'])}; one message goes to that record")
    vicoba_ids = E.V.vicoba_ids(m)
    for oid, org in orgs.items():
        if oid in chosen:
            continue
        lat, lon, prec, how = place_master(org, orgs, dup_of, loc)
        shown = WITHHELD if oid in vicoba_ids and withhold_name(org["name"], person_names) else E.L.display_name(org["name"], oid)
        excluded.append({"seg": "exc", "name": shown, "src": "master",
                         "why": dup_reason.get(oid, "no first message chosen: not a lead for any segment (map record kept for reference)"),
                         "lat": lat, "lon": lon, "prec": prec, "how": how})

    # --- welfare
    row_by_wplan = {r["plan_id"]: r for r in w_rows}
    # A funder with no point near the campuses (its office is usually abroad) is shown at the home or programme it funds or runs,
    # but only where the welfare run records that relationship as verified, and the place is itself located in the map area.
    w_orgs = {r["organisation_id"]: dict(r) for r in w.execute("SELECT organisation_id, name, segment, latitude, longitude, geocode_precision, distance_km FROM organisations")}
    funded_at = {}
    for r in w.execute("SELECT from_organisation_id, to_organisation_id, relationship_type FROM organisation_relationships "
                       "WHERE verification_status='verified' AND relationship_type IN ('funds', 'operates')"):
        t = w_orgs.get(r["to_organisation_id"]) or {}
        tlat, tlon = num(t.get("latitude")), num(t.get("longitude"))
        if not t or t["segment"] in ("Welfare funder", "Out of scope") or tlat is None or not in_box(tlat, tlon):
            continue
        best = funded_at.get(r["from_organisation_id"])
        if best is None or (t["distance_km"] or 99) < (best[0]["distance_km"] or 99):
            funded_at[r["from_organisation_id"]] = (t, r["relationship_type"])
    for mid, p in wplans.items():
        row = row_by_wplan.get(mid)
        conf, why = conf_of(row)
        recipient = p["recipient"] or ""
        if "(" not in recipient or re.search(r"organisation route|\bteam\b", recipient, re.I):
            role = "Organisation team (no named person)"
        else:
            role = drop_notes(recipient.split("(", 1)[1].rsplit(")", 1)[0]) or "Named leader (role not recorded)"
        route = "email" if row is not None else ("phone only" if re.search(r"\d{6}", re.sub(r"\D", "", p["route_value"] or "")) else "none")
        lat, lon = num(p["latitude"]), num(p["longitude"])
        prec_db = p["geocode_precision"] or ""
        if p["segment"] == "Welfare funder" and (lat is None or not in_box(lat, lon)) and p["organisation_id"] in funded_at:
            t, kind = funded_at[p["organisation_id"]]
            where = "its own office has no recorded location" if lat is None else f"its own office is outside the map area ({p['locality'] or 'elsewhere'})"
            lat, lon = num(t["latitude"]), num(t["longitude"])
            prec, how = "estimated", (f"shown at {E.L.display_name(t['name'], t['organisation_id'])}, which it {'funds' if kind == 'funds' else 'runs'} "
                                      f"(a verified relationship in the welfare run); {where}")
        elif lat is None:
            prec, how = "none", ("a funder with no local point: no office location on file and no verified link to a home or programme near the campuses (most are abroad)"
                                 if p["segment"] == "Welfare funder" else "no location on file")
        elif not in_box(lat, lon):
            # Its own point outside the map area: drawn as an outside-the-catchment pin when it lies in Tanzania (see main).
            prec, how = ("exact" if prec_db == "address" else "estimated"), "the record's own point"
        else:
            prec = "exact" if prec_db == "address" else "estimated"
            how = "the record's address point" if prec == "exact" else f"estimated from the {prec_db or 'locality'}{' (' + p['locality'] + ')' if p['locality'] else ''}"
        person_names.add(recipient.split("(")[0].strip())
        leads.append({"seg": "wel", "name": E.L.display_name(p["org_name"], p["organisation_id"]),
                      "sub": {"kind": WELFARE_KIND.get(p["segment"], p["segment"]), "priority": p["priority"] or "Low"}, "conf": conf, "why": why,
                      "names": [recipient.split("(")[0].strip()], "route": route, "role": role,
                      "draft": "Draft ready for review" if p["review_status"] == "draft_ready" else "Needs review",
                      "tier": p["priority"] or "", "lat": lat, "lon": lon, "prec": prec, "how": how, "key": ("welfare", p["organisation_id"])})
    for o in w.execute("SELECT * FROM organisations WHERE segment='Out of scope'"):
        lat, lon = num(o["latitude"]), num(o["longitude"])
        ok = lat is not None and in_box(lat, lon)
        excluded.append({"seg": "exc", "name": E.L.display_name(o["name"], o["organisation_id"]), "src": "welfare",
                         "why": "welfare register entry recorded as out of scope; not written to",
                         "lat": lat if ok else None, "lon": lon if ok else None,
                         "prec": ("exact" if o["geocode_precision"] == "address" else "estimated") if ok else ("outside" if lat is not None else "none"),
                         "how": "the record's location" if ok else "no location in the map area"})

    # --- government
    g = ro(ROOT / "outputs" / "runs" / GOVERNMENT_RUN / "lead-database.sqlite")
    for r in g.execute("SELECT name FROM contacts"):
        person_names.add(r["name"] or "")
    for r in g.execute("SELECT holder_name FROM official_posts WHERE COALESCE(holder_name,'')<>''"):
        person_names.add(r["holder_name"])
    g_email, delivery = E.government_rows(g, today)
    g.row_factory = sqlite3.Row
    offices = {r["message_id"]: dict(r) for r in g.execute(
        "SELECT p.message_id, o.organisation_id, o.name, o.latitude, o.longitude, o.geocode_precision, o.locality, g.office_level "
        "FROM outreach_plans p JOIN organisations o ON o.organisation_id = p.target_id JOIN government_office_profiles g USING(organisation_id)")}
    pilots = {r["council"] for r in delivery if r["office_level"] == "council" and r["draft_status"] == "draft_ready"}
    for d in delivery:
        o = offices[d["plan_id"]]
        lat, lon = num(o["latitude"]), num(o["longitude"])
        if lat is None:
            prec, how = "none", "no location on file" + (" (ward not yet located)" if d["office_level"] in ("ward", "village") else "")
        elif not in_box(lat, lon):
            # Its own point outside the map area: drawn as an outside-the-catchment pin when it lies in Tanzania (see main).
            prec, how = ("exact" if o["geocode_precision"] == "address" else "estimated"), "the office's own point"
        else:
            prec = "exact" if o["geocode_precision"] == "address" else "estimated"
            how = "the office's address point" if prec == "exact" else "estimated (ward centre)"
        level = d["office_level"]
        band = d["wave"] if level in ("ward", "village") else "not a ward or village"
        letter_to = d["letter_to"].split(":", 1)[0]
        leads.append({"seg": "gov", "name": o["name"], "sub": {"level": level, "band": band, "pilot": "yes" if d["council"] in pilots else "no"},
                      "conf": d["confidence"], "why": d["confidence_reason"], "names": [], "route": "letter by hand" + (" (and an official inbox)" if d["official_email"] else ""),
                      "role": letter_to, "draft": ("Letter ready" if d["draft_status"] == "draft_ready" else "Held") + f"; release order {d['release_order']}",
                      "tier": d["release_order"], "council": d["council"], "lat": lat, "lon": lon, "prec": prec, "how": how,
                      "key": ("government", o["organisation_id"])})

    # --- VICOBA savings groups: one marker per ward, at the government run's ward reference point
    names = {n.strip() for n in person_names if n and len(n.strip()) >= 4}
    ward_points = {(r["council"], r["name"]): (num(r["latitude"]), num(r["longitude"])) for r in g.execute(
        "SELECT council, name, latitude, longitude FROM admin_units WHERE level='ward' AND latitude IS NOT NULL AND longitude IS NOT NULL")}
    v_leads, v_private = vicoba_ward_leads(m, vx["delivery"], ward_points, names)
    leads += v_leads
    return campuses, leads, excluded, names, {
        "c_rows": c_rows, "w_rows": w_rows, "kept": kept, "dropped": dropped_strings, "c_skip": c_skip, "w_skip": w_skip,
        "delivery": delivery, "plans": plans, "wplans": wplans, "vicoba": vx, "vicoba_private": v_private,
        "vicoba_groups": E.V.load_vicoba_groups(m)}


def vicoba_ward_leads(m, vdelivery, ward_points: dict, person_names) -> tuple[list, dict]:
    """One employer lead per ward for the VICOBA groups (decision 7): drawn at the ward reference point from the government run
    (marked estimated), with counts by subtype and band, the group names (a name that embeds a person's name withheld) and the
    introducer kinds. No meeting place, officer, phone or group point is used. A group with no ward, or a ward with no reference
    point, is listed under its council. Its confidence is the best band among the ward's groups (export_resend_contacts.vicoba_rows)."""
    groups = E.V.load_vicoba_groups(m)
    m.row_factory = sqlite3.Row
    by_ward = defaultdict(list)
    for d in vdelivery:
        by_ward[(d["council"], d["ward"])].append(d)
    leads, private = [], {"withheld": [], "places": [], "points": set()}
    for g in groups.values():
        private["places"] += [v for v in g["facts"].get("meeting_place_public", []) if v]
    for (council, ward), items in sorted(by_ward.items()):
        point = ward_points.get((council, ward)) if ward else None
        bands = Counter(d["band"] for d in items)
        best = next(b for b in BAND_ORDER if bands[b])
        shown = []
        for d in sorted(items, key=lambda d: d["release_order"]):
            if withhold_name(d["group"], person_names):
                private["withheld"].append(d["group"])
                shown.append(WITHHELD)
            else:
                shown.append(E.L.display_name(d["group"], d["organisation_id"]))
        intro = sorted({d["introducer_kind"].replace("_", " ") for d in items if d["introducer_kind"]})
        women = sum(1 for d in items if d["women_group"] == "yes")
        vg = {"n": len(items), "women": women, "subtypes": dict(Counter(d["subtype"] for d in items).most_common()),
              "bands": {b: bands[b] for b in BAND_ORDER if bands[b]}, "groups": shown, "introducers": intro or ["none linked yet"]}
        held = Counter(h.split(" (")[0] for d in items for h in d["held_because"].split("; ") if h)
        why = (f"best band among the {len(items)} group{'s' if len(items) != 1 else ''} here: {best}"
               + (f"; held because: {'; '.join(f'{h} ({n})' for h, n in held.most_common())}" if held else ""))
        place = f"{ward} ward, {council}" if ward else f"{council} (ward not recorded)"
        if point and point[0] is not None:
            private["points"].add((round(point[0], 5), round(point[1], 5)))
            how = "estimated: the ward reference point from the government run (no meeting place is shown)"
            lat, lon = point
        else:
            lat = lon = None
            how = "no ward recorded: the group is listed under its council" if not ward else "the ward has no reference point yet"
        ready = sum(1 for d in items if d["draft_status"] == "Draft review")
        leads.append({"seg": "emp", "name": f"VICOBA groups: {place}", "sub": {"kind": VICOBA_KIND, "variant": "none", "tier": "unranked"},
                      "conf": best, "why": why, "names": [], "route": "through an introducer (a group has no route of its own)",
                      "role": "The group's committee", "draft": f"Kiswahili drafts: {ready} of {len(items)} ready for review",
                      "tier": "", "lat": lat, "lon": lon, "prec": "estimated" if lat is not None else "none", "how": how,
                      "key": ("vicoba", f"{council}|{ward}"), "vg": vg})
    return leads, private


def location_checks() -> dict:
    """Why a lead is still unplaced after the location research (data/raw/geocode-research/geocodes_*.jsonl): the reason
    only, never the address text."""
    out = {}
    for path in sorted((ROOT / "data" / "raw" / "geocode-research").glob("geocodes_*.jsonl")):
        day = path.stem.split("_")[-1]
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line) if line.strip() else {}
            if r.get("status") == "outside_confirmed":
                out[(r["db"], r["organisation_id"])] = f"located outside the map area (checked {day}: no office found near the campuses)"
            elif r.get("status") == "not_found":
                out[(r["db"], r["organisation_id"])] = f"no location found yet (checked {day}; listed for a map lookup)"
    return out


# ------------------------------------------------------------------ geometry
def spread(items: list[dict]) -> None:
    """Leads that share a spot are laid on a sunflower spiral around it, so each can be clicked; the spot stays the centre."""
    groups = defaultdict(list)
    for it in items:
        if it["lat"] is not None:
            groups[(round(it["lat"], 4), round(it["lon"], 4))].append(it)
    golden = math.pi * (3 - math.sqrt(5))
    for (lat, lon), group in groups.items():
        if len(group) < 2:
            continue
        step_m = 20 if all(it["prec"] == "exact" for it in group) else (110 if len(group) > 40 else 80)
        group.sort(key=lambda it: (it["seg"], it["name"].lower()))
        for i, it in enumerate(group):
            r = step_m * math.sqrt(i + 0.5)
            a = i * golden
            it["lat"] = lat + (r * math.cos(a)) / 111_320
            it["lon"] = lon + (r * math.sin(a)) / (111_320 * math.cos(math.radians(lat)))
            it["spread"] = len(group)


def nearest(campuses, lat, lon):
    best = min(campuses, key=lambda c: hav(lat, lon, c["lat"], c["lon"]))
    return best["key"], round(hav(lat, lon, best["lat"], best["lon"]), 1)


# ------------------------------------------------------------------ checks
def verify(leads, extra, campuses_doc_ok: bool) -> list[str]:
    errors = []
    kept, c_rows, w_rows = extra["kept"], extra["c_rows"], extra["w_rows"]
    plans = extra["plans"]
    vx, vgroups = extra["vicoba"], extra["vicoba_groups"]
    intro_segments = {"Introducers", E.L.VICOBA_INTRODUCER_SEGMENT}
    # VICOBA groups are one marker per ward (council and ward as the groups' facts give them), not one lead per plan.
    wards = {(E._fact(g, "council"), E._fact(g, "ward")) for g in vgroups.values()}
    exp = {"emp": sum(1 for p in plans if p["segment"] not in intro_segments | {E.L.VICOBA_GROUP_SEGMENT}) + len(wards),
           "int": sum(1 for p in plans if p["segment"] in intro_segments), "wel": len(extra["wplans"]), "gov": len(extra["delivery"])}
    got = Counter(l["seg"] for l in leads)
    for seg, n in exp.items():
        if got[seg] != n:
            errors.append(f"{seg}: {got[seg]} leads on the page, {n} in the database")
    track = {"companies": "emp", "introducers": "int", "welfare": "wel", E.VICOBA_INTRODUCER_TRACK: "int"}
    want = Counter()
    for r in kept + vx["intro"]:
        want[(track[r["track"]], f"high-{r['high_route']}" if r["confidence"] == "high" else r["confidence"])] += 1
    kept_ids = {id(r) for r in kept}
    for r in c_rows + w_rows:
        if id(r) not in kept_ids:
            want[(track[r["track"]], "shared")] += 1
    want[("int", "shared")] += len(vx["dropped_rows"])
    for k, n in list(extra["c_skip"].items()) + list(vx["skipped"].items()):
        want[("emp", "no-email")] += n  # company_rows counts introducers without email under the same key
    want[("wel", "no-email")] += sum(extra["w_skip"].values())
    # VICOBA ward markers: every group in exactly one marker, the band counts equal to the exporter's, the marker's confidence its
    # groups' best band, and the marker at a ward reference point (or not drawn).
    markers = [l for l in leads if l.get("vg")]
    if sum(l["vg"]["n"] for l in markers) != len(vgroups) or len(vx["delivery"]) != len(vgroups):
        errors.append(f"VICOBA: {sum(l['vg']['n'] for l in markers)} groups on the page, {len(vgroups)} in the master, "
                      f"{len(vx['delivery'])} from the exporter")
    page_bands = Counter()
    for l in markers:
        page_bands.update(l["vg"]["bands"])
        if l["conf"] != next(b for b in BAND_ORDER if l["vg"]["bands"].get(b)):
            errors.append(f"VICOBA {l['name']}: marker confidence {l['conf']} is not its groups' best band")
        if l["lat"] is not None and (round(l["lat"], 5), round(l["lon"], 5)) not in extra["vicoba_private"]["points"]:
            errors.append(f"VICOBA {l['name']}: drawn away from a ward reference point")
    if page_bands != Counter(d["band"] for d in vx["delivery"]):
        errors.append(f"VICOBA bands {dict(page_bands)} on the page, {dict(Counter(d['band'] for d in vx['delivery']))} from the exporter")
    if vx["errors"]:
        errors += [f"VICOBA exporter: {e}" for e in vx["errors"]]
    have = Counter((l["seg"], l["conf"]) for l in leads if l["seg"] != "gov" and not l.get("vg"))
    no_email_emp_int = have[("emp", "no-email")] + have[("int", "no-email")]
    if no_email_emp_int != want[("emp", "no-email")]:
        errors.append(f"employers and introducers without email: {no_email_emp_int} on the page, {want[('emp', 'no-email')]} skipped by the exporter")
    for key, n in want.items():
        if key[1] == "no-email" and key[0] == "emp":
            continue
        if have[key] != n:
            errors.append(f"{key[0]} {key[1]}: {have[key]} on the page, {n} from the exporter")
    for key, n in have.items():
        if key not in want and not (key[1] == "no-email" and key[0] in ("emp", "int")):
            errors.append(f"{key[0]} {key[1]}: {n} on the page, none from the exporter")
    gov_want = Counter(d["confidence"] for d in extra["delivery"])
    gov_have = Counter(l["conf"] for l in leads if l["seg"] == "gov")
    if gov_want != gov_have:
        errors.append(f"government confidence {dict(gov_have)} on the page, {dict(gov_want)} from the exporter")
    if not campuses_doc_ok:
        errors.append("campus names differ from the segments document")
    return errors


def privacy_check(payload: dict, person_names: set, vicoba_private: dict | None = None) -> list[str]:
    """No email address, phone number or contact name in any field the page shows apart from organisation names. For VICOBA
    (decision 7): no meeting place, and no group name that embeds a person's name (it is shown as WITHHELD)."""
    problems = []
    blob = json.dumps(payload["leads"] + payload["excluded"] + payload["unmapped"], ensure_ascii=False)
    low_blob = blob.lower()
    for place in set((vicoba_private or {}).get("places", [])):
        if len(place) >= 10 and json.dumps(place, ensure_ascii=False)[1:-1].lower() in low_blob:
            problems.append(f"VICOBA meeting place in the page data: {place[:40]}")
    for name in set((vicoba_private or {}).get("withheld", [])):
        if json.dumps(name, ensure_ascii=False)[1:-1].lower() in low_blob:
            problems.append(f"withheld VICOBA group name in the page data: {name}")
    for item in payload["leads"] + payload["unmapped"]:
        for shown in (item.get("g") or {}).get("groups", []):
            if shown != WITHHELD and withhold_name(shown, person_names):
                problems.append(f"VICOBA group name that embeds a person's name in the page data: {shown}")
    for e in set(EMAIL.findall(blob)):
        problems.append(f"email address in the page data: {e}")
    for ph in set(PHONE.findall(blob)):
        if len(re.sub(r"\D", "", ph)) >= 9:
            problems.append(f"phone-like number in the page data: {ph}")
    fields = " \n ".join(" | ".join(str(v) for k, v in item.items() if k not in ("n",)) for item in payload["leads"] + payload["excluded"])
    low = fields.lower()
    org_names = " \n ".join(i["n"] for i in payload["leads"] + payload["excluded"] + payload["unmapped"]).lower()
    for name in person_names:
        n = " ".join(name.split()).lower()
        words = [x for x in re.findall(r"[a-z]{3,}", n) if not E.TITLE.match(x)]
        if len(words) < 2 or n in org_names:
            continue
        if n in low:
            problems.append(f"contact name in the page data: {name}")
    return problems


# ------------------------------------------------------------------ main
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--basemap", type=Path, default=BASEMAP)
    args = parser.parse_args()
    today = date.today().isoformat()
    if not args.basemap.exists():
        raise SystemExit(f"Missing {args.basemap}. Build it first: python scripts/maps/build_basemap.py")
    basemap = json.loads(args.basemap.read_text(encoding="utf-8"))
    loc = Locator(basemap)
    campuses_raw, leads, excluded, person_names, extra = build_leads(loc, today)

    # Campuses: the master's coordinates, named as in the segments document.
    campuses = []
    for c in campuses_raw:
        key = E.L.campus_key(c["name"]) or c["name"]
        basis = " ".join(str(c["geocode_basis"] or "").split())
        source = ("Map pin from the campus page on silverleaf.co.tz" if "silverleaf.co.tz" in basis.lower()
                  else f"Approximate point: {basis}" if basis else "Source of the point not recorded")
        campuses.append({"key": key, "label": CAMPUS_LABEL.get(key, c["name"]), "lat": float(c["latitude"]), "lon": float(c["longitude"]),
                         "source": source, "pin": "silverleaf.co.tz" in basis.lower(),
                         "url": (re.findall(r"https://www\.silverleaf\.co\.tz/[^\s);,]+", basis) or [""])[0]})
    campuses.sort(key=lambda c: CAMPUS_ORDER.index(c["key"]) if c["key"] in CAMPUS_ORDER else 99)
    # The five campuses, under the names the outreach uses (offer_lib.campus_key and CAMPUS_LABEL). The segments document of
    # 2026-10-11 does not list the campuses by name, so the check is on the master's campuses table.
    names_ok = len(campuses) == 5 and {c["key"] for c in campuses} == set(CAMPUS_ORDER)

    errors = verify(leads, extra, names_ok)

    mapped = [l for l in leads if l["lat"] is not None]
    for l in leads + excluded:
        if l["lat"] is not None and not in_box(l["lat"], l["lon"]):
            # A lead whose own point lies outside the map area (every such point is well beyond 25 km of a campus) is still
            # drawn, as a muted pin outside the catchment area, ranked under the others and kept out of the campus counts (the
            # user's decision of 2026-10-11, for African Galleria at Karatu). The online views show its surroundings; the
            # offline basemap covers only the catchment. A point outside Tanzania, or an excluded record, is listed instead.
            camp, km = nearest(campuses, l["lat"], l["lon"])
            if l["seg"] != "exc" and in_tanzania(l["lat"], l["lon"]):
                l["outside"] = True
                l["how"] = (f"{l['how']}, outside the catchment area: {km:g} km from the nearest campus ({CAMPUS_LABEL.get(camp, camp)}); "
                            "deprioritised for the distance")
            else:
                l["prec"], l["how"], l["lat"], l["lon"] = "outside", "located outside the map area", None, None
    spread([l for l in leads + excluded if l["lat"] is not None])
    seg_code = {"emp": 0, "int": 1, "wel": 2, "gov": 3}
    checked = location_checks()
    out_leads, unmapped = [], []
    by_length = sorted(person_names, key=len, reverse=True)
    for i, l in enumerate(sorted(leads, key=lambda l: (seg_code[l["seg"]], l["name"].lower()))):
        why = scrub(l["why"], l["names"] + by_length, notes=l["seg"] == "gov")
        rec = {"n": l["name"], "s": l["seg"], "c": l["conf"], "y": why, "r": l["route"], "o": scrub(l["role"], []), "d": l["draft"],
               "u": l["sub"], "h": l["how"]}
        if l["seg"] == "gov":
            rec["k"] = l.get("council", "")
        if l.get("vg"):
            rec["g"] = l["vg"]  # VICOBA ward marker: group counts, names (some withheld) and introducer kinds
        if l["lat"] is None:
            why = checked.get(l.get("key"), l["how"])
            if l.get("vg"):
                why = f"{l['how']}; {l['vg']['n']} group{'s' if l['vg']['n'] != 1 else ''}: {', '.join(l['vg']['groups'])}"
            unmapped.append({"n": l["name"], "s": l["seg"], "c": l["conf"], "why": why})
            continue
        camp, km = nearest(campuses, l["lat"], l["lon"])
        rec.update({"la": round(l["lat"], 5), "lo": round(l["lon"], 5), "e": 0 if l["prec"] == "exact" else 1, "cp": camp, "km": km,
                    "sp": l.get("spread", 0)})
        if l.get("outside"):
            rec["x"] = 1  # outside the catchment area: drawn muted, under the others, and left out of the campus counts
        out_leads.append(rec)
    out_excluded = []
    for x in excluded:
        if x["lat"] is None:
            continue
        camp, km = nearest(campuses, x["lat"], x["lon"])
        out_excluded.append({"n": x["name"], "s": "exc", "y": scrub(x["why"], []), "h": x["how"], "src": x["src"], "la": round(x["lat"], 5),
                             "lo": round(x["lon"], 5), "e": 0 if x["prec"] == "exact" else 1, "cp": camp, "km": km})
    # Labels stay out of the drawn basemap's points of interest (used for matching only).
    drawn = {"type": "FeatureCollection", "features": [f for f in basemap["features"] if f["properties"]["layer"] != "poi"]}
    # The pannable area: the basemap box widened to every drawn pin (leads outside the catchment area included).
    extent = [min([WEST] + [l["lo"] for l in out_leads]), min([SOUTH] + [l["la"] for l in out_leads]),
              max([EAST] + [l["lo"] for l in out_leads]), max([NORTH] + [l["la"] for l in out_leads])]
    payload = {"built": today, "campuses": campuses, "leads": out_leads, "excluded": out_excluded, "unmapped": unmapped,
               "excludedTotal": len(excluded), "attribution": basemap.get("attribution", ""), "bbox": [WEST, SOUTH, EAST, NORTH],
               "extent": extent}
    errors += privacy_check(payload, person_names, extra["vicoba_private"])

    # Summary.
    seg_name = {"emp": "Employers", "int": "Introducers", "wel": "Welfare", "gov": "Government"}
    print(f"Silverleaf lead map, {today}")
    print(f"{'Segment':<12} {'leads':>6} {'mapped':>7} {'exact':>6} {'estim.':>7} {'outside':>8} {'unmapped':>9}")
    for s in ("emp", "int", "wel", "gov"):
        tot = sum(1 for l in leads if l["seg"] == s)
        mp = [l for l in out_leads if l["s"] == s]
        print(f"{seg_name[s]:<12} {tot:>6} {len(mp):>7} {sum(1 for l in mp if not l['e']):>6} {sum(1 for l in mp if l['e']):>7} "
              f"{sum(1 for l in mp if l.get('x')):>8} {tot - len(mp):>9}")
    print("  (outside: drawn pins outside the catchment area, beyond the map's basemap; included in mapped)")
    print("\nConfidence (all leads, mapped or not):")
    for s in ("emp", "int", "wel", "gov"):
        cnt = Counter(l["conf"] for l in leads if l["seg"] == s)
        print(f"  {seg_name[s]:<12} " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    vmark = [l for l in leads if l.get("vg")]
    vb = Counter()
    for l in vmark:
        vb.update(l["vg"]["bands"])
    print(f"\nVICOBA: {sum(l['vg']['n'] for l in vmark)} groups in {len(vmark)} ward markers "
          f"({sum(1 for l in vmark if l['lat'] is not None)} drawn); bands " + ", ".join(f"{b} {vb[b]}" for b in BAND_ORDER)
          + f"; names withheld {len(extra['vicoba_private']['withheld'])}")
    print("\nUnmapped, by reason:")
    reasons = Counter((u["s"], re.sub(r"\s*\(.*\)$", "", u["why"])) for u in unmapped)
    for (s, why), n in sorted(reasons.items()):
        print(f"  {seg_name[s]:<12} {n:>4}  {why}")
    print(f"\nExcluded layer: {len(out_excluded)} drawn of {len(excluded)} excluded records "
          f"({sum(1 for x in excluded if x['src'] == 'master')} master duplicates or records without a plan, "
          f"{sum(1 for x in excluded if x['src'] == 'welfare')} welfare out of scope)")

    if errors:
        print("\nCHECKS FAILED:")
        for e in errors:
            print("  - " + e)
        return 1

    html = TEMPLATE.read_text(encoding="utf-8")
    data_js = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    base_js = json.dumps(drawn, ensure_ascii=True, separators=(",", ":"))
    html = html.replace("/*__DATA__*/null", data_js.replace("</", "<\\/")).replace("/*__BASEMAP__*/null", base_js.replace("</", "<\\/"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    size = args.out.stat().st_size
    print(f"\nChecks passed: counts match the databases and the exporter; no contact name, email address or phone number in the page.")
    print(f"Wrote {args.out.relative_to(ROOT) if args.out.is_relative_to(ROOT) else args.out}: {size / 1e6:.2f} MB "
          f"(leads {len(data_js) / 1e6:.2f} MB, basemap {len(base_js) / 1e6:.2f} MB)")
    if size > 10e6:
        print("ERROR: the page is over 10 MB")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
