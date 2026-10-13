#!/usr/bin/env python3
"""Idempotently classify current outreach plans into Silverleaf acquisition tracks.

AQ00 while a plan is held; AQ02 for a case B plan (a named person reached only through a general inbox, whose first message
draft_master_messages.py writes in the Attn format), whose three touches are AQ02's (decided 11 October 2026), except variant A
sponsorship; otherwise AQ01 for a referral call to action and AQ02 for the rest. draft_master_messages.track_for applies the same rule.

Value modules by segment: savings groups (offer_lib.SAVINGS_SEGMENTS) are never given the employer modules. VICOBA group plans get
VM02; VM03; VM06; VM20 (and VM19 once they hold an offer message), VICOBA introducer requests VM02; VM03; VM20 (they state no terms;
docs/plans/vicoba-integration-plan.md decision 4).

VICOBA design records (decided 13 October 2026; all design only and disabled, like every flow and campaign here): the value module VM20
'Weekly-meeting talk', flow F26 'VICOBA introduction to weekly-meeting talk' (outreach_flows), campaign C12 'VICOBA acquisition' with its
touchpoints, and a C12 campaign assignment for every VICOBA plan. No automation configuration is added or enabled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
import offer_lib as L  # noqa: E402  (SAVINGS_SEGMENTS and the VICOBA segments)

DEFAULT_DB = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
VERSION = "2026-09-09-new-contact-acquisition-v4"
DESIGN_ONLY = "Design only; not activated"
SCOPE = "New-contact acquisition; track-selected and independent of the internal marketing calendar."

VM20 = ("VM20", "Savings groups (VICOBA)", "Weekly-meeting talk",
        "Members hear a short Kiswahili talk at their own weekly meeting on getting children ready for school and planning their education; "
        "each member decides for themselves whether to ask for more.",
        "A 10-15 minute talk in Kiswahili after the group's own business, a parent booklet and a voluntary paper form or QR code with the "
        "group's VIC- partner code.",
        "The committee agrees a slot at one weekly meeting; the group decides.",
        "VICOBA group plans and introducer requests (F26, campaign C12).",
        "No loan, subsidy, fee financing or term beyond the offer register; no member list, photographs, gifts or payments; no "
        "unannounced visit to a meeting.",
        "PE023; PE024", "Design only; not activated; Kiswahili native-speaker review before use")
# F26 (decision 4): the introducer first, then the committee, then the talk. (step, trigger, condition, action, delay, database update,
# example copy, principle)
F26 = [
    (1, "Introducer request ready for the wave", "Group record complete; introducer linked; a CDO only after the council's introduction "
     "(GA01, government run); one request per introducer per wave; women's groups first",
     "Send the VICOBA introducer plan's request (subject and body)", "Day 0 after checks", "awaiting_reply; campaign_id=C12",
     "Ask the introducer to introduce Silverleaf to one or two group committees; no member list; no offer terms",
     "One request per introducer per wave; women's groups first"),
    (2, "Introducer request delivered; no reply", "No reply, refusal or opt-out", "Call the introducer's office, then deliver a letter by hand",
     "2 working days after delivery", "last_step=2", "Ask once who works with the groups; never for a list",
     "Silence is never a 'no'; then dormant (dormant_no_route)"),
    (3, "Introducer introduced the group, or an officer agreed to be contacted",
     "The group's Kiswahili template version approved (data/reference/kiswahili-reviews.json); group band high",
     "Deliver the group plan's Kiswahili letter (subject and body) through the introducer, or call the officer first (case A)",
     "After the introduction", "awaiting_reply; audience=committee",
     "Ask the committee for 10-15 minutes at one weekly meeting; no offer terms", "Request first, in Kiswahili"),
    (4, "Group letter delivered; no reply", "F01 stop checks pass", "Send follow_up_1 (the check-in), then follow_up_2 (the close)",
     "4 working days after delivery, then 4 more", "sequence_complete",
     "Ask whether the committee would like the talk; then close until the next savings cycle", "Then dormant (dormant_no_response)"),
    (5, "Committee replied", "Reply recorded", "Send the Kiswahili offer message (offer_message_sw; English meaning in offer_message)",
     "Next working day", "conversation", "The family offer and the group rate for savings groups (OF07) exactly as the offer register records them",
     "No loan, subsidy or fee-financing claim"),
    (6, "Committee agreed a slot", "Talk content, booklet and opt-in form approved",
     "Hold the 10-15 minute Kiswahili talk at the weekly meeting, before the group's share-out", "On the agreed date",
     "slot_held; partner code VIC-", "Members opt in themselves with the group's VIC- code; no photographs, gifts or payments",
     "S7 win: slot_held or circulation_partner"),
]
C12 = ("C12", "VICOBA acquisition", "Community savings groups (VICOBA, VSLA) in the catchment, through their introducers and committees",
       "VICOBA members; VICOBA introducers",
       "A short Kiswahili talk at one weekly meeting of each group; members opt in themselves with the group's VIC- code.",
       "Design only", "Introducer email or letter; hand-delivered Kiswahili letter; a call to a published officer route",
       "F26", "Marketing and Partnership Coordinator (Mariam Haji)",
       "Marketing Lead; native-speaker reviewer for Kiswahili; check with Finance before the first offer message",
       "Agree a 10-15 minute slot at one weekly meeting", "Kiswahili for groups (native-speaker review before release); English for NGO and "
       "bank introducers",
       "Record complete; introducer linked; council introduction (GA01) recorded for CDO routes; Kiswahili template version approved; "
       "women's groups first; never a member list",
       "Draft; design only; not activated",
       "docs/plans/vicoba-integration-plan.md decisions 3 to 6 (approved 13 October 2026); VM02; VM03; VM06; VM20; PE023; PE024")


def sid(*parts) -> str:
    return "A" + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def vicoba_records(connection) -> None:
    """VM20, F26, C12 and its touchpoints (design only), and a C12 assignment for every VICOBA plan; idempotent."""
    connection.execute("INSERT OR REPLACE INTO value_proposition_modules VALUES (?,?,?,?,?,?,?,?,?,?)", VM20)
    connection.execute("DELETE FROM outreach_flows WHERE flow_id='F26'")
    connection.executemany("INSERT INTO outreach_flows (flow_id, step, trigger, condition, action, delay, database_update, example_copy, principle, mode) "
                           "VALUES ('F26',?,?,?,?,?,?,?,?,?)", [(*row, DESIGN_ONLY) for row in F26])
    connection.execute("INSERT OR REPLACE INTO campaigns VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", C12)
    connection.execute("DELETE FROM campaign_touchpoints WHERE campaign_id='C12'")
    connection.executemany("INSERT INTO campaign_touchpoints (campaign_id, touchpoint_order, flow_id, flow_step, timing, trigger, purpose, channel, "
                           "audience_state, draft_copy, evidence_ids, status) VALUES ('C12',?,'F26',?,?,?,?,?,?,?,?,?)",
                           [(step, step, delay, trigger, action, "Introducer route, or the group letter by hand" if step != 1 else "Introducer route",
                             condition, example, "PE023; PE024", DESIGN_ONLY) for step, trigger, condition, action, delay, _, example, _ in F26])
    marks = ",".join("?" * len(L.VICOBA_SEGMENTS))
    for mid, ttype, tid, selection, status in connection.execute(
            f"SELECT message_id, target_type, target_id, selection, review_status FROM outreach_plans WHERE segment IN ({marks})",
            tuple(sorted(L.VICOBA_SEGMENTS))).fetchall():
        held = status == "Needs research"
        connection.execute("INSERT OR IGNORE INTO campaign_lead_assignments (assignment_id, campaign_id, target_type, target_id, message_id, selection, "
                           "eligibility_status, reason, next_action, acquisition_track_id, value_module_ids, strategy_scope) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                           (sid("vicoba-c12", mid), "C12", ttype, tid, mid, selection, "", "", "", "", "", SCOPE))
        connection.execute("UPDATE campaign_lead_assignments SET selection=?, eligibility_status=?, reason=?, next_action=? WHERE assignment_id=?",
                           (selection, "Needs research" if held else "Candidate after checks",
                            "VICOBA plan (F26): one request per introducer per wave; women's groups first",
                            "Resolve the holds in the plan's notes" if held else "Human review, then the F26 step for this plan",
                            sid("vicoba-c12", mid)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    connection.execute("PRAGMA foreign_keys=ON")
    before = connection.execute("SELECT COUNT(*) FROM outreach_plans").fetchone()[0]
    savings = ",".join(f"'{s}'" for s in sorted(L.SAVINGS_SEGMENTS - {L.VICOBA_GROUP_SEGMENT}))
    with connection:
        connection.execute(
            f"""
            UPDATE outreach_plans
            SET acquisition_version=?,
                acquisition_track_id=CASE
                  WHEN review_status='Needs research' THEN 'AQ00'
                  WHEN subject LIKE 'Attn:%' AND COALESCE(message_variant,'') NOT LIKE 'A%' THEN 'AQ02'
                  WHEN cta_type LIKE '%Referral%' THEN 'AQ01'
                  ELSE 'AQ02' END,
                value_module_ids=CASE
                  WHEN segment=? THEN 'VM02; VM03; VM06; VM20' || CASE WHEN COALESCE(offer_message,'')<>'' THEN '; VM19' ELSE '' END
                  WHEN segment=? THEN 'VM02; VM03; VM20'
                  ELSE CASE
                    WHEN segment IN ({savings}) THEN 'VM01; VM02; VM03; VM06'
                    WHEN segment='Education employers' THEN 'VM01; VM02; VM03; VM05; VM07'
                    ELSE 'VM01; VM02; VM03; VM04; VM05' END
                  || CASE WHEN COALESCE(offer_version,'')<>'' THEN '; VM19' ELSE '' END END,
                strategy_scope='New-contact acquisition. Approved Silverleaf positioning may be reused where relevant; the acquisition track controls cadence.'
            """,
            (VERSION, L.VICOBA_GROUP_SEGMENT, L.VICOBA_INTRODUCER_SEGMENT),
        )
        vicoba_records(connection)
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
        active_design = connection.execute(
            "SELECT (SELECT COUNT(*) FROM outreach_flows WHERE flow_id='F26' AND mode<>?) + "
            "(SELECT COUNT(*) FROM campaign_touchpoints WHERE campaign_id='C12' AND status<>?)", (DESIGN_ONLY, DESIGN_ONLY)
        ).fetchone()[0]
        if integrity != "ok" or foreign_keys or unassigned or enabled or active_design or sum(counts.values()) != before:
            raise RuntimeError({"integrity": integrity, "foreign_keys": foreign_keys[:5], "unassigned": unassigned, "enabled_automations": enabled,
                                "active_vicoba_design_rows": active_design})
    vicoba = connection.execute("SELECT COUNT(*) FROM campaign_lead_assignments WHERE campaign_id='C12'").fetchone()[0]
    connection.close()
    print(json.dumps({"status": "refreshed", "database": str(args.database.resolve()), "plans": before, "tracks": counts,
                      "vicoba_c12_assignments": vicoba, "sending_enabled": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
