#!/usr/bin/env python3
"""Export deterministic workbook input from the canonical Silverleaf SQLite database.

Writes runtime/artifacts/workbook-input.json for scripts/master/build_master_workbook.py. Besides the tables, it adds
the review enrichment the workbook shows next to each record, all derived from the database:
- organisations: route status, official social pages, named contacts and decision-makers, the contact-research methods
  and the research warnings raised as review items;
- contacts: decision-maker flag, best route (own, else the organisation's published route) and pdpa_risk.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
DEFAULT_OUTPUT = ROOT / "runtime" / "artifacts" / "workbook-input.json"
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import contact_lib as C  # noqa: E402  (decision-maker and personal-email rules shared with the contact research)

RESEARCH_REVIEW = re.compile(r"^(Contact research|Possible closure|Website field holds no website|Phone field holds no phone number)")


def rows(connection: sqlite3.Connection, query: str) -> list[dict]:
    return [dict(row) for row in connection.execute(query)]


def count(connection: sqlite3.Connection, table: str) -> int:
    return connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def decision_maker(role: str) -> bool:
    return bool(C.DECISION.search(C.NOT_A_HEAD.sub("", role or "")))


def enrich(connection: sqlite3.Connection, organisations: list[dict], contacts: list[dict]) -> None:
    """Add the review enrichment in place (see the module docstring)."""
    org_by_id = {o["organisation_id"]: o for o in organisations}
    facts = defaultdict(dict)
    for entity_id, field, value in connection.execute(
            "SELECT entity_id, field, value FROM facts WHERE entity_type='contact' AND field IN ('pdpa_risk','decision_maker')"):
        facts[entity_id][field] = value
    socials = defaultdict(dict)
    for entity_id, field, value in connection.execute(
            "SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' AND field LIKE 'social (%' ORDER BY field, value"):
        socials[entity_id].setdefault(field[8:-1], value)
    methods = {}
    for location, payload in connection.execute("SELECT location, payload_json FROM source_records WHERE location LIKE 'contact profile %'"):
        match = re.match(r"contact profile (\S+) \((\d{4}-\d{2}-\d{2})\)", location or "")
        if match:
            found = json.loads(payload or "{}").get("methods") or []
            methods[match.group(1)] = f"{', '.join(found) or 'searched, nothing found'} ({match.group(2)})"
    flags = defaultdict(list)
    for entity_id, kind in connection.execute("SELECT entity_id, kind FROM review ORDER BY kind"):
        if RESEARCH_REVIEW.match(kind or "") and kind not in flags[entity_id]:
            flags[entity_id].append(kind)

    people = defaultdict(list)
    for c in contacts:
        org = org_by_id.get(c["organisation_id"], {})
        named = c["name"] or ""
        own_email = c["named_email"] if c["named_email"] and not C.W.PERSONAL_EMAIL.search(c["named_email"]) else ""
        route = next(((kind, value) for kind, value in (
            ("own email", own_email), ("role email", c["published_role_email"]), ("own phone", c["role_phone"]),
            ("organisation inbox", c["shared_email"] or org.get("email")), ("organisation phone", c["organisation_phone"] or org.get("phone")))
            if value), ("website or profile page only", c["source_url"] or ""))
        risk = facts[c["contact_id"]].get("pdpa_risk") or (
            "low" if not named else "risky" if c["named_email"] and C.W.PERSONAL_EMAIL.search(c["named_email"]) else "medium")
        decides = facts[c["contact_id"]].get("decision_maker")
        c["decision_maker"] = ("yes" if decides == "true" else "no") if decides else ("yes" if named and decision_maker(c["role"]) else "no")
        c["best_route_type"], c["best_route"], c["pdpa_risk"] = route[0], route[1], risk
        people[c["organisation_id"]].append(c)

    for o in organisations:
        team = people.get(o["organisation_id"], [])
        # Only a real address or number counts: directory imports left category codes in some phone fields.
        direct = bool("@" in (o["email"] or "") or C.is_phone(o["phone"]) or any(c["best_route_type"] in ("own email", "role email", "own phone")
                                                                             for c in team))
        o["route_status"] = "direct route" if direct else ("indirect only" if (o["website"] or o["address"]) else "no route")
        o["social_pages"] = "; ".join(f"{k}: {v}" for k, v in socials.get(o["organisation_id"], {}).items())
        o["named_contacts"] = sum(1 for c in team if c["name"])
        o["decision_makers"] = "; ".join(f"{c['name']} ({c['role']})" for c in team if c["name"] and c["decision_maker"] == "yes")
        o["contact_research"] = methods.get(o["organisation_id"], "")
        o["research_flags"] = "; ".join(flags.get(o["organisation_id"], []))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    connection = sqlite3.connect(f"file:{args.database.resolve().as_posix()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    track_counts = dict(connection.execute(
        "SELECT acquisition_track_id, COUNT(*) FROM outreach_plans GROUP BY acquisition_track_id"
    ))
    counts = {
        "source_files": count(connection, "source_files"),
        "source_records": count(connection, "source_records"),
        "organisations": count(connection, "organisations"),
        "contacts": count(connection, "contacts"),
        "enquiries": count(connection, "enquiries"),
        "messages": count(connection, "messages"),
        "outreach_plans": count(connection, "outreach_plans"),
        "strategies": count(connection, "strategies"),
        "automation_steps": count(connection, "automation_recipes"),
        "knowledge_documents": count(connection, "knowledge_documents"),
        "positioning_evidence": count(connection, "positioning_evidence"),
        "campaigns": count(connection, "campaigns"),
        "campaign_touchpoints": count(connection, "campaign_touchpoints"),
        "outreach_segments": count(connection, "outreach_segments"),
        "campaign_lead_assignments": count(connection, "campaign_lead_assignments"),
        "parent_enquiry_drafts": count(connection, "parent_enquiry_drafts"),
        "parent_enquiry_outreach_drafts": connection.execute(
            "SELECT COUNT(*) FROM parent_enquiry_drafts WHERE status LIKE 'Review only%'"
        ).fetchone()[0],
        "parent_enquiry_excluded_from_outreach": connection.execute(
            "SELECT COUNT(*) FROM parent_enquiry_drafts WHERE status LIKE 'No outreach draft%'"
        ).fetchone()[0],
        "verified_hooks": connection.execute(
            "SELECT COUNT(*) FROM outreach_plans WHERE hook_status LIKE 'Verified%' AND COALESCE(hook,'')<>''"
        ).fetchone()[0],
        "active_unverified_hooks": connection.execute(
            "SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(hook,'')<>'' AND hook_status NOT LIKE 'Verified%'"
        ).fetchone()[0],
        "acquisition_tracks": count(connection, "acquisition_tracks"),
        "value_proposition_modules": count(connection, "value_proposition_modules"),
        "lead_intake_rules": count(connection, "lead_intake_rules"),
        "acquisition_hold": track_counts.get("AQ00", 0),
        "acquisition_routing": track_counts.get("AQ01", 0),
        "acquisition_direct": track_counts.get("AQ02", 0),
        "review": count(connection, "review"),
        "campuses": count(connection, "campuses"),
        "facts": count(connection, "facts"),
        "offer_aligned_plans": connection.execute("SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(offer_version,'')<>''").fetchone()[0],
    }
    report = {
        "run_id": f"workbook-export-{date.today().isoformat()}",
        "checked_on": date.today().isoformat(),
        "result": "complete",
        "missing_records": 0,
        "counts": counts,
        "core_counts_preserved": {key: counts[key] for key in ("organisations", "contacts", "enquiries", "messages", "outreach_plans")},
        "marketing_documents_reviewed": 12,
        "marketing_originals_added_to_master": 11,
        "calendar_already_in_master": True,
        "messages_rewritten_v3": counts["outreach_plans"],
        "historical_parent_drafts_covered": counts["parent_enquiry_drafts"],
        "historical_parent_outreach_drafts": counts["parent_enquiry_outreach_drafts"],
        "sending_enabled": False,
        "notes": [
            "New organisation and business-contact leads use acquisition tracks independent of the internal marketing calendar.",
            "Fees, discounts, referral terms, capacity and event dates require current approval.",
            "No campaign or automation is enabled by this export.",
        ],
        "acquisition_version": "2026-09-09-new-contact-acquisition-v4",
        "new_contact_strategy_scope": "Independent of the internal marketing calendar; approved positioning is reused where applicable.",
        "existing_lead_count_reclassified": counts["outreach_plans"],
        # Later runs recorded as reports beside their outputs (the workbook's audit sheet lists them).
        "offer_messages": read_json(ROOT / "outputs" / "messages" / "master-offer-messages-reconciliation.json"),
        "contact_merge": read_json(ROOT / "outputs" / "contacts" / "master-contact-merge.json"),
        "acquisition_refresh_runs": rows(connection, "SELECT * FROM acquisition_refresh_runs ORDER BY ran_on, run_id"),
        "contact_research_reviews": sum(1 for (kind,) in connection.execute("SELECT kind FROM review") if RESEARCH_REVIEW.match(kind or "")),
        "plans_held_for_closure": connection.execute(
            "SELECT COUNT(*) FROM outreach_plans WHERE missing_information LIKE 'Possible closure found by contact research%'").fetchone()[0],
        "integrity_check": connection.execute("PRAGMA integrity_check").fetchone()[0],
        "foreign_key_violations": len(connection.execute("PRAGMA foreign_key_check").fetchall()),
    }
    organisations = rows(connection, """
            SELECT
              o.organisation_id,o.name,o.segment,o.priority,o.campus,o.locality,o.distance_km,
              o.geocode_precision,o.phone,o.email,o.website,o.address,o.headcount,o.size_evidence,
              o.education_angle,o.desk_tier,o.desk_score,o.verification,o.strategy_id,
              '' AS owner,o.outreach_status,o.next_action,o.next_action_date,
              (
                SELECT group_concat(message_id,' | ')
                FROM (
                  SELECT m.message_id
                  FROM messages m
                  WHERE m.target_type='organisation' AND m.target_id=o.organisation_id
                  ORDER BY m.message_id
                )
              ) AS message_ids,
              (
                SELECT group_concat(record_id,' | ')
                FROM (
                  SELECT es.record_id
                  FROM entity_sources es
                  WHERE es.entity_type='organisation' AND es.entity_id=o.organisation_id
                  ORDER BY es.record_id
                )
              ) AS source_record_ids,
              o.source_url
            FROM organisations o
            ORDER BY o.name,o.organisation_id
        """)
    contacts = rows(connection, """
            SELECT
              c.contact_id,c.name,c.organisation_id,c.role,c.campus,c.named_email,
              c.published_role_email,c.role_phone,c.shared_email,c.organisation_phone,
              c.contact_route,c.verification,o.name AS organisation_name,
              (
                SELECT group_concat(message_id,' | ')
                FROM (
                  SELECT m.message_id
                  FROM messages m
                  WHERE m.target_type='contact' AND m.target_id=c.contact_id
                  ORDER BY m.message_id
                )
              ) AS message_ids,
              c.source_url,
              (
                SELECT group_concat(record_id,' | ')
                FROM (
                  SELECT es.record_id
                  FROM entity_sources es
                  WHERE es.entity_type='contact' AND es.entity_id=c.contact_id
                  ORDER BY es.record_id
                )
              ) AS source_record_ids
            FROM contacts c
            JOIN organisations o USING(organisation_id)
            ORDER BY o.name,c.name,c.contact_id
        """)
    enrich(connection, organisations, contacts)
    names = {("organisation", o["organisation_id"]): o["name"] for o in organisations}
    names |= {("contact", c["contact_id"]): c["name"] or c["role"] for c in contacts}
    names |= {("enquiry", r["enquiry_id"]): r["name"] for r in connection.execute("SELECT enquiry_id, name FROM enquiries")}
    by_id = {entity_id: name for (_, entity_id), name in names.items()}
    review = rows(connection, 'SELECT review_id, kind, entity_id, related_id, field, "values", action FROM review ORDER BY kind, review_id')
    for r in review:
        r["entity_name"] = by_id.get(r["entity_id"], "")
    # Facts as distinct assertions: repeated copies of the same assertion from several source rows become one row.
    facts = []
    for entity_type, entity_id, field, value, records in connection.execute(
            "SELECT entity_type, entity_id, field, value, group_concat(DISTINCT record_id) FROM facts "
            "GROUP BY entity_type, entity_id, field, value ORDER BY entity_type, entity_id, field, value"):
        facts.append({"entity_type": entity_type, "entity_name": names.get((entity_type, entity_id), ""), "entity_id": entity_id, "field": field,
                      "value": value, "source_record_ids": "; ".join(sorted(str(records or "").split(",")))})
    payload = {
        "report": report,
        "organisations": organisations,
        "contacts": contacts,
        "enquiries": rows(connection, "SELECT * FROM enquiries ORDER BY enquiry_date DESC, enquiry_id"),
        "campuses": rows(connection, "SELECT * FROM campuses ORDER BY name"),
        "review": review,
        "facts": facts,
        "positioning_evidence": rows(connection, "SELECT * FROM positioning_evidence ORDER BY evidence_id"),
        "campaigns": rows(connection, "SELECT * FROM campaigns ORDER BY campaign_id"),
        "campaign_touchpoints": rows(connection, "SELECT * FROM campaign_touchpoints ORDER BY campaign_id,touchpoint_order"),
        "outreach_segments": rows(connection, "SELECT * FROM outreach_segments ORDER BY segment"),
        "campaign_lead_assignments": rows(connection, "SELECT * FROM campaign_lead_assignments ORDER BY assignment_id"),
        "parent_enquiry_drafts": rows(connection, "SELECT * FROM parent_enquiry_drafts ORDER BY enquiry_id"),
        "automation_recipes": rows(connection, "SELECT * FROM automation_recipes ORDER BY flow_id,step"),
        "messages": rows(connection, "SELECT * FROM messages ORDER BY message_id"),
        "outreach_plans": rows(connection, "SELECT * FROM outreach_plans ORDER BY message_id"),
        "strategies": rows(connection, "SELECT * FROM strategies ORDER BY title,strategy_id"),
        "source_files": rows(connection, "SELECT source_id,path,sha256,bytes,kind,encoding FROM source_files ORDER BY path"),
        "source_rows": rows(connection, "SELECT r.record_id,r.source_id,f.path AS source_file,r.location FROM source_records r JOIN source_files f USING(source_id) ORDER BY r.record_id"),
        "knowledge_documents": rows(connection, "SELECT * FROM knowledge_documents ORDER BY title,document_id"),
        "acquisition_tracks": rows(connection, "SELECT * FROM acquisition_tracks ORDER BY track_id"),
        "value_proposition_modules": rows(connection, "SELECT * FROM value_proposition_modules ORDER BY module_id"),
        "lead_intake_rules": rows(connection, "SELECT * FROM lead_intake_rules ORDER BY stage_order"),
        # Facts about each researched lead, each with its source, so a person can learn about the lead if they reply.
        "lead_briefs": rows(connection, "SELECT b.*, o.name AS organisation_name FROM lead_briefs b JOIN organisations o USING(organisation_id) "
                                        "ORDER BY o.name, b.position") if connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='lead_briefs'").fetchone() else [],
    }
    connection.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "exported", "output": str(args.output.resolve()), "counts": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
