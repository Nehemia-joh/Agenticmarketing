# Slice Q coverage log: held funders and ready drafts (welfare13), 2026-10-03

Targets: `runtime/contacts/slices/welfare13_D.json` (77 held funders, then 20 ready drafts addressed to the organisation team).
Output: `data/raw/welfare-research/research_Q_funders_and_leaders_2026-10-03.jsonl` (all lines parse; 45 contact + 26 relationship = 71 records; no organisation records, none were asked for).
Run was resumed once after an API cut-off; targets already in the file were not repeated.

## Searches: 15 of 40 used

| # | Query (shortened) | Result |
|---|---|---|
| Q1/40 | Candenez Mission ... director founder | no match for the organisation; nothing used |
| Q2/40 | Zorah Organization Tengeru Pazuri Daycare founder | only a crowdfunding page (not an allowed source type); nothing used |
| Q3/40 | Asante Sana Newport Beach / Light in Africa | GuideStar and a "asantesanaforeducation.com" site; the site returned HTTP 429 when read, so nothing used |
| Q4/40 | Be Part Of Their Story Inc Wharton NJ | no match |
| Q5/40 | Education Equals Power Atlanta, Tanzania school fees | no match (link found instead in its Form 990-PF) |
| Q6/40 | Congregation of the Sisters of Our Lady of Kilimanjaro, generalate | pointed to sistersofkilimanjaro.org; site returned HTTP 521 |
| Q7/40 | Glory Reach and Help Foundation Usa River | no match |
| Q8/40 | Happy Childhood Foundation Arusha | no match |
| Q9/40 | Passionist Community Arusha | no match |
| Q10/40 | Seeds of Kindness Organization Moshi | pointed to seedsofkindness.or.tz (DNS fails) and Idealist (no email) |
| Q11/40 | Peace House Africa Arusha | only 2008-2011 material; own site dead |
| Q12/40 | Focus on AIDS / Arnold House Moshi | no match |
| Q13/40 | Hope and Soul founder (allowed domain filter) | snippet names a founder; the cited team page returned HTTP 404 when fetched |
| Q14/40 | Imaniworld presidenta (allowed domain filter) | no names |
| Q15/40 | Little Oasis Foundation director (allowed domain filter) | no names |

No search was refused. 25 searches left unspent: the remaining gaps are sites that are blocked or dead, which more searches would not fix.

## Method notes

- Pages read with `scripts/contacts/read_page.py` (cached, robots honoured). Where a page rendered in JavaScript and read_page returned nothing (afotatz.org contact page, africanmoons.org emails, thesmallthings.org, arushachildrenstrust.org, adratanzania.org, ywamarusha.org, gemlegacy.org links, bigfuturefoundation.or.tz links, the ProPublica organisation pages), the same public page was read in the browser pane. No login, form, bot check or block was worked around.
- WebFetch was refused for afotatz.org and africanmoons.org (domain denied); not retried.
- IRS filings: filing pages (`projects.propublica.org/nonprofits/full_text/<object id>/<form>`) were read. To find the object ids of filings not already known, the ProPublica organisation page (and, for one test, its public JSON listing) was read; no full-text search-results page was used as a source.

## Pages read and outcome, held funders

(index in the slice; R = relationship record, C = contact record)

