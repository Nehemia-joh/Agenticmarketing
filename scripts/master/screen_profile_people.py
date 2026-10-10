#!/usr/bin/env python3
"""Screen the contact profiles' people for the company master against reviewed exclusions, before the contact merge.

build_contact_profiles.py reads named people from crawled page layouts. A few layouts defeat its person filter: a page
heading read as a name ('Visitor Information' / 'Partner Hotels'), a board list whose second role line was lost (an
association's sector chairs all read as 'CHAIRPERSON', which would make any of them look like the body's elected head),
members listed with their own employers' titles ('Senior HR Manager - SONGAS' on an HR association's page), and a
national body's staff read again on a regional office that shares its website. merge_master_contacts.py would insert
them as contacts of the organisation.

data/reference/employer-people-exclusions.json lists each reviewed case: organisation_id, the name as read (or '*' for
every crawled person of that organisation), the reason, the page and the date decided. This script removes those people
from runtime/contacts/profiles.json (the master's profiles only), so the merge never inserts them; nothing in the
database changes and the raw crawl file is kept as evidence. Only crawled or browser-read people are screened: a
lead built from a search agent's confirmed record is never removed, so an agent can record a screened person with the
role the page actually gives.

Run after build_contact_profiles.py and before merge_master_contacts.py:
  python scripts/master/screen_profile_people.py            # preview: what would be removed
  python scripts/master/screen_profile_people.py --apply    # rewrite runtime/contacts/profiles.json
The report goes to runtime/contacts/people-screen.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import contact_lib as C  # noqa: E402

PROFILES = ROOT / "runtime" / "contacts" / "profiles.json"
EXCLUSIONS = ROOT / "data" / "reference" / "employer-people-exclusions.json"
REPORT = ROOT / "runtime" / "contacts" / "people-screen.json"


def load_exclusions() -> dict:
    out = {}
    for entry in json.loads(EXCLUSIONS.read_text(encoding="utf-8"))["exclusions"]:
        out.setdefault(entry["organisation_id"], []).append(entry)
    return out


def excluded(person: dict, rules: list) -> dict | None:
    """The rule that screens this person out, or None. Only crawled or browser-read people are screened: a lead whose record
    comes from a search agent (who read and confirmed the person and role) is kept."""
    if person.get("method") == "search":
        return None
    for rule in rules:
        if rule["name"] == "*" or C.same_person(rule["name"], person["name"]) or C.W.name_key(rule["name"]) == C.W.name_key(person["name"]):
            return rule
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    data = json.loads(PROFILES.read_text(encoding="utf-8"))
    rules = load_exclusions()
    removed, unmatched = [], []
    used = set()
    for profile in data["profiles"]:
        if profile["db"] != "master" or profile["organisation_id"] not in rules:
            continue
        keep = []
        for person in profile["people"]:
            rule = excluded(person, rules[profile["organisation_id"]])
            if rule and not person.get("already_in_database"):
                removed.append({"organisation_id": profile["organisation_id"], "organisation": profile["name"], "name": person["name"],
                                "role": person["role"], "method": person.get("method"), "reason": rule["reason"]})
                used.add((rule["organisation_id"], rule["name"]))
            else:
                keep.append(person)
        profile["people"] = keep
    for oid, entries in rules.items():
        for rule in entries:
            if (oid, rule["name"]) not in used:
                unmatched.append({"organisation_id": oid, "name": rule["name"]})
    report = {"profiles_date": data.get("date"), "applied": args.apply, "removed": removed, "rules_not_matched": unmatched}
    REPORT.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    if args.apply:
        PROFILES.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(removed)} people {'removed from' if args.apply else 'would be removed from'} {PROFILES.relative_to(ROOT)}; "
          f"{len(unmatched)} exclusion entries matched nobody in this build (kept for later builds). Report: {REPORT.relative_to(ROOT)}")
    for r in removed:
        print(f"  {r['organisation'][:40]} | {r['name']} | {r['role'][:50]} | {r['reason'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
