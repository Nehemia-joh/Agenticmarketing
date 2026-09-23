#!/usr/bin/env python3
"""Write the company master's outreach drafts: a request first, then Silverleaf's documented offer.

Reads data/reference/silverleaf-offer-register.json and the master (outputs/master/Silverleaf Master Database.sqlite).
- Every existing outreach plan gets a request-first sequence (strategy S-request-first-v5, 23 September 2026). Its
  message_id, target, acquisition track and call to action are kept.
  - The first message names the purpose, introduces the sender (Mariam Haji, Marketing and Partnership Coordinator)
    and asks for a short meeting. It states no offer terms.
  - The offer message (outreach_plans.offer_message) states the offer register's terms. AQ02 sends it as follow-up 1;
    on AQ01 it is the reply once someone names the right colleague. AQ01 otherwise sends one routing check-in.
  - Earlier copies are saved in message_versions first: '2026-09-23-before-offer-v4' (the pre-offer copy) and
    '2026-09-23-before-request-first' (the offer-led copy).
- Master organisations with no plan get one, unless they belong to another track or are excluded: local
  administration offices are in the government run, excluded offices (party, court, police, religious) get none.
  New plans are AQ01 when the organisation has a public email or phone and AQ00 (hold) otherwise.
- The nine reviewable historical parent replies gain the family offer.
- Adds offer columns to outreach_plans (offer_version, offer_ids, offer_evidence, offer_message, offer_message_sw),
  value module VM19, positioning evidence PE025-PE028 and the strategy records; everything in one transaction with
  integrity checks.
- Points the design-only send steps (F01, F03 and their touchpoints) at the request-first drafts; nothing is enabled.
Re-running it once the drafts are current changes nothing; run it again after a contact merge and the acquisition
refresh so each plan's copy matches its track. Nothing is sent. Use --dry-run to write the planned changes to runtime/
without touching the database, and --database to try it on a copy (its report then stays in runtime/). Afterwards run
npm run build:workbook (export and rebuild) and scripts/master/verify_master.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE_DB = ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"
GOVERNMENT_DB = ROOT / "outputs" / "runs" / "arusha-government-2026-09" / "lead-database.sqlite"
BACKUP_VERSION = "2026-09-23-before-offer-v4"
REQUEST_FIRST_BACKUP = "2026-09-23-before-request-first"
OFFER_STRATEGY_ID = "S-offer-aligned-v4"
STRATEGY_ID = "S-request-first-v5"
COPY_VERSION = "request-first-v5"
MESSAGE_STATUS = "Draft - not sent; request-first review"
TODAY = "2026-09-23"
OBSOLETE_NOTES = {"replace sender name"}  # the sender is Mariam Haji for every draft
COPY_FIELDS = ("subject", "body", "follow_up_1", "follow_up_2", "offer_message")
CAMPUSES_EN = "Our five campuses are Arusha City (Sakina), Kijenge and Ilboru in Arusha, Usa River, and Boma Ng'ombe."
LEVELS_EN = "We teach Daycare (from 18 months) to Grade 7 in English, with technology in lessons and a focus on student wellness."
# The offer message opens differently when it follows up unanswered (AQ02 follow-up 1) and when it answers a reply.
FOLLOW_UP_OPENER = "Following up on my earlier note, here is what we have in mind."
REPLY_OPENER = "Thank you for your reply. Here is what we have in mind."
EMPLOYER_OFFERS = ["OF04", "OF01", "OF02", "OF09"]
SACCOS_OFFERS = ["OF01", "OF02", "OF09", "OF07"]
RIVERTREES_OFFERS = ["OF08", "OF01", "OF02", "OF09"]
PARENT_OFFERS = ["OF01", "OF02", "OF09"]
CTA = {
    "Format choice": "Would a short staff session or a one-page offer sheet suit your team better?",
    "Information offer": "May I send you the one-page offer sheet to review?",
    "Planning conversation": "Could we have a 15-minute call to agree how best to share it with your staff?",
    "Welfare referral": "Could you point me to the colleague who looks after staff welfare or benefits?",
    "Sponsor referral": "Could you point me to the colleague who decides on staff benefits?",
    "Local referral": "Could you point me to the colleague who looks after your local staff?",
    "Committee referral": "Could you share this with your committee, or tell me who should receive the one-page member offer sheet?",
}
SEGMENT_MAP = [  # master organisation segment -> outreach segment for new plans
    (r"safari|tour|travel|guide|hotel|lodge|guest|attraction|tourism", "Tourism employers"),
    (r"hospital|clinic|health", "Healthcare employers"),
    (r"college|universit|educational", "Education employers"),
    (r"ngo", "NGO employers"),
    (r"office:government", "Public-sector employers"),
]
NEW_SEGMENTS = {
    "Corporate employers": ("Banks, companies and other private employers", "Staff school-fee benefit (OF04) plus the family offer",
                            "Confirm a public business route and the staff-benefits owner; do not infer family demand"),
    "Public-sector employers": ("Public agencies and parastatals as employers", "Staff school-fee benefit (OF04) through the HR route, after a compliance check",
                                "Never combine with a request for official action; route through HR; compliance check before contact"),
}


def sid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def precise(org: dict) -> bool:
    return str(org.get("geocode_precision") or "") in ("point", "locality") and org.get("distance_km") not in (None, "")


def campus_line(org: dict) -> str:
    """The nearest campus only when the organisation's location is precise; otherwise the five-campus network."""
    if org and precise(org):
        return L.campus_line_en(org.get("campus") or "", org.get("distance_km"), True, "you")
    return L.network_line_en()


