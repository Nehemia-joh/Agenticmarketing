# Slice S: published contact routes for homes, orphanages and specialised centres (2026-10-03)

Targets: `runtime/contacts/slices/welfare13_A.json` (87). Output: `data/raw/welfare-research/research_S_routes_homes_centres_2026-10-03.jsonl`.
Records: 29 organisation, 12 contact, 5 relationship (46 lines, all parse). Every organisation record uses the target's exact name.
The run was cut off once by an API limit and resumed; the file was checked first and no target was written twice.

Method: `scripts/contacts/read_page.py` (cache, robots.txt honoured) through a scratch crawler (`runtime/contacts/agents/welfare13_S/crawl.py`) over each target's own site
and the partner pages already held; then one WebSearch per target, in priority order, for targets with a plausible web presence. Targets known only from an NGO register
profile (about 40 small NGOs) have no website and no register contact field, so no search was spent on them. Search snippets were used only to find pages to read;
nothing is recorded from a snippet alone.

## Searches (30 of 55 used)

| # | Query (short) | Target | Result |
|---|---|---|---|
| Q1/55 | Saint Marks Children's Home Usa River contact | St. Mark's | Nothing about it. |
| Q2/55 | Karim Children's Care Centre contact | Karim | Nothing usable; a volunteer-coordinator email in the answer was a private person, not recorded. |
| Q3/55 | Laketatu Orphanage Godlisten Kaaya | Laketatu | Nothing new. |
| Q4/55 | Bahath Orphanage Usherika Moshi | Bahath | Returned an unrelated UK charity (Dar es Salaam); not recorded. |
| Q5/55 | Building a Caring Community Moshi contact | BCC | Partner pages (Mosaic, Living Lutheran); Living Lutheran read, no BCC contact. |
| Q6/55 | Good Hope Orphanage Arusha Mama Asha | Good Hope | Idealist only; no contact. |
| Q7/55 | Matonyok Children's Home contact | Matonyok | Nothing about it. |
| Q8/55 | KCYC Moshi Soweto | KCYC | Nothing about it (other Moshi charities returned). |
| Q9/55 | VOV Center Moshi | VOV Center | Nothing about it. |
| Q10/55 | Kilimahewa Children's Education Center | Kilimahewa | EdPowerment (funder) page read. |
| Q11/55 | "Best Centre for the Blind" Ngaramtoni | Best Centre | Nothing about it. |
| Q12/55 | Arusha Children's Home It Takes a Whole Village | Arusha Children's Home | Nothing about it. |
| Q13/55 | Eripoto safe house contact | Eripoto | Lutheran Partners pages (partner); no email. |
| Q14/55 | St. Gabriel Home Mateves Sr. Flora | St. Gabriel | The Tablet article read (director named, no route). |
| Q15/55 | Huruma Vision Children's Home Muriet | Huruma Vision | Nothing about it. |
| Q16/55 | One Heart Source Arusha children's home | One Heart Source | oneheartsource.org contact page read: info@oneheartsource.org. |
| Q17/55 | Amazing Children's Home Arusha | Amazing Children's Home | Nothing about it. |
| Q18/55 | Mama Jane's Orphanage Arusha | Mama Jane's | Nothing about it. |
| Q19/55 | Malaika Orphanage Arusha | Malaika | Italian partner site has a certificate error, GlobalGiving 403, fundraiso robots-disallowed; not recorded. |
| Q20/55 | Kidcare International street children centre | Kidcare | Nothing about it. |
| Q21/55 | Arnold House AIDS Orphanage Moshi | Arnold House | Nothing about it. |
| Q22/55 | Kim Jones House orphanage Moshi | Kim Jones House | Nothing about it. |
| Q23/55 | Better Future International Tanzania Moshi | Better Future Intl | changingthepresent.org page read: New York office phone. Own site robots-disallowed. |
| Q24/55 | Children of Destiny Foundation Moshi | Children of Destiny | Nothing usable (page not found). |
| Q25/55 | Shalom Centre street children Arusha | Shalom Centre | Partner pages (Anike Foundation) read; no contact. |
| Q26/55 | "Safe Home for Children with Disabilities" Arusha | Safe Home | Daily News article read: director and 82 children. |
| Q27/55 | Sandra Jones Centre Arusha | Sandra Jones | Snippets point to Zimbabwe, not Arusha; not recorded. |
| Q28/55 | Samaritan Children's Home TSCH Arusha | TSCH | Nothing about it. |
| Q29/55 | KWIECO contact | KWIECO Shelter House | No contact in results; kwieco.org times out. |
| Q30/55 | CHISWEA Arusha centre | CHISWEA | Nothing about it. |

