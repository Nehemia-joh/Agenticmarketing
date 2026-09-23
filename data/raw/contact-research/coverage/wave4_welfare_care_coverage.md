# Coverage log: wave 4, welfare care (23 September 2026)

- **Slice:** `runtime/contacts/slices/wave4_welfare_care.json`, nearest first. It holds 45 welfare-run organisations:
  - 42 child-focused NGOs from the national NGO register with no published route
  - 3 children's homes: Jericho, Bethlehem and Peace House. Jericho and Peace House lacked a named decision-maker.
- **Output:** `data/raw/contact-research/search_wave4_welfare_care_2026-09-23.jsonl`, one line per organisation, written as the work went.
- **Searches:** allowance 44 WebSearch calls; used 44 (Q1/44 to Q44/44). The session cap refused none. After Q44, only URLs already in hand were fetched. No search was routed through WebFetch, a browser or a results page.
- **Fetch pacing:** at least 2.2 seconds between requests to one host.
  - robots.txt was read for every host and every redirect hop, and Disallow rules were honoured.
  - A 4xx robots.txt counted as no rules. An unreadable one was crawled under the 23 September decision; this happened only at thelittleoasisfoundation.org, which later proved readable and allowing.
  - The agent's cache, fetch log and helpers are in `runtime/contacts/agents/wave4_welfare_care/`. The shared crawler cache was not touched.
- **Organisations written:** 45 of 45.
  - Status: found 11, partial 13, not_found 21, blocked 0.
  - Identity: confirmed 41, uncertain 4 (HUSNA FOUNDATION, HOPE SEED INITIATIVES, I Want to Be Foundation, SUCARE).
- **Results:**
  - 36 named leads across 11 organisations; 34 hold decision-making roles, 35 come from fetched pages and 1 from a snippet. PDPA risk: 35 medium, 1 risky.
  - New direct routes: 16 emails and 17 phones, for 17 organisations. Of these, 13 emails and 12 phones come from pages that were read; the rest are snippet-only. Peace House's phone was already held and was re-read.
  - Kid Care International's routes are new to this record but already sit on its twin, ORG_43d85c635de01ce1.
- **Prior evidence read before any search:**
  - the slice (every `known_sources` list was empty)
  - `data/raw/welfare-research/research_*.jsonl`
  - the earlier contact-research records and coverage logs, including wave 3's advice for Bethlehem
  - the NIS register profiles held in the run database, which publish no contacts
  - the welfare run database, read only, for twins and register details
- **Recording rules applied:**
  - People come only from the organisation's own site, its imprint or team page, or an official register (the IRS Form 990 data shown by ProPublica). Names on press, supporter, directory, data-broker or outdated blog pages were not recorded as leads.
  - Nothing about children, parents or residents was recorded, and pages about children were not opened.
  - No biographies, family ties, pay figures, personal social profiles or home-looking street addresses were recorded.
  - Every note keeps its warnings within its first 600 characters, the part the profile builder keeps.

## Status definitions