# The six verified hooks were written for the earlier information-session offer. Each keeps its verified fact, rephrased
# as the reason for the request; the fact itself (and its source) is unchanged in outreach_plans.hook.
HOOK_SENTENCES = {
    "University of Arusha": "Your published information lists 150 active staff, so such a benefit could reach a wide team.",
    "Leopard Tours": "Your staffing page describes operations, workshop and driver-guide teams, so such a benefit could reach staff across all of them.",
}


def hook_sentence(plan: dict) -> str:
    hook = str(plan.get("hook") or "").strip()
    if not hook or not str(plan.get("hook_status") or "").startswith("Verified"):
        return ""
    for name, sentence in HOOK_SENTENCES.items():
        if name.lower() in hook.lower() or name.lower() in str(plan.get("organisation_name") or "").lower():
            return sentence
    first = re.split(r"(?<=[.!?])\s", hook)[0]
    return first if first.endswith((".", "?", "!")) else first + "."


# ------------------------------------------------------------------ copy
# The first message is a request (skills/silverleaf-outreach/references/offer-register.md): its purpose, who is writing
# and a short meeting, with no offer terms. The offer message states what Silverleaf offers. AQ02 sends it as follow-up
# 1; on AQ01 it is the reply once someone names the right colleague. Every copy returns both.
def routing_plan(plan: dict, track: str) -> bool:
    return track == "AQ01" or "Referral" in str(plan.get("cta_type") or "")


def employer_offer(greet: str, opener: str, org_name: str, staff: str, org: dict, cta: str) -> str:
    """The staff school-fee benefit and the family offer, exactly as the offer register records them."""
    campus = campus_line(org) if precise(org) else CAMPUSES_EN
    return (f"{greet}\n\n{opener} Silverleaf Academy would like to offer {staff} at {org_name} {L.EN['OF04']}. Every Silverleaf family can "
            f"also get {L.family_offer_en()}.\n\n{LEVELS_EN} {campus}\n\nYour team would only share the offer with staff; interested parents "
            f"deal with our admissions team directly, and applications for the 2027 school year are open. If you like, {org_name} can present "
            f"the benefit as its own, or add to it.\n\n{cta}\n\n{L.SIGNATURE}")


def employer_copy(plan: dict, org: dict, track: str) -> dict:
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"))
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Dear {L.greeting_name(plan['target_name'])}," if named else f"Dear {org_name} team,"
    staff = "local staff" if plan.get("segment") == "NGO employers" else "staff"
    extra = " It concerns your staff's own children, not student admissions." if plan.get("segment") == "Education employers" else ""
    hook = hook_sentence(plan)
    purpose = f"I am writing to explore an education benefit for the children of {staff} at {org_name}.{extra}{(' ' + hook) if hook else ''}"
    offer_cta = CTA.get(plan.get("cta_type") or "", CTA["Information offer"])
    if routing_plan(plan, track):
        referral = CTA.get(plan.get("cta_type") or "", CTA["Welfare referral"])
        if "point me" not in referral:
            referral = CTA["Welfare referral"]
        subject = f"An education benefit for {org_name} staff: who should I speak to?"
        body = (f"{greet}\n\n{purpose}\n\n{L.INTRO}\n\n{referral} I would welcome a short meeting with them, either in person or by phone."
                f"\n\n{L.SIGNATURE}")
        follow_1 = (f"{greet}\n\nA quick check on my note about an education benefit for staff at {org_name}: could you point me to the right "
                    f"colleague? If it is not relevant, just say so and I will close this.\n\n{L.SIGNATURE}")
        follow_2 = ""
        offer_cta = CTA["Information offer"] if "point me" in offer_cta else offer_cta
    else:
        subject = f"Meeting request: an education benefit for {org_name} staff"
        body = f"{greet}\n\n{purpose}\n\n{L.INTRO}\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}"
        follow_1 = employer_offer(greet, FOLLOW_UP_OPENER, org_name, staff, org, offer_cta)
        follow_2 = f"{greet}\n\nShould I send the one-page staff offer sheet for a quick look, or close this for now?\n\n{L.SIGNATURE}"
    offer = employer_offer(greet, REPLY_OPENER, org_name, staff, org, offer_cta)
    return {"subject": subject, "body": body, "follow_up_1": follow_1, "follow_up_2": follow_2, "offer_message": offer,
            "offer_ids": EMPLOYER_OFFERS, "sw": ""}


def saccos_copy(plan: dict, org: dict, track: str) -> dict:
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"))
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Dear {L.greeting_name(plan['target_name'])}," if named else f"Dear {org_name} committee,"
    body = (f"{greet}\n\nI am writing to explore how Silverleaf Academy could support the education of {org_name} members' children, and "
            f"would like to speak with your committee.\n\n{L.INTRO}\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}")

    def offer_text(opener: str) -> str:
        return (f"{greet}\n\n{opener} Every Silverleaf family can get {L.family_offer_en()}. We also offer member associations "
                f"{L.EN['OF07']}.\n\n{campus_line(org)}\n\n{CTA['Committee referral']}\n\n{L.SIGNATURE}")

    if routing_plan(plan, track):
        follow_1 = (f"{greet}\n\nA quick check: could I meet your committee briefly about education for members' children? If it is not "
                    f"relevant, just say so and I will close this.\n\n{L.SIGNATURE}")
        follow_2 = ""
    else:
        follow_1 = offer_text(FOLLOW_UP_OPENER)
        follow_2 = f"{greet}\n\nShould I send the one-page member offer sheet for a quick look, or close this for now?\n\n{L.SIGNATURE}"
    greet_sw = f"Habari {L.greeting_name(plan['target_name'])}," if named else f"Habari Kamati ya {org_name},"
    sw = (f"{greet_sw}\n\nNinaandika kuhusu elimu ya watoto wa wanachama wa {org_name}, na ningependa kuzungumza na kamati yenu.\n\n"
          f"{L.INTRO_SW}\n\n{L.MEETING_ASK_SW}\n\nKwa heshima,\n{L.SENDER_SW}\n{L.SENDER_TITLE_SW}\nSilverleaf Academy")
    return {"subject": f"Meeting request: education for {org_name} members' children", "body": body, "follow_up_1": follow_1,
            "follow_up_2": follow_2, "offer_message": offer_text(REPLY_OPENER), "offer_ids": SACCOS_OFFERS, "sw": sw}


