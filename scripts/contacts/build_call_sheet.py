#!/usr/bin/env python3
"""Build a call sheet: the top-tier employers that still lack a named staff-benefits contact, with a two-minute script to ask who it is.

A short phone call is the most reliable way to learn who looks after staff welfare or benefits, and the person can agree to receive the
email, which is consent-based. Reads the master (read-only): companies in reach tiers P1 and P2 (rank_employer_reach.py) whose chosen
recipient is the company team, or a named person who is not HR or the general manager, and that publish a phone number.
Writes outputs/contacts/Silverleaf Call Sheet - <date>.xlsx:
- "Script": the call script in English and Kiswahili (native-speaker review needed) and the rules for the call;
- "Calls": one row per company, most reach first, with the numbers to call, who to ask for, and blank columns for the answer.
Fill in the blank columns and import them with import_call_results.py. Nothing is dialled or sent.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
OUT = ROOT / "outputs" / "contacts"
PHONE = re.compile(r"\+?\d[\d ()-]{7,}\d")
HEADERS = ["priority", "reach_tier", "reach_score", "organisation", "organisation_id", "kind", "phones", "company_email", "current_recipient",
           "ask_for", "answered_by_name", "answered_by_role", "contact_name", "contact_role", "contact_work_email", "contact_work_phone",
           "agreed_to_receive_email (yes/no)", "outcome (reached / call back / wrong number / not interested / no answer)", "call_date", "caller", "notes"]
SCRIPT_EN = """Good morning / afternoon. My name is [caller], from Silverleaf Academy, the school in Arusha, Usa River and Boma Ng'ombe.
We are setting up partnerships with employers to provide an education benefit for the children of their staff.
Could you tell me who looks after staff welfare or benefits at [company]?
(If named) Thank you. Could I have their work email, so that Mariam Haji, our Marketing and Partnership Coordinator, can send them a short note?
Is it all right for us to email them about this?
Thank you very much for your help."""
SCRIPT_SW = """Habari za asubuhi / mchana. Naitwa [jina], kutoka Silverleaf Academy, shule iliyoko Arusha, Usa River na Boma Ng'ombe.
Tunaanzisha ushirikiano na waajiri ili kutoa fursa ya elimu kwa watoto wa wafanyakazi wao.
Je, unaweza kunieleza ni nani anayeshughulikia ustawi au marupurupu ya wafanyakazi katika [kampuni]?
(Akitajwa) Asante. Naweza kupata barua pepe yake ya kazini, ili Mariam Haji, Mratibu wetu wa Masoko na Ushirikiano, amtumie ujumbe mfupi?
Je, ni sawa tukimtumia barua pepe kuhusu jambo hili?
Asante sana kwa msaada wako."""
WELFARE_EN = """Good morning / afternoon. My name is [caller], from Silverleaf Academy, the school in Arusha, Usa River and Boma Ng'ombe.
We would like to set up a partnership with homes and programmes like [organisation] on the education of the children in their care.
Could you tell me who leads [organisation], or who decides on the children's schooling?
(If named) Thank you. Could I have their work email, so that Mariam Haji, our Marketing and Partnership Coordinator, can send them a short note?
Is it all right for us to email them about this?
Thank you very much for your help."""
WELFARE_SW = """Habari za asubuhi / mchana. Naitwa [jina], kutoka Silverleaf Academy, shule iliyoko Arusha, Usa River na Boma Ng'ombe.
Tungependa kuanzisha ushirikiano na vituo na programu kama [kituo] kuhusu elimu ya watoto walio chini ya uangalizi wao.
Je, unaweza kunieleza ni nani kiongozi wa [kituo], au ni nani anayeamua kuhusu masomo ya watoto?
(Akitajwa) Asante. Naweza kupata barua pepe yake ya kazini, ili Mariam Haji, Mratibu wetu wa Masoko na Ushirikiano, amtumie ujumbe mfupi?
Je, ni sawa tukimtumia barua pepe kuhusu jambo hili?
Asante sana kwa msaada wako."""
RULES = ["Call office numbers in working hours; one call, and at most one call-back. Stop at once if they are not interested.",
         "Ask only for the work name, role and work email or phone of the person who handles staff welfare or benefits. Never ask about anyone's children or family.",
         "Write down only what the person on the phone gives, and whether they agreed to the email. Do not guess spellings: ask them to spell names and emails.",
         "Do not promise discounts or terms on the call; the offer comes in the follow-up email after the first reply.",
         "The Kiswahili script is a draft for native-speaker review."]


def phones(*values) -> str:
    found = []
    for v in values:
        for m in PHONE.findall(str(v or "")):
            m = re.sub(r"[ ()-]", "", m)
            if len(re.sub(r"\D", "", m)) >= 9 and m not in found:
                found.append(m)
    return ", ".join(found[:3])


def save(rows, script_en: str, script_sw: str, path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Script"
    ws["A1"] = f"Silverleaf call sheet, {date.today().isoformat()}"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A3"], ws["A4"] = "English", script_en
    ws["A6"], ws["A7"] = "Kiswahili (draft for native-speaker review)", script_sw
    ws["A9"] = "Rules for the call"
    for i, rule in enumerate(RULES, 10):
        ws[f"A{i}"] = f"- {rule}"
    for cell in ("A3", "A6", "A9"):
        ws[cell].font = Font(bold=True)
    for cell in ("A4", "A7"):
        ws[cell].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = ws.row_dimensions[7].height = 120
    ws.column_dimensions["A"].width = 140
    calls = wb.create_sheet("Calls")
    calls.append(HEADERS)
    for row in rows:
        calls.append(row)
    widths = [8, 10, 10, 40, 16, 22, 34, 32, 40, 40, 22, 22, 26, 26, 32, 20, 18, 30, 12, 16, 40]
    for i, w in enumerate(widths, 1):
        calls.column_dimensions[calls.cell(1, i).column_letter].width = w
    fill = PatternFill("solid", fgColor="FFF2CC")
    for col in range(11, len(HEADERS) + 1):
        calls.cell(1, col).fill = fill
    calls.freeze_panes = "E2"
    if rows:
        tab = Table(displayName="TCalls", ref=f"A1:{calls.cell(1, len(HEADERS)).column_letter}{len(rows) + 1}")
        tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        calls.add_table(tab)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def welfare_sheet(run_id: str) -> int:
    """High- and medium-priority homes and programmes whose draft goes to the organisation route, with a phone to call."""
    db = ROOT / "outputs" / "runs" / run_id / "lead-database.sqlite"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    phones_by_org = {}
    for c in con.execute("SELECT organisation_id, organisation_phone, role_phone FROM contacts"):
        phones_by_org.setdefault(c["organisation_id"], []).extend([c["organisation_phone"], c["role_phone"]])
    rows = []
    for r in con.execute("""SELECT o.*, p.recipient, p.review_status FROM organisations o JOIN outreach_plans p USING(organisation_id)
                            WHERE p.target_type='organisation' AND o.priority IN ('High','Medium') AND o.segment NOT IN ('Welfare funder','Out of scope')
                            ORDER BY CASE o.priority WHEN 'High' THEN 0 ELSE 1 END, o.distance_km, o.name"""):
        if "(organisation route)" not in (r["recipient"] or ""):
            continue  # already addressed to a named leader
        numbers = phones(r["phone"], *phones_by_org.get(r["organisation_id"], []))
        if not numbers:
            continue
        rows.append([len(rows) + 1, r["priority"], r["distance_km"] if r["distance_km"] is not None else "", r["name"], r["organisation_id"], r["segment"],
                     numbers, r["email"] or "", "organisation team (no named person)", "the director or manager of the home or programme"] + [""] * 11)
    path = ROOT / "outputs" / "runs" / run_id / f"Silverleaf Welfare Call Sheet - {date.today().isoformat()}.xlsx"
    save(rows, WELFARE_EN, WELFARE_SW, path)
    print(f"{len(rows)} organisations to call: {path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--tiers", default="P1,P2")
    parser.add_argument("--run-id", help="a welfare run (for example arusha-welfare-2026-09): its high- and medium-priority homes and programmes")
    args = parser.parse_args()
    if args.run_id:
        return welfare_sheet(args.run_id)
    tiers = [t.strip() for t in args.tiers.split(",")]
    con = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    by_org = {}
    for c in contacts.values():
        by_org.setdefault(c["organisation_id"], []).append(c)
    rows = []
    for r in con.execute("""SELECT e.tier, e.score, o.*, p.segment AS plan_segment, p.target_type, p.target_id, p.target_name, p.recipient_role
                            FROM employer_reach e JOIN organisations o USING(organisation_id)
                            JOIN outreach_plans p ON p.organisation_id = e.organisation_id AND p.selection = 'Candidate for review'
                            WHERE e.tier IN (%s) ORDER BY e.tier, e.score DESC, o.name""" % ",".join("?" * len(tiers)), tiers):
        role = r["recipient_role"] or ""
        rank = R.role_rank(role) if r["target_type"] == "contact" else None
        if r["target_type"] == "contact" and rank in (0, 2) and "@" in str(contacts.get(r["target_id"], {}).get("named_email") or ""):
            continue  # already a named HR or general manager with their own email
        numbers = phones(r["phone"], *[c["organisation_phone"] for c in by_org.get(r["organisation_id"], [])],
                         *[c["role_phone"] for c in by_org.get(r["organisation_id"], [])])
        if not numbers:
            continue
        ask = "the human resources or administration manager" if r["plan_segment"] in ("Healthcare employers", "Education employers", "Corporate employers") \
            or re.search(r"hotel|lodge|camp|resort", f"{r['name']} {r['segment'] or ''}", re.I) else "the owner, managing director or general manager"
        current = f"{r['target_name']} ({role})" if r["target_type"] == "contact" else "company team (no named person)"
        rows.append([len(rows) + 1, r["tier"], r["score"], r["name"], r["organisation_id"], r["plan_segment"], numbers,
                     re.split(r"[;, ]+", str(r["email"] or "").strip())[0] if r["email"] else "", current, ask] + [""] * 11)
    path = OUT / f"Silverleaf Call Sheet - {date.today().isoformat()}.xlsx"
    save(rows, SCRIPT_EN, SCRIPT_SW, path)
    print(f"{len(rows)} companies to call: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
