# hooks_a coverage, 25 September 2026

Output: `data/raw/hook-research/hooks_a_2026-09-25.jsonl`. It has 7 lines, one for each of the 7 organisations in `runtime/hooks/hooks_a/leads.json`.

- **Hooks:** 4 written (2 strong, 2 moderate); 3 null.
- **Role checks:** 8 contact messages were checked: 5 confirmed, 0 changed, 0 not_found and 3 unreachable.
- **Searches:** 4 of 5 used, and none was refused.
- **Status:** 4 found; 3 partial (Arusha Villa, Lush Garden Hotel, Silver Palm).

## Searches

| # | Query | Organisation | Why a search was needed | What it led to |
|---|---|---|---|---|
| Q1/5 | `"Arusha Villa" Arusha` | Arusha Villa | Its own site answered HTTP 403 | Tanzania Specialist and Discover Africa listings (read and used); Arusha Trips listing (read, nothing usable) |
| Q2/5 | `"Lush Garden Hotel" Arusha` | Lush Garden Hotel | Its own site fails TLS (certificate hostname mismatch) | Reserving.com (403) and Booking.com (202 bot challenge); nothing readable |
| Q3/5 | `"Silver Palm Hotel" Arusha` | Silver Palm | Its own site shows only a maintenance page | Artu Expeditions listing (read and used); Planet of Hotels (403) |
| Q4/5 | `"Lush Garden" hotel Arusha Sakina` | Lush Garden Hotel | Q2 led only to blocked booking sites | Arusha Park listing dated 15 May 2023 (read and used) |

The other four organisations needed no search, because their own pages, or the contact's source page, gave usable facts. Search-result snippets were not recorded as facts. Where a note mentions one, it is labelled as a snippet.

## Pages read, by organisation

All pages were read with `scripts/contacts/read_page.py`. WebFetch and the browser were not used.

A page marked *(cache …)* was served from the reader's cache, which was written earlier by the reader. The time shows when. A role check on such a page reflects the page as it was then. Every other page was fetched on 25 September 2026 between 19:17 and 19:34.

1. **Davis & Shirtliff**
   - https://www.davisandshirtliff.com/tanzania-branches: 200 *(cache 23 Sep 14:53)*; role check and the Arusha branch fact
   - https://www.davisandshirtliff.com/about-us: 200
   - https://www.davisandshirtliff.com/improvinglives: 404 (a guessed URL; the real one is below)
   - https://tanzania.davisandshirtliff.com/: 200 (no staff or Arusha facts)
   - https://www.davisandshirtliff.com/corporate-social-responsibility: 200
2. **Arusha Villa**
   - https://arushavilla.co.tz/contact: 403, blocked (contact source)
   - https://arushavilla.co.tz/: 403, blocked *(cache 23 Sep 02:29)*
   - https://tanzania-specialist.com/accommodation/arusha-villa/: 200
   - https://www.discoverafrica.com/accommodation/arusha-villa/: 200
   - https://arushatrips.com/tanzania/accommodation/arusha-villa-tanzania/: 200 (no facts about the villa itself; not used)
3. **Lush Garden Hotel**
   - https://lushgardenhotels.co.tz/: TLS certificate hostname mismatch; not read
   - https://www.lushgardenhotels.co.tz/: the same certificate error; not read
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: 200, but unreadable PDF bytes (contact source)
   - https://reserving.com/hotels/africa/tanzania/arusha/arusha/lush-garden-hotel: 403, blocked
   - https://www.booking.com/hotel/tz/lush-garden.html: 202 bot challenge; not passed
   - https://www.arushapark.com/lush-garden-hotel/: 200 (page dated 15 May 2023)
4. **Nyamazela Trading Co (T) LTD (Meserani Snake Park)**
   - https://meseranisnakepark.net/contact/: 200 (contact source)
   - https://meseranisnakepark.net/about/: 200
   - https://meseranisnakepark.net/: 200 (little text)
   - https://meseraniproject.co.uk/: 200 (a separate UK charity linked as a partner; not used for facts)
5. **PwC Tanzania**
   - https://tatotz.org/portfolio/pwc-tanzania/: 200 (page dated 04-Jun-2025; contact source for both managers)
   - https://www.pwc.co.tz: 403, blocked *(cache 23 Sep 02:36)*
6. **Silver Palm**
   - https://www.silverpalmhotel.com, which redirects to https://silverpalmhotel.com/: 200, maintenance page *(cache 23 Sep 14:56)*
   - https://silverpalmhotel.com/: 200, the same maintenance page on 25 Sep
   - https://achpr.au.int/sites/default/files/files/2023-09/arusha-hotel-list.pdf: unreadable PDF bytes (contact source; see Lush Garden Hotel)
   - https://www.artuexpeditions.com/silver-palm-hotel: 200
   - https://en.planetofhotels.com/tanzania/arusha/silver-palm-hotel: 403, blocked
