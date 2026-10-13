#!/usr/bin/env python3
"""Build the VICOBA intake for the company master from raw captures: group-level records only, no personal data.

Decided 13 October 2026 (docs/plans/vicoba-integration-plan.md, "Decisions taken", section 0 and decision 2; the sourcing plan
docs/plans/vicoba-sourcing-plan.md): VICOBAs are a subsegment of savings groups in the master; group names come from council Tier 4
register extracts (requested inside the government run's council letters, group level only), intermediaries and ward CDOs; no web
search is used to find groups; personal columns are stripped on import; no loan-recipient list is ever used.

Modes (each writes only under data/raw/vicoba/; nothing touches a database):

  --import-extract <csv|xlsx> --council <name> --received <date> [--letter <ref>]
      Turns a council-supplied register extract into a capture file, data/raw/vicoba/captures/council_extract_<council>_<date>.csv.
      Only the allow-listed group-level columns are kept (group name, type, ward, village or mtaa, registration number and date,
      member count, meeting place, supporting NGO, cadence, cycle and share-out months). Every other column (chair, secretary,
      treasurer, member names, phones, ID numbers, loan or savings figures) is dropped before anything is written, and the import log
      (<capture>.import-log.json) records the dropped column names and how many values each held, never a value. A phone-like value
      in a kept column is dropped too.

  --rescan-council-news [--council-sites <dir>] [--cache-root <runtime/government/<run>>]
      The offline re-scan of the council website captures (data/raw/government-research/council_sites/*.json) with the collector's
      cached news text (runtime/government/arusha-government-2026-09/http-cache*/, read only; from a worktree pass the main checkout's
      folder). Writes data/raw/vicoba/captures/council_news_<date>.jsonl: every group mention with its council, ward, village and type
      as published, whether it is admitted as a VICOBA candidate and why, and the aggregates ("vikundi 25 vya VICOBA"). Person names
      are never captured: only the words naming the group are kept, and no excerpt of the news text is stored. A group is admitted
      only when the source identifies it as a savings-and-loan group (VICOBA, VIKOBA, VSLA, Village Community Bank, kikundi cha kuweka
      na kukopa); a council 10% loan group reported in the news is not (section 0, item 2 and 4).

  --introducers <research.jsonl>
      Turns introducer research records (savings-group networks, NGO savings programmes, VICOBA support providers, banks' group
      products) into data/raw/vicoba/introducers_intake_<date>.csv (the shared intake contract, segment 'Introducer: savings-group
      network', for organisations not yet in the master) and data/raw/vicoba/introducer_facts_<date>.jsonl (fact lines for
      organisations the master or a run already holds: their savings-group programme or group-account product, with its source).
      Published routes only; every claim keeps its source; an organisation with no published route is kept and labelled.

  (default) build
      Reads every capture in data/raw/vicoba/captures/ (the template data/reference/vicoba-capture-template.csv: council extracts,
      intermediary introductions and publications, ward CDO meeting notes, the group's own published route; the admitted lines of
      council_news_<date>.jsonl; data/raw/gap-census/vicoba_candidates_<date>.json, the map features the gap census routes here) and
      writes:
        data/raw/vicoba/master_intake_<date>.csv   one row per source, in the shared contract plus the VICOBA columns that
                                                   scripts/master/add_vicoba_groups.py reads (its INTAKE_COLUMNS)
        data/raw/vicoba/groups_<date>.jsonl        one line per group: every fact with its source, record_status, review signals
        data/raw/vicoba/aggregates_<date>.jsonl    reported counts ("25 groups formed"): facts for a sponsor or ward, never records
        data/raw/vicoba/build_report_<date>.json   counts, exclusions with reasons, field rejections (names only, never values)

Rules (the shared contracts of the integration plan, section 4.1 with section 0's subtypes):
- Group key VIC|<council>|<ward>|<normalised name> and ID hid("O", "vicoba", key), computed with add_vicoba_groups.py's own functions,
  council and ward spelled as the government run's admin_units spell them (data/runs/arusha-government-2026-09/intake.csv, with the
  run's ward_aliases). Two groups whose names differ only in the stripped type words (Upendo Wanawake, Upendo Vijana) in one ward keep
  the type word in the name part of the key, so neither lead is lost, and are flagged for review.
- Dedupe: an exact key, or an exact registration number within one registration authority, is the same group; its sources
  accumulate (one intake row each). Nothing else merges. A similar name in the same council goes to review ('VICOBA possible
  duplicate'), except a common name (data/reference/vicoba-common-names.json), which matches only on the full key. A name equal to a
  SACCOS name goes to review ('VICOBA may be a registered SACCOS', with --master); a group carrying a master employer's name gets
  employer_ref with a review.
- Aggregates are never records. A meeting place is kept only when it is a public venue (church or mosque hall, school, ward or
  village office, market, bank branch, community hall, NGO office); a home is rejected. A phone is never written: a role phone with
  a published-for-role source keeps only phone_basis (the number goes through the contact path); any other phone is rejected.
- women_group is true only on source evidence (the name names women: wanawake, akina mama, kina mama, women, mama; the source calls it
  a women's group; or the council supplies it as a 10% loan women's group); the disability subtype only when a council or
  intermediary supplies the group as such.
- record_status (complete; incomplete: no ward / no introducer route / name only; stale: not confirmed in 12 months) and the incomplete
  and stale labels are computed as add_vicoba_groups.py computes them. Every group with a name and an area is kept.

--self-test runs the fixtures in data/raw/vicoba/fixtures/ (section 5 of the integration plan) into a temporary folder and checks
every rule above, then validate_intake.py on the output. Run from the repository root.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import html
import io
import json
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "master"))
sys.path.insert(0, str(ROOT / "scripts" / "government"))
sys.path.insert(0, str(ROOT / "skills" / "silverleaf-create-lead-list" / "scripts"))
import add_vicoba_groups as AV  # noqa: E402  (the shared contract: key, ID, labels, status)
import recompute_campus_distances as RC  # noqa: E402  (band, tier)
import validate_intake as VALIDATOR  # noqa: E402

RAW = ROOT / "data" / "raw" / "vicoba"
CAPTURES = RAW / "captures"
FIXTURES = RAW / "fixtures"
REFERENCE = ROOT / "data" / "reference"
TEMPLATE = REFERENCE / "vicoba-capture-template.csv"
INTAKE_TEMPLATE = ROOT / "skills" / "silverleaf-create-lead-list" / "assets" / "lead-intake-template.csv"
GOV_RUN = "arusha-government-2026-09"
WELFARE_RUN = "arusha-welfare-2026-09"
GOV_INTAKE = ROOT / "data" / "runs" / GOV_RUN / "intake.csv"
GOV_CONFIG = ROOT / "data" / "runs" / GOV_RUN / "run-config.json"
GOV_LINKS = ROOT / "data" / "runs" / GOV_RUN / "links.json"
COUNCIL_SITES = ROOT / "data" / "raw" / "government-research" / "council_sites"
GOV_CACHE = ROOT / "runtime" / "government" / GOV_RUN
GAP_CENSUS = ROOT / "data" / "raw" / "gap-census"
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
CAMPUS_LABEL = {"Arusha City": "Arusha City (Sakina)", "Ilboru": "Ilboru", "Kijenge": "Kijenge", "Usa River": "Usa River",
                "Boma Ngombe": "Boma Ng'ombe"}
CATCHMENT_COUNCILS = ("Arusha City Council", "Arusha District Council", "Meru District Council", "Hai District Council",
                      "Siha District Council", "Moshi District Council", "Moshi Municipal Council", "Monduli District Council")

TEMPLATE_COLUMNS = ["capture_id", "capture_kind", "group_name", "group_type_as_published", "women_group_evidence", "council", "ward",
                    "village_or_mtaa", "registration_number", "registration_authority", "registration_date", "member_count",
                    "meeting_place_public", "meeting_place_kind", "meeting_cadence", "cycle_start_month", "share_out_month", "sponsor_name",
                    "sponsor_kind", "sponsor_ref", "introducer_kind", "introducer_ref", "employer_ref", "role_phone", "phone_basis",
                    "phone_source_url", "aggregate_count", "aggregate_area", "source_url", "source_path", "source_locator", "source_date",
                    "acquired_on", "verified_on", "last_confirmed", "evidence_excerpt", "notes"]
CAPTURE_KINDS = ("council_extract", "intermediary_introduction", "intermediary_publication", "ward_cdo_meeting", "group_self",
                 "council_news", "map_feature")
# Source rank: the first source of a group supplies its intake identity; later ones accumulate.
KIND_RANK = {k: i for i, k in enumerate(CAPTURE_KINDS)}
EVIDENCE = {"council_extract": ("official", "verified"), "intermediary_introduction": ("published", "verified"),
            "intermediary_publication": ("published", "needs_review"), "ward_cdo_meeting": ("research_note", "verified"),
            "group_self": ("published", "verified"), "council_news": ("official", "needs_review"), "map_feature": ("directory", "needs_review")}
# Captures whose own date confirms the group (a register received, an introduction, a meeting); for the others the publication date does.
CONFIRMS_ON_RECEIPT = ("council_extract", "intermediary_introduction", "ward_cdo_meeting", "group_self")
PUBLIC_VENUES = ("church_hall", "mosque_hall", "school", "ward_office", "village_office", "market", "bank_branch", "community_hall",
                 "ngo_office", "other_public")
VENUE_WORDS = re.compile(r"\b(kanisa|kanisani|church|msikiti|mosque|shule|school|ofisi ya (kata|kijiji|mtaa)|ward office|village office|"
                         r"soko|sokoni|market|benki|bank|ukumbi|hall|community centre|community center)\b", re.I)
SAVINGS_MARK = re.compile(r"\b(vicoba|vikoba|kikoba|vsla|village community bank|village savings and loans?|kuweka na kukopa|kuweka akiba na kukopa|"
                          r"savings and loans?|saving and loans?|savings group|saving group|tier ?(4|iv)|cmg|community microfinance group|"
                          r"micro-?finance group|mirco-?finance)\b", re.I)
ROTATING = re.compile(r"\b(upatu|mchezo)\b", re.I)
LOAN_10 = re.compile(r"asilimia\s*10|10\s*%|mkopo wa asilimia|mikopo ya asilimia", re.I)
YOUTH = re.compile(r"\b(vijana|youth)\b", re.I)
DISABILITY = re.compile(r"\b(walemavu|wenye ulemavu|disabilit(y|ies)|disabled)\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?255|0)[\s\-]?[67]\d{2}[\s\-]?\d{3}[\s\-]?\d{3}(?!\d)|(?<!\d)(?:\+?255|0)[\s\-]?2\d[\s\-]?\d{3}[\s\-]?\d{4}(?!\d)")
PERSON_IN_NAME = re.compile(r"\b(Mama|Baba|Mzee|Bibi|Bi\.|Bw\.|Mrs?\.|Dkt?\.)\s+[A-Z][a-z]+")
PRODUCT_NAMES = re.compile(r"\b(pamoja account|niamoja|nia moja|kikundi account|m-?koba|group account)\b", re.I)
TYPE_WORDS = {"wanawake": "wanawake", "women": "wanawake", "vijana": "vijana", "youth": "vijana"}
SPONSOR_KINDS, INTRODUCER_KINDS = AV.SPONSOR_KINDS, AV.INTRODUCER_KINDS

# Council extract import: allow-listed columns (header aliases, matched after folding) -> template column.
EXTRACT_ALIASES = {
    "group_name": ("jina la kikundi", "jina kikundi", "group name", "name of group", "name of the group", "kikundi", "group", "jina"),
    "group_type_as_published": ("aina ya kikundi", "aina", "group type", "type", "category", "kundi"),
    "ward": ("kata", "ward"),
    "village_or_mtaa": ("kijiji", "mtaa", "kijiji mtaa", "kijiji au mtaa", "village", "street", "village mtaa", "village or mtaa"),
    "registration_number": ("namba ya usajili", "na ya usajili", "usajili na", "registration number", "registration no", "reg no", "reg number",
                            "namba ya cheti", "certificate number"),
    "registration_date": ("tarehe ya usajili", "registration date", "date registered", "date of registration"),
    "member_count": ("idadi ya wanachama", "idadi", "number of members", "members count", "member count", "no of members", "jumla ya wanachama"),
    "meeting_place_public": ("mahali pa kukutana", "mahali pa mikutano", "eneo la mikutano", "meeting place", "meeting venue"),
    "meeting_cadence": ("siku ya kukutana", "ratiba ya vikao", "meeting day", "meeting frequency"),
    "sponsor_name": ("shirika linalosaidia", "shirika", "mfadhili", "supporting ngo", "ngo", "sponsor", "supporting organisation",
                     "supporting organization"),
    "share_out_month": ("mwezi wa kugawana", "share out month", "share-out month"),
    "cycle_start_month": ("mwezi wa kuanza mzunguko", "cycle start month"),
}
PERSONAL_HEADER = re.compile(r"mwenyekiti|katibu|mweka ?hazina|chair|secretary|treasurer|simu|phone|mobile|namba ya simu|nida|"
                             r"kitambulisho|id no|jina la mwanachama|member name|wanachama majina|majina|names?|email|barua pepe|mkopo|loan|"
                             r"akiba|savings|balance|kiasi|amount|signator|sahihi|anwani|address|nyumba", re.I)


# ------------------------------------------------------------------------------------------------------------- small helpers
def fold(text) -> str:
    return unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()


def squash(text) -> str:
    return re.sub(r"[^a-z0-9]", "", fold(text))


def clean(text) -> str:
    return " ".join(str(text or "").split())


def words25(text: str) -> str:
    w = clean(text).split()
    return " ".join(w[:25])


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return [{k: (v or "").strip() for k, v in r.items() if k is not None} for r in csv.DictReader(fh)]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def stable_run_id(name: str, locality: str) -> str:
    """The run database's organisation ID (initialize_lead_db.stable_id over name and locality)."""
    key = "|".join(VALIDATOR.norm(p) for p in (name, locality))
    return "ORG_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def iso(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value or "")[:10])
    except ValueError:
        return None


