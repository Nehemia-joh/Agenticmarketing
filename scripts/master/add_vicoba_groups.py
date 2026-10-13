#!/usr/bin/env python3
"""Add VICOBA and VSLA savings groups to the company master (one transaction), as group-level records with no personal data.

Decided 13 October 2026 (docs/plans/vicoba-integration-plan.md, "Decisions taken" and section 0): VICOBAs live in the master as a
subsegment of savings groups (segment 'Savings group', subtype 'VICOBA — ...' or 'VSLA — NGO-programme group'), group-level records
only, and OF07 (the group rate) applies to them. The shared contract is section 4.1 of that plan, with section 0's subtypes and the
fact 'women_group'; the intake columns are documented in skills/silverleaf-create-lead-list/references/lead-list-data-contract.md
("VICOBA intake").

Reads data/raw/vicoba/master_intake_<date>.csv (written by scripts/collection/build_vicoba_intake.py), or --intake <csv>. It runs the
create skill's validate_intake.py and the update skill's preflight_update.py on it first (CLAUDE.md, 'Required order') and stops if
either fails.

For every row:
- a row with 'vicoba_groups_reported' is an aggregate ("25 groups formed in Longido"), never a group: the count becomes the fact
  'vicoba_groups_reported' on the sponsor organisation named in 'sponsor_ref' when that is a master organisation, otherwise it is only
  reported;
- a row that breaks the contract (wrong segment or label, no area named, outside Tanzania, a contact or enquiry row) is quarantined
  with its reason;
- the group is matched, in order, by 'vicoba_group_key' (VIC|<council>|<ward>|<normalised name>), by registration number within one
  registration authority, and by the preflight's exact name plus locality when that hits a VICOBA record. A match adds the row's
  source record, entity_sources link and new facts to the existing group; a differing value becomes a 'Multiple source values'
  review item and never overwrites. An exact hit on a record that is not a VICOBA is never merged;
- otherwise a new organisation is inserted with ID hid("O", "vicoba", vicoba_group_key), its subtype, campus, distance, band, tier,
  ward-level point and locality, one source record, an entity_sources link, the contract's facts (women_group always, 'true' only on
  source evidence), and one outreach plan (segment 'VICOBA members', 'Needs research', AQ00, language 'sw') whose copy
  draft_master_messages.py writes later.

Privacy (decision 3): a VICOBA organisation never gets a phone or an email. Phone, email, contact-name and enquiry columns are
withheld: they are blanked in the stored source record and in the stored copy of the intake, and only their count is reported; a
'phone_basis' (published_for_role, or consent_recorded <date>) is kept as a fact without the number, for the contact path
(scripts/master/link_vicoba_introducers.py). A meeting place that reads as a home is withheld the same way. No contacts are written.

Review items (kinds from the contract): 'VICOBA record incomplete', 'VICOBA stale', 'VICOBA possible duplicate' (same council, the
same or a near-identical normalised name, a different key; common names in data/reference/vicoba-common-names.json never produce
one), 'VICOBA may be a registered SACCOS' (a SACCOS of the same normalised name in the same council: never merged),
'VICOBA introducer to confirm' (a route or sponsor named but not linked, or a link that does not resolve), and 'Multiple source
values'.

The schema step adds the outreach_plans columns 'language' and 'english_meaning' (decision 6) and the outreach segments
'VICOBA members' and 'VICOBA introducers'; '--schema-only --apply' runs it alone, for a database copy that later tasks draft on.

Preview by default (runtime/master/vicoba-preview-<intake>.json); --apply writes in one transaction and rolls back on any failed
check. A re-run of the same intake adds nothing. Afterwards, in order:
  python scripts/master/link_vicoba_introducers.py --apply
  python scripts/messaging/draft_master_messages.py; python scripts/master/refresh_acquisition_metadata.py
  python scripts/master/export_master_workbook_data.py; npm run build:workbook; python scripts/master/verify_master.py

Later tasks read the groups with load_vicoba_groups(con) and order a wave with wave_order(groups): women's groups first.
"""
from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import io
import json
import re
import sqlite3
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "vicoba"
WORK = ROOT / "runtime" / "master"
VALIDATOR = ROOT / "skills" / "silverleaf-create-lead-list" / "scripts" / "validate_intake.py"
PREFLIGHT = ROOT / "skills" / "silverleaf-update-lead-list" / "scripts" / "preflight_update.py"
COMMON_NAMES_FILE = ROOT / "data" / "reference" / "vicoba-common-names.json"

# --- The shared contract (vicoba-integration-plan.md section 4.1, with section 0's subtypes and women_group) -------------------
SEGMENT = "Savings group"
SUBTYPES = (
    "VICOBA — women's group",
    "VICOBA — mixed or unspecified",
    "VICOBA — youth group",
    "VICOBA — group of people with disabilities",
    "VSLA — NGO-programme group",
)
DEFAULT_SUBTYPE = "VICOBA — mixed or unspecified"
WOMEN_SUBTYPE = "VICOBA — women's group"
DISABILITY_SUBTYPE = "VICOBA — group of people with disabilities"
OUTREACH_SEGMENTS = ("VICOBA members", "VICOBA introducers")
GROUP_SEGMENT = "VICOBA members"
PRECISIONS = ("ward", "point")
RECORD_STATUSES = (
    "complete",
    "incomplete: no ward",
    "incomplete: no introducer route",
    "incomplete: name only",
    "stale: not confirmed in 12 months",
)
SPONSOR_KINDS = ("ngo", "bank", "church", "mosque", "council", "employer", "other")
INTRODUCER_KINDS = ("cdo_ward", "cdo_council", "ngo_field_office", "bank_branch", "faith_office", "group_published")
WOMEN_BASES = ("name", "source_says", "council_women_loan_group")
REVIEW_KINDS = ("VICOBA record incomplete", "VICOBA stale", "VICOBA possible duplicate", "VICOBA may be a registered SACCOS",
                "VICOBA introducer to confirm")
