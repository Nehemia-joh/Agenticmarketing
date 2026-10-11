#!/usr/bin/env python3
"""Plan a wave of budgeted contact-research agents. No network calls; databases are read-only.

Run build_contact_profiles.py first. Candidates are organisations that no search agent has searched for yet (a record that
only fetched known pages and found nothing does not count) and that, by --target:
- routes (default): still have no published email or phone;
- decision-makers: have a route but no named decision-maker, and no own website the crawler could read (a site it read
  is left to the crawler);
- all: either.
--include-crawled also plans decision-makers for organisations whose own website the crawler read without finding one, and
--second-pass also plans organisations an earlier wave searched only for a route: data/raw/contact-research/search-targets.json
records what each search file looked for (the planner adds each new wave's files).
Left out by rule:
- company master savings groups (reached through KINEFA, not one by one) and government offices (the government run
  covers them);
- welfare records out of scope, and unclassified register-only NGOs unless --include-unclassified;
- organisations a search found closed.
--target direct-email (added 11 October 2026, docs/plans/high-direct-wave-2026-10-11.md) plans the high-direct wave instead: the
exporter's own high-indirect and medium rows (scripts/messaging/export_resend_contacts.py), each needing the named on-the-ground
decision-maker's own published work email ('own work email'), and an unnamed one the decision-maker first. Slices: companies P1 and
P2 with a named recipient, companies P1 and P2 without one, and introducers with the welfare run; P3 companies get no searches
(depth over breadth, D5) and are reported as not planned. Output files are search_hd<wave>_<slice>_<date>.jsonl, and the prompt
carries the wave's hard rules (an address counts only when a page publishes it; site:-scoped name queries only, D4; directory and
risky-source rules, D3 and D6). --rank reach orders by value (companies: reach tier P1, P2, P3, then desk tier; welfare: priority,
then desk tier; introducers first), then distance, a named recipient before none, and a crawled site first. --orgs-from limits the
plan to the organisations in a JSON list ({db, organisation_id}, or analyse_high_direct_pool.py --detail rows).
--searched-since <date> also counts search files of earlier dates as searched (by default only the date's own files count, so a
new date would forget earlier waves).
Candidates are ranked nearest first within each slice (--rank tier puts the company master's desk tier first: A, B, C, D); --max-per-slice keeps only the nearest so one agent's work stays
manageable (the rest wait for a later wave), or with --split divides a larger slice into balanced parts (<slice>_a, _b, ...)
that each get an agent, still at most four in all. The search budget is split across at most four slices in proportion to
their size (at least 5 each). Writes runtime/contacts/slices/wave<N>_<slice>.json and one agent prompt per slice in
runtime/contacts/prompts/, and prints the plan. Launch at most four agents per wave and never exceed the session's
WebSearch cap (skills/silverleaf-create-lead-list/references/research-rate-limits.md).
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

import contact_lib as C

W = C.W
DBS = {"master": C.ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite",
       "welfare": C.ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"}
MASTER_SKIP = {"Savings group", "office:government"}
WELFARE_SKIP = {"Out of scope"}
UNCLASSIFIED = "Welfare (unclassified child-focused NGO)"
MAX_SLICES = 4
MIN_SLICE = 10
TARGETS = C.RAW / "search-targets.json"
TIER_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3}
SLICE_OF = {"master": lambda seg: "master_hotels" if seg in ("tourism:hotel", "guest_house", "tourism:guest_house") else "master_employers",
            "welfare": lambda seg: "welfare_funders_specialised" if seg in ("Welfare funder", "Welfare specialised centre") else "welfare_care"}

PROMPT = """You are a contact-research agent for Silverleaf Academy (a private English-medium school network in Arusha, Usa River
and Boma Ng'ombe, Tanzania). Follow the agent brief in docs/methodology/contact-research.md exactly; its rules are hard rules.

Slice: {slice_path} ({count} organisations, nearest first).
Search allowance: at most {budget} WebSearch calls, numbered Q1/{budget} ... in your log. Stop searching at the limit; after
that only fetch URLs you already have. If a search is refused because the session's search limit is reached, stop
searching at once, do not retry, continue only with fetches of URLs you already have, and say so in the coverage log.
Never route searches through WebFetch, a browser or a results page. Space fetches to
the same site at least 2 seconds apart, honour robots.txt Disallow rules (a robots.txt that cannot be read does not stop
you; say so in notes), and record a block (403, 429, captcha, login wall, bad
certificate) instead of working around it.

Work through the slice nearest first. Each organisation's needs field says what it still lacks: a published route
(email or phone) or a named decision-maker (owner, founder, managing or executive director, general manager, head, HR);
record whatever the brief allows for both. Start with each organisation's known_sources and any website it lists:
fetching them costs no search. {extra}Search only where that gives nothing, one organisation per query such as "<exact name>" Arusha (or
Tanzania); several names joined with OR give unreliable results. Then fetch the organisation's own contact, about or team
pages. A domain that now shows unrelated content (gambling, escort, parked or for sale) no longer belongs to the
organisation: record that in notes and use nothing from it. Say in notes if an organisation looks closed, outside the
Arusha-Kilimanjaro area, or the same as another record. Record the organisation's published routes (website, role or general email, phones, postal and physical address,
official social pages) and the named people who lead or decide for it, exactly as the organisation, an official register,
a parent body, or a funder or partner naming its current leaders publishes them, with a work email or phone only when that
same source gives it for contact. Never record
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


