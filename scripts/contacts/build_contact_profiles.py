#!/usr/bin/env python3
"""Combine contact research into one contact profile per organisation and a list of contact leads. No network calls.

Inputs (data/raw/contact-research/): website_contacts_<date>.jsonl (crawl_org_websites.py), osm_contacts_<date>.json
(collect_osm_contacts.py) and search_*_<date>.jsonl (budgeted research agents; brief in docs/methodology/contact-research.md). Databases are
read-only: the company master, the welfare run and the government run.

For every organisation it records what was already known and what was found (website, typed emails, typed phones,
postal and physical address, official social pages) with sources, and every named person the organisation publishes
(name, role, decision-maker flag, a work email or phone only when the same source links it to them, pdpa_risk).
Writes runtime/contacts/profiles.json (for the database merges), data/interim/contact-profiles/*.tsv and a summary.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import date

import contact_lib as C

W = C.W
DBS = {"master": C.ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite",
       "welfare": C.ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite",
       "government": C.ROOT / "outputs" / "runs" / "arusha-government-2026-09" / "lead-database.sqlite"}
ROLE_LOCALS = re.compile(r"^(info|contact|contacts|admin|administration|office|enquir(y|ies)|hello|mail|reservations?|bookings?|sales|hr|careers?|jobs|"
                         r"director|manager|secretary|accounts?|finance|support|safaris?|tours?|travel|marketing|operations|ops|frontoffice|front\.office|"
                         r"reception|gm|ceo|md|ded|cd|headteacher|principal|school|welfare|programs?|programmes?|volunteers?|donate|sponsorships?|"
                         r"general|team|staff|registrar|dean|vc|dvc|barua|mkurugenzi|ofisi|customercare|customer\.care|care|help)\b", re.I)


def ro(path):
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def phone_type(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("2552"):
        return "office"
    if digits.startswith(("2556", "2557")):
        return "mobile"
    return "international" if not digits.startswith("255") else "unknown"


def email_type(email: str, names: list[str]) -> tuple[str, str]:
    """('named'|'role'|'personal_domain'|'general', person name or '').

    Named: the mailbox carries a word of a published person's name, or their initials at a domain named after them
    (vd@vinnie.co.nz), so it belongs to that person and never serves as the organisation's route."""
    local, domain = email.split("@")[0].lower(), email.split("@")[-1].lower()
    label = domain.split(".")[0]
    for name in names:
        tokens = [t.lower() for t in re.findall(r"[A-Za-z]{3,}", name) if t.lower() not in ("mrs", "miss", "prof", "rev", "hon")]
        initials = "".join(t[0] for t in re.findall(r"[A-Za-z]+", re.sub(r"^" + C.HONORIFIC, "", name, flags=re.I))).lower()
        if tokens and any(t in local for t in tokens):
            return "named", name
        if not ROLE_LOCALS.search(local) and (label in tokens or (len(initials) >= 2 and local == initials)):
            return "named", name
    if W.PERSONAL_EMAIL.search(email):
        return "personal_domain", ""
    if ROLE_LOCALS.search(local):
        return "role", ""
    return "general", ""


def welfare_research_contacts(run_id: str = "arusha-welfare-2026-09") -> set:
    """(organisation key, contact key) pairs the welfare run's own research supplies, leaving out the contact-research
    export (research_W_*). Only these count as already known: the export must carry everything else every time."""
    cfg = json.loads((C.ROOT / "data" / "runs" / run_id / "run-config.json").read_text(encoding="utf-8"))
    pairs = set()
    for path in W.resolve_globs(cfg["research_files"]):
        if path.name.startswith("research_W_"):
            continue
        for r in W.read_jsonl(path):
            if r.get("record_type") == "contact" and r.get("contact_name"):
                pairs.add((W.name_key(r.get("organisation_name")), W.name_key(r["contact_name"])))
    return pairs


