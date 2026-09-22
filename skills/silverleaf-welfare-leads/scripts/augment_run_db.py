#!/usr/bin/env python3
"""Add welfare side tables to a run database created by initialize_lead_db.py, in one transaction.

Adds organisation_relationships, registry_ngos and research_coverage, loads review items into `review`, registers
every raw evidence file (path and SHA-256) in source_files, and records run metadata. Rolls back on any failed check.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3

import welfare_lib as W

SCHEMA = """
CREATE TABLE IF NOT EXISTS organisation_relationships (
  relationship_id TEXT PRIMARY KEY, from_organisation TEXT NOT NULL, to_organisation TEXT NOT NULL,
  from_organisation_id TEXT, to_organisation_id TEXT, relationship_type TEXT NOT NULL, verification_status TEXT,
  pdpa_risk TEXT, notes TEXT, sources_json TEXT,
  FOREIGN KEY (from_organisation_id) REFERENCES organisations(organisation_id),
  FOREIGN KEY (to_organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS registry_ngos (
  nis_id TEXT PRIMARY KEY, name TEXT NOT NULL, welfare_relevance TEXT, welfare_fit TEXT, relevance_signal TEXT, matched_organisation TEXT,
  matched_organisation_id TEXT, reg_no TEXT, reg_date TEXT, level TEXT, region TEXT, district TEXT, years_experience TEXT,
  latest_project_end TEXT, nearest_campus_registry_coords TEXT, distance_km_registry_coords REAL, latitude REAL, longitude REAL,
  profile_url TEXT, profile_fetched INTEGER, vision TEXT, projects_json TEXT,
  FOREIGN KEY (matched_organisation_id) REFERENCES organisations(organisation_id)
);
CREATE TABLE IF NOT EXISTS research_coverage (slice TEXT NOT NULL, line_no INTEGER NOT NULL, text TEXT, PRIMARY KEY (slice, line_no));
"""


def sid(prefix: str, *parts) -> str:
    return f"{prefix}_{hashlib.sha256('|'.join(str(p) for p in parts).encode()).hexdigest()[:16]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    work, raw = cfg["paths"]["work"], cfg["paths"]["raw"]
    final = json.loads((work / "final.json").read_text(encoding="utf-8"))
    reviews = json.loads((work / "review_items.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(cfg["paths"]["db"])
    con.execute("PRAGMA foreign_keys=ON")
    org_ids = {W.name_key(name): oid for oid, name in con.execute("SELECT organisation_id, name FROM organisations")}
    try:
        con.executescript("BEGIN;" + SCHEMA)
        for r in final["relationships"]:
            f, t = r.get("from_organisation", ""), r.get("to_organisation", "")
            con.execute("INSERT OR REPLACE INTO organisation_relationships VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sid("REL", W.name_key(f), W.name_key(t), r.get("relationship_type")), f, t, org_ids.get(W.name_key(f)), org_ids.get(W.name_key(t)),
                         r.get("relationship_type") or "partners_with", r.get("verification_status"), r.get("pdpa_risk") or "low",
                         W.norm_text(r.get("notes")), json.dumps(r.get("sources", []), ensure_ascii=False)))
        for n in final["nis"]:
            matched = str(n.get("matched_organisation", "")).replace(" (added from register)", "")
            con.execute("INSERT OR REPLACE INTO registry_ngos VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (str(n["nis_id"]), n["name"], n["welfare_relevance"], n.get("welfare_fit", ""), n["relevance_signal"], n.get("matched_organisation", ""),
                         org_ids.get(W.name_key(matched)) if matched else None, n["reg_no"], n["reg_date"], n["level"], n["region"], n["district"],
                         n["years_experience"], n["latest_project_end"], n["nearest_campus_registry_coords"], n["distance_km_registry_coords"],
                         float(n["latitude"]) if n.get("latitude") else None, float(n["longitude"]) if n.get("longitude") else None,
                         n["profile_url"], 1 if n["profile_fetched"] else 0, n["vision"], json.dumps(n.get("projects", []), ensure_ascii=False)))
        for item in reviews:
            entity = str(item.get("entity") or "")
            con.execute("INSERT OR REPLACE INTO review VALUES (?,?,?,?,?,?,?,?)",
                        (sid("REV", item.get("kind"), entity, json.dumps(item.get("detail"), default=str, sort_keys=True)), item.get("kind"),
                         "organisation" if W.name_key(entity) in org_ids else "research", org_ids.get(W.name_key(entity), entity),
                         item.get("related", ""), json.dumps(item.get("detail"), ensure_ascii=False, default=str), item.get("action", ""), "open"))
        for path in sorted((raw / "coverage").glob("*_coverage.md")):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                con.execute("INSERT OR REPLACE INTO research_coverage VALUES (?,?,?)", (path.stem.replace("_coverage", ""), n, line))
        for path in sorted(p for p in raw.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
            digest = W.sha256_file(path)
            mime = "application/json" if path.suffix in (".json", ".jsonl") else "text/markdown" if path.suffix == ".md" else "text/plain"
            con.execute("INSERT OR IGNORE INTO source_files VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (f"SRC_{digest[:16]}", path.relative_to(W.ROOT).as_posix(), "", digest, mime, cfg["research_date"], None))
        metadata = {"run_id": args.run_id, "lead_track": "welfare_customer", "research_date": cfg.get("research_period", cfg["research_date"]),
                    "scope": cfg.get("scope", "Welfare institutions near Silverleaf's campuses; research only, no outreach drafted."),
                    "exclusions": "No child-level data; no data on parents or relatives of children in care; no cross-source profiling of individuals.",
                    "risk_labels": "pdpa_risk low | medium | risky on every organisation, contact and enquiry row (see intake extra columns)."}
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
              ("organisations", "contacts", "enquiries", "organisation_relationships", "registry_ngos", "review", "research_coverage", "source_records", "source_files")}
    con.close()
    print(json.dumps({"database": str(cfg["paths"]["db"].relative_to(W.ROOT)), "status": "augmented", "counts": counts}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
