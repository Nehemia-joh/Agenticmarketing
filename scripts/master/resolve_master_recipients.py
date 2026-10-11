#!/usr/bin/env python3
"""Choose one recipient per real organisation in the company master: collapse duplicates, prefer a named decision-maker.

Two steps, both on the selection of outreach plans (no record is merged or deleted):
1. Collapse duplicate organisations. Records of one business (same website, same normalised name, or the same email or
   phone with a similar name) form a cluster; records that only share an inbox form a "shared inbox" cluster. SACCOS and
   employers are never clustered together. One record is the primary (curated record, usable route, verified hook,
   verified decision-makers); the others keep their IDs, their plans become alternatives and a review item names the
   primary, so a person can merge them through the update skill.
2. Choose the recipient. Across the cluster, the chosen draft goes to the best verified named decision-maker (human
   resources first, then owner, founder, managing director or CEO, then general manager, then another director) who has an
   email route and a draft that is ready for review. Without one, the existing chosen draft stays.
   On-the-ground rule (10 October 2026): the recipient is the most senior person running the Tanzania or Arusha operation (a
   Tanzania MD or country head, the Tanzania HR head, the Arusha GM or branch head). In an organisation whose people show a wider
   group, a group, regional or global head (or someone whose own line is abroad) is used only when no one in-country qualifies, and
   otherwise becomes the escalation contact (outreach_plans escalation_contact_id, escalation_recipient, escalation_route,
   escalation_trigger; the same names as the welfare run): not a CC and without a draft. Another country's head is neither.
   Board roles (chair, non-executive, trustee) are never chosen, except an introducer's elected chair. Ties keep the plan already
   selected. data/reference/recipient-overrides.json records reviewed exceptions (recipient, its address, escalation contact), and
   since 11 October 2026 its 'excluded_contacts': records that are never a recipient or escalation contact (a page heading read as
   a person), each with a review item.
Reviewed relations (data/reference/organisation-relations.json, added 2026-10-11) join records the rules above cannot see: a
'duplicate' pair is one cluster whose primary is the record the person chose; a 'branch' is clustered with its main organisation
(the primary), so one message goes to the business as for other branches the website or name rule groups, and its review item
reads 'Branch of another organisation (collapsed for sending)' instead of a duplicate. Both records are always kept.

Default: preview (runtime/master/recipient-selection-preview.json); nothing changes. --apply: one transaction, then the
record of everything changed since the first run goes to outputs/messages/master-recipient-selection.json. Re-running changes nothing.
Afterwards run export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
PREVIEW = ROOT / "runtime" / "master" / "recipient-selection-preview.json"
RECORD = ROOT / "outputs" / "messages" / "master-recipient-selection.json"
OVERRIDES = ROOT / "data" / "reference" / "recipient-overrides.json"
RELATIONS = ROOT / "data" / "reference" / "organisation-relations.json"
BRANCH_KIND = "Branch of another organisation (collapsed for sending)"


def load_relations() -> list:
    """Reviewed duplicate and branch relations: [{kind, organisation_id, related_id, primary?, decision, decided, ...}]."""
    return json.loads(RELATIONS.read_text(encoding="utf-8"))["relations"] if RELATIONS.exists() else []


def reviewed_primary(members, relations):
    """The record a reviewed relation makes primary: a duplicate pair's chosen survivor, or a branch's main organisation."""
    for r in relations:
        target = r.get("primary") if r["kind"] == "duplicate" else r["related_id"]
        if r["organisation_id"] in members and r["related_id"] in members and target in members:
            return target
    return None
ESCALATION_TRIGGER = "no reply after the follow-up, or the country office declines or defers to head office"
ESCALATION_COLUMNS = ("escalation_contact_id", "escalation_recipient", "escalation_route", "escalation_trigger")

FREE_MAIL = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|ymail)\.", re.I)
NOT_A_SITE = re.compile(r"facebook|instagram|tripadvisor|linkedin|google|wordpress|wix|twitter|youtube", re.I)
NAME_NOISE = re.compile(r"\b(ltd|limited|co|company|tz|t|inc|the|and|safaris?|tours?|travels?|expeditions?|adventures?|holidays?|arusha|"
                        r"tanzania|africa|group|plc|bank)\b")
DUPLICATE_NOTE = re.compile(r"(Duplicate organisation:|Shared inbox with|Branch of) [^;]*?\(O[0-9a-f]{12}\)[;,] held as an alternative so one message goes to this business\.;?\s*")
ROLE_NOT_CONFIRMED = re.compile(r"Role not confirmed|Possible closure", re.I)

HR = re.compile(r"human resource|\bhr\b|people (and|&) culture|talent|personnel", re.I)
# The head of an institution under its own title counts as its chief executive: a university's vice-chancellor (often written
# 'Vice-Chancellor'), an institute's rector or provost, a school's head, and an association's or chamber's executive secretary.
TOP = re.compile(r"owner|founder|proprietor|managing director|managing partner|executive partner|country senior partner|\bceo\b|chief executive|"
                 r"principal|vice[- ]?chancellor|\brector\b|\bprovost\b|head of school|head ?teacher|headmaster|headmistress|"
                 r"executive director|executive secretary|secretary general|chairman|chairperson", re.I)
GM = re.compile(r"general manager|country manager|director general|country director|branch manager|branch head|head of branch", re.I)
OTHER_DIRECTOR = re.compile(r"\bdirector\b|head of (finance|operations)|chief (finance|operating) officer|\bcfo\b|\bcoo\b", re.I)
NOT_SENIOR = re.compile(r"board|non-executive|trustee|advis|assistant|\bass\.|deputy|guide|reservation|sales|marketing|logistics|trip|camp|field|audit|"
                        r"credit|risk|compliance|patient|research|technical|\bict?\b|engineer|kenya|kisumu|nairobi|uganda", re.I)
# A role the source itself dates as past ('Head of School (older school site, 2016)', 'Former Director') is not a current recipient.
STALE = re.compile(r"\bolder\b|\bformer(ly)?\b|\bretired\b|\bpast\b|\bex-|\bemeritus\b", re.I)
# Board roles are never a recipient, primary or escalation (decided 10 October 2026), unless the title also makes the person an executive
# ('Chairman and Managing Director', 'Founder and Chairperson', 'Executive Chairman').
BOARD = re.compile(r"\bboard\b|non-?executive|trustee|\bchair(man|person|woman)?\b", re.I)
EXECUTIVE = re.compile(r"\bceo\b|managing director|chief executive|founder|owner|proprietor|executive chair", re.I)
# Where a person works, for the on-the-ground rule (decided 10 October 2026): the primary recipient runs the Tanzania or Arusha operation;
# a group, regional or global head is the escalation contact; another country's head is neither.
FOREIGN = re.compile(r"\b(kenya|nairobi|mombasa|kisumu|uganda|kampala|rwanda|kigali|burundi|ethiopia|zambia|malawi|mozambique|south africa|"
                     r"pakistan|afghanistan|syria|tajikistan|india|portugal|united kingdom|netherlands|germany|france|italy|switzerland|"
                     r"canada|united states|usa|australia)\b", re.I)
WIDE = re.compile(r"\b(global|regional|worldwide|international|east africa)\b", re.I)
GROUP = re.compile(r"\bgroup\b", re.I)
IN_COUNTRY = re.compile(r"tanzania|\(t\)|\btz\b|arusha|moshi|kilimanjaro|country (manager|director|head)|\bcountry\b", re.I)
FALLBACK_OK = re.compile(r"director|operations manager|communications|public relations|\bpr\b|marketing", re.I)
VERIFIED = re.compile(r"^(Published by the organisation|Verified \d{4}-\d\d-\d\d)|role confirmed \d{4}-\d\d-\d\d", re.I)
UNUSABLE = re.compile(r"name incomplete|pdpa_risk risky|decision-maker no", re.I)


def sid(*parts) -> str:
    return "D" + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def emails(*values) -> set:
    found = set()
    for value in values:
        for token in re.split(r"[;,/\s]+", str(value or "").lower()):
            if re.match(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", token) and not FREE_MAIL.search(token):
                found.add(token)
    return found


def phones(*values) -> set:
    return {re.sub(r"\D", "", m)[-9:] for v in values for m in re.findall(r"\+?\d[\d ]{7,}\d", str(v or "")) if len(re.sub(r"\D", "", m)) >= 9}


def domain(url) -> str:
    text = re.sub(r"^https?://", "", str(url or "").lower().strip())
    text = re.sub(r"^www\.", "", text)
    host = re.split(r"[/\s]", text)[0]
    return "" if not host or NOT_A_SITE.search(host) or "." not in host else host


def tokens(name: str) -> set:
    text = re.sub(r"\(.*?\)|trading name.*", " ", str(name or "").lower())
    return {t for t in re.findall(r"[a-z0-9]+", NAME_NOISE.sub(" ", text)) if len(t) > 1}


def similar(a: str, b: str) -> bool:
    x, y = tokens(a), tokens(b)
    return bool(x and y) and (len(x & y) / len(x | y) >= 0.34 or x <= y or y <= x)


def squash(name: str) -> str:
    return "".join(sorted(tokens(name)))


def role_rank(role: str):
    """0 human resources, 1 owner or chief executive, 2 general manager or director, 3 other senior director; None if not senior."""
    role = role or ""
    if STALE.search(role):
        return None
    if re.search(r"non-?executive", role, re.I) or (BOARD.search(role) and not EXECUTIVE.search(role)):
        return None
    if HR.search(role):
        # An HR assistant, clerk or intern supports the HR head and is not the decision-maker (11 October 2026: 'HR and Admin Assistant'
        # had outranked a named managing director).
        return None if re.search(r"assistant|\bass\.|\bclerk\b|\bintern\b|trainee", role, re.I) else 0
    if TOP.search(role) and not re.search(r"assistant|deputy|\bass\.|kenya|kisumu|nairobi|uganda", role, re.I):
        return 1
    if NOT_SENIOR.search(role):
        return None
    if GM.search(role):
        return 2
    if re.fullmatch(r"\s*director\s*", role, re.I):
        return 2
    if OTHER_DIRECTOR.search(role):
        return 3
    return None


def load(con):
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans")]
    return orgs, contacts, plans


def cluster(orgs, contacts, plans):
    """Union-find over organisations of one kind; returns {root: (members, kind)}."""
    kind_of = {}
    for p in plans:
        kind_of.setdefault(p["organisation_id"], "saccos" if p["segment"] == "SACCOS members" else "employer")
    # Introducers are curated one by one, and a regional office (ATE Northern Zone, the TNCC Arusha chamber) is a different route from its
    # national body, so they are never clustered.
    introducers = {p["organisation_id"] for p in plans if p["segment"] == "Introducers"}
    ids = [o for o in orgs if o in kind_of and o not in introducers]
    parent = {o: o for o in ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_email, by_phone, by_site, by_name = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(set)
    for o in ids:
        org = orgs[o]
        mails = emails(org["email"], *[c["shared_email"] for c in contacts.values() if c["organisation_id"] == o],
                       *[p["contact_channel"] for p in plans if p["organisation_id"] == o and p["target_type"] == "organisation"])
        for m in mails:
            by_email[(kind_of[o], m)].add(o)
        for ph in phones(org["phone"], org["email"]):
            by_phone[(kind_of[o], ph)].add(o)
        if domain(org["website"]):
            by_site[(kind_of[o], domain(org["website"]))].add(o)
        if len(squash(org["name"])) >= 5:
            by_name[(kind_of[o], squash(org["name"]))].add(o)
    edges = defaultdict(set)  # root pair -> why

    def join(group, why, need_similar):
        group = sorted(group)
        for other in group[1:]:
            if need_similar and not similar(orgs[group[0]]["name"], orgs[other]["name"]):
                continue
            ra, rb = find(group[0]), find(other)
            if ra != rb:
                parent[ra] = rb
            edges[other].add(why)
            edges[group[0]].add(why)

    for g in by_site.values():
        join(g, "website", False)
    for g in by_name.values():
        join(g, "name", False)
    for g in by_phone.values():
        join(g, "phone", True)
    for g in by_email.values():
        join(g, "email", False)
    for r in load_relations():  # reviewed duplicate pairs and branches (data/reference/organisation-relations.json)
        if r["organisation_id"] in parent and r["related_id"] in parent:
            join([r["organisation_id"], r["related_id"]], "reviewed", False)
    groups = defaultdict(list)
    for o in ids:
        groups[find(o)].append(o)
    out = {}
    for root, members in groups.items():
        if len(members) > 1:
            why = set().union(*[edges[m] for m in members])
            out[root] = (sorted(members), "same organisation" if why & {"website", "name", "reviewed"} else "shared inbox")
    return out, kind_of


def role_rank_for(role: str, segment: str = ""):
    """role_rank, except that an introducer's elected chair (a chamber's or association's chairman) leads the body, so counts as its head."""
    rank = role_rank(role)
    if rank is None and segment == "Introducers" and re.search(r"\bchair(man|person|woman)?\b|\bpresident\b", role or "", re.I)             and not re.search(r"non-?executive|trustee|vice|deputy|former|past", role or "", re.I):
        return 1
    return rank