def load_orgs() -> dict:
    """(db, organisation_id) -> known organisation facts and existing contacts."""
    orgs = {}
    m = ro(DBS["master"])
    for r in m.execute("SELECT * FROM organisations"):
        orgs[("master", r["organisation_id"])] = {"db": "master", "organisation_id": r["organisation_id"], "name": r["name"], "segment": r["segment"],
                                                  "website": r["website"] or "", "email": r["email"] or "", "phone": r["phone"] or "",
                                                  "address": r["address"] or "", "contacts": []}
    for r in m.execute("SELECT * FROM contacts"):
        key = ("master", r["organisation_id"])
        if key in orgs:
            orgs[key]["contacts"].append({"name": r["name"] or "", "role": r["role"] or ""})
    m.close()
    w = ro(DBS["welfare"])
    for r in w.execute("SELECT * FROM organisations"):
        orgs[("welfare", r["organisation_id"])] = {"db": "welfare", "organisation_id": r["organisation_id"], "name": r["name"], "segment": r["segment"],
                                                   "website": r["website"] or "", "email": r["email"] or "", "phone": r["phone"] or "",
                                                   "address": r["address"] or "", "contacts": []}
    # The welfare run is rebuilt from its research files, including this research's own export (slice W). Only contacts its
    # own research supplies count as already known (role desks too); anything the export supplies must be exported again
    # every time, or the next rebuild drops it. This keeps the export the same however often it runs.
    known = welfare_research_contacts()
    for r in w.execute("SELECT c.*, o.name AS organisation_name FROM contacts c JOIN organisations o USING(organisation_id)"):
        key = ("welfare", r["organisation_id"])
        if key in orgs and (not r["name"] or (W.name_key(r["organisation_name"]), W.name_key(r["name"])) in known):
            orgs[key]["contacts"].append({"name": r["name"] or "", "role": r["role"] or ""})
    w.close()
    g = ro(DBS["government"])
    for r in g.execute("SELECT o.*, p.office_level, p.council_name, p.admin_unit_name FROM organisations o JOIN government_office_profiles p USING(organisation_id)"):
        orgs[("government", r["organisation_id"])] = {"db": "government", "organisation_id": r["organisation_id"], "name": r["name"],
                                                      "segment": r["office_level"], "website": r["website"] or "", "email": r["email"] or "",
                                                      "phone": r["phone"] or "", "address": r["address"] or "", "contacts": [],
                                                      "council_name": r["council_name"] or "", "admin_unit_name": r["admin_unit_name"] or ""}
    for r in g.execute("SELECT c.organisation_id, c.name, c.role FROM contacts c"):
        key = ("government", r["organisation_id"])
        if key in orgs and r["name"]:
            orgs[key]["contacts"].append({"name": r["name"], "role": r["role"] or ""})
    g.close()
    return orgs


# Named leads kept per organisation, most senior first; the rest are counted but not recorded (data minimisation).
LEADS_PER_ORGANISATION = 6
SENIORITY = [re.compile(r"founder|\bceo\b|chief exec|managing director|executive director|country director|general manager|proprietor|owner|"
                        r"principal|head of school|headmaster|headmistress|mkurugenzi|meneja mkuu", re.I),
             re.compile(r"human resources|\bhr\b|people|personnel|administrat|director|head of|manager|co-?ordinator|matron|social work|welfare|"
                        r"meneja|mratibu", re.I),
             re.compile(r"chair|president|secretary|treasurer|trustee|board|mwenyekiti|katibu", re.I)]


def seniority(role: str) -> int:
    return next((i for i, pattern in enumerate(SENIORITY) if pattern.search(role or "")), len(SENIORITY))


def government_key(orgs: dict, name: str) -> tuple | None:
    """Match a researched office name to a government-run office (councils, regional secretariats, district offices)."""
    probe = W.name_key(name)
    words = set(probe.split())
    best = None
    for (db, oid), o in orgs.items():
        if db != "government" or o["segment"] not in ("council", "region", "district"):
            continue
        target = W.name_key(o["name"])
        english = W.name_key(o["name"].split("(")[-1].rstrip(")")) if "(" in o["name"] else target
        # The same words in another order: "District Commissioner's Office, Arusha District" and "Arusha District Commissioner's Office".
        if probe and (probe == english or probe in target or english in probe or words == set(english.split())):
            best = (db, oid)
            if probe == english or words == set(english.split()):
                break
    return best


MANIFEST_KINDS = [("website_contacts_", "Own-website crawl: per site, the pages read (URL, status, SHA-256), published emails, phones, postal addresses, "
                                        "official social pages and named people with roles; no page text"),
                  ("osm_contacts_", "OpenStreetMap contact tags (phone, email, website) in the catchment"),
                  ("search_", "Budgeted search-agent records, one per organisation, with per-fact sources"),
                  ("coverage/", "Searches, fetches, blocked sources and organisations not reached, for one agent slice")]


