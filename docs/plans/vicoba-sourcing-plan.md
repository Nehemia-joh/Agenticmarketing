# VICOBA sourcing plan

Phase 1 (plan only), 13 October 2026. This plan covers sources, yield, record shape and privacy for a new subsegment of the employer list: VICOBAs (village community banks, *vikoba*) and related community savings groups (VSLAs, community microfinance groups or CMGs, *vikundi vya kuweka na kukopa*) inside the catchment of the five campuses. A sibling plan covers the schema, segment, pipeline and drafts. No database was touched.

Evidence files:

- Coverage log: `data/raw/vicoba-research/coverage/vicoba_sourcing_2026-10-13_coverage.md`
- Page reads (ledger format): `data/raw/vicoba-research/research_vicoba_sourcing_2026-10-13.jsonl`
- OpenStreetMap extract: `data/raw/vicoba-research/osm_savings_names_2026-10-13.json`

All three were ingested into the research ledger as RL010691 to RL010722. The orchestrator's Google Maps pilot is logged separately in its pending file.

## 0. Orchestrator review (13 October 2026)

- **Confirmed in the browser.** The orchestrator read the IPP Media article of 9 July 2026 (ledger RL010730). It reports BoT registry figures: 74,534 Tier IV groups nationally, and 16,222 Tier IV groups in Arusha region out of 16,509 providers there.
- **Kilimanjaro is far lower than §5 assumed.** The article says Kilimanjaro has fewer than 1,200 registered providers of all tiers, which is under 0.64 per 1,000 residents. That is below even the national rate this plan used as its low end.
  - Boma Ng'ombe's estimate drops from 900–4,100 to **at most about 700**: under about 350 groups for the 549,000 Kilimanjaro residents, plus about 340 for the 50,000 residents on the Arusha side.
  - The five-campus total becomes **about 10,000 registered groups**, almost all of them around the three Arusha campuses and Usa River.
- **Reconciled with the integration plan.** That plan keeps VICOBAs in the master unless the records arrive mainly as council registers holding personal data or number well over 1,000 groups (its decision 1). The evidence here meets both conditions. The decisions put to the user are therefore:
  - where group records live: a separate run reported as the employer segment's VICOBA subsegment, or the master;
  - adding intermediaries to the master as introducers.

## 1. Summary

1. **A register exists, but it is not public.** The September 2026 method (`partner-lead-generation.md` §5) said no VICOBA register exists. That is no longer right.
   - Under the Microfinance Act 2018, every community microfinance group is a Tier 4 provider and must register.
   - The Bank of Tanzania (BoT) built the registration system and delegated registration and supervision to councils.
   - Five councils in and around the catchment list this duty on their own community-development pages: Arusha City, Arusha DC, Monduli, Moshi DC and Moshi MC. They describe it as regulating and supervising Tier 4 microfinance providers under BoT directives.
   - So each council's Community Development division holds a Tier 4 register for its area. It can be asked for; it cannot be downloaded.
2. **No public source lists groups by name at any scale.** Across all the sources tested, the public web gave 6 group names in the catchment, none of them a VICOBA. OpenStreetMap and Google Maps gave no groups. No council publishes a 10% loan beneficiary list.
3. **The inventory is large.** Press reports of BoT registry figures put Arusha region at **16,222 registered Tier IV groups** (July 2026). Scaled by population, that is about **10,000 to 13,600 registered groups** within 25 km of a campus. Section 5 gives the split by campus.
4. **Recommendation.** Build the subsegment in three layers, in this order:
   1. Intermediaries: NGOs, development programmes, a microfinance bank and the banks' group products. These are researchable now.
   2. The council registers, requested at group level through the government run's council introduction.
   3. Groups that intermediaries and ward officers introduce.

   Spend no more web search on finding groups. The public web does not hold them.

**Is there a real data-protection gap today?** No. The repository holds no VICOBA member, chair or treasurer data:

- The 117 "Savings group" records in the master are registered SACCOS with organisation-level routes.
- The full text of council news, which names some group chairs and loan recipients, sits only in the uncommitted collector cache under `runtime/`.

