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
NOT_LINKED_HOLD = "introducer links not recorded yet (run scripts/master/link_vicoba_introducers.py)"
FAITH_HOLD = "faith offices are not approached as introducers until the user decides (vicoba-integration-plan.md decision 5, F6)"
# The band properties scripts/master/link_vicoba_introducers.py writes on each group, one current value each ('none' = not known).
# The intake's own introducer_kind and introducer_ref are proposals only and are never read here.
LINK_FIELDS = ("introducer_status", "linked_introducer_kind", "linked_introducer_ref", "linked_introducer_name", "linked_introducer_db",
               "linked_introducer_state", "introducer_ready", "introducer_outcome", "officer_route", "officer_confirmed_on", "channel")
# Master introducer kinds that get a 'VICOBA introducers' request, and the request each gets (draft_master_messages.py).
MASTER_INTRODUCER = {"ngo_field_office": "ngo", "bank_branch": "bank", "employer": "employer"}
MASTER_REF = re.compile(r"^O[0-9a-f]{12}$")

# The Kiswahili group templates (decision 6, samples a and e). Placeholders {address}, {group} and {campus} are filled per group;
# a template's version (offer_lib.template_version) covers its text and the fixed sentences it inserts, so a review approves exactly
# this wording. draft_master_messages.py writes the drafts and their English meaning from these.
SIGN_SW = f"Kwa heshima,\n{L.SIGNATURE_SW}"
VICOBA_TEMPLATES = {
    "vicoba-group-request": (
        SEGMENTS_SW["vicoba"][1].replace("{org}", "{group}"),
        "{address}Habari Kamati ya {group},\n\nNinaandika kuhusu " + SEGMENTS_SW["vicoba"][2].replace("{org}", "{group}") + ". "
        + SEGMENTS_SW["vicoba"][3] + "\n\n" + L.INTRO_SW + "\n\nJe, itawezekana kupanga kikao kifupi na kamati, ana kwa ana au kwa simu, ili "
        "tukubaliane siku inayofaa?" + "\n\n" + SIGN_SW),
    "vicoba-group-follow-up": (
        "", "Habari Kamati ya {group},\n\nNinafuatilia barua yangu ya kuomba dakika 10 hadi 15 katika mojawapo ya vikao vyenu vya wiki, ili "
        "kuzungumza kwa Kiswahili kuhusu maandalizi ya mtoto kuanza shule. Je, kamati ingependa hilo? Kama ndiyo, tujulisheni siku na saa "
        "mnayokutana.\n\n" + SIGN_SW),
    "vicoba-group-close": ("", "Habari Kamati ya {group},\n\n" + CLOSE_SW["vicoba"][0] + "\n\n" + SIGN_SW),
    "vicoba-group-offer": (
        "", "Habari Kamati ya {group},\n\nAsante kwa jibu lenu. Kwa familia zote za Silverleaf tunatoa: " + L.family_offer_sw() + ".\n\n"
        "Vikundi vya kuweka akiba pia vina punguzo la kikundi. " + L.of07_sw() + "\n\n{campus}\n\nJe, tunaweza kukubaliana siku ya "
        "kuzungumza na wanachama katika kikao chenu cha wiki?\n\n" + SIGN_SW),
}


def vicoba_template_versions() -> dict:
    """{template_id: version} of the VICOBA group templates."""
    return {tid: L.template_version(subject, body, L.network_line_sw()) for tid, (subject, body) in VICOBA_TEMPLATES.items()}


def vicoba_templates_approved(reviews: dict | None = None) -> bool:
    """True when data/reference/kiswahili-reviews.json approves the current version of every VICOBA group template."""
    reviews = reviews if reviews is not None else L.kiswahili_reviews()
    return all(L.kiswahili_approved(t, v, reviews) for t, v in vicoba_template_versions().items())


def _last(facts: dict, field: str) -> str:
    values = [v for v in facts.get(field, []) if v not in (None, "")]
    return str(values[-1]) if values else ""


def _value(facts: dict, field: str) -> str:
    """A band property's current value, '' for 'none' or absent."""
    value = _last(facts, field)
    return "" if value == "none" else value


def _recent(value: str, as_of: date) -> bool:
    try:
        return (as_of - date.fromisoformat(str(value)[:10])).days <= 365
    except ValueError:
        return False


