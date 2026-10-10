#!/usr/bin/env python3
"""Measure the company master's data points per reach stratum: how many organisations hold each kind of contact and lead fact.

Read-only. Strata: the reach tiers in employer_reach (P1, P2, P3; X, held, is left out) and the introducers (segment
'Introducer: ...') as their own stratum. For an enrichment round, measure before and after with the same strata: the baseline
run writes each organisation's stratum into its JSON, and --strata-from <baseline.json> reuses it, so a re-rank in between
does not move organisations between strata.

Data points per organisation (one count each, across the organisation's record, its contacts and its merged research):
- decision-maker: a named, verified contact (resolve_master_recipients.verified_person) in a senior or fallback role
  (senior_rank), not another country's head and not a former role;
- direct email: such a decision-maker reached at their own address, or at the inbox for their role (hr@ for the HR head, md@,
  ceo@ ...), as export_resend_contacts.high_route decides 'direct';
- any email: any address on the organisation or its contacts (free mail included);
- phone: any phone on the organisation or its contacts;
- address: any postal or physical address (organisations.address, postal_address facts, or a physical address in a merged
  contact profile); 'physical address' counts one that is more than a P.O. Box;
- geocode address-level: geocode_precision 'point' (an address or building); 'locality-level' counts city, town or locality;
- website: an own website (not a social or listing site);
- social pages: an official social page fact ('social (...)');
- size evidence: headcount or size_evidence, or a workforce fact in the lead brief;
- founded: organisations.founded, a founded/established fact, or a lead-brief fact that dates the organisation's start;
- escalation: the chosen plan names an escalation contact, out of the organisations whose people show a wider group
  (resolve_master_recipients.wide_organisations);
- lead brief: at least one lead_briefs fact with a source; verified hook: a chosen plan whose hook_status is 'Verified ...'.

Usage:
  python scripts/master/measure_master_coverage.py --label before [--json runtime/master/coverage-before.json]
  python scripts/master/measure_master_coverage.py --label after --strata-from runtime/master/coverage-before.json
Prints a Markdown table (counts and percentages per stratum) and writes the JSON (default runtime/master/coverage-<label>.json).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "master"))
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
import resolve_master_recipients as R  # noqa: E402
from export_resend_contacts import any_emails, high_route  # noqa: E402  (the direct-route rule the segments use)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
STRATA = ("P1", "P2", "P3", "Introducers")
POINTS = [("decision_maker", "Named decision-maker"), ("direct_email", "Direct email (own or role inbox)"), ("any_email", "Any email"),
          ("phone", "Phone"), ("address", "Address (postal or physical)"), ("physical_address", "Physical address (beyond a P.O. Box)"),
          ("geocode_point", "Geocode address-level"), ("geocode_locality", "Geocode locality-level"), ("website", "Website"),
          ("social", "Official social pages"), ("size", "Size evidence"), ("founded", "Founded year"),
          ("escalation", "Escalation contact (of wide orgs)"), ("wide", "Wide (group) organisations"), ("brief", "Lead brief with source"),
          ("hook", "Verified hook")]
PHONE = re.compile(r"\+?\d[\d ()-]{7,}\d")
# A lead-brief fact that dates the organisation's start ('was established in 1963', 'founded in 1999', 'since 1935').
FOUNDED_FACT = re.compile(r"\b(founded|established|since|opened|began|started|incorporated|came into being|date[sd]? back to|traces? (its|their) "
                          r"(origin|roots|beginning)[^.]{0,40}|formed)\b[^.]{0,40}\b(1[89]\d\d|20[0-2]\d)\b", re.I)


PLACE_ONLY = re.compile(r"\b(arusha|moshi|tanzania|kilimanjaro|manyara|city|town|region|municipality|united republic of|east africa|"
                        r"usa[- ]?river|tengeru|karatu|mto wa mbu|p\.?\s?o\.?\s*box|box|s\.?\s?l\.?\s?p\.?)\b", re.I)


def physical(value: str) -> bool:
    """More than a P.O. Box and a town: a street, area, building or plot remains once those are taken out."""
    value = re.sub(r"\(.*?\)", " ", str(value or ""))
    rest = PLACE_ONLY.sub(" ", re.sub(r"(?i)p\.?\s?o\.?\s*box\s*\d+", " ", value))
    return bool(re.search(r"[A-Za-z]{3,}", rest))


def measure(con, strata_from: dict | None = None) -> dict:
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in con.execute("SELECT * FROM contacts")}
    if strata_from is not None:
        stratum = {oid: s for oid, s in strata_from.items() if oid in orgs}
    else:
        stratum = {r["organisation_id"]: r["tier"] for r in con.execute("SELECT organisation_id, tier FROM employer_reach") if r["tier"] in STRATA}
        for oid, org in orgs.items():
            if str(org["segment"] or "").startswith("Introducer"):
                stratum[oid] = "Introducers"
    by_org = defaultdict(list)
    for c in contacts.values():
        by_org[c["organisation_id"]].append(c)
    wide = R.wide_organisations(contacts)
    facts = defaultdict(set)
    for oid, field in con.execute("SELECT entity_id, field FROM facts WHERE entity_type='organisation' AND (field LIKE 'social (%' "
                                  "OR field IN ('postal_address','founded','established','Established'))"):
        facts[oid].add("social" if field.startswith("social") else "founded" if field.lower() in ("founded", "established") else field)
    postal = defaultdict(list)
    for oid, value in con.execute("SELECT entity_id, value FROM facts WHERE entity_type='organisation' AND field='postal_address'"):
        postal[oid].append(value)
    physical_found = defaultdict(list)
    for location, payload in con.execute("SELECT location, payload_json FROM source_records WHERE location LIKE 'contact profile %'"):
        try:
            data = json.loads(payload)
        except ValueError:
            continue
        for value in data.get("physical") or []:
            physical_found[location.split()[2]].append(value)
    briefs = defaultdict(set)
    for oid, kind, fact in con.execute("SELECT organisation_id, fact_type, fact FROM lead_briefs WHERE COALESCE(source_url,'')<>''"):
        briefs[oid].add(kind)
        if FOUNDED_FACT.search(fact or ""):
            briefs[oid].add("founded")
    chosen = defaultdict(list)
    for p in con.execute("SELECT organisation_id, hook_status, escalation_contact_id, selection FROM outreach_plans"):
        if p["selection"] == "Candidate for review":
            chosen[p["organisation_id"]].append(dict(p))

    per_org = {}
    for oid, s in stratum.items():
        org = orgs[oid]
        segment = "Introducers" if s == "Introducers" else ""
        people = by_org.get(oid, [])
        dms = [c for c in people if R.verified_person(c) and R.senior_rank(c, segment) is not None
               and R.location(c, oid in wide) != 2 and not R.STALE.search(c["role"] or "")]
        org_mails = any_emails(org["email"], *[c["shared_email"] for c in people])
        direct = False
        for c in dms:
            own = any_emails(c["named_email"], c["published_role_email"])
            for address in own + [a for a in org_mails if R.domain(org["website"]) and a.endswith(R.domain(org["website"]))]:
                if not R.FREE_MAIL.search(address) and high_route(address, c["name"], c["role"])[0] == "direct":
                    direct = True
        mails = set(org_mails) | set(any_emails(*[c["named_email"] for c in people], *[c["published_role_email"] for c in people]))
        phone = bool(PHONE.search(str(org["phone"] or ""))) or any(PHONE.search(str(c["role_phone"] or "") + " " + str(c["organisation_phone"] or ""))
                                                                     for c in people)
        addresses = [org["address"]] + postal.get(oid, []) + physical_found.get(oid, [])
        precision = str(org["geocode_precision"] or "").lower()
        plans = chosen.get(oid, [])
        per_org[oid] = {
            "stratum": s,
            "decision_maker": bool(dms),
            "direct_email": direct,
            "any_email": bool(mails),
            "phone": phone,
            "address": any(str(a or "").strip() for a in addresses),
            "physical_address": any(physical(a) for a in addresses),
            "geocode_point": precision == "point",
            "geocode_locality": precision in ("city", "town", "locality"),
            "website": bool(R.domain(org["website"])),
            "social": "social" in facts.get(oid, set()),
            "size": bool(org["headcount"] or str(org["size_evidence"] or "").strip()) or "workforce" in briefs.get(oid, set()),
            "founded": bool(str(org["founded"] or "").strip()) or "founded" in facts.get(oid, set()) or "founded" in briefs.get(oid, set()),
            "wide": oid in wide,
            "escalation": any(p["escalation_contact_id"] for p in plans),
            "brief": bool(briefs.get(oid)),
            "hook": any(str(p["hook_status"] or "").startswith("Verified") for p in plans),
        }
    totals = {s: {"organisations": 0, **{k: 0 for k, _ in POINTS}} for s in STRATA}
    for row in per_org.values():
        t = totals[row["stratum"]]
        t["organisations"] += 1
        for k, _ in POINTS:
            t[k] += int(row[k])
    return {"totals": totals, "organisations": per_org}


def table(result: dict, label: str) -> str:
    totals = result["totals"]
    head = "| Data point | " + " | ".join(f"{s} (n={totals[s]['organisations']})" for s in STRATA) + " |"
    lines = [f"### Coverage: {label}", "", head, "|---|" + "---|" * len(STRATA)]
    for key, name in POINTS:
        cells = []
        for s in STRATA:
            n = totals[s]["organisations"]
            base = totals[s]["wide"] if key == "escalation" else n
            v = totals[s][key]
            cells.append(f"{v} ({round(100 * v / base) if base else 0}%)")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default=str(MASTER))
    parser.add_argument("--label", default="now")
    parser.add_argument("--json", help="where to write the result (default runtime/master/coverage-<label>.json)")
    parser.add_argument("--strata-from", help="a baseline JSON whose organisations' strata are reused")
    args = parser.parse_args()
    strata = None
    if args.strata_from:
        strata = {oid: row["stratum"] for oid, row in json.loads(Path(args.strata_from).read_text(encoding="utf-8"))["organisations"].items()}
    con = sqlite3.connect(f"file:{Path(args.database).resolve().as_posix()}?mode=ro", uri=True)
    result = measure(con, strata)
    con.close()
    out = Path(args.json) if args.json else ROOT / "runtime" / "master" / f"coverage-{args.label}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"label": args.label, **result}, indent=1, ensure_ascii=False), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(table(result, args.label))
    print(f"\nWrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
