#!/usr/bin/env python3
"""Write the company master's outreach drafts: a request first, then Silverleaf's documented offer.

Reads data/reference/silverleaf-offer-register.json and the master (outputs/master/Silverleaf Master Database.sqlite).
- Every existing outreach plan gets a request-first sequence (strategy S-request-first-v5, 23 September 2026). Its
  message_id, target, acquisition track and call to action are kept.
  - The first message names the purpose, introduces the sender (Mariam Haji, Marketing and Partnership Coordinator)
    and asks for a short meeting. It states no offer terms. For employers the purpose is a partnership to provide an
    education benefit for the children of staff; on a plan that routes, the second touch asks who is best to speak to
    about staff welfare or benefits.
  - The offer message (outreach_plans.offer_message) states the offer register's terms. AQ02 sends it as follow-up 1;
    on AQ01 it is the reply once someone names the right colleague. AQ01 otherwise sends one routing check-in.
  - Earlier copies are saved in message_versions first: '2026-09-23-before-offer-v4' (the pre-offer copy) and
    '2026-09-23-before-request-first' (the offer-led copy).
- Master organisations with no plan get one, unless they belong to another track or are excluded: local
  administration offices are in the government run, excluded offices (party, court, police, religious) get none.
  New plans are AQ01 when the organisation has a public email or phone and AQ00 (hold) otherwise.
- On every rewrite, an organisation plan's two creation-time holds are checked against the organisation as it is now
  (refresh_creation_holds, 11 October 2026): the map-only note goes once the lead is matched (verification no longer
  'Raw OSM', add_gap_census_leads.py --matches), and the no-route note goes once the organisation has a published email or
  phone (the contact merge). A plan held by nothing else returns to 'Draft review' on its track (AQ01 or AQ02, as
  refresh_acquisition_metadata.py sets it), with the organisation's route as its channel; any other hold stays.
- First touch (docs/strategy/partnership-pipelines.md section 4, approved 11 October 2026; scripts/messaging/first_touch.py):
  by the route each plan can reach (export_resend_contacts.first_touch_case), a named decision-maker at their own or their role's
  address keeps the letter (case A); a named decision-maker reached only through a general inbox gets the Attn subject and routing line
  (case B, with ', or your HR lead' under question 21's rule); no named decision-maker gets the short redirect request with blank
  follow-ups and the planned next touch as a note (case C). The segment row decides the wording: employers, variant A sponsors (their
  content stays sponsorship), public bodies, introducers. SACCOS and Rivertrees are unchanged; VICOBA plans have their own kinds (below). A stored variant draft
  (variant_subject/variant_body, which the exporter sends) gets the same format; its untouched text is kept in variant_subject_base and
  variant_body_base, so run this after assign_message_variants.py.
- Named-person fallout (pipeline draft section 5, applied 11 October 2026): a case B plan for an employer, public body or introducer is
  on AQ02 (Day 0, +4, +4 working days: the Attn request, the offer, the close; track_for, as refresh_acquisition_metadata.py sets it,
  unless it is held on AQ00). Follow-up 1 is the offer message ('Following up on my earlier note ...'), follow-up 2 a short close ending
  with the segment's redirect-style ask (first_touch.close), and a plan with an escalation contact notes 'Then: one message to <recipient>
  5 working days after the close'; nothing is drafted to them. Variant A sponsorship, case A, case C, savings groups and Rivertrees are
  unchanged. A copy this changes is saved first as '2026-10-11-before-named-fallout'.
- Offer-terms note (12 October 2026): the user confirmed the terms come from Silverleaf's discount schedule, so every plan carries
  offer_lib.OFFER_TERMS_NOTE (terms from the schedule; check with Finance before the first send) in place of the 2027 Finance
  condition, which is dropped from the notes. The note holds nothing. A copy this changes after both earlier labels are taken is
  saved as '2026-10-12-before-offer-note'.
- Group rate (13 October 2026): the user decided that OF07, the discount schedule's group rate, applies to savings groups
  generally (SACCOS and VICOBAs), so the SACCOS offer message states it with all three steps, and the note that Finance must
  extend it is dropped from the plans (OBSOLETE_NOTES). A copy a register change alters is saved first under the label
  '<register date>-before-offer-v<n>' (offer_backup_label).
- VICOBA savings groups (docs/plans/vicoba-integration-plan.md decisions 3 to 6, approved 13 October 2026): every 'VICOBA members'
  plan (one per group, created by scripts/master/add_vicoba_groups.py) gets the Kiswahili group request, a check-in, a close and the
  Kiswahili offer (the family offer and OF07 in the register's words), stored Kiswahili-first: subject, body and follow-ups in Kiswahili,
  the English meaning in english_meaning, the Kiswahili offer in offer_message_sw and its meaning in offer_message, language 'sw'. The
  campus line states no distance at 'ward' precision. The band comes from first_touch.vicoba_assess/vicoba_case, which read the band
  properties scripts/master/link_vicoba_introducers.py writes (never the intake's proposed introducer; a group the linker has not run
  for is low) and which the exporter and the call sheet share: a plan is 'Draft review' only in a high band with nothing held, and every
  Kiswahili draft carries NATIVE_REVIEW until its template version is approved in data/reference/kiswahili-reviews.json. One 'VICOBA
  introducers' plan per master introducer (NGO field office, bank branch, or the employer of a workplace group), reusing the plan
  link_vicoba_introducers.py --add-introducers created, in English with no terms, naming its linked groups (fact covers_groups on the
  introducer, '<wave>: <ids>', --vicoba-wave, default W1); it is held while no group is linked, while its introducer_state is not
  'active', and while it is in an employer conversation (until that conversation's S4 meeting). Women's groups come first in wave order, and their notes carry the talk focus on mothers' questions.
  CDO introducers are reached through the government run's ward letters (draft_run_messages.py, kind vicoba_introduction).
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

import sys

import offer_lib as L

sys.path.insert(0, str(L.ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402  (contact verification and role ranking)
import add_vicoba_groups as V  # noqa: E402  (the VICOBA contract: next actions by record status)
sys.path.insert(0, str(L.ROOT / "scripts" / "contacts"))
from merge_master_contacts import BLOCKER, drop_note  # noqa: E402  (the same holds as the contact merge)
import export_resend_contacts as X  # noqa: E402  (the route and recipient tests the segments use, for the first-touch case)
import first_touch as F  # noqa: E402  (the approved first-touch formats)

ROOT = L.ROOT
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE_DB = ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"
GOVERNMENT_DB = ROOT / "outputs" / "runs" / "arusha-government-2026-09" / "lead-database.sqlite"
BACKUP_VERSION = "2026-09-23-before-offer-v4"
REQUEST_FIRST_BACKUP = "2026-09-23-before-request-first"
REDRAFT_BACKUP = "2026-10-01-before-partnership-wording"  # the copy before the employer first message became a partnership request
# The copy before the case B follow-ups followed the named-person fallout (11 October 2026); later changes are saved under this label too,
# because message_versions keeps the first copy saved under a label and the 1 October label is already taken for these plans.
FALLOUT_BACKUP = "2026-10-11-before-named-fallout"
# The copy before the 2027 Finance condition became the offer-terms note (12 October 2026), for plans whose two labels above are taken.
OFFER_NOTE_BACKUP = "2026-10-12-before-offer-note"
OFFER_STRATEGY_ID = "S-offer-aligned-v4"
STRATEGY_ID = "S-request-first-v5"
COPY_VERSION = "request-first-v5"
MESSAGE_STATUS = "Draft - not sent; request-first review"
TODAY = "2026-09-23"
# The sender is Mariam Haji for every draft; the 2027 Finance condition became the offer-terms note (12 October 2026); the
# group rate (OF07) applies to savings groups generally and needs no Finance extension (13 October 2026). The old OF07 note was
# merged part by part, so its two parts are listed as well as the whole.
OLD_GROUP_RATE_NOTE = "The member-association rate is documented for KINEFA only; Finance must agree to extend it before sending."
OBSOLETE_NOTES = {"replace sender name", L.OLD_CONFIRM_2027, OLD_GROUP_RATE_NOTE, *OLD_GROUP_RATE_NOTE.split("; ")}
# Variant A (sponsorship) plans: the register approves no follow-up for a sponsorship ask before a reply.
SPONSORSHIP_FOLLOW_UP_NOTE = ("Sponsorship follow-up awaiting approved copy (variant A: no staff-benefit follow-up, because the offer register "
                              "gives sponsorship rows no offer message until they reply).")
# The two holds a new plan gets from its organisation (below, in main). They describe the organisation when the plan was
# created, so each rewrite checks them against the organisation as it is now (decided 2026-10-11): a lead an enrichment round
# matched to a real organisation (verification no longer 'Raw OSM') is not held as map-only, and an organisation that now
# has a published email or phone is not held as contactless. A plan held only by these is released; any other hold stays.
NO_ROUTE_NOTE = "No public email or phone; find the organisation's route before any message."
RAW_OSM_NOTE = "Raw OpenStreetMap place: match it to a curated organisation first."
OTHER_HOLD = re.compile(BLOCKER.pattern + r"|Role not confirmed|No public email or phone|No published route", re.I)


def refresh_creation_holds(plan: dict, org: dict) -> tuple[dict, str]:
    """The plan with its creation-time holds brought up to date with the organisation, and what changed ('' for nothing,
    'notes' when a stale note was dropped but another hold remains, 'released' when the plan no longer has any hold)."""
    if plan["target_type"] != "organisation":
        return plan, ""
    notes = str(plan.get("missing_information") or "")
    route = org.get("email") or org.get("phone") or ""
    stale = [n for n, gone in ((RAW_OSM_NOTE, not str(org.get("verification") or "").startswith("Raw OSM")), (NO_ROUTE_NOTE, bool(route)))
             if gone and n in notes]
    if not stale:
        return plan, ""
    for note in stale:
        notes = drop_note(notes, note)
    plan = {**plan, "missing_information": notes}
    if plan["review_status"] != "Needs research" or OTHER_HOLD.search(notes):
        return plan, "notes"
    plan["review_status"] = "Draft review"
    # The track follows the status, exactly as scripts/master/refresh_acquisition_metadata.py sets it.
    plan["acquisition_track_id"] = "AQ01" if "referral" in str(plan.get("cta_type") or "").lower() else "AQ02"
    if not plan.get("contact_channel"):
        plan["contact_channel"] = route
        plan["channel_attribution"] = "Organisation's published route in the master (released when its lead was matched or its route found)"
    return plan, "released"
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
    (r"^Introducer", "Introducers"),
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
    """A draft states the nearest campus and its distance only from the organisation's own point (precision 'point').
    A locality, town, city or ward centre, a geocoded street or a P.O. box town is not the recipient's location, so a
    distance computed from it is not a fact about the recipient (13 October 2026): those drafts use the five-campus line."""
    return str(org.get("geocode_precision") or "") == "point" and org.get("distance_km") not in (None, "")


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


def employer_copy(plan: dict, org: dict, track: str, fallout: str = "", hr_named: bool = False) -> dict:
    """fallout is the first-touch kind of a case B plan ('employer' or 'public'; '' otherwise): its follow-ups follow the named-person
    fallout (pipeline draft section 5, applied 11 October 2026): follow-up 1 is the offer, follow-up 2 the close with a redirect-style ask."""
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Dear {L.greeting_name(plan['target_name'])}," if named else f"Dear {org_name} team,"
    staff = "local staff" if plan.get("segment") == "NGO employers" else "staff"
    extra = " It concerns your staff's own children, not student admissions." if plan.get("segment") == "Education employers" else ""
    hook = hook_sentence(plan)
    # The first message states the objective: a partnership to provide an education benefit for staff children (1 October 2026).
    # Who looks after staff welfare or benefits is the second touch, on a plan that routes.
    purpose = (f"We are looking to set up a partnership with {org_name} to provide an education benefit for the children of your {staff}.{extra}"
               f"{(' ' + hook) if hook else ''} I would welcome the chance to explain how it could work, and to discuss whether it might suit you and your team.")
    subject = f"A partnership on education benefits for {org_name} staff"
    body = f"{greet}\n\n{L.INTRO}\n\n{purpose}\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}"
    offer_cta = CTA.get(plan.get("cta_type") or "", CTA["Information offer"])
    if fallout:
        offer_cta = CTA["Information offer"] if "point me" in offer_cta else offer_cta
        follow_1 = employer_offer(greet, FOLLOW_UP_OPENER, org_name, staff, org, offer_cta)
        follow_2 = F.close(fallout, org_name, greet, hr_named)
    elif routing_plan(plan, track):
        follow_1 = (f"{greet}\n\nFollowing up on my note about a partnership to provide an education benefit for the children of {staff} at {org_name}. "
                    f"Who would be the best person to speak to about staff welfare or benefits? If it is not relevant, just say so and I will close this."
                    f"\n\n{L.SIGNATURE}")
        follow_2 = ""
        offer_cta = CTA["Information offer"] if "point me" in offer_cta else offer_cta
    else:
        follow_1 = employer_offer(greet, FOLLOW_UP_OPENER, org_name, staff, org, offer_cta)
        follow_2 = f"{greet}\n\nShould I send the one-page staff offer sheet for a quick look, or close this for now?\n\n{L.SIGNATURE}"
    offer = employer_offer(greet, REPLY_OPENER, org_name, staff, org, offer_cta)
    return {"subject": subject, "body": body, "follow_up_1": follow_1, "follow_up_2": follow_2, "offer_message": offer,
            "offer_ids": EMPLOYER_OFFERS, "sw": ""}


def introducer_copy(plan: dict, org: dict, track: str, fallout: str = "") -> dict:
    """An association, chamber or HR body that could share the staff benefit with its members (decided 2 October 2026). The first
    message asks for a partnership and a meeting and states no offer terms; the offer follows in the reply. A case B plan (fallout
    'introducer') follows the named-person fallout instead: follow-up 1 gives the member benefit, follow-up 2 closes asking who
    handles member benefits and communications (11 October 2026)."""
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    the = "" if org_name.split()[0].isupper() else "the "  # 'the Association of Tanzania Employers', but 'TNCC Arusha Regional Chamber'
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Dear {L.greeting_name(plan['target_name'])}," if named else f"Dear {org_name} team,"
    subject = f"A partnership on education benefits for members of {the}{org_name}"
    body = (f"{greet}\n\n{L.INTRO}\n\nWe are looking to set up a partnership with {the}{org_name} so that its members can offer an education benefit "
            f"for the children of their staff. I would welcome the chance to explain how it could work, and to discuss whether {the}{org_name} might share "
            f"it with members, for example in a member bulletin or at a members' or HR forum.\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}")
    follow_1 = (f"{greet}\n\nFollowing up on my note about a partnership so that members of {the}{org_name} can offer an education benefit for the children of "
                f"their staff. Who would be the best person to speak to about member benefits or communications? If it is not relevant, just say so and "
                f"I will close this.\n\n{L.SIGNATURE}")

    def offer_text(opener: str) -> str:
        return (f"{greet}\n\n{opener} Silverleaf Academy would like to offer the staff of {the}{org_name}'s member organisations {L.EN['OF04']}. Every Silverleaf family "
                f"can also get {L.family_offer_en()}.\n\n{LEVELS_EN} {CAMPUSES_EN}\n\n{(the + org_name)[:1].upper() + (the + org_name)[1:]} would only share the offer with members; interested parents "
                f"deal with our admissions team directly, and applications for the 2027 school year are open. We can provide a one-page note for your bulletin "
                f"or forum.\n\n{CTA['Information offer']}\n\n{L.SIGNATURE}")

    follow_2 = ""
    if fallout:
        follow_1, follow_2 = offer_text(FOLLOW_UP_OPENER), F.close(fallout, f"{the}{org_name}", greet)
    return {"subject": subject, "body": body, "follow_up_1": follow_1, "follow_up_2": follow_2, "offer_message": offer_text(REPLY_OPENER),
            "offer_ids": EMPLOYER_OFFERS, "sw": ""}


def saccos_copy(plan: dict, org: dict, track: str) -> dict:
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    named = plan.get("target_type") == "contact" and plan.get("target_name")
    greet = f"Dear {L.greeting_name(plan['target_name'])}," if named else f"Dear {org_name} committee,"
    hook = hook_sentence(plan)
    body = (f"{greet}\n\nI am writing to explore how Silverleaf Academy could support the education of {org_name} members' children, and "
            f"would like to speak with your committee.{(' ' + hook) if hook else ''}\n\n{L.INTRO}\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}")

    def offer_text(opener: str) -> str:
        return (f"{greet}\n\n{opener} Every Silverleaf family can get {L.family_offer_en()}. We also offer savings groups "
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


# ------------------------------------------------------------------ VICOBA (docs/plans/vicoba-integration-plan.md decisions 3 to 6)
# Kiswahili is the message and English its meaning for review (decision 6): subject, body and the follow-ups hold Kiswahili,
# english_meaning their English meaning, offer_message_sw the Kiswahili offer and offer_message its English meaning; language 'sw'.
# Each Kiswahili template has an ID and a version (offer_lib.template_version of its text); a draft built from it carries NATIVE_REVIEW
# until data/reference/kiswahili-reviews.json records that version as approved. Placeholders are filled from the record.
RUN_CONFIG = ROOT / "data" / "runs" / "arusha-government-2026-09" / "run-config.json"
COUNCILS_SW = ({c["name"]: c.get("name_sw") or c["name"] for c in json.loads(RUN_CONFIG.read_text(encoding="utf-8"))["councils"]}
               if RUN_CONFIG.exists() else {})
SIGN_EN = f"With respect,\n{L.SENDER}\n{L.SENDER_TITLE}, Silverleaf Academy\nP.O. Box 14146, Usa River · +255 769 486 660 · info@silverleaf.co.tz"
VICOBA_TEMPLATES = F.VICOBA_TEMPLATES  # the reviewed Kiswahili templates live with the band rule (first_touch.py)
# The English meaning of each template, for review only (never sent, so not versioned).
VICOBA_MEANINGS = {
    "vicoba-group-request": (
        "Request for a short meeting with the committee of {group}",
        "{address}Hello, Committee of {group},\n\nI am writing about the education of the children of {group}'s members. We would like to ask "
        "for 10 to 15 minutes at one of your weekly meetings, to talk in Kiswahili about getting children ready for school and planning their "
        "education.\n\n" + L.INTRO + "\n\nWould it be possible to arrange a short meeting with the committee, in person or by phone, so that we "
        "can agree a suitable day?\n\n" + SIGN_EN),
    "vicoba-group-follow-up": (
        "", "Hello, Committee of {group},\n\nI am following up my letter asking for 10 to 15 minutes at one of your weekly meetings, to talk in "
        "Kiswahili about getting children ready for school. Would the committee like that? If so, please let us know the day and time you "
        "meet.\n\n" + SIGN_EN),
    "vicoba-group-close": ("", "Hello, Committee of {group},\n\n" + F.CLOSE_SW["vicoba"][1] + "\n\n" + SIGN_EN),
    "vicoba-group-offer": (
        "", "Hello, Committee of {group},\n\nThank you for your reply. For every Silverleaf family we offer " + L.family_offer_en() + ".\n\n"
        "Savings groups also have a group rate. " + L.of07_en() + "\n\n{campus}\n\nCan we agree a day to speak to members at your weekly "
        "meeting?\n\n" + SIGN_EN),
}
GROUP_TEMPLATES = tuple(VICOBA_TEMPLATES)
VICOBA_WAVE = "W1"
VICOBA_GROUP_MODULES = "VM02; VM03; VM06; VM20; VM19"  # decision 4: VM19 once an offer message exists (every group draft has one)
VICOBA_INTRODUCER_MODULES = "VM02; VM03; VM20"         # an introducer request states no terms
VICOBA_TALK_NOTE = ("Talk focus (women's group, section 0): the talk is aimed at mothers' questions (the curriculum, children's safety, "
                    "transport, and how fees are paid: OF09's four instalments, while due dates set to a share-out would need Finance, F2), "
                    "with the same offer and drafts as every group.")
VICOBA_WAITING = "Waiting on the introducer request "
VICOBA_EMPLOYER_HOLD = ("The introducer is already in an employer conversation: raise the savings-group introduction at that conversation's "
                        "S4 meeting, never as its first message or a second cold message (decision 4).")
VICOBA_NO_GROUPS = "No group in this wave is complete yet: the request waits for a group whose record is complete."
VICOBA_NO_ROUTE = "The introducer publishes no email or phone: find its route first."
# The placeholder note link_vicoba_introducers.py --add-introducers writes on a new introducer plan; it goes once the request is drafted.
VICOBA_INTRODUCER_PENDING = "Introducer request pending: draft_master_messages.py writes it (no terms in the request)."
VICOBA_DRAFT_PENDING = "VICOBA draft pending: the Kiswahili group request is written by draft_master_messages.py."
# Notes a VICOBA rewrite replaces (the plan notes too, so they always follow the VICOBA notes and a re-run keeps the same order).
VICOBA_NOTE_PREFIXES = ("VICOBA band: ", "VICOBA wave ", "Talk focus (women's group", VICOBA_WAITING, "Record incomplete", "Record stale",
                        "Record complete", "Also a welfare lead", "Introducer state: ", "No group is linked to this introducer yet")
VICOBA_NOTES = {L.NATIVE_REVIEW, L.OFFER_TERMS_NOTE, VICOBA_DRAFT_PENDING, VICOBA_INTRODUCER_PENDING, VICOBA_EMPLOYER_HOLD, VICOBA_NO_GROUPS, VICOBA_NO_ROUTE,
                F.NEXT_TOUCH["vicoba"], F.NEXT_TOUCH["vicoba_introducer"]}
DISTANCE_CLAIM = re.compile(r"\bkm\b|\bkilomita\b|\bkilometres?\b", re.I)


def template_versions() -> dict:
    """{template_id: version} for the VICOBA Kiswahili templates; a version covers the template text and the fixed sentences it inserts."""
    return F.vicoba_template_versions()


def vicoba_address(facts: dict, lang: str) -> str:
    """The address block above a group letter: 'Kwa: Mwenyekiti na Kamati ya <group>,\\nKata ya <ward>, <council>.' (as published)."""
    ward, council = F._last(facts, "ward"), F._last(facts, "council")
    if lang == "sw":
        place = ", ".join(x for x in (f"Kata ya {ward}" if ward else "", COUNCILS_SW.get(council, council)) if x)
        return f"Kwa: Mwenyekiti na Kamati ya {{group}},\n{place}.\n\n" if place else "Kwa: Mwenyekiti na Kamati ya {group}.\n\n"
    place = ", ".join(x for x in (f"{ward} ward" if ward else "", council) if x)
    return f"To: the Chair and Committee of {{group}},\n{place}.\n\n" if place else "To: the Chair and Committee of {group}.\n\n"


def vicoba_copy(plan: dict, org: dict, info: dict) -> dict:
    """The Kiswahili group request, follow-up, close and offer for a VICOBA group (decision 6, samples a and e), with their English meaning.
    The first message states no terms; the offer message states the family offer and the group rate (OF07) in the register's words. The
    campus line names the nearest campus with a distance only from a public venue's point; at ward precision it is the five-campus line."""
    group = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    facts = info["group"].get("facts", {})
    if precise(org):
        campus_sw = L.campus_line_sw(org.get("campus") or "", org.get("distance_km"), True, "mahali pa vikao vyenu")
        campus_en = L.campus_line_en(org.get("campus") or "", org.get("distance_km"), True, "your meeting place")
    else:
        campus_sw, campus_en = L.network_line_sw(), L.network_line_en()

    def fill(text: str, lang: str) -> str:
        return text.replace("{address}", vicoba_address(facts, lang)).replace("{group}", group).replace("{campus}", campus_sw if lang == "sw" else campus_en)

    sw = {tid: (fill(s, "sw"), fill(b, "sw")) for tid, (s, b) in VICOBA_TEMPLATES.items()}
    en = {tid: (fill(s, "en"), fill(b, "en")) for tid, (s, b) in VICOBA_MEANINGS.items()}
    first_en = en["vicoba-group-request"][1]
    meaning = (f"Subject: {en['vicoba-group-request'][0]}\n\n{first_en}\n\n— Follow-up 1 —\n\n{en['vicoba-group-follow-up'][1]}"
               f"\n\n— Follow-up 2 (the close) —\n\n{en['vicoba-group-close'][1]}")
    return {"subject": sw["vicoba-group-request"][0], "body": sw["vicoba-group-request"][1], "follow_up_1": sw["vicoba-group-follow-up"][1],
            "follow_up_2": sw["vicoba-group-close"][1], "offer_message": en["vicoba-group-offer"][1], "sw": sw["vicoba-group-offer"][1],
            "english_meaning": meaning, "first_en": first_en, "language": "sw", "offer_ids": L.VICOBA_OFFERS,
            "first_fields": ("body", "first_en"), "sw_approved": info["approved"], "value_module_ids": VICOBA_GROUP_MODULES,
            "conditions": vicoba_conditions(L.VICOBA_OFFERS, kiswahili=True)}


