#!/usr/bin/env python3
"""Turn one Google Maps lookup round into its lookup record, geocode fills and geocode corrections, with the shared-pin check.

A round is the coordinator's browser lookups for a slice of the worklist (collect_geocodes.py worklist, or
runtime/geocode/gmaps_worklist_<date>.jsonl). Only the coordinator looks up, in its own browser pane, and the pane must be
visible: Google Maps does not finish rendering results in a hidden pane, and the extractor then records nothing.

  python scripts/maps/build_gmaps_round.py --date 2026-10-13 --tag c \
      --rows <rows.json|.jsonl> --results <results.json> --notes <notes.txt> --db <master.sqlite> [--no-pin-check] [--out-root <dir>]
  python scripts/maps/build_gmaps_round.py --audit data/raw/gap-census/google_maps_enrich_<d><tag>.jsonl ...   # check only, writes nothing
  python scripts/maps/build_gmaps_round.py --retro data/raw/gap-census/google_maps_enrich_*.jsonl --db <master copy>  # precedence, report only

Inputs:
- --rows: the round's worklist rows (a JSON array, or JSON lines), each with id, name, segment and query. Only rows with a
  verdict note are built; every note must name a row.
- --results: the browser results, {organisation_id: [listing, ...]} with the top listing first. Each listing is
  {n: name, la: latitude, lo: longitude, c: category, a: address, i: listing id or blank, w: website, p: phone, u: Maps URL}.
  This is the export of localStorage.slres from the browser extractor (below).
- --notes: one verdict per line: 'A <id>' accept, 'R <id>[|note]' reject, 'V <id>|note' review, 'O <id>|note' accept as
  outside the catchment (the note is the basis). A reject without a note gets "Top listing '<n>' is not this organisation."
  An optional '#n' after the ID picks the listing explicitly, counting from 0 in the results list: 'A O19f15b52b37e#1|note'
  accepts the second result (this replaces the separate pick file of round 4). Without '#n' the first result is the pick.

Multi-hit matching (the user's rule of 13 October 2026: an organisation can have two or three offices). For an accepted lead,
every listing in its results whose name matches the lead's name or the picked listing's name (significant words, ignoring
words such as Ltd, Safaris, Tours, Tanzania, Bank or Branch) is a candidate:
- a lead with a stored point (any source): a candidate within the agreement distance is the match (the nearest one); the
  status is listed, "confirmed at stored point", and the stored point follows the precedence below. The other candidates are
  recorded as other offices (facts other_office: name, point, URL, distance). When no candidate is within the distance, the
  lead is a discrepancy listing every candidate with its distance, whatever the stored point's rank;
- a lead with no stored point and several candidates: accepted only when exactly one candidate lies in the record's
  locality (its locality words appear in the listing's address or name), or when the notes pick one with '#n'. A chain
  (a bank, insurer, microfinance, pharmacy, fuel station, mobile network or a 'branch') is accepted only when exactly one
  candidate's address shares a street word with the record's address. Otherwise the verdict becomes review, with every
  candidate listed in the line's candidates field and the note.
A lead with one candidate is built exactly as before.

The welfare and government runs (13 October 2026). A worklist row whose db is welfare or government names the run's organisation
ID (ORG_...). The run's database (outputs/runs/<run>/lead-database.sqlite, read-only; --welfare-db, --government-db) gives the
name, the stored point and its precision; the run's links.json gives its reviewed overrides. The run lines take the key that
apply_geocodes.py defines: welfare, the organisation name (links.json geo_overrides); government, 'Council|Ward' for a ward office
(ward_locations) or the office record key (office_locations). The enrich line carries db for a run lead (a master line has none).
- Stored point and its rank: a reviewed override ranks by its source_type (own site embed or official site 1, Google Maps 2,
  OpenStreetMap 3); without one, welfare 'address' is the run's point (OpenStreetMap when the record has an osm_id, else a
  research or register point, kept like a Google point), and 'estimated' and 'locality' are estimates; government ranks by the
  record's location_source ('official website map' 1, a reviewed Google point 2, an OpenStreetMap office 3) and every
  'estimated' ward or village reference point is an estimate.
- The same precedence, agreement distance, multi-hit matching and shared-pin check as the master.
- A run is never corrected with --replace (master only). A run correction is an override: when the listing replaces a lower-
  ranked point, the line goes to the round's fills file (geocodes_gmaps_<date><tag>.jsonl) with the run's db and key, and
  apply_geocodes.py (its default path, preview then --apply) adds the override to the run's links.json; the run's rebuild then
  uses it instead of its own point. A lead that already has a reviewed override is never overwritten: within the agreement
  distance the override is kept and the listing corroborates it; beyond it the lead is a discrepancy. The enrich line carries the extra fields candidates and match only
when there were several candidates, so a round with single results is unchanged.
- --db: the master as it was before the round (the pre-round backup), read-only. A lead with no stored point gets a fill; a
  lead with a stored point is decided by the location precedence below.

Outputs (the formats of the 13 October 2026 rounds), under --out-root (default: the repository):
- data/raw/gap-census/google_maps_enrich_<date><tag>.jsonl                one line per lead: verdict, top listing, note;
- data/raw/geocode-research/geocodes_gmaps_<date><tag>.jsonl             the fills (accepted, no stored point; or 'O');
- data/raw/geocode-research/geocodes_corrections_gmaps_<date><tag>.jsonl the replacements (old_* fields, km_moved);
- data/raw/geocode-research/location_checks_gmaps_<date><tag>.jsonl      one line per accepted listing whose lead already had a
  point: the outcome (replaced, corroborates, discrepancy), both points, both sources and the distance;
- data/raw/geocode-research/location_discrepancies_<date>.jsonl          the discrepancies of every round of that date (this
  round's lines are replaced, other rounds' kept);
- runtime/geocode/gmaps_round_<date><tag>_check.json                     the shared-pin check and the distance distribution.
Then: ledger.py ingest the enrich file; apply_geocodes.py (preview, then --apply) for the fills and with --replace for the
corrections; scripts/maps/apply_gmaps_status.py --round <date><tag> (preview, then --apply) for the Google Maps status of every
lead, the corroborations and the discrepancy review items.

Location precedence (the user's rule of 13 October 2026), for an accepted listing whose lead already has a stored point:
- Coordinates found another way are never lost: a lead Google Maps does not list keeps its point (status not_found).
- Source rank: 1 the organisation's own website pin (own site embed, JSON-LD or plus code on its site; official site);
  2 a Google Maps listing; 3 an OpenStreetMap feature at point precision; 4 an estimate (own-site text placed with the gazetteer,
  Nominatim, the NGO register, the offline gazetteer, a shared site, an OpenStreetMap address, a town centroid, no source).
- Within the agreement distance (--agreement-m, default 500 m): the higher-ranked point is kept. A website pin or an earlier
  Google listing stays and the new listing is recorded as a corroborating fact with the distance (outcome corroborates). An
  OpenStreetMap point or an estimate is replaced by the listing (a correction line; an OpenStreetMap point's line carries
  rank_replace and agreement_m, which apply_geocodes.py --replace checks).
- Beyond it: no correction. The lead goes to the discrepancies file with both points, both sources and the distance, and
  apply_gmaps_status.py adds the review item "Location discrepancy: <source> vs Google Maps"; the user and the orchestrator
  decide. This includes an estimate from the organisation's own website text. Any other estimate (a centroid or a geocoded
  text) is replaced at any distance, as before, unless --estimates-beyond discrepancy.
- --no-precedence builds the corrections as the rounds of 13 October 2026 were built (every stored point replaced), to
  reproduce those files.
--retro <enrich files> --db <master copy> runs the precedence over committed rounds against the master as it is now (an applied
listing is compared with the superseded_location it replaced) and writes only runtime/geocode/gmaps_retro_<today>.json and
gmaps_retro_discrepancies_<today>.jsonl (for apply_gmaps_status.py --discrepancies, once the orchestrator has reviewed it).

The shared-pin check (default; docs/methodology/research-playbook.md, "Google Maps traps"):
- Every listing of this round and of every other google_maps_enrich_*.jsonl file is grouped by its point rounded to 4 decimals.
- An accepted listing whose point is shared with a differently named listing, and which has no street address (empty, a plus
  code, or only Arusha, Tanzania, a postcode or a ward or place name), is downgraded to review with the reason.
- Two listings that share a point and both have a street address are likely one building: kept, and reported.
- An accepted listing on a known default pin (the playbook's list, Tanzania's country centre included), or within 60 m of one,
  is downgraded to review.
- Rows with an 'O' verdict (accepted as outside the catchment) are not checked.
Every downgrade is printed and written to the check report. When a person has looked at a flagged listing and keeps it (the
listing is the lead's own, and the stray listing is the other one), pass --keep <id>: it stays accepted and the report says so.

The browser extractor. Two functions kept in the browser's localStorage, run on a Maps search page with
eval(localStorage.slfn)("<organisation_id>") (read the results now) or eval(localStorage.slsync)("<organisation_id>") (wait
for the result list to settle, then read). Each reads the result list, or the single place panel when Maps opens one, and
stores the listings under the ID in localStorage.slres as JSON: {"<id>": [{n, la, lo, c, a, i, w, p, u}, ...]}, top first;
la and lo come from the listing URL's !3d<lat>!4d<lon>. Export with JSON.stringify(JSON.parse(localStorage.slres)) and save it
as the --results file. Each lookup is a navigate to https://www.google.com/maps/search/<query>/@<lat>,<lon>,11z?hl=en (the
area's centre: -3.37,36.69 for Arusha, -3.33,37.20 for Moshi and Hai), a few seconds' wait, then the call. Lookups run signed
out; never pass a bot check or sign in on the user's behalf.

Up to 5 results (requested 13 October 2026). Today both functions keep the top 3 results of the feed; multi-hit matching needs up
to 5, because an organisation can have two or three offices and the right one may rank fourth or fifth. The functions live only
in the coordinator's browser (their source is not in the repository), so make this change there, in both slfn and slsync:
  the limit on the feed's result links, .slice(0, 3)  ->  .slice(0, 5)
  (or, if the function counts in a loop, i < 3  ->  i < 5)
Check it after saving: localStorage.slfn.includes("slice(0, 5)") (or the loop bound) and the same for slsync. The
single place panel (Maps opening one listing directly) still yields one listing. The results format is unchanged: a list of up to
5 listings per ID, top first. Then save both functions in scripts/maps/gmaps_extractor.js, so the extractor is versioned.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENRICH_DIR = ROOT / "data" / "raw" / "gap-census"
GEO_DIR = ROOT / "data" / "raw" / "geocode-research"
VERDICTS = {"A": "accept", "O": "accept", "V": "review", "R": "reject"}
# Known default pins (docs/methodology/research-playbook.md, "Google Maps traps"), and Tanzania's country centre.
DEFAULT_PINS = [("JM7M+65, central Arusha", -3.38689, 36.68296), ("the Namanga road point", -3.35877, 36.66606),
                ("the Sokoine road point", -3.39814, 36.67721), ("the Ngorongoro point", -3.36392, 35.38430),
                ("Tanzania's country centre", -6.37283, 34.98990)]
DEFAULT_RADIUS_KM = 0.06
PLUS_CODE = re.compile(r"\b[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3}\b", re.I)
PLACE_ONLY = re.compile(r"^(arusha|tanzania|united republic of tanzania|moshi|kilimanjaro|usa river|arumeru|meru|\d{4,6})$", re.I)
STREET = re.compile(r"\b(road|rd|street|st|avenue|ave|highway|hwy|lane|drive|way|house|building|bldg|complex|plaza|tower|floor|room|"
                    r"cent(?:re|er)|mall|block|plot|hotel|lodge|opposite|opp|near|along|junction|market|barabara|mtaa)\b", re.I)


def km(a, b, c, d) -> float:
    a, b, c, d = map(math.radians, (a, b, c, d))
    h = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return round(2 * 6371 * math.asin(math.sqrt(h)), 1)


def name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def street_address(address: str) -> bool:
    """A real street address: something beyond a plus code, a postcode and place names (a ward or town alone does not count)."""
    text = PLUS_CODE.sub(" ", address or "")
    parts = [p.strip(" .") for p in text.split(",") if p.strip(" .")]
    parts = [p for p in parts if not PLACE_ONLY.match(p)]
    return any(STREET.search(p) or re.search(r"\d", p) for p in parts)


NAME_NOISE = {"ltd", "limited", "co", "company", "tz", "t", "inc", "the", "and", "of", "safari", "safaris", "tour", "tours", "travel",
              "travels", "expedition", "expeditions", "adventure", "adventures", "holiday", "holidays", "arusha", "moshi", "tanzania", "africa",
              "african", "group", "plc", "bank", "branch", "office", "offices", "investment", "investments", "enterprise", "enterprises",
              "services", "solutions", "international", "trekking", "treks", "agency", "agencies", "transport", "east", "head", "hq"}
CHAIN = re.compile(r"\b(bank|insurance|assurance|microfinance|micro finance|pharmac\w*|supermarket|fuel|petrol|filling station|vodacom|airtel|"
                   r"tigo|halotel|branch|nmb|crdb|nbc|exim|stanbic|absa|equity|dtb|azania|akiba|amana|kcb|ecobank)\b", re.I)
PLACE_NOISE = {"tanzania", "city", "centre", "center", "unspecified", "region", "district", "town", "ward", "road", "street", "p.o.", "box"}


def name_words(name: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", (name or "").lower()) if w not in NAME_NOISE and len(w) > 1}


def same_business(a: str, b: str) -> bool:
    """The two names name the same business: one's significant words contain the other's (Kitulano Investment / Kitulano
    tours; NBC Moshi / NBC Bank Moshi), or the normalised names are equal when either has no significant word."""
    wa, wb = name_words(a), name_words(b)
    if not wa or not wb:
        return bool(name_key(a)) and name_key(a) == name_key(b)
    return wa <= wb or wb <= wa


def place_words(text: str) -> set[str]:
    text = re.sub(r"\([^)]*\)", " ", text or "")
    return {w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in PLACE_NOISE}


def in_locality(row: dict, listing: dict) -> bool:
    words = place_words(row.get("locality", ""))
    hay = f"{listing.get('a') or ''} {listing.get('n') or ''}".lower()
    return bool(words) and any(w in hay for w in words)


def at_address(row: dict, listing: dict) -> bool:
    words = place_words(PLUS_CODE.sub(" ", row.get("address", ""))) - place_words(row.get("locality", "")) - {"arusha", "moshi", "kilimanjaro"}
    hay = (listing.get("a") or "").lower()
    return bool(words) and any(w in hay for w in words)


def read_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def read_notes(path: Path) -> dict:
    notes = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        code, _, rest = line.partition(" ")
        oid, _, note = rest.partition("|")
        oid, _, pick = oid.strip().partition("#")
        if code not in VERDICTS or not oid or (pick and not pick.isdigit()):
            raise SystemExit(f"{path.name} line {n}: expected 'A <id>[#n]', 'R <id>[|note]', 'V <id>|note' or 'O <id>[#n]|note'")
        if code in ("V", "O") and not note.strip():
            raise SystemExit(f"{path.name} line {n}: a '{code}' verdict needs a note")
        if oid in notes:
            raise SystemExit(f"{path.name} line {n}: {oid} has two verdicts")
        notes[oid] = (code, note, int(pick) if pick else None)
    return notes


def candidate(i: int, listing: dict, role: str, distance_m=None, row=None) -> dict:
    c = {"index": i, "name": listing.get("n") or "", "latitude": listing.get("la"), "longitude": listing.get("lo"),
         "address": listing.get("a") or "", "url": listing.get("u") or "", "role": role}
    if distance_m is not None:
        c["distance_m"] = distance_m
    if row is not None:
        c["in_locality"] = in_locality(row, listing)
    return c


def multi_hit(row: dict, listings: list[dict], pick: int, explicit: bool, stored, agreement_m: int) -> dict:
    """Chooses among the same-name candidates (see the docstring). Returns {chosen, verdict_review, note, candidates, match,
    force_discrepancy}; for a single candidate it returns the pick unchanged."""
    top = listings[pick] if pick < len(listings) else {}
    idx = [pick] + [i for i, l in enumerate(listings) if i != pick and l.get("la") is not None and
                    (same_business(row["name"], l.get("n")) or same_business(top.get("n"), l.get("n")))]
    out = {"chosen": pick, "review": "", "candidates": [], "match": "", "force_discrepancy": False}
    if stored is not None and top.get("la") is not None:
        dist = {i: metres(stored[0], stored[1], float(listings[i]["la"]), float(listings[i]["lo"])) for i in idx}
        near = sorted((d, i) for i, d in dist.items() if d <= agreement_m)
        if explicit:  # the coordinator's pick stands; the precedence then decides as for a single listing
            near = [(dist[pick], pick)] if dist[pick] <= agreement_m else []
            out["match"] = "confirmed at stored point" if near else f"picked by the coordinator (#{pick})"
            if len(idx) > 1:
                out["candidates"] = [candidate(i, listings[i], "match" if i == pick else "other office", dist[i]) for i in idx]
            return out
        if near:
            out["chosen"], out["match"] = near[0][1], "confirmed at stored point"
        elif len(idx) > 1:
            out["force_discrepancy"] = True
        if len(idx) > 1:
            out["candidates"] = [candidate(i, listings[i], "match" if i == out["chosen"] and near else ("other office" if near else "candidate"),
                                           dist[i]) for i in idx]
        return out
    if len(idx) < 2 or explicit:
        if len(idx) > 1:
            out["candidates"] = [candidate(i, listings[i], "match" if i == pick else "other office", row=row) for i in idx]
            out["match"] = f"picked by the coordinator (#{pick})"
        return out
    chain = bool(CHAIN.search(f"{row['name']} {row.get('segment', '')}"))
    fit = [i for i in idx if (at_address(row, listings[i]) if chain else in_locality(row, listings[i]))]
    if len(fit) == 1:
        out["chosen"] = fit[0]
        out["match"] = "the only candidate at the record's address" if chain else "the only candidate in the record's locality"
        out["candidates"] = [candidate(i, listings[i], "match" if i == fit[0] else "other office", row=row) for i in idx]
        return out
    out["candidates"] = [candidate(i, listings[i], "candidate", row=row) for i in idx]
    out["review"] = (f"{len(idx)} listings named like this lead ({'a chain: none or several at the record address' if chain else 'none or several in the record locality'}): "
                     + "; ".join(f"#{c['index']} '{c['name']}' {c['latitude']}, {c['longitude']} ({c['address'] or 'no address'})" for c in out["candidates"])
                     + ". Pick one with 'A <id>#n' after checking.")
    return out


def load_geocodes():
    spec = importlib.util.spec_from_file_location("apply_geocodes", ROOT / "scripts" / "master" / "apply_geocodes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------ location precedence
WEBSITE_PIN = ("own site embed", "official site")
WEBSITE_TEXT = ("own site text",)
RANK_LABEL = {1: "website", 2: "Google Maps", 3: "OpenStreetMap", 4: "estimate"}
BANDS = [(100, "0-100 m"), (250, "100-250 m"), (500, "250-500 m"), (1000, "500 m-1 km"), (2000, "1-2 km"), (5000, "2-5 km"),
         (float("inf"), "over 5 km")]


def metres(a, b, c, d) -> int:
    a, b, c, d = map(math.radians, (a, b, c, d))
    h = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return int(round(2 * 6371000 * math.asin(math.sqrt(h))))


def source_rank(source: str | None, precision: str) -> tuple[int, str]:
    """(rank, label) of a stored point from its location_source fact and precision; the label names it in a review item."""
    source = (source or "").strip()
    if source.startswith(WEBSITE_PIN):
        return 1, "website"
    if source.startswith("Google Maps"):
        return 2, "Google Maps"
    if source.startswith("OpenStreetMap") and (precision or "") == "point":
        return 3, "OpenStreetMap"
    if source.startswith(WEBSITE_TEXT):
        return 4, "website"   # an estimate from the organisation's own website text: the user prefers the website
    return 4, "estimate"


def decide(rank: int, label: str, distance_m: int, agreement_m: int, estimates_beyond: str = "replace") -> str:
    """replaced | corroborates | discrepancy, for an accepted Google listing against a stored point of this rank."""
    if distance_m <= agreement_m:
        return "corroborates" if rank <= 2 else "replaced"
    if rank == 4 and label == "estimate" and estimates_beyond == "replace":
        return "replaced"
    return "discrepancy"


def band(distance_m: int) -> str:
    return next(name for limit, name in BANDS if distance_m <= limit)


def distribution(checks: list[dict]) -> dict:
    out = defaultdict(Counter)
    for c in checks:
        kind = {1: "website pin", 2: c["stored_source_label"], 3: "OpenStreetMap"}.get(c["stored_rank"]) or (
            "website text estimate" if c["stored_source_label"] == "website" else "other estimate")
        out[kind][band(c["distance_m"])] += 1
    return {k: {name: v[name] for _, name in BANDS if v[name]} for k, v in out.items()}


# ------------------------------------------------------------------ the welfare and government runs
RUNS = {"welfare": "arusha-welfare-2026-09", "government": "arusha-government-2026-09"}
RUN_SOURCE = (("own site embed", 1, "website"), ("official", 1, "website"), ("Google Maps", 2, "Google Maps"), ("OpenStreetMap", 3, "OpenStreetMap"))


class RunLeads:
    """A run's leads, read-only: {organisation_id: {name, key, stored, precision, source, rank, label, override}}."""

    def __init__(self, db: str, path: Path, links_path: Path):
        self.db, self.path = db, path
        links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else {}
        con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        self.leads = {}
        payload = {}
        for eid, p in con.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr "
                                  "ON sr.source_record_id = es.source_record_id WHERE es.entity_type = 'organisation'"):
            payload.setdefault(eid, json.loads(p))
        profiles = {}
        if db == "government":
            profiles = {r["organisation_id"]: dict(r) for r in con.execute(
                "SELECT organisation_id, record_key, office_level, council_name, admin_unit_name FROM government_office_profiles")}
        for o in con.execute("SELECT * FROM organisations"):
            o = dict(o)
            try:
                stored = (float(o["latitude"]), float(o["longitude"]))
            except (TypeError, ValueError):
                stored = None
            prec = o.get("geocode_precision") or ""
            pay = payload.get(o["organisation_id"], {})
            if db == "welfare":
                key = o["name"]
                override = (links.get("geo_overrides") or {}).get(key)
                source = (override or {}).get("source_type") or ("reviewed override" if override else "")
                if override:
                    rank, label = next(((r, l) for pre, r, l in RUN_SOURCE if source.startswith(pre)), (0, ""))
                    if not rank:
                        rank, label = (4, "estimate") if override.get("precision") in ("locality", "town", "city") else (2, "research or register")
                elif prec == "address":
                    rank, label = (3, "OpenStreetMap") if (o.get("osm_id") or "").strip() else (2, "research or register")
                    source = "OpenStreetMap" if rank == 3 else "the run's research or register point"
                else:
                    rank, label, source = 4, "estimate", f"the run's {prec or 'unstated'} estimate"
            else:
                prof = profiles.get(o["organisation_id"], {})
                ward = prof.get("office_level") == "ward"
                key = f"{prof.get('council_name')}|{prof.get('admin_unit_name')}" if ward else (prof.get("record_key") or pay.get("record_key") or "")
                override = (links.get("ward_locations" if ward else "office_locations") or {}).get(key)
                source = pay.get("location_source") or ""
                if prec == "estimated" or not prec:
                    rank, label = 4, "estimate"
                else:
                    rank, label = next(((r, l) for pre, r, l in RUN_SOURCE if pre.lower() in source.lower()), (2, "research or register"))
            self.leads[o["organisation_id"]] = {"name": o["name"], "key": key, "stored": stored, "precision": prec, "source": source,
                                                "rank": rank, "label": label, "override": bool(override),
                                                # the key the run's notes read (apply_gmaps_status.py): welfare the name, government the record key
                                                "status_key": key if db == "welfare" else (prof.get("record_key") or pay.get("record_key") or key)}
        con.close()

    def get(self, oid: str) -> dict:
        if oid not in self.leads:
            raise SystemExit(f"{oid} is not in the {self.db} run database {self.path}")
        return self.leads[oid]


