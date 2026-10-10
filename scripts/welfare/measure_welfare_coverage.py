#!/usr/bin/env python3
"""Measure a welfare run's data points per stratum (segment x priority). No network calls; read-only.

Reads runtime/welfare/<run-id>/final.json (organisations and contacts as built) and the run database's outreach plans
(addressee, route, escalation contact, hook). Counts, for each stratum, the organisations that have each data point:

- leader: a named person with a leader's role is recorded (draft_run_messages.leader_rank: founder, director, manager,
  coordinator, head; board roles never, a chair only when the draft names them) with a confirmed role, whatever
  their risk label
- addressed: the draft is addressed to a named person (the recipient rule in draft_run_messages.py: the in-country leader
  first, board roles never, a chair only when no executive is named)
- direct_email: the addressee's own published address, or a role inbox on the organisation's own domain
- any_email, phone: any email or phone recorded for the organisation or its contacts (risky ones included)
- no_route: neither an email nor a phone
- address: a physical or postal address; geo_point / geo_locality: geocoded to a point, or to a locality (the rest are
  town, register district or unresolved)
- website, socials, ngo_reg: an own website, official social pages, an NGO register number
- size: children served, capacity or staff count as published; founded: founding year
- escalation: an escalation contact named in the plan
- hook: a sourced hook in the plan, or the published schooling arrangement (the education angle)

Usage: python scripts/welfare/measure_welfare_coverage.py --run-id <run-id> [--json out.json] [--markdown out.md]
       [--final <snapshot final.json> --db <snapshot database>]   (a before/after comparison)
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict

import welfare_lib as W

sys.path.insert(0, str(W.ROOT / "scripts" / "messaging"))
from draft_run_messages import board_role, leader_rank  # noqa: E402  (the drafting rule, read-only)

SEGMENTS = [("Welfare residential care", "Homes"), ("Welfare family-based programme", "Programmes"),
            ("Welfare specialised centre", "Specialised centres"), ("Welfare funder", "Funders"),
            ("Welfare network (introducer)", "Networks")]
PRIORITIES = ["High", "Medium", "Low"]
BAND = {"P1": "High", "P2": "Medium", "P3": "Low", "P4": "Low"}
POINTS = [("leader", "Leader recorded"), ("addressed", "Addressed by name"), ("direct_email", "Direct email"), ("any_email", "Any email"), ("phone", "Phone"),
          ("no_route", "No route"), ("address", "Address"), ("geo_point", "Geocode: point"), ("geo_locality", "Geocode: locality"),
          ("website", "Website"), ("socials", "Socials"), ("ngo_reg", "NGO reg. no."), ("size", "Size"), ("founded", "Founded"),
          ("escalation", "Escalation"), ("hook", "Hook / education angle")]


def emails_of(org: dict, contacts: list[dict]) -> list[str]:
    out = list(org.get("public_emails") or [])
    for c in contacts:
        out += c.get("emails") or []
    return [e for e in out if e and "@" in e]


def phones_of(org: dict, contacts: list[dict]) -> list[str]:
    out = list(org.get("public_phones") or [])
    for c in contacts:
        out += c.get("phones") or []
    return [p for p in out if p and re.search(r"\d{6}", re.sub(r"\D", "", p))]


def measure(run_id: str, final_path=None, db_path=None) -> dict:
    cfg = W.load_config(run_id)
    final = json.loads(open(final_path or cfg["paths"]["work"] / "final.json", encoding="utf-8").read())
    by_org = defaultdict(list)
    for c in final["contacts"]:
        by_org[c.get("organisation_key")].append(c)
    db = W.Path(db_path) if db_path else W.ROOT / "outputs" / "runs" / run_id / "lead-database.sqlite"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    plan_by_key = {}
    for r in con.execute("SELECT o.name, o.website, o.priority, p.* FROM outreach_plans p JOIN organisations o ON o.organisation_id = p.organisation_id "
                         "WHERE p.target_type = 'organisation'"):
        plan_by_key[(W.name_key(r["name"]), r["website"] or "")] = dict(r)
    names = {r["organisation_id"]: r["name"] for r in con.execute("SELECT organisation_id, name FROM organisations")}
    con.close()

    rows, flags = {}, {}
    for org in final["organisations"]:
        seg = org.get("segment")
        label = dict(SEGMENTS).get(seg)
        if not label:
            continue
        prio = BAND.get(org.get("priority_band"), "Low")
        website = org.get("website") or ""
        site = website if str(website).startswith("http") else ("https://" + website if website else "")
        plan = plan_by_key.get((W.name_key(org["organisation_name"]), site)) or plan_by_key.get((W.name_key(org["organisation_name"]), website)) or {}
        contacts = by_org.get(org.get("record_key"), [])
        emails, phones = emails_of(org, contacts), phones_of(org, contacts)
        dom = W.own_domain(website)
        recipient = plan.get("recipient") or ""
        addressed = bool(recipient) and "(organisation route)" not in recipient and not recipient.lower().startswith(("the team", "team"))
        leader = addressed or any(len(W.norm_text(c.get("contact_name")).split()) >= 2 and leader_rank(c.get("role") or "") is not None
                                  and not board_role(c.get("role") or "") and c.get("role_certainty") in ("confirmed", "", None)
                                  for c in contacts)
        route_type, route_value = plan.get("contact_route") or "", plan.get("route_value") or ""
        direct = route_type in ("named_email", "published_role_email") or (
            "@" in route_value and dom and route_value.lower().split("@")[-1].endswith(dom) and not W.PERSONAL_EMAIL.search(route_value))
        if not direct and dom:
            direct = any(e.lower().split("@")[-1].endswith(dom) and not W.PERSONAL_EMAIL.search(e) for e in org.get("public_emails") or [])
        point = {
            "leader": leader, "addressed": addressed, "direct_email": bool(direct), "any_email": bool(emails), "phone": bool(phones),
            "no_route": not emails and not phones, "address": bool(W.norm_text(org.get("address"))),
            "geo_point": org.get("geocode_precision") == "point",
            "geo_locality": org.get("geocode_precision") == "locality",
            "website": bool(website), "socials": bool(org.get("social_media")), "ngo_reg": bool(org.get("nis_reg_no")),
            "size": bool(org.get("children_served_published") or org.get("children_served_evidence") or org.get("staff_count_published")),
            "founded": bool(re.search(r"\b(18|19|20)\d\d\b", str(org.get("founded") or ""))),
            "escalation": bool(plan.get("escalation_recipient")),
            "hook": bool(plan.get("hook") or W.norm_text(org.get("schooling_arrangement_published"))),
        }
        rows.setdefault((label, prio), []).append(point)
        flags[org["record_key"]] = {"name": org["organisation_name"], "segment": label, "priority": prio, **point}
    table = []
    for _, label in SEGMENTS:
        for prio in PRIORITIES:
            pts = rows.get((label, prio), [])
            table.append({"segment": label, "priority": prio, "n": len(pts), **{k: sum(p[k] for p in pts) for k, _ in POINTS}})
    total = {"segment": "All", "priority": "", "n": sum(t["n"] for t in table), **{k: sum(t[k] for t in table) for k, _ in POINTS}}
    return {"run_id": run_id, "table": table, "total": total, "organisations": flags}


def markdown(result: dict) -> str:
    head = "| Segment | Priority | n | " + " | ".join(lbl for _, lbl in POINTS) + " |"
    lines = [head, "|" + "---|" * (3 + len(POINTS))]
    for t in result["table"] + [result["total"]]:
        if not t["n"]:
            continue
        lines.append(f"| {t['segment']} | {t['priority']} | {t['n']} | " + " | ".join(str(t[k]) for k, _ in POINTS) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--final", help="measure another snapshot: a final.json (default: the run's runtime copy)")
    parser.add_argument("--db", help="measure another snapshot: a run database (default: the run's)")
    parser.add_argument("--json", help="write the full result (table and per-organisation flags) here")
    parser.add_argument("--markdown", help="write the table here")
    args = parser.parse_args()
    result = measure(args.run_id, args.final, args.db)
    md = markdown(result)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=1)
    if args.markdown:
        with open(args.markdown, "w", encoding="utf-8") as handle:
            handle.write(md + "\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
