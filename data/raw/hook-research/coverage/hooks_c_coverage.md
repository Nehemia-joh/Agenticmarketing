# Hook research coverage: slice C (14 organisations), 2026-09-23

Brief: `runtime/hooks/hooks_c/prompt.md`. Leads: `runtime/hooks/hooks_c/leads.json`. Output: `data/raw/hook-research/hooks_c_2026-09-23.jsonl` (14 lines, one per organisation).

Summary: 14 of 14 organisations done. 10 hooks written (7 strong, 3 moderate), 4 without a hook. Role checks on 17 contacts: 16 confirmed, 1 not_found, 0 changed, 0 unreachable. WebSearch: 1 of 10 used.

Status values used: `found` means brief facts plus a hook. `partial` means brief facts but no hook. `not_found` and `blocked` were not needed.

Hook quality: `strong` means a specific published fact about the organisation's own staff (size, structure, welfare policy) or its own education or training programme. `moderate` means a general commitment the organisation states.

Every excerpt was checked against the page text that `scripts/contacts/read_page.py` cached: it must appear verbatim, lines joined by single spaces, in at most 300 characters. Each hook was checked for at most 35 words, numbers that appear in the cited excerpt, and none of the words "families", "parents", "discount", "price", "percent" or "fee".

## Queries

| # | Query | Organisation | Result |
|---|-------|--------------|--------|
| Q1/10 | `"Arusha Technical College" staff SACCOS` | Arusha Technical College Staff SACCOS Ltd | Only the college's own SACCOS page (heading only, already read) and aggregator or social listings (ZoomInfo, CB Insights, LinkedIn, Facebook, Educatly, UNEVOC, Wikipedia). None were fetched and nothing about the SACCOS was recorded. |

No other searches were needed: every other organisation's own pages gave usable facts. No search was refused.

## Pages read, by organisation

Each contact's source URL was re-opened for the role check (marked "contact source").

