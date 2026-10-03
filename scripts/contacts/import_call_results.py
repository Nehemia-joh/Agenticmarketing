#!/usr/bin/env python3
"""Turn a filled-in call sheet (build_call_sheet.py) into contact-research records the normal merge can take.

Reads the "Calls" sheet of the given workbook. A row is used only when the outcome is "reached" and a contact name is given. It becomes one
line of data/raw/contact-research/search_calls_<date>.jsonl in the research agents' format: the person's name and role, their work email and
phone as the person on the phone gave them, the source "tel:<number called>", and an excerpt that records who answered, the caller, the date
and whether they agreed to receive the email. A contact who did not agree is recorded with pdpa_risk "risky", so no draft uses that route.
Then run build_contact_profiles.py --date <date> and merge_master_contacts.py (preflight, then --apply), as for any research wave.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "contact-research"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--date", default=date.today().isoformat(), help="the research date the merge will use")
    parser.add_argument("--welfare", action="store_true", help="a welfare call sheet: write welfare research contact records "
                        "(data/raw/welfare-research/research_K_calls_<date>.jsonl), add its glob to the run's run-config research_files if the date is new, then run the welfare pipeline with --rebuild-db")
    args = parser.parse_args()
    ws = load_workbook(args.workbook, read_only=True, data_only=True)["Calls"]
    rows = ws.iter_rows(values_only=True)
    headers = [str(h or "") for h in next(rows)]
    col = {h.split(" (")[0]: i for i, h in enumerate(headers)}
    out, skipped = [], 0
    for r in rows:
        get = lambda k: str(r[col[k]] or "").strip() if k in col and col[k] < len(r) else ""  # noqa: E731
        if not get("organisation_id"):
            continue
        if not get("outcome").lower().startswith("reached") or not get("contact_name"):
            skipped += 1
            continue
        consent = get("agreed_to_receive_email").lower().startswith("y")
        number = (get("phones").split(",")[0] or "").strip()
        email = get("contact_work_email").lower()
        if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
            email = ""
        excerpt = (f"Phone call on {get('call_date') or args.date} by {get('caller') or 'Silverleaf'}; answered by {get('answered_by_name') or 'the office'}"
                   f"{' (' + get('answered_by_role') + ')' if get('answered_by_role') else ''}; agreed to receive the email: {'yes' if consent else 'no'}.")
        out.append({"db": "master", "organisation_id": get("organisation_id"), "organisation_name": get("organisation"), "status": "found", "identity": "confirmed",
                    "searches_used": 0, "website": "", "emails": [], "phones": [], "postal_address": {}, "physical_address": {}, "socials": [],
                    "people": [{"name": get("contact_name"), "role": get("contact_role") or "staff welfare or benefits contact (by phone)", "email": email,
                                "phone": get("contact_work_phone"), "source_url": f"tel:{number}", "fetched": True, "excerpt": excerpt,
                                "pdpa_risk": "medium" if consent else "risky",
                                "pdpa_risk_reason": "given by the organisation by phone, with agreement to email" if consent else "given by phone without agreement to email"}],
                    "sources": [{"url": f"tel:{number}", "title": "Phone call", "fetched": True, "accessed_on": get("call_date") or args.date, "excerpt": excerpt,
                                 "facts": "staff welfare or benefits contact"}],
                    "notes": f"Method: phone call (call sheet). {get('notes')}".strip()})
    if args.welfare:
        out = [{"record_type": "contact", "slice": "K", "organisation_name": rec["organisation_name"], "contact_name": rec["people"][0]["name"],
                "role": rec["people"][0]["role"], "role_certainty": "confirmed", "emails": [rec["people"][0]["email"]] if rec["people"][0]["email"] else [],
                "email_type": "named" if rec["people"][0]["email"] else "", "phones": [rec["people"][0]["phone"]] if rec["people"][0]["phone"] else [],
                "phone_type": "office", "profile_url": "", "channel_attribution": rec["people"][0]["excerpt"],
                "sources": [{"url": rec["people"][0]["source_url"], "title": "Phone call", "source_date": "", "accessed_on": args.date, "evidence_basis": "phone call",
                             "fetched": True, "facts_supported": ["name", "role", "email"], "evidence_excerpt": rec["people"][0]["excerpt"]}],
                "verification_status": "verified", "pdpa_risk": rec["people"][0]["pdpa_risk"], "pdpa_risk_reason": rec["people"][0]["pdpa_risk_reason"],
                "notes": rec["notes"]} for rec in out]
        path = ROOT / "data" / "raw" / "welfare-research" / f"research_K_calls_{args.date}.jsonl"
    else:
        path = RAW / f"search_calls_{args.date}.jsonl"
    with path.open("a", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps({"rows_used": len(out), "rows_skipped": skipped, "file": str(path)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