def rivertrees_copy(org: dict) -> dict:
    greet = "Dear Rivertrees team,"
    body = (f"{greet}\n\nIn 2025 Silverleaf Academy proposed a Corporate Education Benefit Partnership for Rivertrees staff. Applications for the "
            f"2027 school year are now open, and we would like to renew it.\n\n{L.INTRO}\n\nWould it be possible to arrange a short meeting, either "
            f"in person or by phone, to confirm the 2027 terms and how you would like to share them with your staff?\n\n{L.SIGNATURE}")

    def offer_text(opener: str) -> str:
        return (f"{greet}\n\n{opener} As proposed in 2025, the partnership gives employees' children 40% off tuition, waives the TZS 50,000 "
                f"admission fee for new joiners, and allows monthly or quarterly instalments for tuition and transport. Every Silverleaf family "
                f"can also get {L.family_offer_en()}.\n\nOur Usa River campus nearby teaches Pre-Primary and Primary to Grade 7, with boarding. "
                f"Rivertrees can also present the benefit as its own, or add to it.\n\nShall I send a one-page summary of the terms?\n\n{L.SIGNATURE}")

    follow_2 = f"{greet}\n\nShould I send the one-page summary of the staff education benefit, or close this for now?\n\n{L.SIGNATURE}"
    return {"subject": "Renewing Silverleaf's staff education benefit for 2027", "body": body, "follow_up_1": offer_text(FOLLOW_UP_OPENER),
            "follow_up_2": follow_2, "offer_message": offer_text(REPLY_OPENER), "offer_ids": RIVERTREES_OFFERS, "sw": ""}


def parent_reply(draft: dict, enquiry: dict) -> str:
    greet = draft["body"].split("\n", 1)[0] if draft.get("body", "").startswith("Hello") else "Hello,"
    return (f"{greet}\n\nI'm {L.SENDER} from Silverleaf Academy, replying to your question about schools. If you are still looking, applications for "
            f"the 2027 school year are open. We teach Daycare (from 18 months) to Grade 7 in English at five campuses in Arusha, Usa River and "
            f"Boma Ng'ombe. Every family can get {L.family_offer_en()}.\n\nIf it would help, reply with the student's age or grade and the area you "
            f"would travel from, and our team will check the right campus and current fees.\n\n{L.SIGNATURE}")