# ------------------------------------------------------------------------------------------------------------- places
class Places:
    """Councils and wards as the government run spells them, with each ward's reference point and its CDO office ID."""

    def __init__(self, intake: Path = GOV_INTAKE, config: Path = GOV_CONFIG, links: Path = GOV_LINKS):
        conf = json.loads(config.read_text(encoding="utf-8"))
        self.councils = [c["name"] for c in conf["councils"]]
        self.host_council = {c["host"]: c["name"] for c in conf["councils"] if c.get("host")}
        self.alias = {}
        for c in conf["councils"]:
            name, sw = c["name"], c.get("name_sw", "")
            town = name.replace(" City Council", "").replace(" Municipal Council", "").replace(" District Council", "")
            kind = "city" if "City" in name else "municipal" if "Municipal" in name else "district"
            forms = {name, sw, sw.replace("Halmashauri ya ", ""), f"{town} {kind}", f"{town} {kind} council"}
            forms |= {f"{town} cc", f"jiji la {town}", f"{town} city"} if kind == "city" else set()
            forms |= {f"{town} mc", f"manispaa ya {town}", f"{town} municipality"} if kind == "municipal" else set()
            forms |= {f"{town} dc", f"wilaya ya {town}", f"{town} district"} if kind == "district" else set()
            if town not in ("Arusha", "Moshi"):          # 'Arusha' and 'Moshi' alone name two councils each
                forms.add(town)
            for f in forms:
                if f:
                    self.alias[squash(f)] = name
        self.wards, self.council_office = {}, {}
        aliases = {}
        if links.is_file():
            data = json.loads(links.read_text(encoding="utf-8")).get("ward_aliases", {})
            for council, mapping in data.items():
                if isinstance(mapping, dict):
                    for variant, ward in mapping.items():
                        aliases[(council, squash(variant))] = ward
        self.ward_alias = aliases
        for r in read_csv(intake):
            if r.get("subtype") == "ward":
                council, ward = r["council_name"], r["admin_unit_name"]
                self.wards[(council, squash(ward))] = {
                    "ward": ward, "council": council, "latitude": r["latitude"], "longitude": r["longitude"],
                    "distance_km": r["distance_km"], "campus": r["campus"],
                    "office_id": stable_run_id(r["organisation_name"], r["locality"])}
            elif r.get("subtype") == "council":
                self.council_office[r["council_name"]] = stable_run_id(r["organisation_name"], r["locality"])

    def council(self, text: str) -> str:
        if not text:
            return ""
        s = squash(text)
        if s in self.alias:
            return self.alias[s]
        s2 = squash(re.sub(r"(?i)^halmashauri ya |\bcouncil\b", "", text))
        return self.alias.get(s2, "")

    def ward(self, council: str, text: str) -> dict | None:
        if not (council and text):
            return None
        name = re.sub(r"(?i)^(kata ya|ward of)\s+|\s+(ward|kata)$", "", clean(text))
        hit = self.wards.get((council, squash(name)))
        if not hit and (council, squash(name)) in self.ward_alias:
            hit = self.wards.get((council, squash(self.ward_alias[(council, squash(name))])))
        return hit


# ------------------------------------------------------------------------------------------------------------- one capture
def classify(cap: dict) -> dict:
    """Admission, subtype and the women's-group tag from the source's own words."""
    name, typ = cap.get("group_name", ""), cap.get("group_type_as_published", "")
    kind = cap.get("capture_kind", "")
    said = " ".join([name, typ])
    identified = bool(SAVINGS_MARK.search(said)) or kind == "council_extract" or (
        kind in ("intermediary_introduction", "ward_cdo_meeting") and bool(SAVINGS_MARK.search(cap.get("notes", "") + " " + typ)))
    reason = ""
    if ROTATING.search(said) and not re.search(r"vicoba|vikoba", said, re.I):
        identified, reason = False, "rotating group (upatu or mchezo) not called a VICOBA by the source"
    elif not identified:
        reason = "not identified by the source as a savings-and-loan group (VICOBA, VSLA, Tier 4 register, or an intermediary's savings group)"
    women, basis = False, ""
    if AV.WOMEN_NAME.search(name):
        women, basis = True, "name"
    elif re.search(r"women'?s? group|kikundi cha wanawake|wanawake|women", cap.get("women_group_evidence", "") + " " + typ, re.I) and \
            cap.get("women_group_evidence"):
        women, basis = True, "source_says"
    elif kind == "council_extract" and re.search(r"wanawake|women", typ, re.I):
        women, basis = True, "council_women_loan_group" if LOAN_10.search(typ) or re.search(r"mkopo|loan", typ, re.I) else "source_says"
    supplied_disability = kind in ("council_extract", "intermediary_introduction", "intermediary_publication") and bool(DISABILITY.search(typ))
    if supplied_disability:
        subtype = AV.DISABILITY_SUBTYPE
    elif women:
        subtype = AV.WOMEN_SUBTYPE
    elif YOUTH.search(said):
        subtype = "VICOBA — youth group"
    elif (cap.get("sponsor_kind") == "ngo" or kind == "intermediary_publication") and not re.search(r"vicoba|vikoba", said, re.I):
        subtype = "VSLA — NGO-programme group"
    else:
        subtype = AV.DEFAULT_SUBTYPE
    return {"identified": identified, "reason": reason, "women": women, "basis": basis, "subtype": subtype}


