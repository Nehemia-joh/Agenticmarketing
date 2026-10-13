#!/usr/bin/env python3
"""Check that every document and script pair meant to be identical is identical. Read-only.

  python scripts/docs/check_doc_pairs.py            # list the pairs; exit 1 on any difference
  python scripts/docs/check_doc_pairs.py --diff     # also print a unified diff of each pair that differs

The pairs:
- docs/strategy/<name>.md and skills/silverleaf-outreach/references/<name>.md: campaign-positioning-and-cadence,
  new-lead-acquisition-framework, offer-register, hook-guidance;
- docs/strategy/outreach-flows.md and skills/silverleaf-outreach/references/flows-and-automations.md (one document under two
  names: the skill names it by its use);
- every scripts/welfare/*.py and its copy in skills/silverleaf-welfare-leads/scripts/, and every scripts/government/*.py and its
  copy in skills/silverleaf-government-leads/scripts/ (a file on one side only is a failure too).

Line endings are ignored (core.autocrlf rewrites them on checkout). A relative Markdown link in a document pair must resolve
from both folders, because the two copies are byte-identical; use a repository path in backticks for anything else.
Edit the docs/ or scripts/ side first, then copy it over the skill side (Copy-Item), and run this check before committing.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTREACH = "skills/silverleaf-outreach/references"
DOC_PAIRS = [(f"docs/strategy/{n}.md", f"{OUTREACH}/{n}.md")
             for n in ("campaign-positioning-and-cadence", "new-lead-acquisition-framework", "offer-register", "hook-guidance")]
DOC_PAIRS.append(("docs/strategy/outreach-flows.md", f"{OUTREACH}/flows-and-automations.md"))
SCRIPT_DIRS = [("scripts/welfare", "skills/silverleaf-welfare-leads/scripts"),
               ("scripts/government", "skills/silverleaf-government-leads/scripts")]
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def pairs() -> list[tuple[str, str]]:
    out = list(DOC_PAIRS)
    for a, b in SCRIPT_DIRS:
        names = {p.name for p in (ROOT / a).glob("*.py")} | {p.name for p in (ROOT / b).glob("*.py")}
        out += [(f"{a}/{n}", f"{b}/{n}") for n in sorted(names)]
    return out


def text(path: Path) -> str | None:
    return path.read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n") if path.exists() else None


def broken_links(a: str, body: str, b: str) -> list[str]:
    """Relative links that resolve from one copy's folder but not from the other's."""
    bad = []
    for target in LINK.findall(body):
        if re.match(r"^[a-z]+:", target):
            continue
        ok_a, ok_b = (ROOT / a).parent.joinpath(target).exists(), (ROOT / b).parent.joinpath(target).exists()
        if ok_a != ok_b or not ok_a:
            bad.append(target)
    return sorted(set(bad))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--diff", action="store_true", help="print a unified diff for each pair that differs")
    args = parser.parse_args()
    failures = 0
    for a, b in pairs():
        ta, tb = text(ROOT / a), text(ROOT / b)
        if ta is None or tb is None:
            status = f"missing: {a if ta is None else b}"
        elif ta != tb:
            changed = sum(1 for line in difflib.unified_diff(ta.splitlines(), tb.splitlines(), lineterm="", n=0)
                          if line[:1] in "+-" and not line.startswith(("+++", "---")))
            status = f"DIFFERENT ({changed} lines)"
        else:
            links = broken_links(a, ta, b) if a.endswith(".md") else []
            status = f"link resolves in one folder only: {', '.join(links)}" if links else "identical"
        if status != "identical":
            failures += 1
        print(f"{'ok  ' if status == 'identical' else 'FAIL'} {a}  <->  {b}: {status}")
        if args.diff and ta is not None and tb is not None and ta != tb:
            sys.stdout.writelines(line + "\n" for line in difflib.unified_diff(ta.splitlines(), tb.splitlines(), a, b, lineterm=""))
    print(f"{len(pairs())} pairs, {failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
