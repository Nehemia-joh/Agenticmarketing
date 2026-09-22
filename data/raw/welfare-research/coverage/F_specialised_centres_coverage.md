# Slice F coverage log: specialised centres

Run `arusha-welfare-2026-09`. Slice F covers specialised centres across the catchment (Arusha city, Arumeru/Meru, Hai, Siha and Moshi). Research date: 2026-09-22.

## Critical limitation: search budget exhausted

This session shares a WebSearch cap of 200 calls, and it was reached after this slice had run **8 queries**. The next 3 queries were refused ("200 of 200 WebSearch calls"). The system asked agents to continue without further searches, so this slice did not use search engines through WebFetch.

As a result, **the stopping rule (12 consecutive varied queries with no new organisation) was not met.** Discovery stopped after the seeds plus one well-known street-children centre. Every query in the "Not run" list below is still outstanding.

To finish this slice, raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and re-run slice F starting from that list.

## Records written

File: `F_specialised_centres.jsonl`. All 50 lines parse as JSON, and every excerpt is 25 words or fewer.

| Record type | Count |
|---|---|
| organisation | 6 |
| contact | 20 |
| relationship | 24 |

**Organisations:**
- Sibusiso Foundation (Tengeru)
- Usa River Rehabilitation and Training Centre (Usa River)
- Kafika House, formerly The Plaster House (Arusha, with a Moshi house)
- Amani Centre for Street Children (Moshi, with an Arusha drop-in centre)
- Under The Same Sun (national albinism funder, run from Mwanza)
- Standing Voice (albinism funder, based in Mwanza)

## WebSearch queries

| # | Query | Result |
|---|---|---|
| 1 | Sibusiso Foundation Arusha children with intellectual disabilities | New: Sibusiso |
| 2 | Usa River Rehabilitation Centre children disabilities Tanzania | New: URRC |
| 3 | The Plaster House Arusha children rehabilitation | New: The Plaster House |
| 4 | sibusiso.com contact info@sibusiso.com Arusha Njiro | No new organisation; Sibusiso contact snippet |
| 5 | Stichting Sibusiso Nederland ANBI Tanzania kinderen met een beperking | No new organisation; Dutch arm and CBF listing |
| 6 | "Plaster House" Arusha location Kisongo OR Burka OR Olasiti OR Ngaramtoni | No new organisation; found the rename to Kafika House |
| 7 | Kafika House Arusha formerly The Plaster House rehabilitative surgery children | No new organisation; Kafika details |
| 8 | kafikahouse.org heal children stay school classroom teacher Arusha | No new organisation; education during stays |
| 9 | street children centre Moshi Kilimanjaro Mkombozi Amani | **Refused: budget exhausted** |
| 10 | street children centre Arusha Tanzania NGO | **Refused: budget exhausted** |
| 11 | special needs children centre Arusha autism cerebral palsy NGO | **Refused: budget exhausted** |

Amani Centre was found by fetching its known website directly. Under The Same Sun and Standing Voice were also checked through their known websites.

### Not run (outstanding)

These are the queries from the task brief plus planned follow-ups:

- disabled children centre Arusha
- special needs children Arusha NGO
- autism centre Arusha
- deaf children Arusha school centre
- blind children Moshi / Arusha
- albinism children Arusha / Moshi centre
- rehabilitation centre children Usa River
- street children centre Arusha
- street children Moshi centre
- girls rescue centre Arusha
- safe house girls Arusha
- girls rescue centre Arumeru / Meru
- kituo cha watoto wenye ulemavu Arusha / Moshi
- kituo cha watoto wa mitaani Arusha / Moshi
- nyumba salama wasichana Arusha
- disability centre Hai / Siha / Sanya Juu / Machame
- Mkombozi Moshi current status
- Gabriella Rehabilitation Centre Moshi
- Emusoi Centre Arusha

## WebFetch log

### Fetched and used

**Sibusiso**
- tatotz.org Sibusiso listing and TATO NGO category page
- The 2024 annual report PDF on static.cbf.nl (text extracted with PyMuPDF)
- cbf.nl/organisaties/sibusiso

**URRC**
- rehabilitation-center-tanzania.org: home, /en/, /en/das-urrc/, /en/kontakt/ and the sitemap
- urrc.de
- feuerkinder.de

