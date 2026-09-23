#!/usr/bin/env python3
"""Merge a hook-research wave into the company master: lead briefs, verified first-message hooks and role checks.

Reads data/raw/hook-research/hooks_*_<date>.jsonl, which the research agents write (plan_hook_research.py briefs
them). Two stages:
- default: check every record and write runtime/hooks/apply-preview.json with what would change; nothing changes.
- --apply: one transaction, following silverleaf-update-lead-list:
  - Register each raw file in source_files, and one source record per organisation. Link it to the organisation and
    to the contacts whose roles it checked.
  - Replace the organisation's lead brief (table lead_briefs): one row per fact, with its source URL, page title and
    date, verbatim excerpt, the date it was read and its source record. A person can then learn about the lead quickly
    if they reply.
  - Set a verified hook on every outreach plan for the organisation, when the record's hook passes the checks below.
  - Record each contact's role check:
    - a confirmed role is noted on the contact;
    - a changed or missing role becomes a review item and holds that contact's drafts;
    - a page that cannot be read becomes a review item only.
    A later confirmation removes the review item and the hold.
  - Research notes that warn of a closure, a lost website or a duplicate become review items. A possible closure also
    holds the organisation's drafts, as the contact merge does.
Use --database to try it on a copy; its report then stays in runtime/. Afterwards run draft_master_messages.py (the hook
enters the first message), refresh_acquisition_metadata.py, npm run build:workbook and verify_master.py.

A hook is used only when all of these hold:
- the cited fact was read on the page (fetched), with a URL and a verbatim excerpt;
- every number in the sentence appears in that excerpt;
- the sentence states no offer terms and breaks no offer-register rule;
- it mentions no parents or families;
- it has at most 40 words.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import zlib
from collections import Counter
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import contact_lib as C  # noqa: E402  (research-note warnings)
from merge_master_contacts import BLOCKER, CLOSURE_NOTE, drop_note, with_note  # noqa: E402  (the same holds as the contact merge)

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
RAW = ROOT / "data" / "raw" / "hook-research"
WORK = ROOT / "runtime" / "hooks"
FACT_TYPES = {"what_they_do", "workforce", "locations", "education_programme", "community_programme", "staff_welfare", "growth", "recognition",
              "other"}
HOOK_TYPES = {"workforce", "staff_welfare", "education_programme", "community_programme", "locality", "growth"}
ROLE_CHECKS = {"confirmed", "changed", "not_found", "unreachable"}
FAMILY = re.compile(r"\b(parents?|famil(?:y|ies)|kids|mothers?|fathers?|households?)\b", re.I)
ROLE_NOTE = "Role not confirmed by hook research; confirm who holds the role before any message."
# A role hold is released only when nothing else holds the draft.
HOLD = re.compile(BLOCKER.pattern + r"|Role not confirmed|No public email or phone|No published route", re.I)
NOTE_ACTION = "Research raised this while checking the lead; a person must review it before any message."


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def merge_ids(existing, new: str) -> str:
    return "; ".join(dict.fromkeys([x.strip() for x in str(existing or "").split(";") if x.strip()] + [new]))


def text(value, limit: int = 0) -> str:
    out = " ".join(str(value or "").split())
    return out[:limit] if limit else out


def load(run_date: str) -> tuple[list[Path], dict, list[str]]:
    """The raw files, the last record per organisation, and any unreadable lines."""
    files = sorted(RAW.glob(f"hooks_*_{run_date}.jsonl"))
    records, problems = {}, []
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                problems.append(f"{path.name}:{number}: not JSON ({exc.msg})")
                continue
            records[record.get("organisation_id")] = (path, record)
    return files, records, problems


def coordinator_review(run_date: str) -> dict:
    """The coordinator's review, data/raw/hook-research/coordinator-review_<date>.json:
    - "hooks" maps an organisation_id to a decision on its proposed hook:
      - {"decision": "reject", "reason": "..."}: the hook is not used, and the reason is recorded;
      - {"decision": "revise", "sentence": "...", "reason": "..."}: the revised sentence replaces the proposed one and must
        pass the same checks against the same cited fact.
    - "checks" lists points the agents raised for a person ({"organisation_id", "check"}); each becomes a review item."""
    path = RAW / f"coordinator-review_{run_date}.json"
    review = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return {"hooks": review.get("hooks", {}), "checks": review.get("checks", [])}


def check(record: dict, name: str, contact_ids: set, review: dict | None = None) -> tuple[dict, list[str]]:
    """The record reduced to what can be used, and the reasons anything was left out."""
    problems, kept, index = [], [], {}
    for i, fact in enumerate(record.get("brief") or []):
        url, excerpt = text(fact.get("source_url")), text(fact.get("excerpt"))
        if not re.match(r"https?://\S+$", url) or not excerpt or not fact.get("fetched") or not text(fact.get("fact")):
            problems.append(f"{name}: fact {i} left out (it needs a page read live, its URL and a verbatim excerpt)")
            continue
        index[i] = len(kept)
        kept.append({"type": fact.get("type") if fact.get("type") in FACT_TYPES else "other", "fact": text(fact.get("fact"), 400),
                     "source_url": url, "source_title": text(fact.get("source_title"), 300), "source_date": text(fact.get("source_date"), 40),
                     "accessed_on": text(fact.get("accessed_on"), 40), "excerpt": excerpt[:600]})
    hook, rejected = None, ""
    proposed = record.get("hook")
    if proposed and not name.startswith("Rivertrees"):
        revised = (review or {}).get("decision") == "revise" and text((review or {}).get("sentence"))
        sentence = revised or text(proposed.get("sentence"))
        at = proposed.get("fact_index")
        fact = kept[index[at]] if isinstance(at, int) and at in index else None
        numbers = re.findall(r"\d[\d,.]*\d|\d", sentence)
        if (review or {}).get("decision") == "reject":
            rejected = f"the coordinator's review: {review.get('reason', 'rejected')}"
        elif not sentence or not fact:
            rejected = "its fact is missing or was left out"
        elif any(n.replace(",", "") not in fact["excerpt"].replace(",", "") for n in numbers):
            rejected = "a number in the sentence is not in the excerpt"
        elif L.check_first_message(sentence) or L.check_message(sentence, []):
            rejected = "it states offer terms or breaks an offer-register rule"
        elif FAMILY.search(sentence):
            rejected = "it mentions parents or families"
        elif len(sentence.split()) > 40:
            rejected = "it is longer than 40 words"
        else:
            hook = {"sentence": sentence if sentence.endswith((".", "!")) else sentence + ".",
                    "type": proposed.get("type") if proposed.get("type") in HOOK_TYPES else "other",
                    "quality": proposed.get("quality") if proposed.get("quality") in ("strong", "moderate") else "moderate", "fact": fact}
        if rejected:
            problems.append(f"{name}: hook not used ({rejected}): {sentence[:140]}")
    checks = []
    for c in record.get("contacts") or []:
        if c.get("contact_id") not in contact_ids:
            problems.append(f"{name}: role check for an unknown contact {c.get('contact_id')} left out")
            continue
        checks.append({"contact_id": c["contact_id"], "name": text(c.get("name"), 200), "role_on_record": text(c.get("role_on_record"), 300),
                       "role_check": c.get("role_check") if c.get("role_check") in ROLE_CHECKS else "unreachable",
                       "role_published": text(c.get("role_published"), 300), "source_url": text(c.get("source_url"), 500),
                       "excerpt": text(c.get("excerpt"), 400), "accessed_on": text(c.get("accessed_on"), 40)})
    clean = {"organisation_id": record.get("organisation_id"), "organisation_name": name, "status": text(record.get("status"), 20),
             "searches_used": record.get("searches_used"), "brief": kept, "hook": hook, "hook_rejected": rejected, "contacts": checks,
             "notes": text(record.get("notes"), 1200)}
    return clean, problems


def write_manifest() -> None:
    """data/raw/hook-research/MANIFEST.md: every raw research file with its SHA-256, as the other raw evidence folders keep."""
    rows = []
    for path in sorted(RAW.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.md":
            rel = path.relative_to(RAW).as_posix()
            kind = ("Coverage log: pages read, queries, blocks and gaps" if rel.startswith("coverage/") else
                    "Coordinator review: decisions on proposed hooks and checks for a person" if rel.startswith("coordinator-review_") else
                    "Research records: lead brief, hook and role checks per organisation")
            rows.append(f"| `{rel}` | `{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}…` | {kind} |")
    (RAW / "MANIFEST.md").write_text(
        "# Hook research raw evidence\n\nResearch behind the first-message hooks and lead briefs of the company master's named leads. Planned by "
        "`scripts/messaging/plan_hook_research.py`, merged by `scripts/messaging/apply_hook_research.py`; the method is in "
        "`skills/silverleaf-outreach/references/hook-guidance.md`. Every fact carries its source URL, page title, verbatim excerpt and the date "
        "it was read. Nothing here holds page text beyond those excerpts, anything about children, or anyone's private details.\n\n"
        "| File | SHA-256 | Contents |\n|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")


def release(con, message_id: str, stats: Counter) -> None:
    plan = con.execute("SELECT missing_information FROM outreach_plans WHERE message_id=?", (message_id,)).fetchone()
    if plan and ROLE_NOTE in str(plan["missing_information"] or ""):
        rest = drop_note(plan["missing_information"], ROLE_NOTE)
        con.execute("UPDATE outreach_plans SET review_status=?, missing_information=? WHERE message_id=?",
                    ("Needs research" if HOLD.search(rest) else "Draft review", rest, message_id))
        stats["plans_released_role_confirmed"] += 1


def add_checks(con, checks: list, names: dict, stats: Counter) -> None:
    """The coordinator's list of points for a person to check, each as a review item on its organisation."""
    for item in checks:
        oid, note = item.get("organisation_id"), text(item.get("check"), 600)
        if oid in names and note:
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (hid("D", "hook-check", oid, note), "Hook research: check before outreach", oid, "", "research note", note, NOTE_ACTION))
            stats["reviews"] += 1


