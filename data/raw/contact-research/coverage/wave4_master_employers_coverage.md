# Coverage log: wave 4, master employers (2026-09-23)

Slice: `runtime/contacts/slices/wave4_master_employers.json`: 45 company-master organisations, nearest first (0.5-2.3 km). Every one already had a published route; each needed a named decision-maker (owner, founder, managing or executive director, general manager, head, HR). Most are TATO members or affiliates; 16 of them are not tour operators at all (see Warnings).
Search allowance: 45 WebSearch calls, all used (Q1/45 to Q45/45). No search was refused by the session cap. After Q45 only URLs already in hand were fetched.
Output: `data/raw/contact-research/search_wave4_master_employers_2026-09-23.jsonl` (45 records, one per organisation). Scratch: `runtime/contacts/agents/wave4_master_employers/`.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 45 |
| Researched (one JSONL line each) | 45 |
| found | 11 |
| partial | 31 |
| not_found | 3 (R&D Polyclinic, Kipepeo, Meru Mountain Treks) |
| blocked | 0 (own-site blocks were all covered by another source; every block is listed below) |
| Not reached (no line written) | 0 |
| Identity uncertain | 2 (Kipepeo, Meru Mountain Treks; nothing from them is used) |
| WebSearch calls used | 45 / 45 (5 organisations needed none; 4 got a second search) |
| Named people recorded | 30 in 13 organisations, all `medium`; 29 read on fetched pages, 1 snippet-only (Nnko & Smith) |
| Kept by the person filter (`contact_lib.clean_person`) | 24 in 12 organisations, all decision-makers |
| Emails / phones not already in the master's fields | 19 / 37 |
| Website fields | 11 empty master fields filled; 6 differ from the master (review) |

Status rules for this wave (the gap was a decision-maker, not a route):
- `found`: identity confirmed, and at least one named decision-maker read on a fetched page. Allowed pages were the organisation's own site or report, an official register, TATO's pages, or the company's own text on an operator directory.
- `partial`: profile data confirmed or added (routes, addresses, size), but no decision-maker on a fetched page (none named, snippet-only, or first name only), or the organisation is outside the area.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the only sources refused automated reading (none this wave).