def run_leads(args) -> dict:
    out = {}
    for db, run in RUNS.items():
        path = getattr(args, f"{db}_db", None) or ROOT / "outputs" / "runs" / run / "lead-database.sqlite"
        out[db] = RunLeads(db, Path(path), ROOT / "data" / "runs" / run / "links.json")
    return out


# ------------------------------------------------------------------ the shared-pin check
def other_listings(exclude: set[Path]) -> list[dict]:
    out = []
    for path in sorted(ENRICH_DIR.glob("google_maps_enrich_*.jsonl")):
        if path.resolve() in exclude:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                r["_file"] = path.name
                out.append(r)
    return out


def pin_check(round_rows: list[dict], others: list[dict], label: str, keep=frozenset()) -> dict:
    """Downgrades (in place) accepted rows on a shared or default point without a street address; returns the report.
    IDs in keep were reviewed by a person and stay accepted; the report lists them with the reason they were flagged."""
    by_point = defaultdict(list)
    for r in round_rows + others:
        if r.get("latitude") is None or r.get("longitude") is None or not r.get("listing_name"):
            continue
        by_point[(round(float(r["latitude"]), 4), round(float(r["longitude"]), 4))].append(r)
    downgrades, buildings, kept = [], [], []
    for r in round_rows:
        if r["verdict"] != "accept" or r.get("latitude") is None:
            continue
        lat, lon = float(r["latitude"]), float(r["longitude"])
        point = (round(lat, 4), round(lon, 4))
        default = next(((name, la, lo) for name, la, lo in DEFAULT_PINS if km(lat, lon, la, lo) <= DEFAULT_RADIUS_KM), None)
        if default:
            reason = (f"'{r['listing_name']}' sits on the known default pin {default[0]} ({default[1]:.4f}, {default[2]:.4f}): "
                      "not an office point.")
        else:
            shared = [o for o in by_point[point] if o is not r and name_key(o["listing_name"]) != name_key(r["listing_name"])]
            if not shared:
                continue
            names = list(dict.fromkeys(o["listing_name"] for o in shared))
            if street_address(r.get("address")):
                pairs = [o for o in shared if street_address(o.get("address"))]
                if pairs:
                    buildings.append({"organisation_id": r["organisation_id"], "listing": r["listing_name"], "address": r.get("address", ""),
                                      "shares_point_with": [{"listing": o["listing_name"], "address": o.get("address", ""),
                                                             "file": o.get("_file", label)} for o in pairs], "point": list(point)})
                continue
            reason = (f"Listing sits on a point shared with an unrelated listing ('{names[0]}') and has no street address: "
                      "not a specific office point.")
        item = {"organisation_id": r["organisation_id"], "organisation_name": r["organisation_name"],
                "listing": r["listing_name"], "point": list(point), "address": r.get("address", ""), "reason": reason}
        if r["organisation_id"] in keep:
            kept.append(item)
            continue
        downgrades.append(item)
        r["verdict"], r["note"] = "review", reason
    return {"round": label, "downgraded": downgrades, "kept_as_one_building": buildings, "kept_by_reviewer": kept}


