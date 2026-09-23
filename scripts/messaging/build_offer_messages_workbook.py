#!/usr/bin/env python3
"""Build one review workbook with every offer-aligned draft across the three databases, and re-check them all.

Reads (read-only) the company master, the welfare run and the government run, plus the offer register. Writes
outputs/messages/Silverleaf Offer-Aligned Messages - <date>.xlsx and outputs/messages/offer-messages-summary.json.
Every initial message, follow-up, Kiswahili version and English meaning is checked again with offer_lib.check_message;
the script exits 1 if any draft fails. The company master's consolidated workbook (npm run build:workbook) shows the
master drafts too; this workbook is the one view across all three databases.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import offer_lib as L

ROOT = L.ROOT
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RUNS = {"welfare": "arusha-welfare-2026-09", "government": "arusha-government-2026-09"}
BLUE, WHITE = "002368", "FFFFFF"
WRAP = {"subject", "body", "follow_up_1", "follow_up_2", "offer_message", "lead_brief", "kiswahili_version", "english_meaning", "conditions", "terms",
        "use_note", "restriction",
        "text", "offer", "recipient", "issue"}


def ro(path):
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def add_sheet(wb, title, subtitle, headers, rows, widths=None):
    ws = wb.create_sheet(title)
    ws["A1"], ws["A2"] = title, subtitle
    ws["A1"].font = Font(name="Arial", size=14, bold=True, color=BLUE)
    ws["A2"].font = Font(name="Arial", size=9, italic=True, color="818283")
    ws.append([])
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=4, column=col)
        cell.font = Font(name="Arial", size=10, bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for r in rows:
        ws.append(["" if v is None else v for v in r])
    last = 4 + len(rows)
    for col, header in enumerate(headers, 1):
        letter = get_column_letter(col)
        ws.column_dimensions[letter].width = (widths or {}).get(header, 60 if header in WRAP else min(34, max(12, len(header) + 2)))
        if header in WRAP:
            for cell in ws[letter][4:last]:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "C5"
    if rows:
        ws.auto_filter.ref = f"A4:{get_column_letter(len(headers))}{last}"
    return ws


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    issues = []

    def check(scope, mid, text, offer_ids, names=(), convening=False):
        for problem in L.check_message(text, offer_ids, convening=convening, ignore=names):
            issues.append([scope, mid, problem])

    m = ro(MASTER)
    corporate_headers = ["message_id", "organisation", "recipient", "recipient_role", "contact_channel", "segment", "track", "review_status", "selection",
                         "subject", "body", "follow_up_1", "follow_up_2", "offer_message", "kiswahili_version", "lead_brief", "offer_ids", "conditions"]
    # What research found about each lead, one line per fact with its source link (scripts/messaging/apply_hook_research.py).
    brief = {}
    if m.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='lead_briefs'").fetchone():
        for oid, fact, url in m.execute("SELECT organisation_id, fact, source_url FROM lead_briefs ORDER BY organisation_id, position"):
            brief.setdefault(oid, []).append(f"• {fact} ({url})")
    corporate = []
    for r in m.execute("""SELECT p.*, msg.conditions AS conditions FROM outreach_plans p JOIN messages msg USING(message_id)
                          ORDER BY CASE p.acquisition_track_id WHEN 'AQ02' THEN 0 WHEN 'AQ01' THEN 1 ELSE 2 END, p.segment, p.organisation_name"""):
        ids = [x.strip() for x in str(r["offer_ids"] or "").split(";") if x.strip()]
        names = tuple(n for raw in (r["organisation_name"], r["target_name"]) if raw for n in (raw, L.display_name(raw), L.greeting_name(raw)))
        for field in ("body", "follow_up_1", "follow_up_2", "offer_message", "offer_message_sw"):
            check("corporate", r["message_id"], r[field], ids, names)
        for field in ("body", "offer_message_sw"):  # the first message, in English and Kiswahili, is a request with no offer terms
            issues += [["corporate", r["message_id"], problem] for problem in L.check_first_message(r[field], ignore=names)]
        corporate.append([r["message_id"], r["organisation_name"], r["target_name"] if r["target_type"] == "contact" else "Organisation route",
                          r["recipient_role"], r["contact_channel"], r["segment"], r["acquisition_track_id"], r["review_status"], r["selection"],
                          r["subject"], r["body"], r["follow_up_1"], r["follow_up_2"], r["offer_message"], r["offer_message_sw"],
                          "\n".join(brief.get(r["organisation_id"], [])), r["offer_ids"],
                          "; ".join(x for x in (r["missing_information"], r["conditions"]) if x)])
    parents = []
    for r in m.execute("SELECT d.*, e.enquiry_date, e.platform FROM parent_enquiry_drafts d JOIN enquiries e USING(enquiry_id) ORDER BY d.status, e.enquiry_date"):
        if str(r["status"]).startswith("Review only"):
            check("parent", r["enquiry_id"], r["body"], ["OF01", "OF02", "OF09"])
        parents.append([r["enquiry_id"], r["enquiry_date"], r["platform"], r["status"], r["route_status"], r["subject"], r["body"]])
    master_counts = Counter(r[6] for r in corporate)
    m.close()

    run_rows, run_counts = {}, {}
    for track, run_id in RUNS.items():
        con = ro(ROOT / "outputs" / "runs" / run_id / "lead-database.sqlite")
        result = L.run_message_checks(con, convening=track == "government")
        issues += [[track, mid, problem] for mid, problem in result["issues"]]
        run_rows[track] = L.outreach_sheet_rows(con)
        run_counts[track] = dict(con.execute("SELECT review_status, COUNT(*) FROM outreach_plans GROUP BY 1").fetchall())
        con.close()

    offer_rows = [[o["id"], o["name"], o.get("audience", ""), o["terms"], o["use"], o.get("use_note", "") or o.get("restriction", ""),
                   o["source"], o.get("locator", ""), ", ".join(o.get("tracks", []))] for o in L.REGISTER["offers"]]
    source_rows = [[s["id"], s.get("path") or s.get("url"), s.get("sha256", "")[:16], s["title"], s.get("locator", "") or s.get("checked_on", "")]
                   for s in L.REGISTER["sources"]]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary = {"generated": generated, "offer_version": L.OFFER_VERSION, "corporate_drafts": len(corporate), "corporate_by_track": dict(master_counts),
               "parent_replies_reviewable": sum(1 for p in parents if str(p[3]).startswith("Review only")), "welfare": run_counts["welfare"],
               "government": run_counts["government"], "conformance_issues": len(issues)}
    wb = Workbook()
    ws = wb.active
    ws.title = "Read Me"
    lines = [("Silverleaf offer-aligned messages", "title"),
             (f"Generated {generated}. Drafts from the company master and the welfare and government runs (their SQLite databases are the source of "
              f"truth). Offer register version {L.OFFER_VERSION}. Nothing here has been sent, and no automation is enabled.", "sub"), ("", ""),
             ("What changed", "h"),
             ("Request first (23 September 2026). The first message to an organisation makes a relevant request and states no offer terms: its "
              "purpose, who is writing (Mariam Haji, Marketing and Partnership Coordinator) and a short meeting, in person or by phone. The offer "
              "follows in the next message.", ""),
             ("Employers: a meeting about an education benefit for the children of their staff; where the decision-maker is unknown (AQ01), the "
              "message also asks to be pointed to whoever looks after staff welfare. Savings groups: a meeting with the committee about members' "
              "children's education. Welfare homes and programmes: working together on the education of the children in their care. Welfare "
              "funders only: a request to sponsor students (two or three to start), with the funder's verified support for a home as the reason "
              "where the welfare run records one. Rivertrees: renewing its 2025 partnership. Government offices: the Kiswahili letters were "
              "already requests (a free school-readiness talk for parents) and are unchanged apart from the signature.", ""),
             ("The offer, taken only from data/reference/silverleaf-offer-register.json: employers get a staff school-fee benefit at no cost to "
              "the employer (20% off tuition for heads of department for as long as the child studies at Silverleaf; 10% off the first year for all "
              "other staff) and the family offer; savings groups the family offer and a member-association group rate; homes and funders the NGO "
              "partner rate (3–18% per child when all primary-age children are placed). Family offer, open to every family: a free uniform set "
              "(worth TZS 110,000) when the year's tuition is paid before the school year opens; 10% off tuition for a third child and 20% for a "
              "fourth; tuition in four instalments.", ""),
             ("Where the offer appears: company master AQ02 drafts send it as follow-up 1, and every company draft holds it in offer_message, the "
              "reply to send once someone answers (on AQ01, once they name the right colleague). Welfare drafts send it as the follow-up.", ""),
             ("Personalisation only where the fact is relevant and safe: a verified hook (six company drafts), a funder's verified support for a "
              "home, the nearest campus and distance when the lead's location is precise, the recipient's role, and the wards nearest our campuses "
              "in council letters.", ""),
             ("", ""), ("Before anything is sent", "h"),
             ("1. Finance confirms that the 2025 terms apply to the 2027 school year (2027 enrolment plan tasks A1 and A2) before any message that "
              "states them. First messages state no terms.", ""),
             ("2. The 40% rate is Rivertrees' negotiated term only. The member-association rate is documented for KINEFA; Finance must agree to extend it.", ""),
             ("3. Tuition figures are not quoted in first messages; send the current fee schedule on request (the website's figures carry no school year).", ""),
             ("4. Kiswahili drafts need native-speaker review. Government letters also need the campaign C11 gates (session content, guide, privacy notice).", ""),
             ("5. Held drafts (AQ00, WA00, GA00, needs_review) state what is missing in their conditions column.", ""),
             ("", ""), ("Counts", "h"),
             (f"Corporate (company master): {len(corporate)} drafts, by track: " + "; ".join(f"{k} {v}" for k, v in sorted(master_counts.items())) +
              f". Historical parent replies reviewable: {summary['parent_replies_reviewable']}.", ""),
             ("Welfare run: " + "; ".join(f"{k} {v}" for k, v in sorted(run_counts["welfare"].items())) +
              ". Government run: " + "; ".join(f"{k} {v}" for k, v in sorted(run_counts["government"].items())) + ".", ""),
             (f"Conformance issues: {len(issues)} (every percentage and amount matches the register; no expired referral reward; no benefit to "
              f"officials; no offer terms in a first message).", ""),
             ("", ""), ("Sheets", "h"),
             ("Offer Register · Offer Sources · Corporate Messages · Parent Replies · Welfare Messages · Government Letters · Conformance", "")]
    for i, (text, kind) in enumerate(lines, 1):
        cell = ws.cell(row=i, column=1, value=text)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.font = Font(name="Arial", size=16 if kind == "title" else 11 if kind == "h" else 10, bold=kind in ("title", "h"),
                         italic=kind == "sub", color=BLUE if kind in ("title", "h") else "000000")
    ws.column_dimensions["A"].width = 150
    add_sheet(wb, "Offer Register", "Terms a message may state, with their source. 'use: no' terms never appear; 'limited' terms have the audience in use_note.",
              ["offer_id", "name", "audience", "terms", "use", "use_note", "source", "locator", "tracks"], offer_rows, {"terms": 80, "use_note": 70})
    add_sheet(wb, "Offer Sources", "Files and pages behind the register.", ["source_id", "path_or_url", "sha256", "title", "locator_or_checked_on"],
              source_rows, {"path_or_url": 70, "title": 60, "locator_or_checked_on": 70})
    add_sheet(wb, "Corporate Messages", "Company master outreach plans, request first: body asks for a meeting; offer_message states the offer "
              "(AQ02's follow-up 1, or the reply). Earlier versions are in message_versions ('2026-09-23-before-offer-v4', "
              "'2026-09-23-before-request-first').",
              corporate_headers, corporate, {"organisation": 34, "body": 80, "follow_up_1": 90, "offer_message": 90, "kiswahili_version": 80,
                                             "lead_brief": 80, "conditions": 70})
    add_sheet(wb, "Parent Replies", "Historical public enquiries in the master: 'Review only' rows carry one reply with the family offer; the rest get none.",
              ["enquiry_id", "enquiry_date", "platform", "status", "route_status", "subject", "body"], parents, {"body": 90, "status": 50})
    add_sheet(wb, "Welfare Messages", "Welfare run drafts: a meeting request first (sponsorship requests for funders only), then the partner "
              "rates in follow_up_1; replies to in-fit enquiries.",
              L.OUTREACH_HEADERS, run_rows["welfare"], {"target": 36, "body": 90, "follow_up_1": 70, "conditions": 70})
    add_sheet(wb, "Government Letters", "Government run letters in Kiswahili with an English meaning. GA01 councils first; everything else is held.",
              L.OUTREACH_HEADERS, run_rows["government"], {"target": 40, "body": 90, "english_meaning": 90, "conditions": 70})
    add_sheet(wb, "Conformance", "Any draft that fails the offer-register checks (expected: none).", ["scope", "message_id", "issue"], issues)
    out = ROOT / "outputs" / "messages"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"Silverleaf Offer-Aligned Messages - {args.date}.xlsx"
    wb.save(path)
    (out / "offer-messages-summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"workbook": str(path.relative_to(ROOT)), **summary}, indent=1))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
