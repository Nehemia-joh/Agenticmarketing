# Coverage log: wave 2, master employers (2026-09-23)

Slice: `runtime/contacts/slices/wave2_master_employers.json`: 60 records, which are 49 distinct organisations because 11 organisations appear twice under the same OpenStreetMap element. The slice holds travel agencies, safari operators, NGO and company offices, and a few hotels.
Search allowance: 14 WebSearch calls, all used (Q1/14 to Q14/14). After Q14 only URLs already in hand were fetched.
Output: `data/raw/contact-research/search_wave2_master_employers_2026-09-23.jsonl` (34 records). Scratch: `runtime/contacts/agents/wave2_master_employers/`.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 60 (49 distinct organisations) |
| Researched (one JSONL line each) | 34 (28 distinct organisations) |
| found | 19 |
| partial | 7 |
| not_found | 5 |
| blocked | 3 |
| Not reached (no line written) | 26 (21 distinct organisations) |
| Identity uncertain | 2 (Dhariwal Trading Co, Woodtech 2008) |
| WebSearch calls used | 14 / 14 |
| Records with a new email or phone | 19 (15 distinct organisations) |
| Named contact leads | 21 distinct people (31 entries counting duplicate records), all `medium` |
| Role-desk entries | 4 (1 `low`, 3 `medium` because the desk line is a mobile) |

Status rules:
- `found`: identity confirmed, and at least one email or phone read on a fetched page. The page is the organisation's own site, its TATO profile or an operator directory.
- `partial`: some profile data (address, social page or website) but no fetched email or phone.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the organisation's own source, or the only source identified, refused automated reading.

A `not_found` or `blocked` record that holds only an address or a social page would be ignored by `build_contact_profiles.py`, so location-only records are `partial`.

Person filter: `contact_lib.clean_person` will drop three of the 21 named people. Their published roles match neither its decision list nor its admin/HR list: Milcah Masaba (Office Manager) and Shakir Omari (Office Coordinator) at Duma Explorer, and Radhia Chembera (Office Manager, Tanzania) at Kibo Slopes. They are recorded exactly as published, so a person can decide whether to keep them.

## Searches

| # | Query | Organisation(s) | Outcome |
|---|---|---|---|
| Q1/14 | "Oikos East Africa" Arusha | Oikos East Africa | Found own site oikosea.co.tz: contacts page (email, P.O. Box, Haile Selassie Road) and home page (phone); Facebook page from results |
| Q2/14 | "Nale Moru" Arusha | Nale Moru experiential travel (2 records) | Found nalemoru.com: about page with address in Kiranyi, two phones and Founder/Director Robert Chekwaze; socials on home page |
| Q3/14 | "ADRA Tanzania" Arusha contact | Adventist Development Agency | Found adratanzania.org: office at Usa River, P.O. Box 360, phones, Ag. Country Director; Facebook "ADRA in Tanzania \| Usa River" |
| Q4/14 | "Kilimanjaro Bliss Safaris" Arusha | Kilimanjaro Bliss Safaris (2 records) | Found kilimanjarobliss.com (contact and staff pages: emails, phones, Kaloleni office, three director-founders). The SafariBookings profile, fetched, gave P.O. Box 12110 and +255 782 156 128 |
| Q5/14 | "Tanganyika Farmers Association" Arusha | Tanganyika Farmers Association | Found tfa.co.tz contact page: MD office mailbox, sales and property desks, P.O. Box 3010; Facebook and LinkedIn company pages from results |
| Q6/14 | "Dhariwal Trading" Arusha | Dhariwal Trading Co | Only lead is a SIDO register profile; sido.go.tz fails TLS (blocked). Other results were Indian namesakes; an Instagram account could not be tied to Arusha |
| Q7/14 | "Economists (T) Investment Group" Arusha | Economists (T) Investment Group | Nothing about the company; OSM data used instead (industrial building, Kikwakwaru "B") |
| Q8/14 | "United African American Community Center" Arusha | UAACC | Now "United African Alliance Community Center". Wikidata item gave the official site uaacc.net (phone, Imbaseni location, founder); Facebook page from results |
| Q9/14 | "Woodtech 2008" Arusha | Woodtech 2008 (T) Ltd Arusha | Nothing (Woodtech Africa trade-fair pages, Nairobi) |
| Q10/14 | "Kigongoni Lodge" Arusha | Kigongoni Lodge | No official site (kigongoni.net is lost, see below); booking directories only, no phone or email |
| Q11/14 | "Meru Hospital" Tengeru | Meru Hospital | Results all describe the government Meru District Hospital at Tengeru (snippets); no phone or email. The volunteer page is under maintenance |
| Q12/14 | "Moyoni Airport Lodge" | Moyoni Airport Lodge | Facebook page and booking directories only; operator page (Wildlands Camps and Lodges) 404, operator site blank |
| Q13/14 | "Canossa Spirituality Centre" Arusha | Canossa Spirituality Centre | AMECEA article (fetched) places it in Njiro, run by the Canossian Sisters, host of the ICOF programme; no contacts |
| Q14/14 | "Arusha Crown Hotel" Arusha | Arusha Crown Hotel | Directories only (Cvent, TripAdvisor, Kayak, Trip.com, AfricaGuide). No phone or email; AfricaGuide is behind a Cloudflare challenge |

