# Coverage log: wave 8, welfare care (26 September 2026)

- **Slice:** `runtime/contacts/slices/wave8_welfare_care.json`, nearest first: 23 welfare organisations (children's homes and family-based programmes) that already had a published route but no named decision-maker. Distances run from 0.9 km (Nkoaranga, Sun of Hope, Jericho) to 90.1 km (Children Concern, Mto wa Mbu); four have no distance.
- **Output:** `data/raw/contact-research/search_wave8_welfare_care_2026-09-23.jsonl`, one line per organisation. Lines were appended as each organisation was finished and finally put in slice order. The date key is the programme's shared key; the access date is 26 September 2026 (register profiles the welfare run collected keep their 22 September 2026 date).
- **Target:** decision-makers: people who lead or decide for each organisation (founder, director, head, manager, administrator, coordinator, board chair), from the organisation's own site, a parent body's official page, the organisation's own text on a directory or platform, an official register, or (the user's decision of 26 September 2026) a funder's or partner's own page naming its current leaders.
- **Searches:** allowance 18 WebSearch calls; 18 were made (Q1/18 to Q18/18), one organisation per query. The session cap refused none. No search was routed through WebFetch, a browser or a results page. Ten organisations were done from their own or their parent's pages without any search. Second searches: Ummu Aisha (Q14, via its parent body), Klingele (Q15), SOS (Q16, via the national body), Living Water (Q17, via the German partner its blog names) and Mshikamano (Q18). Jericho (Q12), Peace House (Q13) and Sun of Hope (Q1) had been searched in earlier waves, so they were searched from a new angle.
- **Fetching:**
  - Pages were read with `scripts/contacts/read_page.py` (shared cache, spacing per site, robots.txt honoured), plus a link lister, a Cloudflare-email and link reader and a PDF text reader in `runtime/contacts/agents/wave8_welfare_care/`, all using the same cached, robots-aware fetcher. WebFetch and the browser were not used.
  - Pages the crawler had read on 23 September were served from the shared HTTP cache; they are dated 26 September, as the brief directs.
  - robots.txt: every host read had readable rules that allowed the page, or a 4xx robots.txt, which counts as no rules (oneheartsource.org, africaaminialama.com, kili-childrensfund.org, halimaorphanage.org, globalhand.org). No page was disallowed. No page was read under an unreachable robots.txt: every host whose robots.txt could not be read (DNS or certificate failure) also failed for the page itself, so nothing was taken from it.
  - `nslookup` against 1.1.1.1 and 8.8.8.8 was used only to tell a non-existent domain (NXDOMAIN) from a failing one, and to test a few guessed domains; nothing was fetched around a failure.
- **Organisations written:** 23 of 23. Not reached: none.
  - Status: found 13, partial 7, not_found 3, blocked 0.
  - Identity: confirmed 22, uncertain 1 (Jericho: its listings place it at Karatu, its Facebook page at Usa River).
