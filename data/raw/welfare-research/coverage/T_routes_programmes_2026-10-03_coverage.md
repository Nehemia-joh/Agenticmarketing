# Slice T coverage log: published contact routes for family-based and sponsorship programmes (2026-10-03)

Targets: runtime/contacts/slices/welfare13_B.json (105). Output: data/raw/welfare-research/research_T_routes_programmes_2026-10-03.jsonl.
Pages read with scripts/contacts/read_page.py unless marked WebFetch. Search allowance: 50.

## Searches and pages by target

### 1. Ngarasero Community Organization
- Page: dailynews.co.tz/20-vulnerable-children-in-usa-river-seek-education-sponsorship/ (200): manager named, no phone or email.
- Q1/50 `"Ngarasero" Usa River organization contact`: nothing relevant. No route found; skipped.

### 2. POSA - Positive Steps in Arumeru
- Q2/50 `"Positive Steps in Arumeru" POSA Tanzania`: only Arumeru district and lodge pages. No route; skipped.

### 3. HopeCare (Arusha)
- Q3/50 `HopeCare Arusha Tanzania orphans Boma Road contact email`: other Arusha charities (Hope Centre, Hill Foundation, Hope and Soul), none named HopeCare. No route; skipped (the earlier source was a ProPublica full-text search page, not usable).

### 4. TAG Kilimanjaro Revival Temple Child and Youth Development Centre
- Q4/50 `TAG Kilimanjaro Revival Temple Moshi church contact phone email`: IMPAACT directory and unrelated pages. No route; skipped.

### 5. LITTLE PROSPECTS FOUNDATION (LPF)
- NIS profile 18204 (cached register text): no contact fields (NIS profiles publish none).
- Q5/50 `"Little Prospects Foundation" Arusha`: nothing for the name. Skipped.

### 6. Upendo Kwanza
- https://upendokwanza.org/ : certificate hostname mismatch; http://upendokwanza.org/ (200): registrar page, domain registration expired.
- ProPublica organisation page 873669764 (200): no Form 990 data.
- Q6/50 `"Upendo Kwanza" Tanzania Usa River children`: nothing for the name. Organisation record written (website dead, red flag). No route.

### 7. MORAVIAN NORTHERN SOCIAL DEVELOPMENT ORGANIZATION
- Q7/50 `"Moravian Northern Social Development Organization" Arusha`: nothing. Skipped.

### 8. CENTRAL CHILDREN SUPPORT (CCS)
- Q8/50 `Central Children Support CCS Arusha NGO Tanzania`: other Arusha children's charities only. Skipped.

### 9. NIKUMBUKE LEO ORGANIZATION
- Q9/50 `Nikumbuke Leo Organization Arusha`: nothing. Skipped.

### 10. AFRICA MASTERPIECE CHILDREN ORGANIZATION
- Q10/50 `Africa Masterpiece Children Organization Arusha Tanzania`: other Arusha children's charities only. Skipped.

### 11. BRIGHT HOPE CHILDREN DOUNDATION
- Q11/50 `"Bright Hope Children Foundation" Arusha Tanzania`: nothing for the name. Skipped.

### 12. UGUTU COMMUNITY FOUNDATION
- Q12/50 `Ugutu Community Foundation Tanzania`: nothing. Skipped.

### 13. Change your life Foundation
- Q13/50 `"Change Your Life Foundation" Arusha`: nothing. Skipped.

### 14. AFRO RURAL DEVELOPMENT CONSORTIUM
- Q14/50 `"Afro Rural Development Consortium" Tanzania`: nothing. Skipped.

### 15. SPORTS HOSTEL FOUNDATION
- Q15/50 `"Sports Hostel Foundation" Arusha Arumeru`: hostels only. Skipped.

### 16, 17, 19, 20. HUSNA FOUNDATION; CARORYAN FOUNDATION; ME AND ORPHANS TANZANIA; VOLANTE'S EAGLES ORGANIZATION (VEO)
- Q16/50 (one combined search, so no more than one search per target) `Husna Foundation OR Caroryan Foundation OR "Me and Orphans" OR "Volante's Eagles" Arusha`: none of the four names found. Skipped.

**Change of approach after Q16.** Fifteen searches on register-only names found nothing: the search engine has no pages for small register-only NGOs. To use the remaining 34 searches well, the targets that already have a website or source page were read next (no search needed), then the remaining searches went to targets with distinctive names in list order. Register-only targets with generic names that got no search are listed under "Targets not reached".

