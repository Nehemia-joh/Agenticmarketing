# Slice B coverage log: Arusha District Council (Arumeru West)

Run `arusha-welfare-2026-09` · Slice B · research carried out 2026-09-22 (all `accessed_on` values are 2026-09-22; the clock moved to 2026-09-23 while the files were being written) · Tools: WebSearch and WebFetch only. No browser, no sign-in, no forms, no contact with anyone.

## 1. Outcome

`B_arusha_district.jsonl` has **103 records**, and all 103 lines parse as JSON (checked with Python):

| Record type | Count |
|---|---|
| organisation | 45 |
| contact | 22 |
| relationship | 36 |

Of the 45 organisation records:

- **11 are confirmed inside slice B** (Arusha DC): SOS Children's Village Arusha (Ngaramtoni), House of Happiness (Kisongo), Canaan Children's Center (Kisongo), Living Water Children Centre (Kisongo), Habashabi Orphanage Centre (Kisongo), Hope Orphanage Center (Ngaramtoni), Upendo Face Orphanage (Machumba / Olturoto road), St. Gabriel Home (Mateves), The Plaster House (off the Ngaramtoni police post), Best Centre for the Blind (Ngaramtoni, snippet only) and Uhuru Unit Primary School (Ngaramtoni, snippet only, out of scope).
- **12 are in the Arusha area, but I could not confirm the ward.** Some may be in slice B: LOHADA, Matonyok Children's Home, Neema Village, Ucare Family Home, Ummu Aisha Orphanage Centre (Kirika "B", Simba Trucking area), Small Steps for Compassion (Mt Meru region), Tumaini House (YWAM Arusha), Karim Children's Care Centre, New Paradiso Orphanage, Bethlehem Center for Children, CHISWEA, and the funders Kesho and Heart for Africa.
- **The rest are outside the slice** and were recorded incidentally, with a `catchment_note`:
  - In other slices but within the catchment: Samaritan Village (Moshono), Malaika Children's Friends (Moshono), Olasiti Orphans Center, Tumaini For Africa (Njiro Rd), Watoto Kicheko (Njiro), Faraja Orphanage (Shangarai/Duluti), Fruitful Orphanage (Duluti), Save Africa Orphanage (Leganga), Arusha Kids Trust (funder), Tumaini Children's Foundation (Usa River), WOW Tanzania (Usa River), Havilah (University of Arusha, Usa River), Halima (Moshi), Arusha Children Center, and the government retention home, which is out of scope.
  - More than 25 km away: Children Concern Foundation (Mto wa Mbu), Maasai Girls Rescue Center (Karatu), Home Foundation (Karatu), Le Bao's Kids Foundation (Iringa), Huruma Centre (Iringa) and the Bahati Trust (Dar es Salaam).

**Search budget.** The **session-wide WebSearch cap of 200 calls was reached after my 36th query**, and my 37th and 38th queries were refused. I did **not** route searches through WebFetch to get around the cap. From then on I only fetched known URLs: institution sites, directory pages already found, and links on fetched pages. **The stopping rule was therefore not met.** Neither "12 consecutive queries with no new institution" nor "all ward names searched" was reached (see §3).

## 2. WebSearch queries run (36 executed, 2 refused)

