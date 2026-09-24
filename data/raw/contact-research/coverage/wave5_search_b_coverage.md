# Coverage log: wave 5, search slice B (2026-09-24)

Slice: `runtime/contacts/slices/wave5_search_b.json`: 51 organisations, nearest first. 45 are company-master records (44 needed a named decision-maker, Kili Star Tours needed a route); 6 are welfare homes and programmes (Malaika Children's Friends needed a leader, the other five a route). Most master records are TATO members or affiliates whose own sites the crawler could not read.
Search allowance: 40 WebSearch calls, all used (Q1/40 to Q40/40). No search was refused by the session cap. After Q40 only URLs already in hand were fetched.
Output: `data/raw/contact-research/search_wave5_search_b_2026-09-23.jsonl` (51 records, one per organisation, in slice order). Scratch: `runtime/contacts/agents/wave5_search_b/`. Accessed on 24 September 2026.

Pages were read with the logic of `scripts/contacts/read_page.py` (robots.txt Disallow rules matched by `contact_lib.Robots`), through a scratch wrapper that keeps its cache in the scratch folder, spaces requests to one host at least 2 s apart (also across calls), and treats HTTP 429 as a block.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 51 (45 master, 6 welfare) |
| Researched (one JSONL line each) | 51 |
| found | 19 |
| partial | 24 |
| not_found | 7 (trekkingandsafariadventures, Kili Star Tours, Top Of Africa Treks, Upendo Children's Home, Matumaini Child Care, Home Foundation (Rhotia), Huruma Centre Orphanage) |
| blocked | 1 (Arusha Tours) |
| Not reached (no line written) | 0 |
| Identity uncertain | 6 (trekkingandsafariadventures, Fantacy Adventures, Kili Star Tours, Meru Mountain Treks, Matumaini Child Care, Home Foundation (Rhotia)) |
| WebSearch calls used | 40 / 40 (18 organisations needed none; 7 got a second search) |
| Named people recorded | 41 in 20 organisations, all `medium`; 39 read on fetched pages, 2 snippet-only (Malaika Children's Friends) |
| Emails / phones not in the profiles' current fields (approximate match) | 29 / 40, in 21 organisations |
| Website fields that are new or differ from the master | 19 |

Status rules for this slice:
- `found`: identity confirmed and the gap filled: a named leader or decision-maker from an allowed source (own site, TATO entry, the company's own text on an operator directory, a parent body or group page), or, for route gaps, a published email or phone.
- `partial`: profile data confirmed or added (routes, addresses, socials), but the gap not filled (no leader named, snippet-only, first name only, a contact without a leadership title), or the organisation is outside the area.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the only sources refused automated reading.

## Searches

| # | Organisation | Query | Outcome |
|---|---|---|---|
| Q1/40 | Tanzania Outfitter & Safaris (O156beede60a7) | "Tanzania Outfitters" safaris Arusha | No result for this company: only differently named firms (Tanzania Climbing Outfitters & Safaris Ltd, Safari Outfitters) and directory listings. Nothing recorded. |
| Q2/40 | Bald Eagle Safaris Limited (O5df6bc6b95bb) | "Bald Eagle Safaris" Arusha founder OR director OR owner | Own site, TATO, Instagram, TripAdvisor, SafariDeal and SafariBookings (p7477, read: 5-10 employees, founded 2024, Kisongo office); no leader named. |
| Q3/40 | Game Drive Travel Africa Safari Agency (O2a65c8c9c56a) | "Game Drive Travel Africa" safari agency Arusha | SafariBookings p4050 and SafariGo 368 (read: NSSF Mafao House office; no owner named); gamedriveafrica.com is a different firm. |
| Q4/40 | Magilani Safaris (O2a58e0cbc61e) | "Magilani Safaris" Arusha | Own site (403 to our fetcher), SafariBookings p5127 and SafariGo 1516 (read; no names), Facebook, TATO. |
| Q5/40 | Tanganyika Outdoor Safari Guide (Ofe4ce69838f9) | "Tanganyika Outdoor Safari" Arusha | YourAfricanSafari profile (read: operator text names a guide; 'owner' only in a guest review, not used), Facebook page, TripAdvisor, TATO. |
| Q6/40 | Peacock Tours & Safaris (O05b1aa5654c7) | "Peacock Tours & Safaris" Arusha | Facebook page; peacocksafaris.co.tz (certificate for another hostname; not read); TATO. |
| Q7/40 | Afrisafaris Tanzania Ltd (Od8eeaae30f56) | "Afrisafaris Tanzania" Arusha | Own-site pages (TLS failure), Facebook page; snippet adds an Italian number. No leader. |
| Q8/40 | Wildfrontiers (Chelete Adventures LTD) (O4a4028b8ef73) | "Chelete Adventures" Arusha | TATO and ZoomTanzania (read: seasonal Serengeti camps, company-named Gmail inbox). No leader. |
| Q9/40 | VETA Hotel and Tourism Training Institute (Oc1caf9256eba) | "VETA Hotel and Tourism Training Institute" Arusha | VETA's catalogue entry (read, PDF): institute's P.O. Box, phone and mailbox; VETA news page empty; NACTVET page renders in JavaScript. |
| Q10/40 | trekkingandsafariadventures (O281ef16a9906) | "Trekking and Safari Adventures" Moshi Tanzania | No result for this company. |
| Q11/40 | Gypsy Tours and Safaris Limited (O1a6d9ee7e6a9) | "Gypsy Tanzania Tours" Moshi | New own domain gypsytoursandsafaris.com (does not resolve), Facebook page, YourAfricanSafari (read; no names). |
| Q12/40 | RSA LIMITED (Of5f69168bba3) | "RSA Limited" OR "RSA Ltd" Moshi safari vehicle conversions | Own /our-company page (not requested after the site's 429), group site rsaafrica.roughtracksafrica.com (read; no names), Facebook. |
| Q13/40 | Aaa Express Adventure Ltd (Od7226547af1b) | "AAA Express Adventure" Arusha | SafariBookings p842 and SafariGo 64 (read; no names), Facebook, TripAdvisor. |
| Q14/40 | Discover Tanzania Safaris Ltd (O7005bdcebdc4) | "Discover Tanzania Safaris" Ltd | ZoomTanzania (read: same email and phone, Dar es Salaam); YourAfricanSafari profile removed; Facebook page behind a login wall. |
| Q15/40 | Shades of Africa Ltd (O4ecaa464f85b) | "Shades of Africa" safaris Tanzania Arusha | Only differently named or foreign firms (Shadows of Africa; Kenyan shadesofafricasafaris.com, read and rejected). |
| Q16/40 | Napenda Adventures Ltd (O5d0e339d06fe) | "Napenda Adventures" Tanzania safari | Own site (403), second own domain na.co.tz (not read, see Blocks), SafariBookings p6742 (read: Dar es Salaam address). Founders named by first name only. |
| Q17/40 | Twiga Craft Brewery (1001 Organic Limited) (Oe609962d6815) | "Twiga Brewery" OR "1001 Organic" Arusha craft brewery | Listings, Facebook and X; no leader. |
| Q18/40 | Wasim Trans Garage (O07e605285631) | "Wasim Trans Garage" Arusha | Social pages and listings; no leader. |
| Q19/40 | Nyamazela Trading Co (T) LTD (Ob961626c2241) | "Meserani Snake Park" OR "Nyamazela Trading" Arusha | The park's own site (read): operating company, park contact with phone, P.O. Box. |
| Q20/40 | All season bureau de change (O0e4a1216704e) | "All Season Bureau de Change" Arusha | City-guide snippet (Gmail inbox, Instagram); no leader. |
| Q21/40 | Meru Mountain Treks & Safari Ltd. (O03ba1bdd7ddd) | "Meru Mountain Treks" Arusha | merutreks.com ('Mount Meru Treks'; identity uncertain), TripAdvisor. No leader. |
| Q22/40 | Kili Star Tours (O00e287a17a2a) | "KiliStar Tours" OR "Kili Star Tours" Moshi | TripAdvisor snippet: reported permanently closed; a Facebook page. No route. |
| Q23/40 | Africa VIP Travel (Od907f03c37b2) | "Africa VIP Travel" Arusha | Own pages (500 when fetched) and SafariGo 160 (read): the director is named in the operator's own text. |
| Q24/40 | Top Of Africa Treks and Safaris LTD (O99340cb45985) | "Top of Africa Treks" Arusha | Only a TripAdvisor listing (Nkoanrua). |
| Q25/40 | Arusha Tours (O7651e0ebdffa) | "Arusha Tours" "Hidden Arusha Waterfall" coffee village tour | Own site (403) and tour-marketplace listings. |
| Q26/40 | Coastal Aviation Booking Office (Of9cd266cb634) | "Coastal Aviation" Moshi office Tanzania | Own site coastal.co.tz (read: CEO, national routes); snippet: Moshi office on the Arusha-Himo Road. |
| Q27/40 | Malaika Children's Friends (ORG_efa87f3ba9e9144a) | "Malaika Children's Friends" Arusha | Own pages (TLS failure), GlobalGiving (403), Facebook page. |
| Q28/40 | Upendo Children's Home (ORG_8e4c681307ba662f) | "Upendo Children's Home" Moshi | Volunteer-agency page and a US support charity's site (read; neither names the sister in charge); old blogs. |
| Q29/40 | Upendo Children's Home (parent body) | "Precious Blood" sisters Moshi Tanzania Upendo home | Parent body's Tanzania page (connection timed out). |
| Q30/40 | Kili Kids at Rainbow Ridge (ORG_a1f3972574c8fef3) | "Kili Kids" "Rainbow Ridge" Moshi | 2017 crowdfunding appeal (not used), 2014 blog; pointed to the Rainbow Ridge project. |
| Q31/40 | Kili Kids at Rainbow Ridge (parent) | "Kilimanjaro Permaculture Community" Rainbow Ridge Moshi | Communities Assist, the NGO that runs the home (read: email, Tanzania board, founder). |
| Q32/40 | Matumaini Child Care (ORG_6cab4cfa59fba51c) | "Matumaini Child Care" Moshi | Former partner's page (read: Rau Village, partnership ended 2012); a Facebook page (uncertain). |
| Q33/40 | Home Foundation (Rhotia) (ORG_359f116b8adf9907) | "Home Foundation" Rhotia Karatu Tanzania | Only a Dutch foundation for Rhotia Valley Children's Home (ANBI page 403); identity unclear. |
| Q34/40 | Huruma Centre Orphanage (ORG_ecda3e381f90c5d7) | "Huruma Centre" orphanage Iringa | Supporters' pages only (Iringa Diocese ministry, about 500 km away). |
| Q35/40 | Van Mo Safaris (Oc25f579eea3b), second search | "Van Mo Safaris" managing director OR founder Arusha | A 'Van Mo Group' page on vanmo.netlify.app (read) names the group's Managing Director; not recorded as a lead (see Warnings). |
| Q36/40 | Malaika Children's Friends, second search | "Malaika Children's Friends" founder OR director OR president | Own 'Our story' snippets name the director and the association's chairman (snippet-only). |
| Q37/40 | Tanganyika Outdoor Safari Guide, second search | "Tanganyika Outdoor Safari" owner OR founder OR director | Bare own domain also HTTP 500; no allowed source for a role. |
| Q38/40 | Game Drive Travel Africa Safari Agency, second search | "Travel Africa Safari Agency" founder OR director OR CEO Arusha | Facebook page only; no leader. |
| Q39/40 | Magilani Safaris, second search | "Magilani Safaris" founder OR fondatore OR director OR titolare | Own staff page exists (403 to our fetcher); snippets name no one. |
| Q40/40 | Afrisafaris Tanzania Ltd, second search | "AfriSafaris Tanzania" founder OR fondatore OR "chi siamo" OR director | Instagram and Facebook only; no leader. Allowance reached. |

Every query excluded LinkedIn and data-broker sites (ZoomInfo, RocketReach, Apollo, SignalHire, ContactOut, Lusha). No person's name was ever searched; queries used the organisation's name, its registered or trading name, and at most role words.

## Fetches without a search

- TATO directory: all 45 master members' portfolio pages were read (robots.txt allows). Pages for members listed only as `https://tatotz.org/` were found through TATO's category archives (Affiliate Members, NGO, Financial Services, Automotives) and letter tag pages (W, R); `members-list-2` renders in JavaScript.
- Completed with no search (18 organisations), from their own sites and TATO: Sadio Events, KCB Bank Tanzania (kcbbank.co.tz, found through the group site), Base Camp Tanzania, Wilmaar Insurance Brokers, Wildreality Safari, Fantacy Adventures (Manya Luxury Camps site), Pristine Trails, Rioba Safaris, Safari Avventura, Still Waters Safaris, Tanzania Roadside Expeditions, Vimat Safaris, CRDB Bank, RiverStone Safaris, United Tansania e.V., YAS Tanzania; and from TATO alone (own site blocked or gone): Shah Tours, Afric'Aventure.
- Own sites also read alongside a search: Van Mo Safaris (apex host; its leader search Q35 came later), Bald Eagle (apex host), AAA Express Adventure, Wasim Trans Garage, Twiga Brewery, RSA Africa (home page only), merutreks.com, coastal.co.tz, Meserani Snake Park, Communities Assist.
- Directory entries read: SafariBookings p7477, p4050 (+profile), p5127 (+profile), p842 (+profile), p6742 (+profile); SafariGo 368, 1516, 64, 160; YourAfricanSafari (Tanganyika Outdoor, Gypsy Tanzania Tours); ZoomTanzania (Chelete Adventures, Discover Tanzania Safaris); VETA catalogue (VHTTI).

## Blocked or unreadable sources

Blocks (recorded, not worked around):
- HTTP 403: magilani-safaris.com; www.shah-tours.com; www.napendaadventures.co.tz; www.arushatours.com; www.globalgiving.org (Malaika project page; its second project page was not requested); anbi.nl (Rhotia Valley Children's Home publication).
- HTTP 429: www.rsaafrica.com. The home page was read; the next three pages (contact-us, a product page, our-history) answered 429. The helper then still sent the second and third of those requests (2 s apart) before it was fixed to stop at the first 403 or 429; no further requests were sent to the site.
- Certificate failures: www.baldeaglesafaris.com (certificate for another hostname) and www.vanmosafaris.com (expired): in both cases the bare domain had a valid certificate and a robots.txt that allows reading, and the pages were read there (the coordinator may want to confirm this choice). www.afrisafaristanzania.com and the bare domain ('unable to get local issuer certificate'); malaika-childrenfriends.org, www and bare ('unable to get local issuer certificate'); allseasonbdc.co.tz, www and bare (expired); peacocksafaris.co.tz (certificate for another hostname; www does not resolve); new.shadesofafricasafaris.com (expired; unrelated Kenyan firm).
- Not read on purpose: www.na.co.tz, Napenda's second domain, because its main site blocks us (403) and reading another host of the same organisation would sidestep the block.

Unreadable (server or network), not blocks:
- HTTP 500: travelafricasafariagency.com (www and bare); tanganyikaoutdoorsafari.com (www and bare); topafricatrek.com; www.africaviptravel.com (home and about); discoverkenyasafaris.com/Travel_Tz.htm (linked from TATO).
- DNS failure (website gone): tz.kcbgroup.com; peacocksafaris.com (www and bare); www.trekkingandsafariadventures.com (and bare); gypsytanzaniatours.fun; gypsytoursandsafaris.com (www and bare; found by Q11); merutreks.co.tz (www and bare).
- Connection timed out: www.missionarysisterspreciousblood.org (Tanzania page).
- Empty page (HTTP 200, no body): veta.go.tz news item on VHTTI.
- JavaScript only: nactvet.go.tz institute page; tatotz.org/members-list-2.
- Domain now unrelated to the organisation: africaventure.net shows a French travel-guide blog with template placeholders; nothing used, and its email is not recorded as a route.
- Placeholder theme pages: wib.co.tz team, team-carousel, about and contact pages (theme names, a US address, a +92 number, Envato social links); only the genuine home page was used.

## robots.txt disallows

- www.openstreetmap.org: robots.txt disallows `/node/`, `/way/` and `/api/`. Not read: node 4326987993 (trekkingandsafariadventures), node 2534727404 (Kili Star Tours), node 4809822821 (Africa VIP Travel), node 4986137722 (Meru Mountain Treks), node 7161464785 (Top Of Africa Treks), node 13572133101 (Arusha Tours), way 247016485 (Coastal Aviation Booking Office). Their tags are already in the repository's Overpass collection (`osm_contacts_2026-09-23.json`) and in the master; each record's notes say so.

No page was read from a site whose robots.txt could not be fetched, so there are no 'robots.txt unreachable' findings.

## Warnings for review

- Possible closure: Kili Star Tours (TripAdvisor snippet: permanently closed); trekkingandsafariadventures (website gone, no web presence); Afric'Aventure (domain lost to an unrelated blog); Gypsy Tours (both domains gone); Peacock Tours (peacocksafaris.com gone); Tanzania Outfitter & Safaris (email domain shows an empty directory listing); Matumaini Child Care (no evidence after 2012); Discover Tanzania Safaris and Shades of Africa (old TATO entries only).
- Location to check or outside the area: Sadio Events, Afric'Aventure, Wilmaar, Fantacy Adventures (Dar es Salaam / Serengeti camp), Napenda (Dar es Salaam), CRDB and YAS (Dar es Salaam head offices), Discover Tanzania Safaris and Shades of Africa (Dar es Salaam P.O. Box but Arusha-code landlines), United Tansania (Lake Eyasi, Karatu), Home Foundation (Rhotia, about 110 km), Huruma Centre (Iringa, about 500 km). Wildreality Safari: the master and TATO say Dar es Salaam, but its own site says it is based in Arusha.
- Segment to check (filed as tour operators): Sadio Events (events), RSA Limited (vehicle conversions), Wilmaar (insurance broker), Twiga Brewery (brewery), CRDB (bank), Wasim Trans Garage (garage), United Tansania (NGO), Nyamazela Trading (snake park), YAS (telecoms and mobile money), All Season (bureau de change).
- Possible duplicates (twin records in the master): KCB / Oe724c258de33; Kili Star Tours / Ode3e3ade9452; CRDB Bank Plc / O9a7ec2dc8754; Base Camp Tanzania / O519360259232; Africa VIP Travel / Od19d8a210967; Meru Mountain Treks / O0bcf10d5e11c; Top Of Africa Treks / O7fc518549456, Shah Tours / Oacdd2049005a and trekkingandsafariadventures / O3b8a3e4d2f96 (all three in wave 5 slice A).
- Identity uncertain: Fantacy Adventures (the Manya Luxury Camps site never names the company; the link is TATO's mailboxes); Meru Mountain Treks (merutreks.com names itself differently and links another company's social pages); Kili Star Tours and Matumaini Child Care (Facebook pages only); Home Foundation (Rhotia) (only a similarly placed Dutch foundation found); trekkingandsafariadventures (nothing found).
- Candidate lead not recorded: Van Mo Safaris' parent 'Van Mo Group' page (vanmo.netlify.app, on a hosting-platform address that the safari company's site does not link to) names the group's Managing Director; the coordinator may confirm and add him.
- Named contact without a leadership title: Nyamazela Trading's 'Park Contact' (recorded with the phone the park's contact page gives for her); status partial.
- Government-owned institute: VETA Hotel and Tourism Training Institute is addressed by office title (Principal); no official was searched for or named.

## Data-protection decisions

- Not recorded: a role taken from a guest review (Tanganyika Outdoor Safari's 'owner'); founders or co-owners published by first name only (Napenda, Pristine Trails); family relationships (Base Camp, Pristine Trails, Still Waters, Napenda, Malaika snippet); biographies and background (Van Mo team, Afric'Aventure, Wildreality team, Coastal Air CEO, Africa VIP, Pristine Trails); client testimonials (Sadio Events); theme placeholder people (Wilmaar); another organisation's board (the US charity supporting Upendo) and a visitor's note naming a director (Huruma supporters' site); the 2007 blog's named contact and personal mobile (Matumaini).
- Personal-domain inboxes named after a person are not company routes: simonbabuu@gmail.com (trekkingandsafariadventures, from OSM) and Roadside Expeditions' Barcelona contact inbox. Inboxes named after the organisation are kept (cheleteadventures@gmail.com, meseranisnakepark@gmail.com, unitedtansania@gmail.com, info.vhtti@gmail.com, allseasonbdc@gmail.com snippet-only).
- Named company mailboxes without a stated role (for example kibwana.issa@, raphael@, zaakir.siddik@, rngusaru@) are recorded as company emails of type `named`, never attached to a person.
- Welfare records hold only the organisation's routes and the adults who lead it. Nothing about children was recorded, and pages about the children (for example the Kili Kids pages on the Communities Assist site) were not opened.
- Every recorded person carries `pdpa_risk: medium` (named person in a professional role, or a named contact with an organisation-published mobile).

## Organisations not reached

None: all 51 organisations have a record.

Gaps left for a later pass (leader still unnamed): Tanzania Outfitter & Safaris, Bald Eagle, Game Drive Travel Africa, Magilani, Tanganyika Outdoor Safari, Peacock, Afrisafaris, Wildfrontiers, VHTTI (office title only), Gypsy, RSA, Discover Tanzania, Shades of Africa, Wilmaar, AAA Express, Fantacy, Napenda, Safari Avventura, Twiga, Wasim, All Season, Meru Mountain Treks, Top Of Africa, Arusha Tours, Upendo, Huruma; routes still missing: Kili Star Tours, Matumaini, Home Foundation (Rhotia), Huruma.

Sites a browser could check (blocked or unreadable here): magilani-safaris.com (staff page /en/about-us/), www.shah-tours.com, napendaadventures.co.tz and www.na.co.tz, www.arushatours.com, www.afrisafaristanzania.com, www.malaika-childrenfriends.org (our-story, contacts), allseasonbdc.co.tz, peacocksafaris.co.tz, www.rsaafrica.com/our-company (after the 429), GlobalGiving's Malaika pages, travelafricasafariagency.com, tanganyikaoutdoorsafari.com, topafricatrek.com, www.africaviptravel.com, www.missionarysisterspreciousblood.org (Upendo's parent body). OpenStreetMap node and way pages are covered by the Overpass collection.

## Stopping rule

The search allowance was reached at Q40/40; no search was refused by the session cap. After that only URLs already in hand were fetched. No one was contacted, and no file outside the output, this log and the scratch folder was changed.