def multinational(contacts_of_org) -> bool:
    """An organisation whose published people show a wider group: someone abroad, a global or regional role, or a role tied to the
    Tanzania company (which implies a parent). A local group (Hanspaul Group of Arusha) has none of these, so its 'Group CEO' runs
    the business on the ground."""
    roles = " | ".join(c["role"] or "" for c in contacts_of_org)
    return bool(FOREIGN.search(roles) or WIDE.search(roles) or re.search(r"tanzania|\(t\)|\bcountry\b", roles, re.I))


def location(contact, wide_org: bool) -> int:
    """0 runs the Tanzania or Arusha operation; 1 a group, regional or global head (the escalation contact); 2 another country's head."""
    role = contact["role"] or ""
    if IN_COUNTRY.search(role):
        return 0
    if FOREIGN.search(role):
        return 2
    phone = re.sub(r"[^\d+]", "", str(contact.get("role_phone") or "").split(";")[0].split("/")[0])
    if phone.startswith("+") and not phone.startswith("+255") and len(phone) > 8:
        return 1  # their own published line is abroad (Hazzes' co-founder on +46): based outside Tanzania
    if WIDE.search(role) or (wide_org and GROUP.search(role)):
        return 1
    return 0


def senior_rank(contact, segment: str = ""):
    """The role rank a recipient needs, with the fallback roles behind every senior one; None when the person cannot be a recipient."""
    rank = role_rank_for(contact["role"], segment)
    role = contact["role"] or ""
    if rank is None and FALLBACK_OK.search(role) and not BOARD.search(role) and not re.search(r"sales|reservation|representative|agent|assistant|deputy", role, re.I):
        rank = 4  # behind every senior role: a director by another title, an operations manager, or public relations, communications or marketing
    return rank


