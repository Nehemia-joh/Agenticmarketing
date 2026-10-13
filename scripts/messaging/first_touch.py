"""First touch: reach the right person (docs/strategy/partnership-pipelines.md, section 4, approved by the user on 11 October 2026).

Why: relevance, not ambiguity. An ambiguous request to a general inbox (info@, admin@) is more likely to be ignored and may never reach
the person who decides. So the first message depends on who it can reach:
- Case A, a named person with their own (or their role's) address: the letter goes to them unchanged.
- Case B, a named person but only a general inbox: the same letter, explicitly addressed to them (the Attn format): the subject
  'Attn: <Full Name>, <Role> – <segment ending>' and, set apart at the top, the routing line 'For the attention of <Full Name>, <Role>.
  If this inbox does not reach them, we would be grateful if it could be forwarded.' The letter still opens 'Dear <Full Name>,'. When the
  MD, owner or founder is named, no HR head is on file and the company is large enough (open question 21: reach tier P1 or P2, 50 or
  more published staff, or a bank, hospital, college, international organisation, manufacturer, aviation employer or public body), the
  routing line adds ', or your HR lead'.
- Case C, no named person and only a general inbox: a short redirect request instead of the letter (no offer terms), with the
  segment's ask from section 4, and blank follow-ups with the planned next touch from section 5 (fallout) as a note.
- Case B follow-ups (section 5, named-person fallout; applied 11 October 2026): follow-up 1 gives a few offer details from the offer
  register, follow-up 2 is a short close ending with the segment's redirect-style ask (close()), and a plan with an escalation contact
  notes one message to them 5 working days after the close (escalation_note()). Variant A sponsorship follow-ups stay blank.
SACCOS and government letters (delivered by hand, addressed by title) are unchanged.
VICOBA savings groups (docs/plans/vicoba-integration-plan.md, decisions 3 and 6, approved 13 October 2026) have two kinds of their own:
- 'vicoba': the group's officer or committee, in Kiswahili (SEGMENTS_SW). A group is rarely reached by email, so its band comes from the
  route to the group, and the channel (letter, call, email) is a separate property: vicoba_case() holds the band rule, and the exporter
  imports it so drafting and banding share one rule.
- 'vicoba_introducer': an NGO field office, a bank branch or an employer asked to introduce Silverleaf to group committees (English;
  one request per introducer per wave).
Used by draft_master_messages.py (employers, variant A sponsors, public bodies, introducers, VICOBA) and draft_run_messages.py (welfare).
Names are written as the source gives them, with no honorific the source does not state.
"""
from __future__ import annotations

import re
from datetime import date

import offer_lib as L

