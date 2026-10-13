# Coverage log: VICOBA introducers and council-news re-scan, 13 October 2026

Slice: `introducers` (VICOBA task T1, phase 2; `docs/plans/vicoba-sourcing-plan.md` section 3.3 and decision 6; `docs/plans/vicoba-integration-plan.md`).
Budget: at most 10 WebSearch calls, only to confirm each introducer's current programme and published route; no search to find groups (the user's decision of 13 October 2026). Used: **10 searches**. Page reads are listed with outcomes in `research_introducers_2026-10-13.jsonl` (same folder).

Before searching, `ledger.py tried --name` and `--org` were checked for every introducer. Only the Aga Khan Foundation had been searched before (RL010708, name-town, 13 October 2026); this slice's AKF search used another pattern (programme name). Yemco Vicoba and Magnet Vikoba were not searched again (RL010703 found no web presence).

## Searches

| Q | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/10 | "Pamoja Arusha" Aga Khan Foundation community development programme savings groups | Aga Khan Foundation Tanzania | No page names a current Pamoja Arusha programme; AKDN Tanzania economic-development page found (savings groups nationally, Southern Tanzania named); partial |
| Q2/10 | Trias Tanzania Arusha office contact savings groups | Trias Tanzania | Only an aggregator page with a postal box (not used); own site trias.ngo disallows crawling; nothing |
| Q3/10 | "KAMAMA Integrated Development Initiatives" Usa River | KAMAMA Integrated Development Initiatives | Only a 2007 thesis on a CBO of a similar name in Arumeru; no route; nothing |
| Q4/10 | "Tusonge" Community Development Organization Moshi VICOBA savings groups | Tusonge Community Development Organization | TAPO directory profile with postal address, email and phone; UN Women story (13 May 2026) on its enhanced VICOBA model; found |
| Q5/10 | "PIWOYOT" Pioneer for Women and Youth Transformation Arusha | The Pioneer for Women and Youth Transformation (PIWOYOT) | No web presence; nothing |
| Q6/10 | "Business and Entrepreneurship Support Tanzania" BEST Arusha microfinance | Business and Entrepreneurship Support Tanzania (BEST) | No web presence; nothing |
| Q7/10 | "Hope Tanzania" Arusha savings group ministry | Hope Tanzania | Only job notices on an aggregator (HOPE International's Tanzania programme works through church partners); no route; partial |
| Q8/10 | Akiba Commercial Bank VICOBA Pamoja account kikundi | Akiba Commercial Bank | Akiba VICOBA Pamoja Account page; CRDB group-account and Al-Barakah Nia Moja (VICOBA) pages; found |
| Q9/10 | VisionFund Tanzania group loans savings groups VICOBA product | VisionFund Tz MF Bank (HQ) | No product page in the results; the VFT products page (fetched next) lists a Savings Group Loan (VICOBA/VSLA); partial |
| Q10/10 | Moshi Co-operative University VICOBA community groups training We Effect 2025 | Moshi Co-operative University (MoCU) | We Effect-funded training for co-operative and social-institution leaders (May and August 2025); no VICOBA programme; partial |

## Page reads (no search budget)

Read with `scripts/contacts/read_page.py` (robots.txt honoured, 1.5 s per site, cached). Pages already in the contact crawler's cache were read offline from it.

- Fetched: the AKDN Tanzania economic-development page; the TAPO profile of Tusonge; the UN Women VICOBA story; Akiba's VICOBA Pamoja page; CRDB's group-account (Kiswahili) and Al-Barakah Nia Moja (VICOBA) pages; VisionFund Tanzania's home and products pages; the VisionFund International Tanzania story; the MoCU training page; NMB's home page.
- Read offline from the crawl cache: FRI-SUCODE's site (nambala-help.org, category page with the July 2023 post naming its three micro-finance groups); MWACI's home and about pages (its Vicoba Program and the NARETOI Women's Group).
- Blocked or missing: trias.ngo/en/tanzania (robots.txt disallows: not read; left for the orchestrator's browser, tagged risky); nmbbank.co.tz product page for the Kikundi account (DNS failure, then HTTP 403; not retried); hopeinternational.org/where-we-work/tanzania (404); visionfund.org/sq/node/1416 (404).

## Deterministic, offline

- **Council-news re-scan** (`python scripts/collection/build_vicoba_intake.py --rescan-council-news`), over the 26 council-site captures in `data/raw/government-research/council_sites/` with the collector's cached news text (main checkout `runtime/government/arusha-government-2026-09/http-cache*`, read only): 1,120 news items and announcements; 10 group mentions; **1 admitted** (Nesongoyo, a women's group in Kimokouwa ward, Longido District, which the item describes as saving and lending through a Kikoba; outside the catchment); **0 in a catchment council**. The other 9 mentions are council 10% loan groups or other groups not identified as savings-and-loan groups; their names are not kept. 4 aggregates, all in Longido (15, 10, 40 and 25 groups reported). Output: `data/raw/vicoba/captures/council_news_2026-10-13.jsonl`.
- **NGO register** (`data/raw/welfare-research/nis_catchment_profiles_2026-09-22.jsonl`): the savings, VICOBA and microfinance projects of the nine in-catchment intermediaries, re-read offline.
- **Gap census**: under the corrected rule, none of the 3,314 OpenStreetMap features in the 2026-10-11 extracts is VICOBA-named (and none is a SACCOS excluded by name), so the census outputs do not change.

## Not reached

- AKF's Arusha programme: current status and an Arusha route (only a 2023 job notice, seen as a snippet).
- Trias Tanzania's own page (robots.txt disallows: needs the orchestrator's browser read).
- Routes for KAMAMA, PIWOYOT, BEST and Hope Tanzania (none published that a search or the register shows).
- Yemco Vicoba and Magnet Vikoba: the Google Maps listings' category, phone and pin (the orchestrator's browser).