def apply(con, files: list[Path], clean: list[dict], run_date: str, stats: Counter) -> None:
    con.execute("""CREATE TABLE IF NOT EXISTS lead_briefs (brief_id TEXT PRIMARY KEY,
                   organisation_id TEXT NOT NULL REFERENCES organisations(organisation_id), position INTEGER, fact_type TEXT,
                   fact TEXT NOT NULL, source_url TEXT NOT NULL, source_title TEXT, source_date TEXT, excerpt TEXT NOT NULL, accessed_on TEXT,
                   record_id TEXT NOT NULL REFERENCES source_records(record_id))""")
    source_ids = {}
    for path in files:
        body = path.read_bytes()
        sid = hid("F", "hook-research", path.name)
        con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                    (sid, path.relative_to(ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), "jsonl", "zlib", zlib.compress(body, 9)))
        source_ids[path.name] = sid
        stats["source_files"] += 1
    for r in clean:
        oid, path = r["organisation_id"], r.pop("_path")
        record = hid("R", "hook-research", run_date, oid)
        con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                    (record, source_ids[path.name], f"hook research {oid} ({run_date})", json.dumps(r, ensure_ascii=False)))
        for entity_type, entity_id in [("organisation", oid)] + [("contact", c["contact_id"]) for c in r["contacts"]]:
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT ?,?,? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_type=? AND entity_id=? AND record_id=?)",
                        (entity_type, entity_id, record, entity_type, entity_id, record))
        # The brief is replaced as a whole: it shows the latest research, and earlier waves stay in their source records.
        con.execute("DELETE FROM lead_briefs WHERE organisation_id=?", (oid,))
        for position, f in enumerate(r["brief"], 1):
            con.execute("INSERT INTO lead_briefs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (hid("B", oid, f["source_url"], f["excerpt"]), oid, position, f["type"], f["fact"], f["source_url"], f["source_title"],
                         f["source_date"], f["excerpt"], f["accessed_on"] or run_date, record))
            stats["brief_facts"] += 1
        plans = con.execute("SELECT message_id, target_type, target_id, evidence_record_ids FROM outreach_plans WHERE organisation_id=?",
                            (oid,)).fetchall()
        if r["hook"]:
            h, f = r["hook"], r["hook"]["fact"]
            for p in plans:
                con.execute("""UPDATE outreach_plans SET hook=?, hook_status=?, hook_type=?, hook_quality=?, hook_version=?, hook_evidence=?,
                               evidence_url=?, verified_on=?, evidence_basis=?, evidence_record_ids=? WHERE message_id=?""",
                            (h["sentence"], f"Verified {f['accessed_on'] or run_date}", h["type"], h["quality"], f"{run_date}-hook-research",
                             f"\"{f['excerpt']}\" ({f['source_title'] or 'page'}, read {f['accessed_on'] or run_date})", f["source_url"],
                             f["accessed_on"] or run_date, f"Hook research {run_date}: {f['type'].replace('_', ' ')} fact read live on the page cited",
                             merge_ids(p["evidence_record_ids"], record), p["message_id"]))
                stats["plans_with_hook"] += 1
            stats["organisations_with_hook"] += 1
        for c in r["contacts"]:
            cid, review_id = c["contact_id"], hid("D", "hook-role", c["contact_id"])
            contact_plans = [p["message_id"] for p in plans if p["target_type"] == "contact" and p["target_id"] == cid]
            stats[f"role_{c['role_check']}"] += 1
            if c["role_check"] == "confirmed":
                note = f"role confirmed {c['accessed_on'] or run_date} ({c['source_url']})"
                con.execute("UPDATE contacts SET verification = COALESCE(verification,'') || ? WHERE contact_id=? AND COALESCE(verification,'') NOT LIKE ?",
                            (f"; {note}", cid, f"%{note}%"))
                con.execute("DELETE FROM review WHERE review_id=?", (review_id,))
                for mid in contact_plans:
                    release(con, mid, stats)
                continue
            # "changed" can mean a new role for the same person (still listed, e.g. promoted), or that someone else now holds it.
            first_name = (L.greeting_name(c["name"]).split() or [""])[0].lower()
            still_listed = c["role_check"] == "changed" and c["role_published"] and first_name and first_name in c["excerpt"].lower()
            if c["role_check"] == "unreachable":
                kind, action = ("Hook research: role source unreadable",
                                "The page this contact came from could not be read when the research re-checked it. Confirm the role from "
                                "another source before relying on it.")
            elif still_listed:
                kind, action = ("Hook research: role changed",
                                f"The page cited now lists this person as '{c['role_published']}'. Confirm the current role and update the "
                                "contact; the drafts do not mention the role, so they are not held.")
                for mid in contact_plans:
                    release(con, mid, stats)
            else:
                kind, action = ("Hook research: role not confirmed",
                                "Research could not confirm this person in this role on the page cited. Confirm who holds the role before "
                                "any message; the contact's drafts are held until then.")
                for mid in contact_plans:
                    mi = con.execute("SELECT missing_information FROM outreach_plans WHERE message_id=?", (mid,)).fetchone()[0]
                    con.execute("UPDATE outreach_plans SET review_status='Needs research', missing_information=? WHERE message_id=?",
                                (with_note(ROLE_NOTE, mi), mid))
                    stats["plans_held_role_not_confirmed"] += 1
            con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                        (review_id, kind, oid, cid, "role",
                         f"{c['name']}: {c['role_on_record']} | now: {c['role_published'] or 'not on the page'} | {c['source_url']}"[:400], action))
            stats["reviews"] += 1
        for kind, note in C.note_flags(r["notes"]):
            if kind == "possible closure":
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "hook-closure", oid), "Possible closure", oid, "", "status", note[:400],
                             "Hook research found a sign that this organisation has closed. Confirm it still operates before any outreach; "
                             "archive it if it has closed."))
                for p in plans:
                    mi = con.execute("SELECT missing_information FROM outreach_plans WHERE message_id=?", (p["message_id"],)).fetchone()[0]
                    con.execute("UPDATE outreach_plans SET review_status='Needs research', missing_information=? WHERE message_id=?",
                                (with_note(CLOSURE_NOTE, mi), p["message_id"]))
                    stats["plans_held_for_closure"] += 1
            else:
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "hook-note", oid, kind), f"Hook research: {kind}", oid, "", "research note", note[:400], NOTE_ACTION))
            stats["reviews"] += 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--database", default=str(MASTER), help="the master database (a temporary copy for a trial run)")
    args = parser.parse_args()
    files, records, problems = load(args.date)
    if not files:
        raise SystemExit(f"No hook-research files for {args.date} in {RAW.relative_to(ROOT)}.")
    database = Path(args.database)
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    names = dict(con.execute("SELECT organisation_id, name FROM organisations").fetchall())
    contacts_by_org = {}
    for cid, oid in con.execute("SELECT contact_id, organisation_id FROM contacts"):
        contacts_by_org.setdefault(oid, set()).add(cid)
    clean, review = [], coordinator_review(args.date)
    for oid, (path, record) in sorted(records.items(), key=lambda kv: str(kv[0])):
        if oid not in names:
            problems.append(f"{record.get('organisation_name')}: unknown organisation_id {oid}; left out")
            continue
        r, issues = check(record, names[oid], contacts_by_org.get(oid, set()), review["hooks"].get(oid))
        problems += issues
        r["_path"] = path
        clean.append(r)
    preview = {"date": args.date, "files": [f.relative_to(ROOT).as_posix() for f in files], "organisations": len(clean),
               "facts": sum(len(r["brief"]) for r in clean), "hooks": sum(1 for r in clean if r["hook"]),
               "role_checks": dict(Counter(c["role_check"] for r in clean for c in r["contacts"])), "problems": problems,
               "leads": [{"organisation": r["organisation_name"], "facts": len(r["brief"]), "hook": (r["hook"] or {}).get("sentence", ""),
                          "hook_rejected": r["hook_rejected"], "roles": {c["name"]: c["role_check"] for c in r["contacts"]}} for r in clean]}
    WORK.mkdir(parents=True, exist_ok=True)
    if not args.apply:
        con.close()
        (WORK / "apply-preview.json").write_text(json.dumps(preview, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({k: preview[k] for k in ("organisations", "facts", "hooks", "role_checks")}, indent=1))
        print(f"{len(problems)} items left out; details in runtime/hooks/apply-preview.json")
        return 0
    write_manifest()
    stats = Counter()
    try:
        con.execute("BEGIN")
        apply(con, files, clean, args.date, stats)
        add_checks(con, review["checks"], names, stats)
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        enabled = con.execute("SELECT COUNT(*) FROM automation_configuration WHERE enabled=1").fetchone()[0]
        if integrity != "ok" or fks or enabled:
            raise RuntimeError({"integrity": integrity, "foreign_keys": [tuple(x) for x in fks[:5]], "enabled_automations": enabled})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    stats["lead_briefs_after"] = con.execute("SELECT COUNT(*) FROM lead_briefs").fetchone()[0]
    con.close()
    trial = database.resolve() != MASTER.resolve()
    report = (WORK / "trial-apply.json") if trial else (ROOT / "outputs" / "messages" / "hook-research-apply.json")
    earlier = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
    applications = earlier.get("applications", [])
    applications.append({"run_date": args.date, "applied_on": date.today().isoformat(), "trial": trial, **dict(stats), "left_out": problems})
    report.write_text(json.dumps({"applications": applications}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(stats), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
