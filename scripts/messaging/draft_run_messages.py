#!/usr/bin/env python3
"""Draft offer-aligned messages into a separate run database (welfare or government). A pipeline step.

Runs after the run database is built (initialize_lead_db.py plus the track's augment step) and before its workbook.
It replaces the run's messages and outreach_plans, so it is safe to repeat. Terms come only from
data/reference/silverleaf-offer-register.json and every draft is checked against it.

Welfare (plans/b2b-welfare-leads-plan.md): one English sequence per in-scope organisation, request first (23 September
2026). The first message asks for a short meeting and states no offer terms: about the education of the children in a
home's or programme's care, or, for funders only, a request to sponsor students, with the funder's verified support
for a home as the reason when the run records one. The follow-up states the offer: the NGO partner rate (OF03), the
free uniform (OF01) and four instalments (OF09). One neutral reply goes to each current, in-fit public parent enquiry.
Routes come from the organisation or a low- or medium-risk contact, never a risky one. WA01 organisations with a route
are 'draft_ready'; everything else is held.

Government (plans/b2b-government-leads-plan.md): one Kiswahili letter per office with an English meaning for review.
Councils get the GA01 introduction letter, wards and villages the convening request (held until GA01), district and
regional offices a courtesy notice. Letters describe only the family offer (OF01, OF02, OF09) for parents and never
offer officials a benefit.

Nothing is sent; drafts stay 'draft_ready' or 'needs_review'.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone

import offer_lib as L

ROOT = L.ROOT
WELFARE_OFFERS = ["OF03", "OF01", "OF09"]
FAMILY_OFFERS = ["OF01", "OF02", "OF09"]
PERSONAL_DOMAIN = re.compile(r"@(gmail|yahoo|ymail|hotmail|outlook|live|icloud|aol|rocketmail)\.", re.I)


def sid(*parts) -> str:
    return "M" + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def payloads(con, entity_type) -> dict:
    out = {}
    for eid, payload in con.execute("SELECT es.entity_id, sr.payload_json FROM entity_sources es JOIN source_records sr "
                                    "ON sr.source_record_id = es.source_record_id WHERE es.entity_type = ?", (entity_type,)):
        out.setdefault(eid, json.loads(payload))
    return out


def prepare(con) -> None:
    columns = {r[1] for r in con.execute("PRAGMA table_info(outreach_plans)")}
    for column in ("contact_route", "route_value", "recipient", "language", "offer_ids", "offer_version", "follow_up_message_id",
                   "translation_message_id", "subject", "outcome"):
        if column not in columns:
            con.execute(f'ALTER TABLE outreach_plans ADD COLUMN "{column}" TEXT')
    con.execute("DELETE FROM outreach_plans")
    con.execute("DELETE FROM messages")


def add(con, now, plan: dict, subject: str, body: str, follow_up: str = "", translation: str = "", version: str = "offer-v4") -> None:
    mid = plan["message_id"]
    con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid, plan["target_id"], plan["target_type"], subject, body, version,
                                                                 plan["review_status"], now))
    if follow_up:
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid + "-F1", plan["target_id"], plan["target_type"], f"Re: {subject}",
                                                                     follow_up, version + " follow-up 1", plan["review_status"], now))
    if translation:
        con.execute("INSERT INTO messages VALUES (?,?,?,?,?,?,?,?)", (mid + "-EN", plan["target_id"], plan["target_type"], f"English meaning: {subject}",
                                                                     translation, version + " English meaning for review", plan["review_status"], now))
    con.execute("""INSERT INTO outreach_plans (message_id, target_id, target_type, organisation_id, relevance_reason, proposed_offer, cta_type, hook,
                   hook_source_url, hook_verified_on, acquisition_track_id, value_module_ids, review_status, missing_information, contact_route,
                   route_value, recipient, language, offer_ids, offer_version, follow_up_message_id, translation_message_id, subject, outcome)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (mid, plan["target_id"], plan["target_type"], plan.get("organisation_id"), plan["relevance_reason"],
                 "; ".join(f"{i} {L.OFFERS[i]['name']}" for i in plan["offer_ids"]), plan["cta_type"], plan.get("hook", ""),
                 plan.get("hook_source_url", ""), plan.get("hook_verified_on", ""), plan["track"], plan["modules"],
                 plan["review_status"], "; ".join(plan["missing"]), plan.get("contact_route", ""), plan.get("route_value", ""), plan.get("recipient", ""),
                 plan["language"], "; ".join(plan["offer_ids"]), L.OFFER_VERSION, mid + "-F1" if follow_up else "", mid + "-EN" if translation else "",
                 subject, plan["outcome"]))


