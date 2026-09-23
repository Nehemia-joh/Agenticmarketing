#!/usr/bin/env python3
"""Plan a research wave for first-message hooks and lead briefs, one slice per research agent.

Reads the company master (read-only) and selects the outreach plans on one acquisition track (AQ02, the named
decision-makers, by default). Groups them by organisation and splits the organisations into slices. Writes, per slice,
runtime/hooks/<slice>/leads.json and the agent's prompt runtime/hooks/<slice>/prompt.md.

Each agent does three things per organisation. It confirms each named contact's role on the page it came from. It
records a short lead brief: facts, each with its source URL, the page title and date, and a verbatim excerpt, so a
person can learn about the lead quickly if they reply. And it writes one second-person hook sentence when a fact gives
a real reason for the request.

Each agent writes data/raw/hook-research/hooks_<slice>_<date>.jsonl and a coverage log. The search budget is split
evenly after holding back 10% for the coordinator (skills/silverleaf-create-lead-list/references/research-rate-limits.md).
Merge the results with scripts/messaging/apply_hook_research.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from datetime import date
from pathlib import Path

import offer_lib as L

ROOT = L.ROOT
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
WORK = ROOT / "runtime" / "hooks"
RAW = ROOT / "data" / "raw" / "hook-research"

PROMPT = """You are researching {count} Silverleaf Academy leads, organisations near Arusha, Tanzania, for two reasons:
- so that each first email can carry one verified, relevant reason;
- so that Mariam Haji, who signs the emails, can learn about a lead quickly if they reply.

Silverleaf Academy is a private English-medium school: Daycare to Grade 7, with five campuses in Arusha, Usa River and Boma Ng'ombe. The first email asks each organisation for a short meeting about an education benefit for the children of its staff. It opens with the sentence in each lead's "purpose".

Your leads: {leads_path}
(JSON: for each organisation, its website, the purpose sentence, and the named contacts we will write to, each with the page where they were found.)

## Budget and pacing (hard rules)

- **WebSearch:** at most {budget} searches, numbered Q1/{budget}, Q2/{budget} ... in your coverage log.
  - If a search is refused because the session's search limit is reached, stop searching at once. Do not retry; continue only with pages you already have.
  - Never route searches through WebFetch, a browser or a search-results page.
- **Read pages with:** `python scripts/contacts/read_page.py <url> [--grep word ...]`, run from {root}.
  - It caches pages, spaces requests to a site 1.5 s apart, honours robots.txt Disallow and reports blocks.
  - Use WebFetch only when read_page cannot read a page, and then quote only text the page shows.
  - Never work around a block (403, 429, captcha, login wall): record it and move on.
- **Fetch first:** these pages cost no search:
  - the organisation's own website: home, about, team, careers, community, CSR or foundation, and news pages;
  - each contact's source_url.
- **Search only when** the organisation's own pages give no usable fact. Use one organisation per query, for example "<exact name>" Arusha.

## For each organisation

1. **Role check.** Re-open each contact's source_url and record whether the page still names the person with that role:
   - confirmed: the same person, with the same or an equivalent role;
   - changed: the person is listed with a different role, or someone else now holds the role;
   - not_found: the page is readable, but the person is not on it;
   - unreachable: the page cannot be read.

   Quote the line that shows it.
2. **Lead brief.** Record up to five facts that would help Mariam understand the organisation in a first conversation, as the organisation or a reliable source publishes them:
   - what it does, and where;
   - its size or workforce (staff numbers, teams, offices);
   - community, education or staff-welfare programmes;
   - growth or recent news;
   - recognition.

   For each fact, give the exact page URL, the page title, the page's own date if it shows one, and a verbatim excerpt (at most 300 characters) that states the fact. Do not record a fact without both a URL and a verbatim excerpt.
3. **Hook.** Write a hook only when one brief fact gives a real reason why an education benefit for the children of staff fits this organisation.
   - Write one sentence for the first email, in the second person, supported entirely by that fact. It follows the purpose sentence.
   - Pattern: the fact, then why the benefit fits.
   - Good bases: a published workforce size or team structure; long-serving staff; offices or teams in or near Arusha; a staff-welfare, education or community programme; expansion or hiring.
   - Examples:
     - "Your team page says some of your staff have been with you for over 15 years, so such a benefit could reward that loyalty."
     - "Your website lists more than 60 guides, cooks and porters based in Arusha, so such a benefit could reach a wide team."
     - "Your foundation already supports schools around Karatu, so an education benefit for your own staff would fit that commitment."
   - Rules:
     - Every number and name in the sentence must appear in the cited excerpt.
     - No praise without relevance.
     - Never say or imply that staff are parents or need school places. Words such as "families" or "parents" imply it.
     - Do not turn vehicle, bed, room or customer counts into staff counts.
     - No offer terms: no discounts, prices or percentages.
     - At most 35 words.
   - If no fact supports a hook, set "hook" to null. No hook is better than a weak or inaccurate one.
   - {special}
4. **Privacy.** Record only what the organisation or an official source publishes for the public.
   - Never record personal social profiles, home addresses, family details, biographies, personal phone numbers, anything about children, or party affiliation.
   - About contacts, record only the published name and role.

## Output

