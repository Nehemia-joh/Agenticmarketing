#!/usr/bin/env python3
"""Plan a welfare research run: split the web-search budget across slices and write one prompt per slice.

The agent WebSearch tool has a per-session cap (CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION; 200 in the 2026-09 run)
that every subagent shares. In the first run, eight unbudgeted parallel agents spent it in about 40 minutes and some
slices got almost nothing. This script bakes each slice's share into its prompt, keeps a reserve for the coordinator,
and groups slices into waves. Details: skills/silverleaf-create-lead-list/references/research-rate-limits.md.

Each prompt also carries what the research ledger (data/raw/research-ledger/research_ledger.jsonl, scripts/research/ledger.py)
records for the slice: the searches its earlier runs made, which of its search ideas were already run, and which seeds were
already researched, so no agent repeats them inside the retry window (--min-retry-days, default 90). A skill installed on its own
without the ledger plans as before.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import date as today_date
from pathlib import Path

import welfare_lib as W

try:  # the research ledger lives in the repository's scripts/research/; a standalone skill install has none
    sys.path.insert(0, str(W.ROOT / "scripts" / "research"))
    import ledger as LG  # noqa: E402
except ImportError:  # pragma: no cover
    LG = None

TRIED_CHARS = 3500  # the already-tried section of one prompt stays small


def tried_section(tried, s: dict, retry_days: int) -> str:
    """What the ledger records for this slice: its earlier searches, its search ideas already run, its seeds already researched."""
    if tried is None:
        return "none (no research ledger in this installation)"
    ideas = {LG.plain(q).strip(): q for q in s.get("queries", [])}
    earlier, ideas_run = {}, {}
    for e in tried.entries:
        if e.get("tool") != "websearch" or e.get("date", "") > tried.as_of or e.get("outcome") in LG.NOT_MADE or not e.get("query"):
            continue
        key = LG.plain(e["query"]).strip().strip('"')
        if key in ideas:
            ideas_run[ideas[key]] = f"{e['date']} {e.get('outcome')}"
        if str(e.get("run", "")).startswith("welfare-") and str(e.get("agent", "")).startswith(f"{s['id']}_"):
            earlier[e["query"]] = f"{e['date']} {e.get('outcome')}"
    seeds = []
    index = LG.org_index()
    for seed in s.get("seeds", []):
        name = re.sub(r"\s*\([^)]*\)\s*$", "", seed).strip()
        key = index.resolve(name, "welfare") or index.fuzzy(name, "welfare")
        items = tried.summary(*(key or ("welfare", "")), name=name, max_items=3, max_chars=160)
        if items:
            seeds.append(f"{seed}: " + "; ".join(items))
    parts = []
    if ideas_run:
        parts.append("Search ideas above already run (do not run them again): " + "; ".join(f"`{q}` ({v})" for q, v in ideas_run.items()))
    if earlier:
        parts.append(f"Searches this slice's earlier runs made ({len(earlier)}; do not repeat them): " +
                     "; ".join(f"`{q}` ({v})" for q, v in list(earlier.items())[:40]))
    if seeds:
        parts.append("Seeds already researched (read their sources; search only for what is still missing): " + " | ".join(seeds))
    text = "\n".join(parts) or "nothing recorded for this slice"
    if len(text) > TRIED_CHARS:
        text = text[:TRIED_CHARS].rsplit(";", 1)[0] + f"; ... (the rest: python scripts/research/ledger.py tried --pattern ... or --name <seed>)"
    return f"(research ledger, as of {tried.as_of}; retry window {retry_days} days)\n{text}"

PROMPT = """You are a lead researcher for Silverleaf Academy (Tanzania). First read the shared brief in full and follow it exactly: {brief}

Your slice: **{id} — {title}**. {focus}

Localities: {localities}

Seeds to check (unverified hints; confirm or discard): {seeds}

Search ideas (English and Kiswahili): {queries}

Priorities carried over from the last run's coverage logs: {priorities}

Already tried {tried}

{ledger_rules}

Research budget (hard limits):
- You may make at most **{budget} WebSearch calls**. Number each query in your coverage log as "Q<n>/{budget}" and stop searching at {budget}.
- The WebSearch cap is shared by every agent in this session. If a search returns a budget or limit error, stop searching at once and say so in the coverage log.
- Once your searches are spent, continue only with WebFetch on URLs you have already found. Never route searches through WebFetch, a browser or a search-engine results page.
- Pace WebFetch to about one request every 2 seconds on the same site; if a site returns 403 or 429, record it as blocked and move on.
- Do not use browser tools. Do not sign in, submit forms or contact anyone.

Stopping rule: stop when {stop_rule}, or when your search budget is spent, whichever comes first. Record which applied.