# ------------------------------------------------------------------ main
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=str(MASTER))
    parser.add_argument("--dry-run", action="store_true", help="write runtime/messaging/master-preview.json and change nothing")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans ORDER BY message_id")]
    messages = {r["message_id"]: dict(r) for r in con.execute("SELECT * FROM messages")}
    org_record = {}
    for r in con.execute("SELECT entity_id, record_id FROM entity_sources WHERE entity_type='organisation' ORDER BY record_id"):
        org_record.setdefault(r["entity_id"], r["record_id"])
    welfare_links, triage = {}, {}
    if WELFARE_DB.exists():
        w = sqlite3.connect(f"file:{WELFARE_DB.as_posix()}?mode=ro", uri=True)
        for (payload,) in w.execute("SELECT payload_json FROM source_records"):
            p = json.loads(payload)
            if p.get("master_organisation_id") and p.get("record_type") == "organisation":
                welfare_links[p["master_organisation_id"]] = p.get("organisation_name")
        w.close()
    if GOVERNMENT_DB.exists():
        g = sqlite3.connect(f"file:{GOVERNMENT_DB.as_posix()}?mode=ro", uri=True)
        triage = {mid: (grp, detail) for mid, grp, detail in g.execute("SELECT master_organisation_id, triage_group, detail FROM master_triage")}
        g.close()

    updates, backups, outcomes, new_rows = [], [], Counter(), []
    for plan in plans:
        org = orgs.get(plan["organisation_id"], {})
        track = plan["acquisition_track_id"]
        if plan["segment"] == "SACCOS members":
            copy = saccos_copy(plan, org, track)
        elif org.get("name", "").startswith("Rivertrees"):
            copy = rivertrees_copy(org)
        else:
            copy = employer_copy(plan, org, track)
        updates.append((plan, copy, plan_notes(copy, plan["organisation_id"], welfare_links)))
        # The pre-offer and the offer-led copies are each kept once; later, only a copy that actually changes is kept, so a
        # re-run adds nothing.
        stored = tuple(plan.get(k) or "" for k in COPY_FIELDS)
        if not plan.get("offer_version"):
            label = BACKUP_VERSION
        elif plan.get("strategy_version") != COPY_VERSION:
            label = REQUEST_FIRST_BACKUP
        else:
            label = f"{date.today().isoformat()}-before-redraft" if stored != tuple(copy[k] or "" for k in COPY_FIELDS) else ""
        if label:
            backups.append((label, plan["message_id"], json.dumps({"outreach_plan": plan, "message": messages.get(plan["message_id"])},
                                                                  ensure_ascii=False, default=str)))
        outcomes["rewritten"] += 1

    planned_orgs = {p["organisation_id"] for p in plans}
    for oid, org in sorted(orgs.items(), key=lambda kv: kv[1]["name"]):
        if oid in planned_orgs:
            continue
        group, detail = triage.get(oid, ("", ""))
        if group == "Local administration office":
            outcomes["government track (government run)"] += 1
            continue
        if group == "Excluded" or (group == "Tagged as government but is not" and detail == "religious"):
            outcomes["excluded: no message"] += 1
            continue
        if oid in welfare_links:
            outcomes["welfare track (welfare run)"] += 1
            continue
        if org["name"].startswith("Rivertrees"):
            segment = "Tourism employers"
        elif group == "Tagged as government but is not":
            segment = "Education employers" if re.search(r"universit", org["name"], re.I) else "Corporate employers"
        else:
            segment = next((s for pattern, s in SEGMENT_MAP if re.search(pattern, str(org["segment"] or ""), re.I)), "Corporate employers")
        route = org.get("email") or org.get("phone")
        raw_osm = str(org.get("verification") or "").startswith("Raw OSM")
        rivertrees = org["name"].startswith("Rivertrees")
        track = "AQ02" if rivertrees else ("AQ01" if route and not raw_osm else "AQ00")
        plan = {"message_id": sid("M", "offer-v4", oid), "target_id": oid, "target_type": "organisation", "organisation_id": oid,
                "target_name": org["name"], "organisation_name": org["name"], "segment": segment, "cta_type": "Planning conversation" if rivertrees else "Welfare referral",
                "hook": "", "hook_status": ""}
        copy = rivertrees_copy(org) if rivertrees else employer_copy(plan, org, "AQ01")
        missing = []
        if not route:
            missing.append("No public email or phone; find the organisation's route before any message.")
        if raw_osm:
            missing.append("Raw OpenStreetMap place: match it to a curated organisation first.")
        if segment == "Public-sector employers":
            missing.append("Public body: send only to its HR route as an employee benefit, never with a request for official action; compliance check first.")
        if rivertrees:
            missing.append("Follows the 2025 Rivertrees proposal (references/Offers & Discounts/RIVERTREES Offer_2025.pdf); confirm its current status and the 2027 terms.")
        new_rows.append((plan, org, track, route, copy, missing))
        outcomes[f"new plan ({track})"] += 1

    # Named contacts without a plan (for example leads added by contact research) get their own draft, kept as an
    # alternative to the organisation's draft: AQ02 when the person has a direct route, AQ01 otherwise.
    segment_of = {p["organisation_id"]: p["segment"] for p in plans}
    segment_of.update({p["organisation_id"]: p["segment"] for p, *_ in new_rows})
    planned_contacts = {p["target_id"] for p in plans if p["target_type"] == "contact"}
    for c in [dict(r) for r in con.execute("SELECT * FROM contacts ORDER BY contact_id")]:
        if c["contact_id"] in planned_contacts or not c["name"] or c["organisation_id"] not in segment_of:
            continue
        org = orgs.get(c["organisation_id"], {})
        direct = c.get("named_email") or c.get("role_phone") or c.get("published_role_email")
        route = direct or c.get("shared_email") or c.get("organisation_phone") or org.get("email") or org.get("phone")
        track = "AQ02" if direct else ("AQ01" if route else "AQ00")
        plan = {"message_id": sid("M", "offer-v4-contact", c["contact_id"]), "target_id": c["contact_id"], "target_type": "contact",
                "organisation_id": c["organisation_id"], "target_name": c["name"], "organisation_name": org.get("name", ""),
                "segment": segment_of[c["organisation_id"]], "cta_type": "Information offer" if track == "AQ02" else "Welfare referral",
                "hook": "", "hook_status": "", "recipient_role": c.get("role") or "Named contact", "selection": "Alternative"}
        copy = saccos_copy(plan, org, track) if plan["segment"] == "SACCOS members" else employer_copy(plan, org, track)
        missing = [] if route else ["No published route for this person or the organisation; find one before any message."]
        if direct:
            missing.append("Named contact with a direct published route; consider selecting this draft instead of the organisation route.")
        new_rows.append((plan, org, track, route, copy, missing))
        outcomes[f"new contact plan ({track})"] += 1

    parents = [dict(r) for r in con.execute("SELECT * FROM parent_enquiry_drafts WHERE status LIKE 'Review only%'")]
    enquiries = {r["enquiry_id"]: dict(r) for r in con.execute("SELECT * FROM enquiries")}
    parent_updates = [(d, parent_reply(d, enquiries.get(d["enquiry_id"], {}))) for d in parents]
    outcomes["historical parent replies updated"] = len(parent_updates)
    outcomes["parent enquiries without a draft (unchanged)"] = con.execute("SELECT COUNT(*) FROM parent_enquiry_drafts WHERE status NOT LIKE 'Review only%'").fetchone()[0]

    issues = []
    checked = [(plan, copy) for plan, copy, _ in updates] + [(plan, copy) for plan, _, _, _, copy, _ in new_rows]
    for plan, copy in checked:
        names = tuple(n for raw in (plan.get("organisation_name"), plan.get("target_name")) if raw for n in (raw, L.display_name(raw), L.greeting_name(raw)))
        for field in ("body", "follow_up_1", "follow_up_2", "offer_message", "sw"):
            for problem in L.check_message(copy[field], copy["offer_ids"], ignore=names):
                issues.append({"message_id": plan["message_id"], "field": field, "issue": problem})
        for field in ("body", "sw"):  # the first message, in English and Kiswahili, is a request with no offer terms
            for problem in L.check_first_message(copy[field], ignore=names):
                issues.append({"message_id": plan["message_id"], "field": field, "issue": problem})
    for d, body in parent_updates:
        for problem in L.check_message(body, PARENT_OFFERS):
            issues.append({"message_id": d["enquiry_id"], "field": "parent reply", "issue": problem})
    summary = {"outcomes": dict(outcomes), "conformance_issues": len(issues), "tracks_new": dict(Counter(t for _, _, t, _, _, _ in new_rows)),
               "segments_new": dict(Counter(p["segment"] for p, *_ in new_rows))}
    preview_dir = ROOT / "runtime" / "messaging"
    preview_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run or issues:
        sample = [{"message_id": p["message_id"], "segment": p["segment"], "track": p["acquisition_track_id"], "subject": c["subject"], "body": c["body"],
                   "follow_up_1": c["follow_up_1"], "follow_up_2": c["follow_up_2"], "offer_message": c["offer_message"], "sw": c["sw"],
                   "offer_ids": c["offer_ids"], "notes": n} for p, c, n in updates]
        sample += [{"message_id": p["message_id"], "segment": p["segment"], "track": t, "subject": c["subject"], "body": c["body"],
                    "offer_message": c["offer_message"], "offer_ids": c["offer_ids"], "missing": m} for p, _, t, _, c, m in new_rows]
        (preview_dir / "master-preview.json").write_text(json.dumps({"summary": summary, "issues": issues, "messages": sample,
                                                                     "parent_replies": [{"enquiry_id": d["enquiry_id"], "body": b} for d, b in parent_updates]},
                                                                    indent=1, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(summary, indent=1))
        if issues:
            print(json.dumps(issues[:20], indent=1, ensure_ascii=False))
            raise SystemExit("Conformance issues found; nothing was written. See runtime/messaging/master-preview.json.")
        return 0

    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    try:
        con.execute("BEGIN")
        for column in ("offer_version", "offer_ids", "offer_evidence", "offer_message_sw", "offer_message"):
            if column not in columns:
                con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
        con.executemany("INSERT OR IGNORE INTO message_versions (version, message_id, original_json) VALUES (?,?,?)",  # keep the first backup
                        backups)
        evidence = "PE025; PE026; PE027; PE028"
        for plan, copy, notes in updates:
            vm = plan["value_module_ids"] if "VM19" in str(plan["value_module_ids"]) else f"{plan['value_module_ids']}; VM19"
            missing = drop_notes(merge_notes(plan.get("missing_information"), notes), OBSOLETE_NOTES)
            hook_status = NO_HOOK if plan.get("hook_status") == OFFER_LED_NO_HOOK else plan.get("hook_status")
            con.execute("""UPDATE outreach_plans SET subject=?, body=?, follow_up_1=?, follow_up_2=?, offer_message=?, proposed_offer=?,
                           value_module_ids=?, missing_information=?, campaign_copy_status=?, offer_version=?, offer_ids=?, offer_evidence=?,
                           offer_message_sw=?, strategy_version=?, hook_status=? WHERE message_id=?""",
                        (copy["subject"], copy["body"], copy["follow_up_1"], copy["follow_up_2"], copy["offer_message"],
                         offer_summary(copy["offer_ids"]), vm, missing, COPY_STATUS, L.OFFER_VERSION, "; ".join(copy["offer_ids"]), evidence,
                         copy["sw"], COPY_VERSION, hook_status, plan["message_id"]))
            con.execute("UPDATE messages SET subject=?, body=?, strategy_id=?, status=?, conditions=? WHERE message_id=?",
                        (copy["subject"], copy["body"], STRATEGY_ID, MESSAGE_STATUS, conditions_for(copy), plan["message_id"]))
        # Contact research may have found signs that an organisation has closed; its new drafts start held, as the merge
        # holds its existing ones.
        closing = {oid for (oid,) in con.execute("SELECT entity_id FROM review WHERE kind='Possible closure'")}
        for plan, org, track, route, copy, missing in new_rows:
            record = org_record.get(plan["organisation_id"])
            closed = plan["organisation_id"] in closing
            held = track == "AQ00" or closed
            status = "Needs research" if held else "Draft review"
            # Written exactly as a later rewrite would write it, so re-running the script changes nothing.
            conditions = conditions_for(copy)
            missing = [merge_notes("; ".join([CLOSURE_NOTE, *missing] if closed else missing), plan_notes(copy, plan["organisation_id"], welfare_links))]
            is_contact = plan["target_type"] == "contact"
            con.execute("INSERT INTO messages (message_id, target_type, target_id, subject, body, strategy_id, status, conditions, source_record_id) "
                        "VALUES (?,?,?,?,?,?,?,?,?)",
                        (plan["message_id"], plan["target_type"], plan["target_id"], copy["subject"], copy["body"], STRATEGY_ID,
                         MESSAGE_STATUS, conditions, record))
            modules = "VM01; VM02; VM03; VM06; VM19" if plan["segment"] == "SACCOS members" else "VM01; VM02; VM03; VM04; VM05; VM19"
            con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, target_name, organisation_name, strategy_version,
                           segment, recipient_role, persona, contact_channel, channel_attribution, evidence_url, evidence_date, verified_on, evidence_basis,
                           evidence_record_ids, relevance_reason, proposed_offer, cta_type, flow_id, review_status, missing_information, selection,
                           subject, body, follow_up_1, follow_up_2, hook_status, campaign_copy_status, acquisition_version, acquisition_track_id,
                           value_module_ids, strategy_scope, offer_version, offer_ids, offer_evidence, offer_message_sw, offer_message)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (plan["message_id"], plan["target_id"], plan["target_type"], plan["organisation_id"], plan["target_name"], org["name"], COPY_VERSION,
                         plan["segment"], plan.get("recipient_role", "Organisation routing"), "Named contact" if is_contact else "Employer route", route or "",
                         ("Published route of the named contact or organisation in the master" if is_contact else "Organisation's published route in the master")
                         if route else "", org.get("source_url") or "", "", TODAY, "reference_file", record or "",
                         (f"Named {plan.get('recipient_role') or 'contact'} at {org['name']}, as the organisation publishes it; staff school-fee benefit and family offer."
                          if is_contact else f"Employer in the lead list ({org.get('segment') or 'unclassified'}); staff school-fee benefit and family offer."),
                         offer_summary(copy["offer_ids"]), plan["cta_type"], "F03" if plan["segment"] == "SACCOS members" else "F01", status,
                         missing[0], plan.get("selection", "Candidate for review"), copy["subject"], copy["body"],
                         copy["follow_up_1"], copy["follow_up_2"], NO_HOOK, COPY_STATUS,
                         "2026-09-09-new-contact-acquisition-v4", track, modules,
                         "New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the acquisition track controls cadence.",
                         L.OFFER_VERSION, "; ".join(copy["offer_ids"]), evidence, copy.get("sw", ""), copy["offer_message"]))
            con.execute("INSERT OR REPLACE INTO campaign_lead_assignments (assignment_id, campaign_id, target_type, target_id, message_id, selection, "
                        "eligibility_status, reason, next_action, acquisition_track_id, value_module_ids, strategy_scope) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sid("A", "offer-v4", plan["message_id"]), "C02" if plan["segment"] == "SACCOS members" else "C01", plan["target_type"],
                         plan["target_id"], plan["message_id"], plan.get("selection", "Candidate for review"),
                         "Needs research" if held else ("Alternative - inactive" if is_contact else "Candidate after checks"),
                         "Request-first draft for a named contact without a plan" if is_contact else "Request-first draft for an organisation without a plan",
                         "Resolve route and owner" if track == "AQ00" else ("Confirm the organisation still operates" if closed else
                                                                            "Human review; choose one recipient per organisation" if is_contact
                                                                             else "Human review, then the AQ01 routing request"),
                         track, modules, "New-contact acquisition; track-selected and independent of the internal marketing calendar."))
        # message_versions only accepts message IDs, so parent-reply history gets its own table.
        con.execute("CREATE TABLE IF NOT EXISTS parent_enquiry_draft_versions (version TEXT, enquiry_id TEXT REFERENCES enquiries(enquiry_id), "
                    "original_json TEXT NOT NULL, PRIMARY KEY(version, enquiry_id))")
        for d, body in parent_updates:
            con.execute("INSERT OR IGNORE INTO parent_enquiry_draft_versions (version, enquiry_id, original_json) VALUES (?,?,?)",
                        (BACKUP_VERSION, d["enquiry_id"], json.dumps(d, ensure_ascii=False)))
            con.execute("UPDATE parent_enquiry_drafts SET body=?, evidence_ids=? WHERE enquiry_id=?",
                        (body, merge_notes(d["evidence_ids"], ["PE025", "PE027", "PE028"]), d["enquiry_id"]))
        con.execute("INSERT OR REPLACE INTO value_proposition_modules VALUES (?,?,?,?,?,?,?,?,?,?)",
                    ("VM19", "Employers, SACCOS and families", "Documented Silverleaf offer",
                     "The recipient sees concrete, documented savings: staff tuition discounts, the free uniform for full-year payment, sibling discounts and four instalments.",
                     "Offer terms exactly as recorded in data/reference/silverleaf-offer-register.json.", "Share the offer with staff or members.",
                     "Every offer-aligned v4 draft.", "Do not present 2025 terms as confirmed for 2027 before Finance confirms; no guaranteed places, transport or "
                     "outcomes; no referral rewards; the 40% rate is Rivertrees' only; the member-association rate needs Finance to extend it.",
                     "PE025; PE026; PE027; PE028", "Draft; confirm 2027 terms"))
        for row in (
            ("PE025", "Offer terms", "Silverleaf's discount schedule: free uniform for full-year payment; sibling 10%/20%; NGO partner 3-18%; institutional 20% heads of department and 10% first-year for other staff; KINEFA member rates; expired referral package; ECD facilitation.",
             "All offer-aligned v4 drafts state these terms from the offer register.", "references/Offers & Discounts/2025 Proposed Fees & Discounts - 2025 Discounts.pdf",
             "Summary of discounts offered, p.1 (sha256 c6125a41a129e7fd)", "Internal offer document (2025)", TODAY, "Usable with confirmation gate",
             "Confirm with Finance that each term applies to 2027 (Gantt A1, A2) before sending."),
            ("PE026", "Offer terms", "The 2025 Corporate Education Benefit Partnership proposal to Rivertrees: 40% tuition discount, admission fee waiver, monthly or quarterly instalments, facilities, parent events, priority enrolment; employer benefits including co-funding and employer branding.",
             "Rivertrees follow-up only; the proposal structure models later employer proposals.", "references/Offers & Discounts/RIVERTREES Offer_2025.pdf",
             "pp.1-3 (sha256 fc519c1589e80bb3)", "Internal negotiated proposal (2025)", TODAY, "Rivertrees only",
             "Do not quote 40% to other organisations."),
            ("PE027", "Published fees", "The admissions page lists admission 50,000, Daycare 1,600,000, Pre-Primary 1,800,000 and Primary 1,850,000 TZS a year, paid in four instalments; uniform 110,000; transport 550,000-1,000,000. It states no school year and no discounts.",
             "Four instalments and the uniform value may be stated; tuition figures are sent on request, not in first messages.", "https://www.silverleaf.co.tz/admissions",
             "School Fees section, checked 2026-09-23", "Current official web page", TODAY, "Usable with date recheck", "2027 fee structure approval in progress (Gantt A1)."),
            ("PE028", "Offer rule", "Every message records its offer IDs; percentages and amounts must match the offer register; no referral rewards; officials are never offered a benefit in a convening request.",
             "Verification of every offer-aligned draft.", "data/reference/silverleaf-offer-register.json", "rules", "Repository rule", TODAY, "Mandatory gate", ""),
        ):
            con.execute("INSERT OR REPLACE INTO positioning_evidence VALUES (?,?,?,?,?,?,?,?,?,?)", row)
        con.execute("INSERT OR REPLACE INTO strategies VALUES (?,?,?,?,?)",
                    (OFFER_STRATEGY_ID, "Offer-aligned outreach (documented Silverleaf offer)", "All organisation and parent drafts",
                     "Messages lead with the documented offer for the audience: employers get the staff school-fee benefit (OF04) and the family offer; "
                     "SACCOS get the family offer and the member-association rate; Rivertrees gets its 2025 terms. A recipient hook appears only when verified; "
                     "otherwise the message opens with the offer. Terms: data/reference/silverleaf-offer-register.json.",
                     "Superseded for first messages by S-request-first-v5 (23 September 2026); its offer copy is now the offer message"))
        con.execute("INSERT OR REPLACE INTO strategies VALUES (?,?,?,?,?)",
                    (STRATEGY_ID, "Request-first outreach", "All organisation drafts",
                     "The first message makes a relevant request: its purpose (an education benefit for the organisation's staff, a meeting "
                     "with a savings-group committee, or renewing Rivertrees' 2025 partnership), who is writing (Mariam Haji, Marketing and "
                     "Partnership Coordinator) and a short meeting, in person or by phone. It states no offer terms. The documented offer "
                     "follows in the offer message: follow-up 1 on AQ02, or the reply once an AQ01 route names the right colleague. A recipient "
                     "hook appears only when verified. Recommended by Kilusu for first-email response; adopted 23 September 2026. Terms: "
                     "data/reference/silverleaf-offer-register.json.",
                     "Draft; the Finance condition applies from the offer message"))
        con.execute("UPDATE acquisition_tracks SET initial_touch=? WHERE track_id='AQ02'",
                    ("Initial personalised request after human review; the documented offer follows in follow-up 1.",))
        for segment, (audience, offer, qualification) in NEW_SEGMENTS.items():
            if not con.execute("SELECT 1 FROM outreach_segments WHERE segment=?", (segment,)).fetchone():
                con.execute("INSERT INTO outreach_segments VALUES (?,?,?,?,?)", (segment, audience, offer, qualification, "F01"))
        align_recipes(con)
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        enabled = con.execute("SELECT COUNT(*) FROM automation_configuration WHERE enabled=1").fetchone()[0]
        if integrity != "ok" or fks or enabled:
            raise RuntimeError({"integrity": integrity, "foreign_keys": fks[:5], "enabled_automations": enabled})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("messages", "outreach_plans", "message_versions", "campaign_lead_assignments")}
    con.close()
    report = {"run_on": date.today().isoformat(), "offer_version": L.OFFER_VERSION, **summary, "counts_after": counts}
    # The reconciliation report belongs with the outputs only for the canonical master; a trial on a copy stays in runtime/.
    trial = Path(args.database).resolve() != MASTER.resolve()
    out = ROOT / "runtime" / "messaging" if trial else ROOT / "outputs" / "messages"
    out.mkdir(parents=True, exist_ok=True)
    (out / ("trial-reconciliation.json" if trial else "master-offer-messages-reconciliation.json")).write_text(json.dumps(report, indent=1) + "\n",
                                                                                                             encoding="utf-8")
    print(json.dumps(report, indent=1))
    return 0