# ------------------------------------------------------------------ welfare
def precise(p: dict) -> bool:
    return str(p.get("geocode_precision") or "") in ("address", "locality", "point") and p.get("distance_km") not in (None, "")


greeting_name = L.greeting_name


def funder_reasons(con) -> dict:
    """For each funder, the home or programme it supports or runs, from a verified 'funds' or 'operates' relationship with a fetched source: the
    sourced reason for its sponsorship request. A source that is the page itself is preferred to a search-results page. The source URL and date go
    with the plan as its hook."""
    names = dict(con.execute("SELECT organisation_id, name FROM organisations").fetchall())
    candidates = {}
    for funder, kind, supported, supported_id, sources in con.execute(
            "SELECT from_organisation_id, relationship_type, to_organisation, to_organisation_id, sources_json FROM organisation_relationships "
            "WHERE relationship_type IN ('funds','operates') AND verification_status='verified' ORDER BY to_organisation"):
        fetched = [s for s in json.loads(sources or "[]") if s.get("fetched") and s.get("url")]
        fetched.sort(key=lambda s: "full_text_search" in s["url"])
        if funder and fetched:
            candidates.setdefault(funder, []).append((
                "full_text_search" in fetched[0]["url"], kind != "funds",
                {"supported": L.display_name(names.get(supported_id) or supported), "verb": "supports" if kind == "funds" else "runs",
                 "url": fetched[0]["url"], "verified_on": fetched[0].get("accessed_on", "")}))
    return {f: min(c, key=lambda t: (t[0], t[1]))[2] for f, c in candidates.items()}


LEADER_TOP = re.compile(r"founder|owner|\bceo\b|chief executive|executive director|president|chair|director|bishop|head of", re.I)
LEADER_MID = re.compile(r"manager|coordinator|pastor|leader|principal|administrator", re.I)
NOT_LEADER = re.compile(r"treasurer|secretary|volunteer|intern|assistant|adviser|advisor|trustee|board member|accountant|nurse|teacher|social worker|"
                        r"programme officer|vice|deputy", re.I)
FOREIGN_ROUTE = re.compile(r"kenya|uganda|rwanda|burundi|zambia|malawi|congo|southafrica|\.(ke|ug|rw|bi|cd|zm|mw|za)$", re.I)


def leader_rank(role: str):
    """0 founder, owner, chief executive, director or president; 1 manager or coordinator; None for anyone else (treasurer, volunteer, board member)."""
    role = role or ""
    if NOT_LEADER.search(role):
        return None
    if LEADER_TOP.search(role):
        return 0
    return 1 if LEADER_MID.search(role) else None


def role_phrase(role: str) -> str:
    """How a published role reads in 'I understand that you are ... of <organisation>'; '' when it is too long or messy to quote."""
    role = " ".join(str(role or "").split())
    if not role or len(role) > 45 or re.search(r"[();/]", role):
        return ""
    return f"a {role.lower()}" if role.lower().startswith("co-") else f"the {role}"


def best_leader(contacts, prefer=None) -> dict | None:
    """The organisation's most senior named, confirmed, medium-risk contact with a full name, or None."""
    best = None
    for c in contacts:
        name = greeting_name(c.get("contact_name") or "")
        rank = leader_rank(c.get("role") or "")
        if (c.get("pdpa_risk") != "medium" or c.get("role_certainty") != "confirmed" or len(name.split()) < 2 or re.search(r"\d|\?", name) or rank is None):
            continue
        preferred = 0 if prefer and prefer.search(c.get("role") or "") else 1  # for a network: the social-services or children's lead before the bishop
        key = (preferred, rank, 0 if (c.get("named_email") or c.get("published_role_email")) else 1, name)
        if best is None or key < best[0]:
            best = (key, c, name)
    return {**best[1], "greet_name": best[2]} if best else None