- **Results:**
  - 23 named leads across 13 organisations, all from fetched pages. All are `pdpa_risk: medium`.
    - 19 carry a decision role by the builder's pattern (founders, directors, heads, chairs, the president, an administrator, the congregation's US representative).
    - The other 4: a secretary general, a manager listed as "Management", a sponsorship coordinator and a carer with no title ("Mama Salma").
    - 3 have one name only and will be labelled incomplete: "Mama Andrew" (Nkoaranga), "Geoffrey" (Tumaini) and "Mama Salma" (Ummu Aisha).
    - 3 leads have a named work email and 5 a work phone, each given by the same source for contact (Africa Amini Alama's founder, president and sponsorship coordinator; Ucare's leader; Sun of Hope's US fundraising contact).
  - Sources of the people:
    - the organisation's own site: Big Future, Hope Center, Halima, Children Concern, Ucare (its Norwegian founding charity)
    - the operator or parent body's own site: Nkoaranga (the owning hospital), KinderVilla (Africa Amini Alama), Tumaini (YWAM Arusha), Ummu Aisha (Ansaar Muslim Youth Centre, national body)
    - the organisation's own self-reported GuideStar profile: Kilimanjaro Children's Fund; the Holy Spirit Sisters Convent (USA) for Sun of Hope
    - the organisation's own MIT Solve submission: CANDENEZ
    - a partner's own page (quoted; said so in `notes`): CHETI (Inuka's team page), Ummu Aisha ("Mama Salma", on The Wanderlust Women's page and GoFundMe fundraiser)
  - Routes: 25 emails, 26 phones and 28 official social or listing links, mostly re-read from pages already known.
    - Not in the crawl's record, from own or operator pages: Africa Amini Alama's office inbox and phone (KinderVilla), Halima's phone, and Ucare's leader's Norwegian phone.
    - From the searches: Sun of Hope's US fundraising phone (GuideStar), the national inbox of Ummu Aisha's parent body, and P.O. Box 1134 Arusha for Living Water (its 2007 Idealist listing).

## Status definitions (this decision-maker wave)

- `found`: identity confirmed, and at least one named person who leads or decides for the organisation (or its operating or parent body), read on a fetched page from an allowed source.
- `partial`: no named decision-maker, but routes were read or re-read on the organisation's own pages or a directory.
- `not_found`: no named decision-maker and nothing new usable.
- `blocked`: the only promising source refused automated reading (none this wave).

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| Q1/18 | `"Sun of Hope" "Holy Spirit Sisters" Tanzania` | 2. Sun of Hope Village/Orphanage | GuideStar profile of the US convent (read; self-reported, updated September 2022): US representative Sr. Catherine Msuya, board chair and head of fundraising Bernadette Moss, fundraising phone; it also lists Sun of Hope Primary School (English medium). The phillymissions.org page answered HTTP 404. found |
| Q2/18 | `"Mshikamano Orphanage" Moshi` | 4. Mshikamano Orphanage Center | Only its own site (read) and other Moshi homes; no named leader. The site places it in Moshi, not Arusha; its .or.tz inbox domain does not exist. partial |
| Q3/18 | `"Ummu Aisha Orphanage" Arusha` | 5. Ummu Aisha Orphanage Centre | Partner The Wanderlust Women: its Tanzania page and GoFundMe fundraiser (both read) name "Mama Salma", who looks after the girls (no title). Own site re-read: no leader named. partial at this point; found after Q14 |
| Q4/18 | `"Candenez" Arusha` | 12. CANDENEZ MISSION FOR EMPOWERING VULNERABLE CHILDREN | The organisation's own MIT Solve submission (read; updated March 2022) names Sophycandy Enezael Mawalla, Director. Own site re-read; its inbox domain candenez.org does not exist. found |
| Q5/18 | `"SOS Children's Village" Arusha "village director"` | 13. SOS Children's Village Arusha | Only SOS federation pages and job posts elsewhere. SOS Canada's village page (read) names no director, but shows the village's own kindergarten and primary and secondary school. The route held is SOS Kenya's (see below). not_found |
| Q6/18 | `"Living Water Children Centre" Arusha` | 15. Living Water Children Centre | US funder Living Water Children's Fund (project page and board page read) and the centre's old WordPress blog (read) credit only "the Kimaro family"; no director named. The funder's own board was not recorded as the centre's. livingwaterchildrencentre.com could not be reached. partial |
| Q7/18 | `"Kilimanjaro Children's Fund" Haines Alaska` | 17. Kilimanjaro Children's Fund | GuideStar profile (read; self-reported, board as of April 2019): Dr. Greg Higgins, founder and board chair, who also signs the fund's own update of November 2021. Aggregators (Cause IQ, Holdings, city-data, Intellispect, GrantAdvance) were not used. found |
| Q8/18 | `"Terence G. Klingele Foundation"` | 21. THE TERENCE G. KLINGELE FOUNDATION | Own site only. An obituary, a personal LinkedIn profile and a registry aggregator (b2bhint) were not used. No leader named. partial |
| Q9/18 | `"Zorah Organization" Arusha` | 23. ZORAH ORGANIZATION | Only its own site (re-read; the team section shows no names) and NGO directories. partial |
| Q10/18 | `"Tanzania Youth Support and Self Reliance Organization"` | 22. Tanzania Youth Support and Self Reliance Organization | Only its own site (re-read; the board is unnamed) and other youth NGOs. partial |
| Q11/18 | `"Convoy of Hope" Tanzania Arusha country director` | 20. CONVOY OF HOPE | Only job posts (the National Director posting, read, dates from 2017) and parent pages (the team page answered HTTP 403 to the crawler; not retried). A HOPE International blog is about a different organisation. not_found |
| Q12/18 | `"Jericho Orphanage Home" Tanzania` | 3. Jericho Orphanage Home | The same Facebook page (not read), an unverified Globalhand profile and volunteer listings (Globalhand and Volunteer Forever read: no names). Karatu or Usa River is unresolved. not_found |
| Q13/18 | `"Peace House" "North Central Diocese" Arusha` | 6. Peace House (Arusha) | Only the school's Facebook page (not read), a 2012 student-paper article (press, not a source for people) and encyclopaedia pages. The GPEN profile and school.co.tz listing were re-read: no head named. partial |
| Q14/18 | `"Ansaar Muslim Youth Centre" Arusha` | 5. Ummu Aisha Orphanage Centre (second search, via its parent body) | The parent body's own site amyc.or.tz (Team page read) names the national body's Director General, Deputy Director General and Secretary General (HQ Tanga). Its Northern Zone page is empty; its Facebook pages were not read. found (the parent's national leaders) |
| Q15/18 | `"Klingele Foundation" guidestar` | 21. THE TERENCE G. KLINGELE FOUNDATION (second search) | No GuideStar profile for it, only similarly named foundations; the b2bhint aggregator again, not used. partial (unchanged) |
| Q16/18 | `"SOS Children's Villages Tanzania" national director` | 13. SOS Children's Village Arusha (second search, via the national body) | Job adverts only: ajiriwa.net and Mabumbe (read) address "The National Director" without a name. The National Director post was advertised on Impactpool and LinkedIn (not read). RocketReach and ContactOut (data brokers) were not used. The search summary's director name and national-office phone and email were not seen on any fetched page, so they were not recorded. not_found (unchanged) |
| Q17/18 | `"Time to Help" "Living Water" Arusha children centre` | 15. Living Water Children Centre (second search, via the German partner its blog names) | No Time to Help page. The centre's own 2007 Idealist listing (read) gives P.O. Box 1134 Arusha and no names; the funder's pages again. partial (unchanged) |
| Q18/18 | `"Mshikamano" Moshi orphanage founder director street children` | 4. Mshikamano Orphanage Center (second search) | Only its own site and other Moshi homes (Msamaria, Amani, Kilimanjaro Centre); no leader named. partial (unchanged). Allowance reached: no further searches. |

## Organisations done without a search

| Organisation | Pages read | Result |
|---|---|---|
| 1. Nkoaranga Orphanage | nkoarangahospital.org: orphanage page, about, team, home; en.africaheartsdesire.com placement page | The owning hospital's orphanage page: "The head of the orphanage is Mama Andrew" (page undated; photo from October 2019). The hospital's team page names no one. |
| 7. One Heart Source | oneheartsource.org: home, about, programs, contact | No staff named ("a distributed, remote team"); the only programme location is Cape Town. Wave 3 had already searched it. |
| 8. Big Future Foundation | bigfuturefoundation.or.tz: foundation board, profile page, contact | "Promise shayo, Chairperson & Founder". |
| 9. CHETI NGO | inukacommunity.org: about-us, cheti-ngo, meet-the-founder, contact (partner) | Partner's team page: "Zuma Mtui, Founder & Director of CHETI NGO"; routes Inuka gives for CHETI. |
| 10. Tumaini House | ywamarusha.org: home, about, contact, Tumaini Children's Ministry page | Ministry page (June 2019): head "Geoffrey"; home page (current): John Mukolwe, Base Leader. |
| 11. Ucare Family Home | ucareproject.com: family-home page, about-us, contact | "Leader: Lovise Myhre Eikenæs" with a Norwegian phone. Neema House's founders are named there too; they were left to Neema Village's own record. |
| 14. Hope Orphanage Center | hopecentertanzania.org: our-directors, contact, home, blog | "David and Beatrice Mollel, Directors" (the founders); recorded as two leads. |
| 16. KinderVilla Momella | africaaminialama.com: soziales, team, kontakt, bildung | Founder, president (with a Tanzanian mobile), Tanzanian manager, European head office and sponsorship coordinator. |
| 18. Halima Orphanage Center | halimaorphanage.org: home, about, contact | The orphanage was "officially established" in 2017 "under the leadership of Swalehe Zabura Mkilindi". The project PDF answered HTTP 404. |
| 19. Children Concern Foundation | childrenconcern.or.tz: about-us, contact-us, home | "The Founding member was Mr. Andrew Joshua ... Mr. Joshua administers C.C.F. to this day". |

## Blocked sites (recorded, not worked around)

| Site | Answer | Organisation |
|---|---|---|
| sos-tanzania.org (a guessed domain for SOS Tanzania; it resolves) | TLS certificate hostname mismatch; not read | SOS Children's Village Arusha |
| convoyofhope.org /about/, /about/our-team/, /about/contact/ | HTTP 403 to the crawler on 23 September; not retried (the home page was read) | CONVOY OF HOPE |
| Facebook pages (Jericho, Peace House High School, Kilimanjaro Children's Fund, AMYC Arusha) | login wall; not read | several |

## Unreadable, gone or placeholder

- **Inboxes on non-existent domains (NXDOMAIN at 8.8.8.8, and 1.1.1.1 where it answered):**
  - info@candenez.org (CANDENEZ's only inbox)
  - contact@mshikamano.or.tz (Mshikamano's only inbox)
  - greg@kilimanjaro-children.org (the target of Kilimanjaro Children's Fund's mailto link)
  - info@tanzaniayouth.com (in Tanzania Youth Support's header)

  Each is recorded with its type saying so, and the note names the working route.
- **Gone or unreachable sites:**
  - SOS Tanzania's old national site sos-childrensvillages.or.tz is NXDOMAIN, as are the guesses sos-tanzania.or.tz, sostanzania.or.tz, sostanzania.org, soschildrensvillages.or.tz and sos-childrensvillages.co.tz.
  - livingwaterchildrencentre.com failed DNS locally and was not pursued.
  - halimaorphanage.org's project-proposal PDF answered HTTP 404, and the phillymissions.org page on Sun of Hope HTTP 404.
- **Script-built:** thesmallthings.org, a funder of Nkoaranga Orphanage, returns no text. A browser pass might name the home's head.
- **Template placeholders, not used:**
  - Mshikamano: "123 Hope Street, Moshi, Tanzania 12345" and a Facebook link to facebook.com/wix.
  - Tanzania Youth Support: +255 712 345 678.
  - Zorah: facebook.com/# and instagram.com/#.
- **Not sources for people, not used:** an obituary and a personal LinkedIn profile (Klingele); data brokers RocketReach and ContactOut (SOS Tanzania); registry aggregators (b2bhint, Cause IQ, Holdings, city-data, Intellispect, GrantAdvance); a 2012 student-paper article (Peace House).
- **Not recorded:**
  - the Portland street address of the Holy Spirit Sisters (looks residential) and Africa Amini Alama's Vienna seat address
  - the malformed phone "+2646620" on amyc.or.tz, and a personal LinkedIn profile linked from YWAM Arusha's contact page
  - biographies (the Tumaini head's story, Big Future's founder profile, the Klingele namesake), and funders' own boards (Living Water Children's Fund)
  - staff outside outreach: caretakers and nannies, accounting, tourism, office and PR staff
  - every name or story of a child, student or resident on the pages read (Mshikamano, Kilimanjaro Children's Fund, Living Water)

## Organisations not reached

None. All 23 have a line; 13 have at least one search.

## For a person to check

1. **SOS Children's Village Arusha:** the route held for this record is SOS Kenya's. The crawler's `country-redirect` page served SOS Kenya's footer: info@soskenya.org and +254 (0)725 455 554, which was read as +255 725 455 554. Remove it. A search summary named a national director and gave a Dar es Salaam office email and phone, but they traced only to data-broker pages and were not recorded; confirm them with SOS directly. The village runs its own SOS kindergarten and primary and secondary school.
2. **Dead inboxes held as routes:** CANDENEZ (info@candenez.org), Mshikamano (contact@mshikamano.or.tz), Kilimanjaro Children's Fund (greg@kilimanjaro-children.org), Tanzania Youth Support (info@tanzaniayouth.com). For CANDENEZ and Mshikamano only the phone works.
3. **Mshikamano's location:** its site places it in Moshi (P.O. Box 6988; it serves Kaloleni, Kalimani, Pasua and Njoro), not Arusha's Kaloleni. The record's 2.2 km from Ilboru is wrong; it is near Pasua, like Halima and Kilimanjaro Children's Fund (about 22.6 km from Boma Ng'ombe).
4. **Zorah's location:** Patandi Village, Akheri Ward, Tengeru, a few km from Usa River; the register's map point lies about 24 km from Usa River.
5. **Convoy of Hope:** the number (417) 823-8244 held for it is the US parent's fax. No Tanzanian route or leader was found; its Arusha office's National Director post was last advertised in 2017.
6. **Fit:**
   - Organisations that run their own schools (peer schools):
     - Sun of Hope: Sun of Hope Primary School, English medium since 2021
     - SOS Arusha: its own kindergarten and primary and secondary school
     - Living Water: Yakini primary and secondary schools
     - KinderVilla Momella: Africa Amini Alama's Mukuru Primary School
     - CHETI: a network of eight schools
   - Other fit problems:
     - Peace House is a secondary school.
     - Tanzania Youth Support gives vocational training to youth, not residential care, so its segment is wrong.
     - One Heart Source's site now lists only Cape Town, so its Arusha work may have ended (flagged as a possible closure).
   - Strong fit: the Klingele Foundation pays private-school scholarships for 17 children in Tanzania but names no leader; write to its general inbox.
7. **Ucare Family Home:** its page asks sponsors to give directly to Neema Village, so the home may be run within Neema Village's record (possible duplicate).
8. **Incomplete or dated leads:**
   - "Mama Andrew" (Nkoaranga; page from about 2019)
   - "Geoffrey" (Tumaini; page published June 2019)
   - "Mama Salma" (Ummu Aisha; a carer as its UK supporter describes her, no title)
   - The Halima lead is the founding leader of 2017; the current head is not stated.
   - Dated sources: the Kilimanjaro Children's Fund GuideStar board (April 2019), the Sun of Hope GuideStar profile (September 2022), the CANDENEZ MIT Solve submission (March 2022) and the Ucare pages (about 2016-2019).
9. **Parent-body leads:**
   - Ummu Aisha's recorded leaders are the national leaders of Ansaar Muslim Youth Centre (HQ Tanga); its Arusha branch leader is not published.
   - Sun of Hope's are the congregation's US representative and US board chair; the sister in charge of the home is not published.
   - Tumaini's include YWAM Arusha's Base Leader.
10. **Kilimanjaro Children's Fund:** the only working routes are a Yahoo inbox that is not named after the fund and a US phone. Its latest update is from November 2021.
11. **Jericho Orphanage Home:** still unresolved between Usa River (Facebook) and Karatu (listings). It has no own domain and no named leader.

## Next-run priorities

- Browser pass (no search): thesmallthings.org, for Nkoaranga's head; Facebook pages stay closed under the rules.
- Organisations with no named decision-maker: Mshikamano, Living Water, Zorah, Tanzania Youth Support, the Klingele Foundation, Convoy of Hope Tanzania, SOS Children's Village Arusha, Peace House, Jericho and One Heart Source. Of these, SOS (its village director) and the Klingele Foundation (strong fit) matter most.
- Possible sources: ELCT North Central Diocese education office (Peace House); SOS Children's Villages Tanzania national office; IRS filings of the Klingele Foundation once available.