| # | Query | New slice-B institution? |
|---|---|---|
| 1 | orphanage Ngaramtoni Arusha | Yes: Samaritan Village (later found to be in Moshono), Best Centre for the Blind, LOHADA, Uhuru Unit |
| 2 | children's home Kisongo Arusha | Yes: House of Happiness, Living Water |
| 3 | kituo cha kulelea watoto yatima Arumeru | Yes: SOS (Ngaramtoni) |
| 4 | Maasai children's home Arusha | Leads only: Matonyok, Neema, Amani |
| 5 | makao ya watoto Arusha vijijini | No (Arusha DC ward list and government pages) |
| 6 | orphanage near Arusha Tanzania village | Leads: One More Child, Tumaini House, Fruitful, Olasiti, Hope Center |
| 7 | rescue centre girls Arumeru | No (Kenyan results; Maasai rescue turned out to be in Karatu) |
| 8 | volunteer orphanage near Arusha Kisongo OR Ngaramtoni OR Olturumet OR Mateves | Leads: New Paradiso, Bethlehem |
| 9 | "Samaritan Village" orphanage Ngaramtoni | No (confirms US arm; location still open) |
| 10 | LOHADA orphanage Ngaramtoni | No new institution (LOHADA details) |
| 11 | "Best Centre for the Blind" Ngaramtoni | No (no results) |
| 12 | SOS Children's Village Arusha location Ngaramtoni | No new institution (13 km, Nairobi road) |
| 13 | SOS … contact phone email Ngaramtoni Hermann Gmeiner school Arusha | No |
| 14 | "Camp Moses" OR "Camp Joshua" LOHADA Arusha Ngaramtoni Kesho | No (Kesho) |
| 15 | Olturumet orphanage OR "children's home" OR "kituo cha watoto" | No |
| 16 | Oldonyosambu orphanage OR "children's home" Arusha | Lead: Upendo Face (via Idealist) |
| 17 | Oldonyowas orphanage OR "children's centre" OR "children's home" | No |
| 18 | Mateves Arusha orphanage OR "children's home" OR "children's village" | Yes: St. Gabriel Home |
| 19 | Matonyok Children's Home Arusha Tanzania special needs | No (Matonyok details) |
| 20 | "St. Gabriel" children home Mateves OR "St Gemma" Mateves school Arusha | No (St Gabriel details; UK charity 1118031) |
| 21 | Faraja Orphanage Children's Home Arusha location village founded 2008 | No (Shangarai) |
| 22 | "It Takes a Whole Village" Arusha children's home | No |
| 23 | Neema Village Arusha baby home location Kisongo OR Njiro OR Mateves OR Olasiti | No |
| 24 | "Canaan Children" Arusha Archdiocese orphanage location | Yes: Canaan (Kisongo) |
| 25 | Kata za Wilaya ya Arusha Vijijini orodha ya kata | No (ward list) |
| 26 | "Neema Village" Arusha Moshono/Nduruma/Mbuyuni/Njiro/Kisongo/Mateves | No (Samaritan found to be in Moshono) |
| 27 | One More Child Compassion House Tanzania Mount Meru orphanage girls location | Leads: Ummu Aisha, Children of Kilimanjaro (Moshi) |
| 28 | Tumaini House YWAM Arusha orphans location | No |
| 29 | Hope Center Tanzania orphanage Arusha hopecentertanzania location | Yes: Hope Orphanage Center (Ngaramtoni) |
| 30 | "Samaritan Village" Arusha Moshono/Ngaramtoni/Olmotonyi/Kiranyi clinic address | No (Moshono confirmed) |
| 31 | Kiranyi Arusha orphanage OR "children's home" OR "kituo cha watoto yatima" | Lead: unnamed Kiranyi care centre (arushadigital, 7 Apr 2026); Karim |
| 32 | Olkokola Arusha orphanage OR "children's home" OR "children centre" | Leads: Arusha Kids Trust / Save Africa Orphanage |
| 33 | Oljoro Arusha orphanage OR "children's home" OR "kituo cha watoto" | No (Watoto Kicheko is in Njiro) |
| 34 | Mbuyuni Arusha orphanage OR "children's home" OR "kituo cha kulelea watoto" | Leads: Habashabi (turned out to be Kisongo), Huruma (Facebook), Havilah |
| 35 | "Simba Trucking" Arusha area ward location Kirika | No (ward still unresolved) |
| 36 | "Save Africa Orphanage" Arusha location | No |
| 37 | Bangata Arusha orphanage OR "children's home" OR "kituo cha watoto" | **Refused: budget exhausted** |
| 38 | Ilkiding'a OR Ilkidinga Arusha orphanage … | **Refused: budget exhausted** |

## 3. Ward coverage

| Status | Wards and places |
|---|---|
| Searched by name | Ngaramtoni (town), Kisongo, Olturumet, Oldonyosambu, Oldonyowas, Mateves, Kiranyi, Olkokola, Oljoro, Mbuyuni, plus "Arumeru" and "Arusha vijijini" in general |
| Not searched (budget) | Bangata, Ilkiding'a, Moivo, Kimnyaki, Siwandeti, Sokon II, Olmotonyi, Lemanyata, Mwandet, Musa, Nduruma, Oltroto/Olturoto, Laroi, Tarakwa, Sambasha, Ilboru (DC ward) edges, Nengung'u, Likamba, Lengijave, Bwawani, Oloirien (DC), Kiutu, Mlangarini |