**Kafika House / The Plaster House**
- kafikahouse.org: home, /heal, /learn and /partner
- theplasterhouse.org: home, what-we-do-overview, contact-us and about-us-our-partners
- pflasterfuertansania.com/en/kafikahouse
- ProPublica record for EIN 851816030
- africanmissionhealthcare.org/the-plaster-house
- akphilanthropy.org/projects/kafika-house
- aaa.co.tz/kafikahouse
- ZoomTanzania Kafika House listing
- Afya directory Plaster House listing
- facebook.com/kafikahouse (only the page title was visible)

**Amani**
- amanikids.org: home, /contact-us, /our-approach, /our-projects, /team, /history, /news-events and /partners
- ProPublica record for EIN 273621599

**Albinism funders**
- underthesamesun.com: home and /education-support/
- standingvoice.org: home, /education and /contact

**Other pages checked, with no new specialised centre**
- Wikipedia: Usa River, Meru District; Comprehensive Community Based Rehabilitation Tanzania (CCBRT is hospital-based in Dar es Salaam and out of scope)
- Pack for a Purpose Tanzania page: lists lodges only, no named projects
- TATO NGO category: the only other NGO is a hyena research group (United Tansania e.V.)
- ZoomTanzania non-profit directory: no catchment child-welfare listings
- Afya directory Arusha NGO page: only The Plaster House

### Blocked or failed

| Source | Problem |
|---|---|
| sibusiso.com (/en/, /en/what-we-do/, /en/contact/, /en/the-sibusiso-center/, apex domain) | HTTP 403 |
| sibusiso.nl/doelstelling | HTTP 403 |
| vastenactie.nl Sibusiso-related project page | HTTP 403 |
| Charity Commission register (Friends of Amani UK, 1107618) | HTTP 403 |
| web.archive.org | Fetching not permitted |
| mkombozi.org | TLS error on www; empty response on the bare domain |
| gabriellacentre.org, emusoi.org (guessed domains) | DNS not found; nothing recorded |
| elct.or.tz | Expired certificate |
| arushacc.go.tz, moshimc.go.tz | JavaScript shell only ("GWF CORE"), no content |
| buildhealthinternational.org Kafika page | Timed out |
| amanikids.org/contact | 404 (/contact-us worked) |

Facebook and LinkedIn pages were not read, because of login walls.

## Gaps and leads not confirmed

**Mkombozi Centre for Street Children (Moshi, historically also Arusha).** This is a well-known lead. Its website could not be reached, and no fetched evidence was found, so no record was written. Confirm whether it still operates.

**Gabriella Rehabilitation Centre (Moshi)** and **Emusoi Centre (Arusha, for pastoralist girls).** These names come from the researcher's background knowledge, not from any source. The guessed domains did not resolve and nothing was recorded. Both need searches.

**Girls' rescue or safe houses in Arumeru.** None found. Amani's Safe House (girls aged 5–17) is the only rescue facility recorded, and its location is not published.

**Deaf, blind, autism and albinism centres.** No catchment centre was searched for or found. Government special schools and units would be out of scope in any case.

**Hai and Siha.** Not covered at all.

**Sibusiso:**
- Its own site blocks automated fetches, so the contacts rest on the TATO directory (dated 13 Jan 2025) and own-site search snippets.
- Whether it places children in mainstream schools is not published.
- A possible Vastenactie funding link was seen only as a search-result title. It was not recorded as a relationship.

**Amani:**
- The UK income figure is missing because the Charity Commission register returned 403.
- The Tanzanian charity number was transcribed from site text; its characters should be checked.

**Kafika House.** The Moshi house's exact location is not published, and no Tanzanian registration number was seen.

**Under The Same Sun and Standing Voice.** Both are national albinism funders that pay for school places, but no Arusha or Kilimanjaro caseload was found. They are recorded with catchment notes.

## Data-protection handling

- No child names, stories or images were recorded. Organisations' child-story pages are listed only as red flags.
- Street addresses of the Dutch Sibusiso arm and of Amani's UK, Dutch and German support offices were withheld, as they may be private homes.
- Dutch board-member lists were not recorded. Only published operational roles were.
- Named staff are labelled `medium`. The Friends of Amani UK gmail mailbox is labelled `risky`.
- Named people were never linked to role mailboxes that came from different sources.
