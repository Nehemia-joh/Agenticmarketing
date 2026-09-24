# Coverage log: wave 5, search slice A (2026-09-24)

Slice: `runtime/contacts/slices/wave5_search_a.json`: 45 company-master organisations, nearest first (1.5 km to 447.7 km, then 27 with no distance). Every one already had a published route; each needed a named decision-maker (owner, founder, managing or executive director, general manager, head, HR). Most are TATO members or affiliates; 9 of those labelled "Safari / tour operator" are other kinds of business, and one record is a savings cooperative's mill (see Warnings).
Search allowance: 37 WebSearch calls, all used (Q1/37 to Q37/37). No search was refused by the session cap. After Q37 only URLs already in hand were fetched.
Output: `data/raw/contact-research/search_wave5_search_a_2026-09-23.jsonl` (45 records, one per organisation, in slice order). Scratch: `runtime/contacts/agents/wave5_search_a/`.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 45 |
| Researched (one JSONL line each) | 45 |
| found | 18 |
| partial | 20 |
| not_found | 7 (Extraordinary Experience, Samaki Feeds and Fingerlings, Top of Africa Treks, Delaware Luxury Safari, Ibhanilfa Safaris, The First Lady Tour Safari, trekkingandsafariadventures) |
| blocked | 0 (every own-site block was covered by another source or left the record not_found; all blocks are listed below) |
| Not reached (no line written) | 0 |
| Identity uncertain | 3 (Paradise And Wilderness Tours, Kipepeo, Tcp Saccos) |
| WebSearch calls used | 37 / 37 (14 records used none, 25 used one, 6 used two; 2 searches each served a pair of twin records, counted on the nearer twin) |
| Named people recorded | 52 in 25 organisations, all `medium` |
| Full names read on fetched pages | 42 in 20 records: the 18 `found` records (two twin pairs among them) and 2 records whose identity is uncertain (Paradise And Wilderness Tours, Kipepeo) |
| First name only | 9 (Old Explorer 5, Miles to Smile 2, Lomo 1, RA Expeditions 1): the person filter will drop them |
| Snippet only | 1 (Sabrahm Safaris' founder: the team page now answers HTTP 404) |

Status rules (the same as wave 4, since the gap was a decision-maker, not a route):
- `found`: identity confirmed, and at least one named decision-maker read on a fetched page. Allowed pages were the organisation's own site or legal notice, its own press release or newsletter, its own text on an operator directory (SafariBookings, ATTA exhibitor listing), TATO's pages, or a parent company's page.
- `partial`: profile data confirmed or added (routes, addresses, size, socials), but no decision-maker on a fetched page (none named, snippet only, or first name only), or identity uncertain.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the only sources refused automated reading (none this wave).

Not used as sources for people: data brokers (ZoomInfo, RocketReach), personal LinkedIn profiles, client reviews on TripAdvisor or operator directories, and newspaper articles. Where a search summary named someone from such a page, the record says so without the name.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/37 | "Gold Crest Hotel" Arusha general manager | Gold Crest Hotel | A current GM is named only by ZoomInfo-type pages, an older one only in 2017-19 review replies: neither used. TanzaJob recruiter page HTTP 403. Hotel and brand pages name nobody |
| Q2/37 | "OKKA House" Arusha cafe | OKKA House | Instagram @okka_house, TripAdvisor 'Okka Cafe Bakery', TikTok, TATO; nobody named |
| Q3/37 | "Marangu Forex Bureau" Arusha director | Marangu forex bureau | Own site (branches read without a search), Instagram; a person appears only on a personal LinkedIn profile (not used) |
| Q4/37 | "Extraordinary Experience Ltd" Arusha Tanzania | Extraordinary Experience Ltd | TATO only; other hits are different companies |
| Q5/37 | "Lomo Tanzania Safaris" Arusha founder | Lomo Tanzania Safari | SafariBookings (fetched): 5-10 employees, founded 2014. Own about page names the founder by first name only |
| Q6/37 | "SafariHQ" Arusha Tanzania safari company | Safari – HQ | Own site HTTP 403. ATTA directory hides contacts behind a login, but the company's own ATTA exhibitor listing (fetched) names its Sales Director with a mobile |
| Q7/37 | "Legendary Expeditions" Arusha managing director | Legendary Expeditions (both records) | TATO board page (fetched): "He is the CEO of Legendary Expeditions". A 2019 ATTA item on a sales director is too old to use; RocketReach not used |
| Q8/37 | "Samaki Feeds and Fingerlings" Arusha | Samaki Feeds and Fingerlings | No page for this business; Bongo Samaki (bongofish.net, fetched) works from Dar es Salaam and Kipili, so it is a different company |
| Q9/37 | "Regional Air Services" Arusha Tanzania managing director | Regional Air Head Office | Own team page exists but answers HTTP 403. ATTA entry and 2026 member news (fetched) name nobody. Snippet-only inbox and phone with no identifiable source: not recorded |
| Q10/37 | "Top of Africa Treks and Safaris" Arusha | Top Of Africa Treks and Safaris LTD | Nothing for this company. Own site HTTP 500 on every page |
| Q11/37 | "Gazelle Adventures" Tanzania Moshi safari | Gazelle Adventures (both records) | Own site (fetched): "Established in 2012 by Christopher S. Kilawila"; mobile matches OpenStreetMap. SafariBookings: 20-50 employees, NSSF Building, Moshi |
| Q12/37 | "Miles to Smile" Tanzania Kilimanjaro company founder | Miles To Smile Company Ltd | SafariBookings (fetched): "Magnus and Julie - Owners" (first names only); 1-5 employees, founded 2022. Own site blocks (HTTP 403) |
| Q13/37 | "Tamega Adventure" Safaris Moshi | Tamega Adventure & Safaris Ltd | TATO only. The person named in both inboxes has no published role: not recorded. Company domain does not resolve |
| Q14/37 | "Delaware Luxury Safari" Tanzania "Safa Safaris" | Delaware Luxury Safari Limited | Brand site safasafaris.com HTTP 500 and TLS timeout (www. also 500); TATO only |
| Q15/37 | "Ibhanilfa Safaris" Tanzania | Ibhanilfa Safaris & Tours Limited | Only the company's own pages, all HTTP 500 to the reader |
| Q16/37 | "Paradise and Wilderness" Tanzania tours director | Paradise And Wilderness Tours Ltd | The TATO-listed site africa-safari.com (fetched) is the Paradise & Wilderness group's safari brand and names its group director and owner with a work inbox; identity with the Dar es Salaam TATO record uncertain |
| Q17/37 | "Manya Luxury Camps" Serengeti "Fantasy Adventures" | FANTASY ADVENTURES LIMITED | Own camp site and booking sites; nobody named |
| Q18/37 | "RA Expeditions Limited" OR "RA Safaris" Arusha owner managing director | Ra Expeditions | SafariBookings (fetched): 20-50 employees, founded 2004. A full name for the owner-MD traces only to ZoomInfo or reviews: not used. Own site gives first name only |
| Q19/37 | "Sabrahm Safaris" Arusha founder | Sabrahm Safaris | Founder named only in the summary of the own site's former team page, now HTTP 404: snippet only. Personal LinkedIn not used |
| Q20/37 | "Sali Tanzania Safaris" Kilimanjaro Zanzibar tour operator | Sali Safaris | TripAdvisor, Facebook, TATO; no website, nobody named |
| Q21/37 | "Summits Africa" Arusha founder director Kilimanjaro outfitter | Summits Africa | Nobody named (see Q34) |
| Q22/37 | "First Lady Tour Safari" Tanzania | The First Lady Tour Safari | TATO only. firstladysafari.com (fetched) has a different phone and inbox: not the same company, not used |
| Q23/37 | "Wilderness Collection" Ngorongoro Arusha Tanesco Road owner | Wilderness Collection | Own site, ATTA, TripAdvisor; the only person named is its UK representative at another firm (not recorded) |
| Q24/37 | "Rudra Distributors" Arusha Njiro | Rudra distributors | One-page own site and TATO; an Indian namesake on LinkedIn is unrelated |
| Q25/37 | "African Queen Adventures" Arusha owner founder | African Queen Adventure | SafariBookings (fetched): 20-50 employees, founded 2006, P.O. Box 13602. Trade-show exhibitor page (fetched): no names |
| Q26/37 | "Serengeti Safari Marathon" organiser director Arusha | SERENGETI SAFARI MARATHON | A founder-director is named only in newspaper articles (not an allowed source); own site names only the organising committee |
| Q27/37 | "Trekking and Safari Adventures" Tanzania Moshi | trekkingandsafariadventures | Nothing for this business; its domain no longer resolves |
| Q28/37 | "Kipepeo Tours" Arusha Tanzania | Kipepeo | Kipepeo Tours Ltd, central Arusha (SafariBookings, fetched: founder named, 10-20 employees); its phone differs from the mapped office, so identity uncertain. kipepeotours.com now redirects to a gambling site |
| Q29/37 | "TPC SACCOS" Moshi Kilimanjaro | Tcp Saccos Ltp Milling Machine | TCDC register of licensed SACCOS (snippet only; PDF not downloaded): TPC SACCOS LTD, P.O. Box 118 Moshi. No officers named |
| Q30/37 | "Tanzanian Pioneers" Arusha self-drive Land Rover | Tanzanian Pioneers | Own site only; imprint and privacy policy (fetched without a search) name no person |
| Q31/37 | "Arusha Coffee Lodge" "general manager" Elewana | Elewana Arusha Coffee Lodge (follow-up) | Elewana's own February 2020 newsletter (fetched) announces the lodge's general manager; December 2020 newsletter still calls her GM. Minor Hotels page (fetched) lists the lodge |
| Q32/37 | "Regional Air" Tanzania airline Arusha "managing director" OR CEO appointed | Regional Air Head Office (follow-up) | Other airlines only |
| Q33/37 | "Gold Crest Hotel" Arusha vacancy "human resource" | Gold Crest Hotel (follow-up) | No HR contact; snippets give 40 suites and a former name (East African All Suites) |
| Q34/37 | "Summits Africa" Tanzania "managing director" OR "operations director" Kilimanjaro | Summits Africa (follow-up) | The company's 2026 clean-up press release on the Tanzania High Commission (London) tourism site (fetched) quotes "Director Ake Lindstrom" |
| Q35/37 | "The Wilderness Collection" Tanzania "Crater's Edge" founder OR "managing director" | Wilderness Collection (follow-up) | Expert Africa's owner-supplied page (fetched) names nobody; RocketReach not used |
| Q36/37 | "Marangu Forex" bureau Tanzania "managing director" OR "general manager" OR "chief executive" | Marangu forex bureau (follow-up) | Nobody named |
| Q37/37 | "African Queen Adventures" Tanzania "managing director" OR "director" | African Queen Adventure (follow-up) | A managing director appears only on a personal LinkedIn profile: not used |

## Fetches without a search

All pages were read with `scripts/contacts/read_page.py` (polite cached reader: robots.txt checked for every host, one request at a time, at least 1.5 s apart per site, plus 1-2 s pauses between calls): 153 pages on 59 host names, plus TATO's sitemaps, and a robots.txt check per host. Pages the crawl had already cached were answered from the cache. The reader's responses were added to the shared cache `runtime/contacts/http-cache/`.

- **TATO:** robots.txt, sitemap index and the three portfolio sitemaps (to find profile URLs for the 14 records whose known source was only `https://tatotz.org/`), 34 member or affiliate profiles, and the Board of Directors page.
- **Named people read on pages already known before any search (15 organisations; 13 of them used no search):**
  - Aga Khan Health Services: the operator's Tanzania page lists its local leadership team (CEO, HR head and four more).
  - Top Nature Tanzania Safari: own about page (director with work inbox and mobile; US-based sales manager).
  - Basecamp Afromaxx: own Impressum (Geschäftsführerin) and about page (founder, 2004).
  - Shah Tours & Travels: welcome text on its TATO profile, signed by the managing director.
  - Claritas International: own leadership page (six partners and managers) and contact page (Arusha and Moshi offices).
  - African Horizons: company's own overview on its TATO profile (founder).
  - Old Explorer (Tanzania Explorer): own about page (first names only).
  - Elewana Arusha Coffee Lodge: Elewana Collection's contacts page (group staff); the lodge GM came later with Q31.
  - TGN Company: own about page (CEO and GM).
  - NBC Bank: the bank's own news page (managing director, in items dated to about 2022).
  - Easyota: own team page.
  - Victory Attorneys: own home page (three partners).
  - Laitolya Tours & Safaris: own team page (two directors).
  - Lomo and RA Expeditions: own about or team pages (first names only).
- **Other own sites read:** arusha.goldcresthotel.com and goldcresthotel.com/arusha, mfb.co.tz (branches), legendaryexpeditions.co.tz (legacy and contact), rasafaris.com (team, about, contact), sabrahmsafaris.com (about, contact), summits-africa.com (six pages), manyaluxurycamps.com (three pages), thewildernesscollection.com (three pages), rudradistributors.co.tz, africanqueenadventures.com (three pages), serengetisafarimarathon.or.tz (home, contacts, blog), tanzanian-pioneers.com (home, about, imprint, contact, privacy policy), gazelleadventures.com (home, profile, contact), claritas.co.tz (three pages), africa-safari.com and paradiseandwilderness.com (Paradise & Wilderness group), firstladysafari.com (ruled out), bongofish.net (ruled out).
- **Other allowed sources read:** ATTA member entries and member-supplied listings (SafariHQ, Regional Air, Wilderness Collection), SafariBookings operator profiles (Lomo, Gazelle, Miles to Smile, RA, African Queen, Kipepeo), YourAfricanSafari (RA), Expert Africa owner-supplied page (Crater's Edge), World Travel Show exhibitor page (African Queen), Minor Hotels' lodge page (Elewana), friedkin.com (renders only by script; empty).

## Blocked or unreadable sources

Not worked around in any case: no retries in a loop, no change of User-Agent, no browser, no archive copies, and no decoding of Cloudflare-protected email links.

- **HTTP 403 (block):**
  - safarihq.com (the crawl's http:// request on 2026-09-23 and one https:// request today)
  - www.regionaltanzania.com (the crawl's home page; one request today for /About-Us/team)
  - paradise-wilderness.com (one request)
  - www.tanzajob.com recruiter page for Gold Crest Hotel (one request)
  - Not requested again because the crawl was already refused: miles-to-smile.com, www.shah-tours.com
- **Login wall:** the ATTA member directory shows contacts only to logged-in members (SafariHQ, Regional Air, Wilderness Collection); nothing was attempted behind it.
- **Cloudflare email protection, not decoded:** agakhanhospitals.org (the Arusha polyclinic's inbox, already in the master), atta.travel (SafariHQ's Sales Director and reservations inboxes), www.minorhotels.com (Elewana).
- **Server errors:**
  - topafricatrek.com: HTTP 500 on the home, about-us and contact-us pages and on robots.txt (nothing was read, so no "robots.txt unreachable" flag arises)
  - ibhanilfasafaris.com: HTTP 500 on every page tried (the search engine indexes them, so it may be refusing automated readers)
  - safasafaris.com: HTTP 500, then a TLS handshake timeout; www.safasafaris.com HTTP 500
  - www.africanhorizons.com: HTTP 503 (as on the crawl)
  - serengetisafarimarathon.or.tz/about/: HTTP 500 (its home, contacts and blog pages were read)
- **Not found (HTTP 404):** sabrahmsafaris.com/our-team/ (the page the search indexed), arusha.goldcresthotel.com /explore and /contact (the site's own About Us and Contact links), afromaxx.com/?lang=en (the TATO link; the home page was read)
- **DNS failures:** claritasint.co.tz (the TATO-listed site; the firm's site is claritas.co.tz), www.africa-safari.com (the bare host resolves and was read), tamegasafaris.co.tz, trekkingandsafariadventures.com (www and bare)
- **Hijacked domain:** www.kipepeotours.com redirects to walitogel2d.com, an Indonesian lottery-gambling site; nothing used.
- **Files not downloaded:** Legendary Expeditions' annual report (a Google Drive download link on its legacy page); the TCDC register of licensed SACCOS (PDF; its search snippet is recorded as snippet only).
- **Not attempted by policy:** Facebook, Instagram, LinkedIn, X, TikTok and TripAdvisor pages (URLs recorded only as seen), data brokers.

## robots.txt disallows

None. Every page read came from a host whose robots.txt allowed it or answered 4xx (no rules: topnaturesafaris.com, www.tanzaniaexplorer.com, www.kipepeotours.com). The only unreadable robots.txt (topafricatrek.com, HTTP 500) belongs to a site none of whose pages could be read. No site in this slice needs the coordinator's browser pass for a robots.txt reason.

## Organisations not reached

None: all 45 have a record.

## Warnings

Review items the notes raise, and other points for a reviewer:
- **Possible duplicates:**
  - LEGENDARY EXPEDITIONS (MWIBA HOLDINGS LTD) (O7f949d75cae7) and Legendary Expeditions (O9790b08e6804): one TATO member.
  - Gazelle Adventures (Oba62dc5f713c) and Gazelle Adventures (O594144d2b0b9): one map point.
  - NBC Bank Tanzania (Ob2ec027a1fb7) and the master's National Bank of Commerce (NBC) (O6d705d505610).
  - Kipepeo (Obd0df41bdc7d) and Kipepeo (Of6951631ee8a, wave 4): one map point.
  - Miles To Smile Company Ltd (Oc2da1647a7e3) and Miles to Smile (O13fac71333a1, wave 4).
  - Aga Khan Health Services - Arusha (O502fd116053c) and The Aga Khan University Hospital (O4f3c31b53349, wave C): one polyclinic.
  - Paradise And Wilderness Tours Ltd (Dar es Salaam TATO profile) and TATO's 'PARADISE AND WILDERNESS LIMITED' (Arusha): probably one group.
- **Website gone or not working:** Top of Africa Treks (HTTP 500 everywhere), trekkingandsafariadventures (domain gone), Tamega (domain does not resolve; TATO says "under construction"), Safa Safaris / Delaware (HTTP 500), Ibhanilfa (HTTP 500), African Horizons (HTTP 503; profile text looks dated and its only phone is a US number), Claritas (TATO-listed domain gone; use claritas.co.tz).
- **Hijacked:** Kipepeo Tours' old domain (gambling redirect).
- **Location to check:** Dar es Salaam: Delaware Luxury Safari, Ibhanilfa, Paradise And Wilderness Tours, Fantasy Adventures (camp in the Serengeti), Old Explorer (with Zanzibar and South Africa outposts), Easyota, Victory Attorneys, NBC (head office; Arusha branches exist). Zanzibar/Kilimanjaro: Sali Safaris. Claritas is headquartered in Dar es Salaam but has Arusha and Moshi offices. Tanzanian Pioneers' base is in Arusha, its postal address in Dar es Salaam.
- **Segment wrong in the master:** 9 records labelled "Safari / tour operator" are TATO affiliates of other kinds: OKKA House (cafe and bakery), Marangu Forex Bureau (bureau de change), Claritas (audit and tax), TGN (fire-safety equipment), NBC (bank), Easyota (booking software), Rudra (food and drinks distributor), Victory Attorneys (law firm), Serengeti Safari Marathon (annual event). Tcp Saccos is a savings and credit cooperative's business (savings groups are normally reached through KINEFA).
- **Check before outreach:**
  - Laitolya: its founder is described in the past tense on the team page, so he was not recorded as a lead.
  - Elewana: the lodge GM's appointment dates from 2020.
  - NBC: the managing director is named in news items dated to about 2022.
  - SafariHQ's Sales Director and Easyota's team are sales-side contacts; SafariHQ's owner is not named.
  - Kipepeo, Paradise And Wilderness Tours and Tcp Saccos: identity uncertain.
- **Master data to fix:** in 14 records the TATO fields are shifted (the website field holds phones or text, the email field holds the website, the phone field holds a TATO category code such as 'TO/DMC/MAIN' or 'AFF'): Ra, Sabrahm, Sali, Summits Africa, First Lady, Wilderness Collection, TGN, NBC, Easyota, Rudra, Victory, Laitolya, African Queen, Serengeti Safari Marathon. In two more, a field carries TATO page text: Top Nature's email field (slogan after the address) and Tamega's website field ("under construction View Details").

## For the next run or the coordinator

- Browser check (the coordinator's decision; these are HTTP 403 blocks, not robots.txt rules): regionaltanzania.com/About-Us/team (the airline's own team page), safarihq.com/about-us/, www.shah-tours.com, miles-to-smile.com, paradise-wilderness.com.
- Legendary Expeditions' annual report (Google Drive link) may name more leaders, if the user approves a download.
- On the ground or by phone: Gold Crest Hotel's general manager and HR, OKKA House's owner, Marangu Forex Bureau's management, Summits Africa's HR (about 400 porters on its roster), Top of Africa Treks (website broken), Samaki Feeds and Fingerlings (no online presence).
