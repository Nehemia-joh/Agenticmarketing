#!/usr/bin/env python3
"""Add introducer bodies to the company master: associations, chambers and HR bodies that could share the staff education benefit with their
members (the user's decision of 2 October 2026).

Reads data/raw/contact-research/introducers_*_<date>.jsonl (a research agent's records: name, kind, members, member_count, area, website,
emails, phones, addresses, people, channels, sources, notes). Every body is matched to the master by exact normalised name or website domain
first; a match is reused, never duplicated. Then, in one transaction:
- the raw file goes into source_files, and each body gets one source record;
- a new body becomes an organisation with segment "Introducer: <kind>" (draft_master_messages.py files its plans under "Introducers" and writes
  the introducer request, so its first message asks for a partnership with the members in mind and states no offer terms);
- its named secretariat people become contacts, with an email only when the same source gave it for that person or role.
Nothing is sent. Preview by default (runtime/master/introducers-preview.json); --apply writes. Afterwards run draft_master_messages.py,
refresh_acquisition_metadata.py, assign_message_variants.py --apply, export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import sqlite3
import sys
import zlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "contact-research"
PREVIEW = ROOT / "runtime" / "master" / "introducers-preview.json"
DECISIONS = ROOT / "data" / "reference" / "introducer-decisions.json"
GENERIC = re.compile(r"^(info|contact|office|admin|secretariat|membership|members|communications|hello|enquiries|mail|support|ed|ceo|sg|chair|director)@", re.I)
FREE = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|ymail)\.", re.I)


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", re.sub(r"\([^)]*\)", "", str(name or "").lower()))


def domain(url: str) -> str:
    m = re.search(r"(?:https?://)?(?:www\.)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)+)", str(url or "").lower())
    return m.group(1) if m else ""


def clean_name(name: str) -> str:
    """'Tanzania Private Sector Foundation (TPSF; site name: ...)' -> 'Tanzania Private Sector Foundation (TPSF)': research notes after ';' go."""
    name = re.sub(r"\(([^();]*);[^()]*\)", lambda m: f"({m.group(1).strip()})", " ".join(str(name or "").split()))
    return re.sub(r"\s+", " ", name).strip()


def first(items, key="value"):
    for item in items or []:
        value = (item.get(key) if isinstance(item, dict) else item) or ""
        if value:
            return value
    return ""


def load(run_date: str):
    files = sorted(Path(p) for p in glob.glob(str(RAW / f"introducers_*_{run_date}.jsonl")))
    records = []
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append((path, json.loads(line)))
    return files, records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    files, records = load(args.date)
    if not records:
        raise SystemExit(f"No introducer records for {args.date}.")
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    by_name = {norm(r["name"]): r["organisation_id"] for r in con.execute("SELECT organisation_id, name FROM organisations")}
    by_domain = {}
    for r in con.execute("SELECT organisation_id, website FROM organisations"):
        if domain(r["website"]):
            by_domain.setdefault(domain(r["website"]), r["organisation_id"])
    existing_people = {(r["organisation_id"], norm(r["name"])) for r in con.execute("SELECT organisation_id, name FROM contacts")}
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8")) if DECISIONS.exists() else {"skip": {}, "names": {}}
    plan, skipped = [], []
    for path, rec in records:
        name = clean_name(rec.get("name"))
        name = decisions.get("names", {}).get(name, name)
        if not name:
            continue
        if any(name.startswith(k) for k in decisions.get("skip", {})):
            skipped.append(name)
            continue
        if not (rec.get("emails") or rec.get("phones") or rec.get("people")):
            skipped.append(f"{name} (no route and no named person)")
            continue
        match = by_name.get(norm(name)) or by_domain.get(domain(rec.get("website")))
        oid = match or hid("O", "introducer", norm(name))
        email = first([e for e in rec.get("emails") or [] if not FREE.search(e.get("value") or "")])
        phone = first(rec.get("phones"))
        people = []
        for p in rec.get("people") or []:
            pname = " ".join(str(p.get("name") or "").split())
            if not pname or (oid, norm(pname)) in existing_people:
                continue
            pmail = (p.get("email") or "").strip().lower()
            people.append({"contact_id": hid("C", "introducer", oid, norm(pname)), "name": pname, "role": p.get("role") or "",
                           "source_url": p.get("source_url") or first(rec.get("sources"), "url"), "excerpt": p.get("excerpt") or "",
                           "pdpa_risk": p.get("pdpa_risk") or "medium",
                           "named_email": pmail if pmail and not FREE.search(pmail) and not GENERIC.match(pmail) else "",
                           "role_email": pmail if pmail and GENERIC.match(pmail) else "", "phone": p.get("phone") or ""})
        plan.append({"path": path, "record": rec, "organisation_id": oid, "matched": bool(match), "name": name, "email": email, "phone": phone,
                     "people": people})
    summary = {"bodies": len(plan), "matched_existing": sum(1 for p in plan if p["matched"]), "new_organisations": sum(1 for p in plan if not p["matched"]),
               "new_contacts": sum(len(p["people"]) for p in plan),
               "contacts_with_own_email": sum(1 for p in plan for x in p["people"] if x["named_email"]), "skipped": skipped}
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.write_text(json.dumps({"summary": summary, "bodies": [{k: v for k, v in p.items() if k not in ("path", "record")} for p in plan]},
                                  indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    if not args.apply:
        print(f"Preview only: {PREVIEW}")
        return 0
    try:
        con.execute("BEGIN")
        source_ids = {}
        for path in files:
            body = path.read_bytes()
            sid = hid("F", path.relative_to(ROOT).as_posix())
            con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                        (sid, path.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "jsonl", "zlib", zlib.compress(body, 9)))
            source_ids[path] = sid
        for p in plan:
            rec, oid = p["record"], p["organisation_id"]
            record = hid("R", "introducer", args.date, oid)
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source_ids[p["path"]], f"introducer research {p['name']} ({args.date})", json.dumps(rec, ensure_ascii=False)))
            source_url = first(rec.get("sources"), "url") or rec.get("website") or ""
            if not p["matched"]:
                notes = "; ".join(x for x in [f"Members: {rec.get('members')}" if rec.get("members") else "",
                                               f"Channels: " + ", ".join(f"{c.get('what')} ({c.get('url')})" for c in rec.get("channels") or []) if rec.get("channels") else "",
                                               rec.get("notes") or ""] if x)
                address = (rec.get("physical_address") or {}).get("value") if isinstance(rec.get("physical_address"), dict) else (rec.get("physical_address") or "")
                postal = (rec.get("postal_address") or {}).get("value") if isinstance(rec.get("postal_address"), dict) else (rec.get("postal_address") or "")
                con.execute("""INSERT INTO organisations (organisation_id, name, segment, priority, campus, size_evidence, address, education_angle, source_url,
                               verification, email, phone, website, notes, locality) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (oid, p["name"], f"Introducer: {rec.get('kind') or 'other'}", "", "",
                             f"{rec.get('member_count')} members (as published)" if rec.get("member_count") else "", " / ".join(x for x in [address, postal] if x),
                             "Introducer: could share the staff education benefit with its members", source_url,
                             f"Published by the organisation (search, fetched) {args.date}", p["email"], p["phone"], rec.get("website") or "", notes[:2000],
                             rec.get("area") or ""))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)", (oid, record, oid, record))
            for x in p["people"]:
                verification = f"Published by the organisation (search, fetched) {args.date}; pdpa_risk {x['pdpa_risk']}; decision-maker yes"
                con.execute("INSERT OR IGNORE INTO contacts (contact_id, organisation_id, name, role, campus, source_url, verification, shared_email, organisation_phone, "
                            "contact_route, published_role_email, role_phone, named_email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (x["contact_id"], oid, x["name"], x["role"], "", x["source_url"], verification, "" if x["named_email"] else p["email"],
                             p["phone"], "named_email" if x["named_email"] else ("published_role_email" if x["role_email"] else "shared_email"),
                             x["role_email"], x["phone"], x["named_email"]))
                con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'contact', ?, ? WHERE NOT EXISTS "
                            "(SELECT 1 FROM entity_sources WHERE entity_type='contact' AND entity_id=? AND record_id=?)",
                            (x["contact_id"], record, x["contact_id"], record))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    print("Applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
