# Hook research coverage: slice hooks_b (2026-09-25)

Brief: `runtime/hooks/hooks_b/prompt.md`. Leads: `runtime/hooks/hooks_b/leads.json` (7 organisations, 7 contacts).
Output: `data/raw/hook-research/hooks_b_2026-09-25.jsonl` (7 lines, one per organisation).

## Summary

| Measure | Result |
| --- | --- |
| Organisations finished | 7 of 7 (status: 5 found, 2 partial) |
| Hooks written | 6 (all moderate; none strong) |
| Role checks | 6 confirmed, 0 changed, 0 not_found, 1 unreachable |
| WebSearch | 1 of 5 used (Stereo Hotel, which has no website of its own) |
| WebFetch | 1 call (zafstours.com, which read_page.py could not read because the page is built by script; WebFetch also got only the page shell) |

## Queries

1. Q1/5 `"Stereo Hotel" Arusha` (Stereo Hotel). Results: Instagram, Facebook, three TripAdvisor pages, Wanderlog, vacationcottage.com, almosafer.com, closesthotel.com. Only the Wanderlog listing was read. The Facebook handle pointed to the hotel's domain `stereohotel.co.tz`, which does not resolve. Nothing from the result snippets was recorded.

Q2/5 to Q5/5 were not used. Every other organisation's own pages, or a known URL, gave usable facts.

## Pages read, by organisation

All pages were read with `scripts/contacts/read_page.py` unless noted otherwise. robots.txt was read and allowed the page on every site, except newsafarihotel.com (no robots.txt; it answered 4xx) and stereohotel.co.tz (the domain does not resolve).

1. **Maternity Africa Arusha**. Hook: education programme (Kivulini Maternity Centre trains and mentors its service-delivery staff).
   - https://maternityafrica.org/ (contact source)
   - https://maternityafrica.org/who-we-are/
   - https://maternityafrica.org/what-we-do/
   - https://maternityafrica.org/reports-and-policies/
   - https://maternityafrica.org/kivulini/
   - https://maternityafrica.org/groundbreaking-for-phaedra-maternity-health-centre-in-chamwino-dodoma/
2. **Graceland Hotel**. Hook: locality (Father Babu Road, Arusha).
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf (contact source). read_page.py fetched it (HTTP 200, 449 KB) but does not extract PDF text, so the text was extracted locally with pypdf from that cached copy (2 pages). This copy was also used for New Safari Hotel and Stereo Hotel.
   - https://gracelandhotel.co.tz
   - https://gracelandhotel.co.tz/about/
   - https://gracelandhotel.co.tz/facilities/
3. **New Safari Hotel**. Hook: locality (a historic landmark in the heart of Arusha).
   - ACHPR hotel list PDF (contact source; the cached copy above)
   - https://newsafarihotel.com (a one-page site; its menu items are anchors on the same page)
4. **Nyange Adventures Ltd.** Hook: growth (the company says it is expanding its team).
   - https://nyangeadventures.com/our-history/ (contact source)
   - https://nyangeadventures.com/meet-our-team/
   - https://nyangeadventures.com/contact/
5. **RiverStone Africa Safaris**. Hook: locality (mainly based in Arusha town).
   - https://www.riverstonesafaris.co.tz/about/ (contact source)
   - https://www.riverstonesafaris.co.tz/
6. **Stereo Hotel**. No hook.
   - ACHPR hotel list PDF (contact source; the cached copy above)
   - https://www.stereohotel.co.tz and https://stereohotel.co.tz: DNS failure (getaddrinfo failed), not readable
   - https://wanderlog.com/place/details/13314850/stereo-hotel-arusha (a third-party travel listing)
7. **ZAFS Tours**. Hook: locality (the page's own meta description: "run by a local team in Arusha").
   - https://zafstours.com/ (contact source). The page is built by script: read_page.py returned only the title; the served HTML has only meta tags, and the meta description was quoted from it. WebFetch also got only the shell.
   - https://tatotz.org/portfolio/zafs-tours/ (TATO member profile; the URL came from the repository's TATO list, so no search was needed)

## Blocked or unreadable sources

- ACHPR hotel list PDF: not blocked. read_page.py cannot extract PDF text, so the text was extracted from its cached copy with pypdf, and no second request was made. In the extracted text the table cells run together, so the excerpts show no space between cells. The list also gives phone numbers and personal email addresses; none were recorded.
- stereohotel.co.tz (with and without www): the domain does not resolve (DNS failure).
- zafstours.com: the page is built by script, so its visible content could not be read with read_page.py or WebFetch. The contact's role could not be rechecked (unreachable). Research agents do not use the shared browser pane, so this is left for the coordinator's browser.
- Not read: Instagram, Facebook and TripAdvisor results from Q1 (social pages behind login walls, and review sites).
- No 403, 429, captcha or login wall was met.

## Organisations without a hook, and why

- **Stereo Hotel**: it has no website of its own (none on record, and the domain named in its Facebook handle does not resolve). The only facts are from a third-party travel listing (a machine-written description, with reviews going back to 2018) and the ACHPR's 2023 list. Nothing published by the hotel gives a location, workforce or programme fact to base a hook on.

## Organisations not finished

None.

## For a person to check

- **Maternity Africa**: the site footer gives the Country Director as `doreenmoshi@maternityafrica.org`, but the Who We Are page lists Michael Hynds as Country Director beside plans dated 2025. Confirm who is Country Director now.
- **ACHPR-sourced contacts (Graceland, New Safari, Stereo)**: "confirmed" means only that the static September 2023 list still names them. It is not evidence of a current role, and the list gives no job titles. George Joseph Kingazi is also the contact for Senator Hotel on the same list, so he may be a booking agent rather than Graceland staff.
- **New Safari Hotel**: owned by the Evangelical Lutheran Church in Tanzania (ELCT), so a staff benefit may be decided by the Church rather than the hotel.
- **Nyange Adventures**: its only office is in Moshi (Bustani Alley), not Arusha. Check that a campus suits its staff; Boma Ng'ombe is the nearest to Moshi. The team page gives Praise Nyange as "Founder & Director".
- **RiverStone**: fix the record. The website is missing, and the locality field holds an email address. The company's name is "RiverStone African Safaris Ltd", not "RiverStone Africa Safaris", so correct the purpose sentence.
- **Stereo Hotel**: confirm that the hotel still operates, and who manages it.
- **ZAFS Tours**: recheck Burhanuddin (Senior Specialist, an enquiry contact) with the browser, and consider asking for the owner. The location is unclear: the meta description says Arusha, while TATO and the record say Moshi.
