# Slice E: family-based programmes, coverage log

Run: `arusha-welfare-2026-09` · Slice E (family-based programmes: Arusha city, Arumeru/Meru, Hai, Siha, Moshi) · Research date: 2026-09-22
Records: `E_family_programmes.jsonl` (86 lines; every line parses as JSON, checked with Python)

## Status: stopping rule NOT met

- **WebSearch was cut off after 13 queries.** The session-wide cap (200 of 200 WebSearch calls, shared with the other research agents) was reached. Queries 14 and 15 were refused. The last 13 successful queries still produced new organisations, so the rule of "12 consecutive queries with no new organisation" was never reached.
- **No Kiswahili queries were run.** All planned Kiswahili queries were blocked, including "ufadhili wa elimu Arusha", "mfadhili ada shule Arusha NGO" and "watoto wanaoishi katika mazingira hatarishi Arusha NGO".
- **What I did instead:** about 90 WebFetch calls, used only on URLs already found in search results, links on fetched pages, official registers (ABN Lookup), and a few official sites I knew about already (TFFT, KIWAKKUKI, Amanikids; fetched to verify). I did not fetch any search-engine results pages and did not use a site's search box to discover organisations.
- **No other restricted actions.** No browser tools, sign-ins, form submissions or contact with anyone.
- **To finish this slice:** raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and rerun the search phase (see Gaps).

## Records written

| Record type | Count | Verification | PDPA risk |
|---|---|---|---|
| organisation | 29 | verified 12 · needs_review 14 · unverified 1 · historical 2 | low 17 · medium 12 |
| contact | 29 | verified 19 · needs_review 9 · unverified 1 | low 5 · medium 22 · risky 2 |
| relationship | 28 | verified 15 · needs_review 11 · historical 2 | low 28 |

Organisations by segment:
- Welfare family-based programme: 14
- Welfare residential care: 8 (incidental or funder-linked; these overlap slice A)
- Welfare funder: 5
- Welfare specialised centre: 1 (Amani, which overlaps slice C)
- Out of scope: 1 (Renea Pre and Primary School, a competitor school that receives sponsored pupils)

Sources: 73 distinct URLs fetched and read today, plus 4 used from search snippets only (`fetched: false`).

## Query log (WebSearch)

| # | Query | Result | New organisations |
|---|---|---|---|
| 1 | SOS Children's Villages Arusha family strengthening programme | ok | SOS Children's Village Arusha |
| 2 | Compassion International Tanzania child development centre Arusha church partner | ok | Compassion International Tanzania |
| 3 | child sponsorship Arusha school fees charity | ok | Arusha Kids Trust, Sunrise Hope for Foundation, Selfless Solutions, WEHAF, Tanzania School Foundation, Arusha Kids/Fruitful Orphanage, Arusha Children's Effort, Inuka |
| 4 | "Arusha Kids Trust" OR "Save Africa Orphanage" Arusha | ok | Save Africa Orphanage, Ummu Aisha Orphanage Centre; also Enjiva and Faraja orphanages (unreachable) |
| 5 | Arusha Kids Trust ACNC charity register ABN | ok | none |
| 6 | "Selfless Solutions" Tanzania Sing'isi nursery school Renea | ok | Renea school (out of scope); help2kids (Dar es Salaam, not recorded) |
| 7 | "Father Christmas Academy" Tanzania | ok | none (Tanzania School Foundation details) |
| 8 | "Tanzania School Foundation" Father Christmas Academy close 2022 students scholarships schools Arusha | ok | none |
| 9 | "Sunrise for Hope" OR "Sunrise Hope for Foundation" Arusha sponsorship primary school | ok | Good Hope Orphanage School & Clinic, Espero Foundation |
| 10 | education sponsorship Arusha primary school private English medium sponsor children charity | ok | Moshi Kids Centre, Afroplan Foundation; Aruna Partnership (India, not recorded) |
| 11 | Afroplan Foundation Tanzania sponsorship program children school | ok | Passion Projects International |
| 12 | sponsor a child Usa River Tanzania school fees charity | ok | Ngarasero Community Organization, Tanzanian Children's Fund; Waterfall Charity and Chalice (not recorded, see below) |
| 13 | "Mesha's Village" Tanzania Usa River Ngarasero | ok | Mesha's Village |
| 14 | orphans and vulnerable children programme Arusha NGO school fees | **refused (budget)** | none |
| 15 | OVC programme Moshi NGO orphans school fees Kilimanjaro | **refused (budget)** | none |

