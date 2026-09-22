# Slice G coverage log: funders, foreign charity registers and umbrella bodies

Run: `arusha-welfare-2026-09`. Research dates: 2026-09-22 to 2026-09-23. Output: `G_funders_registers.jsonl`, 191 lines. Every line parses as JSON (checked with Python).

## Record counts

| Record type | Count |
|---|---|
| organisation | 118 |
| relationship | 66 |
| contact | 7 (generic or role desks only; no named individuals) |

Organisations by segment:

| Segment | Count |
|---|---|
| Welfare funder (includes faith and umbrella bodies) | 68 |
| Welfare residential care | 27 |
| Welfare specialised centre | 13 |
| Welfare family-based programme | 10 |

Verification status across all records:

| Status | Count |
|---|---|
| verified | 93 |
| needs_review | 65 |
| historical | 31 |
| unverified | 2 |

Field notes:
- I added one extra key, `latest_expenditure`, inside `foreign_charity_registrations` because the task asks for expenditure. Some entries also carry an extra `note` key.
- For small US charities, addresses are city and state only. Street addresses were left out because they may be private homes.
- Officer and trustee names on IRS filings were not recorded. Children named in grant lists were not recorded either.

## Tools and constraints

- **WebSearch:** the session's search budget was already used up (200 of 200) at my first call. All work used WebFetch on register pages and on websites I already knew or found through register links. I did not use browser tools, did not sign in, and did not submit any forms.
- **ProPublica full-text search:** returned HTTP 429 (too many requests) on about 40% of calls. I spaced the calls out and retried.

## Registers tried

| Register | Result |
|---|---|
| US ProPublica Nonprofit Explorer, name API (`api/v2/search.json`) | Works, but the name matching is fuzzy and unhelpful. A query for "peace house africa" returned 404. |
| ProPublica full-text filing search | Main source. The queries are listed below. |
| ProPublica organisation pages | Used for EIN, income and expenditure for about 45 organisations. Full filing pages, schedules, XML and PDF load by JavaScript or return 403, so only the search snippets could be used for grant detail. |
| UK Charity Commission register | HTTP 403 on both the search page and the detail page. **Blocked.** |
| findthatcharity.uk | "Socket hang up" three times. |
| Scottish OSCR | The search page is a JavaScript form; no results were rendered. |
| Charity Commission for Northern Ireland | No results were rendered. |
| Australian ACNC | Timed out twice. |
| Canada CRA charity list | Stuck on a "Loading" page. |
| Dutch CBF | No results were rendered. |
| Dutch ANBI | Not machine-readable. |
| German, Norwegian and Danish registers | Not attempted. There is no usable public search, and web search was unavailable. |
| UK Companies House, search "arusha" | 28 results, all businesses; nothing relevant. |
| Tanzanian NGO register (nis.jamii.go.tz/mapping) | The page loads and shows 8,376 NGOs. Arusha region has 1,319 (Arusha district 791, Arumeru 284). The region and district filter pages (`filter_ngo?region_id=1`, `filter_ngo?district_id=N&region_id=1`) show counts only; organisation names need JavaScript. **I could not read any names.** |
| Three funder registrations taken from Amani's own website | Friends of Amani UK 1107618, Vrienden van Amani RSIN 856833691, Africa Amini Alama ZVR 517623687. Their UK, Dutch and Austrian financials were not retrieved. |

## ProPublica full-text queries

These were run in roughly this order. "New" means the query found a new funder or supported institution.