def process(cap: dict, places: Places, as_of: date) -> dict:
    """One capture -> {'kind': 'group'|'aggregate'|'excluded', ...} with field rejections (names only)."""
    rejections, notes = [], []
    cap = {k: clean(v) for k, v in cap.items()}
    kind = cap.get("capture_kind", "")
    ref = f"{cap.get('_file', '')}:{cap.get('_line', '')}"
    if kind not in CAPTURE_KINDS:
        return {"kind": "excluded", "ref": ref, "name": cap.get("group_name", ""), "reason": f"capture_kind '{kind}' is not one of {list(CAPTURE_KINDS)}"}
    # Phone-like values anywhere but role_phone are dropped; role_phone is never copied.
    for field in TEMPLATE_COLUMNS:
        if field in ("role_phone", "source_url", "phone_source_url", "source_path", "source_locator", "capture_id") or not cap.get(field):
            continue
        if PHONE.search(cap[field]):
            cap[field] = PHONE.sub("", cap[field]).strip(" ,;:-")
            rejections.append(f"{field}: a phone number removed")
    phone_basis = ""
    if cap.get("role_phone") or cap.get("phone_basis"):
        basis = cap.get("phone_basis", "")
        if basis == "published_for_role" and cap.get("phone_source_url", "").startswith("http") and cap.get("role_phone"):
            phone_basis = "published_for_role"
            notes.append(f"A role phone is published for this group at {cap['phone_source_url']}: record it through the contact path "
                         "(contacts.role_phone with its source); it is not stored here.")
        elif AV.CONSENT.match(basis):
            phone_basis = basis
        else:
            rejections.append("role_phone: rejected (no published-for-role source and no recorded consent)")
    name = cap.get("group_name", "")
    if cap.get("aggregate_count"):
        if not re.fullmatch(r"\d+", cap["aggregate_count"].replace(",", "")):
            return {"kind": "excluded", "ref": ref, "name": name, "reason": "aggregate_count is not a whole number"}
        council = places.council(cap.get("council", ""))
        return {"kind": "aggregate", "ref": ref, "cap": cap, "count": int(cap["aggregate_count"].replace(",", "")), "council": council,
                "rejections": rejections}
    if not name:
        return {"kind": "excluded", "ref": ref, "name": "", "reason": "no group name"}
    if PRODUCT_NAMES.search(name):
        return {"kind": "excluded", "ref": ref, "name": name, "reason": "a bank's group product, not a group"}
    cls = classify(cap)
    if not cls["identified"]:
        return {"kind": "excluded", "ref": ref, "name": name, "reason": cls["reason"]}
    council = places.council(cap.get("council", ""))
    if cap.get("council") and not council:
        notes.append(f"Council as published: '{cap['council']}' (not matched to a council of the government run; reviewed mapping needed).")
    ward_hit = places.ward(council, cap.get("ward", ""))
    # A ward the government run does not hold is kept as published (no point, no CDO route) for a reviewed spelling mapping.
    ward = ward_hit["ward"] if ward_hit else re.sub(r"(?i)^(kata ya|ward of)\s+|\s+(ward|kata)$", "", cap.get("ward", "")) if council else ""
    if cap.get("ward") and not ward_hit:
        notes.append(f"Ward as published: '{cap['ward']}' (not a ward of the government run for {council or 'an unknown council'}; "
                     "reviewed spelling mapping needed before the group is placed).")
    meeting = ""
    if cap.get("meeting_place_public"):
        place_kind = cap.get("meeting_place_kind", "")
        if place_kind == "home" or AV.HOME_PLACE.search(cap["meeting_place_public"]):
            rejections.append("meeting_place_public: rejected (a home)")
        elif place_kind in PUBLIC_VENUES or (not place_kind and VENUE_WORDS.search(cap["meeting_place_public"])):
            meeting = cap["meeting_place_public"]
        else:
            rejections.append("meeting_place_public: rejected (not shown to be a public venue)")
    member_count = cap.get("member_count", "")
    if member_count and not re.fullmatch(r"\d+", member_count):
        rejections.append("member_count: rejected (not a whole number)")
        member_count = ""
    for field, allowed in (("sponsor_kind", SPONSOR_KINDS), ("introducer_kind", INTRODUCER_KINDS)):
        if cap.get(field) and cap[field] not in allowed:
            rejections.append(f"{field}: '{cap[field]}' is not one of {list(allowed)}")
            cap[field] = ""
    introducer_kind, introducer_ref, basis_note = cap.get("introducer_kind", ""), cap.get("introducer_ref", ""), ""
    if not introducer_kind and kind == "council_extract" and council in places.council_office:
        introducer_kind, introducer_ref = "cdo_council", f"gov:{GOV_RUN}:{places.council_office[council]}"
        basis_note = "the council's Community Development division that supplied the register"
    if not introducer_kind and cap.get("sponsor_ref") and cap.get("sponsor_kind") in ("ngo", "bank"):
        introducer_kind = "ngo_field_office" if cap["sponsor_kind"] == "ngo" else "bank_branch"
        introducer_ref, basis_note = cap["sponsor_ref"], "the sponsoring organisation"
    if not introducer_kind and ward_hit:
        introducer_kind, introducer_ref = "cdo_ward", f"gov:{GOV_RUN}:{ward_hit['office_id']}"
        basis_note = "the ward Community Development Officer post in the government run (after the council's introduction)"
    if basis_note:
        notes.append(f"Introducer route: {basis_note}.")
    confirmed = cap.get("last_confirmed") or (cap.get("verified_on") if kind in CONFIRMS_ON_RECEIPT else cap.get("source_date", ""))
    if confirmed and not iso(confirmed):
        rejections.append("last_confirmed: not a date")
        confirmed = ""
    row = {"council": council, "ward": ward, "introducer_kind": introducer_kind, "last_confirmed": confirmed or "",
           "verified_on": confirmed or "0001-01-01"}
    status = AV.compute_status(row, as_of)
    missing = {"incomplete: name only": "council and ward, then an introducer route", "incomplete: no ward": "ward",
               "incomplete: no introducer route": "an introducer route",
               "stale: not confirmed in 12 months": "a confirmation within 12 months (newer source or the committee)"}.get(status, "")
    return {"kind": "group", "ref": ref, "cap": cap, "name": name, "council": council, "ward": ward, "ward_hit": ward_hit,
            "village": cap.get("village_or_mtaa", ""), "meeting": meeting, "member_count": member_count, "phone_basis": phone_basis,
            "introducer_kind": introducer_kind, "introducer_ref": introducer_ref, "last_confirmed": confirmed or "",
            "status": status, "missing": missing, "rejections": rejections, "notes": notes, **cls,
            "type_words": sorted({TYPE_WORDS[w] for w in re.findall(r"[a-z]+", fold(name)) if w in TYPE_WORDS}),
            "name_withheld_on_map": bool(PERSON_IN_NAME.search(name))}


