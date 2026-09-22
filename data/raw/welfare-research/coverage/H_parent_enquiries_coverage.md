# Slice H: public parent and guardian enquiries (coverage log)

Run: `arusha-welfare-2026-09` · Research date: 2026-09-22 · Records file: `H_parent_enquiries.jsonl`
Tools used: WebSearch and WebFetch only. No browser. No sign-in, form submission, replies or contact with anyone.

## 1. Result summary

| Record type | Count |
|---|---|
| enquiry | 3 |
| organisation | 0 |
| contact | 0 |
| relationship | 0 |

- All 3 enquiries are from people planning to move to **Moshi**. None published contact details in the post. All are `pdpa_risk: risky`.
- 1 recent enquiry (Tripadvisor, posted on or before 31 Mar 2025). 2 historical enquiries (Tripadvisor c. 2021–22; Expat.com c. 2011–12).
- **No readable in-catchment enquiry** was found for Arusha city, Arumeru/Meru (Usa River, Tengeru), Hai/Boma Ng'ombe or Siha.
- No readable public post by a parent or guardian in the catchment asked for school-fee support, sponsorship, a children's-home place or foster/kinship support.
- JSONL validated: all 3 lines parse. Required keys are present, excerpts are 25 words or fewer, and `pdpa_risk` is `risky` on every record.

## 2. Stopping rule

- The last new enquiry found by search came from query 15 (the Tripadvisor thread "Living in Moshi").
- Queries 16–58 then ran 43 times in a row without a new relevant enquiry. They were varied: Kiswahili and English, across JamiiForums, Reddit, Quora, Expat.com, Tripadvisor, Mumsnet, GoFundMe, Facebook, X, classifieds and blogs. The rule of at least 12 consecutive queries was therefore met.
- The WebSearch budget for the whole session (200 calls, shared with other agents) then ran out, and 3 planned queries were not run (see §8).
- Remaining work used direct fetches of forum index pages. These found the 2 historical Moshi enquiries.

## 3. Search queries run (58)

