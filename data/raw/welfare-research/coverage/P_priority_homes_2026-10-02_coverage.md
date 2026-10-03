# Slice P: priority homes, family programmes and specialised centres (2026-10-02)

Targets: `runtime/contacts/slices/welfare12_P.json` (67). Output: `data/raw/welfare-research/research_P_priority_homes_2026-10-02.jsonl`.
Records: 66 organisation, 80 contact, 16 relationship (162 lines, all parse). Every organisation record uses the target's exact name.

Method: pages read with `scripts/contacts/contact_lib.py` (the `read_page.py` fetcher: cache, robots.txt honoured, 2 s per site). The scratch crawler
`runtime/contacts/agents/welfare12_P/crawl.py` read each own site's home page plus up to eight contact, team, about and programme pages, and each NIS register
profile. `crawl2.py` read known partner, funder and news pages for targets with no own site. WebFetch was refused by the session's permissions for three
script-rendered or certificate-failing sites (mkombozi.org, farajaorphanage.org, malaika-childrenfriends.org); nothing else was tried for them.

## Searches (15 of 15 used)

| # | Query | Target | Result |
|---|---|---|---|
| Q1/15 | "Ngarasero Community Organization" Usa River | Ngarasero | Facebook, GoFundMe, Daily News (held). History in snippet; no email or phone. WorldPlaces returned HTTP 511. |
| Q2/15 | "Bahath" orphanage Moshi Tanzania | Bahath | Snippet only (World Unite pages return 403). |
| Q3/15 | "Kilimanjaro Centre for Orphans and Street Children" Moshi | Kili Centre | Snippet: founded June 2006, three programmes; kilicentre.org does not resolve. |
| Q4/15 | "St. Joseph" orphanage Kiserian Arusha sisters | St. Joseph's | Unite Africa Foundation pages read (founder-director, 50+ children). |
| Q5/15 | "Kitaa Hope Home" Moshi | Kitaa | hope-home.de read; Hope Home Trust snippet (site 429). |
| Q6/15 | "Faraja Orphanage" Shangarai Arusha | Faraja | Sustainable Vision listing read (founder, PO Box, phone). |
| Q7/15 | "Mkombozi Centre for Street Children" Moshi contact | Mkombozi | CRIN directory read; envaya page has an expired certificate. ZoomInfo result ignored (data broker). |
| Q8/15 | "HopeCare" Arusha children Boma Road | HopeCare | Nothing about HopeCare; target not found. |
| Q9/15 | "SOS Children's Village" Arusha Tanzania village director contact | SOS Arusha | SOS Canada page and ATE member directory read. Contactout and RocketReach results ignored (data brokers). |
| Q10/15 | "Building a Caring Community" BCC Moshi disabilities centres contact | BCC | Own site still HTTP 522; contact details from snippet only (fetched: false). |
| Q11/15 | "Karim Children" care centre Arusha orphanage | Karim | karimorphanage.org does not resolve; details from snippet only (fetched: false). |
| Q12/15 | "Kao La Amani" children's village Boma Ng'ombe | Kao La Amani | Article 25 news page read (60 children, 2026). Tir na nOg site 403. |
| Q13/15 | "Laketatu" orphanage Usa River Tanzania | Laketatu | RNZWCS news page read (capacity 140, nearby school). |
| Q14/15 | "Positive Steps in Arumeru" POSA orphanage Usa River | POSA | Only the 2019 blog already held. |
| Q15/15 | "Peace House" Africa Arusha orphans school contact | Peace House | school.co.tz profile read; peacehousefoundation.org does not resolve. |

## Pages read per target (own site pages / other pages)

Pages read for each target are listed in `runtime/contacts/agents/welfare12_P/pages/<nn>/log.json` and `log2.json` (nn = target index).

