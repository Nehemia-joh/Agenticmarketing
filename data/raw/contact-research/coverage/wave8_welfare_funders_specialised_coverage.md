# Coverage log: wave 8, welfare funders and specialised centres (26 September 2026)

- **Slice:** `runtime/contacts/slices/wave8_welfare_funders_specialised.json`, nearest first: 24 welfare organisations (6 specialised centres and 18 funders) that already had a published route but no named decision-maker. Every one needed only a named decision-maker.
- **Output:** `data/raw/contact-research/search_wave8_welfare_funders_specialised_2026-09-23.jsonl`, one line per organisation, appended as each was finished and finally put in slice order. The date key is the programme's shared key; the access date is 26 September 2026.
- **Searches:** allowance 18 WebSearch calls; 9 were made (Q1/18 to Q9/18), each naming one organisation, and none was refused by the session cap. No search was routed through WebFetch, a browser or a results page. Q1-Q4 served organisations whose own pages gave nothing (a blocked site, a parked domain, a site with no names, a site that stopped answering). Q5-Q9 were single searches for five organisations whose own pages left a gap (Kafika House: no executive; KMHO: no US officers; One Heart Source: only a 2021 officer; ACT: contacts without roles; UBORA: no Tanzania-side leader); no organisation had a second search.
- **Fetching:**
  - Pages were read with `scripts/contacts/read_page.py` (shared cache, per-site spacing, robots.txt honoured), plus small helpers in `runtime/contacts/agents/wave8_welfare_funders_specialised/`: a link lister and a PDF text reader on the same fetcher, and the crawler's Cloudflare-email decoder (`contact_lib.decode_cfemail`).
  - Three PDFs larger than the shared fetcher's 2 MB limit (Giving Smiles' 2024 annual report, the Koch Foundation's 2025 annual report, Terrawatu's 25 Years Impact Report) were downloaded once each, after a robots.txt check and with the fetcher's user agent, into the agent's folder (`pdf/`).
  - The shared cache held only the metadata (no body) of arushachildrenstrust.org's home and contact pages, so the contact page was read once afresh into the agent's folder (`pages/`) the same way; the shared cache was not changed.
  - WebFetch was tried twice on known URLs, never for a search: the GO Campaign article on Gabriella (HTTP 404) and Imaniworld's register certificate (connection refused). Both failed and nothing was taken from them. The browser was not used.
  - robots.txt was read for every host fetched; a 4xx robots.txt counted as no rules. One page was disallowed and not read (below). No page was read under an unreachable robots.txt.
- **Organisations written:** 24 of 24.
  - Status: found 21, partial 1, not_found 2, blocked 0.
  - Identity: confirmed 24.
  - Not reached: none.
- **Results:**
  - 118 named people across 22 organisations, all from fetched pages; PDPA risk medium for all.
    - Sources: the organisation's own site, report or letter 67; official IRS filings (Form 990 or 990-PF shown by ProPublica) 48; a parent body's official directory (ELCT Northern Diocese) 2; a funder's own partner page (Segal Family Foundation) 1.
    - 76 hold a role the profile builder counts as a decision role, across 20 organisations. Emusoi's three leads form its Management Committee (the body now running the centre) and ACT's two leads are contacts without stated roles; neither is flagged as a decision role by `contact_lib.DECISION`.
    - 7 are named by one name only and will be labelled incomplete: Giving Smiles' four volunteer project coordinators (Annika, Patricia, Katha, Steffi), Kafika House's two new staff (Ancimary, Chenay) and TrueToTanzania's founder ('Shoshi').
    - 5 carry a work email that the same source gives for contacting them (three Giving Smiles project inboxes, TrueToTanzania's Kilimanjaro trip leader, UBORA's president).
  - Routes: 29 emails, 20 phones, 14 postal and 6 physical addresses, 23 official social links, 21 websites.