| # | Query | Target | Outcome |
|---|---|---|---|
| 1 | natafuta shule Arusha jamiiforums | JamiiForums | Threads were secondary, housing or location questions. Candidates: 1044233, 927959 |
| 2 | ada ya shule msaada Arusha | General (sw) | Arusha CC social welfare page (organisation) and a secondary-fees thread. No enquiry |
| 3 | mfadhili ada Arusha mtoto | General (sw) | News items and GeorDavie (organisation). No enquiry |
| 4 | shule nzuri ya English medium Arusha bei nafuu | JamiiForums | Dar/Goba threads and lists of government English-medium schools. No catchment enquiry |
| 5 | "Wakazi wa Arusha, ni shule zipi zilizopo kata hizi" | JamiiForums | Summary only: a list of city wards. Ambiguous (see §6) |
| 6 | "Shule ya Precious blood ipo maeneo gani Arusha" | JamiiForums | Location question about a secondary school. Out of scope |
| 7 | "Msaada kwa wanaojua ada za shule hizi" jamiiforums | JamiiForums | Secondary science schools, mostly Dar. Out of scope |
| 8 | natafuta shule Moshi mtoto darasa la kwanza | General (sw) | Opinion threads and Form 1 placement lists. No enquiry |
| 9 | reddit Arusha school recommendations kids moving | Reddit | No Reddit results |
| 10 | expat.com Arusha forum school children | Expat.com | Candidate 525116 "SCHOOL HUNT IN ARUSHA" (later found removed) |
| 11 | "Moshi" Tanzania forum looking for primary school for my son affordable | Forums (en) | Tripadvisor donor threads and school listings. No enquiry |
| 12 | "Usa River" school for my daughter forum recommendations | Forums (en) | Irrelevant US results |
| 13 | "SCHOOL HUNT IN ARUSHA" expat.com | Expat.com | Same removed thread, no snippet detail |
| 14 | expat.com Arusha forum kindergarten affordable school fees | Expat.com | Guides only |
| 15 | expat.com Moshi forum school kids Tanzania | Expat.com / Tripadvisor | **Tripadvisor "Living in Moshi" (enquiry 1)**; Expat.com 941693 |
| 16 | "Schools for my children" Tanzania forum expat.com | Expat.com | 941693 has no location; 408199 is Dar |
| 17 | expat.com forum africa tanzania arusha school "not so expensive" | Expat.com | Relocation threads without children |
| 18 | tripadvisor Arusha forum moving with children school kindergarten | Tripadvisor | Safari and donor threads only |
| 19 | site:reddit.com Arusha school kids | Reddit | Operator ignored; no Reddit results |
| 20 | site:reddit.com tanzania "Arusha" school fees child | Reddit | No Reddit results |
| 21 | quora best affordable English medium primary school in Arusha | Quora | School websites only |
| 22 | jamiiforums shule ya msingi English medium Arusha ada msaada wazazi | JamiiForums | Complaints and advice threads. No enquiry |
| 23 | jamiiforums day care Arusha mtoto msaada | JamiiForums | Daycare business and directory results |
| 24 | jamiiforums shule Usa River msingi mtoto | JamiiForums | Generic threads |
| 25 | jamiiforums shule nzuri ya msingi Moshi English medium ada | JamiiForums | Dar and Dodoma threads |
| 26 | "ushauri" shule nzuri Arusha mtoto darasa la kwanza jamiiforums | JamiiForums | Secondary and private-school threads |
| 27 | nahamia Arusha shule watoto ushauri jamiiforums | JamiiForums | Complaints (Turkish Maarif, Arusha Primary, Namanga) |
| 28 | "wana Arusha" shule ya msingi nzuri ada | General (sw) | Fee lists |
| 29 | jamiiforums shule ya bweni ya msingi Arusha Moshi ushauri mzazi | JamiiForums | Debate threads |
| 30 | "Shule nzuri ya private" jamiiforums Arusha Kilimanjaro | JamiiForums | Secondary (Henry Gogaty, Catholic secondaries) |
| 31 | jamiiforums "Arusha" "shule ya awali" OR "chekechea" mtoto wangu ushauri | JamiiForums | General early-years threads |
| 32 | "naomba msaada" ada ya shule mtoto Arusha mfadhili | Blogs / JamiiForums | Two sponsor-request blogs (fetched; see §4) |
| 33 | gofundme school fees my children Arusha Tanzania | GoFundMe | Third-party and charity campaigns only |
| 34 | gofundme school fees Moshi Tanzania my son daughter mother | GoFundMe | Third-party and charity campaigns only |
| 35 | facebook "Arusha" "looking for a daycare" OR "looking for a kindergarten" OR "recommend a school" | Facebook | Daycare pages only |
| 36 | "Expats in Arusha" facebook school recommendations kids | Facebook | Group URL only (fetched; login wall) |
| 37 | "habari wadau" natafuta shule nzuri Arusha | General (sw) | Secondary threads |
| 38 | "natafuta shule" "Arusha" mtoto | General (sw) | News and housing threads |
| 39 | "natafuta day care" Arusha | General (sw) | Daycare listings |
| 40 | "any recommendations" school Arusha kids facebook group post | Facebook | School pages and group URL |
| 41 | yatima ada shule Arusha msaada mlezi | General (sw) | TAMISEMI joining forms, news |
| 42 | kituo cha kulelea watoto yatima Arusha kumpeleka mtoto naomba ushauri | General (sw) | Registration pages and a Dar donor thread |
| 43 | shule ya msingi Tengeru English medium ushauri ada | General (sw) | Generic threads |
| 44 | Boma Ng'ombe shule ya msingi nzuri English medium Hai ushauri | General (sw) | Generic threads; nothing for Hai |
| 45 | "Nimpeleke mwanangu St kayumba au English medium" jamiiforums | JamiiForums | Location not established |
| 46 | "shule za watoto watukutu" jamiiforums shule ya msingi Arusha | JamiiForums | Location not established; behaviour topic |
| 47 | jamiiforums "Moshi" natafuta shule ya msingi mwanangu ushauri | JamiiForums | Opinion threads |
| 48 | "moving to Moshi" with kids school forum | Forums (en) | Same thread as enquiry 1 |
| 49 | "moving to Arusha" with kids school recommendations forum 2025 | Forums (en) | Guides only |
| 50 | tripadvisor Moshi forum school for my children relocating | Tripadvisor | Same thread as enquiry 1; donor threads |
| 51 | mumsnet OR babycenter Arusha Tanzania nursery school toddler moving | Mumsnet | UK threads only |
| 52 | jiji.co.tz Arusha "school fees" sponsor needed child | Classifieds | Sponsorship organisations only |
| 53 | wanabidii naomba msaada ada ya shule mtoto Arusha | Mailing lists | No results from the list |
| 54 | twitter "natafuta shule" Arusha OR Moshi mtoto | X | No X results |
| 55 | zoomtanzania OR kupatana wanted school Arusha child sponsor | Classifieds | Sponsorship organisations only |
| 56 | expat.com "Indian schools in Moshi" | Expat.com | Title only (thread fetched later: enquiry 3) |
| 57 | "school hunt in Arusha" kindergarten primary budget | Expat.com | Nothing more on 525116 |
| 58 | "shule zipi zilizopo kata hizi" Arusha | JamiiForums | Confirms the thread lists all city wards |

## 4. Pages fetched (WebFetch)