CONFLICT_KIND = "Multiple source values"
PLAN_COLUMNS = ("language", "english_meaning")
FACT_FIELDS = ("vicoba_group_key", "ward", "council", "village_or_mtaa", "meeting_place_public", "meeting_cadence", "cycle_start_month",
               "share_out_month", "member_count", "registration_number", "registration_authority", "sponsor_name", "sponsor_kind",
               "sponsor_ref", "introducer_kind", "introducer_ref", "employer_ref", "covers_groups", "record_status", "last_confirmed",
               "sources_seen", "phone_basis", "vicoba_groups_reported", "women_group")
# The VICOBA columns of the intake, after the shared template's columns. sources_seen is written by this script (one per source);
# covers_groups belongs to introducer plans (draft_master_messages.py), so neither is an intake column.
INTAKE_COLUMNS = ("candidate_id", "vicoba_group_key", "council", "ward", "village_or_mtaa", "meeting_place_public", "meeting_cadence",
                  "cycle_start_month", "share_out_month", "member_count", "registration_number", "registration_authority",
                  "sponsor_name", "sponsor_kind", "sponsor_ref", "introducer_kind", "introducer_ref", "employer_ref", "record_status",
                  "last_confirmed", "women_group", "women_group_basis", "phone_basis", "vicoba_groups_reported")
# Facts compared across sources: a differing value is a 'Multiple source values' item, never an overwrite.
SINGLE_VALUED = ("ward", "council", "village_or_mtaa", "meeting_place_public", "meeting_cadence", "cycle_start_month", "share_out_month",
                 "member_count", "registration_number", "registration_authority", "sponsor_name", "sponsor_kind", "sponsor_ref",
                 "introducer_kind", "introducer_ref", "employer_ref")
# Withheld from every VICOBA record (decision 3c and the user's decision of group-level records only).
PHONE_COLUMNS = ("public_phone", "organisation_phone", "role_phone", "enquiry_phone")
PERSONAL_COLUMNS = PHONE_COLUMNS + ("public_email", "shared_email", "published_role_email", "named_email", "enquiry_email",
                                    "contact_name", "enquiry_author", "profile_url")
HOME_PLACE = re.compile(r"\b(nyumbani|home|house|residence|homestead|compound|private)\b|\bkwa\s+(mama|baba|mzee|bibi|bwana|mwenyekiti|katibu)\b",
                        re.I)
WOMEN_NAME = re.compile(r"\b(wanawake|akina\s+mama|kina\s+mama|women|mama)\b", re.I)
KEY_RE = re.compile(r"^VIC\|[^|]*\|[^|]*\|[^|]+$")
MASTER_ID = re.compile(r"^O[0-9a-f]{12}$")
RUN_REF = re.compile(r"^(gov|welfare):[a-z0-9\-]+:[A-Za-z0-9_\-]+$")
CONSENT = re.compile(r"^consent_recorded \d{4}-\d{2}-\d{2}$")
TANZANIA = (-11.8, -0.9, 29.3, 40.5)  # lat min, lat max, lon min, lon max
# Removed from the name for the key only (decision 2b); the record keeps the published name.
KEY_STOPWORDS = ("women group", "kikundi cha", "vicoba", "vikoba", "kikundi", "group", "wanawake", "vijana")
BUILTIN_COMMON = ("upendo", "tumaini", "umoja", "mshikamano", "juhudi", "faraja", "neema", "amani")
SACCOS_STOPWORDS = ("savings and credit cooperative society", "savings and credit co operative society", "saccos", "sacco", "limited",
                    "ltd", "cooperative", "co operative", "society")
STRATEGY_ID = "Safd376f9d269"  # 'Savings-group partnerships', segment 'SACCOS / VICOBA'
MESSAGE_STRATEGY = "S-request-first-v5"
MESSAGE_STATUS = "Draft - not sent; request-first review"
ACQUISITION_VERSION = "2026-09-09-new-contact-acquisition-v4"
VALUE_MODULES = "VM02; VM03; VM06; VM20"
NATIVE_REVIEW = "Kiswahili draft: native-speaker review required before release."  # = scripts/messaging/offer_lib.NATIVE_REVIEW
DRAFT_PENDING = "VICOBA draft pending: the Kiswahili group request is written by draft_master_messages.py."
EDUCATION_ANGLE = ("Savings group: a short Kiswahili talk at one of the group's weekly meetings on getting children ready for school and "
                   "planning their education; members opt in themselves.")
NEXT_ACTION = {
    "complete": "Introduction through the group's introducer first; no direct approach before it.",
    "incomplete: no ward": "Find the group's ward (the source or the council CDO) before any request.",
    "incomplete: no introducer route": "Find an introducer (ward CDO, NGO field office, bank branch or faith office) before any request.",
    "incomplete: name only": "Find the group's council, ward and an introducer before any request.",
    "stale: not confirmed in 12 months": "Confirm the group still meets (a newer source or the committee) before any request.",
}
MISSING = {
    "incomplete: no ward": "ward",
    "incomplete: no introducer route": "introducer route (ward CDO, NGO field office, bank branch, faith office or a route the group publishes)",
    "incomplete: name only": "council and ward, then an introducer route",
}


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def ascii_fold(text: str) -> str:
    return unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()


def norm(text: str) -> str:
    return " ".join(str(text or "").strip().casefold().split())


def key_name(name: str) -> str:
    """The group name as it enters the key: case, punctuation and the words of decision 2b removed."""
    s = " " + re.sub(r"[^a-z0-9]+", " ", ascii_fold(name)) + " "
    for word in KEY_STOPWORDS:
        s = re.sub(rf"\s{re.escape(word)}(?=\s)", " ", s)
    out = re.sub(r"\s+", "", s)
    return out or re.sub(r"[^a-z0-9]", "", ascii_fold(name))


def group_key(council: str, ward: str, name: str) -> str:
    """VIC|<council>|<ward>|<normalised name>; council and ward as the government run's admin_units spell them."""
    return f"VIC|{' '.join(str(council or '').split())}|{' '.join(str(ward or '').split())}|{key_name(name)}"


def saccos_name(name: str) -> str:
    s = " " + re.sub(r"[^a-z0-9]+", " ", ascii_fold(name)) + " "
    for word in SACCOS_STOPWORDS:
        s = re.sub(rf"\s{re.escape(word)}(?=\s)", " ", s)
    return re.sub(r"\s+", "", s)