def welfare(con, now, run_cfg) -> dict:
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    # Reviewed decisions (links.json official_personal_inboxes): the organisation itself publishes this personal-domain address as its contact.
    links_path = ROOT / "data" / "runs" / run_cfg.get("run_id", "") / "links.json"
    official_inboxes = json.loads(links_path.read_text(encoding="utf-8")).get("official_personal_inboxes", {}) if links_path.exists() else {}
    org_payload, con_payload = payloads(con, "organisation"), payloads(con, "contact")
    contacts_by_org = {}
    for r in con.execute("SELECT * FROM contacts ORDER BY contact_id"):
        contacts_by_org.setdefault(r["organisation_id"], []).append({**dict(r), **con_payload.get(r["contact_id"], {})})
    outcomes, issues = Counter(), []
    reasons = funder_reasons(con)
    for oid, o in sorted(orgs.items(), key=lambda kv: kv[1]["name"]):
        p = {**org_payload.get(oid, {}), **{k: v for k, v in o.items() if v not in (None, "")}}
        track = p.get("proposed_welfare_track") or "WA00 Hold"
        if track == "Excluded" or p.get("segment") == "Out of scope":
            outcomes["excluded: no message"] += 1
            continue
        model = p.get("care_model") or ""
        name = L.display_name(o["name"], oid)
        missing = [L.REQUEST_FIRST, L.CONFIRM_2027]
        # Route: the organisation's own published email or phone first; otherwise a low- or medium-risk contact; never a risky one.
        route, value, recipient = "", "", ""
        if p.get("email") and p.get("pdpa_risk") != "risky":
            route, value = "shared_email", p["email"]
        elif p.get("phone") and p.get("pdpa_risk") != "risky":
            route, value = "organisation_phone", p["phone"]
        network = model == "network" or str(p.get("segment") or "").startswith("Welfare network")
        leader = best_leader(contacts_by_org.get(oid, []), re.compile(r"diacon|social|children|programme|program|coordinator|welfare", re.I) if network else None)
        greet = f"Dear {leader['greet_name']}," if leader else f"Dear {name} team,"
        recipient = f"{leader['greet_name']} ({leader.get('role') or 'role not published'})" if leader else ""
        for c in contacts_by_org.get(oid, []):
            if c.get("pdpa_risk") == "risky":
                continue
            email = c.get("named_email") or c.get("published_role_email") or c.get("shared_email")
            if c.get("email_type") == "personal_domain":
                email = ""
            if email or c.get("role_phone") or c.get("organisation_phone"):
                if not route:
                    route = "named_email" if c.get("named_email") and email else ("published_role_email" if email else "role_phone")
                    value = email or c.get("role_phone") or c.get("organisation_phone")
                break
        if not route:
            missing.append("No usable published route (risky routes are never used); find the organisation's own email or phone.")
        route_problem = False
        if route == "organisation_phone" or route == "role_phone":
            if not str(value).replace(" ", "").startswith("+255"):
                route_problem = True
                missing.append("The only route is a phone number outside Tanzania; find an email address.")
        elif value and (model != "funder" and p.get("segment") != "Welfare funder") and FOREIGN_ROUTE.search(str(value).split("@")[-1]):
            route_problem = True
            missing.append("The email address is on a domain outside Tanzania; confirm it reaches this organisation.")
        risky_contact_route = any(c.get("pdpa_risk") == "risky" and str(value or "").lower() in
                                  {str(v).lower() for v in (c.get("named_email"), c.get("published_role_email"), c.get("shared_email"), c.get("role_phone")) if v}
                                  for c in contacts_by_org.get(oid, []))
        confirmed_official = str(official_inboxes.get(o["name"], {}).get("address", "")).lower() == str(value or "").lower() and bool(value)
        if risky_contact_route and not confirmed_official:
            route_problem = True
            missing.append("The only route is a named individual's address on a personal domain (risky); find the organisation's own email or phone.")
        personal_inbox = bool(PERSONAL_DOMAIN.search(str(value or "")))
        if personal_inbox and str(official_inboxes.get(o["name"], {}).get("address", "")).lower() == str(value).lower():
            personal_inbox = False  # reviewed: the organisation publishes it as its official contact
            missing.append(f"Personal-domain inbox confirmed as the organisation's official contact: {official_inboxes[o['name']].get('basis', '')}")
        if personal_inbox:
            missing.append("The organisation's published inbox is on a personal email domain; confirm it is the official address and not a "
                           "person's before use (data-protection check).")
        if str(track).startswith("WA00"):
            missing.append(f"Held: {p.get('track_reason') or 'identity, route or location unresolved'}.")
        if p.get("red_flags"):
            missing.append(f"Review the recorded red flags before any contact: {str(p['red_flags'])[:160]}.")
        campus = (L.campus_line_en(p.get("campus") or "", p.get("distance_km"), True, "you") if precise(p) else L.network_line_en())
        # The first message is a request with no offer terms; the follow-up states the offer. Sponsorship is asked of funders only.
        if model == "funder" or p.get("segment") == "Welfare funder":
            reason = reasons.get(oid)
            hook = f"I understand that {name} {reason['verb']} {reason['supported']}." if reason else ""
            subject = "Sponsorship request: students at Silverleaf Academy"
            asks = ("We are seeking sponsorships for students to help cover school fees and other education-related costs. Support of any size helps, "
                    "including a contribution towards textbooks, transport or meals.")
            if reason and leader and role_phrase(leader.get("role")):
                opening = (f"I understand that you are {role_phrase(leader.get('role'))} of {name}, which {reason['verb']} {reason['supported']}. "
                           f"It is this commitment to supporting communities in Tanzania that led me to reach out to you directly.")
            elif reason:
                opening = (f"{hook} It is this commitment to supporting communities in Tanzania that led me to write."
                           f"{'' if leader else ' I would be grateful if this could reach whoever leads ' + name + chr(39) + 's giving.'}")
            else:
                opening = f"I am writing to ask whether {name} would consider sponsoring students at Silverleaf Academy."
            body = (f"{greet}\n\n{L.INTRO} {opening}\n\n{asks} I would welcome the chance to share more about our school and students, and to discuss "
                    f"whether this might fit within {name}{chr(39) if name.endswith('s') else chr(39) + 's'} current giving.\n\n{L.MEETING_ASK}\n\n"
                    f"Thank you very much for your time and consideration.\n\n{L.SIGNATURE}")
            if not reason:
                missing.append("No verified, sourced relationship with a home or programme: there is no honest reason to ask this funder yet; confirm the fit first.")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is how sponsorship can go further at Silverleaf. When an organisation places "
                      f"all its primary-age children with us, each child receives 3% off tuition at 10 children, rising to 18% at 60 or more. Paying the "
                      f"year's tuition before the school year opens adds a free uniform set (worth TZS 110,000) per child, and tuition can be paid in "
                      f"four instalments.\n\n{L.network_line_en()}\n\nShall I send a one-page summary of the partner rates?\n\n{L.SIGNATURE}")
            cta, modules = "Sponsor conversation", "VM08; VM09; VM13"
            relevance = (f"{p.get('segment')}: sponsorship request{'; supports ' + reason['supported'] if reason else ''}; partner rates in the "
                         f"follow-up.")
        elif model == "network" or str(p.get("segment") or "").startswith("Welfare network"):
            # An introducer (decided 2 October 2026): a network, umbrella or faith social-services body that could share the partnership with its
            # member homes. The first message asks for a partnership and a meeting and states no offer terms; the partner rate follows.
            reason, hook = None, ""
            the = "" if name.split()[0].isupper() else "the "
            subject = "A partnership on education for children in your member homes"
            body = (f"{greet}\n\n{L.INTRO}\n\nWe are looking to set up a partnership with {the}{name} so that the homes and programmes it works with can "
                    f"partner with Silverleaf Academy on the education of the children in their care. I would welcome the chance to explain how it could "
                    f"work, and to discuss whether {the}{name} might share it with members, for example at a members' meeting or in a newsletter."
                    f"\n\n{L.MEETING_ASK}\n\n{L.SIGNATURE}")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is what we can offer member homes. Silverleaf Academy offers "
                      f"{L.EN['OF03']}. Paying the year's tuition before the school year opens also brings a free uniform set (worth TZS 110,000) for "
                      f"each child, and tuition can be paid in four instalments. Our admissions team checks each child's level before a place is "
                      f"confirmed.\n\n{L.network_line_en()}\n\nShall I send a one-page note you could share with members?\n\n{L.SIGNATURE}")
            cta, modules = "Introducer conversation", "VM08; VM09; VM13"
            relevance = f"{p.get('segment')}: introducer request to share the partnership with member homes; partner rates in the follow-up."
        else:
            reason, hook = None, ""
            who = "an organisation" if model == "family_based" else "a home"
            care = "in your programme" if model == "family_based" else "in your care"
            subject = f"A partnership on education for the children {care}"
            needs = (" Before any placement we would talk through each child's needs with you." if model == "specialised" else "")
            body = (f"{greet}\n\n{L.INTRO}\n\nWe are looking to set up a partnership with {name} on the education of the children {care}. I would "
                    f"welcome the chance to explain how it could work, and to discuss whether it might suit you and your team.\n\n{L.MEETING_ASK}"
                    f"\n\n{L.SIGNATURE}")
            follow = (f"{greet}\n\nFollowing up on my earlier note, here is what we can offer. Silverleaf Academy offers "
                      f"{L.EN['OF03'].replace('a home', who)}. Paying the year's tuition before the school year opens also brings a free uniform set "
                      f"(worth TZS 110,000) for each child, and tuition can be paid in four instalments. Our admissions team checks each child's level "
                      f"before a place is confirmed.{needs}\n\n{campus}\n\nWould a 20-minute call to talk through school plans for 2027 for the "
                      f"children {care} be useful?\n\n{L.SIGNATURE}")
            cta, modules = "Placement conversation", "VM08; VM09; VM13"
            relevance = (f"{p.get('segment')}: education partnership request; partner rates in the follow-up; nearest campus "
                         f"{p.get('campus') or 'unknown'}.")
            if model == "specialised":
                missing.append("Specialised centre: confirm Silverleaf can meet the children's needs before contacting.")
        funder = model == "funder" or p.get("segment") == "Welfare funder"
        ready = (str(track).startswith("WA01") and route and model != "specialised" and not p.get("red_flags") and not personal_inbox
                 and not route_problem and (reason is not None if funder else True))
        plan = {"message_id": sid("welfare", oid), "target_id": oid, "target_type": "organisation", "organisation_id": oid,
                "relevance_reason": relevance, "cta_type": cta, "track": str(track).split(" ")[0], "modules": modules,
                "review_status": "draft_ready" if ready else "needs_review", "missing": missing, "contact_route": route, "route_value": value,
                "recipient": recipient or f"{o['name']} (organisation route)", "language": "English", "offer_ids": WELFARE_OFFERS,
                "outcome": "drafted" if ready else "drafted, held",
                **({"hook": hook, "hook_source_url": reason["url"], "hook_verified_on": reason["verified_on"]} if reason else {})}
        names = (o["name"], name, recipient.split(" (")[0], reason["supported"] if reason else "", leader["greet_name"] if leader else "")
        for text in (body, follow):
            issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(text, WELFARE_OFFERS, ignore=names)]
        issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_first_message(body, ignore=names)]
        add(con, now, plan, subject, body, follow)
        outcomes[plan["outcome"]] += 1
    for e in [dict(r) for r in con.execute("SELECT * FROM enquiries")]:
        request = str(e.get("request") or "").lower()
        if re.search(r"indian|cbse|igcse|cambridge|international curriculum|secondary|teacher|job", request):
            outcomes["parent enquiry: outside Silverleaf's offer, no reply"] += 1
            continue
        body = (f"Hello,\n\nI'm {L.SENDER} from Silverleaf Academy, replying to your question about schools. If you are still looking, applications for "
                f"the 2027 school year are open. We teach Daycare (from 18 months) to Grade 7 in English at five campuses in Arusha, Usa River and "
                f"Boma Ng'ombe. Every family can get {L.family_offer_en()}.\n\nIf it would help, reply with the student's age or grade and the area you "
                f"would live in, and our team will check the right campus and current fees.\n\n{L.SIGNATURE}")
        plan = {"message_id": sid("welfare-enquiry", e["enquiry_id"]), "target_id": e["enquiry_id"], "target_type": "enquiry", "organisation_id": None,
                "relevance_reason": "Public parent enquiry within Silverleaf's levels; one reviewed reply at most.", "cta_type": "Requalification reply",
                "track": "C04", "modules": "VM04", "review_status": "needs_review",
                "missing": ["pdpa_risk risky: a lawful basis approved by Silverleaf's data-protection owner is required before replying.",
                            "Reply only on the original public thread; one reply maximum; no follow-up.", L.CONFIRM_2027],
                "contact_route": "source_url", "route_value": e["source_url"], "recipient": "Author of the public enquiry", "language": "English",
                "offer_ids": FAMILY_OFFERS, "outcome": "drafted, held (risky)"}
        issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(body, FAMILY_OFFERS)]
        add(con, now, plan, "Your question about schools near Arusha", body)
        outcomes[plan["outcome"]] += 1
    return {"outcomes": dict(outcomes), "issues": issues}


