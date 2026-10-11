# Coverage log: hd1_welfare_introducers (high-direct wave, 11 October 2026)

Slice: `runtime/contacts/slices/hd1_welfare_introducers.json` (78 organisations: 12 company-master introducers and 66 welfare-run records), worked nearest first.
Output: `data/raw/contact-research/search_hd1_welfare_introducers_2026-10-11.jsonl` (78 lines, one per organisation).

**Search allowance:** 57. **Used: 35** (Q1/57 to Q35/57). I stopped early because results were very thin: 30 of the first 32 searches added no address. The search engine also ignored `site:` and quoted-address operators, so the remaining allowance looked unlikely to pay off. No search was refused for the session limit.

**Method.** Before searching, I read every organisation's known sources and own site. This included pages and PDFs the deep crawl had not reached: Kontakt and imprint pages, vacancy notices, annual reports and policy PDFs, and staff profile pages. Pages were read through `contact_lib`, which keeps the HTTP cache, honours robots.txt and reports blocks. Requests to the same host were spaced at least 2.2 seconds apart, across runs. Earlier coverage logs were checked, and their queries were not repeated. No addresses were constructed from patterns. LinkedIn, data brokers and review sites were not used. Nobody was contacted.

## Results by status

| Status | Count |
|---|---|
| found (the named decision-maker's own published work email, or the inbox for their exact role) | 5 |
| partial (routes and/or named decision-makers, no direct address) | 64 |
| not_found | 5 |
| blocked | 4 |

**Direct addresses found (5):**
- East African Business Council: Executive Director. `director@eabc-online.com` is the role inbox, taken from EABC's own vacancy notices.
- Africa Amini Alama: President. `cornelia@…` and a Tanzanian mobile are in her block on the Kontakt page. The founder's own address is on the same page.
- Christian Social Services Commission (welfare record): Executive Director. `pmaduki@…` is on his own-site profile; the master record already holds it.
- ELCT Northern Diocese: General Secretary. `generalsecretary@…` and his mobile are in his block on the diocese's own page.
- Innovo Benefits Group: President. `egulko@…` is in his block on the team page.

**Other addresses of note:**
- TNCC (national): the HR and Administration lead has her own address and mobile in her block. She is an HR decision-maker, not the CEO.
- Giving Smiles: the second chair has her own first-name inbox. The 2024 report gives `info@` as the first chair's contact.
- Neema Orphanage Centre: the head of the sisterhood that runs it is named on the parent body's page, with the sisterhood's inbox and her mobile.
- Hope and Soul (trustee) and FAE (Executive Director): personal Gmail and Hotmail addresses, recorded as risky. They are never routes until a person approves them.

**New in-country leads named (no address):**
- CTI Arusha/Moshi Outreach Manager
- ATE Northern Zone Manager (May 2023 post)
- WIWOCHI Managing Director (first name only)
- TFFT Managing Director
- Bassari on-site Director
- MILELO Local Manager
- kipepeo Tanzanian co-founder and Local Leader
- Emusoi Management Committee
- SOS Tanzania National Director, confirmed on the national site
- ELCT North Central Diocese children's unit coordinator (with her mobile)

**Data-quality flags (in notes):**
- O'Brien School: the recipient on file is a ward-council chairman quoted in a testimonial. He holds no role at the school.
- Tabasamu Africa: the "leader" on file is a quotation attribution, and the team page is empty.
- ANGONET: an Executive Director is named above the Coordinator on file.
- TFFT, MILELO, kipepeo and Happy Family: the recipients on file are overseas executives, and an in-country manager is named.
- Ucare Family Home: run day to day by Neema House. This may overlap with a Neema Village record.
- Tumaini House: assumed to be YWAM Arusha's Tumaini Children's Ministry, so identity is uncertain.
- Capital International: fit as a welfare funder needs checking.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/57 | `"Tanzania Horticultural Association" "@taha.or.tz" CEO` | TAHA | News and profiles only; no address. |
| Q2/57 | `"Hotel Association of Tanzania" "@hat-tz.org"` | HAT | Only info@ (ATE member directory). Nothing new. |
| Q3/57 | `"Tanzania Bankers Association" "@tanzaniabankers.org"` | TBA | Own pages and news only; no named address. |
| Q4/57 | `"Tanzania Private Sector Foundation" "@tpsf.or.tz"` | TPSF | Job-board copies give recruitment@ and a press contact's address. Not the acting CEO's. |
| Q5/57 | `site:tncc.or.tz "Maeda"` | TNCC Arusha | No tncc.or.tz results; the site: operator was ignored. |
| Q6/57 | `"Women HR Association of Tanzania" "@what.or.tz"` | WHAT | Nothing relevant. |
| Q7/57 | `site:cti.co.tz "Malabeja"` | CTI Arusha/Moshi | No cti.co.tz results; the operator was ignored. |
| Q8/57 | `"TCCIA Kilimanjaro" chamber Moshi chairman executive officer` | TNCC Kilimanjaro | National leaders only; no Kilimanjaro chamber head. |
| Q9/57 | `"Little Oasis Foundation" Arusha founder director` | Little Oasis | Nothing about the organisation. |
| Q10/57 | `"Neema Orphanage Centre" Machame Hai` | Neema Orphanage Centre | Job-board vacancy notice: run by Ushirika wa Neema (ELCT ND). Led to the diocese's diaconal page (head, phone, inbox). |
| Q11/57 | `"WIWOCHI" "@wiwochi.org"` | WIWOCHI | Nothing relevant. |
| Q12/57 | `"Foundation for Tomorrow" Arusha "@thefoundationfortomorrow.org"` | TFFT | Profiles and a data-broker pattern only (not used). |
| Q13/57 | `"Compassion International Tanzania" "@tz.ci.org"` | Compassion Tanzania | News only; no address. |
| Q14/57 | `"Project Zawadi" "@projectzawadi.org"` | Project Zawadi | donate@ and an old 2020 job contact. Not the Country Manager's. |
| Q15/57 | `"Arusha NGO Network" "@angonet.or.tz"` | ANGONET | Funder profile only. |
| Q16/57 | `"Gily's Children Foundation" "@gilyschildrenfoundation.org"` | Gily's | GoFundMe and GoOverseas only; no address. |
| Q17/57 | `site:angonet.or.tz "Bayo"` | ANGONET | Operator ignored; nothing. |
| Q18/57 | `site:tupendanefoundation.or.tz "Masunga"` | Tupendane | Operator ignored; nothing. |
| Q19/57 | `site:himd.or.tz "Rumanyika"` | HIMD | Operator ignored; nothing. |
| Q20/57 | `site:cit.or.tz "Lema"` | Compassion Tanzania | Operator ignored; unrelated politician. Nothing recorded. |
| Q21/57 | `"Tanzania Horticultural Association" vacancy "send your application"` | TAHA | Job-board copies: recruitment@taha.or.tz, addressed to the HR and Admin Manager. Not a person's route. |
| Q22/57 | `"Tanzania Bankers Association" vacancy "Executive Director" application email` | TBA | Nothing. |
| Q23/57 | `"Arusha NGO Network" vacancy OR "send your application"` | ANGONET | Other NGOs' vacancies only. |
| Q24/57 | `"Tanzania Child Rights Forum" annual report filetype:pdf` | TCRF | No report. IATI lists childrightsforum.org, which was fetched and is empty. |
| Q25/57 | `"SOS Children's Villages Tanzania" national office Dar es Salaam contact email` | SOS Arusha | Gave the national domain sos-tanzania.org. Its own leaders and contact pages were read: National Director confirmed; national.office@ only. |
| Q26/57 | `"Selfless Solutions" Arusha Sing'isi program manager` | Selfless Solutions | News and Idealist only. The own site is still 403. |
| Q27/57 | `"Tabasamu Africa Organization" Arusha` | Tabasamu Africa | Idealist listings only; no leader. |
| Q28/57 | `APHFTA "Northern Zone" Moshi zonal coordinator` | APHFTA | Other regions' vacancies only. |
| Q29/57 | `"O'Brien School for the Maasai" executive director OR "head teacher"` | O'Brien School | News about the US founder only (not a source for people). No school head named. |
| Q30/57 | `"Ujamaa Children's Home" Arusha "@ujamaachildren.org"` | Ujamaa | Idealist gives ujamaachildren.com; that host fails the TLS handshake (block). |
| Q31/57 | `"Tumaini Children's Ministry" YWAM Arusha` | Tumaini House | YWAM directory confirms the ministry exists; no lead named. |
| Q32/57 | `"Emusoi Centre" Arusha director` | Emusoi | Led to the centre's own July 2026 letter: three-member Management Committee. |
| Q33/57 | `"TCCIA Arusha" regional chamber executive officer email` | TNCC Arusha | Snippet of an old job advert: Regional Executive Officer at a Gmail inbox (fetched: false; the PDF answered HTTP 202 with no content). |
| Q34/57 | `"Association of Tanzania Employers" Arusha zonal office manager` | ATE | ATE's own May 2023 post names the Northern Zone Manager and zone chair. |
| Q35/57 | `"Hope and Soul Tanzania" "@hopeandsoul.org"` | Hope and Soul | Charity register gives a Gmail inbox; no own-domain address. |

## Blocked sites (recorded, not worked around)

- selflesssolutions.org: HTTP 403.
- malaika-childrenfriends.org: TLS certificate verification failed.
- ujamaachildren.org: HTTP 429 at crawl. ujamaachildren.com: TLS handshake failure.
- farajaschool.org: HTTP 403.
- tnrf.org PDF (TCCIA Arusha advert): HTTP 202 with no content. Snippet only.

**robots.txt notes:**
- www.sinonngarashied.or.tz: robots.txt was unreachable. Pages were read anyway; flag "robots.txt unreachable".
- mail.aphfta.org, africaaminialama.com and gilyschildrenfoundation.org: robots.txt answered 4xx, which means no rules.
- No disallowed page was read.

**Other failures:**
- aphfta.org and aphfta.or.tz do not resolve (DNS failure).
- Several PDFs exceed the 2 MB read limit and were read only in part: TFFT annual reports, Tupendane annual reports and O'Brien reports.

## Organisations not reached or not searched

All 78 organisations were read from their own sites or known sources where one was readable. Several were left with no search because nothing searchable remained, or because earlier waves had already searched them:
- The Small Things (Happy Family): script-built site.
- Dyslexia Tanzania.
- Zorah Organization.
- Godparents for Tanzania: single-page script-built site.
- Malaika Children's Friends, Faraja Fund and Selfless Solutions: blocked. Selfless Solutions did get one search.
- Most overseas funders (Asali, Capital International, EdPowerment, URRC, Friends of Tanzania, GDG USA, Imaniworld, My Daily Armor, One Kind Act, Opportunity Builds Africa, Vibrant Village, Vrienden van Amani, WATOYO): their own sites were read and give only general inboxes.

22 searches remain unused from this agent's allowance.
