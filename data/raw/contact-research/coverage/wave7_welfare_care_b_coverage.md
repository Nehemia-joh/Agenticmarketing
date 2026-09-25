# Coverage log: wave 7, welfare care B (26 September 2026)

- **Slice:** `runtime/contacts/slices/wave7_welfare_care_b.json`, nearest first. It holds 33 NGOs from the national NGO register whose type is not yet known (segment "Welfare (unclassified child-focused NGO)"), 21.0 to 26.8 km from a campus. Every one needed a published route, and every `known_sources` list was empty.
- **Output:** `data/raw/contact-research/search_wave7_welfare_care_b_2026-09-23.jsonl`, one line per organisation in slice order, appended as the work went. The date key is the programme's shared key; the access date is 26 September 2026.
- **Searches:**
  - Allowance: 37 WebSearch calls. All 37 were used (Q1/37 to Q37/37), and the session cap refused none. After Q37 no page was fetched.
  - No search was routed through WebFetch, a browser or a results page. Each query named one organisation.
  - Five organisations got a second query. The allowance left 4 searches beyond one per organisation, and ADRA needed none:
    - ATPWE (Q12 acronym, Q13 full name)
    - AYOFERC (Q24 acronym, Q25 full name)
    - WCAid (Q30 name, Q31 acronym)
    - Dove Foundation (Q36)
    - Kili-Hope (Q37)
- **Fetching:**
  - Pages were read with `scripts/contacts/read_page.py`: shared cache, 1.5 s spacing per site, robots.txt honoured.
  - A small link reader, a Cloudflare-email reader and a record emitter in `runtime/contacts/agents/wave7_welfare_care_b/` use the same cached fetcher. Cloudflare-protected addresses were decoded with `contact_lib.decode_cfemail`, as the crawler does.
  - robots.txt was read for every host. A 4xx robots.txt counted as no rules. One site disallows all crawling (The Same Qualities Foundation, below) and was not read.
  - ADRA's three pages came from the shared HTTP cache (captured 23 September 2026 by the crawl).
  - The NGO register profiles are cited from the welfare run's collection (22 September 2026) and were not fetched again.
  - Every other page was fetched on 26 September 2026.
  - Two domains failed to resolve. `nslookup` checked them against the local resolver and 1.1.1.1, which changed only the name lookup; no block was passed:
    - edvotz.org: Cloudflare nameservers and mail records, but no web address; www does not exist
    - seedsofkindness.or.tz: non-existent domain
- **Script-built site:** NAFGEM's site (nafgemtanzania.or.tz) is a React shell. It was read through what the browser loads: its public script bundle, and the public JSON endpoints its pages call (`/api/public/site-pages`, `/api/public/staff`). Its robots.txt allows everything; no login or key is needed. The live staff list replaces an older default list in the bundle, so the live names were used.
- **Organisations written:** 33 of 33.
  - Status: found 8, partial 6, not_found 19, blocked 0.
  - Identity: confirmed 30. Uncertain 3: KABILA MOJA IMPACT, DOVE FOUNDATION and HOPE FOR CHILDREN ORGANIZATION.
  - Not reached: none.