def council_token(council: str) -> str:
    s = ascii_fold(council)
    s = re.sub(r"\b(city|municipal|district|town|township)?\s*council\b|\b(dc|mc|tc|cc)\b", " ", s)
    return " ".join(s.split())


def common_names() -> set[str]:
    names = set(BUILTIN_COMMON)
    if COMMON_NAMES_FILE.is_file():
        data = json.loads(COMMON_NAMES_FILE.read_text(encoding="utf-8"))
        items = data.get("names", []) if isinstance(data, dict) else data
        for item in items:
            names.add(key_name(item.get("name", "") if isinstance(item, dict) else item))
    return {n for n in names if n}


def truthy(value: str) -> bool:
    return norm(value) == "true"


def compute_status(row: dict, as_of: date) -> str:
    if not row.get("council"):
        return "incomplete: name only"
    if not row.get("ward"):
        return "incomplete: no ward"
    if not row.get("introducer_kind"):
        return "incomplete: no introducer route"
    try:
        confirmed = date.fromisoformat(row.get("last_confirmed") or row.get("verified_on"))
    except (TypeError, ValueError):
        return "stale: not confirmed in 12 months"
    return "stale: not confirmed in 12 months" if (as_of - confirmed).days > 365 else "complete"


# --- Schema ----------------------------------------------------------------------------------------------------------------------
SEGMENT_ROWS = (
    ("VICOBA members", "Community savings-and-loan groups (VICOBA, VSLA) in the catchment, through their committee",
     "A short Kiswahili talk at one of the group's weekly meetings; the family offer and the group rate for savings groups "
     "(OF01, OF02, OF09, OF07) after the committee replies",
     "Group-level record only (no member or officer data); first touch through an introducer; women's groups first; Kiswahili "
     "native-speaker review before release; no loan, subsidy or fee-financing claim", "F26"),
    ("VICOBA introducers", "NGO field offices and bank branches that know local savings groups",
     "A request to introduce Silverleaf to group committees; no terms in the request",
     "One request per introducer per wave; never a member list; an organisation already in an employer conversation keeps that "
     "conversation first", "F26"),
)


def ensure_schema(con: sqlite3.Connection) -> list[str]:
    """Add the outreach_plans columns language and english_meaning and the two VICOBA outreach segments; idempotent."""
    changes = []
    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    for column in PLAN_COLUMNS:
        if column not in columns:
            con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
            changes.append(f"outreach_plans.{column} added")
    existing = {r[0] for r in con.execute("SELECT segment FROM outreach_segments")}
    for row in SEGMENT_ROWS:
        if row[0] not in existing:
            con.execute("INSERT INTO outreach_segments (segment, audience, offer, qualification, flow_id) VALUES (?,?,?,?,?)", row)
            changes.append(f"outreach segment '{row[0]}' added")
    return changes


def schema_ready(con: sqlite3.Connection) -> bool:
    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    segments = {r[0] for r in con.execute("SELECT segment FROM outreach_segments")}
    return set(PLAN_COLUMNS) <= columns and set(OUTREACH_SEGMENTS) <= segments


# --- Readers for later tasks -----------------------------------------------------------------------------------------------------
def vicoba_ids(con: sqlite3.Connection) -> set[str]:
    """Every VICOBA organisation: a savings group with a VICOBA/VSLA subtype or a vicoba_group_key fact."""
    ids = {r[0] for r in con.execute(
        f"SELECT organisation_id FROM organisations WHERE segment=? AND subtype IN ({','.join('?' * len(SUBTYPES))})", (SEGMENT, *SUBTYPES))}
    ids |= {r[0] for r in con.execute("SELECT entity_id FROM facts WHERE entity_type='organisation' AND field='vicoba_group_key'")}
    return ids


def load_vicoba_groups(con: sqlite3.Connection) -> dict[str, dict]:
    """organisation_id -> the organisation's columns plus 'facts' (field -> values in the order recorded) and the contract's
    convenience values: 'group_key', 'record_status', 'women_group' (bool, True only on source evidence), 'last_confirmed'."""
    con_row = con.row_factory
    con.row_factory = sqlite3.Row
    try:
        ids = vicoba_ids(con)
        groups = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations") if r["organisation_id"] in ids}
        for oid in groups:
            groups[oid]["facts"] = {}
        for r in con.execute("SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' ORDER BY rowid"):
            if r["entity_id"] in groups:
                groups[r["entity_id"]]["facts"].setdefault(r["field"], []).append(r["value"])
    finally:
        con.row_factory = con_row
    for g in groups.values():
        f = g["facts"]
        g["group_key"] = (f.get("vicoba_group_key") or [""])[0]
        g["record_status"] = (f.get("record_status") or [""])[-1]
        g["women_group"] = "true" in (f.get("women_group") or [])
        g["last_confirmed"] = max(f.get("last_confirmed") or [""])
    return groups


def wave_order(groups: dict[str, dict]) -> list[str]:
    """Women's groups first in every wave (section 0), then nearest first, then by name."""
    return sorted(groups, key=lambda oid: (not groups[oid]["women_group"],
                                           groups[oid].get("distance_km") if groups[oid].get("distance_km") not in (None, "") else 9e9,
                                           groups[oid].get("name") or ""))


# --- The plan ----------------------------------------------------------------------------------------------------------------------
def run_checks(intake: Path, database: Path, work: Path) -> tuple[dict, dict]:
    work.mkdir(parents=True, exist_ok=True)
    vpath, ppath = work / f"vicoba-validation-{intake.stem}.json", work / f"vicoba-preflight-{intake.stem}.json"
    v = subprocess.run([sys.executable, "-B", str(VALIDATOR), str(intake), "--report", str(vpath)], capture_output=True, text=True,
                       encoding="utf-8")
    if v.returncode:
        raise SystemExit(f"validate_intake.py failed; nothing was written. See {vpath}.\n{v.stdout[-1500:]}")
    p = subprocess.run([sys.executable, "-B", str(PREFLIGHT), str(database), str(intake), "--report", str(ppath)], capture_output=True,
                       text=True, encoding="utf-8")
    if p.returncode:
        raise SystemExit(f"preflight_update.py failed; nothing was written. See {ppath}.\n{p.stdout[-1500:]}{p.stderr[-800:]}")
    return json.loads(vpath.read_text(encoding="utf-8")), json.loads(ppath.read_text(encoding="utf-8"))