# ------------------------------------------------------------------ government
def postal_lines(address) -> tuple[str, str]:
    """('S.L.P. 3013,\\nARUSHA.', 'P.O. Box 3013, Arusha') from a published postal address in either language; ('', '') if none."""
    text = str(address or "").strip()
    m = re.search(r"(?:P\.?\s*O\.?\s*Box|S\.?\s*L\.?\s*P\.?)\s*(?:No\.?\s*)?(\d{1,6})[\s,.]*([A-Za-z' ]*)", text, re.I)
    if not m:
        return (f"{text.rstrip('.')}." if text else ""), text
    number, town = m.group(1), " ".join(m.group(2).split())
    return (f"S.L.P. {number},\n{town.upper()}." if town else f"S.L.P. {number}."), (f"P.O. Box {number}, {town.title()}" if town else f"P.O. Box {number}")


def director_title(council: dict) -> str:
    name = council["name"]
    if "City" in name:
        return "Mkurugenzi wa Jiji"
    if "Municipal" in name:
        return "Mkurugenzi wa Manispaa"
    return "Mkurugenzi Mtendaji wa Halmashauri"


SESSION_SW = ("elimu bure kwa Kiswahili kuhusu maandalizi ya mtoto kuanza shule, kujifunza nyumbani na ratiba ya udahili")
SESSION_EN = "a free talk in Kiswahili on getting children ready for school, learning at home and the admissions calendar"
SAFEGUARDS_SW = ("Mzazi atakayependa taarifa zaidi atajaza fomu yetu kwa hiari yake. Hatutaomba orodha ya wakazi wala taarifa zozote za wakazi, "
                 "na hatutatoa malipo wala zawadi kwa mtu yeyote.")
