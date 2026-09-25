# Hook research coverage: slice D (2026-09-25)

Leads: `runtime/hooks/hooks_d/leads.json` (6 organisations, 7 contacts).
Output: `data/raw/hook-research/hooks_d_2026-09-25.jsonl` (6 lines, one per organisation).
Pages were read with `scripts/contacts/read_page.py`. WebFetch was tried twice, only where read_page failed on a DNS or TLS error (not a block). Both attempts failed too.
Every excerpt was cut verbatim from the page text read_page printed and checked against it before writing.

## Searches (3 of 5 used)

| # | Query | Organisation | Pages read from the results |
|---|---|---|---|
| Q1/5 | `"The Arusha Hotel" Four Points by Sheraton Arusha` | ARUSHA HOTEL | hotelplanner.com listing (read); travelweekly.com listing (HTTP 403) |
| Q2/5 | `"Nnko & Smith Safaris" Usa River` | Nnko & Smith Safaris Ltd | tatotz.org member profile (read); youscholars.com listing (HTTP 404) |
| Q3/5 | `"Four Points by Sheraton Arusha" staff community donation` | ARUSHA HOTEL | none: only booking, review and Facebook pages came back, and none showed a staff or community fact |

Q4 and Q5 were not used. The brief allows a search only when an organisation's own pages give no usable fact. Kibo Palace, Premier Palace, Senator and Vianneys all published usable facts on their own sites.

## Pages read, by organisation

1. **ARUSHA HOTEL** (Four Points by Sheraton Arusha, The Arusha Hotel)
   - https://www.marriott.com/en-us/hotels/jrofp-four-points-arusha-the-arusha-hotel/overview/: HTTP 403, blocked; not retried or worked around
   - https://www.travelweekly.com/Hotels/Arusha-Tanzania/Four-Points-by-Sheraton-Arusha-Hotel-p51729701: HTTP 403, blocked
   - https://www.hotelplanner.com/Hotels/155724/Reservations-Four-Points-by-Sheraton-Arusha-The-Arusha-Hotel-Arusha-Corner-of-Uhuru-Rd-Clock-Tower-1000: read (undated third-party listing; the property description is in the hotel's voice)
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: contact source, unreadable (see below)
2. **Kibo Palace Hotel**
   - https://kibopalacehotel.com (home)
   - https://kibopalacehotel.com/sustainability/ ("Corporate Responsibility": the UTU initiative)
   - https://kibopalacehotel.com/carrers/ (careers; current openings)
   - https://kibopalacehotel.com/kibo-palace-hotel-arusha/
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: contact source for both contacts, unreadable
3. **Nnko & Smith Safaris Ltd**
   - https://www.nnkosmith.com: TLS error (UNEXPECTED_EOF); WebFetch: "Socket is closed"
   - http://www.nnkosmith.com: HTTP 404
   - https://nnkosmith.com: TLS error (UNEXPECTED_EOF)
   - https://deeperadventure.com/about (contact source): DNS lookup failed twice with read_page; WebFetch: ENOTFOUND
   - https://tatotz.org/portfolio/nnko-smith-safaris-ltd/: read (undated TATO member profile)
   - https://www.youscholars.com/nnko-smith-safaris-ltd/: HTTP 404
4. **Premier Palace Hotel**
   - https://www.premierpalace-hotel.com: a redirect page (meta refresh) to premierpalace-hotel.com/arusha/
   - http://premierpalace-hotel.com/arusha/ (final URL https://premierpalace-hotel.com/arusha/): read
   - https://premierpalace-hotel.com/arusha/services/: read
   - https://premierpalace-hotel.com/arusha/contact-us/: read; names no one
   - http://premierpalace-hotel.com/arusha/mariwacastor (a link on the home page): HTTP 404
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: contact source, unreadable
5. **Senator Hotel**
   - https://www.senatorhotel.co.tz/: the page renders in JavaScript; read_page gets only the title "Senator Hotel"
   - https://www.senatorhotel.co.tz/static/js/main.5f817897.js: the site's own app script, which holds the page text. Both facts were quoted from it, following the rate-limits guidance for pages that render in JavaScript. A person should confirm them on the rendered page.
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: contact source, unreadable
6. **Vianneys Untamed Expeditions Company Limited**
   - https://www.vianneysuntamedexpeditions.com/ (home: team section; role check)
   - https://vianneysuntamedexpeditions.com/about.php
   - https://vianneysuntamedexpeditions.com/team.php (role headings only; nothing new)

## Blocked or unreadable sources

- **ACHPR hotel list PDF** (https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf): HTTP 200, but read_page returned raw PDF bytes (it parses HTML only). It was recorded as unreadable, as the brief requires. It is the contact source for 5 of the 7 contacts (Michael Kimario, Amina Kapya, Dorcus Membi, Alex J. Mariwa and George Kingazi), so their role checks are `unreachable`. A person with a PDF reader can check them. The list dates from September 2023 and names booking contacts for the ACHPR 77th session.
- marriott.com (HTTP 403) and travelweekly.com (HTTP 403): blocked; not worked around.
- nnkosmith.com: TLS handshake closed on HTTPS and HTTP 404 on plain HTTP; the site appears to be down.
- deeperadventure.com: DNS lookup fails (read_page and WebFetch); the domain does not resolve.
- youscholars.com listing: HTTP 404.
- senatorhotel.co.tz: JavaScript-only page (see above).

## Organisations without a hook, and why

- **ARUSHA HOTEL**: its own website is blocked (403). The third-party listing gives location, history (established 1894) and a room count only; room counts cannot stand for staff. Q1 and Q3 found no staff, welfare, community or growth fact.
- **Nnko & Smith Safaris Ltd**: its website is down, and the TATO profile gives only what the company does, its location and its TATO/TTLB listing.
- **Premier Palace Hotel**: the site gives location, rooms and facilities only. It has nothing on staff, welfare, community or growth.
- **Senator Hotel**: the site text is generic hotel marketing and is internally inconsistent (34 rooms vs 90; 45 km vs 55 km to Kilimanjaro airport), which suggests template text.

## Hooks written (2)

- **Kibo Palace Hotel** (staff_welfare, moderate): based on the UTU initiative's "Empowering Our Staff" item on /sustainability/.
- **Vianneys Untamed Expeditions** (community_programme, moderate): based on the About page's partnership with SELF AWARENESS FOR EVERYONE since 2019.

## Role checks

confirmed 1 (Vianney Jacob Kabwine, Founder and CEO) · changed 0 · not_found 0 · unreachable 6 (5 on the ACHPR PDF; Aminiel Nnko on deeperadventure.com, which does not resolve).

## Organisations not finished

None: every organisation has a line. The six unreachable role checks are the gap, as above.