| # | Target | Read | Main result |
|---|---|---|---|
| 0 | Afroplan Foundation | NIS | Own site robots.txt disallows: not read. Register only. |
| 1 | Amani Centre for Street Children | 8 own + NIS | Own-domain info@amanikids.org; team of 9; 338 rescued in 2025. |
| 2 | Bahath | World Unite 403 | Search snippet only. |
| 3 | Bethlehem Center for Children | 4 own (Wix) + Heart for Africa 4 | Founder, 15-20 children, government schools; funder Heart for Africa. |
| 4 | Born to Learn | 5 own (4 pages HTTP 429) | Moshi address, 400 children daily. |
| 5 | BCC | own site HTTP 522; Tanzania Volunteers 4 | 10 centres, 250+ children; route from snippet only. |
| 6 | Canaan Children's Center | 6 own | 39 children; Yakini Primary School; ED, social worker, coordinator. |
| 7 | Child First Initiative | 9 own + NIS | Baby home (20), 45 sponsored; registration. |
| 8 | Children of Kilimanjaro Orphanage | 9 own | 32 children; staff incl. chief patron and matron. |
| 9 | Christ Hope Orphanage | 2 own | 44 children; director Steven Issangya. |
| 10 | Compassion International Tanzania | 9 own | New office phone; national director and managers. |
| 11 | Cradle of Love Baby Home | own 403; Giving Smiles 2 | Closed March 2024. |
| 12 | Emusoi Centre | 9 own | Founder-director died April 2026; secondary girls. |
| 13 | Enyorata Children's Home | 8 own + NIS | 25 children 3-10 at a private English-medium school. |
| 14 | Faraja Orphanage | own (script only) + 1 directory | Founder, phone, PO Box. |
| 15 | Fruitful Orphanage | 9 own | Blue Sky private school sponsorships (about 2017). |
| 16 | GP-COSU | 1 own + NIS | 12 children in a house; Ilboru ward outreach. |
| 17 | Halima Orphanage Center | 4 own (3 x 404) | Pasua ward address; 25 children's school needs Jan 2026. |
| 18 | Havilah Children's Village | 4 own | Directors Fred & Naomi with phones; 20 children. |
| 19 | Hope Orphanage Center | 5 own + NIS | Directors David and Beatrice Mollel; 14 + 42 children. |
| 20 | HopeCare (Arusha) | none | Not found (no site, no search result). |
| 21 | House of Happiness | 6 own | 54 children (Aug 2026), Kisongo, state school. |
| 22 | Kao La Amani | own 403 + NIS + Article 25 | 60 children; registration. |
| 23 | Karama Kids | 3 own + ProPublica org page | 20 children 5-18; 990-EZ FY2025 revenue $64,204. |
| 24 | Karim Children's Care Centre | own DNS fail + NIS + 4 partner | 27 children; founder Rehema; route from snippet only. |
| 25 | Kili Kids at Rainbow Ridge | 9 own | 43 kids; Tanzanian board. |
| 26 | Kili Centre | own DNS fail + Idealist | Snippet only. |
| 27 | Kilimanjaro Children's Foundation | 7 own | Early-years school, 200 children, Jorno village. |
| 28 | Kilimanjaro Children's Fund | 3 own | 55 children Pasua; private and public schools. |
| 29 | Kilimanjaro Orphanage Centre | 6 own (newsletter PDF too large) | 89 children, Shabaha village; owner named. |
| 30 | Kitaa Hope Home | own trust site 429; hope-home.de | KITAA umbrella; 30 residential (snippet). |
| 31 | LOHADA | 9 own | Runs Camp Joshua primary school (200+). |
| 32 | Laketatu Orphanage | Papamoa Rotary 3 + RNZWCS | About 100 children, local schools 400 m. |
| 33 | Light in Africa | 1 own (single-page site) | Seven homes; no organisation route. |
| 34 | Maasai Girls Rescue Center | 12 own (earlier wave pages) | Karatu, outside catchment; 75+ girls. |
| 35 | Malaika Children's Friends | own TLS failure + NIS | Register only. |
| 36 | Mkombozi | own (script only) + CRIN | PO Box, ages 5-18. |
| 37 | Moshi Kids Centre | 9 own | Early childhood 3-6, Pasua; second phone. |
| 38 | Msamaria Centre | 5 own + NIS | Government primary schools named; capacity 75. |
| 39 | Neema Village | 9 own | Baby home; leadership. |
| 40 | Ngarasero Community Organization | NIS + 3 news | 20 children need primary sponsorship (2026); manager. |
| 41 | Nkoaranga Orphanage | 5 own (hospital) | 30 infants; head Mama Andrew. |
| 42 | OKAT Children's Home | 3 own | 25 children (July 2026), from age 5. |
| 43 | POSA | 1 blog (2019) | 25+ aged 3-7; operator named. |
| 44 | Peace House | own DNS fail; safari partner 4; school.co.tz | 240+ boarding; phone of the secondary school. |
| 45 | Rainbow Centre | 4 blog pages (2010) | Historical. |
| 46 | SOS Children's Village Arusha | 9 SOS Intl + SOS Canada + ATE | Own primary school; Kenya route in record is wrong. |
| 47 | Samaritan Village | own 429 + NIS | Register only. |
| 48 | Save Africa Orphanage | 7 own + NIS | 78 children; Amani and Hiradali private schools. |
| 49 | Seeway Tanzania | 8 own + NIS | All primary children in private school; Imbaseni. |
| 50 | Selfless Solutions | own 403 + NIS | Register projects only. |
| 51 | Sibusiso Foundation | 9 own | ED and coordinator role emails. |
| 52 | St. Joseph's (Kiserian) | own DNS fail; Unite 2 | Founder-director; 50+ children. |
| 53 | St. Mark's (Usa River) | own (script only); Utopia 4 | 200+ children; Director "Dr. Moshi". |
| 54 | Sun of Hope Village | 10 own | 50 children (2020), pre-school on site. |
| 55 | TAG Kilimanjaro centre | Daily News + church radio 2 | 400+ children over 20 years; Compassion partner. |
| 56 | Tabasamu | 9 own | Founder; no counts. |
| 57 | The Foundation For Tomorrow | 9 own + NIS | Scholarship funder at Usa River; TZ managing director. |
| 58 | Tuleeni Children's Home | 9 own + NIS + 1 | 100+ children, $26,000 fees a year; named contacts with phones. |
| 59 | Tumaini Children's Foundation | 4 own + NIS | New TZ phone; founder-ED Oddo Ndonde. |
| 60 | Tumaini For Africa Orphanage | funder 2 | 30+ children all in private English-medium schools. |
| 61 | Tupendane Orphanage | Tupendane Africa Foundation 3 | Possible match only (registered 2022). |
| 62 | Ujamaa Children's Home | own 429 + NIS | Register only. |
| 63 | Ummu Aisha Orphanage Centre | 1 own | Licence 06422; 27 primary pupils; full address. |
| 64 | Upendo Children's Home | OKAT + Tanzania Volunteers 3 | 45 children 0-7, nursery school. |
| 65 | URRC | 9 own | Updated phone; SETU email and phone. |
| 66 | WEHAF | 9 own | Recommends private school for sponsored children; team incl. social worker. |

