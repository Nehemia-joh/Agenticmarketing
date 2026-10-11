#!/usr/bin/env python3
"""Draft offer-aligned messages into a separate run database (welfare or government). A pipeline step.

Runs after the run database is built (initialize_lead_db.py plus the track's augment step) and before its workbook.
It replaces the run's messages and outreach_plans, so it is safe to repeat. Terms come only from
data/reference/silverleaf-offer-register.json and every draft is checked against it.

Welfare (plans/b2b-welfare-leads-plan.md): one English sequence per in-scope organisation, request first (23 September
2026). The first message asks for a short meeting and states no offer terms: about the education of the children in a
home's or programme's care, or, for funders only, a request to sponsor students, with the funder's verified support
for a home as the reason when the run records one. The follow-up states the offer: the NGO partner rate (OF03), the
free uniform (OF01) and four instalments (OF09). One neutral reply goes to each current, in-fit public parent enquiry.
Routes come from the organisation or a low- or medium-risk contact, never a risky one. WA01 organisations with a route
are 'draft_ready'; everything else is held.
First touch (docs/strategy/partnership-pipelines-draft.md section 4, approved 11 October 2026; first_touch.py): a named leader at their
own or role address keeps the letter; a named leader reached only through a general inbox gets the Attn subject and routing line; an
organisation with no named leader gets the short redirect request (homes and programmes: who leads the home; funders: the programme
officer for Tanzania; networks: the executive secretary or CEO), with no follow-up and the planned next touch as a note.
A case B draft (the Attn format) follows the named-person fallout (section 5, applied 11 October 2026): follow-up 1 (<id>-F1) is the
segment's offer follow-up, follow-up 2 (<id>-F2) a short close with its redirect-style ask (the head of the home or programme, the
programme officer, or who handles member communications), and an escalation contact, if any, is noted for one message after the close.
Reviewed decisions in the run's links.json: recipient_exclusions (never the addressee) and recipient_choices (the in-country lead, with
the overseas executive as escalation). The leader's role inbox on the organisation's domain counts as their address (D2).

Government (plans/b2b-government-leads-plan.md): one Kiswahili letter per office with an English meaning for review.
Councils get the GA01 introduction letter, wards and villages the convening request (held until GA01), district and
regional offices a courtesy notice. Letters describe only the family offer (OF01, OF02, OF09) for parents and never
offer officials a benefit.

Nothing is sent; drafts stay 'draft_ready' or 'needs_review'.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone

import first_touch as FT
import offer_lib as L

ROOT = L.ROOT
WELFARE_OFFERS = ["OF03", "OF01", "OF09"]
FAMILY_OFFERS = ["OF01", "OF02", "OF09"]
PERSONAL_DOMAIN = re.compile(r"@(gmail|yahoo|ymail|hotmail|outlook|live|icloud|aol|rocketmail)\.", re.I)


def sid(*parts) -> str:
    return "M" + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def payloads(con, entity_type) -> dict:
    out = {}
    for eid, payload in con.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr "
                                    "ON sr.source_record_id = es.source_record_id WHERE es.entity_type = ?", (entity_type,)):
        out.setdefault(eid, json.loads(payload))
    return out


def prepare(con) -> None:
    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    for column in ("contact_route", "route_value", "recipient", "language", "offer_ids", "offer_version", "follow_up_message_id",
                   "translation_message_id", "subject", "outcome", "follow_up_2_message_id"):
        if column not in columns:
            con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
    con.execute("DELETE FROM outreach_plans")
    con.execute("DELETE FROM messages")


def add(con, now, plan: dict, subject: str, body: str, follow_up: str = "", translation: str = "", version: str = "offer-v4",
        follow_up_2: str = "") -> None:
    """The plan and its messages: the first message, follow-up 1 (<id>-F1), follow-up 2 (<id>-F2, the close of a case B welfare draft)
    and the English meaning (<id>-EN). Follow-ups go in the same thread ('Re: <subject>')."""
    mid = plan["message_id"]
    con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid, plan["target_id"], plan["target_type"], subject, body, version,
                                                                 plan["review_status"], now))
    if follow_up:
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid + "-F1", plan["target_id"], plan["target_type"], f"Re: {subject}",
                                                                     follow_up, version + " follow-up 1", plan["review_status"], now))
    if follow_up_2:
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid + "-F2", plan["target_id"], plan["target_type"], f"Re: {subject}",
                                                                     follow_up_2, version + " follow-up 2", plan["review_status"], now))
    if translation:
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid + "-EN", plan["target_id"], plan["target_type"], f"English meaning: {subject}",
                                                                     translation, version + " English meaning for review", plan["review_status"], now))
    con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, relevance_reason, proposed_offer, cta_type, hook,
                   hook_source_url, hook_verified_on, acquisition_track_id, value_module_ids, review_status, missing_information, contact_route,
                   route_value, recipient, language, offer_ids, offer_version, follow_up_message_id, translation_message_id, subject, outcome,
                   follow_up_2_message_id)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (mid, plan["target_id"], plan["target_type"], plan.get("organisation_id"), plan["relevance_reason"],
                 "; ".join(f"{i} {L.OFFERS[i]['name']}" for i in plan["offer_ids"]), plan["cta_type"], plan.get("hook", ""),
                 plan.get("hook_source_url", ""), plan.get("hook_verified_on", ""), plan["track"], plan["modules"],
                 plan["review_status"], "; ".join(plan["missing"]), plan.get("contact_route", ""), plan.get("route_value", ""), plan.get("recipient", ""),
                 plan["language"], "; ".join(plan["offer_ids"]), L.OFFER_VERSION, mid + "-F1" if follow_up else "", mid + "-EN" if translation else "",
                 subject, plan["outcome"], mid + "-F2" if follow_up_2 else ""))


# ------------------------------------------------------------------ welfare
def precise(p: dict) -> bool:
    return str(p.get("geocode_precision") or "") in ("address", "locality", "point") and p.get("distance_km") not in (None, "")


greeting_name = L.greeting_name


def funder_reasons(con) -> dict:
    """For each funder, the home or programme it supports or runs, from a verified 'funds' or 'operates' relationship with a fetched source: the
    sourced reason for its sponsorship request. A source that is the page itself is preferred to a search-results page. The source URL and date go
    with the plan as its hook."""
    names = dict(con.execute("SELECT organisation_id, name FROM organisations").fetchall())
    candidates = {}
    for funder, kind, supported, supported_id, sources in con.execute(
            "SELECT from_organisation_id, relationship_type, to_organisation, to_organisation_id, sources_json FROM organisation_relationships "
            "WHERE relationship_type IN ('funds','operates') AND verification_status='verified' ORDER BY to_organisation"):
        fetched = [s for s in json.loads(sources or "[]") if s.get("fetched") and s.get("url")]
        fetched.sort(key=lambda s: "full_text_search" in s["url"])
        if funder and fetched:
            candidates.setdefault(funder, []).append((
                "full_text_search" in fetched[0]["url"], kind != "funds",
                {"supported": L.display_name(names.get(supported_id) or supported), "verb": "supports" if kind == "funds" else "runs",
                 "url": fetched[0]["url"], "verified_on": fetched[0].get("accessed_on", "")}))
    return {f: min(c, key=lambda t: (t[0], t[1]))[2] for f, c in candidates.items()}


LEADER_TOP = re.compile(r"founder|owner|\bceo\b|chief executive|executive director|president|chair|director(?!s)|bishop|head of\b|"
                        r"general secretary|secretary[- ]general|executive secretary", re.I)
LEADER_MID = re.compile(r"manager|coordinator|pastor|leader|principal|administrator|matron|in[- ]charge|mother superior|management committee", re.I)
NOT_LEADER = re.compile(r"treasurer|secretary|volunteer|intern|assistant|adviser|advisor|trustee|board member|accountant|nurse|teacher|social worker|"
                        r"programme officer|vice|deputy", re.I)
SECRETARY_LEADER = re.compile(r"general secretary|secretary[- ]general|executive secretary", re.I)
ROLE_PARTS = re.compile(r"\s*(?:[;,/&()]|\band\b|\s-\s)\s*", re.I)
FOREIGN_ROUTE = re.compile(r"kenya|uganda|rwanda|burundi|zambia|malawi|congo|southafrica|\.(ke|ug|rw|bi|cd|zm|mw|za)$", re.I)


# Board roles are never an addressee or an escalation contact (decided 10 October 2026): a chair, vice chair, treasurer, secretary, trustee,
# board member or emeritus, a "Director, <country>" board seat, and a president or chair qualified by a board ("President (US board)").
BOARD = re.compile(r"\bchair|vorsitz|voorzitter|vorstand|treasurer|(?<!general )(?<!executive )\bsecretary(?![- ]general)|board|trustee|emeritus", re.I)
BOARD_TITLE = re.compile(r"\b(president|chair\w*|director)\s*\(([^)]*\b(?:board|trustees|vorstand)\b[^)]*)\)", re.I)
PLACE = (r"tanzania|kenya|uganda|rwanda|burundi|zambia|malawi|congo|ethiopia|south africa|east africa|north america|usa|us|uk|europe|"
         r"germany|netherlands|switzerland|australia|canada|norway|finland|sweden|denmark|austria|italy|spain")
DIRECTOR_SEAT = re.compile(rf"(?:board )?director\s*[,(\-]\s*(?:{PLACE})\s*\)?", re.I)
# Where a role says the person works: Tanzania (the operation Silverleaf would deal with), another African country's operation, or abroad.
IN_TANZANIA = re.compile(r"tanzania|arusha|moshi|kilimanjaro|usa river|karatu|mto wa mbu|monduli|meru|zanzibar|in-country|on-site|\btz\b", re.I)
OTHER_AFRICA = re.compile(r"kenya|uganda|rwanda|burundi|zambia|malawi|congo|south africa|ethiopia|nigeria|ghana", re.I)
ABROAD = re.compile(r"\bglobal\b|international|north america|\busa?\b|u\.s\.|united states|\buk\b|united kingdom|german|netherlands|nederland|dutch|"
                    r"swiss|switzerland|australia|canada|europe|norway|finland|sweden|denmark|austria|ital|spain|parent|head office|headquarters", re.I)
# The most senior person running the Tanzania or Arusha operation: a country manager or director, a national director, a Tanzania head, or an
# Arusha programme or home manager.
COUNTRY_HEAD = re.compile(r"country (?:manager|director|representative|coordinator|lead|head)|national (?:director|coordinator|manager)|"
                          r"in-country (?:director|manager|lead)|head of (?:the )?(?:tanzania|country)|tanzania (?:programme |program |country )?"
                          r"(?:director|manager|lead|head)|(?:tanzania|arusha) programme lead|programme lead", re.I)
# A named house counts as a home (ProManity's Pippi House in Arusha, whose head is its on-site supervisor; 10 October 2026); a bare
# 'Head of House' (a hostel or household role) does not.
HOME_HEAD = re.compile(r"head of (?:the )?(?:(?:[\w'-]+ ){0,3}(?:home|orphanage|children's village)|(?:[\w'-]+ ){1,3}house)\b|"
                       r"on-site (?:director|manager|head)", re.I)
LOCAL_MANAGER = re.compile(r"(?:programme|program|project|home|centre|center|site|orphanage|village) (?:manager|director|lead|head)", re.I)


def board_role(role: str) -> bool:
    """A board seat with no executive title beside it (see BOARD)."""
    role = " ".join(str(role or "").split())
    return bool(DIRECTOR_SEAT.fullmatch(role)) or (bool(role) and leader_rank(role) is None and bool(BOARD.search(role)))


def role_location(role: str, funder: bool = False) -> str:
    """'tz' when the role names Tanzania or a place in it, 'other' for another African country's operation, 'abroad' for a global,
    head-office or overseas title, '' when the role does not say. A funder is based abroad itself, so its overseas titles count as ''."""
    role = str(role or "")
    if IN_TANZANIA.search(role):
        return "tz"
    if OTHER_AFRICA.search(role):
        return "other"
    return "" if funder or not ABROAD.search(role) else "abroad"


def country_head(role: str) -> bool:
    """The person runs the Tanzania or Arusha operation (see COUNTRY_HEAD; a programme or home manager counts when the role names Tanzania)."""
    role = str(role or "")
    if OTHER_AFRICA.search(role) and not IN_TANZANIA.search(role) or board_role(role):
        return False
    return bool(COUNTRY_HEAD.search(role) or HOME_HEAD.search(role) or (LOCAL_MANAGER.search(role) and IN_TANZANIA.search(role)))


def leader_rank(role: str):
    """0 founder, owner, chief executive, director, president or general secretary; 1 manager, coordinator or matron; None for anyone else
    (a board role, treasurer, volunteer, vice or deputy). A role that joins several titles ('Founder and trustee', 'Director/Social Worker',
    'Founder; board member of the German association') ranks by its most senior title: a second title never hides a founder or director,
    and a board title never makes a leader."""
    role = BOARD_TITLE.sub(lambda m: f"board {m.group(1)} ({m.group(2)})", str(role or ""))
    if DIRECTOR_SEAT.fullmatch(" ".join(role.split())):
        return None
    ranks = []
    parts = [p for p in ROLE_PARTS.split(role) if p.strip()]
    on_board = any(BOARD.search(p) for p in parts)
    for part in parts:
        if on_board and re.fullmatch(r"\s*(?:co-)?president\s*", part, re.I):
            continue  # 'Board Member, President': the president of the board
        if SECRETARY_LEADER.search(part) and not re.search(r"vice|deputy|assistant|former", part, re.I):
            ranks.append(0)  # a general or executive secretary runs the body
        elif BOARD.search(part) or NOT_LEADER.search(part):
            continue
        elif LEADER_TOP.search(part):
            ranks.append(0)
        elif LEADER_MID.search(part):
            ranks.append(1)
    return min(ranks) if ranks else None


SENIORITY = [re.compile(r"\bceo\b|chief executive|executive director|national director|country director|managing director|general secretary|"
                        r"secretary[- ]general", re.I),
             re.compile(r"(?<!co-)(?<!co )founder|president|chair", re.I)]


def seniority(role: str) -> int:
    """Among leaders of the same rank: 0 chief executive or national director, 1 founder, president or chair, 2 any other leader
    (co-founder, director of a unit, head of a programme). Only titles the person holds count, not vice or deputy ones."""
    parts = [p for p in ROLE_PARTS.split(role or "") if p.strip() and leader_rank(p) is not None]
    return min((i for i, pattern in enumerate(SENIORITY) for p in parts if pattern.search(p)), default=len(SENIORITY))


def site_domain(url) -> str:
    """The bare host of a website ('https://www.x.org/en/' -> 'x.org'), or ''."""
    host = re.sub(r"^https?://", "", str(url or "").strip().lower()).split("/")[0]
    return re.sub(r"^www\.", "", host)


def role_phrase(role: str, organisation: str = "") -> str:
    """How a published role reads in 'I understand that you are ... of <organisation>'; '' when it is too long or messy to quote."""
    role = " ".join(str(role or "").split())
    if role.isupper():
        role = role.title()
    # 'Founder & CEO of Inuka' before 'of Inuka': drop the role's own trailing 'of/at <organisation>'.
    head = next((w for w in re.findall(r"[A-Za-z]{3,}", organisation or "") if w.lower() not in {"the", "and", "for"}), "")
    if head:
        role = re.sub(r"\s+(?:of|at)\s+(?:the\s+)?" + re.escape(head) + r"\b.*$", "", role, flags=re.I)
    # 'Group Chairman, Capital International Group' -> 'Group Chairman'; 'Founder, Executive Director' -> 'Founder and Executive Director'.
    first, *rest = [p.strip() for p in role.split(",")]
    role = " and ".join([first] + [p for p in rest if p and leader_rank(p) is not None])
    if not role or len(role) > 45 or re.search(r"[();/]", role):
        return ""
    return f"a {role.lower()}" if role.lower().startswith("co-") else f"the {role}"


# An executive title held on its own: the organisation's director, managing or executive director, owner or (co-)founder. A director of a
# function ('Director of Marketing', 'Creative Director', 'Medical Director') is not the organisation's executive.
EXEC_PART = re.compile(r"\s*(?:the\s+)?(?:managing\s+|executive\s+|general\s+|founding\s+|co-?\s*)?(?:director|owners?|founder)\s*", re.I)


def executive_title(role: str) -> bool:
    """The role holds a chief executive's, executive director's, founder's or president's title (seniority 0 or 1) or one in EXEC_PART."""
    parts = [p for p in ROLE_PARTS.split(role or "") if p.strip() and leader_rank(p) is not None]
    return seniority(role) <= 1 or any(EXEC_PART.fullmatch(p) for p in parts)


def named_leaders(contacts, funder: bool = False) -> list[dict]:
    """The named, confirmed, medium-risk contacts with a full name and a leader's role (never a board role or a person who works for
    another country's operation), each with greet_name and: _rank, _seniority, _where (role_location), _head (runs the Tanzania operation),
    _exec (the organisation's executive: chief executive, executive director, founder, president or its director, not a function's director) and
    _overseas (based abroad, or, when a country head is named, an executive whose role does not name Tanzania: head office)."""
    out = []
    for c in contacts:
        name, role = greeting_name(c.get("contact_name") or ""), c.get("role") or ""
        rank = leader_rank(role)
        if (c.get("pdpa_risk") != "medium" or c.get("role_certainty") != "confirmed" or len(name.split()) < 2 or re.search(r"\d|\?", name)
                or re.search(r"enquir|inbox|\boffice\b|\bteam\b", name, re.I) or rank is None or board_role(role)):
            continue
        where = role_location(role, funder)
        if where == "other":
            continue
        head, level = country_head(role), seniority(role)
        out.append({**c, "greet_name": name, "_rank": 0 if head else rank, "_where": where, "_head": head, "_seniority": level,
                    "_exec": not head and executive_title(role),
                    "_has_email": bool(c.get("named_email") or c.get("published_role_email"))})
    has_head = any(c["_head"] for c in out)
    for c in out:
        c["_overseas"] = c["_where"] == "abroad" or (has_head and c["_exec"] and c["_where"] != "tz" and c["_seniority"] <= 1)
    return out


# A chair or president of the body (Vorsitzender, voorzitter, chairperson, board president) may be the addressee only when the organisation
# names no executive and no one in the country (decided 10 October 2026); a vice chair, treasurer, secretary or emeritus never is.
CHAIR = re.compile(r"\bchair|vorsitz|voorzitter|1\.\s*vorstand|president", re.I)
NOT_CHAIR = re.compile(r"vice|deputy|assistant|emeritus|former", re.I)


def named_chairs(contacts, funder: bool = False) -> list[dict]:
    """The named, confirmed, medium-risk chairs or presidents of the body whose role is a board role only (see CHAIR)."""
    out = []
    for c in contacts:
        name, role = greeting_name(c.get("contact_name") or ""), " ".join(str(c.get("role") or "").split())
        if (c.get("pdpa_risk") != "medium" or c.get("role_certainty") != "confirmed" or len(name.split()) < 2 or re.search(r"\d|\?", name)
                or re.search(r"enquir|inbox|\boffice\b|\bteam\b", name, re.I) or leader_rank(role) is not None or DIRECTOR_SEAT.fullmatch(role)
                or not CHAIR.search(role) or NOT_CHAIR.search(role)):
            continue
        where = role_location(role, funder)
        if where == "other":
            continue
        out.append({**c, "greet_name": name, "_rank": 0, "_where": where, "_head": False, "_seniority": 1, "_exec": False, "_chair": True,
                    "_overseas": False, "_has_email": bool(c.get("named_email") or c.get("published_role_email"))})
    return out


def best_chair(contacts, funder: bool = False) -> dict | None:
    """The body's chair: the chair of the organisation before the chair of a committee, one with a published address first."""
    people = named_chairs(contacts, funder)
    key = lambda c: (bool(re.search(r"committee", c.get("role") or "", re.I)), not c["_has_email"], c["greet_name"])  # noqa: E731
    return min(people, key=key) if people else None


