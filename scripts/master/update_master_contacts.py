#!/usr/bin/env python3
"""Apply a contact-research wave to people the company master already holds.

merge_master_contacts.py inserts the new people a wave finds and skips everyone already on file, so a wave that re-reads
a known person's own page (finding their published work email, their current title, or simply confirming them) had no
way into the master. This script is that way, following silverleaf-update-lead-list: it reads the wave's research records
(data/raw/contact-research/search_*_<date>.jsonl and browser_*_<date>.jsonl, the agent-brief format), matches each
person to a contact of the same organisation (same normalised name, or the same person written two ways), and:
- fills an empty work email (named_email) or direct phone (role_phone), only when the same fetched source links it to that
  person and the address is not on a free-mail domain;
- replaces a role that names no role ('Contact person ...', 'role not stated', 'Named on ... (no job title given)') with
  the title the source gives; any other differing title becomes a review item, never an overwrite;
- notes 'role confirmed <date> (<url>)' on the contact when the person was read on a fetched page, and releases drafts
  held only because hook research could not confirm the role;
- points the person's draft at their newly found work email when the draft had no email route.
Only people a research agent recorded with identity confirmed and fetched: true are used; snippets change nothing.
Every change is recorded as a fact with its source record. Nothing is deleted.

Default: preview (runtime/master/contact-update-preview.json). --apply: one transaction with integrity checks.
Afterwards run resolve_master_recipients.py, export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import zlib
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
import contact_lib as C  # noqa: E402
from apply_hook_research import ROLE_NOTE, release  # noqa: E402  (the same role hold and release as hook research)

W = C.W
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
PREVIEW = ROOT / "runtime" / "master" / "contact-update-preview.json"
PLACEHOLDER_ROLE = re.compile(r"^\s*$|contact person|role not stated|no job title|^named on|booking contact|^contact\b", re.I)


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def files_for(run_date: str) -> list[Path]:
    raw = ROOT / "data" / "raw" / "contact-research"
    return sorted(raw.glob(f"search_*_{run_date}.jsonl")) + sorted(raw.glob(f"browser_*_{run_date}.jsonl"))


def plain(text) -> str:
    return " ".join(str(text or "").split())


def same(a: str, b: str) -> bool:
    return W.name_key(a) == W.name_key(b) or C.same_person(a, b)


def plan_updates(con, files: list[Path]) -> tuple[list[dict], Counter]:
    con.row_factory = sqlite3.Row
    contacts = {}
    for c in con.execute("SELECT * FROM contacts"):
        contacts.setdefault(c["organisation_id"], []).append(dict(c))
    known = {r[0] for r in con.execute("SELECT organisation_id FROM organisations")}
    out, stats = [], Counter()
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            oid = r.get("organisation_id")
            if r.get("db") != "master" or oid not in known or r.get("identity") == "uncertain":
                continue
            for p in r.get("people") or []:
                if not p.get("fetched") or not p.get("name"):
                    stats["people not fetched or unnamed (skipped)"] += 1
                    continue
                match = [c for c in contacts.get(oid, []) if same(c["name"] or "", p["name"])]
                if len(match) != 1:
                    stats["new people (left to merge_master_contacts.py)" if not match else "ambiguous matches (skipped)"] += 1
                    continue
                c = match[0]
                email = C.clean_email(str(p.get("email") or ""))
                if email and W.PERSONAL_EMAIL.search(email):
                    email = ""
                phone = W.norm_phone(str(p.get("phone") or "")) if p.get("phone") else ""
                role = plain(p.get("role"))
                change = {"file": path.name, "organisation_id": oid, "contact_id": c["contact_id"], "name": c["name"], "source_url": p.get("source_url", ""),
                          "accessed_on": next((s.get("accessed_on") for s in r.get("sources") or [] if s.get("accessed_on")), "") or "",
                          "excerpt": plain(p.get("excerpt"))[:300], "set": {}, "review": ""}
                if email and not (c["named_email"] or "").strip():
                    change["set"]["named_email"] = email
                if phone and not (c["role_phone"] or "").strip():
                    change["set"]["role_phone"] = phone
                held, found = plain(c["role"]).lower(), role.lower()
                # 'Managing Director' on record and 'Managing Director, Bushbuck Safaris Ltd' on the page are the same role.
                if role and held != found and not (held and (held in found or found in held)):
                    if PLACEHOLDER_ROLE.search(c["role"] or ""):
                        change["set"]["role"] = role
                    else:
                        change["review"] = f"{c['name']}: on record '{c['role']}' | source now '{role}' | {p.get('source_url', '')}"
                out.append(change)
                stats["people matched"] += 1
    return out, stats


def apply(con, files: list[Path], changes: list[dict], run_date: str, stats: Counter) -> None:
    source_ids = {}
    for path in files:
        body = path.read_bytes()
        sid = hid("F", "contact-research", path.name)  # the same id the contact merge gives the file
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (sid, path.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "jsonl", "zlib", zlib.compress(body, 9)))
        source_ids[path.name] = sid
    for ch in changes:
        cid, day = ch["contact_id"], ch["accessed_on"] or run_date
        record = hid("R", "contact-update", run_date, cid)
        con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                    (record, source_ids[ch["file"]], ch["source_url"] or f"contact {cid}", json.dumps(ch, ensure_ascii=False)))
        con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'contact',?,? WHERE NOT EXISTS "
                    "(SELECT 1 FROM entity_sources WHERE entity_type='contact' AND entity_id=? AND record_id=?)", (cid, record, cid, record))
        before = dict(con.execute("SELECT role, named_email, role_phone FROM contacts WHERE contact_id=?", (cid,)).fetchone())
        for field, value in ch["set"].items():
            con.execute(f"UPDATE contacts SET {field}=? WHERE contact_id=?", (value, cid))
            con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                        (hid("X", cid, field, value), "contact", cid, field, value, record))
            if field == "role" and before["role"]:
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", cid, "previous_role", before["role"]), "contact", cid, "previous_role", before["role"], record))
            stats[f"{field} filled"] += 1
        if ch["set"].get("named_email"):
            con.execute("UPDATE contacts SET contact_route='named_email' WHERE contact_id=?", (cid,))
            # The person's own draft goes to the address the source gives them when it had no email route.
            for mid, channel in con.execute("SELECT message_id, contact_channel FROM outreach_plans WHERE target_type='contact' AND target_id=?",
                                            (cid,)).fetchall():
                if "@" not in str(channel or ""):
                    new = "; ".join(x for x in (ch["set"]["named_email"], plain(channel)) if x)
                    con.execute("UPDATE outreach_plans SET contact_channel=?, channel_attribution=? WHERE message_id=?",
                                (new, f"Work email published with the person's name ({ch['source_url']})", mid))
                    stats["plans pointed at a new work email"] += 1
        note = f"role confirmed {day} ({ch['source_url']})"
        if ch["source_url"] and not ch["review"]:  # a differing title is not a confirmation
            con.execute("UPDATE contacts SET verification = COALESCE(verification,'') || ? WHERE contact_id=? AND COALESCE(verification,'') NOT LIKE ?",
                        (f"; {note}", cid, f"%{note}%"))
            stats["roles confirmed"] += 1
            role_now, verification = con.execute("SELECT role, verification FROM contacts WHERE contact_id=?", (cid,)).fetchone()
            for mid, recipient_role in con.execute("SELECT message_id, recipient_role FROM outreach_plans WHERE target_type='contact' AND target_id=?",
                                                   (cid,)).fetchall():
                if recipient_role != role_now and PLACEHOLDER_ROLE.search(recipient_role or ""):
                    con.execute("UPDATE outreach_plans SET recipient_role=? WHERE message_id=?", (role_now, mid))
                    stats["plan recipient roles updated"] += 1
            if C.DECISION.search(role_now or "") and "decision-maker no" in (verification or ""):
                # A placeholder role ('Contact person ...') had been recorded as 'decision-maker no'; the confirmed title decides now.
                con.execute("UPDATE contacts SET verification = REPLACE(verification, 'decision-maker no', 'decision-maker yes') WHERE contact_id=?", (cid,))
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", cid, "decision_maker", "true"), "contact", cid, "decision_maker", "true", record))
                stats["decision-maker flags corrected"] += 1
            for (mid,) in con.execute("SELECT message_id FROM outreach_plans WHERE target_type='contact' AND target_id=? AND missing_information LIKE ?",
                                      (cid, f"%{ROLE_NOTE}%")).fetchall():
                release(con, mid, stats)
        if ch["review"]:
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "contact-update-role", cid), "Contact research: role differs", ch["organisation_id"], cid, "role", ch["review"][:400],
                         "A newer source gives this person another title. Confirm the current title and update the contact through the update skill."))
            stats["role differences sent to review"] += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="the research wave's date (file suffix)")
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true", help="write the changes in one transaction")
    args = parser.parse_args()
    files = files_for(args.date)
    if not files:
        raise SystemExit(f"No research files for {args.date}.")
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    changes, stats = plan_updates(con, files)
    if not args.apply:
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        PREVIEW.write_text(json.dumps({"date": args.date, "stats": dict(stats), "changes": changes}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(dict(stats), indent=1))
        print(f"Preview only: {PREVIEW}")
        return 0
    try:
        con.execute("BEGIN")
        apply(con, files, changes, args.date, stats)
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fks:
            raise RuntimeError({"integrity": integrity, "foreign_keys": [tuple(f) for f in fks[:5]]})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    print(json.dumps(dict(stats), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
