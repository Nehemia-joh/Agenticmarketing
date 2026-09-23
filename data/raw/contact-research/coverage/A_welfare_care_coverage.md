# Coverage log: slice A, welfare care (23 September 2026)

- Slice: `runtime/contacts/slices/welfare_care.json` (90 children's homes and family-based care programmes, nearest first)
- Output: `data/raw/contact-research/search_A_welfare_care_2026-09-23.jsonl`
- Search budget: 55 WebSearch calls; used so far: 55. WebFetch paced at one request per 2 seconds or slower per site.
- Organisations written: 68 of 90. Status counts: found 12, partial 20, not_found 33, blocked 3.
- Before searching, prior evidence was reused from `data/raw/welfare-research/research_*_2026-09-22.jsonl` (known sources and partner pages), so known pages were fetched without spending searches.
- NIS register profiles (`nis.jamii.go.tz/ngo_profile/<id>`) publish no email, phone or address (checked in the 2026-09-22 profile cache), so they were not refetched for contact data.
- People are recorded only from the organisation's own site, an official register or directory entry, or a parent body's official page. Names that appear only in press articles or on sponsor and funder pages are not recorded; the record's notes say where they appear.
- Nothing about children, parents or relatives was recorded; child sponsorship pages were skipped.

## Status definitions

- `found`: identity confirmed and at least one direct route (email or phone) published by the organisation, its parent body or an official register.
- `partial`: only indirect routes (website, official social page, postal address, contact form), or a direct route whose identity or source is uncertain.
- `not_found`: nothing usable found within the budget.
- `blocked`: the only promising sources refused automated reading.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/55 | `"Mother Kevina" Arusha` | 1. Mother Kevina Feeding Program-Centre | Snippet ties a Mama Kevina Feeding Program in Kijenge to the Little Sisters of St. Francis; their regional page is gone (domain for sale). not_found |
| Q2/55 | `"Fruitful Organization" Arusha` | 2. Fruitful Organization | Only Fruitful Orphanage pages; own site gives phone, PO Box and founder-director; link to the NIS name unproven. partial, identity uncertain |
| Q3/55 | `"Positive Steps in Arumeru" POSA Usa River` | 3. POSA - Positive Steps in Arumeru | Unrelated tourism results. not_found |
| Q4/55 | `"Seeway Tanzania" Usa River` | 4. Seeway Tanzania | Facebook and LinkedIn pages; LinkedIn gave swtz.org; PO Box, contact form and founders from own site. partial |
| Q5/55 | `"Laketatu Orphanage" Tanzania` | 5. Laketatu Orphanage | Only the Rotary sponsor page; no organisational contact route. not_found |
| Q6/55 | `"Ngarasero Community Organization" Usa River` | 6. Ngarasero Community Organization | Official Facebook page; press articles publish no contact route. partial |
| Q7/55 | `"St. Mark's Children's Home" Usa River Tanzania` | 7. St. Mark's Children's Home and Orphanage | Own site saintmarkskids.org found but renders only in JavaScript; funder page gives no contact route. partial |
| Q8/55 | `"His Healing Hands Africa" Arusha` | 8. His Healing Hands Africa Ministry | US parent (His Healing Hands Inc, dba Falco's Children Africa) named; its page unreadable. not_found |
| Q9/55 | `"Bright Hope Children Foundation" Arusha` | 9. Bright Hope Children Doundation | Facebook page 'BrightHope Children Organization', Arusha. partial, identity uncertain |
| Q10/55 | `"Gladness Kanyika" Arusha` | 10. Gladness Kanyika Home Organization | Unrelated people only. not_found |
| Q11/55 | `"Sports Hostel Foundation" Tanzania` | 11. Sports Hostel Foundation | Unrelated hostels. not_found |
| Q12/55 | `"Caroryan Foundation" Arusha` | 12. Caroryan Foundation | Other foundations only. not_found |
| Q13/55 | `"Me and Orphans Tanzania" Arusha` | 13. Me and Orphans Tanzania | Other orphanages only. not_found |
| Q14/55 | `"HopeCare" Arusha orphans Boma Road` | 14. HopeCare (Arusha) | Only differently named Hope organisations. not_found |
| Q15/55 | `"Convoy of Hope" Tanzania Arusha office` | 15. Convoy of Hope | Arusha main office confirmed by snippet; official site HTTP 403. blocked |
| Q16/55 | `"AREM Foundation" Arusha` | 16. AREM Foundation | Own site aremfoundation.or.tz (bot check) and Facebook page. blocked |
| Q17/55 | `"Green Path for Community Success" Arusha` | 17. Green Path for Community Success (GP-COSU) | Own site: phone, email, PO Box, registration, founder-director. found |
| Q18/55 | `"Osiligi" orphanage Arusha` | 19. Osiligi Orphanage Center | Own site (domain not resolving), Facebook and X pages; Idealist listing gives phone and founder. found |
| Q19/55 | `"Amazing Children's Home" Arusha` | 20. Amazing Children's Home | Only differently named homes. not_found |
| Q20/55 | `"Choose Love" home orphans Arusha Tanzania` | 21. Choose Love home for orphans | No match; surfaced a Lief Foundation page on Paradiso Orphanage (used for #28). not_found |
| Q21/55 | `"Tupendane Orphanage" Arusha` | 22. Tupendane Orphanage | Only Tupendane Africa Foundation (2022, women's empowerment), probably different. not_found |
| Q22/55 | `"Holley Children" orphanage Arusha` | 23. Holley Children Orphanage | Other orphanages only. not_found |
| Q23/55 | `"Faraja Support for Needy Children and Orphans" Arusha` | 25. Faraja Support for Needy Children and Orphans (FSNO) | Only 'Faraja Orphanage Children's Home'; email and mobile in snippet; link to registration unproven. partial, identity uncertain |
| Q24/55 | `"It Takes a Whole Village" children's home Arusha Tanzania` | 27. Arusha Children's Home (It Takes a Whole Village Kids) | Nothing new; Facebook page only. partial |
| Q25/55 | `"Matonyok Children's Home" Arusha` | 29. Matonyok Children's Home | Own domain listed but does not resolve; Facebook page. partial |
| Q26/55 | `"Paradiso Orphanage" Arusha` | 28. New Paradiso Orphanage | Supporter and volunteer pages, LinkedIn and Facebook pages; no contact route. partial, identity uncertain |
| Q27/55 | `"Karim Children's Care Centre" OR "Karim Children Care Center" Arusha` | 31. Karim Children's Care Centre | Own domain karimchildren.org (does not resolve) and Facebook page. partial |
| Q28/55 | `"Mama Jane's Orphanage" Arusha` | 32. Mama Jane's Orphanage | Only Uganda/Kenya namesakes. not_found |
| Q29/55 | `"Malaika Orphanage" Arusha Tanzania` | 33. Malaika Orphanage (Arusha) | Candidates only (Malaika Children's Friends, African Malaika; a Johannesburg namesake ruled out). not_found, identity uncertain |
| Q30/55 | `"Victoria's Giving Foundation" Arusha` | 34. Victoria's Giving Foundation | Unrelated namesakes. not_found |
| Q31/55 | `"Levites Children Foundation" Arusha` | 35. Levites Children Foundation | Unrelated Levites organisations. not_found |
| Q32/55 | `"Lengijabe" children Arusha` | 36. Lengijabe Children's Volunteering Relief | Place name only. not_found |
| Q33/55 | `"Sinoni Ngarashi" orphans organization` | 37. Sinoni Ngarashi Education and Orphans Organization | Own site: email, two phones, PO Box, office, founder and board officers. found |
| Q34/55 | `"Ebenezer Orphanage Centre" Arusha OR Arumeru` | 39. Ebenezer Orphanage Centre | Facebook page 'Ebenezer Orphanage and Day Care'; supporter page 404. partial, identity uncertain |
| Q35/55 | `"Terence G. Klingele Foundation" Tanzania` | 40. The Terence G. Klingele Foundation | Own site: general email and socials; private-school scholarships. found |
| Q36/55 | `"Ndovu Foundation" Arusha` | 41. Ndovu Foundation | Unrelated Ndovu companies. not_found |
| Q37/55 | `"Meru Peak Foundation" Tanzania` | 42. Meru Peak Foundation | Mount Meru travel pages only. not_found |
| Q38/55 | `"Tanzania Youth Support and Self Reliance Organization"` | 43. Tanzania Youth Support and Self Reliance Organization | Own site: email, two phones, Maji ya Chai. found |
| Q39/55 | `"Huruma" children's home Arusha Muriet OR "Kwa Mrombo" OR Morombo` | 38. Huruma Vision Children's Home | Official Facebook page only; Kenyan namesake ignored. partial |
| Q40/55 | `"Shalom Center" Kisongo Arusha` | 44. Shalom Center (Kisongo) | Only a Karatu namesake with its own site; Kisongo source is a blocked forum complaint. not_found |
| Q41/55 | `"Arusha Child Rights Organization" ACRO` | 45. Arusha Child Rights Organization (ACRO) | Described in a Norwegian partner letter; no contact route. not_found |
| Q42/55 | `"Zoe Africa" Arusha Tanzania` | 46. Zoe Africa (TZ) | Safari company only. not_found |
| Q43/55 | `"Hope Sunshine Foundation" Arusha` | 47. Hope Sunshine Foundation | Differently named Hope organisations. not_found |
| Q44/55 | `"Precious Orphans Children" POCH Arusha` | 48. Precious Orphans Children (POCH) | Other orphanages only. not_found |
| Q45/55 | `"Moshono Children Foundation" Arusha` | 49. Moshono Children Foundation | Other Moshono organisations only. not_found |
| Q46/55 | `"Nice Orphans Centre" Arusha OR Arumeru` | 50. Nice Orphans Centre | Other orphanages only. not_found |
| Q47/55 | `"Ikunda" orphans children organization Arusha` | 52. Ikunda Needs and Orphans Children Organization | Facebook fundraiser page with the exact name. partial |
| Q48/55 | `"Siouxland Tanzania Education Medical Ministries"` | 53. Siouxland Tanzania Education Medical Ministries (STEMM) | Own site: office email, US phone, PO Box, In-Country Director and Tanzania board chair. found |
| Q49/55 | `"Kalali Orphanage" Tanzania` | 54. Kalali Orphanage | Run by Ushirika wa Neema (ELCT Northern Diocese); head named in its 2017 report; no contact route. partial |
| Q50/55 | `"Share Children's Villages" Tanzania Moshi` | 55. Share Children's Villages Foundation | Own site (Share Tanzania): enquiries email, socials, founder. found |
| Q51/55 | `"Tunajali Foundation" Arusha OR Arumeru OR Tanzania` | 56. Tunajali Foundation | Tunajali Tanzania (Moshi) with email and phone; link to the Arumeru register entry unproven. partial, identity uncertain |
| Q52/55 | `"Candenez Mission" vulnerable children` | 57. Candenez Mission for Empowering Vulnerable Children | Own site: registration match, email, phone, PO Box, Kijenge Juu office. found |
| Q53/55 | `"Children Must Live" Tanzania Siha` | 58. Children Must Live-Tanzania (CML-T) | International charity (Sofia) email and phone; no Tanzanian details. partial, identity uncertain |
| Q54/55 | `"Upendo Foundation Australia" children's home Tanzania` | 59. Upendo Foundation Australia Children's Home (UFACH) | Own site: email, Australian phone, socials, chair and treasurer. found |
| Q55/55 | `"Samaritan Children's Home" Arumeru OR Arusha Tanzania` | 60. The Samaritan Children's Home (TSCH) | Only Samaritan Village (already held); not merged. not_found. Search budget exhausted after this query. |

## Fetches without a search

| Organisation | URL | Outcome |
|---|---|---|
| 2. Fruitful Organization | https://fruitful-orphanage.jimdoweb.com/ (home, /contact-information/, /our-team/) | Phone, PO Box, founder-director; emails hidden by email protection |
| 2. Fruitful Organization | https://arushakids.com/about-us/ | No registered name or number |
| 5. Laketatu Orphanage | https://papamoarotaryclub.co.nz/laketatu-orphanage-usa-river-tanzania/ | Sponsor page; no organisational contact route |
| 6. Ngarasero Community Organization | https://tanzaniainsight.com/20-vulnerable-children-in-usa-river-seek-education-sponsorship/ and https://dailynews.co.tz/care-centre-seeks-sponsors-for-children/ | No contact route published |
| 7. St. Mark's Children's Home | http://saintmarkskids.org/ and https://saintmarkskids.org/contact | Empty script-only pages |
| 7. St. Mark's Children's Home | https://www.utopiafound.org/programs/st-marks-childrens-home | Funder page; no contact route |
| 8. His Healing Hands Africa Ministry | https://asiministries.org/project/his-healing-hands-inc-dba-falcos-children-africa-inc/ | Body not readable (truncated twice) |
| 17, 28, 30 (Heart for Africa homes) | https://www.heartforafrica.co.uk/orphanages | Supporter page; no contact details for the homes |
| 15. Convoy of Hope | https://convoyofhope.org/wp-content/uploads/2015/10/2017-Tanzania-Trip-Guide.pdf | 2017 trip guide; only US staff contacts (not recorded) |
| 18. Tumaini For Africa Orphanage | https://www.loveourtanzaniafamily.org/ | Dedicated US support charity: email, socials, founder and director named. found (no search) |
| 19. Osiligi Orphanage Center | https://www.idealist.org/es/ong/73c7293f69a34bd4b0e33e686a60c007-osiligi-children-foundation-arusha | Listing for 'Osiligi Children Foundation', Moivaro: phone and founder (URL seen in Q9 results) |
| 19. Osiligi Orphanage Center | https://osiligichildrenfoundation.org | Domain does not resolve |
| 24. One Heart Source | https://www.oneheartsource.org/ (home, /contact/, /about/) | General email and US mailing address; site no longer mentions Tanzania. partial (no search) |
| 28. New Paradiso Orphanage | https://liefinc.org/paradiso-orphanage-arusha-tanzania/ | Supporter page on 'Paradiso Orphanage', Arusha; no contact details |
| 19. Osiligi Orphanage Center | https://osiligichildrenfoundation.org/ (second attempt) | Domain still does not resolve |
| 26. Karama Kids | https://www.karamaconnection.org/why-karama/ and /contact/ | Parent charity: named work email, US phone, socials. found (no search) |
| 29. Matonyok Children's Home | https://havenofhopeintl.org/matonyok-childrens-home/ | Password-protected |
| 29. Matonyok Children's Home | https://servingorphans.org/matonyok-childrens-home-tanzania/ | Funder page; only funder's US contacts |
| 31. Karim Children's Care Centre | https://www.readwithmearusha.com/where-we-work/karim-orphanage/ | Supporter page; no contact route |
| 51. Themi Youth Orphanage | https://iantaylortrekking.com/blog/help-children-while-visiting-kilimanjaro/ (seen in Q13 results) | Supporter blog; gives 'Themi Orphanage Center' Facebook page |
| 25. FSNO | https://www.farajaorphanagechildrenshome.org/, https://farajaorphanage.org/, https://ngobase.org/profile/24648 | First domain does not resolve; second shows title only; ngobase has no registration details |
| 28. New Paradiso Orphanage | https://euprogresweb.wixsite.com/paradisorphanage, https://yallagive.com/en/charity/new-paradise-orphanage, https://newparadiseorphanage.wixsite.com/orphanage | Volunteer site; listing with LinkedIn page; linked Wix site 404 |
| 30. Bethlehem Center for Children | https://ngobase.org/profile/316200 | Facebook page only (no search spent) |
| 31. Karim Children's Care Centre | https://e-ducare.org/programmes/karim-orphanage-support/ and http://karimchildren.org/ | Supporter page without contacts; own domain does not resolve |
| 33. Malaika Orphanage (Arusha) | https://impala.digital/public/profiles/01-0832165/programs, https://malaikaskids.org/about/ and /contact-us/, http://africanmalaika.blogspot.com/ | Karama 2023 filing text; Johannesburg namesake ruled out; Ndoombo blog inactive since 2012 |
| 38. Huruma Vision Children's Home | https://terrawatu.org/current-projects/huruma-orphanage | Supporter page; no contact route |
| 37. Sinoni Ngarashi | https://www.sinonngarashied.or.tz/ and /our-team/ | Contacts and leaders |
| 40. Terence G. Klingele Foundation | https://www.tgklingele.org/ and /our-story | Email, socials; no Tanzanian office or staff |
| 43. Tanzania Youth Support | https://tanzaniayouthsupport.org/ | Email, phones, location |
| 39. Ebenezer Orphanage Centre | https://www.childrenofafrica.asso.mc/ebenezer-orphanage/; https://www.ebenezerlifecenter.org/; https://ebenezerlifecenter.org/ | 404; www host does not resolve; bare domain ECONNRESET |
| 44. Shalom Center (Kisongo) | https://shalomcenter.or.tz/ | Karatu namesake (not merged) |
| 45. ACRO | https://ngobase.org/stwa/TZ.AR/RGT/rights-ngos-charities-arusha-region; Horten vgs NN-dagen 2024 PDF; https://www.nn.no/ | Not listed; partner letter describes ACRO; partner site has no ACRO contact |
| 51. Themi Youth Orphanage | https://iantaylortrekking.com/blog/help-children-while-visiting-kilimanjaro/ (fetched earlier, seen in Q13 results) | Facebook page of 'Themi Orphanage Center'. partial, identity uncertain (no search) |
| 52. Ikunda | https://www.arushakidstrust.com/ | Supports Save Africa Orphanage, not Ikunda |
| 53. STEMM | https://stemm.org/, /stemm-contact, /stemm-team; https://ngobase.org/profile/317862 | Contacts and leaders; directory gives Arusha |
| 54. Kalali Orphanage | DRAE 2017 report PDF (text read locally from the fetched file); marafiki-tz-a-janosch.eu Neu-Kalali page | Parent community and its head (2016); location |
| 55. Share Children's Villages | https://www.sharetanzania.co.uk/ and /contact-us | Email, socials, founder; contact page 404 |
| 56. Tunajali Foundation | https://www.tunajali-tanzania.com/ | Email, phone, socials, Moshi |
| 57. Candenez | https://candenez.or.tz/ and /about-us/ | Contacts; no named leaders |
| 58. CML-T | https://childrenmustlive.com/ | International office contacts only |
| 59. UFACH | https://www.upendo.org.au/ and /meet-our-team | Email, phone, socials, board officers |
| 61. One Love Africa Foundation | https://www.onelovetanzania.com/about (URL seen in Q54 results) | One Love Tanzania (Moshi): site and socials; personal contacts not recorded. partial, identity uncertain |
| 66. TAG Kilimanjaro Revival Temple centre | https://dailynews.co.tz/centre-transforms-over-400-childrens-lives/ and https://allafrica.com/stories/202609140381.html | HTTP 500; republication has no contact route. not_found |
| 68. Matumaini Child Care | http://ccsrauorphanages.blogspot.com/ | 2007 third-party blog; stale personal contact not recorded. not_found |
| 71. Upendo One Kid at a Time | https://upendookat.com/ | Email, US mailbox, founder. found |
| 75. Bahath Orphanage | https://www.world-unite.de/en/internships-volunteering/tanzania-moshi/orphanages-street-children.html | HTTP 403. blocked |
| 76. Kili Kids at Rainbow Ridge | https://gogetfunding.com/kili-kids/ | 2017 appeal; no organisational route. not_found |
| 89. Home Foundation (Rhotia) | https://www.idealist.org/en/nonprofit/bba9c335f6e447ce813df044688d843a-home-foundation-arusha | Location only. not_found |
| 90. Huruma Centre Orphanage (Iringa) | https://www.h2oforlifeschools.org/projects/885 | Operator and town only; out of catchment. not_found |

## Blocked or unreadable sites

- envaya.org/fruitfulorphanage: TLS certificate expired (not read).
- fruitfulorphanage.or.tz: TLS certificate expired per the 2026-09-22 run (not retried).
- tanzania.worldplaces.me: HTTP 429 Too Many Requests (not retried).
- lsosfi.org: domain parked ('This domain may be for sale'); page content gone.
- Facebook pages: recorded as official social pages from search results or the organisation's site; not read (login wall).
- saintmarkskids.org: renders only in JavaScript; fetch returns an empty shell (browser not used).
- asiministries.org project page: content truncated by the fetch tool; only the header was readable.
- aremfoundation.or.tz: bot-verification page ('Verifying that you are not a robot'); not bypassed.
- convoyofhope.org: HTTP 403 Forbidden.
- osiligichildrenfoundation.org: DNS lookup failed twice (ENOTFOUND).
- havenofhopeintl.org/matonyok-childrens-home/: password-protected (not bypassed).
- matonyokchildrenshome.org and www.farajaorphanagechildrenshome.org: DNS lookup failed (ENOTFOUND).
- farajaorphanage.org: only the page title readable (probably script-rendered).
- karimchildren.org: DNS lookup failed (ENOTFOUND).
- childrenofafrica.asso.mc/ebenezer-orphanage/: HTTP 404.
- ebenezerlifecenter.org: www host does not resolve; bare domain reset the connection (ECONNRESET); not retried.
- Local DNS check (nslookup) confirmed that matonyokchildrenshome.org, osiligichildrenfoundation.org, karimchildren.org and www.farajaorphanagechildrenshome.org do not resolve, so these domains appear to have lapsed.
- jamiiforums.com: blocks automated reading (not fetched; per the rate-limits note).
- sharetanzania.co.uk/contact-us: HTTP 404.
- world-unite.de: HTTP 403 Forbidden.
- dailynews.co.tz (TAG centre article): HTTP 500 on 2026-09-23 (the republication on allafrica.com was read instead).

## Organisations not reached

- 62. ROLINA ASSOCIATION FOR ORPHANS (21.7 km, ORG_37336aeecdf95525)
- 63. EMUNYANI CHARITY (21.8 km, ORG_f255ef80d21e5935)
- 64. Grace Orphanage (Moshi) (22.8 km, ORG_03833d9c493885ff)
- 65. Better Future International Tanzania (Moshi) (22.8 km, ORG_2c70b6e07a808e15)
- 67. Tanzania Women Research Foundation (Moshi) (22.8 km, ORG_5fb09394b46c9b5f)
- 69. VOV Center (Moshi) (22.8 km, ORG_72d04c7ad70ddb32)
- 70. St Joseph's Children's Home (Franciscan Sisters of St Joseph, Moshi) (22.8 km, ORG_77a5a91149309e27)
- 72. St Joseph Shelter of Hope (Moshi) (22.8 km, ORG_7c5c6d4ad07be87e)
- 73. Children of Destiny Foundation / New Life Christian Children's Home (Moshi) (22.8 km, ORG_984f4011ee757661)
- 74. Arnold House AIDS Orphanage (Moshi) (22.8 km, ORG_9cfe0f232fd76523)
- 77. Habari Foundation (Moshi) (22.8 km, ORG_bcd1cf9aa70de22f)
- 78. OMAWA (Moshi) (22.8 km, ORG_c6fd4d5b2682a52a)
- 79. Asali partner community centre, Majengo (Moshi) (22.8 km, ORG_cae06d3f38ed8a69)
- 80. Kim Jones House (orphanage), Moshi (22.8 km, ORG_cc4f8524a58350f4)
- 81. ZORAH ORGANIZATION (23.7 km, ORG_7b2067e3c63db4b9)
- 82. Comfort Watoto Foundation [COWAFO] (23.8 km, ORG_4e8fb3efbbc9b9ad)
- 83. LIFE SUPPORT FOR CHANGE (LSFORC) (23.8 km, ORG_9298cd45ad7280fb)
- 84. Amazing Grace Widows and orphans Tanzania (24.3 km, ORG_76dabf896c4f3048)
- 85. Tansania Laechelt Organization (24.5 km, ORG_6af26d76ae196a08)
- 86. INITIATIVE FOR YOUTH (INFOY) (24.5 km, ORG_e49bccdfeb8f4926)
- 87. KILIMANJARO AID PROJECT (25.7 km, ORG_502aeb8ec711ef01)
- 88. Kilimanjaro Foundation (27.1 km, ORG_41073d3bf0b36551)

## Problems

- Stopping rule unmet: the 55-search budget ran out at organisation 60 (21.0 km). 22 organisations (numbers 62-88, listed above) were not reached. Their only known sources are NIS register entries, which publish no contacts, or ProPublica full-text search pages. Those pages were not re-fetched, because loading a search-results page would route a search around the cap.
- Lapsed own domains (confirmed with a local DNS lookup): matonyokchildrenshome.org, osiligichildrenfoundation.org, karimchildren.org and www.farajaorphanagechildrenshome.org. saintmarkskids.org and farajaorphanage.org render only in JavaScript. A browser was not used.
- Identity left uncertain rather than merged: Fruitful Organization vs Fruitful Orphanage (Duluti); FSNO vs Faraja Orphanage Children's Home; Malaika Orphanage (Karama grantee) vs Malaika Children's Friends or African Malaika; Shalom Center (Kisongo) vs Shalom Orphanage Centre (Karatu); Tunajali Foundation vs Tunajali Tanzania (Moshi); CML-T vs Children Must Live (Sofia); One Love Africa Foundation vs One Love Tanzania; Themi Youth Orphanage vs Themi Orphanage Center; Ebenezer Orphanage Centre vs Ebenezer Orphanage and Day Care; New Paradiso vs Paradiso/Paradise Orphanage Centre; The Samaritan Children's Home vs Samaritan Village; Tupendane Orphanage vs Tupendane Africa Foundation.
- Slice data to review: Tanzania Youth Support and Self Reliance Organization describes vocational training, not residential care. Sinoni Ngarashi's office is in Monduli town and Candenez's head office is in Kijenge Juu, so their register map pins mislead on distance. His Healing Hands' home may be in Karatu. Home Foundation (Rhotia, about 110 km) and Huruma Centre (Iringa, about 500 km) are outside the catchment. Shalom Center (Kisongo) is known only from an unverified abuse-allegation forum thread; review before any outreach.
- Privacy decisions: names appearing only in press articles or on sponsor and funder pages were not recorded as contact leads (Laketatu, Ngarasero, St. Mark's, Karim, Huruma Vision, Matonyok, Ebenezer, Paradiso). Private-looking street addresses of small foreign support charities (Love Our Tanzania Family, Karama Connection, Share Tanzania, Children Must Live, One Love Tanzania) and One Love Tanzania's personal ISP email were not recorded. Family relationships, biographies and staff below leadership level were left out.
- Parent-body judgement calls, flagged in each record: Love Our Tanzania Family (dedicated US charity of Tumaini For Africa), Karama Connection (founded and runs Karama Kids), Ushirika wa Neema (runs Kalali Orphanage) and UPENDO: One Kid at a Time were treated as parent bodies. Their routes reach the US, Australian or UK charity rather than a Tanzanian office in most cases.
- Three PDFs came back from the fetch tool as binary. Their text was read locally from the fetched copies (the Convoy of Hope trip guide, the Norwegian school letter on ACRO and the DRAE deaconess report); nothing was saved to the repository.
- Several email routes are organisational mailboxes on webmail domains (gmail or outlook) for GP-COSU, Love Our Tanzania Family, Faraja and UPENDO OKAT. They are labelled general, not named.

## Next-run priorities

- Search the 22 unreached organisations, nearest first: Rolina Association for Orphans, Emunyani Charity, Grace Orphanage (Moshi), Better Future International Tanzania, Tanzania Women Research Foundation, VOV Center, St Joseph's Children's Home (Moshi), St Joseph Shelter of Hope, Children of Destiny / New Life Christian Children's Home, Arnold House, Habari Foundation, OMAWA, Asali partner centre (Majengo), Kim Jones House, Zorah, Comfort Watoto Foundation, Life Support for Change, Amazing Grace Widows and Orphans, Tansania Laechelt, INFOY, Kilimanjaro Aid Project and Kilimanjaro Foundation.
- Second searches worth spending: Falco's Children Africa (parent of His Healing Hands Africa Ministry); Matonyok Children's Home (large home with a campus school, lapsed domain); Karim Children's Care Centre; Huruma Vision Children's Home; Arusha Child Rights Organization (a possible connector to many homes); the Faraja registration check; and asking Karama Connection which 'Malaika Orphanage' it funds.
- Fee-paying prospects found: The Terence G. Klingele Foundation (private-school scholarships), STEMM (sponsors about 500 secondary and university students a year), Tumaini For Africa (enrols children in private English-medium schools) and Karim Children's Care Centre (tuition sponsored by Read With Me Arusha).
