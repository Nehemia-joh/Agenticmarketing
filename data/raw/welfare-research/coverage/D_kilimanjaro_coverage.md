# Slice D — Kilimanjaro side: coverage log

Run `arusha-welfare-2026-09` · Slice D (Boma Ng'ombe/Hai, Siha, Moshi town and western Moshi rural) · Research 2026-09-22 (work ran past midnight into 2026-09-23; all `accessed_on` values use the run date 2026-09-22) · Tools: WebSearch and WebFetch only. I used no browser, did not sign in, submitted no forms and contacted no one.

## Record counts

| Record type | Count |
|---|---|
| organisation | 43 |
| contact | 32 |
| relationship | 36 |
| **Total lines** | **111** (all parse as JSON; validated with a Python check of keys, enums, cross-references and excerpt length) |

The 43 organisations by segment: 16 welfare residential care, 10 welfare family-based programmes, 7 welfare specialised centres, 9 welfare funders and 1 out of scope.

Verification status across all 111 records: 70 verified, 26 needs_review, 10 historical and 5 unverified.

PDPA risk across all records: 60 low, 50 medium and 1 risky. The risky record is Kilimanjaro Children's Fund, because its published contact email is a personal yahoo address.

Sources cited: 232 were fetched and read; 20 come from search snippets or search results only (`fetched: false`).

## Important limitation: the search budget ran out

The session-wide WebSearch cap is 200 calls, shared with the other slice agents. It was used up after my 37th query. The 38th query was refused with "session has used its web search budget". As a result:

- **The stopping rule was not met.** New institutions were still turning up in the last queries (Gabriella, Born to Learn, KWIECO and Kitaa details). There was never a run of 12 empty queries.
- After that I used WebFetch only. I fetched pages already found, followed links on those pages, and checked registers (ProPublica, NGO Explorer). I did not use search engines through WebFetch.
- More searching needs `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` to be raised, or a new session. The localities still to search are listed under Gaps below.

## WebSearch queries (37 run, 1 refused)

| # | Query | New institutions in slice |
|---|---|---|
| 1 | Mkombozi Centre for Street Children Moshi | Mkombozi; Kilimanjaro Centre for Orphans & Street Children; Msamaria; Amani |
| 2 | Amani Centre for Street Children Moshi Tanzania | Amani (confirmed); Friends of Amani UK |
| 3 | KIWAKKUKI Moshi orphans vulnerable children | KIWAKKUKI; Rainbow Centre (Catholic Diocese of Moshi) |
| 4 | KILI VIKINGS LIMITED orphanage support over 200 children | Kili Vikings claim; Kili Kids; Kilimanjaro Children's Fund; Kili Centre |
| 5 | site:kilivikings.com orphanage | none; no orphanage named |
| 6 | "Kili Vikings" orphanage Moshi children donation | Tuleeni; Kilimanjaro Orphanage Centre; COKO |
| 7 | Kilimanjaro Children's Fund Pasua orphanage Moshi name | Moshi Kids Centre; Kilimanjaro Children's Foundation |
| 8 | orphanage Moshi Tanzania children's home | Treasures of Africa; Upendo; Hope Home Trust / Kitaa; Halima; Hope Village |
| 9 | orphanage Boma Ng'ombe Hai Kilimanjaro | **Kao La Amani / Tír na nÓg (Boma Ng'ombe)** |
| 10 | orphanage Machame Tanzania children's home | Rosemary Project (Machame funder); Samaritan Village (Arusha, not this slice) |
| 11 | children's home Sanya Juu Siha orphanage | none |
| 12 | kituo cha kulelea watoto yatima Moshi | none in slice (results for Dar, Mara and Songwe) |
| 13 | "Tír na nÓg" Children's Foundation Tanzania Kao La Amani Boma Ng'ombe | Article 25 village and school pages |
| 14 | Kao La Amani school Boma Ng'ombe Hai primary school English medium | Aim Hai Pre & Primary (out of scope) |
| 15 | street children centre Moshi Kilimanjaro NGO | KCYC (Soweto); Kilimanjaro Childlight; Mshikamano |
| 16 | makao ya watoto yatima Kilimanjaro Hai | none in slice |
| 17 | volunteer orphanage Moshi Tanzania | Light in Africa (mention); volunteer agencies |
| 18 | orphanage Hai district Kilimanjaro Tanzania | none new (COKO shown at Uru) |
| 19 | Kilimanjaro Children and Youth Centre KCYC Soweto Moshi | TAG Kilimanjaro Revival Temple centre (Daily News) |
| 20 | Light in Africa Moshi children's home Lyn Cole | Light in Africa |
| 21 | World Unite Moshi orphanage street children placement partner projects | Bahath Orphanage; Tuleeni Academy |
| 22 | Rosemary Project Machame orphanage Lynn | **Light in Africa "Tudor House" at Boma Ng'ombe** |
| 23 | "Light in Africa" Boma Ng'ombe OR Bomang'ombe children's home Tudor House | Tudor Village details |
| 24 | "Tudor Village" "Light in Africa" Tanzania | Tudor Village in Hai district |
| 25 | "Light in Africa" Tanzania NGO children's homes Kilimanjaro contact email | none new |
| 26 | Bahath Orphanage Children's Home Moshi Usherika | Bahath details; Halima listed in Arusha on Idealist |
| 27 | Upendo Children's Home Moshi Precious Blood Sisters Shanty Town | UPENDO: One Kid at a Time |
| 28 | Mkombozi Centre Street Children Moshi Kiboriloni residential 2025 | none new |
| 29 | Mkombozi Moshi street children NGO 2024 OR 2025 OR 2026 | none new |
| 30 | "Kitaa Hope" children home Moshi Kilimanjaro International Tanzania Aid Agency | Child Hope Development Organization |
| 31 | Children of Kilimanjaro Orphanage COKO Uru Moshi new facility | none new (COKO details) |
| 32 | Compassion International child development centre Moshi Hai Tanzania church TZ | Compassion International Tanzania |
| 33 | Gabriella Children Rehabilitation Centre Moshi disabilities | Gabriella Centre |
| 34 | children with disabilities centre Moshi Kilimanjaro NGO rehabilitation | CCBRT Moshi (hospital, out of scope; not recorded) |
| 35 | school fees sponsorship programme Moshi Kilimanjaro vulnerable children NGO | Born to Learn; ZARA charity; KMHO; Tuleeni's school fee list |
| 36 | safe house girls Moshi Kilimanjaro rescue centre | KWIECO shelter |
| 37 | KWIECO shelter Moshi women children Kilimanjaro Women Information Exchange | none new (KWIECO details) |
| 38 | Gabriella Children's Rehabilitation Centre Moshi website contact gabriellacentre | **REFUSED — session search budget exhausted** |

