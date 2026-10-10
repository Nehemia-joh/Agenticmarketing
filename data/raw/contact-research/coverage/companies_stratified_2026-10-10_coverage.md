# Company master: stratified enrichment round, 10 October 2026

Goal: raise the data points held per company (contacts, addresses and other specific facts), stratified by reach tier (`employer_reach`: P1, P2, P3) with the introducers as their own stratum. Measured with `scripts/master/measure_master_coverage.py` (new), before on the main checkout's master (SHA-256 `6998951e…`), after on the merged copy, using the baseline's strata for both.

Outputs:
- `data/raw/contact-research/search_companies_stratified_2026-10-10.jsonl` (13 organisations, agent-brief format)
- `data/raw/hook-research/hooks_companies_2026-10-10.jsonl` (59 organisations, 74 lead-brief facts, 6 verified hooks)
- `data/raw/contact-research/website_contacts_2026-10-10.jsonl` (own-website crawl, 854 sites: the HTTP cache plus the 52 sites added since 23 September)
- `data/raw/contact-research/osm_contacts_2026-10-10.json` (OpenStreetMap contact tags, 1,324 places; almost unchanged since 23 September)
- `data/reference/employer-people-exclusions.json` (35 reviewed crawl misreads, applied by `scripts/master/screen_profile_people.py`)

## Baseline (before)

| Data point | P1 (n=100) | P2 (n=150) | P3 (n=452) | Introducers (n=16) |
|---|---|---|---|---|
| Named decision-maker | 59 (59%) | 34 (23%) | 169 (37%) | 13 (81%) |
| Direct email (own or role inbox) | 11 (11%) | 6 (4%) | 19 (4%) | 2 (12%) |
| Any email | 84 (84%) | 93 (62%) | 408 (90%) | 15 (94%) |
| Phone | 88 (88%) | 106 (71%) | 418 (92%) | 14 (88%) |
| Address (postal or physical) | 85 (85%) | 97 (65%) | 398 (88%) | 14 (88%) |
| Physical address (beyond a P.O. Box) | 75 (75%) | 85 (57%) | 281 (62%) | 14 (88%) |
| Geocode address-level | 2 (2%) | 0 (0%) | 22 (5%) | 0 (0%) |
| Geocode locality-level | 34 (34%) | 30 (20%) | 222 (49%) | 0 (0%) |
| Website | 81 (81%) | 92 (61%) | 413 (91%) | 16 (100%) |
| Official social pages | 72 (72%) | 76 (51%) | 335 (74%) | 0 (0%) |
| Size evidence | 44 (44%) | 24 (16%) | 100 (22%) | 4 (25%) |
| Founded year | 31 (31%) | 19 (13%) | 86 (19%) | 0 (0%) |
| Escalation contact (of wide orgs) | 2 of 8 | 2 of 7 | 3 of 22 | 0 of 0 |
| Lead brief with source | 47 (47%) | 31 (21%) | 80 (18%) | 0 (0%) |
| Verified hook | 41 (41%) | 16 (11%) | 38 (8%) | 0 (0%) |

## After the merge

| Data point | P1 | P2 | P3 | Introducers |
|---|---|---|---|---|
| Named decision-maker | 59 (+0) | 34 (+0) | 170 (+1) | 13 (+0) |
| Direct email (own or role inbox) | 12 (+1) | 7 (+1) | 19 (+0) | 2 (+0) |
| Any email | 84 (+0) | 94 (+1) | 411 (+3) | 16 (+1) |
| Phone | 88 (+0) | 107 (+1) | 421 (+3) | 15 (+1) |
| Address (postal or physical) | 85 (+0) | 97 (+0) | 398 (+0) | 14 (+0) |
| Official social pages | 74 (+2) | 76 (+0) | 338 (+3) | 14 (+14) |
| Size evidence | 46 (+2) | 27 (+3) | 105 (+5) | 4 (+0) |
| Founded year | 44 (+13) | 32 (+13) | 87 (+1) | 8 (+8) |
| Escalation contact | 2 of 8 | 2 of 7 | 3 of 22 | 0 of 1 |
| Lead brief with source | 60 (+13) | 47 (+16) | 87 (+7) | 11 (+11) |
| Verified hook | 43 (+2) | 19 (+3) | 38 (+0) | 0 (+0) |

