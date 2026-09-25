# Coverage log: browser sites A (2026-09-26)

- **Slice:** `runtime/contacts/slices/browser_sites_a.json`. It holds 1 website that a plain crawler could not read (script-built pages), covering 1 welfare organisation. robots.txt allows it.
- **Method:** the built-in browser only, in the agent's own tab. The agent opened the start URL, ran the prompt's capture script and read up to 8,000 characters of page text. On this site the page-text tool read the whole `<body>`, footer included. It then opened the capture's other links one at a time: 4 pages in all, within the limit of 5. No WebSearch or WebFetch calls were made (`searches_used: 0`).
- **Output:** 1 record appended to `data/raw/contact-research/browser_sites_a_2026-09-23.jsonl`. The file held 28 records from the earlier passes and now holds 29. The organisation was not in it before.
- **Coverage file name:** `browser_sites_a_coverage.md` already exists from an earlier pass, so this log is written beside it under a dated name.
- **Scratch:** `runtime/contacts/agents/browser_sites_a/`. This pass added the record file (`record_dyslexiatanzania.json`) and a dated copy of the append-and-validate helper (`append_record_2026-09-26.py`). The copy differs from the original only in the access date it checks.
- **Accessed:** 2026-09-26.

## Summary

| Measure | Count |
|---|---|
| Sites in slice | 1 (1 organisation) |
| Sites read, with the organisation's own content | 1 (Dyslexia Tanzania) |
| Sites behind a bot check, lapsed, or not reachable | 0 |
| Records: found / partial / not_found / blocked | 1 / 0 / 0 / 0 |
| Identity confirmed / uncertain | 1 / 0 |
| Emails | 1 general (info@dyslexiatanzania.org) |
| Phone numbers | 1 Tanzanian mobile (+255 688 535 848) |
| Postal addresses | 0 (none published) |
| Physical addresses | 1 (Tanzanite street, House Number 13, nearby Canossa Primary, Arusha Tanzania) |
| Socials | 2 (Facebook, Instagram) |
| People | 3 (Founder, Co-Founder, Clinical Psychiatrist) |

**Status rules** (as in the earlier passes). `found`: identity confirmed, at least one email or phone, and a named leader or decision-maker read on the organisation's own page. `partial`: new routes or people, but not both. `not_found`: the site was read but publishes nothing usable. `blocked`: a bot check, a lapsed, parked or unrelated domain, or a site with no content.

## Site by site

| # | Site (final URL) | Organisation | Pages read | Outcome |
|---|---|---|---|---|
| 1 | dyslexiatanzania.org (https://www.dyslexiatanzania.org/) | DYSLEXIA TANZANIA (welfare, ORG_6f5b26e68d18c402) | home, /aboutus, /contactus, /about.html | **found**. Every page rendered in the browser, with no bot check or cookie banner. The About Us page's 'Our Team' cards name Caudence Ayoti (Founder), Johns Rashidi (Co-Founder) and Pascal Kang'iria (Clinical Psychiatrist); the list was still three after a wait. The Contact page and the footer of every page give info@dyslexiatanzania.org, +255 688 535 848 (the footer prints +255688535848) and Tanzanite Street, House Number 13, Arusha. The home page FAQ adds 'nearby Canossa Primary'. The footer links the organisation's Facebook (profile.php?id=100090960036619) and Instagram (dyslexia_tanzania). /about.html, the slider buttons' link, loads the app shell but renders nothing: a leftover template route. |

## What this pass adds to wave 6

- Wave 6 (search) read this site's routes and founder from its public JS bundle, not from a rendered page, and could not read the team cards. This pass confirms the inbox, mobile, Facebook, Instagram and founder on rendered pages.
- **New person:** Johns Rashidi, Co-Founder. Wave 6 noted a second co-founder named only on Wikipedia and did not record them. Whether that is Johns Rashidi was not checked (no searches in this pass).
- **New person:** Pascal Kang'iria, Clinical Psychiatrist. His title is clinical, not a leadership role. He is recorded, following the rule that a browser reader's people are kept with the role the source gives, because the organisation lists him in its three-person team.
- **New:** the physical address, which wave 6 withheld (see check 1 below).
- Wave 6 filed the organisation under an older ID (ORG_a9df8236fc369230). This record uses the slice's current ID.

## Blocks and what was not done

- **Blocks:** none. No bot check, login, certificate warning or cookie banner appeared.
- **Placeholders not recorded:**
  - a hidden mobile-menu link `tel:+8898006802`, with no visible text (a theme placeholder number)
  - bare `https://twitter.com` and `https://linkedin.com` icons on each team card
  - the slider buttons' `about.html` link, which renders an empty page
- **Also not recorded:**
  - a YouTube video pop-up (a single video, not a channel)
  - the web designer's credit ('Designed by Essence Creative')
  - the team cards' Facebook link (`https://www.facebook.com/people/Dyslexia-Tanzania/100090960036619/`), which is the same page as the footer's
- **Social URLs:** recorded without their share-tracking parameters (`mibextid`, `igshid`).
- **Forms:** the Contact page's 'Send message' form and the donation buttons were not used.
- **Browser tabs:** the agent worked only in its own tab (opened with `tabs_create`) and closed it at the end. It did not touch the other browser agents' tabs.

## For a person to check

1. **Address:** the site gives 'Tanzanite street, House Number 13' (Contact page, footer and home page FAQ) as the organisation's location. It is recorded as published. Wave 6 withheld the house number in case it is a residence, and nothing on the site says either way, so confirm it is an office before using it. The FAQ's landmark ('nearby Canossa Primary') may help resolve the welfare record's 'location unresolved' flag.
2. **Pascal Kang'iria:** listed as Clinical Psychiatrist in the organisation's team. Decide whether he is a decision-maker or should rank below the founders only as a programme contact.
3. **Johns Rashidi:** check whether he is the second co-founder that Wikipedia names (noted, but not recorded, in wave 6).
4. **Activity:** the home page lists a Talent Show Dinner (22 August) and a Dyslexia Awareness Run (21 August) without years, and an 'Annual - 2023 Impact Report'. Nothing suggests closure, but the site gives no dated activity after 2023.