- **Prior evidence read before any search:** the slice; `data/raw/welfare-research/research_*.jsonl` (records for all 24, reused: Segal Family Foundation for Gabriella, ProPublica EINs for the US funders, LOHADA for Kesho); all earlier `data/raw/contact-research/*.jsonl` (five had earlier records: Mkombozi's parked domain, and four funders whose pages named no leader); the crawler's pages in `website_contacts_2026-09-23.jsonl`; the NGO register profiles (no leaders listed).
- **Recording rules applied:**
  - People come only from the organisation's own site, report or letter, an official filing, a parent body's official directory, or a funder's own page (Gabriella; the note says so).
  - Not recorded as leads: people who have died (Emusoi's founder-director, ACT's founder, a Koch Foundation vice president), roles no longer held (UBORA's chairman emeritus, Kafika's former clinical services manager), staff outside outreach (guards, watchmen, chef, housekeeper, IT and social-media staff, an administrative assistant), advisory councils, testimonial authors, other organisations' staff (Maryknoll Sisters' donations contact, Rummelsberger Diakonie's contact, the Wilderness Trails director, Amani Centre's own staff), LinkedIn personal profiles, and names behind GuideStar's subscription.
  - Also not recorded: biographies and personal statements (Giving Smiles, One Kind Act, Terrawatu, Treasures of Africa, TrueToTanzania, Love for the Least), family ties (joint listings of couples were recorded as two people without the relationship), officers' towns (URRC e.V.), street addresses that look private (Giving Smiles' and ACT's Impressum or contact addresses, Kesho's Columbus address, Imaniworld's flat), compensation figures from the filings, and bank details.
  - Nothing about children, parents or residents was recorded; the newsletters, blogs and story pages that name children or students were used only for the adults' roles or not at all.
  - Roles were kept to 80 characters and without the person's name, because `contact_lib.clean_role` cuts a role at the name and after 80 characters. Notes are at most 600 characters (the profile builder keeps only the first 600) and their warning phrases were checked against `contact_lib.note_flags`. The flags raised are intended: possible closure, parked site and website gone (Mkombozi); check before outreach (Emusoi, ACT, Hidden With Christ Ministries, Terrawatu); fit to check (One Heart Source, TrueToTanzania, UBORA).

## Status definitions

