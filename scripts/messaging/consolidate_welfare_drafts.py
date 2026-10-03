#!/usr/bin/env python3
"""Consolidate the welfare run's first messages into one review file.

Reads the run database (outputs/runs/<run-id>/lead-database.sqlite, read-only) and writes
outputs/messages/Silverleaf Welfare Drafts - <date>.md:
- funders (sponsorship request): ready, then held, each with the sourced relationship that is the reason for the ask;
- homes, programmes, specialised centres and other child-focused NGOs (partnership on the children's education): ready, then held.
Each entry shows the recipient, the route, the status and, for a held draft, why. Follow-up messages (the partner rate) are in the run
workbook. Nothing is sent. Run draft_run_messages.py --track welfare first.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from datetime import date

import offer_lib as L

ROOT = L.ROOT
BOILERPLATE = re.compile(r"^(The first message is a request|Finance must confirm)")


def reasons_held(missing: str) -> list[str]:
    out = []
    for part in re.split(r";\s+(?=[A-Z])", missing or ""):
        part = part.strip()
        if part and not BOILERPLATE.search(part):
            out.append(part if len(part) <= 260 else part[:257] + "...")
    return out


def entry(n: str, r: dict) -> list[str]:
    lines = [f"### {n} {L.display_name(r['org_name'], r['organisation_id'])}: {r['subtype'] or r['segment']} ({(r.get('priority') or 'Low').lower()} priority)", "",
             f"- To: {r['recipient']} | Route: {r['route_value'] or 'none recorded'} ({r['contact_route'] or 'no route'}) | Plan: {r['message_id']} | Status: {r['review_status']}"]
    if r["hook_source_url"]:
        weak = " **The source is a ProPublica search page: open the filing and confirm the grant before sending.**" if "full_text_search" in r["hook_source_url"] else ""
        lines.append(f"- Reason for the ask: {r['relevance_reason'].split('; supports ')[-1].split(';')[0]} (source {r['hook_source_url']}, read {r['hook_verified_on']}).{weak}")
    held = reasons_held(r["missing_information"]) if r["review_status"] != "draft_ready" else []
    if held:
        lines.append("- **Held:** " + " ".join(held))
    return lines + ["", f"Subject: {r['subject']}", "", "```", r["body"], "```", ""]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", default="arusha-welfare-2026-09")
    args = parser.parse_args()
    db = ROOT / "outputs" / "runs" / args.run_id / "lead-database.sqlite"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(
        "SELECT p.*, o.name AS org_name, o.segment, o.subtype, o.priority, m.body, m.subject AS msg_subject FROM outreach_plans p JOIN organisations o USING(organisation_id) "
        "JOIN messages m ON m.message_id = p.message_id WHERE p.target_type='organisation' "
        "ORDER BY CASE o.priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, o.segment, o.name")]
    for r in rows:
        r["subject"] = r["msg_subject"]
    funders = [r for r in rows if r["segment"] == "Welfare funder"]
    networks = [r for r in rows if str(r["segment"]).startswith("Welfare network")]
    homes = [r for r in rows if r["segment"] == "Welfare residential care"]
    programmes = [r for r in rows if r["segment"] == "Welfare family-based programme"]
    centres = [r for r in rows if r["segment"] == "Welfare specialised centre"]
    others = [r for r in rows if r not in funders + networks + homes + programmes + centres]  # anything not yet classified
    groups = [("Funders: sponsorship request", funders),
              ("Children's homes and orphanages: partnership on the education of the children in their care", homes),
              ("Family-based and sponsorship programmes: partnership on the education of the children in the programme", programmes),
              ("Specialised centres (disability, street children, rescue): partnership, after confirming Silverleaf can meet the children's needs", centres)]
    if others:
        groups.append(("Other child-focused organisations, not yet classified", others))
    if networks:
        groups.append(("Introducer networks: share the partnership with member homes", networks))
    today = date.today().isoformat()
    ready = lambda xs: [r for r in xs if r["review_status"] == "draft_ready"]  # noqa: E731
    lines = [f"# Welfare drafts, {today}: every organisation's first message", "",
             "Review copy only: nothing is sent. One first message per organisation.", "",
             f"- **Funders ({len(funders)}).** A request to sponsor students: any size, including textbooks, transport or meals. The reason is a relationship the "
             f"run verified from the funder's own pages (it funds a named home or programme). A funder with no verified relationship is held, because there is no honest "
             f"reason to ask it yet. {len(ready(funders))} are ready.",
             f"- **Children's homes and orphanages ({len(homes)}),** where children live in the home's care. {len(ready(homes))} are ready.",
             f"- **Family-based and sponsorship programmes ({len(programmes)}),** which support children who live with families, often paying school fees. "
             f"{len(ready(programmes))} are ready.",
             f"- **Specialised centres ({len(centres)}):** disability and rehabilitation centres, street-children centres and safe houses. {len(ready(centres))} are ready.",
             "- Homes, programmes and centres all get the same first message: a partnership on the education of the children in their care, and a short meeting. No "
             "offer terms; the partner rate follows in the second message.",
             f"- **Introducer networks ({len(networks)})**: bodies that could share the partnership with many homes. {len(ready(networks))} are ready." if networks else "",
             "- A draft is held when the organisation has no published route, its only route is outside Tanzania, its email domain is outside Tanzania, the record carries "
             "red flags, the inbox is on a personal domain, the centre is specialised (confirm Silverleaf can meet the children's needs first) or the location is unresolved.",
             "- Parent-enquiry replies are separate and held for the data-protection owner; they are not in this file.", "",
             "Follow-up messages and the offer terms are in the run workbook. Companies are in the Employer Drafts file.", "", "---", ""]
    for gi, (title, group) in enumerate(groups, 1):
        lines += [f"# {gi}. {title}", ""]
        for label, subset in (("ready for review", ready(group)), ("held", [r for r in group if r["review_status"] != "draft_ready"])):
            lines += [f"## {gi}.{1 if label == 'ready for review' else 2} {label.capitalize()} ({len(subset)})", ""]
            for i, r in enumerate(subset, 1):
                lines += entry(f"{gi}.{1 if label == 'ready for review' else 2}.{i}", r)
        lines += ["---", ""]
    out = ROOT / "outputs" / "messages" / f"Silverleaf Welfare Drafts - {today}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} organisations ({len(ready(rows))} ready): {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
