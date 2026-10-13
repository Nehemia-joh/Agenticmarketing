#!/usr/bin/env python3
"""Organisation email formats and the inferred work-email candidates made from them (the rule of 11 October 2026).

The rule (.claude/CLAUDE.md; docs/methodology/contact-research.md, "Email formats"). A work-email candidate generated from an
organisation's documented email format is:
- labelled "inferred from format, unverified";
- kept apart from every published route (never a contact's email, never a draft's route, never a high segment);
- kept out of committed files: candidates are written to runtime/ only;
- always low confidence;
- confirmed by a person (by phone, or through the organisation's published route) before any use.
The format itself is documented and committed: data/reference/email-formats.json.

Commands (run from the repository root; every database is opened read-only):

  python scripts/contacts/email_formats.py build              # propose formats; preview in runtime/contacts/email-formats-proposed.json
  python scripts/contacts/email_formats.py build --write      # write data/reference/email-formats.json (review the diff before committing)
  python scripts/contacts/email_formats.py candidates         # runtime/contacts/inferred-candidates.json (addresses: never commit)
  python scripts/contacts/email_formats.py check              # no candidate in a committed file, a route or a draft (exit 1 otherwise)
  python scripts/contacts/email_formats.py retire-table [--apply]   # drop the 2 October table candidate_emails from the master

The <track>-low-inferred.csv Resend files are written by scripts/messaging/export_resend_contacts.py, which calls
low_inferred_rows() below, so they are always made from the databases as they are at export time.

Formats (build). Evidence is a published address at the organisation's own domain whose mailbox is formed from the full name (first
and last) of a person the organisation itself names, under one pattern: first.last, first_last, firstlast, f.last, flast, firstl,
first, last. Only committed sources are read: the master and welfare databases (their contacts and organisation inboxes, which the
committed workbooks carry) and the research files in data/raw/contact-research/. The HTTP cache is not read.
- confirmed: two or more matching addresses of two or more different people, all showing the same pattern;
- provisional: one person's address shows it (generates nothing);
- ambiguous: the evidence shows two patterns (generates nothing).
Role inboxes (info@, hr@, md@ ...), mailboxes of three letters or fewer and free-mail domains are never evidence. The reference file
stores each piece of evidence as the pattern it shows, the person's record, the source URL and the date read: never the address.
A format belongs to its domain, never to another domain of the same group.

Candidates. Only for a named decision-maker who is an organisation's chosen in-country recipient or its escalation contact (master
companies and introducers; welfare run), whose name is complete (not one name, not initials), who is not pdpa_risk risky, not
board-only and not unverified, who has no published own address, and whose organisation's own domain has a confirmed format.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
sys.path.insert(0, str(ROOT / "scripts" / "master"))
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import offer_lib as L  # noqa: E402
import resolve_master_recipients as R  # noqa: E402
import contact_lib as C  # noqa: E402

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE = ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"
REFERENCE = ROOT / "data" / "reference" / "email-formats.json"
RESEARCH = ROOT / "data" / "raw" / "contact-research"
PROPOSED = ROOT / "runtime" / "contacts" / "email-formats-proposed.json"
CANDIDATES = ROOT / "runtime" / "contacts" / "inferred-candidates.json"

LABEL = "inferred from format, unverified"
CONFIDENCE = "low"
REASON = (f"{LABEL}: confirm by phone or through the organisation's published route before any send; "
          "never a draft's route, never a high segment")
INFERRED_FIELDS = ["inferred_format", "inferred_evidence", "inferred_label"]

FREE = re.compile(r"(^|\.)(gmail|googlemail|yahoo|hotmail|outlook|live|icloud|ymail|aol|proton|protonmail|rocketmail|msn|me)\.", re.I)
GENERIC = {"info", "sales", "reservations", "reservation", "bookings", "booking", "enquiries", "enquiry", "admin", "office", "contact", "hello",
           "operations", "safaris", "mail", "support", "accounts", "account", "marketing", "press", "karibu", "welcome", "reception",
           "customercare", "hr", "careers", "jobs", "tours", "travel", "safari", "team", "email", "inquiries", "inquiry", "res", "book",
           "finance", "director", "manager", "ceo", "md", "gm", "webmaster", "noreply", "no-reply", "dhrma"}
ORDER = ["first.last", "first_last", "firstlast", "f.last", "flast", "firstl", "first", "last"]
ADDRESS = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")


# ------------------------------------------------------------------ names and patterns
def name_parts(name: str) -> tuple[str, str]:
    """(first, last) in plain ASCII letters, titles and initials left out; (first, '') for one name; ('', '') for none."""
    return C.mailbox_name_parts(L.greeting_name(name or "") or name or "")


def local_for(pattern: str, first: str, last: str) -> str:
    """The mailbox a full name gives under a pattern ('' without a first and a last name)."""
    if not (first and last):
        return ""
    return {"first.last": f"{first}.{last}", "first_last": f"{first}_{last}", "firstlast": f"{first}{last}", "f.last": f"{first[0]}.{last}",
            "flast": f"{first[0]}{last}", "firstl": f"{first}{last[0]}", "first": first, "last": last}[pattern]


def patterns_of(local: str, first: str, last: str) -> list[str]:
    return [p for p in ORDER if local_for(p, first, last) == local]


def pattern_of(local: str, first: str, last: str):
    """The first pattern (in ORDER) that forms the mailbox from the full name, or None."""
    found = patterns_of(local, first, last)
    return found[0] if found else None


def addresses(*values) -> list[str]:
    found = []
    for value in values:
        for token in ADDRESS.findall(str(value or "")):
            token = token.lower().strip(".")
            if token not in found:
                found.append(token)
    return found


def role_mailbox(local: str) -> bool:
    letters = re.sub(r"[^a-z]", "", local)
    return local in GENERIC or bool(C.ROLE_LOCALS.match(letters)) or len(letters) <= 3


def free_domain(domain: str) -> bool:
    return bool(FREE.search(domain + "."))


def same_or_sub(host: str, site: str) -> bool:
    return bool(host and site) and (host == site or host.endswith("." + site))


# ------------------------------------------------------------------ evidence from committed sources
def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def file_date(path: Path) -> str:
    m = re.search(r"(\d{4}-\d\d-\d\d)", path.name)
    return m.group(1) if m else ""


def gather(master: sqlite3.Connection, welfare: sqlite3.Connection | None):
    """Published addresses, the people each organisation names, and each organisation's own domains.

    Returns (orgs, people, published):
      orgs      {(db, oid): {"name", "domains": set}}
      people    {(db, oid): [{"name", "ref", "source_url", "accessed_on", "own": [addresses linked to the person by the source]}]}
      published [{"address", "key": (db, oid), "person": name or '', "ref", "source_url", "accessed_on", "fetched"}]
    """
    orgs, people, published = {}, defaultdict(list), []
    for con in (master, welfare):
        if con is not None:
            con.row_factory = sqlite3.Row

    def org(key, name, *domains):
        o = orgs.setdefault(key, {"name": name, "domains": set()})
        o["domains"] |= {d.lower() for d in domains if d and not free_domain(d)}
        return o

    for o in master.execute("SELECT organisation_id, name, website, email, source_url FROM organisations"):
        key = ("master", o["organisation_id"])
        own = [a.split("@")[1] for a in addresses(o["email"])]
        site = R.domain(o["website"])
        org(key, o["name"], site, *[d for d in own if same_or_sub(d, site) or same_or_sub(site, d) or not site])
        for a in addresses(o["email"]):
            published.append({"address": a, "key": key, "person": "", "ref": f"master:{o['organisation_id']}", "source_url": o["source_url"] or "",
                              "accessed_on": "", "fetched": True})
    for c in master.execute("SELECT contact_id, organisation_id, name, source_url, verification, named_email, published_role_email, shared_email "
                            "FROM contacts"):
        key = ("master", c["organisation_id"])
        own = addresses(c["named_email"], c["published_role_email"])
        dated = re.search(r"(\d{4}-\d\d-\d\d)", c["verification"] or "")
        people[key].append({"name": c["name"] or "", "ref": f"master:{c['contact_id']}", "source_url": c["source_url"] or "",
                            "accessed_on": dated.group(1) if dated else "", "own": own})
        for a in addresses(c["named_email"], c["published_role_email"], c["shared_email"]):
            published.append({"address": a, "key": key, "person": c["name"] if a in own else "", "ref": f"master:{c['contact_id']}",
                              "source_url": c["source_url"] or "", "accessed_on": dated.group(1) if dated else "", "fetched": True})
    if welfare is not None:
        for o in welfare.execute("SELECT organisation_id, name, domain, website, email FROM organisations"):
            key = ("welfare", o["organisation_id"])
            org(key, o["name"], (o["domain"] or "").lower(), R.domain(o["website"]))
            for a in addresses(o["email"]):
                published.append({"address": a, "key": key, "person": "", "ref": f"welfare:{o['organisation_id']}", "source_url": o["website"] or "",
                                  "accessed_on": "", "fetched": True})
        src = {}
        for eid, payload in welfare.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr "
                                            "ON sr.source_record_id = es.source_record_id WHERE es.entity_type = 'contact'"):
            src.setdefault(eid, json.loads(payload))
        for c in welfare.execute("SELECT contact_id, organisation_id, name, profile_url, named_email, published_role_email, shared_email FROM contacts"):
            key = ("welfare", c["organisation_id"])
            p = src.get(c["contact_id"], {})
            own = addresses(c["named_email"], c["published_role_email"])
            url = p.get("source_url") or c["profile_url"] or ""
            people[key].append({"name": c["name"] or "", "ref": f"welfare:{c['contact_id']}", "source_url": url,
                                "accessed_on": p.get("verified_on") or p.get("acquired_on") or "", "own": own})
            for a in addresses(c["named_email"], c["published_role_email"], c["shared_email"]):
                published.append({"address": a, "key": key, "person": c["name"] if a in own else "", "ref": f"welfare:{c['contact_id']}",
                                  "source_url": url, "accessed_on": p.get("verified_on") or "", "fetched": True})

    # Research files (committed): agent and browser records, and the crawler's site records.
    for path in sorted(RESEARCH.glob("*.jsonl")):
        stem = path.name
        day = file_date(path)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            ref = f"{stem}#L{n}"
            if stem.startswith("website_contacts_"):
                site = (r.get("domain") or "").lower()
                keys = [(o.get("db"), o.get("organisation_id")) for o in r.get("orgs", []) if o.get("db") in ("master", "welfare")]
                for key, o in zip(keys, [o for o in r.get("orgs", []) if o.get("db") in ("master", "welfare")]):
                    org(key, o.get("name", ""), site)
                    for x in r.get("people", []) or []:
                        people[key].append({"name": x.get("name", ""), "ref": ref, "source_url": x.get("page") or r.get("start_url", ""),
                                            "accessed_on": r.get("fetched_on", day), "own": []})
                emails = r.get("emails") or {}
                for a, info in (emails.items() if isinstance(emails, dict) else ((e, {}) for e in emails)):
                    for key in keys:
                        pages = (info or {}).get("pages") or [r.get("start_url", "")]
                        published.append({"address": a.lower(), "key": key, "person": "", "ref": ref, "source_url": pages[0],
                                          "accessed_on": r.get("fetched_on", day), "fetched": True})
                continue
            if r.get("db") not in ("master", "welfare") or not r.get("organisation_id"):
                continue
            key = (r["db"], r["organisation_id"])
            org(key, r.get("organisation_name", ""), R.domain(r.get("website")))
            dates = {s.get("url"): s.get("accessed_on", "") for s in r.get("sources", []) or [] if isinstance(s, dict)}
            for e in r.get("emails", []) or []:
                if isinstance(e, dict) and e.get("value"):
                    for a in addresses(e["value"]):
                        published.append({"address": a, "key": key, "person": "", "ref": ref, "source_url": e.get("source_url", ""),
                                          "accessed_on": dates.get(e.get("source_url"), day), "fetched": bool(e.get("fetched"))})
            for x in r.get("people", []) or []:
                own = addresses(x.get("email"))
                acc = x.get("source_date") or dates.get(x.get("source_url"), day)
                people[key].append({"name": x.get("name", ""), "ref": ref, "source_url": x.get("source_url", ""), "accessed_on": acc, "own": own})
                for a in own:
                    published.append({"address": a, "key": key, "person": x.get("name", ""), "ref": ref, "source_url": x.get("source_url", ""),
                                      "accessed_on": acc, "fetched": bool(x.get("fetched"))})
    return orgs, people, published


def derive(orgs, people, published) -> dict:
    """{domain: entry} for every non-free domain at which a published address shows a format."""
    evidence = defaultdict(dict)  # domain -> address -> item
    org_of = defaultdict(set)     # domain -> organisations whose records hold evidence there
    for p in published:
        a = p["address"]
        if "@" not in a:
            continue
        local, domain = a.split("@", 1)
        o = orgs.get(p["key"])
        if free_domain(domain) or role_mailbox(local) or not o or not any(same_or_sub(domain, d) or same_or_sub(d, domain) for d in o["domains"]):
            continue  # only an address at the organisation's own domain is evidence
        if a in evidence[domain]:
            continue
        # The person: the one the source links the address to; otherwise a person this organisation names whose full name forms it.
        names = [p["person"]] if p["person"] else [x["name"] for x in people.get(p["key"], [])]
        matches = {}
        for name in dict.fromkeys(n for n in names if n):
            if C.name_status(name) != "complete":
                continue
            first, last = name_parts(name)
            pats = patterns_of(local, first, last)
            if pats:
                matches[(first, last)] = (pats[0], name)
        if len(matches) != 1:  # no named person forms it, or two different people could: not evidence
            continue
        (who, (pattern, name)), = matches.items()
        person_ref = p["ref"]
        if not p["person"]:
            hit = next((x for x in people.get(p["key"], []) if x["name"] == name), None)
            person_ref = hit["ref"] if hit else p["ref"]
        evidence[domain][a] = {"pattern": pattern, "person_key": " ".join(who), "person_ref": person_ref, "source_url": p["source_url"],
                               "accessed_on": p["accessed_on"], "fetched": p["fetched"]}
        org_of[domain].add(p["key"])
    formats = {}
    for domain, items in evidence.items():
        if not items:
            continue
        votes = Counter(i["pattern"] for i in items.values())
        persons = defaultdict(set)
        for i in items.values():
            persons[i["pattern"]].add(i["person_key"])
        if len(votes) > 1:
            status, pattern = "ambiguous", ""
        else:
            pattern = next(iter(votes))
            status = "confirmed" if len(items) >= 2 and len(persons[pattern]) >= 2 else "provisional"
        formats[domain] = {
            "domain": domain, "pattern": pattern, "status": status, "evidence_count": len(items),
            "people_count": len({i["person_key"] for i in items.values()}),
            **({"votes": dict(votes)} if status == "ambiguous" else {}),
            "evidence": [{k: i[k] for k in ("pattern", "person_ref", "source_url", "accessed_on", "fetched")}
                         for _, i in sorted(items.items(), key=lambda kv: (kv[1]["person_ref"], kv[1]["source_url"]))][:5],
            "organisations": [{"db": k[0], "organisation_id": k[1], "name": orgs[k]["name"]} for k in sorted(org_of[domain]) if k in orgs]}
    return formats


def load_formats(path: Path = REFERENCE) -> dict:
    """{domain: entry} from the committed reference file ({} when it does not exist yet)."""
    if not path.exists():
        return {}
    return {f["domain"]: f for f in json.loads(path.read_text(encoding="utf-8")).get("formats", [])}


def format_text(entry: dict) -> str:
    """The committed form of a format: the pattern and its evidence count, never an address."""
    return (f"{entry['pattern']} at {entry['domain']} ({entry['evidence_count']} published examples, {entry['people_count']} people); "
            f"{LABEL}: confirm before use")


# ------------------------------------------------------------------ candidates (runtime only)
def _eligible(name: str, role: str, risky: bool, verified: bool, own: list) -> str:
    """'' when a candidate may be made for the person, else the reason it may not."""
    if own:
        return "has a published own address"
    if C.name_status(name) != "complete":
        return "name incomplete (one name or initials)"
    if risky:
        return "pdpa_risk risky"
    if not verified:
        return "not verified"
    if R.BOARD.search(role or "") and not R.EXECUTIVE.search(role or ""):
        return "board-only role"
    return ""


def master_candidates(con: sqlite3.Connection, formats: dict, stats: Counter):
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT organisation_id, name, website, email FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    out = []
    for p in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review' ORDER BY organisation_name"):
        p = dict(p)
        org = orgs.get(p["organisation_id"])
        if not org:
            continue
        track = "introducers" if p["segment"] == "Introducers" else "companies"
        who = []
        if p["target_type"] == "contact" and p["target_id"] in contacts:
            who.append(("recipient", contacts[p["target_id"]]))
        if p.get("escalation_contact_id") in contacts and p.get("escalation_contact_id") != p["target_id"]:
            who.append(("escalation", contacts[p["escalation_contact_id"]]))
        site = R.domain(org["website"])
        for kind, c in who:
            own = addresses(c["named_email"], c["published_role_email"])
            verified = bool(R.VERIFIED.search(c["verification"] or "")) and not R.UNUSABLE.search(c["verification"] or "")
            decides = R.role_rank_for(c["role"], p["segment"] or "") is not None or (kind == "recipient" and bool(R.FALLBACK_OK.search(c["role"] or "")))
            why = _eligible(c["name"] or "", c["role"] or "", "pdpa_risk risky" in (c["verification"] or ""), verified, own)
            if not why and not decides:
                why = "not a decision-maker"
            entry = _format_for(formats, site, ("master", org["organisation_id"]))
            if not entry:
                stats[f"{track} {kind}: no confirmed format at the organisation's domain"] += 1
                continue
            if why:
                stats[f"{track} {kind}: skipped ({why})"] += 1
                continue
            first, last = name_parts(c["name"])
            out.append(_candidate("master", track, kind, p["message_id"], org["organisation_id"], org["name"], c["contact_id"], c["name"],
                                  c["role"], first, last, entry))
    return out


def welfare_candidates(con: sqlite3.Connection, formats: dict, stats: Counter):
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT organisation_id, name, domain, website FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    by_org = defaultdict(list)
    for c in contacts.values():
        by_org[c["organisation_id"]].append(c)
    risk = {}
    for eid, payload in con.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr "
                                    "ON sr.source_record_id = es.source_record_id WHERE es.entity_type = 'contact'"):
        if json.loads(payload).get("pdpa_risk") == "risky":
            risk[eid] = True
    out = []
    for p in con.execute("SELECT * FROM outreach_plans WHERE target_type='organisation'"):
        p = dict(p)
        org = orgs.get(p["organisation_id"])
        if not org:
            continue
        who = []
        recipient = (p["recipient"] or "").split("(")[0].strip()
        if recipient and not re.search(r"team|organisation route", p["recipient"] or "", re.I):
            hit = next((c for c in by_org[p["organisation_id"]] if c["name"] and C.same_person(c["name"], recipient)), None)
            if hit:
                who.append(("recipient", hit))
        if p.get("escalation_contact_id") in contacts and not any(c["contact_id"] == p["escalation_contact_id"] for _, c in who):
            who.append(("escalation", contacts[p["escalation_contact_id"]]))
        site = (org["domain"] or "").lower() or R.domain(org["website"])
        for kind, c in who:
            own = addresses(c["named_email"], c["published_role_email"])
            why = _eligible(c["name"] or "", c["role"] or "", risk.get(c["contact_id"], False), c["role_certainty"] == "confirmed", own)
            if not why and not C.DECISION.search(C.NOT_A_HEAD.sub("", c["role"] or "")):
                why = "not a decision-maker"
            entry = _format_for(formats, site, ("welfare", org["organisation_id"]))
            if not entry:
                stats[f"welfare {kind}: no confirmed format at the organisation's domain"] += 1
                continue
            if why:
                stats[f"welfare {kind}: skipped ({why})"] += 1
                continue
            first, last = name_parts(c["name"])
            out.append(_candidate("welfare", "welfare", kind, p["message_id"], org["organisation_id"], org["name"], c["contact_id"], c["name"],
                                  c["role"], first, last, entry))
    return out


def _format_for(formats: dict, site: str, key: tuple):
    """The confirmed format of the organisation's own domain: its website's domain, or a domain whose evidence came from its own records."""
    if site and site in formats and formats[site]["status"] == "confirmed":
        return formats[site]
    for f in formats.values():
        if f["status"] == "confirmed" and any((o["db"], o["organisation_id"]) == key for o in f.get("organisations", [])):
            return f
    return None


def _candidate(db, track, kind, plan_id, oid, org_name, contact_id, name, role, first, last, entry) -> dict:
    return {"db": db, "track": track, "for": kind, "plan_id": plan_id, "organisation_id": oid, "organisation": org_name,
            "contact_id": contact_id, "person": name, "role": role or "", "first_name": first, "last_name": last,
            "address": f"{local_for(entry['pattern'], first, last)}@{entry['domain']}", "confidence": CONFIDENCE, "label": LABEL,
            "format": entry["pattern"], "format_domain": entry["domain"], "format_status": entry["status"],
            "evidence": f"{entry['evidence_count']} published examples, {entry['people_count']} people",
            "evidence_sources": sorted({e["source_url"] for e in entry["evidence"] if e.get("source_url")})}


def all_published(master: sqlite3.Connection, welfare: sqlite3.Connection | None) -> set:
    """Every address the databases and research files publish (an inferred address equal to one of these is not inferred)."""
    _, _, published = gather(master, welfare)
    return {p["address"] for p in published}


def candidates(master: sqlite3.Connection, welfare: sqlite3.Connection | None, formats: dict | None = None):
    formats = load_formats() if formats is None else formats
    stats = Counter()
    rows = master_candidates(master, formats, stats) + (welfare_candidates(welfare, formats, stats) if welfare is not None else [])
    published = all_published(master, welfare)
    keep = []
    for r in rows:
        if r["address"] in published:
            stats["skipped: the generated address is already published (merge it as a route instead)"] += 1
            continue
        keep.append(r)
    stats["candidates"] = len(keep)
    for r in keep:
        stats[f"candidates: {r['track']} {r['for']}"] += 1
    return keep, dict(stats)


def low_inferred_rows(cands: list, base_rows: list, fields: list) -> dict:
    """{track: [rows]} for runtime/resend/<date>/<track>-low-inferred.csv. Each row is the plan's exported row (its message and
    properties) with the candidate as the address, confidence low and the label; plans without an exported row get the plan's
    organisation and IDs only. The organisation's own row stays in its segment unchanged."""
    by_plan = {r["plan_id"]: r for r in base_rows}
    out = defaultdict(list)
    for c in cands:
        base = dict(by_plan.get(c["plan_id"]) or {k: "" for k in fields})
        base.update({"email": c["address"], "first_name": c["first_name"].title(), "last_name": c["last_name"].title(),
                     "organisation": base.get("organisation") or c["organisation"], "track": c["track"], "confidence": CONFIDENCE,
                     "high_route": "", "recipient": f"{c['person']} ({c['role']})" if c["role"] else c["person"],
                     "confidence_reason": f"{REASON}" + ("; escalation contact, write only per the escalation trigger" if c["for"] == "escalation" else ""),
                     "plan_id": c["plan_id"], "inferred_format": f"{c['format']} at {c['format_domain']}",
                     "inferred_evidence": f"{c['evidence']}: " + " ".join(c["evidence_sources"][:3]), "inferred_label": LABEL})
        out[c["track"]].append(base)
    return out


