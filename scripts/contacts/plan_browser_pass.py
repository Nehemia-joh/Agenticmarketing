#!/usr/bin/env python3
"""Plan a browser pass over the organisations' own websites the crawler could not use. No network calls; reads the crawl
file, its HTTP cache and runtime/contacts/profiles.json (run build_contact_profiles.py first).

Two kinds of site:
- robots: the crawler found that robots.txt disallows crawling. By the user's decision (24 September 2026) such a site is
  read with a browser, as a visitor would; everything taken from it is tagged risky (people pdpa_risk "risky", the
  organisation flagged "robots.txt disallows (read with a browser)").
- script: a page the crawler read (HTTP 200) that gave no email, phone or person and holds little visible text, because
  script builds it; a browser renders it. robots.txt allows these.
Sites that already have a record in browser_*_<date>.jsonl are left out. The script sites are sorted by what their
organisations lack (no route first, then no named decision-maker) and split into at most --slices slices.

Writes runtime/contacts/slices/browser_<kind>[_<n>].json and one prompt per slice in runtime/contacts/prompts/, and
prints the plan. Agents use only the built-in browser tools, each in its own tab: no web search. Launch at most four
research agents at a time (skills/silverleaf-create-lead-list/references/research-rate-limits.md).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import contact_lib as C

LITTLE_TEXT = 800  # visible characters on every cached page of a readable site that gave nothing
CAPTURE = (r"""(() => { const abs = a => { try { return new URL(a.getAttribute('href'), location.href).href } catch(e) { return '' } }; """
           r"""const as = [...document.querySelectorAll('a[href]')]; const hrefs = as.map(a => a.getAttribute('href') || ''); """
           r"""const mail = [...new Set(hrefs.filter(h => /^mailto:/i.test(h)).map(h => decodeURIComponent(h.replace(/^mailto:/i,'').split('?')[0])))]; """
           r"""const tel = [...new Set(hrefs.filter(h => /^(tel:|callto:|https?:\/\/(wa\.me|api\.whatsapp))/i.test(h)))]; """
           r"""const social = [...new Set(as.map(abs).filter(h => /facebook\.com|instagram\.com|linkedin\.com|twitter\.com|\/\/(www\.)?x\.com|youtube\.com|tiktok\.com/i.test(h)))].slice(0, 12); """
           r"""const host = location.hostname.replace(/^www\./, ''); """
           r"""const kw = /contact|about|team|staff|leader|board|founder|management|who-we-are|our-story|people|trustee|mawasiliano|kuhusu|uongozi/i; """
           r"""const links = [...new Map(as.map(a => [abs(a).split('#')[0], (a.innerText || a.title || '').trim().replace(/\s+/g, ' ').slice(0, 50)]).filter(([h, t]) => { try { return h && new URL(h).hostname.replace(/^www\./, '') === host && (kw.test(h) || kw.test(t)) } catch(e) { return false } })).entries()].slice(0, 12); """
           r"""const text = document.body ? document.body.innerText : ''; """
           r"""const emailsInText = [...new Set((text.match(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g) || []))].slice(0, 12); """
           r"""return {title: document.title, url: location.href, mail, emailsInText, tel, social, links, textLength: text.length}; })()""")

PROMPT = """You are a browser research agent for Silverleaf Academy (a private English-medium school network in Arusha, Usa River and
Boma Ng'ombe, Tanzania). You read organisations' own websites that the crawler could not use. You use ONLY the built-in browser
tools (mcp__Claude_Browser__*). Do not use WebSearch or WebFetch.

Slice: runtime/contacts/slices/{slice}.json — sites, each with `domain`, `start_url`, `why` and `orgs` (db, organisation_id, name).
{kind_rules}
## Your own browser tab
The browser pane is shared. First call `mcp__Claude_Browser__tabs_create` on its own and pass the returned tabId in EVERY later
browser call. Never use or close another tab; close yours when you finish.

## For each site
1. `navigate` to start_url; if it fails, try once each with the other scheme and with or without `www.`. Nothing loads: status
   `blocked`, reason "not reachable".
2. A bot check or challenge (CAPTCHA, "verify you are human", "checking your browser", anti-robot validation, BitNinja,
   Cloudflare), a login wall, an HTTP error page, a certificate warning, or parked, expired, for-sale or gambling content: do NOT
   interact. Record `blocked` (or note that the domain no longer belongs to the organisation) and move on. Never solve a CAPTCHA,
   click through a warning, log in, fill in or submit a form, or accept a cookie banner (only "reject" or "necessary only").
3. Run this capture with `javascript_tool` (`javascript_exec`), exactly as written, then `get_page_text` (max_chars 8000):
```
{capture}
```
4. Open at most 4 more pages of the same site from the capture's `links` (contact, about, team, leadership, management, board,
   founder), one at a time, reading each the same way. Never more than 5 pages per site.

## What to record: only what the organisation publishes for contact
- Role or general emails, phones as printed, postal address, physical address, official social pages from the site's own links.
- People who lead or decide for it (founder, owner, director, CEO, general manager, head, principal, coordinator, HR,
  administrator, chair, trustee): name and role exactly as published, all of them, most senior first (a first name only is recorded as given); a work email or phone only
  when the same page gives it for that person.