def sanitise(row: dict) -> tuple[dict, list[str]]:
    """Blank the personal columns and a home meeting place; return the clean row and what was withheld (column names only)."""
    clean, withheld = dict(row), []
    for column in PERSONAL_COLUMNS:
        if clean.get(column):
            withheld.append(column)
            clean[column] = ""
    if clean.get("meeting_place_public") and HOME_PLACE.search(clean["meeting_place_public"]):
        withheld.append("meeting_place_public (reads as a home)")
        clean["meeting_place_public"] = ""
    return clean, withheld


def contract_issues(row: dict) -> list[str]:
    issues = []
    if row.get("record_type") != "organisation":
        issues.append("not an organisation row: the VICOBA intake holds group records only (no contact or enquiry rows)")
    if row.get("segment") not in ("", SEGMENT):
        issues.append(f"segment '{row['segment']}' is not '{SEGMENT}'")
    if row.get("subtype") and row["subtype"] not in SUBTYPES:
        issues.append(f"subtype '{row['subtype']}' is not a VICOBA subtype")
    if row.get("geocode_precision") and row["geocode_precision"] not in PRECISIONS:
        issues.append(f"geocode_precision '{row['geocode_precision']}' is not ward or point")
    for field, allowed in (("sponsor_kind", SPONSOR_KINDS), ("introducer_kind", INTRODUCER_KINDS), ("record_status", RECORD_STATUSES),
                           ("women_group_basis", WOMEN_BASES)):
        if row.get(field) and row[field] not in allowed:
            issues.append(f"{field} '{row[field]}' is not one of {list(allowed)}")
    if row.get("women_group") and norm(row["women_group"]) not in ("true", "false"):
        issues.append("women_group must be true, false or blank")
    if row.get("member_count") and not re.fullmatch(r"\d+", row["member_count"]):
        issues.append("member_count must be a whole number")
    if row.get("last_confirmed"):
        try:
            date.fromisoformat(row["last_confirmed"])
        except ValueError:
            issues.append("last_confirmed must be YYYY-MM-DD")
    if row.get("vicoba_group_key") and not KEY_RE.match(row["vicoba_group_key"]):
        issues.append("vicoba_group_key is not VIC|<council>|<ward>|<name>")
    if not (row.get("council") or row.get("locality") or row.get("village_or_mtaa")):
        issues.append("no area named (no council, locality or village)")
    if row.get("latitude") and row.get("longitude"):
        lat, lon = float(row["latitude"]), float(row["longitude"])
        if not (TANZANIA[0] <= lat <= TANZANIA[1] and TANZANIA[2] <= lon <= TANZANIA[3]):
            issues.append("point outside Tanzania")
    return issues