1. arusha orphanage, pages 1–2: new (Karama, Care For Children Of The Earth, Falcos, Hidden Hearts/Osiligi, Educating Tanzania, Yelloh/Holley).
2. moshi orphanage, pages 1–2: new (Orphans International America, Upendo, Grace Orphanage, Kilimanjaro Childrens Fund, Foundation For Hope In Africa, Sal-vay-shen Green, Hidden With Christ Ministries, Asante Sana, New Day Foundation).
3. "children's home" arusha: new (My Daily Armor, One Heart Source).
4. "usa river" tanzania, pages 1–4: new (Utopia/St Mark's, Faraja, Arthur B Schultz, Foundation For Tomorrow, Afrikids).
5. "children's home" moshi, pages 1–2: new (Go Campaign/Gabriella, Concordia/VOV, Koch/St Joseph's).
6. arumeru: nothing relevant.
7. "street children" moshi: new (Koch grants to Sisters of Our Lady of Kilimanjaro).
8. "street children" arusha: new (Kidcare, Global Development Group USA).
9. "kilimanjaro orphanage": new (Children Of Kilimanjaro Orphanage Inc; Kilimanjaro Orphanage Centre found to be defunct).
10. "sanya juu": new (Faraja Diaconic Centre).
11. tengeru, machame and ngaramtoni, each in quotes: nothing relevant.
12. "peace house" arusha: new (US support entity with EIN 41-2018622, last filing 2010).
13. "light in africa": new (Asante Sana; Tanzanian NGO registration #12049).
14. "boma ngombe": new (TrueToTanzania, which makes grants to individuals).
15. "hai district": 0 results.
16. "siha": new (Uboratz).
17. "nkoaranga": new (The Small Things, Lift-the-lid).
18. kikatiti, kisongo, "njiro" orphan, "baby home" arusha, "cradle of love": nothing relevant.
19. "vulnerable children" moshi: new (Godparents For Tanzania, Hope Without Borders, OMAWA).
20. "vulnerable children" arusha, pages 1–2: new (Choose Love, HopeCare via Vibrant Village). Page 3 was rate-limited.
21. "mark's children's home", "tupendane", "Children Of Kilimanjaro Orphanage": added details to known leads.
22. "orphanage in moshi": nothing new.
23. "orphanage in arusha": new (Love Our Tanzania Family/Tumaini For Africa, Scott Willis/Mama Jane's, Wevol, Al-barro).
24. "orphans in arusha": 0 results.
25. "school fees" arusha: new (Cscna/Emusoi, Education Equals Power, Victoria's Giving Foundation).
26. "school fees" moshi: new (Habari Foundation, Asali, Tanzania Women Research Foundation).
27. "children's home in arusha": nothing new.
28. "disabilities" moshi: new (Kilimahewa, historical).
29. "safe house" arusha: new (Eripoto).
30. "rescue center" arusha: nothing new in the catchment (Karatu only).
31. "sponsored children" arusha: nothing new.
32. sponsorship moshi, pages 1–2: added EdPowerment details.
33. "VOV" moshi: nothing new.
34. "street children" kilimanjaro: new but out of area (Rombo).
35. "children's centre" arusha: 0 results.
36. "eripoto": new (Klehn, Grand Circle).
37. "hopecare": new (Friends of Tanzania).
38. "marafiki wa tanzania" orphans: nothing new.
39. "friends of tanzania" moshi: 0 results.
40. "sexually abused" arusha, then "sandra jones centre": new (Sandra Jones Centre).
41. "children's village" arusha: nothing new.

**Stopping rule not met.** The coordinator told me to stop, and at that point the last queries had been unproductive for only about 2 in a row. The rule needs 12 in a row.

## Websites fetched

**Worked:**
- africadreamsafaris.com: home, community, charitable-visits and Peace House pages
- kilivikings.com: home, about-us and company-profile pages
- amanikids.org: home and partners pages
- neemavillage.org: home and about pages
- sos-childrensvillages.org: Tanzania and Arusha pages
- africaaminialama.com
- thefoundationfortomorrow.org: home, contact-us and investing-in-students pages
- karamaconnection.org: home and why-karama pages
- foundationforhopeinafrica.org
- loveourtanzaniafamily.org
- theplasterhouse.org (plain http)
- edpowerment.org
- uboratz.org
- bootstrapafrica.org, which redirects to opportunitybuildsafrica.org (home and what-we-do pages)
- motheringacrosscontinents.org
- angonet.or.tz: home and contact pages

**Failed or dead:**
- peacehouseafrica.org, godparentsfortanzania.org, hiddenheartsfoundation.org, cradleoflovebabyhome.org, lightinafrica.co.uk, farajafund.org, kilimanjarochildrensfund.org and plasterhouse.org do not resolve.
- lightinafrica.org returns 404.
- salvayshengreen.org redirects to acv3.org, which does not resolve.
- mkombozi.org gives a TLS error or a blank page.
- elct.org fails the TLS handshake.
- sibusiso.nl returns 403.
- habarifoundation.org shows a bot check.
- utopiafoundation.org and kidcareinternational.org refused the connection.
- thesmallthings.org, gocampaign.org and oneheartsource.org rendered no usable content.

## Corporate funders (task item 3)

- **Africa Dream Safaris:** confirmed. It supports Peace House Orphanage with donations and complimentary guest visits. That page describes Peace House as a boarding school for 240+ AIDS orphans. The guest visits are recorded as a red flag. St Jude's, POLI and FAME are recorded only as context.
- **KILI VIKINGS LIMITED:** confirmed. The about-us page mentions a share of profits going to orphanages supporting 200+ children. The company-profile page names **Light in Africa** (Moshi, 200+ orphans) as a home it funds.

## Unfinished leads and gaps

1. **UK, Scottish, Australian and Dutch registers** could not be read, so non-US funders are under-represented. Only the Amani funders and Africa Amini Alama are recorded. Next steps:
   - Re-run with a browser, or with register data extracts.
   - Candidate UK funders to check: Cradle of Love, Mkombozi, Sibusiso (Dutch), the Plaster House supporters and Molly's Network. Molly's Network is a UK charity named in a 2014 Help Better Lives filing.
2. **Tanzanian NGO register:** could not read names, as described above.
3. **Beneficiaries not identified:**
   - Children Of Kilimanjaro Orphanage Inc: the supported orphanage is unknown.
   - Hearts And Hands For Humanity: grant list for its Moshi orphanages is unknown.
   - Kidcare's street-children centre: name unknown.
   - Wevol and Al-barro: the Arusha orphanages they support are not named.
   - Grand Circle Foundation: the children's home it repaired (PO Box 15270, Arusha) is not named.
   - Mothering Across Continents: acts as fiscal agent for an unnamed centre "on the outskirts of Arusha" (2021–22). Not recorded.
4. **Locations to confirm:**
   - Sandra Jones Centre: Tanzania or Arusha is not confirmed.
   - Eripoto Safe House: exact site unknown.
   - Kafika House: location unknown.
   - St Joseph's Children's Home: confirm it is in Moshi.
   - "Tonga Orphanage" (Care For Children Of The Earth): location unknown.
   - VOV Center, Moshi: what "VOV" stands for is unknown.
   - Victoria's Giving Foundation: purpose unclear.
   - St Mark's Children's Home, Usa River: operator and contacts not found.
5. **Records left as needs_review:**
   - The Nkoaranga Village Organization, Happy Families Children's Village and ELCT orphanage names come from filings. Whether they are one entity is inferred.
   - The two Treasures of Africa funders conflict. Hidden With Christ Ministries says the orphanage closed in 2021. Sal-vay-shen Green still describes it as an orphanage in 2024.
6. **Umbrella and faith bodies:** diocesan social-services pages could not be reached (ELCT Meru, Northern and North Central dioceses; Catholic Archdiocese of Arusha; Diocese of Moshi). I found no online national or regional network of children's homes. ANGONET is recorded, but its member list is not public.
7. **Leads found but not recorded:**
   - Cradle of Love: only a 2012 grant of $1,000, with no location given.
   - Adorer Missionary Sisters of the Poor: supports orphans in Rombo, which is outside the catchment.
   - Help Better Lives Inc: funds Tupendane Company, an income-generating enterprise rather than a welfare body.
   - Several funders of schools only, recorded as context in notes: Angaza, Heart To Care, Children's Global Education Fund, Ladybug Project, Be The Change Volunteers.
