#!/usr/bin/env python3
"""Export the company and welfare first messages as Resend contact-import files, one per audience and confidence segment.

Read-only. For every chosen first message with an email route (master: selection 'Candidate for review'; welfare run:
organisation plans) it writes one contact row: the address, the addressee's name, and custom properties that carry the
message itself (message_subject, message_body as text, message_html) and why the row sits in its segment. Resend imports a
CSV into one segment at a time, so each segment gets its own file in runtime/resend/<date>/:
  <track>-<confidence>.csv, track = companies | introducers | welfare, confidence = high | medium | low.

Confidence (in the data and in the recipient):
- high: the draft is ready for review, nothing is held, and it is addressed to a named decision-maker the organisation
  publishes (verified), reached at an address on the organisation's own domain or the person's own published address;
- medium: the draft is ready, but it goes to the organisation's inbox and needs routing, or the inbox is on a personal
  domain that the organisation publishes (companies) or that a reviewer confirmed as official (welfare);
- low: the draft is held or needs research (red flags, possible closure, unconfirmed role, location, unconfirmed personal
  inbox, a funder with no verified relationship, a savings group's Kiswahili and Finance checks, a public body's compliance check).
Rows without an email address (phone only, or no route) are left out and counted; they belong on the call sheets.
An address that two rows share is exported once (the higher-confidence row) and reported.

Every row's confidence_reason says what would promote it. Nothing is sent: sending stays with a person.
Also writes outputs/messages/Silverleaf Resend Segments - <date>.md (counts and the import steps).
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402  (address parsing, role ranking, verification)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
FIELDS = ["email", "first_name", "last_name", "organisation", "track", "audience", "confidence", "confidence_reason", "priority",
          "variant", "recipient", "message_subject", "message_body", "message_html", "plan_id"]
RANK = {"high": 0, "medium": 1, "low": 2}
GENERIC = re.compile(r"^(info|contact|hello|office|admin|enquiries|enquiry|reservations|bookings|operations|sales|mail|safari|tours)", re.I)
LOW_COMPANY = [(r"Possible closure", "possible closure: confirm it still operates"),
               (r"Raw OpenStreetMap", "raw map point: match it to a real company"),
               (r"organisation or branch overlap", "possible duplicate: resolve the overlap"),
               (r"Public body", "public body: compliance check, HR route only"),
               (r"Existing priority excludes", "excluded by priority: reassess fit"),
               (r"verify attribution", "address from an archive: verify it belongs to this person")]


def to_html(body: str) -> str:
    paras = [html.escape(p).replace("\n", "<br>") for p in body.strip().split("\n\n")]
    return "".join(f"<p>{p}</p>" for p in paras)


TITLE = re.compile(r"^(dr|prof|professor|mr|mrs|ms|miss|eng|engr|cpa|rev|fr|sr|hon|amb|capt|col|gen|sheikh|bishop|pastor|mama|mzee)\.?$", re.I)


def split_name(name: str) -> tuple[str, str]:
    """(first, last) without titles such as Dr. or CPA; ('', '') unless at least two name words remain."""
    parts = [w for w in L.greeting_name(name or "").split() if re.search(r"[A-Za-z]", w)]
    while parts and (TITLE.match(parts[0]) or re.fullmatch(r"(most|rt|the|pr)\.?", parts[0], re.I)):
        parts = parts[1:]
    return (parts[0], " ".join(parts[1:])) if len(parts) >= 2 else ("", "")


ROLE_INBOX = re.compile(r"^(md|ceo|gm|hr|cs|hq|res|pr|customer|support|marketing|management|travel|adventure|balloon|barua|tuambie|talktous|"
                        r"karibu|giving|donate|foundation|national|office|friends|code|post|team|general|director|finance|gmfinance|arusha|"
                        r"kilimanjaro|tanzania|moshi)", re.I)


def someone_else(address: str, name: str, organisation: str = "") -> bool:
    """True when the inbox looks like a named person's (not a role, not the organisation's name) and matches none of the addressee's names."""
    local, host = address.lower().split("@", 1)
    letters = re.sub(r"[^a-z]", "", local)
    label = re.sub(r"[^a-z]", "", host.split(".")[0])
    org = re.sub(r"[^a-z]", "", organisation.lower())
    if (not letters or GENERIC.match(local) or ROLE_INBOX.match(local) or (len(label) >= 3 and (label[:5] in letters or letters[:5] in label))
            or (len(letters) >= 6 and letters[:6] in org)):
        return False
    if "firstname" in letters:  # a pattern placeholder, not an address
        return True
    names = [n.lower() for n in re.findall(r"[A-Za-z]{3,}", L.greeting_name(name or "")) if not TITLE.match(n)]
    return bool(names) and not any(n in letters or letters.startswith(n[0] + names[-1][:3]) for n in names)