def build_plan(rows: list[dict], con: sqlite3.Connection, preflight: dict, intake: Path, as_of: date) -> dict:
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT organisation_id, name, segment, subtype, locality, address FROM organisations")}
    existing_records = {r[0] for r in con.execute("SELECT record_id FROM source_records")}
    groups = load_vicoba_groups(con)
    by_key = {norm(g["group_key"]): oid for oid, g in groups.items() if g["group_key"]}
    by_reg = {}
    for oid, g in groups.items():
        for number in g["facts"].get("registration_number", []):
            for authority in g["facts"].get("registration_authority", [""]):
                by_reg[(norm(authority), norm(number))] = oid
    saccos = [(saccos_name(o["name"]), o) for o in orgs.values()
              if o["segment"] == SEGMENT and str(o["subtype"] or "").startswith("SACCOS")]
    common = common_names()
    # Groups already known, per council, for the duplicate check: (key, normalised name, ward, organisation_id)
    known = {}
    for oid, g in groups.items():
        f = g["facts"]
        council, ward = (f.get("council") or [""])[0], (f.get("ward") or [""])[0]
        known.setdefault(norm(council), []).append((g["group_key"], key_name(g["name"]), norm(ward), oid))
    pf = {a["row"]: a for a in preflight.get("actions", [])}
    plan = {"inserts": [], "matches": [], "already_applied": [], "aggregates": [], "quarantined": [], "reviews": [], "warnings": [],
            "withheld": {}, "phone_basis_for_contact_path": 0, "preflight_non_vicoba_hits": []}
    new_by_key, new_by_reg = {}, {}

    def review(kind, oid, related, field, values, action):
        plan["reviews"].append({"review_id": hid("V", "vicoba", kind, oid, related, field), "kind": kind, "entity_id": oid,
                                "related_id": related, "field": field, "values": str(values)[:500], "action": action})

    for line, raw in enumerate(rows, 2):
        raw = {k: (v or "").strip() for k, v in raw.items() if k is not None}
        row, withheld = sanitise(raw)
        if withheld:
            plan["withheld"][line] = withheld
        if any(raw.get(c) for c in PHONE_COLUMNS) and row.get("phone_basis") == "published_for_role":
            plan["phone_basis_for_contact_path"] += 1
        if row.get("phone_basis") and not (row["phone_basis"] == "published_for_role" or CONSENT.match(row["phone_basis"])):
            plan["warnings"].append({"line": line, "warning": f"phone_basis '{row['phone_basis']}' is not published_for_role or "
                                                              "consent_recorded <date>; not recorded"})
            row["phone_basis"] = ""
        if row.get("vicoba_groups_reported"):
            target = row.get("sponsor_ref") if row.get("sponsor_ref") in orgs else ""
            if not re.fullmatch(r"\d+", row["vicoba_groups_reported"]):
                plan["quarantined"].append({"line": line, "name": row.get("organisation_name"), "reason": "vicoba_groups_reported is not a number"})
                continue
            record_id = hid("R", "vicoba", intake.name, "aggregate", row.get("source_location"), row.get("source_url"))
            if record_id in existing_records:
                plan["already_applied"].append({"line": line, "name": row.get("organisation_name"), "record_id": record_id})
                continue
            plan["aggregates"].append({"line": line, "row": row, "target": target, "record_id": record_id})
            continue
        issues = contract_issues(row)
        if issues:
            plan["quarantined"].append({"line": line, "name": row.get("organisation_name"), "reason": "; ".join(issues)})
            continue
        row["segment"] = SEGMENT
        # Women's-group tag: true only on source evidence (section 0); the subtype follows the same evidence.
        women = truthy(row.get("women_group"))
        basis = row.get("women_group_basis") or ("name" if women and WOMEN_NAME.search(row["organisation_name"]) else "")
        downgrade = []
        if women and not basis:
            women = False
            downgrade.append("women_group true without a basis (name, source_says or council_women_loan_group): not tagged")
        if women and basis == "name" and not WOMEN_NAME.search(row["organisation_name"]):
            women, basis = False, ""
            downgrade.append("women_group basis 'name', but the name does not name women: not tagged")
        supplied_subtype = row.get("subtype") or ""
        subtype = supplied_subtype or (WOMEN_SUBTYPE if women else DEFAULT_SUBTYPE)
        if subtype == WOMEN_SUBTYPE and not women:
            subtype = DEFAULT_SUBTYPE
            downgrade.append("subtype 'VICOBA — women's group' without the women's-group evidence")
        if subtype == DISABILITY_SUBTYPE and row.get("evidence_basis") not in ("official", "published", "directory"):
            subtype = DEFAULT_SUBTYPE
            downgrade.append("a group of people with disabilities is recorded only when a council or intermediary supplies it as such")
        row.update({"subtype": subtype, "women_group": "true" if women else "false", "women_group_basis": basis if women else ""})
        computed = compute_status(row, as_of)
        status = row.get("record_status") or computed
        if row.get("record_status") and row["record_status"] != computed:
            plan["warnings"].append({"line": line, "warning": f"record_status '{row['record_status']}' as supplied; computed '{computed}'"})
        row["record_status"] = status
        row["last_confirmed"] = row.get("last_confirmed") or row.get("verified_on")
        mine = group_key(row.get("council"), row.get("ward"), row["organisation_name"])
        if row.get("vicoba_group_key") and norm(row["vicoba_group_key"]) != norm(mine):
            plan["warnings"].append({"line": line, "warning": f"vicoba_group_key as supplied differs from this script's ({mine}); the supplied key is used"})
        key = row.get("vicoba_group_key") or mine
        row["vicoba_group_key"] = key
        if not row.get("locality"):
            row["locality"] = ", ".join(x for x in (row.get("village_or_mtaa"), f"{row['ward']} ward" if row.get("ward") else "", row.get("council")) if x)
        record_id = hid("R", "vicoba", intake.name, key, row.get("source_location"), row.get("source_url"))
        if record_id in existing_records:
            plan["already_applied"].append({"line": line, "name": row["organisation_name"], "record_id": record_id})
            continue
        reg = (norm(row.get("registration_authority")), norm(row.get("registration_number"))) if row.get("registration_number") else None
        hit, how = by_key.get(norm(key)), "vicoba_group_key"
        if not hit and reg:
            hit, how = by_reg.get(reg), "registration number"
        pf_hit = (pf.get(line) or {}).get("organisation_id") if (pf.get(line) or {}).get("action") == "match" else None
        if not hit and pf_hit:
            if pf_hit in groups:
                hit, how = pf_hit, "exact name and locality (preflight)"
            else:
                plan["preflight_non_vicoba_hits"].append({"line": line, "name": row["organisation_name"], "master_id": pf_hit})
        new_hit = None
        if not hit:
            new_hit, how = new_by_key.get(norm(key)), "vicoba_group_key (earlier row of this intake)"
            if not new_hit and reg:
                new_hit, how = new_by_reg.get(reg), "registration number (earlier row of this intake)"
        entry = {"line": line, "row": row, "record_id": record_id, "downgrade": downgrade, "supplied_subtype": supplied_subtype, "new": False}
        if hit or new_hit:
            entry.update({"organisation_id": hit or new_hit["organisation_id"], "how": how,
                          "target": hit and groups[hit] or new_hit})
            plan["matches"].append(entry)
            continue
        oid = hid("O", "vicoba", key)
        entry.update({"organisation_id": oid, "new": True})
        plan["inserts"].append(entry)
        new_by_key[norm(key)] = entry
        if reg:
            new_by_reg[reg] = entry
        # Review items for the new group.
        if status.startswith("incomplete"):
            review("VICOBA record incomplete", oid, "", "record_status", f"{status}: missing {MISSING.get(status, '')}", NEXT_ACTION[status])
        if status.startswith("stale"):
            review("VICOBA stale", oid, "", "last_confirmed", f"last confirmed {row['last_confirmed']}", NEXT_ACTION[status])
        for note in downgrade:
            review("VICOBA record incomplete", oid, "", "subtype" if "subtype" in note or "disabilities" in note else "women_group",
                   f"{note}; supplied subtype '{supplied_subtype or 'blank'}'", "Check the source and record the evidence before the tag or subtype is used.")
        unresolved = []
        if row.get("introducer_kind") and not row.get("introducer_ref"):
            unresolved.append(f"introducer {row['introducer_kind']} named, not linked")
        for field in ("introducer_ref", "sponsor_ref"):
            ref = row.get(field)
            if ref and not ((MASTER_ID.match(ref) and ref in orgs) or RUN_REF.match(ref)):
                unresolved.append(f"{field} '{ref}' does not resolve")
                row[field] = ""
        if row.get("sponsor_name") and not row.get("sponsor_ref"):
            unresolved.append(f"sponsor '{row['sponsor_name']}' not linked")
        if row.get("employer_ref"):
            emp = orgs.get(row["employer_ref"])
            if not emp or emp["segment"] == SEGMENT:
                unresolved.append(f"employer_ref '{row['employer_ref']}' is not a master employer")
                row["employer_ref"] = ""
        if unresolved:
            review("VICOBA introducer to confirm", oid, row.get("introducer_ref") or row.get("sponsor_ref") or "", "introducer_ref",
                   "; ".join(unresolved), "Link the introducer, sponsor or employer through the reviewed file (data/reference/vicoba-introducers.json).")
        # Never merged with a SACCOS: a same-name SACCOS in the same council goes to a reviewer.
        token, vname = council_token(row.get("council")), key_name(row["organisation_name"])
        for sname, s in saccos:
            place = ascii_fold(f"{s['locality'] or ''} {s['address'] or ''}")
            if sname and sname == vname and (not token or not place.strip() or token in place):
                review("VICOBA may be a registered SACCOS", oid, s["organisation_id"], "name", f"{row['organisation_name']} / {s['name']}",
                       "Groups graduate into SACCOS: decide whether this group is the registered SACCOS. Never merged automatically.")
        # Similar names in the same council (decision 2b): review, never merge; common names only on the full key.
        mine_known = known.setdefault(norm(row.get("council")), [])
        for other_key, other_name, other_ward, other_id in mine_known:
            if norm(other_key) == norm(key) or vname in common or other_name in common:
                continue
            same = other_name == vname and (other_ward != norm(row.get("ward")) or not other_ward or not row.get("ward"))
            near = min(len(vname), len(other_name)) >= 5 and difflib.SequenceMatcher(None, vname, other_name).ratio() >= 0.85
            if same or near:
                review("VICOBA possible duplicate", oid, other_id, "name", f"{key} / {other_key}",
                       "Decide whether these are one group; similar names are never merged automatically.")
        mine_known.append((key, vname, norm(row.get("ward")), oid))
    # Conflicts for matched rows: a differing value is a review item, never an overwrite.
    for m in plan["matches"]:
        target = m["target"]
        if "facts" in target:
            before = target["facts"]
        else:
            before = {f: [target["row"].get(f)] for f in SINGLE_VALUED if target["row"].get(f)}
        for field in SINGLE_VALUED:
            value = m["row"].get(field)
            if value and before.get(field) and norm(value) not in {norm(v) for v in before[field]}:
                review(CONFLICT_KIND, m["organisation_id"], m["record_id"], field, f"{' | '.join(before[field])} / {value}",
                       "Two sources disagree: confirm the current value with the source or the committee.")
    return plan


