#!/usr/bin/env python3
"""Plan a wave of budgeted contact-research agents. No network calls; databases are read-only.

Run build_contact_profiles.py first. Candidates are organisations that still have no published email or phone and that
no search agent has searched for yet (a record that only fetched known pages and found nothing does not count). Left out by rule:
- company master savings groups (reached through KINEFA, not one by one) and government offices (the government run
  covers them);
- welfare records out of scope, and unclassified register-only NGOs unless --include-unclassified;
- organisations a search found closed.
Candidates are ranked nearest first within each slice, and the search budget is split across at most four slices in
proportion to their size (at least 5 each). Writes runtime/contacts/slices/wave<N>_<slice>.json and one agent prompt
per slice in runtime/contacts/prompts/, and prints the plan. Launch at most four agents per wave and never exceed the
session's WebSearch cap (skills/silverleaf-create-lead-list/references/research-rate-limits.md).
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict

import contact_lib as C

W = C.W
DBS = {"master": C.ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite",
       "welfare": C.ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"}
MASTER_SKIP = {"Savings group", "office:government"}
WELFARE_SKIP = {"Out of scope"}
UNCLASSIFIED = "Welfare (unclassified child-focused NGO)"
MAX_SLICES = 4
MIN_SLICE = 10
SLICE_OF = {"master": lambda seg: "master_hotels" if seg in ("tourism:hotel", "guest_house", "tourism:guest_house") else "master_employers",
            "welfare": lambda seg: "welfare_funders_specialised" if seg in ("Welfare funder", "Welfare specialised centre") else "welfare_care"}

PROMPT = """You are a contact-research agent for Silverleaf Academy (a private English-medium school network in Arusha, Usa River
and Boma Ng'ombe, Tanzania). Follow the agent brief in docs/methodology/contact-research.md exactly; its rules are hard rules.

Slice: {slice_path} ({count} organisations, nearest first).
Search allowance: at most {budget} WebSearch calls, numbered Q1/{budget} ... in your log. Stop searching at the limit; after
that only fetch URLs you already have. Never route searches through WebFetch, a browser or a results page. Space fetches to
the same site at least 2 seconds apart, honour robots.txt, and record a block (403, 429, captcha, login wall, bad
certificate) instead of working around it.

Work through the slice nearest first. Start with each organisation's known_sources and any website it lists: fetching them
costs no search. {extra}Search only where that gives nothing, one organisation per query such as "<exact name>" Arusha (or
Tanzania); several names joined with OR give unreliable results. Then fetch the organisation's own contact, about or team
pages. A domain that now shows unrelated content (gambling, escort, parked or for sale) no longer belongs to the
organisation: record that in notes and use nothing from it. Say in notes if an organisation looks closed, outside the
Arusha-Kilimanjaro area, or the same as another record. Record the organisation's published routes (website, role or general email, phones, postal and physical address,
official social pages) and the named people who lead or decide for it, exactly as the organisation, an official register
or a parent body publishes them, with a work email or phone only when that same source gives it for contact. Never record
personal social profiles, home addresses, family details, biographies, anything about children, parents or residents, or
party affiliation. Mark snippet-only facts fetched: false, and anything not clearly the same organisation identity: uncertain.