def verified_person(contact) -> bool:
    if contact.get("contact_id") in EXCLUDED:
        return False
    name = contact["name"] or ""
    verification = contact["verification"] or ""
    return (len(name.split()) >= 2 and not re.search(r"\d|\?", name) and bool(VERIFIED.search(verification))
            and not UNUSABLE.search(verification))


def eligible(plan, contacts, wide_orgs=frozenset()):
    """(rank, direct route first, co-founder last) for a verified named decision-maker's plan that is ready for review, else None."""
    if plan["target_type"] != "contact" or plan["review_status"] != "Draft review" or "@" not in (plan["contact_channel"] or ""):
        return None
    contact = contacts.get(plan["target_id"])
    if not contact or ROLE_NOT_CONFIRMED.search(plan["missing_information"] or ""):
        return None
    if not verified_person(contact):
        return None
    rank = senior_rank(contact, plan["segment"])
    where = location(contact, contact["organisation_id"] in wide_orgs)
    if rank is None or where == 2:
        return None
    direct = bool(contact["named_email"] or contact["published_role_email"] or contact["role_phone"])
    # In-country people first, then by rank; a group, regional or global head is chosen only when no one in-country is named.
    return where, rank, 0 if direct else 1, 1 if re.search(r"co-?\s?founder", contact["role"] or "", re.I) else 0