SAFEGUARDS_EN = ("Parents who want more information will fill in our form only if they choose to. We will not ask for resident lists or any "
                 "residents' information, and we will not offer payments or gifts to anyone.")
ABOUT_SW = ("Silverleaf Academy ni shule binafsi inayofundisha kwa lugha ya Kiingereza, yenye kampasi tano: Arusha City (Sakina), Kijenge na "
            "Ilboru jijini Arusha, Usa River, na Boma Ng'ombe.")
ABOUT_EN = ("Silverleaf Academy is a private English-medium school with five campuses: Arusha City (Sakina), Kijenge and Ilboru in Arusha, "
            "Usa River, and Boma Ng'ombe.")
# The letters describe no services, fees or offers (1 October 2026): they ask for a slot and a short meeting.
MEETING_SW = "Je, itawezekana kupanga kikao kifupi, ana kwa ana au kwa simu, ili kujadili maelezo?"
MEETING_EN = "Would it be possible to arrange a short meeting, either in person or by phone, to discuss the details?"
BOOKLET_SW = "Kila mzazi atapata kijitabu cha mzazi."
BOOKLET_EN = "Every parent will receive a parent booklet."
CLOSE_SW = f"Wako katika ujenzi wa Taifa,\n\n{L.SIGNATURE_SW}"
CLOSE_EN = f"Yours in nation building,\n\n{L.SENDER}\n{L.SENDER_TITLE}, Silverleaf Academy"


