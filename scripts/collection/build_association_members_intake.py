#!/usr/bin/env python3
"""Build the intake for the sector-association members workbook (offline, read-only on the master).

Source: references/Tanzania Sector Associations and Members (1).xlsx, a team member's compilation checked on 12 October 2026: an Index tab
(the national associations and two regulator registers) and seven member tabs (Chamber of Mines, TBA banks, ACT agriculture, TATO tour
operators, TAFFA freight, Tier 2 microfinance from the Bank of Tanzania licence list of 14 August 2026, SACCOS from the TCDC licence list
of 30 June 2022). The VICOBA tab is explanatory text, not leads, and is skipped. Each tab's header is the row whose first cell is 'No.';
the lines above it (the tab's source line and note) are kept with every row as its source record.

For every member row it decides one of three things, and says why:
- master_new: its district is one of the catchment councils of data/runs/arusha-government-2026-09/run-config.json (Arusha City,
  Arusha DC/Arumeru, Meru, Hai, Siha, Moshi DC and MC, Monduli, Longido, Simanjiro; the config's 'core' flag is kept), or its district
  is blank, its region is Arusha or Kilimanjaro and its physical or postal address names a catchment town; it is operating; and it does
  not match a master organisation;
- master_match: it matches a master organisation exactly (website domain, then a non-free-mail email, then a free-mail email with a
  similar name, then the normalised name; a register row from outside the two regions matches by name only as a review signal);
  scripts/master/add_association_members.py enriches the match and never overwrites it;
- national: everything else, with the detail 'in region, beyond catchment' (Karatu, Ngorongoro, Same, Mwanga, Rombo ...), 'in region,
  district not given' (no address in the source places it), 'outside the region', 'region not given', or 'non-operating' (the 53
  non-operating Tier 2 licensees and the revoked SACCOS, wherever they are).
Similar names are review signals only, never merges. Rows are then deduplicated into national leads: one per normalised name (legal
suffixes dropped) whose regions agree, listing every association and source row; a master match or a new master organisation carries
its organisation_id.

Writes (all under the repository, nothing to the databases):
- data/raw/association-members/members_<date>.jsonl: every source row (Index rows included) with its fields, placement, decision,
  match and national_lead_id;
- data/raw/association-members/master_intake_<date>.csv: the shared-contract intake of the rows that go to the master (new and
  matched), for validate_intake.py, preflight_update.py and add_association_members.py;
- data/raw/association-members/bank_head_offices_<date>.json: each TBA bank with its head-office phone and email and the master
  branch records it matches (their escalation contact);
- data/raw/contact-research/introducers_associations_<date>.jsonl: the Index associations the master does not hold, for
  scripts/master/add_introducers.py (website, sector and the Index row as source; no new research);
- runtime/association-members/build-summary-<date>.json: the counts per tab and the conservation arithmetic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "references" / "Tanzania Sector Associations and Members (1).xlsx"
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RUN_CONFIG = ROOT / "data" / "runs" / "arusha-government-2026-09" / "run-config.json"
TEMPLATE = ROOT / "skills" / "silverleaf-create-lead-list" / "assets" / "lead-intake-template.csv"
OUT = ROOT / "data" / "raw" / "association-members"
INTRODUCERS = ROOT / "data" / "raw" / "contact-research"
RUNTIME = ROOT / "runtime" / "association-members"
CHECKED_ON = "2026-10-12"

# Tab -> (key, association, acronym, source URL, source date, evidence basis). The URL is the page or file the tab's source line names.
TABS = {
    "Chamber of Mines": ("TCM", "Tanzania Chamber of Mines", "TCM", "https://chamberofmines.or.tz/membership", CHECKED_ON, "directory"),
    "TBA (Bankers)": ("TBA", "Tanzania Bankers Association", "TBA", "https://tanzaniabankers.org", CHECKED_ON, "directory"),
    "ACT (Agriculture)": ("ACT", "Agricultural Council of Tanzania", "ACT",
                          "https://actanzania.or.tz/index.php/membership-services/our-members", CHECKED_ON, "directory"),
    "TATO (Tour Operators)": ("TATO", "Tanzania Association of Tour Operators", "TATO", "https://tatotz.org/members", CHECKED_ON, "directory"),
    "TAFFA (Freight)": ("TAFFA", "Tanzania Freight Forwarders Association", "TAFFA", "https://taffa.or.tz/taffa-members-list", CHECKED_ON, "directory"),
    "Microfinance (Tier 2)": ("MSP2", "Bank of Tanzania register of Tier 2 microfinance service providers", "BoT MSP2",
                              "https://www.bot.go.tz/Other/Orodha%20ya%20Watoa%20Huduma%20Ndogo%20za%20Fedha%20wa%20Daraja%20la%20Pili.pdf",
                              "2026-08-14", "official"),
    "SACCOS (TCDC licensed)": ("SACCOS", "TCDC register of licensed SACCOS", "TCDC SACCOS",
                               "https://www.ushirika.go.tz/uploads/ORODHA_YA_SACCOS_ZILIZOPEWA_LESENI_KUISHIA_30.06.2022.pdf", "2022-06-30", "official"),
}
SKIPPED_TABS = {"VICOBA (community groups)": "explanatory text (where to obtain council VICOBA registers), not leads"}
REGISTER_TABS = {"MSP2", "SACCOS"}
CATEGORY_COLUMN = {"TCM": "Membership category", "TBA": "Type", "ACT": "Member type", "TATO": "Member category",
                   "TAFFA": "TAFFA certificate no.", "MSP2": "Licence no.", "SACCOS": "Licence class"}

# District spellings in the workbook -> catchment council (run-config names). 'ARUSHA' and 'MOSHI' name the town or the district,
# which spans two councils; both councils are in the catchment.
DISTRICT_COUNCIL = {
    "ARUSHA CITY": "Arusha City Council", "ARUSHA URBAN": "Arusha City Council", "ARUSHA MUNICIPAL": "Arusha City Council",
    "ARUSHA": "Arusha City Council or Arusha District Council", "ARUSHA RURAL": "Arusha District Council",
    "ARUSHA DC": "Arusha District Council", "ARUMERU": "Arusha District Council or Meru District Council",
    "MERU": "Meru District Council", "HAI": "Hai District Council", "SIHA": "Siha District Council",
    "MOSHI MUNICIPAL": "Moshi Municipal Council", "MOSHI URBAN": "Moshi Municipal Council", "MOSHI RURAL": "Moshi District Council",
    "MOSHI DC": "Moshi District Council", "MOSHI": "Moshi Municipal Council or Moshi District Council",
    "MONDULI": "Monduli District Council", "LONGIDO": "Longido District Council", "SIMANJIRO": "Simanjiro District Council",
}
# Catchment towns that place a row with a blank district (physical or postal address).
TOWN_COUNCIL = [(r"\busa[ -]?river\b|\bmaji ya chai\b|\bkikatiti\b", "Meru District Council"),
                (r"\btengeru\b|\bngaramtoni\b|\bkisongo\b|\boldonyo ?sambu\b", "Arusha District Council"),
                (r"\bboma ?ng'?ombe\b|\bhai\b", "Hai District Council"), (r"\bsanya ?juu\b|\bsiha\b", "Siha District Council"),
                (r"\bmoshi\b", "Moshi Municipal Council or Moshi District Council"),
                (r"\bmonduli\b", "Monduli District Council"), (r"\blongido\b", "Longido District Council"),
                (r"\bmererani\b|\bsimanjiro\b", "Simanjiro District Council"),
                (r"\barusha\b", "Arusha City Council or Arusha District Council")]
CATCHMENT_REGIONS = {"ARUSHA", "KILIMANJARO"}
LEGAL = {"ltd", "limited", "plc", "inc", "llc", "co", "company", "the", "t", "tz"}
FREE_MAIL = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|ymail|rocketmail|aol)\.", re.I)
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
NOT_A_SITE = re.compile(r"facebook|instagram|tripadvisor|linkedin|google|wordpress|wix|twitter|youtube|blogspot|gmail|yahoo", re.I)
ORG_NOISE = {"limited", "company", "tanzania", "africa", "african", "safaris", "safari", "tours", "travel", "adventures", "adventure",
             "microfinance", "finance", "credit", "saccos", "investment", "investments", "services", "general", "group"}
NOISE_TOKENS = {"ltd", "limited", "co", "company", "tz", "t", "inc", "the", "and", "of", "safaris", "safari", "tours", "tour", "travels", "travel",
                "expeditions", "adventures", "adventure", "holidays", "arusha", "tanzania", "africa", "african", "group", "plc", "bank",
                "saccos", "microfinance", "finance", "credit", "investment", "investments", "services", "general", "enterprises", "trading"}
# The employer/institution hint build_partner_leads.py uses for the SACCOS it imported from the same TCDC list (kept identical).
EMPLOYER_HINT = re.compile(r"(?i)staff|workers|employee|teachers|hotel|lodge|tour guides|utalii|security|braeburn|kia|tpc|bonite|sunflag|rijkzwaan|"
                           r"friedkin|asilia|tarangire|senapa|tawiri|taha|camartec|kcmc|kcmuco|mweka|veta|city council|kurugenzi|water|acu|iaa|"
                           r"elct|kkkt|lutheran|hospital|college|school|club|tbl|tcc")
# Index rows the master already holds under another name (the Index row's website or name differs from the master record's).
INDEX_ALIASES = {"TCCIA": "Tanzania National Chamber of Commerce (TNCC, formerly TCCIA)"}
# The associations the approved plan adds as introducers (Index rows 1-15 the master lacks); others are listed, not added.
PLANNED_INTRODUCERS = {"TCM", "ACT", "TAFFA", "ATI", "TASTA", "TAOMAC", "TSA", "TWCC"}
INTRODUCER_KIND = "sector association"


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def ascii_lower(text) -> str:
    return unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()


def name_key(name) -> str:
    """Normalised name for exact matching: ASCII, lower case, '&' as 'and', '(T)' dropped, legal suffixes (Ltd, Limited, Co ...) dropped."""
    s = ascii_lower(name).replace("&", " and ").replace("(t)", " ")
    return "".join(t for t in re.findall(r"[a-z0-9]+", s) if t not in LEGAL)


def bare_key(name) -> str:
    """name_key without parenthesised parts ('National Bank of Commerce (NBC)' -> 'nationalbankofcommerce')."""
    return name_key(re.sub(r"\([^)]*\)", " ", str(name or "")))


BANK_WORDS = {"bank", "tanzania", "plc", "ltd", "limited", "t", "tz", "branch", "the"}


def bank_key(name) -> str:
    """A bank's name without the generic words ('NBC Bank' -> 'nbc')."""
    return "".join(t for t in re.findall(r"[a-z0-9]+", ascii_lower(re.sub(r"\([^)]*\)", " ", str(name or "")))) if t not in BANK_WORDS)