As you finish each organisation, append one JSON line to {output_path}, including organisations where nothing was found:
{{"organisation_id": "...", "organisation_name": "...", "status": "found|partial|not_found|blocked", "searches_used": 0,
 "brief": [{{"type": "what_they_do|workforce|locations|education_programme|community_programme|staff_welfare|growth|recognition|other",
            "fact": "one plain sentence, no inference", "source_url": "https://...", "source_title": "...", "source_date": "",
            "accessed_on": "{date}", "fetched": true, "excerpt": "verbatim text from the page"}}],
 "hook": {{"sentence": "...", "type": "workforce|staff_welfare|education_programme|community_programme|locality|growth",
           "fact_index": 0, "quality": "strong|moderate"}},
 "contacts": [{{"contact_id": "...", "message_id": "...", "name": "...", "role_on_record": "...",
               "role_check": "confirmed|changed|not_found|unreachable", "role_published": "the role as the page states it now",
               "source_url": "...", "excerpt": "verbatim", "accessed_on": "{date}"}}],
 "notes": "anything a person should check: a possible closure, a different organisation behind the website, a hijacked site, robots.txt could not be read"}}

- "hook" is null when there is none.
- "fact_index" points into "brief".
- Write valid JSON, one object per line, in UTF-8.
- Use "fetched": true only for pages you read yourself. A fact seen only in a search snippet is not recorded.

## Coverage log

At the end, write {coverage_path}. List:
- the queries, numbered;
- the pages read for each organisation;
- blocked or unreadable sources;
- the organisations without a hook, and why;
- any organisation not finished.

Finish when every organisation has a line. Then report in a few lines: organisations done, hooks written, role checks by result, and searches used.
"""


def domain(value) -> str:
    """The first web address in a field that may also hold a slogan ('www.x.com SLOGAN: ...')."""
    m = re.search(r"(?:https?://)?(?:www\.)?[a-z0-9\-]+(?:\.[a-z0-9\-]+)+(?:/[^\s]*)?", str(value or "").lower())
    return m.group(0) if m and not re.fullmatch(r"[\d.\-]+", m.group(0)) else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--track", default="AQ02")
    parser.add_argument("--agents", type=int, default=4, help="at most four research agents per wave")
    parser.add_argument("--budget", type=int, default=48, help="WebSearch calls for the whole wave, before the 10%% reserve")
    parser.add_argument("--database", default=str(MASTER))
    args = parser.parse_args()
    agents = max(1, min(args.agents, 4))
    con = sqlite3.connect(f"file:{Path(args.database).resolve().as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute("""SELECT p.message_id, p.target_type, p.target_id, p.organisation_id, p.segment, o.name, o.website, o.locality,
                                 c.name AS contact_name, c.role, c.source_url
                          FROM outreach_plans p JOIN organisations o USING(organisation_id)
                          LEFT JOIN contacts c ON c.contact_id = p.target_id AND p.target_type = 'contact'
                          WHERE p.acquisition_track_id = ? ORDER BY o.name, p.message_id""", (args.track,)).fetchall()
    orgs = {}
    for r in rows:
        name = L.display_name(r["name"])
        o = orgs.setdefault(r["organisation_id"], {
            "organisation_id": r["organisation_id"], "organisation_name": r["name"], "website": domain(r["website"]),
            "locality": r["locality"] or "", "segment": r["segment"], "contacts": [], "organisation_route_message_ids": [],
            "purpose": (f"I am writing to explore how Silverleaf Academy could support the education of {name} members' children, and would "
                        f"like to speak with your committee." if r["segment"] == "SACCOS members" else
                        f"I am writing to explore an education benefit for the children of staff at {name}.")})
        if r["name"].startswith("Rivertrees"):
            o["purpose"] = "Existing relationship: the first email renews the 2025 staff education partnership. Brief only; the hook must be null."
        if r["target_type"] == "contact":
            o["contacts"].append({"contact_id": r["target_id"], "message_id": r["message_id"], "name": r["contact_name"], "role": r["role"] or "",
                                  "source_url": r["source_url"] or ""})
        else:
            o["organisation_route_message_ids"].append(r["message_id"])
    con.close()
    ordered = sorted(orgs.values(), key=lambda o: (o["segment"], o["organisation_name"].lower()))
    slices = [ordered[i::agents] for i in range(agents)]
    per_agent = (args.budget * 90 // 100) // agents
    WORK.mkdir(parents=True, exist_ok=True)
    (RAW / "coverage").mkdir(parents=True, exist_ok=True)
    summary = []
    for i, part in enumerate(slices):
        name = f"hooks_{chr(ord('a') + i)}"
        folder = WORK / name
        folder.mkdir(parents=True, exist_ok=True)
        leads_path = folder / "leads.json"
        leads_path.write_text(json.dumps(part, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        output_path = RAW / f"{name}_{args.date}.jsonl"
        coverage_path = RAW / "coverage" / f"{name}_coverage.md"
        special = ("Rivertrees Country Inn is an existing relationship: record its brief, and set hook to null."
                   if any(o["organisation_name"].startswith("Rivertrees") for o in part) else
                   "Every organisation here gets the employer purpose sentence, except a savings group, whose hook follows the committee sentence.")
        prompt = PROMPT.format(count=len(part), leads_path=leads_path.relative_to(ROOT).as_posix(), budget=per_agent, root=ROOT.as_posix(),
                               output_path=output_path.relative_to(ROOT).as_posix(), coverage_path=coverage_path.relative_to(ROOT).as_posix(),
                               date=args.date, special=special)
        (folder / "prompt.md").write_text(prompt, encoding="utf-8")
        summary.append({"slice": name, "organisations": len(part), "contacts": sum(len(o["contacts"]) for o in part), "searches": per_agent,
                        "prompt": (folder / "prompt.md").relative_to(ROOT).as_posix(), "output": output_path.relative_to(ROOT).as_posix()})
    print(json.dumps({"track": args.track, "organisations": len(ordered), "plans": len(rows), "budget": args.budget,
                      "reserve": args.budget - per_agent * agents, "slices": summary}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