def primary_of(members, orgs, plans, contacts, wide_orgs=frozenset()):
    def score(o):
        org = orgs[o]
        mine = [p for p in plans if p["organisation_id"] == o]
        curated = not re.match(r"^(amenity|office|tourism|guest_house):", str(org["segment"] or ""))
        usable = any((p["review_status"] == "Draft review" and (p["contact_channel"] or "").strip()) for p in mine)
        hook = any(str(p["hook_status"] or "").startswith("Verified") for p in mine)
        named = sum(1 for p in mine if eligible(p, contacts, wide_orgs))
        return (curated * 100 + usable * 60 + hook * 40 + min(named, 3) * 10 + bool(org["email"]) * 5 + bool(org["website"]) * 3 + len(mine), o)
    return max(members, key=score)


def plan_key(plan, contacts, primary_org, wide_orgs=frozenset()):
    """Lower sorts first: a verified named decision-maker (in-country first); otherwise the draft already chosen for the primary record.
    Between two equal candidates the one already selected stays, so a re-run never flips a tie."""
    if plan["target_type"] == "contact" and plan["target_id"] in EXCLUDED:
        return (2, (), plan["message_id"])  # never the recipient (recipient-overrides.json excluded_contacts)
    if plan.get("variant_body"):  # the plan that holds a variant draft (assign_message_variants.py) is the company's recipient
        return (-1, (), plan["message_id"])
    e = eligible(plan, contacts, wide_orgs)
    if e:
        return (0, e + (0 if plan["selection"] == "Candidate for review" else 1,), plan["message_id"])
    ready = plan["review_status"] == "Draft review" and bool((plan["contact_channel"] or "").strip())
    by_email = ready and "@" in plan["contact_channel"]
    chosen = plan["selection"] == "Candidate for review"
    mine = plan["organisation_id"] == primary_org
    org_type = plan["target_type"] == "organisation"
    # A named person is kept as the recipient when the role can act on the request or pass it on: any director, an operations manager, or
    # public relations, communications or marketing. A sales or reservations agent, or an overseas sales representative, is not.
    junior = (plan["target_type"] == "contact" and role_rank(plan.get("recipient_role")) is None
              and not FALLBACK_OK.search(plan.get("recipient_role") or ""))
    chosen = chosen and not junior
    tier = (0 if chosen and by_email else 1 if org_type and by_email else 2 if chosen and ready else 3 if by_email else 4 if ready else 5)
    return (1, (tier, 0 if mine else 1, 0 if org_type else 1), plan["message_id"])