Person filter: 6 of the 30 entries will be dropped downstream. They are recorded exactly as published so that a person can decide:
- Arusha Technical College's Rector (already in the master) and two Deputy Rectors: "Rector" is not a filter role word. This is also why the college was in the slice.
- Kili Vikings' Operational Director and Teamwise's two Directors, who are published by first name only.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/45 | "Shidolya Tours" Arusha director | Shidolya Tours & Safaris | A managing director is named only on a personal LinkedIn profile and data-broker pages (ZoomInfo, RocketReach): not used. Also TATO, Facebook and TripAdvisor pages. Own sitemap has no team page |
| Q2/45 | "Gran Meliá Arusha" general manager | Gran Meliá Arusha | No manager named. LinkedIn company page, Facebook, Instagram; Cvent venue profile (fetched): Simeon Road, PO Box 1184, 23110; no staff |
| Q3/45 | "Africa VIP Travel" Arusha | Africa VIP Travel | Own About and Contact pages (HTTP 500 when fetched): director, plot address and phones in snippets. SafariGo operator profile (fetched) repeats the About text naming the director |
| Q4/45 | "Nnko & Smith Safaris" Arusha | Nnko & Smith Safaris | Snippet of affiliate Deeper Adventure LLC's About page names the director; its site could not be reached. Licence aggregators and ZoomInfo not used |
| Q5/45 | "Avinta Care" polyclinic Arusha | Avinta Care Specialized Polyclinic | MoH facility register PDF 121376-8 (fetched): operating since 2018-01-04, owner Kilimanjaro Fertility Institute, official phone 0789357077; no in-charge named |
| Q6/45 | "R&D Polyclinic" Arusha | R&D Polyclinic | Other polyclinics only. The Jubilee insurer's provider panel PDF (fetched) has no entry |
| Q7/45 | "Lemala Camps" managing director Tanzania | Grumeti Expeditions (Lemala Camps) | Lemala press release on Hospitality Net (fetched) names the CEO; Lemala's own 2026 report PDF (fetched) confirms her and the operating company, Grumeti Expeditions TZ Limited |
| Q8/45 | "St. Elizabeth Hospital" Arusha Ngarenaro | St. Elizabeth Hospital | Own site seha.co.tz in results, but the domain is NXDOMAIN. Snippets: owned by the Catholic Archdiocese of Arusha |
| Q9/45 | "Krisha African Safaris" Arusha founder | Krisha African Safaris | TATO Board of Directors page (fetched): "He is the CEO of Krisha African Safaris". TATO profile (fetched): phones, three inboxes. SafariBookings (fetched): 1-5 employees |
| Q10/45 | "Al-Anver" tents Arusha | Mega Tents (Al-Anver Outfitters) | Own contact page snippet: warehouse at Simba Safari Building, Njiro Road. Own site still over its bandwidth limit. ZoomInfo names not used |
| Q11/45 | "King Mart" Arusha Themi | King Mart | Pointed to the TATO profile already fetched, which names the two founders (2019) |
| Q12/45 | "Mama Africa Safaris" Arusha Kaloleni founder | Mama Africa Safaris | No founder named. SafariBookings (fetched): 1-5 employees, founded 2005. SafariGo (fetched): no names |
| Q13/45 | "Safarini Africa" Arusha Boma Road | Safarini Africa | TripAdvisor and TATO pages only; own site disallows all crawling |
| Q14/45 | "Travel Booking Guide Ltd" Arusha | Travel Booking Guide | SafariGo (fetched; no names), Bookmundi (HTTP 503), own pages behind Cloudflare. Snippet: office on Pangani Street |
| Q15/45 | "Alex Walker's Serian" founder Tanzania | Serian | Own Tanzania terms page (fetched): Alex Walker Safaris (TZ) Limited, P.O. Box 1232 Arusha. ATTA directory hides contacts behind a login; third-party "owner" pages not used |
| Q16/45 | "Kili Vikings" OR "Kilimanjaro Vikings" Arusha director Vincent | Kili Vikings | Own About page: "Charlie Richard ... leads Kili Vikings". SafariBookings (fetched): 10-20 employees. **This query included the Operational Director's published first name, which breaks the rule against searching a person's name; nothing beyond the company's own page was used** |
| Q17/45 | "Shaw Safaris" Arusha Tanzania | Shaw Safaris | SafariBookings (fetched): based at Twiga Lodge, Usa River. Owners named only in client reviews: not used |
| Q18/45 | "Anderson's African Adventures" Arusha | Anderson's African Adventures | Tanzania Pages listing (fetched; unclaimed, locked since 2012; not used), SafariBookings (no names), a review site marks it "(Deleted)" |
| Q19/45 | "Kilaweni" Usa River Arusha | Kilaweni | Facebook "Kilaweni Tours \| Usa River", TATO; no names |
| Q20/45 | "Kilimanjaro Outfitters Limited" Arusha | Kilimanjaro Outfitters | TATO; SafariBookings "Kilimanjaro Outfitters" (Moshi; identity uncertain, not used) |
| Q21/45 | "Kudu Safaris" Arusha Tanzania | Kudu Safaris | Working company site kudusafaris.net (fetched): Themi Industrial Area address, P.O. Box 378, phone, inbox; content looks stale |
| Q22/45 | "Kipepeo" Arusha "0755 753 576" OR "755753576" OR "+255 755 753 576" (the mapped office phone) | Kipepeo | A TripAdvisor "Kipepeo Tours Ltd" listing; the phone is not matched; unrelated Kipepeo businesses |
| Q23/45 | "Meru Mountain Treks" Arusha | Meru Mountain Treks & Safari | TripAdvisor listing only; merutreks.com now belongs to another operator's site |
| Q24/45 | "East African Voyage" Arusha director founder | East African Voyage | Company booking site eastafricavoyage.activitar.com (fetched) names the director. A data-broker entry naming someone else was not used |
| Q25/45 | "Bush 2 Beach" "African Footprint" Arusha | Bush 2 Beach | YourAfricanSafari profile (fetched): owners named only in a client review (not used). Snippet: based in Arusha since 2004, under The African Footprint Co Ltd |
| Q26/45 | "Utopia Safaris" Arusha AICC | Utopia Safaris | SafariBookings profile, company's own text (fetched): "founded by Exaud Marandu"; 10-20 employees |
| Q27/45 | "Miles to Smile" Tanzania safari Moshi Arusha | Miles to Smile | TripAdvisor and TATO only |
| Q28/45 | "African Galleria" Tanzania Karatu OR "Mto wa Mbu" | African Galleria | Live site africangalleria.com (fetched): Karambacha Road, Karatu; phone; group inbox. Founded by a family, no individual named |
| Q29/45 | "Safari Plus" aviation Tanzania managing director | Safari Plus | Parent ASB Hospitality portfolio page (fetched): no names. A trade-magazine interview was not used |
| Q30/45 | "Tanmanagement Insurance Brokers" Arusha | TanManagement (JW Seagon) | Own site tm.co.tz (fetched management and contact pages): leadership and Arusha offices |
| Q31/45 | "Lashku Forex Bureau" Arusha | Lashku Forex Bureau | TATO pages only. The Bank of Tanzania register (fetched without a search) confirms the licence and address |
| Q32/45 | "Kitamu" Arusha Haile Selassie Road | Kitamu Africa | Kitamu House restaurant complex at 64 Haile Selassie Road (snippets). Own and sister sites all disallow crawling |
| Q33/45 | "Safari Wholesalers" Arusha Olasiti | Safari Wholesalers and Retailers | Own site safariwholesalers.com (fetched): "Coming Soon", Olasiti, hours |
| Q34/45 | "House of Gems" Arusha "Beautiful African Gemstones" | House of Gems | TATO profile (fetched): address, three phones, two inboxes |
| Q35/45 | "NSK Hospital" Arusha | NSK Hospitals | Own site nskhospitals.co.tz (fetched; no names) and MoH register PDF 111486-7 (fetched): regional-level hospital, official phone |
| Q36/45 | "Tanzania Federation of Tourism Service Providers" chairman OR secretary Arusha | TFTSP | TATO only; no officers named |
| Q37/45 | "Teamwise Tanzania Travel" Arusha | Teamwise | SafariBookings (fetched): 10-20 employees, founded 2017. teamwiseafrica.com About page failed DNS |
| Q38/45 | "Vehicle Pharmacy" Arusha spare parts | Vehicle Pharmacy | Toyota parts supplier; no names |
| Q39/45 | "Mkizughuno" Arusha | Mkizughuno | TATO pages only |
| Q40/45 | "Artisan" coffee patisserie Arusha "Sable Square" | Artisan Coffee and Patissier | Instagram, TripAdvisor, TATO; no names |
| Q41/45 | "Gran Meliá Arusha" appoints OR appointed "general manager" | Gran Meliá Arusha | Meliá's 2019 opening release on Hospitality Net (fetched): opened 1 September 2019; no manager named |
| Q42/45 | "Kilimanjaro Fertility Institute" Arusha | Avinta Care (owner company) | Nothing on the owner company |
| Q43/45 | "St. Elizabeth Hospital" Arusha "Medical Officer in Charge" OR "Hospital Director" OR administrator | St. Elizabeth Hospital | 123Tanzania listing (fetched): P.O. Box 498, landline, just over 100 beds. The posts exist, but no page names the holders |
| Q44/45 | "Gran Meliá Arusha" "human resources" OR "HR manager" OR "people and culture" | Gran Meliá Arusha | Hotel's job adverts (fetched): 171 rooms, a cluster GM for Arusha and Zanzibar (not named), applications through Meliá's careers portal; no HR inbox |
| Q45/45 | "Shidolya" managing director OR founder OR proprietor Arusha (LinkedIn, ZoomInfo, RocketReach excluded) | Shidolya | No allowed source names anyone. A review reply signed with a first name only was not recorded. shidolya-safaris.com is for sale |

