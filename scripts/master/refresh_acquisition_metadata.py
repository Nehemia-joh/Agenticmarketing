#!/usr/bin/env python3
"""Idempotently classify current outreach plans into Silverleaf acquisition tracks."""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
VERSION = "2026-09-09-new-contact-acquisition-v4"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    connection.execute("PRAGMA foreign_keys=ON")
    before = connection.execute("SELECT COUNT(*) FROM outreach_plans").fetchone()[0]
    with connection:
        connection.execute(
            """
            UPDATE outreach_plans
            SET acquisition_version=?,
                acquisition_track_id=CASE
                  WHEN review_status='Needs research' THEN 'AQ00'
                  WHEN cta_type LIKE '%Referral%' THEN 'AQ01'
                  ELSE 'AQ02' END,
                value_module_ids=CASE
                  WHEN segment='SACCOS members' THEN 'VM01; VM02; VM03; VM06'
                  WHEN segment='Education employers' THEN 'VM01; VM02; VM03; VM05; VM07'
                  ELSE 'VM01; VM02; VM03; VM04; VM05' END
                  || CASE WHEN COALESCE(offer_version,'')<>'' THEN '; VM19' ELSE '' END,
                strategy_scope='New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the acquisition track controls cadence.'
            """,
            (VERSION,),
        )
        connection.execute(
            """
            UPDATE campaign_lead_assignments
            SET acquisition_track_id=(SELECT p.acquisition_track_id FROM outreach_plans p WHERE p.message_id=campaign_lead_assignments.message_id),
                value_module_ids=(SELECT p.value_module_ids FROM outreach_plans p WHERE p.message_id=campaign_lead_assignments.message_id),
                strategy_scope=CASE WHEN target_type='enquiry'
                  THEN 'Parent-enquiry flow; outside the organisation acquisition framework.'
                  ELSE 'New-contact acquisition; track-selected and independent of the internal marketing calendar.' END
            """
        )
        counts = dict(connection.execute(
            "SELECT acquisition_track_id,COUNT(*) FROM outreach_plans GROUP BY acquisition_track_id"
        ))
        connection.execute(
            """
            INSERT OR REPLACE INTO acquisition_refresh_runs
              (run_id,ran_on,acquisition_version,outreach_plan_count,hold_count,routing_count,direct_count,notes)
            VALUES (?,?,?,?,?,?,?,?)
            """,
            (f"refresh-{date.today().isoformat()}", date.today().isoformat(), VERSION, before,
             counts.get("AQ00", 0), counts.get("AQ01", 0), counts.get("AQ02", 0),
             "Idempotent metadata refresh; no messages sent."),
        )
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        unassigned = connection.execute(
            "SELECT COUNT(*) FROM outreach_plans WHERE COALESCE(acquisition_track_id,'')=''"
        ).fetchone()[0]
        enabled = connection.execute(
            "SELECT COUNT(*) FROM automation_configuration WHERE enabled=1"
        ).fetchone()[0]
        if integrity != "ok" or foreign_keys or unassigned or enabled or sum(counts.values()) != before:
            raise RuntimeError({"integrity": integrity, "foreign_keys": foreign_keys[:5], "unassigned": unassigned, "enabled_automations": enabled})
    connection.close()
    print(json.dumps({"status": "refreshed", "database": str(args.database.resolve()), "plans": before, "tracks": counts, "sending_enabled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