The official ward list comes from the Kiswahili Wikipedia template *Kata za Wilaya ya Arusha Vijijini* (27 wards). That template confirms that Olasiti and Moshono belong to Arusha City, not Arusha DC.

## 4. Sources fetched (WebFetch)

**Read successfully (used as evidence):**

- **Institution sites**
  - sos-tanzania.org (home and Arusha page); sos-childrensvillages.org (Arusha and Tanzania pages); soschildrensvillages.ca; soschildrensvillages.org.uk news
  - houseofhappiness.ch (/en, /house-of-happiness, /organisation, /fakten)
  - canaanchildrenscenter.com (home, contact, donate); arusha-archdiocese.or.tz (Kanaani page)
  - livingwaterchildrencentre.org (home, about, safe-houses, academic-excellence, volunteer)
  - habashabiorphanage.wixsite.com (home, projects, contact)
  - hopecentertanzania.org (home, orphanage page, about, blog)
  - upendo-face.org (home, story, contact /info, association, news)
  - lohada.org (home, about, camp schools, contact, newsletters, farm)
  - neemavillage.org (home, about, original homepage, contact); ucareproject.com
  - ummuaishaorphanage.org (home, about, contact)
  - theplasterhouse.org (home, contact)
  - smallstepsforcompassion.org (home, about)
  - ywam.org location pages; ywamarusha.org
  - samaritanvillageorphanage.org (home, about, contact)
  - malaika-childrenfriends.org (home, family home)
  - tanzanianorphans.org; fruitful-orphanage.jimdoweb.com
  - arushakidstrust.com (home, about, school sponsorship, contact-us)
  - tumainimeanshope.org; wowtanzania.org (home, contact); halimaorphanagecenter.org; childrenconcern.or.tz; lebaoskidsfoundation.com; bahatitrust.com; maasairescue.org
- **Funder and partner pages**
  - lovefortheleast.org; havenofhopeintl.org (progress report); servingorphans.org (partner homes, Matonyok, Bethsaida, Shalom)
  - childrensrefuge.org; e-ducare.org (programmes, Karim, Matonyok)
  - readwithmearusha.com (where-we-work, Samaritan, Karim); heartforafrica.co.uk (home, orphanages, news, major projects)
  - onemorechild.org; futureforkids.nl (Arusha page and home); acyc.family
  - kilimanjaroclimbingcompany.com (Faraja); sustainablevision.org (Faraja)
  - fondazioneslowfood.com (Canaan garden); h2oforlifeschools.org
- **Registers and directories**
  - ProPublica Nonprofit Explorer (Kesho, Samaritan Village, Serving Orphans Worldwide); GuideStar (Kesho)
  - ngobase.org (orphanage list p1–p2, child-rights list, vulnerable-groups list, profiles 24648, 24656, 316196, 316200)
  - idealist.org (Upendo Face, Arusha Children Center, Home Foundation); oneworld365.org (LOHADA); betterplace.org (Samaritan)
  - projectsoverland.wordpress.com; bandalakuku.wordpress.com; Tripadvisor forum thread (Faraja)