## Fetches without a search

| Source | Organisation(s) | Outcome |
|---|---|---|
| Crawler page cache for www.tzcrc.org (page source served 2026-09-23) | Tanzania Conservation Resource Centre | info@tzcrc.org in the page source. The page renders in JavaScript, so WebFetch saw only the shell |
| www.snvworld.org, then snv.org/country/tanzania | SNV | snvworld.org fails TLS (certificate for *.netlify.app). snv.org gave the country office email, phone and P.O. Box, and five named staff (three recorded) |
| www.arushacrownhotel.com | Arusha Crown Hotel | HTTP 401 (blocked) |
| ndorolodge.com | Ndoro Lodge | HTTP 403 (blocked) |
| lemutakhakisafaris.co.tz | Lemuta & Khaki Safaris | DNS failure |
| www.moyoni-airport-lodge.com | Moyoni Airport Lodge | DNS failure |
| www.bokeradventure.com/boker, /terms, /privacy | Boker Adventures (2 records) | Itinerary page on the Pin Destinations platform; only the platform's shared inbox |
| tatotz.org portfolio pages: access-2-tanzania, lemuta-khaki-safaris, serengeti-wakanda-tours-safaris, portfolio-kibo-slopes-t-ltd, monkey-adventutres, zara-tanzania-adventures, roy-safaris-ltd | 7 operators | Member profiles. Addresses, phones and emails where listed; Monkey Adventures names two founder-directors |
| tatotz.org sitemap (listed in robots.txt; portfolio-sitemap1-3.xml, 522 profile URLs) | Operators in the slice | Matched Monkey Adventures, Zara and Roy only; no TATO profile for Nale Moru, Kilimanjaro Bliss, Duma, Gladys, Kessy Brothers, Tintin, Enosa, Kili Star, JM Tours or Boker |
| www.dumaexplorer.com (home, contact-us, about-us) | Duma Explorers (2 records) | Email, Tanzania and US phones, owner, Tanzania branch owner, office manager and coordinator |
| roysafaris.com, which redirects to roysafaris.co.tz (home, contact-us, why-travel page) | Roy Safaris | Email, office and WhatsApp lines, P.O. Box 50, 2 Serengeti Road, socials; no named managers |
| zaratours.com, which redirects to zaratanzaniaadventures.com (home, contact-us, about-zara, ceo-story) | Zara Tours | Emails, phones, Tembo Road (Pasua, Moshi), Founder and CEO |
| serengetiwakandatours.com (home, team) | Serengeti Wakanda | Wakanda House, Njiro Road; phone, email, Instagram. Team page lists guides and chefs only |
| www.gladysadventure.com (home, companyinfo.html) | Gladys Adventure & Safaris (2 records) | 224 Lema Road, Moshi; emails, phone, CEO and founder |
| kiboslopes.com (home, staff, contact) | Portfolio Kibo Slopes T Ltd | Arusha office (Sakina, Kiranyi Road), Office Manager (Tanzania), group directors |
| monkey.travel/en/ and /en/usd/contact | Monkey Adventures | Moshi, Arusha and Nairobi offices; phones, email, socials |
| en.wikipedia.org/wiki/Fastjet_Tanzania | Fastjet ticket office Shuttlebus | Airline ceased operations on 25 November 2019; liquidator appointed on 21 December 2019 |
| www.precisionairtz.com | Precision Air | JavaScript shell only; nothing read (organisation left as not reached) |
| Overpass API, one exact-name query (overpass-api.de, 2026-09-23) | 17 OSM names from the slice | Coordinates and tags for 12 elements (see "Not reached"); Oikos house number; Meru Hospital polygon; Economists address |
| www.wikidata.org Q96619659 | UAACC | Official website www.uaacc.net |

