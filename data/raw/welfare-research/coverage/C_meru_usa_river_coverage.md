# Slice C coverage log: Meru District Council (Arumeru East), Usa River campus area

Run: `arusha-welfare-2026-09` · Slice C · Research date 2026-09-22 · Tools: WebSearch and WebFetch only. No browser, no sign-in, no forms, no contact with anyone.

## 1. Summary

| Record type | Count | verified | needs_review | historical | unverified |
|---|---|---|---|---|---|
| organisation | 32 | 12 | 13 | 5 | 2 |
| contact | 20 | 8 | 12 | 0 | 0 |
| relationship | 24 | 8 | 11 | 5 | 0 |
| **Total lines** | **76** | | | | |

The organisation records break down by segment as follows:

- Welfare residential care: 16 (includes the closed Cradle of Love and 4 historical homes)
- Welfare funder: 7
- Welfare family-based programme: 5
- Welfare specialised centre: 1
- Out of scope: 3 (Next Life Foundation, a vocational centre; Africa Hearts Desire, a volunteer company; IBES, a daycare chain)

PDPA labels:

- Organisations: 16 low and 16 medium.
- Contacts: 19 medium and 1 risky. The risky one is a Rotary funder contact with an ISP-domain email.
- Relationships: all low.

Validation: every line of `C_meru_usa_river.jsonl` parsed as JSON. Python checks also confirmed the allowed enum values, `slice` set to "C", at least one source per record, and evidence excerpts of 25 words or fewer.

### Constraint that limited coverage

The session-wide WebSearch budget ran out after my 26th search. The tool reported 200 of 200 calls used, a total shared across all agents. The message said to continue with gathered information. I did **not** route searches through another tool or site.

