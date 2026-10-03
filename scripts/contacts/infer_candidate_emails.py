#!/usr/bin/env python3
"""Propose candidate work-email addresses for named decision-makers whose company publishes an address pattern.

Decided by the user on 2 October 2026 (it overrides the earlier rule never to infer a contact detail), with these safeguards:
- A candidate is made only when the company's own domain already shows a personal-style address that belongs to a named person on
  file, so the pattern has evidence (for example joseph@faune-flore.com belongs to Joseph Aweth, so the pattern is first name).
  Generic mailboxes (info@, sales@, reservations@ ...) and free-mail addresses are never evidence.
- A candidate is kept apart from every published route, in the table candidate_emails. It is never written to contacts, never becomes the
  route of a draft, and is marked "candidate, unverified": a person approves each address before it is used.
- Confidence is medium when two or more published addresses at the domain follow the pattern, low when one does.
- A name given only in part gets a candidate only for a first-name pattern and only when no one else at the company shares the first name.
Default: preview (runtime/contacts/candidate-emails-preview.json); nothing changes. --apply writes the table in one transaction.
Afterwards run export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import offer_lib as L  # noqa: E402
import resolve_master_recipients as R  # noqa: E402

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
PREVIEW = ROOT / "runtime" / "contacts" / "candidate-emails-preview.json"
GENERIC = {"info", "sales", "reservations", "reservation", "bookings", "booking", "enquiries", "enquiry", "admin", "office", "contact", "hello", "operations",
           "safaris", "mail", "support", "accounts", "account", "marketing", "press", "karibu", "welcome", "reception", "customercare", "hr", "careers", "jobs",
           "tours", "travel", "safari", "team", "email", "inquiries", "inquiry", "res", "book", "booking", "finance", "director", "manager", "ceo", "md", "gm",
           "webmaster", "noreply", "no-reply", "dhrma"}
FREE = re.compile(r"(gmail|yahoo|hotmail|outlook|live|icloud|ymail|aol|proton|rocketmail)\.", re.I)
TITLES = {"dr", "mr", "mrs", "ms", "miss", "eng", "prof", "rev", "hon", "cpa", "mag", "sir", "fr", "pastor", "bishop", "mzee", "ca", "adv"}
ORDER = ["first.last", "first_last", "firstlast", "f.last", "flast", "firstl", "first", "last"]
NEEDS_LAST = {"first.last", "first_last", "firstlast", "f.last", "flast", "firstl", "last"}


def ascii_token(text: str) -> str:
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower())


def name_parts(name: str):
    """(first, last) in ASCII, or (first, '') when only one name is given."""
    text = re.sub(r"\([^)]*\)", " ", L.greeting_name(name))
    tokens = [ascii_token(t) for t in re.split(r"[\s,]+", text) if t]
    tokens = [t for t in tokens if len(t) > 1 and t not in TITLES]
    return (tokens[0], tokens[-1]) if len(tokens) >= 2 else ((tokens[0], "") if tokens else ("", ""))


def local_for(pattern: str, first: str, last: str) -> str:
    if not first or (pattern in NEEDS_LAST and not last):
        return ""
    return {"first.last": f"{first}.{last}", "first_last": f"{first}_{last}", "firstlast": f"{first}{last}", "f.last": f"{first[0]}.{last}",
            "flast": f"{first[0]}{last}", "firstl": f"{first}{last[:1]}", "first": first, "last": last}[pattern]


def pattern_of(local: str, first: str, last: str):
    for pattern in ORDER:
        if local_for(pattern, first, last) == local:
            return pattern
    return None


def addresses(*values):
    found = []
    for value in values:
        for token in re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+", str(value or "")):
            token = token.lower().strip(".")
            if token not in found:
                found.append(token)
    return found


def build(con):
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = defaultdict(list)
    for r in con.execute("SELECT * FROM contacts"):
        contacts[r["organisation_id"]].append(dict(r))
    chosen = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review'")}
    firstnames = {name_parts(c["name"] or "")[0] for cs in contacts.values() for c in cs}
    firstnames = {f for f in firstnames if len(f) >= 3} - GENERIC
    by_domain = defaultdict(set)  # an email domain -> the organisation records that use it
    for oid, o in orgs.items():
        for a in addresses(o["email"], *[c["shared_email"] for c in contacts[oid]], *[c["named_email"] for c in contacts[oid]], *[c["published_role_email"] for c in contacts[oid]]):
            if not FREE.search(a):
                by_domain[a.split("@")[1]].add(oid)
    rows, stats = [], Counter()
    for domain, oids in sorted(by_domain.items()):
        people = [c for oid in oids for c in contacts[oid]]
        published = set()
        for oid in oids:
            published |= set(addresses(orgs[oid]["email"], *[c["shared_email"] for c in contacts[oid]], *[c["named_email"] for c in contacts[oid]],
                                       *[c["published_role_email"] for c in contacts[oid]]))
        evidence = []  # (pattern, address, person)
        for a in sorted(published):
            local, d = a.split("@")
            if d != domain or local in GENERIC or re.fullmatch(r"[a-z]{1,3}", local):
                continue
            for c in people:
                first, last = name_parts(c["name"] or "")
                pattern = pattern_of(local, first, last) if first else None
                if pattern:
                    evidence.append((pattern, a, c))
                    break
            else:
                if local in firstnames:  # a first-name mailbox whose owner is not named on file still shows the company uses first names
                    evidence.append(("first", a, {"name": "owner not named", "source_url": ""}))
        if not evidence:
            stats["domains without evidence"] += 1
            continue
        votes = Counter(p for p, _, _ in evidence)
        pattern, agree = votes.most_common(1)[0]
        if len(votes) > 1 and votes.most_common(2)[1][1] == agree:
            stats["domains with conflicting patterns"] += 1
            continue
        proof = [(a, c) for p, a, c in evidence if p == pattern]
        confidence = "medium" if len(proof) >= 2 else "low"
        for oid in sorted(oids):
            firsts = Counter(name_parts(c["name"] or "")[0] for c in contacts[oid])
            for c in contacts[oid]:
                first, last = name_parts(c["name"] or "")
                rank = R.role_rank(c["role"])
                is_chosen = chosen.get(oid, {}).get("target_id") == c["contact_id"]
                if not first or not (rank is not None or is_chosen) or R.UNUSABLE.search(c["verification"] or ""):
                    continue
                own = [a for a in addresses(c["named_email"], c["published_role_email"]) if a.split("@")[0] not in GENERIC]
                if own:
                    continue
                if not last and (pattern in NEEDS_LAST or firsts[first] > 1):
                    stats["skipped: name incomplete"] += 1
                    continue
                local = local_for(pattern, first, last)
                address = f"{local}@{domain}"
                if not local or address in published:
                    continue
                rows.append({"candidate_id": "E" + hashlib.sha256(f"{c['contact_id']}|{address}".encode()).hexdigest()[:12], "contact_id": c["contact_id"], "organisation_id": oid,
                             "organisation": orgs[oid]["name"], "person": c["name"], "role": c["role"], "address": address, "pattern": pattern, "confidence": confidence,
                             "evidence": "; ".join(f"{a} ({ec['name']})" for a, ec in proof[:3]), "chosen_recipient": is_chosen,
                             "evidence_source": next((ec.get("source_url") for _, ec in proof if ec.get("source_url")), "") or orgs[oid].get("source_url") or ""})
    stats["candidates"] = len(rows)
    stats["for the chosen recipient"] = sum(1 for r in rows if r["chosen_recipient"])
    return rows, dict(stats)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    rows, stats = build(con)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps({"stats": stats, "candidates": rows}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, indent=1))
    if not args.apply:
        print(f"Preview only: {PREVIEW}")
        return 0
    today = date.today().isoformat()
    try:
        con.execute("BEGIN")
        con.execute("""CREATE TABLE IF NOT EXISTS candidate_emails (candidate_id TEXT PRIMARY KEY, contact_id TEXT, organisation_id TEXT, address TEXT, pattern TEXT,
                       confidence TEXT, evidence TEXT, evidence_source TEXT, status TEXT, created_on TEXT, approved_by TEXT, approved_on TEXT)""")
        keep = {r["candidate_id"] for r in rows}
        for (cid,) in con.execute("SELECT candidate_id FROM candidate_emails WHERE status LIKE 'candidate%'").fetchall():
            if cid not in keep:
                con.execute("DELETE FROM candidate_emails WHERE candidate_id=?", (cid,))
        for r in rows:
            con.execute("INSERT OR IGNORE INTO candidate_emails VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (r["candidate_id"], r["contact_id"], r["organisation_id"], r["address"], r["pattern"], r["confidence"], r["evidence"], r["evidence_source"],
                         "candidate, unverified: a person approves it before use", today, "", ""))
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    print("Applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