COPY_STATUS = ("Draft; request-first v5 (message 1 asks for a meeting and states no offer terms; the offer message states the offer "
               "register v4 terms); no recipient hook unless verified; not sent")
NO_HOOK = "No hook: request-first opening"
OFFER_LED_NO_HOOK = "No hook: offer-led opening"
# The hold note scripts/contacts/merge_master_contacts.py writes for an organisation that may have closed.
CLOSURE_NOTE = "Possible closure found by contact research; confirm the organisation still operates before any message."


def conditions_for(copy: dict) -> str:
    """The message's release conditions; the same whether the plan is new or rewritten."""
    return (f"{L.REQUEST_FIRST} {L.CONFIRM_2027} Offer terms: {'; '.join(copy['offer_ids'])} (data/reference/silverleaf-offer-register.json). "
            "Confirm the route, campus fit and organisation relevance before use. No guaranteed places, transport or outcomes. One active "
            "recipient per organisation.")


def plan_notes(copy: dict, organisation_id: str, welfare_links: dict) -> list[str]:
    """The notes every offer-aligned plan carries, whether new or rewritten."""
    notes = [L.CONFIRM_2027]
    if "OF07" in copy["offer_ids"]:
        notes.append("The member-association rate is documented for KINEFA only; Finance must agree to extend it before sending.")
    if organisation_id in welfare_links:
        notes.append(f"Also a welfare lead ({welfare_links[organisation_id]}); contact the organisation once.")
    if copy.get("sw"):
        notes.append(L.NATIVE_REVIEW)
    return notes


