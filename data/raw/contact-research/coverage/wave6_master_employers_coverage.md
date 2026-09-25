# Coverage log: wave 6, master employers (2026-09-25)

Slice: `runtime/contacts/slices/wave6_master_employers.json`: 6 company-master records, nearest first. Each already had a published route; each needed a named decision-maker, and the crawler could not read their own websites.
Search allowance: 6 WebSearch calls. 5 were used (Q1/6 to Q5/6) and Q6/6 was not needed. The session cap never refused a search.
Output: `data/raw/contact-research/search_wave6_master_employers_2026-09-23.jsonl` (6 records, one per organisation, in slice order). Scratch files are in `runtime/contacts/agents/wave6_master_employers/`. Access date: 25 September 2026.

Pages were read with `scripts/contacts/read_page.py`. It honours robots.txt Disallow rules, caches pages and paces requests. Requests to one site were kept at least 2 seconds apart. A scratch helper, `read_pdf.py`, was written to read PDFs with the same fetcher and robots check. It was used once, and robots.txt refused that PDF. Four pages came from the shared HTTP cache, where the crawl of 24 September 2026 had saved them: the TATO entry for Fantasy Adventures and the manyaluxurycamps.com home, about-us and contact-us pages. Every other page was fetched on 25 September.

## Summary

| Measure | Count |
|---|---|
| Records in slice | 6 (all master) |
| Researched (one JSONL line each) | 6 |
| found | 2 (Namiri Tours And Safaris Limited, Safari Avventura T Ltd) |
| partial | 4 (Akshar Tours and Safaris, Sunny Adventure Safaris Ltd, Sadio Events, Fantacy Adventures Limited) |
| not_found | 0 |
| blocked | 0 |
| Not reached | 0 |
| Identity uncertain | 0 |
| WebSearch calls used | 5 / 6 |
| Named people recorded | 5 in 2 organisations, all `medium`, all read on fetched pages of the organisations' own sites. One of them, Ruth of Safari Avventura, is named by first name only. |
| New routes not in the current profiles | Akshar: website akshartoursandsafaris.com, travel@ and uk@ mailboxes on it, a UK number, and X and YouTube pages. Sunny Adventure: two office lines. Namiri: its whole profile (website, info@, phone, P.O. Box, address, socials), which was empty. Fantacy: its whole profile, which was empty because wave 5 marked it uncertain. Sadio: a Facebook page seen only in search results. |

Status rules: `found` means the identity is confirmed and a named decision-maker was recorded from an allowed source. `partial` means routes or profile data were confirmed or added but no decision-maker was found.

## Searches

| # | Organisation | Query | Outcome |
|---|---|---|---|
| Q1/6 | Akshar Tours and Safaris (Oa881d17035bb) | "Akshar Tours and Safaris" Tanzania | Found the live own site akshartoursandsafaris.com, read (home, about). New mailboxes and a UK number; no leader named. Also Tripadvisor, Instagram and the TATO entry. |
| Q2/6 | Sunny Adventure Safaris Ltd (O49acf40de67b) | "Sunny Adventure Safaris" Arusha | Found the TATO entry, read: two office lines, no names. Instagram and Facebook seen in results but not read. Sunny Safaris Ltd (sunnysafaris.com, SafariBookings p117) is a different company and was not used. |
| Q3/6 | Sadio Events (O6c2976e997c2) | "Sadio Events" Tanzania | sadioevents.com timed out. The company-profile PDF on app.glueup.com was refused by robots.txt. A Facebook page appeared in results and was not read. No leader named. |
| Q4/6 | Fantacy Adventures Limited (O0320a82cdbde) | "Fantacy Adventures Limited" Tanzania | Only the TATO entry, plus differently named firms that were not used. |
| Q5/6 | Fantacy Adventures Limited (O0320a82cdbde), second search on its camp brand | "Manya Luxury Camps" Serengeti | The camp's own pages and travel listings, none naming an owner or manager. Tripadvisor answered 403. |
| Q6/6 | not used | | Namiri and Safari Avventura needed no search, because their own sites named their leaders. Each record had already been written when this search became spare, and records are appended once. |

