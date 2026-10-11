#!/usr/bin/env python3
"""Apply the reviewed employer corrections (data/reference/employer-corrections.json) to the company master's outreach plans.

- segment: every plan of the organisation is filed under the right kind of employer (Corporate or Healthcare employers instead of
  Tourism employers). The drafts take the new segment the next time draft_master_messages.py runs. The organisation record is
  unchanged unless the entry also names 'organisation_segment' (added 2026-10-11): then the record's own segment is corrected, the
  earlier value kept as the fact segment_before_correction (source record: this file's entry) with a 'Segment corrected' review item.
- fields (added 2026-10-11): 'website' and/or 'phone' replace the record's value; the earlier value is kept as the fact
  <field>_before_correction with a '<Field> corrected' review item. Any entry may also carry 'review_kind' and 'review' (a review item
  only, for example a domain now parked or a name that may be out of date); action 'review' does nothing else.
- hold: every plan of the organisation is held (review_status 'Needs research') with the note "Outside the Arusha-Kilimanjaro catchment
  or not an employer: <reason>", which the contact merge treats as a blocker, so a new route does not release it.
Preview by default; --apply in one transaction. Re-running changes nothing. Afterwards run draft_master_messages.py,
refresh_acquisition_metadata.py, assign_message_variants.py --apply, export_master_workbook_data.py, npm run build:workbook and verify_master.py.
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
CORRECTIONS = ROOT / "data" / "reference" / "employer-corrections.json"
NOTE = "Outside the Arusha-Kilimanjaro catchment or not an employer: {reason} (data/reference/employer-corrections.json)."
NOTE_RE = re.compile(r"\s*Outside the Arusha-Kilimanjaro catchment or not an employer: .*?\(data/reference/employer-corrections\.json\)\.;?")


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    corrections = json.loads(CORRECTIONS.read_text(encoding="utf-8"))["organisations"]
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    changes = []
    for oid, c in corrections.items():
        if c["action"] not in ("segment", "hold"):
            continue  # 'fields' and 'review' entries leave the plans alone
        for p in con.execute("SELECT message_id, segment, review_status, missing_information, selection FROM outreach_plans WHERE organisation_id=?", (oid,)):
            missing = NOTE_RE.sub("", p["missing_information"] or "").strip("; ").strip()
            segment, status = p["segment"], p["review_status"]
            if c["action"] == "segment":
                segment = c["segment"]
            else:
                note = NOTE.format(reason=c["reason"])
                missing = f"{missing}; {note}" if missing else note
                status = "Needs research"
            if (segment, status, missing) != (p["segment"], p["review_status"], p["missing_information"] or ""):
                changes.append((segment, status, missing, p["message_id"], c["name"], c["action"], p["selection"]))
    # A segment entry may also correct the organisation record's own segment ('organisation_segment', added 2026-10-11).
    org_changes = []
    for oid, c in corrections.items():
        row = con.execute("SELECT segment FROM organisations WHERE organisation_id=?", (oid,)).fetchone()
        if c["action"] == "segment" and c.get("organisation_segment") and row and row["segment"] != c["organisation_segment"]:
            org_changes.append((oid, c, row["segment"] or ""))
    # Field corrections ('website', 'phone', added 2026-10-11): the reviewed value replaces the record's, the earlier value is kept as the
    # fact <field>_before_correction with a '<Field> corrected' review item. A 'review' entry adds its review item only.
    field_changes, review_items = [], []
    for oid, c in corrections.items():
        row = con.execute("SELECT website, phone FROM organisations WHERE organisation_id=?", (oid,)).fetchone()
        for field in ("website", "phone"):
            if row and c.get(field) and (row[field] or "") != c[field]:
                field_changes.append((oid, c, field, row[field] or ""))
        if row and c.get("review"):
            review_items.append((oid, c))
    summary_fields = {"fields_corrected": len(field_changes), "review_items": len(review_items)}
    summary = {"organisations": len(corrections), "plans_changed": len(changes), "organisation_segments_corrected": len(org_changes),
               "chosen_plans_held": sum(1 for x in changes if x[5] == "hold" and x[6] == "Candidate for review"),
               "chosen_plans_refiled": sum(1 for x in changes if x[5] == "segment" and x[6] == "Candidate for review"), **summary_fields}
    print(json.dumps(summary, indent=1))
    if not args.apply:
        print("Preview only.")
        return 0
    try:
        con.execute("BEGIN")
        for segment, status, missing, mid, *_ in changes:
            con.execute("UPDATE outreach_plans SET segment=?, review_status=?, missing_information=? WHERE message_id=?", (segment, status, missing, mid))
            if status == "Needs research":
                con.execute("UPDATE campaign_lead_assignments SET eligibility_status='Needs research', next_action='Held: outside the catchment or not an employer' "
                            "WHERE message_id=? AND selection='Candidate for review'", (mid,))
        body = CORRECTIONS.read_bytes()
        sid = hid("F", "reference", CORRECTIONS.name)
        if org_changes or field_changes or review_items:
            con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                        (sid, CORRECTIONS.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "json", "utf-8", body))
        for oid, c, field, before in field_changes:
            record = hid("R", "employer-correction", oid)
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, sid, f"employer correction {oid}", json.dumps(c, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)", (oid, record, oid, record))
            for f, value in ((f"{field}_before_correction", before), (field, c[field])):
                if value:
                    con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                                (hid("X", oid, f, value), "organisation", oid, f, value, record))
            con.execute(f"UPDATE organisations SET {field}=? WHERE organisation_id=?", (c[field], oid))
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", f"employer-correction-{field}", oid), f"{field.capitalize()} corrected", oid, "", field, f"{before} -> {c[field]}",
                         f"{c.get('field_reason', c['reason'])} ({c.get('field_source', c['source'])}; data/reference/employer-corrections.json). "
                         f"The earlier value is kept as the fact {field}_before_correction."))
        for oid, c in review_items:
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "employer-correction-review", oid, c["review_kind"]), c["review_kind"], oid, "", c.get("review_field", ""),
                         c["review"][:900], f"{c.get('review_action', 'Check and correct through the update skill.')} ({c['source']})"))
        for oid, c, before in org_changes:
            record = hid("R", "employer-correction", oid)
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, sid, f"employer correction {oid}", json.dumps(c, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)", (oid, record, oid, record))
            for field, value in (("segment_before_correction", before), ("segment", c["organisation_segment"])):
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", oid, field, value), "organisation", oid, field, value, record))
            con.execute("UPDATE organisations SET segment=? WHERE organisation_id=?", (c["organisation_segment"], oid))
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "employer-correction-segment", oid), "Segment corrected", oid, "", "segment", f"{before} -> {c['organisation_segment']}",
                         f"{c['reason']} ({c['source']}; data/reference/employer-corrections.json). The earlier segment is kept as the fact "
                         "segment_before_correction."))
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
