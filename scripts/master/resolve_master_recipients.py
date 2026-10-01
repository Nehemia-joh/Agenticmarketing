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

FREE_MAIL = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|ymail)\.", re.I)
NOT_A_SITE = re.compile(r"facebook|instagram|tripadvisor|linkedin|google|wordpress|wix|twitter|youtube", re.I)
NAME_NOISE = re.compile(r"\b(ltd|limited|co|company|tz|t|inc|the|and|safaris?|tours?|travels?|expeditions?|adventures?|holidays?|arusha|"
                        r"tanzania|africa|group|plc|bank)\b")
DUPLICATE_NOTE = re.compile(r"(Duplicate organisation:|Shared inbox with) [^;]*?\(O[0-9a-f]{12}\)[;,] held as an alternative so one message goes to this business\.;?\s*")
ROLE_NOT_CONFIRMED = re.compile(r"Role not confirmed|Possible closure", re.I)

HR = re.compile(r"human resource|\bhr\b|people (and|&) culture|talent|personnel", re.I)
TOP = re.compile(r"owner|founder|managing director|managing partner|executive partner|\bceo\b|chief executive|principal|vice chancellor|executive director|chairman|chairperson", re.I)
GM = re.compile(r"general manager|country manager|director general|country director", re.I)
OTHER_DIRECTOR = re.compile(r"\bdirector\b|head of (finance|operations)|chief (finance|operating) officer|\bcfo\b|\bcoo\b", re.I)
NOT_SENIOR = re.compile(r"board|non-executive|trustee|advis|assistant|\bass\.|deputy|guide|reservation|sales|marketing|logistics|trip|camp|field|audit|"
                        r"credit|risk|compliance|patient|research|technical|\bict?\b|engineer|kenya|kisumu|nairobi|uganda", re.I)
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
    if HR.search(role):
        return 0
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
    ids = [o for o in orgs if o in kind_of]
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
    groups = defaultdict(list)
    for o in ids:
        groups[find(o)].append(o)
    out = {}
    for root, members in groups.items():
        if len(members) > 1:
            why = set().union(*[edges[m] for m in members])
            out[root] = (sorted(members), "same organisation" if why & {"website", "name"} else "shared inbox")
    return out, kind_of


def eligible(plan, contacts):
    """(rank, direct route first, co-founder last) for a verified named decision-maker's plan that is ready for review, else None."""
    if plan["target_type"] != "contact" or plan["review_status"] != "Draft review" or "@" not in (plan["contact_channel"] or ""):
        return None
    contact = contacts.get(plan["target_id"])
    if not contact or ROLE_NOT_CONFIRMED.search(plan["missing_information"] or ""):
        return None
    name = contact["name"] or ""
    if len(name.split()) < 2 or re.search(r"\d|\?", name):
        return None
    verification = contact["verification"] or ""
    if not VERIFIED.search(verification) or UNUSABLE.search(verification):
        return None
    rank = role_rank(contact["role"])
    if rank is None:
        return None
    direct = bool(contact["named_email"] or contact["published_role_email"] or contact["role_phone"])
    return rank, 0 if direct else 1, 1 if re.search(r"co-?\s?founder", contact["role"] or "", re.I) else 0


def primary_of(members, orgs, plans, contacts):
    def score(o):
        org = orgs[o]
        mine = [p for p in plans if p["organisation_id"] == o]
        curated = not re.match(r"^(amenity|office|tourism|guest_house):", str(org["segment"] or ""))
        usable = any((p["review_status"] == "Draft review" and (p["contact_channel"] or "").strip()) for p in mine)
        hook = any(str(p["hook_status"] or "").startswith("Verified") for p in mine)
        named = sum(1 for p in mine if eligible(p, contacts))
        return (curated * 100 + usable * 60 + hook * 40 + min(named, 3) * 10 + bool(org["email"]) * 5 + bool(org["website"]) * 3 + len(mine), o)
    return max(members, key=score)


def plan_key(plan, contacts, primary_org):
    """Lower sorts first: a verified named decision-maker; otherwise the draft already chosen for the primary record."""
    if plan.get("variant_body"):  # the plan that holds a variant draft (assign_message_variants.py) is the company's recipient
        return (-1, (), plan["message_id"])
    e = eligible(plan, contacts)
    if e:
        return (0, e, plan["message_id"])
    ready = plan["review_status"] == "Draft review" and bool((plan["contact_channel"] or "").strip())
    by_email = ready and "@" in plan["contact_channel"]
    chosen = plan["selection"] == "Candidate for review"
    mine = plan["organisation_id"] == primary_org
    org_type = plan["target_type"] == "organisation"
    tier = (0 if chosen and by_email else 1 if org_type and by_email else 2 if chosen and ready else 3 if by_email else 4 if ready else 5)
    return (1, (tier, 0 if mine else 1, 0 if org_type else 1), plan["message_id"])


