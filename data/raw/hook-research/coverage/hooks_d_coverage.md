# Hook research coverage: slice D (2026-09-23)

Leads: `runtime/hooks/hooks_d/leads.json` (14 organisations, 22 contacts).
Output: `data/raw/hook-research/hooks_d_2026-09-23.jsonl` (14 lines, one per organisation).
Pages were read with `scripts/contacts/read_page.py`. WebFetch was not used.
The run stalled once on a connection problem and was resumed. No line was written twice.

## Searches (1 of 10 used)

| # | Query | Organisation | Pages read from the results |
|---|---|---|---|
| Q1/10 | `"Safari Crew Tanzania" Arusha` | Safari Crew Tanzania | tatotz.org member profile, atta.travel directory entry, safaribookings.com/p1368 |

No other search was needed: every other organisation's own pages gave usable facts.

## Pages read, by organisation

1. **Arusha Technical College** (8 pages, read before the six-page guidance)
   - https://www.atc.ac.tz/directorate/DHRMA
   - https://www.atc.ac.tz/management
   - https://www.atc.ac.tz/about
   - https://www.atc.ac.tz/ (home: rector's message, news)
   - https://www.atc.ac.tz/structure: no text, probably an image
   - https://www.atc.ac.tz/SACCOS, https://www.atc.ac.tz/maafa and https://www.atc.ac.tz/health_centre: empty stubs
2. **AFRICA SAFARI EXPERTS LTD**
   - https://safari-experts.de/ueber-uns
   - https://www.safari-experts.com/: failed (SSL certificate hostname mismatch)
   - http://www.safari-experts.com/: redirects to https://safari-experts.de/home
3. **Alika Africa**: https://www.dumaexplorer.com/about-us
4. **Cheli Peacock Safaris T Ltd**
   - https://chelipeacock.com/about/team
   - https://chelipeacock.com/consservation-and-community
5. **Duma Explorer (Alika Africa)**: https://www.dumaexplorer.com/about-us (the same page as Alika Africa)
6. **Eyes Of Tanzania Limited**
   - https://eyes-of-tanzania.com/about-us/
   - https://eyes-of-tanzania.com/
   - https://tlto.org/members/eyes-of-tanzania-limited: HTTP 500 (the site links to it)
7. **Great Image Expedition Ltd**
   - https://gie.co.tz/office-team/
   - https://gie.co.tz/about-us/
8. **Kingse Safaris**
   - https://kingsesafaris.com/team
   - https://kingsesafaris.com/nanyaro-foundation
9. **Make My Safari Limited**
   - https://makemysafari.com/about/
   - https://makemysafari.com/
10. **Paradies Safaris Ltd**
    - https://www.paradiessafaris.com/en/home/about-us
    - https://www.paradiessafaris.com/de/impressum
    - https://www.paradiessafaris.com/de/angebote/Community-reise
11. **Safari Crew Tanzania**
    - https://www.safaricrewtanzania.com/chi-siamo/, https://www.safaricrewtanzania.com/ and https://www.safaricrewtanzania.com/en/about-us-safari-crew-tanzania-local-tour-operator/: all disallowed by robots.txt, not read
    - https://tatotz.org/portfolio/safari-crew-tanzania/
    - https://atta.travel/organisation/safari-crew-tanzania.html
    - https://www.safaribookings.com/p1368: no usable fact
12. **Serengeti Big Cats Safaris Ltd**
    - https://serengeti-big-cats-safaris.com/lagence/
    - https://serengeti-big-cats-safaris.com/politique-de-durabilite-et-engagements/
13. **Udaay Safari and Tours Ltd**
    - https://udaaysafaris.com/about-us/
    - https://udaaysafaris.com/?page_id=1294, which redirects to https://udaaysafaris.com/conservation-community/
14. **Wilkinson Tours Ltd**
    - https://wilkinson-tours.com/about/
    - https://wilkinson-tours.com/

## Blocked or unreadable sources

- **www.safaricrewtanzania.com:** robots.txt disallows our crawler on every page tried. Nothing was worked around. Hillary Mwanga's role is recorded as `unreachable`.
- **https://www.safari-experts.com/:** SSL certificate hostname mismatch, and its robots.txt could not be read. The http address redirected to safari-experts.de, which was read.
- **https://tlto.org/members/eyes-of-tanzania-limited:** HTTP 500, and its robots.txt could not be read.
- **atta.travel:** contact details appear only after a member login. The login was not attempted.
- **Pages without text:** ATC's Organization Structure page (probably an image) and its SACCOS, Chama cha Maafa and Health Centre stubs.
- **Unreliable text:** Udaay's Conservation & Community page ends with leftover drafting text ("Feel free to adjust any part of the text…"), so its programme claims were not used.

## Organisations without a hook

- **Safari Crew Tanzania:** its own site cannot be read (robots.txt). The readable member profiles on TATO and ATTA give only location, licensing and memberships. There is no workforce, staff or programme fact to support a hook.

## Hooks written: 13

- **Strong (5):**
  - Alika Africa and Duma Explorer: most staff have been with the company more than a decade
  - Cheli & Peacock: some of the team have been with the company over 15 years
  - Kingse Safaris: the Nanyaro Foundation's community school
  - Serengeti Big Cats: the sustainability policy's fair wages, benefits and advancement for employees
- **Moderate (8):**
  - Arusha Technical College: new Kikuletwa Campus (growth)
  - Africa Safari Experts: own team in Arusha (locality)
  - Eyes Of Tanzania: Usa River address only (locality)
  - Great Image Expedition: own guides lead every safari (workforce)
  - Make My Safari: Arusha team roles (workforce)
  - Paradies Safaris: team of coordinators, service liaisons, cooks and guides (workforce)
  - Udaay: each trip led by a driver-guide (workforce)
  - Wilkinson Tours: driver guides and supporting staff (workforce)

## Role checks

- **Confirmed: 21.**
- **Unreachable: 1** (Hillary Mwanga, Safari Crew Tanzania: robots.txt).
- **Changed: 0. Not found: 0.**

## Organisations not finished

None. All 14 have a line.

## For a person to check

- **Duplicate lead:** Alika Africa (O99edb02a90e9) and Duma Explorer (Alika Africa) (O1abe9227eaf0) are the same company. Omary Ridhiwan is a contact on both, so make sure he gets only one first email.
- **Safari Crew Tanzania:** check Hillary Mwanga's role by hand.
- **AFRICA SAFARI EXPERTS LTD:**
  - The site is German. Its excerpts are German, and the facts and hook are translations.
  - Confirm that the Ltd is the Arusha operating company behind the German business.
- **Serengeti Big Cats:**
  - The site is French. Its excerpts are French, and the facts and hook are translations.
  - Kilimanjaro climbs run through a partner agency (Memorable Sunrise to Sunset Safaris).
- **Cheli & Peacock:** Jacqueline Onyango is listed in the Kenya section of the team page. Patrick Bourgeix is General Manager Tanzania.
- **Possibly better addressees:**
  - Make My Safari: Talib Chagani (Director)
  - Udaay: Kalpesh Sangar (Managing Director)
  - Wilkinson Tours: Horst and Debbie Bachmann (Directors)
  - Serengeti Big Cats: Cécile (co-founder, agency manager)
- **Kingse Safaris:** Samara Imhoof may be based in Australia.
- **Arusha Technical College:** it is a public college, so a staff benefit may need approval beyond the college.
- **Privacy:** several pages carry personal or family details of owners and staff. None is recorded.
