#!/usr/bin/env python3
"""Extract ward populations for the run's councils from the 2022 census administrative-units report (NBS).

Downloads the report once (cached under runtime/government/<run-id>/http-cache/, never committed), finds each
council's ward table ("Population Distribution by Sex, Sex Ratio, Number of Households and Average Household Size
by Ward, <council>; 2022 PHC"), and parses every ward row with its PDF page and printed page as a locator.

Each council's ward rows must add up to the council total printed in the same table (population, male, female and
households), and every ward number must be present in sequence; otherwise the script fails.

Outputs in data/raw/government-research/:
- nbs_2022_wards_<date>.csv: one row per ward
- nbs_2022_councils_<date>.json: council totals, table references, reconciliation results and the report's SHA-256
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re

from pypdf import PdfReader

import gov_lib as G

W = G.W
TITLE = re.compile(r"Size\s+(?:by\s+)?Ward,\s*(.+?)\s*;\s*2022", re.S)
TABLE_NO = re.compile(r"Table\s+(\d+)\.\s*(\d+)")
NUM = r"([\d,]+)"
TOTAL = re.compile(r"(?:Council|City)\s+" + r"\s+".join([NUM] * 3) + r"\s+(\d+)\s+" + NUM + r"\s+([\d.]+)")
ROW = re.compile(r"^\s*(\d+)\.+\s+(.+?)\s+" + r"\s+".join([NUM] * 3) + r"\s+(\d+)\s+" + NUM + r"\s+([\d.]+)\s*$")
QUOTES = re.compile(r"[‘’“”�\"]")


def to_int(value: str) -> int:
    return int(value.replace(",", ""))


def council_name(title: str) -> str:
    name = " ".join(title.split())
    return name + " Council" if name.endswith("City") else name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    census, raw, date = cfg["census"], cfg["paths"]["raw"], cfg["research_date"]
    wanted = set(census["councils"])
    body = W.polite_request(census["report_url"], cache_dir=cfg["paths"]["cache"], retries=2, backoff=10.0)
    report_sha = hashlib.sha256(body).hexdigest()
    reader = PdfReader(io.BytesIO(body))
    tables: dict[str, dict] = {}
    current = None
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        printed = next((line.strip() for line in text.splitlines() if line.strip()), "")
        title = TITLE.search(text)
        body_text = text
        if title:
            name = council_name(title.group(1))
            current = name if name in wanted else None
            if current:
                numbers = list(TABLE_NO.finditer(text[: title.start()]))
                total = TOTAL.search(text, title.end())
                tables[current] = {"council": current, "table": f"Table {numbers[-1].group(1)}.{numbers[-1].group(2)}" if numbers else "",
                                   "pdf_pages": [], "printed_pages": [], "wards": [],
                                   "total": dict(zip(("population", "male", "female", "sex_ratio", "households", "avg_household_size"),
                                                     (to_int(total.group(1)), to_int(total.group(2)), to_int(total.group(3)), int(total.group(4)),
                                                      to_int(total.group(5)), float(total.group(6))))) if total else {}}
                body_text = text[title.end():]  # a region's council table can share the page; read only below the title
        if not current:
            continue
        table = tables[current]
        rows = [m for m in (ROW.match(line) for line in body_text.splitlines()) if m]
        expected = len(table["wards"]) + 1
        added = 0
        for m in rows:
            number = int(m.group(1))
            if number != expected:
                continue
            ward = " ".join(QUOTES.sub("", m.group(2)).split())
            table["wards"].append({"council": current, "ward_no": number, "ward": ward, "population": to_int(m.group(3)),
                                   "male": to_int(m.group(4)), "female": to_int(m.group(5)), "sex_ratio": int(m.group(6)),
                                   "households": to_int(m.group(7)), "avg_household_size": float(m.group(8)),
                                   "pdf_page": index, "printed_page": printed})
            expected += 1
            added += 1
        if added:
            table["pdf_pages"].append(index)
            table["printed_pages"].append(printed)
        elif not title:
            current = None  # a page without this council's rows ends its table
    missing = sorted(wanted - tables.keys())
    checks, failed = {}, []
    for name, table in sorted(tables.items()):
        sums = {k: sum(w[k] for w in table["wards"]) for k in ("population", "male", "female", "households")}
        ok = bool(table["total"]) and all(sums[k] == table["total"].get(k) for k in sums)
        checks[name] = {"wards": len(table["wards"]), "sum_of_wards": sums, "council_total": table["total"], "reconciles": ok}
        if not ok:
            failed.append(name)
    out_csv = raw / f"nbs_2022_wards_{date}.csv"
    fields = ["council", "ward_no", "ward", "population", "male", "female", "sex_ratio", "households", "avg_household_size",
              "table", "pdf_page", "printed_page", "source_url"]
    with open(out_csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for name in sorted(tables):
            for ward in tables[name]["wards"]:
                writer.writerow({**ward, "table": tables[name]["table"], "source_url": census["report_url"]})
    summary = {"report_title": census.get("report_title", ""), "report_url": census["report_url"], "report_sha256": report_sha,
               "report_pages": len(reader.pages), "retrieved": date, "councils_requested": sorted(wanted), "councils_missing": missing,
               "tables": {name: {k: t[k] for k in ("table", "pdf_pages", "printed_pages", "total")} for name, t in sorted(tables.items())},
               "reconciliation": checks}
    (raw / f"nbs_2022_councils_{date}.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"wards": sum(len(t["wards"]) for t in tables.values()), "councils": {k: v["wards"] for k, v in checks.items()},
                      "missing": missing, "not_reconciled": failed, "csv": str(out_csv.relative_to(G.ROOT))}, indent=1))
    return 1 if missing or failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