- `found`: identity confirmed, and at least one email or phone read on a page published by the organisation, its parent body or an official register.
- `partial`: only indirect routes (website, official social page, postal address), or a direct route that is snippet-only, from a directory, or of uncertain identity.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading. None this wave; blocked sites with other evidence are marked partial.

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| Q1/44 | `"Vuka Initiative" Arusha` | 1. VUKA INITIATIVE | Facebook page 'VUKA Initiative'. A 2020 Michuzi Blog launch report quotes registration 00NGO/R/1149, matching the register; its named leaders were not recorded (press page). partial |
| Q2/44 | `"ProManity International" Arusha` | 2. ProManity International | German member association ProManity e.V. (promanity.de): inbox, socials, imprint board, and the Pippi House team in Arusha; 5 leads. promanity.org is a non-existent domain. found |
| Q3/44 | `"WIWOCHI" Arusha street and working children` | 3. WIWOCHI | Own site wiwochi.org: inbox, mobile, Moshono; Core President. The Managing Director is named by first name only (not recorded). found |
| Q4/44 | `"Glory Reach and Help Foundation" Tanzania` | 4. GLORY REACH AND HELP FOUNDATION | No match; Glorious Foundation Tanzania is a different registration. not_found, possibly inactive |
| Q5/44 | `"Little Prospects Foundation" Arusha` | 5. LITTLE PROSPECTS FOUNDATION (LPF) | No match (other Arusha foundations). not_found |
| Q6/44 | `"Upendo Kwanza" Tanzania education` | 6. Upendo Kwanza | Upendo Kwanza Inc (US; Kisimiri Secondary School project, matching the register). upendokwanza.org serves a TLS certificate for another host and was not read. X and LinkedIn pages found; ProPublica holds no Form 990. partial |
| Q7/44 | `"Jericho Orphanage" "Usa River"` | 7. Jericho Orphanage Home | Only the known Facebook page and third-party volunteer listings; no named leader in an allowed source. partial |
| Q8/44 | `"Asante Africa" Tanzania Arusha office` | 8. ASANTE AFRICA TANZANIA | Asante Africa Foundation's Tanzania business office (PO Box 8097, Arusha): inbox, two phones, and the Country Manager with a work email; 6 leads. found |
| Q9/44 | `"Moravian Northern Social Development Organization" Tanzania` | 9. MORAVIAN NORTHERN SOCIAL DEVELOPMENT ORGANIZATION | Only Moravian Church pages; the Board of World Mission page on the church's northern province was read and does not mention it. not_found |
| Q10/44 | `"Central Children Support" Arusha` | 10. CENTRAL CHILDREN SUPPORT (CCS) | No match. not_found |
| Q11/44 | `"Nikumbuke Leo" Arusha` | 12. NIKUMBUKE LEO ORGANIZATION | No match. not_found, possibly inactive; fit to check |
| Q12/44 | `"Project Zawadi" Tanzania Arusha` | 13. PROJECT ZAWADI INCORPORATED | Own site: US toll-free line, inbox, socials, an Arusha administrative office; 6 leads. Its base is in Bunda District, Mara (location to check). found |
| Q13/44 | `"Willows International" Tanzania Arusha` | 14. WILLOWS INTERNATIONAL TANZANIA | Arusha landline and inbox from the Association of Tanzania Employers' member directory; Facebook page. willowsintl.org answers 404 and the Harvard page 403. Reproductive-health programme (fit to check). partial |
| Q14/44 | `"Africa Masterpiece Children" Arusha` | 15. AFRICA MASTERPIECE CHILDREN ORGANIZATION | No match. not_found |
| Q15/44 | `"From Hearts 2 Hands" Tanzania` | 16. From Hearts 2 Hands | Own site: a Gmail inbox named after it, Instagram, YouTube, founder. found |
| Q16/44 | `"Ugutu Community Foundation" Tanzania` | 17. UGUTU COMMUNITY FOUNDATION | No match. not_found |
| Q17/44 | `"Change Your Life Foundation" Arusha Tanzania` | 18. Change your life Foundation | No match (differently named Arusha organisations). not_found |
| Q18/44 | `"Elle Peut Naidim" Tanzania` | 19. ELLE PEUT NAIDIM (EPN) | Own site epn.or.tz: inbox, mobile, Arusha, Instagram; 3 leads. Programmes match the register. found |
| Q19/44 | `"Afro Rural Development Consortium" Tanzania` | 20. AFRO RURAL DEVELOPMENT CONSORTIUM | No match (AARDO and other bodies). not_found |
| Q20/44 | `"Husna Foundation" Arusha` | 21. HUSNA FOUNDATION | Namesakes only. A travel company's Arusha itinerary mentions a 'Husna Foundation' project that no source links to this entry. husnafoundation.org has no content. not_found, uncertain |
| Q21/44 | `"Warioba Child Compassion" Arusha` | 22. WARIOBA CHILD COMPASSION | Facebook page and Instagram named after it. Phone, a Gmail inbox and Lolovono street come from the result summary only. warioba.org is a non-existent domain. partial |
| Q22/44 | `"Little Oasis Foundation" Tanzania` | 23. THE LITTLE OASIS FOUNDATION (TLOF) | Own site: inbox, mobile, Njiro (Arusha Region), Instagram. The contact page was read on one retry after HTTP 503 (maintenance). found |
| Q23/44 | `"Hearts of Hope Foundation" Tanzania Arusha` | 24. The Hearts of Hope Foundation Tanzania | Facebook page in Arusha only. partial |
| Q24/44 | `"Mother and Child Care" NGO Arusha pastoral` | 25. MOTHER AND CHILD CARE | No match. The ngobase Arusha list answered HTTP 403. not_found, possibly inactive |
| Q25/44 | `"Finnish Special Education in Africa" Arusha` | 26. FINNISH SPECIAL EDUCATION IN AFRICA ry | Own site fsea.fi: inbox, the founders' two Finnish phones, socials; 6 leads from the Finnish and Tanzanian boards. found |
| Q26/44 | `"Gily's Children Foundation" Arusha` | 27. Gily's Children Foundation | Own site gilyschildrenfoundation.org: inbox, mobile, Arusha, founder and managing director. gilysfoundation.org fails DNS (SERVFAIL). found |
| Q27/44 | `"Volante's Eagles" Arusha` | 28. VOLANTE'S EAGLES ORGANIZATION (VEO) | No match (registered August 2026). not_found |
| Q28/44 | `"DIWODEO" Dinkwa Women Development Organization Arusha` | 29. DINKWA WOMEN DEVELOPMENT ORGANIZATION (DIWODEO) | Own blog has no posts. PO Box, mobile and Yahoo inbox come from the summary of a Yumpu copy of an education CSO directory (HTTP 403). partial |
| Q29/44 | `"Hope Seed Initiatives" Arusha` | 30. HOPE SEED INITIATIVES | Only hopeseedinitiatives.org ('Goat Project'), now a non-existent domain. not_found, uncertain, possibly inactive |
| Q30/44 | `"Leading by Feeding Africa" Tanzania` | 31. LEADING BY FEEDING AFRICA | No match (national food-security news). not_found |
| Q31/44 | `"Tree of Love Foundation" Arusha Tanzania` | 32. TREE OF LOVE FOUNDATION | No match. not_found, possibly inactive |
| Q32/44 | `"Eastern Star Children Organization" Tanzania` | 33. EASTERN STAR CHILDREN ORGANIZATION | Facebook page in Arusha (registered 2016 per snippet; international volunteers stopped in 2024). partial |
| Q33/44 | `"I Want to Be Foundation" Arusha Tanzania` | 34. I Want to Be Foundation | Own site: home page read; contact and about pages answered HTTP 429. Arusha unconfirmed. partial, uncertain |
| Q34/44 | `"Learning Minds Africa" Arusha` | 35. LEARNING MINDS AFRICA ORGANIZATION | Its site learningmindsafrica.co.tz is now a non-existent domain; phone and PO Box come from its snippet. Facebook page in Arusha. partial |
| Q35/44 | `"SUCARE" "Support Children and Community Advancement" Tanzania` | 36. SUCARE | Only a LavHa supporter page, now HTTP 404, about a similarly named orphanage started in 2017 (the register says 2010). not_found, uncertain |
| Q36/44 | `"HACHAWOTA" Hands for Children and Women in Tanzania` | 37. HACHAWOTA | Only a 2020 video mention and grant-application screens, which were not opened. not_found |
| Q37/44 | `"Loving by Actions" organization Arusha` | 38. LOVING BY ACTIONS ORGANIZATION | No match. not_found |
| Q38/44 | `"becechi" Bethlehem Center for Children Arusha` | 39. Bethlehem Center for Children | Wave 3's handle query worked: own Wix site with mobile, PO Box 1597, a Yahoo inbox named after the home, and the founder (her personal Yahoo kept on the lead as risky). becechi.org is a non-existent domain. found |
| Q39/44 | `"Peace House Secondary School" Arusha head of school` | 40. Peace House (Arusha) | No named head. The GPEN member profile gives the parent body (ELCT North-Central Diocese) and Olasiti Ward. A 2007 blog was not used. partial |
| Q40/44 | `"Butterfly Africa" Arusha digital education children` | 41. Butterfly Africa | No match. not_found |
| Q41/44 | `"Education for Children in Need" Arusha Tanzania` | 42. EDUCATION FOR CHILDREN IN NEED (ECN) | No match. not_found, possibly inactive |
| Q42/44 | `"Happy Childhood Foundation" Tanzania Canaan children's home` | 43. Happy Childhood Foundation | No match. Canaan Children's Center pages were checked and do not mention it. not_found |
| Q43/44 | `"World Vision Tanzania" Arusha office contact` | 44. WORLD VISION TANZANIA | National office at Njiro, Arusha: address and two office lines from the snippet of its contact page (HTTP 403). partial |
| Q44/44 | `"Osotuwa Foundation" Arusha` | 45. OSOTUWA FOUNDATION | osotuwa.org answered HTTP 429. Gmail inbox and the Arusha programme director come from the summary. President and Secretary/treasurer come from the FY2024 Form 990. partial. Allowance spent. |

