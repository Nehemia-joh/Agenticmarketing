# hooks_a coverage, 23 September 2026

Output: `data/raw/hook-research/hooks_a_2026-09-23.jsonl`. There are 15 lines, one for each of the 15 organisations in `runtime/hooks/hooks_a/leads.json`.

- **Hooks:** 12 written (5 strong, 7 moderate); 3 null.
- **Role checks:** 22 contact messages checked: 20 confirmed, 0 changed, 0 not_found, 2 unreachable.
- **Searches:** 3 of 10 used. No search was refused.
- **Status:** 11 found, 4 partial (Hanspaul, Wild Ways, Faune & Flore, Kirengo).

## Searches

| # | Query | Organisation | Why a search was needed | What it led to |
|---|---|---|---|---|
| Q1/10 | `"Hanspaul Group" Arusha` | Hanspaul Group | Its own site answered HTTP 403 | AUTO corporate-partner page (read); ATTA page (404); LinkedIn (robots.txt disallows; not read) |
| Q2/10 | `"Wild Ways Tanzania" Arusha` | Wild Ways Tanzania Adventure | Its own site answered HTTP 403 | TATO member page and SafariBookings profile (both read) |
| Q3/10 | `"Hanspaul" Arusha employees workers factory` | Hanspaul Group | The AUTO page covered one subsidiary only, with no size or programme | May 2015 article reprinted on expogr.com (read) |

No other organisation needed a search, because its own pages gave usable facts. Search-result snippets were not recorded.

## Pages read, by organisation

All pages were read with `scripts/contacts/read_page.py`. WebFetch was not used.

Pages marked *(cache hh:mm)* were served from the reader's cache. Those copies were fetched earlier on 23 September 2026 by the reader, and the time is when. The role checks on those pages therefore reflect the page as it was that morning.

1. **Hanspaul Group**
   - https://hanspaul.co.tz/: 403, blocked
   - https://www.hanspaul.co.tz: 403, blocked *(cache 02:32)*
   - https://atta.travel/organisation/hanspaul-group.html: 404
   - https://ugandatouroperators.org/corporate_partners/hanspaul-group/: 200
   - https://tz.linkedin.com/company/hanspaul-group: robots.txt disallows; not read
   - https://expogr.com/tanzania/evexpo/detail_news.php?newsid=1225&pageid=2: 200 (robots.txt 4xx, so no rules)
2. **MS Training Centre for Development Cooperation**
   - https://mstcdc.or.tz/about/team *(cache 02:35)*
   - https://mstcdc.or.tz/about *(cache 02:35)*
   - https://mstcdc.or.tz/about/our-history
   - https://mstcdc.or.tz/jobs (one consultancy post; not used)
3. **African Big Cats Safaris**
   - https://africanbigcatssafaris.com/company-profile/
   - https://africanbigcatssafaris.com/
4. **Augustine's Adventure Africa (AA Africa)**
   - https://aaafrica.net/about-us/about-usmessage/
   - https://aaafrica.net/about-us/our-staff/ *(cache 02:26)*
   - https://aaafrica.net/about-us/ *(cache 02:26)*
5. **CORTO SAFARIS Ltd**
   - https://cortosafaris.com/agence-tanzanie/ (the first attempt failed a DNS lookup; the retry succeeded)
6. **Earthlife Expeditions Company Limited**
   - https://www.earthlifeexpeditions.com/about-us/our-team/ *(cache 02:30)*
   - https://www.earthlifeexpeditions.com/about-us/ *(cache 02:30)*
7. **Faune & Flore Ltd** (robots.txt 4xx, so no rules)
   - https://www.faune-flore.com/pages/about_us.html *(cache 02:31)*
   - https://www.faune-flore.com/index.html
8. **I Dream of Africa Ltd**
   - https://www.idreamofafrica.com/ (the fetcher's first attempt failed a DNS lookup; its retry succeeded)
   - https://www.idreamofafrica.com/about-us *(cache 02:32)*
9. **Kirengo Tours And Safaris Limited**
   - https://www.kirengotours.com/
   - https://www.kirengotours.com/acerca-de-nosotros/
   - https://www.kirengotours.com/contacta-con-nosotros/ *(cache 02:33)*