def bank_keys(name) -> set:
    """bank_key of a master record's name, and of its parenthesised acronym ('National Bank of Commerce (NBC)' -> {'nationalofcommerce', 'nbc'}),
    only for a record whose name says it is a bank."""
    if not re.search(r"\bbank\b", str(name or ""), re.I):
        return set()
    keys = {bank_key(name)}
    keys |= {bank_key(m) for m in re.findall(r"\(([^)]*)\)", str(name))}
    return {k for k in keys if len(k) >= 3}


def tokens(name) -> set:
    return {t for t in re.findall(r"[a-z0-9]+", ascii_lower(name)) if len(t) > 2 and t not in NOISE_TOKENS}


def similar(a, b) -> bool:
    x, y = tokens(a), tokens(b)
    if not x or not y or not any(len(t) >= 4 for t in x & y):
        return False
    return len(x & y) / len(x | y) >= 0.6


def domain(url) -> str:
    m = re.search(r"(?:https?://)?(?:www\.)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)+)", str(url or "").lower())
    host = m.group(1) if m else ""
    return "" if not host or NOT_A_SITE.search(host) else host


def emails_of(value) -> list:
    return [e.lower().strip(".") for e in EMAIL.findall(str(value or ""))]


def phone_keys(value) -> set:
    out = set()
    for m in re.findall(r"\+?\d[\d \-]{7,}\d", str(value or "")):
        digits = re.sub(r"\D", "", m)
        if len(digits) >= 9:
            out.add(digits[-9:])
    return out