def decide(orgs, contacts, plans):
    clusters, kind_of = cluster(orgs, contacts, plans)
    cluster_of, info = {}, {}
    for root, (members, kind) in clusters.items():
        primary = primary_of(members, orgs, plans, contacts)
        for m in members:
            cluster_of[m] = root
        info[root] = {"members": members, "kind": kind, "primary": primary}
    groups = defaultdict(list)
    for p in plans:
        if p["selection"] in ("Candidate for review", "Alternative") and p["target_type"] in ("organisation", "contact"):
            groups[cluster_of.get(p["organisation_id"], p["organisation_id"])].append(p)
    changes = []
    for root, group in groups.items():
        primary = info[root]["primary"] if root in info else group[0]["organisation_id"]
        chosen = min(group, key=lambda p: plan_key(p, contacts, primary))
        if root in info and chosen["organisation_id"] in info[root]["members"]:
            primary = info[root]["primary"] = chosen["organisation_id"]  # the record that carries the message is the primary
        for p in group:
            want = "Candidate for review" if p["message_id"] == chosen["message_id"] else "Alternative"
            duplicate_of = None
            if root in info and p["organisation_id"] != info[root]["primary"]:
                duplicate_of = info[root]["primary"]
            changes.append({"message_id": p["message_id"], "organisation_id": p["organisation_id"], "from": p["selection"], "to": want,
                            "duplicate_of": duplicate_of, "cluster_kind": info[root]["kind"] if root in info else ""})
    return changes, info


def note_for(change, orgs) -> str:
    target = orgs[change["duplicate_of"]]["name"]
    kind = "Shared inbox with" if change["cluster_kind"] == "shared inbox" else "Duplicate organisation:"
    return f"{kind} {target} ({change['duplicate_of']}), held as an alternative so one message goes to this business."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true", help="write the selection in one transaction")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    orgs, contacts, plans = load(con)
    changes, info = decide(orgs, contacts, plans)
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
    }
    detail = {
        "clusters": [{"kind": v["kind"], "primary": f"{orgs[v['primary']]['name']} ({v['primary']})",
                      "duplicates": [f"{orgs[m]['name']} ({m})" for m in v["members"] if m != v["primary"]]} for v in info.values()],
        "promoted": [{"message_id": c["message_id"], "organisation": orgs[c["organisation_id"]]["name"], "recipient": by_id[c["message_id"]]["target_name"],
                      "role": by_id[c["message_id"]]["recipient_role"], "was": c["from"]} for c in promoted],
        "demoted": [{"message_id": c["message_id"], "organisation": orgs[c["organisation_id"]]["name"], "recipient": by_id[c["message_id"]]["target_name"],
                     "duplicate_of": c["duplicate_of"]} for c in demoted],
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
        for c in changes:
            plan = by_id[c["message_id"]]
            missing = DUPLICATE_NOTE.sub("", plan["missing_information"] or "").strip("; ").strip()
            if c["duplicate_of"]:
                missing = f"{missing}; {note_for(c, orgs)}" if missing else note_for(c, orgs)
            ready = plan["review_status"] == "Draft review"
            if c["to"] == "Candidate for review":
                status, action = ("Candidate after checks" if ready else "Needs research"), "Human review, then send the request"
            else:
                status, action = "Alternative - inactive", ("Duplicate organisation; keep inactive unless the primary record is rejected." if c["duplicate_of"]
                                                            else "Keep inactive unless the selected recipient is rejected or invalid.")
            if (c["to"], missing) != (plan["selection"], plan["missing_information"] or ""):
                con.execute("UPDATE outreach_plans SET selection=?, missing_information=? WHERE message_id=?", (c["to"], missing, c["message_id"]))
            if c["from"] != c["to"]:
                con.execute("UPDATE campaign_lead_assignments SET selection=?, eligibility_status=?, next_action=? WHERE message_id=?",
                            (c["to"], status, action, c["message_id"]))
        con.execute("DELETE FROM review WHERE kind LIKE 'Duplicate organisation (collapsed%' OR kind LIKE 'Shared inbox (one message%'")
        for root, v in info.items():
            for m in v["members"]:
                if m == v["primary"]:
                    continue
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (sid("collapse", m), "Duplicate organisation (collapsed for sending)" if v["kind"] == "same organisation" else "Shared inbox (one message per inbox)",
                             m, v["primary"], "organisation",
                             f"{orgs[m]['name']} and {orgs[v['primary']]['name']}: {v['kind']}. Decided {today} by resolve_master_recipients.py.",
                             "Its drafts are alternatives and one message goes to the primary record. Merge the records through the update skill when a person confirms."))
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
    if not moved and previous:
        print("Nothing changed; the record stays.")
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