Write outputs (append as you confirm records; if a file already exists, add to it and never delete existing lines):
- Records: {records}
- Coverage log: {coverage}
Validate that every JSONL line parses before you finish. Final reply under 200 words as the brief says.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--search-budget", type=int, default=int(os.environ.get("CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION", "200")),
                        help="per-session WebSearch cap (defaults to CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION or 200)")
    parser.add_argument("--already-used", type=int, default=0, help="searches already spent in this session")
    parser.add_argument("--reserve", type=float, default=0.10, help="share kept for the coordinator's own checks")
    parser.add_argument("--max-parallel", type=int, default=4, help="agents per wave")
    parser.add_argument("--slices", default=str(W.SKILL / "references" / "research-slices.json"))
    parser.add_argument("--only", help="comma-separated slice ids, e.g. a refresh of unfinished slices")
    parser.add_argument("--min-retry-days", type=int, default=90,
                        help="days before a search the research ledger records may be run again (default 90)")
    parser.add_argument("--as-of", default=today_date.today().isoformat(), help="plan date for the research ledger (default today)")
    args = parser.parse_args()
    tried = LG.Tried(as_of=args.as_of, retry_days=args.min_retry_days) if LG and LG.LEDGER.exists() else None
    cfg = W.load_config(args.run_id)
    date = cfg["research_date"]
    slices = json.loads(Path(args.slices).read_text(encoding="utf-8"))["slices"]
    if args.only:
        wanted = {s.strip() for s in args.only.split(",")}
        slices = [s for s in slices if s["id"] in wanted]
    available = max(0, args.search_budget - args.already_used)
    reserve = math.ceil(available * args.reserve)
    pool = available - reserve
    total_weight = sum(s["weight"] for s in slices) or 1
    work = cfg["paths"]["work"]
    (work / "prompts").mkdir(parents=True, exist_ok=True)
    brief_path = work / "research-brief.md"
    brief = (W.SKILL / "references" / "research-brief.md").read_text(encoding="utf-8")
    brief_path.write_text(brief.replace("{run_id}", args.run_id).replace("{research_date}", date), encoding="utf-8")
    plan = {"run_id": args.run_id, "research_date": date, "search_budget": args.search_budget, "already_used": args.already_used,
            "reserve_for_coordinator": reserve, "max_parallel": args.max_parallel, "slices": [], "waves": []}
    for index, s in enumerate(slices):
        budget = int(pool * s["weight"] / total_weight)
        records = W.ROOT / "data" / "raw" / "welfare-research" / f"research_{s['id']}_{s['name']}_{date}.jsonl"
        coverage = W.ROOT / "data" / "raw" / "welfare-research" / "coverage" / f"{s['id']}_{s['name']}_coverage.md"
        prompt = PROMPT.format(brief=brief_path, id=s["id"], title=s["title"], focus=s["focus"],
                               localities=", ".join(s.get("localities", [])) or "the whole catchment",
                               seeds="; ".join(s.get("seeds", [])) or "none", queries="; ".join(s.get("queries", [])),
                               priorities="; ".join(s.get("next_run_priorities", [])) or "none", budget=budget,
                               stop_rule=s.get("stop_rule", "12 consecutive varied queries produce nothing new"),
                               records=records, coverage=coverage, tried=tried_section(tried, s, args.min_retry_days),
                               ledger_rules=(LG.AGENT_RULES.format(retry_days=args.min_retry_days, slice=f"{s['id']}_{s['name']}")
                                             if LG else ""))
        prompt_path = work / "prompts" / f"{s['id']}_{s['name']}.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        if records.exists():
            print(f"WARNING: {records.relative_to(W.ROOT)} already exists; its agent will append to it. Use a new research_date "
                  "in run-config.json for a fresh run.")
        plan["slices"].append({"id": s["id"], "name": s["name"], "weight": s["weight"], "web_searches": budget,
                               "wave": index // args.max_parallel + 1, "prompt": str(prompt_path.relative_to(W.ROOT)),
                               "records": str(records.relative_to(W.ROOT)), "coverage": str(coverage.relative_to(W.ROOT))})
    plan["waves"] = sorted({s["wave"] for s in plan["slices"]})
    out = cfg["paths"]["run_data"] / "research-plan.json"
    out.write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
    print(f"Search budget {args.search_budget} (used {args.already_used}); coordinator reserve {reserve}; per-slice allocation:")
    for s in plan["slices"]:
        print(f"  wave {s['wave']}  {s['id']} {s['name']:<24} {s['web_searches']:>3} searches  -> {s['prompt']}")
    print("Run the deterministic collectors (fetch_ngo_register.py, collect_osm_welfare.py) before wave 1; launch at most "
          f"{args.max_parallel} agents per wave; start the next wave when the previous one finishes.")
    print(f"Plan written to {out.relative_to(W.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