def best_leader(contacts, prefer=None, funder: bool = False) -> dict | None:
    """The addressee (decided 10 October 2026: someone on the ground). First the most senior person running the Tanzania or Arusha
    operation (country manager or director, national director, Tanzania head, the head of a home, an Arusha programme manager); otherwise
    the organisation's most senior named leader, a local founder or director first. A global or overseas chief executive, executive director,
    founder or president is the fallback when no one in the country is named, and the body's chair or president only when no executive and
    no one in the country is named. A vice chair, treasurer, secretary, emeritus or other board seat, a person working for another country's
    operation and a non-executive based abroad are never chosen."""
    best = None
    for c in named_leaders(contacts, funder):
        if c["_where"] == "abroad" and not c["_exec"]:
            continue  # based abroad and not the organisation's executive (a marketing manager in the USA)
        preferred = 0 if prefer and prefer.search(c.get("role") or "") else 1  # for a network: the social-services or children's lead before the bishop
        key = (preferred, c["_overseas"], not c["_head"], c["_rank"], not c["_exec"], not c["_has_email"], c["_seniority"], c["greet_name"])
        if best is None or key < best[0]:
            best = (key, c)
    return best[1] if best else best_chair(contacts, funder)


def chosen_person(contacts, name: str) -> dict | None:
    """The contact a reviewed choice names, shaped like a named_leaders entry (links.json recipient_choices)."""
    key = lambda s: " ".join(re.findall(r"[a-z0-9]+", greeting_name(s or "").lower()))  # noqa: E731
    hits = [c for c in contacts if key(c.get("contact_name") or c.get("name")) == key(name) and c.get("pdpa_risk") != "risky"]
    if not hits:
        return None
    c = hits[0]
    return {**c, "greet_name": greeting_name(c.get("contact_name") or c.get("name") or ""), "_rank": 0, "_where": "tz", "_head": True,
            "_seniority": 1, "_exec": True, "_overseas": False, "_has_email": bool(c.get("named_email") or c.get("published_role_email"))}


