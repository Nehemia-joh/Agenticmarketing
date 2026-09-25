# Hook research coverage: slice C (6 organisations), 2026-09-25

Brief: `runtime/hooks/hooks_c/prompt.md`. Leads: `runtime/hooks/hooks_c/leads.json`. Output: `data/raw/hook-research/hooks_c_2026-09-25.jsonl` (6 lines, one per organisation).

Summary: 6 of 6 organisations done. 2 hooks written (both strong), 4 without a hook. Role checks on 7 contacts: 5 confirmed, 2 unreachable, 0 changed, 0 not_found. WebSearch: 4 of 5 used, none refused.

Status values: `found` means brief facts plus a hook; `partial` means brief facts but no hook. `not_found` and `blocked` were not needed: every organisation had at least one readable source.

Hook quality: `strong` means a specific published fact about the organisation's own staff or its own education programme.

Checks on every record:
- Each excerpt was checked against the text of the page as cached by `scripts/contacts/read_page.py`. It must appear verbatim, lines joined by single spaces, in at most 300 characters.
- Aafrin's excerpts were checked against the string literals in the site's script bundle (see below).
- Each hook is at most 35 words, uses only numbers found in its cited excerpt, and contains none of "families", "parents", "discount", "price", "percent" or "fee".

## Queries

| # | Query | Organisation | Result |
|---|-------|--------------|--------|
| Q1/5 | `"Gran Melia Arusha" staff employees community` | Gran Melia Arusha | Guest reviews (Tripadvisor), a safari operator's lodge page (Yellow Zebra Safaris, read), Travel Weekly, melia.com, Facebook, Instagram, hotels.com. No workforce or community facts. |
| Q2/5 | `"SafariHQ" Arusha Tanzania tour operator` | Safari – HQ | ATTA organisation page and TATO member page (both read). The other results were not fetched: LinkedIn, Tripadvisor, Facebook, directories, and safarihq.com, which is already blocked. |
| Q3/5 | `"Gran Melia Arusha" donation school CSR employees news` | Gran Melia Arusha | Venue listings (Cvent, Northstar), tour-operator pages (Somak, Easy Travel), reviews, Facebook, and a Wikipedia article on another school. Nothing relevant; nothing fetched. |
| Q4/5 | `Meliá Hotels International "Gran Meliá Arusha" opening press release jobs` | Gran Melia Arusha | The 2019 opening announcement (Hospitality Net) and article (Tourism Update), both read, plus the TATO member page (read). Neither gives job or staff numbers. |

Q5 was not used. Searches were run only where the organisation's own website was blocked: Gran Melia (melia.com, HTTP 403) and Safari – HQ (safarihq.com, HTTP 403).

## Pages read, by organisation

Each contact's source URL was re-opened for the role check (marked "contact source").

1. **Aafrin Medihealth Solutions Ltd** (no hook)
   - https://aafrinmedihealth.com/about (contact source): HTTP 200, but only the script shell (title only). WebFetch also saw only the shell.
   - https://aafrinmedihealth.com/: the same shell (same SHA-256), with a meta description and JSON-LD.
   - https://aafrinmedihealth.com/assets/index-CN3aQvob.js: the site's own script bundle, which robots.txt allows (checked).
     - The page text of the routes `/`, `/about` and `/contact` was found in it. The router maps `/about` to the component with the Our Team section, and `/` and `/contact` render the Our Offices section.
     - It was read through the project's polite fetcher (`contact_lib.fetch`, cached), with small helper scripts in the session scratchpad.
2. **Gran Melia Arusha** (no hook; Q1, Q3, Q4)
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf (contact source): unreadable, see below.
   - https://www.melia.com/en/hotels/tanzania/arusha/gran-melia-arusha: HTTP 403, blocked.
   - https://yellowzebrasafaris.com/us/tanzania/accommodation/gran-melia-arusha/
   - https://www.tourismupdate.com/article/new-luxury-hotel-opens-in-arusha (22 Sep 2019)
   - https://www.hospitalitynet.org/announcement/41003669/gran-melia-arusha.html, which redirected to /announcement/41003669/new-luxury-hotel-opening-gran-melia-arusha (19 Sep 2019)
   - https://tatotz.org/portfolio/gran-melia-arusha/
3. **Ngare Sero Mountain Retreat** (hook: workforce, strong)
   - https://ngare-sero-lodge.co.tz/contact (contact source)
   - https://ngare-sero-lodge.co.tz/
   - https://ngare-sero-lodge.co.tz/lodge
   - robots.txt answered 4xx (none).
4. **Palace Hotel** (no hook)
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf (contact source): unreadable, see below.
   - https://palacehotelarusha.com/ (the page is mostly a booking calendar; links were taken from the cached copy)
   - https://palacehotelarusha.com/about-us/
   - https://palacehotelarusha.com/contact-us/: HTTP 404 (a guessed URL; no further guessing).