def load_overrides() -> dict:
    """Reviewed recipient choices (data/reference/recipient-overrides.json): {organisation_id: {contact_id, route, reason, source, decided}}."""
    return json.loads(OVERRIDES.read_text(encoding="utf-8"))["organisations"] if OVERRIDES.exists() else {}


def load_excluded() -> dict:
    """Contacts that are never a recipient or an escalation contact (recipient-overrides.json 'excluded_contacts', added 11 October 2026:
    a page heading read as a person, a public figure): {contact_id: {name, reason, source, decided}}."""
    return json.loads(OVERRIDES.read_text(encoding="utf-8")).get("excluded_contacts", {}) if OVERRIDES.exists() else {}


EXCLUDED = load_excluded()


def wide_organisations(contacts) -> set:
    by_org = defaultdict(list)
    for c in contacts.values():
        by_org[c["organisation_id"]].append(c)
    return {oid for oid, cs in by_org.items() if multinational(cs)}


def escalation_for(chosen, members, contacts, plans, wide_orgs):
    """The group, regional or global head to escalate to when the in-country recipient does not answer: a verified named senior person
    whose role is wider than the Tanzania operation. None when the recipient is already that person. Board roles never qualify."""
    target = contacts.get(chosen["target_id"]) if chosen["target_type"] == "contact" else None
    if target and location(target, target["organisation_id"] in wide_orgs) != 0:
        return None
    pool = []
    for c in contacts.values():
        if c["organisation_id"] not in members or (target and c["contact_id"] == target["contact_id"]) or not verified_person(c):
            continue
        rank = senior_rank(c)
        if rank is None or location(c, c["organisation_id"] in wide_orgs) != 1:
            continue
        own = sorted(emails(c["named_email"], c["published_role_email"]))
        route = own[0] if own else (c["role_phone"] or "")
        if not route:  # the person's own draft channel, when it differs from the recipient's
            mine = [p["contact_channel"] for p in plans if p["target_type"] == "contact" and p["target_id"] == c["contact_id"]]
            route = next((ch for ch in mine if ch and ch != chosen["contact_channel"]), "")
        pool.append(((rank, 0 if own else 1, c["name"]), c, route))
    if not pool:
        return None
    _, c, route = min(pool, key=lambda x: x[0])
    return {"escalation_contact_id": c["contact_id"], "escalation_recipient": f"{c['name']} ({c['role']})", "escalation_route": route,
            "escalation_trigger": ESCALATION_TRIGGER}