After that point, discovery used only WebFetch. I followed links on pages I had already found, read directory listings (ngobase profile links, partner pages, annual reports) and queried OpenStreetMap through the Overpass API. OSM was the data source named in the task seeds. **The stopping rule was not satisfied:** I could not run 12 consecutive empty queries, and several localities got no dedicated search (see §5). Raising `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and re-running the locality queries in §5 would close this gap.

## 2. Seeds: outcome

| Seed | Outcome |
|---|---|
| Cradle of Love Children's Home / Baby Home | Confirmed **closed**. Giving Smiles' 2024 report says the closure was announced in March 2024 and the children moved on 3 April 2024 to Falco's Children Village in Karatu (His Healing Hands Ministries), which is outside the catchment. The OSM node is at -3.3720770, 36.8386670, about 2.7 km west of the campus. Its successor, Child First Initiative, opened **Child First Baby Home in Usa River** in December 2024. |
| Next Life Foundation (nextlifefound.org) | A Christian vocational training centre in **Mbuguni** (tailoring and carpentry, tuition-free), US EIN 46-5588534. It has no children's residential care and no school-fee sponsorship. Recorded as Out of scope. |
| Usa-River Rehabilitation Centre | Confirmed. ELCT Meru Diocese, founded 1988, 70 boarding places for ages 16–25, and a Faraja primary-school programme for disabled children. OSM places it at -3.3748, 36.8430. The German funders (Förderverein URRC e.V., Mission EineWelt) are also recorded. |
| Nkoaranga | Confirmed **Nkoaranga Orphanage (Baby Home)**, owned by Nkoaranga Lutheran Hospital, caring for about 30 children aged 0–3/4. **The Small Things** is based in Nkoaranga village and runs **Happy Family Children's Village** and a family-preservation programme that pays school fees. |

## 3. WebSearch queries run (26 run, 1 refused)

| # | Query | New institutions in slice C |
|---|---|---|
| 1 | Cradle of Love Baby Home Usa River Arusha | Cradle of Love (closed); Giving Smiles link |
| 2 | Next Life Foundation nextlifefound.org Tanzania | Next Life Foundation (Mbuguni) |
| 3 | Usa River Rehabilitation Centre disabled children Arusha | URRC; Ngarasero (via Daily News article) |
| 4 | orphanage Usa River Tanzania | Jericho, Laketatu, POSA, Tabasamu, Save Africa, Tumaini, Enyorata/Little Souls, Sun of Hope |
| 5 | Giving Smiles e.V. Child First Initiative Tanzania Arusha | Child First Initiative |
| 6 | "Cradle of Love" baby home Arusha closed 2024 children moved | none new (confirmed closure) |
| 7 | Tabasamu orphanage Usa River | none new (Tabasamu details) |
| 8 | "Jericho" orphanage home Usa River Arusha | Fruitful (Duluti, via its jimdo site); Havilah lead; others outside the slice |
| 9 | "Canaan Children's Center" Arusha Catholic Archdiocese location | none (Kisongo, outside the slice) |
| 10 | "Fruitful Orphanage" Duluti Arusha | none new (Fruitful details, including its own school) |
| 11 | Neema Village baby home Arusha location village | none (Moivaro, outside the slice) |
| 12 | Tumaini Children's Foundation Usa River children's home Nshupu | none new (Nshupu home move, snippet) |
| 13 | "Enyorata" children's home Tanzania | none new (Maji ya Chai/Kitefu location; own school) |
| 14 | orphanage Tengeru Arusha children's home | none in the slice (Faraja, Samaritan, Ummu Aisha, Malaika: all Arusha city or unknown) |
| 15 | kituo cha kulelea watoto yatima Usa River (Swahili) | none (NTUC Adventist Facebook post, behind login) |
| 16 | Samaritan Village orphanage Arusha Tanzania village location Josephat | none (Moshono, outside the slice) |
| 17 | children's home Maji ya Chai Arusha | IBES daycare (out of scope) |
| 18 | orphanage Kikatiti OR King'ori Arusha Tanzania | ROAM Humanitarian's Kikatiti orphanage and school |
| 19 | ROAM Humanitarian orphanage Kikatiti Tanzania | none new |
| 20 | "ROAM Humanitarian" Tanzania orphanage Arusha boys dormitory school | none in the slice |
| 21 | "New Paradiso" orphanage Arusha | none (locality unknown) |
| 22 | "Bethlehem Center for Children" Arusha location | Havilah Children's Village (University of Arusha campus, Usa River) |
| 23 | Havilah orphanage University of Arusha Usa River | none new |
| 24 | Nkoaranga children's home orphanage | Nkoaranga Orphanage, The Small Things, Happy Family Children's Village |
| 25 | orphanage Arumeru district Arusha children's home | none in the slice (House of Happiness is in Kisongo) |
| 26 | "The Small Things" Happy Family Children's Village Tanzania Nkoaranga | none new |
| 27 | thesmallthings.org … school fees education sponsorship | **Not run: budget exhausted** |

## 4. Discovery and verification by WebFetch (after the search budget ran out)

Institutions found through link-following and data queries:

- **Afro Plan Foundation** (Usa River). It pays private-school tuition for sponsored children. Found via Africa Hearts Desire's partner list.
- **The Foundation for Tomorrow (TFFT)** learning centre at Magadirisho, Ndurumanga, Usa River. Found via a 2012 blog's partner list and then TFFT's own contact page.
- **Seeway Tanzania** (Usa River) and **Matonyak Children's Home** (Tengeru). Both are historical and appear only in a 2012 TFFT partner list.
- **Child First Baby Home** in Usa River. Found via the Giving Smiles project pages and its 2024 annual report.
- **KinderVilla / Momella Orphanage**, run by Africa Amini Alama. Found via OSM Overpass and then AAA's own site.

**OSM Overpass**, 3 calls:

- Call 1 (a regex name search) timed out with HTTP 504.
- Call 2 searched `amenity=social_facility|childcare|kindergarten` in the bbox -3.50, 36.77, -3.10, 37.10. It returned Momella Orphanage (operator Africa Amini Alama), St Bernard nursery, and one unnamed childcare and one unnamed kindergarten.
- Call 3 was a name regex in the bbox -3.48, 36.77, -3.12, 37.08. It returned:
  - Cradle of Love (node 6233240290)
  - Usa-River Rehabilitation Centre (node 7217814678)
  - **"Usa River Children Center"** (way 273457802, -3.3764130, 36.8534324, tagged only as a building and not identified)
  - Momella Orphanage (way 528955936)
  - Watoto Momella Nursery (way 528955939; school; operator "The African Embassy")

**Documents extracted locally** after WebFetch saved the PDF:

- Giving Smiles e.V. 2024 annual report: income EUR 109,074.27; TZS 44m on sponsorships for 40 children, 90% of it school costs.
- TFFT 2024 Form 990: revenue US$1,056,111, expenses US$901,272, 97 scholarship children.

### Pages fetched and read (fetched: true)

- **Giving Smiles:** `/en/cradle-of-love-baby-home/`, `/en/`, `/impressum/`, `/jahresberichte/`, the 2024 report PDF, `/en/child-first-baby-home-2/`, plus the Gily's, Miles of Smile, Furahia, Pamoja Tunalea, Jitambue and Nanc's project pages. Those last six are outside the slice or have no locality.
- **CFI:** home, `/about/`, `/contact`, `/programs/6`, `/programs/7`, `/programs/8`.
- **URRC:** home, `/en/`, contact, `/en/das-urrc/`, `/en/aktivitaeten/`; urrc.de; Wikipedia's Usa River page.
- **Ngarasero:** Daily News and Tanzania Insight (2026-09-09).
- **Laketatu:** Papamoa Rotary Club page.
- **Tumaini:** `/about-tumaini/`, home, `/news/`; CanadaHelps.
- **Enyorata and Little Souls:** littlesoulsoftz home and `/about-us/`; eBay for Charity; misoadventures; 2 GoFundMe pages. These pages were used for organisation facts only; private organisers are not recorded.
- **Save Africa:** weebly site; Volunteer in the World (2020).
- **Tabasamu:** home, `/about/`, `/contact-us/`; Idealist.
- **Jericho:** Facebook (title only, behind login); Idealist (2013).
- **POSA:** 2019 volunteer blog.
- **Fruitful:** jimdo site, 2 WordPress sites, VOA (2024-02-17).
- **Havilah / Global Vessels:** weebly about, contact and home pages; globalvessels `/orphanage/` and home.
- **Nkoaranga / TST:** nkoarangahospital page-7; AHD Nkoaranga page; Fathom (2017); Mightycause; Lift the Lid; thesmallthings.org (no content rendered).
- **AHD:** home, links page, afroplanfoundation page, fees page, about page; afroplanfoundation.com (no content).
- **TFFT:** home, contact-us, who-we-are, news-and-reports, 2024 Form 990; debsphotographs 2012 blog.
- **AAA:** home, `/projekte/soziales`, `/projekte/bildung`, `/kontakt`, `/ueber-uns/impressum`, `/aktuelles/news`.
- **ROAM:** home, the Tanzania expedition page, GuideStar; Water for Life (Kikatiti well); Heber Valley Life (2025-12-12).
- **Out of scope:** Next Life home; GuideStar; ibes.co.tz.
- **Outside the slice, read while checking locality:** canaanchildrenscenter home and contact; samaritanvillageorphanage; neemavillage; hopecentertanzania; malaika family-home and contacts; stepbystep; servingorphans; bahatitrust; embracerelief ×2; heartforafrica; becechi.wixsite; idealist (Halima, Upendo Face, Beyond Child Smile); houseofhappiness.ch; e-ducare Karim; ummuaishaorphanage; ngobase lists (2 pages) and profiles 24648, 316196, 316195, 301181; childrenconcern.or.tz; lebaoskidsfoundation; lovefortheleast; naturaltrekking 2013; havilahorphanagehome.org (Nigeria, unrelated).

### Blocked or failed

- **Login wall:** Facebook, Jericho page (title only). Other Facebook pages were not attempted.
- **HTTP 403:**
  - UK Charity Commission register, charity 1157470 (The Small Things UK)
  - tz.profdir (Jericho)
  - ZoomInfo
  - GoOverseas
- **Not fetchable by the tool:** web.archive.org.
- **TLS errors:**
  - theholyspiritsisters.org (Sun of Hope; http and https)
  - fruitfulorphanage.or.tz (certificate expired)
  - envaya.org/fruitfulorphanage (certificate expired)
- **Connection refused or reset:** cradleoflove.com (refused), afroplanfoundation.com (reset on the first try; no content on the second).
- **DNS failure:**
  - jerichome.org and jerichome.or.tz (dead website)
  - enjivaiorphanage.org
  - seewaytanzania.org (a guessed domain; not recorded)
- **404 Not Found:**
  - volunteerintanzania.com Cradle page
  - childrenofafrica.asso.mc day-care page
  - Tumaini 2019 annual report PDF, portfolio page and `/feed/`
  - lavha.com SUCARE page
  - Idealist Tabasamu volunteer listing (VolunteerMatch redirect)
- **Too large:** TFFT 2024 annual report PDF (over 10 MB).
- **Overpass:** first query timed out (504).

## 5. Locality coverage and gaps

| Locality | Status |
|---|---|
| Usa River | Well covered: 15+ institutions |
| Tengeru | Searched once; only the historical Matonyak home found |
| Maji ya Chai | Searched; Enyorata found (plus IBES daycare) |
| Kikatiti, King'ori | One combined search; ROAM's Kikatiti orphanage found (name not published) |
| Nkoaranga | Searched; Nkoaranga Orphanage, TST, HFCV found |
| Duluti | Fruitful found by chance; no dedicated search |
| Momela, Ngabobo | OSM and AAA pages; KinderVilla found; CFI literacy class in Ngabobo |
| Mbuguni | Next Life (out of scope) found by seed; no dedicated search |
| **Not specifically searched** (budget exhausted) | Leguruki, Ngarenanyuki, Poli (only the Nshupu snippet), Akheri, Patandi, Seela Sing'isi, Makiba, Nkwanrua, Songoro, Kikwe, Imbaseni, Maroroni, Malula, Karangai, Ambureni, Leganga, Kisimiri, Nkoanekoli, Kilinga, Uwiro, Majengo |
| Swahili queries | Only 1 run. "makao ya watoto Meru Arusha", "kituo cha watoto yatima Tengeru / Maji ya Chai" and similar were not run |

### Unconfirmed leads and open questions

- **"Usa River Children Center"** (OSM way 273457802, -3.3764, 36.8534). This is about 1 km from the Silverleaf Usa River campus and not identified. It could be one of the known Usa River homes.
- **ROAM Humanitarian's Kikatiti orphanage, school and community centre.** The local partner's name is not published. Contact route: the expedition leaders' published number.
- **Sun of Hope Village/Orphanage** (Holy Spirit Sisters, Usa River, 21 children in 2015). Known only from a snippet; the site has a TLS error.
- **Jericho Orphanage Home.** Facebook only; website dead; Usa River and Karatu addresses conflict.
- **The Small Things.** No dated activity found after 2017; UK income not retrieved (register 403); site content did not render.
- **TFFT.** Check whether its scholarships cover primary or English-medium placements; the 2024 annual report was too large to fetch.
- **Tumaini.** The move of the home to Nshupu is snippet-only; the number of children resident now is not published.
- **Laketatu.** The article date is not shown on the page.
- **Afro Plan Foundation.** Contact is only through Africa Hearts Desire, and the currency of its information is unknown (AHD site © 2020).
- **Historical only:** Seeway Tanzania and Matonyak (2012), POSA (2019), Save Africa (2020).
- **Seen but not recorded** (schools or nurseries, out of scope):
  - Watoto Momella Nursery (OSM; operator "The African Embassy")
  - St Bernard nursery (OSM, -3.1853, 37.0036)
  - Young Roses Pre- and Primary School and Usa River Primary School (AHD placements)
  - School of St Jude Usa River campus and Kennedy House International School (Wikipedia)
  - Gily's Daycare second site in "Shangarai" (locality unclear; free daycare)
  - Furahia Mtoto Foundation daycare (locality not given)
- **Behind login, not viewed:** a Facebook post by NTUC Adventist about disabled children at an Usa River centre.

## 6. Found outside slice C, handed off and not recorded

These are listed for the agents covering the right slice.

**Arusha City and Arusha DC:**

- Canaan Children's Center, Kisongo (Catholic Archdiocese; 39 children)
- Samaritan Village Orphanage, Moshono
- Neema Village, Moivaro
- Hope Orphanage Center, Ngaramtoni
- House of Happiness, Kisongo (about 50 children; Swiss association)
- **Pamoja Tunalea Daycare, Moshono.** A Giving Smiles project that sponsors children into English-language primary schools, about 15 leavers a year. A strong lead for the Arusha City campuses.
- Ummu Aisha Orphanage Center (Arusha city; licence 06422)
- Orphanage Halima Selengiya (Simeon Rd)
- Upendo Face Orphanage (Olturoto Rd)
- Bethlehem Center for Children (PO Box 1597 Arusha; Heart for Africa UK, charity 1173027, pays education costs)
- New Paradiso Orphanage (Heart for Africa)
- Karim Orphanage (E-ducare)
- Malaika Children's Friends (Italy; PO Box 1708 Arusha)
- Beyond Child Smile (Ilboru)
- Miles of Smile daycare (Kwa Maretu)

**Arusha, locality not found:** Faraja Orphanage Children's Home, Chakuwama/Lukiza, Ummah Charity and One Ummah, Tumaini House (YWAM), Huruma Orphanage, SUCARE, Living Water Children Centre, Enjivai Orphanage, Gily's Daycare (Giving Smiles).

**Moshi:** Amani Orphanage (Embrace Relief).

**Outside the 25 km catchment:**

- Falco's Children Village, Karatu (received the Cradle of Love children)
- Children Concern Foundation, Mto wa Mbu
- Le Baos Kids Foundation, Iringa
- Step by Step / Mafiri, Morogoro
- Bahati Trust and Hiari Orphanage, Dar es Salaam

## 7. Data-protection handling

- No child names, photographs, ages linked to identities, stories or health information were recorded. Organisation-level counts were paraphrased.
- Personal circumstances of founders mentioned in some sources were not recorded.
- Board or trustee lists (Giving Smiles Vorstand, Little Souls board) were not recorded.
- US and German street addresses that may be residential were reduced to city level.
- Private GoFundMe organisers were not recorded.
- The one ISP-domain email of a named funder contact is labelled `risky`.
