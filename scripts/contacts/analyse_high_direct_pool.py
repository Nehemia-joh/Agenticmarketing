#!/usr/bin/env python3
"""Read-only analysis of the high-direct pool: the company and welfare leads in high-indirect and medium, what each lacks to
become high-direct, how valuable it is, and what the repository already holds (contact profiles, crawled pages in the HTTP
cache, research records) that could move it without a web search. Also measures how many email domains already show a
personal address format (the email-format track of docs/plans/high-direct-wave-2026-10-11.md).

No network, no database writes. The segments come from scripts/messaging/export_resend_contacts.py's own row builders
(company_rows, welfare_rows, dedupe), so the counts are the exporter's. Databases are opened read-only.

  python scripts/contacts/analyse_high_direct_pool.py [--runtime <dir with contacts/profiles.json and contacts/http-cache>]

--runtime defaults to this checkout's runtime/; a worktree points it at the main checkout's runtime/ (read-only use).
Writes a summary JSON to stdout and, with --detail <path>, one row per pool lead (names and addresses: keep it under
runtime/, never commit it).

Before and after a wave (no cache reading):
  --snapshot runtime/analysis/before.json     every exported row and its segment
  --compare before.json after.json            segment counts, moves, high-direct gained, and any high-direct row lost (exit 1)
  --check                                     the plan's invariants: no free-mail, rejected or inferred address among high-direct,
                                              every company high-direct address on a sourced fact, no risky/incomplete/board-only
                                              high-direct recipient (exit 1 on a failure)
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "messaging"))
sys.path.insert(0, str(ROOT / "scripts" / "master"))
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import export_resend_contacts as X  # noqa: E402
import resolve_master_recipients as R  # noqa: E402
import infer_candidate_emails as I  # noqa: E402

MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WELFARE = ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"
RAW = ROOT / "data" / "raw" / "contact-research"
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
FREE = re.compile(r"@(gmail|yahoo|hotmail|outlook|live|icloud|ymail|aol|proton|rocketmail|googlemail)\.", re.I)
ROLEISH = re.compile(r"^(info|sales|reservations?|bookings?|enquir(y|ies)|inquir(y|ies)|admin|office|contact|hello|operations?|safaris?|mail|support|"
                     r"accounts?|marketing|press|karibu|welcome|reception|customercare|customer|hr|careers|jobs|tours?|travel|team|email|res|book|"
                     r"finance|director|manager|ceo|md|gm|webmaster|no-?reply|dhrma|general|management|ops|procurement|tender|recruitment|"
                     r"secretary|registrar|principal|headmaster|admissions?|it|ict|events?|media|communications?|pr|partnerships?|donate|giving|"
                     r"volunteer|programs?|programmes?|projects?|national|country|executive|chair|president|board|legal|audit|feedback|complaints?)",
                     re.I)


def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def names_of(name: str) -> list[str]:
    return [n.lower() for n in re.findall(r"[A-Za-z]{3,}", X.L.greeting_name(name or "")) if not X.TITLE.match(n)]


def carries_name(address: str, name: str) -> bool:
    """The mailbox carries the person's name, by the exporter's own direct-route test (high_route)."""
    route, _ = X.high_route(address, name, "")
    return route == "direct" and "own address" in _


def full_name(name: str) -> bool:
    first, last = X.split_name(name or "")
    return bool(first and last)


def cache_body(cache: Path, url: str) -> bytes:
    key = hashlib.sha256(url.encode()).hexdigest()
    body, meta = cache / f"{key}.bin", cache / f"{key}.json"
    if not meta.exists() or not body.exists():
        return b""
    try:
        data = body.read_bytes()
    except OSError:
        return b""
    if data[:2] == b"\x1f\x8b":
        try:
            return gzip.decompress(data)
        except (OSError, EOFError):
            return data
    return data


SNAPSHOT_FIELDS = ("track", "organisation", "plan_id", "email", "confidence", "high_route", "recipient")
REJECTED = ROOT / "data" / "reference" / "rejected-routes.json"


def segment(r: dict) -> str:
    return f"{r['track']}-{r['confidence']}" + (f"-{r['high_route']}" if r.get("high_route") else "")


def snapshot(path: Path) -> int:
    """Every exported row (all tracks except government) as the exporter builds it now: the before or after picture of a wave.
    Holds addresses, so keep it under runtime/."""
    master, welfare = ro(MASTER), ro(WELFARE)
    rows, _ = X.dedupe(X.company_rows(master)[0] + X.welfare_rows(welfare)[0])
    data = [{k: r.get(k, "") for k in SNAPSHOT_FIELDS} for r in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(dict(sorted(Counter(segment(r) for r in data).items())), indent=1))
    return 0


def compare(before_path: Path, after_path: Path) -> int:
    """Segment counts before and after, the leads that moved (by organisation and track), and every earlier high-direct row that
    is no longer high-direct (there should be none)."""
    before = json.loads(before_path.read_text(encoding="utf-8"))
    after = json.loads(after_path.read_text(encoding="utf-8"))
    key = lambda r: (r["track"], r["organisation"])  # noqa: E731
    b, a = {key(r): r for r in before}, {key(r): r for r in after}
    counts_b, counts_a = Counter(segment(r) for r in before), Counter(segment(r) for r in after)
    moved = Counter((segment(b[k]), segment(a[k])) for k in b.keys() & a.keys() if segment(b[k]) != segment(a[k]))
    lost = [{"organisation": k[1], "track": k[0], "now": segment(a[k]) if k in a else "not exported"}
            for k, r in b.items() if r.get("high_route") == "direct" and (k not in a or a[k].get("high_route") != "direct")]
    gained = [{"organisation": k[1], "track": k[0], "was": segment(b[k]) if k in b else "not exported", "recipient": a[k]["recipient"]}
              for k, r in a.items() if r.get("high_route") == "direct" and (k not in b or b[k].get("high_route") != "direct")]
    out = {"segments": {s: {"before": counts_b.get(s, 0), "after": counts_a.get(s, 0)} for s in sorted(set(counts_b) | set(counts_a))},
           "moves": {f"{x} -> {y}": n for (x, y), n in sorted(moved.items())},
           "high_direct_gained": sorted(gained, key=lambda g: (g["track"], g["organisation"])),
           "high_direct_lost": lost,
           "rows_only_before": len(b.keys() - a.keys()), "rows_only_after": len(a.keys() - b.keys())}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 1 if lost else 0


def check() -> int:
    """Invariants on the high and high-direct rows (docs/plans/high-direct-wave-2026-10-11.md section 5): no free-mail and no rejected
    route among high-direct, no inferred candidate as a high address, every company high-direct address traceable to a fact with a
    source record, and no high recipient whose contact is risky, incomplete or board-only. Exit 1 on any failure."""
    master, welfare = ro(MASTER), ro(WELFARE)
    rows, _ = X.dedupe(X.company_rows(master)[0] + X.welfare_rows(welfare)[0])
    rejected = {str(x["value"]).lower() for x in json.loads(REJECTED.read_text(encoding="utf-8"))["routes"] if x["kind"] == "email"}
    try:
        inferred = {r[0].lower() for r in master.execute("SELECT address FROM candidate_emails")}
    except sqlite3.OperationalError:
        inferred = set()
    plans = {r["message_id"]: dict(r) for r in master.execute("SELECT message_id, target_type, target_id FROM outreach_plans")}
    contacts = {r["contact_id"]: dict(r) for r in master.execute("SELECT contact_id, name, role, verification FROM contacts")}
    traced = {(r[0], str(r[1]).lower()) for r in master.execute(
        "SELECT f.entity_id, f.value FROM facts f JOIN source_records s ON s.record_id=f.record_id "
        "WHERE f.entity_type='contact' AND f.field IN ('named_email','published_role_email','shared_email','email')")}
    org_traced = {str(r[0]).lower() for r in master.execute(
        "SELECT f.value FROM facts f JOIN source_records s ON s.record_id=f.record_id WHERE f.entity_type='organisation' AND f.field LIKE '%email%'")}
    failures = defaultdict(list)
    for r in rows:
        address = r["email"].lower()
        if r["confidence"] != "high":
            continue
        if address in inferred:
            failures["inferred candidate used as a high address"].append(r["organisation"])
        if r["high_route"] != "direct":
            continue
        if FREE.search(address):
            failures["free-mail high-direct address"].append(r["organisation"])
        if address in rejected:
            failures["rejected route as high-direct"].append(r["organisation"])
        if r["track"] in ("companies", "introducers"):
            p = plans.get(r["plan_id"], {})
            c = contacts.get(p.get("target_id")) if p.get("target_type") == "contact" else None
            if c and not any(cid == c["contact_id"] and address in v for cid, v in traced) and address not in org_traced:
                failures["high-direct address without a sourced fact"].append(r["organisation"])
            if c and (R.UNUSABLE.search(c["verification"] or "") or (R.BOARD.search(c["role"] or "") and not R.EXECUTIVE.search(c["role"] or ""))):
                failures["high-direct recipient risky, incomplete or board-only"].append(r["organisation"])
    result = {"high_rows": sum(1 for r in rows if r["confidence"] == "high"),
              "high_direct_rows": sum(1 for r in rows if r["high_route"] == "direct"),
              "failures": {k: sorted(set(v)) for k, v in failures.items()}}
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runtime", type=Path, default=ROOT / "runtime")
    parser.add_argument("--detail", type=Path, help="write one row per pool lead here (contains names and addresses: runtime/ only)")
    parser.add_argument("--snapshot", type=Path, help="write every exported row (segment, address) here and stop (runtime/ only)")
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("BEFORE", "AFTER"), help="compare two snapshots and stop")
    parser.add_argument("--check", action="store_true", help="check the high-direct invariants on the databases as they are now and stop")
    parser.add_argument("--master", type=Path, help="another master database (a trial copy)")
    parser.add_argument("--welfare", type=Path, help="another welfare run database (a trial copy)")
    args = parser.parse_args()
    global MASTER, WELFARE
    MASTER, WELFARE = args.master or MASTER, args.welfare or WELFARE
    if args.snapshot:
        return snapshot(args.snapshot)
    if args.compare:
        return compare(*args.compare)
    if args.check:
        return check()
    cache = args.runtime / "contacts" / "http-cache"
    profiles = json.loads((args.runtime / "contacts" / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    prof = {(p["db"], p["organisation_id"]): p for p in profiles}

    master, welfare = ro(MASTER), ro(WELFARE)
    c_rows, _ = X.company_rows(master)
    w_rows, _ = X.welfare_rows(welfare)
    rows, _ = X.dedupe(c_rows + w_rows)
    master.row_factory = sqlite3.Row
    welfare.row_factory = sqlite3.Row
    segments = Counter((r["track"], r["confidence"] + (("-" + r["high_route"]) if r["high_route"] else "")) for r in rows)

    # ---- organisation and contact context
    plans = {r["message_id"]: dict(r) for r in master.execute("SELECT * FROM outreach_plans")}
    orgs = {r["organisation_id"]: dict(r) for r in master.execute("SELECT * FROM organisations")}
    contacts = {r["contact_id"]: dict(r) for r in master.execute("SELECT * FROM contacts")}
    by_org = defaultdict(list)
    for c in contacts.values():
        by_org[c["organisation_id"]].append(c)
    reach = {r["organisation_id"]: r["tier"] for r in master.execute("SELECT organisation_id, tier FROM employer_reach")}
    cands = defaultdict(list)
    for r in master.execute("SELECT contact_id, organisation_id, address, confidence FROM candidate_emails"):
        cands[r["contact_id"]].append(dict(r))
    published = X.published_inbox_domains(master, orgs)
    w_plans = {r["message_id"]: dict(r) for r in welfare.execute("SELECT * FROM outreach_plans")}
    w_orgs = {r["organisation_id"]: dict(r) for r in welfare.execute("SELECT * FROM organisations")}
    w_by_org = defaultdict(list)
    for c in welfare.execute("SELECT * FROM contacts"):
        w_by_org[c["organisation_id"]].append(dict(c))

    # ---- crawled pages per organisation (all crawl files), resolving stale IDs as the planner does
    import contact_lib as C  # noqa: E402
    resolve = C.Resolver((p["db"], p["organisation_id"], p["name"]) for p in profiles)
    pages = defaultdict(list)
    robots = {}
    for path in sorted(RAW.glob("website_contacts_*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            site = json.loads(line)
            for o in site["orgs"]:
                key = resolve(o["db"], o["organisation_id"], o["name"]) or (o["db"], o["organisation_id"])
                robots[key] = site.get("robots", "")
                for pg in site["pages"]:
                    if pg.get("status") == 200 and pg["url"] not in [x["url"] for x in pages[key]]:
                        pages[key].append(pg)
    browser_read = set()
    for path in RAW.glob("browser_*.jsonl"):
        if "googlemaps" in path.name:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                key = resolve(r.get("db"), r.get("organisation_id"), r.get("organisation_name", "")) or (r.get("db"), r.get("organisation_id"))
                browser_read.add(key)

    memo = {}

    def site_emails(key) -> dict:
        """Every address on the organisation's cached pages: {address: [page urls]} (crawler extraction rules, re-read offline)."""
        if key in memo:
            return memo[key]
        out = memo[key] = defaultdict(list)
        for pg in pages.get(key, []):
            body = cache_body(cache, pg["url"])
            if not body:
                continue
            try:
                found = C.extract(pg.get("final_url") or pg["url"], body)["emails"]
            except Exception:  # noqa: BLE001 - a page the extractor cannot parse
                found = {}
            for a in found:
                out[a.lower()].append(pg["url"])
        return out

    # ---- classify the pool
    pool, detail = [], []
    for r in rows:
        if not (r["confidence"] == "medium" or (r["confidence"] == "high" and r["high_route"] == "indirect")):
            continue
        band = "high-indirect" if r["confidence"] == "high" else "medium"
        if r["track"] in ("companies", "introducers"):
            p = plans[r["plan_id"]]
            oid = p["organisation_id"]
            org = orgs[oid]
            key = ("master", oid)
            contact = contacts.get(p["target_id"]) if p["target_type"] == "contact" else None
            site = R.domain(org["website"])
            people = by_org[oid]
            tier, desk, dist, rad = reach.get(oid, ""), org["desk_tier"] or "", org["distance_km"], org["radius_tier"] or ""
            headcount = org["headcount"] or ""
            segment = org["segment"] or ""
            reason = r["confidence_reason"]
        else:
            p = w_plans[r["plan_id"]]
            oid = p["organisation_id"]
            org = w_orgs[oid]
            key = ("welfare", oid)
            rec = (p["recipient"] or "").split("(")[0].strip()
            contact = None
            for c in w_by_org[oid]:
                if rec and (W_same(c["name"], rec)):
                    contact = c
                    break
            site = (org["domain"] or R.domain(org["website"]) or "").lower()
            people = w_by_org[oid]
            tier, desk, dist, rad = org["priority"] or "", org["desk_tier"] or "", org["distance_km"], org["radius_tier"] or ""
            headcount = org["headcount"] or ""
            segment = org["segment"] or ""
            reason = r["confidence_reason"]
        # The exporter's own test: its reason says whether a verified named decision-maker is the addressee.
        named = (r["confidence_reason"].startswith("named, verified") if r["track"] != "welfare"
                 else r["confidence_reason"].startswith(("ready; addressed to the named leader", "ready; named leader")))
        name = (contact or {}).get("name") or (r["recipient"].split("(")[0].strip() if named else "")
        role = (contact or {}).get("role") or ""
        addr = r["email"].lower()
        # what blocks a move to high-direct
        if band == "high-indirect":
            why = "named decision-maker, only a general or shared inbox"
        elif r["track"] != "welfare":
            if named:
                why = ("named decision-maker, address on free-mail" if FREE.search(addr)
                       else "named decision-maker, address not on the organisation's domain")
            else:
                why = "no usable named decision-maker (organisation inbox, " + ("free-mail)" if FREE.search(addr) else "own domain)")
        else:
            if named:
                why = "named decision-maker, address on free-mail"
            else:
                why = "no usable named decision-maker (organisation inbox, " + ("free-mail)" if FREE.search(addr) else "own domain)")
        # why an organisation without a usable named recipient has none: a person on file who fails the recipient tests
        unnamed_sub = ""
        if not named:
            if r["track"] != "welfare":
                dms = [c for c in people if c["name"] and (R.role_rank(c["role"]) is not None or R.FALLBACK_OK.search(c["role"] or ""))
                       and not R.BOARD.search(c["role"] or "")]
                if not dms:
                    unnamed_sub = "no decision-maker on file"
                elif any(R.UNUSABLE.search(c["verification"] or "") for c in dms) and not any(R.verified_person(c) for c in dms):
                    unnamed_sub = "decision-maker on file but incomplete name, risky or not a decision-maker"
                elif not any(R.VERIFIED.search(c["verification"] or "") for c in dms):
                    unnamed_sub = "decision-maker on file but unverified"
                else:
                    unnamed_sub = "verified decision-maker on file, not selected (no email route of their own or draft not ready)"
            else:
                dms = [c for c in people if c["name"] and C.DECISION.search(C.NOT_A_HEAD.sub("", c["role"] or ""))]
                unnamed_sub = "decision-maker on file, not the addressee" if dms else "no decision-maker on file"
            pp = prof.get(key, {}).get("people", [])
            if not dms and any(x.get("decision_maker") and not x.get("already_in_database") for x in pp):
                unnamed_sub += "; a decision-maker is in the contact profiles, not merged"
        # what the repository already holds
        crawled = bool(pages.get(key))
        team_pages = sum(1 for pg in pages.get(key, []) if pg.get("kind") in ("team", "about"))
        on_site = site_emails(key) if crawled else {}
        own = {a: u for a, u in on_site.items() if site and (a.split("@")[-1].endswith(site) or site.endswith(a.split("@")[-1]))}
        personal_like = sorted(a for a in own if not ROLEISH.match(a.split("@")[0]) and not re.fullmatch(r"[a-z]{1,3}", a.split("@")[0]))
        name_match_site = sorted(a for a in own if name and full_name(name) and carries_name(a, name))
        prof_named = [e for e in prof.get(key, {}).get("emails", []) if e.get("type") == "named" and not FREE.search(e["email"])]
        name_match_prof = sorted({e["email"].lower() for e in prof_named if name and carries_name(e["email"], name)})
        person_email_prof = sorted({x["email"].lower() for x in prof.get(key, {}).get("people", [])
                                    if x.get("email") and name and C.same_person(x["name"], name) and not FREE.search(x["email"])})
        other_dm_own = sorted({a for c in people for a in R.emails(c.get("named_email"), c.get("published_role_email"))
                               if c.get("name") and name and not C.same_person(c["name"], name)})
        candidate = bool(contact and cands.get(contact.get("contact_id", "")))
        hit = sorted(set(name_match_site) | set(name_match_prof) | set(person_email_prof))
        if hit:
            deterministic = "name-matched own-domain address already in the repository"
        elif personal_like and named:
            deterministic = "own-domain personal-style address on file, not tied to the recipient"
        elif crawled:
            deterministic = "site crawled, no address for the person"
        elif key in browser_read:
            deterministic = "site read with the browser, no address for the person"
        elif site:
            deterministic = "website known, not readable by the crawler"
        else:
            deterministic = "no website"
        try:
            km = float(dist) if dist not in (None, "") else None
        except ValueError:
            km = None
        item = {"site": site, "track": r["track"], "band": band, "why": why, "unnamed_sub": unnamed_sub, "segment": segment, "tier": tier, "desk": desk,
                "km": km, "radius": rad, "headcount": headcount, "named": named, "full_name": bool(name and full_name(name)),
                "website": bool(site), "crawled": crawled, "team_pages": team_pages, "robots": robots.get(key, ""), "browser_read": key in browser_read,
                "deterministic": deterministic, "candidate_email": candidate, "other_dm_has_own": bool(other_dm_own),
                "role_inbox_for_role": bool(named and any(X.high_route(a, name, role)[0] == "direct" for a in own if a not in name_match_site))}
        pool.append(item)
        detail.append({**item, "organisation": r["organisation"], "organisation_id": oid, "recipient": r["recipient"], "email": addr,
                       "hits": hit, "personal_like": personal_like[:5]})

    def tally(key_fn, items=None):
        out = defaultdict(Counter)
        for it in (pool if items is None else items):
            out[it["track"] + " " + it["band"]][key_fn(it)] += 1
        return {k: dict(sorted(v.items(), key=lambda kv: -kv[1])) for k, v in sorted(out.items())}

    def km_band(it):
        km = it["km"]
        return "unknown" if km is None else "0-5" if km <= 5 else "5-10" if km <= 10 else "10-25" if km <= 25 else ">25"

    summary = {
        "segments": {f"{t}-{c}": n for (t, c), n in sorted(segments.items())},
        "pool_by_reason": tally(lambda it: it["why"]),
        "unnamed_sub_reasons": tally(lambda it: it["unnamed_sub"], [it for it in pool if not it["named"]]),
        "pool_by_tier": tally(lambda it: str(it["tier"] or "-")),
        "pool_by_desk": tally(lambda it: str(it["desk"] or "-")),
        "pool_by_km": tally(km_band),
        "pool_by_segment": tally(lambda it: it["segment"]),
        "deterministic": tally(lambda it: it["deterministic"]),
        "headcount_known": tally(lambda it: "known" if it["headcount"] else "unknown"),
        "named_full_name": tally(lambda it: "full name" if it["full_name"] else "incomplete", [it for it in pool if it["named"]]),
        "crawled_team_or_about_pages": tally(lambda it: "has team/about page cached" if it["team_pages"] else "no team/about page cached",
                                             [it for it in pool if it["crawled"]]),
        "robots_disallowed": tally(lambda it: it["robots"] or "-"),
        "candidate_email_exists": tally(lambda it: "yes" if it["candidate_email"] else "no", [it for it in pool if it["named"]]),
        "role_inbox_for_their_role_on_site": tally(lambda it: "yes" if it["role_inbox_for_role"] else "no", [it for it in pool if it["named"]]),
        "priority_matrix_companies": dict(Counter(
            f"{it['tier'] or '-'} | {km_band(it)} | {'named' if it['named'] else 'unnamed'} | {'crawled' if it['crawled'] else ('browser' if it['browser_read'] else ('site' if it['website'] else 'no site'))}"
            for it in pool if it["track"] != "welfare").most_common(40)),
        "priority_matrix_welfare": dict(Counter(
            f"{it['tier'] or '-'} | {km_band(it)} | {'named' if it['named'] else 'unnamed'} | {'crawled' if it['crawled'] else ('browser' if it['browser_read'] else ('site' if it['website'] else 'no site'))}"
            for it in pool if it["track"] == "welfare").most_common(40)),
    }
    formats = email_formats(master, welfare, profiles, pages, cache, site_emails, resolve)
    format_detail = {"formats": formats.pop("_formats"), "candidates_per_domain": formats.pop("_candidates_per_domain")}
    summary["email_formats"] = formats
    ok = {d: f for d, f in format_detail["formats"].items() if f["status"] == "ok"}
    summary["pool_recipients_on_a_domain_with_a_clear_format"] = tally(
        lambda it: ("format, " + ("2+" if ok[it["site"]]["evidence"] >= 2 else "1") + " evidence") if it["site"] in ok else
        ("ambiguous format" if it["site"] in format_detail["formats"] else "no format"), [it for it in pool if it["named"]])
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    if args.detail:  # names and addresses: runtime/ only
        args.detail.parent.mkdir(parents=True, exist_ok=True)
        args.detail.write_text(json.dumps(detail, indent=1, ensure_ascii=False), encoding="utf-8")
        args.detail.with_name(args.detail.stem + "-formats.json").write_text(json.dumps(format_detail, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


def W_same(a: str, b: str) -> bool:
    import contact_lib as C  # noqa: E402
    return bool(a and b) and (C.same_person(a, b) or C.W.name_key(a) == C.W.name_key(b))


def email_formats(master, welfare, profiles, pages, cache, site_emails, resolve) -> dict:
    """Domains whose published personal addresses show a format, with evidence from named people on file (master and welfare
    contacts, contact-profile people) matched against every published address (database fields, profiles, cached pages)."""
    import contact_lib as C  # noqa: E402
    people = defaultdict(list)   # (db, oid) -> [(name, role, verification, pdpa, contact_id, own addresses)]
    domain_of = {}
    for o in master.execute("SELECT organisation_id, website, email FROM organisations"):
        domain_of[("master", o["organisation_id"])] = R.domain(o["website"])
    for o in welfare.execute("SELECT organisation_id, domain, website FROM organisations"):
        domain_of[("welfare", o["organisation_id"])] = (o["domain"] or R.domain(o["website"]) or "").lower()
    for c in master.execute("SELECT * FROM contacts"):
        people[("master", c["organisation_id"])].append({"name": c["name"] or "", "role": c["role"] or "", "verification": c["verification"] or "",
                                                         "own": I.addresses(c["named_email"], c["published_role_email"]), "db": "master",
                                                         "all": I.addresses(c["named_email"], c["published_role_email"], c["shared_email"])})
    for c in welfare.execute("SELECT * FROM contacts"):
        people[("welfare", c["organisation_id"])].append({"name": c["name"] or "", "role": c["role"] or "", "verification": c["role_certainty"] or "",
                                                          "own": I.addresses(c["named_email"], c["published_role_email"]), "db": "welfare",
                                                          "all": I.addresses(c["named_email"], c["published_role_email"], c["shared_email"])})
    published = defaultdict(set)  # domain -> addresses published anywhere we hold
    names_at = defaultdict(list)  # domain -> person names known at organisations using it
    orgs_at = defaultdict(set)
    for key, ps in people.items():
        for p in ps:
            for a in p["all"]:
                published[a.split("@")[1]].add(a)
    for o in master.execute("SELECT organisation_id, email FROM organisations"):
        for a in I.addresses(o["email"]):
            published[a.split("@")[1]].add(a)
    for o in welfare.execute("SELECT organisation_id, email FROM organisations"):
        for a in I.addresses(o["email"]):
            published[a.split("@")[1]].add(a)
    for p in profiles:
        if p["db"] not in ("master", "welfare"):
            continue
        key = (p["db"], p["organisation_id"])
        for e in p.get("emails", []):
            published[e["email"].lower().split("@")[-1]].add(e["email"].lower())
        for x in p.get("people", []):
            if x.get("email"):
                published[x["email"].lower().split("@")[-1]].add(x["email"].lower())
        site = domain_of.get(key) or ""
        names = [x["name"] for x in p.get("people", [])] + [q["name"] for q in people.get(key, [])]
        for a in set().union(*[set(I.addresses(e["email"])) for e in p.get("emails", [])] or [set()]):
            names_at[a.split("@")[1]] += names
            orgs_at[a.split("@")[1]].add(key)
        if site:
            names_at[site] += names
            orgs_at[site].add(key)
    cache_domains = 0
    for key in list(pages):
        if key[0] not in ("master", "welfare"):
            continue
        found = site_emails(key)
        if found:
            cache_domains += 1
        for a in found:
            published[a.split("@")[1]].add(a)
    for key, ps in people.items():
        for p in ps:
            for a in p["all"]:
                names_at[a.split("@")[1]].append(p["name"])
                orgs_at[a.split("@")[1]].add(key)
    stats = Counter()
    formats = {}
    for domain, addrs in published.items():
        if FREE.search("@" + domain):
            continue
        names = [n for n in dict.fromkeys(names_at.get(domain, [])) if n]
        evidence = []
        for a in sorted(addrs):
            local = a.split("@")[0]
            if local in I.GENERIC or ROLEISH.match(local) or re.fullmatch(r"[a-z]{1,3}", local):
                continue
            for n in names:
                first, last = I.name_parts(n)
                pat = I.pattern_of(local, first, last) if first and last else None  # full names only: one-name evidence is ambiguous
                if pat:
                    evidence.append((pat, a, n))
                    break
        if not evidence:
            continue
        votes = Counter(p for p, _, _ in evidence)
        top, n_top = votes.most_common(1)[0]
        if len(votes) > 1:
            stats["domains: ambiguous (mixed patterns)"] += 1
            formats[domain] = {"status": "ambiguous", "votes": dict(votes), "evidence_addresses": [a for _, a, _ in evidence]}
            continue
        stats[f"domains: one pattern, {'2+' if n_top >= 2 else '1'} evidence"] += 1
        formats[domain] = {"status": "ok", "pattern": top, "evidence": n_top, "evidence_addresses": [a for _, a, _ in evidence],
                           "organisations": sorted("/".join(k) for k in orgs_at.get(domain, set()))}
    stats["domains with any non-free published address"] = sum(1 for d in published if not FREE.search("@" + d))
    stats["organisations with cached pages that show any address"] = cache_domains
    stats["patterns"] = dict(Counter(f["pattern"] for f in formats.values() if f["status"] == "ok"))
    # Named decision-makers without a published own address at a domain with a clear format: candidates the track would make
    would, per_domain = Counter(), Counter()
    for key, ps in people.items():
        site = domain_of.get(key) or ""
        doms = {d for d in [site] + [a.split("@")[1] for p in ps for a in p["all"]] if d and d in formats and formats[d]["status"] == "ok"}
        if not doms:
            continue
        for p in ps:
            dm = (R.role_rank(p["role"]) is not None) if key[0] == "master" else bool(C.DECISION.search(C.NOT_A_HEAD.sub("", p["role"])))
            if not dm or p["own"]:
                continue
            first, last = I.name_parts(p["name"])
            label = "master" if key[0] == "master" else "welfare"
            if not (first and last) or R.UNUSABLE.search(p["verification"]):
                would[f"{label}: skipped (one name, incomplete or risky)"] += 1
                continue
            best = max(doms, key=lambda d: formats[d]["evidence"])
            strength = "2+" if formats[best]["evidence"] >= 2 else "1"
            would[f"{label}: candidate possible ({strength} evidence)"] += 1
            per_domain[f"{label} {best}"] += 1
    stats["decision_makers_who_would_get_a_candidate"] = dict(would)
    stats["organisations_with_a_candidate"] = dict(Counter(k.split()[0] for k in per_domain))
    stats["_formats"] = formats
    stats["_candidates_per_domain"] = dict(per_domain.most_common())
    return dict(stats)


if __name__ == "__main__":
    sys.exit(main())