def decide(orgs, contacts, plans):
    clusters, kind_of = cluster(orgs, contacts, plans)
    wide_orgs = wide_organisations(contacts)
    overrides = load_overrides()
    relations = load_relations()
    cluster_of, info = {}, {}
    for root, (members, kind) in clusters.items():
        pinned_primary = reviewed_primary(members, relations)
        primary = pinned_primary or primary_of(members, orgs, plans, contacts, wide_orgs)
        for m in members:
            cluster_of[m] = root
        info[root] = {"members": members, "kind": kind, "primary": primary, "reviewed": bool(pinned_primary)}
    groups = defaultdict(list)
    for p in plans:
        if p["selection"] in ("Candidate for review", "Alternative") and p["target_type"] in ("organisation", "contact"):
            groups[cluster_of.get(p["organisation_id"], p["organisation_id"])].append(p)
    changes, escalations = [], {}
    for root, group in groups.items():
        primary = info[root]["primary"] if root in info else group[0]["organisation_id"]
        chosen = min(group, key=lambda p: plan_key(p, contacts, primary, wide_orgs))
        if root in info and info[root]["reviewed"] and chosen["organisation_id"] != primary:
            # A reviewed relation names the record that carries the message: its best draft is chosen.
            own = [p for p in group if p["organisation_id"] == primary]
            chosen = min(own, key=lambda p: plan_key(p, contacts, primary, wide_orgs)) if own else chosen
        members =set(info[root]["members"]) if root in info else {group[0]["organisation_id"]}
        pinned = [p for p in group if p["target_type"] == "contact" and any(
            o.get("contact_id") == p["target_id"] for oid, o in overrides.items() if oid in members) and p["review_status"] == "Draft review"]
        if pinned:  # a reviewed choice (data/reference/recipient-overrides.json) wins
            chosen = pinned[0]
        escalation = escalation_for(chosen, members, contacts, plans, wide_orgs)
        reviewed = next((o for oid, o in overrides.items() if oid in members and o.get("contact_id") == chosen["target_id"]), None)
        if reviewed and reviewed.get("escalation_contact_id") in contacts:  # a reviewed escalation contact wins too
            c = contacts[reviewed["escalation_contact_id"]]
            own = sorted(emails(c["named_email"], c["published_role_email"]))
            escalation = {"escalation_contact_id": c["contact_id"], "escalation_recipient": f"{c['name']} ({c['role']})",
                          "escalation_route": own[0] if own else (c["role_phone"] or ""), "escalation_trigger": ESCALATION_TRIGGER}
        if escalation:
            escalations[chosen["message_id"]] = escalation
        if root in info and chosen["organisation_id"] in info[root]["members"] and not info[root]["reviewed"]:
            primary = info[root]["primary"] = chosen["organisation_id"]  # the record that carries the message is the primary
        for p in group:
            want = "Candidate for review" if p["message_id"] == chosen["message_id"] else "Alternative"
            duplicate_of = None
            if root in info and p["organisation_id"] != info[root]["primary"]:
                duplicate_of = info[root]["primary"]
            changes.append({"message_id": p["message_id"], "organisation_id": p["organisation_id"], "from": p["selection"], "to": want,
                            "duplicate_of": duplicate_of, "cluster_kind": info[root]["kind"] if root in info else ""})
    return changes, info, escalations


