# Government enrichment round 2, 10 October 2026: coverage log (stratified)

Run `arusha-government-2026-09`. Goal: more data points per office (holders, quick-decision contacts, routes, addresses), measured per
stratum of office level, and for wards per distance band from the nearest campus. Allowance: 40 web searches (hard cap, shared by three
workers this session). Used: **22 of 40**. Measured with `scripts/government/measure_government_coverage.py` (from `final.json`).

Columns: `holder` = the lead post (RC, DC, council director, WEO, VEO) named with a source date; `verified` = of those, verified by the build;
`quick` = offices with at least one quick-decision post named (RAS or regional education or community development; DAS; council education,
community development or social welfare head; ward community development officer; village chair); `quick_posts` = those named posts;
`email`, `phone`, `postal` = official office email (or role inbox), office phone, P.O. box; `physical` = physical address in words;
`point` = office point at address precision; `census` = 2022 census population; `signals` = official news or notices with a convening tag
that name the office.

## Baseline (before this round)

| Stratum | offices | holder | verified | quick | quick_posts | email | phone | postal | physical | point | census | signals | geocode precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 region | 3 | 3 | 3 | 3 | 4 | 2 | 2 | 3 | 3 | 3 | 0 | 3 | address 3 |
| 2 district | 7 | 7 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 7 | address 1, none 6 |
| 3a council: pilot | 4 | 4 | 4 | 2 | 2 | 4 | 4 | 4 | 2 | 4 | 4 | 4 | address 4 |
| 3b council: other | 5 | 5 | 5 | 3 | 4 | 5 | 5 | 5 | 4 | 4 | 5 | 4 | address 4, none 1 |
| 4a ward: up to 10 km | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 51 | 1 | estimated 51 |
| 4b ward: 10-20 km | 34 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 34 | 1 | address 3, estimated 31 |
| 4c ward: over 20 km | 31 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 1 | estimated 31 |
| 4d ward: not located | 12 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | none 12 |
| 5 village | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | address 2 |
| **all** | **149** | **21** | **16** | **12** | **14** | **11** | **11** | **12** | **9** | **17** | **137** | **21** | |

Ward councillors (not a column above): 127 of 128 wards named from official rosters, unchanged.

## After this round

| Stratum | offices | holder | verified | quick | quick_posts | email | phone | postal | physical | point | census | signals | geocode precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 region | 3 | 3 | 2 | 3 | 5 | 2 | 2 | 3 | 3 | 3 | 0 | 3 | address 3 |
| 2 district | 7 | 7 | 4 | 5 | 5 | 0 | 0 | 0 | 0 | 1 | 0 | 7 | address 1, none 6 |
| 3a council: pilot | 4 | 4 | 4 | 2 | 4 | 4 | 4 | 4 | 2 | 4 | 4 | 4 | address 4 |
| 3b council: other | 5 | 5 | 4 | 3 | 4 | 5 | 5 | 5 | 4 | 4 | 5 | 4 | address 4, none 1 |
| 4a ward: up to 10 km | 51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 51 | 1 | estimated 51 |
| 4b ward: 10-20 km | 34 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 34 | 1 | address 3, estimated 31 |
| 4c ward: over 20 km | 31 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 31 | 1 | estimated 31 |
| 4d ward: not located | 12 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | none 12 |
| 5 village | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | address 2 |
| **all** | **149** | **22** | **14** | **13** | **18** | **11** | **11** | **12** | **9** | **17** | **137** | **21** | |

`verified` fell by two on purpose: the Manyara Regional Commissioner and the Simanjiro council director are now marked to recheck (below).
The Siha council director row changed holder (a handover the profile does not show yet).

## Deterministic sources first (no search budget)

1. **Holder-mention extractor** (`gov_lib.holder_mentions`): it missed honorifics written without a space ("Bi.Warda", "Mwl.Marcel",
   "Mhe.Gloriana"), lower-case honorifics ("ndugu"), "DAS <district>", council titles written "Halmashauri ya <name>" and the regional
   community development head. Fixed, and all-capitals headlines (which give no end to a name) are now skipped. The 13 captures of
   2026-10-10 were re-extracted from the cache (`collect_council_sites.py --date 2026-10-10 --refresh`); only the three known 404 pages were
   requested again. Only `holder_mentions` changed in the captures (checked field by field). 58 mentions added, 3 garbage mentions dropped.
   One misattribution found and rejected in `links.json` `holder_rejects` (a caption that names the Meru council director straight after
   "Mkuu wa Wilaya ya Arumeru,").
2. **Full news text** (2,102 cached news and notice items from both captures) read for ward, village and mtaa executive officers, education,
   community development and social welfare officers, DAS and DC office details. Results in `post_holders_gov_round2_2026-10-10.json`.