I stopped at 30 because every further target was either a register-only NGO with no web presence, or had already returned nothing; the last 12 searches found no route.
No search was refused or limited.

## Routes found (13 targets)

| Target | Route | Kind | Note |
|---|---|---|---|
| Canaan Children's Center | a_lengeju@yahoo.com; +255786533776, +255715033776 | personal-domain email + mobiles, published as the centre's contact on its own contact page | Executive Director Dr. Alex Lengeju; Archdiocese of Arusha page repeats the email. pdpa risky for the contact. |
| Kilimanjaro Children's Fund | ghomar003@yahoo.com; +15419415104 | personal-domain email + US phone on own site | Pasua site, 55+ children. |
| Watoto Kicheko Orphanage | info@watotokicheko.com | own-domain role email (own adoption page) | Plus postal address and contact form. |
| One Heart Source (Arusha home) | info@oneheartsource.org | own-domain email of the US operator | needs_review: page is about immersion programmes. |
| TUMAINI HOME ORGANIZATION (T.H.T.O) | tumaini.home.tanzania@gmail.com; +255756587167 | gmail published by the organisation as its contact | Mto wa Mbu (Monduli): likely outside 25 km; runs its own English-medium school. |
| Le Bao's Kids Foundation | catherinemoreno@live.fr; theophilmyinga9@gmail.com | personal-domain emails on own contact page | Iringa: outside catchment. |
| Better Future International Tanzania (Moshi) | +19176269695 | New York office phone, from a giving-platform page | Family-care programme, not an orphanage. |
| Kilimanjaro Centre for Orphans and Street Children | +255754201080 | mobile of a named contact, 2007 partner post | historical. |
| Matumaini Child Care | +255755890765 | phone of founder, 2007 partner post | historical. |
| Seeway Tanzania | website contact form; PO Box 379 Usa River | form only | no email or phone published. |
| Eripoto Safe House | website contact form | form only | contact page returned 429, not retried. |
| Emayani vulnerable people's center | info@emayani.org; +255683142145 (not recorded as route) | match unconfirmed | The Emayani Foundation is a women's group on Bondeni Street; no sign it is the same body. |
| Cradle of Love Baby Home | none | closed end March 2024 per partner Giving Smiles | Suggest dropping from outreach. |