# ------------------------------------------------------------------ commands
def cmd_build(args) -> int:
    master, welfare = ro(args.master), (ro(args.welfare) if args.welfare.exists() else None)
    formats = derive(*gather(master, welfare))
    old = load_formats()
    today = date.today().isoformat()
    for d, f in formats.items():
        prev = old.get(d)
        same = prev and prev.get("pattern") == f["pattern"] and prev.get("status") == f["status"]
        f["decided_on"] = prev.get("decided_on", today) if same else today
        f["reviewed_by"] = prev.get("reviewed_by", "") if same else ""
    stats = Counter(f["status"] for f in formats.values())
    stats_patterns = Counter(f["pattern"] for f in formats.values() if f["status"] == "confirmed")
    changed = sorted(d for d in formats.keys() | old.keys()
                     if (formats.get(d) or {}).get("status") != (old.get(d) or {}).get("status")
                     or (formats.get(d) or {}).get("pattern") != (old.get(d) or {}).get("pattern"))
    doc = {"about": ("Organisation email formats (docs/methodology/contact-research.md, 'Email formats', 11 October 2026). Written by "
                     "scripts/contacts/email_formats.py build --write from published addresses in committed sources; reviewed before commit. "
                     "Evidence is stored as the pattern each published address shows, the person's record, the source URL and the date read, "
                     "never as an address. Only 'confirmed' formats (two or more people, one pattern) generate candidates, and those are written "
                     "to runtime/ only, labelled 'inferred from format, unverified', always low confidence."),
           "updated_on": today, "counts": {"confirmed": stats["confirmed"], "provisional": stats["provisional"], "ambiguous": stats["ambiguous"]},
           "formats": [formats[d] for d in sorted(formats, key=lambda d: ({"confirmed": 0, "provisional": 1, "ambiguous": 2}[formats[d]["status"]], d))]}
    target = REFERENCE if args.write else PROPOSED
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"formats": dict(stats), "confirmed_patterns": dict(stats_patterns), "changed_domains": changed}, indent=1))
    print(("Written: " if args.write else "Preview only: ") + str(target))
    return 0