3. **Official documents** (`scan_official_documents.py --date 2026-10-10`): 12 PDFs listed on the sites (Arusha regional strategic plan
   2026-2030, Kilimanjaro strategic plan and client service charter, Simanjiro and Moshi DC strategic plans, Monduli investment profile,
   TAMISEMI newsletter 52, organisation structures). No District Commissioner's office address, phone or email and no ward or village
   executive officer roster in any of them. Scanned (image) PDFs that would need a transcription to read: Moshi DC strategic plan
   (107 pages), Monduli "Muundo wa Mamlaka ya Serikali za Mtaa" (42 pages), the Kilimanjaro and Moshi Municipal organisation charts; the
   Kilimanjaro client service charter is mostly images (448 characters over 8 pages). None is likely to hold DC office routes.
4. **GWF CORE API pages** tried by slug: `arushacc.go.tz` `sekei`, `elerai` (ward pages the search engine still indexes from the old site);
   `sihadc.go.tz` `wards` (linked from its footer), `othercontacts`, `contact-us`; `manyara.go.tz` `simanjiro`, `kumuona-mkuu-wa-mkoa`;
   `mondulidc.go.tz` `contact-us`. All 404: the old sites' pages are not on the new framework.
5. **OpenStreetMap**: one exploratory Overpass query for office names the run's two queries miss (kata, ward, wilaya, district office, boma,
   mtaa, kijiji, village, tarafa). 504 on the first endpoint, then answered; nothing new (ward-border markers, shops, a court). Unproductive.
