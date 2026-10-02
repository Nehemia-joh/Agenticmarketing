#!/usr/bin/env python3
"""Draft the first message for employers that publish education or community giving, and consolidate every company's first message.

- Variant A (sponsorship of students, any size, including textbooks, transport or meals) for companies that fund education
  (strong fit); variant B (a partnership on an education benefit for the children of staff, no offer terms) for every other
  company. The form follows the user's template of 30 September 2026.
- Only the companies in data/reference/employer-sponsorship-reasons.json get these drafts. Each entry holds one sourced fact; its
  source URL, read date and verbatim excerpt come from the master's lead_briefs and are printed with the draft.
- Addressee: the best verified named decision-maker (human resources, owner, founder, managing director or CEO, general
  manager, director) with a full name; otherwise "<company> team". No honorific is guessed.
- Route: the person's direct published email, else the company's email.
- Checks: no offer terms (first-message rule), no figure that is not in the register, at most 200 words before the sign-off.

Read-only. Writes outputs/messages/Silverleaf Employer Sponsorship Drafts - <date>.md: these drafts, then every other company's
chosen first message from the master (variant B), the held ones, and the duplicate records. scripts/master/assign_message_variants.py
stores the drafts in the master (variant_subject, variant_body); run it first, so the file and the workbook agree.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402  (role ranking and contact verification)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
REASONS = ROOT / "data" / "reference" / "employer-sponsorship-reasons.json"
OUT = ROOT / "outputs" / "messages"
SENDER = "Mariam Haji\nMarketing and Partnership Coordinator\nSilverleaf Academy"
LEGAL_SUFFIX = re.compile(r"[\s,]+((Company|Co\.?)\s+)?(Ltd\.?|Limited)$", re.I)


def trade_name(name: str, organisation_id: str) -> str:
    """The name as the company trades: a reviewed trading name, else the record name without a legal suffix."""
    text = L.display_name(name, organisation_id)
    while LEGAL_SUFFIX.search(text):
        text = LEGAL_SUFFIX.sub("", text).strip()
    return text


def addressee(contacts):
    """The best verified named decision-maker, or None."""
    best = None
    for c in contacts:
        verification = c["verification"] or ""
        name = L.greeting_name(c["name"])
        if not R.VERIFIED.search(verification) or R.UNUSABLE.search(verification) or len(name.split()) < 2 or re.search(r"\d|\?", name):
            continue
        rank = R.role_rank(c["role"])
        if rank is None or rank > 2:  # a request for giving goes to the owner, chief executive, general manager or a director
            continue
        direct = c["named_email"] or c["published_role_email"]
        key = (rank, 0 if direct else 1, 1 if re.search(r"co-?\s?founder", c["role"] or "", re.I) else 0, name)
        if best is None or key < best[0]:
            best = (key, c, name)
    return best[1:] if best else None


def suggestion(contacts):
    """The senior contact a person might confirm when no verified one exists (not used in the letter)."""
    seen = sorted(((R.role_rank(c["role"]), L.greeting_name(c["name"]), c["role"]) for c in contacts
                   if R.role_rank(c["role"]) is not None and len(L.greeting_name(c["name"]).split()) >= 2 and not re.search(r"retired", c["role"] or "", re.I)), key=lambda t: (t[0], t[1]))
    return "; ".join(f"{n} ({r})" for _, n, r in seen[:2])


def role_of(role) -> str:
    """'the Managing Director of' from a published role, or '' when it is too long or messy to quote."""
    r = " ".join(str(role or "").split())
    if not r or len(r) > 45 or re.search(r"[();/]", r):
        return ""
    return f"a {r.lower()} of" if r.lower().startswith("co-") else f"the {r} of"


def possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def pick_route(who, org, contacts, chosen) -> str:
    """The person's direct email; otherwise the company's own address, preferring a generic one."""
    if who and (who[0]["named_email"] or who[0]["published_role_email"]):
        return who[0]["named_email"] or who[0]["published_role_email"]
    pool = []  # the address chosen for the company first, then the record's, then those published with the contacts
    for source in (chosen["contact_channel"] if chosen else "", org["email"], *[c["shared_email"] for c in contacts]):
        pool += [e for e in sorted(R.emails(source)) if e not in pool]
    if who:
        first = who[1].split()[0].lower()
        personal = [e for e in pool if e.split("@")[0].startswith(first)]
        if personal:
            return personal[0]
    generic = [e for e in pool if re.match(r"(info|contact|hello|office|admin|enquiries|reservations|bookings|operations|sales)", e)]
    return (generic or pool or [""])[0]


GREETING = "My name is Mariam Haji, Marketing and Partnership Coordinator at Silverleaf Academy, based in Arusha."
ASK = {
    # A: sponsorship. No number of students, so the reply can go high or low; in-kind help gives a small way to say yes.
    "A": ("We are seeking sponsorships for students to help cover school fees and other education-related costs. Support of any size helps, "
          "including a contribution towards textbooks, transport or meals. I would welcome the chance to share more about our school and "
          "students, and to discuss whether this might fit within {org_possessive} current community or charitable initiatives."),
    # B: partnership on an education benefit for staff. Request first: no offer terms until the company replies.
    "B": ("We are looking to set up a partnership with {org} to provide an education benefit for the children of your staff. I would welcome "
          "the chance to explain how it could work, and to discuss whether it might suit you and your team."),
}
SUBJECT = {"A": "Sponsorship for students at Silverleaf Academy", "B": "A partnership on education benefits for {org} staff"}


def variant_for(fit: str) -> str:
    """A (sponsorship) only for a strong fit, where the company funds education; B (an education benefit for staff) for every other company."""
    return "A" if fit == "strong" else "B"


def compose(org_name: str, who, reason: dict, variant: str = "A") -> str:
    if who:
        contact, name = who
        role = reason["role"]  # how this person's role reads, with its preposition; a named addressee needs one in the reasons file
        opening = (f"Dear {name},\n\n{GREETING} "
                   f"I understand that you are {role} {org_name}, and that the company {reason['clause']}. "
                   f"It is this commitment to {reason['commitment']} that led me to reach out to you directly.")
    else:
        routing = ("whoever leads the company's community or charitable giving" if variant == "A" else "whoever looks after staff welfare or benefits")
        opening = (f"Dear {org_name} team,\n\n{GREETING} "
                   f"I understand that {org_name} {reason['clause']}. It is this commitment to {reason['commitment']} that led me to write. "
                   f"I would be grateful if this could reach {routing}.")
    ask = ASK[variant].format(org=org_name, org_possessive=possessive(org_name))
    return (f"{opening}\n\n{ask}\n\n"
            "Would it be possible to arrange a short meeting, either in person or by phone, to discuss this further?\n\n"
            f"Thank you very much for your time and consideration.\n\nWarm regards,\n{SENDER}")


def build_drafts(con):
    """(rows, issues): the variant draft for every company in the reasons file, each checked against the offer register."""
    reasons = json.loads(REASONS.read_text(encoding="utf-8"))["organisations"]
    rows, issues = [], []
    for oid, reason in reasons.items():
        org = dict(con.execute("SELECT * FROM organisations WHERE organisation_id=?", (oid,)).fetchone())
        contacts = [dict(r) for r in con.execute("SELECT * FROM contacts WHERE organisation_id=?", (oid,))]
        name = trade_name(org["name"], oid)
        if reason["fit"] == "hold":
            rows.append({"oid": oid, "org": name, "fit": "hold", "hold_reason": reason["hold_reason"]})
            continue
        brief = con.execute("SELECT source_url, source_date, accessed_on, excerpt FROM lead_briefs WHERE organisation_id=? AND fact LIKE ? || '%'",
                            (oid, reason["fact"])).fetchone()
        if not brief:
            issues.append(f"{name}: no lead brief starts with the cited fact")
            continue
        who = addressee(contacts)
        if who and not reason.get("role"):  # a named addressee needs a role that reads well; otherwise address the team
            phrase = role_of(who[0]["role"])
            reason = {**reason, "role": phrase} if phrase else reason
            who = who if phrase else None
        chosen = con.execute("SELECT contact_channel, channel_attribution FROM outreach_plans WHERE organisation_id=? AND selection='Candidate for review'", (oid,)).fetchone()
        route = pick_route(who, org, contacts, chosen)
        bodies = {v: compose(name, who, reason, v) for v in ASK}
        ignore = (name, org["name"], who[1] if who else "")
        for v, body in bodies.items():
            for problem in L.check_message(body, [], ignore=ignore) + L.check_first_message(body, ignore=ignore):
                issues.append(f"{name} ({v}): {problem}")
            if L.words(body) > 200:
                issues.append(f"{name} ({v}): {L.words(body)} words before the sign-off")
        variant = variant_for(reason["fit"])
        rows.append({"oid": oid, "org": name, "record": org["name"], "fit": reason["fit"], "arm": variant,
                     "contact_id": who[0]["contact_id"] if who else "", "to": who[1] if who else f"{name} team",
                     "role": who[0]["role"] if who else "", "route": route or "NO EMAIL ROUTE: find one before sending",
                     "suggest": "" if who else suggestion(contacts), "bodies": bodies,
                     "subjects": {v: SUBJECT[v].format(org=name) for v in ASK}, "words": {v: L.words(b) for v, b in bodies.items()},
                     "source": brief["source_url"], "read": brief["accessed_on"], "excerpt": " ".join((brief["excerpt"] or "").split()),
                     "also_in": reason.get("also_in", "")})
    return rows, issues


HOLD_LABELS = [(r"Raw OpenStreetMap", "raw map point, not yet matched to a real company"), (r"Possible closure", "possible closure"),
               (r"organisation or branch overlap", "possible duplicate"), (r"Role not confirmed", "role not confirmed")]


def other_companies(con, reviewed: set):
    """Every other company's chosen draft, ready-for-review drafts first."""
    sql = """SELECT p.*, o.name AS org_name FROM outreach_plans p JOIN organisations o USING(organisation_id)
             WHERE p.selection='Candidate for review' ORDER BY p.review_status, p.segment, o.name"""
    return [dict(r) for r in con.execute(sql) if r["organisation_id"] not in reviewed]