No search was spent on **11. Kid Care International**. Its twin record's site kidcare.org gave an inbox, a US phone, a mailing address and 3 leads, including the director of the Shalom Center in Arusha. found.

## Fetches without a search

Each URL came from the slice's prior evidence, a result of that organisation's search, or a link on a page already fetched.

| Organisation | URL | Outcome |
|---|---|---|
| 1. VUKA | https://issamichuzi.blogspot.com/2020/09/balelewazaziwalezi-jengeni.html (redirects to www.michuzi.co.tz) | Launch report quoting 00NGO/R/1149; identity only |
| 1. VUKA | https://www.loominternational.org/category/agriculture/ | Different 'Vuka' programme; not used |
| 2. ProManity | https://promanity.org/en/ | Non-existent domain (local resolver and 1.1.1.1) |
| 2. ProManity | https://promanity.de/ (home, /kontakt/, /impressum/, /ueber-uns-team/) | Inbox, socials, board, Arusha team |
| 3. WIWOCHI | https://wiwochi.org/ (/about-what-we-do/, /contact-us/, /our-founder/, /our-president/, /about-who-we-are/) | Contacts, president, registration year |
| 6. Upendo Kwanza | https://upendokwanza.org/ | TLS certificate for another host; Python and curl both refused. Verification was never disabled. |
| 6. Upendo Kwanza | https://projects.propublica.org/nonprofits/organizations/873669764; https://givebutter.com/October100mileswithUpendoKwanza | EIN and 'no Form 990 data'; the campaign page has no contacts |
| 7. Jericho | https://www.idealist.org/en/nonprofit/2b2395d9956c448c9483d4588b5e2250-jericho-orphanage-arusha | 2013 listing (Arusha karatu, www.jerichome.org); no names |
| 7. Jericho | http://www.volunteerbasecamp.com/…/Jericho-Orphanage-Home/Karatu/623 | HTTP 521; its robots.txt redirects to a gambling domain (hijacked); not used |
| 7. Jericho | jerichome.org, jerichome.or.tz (DNS only) | Non-existent domains |
| 8. Asante Africa | https://asanteafrica.org/contact-us/, /global-team/ | Tanzania office routes, Country Manager, board and management |
| 9. Moravian Northern | https://www.moravian.org/mission/northern-tanzania/ | No mention of the organisation |
| 11. Kid Care | https://kidcare.org/contact/, /leadership/, /about/ (twin record's known site) | Inbox, phone, mailing address, team, Tanzania programme |
| 13. Project Zawadi | https://projectzawadi.org/ (home, /more-information/contact-us/, /about/team/, /where-we-work/) | Contacts, team, Arusha office; a hidden trap link was not followed |
| 14. Willows | https://www.idealist.org/en/nonprofit/dd0df453b1a346e0956b11fbce517ac4-willows-international-middletown | Programme description (reproductive health) |
| 14. Willows | https://membership.ate.or.tz/members/willows-internnational-tanzania-ltd-4108 | Arusha landline and inbox (member directory) |
| 14. Willows | https://projects.iq.harvard.edu/willowsimpacteval/tanzania | HTTP 403 (robots.txt and page) |
| 14. Willows | https://willowsintl.org/, https://www.willowsintl.org/ | HTTP 404 on both (disconnected Wix site) |
| 16. From Hearts 2 Hands | https://fromhearts2hands.com/ (home, /contact/, /about/) | Inbox, socials, founder |
| 19. EPN | https://www.epn.or.tz/ (home, /contact-us, /our-team) | Contacts and leadership |
| 21. Husna | https://husna.com/sandb-overview/ | Itinerary mention only; company contacts not used |
| 21. Husna | https://husnafoundation.org/ | No content (script redirect to a lander page) |
| 22. Warioba | https://warioba.org/ | Non-existent domain |
| 23. Little Oasis | https://thelittleoasisfoundation.org/ (home, /our-story/, /contact-us/) | robots.txt timed out, then 503, then readable (allows these pages); contact page 503, then read on one retry |
| 25. Mother and Child Care | https://ngobase.org/ci/TZ.AR.AR/arusha-ngos-charities | HTTP 403 |
| 26. FSE | https://www.fsea.fi/who-we-are/, /contact/, /meet-our-team/ | Registration, contacts, boards |
| 27. Gily's | https://www.gilyschildrenfoundation.org/ (home, contact.php, about.php, single-staff.php?view=23 and 24) | Contacts and director. A first attempt hit a transient DNS failure. The pages parse badly, so text was read from the saved HTML. The portal and webmail were not opened. |
| 27. Gily's | http://gilysfoundation.org/imprint/ | DNS SERVFAIL (local resolver and 1.1.1.1) |
| 29. DIWODEO | https://diwodeo.blogspot.com/ | Blog with no posts |
| 29. DIWODEO | https://www.yumpu.com/en/document/view/37439130/directory-of-education-civil-society-organizations-tanzania-/29 | HTTP 403 (robots.txt and page) |
| 29. DIWODEO | https://mabumbe.com/kb/dinkwa-women-development-organizationdiwodeo-details-profile-overview-tanzania/ | SEO aggregator; not used |
| 30. Hope Seed | https://hopeseedinitiatives.org/ | Non-existent domain |
| 34. I Want to Be | https://iwanttobefoundation.com/ (redirects to www), /contact-i-want-to-be-foundation, /about-i-want-to-be-foundation | Home read; both other pages HTTP 429 |
| 35. Learning Minds | https://www.learningmindsafrica.co.tz/ | Non-existent domain |
| 36. SUCARE | https://lavha.com/pages/kenedy-lyimo | HTTP 404 |
| 39. Bethlehem | https://becechi.org/ | Non-existent domain |
| 39. Bethlehem | https://becechi.wixsite.com/2013, /2013/about_us | Contacts and founder; children's pages not opened |
| 40. Peace House | https://www.school.co.tz/s3838/school-profile | Phone and PO Box (re-read); no head named |
| 40. Peace House | https://www.gpenreformation.net/members/peace-house-high-school/ (redirects to the bare host) | Parent body and ward |
| 43. Happy Childhood | https://www.canaanchildrenscenter.com/ (home, /projects/, /about/) | No mention of the foundation; other partners listed |
| 44. World Vision | https://www.wvi.org/tanzania/contact-us | HTTP 403 (robots.txt and page) |
| 45. OSOTUWA | https://www.osotuwa.org/contact, /about-us, /our-board | HTTP 429 (robots.txt and all three pages) |
| 45. OSOTUWA | https://projects.propublica.org/nonprofits/organizations/921856680 | FY2024 Form 990 officers (names and roles only) |
| 45. OSOTUWA | https://isaya-oleporuo.squarespace.com/ | Disallowed by robots.txt; not fetched |