def note_for(change, orgs, branch_of=None) -> str:
    target = orgs[change["duplicate_of"]]["name"]
    kind = "Shared inbox with" if change["cluster_kind"] == "shared inbox" else "Duplicate organisation:"
    if (branch_of or {}).get(change["organisation_id"]) == change["duplicate_of"]:
        kind = "Branch of"
    return f"{kind} {target} ({change['duplicate_of']}), held as an alternative so one message goes to this business."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true", help="write the selection in one transaction")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    orgs, contacts, plans = load(con)
    overrides = load_overrides()
    # A reviewed recipient's own address (an override's route) is the draft's channel and fills an empty work email.
    route_fixes = []
    for oid, o in overrides.items():
        for p in plans:
            if p["target_type"] == "contact" and p["target_id"] == o.get("contact_id") and o.get("route") and p["contact_channel"] != o["route"]:
                route_fixes.append((o["route"], p["message_id"], o))
                p["contact_channel"] = o["route"]
    changes, info, escalations = decide(orgs, contacts, plans)
    relations = load_relations()
    branch_of = {r["organisation_id"]: r["related_id"] for r in relations if r["kind"] == "branch"}
    by_id = {p["message_id"]: p for p in plans}
    moved = [c for c in changes if c["from"] != c["to"]]
    promoted = [c for c in moved if c["to"] == "Candidate for review"]
    demoted = [c for c in moved if c["to"] == "Alternative"]
    duplicate_orgs = sorted({c["organisation_id"] for c in changes if c["duplicate_of"]})
    summary = {
        "clusters": len(info), "organisations_in_clusters": sum(len(v["members"]) for v in info.values()),
        "cluster_kinds": dict(Counter(v["kind"] for v in info.values())),
        "duplicate_organisations_held": len(duplicate_orgs),
        "plans_promoted_to_candidate": len(promoted), "plans_demoted_to_alternative": len(demoted),
        "promoted_to_named_contact": sum(1 for c in promoted if by_id[c["message_id"]]["target_type"] == "contact"),
        "candidates_after": sum(1 for c in changes if c["to"] == "Candidate for review"),
        "escalation_contacts": len(escalations), "override_routes": len(route_fixes),
    }
    detail = {
        "clusters": [{"kind": v["kind"], "primary": f"{orgs[v['primary']]['name']} ({v['primary']})",
                      "duplicates": [f"{orgs[m]['name']} ({m})" for m in v["members"] if m != v["primary"]]} for v in info.values()],
        "promoted": [{"message_id": c["message_id"], "organisation": orgs[c["organisation_id"]]["name"], "recipient": by_id[c["message_id"]]["target_name"],
                      "role": by_id[c["message_id"]]["recipient_role"], "was": c["from"]} for c in promoted],
        "demoted": [{"message_id": c["message_id"], "organisation": orgs[c["organisation_id"]]["name"], "recipient": by_id[c["message_id"]]["target_name"],
                     "duplicate_of": c["duplicate_of"]} for c in demoted],
        "escalations": [{"message_id": mid, "organisation": by_id[mid]["organisation_name"], "recipient": by_id[mid]["target_name"], **e}
                        for mid, e in escalations.items()],
    }
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps({"summary": summary, **detail}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    if not args.apply:
        print(f"Preview only: {PREVIEW}")
        return 0

    today = date.today().isoformat()
    try:
        con.execute("BEGIN")
        columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
        for column in ESCALATION_COLUMNS:  # shared contract with the welfare run (same names)
            if column not in columns:
                con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
        if route_fixes:
            body = OVERRIDES.read_bytes()
            source = "F" + hashlib.sha256(b"recipient-overrides|" + body).hexdigest()[:12]
            con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                        (source, OVERRIDES.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "json", "utf-8", body))
            for route, mid, o in route_fixes:
                record = sid("override", mid, route)
                con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                            (record, source, o.get("source") or "recipient override", json.dumps(o, ensure_ascii=False)))
                con.execute("UPDATE outreach_plans SET contact_channel=?, channel_attribution=? WHERE message_id=?",
                            (route, f"Reviewed recipient override: {o.get('reason', '')}"[:300], mid))
                con.execute("UPDATE contacts SET named_email=?, contact_route='named_email' WHERE contact_id=? AND COALESCE(named_email,'')=''",
                            (route, o["contact_id"]))
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (sid("override-fact", o["contact_id"], route), "contact", o["contact_id"], "named_email", route, record))
        for oid, o in overrides.items():
            wrong = o.get("misattributed") or {}
            if wrong.get("contact_id"):  # an address on another person's contact: flagged for a person to correct, never deleted
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (sid("misattributed", wrong["contact_id"], wrong.get("value", "")), "Contact email belongs to another person", oid,
                             wrong["contact_id"], "named_email", f"{wrong.get('value', '')}: {wrong.get('reason', '')}"[:400],
                             "Remove the address from this contact through the update skill; the recipient override uses it for its owner."))
        for oid, o in overrides.items():
            # A reviewed choice may confirm the recipient's role from a fetched page ('role_confirmed', added 11 October 2026): noted on the
            # contact exactly as update_master_contacts.py notes a confirmation, so the exporter counts the person as verified.
            if o.get("role_confirmed") and o.get("contact_id") in contacts:
                note = f"role confirmed {o.get('decided', '')} ({o['role_confirmed']})"
                con.execute("UPDATE contacts SET verification = COALESCE(verification,'') || ? WHERE contact_id=? AND COALESCE(verification,'') NOT LIKE ?",
                            (f"; {note}", o["contact_id"], f"%{note}%"))
        for cid, x in EXCLUDED.items():
            if cid in contacts:  # flagged for a person to correct through the update skill; the contact is kept, never deleted
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (sid("excluded-contact", cid), "Contact excluded as recipient", contacts[cid]["organisation_id"], cid, "name",
                             f"{x.get('name', '')}: {x.get('reason', '')}"[:400],
                             "Never chosen as recipient or escalation contact (data/reference/recipient-overrides.json excluded_contacts). "
                             "Correct or remove the contact through the update skill."))
        con.execute("UPDATE outreach_plans SET escalation_contact_id=NULL, escalation_recipient=NULL, escalation_route=NULL, escalation_trigger=NULL")
        for mid, e in escalations.items():
            con.execute("UPDATE outreach_plans SET escalation_contact_id=?, escalation_recipient=?, escalation_route=?, escalation_trigger=? WHERE message_id=?",
                        (e["escalation_contact_id"], e["escalation_recipient"], e["escalation_route"], e["escalation_trigger"], mid))
        for c in changes:
            plan = by_id[c["message_id"]]
            missing = DUPLICATE_NOTE.sub("", plan["missing_information"] or "").strip("; ").strip()
            if c["duplicate_of"]:
                note = note_for(c, orgs, branch_of)
                missing = f"{missing}; {note}" if missing else note
            ready = plan["review_status"] == "Draft review"
            if c["to"] == "Candidate for review":
                status, action = ("Candidate after checks" if ready else "Needs research"), "Human review, then send the request"
            else:
                status, action = "Alternative - inactive", (("Branch of the main organisation; keep inactive unless the main record is rejected."
                                                             if branch_of.get(c["organisation_id"]) == c["duplicate_of"] else
                                                             "Duplicate organisation; keep inactive unless the primary record is rejected.") if c["duplicate_of"]
                                                            else "Keep inactive unless the selected recipient is rejected or invalid.")
            if (c["to"], missing) != (plan["selection"], plan["missing_information"] or ""):
                con.execute("UPDATE outreach_plans SET selection=?, missing_information=? WHERE message_id=?", (c["to"], missing, c["message_id"]))
            if c["from"] != c["to"]:
                con.execute("UPDATE campaign_lead_assignments SET selection=?, eligibility_status=?, next_action=? WHERE message_id=?",
                            (c["to"], status, action, c["message_id"]))
        con.execute("DELETE FROM review WHERE kind LIKE 'Duplicate organisation (collapsed%' OR kind LIKE 'Shared inbox (one message%' OR kind=?", (BRANCH_KIND,))
        reviewed_pair = {(r["organisation_id"], r.get("primary") if r["kind"] == "duplicate" else r["related_id"]): r for r in relations}
        for root, v in info.items():
            for m in v["members"]:
                if m == v["primary"]:
                    continue
                rel = reviewed_pair.get((m, v["primary"]))
                if branch_of.get(m) == v["primary"]:
                    kind, values = BRANCH_KIND, (f"{orgs[m]['name']} is a branch of {orgs[v['primary']]['name']} at another site; both records are kept. "
                                                 f"{rel['decision']} (data/reference/organisation-relations.json)")
                    action = ("A branch link, not a duplicate: never merge the records. Its drafts are alternatives and one message goes to the main "
                              "organisation, as for other branches of one employer.")
                else:
                    kind = "Duplicate organisation (collapsed for sending)" if v["kind"] == "same organisation" else "Shared inbox (one message per inbox)"
                    values = (f"{orgs[m]['name']} and {orgs[v['primary']]['name']}: {v['kind']}. "
                              + (f"{rel['decision']} (data/reference/organisation-relations.json)" if rel else f"Decided {today} by resolve_master_recipients.py."))
                    action = "Its drafts are alternatives and one message goes to the primary record. Merge the records through the update skill when a person confirms."
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (sid("collapse", m), kind, m, v["primary"], "organisation", values[:900], action))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        candidates = con.execute("SELECT COUNT(*) FROM outreach_plans WHERE selection='Candidate for review'").fetchone()[0]
        if candidates != summary["candidates_after"]:
            raise RuntimeError(f"expected {summary['candidates_after']} candidates, found {candidates}")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    previous = json.loads(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
    baseline = previous.get("baseline") or {p["message_id"]: p["selection"] for p in plans}  # the selection before the first apply
    if not moved and previous and not route_fixes:
        print("Nothing changed in the selection; the record stays.")
        return 0
    now = {r[0]: r for r in con.execute("SELECT message_id, organisation_name, target_name, recipient_role, selection FROM outreach_plans")}
    changed = [now[k] for k in now if k in baseline and baseline[k] != now[k][4]]
    record = {"decided_on": previous.get("decided_on", today), "method": "scripts/master/resolve_master_recipients.py",
              "note": "No record was merged or deleted. The baseline is the selection before the first run; the lists compare the database with it.",
              "summary": {**{k: v for k, v in summary.items() if not k.startswith(("plans_", "promoted_"))}, "candidates_before": sum(1 for v in baseline.values() if v == "Candidate for review"),
                          "plans_changed": len(changed), "plans_now_candidate": sum(1 for r in changed if r[4] == "Candidate for review"),
                          "plans_now_alternative": sum(1 for r in changed if r[4] == "Alternative"),
                          "named_contacts_now_candidate": sum(1 for r in changed if r[4] == "Candidate for review" and r[3] != "Organisation routing")},
              "clusters": detail["clusters"],
              "now_candidate": [{"message_id": r[0], "organisation": r[1], "recipient": r[2], "role": r[3]} for r in changed if r[4] == "Candidate for review"],
              "now_alternative": [{"message_id": r[0], "organisation": r[1], "recipient": r[2], "role": r[3]} for r in changed if r[4] == "Alternative"],
              "baseline": baseline}
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Applied. Record: {RECORD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