RECIPE_CONFIGURATION = "automation-2026-09-23-offer-v4"
SACCOS_V3_COPY = "Offer an optional member information session without a loan, subsidy or discount claim"
SACCOS_V4_COPY = ("State the family offer and the member-association rate exactly as the offer register records them (Finance must extend "
                  "the KINEFA rate first); no loan, subsidy or referral claim")
SACCOS_V4_STEP2 = "Offer the one-page version using approved fee information without figures unless cleared"
SACCOS_V5_STEP1 = "Ask for a short meeting with the committee about members' children's education; no offer terms"
F01_V4_PRINCIPLE = "Offer-led, recipient-centred, one CTA; PE023 and PE024"
F01_V5_PRINCIPLE = "Request-first, recipient-centred, one CTA; the offer follows in follow_up_1; PE023 and PE024"
F01_V4_STEP2 = "Add durable value pillars and the campus-fit check; offer the one-page outline"
F01_V5_STEP2 = "State the documented offer from the offer register, with the campus fit; offer the one-page outline"


def align_recipes(con) -> None:
    """Point the design-only send steps at the offer-aligned drafts. They named the v3 copy column (which still holds the
    earlier copy) and ruled out any discount for SACCOS. The earlier text stays in automation_recipe_history under
    automation-2026-09-09-marketing-v3; the changed steps move to a new design-only configuration. Nothing is enabled."""
    con.execute("INSERT OR IGNORE INTO automation_configuration SELECT ?, '2026-09-23-offer-v4', 0, timezone, mode, ?, stop_events_json, "
                "source_id, 'Design only; the send steps use the offer-aligned drafts; no sending integration or recurring job is active.' "
                "FROM automation_configuration WHERE configuration_id='automation-2026-09-09-marketing-v3'",
                (RECIPE_CONFIGURATION, json.dumps({"copy": "outreach_plans subject, body, follow_up_1, follow_up_2 (offer v4)",
                                                   "terms": "data/reference/silverleaf-offer-register.json"})))
    for table, column in (("automation_recipes", "action"), ("outreach_flows", "action"), ("campaign_touchpoints", "purpose")):
        for old, new in (("campaign_message_v3", "offer-aligned message (subject and body)"),
                         ("campaign_follow_up_1_v3", "offer-aligned follow_up_1"), ("campaign_follow_up_2_v3", "offer-aligned follow_up_2")):
            con.execute(f'UPDATE {table} SET "{column}"=REPLACE("{column}", ?, ?) WHERE "{column}" LIKE ?', (old, new, f"%{old}%"))
    for table, column in (("automation_recipes", "example_copy"), ("outreach_flows", "example_copy"), ("campaign_touchpoints", "draft_copy")):
        con.execute(f'UPDATE {table} SET "{column}"=? WHERE "{column}"=?', (SACCOS_V4_COPY, SACCOS_V3_COPY))
    con.execute("UPDATE automation_recipes SET configuration_id=? WHERE action LIKE '%offer-aligned%'", (RECIPE_CONFIGURATION,))
    # Request-first (23 September 2026): step 1 sends the request and the offer moves to step 2.
    for table, column in (("automation_recipes", "action"), ("outreach_flows", "action"), ("campaign_touchpoints", "purpose")):
        for old, new in (("offer-aligned message (subject and body)", "request-first message (subject and body)"),
                         ("offer-aligned follow_up_1", "follow_up_1 (the documented offer)"), ("offer-aligned follow_up_2", "follow_up_2 (the close)")):
            con.execute(f'UPDATE {table} SET "{column}"=REPLACE("{column}", ?, ?) WHERE "{column}" LIKE ?', (old, new, f"%{old}%"))
    for table in ("automation_recipes", "outreach_flows"):
        con.execute(f"UPDATE {table} SET principle=? WHERE principle=?", (F01_V5_PRINCIPLE, F01_V4_PRINCIPLE))
    for table, column, step in (("automation_recipes", "example_copy", "step"), ("outreach_flows", "example_copy", "step"),
                                ("campaign_touchpoints", "draft_copy", "flow_step")):
        for flow, number, old, new in (("F01", 2, F01_V4_STEP2, F01_V5_STEP2), ("F03", 1, SACCOS_V4_COPY, SACCOS_V5_STEP1),
                                       ("F03", 2, SACCOS_V4_STEP2, SACCOS_V4_COPY)):
            con.execute(f'UPDATE {table} SET "{column}"=? WHERE flow_id=? AND "{step}"=? AND "{column}"=?', (new, flow, number, old))


def drop_notes(text: str, obsolete: set) -> str:
    """The field without notes that no longer apply."""
    return "; ".join(p for p in str(text or "").split("; ") if p.strip() and p.strip() not in obsolete)


def merge_notes(existing, notes) -> str:
    """Add notes to a '; '-separated field without repeating any, so re-running the script changes nothing.

    Some notes contain '; ' themselves, so notes are compared part by part, and parts repeated by earlier runs are dropped."""
    parts = list(dict.fromkeys(x.strip() for x in str(existing or "").split("; ") if x.strip()))
    for note in notes:
        parts += [p for p in dict.fromkeys(x.strip() for x in str(note or "").split("; ") if x.strip()) if p not in parts]
    return "; ".join(parts)


def offer_summary(ids) -> str:
    return "; ".join(f"{i} {L.OFFERS[i]['name']}" for i in ids)


if __name__ == "__main__":
    raise SystemExit(main())
