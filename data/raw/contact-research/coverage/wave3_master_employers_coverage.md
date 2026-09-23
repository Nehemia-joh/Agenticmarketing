# Coverage log: wave 3, master employers (2026-09-23)

Slice: `runtime/contacts/slices/wave3_master_employers.json`: 37 records, which are 30 distinct organisations because 7 organisations appear twice under the same OpenStreetMap element. The slice holds travel agencies, safari operators, bus booking offices, company offices, dispensaries and health centres, bank branches and a savings cooperative.
Search allowance: 32 WebSearch calls, all used (Q1/32 to Q32/32). No search was refused by the session cap. After Q32 only URLs already in hand were fetched.
Output: `data/raw/contact-research/search_wave3_master_employers_2026-09-23.jsonl` (37 records). Scratch: `runtime/contacts/agents/wave3_master_employers/`.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 37 (30 distinct organisations) |
| Researched (one JSONL line each) | 37 (30 organisations) |
| found | 18 records (13 organisations) |
| partial | 14 records (12 organisations) |
| not_found | 5 records (5 organisations) |
| blocked | 0 (Kessy Brothers was blocked on its own site, then found through a directory; all blocks are listed below) |
| Not reached (no line written) | 0 |
| Identity uncertain | 6 (Mazda, Oloirien Community Dispensary, Chemical Industry Ltd, Israel community office, PAG Church Njiro, Usa River Booking Office) |
| WebSearch calls used | 32 / 32 |
| Records with a new email or phone | 27 (25 read on fetched pages; the 2 Boker Adventures records are snippet-only) |
| Organisations with a fetched email or phone | 20 (19 with confirmed identity; 6 of these have only head-office or national routes: Ecobank, KCB, Tigo/Yas, Vodacom, Dar Express, Mtei) |
| Named contact leads | 19 distinct people (27 entries counting twin records), all `medium`; 2 are snippet-only |
| Role-desk entries | 0 |