# ------------------------------------------------------------------ build
def build(args) -> int:
    rows_all = read_rows(args.rows)
    rows = {r["id"]: r for r in rows_all}
    results = json.loads(args.results.read_text(encoding="utf-8"))
    notes = read_notes(args.notes)
    missing = sorted(set(notes) - set(rows))
    if missing:
        raise SystemExit(f"{len(missing)} noted IDs are not in the rows file: {missing[:5]}")
    unnoted = [oid for oid in rows if oid not in notes]
    label = f"{args.date}{args.tag}"
    root = args.out_root
    enrich_path = root / "data" / "raw" / "gap-census" / f"google_maps_enrich_{label}.jsonl"
    fills_path = root / "data" / "raw" / "geocode-research" / f"geocodes_gmaps_{label}.jsonl"
    corr_path = root / "data" / "raw" / "geocode-research" / f"geocodes_corrections_gmaps_{label}.jsonl"
    check_path = root / "runtime" / "geocode" / f"gmaps_round_{label}_check.json"
    checks_path = root / "data" / "raw" / "geocode-research" / f"location_checks_gmaps_{label}.jsonl"
    disc_path = root / "data" / "raw" / "geocode-research" / f"location_discrepancies_{args.date}.jsonl"

    con = sqlite3.connect(f"file:{args.db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    runs = run_leads(args) if any((r.get("db") or "master") != "master" for r in rows.values()) else {}

    def stored_point(oid):
        db = rows[oid].get("db") or "master"
        if db != "master":
            return runs[db].get(oid)["stored"]
        o = con.execute("SELECT latitude, longitude FROM organisations WHERE organisation_id=?", (oid,)).fetchone()
        try:
            return (float(o["latitude"]), float(o["longitude"])) if o else None
        except (TypeError, ValueError):
            return None

    enrich, codes, chosen, forced = [], {}, {}, {}
    for oid, row in rows.items():
        if oid not in notes:
            continue
        code, note, pick = notes[oid]
        listings = results.get(oid) or []
        if pick is not None and pick >= len(listings):
            raise SystemExit(f"{oid}#{pick}: the results hold only {len(listings)} listings")
        p = pick or 0
        extra = {}
        verdict = VERDICTS[code]
        if code in ("A", "O") and listings:
            m = multi_hit(row, listings, p, pick is not None, stored_point(oid) if code == "A" else None, args.agreement_m)
            p = m["chosen"]
            forced[oid] = m["force_discrepancy"]
            if m["review"]:
                verdict, note = "review", m["review"] + (f" Coordinator: {note}" if note else "")
            if m["candidates"]:
                extra = {"candidates": m["candidates"], "match": m["match"] or ("no candidate within the agreement distance" if m["force_discrepancy"] else "")}
        top = listings[p] if p < len(listings) else {}
        chosen[oid] = top
        if code == "R" and not note:
            note = f"Top listing '{top.get('n')}' is not this organisation."
        codes[oid] = code
        enrich.append({**({"db": row["db"]} if (row.get("db") or "master") != "master" else {}), "organisation_id": oid, "organisation_name": row["name"], "kind": row.get("segment", ""), "verdict": verdict,
                       "listing_name": top.get("n") or "", "latitude": top.get("la"), "longitude": top.get("lo"), "category": top.get("c") or "",
                       "address": top.get("a") or "", "phone": top.get("p") or "", "phone_note": "", "website": top.get("w") or "",
                       "website_note": "", "source_type": "Google Maps listing", "source_url": top.get("u") or "", "fetched_on": args.date,
                       "query": row["query"], "note": note, **extra})

    report = {"round": label, "downgraded": [], "kept_as_one_building": [], "kept_by_reviewer": []}
    if not args.no_pin_check:
        exclude = {(ENRICH_DIR / enrich_path.name).resolve(), enrich_path.resolve()}
        report = pin_check([e for e in enrich if codes[e["organisation_id"]] != "O"], other_listings(exclude), label, set(args.keep))

    gc = load_geocodes()
    fills, corr, checks = [], [], []
    for e in enrich:
        oid, code = e["organisation_id"], codes[e["organisation_id"]]
        if e["verdict"] != "accept" or e["latitude"] is None:
            continue
        top, row = chosen[oid], rows[oid]
        if (row.get("db") or "master") != "master":
            run_line(args, label, e, top, row, code, runs[row["db"]].get(oid), forced.get(oid), fills, checks)
            continue
        o = con.execute("SELECT * FROM organisations WHERE organisation_id=?", (oid,)).fetchone()
        if o is None:
            raise SystemExit(f"{oid} is not in {args.db}")
        addr = top.get("a") or ""
        note = e["note"]
        line = {"db": "master", "organisation_id": oid, "organisation_name": o["name"], "key": "",
                "status": "outside_confirmed" if code == "O" else "placed", "latitude": top["la"], "longitude": top["lo"], "precision": "point",
                "source_type": "Google Maps listing", "source_url": top["u"], "fetched_on": args.date,
                "as_found": f"Google Maps listing '{top['n']}' at {top['la']}, {top['lo']}" + (f"; {addr}" if addr else ""),
                "basis": note or f"Google Maps listing named '{top['n']}' for the search '{row['query']}': same organisation, in the record's area.",
                "geocode_source": f"Google Maps: {top['u']}", "confidence": "high"}
        try:
            stored = (float(o["latitude"]), float(o["longitude"]))
        except (TypeError, ValueError):
            stored = None
        if stored is None or code == "O":
            fills.append(line)
            continue
        src = gc.stored_source(con, o)
        correction = {**line, "replace": True, "old_latitude": stored[0], "old_longitude": stored[1], "old_precision": o["geocode_precision"] or "",
                      "old_location_source": src if src is not None else gc.NO_SOURCE,
                      "km_moved": km(stored[0], stored[1], top["la"], top["lo"])}
        rank, slabel = source_rank(src, o["geocode_precision"] or "")
        dist = metres(stored[0], stored[1], float(top["la"]), float(top["lo"]))
        outcome = "replaced" if args.no_precedence else decide(rank, slabel, dist, args.agreement_m, args.estimates_beyond)
        if forced.get(oid) and not args.no_precedence:
            outcome = "discrepancy"   # several same-name listings, none at the stored point: a second office or a wrong point
        if outcome == "replaced":
            if rank == 3 and not args.no_precedence:
                correction.update({"rank_replace": True, "agreement_m": args.agreement_m})
            corr.append(correction)
        line_ = check_line(label, args.date, o, e, top, stored, src if src is not None else gc.NO_SOURCE, o["geocode_precision"] or "",
                           rank, slabel, dist, args.agreement_m, outcome)
        line_["match"] = "confirmed at stored point" if dist <= args.agreement_m else e.get("match", "")
        if e.get("candidates"):
            line_["candidates"] = e["candidates"]
        checks.append(line_)
    con.close()

    def write(path: Path, lines: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines), encoding="utf-8", newline="\n")

    write(enrich_path, enrich)
    write(fills_path, fills)
    write(corr_path, corr)
    write(checks_path, checks)
    earlier = [json.loads(x) for x in disc_path.read_text(encoding="utf-8").splitlines() if x.strip()] if disc_path.exists() else []
    write(disc_path, [d for d in earlier if d.get("round") != label] + [c for c in checks if c["outcome"] == "discrepancy"])
    report["agreement_m"] = args.agreement_m
    report["location_outcomes"] = dict(Counter(c["outcome"] for c in checks))
    report["distance_distribution"] = distribution(checks)
    report["google_maps_status"] = dict(Counter(status_of(e)[0] for e in enrich))
    check_path.parent.mkdir(parents=True, exist_ok=True)
    check_path.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{label}: verdicts {dict(Counter(e['verdict'] for e in enrich))}; fills {len(fills)}; corrections {len(corr)}"
          + (f"; {len(unnoted)} rows without a verdict were left out" if unnoted else ""))
    print(f"Google Maps status: {report['google_maps_status']}")
    print(f"stored points against accepted listings (agreement {args.agreement_m} m): {report['location_outcomes']}")
    print(f"distance distribution: {json.dumps(report['distance_distribution'])}")
    print_discrepancies([c for c in checks if c["outcome"] == "discrepancy"])
    print_report(report)
    print("\n".join(str(p) for p in (enrich_path, fills_path, corr_path, checks_path, disc_path, check_path)))
    return 0


