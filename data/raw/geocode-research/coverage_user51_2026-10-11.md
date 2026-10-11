# Office locations for the 51 named company leads, 2026-10-11: coverage log

Evidence file: `geocodes_user51_2026-10-11.jsonl` (58 lines for 51 leads, in the `scripts/master/apply_geocodes.py` format plus an `office` field: `arusha_branch`, `head` or `only`). The lead list is `user_requested_locations_2026-10-11.json`. Nothing was written to any database. `apply_geocodes.py --file <this file> --db master` in preview, run against a copy of the master, reports 35 leads to fill, 0 skipped.

## Result

| Outcome | Leads |
|---|---|
| Placed in the catchment (an Arusha or Moshi office) | 10: White House, Wilderness Collection, Imara Kilele Safaris (Moshi), The Rickshaw Travels, Claritas International, Flightlink, Fortes Africa, Takims Holidays, Robin Hurt Safaris, Shades of Africa |
| Placed outside the catchment (only office or head office) | 25 |
| Outside, no exact office (town or country only) | 12 |
| Not found | 4: The First Lady Tour Safari, Discover Tanzania Safaris, Mount Kilimanjaro Safari Club, Mbali Mbali Lodges and Camps |

Each lead has at most one `placed` line: its Arusha-area office where one exists, otherwise its office. A lead with an Arusha office also has a second line with `"office": "head"` and status `outside_confirmed`, so `apply_geocodes.py` ignores it. Where the head office could be located, that line carries its point.

Precision used: `point` for an own-site pin or JSON-LD geo point and for OpenStreetMap features of the organisation; `address` for a building or short street found by Nominatim from a published address; `locality` for a long street, a ward, a suburb, a landmark of the area or the airport; `city` for Arusha city centre where only "an Arusha office" is published. Four leads are placed at `city` precision: Fortes Africa, Takims Holidays, Robin Hurt Safaris and Shades of Africa. The lead map draws locality and city points as estimates.

## Sources and how they were used

