# Browser sites B: coverage log (2026-09-26 pass)

Slice: `runtime/contacts/slices/browser_sites_b.json` (1 site, 1 organisation; pages built by script, robots.txt
allows it). Purpose: the wave-7 search agent read this site's contacts and staff from the public JSON its pages load
(`/api/public/site-pages`, `/api/public/staff`). This pass confirms them on rendered pages a person can open, so every
fact has a page URL. Method: the built-in browser (own tab), one page at a time, at most 5 pages per site; the brief's
capture script and page-text read on every page. Where the 8,000-character page text stopped short, the footer (home
page) and the staff cards (About page) were read from the same page with a second script call. No forms, logins,
CAPTCHAs or cookie acceptance (no banner appeared); no web searches. Accessed 2026-09-26. Output: 1 line appended to
`data/raw/contact-research/browser_sites_b_2026-09-23.jsonl` (the earlier passes' 28 lines are unchanged; their logs are
`browser_sites_b_coverage.md` and `browser_sites_b_2026-09-25_coverage.md`).

| # | Site | Organisation(s) | Outcome | Pages read | What was found / why blocked |
|---|------|-----------------|---------|------------|------------------------------|
| 1 | nafgemtanzania.or.tz | NAFGEM Tanzania (welfare ORG_2c99c49e7035e66f) | found | 3 (home, contact, about) | mail@ and info@nafgemtanzania.or.tz; landline +255 27 2750056; mobiles +255 754 801 784 (also the WhatsApp chat number) and +255 611 502 410 (the 24/7 hotline for reporting a case); P.O. Box 6413 Moshi; head office Shanty Town, Bustani Alley, Moshi; Facebook, Instagram and X (Twitter). People, from the About page's staff section, all in Moshi: Executive Director, Director of Programs, Project Manager, Finance Manager, MERL Manager, Human Resource Officer, Office Administrator, Social Welfare Officer and Procurement Officer. No card gives an email or phone. |

## Summary

- Sites: 1 (1 organisation). Read: 1 (found, identity confirmed). Blocked: none. The site rendered normally in the
  browser, with no challenge, login or banner.
- Found: 2 emails, 3 phones, 1 postal and 1 physical address, 3 social pages and 9 named people. All people are
  `medium` risk; none has a personal email or any personal route.
- Pages read: 3 (the limit is 5): `/`, `/contact`, `/about`. The staff list is on the About page; the site has no
  separate team, board or leadership page. Not opened:
  - careers ('Join our team', a jobs page), whistleblowing and Learn About FGM. These were in the capture's links but are
    not contact or leadership pages.
  - the footer's other links (press kit, impact, events, programmes, stories, resources, supporters). They were not in
    the capture's contact or leadership links.
- Compared with the wave-7 search record, which was read from the site's public JSON:
  - Every route matches. The Contact page prints the landline as +255 27 2750056 (the record's +255 27 275 0056 is the
    same number). The About page adds 'Bustani Alley' to the Shanty Town head-office address.
  - All six of its leads are on the rendered About page, with the same names and roles.
  - Three staff are new to the record: Edita Moses Lupenza (Finance Manager), Yona Godwin Ahia (MERL Manager) and
    Rehema Mseven Mboya (Procurement Officer). The search record left out finance, procurement and M&E staff. They are
    kept here under the keep-every-lead rule; the pipeline's role rules decide which count as decision makers.
  - The About page says the Board of Directors has 7 members, but no page read names them.
- For a person to check:
  - +255 611 502 410 is the 24/7 hotline for reporting FGM or GBV cases, so do not use it for partnership outreach.
    Use the inboxes, the landline or +255 754 801 784 instead.
  - The WhatsApp chat button (+255 754 801 784) pre-fills a message to the Executive Director. The site does not give
    that number for him by name, so it is kept as the organisation's number.
  - The slice and the current contact profile use organisation_id ORG_2c99c49e7035e66f. The wave-7 search record for
    the same organisation carries ORG_e061c060529cab8c.
  - The About page lists a Siha office (Lekrimuni, Siha, Kilimanjaro) as well as the Moshi head office. It may be the
    office nearest the Boma Ng'ombe campus.
