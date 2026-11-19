#!/usr/bin/env python3
"""Merge the sector-association members workbook into the company master (one transaction): catchment members, enrichment of matched
records, bank head offices as escalation contacts, and the national leads table.

Reads what scripts/collection/build_association_members_intake.py wrote for one date:
- data/raw/association-members/master_intake_<date>.csv (run validate_intake.py and preflight_update.py on it first, CLAUDE.md 'Required
  order'): the rows that go to the master, new ('decision' master_new) and matched (master_match);
- data/raw/association-members/members_<date>.jsonl: every source row with its decision and national_lead_id;
- data/raw/association-members/bank_head_offices_<date>.json: each TBA bank's head office and the branch records it matches.
Run scripts/master/add_introducers.py --date <date> --keep-website-only --apply first, so the Index associations it adds exist.

In one transaction:
- the source workbook, the members file, the intake and the bank file go into source_files, and every source row (Index rows included)
  gets one source record: the tab, its source line and note, the sheet row and the row's values;
- a new catchment member becomes an organisation (segment and subtype from the intake: 'Safari / tour operator', 'Hotel', 'Microfinance
  lender', 'Savings group' with a SACCOS subtype ...), with its published routes, an entity_sources link per source row and the facts
  'member_of' (association and member category), licence number or class, status, district, region, catchment council, and every
  published email, phone, website and WhatsApp line. No point is written: the geolocation stage places it;
- a matched organisation is enriched, never overwritten: the same facts and link; an empty email, phone or website is filled only from a
  row placed in the catchment (or with no place given) and never from a bank's head office; a value that differs from the stored one is a
  fact plus a 'Multiple source values' review item; a non-operating licence on a matched record is a review item;
- a personal-domain inbox (free mail not named after the organisation; docs/methodology/contact-research.md) is never a route: it is kept
  as the fact 'email_personal_domain' (pdpa_risk risky) with a review item;
- a bank branch gets its head office (TBA tab: the Bank of Tanzania register's phone and email) as a role-desk contact 'Head office
  (escalation)', which resolve_master_recipients.py records as the branch plan's escalation contact; the branch stays the primary. A
  branch record that already carries the head office's route gets a review item instead (find the Arusha branch's own route);
- the national leads table (national_leads, national_lead_sources; documented in the lead-list data contract) holds every deduplicated
  member and every Index association with its flag: 'in master' (with organisation_id), 'in catchment' (became an organisation in this
  merge) or 'national only' (with its detail: in region, beyond catchment; in region, district not given; outside the region; region not
  given; non-operating). It is never an organisation: no plan, draft, segment, map pin or reach tier.
Checks before commit: integrity and foreign keys, every source row accounted for exactly once, no national-only row is an organisation,
every new organisation has a source link, and the organisation count equals before plus inserted. Preview by default
(runtime/master/association-members-preview.json); --apply writes. A re-run inserts no organisation, fact, review item or contact.
Afterwards: the geolocation stage (scripts/maps/collect_geocodes.py, apply_geocodes.py), recompute_campus_distances.py --apply,
rank_employer_reach.py --apply, then the full rebuild of skills/silverleaf-keep-outputs-current/SKILL.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "collection"))
import build_association_members_intake as B  # noqa: E402  (keys, free-mail and naming rules, the source tabs)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "association-members"
PREVIEW = ROOT / "runtime" / "master" / "association-members-preview.json"
HEAD_OFFICE_ROLE = "Head office (escalation)"
EMPLOYER_ANGLE = "Employer: a staff education benefit for its employees' children"
ANGLES = {"Microfinance lender": EMPLOYER_ANGLE + "; also a candidate introducer (some lenders finance school fees), not used as one yet",
          "Savings group": ""}
FLAGS = ("in master", "in catchment", "national only")
SCHEMA = """
CREATE TABLE IF NOT EXISTS national_leads (
  national_lead_id TEXT PRIMARY KEY, kind TEXT, name TEXT, associations TEXT, member_categories TEXT, licence_numbers TEXT, status TEXT,
  operating TEXT, phone TEXT, email TEXT, personal_inbox TEXT, website TEXT, whatsapp TEXT, physical_address TEXT, postal_address TEXT,
  district TEXT, region TEXT, flag TEXT, flag_detail TEXT, organisation_id TEXT REFERENCES organisations(organisation_id),
  source_rows INTEGER, notes TEXT, source_file TEXT, added_on TEXT);