5. **Safari – HQ** (no hook; Q2)
   - https://atta.travel/resource/safarihq-wtma26.html (contact source; ATTA trade-show exhibitor entry dated 26 Mar 2026)
   - https://safarihq.com: HTTP 403, blocked. robots.txt answered 4xx.
   - https://tatotz.org/portfolio/safari-hq/
   - https://atta.travel/organisation/safarihq-ltd.html
6. **Top Nature Tanzania Safari** (hook: education programme, strong)
   - https://topnaturesafaris.com/about%20us.html (contact source for both contacts)
   - https://topnaturesafaris.com/script.js (checked for the contacts' surnames and titles; none found)
   - https://topnaturesafaris.com/
   - robots.txt answered 4xx (none).

## Blocked or unreadable sources

- **https://www.melia.com/en/hotels/tanzania/arusha/gran-melia-arusha**: HTTP 403. Recorded and not worked around; WebFetch was not tried on a blocked page.
- **https://safarihq.com**: HTTP 403. Recorded and not worked around; no other hostname (such as www.) was tried.
- **https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf** (contact source for Gran Melia and Palace Hotel):
  - It answered HTTP 200 and robots.txt allows it, but `read_page.py` does not parse PDFs.
  - WebFetch reported it as binary it could not read, and saved a copy. The Read tool was tried on that copy but cannot render PDFs on this machine (pdftoppm is missing).
  - Following this run's rule to record unreadable bytes as unreadable rather than work around them, the text was not extracted another way, for example with a local PDF library. Both role checks are therefore `unreachable`.
  - The 2026-09-23 run (slice B) did extract a prospectus PDF with pypdf. The coordinator can decide whether to do the same here.
- **aafrinmedihealth.com** is not blocked, but it is built by script: read_page and WebFetch return only the shell. Its text was read from the site's own script bundle, as the rate-limits reference suggests for pages that render in JavaScript. The shared browser pane was not used, because research subagents do not use it.

## Organisations without a hook, and why

- **Aafrin Medihealth Solutions Ltd**:
  - The site publishes no workforce size and no staff-welfare, education or community programme.
  - Its Arusha link is only a registered address in Njiro Industrial Area; the office address is in Dar es Salaam, with a branch in Mumbai.
- **Gran Melia Arusha**:
  - The hotel's own page is blocked, and three searches found no published workforce size and no staff, education or community programme.
  - The 171 rooms are a room count, not a staff count.
- **Palace Hotel**: the site publishes no workforce size or programme, and a central Arusha location is shared by most leads, so it is not a specific reason.
- **Safari – HQ**: the own site is blocked, and the ATTA and TATO directories give no workforce size or programme.

## Organisations not finished

None. All 6 have a line.

## For a person to check

- **Aafrin Medihealth Solutions Ltd: wrong sector.**
  - It is a medical tourism and concierge facilitator that sends patients from Tanzania to hospitals in India, not a leisure tourism employer.
  - Check whether any of its staff work in Arusha.
  - The page's JSON-LD (Dar es Salaam, founded 2020, 10-50 employees, placeholder phone +255-XXX-XXX-XXX) conflicts with the site's "Established in 2023" and was not used.
  - A browser check of /about would confirm the text read from the script bundle.
- **Ngare Sero: name.** The website calls the business "Ngare Sero Mountain Lodge" (Ngare Sero Mountain Lodge Ltd.), not "Ngare Sero Mountain Retreat" as in our records and the purpose sentence.
- **Top Nature: names and locality.**
  - The About page no longer shows the surnames "Grist" and "Meshallu" or the titles "Sales Manager" and "Director, Naturalist, Guide". It names "Deneen" as U.S. sales representative and "Adam" / "Adam Stephen" as Tanzania-based founder and lead operator. Both are recorded as confirmed with equivalent roles; check the surnames before sending.
  - No office address was found, so the "Arusha" locality in our records is unconfirmed.
- **ACHPR PDF (Gran Melia, Palace Hotel)**:
  - Open it by hand to check whether it still names Godlove Mlaki and Bahati Shirima.
  - The list is from September 2023 and states no role, so both contacts' current roles are unknown.
- **Safari – HQ**:
  - The sources give only a P.O. Box in Arusha, and do not say where the Sales Director is based.
  - Search snippets claimed "since 2010" and "over 50 years" of combined team experience, but no page read showed this, so it was not recorded.

## Privacy exclusions

The following were seen and deliberately not recorded:
- Aafrin founder's personal and family story.
- Ngare Sero owners' family history, named staff, and the clause about employees' children. The workforce excerpt stops before that clause.
- Top Nature founders' personal and family background.
- Guest reviews naming individual hotel staff.
- Phone numbers and email addresses. For Ngare Sero, the phone number printed beside "Hellen" is replaced in the contact excerpt with "[phone number omitted]".

Excerpts from the copyrighted Tourism Update article were kept to short phrases.
