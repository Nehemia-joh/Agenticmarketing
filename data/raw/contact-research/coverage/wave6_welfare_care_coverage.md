# Coverage log: wave 6, welfare care (25 September 2026)

- **Slice:** `runtime/contacts/slices/wave6_welfare_care.json`, nearest first: 45 NGOs from the national NGO register whose type is not yet known (segment "Welfare (unclassified child-focused NGO)"), 2.9 to 6.7 km from a campus. Every one needed a published route; every `known_sources` list was empty.
- **Output:** `data/raw/contact-research/search_wave6_welfare_care_2026-09-23.jsonl`, one line per organisation researched, appended as the work went. The date key is the programme's shared key; the access date is 25 September 2026.
- **Searches:** allowance 42 WebSearch calls; used 42 (Q1/42 to Q42/42). The session cap refused none. After Q42 only URLs already in hand were fetched. No search was routed through WebFetch, a browser or a results page. Each query named one organisation. Q27 and Q35 joined that organisation's acronym and full name with OR.
- **Fetching:**
  - Pages were read with `scripts/contacts/read_page.py` (shared cache, 1.5 s spacing per site, robots.txt honoured), plus a small link, Cloudflare-email and raw-HTML reader in `runtime/contacts/agents/wave6_welfare_care/` that uses the same cached fetcher.
  - Cloudflare-protected addresses were decoded with `contact_lib.decode_cfemail`, as the crawler does.
  - robots.txt was read for every host and redirect hop. A 4xx robots.txt counted as no rules. No page was disallowed.
  - Two hosts failed on the local resolver while 1.1.1.1 resolved them: salaamafoundation.org and thekutamanifoundation.org. For these, curl resolved the name through 1.1.1.1 (DNS over HTTPS), with at least 2 s between requests. That changed only the name lookup; no block was passed. Both still failed, as the blocked-sites list below shows.
  - WebFetch was tried once, on salaamafoundation.org's robots.txt, and hit the same DNS failure.
- **Organisations written:** 43 of 45.
  - Status: found 11, partial 7, not_found 24, blocked 1.
  - Identity: confirmed 41, uncertain 2 (Salama Foundation Tanzania, MAMA ZETU FOUNDATION).
  - Not reached: 2 (see below).
- **Results:**
  - 59 named leads across 15 organisations; 55 come from fetched pages and 4 from snippets. PDPA risk: all 59 medium.
    - 31 lead the organisation (founders, directors, chairs, heads, managers, secretaries), across 14 organisations.
    - 18 are trustees or board members, from the UK Charity Commission register and two organisations' own sites.
    - 10 are coordinators, officers or team members.
    - 7 leads are named by first name only and will be labelled incomplete: Gem Legacy's Skyler and Pia, Nuru Yetu's Zauja, CHAYETEO's Weza, LISCO's Eva and Joyce, and New Stars' Elizabeth.
  - Direct routes: 19 emails and 13 phones for 12 organisations, all read on fetched pages (none snippet-only). Three emails are personal-domain (Gmail) inboxes named after the organisation or its programme: Hope and Soul, AFOTA and CHAYETEO's football academy.
  - Indirect routes: 14 websites, 3 postal and 8 physical addresses, and 33 official social links for 13 organisations.
  - Ndoto in Action needed no search. The funder page already cited in the welfare run's evidence (Vibrant Village Foundation, "Where we fund") links to its site.
- **Prior evidence read before any search:**
  - the slice
  - `data/raw/welfare-research/research_*.jsonl`: only Vibrant Village's link to Ndoto in Action is relevant
  - the earlier contact-research records: only wave 4's note that AFOTA is not Asante Africa is relevant
  - the NIS register profiles in `nis_catchment_profiles_2026-09-22.jsonl`, which give each entry's registration number, aims and projects but no contacts. All 45 organisations matched a profile by name.
  - `data/interim/welfare-leads/welfare_organisations.tsv`, read only, to check for twins (Good Hope Kiwawa has none)
- **Recording rules applied:**
  - People come only from the organisation's own site (including its programme's site, or text its own pages render), an official register (the UK Charity Commission) or search snippets of those pages.
  - Not recorded as leads: names on press, podcast, Wikipedia, supporter or venture-funder, marketplace and data-broker pages (ZoomInfo).
  - Also not recorded: biographies, family ties, ages, personal-profile LinkedIn links, home-looking street addresses (Hope and Soul's UK register address, Dyslexia Tanzania's house number), and staff outside outreach (teachers, cooks, caretakers, instructors, volunteers, media staff).
  - Nothing about children, parents or residents was recorded. Pages about individual children were not opened.
  - Every note keeps its warnings within its first 600 characters, the part the profile builder keeps; no note is longer than 600 characters. Warning phrases were checked against `contact_lib.note_flags`.

