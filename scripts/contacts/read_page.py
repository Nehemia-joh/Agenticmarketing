#!/usr/bin/env python3
"""Read one web page politely for a research agent, and print its visible text so facts can be quoted exactly.

Uses the contact-research fetcher in contact_lib.py:
- responses are cached under runtime/contacts/http-cache/ (never committed);
- requests to one site are spaced 1.5 s apart;
- explicit robots.txt Disallow rules are honoured;
- a robots.txt that cannot be read is reported, and the page is read anyway (the user's decision of 23 September 2026);
- a block (403, 429, login wall, captcha) is reported and never worked around.

The first line printed is a JSON header: url, final_url, status, robots, title and the page's SHA-256. The page text
follows, one line per block. Quote excerpts from that text exactly.

Usage: python scripts/contacts/read_page.py <url> [--grep word ...] [--max-lines 400]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys

import contact_lib as C


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--grep", nargs="*", default=[], help="print only lines containing one of these words (any case), with a line of context")
    parser.add_argument("--max-lines", type=int, default=400)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    url = args.url if "://" in args.url else "https://" + args.url
    robots, state = C.robots_state(C.site_base(url))
    if not C.allowed(robots, url):
        print(json.dumps({"url": url, "robots": "disallowed", "note": "robots.txt disallows this page: not read"}))
        return 2
    result = C.fetch(url, retries=1)
    final = result.get("final_url") or url
    if C.site_base(final) != C.site_base(url):
        robots, state = C.robots_state(C.site_base(final))
        if not C.allowed(robots, final):
            print(json.dumps({"url": url, "final_url": final, "robots": "disallowed", "note": "the redirect target's robots.txt disallows it: not read"}))
            return 2
    body = result.get("body") or b""
    header = {"url": url, "final_url": final, "status": result.get("status"), "error": result.get("error", ""),
              "robots": {"rules": "read; allowed", "none": "none (4xx)", "unreachable": "could not be read; page read anyway, flag it"}[state],
              "sha256": hashlib.sha256(body).hexdigest() if body else ""}
    if result.get("status") != 200 or not body:
        print(json.dumps(header))
        return 1
    lines, doc = C.html_lines(body)
    header["title"] = " ".join((doc.findtext(".//title") or "").split())[:200] if doc is not None else ""
    print(json.dumps(header, ensure_ascii=False))
    if args.grep:
        words = [w.lower() for w in args.grep]
        keep = sorted({j for i, line in enumerate(lines) if any(w in line.lower() for w in words) for j in (i - 1, i, i + 1) if 0 <= j < len(lines)})
        lines = [lines[i] for i in keep]
    for line in lines[: args.max_lines]:
        print(line)
    if len(lines) > args.max_lines:
        print(f"... {len(lines) - args.max_lines} more lines (use --grep or --max-lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
