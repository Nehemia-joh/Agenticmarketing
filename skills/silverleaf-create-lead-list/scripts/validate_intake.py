#!/usr/bin/env python3
"""Validate a Silverleaf lead-intake CSV without changing any data."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

RECORD_TYPES = {"organisation", "contact", "enquiry"}
VERIFICATION = {"verified", "needs_review", "historical", "unverified"}
EVIDENCE = {
    "official", "published", "public_profile", "public_post", "directory",
    "reference_file", "research_note",
}
TRACKS = {"", "AQ00_RESEARCH_ONLY", "AQ01_PERMISSION_LED", "AQ02_TRIGGER_LED"}
REVIEW = {"", "research_only", "needs_review", "draft_ready", "approved"}
ROLE_CERTAINTY = {"", "confirmed", "role_desk", "inferred_role", "unknown"}
DATE_QUALIFICATION = {"", "exact", "month_only", "year_only", "unknown"}
CURRENT_RELEVANCE = {"", "current", "recent", "historical", "unknown"}
PRIORITY = {"", "High", "Medium", "Low"}
REQUIRED_HEADERS = {
    "record_type", "source_path", "source_location", "source_url", "acquired_on",
    "verified_on", "verification_status", "evidence_basis", "evidence_excerpt",
    "organisation_name", "contact_name", "contact_route", "enquiry_author",
    "enquiry_type", "enquiry_date", "request", "platform", "hook",
    "hook_source_url", "hook_verified_on", "acquisition_track_id", "value_module_ids",
    "review_status",
}
CONTACT_ROUTES = {
    "named_email", "published_role_email", "shared_email", "role_phone",
    "organisation_phone", "profile_url", "source_url",
}
EMAIL_FIELDS = {"public_email", "shared_email", "published_role_email", "named_email", "enquiry_email"}
URL_FIELDS = {"source_url", "website", "profile_url", "hook_source_url"}
DATE_FIELDS = {"source_date", "acquired_on", "verified_on", "enquiry_date", "hook_verified_on"}
NUMERIC_FIELDS = {"distance_km", "latitude", "longitude", "desk_score"}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def norm(value: str | None) -> str:
    return " ".join((value or "").strip().casefold().split())


def canonical_url(value: str | None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    parts = urlsplit(raw)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), path, parts.query, ""))


def row_key(row: dict[str, str]) -> tuple[str, ...] | None:
    kind = norm(row.get("record_type"))
    if kind == "organisation":
        domain = norm(row.get("organisation_domain"))
        return (kind, domain) if domain else (kind, norm(row.get("organisation_name")), norm(row.get("locality")))
    if kind == "contact":
        org = norm(row.get("organisation_name"))
        email = norm(row.get("named_email"))
        if email:
            return (kind, org, email)
        name_role = (norm(row.get("contact_name")), norm(row.get("role")))
        if any(name_role):
            return (kind, org, *name_role)
        route = next((norm(row.get(field)) for field in CONTACT_ROUTES if row.get(field)), "")
        return (kind, org, route)
    if kind == "enquiry":
        return (
            kind, norm(row.get("platform")), canonical_url(row.get("source_url")),
            norm(row.get("enquiry_date")), norm(row.get("enquiry_author")),
        )
    return None


def validate(path: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    counts: Counter[str] = Counter()
    seen: dict[tuple[str, ...], int] = {}

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_HEADERS - headers)
        if missing:
            errors.append({"row": 1, "field": "header", "message": f"Missing columns: {', '.join(missing)}"})
        for line_number, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key is not None}
            kind = norm(row.get("record_type"))
            if kind not in RECORD_TYPES:
                errors.append({"row": line_number, "field": "record_type", "message": "Use organisation, contact, or enquiry."})
                continue
            counts[kind] += 1
            for field in ("source_location", "acquired_on", "verified_on", "verification_status", "evidence_basis", "evidence_excerpt"):
                if not row.get(field):
                    errors.append({"row": line_number, "field": field, "message": "Required."})
            if not row.get("source_path") and not row.get("source_url"):
                errors.append({"row": line_number, "field": "source_path/source_url", "message": "Provide at least one source reference."})
            if row.get("verification_status") not in VERIFICATION:
                errors.append({"row": line_number, "field": "verification_status", "message": f"Allowed: {sorted(VERIFICATION)}"})
            if row.get("evidence_basis") not in EVIDENCE:
                errors.append({"row": line_number, "field": "evidence_basis", "message": f"Allowed: {sorted(EVIDENCE)}"})
            if row.get("acquisition_track_id", "") not in TRACKS:
                errors.append({"row": line_number, "field": "acquisition_track_id", "message": f"Allowed: {sorted(TRACKS)}"})
            if row.get("review_status", "") not in REVIEW:
                errors.append({"row": line_number, "field": "review_status", "message": f"Allowed: {sorted(REVIEW)}"})
            if row.get("role_certainty", "") not in ROLE_CERTAINTY:
                errors.append({"row": line_number, "field": "role_certainty", "message": f"Allowed: {sorted(ROLE_CERTAINTY)}"})
            if row.get("date_qualification", "") not in DATE_QUALIFICATION:
                errors.append({"row": line_number, "field": "date_qualification", "message": f"Allowed: {sorted(DATE_QUALIFICATION)}"})
            if row.get("current_relevance", "") not in CURRENT_RELEVANCE:
                errors.append({"row": line_number, "field": "current_relevance", "message": f"Allowed: {sorted(CURRENT_RELEVANCE)}"})
            if row.get("priority", "") not in PRIORITY:
                errors.append({"row": line_number, "field": "priority", "message": f"Allowed: {sorted(PRIORITY)}"})
            for field in DATE_FIELDS:
                value = row.get(field, "")
                if value:
                    try:
                        date.fromisoformat(value)
                    except ValueError:
                        errors.append({"row": line_number, "field": field, "message": "Use YYYY-MM-DD."})
            for field in URL_FIELDS:
                value = row.get(field, "")
                if value and urlsplit(value).scheme not in {"http", "https"}:
                    errors.append({"row": line_number, "field": field, "message": "Use an http or https URL."})
            for field in EMAIL_FIELDS:
                value = row.get(field, "")
                if value and not EMAIL_RE.match(value):
                    errors.append({"row": line_number, "field": field, "message": "Invalid email format."})
            for field in NUMERIC_FIELDS:
                value = row.get(field, "")
                if value:
                    try:
                        float(value)
                    except ValueError:
                        errors.append({"row": line_number, "field": field, "message": "Use a number."})
            if row.get("headcount"):
                try:
                    int(row["headcount"])
                except ValueError:
                    errors.append({"row": line_number, "field": "headcount", "message": "Use an integer."})
            if kind in {"organisation", "contact"} and not row.get("organisation_name"):
                errors.append({"row": line_number, "field": "organisation_name", "message": "Required for this record type."})
            if kind == "contact":
                if not row.get("contact_name") and not row.get("role"):
                    errors.append({"row": line_number, "field": "contact_name/role", "message": "Provide a person or role desk."})
                if not any(row.get(field) for field in CONTACT_ROUTES):
                    errors.append({"row": line_number, "field": "contact route", "message": "Provide at least one public route."})
            if kind == "enquiry":
                for field in ("enquiry_type", "enquiry_date", "request", "platform", "source_url"):
                    if not row.get(field):
                        errors.append({"row": line_number, "field": field, "message": "Required for an enquiry."})
            if row.get("hook") and (not row.get("hook_source_url") or not row.get("hook_verified_on")):
                errors.append({"row": line_number, "field": "hook", "message": "A hook requires hook_source_url and hook_verified_on."})
            modules = [item for item in row.get("value_module_ids", "").split("|") if item]
            invalid_modules = [item for item in modules if not re.fullmatch(r"VM0[1-7]", item)]
            if invalid_modules:
                errors.append({"row": line_number, "field": "value_module_ids", "message": f"Invalid modules: {invalid_modules}"})
            key = row_key(row)
            if key and key in seen:
                warnings.append({"row": line_number, "field": "identity", "message": f"Exact duplicate of row {seen[key]}."})
            elif key:
                seen[key] = line_number

    if not sum(counts.values()):
        warnings.append({"row": 1, "field": "data", "message": "The intake has headers but no records."})
    return {
        "file": str(path.resolve()),
        "status": "valid" if not errors else "invalid",
        "row_count": sum(counts.values()),
        "counts": dict(sorted(counts.items())),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("intake", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate(args.intake)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    sys.exit(main())