def vicoba_area(groups: list) -> str:
    """Where the covered groups meet, as their records name it: one ward, else one council, else 'Arusha and Kilimanjaro'."""
    wards = {(F._last(g["facts"], "ward"), F._last(g["facts"], "council")) for g in groups}
    if len(wards) == 1 and next(iter(wards))[0]:
        return f"{next(iter(wards))[0]} ward"
    councils = {c for _, c in wards if c}
    return next(iter(councils)) if len(councils) == 1 else "the Arusha and Kilimanjaro area"


def name_list(names: list) -> str:
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


def vicoba_introducer_copy(plan: dict, org: dict, request: str, groups: list) -> dict:
    """The introducer request (decision 6, samples b and c; English; no terms): an NGO field office is asked to introduce Silverleaf to
    one or two of the group committees its programme works with (named from the groups' sources); a bank branch to pass a note to group
    committees, naming none (it cannot share customer information); an employer, at its S4 meeting, to introduce its staff group's
    committee. None asks for a member list."""
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    area = vicoba_area(groups)
    names = [L.display_name(g["name"], g["organisation_id"]) for g in groups][:5]
    if request == "bank":
        subject = "Savings groups at your branch – a short note for their committees"
        body = ("Dear Branch Manager,\n\nI am writing from Silverleaf Academy in Arusha. Many savings groups plan for their members' school costs, "
                "and we would like to offer group committees a short talk in Kiswahili at one of their own meetings, on getting children ready "
                "for school.\n\nWe understand the branch cannot share customer information, and we do not ask for any. Would you be willing to "
                "pass a one-page note to group committees when they visit, or tell us who at the branch looks after group accounts?"
                f"\n\n{L.SIGNATURE}")
    elif request == "employer":
        subject = "Your staff savings group – a short talk for its committee"
        body = (f"Dear {org_name} team,\n\nAs part of our conversation about an education benefit for your staff, we would like to offer the "
                f"committee of {name_list(names)} a short talk in Kiswahili at one of its own meetings, on getting children ready for school "
                "and planning for their education.\n\nCould you introduce us to the group's committee, or tell us who looks after staff "
                "welfare? We do not ask for member lists or any member's details; the group decides for itself."
                f"\n\n{L.SIGNATURE}")
    else:
        subject = f"Savings groups in {area} – could you introduce us?"
        known = f" The groups we know of from published sources include {name_list(names)}." if names else ""
        body = (f"Hello,\n\nI am writing from Silverleaf Academy in Arusha. We would like to offer the savings groups your programme works with "
                f"in {area} a short talk in Kiswahili, at one of their regular meetings, on getting children ready for school and planning for "
                f"their education.{known}\n\n{F.SEGMENTS['vicoba_introducer'][3]}\n\n{F.SIGN_OFF}")
    return {"subject": subject, "body": body, "follow_up_1": "", "follow_up_2": "", "offer_message": "", "sw": "", "english_meaning": "",
            "language": "en", "offer_ids": [], "value_module_ids": VICOBA_INTRODUCER_MODULES,
            "conditions": vicoba_conditions([], kiswahili=False)}