# kind -> (case B subject ending, case C subject, case C topic (with {org}), case C ask). From section 4, 'Adapting the rule by segment'.
SEGMENTS = {
    "employer": ("staff education benefit", "Staff education benefit – who should we write to?",
                 "a staff education benefit for the children of {org}'s employees",
                 "Who looks after staff welfare and benefits (HR, the welfare officer or the COO)? We would like to send them a short note."),
    "variant_a": ("student sponsorship", "Student sponsorship – who should we write to?", "sponsoring students' education at Silverleaf",
                  "Who looks after the company's community giving? We would like to send them a short note."),
    "public": ("staff education benefit", "Staff education benefit – who should we write to?",
               "a staff education benefit for the children of {org}'s employees",
               "Who heads human resources? We would like to send them a short note."),
    "welfare_home": ("education of the children in your care", "Education of the children in your care – who should we write to?",
                     "the education of the children in {org}'s care",
                     "Who leads the home (or the programme) and looks after the children's schooling? We would like to send them a short note."),
    "funder": ("student sponsorship", "Student sponsorship – who should we write to?", "sponsoring students' education at Silverleaf",
               "Who is the programme officer for your work in Tanzania? We would like to send them a short note."),
    "introducer": ("an education benefit for your members", "An education benefit for your members – who should we write to?",
                   "an education benefit for {org}'s members",
                   "Who looks after member benefits and communications (the executive secretary or CEO)? We would like to send them a short note."),
    # The introducer request is itself the case C equivalent (decision 3b, medium band): it asks to be introduced, never for a list.
    "vicoba_introducer": ("savings groups in your area", "Savings groups in your area – could you introduce us?",
                          "a short Kiswahili talk for the savings groups {org} works with",
                          "Could you introduce us to one or two group committees, or tell us who works with the groups? We do not ask for member "
                          "lists or any member's details; each group decides for itself."),
}
# Kiswahili rows (section 4: 'Kiswahili wording, to be drafted and reviewed by a native speaker'). kind -> (case B subject ending,
# subject, topic (with {org}), ask). Every draft built from these carries offer_lib.NATIVE_REVIEW until its template is approved.
SEGMENTS_SW = {
    "vicoba": ("kikao kifupi na kamati", "Ombi la kikao kifupi na kamati ya {org}",
               "elimu ya watoto wa wanachama wa {org}",
               "Tungependa kuomba nafasi ya dakika 10 hadi 15 katika mojawapo ya vikao vyenu vya wiki, ili kuzungumza kwa Kiswahili kuhusu "
               "maandalizi ya mtoto kuanza shule na kupanga elimu ya watoto."),
}
# The planned next touch after a silent redirect request (section 5, fallout), noted on the plan; nothing is sent from the repository.
NEXT_TOUCH = {
    "employer": "Next touch: front-desk call after 2 working days to ask for the HR or welfare officer's name (see the pipeline draft, fallout)",
    "variant_a": "Next touch: front-desk call after 2 working days to ask who looks after community giving (see the pipeline draft, fallout)",
    "public": "Next touch: call the HR office or registry after 2 working days to ask for the HR head's name (see the pipeline draft, fallout)",
    "welfare_home": "Next touch: a call to the home's office after 2 working days, then a letter left at the office (see the pipeline draft, fallout)",
    "funder": "Next touch: none by phone (funders are mostly abroad, so email only), dormant until the funder's next budget cycle (see the pipeline draft, fallout)",
    "introducer": "Next touch: a call to the secretariat after 2 working days (see the pipeline draft, fallout)",
    # VICOBA (vicoba-integration-plan.md decision 4, fallout): silence is never a 'no'.
    "vicoba": ("Next touch: a group that does not answer is asked once more through its introducer, then dormant until its next savings "
               "cycle (dormant_no_response), and never an unannounced visit to a meeting"),
    "vicoba_introducer": ("Next touch: a call to the introducer's office after 2 working days, then a letter by hand, then dormant "
                          "(dormant_no_route)"),
}
# Named-person fallout (section 5, 'Contacted, no reply (named person)'; applied to the case B drafts on 11 October 2026): follow-up 1
# gives a few offer details from the offer register, follow-up 2 closes with a redirect-style ask, then one message to the escalation
# contact if one exists (noted on the plan; no draft is written to them). Variant A sponsors are left out: the register approves no
# sponsorship follow-up before a reply. kind -> (the topic of the close, with {org}; who it might sit with, or '').
CLOSE = {
    "employer": ("this", "HR or the welfare officer"),
    "public": ("this", "the head of human resources"),
    "introducer": ("member benefits and communications", ""),
    "welfare_home": ("this", "the head of the home or programme"),
    "funder": ("this", "the programme officer for your work in Tanzania"),
}
NAMED_FALLOUT_KINDS = set(CLOSE)
# The Kiswahili close of a VICOBA group draft (decision 3b, high direct: 'one follow-up, a close, then dormant until the next cycle').
# kind -> (Kiswahili close, its English meaning), each with {org}.
CLOSE_SW = {
    "vicoba": ("Huu ni ujumbe wangu wa mwisho kuhusu ombi letu. Kama si wakati mwafaka sasa, tutawasiliana tena kabla ya mzunguko wenu "
               "ujao wa akiba. Asanteni.",
               "This is my last note about our request. If now is not a good time, we will be in touch again before your next savings cycle. "
               "Thank you."),
}
VICOBA_KINDS = {"vicoba", "vicoba_introducer"}
ESCALATION_START = "Then: one message to "
CLOSE_END = "Otherwise I will close this for now."
ROUTING_START = "For the attention of "
REDIRECT_START = "Hello,\n\nI am writing from Silverleaf Academy in Arusha about "
SIGN_OFF = f"Thank you,\n{L.SENDER}\n{L.SENDER_TITLE}, Silverleaf Academy"
GENERAL_INBOX = re.compile(r"^(info|infos|admin|contact|contacts|office|hello|enquiries|enquiry|inquiries|inquiry|mail|reservations?|bookings?|"
                           r"sales|customercare|customer|support|reception)\b", re.I)
TOP_ROLE = re.compile(r"\bmd\b|managing director|owner|founder|proprietor|\bceo\b|chief executive", re.I)
LARGE_KIND = re.compile(r"bank|hospital|college|universit|international organi[sz]ation|manufactur|industrial|aviation|airline|airport|aeroway|"
                        r"air charter|office:government|public", re.I)