## Fetches without a search

- **TATO member profiles:** 38 pages on tatotz.org, plus TATO's Board of Directors page. They gave the named people for PwC, King Mart and Krisha, and addresses and phones for most records.
  - 35 URLs came from the known sources and wave 2's saved list of TATO profile URLs.
  - Kilimanjaro Outfitters' URL came from a link on a saved TATO page.
  - Krisha's (`/portfolio/2366/`) and House of Gems' URLs came from search results (Q9, Q34).
- **Own websites read:**
  - shidolyasafaris.com (contact, About, sitemap)
  - atc.ac.tz (top leadership, management, HR directorate)
  - lemalacamps.com (four pages and the 2026 report PDF)
  - krishasafaris.com
  - serian.com (enquiry, team, about, agents, Tanzania terms)
  - kilivikings.com
  - mamaafricasafaris.co.tz
  - vianneysuntamedexpeditions.com (home, founder, team)
  - eastafricanvoyage.com (home and two policy pages)
  - safariplus.co.tz
  - sadioevents.co.tz
  - teamwise.travel
  - merutreks.com (identity doubtful; not used)
- **Other allowed sources:**
  - Bank of Tanzania register of supervised institutions (Lashku)
  - Jubilee Insurance provider panel PDF (health facilities)
- **Pacing:** 232 requests to 75 hosts, at least 2.5 seconds apart per host; robots.txt was checked before every page (77 robots.txt requests). WebFetch was used twice, when the fetcher failed: the tatotz.org robots.txt (DNS) and the Africa VIP About page (HTTP 500). Both failed the same way.
- **robots.txt matching:** Python's `urllib.robotparser` reads `Disallow: /?` as `Disallow: /`, because the empty query is dropped. That is why the crawl marked kilivikings.com as fully disallowed. The crawl also flagged shidolyasafaris.com, but its robots.txt now disallows only /wp-admin/. This agent matched rules by RFC 9309 (longest match, `*` and `$`), checking both its own agent group and `*`. The same quirk may affect `contact_lib.robots_state`.