def vicoba_conditions(offer_ids, kiswahili: bool) -> str:
    """The release conditions of a VICOBA draft; the same on every run."""
    terms = (f"{L.REQUEST_FIRST} {L.OFFER_TERMS_NOTE} Offer terms: {'; '.join(offer_ids)} (data/reference/silverleaf-offer-register.json). "
             if offer_ids else "An introducer request: it states no offer terms; the offer goes to the group's committee after it replies. ")
    return (terms + ("Kiswahili: native-speaker review of the template version before release. " if kiswahili else "")
            + "Group-level only: never ask for or accept a member list, members' names or phones, savings or loans. No unannounced visit to a "
              "meeting; no photographs, gifts or payments. No loan, subsidy or fee-financing claim. One request per introducer per wave.")


def vicoba_plan_state(plan: dict, case: dict, info: dict, introducer_plan: str) -> tuple[str, list]:
    """(review_status, notes) of a VICOBA group plan: 'Draft review' only in a high band (case A or B) with nothing held; the band
    note, wave position and, for women's groups, the talk focus. A medium group waits on its introducer's request."""
    # Each note is one '; '-free item, so the next run replaces it instead of keeping stale parts.
    notes = [f"VICOBA band: {case['band']}" + (f" (case {case['case']}, channel {case['channel']})" if case["case"] else "")
             + (f" · held: {' / '.join(case['holds'])}" if case["holds"] else "")
             + (f" · once the template is approved: {case['band_after_review']}" if case["band_after_review"] != case["band"] else ""),
             f"VICOBA wave {info['wave']}: position {info['position']} of {info['wave_size']} (women's groups first)"]
    status = info["group"].get("record_status") or ""
    if status and status != "complete":
        notes.append(f"Record {status}: {V.NEXT_ACTION.get(status, '')}".rstrip(": "))
    if info["group"].get("women_group"):
        notes.append(VICOBA_TALK_NOTE)
    if not info["approved"]:
        notes.append(L.NATIVE_REVIEW)
    if case["case"] == "C" and introducer_plan:
        notes.append(f"{VICOBA_WAITING}({introducer_plan}).")
    ready = case["band"] in ("high-direct", "high-indirect") and not case["holds"]
    return ("Draft review" if ready else "Needs research"), notes


