"""First touch: reach the right person (docs/strategy/partnership-pipelines-draft.md, section 4, approved by the user on 11 October 2026).

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
Savings groups (Kiswahili wording still to be drafted) and government letters (delivered by hand, addressed by title) are unchanged.
Used by draft_master_messages.py (employers, variant A sponsors, public bodies, introducers) and draft_run_messages.py (welfare).
Names are written as the source gives them, with no honorific the source does not state.
"""
from __future__ import annotations

import re

import offer_lib as L

# kind -> (case B subject ending, case C subject, case C topic (with {org}), case C ask). From section 4, 'Adapting the rule by segment'.
SEGMENTS = {
    "employer": ("staff education benefit", "Staff education benefit – who should we write to?",
                 "a staff education benefit for the children of {org}'s employees",
                 "Who looks after staff welfare and benefits (HR, the welfare officer or the COO)? We would like to send them a short note."),
    "variant_a": ("student sponsorship", "Student sponsorship – who should we write to?", "sponsoring students' education",
                  "Who looks after the company's community giving? We would like to send them a short note."),
    "public": ("staff education benefit", "Staff education benefit – who should we write to?",
               "a staff education benefit for the children of {org}'s employees",
               "Who heads human resources? We would like to send them a short note."),
    "welfare_home": ("education of the children in your care", "Education of the children in your care – who should we write to?",
                     "the education of the children in {org}'s care",
                     "Who leads the home (or the programme) and looks after the children's schooling? We would like to send them a short note."),
    "funder": ("student sponsorship", "Student sponsorship – who should we write to?", "sponsoring students' education",
               "Who is the programme officer for your work in Tanzania? We would like to send them a short note."),
    "introducer": ("an education benefit for your members", "An education benefit for your members – who should we write to?",
                   "an education benefit for {org}'s members",
                   "Who looks after member benefits and communications (the executive secretary or CEO)? We would like to send them a short note."),
}
# The planned next touch after a silent redirect request (section 5, fallout), noted on the plan; nothing is sent from the repository.
NEXT_TOUCH = {
    "employer": "Next touch: front-desk call after 2 working days to ask for the HR or welfare officer's name (see the pipeline draft, fallout)",
    "variant_a": "Next touch: front-desk call after 2 working days to ask who looks after community giving (see the pipeline draft, fallout)",
    "public": "Next touch: call the HR office or registry after 2 working days to ask for the HR head's name (see the pipeline draft, fallout)",
    "welfare_home": "Next touch: a call to the home's office after 2 working days, then a letter left at the office (see the pipeline draft, fallout)",
    "funder": "Next touch: none by phone (funders are mostly abroad, so email only), dormant until the funder's next budget cycle (see the pipeline draft, fallout)",
    "introducer": "Next touch: a call to the secretariat after 2 working days (see the pipeline draft, fallout)",
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
