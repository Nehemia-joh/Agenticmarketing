# Coverage log: wave 3, welfare care (23 September 2026)

- Slice: `runtime/contacts/slices/wave3_welfare_care.json` (40 children's homes and family-based care programmes with no published email or phone, nearest first)
- Output: `data/raw/contact-research/search_wave3_welfare_care_2026-09-23.jsonl`
- Search allowance: 35 WebSearch calls. Used: 35 (Q1/35 to Q35/35). No search was refused by the session cap. After Q35, only URLs already in hand were fetched.
- Fetch pacing: at least 2.2 seconds between requests to the same host. robots.txt was checked before every host was read. Two hosts answered robots.txt with HTTP 403 and were treated as disallowed. The agent's own cache is in `runtime/contacts/agents/wave3_welfare_care/`; the shared crawler cache was not touched.
- Organisations written: 35 of 40.
  - Status counts: found 10, partial 7, not_found 17, blocked 1.
  - Identity: confirmed 30, uncertain 5.
- Results:
  - 33 named leads, all on confirmed identities, 30 of them decision-makers, across 9 organisations.
  - New direct routes: 13 emails and 14 phones, for 10 organisations.
- Prior evidence was read before any search, and failed fetches were not repeated:
  - the slice-A and wave-2 coverage logs and records
  - `data/raw/welfare-research/research_*.jsonl`
  - the NIS register profiles, which publish no contacts
  - the welfare run database, read only, to check for twin records
- Recording rules applied:
  - People come only from the organisation's own site or annual report, or from a parent body's official page.
  - Names on supporter, funder or press pages were not recorded as leads.
  - Nothing about children, parents or residents was recorded. Sponsorship pages, stories and children's reports were not read for content.
  - Each note keeps its warnings within its first 600 characters, the part the profile builder keeps.

## Status definitions

- `found`: identity confirmed and at least one email or phone published by the organisation, its parent body or an official register.
- `partial`: only indirect routes (website, official social page, postal address), or a direct route whose identity or source is uncertain.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/35 | `"One Heart Source" Arusha children's home` | 2. One Heart Source (Arusha) | Only US-charity pages (Wikipedia, GuideStar, Charity Navigator, Omaze blog, 2008 blog, Idealist listing). No Tanzanian route. not_found, uncertain; twin of ORG_08b0d9a3e3caefd0 |
| Q2/35 | `"Hossana Home Care Foundation" Arusha` | 3. HOSSANA HOME CARE FOUNDATION | No match (Kenyan Hossana Initiative, US home-health firms). not_found |
| Q3/35 | `"Olasiti Children's Foundation" Arusha` | 4. Olasiti Orphans Center | Only its known site; home and donate pages have no email or phone; Dorobo Fund is the fiscal sponsor (funder route, noted only). partial |
| Q4/35 | `"Happy Watoto" Kikatiti` | 5. KIKATITI HAPPY WATOTO HOME | Stichting Happy Watoto (happywatoto.nl): general inbox, socials, 2025 annual report naming the Tanzanian management and NGO board. The Kikatiti site has stood empty since 2025 (moved to Ngorika, Maji ya Chai). found |
| Q5/35 | `"Africa Ndoto" Arusha` | 6. AFRICA NDOTO ORGANIZATION | No match (Nyumba Ndoto lodge, Ndoto Hub). not_found |
| Q6/35 | `"Mosses Confort Home Foundation"` | 7. Mosses Confort Home Foundation | Own site: registration 00NGO/R/1185 matches the register; 3 phones, gmail inbox named after the organisation, PO Box 135 Usa River, Kisambare village, founder. found |
| Q7/35 | `"Themi Youth Orphanage" Arusha` | 8. THEMI YOUTH ORPHANAGE | A private GoFundMe appeal and the trekking blog already read. not_found, uncertain |
| Q8/35 | `"Gracious Givers Family" Arusha` | 9. GRACIOUS GIVERS FAMILY | Only differently named organisations (TGGF, TGGC, Gracious Givers South Africa). not_found |
| Q9/35 | `"One Love Africa Foundation" Moshi` | 10. ONE LOVE AFRICA FOUNDATION | OneLove Africa Foundation (Canada and Tanzania): its Biashara Village Ventures programme matches the register. Facebook page; oneloveafrica.ca does not resolve. partial |
| Q10/35 | `"Rolina Association" orphans Moshi` | 11. ROLINA ASSOCIATION FOR ORPHANS | Snippet of a 2018 NaCoNGO list (Hai district); the PDF is unreadable. not_found |
| Q11/35 | `"Emunyani Charity" Tanzania` | 12. EMUNYANI CHARITY | No match. not_found |
| Q12/35 | `"Bahath" orphanage Moshi Usherika` | 13. Bahath Orphanage & Children's Home | Only the World Unite page (HTTP 403 in slice A; not refetched). not_found |
| Q13/35 | `"Kilimanjaro Revival Temple" Moshi` | 15. TAG Kilimanjaro Revival Temple centre | Parent church's Facebook, X and YouTube pages; the church radio's site has no contacts. partial |
| Q14/35 | `"Kili Centre" orphans street children Moshi` | 16. Kilimanjaro Centre for Orphans and Street Children | Snippet of its own page (Kariwa village, Moshi District, founded June 2006); domain DNS failure again; Facebook page. partial |
| Q15/35 | `"Rainbow Centre" "Diocese of Moshi"` | 17. Rainbow Centre, Catholic Diocese of Moshi | Diocese site: the centre sits under the Health Department; Director of Health named; chancery phone, PO Box and inbox. found (parent body) |
| Q16/35 | `"Habari Foundation" Moshi Tanzania` | 19. Habari Foundation (Moshi) | Snippets show habarifoundation.org is the Moshi foundation's own site (founded 2018, PO Box 7644); the site has a bot check (not retried). partial |
| Q17/35 | `"Arnold House" orphanage Moshi` | 20. Arnold House AIDS Orphanage | No match. not_found |
| Q18/35 | `Asali community centre Majengo Moshi Tanzania partner` | 21. Asali partner community centre, Majengo | The partner is Simbas Footprints Foundation (simbasfootprints.org): inbox, Tanzanian and Swiss phones, Majengo Mji Mpya, socials, 6 leads. found |
| Q19/35 | `"Better Future International" Moshi Tanzania orphanage` | 22. Better Future International Tanzania | Only a 2021 journal article (family care model). not_found |
| Q20/35 | `"New Life Christian Children's Home" Moshi` | 23. Children of Destiny / New Life Christian Children's Home | New Life International Foundation for Children (USA), from a snippet; its site answered HTTP 429. blocked, uncertain |
| Q21/35 | `"Grace Orphanage" Moshi Kilimanjaro` | 24. Grace Orphanage (Moshi) | No match (Ugandan namesakes). not_found |
| Q22/35 | `"Kim Jones House" Moshi Tanzania` | 25. Kim Jones House | Facebook page "Kim Jones Children's Home, Moshi"; snippet places it at Gihon Springs. partial |
| Q23/35 | `"OMAWA" Moshi Tanzania orphans` | 26. OMAWA (Moshi) | Own site (Okoa Maisha Ya Watoto): phone, inbox, PO Box 2093, Soweto Street, socials, 5 leads. found |
| Q24/35 | `"Shelter of Hope" St Joseph Moshi Tanzania` | 27. St Joseph Shelter of Hope | Only a namesake hospital in Voi, Kenya; its site does not mention Moshi. not_found, uncertain |
| Q25/35 | `"Franciscan Sisters of St Joseph" Moshi children's home` | 28. St Joseph's Children's Home (Franciscan Sisters) | No match. not_found, uncertain |
| Q26/35 | `"Tanzania Women Research Foundation" Moshi` | 29. Tanzania Women Research Foundation (TAWREF) | Own site: inbox, phone, PO Box 8598, Shaurimoyo Road, Executive Director; Facebook page. found |
| Q27/35 | `"VOV Center" Moshi Tanzania school children's home clinic` | 30. VOV Center (Moshi) | No match. not_found |
| Q28/35 | `"Zorah Organization" orphans Arusha` | 31. ZORAH ORGANIZATION | Own site: 2 inboxes, 2 WhatsApp numbers, Patandi Village (Tengeru); no named leaders. found |
| Q29/35 | `"Comfort Watoto Foundation" Arusha` | 32. Comfort Watoto Foundation [COWAFO] | No match. not_found |
| Q30/35 | `"Life Support for Change" Tanzania Arusha` | 33. LIFE SUPPORT FOR CHANGE (LSFORC) | Facebook page (Mbuguni); own domain does not resolve; GivingWay unreadable (DNS). partial |
| Q31/35 | `"Amazing Grace Widows and Orphans" Tanzania` | 34. Amazing Grace Widows and Orphans Tanzania | Own site: registration matches; mobile, gmail inbox named after the organisation, PO Box 15, Monduli headquarters, 6 leads. found |
| Q32/35 | `"Initiative for Youth" INFOY Arusha orphans` | 35. INITIATIVE FOR YOUTH (INFOY) | infoy.org now serves gambling content (hijacked); nothing used. not_found |
| Q33/35 | `"Tansania lächelt" Arusha` | 36. Tansania Laechelt Organization | Swiss association Tansania lächelt: inbox, Swiss phone, socials, co-presidents and local committee in Arusha. found |
| Q34/35 | `"Kilimanjaro Aid Project" Moshi` | 37. KILIMANJARO AID PROJECT | No match. not_found |
| Q35/35 | `"Kilimanjaro Foundation" Moshi women orphanage centres` | 38. Kilimanjaro Foundation | Own site: 3 inboxes, 2 phones, PO Box 8130, Uru-Shimbwe; CEO and programme manager. found. Allowance spent. |

## Fetches without a search

Each URL below came from the slice, the prior evidence, a result of the search in the same row's organisation, or a link on a page already fetched.

| Organisation | URL | Outcome |
|---|---|---|
| 2. One Heart Source | https://www.idealist.org/en/nonprofit/54dc5db7c7994320bcffa16d5986c87e-one-heart-source-los-angeles | US listing (joined April 2008, Los Angeles PO Box); no Tanzanian route |
| 4. Olasiti | https://www.tanzanianorphans.org/ and /how-to-donate | Registration name, Dorobo Fund link; no email, phone or address |
| 4. Olasiti | https://www.dorobofund.org/, /protect-special-projects, /protect-people | Fiscal sponsor, based in Olasiti; its gmail inbox is a funder route (noted only) |
| 5. Kikatiti Happy Watoto | https://happywatoto.nl/over-happy-watoto/onze-organisatie/, /contact/, /rapportages/ | Organisation history, general inbox, socials, report links; the Dutch street address was not recorded |
| 5. Kikatiti Happy Watoto | Annual report 2025 PDF (https://happywatoto.nl/wp-content/uploads/2026/05/1-jaarverslag_happy_watoto_2025.pdf) | Text extracted locally from the fetched copy; Kikatiti site empty since 2025; management and NGO board; Ngorika School |
| 5. Kikatiti Happy Watoto | Annual report 2020 PDF | Exceeded the fetcher's 4 MB read limit; not used (2025 report used instead) |
| 7. Mosses Confort | https://www.mossesconforthome.com/, /the-team, /about, /contact-2 | Registration, phones, inbox, PO Box, location, founder |
| 9. Gracious Givers Family | https://tggf.or.tz/ and https://graciousgif.org/ | Different organisations (no location; South Africa) |
| 10. One Love Africa Foundation | http://www.oneloveafrica.ca/ | DNS: non-existent domain (also the bare domain) |
| 10. One Love Africa Foundation | https://causes.benevity.org/causes/124-820686632RR0001 | Canadian charity profile confirming identity; Facebook page |
| 11. Rolina | NaCoNGO 2018 PDF (www.nacongo.or.tz/uploads/...) | www host SERVFAIL locally; bare host and WebFetch HTTP 404 |
| 15. TAG KRT centre | https://www.kilimanjarorevivalfm.or.tz/ and /about-us.php | Church-owned radio in Moshi; no phone or email in its pages |
| 16. Kilimanjaro Centre | https://kilicentre.org/kili-centre/ (WebFetch) | EAI_AGAIN (DNS); local lookup SERVFAIL |
| 17. Rainbow Centre | https://www.moshidiocese.org/education and /contact | Parent body page and chancery contacts |
| 17. Rainbow Centre | https://intercare.org.uk/case-studies/rainbow-centre-moshi/ | UK supporter's case study: location; the co-ordinator named there was not recorded |
| 19. Habari Foundation | https://meadowmontessori.org/habari-foundation/ | robots.txt HTTP 403: treated as disallowed, not fetched |
| 21. Asali partner (Simbas) | https://data.charitysense.com/charity/823193062 | Filing summary naming Simba's Footprints, Majengo, Moshi; gives asaliproject.org |
| 21. Asali partner (Simbas) | https://www.asaliproject.org | Python TLS check failed (local issuer chain); curl verified the certificate, so robots.txt, home and /partners/ (redirected to /partnership/) were read with curl |
| 21. Asali partner (Simbas) | https://www.simbasfootprints.org/ (home, contact.html, Board.html, Staff-2.html, about.html) | Contacts, board and staff |
| 23. Children of Destiny / New Life | https://www.newlifeif.org/ | HTTP 429 on robots.txt and home page; not retried |
| 25. Kim Jones House | https://www.continuetogive.com/1643652 | robots.txt HTTP 403: treated as disallowed, not fetched |
| 26. OMAWA | https://omawatanzania.org/ (home, /contact-us/, /team/, /board-members/) | Contacts, team and board |
| 27. St Joseph Shelter of Hope | https://sjshope.org/ | Voi (Kenya) hospital; script-rendered; no Moshi or Tanzania |
| 28. St Joseph's Children's Home | https://www.peekskillfranciscans.org/st-joseth-children | No Moshi, Tanzania or Africa in readable text |
| 29. TAWREF | https://tawref.org/ (home, /contact/, /about/) | Contacts and Executive Director; theme placeholders ignored |
| 31. Zorah | https://zorah.or.tz/ (home, /contact-us/, /about-us/) | Contacts and location |
| 33. LSFORC | www.lifesupportforchange.org and lifesupportforchange.org | DNS: www non-existent; bare domain has no address record |
| 33. LSFORC | https://www.givingway.com/organization/life-support-for-change--lsforc | DNS SERVFAIL locally; EAI_AGAIN through WebFetch |
| 33. LSFORC | https://vymaps.com/TZ/Life-Support-For-Change-Lsforc-1736610629938041/ | HTTP 404 (third-party listing gone) |
| 34. AGWOT | https://amazinggrace.or.tz/ (home, ?page_id=140 contact, ?page_id=65 team, ?page_id=53 about) | Contacts, registration, headquarters and team |
| 35. INFOY | https://infoy.org/ | Gambling content (hijacked); no further pages read |
| 36. Tansania Laechelt | https://www.tansania-laechelt.ch/ (home, /kontakt, /verein, /projekte, /reiseberichte, /inhalte/vereinshistory) | Contacts, board, local committee, projects; no mention of 'Hossana' on the last two pages |
| 38. Kilimanjaro Foundation | https://kilimanjarofoundation.org/ (home, /contact-us/, /the-foundation/) | Contacts, team and mission |

## Blocked or unreadable sites

- newlifeif.org: HTTP 429 Too Many Requests on the first two requests; not retried.
- meadowmontessori.org and continuetogive.com: robots.txt answered HTTP 403; treated as disallowed and not fetched.
- habarifoundation.org: bot-verification page on 2026-09-22 and 2026-09-23 (earlier waves); not retried in this wave.
- world-unite.de (Bahath): HTTP 403 in slice A; not refetched.
- infoy.org: hijacked (gambling content); not used.
- DNS failures:
  - kilicentre.org: SERVFAIL locally, EAI_AGAIN through WebFetch.
  - www.nacongo.or.tz: SERVFAIL locally. Its bare host and WebFetch returned HTTP 404 for the PDF.
  - www.givingway.com: SERVFAIL locally, EAI_AGAIN through WebFetch.
  - oneloveafrica.ca: non-existent domain.
  - lifesupportforchange.org: the www host is a non-existent domain and the bare domain has no address record.
- vymaps.com listing: HTTP 404.
- Facebook, Instagram and X pages: recorded as official pages from search results or the organisation's own site; not read (login wall).
- sjshope.org and peekskillfranciscans.org: mostly rendered in JavaScript. A browser was not used.

## Organisations not reached

- 1. Bethlehem Center for Children (2.7 km, ORG_ccaba4b127b13316): no search spent. The 2026-09-22 run had already searched the name three times and found only the Facebook page and an ngobase entry (already held). No new URL was in hand.
- 14. Kili Kids at Rainbow Ridge (22.8 km, ORG_a1f3972574c8fef3): no search spent. The only sources are a 2014 blog and a 2017 appeal, both already read.
- 18. Matumaini Child Care (22.8 km, ORG_6cab4cfa59fba51c): no search spent. The only source is a 2007 blog, already read.
- 39. Home Foundation (Rhotia) (110 km, ORG_359f116b8adf9907): outside the catchment; not searched.
- 40. Huruma Centre Orphanage (Iringa, 500.6 km, ORG_ecda3e381f90c5d7): outside the catchment; not searched.

## Problems and warnings

- **Stopping rule partly met.** 35 of the 38 in-catchment organisations got one search each, and the allowance was then spent. That left Bethlehem Center (searched three times on 2026-09-22), and Kili Kids and Matumaini (stale sources only).
- **Hijacked domain.** infoy.org (INFOY) now serves Indonesian slot-gambling content; nothing from it was used.
- **Home closed, organisation active: KIKATITI HAPPY WATOTO HOME.**
  - Happy Watoto's 2025 annual report says the Kikatiti site has stood empty since 2025. The children moved to Ngorika Home and School (Maji ya Chai), a temporary daycare ended in December 2025, and the site is to be sold.
  - The organisation continues at Ngorika. The note is therefore worded as "location to check", not as a closure.
  - The note also asks for a check before outreach, because Happy Watoto runs an English-medium primary school (about 250 pupils, including fee-paying local pupils).
- **Location to check:**
  - Mosses Confort: the register pin is 9.0 km from Kijenge, but the home is in Kisambare village, Usa River ward.
  - Rolina: the 2018 NaCoNGO list gives Hai district; the register gives Moshi.
  - AGWOT: its site and the register give Monduli; an Idealist listing says Moshi Urban.
  - Tansania Laechelt: its register pin is identical to INFOY's.
  - St Joseph Shelter of Hope: the only match is in Voi, Kenya, outside the catchment area.
- **Related records** (not merged):
  - One Heart Source (Arusha) is a twin of ORG_08b0d9a3e3caefd0 and of the funder record ORG_6c36122d00b7a131.
  - The Rainbow Centre's routes are those of the Catholic Diocese of Moshi, which has its own record (ORG_0050c8fb39706440).
  - Habari Foundation (Moshi) and Habari Foundation International (ORG_25ee34d6ed658e77) share habarifoundation.org.
  - "Asali partner community centre, Majengo" is Simbas Footprints Foundation; the record could be renamed.
  - Slice A's "One Love Tanzania" is a different organisation from OneLove Africa Foundation; do not merge its routes.
  - No link was found between Tansania lächelt's "Tabasamu Campus" and the welfare records "Tabasamu Childcare and Orphanage Centre" (ORG_8797eaeb13c2cf3a) or "TABASAMU AFRICA ORGANIZATION" (ORG_2a405ec42bdab16b).
- **Fit to check:**
  - OneLove Africa Foundation is a women's micro-enterprise programme, not residential care.
  - Better Future International uses kinship family care, so its segment should be family-based.
  - Zorah now runs a daycare and nursery and community programmes, not a residential home.
  - Happy Watoto may be a competitor (see above).
- **Safeguarding.** No new concerns. Sponsorship pages, stories, travel reports and children's reports were not read for content. Nothing about children, parents or residents was recorded.
- **Privacy decisions.** None of the following was recorded:
  - Personal pages: TAWREF's Executive Director's personal LinkedIn profile; a volunteer call posted from a personal Facebook profile (AGWOT).
  - Contacts that are not the organisation's:
    - AGWOT's web designer's gmail and phones (site footer)
    - LSFORC's phone and PO Box from a third-party listing
    - OneLove's masked Canadian email
  - Street addresses: the residential-looking Dutch (Happy Watoto) and Swiss (Tansania lächelt) street addresses.
  - Uncertain or unsuitable leads:
    - Happy Watoto's Dutch board, whose roles conflict between the website and the report
    - names found only on supporter or press pages (the Rainbow Centre co-ordinator, the TAG centre's press quotes)
    - first names only (the Bahath founders)
    - team members listed without roles (Mosses Confort)
    - a public-figure patron (Tansania lächelt)
  - Personal details: staff qualifications (OMAWA) and family relationships.
- **Tooling notes:**
  - Python could not verify asaliproject.org's certificate chain, but curl verified it through the Windows certificate store. The site was read with curl after a robots.txt check; verification was never disabled.
  - The local resolver (10.10.1.1) returned SERVFAIL for several hosts. WebFetch showed the same DNS failure for them.
  - PDF text was extracted locally from the fetched copy; nothing was saved to the repository.

## Next-run priorities

- Bethlehem Center for Children (2.7 km, nearest): try its Facebook handle "becechi" as a query, or ask the user to open the Facebook page.
- A Tanzanian phone or email for Happy Watoto at Ngorika, Maji ya Chai (for example "Ngorika School" Maji ya Chai).
- Habari Foundation (Moshi): ask the user to open habarifoundation.org by hand (bot check). It pays primary school fees for about 40 pupils.
- Retry once, in a later session:
  - newlifeif.org (HTTP 429), to confirm the New Life / Children of Destiny link
  - kilicentre.org and the LSFORC GivingWay profile, when DNS resolves
- The "Hossana" home that Tansania lächelt supports: check whether it is HOSSANA HOME CARE FOUNDATION.
- No web presence found. Reach them through the register or the district social welfare offices:
  - Arusha area: Hossana, Africa Ndoto, Gracious Givers Family, Emunyani, COWAFO
  - Moshi area: Rolina, Arnold House, Grace Orphanage, VOV Center, Kilimanjaro Aid Project
- INFOY: its domain is hijacked; look for a route through Arusha City Council's youth platforms, which the search results mention.
- School-fit signals:
  - Mosses Confort: boarding, with schooling from pre-primary to college
  - Simbas Footprints: school partnerships and after-school programmes
  - OMAWA: pays school costs
  - TAWREF: early childhood development
  - Zorah: daycare and nursery, a possible pre-primary feeder
  - Kilimanjaro Foundation: school supplies from pre-primary to secondary
  - Tansania lächelt: supports about ten homes and schools
  - Happy Watoto: runs its own English-medium school, possibly a competitor
