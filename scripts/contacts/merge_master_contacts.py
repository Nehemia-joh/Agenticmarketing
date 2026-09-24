#!/usr/bin/env python3
"""Merge contact research into the company master, following silverleaf-update-lead-list.

Reads runtime/contacts/profiles.json (build_contact_profiles.py). Two stages:
- default: write the shared-contract intake (runtime/contacts/master-contact-intake.csv), then run the create skill's
  validator and the read-only update preflight, and print both reports. Nothing changes.
- --apply: in one transaction, register the raw research files and one source record per organisation, fill only
  empty organisation fields (website, email, phone, address), record every found value as a fact, send conflicting
  values to review, insert the new named contacts with their evidence, and move held drafts (AQ00) whose only gap was
  a missing route to 'Draft review'. Run scripts/messaging/draft_master_messages.py and
  scripts/master/refresh_acquisition_metadata.py afterwards so the new contacts get drafts and tracks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import zlib
from datetime import date
from pathlib import Path

import contact_lib as C

W = C.W
MASTER = C.ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
ROUTE_GAP_PARTS = {"No public email or phone", "find the organisation's route before any message.", "No contact channel recorded"}
# Held-plan notes that are real blockers, not reminders: a new route does not release these.
BLOCKER = re.compile(r"Raw OpenStreetMap place|organisation or branch overlap|Confirm current operation and committee|member-association rate|"
                     r"Finance must agree to extend|Possible closure|Route unconfirmed|Outside the|excluded", re.I)
CLOSURE_NOTE = "Possible closure found by contact research; confirm the organisation still operates before any message."
NOTE_ACTIONS = {"hijacked or parked site": "The organisation's former website or inbox now belongs to someone else; never use it. Confirm the current route.",
                "location to check": "Research places the organisation elsewhere than the database does; confirm its location before outreach.",
                "website gone": "The recorded website no longer resolves; find the current route.",
                "fit to check": "Research suggests the organisation may not serve the audience this list assumes; confirm the fit before outreach.",
                "segment to check": "Research says the organisation is a different kind of business than its segment records (for example a "
                                    "hospital recorded as a tour operator); correct the segment through the update skill and check its drafts.",
                "possible duplicate": "Research suggests this is the same organisation as another record; confirm, then merge through the update skill.",
                "check before outreach": "Research raised a concern; a person must review it before any outreach."}


def hid(prefix: str, *parts) -> str:
    return prefix + hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def domain(value) -> str:
    """The host of a website value, or '' when the field holds free text (some directory imports carry slogans or phones)."""
    m = re.search(r"(?:https?://)?(?:www\.)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)+)", str(value or "").lower())
    return m.group(1) if m and not re.fullmatch(r"[\d.\-]+", m.group(1)) else ""


def org_named(email: str, org_name: str) -> bool:
    """A mailbox named after the organisation (e.g. kiriwetravel@gmail.com for Kiriwe Travel), not after a person."""
    local = re.sub(r"[^a-z]", "", email.split("@")[0].lower())
    tokens = [t for t in re.findall(r"[a-z]{5,}", org_name.lower()) if t not in ("limited", "company", "tanzania", "africa", "african", "safaris",
                                                                                  "safari", "tours", "travel", "adventures", "adventure")]
    return bool(tokens) and any(t in local for t in tokens)


def best_email(profile, org_name: str = "") -> str:
    """The organisation's own inbox: a role or general address, else a personal-domain inbox named after the organisation.
    A person's named address stays with that person's contact record."""
    for kind in ("role", "general"):
        for e in profile["emails"]:
            if e["type"] == kind:
                return e["email"]
    return next((e["email"] for e in profile["emails"] if e["type"] == "personal_domain" and org_named(e["email"], org_name)), "")


UNSUPPORTED_NOTE = "Route unconfirmed: the only evidence for it is no longer usable; confirm it from another source before any message."


def drop_note(text, note: str) -> str:
    """The field without one note. Notes are stored joined with '; ', and several notes contain '; ' themselves, so a
    note is removed whole, never by splitting the field and comparing parts."""
    return "; ".join(n for n in str(text or "").replace(note, "").split("; ") if n.strip())


def with_note(note: str, text) -> str:
    rest = drop_note(text, note)
    return f"{note}; {rest}" if rest else note


def unsupported_routes(con, oid, org, profile, record, stats) -> None:
    """Flag an email or phone an earlier wave filled when no current evidence supports it any more (for example, a site
    whose robots.txt now disallows crawling, or a value found to be a template placeholder). Nothing is deleted: the value stays, a review item explains it, and
    drafts that use it are held until someone confirms it. Runs before the research facts are replaced."""
    digits = lambda s: re.sub(r"\D", "", str(s or ""))  # noqa: E731
    earlier = {str(v).lower() for (v,) in con.execute("SELECT value FROM facts WHERE entity_type='organisation' AND entity_id=? AND record_id=?",
                                                      (oid, record))}
    other = [str(v).lower() for (v,) in con.execute(
        "SELECT value FROM facts WHERE entity_type='organisation' AND entity_id=? AND record_id NOT IN "
        "(SELECT record_id FROM source_records WHERE location LIKE 'contact profile %')", (oid,))]
    current = {e["email"].lower() for e in profile["emails"]} | {digits(x["phone"]) for x in profile["phones"]}
    for field, value in (("email", org["email"]), ("phone", org["phone"])):
        key = str(value or "").lower() if field == "email" else digits(value)
        if key and key in current:
            resolve_unconfirmed(con, oid, field, value, stats)  # supported again: clear an earlier flag and its hold
        if not key or key in current or not any(key in (e if field == "email" else digits(e)) for e in earlier):
            continue
        if any(key in (o if field == "email" else digits(o)) for o in other):
            continue  # another source record supports it
        con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                    (hid("D", "contact-unsupported", oid, field), "Contact research: route unconfirmed", oid, "", field, str(value),
                     "An earlier research wave filled this value, and no current evidence supports it (for example, the site's robots.txt "
                     "now disallows crawling). Confirm it from another source; drafts that use it are held until then."))
        for plan in con.execute("SELECT message_id, missing_information FROM outreach_plans WHERE organisation_id=? AND contact_channel=?",
                                (oid, value)).fetchall():
            con.execute("UPDATE outreach_plans SET review_status='Needs research', missing_information=? WHERE message_id=?",
                        (with_note(UNSUPPORTED_NOTE, plan["missing_information"]), plan["message_id"]))
            stats["plans_held_for_unconfirmed_route"] += 1
        stats["reviews"] += 1


def resolve_unconfirmed(con, oid, field, value, stats) -> None:
    """Undo an earlier 'route unconfirmed' flag once current evidence supports the value again: remove the review item and
    release the drafts it held, unless another blocker still holds them."""
    review_id = hid("D", "contact-unsupported", oid, field)
    if not con.execute("SELECT 1 FROM review WHERE review_id=?", (review_id,)).fetchone():
        return
    con.execute("DELETE FROM review WHERE review_id=?", (review_id,))
    for plan in con.execute("SELECT message_id, missing_information FROM outreach_plans WHERE organisation_id=? AND contact_channel=? "
                            "AND missing_information LIKE ?", (oid, value, f"{UNSUPPORTED_NOTE}%")).fetchall():
        rest = drop_note(plan["missing_information"], UNSUPPORTED_NOTE)
        status = "Needs research" if BLOCKER.search(rest) or any(gap in rest for gap in ROUTE_GAP_PARTS) else "Draft review"
        con.execute("UPDATE outreach_plans SET review_status=?, missing_information=? WHERE message_id=?", (status, rest, plan["message_id"]))
        stats["plans_released_route_confirmed"] += 1


ROBOTS_ACTION = ("The site's robots.txt could not be read when it was crawled (server, network or certificate error). By decision, such sites "
                 "are crawled anyway and their details used; check the site's own terms if in doubt.")
ROBOTS_BROWSER_ACTION = ("The site's robots.txt disallows crawling. By the user's decision (24 September 2026) its public pages were read with a "
                         "browser, as a visitor would, and everything taken from them is tagged risky (pdpa_risk risky on its people). Check the "
                         "site's own terms before relying on it.")
NAME_ACTION = ("The source gives only part of this person's name. The lead is kept, labelled incomplete, rather than dropped (the user's "
               "decision, 24 September 2026); find the full name from the organisation before relying on it. Drafts are not held.")
# Crawl-flag kind -> (review ID part, review kind, action). The first keeps the ID earlier merges gave it.
ROBOTS_REVIEWS = {"robots.txt unreachable": ("contact-robots", "Contact research: robots.txt unreachable", ROBOTS_ACTION),
                  "robots.txt disallows": ("contact-robots-browser", "Contact research: robots.txt disallows (read with a browser)",
                                           ROBOTS_BROWSER_ACTION)}


def repair_research_emails(con, stats) -> None:
    """An address an earlier wave recorded with page junk around it (a URL-encoded space, a zero-width character, a word
    glued onto the domain) is replaced by the same address, cleaned, wherever that wave put it: the contacts it added,
    an organisation field it filled, and the drafts that use it. Runs before the research facts are replaced."""
    earlier = {v for (v,) in con.execute("SELECT DISTINCT f.value FROM facts f JOIN source_records s ON s.record_id=f.record_id "
                                         "WHERE f.field LIKE 'email%' AND s.location LIKE 'contact profile %'")}
    added = con.execute("SELECT contact_id, shared_email, named_email FROM contacts WHERE verification LIKE 'Published by the organisation (%'").fetchall()
    earlier |= {str(r[f] or "") for r in added for f in ("shared_email", "named_email")}
    for value in sorted(v for v in earlier if v and v.count("@") == 1):
        cleaned = C.clean_email(value)
        if not cleaned or cleaned == value:
            continue
        for r in added:
            for field in ("shared_email", "named_email"):
                if r[field] == value:
                    con.execute(f"UPDATE contacts SET {field}=? WHERE contact_id=?", (cleaned, r["contact_id"]))
                    stats["research_emails_cleaned"] += 1
        stats["research_emails_cleaned"] += con.execute("UPDATE organisations SET email=? WHERE email=?", (cleaned, value)).rowcount
        stats["research_emails_cleaned"] += con.execute("UPDATE outreach_plans SET contact_channel=? WHERE contact_channel=?", (cleaned, value)).rowcount


def best_phone(profile) -> str:
    for kind in ("office", "mobile", "international", "unknown"):
        for p in profile["phones"]:
            if p["type"] == kind:
                return p["phone"]
    return ""


def raw_files(run_date: str) -> list:
    files = [C.RAW / f"website_contacts_{run_date}.jsonl", C.RAW / f"osm_contacts_{run_date}.json"]
    files += sorted(C.RAW.glob(f"search_*_{run_date}.jsonl")) + sorted(C.RAW.glob(f"browser_*_{run_date}.jsonl"))
    return [f for f in files if f.exists()]


def record_files(run_date: str) -> dict:
    """organisation_id -> the agent and browser files that hold a record for it (the source file of its source records)."""
    out = {}
    for path in raw_files(run_date):
        if not path.name.startswith(("search_", "browser_")):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                oid = json.loads(line).get("organisation_id") if line.strip() else None
            except json.JSONDecodeError:
                oid = None
            if oid and path.name not in out.setdefault(oid, []):
                out[oid].append(path.name)
    return out


def file_for(method: str, oid: str, by_org: dict, source_ids: dict, run_date: str) -> str:
    """The raw file a finding came from: the crawl file, else this organisation's browser or search record file."""
    if method == "website":
        return f"website_contacts_{run_date}.jsonl"
    prefix = "browser_" if method == "browser" else "search_"
    return next((n for n in by_org.get(oid, []) if n.startswith(prefix)),
                next((n for n in source_ids if n.startswith(prefix)), f"osm_contacts_{run_date}.json"))


