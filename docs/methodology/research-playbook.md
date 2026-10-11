# Research playbook

What Silverleaf's lead research has tried so far, and how well each strategy worked. Read this before planning a wave; the planners (`scripts/contacts/plan_contact_research.py`, `scripts/welfare/plan_research.py`, `scripts/messaging/plan_hook_research.py`) already put each organisation's own history into the agents' prompts.

Every figure here comes from the research ledger, `data/raw/research-ledger/research_ledger.jsonl`, as backfilled on 11 October 2026. Re-run the numbers with:

```powershell
python scripts/research/ledger.py stats --by tool --by family --by segment
python scripts/research/ledger.py stats --tool websearch --by family --by target
python scripts/research/ledger.py tried --org <organisation_id>
python scripts/research/ledger.py tried --pattern at-domain
```

Statements marked **Hypothesis** are not proven by the ledger; test them in a small slice before spending a wave on them.

## How to read the numbers

- **One line per attempt.** A search, a page read (WebFetch), a site crawl, a browser read, a Google Maps lookup or a collector run. A line's `query_pattern` is a template (`"<org>" "@<domain>"`, `site:<domain> "<person>"`, `fetch:own-site/team`, `gmaps:"<org> <town>"`), and its family groups patterns that ask the same thing (`at-domain`, `site-person`, `vacancy`, `name-town` ...). `ledger.py` derives both.
- **Outcomes** are hit, partial, nothing, blocked, refused-cap, skipped or unknown. For the backfill they were read from each coverage log's outcome text by keyword rules, so they are approximate: 231 lines whose text was ambiguous are `unknown`, and a log that said "found the site, no route" may read as partial.
- **Yield** is (hit + partial) / attempts judged, and the **hit rate** is hit / attempts judged; refused, skipped and unknown attempts are left out.
- **Three biases to keep in mind:**
  - Page reads (`webfetch`) look 99% successful only because research files cite the pages that gave a fact; pages that gave nothing were rarely recorded. Use their counts to see what was read, not as a yield.
  - 326 searches (211 lines) were counted in research files (`searches_used`) but never logged query by query. They appear as the pattern `<unlogged>` and count as the baseline `"<org>" <town>` search the brief makes normal.
  - The crawl file of 10 October 2026 re-extracted the 23 September cache: 787 of the 802 sites it shares with that file have identical page hashes. Only the 67 sites it actually read again are in the ledger.

## The ledger at a glance

10,690 lines from 224 research files (11,283 parsed; 593 duplicates collapsed). 1,002 organisations were searched at least once.