def vicoba_channel(info: dict) -> str:
    """The plan's channel attribution: the group has no route of its own, so this says how the first touch reaches it."""
    intro, case = info["introducer"], info["case"]
    how = {"A": "a Kiswahili call to the officer's published role route, then the letter 'as discussed'",
           "B": "the Kiswahili letter to the committee, handed over by the introducer",
           "C": "the introducer request first; the group letter follows the introduction"}.get(case["case"], "none yet (held)")
    who = f"{intro['kind'] or 'no introducer'}" + (f": {intro['name']}" if intro.get("name") else "")
    return f"VICOBA group-level record with no route of its own. First touch: {how}. Introducer: {who}."


def vicoba_missing(existing: str, notes: list) -> str:
    """The plan's notes with every VICOBA-managed note replaced by the current ones (so an approval or a new band takes effect)."""
    kept = [n for n in str(existing or "").split("; ") if n.strip() and n.strip() not in VICOBA_NOTES
            and not n.strip().startswith(VICOBA_NOTE_PREFIXES)]
    return merge_notes("; ".join(kept), notes)


def vicoba_context(con, wave: str) -> dict:
    """Everything the VICOBA drafts need: each group's band (first_touch.vicoba_assess, from the band properties
    scripts/master/link_vicoba_introducers.py writes; the exporter and call sheet share the rule), its introducer and wave position, and
    one introducer plan per master introducer per wave (NGO field office, bank branch or employer), its linked groups in wave order. An
    introducer plan another script created (link_vicoba_introducers.py --add-introducers) is the introducer's plan: it is rewritten,
    never doubled."""
    row_factory = con.row_factory
    con.row_factory = sqlite3.Row
    try:
        groups = V.load_vicoba_groups(con)
        con.row_factory = sqlite3.Row
        orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT organisation_id, name, segment, email, phone FROM organisations")}
        existing = {}
        for oid, mid in con.execute("SELECT organisation_id, message_id FROM outreach_plans WHERE segment=? ORDER BY message_id",
                                    (L.VICOBA_INTRODUCER_SEGMENT,)):
            existing.setdefault(oid, mid)
        org_facts = {}
        for oid, field, value in con.execute("SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' AND field IN "
                                             "('introducer_state', 'group_account_product') ORDER BY rowid"):
            org_facts.setdefault(oid, {})[field] = value
    finally:
        con.row_factory = row_factory
    order = V.wave_order(groups)
    approved = F.vicoba_templates_approved()
    by_group, introducers = {}, {}
    for position, gid in enumerate(order, 1):
        case = F.vicoba_assess(groups[gid], template_approved=approved)
        intro = case["introducer"]
        by_group[gid] = {"group": groups[gid], "introducer": intro, "case": case, "approved": approved, "position": position,
                         "wave_size": len(order), "wave": wave}
        if intro["status"] == "linked" and intro["organisation_id"] in orgs and intro["request"]:
            entry = introducers.setdefault(intro["organisation_id"], {"request": intro["request"], "groups": [], "women": False})
            entry["groups"].append(groups[gid])
            entry["women"] |= bool(groups[gid].get("women_group"))
    for oid in existing:  # an introducer with a plan but no linked group yet keeps its plan, held
        if oid in orgs and oid not in introducers:
            introducers[oid] = {"request": "bank" if org_facts.get(oid, {}).get("group_account_product") else "ngo", "groups": [], "women": False}
    # Introducers that cover a women's group come first, then the nearest group's distance (section 0).
    ranked = sorted(introducers, key=lambda oid: (not introducers[oid]["women"],
                                                  min((float(g.get("distance_km")) for g in introducers[oid]["groups"] if g.get("distance_km") not in (None, "")), default=9e9),
                                                  orgs[oid]["name"]))
    for i, oid in enumerate(ranked, 1):
        introducers[oid].update(message_id=existing.get(oid) or sid("M", "vicoba-introducer", oid), position=i, wave_size=len(ranked), wave=wave,
                                state=org_facts.get(oid, {}).get("introducer_state", ""))
    for info in by_group.values():
        oid = info["introducer"]["organisation_id"]
        info["introducer_plan"] = introducers[oid]["message_id"] if oid in introducers else ""
    return {"groups": by_group, "introducers": introducers, "versions": template_versions(), "approved": approved, "wave": wave, "orgs": orgs}


INTRODUCER_STATE_HOLDS = {
    "to_confirm": "Introducer state: to confirm (its savings-group work is not confirmed).",
    "outside_region": "Introducer state: outside the region (no introducer route in the catchment).",
    "employer_conversation_first": VICOBA_EMPLOYER_HOLD,
    "welfare_conversation_first": "Introducer state: in its welfare-run conversation (raise savings groups there, never a second cold message).",
}
VICOBA_NO_LINK = "No group is linked to this introducer yet (data/reference/vicoba-introducers.json)."


def vicoba_introducer_state(oid: str, entry: dict, org: dict, other_plans: bool) -> tuple[str, list]:
    """(review_status, notes) of an introducer plan: held while no group is linked to it, while its introducer_state is not 'active'
    (to confirm, outside the region, another conversation first), while it is in an employer conversation (decision 4), always for an
    employer (the request belongs to its S4 meeting), without a route, or while none of its groups is complete."""
    covered = ", ".join(f"{g['name']} ({g['organisation_id']})" for g in entry["groups"]) or "no group yet"
    notes = [f"VICOBA wave {entry['wave']}: introducer {entry['position']} of {entry['wave_size']} (introducers of women's groups first), "
             f"covering {covered}"]
    if not entry["groups"]:
        notes.append(VICOBA_NO_LINK)
    if entry.get("state") in INTRODUCER_STATE_HOLDS:
        notes.append(INTRODUCER_STATE_HOLDS[entry["state"]])
    if (other_plans or entry["request"] == "employer") and VICOBA_EMPLOYER_HOLD not in notes:
        notes.append(VICOBA_EMPLOYER_HOLD)
    if not (org.get("email") or org.get("phone")):
        notes.append(VICOBA_NO_ROUTE)
    if entry["groups"] and not any(g.get("record_status") == "complete" for g in entry["groups"]):
        notes.append(VICOBA_NO_GROUPS)
    held = len(notes) > 1
    return ("Needs research" if held else "Draft review"), notes


def rivertrees_copy(org: dict) -> dict:
    greet = "Dear Rivertrees team,"
    body = (f"{greet}\n\nIn 2025 Silverleaf Academy proposed a Corporate Education Benefit Partnership for Rivertrees staff. Applications for the "
            f"2027 school year are now open, and we would like to renew it.\n\n{L.INTRO}\n\nWould it be possible to arrange a short meeting, either "
            f"in person or by phone, to go through the terms and how you would like to share them with your staff?\n\n{L.SIGNATURE}")

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
def decision_maker(contact: dict) -> bool:
    """A verified named decision-maker, as resolve_master_recipients.py counts one (published or confirmed, full name, senior role)."""
    verification = contact.get("verification") or ""
    name = contact.get("name") or ""
    return bool(R.VERIFIED.search(verification) and not R.UNUSABLE.search(verification) and len(name.split()) >= 2
                and not re.search(r"\d|\?", name) and (R.role_rank(contact.get("role")) is not None or R.FALLBACK_OK.search(contact.get("role") or "")))