CREATE TABLE IF NOT EXISTS national_lead_sources (
  national_lead_id TEXT REFERENCES national_leads(national_lead_id), record_id TEXT REFERENCES source_records(record_id), source_tab TEXT,
  sheet_row INTEGER, decision TEXT, PRIMARY KEY (national_lead_id, record_id));
"""


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def fact(con, oid, field, value, record, entity="organisation"):
    if value in (None, ""):
        return 0
    cur = con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                      (hid("X", entity, oid, field, value, record), entity, oid, field, str(value)[:2000], record))
    return cur.rowcount


def review(con, kind, oid, related, field, values, action, key=""):
    cur = con.execute('INSERT OR IGNORE INTO review (review_id, kind, entity_id, related_id, field, "values", action) VALUES (?,?,?,?,?,?,?)',
                      (hid("V", "association-members", kind, oid, related, field, key or values), kind, oid, related, field, str(values)[:500], action))
    return cur.rowcount


def register_file(con, path: Path, kind: str) -> str:
    body = path.read_bytes()
    sid = hid("F", "association-members", path.relative_to(ROOT).as_posix())
    con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                (sid, path.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), kind, "zlib", zlib.compress(body, 9)))
    return sid


def load(date: str):
    intake_path = RAW / f"master_intake_{date}.csv"
    members_path = RAW / f"members_{date}.jsonl"
    banks_path = RAW / f"bank_head_offices_{date}.json"
    intake = list(csv.DictReader(intake_path.open(encoding="utf-8-sig", newline="")))
    members = [json.loads(line) for line in members_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    banks = json.loads(banks_path.read_text(encoding="utf-8"))
    return intake_path, members_path, banks_path, intake, members, banks


def national_rows(members: list, orgs: dict) -> tuple[list, list]:
    """(national_leads rows, national_lead_sources rows) from the members file."""
    groups = defaultdict(list)
    for m in members:
        if m.get("national_lead_id"):
            groups[m["national_lead_id"]].append(m)
    leads, links = [], []
    for nid, rows in sorted(groups.items()):
        rows = sorted(rows, key=lambda r: (r["tab"] == "Index", r["row_id"]))
        first = rows[0]
        index = first["tab"] == "Index"
        matched = [r for r in rows if r["decision"] in ("master_match",) or (index and r["decision"] == "introducer_new")]
        new = [r for r in rows if r["decision"] == "master_new"]
        if matched and matched[0].get("organisation_id"):
            flag, oid = "in master", matched[0]["organisation_id"]
            detail = matched[0]["decision_detail"] if not index else (
                "introducer added in this merge" if matched[0]["decision"] == "introducer_new" else "introducer already in the master")
        elif new:
            flag, oid, detail = "in catchment", new[0]["organisation_id"], new[0]["decision_detail"]
        else:
            flag, oid = "national only", None
            detail = "; ".join(sorted({r["decision_detail"] for r in rows}))
        if oid and oid not in orgs:
            oid = None if flag == "national only" else oid
        f = [r.get("fields", {}) for r in rows]
        joined = lambda key: "; ".join(dict.fromkeys(x[key] for x in f if x.get(key)))  # noqa: E731
        emails = list(dict.fromkeys(e for x in f for e in x.get("emails", [])))
        personal = list(dict.fromkeys(e for x in f for e in x.get("personal_inboxes", [])))
        notes = [r["match_signal"] for r in rows if r.get("match_signal")]
        if any(x.get("contact_person_published") for x in f):
            notes.append("the TATO profile names a contact person (not copied here)")
        if index:
            notes.append(f"Sector {first.get('sector', '')}; members as published: {first.get('members_published', '')}; member list: "
                         f"{first.get('member_list', '')}; TPSF membership: {first.get('tpsf', '')}; source checked: {first.get('source_checked', '')}")
        leads.append({
            "national_lead_id": nid, "kind": "association" if index else "member", "name": first["name"],
            "associations": first["name"] if index else "; ".join(dict.fromkeys(x["association_acronym"] for x in f)),
            "member_categories": joined("member_category"), "licence_numbers": "; ".join(dict.fromkeys(x["licence_no"] for x in f if x.get("licence_no") and x.get("licence_no") not in ("A", "B"))),
            "status": joined("status"), "operating": "" if index else ("yes" if all(r.get("operating", True) for r in rows) else "no"),
            "phone": joined("phone"), "email": "; ".join(emails), "personal_inbox": "yes" if personal else "",
            "website": first.get("website", "") if index else joined("website"), "whatsapp": joined("whatsapp"),
            "physical_address": joined("physical_address"), "postal_address": joined("postal_address"), "district": joined("district"),
            "region": joined("region"), "flag": flag, "flag_detail": detail, "organisation_id": oid, "source_rows": len(rows),
            "notes": "; ".join(notes)[:1000]})
        for r in rows:
            links.append({"national_lead_id": nid, "row_id": r["row_id"], "source_tab": r["tab"], "sheet_row": r["sheet_row"], "decision": r["decision"]})
    return leads, links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default="2026-11-19")
    parser.add_argument("--database", type=Path, default=MASTER)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    intake_path, members_path, banks_path, intake, members, banks = load(args.date)
    con = sqlite3.connect(args.database)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    before = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("organisations", "contacts", "facts", "review", "source_records")}
    by_row = {m["row_id"]: m for m in members}

    new_orgs, matched_rows = defaultdict(list), []
    for r in intake:
        (new_orgs[r["new_organisation_id"]].append(r) if r["decision"] == "master_new" else matched_rows.append(r))
    leads, links = national_rows(members, {**orgs, **{k: {} for k in new_orgs}})
    rows_total = sum(1 for m in members)
    linked = Counter(l["row_id"] for l in links)
    skipped_rows = [m for m in members if not m.get("national_lead_id")]
    summary = {
        "date": args.date, "source_rows": rows_total, "member_rows": sum(1 for m in members if m["tab"] != "Index"),
        "index_rows": sum(1 for m in members if m["tab"] == "Index"),
        "rows_to_master_new": sum(len(v) for v in new_orgs.values()), "new_organisations": len(new_orgs),
        "rows_matched": len(matched_rows), "matched_organisations": len({r["match_organisation_id"] for r in matched_rows}),
        "new_by_segment": dict(Counter(v[0]["segment"] for v in new_orgs.values())),
        "national_leads": len(leads), "national_flags": dict(Counter(l["flag"] for l in leads)),
        "national_by_kind": dict(Counter(l["kind"] for l in leads)),
        "rows_without_national_lead": [m["row_id"] for m in skipped_rows],
        "conservation": {"source_rows": rows_total, "linked_to_a_national_lead": len(linked), "skipped (Index register rows)": len(skipped_rows),
                         "linked_twice": sum(1 for v in linked.values() if v > 1)},
        "banks_with_branches": sum(1 for b in banks["banks"] if b["branch_organisation_ids"]),
    }
    assert summary["conservation"]["linked_to_a_national_lead"] + len(skipped_rows) == rows_total, "a source row is not accounted for"
    missing_matches = sorted({r["match_organisation_id"] for r in matched_rows} - set(orgs))
    if missing_matches:
        raise SystemExit(f"Matched organisations not in the master: {missing_matches[:5]}")
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)

    stats = Counter()
    try:
        con.execute("BEGIN")
        for stmt in SCHEMA.strip().split(";"):
            if stmt.strip():
                con.execute(stmt)
        src = {"xlsx": register_file(con, B.SOURCE, "xlsx"),
               "members": register_file(con, members_path, "jsonl"), "intake": register_file(con, intake_path, "csv"),
               "banks": register_file(con, banks_path, "json")}
        record_of = {}
        for m in members:
            rid = hid("R", "association-members", args.date, m["row_id"])
            record_of[m["row_id"]] = rid
            payload = {k: v for k, v in m.items() if k not in ("similar_master",)}
            payload["source_file"] = B.SOURCE.relative_to(ROOT).as_posix()
            cur = con.execute("INSERT OR IGNORE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                              (rid, src["xlsx"], f"{B.SOURCE.name} {m['source_location']}: {m['name']}"[:500], json.dumps(payload, ensure_ascii=False)))
            stats["source_records"] += cur.rowcount

        def link(oid, row_id):
            cur = con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                              "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)",
                              (oid, record_of[row_id], oid, record_of[row_id]))
            stats["entity_links"] += cur.rowcount

        def row_facts(oid, r, m):
            """The facts every master row gives its organisation (new or matched)."""
            rec, f = record_of[r["source_row"]], m["fields"]
            n = fact(con, oid, "member_of", f"{f['association']} ({f['member_category']})", rec)
            n += fact(con, oid, "licence_no", f["licence_no"] if r["source_tab"] != "SACCOS (TCDC licensed)" else "", rec)
            n += fact(con, oid, "licence_class", f["licence_no"] if r["source_tab"] == "SACCOS (TCDC licensed)" else "", rec)
            n += fact(con, oid, "licence_status" if r["source_tab"] in ("Microfinance (Tier 2)", "SACCOS (TCDC licensed)") else "membership_status", f["status"], rec)
            n += fact(con, oid, "district", f["district"], rec) + fact(con, oid, "region", f["region"], rec)
            n += fact(con, oid, "catchment_council", r["catchment_council"], rec)
            n += fact(con, oid, "services", f["services"], rec) + fact(con, oid, "whatsapp", f["whatsapp"], rec)
            n += fact(con, oid, "postal_address", f["postal_address"], rec) + fact(con, oid, "physical_address", f["physical_address"], rec)
            for e in f["emails"]:
                if e in f["personal_inboxes"]:
                    n += fact(con, oid, "email_personal_domain", f"{e} (personal-domain inbox published by {m['source_url']} for the organisation; "
                                                                  "pdpa_risk risky; not a route until a person confirms it is the organisation's own)", rec)
                    stats["personal_inboxes"] += review(con, "Personal-domain inbox to confirm", oid, "", "email", e,
                                                        "The source publishes this free-mail inbox for the organisation, but it is not named after it: "
                                                        "confirm it is the organisation's own inbox before using it (it is not a route until then).")
                else:
                    n += fact(con, oid, "email", e, rec)
            n += fact(con, oid, "phone", f["phone"], rec) + fact(con, oid, "website", f["website"], rec)
            if f.get("contact_person_published"):
                stats["contact_person_reviews"] += review(con, "Association list: named contact on the member profile", oid, "", "contact",
                                                          f"{f['association']} profile names a contact person ({m['source_location']})",
                                                          "Read the member profile and add the person through the contact path (name_status, pdpa_risk).")
            return n

        # New organisations.
        for oid, rows in new_orgs.items():
            r0 = rows[0]
            m0 = by_row[r0["source_row"]]
            if oid not in orgs:
                verification = (f"Association list {args.date}: {r0['association']} ({'official register' if r0['evidence_basis'] == 'official' else 'member directory'}, "
                                f"compiled by the team, checked {B.CHECKED_ON}); unverified")
                notes = (f"{r0['association']} {r0['member_category']}{', licence ' + r0['licence_no'] if r0['licence_no'] and 'SACCOS' not in r0['source_tab'] else ''}; "
                         f"{r0['placement_basis']}; council {r0['catchment_council']} ({'core' if r0['council_core'] == 'yes' else 'non-core'}). "
                         f"Source: {r0['source_tab']} row {r0['sheet_row']} of {B.SOURCE.name}. No point yet: the geolocation stage places it."
                         + (f" Similar names in the master (review, not merged): {r0['similar_master_ids']}." if r0["similar_master_ids"] else ""))
                angle = ANGLES.get(r0["segment"], EMPLOYER_ANGLE)
                con.execute("""INSERT INTO organisations (organisation_id, name, segment, priority, campus, distance_km, size_evidence, address,
                               education_angle, source_url, verification, email, phone, subtype, radius_tier, website, notes, locality, licence_class)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (oid, r0["organisation_name"], r0["segment"], "", "", None, "", r0["address"], angle, r0["source_url"], verification,
                             r0["public_email"], r0["public_phone"], r0["subtype"], "", r0["website"], notes[:2000],
                             r0["locality"] or r0["catchment_council"], r0["licence_class"]))
                stats["organisations_inserted"] += 1
                orgs[oid] = {"organisation_id": oid, "name": r0["organisation_name"], "email": r0["public_email"], "phone": r0["public_phone"],
                             "website": r0["website"]}
                for sim in [x for x in r0["similar_master_ids"].split("; ") if x]:
                    stats["possible_duplicate_reviews"] += review(con, "Association list: possible duplicate", oid, sim, "name",
                                                                  f"{r0['organisation_name']} / {orgs.get(sim, {}).get('name', sim)}",
                                                                  "Similar name: decide whether these are one business (organisation-relations.json); never merged automatically.")
                if r0["source_tab"] == "TATO (Tour Operators)":
                    stats["tato_membership_reviews"] += review(con, "Association list: confirm membership", oid, "", "member_of",
                                                               "TATO's site holds 512 member profiles against a directory counter of about 270",
                                                               "Some TATO profiles may be lapsed: confirm the business operates before the first message.")
            for r in rows:
                link(oid, r["source_row"])
                stats["facts"] += row_facts(oid, r, by_row[r["source_row"]])

        # Matched organisations: enrich, never overwrite.
        for r in matched_rows:
            oid, m = r["match_organisation_id"], by_row[r["source_row"]]
            org, f = orgs[oid], m["fields"]
            link(oid, r["source_row"])
            stats["facts"] += row_facts(oid, r, m)
            placed = m["placement"]["placement"] in ("catchment", "unknown", "region_unplaced")
            head_office = r["source_tab"] in ("TBA (Bankers)",) or (r["source_tab"] == "Chamber of Mines" and not placed)
            own = [e for e in f["emails"] if e not in f["personal_inboxes"]]
            fills = {}
            if placed and not head_office:
                if own and not str(org.get("email") or "").strip():
                    fills["email"] = own[0]
                if f["phone"] and not str(org.get("phone") or "").strip():
                    fills["phone"] = f["phone"]
                if f["website"] and not str(org.get("website") or "").strip():
                    fills["website"] = f["website"]
            for col, value in fills.items():
                con.execute(f"UPDATE organisations SET {col}=? WHERE organisation_id=? AND COALESCE({col},'')=''", (value, oid))
                org[col] = value
                stats[f"filled_{col}"] += 1
            stored_mail = set(B.emails_of(org.get("email")))
            for e in own:
                if stored_mail and e not in stored_mail:
                    stats["conflicts_email"] += review(con, "Multiple source values", oid, "", "email", f"{org.get('email')} | {e} ({r['association_acronym']} list)",
                                                       "The association list gives another inbox (kept as a fact): decide which is current; the stored value stays."
                                                       + (" This is the head office's inbox." if head_office else ""))
            stored_phone = B.phone_keys(org.get("phone"))
            new_phone = B.phone_keys(f["phone"])
            if stored_phone and new_phone and not (new_phone <= stored_phone):
                stats["conflicts_phone"] += review(con, "Multiple source values", oid, "", "phone", f"{org.get('phone')} | {f['phone']} ({r['association_acronym']} list)",
                                                   "The association list gives another number (kept as a fact): decide which is current; the stored value stays."
                                                   + (" This is the head office's number." if head_office else ""))
            if f["website"] and B.domain(org.get("website")) and B.domain(f["website"]) and B.domain(f["website"]) != B.domain(org.get("website")):
                stats["conflicts_website"] += review(con, "Multiple source values", oid, "", "website", f"{org.get('website')} | {f['website']} ({r['association_acronym']} list)",
                                                     "The association list gives another website (kept as a fact): decide which is current; the stored value stays.")
            if not m.get("operating", True):
                stats["non_operating_reviews"] += review(con, "Licence non-operating (regulator list)", oid, "", "licence_status", f["status"],
                                                         "The regulator lists this licence as non-operating: hold any message until a person confirms the organisation operates.")

        # Index rows: an association the master holds (or add_introducers.py just added) is linked to its Index row, with its sector.
        for m in members:
            if m["tab"] == "Index" and m["decision"] in ("master_match", "introducer_new") and m.get("organisation_id") in orgs:
                link(m["organisation_id"], m["row_id"])
                stats["facts"] += fact(con, m["organisation_id"], "sector", m.get("sector", ""), record_of[m["row_id"]])
                stats["facts"] += fact(con, m["organisation_id"], "tpsf_membership", m.get("tpsf", ""), record_of[m["row_id"]])

        # Bank head offices: the escalation contact of each branch record.
        for b in banks["banks"]:
            rec = record_of[b["row_id"]]
            for oid in b["branch_organisation_ids"]:
                org = orgs[oid]
                same_mail = b["head_office_email"] and b["head_office_email"].lower() in set(B.emails_of(org.get("email")))
                same_phone = bool(B.phone_keys(b["head_office_phone"]) & B.phone_keys(org.get("phone")))
                if same_mail or same_phone:
                    stats["branch_carries_head_office_route"] += review(
                        con, "Branch record carries the head office's route", oid, "", "email; phone",
                        f"{org.get('email') or ''} {org.get('phone') or ''} = {b['bank']} head office (TBA list)",
                        "On-the-ground rule: find the Arusha branch's own route (Google Maps listing or the bank's branch page); the head office is the "
                        "escalation, not the primary.")
                    if same_mail and (not b["head_office_phone"] or same_phone):
                        continue  # escalating to the route the branch draft already uses would repeat it
                cid = hid("C", "bank-head-office", oid, B.name_key(b["bank"]))
                cur = con.execute("INSERT OR IGNORE INTO contacts (contact_id, organisation_id, name, role, campus, source_url, verification, shared_email, "
                                  "organisation_phone, contact_route, published_role_email, role_phone, named_email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                  (cid, oid, "", f"{HEAD_OFFICE_ROLE}: {b['bank']} head office, {b['head_office_region'] or 'Dar es Salaam'}", "",
                                   B.TABS["TBA (Bankers)"][3],
                                   f"Head office route from the Bank of Tanzania register (TBA member list in the team workbook, checked {B.CHECKED_ON}); "
                                   "role desk; escalation only, never the primary recipient", b["head_office_email"], b["head_office_phone"],
                                   "shared_email" if b["head_office_email"] else "organisation_phone", "", "", ""))
                stats["head_office_contacts"] += cur.rowcount
                con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'contact', ?, ? WHERE NOT EXISTS "
                            "(SELECT 1 FROM entity_sources WHERE entity_type='contact' AND entity_id=? AND record_id=?)", (cid, rec, cid, rec))
                fact(con, cid, "head_office_escalation", f"{b['bank']} head office: {b['head_office_email']} {b['head_office_phone']}".strip(), rec, "contact")

        # The national leads table: rebuilt from this date's members file (a re-run writes the same rows).
        source_file = B.SOURCE.relative_to(ROOT).as_posix()
        ids = [l["national_lead_id"] for l in leads]
        con.execute("DELETE FROM national_lead_sources WHERE national_lead_id IN (SELECT national_lead_id FROM national_leads WHERE source_file=?)", (source_file,))
        con.execute("DELETE FROM national_leads WHERE source_file=?", (source_file,))
        for l in leads:
            if l["organisation_id"] and l["organisation_id"] not in orgs:
                raise RuntimeError(f"national lead {l['national_lead_id']} points to a missing organisation {l['organisation_id']}")
            con.execute("""INSERT INTO national_leads (national_lead_id, kind, name, associations, member_categories, licence_numbers, status, operating, phone,
                           email, personal_inbox, website, whatsapp, physical_address, postal_address, district, region, flag, flag_detail, organisation_id,
                           source_rows, notes, source_file, added_on) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (l["national_lead_id"], l["kind"], l["name"], l["associations"], l["member_categories"], l["licence_numbers"], l["status"],
                         l["operating"], l["phone"], l["email"], l["personal_inbox"], l["website"], l["whatsapp"], l["physical_address"],
                         l["postal_address"], l["district"], l["region"], l["flag"], l["flag_detail"], l["organisation_id"], l["source_rows"],
                         l["notes"], source_file, args.date))
        for x in links:
            con.execute("INSERT INTO national_lead_sources (national_lead_id, record_id, source_tab, sheet_row, decision) VALUES (?,?,?,?,?)",
                        (x["national_lead_id"], record_of[x["row_id"]], x["source_tab"], x["sheet_row"], x["decision"]))
        stats["national_leads"] = len(ids)

        # Checks before commit.
        problems = []
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            problems.append("integrity check")
        if con.execute("PRAGMA foreign_key_check").fetchall():
            problems.append("foreign keys")
        after_orgs = con.execute("SELECT COUNT(*) FROM organisations").fetchone()[0]
        if after_orgs != before["organisations"] + stats["organisations_inserted"]:
            problems.append(f"organisations {after_orgs} != {before['organisations']} + {stats['organisations_inserted']}")
        if con.execute("SELECT COUNT(*) FROM national_leads n JOIN organisations o ON o.organisation_id = n.national_lead_id").fetchone()[0]:
            problems.append("a national lead ID is an organisation ID")
        if con.execute("SELECT COUNT(*) FROM national_leads WHERE flag='national only' AND organisation_id IS NOT NULL").fetchone()[0]:
            problems.append("a national-only lead carries an organisation")
        if con.execute("SELECT COUNT(*) FROM national_leads WHERE flag<>'national only' AND (organisation_id IS NULL OR organisation_id NOT IN "
                       "(SELECT organisation_id FROM organisations))").fetchone()[0]:
            problems.append("an in-master or in-catchment lead without its organisation")
        unlinked = con.execute("SELECT COUNT(*) FROM organisations o WHERE o.organisation_id IN (%s) AND NOT EXISTS (SELECT 1 FROM entity_sources e "
                               "WHERE e.entity_type='organisation' AND e.entity_id=o.organisation_id)" % ",".join("?" * len(new_orgs)), list(new_orgs)).fetchone()[0] if new_orgs else 0
        if unlinked:
            problems.append(f"{unlinked} new organisations without a source link")
        accounted = con.execute("SELECT COUNT(DISTINCT record_id) FROM national_lead_sources").fetchone()[0]
        if accounted + len(skipped_rows) != rows_total:
            problems.append(f"source rows: {accounted} linked + {len(skipped_rows)} skipped != {rows_total}")
        if problems:
            raise RuntimeError("; ".join(problems))
        summary["applied" if args.apply else "would_apply"] = dict(stats)
        summary["after"] = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("organisations", "contacts", "facts", "review", "source_records")}
        summary["before"] = before
        con.execute("COMMIT" if args.apply else "ROLLBACK")
    except Exception:
        con.execute("ROLLBACK")
        raise
    PREVIEW.write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    print("Applied." if args.apply else f"Preview only (rolled back): {PREVIEW.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
