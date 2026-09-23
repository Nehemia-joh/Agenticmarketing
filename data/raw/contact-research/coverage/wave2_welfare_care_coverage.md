# Coverage log: wave 2, welfare care (23 September 2026)

- Slice: `runtime/contacts/slices/wave2_welfare_care.json` (44 children's homes and family-based care programmes, nearest first)
- Output: `data/raw/contact-research/search_wave2_welfare_care_2026-09-23.jsonl`
- Search allowance: 10 WebSearch calls. Used: 10 (Q1/10 to Q10/10). After Q10, only URLs already in hand were fetched.
- Fetch pacing: at least 2 seconds between requests to the same site. robots.txt was checked for every host fetched; all pages used are allowed (tumaini-home.no publishes no robots.txt). The crawler's copies from 2026-09-23 (`runtime/contacts/http-cache/`) were read locally where they existed, without new requests.
- Organisations written: 19 of 44. Status counts: found 2, partial 9, not_found 7, blocked 1. Identity: confirmed 15, uncertain 4.
- Named leads recorded: 9 (7 on confirmed identities, 2 on the uncertain Tumaini Home match). New direct routes: 2 emails and 4 phones (the gmail inbox and both phones of Tumaini Home are on an uncertain identity, so the profile builder will not merge them).
- Prior evidence from `data/raw/welfare-research/research_*_2026-09-22.jsonl` and the NIS register cache was reused before any search. NIS profiles publish no email, phone or address.
- Recording rules applied:
  - People come only from the organisation's own site or blog, a parent body, a dedicated support charity treated as the home's website (Hope Home Trust for Kitaa), or a directory entry (GuideStar).
  - Funder routes (Arusha Kids Trust, Foundation For Hope In Africa) are described in notes only, not recorded as the home's routes.
  - The following were not recorded: named people's personal webmail, residential-looking foreign street addresses, family relationships, and anything about children, parents or residents.
  - Child sponsorship pages were skipped.

## Status definitions

- `found`: identity confirmed and at least one email or phone published by the organisation, its parent body, its dedicated support charity or an official register.
- `partial`: only indirect routes (website, official social page, postal address, contact form, named lead), or a direct route whose identity or source is uncertain or stale.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/10 | `"Save Africa Orphanage" Usa River` | 1. Save Africa Orphanage | Official Instagram account "Save Africa Tanzania" (the NIS-registered name). No phone or email. partial |
| Q2/10 | `"Sun of Hope" orphanage "Usa River"` | 2. Sun of Hope Village/Orphanage | Facebook page "Sun of Hope Orphanage" (Portland OR). The parent body's page gives a US phone. found (US contact only) |
| Q3/10 | `"The Small Things" Nkoaranga Arusha` | 3. Happy Family Children's Village | Operator's GuideStar entry (fetched): Executive Director and Chair named, email shown only to paying subscribers. Operator's own site gives socials. partial |
| Q4/10 | `"Tumaini Home Organization" Arusha` | 4. TUMAINI HOME ORGANIZATION (T.H.T.O) | Tumaini Home, Mto wa Mbu (tumaini-home.no): gmail inbox, Tanzanian phones, P.O. Box, co-founders. No source links it to the NIS entry. partial, identity uncertain |
| Q5/10 | `"Good Hope Orphanage" Arusha Tanzania` | 6. Good Hope Orphanage, School & Clinic | Facebook page "Good Hope Orphanage \| Arusha" (handle www.cometoafrica.org, domain does not resolve). "Good Hope Centre" in Usa River is a different organisation. partial |
| Q6/10 | `"St Gabriel" home Mateves Arusha` | 7. St. Gabriel Home | Snippet from the St Gemma sisters' site (no longer resolves) names Sr. Flora Ndwata as Manager. UK sponsor-charity pages blocked (403). partial |
| Q7/10 | `"Sunrise Hope for Foundation" Arusha` | 8. Sunrise Hope for Foundation | Only old snippets of the former site. ww1 host does not resolve; old domain now serves unrelated content. not_found |
| Q8/10 | `"Espero Foundation" Arusha` | 9. Espero Foundation | Only the 2013 Idealist listing. not_found |
| Q9/10 | `"Relief for the Hopeless Foundation" Arusha` | 11. RELIEF FOR THE HOPELESS FOUNDATION (RHF) | No match (other foundations only). not_found |
| Q10/10 | `"TATA Children Organization" Arusha` | 12. TATA CHILDREN ORGANIZATION | No match (other Arusha children's organisations, India's Tata Trusts). not_found. Allowance spent. |

## Fetches without a search

| Organisation | URL | Outcome |
|---|---|---|
| 1. Save Africa Orphanage | https://saveafricatanzania.weebly.com/ and /contact.html | Director named, registration 0005039, P.O. Box 677 USA River, contact form. The email is hidden by Cloudflare email protection and was not decoded. |
| 1. Save Africa Orphanage | https://www.arushakidstrust.com/ and /contact-us (crawler copy) | Australian funder whose focus is the home; its gmail inbox is noted as a funder route only |
| 2. Sun of Hope | theholyspiritsisters.org: sun-of-hope page, /contact-us/, /about-us/, /history/ (crawler copies, http) | Parent body: US phone. Its Portland street address looks residential (not recorded). Regional centre at Rauya, Moshi. Menu lists a Sun of Hope Primary School page. |
| 2. Sun of Hope | http://www.theholyspiritsisters.org/the-children-of-god-at-usariver-arusha/ | WebFetch forces https: TLS internal error, not retried |
| 3. Happy Family Children's Village | https://www.thesmallthings.org/ (crawler copy; page data read locally) and /contact (live) | US FEIN 45-2466306, TZ NGO/00007641, five official social pages. The contact page renders only in JavaScript. |
| 3. Happy Family Children's Village | https://www.guidestar.org/profile/45-2466306 (URL from Q3) | Executive Director and Chair. Email paywalled (not pursued). Branford CT street address not recorded. |
| 4. T.H.T.O | https://tumaini-home.no/about-us and /kontakt (URL from Q4; about page fetched twice for verbatim check) | Contacts and founders. Norwegian board members' personal webmail and mobiles not recorded. |
| 5. Watoto Kicheko Orphanage | https://watotokicheko.com/, /contact-us/, /watoto-kicheko/ (crawler copies); /laughter-of-a-child-foundation/ (live) | No longer admits children; donations closed. P.O. Box 14311. Facebook and X pages. No leaders named. |
| 6. Good Hope Orphanage | Idealist listing (joined October 2012) | No phone, email or contact person |
| 6. Good Hope Orphanage | https://www.betterplace.org/en/projects/18094-... (from Q5) | Only site navigation readable |
| 6. Good Hope Orphanage | https://ngobase.org/stswa/TZ.AR/VNG.OC/orphanages-arusha-region (from Q5) | No slice organisation listed |
| 6. Good Hope Orphanage | https://www.ampuriabrava-hoffmann.de/goodhopein.html (from Q5) | "Good Hope Centre", Usa River: different founder, 2008 data. Not merged. |
| 6. Good Hope Orphanage | http://www.cometoafrica.org/ (Facebook handle) | DNS lookup failed |
| 7. St. Gabriel Home | https://www.totalgiving.co.uk/charity/sponsors-of-st-gabriel-home-mateves-arusha-tanzania (from Q6) | HTTP 403 |
| 7. St. Gabriel Home | https://www.futureforkids.nl/language/en/news/ (from Q6) | Latest item on the home dated July 2010 |
| 8. Sunrise Hope for Foundation | http://sunriseforhope.org/ (crawler copy) | Redirects to an Indonesian "Shortlink Management" login page. The domain no longer belongs to the organisation. |
| 8. Sunrise Hope for Foundation | https://ww1.sunriseforhope.org/ (from Q7) | DNS lookup failed |
| 9. Espero Foundation | Idealist listing (joined May 2013) | Dodoma road location only |
| 10. Cradle of Love Baby Home | https://givingsmiles.org/en/cradle-of-love-baby-home/ | Closed suddenly at the end of March 2024 |
| 14. Olasiti Orphans Center | tanzanianorphans.org: /orphans-center, /about-us, /scholarships (crawler copies); /how-to-donate (live) | Registered as Olasiti Children's Foundation. Programme director named. No email or phone. |
| 14. Olasiti Orphans Center | 2025 annual report PDF (linked from /about-us) | Returned as binary; text extracted locally from the fetched copy. Executive Director named; activity to 26 Dec 2025. |
| 17. St. Joseph's Orphanage (Kiserian) | https://www.uniteafricafoundation.org/st-josephs-orphanage-1 | Funder page (2014-2019) names founder and director |
| 17. St. Joseph's Orphanage (Kiserian) | https://saintjosephsorphanage.wordpress.com/ and /contact-us/ (contact page fetched twice for verbatim check) | Blog (latest post August 2014) gives the phone, a P.O. Box and the parent congregation (Medical Daughters of Mary). Director's personal webmail not recorded. |
| 22. Kitaa Hope Home | https://www.hopehometrust.org.uk/contactus, /meetthestaff (fetched twice), /history | Trust inbox (webmail), charity 1126415, founder-director, KITAA as operator. Brighton street address and family details not recorded. |
| 23. Kilimanjaro Centre for Orphans and Street Children | Idealist listing (joined June 2008) | No contacts. Facebook page from the 2026-09-22 run reused. |
| 24. Rainbow Centre | http://rainbow-centre.blogspot.com/ | No contacts or coordinator; latest post 10 May 2010 |
| 25. Habari Foundation (Moshi) | https://habarifoundation.org/ | Bot-verification page (blocked), as on 2026-09-22 |
| 31. Kim Jones House | https://www.foundationforhopeinafrica.org/tanzania.html (live); /, /about-us.html, /the-team.html (crawler copies) | Built by FFHIA in 2012. No local manager or contact. FFHIA's own US route noted only. |
| General | https://ngobase.org/ci/TZ.AR.AR/arusha-ngos-charities (from Q8-Q10) | Page 1 of 8 has no slice organisation; later pages not read |
| General | https://www.arushacity.com/listing-category/charity-organizations/ (from Q9) | HTTP 526 (origin certificate error) |
| 15. KIKATITI HAPPY WATOTO HOME | http://www.educatingtanzaniafoundation.com/ (website in the contact profiles) | Checked for "Happy Watoto School", a grantee named in the 2026-09-22 run. Not mentioned. Organisation left unreached. |

## Blocked or unreadable sites

- habarifoundation.org: bot-verification page (not bypassed).
- totalgiving.co.uk (Sponsors of St Gabriel Home): HTTP 403.
- UK Charity Commission register (charity 1118031): HTTP 403 on 2026-09-22; not retried.
- arushacity.com charity listing: HTTP 526 (origin certificate error).
- theholyspiritsisters.org over https: TLS internal error. WebFetch upgrades to https, so the crawler's http copies were used; no workaround attempted.
- guidestar.org: email shown only to paying subscribers (not pursued).
- saveafricatanzania.weebly.com/contact.html: email hidden by Cloudflare email protection (not decoded).
- thesmallthings.org/contact: renders only in JavaScript (browser not used).
- betterplace.org project page: only navigation readable.
- Facebook and Instagram pages: recorded as official pages from search results or the organisation's site; not read (login wall).
- DNS failures: goodhopeorphanage.org, cometoafrica.org, ww1.sunriseforhope.org, esperofoundationtz.org, stgemma.org, kilicentre.org, stjosephorphanage.co.tz.
- sunriseforhope.org: https returns HTTP 522; http serves unrelated content (the domain no longer belongs to the organisation).
- cradleoflove.com: HTTP 403 (http) and connection refused (https) for the crawler.

## Organisations not reached

No search was spent and no organisation-specific source was in hand. Their only known sources are NIS register entries, which publish no contacts, or funders' IRS filings seen through ProPublica full-text search pages. Those pages were not re-fetched, because loading a search-results page would route a search around the cap.

- 13. HOSSANA HOME CARE FOUNDATION (5.6 km, ORG_9769a5d226dd529e)
- 15. KIKATITI HAPPY WATOTO HOME (6.7 km, ORG_f391af47444aa25c)
- 16. AFRICA NDOTO ORGANIZATION (7.2 km, ORG_856dedfa3d649047)
- 18. Mosses Confort Home Foundation (CHF) (9.0 km, ORG_523e74a4d1a84a75)
- 19. GRACIOUS GIVERS FAMILY (19.4 km, ORG_30b3480487614aca)
- 20. ROLINA ASSOCIATION FOR ORPHANS (21.7 km, ORG_37336aeecdf95525)
- 21. EMUNYANI CHARITY (21.8 km, ORG_f255ef80d21e5935)
- 26. Arnold House AIDS Orphanage (Moshi) (22.8 km, ORG_9cfe0f232fd76523)
- 27. Asali partner community centre, Majengo (Moshi) (22.8 km, ORG_cae06d3f38ed8a69)
- 28. Better Future International Tanzania (Moshi) (22.8 km, ORG_2c70b6e07a808e15)
- 29. Children of Destiny Foundation / New Life Christian Children's Home (Moshi) (22.8 km, ORG_984f4011ee757661)
- 30. Grace Orphanage (Moshi) (22.8 km, ORG_03833d9c493885ff)
- 32. OMAWA (Moshi) (22.8 km, ORG_c6fd4d5b2682a52a)
- 33. St Joseph Shelter of Hope (Moshi) (22.8 km, ORG_7c5c6d4ad07be87e)
- 34. St Joseph's Children's Home (Franciscan Sisters of St Joseph, Moshi) (22.8 km, ORG_77a5a91149309e27)
- 35. Tanzania Women Research Foundation (Moshi) (22.8 km, ORG_5fb09394b46c9b5f)
- 36. VOV Center (Moshi) (22.8 km, ORG_72d04c7ad70ddb32)
- 37. ZORAH ORGANIZATION (23.7 km, ORG_7b2067e3c63db4b9)
- 38. Comfort Watoto Foundation [COWAFO] (23.8 km, ORG_4e8fb3efbbc9b9ad)
- 39. LIFE SUPPORT FOR CHANGE (LSFORC) (23.8 km, ORG_9298cd45ad7280fb)
- 40. Amazing Grace Widows and orphans Tanzania (24.3 km, ORG_76dabf896c4f3048)
- 41. INITIATIVE FOR YOUTH (INFOY) (24.5 km, ORG_e49bccdfeb8f4926)
- 42. Tansania Laechelt Organization (24.5 km, ORG_6af26d76ae196a08)
- 43. KILIMANJARO AID PROJECT (25.7 km, ORG_502aeb8ec711ef01)
- 44. Kilimanjaro Foundation (27.1 km, ORG_41073d3bf0b36551)

## Problems and warnings

- **Stopping rule unmet.** The 10-search allowance ran out at organisation 12 (TATA Children Organization, 4.1 km); 25 organisations were not reached.
- **Closed:**
  - Cradle of Love Baby Home closed at the end of March 2024.
  - Watoto Kicheko no longer admits children and no longer takes donations, so it no longer operates as an orphanage. Its charity continues a community project.
- **Domain that changed hands.** sunriseforhope.org now serves an unrelated Indonesian shortlink login; nothing from it was used.
- **Possibly outside the catchment.** The only match for T.H.T.O is Tumaini Home at Mto wa Mbu, about 115 km west of Arusha. Identity is uncertain, so its routes will not merge.
- **Related records** (flagged "possible duplicate for outreach"; not merged):
  - Happy Family Children's Village is a programme of The Small Things, which has its own welfare record.
  - Kitaa Hope Home's only route is the inbox of Hope Home Trust, which also has its own record.
- **Not merged.** "Good Hope Centre" (Usa River) is a different organisation from Good Hope Orphanage, School & Clinic.
- **Stale sources:**
  - St Joseph's (Kiserian): phone and P.O. Box from a 2014 blog.
  - Holy Spirit Sisters site: 2013, with a 2020 update.
  - Good Hope: 2012.
  - Espero: 2013.
  - Kilimanjaro Centre: 2013.
  - Rainbow Centre blog: 2010.
  - St Gabriel updates: 2010.
- **Safeguarding.** No new concerns found. St. Gabriel Home's client group was deliberately not recorded (family circumstances). Sponsorship, adoption and children's pages were not read for content.
- **Privacy decisions.** None of the following was recorded:
  - personal webmail of named people: the St Joseph's director; Tumaini Home's Norwegian board
  - residential-looking street addresses: the Holy Spirit Sisters in Portland; Hope Home Trust in Brighton; The Small Things in Branford CT
  - family relationships on Kitaa's staff page, or the person named there only as responsible for day-to-day running (no formal title)
  - Save Africa's two co-founders (current roles not stated)
  - FFHIA's Arusha team (not linked to Kim Jones House)
- **Tooling notes:**
  - `contact_lib.clean_person` drops "Ståle Anda" (Tumaini Home) because its name pattern accepts only ASCII letters. Names with letters such as å, ø or é will be lost in any slice.
  - Tumaini Home prints one Tanzanian number as "+225 759605561" (probably +255). It was recorded as printed.
- **Planner effect.** Every line in this file counts as "researched" for `plan_contact_research.py`, including the organisations covered by fetches only (searches_used 0). These still deserve a search and must be re-added by hand if wanted:
  - Habari Foundation (Moshi)
  - Kilimanjaro Centre for Orphans and Street Children
  - Rainbow Centre
  - Kim Jones House
  - Olasiti Orphans Center
  - Kitaa Hope Home
  - St. Joseph's Orphanage (Kiserian)

## Next-run priorities

- **Search the unreached organisations, nearest first:**
  - HOSSANA Home Care Foundation
  - KIKATITI HAPPY WATOTO HOME. Unverified hints: the 2026-09-22 run found an Educating Tanzania Foundation grantee "Happy Watoto School" and a ROAM Humanitarian orphanage and school in Kikatiti.
  - Africa Ndoto Organization
  - Mosses Confort Home Foundation
  - Gracious Givers Family
  - Rolina Association for Orphans
  - Emunyani Charity (active in 2025 with student-support projects)
  - the Moshi funder-filing grantees:
    - Arnold House, Asali partner centre, Better Future International, Children of Destiny
    - Grace Orphanage, OMAWA, St Joseph Shelter of Hope, St Joseph's Children's Home
    - Tanzania Women Research Foundation (NIS: OVC shelter project 2024-2025), VOV Center
  - Zorah, COWAFO
  - Life Support for Change (NIS projects into 2026, volunteer programme)
  - Amazing Grace Widows and Orphans (volunteer programme 2025)
  - INFOY
  - Tansania Laechelt (international NGO)
  - Kilimanjaro Aid Project
  - Kilimanjaro Foundation
- **Second searches worth spending:**
  - The Small Things' Tanzanian email or phone (Happy Family Children's Village, 0.9 km from Usa River)
  - a Tanzanian phone for Sun of Hope (0.9 km) and for Save Africa Orphanage (0.9 km)
  - an email or phone for Olasiti Children's Foundation
  - a current contact for St. Gabriel Home (St Gemma Galgani Sisters)
  - an alternative page for Habari Foundation (Moshi), which pays primary school fees for 40 pupils
- **Possible new lead outside the slice.** "Good Hope Centre", Usa River (a 2008 supporter page names its founder and a website, good-hope-centre.com, which was not checked). Verify it before adding.
- **School-fit signals seen:**
  - Sun of Hope has pre-school classrooms, and its parent body's site lists a Sun of Hope Primary School.
  - The Small Things runs a daycare and pre-primary school.
  - Olasiti pays secondary tuition.
  - Kitaa pays private primary fees (2026-09-22 run).
  - Save Africa's funder sponsors pupils at private schools (2026-09-22 run).