def intake(profiles, run_date, orgs) -> list[dict]:
    headers = next(csv.reader(open(W.TEMPLATE, encoding="utf-8-sig")))
    rows = []
    for p in profiles:
        org = orgs[p["organisation_id"]]
        source = p["sources"][0] if p["sources"] else {}
        base = {h: "" for h in headers}
        base.update({"source_path": "runtime/contacts/profiles.json", "source_location": f"profile {p['organisation_id']}",
                     "source_url": source.get("url", ""), "acquired_on": run_date, "verified_on": run_date,
                     "verification_status": "verified" if source.get("fetched") else "unverified", "evidence_basis": "published",
                     "organisation_name": org["name"], "locality": org["locality"] or ""})
        email, phone = best_email(p, org["name"]), best_phone(p)
        website = p["websites"][0] if p["websites"] else ""
        if (email and not org["email"]) or (phone and not org["phone"]) or (website and not org["website"]):
            row = dict(base)
            row.update({"record_type": "organisation", "website": website if website.startswith("http") else "", "public_email": email,
                        "public_phone": phone, "evidence_excerpt": f"Published contact routes for {org['name']} ({', '.join(p['methods'])})"})
            rows.append(row)
        for person in p["people"]:
            if person["already_in_database"] or person.get("identity") == "uncertain":
                continue
            named = person["email"] if person["email"] and not W.PERSONAL_EMAIL.search(person["email"]) else ""
            row = dict(base)
            row.update({"record_type": "contact", "source_url": person["source_url"] or base["source_url"],
                        "verification_status": "verified" if person.get("fetched") else "unverified",
                        "evidence_excerpt": (person.get("excerpt") or f"{person['name']}, {person['role']}")[:200],
                        "contact_name": person["name"], "role": person["role"], "role_certainty": "confirmed",
                        "named_email": named, "shared_email": "" if named else (email or ""),
                        "role_phone": person["phone"] if person["phone"] else "", "organisation_phone": phone or org["phone"] or "",
                        "profile_url": person["source_url"] if str(person["source_url"]).startswith("http") else "",
                        "contact_route": "named_email" if named else ("shared_email" if email else ("organisation_phone" if (phone or org["phone"]) else "profile_url")),
                        "channel_attribution": f"Published by the organisation ({person['method']}); pdpa_risk {person['pdpa_risk']}"})
            if row["contact_route"] == "profile_url" and not row["profile_url"]:
                row["contact_route"] = "source_url"
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--database", default=str(MASTER), help="the master database (a temporary copy for a trial run)")
    args = parser.parse_args()
    data = json.loads((C.WORK / "profiles.json").read_text(encoding="utf-8"))
    run_date = data["date"]
    researched = {oid for (oid,) in sqlite3.connect(f"file:{Path(args.database).resolve().as_posix()}?mode=ro", uri=True).execute(
        "SELECT substr(location, 17, instr(substr(location, 17), ' ') - 1) FROM source_records WHERE location LIKE 'contact profile %'")}
    # Organisations with findings, warnings, or an earlier research record (whose facts must be brought up to date).
    profiles = [p for p in data["profiles"] if p["db"] == "master" and (p["emails"] or p["phones"] or p["websites"] or p["people"] or p["postal"]
                                                                          or C.note_flags(p.get("notes")) or p["organisation_id"] in researched)]
    database = Path(args.database)
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    rows = intake(profiles, run_date, orgs)
    intake_path = C.WORK / "master-contact-intake.csv"
    headers = next(csv.reader(open(W.TEMPLATE, encoding="utf-8-sig")))
    with open(intake_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    if not args.apply:
        con.close()
        validate = subprocess.run([sys.executable, str(W.CREATE_SCRIPTS / "validate_intake.py"), str(intake_path), "--report",
                                   str(C.WORK / "master-contact-validation.json")], capture_output=True, text=True, encoding="utf-8")
        preflight = subprocess.run([sys.executable, str(C.ROOT / "skills" / "silverleaf-update-lead-list" / "scripts" / "preflight_update.py"),
                                    str(database), str(intake_path), "--report", str(C.WORK / "master-contact-preflight.json")],
                                   capture_output=True, text=True, encoding="utf-8")
        print(validate.stdout[-1500:], preflight.stdout[-2500:], preflight.stderr[-800:])
        return validate.returncode or preflight.returncode
    contacts = {(r["organisation_id"], W.name_key(r["name"] or "")) for r in con.execute("SELECT organisation_id, name FROM contacts")}
    # The master holds some organisations twice (same name or same website). A person already on one record is not added
    # to its twin; the twins themselves are review items ('Possible organisation / branch overlap').
    def identities(org) -> set:
        return {("name", W.name_key(org["name"]))} | ({("domain", domain(org["website"]))} if domain(org["website"]) else set())
    people_seen = {(ident, W.name_key(r["name"] or "")) for r in con.execute("SELECT organisation_id, name FROM contacts WHERE COALESCE(name,'')<>''")
                   if r["organisation_id"] in orgs for ident in identities(orgs[r["organisation_id"]])}
    stats = {"organisations_updated": 0, "fields_filled": 0, "facts": 0, "contacts_inserted": 0, "reviews": 0, "plans_unheld": 0,
             "plans_held_for_closure": 0, "plans_held_for_unconfirmed_route": 0, "plans_released_route_confirmed": 0,
             "research_emails_cleaned": 0, "contacts_on_twin_records_skipped": 0, "contacts_with_incomplete_names": 0, "source_files": 0}
    try:
        con.execute("BEGIN")
        source_ids = {}
        for path in raw_files(run_date):
            body = path.read_bytes()
            sid = hid("F", "contact-research", path.name)
            con.execute("INSERT OR REPLACE INTO source_files (source_id, path, sha256, bytes, kind, encoding, content) VALUES (?,?,?,?,?,?,?)",
                        (sid, path.relative_to(C.ROOT).as_posix(), hashlib.sha256(body).hexdigest(), len(body), path.suffix.lstrip("."), "zlib",
                         zlib.compress(body, 9)))
            source_ids[path.name] = sid
            stats["source_files"] += 1
        default_source = next(iter(source_ids.values()))
        by_org = record_files(run_date)
        repair_research_emails(con, stats)
        for p in profiles:
            oid, org = p["organisation_id"], orgs[p["organisation_id"]]
            file_name = file_for("website" if "website" in p["methods"] else ("browser" if "browser" in p["methods"] else "search"),
                                 oid, by_org, source_ids, run_date)
            record = hid("R", "contact-research", run_date, oid)
            payload = {k: p[k] for k in ("websites", "emails", "phones", "postal", "physical", "socials", "methods", "sources", "blocked")}
            con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                        (record, source_ids.get(file_name, default_source), f"contact profile {oid} ({run_date})", json.dumps(payload, ensure_ascii=False)))
            con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) SELECT 'organisation', ?, ? WHERE NOT EXISTS "
                        "(SELECT 1 FROM entity_sources WHERE entity_type='organisation' AND entity_id=? AND record_id=?)", (oid, record, oid, record))
            updates = {}
            website = next((w for w in p["websites"] if w.startswith("http")), "")
            found, known = domain(website), domain(org["website"])
            if website and not org["website"]:
                updates["website"] = website
            elif found and known and found != known:
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "contact-website", oid), "Contact research conflict", oid, "", "website", f"{org['website']} | {website}",
                             "The research found a different website; confirm which is the organisation's own before changing it."))
                stats["reviews"] += 1
            elif found and not known:
                # Directory imports left slogans or phone numbers in some website fields; nothing is overwritten.
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "contact-website-text", oid), "Website field holds no website", oid, "", "website",
                             f"{org['website'][:200]} | {website}", "The website field holds text, not a web address. Research found the site "
                             "shown; replace the field after checking it."))
                stats["reviews"] += 1
            email, phone = best_email(p, org["name"]), best_phone(p)
            if email and not org["email"]:
                updates["email"] = email
            if phone and not org["phone"]:
                updates["phone"] = phone
            elif phone and not C.is_phone(org["phone"]):
                # Directory imports left category codes ('TO/DMC/MAIN', 'AFF/FIN') in some phone fields; nothing is overwritten.
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "contact-phone-text", oid), "Phone field holds no phone number", oid, "", "phone",
                             f"{org['phone'][:120]} | {phone}", "The phone field holds text, not a number. Research found the number shown; "
                             "replace the field after checking it."))
                stats["reviews"] += 1
            unsupported_routes(con, oid, org, p, record, stats)
            if p["postal"] and not org["address"]:
                updates["address"] = p["postal"][0]
            for field, value in updates.items():
                con.execute(f"UPDATE organisations SET {field}=? WHERE organisation_id=? AND COALESCE({field},'')=''", (value, oid))
                stats["fields_filled"] += 1
            if updates:
                stats["organisations_updated"] += 1
            facts = [("website", w) for w in p["websites"]] + [(f"email ({e['type']})", e["email"]) for e in p["emails"]]
            facts += [(f"phone ({x['type']})", x["phone"]) for x in p["phones"]] + [("postal_address", a) for a in p["postal"]]
            facts += [(f"social ({k})", v) for k, v in p["socials"].items()]
            # The research record was just replaced with the current profile, so its facts are replaced with it: every fact
            # stays traceable to what that record now holds (a later wave may drop a value an earlier one found).
            con.execute("DELETE FROM facts WHERE entity_type='organisation' AND entity_id=? AND record_id=?", (oid, record))
            for field, value in facts:
                con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                            (hid("X", oid, field, value), "organisation", oid, field, value, record))
                stats["facts"] += 1
            if updates.get("email") or updates.get("phone"):
                for plan in con.execute("SELECT message_id, missing_information, contact_channel FROM outreach_plans WHERE organisation_id=? "
                                        "AND target_type='organisation' AND review_status='Needs research'", (oid,)).fetchall():
                    # Notes are stored joined with "; ", and the route-gap note itself contains one, so it arrives in parts.
                    parts = [n for n in str(plan["missing_information"] or "").split("; ") if n]
                    notes = [n for n in parts if n not in ROUTE_GAP_PARTS]
                    # Release only a plan held for its route alone; any other blocker keeps it on hold.
                    if len(notes) < len(parts) and not any(BLOCKER.search(n) for n in notes):
                        con.execute("UPDATE outreach_plans SET review_status='Draft review', contact_channel=?, channel_attribution=?, missing_information=? "
                                    "WHERE message_id=?", (updates.get("email") or updates.get("phone"),
                                                           f"Found by contact research {run_date} ({', '.join(p['methods'])})", "; ".join(notes), plan["message_id"]))
                        stats["plans_unheld"] += 1
            closure = next((n for n in p.get("notes") or [] if C.CLOSURE.search(n)), "")
            if closure:
                # A sign the organisation has closed: hold every plan for it and ask a person to confirm; nothing is deleted.
                con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                            (hid("D", "contact-closure", oid), "Possible closure", oid, "", "status", closure[:400],
                             "Contact research found a sign that this organisation has closed. Confirm it still operates before any outreach; "
                             "archive it if it has closed."))
                for plan in con.execute("SELECT message_id, missing_information FROM outreach_plans WHERE organisation_id=?", (oid,)).fetchall():
                    con.execute("UPDATE outreach_plans SET review_status='Needs research', missing_information=? WHERE message_id=?",
                                (with_note(CLOSURE_NOTE, plan["missing_information"]), plan["message_id"]))
                    stats["plans_held_for_closure"] += 1
                stats["reviews"] += 1
            for kind, note in C.note_flags(p.get("notes")):
                if kind != "possible closure":
                    con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                                (hid("D", "contact-note", oid, kind), f"Contact research: {kind}", oid, "", "research note", note[:400], NOTE_ACTIONS[kind]))
                    stats["reviews"] += 1
            # A site crawled while its robots.txt could not be read, or read with a browser although its robots.txt disallows
            # crawling: flagged, not held (the user's decisions of 23 and 24 September 2026).
            flag_kinds = C.crawl_flag_kinds(p.get("crawl_flags"))
            for flag_kind, (id_part, review_kind, action) in ROBOTS_REVIEWS.items():
                robots_review = hid("D", id_part, oid)
                if flag_kind in flag_kinds:
                    con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                                (robots_review, review_kind, oid, "", "website", "; ".join(flag_kinds[flag_kind])[:400], action))
                    stats["reviews"] += 1
                else:
                    con.execute("DELETE FROM review WHERE review_id=?", (robots_review,))
            email_default = best_email(p, org["name"]) or org["email"] or ""
            phone_default = best_phone(p) or org["phone"] or ""
            for person in p["people"]:
                key = (oid, W.name_key(person["name"]))
                twins = {(ident, W.name_key(person["name"])) for ident in identities(org)}
                if person["already_in_database"] or person.get("identity") == "uncertain" or key in contacts:
                    continue
                if twins & people_seen:
                    stats["contacts_on_twin_records_skipped"] += 1
                    continue
                contacts.add(key)
                people_seen |= twins
                named = person["email"] if person["email"] and not W.PERSONAL_EMAIL.search(person["email"]) else ""
                cid = hid("C", oid, W.name_key(person["name"]))
                route = "named_email" if named else ("shared_email" if email_default else ("organisation_phone" if phone_default else "profile_url"))
                name_status = person.get("name_status") or C.name_status(person["name"])
                verification = (f"Published by the organisation ({person['method']}, {'fetched' if person.get('fetched') else 'search snippet'}) "
                                f"{person.get('accessed_on') or run_date}; pdpa_risk {person['pdpa_risk']}; "
                                f"decision-maker {'yes' if person['decision_maker'] else 'no'}"
                                + (f"; name {name_status}" if name_status != "complete" else ""))
                con.execute("INSERT INTO contacts (contact_id, organisation_id, name, role, campus, source_url, verification, shared_email, organisation_phone, "
                            "contact_route, published_role_email, role_phone, named_email) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (cid, oid, person["name"], person["role"], org["campus"] or "", person["source_url"], verification,
                             "" if named else email_default, phone_default, route, "", person["phone"] or "", named))
                crecord = hid("R", "contact-research-person", run_date, cid)
                con.execute("INSERT OR REPLACE INTO source_records (record_id, source_id, location, payload_json) VALUES (?,?,?,?)",
                            (crecord, source_ids.get(file_for(person["method"], oid, by_org, source_ids, run_date), default_source),
                             person["source_url"] or f"contact {cid}", json.dumps(person, ensure_ascii=False)))
                con.execute("INSERT INTO entity_sources (entity_type, entity_id, record_id) VALUES ('contact', ?, ?)", (cid, crecord))
                for field, value in (("role", person["role"]), ("pdpa_risk", person["pdpa_risk"]), ("decision_maker", str(person["decision_maker"]).lower()),
                                     ("named_email", named), ("role_phone", person["phone"]),
                                     ("name_status", name_status if name_status != "complete" else "")):
                    if value:
                        con.execute("INSERT OR IGNORE INTO facts (fact_id, entity_type, entity_id, field, value, record_id) VALUES (?,?,?,?,?,?)",
                                    (hid("X", cid, field, value), "contact", cid, field, value, crecord))
                if name_status != "complete":
                    # Kept, not dropped (the user's decision, 24 September 2026): a person someone can complete later. Drafts are not held;
                    # they address the person by the name the source gives.
                    con.execute("INSERT OR REPLACE INTO review (review_id, kind, entity_id, related_id, field, \"values\", action) VALUES (?,?,?,?,?,?,?)",
                                (hid("D", "contact-name-incomplete", cid), "Contact name incomplete", oid, cid, "name",
                                 f"{person['name']} | {person['role']} | {name_status} | {person['source_url']}"[:400], NAME_ACTION))
                    stats["contacts_with_incomplete_names"] += 1
                    stats["reviews"] += 1
                stats["contacts_inserted"] += 1
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        fks = con.execute("PRAGMA foreign_key_check").fetchall()
        if integrity != "ok" or fks:
            raise RuntimeError({"integrity": integrity, "foreign_keys": fks[:5]})
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        con.close()
        raise
    stats["contacts_after"] = con.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    con.close()
    # The merge report belongs with the outputs only when the canonical master changed; a trial on a copy stays in runtime/.
    trial = database.resolve() != MASTER.resolve()
    report = (C.WORK / "trial-master-contact-merge.json") if trial else (C.ROOT / "outputs" / "contacts" / "master-contact-merge.json")
    report.parent.mkdir(parents=True, exist_ok=True)
    # One entry per application (each research wave is merged in turn); the totals are what the workbook's audit shows.
    earlier = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
    applications = earlier.get("applications") or ([earlier] if earlier.get("applied_on") else [])
    applications.append({"run_date": run_date, "applied_on": date.today().isoformat(), "trial": trial, **stats})
    totals = {k: sum(a.get(k, 0) for a in applications) for k in ("contacts_inserted", "fields_filled", "plans_unheld", "organisations_updated")}
    report.write_text(json.dumps({"applications": applications, "totals": totals, "contacts_after": stats["contacts_after"]}, indent=1) + "\n",
                      encoding="utf-8")
    print(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