def status_of(e: dict) -> tuple[str, str]:
    """(google_maps_status, detail) of one enrich line: listed (an accepted listing, with its URL), not_found (no matching
    listing: the lead is not registered on Google Maps) or review (with the reason)."""
    if e.get("verdict") == "accept":
        return "listed", f"'{e.get('listing_name', '')}' {e.get('source_url', '')}".strip()
    if e.get("verdict") == "review":
        return "review", e.get("note") or "listing to confirm"
    return "not_found", f"not registered on Google Maps (search '{e.get('query', '')}'" + (
        f"; top result '{e['listing_name']}' is another organisation)" if e.get("listing_name") else ")")


def run_line(args, label, e, top, row, code, lead, forced, fills, checks) -> None:
    """A run lead's accepted listing: a fill (an override for apply_geocodes.py) or a location check (see the docstring)."""
    oid, addr, note = e["organisation_id"], top.get("a") or "", e["note"]
    line = {"db": row["db"], "organisation_id": oid, "organisation_name": lead["name"], "key": lead["key"],
            "status": "outside_confirmed" if code == "O" else "placed", "latitude": top["la"], "longitude": top["lo"], "precision": "point",
            "source_type": "Google Maps listing", "source_url": top["u"], "fetched_on": args.date,
            "as_found": f"Google Maps listing '{top['n']}' at {top['la']}, {top['lo']}" + (f"; {addr}" if addr else ""),
            "basis": note or f"Google Maps listing named '{top['n']}' for the search '{row['query']}': same organisation, in the record's area.",
            "geocode_source": f"Google Maps: {top['u']}", "confidence": "high"}
    stored = lead["stored"]
    if stored is None or code == "O":
        if not lead["override"]:
            fills.append(line)
        return
    dist = metres(stored[0], stored[1], float(top["la"]), float(top["lo"]))
    outcome = "replaced" if args.no_precedence else decide(lead["rank"], lead["label"], dist, args.agreement_m, args.estimates_beyond)
    if forced and not args.no_precedence:
        outcome = "discrepancy"
    decision = None
    if outcome == "replaced" and lead["override"]:
        outcome, decision = "corroborates", "the run's reviewed override is kept (an override is never overwritten); the listing corroborates it"
    if outcome == "replaced":
        fills.append({**line, "replaces": {"latitude": stored[0], "longitude": stored[1], "precision": lead["precision"], "source": lead["source"],
                                           "km_moved": km(stored[0], stored[1], top["la"], top["lo"])}})
    c = check_line(label, args.date, {"organisation_id": oid, "name": lead["name"]}, e, top, stored, lead["source"], lead["precision"],
                   lead["rank"], lead["label"], dist, args.agreement_m, outcome, db=row["db"])
    c["key"] = lead["key"]
    if decision:
        c["decision"] = decision
    c["match"] = "confirmed at stored point" if dist <= args.agreement_m else e.get("match", "")
    if e.get("candidates"):
        c["candidates"] = e["candidates"]
    checks.append(c)