def org_named_inbox(address: str, organisation: str) -> bool:
    """A free-mail inbox named after the organisation: the rule of export_resend_contacts.org_named_inbox (and merge_master_contacts.py)."""
    local = re.sub(r"[^a-z]", "", address.split("@")[0].lower())
    toks = [w for w in re.findall(r"[a-z]{5,}", organisation.lower()) if w not in ORG_NOISE]
    return bool(toks) and any(w in local for w in toks)


def cell(value) -> str:
    if value is None or not isinstance(value, (str, int, float)):
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return " ".join(str(value).split())


def clean_website(value) -> str:
    v = cell(value)
    if not v or v.lower() in ("not found", "none", "not applicable"):
        return ""
    v = v.split()[0].rstrip("/")
    return v if re.match(r"^https?://", v, re.I) else f"https://{v}"


# ------------------------------------------------------------------ reading the workbook
def read_workbook(path: Path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    index, members, skipped = [], [], []
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if ws.title in SKIPPED_TABS:
            skipped.append({"tab": ws.title, "rows": sum(1 for r in rows if any(cell(c) for c in r)), "reason": SKIPPED_TABS[ws.title]})
            continue
        header_at = next(i for i, r in enumerate(rows) if r and cell(r[0]) == "No.")
        header = [cell(c) for c in rows[header_at]]
        preamble = [cell(r[0]) for r in rows[:header_at] if r and cell(r[0])]
        for i in range(header_at + 1, len(rows)):
            r = rows[i]
            values = {h: cell(v) for h, v in zip(header, r) if h}
            name = values.get("Member") or values.get("Name") or values.get("Association")
            if not name:
                continue
            sheet_row = i + 1  # Excel row number
            if ws.title == "Index":
                index.append({"tab": "Index", "sheet_row": sheet_row, "values": values, "source_line": preamble[0] if preamble else "",
                              "note": preamble[1] if len(preamble) > 1 else ""})
                continue
            key = TABS[ws.title][0]
            members.append({"tab": ws.title, "tab_key": key, "sheet_row": sheet_row, "values": values, "source_line": preamble[1] if len(preamble) > 1 else "",
                            "note": preamble[2] if len(preamble) > 2 else "", "title": preamble[0] if preamble else ""})
    return index, members, skipped


# ------------------------------------------------------------------ placement
def norm_district(value: str) -> str:
    d = re.sub(r"\s+", " ", str(value or "").upper().replace("-", " ")).strip()
    d = re.sub(r"\b(DISTRICT|DC|COUNCIL|REGION)\b$", "", d).strip() if d not in ("ARUSHA DC", "MOSHI DC") else d
    return d


def place(row: dict, cores: dict) -> dict:
    v = row["values"]
    district, region = norm_district(v.get("District")), str(v.get("Region") or "").upper().strip()
    address = " ".join(x for x in (v.get("Physical address"), v.get("Postal address")) if x)
    if district in DISTRICT_COUNCIL:
        council = DISTRICT_COUNCIL[district]
        return {"placement": "catchment", "council": council, "core": any(cores.get(c, False) for c in council.split(" or ")),
                "basis": f"district {v.get('District')} ({region.title() or 'region not given'})"}
    if region in CATCHMENT_REGIONS:
        if district:
            return {"placement": "beyond", "council": "", "core": False,
                    "basis": f"district {v.get('District')}, {region.title()} region: in region, beyond catchment"}
        text = ascii_lower(address)
        for pattern, council in TOWN_COUNCIL:
            if text and re.search(pattern, text):
                return {"placement": "catchment", "council": council, "core": any(cores.get(c, False) for c in council.split(" or ")),
                        "basis": f"district not given; address '{address}' names a catchment town"}
        return {"placement": "region_unplaced", "council": "", "core": False,
                "basis": f"{region.title()} region; district not given and no address in the source places it"}
    if region:
        return {"placement": "outside", "council": "", "core": False, "basis": f"{region.title()} region: outside the catchment regions"}
    return {"placement": "unknown", "council": "", "core": False, "basis": "region not given"}


def operating(row: dict) -> tuple[bool, str]:
    status = row["values"].get("Status", "")
    if row["tab_key"] == "MSP2" and status.lower().startswith("non-operating"):
        return False, f"non-operating ({status})"
    if row["tab_key"] == "SACCOS" and "revoked" in status.lower():
        return False, f"licence revoked ({status})"
    return True, status


# ------------------------------------------------------------------ the master (read-only)
class Master:
    def __init__(self, path: Path):
        con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        self.orgs = {r["organisation_id"]: dict(r) for r in con.execute(
            "SELECT organisation_id, name, segment, subtype, website, email, phone, locality, address FROM organisations")}
        chosen = {r[0] for r in con.execute("SELECT organisation_id FROM outreach_plans WHERE selection='Candidate for review'")}
        self.by_name, self.by_bare, self.by_domain, self.by_email = (defaultdict(list) for _ in range(4))
        for oid, o in sorted(self.orgs.items(), key=lambda kv: (kv[0] not in chosen, kv[0])):
            if name_key(o["name"]):
                self.by_name[name_key(o["name"])].append(oid)
            if bare_key(o["name"]):
                self.by_bare[bare_key(o["name"])].append(oid)
            if domain(o["website"]):
                self.by_domain[domain(o["website"])].append(oid)
            for e in emails_of(o["email"]):
                self.by_email[e].append(oid)
        self.token_index = defaultdict(set)
        for oid, o in self.orgs.items():
            for t in tokens(o["name"]):
                if len(t) >= 4:
                    self.token_index[t].add(oid)

    def where_ok(self, oid: str, row: dict) -> bool:
        """A register row (SACCOS, Tier 2 lender) names its place: the master record's locality or address must carry its district or a
        word of its postal or physical address."""
        v = row["values"]
        words = {w for w in re.findall(r"[a-z]{4,}", ascii_lower(" ".join(str(v.get(k) or "") for k in
                                                                         ("District", "Postal address", "Physical address"))))
                 if w not in {"box", "district", "region", "road", "street", "plot", "council", "municipal", "city", "rural", "urban"}}
        text = ascii_lower(f"{self.orgs[oid]['locality'] or ''} {self.orgs[oid]['address'] or ''}")
        return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)

    def match(self, row: dict, placement: dict, name_count: int = 1) -> tuple[str, str, list, str]:
        """(organisation_id, basis, other ids, signal) for an exact match; ('', '', [], signal) when none. Domain first, then email, then
        name. A website or inbox match from a row placed outside the catchment whose name is not like the record's is another property of
        the group (Melia Serengeti on the Gran Melia Arusha site): a review signal, not a match. A register name matches only a record at
        its place, unless the name is unique in the register and the record carries no other place."""
        v, name, tab = row["values"], row["name"], row["tab_key"]
        far = placement["placement"] in ("outside", "beyond") and tab != "TBA"  # a bank's head office is in Dar by nature

        def same_business(oid):
            return name_key(name) == name_key(self.orgs[oid]["name"]) or similar(name, self.orgs[oid]["name"])

        site = domain(v.get("Website"))
        if site and tab != "TCM":  # Chamber of Mines websites are often the parent group's (the tab's note), never a match key
            hits = self.by_domain.get(site, [])
            if hits:
                if far and not same_business(hits[0]):
                    return "", "", [], f"same website {site} as {hits[0]} ({self.orgs[hits[0]]['name']}), another place: possibly another property"
                return hits[0], f"website domain {site}", hits[1:], ""
        for e in emails_of(v.get("Email")):
            hits = self.by_email.get(e, [])
            if hits and (not FREE_MAIL.search(e) or same_business(hits[0])):
                if far and not same_business(hits[0]):
                    return "", "", [], f"same inbox as {hits[0]} ({self.orgs[hits[0]]['name']}), another place"
                return hits[0], f"email {e}", hits[1:], ""
        if tab == "TBA":  # a bank's head-office inbox domain equals the domain on a branch record
            for e in emails_of(v.get("Email")):
                d = e.split("@")[1]
                hits = [oid for oid, o in self.orgs.items() if d in {domain(o["website"]), *(x.split("@")[1] for x in emails_of(o["email"]))}]
                if hits:
                    return hits[0], f"email domain {d}", hits[1:], ""
            key = bank_key(name)
            hits = [oid for oid, o in self.orgs.items() if key and key in bank_keys(o["name"])]
            if hits:
                return hits[0], "bank name (generic words dropped)", hits[1:], ""
        key = name_key(name)
        hits = self.by_name.get(key, []) or self.by_bare.get(bare_key(name), [])
        if hits:
            if tab in REGISTER_TABS:
                placed = [oid for oid in hits if self.where_ok(oid, row)]
                if placed:
                    return placed[0], "normalised name and place", [x for x in hits if x != placed[0]], ""
                if far or name_count > 1:
                    return "", "", [], f"same name as {hits[0]} ({self.orgs[hits[0]]['name']}, {self.orgs[hits[0]]['address'] or self.orgs[hits[0]]['locality'] or 'no place'}), another place"
            return hits[0], "normalised name", hits[1:], ""
        return "", "", [], ""

    def similar_to(self, name: str) -> list:
        cands = set()
        for t in tokens(name):
            if len(t) >= 4:
                cands |= self.token_index.get(t, set())
        return sorted(oid for oid in cands if similar(name, self.orgs[oid]["name"]))[:3]