10. **Matembezi Company Ltd**
    - https://matembezi.co.tz/about-us/ *(cache 02:34)*
11. **Rivertrees Country Inn**
    - https://rivertrees.com/ *(cache 02:37)*
    - https://rivertrees.com/history/ *(cache 02:37)*
    - https://rivertrees.com/reaching-us/
12. **Safari.Africa**
    - https://www.safari.africa/our-story *(cache 02:37)*
13. **Snow Africa Adventures**
    - https://snowafricaadventure.com/about-us/ *(cache 02:38)*
14. **Wild Ways Tanzania Adventure**
    - https://wildwaystanzania.com/about-us/: 403, blocked
    - https://wildwaystanzania.com/: 403, blocked
    - https://tatotz.org/portfolio/wild-ways-tanzania-adventure/: 200, page dated 12 June 2025
    - https://www.safaribookings.com/p3873: 200
15. **Wonders Of Creation Tours And Safaris Co Ltd**
    - https://www.wonderfultours.com/about/team *(cache 02:40)*
    - https://www.wonderfultours.com/about/volunteering
    - https://www.wonderfultours.com/about/about-us
    - https://www.wonderfultours.com/about/community

## Blocked or unreadable sources

- **hanspaul.co.tz and www.hanspaul.co.tz:** HTTP 403 on the home page. This was recorded and not worked around, and no other page on that site was tried. As a result, Kamaljit Singh Hanspaul's role check is `unreachable`.
- **wildwaystanzania.com:** HTTP 403 on /about-us/ (the contact's source page) and on the home page. This was recorded and not worked around. As a result, Joan Mariki's role check is `unreachable`.
- **atta.travel Hanspaul member page:** HTTP 404.
- **tz.linkedin.com/company/hanspaul-group:** robots.txt disallows it, so it was not read.
- **Transient DNS failures:** cortosafaris.com and www.idreamofafrica.com each failed a DNS lookup once, and both read successfully on retry. These were network faults, not blocks.
- **robots.txt answered 4xx (no rules):** hanspaul.co.tz, wildwaystanzania.com, faune-flore.com and expogr.com. No robots.txt was unreachable.

## Organisations without a hook, and why

- **Rivertrees Country Inn:** existing relationship (renewal of the 2025 staff education partnership). The hook is null by instruction and only the brief was recorded.
- **Faune & Flore Ltd:** the site describes an outfitter run by its two founders. It publishes no staff numbers, team, staff-welfare, education or community programme, so there is no fact to support a hook. The site is old (Flash content) and undated.
- **Kirengo Tours And Safaris Limited:** the Spanish-language site gives no team size, staff structure or programme. It says only that the company works "mano a mano con nuestro equipo local en Tanzania y Kenya" (brief fact 2), which was judged too weak to use.

## Organisations not finished

None. All 15 organisations have a line.

## Points for a person to check

- **Hanspaul Group:**
  - The contact's current title is unconfirmed, because the site is blocked. A 2015 article calls Kamaljit Hanspaul "Group Chief Executive", against "Group Chairman" on record.
  - The hook rests on an undated AUTO profile of one subsidiary (Hanspaul Automechs). Its excerpt joins two passages of that page with [...].
- **Wild Ways Tanzania Adventure:**
  - The role check was impossible because the site is blocked.
  - The hook rests on the SafariBookings size field "5-10 employees (Founded in 2011)", which the company supplied and which may be out of date.
- **I Dream of Africa:** the hook's community projects are described on the site as the founder's aim ("dream"), not as a running programme.
- **Faune & Flore:** confirm that the business is still active.
- **Excerpts trimmed with [...]:** these leave out family, origin or education details. They are:
  - the AA Africa contacts (Eva Minja, Augustine Minja);
  - the Faune & Flore founders fact and contact;
  - the Corto and Matembezi contacts.

  Each segment is verbatim.
- **MS TCDC:** the team page lists a Head of Human Resource who is not a contact on record and may be the right person for a staff benefit.
- **Privacy:** no staff emails, phone numbers, biographies, family details, social profiles or information about children were recorded.