def role_inbox_for(local: str, role: str) -> bool:
    """D2: the inbox for this exact role (scripts/contacts/extract_direct_emails.py ROLE_INBOX)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
    import extract_direct_emails as E  # noqa: E402
    return E.role_inbox_for(local, role)


# A case B welfare draft whose segment has no follow-up content in the offer register gets a blank follow-up 1 and this note, never invented copy.
NO_APPROVED_FOLLOW_UP = "Follow-up 1 awaiting approved copy: the offer register has no follow-up content for this segment."
ESCALATION_TRIGGER = "No reply after the follow-up, or the country office declines or defers to head office."
# escalation_route holds the address or phone (the companies master and the Resend exporter read these four by name); the other two are
# the welfare run's own detail: what kind of route it is and where the executive is published.
ESCALATION_COLUMNS = ("escalation_contact_id", "escalation_recipient", "escalation_route", "escalation_trigger", "escalation_route_type",
                      "escalation_source_url")


def escalation_contact(contacts, leader, funder: bool = False) -> dict | None:
    """A more senior person to escalate to by hand. No message is drafted to them and they are not copied on the first message.
    - The addressee runs the Tanzania operation, or is an executive whose role names Tanzania: the organisation's executive abroad or at
      head office (a global chief executive, executive director, founder or president), never less senior than the addressee.
    - The addressee is a local person who is not an executive (a coordinator, volunteer, programme officer or unit director): the
      organisation's most senior executive, or its chair or president when no executive is named.
    - The addressee is the chair: none (there is no executive)."""
    if not leader or leader.get("_chair") or leader.get("_overseas"):
        return None
    remit = lambda c: not re.search(r"orphan|child|home|welfare|programme|program", c.get("role") or "", re.I)  # noqa: E731
    people = [c for c in named_leaders(contacts, funder) if c.get("contact_id") != leader.get("contact_id")]
    if not leader["_head"] and not leader["_exec"]:
        execs = [c for c in people if c["_exec"]]
        if execs:  # on a tie, the executive whose remit names the children's work
            return min(execs, key=lambda c: (c["_seniority"], c["_rank"], not c["_has_email"], remit(c), c["greet_name"]))
        return best_chair(contacts, funder)
    if not (leader["_head"] or leader["_where"] == "tz"):
        return None
    best = None
    for c in people:
        if (not (c["_overseas"] and c["_exec"]) or c["_seniority"] > 1
                or (not leader["_head"] and c["_seniority"] > leader["_seniority"])):
            continue  # only a chief executive, executive director, founder or president, and never less senior than the addressee
        # on a tie, the executive whose remit names the children's work (a co-president for 'medicine and orphanages')
        key = (c["_seniority"], not c["_has_email"], remit(c), c["greet_name"])
        if best is None or key < best[0]:
            best = (key, c)
    return best[1] if best else None


def welfare(con, now, run_cfg) -> dict:
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    for column in ESCALATION_COLUMNS:  # welfare only: who to escalate to by hand when the country office stalls
        if column not in columns:
            con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
    # Reviewed decisions (links.json official_personal_inboxes): the organisation itself publishes this personal-domain address as its contact.
    links_path = ROOT / "data" / "runs" / run_cfg.get("run_id", "") / "links.json"
    links = json.loads(links_path.read_text(encoding="utf-8")) if links_path.exists() else {}
    official_inboxes = links.get("official_personal_inboxes", {})
    # Reviewed decisions (links.json recipient_exclusions, added 11 October 2026): a person recorded for an organisation who is never its
    # addressee or escalation contact (a public figure listed on the site), by organisation name and person name.
    key = lambda s: " ".join(re.findall(r"[a-z0-9]+", str(s or "").lower()))  # noqa: E731
    excluded = {(key(org), key(x["name"])) for org, items in links.get("recipient_exclusions", {}).items() for x in items}
    # Reviewed recipient choices (links.json recipient_choices, added 11 October 2026): {organisation name: {name, escalation?, reason, ...}}.
    choices = {key(org): c for org, c in links.get("recipient_choices", {}).items()}
    org_payload, con_payload = payloads(con, "organisation"), payloads(con, "contact")
    org_names = {r["organisation_id"]: r["name"] for r in con.execute("SELECT organisation_id, name FROM organisations")}
    contacts_by_org = {}
    for r in con.execute("SELECT * FROM contacts ORDER BY contact_id"):
        if (key(org_names.get(r["organisation_id"], "")), key(r["name"])) in excluded:
            continue
        contacts_by_org.setdefault(r["organisation_id"], []).append({**dict(r), **con_payload.get(r["contact_id"], {})})
    # Same-named twins (one body's funder record and its programme record) keep their own contacts in the run; its people lead both, so
    # each twin's draft chooses from the contacts of all of them (its own first on a tie).
    twins = {}
    for oid, o in orgs.items():
        twins.setdefault(" ".join(re.findall(r"[a-z0-9]+", str(o["name"]).lower())), []).append(oid)
    people_of = {oid: contacts_by_org.get(oid, []) + [c for t in group if t != oid for c in contacts_by_org.get(t, [])]
                 for group in twins.values() for oid in group}
    outcomes, issues = Counter(), []
    reasons = funder_reasons(con)
    for oid, o in sorted(orgs.items(), key=lambda kv: kv[1]["name"]):
        p = {**org_payload.get(oid, {}), **{k: v for k, v in o.items() if v not in (None, "")}}
        track = p.get("proposed_welfare_track") or "WA00 Hold"
        if track == "Excluded" or p.get("segment") == "Out of scope":
            outcomes["excluded: no message"] += 1
            continue
        model = p.get("care_model") or ""
        name = L.display_name(o["name"], oid)
        missing = [L.REQUEST_FIRST, L.CONFIRM_2027]
        # Route: the organisation's own published email or phone first; otherwise a low- or medium-risk contact; never a risky one.
        route, value, recipient = "", "", ""
        if p.get("email") and p.get("pdpa_risk") != "risky":
            route, value = "shared_email", p["email"]
        elif p.get("phone") and p.get("pdpa_risk") != "risky":
            route, value = "organisation_phone", p["phone"]
        network = model == "network" or str(p.get("segment") or "").startswith("Welfare network")
        is_funder = model == "funder" or p.get("segment") == "Welfare funder"
        leader = best_leader(people_of.get(oid, []), re.compile(r"diacon|social|children|programme|program|coordinator|welfare", re.I) if network else None,
                             is_funder)
        escalate = escalation_contact(people_of.get(oid, []), leader, is_funder)
        choice = choices.get(key(o["name"]))
        if choice:  # a reviewed choice (links.json recipient_choices): the in-country lead, and the overseas executive as escalation
            leader = chosen_person(people_of.get(oid, []), choice["name"]) or leader
            if choice.get("escalation"):
                escalate = chosen_person(people_of.get(oid, []), choice["escalation"]) or escalate
            elif leader:
                escalate = escalation_contact(people_of.get(oid, []), leader, is_funder)
        greet = f"Dear {leader['greet_name']}," if leader else f"Dear {name} team,"
        recipient = f"{leader['greet_name']} ({leader.get('role') or 'role not published'})" if leader else ""
        for c in contacts_by_org.get(oid, []):
            if c.get("pdpa_risk") == "risky":
                continue
            email = c.get("named_email") or c.get("published_role_email") or c.get("shared_email")
            if c.get("email_type") == "personal_domain":
                email = ""
            if email or c.get("role_phone") or c.get("organisation_phone"):
                if not route:
                    route = "named_email" if c.get("named_email") and email else ("published_role_email" if email else "role_phone")
                    value = email or c.get("role_phone") or c.get("organisation_phone")
                break
        # The named leader's own published address on the organisation's domain reaches the person who decides: it is used ahead of
        # the shared inbox or another person's address (decided 10 October 2026: direct routes to decision-makers first).
        own = {d for d in (site_domain(p.get("website")), str(p.get("email") or "").split("@")[-1].lower()) if d}
        direct = str((leader or {}).get("named_email") or "").strip().lower()
        if (direct and "@" in direct and not PERSONAL_DOMAIN.search(direct) and direct.split("@")[-1] in own
                and str(value or "").lower() != direct):
            route, value = "named_email", direct
        # D2 (11 October 2026): with no address of their own, the inbox for the leader's exact role on the organisation's domain
        # (generalsecretary@ for the General Secretary) reaches them directly too.
        role_box = str((leader or {}).get("published_role_email") or "").strip().lower()
        if (not (direct and route == "named_email") and role_box and "@" in role_box and not PERSONAL_DOMAIN.search(role_box)
                and role_box.split("@")[-1] in own and role_inbox_for(role_box.split("@")[0], (leader or {}).get("role") or "")):
            route, value = "published_role_email", role_box
        escalation = {}
        if escalate:
            # The executive's own published work address when there is one; otherwise the organisation's inbox, addressed to them by name.
            own_address = next((str(e).strip().lower() for e in (escalate.get("named_email"), escalate.get("published_role_email"))
                                if e and not PERSONAL_DOMAIN.search(str(e))), "")
            e_route, e_value = (("named_email" if escalate.get("named_email") else "published_role_email"), own_address) if own_address else (
                ("organisation_email", p["email"]) if p.get("email") and p.get("pdpa_risk") != "risky" else ("", ""))
            escalation = {"escalation_contact_id": escalate.get("contact_id", ""),
                          "escalation_recipient": f"{escalate['greet_name']} ({escalate.get('role') or 'role not published'})",
                          "escalation_route": e_value, "escalation_trigger": ESCALATION_TRIGGER, "escalation_route_type": e_route,
                          "escalation_source_url": escalate.get("source_url") or escalate.get("profile_url") or ""}
        if not route:
            missing.append("No usable published route (risky routes are never used); find the organisation's own email or phone.")
        route_problem = False
        if route == "organisation_phone" or route == "role_phone":
            if not str(value).replace(" ", "").startswith("+255"):
                route_problem = True
                missing.append("The only route is a phone number outside Tanzania; find an email address.")
        elif value and (model != "funder" and p.get("segment") != "Welfare funder") and FOREIGN_ROUTE.search(str(value).split("@")[-1]):
            route_problem = True
            missing.append("The email address is on a domain outside Tanzania; confirm it reaches this organisation.")
        risky_contact_route = any(c.get("pdpa_risk") == "risky" and str(value or "").lower() in
                                  {str(v).lower() for v in (c.get("named_email"), c.get("published_role_email"), c.get("shared_email"), c.get("role_phone")) if v}
                                  for c in contacts_by_org.get(oid, []))
        confirmed_official = str(official_inboxes.get(o["name"], {}).get("address", "")).lower() == str(value or "").lower() and bool(value)
        if risky_contact_route and not confirmed_official:
            route_problem = True
            missing.append("The only route is a named individual's address on a personal domain (risky); find the organisation's own email or phone.")
        personal_inbox = bool(PERSONAL_DOMAIN.search(str(value or "")))
        if personal_inbox and str(official_inboxes.get(o["name"], {}).get("address", "")).lower() == str(value).lower():
            personal_inbox = False  # reviewed: the organisation publishes it as its official contact
            missing.append(f"Personal-domain inbox confirmed as the organisation's official contact: {official_inboxes[o['name']].get('basis', '')}")
        if personal_inbox:
            missing.append("The organisation's published inbox is on a personal email domain; confirm it is the official address and not a "
                           "person's before use (data-protection check).")
        if str(track).startswith("WA00"):
            missing.append(f"Held: {p.get('track_reason') or 'identity, route or location unresolved'}.")
        if p.get("red_flags"):
            missing.append(f"Review the recorded red flags before any contact: {str(p['red_flags'])[:160]}.")
        campus = (L.campus_line_en(p.get("campus") or "", p.get("distance_km"), True, "you") if precise(p) else L.network_line_en())
        # The first message is a request with no offer terms; the follow-up states the offer. Sponsorship is asked of funders only.
        if model == "funder" or p.get("segment") == "Welfare funder":
            reason = reasons.get(oid)
            hook = f"I understand that {name} {reason['verb']} {reason['supported']}." if reason else ""
            subject = "Sponsorship request: students at Silverleaf Academy"
            asks = ("We are seeking sponsorships for students to help cover school fees and other education-related costs. Support of any size helps, "
                    "including a contribution towards textbooks, transport or meals.")
            if reason and leader and role_phrase(leader.get("role"), name):
                opening = (f"I understand that you are {role_phrase(leader.get('role'), name)} of {name}, which {reason['verb']} {reason['supported']}. "
                           f"It is this commitment to supporting communities in Tanzania that led me to reach out to you directly.")
            elif reason:
                opening = (f"{hook} It is this commitment to supporting communities in Tanzania that led me to write."
                           f"{'' if leader else ' I would be grateful if this could reach whoever leads ' + name + chr(39) + 's giving.'}")
            else:
                opening = f"I am writing to ask whether {name} would consider sponsoring students at Silverleaf Academy."
            body = (f"{greet}\n\n{L.INTRO} {opening}\n\n{asks} I would welcome the chance to share more about our school and students, and to discuss "
                    f"whether this might fit within {name}{chr(39) if name.endswith('s') else chr(39) + 's'} current giving.\n\n{L.MEETING_ASK}\n\n"
                    f"Thank you very much for your time and consideration.\n\n{L.SIGNATURE}")
            if not reason:
                missing.append("No verified, sourced relationship with a home or programme: there is no honest reason to ask this funder yet; confirm the fit first.")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is how sponsorship can go further at Silverleaf. When an organisation places "
                      f"all its primary-age children with us, each child receives 3% off tuition at 10 children, rising to 18% at 60 or more. Paying the "
                      f"year's tuition before the school year opens adds a free uniform set (worth TZS 110,000) per child, and tuition can be paid in "
                      f"four instalments.\n\n{L.network_line_en()}\n\nShall I send a one-page summary of the partner rates?\n\n{L.SIGNATURE}")
            cta, modules = "Sponsor conversation", "VM08; VM09; VM13"
            relevance = (f"{p.get('segment')}: sponsorship request{'; supports ' + reason['supported'] if reason else ''}; partner rates in the "
                         f"follow-up.")
        elif model == "network" or str(p.get("segment") or "").startswith("Welfare network"):
            # An introducer (decided 2 October 2026): a network, umbrella or faith social-services body that could share the partnership with its
            # member homes. The first message asks for a partnership and a meeting and states no offer terms; the partner rate follows.
            reason, hook = None, ""
            the = "" if name.split()[0].isupper() else "the "
            subject = "A partnership on education for children in your member homes"
            body = (f"{greet}\n\n{L.INTRO}\n\nWe are looking to set up a partnership with {the}{name} so that the homes and programmes it works with can "
                    f"partner with Silverleaf Academy on the education of the children in their care. I would welcome the chance to explain how it could "
                    f"work, and to discuss whether {the}{name} might share it with members, for example at a members' meeting or in a newsletter."
                    f"\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is what we can offer member homes. Silverleaf Academy offers "
                      f"{L.EN['OF03']}. Paying the year's tuition before the school year opens also brings a free uniform set (worth TZS 110,000) for "
                      f"each child, and tuition can be paid in four instalments. Our admissions team checks each child's level before a place is "
                      f"confirmed.\n\n{L.network_line_en()}\n\nShall I send a one-page note you could share with members?\n\n{L.SIGNATURE}")
            cta, modules = "Introducer conversation", "VM08; VM09; VM13"
            relevance = f"{p.get('segment')}: introducer request to share the partnership with member homes; partner rates in the follow-up."
        else:
            reason, hook = None, ""
            who = "an organisation" if model == "family_based" else "a home"
            care = "in your programme" if model == "family_based" else "in your care"
            subject = f"A partnership on education for the children {care}"
            needs = (" Before any placement we would talk through each child's needs with you." if model == "specialised" else "")
            body = (f"{greet}\n\n{L.INTRO}\n\nWe are looking to set up a partnership with {name} on the education of the children {care}. I would "
                    f"welcome the chance to explain how it could work, and to discuss whether it might suit you and your team.\n\n{L.MEETING_ASK}"
                    f"\n\n{L.SIGNATURE}")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is what we can offer. Silverleaf Academy offers "
                      f"{L.EN['OF03'].replace('a home', who)}. Paying the year's tuition before the school year opens also brings a free uniform set "
                      f"(worth TZS 110,000) for each child, and tuition can be paid in four instalments. Our admissions team checks each child's level "
                      f"before a place is confirmed.{needs}\n\n{campus}\n\nWould a 20-minute call to talk through school plans for 2027 for the "
                      f"children {care} be useful?\n\n{L.SIGNATURE}")
            cta, modules = "Placement conversation", "VM08; VM09; VM13"
            relevance = (f"{p.get('segment')}: education partnership request; partner rates in the follow-up; nearest campus "
                         f"{p.get('campus') or 'unknown'}.")
            if model == "specialised":
                missing.append("Specialised centre: confirm Silverleaf can meet the children's needs before contacting.")
        funder = model == "funder" or p.get("segment") == "Welfare funder"
        ready = (str(track).startswith("WA01") and route and model != "specialised" and not p.get("red_flags") and not personal_inbox
                 and not route_problem and (reason is not None if funder else True))
        plan = {"message_id": sid("welfare", oid), "target_id": oid, "target_type": "organisation", "organisation_id": oid,
                "relevance_reason": relevance, "cta_type": cta, "track": str(track).split(" ")[0], "modules": modules,
                "review_status": "draft_ready" if ready else "needs_review", "missing": missing, "contact_route": route, "route_value": value,
                "recipient": recipient or f"{o['name']} (organisation route)", "language": "English", "offer_ids": WELFARE_OFFERS,
                "outcome": "drafted" if ready else "drafted, held",
                **({"hook": hook, "hook_source_url": reason["url"], "hook_verified_on": reason["verified_on"]} if reason else {})}
        # First touch (docs/strategy/partnership-pipelines-draft.md section 4, approved 11 October 2026; first_touch.py): the named leader's
        # own or role address keeps the letter; a named leader reached only through a general inbox gets the Attn format; no named leader
        # gets the short redirect request, with no follow-up and the planned next touch as a note.
        touch_kind = "funder" if funder else ("introducer" if network else "welfare_home")
        own_routes = {str((leader or {}).get(k) or "").strip().lower() for k in ("named_email", "published_role_email")} - {""}
        follow_2 = ""
        if "@" in str(value or ""):
            if leader and str(value).strip().lower() in own_routes and route in ("named_email", "published_role_email"):
                outcomes["first touch: A (own address)"] += 1
            elif leader:
                subject, body = FT.attn(touch_kind, body, leader["greet_name"], leader.get("role") or "")
                outcomes["first touch: B (Attn)"] += 1
                # Named-person fallout (pipeline draft section 5, applied 11 October 2026): follow-up 1 gives the offer details the register
                # approves for the segment, follow-up 2 closes with the segment's redirect-style ask, then one message to the escalation
                # contact, if one exists, 5 working days after the close (noted here; nothing is drafted to them).
                if not follow:
                    missing.append(NO_APPROVED_FOLLOW_UP)
                follow_2 = FT.close(touch_kind, f"{'' if name.split()[0].isupper() else 'the '}{name}" if network else name, greet)
                if escalation:
                    missing.append(FT.escalation_note(escalation["escalation_recipient"]))
                outcomes[f"named-person fallout (case B): {touch_kind}"] += 1
            else:
                subject, body = FT.redirect(touch_kind, name)
                follow = ""
                missing.append(FT.NEXT_TOUCH[touch_kind])
                outcomes["first touch: C (redirect request)"] += 1
        names = (o["name"], name, recipient.split(" (")[0], reason["supported"] if reason else "", leader["greet_name"] if leader else "")
        for text in (body, follow, follow_2):
            issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(text, WELFARE_OFFERS, ignore=names)]
        issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_first_message(body, ignore=names)]
        add(con, now, plan, subject, body, follow, follow_up_2=follow_2)
        if escalation:
            con.execute(f"UPDATE outreach_plans SET {', '.join(f'{k} = ?' for k in escalation)} WHERE message_id = ?",
                         (*escalation.values(), plan["message_id"]))
            outcomes["with an escalation contact"] += 1
        outcomes[plan["outcome"]] += 1
    for e in [dict(r) for r in con.execute("SELECT * FROM enquiries")]:
        request = str(e.get("request") or "").lower()
        if re.search(r"indian|cbse|igcse|cambridge|international curriculum|secondary|teacher|job", request):
            outcomes["parent enquiry: outside Silverleaf's offer, no reply"] += 1
            continue
        body = (f"Hello,\n\nI'm {L.SENDER} from Silverleaf Academy, replying to your question about schools. If you are still looking, applications for "
                f"the 2027 school year are open. We teach Daycare (from 18 months) to Grade 7 in English at five campuses in Arusha, Usa River and "
                f"Boma Ng'ombe. Every family can get {L.family_offer_en()}.\n\nIf it would help, reply with the student's age or grade and the area you "
                f"would live in, and our team will check the right campus and current fees.\n\n{L.SIGNATURE}")
        plan = {"message_id": sid("welfare-enquiry", e["enquiry_id"]), "target_id": e["enquiry_id"], "target_type": "enquiry", "organisation_id": None,
                "relevance_reason": "Public parent enquiry within Silverleaf's levels; one reviewed reply at most.", "cta_type": "Requalification reply",
                "track": "C04", "modules": "VM04", "review_status": "needs_review",
                "missing": ["pdpa_risk risky: a lawful basis approved by Silverleaf's data-protection owner is required before replying.",
                            "Reply only on the original public thread; one reply maximum; no follow-up.", L.CONFIRM_2027],
                "contact_route": "source_url", "route_value": e["source_url"], "recipient": "Author of the public enquiry", "language": "English",
                "offer_ids": FAMILY_OFFERS, "outcome": "drafted, held (risky)"}
        issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(body, FAMILY_OFFERS)]
        add(con, now, plan, "Your question about schools near Arusha", body)
        outcomes[plan["outcome"]] += 1
    return {"outcomes": dict(outcomes), "issues": issues}


# ------------------------------------------------------------------ government
def postal_lines(address) -> tuple[str, str]:
    """('S.L.P. 3013,\\nARUSHA.', 'P.O. Box 3013, Arusha') from a published postal address in either language; ('', '') if none."""
    text = str(address or "").strip()
    m = re.search(r"(?:P\.?\s*O\.?\s*Box|S\.?\s*L\.?\s*P\.?)\s*(?:No\.?\s*)?(\d{1,6})[\s,.]*([A-Za-z' ]*)", text, re.I)
    if not m:
        return (f"{text.rstrip('.')}." if text else ""), text
    number, town = m.group(1), " ".join(m.group(2).split())
    return (f"S.L.P. {number},\n{town.upper()}." if town else f"S.L.P. {number}."), (f"P.O. Box {number}, {town.title()}" if town else f"P.O. Box {number}")


def director_title(council: dict) -> str:
    name = council["name"]
    if "City" in name:
        return "Mkurugenzi wa Jiji"
    if "Municipal" in name:
        return "Mkurugenzi wa Manispaa"
    return "Mkurugenzi Mtendaji wa Halmashauri"


SESSION_SW = ("elimu bure kwa Kiswahili kuhusu maandalizi ya mtoto kuanza shule, kujifunza nyumbani na ratiba ya udahili")
SESSION_EN = "a free talk in Kiswahili on getting children ready for school, learning at home and the admissions calendar"
SAFEGUARDS_SW = ("Mzazi atakayependa taarifa zaidi atajaza fomu yetu kwa hiari yake. Hatutaomba orodha ya wakazi wala taarifa zozote za wakazi, "
                 "na hatutatoa malipo wala zawadi kwa mtu yeyote.")
SAFEGUARDS_EN = ("Parents who want more information will fill in our form only if they choose to. We will not ask for resident lists or any "
                 "residents' information, and we will not offer payments or gifts to anyone.")
ABOUT_SW = ("Silverleaf Academy ni shule binafsi inayofundisha kwa lugha ya Kiingereza, yenye kampasi tano: Arusha City (Sakina), Kijenge na "
            "Ilboru jijini Arusha, Usa River, na Boma Ng'ombe.")
ABOUT_EN = ("Silverleaf Academy is a private English-medium school with five campuses: Arusha City (Sakina), Kijenge and Ilboru in Arusha, "
            "Usa River, and Boma Ng'ombe.")
# The letters describe no services, fees or offers (1 October 2026): they ask for a slot and a short meeting.
MEETING_SW = "Je, itawezekana kupanga kikao kifupi, ana kwa ana au kwa simu, ili kujadili maelezo?"
MEETING_EN = "Would it be possible to arrange a short meeting, either in person or by phone, to discuss the details?"
BOOKLET_SW = "Kila mzazi atapata kijitabu cha mzazi."
BOOKLET_EN = "Every parent will receive a parent booklet."
CLOSE_SW = f"Wako katika ujenzi wa Taifa,\n\n{L.SIGNATURE_SW}"
CLOSE_EN = f"Yours in nation building,\n\n{L.SENDER}\n{L.SENDER_TITLE}, Silverleaf Academy"


def government(con, now, run_cfg) -> dict:
    councils = {c["name"]: c for c in run_cfg["councils"]}
    offices = [dict(r) for r in con.execute("SELECT o.*, g.office_level, g.admin_unit_name, g.parent_admin_unit, g.council_name, g.region, "
                                            "g.proposed_government_track, g.admin_unit_key FROM organisations o JOIN government_office_profiles g "
                                            "USING(organisation_id) ORDER BY g.office_level, o.name")]
    units = {r["unit_key"]: dict(r) for r in con.execute("SELECT * FROM admin_units")}
    posts = {}
    for r in con.execute("SELECT * FROM official_posts"):
        posts.setdefault(r["organisation_id"], {})[r["post_key"]] = dict(r)
    # The council letter names wards "near our campuses": the highest-scored wards within 10 km of a campus (the first wave),
    # then the nearest others, so the claim holds (review of 10 October 2026: Hai's letter named a ward 18 km away).
    top_wards = {}
    near_wards = [u for u in units.values() if u["level"] == "ward" and u["in_catchment"] == "yes" and u["distance_km"] is not None]
    for u in sorted(near_wards, key=lambda u: (u["distance_km"] > 10, -(u["ward_score"] or 0) if u["distance_km"] <= 10 else u["distance_km"])):
        first_wave = [w for w in top_wards.get(u["council"], []) if w[1] <= 10]
        if u["distance_km"] > 10 and first_wave:
            continue  # name only first-wave wards when the council has any
        top_wards.setdefault(u["council"], []).append((u["name"], u["distance_km"]))
    top_wards = {council: [name for name, _ in wards] for council, wards in top_wards.items()}
    outcomes, issues = Counter(), []
    for o in offices:
        level, track = o["office_level"], o["proposed_government_track"] or "GA00 Hold"
        council = councils.get(o.get("council_name") or "", {})
        missing = [L.NATIVE_REVIEW, "Letter on Silverleaf letterhead, delivered by hand or to the official address; approve the session "
                   "content, parent guide and privacy notice first (campaign C11 gates)."]
        ready = False
        if level == "council":
            recipient_post = "council_director"
            title = director_title(o | {"name": o["council_name"]})
            wards = top_wards.get(o["council_name"], [])[:3]
            ward_sw = (f"\n\nTungependa kuanzia katika kata zilizo karibu na kampasi zetu, kama vile {', '.join(wards[:-1])} na {wards[-1]}." if len(wards) > 1
                       else (f"\n\nTungependa kuanzia katika Kata ya {wards[0]}, iliyo karibu na kampasi zetu." if wards else ""))
            ward_en = (f"\n\nWe would like to start in the wards nearest our campuses, such as {', '.join(wards[:-1])} and {wards[-1]}." if len(wards) > 1
                       else (f"\n\nWe would like to start in {wards[0]} ward, near our campuses." if wards else ""))
            subject = "YAH: OMBI LA UTAMBULISHO ILI KUTOA ELIMU KWA WAZAZI KUHUSU MAANDALIZI YA WATOTO KUANZA SHULE"
            # The official postal address, when contact research found one, completes the formal address block.
            postal_sw, postal = postal_lines(o.get("address"))
            addressee = f"{council.get('name_sw', o['council_name'])},\n{postal_sw}" if postal_sw else f"{council.get('name_sw', o['council_name'])}."
            body = (f"{title},\n{addressee}\n\n{subject}\n\n{ABOUT_SW}\n\nTunaomba ushauri wako na barua ya utambulisho "
                    f"kwa Watendaji wa Kata ili, pale itakapofaa, tupewe muda mfupi wa dakika 15 hadi 20 katika mikutano ya wananchi. Tutatoa "
                    f"{SESSION_SW}. {BOOKLET_SW}"
                    f"{ward_sw}\n\n{SAFEGUARDS_SW}\n\n{MEETING_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'City Director' if 'City' in o['council_name'] else 'Municipal Director' if 'Municipal' in o['council_name'] else 'District Executive Director'}, "
                       f"{o['council_name']}{', ' + postal if postal else ''}.\n\nRE: REQUEST FOR AN INTRODUCTION TO GIVE PARENTS INFORMATION ON PREPARING CHILDREN TO START SCHOOL\n\n{ABOUT_EN}\n\n"
                       f"We ask for your advice and a letter introducing us to the ward executive officers so that, where appropriate, we can have a "
                       f"short 15 to 20 minutes at community meetings. We will give {SESSION_EN}. {BOOKLET_EN}"
                       f"{ward_en}\n\n{SAFEGUARDS_EN}\n\n{MEETING_EN}\n\n{CLOSE_EN}")
            follow = (f"{title},\n{addressee}\n\nYAH: UFUATILIAJI WA BARUA YETU YA OMBI LA UTAMBULISHO\n\nTunafuatilia "
                      f"barua yetu kuhusu elimu kwa wazazi kuhusu maandalizi ya watoto kuanza shule. {MEETING_SW}"
                      f"\n\n{CLOSE_SW}")
            modules, cta = "VM14; VM15; VM16; VM17", "Protocol introduction"
            ready = track.startswith("GA01")
            if not ready:
                missing.append("Outside the v1 pilot councils (plan §5.10): hold.")
        elif level in ("ward", "village"):
            recipient_post = "ward_executive_officer" if level == "ward" else "village_executive_officer"
            unit = units.get(o.get("admin_unit_key") or "", {})
            name = " ".join(str(o["admin_unit_name"] or "").split())
            if not name:  # a letter needs the ward's or village's name; the build never imports an unnamed unit (fixed 11 October 2026)
                issues.append({"message_id": o["organisation_id"], "issue": f"{level} office without a place name: no letter can be addressed"})
            place_sw = "kata yenu" if level == "ward" else "kijiji chenu"
            located = o.get("latitude") not in (None, "") and o.get("campus")
            key = L.campus_key(o.get("campus") or "")
            near = bool(located and key and o.get("distance_km") not in (None, "") and float(o["distance_km"]) <= 25)
            km = round(float(o["distance_km"])) if near else 0
            campus_sw = (f"Kampasi yetu iliyo karibu zaidi ni {L.campus_display(key)} (takriban kilomita {km} kutoka {place_sw})." if near and km >= 1
                         else (f"Kampasi yetu iliyo karibu zaidi ni {L.campus_display(key)}, chini ya kilomita 1 kutoka {place_sw}." if near else ""))
            campus_en = (f"Our nearest campus is {L.campus_display(key)}, about {km} km from your {level}." if near and km >= 1
                         else (f"Our nearest campus is {L.campus_display(key)}, less than 1 km from your {level}." if near else ""))
            forum_sw = f"mkutano ujao wa wananchi wa Kata ya {name}" if level == "ward" else f"mkutano mkuu ujao wa Kijiji cha {name}"
            forum_en = f"the next community meeting of {name} ward" if level == "ward" else f"the next village assembly of {name}"
            head_sw = f"Afisa Mtendaji wa Kata ya {name}" if level == "ward" else f"Afisa Mtendaji wa Kijiji cha {name}"
            subject = f"YAH: OMBI LA NAFASI FUPI KATIKA {'MKUTANO WA WANANCHI WA KATA YA' if level == 'ward' else 'MKUTANO MKUU WA KIJIJI CHA'} {name.upper()}"
            body = (f"{head_sw},\n{council.get('name_sw', o.get('council_name') or '')}.\n\n{subject}\n\nKufuatia utambulisho wa Halmashauri, "
                    f"Silverleaf Academy inaomba nafasi ya dakika 15 hadi 20 katika {forum_sw}, ili kutoa {SESSION_SW}.\n\n{campus_sw + chr(10) + chr(10) if campus_sw else ''}{BOOKLET_SW}"
                    f"\n\n{SAFEGUARDS_SW}\n\n{MEETING_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'Ward' if level == 'ward' else 'Village'} Executive Officer, {name}, {o.get('council_name') or ''}.\n\nRE: REQUEST FOR A "
                       f"SHORT SLOT AT {forum_en.upper()}\n\nFollowing the council's introduction, Silverleaf Academy asks for 15 to 20 minutes at "
                       f"{forum_en}, to give {SESSION_EN}.\n\n{campus_en + chr(10) + chr(10) if campus_en else ''}{BOOKLET_EN}"
                       f"\n\n{SAFEGUARDS_EN}\n\n{MEETING_EN}\n\n{CLOSE_EN}")
            follow = ""
            modules, cta = "VM14; VM15; VM16; VM17", "Convening request"
            missing.append("Held until the council introduction (GA01) is recorded and this post is verified within 90 days (GA02 gate).")
            if level == "village" and council.get("urban"):
                missing.append("A city or municipal council has mitaa, not villages: confirm this office and its title (a mtaa office?) "
                               "with the council before any letter.")
            if unit.get("ward_score") is not None:
                missing.append(f"Ward priority: tier {unit.get('ward_tier')}, score {unit.get('ward_score')}, rank {unit.get('rank_in_cluster')} in "
                               f"{unit.get('campus_cluster')}.")
            if not located:
                missing.append("Ward location unknown: campus line omitted.")
        else:
            recipient_post = "district_administrative_secretary" if level == "district" else "regional_administrative_secretary"
            head_sw = (f"Katibu Tawala wa Wilaya ya {o['admin_unit_name']}" if level == "district" else f"Katibu Tawala wa Mkoa wa {o['admin_unit_name']}")
            subject = "YAH: TAARIFA KUHUSU ELIMU KWA WAZAZI JUU YA MAANDALIZI YA WATOTO KUANZA SHULE"
            # The official postal address, when one is published, completes the address block (as in the council letters).
            postal_sw, postal = postal_lines(o.get("address"))
            body = (f"{head_sw}{(',' + chr(10) + postal_sw) if postal_sw else '.'}\n\n{subject}\n\n{ABOUT_SW}\n\nKwa utambulisho wa Halmashauri husika, tunapanga kutoa {SESSION_SW} katika mikutano ya "
                    f"wananchi, kwa muda mfupi utakaotolewa na Watendaji wa Kata. Tunapenda ofisi yako ifahamu mpango huu, na tutashukuru kwa ushauri "
                    f"wowote.\n\n{SAFEGUARDS_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'District' if level == 'district' else 'Regional'} Administrative Secretary, {o['admin_unit_name']}"
                       f"{', ' + postal if postal else ''}.\n\nRE: NOTICE OF "
                       f"PARENT INFORMATION SESSIONS ON PREPARING CHILDREN TO START SCHOOL\n\n{ABOUT_EN}\n\nWith the relevant councils' introduction, we "
                       f"plan to give {SESSION_EN} at community meetings, in short slots the ward executive officers allow. We would like your office to "
                       f"know of this plan and would welcome any advice.\n\n{SAFEGUARDS_EN}\n\n{CLOSE_EN}")
            follow = ""
            modules, cta = "VM14", "Courtesy notice"
            missing.append("District and regional offices are not a v1 target (plan §1): hold; coordinate with the B2G owner first.")
        post = posts.get(o["organisation_id"], {}).get(recipient_post, {})
        offer_ids = []  # the letters state no offer, fee or service
        plan = {"message_id": sid("government", o["organisation_id"]), "target_id": o["organisation_id"], "target_type": "organisation",
                "organisation_id": o["organisation_id"],
                "relevance_reason": f"{level.title()} office that can convene or introduce community meetings ({o.get('council_name') or o['admin_unit_name']}).",
                "cta_type": cta, "track": track.split(" ")[0], "modules": modules, "review_status": "draft_ready" if ready else "needs_review",
                "missing": missing, "contact_route": "letter", "route_value": "Official office address (hand delivery)",
                "recipient": f"{post.get('office_title_sw') or recipient_post} ({post.get('office_title') or ''})".strip(),
                "language": "Kiswahili (English meaning attached)", "offer_ids": offer_ids, "outcome": "drafted" if ready else "drafted, held"}
        for text in (body, follow, english):
            issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(text, offer_ids, convening=True,
                                                                                             ignore=(o["name"], o.get("council_name") or ""))]
        add(con, now, plan, subject, body, follow, english)
        outcomes[plan["outcome"]] += 1
    outcomes["named councillors: no direct message (engage through the forum they chair; plan decision 7)"] = con.execute(
        "SELECT COUNT(*) FROM official_posts WHERE post_key='ward_councillor' AND holder_name != ''").fetchone()[0]
    return {"outcomes": dict(outcomes), "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", required=True, choices=["welfare", "government"])
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run_cfg = json.loads((ROOT / "data" / "runs" / args.run_id / "run-config.json").read_text(encoding="utf-8"))
    db = ROOT / "outputs" / "runs" / args.run_id / "lead-database.sqlite"
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        con.execute("BEGIN")
        prepare(con)
        result = (welfare if args.track == "welfare" else government)(con, now, run_cfg)
        if result["issues"]:
            raise RuntimeError({"conformance_issues": result["issues"][:10], "count": len(result["issues"])})
        con.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?)", ("offer_version", L.OFFER_VERSION))
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fks:
            raise RuntimeError({"integrity": integrity, "foreign_keys": fks[:5]})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("messages", "outreach_plans")}
    statuses = dict(con.execute("SELECT review_status, COUNT(*) FROM outreach_plans GROUP BY 1").fetchall())
    con.close()
    print(json.dumps({"track": args.track, "run_id": args.run_id, "offer_version": L.OFFER_VERSION, "outcomes": result["outcomes"],
                      "counts": counts, "review_status": statuses, "conformance_issues": 0}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
