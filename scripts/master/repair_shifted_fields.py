#!/usr/bin/env python3
"""Repair organisation records in the company master whose contact fields were imported one column out of place.

Some TATO-directory rows reached the master shifted: the website field holds the phone number, the email field holds the
website, and the phone field holds the directory's membership code ('TO/DMC/TREK/MAIN', 'AFF/FIN'). Such a record has no
usable website, so the exporter cannot tell that the company's inbox is on its own domain, and the contact merge (which
never overwrites) sends any found website to review instead of filling it.

The repair only moves values the record already holds into the right field; it infers nothing:
- a website field holding a phone number or a directory code is cleared, and the number moves to the phone field when that
  field is empty or holds only a code;
- an email field holding a website (no '@') is cleared, and the website moves to the website field when that field had no
  website;
- a phone field holding only a directory code is cleared.
Every earlier value is kept as a fact ('previous_<field>') with a source record, and each repaired organisation gets a review
item listing the change. A later contact merge can then fill an empty website from research.

Default: preview (runtime/master/shifted-fields-preview.json). --apply: one transaction. Re-running changes nothing.
Afterwards run export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
PREVIEW = ROOT / "runtime" / "master" / "shifted-fields-preview.json"
DOMAIN = re.compile(r"(?:https?://)?(?:www\.)?[a-z0-9\-]+(?:\.[a-z0-9\-]+)*\.[a-z]{2,}(?:/\S*)?$", re.I)
CODE = re.compile(r"^\s*(?:(?:TO|DMC|TREK|MAIN|AFF|FIN|AUTO|NGO|HOT|HOTEL|LODGE|CAMP|ASSOC)\s*/?\s*)+$", re.I)
JUNK_SITE = re.compile(r"under construction|view details", re.I)


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def phone_like(value: str) -> bool:
    text = str(value or "")
    return len(re.sub(r"\D", "", text)) >= 9 and not re.search(r"[a-z]{3,}", text, re.I)


def repair(website: str, email: str, phone: str) -> dict:
    """The corrected fields (only those that change)."""
    web, em, ph = (str(v or "").strip() for v in (website, email, phone))
    new = {}
    web_bad = bool(web) and (phone_like(web) or CODE.match(web) or JUNK_SITE.search(web)) and not re.search(r"\.[a-z]{2,}", web, re.I)
    email_is_site = bool(em) and "@" not in em and DOMAIN.match(em.split()[0])
    phone_is_code = bool(ph) and bool(CODE.match(ph))
    if web_bad:
        new["website"] = em.split()[0] if email_is_site else ""
        if phone_like(web) and (not ph or phone_is_code):
            new["phone"] = web
    elif email_is_site and not web:
        new["website"] = em.split()[0]
    if email_is_site:
        new["email"] = ""
    if phone_is_code and "phone" not in new:
        new["phone"] = ""
    return {k: v for k, v in new.items() if v != {"website": web, "email": em, "phone": ph}[k]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    changes = []
    for o in con.execute("SELECT organisation_id, name, website, email, phone FROM organisations ORDER BY organisation_id"):
        new = repair(o["website"], o["email"], o["phone"])
        if new:
            changes.append({"organisation_id": o["organisation_id"], "name": o["name"],
                            "before": {k: o[k] or "" for k in new}, "after": new})
    if not args.apply:
        PREVIEW.parent.mkdir(parents=True, exist_ok=True)
        PREVIEW.write_text(json.dumps({"organisations": len(changes), "changes": changes}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"organisations_to_repair": len(changes)}, indent=1))
        print(f"Preview only: {PREVIEW}")
        return 0
    today = date.today().isoformat()
    try:
        con.execute("BEGIN")
        source = hid("F", "shifted-fields", today)
        payload = json.dumps(changes, ensure_ascii=False).encode()
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (source, f"scripts/master/repair_shifted_fields.py ({today})", hashlib.sha256(payload).hexdigest(), len(payload), "json", "utf-8", payload))
        for ch in changes:
            oid = ch["organisation_id"]
            record = hid("R", "shifted-fields", today, oid)
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source, f"organisation {oid}: contact fields repaired", json.dumps(ch, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", (oid, record))
            for field, value in ch["after"].items():
                old = ch["before"][field]
                con.execute(f"UPDATE organisations SET {field}=? WHERE organisation_id=?", (value, oid))
                if old:
                    con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                                (hid("X", oid, f"previous_{field}", old), "organisation", oid, f"previous_{field}", old, record))
            summary = "; ".join(f"{k}: '{ch['before'][k]}' -> '{v}'" for k, v in ch["after"].items())
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "shifted-fields", oid), "Contact fields repaired (imported one column out of place)", oid, "", "website; email; phone",
                         summary[:400], "Values were moved to the right field; the earlier values are kept as facts. Check the website and phone."))
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    print(json.dumps({"organisations_repaired": len(changes)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