def email_route(contact: dict, org: dict) -> str:
    """The best email for a person: their own published address, else their role desk, else the company's own inbox (no free mail)."""
    for value in (contact.get("named_email"), contact.get("published_role_email"), contact.get("shared_email"), org.get("email")):
        found = sorted(R.emails(value))
        if found:
            return found[0]
    return ""


def emailed_channel(contact: dict, org: dict, channel: str) -> str:
    """A verified decision-maker whose draft would go to a phone is emailed instead (decided 10 October 2026): the email route
    comes first and the phone is kept after it, so a call or WhatsApp stays possible. Other channels are unchanged."""
    channel = channel or ""
    if "@" in channel or not decision_maker(contact):
        return channel
    email = email_route(contact, org)
    return "; ".join(x for x in (email, channel) if x) if email else channel


FIRST_TOUCH_NOTES = set(F.NEXT_TOUCH.values())


def first_touch_kind(plan: dict, org: dict) -> str:
    """The segment row of the first-touch rule (pipeline draft section 4), or '' for copy it leaves alone (SACCOS, Rivertrees). VICOBA
    plans have their own kinds, 'vicoba' and 'vicoba_introducer', whose case comes from first_touch.vicoba_case (decision 3b)."""
    if plan.get("segment") == L.VICOBA_GROUP_SEGMENT:
        return "vicoba"
    if plan.get("segment") == L.VICOBA_INTRODUCER_SEGMENT:
        return "vicoba_introducer"
    if plan.get("segment") in L.SAVINGS_SEGMENTS or str(org.get("name") or "").startswith("Rivertrees"):
        return ""
    if plan.get("segment") == "Introducers":
        return "introducer"
    if str(plan.get("message_variant") or "").startswith("A"):
        return "variant_a"
    return "public" if plan.get("segment") == "Public-sector employers" else "employer"


def touch_case(plan: dict, org: dict, ctx: dict) -> tuple[str, dict | None, str]:
    """(segment kind, the plan's contact, first-touch case 'A', 'B', 'C' or '') for a plan; ('', contact, '') for copy the rule leaves alone."""
    kind = first_touch_kind(plan, org)
    contact = ctx["contacts"].get(plan.get("target_id")) if plan.get("target_type") == "contact" else None
    if not kind:
        return "", contact, ""
    if kind == "vicoba":  # the group's band rule, not the email route (decision 3b)
        info = ctx.get("vicoba", {}).get("groups", {}).get(plan["organisation_id"])
        return kind, contact, info["case"]["case"] if info else ""
    if kind == "vicoba_introducer":  # the introducer request is the case C equivalent
        return kind, contact, "C"
    return kind, contact, X.first_touch_case(plan, org, contact, ctx["people_at"].get(plan["organisation_id"], []))


def fallout_kind(plan: dict, org: dict, ctx: dict) -> str:
    """The kind of a case B plan whose follow-ups follow the named-person fallout (employers, public bodies, introducers), else ''.
    Variant A sponsors are left out: their follow-ups stay blank until sponsorship follow-up copy is approved."""
    kind, _, case = touch_case(plan, org, ctx)
    return kind if case == "B" and kind in F.NAMED_FALLOUT_KINDS else ""


def track_for(plan: dict, fallout: str) -> str:
    """The plan's acquisition track, as scripts/master/refresh_acquisition_metadata.py sets it: AQ00 while held; AQ02 for a case B plan
    (decided 11 October 2026: its three touches, the Attn request, the offer and the close, are AQ02's Day 0, +4 and +4 working days);
    otherwise AQ01 for a referral call to action and AQ02 for the rest."""
    if plan.get("review_status") == "Needs research":
        return "AQ00"
    if fallout:
        return "AQ02"
    return "AQ01" if "referral" in str(plan.get("cta_type") or "").lower() else "AQ02"