def cmd_candidates(args) -> int:
    master, welfare = ro(args.master), (ro(args.welfare) if args.welfare.exists() else None)
    rows, stats = candidates(master, welfare)
    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES.write_text(json.dumps({"label": LABEL, "confidence": CONFIDENCE, "generated_on": date.today().isoformat(),
                                      "note": "Runtime only: never commit. A person confirms each address before any use.",
                                      "stats": stats, "candidates": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=1))
    print(f"{CANDIDATES} (not committed)")
    return 0


def tracked_texts():
    """(path, text) for every file Git tracks that can hold an address (text files, and the strings of .xlsx workbooks)."""
    names = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8").split("\0")
    for name in filter(None, names):
        path = ROOT / name
        if not path.exists() or path.stat().st_size > 60_000_000:
            continue
        if path.suffix.lower() == ".xlsx":
            try:
                with zipfile.ZipFile(path) as z:
                    yield name, " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
            except zipfile.BadZipFile:
                continue
        elif path.suffix.lower() in {".md", ".json", ".jsonl", ".csv", ".tsv", ".txt", ".html", ".py", ".js", ".mjs"}:
            yield name, path.read_text(encoding="utf-8", errors="ignore")


def cmd_check(args) -> int:
    """No inferred candidate in a committed file, a contact field or a draft's route; the reference file holds no address."""
    master, welfare = ro(args.master), (ro(args.welfare) if args.welfare.exists() else None)
    rows, _ = candidates(master, welfare)
    inferred = {r["address"] for r in rows}
    try:
        inferred |= {r[0].lower() for r in master.execute("SELECT address FROM candidate_emails")}  # the retired 2 October table
    except sqlite3.OperationalError:
        pass
    published = all_published(master, welfare)
    inferred -= published
    failures, where = defaultdict(list), {}
    if REFERENCE.exists() and ADDRESS.search(REFERENCE.read_text(encoding="utf-8")):
        failures["data/reference/email-formats.json holds an address"].append(str(REFERENCE.relative_to(ROOT)))
    for p in master.execute("SELECT message_id, contact_channel FROM outreach_plans"):
        if set(addresses(p["contact_channel"])) & inferred:
            failures["an inferred address is a master draft's route"].append(p["message_id"])
    if welfare is not None:
        for p in welfare.execute("SELECT message_id, route_value FROM outreach_plans"):
            if set(addresses(p["route_value"])) & inferred:
                failures["an inferred address is a welfare draft's route"].append(p["message_id"])
    if inferred:
        pattern = re.compile(r"(?<![\w.%+\-])(" + "|".join(re.escape(a) for a in sorted(inferred)) + r")(?![\w\-]|\.[a-z])", re.I)
        for name, text in tracked_texts():
            found = {m.lower() for m in pattern.findall(text)}
            if found:
                failures["an inferred address is in a committed file"].append(f"{name} ({len(found)})")
                where[name] = found
    result = {"inferred_addresses_checked": len(inferred), "failures": {k: sorted(set(v)) for k, v in failures.items()}}
    print(json.dumps(result, indent=1))
    if where and args.detail:  # the addresses themselves: runtime/ only
        args.detail.parent.mkdir(parents=True, exist_ok=True)
        args.detail.write_text(json.dumps({k: sorted(v) for k, v in where.items()}, indent=1), encoding="utf-8")
        print(f"Detail (addresses; never commit): {args.detail}")
    return 1 if failures else 0


def cmd_retire_table(args) -> int:
    """The 2 October table candidate_emails (medium confidence, partial names) is superseded: candidates live in runtime/ only."""
    con = sqlite3.connect(args.database)
    try:
        n = con.execute("SELECT COUNT(*) FROM candidate_emails").fetchone()[0]
    except sqlite3.OperationalError:
        print("No table candidate_emails: nothing to retire.")
        return 0
    print(f"candidate_emails holds {n} rows (the 2 October rule).")
    if not args.apply:
        print("Preview only: --apply drops the table in one transaction.")
        return 0
    try:
        con.execute("BEGIN")
        con.execute("DROP TABLE candidate_emails")
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    print("Dropped. Then run export_master_workbook_data.py, npm run build:workbook and verify_master.py.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "candidates", "check"):
        p = sub.add_parser(name)
        p.add_argument("--master", type=Path, default=MASTER)
        p.add_argument("--welfare", type=Path, default=WELFARE)
        if name == "check":
            p.add_argument("--detail", type=Path, default=ROOT / "runtime" / "contacts" / "inferred-check-detail.json",
                           help="where to write which addresses were found in which file (runtime/ only)")
        if name == "build":
            p.add_argument("--write", action="store_true", help="write data/reference/email-formats.json (review the diff before committing)")
    p = sub.add_parser("retire-table")
    p.add_argument("--database", type=Path, default=MASTER)
    p.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    return {"build": cmd_build, "candidates": cmd_candidates, "check": cmd_check, "retire-table": cmd_retire_table}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
