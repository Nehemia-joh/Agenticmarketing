# Government-lead pitfalls found the hard way (2026-09 run)

Each entry records a trap that would catch a competent agent again, and says how the scripts in `scripts/government/` now handle it.

| Pitfall | What happened | Now handled by |
|---|---|---|
| Council sites render in JavaScript | Plain fetches of GWF CORE pages return only a title and deep links redirect home | `collect_council_sites.py` reads the sites' public JSON API: `/api/profiles`, `/api/statistics`, `/api/footer`, `/api/menus`, `/api/pages/slug/<slug>`, `/api/files`, `/api/news`, `/api/announcements` |
| API responses name the website editors | Every record carries `createdBy` with an editor's name and work email | `gov_lib.sanitise` drops `createdBy`, photos and biographies before anything is written; verification fails if a capture still holds `createdBy` |
| Council contacts are not where expected | `footer.contact` was empty on every site; Moshi District and Moshi Municipal publish email, phone and P.O. box inside `footer.links.keyServices` | The build walks the whole footer for `email`, `phone` and `poBox` |
| An official map point is malformed | Moshi District Council's longitude is `3741495200674615` | Points outside Tanzania are rejected and raised for review, never repaired silently |
| Websites and the census disagree on population | Hai's site shows 269,999; the 2022 census has 240,999 | The run uses the census and raises `council_population_differs` |
| A region's table shares a page with the first council's ward table | Parsing the whole page read Arusha Region's council list as Monduli's wards | `collect_census_wards.py` reads rows only below the ward-table title, requires ward numbers in sequence and checks every council total |
| Census quirks | "13.. Moivo", odd quotes in "Longuo 'B'", and a Moshi District title without "by" | Tolerant row and title patterns; quotes are stripped |
| No ward boundaries in OpenStreetMap | Only regions (admin_level 4) and districts (level 5) exist here | Ward reference points from mapped ward offices, Wikipedia and OpenStreetMap places, labelled `estimated` |
| The city polygon is too small | OpenStreetMap's "Arusha Municipal" excludes Sakina ward and the Arusha City campus | `joint_zones` checks Arusha City with Arusha District (and Moshi Municipal with Moshi District) as one zone |
| Wikipedia coordinates can belong to another ward | "Terrat, Arusha District" sits in Simanjiro; "Majengo, Monduli" sits in Meru; Nkoaranga and Poli share coordinates; 16 ward articles have none | Articles must name an allowed district and fall inside the zone; shared coordinates are rejected; each rejection is a review item |
| The same ward name exists in neighbouring councils | Oloirien is a ward of both Arusha City and Arusha District | Evidence claimed by two wards goes to neither; a review item asks for a decision |
| OpenStreetMap names places "Hamlet, Village" | "Uswaa, Machame Uroki", "Ekenywa, Oltrumet" | Places listed under an area named like the ward give a centre point (three or more count as strong evidence) |
| Spellings differ between sources | Olturoto / Oltroto / Oltoroto / OLTURUTO; Kimnyak / Kimnyaki; Sokon I / Sokoni I | Reviewed `ward_aliases` in `links.json`, applied to every source |
| Rosters come in different forms | Hai: web page and spreadsheet; Arusha District: a two-page scanned PDF with phones; Longido: English and Kiswahili pages that list different people | Page-line parser, transcription files with locators, and a `roster_conflict` review when sources disagree |
| PDF page rendering was unavailable | The Read tool could not render PDF pages (no `pdftoppm`) | Extract the embedded page images with pypdf, crop them into strips and read those |
| Rosters list people who do not convene wards | Special-seat councillors and the constituency MP | Not copied; the transcription README says which rows were left out |
| OpenStreetMap government tags are mixed | About 200 unnamed `government=administrative` points; party offices, a court and police tagged `office=government`; a ward office tagged as a place of worship | Every named office is classified and logged; unnamed points are counted, not imported; a tag that conflicts with a name is a review item |
| Overpass `out tags` has no coordinates | The place query returned names without `lat` and `lon` | Use `out body` for nodes and `out center` for ways |
| Back-to-back Overpass queries are refused | 429 and 504 after a heavy query; the kumi.systems mirror completed it | `gov_lib.overpass` retries with backoff, then falls back to the mirrors |
| Wikipedia rate-limits at 1 request per second | HTTP 429 with Retry-After | Wikipedia spacing is 2 s in `gov_lib.py` |
