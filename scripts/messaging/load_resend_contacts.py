#!/usr/bin/env python3
"""Load the Resend contact-import files (export_resend_contacts.py) into Resend through its API.

Each row becomes a contact (email, first_name, last_name, the custom properties) in the segment named for its file:
  companies-high.csv -> "Companies - High", companies-high-direct.csv -> "Companies - High - Direct",
  companies-high-indirect.csv -> "Companies - High - Indirect", welfare-medium.csv -> "Welfare - Medium", and so on for the
  companies, introducers, welfare and government tracks (override with --segment). A high contact is loaded into its
  high segment and into one of the two high sub-segments, so load both files.
A contact that already exists is updated and added to the segment, so the script can be re-run after a promotion.
The custom properties must already exist in Resend (all strings).

The API key is read from the RESEND_API_KEY environment variable or from --key-file (default: ~/.resend-key); it is never
printed. Use a key you revoke afterwards. Preview by default; --apply calls the API. Nothing is sent: this only loads contacts.
Writes a log of every call's outcome (no key) to runtime/resend/<date>/load-log.jsonl.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = "https://api.resend.com"
PROPERTIES = ["organisation", "track", "audience", "confidence", "high_route", "confidence_reason", "priority", "variant", "recipient",
              "escalation_recipient", "escalation_email", "message_subject", "message_body", "message_html", "plan_id"]
SEGMENT_FILE = re.compile(r"^(companies|introducers|welfare|government)-(high|medium|low)(?:-(direct|indirect))?$")


def segment_for(stem: str) -> str:
    """'companies-high-direct' -> 'Companies - High - Direct'; '' for a file that is not a Resend segment (such as government-delivery-*)."""
    m = SEGMENT_FILE.match(stem)
    return " - ".join(part.capitalize() for part in m.groups() if part) if m else ""


def read_key(path: Path) -> str:
    key = os.environ.get("RESEND_API_KEY", "").strip()
    if not key and path.exists():
        key = path.read_text(encoding="utf-8").strip()
    if not key.startswith("re_"):
        raise SystemExit(f"No Resend API key found in RESEND_API_KEY or {path}.")
    return key


def call(key: str, method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    """One API call with retries on rate limits; returns (status, json)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    for attempt in range(5):
        req = urllib.request.Request(API + path, data=data, method=method, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "silverleaf-contact-loader/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as err:
            payload = json.loads(err.read() or b"{}") if err.headers.get("Content-Type", "").startswith("application/json") else {}
            if err.code == 429 and attempt < 4:
                time.sleep(1.5 * (attempt + 1))
                continue
            return err.code, payload
    return 429, {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path, help="CSV files from export_resend_contacts.py")
    parser.add_argument("--segment", help="segment name for every file (default: by file name)")
    parser.add_argument("--key-file", type=Path, default=Path.home() / ".resend-key")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--pause", type=float, default=0.6, help="seconds between calls (Resend's default limit is about 2 a second)")
    args = parser.parse_args()

    jobs = []
    for path in args.files:
        name = args.segment or segment_for(path.stem)
        if not name:
            raise SystemExit(f"{path.name}: no segment for this file; pass --segment.")
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        # Inferred candidates (email_formats.py) are never loaded: a person confirms each address first (rule of 11 October 2026).
        if path.stem.endswith("-low-inferred") or any(r.get("inferred_label") for r in rows):
            raise SystemExit(f"{path.name}: inferred from format, unverified; never loaded. Confirm each address by phone or the "
                             "organisation's published route, record it as a route, and re-export.")
        jobs.append((path, name, rows))
        print(f"{path.name}: {len(rows)} contacts -> segment '{name}'")
    if not args.apply:
        print("Preview only; add --apply to load.")
        return 0

    key = read_key(args.key_file)
    status, listing = call(key, "GET", "/segments")
    if status != 200:
        raise SystemExit(f"Could not list segments (HTTP {status}): {listing.get('message', listing)}")
    segment_ids = {s["name"]: s["id"] for s in listing.get("data", [])}
    log_path = ROOT / "runtime" / "resend" / date.today().isoformat() / "load-log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    totals = {"created": 0, "updated": 0, "failed": 0}
    with log_path.open("a", encoding="utf-8") as log:
        for path, name, rows in jobs:
            if name not in segment_ids:
                raise SystemExit(f"Segment '{name}' does not exist in Resend; create it first.")
            seg = segment_ids[name]
            for row in rows:
                props = {k: row.get(k, "") for k in PROPERTIES if row.get(k)}
                body = {"email": row["email"], "first_name": row.get("first_name") or None, "last_name": row.get("last_name") or None,
                        "unsubscribed": False, "properties": props, "segments": [{"id": seg}]}
                body = {k: v for k, v in body.items() if v is not None}
                status, out = call(key, "POST", "/contacts", body)
                outcome = "created" if status in (200, 201) else ""
                if not outcome and "exist" in str(out.get("message", "")).lower():
                    ref = urllib.parse.quote(row["email"], safe="")
                    s1, o1 = call(key, "PATCH", f"/contacts/{ref}", {k: v for k, v in body.items() if k not in ("email", "segments")})
                    time.sleep(args.pause)
                    s2, o2 = call(key, "POST", f"/contacts/{ref}/segments/{seg}")
                    outcome = "updated" if s1 in (200, 201) and s2 in (200, 201, 409) else ""
                    out = {"update": o1, "segment": o2}
                    status = max(s1, s2)
                outcome = outcome or "failed"
                totals[outcome] += 1
                log.write(json.dumps({"file": path.name, "email": row["email"], "segment": name, "outcome": outcome, "status": status,
                                      "message": out.get("message", "") if isinstance(out, dict) else ""}, ensure_ascii=False) + "\n")
                if outcome == "failed":
                    print(f"  failed {row['email']}: HTTP {status} {out.get('message', out) if isinstance(out, dict) else out}")
                time.sleep(args.pause)
            print(f"{path.name}: done")
    print(json.dumps(totals), f"log: {log_path.relative_to(ROOT)}")
    return 0 if not totals["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
