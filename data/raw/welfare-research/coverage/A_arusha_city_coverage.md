# Slice A: Arusha City Council, coverage log

Run: `arusha-welfare-2026-09` · Slice A (urban Arusha, focus on residential care) · Research date 2026-09-22. The session ran past midnight, so the last few fetches were early on 2026-09-23. All records carry `accessed_on: 2026-09-22`, the run date.

Output: `A_arusha_city.jsonl`. 108 lines, all parse as JSON (checked with Python). The same check also confirmed allowed enum values, excerpts of 25 words or fewer, and a risk reason on every record.

| Record type | Count |
|---|---|
| organisation | 49 |
| contact | 31 |
| relationship | 28 |
| enquiry | 0 (slice H only) |

Organisation segments: residential care 25, funder 12, family-based programme 5, specialised centre 4, out of scope 3.
Verification (organisations): verified 21, needs_review 16, unverified 9, historical 3.
`pdpa_risk` across all records: low 62, medium 40, risky 6.

## Main constraint: search budget exhausted

The session-wide WebSearch cap (200 calls, shared with the other agents) ran out after this agent's 22nd query. The tool said to stop searching, and I did not try to get around the cap through search engines. After that I only used WebFetch on URLs I already had, links followed from those pages, and map-data APIs (OSM Nominatim and Overpass) to geocode places I already knew about.

- **The stopping rule was NOT met.** I did not reach 12 consecutive queries with no new institution, and new names were still appearing when the budget ran out.
- **Ward-by-ward searches were not run.** None of these ward names were searched: Sakina, Kijenge, Ilboru, Njiro, Moshono, Sombetini, Olasiti, Kimandolu, Themi, Sekei, Levolosi, Ngarenaro, Unga Ltd, Kaloleni, Daraja Mbili, Lemara, Baraa, Terrat, Muriet, Sinoni, Engutoto, Oloirien, Olmoti, Osunyai, Kati, Elerai, Olorieni, Sokon I, Mjini Kati.
- **To finish the slice:** raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and run the ward queries, plus "street children Arusha", "makao ya watoto Arusha" and "baby home Arusha".

## WebSearch queries run (22 completed, 4 refused)

| # | Query | New institutions found |
|---|---|---|
| 1 | Arusha Children's Trust arushachildrenstrust.org | ACT (seed) |
| 2 | Neema House baby home Arusha Tanzania | Neema Village; Neema House is in Geita (discarded) |
| 3 | SOS Children's Village Arusha Tanzania | SOS CV Arusha (seed) |
| 4 | Faraja Orphanage Children's Home Arusha | Faraja (seed); ngobase profile |
| 5 | Neema Village Arusha location Njiro baby home address | Projects Overland list, GuideStar |
| 6 | "Emayani" Arusha vulnerable center | Emayani Foundation (not a match) |
| 7 | orphanage Arusha Tanzania children's home | Fruitful, Hope Center, Samaritan Village, Ummu Aisha, Canaan |
| 8 | kituo cha kulelea watoto yatima Arusha | Huruma (Muriet), Shalom Center (Kisongo) |
| 9 | Samaritan Village orphanage Moshono Arusha | Funders: WATOYO, Love for the Least, Read With Me, Adventure Church |
| 10 | "Tumaini for Africa" orphanage Arusha Njiro | Love Our Tanzania Family, Tumaini Children's Foundation, ngobase list |
| 11 | takesawholevillagekids Arusha children's home | Malaika Children's Friends (link), abroaderview |
| 12 | "Peace House" Arusha Tanzania | Peace House Africa / Secondary School |
| 13 | Huruma children's home Muriet Arusha kituo cha watoto yatima | Ujamaa Children's Home, Huruma Children's Trust (Morombo) |
| 14 | "Camp Joshua" Arusha orphanage | LOHADA, Enjivai, St Joseph's, Christ Hope (YouTube) |
| 15 | LOHADA Arusha Camp Moses Camp Joshua orphanage Unga Limited | Kesho (funder) |
| 16 | kituo cha watoto yatima Huruma Muriet Arusha mgogoro ardhi | Huruma Vision land dispute (Arusha Digital, Aug 2026) |
| 17 | "Ujamaa Children's Home" Arusha Njiro | Ujamaa new domain, Weily Tribe, Cybo plus code |
| 18 | "Huruma" children's trust Arusha "Mrombo" OR "Muriet" OR "Sokon" | TerraWatu, Hope for Huruma (Kenya; discarded) |
| 19 | "Huruma Vision" Arusha orphanage | Capital International, Hands In For Huruma (ACNC), Azar Foundation, Imaniworld |
| 20 | "Christ Hope" orphanage Arusha Tanzania | Christ Hope, Good Hope Orphanage (Idealist), Hope Orphanage Centre (FB) |
| 21 | Enjivai orphanage Arusha | Enjivai details |
| 22 | St Joseph's orphanage Arusha Sister Crispina Mnate | Unite Africa Foundation, BabuBibi (not checked) |
| 23-26 | street children centre Arusha; makao ya watoto Arusha jiji; baby home Arusha abandoned infants rescue centre; children's home Njiro Arusha orphans | Refused: budget exhausted |