# ------------------------------------------------------------------------------------------------------------- the build
def load_captures(captures: Path, gap_census: Path | None) -> tuple[list[dict], list[dict]]:
    caps, skipped = [], []
    for path in sorted(captures.glob("*.csv")) if captures.is_dir() else []:
        rows = read_csv(path)
        header = set(rows[0].keys()) if rows else set()
        if rows and "capture_kind" not in header:
            skipped.append({"file": rel(path), "reason": "not in the capture template (no capture_kind column)"})
            continue
        for i, r in enumerate(rows, 2):
            extra = sorted(set(r) - set(TEMPLATE_COLUMNS))
            r = {k: r.get(k, "") for k in TEMPLATE_COLUMNS}
            r.update({"_file": rel(path), "_line": i, "_dropped_columns": extra})
            caps.append(r)
    for path in sorted(captures.glob("council_news_*.jsonl")) if captures.is_dir() else []:
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            m = json.loads(line)
            if m.get("admitted") or m.get("aggregate_count"):
                r = {k: str(m.get(k, "") or "") for k in TEMPLATE_COLUMNS}
                r.update({"capture_kind": "council_news", "_file": rel(path), "_line": i, "_dropped_columns": []})
                caps.append(r)
    if gap_census and gap_census.is_dir():
        for path in sorted(gap_census.glob("vicoba_candidates_*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for i, f in enumerate(data.get("features", []), 1):
                caps.append({**{k: "" for k in TEMPLATE_COLUMNS}, "capture_id": f"osm:{f.get('osm_id', '')}", "capture_kind": "map_feature",
                             "group_name": f.get("name", ""), "group_type_as_published": f.get("name", ""), "council": f.get("council", ""),
                             "source_url": f.get("source_url", ""), "source_locator": f"feature {i}: {f.get('osm_id', '')}",
                             "acquired_on": data.get("retrieved", ""), "verified_on": data.get("retrieved", ""),
                             "evidence_excerpt": f"OpenStreetMap feature named '{f.get('name', '')}' ({f.get('osm_id', '')})",
                             "notes": "Map feature routed from the gap census: confirm it is a group (not a support provider) and find its ward; "
                                      "its mapped point is not stored, because a group's mapped point may be a home.",
                             "_file": rel(path), "_line": i, "_dropped_columns": []})
    return caps, skipped


def load_master_lists(master: Path | None) -> tuple[list[dict], list[dict], str]:
    """SACCOS and employers from a read-only master copy, for the SACCOS and workplace checks."""
    if not master or not Path(master).is_file():
        return [], [], "master not given or not found: SACCOS and workplace checks skipped"
    import sqlite3
    con = sqlite3.connect(f"file:{Path(master).as_posix()}?mode=ro", uri=True)
    rows = con.execute("SELECT organisation_id, name, segment, subtype, locality, address FROM organisations").fetchall()
    con.close()
    saccos = [{"id": r[0], "name": r[1], "place": f"{r[4] or ''} {r[5] or ''}"} for r in rows
              if r[2] == AV.SEGMENT and str(r[3] or "").startswith("SACCOS")]
    employers = [{"id": r[0], "name": r[1]} for r in rows if r[2] != AV.SEGMENT and not str(r[2] or "").startswith("Introducer")
                 and len(squash(r[1])) >= 8]
    return saccos, employers, f"read-only copy of the master ({Path(master).name}): {len(saccos)} SACCOS, {len(employers)} employers compared"


def base_key_name(name: str) -> str:
    return AV.key_name(name)


def merge(items: list[dict], common: set[str], saccos: list[dict], employers: list[dict]) -> list[dict]:
    """Exact key or registration number only; type-word conflicts kept apart; review signals for similar names, SACCOS, employers."""
    by_base = {}
    for it in items:
        by_base.setdefault((it["council"], it["ward"], base_key_name(it["name"])), []).append(it)
    for (council, ward, base), its in by_base.items():
        typed = {tuple(i["type_words"]) for i in its if i["type_words"]}
        conflict = len(typed) > 1
        for it in its:
            name_part = base + ("".join(it["type_words"]) if conflict and it["type_words"] else "")
            it["key"] = f"VIC|{council}|{ward}|{name_part}"
            it["type_conflict"] = conflict
    groups, by_key, by_reg = [], {}, {}
    for it in sorted(items, key=lambda i: (KIND_RANK[i["cap"]["capture_kind"]], i["ref"])):
        cap = it["cap"]
        reg = (VALIDATOR.norm(cap.get("registration_authority")), VALIDATOR.norm(cap.get("registration_number"))) if cap.get("registration_number") else None
        g = by_key.get(it["key"]) or (by_reg.get(reg) if reg else None)
        if g is None:
            g = {"key": it["key"], "organisation_id": AV.hid("O", "vicoba", it["key"]), "items": [], "alt_names": [], "reviews": []}
            groups.append(g)
            by_key[it["key"]] = g
        elif it["key"] != g["key"]:
            g["alt_names"].append(it["name"])
            g["reviews"].append({"kind": AV.CONFLICT_KIND,
                                 "field": "name", "values": f"{g['items'][0]['name']} / {it['name']}",
                                 "action": "Same registration number in one authority: one group; confirm the name the group uses."})
        g["items"].append(it)
        if reg:
            by_reg.setdefault(reg, g)
    # Group-level fields, conflicts, and review signals.
    single = ("village", "meeting", "member_count")
    capfields = ("meeting_cadence", "cycle_start_month", "share_out_month", "registration_number", "registration_authority", "sponsor_name",
                 "sponsor_kind", "sponsor_ref", "employer_ref")
    for g in groups:
        first = g["items"][0]
        g["name"] = first["name"]
        for f in single:
            vals = [i[f] for i in g["items"] if i[f]]
            if len({VALIDATOR.norm(v) for v in vals}) > 1:
                g["reviews"].append({"kind": AV.CONFLICT_KIND, "field": f, "values": " | ".join(dict.fromkeys(vals)),
                                     "action": "Two sources disagree: confirm the current value with the source or the committee."})
        for f in capfields:
            vals = [i["cap"].get(f) for i in g["items"] if i["cap"].get(f)]
            if len({VALIDATOR.norm(v) for v in vals}) > 1:
                g["reviews"].append({"kind": AV.CONFLICT_KIND, "field": f, "values": " | ".join(dict.fromkeys(vals)),
                                     "action": "Two sources disagree: confirm the current value with the source or the committee."})
        if first["type_conflict"]:
            g["reviews"].append({"kind": "VICOBA possible duplicate", "field": "name", "values": g["key"],
                                 "action": "Same name apart from Wanawake/Vijana in one ward: kept as separate groups; confirm they are."})
        # One introducer per group: a route a source states outranks a derived one (council division, sponsor, ward CDO), so two
        # sources of one group never disagree only because their derived routes differ.
        stated = [i for i in g["items"] if i["cap"].get("introducer_kind")]
        lead = (stated or [i for i in g["items"] if i["introducer_kind"]] or [first])[0]
        g["introducer"] = (lead["introducer_kind"], lead["introducer_ref"])
        for i in g["items"]:
            if not i["cap"].get("introducer_kind"):
                i["introducer_kind"], i["introducer_ref"] = g["introducer"]
        dates = [i["last_confirmed"] for i in g["items"] if i["last_confirmed"]]
        g["last_confirmed"] = max(dates) if dates else ""
        best = max(g["items"], key=lambda i: (bool(i["ward"]), bool(i["introducer_kind"]), i["last_confirmed"] or ""))
        g["status"] = AV.compute_status({"council": best["council"], "ward": best["ward"], "introducer_kind": best["introducer_kind"],
                                         "last_confirmed": g["last_confirmed"], "verified_on": g["last_confirmed"] or "0001-01-01"},
                                        AS_OF[0])
        g["women"] = any(i["women"] for i in g["items"])
        g["basis"] = next((i["basis"] for i in g["items"] if i["women"]), "")
        g["subtype"] = next((i["subtype"] for i in g["items"] if i["subtype"] == AV.DISABILITY_SUBTYPE), "") or \
            (AV.WOMEN_SUBTYPE if g["women"] else first["subtype"])
        vname = base_key_name(g["name"])
        for s in saccos:
            if AV.saccos_name(s["name"]) == vname and vname:
                token = AV.council_token(first["council"])
                place = fold(s["place"])
                if not token or not place.strip() or token in place:
                    g["reviews"].append({"kind": "VICOBA may be a registered SACCOS", "field": "name", "related_id": s["id"],
                                         "values": f"{g['name']} / {s['name']}", "action": "Groups graduate into SACCOS: a reviewer decides; never merged."})
        gname = f" {re.sub(r'[^a-z0-9]+', ' ', fold(g['name']))} "
        for e in employers:
            ename = re.sub(r"[^a-z0-9]+", " ", fold(e["name"])).strip()
            if len(ename.split()) >= 2 and f" {ename} " in gname and not any(i["cap"].get("employer_ref") for i in g["items"]):
                g["employer_candidate"] = e["id"]
                g["reviews"].append({"kind": "VICOBA introducer to confirm", "field": "employer_ref", "related_id": e["id"],
                                     "values": f"{g['name']} carries the employer name '{e['name']}'",
                                     "action": "Confirm this is the staff group of that employer; it then joins the employer's deal."})
                break
    # Similar names in one council (never merged; common names only on the full key).
    for i, a in enumerate(groups):
        na = base_key_name(a["name"])
        for b in groups[i + 1:]:
            ca, cb = a["items"][0]["council"], b["items"][0]["council"]
            if not ca or ca != cb or a["key"] == b["key"]:
                continue
            nb = base_key_name(b["name"])
            if na in common or nb in common:
                continue
            same = na == nb
            near = min(len(na), len(nb)) >= 5 and difflib.SequenceMatcher(None, na, nb).ratio() >= 0.85
            if same or near:
                a["reviews"].append({"kind": "VICOBA possible duplicate", "field": "name", "related_id": b["organisation_id"],
                                     "values": f"{a['key']} / {b['key']}",
                                     "action": "Decide whether these are one group; similar names are never merged automatically."})
    return groups


AS_OF = [date.today()]


def intake_header() -> list[str]:
    base = INTAKE_TEMPLATE.read_text(encoding="utf-8").splitlines()[0].split(",")
    return base + [c for c in AV.INTAKE_COLUMNS if c not in base]


def intake_rows(groups: list[dict], aggregates: list[dict], acquired: str) -> list[dict]:
    header = intake_header()
    rows = []
    for g in groups:
        for it in g["items"]:
            cap = it["cap"]
            basis, status = EVIDENCE[cap["capture_kind"]]
            w = it["ward_hit"]
            r = {h: "" for h in header}
            dist = float(w["distance_km"]) if w and w.get("distance_km") else None
            url = cap.get("source_url") if cap.get("source_url", "").startswith("http") else ""
            excerpt = words25(cap.get("evidence_excerpt") or f"{cap['capture_kind']} names the group '{it['name']}'")
            notes = " ".join([f"{g['status']}" + (f": missing {g['missing']}" if g.get("missing") else "") + ".",
                              *it["notes"], cap.get("notes", "")]).strip()
            r.update({
                "record_type": "organisation", "source_path": cap.get("source_path") or cap["_file"],
                "source_location": cap.get("source_locator") or f"{cap['_file']} line {cap['_line']}", "source_url": url,
                "source_date": cap.get("source_date", "") if iso(cap.get("source_date")) else "",
                "acquired_on": cap.get("acquired_on") or acquired, "verified_on": cap.get("verified_on") or acquired,
                "verification_status": status, "evidence_basis": basis, "evidence_excerpt": excerpt, "notes": notes[:1500],
                "organisation_name": it["name"], "segment": AV.SEGMENT, "subtype": g["subtype"],
                "campus": CAMPUS_LABEL.get(w["campus"], w["campus"]) if w else "", "distance_km": f"{dist:g}" if dist is not None else "",
                "radius_tier": RC.tier(dist) if dist is not None else "", "transport_band": RC.band(dist) if dist is not None else "",
                "geocode_precision": "ward" if w else "", "latitude": w["latitude"] if w else "", "longitude": w["longitude"] if w else "",
                "locality": ", ".join(x for x in (it["village"], f"{it['ward']} ward" if it["ward"] else "", it["council"]) if x) or
                            cap.get("council", ""),
                "size_evidence": f"about {it['member_count']} members, as published by the source" if it["member_count"] else "",
                "headcount": it["member_count"], "education_angle": AV.EDUCATION_ANGLE,
                "acquisition_track_id": "AQ00_RESEARCH_ONLY", "review_status": "research_only",
                "missing_information": g.get("missing", ""),
                "candidate_id": cap.get("capture_id") or f"{Path(cap['_file']).stem}:{cap['_line']}", "vicoba_group_key": g["key"],
                "council": it["council"], "ward": it["ward"], "village_or_mtaa": it["village"], "meeting_place_public": it["meeting"],
                "meeting_cadence": cap.get("meeting_cadence", ""), "cycle_start_month": cap.get("cycle_start_month", ""),
                "share_out_month": cap.get("share_out_month", ""), "member_count": it["member_count"],
                "registration_number": cap.get("registration_number", ""), "registration_authority": cap.get("registration_authority", ""),
                "sponsor_name": cap.get("sponsor_name", ""), "sponsor_kind": cap.get("sponsor_kind", ""), "sponsor_ref": cap.get("sponsor_ref", ""),
                "introducer_kind": it["introducer_kind"], "introducer_ref": it["introducer_ref"],
                "employer_ref": cap.get("employer_ref") or g.get("employer_candidate", ""), "record_status": g["status"],
                "last_confirmed": it["last_confirmed"] if iso(it["last_confirmed"]) else "",
                "women_group": "true" if g["women"] else "false", "women_group_basis": g["basis"] if g["women"] else "",
                "phone_basis": it["phone_basis"]})
            rows.append(r)
    for a in aggregates:
        cap = a["cap"]
        r = {h: "" for h in header}
        r.update({"record_type": "organisation", "source_path": cap.get("source_path") or cap["_file"],
                  "source_location": cap.get("source_locator") or f"{cap['_file']} line {cap['_line']}",
                  "source_url": cap.get("source_url") if cap.get("source_url", "").startswith("http") else "",
                  "acquired_on": cap.get("acquired_on") or acquired, "verified_on": cap.get("verified_on") or acquired,
                  "verification_status": EVIDENCE[cap["capture_kind"]][1], "evidence_basis": EVIDENCE[cap["capture_kind"]][0],
                  "evidence_excerpt": words25(cap.get("evidence_excerpt") or f"{a['count']} groups reported"),
                  "notes": f"Aggregate: {a['count']} groups reported ({cap.get('aggregate_area') or a['council'] or 'area as published'}); never a record.",
                  "organisation_name": f"{a['count']} savings groups reported: {cap.get('aggregate_area') or a['council'] or 'area as published'}",
                  "segment": AV.SEGMENT, "council": a["council"], "sponsor_name": cap.get("sponsor_name", ""),
                  "sponsor_kind": cap.get("sponsor_kind", ""), "sponsor_ref": cap.get("sponsor_ref", ""),
                  "candidate_id": cap.get("capture_id") or f"{Path(cap['_file']).stem}:{cap['_line']}",
                  "vicoba_groups_reported": str(a["count"]), "locality": cap.get("aggregate_area") or a["council"]})
        rows.append(r)
    return rows


def build(date_label: str, captures: Path, out: Path, gap_census: Path | None, master: Path | None, places: Places,
          extra_saccos=None, extra_employers=None) -> dict:
    caps, skipped = load_captures(captures, gap_census)
    common = AV.common_names()
    saccos, employers, master_note = load_master_lists(master)
    saccos += extra_saccos or []
    employers += extra_employers or []
    results = [process(c, places, AS_OF[0]) for c in caps]
    items = [r for r in results if r["kind"] == "group"]
    aggregates = [r for r in results if r["kind"] == "aggregate"]
    excluded = [{k: r[k] for k in ("ref", "name", "reason")} for r in results if r["kind"] == "excluded"]
    groups = merge(items, common, saccos, employers)
    for g in groups:
        g["missing"] = {"incomplete: name only": "council and ward, then an introducer route", "incomplete: no ward": "ward",
                        "incomplete: no introducer route": "an introducer route",
                        "stale: not confirmed in 12 months": "a confirmation within 12 months"}.get(g["status"], "")
        if g["status"].startswith("incomplete"):
            g["reviews"].append({"kind": "VICOBA record incomplete", "field": "record_status", "values": f"{g['status']}: missing {g['missing']}",
                                 "action": AV.NEXT_ACTION[g["status"]]})
        if g["status"].startswith("stale"):
            g["reviews"].append({"kind": "VICOBA stale", "field": "last_confirmed", "values": f"last confirmed {g['last_confirmed'] or 'not dated'}",
                                 "action": AV.NEXT_ACTION[g["status"]]})
    rows = intake_rows(groups, aggregates, date_label)
    out.mkdir(parents=True, exist_ok=True)
    intake = out / f"master_intake_{date_label}.csv"
    with intake.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=intake_header(), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    lines = []
    for g in groups:
        sources = [{"capture": i["ref"], "capture_kind": i["cap"]["capture_kind"], "source_url": i["cap"].get("source_url", ""),
                    "source_path": i["cap"].get("source_path", ""), "locator": i["cap"].get("source_locator", ""),
                    "source_date": i["cap"].get("source_date", ""), "acquired_on": i["cap"].get("acquired_on", ""),
                    "verified_on": i["cap"].get("verified_on", ""), "excerpt": words25(i["cap"].get("evidence_excerpt", ""))} for i in g["items"]]
        facts = []
        for n, i in enumerate(g["items"]):
            for field, value in (("ward", i["ward"]), ("council", i["council"]), ("village_or_mtaa", i["village"]),
                                 ("meeting_place_public", i["meeting"]), ("member_count", i["member_count"]),
                                 ("introducer_kind", i["introducer_kind"]), ("introducer_ref", i["introducer_ref"]),
                                 ("phone_basis", i["phone_basis"]), ("last_confirmed", i["last_confirmed"]),
                                 *[(f, i["cap"].get(f, "")) for f in ("meeting_cadence", "cycle_start_month", "share_out_month",
                                                                      "registration_number", "registration_authority", "registration_date",
                                                                      "sponsor_name", "sponsor_kind", "sponsor_ref", "employer_ref",
                                                                      "group_type_as_published")]):
                if value:
                    facts.append({"field": field, "value": value, "source": n})
        lines.append({"organisation_id": g["organisation_id"], "vicoba_group_key": g["key"], "name": g["name"], "alt_names": g["alt_names"],
                      "segment": AV.SEGMENT, "subtype": g["subtype"], "women_group": g["women"], "women_group_basis": g["basis"],
                      "name_withheld_on_map": any(i["name_withheld_on_map"] for i in g["items"]), "record_status": g["status"],
                      "missing": g["missing"], "last_confirmed": g["last_confirmed"], "sources_seen": len(g["items"]), "sources": sources,
                      "facts": facts, "review": g["reviews"],
                      "rejections": sorted({x for i in g["items"] for x in i["rejections"]}),
                      "dropped_columns": sorted({x for i in g["items"] for x in i["cap"].get("_dropped_columns", [])})})
    write_jsonl(out / f"groups_{date_label}.jsonl", lines)
    write_jsonl(out / f"aggregates_{date_label}.jsonl", [
        {"count": a["count"], "council": a["council"], "area": a["cap"].get("aggregate_area", ""), "sponsor_name": a["cap"].get("sponsor_name", ""),
         "sponsor_ref": a["cap"].get("sponsor_ref", ""), "fact": "vicoba_groups_reported", "source_url": a["cap"].get("source_url", ""),
         "locator": a["cap"].get("source_locator", ""), "source_date": a["cap"].get("source_date", ""), "capture": a["ref"]} for a in aggregates])
    report = {"date": date_label, "as_of": AS_OF[0].isoformat(), "captures": len(caps), "groups": len(groups), "intake_rows": len(rows),
              "aggregates": len(aggregates), "excluded": excluded, "skipped_files": skipped, "master": master_note,
              "by_status": {}, "by_subtype": {}, "women_groups": sum(1 for g in groups if g["women"]),
              "rejections": sum(len(i["rejections"]) for i in items),
              "review_signals": sum(len(g["reviews"]) for g in groups),
              "outputs": [rel(intake), rel(out / f"groups_{date_label}.jsonl"), rel(out / f"aggregates_{date_label}.jsonl")]}
    for g in groups:
        report["by_status"][g["status"]] = report["by_status"].get(g["status"], 0) + 1
        report["by_subtype"][g["subtype"]] = report["by_subtype"].get(g["subtype"], 0) + 1
    (out / f"build_report_{date_label}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return report


# ------------------------------------------------------------------------------------------------------------- council extract import
def header_target(header: str) -> str:
    h = " ".join(re.sub(r"[^a-z0-9]+", " ", fold(header)).split())
    for target, aliases in EXTRACT_ALIASES.items():
        if h in aliases:
            return target
    return ""


def import_extract(path: Path, council: str, received: str, letter: str, out_dir: Path, places: Places) -> tuple[Path, dict]:
    if path.suffix.lower() in (".xlsx", ".xlsm"):
        import openpyxl
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        table = [["" if v is None else str(v) for v in row] for row in ws.iter_rows(values_only=True)]
        header, body = table[0], table[1:]
    else:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            table = list(csv.reader(fh))
        header, body = table[0], table[1:]
    canonical = places.council(council) or council
    mapping, dropped = {}, {}
    for idx, h in enumerate(header):
        t = header_target(h)
        if t and t not in mapping.values() and (t == "group_name" or not PERSONAL_HEADER.search(fold(h))):
            mapping[idx] = t
        else:
            dropped[h or f"column {idx + 1}"] = {"values": sum(1 for r in body if idx < len(r) and str(r[idx]).strip()),
                                                 "why": "personal or financial column" if PERSONAL_HEADER.search(fold(h)) else "not on the allow-list"}
    slug = re.sub(r"[^a-z0-9]+", "-", fold(canonical)).strip("-")
    target = out_dir / f"council_extract_{slug}_{received}.csv"
    removed_values = 0
    rows = []
    for n, r in enumerate(body, 2):
        rec = {k: "" for k in TEMPLATE_COLUMNS}
        for idx, t in mapping.items():
            value = clean(r[idx]) if idx < len(r) else ""
            if PHONE.search(value):
                value, removed_values = PHONE.sub("", value).strip(" ,;:-"), removed_values + 1
            rec[t] = value
        if not any(rec.values()):
            continue
        rec.update({"capture_id": f"{slug}-{received}-{n}", "capture_kind": "council_extract", "council": canonical,
                    "registration_authority": f"{canonical} (Tier 4 community microfinance group register)" if rec["registration_number"] else "",
                    "source_path": rel(target), "source_locator": f"{path.name} row {n}", "acquired_on": received, "verified_on": received,
                    "last_confirmed": received,
                    "evidence_excerpt": f"{canonical} register extract (received {received}{', ' + letter if letter else ''}) lists the group",
                    "notes": f"Imported from the council's extract {path.name}; personal columns removed on import."})
        rows.append(rec)
    out_dir.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=TEMPLATE_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    log = {"source_file": path.name, "council": canonical, "received": received, "letter": letter, "rows": len(rows),
           "kept_columns": {header[i]: t for i, t in mapping.items()}, "dropped_columns": dropped,
           "phone_values_removed_from_kept_columns": removed_values,
           "note": "Column names and counts only; no dropped value was read into any output."}
    (target.with_suffix(".import-log.json")).write_text(json.dumps(log, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return target, log


# ------------------------------------------------------------------------------------------------------------- council news re-scan
NAME_TOKEN = r"[A-Z][A-Za-z'’\-]+"
GROUP_PATTERNS = [
    # 'Kikundi cha vijana cha Hakuna Matata Art', 'kikundi cha wanawake cha Upendo'
    re.compile(rf"[Kk]ikundi\s+cha\s+(?:vijana|wanawake|akina\s+mama|kina\s+mama|walemavu|wafugaji|wakulima)\s+(?:cha|wa)\s+((?:{NAME_TOKEN})(?:\s+{NAME_TOKEN}){{0,4}})"),
    # 'Kikundi cha Moisha Vijana Group', 'kikundi cha VICOBA Upendo'
    re.compile(rf"[Kk]ikundi\s+cha\s+((?:{NAME_TOKEN})(?:\s+(?:{NAME_TOKEN}|wa|ya|na|ni)){{0,5}})"),
    # 'Upendo VICOBA', 'Tumaini Women Group'
    re.compile(rf"((?:{NAME_TOKEN})(?:\s+{NAME_TOKEN}){{0,3}})\s+(?:VICOBA|Vicoba|VIKOBA|Vikoba|VSLA|Women'?s?\s+Group|Youth\s+Group|Group)\b"),
]
AGGREGATE = re.compile(r"(?:vikundi|groups?)\s+(\d[\d,\.]*)\b|(\d[\d,\.]*)\s+(?:vikundi|groups?)\b", re.I)
WARD_NEAR = re.compile(r"\bKata\s+ya\s+([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?)")
VILLAGE_NEAR = re.compile(r"\bKijiji\s+cha\s+([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?)")
NOT_GROUP = re.compile(r"\b(Limited|Ltd|Co|Corporation|Company|Engineering|Construction|Railway|Jeshi|Akiba|Halmashauri|Serikali|Wilaya|Mkoa|"
                       r"Kata|Kijiji|Mwenge|Shirika|Benki|Bank)\b")
PERSON_TITLE = re.compile(r"\b(Bw|Bi|Mhe|Dkt|Dr|Mwl|Prof|Ndg|Mr|Mrs|Ms)\.?\s", re.I)


def sentence_at(text: str, start: int, end: int) -> str:
    a = max(text.rfind(". ", 0, start), text.rfind("? ", 0, start), text.rfind("! ", 0, start))
    b = min([x for x in (text.find(". ", end), text.find("? ", end), text.find("! ", end)) if x != -1] or [len(text)])
    return text[a + 1:b + 1]


def scan_text(text: str) -> tuple[list[dict], list[dict]]:
    """Group mentions and aggregates in one news text. Only the group's own name words are kept; no person name is captured."""
    mentions, aggregates, seen = [], [], set()
    for pat in GROUP_PATTERNS:
        for m in pat.finditer(text):
            if m.start() > 0 and text[m.start() - 1].isalpha():
                continue                                    # 'mwanakikundi', 'wanakikundi': a member, not a group name
            name = clean(m.group(1))
            # Stop at a list of people ('Kihuba na <person> wa Kikundi ...') and at an administrative unit: only the group's words stay.
            name = re.split(r"\s+(?:na|ni)\s+|\s+wa\s+[Kk]ikundi\b|\s+(?:cha|wa|ya)\s+(?:Kata|Kijiji|Halmashauri|Wilaya|Mtaa)\b", name)[0]
            name = re.sub(r"\s+(wa|ya|na|ni|cha)$", "", name).strip(" -,")
            words = name.split()
            if not name or len(name) < 3 or NOT_GROUP.search(name) or PERSON_TITLE.search(name + " "):
                continue
            if len(words) >= 2 and name.isupper():
                continue                                    # a headline, not a name
            if not AV.key_name(name) or AV.key_name(name) in ("kikoba", "vsla", "ya", "vya") or \
                    all(w.lower() in ("vicoba", "vikoba", "kikoba", "vsla", "vya", "ya", "group") for w in words):
                continue                                    # a generic word, not a group's name
            if AV.key_name(name) in seen:
                continue
            seen.add(AV.key_name(name))
            full = text[m.start():m.end()]
            sent = sentence_at(text, m.start(), m.end())
            near = text[max(0, m.start() - 250): m.end() + 250]
            after = text[m.start(): m.end() + 1500]          # what the item goes on to say about the group, up to the next group
            nxt = re.search(rf"\b[Kk]ikundi\s+cha\s+(?!{re.escape(words[0])})[A-Z]", after[m.end() - m.start():])
            if nxt:
                after = after[: m.end() - m.start() + nxt.start()]
            backref = re.compile(r"\b(kikundi hicho|kikundi hiki|wanakikundi hao|wanakikundi hawa|wanakikundi)\b", re.I)
            sentences = re.split(r"(?<=[.!?])\s+", after)
            ward = WARD_NEAR.search(sent) or WARD_NEAR.search(near)
            village = VILLAGE_NEAR.search(sent) or VILLAGE_NEAR.search(near)
            marked = bool(SAVINGS_MARK.search(full) or SAVINGS_MARK.search(name))
            # Described as saving and lending: a sentence that refers back to this group ('kikundi hicho', 'wanakikundi hao'), uses a
            # savings-and-loan word, and names no other group.
            described = not marked and any(backref.search(s) and SAVINGS_MARK.search(s) and not re.search(r"kikundi cha|vikundi vya", s, re.I)
                                           for s in sentences)
            loan = bool(LOAN_10.search(sent) or re.search(r"\bmkopo|mikopo\b", sent, re.I))
            typ = "VICOBA" if marked else ("savings and loans as the item describes the group" if described else
                                           "10% loan group" if loan else "group")
            for word, label in (("wanawake", "women's group"), ("vijana", "youth group"), ("walemavu", "group of people with disabilities")):
                if re.search(rf"\b{word}\b", full, re.I):
                    typ += f"; {label} (as written)"
            women = re.search(r"\b(wanawake wa kikundi|kikundi cha wanawake|akina mama wa kikundi|women'?s group)\b", near + " " + after, re.I)
            members = re.search(r"\bwanachama\s+(\d{1,3})\b|\b(\d{1,3})\s+wanachama\b", after)
            admitted = marked or described
            mentions.append({"group_name": name, "ward": ward.group(1) if ward else "", "village_or_mtaa": village.group(1) if village else "",
                             "group_type_as_published": typ, "admitted": admitted,
                             "women_group_evidence": "the news item calls its members women ('wanawake wa kikundi')" if women else "",
                             "member_count": (members.group(1) or members.group(2)) if members and admitted else "",
                             "reason": "" if admitted else ("council 10% loan group reported in the news, not identified as a savings-and-loan group"
                                                            if loan else "not identified as a savings-and-loan group")})
    seen_aggs = set()
    for m in AGGREGATE.finditer(text):
        raw = (m.group(1) or m.group(2) or "").replace(",", "")
        if not re.fullmatch(r"\d+", raw) or int(raw) < 2:
            continue
        sent = sentence_at(text, m.start(), m.end())
        if not SAVINGS_MARK.search(sent):
            continue
        ward = WARD_NEAR.search(sent)
        k = (int(raw), ward.group(1) if ward else "")
        if k in seen_aggs:
            continue
        seen_aggs.add(k)
        aggregates.append({"aggregate_count": k[0], "ward": k[1], "group_type_as_published": "VICOBA or savings groups (aggregate)"})
    return mentions, aggregates


def rescan(sites_dir: Path, cache_root: Path, out: Path, date_label: str, places: Places) -> dict:
    lines, items_read, missing = [], 0, 0
    seen_items = set()
    for cap_path in sorted(sites_dir.glob("*.json")):
        cap = json.loads(cap_path.read_text(encoding="utf-8"))
        host, retrieved = cap.get("host", ""), cap.get("retrieved", "")
        council = places.host_council.get(host, "")
        caches = [cache_root / f"http-cache-{retrieved}", cache_root / "http-cache"]
        for kind in ("news", "announcements"):
            for url in sorted({n.get("listing_url") for n in cap.get(kind, []) if n.get("listing_url")}):
                body = None
                for c in caches:
                    f = c / (hashlib.sha256((url + "\n").encode()).hexdigest() + ".bin")
                    if f.is_file():
                        body = f.read_bytes()
                        break
                if body is None:
                    missing += 1
                    continue
                for it in json.loads(body).get("data", []):
                    key = (host, kind, it.get("id"))
                    if key in seen_items:
                        continue
                    seen_items.add(key)
                    items_read += 1
                    text = clean(html.unescape(re.sub(r"<[^>]+>", " ", f"{it.get('title') or ''}. {it.get('content') or ''}")))
                    mentions, aggs = scan_text(text)
                    loc = f"{host} {kind} id {it.get('id')} ({str(it.get('date') or '')[:10]})"
                    base = {"council": council, "host": host, "item_kind": kind, "item_id": it.get("id"), "source_url": url,
                            "source_path": rel(cap_path), "source_locator": loc, "source_date": str(it.get("date") or "")[:10],
                            "acquired_on": retrieved, "verified_on": date_label, "in_catchment_council": council in CATCHMENT_COUNCILS}
                    for mnt in mentions:
                        if not mnt["admitted"]:
                            # Not a VICOBA candidate (mostly council 10% loan groups): the name is not kept, so the repository never
                            # compiles a list of loan recipients; the line records only that a mention was seen and why it was left out.
                            mnt.update({"group_name": "(withheld: not admitted)", "ward": "", "village_or_mtaa": "", "member_count": "",
                                        "women_group_evidence": ""})
                        mnt["evidence_excerpt"] = (f"Council news item {it.get('id')} ({base['source_date']}) names the group '{mnt['group_name']}'"
                                                   + (f" in {mnt['ward']} ward" if mnt["ward"] else "") + f"; type as written: {mnt['group_type_as_published']}")
                        lines.append({"kind": "mention", **base, **mnt, "capture_id": f"news:{host}:{it.get('id')}:{squash(mnt['group_name'])}"})
                    for a in aggs:
                        lines.append({"kind": "aggregate", **base, **a, "aggregate_area": f"{a['ward'] + ' ward, ' if a['ward'] else ''}{council or host}",
                                      "evidence_excerpt": f"Council news item {it.get('id')} ({base['source_date']}) reports {a['aggregate_count']} VICOBA or savings groups",
                                      "capture_id": f"news:{host}:{it.get('id')}:agg{a['aggregate_count']}"})
    path = out / f"council_news_{date_label}.jsonl"
    write_jsonl(path, lines)
    ment = [x for x in lines if x["kind"] == "mention"]
    return {"file": rel(path), "news_items_read": items_read, "listing_pages_not_in_cache": missing, "group_mentions": len(ment),
            "admitted": sum(1 for x in ment if x["admitted"]),
            "admitted_in_catchment_councils": sum(1 for x in ment if x["admitted"] and x["in_catchment_council"]),
            "not_admitted_by_reason": {r: sum(1 for x in ment if x["reason"] == r) for r in sorted({x["reason"] for x in ment if not x["admitted"]})},
            "aggregates": sum(1 for x in lines if x["kind"] == "aggregate")}


# ------------------------------------------------------------------------------------------------------------- introducers
INTRODUCER_SEGMENT = "Introducer: savings-group network"


def introducers(path: Path, date_label: str, out: Path) -> dict:
    """Introducer research records -> master intake rows (new organisations) and fact lines (organisations already held)."""
    records = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    header = intake_header()
    rows, facts = [], []
    for n, rec in enumerate(records, 1):
        src = rec.get("sources") or []
        prog = rec.get("programme") or {}
        if rec.get("existing"):
            ex = rec["existing"]
            for f in rec.get("facts") or []:
                facts.append({"db": ex["db"], "organisation_id": ex["organisation_id"], "organisation_name": ex["name"],
                              "also_ids": ex.get("also_ids", []), "field": f["field"], "value": f["value"], "source_url": f["source_url"],
                              "accessed_on": f["accessed_on"], "fetched": f.get("fetched", True), "excerpt": words25(f.get("excerpt", "")),
                              "verification_status": f.get("verification_status", "verified"), "review": f.get("review", ""),
                              "research_file": rel(path), "line": n})
            continue
        loc = rec.get("location") or {}
        email = next((e["value"] for e in rec.get("emails") or [] if e.get("source_url")), "")
        phone = next((p["value"] for p in rec.get("phones") or [] if p.get("source_url")), "")
        route_src = next((e.get("source_url") for e in (rec.get("emails") or []) + (rec.get("phones") or []) if e.get("source_url")), "")
        dist = loc.get("distance_km")
        missing = rec.get("missing") or ([] if (email or phone) else ["a published route (email or phone)"])
        main = src[0] if src else {}
        r = {h: "" for h in header}
        r.update({"record_type": "organisation", "source_path": rel(path), "source_location": f"line {n}: {rec['name']}",
                  "source_url": main.get("url", ""), "source_date": main.get("source_date", ""),
                  "acquired_on": main.get("accessed_on", date_label), "verified_on": date_label,
                  "verification_status": rec.get("verification_status", "needs_review"), "evidence_basis": main.get("basis", "official"),
                  "evidence_excerpt": words25(prog.get("excerpt") or main.get("excerpt", "")),
                  "notes": " ".join(x for x in [f"Savings-group programme: {prog.get('claim', '')} ({prog.get('source_url', '')}, read {prog.get('accessed_on', '')})."
                                                if prog else "", f"Routes from {route_src}." if route_src else "No published route found.",
                                                rec.get("notes", "")] if x)[:1500],
                  "organisation_name": rec["name"], "organisation_domain": rec.get("domain", ""), "segment": INTRODUCER_SEGMENT,
                  "subtype": rec.get("subtype", ""), "campus": loc.get("campus", ""), "distance_km": f"{dist:g}" if dist is not None else "",
                  "radius_tier": RC.tier(dist) if dist is not None else "", "transport_band": RC.band(dist) if dist is not None else "",
                  "geocode_precision": loc.get("precision", ""), "latitude": loc.get("latitude", ""), "longitude": loc.get("longitude", ""),
                  "locality": loc.get("locality", ""), "address": rec.get("address", ""), "website": rec.get("website", ""),
                  "public_email": email, "public_phone": phone, "channel_attribution": route_src,
                  "education_angle": "Introducer: could introduce Silverleaf to the savings groups it works with (a talk at their weekly meeting); "
                                     "never a member list",
                  "acquisition_track_id": "AQ00_RESEARCH_ONLY", "review_status": "research_only", "missing_information": "; ".join(missing),
                  "candidate_id": rec.get("candidate_id", f"VIC-INT-{n:02d}")})
        rows.append(r)
    out.mkdir(parents=True, exist_ok=True)
    extra = ["candidate_id", "subsegment", "candidate_source", "google_maps_url", "maps_lookup", "fit_reason"]
    cols = INTAKE_TEMPLATE.read_text(encoding="utf-8").splitlines()[0].split(",") + extra
    for r in rows:
        r["subsegment"], r["candidate_source"] = INTRODUCER_SEGMENT, "vicoba_introducer_research"
        r["maps_lookup"] = "yes" if not r["public_phone"] else ""
        r["fit_reason"] = r["education_angle"]
    intake = out / f"introducers_intake_{date_label}.csv"
    with intake.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    write_jsonl(out / f"introducer_facts_{date_label}.jsonl", facts)
    return {"intake": rel(intake), "new_organisations": len(rows), "with_route": sum(1 for r in rows if r["public_email"] or r["public_phone"]),
            "fact_lines": len(facts), "facts_file": rel(out / f"introducer_facts_{date_label}.jsonl")}


# ------------------------------------------------------------------------------------------------------------- self-test
def self_test() -> int:
    places = Places()
    failures = []

    def check(cond, what):
        if not cond:
            failures.append(what)

    # 1. Name normalisation and the key (add_vicoba_groups.py's own functions).
    check(AV.key_name("Kikundi cha Wanawake Upendo VICOBA") == "upendo", "key_name strips decision 2b's words")
    check(AV.key_name("Upendo VSLA") == "upendovsla", "VSLA is not stripped")
    check(places.council("Halmashauri ya Jiji la Arusha") == "Arusha City Council" and places.council("Meru DC") == "Meru District Council",
          "council aliases resolve")
    check(places.council("Arusha") == "", "'Arusha' alone is ambiguous and never resolved")
    check((places.ward("Arusha City Council", "Kata ya Kaloleni") or {}).get("ward") == "Kaloleni", "ward lookup strips 'Kata ya'")
    # 2. The fixture build.
    tmp = Path(tempfile.mkdtemp(prefix="vicoba-selftest-"))
    try:
        caps = tmp / "captures"
        caps.mkdir()
        shutil.copy(FIXTURES / "selftest_captures.csv", caps / "selftest_captures.csv")
        target, log = import_extract(FIXTURES / "selftest_council_extract.csv", "Halmashauri ya Wilaya ya Meru", "2026-10-01", "fixture letter",
                                     caps, places)
        check("Jina la Mwenyekiti" in log["dropped_columns"] and "Simu ya Mwenyekiti" in log["dropped_columns"]
              and "Majina ya Wanachama" in log["dropped_columns"], "personal columns are dropped on import")
        check(log["phone_values_removed_from_kept_columns"] == 1, "a phone in a kept column is removed")
        imported = target.read_text(encoding="utf-8")
        check("Fixture Person" not in imported and "0712" not in imported, "no personal value reaches the capture file")
        AS_OF[0] = date(2026, 10, 13)
        report = build("selftest", caps, tmp / "out", None, None, places,
                       extra_saccos=[{"id": "Ofixturesacc1", "name": "Ilboru Jitambue SACCOS Ltd", "place": "Arusha"}],
                       extra_employers=[{"id": "Ofixtureemp01", "name": "Fixture Brewers"}])
        groups = [json.loads(l) for l in (tmp / "out" / "groups_selftest.jsonl").read_text(encoding="utf-8").splitlines()]
        by = {g["name"]: g for g in groups}
        allnames = {n for g in groups for n in [g["name"], *g["alt_names"]]}
        g = by.get("Kikundi cha Wanawake Upendo VICOBA")
        check(g and g["sources_seen"] == 2 and g["vicoba_group_key"] == "VIC|Arusha City Council|Kaloleni|upendo",
              "exact key: two sources, one group, key as admin_units spell it")
        check(g and g["women_group"] and g["women_group_basis"] == "name" and g["subtype"] == "VICOBA — women's group", "women tag from the name")
        check(g and g["record_status"] == "complete", "complete: ward, introducer route, confirmed within 12 months")
        reg = [x for x in groups if "Tegemeo Mlangarini" in x["name"] or "Tegemeo Mlangarini" in " ".join(x["alt_names"])]
        check(len(reg) == 1 and reg[0]["sources_seen"] == 2, "registration number within one authority merges a spelling variant")
        umoja = [x for x in groups if x["name"].startswith("Umoja")]
        check(len(umoja) == 2 and not any(r["kind"] == "VICOBA possible duplicate" for x in umoja for r in x["review"]),
              "common names never fuzzy-match across wards")
        jit = [x for x in groups if x["name"].startswith(("Jitambue", "Jitambuwe"))]
        check(len(jit) >= 2 and any(r["kind"] == "VICOBA possible duplicate" for x in jit for r in x["review"]),
              "a same-council name variant goes to review, never merged")
        sac = by.get("Ilboru Jitambue VICOBA")
        check(sac and any(r["kind"] == "VICOBA may be a registered SACCOS" for r in sac["review"]), "a SACCOS name overlap goes to review")
        emp = by.get("Fixture Brewers Staff VICOBA")
        check(emp and any(r["field"] == "employer_ref" for r in emp["review"]), "a workplace group gets an employer candidate and a review")
        check("25 savings groups reported" not in allnames and report["aggregates"] == 1, "an aggregate is not turned into a record")
        stale = by.get("Faraja Ngarenaro VICOBA")
        check(stale and stale["record_status"] == "stale: not confirmed in 12 months", "stale after 12 months")
        noward = by.get("Neema Hai VICOBA")
        check(noward and noward["record_status"] == "incomplete: no ward", "council only: incomplete, no ward")
        nameonly = by.get("Mshikamano Kaskazini VICOBA")
        check(nameonly and nameonly["record_status"] == "incomplete: name only", "no council: incomplete, name only")
        noroute = by.get("Kilimo Bora VICOBA")
        check(noroute and noroute["record_status"] == "incomplete: no introducer route", "unplaced ward and no sponsor: no introducer route")
        home = by.get("Tupendane Sekei VICOBA")
        check(home and "meeting_place_public: rejected (a home)" in home["rejections"] and
              not any(f["field"] == "meeting_place_public" for f in home["facts"]), "a home meeting place is rejected")
        unsourced = by.get("Juhudi Themi VICOBA")
        check(unsourced and any(x.startswith("role_phone: rejected") for x in unsourced["rejections"]), "an unsourced phone is rejected")
        published = by.get("Baraka Kati VICOBA")
        check(published and any(f["field"] == "phone_basis" and f["value"] == "published_for_role" for f in published["facts"]),
              "a published-for-role phone keeps only its basis")
        mama = by.get("Mama Neema Group VICOBA")
        check(mama and mama["women_group"] and mama["name_withheld_on_map"], "a name embedding a person is tagged for withholding on the map")
        youth = by.get("Vijana Imara VICOBA")
        check(youth and youth["subtype"] == "VICOBA — youth group" and not youth["women_group"], "youth subtype; not a women's group")
        dis = [x for x in groups if x["subtype"] == "VICOBA — group of people with disabilities"]
        check(len(dis) == 1 and dis[0]["name"] == "Tuinuane Walemavu VICOBA", "disability subtype only when the council supplies it as such")
        sour = by.get("Kazi Njema VSLA")
        check(sour and sour["women_group"] and sour["women_group_basis"] == "source_says", "women tag when the source calls it a women's group")
        mixed = by.get("Mwangaza Usa VICOBA")
        check(mixed and not mixed["women_group"] and mixed["subtype"] == "VICOBA — mixed or unspecified", "no evidence, no tag")
        tw = [x for x in groups if x["name"] in ("Upendo Wanawake Sekei VICOBA", "Upendo Vijana Sekei VICOBA")]
        check(len(tw) == 2 and len({x["vicoba_group_key"] for x in tw}) == 2, "type-word conflict keeps both groups")
        ex = {e["name"]: e["reason"] for e in report["excluded"]}
        check(any("10% loan" in n or "not identified" in r for n, r in ex.items()), "a group not identified as savings-and-loan is excluded")
        check("Upatu Wema" in ex, "a rotating group is excluded")
        intake = tmp / "out" / "master_intake_selftest.csv"
        text = intake.read_text(encoding="utf-8") + (tmp / "out" / "groups_selftest.jsonl").read_text(encoding="utf-8")
        check(not PHONE.search(text), "no phone number in any output")
        check("Fixture Person" not in text and "Home of" not in text and "nyumbani" not in text.lower(), "no person or home in any output")
        v = VALIDATOR.validate(intake)
        check(v["status"] == "valid", f"validate_intake.py passes ({v['error_count']} errors)")
        header = intake.read_text(encoding="utf-8").splitlines()[0].split(",")
        check(header[-len(AV.INTAKE_COLUMNS):] == list(AV.INTAKE_COLUMNS), "intake header ends with add_vicoba_groups.INTAKE_COLUMNS")
        rows = read_csv(intake)
        check(all(not AV.contract_issues(r) for r in rows if not r["vicoba_groups_reported"]), "every group row meets add_vicoba_groups' contract")
        check(all(r["public_phone"] == "" and r["public_email"] == "" for r in rows), "no group row carries a phone or an email")
        # 3. The news re-scan on a synthetic text: person names never captured; 10% loan groups not admitted; aggregates counted.
        mentions, aggs = scan_text("Bi. Fixture Person wa kikundi cha Kilele cha Kata ya Kati amepata mkopo wa asilimia 10. "
                                   "Kikundi cha Upendo VICOBA cha Kata ya Sekei kimeanza. Shirika limeanzisha vikundi 25 vya VICOBA katika Kata ya Kati. "
                                   "Wanufaika akiwemo Fixture Other wa kikundi cha Kisima na Fixture Third wa Kikundi cha Mlima wamesema mikopo imesaidia. "
                                   "Naye mwanakikundi cha VICOBA, Fixture Fourth, amesema. Shamba la Kikundi cha Nyota kilichopo Kata ya Themi. "
                                   "Wanawake wa kikundi hicho wanajihusisha na mfumo wa Kikoba, unaowawezesha kuweka na kukopa fedha.")
        names = [m["group_name"] for m in mentions]
        check("Upendo VICOBA" in names or "Upendo" in names, "a VICOBA-named group is found")
        check(not any("Fixture" in n or "Person" in n or "Other" in n or "Third" in n or "Fourth" in n for n in names),
              "no person name is captured")
        nyota = [m for m in mentions if m["group_name"] == "Nyota"]
        check(nyota and nyota[0]["admitted"] and nyota[0]["women_group_evidence"],
              "a group the item describes as saving and lending is admitted, with the item's women's-group wording")
        check(any(not m["admitted"] and "10% loan" in m["reason"] for m in mentions), "a 10% loan group is not admitted")
        check(any(a["aggregate_count"] == 25 for a in aggs), "an aggregate count is captured")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    result = {"self_test": "passed" if not failures else "failed", "failures": failures}
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0 if not failures else 1


# ------------------------------------------------------------------------------------------------------------- main
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="date stamp of the outputs")
    parser.add_argument("--as-of", help="date for the 12-month staleness rule (default: --date)")
    parser.add_argument("--captures", type=Path, default=CAPTURES)
    parser.add_argument("--out", type=Path, default=RAW)
    parser.add_argument("--gap-census", type=Path, default=GAP_CENSUS, help="folder with vicoba_candidates_<date>.json")
    parser.add_argument("--master", type=Path, default=MASTER, help="read-only master copy for the SACCOS and workplace checks")
    parser.add_argument("--import-extract", type=Path)
    parser.add_argument("--council")
    parser.add_argument("--received")
    parser.add_argument("--letter", default="")
    parser.add_argument("--rescan-council-news", action="store_true")
    parser.add_argument("--council-sites", type=Path, default=COUNCIL_SITES)
    parser.add_argument("--cache-root", type=Path, default=GOV_CACHE)
    parser.add_argument("--introducers", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.self_test:
        return self_test()
    AS_OF[0] = date.fromisoformat(args.as_of or args.date)
    places = Places()
    if args.import_extract:
        if not (args.council and args.received):
            parser.error("--import-extract needs --council and --received")
        target, log = import_extract(args.import_extract, args.council, args.received, args.letter, args.captures, places)
        print(json.dumps({"capture": rel(target), **{k: v for k, v in log.items() if k != "kept_columns"}}, indent=1, ensure_ascii=False))
        return 0
    if args.rescan_council_news:
        print(json.dumps(rescan(args.council_sites, args.cache_root, args.captures, args.date, places), indent=1, ensure_ascii=False))
        return 0
    if args.introducers:
        print(json.dumps(introducers(args.introducers, args.date, args.out), indent=1, ensure_ascii=False))
        return 0
    report = build(args.date, args.captures, args.out, args.gap_census, args.master, places)
    print(json.dumps({k: v for k, v in report.items() if k != "excluded"} | {"excluded": len(report["excluded"])}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
