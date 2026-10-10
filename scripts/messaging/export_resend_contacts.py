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

Government track (--tracks government; the government run database, read-only). Every office is segmented, whatever the
channel, because its letters go by hand or post (Tanzanian protocol: addressed by title, on letterhead). Two kinds of file:
  government-<confidence>.csv           Resend import rows, only for offices that publish an official inbox (an advance copy);
  government-delivery-<confidence>.csv  every office: letter addressee, who decides, who can decide quickly, the delivery route
                                        (postal and physical address, office phone, official email), wave and reason.
Confidence for government:
- high: the letter is ready (a pilot council's GA01 introduction, review_status draft_ready), the addressee's post has a holder
  named by an official source (leadership profile, the office's or its parent's own news, or a researched official page),
  verified and dated within 180 days, and the postal address comes from an official source;
- medium: the letter is ready, but the holder is not named, not verified or older than 180 days, or the postal address is
  missing or not official;
- low: the letter is held: councils outside the v1 pilot (promote: the user adds the council to the pilot), district and
  regional courtesy notices (promote: the B2G owner approves them after the pilot introductions), and every ward and village
  letter, held until its council introduces us (GA01 recorded) and the executive officer is verified within 90 days (GA02 gate).
  Wards carry a wave: first (up to 10 km from a campus), second (10 to 20 km), later (over 20 km), or 'locate the ward first'.
  A village office mapped inside a city council is flagged (cities have mitaa).
Writes outputs/messages/Silverleaf Government Segments - <date>.md (rules, counts, the high and medium offices, held offices).

Every row's confidence_reason says what would promote it. Nothing is sent: sending stays with a person.
Also writes outputs/messages/Silverleaf Resend Segments - <date>.md (counts and the import steps) for the companies, introducers
and welfare tracks (--tracks companies,welfare, the default together with government).
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
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


# ------------------------------------------------------------------ government (separate run database; letters, not email)
GOV_RECIPIENT = {"council": "council_director", "district": "district_administrative_secretary", "region": "regional_administrative_secretary",
                 "ward": "ward_executive_officer", "village": "village_executive_officer"}
GOV_DECIDES = {"council": "council_director", "district": "district_commissioner", "region": "regional_commissioner",
               "ward": "ward_executive_officer", "village": "village_executive_officer"}
GOV_QUICK = {"council": ["primary_education_head", "community_development_head", "social_welfare_officer"],
             "district": ["district_administrative_secretary"], "region": ["regional_administrative_secretary", "regional_education"],
             "ward": ["ward_community_development_officer", "ward_councillor"], "village": ["village_chair"]}
GOV_CURRENT_DAYS = 180   # a named holder counts as current when an official source named them within this many days
DELIVERY_FIELDS = ["confidence", "release_order", "confidence_reason", "wave", "office", "office_level", "council", "letter_to", "decision_maker",
                   "decision_maker_source", "quick_decision", "delivery", "postal_address", "physical_address", "office_phone", "official_email",
                   "campus", "distance_km", "ward_tier", "draft_status", "subject", "plan_id"]


def gov_wave(level: str, distance) -> str:
    if level not in ("ward", "village"):
        return {"council": "council introduction (GA01)", "district": "courtesy notice", "region": "courtesy notice"}.get(level, "")
    if distance in (None, ""):
        return "locate the ward first"
    d = float(distance)
    return "first wave (up to 10 km)" if d <= 10 else "second wave (10 to 20 km)" if d <= 20 else "later wave (over 20 km)"


def gov_person(post: dict | None, payload: dict, today: str) -> tuple[str, str, bool]:
    """('Title: Name', 'basis, source date, URL', current-and-verified) for a post; the name only as an official source gives it."""
    if not post:
        return "", "", False
    title = f"{post['office_title_sw']} ({post['office_title']})"
    name = post.get("holder_name") or ""
    if not name:
        return f"{title}: not named in any official source", "", False
    source_date = post.get("holder_source_date") or payload.get("holder_source_date") or ""
    age = (date.fromisoformat(today) - date.fromisoformat(source_date)).days if re.match(r"\d{4}-\d{2}-\d{2}$", source_date) else None
    current = (payload.get("verification_status") == "verified" and age is not None and age <= GOV_CURRENT_DAYS)
    basis = post.get("holder_basis") or payload.get("holder_basis") or "official source"
    return (f"{title}: {name}", f"{basis}; source dated {source_date or 'unknown'}; checked {post.get('holder_verified_on') or ''}; "
            f"{post.get('tenure_source_url') or ''}", current)


def government_rows(con, today: str):
    """Every government office, in a confidence segment: email rows (offices with an official inbox) and delivery rows (all)."""
    con.row_factory = sqlite3.Row
    payload = {}
    for eid, raw in con.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr USING(source_record_id)"):
        payload.setdefault(eid, json.loads(raw))
    posts = defaultdict(dict)
    for r in con.execute("SELECT * FROM official_posts"):
        posts[r["organisation_id"]][r["post_key"]] = dict(r)
    units = {r["unit_key"]: dict(r) for r in con.execute("SELECT * FROM admin_units")}
    sql = ("SELECT o.*, g.office_level, g.council_name, g.admin_unit_key, g.proposed_government_track, p.message_id, p.review_status, "
           "p.subject AS plan_subject, m.body FROM organisations o JOIN government_office_profiles g USING(organisation_id) "
           "JOIN outreach_plans p ON p.target_id = o.organisation_id JOIN messages m ON m.message_id = p.message_id")
    email_rows, delivery = [], []
    pilots = {r[0] for r in con.execute("SELECT g.council_name FROM government_office_profiles g JOIN outreach_plans p ON p.target_id = "
                                        "g.organisation_id WHERE g.office_level = 'council' AND p.review_status = 'draft_ready'")}
    for o in con.execute(sql):
        o = dict(o)
        level, oid = o["office_level"], o["organisation_id"]
        opay = payload.get(oid, {})
        office_posts = posts.get(oid, {})
        recipient = office_posts.get(GOV_RECIPIENT[level])
        rpay = payload.get(recipient["contact_id"], {}) if recipient else {}
        to_line, to_source, to_current = gov_person(recipient, rpay, today)
        decides = office_posts.get(GOV_DECIDES[level])
        dm_line, dm_source, dm_current = gov_person(decides, payload.get(decides["contact_id"], {}) if decides else {}, today)
        quick = []
        for key in GOV_QUICK[level]:
            q = office_posts.get(key)
            if q and q.get("holder_name"):
                note = " (B2G check first)" if q.get("b2g_check_required") == "yes" else (
                    " (engage only through the forum they chair)" if key == "ward_councillor" else "")
                quick.append(f"{q['office_title']}: {q['holder_name']}{note}")
        postal = o["address"] or ""
        official_route = opay.get("route_official") == "yes"
        email = (recipient or {}).get("published_role_email") or ""
        if not email and level in ("council", "region", "district"):
            email = o["email"] or ""
        unit = units.get(o.get("admin_unit_key") or "", {})
        wave = gov_wave(level, o["distance_km"])
        ready = o["review_status"] == "draft_ready"
        name_line = to_line.split(": ", 1)[-1]
        if not ready:
            confidence = "low"
            if level == "council":
                why = (f"held: outside the v1 pilot councils; promote: the user adds {o['council_name']} to the pilot"
                       + ("" if to_current else "; then confirm the director's name from an official source"))
            elif level in ("district", "region"):
                why = ("held: courtesy notice, not a v1 target; promote: the B2G owner approves the notice once the pilot councils have "
                       "introduced us" + ("" if postal else "; find the office's postal address"))
            else:
                why = (f"held until {o['council_name']} introduces us (GA01 recorded) and the "
                       f"{'WEO' if level == 'ward' else 'VEO'} is verified within 90 days; {wave}"
                       + ("" if (recipient or {}).get("holder_name") else f"; ask the council for the {'WEO' if level == 'ward' else 'VEO'}'s name and office phone at the GA01 meeting"))
                if level == "village" and "City" in (o["council_name"] or ""):
                    why += "; a city council has mitaa, not villages: confirm the office (mtaa?) before any letter"
        elif to_current and postal and official_route:
            confidence = "high"
            why = (f"ready; addressed to the {recipient['office_title']} by title, held by {name_line} ({to_source.split(';')[0]}, "
                   f"{to_source.split(';')[1].strip()}); official postal address {postal}")
        else:
            confidence = "medium"
            gaps = []
            if not (recipient or {}).get("holder_name"):
                gaps.append(f"the {GOV_RECIPIENT[level].replace('_', ' ')} is not named in an official source: confirm the holder")
            elif not to_current:
                gaps.append(f"{name_line} needs confirming (source older than {GOV_CURRENT_DAYS} days or not verified)")
            if not postal:
                gaps.append("no published postal address: confirm the delivery address")
            elif not official_route:
                gaps.append("postal address not from an official source: confirm it")
            why = "ready; " + "; ".join(gaps) + "; promote when confirmed"
        pilot = o["council_name"] in pilots
        order = ("1 now: pilot council introduction" if ready else
                 "2 after the introduction: pilot ward, first wave" if pilot and level in ("ward", "village") and wave.startswith("first") else
                 "3 after the introduction: pilot ward, second wave" if pilot and level in ("ward", "village") and wave.startswith("second") else
                 "4 courtesy notice after the pilot introductions" if level in ("district", "region") else
                 "5 if the pilot widens: non-pilot council" if level == "council" else
                 "6 later: non-pilot ward" if level in ("ward", "village") and wave.startswith(("first", "second")) else
                 "7 later wave or locate first")
        base = {"office": o["name"], "council": o["council_name"] or "", "confidence": confidence, "release_order": order,
                "confidence_reason": why, "wave": wave, "plan_id": o["message_id"]}
        delivery.append({**base, "office_level": level, "letter_to": to_line, "decision_maker": dm_line + (" (current)" if dm_current else ""),
                         "decision_maker_source": dm_source, "quick_decision": "; ".join(quick),
                         "delivery": "by hand to the office (letter on letterhead), or post to the postal address",
                         "postal_address": postal, "physical_address": opay.get("physical_address", ""), "office_phone": o["phone"] or "",
                         "official_email": email, "campus": o["campus"] or "", "distance_km": o["distance_km"] if o["distance_km"] is not None else "",
                         "ward_tier": unit.get("ward_tier") or "", "draft_status": o["review_status"], "subject": o["plan_subject"] or ""})
        if "@" in email:
            plain = re.sub(r"^(?:(?:Ndg|Ndugu|Bw|Bwana|Bi|Bibi|Mwl|Mhe|Mh|Mheshimiwa|Dkt|Dk|Hon|CPA)\.?\s*)+", "", name_line, flags=re.I)
            first, last = split_name(plain) if (recipient or {}).get("holder_name") else ("", "")
            email_rows.append({"email": email, "first_name": first, "last_name": last, "organisation": o["name"], "track": "government",
                               "audience": f"Local government office: {level}", "confidence": confidence,
                               "confidence_reason": why + "; email is an advance copy only: the signed letter goes by hand",
                               "priority": wave, "variant": "", "recipient": to_line, "message_subject": o["plan_subject"] or "",
                               "message_body": o["body"] or "", "message_html": to_html(o["body"] or ""), "plan_id": o["message_id"]})
    return email_rows, delivery


def write_government_summary(out: Path, today: str, email_rows, delivery) -> Path:
    counts = Counter(r["confidence"] for r in delivery)
    by_level = Counter((r["confidence"], r["office_level"]) for r in delivery)
    waves = Counter((r["council"], r["wave"]) for r in delivery if r["office_level"] in ("ward", "village"))
    lines = [f"# Government segments, {today}", "",
             "Every office in the government run, in one confidence segment, whatever the channel: the letters go by hand or post, and "
             "email (where an office publishes an official inbox) is an advance copy at most. Nothing is sent from this repository; a person "
             "delivers. Files in runtime/resend/" + today + "/ (not committed): `government-<confidence>.csv` (Resend import, email rows only) and "
             "`government-delivery-<confidence>.csv` (every office: who decides, who can decide quickly, how to deliver).", "",
             "## Rules", "",
             "- **High**: the letter is ready (a pilot council's GA01 introduction), it goes to a post whose current holder an official source "
             f"named within {GOV_CURRENT_DAYS} days (leadership profile, or the office's own news), and the postal address comes from an official source.",
             "- **Medium**: the letter is ready, but the addressee's holder is not named or not current in an official source, or the postal "
             "address needs confirming. The reason says what to confirm.",
             "- **Low**: the letter is held. Non-pilot councils (promote: add the council to the pilot), district and regional courtesy notices "
             "(promote: the B2G owner's approval after the pilot introductions), and every ward and village letter, held until its council "
             "introduces us (GA01) and the executive officer is verified within 90 days. Wards carry a wave: first (up to 10 km from a campus), "
             "second (10 to 20 km) and later (over 20 km).",
             "- Letters are addressed by title, as Tanzanian protocol expects. The holder's name is for the cover note, the follow-up call and "
             "the visit, never a reason to write to a person privately. Named councillors are engaged only through the forum they chair.", "",
             "## Counts", "", "| Segment | Offices | Of which with an official email (Resend file) |", "|---|---:|---:|"]
    emails = Counter(r["confidence"] for r in email_rows)
    for c in ("high", "medium", "low"):
        lines.append(f"| government-{c} | {counts[c]} | {emails[c]} |")
    lines += ["", "| Segment | Council | District | Region | Ward | Village |", "|---|---:|---:|---:|---:|---:|"]
    for c in ("high", "medium", "low"):
        lines.append(f"| {c} | " + " | ".join(str(by_level[(c, lvl)]) for lvl in ("council", "district", "region", "ward", "village")) + " |")
    lines += ["", "Within the segments, `release_order` gives the order of delivery once each gate opens:", "",
              "| Release order | Offices | Segment |", "|---|---:|---|"]
    orders = Counter((r["release_order"], r["confidence"]) for r in delivery)
    lines += [f"| {o} | {n} | {c} |" for (o, c), n in sorted(orders.items())]
    lines += ["", "## High and medium: deliver first", "", "| Segment | Office | Letter to | Decides | Quick decision | Postal address | Office phone | Reason |",
              "|---|---|---|---|---|---|---|---|"]
    for r in sorted((r for r in delivery if r["confidence"] != "low"), key=lambda r: (RANK[r["confidence"]], r["office"])):
        lines.append(f"| {r['confidence']} | {r['office']} | {r['letter_to']} | {r['decision_maker']} | {r['quick_decision'] or '-'} | "
                     f"{r['postal_address'] or '-'} | {r['office_phone'] or '-'} | {r['confidence_reason']} |")
    lines += ["", "## Low: held offices", "", "| Office | Letter to | Decides | Postal address | Promote by |", "|---|---|---|---|---|"]
    for r in sorted((r for r in delivery if r["confidence"] == "low" and r["office_level"] not in ("ward", "village")), key=lambda r: (r["office_level"], r["office"])):
        lines.append(f"| {r['office']} | {r['letter_to']} | {r['decision_maker']} | {r['postal_address'] or '-'} | {r['confidence_reason']} |")
    lines += ["", "Wards and villages (all low until their council introduces us), by council and wave:", "",
              "| Council | First wave (up to 10 km) | Second wave (10 to 20 km) | Later wave (over 20 km) | Locate first |", "|---|---:|---:|---:|---:|"]
    for council in sorted({k[0] for k in waves}):
        lines.append(f"| {council} | " + " | ".join(str(waves[(council, w)]) for w in ("first wave (up to 10 km)", "second wave (10 to 20 km)",
                                                                                      "later wave (over 20 km)", "locate the ward first")) + " |")
    named_weo = sum(1 for r in delivery if r["office_level"] in ("ward", "village") and "not named" not in r["letter_to"])
    lines += ["", f"Ward and village executive officers named by an official source: {named_weo} of "
              f"{sum(1 for r in delivery if r['office_level'] in ('ward', 'village'))}. Ask each pilot council for the WEO list at the GA01 meeting.",
              "", "Rules in full: the docstring of scripts/messaging/export_resend_contacts.py. Each row's confidence_reason says what would promote it."]
    path = ROOT / "outputs" / "messages" / f"Silverleaf Government Segments - {today}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


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


def government_main(args, today: str) -> int:
    gov_db = ROOT / "outputs" / "runs" / args.government_run / "lead-database.sqlite"
    con = sqlite3.connect(f"file:{gov_db.as_posix()}?mode=ro", uri=True)
    email_rows, delivery = government_rows(con, today)
    con.close()
    seen, unique, dropped = set(), [], []
    for r in sorted(email_rows, key=lambda r: RANK[r["confidence"]]):
        if r["email"].lower() in seen:
            dropped.append(f"{r['email']}: {r['organisation']} ({r['confidence']})")
            continue
        seen.add(r["email"].lower())
        unique.append(r)
    out = ROOT / "runtime" / "resend" / today
    out.mkdir(parents=True, exist_ok=True)
    for old in list(out.glob("government-*.csv")):  # only the government files; other tracks' files are left alone
        old.unlink()
    for confidence in ("high", "medium", "low"):
        subset = [r for r in unique if r["confidence"] == confidence]
        if subset:
            with (out / f"government-{confidence}.csv").open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(sorted(subset, key=lambda r: r["organisation"]))
        rows = sorted((r for r in delivery if r["confidence"] == confidence),
                      key=lambda r: (r["release_order"], r["council"], str(r["distance_km"]).zfill(8), r["office"]))
        with (out / f"government-delivery-{confidence}.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=DELIVERY_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    report = write_government_summary(out, today, unique, delivery)
    counts = Counter(r["confidence"] for r in delivery)
    print(f"government offices: high {counts['high']}, medium {counts['medium']}, low {counts['low']}; email rows {len(unique)}"
          f"{'; shared inboxes dropped: ' + str(len(dropped)) if dropped else ''}")
    print(f"{out}\n{report}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--welfare-run", default="arusha-welfare-2026-09")
    parser.add_argument("--government-run", default="arusha-government-2026-09")
    parser.add_argument("--tracks", default="companies,welfare,government",
                        help="'companies,welfare' (companies and introducers from the master, welfare from its run) and/or 'government'")
    args = parser.parse_args()
    today = date.today().isoformat()
    tracks = {t.strip() for t in args.tracks.split(",") if t.strip()}
    if "government" in tracks:
        government_main(args, today)
    if not tracks & {"companies", "welfare"}:
        return 0
    master = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
    welfare_db = ROOT / "outputs" / "runs" / args.welfare_run / "lead-database.sqlite"
    welfare = sqlite3.connect(f"file:{welfare_db.as_posix()}?mode=ro", uri=True)
    c_rows, c_skip = company_rows(master)
    w_rows, w_skip = welfare_rows(welfare)
    rows, dropped = dedupe(c_rows + w_rows)
    out = ROOT / "runtime" / "resend" / today
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.csv"):  # this script's own earlier files for the day (the government files have their own step)
        if not old.name.startswith("government-"):
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