## Blocked or unreadable sources

Not worked around in any case: no retries in a loop, no change of User-Agent, no plain-HTTP downgrade, no browser, no decoding of protected email links.

- **HTTP 403:**
  - www.melia.com (Akamai "Access Denied")
  - www.pwc.co.tz ("Access Denied")
  - www.utopia-safaris.com
  - miles-to-smile.com
  - www.jwseagon.com
  - www.travelbookingtz.com (Cloudflare "Just a moment..." challenge)
- **HTTP 429:** www.bush2beach.com
- **Bot check:** shawsafaris.co.tz ("Bot Verification" page)
- **Bad certificates:**
  - akshartoursandsafaris.co.tz and andersons.co.tz (hostname mismatch)
  - www.tanzaniaporters.org (expired)
  - artisan.co.tz (self-signed)
  - nnkosmith.com, www and bare host (TLS handshake failure)
- **robots.txt `Disallow: /` (not fetched):** safarini.com, kitamuhouse.com, kitamucafe.com, kitamugourmetbasket.com
- **Server errors:**
  - www.africaviptravel.com: HTTP 500 on every page, also through WebFetch
  - alanvertents.com: "509 Bandwidth Limit Exceeded", twice
  - www.bookmundi.com: HTTP 503
  - www.africangalleria.co.tz: HTTP 503 "under construction" page (its text was read)
- **Connection refused:** www.kilaweni.com
- **DNS failures:**
  - Do not resolve: kudusafaris.co.tz, merutreks.co.tz, www.kiliadventures.com, houseofgemstz.co.tz, seha.co.tz (NXDOMAIN), deeperadventure.com, teamwiseafrica.com, shawsafaris.com (from the crawl)
  - Resolved later: tatotz.org (bare host) at 18:40, and www.safarigo.com once
