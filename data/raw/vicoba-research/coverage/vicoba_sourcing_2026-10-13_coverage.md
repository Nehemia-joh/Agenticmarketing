# Coverage log: VICOBA sourcing test, 13 October 2026

Slice: `vicoba_sourcing` (phase-1 sourcing test; plan in `docs/plans/vicoba-sourcing-plan.md`).
Budget: 20 WebSearch calls, 30 page reads. Used: **19 searches**, **12 page reads** (listed with outcomes in `research_vicoba_sourcing_2026-10-13.jsonl`), **3 Overpass queries** (one per catchment box; extract in `osm_savings_names_2026-10-13.json`).
Before searching, `ledger.py tried --pattern` was checked for vicoba, vikoba, vsla, savings group, kikundi, microfinance, wezesha, mikopo, SEDIT, KINEFA and community bank: none had been tried. The only earlier related line is RL001732, a read of Arusha City Council's 10% loan notice (contact routes only).

## Searches

| Q | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/20 | "Wezesha portal" mikopohalmashauri.tamisemi.go.tz vikundi usajili | Wezesha Portal (PO-RALG) | Portal named only by a third-party blog; login-only; no public list; partial |
| Q2/20 | vikundi vya kijamii vya huduma ndogo za fedha daraja la nne usajili halmashauri mfumo Benki Kuu | Bank of Tanzania | BoT delegates Tier 4 registration and supervision to councils; no public register found; partial |
| Q3/20 | Bank of Tanzania annual report tier 4 community microfinance groups registered number by region Arusha Kilimanjaro | Bank of Tanzania | Press report (IPP Media, July 2026) of BoT registry, 16,222 Tier IV groups in Arusha region of 74,534 nationally; no Kilimanjaro figure; found |
| Q4/20 | BoT "16,222" Tier IV Arusha microfinance registry | Bank of Tanzania | Same single article; the registry itself is not public; partial |
| Q5/20 | "orodha ya vikundi" mikopo asilimia 10 Halmashauri Jiji la Arusha OR Meru OR Hai pdf | Arusha City Council | No published beneficiary list; nothing found |
| Q6/20 | SEDIT VICOBA Tanzania Arusha office contact Social Economic Development Initiatives of Tanzania | SEDIT | No web presence found; nothing found |
| Q7/20 | CARE Tanzania VSLA savings groups Arusha Meru Hai Moshi programme 2025 | CARE Tanzania | National VSLA work, NMB Pamoja product and Chomoka app; nothing in the catchment; partial |
| Q8/20 | KINEFA Arusha VICOBA network umoja wa vikoba Arusha | KINEFA | No source names KINEFA; TCB and Vodacom M-Koba digital group product noted; nothing found |
| Q9/20 | World Vision Tanzania savings groups Arumeru OR Meru OR Arusha area programme VSLA | World Vision Tanzania | Savings groups run through VisionFund Tanzania; no Arusha area-programme detail; partial |
| Q10/20 | KKKT Dayosisi ya Meru OR Kaskazini OR Kaskazini Kati vikundi vya VICOBA mradi wanawake | ELCT dioceses | No diocese VICOBA programme in the catchment found; nothing found |
| Q11/20 | VICOBA Arusha facebook kikundi Sakina OR Njiro OR Tengeru OR "Usa River" vikoba | none | No group Facebook page indexed; nothing found |
| Q12/20 | NeST PPRA special groups vikundi maalum registered list public search women youth disability groups tenderers | PPRA (NeST) | 27,946 special groups on NeST nationally; no public list; partial |
| Q13/20 | "Yemco" OR "Magnet Vikoba" OR "Kibaba Vicoba" Arusha | Yemco Vicoba; Magnet Vikoba; Kibaba Vicoba Solution | No web presence beyond the Google Maps listings; nothing found |
| Q14/20 | NMB "Pamoja" account VICOBA OR CRDB "akaunti ya kikundi" vikundi vya kuweka na kukopa | NMB Bank; CRDB Bank | NMB Pamoja, CRDB Niamoja, Akiba Commercial Bank VICOBA Pamoja (needs a letter from the group's VICOBA umbrella body), Cooperative Bank Pamoja; found |
| Q15/20 | Jimbo Kuu Katoliki Arusha OR Caritas Arusha OR Heifer Tanzania Arusha savings groups vikoba programme | Archdiocese of Arusha; Caritas; Heifer Tanzania | No programme in the catchment found; nothing found |
| Q16/20 | vikundi vya kijamii vya huduma ndogo za fedha vilivyosajiliwa Jiji la Arusha OR Meru OR Hai OR Moshi idadi | Bank of Tanzania | No council counts; led to the 2021 BoT notice naming the CMG registration portal; partial |
| Q17/20 | usajili wa vikundi vya kijamii vya huduma ndogo za fedha mfumo mpya 2026 halmashauri tovuti cheti cha usajili kikundi | Bank of Tanzania | No newer registration system published than the 2021 portal; nothing found |
| Q18/20 | Aga Khan Foundation Tanzania savings groups regions where it works Arusha | Aga Khan Foundation Tanzania | Pamoja Arusha Community Development Programme, outreach centre on the AKU Arusha campus, building on an existing savings-group programme (2023 job notice); found |
| Q19/20 | vikundi vya VICOBA Hai OR Siha OR Moshi Kilimanjaro shirika mafunzo 2026 | none | Only MoCU and We Effect community-group training noted; nothing found |

One search was left unused.

## Deterministic sources (no search budget)

- **Council website captures** (`data/raw/government-research/council_sites/*_2026-10-10.json`, with full news text from the collector's cache in the main checkout's `runtime/`): 13 hosts, about 1,000 news items and 100 announcements. Mentions of VICOBA are in Longido (outside the catchment) and in the Meru and Longido community-development pages. Council community-development pages of Arusha City, Arusha DC, Monduli, Moshi DC and Moshi MC list "regulate and supervise Tier 4 microfinance providers under BoT directives" as a division function. Loan-scheme news gives aggregate counts (Moshi DC 76 groups, Hai 49 eligible groups, Monduli 21, Longido 29), Meru DC's 204 groups registered on NeST, and Arusha region's 1,400 groups on NeST. About 11 group names appear in all, 6 of them in catchment news (10% loan or parenting groups, none labelled VICOBA). No council publishes a beneficiary list or a Tier 4 register.
- **Gap census and contact profiles** (`data/raw/gap-census/*`, `data/interim/contact-profiles/*`): no VICOBA or VSLA. The 117 "Savings group" records in the master are all SACCOS.
- **NGO register** (`data/raw/welfare-research/nis_catchment*`, 898 NGOs within 30 km): 10 NGOs publish savings-group, VICOBA or microfinance projects, 9 of them within 25 km (listed in the plan).
- **OpenStreetMap** (3 Overpass queries, 13 October 2026): no feature in the catchment is a savings group; 12 matches were banks, financial offices, the Makiba place names and one milling group.
- **Google Maps** (orchestrator, 7 signed-out lookups, logged separately): no groups; 4 support providers or intermediaries.

## Blocked or left for the orchestrator's browser

- ippmedia.co.tz article of 9 July 2026 (BoT registry figures by region): HTTP 520 twice. Read it in the browser to confirm the Arusha figure and look for Kilimanjaro's.
- cmg.bot.go.tz (BoT CMG registration portal, 2021): the host no longer resolves.
- mikopohalmashauri.tamisemi.go.tz (Wezesha portal): login-only app; not to be signed into.

## Not reached

- Group-level lists from any council (only obtainable by request to the community development divisions).
- SEDIT's current status and any Arusha presence.
- Kilimanjaro region Tier 4 count.