- **Results:**
  - **Named leads:** 37 across 8 organisations, all from the organisations' own sites (including NAFGEM's public site data) and all fetched. PDPA risk: all medium.
    - 25 carry a role that `contact_lib.DECISION` counts as a decision role:
      - 11 founders and co-founders
      - 4 executive, country or programme directors
      - 5 managers
      - FAE's board chair and its 3 other members of the Board of Directors
      - NAFGEM's office administrator
    - The other 12 are board members, a secretary and a treasurer (Zion Gates), an HR officer, social welfare staff and a team leader.
    - Six leads are named by first name only and will be labelled incomplete. All are Ndoto Zetu's: Simone (founder), Magreth (project manager) and board members Emmanuel, Flo, George and Edna.
  - **Direct routes:** 12 emails and 15 phones for 11 organisations.
    - Read on fetched pages: 11 emails and 14 phones.
    - Snippet-only (EDVO, whose site no longer resolves): 1 email and 1 phone.
    - Personal-domain (Gmail) inboxes: 3. HalevAfrica's and Zion Gates' are named after the organisation. Seeds of Kindness gives one named after a person on its Idealist directory profile.
    - Dove Foundation's routes are on an uncertain record, so the profile builder will not use them.
  - **Indirect routes:** 10 websites, 7 postal and 4 physical addresses, and 21 official social links for 10 organisations.
  - **Type of organisation** (for the welfare run's classification; details in each record's notes):
    - Child-focused, 14:
      - education support: Marangu Anza Pamoja, HalevAfrica, FAE (disability-inclusive education)
      - family programmes: Kipepeo, Ndoto Zetu (with a day centre)
      - a children's day centre: Kili-Hope
      - children's health: The Same Qualities Foundation (cleft care)
      - register-only entries: Usa River Children Centre, Passionate Kids Connect, Empathy Foundation, Students Support Foundation, Vision of East African Child, Hope for Children, Bridge foundation
    - Partly child-focused, 18: ADRA, Restore Hope for Youth, Green Future, Neemah Wings, Lipo Tumaini, Relight Wings, EDVO, Kilimanjaro Smiley, ATPWE, Kabila Moja Impact, NAFGEM, Zion Gates, AYOFERC, Dove Foundation, Likalilo, SAWATA, WCAid, Seeds of Kindness. They are women's, community, relief, volunteer-placement or advocacy bodies with children among their groups.
    - Not specifically child-focused, 1: Jamii Innovation (gender equality).
    - None was found to be a residential children's home. Relight Wings runs a small safe house for teenage mothers and their babies.
- **Prior evidence read before any search:**
  - the slice
  - the NGO register profiles in `data/raw/welfare-research/nis_catchment_profiles_2026-09-22.jsonl`. All 33 organisations matched a profile by name; the profiles give registration numbers, aims and projects but no contacts.
  - `data/raw/welfare-research/research_*.jsonl`: nothing relevant. Only unrelated mentions (ADRA as a neighbour of a closed baby home; Seeway, a different Usa River home).
  - earlier contact-research records: only the company master's wave-2 record for ADRA Tanzania ('Adventist Development Agency', Odaf2beeadcd4) is relevant; its website was reused without a search. The Kipepeo tour company and the other 'Ndoto' and 'Bridge' entries are different bodies.
- **Register pins:** many register pins are shared by several entries in one district, so distances in the slice are rough. Where an organisation's own site or its registered district shows a different place, the note says so:
  - Ndoto Zetu is in Mianzini, Arusha city.
  - Usa River Children Centre's pin is about 30 km from Usa River.
  - Lipo Tumaini, SAWATA and Jamii Innovation are registered in Simanjiro (Manyara Region).