The risk would start in phase 2 if a collector copied people's names from that text, or loaded a council list with members on it. Section 7 sets the rules that prevent this.

## 2. How the catchment is tested

Other leads are tested the same way everywhere (`scripts/collection/build_gap_census.py`, `scripts/master/recompute_campus_distances.py`):

- Take the straight-line distance to the nearest campus point in the master's `campuses` table.
- A lead is inside the catchment at 25 km or less.
- Stamp it with the transport band: 0–5, 6–10, 11–15, 16–20 or 21–25 km.

`data/reference/maps/arusha-catchment-basemap.geojson` is the lead map's basemap, not a catchment polygon.

VICOBAs have no published points. A group is placed at its **ward**, using the government run's ward point (`data/runs/arusha-government-2026-09/intake.csv`, 124 wards within 25 km). It carries `geocode_precision: ward`, and its campus and band come from that point. Ward points are estimated: from Wikipedia, with OpenStreetMap where available. A group near a band edge can therefore shift one band.

## 3. Evidence per source

**Columns.** "Tried" is what was done, with the search (Q) or page-read (F) numbers from the coverage log. "Sample" is what was examined. "Yield" is groups named by the source. "In catchment" is the subset within 25 km.

### 3.1 Deterministic sources (no search budget)

| Source | Tried | Sample | Yield (groups) | In catchment | Verdict |
|---|---|---|---|---|---|
| Council website captures, 13 hosts (`council_sites/*_2026-10-10.json` and the collector's cached news text) | Scanned pages, files, 1,019 news items and 101 announcements for VICOBA, *vikundi*, 10% loans and Tier 4 | 13 councils and regions | about 11 group names in all, mostly 10% loan groups; none is a register entry | 6: Moisha Vijana Group (Ilboru), Vijana Uchumi Youth Group (Meru), Mclives (Arusha), Kihuba and Mtaaluma (Hai), Malezikambo Kilimamoto (parenting group, Arusha DC). None is labelled VICOBA. | Useful for **aggregate counts and CDO roles**; not an inventory source. VICOBA news is all from Longido, outside the catchment. |
| Council 10% loan notices (PDF) | Read 4 scanned notices: Hai, Moshi DC, Monduli, Longido (F9–F12). Arusha City's was read on 23 September 2026 (RL001732). | 5 | 0 | 0 | Calls for applications only. Groups need a council identification certificate, issued through the Wezesha portal. No beneficiary lists. |
| Gap census, contact profiles, `tcdc_saccos_north.txt` | Text scan | All files | 0 VICOBA or VSLA | 0 | Nothing. The master's 117 "Savings group" records are SACCOS: 67 community or open-bond, 48 employer-based, 2 mapped from OpenStreetMap. |
| OpenStreetMap, 3 Overpass name queries, one per catchment box | Names or descriptions matching vicoba, vikoba, vsla, saving, akiba, kikundi, microfinance or community bank, plus office=financial, amenity=microfinance and office=association | 12 features | 0 savings groups | 0 | Nothing. The matches are banks, financial offices, the Makiba place names and a milling group. Groups are not mapped. |
| NGO register (898 NGOs within 30 km, 2026-09-22) | Project and vision text scan | 898 | 0 groups; **10 intermediaries** with savings, VICOBA or microfinance projects | 9 within 25 km (Victoria's Giving Foundation is at 25.8 km) | Good source of **intermediaries** (§3.3). |
| Government run (`arusha-government-2026-09`) | Ward and council offices | 124 wards, 9 council divisions within 25 km | 0 | n/a | Already holds the **routes**: a Ward Community Development Officer post per ward and the Head of the Community Development Division per council. These are role-addressed, with no names. |

### 3.2 Registers and portals (Microfinance Act 2018, Tier 4)

| Source | Tried | Finding | Public? | Verdict |
|---|---|---|---|---|
| BoT CMG registration portal, cmg.bot.go.tz (2021) | Q16–Q17, F6–F7 | The 2021 BoT notice named this portal for group registration, with council community-development and ICT officers to help. The host no longer resolves. | No | Gone. The registration records now sit with the councils. |
| BoT regulated-institutions list | F5 | Lists banks, bureaux, Tier 2 microfinance providers and digital lenders. No Tier 4 groups. | Yes, Tier 2 only | Not a source for groups. |
| BoT registry counts, as reported in the press | Q3–Q4; F3–F4 blocked (HTTP 520) | 74,534 Tier IV groups nationally, 16,222 in Arusha region. No Kilimanjaro figure seen. | Counts only | Use **for sizing only**, after the orchestrator reads the article in the browser. |
| Wezesha portal, mikopohalmashauri.tamisemi.go.tz | Q1, F1 | PO-RALG's system for 10% loan groups: identification certificates and applications (Hai notice of 1 July 2026). | Login only | Do not use. Never sign in. Ask the council instead. |
| NeST, the public procurement system's register of special groups | Q12 | 27,946 special groups nationally. Arusha region registered 1,400 (council news, July 2026). Meru DC registered 204, second only to Arusha City. | No public list found | Not a source. It holds women, youth and disability groups seeking tenders, not VICOBAs. |
| Council 10% loan beneficiary lists | Q5; all council files and announcements | Published nowhere in the 13 captures. News gives counts: Moshi DC 76 groups (TZS 873m, 2025/26), Hai 49 eligible groups (September 2026), Monduli 21, Longido 26 + 29. | No | Not a source (§7 on why not to seek them). |

### 3.3 Intermediaries (possible introducers)

Every route below is an **organisation route**. None of these organisations will share member data, and they should not be asked to. The ask is an introduction or a joint session with their groups.

| Intermediary | Evidence | Campus, distance | Published route | Note |
|---|---|---|---|---|
| Aga Khan Foundation Tanzania: Pamoja Arusha Community Development Programme | Q18: 2023 job notice for the programme, run from an outreach centre on the AKU Arusha campus and building on an existing savings-group programme | Arusha (AKU campus); point to confirm | To research: own site and AKDN pages | Confirms §5's Aga Khan lead for Arusha. Strong fit. |
| VisionFund Tanzania Microfinance Bank (HQ) | Q9: World Vision runs its savings groups through VisionFund. Already in the master as "VisionFund Tz MF Bank (HQ)". | Kijenge, 2.0 km | In the master (HR or GM role inbox from the 11 October wave) | Group-lending bank; World Vision's savings-group arm. |
| Akiba Commercial Bank: VICOBA Pamoja account | Q14: opening the account needs a letter from the group's VICOBA umbrella body | Arusha City (Sakina), 2.6 km; in the master | In the master | Shows that umbrella bodies exist. Ask the branch which ones serve Arusha. |
| NMB (Pamoja account), CRDB (Niamoja group account), Cooperative Bank (Pamoja), TCB and Vodacom (M-Koba) | Q14, Q7, Q8 | Branches in the master | Branch routes in the master | Banks cannot share customer data. Their role is a co-hosted information session at a branch. |
| Trias Tanzania | NGO register: works with "credit and saving groups" | Arusha City, 2.6 km | Register entry; site to crawl | Membership-based organisations focus. |
| KAMAMA Integrated Development Initiatives | NGO register: "Community Managed Saving Groups (CMSGs)" projects | Usa River, 3.6 km | Register | — |
| Hope Tanzania | NGO register: "Savings Group Ministry" (2026) | Ilboru, 3.3 km | Register | — |
| Hope and Soul Tanzania | NGO register: women's microfinance project | Kijenge, 3.0 km | In the welfare run | — |
| Maasai Women and Children Initiative (MWACI) | Welfare classification: women's VICOBA groups, but in Monduli | Ilboru, 3.1 km (office) | Welfare register research (slice U) | Its groups are mostly outside the catchment. |
| Business and Entrepreneurship Support Tanzania (BEST) | NGO register: microfinance project 2025 | Arusha City, 5.2 km | Register | Not the "BEST" parent survey in the 2026-09 workbook note. |
| PIWOYOT | NGO register: "women empowerment through VICOBA" (2025, Monduli) | Arusha City, 6.5 km | Register | Its groups are in Monduli. |
| FRI-SUCODE | NGO register: "Follow up of Village saving Groups (VICOBA)" | Kijenge, 8.4 km | Register | — |
| Tusonge Community Development Organization | NGO register: VICOBA and microfinance linkage | Boma Ng'ombe, 21.8 km | Register | Kilimanjaro side. |
| Moshi Co-operative University (MoCU), with We Effect | Q19: community and cooperative group training | Boma Ng'ombe, 21.3 km; in the master | In the master | Kilimanjaro side. |
| Yemco Vicoba, Magnet Vikoba, Kibaba Vicoba Solution, VICOBA Sustainable, Vicobank | The orchestrator's Google Maps pilot. Q13 found no web presence. | Arusha | Maps listing only | Candidate intermediaries. Check each listing's category and phone in the browser before use. |
| SEDIT, CARE Tanzania, Heifer, ELCT dioceses, Archdiocese of Arusha or Caritas | Q6, Q7, Q10, Q15 | — | — | **Not confirmed in the catchment.** SEDIT has no web presence. CARE's VSLA work is national, with no catchment evidence. Drop them from the shortlist unless a CDO names them. |
| KINEFA | Q8: no public source | — | — | Already the offer register's member association (OF07). Ask Silverleaf what it is: it may be the umbrella body the Akiba account refers to. |

### 3.4 Google Maps and Facebook

- **Google Maps.** The orchestrator ran 7 signed-out lookups. They found 5 support providers or intermediaries and no groups.
- **Facebook.** Q11 found no indexed VICOBA page or group in the catchment. Facebook is behind a login wall and stays off-limits.

## 4. Recommended order of sources

1. **Intermediaries first** (no new search budget).
   - Add the confirmed intermediaries in §3.3 as introducer organisations.
   - Crawl their own sites with `crawl_org_websites.py`.
   - Record the bank group products as facts on the existing bank records.
2. **Council Tier 4 registers, by request.** Fold the request into the government run's council introduction (GA01) to the Community Development divisions of the catchment councils:
   - Arusha City, Arusha DC and Meru DC
   - Hai, Siha and Moshi DC
   - Moshi MC, which is at the edge of Boma Ng'ombe's 25 km

   Ask for a group-level extract: group name, Tier 4 registration number and date, ward, village or mtaa, member count, meeting place, and supporting NGO. Ask for no member names or phones.
3. **Ward Community Development Officers** (124 wards, role routes already in the government run). This route is for wards whose council does not supply an extract. It is also how Silverleaf meets groups at a ward meeting; Silverleaf does not collect their data there.
4. **Introductions from intermediaries** (step 1) and from bank branches, recorded as group records with the introducer as source.
5. **Public council news.** Run only as a deterministic, offline re-scan of each refreshed council capture. It records group name, ward and type, with **no person names**. Expect a few groups a year.
6. **Not used:** web search for group names, OpenStreetMap, Google Maps for groups, Facebook, and the BoT, Wezesha and NeST portals.

## 5. Inventory size estimate

**Basis:**

- Arusha region has 16,222 registered Tier IV groups (press report of the BoT registry, July 2026, to be confirmed in the browser). With 2,356,255 residents in the 2022 census, that is 6.88 groups per 1,000 people.
- The national rate is 1.21 per 1,000 (74,534 groups for 61.7 million people).
- There is no Kilimanjaro figure. Its wards are given a range: the national rate at the low end and Arusha's rate at the high end.
- Population is the 2022 census population of the 124 catchment wards, each assigned to its nearest campus.

| Campus | Wards ≤ 25 km | Residents (2022) | Estimated registered groups |
|---|---|---|---|
| Kijenge | 25 | 563,002 | about 3,900 |
| Arusha City (Sakina) | 22 | 380,484 | about 2,600 |
| Usa River | 19 | 261,590 | about 1,700 |
| Ilboru | 11 | 174,675 | about 1,200 |
| Boma Ng'ombe | 47 | 598,824 (549k in Kilimanjaro) | about 900 to 4,100 |
| **All five** | **124** | **1,978,575** | **about 10,300 to 13,600** |

**Caveats:**

- Registered is not the same as active. The register accumulates and closures are seldom recorded.
- The three Arusha campuses are 2 to 6 km apart, so their split is an allocation, not three separate markets.
- The figure rests on one press report.

**What to expect in practice:**

- The council extracts are the only route to group names at this scale.
- Even partial cooperation from Arusha City, Arusha DC and Meru DC would cover about 1.4 million of the 2 million residents.
- Without them, expect tens of groups, not thousands. These would come through intermediaries and ward meetings.

## 6. Record fields each source can fill

| Field | Council Tier 4 extract | Intermediary introduction | Council news (offline) | Ward CDO meeting |
|---|---|---|---|---|
| Group name | yes | yes | yes | yes |
| Group type (VICOBA, VSLA or CMG; women, youth or disability group) | yes | yes | partly | yes |
| Tier 4 registration number and date | yes | sometimes | no | sometimes |
| Council, ward, village or mtaa | yes | yes | ward usually | yes |
| Campus, distance band (from the ward point; precision `ward`) | derived | derived | derived | derived |
| Member count | yes | often | sometimes | yes |
| Meeting place and cycle (weekly or monthly; share-out month) | sometimes | often | rarely | yes |
| Supporting NGO or programme | sometimes | yes (the introducer) | sometimes | yes |
| Bank product (Pamoja, Niamoja, M-Koba) | no | sometimes | no | sometimes |
| Route | the council CD division (office) | the introducer (organisation) | the ward CDO (office) | the ward CDO (office) |
| Source: URL or locator, date, excerpt of 25 words or fewer | the letter or file received | the introducer's record | the news item ID and date | the meeting note |
| Named chair or treasurer, mobile | **never stored** | only if the group itself agrees, and recorded with consent | **never** | only with consent |

The route is always an office or an organisation. A group is contacted through the person or office that introduced it, until the group itself gives Silverleaf a contact and agrees to receive messages.

## 7. Privacy position

- **Members and leaders are private individuals.** Under `docs/methodology/contact-research.md`, a chair's or treasurer's name and mobile count only where a public body or the group itself publishes them **for that role, for contact**.
  - Council news that names a group chair while reporting a loan is journalism about the loan, not a published contact route. Such names are not recorded.
  - Nothing is inferred.
- **10% loan beneficiary lists.** No council in the catchment publishes one, and Silverleaf should not ask for one. Such a list identifies small groups (five or more members, or two for disability groups) as recipients of public credit. In many cases it also names individuals, and for disability groups it reveals a health-related status.
  - Using it to target school marketing would be a new purpose, unrelated to why the data was collected. That is a real issue under the Personal Data Protection Act 2022's purpose and lawful-basis rules, not a technicality.
  - Silverleaf's own registration with the Personal Data Protection Commission is still an open question (§10 of the method).
  - This is not legal advice; confirm with counsel before any list containing personal data is received.
- **Group-level records carry low risk.** A record holding a group's name, ward, type, registration number and an office route is organisation-level data. That is the boundary this plan sets:
  - no member, chair or treasurer data enters a committed file or a database;
  - a council extract that arrives with personal columns has them removed on import, before anything is stored, and the removal is logged;
  - consent-based contacts from a meeting go through the existing call-results route (`import_call_results.py`), with consent recorded.
- **No candidate emails.** Groups have no domain, so the email-format rule never applies to them.

## 8. Decisions for the user

1. **Scope of "VICOBA".**
   - Recommended: registered Tier 4 community groups (VICOBA, VSLA, CMG) as the subsegment. Council 10% loan groups count only where a council or intermediary supplies them as groups. They are tagged with their type, never sourced from beneficiary lists.
   - Alternative: include all special-interest groups (NeST, 10% loan groups). This is not recommended: different motive and higher privacy risk.
2. **Primary route to groups.**
   - Recommended: a group-level Tier 4 extract requested from each catchment council's Community Development division, inside the government run's GA01 introduction. The request letter is drafted with the government run's letters.
   - Alternative: ward-by-ward contact through 124 Ward CDOs. This is slower and better kept as a fallback.
3. **Intermediaries as introducers.**
   - Recommended: add the confirmed intermediaries in §3.3 to the master as introducers. The orchestrator owns the segment name, for example "Introducer: savings-group network". Their first message asks to meet their groups' committees.
   - The banks are recorded as facts on their existing records, not as new introducers.
4. **Personal data boundary.** Recommended: group-level records only; no member, chair or treasurer data stored without the group's own consent; council extracts stripped of personal columns on import; no beneficiary lists requested.
5. **PDPC registration first.** Recommended: confirm Silverleaf's registration before receiving any council extract, in case one arrives with personal data despite the request.
6. **Web-search budget.** Recommended: none for finding groups (public-web yield: 6 groups, none a VICOBA). Use 5 to 10 searches only to confirm the intermediaries' current programmes: AKF Pamoja Arusha, Trias, KAMAMA, and the Maps-listed providers.
7. **Browser tasks for the orchestrator.** Recommended:
   - read the IPP Media article of 9 July 2026, to confirm 16,222 and look for a Kilimanjaro figure;
   - check the category and phone of the five Maps-listed providers.

   Do not sign into the Wezesha or NeST portals.
8. **KINEFA.** Recommended: ask Silverleaf what KINEFA is. If it is a VICOBA umbrella body, it is the first introducer, and OF07's extension to other groups (a Finance decision) becomes the offer lever.

## 9. Files and scripts for a phase-2 collector

Checked against `scripts/README.md`. Extend existing scripts first.

| Task | File | Change |
|---|---|---|
| Intermediaries | `data/raw/contact-research/introducers_savings_<date>.jsonl` (new data) → `scripts/master/add_introducers.py` (existing) | Research the intermediaries in §3.3 in the introducer format; add them with the existing script. It may need the new introducer kind added to its allowed list. |
| Intermediaries: contacts | `scripts/contacts/crawl_org_websites.py` (existing) | No change; crawl the new introducers after they are added. |
| Council news re-scan | **new** `scripts/collection/scan_council_group_mentions.py` | Reads the council-site captures and the collector's cache offline. Writes `data/raw/vicoba-research/council_group_mentions_<date>.jsonl`: group name, type, council, ward, item ID and date, aggregate counts. It drops every person name (a stop-list of titles such as Bw., Bi., Mwenyekiti, Mhe., plus the existing `contact_lib` person filter run in reverse to remove, not keep). |
| Council register import | **new** `scripts/collection/import_council_group_register.py` | Reads a council-supplied CSV or XLSX. Keeps an allow-list of group-level columns only and logs dropped columns. Matches each ward to the government run's ward points for campus and band, at precision `ward`. Writes group-level intake rows for the sibling's pipeline (record shape in §6). |
| Ward placement | `scripts/government/gov_lib.py` (`ward_key`) | Reuse for ward-name matching; no change. |
| Research ledger | `scripts/research/ledger.py` | Add `"vicoba-research": "vicoba"` to `AREA`, and the folder to `backfill_paths`. Without it, the coverage log's searches ingest with target `route` instead of `discovery`, and a backfill would not re-read this folder. |
| Method | `docs/methodology/partner-lead-generation.md` §5 | Replace "there is no register" with the Tier 4 register held by councils, and drop SEDIT and CARE as named intermediaries pending evidence. Owned by whoever edits the method. |
| Rate limits | `skills/silverleaf-create-lead-list/references/research-rate-limits.md` | Note: ippmedia.co.tz answered HTTP 520 to page reads (13 October 2026); cmg.bot.go.tz no longer resolves. |

Not needed: a new OpenStreetMap collector (no savings groups are mapped), a portal scraper, or search agents for groups.
