# Coverage log: wave10_master_employers_b (2026-10-02)

Slice: runtime/contacts/slices/wave10_master_employers_b.json (40 master organisations, nearest first, all listed as needing a named decision-maker).
Output: data/raw/contact-research/search_wave10_master_employers_b_2026-10-02.jsonl (40 lines).
Method: every organisation's TATO member page (tatotz.org/portfolio/...) was fetched first (no search cost) to get the website, then each website's home, contact, about and team pages were read with the project fetcher (robots.txt honoured, fetches spaced). Searches were used only where that gave nothing.

Searches used: 36 of 37 (Q37 not used). No search was refused. No search was routed through WebFetch or a browser.

## Searches

| No. | Query | Outcome |
|---|---|---|
| Q1/37 | "Gemuka Adventures" Arusha | own site found (gemukaadventures.com); pages fetched name no one |
| Q2/37 | "Arusha Local Trips Tanzania" Limited | TATO page and arushatrips.com; founder "Lex" on the site |
| Q3/37 | "Hanspaul Automechs" Arusha | hanspaul.co.tz (403) and a corporate-partner page at ugandatouroperators.org naming the founders |
| Q4/37 | "Wakali Safaris" Arusha founder | only Tripadvisor snippet naming owners by first name (not a source); site 403 |
| Q5/37 | "Serengeti Balloon Safaris" Arusha | balloonsafaris.com found; team page names founders and managers |
| Q6/37 | "United Aviation Services" Arusha Tanzania managing director | no person on any allowed source |
| Q7/37 | "Delight Polyclinic" Arusha | own site only; no person |
| Q8/37 | "The Safari Doctors" Arusha | own site only; Kenyan namesake ignored |
| Q9/37 | "Aglow Safaris" Arusha founder director | nothing usable |
| Q10/37 | "Miles to Smile" Arusha safari company | review sites only; site 403 |
| Q11/37 | "Ronjoo Safaris" Arusha | directory listings only |
| Q12/37 | "African Galleria" Karatu Tanzania | news and review pages only; no allowed person source |
| Q13/37 | "Safari Plus" safariplus.co.tz Arusha | own site; head office in Dar es Salaam |
| Q14/37 | "Roy Safaris" Arusha managing director | ZoomInfo and Crunchbase only (not sources) |
| Q15/37 | "Sher East Africa" Arusha | TATO page only |
| Q16/37 | "Lashku Forex Bureau" Arusha | TATO page only |
| Q17/37 | "Colours Africa Tours and Safaris" Arusha | review sites only; site 500 |
| Q18/37 | "Ebony Tours" Safaris Arusha | ebony-safaris.com found; no person |
| Q19/37 | "Meijo Safaris" Arusha founder | LinkedIn and travel-network snippets only (not sources) |
| Q20/37 | "Myriad Safari" Arusha director | directory snippet only (not a source) |
| Q21/37 | "E&H Tanzanian Adventures" Arusha | own site and reviews |
| Q22/37 | "Stavo Adventures" Arusha | TATO page only |
| Q23/37 | "See Endless Adventures" Tanzania founder | directory snippets only (not sources) |
| Q24/37 | "Ignite Energy Access" leadership team chief executive | own-site blog page names the group CEO and President |
| Q25/37 | "Alex Walker's Serian" founder Alex Walker | serian.com page "The Wild Bunch - Alex Walker" |
| Q26/37 | "Abercrombie & Kent" Tanzania country manager Arusha | A&K DMC Tanzania contact page names a contact with email and phone |
| Q27/37 | "Sidai Designs" Arusha founder | sidaidesigns.com found; Our Team page lists directors by first name |
| Q28/37 | "Sabrahm Consulting" Arusha director | ZoomInfo and LinkedIn only (not sources) |
| Q29/37 | "Superdoll Trailer Manufacturer" Arusha branch manager | LinkedIn and ZoomInfo only (not sources) |
| Q30/37 | "Travelling Monkey" safari Tanzania founder | no names |
| Q31/37 | "Hanspaul Assurance Brokers" Arusha director | group pages; hanspaul.co.tz Team page is 403 |
| Q32/37 | "Africanzoom Safaris" Arusha founder managing director | ZoomInfo only (not a source) |
| Q33/37 | "4x4 Safaris Adventures" Arusha Tanzania owner | review sites only |
| Q34/37 | "Serengeti Wakanda" Tours Safaris Arusha founder | founders named only in a third-party snippet; own pages do not repeat them |
| Q35/37 | "Explora V Tanzania" Arusha | own site and reviews |
| Q36/37 | "Safari Wholesalers and Retailers" Arusha | safariwholesalers.com ("Coming Soon") |

## Blocks and unreadable sites (recorded, not worked around)

- wakalisafaris.co.tz and www.wakalisafaris.co.tz: HTTP 403.
- miles-to-smile.com: HTTP 403.
- hanspaul.co.tz (home, /hal/, /team/): HTTP 403.
- africangalleria.co.tz: HTTP 503; africangalleria.com: TLS handshake failure.
- coloursafrica.com: HTTP 500.
- sher.co.tz and ronjoosafaris.co.tz: script-built, no readable text.
- exploravtanzania.com/contact-us/: now shows unrelated content (a gambling-style page); not used. Home page is used for the shared email and phone only.
- goldfinch-adventures.com/admin/login: disallowed by robots.txt and a login; not opened.
- robots.txt was readable on every site read (a 4xx robots.txt means no rules); no robots.txt was unreachable.

## Organisations not reached

None. All 40 were researched.

## Results

- 9 found (named leaders): Pure Afro Travels, Alex Walker Safaris, Babji Tours & Safaris, Hanspaul Automechs, Serengeti Balloon Safaris, Arusha Local Trips Tanzania, Transcendent Journeys Tanzania, Goldfinch Adventures, Sidai Designs.
- 31 partial (routes from TATO and/or the own site, no named person), 0 not_found, 0 blocked as a status (blocks are noted in notes).
- 23 people recorded: 19 with a leadership or management role; 4 contacts with no title (Alex and Terry for Arusha Local Trips, Nishit for African Galleria, Happy Richard for A&K Tanzania).
- 1 person with a direct work email (Happy Richard, A&K Tanzania, from the A&K DMC Tanzania contact page). No email was inferred. Named inboxes that no source links to a person (for example victor@, satbir@, pascal@, flavia@) are recorded as organisation inboxes only.
- Names recorded in part: Lex, Alex, Terry, Nishit, Becky, Eszter, Julie.
- The Hanspaul Automechs founders come from an operator-association directory page (ugandatouroperators.org), not the company's own site. The Ignite Energy Access leaders are the group's, so that record's identity is marked uncertain.

## Segment and location warnings (for review items)

Many records in this slice are TATO affiliate members filed as "Safari / tour operator" that are not tour operators: Delight Polyclinic, The Safari Doctors, Hanspaul Automechs, Hanspaul Assurance Brokers, United Aviation Services, Ignite Energy Access, Superdoll Trailer Manufacturer, Lashku Forex Bureau, Sabrahm Consulting, Safari Wholesalers and Retailers, African Galleria, Safari Plus (air charter, head office Dar es Salaam), Sidai Designs, Sher East Africa. Miles to Smile and African Galleria have locations to check (Moshi P.O. Box; Manyara). 4x4 Adventures and Stavo Adventures have a P.O. Box or phone that differs between TATO and their sites. Lashku Forex's only inbox is on another business's domain (praxisaccounts.com).
