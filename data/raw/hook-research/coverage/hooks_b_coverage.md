# Hook research coverage: slice hooks_b (2026-09-23)

Brief: `runtime/hooks/hooks_b/prompt.md`. Leads: `runtime/hooks/hooks_b/leads.json` (15 organisations, 20 contacts).
Output: `data/raw/hook-research/hooks_b_2026-09-23.jsonl` (15 lines, one per organisation).

## Summary

| Measure | Result |
| --- | --- |
| Organisations finished | 15 of 15 (status: 14 found, 1 partial) |
| Hooks written | 15 (7 strong, 8 moderate) |
| Role checks | 18 confirmed, 1 changed, 0 not_found, 1 unreachable |
| WebSearch | 0 of 10 used (every organisation's own pages gave usable facts) |
| WebFetch | 1 call (NM-AIST prospectus PDF, which read_page.py could not parse) |

## Queries

None. No WebSearch was run (0/10).

## Pages read, by organisation

All pages were read with `scripts/contacts/read_page.py` (robots.txt read and allowing on every site), unless noted otherwise.

1. **Tanzania Wildlife Research Institute (TAWIRI)**: hook = locality (HQ at Njiro, Arusha)
   - https://www.tawiri.or.tz/corporate_service/ (contact source)
   - https://www.tawiri.or.tz/jet-popup/director-general-biography/ (contact source)
   - https://tawiri.or.tz/ (redirects to https://www.tawiri.or.tz/)
   - https://www.tawiri.or.tz/about-tawiri/
   - https://www.tawiri.or.tz/management-and-organization-structure/
   - https://www.tawiri.or.tz/njiro-wildlife-researh-center/
   - https://www.tawiri.or.tz/uzinduzi-rasmi-wa-matokeo-ya-kitaifa-ya-sensa-ya-wanyamapori/
2. **Nelson Mandela African Institution of Science and Technology (NM-AIST)**: hook = locality (Tengeru campus)
   - https://nm-aist.ac.tz/wp-content/uploads/2024/04/prospectus-2024.pdf (contact source)
     - read_page.py got HTTP 200 but stops at 2 MB and does not parse PDFs;
     - read through WebFetch's saved copy (6.7 MB), with text extracted locally by pypdf (pages viii and 9).
   - http://www.nm-aist.ac.tz (redirects to https://nm-aist.ac.tz/)
   - https://nm-aist.ac.tz/the-nelson-mandela-african-institution-of-science-and-technology-nm-aist/about-nm-aist/governance-and-leadership/executive-management/
   - https://nm-aist.ac.tz/the-nelson-mandela-african-institution-of-science-and-technology-nm-aist/about-nm-aist/our-history/
   - https://nm-aist.ac.tz/nm-aist-kinara-wa-maonesho-ya-nanenane-kanda-ya-kaskazini-2026/
3. **African Environments Ltd**: hook = workforce (team members with decades of service)
   - https://www.africanenvironments.com/about-us (contact source)
4. **Betheli Expeditions**: hook = education programme (engages with local schools)
   - https://betheliexpeditions.com/about/ (contact source)
5. **Dakik Expeditions LTD**: hook = workforce (guides, porters and operations staff called "the heartbeat" of the company)
   - https://dakikexpeditions.com/about-us/ (contact source)
   - https://dakikexpeditions.com/contact-us/
6. **Ecological Wilderness Adventure & Car Hire**: hook = education programme (hires locally, contributes to education and healthcare initiatives)
   - https://www.ecologicaladventure.com/team (contact source)
   - https://www.ecologicaladventure.com/about
   - https://www.ecologicaladventure.com/conservation
7. **Get together adventure**: hook = locality (team based in Arusha)
   - https://gettogetheradventures.com/about-us/ (contact source): HTTP 404
   - https://www.gettogetheradventures.com (redirects to https://gettogetheradventures.com/)
   - https://gettogetheradventures.com/about (replacement About page; used for the role check)
   - https://gettogetheradventures.com/contact
8. **Josh Dreamland Safaris**: hook = staff welfare (fair wages)
   - https://joshdreamlandsafari.com/team-member/ (contact source)
   - https://joshdreamlandsafari.com
   - https://joshdreamlandsafari.com/contact-us/
9. **Kojuu Safaris Limited**: hook = education programme (Kojuu Shares)
   - https://kojuusafaris.com/meet-kojuu-team/ (contact source)
   - https://kojuusafaris.com/about-kojuu/
   - https://kojuusafaris.com/why-choose-a-luxury-safari-with-kojuu/
10. **Meru Slopes Tours And Safaris Ltd**: hook = education programme (girls' education)
    - https://meruslopestours.com/team/ (contact source)
    - https://meruslopestours.com/about-us/
    - https://meruslopestours.com/community-development/
11. **Rupia Adventure**: hook = staff welfare (founded with a focus on customer and staff satisfaction)
    - https://rupiaadventure.com/about-us-2/ (contact source)
    - https://www.rupiaadventure.com (redirects to https://rupiaadventure.com/)
12. **Serengeti African Tours**: hook = workforce (team "more than thirty-five strong")
    - https://serengetiafricantours.com/our-team/ (contact source)
    - https://serengetiafricantours.com/contact-us/: HTTP 404 (the site's own "Plan Your Safari" link)
    - https://serengetiafricantours.com/contact/
13. **Summit 2 Sand Safaris**: hook = staff welfare (employs, empowers and rewards local guides)
    - https://www.summit2sandsafaris.com/contact-details.html (contact source)
      - read once (HTTP 200), then the local system refused to open the saved copy;
      - treated as unreadable and not used. See the next section.
    - https://www.summit2sandsafaris.com/
    - https://www.summit2sandsafaris.com/about-us.html
    - https://www.summit2sandsafaris.com/message-from-managing-director.html
    - https://www.summit2sandsafaris.com/mountain-crews-guides-cooks-porters-and-recommended-guidelines.html
14. **Wildersun Safaris Tours T Ltd**: hook = education programme ("our passion being education")
    - http://www.wildersuntanzania.com/contact-us (contact source; names only "(Ervin)" beside a phone number)
    - http://www.wildersuntanzania.com/about-us (role confirmed here)
    - http://www.wildersuntanzania.com/
15. **Zara Tours**: hook = community programme (ZARA Charity addresses education)
    - https://zaratanzaniaadventures.com/ceo-story/ (contact source)
      - redirects to https://zaratanzaniaadventures.com/meet-the-ceo/;
      - the body was gzip-compressed and was decoded locally from the cache.
    - https://zaratanzaniaadventures.com/contact-us/ (gzip, decoded locally)

## Blocked or unreadable sources

- **summit2sandsafaris.com/contact-details.html: possible compromised site.**
  - The page answered HTTP 200 and was read once. The local system (probably antivirus) then refused to open its saved copy (`OSError`), and read_page.py now reports `saved copy unreadable (OSError); not used`.
  - Following contact_lib's rule, the page was treated as unreadable and nothing from it was used; the role check is `unreachable`.
  - The site's other four pages re-open normally.
- **gettogetheradventures.com/about-us/: HTTP 404.** The site moved its About page to `/about`, which was used for the role check (recorded as `changed`).
- **serengetiafricantours.com/contact-us/: HTTP 404.** `/contact/` works.
- **NM-AIST prospectus PDF.** read_page.py truncates at 2 MB and cannot parse PDFs. It was read through one WebFetch call, whose saved copy was parsed locally. This was a tool limit, not a block.
- **zaratanzaniaadventures.com.** The server sends gzip-compressed bodies that read_page.py does not decode, so they were decompressed from the cache. This was a tool limit, not a block.
- No robots.txt disallowed or unreachable cases; no 403, 429, captcha or login walls.

## Organisations without a hook

None. Every organisation has a hook supported by one cited fact. The eight moderate hooks rest on general statements, such as location or broad community wording.

## Organisations not finished

None.

## Checks for a person

- **Summit 2 Sand Safaris** (status `partial`)
  - The contact page may carry harmful content (see above).
  - The contact on record, "David Livingstone", looks like the group's name. The Managing Director's message is headed "Message from David Livingstone" but signed "Daudi Nyabirumo, Summit 2 Sand Safaris in David Livingstone Group Co., Ltd.". Confirm the name before addressing an email.
  - The company is in Moshi, not Arusha.
- **Zara Tours**
  - Based in Moshi (Tembo Road, Pasua Area); check the fit with the nearest campus.
  - The 1,410-employee figure sits in a COVID-era CEO profile and may be dated.
- **Get together adventure**
  - Rogath Johnson is now listed as "Chief Operations Officer", and the title "Safari Operations Manager" belongs to Gilbath Sechu. Update the title and source URL.
  - The address is now Arusha Bypass Rd, Masaki Street; the locality on record is Kaloleni.
- **Wildersun Safaris**
  - The role was confirmed on the About page, not on the recorded contact page.
  - The site text is dated ("over 35 years" for a company registered in 1980), so the published staff figure (35 employees) may be old.
- **Ecological Wilderness Adventure**: the contact appears only as "Prudence T. B"; confirm the full name before addressing.
- **Serengeti African Tours**
  - Lucas David is titled "Leader", while James Michael holds "Operations Manager".
  - The office is Plot 28, Boma Road; the locality on record is Sakina.
- **Dakik Expeditions**: Zainab Dakik has no formal title on the page ("the backbone of Dakik Expeditions"; "Rawan and Zainab built the foundation").
- **Kojuu Safaris**: the address is PPF-Njiro; the locality on record is Olorien.
- **TAWIRI and NM-AIST**: both are public institutions, so a staff benefit may need to follow public-service procedures.
- **Omitted personal content.** Several sites (Rupia, Kojuu, Betheli, Wildersun, Zara, Dakik) carry personal biographies with family details. Only names and roles were recorded for contacts, and only company facts for briefs.

## Tooling notes (for the coordinator)

- **Per-site spacing.** read_page.py spaces requests to a site only within one process (`welfare_lib._wait_turn`), so separate calls to the same site are not spaced. This slice ran same-site reads through one process: a scratchpad wrapper that calls read_page.py's `main()` in a loop.
- **Unsupported formats.** read_page.py does not decode gzip bodies (seen on zaratanzaniaadventures.com) and cannot read PDFs over 2 MB. Both may be worth fixing in `scripts/contacts/`.