## Blocked or unreadable sites

- **HTTP 403** (not retried): projects.iq.harvard.edu, www.yumpu.com and www.wvi.org, where both robots.txt and the page answered 403; and ngobase.org (list page).
- **HTTP 429** (not retried): www.iwanttobefoundation.com (contact and about pages) and www.osotuwa.org (robots.txt, contact, about and board). No URL was requested twice. The other pages were in the same batch as the first 429, so they were requested after it. A later wave should stop at a host's first 429.
- **Bad certificate:** upendokwanza.org presents a certificate for another host. Not worked around.
- **robots.txt disallow:** isaya-oleporuo.squarespace.com.
- **Hijacked or empty:**
  - volunteerbasecamp.com (a third-party listing): HTTP 521, and its robots.txt redirects to a gambling domain
  - husnafoundation.org: no content, a lander redirect
- **Gone or missing:**
  - willowsintl.org: HTTP 404 on both hosts
  - lavha.com: the supporter page answers HTTP 404
- **DNS failures:**
  - non-existent domains on the local resolver and 1.1.1.1: promanity.org, warioba.org, hopeseedinitiatives.org, learningmindsafrica.co.tz, becechi.org, jerichome.org, jerichome.or.tz
  - SERVFAIL on both resolvers: gilysfoundation.org