## Pages fetched with WebFetch

Pages I fetched and read (`fetched: true`), grouped by institution:

- **Kao La Amani / Tír na nÓg:** tirnanogchildrensfoundation.com home, /about, /contact and /news. Also Article 25's village page, school page, Jan 2026 progress news and village update.
- **Light in Africa:** lightinafricachildrenshomes.com (twice), onekindact.org charity/light-in-africa, charity/54 and the 2015 interview. Also arpanglobal Mission 16 (2014) and the Euromic act of kindness (2023). The hopeministries.co post had no facts.
- **Tuleeni:** home, about, contact, our-projects, sponsor-a-child (twice, second time to confirm the school fee table), where-the-money-goes, quality-education portfolio, become-a-volunteer and friends-of-tuleeni. ProPublica for The Faraji Foundation (EIN 46-1300200).
- **Amani:** home, contact-us, our-projects, team, history, volunteer, partners, financials and news-events. Also NGO Explorer 1107618, ProPublica 27-3621599, the Idealist profile and Embrace Relief.
- **Kitaa Hope Home / Hope Home Trust:** home, childrenshome, history, education, meetthestaff, orphansintanzania and contactus. NGO Explorer 1126415.
- **Msamaria:** home, /about and /program. Also the Tanzania Volunteers Msamaria page and a Tripadvisor forum thread from about 2013.
- **COKO:** home, facility, volunteer and the Sep 2025 news post. Greenfield Recorder article (3 Jan 2026).
- **KIWAKKUKI:** vulnerable-children page, about page and home.
- **Born to Learn:** home page.
- **Moshi Kids Centre / ZARA:** home, about-us and top-ngos pages. Tanzania Times (1 Jul 2026) and the zaratanzaniacharity.org home page.
- **Kilimanjaro Orphanage Centre:** home (twice), Thirdeyemom (2015) and the trip-drop listing.
- **Kilimanjaro Children's Fund:** home (twice) and news. ProPublica 27-1426013.
- **Kilimanjaro Children's Foundation:** home (twice), about, contact, place-people and programs. ProPublica 36-4592181.
- **Upendo / OKAT / KMHO:** CCS Rau blog home and its Upendo post (2007). Tanzania Volunteers Upendo page. kmho.org home and sponsorship page (twice). upendookat.com home and about (twice).
- **Rainbow Centre:** rainbow-centre.blogspot.com (last post 2010).
- **Gabriella / BCC:** Tanzania Volunteers home, Gabriella page and BCC page.
- **Compassion and TAG Kilimanjaro Revival Temple:** Daily News and allAfrica (Sep 2026). cit.or.tz who-we-are and contact.
- **Hope Village:** pathtoafrica.org hope_village_orphanage, home and contact.
- **Treasures of Africa:** about, home (twice) and contact-us. Altezza Travel article (2021).
- **Halima:** home, about and contact. Idealist Arusha listing.
- **Other Moshi organisations:**
  - mshikamanoorphanage.com home.
  - kilimanjarochildlight.org home, about-us and volunteers.
  - childhopetz.org home.
  - neemainternational.org (worked over http after two socket errors).
  - Idealist Kili Centre and Mkombozi profiles, and the CRIN Mkombozi archive entry.
  - NGO Explorer 1101318 (Friends of Mkombozi).
  - ilivetotravel (Kili Centre) and hostelhoffmoshi (Kili Kids, 2014).
  - GoGetFunding Kili Kids (2017) and the Ukumbi KWIECO project page.