- **Recording rules applied:**
  - People come only from the organisation's own site, including text its pages render from their own public data.
  - Not recorded as leads:
    - names on supporter fundraisers (Relight Wings' and Kili-Hope's GoFundMe pages)
    - personal-profile LinkedIn URLs
    - ZoomInfo and other data brokers
    - staff outside outreach: caretakers, a cook, finance, procurement and M&E staff, local partners, and team members shown only with a template role
    - a partner who leads another company
  - Also not recorded:
    - biographies and personal histories
    - home-looking street addresses (HalevAfrica's Israeli address; the Fürth address of MAPO's German association)
    - bank details
    - a Rotary Facebook link on MAPO's site
  - Nothing about children, parents or residents was recorded. Where a page told individual children's stories (HalevAfrica's 'Why we exist'), nothing from it was used.
  - Every note is 600 characters or fewer, with its warnings early. Warning phrases were checked against `contact_lib.note_flags`. The flags raised:
    - possible duplicate: ADRA
    - location to check: Lipo Tumaini, Usa River Children Centre, Ndoto Zetu, SAWATA, Jamii Innovation
    - fit to check: Jamii Innovation
    - website gone: EDVO, Seeds of Kindness
    - check before outreach: Seeds of Kindness (its only inbox is a person's Gmail)

## Status definitions

- `found`: identity confirmed, and at least one email or phone read on a page published by the organisation (or its own programme), its parent body or an official register.
- `partial`: only indirect routes (website, official social page, postal address), a route seen only in a snippet or given on a directory, or routes on a record whose identity is uncertain.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading. None this wave; blocked sites with other evidence are marked by their other evidence.

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| (none) | (no search) | 1. ADVENTIST DEVELOPMENT AND RELIEF AGENCY | Own site adratanzania.org, already cited by the master's wave-2 record. It gave an inbox (Cloudflare, decoded), an office phone and a mobile, PO Box 360 Usa River, socials and the Ag. Country Director. Same organisation as the master's 'Adventist Development Agency'. found |
| Q1/37 | `"Restore Hope for Youth" Arusha` | 2. RESTORE HOPE FOR YOUTH | No match: namesakes in Uganda and Kenya, plus Good Hope Orphanage, ACE, YWAM and Youth Agile Solutions. not_found |
| Q2/37 | `"Anza Pamoja" Marangu` | 3. Marangu Anza Pamoja Organization | Own site anza-pamoja.com. The imprint gives an inbox, the Pasua Street seat, PO Box 1995 Moshi and the NGO's authorised board; the about page names founder Daudi. LinkedIn company page. found |
| Q3/37 | `"Kipepeo Family Foundation" Moshi` | 4. kipepeo family foudation | Own site kipepeo-kiwavi.com: inbox (Cloudflare, decoded), a Tanzanian mobile and a Swiss WhatsApp number, Facebook and Instagram. Two founders, a team leader and a social worker. found |
| Q4/37 | `"Green Future and Community Development" Monduli` | 5. Green Future and Community Development Tanzania Organization. | No match: Monduli Green (a UK school charity), Monduli CDTI and carbon projects. not_found |
| Q5/37 | `"Neemah Wings Foundation" Tanzania` | 6. NEEMAH WINGS FOUNDATION | No match: Neema Village, Neema International, Neema Women and Youth Wings. not_found |
| Q6/37 | `"Lipo Tumaini" Tanzania` | 7. LIPO TUMAINI ORGANIZATION (LTO) | No match: a gospel song and other 'Tumaini' bodies. Registered in Simanjiro (Manyara), with a pin near Moshi. not_found |
| Q7/37 | `"Usa River Children Centre" Tanzania` | 8. USA-RIVER CHILDREN CENTRE | No match: URRC, Tumaini and Save Africa. A Daily News story was read; it concerns Ngarasero Community Organization and was not used. not_found |
| Q8/37 | `"Passionate Kids Connect" Moshi` | 9. PASSIONATE KIDS CONNECT | No match: the Moshi Kids app and Moshi Kids Centre. not_found |
| Q9/37 | `"Relight Wings Foundation" Moshi` | 10. RELIGHT WINGS FOUNDATION | Instagram @relight_wings_foundation (snippet). A volunteer's GoFundMe was read: a safe house for teenage mothers. Its founder's first name and personal story were not recorded. partial |
| Q10/37 | `"Elective Development Volunteers" Moshi` | 11. ELECTIVE DEVELOPMENT VOLUNTEERS ORGANIZATION | Own site edvotz.org appeared in the results; the snippet gives an inbox, a mobile and PO Box 8918 Moshi. The site no longer resolves. partial |
| Q11/37 | `"Kilimanjaro Smiley Foundation"` | 12. KILIMANJARO SMILEY FOUNDATION | No match: Kilimanjaro Foundation, Kilimanjaro Initiative and charity climbs. not_found |
| Q12/37 | `"ATPWE" Moshi women FGM` | 13. ATPWE | No match: research papers and an FGM country-profile PDF, which is over the fetcher's 2 MB cap and was not read. |
| Q13/37 | `"Alliance on Traditional Practices and Women Empowerment"` | 13. ATPWE | No match: GAMCOTRAP, UN Women and WCEI. not_found |
| Q14/37 | `"Empathy Foundation Tanzania"` | 14. EMPATHY FOUNDATION TANZANIA | No match: Help Tanzania Foundation, an Indian Empathy Foundation, and a YouTube channel that gives no place. not_found |
| Q15/37 | `"Halevafrica" Moshi` | 15. HALEVAFRICA | Own site halevafrica.com: a Gmail inbox named after it, an Israeli mobile and socials. Founder & CEO, three co-founders, the local team manager and the marketing manager. found |
| Q16/37 | `"Kabila Moja Impact" Moshi` | 16. KABILA MOJA IMPACT | vzw Kabila Moja, a Belgian association (kabilamoja.org) working around Moshi. It never names 'Kabila Moja Impact' and offers only a contact form. not_found, uncertain |
| Q17/37 | `"NAFGEM" Moshi Tanzania` | 17. NAFGEM Tanzania | Own site nafgemtanzania.or.tz, read through its public site data: 2 inboxes, a landline, 2 mobiles, Shanty Town and PO Box 6413, and socials. Leads: executive director, director of programs, project manager, HR officer, office administrator and social welfare officer. found |
| Q18/37 | `"Foundation for African Empowerment" Arusha` | 18. FAE | Own site thefaeafrica.org: an inbox (Cloudflare, decoded), a mobile and WhatsApp number, and PO Box 116 Duluti. Founder & Executive Director, board chair and three board members. Facebook and LinkedIn (snippets). found |
| Q19/37 | `"Ndoto Zetu" Arusha children` | 19. NDOTO ZETU | Own site ndotozetu.or.tz: an inbox, an office mobile and the fundraising coordinator's mobile, Mianzini Juu, Facebook and Instagram. Six first-name leads. found |
| Q20/37 | `"Students Support Foundation" Moshi` | 20. STUDENTS SUPPORT FOUNDATION(SSF) | No match: the US Student Support Foundation, Good Hope Moshi and Born To Learn. not_found |
| Q21/37 | `"Vision of East African Child" Tanzania` | 21. Vision of East African Child | No match: World Vision, World Bank and EAC pages. not_found |
| Q22/37 | `"Zion Gates Foundation" Moshi` | 22. ZION GATES FOUNDATION | Own site ziongates.org: a Gmail inbox named after it, a mobile and PO Box 824 Moshi. Executive director, programs manager, secretary, treasurer and a board member. found |
| Q23/37 | `"Kili-Hope" Moshi children` | 23. KILI-HOPE ORGANISATION | A supporter's GoFundMe was read. It confirms that the Kili Hope Center in Pasua, Moshi became Kili Hope Organization. No route. |
| Q24/37 | `"AYOFERC" Arusha` | 24. AYOFERC | No match (general Arusha pages). |
| Q25/37 | `"Arusha Young Female Recovery Community"` | 24. AYOFERC | No match: Faraja Young Women Development Organization, New Life Outreach and a tribunal's girls' mentoring programme. not_found |
| Q26/37 | `"Dove Foundation" Arusha children women` | 25. DOVE FOUNDATION | The Dove Foundation (thedovefoundation.org), Mawe Lodges' staff foundation: an inbox, a mobile, Block E Plot 300 and Box 12270 Arusha. Also a 'Dove Foundation, Arusha' Facebook page. Nothing ties either to the register entry. partial, uncertain |
| Q27/37 | `"Likalilo Initiatives Foundation"` | 26. LIKALILO INITIATIVES FOUNDATION | No match (similar-sounding foundations elsewhere). not_found |
| Q28/37 | `"Saidia Wanajamii Tanzania" SAWATA` | 27. SAWATA | No match. Saidia Wazee Tanzania (Mara) shares the acronym and is a different body. not_found |
| Q29/37 | `"Jamii Innovation" Simanjiro` | 28. JAMII INNOVATION | No match: Jamii Technology, Jamii.one and Jamii Impact Hub. not_found |
| Q30/37 | `"We Care Aid" Moshi` | 29. WCAid | No match: Moshi-branded products, Rainbow Centre and Cornerstone. |
| Q31/37 | `"WCAid" Tanzania grannies children` | 29. WCAid | No match: Save the Children, UNICEF and SOS. not_found |
| Q32/37 | `"Hope for Children Organization" Arusha` | 30. HOPE FOR CHILDREN ORGANIZATION | A 'Hopeforchildrenarusha' Facebook page (snippet, not read). The other 'Hope' bodies in Arusha are different. partial, uncertain |
| Q33/37 | `"Same Qualities Foundation" Arusha cleft` | 31. THE SAME QUALITIES FOUNDATION (SQF) | Own site samequalitiesfoundation.org. Its robots.txt disallows all crawling on both hosts, so it was not read. Facebook page (snippet). partial |
| Q34/37 | `"Seeds of Kindness" Moshi children` | 32. SEEDS OF KINDNESS ORGANIZATION (SOK) | Own site seedsofkindness.or.tz is a non-existent domain. Its Idealist profile was read: a Gmail inbox named after a person and a French mobile. partial |
| Q35/37 | `"Bridge Foundation" Moshi Tanzania children` | 33. Bridge foundation | No match: KCF, Moshi Kids Centre, Good Hope and Born To Learn. Bridge Africa Foundation has a different name; its site answered HTTP 403. not_found |
| Q36/37 | `"Kili Dove Foundation" Arusha` | 25. DOVE FOUNDATION | The same two candidates came back. A Daily News golf-charity article was read; it does not concern Dove. Still uncertain. |
| Q37/37 | `"Kili Hope Organization" Moshi` | 23. KILI-HOPE ORGANISATION | No match: Child Hope Development Organization, Good Hope and Hope Village. not_found. Allowance spent. |

## Fetches

Each URL came from the slice's prior evidence, a result of that organisation's search, or a link on a page already fetched.

| Organisation | URL | Outcome |
|---|---|---|
| 1. ADRA | https://adratanzania.org/ (home, /contact-us/, /about-us/) | Shared cache (23 September). Routes, the Ag. Country Director and programmes. The LinkedIn link is a personal-profile URL and was not used. |
| 3. MAPO | https://www.anza-pamoja.com/ (home, /impressum, /uber-uns) | Imprint routes and board; the founder on the about page; Instagram |
| 4. Kipepeo | https://www.kipepeo-kiwavi.com/ (home, /english/contact/, /english/team/) | Routes, socials and team |
| 8. Usa River Children Centre | https://dailynews.co.tz/20-vulnerable-children-in-usa-river-seek-education-sponsorship/ | About Ngarasero Community Organization; not used |
| 10. Relight Wings | https://www.gofundme.com/f/relight-wings-foundation | A volunteer's fundraiser; type only |
| 11. EDVO | https://www.edvotz.org/, https://edvotz.org/ | Name lookup failed (no web address; www does not exist). robots.txt was unreadable for the same reason. Not read. |
| 13. ATPWE | https://www.fgmcri.org/media/uploads/Country%20Research%20and%20Resources/Tanzania/tanzania_country_profile_v3_(july_2020).pdf | Truncated at the fetcher's 2 MB cap; not read |
| 15. HalevAfrica | https://halevafrica.com/ (home, /contact-us/, /our-story/, /what-we-do/, /why-we-exist/) | Routes, socials and team. The children's stories on 'why we exist' were not used. |
| 16. Kabila Moja Impact | https://kabilamoja.org/ (redirects to www), /plastiki-safari-tanzania, /bouwkampen | A Belgian association; Wix; contact form only |
| 17. NAFGEM | https://www.nafgemtanzania.or.tz/ (and /index.php/get-involved/our-supporters, the same shell), /assets/index-Cal_LNBP.js, /api/public/site-pages, /api/public/staff | Routes, socials, staff and programmes |
| 18. FAE | https://www.thefaeafrica.org/ (home, /contact-us/, /our-leadership/) | Routes, leadership and type |
| 19. Ndoto Zetu | https://ndotozetu.or.tz/ (home, /contacts/, /about/, /programs/) | Routes, team, board and type |
| 22. Zion Gates | https://ziongates.org/ (home, /contact/, /about/) | Routes, team and type |
| 23. Kili-Hope | https://www.gofundme.com/f/thyagos-charity-2019 | A supporter's fundraiser; identity and type |
| 25. Dove Foundation | https://thedovefoundation.org/ (home, /contact/), https://mawelodges.com/dove-foundation/ | Routes; tie to Mawe Lodges |
| 25. Dove Foundation | https://dailynews.co.tz/diplomatic-golf-supports-education-of-74-vulnerable-children/ | Not about Dove; not used |
| 31. SQF | https://www.samequalitiesfoundation.org/robots.txt, https://samequalitiesfoundation.org/robots.txt | `User-agent: *` / `Disallow: /` on both hosts. No page was read. |
| 32. Seeds of Kindness | https://seedsofkindness.or.tz/ | Non-existent domain (local resolver and 1.1.1.1) |
| 32. Seeds of Kindness | https://www.idealist.org/en/nonprofit/7db840e496484f04b0888e28b0a57441-seeds-of-kindness-moshi | Directory profile: inbox, phone and programmes |
| 33. Bridge foundation | https://bridgeafricafoundation.org/ | HTTP 403. Stopped at the first 403. A different name in any case. |

## Blocked, disallowed or unreadable sites

- **samequalitiesfoundation.org** (The Same Qualities Foundation): robots.txt disallows all crawling on both hosts, so it was not read. It is for the browser pass, where what it publishes would be tagged risky.
- **bridgeafricafoundation.org:** HTTP 403 (not worked around). It is not this slice's organisation.
- **edvotz.org** (EDVO): the site no longer resolves, though mail records remain.
- **seedsofkindness.or.tz** (Seeds of Kindness): non-existent domain.
- **fgmcri.org Tanzania country profile (PDF):** larger than the fetcher's 2 MB cap, so it was not read.
- Facebook and Instagram pages were recorded from search results or site links and not opened, as the rules require.

## Organisations not reached

None. All 33 were researched and written.

## For a person to check

- **ADRA:** the welfare record is ADRA Tanzania, already in the company master as 'Adventist Development Agency' (Odaf2beeadcd4), with the same site and routes.
- **DOVE FOUNDATION:** check whether register entry 00NGO/R/5891 (2023) is Mawe Lodges' staff foundation (thedovefoundation.org) or the body behind the 'kilidovefoundation' Facebook page. Routes are recorded but marked uncertain.
- **KABILA MOJA IMPACT:** check whether it is the Tanzanian arm of the Belgian vzw Kabila Moja.
- **HOPE FOR CHILDREN ORGANIZATION:** check whether the 'Hopeforchildrenarusha' Facebook page is its own.
- **SEEDS OF KINDNESS:** its only inbox is a Gmail address named after a person (on its Idealist profile), and its phone is French. Confirm the right contact before outreach.
- **EDVO:** check whether info@edvotz.org still delivers; the web address is gone, but the mail records remain.
- **Locations:**
  - Ndoto Zetu is in Mianzini, Arusha city, not at its Arumeru pin.
  - Usa River Children Centre's pin is about 30 km from Usa River.
  - Lipo Tumaini, SAWATA and Jamii Innovation are registered in Simanjiro (Manyara Region).
- **The Same Qualities Foundation:** its routes are on its robots-disallowed site. A browser pass could read up to five pages, tagged risky.
