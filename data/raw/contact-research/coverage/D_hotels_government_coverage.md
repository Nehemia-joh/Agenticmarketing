# Slice D coverage log: hotels (master) and local government offices

Agent D, 23 September 2026. Output: `data/raw/contact-research/search_D_hotels_government_2026-09-23.jsonl` (93 records: 74 hotels, 19 government offices).

## Summary

| Part | Organisations | found | partial | not_found | blocked | WebSearch used |
|---|---|---|---|---|---|---|
| 1 Hotels (`db: master`) | 74 | 24 | 25 | 25 | 0 | 25 of 25 |
| 2 Government (`db: government`) | 19 | 10 | 2 | 7 | 0 | 10 of 10 |
| **Total** | **93** | **34** | **27** | **32** | **0** | **35 of 35** |

- Every organisation in the slice was attempted; none was left unreached. `not_found` means no contact route was found, not that the organisation was skipped.
- Status meanings: `found` means an e-mail or phone from the organisation's own site, its own document, or an official or association list, with identity confirmed. `partial` means some contact-profile data (address, social page, snippet-only or dated numbers) or an uncertain identity. `not_found` means nothing usable.
- No organisation was wholly blocked. Blocked or unreadable sources are listed below.

## Method notes

- **Search budget.** Searches were numbered Q1/35 to Q35/35: Q1–Q25 for hotels, Q26–Q35 for government. From Q5 onwards, most hotel queries combined two to four exact names with `OR` to cover the 74 hotels within 25 calls. The search tool sometimes ran one sub-search per name (Q5–Q8, Q10, Q16, Q21) and sometimes a single mixed search (Q9, Q11, Q12, Q15, Q17 and others), so some names got weaker coverage. Each record's `searches_used` counts every search that covered it; shared searches are therefore counted more than once, and the true total is 35.
- **No searches through fetch.** WebFetch was used only for organisations' own pages, official documents, directory entries surfaced by searches, and a few guessed official domains before the budget ran out. After Q35, only URLs already in hand were fetched.
- **Government letterheads (no searches).** Council and regional attachment URLs were taken from the public-API capture already in the repository (`data/raw/government-research/council_sites/`, `runtime/government/arusha-government-2026-09/http-cache`).
  - 24 official PDFs and one DOCX were downloaded to the session scratchpad by a paced script (at least 2.5 s per host). The 24 include the UNDP-hosted Kilimanjaro guide. None was written to the repository.
  - The ACHPR list PDF came through WebFetch as binary and was parsed locally.
  - Scanned letterheads were rendered to images and read visually.
  - The public GWF CORE `/api/footer` endpoint, which `research-rate-limits.md` names as the supported route, was fetched for Moshi DC and Moshi MC.
  - CMS editor names and e-mails in the cache, and applicants' details in interview lists, were ignored and not recorded. Officials' names printed on letters were not recorded; office titles only.