# ------------------------------------------------------------------ the rows
def member_fields(row: dict) -> dict:
    v, tab = row["values"], row["tab_key"]
    emails = emails_of(v.get("Email"))
    category = v.get(CATEGORY_COLUMN[tab], "")
    return {"name": row["name"], "association": TABS[row["tab"]][1], "association_acronym": TABS[row["tab"]][2],
            "member_category": category if tab not in ("TAFFA", "MSP2", "SACCOS") else
            {"TAFFA": "Registered member", "MSP2": "Tier 2 microfinance service provider", "SACCOS": f"Licence class {category}"}[tab],
            "licence_no": category if tab in ("TAFFA", "MSP2") else (category if tab == "SACCOS" else ""),
            "status": v.get("Status", ""), "phone": v.get("Phone", ""), "emails": emails, "whatsapp": v.get("WhatsApp", ""),
            "website": clean_website(v.get("Website")), "contact_person_published": bool(v.get("Contact person")),
            "services": v.get("Services listed", ""), "physical_address": v.get("Physical address", ""),
            "postal_address": v.get("Postal address", ""), "district": v.get("District", ""), "region": v.get("Region", ""),
            "country": v.get("Country", ""),
            "personal_inboxes": [e for e in emails if FREE_MAIL.search(e) and not org_named_inbox(e, row["name"])]}