def own_domain(address: str, website: str) -> bool:
    site = R.domain(website)
    return bool(site) and address.split("@")[-1].endswith(site)


def company_route(plan, org, contact) -> str:
    """The address the message goes to: the person's own published address, else the plan's channel, preferring a generic inbox."""
    if contact and (contact["named_email"] or contact["published_role_email"]):
        direct = sorted(R.emails(contact["named_email"] or contact["published_role_email"]))
        if direct:
            return direct[0]
    pool = sorted(R.emails(plan["contact_channel"])) or sorted(R.emails(org["email"]))
    if contact:
        first = split_name(contact["name"])[0].lower()
        mine = [e for e in pool if first and e.split("@")[0].startswith(first)]
        if mine:
            return mine[0]
    generic = [e for e in pool if GENERIC.match(e)]
    return (generic or pool or [""])[0]


def company_rows(con):
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    reach = {r["organisation_id"]: r["tier"] for r in con.execute("SELECT organisation_id, tier FROM employer_reach")}
    rows, skipped = [], Counter()
    for p in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review' ORDER BY organisation_name"):
        p = dict(p)
        org = orgs[p["organisation_id"]]
        contact = contacts.get(p["target_id"]) if p["target_type"] == "contact" else None
        track = "introducers" if p["segment"] == "Introducers" else "companies"
        address = company_route(p, org, contact)
        if "@" not in address:
            skipped[f"{track}: no email route (phone only or none)"] += 1
            continue
        subject, body = (p["variant_subject"], p["variant_body"]) if p["variant_body"] else (p["subject"], p["body"])
        missing = p["missing_information"] or ""
        reasons = [label for pattern, label in LOW_COMPANY if re.search(pattern, missing)]
        if p["review_status"] != "Draft review":
            reasons.insert(0, "needs research: recheck the source, role and organisation")
        if p["segment"] == "SACCOS members":
            reasons.append("savings group: Kiswahili review and Finance's approval of the member rate first")
        named = bool(contact and R.VERIFIED.search(contact["verification"] or "") and not R.UNUSABLE.search(contact["verification"] or "")
                     and split_name(contact["name"])[0] and (R.role_rank(contact["role"]) is not None or R.FALLBACK_OK.search(contact["role"] or "")))
        direct = contact and address in R.emails(contact["named_email"], contact["published_role_email"])
        if named and someone_else(address, contact["name"], org["name"]) and not direct:
            reasons.append(f"the address {address} looks like another person's: confirm who reads it")
        if reasons:
            confidence, why = "low", "; ".join(dict.fromkeys(reasons))
        elif named and (direct or own_domain(address, org["website"])):
            confidence = "high"
            why = f"named, verified {contact['role'] or 'decision-maker'}" + (" at their own published address" if direct else " via the company's own inbox")
        elif named:
            confidence, why = "medium", "named, verified contact, but the address is not on the company's domain: confirm it reaches them"
        elif R.FREE_MAIL.search(address):
            confidence, why = "medium", "company inbox on a personal domain, published by the company; promote with a named decision-maker"
        else:
            confidence, why = "medium", "company inbox, needs routing; promote with a verified named decision-maker"
        first, last = split_name(contact["name"]) if contact else ("", "")
        rows.append({"email": address, "first_name": first, "last_name": last, "organisation": L.display_name(org["name"], org["organisation_id"]),
                     "track": track, "audience": p["segment"], "confidence": confidence, "confidence_reason": why,
                     "priority": reach.get(p["organisation_id"], org["priority"] or ""), "variant": p["message_variant"] or "",
                     "recipient": p["target_name"] if contact else f"{org['name']} team", "message_subject": subject or "",
                     "message_body": body or "", "message_html": to_html(body or ""), "plan_id": p["message_id"]})
    return rows, skipped