1. **Own websites.** `scripts/maps/collect_geocodes.py sites --targets-file user_requested_locations_2026-10-11.json --crawl-cache <main checkout crawl cache> --fetch --always-fetch --max-extra 4 --mentions` scanned the cached pages read-only. It then read each site's home page and up to four contact or location pages (1.5 s per site, robots.txt honoured), looking for map pins and for the text around any mention of Arusha, Moshi, Usa River or the airport. Some pages were found by hand, for example Rickshaw's `about/contact?loc=Arusha`, Claritas's `claritas.co.tz/contact/`, Wilderness Collection's contact page and Shades of Africa's contact page. Those were read with the new `pages` subcommand. Embeds are used as `point` only when the view is about 4 km or less. City-scale embeds (Dolphin Tours 255 km and 63 km, Macho Halisi 1,390 km) and template maps (Wilmaar's London Eye) were not used.
2. **OpenStreetMap, nationwide by name.** The new `osm-names` subcommand ran four batched name-regex queries over Tanzania (one at a time, at least 6 s apart, `[timeout:180]`), all on overpass-api.de. A fifth query looked up office buildings (PSSSF Plaza, PPF Plaza, NSSF Commercial, Ursino, Samora Tower, IT Plaza, Oyster Pearl).
3. **Nominatim.** 43 queries in five batches at one per second, cached. The queries are the addresses read from the leads' own pages or records (`nominatim --queries`).
4. **Directories.** TATO portfolio pages, which mostly give no street; several share the bulk entry "P.O.Box 2485, Dar es Salaam". The ATE member directory (Shades of Africa) and SafariBookings (African Horizons, Urth Expedition, Afric'Aventure, Skylink) were also used. Earlier contact research in `data/raw/contact-research/` supplied Claritas's Arusha and Moshi offices and the African Galleria address.
5. **Web search: 20 of 35 used** (listed below). Then WebFetch only on URLs already in hand.

## Per lead

### Catchment: Arusha-area office found

- **White House** (hotel, Arusha): placed at `point` from OpenStreetMap node/4391202490 ('White House', tourism=hotel, Fire Sinone). The earlier round held it back because the stored distance did not match. This node is 2.63 km from the importer's original Kijenge anchor (-3.3701, 36.7123, `collect_partner_leads.js` at 504b729), which reproduces the stored 2.6 km. The hostel 'The White House of Tanzania' is 3.95 km away and has a different kind.
- **Wilderness Collection**: placed at `point`. Its contact page gives 'Tanesco Road, Clocktower Roundabout, Plot 2, Arusha 23100', the footer says Plot 75, and the page links the Google Maps place of the Four Points by Sheraton / The Arusha Hotel building (!3d-3.3730859!4d36.694542). The camp at Ngorongoro is not the office.
- **Imara Kilele Safaris**: placed at `address`, Moshi. Its contact page gives 'KIUSA LINE STREET, MOSHI, KILIMANJARO, P.O. BOX 623', and Nominatim places Kiusa Street (way/56670842) in central Moshi. The many embeds on its home page are national parks. A SafariBookings-style listing (web search Q4) also says it is based in Moshi.
- **The Rickshaw Travels** (`arusha_branch`): placed at `address`. Its Arusha contact page gives 'Ingira Road, House No.184, Behind Kibo Palace Hotel, P.O. Box 13959', and the point is Kibo Palace Hotel (way/247916207). The head office line is Buzwagi Street, Msasani, Dar es Salaam (street, Nominatim).
- **Claritas International** (`arusha_branch`): placed at `locality`. Its contact page gives '5th Floor, PSSSF Plaza, Plot No. 15 Corridor Street (Off Old Moshi Road)' and a Moshi office (NSSF Commercial Complex, Aghakhan Road). Neither building is in OpenStreetMap or Nominatim, so the point is the Arusha segment of Old Moshi Road. The head office, '395 Ursino Building, Morocco Junction, Mwai Kibaki Road', is not placed because the OSM candidates are ambiguous. The TATO site claritasint.co.tz does not resolve (DNS).
- **Flightlink** (`arusha_branch`): placed at `locality`, Arusha Airport. Its own site says 'our hubs in Dar es Salaam, Zanzibar and Arusha' and that tickets are sold at airport offices, and Wikipedia gives 'Secondary hubs: Arusha Airport'. The point is the aerodrome node from Nominatim. The head office line is the own-site embed at Oyster Pearl Galleria, Masaki.
- **Fortes Africa** (`arusha_branch`): placed at `city`. Its site says 'Headquartered in Mwanza with branches in Arusha, Dar es Salaam, and Mtwara' and gives no Arusha address (contact pages read; web search Q13). The head office line is the own-site embed at 19 Station Road, Mwanza, which matches OSM node/4759226025.
- **Takims Holidays** (`arusha_branch`): placed at `city`. Its contact page lists 'Dar es Salaam | Arusha | Zanzibar', and a World Travel Awards profile (Q16) says it opened in Arusha in 1981. No Arusha address was found. The head office line is OSM way/368493345, 23 Mtendeni Street, Dar es Salaam.
- **Robin Hurt Safaris** (`arusha_branch`): placed at `city`. Its team page names staff 'based in the Arusha office'. No address was found (contact page; Q12). The head office in Nanyuki, Kenya, is outside Tanzania and not placed.
- **Shades of Africa** (`arusha_branch`): placed at `city`. The ATE directory lists it in Arusha with the Arusha landline +255 27 2548659. Its own site and contact embed give the main office as Corner House, Kimathi Street, Nairobi. **Note:** `apply_geocodes.py`'s Tanzania check (-12 < lat < -0.9, 29 < lon < 41) would accept that Nairobi point (-1.2849, 36.8217), so it was deliberately left out.

### Outside the catchment: office placed

- **AFRICAN GALLERIA**: `point`, OSM way/476917459, shop=gift 'African Galleria', Kibaoni/Rhotia on the Karatu-Ngorongoro road. This matches the ATE address 'Manyara Kibaoni Karatu'. The record's site answered 503, and africangalleria.com failed its TLS handshake.
- **Dolphin Tours & Safaris** (`head`): `point`, OSM node/11585005829, office at Butimba, Mwanza. Its own embeds are city-scale and were not used.
- **Easyota**: `address`, the 84 Kinondoni Road building (Regus, Suite 124), from its own contact page.
- **Endelea**: `locality`, Nelson Mandela Road, Kurasini (Plot 71-74), from its own contact page.
- **EvMak Tanzania**: `address`, Mtwara Crescent, Msasani (Plot 235 Oyster Bay), from its own contact page. OSM node/2807690585 'EvMak Tanzania' was not used: it lies in the city centre while its own tags give Ghuba road and postcode 14111.
- **Feimac Travels**: `locality`, Mbezi Beach. This is the place text of its own embed.
- **GO TANZANIA**: `address`, Diamond Plaza, Samora Avenue. The office is opposite it.
- **H & A Holidays**: `address`, Tanzanite Park, New Bagamoyo Road, Dar es Salaam, from its own home page ('3rd Floor, Tanzanite Park'). It also has an operations officer for Zanzibar. Searched with Q5.
- **Imaging Smart**: `locality`, Chang'ombe ward. Mbozi Road (opposite Berger Paints) is not in Nominatim. It also has showrooms on Zanaki Street and at Shoppers Plaza, Mikocheni.
- **Kearsleys Travel & Tours**: `point`, its own JSON-LD geo, about 25 m from OSM way/368435780 (16 Zanaki Street). No Arusha office (Q14).
- **MAGS Travel**: `locality`, Azikiwe Street.
- **Masumin Tours**: `point`, its own contact embed in Mwanza.
- **Mount Royal Safaris**: `locality`, Gangilonga, Iringa.
- **Namiri Tours**: `point`, OSM node/13274021854 near Rufiji Street, Mwanza. Its home page is disallowed by robots.txt, so the about and contact pages were read.
- **Napenda Adventures**: `locality`, Tabata Relini roundabout (Plot 299, Block A). Its site answered 202 with no page.
- **Nuru Tours**: `locality`, Mbezi Beach, from its own contact page.
- **Old Explorer (Tanzania Explorer)**: `point`, its own businessLocationCoordinates (head office Kawe Beach, Dar es Salaam).
- **Print Plus Media**: `point`, its own contact embed in Zanzibar.
- **Safari Jens / Kitulano**: `locality`, Kibangu (Ubungo), with Kibangu Police Station as the landmark.
- **Stan Tours & Safaris**: `point`, its own contact embed in Dar es Salaam (Kipalapala Street). The Moshi lodge is accommodation, not an office.
- **United Tansania e.V**: `point`, its own contact embed at Endamaghan, Lake Eyasi.
- **Victory Attorneys**: `address`, IT Plaza, Ohio Street. This is the place text of its own embed.
- **Wilmaar Insurance Brokers**: `locality`, Samora Avenue. Its contact page gives 'Samora Tower, Samora Avenue, C3, Office No 604', and Samora Tower is not in OSM. The page's map is a template's London Eye.
- **Delaware Luxury Safari**: `locality`, Kisutu ward (Plot 1145, Block 16). safasafaris.com refused the connection. Searched with Q19.
- **Bongoplan**: `locality`, Sokoine Drive. Its 'Arusha' page is a tour category, not an office.

### Outside, no exact office

- A Tent With A View: 'Dar Es Salaam Office', P.O. Box 40525 only.
- Afric'Aventure: Dar es Salaam only. Its domain now belongs to an unrelated blog. Searched with Q11.
- African Horizons: Wilmette, Illinois, USA (SafariBookings p282). Searched with Q3.
- Urth Expedition: Austin, Texas, USA (SafariBookings p2331). Searched with Q2.
- Amazing Tanzania: Karatu only. Its embed is a place search with no point.
- Macho Halisi: Karatu only. Its embed is a regional view.
- Fantacy Adventures: Dar es Salaam P.O. Box only. Its map shows the Serengeti camp.
- Ibhanilfa Safaris: 'Malindi Estates, Dar es Salaam'. The Nominatim matches are ambiguous.
- Senjaro Pay: Dar es Salaam P.O. Box only.
- Shayona Safaris: Mwanza only. Its site answered 522.
- Skylink Travel: its text address (Nature Offices, Toure Drive, Msasani) and its map embed (city centre, the older Amani Place address) disagree. Not placed. Searched with Q6.
- Wilderness Experience: Sua Road, Morogoro CBD is not in Nominatim.

### Not found

- **The First Lady Tour Safari**: no site and no address. Searched with Q1, Q15 and Q20 (phone numbers). OSM has only unrelated shops.
- **Discover Tanzania Safaris**: no site. TATO shows the bulk P.O.Box 2485 Dar es Salaam, but its phone is a northern-zone landline. Searched with Q10.
- **Mount Kilimanjaro Safari Club**: TATO shows the bulk P.O.Box 2485 with an Arusha landline and info@tanganyika.com. Tanganyika Expeditions lists an Arusha contact without an address. Searched with Q8.
- **Mbali Mbali Lodges and Camps**: job listings (Q18) name an Arusha reservations office, but the listing page answered 403. The contact page gives only a Dar es Salaam P.O. Box. Left for a browser lookup.

## Web searches (20 of 35)

| # | Query | Result |
|---|---|---|
| Q1 | "First Lady Tour Safari" Arusha office | nothing |
| Q2 | Urth Expedition / Urth Safari office | US, Austin TX (SafariBookings) |
| Q3 | African Horizons safari (847) 905-0296 | US, Wilmette IL (SafariBookings) |
| Q4 | Imara Kileleni Safaris Arusha/Moshi | based in Moshi |
| Q5 | H&A Holidays Tanzanite Park | nothing; the own site gave the address |
| Q6 | Skylink Travel Arusha branch | only Dar es Salaam (Amani Place) |
| Q7 | Rickshaw Travels Arusha office | nothing; the own site gave the address |
| Q8 | Mount Kilimanjaro Safari Club Arusha | nothing |
| Q9 | Shades of Africa Arusha | ATE directory (Arusha) |
| Q10 | Discover Tanzania Safaris 2050125 / habari | nothing |
| Q11 | Afric'Aventure | Dar es Salaam (forum, SafariBookings) |
| Q12 | Robin Hurt Safaris Arusha office | nothing |
| Q13 | Fortes Africa Arusha branch | nothing |
| Q14 | Kearsleys Arusha office | head office only (16 Zanaki Street) |
| Q15 | thefirstladytoursafari | nothing |
| Q16 | Takims Holidays Arusha office | Arusha branch since 1981, no address |
| Q17 | Flightlink Arusha airport office | Wikipedia: Arusha Airport secondary hub |
| Q18 | Mbali Mbali Arusha office | job listings name Arusha (page 403) |
| Q19 | Delaware Luxury Safari / Safa Safaris | nothing |
| Q20 | First Lady phone numbers | nothing |

## Blocked or unreadable (not retried or worked around)

- mabumbe.com job listing: HTTP 403.
- safasafaris.com: connection refused.
- claritasint.co.tz and albatros.co.tz: DNS failure.
- africangalleria.co.tz: 503. africangalleria.com: TLS EOF.
- shayonasafaris.com: 522.
- napendaadventures.co.tz: 202 with an empty body.
- namiritours.co.tz: home page disallowed by robots.txt.
- tanganyika.com/contact: 406. The contact.php page was read.
- rickshawtravels.com /contact and /contact-us: 404. The `about/contact?loc=` pages were read.
- skylinktanzania.co.tz/branches renders no text without a browser.
- No browser tools or Google Maps were used.

## Tooling

`scripts/maps/collect_geocodes.py` gained these additive options. `--targets-file` (a named lead list) works for `sites`, `osm`, `osm-names` and `nominatim`. `sites` also takes `--crawl-cache`, `--always-fetch` and `--mentions`. `nominatim` takes `--queries` (reviewer-written queries). `--out` is available on each of them. There are also two new subcommands: `osm-names` (nationwide batched Overpass name search) and `pages` (scan named URLs for pins and Arusha mentions). Working files are in `runtime/geocode/` of the worktree: `site_hits_user51.json`, `osm_name_hits_user51.json`, `osm_buildings_user51.json`, `nominatim_hits_user51*.json` and `queries_user51*.json`.
