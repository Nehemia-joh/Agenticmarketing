#!/usr/bin/env python3
"""Verify the canonical database, workbook, skills, and repository cleanliness."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True  # the import below must not leave a __pycache__ folder, which this script reports as debris
sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_vicoba_groups as V  # noqa: E402  the VICOBA contract (vicoba-integration-plan.md section 4.1 and section 0)

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


def vicoba_checks(connection: sqlite3.Connection) -> tuple[dict, dict]:
    """VICOBA and VSLA savings groups (decided 13 October 2026): group-level records under the shared contract, with no phone on the
    organisation, no automatic merge with a SACCOS, and a recorded basis for any contact phone. All pass while the master holds none."""
    ids = V.vicoba_ids(connection)
    marks = ",".join("?" * len(ids))
    orgs = {r[0]: r[1:] for r in connection.execute(
        f"SELECT organisation_id, segment, subtype, geocode_precision, phone, email FROM organisations WHERE organisation_id IN ({marks})",
        tuple(ids))} if ids else {}
    facts: dict[str, dict[str, list[str]]] = {oid: {} for oid in ids}
    if ids:
        for oid, field, value in connection.execute(
                f"SELECT entity_id, field, value FROM facts WHERE entity_type='organisation' AND entity_id IN ({marks})", tuple(ids)):
            facts[oid].setdefault(field, []).append(value)
    linked = {r[0] for r in connection.execute(
        "SELECT DISTINCT es.entity_id FROM entity_sources es JOIN source_records sr ON sr.record_id=es.record_id WHERE es.entity_type='organisation'")}
    keys: dict[str, set[str]] = {}
    for oid, value in connection.execute("SELECT entity_id, value FROM facts WHERE field='vicoba_group_key'"):
        keys.setdefault(value.casefold(), set()).add(oid)
    saccos = {r[0] for r in connection.execute("SELECT organisation_id FROM organisations WHERE subtype LIKE 'SACCOS%'")}
    plans = {}
    for oid, segment in connection.execute("SELECT organisation_id, segment FROM outreach_plans"):
        plans.setdefault(oid, []).append(segment)
    plan_columns = {r[1] for r in connection.execute("PRAGMA table_info(outreach_plans)")}
    contact_phones = connection.execute(
        f"SELECT contact_id FROM contacts WHERE organisation_id IN ({marks}) AND (COALESCE(role_phone,'')<>'' OR COALESCE(organisation_phone,'')<>'')",
        tuple(ids)).fetchall() if ids else []
    phone_basis = {r[0] for r in connection.execute("SELECT entity_id FROM facts WHERE entity_type='contact' AND field='phone_basis' AND value='published_for_role'")}
    bad_labels = [oid for oid, (segment, subtype, precision, _, _) in orgs.items()
                  if segment != V.SEGMENT or subtype not in V.SUBTYPES or (precision or "") not in ("",) + V.PRECISIONS]
    unsourced = [oid for oid in ids if not facts[oid].get("vicoba_group_key") or oid not in linked
                 or not set(facts[oid].get("record_status", [])) or not set(facts[oid].get("record_status", [])) <= set(V.RECORD_STATUSES)
                 or not facts[oid].get("women_group") or not set(facts[oid]["women_group"]) <= {"true", "false"}]
    checks = {
        "vicoba_labels_valid": not bad_labels,
        "vicoba_keyed_and_sourced": not unsourced,
        "vicoba_keys_unique": all(len(owners) == 1 for owners in keys.values()) and all(len(set(facts[o].get("vicoba_group_key", []))) <= 1 for o in ids),
        "vicoba_no_organisation_phone": not any((orgs[o][3] or "").strip() for o in orgs),
        "vicoba_contact_phones_have_basis": all(c in phone_basis for (c,) in contact_phones),
        "vicoba_not_merged_with_saccos": not (saccos & {o for owners in keys.values() for o in owners}) and not (saccos & ids),
        "vicoba_plans_valid": all(plans.get(o) and set(plans[o]) <= set(V.OUTREACH_SEGMENTS) for o in ids)
                              and (not any(s in V.OUTREACH_SEGMENTS for ss in plans.values() for s in ss) or set(V.PLAN_COLUMNS) <= plan_columns),
    }
    summary = {"groups": len(ids), "by_subtype": {}, "by_record_status": {}, "women_groups": sum(1 for o in ids if "true" in facts[o].get("women_group", [])),
               "group_plans": sum(1 for ss in plans.values() for s in ss if s == V.GROUP_SEGMENT),
               "introducer_plans": sum(1 for ss in plans.values() for s in ss if s == "VICOBA introducers"),
               "organisation_emails": sum(1 for o in orgs if (orgs[o][4] or "").strip()),
               "review_items": dict(connection.execute(
                   f"SELECT kind, COUNT(*) FROM review WHERE kind IN ({','.join('?' * len(V.REVIEW_KINDS))}) GROUP BY kind", V.REVIEW_KINDS).fetchall()),
               "failing": {"labels": bad_labels[:10], "keyed_and_sourced": unsourced[:10]}}
    for o in ids:
        summary["by_subtype"][orgs[o][1]] = summary["by_subtype"].get(orgs[o][1], 0) + 1
        status = (facts[o].get("record_status") or [""])[-1]
        summary["by_record_status"][status] = summary["by_record_status"].get(status, 0) + 1
    return checks, summary


def national_checks(connection: sqlite3.Connection) -> tuple[dict, dict]:
    """The national leads table (association-members merge, 19 November 2026; scripts/master/add_association_members.py): every source row
    of the association workbook is accounted for once (in the master or in the national table, or an Index register row skipped), no
    national lead is an organisation, and the flags agree with the rows behind them. All pass while the table does not exist."""
    if not connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='national_leads'").fetchone():
        return {}, {"national_leads": 0}
    files = [r[0] for r in connection.execute("SELECT DISTINCT source_file FROM national_leads")]
    source_ids = [r[0] for f in files for r in connection.execute("SELECT source_id FROM source_files WHERE path=?", (f,))]
    marks = ",".join("?" * len(source_ids)) or "''"
    records = {r[0]: json.loads(r[1]) for r in connection.execute(
        f"SELECT record_id, payload_json FROM source_records WHERE source_id IN ({marks})", source_ids)}
    leads = {r[0]: {"flag": r[1], "organisation_id": r[2], "operating": r[3]} for r in connection.execute(
        "SELECT national_lead_id, flag, organisation_id, operating FROM national_leads")}
    links: dict[str, list[str]] = {}
    for nid, rid in connection.execute("SELECT national_lead_id, record_id FROM national_lead_sources"):
        links.setdefault(rid, []).append(nid)
    orgs = {r[0] for r in connection.execute("SELECT organisation_id FROM organisations")}
    org_links: dict[str, set[str]] = {}
    for oid, rid in connection.execute("SELECT entity_id, record_id FROM entity_sources WHERE entity_type='organisation'"):
        if rid in records:
            org_links.setdefault(rid, set()).add(oid)
    decisions: dict[str, int] = {}
    for rec in records.values():
        key = f"{'index' if rec.get('tab') == 'Index' else 'member'}:{rec.get('decision')}"
        decisions[key] = decisions.get(key, 0) + 1
    skipped = [rid for rid, rec in records.items() if rec.get("decision") == "skipped"]
    linked = [rid for rid in records if rid in links]
    to_master = [rid for rid, rec in records.items() if rec.get("tab") != "Index" and rec.get("decision") in ("master_new", "master_match")]
    member_rows = sum(1 for rec in records.values() if rec.get("tab") != "Index")
    national_rows = sum(1 for rec in records.values() if rec.get("tab") != "Index" and rec.get("decision") == "national")
    by_lead: dict[str, list[dict]] = {}
    for rid, nids in links.items():
        for nid in nids:
            by_lead.setdefault(nid, []).append(records.get(rid, {}))
    bad_flags = []
    for nid, lead in leads.items():
        rows = by_lead.get(nid, [])
        kinds = {r.get("decision") for r in rows}
        if lead["flag"] == "national only":
            ok = lead["organisation_id"] is None and kinds <= {"national"}
        elif lead["flag"] == "in master":
            ok = lead["organisation_id"] in orgs and bool(kinds & {"master_match", "introducer_new"})
        elif lead["flag"] == "in catchment":
            ok = lead["organisation_id"] in orgs and "master_new" in kinds and "master_match" not in kinds
        else:
            ok = False
        if not ok:
            bad_flags.append(nid)
    plan_targets = {r[0] for r in connection.execute("SELECT target_id FROM outreach_plans")} | {r[0] for r in connection.execute("SELECT organisation_id FROM outreach_plans")}
    reach = {r[0] for r in connection.execute("SELECT organisation_id FROM employer_reach")} if connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='employer_reach'").fetchone() else set()
    national_only_linked = [rid for rid in linked if records[rid].get("decision") == "national" and org_links.get(rid)]
    checks = {
        "national_source_rows_accounted": len(records) == len(linked) + len(skipped) and all(len(v) == 1 for v in links.values())
                                          and not (set(skipped) & set(linked)),
        "national_master_rows_linked": all(org_links.get(rid) for rid in to_master),
        "national_leads_not_organisations": not (set(leads) & (orgs | plan_targets | reach)) and not national_only_linked,
        "national_flags_consistent": not bad_flags,
    }
    summary = {
        "national_leads": len(leads), "flags": {f: sum(1 for x in leads.values() if x["flag"] == f) for f in ("in master", "in catchment", "national only")},
        "conservation": {"source_rows": len(records), "member_rows": member_rows, "index_rows": len(records) - member_rows,
                         "members_to_master_new": decisions.get("member:master_new", 0), "members_to_master_matched": decisions.get("member:master_match", 0),
                         "members_to_national": national_rows, "index_in_master": decisions.get("index:master_match", 0) + decisions.get("index:introducer_new", 0),
                         "index_national": decisions.get("index:national", 0), "index_skipped": len(skipped), "linked_to_a_national_lead": len(linked),
                         "check": f"{len(records)} source rows = {len(linked)} linked to a national lead + {len(skipped)} Index register rows skipped; "
                                  f"{member_rows} member rows = {decisions.get('member:master_new', 0)} new + {decisions.get('member:master_match', 0)} matched + "
                                  f"{national_rows} national"},
        "failing": {"flags": bad_flags[:10], "national_only_linked_to_an_organisation": national_only_linked[:10]},
    }
    return checks, summary


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
    vicoba, vicoba_summary = vicoba_checks(connection)
    national, national_summary = national_checks(connection)
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
        **vicoba,
        **national,
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
        "vicoba": vicoba_summary,
        "national_leads": national_summary,
        "unwanted_paths": unwanted,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