## Blocks and unreadable sources (none worked around)

- robots.txt disallows: afroplanfoundation.com.
- HTTP 429: borntolearnglobal.org (some pages), hopehometrust.org.uk, samaritanvillageorphanage.org, ujamaachildren.org, arushakidstrust.com.
- HTTP 403: cradleoflove.com, tirnanogchildrensfoundation.com, selflesssolutions.org, world-unite.de (both language versions), ngobase.org.
- HTTP 522 (server down): buildingacaringcommunity.org (twice). HTTP 511: tanzania.worldplaces.me.
- DNS failure (domain gone): karimchildren.org, karimorphanage.org, kilicentre.org, stjosephorphanage.co.tz, peacehouseafrica.org, peacehousefoundation.org, sos-childrensvillages.or.tz, lightinafricaschildrenshome.com, farajaorphanagechildrenshome.org.
- TLS failures: malaika-childrenfriends.org, envaya.org.
- Script-only pages (no text): mkombozi.org, farajaorphanage.org, saintmarkskids.org. WebFetch was not permitted in this session.
- commonwealthofnations.org now redirects to a gambling site: not used.
- Not used as sources: LinkedIn, Facebook, ZoomInfo, Contactout, RocketReach, GoFundMe, Tripadvisor.

## Gaps and leads not confirmed

- HopeCare (Arusha): nothing found.
- Still no email or phone: Ngarasero (strong lead), Seeway (contact form only), Laketatu, POSA, Kili Centre, Bahath, St. Mark's, TAG centre, Kao La Amani, Light in Africa, St. Joseph's.
- Route facts from search snippets only (fetched: false): BCC (+255769812291, info@buildingacaringcommunity.org) and Karim (+255689571452, info@karimorphanage.org). Confirm before use.
- SOS Children's Village Arusha: the held route (info@soskenya.org, +254...) belongs to SOS Kenya; replace it. Only the national office phone was confirmed.
- Tupendane: the 2022 NGO found may not be the 2020 "Tupendane Orphanage".
- Kilimanjaro Orphanage Centre: called "defunct" by Kilimanjaro Children's Fund (2021) while its own site is live; shares wording with Tuleeni's site.
- Emusoi: the new director after the founder's death (April 2026) is not named.
