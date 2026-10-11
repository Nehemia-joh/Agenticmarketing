#!/usr/bin/env python3
"""Turn a round of the coordinator's Google Maps lookups into contact-research records and map-match lines (read-only on the master).

Input: data/raw/gap-census/google_maps_enrich_<date><round>.jsonl, one row per master lead the coordinator looked up in the browser
(organisation_id, organisation_name, verdict accept | review | reject, listing_name, category, latitude, longitude, address, phone,
phone_note, website, website_note, source_url, fetched_on, note, and from round c km_from_census_point).

Only accept rows are used; review rows are hints for a person and reject rows are a different place. For each accept row:
- data/raw/contact-research/browser_googlemaps_<round>_<date>.jsonl gets one browser-method record in the research format
  (docs/methodology/contact-research.md): the listing as its source (title '<listing> - Google Maps', the place URL, the date),
  the listing's phone as an office phone, its website, and a street address only where the listing gives more than a plus code and
  a place or ward name (a road, street, plot, block, house number or building; decided 2026-10-11). A listing phone or website the
  coordinator noted as someone else's (phone_note, website_note) is not used. A row with none of these is kept as 'not_found' with
  the listing as its source.
- data/raw/gap-census/osm_matches_<date><round>.jsonl gets a line for a lead still labelled 'Raw OSM' whose listing publishes a phone
  or website (the same rule as rounds 1 and 2), for scripts/master/add_gap_census_leads.py --matches.
Stored coordinates are never touched; accept rows whose pin lies more than --far km from the lead's stored point are reported.
Then: scripts/contacts/build_contact_profiles.py --date <date>, scripts/master/screen_profile_people.py --apply,
scripts/contacts/merge_master_contacts.py (preflight) and --apply, add_gap_census_leads.py --matches ... --apply, and the drafts,
recipients, tracks, reach tiers, workbook and verify_master.py.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
PLUS_CODE = re.compile(r"\b[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3}\b", re.I)
STREET = re.compile(r"\b(road|rd|street|st|avenue|ave|drive|lane|highway|plot|block|house|building|bldg|complex|plaza|tower|centre|center|"
                    r"p\.?\s?o\.?\s?box)\b|\b\d{1,5}\b", re.I)


def hav(a, b, c, d) -> float:
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin(math.radians(c - a) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def street_address(address: str) -> str:
    """The listing's address when it names more than a plus code and a place or ward (a road, plot, block, number or building)."""
    rest = PLUS_CODE.sub(" ", address or "")
    rest = re.sub(r"\b(1\d{4}|2\d{4})\b", " ", rest)  # a postcode alone is not a street
    return address.strip() if STREET.search(rest) else ""