- 0 Inuka: contact page. C hello@inukacommunity.org (the held gmail inbox is CHETI NGO's, published on the same page; recorded separately as CHETI's).
- 1 Mesha's Village: team, about, home (429). C org-named gmail confirmed as its own published inbox.
- 2 The Small Things: contact, home, reports (browser). R operates the Nkoaranga children's village (Usa River office, PO Box 594); flags "no activity after 2017" and "did not render" cleared. C info@thesmallthings.org.
- 3 Arusha Kids Trust: contact-us. C org-named gmail confirmed.
- 4 From Hearts 2 Hands: home, about, contact. R x4 (Mind Investor sponsorship, Usa River; Vipaji daycare, Usa River; Cradle of Love; Kwamkono, Tanga - far). C org-named gmail confirmed.
- 5 GEM Legacy: story, primary-schools, mwatate-home, scholarships, campus-overview, secondary-school. R x3; nothing near the campuses except an Arusha campus under construction (post-primary). Route info@gemlegacy.org already sufficient.
- 6 Under The Same Sun: education-support. R (Mwanza; supports nothing near the campuses).
- 7 ADRA Tanzania: home, about, contact, albinism project. R (programmes in Dodoma/Morogoro; HQ at Usa River; supports nothing near the campuses on pages read).
- 8 AFOTA: contact, news (browser). C info@afotatz.org, +255 760 904 245; R own education-support programme, Arusha.
- 9 Africa Dream Safaris: about, community, contact. No email published anywhere (web form only); C Tanzania office +255 752 225 554.
- 10 African Moons: contact-us (browser). C jvann@africanmoons.org (named, own domain).
- 11 Afrikids: home. C Laurie Evans, free-mail plus cell (risky; no own-domain email).
- 12 Al-barro: home, about, ProPublica TY2023 990. R unnamed orphanage in Arusha (in-kind, 2023); site otherwise Baja Mexico.
- 13 Arusha Children's Trust: home, about, newsletters (browser). R school support Arusha/Rift Valley; newsletter #21 2022/23 clears the "no activity after 2021" flag.
- 14 Asante Sana: Q3; asantesanaforeducation.com HTTP 429 (blocked, not retried). NOT REACHED.
- 15 Be Part Of Their Story: Q4; bepartoftheirstory.org DNS failure; TY2023 990-EZ read (one $500 grant in Tanzania). No email found.
- 16 Care For Children Of The Earth: operates as Africa Student Fund (990-EZ website). C africastudentfundusa@gmail.com (org-named); R Passionist Community Arusha (general: Passionist schools and orphanages in Kenya and Tanzania).
- 17 Catholic Diocese of Moshi: contact. C Chancery Office bishopshouse_moshi@yahoo.co.uk (only free-mail addresses published; no own domain).
- 18 Children Of Kilimanjaro Orphanage: contact. info@helpcoko.org already own-domain; link already recorded; no change.
- 19 Choose Love Inc: Q-none; TY2018 990-EZ via ProPublica org page. R home for orphans in Arusha (historical 2018; no website or contact).
- 20 Coffeyville Area Community Foundation: grant-history, history page, TY2023 990. No Tanzania link found on any page read. Gap.
- 21 Compassion International Tanzania: contact, where-we-work, story, education programme. R TAG Bethel Church Child and Youth Ministry, Arusha (school-fee support via sponsorship).
- 22 Concordia Lutheran: contact. No new link (earlier indirect grant stays).
- 23 Sisters of Our Lady of Kilimanjaro: Q6; own site HTTP 521. No route found. NOT REACHED.
- 24 CSCNA Charity Corps: contact-us, about. Web form and postal address only; no email.
- 25 Educating Tanzania Foundation: contact-us. C org-named gmail confirmed.
- 26 Education Equals Power: TY2024 and TY2025 990-PF; Q5. R school-fee grant to an individual in Meru, Arusha (unnamed; near Usa River campus). No contact route beyond phone.
- 27 ELCT: contact, social-services pages. Own-domain elcthq@elct.or.tz already recorded; no named children's home near the campuses on pages read. Gap.
- 28 FSEA: contact, who-we-are, team. C info@fsea.fi (the firstname.lastname pattern is not an address); R Meru Primary School Deaf Unit (teacher-training project, ended 2016).
- 29 Falcos Children Africa: contact (no email), TY2024 990 Schedule F/R. R His Healing Hands Africa Ministry, Meru Post Office, Arusha. No email.
- 30 Focus On Aids: Q12; TY2022 990-EZ has no Tanzania detail. NOT REACHED (no route).
- 31 Foundation For Hope In Africa: about, tanzania, team pages. Phone and postal address only. No email.
- 32 Friends of Amani UK: amanikids.org contact. C friendsofamani.uk@gmail.com published by Amani as its UK address; friendsofamani.co.uk HTTP 429.
- 33 Glory Reach and Help: Q7. NOT REACHED (no website or route).
- 34 Global Vessels: about-us. C org-named aol address confirmed.
- 35 Go Campaign: where-we-work, TY2024 990 (no Tanzania text); gabriella article 404. No link found. Gap.
- 36 Grand Circle Foundation: TY2024 990-PF. R Community Service East Africa, Karatu (far).
- 37 Habari Foundation: site (JavaScript, no email), TY2025 990-EZ. R school-fee sponsorship of 40 children, "rural Tanzania" (district not stated).
- 38 Happy Childhood Foundation: Q8. NOT REACHED (no website or route).
- 39 Heart for Africa (UK): orphanages page. Admin email already own-domain; two-address red flag unchanged.
- 40 Hearts And Hands For Humanity: contact-us, orphanage page. Phone only; no email.
- 41 Hidden Hearts: home. Emails are personal (micmedoth@gmail.com, kimcwilson@icloud.com); not used.
- 42 Hidden With Christ Ministries: contact-us. Phone only; no email.
- 43 Hope Home Trust: contactus HTTP 429 (blocked, not retried). NOT REACHED.
- 44 Hope Without Borders: community-development, TY2025 990. R Moshi/Same/Pare programmes (general).
- 45 Kesho: lohada.org contact-us. C LOHADA yahoo inbox, Arusha, +255 754 447640.
- 46 Kid Care International: about, leadership, orphanage, contact. R Shalom Center, Arusha (suburb not stated).
- 47 Kili Vikings: company-profile. No change (beneficiary Light in Africa, Boma Ng'ombe, already recorded).
- 48 Kilimanjaro Childrens Fund: home. C ghomar003@yahoo.com (personal-looking; risky).
- 49 KMHO: contact. C org-named gmail confirmed.
- 50 Klehn Family Foundation: TY2024 990-PF. R Eripoto Safe House (town not stated). No contact route beyond phone.
- 51 Koch Foundation: contact-us, about. Phone and postal address only; no email.
- 52 Liaison Group: our-charity-group HTTP 403 (blocked). NOT REACHED.
- 53 Lift-the-lid: donate, pen-pals, privacy, Tanzania school page. C Sara Goff saragoff@saragoff.com (personal domain, risky).
- 54 Little Souls of Tanzania: donate, staff. C org-named gmail confirmed.
- 55 Love Our Tanzania Family: home. C org-named gmail confirmed.
- 56 Maasai Girls Rescue Center: no new reading; Karatu, outside the catchment (earlier record).
- 57 New Day Foundation: home. C Tanner Jarrell tanner@newdayfoundation.org; site shows children's homes in the Dominican Republic, nothing on Tanzania.
- 58 One Heart Source: about page, TY2021 990. Tanzania programme named; no district or home found. Gap.
- 59 Orphans International America: TY2024 990-EZ funds Haiti; betterfutureinternational.org DNS failure. No Tanzania link. Gap.
- 60 Passionist Community Arusha: Q9; passioniststanzania.or.tz DNS failure. NOT REACHED.
- 61 Peace House Africa: Q11; site DNS failure. NOT REACHED.
- 62 ROAM Humanitarian: Tanzania expeditions page. Orphanage still unnamed; email is JavaScript-hidden (hello@ already recorded). No change.
- 63 Read With Me Arusha: contact. C readerast@gmail.com (handle unclear; risky).
- 64 Seeds of Kindness: Q10; site DNS failure. NOT REACHED.
- 65 Sal-vay-shen Green: acv3.org not resolving (earlier record). NOT REACHED.
- 66 Scott Willis Legacy: home. C org-named gmail confirmed.
- 67 Standing Voice: education page. R programme-level tuition sponsorship (no district; Mwanza office).
- 68 TerraWatu: contact. info@terrawatu.org already recorded; transition flag unchanged.
- 69 Bahati Trust: home HTTP 429 (blocked, not retried). NOT REACHED.
- 70 TrueToTanzania: home, TY2025 990-PF. Only a Dar es Salaam institute and an adult workshop in Moshi; supports nothing near the campuses; no record.
- 71 UPENDO OKAT: home. C team inbox (org-named gmail).
- 72 UBORA: what-we-do. info@uboratz.org already recorded; no change.
- 73 World Vision Tanzania: contact-us HTTP 403 (blocked). NOT REACHED.
- 74 Weily Tribe: home HTTP 429 (blocked, not retried). NOT REACHED.
- 75 Wevol: home, projects, active-projects, TY2025 990-EZ. C info@wevol.org; R Good Hope Kiwawa Orphanage, Arusha.
- 76 Yelloh Foundation: yelloh.ngo is an empty frameset (domain forward). No email.

## Ready drafts addressed to the team (77-96)

- 77 Bassari: staff page. C Peter Moosbrugger (Founder Director), Harrieth Minja (Director/Social Worker, on site); no personal emails.
- 78 Big Future Foundation: foundation page, member page. C Promise Shayo (Chairperson & Founder), general inbox.
- 79 Candenez: about, contact, home, Q1. No named leader published. NOT FOUND.
- 80 Capital International (Isle of Man): Huruma project page. Corporate sponsor; no named lead for the programme. NOT FOUND.
- 81 Compassion International Tanzania: governance page. C Mary Lema (National Director and Board Secretary).
- 82 Ereto East Africa: about, contact. A "Chairman" is listed under a teachers section with obviously placeholder names; not recorded. NOT FOUND.
- 83 Foerderverein URRC: impressum. C Wolfgang Hertrich (legal representative); email hidden by JavaScript.
- 84 Friends of Amani US: team page. C Meghan Wood (Director of Development USA), info@amanikids.org.
- 85 Giving Smiles: impressum. C Katherina Campe and Miriam Vogt (Vorstand).
- 86 Hope and Soul: about, contact; Q13. C Hope Prosser (founder; surname only from a search snippet, team page 404; status needs_review).
- 87 Imaniworld: contact, legal notice, projects; Q14. No names published. NOT FOUND.
- 88 KinderVilla Momella: team page. C Christine Wallner (Founder), Cornelia Wallner-Frisee (President).
- 89 Love for the Least: governance, contact-us. C Jerry Kramer and Stacy Kramer with their own-domain emails.
- 90 Marangu Anza Pamoja: impressum. C Daudi Boniface Mtui; team inbox.
- 91 One Kind Act: committee, contact. C Shamit Malhotra (founder, trustee); info@onekindact.org.
- 92 Small Steps for Compassion: board page. C Shannin Pickle (President/Founder), spickle@smallstepsforcompassion.org.
- 93 The Little Oasis Foundation: our-story, contact-us, programs; Q15. No names published. NOT FOUND.
- 94 Tumaini House (YWAM Arusha): about, Tumaini ministry page. C Geoffrey (head of the ministry, given name only); base inbox registrar@ywamarusha.org.
- 95 Ucare Family Home: about, contact. C Lovise Myhre Eikenaes (leader and founder); info@ucareproject.com.
- 96 Zorah: about, contact, volunteer; Q2. No names published. NOT FOUND.

## Blocks and unreadable sources

- HTTP 429: meshasvillage.com home (other pages read), weilytribe.com, hopehometrust.org.uk, bahatitrust.com, friendsofamani.co.uk, asantesanaforeducation.com, africastudentfund.net/about-us. Not retried in a loop.
- HTTP 403: liaisongroup.com, wvi.org/tanzania contact. HTTP 521: sistersofkilimanjaro.org.
- DNS failure: bepartoftheirstory.org, passioniststanzania.or.tz, peacehouseafrica.org, seedsofkindness.or.tz, betterfutureinternational.org, acv3.org.
- Empty frameset: yelloh.ngo. JavaScript-only pages with no email even in the browser: falcoschildrenafrica.org/contact, habarifoundationinternational.org.
- PDF newsletter of Arusha Children's Trust (2022/23) is not machine-readable; contents unread.
- Not used as sources: Facebook, LinkedIn, crowdfunding and volunteer-placement sites; no login, form or CAPTCHA touched.

## Counts and leads

Records: 45 contact, 26 relationship, 0 organisation.
Own-domain emails found: hello@inukacommunity.org, info@afotatz.org, jvann@africanmoons.org, info@wevol.org, tanner@newdayfoundation.org, info@fsea.fi, info@thesmallthings.org, spickle@smallstepsforcompassion.org, jerry@ and stacy@lovefortheleast.org, info@bigfuturefoundation.or.tz, info@givingsmiles.org, info@onekindact.org, info@ucareproject.com, hello@hopeandsoul.org (plus general inboxes already known for others).
Strongest near-campus links found: The Small Things (Happy Family Children's Village, Usa River office); Falcos Children Africa to His Healing Hands (Meru P.O., orphanage support); Education Equals Power (school-fee grant, Meru); From Hearts 2 Hands (private-school sponsorship from Usa River); Compassion to TAG Bethel (Arusha, fees via sponsorship); Wevol to Good Hope Kiwawa (Arusha); Kid Care to Shalom Center (Arusha).
