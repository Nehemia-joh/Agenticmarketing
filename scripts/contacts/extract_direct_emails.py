#!/usr/bin/env python3
"""Find, in pages already crawled from organisations' own websites, the published work address of a named decision-maker the
databases already hold (high-direct plan D-1 and D-2, docs/plans/high-direct-wave-2026-10-11.md). No network: every page is
read from the HTTP cache (runtime/contacts/http-cache, or CONTACTS_CACHE_FALLBACK in a worktree); databases are read-only.

For each decision-maker on file (company master and welfare run) without a published address of their own, an address on the
organisation's own domain, published on its own website, is tied to the person only by one of these rules (decided by the user on
11 October 2026, D1 and D2):
- same block: the address sits in the person's block on the same page (the line that names them or the next three lines, before
  the next person's name), and no other person of the organisation owns the mailbox by name;
- name-matched on own site: the mailbox carries the person's name by the strict test (contact_lib.mailbox_owner: first name at the
  start, the surname, or first initial and surname) and no other listed person of the organisation matches it as strongly;
- role inbox for role: md@, ceo@, gm@, dg@, vc@, principal@, rector@, registrar@, hr@ ... when the person holds exactly that role
  and is the only person on file who does (for the company master, only someone running the Tanzania or Arusha operation).
Free-mail addresses, other people's mailboxes and desk inboxes (info@, sales@ ...) are never tied to anyone. Nothing is inferred
from a pattern: an address counts only when a page publishes it.

Output (--write): data/raw/contact-research/website_direct_<date>.jsonl, one record per organisation with a finding, in the agent
brief's format (method website, fetched, identity confirmed, an excerpt of 25 words or fewer, email_link and source_type on each
person). update_master_contacts.py fills the master contacts' named_email or published_role_email from it, and
build_contact_profiles.py reads it for the welfare run. Default: preview to stdout. --self-test runs the rule fixtures.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

import contact_lib as C

W = C.W
ROOT = C.ROOT
sys.path.insert(0, str(ROOT / "scripts" / "master"))
import resolve_master_recipients as R  # noqa: E402  (role ranks, the on-the-ground rule)

DATABASES = {"master": ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite",
             "welfare": ROOT / "outputs" / "runs" / "arusha-welfare-2026-09" / "lead-database.sqlite"}
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
MAILTO = re.compile(rb"""<a\b[^>]*href\s*=\s*["']mailto:([^"'?>]+)[^>]*>""", re.I)
CFEMAIL = re.compile(rb"""data-cfemail\s*=\s*["']([0-9a-fA-F]+)["']""")
CF_LINK = re.compile(rb"/cdn-cgi/l/email-protection#([0-9a-fA-F]+)")
# Role inboxes and the role each belongs to (D2: exactly that role; a deputy, assistant or vice holder never).
ROLE_INBOX = [
    (re.compile(r"^(md|managingdirector)$"), re.compile(r"managing director|\bmd\b", re.I)),
    (re.compile(r"^ceo$"), re.compile(r"\bceo\b|chief executive", re.I)),
    (re.compile(r"^gm$"), re.compile(r"general manager", re.I)),
    (re.compile(r"^(dg|directorgeneral)$"), re.compile(r"director[- ]general|mkurugenzi mkuu", re.I)),
    (re.compile(r"^vc$"), re.compile(r"vice[- ]?chancellor", re.I)),
    (re.compile(r"^principal$"), re.compile(r"\bprincipal\b", re.I)),
    (re.compile(r"^rector$"), re.compile(r"\brector\b", re.I)),
    (re.compile(r"^registrar$"), re.compile(r"\bregistrar\b", re.I)),
    (re.compile(r"^(ed|edr|executivedirector)$"), re.compile(r"executive director", re.I)),
    (re.compile(r"^(cd|countrydirector)$"), re.compile(r"country director", re.I)),
    (re.compile(r"^(es|executivesecretary)$"), re.compile(r"executive secretary", re.I)),
    (re.compile(r"^(headteacher|headmaster|headofschool)$"), re.compile(r"head ?teacher|headmaster|headmistress|head of school", re.I)),
    (re.compile(r"^(hr|hrm|humanresources?|dhrma|hrmanager)$"), re.compile(r"(head|manager|director|chief|officer)\b.*(human resource|\bhr\b)|"
                                                                         r"(human resource|\bhr\b).*(head|manager|director|chief)", re.I)),
]
NOT_HOLDER = re.compile(r"deputy|assistant|\bvice\b(?![- ]?chancellor)|\bass\.|former|retired|emeritus|board|non-executive", re.I)


def ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def registrable(host: str) -> str:
    return C.registrable(host) if host else ""


def site_of(website: str) -> str:
    """The registrable domain of a website field, '' when the field holds no usable address (free text, a bracketed note)."""
    token = str(website or "").strip().split()[0] if str(website or "").strip() else ""
    try:
        return registrable(W.own_domain(token))
    except ValueError:
        return ""


def own_address(address: str, site_domains: set) -> bool:
    host = address.split("@")[-1].lower()
    return bool(site_domains) and not W.PERSONAL_EMAIL.search(address) and registrable(host) in site_domains


def expose_addresses(body: bytes) -> bytes:
    """The page with every mailto and Cloudflare-protected address written out as text where it stands, so a person's block shows it."""
    body = MAILTO.sub(lambda m: m.group(0) + b" " + m.group(1) + b" ", body)
    body = CF_LINK.sub(lambda m: m.group(0) + b'">' + C.decode_cfemail(m.group(1).decode()).encode() + b"<x x=\"", body)
    return CFEMAIL.sub(lambda m: m.group(0) + b">" + C.decode_cfemail(m.group(1).decode()).encode() + b"<x x=\"\"", body)


def page_lines(body: bytes) -> list[str]:
    lines, _ = C.html_lines(expose_addresses(body))
    return lines


def emails_in(line: str) -> list[str]:
    return [e for e in (C.clean_email(m.group(0)) for m in EMAIL.finditer(line)) if e]


def names_line(line: str, name: str) -> bool:
    """The line names the person: their first name and surname as words (titles and initials ignored)."""
    first, last = C.mailbox_name_parts(name)
    if not first or not last:
        return False
    words = {C._fold(w) for w in re.findall(r"[^\W\d_]+", line)}
    return first in words and last in words


def excerpt(text: str, address: str = "") -> str:
    words = text.split()
    if len(words) <= 25:
        return text
    if address and address in text.lower():
        i = next((k for k, w in enumerate(words) if address in w.lower()), 0)
        start = max(0, min(i - 12, len(words) - 25))
        return " ".join(words[start:start + 25])
    return " ".join(words[:25])


def role_inbox_for(local: str, role: str) -> bool:
    letters = re.sub(r"[^a-z]", "", local.lower())
    return any(box.match(letters) and holder.search(role or "") and not NOT_HOLDER.search(role or "") for box, holder in ROLE_INBOX)


def find_for_org(pages: list[tuple[str, list[str]]], site_domains: set, targets: list[dict], everyone: list[str], desk=frozenset()) -> list[dict]:
    """Findings for one organisation: [{person, address, email_link, source_url, excerpt}]. pages: [(url, lines)]; targets: the people
    who need an address (name, role, in_country); everyone: every person's name known for the organisation (for ownership); desk: the
    organisation's own general inboxes on file, which are never a person's."""
    found, seen = [], set()
    on_site = {}
    for url, lines in pages:
        for i, line in enumerate(lines):
            for address in emails_in(line):
                if own_address(address, site_domains) and address not in desk:
                    on_site.setdefault(address, (url, line))
    for t in targets:
        name = t["name"]
        # 1. same block
        for url, lines in pages:
            for i, line in enumerate(lines):
                if not names_line(line, name) or any(names_line(line, o) for o in everyone if o != name and not C.same_person(o, name)):
                    continue
                block = [line]
                for nxt in lines[i + 1:i + 4]:
                    if any(names_line(nxt, o) for o in everyone if o != name and not C.same_person(o, name)):
                        break
                    block.append(nxt)
                for text in block:
                    for address in emails_in(text):
                        local = address.split("@")[0]
                        if not own_address(address, site_domains) or address in desk or (address, name) in seen:
                            continue
                        owner = C.mailbox_owner(address, everyone)
                        if owner and not C.same_person(owner, name) and W.name_key(owner) != W.name_key(name):
                            continue  # another person's mailbox printed near this person
                        if C.ROLE_LOCALS.match(re.sub(r"[^a-z]", "", local)) and not role_inbox_for(local, t["role"]):
                            continue  # a desk inbox in the block (info@, sales@) is not the person's
                        link = "role inbox for role" if role_inbox_for(local, t["role"]) else "same block"
                        if link == "role inbox for role" and not t["sole_holder"]:
                            continue
                        seen.add((address, name))
                        found.append({"person": name, "address": address, "email_link": link, "source_url": url,
                                      "excerpt": excerpt(" ".join(block), address)})
        # 2. name-matched anywhere on the organisation's own site
        for address, (url, line) in sorted(on_site.items()):
            if (address, name) in seen:
                continue
            if C.mailbox_owner(address, everyone, name):
                seen.add((address, name))
                found.append({"person": name, "address": address, "email_link": "name-matched on own site", "source_url": url,
                              "excerpt": excerpt(line, address)})
        # 3. the inbox for the person's role
        if t["sole_holder"] and t["in_country"]:
            for address, (url, line) in sorted(on_site.items()):
                if (address, name) not in seen and role_inbox_for(address.split("@")[0], t["role"]):
                    seen.add((address, name))
                    found.append({"person": name, "address": address, "email_link": "role inbox for role", "source_url": url,
                                  "excerpt": excerpt(line, address)})
    # One address per person and kind: same block before name-matched; a role inbox only fills published_role_email.
    best = {}
    order = {"same block": 0, "name-matched on own site": 1, "role inbox for role": 2}
    for f in found:
        kind = "role" if f["email_link"] == "role inbox for role" else "own"
        key = (f["person"], kind)
        if key not in best or order[f["email_link"]] < order[best[key]["email_link"]]:
            best[key] = f
    # An address tied to two different people is no one's.
    owners = defaultdict(set)
    for f in best.values():
        owners[f["address"]].add(W.name_key(f["person"]))
    return [f for f in best.values() if len(owners[f["address"]]) == 1]


def load_crawl(resolve) -> dict:
    """{(db, organisation_id): [record]} from every crawl file: per site, the deep record first, then the newest."""
    by_domain = {}
    for path in sorted(C.RAW.glob("website_contacts_*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            old = by_domain.get(rec["domain"])
            if old is None or (bool(rec.get("deep")), rec.get("fetched_on", "")) >= (bool(old.get("deep")), old.get("fetched_on", "")):
                by_domain[rec["domain"]] = rec
    out = defaultdict(list)
    for rec in by_domain.values():
        for o in rec["orgs"]:
            key = resolve(o["db"], o["organisation_id"], o["name"])
            if key:
                out[key].append(rec)
    return out


def people_on_file(db: str, con) -> tuple[dict, dict]:
    """({organisation_id: [person]}, {organisation_id: org}) for one database; a person: name, role, own (published own address),
    decision (a decision-maker), verified, risky, in_country."""
    orgs = {r["organisation_id"]: dict(r) for r in con.execute("SELECT * FROM organisations")}
    people = defaultdict(list)
    rows = [dict(r) for r in con.execute("SELECT * FROM contacts")]
    wide = R.wide_organisations({r["contact_id"]: r for r in rows}) if db == "master" else set()
    for c in rows:
        if not c.get("name"):
            continue
        own = [e for e in R.emails(c.get("named_email"), c.get("published_role_email"))]
        if db == "master":
            verification = c.get("verification") or ""
            decision = R.senior_rank(c) is not None
            risky = bool(R.UNUSABLE.search(verification))
            in_country = R.location(c, c["organisation_id"] in wide) == 0
        else:
            decision = bool(C.DECISION.search(C.NOT_A_HEAD.sub("", c.get("role") or "")))
            risky = c.get("role_certainty") != "confirmed"
            in_country = True
        people[c["organisation_id"]].append({"name": c["name"], "role": c.get("role") or "", "own": own, "decision": decision,
                                             "risky": risky, "in_country": in_country, "contact_id": c["contact_id"]})
    return people, orgs


def self_test() -> int:
    ok = True
    cases = [("camilla.brian@x.com", "Brian Mengoriki", False), ("joshua@x.com", "Joshua Monah", True), ("lctenga@cti.co.tz", "Eng. Leodegar Tenga", True),
             ("fthomas@a.org", "Florence Thomas", True), ("sarap@h.org", "Sara Preston", True), ("jvann@a.org", "Joel Vann", True),
             ("nnko@n.com", "Aminiel Nnko", True), ("ed@x.org", "Edward Mushi", False), ("info@x.com", "Ingrid Fox", False),
             ("mary.mponda@crdb.co.tz", "Godfrey Rutasingwa", False), ("henryobedi.mejooli@a.com", "Henry Obed Mejooli", True),
             ("peter.kroll@dsw.org", "Peter Owaga", False), ("peterkroll@dsw.org", "Peter Owaga", False), ("pmaduki@cssc.or.tz", "Peter Maziku Maduki", True),
             ("vianney.jacob@v.com", "Vianney Jacob Kabwine", True), ("zaharahnamanda@u.org", "Zaharah Namanda", True),
             ("rngusaru@r.co.tz", "Reuben Ngusaru", True), ("edr@kcmc.ac.tz", "Prof. Gileard Masenga", False)]
    for address, name, want in cases:
        if C.mailbox_carries_name(address, name) != want:
            ok = False
            print(f"FAIL strict test: {address} / {name}: expected {want}")
    if C.mailbox_owner("hilde.keil@p.com", ["Hilde Keil", "Robin Keil"]) != "Hilde Keil":
        ok = False
        print("FAIL owner: hilde.keil@ belongs to Hilde Keil although Robin Keil shares the surname")
    if C.mailbox_owner("keil@p.com", ["Hilde Keil", "Robin Keil"]) != "":
        ok = False
        print("FAIL owner: keil@ is ambiguous between two Keils")
    page = (b"<html><body><div class='team'><h3>Brian Mengoriki</h3><p>Founder &amp; Director</p>"
            b"<p><a href='mailto:camilla.brian@eco.com'>Camilla Brian</a></p></div>"
            b"<div><h3>Anna Mushi</h3><p>Managing Director</p><p><a href='mailto:am@eco.com'>am@eco.com</a></p></div>"
            b"<div><h3>Peter Laizer</h3><p>General Manager</p><p>info@eco.com</p></div>"
            b"<footer>Contact <a href='mailto:gm@eco.com'>gm@eco.com</a> or md@eco.com</footer></body></html>")
    lines = page_lines(page)
    everyone = ["Brian Mengoriki", "Camilla Brian", "Anna Mushi", "Peter Laizer"]
    targets = [{"name": "Brian Mengoriki", "role": "Founder & Director", "sole_holder": True, "in_country": True},
               {"name": "Anna Mushi", "role": "Managing Director", "sole_holder": True, "in_country": True},
               {"name": "Peter Laizer", "role": "General Manager", "sole_holder": True, "in_country": True}]
    got = {(f["person"], f["address"], f["email_link"]) for f in find_for_org([("https://eco.com/team", lines)], {"eco.com"}, targets, everyone)}
    want = {("Anna Mushi", "am@eco.com", "same block"), ("Anna Mushi", "md@eco.com", "role inbox for role"),
            ("Peter Laizer", "gm@eco.com", "role inbox for role")}
    if got != want:
        ok = False
        print(f"FAIL fixture page: got {sorted(got)}, expected {sorted(want)}")
    print("self-test passed" if ok else "self-test FAILED")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", default=date.today().isoformat(), help="file suffix: website_direct_<date>.jsonl")
    parser.add_argument("--orgs", type=Path, help="JSON list of organisations ({db, organisation_id}); default: every organisation")
    parser.add_argument("--write", action="store_true", help="write the research file (default: preview)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    C.OFFLINE = True  # never the network: cached pages only
    wanted = None
    if args.orgs:
        wanted = {(o.get("db") or ("welfare" if o.get("track") == "welfare" else "master"), o["organisation_id"])
                  for o in json.loads(args.orgs.read_text(encoding="utf-8"))}
    data = {}
    for db, path in DATABASES.items():
        con = ro(path)
        data[db] = people_on_file(db, con)
        con.close()
    resolve = C.Resolver((db, oid, o["name"]) for db, (_, orgs) in data.items() for oid, o in orgs.items())
    crawl = load_crawl(resolve)
    stats, records, today = Counter(), [], args.date
    for db, (people, orgs) in data.items():
        for oid, o in orgs.items():
            key = (db, oid)
            if wanted is not None and key not in wanted:
                continue
            targets = [p for p in people.get(oid, []) if p["decision"] and not p["risky"] and not p["own"] and C.mailbox_name_parts(p["name"])[1]]
            if not targets:
                stats["organisations without a decision-maker who needs an address"] += 1
                continue
            recs = crawl.get(key, [])
            if not recs:
                stats["organisations without a crawled site"] += 1
                continue
            site_domains = {site_of(o.get("website"))} - {""}
            site_domains |= {registrable(r["domain"]) for r in recs}
            pages, robots_flag = [], ""
            for rec in recs:
                if rec.get("robots") == "unreachable":
                    robots_flag = f"{rec['domain']}: robots.txt could not be read; the site was crawled anyway"
                for pg in rec["pages"]:
                    if pg.get("status") != 200 or pg.get("kind") == "spam":
                        continue
                    result = C.fetch(pg["url"])
                    if result.get("status") == 200 and result.get("body"):
                        pages.append((pg.get("final_url") or pg["url"], page_lines(result["body"])))
            if not pages:
                stats["organisations whose pages are not in the cache"] += 1
                continue
            everyone = [p["name"] for p in people.get(oid, [])] + [x["name"] for rec in recs for x in rec.get("people", [])]
            for p in targets:
                holders = [q for q in people.get(oid, []) if q["decision"] and W.name_key(q["name"]) != W.name_key(p["name"])
                           and any(holder.search(q["role"]) and holder.search(p["role"]) for _, holder in ROLE_INBOX)]
                p["sole_holder"] = not holders
            desk = {a.lower() for a in EMAIL.findall(str(o.get("email") or ""))}
            findings = find_for_org(pages, site_domains, targets, everyone, desk)
            stats["organisations searched in the cache"] += 1
            if not findings:
                continue
            by_person = {p["name"]: p for p in targets}
            fetched_on = max((rec.get("fetched_on", "") for rec in recs), default="") or today
            persons, sources = [], []
            for f in findings:
                p = by_person[f["person"]]
                persons.append({"name": p["name"], "role": p["role"], "email": f["address"], "phone": "", "source_url": f["source_url"], "fetched": True,
                                "excerpt": f["excerpt"], "pdpa_risk": "medium",
                                "pdpa_risk_reason": "Work email on the organisation's own domain, published on its own website (" + f["email_link"] + ").",
                                "email_link": f["email_link"], "source_type": "own site"})
                if not any(s["url"] == f["source_url"] for s in sources):
                    sources.append({"url": f["source_url"], "title": "", "fetched": True, "accessed_on": fetched_on, "excerpt": f["excerpt"],
                                    "facts": ["work email of a named decision-maker"]})
                stats[f"addresses: {f['email_link']}"] += 1
            records.append({"db": db, "organisation_id": oid, "organisation_name": o["name"], "status": "found", "identity": "confirmed",
                            "searches_used": 0, "method": "website", "website": o.get("website") or "", "emails": [], "phones": [],
                            "postal_address": {}, "physical_address": {}, "socials": [], "people": persons, "sources": sources,
                            "notes": "Read from the HTTP cache of the organisation's own website by extract_direct_emails.py (no network)."
                                     + (f" {robots_flag}." if robots_flag else "")})
            stats[f"{db}: organisations with a finding"] += 1
    print(json.dumps(dict(sorted(stats.items())), indent=1))
    for r in records:
        for p in r["people"]:
            print(f"  {r['db']} | {r['organisation_name'][:40]} | {p['name']} ({p['role'][:40]}) | {p['email']} | {p['email_link']}")
    if args.write:
        out = C.RAW / f"website_direct_{args.date}.jsonl"
        out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(records)} organisations)")
    else:
        print("Preview only; --write writes the research file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