| URL (short) | Result |
|---|---|
| jamiiforums.com threads 1044233, 927959, 1072049 | HTTP 403 (bot protection) |
| jamiiforums.com education forum `index.rss` | HTTP 403 |
| web.archive.org copy of 1044233 | Tool cannot fetch this domain |
| expat.com `viewtopic.php?id=525116` | HTTP 403 |
| expat.com 525116 canonical URLs (two variants) | **HTTP 410 Gone**. The site resolves threads by ID (checked with 941693 and a wrong slug), so the thread has been removed |
| expat.com 436543, 1025348, 941693, 1024259, 408199, 34803, 527454, 606835, 737972, 873372, 259351 | Loaded; none qualify (see §6) |
| **expat.com 190219 "Indian Schools in Moshi"** (fetched 2×) | Loaded. **Enquiry 3** |
| expat.com Tanzania forum index pages 1–8 | Loaded; complete scan of the forum (2008–2026) |
| tripadvisor.com k2815974 "Living in Arusha"; k15261676 "Tanzanian Schools" | Loaded; no school enquiry / donor post |
| **tripadvisor.in k15245397 "Living in Moshi"** (fetched 5×: content, dates, reply order, wording) | Loaded. **Enquiry 1** |
| **tripadvisor.com k14083815 "English Speaking Nursery School"** (fetched 2×) | Loaded. **Enquiry 2** |
| tripadvisor.com k13378966 "School information" (Moshi) | Loaded; ambiguous (see §6) |
| Tripadvisor Arusha forum index o0–o80 (5 pages, Jan 2023–Aug 2026), scanned twice (school titles, then relocation titles) | No school or relocation topics (only "Children on safari", tourism) |
| Tripadvisor Moshi forum index o0–o80 (5 pages, May 2015–Feb 2026), scanned twice | Found enquiries 1 and 2 and "School information" |
| dirayamafanikio.blogspot.com (sponsor-request blog, 64 comments) | No comment from the catchment |
| mbuke.blogspot.com (sponsor-request blog, about 120 comments) | One Arusha comment, from a school-leaver seeking university funding (self, post-secondary). Out of scope; nothing recorded |
| old.reddit.com r/tanzania search | Tool cannot fetch this domain |
| facebook.com/groups "Expats in Arusha"; "All About Arusha" (both public, about 77.6k members in the latter) | Login wall; one unrelated post visible in each |

## 5. Blocked or unavailable

- **JamiiForums** (the main Kiswahili source) returns HTTP 403 to automated fetches, including RSS. I did not try to get around this. Only search-engine summaries were available, so no JamiiForums thread could be read and nothing was recorded from it.
- **Facebook groups**: login wall. **WhatsApp/Telegram groups** are private and out of bounds. **Instagram, TikTok and X** gave no usable indexed results.
- **Reddit and Quora**: the `site:` operator returned no Reddit results, and Reddit cannot be fetched by the tool.
- **Internet Archive**: cannot be fetched by the tool.
- The search tool returns summarised results rather than raw snippets, so display names and dates of snippet-only posts could not be captured.

## 6. Candidates reviewed and not recorded (no personal details kept)