def welfare_rows(con):
    con.row_factory = sqlite3.Row
    rows, skipped = [], Counter()
    sql = ("SELECT p.*, o.name AS org_name, o.segment, o.priority, m.subject AS msg_subject, m.body FROM outreach_plans p "
           "JOIN organisations o USING(organisation_id) JOIN messages m ON m.message_id = p.message_id WHERE p.target_type='organisation'")
    for p in con.execute(sql):
        p = dict(p)
        address = (sorted(R.emails(p["route_value"])) or [""])[0]
        if "@" not in address:
            skipped["welfare: no email route (phone only or none)"] += 1
            continue
        missing = p["missing_information"] or ""
        held = [s.strip() for s in re.split(r";\s+(?=[A-Z])", missing)
                if s.strip() and not re.match(r"(The first message is a request|Finance must confirm|Personal-domain inbox confirmed)", s.strip())]
        recipient = p["recipient"] or ""
        named = not re.search(r"team|organisation route|\(.*route\)", recipient, re.I) and bool(split_name(recipient.split("(")[0])[0])
        if named and someone_else(address, recipient.split("(")[0], p["org_name"]):
            confidence, why = "low", f"addressed to {recipient.split('(')[0].strip()} but {address} looks like another person's address: confirm who reads it"
        elif p["review_status"] != "draft_ready":
            confidence, why = "low", ("; ".join(h[:160] for h in held) or "held: needs review")
        elif named:
            confidence, why = "high", "ready; addressed to the named leader the organisation publishes"
        elif "Personal-domain inbox confirmed" in missing:
            confidence, why = "medium", "ready; personal-domain inbox confirmed as official; promote with a named leader"
        else:
            confidence, why = "medium", "ready; organisation inbox addressed to the team; promote with a named leader"
        first, last = split_name(recipient.split("(")[0]) if named else ("", "")
        rows.append({"email": address, "first_name": first, "last_name": last, "organisation": L.display_name(p["org_name"], p["organisation_id"]),
                     "track": "welfare", "audience": p["segment"], "confidence": confidence, "confidence_reason": why,
                     "priority": p["priority"] or "", "variant": "", "recipient": recipient, "message_subject": p["msg_subject"] or "",
                     "message_body": p["body"] or "", "message_html": to_html(p["body"] or ""), "plan_id": p["message_id"]})
    return rows, skipped


def dedupe(rows):
    """One row per address: the higher-confidence row, then companies before welfare."""
    best, dropped = {}, []
    for r in sorted(rows, key=lambda r: (RANK[r["confidence"]], r["track"] != "companies")):
        key = r["email"].lower()
        if key in best:
            dropped.append(f"{r['email']}: {r['organisation']} ({r['track']}, {r['confidence']}) kept as {best[key]['organisation']} ({best[key]['track']})")
        else:
            best[key] = r
    return list(best.values()), dropped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--welfare-run", default="arusha-welfare-2026-09")
    args = parser.parse_args()
    today = date.today().isoformat()
    master = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
    welfare_db = ROOT / "outputs" / "runs" / args.welfare_run / "lead-database.sqlite"
    welfare = sqlite3.connect(f"file:{welfare_db.as_posix()}?mode=ro", uri=True)
    c_rows, c_skip = company_rows(master)
    w_rows, w_skip = welfare_rows(welfare)
    rows, dropped = dedupe(c_rows + w_rows)
    out = ROOT / "runtime" / "resend" / today
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.csv"):  # this script's own earlier files for the day
        old.unlink()
    counts = Counter((r["track"], r["confidence"]) for r in rows)
    for (track, confidence) in sorted(counts):
        subset = sorted((r for r in rows if r["track"] == track and r["confidence"] == confidence), key=lambda r: (str(r["priority"]), r["organisation"]))
        with (out / f"{track}-{confidence}.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(subset)
    skipped = c_skip + w_skip
    lines = [f"# Resend segments, {today}", "",
             "Contact-import files for Resend, one per segment, in runtime/resend/" + today + "/ (not committed: they hold contact addresses). "
             "Nothing is sent from this repository; a person sends.", "",
             "| Segment | Contacts |", "|---|---|"]
    lines += [f"| {t}-{c} | {n} |" for (t, c), n in sorted(counts.items(), key=lambda kv: (kv[0][0], RANK[kv[0][1]]))]
    lines += ["", "Left out (no email address; use the call sheets):", ""] + [f"- {k}: {v}" for k, v in sorted(skipped.items())]
    lines += ["", f"Addresses shared by two rows, exported once ({len(dropped)}):", ""] + [f"- {d}" for d in dropped]
    lines += ["", "Confidence rules and promotion: see the docstring of scripts/messaging/export_resend_contacts.py. Each contact's "
              "confidence_reason property says what would promote it.", "",
              "Custom contact properties to create in Resend before importing (all strings): " + ", ".join(FIELDS[3:]) + "."]
    report = ROOT / "outputs" / "messages" / f"Silverleaf Resend Segments - {today}.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for (t, c), n in sorted(counts.items(), key=lambda kv: (kv[0][0], RANK[kv[0][1]])):
        print(f"{t}-{c}: {n}")
    print(f"skipped: {dict(skipped)}; shared addresses dropped: {len(dropped)}")
    print(f"{out}\n{report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