DIRECT_RULES = """This is a high-direct wave (docs/plans/high-direct-wave-2026-10-11.md, approved 11 October 2026). Hard rules:
- Goal per organisation: the named on-the-ground decision-maker's own published work email (the in-country lead first; a group or
  regional head is recorded as escalation; a chair only when no executive is named). Each organisation's needs say whether the
  person is already named (recipient) or must be found first.
- An address counts only when a page publishes it for that person (in their block, or a mailbox that carries their name on the
  organisation's own site), or for that person's exact role on the organisation's domain (md@, vc@, hr@ for the HR head ...).
  Never construct an address from a pattern (firstname@domain), even when the domain's format is known.
- Sources: the organisation's own site (team, staff, leadership, contact and press pages, annual reports and PDFs), its own
  vacancy notices, official registers, a parent body's official page, and public chamber, association, trade-fair and government
  lists. LinkedIn and other social profiles, data brokers, review sites and anything behind a login stay out.
- A person's name is never searched across other sites. Allowed queries: site:<own domain> "<surname>", site:<own domain> email OR
  contact OR team, "<organisation name>" "@<own domain>", "<organisation name>" annual report filetype:pdf, "<organisation name>"
  vacancy OR "send your application", "<organisation name>" <directory host>.
- Record on each person email_link (same block | name-matched on own site | role inbox for role | directory entry) and
  source_type (own site | register | directory | press or report | vacancy notice); a directory entry also source_date.
- pdpa_risk medium for a named work email on the organisation's own domain; risky for anything on a personal domain or from a site
  whose robots.txt disallows crawling (those are never routes until a person approves them).
- Previous coverage logs in data/raw/contact-research/coverage/ list queries already run for these organisations: do not repeat them.
"""


def ro(path):
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def file_date(path) -> str:
    """The date suffix of a research file name (search_<slice>_<YYYY-MM-DD>.jsonl), '' when there is none."""
    m = re.search(r"_(\d{4}-\d{2}-\d{2})\.jsonl$", path.name)
    return m.group(1) if m else ""