- **ACHPR hotel list.** Q10 surfaced an official list, *List of hotels vetted by the Govt of Tanzania and ACHPR jointly* (African Commission on Human and Peoples' Rights, 77th session, Arusha, September 2023). It gave booking contacts for 14 hotels in this slice. Its data are three years old and are flagged as such in each record. Two named contacts are on personal webmail (Senator Hotel, Stereo Hotel) and are labelled `risky`. A third personal webmail address (Palace Hotel) was deliberately not recorded.

## Search log

| # | Part | Query (abridged) | Outcome |
|---|---|---|---|
| Q1/35 | Hotels | "Ilboru Safari Lodge" Arusha contact | Official site ilborusafarilodge.net: contact page fetched (phone, e-mails, P.O. Box). Found. |
| Q2/35 | Hotels | "Citylink Hotel" Arusha | citylinkhotel.co.tz contact page fetched (City Link Pentagon Hotel). Found. |
| Q3/35 | Hotels | "Saruni River Lodge" Arusha | Booking listings and a Facebook page only; address from HotelFriend. Partial. |
| Q4/35 | Hotels | "Makeseni Lodge" Usa River Arusha | Booking listings only (four-room guest house). Not found. |
| Q5/35 | Hotels | Tanzanite City Park Lodge / La Bella Luna / Serengeti Villa | La Bella Luna from the 123tanzania directory (partial); the others not found. Also surfaced the Airport Planet Lodge and Arusha Serena URLs. |
| Q6/35 | Hotels | Gran Melia / Mount Meru Game Lodge / Club Afriko / Impala | Gran Melia via Wetu brochure and TATO (melia.com 403). MMGL official site and impressum. Klub Afriko via Finder Africa (partial). Impala closed in 2019 per Wikipedia (partial). |
| Q7/35 | Hotels | Mango B&B / Mzunguu's / Moon Shine / L'Oasis | Booking listings only. L'Oasis P.O. Box via HotelFriend (partial); the others not found. |
| Q8/35 | Hotels | Bay Leaf / Tulia / Le Jacaranda / Charity Hotel | Tulia Retreat via Tulia Hotel Group contact page (found). Charity Hotel official contact page (found). Le Jacaranda via Tanzapages 2012 (partial). Bay Leaf: Facebook only (partial). |
| Q9/35 | Hotels | East African / Freedom Lodge / Ahadi Lodge / Kibo Palace | Not split. Kibo Palace official contact page (found). Ahadi: location only. Freedom: nothing. |
| Q10/35 | Hotels | Four Points (Arusha Hotel) / East African / Naura Springs / New Safari | Four ways. Surfaced the ACHPR 2023 hotel list, which resolved Arusha Hotel, New Safari, Palace, Premier Palace, Briston, Graceland, Silver Palm, Senator, Natron Palace and Stereo. East African via an undated ATA page (partial). Naura Springs' domain has been taken over (partial). |
| Q11/35 | Hotels | Naaz / Snow Crest / Jevas / Davos | Arusha Naaz official contact page (found). Jevas address only (partial). Snow Crest and Davos: nothing. |
| Q12/35 | Hotels | Dik Dik / Ngare Sero / Ngurdoto / Meru View | Not split. Dik Dik official-site snippet only; the site reset the connection (partial). |
| Q13/35 | Hotels | Ngurdoto / Ngare Sero | Ngare Sero official contact page (found). Ngurdoto: nothing. |
| Q14/35 | Hotels | Ngurdoto Mountain Lodge official website | Phones from a directory summary only; no official site (partial). |
| Q15/35 | Hotels | Pallsons / Aquiline / Arusha Tourist Inn | Weak. Arusha Tourist Inn phone (snippet) and address (partial); Aquiline street only (partial, identity uncertain); Pallsons nothing. |
| Q16/35 | Hotels | Olasiti Lodge / Kahawa House | Tanganyika Wilderness Camps site: Kahawa House found. Olasiti appears to be its former name (partial, identity uncertain). |
| Q17/35 | Hotels | Golden Rose / African Grand / Forest Hill | Golden Rose via 2012 Tanzapages and an old site (partial, identity uncertain); the others not found. |
| Q18/35 | Hotels | Meru View / Twiga / Mountain Village | Meru View address and box from a snippet (partial); Twiga nothing; Mountain Village mapped to the Arusha Serena at Lake Duluti (partial, identity uncertain). |
| Q19/35 | Hotels | Weru Weru / Boma Masai Garden / Royal Hotel | Weru Weru official contact page (found); Boma Masai Gardens site renders in JavaScript only (partial); Royal Hotel nothing. |
| Q20/35 | Hotels | Fun Retreat / Njiro Ebenezer / Njiro Legacy | Fun Retreat via TATO member page (found); Njiro Ebenezer Instagram only (partial); Njiro Legacy nothing. |
| Q21/35 | Hotels | Pamoja Expedition Lodge / Monjes Tours | Pamoja address only (partial); Monjes listings only (not found). |
| Q22/35 | Hotels | Saleka GH / Green Leaf Lodge / Nature Tree Lodge | Nothing for any of the three. |
| Q23/35 | Hotels | Settlers Executive Inn / New Annex / GMV Lodge | New Annex address only (partial); the others not found. |
| Q24/35 | Hotels | AM Hotel / Rich Hotel / 7 11 Hotel / White House | Listings only; not found. |
| Q25/35 | Hotels | Snow Crest / Pallsons / Davos (retry) | Snow Crest location only (partial); the others not found. **Hotel budget spent.** |
| Q26/35 | Government | Simanjiro DC "S.L.P" barua pepe | Council's old 'othercontacts' snippet (ded@, P.O. Box 9596, mobile); page now a JavaScript shell (partial). |
| Q27/35 | Government | Manyara Regional Secretariat S.L.P / ras@ | P.O. Box 310 Babati from the old 'othercontacts' snippet. |
| Q28/35 | Government | DC offices Hai/Siha/Moshi (kilimanjaro.go.tz only) | Old district page URL only; no DC office contacts. Regional hall-booking phone 027 275 8248. |
| Q29/35 | Government | Kilimanjaro Region Investment Guide (key contacts) | UNDP-hosted 2018 guide read: Regional Secretariat rows confirmed; no DC office section. |
| Q30/35 | Government | DC offices Arumeru/Arusha/Monduli (Swahili) | Only officials' names (not recorded) and old sub-site URLs now in JavaScript. |
| Q31/35 | Government | DC offices Hai/Siha/Moshi (Swahili) | Summary misattributed council and regional addresses; nothing recorded. |
| Q32/35 | Government | DC offices Arumeru/Monduli/Simanjiro (government domains only) | Confirmed 'S.L.P 3050 ARUSHA' for the Regional Secretariat; no DC office contacts. |
| Q33/35 | Government | "ras@manyara.go.tz" | No page uses it; not recorded. |
| Q34/35 | Government | "District Commissioner's Office" ... "P.O. Box" (English) | News items naming officials only; nothing recorded. |
| Q35/35 | Government | Manyara "Ofisi ya Mkuu wa Mkoa" S.L.P 310 | Led to the NBS offices directory (Regional Commissioner building addresses for Manyara, Arusha and Kilimanjaro) and the region's Facebook page. **Budget spent.** |

## Deterministic sources used (no search)

- **Council and regional letterheads**, fetched from the councils' own attachment store (`/minio/<host>/attachments/...`):
  - Arusha CC: public notice on group loans, August 2026.
  - Arusha DC: 'KERO' notice footer, March 2026, and job advert, April 2026.
  - Meru DC: council-meeting notice, February 2026.
  - Hai DC: loans notice, March 2026.
  - Siha DC: contract-jobs advert, September 2026.
  - Moshi DC: loans notice, April 2026.
  - Moshi MC: temporary-jobs advert, August 2026.
  - Monduli DC: loans notice, March 2026.
  - Kilimanjaro Regional Secretariat: Client Service Charter, February 2025.
  - Simanjiro DC: Strategic Plan 2026/27–2030/31.
  - Arusha Regional Secretariat: Region Investment Guide on arusha.go.tz (data to 2020).
- **GWF CORE API footers:** `moshidc.go.tz/api/footer`, `moshimc.go.tz/api/footer`.
- **Hotels fetched directly** from known or likely official domains: Onsea House, Moivaro, The African Tulip (redirected to .co.tz), and the sites of hotels named in the ACHPR list (Palace Hotel, Graceland, Natron Palace, Silver Palm, Premier Palace).

## Blocked, broken or unreadable sources

- **HTTP 403 (not retried):** melia.com; marriott.com (Retry-After 28800); travelweekly.com; hotel.com.au; hotelcontact.net.
- **Bot-verification page:** tuliahotelandspa.com. The group site tuliahotelgroup.com was used instead.
- **Connection failures:**
  - dikdik.ch: connection reset on three attempts.
  - impalahotel.com: socket closed.
  - funretreat.com: TLS handshake failure.
  - ilborusafarilodge.com: HTTP 526. The current site is ilborusafarilodge.net.
  - meru-view-lodge.de: certificate for another host.
  - goldenrose.20m.com: connection refused.
  - old.tamisemi.go.tz: HTTPS refused and HTTP timed out.
- **Server errors:** tanzania1.com (500), amimagazine.global (405), vymaps.com (404), calabashadventures.com (404), unitedrepublicoftanzania.com (404).
- **Pages that give nothing to automated reading:**
  - newsafarihotel.com: home page over 10 MB, and /contact/ returns 404.
  - premierpalace-hotel.com and bomamasaigardens.com: render in JavaScript.
  - silverpalmhotel.com: maintenance page.
- **Domains that no longer resolve:** eastafricanhotel.com, thearushahotel.com. Guessed domains that do not exist: kibopalacehotels.com, mountmerugamelodge.com, thebayleafhotel.com, snowcresthotel.com, ngurdotomountainlodge.com.
- **Domain taken over:** nauraspringshotel.com now serves unrelated adult-service content. Do not use `info@nauraspringshotel.com`.
- **Council and regional sites:** JavaScript shells, including the old `/othercontacts` and district sub-pages. The GWF API has no district-office pages: `kilimanjaro.go.tz/api/pages/slug/hai-district` and `manyara.go.tz/api/pages/slug/simanjiro` return 404.
- **Facebook, Instagram and X pages** were recorded from search results or the organisations' own sites only, and were never read.

## Data-quality warnings for the coordinator

1. **Stale data.** All ACHPR-list contacts date from September 2023, and the Tanzapages entries (Le Jacaranda, Golden Rose, Impala) from 2012. Treat them as leads to verify.
2. **Impala Hotel** closed in 2019 and was reportedly sold and due to reopen in 2025. No current contact is recorded.
3. **Conflicting list rows.** The ACHPR row for 'City Link' copies the Premier Palace contact (P.O. Box 674, same mobile), which conflicts with City Link's own site (P.O. Box 448). The row was not used for Citylink.
4. **Possible duplicate.** Olasiti Lodge (O8b477ba37c7a) looks like the former name of Kahawa House (O9a4c9b2e7af9); check for a duplicate in the master.
5. **Uncertain identities.**
   - Mountain Village Hotel is recorded against the Arusha Serena at Lake Duluti.
   - Golden Rose: the OpenStreetMap distance fits the downtown hotel poorly.
   - Aquiline appears as 'New Hotel Aquiline'.
   - Boma Masai Garden's site is unreadable.
6. **Snippet-only facts** (`fetched: false`) need verification: Dik Dik (all contacts), Ngurdoto (phones), Simanjiro DC (ded@, mobile, P.O. Box 9596), Manyara Regional Secretariat (P.O. Box 310), Kahawa House (info@twctanzania.com), Arusha Tourist Inn phone, and Four Points street address.
7. **Printing errors in sources, handled:**
   - Simanjiro strategic plan prints `ded@sdc.ac.tz`: not recorded.
   - Moshi MC website footer prints `274371/4`: the letterhead's 275 4371/4 is used.
   - The 2018 Kilimanjaro guide has wrong e-mails for Hai and Moshi DC: not used.
   - Meru's phone is missing a digit in the Arusha guide: the 2026 notice is used.
8. **Arusha DC.** Its 2026 footer gives a mobile-range office line (0736 500 476); the landline 027 250 2737 comes from the older guide.

## Organisations not reached

None. Every organisation in the slice was attempted. These remain unresolved (`not_found`):

- **Hotels (25):**
  - Makeseni Lodge
  - Tanzanite City Park Lodge
  - Serengeti Villa
  - Mango Bed & Breakfast
  - Mzunguu's hotel, bar & restaurant
  - Moon Shine Hotel
  - Freedom Lodge
  - Ahadi Lodge
  - Davos Hotel
  - Hotel Pallsons
  - African Grand Hotel
  - Forest Hill Hotel
  - Twiga Lodge
  - Royal Hotel
  - Njiro Legacy
  - Monjes Tours & Lodges Office
  - Saleka Guest House
  - Green leaf lodge
  - Nature Tree Lodge
  - Sttlers executive Inn
  - GMV Lodge
  - AM Hotel
  - 7 11 Hotel
  - Rich Hotel
  - White House
- **Government (7):** the District Commissioner's offices of Arusha, Arumeru, Hai, Siha, Moshi, Monduli and Simanjiro. None of the offices publishes contact details that could be found. Their records point to the parent Regional Secretariat's route in the meantime.

## Next-run priorities

1. **District Commissioner offices.** Ask each Regional Secretariat (RAS e-mail or phone) for the DC office addresses. Alternatively, with the user's go-ahead, have the coordinator read the regional sites' district pages in the browser pane.
2. **Manyara Regional Secretariat.** Find a phone and e-mail, from a Manyara letterhead or its client service charter if published.
3. **Ngurdoto Mountain Lodge.** Find its official contact. It is a large employer about 3 km from the Usa River campus.
4. **Verify snippet-only facts** and the 2023 ACHPR contacts before outreach.
5. **Unresolved hotels.** Most are small guest houses with no web presence. A field visit or phone directory is more likely to work than web search.