7. **Victory Attorneys & Consultants**
   - https://victoryattorneys.co.tz/: 200 *(cache 24 Sep 01:55)*; contact source
   - https://victoryattorneys.co.tz/contact/: 200 *(cache 24 Sep 01:56)*; no office list
   - https://victoryattorneys.co.tz/about-mootcourt/: 200
   - https://victoryattorneys.co.tz/about-vicon/: 200
   - https://victoryattorneys.co.tz/the-firm/: 200 (source of all five facts)
   - https://victoryattorneys.co.tz/partners/: 200 (read fresh to back up the role check made on the cached home page)

## Blocked or unreadable sources

- **arushavilla.co.tz: HTTP 403.** Both the contact page (25 Sep) and the home page (cache, 23 Sep) returned 403. The block was not worked around, so the manager's role check is `unreachable`.
- **lushgardenhotels.co.tz, with and without www: TLS certificate hostname mismatch.** Certificate errors are never passed. It is not clear whether the domain still belongs to the hotel.
- **ACHPR Arusha hotel list (PDF, September 2023): unreadable.** It answered HTTP 200 (application/pdf, 448,888 bytes), but read_page.py returns raw PDF bytes, not text. It was recorded as unreadable and was not decoded any other way. Two role checks depend on it (Mary Joseph and Jakline Mzindakaya), and both are `unreachable`.
- **www.pwc.co.tz: HTTP 403.** This was the reader's cached answer from 23 September, and it was not retried.
- **Booking.com: HTTP 202 with a bot challenge.** It was not passed.
- **Reserving.com and Planet of Hotels: HTTP 403.**
- **silverpalmhotel.com: readable, but only a maintenance page** ("Maintenance mode is on", "© Silver Palm Hotel 2022").
- **Not tried (usually blocked, or behind a login):** TripAdvisor, Hotels.com, Expedia, Agoda, Trip.com, Priceline and Facebook from the search results.
- **The firm profile PDF of Victory Attorneys** is hosted at vps101783.inmotionhosting.com. It was not read.

## Organisations without a hook, and why

- **Arusha Villa.** Its own site is blocked. The only usable basis is its location just outside Arusha town, taken from undated third-party travel listings. That is too weak for a first message: in the 23 September review, the coordinator rejected hooks built on undated third-party profiles when the organisation's own site could not be read. No staff, programme or community fact was found.
- **Lush Garden Hotel.** Its own site cannot be read. The only facts come from a 2023 safari-site listing: location, 100 rooms and four restaurants. Rooms are not staff, and no workforce, programme or staff fact was found.
- **Silver Palm.** Its website shows only a maintenance page. The only facts come from one undated tour-operator listing: 50 rooms and a central Arusha location. A central-Arusha basis fits any hotel in town.

## Hooks written

| Organisation | Basis (fact index) | Type / quality |
|---|---|---|
| Davis & Shirtliff | Its own branch list shows an Arusha branch on Sokoine Rd (3) | locality / moderate |
| Nyamazela Trading Co (T) LTD | The park's About page features the Free Education Centre, where local Maasai learn to read and write (2) | education_programme / moderate |
| PwC Tanzania | Its TATO profile gives over 290 staff working from offices in Dar es Salaam and Arusha (0) | workforce / strong |
| Victory Attorneys & Consultants | The firm has organised a yearly national moot court competition for students since 2020 (2) | education_programme / strong |

## Organisations not finished

None. All 7 have a line.

## Points for a person to check

- **Wrong sector in our records.** PwC Tanzania is a professional services firm: TATO lists it as an affiliate member under Financial Services. Victory Attorneys & Consultants is a law firm. Both are filed under Tourism employers.
- **Victory Attorneys: location fit.** The only published office is its main office in Dar es Salaam (IT Plaza Building, Ohio Street/Garden Avenue). No Arusha office or Arusha-based staff were found. Check this before sending.
- **Silver Palm: possible closure or lapsed website.** The site has shown a maintenance page since at least 23 September, with a 2022 copyright. Search snippets (not verified) show 2026 reviews on travel sites.
- **Lush Garden Hotel.**
  - The site's certificate does not match its domain.
  - Search snippets (not verified) show a separate "Lush Garden Business Hotel". An unofficial site, lushgardenhotel.com-tanzania.com, also appears. It is not the hotel's own and was not read.
- **ACHPR list contacts.** Mary Joseph (Lush Garden Hotel) and Jakline Mzindakaya (Silver Palm) come from a 2023 event list that gives no role, and could not be re-checked.
- **Arusha Villa.** The contact is recorded by surname only ("Pallangyo"), and the role could not be re-checked.
- **Records with an email address in the locality field.** For Nyamazela Trading Co (T) LTD, the public name is Meserani Snake Park and the website is https://meseranisnakepark.net/. For Victory Attorneys, the website is https://victoryattorneys.co.tz/.
- **Davis & Shirtliff.** The figure of over 900 staff is group-wide. No Tanzania or Arusha staff count is published.
- **Role checks on cached pages.** The Davis & Shirtliff branch page was cached on 23 Sep, and the Victory home page on 24 Sep. The Victory partners page, read fresh on 25 Sep, shows the same name and role.
- **PwC Tanzania.** Two senior managers at one firm are on our list, so send one version of the first message per organisation.
- **Contact details not recorded.** Some source pages list mobile numbers or personal work emails for contacts: PwC's TATO page, the Victory contact page and the Meserani contact page. Only names and roles were recorded.