def check_line(label, day, o, e, top, stored, source, precision, rank, slabel, dist, agreement_m, outcome, db="master") -> dict:
    return {"round": label, "date": day, "db": db, "organisation_id": o["organisation_id"], "organisation_name": o["name"],
            "status": outcome, "outcome": outcome, "distance_m": dist, "agreement_m": agreement_m,
            "stored_latitude": stored[0], "stored_longitude": stored[1], "stored_precision": precision, "stored_source": source,
            "stored_rank": rank, "stored_source_label": slabel,
            "google_latitude": top["la"], "google_longitude": top["lo"], "google_listing": top.get("n", ""), "google_address": top.get("a") or "",
            "google_url": top.get("u", ""), "enrich_file": f"data/raw/gap-census/google_maps_enrich_{label}.jsonl",
            "decision": {"replaced": "the listing replaces the lower-ranked stored point (correction line)",
                         "corroborates": f"the stored {RANK_LABEL[rank]} point is kept; the listing corroborates it",
                         "discrepancy": "no correction: the user and the orchestrator decide which point to keep"}[outcome]}


def print_discrepancies(items: list[dict]) -> None:
    for c in items:
        print(f"DISCREPANCY ({c['round']}): {c['organisation_name']} ({c['organisation_id']}): stored {c['stored_source_label']} point "
              f"{c['stored_latitude']}, {c['stored_longitude']} ({c['stored_source'][:70]}) vs Google '{c['google_listing']}' "
              f"{c['google_latitude']}, {c['google_longitude']}: {c['distance_m']} m")