def short_role(role: str) -> str:
    """The role as a short title for the routing line: no bracketed notes, phone numbers or trailing clauses."""
    text = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", str(role or ""))
    text = re.sub(r"\+?\d[\d\s\-–]{6,}\d", " ", text)
    text = text.split(";")[0]
    text = " ".join(text.split()).strip(" ,.;:-–—")
    if len(text) > 60:
        cut = max(text.rfind(",", 0, 60), text.rfind(" and ", 0, 60))
        text = text[:cut] if cut > 10 else text[:60].rsplit(" ", 1)[0]
    return text.strip(" ,.;:-–—")


def strip_routing(body: str) -> str:
    """The letter without an earlier routing line (re-running never adds a second one)."""
    if body.startswith(ROUTING_START) and "\n\n" in body:
        return body.split("\n\n", 1)[1]
    return body


def is_redirect(body: str) -> bool:
    return str(body or "").startswith(REDIRECT_START)


def attn(kind: str, body: str, name: str, role: str, hr_lead: bool = False) -> tuple[str, str]:
    """(subject, body) in the Attn format for a named person reached only through a general inbox (case B)."""
    who = f"{name}, {short_role(role)}" if short_role(role) else name
    routing = (f"{ROUTING_START}{who}{', or your HR lead' if hr_lead else ''}. "
               "If this inbox does not reach them, we would be grateful if it could be forwarded.")
    return f"Attn: {who} – {SEGMENTS[kind][0]}", f"{routing}\n\n{strip_routing(body)}"


def redirect(kind: str, org_name: str) -> tuple[str, str]:
    """(subject, body) of the redirect request (case C): one line on what it is about, the ask, nothing more."""
    _, subject, topic, ask = SEGMENTS[kind]
    return subject, f"{REDIRECT_START}{topic.format(org=org_name)}.\n\n{ask}\n\n{SIGN_OFF}"


def close(kind: str, org_name: str, greet: str, hr_named: bool = False) -> str:
    """Follow-up 2 of a case B draft: a short close that ends with the redirect-style ask (section 5), with the sender's usual sign-off.
    An employer's named HR person is not asked whether it sits with HR."""
    topic, who = CLOSE[kind]
    if kind == "employer" and hr_named:
        who = "the welfare officer"
    sits = "sit" if topic.endswith("s") and topic != "this" else "sits"
    such = f", such as {who}," if who else ","
    return f"{greet}\n\nIf {topic} {sits} with someone else at {org_name}{such} who should I write to? {CLOSE_END}\n\n{L.SIGNATURE}"


def escalation_note(recipient: str) -> str:
    """The plan note for the last fallout step (section 5): one message to the escalation contact 5 working days after the close.
    Written as one note (no '; ' inside), so it is replaced, never repeated, when the escalation contact changes."""
    who = " ".join(str(recipient or "").replace(";", ",").split())
    return f"{ESCALATION_START}{who} 5 working days after the close" if who else ""


def hr_lead(role: str, hr_on_file: bool, tier: str = "", headcount=None, kind_text: str = "") -> bool:
    """Question 21: the MD, owner or founder is named, no HR head is on file, and the company is large enough."""
    try:
        staff = float(headcount) if headcount not in (None, "") else 0
    except (TypeError, ValueError):
        staff = 0
    large = str(tier) in ("P1", "P2") or staff >= 50 or bool(LARGE_KIND.search(kind_text or ""))
    return bool(TOP_ROLE.search(role or "")) and not hr_on_file and large


# ------------------------------------------------------------------ VICOBA: the band rule (vicoba-integration-plan.md decision 3b)
VICOBA_BANDS = ("high-direct", "high-indirect", "medium", "low")
VICOBA_CHANNELS = ("letter", "call", "email")
TEMPLATE_HOLD = "Kiswahili template not yet approved by a native speaker (data/reference/kiswahili-reviews.json)"
# Introducer kinds that are master organisations (one introducer plan per introducer per wave) and the request each gets.
MASTER_INTRODUCER = {"ngo_field_office": "ngo", "bank_branch": "bank", "employer": "employer"}
GOV_REF = re.compile(r"^gov:([a-z0-9\-]+):([A-Za-z0-9_\-]+)$")
MASTER_REF = re.compile(r"^O[0-9a-f]{12}$")


def _last(facts: dict, field: str) -> str:
    values = [v for v in facts.get(field, []) if v not in (None, "")]
    return str(values[-1]) if values else ""


