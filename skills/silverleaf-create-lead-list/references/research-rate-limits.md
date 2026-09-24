# Research rate limits and budgets

Read this before any lead research that uses web search, web fetch, public registers or map APIs, and before launching research agents in parallel. The figures come from the `arusha-welfare-2026-09` and `arusha-government-2026-09` runs (22–23 September 2026). Treat them as planning defaults, and re-measure when a source behaves differently.

The scripts enforce the network limits in code: `scripts/welfare/welfare_lib.py` (`HOST_LIMITS`, `polite_request`, `clamp_workers`), and `scripts/government/gov_lib.py`, which registers the council, regional, census and Wikipedia hosts. Change a limit there and here together.

## Web search: a shared, per-session cap

- **The cap.** The agent WebSearch tool allows 200 searches per session in this environment (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`). Every subagent in the session draws from the same cap.
- **What happened without budgets.** In the first welfare run, eight parallel research agents used the whole cap in about 40 minutes. Their shares were very uneven: one agent ran 8 searches, another about 58, and one got none. Most slices ended before their stopping rule, so coverage has gaps.
- **Deploying agents:**
  1. Run the deterministic collectors first. They use no search budget: the NGO register (`scripts/welfare/fetch_ngo_register.py`) and OpenStreetMap (`scripts/welfare/collect_osm_welfare.py`).
  2. Split the budget with `scripts/welfare/plan_research.py`. It writes each slice's allocation into the agent's prompt, and keeps 10% back for the coordinator's own checks.
  3. Launch at most four agents per wave. Start the next wave when the previous one finishes, and hand unused searches to the slices with the largest gaps.
  4. Agents number every query in their coverage log (`Q7/25`) and stop at their allocation.
  5. Once searches are spent, agents continue only with WebFetch on URLs they already have. Never route searches through WebFetch, a browser or a search-results page to get around the cap.
- **Raising the cap is the user's decision.** They set the environment variable and start a new session; do not assume it has been raised. When the cap is reached, finish what can be done by fetching known pages, record the unsearched areas, and report them.

## Web fetch

- **No cap was hit, but pace it.** Allow about one request every 2 seconds on the same site. Responses are cached for about 15 minutes per URL.
- **Blocked or unreadable in 2026-09:**
  - UK Charity Commission register (HTTP 403 on 22 September; it answered normally on 23 September, with a robots.txt that allows everything)
  - JamiiForums (blocks automated reading)
  - Facebook groups and many pages (login wall)
  - Reddit (not fetchable)
  - Tanzanian council sites on the GWF CORE framework (pages render in JavaScript and deep links redirect to the home page). Their public JSON API works; see the next section.
- **Handling blocks.** Record a blocked source in the coverage log and move on. Do not retry in a loop, sign in or bypass a bot check.
- **Pages that render in JavaScript** return only a shell. Look for data embedded in the page (the NGO register map embeds every NGO as a JavaScript array) and collect it with a script, or read the page with the built-in browser (next item).
- **Browser pass.** On 24 September 2026 the user allowed the built-in browser for organisations' own websites the crawler could not use (`scripts/contacts/plan_browser_pass.py`; rules in `docs/methodology/contact-research.md`):
  - sites built by script
  - sites whose robots.txt disallows crawling; everything taken from them is tagged risky

  Browser agents use no web search. Each works in its own tab, reads at most five pages per site one at a time, and counts toward the four research agents at a time. BitNinja and Cloudflare challenges, CAPTCHAs, logins, 403 and 429 answers, and certificate warnings are never passed. On 24 September three safari operators on one host showed a BitNinja CAPTCHA and were recorded as blocked.

## Council and regional websites (GWF CORE API)

- **Use the API, not the pages.** `scripts/government/collect_council_sites.py` reads `/api/profiles`, `/api/statistics`, `/api/footer`, `/api/menus`, `/api/pages/slug/<slug>`, `/api/files`, `/api/news` and `/api/announcements`. Do not call endpoints that ask for a login (for example `/api/organizations/current` answers 401).
- **Defaults:** one request at a time per host, at least 1.5 seconds apart, 2 retries with backoff, and an on-disk cache. In the 2026-09 run, 13 sites answered about 40–70 requests each with no errors apart from missing pages (404).
- **Sanitise.** Responses name the website editors (`createdBy`); the collector drops them before writing.

## Census report (National Bureau of Statistics)

- **One download.** The 2022 administrative-units report, volume 1b, is 13 MB. `collect_census_wards.py` downloads it once, caches it under `runtime/`, and never commits it.

## Wikipedia API

- **Rate-limited at one request per second.** It answered HTTP 429 with `Retry-After` at that pace on 23 September 2026. Use one request every 2 seconds, batch titles (50 for coordinates, 20 for intros), and cache responses.

## NGOs Information System (nis.jamii.go.tz)

- **The map.** `/mapping` embeds all registered NGOs: 8,376 on 22 September 2026, in a 2.4 MB page. Fetch it once and cache it.
- **Profiles.** `/ngo_profile/<id>` takes about 2.2 seconds per request.
  - A sequential run with 0.6-second pauses averaged about 17 seconds per profile, because of slowdowns on the server.
  - Four concurrent workers with 0.3-second spacing fetched 855 profiles in about 30 minutes with no errors.
- **Defaults:** at most 4 workers, at least 0.3 seconds between requests to the host, and 3 retries with exponential backoff.
- **Reuse.** The collector resumes where it stopped and reuses cached profiles. Refetch (`--refresh`) only when the cache is older than about 90 days, or when the user asks.

## OpenStreetMap Overpass API

- **Broad queries time out.** A single name-regex query over the whole catchment returned HTTP 504. Split into a tag query and a narrow name query; each then ran in 8–11 seconds.
- **Back-to-back queries are refused.** In the government run, a district-boundary query sent 5 seconds after a place query got HTTP 429, then 504; the kumi.systems mirror completed it. Keep the backoff and the mirror fallback.
- **Ask for coordinates.** `out tags` returns no coordinates; use `out body` for nodes and `out center` for ways.
- **Defaults:**
  - one query at a time, at least 5 seconds apart
  - `[timeout:120]` to `[timeout:180]`
  - retries with backoff, honouring `Retry-After`
  - a User-Agent header
  - fallback mirrors: `overpass.kumi.systems`, `overpass.private.coffee`
- **Fair use.** Stay far below the public instances' limits (about 10,000 queries a day), and never run queries in parallel.

## Nominatim geocoding

- **Usage policy:** at most one request per second, a User-Agent, and cached results.
- **Prefer the offline gazetteer.** The welfare run needed no Nominatim calls, because the repository's offline gazetteers (`data/reference/lead-gazetteer.txt` and the `GAZ` table in `scripts/collection/collect_partner_leads.js`) covered the catchment.

## Browser pane

- **Slow sites time out.** Navigation to slow government sites can stop at 300 seconds.
- **One agent only.** The pane is shared, so research subagents do not use it; only the coordinator does, and only with the user's go-ahead for that site.

## Time

- **Welfare run:** the research slices took 16–46 minutes each. The whole run took about 2.5 hours, including the register fetch, consolidation and verification.
- **Government run:** no web search. The collectors took about 15 minutes (the 13 council and regional sites about 8 of them); curation and review took most of the rest.
- **Planning:** set aside about 30 minutes for a full register refresh and about an hour per wave of research agents.

## When a limit is reached

1. Keep what was confirmed: agents append records as they go.
2. Mark the slice's stopping rule as unmet in its coverage log, and list the localities, sources and queries not reached.
3. Report the gap to the user with the fix (budget, new session or manual source).
4. The next run starts from those coverage logs; `research-slices.json` carries them as `next_run_priorities`.
