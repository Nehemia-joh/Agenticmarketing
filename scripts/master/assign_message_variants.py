#!/usr/bin/env python3
"""Record which first-message variant each company in the master gets, and store the variant drafts.

- A (sponsorship of students, any size): only for companies whose published giving funds education (strong fit in
  data/reference/employer-sponsorship-reasons.json).
- B (a partnership on an education benefit for the children of staff): every other company. It is the catch-all: a company in
  the reasons file gets the personalised B draft; every other company keeps the staff-benefit request already held in its plan.
- n/a: savings groups, which get their own request to the committee.
A duplicate record held by scripts/master/resolve_master_recipients.py takes the variant of the record it duplicates.

Writes to outreach_plans (columns added on first use): message_variant, variant_reason, and for the companies in the reasons file
variant_subject and variant_body. The draft is stored on the plan of its addressee (the verified named decision-maker, else the
company's own plan), and that plan becomes the company's chosen recipient (resolve_master_recipients.py keeps a plan that holds
a variant draft). The earlier message text is unchanged.

Preview by default; --apply for one transaction, then the recipient selection is re-run. Re-running changes nothing. Afterwards run
draft_employer_sponsorship.py, export_master_workbook_data.py, npm run build:workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
import draft_employer_sponsorship as D  # noqa: E402  (the rule: variant_for; the drafts)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
DEFAULT_B = "B: a partnership on an education benefit for staff (the catch-all). No published education giving on record."
NOT_APPLICABLE = "n/a: a savings group, which gets its own request to the committee."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    reasons = json.loads(D.REASONS.read_text(encoding="utf-8"))["organisations"]
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    primary_of = {r[0]: r[1] for r in con.execute("SELECT entity_id, related_id FROM review WHERE kind LIKE 'Duplicate organisation%' OR kind LIKE 'Shared inbox%'")}
    rows, issues = D.build_drafts(con)
    if issues:
        print("\n".join(issues))
        raise SystemExit("Draft checks failed; nothing written.")
    drafts = {r["oid"]: r for r in rows if r["fit"] != "hold"}

    def decide(oid: str, segment: str) -> tuple[str, str]:
        if segment == "SACCOS members":
            return "n/a", NOT_APPLICABLE
        if segment == "Introducers":
            return "introducer", "Introducer: a partnership so that the body shares the staff education benefit with its members."
        source = oid if oid in reasons else primary_of.get(oid)
        reason = reasons.get(source) if source else None
        if not reason or reason["fit"] == "hold":
            return "B", DEFAULT_B
        clause = reason["clause"]
        if D.variant_for(reason["fit"]) == "A":
            return "A", f"A: sponsorship of students. Strong fit: the company {clause}."
        return "B", f"B: a partnership on an education benefit for staff. {reason['fit'].capitalize()} fit, so not a sponsorship ask: the company {clause}."

    plans = [dict(r) for r in con.execute("SELECT message_id, organisation_id, target_type, target_id, segment FROM outreach_plans")]
    chosen = {p["message_id"]: decide(p["organisation_id"], p["segment"]) for p in plans}
    # The plan that holds each variant draft: the addressee's plan, else the company's own.
    host = {}
    for oid, r in drafts.items():
        mine = [p for p in plans if p["organisation_id"] == oid]
        addressee_plan = [p for p in mine if r["contact_id"] and p["target_type"] == "contact" and p["target_id"] == r["contact_id"]]
        company_plan = [p for p in mine if p["target_type"] == "organisation"]
        host[oid] = (addressee_plan or company_plan)[0]["message_id"]
    print(json.dumps({"plans": dict(Counter(v for v, _ in chosen.values())), "drafts_stored_on": len(host)}))
    if not args.apply:
        print("Preview only.")
        return 0
    try:
        con.execute("BEGIN")
        columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
        for column in ("message_variant", "variant_reason", "variant_subject", "variant_body"):
            if column not in columns:
                con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
        for mid, (variant, why) in chosen.items():
            con.execute("UPDATE outreach_plans SET message_variant=?, variant_reason=?, variant_subject='', variant_body='' WHERE message_id=?", (variant, why, mid))
        for oid, mid in host.items():
            r = drafts[oid]
            con.execute("UPDATE outreach_plans SET variant_subject=?, variant_body=?, variant_reason=variant_reason||? WHERE message_id=?",
                        (r["subjects"][r["arm"]], r["bodies"][r["arm"]], f" Draft stored in variant_subject and variant_body; source {r['source']} (read {r['read']}).", mid))
        if con.execute("PRAGMA foreign_key_check").fetchall() or con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("integrity check failed")
        if con.execute("SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(message_variant,'')=''").fetchone()[0]:
            raise RuntimeError("a plan has no variant")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    con.close()
    subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "master" / "resolve_master_recipients.py"), "--database", str(args.database), "--apply"], check=True)
    print("Applied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