Pacing: at least 2 seconds between requests to one host (at least 6 seconds on monkey.travel, which sets `Crawl-delay: 5`). robots.txt was read before any page beyond a home page. The Squarespace robots files on dumaexplorer.com and tfa.co.tz list AI crawlers in the shared `*` group, which only disallows service paths, so content pages are allowed. snv.org allows `*`, and safaribookings.com allows its `/p` operator pages.

## Blocked or unreadable sites

- **Blocked (recorded, not worked around):**
  - www.arushacrownhotel.com: HTTP 401
  - ndorolodge.com: HTTP 403
  - www.snvworld.org: TLS certificate mismatch (certificate for *.netlify.app)
  - sido.go.tz/en/profile-main/1680: TLS certificate mismatch; the certificate names www.sido.go.tz, and that host was not tried
  - www.africaguide.com: Cloudflare challenge (HTTP 403)
- **Lost or dead websites:**
  - kigongoni.net now serves unrelated content: a Chinese "website under construction" placeholder and a DedeCMS robots file. Nothing was used.
  - lemutakhakisafaris.co.tz and www.moyoni-airport-lodge.com do not resolve (DNS).
  - wildlandscampsandlodges.com/moyoni-airport-lodge/ returns 404, and the operator's site is a blank default WordPress install (first post dated 16 Sep 2026).
- **Unreadable or empty:**
  - www.tzcrc.org and www.precisionairtz.com render in JavaScript.
  - www.uaacc.net/contact returns 404.
  - electiveandvolunteers.com shows "Website Under Maintenance".
  - The TATO members list filters in JavaScript; the sitemap was used instead.
- **Email protection:** the visible email on adratanzania.org is hidden by Cloudflare email protection. It was not decoded; info@adratanzania.org was taken from the link's plain-text `aria-label` in the served HTML.

## Warnings

- **Closed:** Fastjet ticket office Shuttlebus (O8e55c124984b). Fastjet Tanzania ceased operations on 25 November 2019 and is in liquidation.
- **Lost or hijacked domains:**
  - kigongoni.net (Kigongoni Lodge): unrelated content.
  - lemutakhakisafaris.co.tz (Lemuta & Khaki Safaris): does not resolve.
  - moyoni-airport-lodge.com (Moyoni Airport Lodge): does not resolve, and the operator's site is blank.
  - www.snvworld.org (SNV): fails TLS. SNV now uses snv.org.
- **Moved websites:**
  - Zara Tours: zaratours.com redirects to zaratanzaniaadventures.com.
  - Roy Safaris: roysafaris.com redirects to roysafaris.co.tz.