def apply_first_touch(plan: dict, org: dict, copy: dict, ctx: dict) -> tuple[dict, list, str]:
    """The plan's copy in its first-touch format (first_touch.py): unchanged for case A or no email route; the Attn format for case B;
    the redirect request with blank follow-ups for case C. Returns (copy, notes to add, case). The stored variant draft (variant A
    sponsorship or a personalised B), which the exporter sends instead of the body, gets the same format from its base text."""
    kind, contact, case = touch_case(plan, org, ctx)
    if not kind:
        return copy, [], ""
    if kind in F.VICOBA_KINDS:  # vicoba_copy and vicoba_introducer_copy already write the first touch; only the planned next touch is added
        return copy, [F.NEXT_TOUCH[kind]], case
    org_name = L.display_name(plan.get("organisation_name") or org.get("name"), plan.get("organisation_id"))
    notes, out = [], dict(copy)

    def shaped(subject: str, body: str) -> tuple[str, str]:
        if case == "B":
            lead = F.hr_lead(contact["role"], plan["organisation_id"] in ctx["hr_on_file"], ctx["reach"].get(plan["organisation_id"], ""),
                             org.get("headcount"), f"{org.get('segment') or ''} {plan.get('segment') or ''} {org.get('name') or ''}")
            return F.attn(kind, body, L.greeting_name(plan["target_name"]), contact["role"], lead)
        if case == "C":
            return F.redirect(kind, org_name)
        return subject, body

    out["subject"], out["body"] = shaped(copy["subject"], copy["body"])
    if case == "C":
        out["follow_up_1"], out["follow_up_2"] = "", ""
        notes.append(F.NEXT_TOUCH[kind])
    if plan.get("variant_body"):
        base_subject, base_body = plan.get("variant_subject_base") or "", plan.get("variant_body_base") or ""
        current = plan["variant_body"]
        if not (current.startswith(F.ROUTING_START) or F.is_redirect(current)) or not base_body:
            base_subject, base_body = plan.get("variant_subject") or "", F.strip_routing(current)  # a fresh draft from assign_message_variants.py
        out["_variant"] = (*shaped(base_subject, base_body), base_subject, base_body)
    return out, notes, case


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=str(MASTER))
    parser.add_argument("--dry-run", action="store_true", help="write runtime/messaging/master-preview.json and change nothing")
    parser.add_argument("--vicoba-wave", default=VICOBA_WAVE, help="the VICOBA wave label in the notes and covers_groups: one introducer "
                                                                   "plan per introducer, rewritten for each wave")
    args = parser.parse_args()
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans ORDER BY message_id")]
    messages = {r["message_id"]: dict(r) for r in con.execute("SELECT * FROM messages")}
    # First-touch context (pipeline draft section 4): contacts, each organisation's people, whether an HR head is on file, reach tiers.
    contacts_by_id = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    people_at, hr_on_file = {}, set()
    for c in contacts_by_id.values():
        if c["name"]:
            people_at.setdefault(c["organisation_id"], []).append(c["name"])
        if c["name"] and R.HR.search(c["role"] or ""):
            hr_on_file.add(c["organisation_id"])
    try:
        reach = {r[0]: r[1] for r in con.execute("SELECT organisation_id, tier FROM employer_reach")}
    except sqlite3.OperationalError:
        reach = {}
    ctx = {"contacts": contacts_by_id, "people_at": people_at, "hr_on_file": hr_on_file, "reach": reach}
    # VICOBA (decisions 3 to 6): each group's band, introducer and wave position, and one introducer plan per introducer per wave.
    vicoba = vicoba_context(con, args.vicoba_wave)
    con.row_factory = sqlite3.Row
    ctx["vicoba"] = vicoba
    vicoba_plans = {p["message_id"] for p in plans if p["segment"] in L.VICOBA_SEGMENTS}
    other_plans = {p["organisation_id"] for p in plans if p["segment"] not in L.VICOBA_SEGMENTS}
    first_touch_cases = Counter()
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

    updates, backups, outcomes, new_rows, track_moves = [], [], Counter(), [], []
    released = Counter()
    for plan in plans:
        org = orgs.get(plan["organisation_id"], {})
        original = plan  # the plan as stored, for its backup (the changes below go into new dicts)
        plan, change = refresh_creation_holds(plan, org)
        if change:
            outcomes[f"stale creation holds dropped ({change})"] += 1
            if change == "released":
                released[f"{plan['selection']}: {plan['segment']}"] += 1
        # VICOBA (decisions 3 to 6): the band decides the status before the track does; the VICOBA notes are replaced, never repeated.
        vicoba_entry = None
        if plan["segment"] == L.VICOBA_GROUP_SEGMENT:
            info = vicoba["groups"].get(plan["organisation_id"])
            if not info:
                outcomes["VICOBA group plan without a VICOBA group (left as stored)"] += 1
                continue
            status, vicoba_notes = vicoba_plan_state(plan, info["case"], info, info["introducer_plan"])
            plan = {**plan, "review_status": status, "missing_information": vicoba_missing(plan.get("missing_information"), vicoba_notes),
                    "channel_attribution": vicoba_channel(info)}
            outcomes[f"VICOBA group: band {info['case']['band']}"] += 1
        elif plan["segment"] == L.VICOBA_INTRODUCER_SEGMENT:
            vicoba_entry = vicoba["introducers"].get(plan["organisation_id"])
            if not vicoba_entry or vicoba_entry["message_id"] != plan["message_id"]:
                outcomes["VICOBA introducer plan of another wave (left as stored)"] += 1
                continue
            status, vicoba_notes = vicoba_introducer_state(plan["organisation_id"], vicoba_entry, org, plan["organisation_id"] in other_plans)
            plan = {**plan, "review_status": status, "missing_information": vicoba_missing(plan.get("missing_information"), vicoba_notes)}
            outcomes[f"VICOBA introducer ({vicoba_entry['request']}): {status}"] += 1
        # Named-person fallout (11 October 2026): a case B plan's follow-ups are the offer and a close with a redirect-style ask, on AQ02.
        fallout = fallout_kind(plan, org, ctx)
        track = track_for(plan, fallout)
        if track != plan["acquisition_track_id"]:
            outcomes[f"track {plan['acquisition_track_id']} -> {track}"] += 1
            track_moves.append((track, plan["message_id"]))
            plan = {**plan, "acquisition_track_id": track}
        contact = ctx["contacts"].get(plan.get("target_id")) if plan.get("target_type") == "contact" else None
        if plan["segment"] == L.VICOBA_GROUP_SEGMENT:
            copy = vicoba_copy(plan, org, vicoba["groups"][plan["organisation_id"]])
        elif plan["segment"] == L.VICOBA_INTRODUCER_SEGMENT:
            copy = vicoba_introducer_copy(plan, org, vicoba_entry["request"], vicoba_entry["groups"])
        elif plan["segment"] == "SACCOS members":
            copy = saccos_copy(plan, org, track)
        elif plan["segment"] == "Introducers":
            copy = introducer_copy(plan, org, track, fallout)
        elif org.get("name", "").startswith("Rivertrees"):
            copy = rivertrees_copy(org)
        else:
            copy = employer_copy(plan, org, track, fallout, bool(contact and R.HR.search(contact.get("role") or "")))
        notes = plan_notes(copy, plan["organisation_id"], welfare_links)
        if str(plan.get("message_variant") or "").startswith("A"):
            # Variant A asks for sponsorship (draft_employer_sponsorship.py). The offer register gives sponsorship rows no offer message
            # until they reply, so the staff-benefit follow-ups would switch the ask mid-thread: left blank until sponsorship follow-up
            # copy is approved (fixed 11 October 2026).
            copy = {**copy, "follow_up_1": "", "follow_up_2": ""}
            notes.append(SPONSORSHIP_FOLLOW_UP_NOTE)
        else:
            plan = {**plan, "missing_information": drop_note(str(plan.get("missing_information") or ""), SPONSORSHIP_FOLLOW_UP_NOTE)}
        # The first touch (approved 11 October 2026): the Attn format or the redirect request, by who the route can reach.
        copy, touch_notes, case = apply_first_touch(plan, org, copy, ctx)
        first_touch_cases[(plan["selection"] == "Candidate for review", case or "unchanged")] += 1
        if fallout:
            outcomes[f"named-person fallout (case B): {plan['segment']}"] += 1
            # The last fallout step: one message to the escalation contact, if one exists. Noted on the plan; nothing is drafted to them.
            touch_notes = touch_notes + [n for n in (F.escalation_note(plan.get("escalation_recipient")),) if n]
        missing_now = str(plan.get("missing_information") or "")
        for note in FIRST_TOUCH_NOTES - set(touch_notes):
            missing_now = drop_note(missing_now, note)
        missing_now = "; ".join(n for n in missing_now.split("; ") if n.strip() and (not n.startswith(F.ESCALATION_START) or n in touch_notes))
        plan = {**plan, "missing_information": missing_now}
        notes += touch_notes
        updates.append((plan, copy, notes))
        # The pre-offer and the offer-led copies are each kept once; later, only a copy that actually changes is kept, so a
        # re-run adds nothing.
        stored = tuple(plan.get(k) or "" for k in COPY_FIELDS)
        if not plan.get("offer_version"):
            label = BACKUP_VERSION
        elif plan.get("strategy_version") != COPY_VERSION:
            label = REQUEST_FIRST_BACKUP
        else:
            changed = stored != tuple(copy[k] or "" for k in COPY_FIELDS)
            taken = {v for (v,) in con.execute("SELECT version FROM message_versions WHERE message_id=? AND version IN (?,?)",
                                               (plan["message_id"], REDRAFT_BACKUP, FALLOUT_BACKUP))}
            free = [v for v in (REDRAFT_BACKUP, FALLOUT_BACKUP) if v not in taken]
            label = ((offer_backup_label() if plan.get("offer_version") != L.OFFER_VERSION else free[0] if free else OFFER_NOTE_BACKUP)
                     if changed else "")
        if label:
            backups.append((label, plan["message_id"], json.dumps({"outreach_plan": original, "message": messages.get(plan["message_id"])},
                                                                  ensure_ascii=False, default=str)))
        outcomes["rewritten"] += 1

    contacts_by_id = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    channel_updates = []
    for plan in plans:
        contact = contacts_by_id.get(plan["target_id"]) if plan["target_type"] == "contact" else None
        if contact:
            channel = emailed_channel(contact, orgs.get(plan["organisation_id"], {}), plan["contact_channel"])
            if channel != (plan["contact_channel"] or ""):
                channel_updates.append((channel, plan["message_id"]))
    outcomes["decision-maker drafts moved from a phone to an email route"] = len(channel_updates)

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
        copy = rivertrees_copy(org) if rivertrees else (introducer_copy(plan, org, "AQ01") if segment == "Introducers" else employer_copy(plan, org, "AQ01"))
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
    segment_of = {p["organisation_id"]: p["segment"] for p in plans if p["segment"] not in L.VICOBA_SEGMENTS}
    segment_of.update({p["organisation_id"]: p["segment"] for p, *_ in new_rows})
    vicoba_orgs = set(vicoba["groups"])  # a group's officers are reached through the group plan, never a plan of their own
    planned_contacts = {p["target_id"] for p in plans if p["target_type"] == "contact"}
    for c in [dict(r) for r in con.execute("SELECT * FROM contacts ORDER BY contact_id")]:
        if c["contact_id"] in planned_contacts or not c["name"] or c["organisation_id"] not in segment_of or c["organisation_id"] in vicoba_orgs:
            continue
        org = orgs.get(c["organisation_id"], {})
        direct = c.get("named_email") or c.get("role_phone") or c.get("published_role_email")
        route = direct or c.get("shared_email") or c.get("organisation_phone") or org.get("email") or org.get("phone")
        route = emailed_channel(c, org, route)
        track = "AQ02" if direct else ("AQ01" if route else "AQ00")
        plan = {"message_id": sid("M", "offer-v4-contact", c["contact_id"]), "target_id": c["contact_id"], "target_type": "contact",
                "organisation_id": c["organisation_id"], "target_name": c["name"], "organisation_name": org.get("name", ""),
                "segment": segment_of[c["organisation_id"]], "cta_type": "Information offer" if track == "AQ02" else "Welfare referral",
                "hook": "", "hook_status": "", "recipient_role": c.get("role") or "Named contact", "selection": "Alternative"}
        copy = (saccos_copy(plan, org, track) if plan["segment"] == "SACCOS members" else
                introducer_copy(plan, org, track) if plan["segment"] == "Introducers" else employer_copy(plan, org, track))
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

    # New plans take the first-touch format too, with the route they are created with as their channel.
    for i, (plan, org, track, route, copy, missing) in enumerate(new_rows):
        shaped_plan = {**plan, "contact_channel": route or "", "message_variant": ""}
        fallout = fallout_kind(shaped_plan, org, ctx) if not org.get("name", "").startswith("Rivertrees") else ""
        if fallout:  # a case B plan: the named-person fallout follow-ups, on AQ02 unless it is held
            track = "AQ00" if track == "AQ00" else "AQ02"
            contact = ctx["contacts"].get(plan.get("target_id")) if plan.get("target_type") == "contact" else None
            copy = (introducer_copy(plan, org, track, fallout) if plan["segment"] == "Introducers" else
                    employer_copy(plan, org, track, fallout, bool(contact and R.HR.search(contact.get("role") or ""))))
        copy, touch_notes, case = apply_first_touch(shaped_plan, org, copy, ctx)
        first_touch_cases[(False, case or "unchanged")] += 1
        new_rows[i] = (plan, org, track, route, copy, missing + touch_notes)
    outcomes.update({f"first touch: {'chosen' if chosen else 'alternative'} plans, {case}": n for (chosen, case), n in sorted(first_touch_cases.items())})
    # One introducer plan per master introducer per wave (NGO field office, bank branch, employer), listing the groups it covers.
    stored_ids = {p["message_id"] for p in plans}
    vicoba_new = []
    for oid, entry in vicoba["introducers"].items():
        if entry["message_id"] in stored_ids:
            continue
        org = orgs[oid]
        plan = {"message_id": entry["message_id"], "target_id": oid, "target_type": "organisation", "organisation_id": oid, "target_name": org["name"],
                "organisation_name": org["name"], "segment": L.VICOBA_INTRODUCER_SEGMENT, "cta_type": "Introducer referral", "hook": "", "hook_status": "",
                "selection": "Candidate for review"}
        status, notes = vicoba_introducer_state(oid, entry, org, oid in other_plans)
        copy = vicoba_introducer_copy(plan, org, entry["request"], entry["groups"])
        # The same order a rewrite gives: the VICOBA notes, then the plan notes, then the planned next touch.
        vicoba_new.append((plan, org, entry, status, copy, notes + plan_notes(copy, oid, welfare_links) + [F.NEXT_TOUCH["vicoba_introducer"]]))
        outcomes[f"new VICOBA introducer plan ({entry['request']}): {status}"] += 1
    issues = []
    checked = [(plan, copy) for plan, copy, _ in updates] + [(plan, copy) for plan, _, _, _, copy, _ in new_rows]
    checked += [(plan, copy) for plan, _, _, _, copy, _ in vicoba_new]
    checked += [(plan, {**copy, "body": copy["_variant"][1], "follow_up_1": "", "follow_up_2": "", "offer_message": "", "sw": ""})
                for plan, copy, _ in updates if copy.get("_variant")]
    for plan, copy in checked:
        names = tuple(n for raw in (plan.get("organisation_name"), plan.get("target_name")) if raw for n in (raw, L.display_name(raw), L.greeting_name(raw)))
        for field in ("body", "follow_up_1", "follow_up_2", "offer_message", "sw", "english_meaning"):
            for problem in L.check_message(copy.get(field, ""), copy["offer_ids"], ignore=names):
                issues.append({"message_id": plan["message_id"], "field": field, "issue": problem})
        # The first message, in English and Kiswahili, is a request with no offer terms. A VICOBA group's Kiswahili offer sits in 'sw'
        # (offer_message_sw), so its first message is checked in Kiswahili (body) and in its English meaning (first_en).
        for field in copy.get("first_fields", ("body", "sw")):
            for problem in L.check_first_message(copy[field], ignore=names):
                issues.append({"message_id": plan["message_id"], "field": field, "issue": problem})
        if plan["segment"] in L.VICOBA_SEGMENTS:
            texts = {f: copy.get(f, "") for f in ("subject", "body", "follow_up_1", "follow_up_2", "offer_message", "sw", "english_meaning")}
            for field, text in texts.items():
                issues += [{"message_id": plan["message_id"], "field": field, "issue": i} for i in L.check_savings_message(text)]
                if DISTANCE_CLAIM.search(text) and not precise(orgs.get(plan["organisation_id"], {})):
                    issues.append({"message_id": plan["message_id"], "field": field, "issue": "distance claim without a point-level location"})
    for plan, copy, notes in updates:  # every Kiswahili VICOBA draft carries NATIVE_REVIEW until its template version is approved
        if plan["segment"] == L.VICOBA_GROUP_SEGMENT and not copy.get("sw_approved") and L.NATIVE_REVIEW not in merge_notes(plan["missing_information"], notes):
            issues.append({"message_id": plan["message_id"], "field": "missing_information", "issue": "Kiswahili draft without NATIVE_REVIEW"})
    # One introducer plan per introducer per wave: the wave's plans (stored and new) counted per introducer.
    this_wave = {e["message_id"] for e in vicoba["introducers"].values()}
    per_introducer = Counter(p["organisation_id"] for p in plans if p["segment"] == L.VICOBA_INTRODUCER_SEGMENT and p["message_id"] in this_wave)
    per_introducer.update(p["organisation_id"] for p, *_ in vicoba_new)
    for oid, n in per_introducer.items():
        if n > 1:
            issues.append({"message_id": oid, "field": "plans", "issue": f"{n} introducer plans for this introducer in wave {args.vicoba_wave}"})
    for d, body in parent_updates:
        for problem in L.check_message(body, PARENT_OFFERS):
            issues.append({"message_id": d["enquiry_id"], "field": "parent reply", "issue": problem})
    summary = {"outcomes": dict(outcomes), "conformance_issues": len(issues), "tracks_new": dict(Counter(t for _, _, t, _, _, _ in new_rows)),
               "segments_new": dict(Counter(p["segment"] for p, *_ in new_rows)), "released_by_selection_and_kind": dict(released),
               "vicoba": {"wave": args.vicoba_wave, "groups": len(vicoba["groups"]), "introducer_plans": len(vicoba["introducers"]),
                          "bands": dict(Counter(i["case"]["band"] for i in vicoba["groups"].values())),
                          "bands_once_templates_approved": dict(Counter(i["case"]["band_after_review"] for i in vicoba["groups"].values())),
                          "kiswahili_templates": {t: {"version": v, "approved": L.kiswahili_approved(t, v)} for t, v in vicoba["versions"].items()}}}
    preview_dir = ROOT / "runtime" / "messaging"
    preview_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run or issues:
        sample = [{"message_id": p["message_id"], "segment": p["segment"], "track": p["acquisition_track_id"], "subject": c["subject"], "body": c["body"],
                   "follow_up_1": c["follow_up_1"], "follow_up_2": c["follow_up_2"], "offer_message": c["offer_message"], "sw": c["sw"],
                   "english_meaning": c.get("english_meaning", ""), "language": c.get("language", ""), "review_status": p["review_status"],
                   "offer_ids": c["offer_ids"], "notes": n, "missing_information": p.get("missing_information")} for p, c, n in updates]
        sample += [{"message_id": p["message_id"], "segment": p["segment"], "track": t, "subject": c["subject"], "body": c["body"],
                    "offer_message": c["offer_message"], "offer_ids": c["offer_ids"], "missing": m} for p, _, t, _, c, m in new_rows]
        sample += [{"message_id": p["message_id"], "segment": p["segment"], "review_status": st, "subject": c["subject"], "body": c["body"],
                    "language": c["language"], "missing": n} for p, _, _, st, c, n in vicoba_new]
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
        for column in ("offer_version", "offer_ids", "offer_evidence", "offer_message_sw", "offer_message", "variant_subject_base", "variant_body_base"):
            if column not in columns:
                con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
        con.executemany("INSERT OR IGNORE INTO message_versions (version, message_id, original_json) VALUES (?,?,?)",  # keep the first backup
                        backups)
        evidence = "PE025; PE026; PE027; PE028"
        for plan, copy, notes in updates:
            vm = copy.get("value_module_ids") or (plan["value_module_ids"] if "VM19" in str(plan["value_module_ids"]) else f"{plan['value_module_ids']}; VM19")
            if plan["segment"] in L.VICOBA_SEGMENTS:  # Kiswahili in the message fields, English meaning apart (decision 6)
                con.execute("UPDATE outreach_plans SET language=?, english_meaning=?, cta_type=? WHERE message_id=?",
                            (copy["language"], copy["english_meaning"], plan.get("cta_type") or "", plan["message_id"]))
            missing = drop_notes(merge_notes(plan.get("missing_information"), notes), OBSOLETE_NOTES)
            hook_status = NO_HOOK if plan.get("hook_status") == OFFER_LED_NO_HOOK else plan.get("hook_status")
            con.execute("""UPDATE outreach_plans SET subject=?, body=?, follow_up_1=?, follow_up_2=?, offer_message=?, proposed_offer=?,
                           value_module_ids=?, missing_information=?, campaign_copy_status=?, offer_version=?, offer_ids=?, offer_evidence=?,
                           offer_message_sw=?, strategy_version=?, hook_status=? WHERE message_id=?""",
                        (copy["subject"], copy["body"], copy["follow_up_1"], copy["follow_up_2"], copy["offer_message"],
                         offer_summary(copy["offer_ids"]), vm, missing, COPY_STATUS, L.OFFER_VERSION, "; ".join(copy["offer_ids"]),
                         evidence if copy["offer_ids"] else "",
                         copy["sw"], COPY_VERSION, hook_status, plan["message_id"]))
            # A plan whose creation-time holds were released (refresh_creation_holds): its status, track and route.
            con.execute("UPDATE outreach_plans SET review_status=?, acquisition_track_id=?, contact_channel=?, channel_attribution=? WHERE message_id=?",
                        (plan["review_status"], plan["acquisition_track_id"], plan["contact_channel"], plan["channel_attribution"], plan["message_id"]))
            con.execute("UPDATE messages SET subject=?, body=?, strategy_id=?, status=?, conditions=? WHERE message_id=?",
                        (copy["subject"], copy["body"], STRATEGY_ID, MESSAGE_STATUS, conditions_for(copy), plan["message_id"]))
            if copy.get("_variant"):  # the stored variant draft in its first-touch format; its untouched text is kept as the base
                v_subject, v_body, base_subject, base_body = copy["_variant"]
                con.execute("UPDATE outreach_plans SET variant_subject=?, variant_body=?, variant_subject_base=?, variant_body_base=? WHERE message_id=?",
                            (v_subject, v_body, base_subject, base_body, plan["message_id"]))
        # A plan whose track moved (case B to AQ02, 11 October 2026): its campaign assignment follows, as refresh_acquisition_metadata.py syncs it.
        con.executemany("UPDATE campaign_lead_assignments SET acquisition_track_id=? WHERE message_id=?", track_moves)
        con.executemany("UPDATE outreach_plans SET contact_channel=?, channel_attribution='Company inbox first for a verified decision-maker; the published phone follows' WHERE message_id=?", channel_updates)
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
                                                                             else "Human review, then send the request" if track == "AQ02"
                                                                             else "Human review, then the AQ01 routing request"),
                         track, modules, "New-contact acquisition; track-selected and independent of the internal marketing calendar."))
        # VICOBA introducer plans (one per introducer per wave) and, on each introducer, the groups it covers in wave order (fact
        # covers_groups, '<wave>: <id>; <id>', women's groups first), sourced to the covered groups' own records.
        for plan, org, entry, status, copy, notes in vicoba_new:
            records = [org_record[g["organisation_id"]] for g in entry["groups"] if org_record.get(g["organisation_id"])]
            missing = merge_notes("", notes)
            con.execute("INSERT INTO messages (message_id, target_type, target_id, subject, body, strategy_id, status, conditions, source_record_id) "
                        "VALUES (?,?,?,?,?,?,?,?,?)", (plan["message_id"], "organisation", plan["target_id"], copy["subject"], copy["body"],
                                                       STRATEGY_ID, MESSAGE_STATUS, conditions_for(copy), records[0] if records else None))
            con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, target_name, organisation_name, strategy_version,
                           segment, recipient_role, persona, contact_channel, channel_attribution, evidence_url, evidence_date, verified_on, evidence_basis,
                           evidence_record_ids, relevance_reason, proposed_offer, cta_type, flow_id, review_status, missing_information, selection,
                           subject, body, follow_up_1, follow_up_2, hook_status, campaign_copy_status, acquisition_version, acquisition_track_id,
                           value_module_ids, strategy_scope, offer_version, offer_ids, offer_evidence, offer_message_sw, offer_message, message_variant,
                           variant_reason, language, english_meaning)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (plan["message_id"], plan["target_id"], "organisation", plan["organisation_id"], org["name"], org["name"], COPY_VERSION,
                         plan["segment"], {"ngo": "NGO field office", "bank": "Branch manager", "employer": "Employer (at its S4 meeting)"}[entry["request"]],
                         "VICOBA introducer", org.get("email") or org.get("phone") or "", "Organisation's published route in the master",
                         org.get("source_url") or "", "", TODAY, "derived_from_group_records", "; ".join(records),
                         f"Introducer of {len(entry['groups'])} savings group(s) in wave {args.vicoba_wave}: a request to introduce Silverleaf to "
                         "group committees; one request per introducer per wave; no member list.", "", plan["cta_type"], "F26", status, missing,
                         plan["selection"], copy["subject"], copy["body"], "", "", NO_HOOK, COPY_STATUS, "2026-09-09-new-contact-acquisition-v4",
                         "AQ00" if status == "Needs research" else "AQ01", copy["value_module_ids"],
                         "New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the acquisition track controls cadence.",
                         L.OFFER_VERSION, "", "", "", "", "n/a", "n/a: a VICOBA introducer request (an introduction to group committees).", "en", ""))
        for oid, entry in vicoba["introducers"].items():
            value = f"{args.vicoba_wave}: " + "; ".join(g["organisation_id"] for g in entry["groups"])
            record = next((org_record[g["organisation_id"]] for g in entry["groups"] if org_record.get(g["organisation_id"])), None)
            con.execute("DELETE FROM facts WHERE entity_type='organisation' AND entity_id=? AND field='covers_groups' AND value LIKE ? AND value<>?",
                        (oid, f"{args.vicoba_wave}: %", value))
            con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                        (sid("X", oid, "covers_groups", value), "organisation", oid, "covers_groups", value, record))
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
                     "Every offer-aligned v4 draft.", "No term beyond the discount schedule the register records; no guaranteed places, transport or "
                     "outcomes; no referral rewards; the 40% rate is Rivertrees' only; the group rate (OF07) is for savings groups only, "
                     "counted from one group's members.",
                     "PE025; PE026; PE027; PE028", "Draft; terms from the discount schedule (confirmed 12 October 2026); check with Finance before the first send"))
        for row in (
            ("PE025", "Offer terms", "Silverleaf's discount schedule: free uniform for full-year payment; sibling 10%/20%; NGO partner 3-18%; institutional 20% heads of department and 10% first-year for other staff; group rates 7%/12%/17% at 50/100/150 primary-age students (the row 'KINEFA discount', applied to savings groups generally by the user's decision of 13 October 2026); expired referral package; ECD facilitation.",
             "All offer-aligned v4 drafts state these terms from the offer register.", "references/Offers & Discounts/2025 Proposed Fees & Discounts - 2025 Discounts.pdf",
             "Summary of discounts offered, p.1 (sha256 c6125a41a129e7fd)", "Internal offer document (2025)", TODAY, "Usable",
             "The user confirmed on 12 October 2026 that the offer terms come from this schedule; check with Finance before the first send. "
             "The referral package expired on 30 November 2024."),
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
                     "SACCOS get the family offer and the group rate for savings groups; Rivertrees gets its 2025 terms. A recipient hook appears only when verified; "
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
                     "Draft; the offer message states the discount schedule's terms; check with Finance before the first send"))
        con.execute("UPDATE acquisition_tracks SET initial_touch=? WHERE track_id='AQ02'",
                    ("Initial personalised request after human review; the documented offer follows in follow-up 1.",))
        # Case B (a named person reached only through a general inbox) joins AQ02 (11 October 2026): the Attn request, the offer, then a
        # close with a redirect-style ask; the escalation contact, if any, gets one message after that (noted on the plan, not drafted).
        con.execute("UPDATE acquisition_tracks SET use_when=?, follow_up_policy=? WHERE track_id='AQ02'", (AQ02_USE_WHEN, AQ02_FOLLOW_UP))
        for table, column, step in (("outreach_flows", "example_copy", "step"), ("automation_recipes", "example_copy", "step"),
                                    ("campaign_touchpoints", "draft_copy", "flow_step")):
            con.execute(f'UPDATE {table} SET "{column}"=? WHERE flow_id=? AND "{step}"=3 AND "{column}"=?', (F01_STEP3_COPY, "F01", F01_STEP3_BEFORE))
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
               "register's terms); no recipient hook unless verified; not sent")
