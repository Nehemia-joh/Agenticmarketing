# Coverage log: wave10_master_employers_d (2026-10-02)

Slice: runtime/contacts/slices/wave10_master_employers_d.json (40 master organisations). Records: data/raw/contact-research/search_wave10_master_employers_d_2026-10-02.jsonl.

Result: 40 of 40 organisations reached. 7 found, 31 partial, 2 not_found, 0 blocked as a whole. 37 of 38 searches used (Q38 left unused). No search was refused by a session cap.

People: 8 recorded for 7 organisations (Amazing Tanzania 2, Macho Halisi, Ndoto Kubwa, Mrembo, K&K, Kudu, Dorobo). One is linked to a work email and phone by the same source (Dorobo, via a partner listing). Two names are incomplete (Andrew, Karine, first names only); the surname of Elizabeth Ayo differs in a news result and is flagged.

## Searches

| No. | Query | Outcome |
|---|---|---|
| Q1/38 | "Sameer Parts Limited" Arusha | Own site found (sameerpartsltd.com); no people |
| Q2/38 | "SIBROS (T) LIMITED" Arusha | Own site found (sibros.co.tz); staff only on a people-search site (not used) |
| Q3/38 | "Afrisafaris Tanzania" Arusha | Website and Facebook link; site blocked by TLS |
| Q4/38 | "Ndoto Kubwa Tours and Safaris" Arusha | Confirms TATO profile; site blocked by TLS |
| Q5/38 | "Kilpath African Safaris" Arusha | Own site found (kilpathafricansafaris.com); no people |
| Q6/38 | "African Safari Travel" Arusha Muriet | africansafari.travel, Spanish phone; identity uncertain |
| Q7/38 | "Tanzania a la Carte Safaris" Arusha | tanzaniaalacarte.com; no people |
| Q8/38 | "Kilaweni" Arusha safari | Review pages and a Facebook link only; site refuses connections |
| Q9/38 | "Kudu Safaris" Arusha Tanzania | Led to kudusafaris.net (Rhino Safaris group site): manager named |
| Q10/38 | "Maasai Magic Safari" Arusha | Domain shows gambling content; nothing used |
| Q11/38 | "House of Gems" Tanzania Arusha "Beautiful African Gemstones" | houseofgems.tz; no named owner |
| Q12/38 | "MajorityMart Suppliers" Arusha | majoritysuppliers.com; no people |
| Q13/38 | "NSK Hospital" Arusha Tanzania | nskhospitals.co.tz; no leaders on pages read |
| Q14/38 | "Sadio Events" Arusha | sadioevents.co.tz; no people |
| Q15/38 | "Tanzania Federation of Tourism Service Providers" | TATO profile only; site has an expired certificate |
| Q16/38 | "Karine & Kitanga Safaris" Arusha | kandksafaris.com; founders by first name |
| Q17/38 | "Vehicle Pharmacy" Arusha Tanzania | TATO profile only; no website |
| Q18/38 | "Mkizughuno Company Limited" Arusha | TATO profile only; no website |
| Q19/38 | "Artisan Coffee and Patissier" Arusha | TATO profile only; artisan.co.tz has a self-signed certificate |
| Q20/38 | "Marangu forex bureau" Arusha | mfb.co.tz; no people |
| Q21/38 | "Maradawa Tours" Arusha | TATO profile only; site has an expired certificate |
| Q22/38 | "Safarini Africa" Arusha | Review pages; safarini.com disallowed by robots.txt |
| Q23/38 | "Papagei Tours and Safaris" founder Arusha | Founder described, not named |
| Q24/38 | "Triumph Travel & Film Safaris" Arusha managing director | No managing director named |
| Q25/38 | "Jaribu Africa Adventures" Arusha director | Only a people-search site named a director (not used) |
| Q26/38 | "Popote Africa Adventures" Moshi owner | Only review pages named an owner (not used) |
| Q27/38 | "Ang'ata Camps" Tanzania owner managing director | Names with no fetchable source (annual report PDF unreadable); not recorded |
| Q28/38 | "Eco-Africa Climbing" Moshi Kilimanjaro founder | Only profile and review pages named an owner (not used) |
| Q29/38 | "Tanzania Classic Tours" Arusha founder | Only reviews gave a first name (not used) |
| Q30/38 | "Karibu Africa Safaris" Arusha managing director | No managing director named |
| Q31/38 | "Firstpace African Travel" Arusha | Nothing beyond the site and TATO |
| Q32/38 | "Dorobo Safaris" Arusha owner | Led to Serengeti Watch listing: primary contact with email and phone |
| Q33/38 | "Bushtops" Orion Hotels Tanzania Arusha general manager | No manager named |
| Q34/38 | "Kananga" "Rumangabo International" Arusha | Group site; head office in Barcelona |
| Q35/38 | "African Spoonbill Tours" Moshi Tanzania CEO | Only a personal LinkedIn profile named an owner (not used) |
| Q36/38 | Kilimanjaro Porters Assistance Project partner company "Eco-Africa Climbing" | Nothing new |
| Q37/38 | Tanzania Association of Women Tour Operators TAWTO chairperson "Mrembo Safaris" | News gave a different surname for the founder; flagged |
| Q38/38 | not used | |

## Blocks and unreadable sites (none worked around)

- TLS failure, site not read: afrisafaristanzania.com (both hosts, local issuer certificate), ndotokubwatours.com (SSL EOF), maradawa.com (certificate expired), tanzaniaporters.org (certificate expired), artisan.co.tz (self-signed certificate).
- HTTP 429: www.bush2beach.com/our-team and /about, then the home page on a later read. Not retried.
- robots.txt disallows: safarini.com (not read; candidate for the browser pass).
- Not reachable: www.kilaweni.com (connection refused), kudusafaris.co.tz (DNS failure).
- Known source gone: maasai-magic.com/about-us/ (404); the domain's home page now shows unrelated Chinese gambling content (hijacked; nothing used).
- A PDF (angatacamps.com/downloads/ANGATA-REPORT-2015.pdf) was cut at the 2 MB fetch limit and could not be parsed.
- Third-party pages not read for people by rule: Tripadvisor, ZoomInfo, LinkedIn, news. Facebook pages recorded only as URLs.

## Segment and fit flags

Records that do not look like safari or tour operators: Sameer Parts, SIBROS, Vehicle Pharmacy, MajorityMart Suppliers, NSK Hospitals, Mkizughuno (pest control), Artisan Coffee, Marangu forex bureau, Beautiful African Gemstones; the Tanzania Federation of Tourism Service Providers is a body, not a company. Outside the Arusha area: Eco-Africa Climbing and Popote Africa Adventures (Moshi), Karatu-based Amazing Tanzania and Macho Halisi. Kananga and andBeyond are parts of larger groups with head offices abroad. African Safari Travel looks like a European agent (identity uncertain).

## Organisations not reached

None. Organisations with nothing found for a decision-maker after reading their own pages: all 31 partial records, Kilaweni and Maasai Magic.