def fact(con, oid, field, value, record, entity_type="organisation"):
    if value in (None, ""):
        return 0
    cur = con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                      (hid("X", oid, field, value), entity_type, oid, field, str(value), record))
    return cur.rowcount


def facts_for(row: dict) -> dict:
    out = {f: row.get(f, "") for f in FACT_FIELDS if f not in ("sources_seen", "covers_groups", "vicoba_groups_reported")}
    out["sources_seen"] = f"{row.get('source_url') or row.get('source_path')} ({row.get('source_location')})"
    out["women_group_basis"] = row.get("women_group_basis", "")
    for field in ("subtype", "locality", "geocode_precision", "size_evidence", "website", "osm_id"):
        out[field] = row.get(field, "")
    return out


def sanitised_intake(intake: Path, plan: dict) -> tuple[bytes, bool]:
    """The intake as stored in source_files: the personal columns and home meeting places blanked."""
    text = intake.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    changed = False
    for row in reader:
        clean, withheld = sanitise({k: v or "" for k, v in row.items() if k is not None})
        changed |= bool(withheld)
        writer.writerow(clean)
    return out.getvalue().encode("utf-8"), changed


def apply(con: sqlite3.Connection, plan: dict, intake: Path, date_label: str) -> dict:
    con.row_factory = None
    tables = ("organisations", "contacts", "outreach_plans", "messages", "source_records", "entity_sources", "facts", "review")
    before = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    ids_before = {t: {r[0] for r in con.execute(f"SELECT {c} FROM {t}")} for t, c in
                  (("organisations", "organisation_id"), ("contacts", "contact_id"), ("outreach_plans", "message_id"), ("messages", "message_id"))}
    raw = intake.read_bytes()
    content, sanitised = sanitised_intake(intake, plan)
    sid = hid("F", "vicoba", intake.name)
    try:
        rel = intake.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        rel = intake.as_posix()
    written = {"facts": 0, "reviews": 0}
    try:
        con.execute("BEGIN")
        schema = ensure_schema(con)
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (sid, rel, hashlib.sha256(raw).hexdigest(), len(raw), "csv; personal columns blanked" if sanitised else "csv", "utf-8", content))
        for entry in plan["inserts"] + plan["matches"]:
            r, oid, record = entry["row"], entry["organisation_id"], entry["record_id"]
            payload = {k: v for k, v in r.items() if k not in PERSONAL_COLUMNS}
            con.execute("INSERT INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, sid, f"line {entry['line']}: {r['organisation_name']}", json.dumps(payload, ensure_ascii=False)))
            if entry["new"]:
                verification = f"VICOBA intake {date_label}: {r['evidence_basis']} source ({r['verification_status']}); {r['record_status']}"
                notes = " ".join(x for x in [
                    f"VICOBA intake {date_label}" + (f" ({r['candidate_id']})." if r.get("candidate_id") else "."), r.get("notes", ""),
                    f"Women's group (source: {r['women_group_basis']})." if r["women_group"] == "true" else "",
                    "Group-level record only: no member or officer data, no phone or email on the organisation."] if x)
                con.execute("""INSERT INTO organisations (organisation_id, name, segment, priority, campus, distance_km, size_evidence, headcount,
                               address, education_angle, source_url, verification, strategy_id, outreach_status, next_action, email, phone, subtype,
                               radius_tier, geocode_precision, website, notes, transport_band, locality, osm_id, latitude, longitude)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (oid, r["organisation_name"], SEGMENT, r.get("priority", ""), r.get("campus", ""),
                             float(r["distance_km"]) if r.get("distance_km") else None, r.get("size_evidence", ""),
                             float(r.get("headcount") or r.get("member_count")) if (r.get("headcount") or r.get("member_count")) else None,
                             "" if HOME_PLACE.search(r.get("address", "")) else r.get("address", ""), EDUCATION_ANGLE, r.get("source_url", ""),
                             verification, STRATEGY_ID, "Not contacted", NEXT_ACTION[r["record_status"]], "", "", r["subtype"],
                             r.get("radius_tier", ""), r.get("geocode_precision", ""), r.get("website", ""), notes[:2000],
                             r.get("transport_band", ""), r["locality"], r.get("osm_id", ""),
                             float(r["latitude"]) if r.get("latitude") else None, float(r["longitude"]) if r.get("longitude") else None))
                if entry["supplied_subtype"] and entry["supplied_subtype"] != r["subtype"]:
                    written["facts"] += fact(con, oid, "subtype_as_supplied", entry["supplied_subtype"], record)
                mid = hid("M", "vicoba", oid)
                missing = "; ".join(x for x in [
                    DRAFT_PENDING, f"Record {r['record_status']}: {NEXT_ACTION[r['record_status']]}" if r["record_status"] != "complete" else "",
                    "First touch through the introducer; no direct approach before an introduction.", NATIVE_REVIEW] if x)
                con.execute("INSERT INTO messages (message_id, target_type, target_id, subject, body, strategy_id, status, conditions, "
                            "source_record_id) VALUES (?,?,?,?,?,?,?,?,?)",
                            (mid, "organisation", oid, "", "", MESSAGE_STRATEGY, MESSAGE_STATUS, "Held: VICOBA draft pending", record))
                con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, target_name, organisation_name,
                               strategy_version, segment, recipient_role, persona, contact_channel, channel_attribution, evidence_url, evidence_date,
                               verified_on, evidence_basis, evidence_record_ids, relevance_reason, proposed_offer, cta_type, flow_id, review_status,
                               missing_information, selection, subject, body, follow_up_1, follow_up_2, hook_status, hook, acquisition_version,
                               acquisition_track_id, value_module_ids, strategy_scope, message_variant, variant_reason, language, english_meaning)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (mid, oid, "organisation", oid, r["organisation_name"], r["organisation_name"], "vicoba-intake-v1", GROUP_SEGMENT,
                             "Group committee (through the introducer)", "Savings-group committee", "", "No recorded channel",
                             r.get("source_url", ""), r.get("source_date", ""), r.get("verified_on", ""), r["evidence_basis"], record,
                             f"Community savings group ({r['subtype']}) in {r['locality']}; a short Kiswahili talk at a weekly meeting on "
                             "planning children's education.", "", "Introduction to the committee", "F26", "Needs research", missing,
                             "Candidate for review", "", "", "", "", "No hook: request-first opening", "", ACQUISITION_VERSION, "AQ00",
                             VALUE_MODULES, "New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the "
                             "acquisition track controls cadence.", "n/a", "n/a: a savings group, which gets its own request to the committee.",
                             "sw", ""))
            else:
                written["facts"] += fact(con, oid, "name_variant", r["organisation_name"], record)
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))
            for field, value in facts_for(r).items():
                if field == "vicoba_group_key" and not entry["new"]:
                    continue  # the group keeps its first key; another key is a name variant
                written["facts"] += fact(con, oid, field, value, record)
        for agg in plan["aggregates"]:
            if not agg["target"]:
                continue
            r = agg["row"]
            payload = {k: v for k, v in r.items() if k not in PERSONAL_COLUMNS}
            con.execute("INSERT OR IGNORE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (agg["record_id"], sid, f"line {agg['line']}: aggregate", json.dumps(payload, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_id=? AND record_id=?)", (agg["target"], agg["record_id"], agg["target"], agg["record_id"]))
            area = r.get("council") or r.get("locality") or "the area named"
            written["facts"] += fact(con, agg["target"], "vicoba_groups_reported",
                                     f"{r['vicoba_groups_reported']} groups in {area} ({r.get('source_date') or r.get('acquired_on')}): "
                                     f"{r.get('evidence_excerpt', '')}"[:500], agg["record_id"])
        for v in plan["reviews"]:
            cur = con.execute('INSERT OR IGNORE INTO review (review_id, kind, entity_id, related_id, field, "values", action) VALUES (?,?,?,?,?,?,?)',
                              (v["review_id"], v["kind"], v["entity_id"], v["related_id"], v["field"], v["values"], v["action"]))
            written["reviews"] += cur.rowcount
        checks = transaction_checks(con, plan, sid, before, ids_before)
        if not all(checks.values()):
            raise RuntimeError(f"checks failed: {[k for k, ok in checks.items() if not ok]}")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    after = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}
    return {"schema": schema, "before": before, "after": after, "written": written, "checks": checks}


def transaction_checks(con, plan, sid, before, ids_before) -> dict:
    inserted = {e["organisation_id"] for e in plan["inserts"]}
    vic = vicoba_ids(con)
    linked = {r[0] for r in con.execute("SELECT DISTINCT es.entity_id FROM entity_sources es JOIN source_records sr ON sr.record_id=es.record_id "
                                        "WHERE es.entity_type='organisation'")}
    keyed = {r[0] for r in con.execute("SELECT entity_id FROM facts WHERE field='vicoba_group_key'")}
    status = {r[0] for r in con.execute("SELECT entity_id FROM facts WHERE field='record_status'")}
    saccos = {r[0] for r in con.execute("SELECT organisation_id FROM organisations WHERE subtype LIKE 'SACCOS%'")}
    this_run = {r[0] for r in con.execute("SELECT es.entity_id FROM entity_sources es JOIN source_records sr ON sr.record_id=es.record_id "
                                          "WHERE sr.source_id=?", (sid,))}
    ids_after = {t: {r[0] for r in con.execute(f"SELECT {c} FROM {t}")} for t, c in
                 (("organisations", "organisation_id"), ("contacts", "contact_id"), ("outreach_plans", "message_id"), ("messages", "message_id"))}
    return {
        "integrity": con.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
        "foreign_keys": not con.execute("PRAGMA foreign_key_check").fetchall(),
        "earlier_ids_kept": all(ids_before[t] <= ids_after[t] for t in ids_before),
        "organisations_conserved": len(ids_after["organisations"]) == before["organisations"] + len(inserted),
        "plans_conserved": len(ids_after["outreach_plans"]) == before["outreach_plans"] + len(inserted),
        "no_contacts_written": len(ids_after["contacts"]) == before["contacts"],
        "every_vicoba_keyed_and_sourced": all(o in keyed and o in status and o in linked for o in vic),
        "no_vicoba_phone_or_email": not any(oid in vic for (oid,) in con.execute(
            "SELECT organisation_id FROM organisations WHERE COALESCE(phone,'')<>'' OR COALESCE(email,'')<>''")),
        "no_saccos_merge": not (this_run & saccos) and not (keyed & saccos),
        "plans_have_messages": not con.execute("SELECT COUNT(*) FROM outreach_plans p WHERE NOT EXISTS (SELECT 1 FROM messages m WHERE m.message_id=p.message_id)").fetchone()[0],
        "automations_disabled": not con.execute("SELECT COUNT(*) FROM automation_configuration WHERE enabled=1").fetchone()[0],
        "schema_ready": schema_ready(con),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="the intake's date: data/raw/vicoba/master_intake_<date>.csv")
    parser.add_argument("--intake", type=Path, help="another intake CSV in the same format (for example a fixture)")
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--as-of", default=date.today().isoformat(), help="date for the 12-month staleness rule when record_status is blank")
    parser.add_argument("--work", type=Path, default=WORK, help="where the validation, preflight and preview reports go (runtime/)")
    parser.add_argument("--schema-only", action="store_true", help="only add the outreach_plans columns and the VICOBA outreach segments")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if not args.database.is_file():
        raise SystemExit(f"No database at {args.database}.")
    if args.schema_only:
        con = sqlite3.connect(args.database, isolation_level=None)
        if not args.apply:
            print(json.dumps({"schema_ready": schema_ready(con), "preview": "run with --apply to add what is missing"}))
            return 0
        con.execute("BEGIN")
        changes = ensure_schema(con)
        con.execute("COMMIT")
        print(json.dumps({"schema_changes": changes, "schema_ready": schema_ready(con)}, indent=1))
        return 0
    intake = args.intake or RAW / f"master_intake_{args.date}.csv"
    intake = intake if intake.is_absolute() else ROOT / intake
    if args.apply and "fixtures" in intake.resolve().parts and args.database.resolve() == MASTER.resolve():
        raise SystemExit("A fixture intake is for database copies only; it is never applied to the canonical master.")
    validation, preflight = run_checks(intake, args.database, args.work)
    con = sqlite3.connect(args.database, isolation_level=None)
    rows = list(csv.DictReader(intake.open(encoding="utf-8-sig", newline="")))
    missing_columns = [c for c in INTAKE_COLUMNS if c not in (rows[0].keys() if rows else ())]
    plan = build_plan(rows, con, preflight, intake, date.fromisoformat(args.as_of))
    if missing_columns:
        plan["warnings"].append({"line": 1, "warning": f"VICOBA columns missing from the intake (read as blank): {missing_columns}"})
    inserts = plan["inserts"]
    summary = {
        "intake": intake.as_posix(), "database": str(args.database), "validated_rows": validation["row_count"],
        "inserted": len(inserts), "matched": len(plan["matches"]), "already_applied": len(plan["already_applied"]),
        "aggregates": len(plan["aggregates"]), "aggregates_recorded_on_a_sponsor": sum(1 for a in plan["aggregates"] if a["target"]),
        "quarantined": len(plan["quarantined"]),
        "conservation": validation["row_count"] == len(inserts) + len(plan["matches"]) + len(plan["already_applied"]) + len(plan["aggregates"]) + len(plan["quarantined"]),
        "preflight_counts": preflight.get("counts"), "preflight_non_vicoba_hits_not_merged": len(plan["preflight_non_vicoba_hits"]),
        "by_subtype": {}, "by_record_status": {}, "women_groups": sum(1 for e in inserts if e["row"]["women_group"] == "true"),
        "review_items": {}, "rows_with_withheld_columns": len(plan["withheld"]),
        "phones_withheld": sum(1 for cols in plan["withheld"].values() if any(c in PHONE_COLUMNS for c in cols)),
        "phone_basis_for_contact_path": plan["phone_basis_for_contact_path"],
        "home_meeting_places_withheld": sum(1 for cols in plan["withheld"].values() if any(c.startswith("meeting_place") for c in cols)),
        "warnings": len(plan["warnings"]),
    }
    for e in inserts:
        summary["by_subtype"][e["row"]["subtype"]] = summary["by_subtype"].get(e["row"]["subtype"], 0) + 1
        summary["by_record_status"][e["row"]["record_status"]] = summary["by_record_status"].get(e["row"]["record_status"], 0) + 1
    for v in plan["reviews"]:
        summary["review_items"][v["kind"]] = summary["review_items"].get(v["kind"], 0) + 1
    preview = {"summary": summary,
               "inserts": [{"line": e["line"], "organisation_id": e["organisation_id"], "name": e["row"]["organisation_name"],
                            "key": e["row"]["vicoba_group_key"], "subtype": e["row"]["subtype"], "record_status": e["row"]["record_status"],
                            "women_group": e["row"]["women_group"]} for e in inserts],
               "matches": [{"line": m["line"], "organisation_id": m["organisation_id"], "name": m["row"]["organisation_name"], "how": m["how"]}
                           for m in plan["matches"]],
               "aggregates": [{"line": a["line"], "count": a["row"]["vicoba_groups_reported"], "sponsor": a["target"] or "(not a master organisation: reported only)"}
                              for a in plan["aggregates"]],
               "quarantined": plan["quarantined"], "reviews": plan["reviews"], "warnings": plan["warnings"],
               "withheld_columns_by_line": plan["withheld"], "preflight_non_vicoba_hits": plan["preflight_non_vicoba_hits"]}
    args.work.mkdir(parents=True, exist_ok=True)
    out = args.work / f"vicoba-preview-{intake.stem}.json"
    out.write_text(json.dumps(preview, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    if not summary["conservation"]:
        raise SystemExit("Row conservation failed; nothing was written.")
    if not args.apply:
        print(f"Preview only: {out}")
        return 0
    result = apply(con, plan, intake, args.date if not args.intake else intake.stem)
    print(json.dumps(result, indent=1))
    print("Applied." if result["before"] != result["after"] or result["schema"] else "Applied: nothing new.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
