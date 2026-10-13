#!/usr/bin/env python3
"""Turn one Google Maps lookup round into its lookup record, geocode fills and geocode corrections, with the shared-pin check.

A round is the coordinator's browser lookups for a slice of the worklist (collect_geocodes.py worklist, or
runtime/geocode/gmaps_worklist_<date>.jsonl). Only the coordinator looks up, in its own browser pane, and the pane must be
visible: Google Maps does not finish rendering results in a hidden pane, and the extractor then records nothing.

  python scripts/maps/build_gmaps_round.py --date 2026-10-13 --tag c \
      --rows <rows.json|.jsonl> --results <results.json> --notes <notes.txt> --db <master.sqlite> [--no-pin-check] [--out-root <dir>]
  python scripts/maps/build_gmaps_round.py --audit data/raw/gap-census/google_maps_enrich_<d><tag>.jsonl ...   # check only, writes nothing

Inputs:
- --rows: the round's worklist rows (a JSON array, or JSON lines), each with id, name, segment and query. Only rows with a
  verdict note are built; every note must name a row.
- --results: the browser results, {organisation_id: [listing, ...]} with the top listing first. Each listing is
  {n: name, la: latitude, lo: longitude, c: category, a: address, i: listing id or blank, w: website, p: phone, u: Maps URL}.
  This is the export of localStorage.slres from the browser extractor (below).
- --notes: one verdict per line: 'A <id>' accept, 'R <id>[|note]' reject, 'V <id>|note' review, 'O <id>|note' accept as
  outside the catchment (the note is the basis). A reject without a note gets "Top listing '<n>' is not this organisation."
- --db: the master as it was before the round (the pre-round backup), read-only. A lead with no stored point gets a fill; a
  lead with a stored point gets a correction carrying the old point, its precision and source, and km_moved.

Outputs (the formats of the 13 October 2026 rounds), under --out-root (default: the repository):
- data/raw/gap-census/google_maps_enrich_<date><tag>.jsonl                one line per lead: verdict, top listing, note;
- data/raw/geocode-research/geocodes_gmaps_<date><tag>.jsonl             the fills (accepted, no stored point; or 'O');
- data/raw/geocode-research/geocodes_corrections_gmaps_<date><tag>.jsonl the replacements (old_* fields, km_moved);
- runtime/geocode/gmaps_round_<date><tag>_check.json                     the shared-pin check's report.
Then: ledger.py ingest the enrich file, apply_geocodes.py (preview, then --apply; --replace for the corrections file).

The shared-pin check (default; docs/methodology/research-playbook.md, "Google Maps traps"):
- Every listing of this round and of every other google_maps_enrich_*.jsonl file is grouped by its point rounded to 4 decimals.
- An accepted listing whose point is shared with a differently named listing, and which has no street address (empty, a plus
  code, or only Arusha, Tanzania, a postcode or a ward or place name), is downgraded to review with the reason.
- Two listings that share a point and both have a street address are likely one building: kept, and reported.
- An accepted listing on a known default pin (the playbook's list, Tanzania's country centre included), or within 60 m of one,
  is downgraded to review.
- Rows with an 'O' verdict (accepted as outside the catchment) are not checked.
Every downgrade is printed and written to the check report. When a person has looked at a flagged listing and keeps it (the
listing is the lead's own, and the stray listing is the other one), pass --keep <id>: it stays accepted and the report says so.

The browser extractor. Two functions kept in the browser's localStorage, run on a Maps search page with
eval(localStorage.slfn)("<organisation_id>") (read the results now) or eval(localStorage.slsync)("<organisation_id>") (wait
for the result list to settle, then read). Each reads the result list, or the single place panel when Maps opens one, and
stores the listings under the ID in localStorage.slres as JSON: {"<id>": [{n, la, lo, c, a, i, w, p, u}, ...]}, top first;
la and lo come from the listing URL's !3d<lat>!4d<lon>. Export with JSON.stringify(JSON.parse(localStorage.slres)) and save it
as the --results file. Each lookup is a navigate to https://www.google.com/maps/search/<query>/@<lat>,<lon>,11z?hl=en (the
area's centre: -3.37,36.69 for Arusha, -3.33,37.20 for Moshi and Hai), a few seconds' wait, then the call. Lookups run signed
out; never pass a bot check or sign in on the user's behalf.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENRICH_DIR = ROOT / "data" / "raw" / "gap-census"
GEO_DIR = ROOT / "data" / "raw" / "geocode-research"
VERDICTS = {"A": "accept", "O": "accept", "V": "review", "R": "reject"}
# Known default pins (docs/methodology/research-playbook.md, "Google Maps traps"), and Tanzania's country centre.
DEFAULT_PINS = [("JM7M+65, central Arusha", -3.38689, 36.68296), ("the Namanga road point", -3.35877, 36.66606),
                ("the Sokoine road point", -3.39814, 36.67721), ("the Ngorongoro point", -3.36392, 35.38430),
                ("Tanzania's country centre", -6.37283, 34.98990)]
DEFAULT_RADIUS_KM = 0.06
PLUS_CODE = re.compile(r"\b[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3}\b", re.I)
PLACE_ONLY = re.compile(r"^(arusha|tanzania|united republic of tanzania|moshi|kilimanjaro|usa river|arumeru|meru|\d{4,6})$", re.I)
STREET = re.compile(r"\b(road|rd|street|st|avenue|ave|highway|hwy|lane|drive|way|house|building|bldg|complex|plaza|tower|floor|room|"
                    r"cent(?:re|er)|mall|block|plot|hotel|lodge|opposite|opp|near|along|junction|market|barabara|mtaa)\b", re.I)


def km(a, b, c, d) -> float:
    a, b, c, d = map(math.radians, (a, b, c, d))
    h = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return round(2 * 6371 * math.asin(math.sqrt(h)), 1)


def name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def street_address(address: str) -> bool:
    """A real street address: something beyond a plus code, a postcode and place names (a ward or town alone does not count)."""
    text = PLUS_CODE.sub(" ", address or "")
    parts = [p.strip(" .") for p in text.split(",") if p.strip(" .")]
    parts = [p for p in parts if not PLACE_ONLY.match(p)]
    return any(STREET.search(p) or re.search(r"\d", p) for p in parts)


def read_rows(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    return json.loads(text)


def read_notes(path: Path) -> dict:
    notes = {}
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        code, _, rest = line.partition(" ")
        oid, _, note = rest.partition("|")
        if code not in VERDICTS or not oid.strip():
            raise SystemExit(f"{path.name} line {n}: expected 'A <id>', 'R <id>[|note]', 'V <id>|note' or 'O <id>|note'")
        if code in ("V", "O") and not note.strip():
            raise SystemExit(f"{path.name} line {n}: a '{code}' verdict needs a note")
        if oid.strip() in notes:
            raise SystemExit(f"{path.name} line {n}: {oid.strip()} has two verdicts")
        notes[oid.strip()] = (code, note)
    return notes


def load_geocodes():
    spec = importlib.util.spec_from_file_location("apply_geocodes", ROOT / "scripts" / "master" / "apply_geocodes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------ the shared-pin check
def other_listings(exclude: set[Path]) -> list[dict]:
    out = []
    for path in sorted(ENRICH_DIR.glob("google_maps_enrich_*.jsonl")):
        if path.resolve() in exclude:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                r["_file"] = path.name
                out.append(r)
    return out


def pin_check(round_rows: list[dict], others: list[dict], label: str, keep=frozenset()) -> dict:
    """Downgrades (in place) accepted rows on a shared or default point without a street address; returns the report.
    IDs in keep were reviewed by a person and stay accepted; the report lists them with the reason they were flagged."""
    by_point = defaultdict(list)
    for r in round_rows + others:
        if r.get("latitude") is None or r.get("longitude") is None or not r.get("listing_name"):
            continue
        by_point[(round(float(r["latitude"]), 4), round(float(r["longitude"]), 4))].append(r)
    downgrades, buildings, kept = [], [], []
    for r in round_rows:
        if r["verdict"] != "accept" or r.get("latitude") is None:
            continue
        lat, lon = float(r["latitude"]), float(r["longitude"])
        point = (round(lat, 4), round(lon, 4))
        default = next(((name, la, lo) for name, la, lo in DEFAULT_PINS if km(lat, lon, la, lo) <= DEFAULT_RADIUS_KM), None)
        if default:
            reason = (f"'{r['listing_name']}' sits on the known default pin {default[0]} ({default[1]:.4f}, {default[2]:.4f}): "
                      "not an office point.")
        else:
            shared = [o for o in by_point[point] if o is not r and name_key(o["listing_name"]) != name_key(r["listing_name"])]
            if not shared:
                continue
            names = list(dict.fromkeys(o["listing_name"] for o in shared))
            if street_address(r.get("address")):
                pairs = [o for o in shared if street_address(o.get("address"))]
                if pairs:
                    buildings.append({"organisation_id": r["organisation_id"], "listing": r["listing_name"], "address": r.get("address", ""),
                                      "shares_point_with": [{"listing": o["listing_name"], "address": o.get("address", ""),
                                                             "file": o.get("_file", label)} for o in pairs], "point": list(point)})
                continue
            reason = (f"Listing sits on a point shared with an unrelated listing ('{names[0]}') and has no street address: "
                      "not a specific office point.")
        item = {"organisation_id": r["organisation_id"], "organisation_name": r["organisation_name"],
                "listing": r["listing_name"], "point": list(point), "address": r.get("address", ""), "reason": reason}
        if r["organisation_id"] in keep:
            kept.append(item)
            continue
        downgrades.append(item)
        r["verdict"], r["note"] = "review", reason
    return {"round": label, "downgraded": downgrades, "kept_as_one_building": buildings, "kept_by_reviewer": kept}


# ------------------------------------------------------------------ build
def build(args) -> int:
    rows_all = read_rows(args.rows)
    rows = {r["id"]: r for r in rows_all}
    results = json.loads(args.results.read_text(encoding="utf-8"))
    notes = read_notes(args.notes)
    missing = sorted(set(notes) - set(rows))
    if missing:
        raise SystemExit(f"{len(missing)} noted IDs are not in the rows file: {missing[:5]}")
    unnoted = [oid for oid in rows if oid not in notes]
    label = f"{args.date}{args.tag}"
    root = args.out_root
    enrich_path = root / "data" / "raw" / "gap-census" / f"google_maps_enrich_{label}.jsonl"
    fills_path = root / "data" / "raw" / "geocode-research" / f"geocodes_gmaps_{label}.jsonl"
    corr_path = root / "data" / "raw" / "geocode-research" / f"geocodes_corrections_gmaps_{label}.jsonl"
    check_path = root / "runtime" / "geocode" / f"gmaps_round_{label}_check.json"

    enrich, codes = [], {}
    for oid, row in rows.items():
        if oid not in notes:
            continue
        code, note = notes[oid]
        top = (results.get(oid) or [{}])[0]
        verdict = VERDICTS[code]
        if code == "R" and not note:
            note = f"Top listing '{top.get('n')}' is not this organisation."
        codes[oid] = code
        enrich.append({"organisation_id": oid, "organisation_name": row["name"], "kind": row.get("segment", ""), "verdict": verdict,
                       "listing_name": top.get("n") or "", "latitude": top.get("la"), "longitude": top.get("lo"), "category": top.get("c") or "",
                       "address": top.get("a") or "", "phone": top.get("p") or "", "phone_note": "", "website": top.get("w") or "",
                       "website_note": "", "source_type": "Google Maps listing", "source_url": top.get("u") or "", "fetched_on": args.date,
                       "query": row["query"], "note": note})

    report = {"round": label, "downgraded": [], "kept_as_one_building": [], "kept_by_reviewer": []}
    if not args.no_pin_check:
        exclude = {(ENRICH_DIR / enrich_path.name).resolve(), enrich_path.resolve()}
        report = pin_check([e for e in enrich if codes[e["organisation_id"]] != "O"], other_listings(exclude), label, set(args.keep))

    gc = load_geocodes()
    con = sqlite3.connect(f"file:{args.db.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    fills, corr = [], []
    for e in enrich:
        oid, code = e["organisation_id"], codes[e["organisation_id"]]
        if e["verdict"] != "accept" or e["latitude"] is None:
            continue
        top, row = (results.get(oid) or [{}])[0], rows[oid]
        o = con.execute("SELECT * FROM organisations WHERE organisation_id=?", (oid,)).fetchone()
        if o is None:
            raise SystemExit(f"{oid} is not in {args.db}")
        addr = top.get("a") or ""
        note = notes[oid][1]
        line = {"db": "master", "organisation_id": oid, "organisation_name": o["name"], "key": "",
                "status": "outside_confirmed" if code == "O" else "placed", "latitude": top["la"], "longitude": top["lo"], "precision": "point",
                "source_type": "Google Maps listing", "source_url": top["u"], "fetched_on": args.date,
                "as_found": f"Google Maps listing '{top['n']}' at {top['la']}, {top['lo']}" + (f"; {addr}" if addr else ""),
                "basis": note or f"Google Maps listing named '{top['n']}' for the search '{row['query']}': same organisation, in the record's area.",
                "geocode_source": f"Google Maps: {top['u']}", "confidence": "high"}
        try:
            stored = (float(o["latitude"]), float(o["longitude"]))
        except (TypeError, ValueError):
            stored = None
        if stored is None or code == "O":
            fills.append(line)
        else:
            src = gc.stored_source(con, o)
            corr.append({**line, "replace": True, "old_latitude": stored[0], "old_longitude": stored[1], "old_precision": o["geocode_precision"] or "",
                         "old_location_source": src if src is not None else gc.NO_SOURCE,
                         "km_moved": km(stored[0], stored[1], top["la"], top["lo"])})
    con.close()

    def write(path: Path, lines: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in lines), encoding="utf-8", newline="\n")

    write(enrich_path, enrich)
    write(fills_path, fills)
    write(corr_path, corr)
    check_path.parent.mkdir(parents=True, exist_ok=True)
    check_path.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{label}: verdicts {dict(Counter(e['verdict'] for e in enrich))}; fills {len(fills)}; corrections {len(corr)}"
          + (f"; {len(unnoted)} rows without a verdict were left out" if unnoted else ""))
    print_report(report)
    print("\n".join(str(p) for p in (enrich_path, fills_path, corr_path, check_path)))
    return 0


def print_report(report: dict) -> None:
    if not report["downgraded"]:
        print(f"shared-pin check ({report['round']}): no accepted listing downgraded")
    for d in report["downgraded"]:
        print(f"DOWNGRADED to review ({report['round']}): {d['organisation_name']} ({d['organisation_id']}), listing '{d['listing']}' "
              f"at {d['point'][0]}, {d['point'][1]}: {d['reason']}")
    for k in report.get("kept_by_reviewer", []):
        print(f"kept by reviewer (--keep) ({report['round']}): {k['organisation_name']} ({k['organisation_id']}): flagged as: {k['reason']}")
    for b in report["kept_as_one_building"]:
        others = "; ".join(f"'{o['listing']}' ({o['address']}, {o['file']})" for o in b["shares_point_with"])
        print(f"kept, likely one building ({report['round']}): '{b['listing']}' ({b['address']}) shares {b['point'][0]}, {b['point'][1]} with {others}")


def audit(paths: list[Path]) -> int:
    """The shared-pin check on committed round files, against every other round file; writes nothing. Exit 1 on a downgrade."""
    found = 0
    for path in paths:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [r for r in rows if not (r["verdict"] == "accept" and "outside" in (r.get("note") or "").lower())]
        exclude = {path.resolve(), (ENRICH_DIR / path.name).resolve()}
        report = pin_check(rows, other_listings(exclude), path.name)
        print_report(report)
        found += len(report["downgraded"])
    return 1 if found else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", nargs="+", type=Path, help="run only the shared-pin check on these enrich files")
    parser.add_argument("--date", help="the lookup date, YYYY-MM-DD (fetched_on and the file names)")
    parser.add_argument("--tag", default="", help="the round letter (a, b, c ...)")
    parser.add_argument("--rows", type=Path)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--db", type=Path, help="the master before the round (read-only)")
    parser.add_argument("--no-pin-check", action="store_true", help="skip the shared-pin check (not recommended)")
    parser.add_argument("--keep", nargs="+", default=[], metavar="ID",
                        help="organisation IDs a person reviewed after the check flagged them: they stay accepted (listed in the report)")
    parser.add_argument("--out-root", type=Path, default=ROOT, help="write under this folder instead of the repository (for a trial)")
    args = parser.parse_args()
    if args.audit:
        return audit(args.audit)
    for need in ("date", "rows", "results", "notes", "db"):
        if not getattr(args, need):
            parser.error(f"--{need} is required")
    return build(args)


if __name__ == "__main__":
    sys.exit(main())