NO_HOOK = "No hook: request-first opening"
OFFER_LED_NO_HOOK = "No hook: offer-led opening"
# The hold note scripts/contacts/merge_master_contacts.py writes for an organisation that may have closed.
CLOSURE_NOTE = "Possible closure found by contact research; confirm the organisation still operates before any message."


def conditions_for(copy: dict) -> str:
    """The message's release conditions; the same whether the plan is new or rewritten (a VICOBA draft carries its own)."""
    if copy.get("conditions"):
        return copy["conditions"]
    return (f"{L.REQUEST_FIRST} {L.OFFER_TERMS_NOTE} Offer terms: {'; '.join(copy['offer_ids'])} (data/reference/silverleaf-offer-register.json). "
            "Confirm the route, campus fit and organisation relevance before use. No guaranteed places, transport or outcomes. One active "
            "recipient per organisation.")


def plan_notes(copy: dict, organisation_id: str, welfare_links: dict) -> list[str]:
    """The notes every offer-aligned plan carries, whether new or rewritten. A VICOBA introducer request states no terms, so it carries
    no offer-terms note; a VICOBA Kiswahili draft whose template version is approved (sw_approved) no longer carries NATIVE_REVIEW."""
    notes = [L.OFFER_TERMS_NOTE] if copy.get("offer_ids") else []  # a note, never a hold; OF07 carries no Finance condition since 13 October 2026
    if organisation_id in welfare_links:
        notes.append(f"Also a welfare lead ({welfare_links[organisation_id]}); contact the organisation once.")
    if copy.get("sw") and not copy.get("sw_approved"):
        notes.append(L.NATIVE_REVIEW)
    return notes


