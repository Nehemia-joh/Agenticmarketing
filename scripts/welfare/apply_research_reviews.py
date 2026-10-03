#!/usr/bin/env python3
"""Turn research agents' hold reviews into reviewed decisions in a welfare run's links.json.

A check agent (for example slice V, 3 October 2026) adds to an organisation record a field
  "review": {"flags_still_hold": [...], "flags_no_longer_hold": [...], "official_personal_inbox": true|false, "basis": "...", "source_url": "..."}
This script lists those reviews and, with --apply, writes them into data/runs/<run-id>/links.json:
- flags_cleared[<organisation>] = {"flags": <the words of the flags that no longer hold>, "basis": ..., "source_url": ...}
  (consolidate_research.py drops those red flags);
- official_personal_inboxes[<organisation>] = {"address": <the organisation's personal-domain inbox>, "basis": ..., "source_url": ...}
  (draft_run_messages.py releases the draft only for that exact address).
A review is used only when it gives a basis and a fetched source URL. A flag that still holds, or one the review does not name, stays.
Then run scripts/welfare/run_pipeline.py --run-id <run-id> --rebuild-db.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import welfare_lib as W

PERSONAL = re.compile(r"@(gmail|yahoo|ymail|hotmail|outlook|live|icloud|aol|rocketmail)\.", re.I)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--date", required=True, help="the research files' date (research_*_<date>.jsonl)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    links_path = W.ROOT / "data" / "runs" / args.run_id / "links.json"
    links = json.loads(links_path.read_text(encoding="utf-8"))
    cleared, inboxes, skipped = {}, {}, []
    for path in sorted((W.ROOT / "data" / "raw" / "welfare-research").glob(f"research_*_{args.date}.jsonl")):
        for rec in W.read_jsonl(path):
            review = rec.get("review") if rec.get("record_type") == "organisation" else None
            if not isinstance(review, dict):
                continue
            name, basis, url = rec.get("organisation_name"), (review.get("basis") or "").strip(), (review.get("source_url") or "").strip()
            if not (name and basis and url.startswith("http")):
                skipped.append(f"{name}: no basis or fetched source")
                continue
            gone = [str(f).strip() for f in W.as_list(review.get("flags_no_longer_hold")) if str(f).strip()]
            if gone:
                cleared[name] = {"flags": gone, "basis": basis, "source_url": url, "decided_on": args.date}
            if review.get("official_personal_inbox") is True and re.search(r"supporter|funder'?s own|not the home'?s own|belongs to", basis, re.I):
                skipped.append(f"{name}: the personal inbox belongs to a supporter or funder, not the organisation")
            elif review.get("official_personal_inbox") is True:
                personal = [e for e in W.as_list(rec.get("public_emails")) if PERSONAL.search(str(e))]
                if personal:
                    inboxes[name] = {"address": str(personal[0]).lower(), "basis": basis, "source_url": url, "decided_on": args.date}
                else:
                    skipped.append(f"{name}: inbox marked official but no personal-domain address in the record")
    print(json.dumps({"flags_cleared": len(cleared), "official_personal_inboxes": len(inboxes), "skipped": skipped}, indent=1, ensure_ascii=False))
    for name, entry in list(cleared.items())[:10]:
        print(f"  clear {name}: {entry['flags']} ({entry['basis'][:90]})")
    if not args.apply:
        print("Preview only.")
        return 0
    links.setdefault("flags_cleared", {}).update(cleared)
    links.setdefault("official_personal_inboxes", {}).update(inboxes)
    links_path.write_text(json.dumps(links, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Written to {links_path.relative_to(W.ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