Organisations found through links on fetched pages (not through search): Heart for Africa, New Paradiso Orphanage, Bethlehem Center for Children, GP-COSU (all from Heart for Africa's site, which appeared in search results), and CHETI NGO (from Inuka's site). The Foundation For Tomorrow, KIWAKKUKI and Amani Centre were fetched directly from sites I already knew about and confirmed on their own pages.

## Sources fetched (WebFetch, 2026-09-22)

- **Compassion International Tanzania**
  - cit.or.tz: home, who-we-are, contact, where-we-work, education page, annual-reports, annual-report-2025 download page (the PDF itself was not readable)
  - compassion.com Tanzania facts
  - Daily News article, 25 Mar 2026
  - ZoomTanzania directory entry
- **SOS Arusha:** sos-childrensvillages.org (Arusha and Tanzania pages), sos-usa.org, soschildrensvillages.ca, offline Wikipedia copy (solarspell)
- **Selfless Solutions:** sponsor page, home, contact; MIT Solve profile; school.co.tz profile for Renea
- **The Foundation For Tomorrow:** home, contact-us, investing-in-students, sponsorship, news-and-reports, impact, who-we-are
- **Amani Centre for Street Children:** amanikids.org home, contact-us, our-approach
- **KIWAKKUKI:** home, vulnerable-children page, annual-reports page (no reports listed)
- **Arusha Kids Trust:** home, about-us, school-sponsorship, contact-us, news-events; ABN Lookup (name search and ABN 84 395 724 644)
- **Save Africa Orphanage:** weebly home, contact, volunteer pages
- **Arusha Children's Effort:** home, sponsorships, blog
- **Tanzania School Foundation:** home, sponsor-a-child; GuideStar 26-2523039; Patch article (2013)
- **WEHAF:** home, sponsor page
- **Inuka and CHETI NGO:** Inuka home, student-sponsorship, cheti-ngo, contact; ABN Lookup 96 836 629 276
- **Afroplan Foundation and Passion Projects International:** passionprojectsintl.com Afroplan and sponsorship pages; Africa Heart's Desire Afroplan page
- **Ngarasero Community Organization:** Tanzania Insight article (9 Sep 2026), Daily News article (Sep 2026), public Facebook page (name and category only)
- **Mesha's Village:** home, newsletters page (about); GuideStar 82-3424413
- **Heart for Africa:** home, orphanages, schools, people, news
- **Ummu Aisha Orphanage Centre:** home page
- **Moshi Kids Centre:** home, sponsor page
- **Others:**
  - Idealist listings for Espero Foundation and Good Hope Orphanage
  - arushakids.com (Fruitful Orphanage)
  - tanzanianchildrensfund.org sponsor page
  - chaliceus.org Tanzania page
  - waterfallcharity.org child-sponsor page
  - help2kids nursery-schools page
  - arunapartnership.org
  - tatuproject.org
  - ZoomTanzania Arusha location page (not useful: only 2 NGOs listed, and the rest loads through a "Load More" script)
  - Tanzania Insight related-articles list (nothing relevant)

## Blocked or failed

| URL or site | Problem |
|---|---|
| sunriseforhope.org (/ and /sponsorship/) | HTTP 522 three times; recorded from search snippet only |
| Charity Commission register (Heart for Africa 1173027) | HTTP 403 |
| mabumbe.com SOS vacancy page | HTTP 403 (title used from snippet only) |
| wvi.org/tanzania (World Vision) | HTTP 403 |
| acnc.gov.au charity search | timeout (ABN Lookup used instead) |
| mkombozi.org | SSL error, then empty page |
| umojacentre.org | connection refused |
| afroplanfoundation.com | no content, then connection reset |
| fruitfulorphanage.or.tz | expired certificate |
| fatherchristmasacademy.org, esperofoundationtz.org, goodhopeorphanage.org, enjivaiorphanage.org | domain does not resolve |
| farajaorphanage.org | title only, no body (location unknown; not recorded) |
| preciousproject.org/sponsorship, volunteerintanzania.com v4c page, idealist Flowers Charity page, pccfw.org Compassion church page | HTTP 404 |
| facebook.com/ngarasero | only name and category visible without login (nothing behind the login was used) |
| Compassion 2025 annual report | download page only; PDF content not readable |
| GuideStar financials | paywalled (only public programme expenses used) |