def write_file(con, rows, today: str) -> Path:
    drafted = [r for r in rows if r["fit"] != "hold"]
    reviewed = {r["oid"] for r in rows}
    others = other_companies(con, reviewed)
    held_dups = [dict(r) for r in con.execute(
        "SELECT r.entity_id, o.name AS dup, r.related_id, p.name AS primary_name FROM review r JOIN organisations o ON o.organisation_id=r.entity_id "
        "JOIN organisations p ON p.organisation_id=r.related_id WHERE r.kind LIKE 'Duplicate organisation%' OR r.kind LIKE 'Shared inbox%' ORDER BY o.name")]
    ready = [p for p in others if p["review_status"] == "Draft review"]
    held = [p for p in others if p["review_status"] != "Draft review"]
    import build_company_audience_profile as P  # the audience profile goes first, for presenting

    lines = P.profile_lines(con) + ["", "---", "", f"# Employer drafts, {today}: every company's first message", "",
             "Review copy only: nothing is sent. One first message per company, one recipient each. Four parts:", "",
             f"1. **Companies whose giving funds or supports education ({len(drafted)}).** Variant **A** (sponsorship of students, any size, including textbooks, "
             f"transport or meals) for the {sum(r['arm'] == 'A' for r in drafted)} that fund education; variant **B** (a partnership on an education benefit for the "
             f"children of staff) for the other {sum(r['arm'] == 'B' for r in drafted)}. Each draft rests on one fact the company publishes, with its page. These drafts "
             "are stored in the master (variant_subject, variant_body).",
             f"2. **All other companies, variant B, ready for review ({len(ready)}).** The partnership request (the same ask as variant B, without a giving fact): "
             f"set up a partnership to provide an education benefit for staff children, and a short meeting. No offer terms. The second touch asks who is best to speak to about staff welfare or benefits. {sum('@' not in (p['contact_channel'] or '') for p in ready)} of them have a phone number as "
             "their only route and are marked.",
             f"3. **Held, variant B ({len(held)}).** The same request, but there is no email route or another check is open, so it cannot go yet.",
             f"4. **Duplicate records held ({len(held_dups)}),** so each business gets one message.", "",
             "Follow-up and offer messages are in the master workbook's Outreach plans sheet. Welfare funders and homes, and the government letters, are separate "
             "runs with their own workbooks and are not in this file. Savings groups appear in part 2 or 3 with their own request to the committee (variant n/a).", "",
             "Fit: strong = the company funds education; moderate = it funds education-related items or community projects; weak = community giving with "
             "no education link. Count replies, positive replies and meetings agreed per variant, and report the denominators; keep automatic replies and "
             "refusals apart.", "", "---", "", "# 1. Companies with a reviewed draft", ""]
    for i, r in enumerate(drafted, 1):
        v = r["arm"]
        lines += [f"## 1.{i} {r['org']} ({r['fit']} fit): variant {v}", "",
                  f"- To: {r['to']}" + (f", {r['role']}" if r["role"] else ""), f"- Route: {r['route']}", f"- Organisation record: {r['oid']} ({r['record']})"]
        if r["suggest"]:
            lines.append(f"- Addressed to the team because no contact here is verified. Confirm this person, then address them: {r['suggest']}")
        if r["also_in"]:
            lines.append(f"- **Overlap:** {r['also_in']}")
        lines += [f"- Source: {r['source']} (read {r['read']})", f"- Excerpt: \"{r['excerpt'][:300]}\"", "",
                  f"Subject: {r['subjects'][v]} ({r['words'][v]} words)", "", "```", r["bodies"][v], "```", ""]
    not_drafted = [r for r in rows if r["fit"] == "hold"]
    if not_drafted:
        lines += ["## Not drafted", ""] + [f"- **{r['org']}** ({r['oid']}): {r['hold_reason']}" for r in not_drafted] + [""]

    def entry(n: str, p: dict) -> list[str]:
        why = [label for pattern, label in HOLD_LABELS if re.search(pattern, p["missing_information"] or "")]
        no_route = not (p["contact_channel"] or "").strip()
        if p["review_status"] != "Draft review" or no_route:
            why.insert(0, "no contact route recorded" if no_route else "needs research")
        who = p["target_name"] if p["target_type"] == "contact" else f"{p['org_name']} team"
        role = f", {p['recipient_role']}" if p["target_type"] == "contact" and p["recipient_role"] else ""
        variant = p.get("message_variant") or ""
        flag = f" | **Held: {'; '.join(dict.fromkeys(why))}**" if why and p["review_status"] != "Draft review" else ""
        if p["review_status"] == "Draft review" and p["contact_channel"] and "@" not in p["contact_channel"]:
            flag = " | **Phone route only: call or message, this is not an email address**"
        return [f"### {n} {p['org_name']} ({p['segment']}): variant {variant}", "",
                f"- To: {who}{role} | Route: {p['contact_channel'] or 'none recorded'} | Plan: {p['message_id']}{flag}",
                "", f"Subject: {p['subject']}", "", "```", p["body"], "```", ""]

    lines += ["---", "", f"# 2. All other companies, ready for review ({len(ready)})", ""]
    for i, p in enumerate(ready, 1):
        lines += entry(f"2.{i}", p)
    lines += ["---", "", f"# 3. Held until a route or check is resolved ({len(held)})", ""]
    for i, p in enumerate(held, 1):
        lines += entry(f"3.{i}", p)
    lines += ["---", "", f"# 4. Duplicate records held ({len(held_dups)})", "",
              "These records keep their IDs. Their drafts are alternatives so each business gets one message; the message goes to the record named on the right.", ""]
    lines += [f"- {d['dup']} ({d['entity_id']}) -> {d['primary_name']} ({d['related_id']})" for d in held_dups]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"Silverleaf Employer Sponsorship Drafts - {today}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    args = parser.parse_args()
    con = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows, issues = build_drafts(con)
    if issues:
        print("\n".join(issues))
        raise SystemExit("Checks failed; nothing written.")
    path = write_file(con, rows, date.today().isoformat())
    print(f"{sum(r['fit'] != 'hold' for r in rows)} reviewed drafts, {sum(r['fit'] == 'hold' for r in rows)} held: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