Write one JSON line per organisation you researched (including those with nothing found) to
{output_path}
with the fields db, organisation_id, organisation_name, status (found|partial|not_found|blocked), identity
(confirmed|uncertain), searches_used, website, emails [{{value, type, source_url, fetched}}], phones [{{value, type,
source_url, fetched}}], postal_address {{value, source_url}}, physical_address {{value, source_url}}, socials [{{platform,
url, source_url}}], people [{{name, role, email, phone, source_url, fetched, excerpt, pdpa_risk, pdpa_risk_reason}}],
sources [{{url, title, fetched, accessed_on, excerpt, facts}}], notes. Copy db and organisation_id from the slice.
Also write a coverage log to {coverage_path}: every search with its number and outcome, blocked sites, and the
organisations not reached. Keep scratch files in your own folder under runtime/contacts/agents/{slice}/. Do not change
any other file and do not contact anyone. Finish with a short report: counts by status, searches used, leads found,
blocks, and organisations not reached.
"""


def ro(path):
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="research date, as in the search_*_<date>.jsonl files")
    parser.add_argument("--wave", type=int, required=True)
    parser.add_argument("--budget", type=int, required=True, help="WebSearch calls this wave may use in total")
    parser.add_argument("--include-unclassified", action="store_true")
    args = parser.parse_args()
    profiles = json.loads((C.WORK / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    searched, closed = set(), set()
    for path in C.RAW.glob(f"search_*_{args.date}.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                # An organisation an agent only fetched pages for (no search) and found no route for stays a candidate.
                if r.get("searches_used", 1) or r.get("status") == "found":
                    searched.add((r.get("db"), r.get("organisation_id")))
                if C.CLOSURE.search(str(r.get("notes") or "")):
                    closed.add((r.get("db"), r.get("organisation_id")))
    place, planned = {}, set()
    for db, path in DBS.items():
        con = ro(path)
        columns = {r[1] for r in con.execute("PRAGMA table_info(organisations)")}
        source = "source_url" if "source_url" in columns else "website AS source_url"
        for r in con.execute(f"SELECT organisation_id, locality, campus, distance_km, {source} FROM organisations"):
            place[(db, r["organisation_id"])] = dict(r)
        # Only organisations outreach is planned for: triage exclusions (religious bodies, welfare-linked records) are not researched.
        planned |= {(db, oid) for (oid,) in con.execute("SELECT DISTINCT organisation_id FROM outreach_plans")}
        con.close()
    slices = defaultdict(list)
    for p in profiles:
        key = (p["db"], p["organisation_id"])
        if p["db"] not in SLICE_OF or key in searched or key in closed or key not in planned:
            continue
        direct = p["known"]["email"] or p["known"]["phone"] or p["emails"] or p["phones"]
        skip = MASTER_SKIP if p["db"] == "master" else WELFARE_SKIP | (set() if args.include_unclassified else {UNCLASSIFIED})
        if direct or p["segment"] in skip:
            continue
        info = place.get(key, {})
        slices[SLICE_OF[p["db"]](p["segment"])].append({
            "db": p["db"], "organisation_id": p["organisation_id"], "name": p["name"], "segment": p["segment"], "locality": info.get("locality") or "",
            "campus": info.get("campus") or "", "distance_km": info.get("distance_km"),
            "known_sources": [s for s in [info.get("source_url"), *(w for w in p["websites"])] if s][:3]})
    # A slice too small to justify its own agent joins the largest slice of the same database.
    for name in sorted(slices, key=lambda n: len(slices[n])):
        same_db = [n for n in slices if n != name and n.split("_")[0] == name.split("_")[0]]
        if len(slices[name]) < MIN_SLICE and same_db:
            slices[max(same_db, key=lambda n: len(slices[n]))].extend(slices.pop(name))
    chosen = sorted(slices.items(), key=lambda kv: -len(kv[1]))[:MAX_SLICES]
    total = sum(len(v) for _, v in chosen)
    plan, out_dir, prompt_dir = [], C.WORK / "slices", C.WORK / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)
    budgets = {name: max(5, round(args.budget * len(items) / total)) if total else 0 for name, items in chosen}
    while sum(budgets.values()) > args.budget and any(b > 5 for b in budgets.values()):
        budgets[max(budgets, key=budgets.get)] -= 1
    for name, items in chosen:
        items.sort(key=lambda o: (o["distance_km"] in (None, ""), float(o["distance_km"] or 0)))
        slug = f"wave{args.wave}_{name}"
        slice_path = out_dir / f"{slug}.json"
        slice_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        output_path = C.RAW / f"search_{slug}_{args.date}.jsonl"
        coverage_path = C.RAW / "coverage" / f"{slug}_coverage.md"
        extra = ("The welfare run's own research (data/raw/welfare-research/research_*.jsonl) often cites sources for these organisations; "
                 "reuse them.\n" if name.startswith("welfare") else "")
        prompt = PROMPT.format(slice_path=slice_path.relative_to(C.ROOT).as_posix(), count=len(items), budget=budgets[name], extra=extra,
                               output_path=output_path.relative_to(C.ROOT).as_posix(), coverage_path=coverage_path.relative_to(C.ROOT).as_posix(),
                               slice=slug)
        (prompt_dir / f"{slug}.md").write_text(prompt, encoding="utf-8")
        plan.append({"slice": slug, "organisations": len(items), "searches": budgets[name], "prompt": (prompt_dir / f"{slug}.md").relative_to(C.ROOT).as_posix()})
    left_out = {name: len(items) for name, items in sorted(slices.items()) if name not in dict(chosen)}
    print(json.dumps({"wave": args.wave, "budget": args.budget, "searches_planned": sum(budgets.values()), "slices": plan, "not_planned": left_out,
                      "already_searched": len(searched), "closed": len(closed)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