- `found`: identity confirmed and at least one named person who leads or decides for the organisation, read on a fetched page of the organisation, an official filing or register, its parent body, or a funder naming its current leaders.
- `partial`: named contacts whose roles are not stated, or leads whose currency is doubtful.
- `not_found`: no named decision-maker found.
- `blocked`: the only promising source refused automated reading (none; Faraja's blocked site was covered by its parent body).

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| Q1/18 | `"Faraja Diaconic Centre" Sanya Juu` | 5. Faraja Diaconic Centre | Own site farajaschool.org answers HTTP 403. Results led to the ELCT Northern Diocese's diaconal-institutions directory (read): the centre's head (Kaka Mkuu) and the special school's head teacher, phone, Gmail, P.O. Box 167 Sanya Juu. Rummelsberger Diakonie and faraja.de (partners, read) name no leader; ushirika-wa-diakonia-faraja.org answered 404. found |
| Q2/18 | `"Mkombozi Centre for Street Children" Moshi` | 6. Mkombozi Centre for Street Children | Only historical material: CRIN archive (read, no names), research papers, GlobalGiving reports (HTTP 403), NGO Explorer (UK support charity's last income December 2013). Domain parked. not_found, possible closure |
| Q3/18 | `"Gabriella Children's Rehabilitation Centre" director` | 7. Gabriella Children's Rehabilitation Centre | GO Campaign article (HTTP 404, also by WebFetch), LinkedIn personal profiles (not used), Catchafire (script shell), Tanzania Volunteers and Autism Connect (404). The funder Segal Family Foundation's own partner page, reached through its partner list without a further search, names the executive director. found |
| Q4/18 | `"Asociación Imaniworld" Tanzania presidenta` | 16. Imaniworld | Only the association's own pages (host unreachable) and unrelated results. not_found |
| Q5/18 | `"Kafika House" Arusha executive director` | 3. Kafika House | Partner pages (Build Health International: no names; Explorations Company: founder in 2008 only), Idealist (Friends of Kafika House), a LinkedIn profile (not used). No executive named; board from its own site stands. found |
| Q6/18 | `"Kilimanjaro Mission of Hope and Outreach" Portland Oregon` | 8. KMHO | Charity Navigator, Cause IQ, Zeffy, Instrumentl, GrantAdvance and the official 'KMHO Education' Facebook page; gave EIN 47-1398078, whose ProPublica page (read) lists the FY2024 president, treasurer, chaplain and five directors. found |
| Q7/18 | `"One Heart Source" Pasadena nonprofit executive director` | 20. One Heart Source | GuideStar profile (read): principal officer matches the FY2021 Form 990 president; Wikipedia, Crunchbase, Cause IQ not used for people. partial raised to found |
| Q8/18 | `"Arusha Children's Trust" Scotland charity trustees` | 4. Arusha Children's Trust | Only the Trust's own home page and unrelated charities (Project Arusha, Arusha Kids Trust in Sydney, other Scottish charities). No register entry or roles. partial |
| Q9/18 | `"UBORA Tanzania" Siha Karansi director` | 24. Uboratz Inc (UBORA) | A UBORA blog post (read) names the president with a work email; the Siha Leadership School site is disallowed by robots.txt (not read); LinkedIn profiles and an 11Alive news story not used; a snippet names an in-country partner (SHEFO), not recorded. found |

## Blocked, unreachable and missing sources

| Source | Result | Organisation |
|---|---|---|
| https://www.farajaschool.org/ and /contact-us/ | HTTP 403 (blocked; not worked around) | Faraja Diaconic Centre |
| https://www.globalgiving.org/projects/tanzanian-street-children/reports/ | HTTP 403 (blocked) | Mkombozi |
| https://www.uboraleadershipprimary.sc.tz/overview-1 | robots.txt disallows; not read (browser-pass candidate) | UBORA |
| https://imaniworld.org/ (legal notice, register certificate, projects) | host timed out, then refused connections (network failure, not an HTTP block); retry later | Imaniworld |
| https://www.mkombozi.org/ | parked domain, no content | Mkombozi |
| gocampaign.org article, tanzaniavolunteers.com page, autismconnect.com entry, ushirika-wa-diakonia-faraja.org/about.html | HTTP 404 | Gabriella, Faraja |
| https://www.segalfamilyfoundation.org/portfolio-items/gabriella-centre/ | old URL redirects to an image; the funder's current partner page was used | Gabriella |
| https://www.catchafire.org/organizations/gabriella-children-s-rehabilitation-centre_18832/ | script shell, no text | Gabriella |

## Organisations (slice order)

| # | Organisation | Status | Searches | People | Main source |
|---|---|---|---|---|---|
| 1 | Emusoi Centre | found | 0 | 3 | own July 2026 letter (Management Committee) |
| 2 | Giving Smiles e.V. | found | 0 | 7 | own transparency page, Impressum, 2024 report |
| 3 | Kafika House | found | 1 | 10 | own Fund page (board) and March 2026 update |
| 4 | Arusha Children's Trust (ACT) | partial | 1 | 2 | own contact page (roles not stated) |
| 5 | Faraja Diaconic Centre, Sanya Juu | found | 1 | 2 | ELCT Northern Diocese directory (parent body) |
| 6 | Mkombozi Centre for Street Children | not_found | 1 | 0 | none; possible closure |
| 7 | Gabriella Children's Rehabilitation Centre | found | 1 | 1 | Segal Family Foundation partner page (funder) |
| 8 | Kilimanjaro Mission of Hope and Outreach | found | 1 | 10 | own site and FY2024 Form 990 |
| 9 | Foerderverein URRC e.V. | found | 0 | 4 | own Verein page and Impressum |
| 10 | Kesho | found | 0 | 3 | FY2025 Form 990 |
| 11 | Capital International (Isle of Man) | found | 0 | 7 | own About page |
| 12 | Concordia Lutheran Ministries Foundation | found | 0 | 2 | FYE June 2025 Form 990 |
| 13 | Friends of Amani US Inc | found | 0 | 10 | FY2025 Form 990 and Amani team page |
| 14 | Grand Circle Foundation Inc | found | 0 | 5 | FY2024 Form 990 |
| 15 | Hidden With Christ Ministries | found | 0 | 5 | own staff page |
| 16 | Imaniworld | not_found | 1 | 0 | none; site unreachable |
| 17 | Kilimanjaro Childrens Fund | found | 0 | 3 | FY2025 Form 990 (and own letter) |
| 18 | Koch Foundation Inc | found | 0 | 11 | own Welcome page and FYE March 2025 990-PF |
| 19 | Love for the Least | found | 0 | 2 | own governance and support pages |
| 20 | One Heart Source | found | 1 | 1 | FY2021 Form 990 and GuideStar |
| 21 | One Kind Act | found | 0 | 6 | own trustees page |
| 22 | TerraWatu | found | 0 | 12 | own leadership page and impact report |
| 23 | TrueToTanzania | found | 0 | 6 | own site and FY2025 990-PF |
| 24 | Uboratz Inc (UBORA) | found | 1 | 6 | own blog and FY2024 Form 990 |

## For a person to check

- **Person filter:** `contact_lib.is_name` refuses two real people because their given names are a weekday and a month: 'Sunday Joseph' (Hidden With Christ Ministries, Project Coordinator) and 'Dr. April Linton' (Terrawatu, Board Member). The builder is likely to drop them unless they are added by hand or the filter is changed.
- **Decision flag:** Emusoi's Management Committee members lead the centre since the founder-director's death, but 'Management Committee' is not in `contact_lib.DECISION`.
- **Currency:** Emusoi's committee is described as transitional; Faraja's diocese directory is undated; Gabriella's executive director is named in a 2024 item; One Heart Source's last full filing is FY2021; KMHO's About page carries a 2020 copyright; URRC e.V. holds its AGM on 9 October 2026; Terrawatu is 'transitioning' (new Tanzania home from May 2026).
- **Routes:** KMHO's displayed phone and its tel: link differ; the Kilimanjaro Childrens Fund shows a Yahoo address but links to greg@kilimanjaro-children.org; Kesho's profile may carry LOHADA's routes; Imaniworld shows two different tax IDs.
- **Not reached by this wave:** Imaniworld's register certificate (retry when the host answers); the Siha Leadership School site (robots.txt disallows; browser pass); Mkombozi's status (possible closure).
