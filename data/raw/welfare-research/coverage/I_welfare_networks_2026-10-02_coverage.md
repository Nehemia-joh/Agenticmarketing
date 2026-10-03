# Slice I - welfare networks (introducers) - coverage log

Research date 2026-10-02 (the brief fixes the date; some pages were read just after midnight, on 2026-10-03 local time). No targets file: the task was to find bodies that could introduce Silverleaf to many homes and programmes at once.
Output: `data/raw/welfare-research/research_I_welfare_networks_2026-10-02.jsonl`. All 36 lines parse as JSON, and every record has `"slice": "I"`.

## Records written

| Type | Count |
|---|---|
| organisation (segment "Welfare network (introducer)", care_model "network") | 7 |
| contact | 22 |
| relationship | 7 |

Organisations:

- Arusha NGO Network (ANGONET). The name matches the existing record. About 100 member CSOs. The member list is not online.
- Christian Social Services Commission (CSSC). National. The Northern Zone office is in Arusha, but no address is given.
- Tanzania Child Rights Forum (TCRF). National. The published member list has two Arusha members.
- ELCT Northern Diocese (Moshi). Its Diaconal department runs Kalali Orphanage, Faraja Diaconic Centre (Sanya Juu) and BCC.
- ELCT North Central Diocese (Arusha). Its Udiakonia unit runs an orphans-and-widows service through its parishes. It also has a Children's unit coordinator.
- ELCT Meru Diocese (Usa River). Marked needs_review because its details come from a partly stale ELCT directory. It operates the Usa River Rehabilitation and Training Centre (URRC).
- Catholic Archdiocese of Arusha. Marked needs_review. It founded and runs Canaan Children's Center.

Relationships:

- TCRF partners_with WOMEN AND CHILD VISION (WOCHIVI)
- TCRF partners_with Centre for Women and Children Development (CWCD). CWCD is new and is not a home.
- ELCT Northern Diocese operates Kalali Orphanage
- ELCT Northern Diocese operates Faraja Diaconic Centre (Faraja school for children with physical disabilities), Sanya Juu
- ELCT Northern Diocese operates Building a Caring Community (BCC)
- ELCT Meru Diocese operates Usa River Rehabilitation and Training Centre (URRC)
- Catholic Archdiocese of Arusha operates Canaan Children's Center

Member-home contacts written under the homes' own names: Kalali Orphanage (head of centre) and Faraja Diaconic Centre (head of centre). The ELCT Northern Diocese published both.

## Searches (allowance 12, all used)

- Q1/12 `network of children's homes Arusha orphanages association members`. No formal network of children's homes was found, only individual homes.
- Q2/12 `Tanzania Child Rights Forum members Arusha Kilimanjaro`. Found tcrfnet.org and the Better Care Network profile.
- Q3/12 `ELCT Northern Diocese Moshi diakonia department orphans children contact`. Found elctnortherndiocese.org.
- Q4/12 `Caritas Arusha Archdiocese of Arusha social services orphans children's homes`. Found Canaan Children's Center and the archdiocese site (arushaarchdiocesea.com).
- Q5/12 `"Caritas Moshi" OR "Moshi Diocese Caritas" orphans ...`. Nothing about Caritas Moshi. Only individual Moshi homes came up, and those are already in the welfare list.
- Q6/12 `KKKT Dayosisi ya Meru diakonia watoto yatima Usa River Nkoaranga`. Found elctncd.or.tz (North Central Diocese), plus a Meru health-facility record.
- Q7/12 `ELCT Meru Diocese Usa River official website diakonia department`. Found the ELCT All dioceses directory and an LWF article.
- Q8/12 `Archdiocese of Arusha Caritas social development office contact TEC dioceses directory`. Found the AMECEA directory and the Caritas Internationalis Tanzania page. The TEC Catholic Directory 2020 PDF returned 404.
- Q9/12 `Kilimanjaro NGO network KINGONET members Moshi children organisations`. No Kilimanjaro network was found; KINGONET turned out to be the Kilwa network. The Policy Forum 2017 directory PDF had no text that could be read.
- Q10/12 `umoja wa vituo vya kulelea watoto yatima Arusha OR Kilimanjaro mwenyekiti`. Found UVIKUWA (Umoja wa Vituo vya Kulea Watoto Tanzania), a union based in Dar es Salaam (Msumba News, Aug 2026). It deals with early-childhood day care, so it is out of scope (competitors) and no record was written.
- Q11/12 `Moshi NGO network OR "Kilimanjaro NGOs Network" OR "Hai NGO network" OR "Meru NGO network"`. No district or regional network found.
- Q12/12 `Anglican Diocese of Mount Kilimanjaro Arusha orphans vulnerable children programme contact`. Only Wikipedia and third-party pages came up, with no official contact route, so no record was written.

