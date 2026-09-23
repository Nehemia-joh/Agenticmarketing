#!/usr/bin/env python3
"""Verify the canonical database, workbook, skills, and repository cleanliness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
DEFAULT_WORKBOOK = ROOT / "outputs" / "master" / "Silverleaf Master Database - Consolidated.xlsx"
DEFAULT_REPORT = ROOT / "outputs" / "reports" / "master-verification.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    connection = sqlite3.connect(f"file:{args.database.resolve().as_posix()}?mode=ro", uri=True)
    tables = [
        "source_files", "source_records", "organisations", "contacts", "enquiries",
        "messages", "outreach_plans", "strategies", "automation_recipes",
        "campaign_lead_assignments", "acquisition_tracks", "value_proposition_modules",
        "lead_intake_rules",
    ]
    counts = {table: connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in tables}
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    hooks = {
        "verified": connection.execute("SELECT COUNT(*) FROM outreach_plans WHERE hook_status LIKE 'Verified%' AND COALESCE(hook,'')<>''").fetchone()[0],
        "active_unverified": connection.execute("SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(hook,'')<>'' AND hook_status NOT LIKE 'Verified%'").fetchone()[0],
    }
    # Every verified hook links to its source, and every lead-brief fact keeps its link, excerpt and research record.
    hooks["verified_without_source"] = connection.execute(
        "SELECT COUNT(*) FROM outreach_plans WHERE hook_status LIKE 'Verified%' AND COALESCE(hook,'')<>'' AND COALESCE(evidence_url,'') NOT LIKE 'http%'"
    ).fetchone()[0]
    briefs = {"facts": 0, "untraceable": 0}
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='lead_briefs'").fetchone():
        briefs["facts"] = connection.execute("SELECT COUNT(*) FROM lead_briefs").fetchone()[0]
        briefs["untraceable"] = connection.execute(
            "SELECT COUNT(*) FROM lead_briefs WHERE source_url NOT LIKE 'http%' OR COALESCE(excerpt,'')='' OR record_id NOT IN "
            "(SELECT record_id FROM source_records)").fetchone()[0]
    assignments = {
        "plans": counts["outreach_plans"],
        "with_track": connection.execute("SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(acquisition_track_id,'')<>''").fetchone()[0],
    }
    enabled_automations = connection.execute("SELECT COUNT(*) FROM automation_configuration WHERE enabled=1").fetchone()[0]
    connection.close()
    unwanted = []
    for path in ROOT.rglob("*"):
        relative_parts = path.relative_to(ROOT).parts
        if relative_parts[:2] == (".claude", "worktrees"):
            continue  # other sessions' git worktrees are separate checkouts (git excludes them), not part of this one
        if "node_modules" in relative_parts or "__pycache__" in relative_parts or path.name.endswith(".inspect.ndjson"):
            unwanted.append(str(path.relative_to(ROOT)))
    checks = {
        "integrity": integrity == "ok",
        "foreign_keys": not foreign_keys,
        "workbook_exists": args.workbook.is_file(),
        "all_plans_classified": assignments["plans"] == assignments["with_track"],
        "hooks_supported": hooks["active_unverified"] == 0,
        "hooks_link_to_sources": hooks["verified_without_source"] == 0,
        "lead_briefs_traceable": briefs["untraceable"] == 0,
        "automations_disabled": enabled_automations == 0,
        "no_generated_dependency_debris": not unwanted,
    }
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "result": "passed" if all(checks.values()) else "failed",
        "database": str(args.database.resolve()),
        "database_sha256": sha256(args.database),
        "workbook": str(args.workbook.resolve()),
        "workbook_sha256": sha256(args.workbook) if args.workbook.is_file() else None,
        "checks": checks,
        "counts": counts,
        "hooks": hooks,
        "lead_briefs": briefs,
        "assignments": assignments,
        "enabled_automations": enabled_automations,
        "unwanted_paths": unwanted,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
