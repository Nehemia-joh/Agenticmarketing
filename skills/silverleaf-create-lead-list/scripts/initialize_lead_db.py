#!/usr/bin/env python3
"""Create a canonical SQLite lead database from a validated intake CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sqlite3
import sys
import zlib
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_intake", SCRIPT_DIR / "validate_intake.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(VALIDATOR)

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE source_files (
  source_file_id TEXT PRIMARY KEY, path TEXT, source_url TEXT, sha256 TEXT NOT NULL,
  mime_type TEXT, acquired_on TEXT NOT NULL, original_bytes_zlib BLOB
);
CREATE TABLE source_records (
  source_record_id TEXT PRIMARY KEY, source_file_id TEXT NOT NULL, source_location TEXT NOT NULL,
  source_date TEXT, verified_on TEXT NOT NULL, verification_status TEXT NOT NULL,
  evidence_basis TEXT NOT NULL, evidence_excerpt TEXT NOT NULL, payload_json TEXT NOT NULL,
  FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id)
);
CREATE TABLE organisations (
  organisation_id TEXT PRIMARY KEY, name TEXT NOT NULL, domain TEXT, segment TEXT, subtype TEXT,
  priority TEXT, campus TEXT, distance_km REAL, radius_tier TEXT, geocode_precision TEXT,
  latitude REAL, longitude REAL, locality TEXT, address TEXT, website TEXT, email TEXT, phone TEXT,
  size_evidence TEXT, headcount INTEGER, education_angle TEXT, founded TEXT, licence_class TEXT,
  osm_id TEXT, desk_tier TEXT, desk_score REAL, transport_band TEXT, notes TEXT
);
CREATE TABLE contacts (
  contact_id TEXT PRIMARY KEY, organisation_id TEXT NOT NULL, name TEXT, role TEXT, role_certainty TEXT,
  contact_route TEXT, shared_email TEXT, published_role_email TEXT, named_email TEXT,
  organisation_phone TEXT, role_phone TEXT, profile_url TEXT, channel_attribution TEXT,
  FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE enquiries (
  enquiry_id TEXT PRIMARY KEY, name TEXT, type TEXT NOT NULL, enquiry_date TEXT NOT NULL,
  date_qualification TEXT, locality TEXT, request TEXT NOT NULL, campus_fit TEXT, phone TEXT, email TEXT,
  contact_attribution TEXT, platform TEXT NOT NULL, source_url TEXT NOT NULL, current_relevance TEXT,
  source_record_id TEXT NOT NULL, FOREIGN KEY (source_record_id) REFERENCES source_records(source_record_id)
);
CREATE TABLE entity_sources (
  entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, source_record_id TEXT NOT NULL,
  relationship TEXT NOT NULL DEFAULT 'supports',
  PRIMARY KEY (entity_type, entity_id, source_record_id),
  FOREIGN KEY (source_record_id) REFERENCES source_records(source_record_id)
);
CREATE TABLE facts (
  fact_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, field TEXT NOT NULL,
  value TEXT, source_record_id TEXT NOT NULL,
  FOREIGN KEY (source_record_id) REFERENCES source_records(source_record_id)
);
CREATE TABLE review (
  review_id TEXT PRIMARY KEY, kind TEXT NOT NULL, entity_type TEXT, entity_id TEXT, field TEXT,
  values_json TEXT, action TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open'
);
CREATE TABLE messages (
  message_id TEXT PRIMARY KEY, target_id TEXT NOT NULL, target_type TEXT NOT NULL,
  subject TEXT, body TEXT, version TEXT, review_status TEXT, created_at TEXT NOT NULL
);
CREATE TABLE outreach_plans (
  message_id TEXT PRIMARY KEY, target_id TEXT NOT NULL, target_type TEXT NOT NULL,
  organisation_id TEXT, relevance_reason TEXT, proposed_offer TEXT, cta_type TEXT,
  hook TEXT, hook_source_url TEXT, hook_verified_on TEXT, acquisition_track_id TEXT,
  value_module_ids TEXT, review_status TEXT, missing_information TEXT
);
CREATE TABLE automation_recipes (
  recipe_id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'DISABLED'
);
"""


def stable_id(prefix: str, *parts: str) -> str:
    key = "|".join(VALIDATOR.norm(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]}"


def as_float(value: str):
    return float(value) if value else None