def master_labels(row: dict, f: dict) -> tuple[str, str]:
    """(segment, subtype) for a new master organisation, in the labels the drafter and kind_of already read."""
    tab, cat = row["tab_key"], f["member_category"]
    if tab == "TATO":
        if cat == "Hotel / lodge":
            return "Hotel", "TATO member (hotel / lodge)"
        if cat == "Affiliate member":
            return "Company (TATO affiliate member)", "TATO affiliate member"
        if cat == "Airline / aviation":
            return "Airline / aviation (TATO member)", "TATO member (airline / aviation)"
        return "Safari / tour operator", "TATO member (licensed)" if cat == "Tour operator" else "TATO member (not categorised)"
    if tab == "MSP2":
        return "Microfinance lender", "Tier 2 microfinance service provider (BoT licence)"
    if tab == "SACCOS":
        kind = "employer/institution-based" if EMPLOYER_HINT.search(f["name"]) else "community/open-bond"
        return "Savings group", f"SACCOS — {kind} (TCDC licence class {f['licence_no']})"
    if tab == "TCM":
        return "Mining company (Chamber of Mines member)", f"Chamber of Mines member ({cat})"
    if tab == "TBA":
        return "Bank (head office)", f"TBA member ({cat})"
    if tab == "ACT":
        return f"Agriculture ({cat}, ACT member)", f"ACT member ({cat})"
    return "Freight forwarder (TAFFA member)", "TAFFA registered member"


def display_name(name: str, tab: str) -> str:
    """Upper-case register names in title case (as the master's SACCOS import did); other names as published."""
    if name.isupper() and tab in ("MSP2", "SACCOS", "TAFFA", "ACT"):
        t = name.title()
        for a, b in (("Saccos", "SACCOS"), ("Amcos", "AMCOS"), ("Ltd", "Ltd"), (" And ", " and "), (" Of ", " of ")):
            t = t.replace(a, b)
        return t
    return name