- **Temporary:**
  - thelittleoasisfoundation.org: maintenance 503, read on one retry about ten minutes later
  - gilyschildrenfoundation.org: a transient local lookup failure, then read
- **Social pages** (Facebook, Instagram, X, LinkedIn, YouTube): recorded from search results or the organisation's own site; not read.
- **Not opened by choice:**
  - smartgrants.co.tz grant-application edit and view screens (non-public application records)
  - projectzawadi.org's hidden trap link
  - Gily's portal and staff mail
  - pages about children (Bethlehem's children page, sponsorship pages)

## Organisations not reached

None. All 45 organisations have a record: 44 with one search each, and Kid Care International researched from its twin's known site without a search.

## Problems and warnings

- **Stopping rule met.** One search per organisation, nearest first, and the allowance was spent exactly (44/44). No search was refused by the session cap.
- **Twin record:** Kid Care International (register entry 00NGO/00004274) is the same organisation as the welfare funder record Kidcare International (ORG_43d85c635de01ce1), which already holds its site, inbox, phone and team.
- **Register-match review suggestions that do not hold:**
  - Asante Sana is a different charity from ASANTE AFRICA TANZANIA.
  - Africa Hearts Desire is a different organisation from From Hearts 2 Hands.
  - Hidden Hearts Foundation is a different organisation from The Hearts of Hope Foundation Tanzania.
- **Possibly inactive** (registered before 2020, no register project after 2022, no web presence): GLORY REACH AND HELP FOUNDATION, NIKUMBUKE LEO, MOTHER AND CHILD CARE, TREE OF LOVE FOUNDATION, EDUCATION FOR CHILDREN IN NEED. HOPE SEED INITIATIVES is flagged too: its site is gone and its last register project ended in 2023.
- **Location to check:**
  - Jericho: Usa River on Facebook, but Karatu in the 2013 listings.
  - Project Zawadi: based at Nyamuswa, Bunda District, Mara.
  - OSOTUWA: programmes in Maasai areas.
  - Upendo Kwanza: Kisimiri, about 40 miles from Arusha.
  - Peace House: Olasiti Ward (GPEN), which settles the old conflict with '15 km along the Dodoma road'.
- **Fit to check:**
  - Willows International: a reproductive-health programme for women.
  - Upendo Kwanza: funds secondary pupils.
  - NIKUMBUKE LEO: its only register project was not child-focused.
  - Peace House: a secondary school.
  - VUKA: its focus is gender-based violence against women, girls and children.
- **Check before outreach:**
  - Warioba: snippet-only routes; its social handles look like a person's.
  - DIWODEO: routes from an undated directory copy.
  - Eastern Star: its international volunteers stopped in 2024.
  - Bethlehem: its Wix site may date from 2013.
- **Safeguarding.** No concerns found.
  - Nothing about children, parents or residents was recorded.
  - Not recorded:
    - children's names in a search summary (SUCARE)
    - residents' circumstances (the Pippi House)
    - a statement about children's health (Canaan)
- **Privacy decisions.** None of the following was recorded:
  - **Street addresses that may be private:** ProManity in Hamburg, Project Zawadi in the US, FSE in Espoo (an apartment).
  - **Built addresses:** FSE invites email to FirstName.LastName@fsea.fi; no address was built from that template.
  - **Names from sources the brief does not allow:**
    - press: VUKA's director and secretary
    - a directory copy: DIWODEO's coordinator
    - a 2007 blog: Peace House's earlier heads
    - a data broker: an Upendo Kwanza staff member
    - a supporter page: SUCARE's founder
    - first names only: WIWOCHI's managing director, OSOTUWA's founder on its own site. OSOTUWA's President is recorded from the Form 990.
  - **Personal details:**
    - personal LinkedIn links on the EPN team page
    - biographies and family details: WIWOCHI's president, From Hearts 2 Hands' founder and her trip blogs, OSOTUWA's founder and director
    - pay figures in the Form 990
  - **Personal inbox:** Bethlehem's founder's personal Yahoo address appears only on her lead, labelled risky, not as a route.
- **Tooling notes:**
  - **Encoding:** Windows passed the helper's input as cp1252, so non-ASCII characters in the drafts were double-encoded. They were repaired before the final write, and the helper now reads UTF-8.
  - **Re-verification:** all 75 fetched excerpts and 30 fetched routes were checked against the saved pages. Six excerpts were corrected to join non-adjacent fragments with '...'.
  - **Lead roles:** three were trimmed to their published decision or welfare wording, so the profile builder's person filter keeps them:
    - the Pippi House supervisor ('heads the Pippi House')
    - the Pippi House social worker
    - FSE's co-founder ('Founder | Association Treasurer')
  - **Stall:** the run stalled once at organisation 28. The drafted records were then written first, and the output file was rewritten after every organisation.
  - **Stray file:** scripts/contacts/read_page.py in the main checkout is not this agent's. Nothing was written outside the worktree.

## Next-run priorities

- **Named decision-makers still missing:**
  - Jericho Orphanage Home: its only source is the Facebook page; ask the user to open it.
  - Peace House: ask the ELCT North-Central Diocese's education office for the head of school.
- **Open by hand (blocked for automated reading):**
  - upendokwanza.org (bad certificate)
  - iwanttobefoundation.com contact page (HTTP 429); this also settles whether it is in Arusha
  - osotuwa.org contact and board pages (HTTP 429)
  - wvi.org/tanzania/contact-us (HTTP 403), for an inbox and the National Director
  - the Yumpu copy of the education CSO directory (DIWODEO's entry)
- **Confirm identity:**
  - HUSNA FOUNDATION: is it the Arusha partner of Husna Vacations?
  - SUCARE: the orphanage started in 2017, but the registration dates from 2010.
  - HOPE SEED INITIATIVES: its 'Goat Project' site is gone.
- **Snippet-only routes to verify:** Warioba, DIWODEO, Learning Minds Africa, World Vision Tanzania, OSOTUWA.
- **No web presence:** reach these through the register or the district social welfare offices:
  - Glory Reach, Little Prospects, CCS, Nikumbuke Leo, Africa Masterpiece, Ugutu, Change your life, Afro Rural, Mother and Child Care, Volante's Eagles, Leading by Feeding, Tree of Love, Loving by Actions, Butterfly Africa, ECN, HACHAWOTA
  - Moravian Northern: try the Moravian Church in Northern Tanzania's provincial office.
  - Happy Childhood Foundation: ask Canaan Children's Center's management (ORG_844eafff33788600).
- **School-fit signals:**
  - Gily's Children Foundation: a daycare for ages 9 months to 9 years and afternoon care for primary pupils; a possible pre-primary feeder.
  - FSE: deaf and inclusive education in Arusha schools, including Meru Primary School Deaf Unit.
  - UGUTU and DIWODEO: early childhood care and development.
  - EPN: programmes run in schools.
  - Scholarships and student sponsorship: The Little Oasis Foundation, Project Zawadi (Arusha office), Asante Africa.
  - Kid Care International: the Shalom Center in Arusha.
  - ProManity: pays for Pippi House girls' schooling.
  - Bethlehem Center: Heart for Africa pays school costs.
