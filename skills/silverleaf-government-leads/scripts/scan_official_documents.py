#!/usr/bin/env python3
"""Fetch the official documents a council or regional site lists, and find the office contacts and post holders in them.

The council-site captures (collect_council_sites.py) list each site's documents (/api/files) and page attachments, but
read the text only of the councillor, ward and contact pages. Strategic plans, client service charters, investment
profiles and newsletters often print office addresses (S.L.P / P.O. Box), phones and emails, and name post holders.

This script takes the documents whose names match DOC_PATTERN (or every PDF with --all), fetches each one politely
(gov_lib host limits: one request at a time, 1.5 s apart, retries, the refresh's on-disk cache), extracts the text page
by page with pypdf, and writes, to runtime/government/<run-id>/documents-<date>.json (never committed):
- per document: URL, host, name, SHA-256, pages, and whether the text layer is empty (scanned: needs transcription);
- hits: every line that names a post office box, an official phone or email, a District Commissioner's or
  Administrative Secretary's office, or a ward, village or mtaa executive officer, with its page and line number.

A person reads the hits and records what holds up, with the page locator, in data/raw/government-research/
(office_contacts_<date>.json for office routes, post_holders_*.json for named holders). Nothing here is used by the
build directly, and no document text is committed. Usage:
    python scripts/government/scan_official_documents.py --run-id <run-id> --date <capture date> [--host h ...] [--all]
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re

import gov_lib as G

W = G.W
DOC_PATTERN = re.compile(r"mkakati|strategic|\bsp\b|charter|huduma kwa wateja|investment|uwekezaji|profile|profaili|jarida|newsletter|"
                         r"magazine|utawala|watendaji|mawasiliano|contact|orodha|directory|muundo|structure", re.I)
SKIP_PATTERN = re.compile(r"mwongozo|guideline|sheria|\bact\b|regulation|policy|sera\b|kanuni|form\b|fomu|mavazi|vision 2050|hotuba", re.I)
HIT_PATTERNS = {
    "po_box": r"\b(?:S\.?\s?L\.?\s?P\.?|P\.?\s?O\.?\s?Box)\s*\.?\s*\d{1,5}",
    "phone": r"(?:\+?255|\b0)[\s-]?(?:2[2-9]|6[1-9]|7[1-9])\d[\s-]?\d{3}[\s-]?\d{3,4}\b",
    "email": r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.go\.tz",
    "district_office": r"mkuu wa wilaya|district commissioner|katibu tawala (?:wa )?wilaya|district administrative secretary|\bDAS\b|\bDC'?s office",
    "executive_officer": r"mtendaji wa (?:kata|kijiji|mtaa)|ward executive|village executive|\bWEO\b|\bVEO\b|\bMEO\b",
    "department_head": r"afisa elimu|mkuu wa (?:idara|divisheni)|maendeleo ya jamii|ustawi wa jamii|community development|social welfare|education officer",
}
HIT_RES = {k: re.compile(v, re.I) for k, v in HIT_PATTERNS.items()}


def candidates(sites: dict, take_all: bool) -> list[dict]:
    out, seen = [], set()
    for host, site in sorted(sites.items()):
        docs = [{"name": f.get("name") or "", "url": f.get("url") or "", "source": "files", "date": str(f.get("date") or "")[:10]}
                for f in site.get("files") or []]
        for page in site.get("pages") or []:
            for a in page.get("attachments") or []:
                if not a.get("text"):
                    docs.append({"name": a.get("file_name") or "", "url": a.get("url") or "", "source": f"page {page['slug']}", "date": ""})
        for d in docs:
            name = d["name"]
            if not d["url"] or d["url"] in seen or not re.search(r"\.pdf$", d["url"].split("?")[0], re.I):
                continue
            if not take_all and (SKIP_PATTERN.search(name) or not DOC_PATTERN.search(name)):
                continue
            seen.add(d["url"])
            out.append({"host": host, **d})
    return out


def scan(doc: dict, cache) -> dict:
    record = dict(doc)
    try:
        body = W.polite_request(doc["url"], cache_dir=cache, retries=2, backoff=5.0)
    except Exception as exc:  # noqa: BLE001 - record the failure and move on (never retry in a loop)
        record.update(status="fetch_failed", error=repr(exc)[:200], hits=[])
        return record
    record.update(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(body))
        pages = [(p.extract_text() or "") for p in reader.pages]
    except Exception as exc:  # noqa: BLE001
        record.update(status="parse_failed", error=repr(exc)[:200], hits=[])
        return record
    chars = sum(len(p.strip()) for p in pages)
    # fewer than about 30 characters a page means the pages are images: a person transcribes them (transcriptions/README.md)
    record.update(pages=len(pages), text_chars=chars, status="text_extracted" if chars >= 30 * max(1, len(pages)) else "scanned_needs_transcription")
    hits = []
    for page_no, text in enumerate(pages, 1):
        for line_no, line in enumerate(text.splitlines(), 1):
            line = " ".join(line.split())
            kinds = [k for k, rx in HIT_RES.items() if rx.search(line)]
            if kinds:
                hits.append({"page": page_no, "line": line_no, "kinds": kinds, "text": line[:300]})
    record["hits"] = hits
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--date", required=True, help="the capture date whose council-site files to read (and whose cache to use)")
    parser.add_argument("--host", action="append", help="limit to these hosts (repeatable)")
    parser.add_argument("--all", action="store_true", help="scan every listed PDF, not only those whose names suggest contacts")
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    cache = cfg["paths"]["cache"] if args.date == cfg["research_date"] else cfg["paths"]["work"] / f"http-cache-{args.date}"
    sites = {}
    for path in sorted((cfg["paths"]["raw"] / "council_sites").glob(f"*_{args.date}.json")):
        site = json.loads(path.read_text(encoding="utf-8"))
        if not args.host or site["host"] in args.host:
            sites[site["host"]] = site
    docs = candidates(sites, args.all)
    results = []
    for doc in docs:
        result = scan(doc, cache)
        results.append(result)
        print(f"{doc['host']}: {doc['name'][:70]}: {result['status']}, pages {result.get('pages', 0)}, hits {len(result['hits'])}", flush=True)
    out = cfg["paths"]["work"] / f"documents-{args.date}.json"
    out.write_text(json.dumps({"run_id": args.run_id, "capture_date": args.date, "documents": results}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out.relative_to(G.ROOT)}: {len(results)} documents, {sum(len(r['hits']) for r in results)} hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