def as_int(value: str):
    return int(value) if value else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("intake", type=Path)
    parser.add_argument("database", type=Path)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    report = VALIDATOR.validate(args.intake)
    if report["status"] != "valid":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1
    if args.database.exists() and not args.replace:
        print(f"Refusing to overwrite existing database: {args.database}", file=sys.stderr)
        return 2
    if args.database.exists():
        args.database.unlink()
    args.database.parent.mkdir(parents=True, exist_ok=True)
    raw_bytes = args.intake.read_bytes()
    source_sha = hashlib.sha256(raw_bytes).hexdigest()
    source_file_id = f"SRC_{source_sha[:16]}"
    created_at = datetime.now(timezone.utc).isoformat()
    connection = sqlite3.connect(args.database)
    connection.executescript(SCHEMA)
    connection.execute("INSERT INTO metadata VALUES (?, ?)", ("created_at", created_at))
    connection.execute("INSERT INTO metadata VALUES (?, ?)", ("source_of_truth", "SQLite"))
    connection.execute(
        "INSERT INTO source_files VALUES (?, ?, ?, ?, ?, ?, ?)",
        (source_file_id, str(args.intake.resolve()), "", source_sha, "text/csv", created_at[:10], zlib.compress(raw_bytes)),
    )
    organisation_ids: dict[tuple[str, ...], str] = {}
    inserted = {"organisations": 0, "contacts": 0, "enquiries": 0, "outreach_plans": 0}
    with args.intake.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]
    try:
        for index, row in enumerate(rows, start=2):
            source_record_id = stable_id("REC", source_sha, str(index), row.get("source_location", ""))
            connection.execute(
                "INSERT INTO source_records VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (source_record_id, source_file_id, row["source_location"], row.get("source_date"), row["verified_on"],
                 row["verification_status"], row["evidence_basis"], row["evidence_excerpt"], json.dumps(row, ensure_ascii=False)),
            )
            kind = VALIDATOR.norm(row["record_type"])
            target_id = ""
            organisation_id = None
            if kind in {"organisation", "contact"}:
                org_key = (VALIDATOR.norm(row.get("organisation_domain")),) if row.get("organisation_domain") else (
                    VALIDATOR.norm(row.get("organisation_name")), VALIDATOR.norm(row.get("locality")),
                )
                organisation_id = organisation_ids.get(org_key) or stable_id("ORG", *org_key)
                if org_key not in organisation_ids:
                    connection.execute(
                        "INSERT INTO organisations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (organisation_id, row["organisation_name"], row.get("organisation_domain"), row.get("segment"), row.get("subtype"),
                         row.get("priority"), row.get("campus"), as_float(row.get("distance_km", "")), row.get("radius_tier"),
                         row.get("geocode_precision"), as_float(row.get("latitude", "")), as_float(row.get("longitude", "")),
                         row.get("locality"), row.get("address"), row.get("website"), row.get("public_email"), row.get("public_phone"),
                         row.get("size_evidence"), as_int(row.get("headcount", "")), row.get("education_angle"), row.get("founded"),
                         row.get("licence_class"), row.get("osm_id"), row.get("desk_tier"), as_float(row.get("desk_score", "")),
                         row.get("transport_band"), row.get("notes")),
                    )
                    organisation_ids[org_key] = organisation_id
                    inserted["organisations"] += 1
                target_id = organisation_id
            if kind == "contact":
                key = VALIDATOR.row_key(row) or ("contact", str(index))
                target_id = stable_id("CON", *key)
                connection.execute(
                    "INSERT OR IGNORE INTO contacts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (target_id, organisation_id, row.get("contact_name"), row.get("role"), row.get("role_certainty"),
                     row.get("contact_route"), row.get("shared_email"), row.get("published_role_email"), row.get("named_email"),
                     row.get("organisation_phone"), row.get("role_phone"), row.get("profile_url"), row.get("channel_attribution")),
                )
                inserted["contacts"] += connection.execute("SELECT changes()").fetchone()[0]
            elif kind == "enquiry":
                key = VALIDATOR.row_key(row) or ("enquiry", str(index))
                target_id = stable_id("ENQ", *key)
                connection.execute(
                    "INSERT OR IGNORE INTO enquiries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (target_id, row.get("enquiry_author"), row["enquiry_type"], row["enquiry_date"], row.get("date_qualification"),
                     row.get("locality"), row["request"], row.get("campus_fit"), row.get("enquiry_phone"), row.get("enquiry_email"),
                     row.get("contact_attribution"), row["platform"], row["source_url"], row.get("current_relevance"), source_record_id),
                )
                inserted["enquiries"] += connection.execute("SELECT changes()").fetchone()[0]
            connection.execute(
                "INSERT OR IGNORE INTO entity_sources VALUES (?, ?, ?, 'supports')", (kind, target_id, source_record_id)
            )
            if any(row.get(field) for field in ("relevance_reason", "proposed_offer", "cta_type", "hook", "acquisition_track_id")):
                message_id = stable_id("MSG", kind, target_id, "v1")
                connection.execute(
                    "INSERT OR IGNORE INTO outreach_plans VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (message_id, target_id, kind, organisation_id, row.get("relevance_reason"), row.get("proposed_offer"),
                     row.get("cta_type"), row.get("hook"), row.get("hook_source_url"), row.get("hook_verified_on"),
                     row.get("acquisition_track_id") or "AQ00_RESEARCH_ONLY", row.get("value_module_ids"),
                     row.get("review_status") or "research_only", row.get("missing_information")),
                )
                inserted["outreach_plans"] += connection.execute("SELECT changes()").fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or foreign_keys:
            raise RuntimeError({"integrity_check": integrity, "foreign_key_check": foreign_keys})
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        args.database.unlink(missing_ok=True)
        raise
    connection.close()
    print(json.dumps({"database": str(args.database.resolve()), "status": "created", "inserted": inserted}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