def dedupe(rows: list) -> dict:
    """national_lead_id per row id: rows join on the normalised name when their regions agree (a blank region joins any), and rows
    matched to one master organisation always join."""
    parent = {r["row_id"]: r["row_id"] for r in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    by_key = defaultdict(list)
    for r in rows:
        by_key[name_key(r["name"])].append(r)
    for group in by_key.values():
        regional = defaultdict(list)
        blank = []
        for r in group:
            (regional[r["fields"]["region"].upper()] if r["fields"]["region"] else blank).append(r)
        anchors = []
        for reg, items in sorted(regional.items()):
            for r in items[1:]:
                union(items[0]["row_id"], r["row_id"])
            anchors.append(items[0]["row_id"])
        for r in blank:
            union(anchors[0] if anchors else blank[0]["row_id"], r["row_id"])
    by_org = defaultdict(list)
    for r in rows:
        if r["organisation_id"]:
            by_org[r["organisation_id"]].append(r["row_id"])
    for ids in by_org.values():
        for x in ids[1:]:
            union(ids[0], x)
    clusters = defaultdict(list)
    for r in rows:
        clusters[find(r["row_id"])].append(r)
    out = {}
    for members in clusters.values():
        first = sorted(members, key=lambda r: r["row_id"])[0]
        nid = hid("N", "association-members", name_key(first["name"]), first["fields"]["region"].upper())
        for r in members:
            out[r["row_id"]] = nid
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default="2026-11-19", help="label of the output files (the merge date)")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--database", type=Path, default=MASTER)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    config = json.loads(RUN_CONFIG.read_text(encoding="utf-8"))
    cores = {c["name"]: bool(c.get("core")) for c in config["councils"]}
    index, members, skipped_tabs = read_workbook(args.source)
    master = Master(args.database)
    source_path = args.source.relative_to(ROOT).as_posix()

    for m in members:
        m["name"] = m["values"].get("Member") or m["values"].get("Name")
    name_counts = Counter((m["tab_key"], name_key(m["name"])) for m in members)
    rows = []
    for m in members:
        f = member_fields(m)
        p = place(m, cores)
        ok, status_note = operating(m)
        oid, basis, others, signal = master.match(m, p, name_counts[(m["tab_key"], name_key(m["name"]))])
        if oid:
            decision, detail = "master_match", f"in master ({basis})"
        elif not ok:
            decision, detail = "national", status_note
        elif p["placement"] == "catchment":
            decision, detail = "master_new", f"in catchment: {p['council']}"
        else:
            decision, detail = "national", {"beyond": "in region, beyond catchment", "region_unplaced": "in region, district not given",
                                            "outside": "outside the region", "unknown": "region not given"}[p["placement"]]
        rows.append({"row_id": f"{m['tab_key']}:{m['sheet_row']}", "tab": m["tab"], "tab_key": m["tab_key"], "sheet_row": m["sheet_row"],
                     "source_location": f"'{m['tab']}'!A{m['sheet_row']}", "source_line": m["source_line"], "note": m["note"],
                     "source_url": TABS[m["tab"]][3], "source_date": TABS[m["tab"]][4], "evidence_basis": TABS[m["tab"]][5],
                     "name": m["name"], "fields": f, "placement": p, "operating": ok, "operating_note": status_note,
                     "decision": decision, "decision_detail": detail, "organisation_id": oid, "match_basis": basis,
                     "also_matches": others, "similar_master": [], "match_signal": signal, "values": m["values"]})

    # New master organisations: one per normalised name among the catchment rows (rows of one business share one record).
    new_ids = {}
    for r in rows:
        if r["decision"] == "master_new":
            key = name_key(r["name"])
            new_ids.setdefault(key, hid("O", "association-member", key))
            r["organisation_id"] = new_ids[key]
            r["similar_master"] = [oid for oid in master.similar_to(r["name"]) if oid != r["organisation_id"]]
    # A national row that shares its normalised name with a new organisation is the same business (a second listing): it joins it.
    for r in rows:
        if r["decision"] == "national" and r["operating"] and name_key(r["name"]) in new_ids and r["placement"]["placement"] in ("unknown",):
            r["organisation_id"] = new_ids[name_key(r["name"])]
            r["decision"], r["decision_detail"] = "master_new", "in catchment: second listing of a catchment member (same normalised name)"
    nid = dedupe(rows)
    for r in rows:
        r["national_lead_id"] = nid[r["row_id"]]

    # Index rows: associations the master holds, the planned introducers, and the rest (listed in the national table).
    index_out, introducers = [], []
    for ix in index:
        v = ix["values"]
        acr, name = v.get("Acronym", ""), v.get("Association", "")
        site = clean_website(v.get("Website"))
        register = v.get("TPSF membership (as published)", "").startswith("Regulator register") or acr == "VICOBA"
        hits = master.by_name.get(name_key(f"{name} ({acr})"), []) or master.by_name.get(name_key(name), [])
        hits = hits or master.by_name.get(name_key(INDEX_ALIASES.get(acr, "")), []) or (master.by_domain.get(domain(site), []) if site else [])
        hits = hits or [oid for oid, o in master.orgs.items() if str(o["segment"]).startswith("Introducer") and f"({acr})" in (o["name"] or "")]
        if register:
            decision, detail, oid = "skipped", "regulator register or explanatory row, not an association (its members are on a member tab)", ""
        elif hits:
            decision, detail, oid = "master_match", "introducer already in the master", hits[0]
        elif acr in PLANNED_INTRODUCERS and site:
            decision, detail, oid = "introducer_new", "added as an introducer (Index row: website, sector and source)", hid("O", "introducer",
                                                                                                                            re.sub(r"[^a-z0-9]", "", re.sub(r"\([^)]*\)", "", f"{name} ({acr})".lower())))
        elif acr in PLANNED_INTRODUCERS:
            decision, detail, oid = "national", "planned introducer skipped: no website and no published route in the source", ""
        else:
            decision, detail, oid = "national", "association outside the approved list of introducers (listed, not added)", ""
        rec = {"row_id": f"Index:{ix['sheet_row']}", "tab": "Index", "tab_key": "Index", "sheet_row": ix["sheet_row"],
               "source_location": f"'Index'!A{ix['sheet_row']}", "source_line": ix["source_line"], "note": ix["note"],
               "source_url": site or "", "source_date": CHECKED_ON, "evidence_basis": "directory", "name": f"{name} ({acr})" if acr else name,
               "acronym": acr, "sector": v.get("Sector", ""), "website": site, "members_published": v.get("Members (as published)", ""),
               "member_list": v.get("Member list", ""), "tpsf": v.get("TPSF membership (as published)", ""), "source_checked": v.get("Source checked", ""),
               "decision": decision, "decision_detail": detail, "organisation_id": oid,
               "national_lead_id": "" if decision == "skipped" else hid("N", "association", acr or name_key(name))}
        index_out.append(rec)
        if decision == "introducer_new":
            introducers.append({"name": f"{name} ({acr})", "kind": INTRODUCER_KIND, "members": f"{v.get('Sector', '')} businesses (members of {acr})",
                                "member_count": "" if v.get("Members (as published)", "") == "Not stated" else v.get("Members (as published)", ""),
                                "area": "national", "website": site, "emails": [], "phones": [], "postal_address": "", "physical_address": "",
                                "people": [], "channels": [],
                                "sources": [{"url": site, "title": f"{source_path}, Index row {ix['sheet_row']}", "accessed_on": CHECKED_ON,
                                             "excerpt": f"{name}, {acr}, sector {v.get('Sector', '')}, website {v.get('Website', '')}; source checked: {v.get('Source checked', '')}"}],
                                "notes": (f"From the team's association workbook (Index row {ix['sheet_row']}, checked {CHECKED_ON}); sector {v.get('Sector', '')}; "
                                          f"TPSF membership: {v.get('TPSF membership (as published)', '')}. No email, phone or secretariat person in the source and "
                                          "none in the crawl cache: the route is still to find."),
                                "verification": f"Listed in the team's association workbook (Index row {ix['sheet_row']}, checked {CHECKED_ON}); unverified; no route yet",
                                "source_row": f"Index:{ix['sheet_row']}"})

    # Banks: head offices from the TBA tab, with the master branch records they match.
    banks = []
    for r in rows:
        if r["tab_key"] != "TBA":
            continue
        branch_ids = [x for x in [r["organisation_id"], *r["also_matches"]] if x and r["decision"] == "master_match"]
        banks.append({"bank": r["name"], "type": r["fields"]["member_category"], "row_id": r["row_id"], "sheet_row": r["sheet_row"],
                      "head_office_phone": r["fields"]["phone"], "head_office_email": (r["fields"]["emails"] or [""])[0],
                      "other_emails": r["fields"]["emails"][1:], "website": r["fields"]["website"],
                      "head_office_region": r["fields"]["region"], "head_office_district": r["fields"]["district"],
                      "match_basis": r["match_basis"], "branch_organisation_ids": branch_ids,
                      "branch_names": [master.orgs[x]["name"] for x in branch_ids]})

    # ------------------------------------------------------------------ write
    OUT.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    members_path = OUT / f"members_{args.date}.jsonl"
    with members_path.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in index_out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        for r in rows:
            fh.write(json.dumps({k: v for k, v in r.items() if k != "values"}, ensure_ascii=False) + "\n")

    header = next(csv.reader(TEMPLATE.open(encoding="utf-8-sig")))
    extra = ["source_row", "source_tab", "sheet_row", "association", "association_acronym", "member_category", "licence_no", "status",
             "district", "region", "catchment_council", "council_core", "placement_basis", "decision", "match_organisation_id", "match_basis",
             "new_organisation_id", "national_lead_id", "other_emails", "personal_inbox_count", "whatsapp", "contact_person_published",
             "similar_master_ids"]
    intake_path = OUT / f"master_intake_{args.date}.csv"
    with intake_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header + [c for c in extra if c not in header], extrasaction="ignore")
        w.writeheader()
        for r in rows:
            if r["decision"] not in ("master_new", "master_match"):
                continue
            f = r["fields"]
            own = [e for e in f["emails"] if e not in f["personal_inboxes"]]
            segment, subtype = master_labels(r, f)
            site = f["website"]
            excerpt = (f"{r['name']}: {f['member_category']}" + (f", licence {f['licence_no']}" if f["licence_no"] and r["tab_key"] != "SACCOS" else "")
                       + (f"; {f['district']}, {f['region']}" if f["district"] or f["region"] else "") + f" ({TABS[r['tab']][1]})")
            w.writerow({
                "record_type": "organisation", "source_path": source_path, "source_location": r["source_location"], "source_url": r["source_url"],
                "source_date": r["source_date"], "acquired_on": CHECKED_ON, "verified_on": CHECKED_ON, "verification_status": "unverified",
                "evidence_basis": r["evidence_basis"], "evidence_excerpt": excerpt[:500],
                "notes": f"{r['title'] if False else ''}{r['source_line']} | {r['note']}"[:1000],
                "organisation_name": display_name(r["name"], r["tab_key"]), "organisation_domain": domain(site),
                "segment": segment, "subtype": subtype, "locality": ", ".join(x for x in (f["district"].title(), f["region"].title()) if x),
                "address": "; ".join(x for x in (f["physical_address"], f["postal_address"]) if x), "website": site,
                "public_email": own[0] if own else "", "public_phone": f["phone"], "licence_class": f["licence_no"],
                "source_row": r["row_id"], "source_tab": r["tab"], "sheet_row": r["sheet_row"], "association": f["association"],
                "association_acronym": f["association_acronym"], "member_category": f["member_category"], "licence_no": f["licence_no"],
                "status": f["status"], "district": f["district"], "region": f["region"], "catchment_council": r["placement"]["council"],
                "council_core": "yes" if r["placement"]["core"] else ("no" if r["placement"]["council"] else ""),
                "placement_basis": r["placement"]["basis"], "decision": r["decision"],
                "match_organisation_id": r["organisation_id"] if r["decision"] == "master_match" else "", "match_basis": r["match_basis"],
                "new_organisation_id": r["organisation_id"] if r["decision"] == "master_new" else "", "national_lead_id": r["national_lead_id"],
                "other_emails": "; ".join(own[1:]), "personal_inbox_count": len(f["personal_inboxes"]), "whatsapp": f["whatsapp"],
                "contact_person_published": "yes" if f["contact_person_published"] else "", "similar_master_ids": "; ".join(r["similar_master"]),
                "review_status": "research_only"})

    banks_path = OUT / f"bank_head_offices_{args.date}.json"
    banks_path.write_text(json.dumps({"source": source_path, "tab": "TBA (Bankers)", "checked_on": CHECKED_ON,
                                      "rule": "A bank's head office (TBA tab: the Bank of Tanzania register's phone and email) is the escalation contact of "
                                              "its branch records in the master; the branch stays the primary recipient (on-the-ground rule).",
                                      "banks": banks}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    intro_path = INTRODUCERS / f"introducers_associations_{args.date}.jsonl"
    with intro_path.open("w", encoding="utf-8", newline="\n") as fh:
        for rec in introducers:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------ summary and conservation
    per_tab = defaultdict(Counter)
    for r in rows:
        per_tab[r["tab"]]["rows"] += 1
        per_tab[r["tab"]][r["decision"]] += 1
        per_tab[r["tab"]][f"placement:{r['placement']['placement']}"] += 1
        if r["decision"] == "national":
            per_tab[r["tab"]][f"national:{r['decision_detail'].split(' (')[0]}"] += 1
    leads = defaultdict(list)
    for r in rows:
        leads[r["national_lead_id"]].append(r)
    flags = Counter()
    for nid_, members_ in leads.items():
        if any(m["decision"] == "master_match" for m in members_):
            flags["in master"] += 1
        elif any(m["decision"] == "master_new" for m in members_):
            flags["in catchment"] += 1
        else:
            flags["national only"] += 1
    summary = {
        "source": source_path, "date": args.date, "skipped_tabs": skipped_tabs,
        "index_rows": len(index_out), "index_decisions": dict(Counter(x["decision"] for x in index_out)),
        "member_rows": len(rows), "per_tab": {k: dict(v) for k, v in per_tab.items()},
        "decisions": dict(Counter(r["decision"] for r in rows)),
        "new_organisations": len(new_ids), "matched_organisations": len({r["organisation_id"] for r in rows if r["decision"] == "master_match"}),
        "national_leads_from_members": len(leads), "national_flags": dict(flags),
        "duplicate_names": sum(1 for v in leads.values() if len(v) > 1),
        "conservation": {"member_rows": len(rows),
                         "to_master_new_rows": sum(1 for r in rows if r["decision"] == "master_new"),
                         "to_master_matched_rows": sum(1 for r in rows if r["decision"] == "master_match"),
                         "to_national_rows": sum(1 for r in rows if r["decision"] == "national")},
        "banks_with_master_branches": sum(1 for b in banks if b["branch_organisation_ids"]), "introducers_new": len(introducers),
        "outputs": [p.relative_to(ROOT).as_posix() for p in (members_path, intake_path, banks_path, intro_path)],
    }
    c = summary["conservation"]
    c["check"] = f"{c['member_rows']} = {c['to_master_new_rows']} + {c['to_master_matched_rows']} + {c['to_national_rows']}"
    assert c["member_rows"] == c["to_master_new_rows"] + c["to_master_matched_rows"] + c["to_national_rows"]
    (RUNTIME / f"build-summary-{args.date}.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