## Other discovery, without WebSearch

- **OpenStreetMap Overpass**, bounding box -3.46,36.58 to -3.28,36.80:
  - `amenity=social_facility` returned only the Neema House Orphanage node.
  - A name regex (orphan, yatima, watoto, children, kids, baby, street child, vulnerable, huruma, rescue) added Emayani vulnerable people's center and Jitihada pre & primary school (orphans).
  - `office=ngo` returned 8 NGOs, none of them child welfare apart from Emayani.
  - Two other Overpass queries timed out (504 / 60 s).
- **Nominatim:** name search worked for "Emayani" and "orphanage". Searches for children, watoto, home, kituo, center and "social facility in Arusha" returned nothing or irrelevant places. I also used it to geocode Kigongoni, Moivaro, Kiserian, Simba Trucking, Kirika and Plaster House, and to reverse-geocode Jitihada and Moivaro.
- **NGOBase lists for Arusha Region:**
  - Orphanages, pages 1-2: 17 entries.
  - Child Rights and Welfare: 10 entries.
  - Shelter Homes: 1 entry.
  - Disability Support: 4 entries.
  - Education and Training: pages 1-2 read; page 3 rendered without listings.
- **Funder and partner pages followed:**
  - Heart for Africa: orphanages, where-we-work, schools and news pages.
  - Read With Me Arusha: where-we-work and Karim pages.
  - Love for the Least, Love Our Tanzania Family (home, vision, past projects), WATOYO, Imaniworld, Azar Foundation, Capital International, TerraWatu, Weily Tribe.
- **Volunteer and forum pages:** Projects Overland "Orphanages in Arusha", the TripAdvisor forum thread, abroaderview (orphanage not named), and oneworld365 (LOHADA).

## Seeds from the brief

| Seed | Outcome |
|---|---|
| Emayani vulnerable people's center | OSM node 6222938386, office=ngo, Chandama Ave, **Sombetini** (not Sakina). Nothing else found; the link to Emayani Foundation (a women's business NGO) is not established. Recorded as unverified. |
| Arusha Children's Trust | Small volunteer-run educational charity (since 1999) supporting a Maasai kindergarten at Olmuringiringa. Last dated activity Dec 2021. Recorded as a funder (needs_review). The newsletter's child and family details were deliberately left out. |
| Faraja Orphanage Children's Home | At **Shangarai (Meru)**, outside slice A. Old domain is dead and the new site does not render, so facts rest on search snippets. Recorded as unverified. |
| "Arusha Children's home" (takesawholevillagekids) | Facebook login wall; only the name and "Arusha" are visible. Recorded as unverified. |
| Neema House | neemahouse.org is in **Geita** (discarded). The Arusha home is **Neema Village** (formerly Neema House Arusha), about 13 acres at **Moivaro**, inside Arusha Municipal. Recorded as verified. |
| SOS Children's Village Arusha | About 13 km from the centre on the Nairobi highway (probably Arusha DC). Runs its own kindergarten and school. Recorded as verified, outside slice A. |
| Peace House | A Christian co-ed boarding **secondary school** (opened 2007 for AIDS orphans), now owned by ELCT Northern Central Diocese. The US founder, Peace House Africa, has had its tax exemption revoked. Recorded as out of scope, plus a historical funder record. |

## Institutions recorded

**In Arusha City (slice A):**
- Ujamaa Children's Home (Njiro)
- Malaika Children's Friends (Moshono)
- Samaritan Village (Moshono)
- Tumaini For Africa (near Njiro Road)
- Neema Village (Moivaro)
- Huruma Vision / Huruma Children's Trust (Muriet, Kwa Mrombo)
- LOHADA / Camp Joshua (Unga Ltd)
- Emusoi Centre (originally Sakina)
- Emayani centre (Sombetini)
- Jitihada school (Themi; out of scope)
- GP-COSU (central Arusha)

**In "Arusha", ward unknown:**
- Ummu Aisha Orphanage Center (Kirika 'B', Simba Trucking; may be outside the city)
- Karim Children's Care Centre
- Bethlehem Center for Children
- New Paradiso Orphanage
- Arusha Children's Home (FB)
- Good Hope Orphanage (historical)
- Tumaini House (YWAM)
- WOW Tanzania
- Connects Autism Tanzania
- Big Future Foundation
- WEHAF (Mtaa wa Jaluo)

**Outside slice A but within or near the catchment, recorded briefly:**
- SOS CV Arusha
- Canaan Children's Center (Kisongo)
- Shalom Center (Kisongo; unverified complaint thread)
- Hope Center (Ngaramtoni)
- The Plaster House (Ngaramtoni/Olmotonyi)
- Faraja (Shangarai)
- Christ Hope Orphanage (Kigongoni Road; probably Shangarai)
- Fruitful Orphanage (Duluti)
- Tumaini Children's Foundation (Usa River; snippet only)
- St Joseph's Orphanage (Kiserian)
- Enjivai (Kambi ya Chupa; out of scope as a day nursery)
- Small Steps for Compassion (Mt Meru region)
- One Heart Source (outside Arusha)
- Halima Orphanage Center (Moshi)
- Peace House Secondary School

