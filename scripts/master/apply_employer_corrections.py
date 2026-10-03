#!/usr/bin/env python3
"""Apply the reviewed employer corrections (data/reference/employer-corrections.json) to the company master's outreach plans.

- segment: every plan of the organisation is filed under the right kind of employer (Corporate or Healthcare employers instead of
  Tourism employers). The organisation record is unchanged; the drafts take the new segment the next time draft_master_messages.py runs.
- hold: every plan of the organisation is held (review_status 'Needs research') with the note "Outside the Arusha-Kilimanjaro catchment
  or not an employer: <reason>", which the contact merge treats as a blocker, so a new route does not release it.
Preview by default; --apply in one transaction. Re-running changes nothing. Afterwards run draft_master_messages.py,
refresh_acquisition_metadata.py, assign_message_variants.py --apply, export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
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
    summary = {"organisations": len(corrections), "plans_changed": len(changes),
               "chosen_plans_held": sum(1 for x in changes if x[5] == "hold" and x[6] == "Candidate for review"),
               "chosen_plans_refiled": sum(1 for x in changes if x[5] == "segment" and x[6] == "Candidate for review")}
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