def government(con, now, run_cfg) -> dict:
    councils = {c["name"]: c for c in run_cfg["councils"]}
    offices = [dict(r) for r in con.execute("SELECT o.*, g.office_level, g.admin_unit_name, g.parent_admin_unit, g.council_name, g.region, "
                                            "g.proposed_government_track, g.admin_unit_key FROM organisations o JOIN government_office_profiles g "
                                            "USING(organisation_id) ORDER BY g.office_level, o.name")]
    units = {r["unit_key"]: dict(r) for r in con.execute("SELECT * FROM admin_units")}
    posts = {}
    for r in con.execute("SELECT * FROM official_posts"):
        posts.setdefault(r["organisation_id"], {})[r["post_key"]] = dict(r)
    top_wards = {}
    for u in sorted((u for u in units.values() if u["level"] == "ward" and u["in_catchment"] == "yes"), key=lambda u: -(u["ward_score"] or 0)):
        top_wards.setdefault(u["council"], []).append(u["name"])
    outcomes, issues = Counter(), []
    for o in offices:
        level, track = o["office_level"], o["proposed_government_track"] or "GA00 Hold"
        council = councils.get(o.get("council_name") or "", {})
        missing = [L.NATIVE_REVIEW, "Letter on Silverleaf letterhead, delivered by hand or to the official address; approve the session "
                   "content, parent guide and privacy notice first (campaign C11 gates)."]
        ready = False
        if level == "council":
            recipient_post = "council_director"
            title = director_title(o | {"name": o["council_name"]})
            wards = top_wards.get(o["council_name"], [])[:3]
            ward_sw = (f"\n\nTungependa kuanzia katika kata zilizo karibu na kampasi zetu, kama vile {', '.join(wards[:-1])} na {wards[-1]}." if len(wards) > 1
                       else (f"\n\nTungependa kuanzia katika Kata ya {wards[0]}, iliyo karibu na kampasi zetu." if wards else ""))
            ward_en = (f"\n\nWe would like to start in the wards nearest our campuses, such as {', '.join(wards[:-1])} and {wards[-1]}." if len(wards) > 1
                       else (f"\n\nWe would like to start in {wards[0]} ward, near our campuses." if wards else ""))
            subject = "YAH: OMBI LA UTAMBULISHO ILI KUTOA ELIMU KWA WAZAZI KUHUSU MAANDALIZI YA WATOTO KUANZA SHULE"
            # The official postal address, when contact research found one, completes the formal address block.
            postal_sw, postal = postal_lines(o.get("address"))
            addressee = f"{council.get('name_sw', o['council_name'])},\n{postal_sw}" if postal_sw else f"{council.get('name_sw', o['council_name'])}."
            body = (f"{title},\n{addressee}\n\n{subject}\n\n{ABOUT_SW}\n\nTunaomba ushauri wako na barua ya utambulisho "
                    f"kwa Watendaji wa Kata ili, pale itakapofaa, tupewe muda mfupi wa dakika 15 hadi 20 katika mikutano ya wananchi. Tutatoa "
                    f"{SESSION_SW}. {BOOKLET_SW}"
                    f"{ward_sw}\n\n{SAFEGUARDS_SW}\n\n{MEETING_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'City Director' if 'City' in o['council_name'] else 'Municipal Director' if 'Municipal' in o['council_name'] else 'District Executive Director'}, "
                       f"{o['council_name']}{', ' + postal if postal else ''}.\n\nRE: REQUEST FOR AN INTRODUCTION TO GIVE PARENTS INFORMATION ON PREPARING CHILDREN TO START SCHOOL\n\n{ABOUT_EN}\n\n"
                       f"We ask for your advice and a letter introducing us to the ward executive officers so that, where appropriate, we can have a "
                       f"short 15 to 20 minutes at community meetings. We will give {SESSION_EN}. {BOOKLET_EN}"
                       f"{ward_en}\n\n{SAFEGUARDS_EN}\n\n{MEETING_EN}\n\n{CLOSE_EN}")
            follow = (f"{title},\n{addressee}\n\nYAH: UFUATILIAJI WA BARUA YETU YA OMBI LA UTAMBULISHO\n\nTunafuatilia "
                      f"barua yetu kuhusu elimu kwa wazazi kuhusu maandalizi ya watoto kuanza shule. {MEETING_SW}"
                      f"\n\n{CLOSE_SW}")
            modules, cta = "VM14; VM15; VM16; VM17", "Protocol introduction"
            ready = track.startswith("GA01")
            if not ready:
                missing.append("Outside the v1 pilot councils (plan §5.10): hold.")
        elif level in ("ward", "village"):
            recipient_post = "ward_executive_officer" if level == "ward" else "village_executive_officer"
            unit = units.get(o.get("admin_unit_key") or "", {})
            name = o["admin_unit_name"]
            place_sw = "kata yenu" if level == "ward" else "kijiji chenu"
            located = o.get("latitude") not in (None, "") and o.get("campus")
            key = L.campus_key(o.get("campus") or "")
            near = bool(located and key and o.get("distance_km") not in (None, "") and float(o["distance_km"]) <= 25)
            km = round(float(o["distance_km"])) if near else 0
            campus_sw = (f"Kampasi yetu iliyo karibu zaidi ni {L.campus_display(key)} (takriban kilomita {km} kutoka {place_sw})." if near and km >= 1
                         else (f"Kampasi yetu iliyo karibu zaidi ni {L.campus_display(key)}, chini ya kilomita 1 kutoka {place_sw}." if near else ""))
            campus_en = (f"Our nearest campus is {L.campus_display(key)}, about {km} km from your {level}." if near and km >= 1
                         else (f"Our nearest campus is {L.campus_display(key)}, less than 1 km from your {level}." if near else ""))
            forum_sw = f"mkutano ujao wa wananchi wa Kata ya {name}" if level == "ward" else f"mkutano mkuu ujao wa Kijiji cha {name}"
            forum_en = f"the next community meeting of {name} ward" if level == "ward" else f"the next village assembly of {name}"
            head_sw = f"Afisa Mtendaji wa Kata ya {name}" if level == "ward" else f"Afisa Mtendaji wa Kijiji cha {name}"
            subject = f"YAH: OMBI LA NAFASI FUPI KATIKA {'MKUTANO WA WANANCHI WA KATA YA' if level == 'ward' else 'MKUTANO MKUU WA KIJIJI CHA'} {name.upper()}"
            body = (f"{head_sw},\n{council.get('name_sw', o.get('council_name') or '')}.\n\n{subject}\n\nKufuatia utambulisho wa Halmashauri, "
                    f"Silverleaf Academy inaomba nafasi ya dakika 15 hadi 20 katika {forum_sw}, ili kutoa {SESSION_SW}.\n\n{campus_sw + chr(10) + chr(10) if campus_sw else ''}{BOOKLET_SW}"
                    f"\n\n{SAFEGUARDS_SW}\n\n{MEETING_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'Ward' if level == 'ward' else 'Village'} Executive Officer, {name}, {o.get('council_name') or ''}.\n\nRE: REQUEST FOR A "
                       f"SHORT SLOT AT {forum_en.upper()}\n\nFollowing the council's introduction, Silverleaf Academy asks for 15 to 20 minutes at "
                       f"{forum_en}, to give {SESSION_EN}.\n\n{campus_en + chr(10) + chr(10) if campus_en else ''}{BOOKLET_EN}"
                       f"\n\n{SAFEGUARDS_EN}\n\n{MEETING_EN}\n\n{CLOSE_EN}")
            follow = ""
            modules, cta = "VM14; VM15; VM16; VM17", "Convening request"
            missing.append("Held until the council introduction (GA01) is recorded and this post is verified within 90 days (GA02 gate).")
            if unit.get("ward_score") is not None:
                missing.append(f"Ward priority: tier {unit.get('ward_tier')}, score {unit.get('ward_score')}, rank {unit.get('rank_in_cluster')} in "
                               f"{unit.get('campus_cluster')}.")
            if not located:
                missing.append("Ward location unknown: campus line omitted.")
        else:
            recipient_post = "district_administrative_secretary" if level == "district" else "regional_administrative_secretary"
            head_sw = (f"Katibu Tawala wa Wilaya ya {o['admin_unit_name']}" if level == "district" else f"Katibu Tawala wa Mkoa wa {o['admin_unit_name']}")
            subject = "YAH: TAARIFA KUHUSU ELIMU KWA WAZAZI JUU YA MAANDALIZI YA WATOTO KUANZA SHULE"
            body = (f"{head_sw}.\n\n{subject}\n\n{ABOUT_SW}\n\nKwa utambulisho wa Halmashauri husika, tunapanga kutoa {SESSION_SW} katika mikutano ya "
                    f"wananchi, kwa muda mfupi utakaotolewa na Watendaji wa Kata. Tunapenda ofisi yako ifahamu mpango huu, na tutashukuru kwa ushauri "
                    f"wowote.\n\n{SAFEGUARDS_SW}\n\n{CLOSE_SW}")
            english = (f"To the {'District' if level == 'district' else 'Regional'} Administrative Secretary, {o['admin_unit_name']}.\n\nRE: NOTICE OF "
                       f"PARENT INFORMATION SESSIONS ON PREPARING CHILDREN TO START SCHOOL\n\n{ABOUT_EN}\n\nWith the relevant councils' introduction, we "
                       f"plan to give {SESSION_EN} at community meetings, in short slots the ward executive officers allow. We would like your office to "
                       f"know of this plan and would welcome any advice.\n\n{SAFEGUARDS_EN}\n\n{CLOSE_EN}")
            follow = ""
            modules, cta = "VM14", "Courtesy notice"
            missing.append("District and regional offices are not a v1 target (plan §1): hold; coordinate with the B2G owner first.")
        post = posts.get(o["organisation_id"], {}).get(recipient_post, {})
        offer_ids = []  # the letters state no offer, fee or service
        plan = {"message_id": sid("government", o["organisation_id"]), "target_id": o["organisation_id"], "target_type": "organisation",
                "organisation_id": o["organisation_id"],
                "relevance_reason": f"{level.title()} office that can convene or introduce community meetings ({o.get('council_name') or o['admin_unit_name']}).",
                "cta_type": cta, "track": track.split(" ")[0], "modules": modules, "review_status": "draft_ready" if ready else "needs_review",
                "missing": missing, "contact_route": "letter", "route_value": "Official office address (hand delivery)",
                "recipient": f"{post.get('office_title_sw') or recipient_post} ({post.get('office_title') or ''})".strip(),
                "language": "Kiswahili (English meaning attached)", "offer_ids": offer_ids, "outcome": "drafted" if ready else "drafted, held"}
        for text in (body, follow, english):
            issues += [{"message_id": plan["message_id"], "issue": i} for i in L.check_message(text, offer_ids, convening=True,
                                                                                             ignore=(o["name"], o.get("council_name") or ""))]
        add(con, now, plan, subject, body, follow, english)
        outcomes[plan["outcome"]] += 1
    outcomes["named councillors: no direct message (engage through the forum they chair; plan decision 7)"] = con.execute(
        "SELECT COUNT(*) FROM official_posts WHERE post_key='ward_councillor' AND holder_name != ''").fetchone()[0]
    return {"outcomes": dict(outcomes), "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--track", required=True, choices=["welfare", "government"])
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run_cfg = json.loads((ROOT / "data" / "runs" / args.run_id / "run-config.json").read_text(encoding="utf-8"))
    db = ROOT / "outputs" / "runs" / args.run_id / "lead-database.sqlite"
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        con.execute("BEGIN")
        prepare(con)
        result = (welfare if args.track == "welfare" else government)(con, now, run_cfg)
        if result["issues"]:
            raise RuntimeError({"conformance_issues": result["issues"][:10], "count": len(result["issues"])})
        con.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?)", ("offer_version", L.OFFER_VERSION))
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fks:
            raise RuntimeError({"integrity": integrity, "foreign_keys": fks[:5]})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("messages", "outreach_plans")}
    statuses = dict(con.execute("SELECT review_status, COUNT(*) FROM outreach_plans GROUP BY 1").fetchall())
    con.close()
    print(json.dumps({"track": args.track, "run_id": args.run_id, "offer_version": L.OFFER_VERSION, "outcomes": result["outcomes"],
                      "counts": counts, "review_status": statuses, "conformance_issues": 0}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