- **Expat.com 525116 "SCHOOL HUNT IN ARUSHA - Not so expensive school?"**: the title indicates an enquiry for an affordable school in Arusha, but the thread has been removed (410 Gone) and the author and date are unknown. Not recorded because the post was withdrawn.
- **JamiiForums 1044233 "Wakazi wa Arusha, ni shule zipi zilizopo kata hizi?"**: could not be read. The summary suggests it lists all Arusha city wards and asks which schools are in them. No child or request for a place is visible. Ambiguous; not recorded.
- JamiiForums "Shule ya Precious blood ipo maeneo gani Arusha?": asks where a **secondary** school is (Poli ward, Meru). Outside Silverleaf's levels.
- JamiiForums threads about secondary schools (affordable seminaries, O-level boarding under 1.5m, private A-level science in Kilimanjaro/Arusha/Tanga, girls' O-level schools in Kilimanjaro, "Shule nzuri ya private"): secondary level, out of scope.
- JamiiForums threads about Dar es Salaam, Dodoma or other regions (Goba, Tusiime, Dar English-medium primaries, Dodoma international school, a Dar orphanage donor): outside the catchment.
- JamiiForums "USHAURI; Nimpeleke mwanangu St kayumba au English medium??" and "Wakuu naomba kujuzwa shule za watoto watukutu shule ya msingi": location not established, and the second concerns child behaviour. Not recorded.
- Tripadvisor "School information" (Moshi, Aug 2020): asks for contact details of a named Moshi pre-primary and primary school. No child or relationship is mentioned. Ambiguous; not recorded.
- Tripadvisor "Living in Arusha" (c. 2009): a relocating family asks about safety and activities, not schooling.
- Tripadvisor threads by visitors or donors, not enquiries: "Tanzanian Schools", "Looking for school or orphanage to assist", "Anyone know this orphanage?", "Visiting a local school in Moshi", "MsaMaria Center for Street Children".
- Expat.com threads:
  - "Schools for my children" (c. 2021): no location given.
  - "Need a good american or british preschool…" (c. 2015) and "French family of 4…" (c. 2010): Dar es Salaam.
  - "Moving to Arusha", "I am thinking of Moving to Arusha", "New in Arusha": no children or schooling mentioned.
  - "Family with toddler moving to Arusha" (c. 2016): living questions only.
  - "Home School Network in Arusha" (c. 2016): a homeschool network, not a school place. A reply mentions moving with a toddler but asks only about housing.
  - "Raising kids in Tanzania" and "Homeschooling in Tanzania": no catchment school request.
- GoFundMe campaigns for children in Arusha or Moshi: organised by volunteers or charities, not by the children's parents or guardians. Several name or picture children. Not recorded as enquiries; the organisations are listed in §7.

**Sensitive content noted, not recorded:** search results included news items and a video about violence against children and a child's death in Arusha, and JamiiForums threads about a child's condition and about children with learning or behavioural difficulties. None was opened for detail or recorded.

## 7. Cross-slice organisation leads (organisation level only; for slices A–G to verify)

- **Selfless Solutions** (selflesssolutions.org): matches sponsors to Arusha children for **private-school** places.
- **Arusha Kids Trust** (arushakidstrust.com/school-sponsorship): full and part school sponsorship.
- **Arusha Children's Effort** (arushachildrenseffort.com): education support since 2010.
- **Arusha Kids** (arushakids.com/sponsor); **WEHAF** (wehaf.org, daycare plus school support); **Tanzania School Foundation** (tanzaniaschoolfoundation.org); **Panos Education Support** and **WIPAHS** (location not confirmed).
- **Soul Ties Arusha**: charity fundraising school fees for Arusha children (campaign URL withheld because it contains children's names).
- **Lasting Bless School**, Arusha, a small primary school for orphaned and vulnerable children (gofundme.com/f/a-mission-to-feed-empower-arushas-children).
- **"Almo" School and Daycare**, Arusha (gofundme.com/f/to-help-the-kids-and-animals-in-arusha-tanzania).
- **Greenwich Nursery School**, Arusha (gofundme.com/f/help-greenwich-nursery-school-arusha-tanzania).
- **Moshi Kids Centre / Zara Charity Tanzania** (gofundme.com/f/allow-25-children-to-be-able-to-access-primary-school).
- A school-fees campaign for 30 children in Moshi (gofundme.com/f/school-fees-to-help-30-children-in-moshi-tanzania).
- **Tumaini Children's Foundation** (Usa River); **MsaMaria Center for Street Children** (Moshi); **Fruitful Orphanage and Day Care Centre** (Arusha, Facebook page); **SOS Children's Village Arusha**; **GeorDavie Ministries** (reported to pay school fees).
- **Arusha City Council, Community Development and Social Welfare**: pays school fees and uniforms for identified orphans (a government referral route).
- Competitors named in enquiry replies: **UWC East Africa** (described as expensive) and **HOPE School / Hope International School Moshi** (hopetz.org, described as the budget option).

## 8. Known gaps and follow-ups

1. **JamiiForums could not be read.** A human reviewer with a normal browser (public pages, no login) could check thread 1044233 and search JamiiForums for 2024–2026 posts combining Arusha/Moshi/Usa River/Tengeru with "shule ya msingi", "day care", "chekechea", "ada" or "mfadhili".
2. **Not run because the search budget ran out:**
   - Siha/Sanya Juu; Hai/Machame/Masama/KIA; Maji ya Chai/Kikatiti.
   - Kiswahili terms for foster and kinship care (e.g., "malezi ya kambo", "kulea mtoto wa ndugu").
   - Children's-home placement in Moshi.
   - The Expat Exchange forum.
   - Three planned Expat.com follow-up queries (not needed: the full Expat.com Tanzania index was fetched instead).
3. **Tripadvisor**: the Arusha forum was scanned only for Jan 2023–Aug 2026 (5 of about 87 index pages). The Moshi forum was scanned for May 2015–Feb 2026 (5 of 13 pages). The Tanzania country forum was not scanned.
4. Public Facebook groups and parent WhatsApp groups are probably where most real local enquiries happen. They are behind a login or private, so they are out of bounds under the brief.
5. All 3 records are demand signals from relocating families. None has published contact details, and the brief forbids contacting them or looking them up elsewhere.