## Pages read (read_page.py unless noted)

- ANGONET: `/`, `/about-us/`, `/contact/`, `/member-or-partner/`, `/swahili-for-foreigners/`, the WordPress sitemaps. `/membership-or-partnership/` returned 404. The membership page gives `info@angonetz.or.tz`, which looks like a typo and was not recorded.
- CSSC: `/`, `/contact-us`, `/experts`. `/contact`, `/our-experts`, `/about/experts`, `/our-team` and `/sitemap.xml` returned 404.
- TCRF: `/`, `/about`, `/members`. `/contact`, `/our-members` and `/about-us` returned **HTTP 429**, so I stopped reading that site. Also read the Better Care Network TCRF profile.
- ELCT Northern Diocese: `/`, `/diaconal/`, `/diaconal-service-institutions/`, `/contact/` (redirects to `/contact-us/`), `/bishops-office/`, `/general-administration/`, `/hai-district/`, `/siha-district/`, `/central-district/`, `/health-service-institutions/` (empty). `/parenting-and-family/` gave no body.
  - The Hai District (Jimbo) of this diocese has 51 parishes across Hai, Siha, Moshi, Meru and Simanjiro. It could be an intermediate introducer.
- ELCT North Central Diocese: `/`, `/kuhusu-sisi/`, `/uongozi/`, `/misioni-na-uinjilisti/`. The leadership page also lists parish pastors' mobiles; none were recorded.
- ELCT national: `elct.org/dioceses/alldioceses.html` (undated and partly stale), plus elct.or.tz `/index.php/about-us/`, `/women-and-children/`, `/health-and-diakonia/` (no body), `/contact/`. `/index.php/dioceses/` returned 404.
- LWF news article of 30 Mar 2022 on Usa River (URRC). The article names a young resident and her health condition; none of that was recorded.
- AMECEA Catholic dioceses directory. Caritas Internationalis Tanzania page (no contact details shown). moshidiocese.org `/`, `/about1`, `/about-us`. kmho.org `/`.
- canaanchildrenscenter.com `/`.
- Mwananchi article of 4 May 2022 (not relevant). Msumba News article (UVIKUWA).
- Policy Forum `DIRECTORY2017.pdf`: fetched, but no text could be extracted.

## Blocks and failures (not worked around)

- `www.arushaarchdiocesea.com`: the connection was refused for read_page, and WebFetch was denied for the domain.
- `elctdme.or.tz` (ELCT Meru Diocese): the TLS certificate has expired, so read_page failed, and WebFetch was denied for the domain.
- `tcrfnet.org`: HTTP 429 after three pages.
- `tcrf.or.tz`, `elct-nd.org` and `arushaarchdiocese.org` do not resolve. These were guessed domains and none was used as a source.
- TEC Catholic Directory 2020 PDF: 404.

## Gaps and leads not confirmed

- No network or association of children's homes specific to Arusha or Kilimanjaro was found on any public page.
- Caritas Arusha and Caritas Moshi: no office, coordinator or contact page was found.
- Catholic Diocese of Moshi: already in the list. Its site shows no social-services or Caritas desk.
- ANGONET does not publish its member list. Ask the secretariat which members are child-focused.
- The CSSC Northern Zone office in Arusha has no published address or contacts.
- ELCT Meru Diocese: the current leadership and the diaconal head need confirming once the diocese site's certificate is fixed.
- ELCT North Central Diocese: the Udiakonia (orphans and widows) unit has no named head. The Children's unit coordinator and the Gender department secretary are recorded instead.
- Anglican Diocese of Mount Kilimanjaro (Arusha) and Muslim bodies such as the Ansaar Muslim Youth Centre (operator of Ummu Aisha): not researched beyond Q12, because the searches were used up.