def direct_email_candidates(args, place, searched_for, closed, assigned, wanted) -> dict:
    """{slice: [organisation]} for --target direct-email: the exporter's high-indirect and medium rows (one recipient per business)."""
    sys.path.insert(0, str(C.ROOT / "scripts" / "messaging"))
    import export_resend_contacts as X  # noqa: E402  (the segments, exactly as exported)
    master, welfare = ro(DBS["master"]), ro(DBS["welfare"])
    rows, _ = X.dedupe(X.company_rows(master)[0] + X.welfare_rows(welfare)[0])
    plans = {r["message_id"]: r["organisation_id"] for r in master.execute("SELECT message_id, organisation_id FROM outreach_plans")}
    w_plans = {r["message_id"]: r["organisation_id"] for r in welfare.execute("SELECT message_id, organisation_id FROM outreach_plans")}
    reach = {r["organisation_id"]: r["tier"] for r in master.execute("SELECT organisation_id, tier FROM employer_reach")}
    segments = {("master", r["organisation_id"]): r["segment"] for r in master.execute("SELECT organisation_id, segment FROM organisations")}
    segments |= {("welfare", r["organisation_id"]): r["segment"] for r in welfare.execute("SELECT organisation_id, segment FROM organisations")}
    priority = {r["organisation_id"]: r["priority"] for r in welfare.execute("SELECT organisation_id, priority FROM organisations")}
    websites = {("master", r[0]): r[1] for r in master.execute("SELECT organisation_id, website FROM organisations")}
    websites |= {("welfare", r[0]): r[1] for r in welfare.execute("SELECT organisation_id, website FROM organisations")}
    master.close()
    welfare.close()
    slices, skipped = defaultdict(list), Counter()
    for r in rows:
        if not (r["confidence"] == "medium" or (r["confidence"] == "high" and r["high_route"] == "indirect")):
            continue
        db = "welfare" if r["track"] == "welfare" else "master"
        oid = (w_plans if db == "welfare" else plans).get(r["plan_id"])
        key = (db, oid)
        if not oid or key in closed or key in assigned or (wanted is not None and key not in wanted):
            continue
        named = (r["confidence_reason"].startswith("named, verified") if db == "master"
                 else r["confidence_reason"].startswith(("ready; addressed to the named leader", "ready; named leader")))
        needs = ["own work email"] if named else ["named decision-maker", "own work email"]
        needs = [n for n in needs if not (args.second_pass and n in searched_for.get(key, set()))]
        if not needs or ("own work email" in searched_for.get(key, set()) and not args.second_pass):
            skipped["already searched for an own work email"] += 1
            continue
        tier = reach.get(oid, "") if db == "master" else ""
        if r["track"] == "companies" and tier not in ("P1", "P2"):
            skipped["P3 companies: no searches (depth over breadth, D5)"] += 1
            continue
        name = ("hd_welfare_introducers" if r["track"] in ("welfare", "introducers")
                else "hd_companies_p12_named" if named else "hd_companies_p12_unnamed")
        value = (0 if r["track"] == "introducers" else
                 {"P1": 1, "P2": 2}.get(tier, 3) if db == "master" else {"High": 1, "Medium": 2}.get(priority.get(oid) or "", 3))
        info = place.get(key, {})
        slices[name].append({"db": db, "organisation_id": oid, "name": r["organisation"], "segment": segments.get(key, ""), "track": r["track"],
                             "band": "high-indirect" if r["confidence"] == "high" else "medium", "recipient": r["recipient"] if named else "",
                             "reach_tier": tier, "priority": priority.get(oid, "") if db == "welfare" else "", "value": value,
                             "locality": info.get("locality") or "", "campus": info.get("campus") or "", "distance_km": info.get("distance_km"),
                             "desk_tier": info.get("desk_tier") or "", "needs": needs, "has_named": named,
                             "known_sources": list(dict.fromkeys(s for s in [websites.get(key), info.get("source_url")] if s))[:3]})
    print(json.dumps({"direct-email: left out": dict(skipped)}, indent=1))
    return slices


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="research date, as in the search_*_<date>.jsonl files")
    parser.add_argument("--wave", type=int, required=True)
    parser.add_argument("--budget", type=int, required=True, help="WebSearch calls this wave may use in total")
    parser.add_argument("--include-unclassified", action="store_true")
    parser.add_argument("--target", choices=("routes", "decision-makers", "all", "direct-email"), default="routes",
                        help="what the organisations still lack: a published email or phone (default), a named decision-maker, either, or "
                             "(direct-email) the named on-the-ground decision-maker's own published work email for the exporter's "
                             "high-indirect and medium rows")
    parser.add_argument("--orgs-from", type=Path, help="plan only the organisations in this JSON list ({db, organisation_id} or "
                                                       "analyse_high_direct_pool.py --detail rows)")
    parser.add_argument("--searched-since", help="also count search files dated from this date (YYYY-MM-DD) as searched, not only the date's own")
    parser.add_argument("--max-per-slice", type=int, default=0, help="keep only the nearest N organisations in each slice (0 keeps all)")
    parser.add_argument("--split", action="store_true",
                        help="with --max-per-slice, divide a larger slice into balanced parts of at most that size instead of deferring the rest")
    parser.add_argument("--include-crawled", action="store_true",
                        help="decision-makers: also organisations whose own website the crawler read without finding one")
    parser.add_argument("--second-pass", action="store_true",
                        help="also organisations an earlier wave searched, unless it already looked for what they still lack (search-targets.json)")
    parser.add_argument("--db", choices=("master", "welfare"), help="plan only this database's organisations")
    parser.add_argument("--exclude-wave", type=int, action="append", default=[],
                        help="leave out organisations already in this wave's slices (a wave whose agents are still running)")
    parser.add_argument("--max-slices", type=int, default=MAX_SLICES, help="agents in this plan (at most four)")
    parser.add_argument("--rank", choices=("distance", "tier", "reach"), default="distance",
                        help="order within a slice: nearest first (default), the company master's desk tier first, then nearest, or (reach) "
                             "value first: introducers, reach tier P1/P2 or welfare priority, desk tier, then nearest, named, crawled")
    args = parser.parse_args()
    profiles = json.loads((C.WORK / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    # Research records can carry a stale organisation ID (see contact_lib.Resolver).
    resolve = C.Resolver((p["db"], p["organisation_id"], p["name"]) for p in profiles)
    # Organisations whose own website the crawler read: finding their people is the crawler's job, not a search's.
    crawl_path = C.RAW / f"website_contacts_{args.date}.jsonl"
    read_by_crawler = set()
    for line in (crawl_path.read_text(encoding="utf-8").splitlines() if crawl_path.exists() else []):
        site = json.loads(line) if line.strip() else {}
        if any(page.get("status") == 200 for page in site.get("pages", [])):
            read_by_crawler |= {resolve(o["db"], o["organisation_id"], o["name"]) for o in site["orgs"]}
    # Named decision-makers already known: in the databases, or found by this research and not merged yet.
    deciders = {(p["db"], p["organisation_id"]) for p in profiles if any(x["decision_maker"] for x in p["people"])}
    targets = json.loads(TARGETS.read_text(encoding="utf-8")) if TARGETS.exists() else {"files": {}}
    searched, closed = set(), set()
    searched_for = defaultdict(set)  # what earlier waves searched each organisation for
    search_files = [p for p in C.RAW.glob("search_*.jsonl")
                    if file_date(p) == args.date or (args.searched_since and args.searched_since <= file_date(p) <= args.date)]
    for path in search_files:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                key = resolve(r.get("db"), r.get("organisation_id"), r.get("organisation_name", "")) or (r.get("db"), r.get("organisation_id"))
                # An organisation an agent only fetched pages for (no search) and found no route for stays a candidate.
                if r.get("searches_used", 1) or r.get("status") == "found":
                    searched.add(key)
                    searched_for[key] |= set(targets["files"].get(path.name, ["published route", "named decision-maker"]))
                if C.CLOSURE.search(str(r.get("notes") or "")):
                    closed.add(key)
    # Organisations handed to a wave that is still running: their records are not all written yet.
    assigned = {(o["db"], o["organisation_id"]) for wave in args.exclude_wave
                for path in [*(C.WORK / "slices").glob(f"wave{wave}_*.json"), *(C.WORK / "slices").glob(f"hd{wave}_*.json")]
                for o in json.loads(path.read_text(encoding="utf-8"))}
    wanted = None
    if args.orgs_from:
        wanted = {(o.get("db") or ("welfare" if o.get("track") == "welfare" else "master"), o["organisation_id"])
                  for o in json.loads(args.orgs_from.read_text(encoding="utf-8"))}
    place, planned = {}, set()
    for db, path in DBS.items():
        con = ro(path)
        columns = {r[1] for r in con.execute("PRAGMA table_info(organisations)")}
        source = "source_url" if "source_url" in columns else "website AS source_url"
        tier = "desk_tier" if "desk_tier" in columns else "'' AS desk_tier"
        for r in con.execute(f"SELECT organisation_id, locality, campus, distance_km, {tier}, {source} FROM organisations"):
            place[(db, r["organisation_id"])] = dict(r)
        # Only organisations outreach is planned for: triage exclusions (religious bodies, welfare-linked records) are not researched.
        planned |= {(db, oid) for (oid,) in con.execute("SELECT DISTINCT organisation_id FROM outreach_plans")}
        deciders |= {(db, oid) for oid, name, role in con.execute("SELECT organisation_id, name, role FROM contacts")
                     if name and C.DECISION.search(C.NOT_A_HEAD.sub("", role or ""))}
        con.close()
    slices = defaultdict(list)
    if args.target == "direct-email":
        slices = direct_email_candidates(args, place, searched_for, closed, assigned, wanted)
        if args.db:
            slices = defaultdict(list, {n: [o for o in items if o["db"] == args.db] for n, items in slices.items()})
    for p in (profiles if args.target != "direct-email" else []):
        key = (p["db"], p["organisation_id"])
        if wanted is not None and key not in wanted:
            continue
        if (p["db"] not in SLICE_OF or (args.db and p["db"] != args.db) or key in closed or key not in planned or key in assigned
                or (key in searched and not args.second_pass)):
            continue
        direct = p["known"]["email"] or p["known"]["phone"] or p["emails"] or p["phones"]
        skip = MASTER_SKIP if p["db"] == "master" else WELFARE_SKIP | (set() if args.include_unclassified else {UNCLASSIFIED})
        needs = []
        if not direct and args.target in ("routes", "all"):
            needs.append("published route")
        if direct and key not in deciders and (key not in read_by_crawler or args.include_crawled) and args.target in ("decision-makers", "all"):
            needs.append("named decision-maker")
        # A second pass looks again only for what no earlier wave searched this organisation for.
        needs = [n for n in needs if n not in searched_for.get(key, set())]
        if not needs or p["segment"] in skip:
            continue
        info = place.get(key, {})
        slices[SLICE_OF[p["db"]](p["segment"])].append({
            "db": p["db"], "organisation_id": p["organisation_id"], "name": p["name"], "segment": p["segment"], "locality": info.get("locality") or "",
            "campus": info.get("campus") or "", "distance_km": info.get("distance_km"), "desk_tier": info.get("desk_tier") or "", "needs": needs,
            "known_sources": [s for s in [info.get("source_url"), *(w for w in p["websites"])] if s][:3]})
    # A slice too small to justify its own agent joins the largest slice of the same database (a direct-email wave keeps its slices).
    for name in sorted(slices, key=lambda n: len(slices[n])):
        same_db = [n for n in slices if n != name and n.split("_")[0] == name.split("_")[0]]
        if len(slices[name]) < MIN_SLICE and same_db and args.target != "direct-email":
            slices[max(same_db, key=lambda n: len(slices[n]))].extend(slices.pop(name))
    max_slices = max(1, min(args.max_slices, MAX_SLICES))
    top = sorted(slices.items(), key=lambda kv: -len(kv[1]))[:max_slices]
    waiting, parts = {}, []
    crawled = read_by_crawler | {resolve(o["db"], o["organisation_id"], o["name"]) for path in C.RAW.glob("website_contacts_*.jsonl")
                                 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
                                 for site in [json.loads(line)] if any(pg.get("status") == 200 for pg in site.get("pages", []))
                                 for o in site["orgs"]} if args.rank == "reach" else set()

    def order(o):
        near = (o["distance_km"] in (None, ""), float(o["distance_km"] or 0))
        if args.rank == "tier":
            return (TIER_ORDER.get(str(o["desk_tier"])[:1], 4),) + near
        if args.rank == "reach":
            desk = TIER_ORDER.get(str(o["desk_tier"])[:1], int(str(o["desk_tier"])[1:2]) - 1 if re.fullmatch(r"P\d", str(o["desk_tier"])) else 4)
            return (o.get("value", 3), desk) + near + (not o.get("has_named", False), (o["db"], o["organisation_id"]) not in crawled)
        return near
    for name, items in top:
        items.sort(key=order)
        if args.max_per_slice and len(items) > args.max_per_slice:
            if args.split:
                # Balanced parts of at most --max-per-slice each, nearest first; each part gets its own agent.
                count = math.ceil(len(items) / args.max_per_slice)
                size = math.ceil(len(items) / count)
                parts += [(f"{name}_{chr(ord('a') + i)}", items[i * size:(i + 1) * size]) for i in range(count)]
                continue
            waiting[name] = len(items) - args.max_per_slice
            del items[args.max_per_slice:]
        parts.append((name, items))
    chosen = parts[:max_slices]  # still at most four agents; any further part waits for a later wave
    waiting.update({name: len(items) for name, items in parts[max_slices:]})
    total = sum(len(v) for _, v in chosen)
    plan, out_dir, prompt_dir = [], C.WORK / "slices", C.WORK / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)
    budgets = {name: max(5, round(args.budget * len(items) / total)) if total else 0 for name, items in chosen}
    while sum(budgets.values()) > args.budget and any(b > 5 for b in budgets.values()):
        budgets[max(budgets, key=budgets.get)] -= 1
    for name, items in chosen:
        slug = f"hd{args.wave}_{name[3:]}" if name.startswith("hd_") else f"wave{args.wave}_{name}"
        slice_path = out_dir / f"{slug}.json"
        slice_path.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        output_path = C.RAW / f"search_{slug}_{args.date}.jsonl"
        coverage_path = C.RAW / "coverage" / f"{slug}_coverage.md"
        extra = ("The welfare run's own research (data/raw/welfare-research/research_*.jsonl) often cites sources for these organisations; "
                 "reuse them.\n" if "welfare" in name else "")
        if args.target == "direct-email":
            extra = DIRECT_RULES + extra
        prompt = PROMPT.format(slice_path=slice_path.relative_to(C.ROOT).as_posix(), count=len(items), budget=budgets[name], extra=extra,
                               output_path=output_path.relative_to(C.ROOT).as_posix(), coverage_path=coverage_path.relative_to(C.ROOT).as_posix(),
                               slice=slug)
        (prompt_dir / f"{slug}.md").write_text(prompt, encoding="utf-8")
        plan.append({"slice": slug, "organisations": len(items), "searches": budgets[name], "prompt": (prompt_dir / f"{slug}.md").relative_to(C.ROOT).as_posix(),
                     "needs": {n: sum(1 for o in items if n in o["needs"]) for n in ("published route", "named decision-maker", "own work email")}})
        targets["files"][output_path.name] = sorted({n for o in items for n in o["needs"]}, reverse=True)
    if chosen:
        targets["files"] = dict(sorted(targets["files"].items()))
        TARGETS.write_text(json.dumps(targets, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    left_out = {name: len(items) for name, items in sorted(slices.items()) if name not in dict(top)}
    print(json.dumps({"wave": args.wave, "target": args.target, "budget": args.budget, "searches_planned": sum(budgets.values()), "slices": plan,
                      "not_planned": left_out, "waiting_beyond_slice_limit": waiting, "already_searched": len(searched), "closed": len(closed)},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