- **Official and reference pages**
  - jamii.go.tz (children's-home registration page; Arusha retention home)
  - Wikipedia (Arusha District Council, Kisongo, Mateves, One Heart Source; Kiswahili ward templates for Arusha Vijijini, Arusha mjini and Meru)
  - arushadigital.com (7 Apr 2026 news item)

**Blocked or failed:**

| Source | Result |
|---|---|
| facebook.com (neemavillagearusha, Matonyak page, becechi) | Login wall; only the title was visible |
| instagram.com (neema_village) | Login wall |
| Charity Commission register (1118031), totalgiving.co.uk | HTTP 403 |
| findthatcharity.uk | Socket hang-up (tried twice) |
| stgemma.org, www.stgemma.org, stgemmagalganschoolarusha.ac.tz | DNS failure (sites appear dead) |
| farajaorphanagechildrenshome.org, enjivaiorphanage.org, chiswea.org, chiswea.or.tz, cradleoflovebabyhome.org, emusoi.org, goforitgranny.com | DNS failure |
| farajaorphanage.org | Title only |
| venerateorphanage.com, stepbystep.or.tz | HTTP 500 |
| volunteerbasecamp.com | HTTP 521; its placement page **redirects to an unrelated gambling domain (not followed)**. Its Ngaramtoni location claims are therefore treated as unverified |
| netzkraft.net, umojacentre.org | Connection refused |
| arushadc.go.tz and arushacc.go.tz department pages | JavaScript-only (only "GWF CORE" returned) |
| TCRA Arusha postcode PDF | HTTP 404 |
| havenofhopeintl.org Matonyok main page | Password-protected |
| felicityfeinman.wordpress.com | Private WordPress blog |
| GoFundMe (Matonyok) | HTTP 404 |
| JustGiving (Save Africa Orphanage) | HTTP 410 |
| Viator, hotel.com.au | HTTP 403 |
| arushacity.com | HTTP 526 |
| 404s | htcfsurprise.org, watoyo-tanzania.de, sfasu.edu article, simbatrucking contact page, third-lens.org, and sub-pages of upendo-face (/en, /kontakt), hopecentertanzania (/directors, /contact), houseofhappiness (/blog, /about-us), smallstepsforcompassion (/contact), arushakidstrust (/contact), livingwaterchildrencentre (/about) |

**Deliberately not used (brief §4):**

- Child sponsorship profile pages (e.g., the LOHADA "Musa" page and a Haven of Hope sponsorship product page).
- Children's health or HIV data on the Canaan archdiocese and Slow Food pages.
- Details of the family circumstances of children at St. Gabriel Home.
- Founder names that appear only on third-party pages (Faraja).
- Website-template placeholder names on the Hope Center About page.

## 5. Gaps and leads I could not confirm

1. **Unnamed Kiranyi care centre.** Arushadigital (7 Apr 2026) reports the Arumeru West MP hosting orphaned children from a care centre (*kituo cha malezi*) in Kiranyi ward. The article does not name it, and I could not identify it without further searches.
2. **Location to confirm (possibly in slice B):**
   - Neema Village and its Ucare home: 10-acre site, pays school fees for 49 children.
   - Matonyok Children's Home: 54 children and a campus school.
   - LOHADA: a now-defunct directory places it in Ngaramtoni; the farm is south-east of Unga Limited.
   - Ummu Aisha: Kirika "B", Simba Trucking area, possibly off Oljoro road. Could be Arusha City or DC.
   - Small Steps for Compassion: "Mt Meru region". It may be the same place as One More Child's "Compassion House".
   - YWAM Tumaini House: base "near KIA", probably Meru.
   - Also Karim, New Paradiso, Bethlehem Center for Children and CHISWEA.
3. **Upendo Face ward.** Olturoto is inferred only from the Idealist address "Olturonto Rd"; the organisation's own site says Machumba village.
4. **Names found but not located or verified:** Enjivai Orphanage (dead domain), Venerate Orphanage (site error), "Arusha Children's home" (Facebook takesawholevillagekids), Huruma Orphanage Arusha (Facebook, 15 children), Chakuwama Orphanage – Lukiza Foundation (ngobase, no details), Step By Step (site error), Shalom Orphanage and Bethsaida Girls Home (Serving Orphans Worldwide partners; locations not published), an unnamed abroaderview orphanage (founded 2009, 25 children), Amani Children's Home (Viator page blocked), One Heart Source (children's home "outside Arusha" per Wikipedia; own site gives no detail), Ace Africa (office location not found), the zili_house_of_child_care Instagram account (city unknown), and Upendo Friends School and Hope School in Mateves (school list only; any link to a welfare body unknown).
5. **Registers not confirmed:** UK charity 1118031 (Sponsors of St Gabriel Home): status and income unread because of the 403. Also not captured: Neema Village's EIN and income, Seeds of Hope Tanzania's details, Arusha Kids Trust's ACNC number, and Tumaini Children's Foundation's CRA number.
6. **Sites that look dead or stale:** St Gabriel and St Gemma sites (DNS); Canaan (latest date 2020); Habashabi, Hope Center and Living Water (undated); Ucare (2019); CHISWEA (2018).
7. **Next steps if the search budget is raised** (CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION): run the 23 unsearched wards in §3 as "<ward> orphanage", "<ward> children's home" and "kituo cha watoto <ward>"; look up Neema Village's and Matonyok's ward; and identify the Kiranyi centre.