def print_report(report: dict) -> None:
    if not report["downgraded"]:
        print(f"shared-pin check ({report['round']}): no accepted listing downgraded")
    for d in report["downgraded"]:
        print(f"DOWNGRADED to review ({report['round']}): {d['organisation_name']} ({d['organisation_id']}), listing '{d['listing']}' "
              f"at {d['point'][0]}, {d['point'][1]}: {d['reason']}")
    for k in report.get("kept_by_reviewer", []):
        print(f"kept by reviewer (--keep) ({report['round']}): {k['organisation_name']} ({k['organisation_id']}): flagged as: {k['reason']}")
    for b in report["kept_as_one_building"]:
        others = "; ".join(f"'{o['listing']}' ({o['address']}, {o['file']})" for o in b["shares_point_with"])
        print(f"kept, likely one building ({report['round']}): '{b['listing']}' ({b['address']}) shares {b['point'][0]}, {b['point'][1]} with {others}")


def audit(paths: list[Path]) -> int:
    """The shared-pin check on committed round files, against every other round file; writes nothing. Exit 1 on a downgrade."""
    found = 0
    for path in paths:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [r for r in rows if not (r["verdict"] == "accept" and "outside" in (r.get("note") or "").lower())]
        exclude = {path.resolve(), (ENRICH_DIR / path.name).resolve()}
        report = pin_check(rows, other_listings(exclude), path.name)
        print_report(report)
        found += len(report["downgraded"])
    return 1 if found else 0