def phone_of(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""
    return "+" + re.sub(r"\s+", " ", value.strip().lstrip("+")) if digits.startswith("255") else value.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", type=Path, required=True, help="data/raw/gap-census/google_maps_enrich_<date><round>.jsonl")
    parser.add_argument("--round", required=True, help="the round's letter, used in the output names (b, c, ...)")
    parser.add_argument("--date", default="2026-10-11")
    parser.add_argument("--far", type=float, default=1.0, help="report accept rows whose pin is more than this many km from the stored point")
    parser.add_argument("--write", action="store_true", help="write the two output files (default: preview)")
    args = parser.parse_args()
    path = args.file if args.file.is_absolute() else ROOT / args.file
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    con = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    records, matches, far, problems, counts = [], [], [], [], {"accept": 0, "address": 0, "phone": 0, "website": 0, "nothing": 0}
    for i, r in enumerate(rows, 1):
        if r.get("verdict") != "accept":
            continue
        counts["accept"] += 1
        o = con.execute("SELECT name, verification, latitude, longitude FROM organisations WHERE organisation_id=?", (r["organisation_id"],)).fetchone()
        if o is None or o["name"] != r["organisation_name"]:
            problems.append(f"line {i}: {r['organisation_name']} ({r['organisation_id']}) is not this master record")
            continue
        url, listing = r["source_url"], r["listing_name"]
        phone = "" if r.get("phone_note") else phone_of(r.get("phone", ""))
        website = "" if r.get("website_note") else (r.get("website") or "").strip()
        address = street_address(r.get("address", ""))
        excerpt = "; ".join(x for x in (listing, r.get("category", ""), r.get("address", ""), (r.get("phone") or "").strip(), website) if x)
        facts = [k for k, v in (("address", address), ("phone", phone), ("website", website)) if v] or ["listing"]
        for k in ("address", "phone", "website"):
            counts[k] += k in facts
        counts["nothing"] += facts == ["listing"]
        note = (f"Google Maps listing (coordinator's lookup in the browser, {r['fetched_on']}; {path.name}). Listed as '{listing}' "
                f"({r.get('category', '')}).") + (f" {r['note']}" if r.get("note") else "")
        if r.get("address") and not address:
            note += " The listing's address gives only a plus code or a place name, so no street address is recorded."
        records.append({
            "db": "master", "organisation_id": r["organisation_id"], "organisation_name": r["organisation_name"],
            "status": "partial" if facts != ["listing"] else "not_found", "identity": "confirmed", "method": "browser", "robots": "allowed",
            "searches_used": 0, "website": website, "emails": [],
            "phones": [{"value": phone, "type": "office (Google Maps listing)", "source_url": url, "fetched": True, "excerpt": excerpt}] if phone else [],
            "postal_address": None, "physical_address": {"value": address, "source_url": url, "fetched": True, "excerpt": excerpt} if address else None,
            "socials": [], "people": [],
            "sources": [{"url": url, "title": f"{listing} - Google Maps", "fetched": True, "accessed_on": r["fetched_on"], "excerpt": excerpt, "facts": facts}],
            "pages_read": [url], "notes": note})
        if str(o["verification"] or "").startswith("Raw OSM") and (phone or website):
            matches.append({"organisation_id": r["organisation_id"], "organisation_name": r["organisation_name"],
                            "basis": f"Google Maps listing '{listing}' ({r.get('category', '')}) with a published phone or website",
                            "source_url": url, "accessed_on": r["fetched_on"], "excerpt": excerpt})
        try:
            km = hav(float(o["latitude"]), float(o["longitude"]), float(r["latitude"]), float(r["longitude"]))
            if km > args.far:
                far.append({"line": i, "organisation_id": r["organisation_id"], "name": r["organisation_name"], "listing": listing,
                            "km_from_stored_point": round(km, 1), "km_from_census_point": r.get("km_from_census_point")})
        except (TypeError, ValueError):
            far.append({"line": i, "organisation_id": r["organisation_id"], "name": r["organisation_name"], "listing": listing,
                        "km_from_stored_point": None, "note": "no stored point (not filled here)"})
    out_records = ROOT / "data" / "raw" / "contact-research" / f"browser_googlemaps_{args.round}_{args.date}.jsonl"
    out_matches = ROOT / "data" / "raw" / "gap-census" / f"osm_matches_{args.date}{args.round}.jsonl"
    report = {"file": path.relative_to(ROOT).as_posix(), "rows": len(rows), **counts, "records": len(records), "matches": len(matches),
              "problems": problems, "far_from_stored_point": far}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(report, indent=1, ensure_ascii=False))
    if problems:
        print("Refused: fix the rows above first.")
        return 1
    if args.write:
        for target, items in ((out_records, records), (out_matches, matches)):
            with target.open("w", encoding="utf-8", newline="\n") as fh:
                for item in items:
                    fh.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Wrote {out_records.relative_to(ROOT).as_posix()} ({len(records)}) and {out_matches.relative_to(ROOT).as_posix()} ({len(matches)}).")
    else:
        print("Preview only; --write writes the two files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
