#!/usr/bin/env python3
"""Profile the audience of the company drafts, from the master's organisations, contacts and chosen recipients.

Read-only. Gives the numbers behind who Silverleaf is writing to (kinds of company, where they are, who in each company receives the
message, how reachable they are, what they publish about giving) and a short persona for each kind of company, written as working
hypotheses to test, not findings. Writes outputs/messages/Silverleaf Company Audience Profile - <date>.md, and
draft_employer_sponsorship.py puts the same text at the top of the employer drafts file.
Nothing here describes a person beyond the role the organisation publishes: no parenthood, household or personal status is inferred.
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402  (role ranking and verification)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
HOOK_TYPES = {"workforce", "staff_welfare", "education_programme", "community_programme", "locality", "growth"}
HOSPITALITY = re.compile(r"hotel|lodge|guest|camp|resort|villa", re.I)
BANDS = [("0-5 km", "0-5 km"), ("6-10 km", "6-10 km"), ("11-15 km", "11-25 km"), ("16-20 km", "11-25 km"), ("21-25 km", "11-25 km")]


def pct(n: int, d: int) -> str:
    return f"{n} ({round(100 * n / d)}%)" if d else f"{n}"


def share(n: int, d: int) -> str:
    return f"{round(100 * n / d)}%" if d else ""


def table(headers: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    return out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows] + [""]


def kind_of(plan: dict, org: dict) -> str:
    seg = plan["segment"]
    if seg == "Tourism employers":
        return "Hotels, lodges and camps" if HOSPITALITY.search(f"{org['name']} {org['segment'] or ''}") else "Safari operators and travel agencies"
    return {"Corporate employers": "Banks and other companies", "Healthcare employers": "Hospitals and clinics",
            "Education employers": "Colleges and universities", "NGO employers": "NGOs and research bodies",
            "Public-sector employers": "Public bodies"}.get(seg, seg)


def recipient_kind(plan: dict, contacts: dict) -> str:
    if plan["target_type"] != "contact":
        return "Company team (no named person)"
    contact = contacts.get(plan["target_id"], {})
    rank = R.role_rank(contact.get("role") or plan.get("recipient_role"))
    verified = bool(R.VERIFIED.search(contact.get("verification") or "")) and not R.UNUSABLE.search(contact.get("verification") or "")
    label = {0: "HR / people", 1: "Owner, founder, MD or CEO", 2: "General manager or director", 3: "Other senior director"}.get(rank, "Other named manager")
    return f"{label}{'' if verified else ' (role not yet confirmed)'}"


def route_kind(plan: dict) -> str:
    channel = plan.get("contact_channel") or ""
    if "@" in channel:
        return "email"
    return "phone only" if re.search(r"\d{6}", channel) else "no route yet"


def profile_lines(con: sqlite3.Connection) -> list[str]:
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    plans = [dict(r) for r in con.execute("SELECT * FROM outreach_plans WHERE selection='Candidate for review'")]
    companies = [p for p in plans if p["segment"] != "SACCOS members"]
    groups = [p for p in plans if p["segment"] == "SACCOS members"]
    total_orgs = len(orgs)
    held_dups = con.execute("SELECT COUNT(DISTINCT entity_id) FROM review WHERE kind LIKE 'Duplicate organisation%' OR kind LIKE 'Shared inbox%'").fetchone()[0]
    ready = [p for p in companies if p["review_status"] == "Draft review"]
    kinds = Counter(kind_of(p, orgs[p["organisation_id"]]) for p in companies)
    kinds_ready = Counter(kind_of(p, orgs[p["organisation_id"]]) for p in ready)
    N = len(companies)
    all_contacts = list(contacts.values())
    roles = Counter()
    for c in all_contacts:
        r = (c["role"] or "").lower()
        roles["Founder, owner or co-founder" if re.search(r"founder|owner", r) else "Managing director, CEO or chairman" if re.search(r"managing director|\bceo\b|chief exec|chairm", r)
              else "General manager or director" if re.search(r"general manager|director", r) else "HR or people" if re.search(r"human resource|\bhr\b|people|talent", r)
              else "Operations, reservations, sales or marketing" if re.search(r"operation|reservation|sales|marketing|booking|trip|logistic", r) else "Other roles"] += 1

    lines = ["# Who we are writing to: the company audience", "",
             f"*As of {date.today().isoformat()}, from the master database. Every number below is counted from the database; the personas are working hypotheses to test, not findings.*", "",
             "## In one minute", "",
             f"- We start from **{total_orgs} organisations** near the campuses. After merging {held_dups} duplicate records we write to **{N + len(groups)} separate businesses**: "
             f"{N} companies and {len(groups)} savings groups.",
             f"- **{pct(len(ready), N)} of the companies are ready for review now** (a draft and a usable route). The rest are held, mostly for want of a published route.",
             f"- The audience is **overwhelmingly tourism**: {pct(kinds['Safari operators and travel agencies'] + kinds['Hotels, lodges and camps'], N)} are safari operators, travel agencies, hotels or lodges. "
             "The rest are banks and other companies, hospitals, colleges and NGOs.",
             f"- **Founders and owners are the largest named role group in our contact list** ({roles['Founder, owner or co-founder']} of {len(contacts)} people), and HR contacts are rare "
             f"({roles['HR or people']}). So the person who decides is usually the founder, managing director or general manager, not an HR department.",
             "- We ask **one of two things** of a company. A strong fit (it already funds education) is asked to sponsor students. Every other company is asked to set up a partnership "
             "on an education benefit for its staff's children. Neither first message states an offer.", ""]

    lines += ["## Kinds of company", ""]
    rows = [[k, kinds[k], share(kinds[k], N), kinds_ready[k]] for k, _ in kinds.most_common()]
    lines += table(["Kind of company", "Businesses", "Share", "Ready for review"], rows)

    lines += ["## Where they are", ""]
    near = Counter()
    for p in companies:
        o = orgs[p["organisation_id"]]
        near[o["transport_band"] if o["transport_band"] in ("0-5 km", "6-10 km") else ("11-25 km" if o["transport_band"] in ("11-15 km", "16-20 km", "21-25 km") else
                                                                                                   ("More than 25 km" if o["transport_band"] == ">40 km" else "Location not recorded"))] += 1
    campus = Counter(L.campus_key(orgs[p["organisation_id"]]["campus"]) or "Not recorded" for p in companies)
    lines += table(["Distance to the nearest campus", "Businesses"], [[k, near[k]] for k in ("0-5 km", "6-10 km", "11-25 km", "More than 25 km", "Location not recorded")])
    lines += table(["Nearest campus", "Businesses"], [[k.replace("Boma Ngombe", "Boma Ng'ombe"), v] for k, v in campus.most_common()])
    tiers = Counter(orgs[p["organisation_id"]]["desk_tier"] or "unscored" for p in companies)
    lines += [f"Desk-research tiers (A is the strongest fit): " + ", ".join(f"{k} {v}" for k, v in sorted(tiers.items())) + ".", ""]

    lines += ["## Size", "",
              f"Staff numbers are published for only {sum(1 for p in companies if orgs[p['organisation_id']]['headcount'])} of {N} companies, so we do not size the audience by headcount. "
              "Where a site does say, the range is wide: a hospital with 650 staff, a university with 150, safari operators with 11 to 100.", ""]

    lines += ["## Who receives the message", ""]
    rk = Counter(recipient_kind(p, contacts) for p in companies)
    lines += table(["Recipient", "Businesses", "Share"], [[k, v, share(v, N)] for k, v in sorted(rk.items(), key=lambda kv: (kv[0].startswith("Company"), -kv[1]))])
    rt = Counter(route_kind(p) for p in companies)
    lines += table(["Route", "Businesses", "Share"], [[k, rt[k], share(rt[k], N)] for k in ("email", "phone only", "no route yet")])
    senior = [c for c in all_contacts if R.role_rank(c["role"]) is not None]
    verified_senior = [c for c in senior if R.VERIFIED.search(c["verification"] or "") and not R.UNUSABLE.search(c["verification"] or "")]
    direct = [c for c in all_contacts if c["named_email"] or c["published_role_email"]]
    lines += [f"Our contact list holds **{len(all_contacts)} people**. {len(senior)} hold a senior role (HR, owner, founder, MD, CEO, general manager or director), "
              f"{len(verified_senior)} of them with a role we have confirmed on a published page. {len(direct)} have a published email of their own or for their role; "
              "most are reachable only through the company's shared inbox, and we do not guess personal addresses.", ""]
    lines += table(["Role on file", "People"], [[k, v] for k, v in roles.most_common()])

    hooks = Counter()
    hooked = set()
    for r in con.execute("SELECT organisation_id, hook_type FROM outreach_plans WHERE hook_status LIKE 'Verified%' AND COALESCE(hook,'')<>''"):
        if r["organisation_id"] not in hooked:
            hooked.add(r["organisation_id"])
            hooks[r["hook_type"] if r["hook_type"] in HOOK_TYPES else "other"] += 1
    lines += ["## What they publish that gives us a reason to write", "",
              f"{len(hooked)} businesses publish a fact we have verified and quoted (the page and the exact words are on file): " + ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in hooks.most_common()) + ". "
              "The rest get the plain partnership request, which is honest and needs no hook.", ""]
    variants = Counter(p.get("message_variant") for p in plans)
    lines += [f"Of these, **{variants.get('A', 0)} companies already fund education** and are asked for sponsorship (variant A); the other "
              f"{variants.get('B', 0)} companies are asked for a staff-benefit partnership (variant B); {len(groups)} savings groups are asked for a meeting with their committee.", ""]

    lines += ["## Personas (working hypotheses)", "",
              "Use these to talk about the audience, and to decide what to test. None of this claims that any staff member is a parent.", ""]
    persona = [
        ("Owner-led safari operator or travel agency", kinds["Safari operators and travel agencies"],
         "A founder or managing director who runs a team of office staff, guides and drivers, much of it seasonal and based locally.",
         "A benefit that helps them keep a settled local team, at no cost to the company; for those that already fund education, a chance to extend what they do.",
         "Founder, owner, MD or GM. Often the only decision-maker; no HR department."),
        ("Hotel, lodge or camp", kinds["Hotels, lodges and camps"],
         "Larger resident teams in hospitality and operations, with a general manager and sometimes an HR officer.",
         "Staff welfare and retention; a benefit that reaches many staff through one arrangement.",
         "General manager first; HR or the owner if one is published."),
        ("Bank or other company", kinds["Banks and other companies"],
         "Offices with an HR function and a corporate-benefits process.",
         "A structured, low-effort benefit the HR team can offer; clarity on process.",
         "HR head or the managing director; regional offices often defer to head office."),
        ("Hospital or clinic", kinds["Hospitals and clinics"],
         "Large, shift-working teams on site, and a hospital director or administrator.",
         "Staff welfare for people who work long and irregular hours.",
         "Hospital director, administrator or HR."),
        ("College or university", kinds["Colleges and universities"],
         "Academic and administrative staff, with a registrar, principal or vice-chancellor.",
         "A staff benefit, kept clearly separate from student admissions.",
         "HR or the administration; the principal or vice-chancellor for sign-off."),
        ("NGO or research body", kinds["NGOs and research bodies"],
         "Programme teams, often partly funded by donors, with a country or executive director.",
         "A modest staff benefit and a link to local education work.",
         "Country director or executive director."),
        ("Public body", kinds["Public bodies"],
         "Government agencies and parastatals, as employers.",
         "An employee benefit offered through the HR route only, after a compliance check; never combined with a request for official action.",
         "The HR route; held until the compliance check."),
        ("Savings group (SACCOS)", len(groups),
         "A member-owned group governed by a committee. Members, not employees.",
         "Information on schools for members' children, delivered through the committee; handled in a separate Kiswahili request.",
         "The committee; no individual published."),
    ]
    for name, n, who, wants, door in persona:
        lines += [f"### {name} ({n})", "", f"- **Who they are:** {who}", f"- **What may matter to them:** {wants}", f"- **Who to write to:** {door}", ""]

    lines += ["## Limits to state when presenting", "",
              "- Most companies publish only a shared inbox; a named person with a direct email is rare, and we do not infer one.",
              "- The persona descriptions are hypotheses drawn from the kind of business and the roles on file. The first replies will tell us which ones hold.",
              "- Reply counts will be small, so report them per variant with their denominators and read them as a direction.", ""]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--database", type=Path, default=MASTER)
    args = parser.parse_args()
    con = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    path = ROOT / "outputs" / "messages" / f"Silverleaf Company Audience Profile - {date.today().isoformat()}.md"
    path.write_text("\n".join(profile_lines(con)) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