- Never: personal social profiles, home addresses, family details, photos, biographies, anything about children, parents or
  residents (a children's home names children: never record them), party affiliation, or theme placeholder links.
- Evidence for every fact: page URL, `fetched: true`, an excerpt of 25 words or fewer from the page.
- Identity: confirm the site is the organisation's (same name and place); otherwise `identity: "uncertain"` and say why.

## Output
Append one JSON line per organisation to data/raw/contact-research/{slice}_{date}.jsonl as you finish each site. Fields: db,
organisation_id, organisation_name (from the slice), status (found|partial|not_found|blocked), identity (confirmed|uncertain),
method "browser", robots "{robots}", searches_used 0, website (final URL of the home page), emails [{{value, type, source_url,
fetched, excerpt}}], phones [{{value, type, source_url, fetched, excerpt}}], postal_address {{value, source_url}}, physical_address
{{value, source_url}}, socials [{{platform, url, source_url}}], people [{{name, role, email, phone, source_url, fetched, excerpt,
pdpa_risk, pdpa_risk_reason}}], sources [{{url, title, fetched: true, accessed_on, excerpt, facts}}], pages_read [urls], notes.
Say in notes if an organisation looks closed, outside the Arusha-Kilimanjaro area, the same as another record, or a different
kind of business. Write a coverage log to data/raw/contact-research/coverage/{slice}_coverage.md (every site: pages read and what
was found, or why it was blocked). Keep scratch files under runtime/contacts/agents/{slice}/; change no other file and contact no
one. Finish with a short report.
"""
KIND_RULES = {
    "robots": ("These sites' robots.txt disallows crawling. By the user's decision (24 September 2026) read them as a visitor would; "
               "tag every person `pdpa_risk: \"risky\"` with the reason \"" + C.ROBOTS_BROWSER_RISK + "\", and say so in each record's notes.\n"),
    "script": "These sites' pages are built by script, so a crawler saw little text; robots.txt allows them. Per person, `pdpa_risk` is "
              "`medium` for a named professional as published, `low` for a role desk, `risky` for a named person on a personal email domain.\n"}


def visible_text(url: str) -> int:
    body = C.fetch(url).get("body") or b""
    text = re.sub(rb"<script.*?</script>|<style.*?</style>", b" ", body, flags=re.S | re.I)
    return len(b" ".join(re.sub(rb"<[^>]+>", b" ", text).split()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="research date, as in website_contacts_<date>.jsonl")
    parser.add_argument("--slices", type=int, default=2, help="split the script-built sites into at most this many slices")
    args = parser.parse_args()
    C.OFFLINE = True
    crawl = [json.loads(line) for line in (C.RAW / f"website_contacts_{args.date}.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    profiles = {(p["db"], p["organisation_id"]): p for p in json.loads((C.WORK / "profiles.json").read_text(encoding="utf-8"))["profiles"]}
    done = set()
    for path in C.RAW.glob(f"browser_*_{args.date}.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r.get("db"), r.get("organisation_id")))
    targets = {"robots": [], "script": []}
    for site in crawl:
        orgs = [o for o in site["orgs"] if (o["db"], o["organisation_id"]) not in done]
        if not orgs:
            continue
        readable = [p for p in site["pages"] if p.get("status") == 200 and p.get("kind") not in ("spam", "unreadable")]
        if site.get("robots") == "disallowed":
            kind = "robots"
        elif readable and not (site["emails"] or site["phones"] or site["people"]) and max(visible_text(p["final_url"]) for p in readable) < LITTLE_TEXT:
            kind = "script"
        else:
            continue
        lacks = [{"db": o["db"], "organisation_id": o["organisation_id"], "name": o["name"],
                  "route": bool(profiles.get((o["db"], o["organisation_id"]), {}).get("emails") or profiles.get((o["db"], o["organisation_id"]), {}).get("phones")),
                  "decision_makers": sum(1 for x in profiles.get((o["db"], o["organisation_id"]), {}).get("people", []) if x.get("decision_maker"))}
                 for o in orgs]
        targets[kind].append({"domain": site["domain"], "start_url": site["start_url"], "why": kind, "orgs": lacks})
    targets["script"].sort(key=lambda t: (any(o["route"] for o in t["orgs"]), max(o["decision_makers"] for o in t["orgs"]) > 0))
    slices = [("browser_robots", "robots", targets["robots"])] if targets["robots"] else []
    n = max(1, min(args.slices, len(targets["script"])))
    size = -(-len(targets["script"]) // n) if targets["script"] else 0
    for i in range(n if targets["script"] else 0):
        part = targets["script"][i * size:(i + 1) * size]
        if part:
            slices.append((f"browser_sites_{chr(97 + i)}" if n > 1 else "browser_sites", "script", part))
    out_dir, prompt_dir = C.WORK / "slices", C.WORK / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir.mkdir(parents=True, exist_ok=True)
    plan = []
    for name, kind, part in slices:
        (out_dir / f"{name}.json").write_text(json.dumps(part, indent=1, ensure_ascii=False), encoding="utf-8")
        (prompt_dir / f"{name}.md").write_text(PROMPT.format(slice=name, date=args.date, kind_rules=KIND_RULES[kind], capture=CAPTURE,
                                                             robots="disallowed" if kind == "robots" else "allowed"), encoding="utf-8")
        plan.append({"slice": name, "kind": kind, "sites": len(part), "prompt": str(Path("runtime/contacts/prompts") / f"{name}.md")})
    print(json.dumps({"date": args.date, "slices": plan, "already_read": len(done)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