def _route(org: dict) -> str:
    return "email" if "@" in str(org.get("email") or "") else "call" if str(org.get("phone") or "").strip() else ""


def vicoba_introducer(group: dict, orgs: dict, gov_offices: dict, planned: set) -> dict:
    """The route through which a group is first reached, from the contract's facts (section 4.1: introducer_kind, introducer_ref,
    sponsor_name, sponsor_kind, sponsor_ref, employer_ref), which the adder and scripts/master/link_vicoba_introducers.py record.
    A workplace group whose employer is already in a conversation joins that employer's deal (decision 4), so the employer is its
    introducer. Returns the kind, ref, master organisation (NGO, bank or employer), name, whether the route is ready, why not, its channel
    and the request a master introducer gets ('ngo', 'bank', 'employer')."""
    f = group.get("facts", {})
    kind, ref = _last(f, "introducer_kind"), _last(f, "introducer_ref")
    sponsor_kind, sponsor_ref, sponsor_name = _last(f, "sponsor_kind"), _last(f, "sponsor_ref"), _last(f, "sponsor_name")
    employer = _last(f, "employer_ref")
    if employer in orgs and employer in planned:
        kind, ref = "employer", employer
    elif not kind and sponsor_kind in ("ngo", "bank") and sponsor_ref in orgs:
        kind, ref = ("ngo_field_office" if sponsor_kind == "ngo" else "bank_branch"), sponsor_ref
    out = {"kind": kind, "ref": ref, "organisation_id": "", "name": "", "ready": False, "why": "", "channel": "", "request": "", "gov_office": ""}
    if sponsor_name and not sponsor_ref:
        out["why"] = f"the sponsor link is unverified ({sponsor_name}): link it through data/reference/vicoba-introducers.json"
        return out
    if kind in ("cdo_ward", "cdo_council"):
        m = GOV_REF.match(ref)
        office = gov_offices.get(m.group(2)) if m else None
        if not office:
            out["why"] = "the community development office is not linked to a government-run office"
            return out
        out.update(gov_office=m.group(2), name=office["name"], channel="letter")
        out["ready"] = office["council_introduced"]
        out["why"] = "" if out["ready"] else (f"the council ({office['council'] or 'unknown'}) has no recorded introduction (GA01) yet: the "
                                               "ward CDO letter in the government run waits for it")
        return out
    if kind in MASTER_INTRODUCER:
        org = orgs.get(ref) if MASTER_REF.match(ref or "") else None
        if not org:
            out["why"] = "the introducer is not linked to a master organisation (data/reference/vicoba-introducers.json)"
            return out
        out.update(organisation_id=ref, name=org.get("name") or "", request=MASTER_INTRODUCER[kind], channel=_route(org))
        out["ready"] = bool(out["channel"])
        out["why"] = "" if out["ready"] else "the introducer publishes no email or phone"
        return out
    if kind == "faith_office":
        out["why"] = "faith offices are not approached as introducers until the user decides (vicoba-integration-plan.md decision 5, F6)"
    elif kind == "group_published":
        out["why"] = "the group's own route has no officer named for it on file"
    else:
        out["why"] = "no introducer route (ward CDO, NGO field office, bank branch or a route the group publishes)"
    return out


def vicoba_officer(contact: dict, bases: list, as_of: date, last_confirmed: str) -> dict:
    """A group officer as the band rule sees one: a name, and whether a role route is published for them (phone_basis
    published_for_role, with a route, confirmed within 12 months) or they agreed to be contacted (phone_basis consent_recorded <date>)."""
    basis = bases[-1] if bases else ""
    try:
        recent = (as_of - date.fromisoformat(str(last_confirmed)[:10])).days <= 365
    except ValueError:
        recent = False
    route = any(str(contact.get(k) or "").strip() for k in ("role_phone", "published_role_email", "named_email"))
    direct = basis.startswith("consent_recorded") or (basis == "published_for_role" and route and recent)
    return {"contact_id": contact.get("contact_id"), "name": contact.get("name") or "", "role": contact.get("role") or "", "direct": direct}


