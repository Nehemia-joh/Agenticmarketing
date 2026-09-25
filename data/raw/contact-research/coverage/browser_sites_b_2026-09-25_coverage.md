# Browser sites B: coverage log (2026-09-25 pass)

Slice: `runtime/contacts/slices/browser_sites_b.json` (2 sites, 2 organisations; pages built by script, robots.txt
allows them). Method: the built-in browser (own tab), one page at a time, at most 5 pages per site; the brief's
capture script and page-text read on every page. No forms, logins, CAPTCHAs or cookie acceptance; no web searches.
Accessed 2026-09-25. Output: 2 lines appended to `data/raw/contact-research/browser_sites_b_2026-09-23.jsonl`
(the earlier pass's 26 lines are unchanged; its log is `browser_sites_b_coverage.md`).

| # | Site | Organisation(s) | Outcome | Pages read | What was found / why blocked |
|---|------|-----------------|---------|------------|------------------------------|
| 1 | vehiclepharmacy.com | Vehicle Pharmacy (master O3974c6961fd9) | found | 3 (home, about, contact) | info@vehiclepharmacy.com; +255 783 827 125 (trade counter, calls and WhatsApp); P.O BOX 10542 Arusha; Facebook, Instagram. No named people: no team or leadership page, and the only names are three customer testimonials (not recorded). No street address. LinkedIn and Twitter icons are bare placeholders (not recorded). An auto spare parts supplier, not a safari operator. |
| 2 | osotuwa.org | OSOTUWA FOUNDATION (welfare ORG_625ffe9021a73962) | found | 4 (home, about us, our board, contact) | osotuwa@gmail.com (the organisation's own Gmail address); Instagram @osotuwa. People: Isaya Oleporuo (Founder and President; Chairman of the Board), Patricia Allenby (Secretary), Steven Prue (board member), Nguvu Lukumay (Program Director, Arusha). No phone or address. The Facebook icon is a Facebook search link, not a page (not recorded). A US 501(c)(3); the programme is in Eluai, Tanzania, led from Arusha. |

## Summary

- Sites: 2 (2 organisations). Read: 2 (both found). Blocked: none. osotuwa.org, which answered the crawler with
  HTTP 429, loaded normally in the browser.
- Found: 2 emails, 1 phone, 1 postal address, 3 social pages and 4 named people (all `medium`; none with a
  personal email). Records: 2 found, identity confirmed for both.
- Pages read: 7 (never more than 5 per site). Not opened: Vehicle Pharmacy's products, brands, services and quote
  pages (not contact or leadership pages); OSOTUWA's How We Began, Stories, News, Sponsor and Support Us pages (not
  in the capture's contact or leadership links; the Stories pages are about the girls).
- New compared with the record: Steven Prue (OSOTUWA board member). The board page confirms Isaya Oleporuo and Nguvu
  Lukumay and gives Patricia Allenby's role as secretary (the Form 990 says Secretary/treasurer).
- Different kind or place than the record suggests: Vehicle Pharmacy is an auto spare parts supplier, although its
  record's segment is Safari / tour operator. OSOTUWA Foundation is a US-registered non-profit with a mostly US-based
  board; its Arusha contact is the Program Director.
- For a person to check: the record's Facebook link for OSOTUWA is the same Facebook search URL, not a page. Vehicle
  Pharmacy's record also holds +255715827125, +255736827125 and a Gmail address that the site does not show.