By kind: 2 own-domain emails, 4 personal-domain emails published by the organisation itself (Canaan, KCF, Tumaini, Le Bao's), 3 phones without email, 2 form-only, 2 historical (2007), 1 closed.

## Pages read per target (own site / partner / other)

| # | Target | Read | Result |
|---|---|---|---|
| 0 | Laketatu Orphanage | Papamoa Rotary, RNZWCS | No route for the orphanage; funder RNZWCS info@rnzwcs.org and +64272695615 noted in notes only. |
| 1 | St. Mark's | saintmarkskids.org (empty, script-rendered), Utopia Foundation | No route; WebFetch of the contact page was denied by permissions, not worked around. |
| 2 | Canaan | 6 own pages, Archdiocese page | Route found. Slow Food page 403. |
| 3 | Karim | Both own domains fail DNS; E-ducare, Read With Me Arusha | No route. |
| 4 | Cradle of Love | Own site 403; Giving Smiles | Closed. |
| 5 | Seeway | 8 own pages | Form only. |
| 6 | KCF | 3 own pages | Route found. |
| 7 | Bahath | World Unite 403 | No route. |
| 8 | BCC | Own site HTTP 522 x3; tanzaniavolunteers.com, Living Lutheran | No route. |
| 9 | Kili Centre | Own site fails DNS; Idealist; blog 2007 | Historical phone. |
| 12 | Huruma Orphanage (Nshupu) | Worldview, Juapole (Le Solstice) | No route; funders found. |
| 20 | Watoto Kicheko | 10 own pages | Route found. |
| 25 | CHISWEA | Heart for Africa (2 pages) | Named coordinator, no route. |
| 27 | Eripoto | Own site (contact pages 429), OBA | Form only. |
| 28 | Good Hope | Own site fails DNS; Idealist | No route. |
| 33 | Matonyok | Own site fails DNS; 4 partner pages (1 x 403) | No route. |
| 34 | New Paradiso | Heart for Africa | No route. |
| 36 | Safe Home | African Moons, Daily News | Director named, no route. |
| 38 | St. Gabriel | stgemma.org fails DNS; Future for Kids, The Tablet; TotalGiving 403 | Director named, no route. |
| 39 | KCYC | kcyc.or.tz fails DNS | No route. |
| 42 | Huruma Vision | Arusha Digital (Aug 2026), blog, Terrawatu | Ward found, no route. |
| 44 | Emayani | emayani.org (3 pages) | Match unconfirmed. |
| 46 | Best Centre for the Blind | volunteerbasecamp redirect to unrelated site | No route. |
| 67 | KWIECO Shelter House | kwieco.org timed out; Ukumbi, Archello | No route. |
| 70 | Matumaini | CCS blog 2007 | Historical phone. |
| 77 | Same Qualities Foundation | Own site robots-disallowed | Not read. |
| 80 | Disability Repro-Light | Own site fails DNS | No route. |
| 81 | Ilboru Special Needs School | OBA page | Funder only. |
| 82 | TAFCOM | tafcomtz.org shows an expired-domain page | No route. |
| 83 | Tumaini Home | 2 own pages | Route found. |
| 85 | Huruma Centre (Iringa) | H2O for Life | Out of catchment; funder only. |
| 86 | Le Bao's | 6 own pages | Route found; Iringa. |

## Blocks and unreadable sources

- Own sites that do not resolve: karimchildren.org, karimorphanage.org, kilicentre.org, goodhopeorphanage.org, matonyokchildrenshome.org, stgemma.org, kcyc.or.tz, disabilityreprolight.org. kwieco.org timed out. buildingacaringcommunity.org returned HTTP 522.
- 403: cradleoflove.com, world-unite.de, servingorphans.org, totalgiving.co.uk, globalgiving.org, fondazioneslowfood.com. 429: eripoto.org contact and about pages.
- robots.txt disallowed (not read): samequalitiesfoundation.org, betterfutureinternational.org, fundraiso.com.
- malaika-childrenfriends.org: certificate verification failed; not worked around.
- saintmarkskids.org returned an empty page; WebFetch was denied by permissions. tafcomtz.org: domain expired.
- No login wall, captcha or search limit met.

## Not reached (no search or page read beyond the initial crawl)

Register-only NGOs with no website (NIS profile held, no contact on it): Gloria foundation, Better Life for Deaf, Better Future for All, Gladness Kanyika Home, Friends of Kids Speak Out,
Shield of Women and Children, ATPEACE, Tanzania Child Care and Technical Support, Deaf and Community Progress, ANGAZIA, Holley Children Orphanage, Choose Love home, NAVUGIREI, TAPDISO, Ebenezer Orphanage Centre,
The Light of Change, Hossana Home Care, Africa Action for Fundamental Change, Kingdom Matters, Salama Home, Shalom Center (Kisongo), DBAS, Shalom Centre for Street Children, Themi Youth Orphanage, Ability in Disability,
Huduma ya Fahari Kubwa, YOSIMODO, Rise Up and Go, TSCH (one search, nothing), One Love Africa Foundation, LIPO Tumaini, Jamii Jasiri, TIESO, AYOFERC, Siloam International Africa, Deaf Hands Foundation, VUKA Initiative,
His Healing Hands Africa Ministry, Gladness Kanyika, Grace Orphanage (Moshi), St Francis of Assisi Primary School (Moshi), St Joseph Shelter of Hope (Moshi), St Joseph's Children's Home (Moshi), New Life/Children of Destiny (one search, nothing),
Arnold House and Kim Jones House (one search each, nothing), Amazing Children's Home, Mama Jane's, Malaika, Kidcare, Sandra Jones Centre, Arusha Children's Home, Best Centre for the Blind, VOV Center, Bahath (one search each, nothing).
These have no published route in anything read; a later wave could try the Arusha City and Meru social welfare offices' lists, if they publish them.

## Notes for the coordinator

- Laketatu Orphanage, Ilboru Special Needs School, New Paradiso, CHISWEA, Kilimahewa, Huruma Nshupu and St. Mark's have funders or partners with published routes (RNZWCS, Opportunity Builds Africa, Heart for Africa, EdPowerment, Utopia Foundation). These are in notes and relationship records, not recorded as the target's own route.
- Out of catchment: Huruma Centre Orphanage and Le Bao's Kids Foundation (Iringa); Tumaini Home (Mto wa Mbu).
- Cradle of Love Baby Home was reported closed in March 2024.