## Data withheld on purpose

- Child names, stories and profiles on sponsorship pages. One example: a named alumnus on the TFFT impact page.
- Group-level health or HIV information on KIWAKKUKI's children's page.
- Probable private or home addresses: the ACE director's New Zealand street address, and the street addresses of the Friends of Amani groups in the UK, Netherlands and Germany. For the Selfless Solutions US office, only the city is recorded.
- Personal gmail addresses of the volunteer web designers on arushakids.com.
- Names of the Save Africa Orphanage founders and director, the Good Hope founder, and the Fruitful Orphanage founder. No contact route was published for them.
- Principal officers listed on GuideStar (these come from regulator filings).
- Two contact records are marked risky: a named person's personal-domain email for ACE (vd@vinnie.co.nz) and a first-name gmail for WEHAF.

## Seen but not recorded (out of region or no catchment evidence)

- help2kids: campus in Dar es Salaam
- Aruna Partnership: India
- Chalice: its sponsor sites are Mbinga and "Neema", with no Arusha or Kilimanjaro evidence
- Waterfall Charity (UK 1140634): Tanzanian location not stated
- CORE Tanzania: Kagera
- LOHADA: Singida
- Village Africa and Children of Hope and Faith: location not stated
- Tatu Project: Msitu wa Tembo and Londoto; no education-fee programme evident
- Plan International and Charity and Hope: generic, not in the catchment
- Ebenezer Orphanage, Arusha: named only in Mesha's Village's origin story; no organisation facts

## Gaps and leads not confirmed

1. **Compassion church partner centres** in Arusha, Meru, Hai, Siha and Moshi are not publicly listed on the pages I could fetch. Finding them needs searches of church and centre Facebook pages and centre codes. The country office in Sekei, Arusha, is the fallback route.
2. **No organisations found in Hai or Siha districts**, and only 4 in Moshi (Amani, KIWAKKUKI, Moshi Kids Centre; also Tanzanian Children's Fund, which is probably outside the catchment). These need targeted searches, e.g. "Boma Ng'ombe", "Machame", "Sanya Juu", "Hai OVC".
3. **Kinship, foster-care and diocesan OVC programmes were not researched** because search was cut off. Examples: Caritas Arusha, Moshi Catholic Diocese, ELCT Northern and Meru dioceses, the Anglican Diocese of Mount Kilimanjaro, and council social-welfare foster care.
4. **Programmes from the USAID era** (e.g., Pact Kizazi Kipya) were not checked. Treat them as historical.
5. **SOS Arusha:** no local phone or email found, and no statement that its family-strengthening programme pays school fees.
6. **Tanzania School Foundation:** conflicting evidence on whether Father Christmas Academy closed after 2022, and on its village (Mlangarini or Olosiva).
7. **KIWAKKUKI and WEHAF:** no dated evidence that they are active; their pages have no dates or a 2022 copyright.
8. **Unreachable sites worth retrying:** Umoja Centre (Arusha, youth education), Mkombozi (Moshi and Arusha, street children with family reintegration), Sunrise for Hope, Afroplan's own site, Fruitful Orphanage.
9. **Private schools that already take sponsored pupils** (competitor intelligence; recorded only as relationships or notes):
   - Haradali Primary and Haradali Winners Secondary
   - Blue Sky Primary
   - Same Hill Primary
   - Maua English Medium School (Usa River)
   - Usa River Academy
   - Usa-River Rehabilitation Secondary
   - Renea (Njiro)
   - Shine School