def write_manifest() -> None:
    """data/raw/contact-research/MANIFEST.md: every raw file with its SHA-256, as the other raw-evidence folders have."""
    import hashlib
    rows = []
    for path in sorted(p for p in C.RAW.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
        rel = path.relative_to(C.RAW).as_posix()
        kind = next((text for prefix, text in MANIFEST_KINDS if rel.startswith(prefix)), "Contact-research evidence")
        rows.append(f"| `{rel}` | `{hashlib.sha256(path.read_bytes()).hexdigest()[:16]}…` | {kind} |")
    (C.RAW / "MANIFEST.md").write_text(
        "# Contact-research raw evidence\n\nEvidence behind the contact profiles and contact leads of all three databases. The scripts are in "
        "`scripts/contacts/`; the method, rules and agent brief are in `docs/methodology/contact-research.md`. Nothing here holds page text, "
        "children's data or anyone's private details.\n\n| File | SHA-256 | Contents |\n|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    orgs = load_orgs()
    found = defaultdict(lambda: {"websites": {}, "emails": {}, "phones": {}, "postal": {}, "physical": {}, "socials": {}, "people": [], "sources": [],
                                 "status": set(), "blocked": [], "crawl_flags": []})
    # Research records can carry a stale organisation ID (see contact_lib.Resolver).
    resolve = C.Resolver((db, oid, o["name"]) for (db, oid), o in orgs.items())

    def add_source(entry, url, title, facts, fetched, method, excerpt=""):
        if url and not any(s["url"] == url and s["method"] == method for s in entry["sources"]):
            entry["sources"].append({"url": url, "title": title, "facts": facts, "fetched": fetched, "method": method, "accessed_on": args.date,
                                     "excerpt": C.W.norm_text(excerpt)[:200]})

    # 1. website crawl
    crawl_path = C.RAW / f"website_contacts_{args.date}.jsonl"
    crawled = [json.loads(line) for line in crawl_path.read_text(encoding="utf-8").splitlines() if line.strip()] if crawl_path.exists() else []
    site_stats, dropped = Counter(), Counter()
    # A number or address on three or more different websites belongs to a shared platform (a booking portal, a web
    # designer, a theme's demo), not to any one organisation. (Several records sharing one website count once.)
    on_sites = defaultdict(set)
    for site in crawled:
        for raw in site["emails"]:
            on_sites[("email", C.clean_email(raw))].add(site["domain"])
        for phone in site["phones"]:
            on_sites[("phone", re.sub(r"\D", "", phone))].add(site["domain"])
    shared = {k for k, domains in on_sites.items() if k[1] and len(domains) >= 3}
    site_stats["values found on three or more websites (not used)"] = len(shared)
    for site in crawled:
        readable = [p for p in site["pages"] if p.get("status") == 200]
        site_stats["readable" if readable else (f"robots_{site['robots']}" if site.get("robots") == "disallowed" else "unreadable")] += 1
        if readable and site.get("robots") == "unreachable":
            site_stats["readable, crawled with robots.txt unreachable (flagged)"] += 1
        # A site recorded for several different organisations: its people belong to the one the site is named after.
        owners = {o["organisation_id"] for o in site["orgs"] if C.named_after(o["name"], site["domain"])}
        several = len({W.name_key(o["name"]) for o in site["orgs"]}) > 1
        for o in site["orgs"]:
            site_people = site["people"]
            if several and owners and o["organisation_id"] not in owners:
                dropped["site named after another organisation"] += len(site_people)
                site_people = []
            key = resolve(o["db"], o["organisation_id"], o["name"])
            if not key:
                site_stats["organisation no longer in its database"] += 1
                continue
            e = found[key]
            if not readable:
                e["blocked"].append(f"{site['domain']}: " + (f"robots.txt {site['robots']}" if site.get('robots') == 'disallowed' else (site['errors'][:1] or ['unreadable'])[0]))
                continue
            e["websites"].setdefault(readable[0]["final_url"], "crawl")
            for raw, info in site["emails"].items():
                email = C.clean_email(raw)  # the crawl file keeps what the page held; the profile keeps the clean address
                if email and ("email", email) not in shared:
                    e["emails"].setdefault(email, {"source_url": info["pages"][0], "fetched": True, "method": "website"})
            for phone, info in site["phones"].items():
                if not C.template_phone(phone) and ("phone", re.sub(r"\D", "", phone)) not in shared:
                    e["phones"].setdefault(phone, {"source_url": info["pages"][0], "fetched": True, "method": "website"})
            for postal in site["postal"]:
                e["postal"].setdefault(postal, {"source_url": readable[0]["final_url"], "method": "website"})
            for platform, link in site["socials"].items():
                e["socials"].setdefault(platform, link)
            for person in site_people:
                e["people"].append({"name": person["name"], "role": person["role"], "decision_maker": person["decision_maker"], "email": "", "phone": "",
                                    "source_url": person["page"], "fetched": True, "method": "website", "excerpt": person.get("context", ""),
                                    "pdpa_risk": person["pdpa_risk"], "pdpa_risk_reason": person["pdpa_risk_reason"]})
            for page in readable:
                add_source(e, page["final_url"], page.get("title", ""), [page.get("kind", "")], True, "website")
            e["status"].add("website")
            if site.get("robots") == "unreachable" and site["domain"] not in " ".join(e["crawl_flags"]):
                e["crawl_flags"].append(f"{site['domain']}: robots.txt could not be read (server, network or certificate error); the site was crawled anyway")

    # 2. OpenStreetMap contact tags, by exact normalised name when exactly one element matches
    osm_path = C.RAW / f"osm_contacts_{args.date}.json"
    osm = json.loads(osm_path.read_text(encoding="utf-8"))["elements"] if osm_path.exists() else []
    osm_by_key = defaultdict(list)
    for el in osm:
        for tag in ("name", "name:en", "alt_name"):
            if el["tags"].get(tag):
                osm_by_key[W.name_key(el["tags"][tag])].append(el)
    osm_matches = 0
    for key, o in orgs.items():
        # Every organisation, whatever the database holds now: a rebuilt run database already carries this step's own
        # findings, so conditioning on it would make the export flip between runs. Merges only fill blanks.
        if key[0] == "government":
            continue
        hits = osm_by_key.get(W.name_key(o["name"]), [])
        if len(hits) != 1:
            continue
        el, e = hits[0], found[key]
        url = f"https://www.openstreetmap.org/{el['osm_id']}"
        for tag in ("phone", "contact:phone", "mobile", "contact:mobile"):
            for part in str(el["tags"].get(tag) or "").split(";"):
                phone = W.norm_phone(part)
                if len(re.sub(r"\D", "", phone)) >= 10 and not C.template_phone(phone):
                    e["phones"].setdefault(phone, {"source_url": url, "fetched": True, "method": "openstreetmap"})
        for tag in ("email", "contact:email"):
            email = C.clean_email(str(el["tags"].get(tag) or ""))
            if email:
                e["emails"].setdefault(email, {"source_url": url, "fetched": True, "method": "openstreetmap"})
        for tag in ("website", "contact:website", "url"):
            if el["tags"].get(tag):
                e["websites"].setdefault(el["tags"][tag], "openstreetmap")
        if el["tags"].get("contact:facebook"):
            e["socials"].setdefault("facebook", el["tags"]["contact:facebook"])
        add_source(e, url, f"OpenStreetMap: {el['tags'].get('name')}", ["contact tags"], True, "openstreetmap")
        e["status"].add("openstreetmap")
        osm_matches += 1

    # 3. budgeted search research
    search_stats = Counter()
    for path in sorted(C.RAW.glob(f"search_*_{args.date}.jsonl")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                search_stats["unparsable lines"] += 1
                continue
            key = (resolve(r.get("db"), r.get("organisation_id"), r.get("organisation_name", "")) if r.get("organisation_id")
                   else government_key(orgs, r.get("organisation_name", "")))
            if not key or key not in orgs:
                search_stats["unmatched records"] += 1
                continue
            search_stats[f"{r.get('status', 'unknown')}"] += 1
            # Notes are kept whatever the outcome: a search that found nothing may still report a closure or a lost domain.
            if r.get("notes"):
                found[key].setdefault("notes", []).append(str(r["notes"])[:600])
            if r.get("status") in ("not_found", "blocked") and not any(r.get(k) for k in ("website", "emails", "phones", "people")):
                found[key]["status"].add(f"search:{r.get('status')}")
                continue
            e = found[key]
            uncertain = r.get("identity") == "uncertain"
            if r.get("website") and not uncertain:
                e["websites"].setdefault(r["website"], "search")
            for item in r.get("emails") or []:
                email = C.clean_email(str(item.get("value") or ""))
                if email and not uncertain:
                    e["emails"].setdefault(email, {"source_url": item.get("source_url", ""), "fetched": bool(item.get("fetched")), "method": "search"})
            for item in r.get("phones") or []:
                phone = W.norm_phone(str(item.get("value") or ""))
                if len(re.sub(r"\D", "", phone)) >= 10 and not uncertain and not C.template_phone(phone):
                    e["phones"].setdefault(phone, {"source_url": item.get("source_url", ""), "fetched": bool(item.get("fetched")), "method": "search"})
            for field, target in (("postal_address", "postal"), ("physical_address", "physical")):
                value = (r.get(field) or {}).get("value") if isinstance(r.get(field), dict) else r.get(field)
                if value and not uncertain:
                    e[target].setdefault(str(value)[:120], {"source_url": (r.get(field) or {}).get("source_url", "") if isinstance(r.get(field), dict) else "",
                                                             "method": "search"})
            for item in r.get("socials") or []:
                if item.get("url") and not uncertain:
                    e["socials"].setdefault(item.get("platform") or "other", item["url"])
            for p in r.get("people") or []:
                if not p.get("name") or not p.get("role"):
                    continue
                e["people"].append({"name": C.W.norm_text(p["name"]), "role": C.W.norm_text(p["role"]), "decision_maker": bool(C.DECISION.search(p["role"])),
                                    "email": C.clean_email(str(p.get("email") or "")), "phone": W.norm_phone(str(p.get("phone") or "")) if p.get("phone") else "",
                                    "source_url": p.get("source_url", ""), "fetched": bool(p.get("fetched")), "method": "search",
                                    "excerpt": p.get("excerpt", ""), "pdpa_risk": p.get("pdpa_risk") or "medium",
                                    "pdpa_risk_reason": p.get("pdpa_risk_reason") or "Named person in a professional role, as published.",
                                    "identity": r.get("identity", "confirmed")})
            for s in r.get("sources") or []:
                add_source(e, s.get("url"), s.get("title", ""), s.get("facts", []), bool(s.get("fetched")), "search", s.get("excerpt", ""))
            e["status"].add("search")

    # 4. profiles
    profiles, leads = [], []
    for key, o in orgs.items():
        e = found.get(key)
        people = []
        # Host names only; website fields sometimes hold free text, so no URL parsing.
        domains = " ".join(h for w in [o["website"], *((e["websites"] if e else {}).keys())] for h in re.findall(r"[a-z0-9\-]+(?:\.[a-z0-9\-]+)+", w.lower()))
        for p in (e["people"] if e else []):
            person = C.clean_person(p["name"], p["role"], o["name"], domains)
            if not person or (key[0] == "government" and p["method"] == "search"):
                # Government offices are addressed by office title; officials are named only from the run's own official sources.
                dropped["government official (office title only)" if person else "not a current, relevant, named person"] += 1
                continue
            p = {**p, "name": person[0], "role": person[1], "decision_maker": person[2]}
            same = next((x for x in people if W.name_key(p["name"]) == W.name_key(x["name"]) or C.same_person(p["name"], x["name"])), None)
            if same:
                # The same person from a second source: keep the first record and add any work route that source links to them.
                same["email"], same["phone"] = same["email"] or p["email"], same["phone"] or p["phone"]
                continue
            existing = any(W.name_key(p["name"]) == W.name_key(c["name"]) or C.same_person(p["name"], c["name"]) for c in o["contacts"] if c["name"])
            people.append({**p, "already_in_database": existing})
        new = sorted((p for p in people if not p["already_in_database"]), key=lambda p: seniority(p["role"]))
        if len(new) > LEADS_PER_ORGANISATION:
            dropped[f"beyond {LEADS_PER_ORGANISATION} new leads per organisation"] += len(new) - LEADS_PER_ORGANISATION
            keep = {id(p) for p in new[:LEADS_PER_ORGANISATION]}
            people = [p for p in people if p["already_in_database"] or id(p) in keep]
        emails = []
        for email, info in (e["emails"].items() if e else []):
            etype, person = email_type(email, [x["name"] for x in people] + [c["name"] for c in o["contacts"] if c["name"]])
            emails.append({"email": email, "type": etype, "person": person, **info})
        for p in people:
            if not p["email"]:
                linked = next((x["email"] for x in emails if x["person"] == p["name"]), "")
                p["email"] = linked
            if p["email"] and W.PERSONAL_EMAIL.search(p["email"]):
                p["pdpa_risk"], p["pdpa_risk_reason"] = "risky", "Named person linked to a personal-domain email."
        phones = [{"phone": ph, "type": phone_type(ph), **info} for ph, info in (e["phones"].items() if e else [])]
        profile = {"db": key[0], "organisation_id": key[1], "name": o["name"], "segment": o["segment"],
                   "known": {"website": o["website"], "email": o["email"], "phone": o["phone"], "address": o["address"], "contacts": len(o["contacts"])},
                   "websites": sorted((e["websites"] if e else {}).keys()), "emails": emails, "phones": phones,
                   "postal": sorted((e["postal"] if e else {}).keys()), "physical": sorted((e["physical"] if e else {}).keys()),
                   "socials": dict(e["socials"]) if e else {}, "people": people, "sources": e["sources"] if e else [],
                   "methods": sorted(e["status"]) if e else [], "blocked": e["blocked"] if e else [], "notes": (e or {}).get("notes", []),
                   "crawl_flags": e["crawl_flags"] if e else []}
        has_route_before = bool(o["website"] or o["email"] or o["phone"])
        has_route_after = has_route_before or bool(profile["emails"] or profile["phones"] or profile["websites"])
        profile["route_before"], profile["route_after"] = has_route_before, has_route_after
        profile["named_before"] = sum(1 for c in o["contacts"] if c["name"])
        profile["named_new"] = sum(1 for p in people if not p["already_in_database"])
        profiles.append(profile)
        for p in people:
            leads.append({"db": key[0], "organisation_id": key[1], "organisation": o["name"], **{k: p.get(k, "") for k in (
                "name", "role", "decision_maker", "email", "phone", "source_url", "fetched", "method", "excerpt", "pdpa_risk", "pdpa_risk_reason",
                "already_in_database", "identity")}})
    C.WORK.mkdir(parents=True, exist_ok=True)
    (C.WORK / "profiles.json").write_text(json.dumps({"date": args.date, "profiles": profiles}, ensure_ascii=False, indent=1), encoding="utf-8")
    interim = C.ROOT / "data" / "interim" / "contact-profiles"
    interim.mkdir(parents=True, exist_ok=True)
    with open(interim / "organisation_contact_profiles.tsv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["db", "organisation_id", "name", "segment", "route_before", "route_after", "websites", "emails", "phones", "postal", "socials",
                         "named_contacts_before", "new_named_leads", "methods", "blocked"])
        for p in profiles:
            writer.writerow([p["db"], p["organisation_id"], p["name"], p["segment"], p["route_before"], p["route_after"], " | ".join(p["websites"]),
                             " | ".join(f"{x['email']} ({x['type']})" for x in p["emails"]), " | ".join(f"{x['phone']} ({x['type']})" for x in p["phones"]),
                             " | ".join(p["postal"]), " | ".join(f"{k}: {v}" for k, v in p["socials"].items()), p["named_before"], p["named_new"],
                             ", ".join(p["methods"]), " | ".join(p["blocked"])])
    lead_fields = ["db", "organisation_id", "organisation", "name", "role", "decision_maker", "email", "phone", "source_url", "fetched", "method",
                   "pdpa_risk", "pdpa_risk_reason", "already_in_database", "identity"]
    with open(interim / "contact_leads.tsv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=lead_fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)
    summary = {"date": args.date, "sites_crawled": len(crawled), "sites": dict(site_stats), "osm_matches": osm_matches, "search_records": dict(search_stats),
               "people_not_recorded": dict(dropped)}
    for db in DBS:
        rows = [p for p in profiles if p["db"] == db]
        summary[db] = {"organisations": len(rows), "route_before": sum(p["route_before"] for p in rows), "route_after": sum(p["route_after"] for p in rows),
                       "with_named_contact_before": sum(1 for p in rows if p["named_before"]),
                       "with_named_contact_after": sum(1 for p in rows if p["named_before"] or p["named_new"]),
                       "new_named_leads": sum(p["named_new"] for p in rows),
                       "new_decision_maker_leads": sum(1 for p in rows for x in p["people"] if not x["already_in_database"] and x["decision_maker"])}
    (C.WORK / "profiles-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    write_manifest()
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