1. **Arusha Meru International School** (no hook)
   - https://www.arushameru.sc.tz/ (contact source)
   - https://www.arushameru.sc.tz/about
   - https://www.arushameru.sc.tz/faculties-and-staff
   - https://www.arushameru.sc.tz/notice (empty list)
   - https://www.arushameru.sc.tz/events (empty list)
   - HTTP 404 (the site's own links): /admission-details/2%2Fover-all-admission, /message-view/5%2FHead%20of%20Primary, /message-view/3%2FHead%20of%20Secondary
2. **Arusha Technical College Staff SACCOS Ltd** (no hook; Q1)
   - https://www.atc.ac.tz/directorate/DHRMA (contact source)
   - https://www.atc.ac.tz/SACCOS (heading only)
   - https://www.atc.ac.tz/about
   - https://www.atc.ac.tz/
3. **Afrika Roots Safari Company Limited** (hook: community programme, moderate)
   - https://afrikaroots.com/meet-the-team (contact source)
   - https://afrikaroots.com/
4. **Bush 2 City Adventure** (hook: workforce, moderate)
   - https://bush2cityadventure.com/about-us/ (contact source)
   - https://bush2cityadventure.com/
5. **Dream Peak Safaris** (hook: workforce, strong)
   - https://dreampeaksafaris.com/about-dream-peak-tours-safaris/ (contact source for both contacts)
   - https://dreampeaksafaris.com/
6. **ET Investments Ltd (Tanzania Experience)** (hook: workforce, strong)
   - https://www.tanzania-experience.com/about-us/tanzania-safari-specialists/ (contact source for both contacts)
   - https://www.tanzania-experience.com/about-us/
   - https://www.tanzania-experience.com/careers/
7. **Good Earth Safaris & Tours Ltd** (hook: staff welfare, strong)
   - https://goodearthtours.com/team/ (contact source)
   - https://goodearthtours.com/our-impact/
   - https://goodearthtours.com/about-us/
8. **Kiliclimb Africa Safaris** (hook: education programme, strong)
   - https://kiliclimbafricasafaris.com/meet-the-kiliclimb-africa-safaris-team/ (contact source)
   - https://kiliclimbafricasafaris.com/giving-back-to-the-community/
9. **Lion King Adventures (King Kidaisho)** (hook: workforce, strong). All three pages arrived gzip-compressed; see the next section.
   - https://lionkingadventures.com/office-team/ (contact source for both contacts)
   - https://lionkingadventures.com/
   - https://lionkingadventures.com/maasai-community-work/
10. **Nndeeafrika** (no hook)
    - https://nndeeafrika.com/our-story/ (contact source)
    - https://nndeeafrika.com/
11. **Safari Asap** (hook: staff welfare, strong)
    - https://safariasap.com/about-us/ (contact source)
12. **Serengeti Balloon Safaris** (hook: education programme, strong)
    - https://www.balloonsafaris.com/our-story (contact source)
    - https://www.balloonsafaris.com/responsibility
    - https://www.balloonsafaris.com/
    - https://www.balloonsafaris.com/contact
13. **The Wanderer Tanzania Ltd** (no hook)
    - https://wanderertanzania.com/about-us (contact source)
    - https://wanderertanzania.com/contact-us
    - https://wanderertanzania.com/
14. **Wildfinder Tours & Safaris Limited** (hook: community programme, moderate)
    - https://wildfindersafaris.com/en/about-us/ (contact source)
    - https://wildfindersafaris.com/en/impressum/
    - https://wildfindersafaris.com/en/contact/

## Blocked or unreadable sources

- **No blocks.** There was no 403, 429, captcha or login wall. Every site's robots.txt was read and allowed the pages above.
- **lionkingadventures.com: compressed pages.** The server sends gzip-compressed pages even when compression is not requested, and `read_page.py` printed the compressed bytes undecoded.
  - The bytes already cached were decompressed locally with no further request, and the text was extracted with `contact_lib.html_lines`, so the excerpts are verbatim.
  - The office-team page was cross-checked once with WebFetch.
  - Suggested fix: `contact_lib.fetch` should decode a `Content-Encoding: gzip` response.
- **arushameru.sc.tz: 404s.** Three of the site's own links return HTTP 404 (listed above). This is not a block.
- **atc.ac.tz: slow.**
  - The first read of the DHRMA page ran past the tool's 2-minute limit. It then finished in the background and was cached.
  - The SACCOS page timed out once, and the fetcher's own retry succeeded.

## Organisations without a hook, and why

- **Arusha Meru International School.**
  - The organisation is itself a school teaching Nursery or Pre Primary to Year 13.
  - Its pages publish no staff numbers, staff programmes or news, and the staff page is generic template text that begins "At Cambridge".
  - A person should decide whether an education-benefit approach suits a school covering the same ages.
- **Arusha Technical College Staff SACCOS Ltd.**
  - Nothing is published about the SACCOS itself: the college's ATC-SACCOS page shows only its heading, and Q1 found no other source.
  - The brief facts describe the college.
- **Nndeeafrika.**
  - The site describes a California-registered LLC ("African-rooted. California-based.") run by two co-founders with "local partners on the ground".
  - It publishes no Tanzanian staff or office, so no fact shows an Arusha workforce.
- **The Wanderer Tanzania Ltd.**
  - The pages give only general statements (a dedicated team, work with local communities).
  - They publish no staff numbers, programmes, news or street address.

## Organisations not finished

None. All 14 have a line.

## For a person to check

- **Good Earth Safaris & Tours:** Rose Moses is not on the team page (not_found). The reservations role is listed as "Juliet Kamili, Reservation Manager", and the page also lists a CEO and a Director. Choose a current contact before sending.
- **ET Investments Ltd:** the name "ET Investments Ltd" does not appear on the Tanzania-Experience pages, but the purpose sentence uses it. Confirm the legal entity or use the trading name. The 80 permanent employees are company-wide, and the company also has a sales office in Stellenbosch.
- **Arusha Technical College Staff SACCOS:** the contact is the college's Director of Human Resource Management and Administration, not a named SACCOS committee member.
- **Arusha Meru International School:** the home page shows "Mr Ms. Shanmugapriya Magesh", so avoid an honorific in the salutation.
- **Serengeti Balloon Safaris:**
  - The 70+ staff come from communities next to the parks.
  - The Operations Manager contact leads the field team in Serengeti, Ruaha and Tarangire.
  - The only address given is a PO Box in Arusha.
  - Consider how many staff are near Silverleaf's campuses.
- **Wildfinder:** the page confirms Happyness only as co-founder. The "Managing Director (Geschaeftsfuehrerin)" title on record is not on the English about or imprint pages.
- **Lion King Adventures:** "(CPA)" and "King Kidaisho" from the records do not appear on the pages read.
- **Safari Asap:** the about page calls Safari ASAP "one of our brands", so the operating company's legal name may differ.
- **Privacy:** several pages publish personal biographies, family details or details about children (Afrika Roots, Dream Peak, Good Earth, Lion King, Nndeeafrika, Serengeti Balloon Safaris). None of it was recorded; contacts are recorded by published name and role only.

## Working files

Pages were cached under `runtime/contacts/http-cache/` by `read_page.py`, as designed. Helper scripts and intermediate records were kept in the session scratchpad, outside the repository. No other repository file and no database was changed.