SUPERSEDED = re.compile(r"^(-?\d+(?:\.\d+)?), (-?\d+(?:\.\d+)?) \(([^;]*); (.*?); record .*?\), replaced (\d{4}-\d\d-\d\d)")


def retro(paths: list[Path], db: Path, agreement_m: int, estimates_beyond: str) -> int:
    """The precedence over committed rounds, against the master as it is now; report only (runtime/geocode/gmaps_retro_<today>.json).
    A listing already applied is compared with the superseded_location it replaced; a listing that filled an empty point has
    nothing to compare."""
    from datetime import date
    gc = load_geocodes()
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    items, outcomes = [], Counter()
    for path in paths:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            e = json.loads(line)
            if e.get("verdict") != "accept" or e.get("latitude") in (None, "") or "outside" in (e.get("note") or "").lower():
                continue
            o = con.execute("SELECT * FROM organisations WHERE organisation_id=?", (e["organisation_id"],)).fetchone()
            if o is None:
                outcomes["organisation no longer in the master"] += 1
                continue
            try:
                current = (float(o["latitude"]), float(o["longitude"]))
            except (TypeError, ValueError):
                outcomes["no point in the master (listing not applied)"] += 1
                continue
            g = (float(e["latitude"]), float(e["longitude"]))
            src = gc.stored_source(con, o)
            applied = metres(*current, *g) <= 1 and (src or "").startswith("Google Maps")
            other, how = None, "current"
            if applied:
                olds = []
                for (value,) in con.execute("SELECT value FROM facts WHERE entity_type='organisation' AND entity_id=? AND field='superseded_location'",
                                            (o["organisation_id"],)):
                    m = SUPERSEDED.match(value)
                    if m:
                        olds.append((m.group(5), float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)))
                if not olds:
                    outcomes["filled an empty point (nothing to compare)"] += 1
                    continue
                _, la, lo, prec, osrc = max(olds)
                other, how = (la, lo, prec, osrc), "superseded"
            else:
                other = (current[0], current[1], o["geocode_precision"] or "", src if src is not None else gc.NO_SOURCE)
            rank, slabel = source_rank(other[3], other[2])
            dist = metres(other[0], other[1], *g)
            outcome = decide(rank, slabel, dist, agreement_m, estimates_beyond)
            state = ("applied: " if applied else "not applied: ") + outcome
            outcomes[state] += 1
            items.append({"file": path.name, "line": n, "organisation_id": o["organisation_id"], "organisation_name": o["name"],
                          "compared_with": how, "applied": applied, "outcome": outcome, "distance_m": dist,
                          "stored_latitude": other[0], "stored_longitude": other[1], "stored_precision": other[2], "stored_source": other[3],
                          "stored_rank": rank, "stored_source_label": slabel, "google_latitude": g[0], "google_longitude": g[1],
                          "google_listing": e.get("listing_name", ""), "google_url": e.get("source_url", "")})
    con.close()
    out = ROOT / "runtime" / "geocode" / f"gmaps_retro_{date.today().isoformat()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    report = {"agreement_m": agreement_m, "estimates_beyond": estimates_beyond, "files": [p.name for p in paths], "outcomes": dict(outcomes),
              "distance_distribution": distribution(items), "discrepancies": [i for i in items if i["outcome"] == "discrepancy"], "items": items}
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    disc = out.with_name(f"gmaps_retro_discrepancies_{date.today().isoformat()}.jsonl")  # for apply_gmaps_status.py --discrepancies
    disc.write_text("".join(json.dumps({**i, "agreement_m": agreement_m}, ensure_ascii=False) + "\n" for i in report["discrepancies"]),
                    encoding="utf-8", newline="\n")
    print(json.dumps({k: report[k] for k in ("agreement_m", "outcomes", "distance_distribution")}, indent=1))
    for i in report["discrepancies"]:
        print(f"DISCREPANCY ({i['file']}, {'applied as a correction' if i['applied'] else 'not applied'}): {i['organisation_name']} "
              f"({i['organisation_id']}): {i['stored_source_label']} point {i['stored_latitude']}, {i['stored_longitude']} "
              f"[{i['stored_source'][:80]}] vs Google '{i['google_listing']}' {i['google_latitude']}, {i['google_longitude']}: {i['distance_m']} m")
    print(out)
    print(disc)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", nargs="+", type=Path, help="run only the shared-pin check on these enrich files")
    parser.add_argument("--date", help="the lookup date, YYYY-MM-DD (fetched_on and the file names)")
    parser.add_argument("--tag", default="", help="the round letter (a, b, c ...)")
    parser.add_argument("--rows", type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--db", type=Path, help="the master before the round (read-only)")
    parser.add_argument("--no-pin-check", action="store_true", help="skip the shared-pin check (not recommended)")
    parser.add_argument("--keep", nargs="+", default=[], metavar="ID",
                        help="organisation IDs a person reviewed after the check flagged them: they stay accepted (listed in the report)")
    parser.add_argument("--out-root", type=Path, default=ROOT, help="write under this folder instead of the repository (for a trial)")
    parser.add_argument("--agreement-m", type=int, default=500, help="the agreement distance in metres (default 500)")
    parser.add_argument("--estimates-beyond", choices=["replace", "discrepancy"], default="replace",
                        help="an estimate (not from the organisation's own website) beyond the agreement distance: replaced (default) or a discrepancy")
    parser.add_argument("--no-precedence", action="store_true",
                        help="build corrections as the 13 October 2026 rounds were built (every stored point replaced), to reproduce them")
    parser.add_argument("--welfare-db", type=Path, help="the welfare run database (read-only; default outputs/runs/<run>/lead-database.sqlite)")
    parser.add_argument("--government-db", type=Path, help="the government run database (read-only; default as for welfare)")
    parser.add_argument("--retro", nargs="+", type=Path, help="report the precedence over these committed enrich files (needs --db); writes runtime/ only")
    args = parser.parse_args()
    if args.audit:
        return audit(args.audit)
    if args.retro:
        if not args.db:
            parser.error("--retro needs --db (a read-only copy of the master as it is now)")
        return retro(args.retro, args.db, args.agreement_m, args.estimates_beyond)
    for need in ("date", "rows", "results", "notes", "db"):
        if not getattr(args, need):
            parser.error(f"--{need} is required")
    return build(args)


if __name__ == "__main__":
    sys.exit(main())