def vicoba_case(group: dict, officers=(), introducer: dict | None = None, *, template_approved: bool = False, introduced: bool = False) -> dict:
    """The band, first-touch case and channel of a VICOBA group (decision 3b, approved 13 October 2026).

    - low (held, S0): any record_status other than 'complete'; no ready route (the CDO's council has no GA01 introduction yet, the
      sponsor link is unverified, the introducer is not linked or publishes no route); or the Kiswahili template is not yet approved;
    - high-direct, case A, channel call: a group officer with a role route published for them and confirmed within 12 months, or who
      agreed by phone to be contacted (consent recorded): a Kiswahili call, then the letter 'as discussed';
    - high-indirect, case B, channel letter: a named officer reachable only through the introducer, or an introducer that has introduced
      the group (outcome 'introduced'): the Kiswahili letter to the committee, handed over by the introducer;
    - medium, case C, the introducer's channel: group identified and an introducer route ready, no named officer: the introducer request.
    'band_after_review' is the band once the template is approved, so a reviewer sees what the review alone would unlock. The channel
    is a property apart from the band; a group on the call sheet keeps its band."""
    introducer = introducer or {"kind": "", "ready": False, "why": "no introducer route", "channel": ""}
    status = group.get("record_status") or ""
    officers = list(officers)
    direct = [o for o in officers if o.get("direct")]
    named = [o for o in officers if o.get("name")]
    holds = []
    if status != "complete":
        holds.append(f"record {status or 'without a status'}")
    if not direct and not introduced and not introducer.get("ready"):
        holds.append(introducer.get("why") or "no ready introducer route")
    if direct:
        band, case, channel = "high-direct", "A", "call"
    elif named or introduced:
        band, case, channel = "high-indirect", "B", "letter"
    else:
        band, case, channel = "medium", "C", introducer.get("channel") or ""
    after_review = "low" if holds else band
    if not template_approved:
        holds.append(TEMPLATE_HOLD)
    if holds:
        band, case, channel = "low", "", ""
    return {"band": band, "case": case, "channel": channel, "introducer_kind": introducer.get("kind") or "", "holds": holds,
            "band_after_review": after_review, "women_group": bool(group.get("women_group"))}


def vicoba_inputs(con, government_db=None, as_of: date | None = None) -> dict:
    """What the band rule reads, from the master and (read-only) the government run, for the CDO offices and whether their council's
    introduction is recorded (protocol_status 'introduced'): {'groups', 'officers', 'introducers', 'order', 'orgs'}, where 'order' is the
    wave order, women's groups first (section 0). The exporter can call this and vicoba_case() to band exactly as the drafter does."""
    import sqlite3
    import sys
    from pathlib import Path
    sys.path.insert(0, str(L.ROOT / "scripts" / "master"))
    import add_vicoba_groups as V  # the contract's reader: load_vicoba_groups, wave_order
    as_of = as_of or date.today()
    row_factory = con.row_factory
    con.row_factory = sqlite3.Row
    try:
        groups = V.load_vicoba_groups(con)
        orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT organisation_id, name, segment, email, phone FROM organisations")}
        planned = {r[0] for r in con.execute("SELECT organisation_id FROM outreach_plans WHERE segment NOT IN (?, ?)",
                                             (L.VICOBA_GROUP_SEGMENT, L.VICOBA_INTRODUCER_SEGMENT))}
        bases, contacts = {}, {}
        for r in con.execute("SELECT entity_id, value FROM facts WHERE entity_type='contact' AND field='phone_basis' ORDER BY rowid"):
            bases.setdefault(r["entity_id"], []).append(r["value"])
        if groups:
            marks = ",".join("?" * len(groups))
            for r in con.execute(f"SELECT * FROM contacts WHERE organisation_id IN ({marks})", tuple(groups)):
                contacts.setdefault(r["organisation_id"], []).append(dict(r))
    finally:
        con.row_factory = row_factory
    gov_offices = {}
    if government_db and Path(government_db).exists():
        g = sqlite3.connect(f"file:{Path(government_db).as_posix()}?mode=ro", uri=True)
        introduced = {c for (c,) in g.execute("SELECT council_name FROM government_office_profiles WHERE office_level='council' "
                                              "AND protocol_status='introduced'")}
        for oid, name, council in g.execute("SELECT o.organisation_id, o.name, p.council_name FROM organisations o JOIN "
                                            "government_office_profiles p USING(organisation_id)"):
            gov_offices[oid] = {"name": name, "council": council or "", "council_introduced": (council or "") in introduced}
        g.close()
    officers = {gid: [vicoba_officer(c, bases.get(c["contact_id"], []), as_of, groups[gid].get("last_confirmed") or "")
                      for c in contacts.get(gid, []) if c.get("name")] for gid in groups}
    introducers = {gid: vicoba_introducer(groups[gid], orgs, gov_offices, planned) for gid in groups}
    return {"groups": groups, "officers": officers, "introducers": introducers, "order": V.wave_order(groups), "orgs": orgs}
