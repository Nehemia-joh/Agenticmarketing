#!/usr/bin/env python3
"""Record the reviewed organisation relations (data/reference/organisation-relations.json) in the company master. Nothing is deleted.

- duplicate (organisation_id is the same organisation as primary, at one site): every source record of the duplicate is also linked
  to the primary (entity_sources), the duplicate's phone and OpenStreetMap ID become facts on the primary ('phone (duplicate record
  <id>)', 'osm_id (duplicate record <id>)') when they differ from its own, a 'Duplicate record: phone conflict' review item names
  both phones (and says when a phone is stored malformed), and the open 'Contact research: possible duplicate' items on the pair are
  closed: kept, relabelled '(closed)', with the decision as the action.
- branch (organisation_id is a branch of related_id at another site): 'borrowed_fields' that the branch holds from the main
  organisation's listing get a 'Branch record holds the main organisation's details' review item, and 'confirm_operating' adds a
  'Confirm the branch still operates' item. The branch keeps its own record and values.
The selection (one message per business, the duplicate or branch review link) is made by resolve_master_recipients.py, which reads
the same file. Preview by default; --apply in one transaction; re-running changes nothing. Afterwards run
resolve_master_recipients.py --apply, the workbook export and build, and verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RELATIONS = ROOT / "data" / "reference" / "organisation-relations.json"
MALFORMED_PHONE = re.compile(r"^\+?255[\s-]*0")  # a country code followed by the trunk 0


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def digits(value) -> str:
    d = re.sub(r"\D", "", str(value or ""))
    return "255" + d[4:] if d.startswith("2550") else d


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    relations = json.loads(RELATIONS.read_text(encoding="utf-8"))["relations"]
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    org = lambda oid: con.execute("SELECT * FROM organisations WHERE organisation_id=?", (oid,)).fetchone()  # noqa: E731
    links, facts, reviews, closed = [], [], [], []
    for i, r in enumerate(relations, 1):
        a, b = org(r["organisation_id"]), org(r["related_id"])
        if a is None or b is None:
            print(f"Refused: relation {i} names an organisation that is not in the master.")
            return 1
        record = hid("R", "organisation-relation", r["kind"], r["organisation_id"], r["related_id"])
        if r["kind"] == "duplicate":
            dup, surv = a, org(r.get("primary") or r["related_id"])
            for (rec,) in con.execute("SELECT DISTINCT record_id FROM entity_sources WHERE entity_type='organisation' AND entity_id=?", (dup["organisation_id"],)):
                links.append((surv["organisation_id"], rec))
            for field in ("phone", "osm_id"):
                value = str(dup[field] or "").strip()
                if not value or (digits(value) == digits(surv[field]) if field == "phone" else value == str(surv[field] or "")):
                    continue
                support = con.execute("SELECT record_id FROM facts WHERE entity_type='organisation' AND entity_id=? AND lower(field)=? AND value=?",
                                      (dup["organisation_id"], field, value)).fetchone()
                facts.append((surv["organisation_id"], f"{field} (duplicate record {dup['organisation_id']})", value, support[0] if support else record))
            if str(dup["phone"] or "").strip() and str(surv["phone"] or "").strip() and digits(dup["phone"]) != digits(surv["phone"]):
                bad = [p for p in (surv["phone"], dup["phone"]) if MALFORMED_PHONE.match(str(p))]
                note = (f" {', '.join(bad)} is stored malformed (the country code 255 followed by the trunk 0); written in full it would read "
                        f"+255 {digits(bad[0])[3:5]} {digits(bad[0])[5:8]} {digits(bad[0])[8:]}." if bad else "")
                reviews.append((hid("D", "relation-phone", surv["organisation_id"], dup["organisation_id"]), "Duplicate record: phone conflict",
                                surv["organisation_id"], dup["organisation_id"], "phone",
                                f"{surv['name']}: {surv['phone']} | {dup['name']}: {dup['phone']}",
                                "Two records of one facility publish different phones (data/reference/organisation-relations.json). Confirm which line "
                                "the facility answers before relying on either; both are kept." + note))
            for rv in con.execute("SELECT review_id FROM review WHERE kind='Contact research: possible duplicate' AND entity_id IN (?,?)",
                                  (dup["organisation_id"], surv["organisation_id"])):
                closed.append((rv["review_id"], f"Closed: {r['decision']} (data/reference/organisation-relations.json)"))
        elif r["kind"] == "branch":
            br, main_org = a, b
            held = [f"{f}: {br[f]}" for f in r.get("borrowed_fields", []) if str(br[f] or "").strip()]
            if held:
                reviews.append((hid("D", "relation-borrowed", br["organisation_id"]), "Branch record holds the main organisation's details",
                                br["organisation_id"], main_org["organisation_id"], "; ".join(r["borrowed_fields"]), "; ".join(held)[:900],
                                f"These values came from {r['borrowed_from']}. They describe {main_org['name']}, not this branch; do not use them "
                                "as the branch's own address or line (data/reference/organisation-relations.json)."))
            if r.get("confirm_operating"):
                reviews.append((hid("D", "relation-operating", br["organisation_id"]), "Confirm the branch still operates",
                                br["organisation_id"], main_org["organisation_id"], "status",
                                f"{br['name']}: a branch of {main_org['name']} known only from OpenStreetMap",
                                f"Call {main_org['name']} on its published line ({main_org['phone'] or 'see its record'}) and ask whether the clinic still "
                                "operates and where; record the answer through the update skill."))
        else:
            print(f"Refused: relation {i} has unknown kind '{r['kind']}'.")
            return 1
    have = {(e, rec) for e, rec in con.execute("SELECT entity_id, record_id FROM entity_sources WHERE entity_type='organisation'")}
    links = sorted({x for x in links if x not in have})
    summary = {"relations": len(relations), "source_links_added": len(links), "facts": len(facts), "reviews": len(reviews),
               "possible_duplicate_items_closed": len(closed)}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(summary, indent=1))
    if not args.apply:
        print("Preview only.")
        return 0
    body = RELATIONS.read_bytes()
    source = hid("F", "reference", RELATIONS.name)
    try:
        con.execute("BEGIN")
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (source, RELATIONS.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "json", "utf-8", body))
        for r in relations:
            record = hid("R", "organisation-relation", r["kind"], r["organisation_id"], r["related_id"])
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source, f"{r['kind']} {r['organisation_id']} -> {r['related_id']}", json.dumps(r, ensure_ascii=False)))
            for oid in (r["organisation_id"], r["related_id"]):
                con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                            "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)", (oid, record, oid, record))
        con.executemany("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('organisation', ?, ?)", links)
        for oid, field, value, rec in facts:
            con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                        (hid("X", oid, field, value), "organisation", oid, field, value, rec))
        con.executemany("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)", reviews)
        for review_id, action in closed:
            con.execute("UPDATE review SET kind='Contact research: possible duplicate (closed)', action=? WHERE review_id=?", (action, review_id))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    print("Applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