| Tool | Lines | Hit | Partial | Nothing | Blocked | Refused | Unknown |
|---|---|---|---|---|---|---|---|
| WebFetch (pages cited in research files) | 6,230 | 6,136 | 0 | 46 | 47 | 0 | 1 |
| WebSearch | 1,845 (1,960 searches) | 404 | 467 | 804 | 40 | 17 | 228 |
| Crawler (one line per site per crawl) | 1,609 | 1,282 | 0 | 234 | 93 | 0 | 0 |
| Google Maps (coordinator's lookups) | 497 | 333 | 36 | 128 | 0 | 0 | 0 |
| Browser (own-site pages) | 262 | 87 | 118 | 17 | 40 | 0 | 0 |
| Other (geocode collector, census, Wikipedia) | 119 | 81 | 1 | 35 | 0 | 0 | 2 |
| Overpass | 78 | 78 | 0 | 0 | 0 | 0 | 0 |
| Council API (one line per host per capture) | 26 | 26 | 0 | 0 | 0 | 0 | 0 |
| Nominatim | 22 | 22 | 0 | 0 | 0 | 0 | 0 |
| NGO register | 2 | 2 | 0 | 0 | 0 | 0 | 0 |

## What has paid

### Web search, by pattern family

| Family | Example pattern | Searches | Hit | Partial | Nothing | Hit rate | Yield |
|---|---|---|---|---|---|---|---|
| name-town | `"<org>" <town>` | 946 | 170 | 157 | 439 | 0.21 | 0.41 |
| leader-role | `"<org>" <town> managing director` | 227 | 46 | 57 | 102 | 0.22 | 0.50 |
| discovery | `orphanage <town>`, `kituo watoto yatima <town>` | 180 | 55 | 12 | 65 | 0.41 | 0.50 |
| vacancy | `"<org>" vacancy "send your application"` | 79 | 16 | 4 | 55 | 0.21 | 0.27 |
| contact | `"<org>" <town> contact` | 69 | 18 | 13 | 27 | 0.29 | 0.49 |
| directory | `<org> safaribookings`, `site:tatotz.org ...` | 59 | 27 | 12 | 13 | 0.52 | 0.75 |
| at-domain | `"<org>" "@<domain>"` | 44 | 8 | 6 | 29 | 0.19 | 0.33 |
| site-keywords | `site:<domain> "managing director" OR founder` | 11 | 3 | 0 | 4 | 0.43 | 0.43 |
| site-person | `site:<domain> "<person>"` | 11 | 0 | 0 | 9 | 0.00 | 0.00 |
| report-pdf | `"<org>" annual report filetype:pdf` | 4 | 4 | 0 | 0 | 1.00 | 1.00 |

### Findings

1. **The organisation's own website, crawled deep, is the best source of people and addresses.**
   - The deep crawl of 11 October 2026 (`crawl_org_websites.py --deep`, up to 15 pages) found emails on 507 of 627 sites (81%), phones on 460 and named people on 217 (35%).
   - The shallow crawl (6 pages) found emails on 638 of 883 site crawls (72%) and people on 290 (33%).
   - Run it before any search: it costs no search budget.
2. **A name search is the workhorse, but a repeated one rarely pays.**
   - The first `"<org>" <town>` search for an organisation hit in 24% of the attempts judged (178 hits in 819 searches); a repeat of the same family for the same organisation hit in 11% (32 hits in 321).
   - 202 of the 817 organisations searched by name were searched by name in two or more runs. The planners now skip that.
3. **Vacancy notices give HR role inboxes for banks and larger employers, not for small safari operators.**
   - Banks and finance: vacancy searches hit 3 of 7, and `"<org>" "@<domain>"` 3 of 6 (2 more partial). The high-direct wave of 11 October found seven HR or GM role inboxes in the employer's own notices (VisionFund, MS TCDC, Aga Khan Health Services, Equity, Exim, Akiba, Elewana Arusha Coffee Lodge).
   - Safari or tour operators: vacancy searches hit 1 of 18.
4. **Address and person queries on a small operator's domain do not pay.**
   - `"<org>" "@<domain>"` for safari or tour operators: 0 hits in 8 (1 partial); for hotels and lodges 0 in 3. Results are SafariBookings and booking listings.
   - `site:<domain> "<person>"`: 0 hits in 11. The coverage logs report that the engine largely ignores `site:`.
5. **Directories pay for decision-makers.** Directory searches gave 27 hits in 59 (52% of those judged), most of them a named decision-maker (21 hits in 41 decision-maker searches). The TATO member pages are the most-read directory (1,573 page reads, from wave 11); SafariBookings (56), Idealist (39) and the ATE member directory (33) follow.
6. **Google Maps gives pins, addresses and phones, never people.**
   - 497 lookups, 333 accepted (67%). Of the accepted: a pin 329, a street address 260, a phone 187 (56%), a website 91 (27%). No listing names a person.
   - Acceptance is highest for safari operators (58 of 68) and hotels (59 of 81), lowest for NGOs (20 of 52) and ward offices (2 of 8). The 14 unplaced government offices gave 1 accepted listing.
7. **Welfare homes and programmes without a website are rarely found by search.**
   - Family-based programmes: name searches hit 6 of 156. Specialised centres: 6 of 60.
   - The route slices S and T (3 October 2026) ran 69 searches with no hit.
   - Use the call sheet (`build_call_sheet.py --run-id`), the register and funders' own pages instead.
8. **Discovery searches find new institutions, until the cap runs out.** The first welfare run (22 September 2026, all discovery) hit in 56% of its judged searches (69 hits in 213), but the shared 200-search cap ran out mid-run: 13 of its searches were refused and slice G got none (17 refusals in the whole ledger). Budget every wave (`plan_research.py`).

### Other channels

- **Browser pass:** 262 page reads for 91 organisations. Robots-disallowed sites gave partial records (tagged risky); 18 reads met a bot check (BitNinja, Cloudflare) and stopped there; other "blocked" lines are dead, lapsed or parked domains.
- **Report and PDF searches:** 4 tried, 4 hits (two for a named decision-maker, two for a direct email). **Hypothesis:** annual reports and company profiles pay for P1 employers and banks; the sample is far too small to say more.
- **Queries joining several names with OR:** 63 searches, hit rate 0.19. The brief already says they give unreliable results.

## Patterns that have stopped paying (skip them)

- A second `"<org>" <town>` search for an organisation already searched by name (11% hit rate on repeats). Fetch the pages the first search found instead.
- `site:<domain> "<person>"`, for any segment (0 of 11).
- `"<org>" "@<domain>"` for safari or tour operators and small hotels (0 of 11).
- Vacancy searches for safari or tour operators (1 of 18).
- Name searches for welfare family-based programmes and small homes with no website (6 of 156): plan a call instead.
- NGO register profiles (`nis.jamii.go.tz/ngo_profile/<id>`) for contact data: they publish no email, phone or address (welfare coverage log A, 23 September 2026).
- Re-reading pages a crawl or an earlier wave already read: the ledger lists them (`tried --org`), and `read_page.py` serves the cache.

## Never or rarely tried (may pay)

- **Places API:** never used (0 lines). **Hypothesis:** it could return phone, website and opening status for the map-only and unplaced leads in bulk, replacing manual Maps lookups. It needs a key and the user's decision.
- **Annual reports and company profiles** (`"<org>" annual report filetype:pdf`): 4 tries, all hits. Worth a small slice of P1 employers and banks.
- **`site:<domain> contact OR team OR email`:** 11 tries, 3 hits and 4 unknown. Cheap; a candidate for organisations whose site the crawler could not read.
- **Public lists allowed since 2 October 2026 but barely used:** trade-fair exhibitor lists (Kilifair 11 lines, other exhibitor pages 12), chamber directories (TCCIA 2 lines), licensed-operator lists (the Tanzania Tourist Board and TALA lists: 0 lines), BRELA (0).
- **Phone calls:** the call sheet and `import_call_results.py` exist, but the ledger holds no call results yet. For welfare programmes without websites, calls are the remaining route.
- **Checking an inferred address with one exact-address search:** 3 tries, none confirmed; too few to judge.

## Blocked or off-limits sources

- **Off-limits by rule** (`docs/methodology/contact-research.md`): LinkedIn and other social profiles, data brokers (ZoomInfo, SignalHire, RocketReach, Apollo, Lusha), review sites, and anything behind a login, paywall or bot check. Search results surfaced brokers in 47 outcomes and LinkedIn in 36; none was used (0 broker page reads in the ledger). A person's name is never searched across other sites.
- **Bot checks:** 18 browser reads stopped at BitNinja or Cloudflare challenges; they are never passed.
- **Crawler blocks:** HTTP 403 on 58 home pages and 429 on 19; 80 sites failed DNS or the connection; 90 sites' robots.txt could not be read (crawled and flagged); 15 disallow crawling (read with the browser, tagged risky).
- **Hosts that blocked page reads most often:** achpr.au.int (8), facebook.com (6, login wall), atta.travel (3), tatotz.org (3). Facebook pages are recorded as URLs, never read.
- **Rate-limited registers:** ProPublica full-text search answered HTTP 429 on about 40% of calls in the first welfare run, and its search is disallowed by robots.txt; use filing pages reached from known EINs. The UK Charity Commission register answered 403 on 22 September 2026.
- **The search cap** (200 per session, shared by all agents) refused 17 logged searches. Never work around it.

## How the ledger grows

- **Agents** log every search in their coverage log (`| Q | Query | Organisation | Outcome |`, one row per search) and every page in their JSONL `sources`; they may also append to a pending file with `ledger.py append --file runtime/research-ledger/pending/<slice>.jsonl`. They never write the ledger itself.
- **The coordinator** ingests each finished slice before the merge: `python scripts/research/ledger.py ingest <coverage log> <research JSONL> [<pending file>]`.
- **The coordinator's own work** goes in the same way:
  - Google Maps rounds: `ledger.py ingest data/raw/gap-census/google_maps_enrich_<date><round>.jsonl`, or one line at a time with `ledger.py append --tool gmaps --org <id> --query "<what was typed>" --outcome hit|partial|nothing --found "listing; pin; phone listed"`.
  - Browser passes: `ledger.py ingest data/raw/contact-research/browser_<slice>_<date>.jsonl`.
  - Crawls: `ledger.py ingest data/raw/contact-research/website_contacts_<date>.jsonl`.
- `ledger.py check` validates the file; `backfill` can be re-run at any time and adds nothing already present.

## Backfill coverage (11 October 2026)

- **Files examined:** 252. Of these, 224 gave ledger lines, 8 gave none (no searches logged: `G_funders_registers` ran after the cap was spent, `hooks_b` and two other hook logs used no searches, `wave8_funder_pages` lists pages only, `W_contact_profiles` is an export, `research_H_parent_enquiries` holds enquiries only and `research_GC_welfare` cites snippets only), and 20 were skipped as derived or duplicate records:
  - `browser_googlemaps_*.jsonl` (4), `geocodes_corrections_*` and `geocodes_gmaps_newleads_*`: derived from the Google Maps lookup files, which are ingested themselves (`osm_matches_*` and `geocodes_gap_census_*`, derived the same way, are not read at all);
  - `research_W_contact_profiles_*` (2): exports of the contact profiles;
  - `website_direct_2026-10-11.jsonl`: offline extraction from cached pages, no network;
  - the 11 browser pass coverage logs: their `browser_*.jsonl` records the same pages.
- **Lines by date and tool:**

  | Date | WebFetch | WebSearch | Crawler | Google Maps | Browser | Other | Overpass | Council API | Nominatim | NGO register | All |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | 2026-09-22 | 1,102 | 213 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 2 | 1,319 |
  | 2026-09-23 | 999 | 762 | 786 | 0 | 0 | 3 | 5 | 13 | 0 | 0 | 2,568 |
  | 2026-09-24 | 232 | 0 | 3 | 0 | 115 | 0 | 0 | 0 | 0 | 0 | 350 |
  | 2026-09-25 | 129 | 13 | 45 | 0 | 12 | 0 | 0 | 0 | 0 | 0 | 199 |
  | 2026-09-26 | 524 | 3 | 34 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 569 |
  | 2026-10-02 | 2,525 | 402 | 10 | 0 | 26 | 0 | 0 | 0 | 0 | 0 | 2,963 |
  | 2026-10-03 | 298 | 90 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 390 |
  | 2026-10-10 | 131 | 112 | 73 | 0 | 0 | 0 | 1 | 13 | 0 | 0 | 330 |
  | 2026-10-11 | 290 | 250 | 656 | 497 | 101 | 116 | 70 | 0 | 22 | 0 | 2,002 |

- **Organisations:** 10,164 lines carry organisation IDs (current IDs from the contact profiles, stale IDs resolved by name), 159 carry a name only (organisations not in the three lists, such as funders named in relationship records), and 367 concern no organisation (discovery searches and collector runs).
- **Not backfilled:**
  - `data/raw/lead-research/` (the first company-list collection: TATO and OpenStreetMap pulls and contact batches): no dates or queries were recorded.
  - Searches a log counted but did not list (the `<unlogged>` lines record their number only).
  - The query text of wave 10's logs, which list organisations and outcomes but not the queries (recorded as `<unlogged>` with their outcome).
  - Government council-site captures and census, Wikipedia and Overpass collections are recorded as one line per run or host, not per request.
