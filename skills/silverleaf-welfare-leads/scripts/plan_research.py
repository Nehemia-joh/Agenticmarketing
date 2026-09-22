#!/usr/bin/env python3
"""Plan a welfare research run: split the web-search budget across slices and write one prompt per slice.

The agent WebSearch tool has a per-session cap (CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION; 200 in the 2026-09 run)
that every subagent shares. In the first run, eight unbudgeted parallel agents spent it in about 40 minutes and some
slices got almost nothing. This script bakes each slice's share into its prompt, keeps a reserve for the coordinator,
and groups slices into waves. Details: skills/silverleaf-create-lead-list/references/research-rate-limits.md.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import welfare_lib as W

PROMPT = """You are a lead researcher for Silverleaf Academy (Tanzania). First read the shared brief in full and follow it exactly: {brief}

Your slice: **{id} — {title}**. {focus}

Localities: {localities}

Seeds to check (unverified hints; confirm or discard): {seeds}

Search ideas (English and Kiswahili): {queries}

Priorities carried over from the last run's coverage logs: {priorities}

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
    args = parser.parse_args()
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
                               records=records, coverage=coverage)
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
