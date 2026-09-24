#!/usr/bin/env python3
"""Export contact research to the welfare and government runs, so their pipelines absorb it. No network calls.

Reads runtime/contacts/profiles.json (build_contact_profiles.py).
- Welfare: data/raw/welfare-research/research_W_contact_profiles_<date>.jsonl in the welfare research format
  (skills/silverleaf-welfare-leads/references/research-brief.md §8). Organisation records carry the organisation's own
  published routes under its exact run name and segment, so consolidate_research.py merges them. Contact records
  carry the named people the organisation publishes. Also writes a coverage log and adds the file to the run's
  research_files.
- Government: data/raw/government-research/office_contacts_<date>.json with published council, regional and
  district office routes (postal address, phone, email) and their sources, read by build_government_run.py.
Re-run the welfare and government pipelines afterwards.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict

import contact_lib as C

W = C.W


def sources_for(profile, facts) -> list[dict]:
    out = []
    for s in profile["sources"][:12]:
        out.append({"url": s["url"], "title": s.get("title", ""), "source_date": "", "accessed_on": s.get("accessed_on", ""),
                    "evidence_basis": "published", "fetched": bool(s.get("fetched")), "facts_supported": facts,
                    "evidence_excerpt": s.get("excerpt", "")[:160] or f"Contact details published by the organisation ({s.get('method')})."})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--welfare-run", default="arusha-welfare-2026-09")
    args = parser.parse_args()
    data = json.loads((C.WORK / "profiles.json").read_text(encoding="utf-8"))
    run_date = data["date"]
    welfare = [p for p in data["profiles"] if p["db"] == "welfare" and (p["emails"] or p["phones"] or p["websites"] or p["people"] or p["postal"])]
    # consolidate_research.py treats slice W as supplementary: these records fill blanks and never replace the research.
    # A website that any other run organisation record already uses (a funder and the home it supports often share one)
    # would merge or flag the two there, so it is left out.
    with open(C.ROOT / "data" / "runs" / args.welfare_run / "intake.csv", encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle) if r["record_type"] == "organisation"]
    domain_owners = defaultdict(set)
    for r in rows:
        if W.own_domain(r["website"]):
            domain_owners[W.own_domain(r["website"])].add((W.norm_text(r["organisation_name"]).lower(), r["segment"]))
    # Several of these records can claim the same new website (a funder's site covering its partners): only the one whose
    # name the domain carries most keeps it, and none does on a tie, so no two run organisations merge on it.
    identity = lambda p: (W.norm_text(p["name"]).lower(), p["segment"])  # noqa: E731
    candidate = {identity(p): next((w for w in p["websites"] if w.startswith("http")), "") for p in welfare}
    claims = defaultdict(set)
    for key, site in candidate.items():
        if W.own_domain(site):
            claims[W.own_domain(site)].add(key)

    def keeps_website(key, site) -> bool:
        dom = W.own_domain(site)
        if not dom or domain_owners.get(dom, set()) - {key}:
            return False
        scores = {k: C.name_domain_score(k[0], dom) for k in claims[dom]}
        best = max(scores.values())
        return scores[key] == best and list(scores.values()).count(best) == 1

    records, counts = [], {"organisations": 0, "contacts": 0}
    for p in welfare:
        website = candidate[identity(p)]
        if website and not keeps_website(identity(p), website):
            website = ""
        org_emails = [e["email"] for e in p["emails"] if e["type"] in ("role", "general", "personal_domain")]
        personal = [e for e in org_emails if W.PERSONAL_EMAIL.search(e)]
        socials = {k if k in ("facebook", "instagram", "youtube", "linkedin") else ("x" if k == "twitter" else "other"): v for k, v in p["socials"].items()}
        risk, reason = (("medium", "The organisation publishes an inbox on a personal email domain; confirm it is the official address.") if personal
                        else ("low", "Organisation-level routes published by the organisation."))
        flag_kinds = C.crawl_flag_kinds(p.get("crawl_flags"))
        if "robots.txt disallows" in flag_kinds:
            risk, reason = "risky", C.ROBOTS_BROWSER_RISK
        record = {"record_type": "organisation", "slice": "W", "organisation_name": p["name"], "segment": p["segment"],
                  "website": website, "public_emails": org_emails,
                  "public_phones": [x["phone"] for x in p["phones"]], "social_media": socials,
                  "address": p["postal"][0] if p["postal"] else "",
                  "sources": sources_for(p, ["website", "email", "phone"]),
                  "verification_status": "verified" if any(s.get("fetched") for s in p["sources"]) else "unverified",
                  "pdpa_risk": risk, "pdpa_risk_reason": reason,
                  # Warning kinds only: the full notes are in the contact-profiles workbook's Flags sheet (free text could trip the
                  # run's child-identifier guard with phrases such as "now called ...").
                  "notes": " ".join([f"Contact research {run_date}: {', '.join(p['methods'])}.",
                                     *(f"Check before outreach ({kind}; see the contact-profiles workbook, Flags)."
                                       for kind in dict.fromkeys(k for k, _ in C.note_flags(p.get("notes")))),
                                     *(["Website crawled although its robots.txt could not be read (flagged; see the contact-profiles workbook, "
                                        "Flags)."] if "robots.txt unreachable" in flag_kinds else []),
                                     *(["Website read with a browser although its robots.txt disallows crawling (the user's decision; tagged "
                                        "risky; see the contact-profiles workbook, Flags)."] if "robots.txt disallows" in flag_kinds else [])])}
        records.append(record)
        counts["organisations"] += 1
        for person in p["people"]:
            if person["already_in_database"] or person.get("identity") == "uncertain":
                continue
            email = person["email"]
            etype = "personal_domain" if email and W.PERSONAL_EMAIL.search(email) else ("named" if email else "")
            records.append({"record_type": "contact", "slice": "W", "organisation_name": p["name"], "contact_name": person["name"], "role": person["role"],
                            "role_certainty": "confirmed", "emails": [email] if email else [], "email_type": etype,
                            "phones": [person["phone"]] if person["phone"] else [], "phone_type": "mobile" if person["phone"] else "unknown",
                            "profile_url": person["source_url"],
                            "channel_attribution": f"Published by the organisation ({person['method']}) at {person['source_url']}",
                            "sources": [{"url": person["source_url"], "title": "", "source_date": "", "accessed_on": person.get("accessed_on") or run_date,
                                         "evidence_basis": "published",
                                         "fetched": bool(person.get("fetched")), "facts_supported": ["name", "role"] + (["email"] if email else []),
                                         "evidence_excerpt": (person.get("excerpt") or f"{person['name']}, {person['role']}")[:160]}],
                            "verification_status": "verified" if person.get("fetched") else "unverified", "pdpa_risk": person["pdpa_risk"],
                            "pdpa_risk_reason": person["pdpa_risk_reason"],
                            "notes": "; ".join(n for n in ("Decision-maker" if person["decision_maker"] else "",
                                                           f"Name {person['name_status']}: kept and labelled; find the full name"
                                                           if person.get("name_status", "complete") != "complete" else "") if n)})
            counts["contacts"] += 1
    raw = C.ROOT / "data" / "raw" / "welfare-research"
    out = raw / f"research_W_contact_profiles_{run_date}.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    summary = json.loads((C.WORK / "profiles-summary.json").read_text(encoding="utf-8"))
    (raw / "coverage" / "W_contact_profiles_coverage.md").write_text(
        f"# Slice W: contact profiles ({run_date})\n\n"
        f"- Own websites crawled: {summary['sites_crawled']} across all databases ({summary['sites']}); explicit robots.txt Disallow rules "
        f"honoured, one request at a time per site, 1.5 s apart. A site whose robots.txt could not be read (server, network or certificate "
        f"error) was crawled anyway and flagged.\n"
        f"- Pages read with a browser (browser_*_{run_date}.jsonl): sites built by script, and, by the user's decision, sites whose robots.txt "
        f"disallows crawling; everything from the latter is tagged risky and flagged.\n"
        f"- Welfare organisations for which the research found a published email or phone: "
        f"{sum(1 for p in data['profiles'] if p['db'] == 'welfare' and (p['emails'] or p['phones']))} of {summary['welfare']['organisations']}; "
        f"with named people found: {sum(1 for p in data['profiles'] if p['db'] == 'welfare' and p['people'])}; named people recorded: "
        f"{sum(len(p['people']) for p in data['profiles'] if p['db'] == 'welfare')} (every lead kept, most senior first; a name given only in part is labelled incomplete).\n"
        f"- Before-and-after counts for the run are in the contact-profiles workbook (outputs/contacts/).\n"
        f"- Budgeted searches: every welfare slice in data/raw/contact-research/coverage/ (homes and programmes, specialised centres "
        f"and funders, in each wave).\n"
        f"- Not reached: register-only NGOs without a website or search result; they still have no published route.\n", encoding="utf-8")
    cfg_path = C.ROOT / "data" / "runs" / args.welfare_run / "run-config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    pattern = f"data/raw/welfare-research/research_W_*_{run_date}.jsonl"
    if pattern not in cfg["research_files"]:
        cfg["research_files"].append(pattern)
        cfg_path.write_text(json.dumps(cfg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    government = [p for p in data["profiles"] if p["db"] == "government" and (p["emails"] or p["phones"] or p["postal"])]
    # Keyed by office name: build_government_run.py matches its office records by name.
    offices = {p["name"]: {"emails": p["emails"], "phones": p["phones"], "postal": p["postal"], "physical": p["physical"],
                           "sources": p["sources"], "methods": p["methods"]} for p in government}
    gov_out = C.ROOT / "data" / "raw" / "government-research" / f"office_contacts_{run_date}.json"
    gov_out.write_text(json.dumps({"retrieved": run_date, "note": "Published office routes found by contact research (budgeted searches of "
                                   "official documents and directories). Office titles only; no officials' personal details.", "offices": offices},
                                  indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"welfare_records": str(out.relative_to(C.ROOT)), **counts, "government_offices_with_routes": len(offices)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