The address and geocode rows did not move. The merge writes a researched physical address only into the contact-profile record, never into `organisations.address` (see the report's proposed change to `merge_master_contacts.py`), and the addresses found this round belonged to organisations that already held one.

## Deterministic work (no search)

- **Own-website crawl** (`crawl_org_websites.py --date 2026-10-10`): every master and welfare site re-read from the shared HTTP cache with the current rules, plus the 52 sites never crawled (33 master: the 16 introducers' own sites and records whose website was repaired on 10 October). The new reads added socials for 14 introducers, phones and emails for 21 organisations, and about 250 named people.
- **Crawl misreads screened before the merge**: 67 crawled people left out (`data/reference/employer-people-exclusions.json`, `screen_profile_people.py`):
  - page headings read as names (AICC 'Visitor Information', EAC 'Quick Facts', TICD organisation-chart units);
  - ATE's sector chairs and vice-chairs read as 'CHAIRPERSON' without their sector, which would have looked like ATE's elected head;
  - members listed with their own employers' titles (WHAT Advisory Board; TATO board members' companies; TPSF's news teaser on Kamal Group's CEO; ATE's home-page testimonial);
  - national bodies' people read again on regional offices that share the website (ATE Northern Zone, TNCC Arusha and Kilimanjaro, CTI Arusha).
- **Own pages the crawler did not reach** (`read_page.py`): Easy Travel's Directors page (General Manager Musaddiq Gulamhussein, Director Sayyedah), Tropical Trails' community page (the Arusha Children's Trust it founded in 1999), Bushtops' careers page, the ATE Management Board page, ATC's about page.
- **Lead briefs from cached own pages**: founding years, staff numbers and community or staff-welfare facts for 59 organisations, every excerpt checked verbatim against the cached page. Notable:
  - Sunflag employs over 2,700 people in Arusha;
  - NBC Bank about 1,200 staff; VisionFund Tanzania more than 500 staff in 46 branches; Altezza Travel 300+ office and hotel staff;
  - Tanzania-Experience 80 permanent employees; Okota 80+ staff;
  - Onsea House says its staff receive child education among their benefits;
  - Karibu Camps is funding a chemotherapy centre at Mount Meru Hospital; House of Gems runs 15 branches and charity sponsorships;
  - founding years for TICD (1963), ATE (1960), TATO (1983), TNCC (1988), TPSF (1998), CSSC (1992), EABC (1997), HAT (2004), TFA (1935), Exim (1997), Moivaro (1999) and others.
- **Association of Tanzania Employers members directory** (`membership.ate.or.tz/members`, GET pages only; its filter is a form and was not submitted): 116 entries listed, 6 matched master names. Used: TFA's head-office address, P.O. Box and phone. Ecobank's entry gives its Dar head office; Shree Hindu Mandal is a Dar hospital, not Arusha's Shree Hindu Union; neither was used.
- **Embassy and High Commission lists of medical facilities** (found through Q11 and Q12; official lists naming facility contacts):
  - German Embassy Dar es Salaam, April 2023: the Aga Khan Health Centre Arusha's director and her work email, P.O. Box 2546, and ALMC's office phone. The director it names for ALMC has only a personal email, so he is not recorded.
  - British High Commission, May 2021: Mount Meru RRH's P.O. Box and office phone. Its ALMC street address and P.O. Box differ from the German list's, so neither is recorded (the conflict is described in the record's notes).

## Searches (19 of 75 used)

| # | Stratum | Query | Outcome |
|---|---|---|---|
| Q1/75 | P2 | "Sunflag" Tanzania Arusha "managing director" OR "general manager" textile | Names only in a 2006 cable and an undated news story (news is not a source for people). Sunflag's own vacancy notice (Ajiriwa, closing 15 Jan 2019, fetched) gives the HR Manager's P.O. Box 3123 and the Njiro facility. Recorded the address only; the notice's named inboxes are not attributed to anyone. |
| Q2/75 | P1 | "Mganga Mfawidhi" "Kituo cha Afya Levolosi" OR "Kaloleni" Arusha | No in-charge named. maoni.moh.go.tz timed out. Nothing recorded. |
| Q3/75 | P1 | site:health4allclinics.co.tz doctor OR director OR founder | The engine ignored site:; only other organisations. The domain does not resolve. Nothing. |
| Q4/75 | P1 | "AAR Healthcare Tanzania" "Managing Director" OR "Country Manager" OR "Chief Executive" | The Citizen (7 Apr 2021, fetched): AAR Healthcare Tanzania began a creditors' voluntary winding-up and planned to close its eight clinics. Recorded as a possible closure for AAR Clinic (its drafts are held for review). |
| Q5/75 | P1 | "Shree Hindu Union" hospital Arusha "medical director" OR administrator | Its Oct 2021 notices address the Medical Director, P.O. Box 3051, and give job.application@ (already held). No name. Nothing new. |
| Q6/75 | P1 | "Karibu Camps" Tanzania owner OR founder OR "managing director" | No owner named. The results led to the ATE members directory (used above). |
| Q7/75 | P1 | "Kibo Palace Hotel" Arusha owner OR "managing director" OR proprietor | Only travel listings. Nothing. |
| Q8/75 | P1 | "Delight Polyclinic" Arusha founder OR "medical director" … | Nothing on Delight. Aga Khan's own page gives the Arusha polyclinic's street address and phone; recorded for Aga Khan Health Services - Arusha (P2). The P1 map point 'The Aga Khan University Hospital' is flagged as a possible duplicate. |
| Q9/75 | P1 | "@eximbank.co.tz" OR "@diamondtrust.co.tz" OR "@azaniabank.co.tz" human resources email vacancy | DTB's own notice (closing 20 Jan 2020): HR@diamondtrust.co.tz, the inbox for the HR head's role; recorded, with a reviewed recipient override routing Pamela Kieti's draft there. Azania's notice (2019): hra@azaniabank.co.tz, recorded as an organisation route (no HR head named). Exim's notice used another domain; not used. |
| Q10/75 | P1 | "@nmbbank.co.tz" OR "@tcbbank.co.tz" OR "@kcbgroup.com" Tanzania "human resources" … | Portals only, no inboxes. Nothing. |
| Q11/75 | P1 | "@almc.or.tz" OR "@selianlh.or.tz" OR "@mtmerurrh.go.tz" email | No inboxes; the results led to the German Embassy list of medical facilities (used above). |
| Q12/75 | P1 | U.S. Embassy Tanzania list of medical facilities Arusha … | No US list. Led to the British High Commission list on gov.uk (used above). |
| Q13/75 | P1 | "NSK Hospital" OR "NSK Hospitals" Arusha "managing director" OR director … | Only a partner page naming visitors by first name. Nothing. |
| Q14/75 | P2 | "Gold Crest Hotel" Arusha "general manager" OR owner … | No manager named. The hotel's own notice (deadline 31 Aug 2024) gives hr.arusha@goldcresthotel.com; recorded as a role route. |
| Q15/75 | P3 | "Altezza Travel" founder OR CEO OR "managing director" … | Names only on data-broker and CB Insights pages (not sources). Its press release on businesswire answers 403. Nothing. |
| Q16/75 | Introducers | "@ate.or.tz" "Chief Executive Officer" OR "CEO" … | Only info@ (held). Nothing. |
| Q17/75 | P2 | "Nkoaranga" hospital "Medical Officer In-charge" OR … | Unrelated results. Nothing. |
| Q18/75 | P3 | "Abercrombie & Kent" Tanzania Arusha "General Manager" OR "Managing Director" … | No head named. A&K's ATE directory entry (its own text) gives a founding statement, used as a lead-brief fact. Its email there is not attributed to anyone; not used. |
| Q19/75 | P3 | Tanzania tourism licensing TALA licensed tour operators list … | No official TALA register is online. Nothing. |

Searches by stratum: P1 12, P2 3, P3 3, introducers 1.

**Why the round stopped at 19 of 75.** The planned split (about 37 P1, 19 P2, 11 P3, 8 introducers) assumed open ground, but there was little left to find:
- Every P1 and P2 organisation without a decision-maker had already been searched one to four times in waves 2 to 12 and in the morning's companies wave. These queries returned travel listings, aggregators and data brokers; the gains came from official lists and the employers' own vacancy notices.
- The introducers were already 81% covered for decision-makers; the crawl and the briefs closed their founding-year, brief and social gaps without search.
- P3 queries found heads only on data-broker sites.
- The remaining 56 searches are left in the shared session cap for the welfare and government workers.

## Blocked, unreadable, or needing a browser read

- **Robots.txt disallows** (browser read, tagged risky): kitamuhouse.com (Kitamu Africa, P1); shidolyasafaris.com (P2).
- **403 / 401 / 429**:
  - P1: pwc.co.tz, jwseagon.com, melia.com;
  - P2: artisan.co.tz, arushavilla.co.tz, leopard-tours.com, marriott.com, ndorolodge.com, pajotasafaris.com, tccl.co.tz, arushacrownhotel.com (401), krishasafaris.com (429);
  - other pages: nmbbank.co.tz/about-us pages and businesswire.com (403).
- **TLS failure**: iaa.ac.tz (P1), lushgardenhotels.co.tz (P2).
- **Not resolving**:
  - P1: health4allclinics.co.tz, safariplus.tz, tz.kcbgroup.com;
  - P2: a1hotelandresort.co.tz, arushacenterinn.com, newwayhotel.co.tz, venicehotel.co.tz;
  - introducers: aphfta.org.
- **Server error or timeout**: alanvertents.com (500), arushabackpackers.co.tz (timeout), mtmerurrh.go.tz/contact-us (503), maoni.moh.go.tz (timeout).
- **Not found (404)**: nnkosmith.com, snvworld.org (the master's website for SNV).

## Not reached

- P1 hotels and clinics with no website and no named manager are left for the call sheet (`scripts/contacts/build_call_sheet.py`): Kibo Palace, Citylink, Ilboru Safari Lodge, Delight, NSK, Old Arusha, Health 4 All, Avinta, R&D, Gemsa, Tanta, Levolosi, Kaloleni, Usa River RC, Oloirien and Kijenge dispensaries.
- About 50 P2 map-point hotels with no email, phone or website, each searched once in September.
- Geocode precision (address-level for 2% of P1) needs a geocoding pass on the street addresses already held; outside this round.