## Status definitions

- `found`: identity confirmed, and at least one email or phone read on a page published by the organisation (or its own programme), its parent body or an official register.
- `partial`: only indirect routes (website, official social page, postal address), a route from a directory, or leads without a route.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading. Blocked sites with other evidence are marked partial.

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| Q1/42 | `"Salama Foundation Tanzania" Arusha` | 1. Salama Foundation Tanzania | Candidate site salaamafoundation.org ("Islamic charity in Arusha", snippet): the local resolver answers SERVFAIL; 1.1.1.1 resolves it but the TLS handshake fails (fatal alert), so it was not read. Gender Links' national GBV 'Salama Foundation' is not placed in Arusha. A Daily News Arusha article answered HTTP 500. blocked, uncertain |
| Q2/42 | `"Hope and Soul Tanzania" Arusha` | 2. Hope and Soul Tanzania | UK charity 1173832: the register gives a Gmail inbox, a UK mobile and 8 trustees (its residential address was not recorded). Own site hopeandsoul.org.uk shows I-NGO/R/2104 (match), an inbox, Facebook and Instagram. found |
| Q3/42 | `"Uplifting and Nurturing Them" Arusha` | 3. Uplifting and Nurturing Them | No match (unrelated schools, orphanages, a church). not_found |
| Q4/42 | `"Acha Wacheze" Arusha` | 4. ACHA WACHEZE | No match (general Arusha pages, forums). not_found |
| Q5/42 | `"Dyslexia Tanzania" Arusha` | 5. DYSLEXIA TANZANIA | Own site dyslexiatanzania.org is script-built; its public JS bundle gives inbox, mobile, Instagram, Facebook and the founder. The house-number address was not recorded; the team CMS API (needs a key) was not read. found |
| Q6/42 | `"Gem Legacy" Arusha Tanzania` | 6. GEM LEGACY INC | Own site gemlegacy.org: inbox, Facebook, YouTube; leadership page gives the executive director, two East Africa directors, two first-name staff leads and 5 board members. found |
| Q7/42 | `"Help for the Maasai" Arusha` | 7. HELP FOR THE MAASAI ORGANIZATION | No match (ALMASI, MAA Eagle, Emusoi, Nadumu are different). not_found |
| Q8/42 | `"Maasai Women and Children Initiative" MWACI Arusha` | 8. MWACI | Own site mwaci.org: 3 inboxes, mobile, office in Arusha Mall; chairperson, secretary and 3 members. found |
| Q9/42 | `"Nuru Yetu Foundation" Arusha` | 9. NURU YETU FOUNDATION | Own site: 4 inboxes, mobile, socials, 5 leads. It gives Dar es Salaam as its location (location to check). found |
| Q10/42 | `"OKIA Tanzania" Arusha` | 10. OKIA TANZANIA | Instagram @okiatanzania (Arusha) only. partial |
| Q11/42 | `"Benjamin Runga Foundation" Tanzania` | 11. Benjamin Runga Foundation | Own site: inbox, 2 mobiles (WhatsApp), Sinoni address, socials; about page confirms 00NGO/R/2682; 9 leads. The ZoomInfo result was not used. found |
| Q12/42 | `"Furahia Mtoto Foundation" Tanzania` | 12. FUMFO | Own site furahiafoundation.org answered HTTP 403. The snippet gives registration 00NGO/R/842 (match) and the founder. partial |
| Q13/42 | `"CHAYETEO" Arusha` | 13. CHAYETEO | Its football programme's site satinofootballacademy.com ('exists under CHAYETEO'): Gmail inbox, Sinoni address, founder 'Weza'. found |
| Q14/42 | `"Empact Foundation" Arusha` | 14. Empact Foundation | No match (EMpact One Foundation, Arkansas, is different). not_found |
| Q15/42 | `"Every Child Count" Arusha FGM` | 15. Every Child Count | No match (general anti-FGM reports). not_found |
| Q16/42 | `"Life Bridge Foundation" Arusha` | 16. LIFE BRIDGE FOUNDATION | Namesakes only; lifebfoundation.org is an Islamabad NGO (read and rejected). not_found |
| Q17/42 | `"Light for Many" Arusha Tanzania` | 17. LIGHT FOR MANY | No match (tour operators, a solar company). not_found |
| Q18/42 | `"Safaris with a Heart" Arusha` | 18. SAFARIS WITH A HEART | The Arusha safari company of the same name funds 'our Tanzanian charity projects'. Its contact page names the Tanzania and US office managers, with named inboxes and phones; socials. found (segment to check) |
| Q19/42 | `"Bandari ya Maendeleo" Arusha` | 19. THE BANDARI YA MAENDELEO ORGANIZATION | No match (port-authority news). not_found |
| Q20/42 | `"Good Hope Kiwawa Foundation"` | 20. GOOD HOPE KIWAWA FOUNDATION | Facebook page 'Good Hope Kiwawa Children Home, Usa River'. Its site goodhopekiwawa.org no longer resolves. The snippet gives a Momella Road address, the founder, and a move towards a vocational learning centre. partial |
| Q21/42 | `"Starving Children" Arusha Orkisima mother and child` | 21. Starving children | No match (general hunger reports, other orphanages). not_found |
| Q22/42 | `"Kalulu Charitable Foundation" Siha` | 22. KALULU CHARITABLE FOUNDATION | No match (other SIHA bodies). not_found |
| Q23/42 | `"Ahsante Foundation Tanzania" Arusha` | 23. AFOTA | Own site afotatz.org: inbox, a Gmail inbox named after it, 2 phones, Bondeni Street office, PO Box 12948; chair and founder, executive secretary. Asante Africa's details, which the result summary mixed in, were not used. found |
| Q24/42 | `"Lifted Strong Community Organization" LISCO Arusha` | 24. LISCO | liftedstrong.org answered HTTP 403; liftedstrongco.org is a non-existent domain. Facebook page; co-founders by first name from the summary. partial |
| Q25/42 | `"Exploration Kids Organization" Arusha` | 26. EKO | No match (other children's organisations, Workaway listings). not_found |
| Q26/42 | `"Children Talents Identification and Development Organization" Arusha` | 27. Children Talents Identification and Development Organization | No match. not_found, possibly inactive |
| Q27/42 | `"TCYLO" OR "Today's Children and Youth Life Organization" Arusha` | 28. TCYLO | No match (TCYRO of Kigoma and CYVC of Arusha are different). not_found |
| Q28/42 | `"Women and Child Vision" WOCHIVI Arusha` | 29. WOCHIVI | Tanzania Child Rights Forum member list: a mobile and 'Arusha'. The same number is listed for EKAMA Foundation (Dar es Salaam) (check). partial |
| Q29/42 | `"Health Initiative for Kids and Elders" Arusha` | 30. HIKE | No match (Mama Kwanza initiative, Arusha Kids Trust, Saveelders). not_found |
| Q30/42 | `"Mama Zetu Foundation" Arusha` | 31. MAMA ZETU FOUNDATION | Only a Resolution Project venture page for a 'Mama Zetu' dairy farm in Tanzania. It fits the register's project but gives no place or contact. not_found, uncertain |
| Q31/42 | `"Hope Bearers" Arusha Tanzania` | 32. Hope Bearers | No match (other 'hope' organisations). not_found |
| Q32/42 | `"Youth Power in Social Action" Tanzania` | 33. YOUTH POWER IN SOCIAL ACTION | No match (national youth news). not_found |
| Q33/42 | `"Green Path Foundation" Arusha` | 34. Green Path Foundation | Namesakes only (India, Guyana). It was registered on 7 September 2026. not_found |
| Q34/42 | `"Shujaa wa Upendo" Tanzania` | 35. SUI Tanzania | No match (Swahili Wikipedia and news). not_found |
| Q35/42 | `"LEHCSO" OR "Lead for Human Care and Share" Arusha` | 36. LEHCSO | No match (LEAD Foundation and others are different). not_found, possibly inactive |
| Q36/42 | `"New Stars Foundation" Arusha` | 37. NEW STARS FOUNDATION | Own site: director's named inbox, mobile, Mjimwema (Usa River), PO Box 360, socials; Director and Founder 'Elizabeth'. found |
| Q37/42 | `"Wamoja Foundation" Tanzania` | 38. WAMOJA FOUNDATION | No match (Wamoja ICT, a company; a charity song not linked to it). not_found |
| Q38/42 | `"Ely Education Vision Organization" Arusha` | 39. ELY EDUCATION VISION ORGANIZATION | Own Google Site ely-school.org (Reg. No. 00NGO/R/7530): two directors, the head teacher, a project coordinator and the project initiator. It shows no email or phone; ely-school.com is a non-existent domain. partial |
| Q39/42 | `"Huduma ya Kijamii Tanzania" Arusha` | 40. HKT | No match (the generic phrase returned government social-service pages). not_found |
| Q40/42 | `"Jamii Imarika Foundation" Arusha` | 41. JAMII IMARIKA FOUNDATION | Active: it sells a community food tour in Sinoni (Tripspoint listing read; GetYourGuide HTTP 403). No route. not_found |
| Q41/42 | `"Lomayana" Arusha school` | 42. Lomayana-Saint | No match. The word appears only as a pupil's name in another school's story; nothing from it was recorded. not_found |
| Q42/42 | `"Kutamani Foundation" Tanzania` | 43. The Kutamani Foundation | Australian charity (ACNC-registered) with a teachers' programme in Arusha. Its Wix site has expired, the ACNC register timed out, and AIIW and GoVolunteer answered HTTP 403. Facebook and LinkedIn only. partial. Allowance spent. |

No search was spent on **25. Ndoto in Action (NIA)**. Its site came from the funder page already in the welfare run's evidence: found.

## Fetches without a search

Each URL came from the slice's prior evidence, a result of that organisation's search, or a link on a page already fetched.

| Organisation | URL | Outcome |
|---|---|---|
| 1. Salama | https://www.salaamafoundation.org/, https://salaamafoundation.org/ | Local resolver SERVFAIL (WebFetch: EAI_AGAIN); 1.1.1.1 resolves 2.57.91.92; the TLS handshake fails with a fatal alert. robots.txt unreadable for the same reason. Not read. |
| 1. Salama | https://dailynews.co.tz/activists-call-on-community-in-arusha-to-speak-out-against-child-abuse/ | HTTP 500 |
| 1. Salama | https://www.genderlinks.org.za/change/stories-of-change/story-of-change-salama-foundations-transformative-campaign-in-tanzania | A national GBV/SRHR campaign body; no location or contacts; not used |
| 2. Hope and Soul | https://register-of-charities.charitycommission.gov.uk/en/charity-search/-/charity-details/5090863/full-print | Register contacts, trustees, objects |
| 2. Hope and Soul | https://hopeandsoul.org.uk/about-us/, /contact-us/ | I-NGO/R/2104, inbox (Cloudflare-protected, decoded), socials |
| 5. Dyslexia Tanzania | https://www.dyslexiatanzania.org/ and its bundle /static/js/main.cc9a8427.js | Home is a script shell; the bundle holds the inbox, mobile, socials, founder and address |
| 6. Gem Legacy | https://gemlegacy.org/ (home, /contact/, /our-leadership/, /our-story/, /faq/) | Inbox, socials, leadership, 501(c)(3), Arusha base |
| 8. MWACI | https://mwaci.org/ (home, /about-us/, /contact-us/) | Inboxes, mobile, office, team |
| 9. Nuru Yetu | https://www.nuruyetufoundation.org/ | Inboxes, mobile, socials, team, Dar es Salaam location |
| 11. BRF | https://benjaminrungafoundation.org/ (home; /about.html redirects to /about/) | Routes, registration, team |
| 12. FUMFO | https://furahiafoundation.org/ | HTTP 403; stopped at the host's first 403 |
| 13. CHAYETEO | https://satinofootballacademy.com/involved, /about | Programme inbox, address, founder |
| 16. Life Bridge | https://lifebfoundation.org/ | Islamabad namesake; not used |
| 18. Safaris with a Heart | https://safariswithaheart.com/ (home, /about/, /contact/, /charity-projects/) | Managers' routes, socials, charity model |
| 20. Good Hope Kiwawa | https://goodhopekiwawa.org/ | Non-existent domain (local resolver and 1.1.1.1) |
| 23. AFOTA | https://afotatz.org/ (home, contact.php, leadership.php) | Routes, address, leaders. The plain text reader showed only menus, so the text was read from the saved HTML. |
| 24. LISCO | https://www.liftedstrong.org/ | HTTP 403; stopped |
| 24. LISCO | https://www.liftedstrongco.org/ | Non-existent domain (local resolver and 1.1.1.1) |
| 25. NIA | https://www.vibrantvillage.org/where-we-fund | Funder page; links to http://www.ndotoinaction.or.tz |
| 25. NIA | https://ndotoinaction.or.tz/ (home, /contacts/, /meet-the-team/) | Routes, PO Box, Njiro office, socials, team |
| 29. WOCHIVI | https://www.tcrfnet.org/members | Member entry with a phone that the entry above also carries |
| 31. Mama Zetu | https://resolutionproject.org/ventures/mama-zetu/ | Venture profile; no links or contacts |
| 37. New Stars | https://newstarsfoundation.org/ (home, /about-us/) | Routes, address, founder |
| 39. ELY | https://www.ely-school.org/ (home, /contact, /team, /about-us/management-team-leadership-structure, /about-us/our-history) | Identity and team; no routes (the contact block is empty and the leadership chart is an image) |
| 39. ELY | http://www.ely-school.com/ | Non-existent domain (local resolver and 1.1.1.1) |
| 41. Jamii Imarika | https://www.tripspoint.com/tanzania/arusha/tour/city-tours/community-and-local-food-testing-tour/9578 | Tour listing by the foundation; no contacts |
| 41. Jamii Imarika | https://www.getyourguide.com/jamii-imarika-foundation-s667736/ | HTTP 403 |
| 43. Kutamani | https://www.acnc.gov.au/charity/charities/51300971-09dd-ea11-a815-000d3ad1f9f4/profile | Timed out twice with read_page, then with curl on robots.txt and the page |
| 43. Kutamani | https://www.aiiw.org.au/registered-projects/teacher-outreach-arusha-project/ | HTTP 403 |
| 43. Kutamani | https://govolunteer.com.au/volunteering-organisations/23309 | HTTP 403 |
| 43. Kutamani | https://www.mycause.com.au/charity/43523/TheKutamaniFoundation | Description; links to thekutamanifoundation.org |
| 43. Kutamani | https://www.thekutamanifoundation.org/ | The local resolver timed out; 1.1.1.1 resolves it. HTTPS refused the connection; HTTP answered 302 to expiredwixdomain.com, which was not followed. |

## Blocked or unreadable sites

- **HTTP 403** (not retried; no further page requested from the host):
  - furahiafoundation.org (FUMFO's own site)
  - www.liftedstrong.org (LISCO's own site)
  - www.getyourguide.com (supplier page)
  - www.aiiw.org.au
  - govolunteer.com.au
- **TLS failure:** salaamafoundation.org gives a fatal alert in the handshake. Not worked around; plain HTTP was not tried.
- **Timeout:** www.acnc.gov.au (the Australian charity register) did not answer, not even for robots.txt.
- **Server error:** dailynews.co.tz answered HTTP 500 on one article.
- **Gone:**
  - goodhopekiwawa.org, liftedstrongco.org and ely-school.com are non-existent domains on the local resolver and 1.1.1.1
  - thekutamanifoundation.org is an expired Wix domain
- **Script-built:** dyslexiatanzania.org. It was read from its own public JS bundle; a browser pass could confirm those details and read the team cards.
- **Social pages** (Facebook, Instagram, LinkedIn, TikTok, YouTube, X): recorded from the organisation's own site or a search result; not read.
- **Not opened by choice:**
  - Dyslexia Tanzania's team CMS API, which needs an embedded key
  - Workaway and GoGetFunding pages
  - data-broker listings (ZoomInfo)
  - pages about individual children

## Organisations not reached

The allowance (42) was spent before the last two organisations in slice order. Both lie 6.7 km from Usa River. For neither is any source held beyond the register, which publishes no contacts, so no line was written for them. They stay candidates for the next wave.

- **44. VICTORY OF WOMEN AND CHILDREN FOUNDATION** (ORG_963532783309db7f, 00NGO/R/5350, Arumeru, 2023). The register describes a maternal-health programme (safe birth, maternal and child mortality). It looks like a maternal-health NGO rather than a child-welfare one.
- **45. WINGS OF CHANGE (WOC)** (ORG_86c19bd6f8efd507, 00NGO/R/5730, Arumeru, 2023). The register describes support for children, girls and women: child-focused in part. The name is common, so a query should add Usa River or Arumeru.

The Tanzania Child Rights Forum member list (already read) was checked for both, and for the other late entries, without a match.

## What each organisation is (for the welfare run's classification)

- **Child-focused (21):**
  - Hope and Soul (family programme)
  - Uplifting and Nurturing Them (education support)
  - ACHA WACHEZE (children's sport and talent)
  - DYSLEXIA TANZANIA (specialised: children with dyslexia)
  - NURU YETU (girls' leadership in schools; based in Dar es Salaam)
  - FUMFO (charity daycare and pre-school)
  - CHAYETEO (pre-school programme, arts, free football academy)
  - Bandari ya Maendeleo (school sponsorship)
  - Good Hope Kiwawa (children's home becoming a learning centre)
  - Ndoto in Action (education in rural schools)
  - EKO (education access)
  - Children Talents (talent development)
  - Youth Power in Social Action (street children)
  - Green Path Foundation (children's rights, parenting, nutrition)
  - SUI Tanzania (children's education)
  - LEHCSO (education for vulnerable children)
  - New Stars (children's centre with its own teachers)
  - Wamoja (pastoralist children's education and health)
  - ELY (school)
  - Lomayana-Saint (education)
  - The Kutamani Foundation (teacher training for grassroots schools)
- **Child-focused in part (12):**
  - Gem Legacy (education funder for mining communities)
  - Help for the Maasai
  - MWACI
  - Benjamin Runga Foundation (youth ICT)
  - Empact
  - Every Child Count (girls; anti-FGM)
  - Life Bridge (family livelihood)
  - Safaris with a Heart (charity arm of a safari company)
  - Starving children (mother and child care)
  - AFOTA (Islamic humanitarian NGO; orphan centre being built)
  - WOCHIVI
  - HIKE
- **Doubtful fit, not clearly child-focused (10):**
  - Salama
  - OKIA
  - Light for Many
  - Kalulu (youth)
  - LISCO (women)
  - TCYLO (youth livelihoods)
  - Mama Zetu (women's dairy farm)
  - Hope Bearers
  - HKT
  - Jamii Imarika

## Problems and warnings

- **Stopping rule not fully met.** One search per organisation, nearest first. The allowance was spent at organisation 43 of 45, so two organisations are unresearched (see above). No search was refused by the session cap.
- **Flags raised in notes** (checked against `contact_lib.note_flags`):
  - **location to check:** NURU YETU. Its own site gives Dar es Salaam, outside the Arusha-Kilimanjaro area.
  - **segment to check:** SAFARIS WITH A HEART. The routes are the safari company's office managers; the NGO looks like its charity arm.
  - **website gone:**
    - GOOD HOPE KIWAWA: no longer resolves
    - The Kutamani Foundation: its domain has expired
  - **check before outreach:**
    - GOOD HOPE KIWAWA: confirm the children's home still operates
    - WOCHIVI: its only phone is also listed for another organisation
  - **possible closure** (registered before 2020, no register project, no web trace): Children Talents Identification and Development Organization (2015) and LEHCSO (2018). Neither has a route, so no draft is affected.
  - **fit to check:**
    - the 10 doubtful-fit entries above
    - FUMFO and ELY, which run a pre-school or school (possible peer schools)
- **Check before outreach (no flag):**
  - Hope and Soul: every route is UK-based (UK mobile, a Gmail inbox, the site inbox), and only the UK trustees are named.
  - CHAYETEO: the route is its football academy's Gmail inbox. The academy is also registered under the National Sports Council Act.
  - Dyslexia Tanzania: routes and founder come from the site's code, not from a rendered page.
  - AFOTA's leadership enquiries go to a Gmail inbox named after it.
- **Identity uncertain:**
  - Salama Foundation Tanzania: the only candidate site is unreadable (TLS failure), and nothing ties it to the register entry.
  - MAMA ZETU FOUNDATION: a dairy-farm venture with no place given.
- **Not the same organisation:** AFOTA is not Asante Africa. TCYRO, CYVC, EMpact One, Imarika Foundation (Kenya), Wamoja ICT and LEAD Foundation are all different from the slice entries.
- **Data quirk:** EKO's slice locality reads 'Level:' because the register gives no district. It is a parsing gap, not a place.
- **Safeguarding:** no concerns found.
  - Not recorded:
    - a child's name that appeared in a search result (Q41)
    - staff biographies and family details (New Stars, Benjamin Runga Foundation)
    - children's details on Gem Legacy's and CHAYETEO's pages
  - Nothing about children, parents or residents was recorded.
