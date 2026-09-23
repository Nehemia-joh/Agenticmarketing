#!/usr/bin/env python3
"""Rewrite the company master's outreach drafts so they state Silverleaf's documented offer (offer v4).

Reads data/reference/silverleaf-offer-register.json and the master (outputs/master/Silverleaf Master Database.sqlite).
- Every existing outreach plan (927 on 23 September 2026) gets an offer-aligned first message and follow-ups, keeping
  its message_id, target, acquisition track and call to action. The previous plan and message rows are saved in
  message_versions under '2026-09-23-before-offer-v4' first.
- Master organisations with no plan get one, unless they belong to another track or are excluded: local
  administration offices are in the government run, excluded offices (party, court, police, religious) get none.
  New plans are AQ01 when the organisation has a public email or phone and AQ00 (hold) otherwise.
- The nine reviewable historical parent replies gain the family offer.
- Adds offer columns to outreach_plans (offer_version, offer_ids, offer_evidence, offer_message_sw), value module VM19,
  positioning evidence PE025-PE028 and a strategy record; everything in one transaction with integrity checks.
Nothing is sent and no automation changes. Use --dry-run to write the planned changes to runtime/ without touching
the database. Afterwards run scripts/master/export_master_workbook_data.py, rebuild the workbook where
@oai/artifact-tool is available (npm run build:workbook) and run scripts/master/verify_master.py.
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
STRATEGY_ID = "S-offer-aligned-v4"
TODAY = "2026-09-23"
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


# The six verified hooks were written for the earlier information-session offer. Offer v4 keeps each verified fact and
# rephrases it for the recipient; the fact itself (and its source) is unchanged in outreach_plans.hook.
HOOK_V4 = {
    "University of Arusha": "University of Arusha's published information lists 150 active staff, so a staff benefit can reach a wide team.",
    "Leopard Tours": "Leopard Tours' staffing page describes operations, workshop and driver-guide teams; the benefit below covers every one of them.",
}


def hook_sentence(plan: dict) -> str:
    hook = str(plan.get("hook") or "").strip()
    if not hook or not str(plan.get("hook_status") or "").startswith("Verified"):
        return ""
    for name, sentence in HOOK_V4.items():
        if name.lower() in hook.lower() or name.lower() in str(plan.get("organisation_name") or "").lower():
            return sentence
    first = re.split(r"(?<=[.!?])\s", hook)[0]
    return first if first.endswith((".", "?", "!")) else first + "."


# ------------------------------------------------------------------ copy
def employer_copy(plan: dict, org: dict, track: str) -> dict:
    org_name = plan.get("organisation_name") or org.get("name")
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Hello {plan['target_name']}," if named else f"Hello {org_name} team,"
    staff = "local staff" if plan.get("segment") == "NGO employers" else "staff"
    offer = f"Silverleaf Academy would like to offer {org_name} {staff} {L.EN['OF04'].replace('costs {org} nothing', 'costs your organisation nothing')}."
    extra = " It is for your staff's own children and separate from student admissions." if plan.get("segment") == "Education employers" else ""
    hook = hook_sentence(plan)
    routing = track == "AQ01" or "Referral" in str(plan.get("cta_type") or "")
    cta = CTA.get(plan.get("cta_type") or "", CTA["Welfare referral"] if routing else CTA["Information offer"])
    if routing and not named:
        subject = f"Staff school-fee benefit: who should review it at {org_name}?"
        offer = f"Silverleaf Academy would like to offer your {staff} {L.EN['OF04']}."
        body = (f"{greet}\n\nWho looks after staff benefits at {org_name}? {offer}{extra}\n\n{campus_line(org)}\n\n"
                f"Please point me to the right colleague and I will send them a one-page summary.\n\n{L.SIGNATURE}")
    else:
        subject = f"A school-fee benefit for {org_name} staff"
        body = (f"{greet}\n\n{(hook + ' ') if hook else ''}{offer}{extra}\n\n{campus_line(org)}\n\n"
                f"Your team would only share the offer with staff; interested parents deal with our admissions team directly, "
                f"and applications for the 2027 school year are open.\n\n{cta}\n\n{L.SIGNATURE}")
    if routing:
        follow_1 = (f"{greet}\n\nA quick check: who should receive the one-page summary of Silverleaf Academy's staff school-fee benefit "
                    f"for {org_name}? If it is not relevant, just say so and I will close this.\n\n{L.SIGNATURE}")
        follow_2 = ""
    else:
        follow_1 = (f"{greet}\n\nA little more detail in case it helps. Alongside the staff discount, every Silverleaf family can get "
                    f"{L.family_offer_en()}. We teach Daycare (from 18 months) to Grade 7 in English, with technology in lessons and a focus "
                    f"on student wellness. If you like, {org_name} can present the benefit as its own, or add to it.\n\n"
                    f"Shall I send the one-page offer sheet?\n\n{L.SIGNATURE}")
        follow_2 = f"{greet}\n\nShould I send the one-page staff offer sheet for a quick look, or close this for now?\n\n{L.SIGNATURE}"
    return {"subject": subject, "body": body, "follow_up_1": follow_1, "follow_up_2": follow_2, "offer_ids": EMPLOYER_OFFERS, "sw": ""}


def saccos_copy(plan: dict, org: dict) -> dict:
    org_name = plan.get("organisation_name") or org.get("name")
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Hello {plan['target_name']}," if named else f"Hello {org_name} committee,"
    body = (f"{greet}\n\nSilverleaf Academy would like to share some school-fee savings with {org_name} members. Every Silverleaf family can get "
            f"{L.family_offer_en()}. We also offer member associations {L.EN['OF07']}.\n\n{campus_line(org)}\n\n{CTA['Committee referral']}\n\n{L.SIGNATURE}")
    follow_1 = (f"{greet}\n\nA quick check: could your committee use a one-page summary of Silverleaf Academy's school-fee savings for members? "
                f"If it is not relevant, just say so and I will close this.\n\n{L.SIGNATURE}")
    greet_sw = f"Habari {plan['target_name']}," if named else f"Habari Kamati ya {org_name},"
    sw = (f"{greet_sw}\n\nSilverleaf Academy ingependa kuwaeleza wanachama wa {org_name} kuhusu nafuu za ada za shule. Kila familia ya Silverleaf "
          f"inaweza kupata {L.family_offer_sw()}. Pia vyama vya wanachama vinaweza kupata {L.SW['OF07']}.\n\n"
          f"{L.campus_line_sw(org.get('campus') or '' if precise(org) else '', org.get('distance_km'), precise(org))}\n\n"
          f"Je, unaweza kuwasilisha taarifa hii kwa kamati yako, au kunijulisha nani apokee muhtasari wa ofa kwa wanachama?\n\n{L.SENDER_SW}\nSilverleaf Academy")
    return {"subject": f"School-fee savings for {org_name} members", "body": body, "follow_up_1": follow_1, "follow_up_2": "",
            "offer_ids": SACCOS_OFFERS, "sw": sw}


def rivertrees_copy(org: dict) -> dict:
    greet = "Hello Rivertrees team,"
    body = (f"{greet}\n\nIn 2025 Silverleaf Academy proposed a Corporate Education Benefit Partnership for Rivertrees staff: 40% off tuition for "
            f"employees' children, the TZS 50,000 admission fee waived for new joiners, and monthly or quarterly instalments for tuition and "
            f"transport. Applications for the 2027 school year are now open, and we would like to renew that offer.\n\n"
            f"Our Usa River campus nearby teaches Pre-Primary and Primary to Grade 7, with boarding.\n\n"
            f"Could we meet for 15 minutes to confirm the 2027 terms and how you would like to share them with your staff?\n\n{L.SIGNATURE}")
    follow_1 = (f"{greet}\n\nA little more detail in case it helps. Alongside the staff rate, every Silverleaf family can get {L.family_offer_en()}. "
                f"Rivertrees can also present the benefit as its own, or add to it.\n\nShall I send a one-page summary of the terms?\n\n{L.SIGNATURE}")
    follow_2 = f"{greet}\n\nShould I send the one-page summary of the staff education benefit, or close this for now?\n\n{L.SIGNATURE}"
    return {"subject": "Renewing Silverleaf's staff education benefit for 2027", "body": body, "follow_up_1": follow_1, "follow_up_2": follow_2,
            "offer_ids": RIVERTREES_OFFERS, "sw": ""}


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
            copy = saccos_copy(plan, org)
        elif org.get("name", "").startswith("Rivertrees"):
            copy = rivertrees_copy(org)
        else:
            copy = employer_copy(plan, org, track)
        notes = [L.CONFIRM_2027]
        if "OF07" in copy["offer_ids"]:
            notes.append("The member-association rate is documented for KINEFA only; Finance must agree to extend it before sending.")
        if plan["organisation_id"] in welfare_links:
            notes.append(f"Also a welfare lead ({welfare_links[plan['organisation_id']]}); contact the organisation once.")
        if copy["sw"]:
            notes.append(L.NATIVE_REVIEW)
        updates.append((plan, copy, notes))
        backups.append((plan["message_id"], json.dumps({"outreach_plan": plan, "message": messages.get(plan["message_id"])}, ensure_ascii=False, default=str)))
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
        copy = saccos_copy(plan, org) if plan["segment"] == "SACCOS members" else employer_copy(plan, org, track)
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
    for plan, copy, _ in updates:
        for field in ("body", "follow_up_1", "follow_up_2", "sw"):
            for problem in L.check_message(copy[field], copy["offer_ids"], ignore=(plan.get("organisation_name"), plan.get("target_name"))):
                issues.append({"message_id": plan["message_id"], "field": field, "issue": problem})
    for plan, _, _, _, copy, _ in new_rows:
        for field in ("body", "follow_up_1", "follow_up_2"):
            for problem in L.check_message(copy[field], copy["offer_ids"], ignore=(plan.get("organisation_name"),)):
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
                   "follow_up_1": c["follow_up_1"], "follow_up_2": c["follow_up_2"], "sw": c["sw"], "offer_ids": c["offer_ids"], "notes": n}
                  for p, c, n in updates]
        sample += [{"message_id": p["message_id"], "segment": p["segment"], "track": t, "subject": c["subject"], "body": c["body"], "offer_ids": c["offer_ids"],
                    "missing": m} for p, _, t, _, c, m in new_rows]
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
        for column in ("offer_version", "offer_ids", "offer_evidence", "offer_message_sw"):
            if column not in columns:
                con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
        con.executemany("INSERT OR IGNORE INTO message_versions (version, message_id, original_json) VALUES (?,?,?)",  # keep the first backup
                        [(BACKUP_VERSION, mid, blob) for mid, blob in backups])
        evidence = "PE025; PE026; PE027; PE028"
        for plan, copy, notes in updates:
            vm = plan["value_module_ids"] if "VM19" in str(plan["value_module_ids"]) else f"{plan['value_module_ids']}; VM19"
            missing = merge_notes(plan.get("missing_information"), notes)
            con.execute("""UPDATE outreach_plans SET subject=?, body=?, follow_up_1=?, follow_up_2=?, proposed_offer=?, value_module_ids=?,
                           missing_information=?, campaign_copy_status=?, offer_version=?, offer_ids=?, offer_evidence=?, offer_message_sw=?,
                           strategy_version=? WHERE message_id=?""",
                        (copy["subject"], copy["body"], copy["follow_up_1"], copy["follow_up_2"], offer_summary(copy["offer_ids"]), vm, missing,
                         "Draft; offer-aligned v4 (offer register); no recipient hook unless verified; not sent", L.OFFER_VERSION,
                         "; ".join(copy["offer_ids"]), evidence, copy["sw"], "offer-v4", plan["message_id"]))
            con.execute("UPDATE messages SET subject=?, body=?, strategy_id=?, status=?, conditions=? WHERE message_id=?",
                        (copy["subject"], copy["body"], STRATEGY_ID, "Draft - not sent; offer-aligned v4 review",
                         f"{L.CONFIRM_2027} Offer terms: {'; '.join(copy['offer_ids'])} (data/reference/silverleaf-offer-register.json). "
                         "Confirm the sender, route, campus fit and organisation relevance before use. No guaranteed places, transport or outcomes. "
                         "One active recipient per organisation.", plan["message_id"]))
        for plan, org, track, route, copy, missing in new_rows:
            record = org_record.get(plan["organisation_id"])
            status = "Needs research" if track == "AQ00" else "Draft review"
            conditions = f"{L.CONFIRM_2027} {' '.join(missing)}".strip()
            is_contact = plan["target_type"] == "contact"
            con.execute("INSERT INTO messages (message_id, target_type, target_id, subject, body, strategy_id, status, conditions, source_record_id) "
                        "VALUES (?,?,?,?,?,?,?,?,?)",
                        (plan["message_id"], plan["target_type"], plan["target_id"], copy["subject"], copy["body"], STRATEGY_ID,
                         "Draft - not sent; offer-aligned v4 review", conditions, record))
            modules = "VM01; VM02; VM03; VM06; VM19" if plan["segment"] == "SACCOS members" else "VM01; VM02; VM03; VM04; VM05; VM19"
            con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, target_name, organisation_name, strategy_version,
                           segment, recipient_role, persona, contact_channel, channel_attribution, evidence_url, evidence_date, verified_on, evidence_basis,
                           evidence_record_ids, relevance_reason, proposed_offer, cta_type, flow_id, review_status, missing_information, selection,
                           subject, body, follow_up_1, follow_up_2, hook_status, campaign_copy_status, acquisition_version, acquisition_track_id,
                           value_module_ids, strategy_scope, offer_version, offer_ids, offer_evidence, offer_message_sw)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (plan["message_id"], plan["target_id"], plan["target_type"], plan["organisation_id"], plan["target_name"], org["name"], "offer-v4",
                         plan["segment"], plan.get("recipient_role", "Organisation routing"), "Named contact" if is_contact else "Employer route", route or "",
                         ("Published route of the named contact or organisation in the master" if is_contact else "Organisation's published route in the master")
                         if route else "", org.get("source_url") or "", "", TODAY, "reference_file", record or "",
                         (f"Named {plan.get('recipient_role') or 'contact'} at {org['name']}, as the organisation publishes it; staff school-fee benefit and family offer."
                          if is_contact else f"Employer in the lead list ({org.get('segment') or 'unclassified'}); staff school-fee benefit and family offer."),
                         offer_summary(copy["offer_ids"]), plan["cta_type"], "F03" if plan["segment"] == "SACCOS members" else "F01", status,
                         "; ".join([*missing, L.CONFIRM_2027]), plan.get("selection", "Candidate for review"), copy["subject"], copy["body"],
                         copy["follow_up_1"], copy["follow_up_2"], "No hook: offer-led opening", "Draft; offer-aligned v4 (offer register); not sent",
                         "2026-09-09-new-contact-acquisition-v4", track, modules,
                         "New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the acquisition track controls cadence.",
                         L.OFFER_VERSION, "; ".join(copy["offer_ids"]), evidence, copy.get("sw", "")))
            con.execute("INSERT OR REPLACE INTO campaign_lead_assignments (assignment_id, campaign_id, target_type, target_id, message_id, selection, "
                        "eligibility_status, reason, next_action, acquisition_track_id, value_module_ids, strategy_scope) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sid("A", "offer-v4", plan["message_id"]), "C02" if plan["segment"] == "SACCOS members" else "C01", plan["target_type"],
                         plan["target_id"], plan["message_id"], plan.get("selection", "Candidate for review"),
                         "Needs research" if track == "AQ00" else ("Alternative - inactive" if is_contact else "Candidate after checks"),
                         "Offer-aligned v4 draft for a named contact without a plan" if is_contact else "Offer-aligned v4 draft for an organisation without a plan",
                         "Resolve route and owner" if track == "AQ00" else ("Human review; choose one recipient per organisation" if is_contact
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
                    (STRATEGY_ID, "Offer-aligned outreach (documented Silverleaf offer)", "All organisation and parent drafts",
                     "Messages lead with the documented offer for the audience: employers get the staff school-fee benefit (OF04) and the family offer; "
                     "SACCOS get the family offer and the member-association rate; Rivertrees gets its 2025 terms. A recipient hook appears only when verified; "
                     "otherwise the message opens with the offer. Terms: data/reference/silverleaf-offer-register.json.",
                     "Draft; PE025-PE028; confirm 2027 terms before sending"))
        for segment, (audience, offer, qualification) in NEW_SEGMENTS.items():
            if not con.execute("SELECT 1 FROM outreach_segments WHERE segment=?", (segment,)).fetchone():
                con.execute("INSERT INTO outreach_segments VALUES (?,?,?,?,?)", (segment, audience, offer, qualification, "F01"))
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


def merge_notes(existing, notes) -> str:
    """Add notes to a '; '-separated field without repeating any, so re-running the script changes nothing."""
    parts = [x.strip() for x in str(existing or "").split("; ") if x.strip()]
    for note in notes:
        if note and note not in parts:
            parts.append(note)
    return "; ".join(parts)


def offer_summary(ids) -> str:
    return "; ".join(f"{i} {L.OFFERS[i]['name']}" for i in ids)


if __name__ == "__main__":
    raise SystemExit(main())