- **Parked, for sale or changed hands:**
  - nsktz.com (GoDaddy parking lander)
  - kingmart.co.tz (hosting default page)
  - shidolya-safaris.com (for sale; seen in search only)
  - merutreks.com (another operator's SEO site)
- **Not attempted by policy:** Facebook, Instagram and LinkedIn pages (URLs recorded only as seen), TripAdvisor, and Medpages (robots.txt disallows all agents but search engines).
- **Cloudflare email protection, not decoded:** atta.travel, www.zoomtanzania.net, ajirayako.co.tz

## Warnings

Review items the notes will raise (`contact_lib.note_flags`), and other points for a reviewer:
- **Possible closure:** Meru Mountain Treks. Its domain is dead and merutreks.com (the master's inbox domain) has changed hands.
- **Website gone:**
  - St. Elizabeth Hospital (seha.co.tz)
  - Shaw Safaris (shawsafaris.com)
  - Kudu Safaris (kudusafaris.co.tz)
  - Safari Plus (safariplus.tz)
  - House of Gems (houseofgemstz.co.tz; its info@ inbox may bounce)
  - Meru Mountain Treks
- **Hijacked or parked:**
  - Travel Booking Guide: the master earlier saw gambling spam on its homepage.
  - NSK Hospitals: nsktz.com is parked, so the master's named inbox on it needs checking.
  - Meru Mountain Treks.
- **Location to check:**
  - Akshar Tours: Mwanza, outside the area.
  - African Galleria: near Karatu, about 130 km west of Arusha.
  - Sadio Events: Dar es Salaam.
  - Shaw Safaris and Kilaweni: Usa River, not Arusha centre; possibly nearer the Usa River campus.
- **Check before outreach:**
  - Africa VIP Travel: snippet phones differ from the master's.
  - Lashku: its inbox sits at another company's domain.
  - Anderson's: a review site lists it as "(Deleted)" (not flagged).
  - Kudu: the site looks stale (not flagged).
- **Segment wrong in the master:** 16 records labelled "Safari / tour operator" are TATO affiliates of other kinds:
  - PwC (audit and tax)
  - King Mart (hospitality procurement)
  - NSK Hospitals (hospital)
  - Mega Tents (tent maker)
  - Safari Plus (charter airline)
  - TanManagement (insurance broker)
  - Lashku (bureau de change)
  - Kitamu (restaurant complex)
  - Safari Wholesalers (supplier)
  - House of Gems (gem cutting and jewellery)
  - Sadio Events (events)
  - Vehicle Pharmacy (vehicle parts)
  - Mkizughuno (pest control)
  - Artisan (cafe)
  - African Galleria (art gallery)
  - TFTSP (federation)
- **Website values that differ from the master (review):**
  - Shaw: shawsafaris.co.tz
  - Kudu: kudusafaris.net
  - African Galleria: africangalleria.com
  - Safari Plus: safariplus.co.tz
  - TanManagement: tm.co.tz
  - Sadio: sadioevents.co.tz
- **Empty website fields filled:** ATC, Lemala, Vianneys, Mama Africa, Serian, East African Voyage, NSK, Teamwise, Vehicle Pharmacy, Safari Wholesalers, and Gran Meliá (its page on melia.com).
- **Master data to fix:**
  - King Mart's phone "+255 694 774" is truncated: +255 694 774 477 (TATO).
  - Vianneys' email value is malformed; the clean inbox is vianney.jacob@vianneysuntamedexpeditions.com.
  - TATO lists Kudu's phone as "+225..." (a typo for +255).
- **Name and identity notes:**
  - Lemala Camps & Lodges is operated by Grumeti Expeditions TZ Limited.
  - Serian's Tanzanian company is Alex Walker Safaris (TZ) Limited.
  - Tanmanagement (JW Seagon) is TanManagement Insurance Brokers Limited (head office in Moshi).
  - Mama Africa Safaris is Mama Africa Tanzania Safari Limited.
  - Kudu Safaris shares a site with Rhino Safaris Ltd of Nairobi.

## Data-protection decisions

- **Not used as sources for people:** personal LinkedIn profiles and data brokers (ZoomInfo, RocketReach, aeroleads), client reviews, forum posts, a trade-magazine interview and third-party "owner" pages. This affected Shidolya, Mega Tents, East African Voyage, Nnko & Smith, Shaw, Bush 2 Beach, Kipepeo, Safari Plus and Serian.
- **Search rule lapse:** Q16/45 included a published first name next to the company name. No other query named a person, and nothing about that person beyond the company's own page was recorded.
- **Biographies and personal details not recorded:**
  - birthplaces (Vianneys, Kili Vikings) and a family link (Vianneys)
  - nationality (Africa VIP Travel)
  - career histories (Krisha's CEO and the other TATO board biographies)
  - degrees, other directorships and a community chairmanship (TanManagement)
  - a professional certificate (East African Voyage)
  - a family relation between founders (King Mart)
  Excerpts were cut with "..." to leave these out.
- **Possible family detail:** Utopia's co-founder is given by first name only and described as "his partner"; not recorded. African Galleria says a family founded it; no individual was recorded.
- **Personal-domain inboxes:**
  - Not recorded, because they are named after people: a Hotmail inbox (Safarini) and two Gmail inboxes (Mkizughuno).
  - Kept, because they are named after the organisation: free-mail inboxes for Kitamu, Safari Wholesalers, TFTSP (2), Vehicle Pharmacy and House of Gems.
- **Named inboxes without a published role:** recorded as organisation routes only, not linked to anyone. These are Akshar, Mama Africa, Mega Tents, Safari Plus, JW Seagon, East African Voyage and Vianneys (its founder's inbox, published by TATO, not on the page that gives his role).
- **Inboxes at another organisation's domain:**
  - Not recorded: Kilimanjaro Outfitters (honeyguide.org), Lemala (tourvesteastafrica.com), and NSK's on the parked nsktz.com.
  - Recorded with a warning: Lashku's inbox at praxisaccounts.com, which is the only inbox TATO gives.
- **Staff left out:** guides (Serian, Vianneys), finance, reservations and guide staff (Teamwise), Lemala's overseas sales agents (other companies), and ATC unit heads beyond the six most relevant.
- **Name normalisation:**
  - Nnko & Smith's director is recorded as "Aminiel Nnko" (published as Aminiel "Ammy" Nnko; the excerpt keeps the published form).
  - ATC's HR director uses his directorate page's form, "Emanuel Ishika".

## Organisations not reached

None: all 45 have a line. These still have no named decision-maker on a fetched allowed source:

| Organisation | organisation_id | Distance | Why |
|---|---|---|---|
| Shidolya Tours & Safaris | Ob2f968f00c1d | 0.5 km | Named only on LinkedIn and data brokers (2 searches) |
| Gran Meliá Arusha | Oc0616ccade39 | 0.6 km | melia.com 403; GM and HR not named anywhere allowed (3 searches) |
| Akshar Tours and Safaris | Oa881d17035bb | 0.9 km (mis-mapped) | Mwanza company; no search spent |
| Nnko & Smith Safaris | O0506bda0252b | 0.9 km | Director snippet-only, from an affiliate; own site TLS failure |
| Avinta Care Specialized Polyclinic | O4e451c44259b | 1.3 km | Register names the owner company only (2 searches) |
| R&D Polyclinic | O6d9b7e357294 | 1.9 km | Nothing beyond OSM |
| St. Elizabeth Hospital Arusha | Oae7daca781fb | 2.0 km | Own site gone; post holders not named (2 searches) |
| Mega Tents (Al-Anver Outfitters) | O790a03b81388 | 2.1 km | Own site over its bandwidth limit; names only on ZoomInfo |
| Mama Africa Safaris | O60cd5e6c0e9b | 2.2 km | No one named anywhere |
| Safarini Africa | O133d963b1d2f | 2.2 km | Own site disallows crawling |
| Travel Booking Guide | O6ef8ec4bce53 | 2.2 km | Own site Cloudflare-blocked; "founded by experienced professionals" only |
| Serian / Alex Walker Safaris | Ob57f8d39dff5 | 2.3 km | No role published for anyone |
| Shaw Safaris | Ofa40434a1f64 | 2.3 km | Bot check; owners only in reviews |
| Anderson's African Adventures | Oe5bd1b3cf183 | 2.3 km | Bad certificate; "owner operated", no name |
| Kilaweni | O165bb1966844 | 2.3 km | Site refuses connections |
| Kilimanjaro Outfitters | O5680f8038d8d | 2.3 km | Wrong website; no names |
| Kudu Safaris | Oa9f2f6cfc8fa | 2.3 km | Stale site; no names |
| Kipepeo | Of6951631ee8a | 2.3 km | Not identifiable |
| Meru Mountain Treks | O0bcf10d5e11c | 2.3 km | Possibly lapsed |
| Bush 2 Beach (The African Footprint Co) | O73505d5bea54 | 2.3 km | Own site 429; owners only in a review |
| Miles to Smile | O13fac71333a1 | 2.3 km | Own site 403 |
| African Galleria | O59219a33cb30 | 2.3 km (mis-mapped) | Karatu; family-founded, no individual |
| Safari Plus | O69b33ef5c8f2 | 2.3 km | Dar es Salaam airline; no names on own or parent pages |
| Lashku Forex Bureau | O560785f0759a | 2.3 km | Register gives no contact person |
| Kitamu Africa | O628305bfb723 | 2.3 km | All three sites disallow crawling |
| Safari Wholesalers and Retailers | O557fde8b56a5 | 2.3 km | "Coming Soon" site |
| House of Gems | O43fbd884d754 | 2.3 km | Domain gone; TATO only |
| NSK Hospitals | O7948a9942116 | 2.3 km | Own site and register name no one |
| Sadio Events | O6c2976e997c2 | 2.3 km (mis-mapped) | Dar es Salaam; no search spent |
| TFTSP | Od82a9ff8b85d | 2.3 km | Expired certificate; not in the NGO register extracts |
| Teamwise Tanzania Travel | O7bfec9bb050a | 2.3 km | Directors by first name only |
| Vehicle Pharmacy | O3974c6961fd9 | 2.3 km | Script-only site |
| Mkizughuno | Oe993b62c844c | 2.3 km | TATO only |
| Artisan Coffee and Patissier | O4a1cc6cdc040 | 2.3 km | Self-signed certificate; no names |

Most records at "2.3 km" appear to share one Arusha-centre point (TATO addresses geocoded to the city), so their real distances are unknown.

## Stopping rule and next steps

The stopping rule (every record researched) is met. The search allowance is spent, and no search was refused by the session cap.

Suggested next steps:
1. **Master review:**
   - Correct the 16 segments.
   - Resolve the 6 website conflicts.
   - Fix King Mart's truncated phone.
   - Check NSK's and Meru's inboxes on parked or changed-hands domains.
   - Re-geocode the "2.3 km" TATO records, especially Shaw and Kilaweni (Usa River), Akshar (Mwanza), African Galleria (Karatu) and Sadio (Dar es Salaam).
2. **Parent bodies to ask or read by hand:**
   - Catholic Archdiocese of Arusha (St. Elizabeth Hospital's head)
   - Kilimanjaro Fertility Institute (Avinta Care)
   - Meliá Hotels International (Gran Meliá's general manager and HR)
3. **Crawler fix:** `contact_lib.robots_state` uses `urllib.robotparser`, which treats `Disallow: /?` as disallowing the whole site. An RFC 9309 matcher would let the crawl read kilivikings.com and similar sites.
4. **Phone or on-the-ground checks:** Kipepeo (which business), Meru Mountain Treks (still trading?), Anderson's and Kudu (still trading?).