Status rules (as in wave 2):
- `found`: identity confirmed, and at least one email or phone read on a fetched page (the organisation's own site, an official register, or a business or operator directory).
- `partial`: some profile data, but contacts only from snippets, head-office or national routes only, location only, or identity uncertain.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the organisation's own source, or the only source identified, refused automated reading.

Person filter: `contact_lib.clean_person` will drop 4 of the 19 people because their published roles carry no role word. They are the Bank of Tanzania register's "contact person" for Ecobank Tanzania (Charles Asiedu) and KCB Bank Tanzania (Cosmas Kimario), and Base Camp Tanzania's Achmed Phillips and Zainab Phillips, whose site gives no job titles. A third-party bank list names the two bankers as managing directors, but it is not an allowed source, so the roles stay as the register publishes them. All four are recorded exactly as published so that a person can decide whether to keep them.

## Searches

| # | Query | Organisation(s) | Outcome |
|---|---|---|---|
| Q1/32 | "Mazda" "Usa River" Arusha | Mazda | Mazda USA pages and a Usa River article only; no Tanzanian company behind the OSM name |
| Q2/32 | "Oloirien" dispensary Arusha | Oloirien Community Dispensary | TMDA northern-zone dispensary list (fetched): "OLORIENI COMMUNITY, MOIVOI, faith-based"; no phone. The HFRS PDF 113631-6 in the results is an unrelated laboratory |
| Q3/32 | "Ecobank" Arusha branch Tanzania | Ecobank | Association of Tanzania Employers member page (fetched): head office at Quality Plaza, Dar es Salaam, and 5 branches including Arusha. Then the Bank of Tanzania register (no search) gave the head-office phone, email, P.O. Box and contact person |
| Q4/32 | "Old Arusha" health centre Arusha | Old Arusha Health Center | "Old Arusha Clinic": Facebook page and Medpages listings (robots.txt disallows Medpages). Tied to the facility after Q14 |
| Q5/32 | "Isamilo Express" bus Arusha | Isamilo Express booking office | Company booking site isamilo.co.tz (fetched): per-town office lines, including Arusha. isamilo.com blocked (Vercel bot check) |
| Q6/32 | "Henkel" Arusha Tanzania office | Henkel | Henkel Polymer Co. Ltd: Tanzania Pages verified listing (fetched; Dodoma Road, office phone, Facebook page as website) |
| Q7/32 | "Vodacom" shop Arusha contact Tanzania | VODACOM SERVICE CENTER | National Commercial Directory listing (fetched): customer-care line and inbox, head-office P.O. Box. vodacom.co.tz is a JavaScript app. An unclaimed Finder Africa shop listing was not used |
| Q8/32 | "Access 2 Tanzania" Arusha | Access 2 Tanzania (2 records) | Own site access2tanzania.com (fetched home and owners-and-staff page): email, Tanzania line, P.O. Box, three owner-directors and two Arusha managers |
| Q9/32 | "Lemuta" Khaki Safaris Arusha | Lemuta & Khaki Safaris | Only TATO directory pages and generic safari listings; no trace of the company elsewhere |
| Q10/32 | "Ndoro Lodge" Usa River Arusha | Ndoro Lodge | Booking and review listings only ("Ndoro Lorge", opposite Tumaini University Makumira) |
| Q11/32 | "Chemical Industry Ltd" Arusha | Chemical Industry Ltd | Only Arusha match: Osho Chemical Industries' Tanzania office (group contact page fetched: Themi/Njiro address, phones, email). Identity uncertain |
| Q12/32 | "Israel community" office Arusha Tanzania | Israel community office | Articles about Arusha's Jewish religious community; nothing tied to the OSM node; no names recorded |
| Q13/32 | "PAG" Njiro church Arusha Pentecostal Assemblies of God | PAG Church Njiro | Pentecostal Assemblies of God bodies in Kenya, Uganda and the USA only |
| Q14/32 | "Canossa" dispensary Arusha Njiro | Canossa Dispensary (and Old Arusha) | Jubilee Insurance public provider panel PDF (fetched): Canossa dispensary inbox and phone; Old Arusha Dispensary at 6 Old Moshi Road with inbox and two phones |
| Q15/32 | "Boker Adventures" Moshi Tanzania | Boker Adventures (2 records) | Former company pages on bokeradventure.com (now 404; the domain serves a platform app): founder name and NSSF Building address from snippets; Facebook and TripAdvisor URLs |
| Q16/32 | "Tintin Tours" Moshi Tanzania | Tintintours (2 records) | Tanzania Pages verified listing (fetched; last updated 2015): three phones. SafariBookings (fetched): Viwanda Street, 10-20 employees. RealAdventures (fetched): host contact. tintintours.com is for sale |
| Q17/32 | "Summit 2 Sand Safaris" Moshi | Summit 2 Sand Safaris (2 records) | Own site (fetched contact and MD pages): P.O. Box 7393 Moshi, general inbox, Managing Director with work inbox and mobile |
| Q18/32 | "Kessy Brothers" Moshi | Kessy Brothers (2 records) | Own site blocked (Cloudflare challenge); SafariBookings profile (fetched) has no address or phone |
| Q19/32 | "Enosa Expedition" Moshi | Enosa Expedition (2 records) | Own site (www host fetched): inbox and phone; SafariBookings (fetched): P.O. Box 8294 Moshi, 20-50 employees |
| Q20/32 | "Kili Star Tours" Moshi | Kili Star Tours (2 records) | Only a TripAdvisor listing ("KiliStar Tours and Safaris - Day Tours"), which answered HTTP 403 |
| Q21/32 | "Dar Express" bus Arusha booking office contact | Dar Express Booking Office | 123Tanzania listing (fetched): head-office P.O. Box, Dar es Salaam landlines, two mobiles. The company booking site shows only the platform's support line |
| Q22/32 | "Mtei" bus Arusha booking office | Mtey Booking Office | Mtei Express booking site (fetched): head-office line and lines for Dar es Salaam, Moshi, Kateshi, Kahama; none for Arusha |
| Q23/32 | "Lim Safaris" bus Moshi | Lim Safaris Booking Office | Lim Safari booking site (fetched): two head-office lines (head office in Moshi) |
| Q24/32 | "JM Tours" Arusha Tanzania | JM Tours | Own site jmtours.com (fetched contact and about pages): sales line, inbox, P.O. Box 392 and Plot 15 Olorien, five Directors |
| Q25/32 | "Basecamp Tanzania" Arusha | Basecamp Tanzania | Own site basecamptanzania.com (fetched contact and about pages): #14 Middleton Road, P.O. Box 568, two phones, management inbox, two named people |
| Q26/32 | "Usa River" bus booking office Arusha Moshi | Usa River Booking Office | Shuttle and coach booking sites only; nothing names the operator |
| Q27/32 | "Kikalora" SACCOS Moshi Kilimanjaro | Kkikalora Saccos | Tanzania Cooperative Development Commission licensed-SACCOS lists: "Kikalora SACCOS Ltd, P.O. Box 931 Moshi" (snippet); the PDF answered HTTP 403 |
| Q28/32 | "Olorieni Community" dispensary Arusha | Oloirien Community Dispensary | Ward pages show "Olorieni" is also an Arusha District Council ward; a directory page timed out; no register entry. Identity downgraded to uncertain |
| Q29/32 | "Ndoro Lodge" Makumira contact phone email | Ndoro Lodge | A booking mini-site's contact page failed the TLS handshake; nothing else new |
| Q30/32 | "Boker Adventure" Moshi contact phone email | Boker Adventures (2 records) | Snippets of the former contact pages: inbox and phone/WhatsApp line (page now 404; recorded as fetched: false) |
| Q31/32 | "Kessy Brothers Tours" Moshi phone email office | Kessy Brothers (2 records) | Go Africa Online yellow-pages listing (fetched; unclaimed): Old Moshi Road office opposite KNCU/Coffee Tree Hotel, P.O. Box 7502, two mobiles. The older domain kessybrotherstours.co.tz does not resolve |
| Q32/32 | "KiliStar Tours and Safaris" Moshi | Kili Star Tours (2 records) | The same TripAdvisor listing and differently named companies only |

## Fetches without a search

| Source | Organisation(s) | Outcome |
|---|---|---|
| www.bot.go.tz/BankSupervision/Institutions (Bank of Tanzania register of supervised institutions) | Ecobank, KCB | Head-office phone, email, P.O. Box and contact person for both banks |
| kcbgroup.com (home, /contacts, /contact-us, /location) | KCB | Kenya investor contacts only; every Tanzania link points to tz.kcbgroup.com, which failed DNS in slice C and was not re-fetched |
| www.tigo.co.tz, which redirects to yas.co.tz (home, /consumer/assistance/, /about/, /store-locator/, sitemaps) | Tigo Store | Tigo Tanzania is now Yas Tanzania; WhatsApp line, short code 100, socials, the CEO's signed message. The store list loads by script and was not called |
| vodacom.co.tz (home, main script, /sitemap.xml) and www.vodacom.com/contact-us.php | VODACOM SERVICE CENTER | JavaScript app with no contact text in its script; group page is South African only |
| www.precisionairtz.com (home, robots, sitemap, main script) | Precision Air | The site is a JavaScript app; its own script holds the /contact office list (Moshi office at KNCU Building, Old Moshi Road, with office and mobile lines) and the /Introduction message signed by the Group MD and CEO. No API was called |
| hfrs.moh.go.tz (portal, dispensary listing, advanced-search page) | Dispensaries | No robots.txt. The listing is national (451 pages) and the advanced search is a POST form, which was not submitted |
| tatotz.org/portfolio/access-2-tanzania/ (known source) | Access 2 Tanzania | Re-read: P.O. Box 10955, Blue Rock House, Middleton Road |
| oshochem.com (home, /contact-us/) | Chemical Industry Ltd | Tanzania office contacts (identity uncertain) |
| www.tmda.go.tz/pages/northern-zone-health-centres (URL guess) | Old Arusha | HTTP 404; guessing stopped |

Pacing: at least 2.5 seconds between requests to one host, and 5.5 seconds on access2tanzania.com, which sets `Crawl-delay: 5`. robots.txt was read before every page: 123 requests to 45 hosts. OpenStreetMap and Overpass were not used, because both disallow `/api/` (and openstreetmap.org also disallows `/node/` and `/way/`) in robots.txt. The OSM tags and coordinates cited in notes come from the master and from wave 2's saved Overpass output.

## Blocked or unreadable sources

Not worked around in any case: no retries in a loop, no sign-in, no browser, no decoding of protected email links.

- **Blocked:**
  - www.isamilo.com/en/contact: HTTP 403 (Vercel security checkpoint)
  - kessybrotherstours.com: HTTP 403 (Cloudflare "Just a moment..." challenge)
  - www.tripadvisor.com (KiliStar listing): HTTP 403
  - www.ushirika.go.tz licensed-SACCOS PDF: HTTP 403
  - www.ndoro-lorge.connectotels.com/contact-us.html: TLS handshake failure
  - www.medpages.info: robots.txt disallows all agents except Google and Bing (not fetched)
- **Failed earlier waves, not re-fetched:** ndorolodge.com (HTTP 403), lemutakhakisafaris.co.tz (DNS), tz.kcbgroup.com (DNS), ecobank.com/tz (redirect loop)
- **Unreachable:** www.africadirectoryservices.com timed out, as in slice C
- **Lost or dead websites:**
  - tintintours.com redirects to a GoDaddy for-sale page
  - kessybrotherstours.co.tz does not resolve
  - bokeradventure.com: the old company pages (/about-us/, /contact-us/) return 404; the domain now serves a Pin Destinations itinerary app
  - enosaexpeditions.com: the bare host failed DNS once; the www host answered
- **Rendered by script:**
  - vodacom.co.tz: nothing read
  - www.precisionairtz.com: read from its own script bundle
  - yas.co.tz store locator: not called
- **Email protection (Cloudflare) not decoded:** yas.co.tz, isamilo.co.tz, dar-express.co.tz, mteiexpress.co.tz, limsafaris.co.tz, kcbgroup.com. Where the same address was published in plain text, it was used: access2tanzania.com in its structured data, summit2sandsafaris.com in its page text and meta description.

## Warnings

- **Possible closure or lapse (check before outreach):**
  - Tintintours: its domain is for sale, the directory phones date from 2015, and the newest reviews seen are several years old.
  - Lemuta & Khaki Safaris: no trace beyond its 2023 TATO listing, and its domain is dead.
- **Lost or hijacked domains:** tintintours.com (for sale), lemutakhakisafaris.co.tz and kessybrotherstours.co.tz (DNS), bokeradventure.com (content replaced by a booking-platform app). Nothing was used from them.
- **Renamed:** Tigo Tanzania is now Yas Tanzania (Axian Telecom); tigo.co.tz redirects to yas.co.tz.
- **Names that differ from the master:**
  - Tintintours trades as Tin Tin Tours / Tin Tin Adventure Safaris & Treks.
  - Enosa Expedition is Enosa Expeditions.
  - Kili Star Tours is "KiliStar Tours and Safaris - Day Tours".
  - Kessy Brothers is Kessy Brothers Tours & Travel Ltd.
  - Basecamp Tanzania is Base Camp Tanzania.
  - Mtey Booking Office appears to be Mtei Express (spelling to check on site).
  - Kkikalora Saccos is Kikalora SACCOS Ltd.
  - Old Arusha Health Center is listed as Old Arusha Dispensary / Old Arusha Clinic.
  - Canossa Dispensary is "CANOSA" in the TMDA list.
  - Henkel is Henkel Polymer Co. Ltd, a local company, not the multinational.
- **Duplicate records**, each pair researched once and cross-referenced in notes:
  - Access 2 Tanzania: Of266669dd470 and O31b73e1bb936
  - Boker Adventures: O7136ae38625d and Odade2f68937f
  - Tintintours: O66a49150a30a and O6c7f7cdd682b
  - Summit 2 Sand Safaris: O923da4a684cd and O9d6f9263adfd
  - Kessy Brothers: O17bd2f803731 and O9e7e9c05bdc1
  - Enosa Expedition: Odb7e9aa1b559 and O2ea7d99baa8a
  - Kili Star Tours: Ode3e3ade9452 and O00e287a17a2a
  - KCB (O911659e30dbc) is the same bank as KCB Bank (Oe724c258de33, slice C).
- **Shared spots, not duplicates:** Henkel and the Vodacom service centre are 20 m apart south-west of the Clock Tower; Access 2 Tanzania and Base Camp Tanzania are 45 m apart; the Dar Express and Mtey offices adjoin at the central bus stand.
- **Out of area:** none.
  - The Moshi records (Boker, Tintintours, Summit 2 Sand, Kessy, Enosa, Kili Star, Precision Air's Moshi office, Lim Safaris, Kikalora SACCOS) are in Kilimanjaro Region, about 22-23 km from Boma Ng'ombe.
  - Head-office routes only, all in Dar es Salaam: Ecobank, KCB, Vodacom and Dar Express.
- **Location to check:**
  - Henkel: the directory gives Dodoma Road, while OSM puts it beside the Clock Tower.
  - Old Arusha: the insurer's panel gives 6 Old Moshi Road, while a map-derived directory gave Nyerere Road.
  - Oloirien: TMDA's "Moivoi" entry may be in Arusha District Council, not near Kijenge.
  - Canossa: the master gives 9.8 km from Kijenge; the sources say Korongoni or Njiro Road.
- **Fit to check:**
  - Israel community office: a religious community.
  - PAG Church Njiro: a church office.
  - Kikalora SACCOS: a savings group, normally reached through KINEFA.
  - Usa River Booking Office: operator unknown.
  - Mazda: brand name only.
- **Master data to review:**
  - Access 2 Tanzania's website value "DMC/MAIN" is a TATO category; the real site is access2tanzania.com.
  - KCB's website value tz.kcbgroup.com does not resolve.

## Data-protection decisions

- **Personal inbox:** Summit 2 Sand Safaris' Managing Director is recorded with his published work inbox and mobile. The personal-domain (Gmail) inbox listed beside them was not recorded.
- **Base Camp Tanzania:** the About page states the two proprietors' relationship and one's nationality. Neither was recorded; their roles are worded neutrally from the pages.
- **Biographies not recorded:** Access 2 Tanzania (owners' backgrounds and a family link), JM Tours (founder's origin), Summit 2 Sand (MD's life story), Precision Air, Boker. Only names and published titles were kept.
- **Religion:** no names or details were recorded for the Israel community office.
- **Staff left out:** guides, drivers, porters, mechanics, the accountant, the intern and US office staff at Access 2 Tanzania; driver-guides and the sales consultant at JM Tours.
- **Snippet-only people:** Boker Adventures' founder and Tin Tin Tours' owner title come from search snippets and are marked `fetched: false`. Tin Tin's name is also on a fetched listing, as its host contact.
- **Not recorded because they are not the organisation's own publication:**
  - an unclaimed Finder Africa mobile for a Vodacom store
  - a booking aggregator's P.O. Box for Ndoro Lodge
  - a travel blog's P.O. Box and phones for Lim Safari
  - the BusBora platform support line on the Isamilo, Dar Express and Mtei booking sites
- **Facility inboxes kept:** Old Arusha and Canossa's Gmail inboxes are named after the facility, so they were kept as general inboxes.
- **Third-party names not used:** a data-broker result for a person named "Ndoro" and a third-party list of bank chief executives were ignored.

## Organisations not reached

None: all 37 records (30 organisations) have a line. These still have no email or phone with confirmed identity:

| Organisation | organisation_id | Distance | Why |
|---|---|---|---|
| Mazda | O615ce17408df | 1.6 km (Usa River) | Brand name only; no company found |
| Oloirien Community Dispensary | Of524b9360eb7 | 1.7 km | No register entry or phone; identity of the TMDA entry uncertain |
| Lemuta & Khaki Safaris | Ocb8c0d83adbf | 2.7 km | Dead domain; nothing beyond TATO |
| Ndoro Lodge | O6fa070dd7a9c | 3.2 km (Usa River) | Own site 403; booking mini-site TLS failure |
| Chemical Industry Ltd | O2310c00d7b59 | 3.4 km | Osho Chemical contacts found, identity uncertain |
| Israel community office | O822d982b3f46 | 3.8 km | Not identifiable; religious community |
| PAG Church Njiro | Oa8a5a32fa9fe | 4.4 km | Nothing found |
| Boker Adventures (2 records) | O7136ae38625d, Odade2f68937f | 22.2 km (Moshi) | Email and phone are snippet-only (pages now 404) |
| Kili Star Tours (2 records) | Ode3e3ade9452, O00e287a17a2a | 23.4 km (Moshi) | TripAdvisor listing only (403) |
| Usa River Booking Office | Of38ed0efb017 | not recorded (Usa River) | Operator unknown |
| Kkikalora Saccos | O225198c6cffe | not recorded (north of Moshi) | Register PDF 403; P.O. Box from snippet only |

## Stopping rule and next steps

The stopping rule (every record researched) is met. The search allowance is spent, and no search was refused by the session cap.

Suggested next steps:
1. **Health facilities:** the Ministry of Health master facility list, by official request (the user's decision), would give official phones for Oloirien and confirm Old Arusha and Canossa. The HFRS advanced search is a form and needs a person.
2. **On-site or phone checks:**
   - Mazda, Usa River Booking Office and Israel community office (what they are)
   - Chemical Industry Ltd (is it Osho Chemical?)
   - the Mtey/Mtei sign
   - Henkel's location
3. **Bank branch phones and managers** for Ecobank Arusha and the KCB Arusha outlets need a branch visit or a browser session (coordinator only, with the user's go-ahead).
4. **Ndoro Lodge** (3.2 km from Usa River) needs a call or visit; both of its web sources refuse automated reading.
5. **Confirm before use:** the Boker Adventures snippet contacts, the Tin Tin Tours directory phones (2015) and the Kessy Brothers yellow-pages phones.
6. `plan_contact_research.py` treats any line in this file as searched for this date, so re-queue records by hand if a later wave should retry them.