def vicoba_link(group: dict) -> dict:
    """The group's introducer as link_vicoba_introducers.py recorded it (its band properties), for the band rule and the drafter."""
    f = group.get("facts", {})
    p = {field: _value(f, field) for field in LINK_FIELDS}
    ran = any(f.get(field) for field in LINK_FIELDS)
    kind, ref, db = p["linked_introducer_kind"], p["linked_introducer_ref"], p["linked_introducer_db"]
    master = db == "master" and bool(MASTER_REF.match(ref)) and kind in MASTER_INTRODUCER
    return {"ran": ran, "status": p["introducer_status"], "kind": kind, "ref": ref, "name": p["linked_introducer_name"], "db": db,
            "state": p["linked_introducer_state"], "ready": p["introducer_ready"], "outcome": p["introducer_outcome"],
            "officer_route": p["officer_route"], "officer_confirmed_on": p["officer_confirmed_on"], "channel": p["channel"],
            "organisation_id": ref if master else "", "request": MASTER_INTRODUCER[kind] if master else ""}


def vicoba_assess(group: dict, *, template_approved: bool | None = None, as_of: date | None = None) -> dict:
    """The band, first-touch case and channel of a VICOBA group (decision 3b, approved 13 October 2026), from the band properties
    link_vicoba_introducers.py writes (LINK_FIELDS):
    - low (held, S0): the linker has not run for the group; the record is not 'complete'; no usable route (no accepted link, the
      introducer not ready: the council's introduction not recorded, to confirm, outside the region, another conversation first, no
      published route; the introducer declined; a faith office, F6); or the Kiswahili template version not yet approved;
    - high-direct, case A: officer_route published_for_role confirmed within 12 months, or consent_recorded <date>; a Kiswahili call,
      then the letter 'as discussed';
    - high-indirect, case B: introducer_outcome 'introduced <date>' (it overrides a conversation-first state: the existing conversation
      produced the introduction) or officer_route known_through_introducer <date>; the letter handed over by the introducer;
    - medium, case C: an accepted link whose introducer is ready (introducer_ready 'yes'), no officer route: the introducer request.
    The channel is the linker's 'channel' (call, letter, email), with call for case A and letter for case B when it gives none.
    'band_after_review' is the band once the template is approved."""
    as_of = as_of or date.today()
    link = vicoba_link(group)
    route, outcome = link["officer_route"], link["outcome"]
    direct = route.startswith("consent_recorded") or (route == "published_for_role" and _recent(link["officer_confirmed_on"], as_of))
    introduced = outcome.startswith("introduced") or route.startswith("known_through_introducer")
    holds = []
    if not link["ran"]:
        holds.append(NOT_LINKED_HOLD)
    status = group.get("record_status") or ""
    if status != "complete":
        holds.append(f"record {status or 'without a status'}")
    usable = link["status"] == "linked" and link["ready"] == "yes" and not outcome.startswith("declined")
    if link["kind"] == "faith_office" and not introduced:
        usable = False
    if direct:
        band, case, channel = "high-direct", "A", link["channel"] or "call"
    elif introduced and link["status"] == "linked":
        band, case, channel = "high-indirect", "B", link["channel"] or "letter"
    elif usable:
        band, case, channel = "medium", "C", link["channel"]
    else:
        band, case, channel = "low", "", ""
        if link["ran"]:
            if outcome.startswith("declined"):
                holds.append(f"the introducer {outcome}")
            elif link["kind"] == "faith_office":
                holds.append(FAITH_HOLD)
            elif link["status"] != "linked":
                holds.append("no accepted introducer link (data/reference/vicoba-introducers.json)" if link["status"] != "to_confirm"
                             else "introducer named by the intake, link to confirm (data/reference/vicoba-introducers.json)")
            else:
                holds.append(f"introducer {link['ready'] or 'not ready'}")
    after_review = "low" if holds else band
    if not (vicoba_templates_approved() if template_approved is None else template_approved):
        holds.append(TEMPLATE_HOLD)
    if holds:
        band, case, channel = "low", "", ""
    return {"band": band, "case": case, "channel": channel, "introducer_kind": link["kind"], "introducer": link, "holds": holds,
            "band_after_review": after_review, "women_group": bool(group.get("women_group"))}


def vicoba_case(group: dict, *, template_approved: bool | None = None, as_of: date | None = None) -> str:
    """The group's band ('high-direct', 'high-indirect', 'medium' or 'low'), for the call sheet and the exporter. The group is a
    row of add_vicoba_groups.load_vicoba_groups(); vicoba_assess() gives the case, channel and why it is held."""
    return vicoba_assess(group, template_approved=template_approved, as_of=as_of)["band"]
