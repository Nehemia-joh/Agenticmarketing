#!/usr/bin/env python3
"""Add the government side tables to a run database created by initialize_lead_db.py, in one transaction.

Adds the tables from plans/b2b-government-leads-plan.md §5.2 (admin_units, government_office_profiles,
official_posts and community_events, which holds counts only and has no person-level columns), plus office_triage,
master_triage and convening_signals. Loads review items into `review`, registers every raw evidence file (path and
SHA-256) in source_files and records run metadata. Rolls back on any failed check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3

import gov_lib as G

W = G.W
SCHEMA = """
CREATE TABLE IF NOT EXISTS admin_units (
  unit_key TEXT PRIMARY KEY, level TEXT NOT NULL, name TEXT NOT NULL, council TEXT NOT NULL, region TEXT, admin_district TEXT,
  core_council INTEGER, population_2022 INTEGER, male_2022 INTEGER, female_2022 INTEGER, households_2022 INTEGER,
  avg_household_size_2022 REAL, census_table TEXT, census_pdf_page INTEGER, census_printed_page TEXT, census_row INTEGER,
  census_source_location TEXT, census_url TEXT, latitude REAL, longitude REAL, geocode_precision TEXT, location_source TEXT,
  location_ref TEXT, location_url TEXT, location_note TEXT, campus TEXT, distance_km REAL, transport_band TEXT,
  nearest_primary_campus TEXT, distance_to_primary_km REAL, primary_band TEXT, campus_cluster TEXT, in_catchment TEXT,
  ward_score REAL, ward_tier TEXT, rank_in_cluster INTEGER, factors_known TEXT, score_factors TEXT, office_organisation_id TEXT,
  FOREIGN KEY (office_organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS government_office_profiles (
  organisation_id TEXT PRIMARY KEY, record_key TEXT NOT NULL, office_level TEXT NOT NULL, admin_unit_key TEXT, admin_unit_name TEXT,
  parent_admin_unit TEXT, council_name TEXT, region TEXT, convening_forum TEXT, protocol_status TEXT NOT NULL DEFAULT 'none',
  protocol_ref TEXT, proposed_government_track TEXT, track_reason TEXT, last_verified_on TEXT, master_organisation_id TEXT, osm_id TEXT,
  FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id),
  FOREIGN KEY (admin_unit_key) REFERENCES admin_units(unit_key)
);
CREATE TABLE IF NOT EXISTS official_posts (
  post_id TEXT PRIMARY KEY, contact_id TEXT NOT NULL, organisation_id TEXT NOT NULL, record_key TEXT NOT NULL, post_key TEXT NOT NULL,
  office_title TEXT NOT NULL, office_title_sw TEXT, appointment_type TEXT NOT NULL, holder_name TEXT, holder_verified_on TEXT,
  tenure_source_url TEXT, b2g_check_required TEXT, convening_role TEXT, pdpa_risk TEXT NOT NULL, pdpa_risk_reason TEXT,
  FOREIGN KEY (contact_id) REFERENCES contacts(contact_id),
  FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS community_events (
  event_code TEXT PRIMARY KEY, organisation_id TEXT NOT NULL, event_type TEXT NOT NULL, event_date TEXT, event_status TEXT NOT NULL,
  expected_attendance INTEGER CHECK (expected_attendance >= 0), attendance_estimate INTEGER CHECK (attendance_estimate >= 0),
  attendance_method TEXT, opt_ins INTEGER CHECK (opt_ins >= 0), enquiries INTEGER CHECK (enquiries >= 0), tours INTEGER CHECK (tours >= 0),
  applications INTEGER CHECK (applications >= 0), enrolments INTEGER CHECK (enrolments >= 0), cost_tzs INTEGER CHECK (cost_tzs >= 0),
  FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS office_triage (
  triage_id TEXT PRIMARY KEY, source TEXT NOT NULL, source_id TEXT NOT NULL, name TEXT, category TEXT NOT NULL, detail TEXT, tags TEXT,
  osm_district TEXT, latitude REAL, longitude REAL, campus TEXT, distance_km REAL, linked_organisation_id TEXT, note TEXT,
  FOREIGN KEY (linked_organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS master_triage (
  master_organisation_id TEXT PRIMARY KEY, name TEXT NOT NULL, master_campus TEXT, master_distance_km REAL, category TEXT NOT NULL,
  detail TEXT, triage_group TEXT NOT NULL, proposed_treatment TEXT NOT NULL, matched_osm_id TEXT, linked_organisation_id TEXT,
  FOREIGN KEY (linked_organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS convening_signals (
  signal_id TEXT PRIMARY KEY, organisation TEXT NOT NULL, host TEXT NOT NULL, kind TEXT NOT NULL, item_id TEXT, item_date TEXT,
  title TEXT NOT NULL, tags TEXT, listing_url TEXT
);
"""


def sid(prefix: str, *parts) -> str:
    return f"{prefix}_{hashlib.sha256('|'.join(str(p) for p in parts).encode()).hexdigest()[:16]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = G.load_config(args.run_id)
    work, raw, date = cfg["paths"]["work"], cfg["paths"]["raw"], cfg["research_date"]
    final = json.loads((work / "final.json").read_text(encoding="utf-8"))
    reviews = json.loads((work / "review_items.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(cfg["paths"]["db"])
    con.execute("PRAGMA foreign_keys=ON")
    ids = {}
    for entity_type, eid, payload in con.execute("SELECT es.entity_type, es.entity_id, sr.payload_json FROM entity_sources es "
                                                 "JOIN source_records sr ON sr.source_record_id = es.source_record_id"):
        ids[json.loads(payload).get("record_key")] = eid
    try:
        con.executescript("BEGIN;" + SCHEMA)
        office_by_unit = {o["unit_key"]: ids.get(o["record_key"]) for o in final["offices"] if o.get("unit_key")}
        for u in final["admin_units"]:
            office = office_by_unit.get(u["record_key"])
            con.execute("INSERT INTO admin_units VALUES (" + ",".join("?" * 39) + ")",
                        (u["record_key"], u["level"], u["name"], u["council"], u["region"], u["admin_district"], 1 if u["core_council"] else 0,
                         u["population_2022"], u["male_2022"], u["female_2022"], u["households_2022"], u["avg_household_size_2022"],
                         u["census_table"], u["census_pdf_page"], str(u["census_printed_page"]), u["census_row"], u["census_source_location"],
                         u["census_url"], u["lat"], u["lon"], u["geocode_precision"], u["location_source"], u["location_ref"], u["location_url"],
                         u["location_note"], u["campus"], u["distance_km"], u["transport_band"], u["nearest_primary_campus"],
                         u["distance_to_primary_km"], u["primary_band"], u["campus_cluster"], u["in_catchment"], u.get("ward_score"),
                         u.get("ward_tier"), u.get("rank_in_cluster"), u.get("factors_known"), u.get("score_factors"), office))
        for o in final["offices"]:
            con.execute("INSERT INTO government_office_profiles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (ids[o["record_key"]], o["record_key"], o["office_level"], o.get("unit_key"), o.get("admin_unit_name"),
                         o.get("parent_admin_unit"), o.get("council_name"), o.get("region"), o.get("convening_forum"), "none", "",
                         o["proposed_government_track"], o["track_reason"], date if o["verification_status"] == "verified" else "",
                         o.get("master_organisation_id", ""), o.get("osm_id", "")))
        for p in final["posts"]:
            con.execute("INSERT INTO official_posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sid("POST", p["record_key"]), ids[p["record_key"]], ids[p["office_key"]], p["record_key"], p["post_key"], p["office_title"],
                         p["office_title_sw"], p["appointment_type"], p.get("holder_name", ""), p.get("holder_verified_on", ""),
                         p.get("tenure_source_url", ""), p["b2g_check_required"], p["convening_role"], p["pdpa_risk"], p["pdpa_risk_reason"]))
        for t in final["office_triage"]:
            con.execute("INSERT INTO office_triage VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sid("TRI", t["source"], t["source_id"]), t["source"], t["source_id"], t["name"], t["category"], t["detail"], t["tags"],
                         t["osm_district"], t["lat"], t["lon"], t["campus"], t["distance_km"], ids.get(t["linked_office"]) if t["linked_office"] else None,
                         t["note"]))
        for m in final["master_triage"]:
            con.execute("INSERT INTO master_triage VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (m["master_organisation_id"], m["name"], m["master_campus"], m["master_distance_km"], m["category"], m["detail"], m["group"],
                         m["proposed_treatment"], m["matched_osm_id"], ids.get(m["linked_office"]) if m["linked_office"] else None))
        for s in final["signals"]:
            con.execute("INSERT OR IGNORE INTO convening_signals VALUES (?,?,?,?,?,?,?,?,?)",
                        (sid("SIG", s["host"], s["kind"], s["item_id"]), s["organisation"], s["host"], s["kind"], str(s["item_id"]), s["date"],
                         s["title"], s["tags"], s["listing_url"]))
        for item in reviews:
            entity = str(item.get("entity") or "")
            con.execute("INSERT OR REPLACE INTO review VALUES (?,?,?,?,?,?,?,?)",
                        (sid("REV", item.get("kind"), entity, json.dumps(item.get("detail"), default=str, sort_keys=True)), item.get("kind"),
                         "government_run", entity, item.get("related", ""), json.dumps(item.get("detail"), ensure_ascii=False, default=str),
                         item.get("action", ""), "open"))
        for path in sorted(p for p in raw.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
            digest = W.sha256_file(path)
            mime = {".json": "application/json", ".csv": "text/csv", ".md": "text/markdown"}.get(path.suffix, "text/plain")
            con.execute("INSERT OR IGNORE INTO source_files VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (f"SRC_{digest[:16]}", path.relative_to(G.ROOT).as_posix(), "", digest, mime, date, None))
        metadata = {"run_id": args.run_id, "lead_track": "government_convener", "research_date": cfg.get("research_period", date),
                    "scope": cfg.get("scope", ""),
                    "exclusions": "No party offices, courts, police, prisons, military, health facilities, schools or religious sites; no resident, "
                                  "voter, beneficiary or pupil lists; no parent data; no party affiliation.",
                    "risk_labels": "pdpa_risk low | medium | risky on every office and post row (see intake extra columns).",
                    "tracks": "GA00 Hold, GA01 Protocol introduction, GA02 Convening request (proposed only; no outreach planned)."}
        for key, value in metadata.items():
            con.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?)", (key, value))
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fks:
            raise RuntimeError({"integrity": integrity, "foreign_keys": fks[:10]})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
              ("organisations", "contacts", "admin_units", "government_office_profiles", "official_posts", "community_events", "office_triage",
               "master_triage", "convening_signals", "review", "source_records", "source_files")}
    con.close()
    print(json.dumps({"database": str(cfg["paths"]["db"].relative_to(G.ROOT)), "status": "augmented", "counts": counts}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
