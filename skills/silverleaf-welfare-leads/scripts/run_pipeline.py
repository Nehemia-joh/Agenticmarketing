#!/usr/bin/env python3
"""Run the deterministic part of a welfare run end to end (no network calls).

Order: master baseline -> classify register -> consolidate research -> build -> export -> validate intake (create skill)
-> initialise run database (create skill) -> augment -> workbook -> verify. Stops at the first failing step.

Network collection happens before this, separately and rate-limited: fetch_ngo_register.py, collect_osm_welfare.py
and the research agents planned by plan_research.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime

import welfare_lib as W


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--rebuild-db", action="store_true",
                        help="replace an existing run database; it is derived from the intake, so nothing else is lost")
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    paths = cfg["paths"]
    if paths["db"].exists() and not args.rebuild_db:
        raise SystemExit(f"{paths['db'].relative_to(W.ROOT)} exists. Re-run with --rebuild-db to regenerate it from the intake.")
    master_wb = W.ROOT / "outputs" / "master" / "Silverleaf Master Database - Consolidated.xlsx"
    baseline = {"recorded_at": datetime.now().isoformat(timespec="seconds"), "master_db_sha256": W.sha256_file(W.MASTER),
                "master_workbook_sha256": W.sha256_file(master_wb) if master_wb.exists() else ""}
    (paths["work"] / "master-baseline.json").write_text(json.dumps(baseline, indent=1), encoding="utf-8")
    here = W.SKILL / "scripts"
    run = ["--run-id", args.run_id]
    steps = [
        ("classify register", [here / "classify_ngo_register.py", *run]),
        ("consolidate research", [here / "consolidate_research.py", *run]),
        ("build run", [here / "build_welfare_run.py", *run]),
        ("export intake", [here / "export_welfare_run.py", *run]),
        ("validate intake", [W.CREATE_SCRIPTS / "validate_intake.py", paths["intake"], "--report", paths["run_out"] / "intake-validation.json"]),
        ("initialise database", [W.CREATE_SCRIPTS / "initialize_lead_db.py", paths["intake"], paths["db"], *(["--replace"] if args.rebuild_db else [])]),
        ("augment database", [here / "augment_run_db.py", *run]),
        ("build workbook", [here / "build_welfare_workbook.py", *run]),
        ("verify run", [here / "verify_welfare_run.py", *run]),
    ]
    for label, command in steps:
        print(f"\n== {label} ==", flush=True)
        result = subprocess.run([sys.executable, *map(str, command)], cwd=W.ROOT, capture_output=True, text=True, encoding="utf-8")
        tail = (result.stdout or "").strip().splitlines()[-12:]
        print("\n".join(tail))
        if result.returncode != 0:
            print((result.stderr or "").strip()[-2000:])
            print(f"\nStopped: '{label}' failed (exit {result.returncode}).")
            return result.returncode
    print(f"\nDone. Workbook: {paths['workbook'].relative_to(W.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
