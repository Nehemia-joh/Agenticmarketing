#!/usr/bin/env python3
"""Consolidate the government run's letters into one review file.

Reads the run database (outputs/runs/<run-id>/lead-database.sqlite, read-only) and writes
outputs/messages/Silverleaf Government Drafts - <date>.md:
1. councils (the protocol introduction, GA01): the four pilot councils first, then the rest;
2. district and regional offices (courtesy notice);
3. wards and villages (convening request), by council and by distance from the nearest campus, so the first wave is the nearest wards.
Each entry has the Kiswahili letter, the English meaning for review, and the follow-up where there is one. Nothing is sent: the letters go on
letterhead, by hand or to the official address, after the Kiswahili is reviewed by a native speaker. Run draft_run_messages.py --track
government first.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
from datetime import date

import offer_lib as L

ROOT = L.ROOT
GENERIC = re.compile(r"^(Finance must confirm|Kiswahili draft: native-speaker|Letter on Silverleaf letterhead)")


def band(km) -> str:
    km = float(km) if km not in (None, "") else None
    if km is None:
        return "distance unknown"
    return "first wave (up to 10 km)" if km <= 10 else ("second wave (10 to 20 km)" if km <= 20 else "later (over 20 km)")


def holds(missing: str) -> str:
    parts = [p.strip() for p in re.split(r";\s+(?=[A-Z])", missing or "") if p.strip() and not GENERIC.search(p.strip())]
    return " ".join(parts)


def entry(n: str, r: dict, messages: dict) -> list[str]:
    mid = r["message_id"]
    lines = [f"### {n} {r['name']}", "",
             f"- To: {r['recipient']} | Delivery: {r['route_value']} | Plan: {mid} | Status: {r['review_status']}"]
    if r["office_level"] in ("ward", "village"):
        lines.append(f"- Nearest campus: {r['campus'] or 'unknown'}"
                     + (f", {r['distance_km']} km ({band(r['distance_km'])})" if r["distance_km"] not in (None, "") else "")
                     + (f" | Ward priority: tier {r['ward_tier']}, score {r['ward_score']}" if r.get("ward_score") is not None else ""))
    held = holds(r["missing_information"])
    if r["review_status"] != "draft_ready" and held:
        lines.append(f"- **Held:** {held}")
    lines += ["", f"**Kiswahili.** {messages[mid]['subject']}", "", "```", messages[mid]["body"], "```", ""]
    if mid + "-EN" in messages:
        lines += ["**English meaning, for review:**", "", "```", messages[mid + "-EN"]["body"], "```", ""]
    if mid + "-F1" in messages:
        lines += ["**Follow-up after 5 working days (Kiswahili):**", "", "```", messages[mid + "-F1"]["body"], "```", ""]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", default="arusha-government-2026-09")
    args = parser.parse_args()
    db = ROOT / "outputs" / "runs" / args.run_id / "lead-database.sqlite"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    messages = {r["message_id"]: dict(r) for r in con.execute("SELECT * FROM messages")}
    rows = [dict(r) for r in con.execute(
        "SELECT p.*, o.name, o.campus, o.distance_km, g.office_level, g.council_name, g.admin_unit_name, u.ward_score, u.ward_tier "
        "FROM outreach_plans p JOIN organisations o USING(organisation_id) JOIN government_office_profiles g USING(organisation_id) "
        "LEFT JOIN admin_units u ON u.unit_key = g.admin_unit_key")]
    councils = sorted((r for r in rows if r["office_level"] == "council"), key=lambda r: (r["review_status"] != "draft_ready", r["name"]))
    higher = sorted((r for r in rows if r["office_level"] in ("district", "region")), key=lambda r: (r["office_level"], r["name"]))
    local = [r for r in rows if r["office_level"] in ("ward", "village")]
    pilot = {r["council_name"] for r in councils if r["review_status"] == "draft_ready"}
    local.sort(key=lambda r: (r["council_name"] not in pilot, r["council_name"] or "", float(r["distance_km"] or 999), r["name"]))
    today = date.today().isoformat()
    lines = [f"# Government drafts, {today}: letters to local government offices", "",
             "Review copy only: nothing is sent. Kiswahili first, with an English meaning for review.", "",
             "## The angle", "",
             "Silverleaf is not selling to these offices and asks them for nothing for themselves. The request is **access to a forum parents already trust**: a 15 to 20 minute "
             "free talk in Kiswahili at a community meeting on getting children ready for school, learning at home and the admissions calendar, with a take-home booklet. "
             "Parents who want to hear more fill in Silverleaf's own form, and only if they choose to.", "",
             "- **Order:** a protocol introduction to the council first (it advises and introduces us to the ward executive officers), then the convening request to each ward "
             "or village, only after the council has introduced us. District and regional offices get a courtesy notice only.",
             "- **Message:** what the community gets (useful, free, in their language, no obligation). The letter states two safeguards plainly: no resident lists or "
             "residents' information, and no payments or gifts to anyone. It states no service, fee or offer: the parent booklet is mentioned, not described. Beyond the "
             "letter, the rules are no party or campaign involvement and no criticism of public schools.",
             "- **Ask:** a short meeting, in person or by phone, to discuss the details (the wards also ask for the 15 to 20 minute slot at their next community meeting).",
             "- **Hook:** none that is personal. The honest, sourced reasons are the office's role in convening the meeting and, for a ward or village, how far it is from our "
             "nearest campus. We do not flatter an official, use a personal fact about them, or claim government endorsement.",
             "- **What is deliberately left out:** fees, discounts and the list of services (they read as too salesy; they are in the booklet and the replies), the staff discount (it could read as an inducement to officials whose cooperation we seek), sponsorship, and any ask of the "
             "official personally. The letter goes to the office by title, not to a named person.",
             "- **Language and form:** formal Kiswahili on letterhead, delivered by hand or to the official postal address, closing \"Wako katika ujenzi wa Taifa\". The Kiswahili "
             "needs a native-speaker review before use.", "",
             f"**Counts.** {len(councils)} councils ({len(pilot)} pilot councils are ready: {', '.join(sorted(pilot))}); {len(higher)} district and regional offices (held); "
             f"{len(local)} ward and village offices (held until the council has introduced us). Wards are listed nearest first; "
             f"{sum(1 for r in local if float(r['distance_km'] or 0) > 20)} are more than 20 km from the nearest campus and belong in a later wave.", "", "---", "",
             f"# 1. Councils: protocol introduction ({len(councils)})", ""]
    for i, r in enumerate(councils, 1):
        lines += entry(f"1.{i}", r, messages)
    lines += ["---", "", f"# 2. District and regional offices: courtesy notice ({len(higher)})", ""]
    for i, r in enumerate(higher, 1):
        lines += entry(f"2.{i}", r, messages)
    lines += ["---", "", f"# 3. Wards and villages: convening request ({len(local)})", ""]
    last, k = None, 0
    for r in local:
        if r["council_name"] != last:
            last, k = r["council_name"], 0
            lines += [f"## {r['council_name']}" + (" (pilot council)" if r["council_name"] in pilot else ""), ""]
        k += 1
        lines += entry(f"3.{k}", r, messages)
    out = ROOT / "outputs" / "messages" / f"Silverleaf Government Drafts - {today}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(rows)} offices ({sum(r['review_status'] == 'draft_ready' for r in rows)} ready): {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