RECIPE_CONFIGURATION = "automation-2026-09-23-offer-v4"
SACCOS_V3_COPY = "Offer an optional member information session without a loan, subsidy or discount claim"
SACCOS_V4_COPY = ("State the family offer and the group rate for savings groups (OF07) exactly as the offer register records them; "
                  "no loan, subsidy or referral claim")
# The step-2 copy before the group-rate decision (13 October 2026); align_recipes replaces it.
SACCOS_V4_COPY_BEFORE_GROUP_RATE = ("State the family offer and the member-association rate exactly as the offer register records them (Finance must "
                                    "extend the KINEFA rate first); no loan, subsidy or referral claim")
SACCOS_V4_STEP2 = "Offer the one-page version using approved fee information without figures unless cleared"
SACCOS_V5_STEP1 = "Ask for a short meeting with the committee about members' children's education; no offer terms"
F01_V4_PRINCIPLE = "Offer-led, recipient-centred, one CTA; PE023 and PE024"
F01_V5_PRINCIPLE = "Request-first, recipient-centred, one CTA; the offer follows in follow_up_1; PE023 and PE024"
# Case B on AQ02 (11 October 2026; pipeline draft section 5, named-person fallout).
AQ02_USE_WHEN = ("Recipient role, route and organisational relevance are sufficiently verified; also a named decision-maker reached only "
                 "through a general inbox (case B, the Attn format), from 11 October 2026.")
AQ02_FOLLOW_UP = ("Follow up after 4 working days and once more after another 4 working days; then stop. Case B (11 October 2026): follow-up 1 "
                  "gives the documented offer, follow-up 2 closes with a redirect-style ask (who should I write to?), then one message to the "
                  "escalation contact, if one exists, 5 working days after the close (noted on the plan; not drafted).")
F01_STEP3_BEFORE = "Ask whether to send the outline or close the conversation"
F01_STEP3_COPY = ("Ask whether to send the outline or close the conversation; for case B (Attn, 11 October 2026) ask who to write to if it "
                  "sits with someone else, such as HR, or close")
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
                                       ("F03", 1, SACCOS_V4_COPY_BEFORE_GROUP_RATE, SACCOS_V5_STEP1),
                                       ("F03", 2, SACCOS_V4_STEP2, SACCOS_V4_COPY), ("F03", 2, SACCOS_V4_COPY_BEFORE_GROUP_RATE, SACCOS_V4_COPY)):
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


def offer_backup_label() -> str:
    """The message_versions label for a copy a change of the offer register alters: '2026-10-13-before-offer-v6' for register
    version '2026-10-13-offer-v6'. One label per register version, so each plan's copy before that version is kept once."""
    return L.OFFER_VERSION.replace("-offer-", "-before-offer-")


def offer_summary(ids) -> str:
    return "; ".join(f"{i} {L.OFFERS[i]['name']}" for i in ids)


if __name__ == "__main__":
    raise SystemExit(main())