- **Kili Vikings:** about-us, contact-us and testimonial pages.
- **Other pages:**
  - ngobase Tanzania orphanages list and Kilimanjaro-region filter (0 results).
  - Volunteer agency pages: IFRE, New Hope and RCDP. None names any orphanage.
  - Michuzi May 2026 article (about Dar es Salaam, not relevant).
  - A GoFundMe from 2016: organisation-level facts only, and nothing recorded because it describes family circumstances.
  - aimhaischool.wordpress.com background page.

## Blocked or failed fetches

| URL | Result |
|---|---|
| kilicentre.org, www.kcyc.or.tz, kcyc.or.tz, www.kilimanjaro-children.org, www.gabriellacentre.org (guessed) | DNS: domain not found |
| www.mkombozi.org / mkombozi.org | TLS error / empty page |
| www.rosemaryproject.com (orphanage, contact) | Certificate mismatch (relied on search snippet, `fetched: false`) |
| world-unite.de (both hosts), register-of-charities.charitycommission.gov.uk (two charities), charitiesregulator.ie, archello.com, globalgiving.org (two pages), mabumbe.com, bellinghambulletin.com | 403 Forbidden |
| Several guessed or old subpages: msamariakids.org/about.html and contact.html; tirnanog /boma-ngombe-tanzania, /new-beginnings, /existing-home and /projects; hopehometrust /Policies; amanikids /about; tuleenihome /about-us/; kilimanjaroorphanagecentre /about-us/ and /contact-us/; kili-childrensfund /about; mshikamano /about; treasuresofafrica /contact; gocampaign article; autismconnect; lightinafrica.org; alightinafrica.com; lightinafricachildrenshomes /contact; ngoexplorer 1160116; tanzaniavolunteers old Gabriella URL; numadi.com | 404 |
| www.kwieco.org (guessed) | Connection reset (not recorded as a confirmed site) |
| elimumwangaza.org | 301 redirect to an unrelated gambling domain (not followed) |
| haidc.go.tz, moshimc.go.tz | JavaScript shell only ("GWF CORE"), no content |
| Segal Family Foundation Gabriella page | Returned an image only |
| All Facebook, Instagram and LinkedIn pages | Not fetched: login wall and brief exclusion. URLs are recorded only from search results or from links on the organisations' own sites |

## Outcome of the seed checks