**Funders:**
- Love Our Tanzania Family
- Love for the Least
- Kesho
- WATOYO Tanzania e.V.
- Read With Me Arusha
- Heart for Africa (UK 1173027)
- Capital International (corporate CSR)
- TerraWatu
- Imaniworld
- Weily Tribe Foundation
- Arusha Children's Trust
- Peace House Africa (historical)

## Blocked or failed sources

- **Facebook** (login wall, page title only): takesawholevillagekids, becechi, Huruma Orphanage Arusha.
- **HTTP 403:**
  - UK Charity Commission register (the old URL redirect drops the charity number, and the portlet URL returns 403). As a result, UK income for Ujamaa (1150850) and Heart for Africa (1173027) was not captured.
  - Cybo, GlobalGiving, JamiiForums (Shalom thread), excursionmania (Amani Children's Home).
- **Timeouts:** ACNC profile for Hands In For Huruma; Overpass (twice).
- **Dead or unresolvable domains:** sos-childrensvillages.or.tz, enjivaiorphanage.org, stjosephorphanage.co.tz, goodhopeorphanage.org, farajaorphanagechildrenshome.org, wamisionariwakatoliki.or.tz, www.plasterhouse.org (theplasterhouse.org works), cradleoflovebabyhome.org (guessed URL; nothing found).
- **TLS errors:** ujamaachildren.com (the .org site works), mkombozi.org.
- **JavaScript-only pages** (no usable content): arushacc.go.tz, ubungomc.go.tz, farajaorphanage.org, oneheartsource.org (navigation only), mapy.com.
- **404:** ieoafrica.org Christ Hope page.
- **ACT 2019 newsletter PDF:** WebFetch returned binary, so I extracted the text locally with pypdf. Only organisation-level facts were used.

## Discarded or unconfirmed (no record written)

- **Outside the catchment:**
  - Neema House (Geita)
  - Children Concern Foundation (Mto wa Mbu)
  - Le Baos Kids Foundation (Iringa)
  - Step By Step / Mafiri (Morogoro)
  - Bahati Trust (Dar es Salaam)
  - Ilula Orphan Program (Kilolo)
  - Huruma Centre (Iringa)
  - Huruma Children's Home (Ubungo)
  - Hope for Huruma and Africa Mission Huruma (Kenya)
  - Tumaini Africa (DR Congo)
  - Kwetu Faraja (Mwanza)
- **Not a match:**
  - Ummah Charity: orphan programme is in Indonesia, Mauritania and Togo.
  - Emayani Foundation: women's business training.
  - Bethsaida Girls Home: the SO Worldwide link redirects with no Tanzania information.
- **Directory-only names, not checked further:** Chakuwama Orphanage – Lukiza Foundation (no details; the name is known from Dar es Salaam), One Ummah Charity, Zara Charity (Moshi), Ace Africa (UK 1111283; Tanzania office not identified), Barath Foundation (Moshi), Get There Organisation (forum, about 10 years old), Stichting BabuBibi.
- **Unnamed or unidentified:**
  - The abroaderview placement: an orphanage in Arusha founded 2009, 25 children aged 4-15.
  - An "Umoja orphanage" in a Weily Tribe URL slug.
  - Hands In For Huruma Orphanage Inc (ACNC): not read because of the timeout.
- **Not welfare institutions:** NGOBase education entries (DOT, VSO, STEMM, Travel For Charity, Malengo, LESCOTA, Elimu Yetu, Forecasted Africa, HOPE WITH US, Kukua Pamoja, YEP, Tanzania ECD Network).

## Known gaps and items to confirm

1. The ward-level sweep and the street-children, baby-home and "makao ya watoto" searches were not run (budget). No street-children centre inside the city has been found yet.
2. **Huruma merge.** Huruma Vision (Muriet, 2026 press), Huruma Children's Trust Centre (Morombo, 2015), and the TerraWatu, Capital International, Imaniworld and Azar "Huruma" pages were merged into one record on name and place. This needs confirming.
3. **Samaritan Village email.** The site shows "samaritan" followed by a mailto link to "vo@gmail.com". The recorded address, samaritanvo@gmail.com, needs verifying.
4. **Locations to confirm:** Tumaini For Africa (only an undated blog), Ummu Aisha (Kirika 'B'), Christ Hope (Kigongoni Road: Shangarai or elsewhere), Neema Village's exact campus, the Ujamaa coordinates (decoded from a Cybo snippet), Emusoi's current site, and Peace House School (Arusha Mjini vs 15 km along the Dodoma road).
5. **No own contacts found** for Tumaini For Africa (only the funder), Karim, Bethlehem, New Paradiso, GP-COSU, Tumaini House (YWAM Arusha), Huruma (no website) and Read With Me Arusha.
6. **Foreign-register financials were not captured** (UK register blocked; GuideStar hides revenue).
7. **Government registers were not accessed.** These are the Department of Social Welfare list of registered children's homes and the council social-welfare pages, which render only with JavaScript. A registered-homes list would be the best way to close the coverage gap.