- **Duplicate records**, each pair researched once and cross-referenced in notes:
  - Nale Moru: O2f6810861cd1 and Of31aaf82637c
  - Access 2 Tanzania: Of266669dd470 and O31b73e1bb936
  - Kilimanjaro Bliss: O093920d51418 and O4f3f8078260d
  - Duma Explorers: O8d12f5792f73 and O53a36854f8df
  - Boker Adventures: O7136ae38625d and Odade2f68937f
  - Gladys Adventure & Safaris: O629d1111168f and O567804e1042f
  - Not reached, same OSM element in each pair: Tintintours, Summit 2 Sand Safaris, Kessy Brothers, Enosa Expedition and Kili Star Tours
- **Out of area:** none.
  - The Moshi records (Boker, Gladys, Zara, Monkey and the unreached Moshi operators) are in Kilimanjaro Region, about 22–23 km from Boma Ng'ombe.
  - Kibo Slopes' group head office is in Nairobi, but this record is its Arusha subsidiary. Duma Explorer (San Francisco) and Kilimanjaro Bliss (Cowichan Bay, Canada) also have offices abroad; both have Tanzanian offices in Arusha.
- **Names that differ from the master:**
  - "Zara Tours" trades as Zara Tanzania Adventures.
  - "United African American Community Center" is now the United African Alliance Community Center.
  - "Adventist Development Agency" is ADRA Tanzania (Usa River).
  - "Portfolio Kibo Slopes T Ltd" is KIBO SLOPES T LIMITED; "Portfolio" comes from the TATO URL.
  - "Meru Hospital" appears to be the Meru District Hospital, Tengeru. That rests on snippets and the OSM polygon.
- **Master data to review:**
  - The website value "DMC/MAIN" for Access 2 Tanzania (Of266669dd470) is a TATO category, not a website.
  - Kibo Slopes (Ob5939181e661) is located at Sakina, Kiranyi Road, Arusha, although the master has it unlocated.
  - Current addresses differ from OSM: Nale Moru (Kiranyi, not near Kijenge), Gladys (224 Lema Road, not Hill Street), Zara (Tembo Road, Pasua, not Ghala Road).
  - Oikos: the site says Haile Selassie Road n 31; OSM says 165 Haille Sellassie.

## Data-protection decisions

- UAACC's only published email is a personal-domain (Yahoo) inbox named after a person. It was not recorded. The site also links two personal Facebook profiles, which were not recorded; the organisation's own Facebook page (from Q8) was recorded instead.
- ADRA Tanzania's LinkedIn link is a personal-profile-type (`/in/`) page. It was not recorded.
- Duma Explorer's owner has a named email in the site-builder's hidden settings JSON (`contactEmail`). It is not published for contact, so it was not recorded.
- Biographies on the Duma, Kilimanjaro Bliss, Zara, Gladys and UAACC pages were not recorded, and neither was the family relationship stated on the Gladys page or any founder history. Only names and published titles were kept.
- Not recorded:
  - Guides and chefs on the Serengeti Wakanda team page.
  - Kibo Slopes staff in Kenya and Uganda.
  - The Nale Moru co-founder, who is named by first name only.
  - People without a published role on the UAACC site.
  - ICOF programme officers named in the Canossa sources.
  - SNV's two sector leaders (programme roles).
- Gladys Adventure's gmail inbox is named after the company, so it was kept as a general inbox.

## Organisations not reached (no JSONL line)

The search budget was spent on the nearest organisations that had an identifiable name and no route at all. The records below have no website of their own, so each would need a search. Where the Overpass lookup found the OSM element, its id and coordinates are given; the master has neither for these.

