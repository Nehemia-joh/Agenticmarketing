#!/usr/bin/env python3
"""Crawl each organisation's own website for the contact details and named leaders it publishes, politely.

Targets are the organisations with their own website in the company master and the welfare run (read-only);
council and regional sites are covered by scripts/government/collect_council_sites.py. For each site: robots.txt,
the home page, then up to five same-site pages that look like contact, team or about pages. One request at a time
per site, 1.5 s apart, several sites in parallel; HTTP 403 and other blocks are recorded, never bypassed.

Output (appended per site, so a stopped run resumes): data/raw/contact-research/website_contacts_<date>.jsonl with
the pages fetched (URL, status, kind, SHA-256) and the extracted emails, phones, social pages, postal addresses and
named people with roles. Page text itself is not kept.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from urllib.parse import urljoin, urlsplit

import contact_lib as C

W = C.W
DATABASES = {"master": C.ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite",
             "welfare": C.ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"}
_write_lock = threading.Lock()


def targets() -> dict:
    out = {}
    for label, path in DATABASES.items():
        con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
        for oid, name, website in con.execute("SELECT organisation_id, name, website FROM organisations"):
            site = str(website or "").strip().split()[0] if str(website or "").strip() else ""
            if not site:
                continue
            url = site if "://" in site else "http://" + site
            domain = W.own_domain(url)
            if not domain or "." not in domain or any(s in domain for s in C.SOCIAL_HOSTS) or domain.endswith(".go.tz"):
                continue
            rec = out.setdefault(domain, {"domain": domain, "start_url": url, "orgs": []})
            rec["orgs"].append({"db": label, "organisation_id": oid, "name": name})
        con.close()
    return out


def page_ok(result: dict) -> bool:
    return result.get("status") == 200 and "html" in str(result.get("content_type") or "html").lower() and bool(result.get("body"))


def crawl(rec: dict) -> dict:
    start = rec["start_url"]
    parts = urlsplit(start)
    out = {**rec, "fetched_on": date.today().isoformat(), "robots": "allowed", "pages": [], "emails": {}, "phones": {}, "socials": {},
           "postal": [], "people": [], "errors": []}
    robots = C.robots_for(f"{parts.scheme}://{parts.netloc}/")
    if not C.allowed(robots, start):
        out["robots"] = "disallowed"
        return out
    home = C.fetch(start, retries=1)
    if not page_ok(home):
        alternative = start.replace("http://", "https://", 1) if start.startswith("http://") else start.replace("https://", "http://", 1)
        if C.allowed(robots, alternative):
            second = C.fetch(alternative, retries=1)
            if page_ok(second):
                home = second
    queue = [(home, "home")]
    visited = {home["final_url"]}
    if page_ok(home):
        final_host = W.own_domain(home["final_url"])
        if final_host and any(s in final_host for s in C.SOCIAL_HOSTS):
            out["errors"].append(f"home page redirects to a shared host ({final_host})")
            queue = []
        else:
            first = C.extract(home["final_url"], home["body"])
            for link in C.rank_links(home["final_url"], first["links"])[: C.MAX_PAGES - 1]:
                if link not in visited and C.allowed(robots, link):
                    visited.add(link)
                    queue.append((C.fetch(link, retries=1), None))
    else:
        out["errors"].append(f"home page not readable: {home.get('error') or home.get('status')}")
        queue = [(home, "home")]
    for result, kind in queue:
        entry = {"url": result["url"], "final_url": result["final_url"], "status": result["status"], "error": result.get("error", ""),
                 "sha256": hashlib.sha256(result.get("body") or b"").hexdigest() if result.get("body") else ""}
        if not page_ok(result):
            out["pages"].append({**entry, "kind": kind or "unreadable"})
            continue
        ex = C.extract(result["final_url"], result["body"])
        entry["kind"] = kind or C.page_kind(result["final_url"], ex.get("title", ""))
        entry["title"] = ex.get("title", "")
        if ex.get("spam"):
            # A hijacked page (gambling or parked content): nothing on it speaks for the organisation.
            out["pages"].append({**entry, "kind": "spam"})
            out["errors"].append(f"{result['final_url']}: spam or hijacked content, not used")
            continue
        out["pages"].append(entry)
        for email, context in ex["emails"].items():
            out["emails"].setdefault(email, {"pages": [], "context": context})["pages"].append(result["final_url"])
        for phone, context in ex["phones"].items():
            out["phones"].setdefault(phone, {"pages": [], "context": context})["pages"].append(result["final_url"])
        for platform, link in ex["socials"].items():
            out["socials"].setdefault(platform, link)
        out["postal"] = sorted(set(out["postal"]) | set(ex["postal"]))[:6]
        for person in ex["people"]:
            if not any(p["name"].lower() == person["name"].lower() and p["role"].lower() == person["role"].lower() for p in out["people"]):
                risk, reason = C.person_risk(person)
                out["people"].append({**person, "page": result["final_url"], "page_kind": entry["kind"], "pdpa_risk": risk, "pdpa_risk_reason": reason})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--workers", type=int, default=8, help="sites crawled in parallel (each site is still one request at a time)")
    parser.add_argument("--limit", type=int, default=0, help="crawl only this many sites (testing)")
    args = parser.parse_args()
    C.RAW.mkdir(parents=True, exist_ok=True)
    out_path = C.RAW / f"website_contacts_{args.date}.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(line)["domain"] for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    todo = [rec for domain, rec in sorted(targets().items()) if domain not in done]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(done)} sites already crawled; {len(todo)} to crawl with {args.workers} workers", flush=True)
    finished = 0
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 12))) as pool:
        futures = {pool.submit(crawl, rec): rec["domain"] for rec in todo}
        for future in as_completed(futures):
            domain = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001 - record and continue with the other sites
                result = {**next(r for r in todo if r["domain"] == domain), "errors": [f"crawler error: {exc!r}"[:200]], "pages": [],
                          "emails": {}, "phones": {}, "socials": {}, "postal": [], "people": [], "robots": "unknown"}
            with _write_lock, open(out_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            finished += 1
            if finished % 25 == 0:
                print(f"{finished}/{len(todo)} sites", flush=True)
    print(f"done: {out_path.relative_to(C.ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