## Organisations

| Organisation | Status | What was read | Result |
|---|---|---|---|
| Akshar Tours and Safaris | partial | TATO entry. akshartoursandsafaris.com: home and about.php; contact.php gave HTTP 409; /contact serves the home page. akshartoursandsafaris.co.tz fails TLS. | No leader named. The TATO mailbox parimalpatel@ has no published name or role, so no lead was made from it. Guest testimonials were not used. The office is in Mwanza. |
| Sunny Adventure Safaris Ltd | partial | TATO entry. The own site is disallowed by robots.txt on http and https and was not read. | New office lines +255 27 250 6760/6761. A fax number was not recorded. No leader named. |
| Sadio Events | partial | Own site (home, about, contact) and TATO entry. | An events company in Dar es Salaam, outside the area. No leader named. |
| Namiri Tours And Safaris Limited | found | TATO entry and own site over https (home, about-us, contact-us). | Shivam Barot (CEO) and Bijal Barot (CEO, co-founder). Two theme placeholder cards (Braydon Wilkerson, Kristin Watson) were dropped. The office is in Mwanza. |
| Fantacy Adventures Limited | partial | TATO entry, the manyaluxurycamps.com home, about-us and contact-us pages, and two blog pages. | Identity confirmed: TATO's entry for the company carries the camp's mailboxes and the camp's slogan. No leader named. The office is in Dar es Salaam and the camp is in Central Serengeti. |
| Safari Avventura T Ltd | found | Own site: home, /tour-operator/ (Italian), /contattaci/, /en/ and /en/about-us/. TATO entry. | Francis Emmanuel Mathayo (administrator and guide, co-founder), Gianluca Donati (manager, co-founder) and Ruth (office manager in Tanzania, first name only). Biographical and family details on the page were left out. |

## Blocks and unreadable sources

- akshartoursandsafaris.co.tz: the TLS certificate fails with a hostname mismatch, so robots.txt could not be read either. Recorded; not worked around.
- akshartoursandsafaris.com/contact.php: HTTP 409. Not retried.
- sunnyadventures.co.tz: robots.txt disallows crawling on both http and https, so it was not read. A browser agent read it on 24 September 2026 and tagged it risky.
- sadioevents.com: the connection timed out, and robots.txt could not be read.
- app.glueup.com, the Sadio company-profile PDF: robots.txt disallows the path, so it was not read.
- tripadvisor.com, the Manya Luxury Camps hotel page: HTTP 403. Not worked around.
- Facebook and Instagram pages: recorded as seen in results or site links. None was read.

## For a person to check

- **Namiri robots.txt changed.** Over https, robots.txt (read 25 September) disallows only /wp-admin/, and the pages answered 200 with no bot check. The http host's robots.txt, cached on 23 September, disallowed everything, and a browser visit on 24 September met a BitNinja CAPTCHA. Rules apply per scheme and host, so the https pages were read and the leads are not tagged risky. Confirm this reading before outreach.
- **Outside the Arusha-Kilimanjaro area.** Akshar and Namiri are in Mwanza. Sadio Events and Fantacy Adventures are in Dar es Salaam, with Fantacy's camp in the Serengeti. Check these locations before outreach.
- **Safari Avventura phone.** The Italian contact page lists "Gianluca +39 380 253 1425" by first name only, so the number was kept as a company phone and not linked to Gianluca Donati. Link it by hand if wanted.
- **Safari Avventura's legal entities.** The site's footer names UAE companies (SAFARI AVVENTURA LLC in Sharjah and SAFARI ADVENTURE LLC in Dubai). TATO lists SAFARI AVVENTURA (T) LTD, P.O. Box 14948 Arusha. The licence numbers differ: the site gives no. 005506, TATO's 2018 entry no. 125319.
- **Fantacy identity changed.** It is now confirmed, where wave 5 left it uncertain, because of the slogan match. Check this if the camp brand matters for outreach.