| Organisation | organisation_id | Distance | Why not reached | OSM element found on 2026-09-23 |
|---|---|---|---|---|
| Mazda | O615ce17408df | 1.6 km (Usa River) | Brand name only; cannot be tied to a company without a search | node/6244490885, -3.36812, 36.87251 (office=company, Usa River town) |
| Tigo Store | O93c8c9fb672c | 2.1 km | Retail branch of a national chain (Tigo, now Yas); corporate routes only | node/4322760097, -3.36726, 36.68463 |
| Isamilo Express booking office | O8b531d7b107c | 2.1 km | Bus-company booking office; budget | node/6081188785, -3.36718, 36.68261 |
| Henkel | O4c8db1a3c7f6 | 2.2 km | Brand name only | node/6243895191, -3.37306, 36.69226 |
| VODACOM SERVICE CENTER | O2d14bb8409eb | 2.2 km | Retail branch of a national chain | node/9019419886, -3.37304, 36.69243 |
| Chemical Industry Ltd | O2310c00d7b59 | 3.4 km | Generic name | node/8550559318, -3.40097, 36.71293 |
| Israel community office | O822d982b3f46 | 3.8 km | Unclear what it is | node/6043713486, -3.37652, 36.74609 |
| PAG Church Njiro | Oa8a5a32fa9fe | 4.4 km | Church office; budget | node/9220891880, -3.40842, 36.70119 |
| Tintintours (2 records) | O66a49150a30a, O6c7f7cdd682b | 22.6 km (Moshi) | Budget | node/2516074740 |
| Summit 2 Sand Safaris (2 records) | O923da4a684cd, O9d6f9263adfd | 22.7 km (Moshi) | Budget | node/6782817087 |
| Kessy Brothers (2 records) | O17bd2f803731, O9e7e9c05bdc1 | 23.0 km (Moshi) | Budget | way/246423702 |
| Enosa Expedition (2 records) | Odb7e9aa1b559, O2ea7d99baa8a | 23.3 km (Moshi) | Budget | way/696402131 |
| Kili Star Tours (2 records) | Ode3e3ade9452, O00e287a17a2a | 23.4 km (Moshi) | Budget | node/2534727404 |
| Precision Air | O6677eba8a8ed | none recorded (Moshi) | Airline sales office; home page is a JavaScript shell | node/894160585 |
| Dar Express Booking Office | O4937b79f7118 | none recorded (Arusha) | Bus booking office; budget | node/2551998758 |
| Mtey Booking Office | Ob15b6a1a175e | none recorded (Arusha) | Bus booking office; budget | node/2552014411 |
| Lim Safaris Booking Office | O4816d5a5693d | none recorded (Moshi) | Bus booking office; budget | node/2552076053 |
| JM Tours | O09923d262264 | none recorded (Arusha) | Budget | node/3147591945 |
| Basecamp Tanzania | O519360259232 | none recorded (Arusha) | Budget; the TATO sitemap has "Base Camp Site Ltd", but the name does not match | node/4295739592 |
| Usa River Booking Office | Of38ed0efb017 | none recorded (Usa River) | Bus booking office; budget | node/6244370986 |
| Kkikalora Saccos | O225198c6cffe | none recorded | Savings cooperative; budget | node/7487189045 |

## Stopping rule and next steps

The slice's stopping rule was not met: 26 records (21 organisations) were not reached because the 14-search allowance was spent.

Suggested priorities for a later wave, one search each:
1. Kessy Brothers, Tintintours, Summit 2 Sand Safaris, Enosa Expedition and Kili Star Tours. These are Moshi operators, and each search covers two records.
2. JM Tours and Basecamp Tanzania (Arusha agencies).
3. Isamilo Express, Dar Express and Mtey (bus booking offices, if still wanted).
4. Precision Air's Moshi office.

Four organisations (six records) were researched from their known sources without a search and still have no email or phone. Each would benefit from one search:
- Access 2 Tanzania (2 records)
- Lemuta & Khaki Safaris
- Boker Adventures (2 records)
- Ndoro Lodge, whose own site is blocked

`plan_contact_research.py` treats any line in these files as searched for this date, so re-queue them by hand if wanted.