- **Mkombozi Centre for Street Children:** confirmed as a historical Moshi street-children NGO (PO Box 9601; Idealist profile from 2012). Its website fails, and the UK support charity's latest accounts are from 2013. Recorded as `historical`.
- **Amani Centre for Street Children / Amani Children's Home:** confirmed and active (news dated March 2026). It has US, UK and NL support arms, with register data for US and UK. Recorded as `verified`.
- **KIWAKKUKI:** confirmed. Its vulnerable-children programme sponsors schooling from primary through secondary and vocational training. Recorded as `verified`.
- **KILI VIKINGS "over 200 children":** the about, contact and testimonial pages on kilivikings.com name no orphanage, and no other page on the site does either. Recorded as a funder with the red flag "beneficiaries not named". Searches for the claim turned up Kili Kids (Maili Sita) and Kili Centre. Neither is shown to be linked to Kili Vikings.

## Localities

- **Covered with a direct query or a confirmed record:**
  - Boma Ng'ombe (Kao La Amani, Light in Africa's Tudor House, Aim Hai).
  - Hai District (Tudor Village) and Machame (Rosemary Project, historical).
  - Sanya Juu/Siha (no institution found).
  - Moshi town: Pasua, Shanty Town, Rau, Soweto, Kaloleni, Korongoni, Majengo (only as a preschool mention).
  - Uru, Uru West and Uru Kusini; TPC (Moshi Rural); Maili Sita.
- **Not searched individually** (the budget ran out): Masama, Narumu, Weruweru, Mnadani, Rundugai, KIA area, Kwa Sadala, Lyamungo, Kibosho, Mabogini, Kiboriloni, Njoro, Karanga and Longuo. Kiswahili queries were run for only two phrasings. None of the farther east/south places (Himo, Marangu, Rombo, Same) were searched.

## Gaps and leads I could not confirm

- **Light in Africa (Tudor Village, Hai):** strongest near-campus lead after Kao La Amani, but there is no official contact route. Child numbers and locations conflict (Tudor Village vs Mererani), and the exact village is unconfirmed. Coordinates only exist on a Google My Maps link, which I did not fetch.
- **OKAT Children's Home:** the location is unpublished. It holds school-age children (5+) moved on from Upendo, so it may be a good lead if it is in Moshi.
- **Kilimanjaro Children's Fund:** the Pasua home's name is unpublished and may be Kilimanjaro Orphanage Centre. Its published contact email is a personal yahoo address.
- **Gabriella Centre and BCC:** no own websites found. BCC's 10 centre locations are unpublished.
- **KCYC (Soweto):** its website no longer resolves, so the facts come from snippets only.
- **Bahath Orphanage:** facts come from snippets only (the World Unite page is blocked).
- **Halima Orphanage Center:** conflicting location (Moshi vs Arusha), founding date and size.
- **Compassion International:** the partner church centres in Moshi and Hai are not listed publicly. Only TAG Kilimanjaro Revival Temple was found.
- **Facebook-only groups:** any in Hai or Siha could not be seen.
- **Tanzanian registration:** numbers were published by only a few organisations (Amani, KIWAKKUKI, Kilimanjaro Childlight, Compassion, and KCYC via snippet). The national NGO register was not queried because it needs form input.

## Found but not recorded as records (out of scope or outside the slice)

- **Out of scope in or near the slice:**
  - CCBRT Moshi (hospital rehabilitation).
  - Moshi juvenile detention centre (Mahabusu ya Watoto; government retention home).
  - Rau Daycare Center and Majengo Preschool (daycare and preschool).
  - Eden Garden Primary, Ebenezer Education Trust Primary and the other private and public schools in Tuleeni's fee table (general schools). These are competitor intelligence only.
- **Outside the slice:** Samaritan Village Orphanage (Arusha), Neema Village (Arusha), Malaika Kids (Dar es Salaam), Maasai Girls Rescue Center (Karatu), and Watoto Wetu and Norca Upendo (Dar es Salaam).

## How personal data was handled

- No child names, photos, stories, health or HIV data, or family circumstances are recorded. Programme counts are kept at organisation level.
- I deliberately left out these personal routes or addresses:
  - a volunteer's personal email in Light in Africa site comments;
  - a personal yahoo address on the trip-drop listing;
  - Amani's UK chapter gmail and a named US staff email;
  - a US school club teacher's email and a Neema staff email (both shown on Tuleeni's partner page);
  - the founders' personal LinkedIn (Tuleeni) and Facebook (Msamaria) profiles linked from those organisations' own sites;
  - UK and Irish street addresses that may be private homes (recorded only as the town);
  - board and trustee lists.
- Contact records are limited to role desks and to named people in professional roles, as published by the organisation, a funder or the press. Each is labelled with a PDPA risk.