6. **Wikipedia** full ward articles (7 requests, 2 s apart): a few Arusha City articles name the neighbourhood of the ward office
   (Ngarenaro: Kambi ya Fisi) and give postal codes, but the text is unofficial and partly wrong (Sekei's says "Kata ya Karatu"). Not used.
7. **Census**: already cached; every ward and council has its 2022 population.

## Searches (Q n/40, by stratum)

| Q | Stratum | Query | Outcome |
|---|---|---|---|
| Q1/40 | 3a pilot council | "Afisa Elimu Msingi" "Jiji la Arusha" 2026 | Nothing relevant (Ruvuma pages) |
| Q2/40 | 3a pilot council | Mkuu wa Divisheni ya Elimu Awali na Msingi Jiji la Arusha (arushacc.go.tz, arusha.go.tz) | Old-site pages only; ward slugs sekei, elerai (404 in the API) |
| Q3/40 | 3a pilot council | "Afisa Elimu Msingi" Halmashauri ya Wilaya ya Meru | Nothing relevant (Meru County, Kenya) |
| Q4/40 | 3a pilot council | merudc.go.tz Mkuu wa Divisheni Elimu Msingi Meru DC Mwl (merudc.go.tz) | 2024-2025 news on the old site; no name |
| Q5/40 | 4a ward up to 10 km | "Mtendaji wa Kata" Jiji la Arusha 2026 (four council and regional hosts) | 2022 Arusha DC recruitment documents only |
| Q6/40 | 4a ward up to 10 km | "Afisa Mtendaji wa Kata ya" Arusha mjini Sakina OR Sombetini OR Kaloleni OR Themi OR Ngarenaro | Wikipedia ward articles only |
| Q7/40 | 2 district | "Ofisi ya Mkuu wa Wilaya" Hai "S.L.P" Bomang'ombe | Nothing relevant |
| Q8/40 | 2 district | "District Administrative Secretary" Arumeru OR Monduli OR Hai OR Siha "P.O. Box" | Old appointment news; no address |
| Q9/40 | 2 district | President Samia appoints district commissioners 2026 Monduli Simanjiro Moshi new DC list | Led to the 27 August 2026 regional reshuffle report (Q10) |
| Q10/40 | 1 region | "Mkuu wa Mkoa wa Manyara" Septemba 2026 | The Citizen, 27 Aug 2026: Manyara RC transferred to Morogoro, successor named (fetched; nation.africa copy 403) |
| Q11/40 | 1 region | Mkuu wa Mkoa wa Manyara Martine Shigela (go.tz) | No official page names the successor at Manyara yet |
| Q12/40 | 2 district | Samia new district commissioners September 2026 Lugangira Arumeru Mwikozi Arusha | Daily News ?p=163358 (fetched): the late-September reshuffle list |
| Q13/40 | 2 district | "Florida Lulandala" Katibu Tawala Wilaya ya Moshi | No official source |
| Q14/40 | 2 district | "Mkuu wa Wilaya" Arumeru OR Monduli OR Siha OR Simanjiro ofisi "S.L.P" barua pepe (go.tz) | Council contact pages only; old-site "How do I" pages (shell, 404 in the API) |
| Q15/40 | 3a pilot council | "Maendeleo ya Jamii" "Jiji la Arusha" Mkuu wa Divisheni 2026 | Nothing relevant |
| Q16/40 | 4a ward up to 10 km | "Afisa Mtendaji wa Kata" Usa River OR Akheri OR "Maji ya Chai" OR Kikatiti OR Nkoaranga OR Poli | Wikipedia only |
| Q17/40 | 4b ward 10-20 km | "Mtendaji wa Kata ya" Masama OR Machame OR Bomang'ombe OR Muungano Hai Kilimanjaro (haidc, kilimanjaro) | Old-site pages; no name |
| Q18/40 | 4c ward over 20 km | "Afisa Mtendaji wa Kata" Manispaa ya Moshi 2026 | Nothing relevant |
| Q19/40 | 3b other council | Mkurugenzi Mtendaji Halmashauri ya Wilaya ya Simanjiro Mwanamvua Muyombo | No official source |
| Q20/40 | 5 village | "Mtendaji wa Kijiji" "Maji ya Chai" OR Mwanama Meru OR Arusha | Nothing relevant |
| Q21/40 | 1 region | "Afisa Elimu Mkoa wa Kilimanjaro" 2026 | Nothing relevant |
| Q22/40 | 2 district | "Katibu Tawala Wilaya ya Monduli" OR "Katibu Tawala wa Wilaya ya Monduli" OR "DAS Monduli" | Nothing relevant (a party list in the results was not opened) |

Split: pilot councils 5, wards up to 10 km 3, wards 10-20 km 1, wards over 20 km 1, districts 7, regions 3, other councils 1, villages 1.
The plan weighted pilot councils and the nearest wards (about 10 and 10 of 40); both stopped early as unproductive (5 and 3 queries
returned nothing current), and the budget moved to districts and regions, where the reshuffle reports were the round's only search finds.
**Stopped at 22**: every stratum had been tried and the engine does not index current Tanzanian council news (it returns the old sites'
2022-2025 pages and other regions). The remaining 18 searches were not used.

## Findings

From official news (cached item text, quoted in `post_holders_gov_round2_2026-10-10.json` or found by the mention extractor):

- **Siha council director**: handover reported by Siha District Council on 1 October 2026 (news 10676): Hellen Mwambeta moved to
  Shinyanga Municipal Council, "Bw. Binuru Mussa" takes her place. The leadership profile (2026-09-04) is not updated; the record supersedes it
  and a review item asks to confirm. (Daily News spells the incoming director "Binuru Shekidele".)
- **Simanjiro District Administrative Secretary**: Warda A. Maulid / Warda Abeid Maulid (Simanjiro news 1358 and 1463, 2026-03-16).
- **Arusha District Council community development head**: Stedvant Kileo (Arusha DC news 1948, 2026-03-26).
- **Arusha District Council social welfare officer**: Beatrice Tengi (regional news 4057, 2026-05-19); an officer, not stated to be the head.
- **Arusha regional community development head**: Erena Materu (Meru DC news 10431, 2026-09-01; Monduli news 2193, 2026-03-27).
- **Bwawani ward executive officer** (Arusha DC, 22.9 km): Simon Kaaya (regional news 6543, 2026-07-16); one item, marked to review.

From national newspaper reports (used only to mark a post to recheck; officials are named only from official sources):

- The Citizen, 27 August 2026: the Manyara Regional Commissioner was transferred to Morogoro and a successor named. The Manyara site's profile
  (31 July 2026) still shows the previous holder. `holder_recheck` for that post.
- Daily News (dailynews.co.tz/?p=163358), late-September 2026 reshuffle: confirms the Arusha, Arumeru and Hai DC changes already in the run,
  the Siha and Moshi Municipal director changes, a new Moshi District Administrative Secretary (searched as Q13, not recorded as the holder until an official source
  does), and a council executive director moved to Simanjiro. `holder_recheck` for the Simanjiro director. It does not mention the Moshi,
  Monduli or Simanjiro District Commissioners, which suggests they stayed; they remain marked to recheck until an official item after
  27 September names them.

## Blocked and browser-only

- nation.africa reshuffle article: HTTP 403 (the same article was read on thecitizen.co.tz).
- Overpass main endpoint: one 504, retried with backoff and answered.
- Old-site URLs the search engine still indexes (`sihadc.go.tz/othercontacts`, `arushacc.go.tz/<ward>`, `*/how-do-i-single/...`): the new
  framework returns a script shell and the API has no such pages; a browser read would show the same shell. No site needs a browser read
  for this round.

## Not reached (for the GA01 meetings)

- District Commissioners' office postal addresses, phones and emails: not published in any official source read (sites, documents, search).
- Heads of Pre-Primary and Primary Education for Arusha City and Meru; community development heads for Arusha City, Meru and Hai; social
  welfare officers for every council except Arusha DC.
- Ward executive officers: 3 of 128 named (Mnadani and KIA in Hai, Bwawani in Arusha DC). Ask each pilot council for the WEO list.
- Monduli and Moshi District Administrative Secretaries (Moshi: a newspaper names a new appointee); the current Manyara Regional
  Commissioner and Simanjiro council director from an official source.
