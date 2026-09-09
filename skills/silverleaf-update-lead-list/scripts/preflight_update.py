#!/usr/bin/env python3
"""Read-only validation and exact-match preflight for a lead database update."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = SKILLS_DIR / "silverleaf-create-lead-list" / "scripts" / "validate_intake.py"
SPEC = importlib.util.spec_from_file_location("validate_intake", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(VALIDATOR)


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f'PRAGMA table_info("{table}")')}


def fetch_existing(connection: sqlite3.Connection):
    org_cols = table_columns(connection, "organisations")
    name_col = "name" if "name" in org_cols else "organisation_name"
    domain_col = "domain" if "domain" in org_cols else None
    locality_col = "locality" if "locality" in org_cols else None
    select = ["organisation_id", name_col]
    select.append(domain_col or "NULL")
    select.append(locality_col or "NULL")
    organisations = {}
    by_name_locality = {}
    for org_id, name, domain, locality in connection.execute(f"SELECT {', '.join(select)} FROM organisations"):
        if domain:
            organisations[(VALIDATOR.norm(domain),)] = org_id
        by_name_locality[(VALIDATOR.norm(name), VALIDATOR.norm(locality))] = org_id

    contacts = set()
    contact_cols = table_columns(connection, "contacts")
    if contact_cols:
        fields = [field for field in ("organisation_id", "name", "role", "named_email", "published_role_email", "shared_email", "role_phone", "organisation_phone") if field in contact_cols]
        for row in connection.execute(f"SELECT {', '.join(fields)} FROM contacts"):
            item = dict(zip(fields, row))
            org_id = item.get("organisation_id")
            for value in (item.get("named_email"), item.get("published_role_email"), item.get("shared_email")):
                if value:
                    contacts.add((org_id, "email", VALIDATOR.norm(value)))
            contacts.add((org_id, "name_role", VALIDATOR.norm(item.get("name")), VALIDATOR.norm(item.get("role"))))
    enquiries = set()
    enquiry_cols = table_columns(connection, "enquiries")
    if enquiry_cols:
        name_col = "name" if "name" in enquiry_cols else "enquiry_author"
        for platform, source_url, enquiry_date, author in connection.execute(
            f"SELECT platform, source_url, enquiry_date, {name_col} FROM enquiries"
        ):
            enquiries.add((VALIDATOR.norm(platform), VALIDATOR.canonical_url(source_url), VALIDATOR.norm(enquiry_date), VALIDATOR.norm(author)))
    return organisations, by_name_locality, contacts, enquiries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("intake", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    validation = VALIDATOR.validate(args.intake)
    if validation["status"] != "valid":
        result = {"status": "invalid_intake", "validation": validation}
        payload = json.dumps(result, indent=2, ensure_ascii=False)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 1
    connection = sqlite3.connect(f"file:{args.database.resolve().as_posix()}?mode=ro", uri=True)
    required = {"organisations", "contacts", "enquiries", "source_files", "source_records", "entity_sources"}
    existing_tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing_tables = sorted(required - existing_tables)
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
    if missing_tables:
        result = {"status": "invalid_database", "missing_tables": missing_tables, "integrity_check": integrity}
    else:
        organisations, by_name_locality, contacts, enquiries = fetch_existing(connection)
        actions = []
        counts = Counter()
        with args.intake.open("r", encoding="utf-8-sig", newline="") as handle:
            for line_number, row in enumerate(csv.DictReader(handle), start=2):
                row = {key: (value or "").strip() for key, value in row.items()}
                kind = VALIDATOR.norm(row["record_type"])
                action = "insert"
                reason = "no exact match"
                organisation_id = None
                if kind in {"organisation", "contact"}:
                    domain_key = (VALIDATOR.norm(row.get("organisation_domain")),)
                    name_key = (VALIDATOR.norm(row.get("organisation_name")), VALIDATOR.norm(row.get("locality")))
                    organisation_id = organisations.get(domain_key) if domain_key[0] else None
                    organisation_id = organisation_id or by_name_locality.get(name_key)
                    if kind == "organisation" and organisation_id:
                        action, reason = "match", "exact organisation key"
                    elif kind == "contact" and not organisation_id:
                        action, reason = "review", "organisation not found"
                    elif kind == "contact":
                        email = VALIDATOR.norm(row.get("named_email") or row.get("published_role_email") or row.get("shared_email"))
                        name_role = (organisation_id, "name_role", VALIDATOR.norm(row.get("contact_name")), VALIDATOR.norm(row.get("role")))
                        if (email and (organisation_id, "email", email) in contacts) or name_role in contacts:
                            action, reason = "match", "exact contact key"
                elif kind == "enquiry":
                    key = (VALIDATOR.norm(row.get("platform")), VALIDATOR.canonical_url(row.get("source_url")), VALIDATOR.norm(row.get("enquiry_date")), VALIDATOR.norm(row.get("enquiry_author")))
                    if key in enquiries:
                        action, reason = "match", "exact enquiry key"
                counts[action] += 1
                actions.append({"row": line_number, "record_type": kind, "action": action, "reason": reason, "organisation_id": organisation_id})
        result = {
            "status": "ready" if not foreign_keys and integrity == "ok" else "invalid_database",
            "database": str(args.database.resolve()),
            "intake": str(args.intake.resolve()),
            "integrity_check": integrity,
            "foreign_key_violations": len(foreign_keys),
            "counts": dict(sorted(counts.items())),
            "actions": actions,
        }
    connection.close()
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    sys.exit(main())