### Pages read without a search (targets that already had a site or source page)
- 25 Arusha Children's Effort: home and contact pages (200). FOUND: email vd@vinnie.co.nz (published as contact), director Vinnie Duncan, Arusha liaison Blandina Mapunda. 3 records.
- 27 Espero Foundation: own domain does not resolve; Idealist listing (200) shows no email or phone. Record: dead site.
- 29 Sunrise Hope for Foundation: sunriseforhope.org and /sponsorship/ both HTTP 522. WebFetch denied for the domain. BLOCK/down.
- 36 Furahia Mtoto Foundation: furahiafoundation.org HTTP 403 (read_page); WebFetch denied. BLOCK, not worked around.
- 40 THE BANDARI YA MAENDELEO ORGANIZATION: thebandariproject.com contact and about pages (200). FOUND: thebandariproject@gmail.com (organisation's own contact, gmail), co-founder Seif Sakate, project manager Glory (given name). Located Mto wa Mbu, probably outside 25 km; runs its own school. 3 records.
- 41 GOOD HOPE KIWAWA FOUNDATION: goodhopekiwawa.org does not resolve (DNS). Record: site gone.
- 53 Olasiti Orphans Center: tanzanianorphans.org home, about-us, orphans-center, how-to-donate, scholarships; dorobofund.org special projects. No email or phone anywhere. Learned registered name Olasiti Children's Foundation; funder Dorobo Fund. PDF unparseable. Record without route.
- 57 TRMEGA: netzkraft.net profile timed out (connection failure). Not retried.
- 77 Son and Oscar Foundation: oscarfoundation.com home, about, support (200). Contact form only; no email or phone. Record written.
- 90 Habari Foundation (Moshi): habarifoundation.org returned a 'Bot Verification' page (BLOCK); meadowmontessori.org/habari-foundation HTTP 403 (BLOCK). Not worked around.
- 6 Upendo Kwanza: see above (domain expired).
- 103 Fruitful Organization: jimdoweb contact, home and our-team pages (200); arushakids.com/about-us HTTP 403 (block). FOUND: office/director mobile +255 762 353 576, P.O. Box 112 Duluti; emails obfuscated by the host and not decoded. 2 records.
- 102 AREM FOUNDATION: aremfoundation.or.tz shows a 'Bot Verification' page. BLOCK, not worked around.
- 105 Home Foundation (Rhotia): Idealist listing (200): village Kilimatembo, Rhotia, Karatu District; no route. Outside the catchment.
- 104 Mother Kevina and 30 Victoria's Giving, 3 HopeCare: only earlier source is a ProPublica full-text SEARCH results page, which is not a permitted source; not read.

### Searches Q17 to Q32 (resumed run; all found nothing for the exact name unless stated)
- Q17/50 `"Hearts of Hope Foundation" Tanzania Arusha children` (target 18): other charities only.
- Q18/50 `"Leading by Feeding Africa" Arusha` (21): agriculture and event pages. Nothing.
- Q19/50 `"Eastern Star Children Organization" Arusha Tanzania` (22): Arusha Children's Trust etc. Nothing.
- Q20/50 `"Support Children and Community Advancement" SUCARE Arusha` (24): nothing.
- Q21/50 `"Levites Children Foundation" Arusha` (31): nothing.
- Q22/50 `"Education for Children in Need" ECN Arusha Tanzania` (26): nothing.
- Q23/50 `"Faraja Support for Needy Children and Orphans" Arusha` (28): results are for Faraja Support (UK charity 1125285, boys' home in Moshi area), a different body; identity with the register entry not established, so no record.
- Q24/50 `"Relief for the Hopeless Foundation" Arusha` (32): nothing.
- Q25/50 `"Lengijabe" children's volunteering relief Arusha` (35): nothing.
- Q26/50 `"Every Child Count" Arusha Tanzania scholarship girls` (38): nothing.
- Q27/50 `TRMEGA Training Research Monitoring ... Arusha` (57): nothing.
- Q28/50 `"Kutamani Foundation" Arusha OR "Widows & Watoto"` (55): govolunteer.com.au directory snippet (page 403, not read). Record written, snippet-only.
- Q29/50 `"Mother Kevina" feeding program Kijenge Arusha` (104): ACI Prensa article (read, 200): congregation-run Kijenge dining hall since 2002; no route. Record written.
- Q30/50 `"Emunyani" charity Arusha children's home` (86): nothing.
- Q31/50 `"Ikunda" orphans children organization Arumeru Tanzania` (73): nothing.
- Q32/50 `"Kilimanjaro Aid Project" OR "Kili-Hope" OR "Rolina Association for Orphans" Moshi` (99, 94, 85; one combined search): nothing for the names.
- Blocks in this stretch: govolunteer.com.au 403; globalgiving.org 403.
- Q33/50 `"Mesha's Village" Tanzania Usa River Ngarasero` (target 1): nothing on Mesha's Village; Wikipedia Usa River page read (200) for the Ngaresero neighbourhood name only.
- Target 1 Ngarasero: also read dailynews.co.tz/care-centre-seeks-sponsors-for-children and tanzaniainsight.com article (200): partner Mesha's Village (US donor group) sponsors 75 children; still no email or phone. Records: organisation, contact Zuhura Igwe, relationship.
- Target 4 TAG Kilimanjaro: read dailynews.co.tz/centre-transforms-over-400-childrens-lives and allafrica.com/stories/202609140381 (200): Compassion partner, Senior Pastor Ron Swai; no route. Records: organisation, contact.

### Searches Q34 to Q39 (nothing found for any name)
- Q34/50 `"Meru Peak Foundation" Tanzania orphans` (46): only a removed UK charity, Meru Peak Children's Trust, a different body; no record.
- Q35/50 `"Ndovu Foundation" Arusha Tanzania orphans` (45): nothing.
- Q36/50 `"Children Must Live" Tanzania Siha CML-T` (79): nothing.
- Q37/50 `"Shujaa wa Upendo Initiative" Tanzania` (50): nothing.
- Q38/50 `"Glory Vision Tanzania" Arusha Korea children` (75): nothing.
- Q39/50 `"Kujengana Network" Arusha` (74): nothing.

Searching stopped at 39 of 50. Thirty-nine searches on named targets produced no page for any register-only NGO, so the remaining allowance was not spent on more of the same.

## Totals
- Searches used: 39 of 50 (Q1 to Q39). No search was refused. No limit reached.
- Records written: 25 lines (17 organisation, 7 contact, 1 relationship), every line parses as JSON, all with "slice": "T". 17 of the 105 targets have a record.
- Routes found: 3 targets.
  - Arusha Children's Effort: email vd@vinnie.co.nz (organisation's own contact page; non-organisation domain, pdpa medium).
  - THE BANDARI YA MAENDELEO ORGANIZATION (The Bandari Project): thebandariproject@gmail.com (published as its contact; gmail; Mto wa Mbu, probably outside 25 km; runs its own school).
  - Fruitful Organization: phone +255 762 353 576 (director's mobile as published contact line); two emails exist on the page but are obfuscated by the host and were not decoded.
- Named people recorded: Vinnie Duncan, Blandina Mapunda (ACE); Seif Sakate, Glory (Bandari); Isaac John Sumary (Fruitful); Zuhura Igwe (Ngarasero); Ron Swai (TAG Kilimanjaro).
- Other records (no route): Ngarasero (plus relationship Mesha's Village, a US donor group, funds 75 children), TAG Kilimanjaro (Compassion partner), Olasiti Orphans Center (registered name Olasiti Children's Foundation; funder Dorobo Fund), Mother Kevina Kijenge (Little Sisters of St Francis; 91 children fed daily), Home Foundation (Kilimatembo, Rhotia; Karatu, outside catchment), Son and Oscar Foundation (contact form only), The Kutamani Foundation (snippet only; teacher training).
- Dead or down sites: Upendo Kwanza (domain expired), Espero Foundation (domain dead), Good Hope Kiwawa (domain dead), Sunrise Hope for Foundation (HTTP 522).

## Blocks (none worked around)
- Bot verification pages: habarifoundation.org, aremfoundation.or.tz.
- HTTP 403: furahiafoundation.org, meadowmontessori.org, arushakids.com, govolunteer.com.au, globalgiving.org.
- WebFetch denied for furahiafoundation.org and sunriseforhope.org.
- netzkraft.net timed out (TRMEGA), not retried.
- ProPublica full-text SEARCH pages (earlier sources for HopeCare, Victoria's Giving, Mother Kevina) are not permitted sources and were not read.

## Targets not reached (no search, no page read)
Numbers are positions in runtime/contacts/slices/welfare13_B.json. All are register-only names with no site or source page; 49 targets:
23, 33, 34, 37, 39, 42, 43, 44, 47, 48, 49, 51, 52, 54, 56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 76, 78, 80, 81, 82, 83, 84, 87, 88, 89, 91, 92, 93, 95, 96, 97, 98, 100, 101

Target 30 (Victoria's Giving Foundation) had only a ProPublica full-text search page as its source, which is not permitted, so it was not read.
Targets searched with no usable result and no record written are not repeated here; each is listed against its search above.
