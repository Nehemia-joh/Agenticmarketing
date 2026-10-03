# Slice R coverage: welfare funder relationships (welfare12_R), 2026-10-02

Targets: `runtime/contacts/slices/welfare12_R.json` (78 held welfare funders), then the 12 funders whose only source was a ProPublica search page.
Output: `data/raw/welfare-research/research_R_funder_relationships_2026-10-02.jsonl` (203 lines, every line parses).
Pages were read with `scripts/contacts/read_page.py` (shared cache, robots honoured, 1.5 s spacing) and small helpers under `runtime/contacts/agents/welfare12_R/` that use the same fetcher. The work ran across midnight into 2026-10-03; `accessed_on` is set to the brief's research date, 2026-10-02.

IRS 990 sources are ProPublica filing pages (`/nonprofits/full_text/<object id>/<form or schedule>`), never full-text search pages. ProPublica's organisation search (`/nonprofits/search`) is disallowed by robots.txt and was not used.

## Records written

- Organisation: 81
- Relationship: 75 (funds historical: 1, funds needs_review: 9, funds verified: 46, operates needs_review: 3, operates verified: 14, partners_with verified: 2)
- Contact: 47

## Searches (allowance 15; used 3)

- Q1/15 "Choose Love" Charleston SC orphans Arusha Tanzania home -> no result for the charity
- Q2/15 Passionist Fathers Arusha Tanzania orphanage children home Passionists -> no Passionist home found
- Q3/15 "Door of Hope" Maasai Ministry girls home Tanzania -> only video/wiki/blog results; location not confirmed from an allowed source

## Pages read per target

- Afrikids: afrikidsinc.org/the-schools; 990-EZ TY2024 full_text 202540939349200204
- Asante Sana: ProPublica org 371654466; 990 TY2024 full_text 202533179349310393 (names Light In Africa, Boma)
- Be Part Of Their Story: 990-EZ TY2023 202400649349201300, TY2022 202310469349200511, TY2021 202210759349200511 - grantee not named
- Care For Children Of The Earth: 990-EZ 202610689349200146, 202500579349201035, 202420889349200707 - Passionist schools/orphanages Kenya+Tanzania, none named
- COKO: helpcoko.org/, /pages/contact, /pages/staff; 990 202621529349300342
- Cscna: 990 202641039349300804 (Emusoi Center Arusha)
- EdPowerment: 990 202631259349301993; edpowerment.org/sponsorships/, /our-story/
- Educating Tanzania Fdn: 990 202630639349301483; educatingtanzaniafoundation.com/what-we-do
- Education Equals Power: 990-PF 202632259349101003, 202531359349100623 (individual grant Nshupu), 202423209349102162
- Falcos: 990 202533219349316473 + ScheduleF + ScheduleO; falcoschildrenafrica.org /, /about/, /a-word-from-our-hearts/ (no text, JS)
- Focus On Aids: 990-EZ 202333169349200238 (AIDS research; no home)
- Foundation For Hope: 990-EZ 202601409349201015 (Kim Jones House Moshi)
- Grand Circle: 990-PF 202523249349100102 (Karatu only); grandcirclefoundation.org/locations/tanzania/
- Habari: 990-EZ 202621219349201902
- Hearts and Hands: 990-PF 202543229349100904; heartsandhandsforhumanity.org/hearts-and-hands-for-humanity-orphanage/
- Hidden Hearts: hiddenhearts.org; 990-EZ 202622309349201212
- Hidden With Christ: 990 202621369349301107; treasuresofafrica.org/about
- Kesho: 990 202631229349300613 + ScheduleF + ScheduleO; lohada.org/about-lohada/
- Kidcare: 990-EZ 202541339349202824; kidcare.org/education/sponsor-a-child/, /about/, 2025 news post (child story - read, not cited)
- Kilimanjaro Childrens Fund: 990-EZ 202640489349201714; kili-childrensfund.org/
- KMHO: kmho.org/sponsorships/child/, /contact/; 990 202522959349301537
- Klehn: 990-PF 202632049349100223, 202513179349100146, 202441289349104054 (no Tanzania)
- Koch: 990-PF 202610479349100866 (grant list, Arusha/Moshi lines)
- Love Our Tanzania: 990-EZ 202601259349202090
- Maasai Girls: 990 202522539349301417; maasairescue.org/about-us/ (redirect to /)
- Neema Village: 990 202513189349314101
- One Heart Source: 990 202233199349324478 (TY2021 latest); org page filings list
- Sal-vay-shen Green: 990-EZ 202523219349211352
- Scott Willis: 990-PF 202630479349100518 (Shades of Hope Arusha)
- Small Things: 990 202601669349300615
- TrueToTanzania: 990-PF 202611359349104641; truetotanzania.org/
- Uboratz: 990 202533169349307428; uboratz.org/what-we-do (nav only)
- Wevol: 990-EZ 202541619349201104
- Yelloh: 990-PF 202502169349100220
- Africa Amini Alama: africaaminialama.com/projekte/soziales
- Africa Dream Safaris: /community/, /community/humanitarian/peace-house-orphanage/, /contact/
- Al-barro: albarrofoundation.org/, /about/
- ACT: arushachildrenstrust.org/ (no text), /about.html
- Arusha Kids Trust: arushakidstrust.com/ (200 after one 429), /news-events
- ALMC: theplasterhouse.org/about-us-our-partners
- ANGONET: angonet.or.tz/about-us/
- Capital International: capital-iom.com/company/huruma-project, /contact-us
- Imaniworld: imaniworld.org/en/, /en/contact/
- TerraWatu: terrawatu.org/, /current-projects/huruma-orphanage
- Diocese of Moshi: moshidiocese.org/contact; rainbow-centre.blogspot.com
- Coffeyville: coffeyvillefoundation.org/cacf-grant-history.cfm
- Compassion: cit.or.tz/where-we-work/, /download/annual-report-2025/ (no text); allafrica.com/stories/202609140381.html
- Amani (FOA UK, Innovo, Liaison): amanikids.org/global-network, /partners, /contact-us
- Global Vessels: globalvessels.org/orphanage/, /about-us/
- Go Campaign: gocampaign.org/, /where-we-work; /articles/gabriella-center-visit 404
- Heart for Africa: heartforafrica.co.uk/orphanages
- Hope Home Trust: ngoexplorer.org/charity/1126415
- Inuka: inukacommunity.org/cheti-ngo
- Kili Vikings: kilivikings.com/company-profile/
- Lift-the-lid: lift-the-lid.org/how-it-works/, /schools/tanzania/happy-family-childrens-village/
- Little Souls: littlesoulsoftz.org/
- New Day: newdayfoundation.org/
- Passion Projects: passionprojectsintl.com/afroplan-foundation, /new-page, /our-team
- Private Explorers: tuleenihome.org/friends-of-tuleeni/
- ROAM: roamhumanitarian.org/expeditions/tanzania/
- Read With Me: readwithmearusha.com/where-we-work/karim-orphanage/, /samaritan-village/
- SOS: sos-tanzania.org/.../arusha
- Standing Voice: standingvoice.org/education
- UPENDO OKAT: upendookat.com/about-us
- Under The Same Sun: underthesamesun.com/education-support/
- Weily Tribe: weilytribe.com/copy-of-umoja-orphanage
- ZARA: zaratanzaniacharity.org/ (project pages 404/500)
- ELCT: elct.org (https SSL failure; http redirect), elct.or.tz/index.php/contact/, /social-services-women-and-children/
- Hope Without Borders: hwb-intl.org/, /community-development, /about-us

## Re-sourced funders (previously only a ProPublica search page)

- Arthur B Schultz: 990-PF 202533219349104043
- Asali: 990-EZ 202523109349201572; asaliproject.org/, /partners (->/partnership/)
- Concordia: 990 202621109349301077 + ScheduleI + ScheduleO
- Faraja Fund: 990 202523519349301607 (+ schedules)
- Friends of Tanzania: 990-EZ 202533039349201363 + ScheduleO
- Global Development Group: 990 202601489349300515 + ScheduleF; globaldevelopmentusa.org (projects JS-rendered)
- Godparents: 990-EZ 202631259349201878 + ScheduleO
- Karama: 990-EZ 202611359349200821 + ScheduleO (EIN 10832165 on ProPublica)
- My Daily Armor: 990-EZ 202630409349200538; mydailyarmor.org/
- Opportunity Builds Africa: 990 202601829349301655 (+ schedules)
- Utopia: 990 202503219349317750 + ScheduleF + ScheduleO
- Vibrant Village: 990-PF 202513089349100321

## Blocks (recorded, not worked around)

- africastudentfund.net/about-us HTTP 429
- passioniststanzania.or.tz/entities/arusha/ DNS failure (getaddrinfo)
- WebFetch denied for falcoschildrenafrica.org (tool permission)
- habarifoundation.org bot verification page
- arushakidstrust.com/about-us HTTP 429 (not retried)
- peacehouseafrica.org DNS failure
- hopehometrust.org.uk HTTP 429
- meshasvillage.com HTTP 429
- waterforlifecharity.org arusha-orphanage-well HTTP 403
- bahatitrust.com HTTP 429
- ProPublica /nonprofits/search disallowed by robots.txt (not used)
- falcoschildrenafrica.org pages return no readable text (script-rendered).
- globaldevelopmentusa.org project search is script-rendered.
- zaratanzaniacharity.org project pages returned 404/500; gocampaign.org Gabriella article returned 404.

## Targets with no current catchment link, or not confirmed

- Be Part Of Their Story Inc: No current link to the catchment confirmed: the three latest 990-EZ filings name no grantee (the earlier Grace Orphanage, Moshi link came only from a ProPublica search page and is not confirmed by the filings). Grants are very small ($500 in 2023). Phone is the organisation telephone in the 990 header.
- Education Equals Power Inc: No named home or programme: grants are school fees paid to a named private individual in Nshupu, Meru (the individual is not recorded). The TY2023 990-PF shows the same pattern. Website field reads N/A. Phone is the books-in-care-of number in the 990-PF.
- Falcos Children Africa Inc: No named home confirmed: the TY2024 990 and Schedule F name only 'orphanage support' in Tanzania and Kenya. The earlier His Healing Hands Africa Ministry (Meru) link came from a ProPublica search page and is not re-confirmed. The charity's own pages returned no readable text (script-rendered) and WebFetch was not permitted for the domain.
- Focus On Aids: No current link to the catchment: the latest 990-EZ describes donations to AIDS research centres and names no home; the Arnold House AIDS Orphanage (Moshi) link came only from a ProPublica search page and is not confirmed. Latest filing found is from 2023.
- Grand Circle Foundation Inc: No current link to a home in the catchment: the TY2024 990-PF lists Tanzanian grants to Karatu primary schools, a Karatu scholarship fund and a $1,000 Arusha water-filter grant; Eripoto Safe House is not listed in the 2024 grants or on the Tanzania page.
- Klehn Family Foundation: No current link to the catchment: the TY2023, TY2024 and TY2025 990-PF filings list no Tanzanian or Eripoto grantee. The earlier Eripoto Safe House link came only from a ProPublica search page. Phone is the books-in-care-of number (Finch & Associates, an accountant), not the foundation's own line.
- Maasai Girls Rescue Center Inc: No link to the catchment: its only home is in Karatu. Phone is the organisation telephone in the 990 header (US). /about-us/ redirects to the home page.
- One Heart Source: No current link confirmed: the latest filing on ProPublica is for 2021 (filed 2022) and names no home or town. Phone is the organisation telephone in that 990 header.
- TrueToTanzania: No current link to a home or programme in the catchment: the TY2025 990-PF lists a single $560 tuition grant for one student at a Dar es Salaam institute (the student is not recorded); the site is mainly expeditions and safaris. Phone is the books-in-care-of number in the 990-PF.
- Al-barro Foundation: No link to the catchment: its own About page describes orphanages in Baja, Mexico and medical aid in Nicaragua, with no Tanzanian or Arusha programme. The earlier link came only from a ProPublica search page.
- Arusha NGO Network (ANGONET): No funding or operating link to a named home or programme found: ANGONET is a coordination network of Arusha NGOs, not a funder. Better used as a referral route to member children's homes than as a sponsorship target.
- Coffeyville Area Community Foundation Inc: No current link to the catchment: the foundation's own 2024-2025 grant history lists no African or Tanzanian grantee. The Light in Africa link came from a ProPublica search page (likely a donor-advised pass-through) and is historical.
- Go Campaign: No current link: the Gabriella Centre (Moshi) article now returns 404 and Tanzania is not on the Where We Work page; the earlier link is historical.
- New Day Foundation Inc: No current link confirmed: its home page mentions children's homes generally but names no home or country; the Children of Destiny / New Life Christian Children's Home (Moshi) link came only from a ProPublica search page. 'Partner with us' goes to a third-party donation form.
- ROAM Humanitarian: No named home: the Tanzania expedition page lists 'ROAM Education Center, Orphanage... Special Needs School' without names. The Water for Life Arusha orphanage-well page returned HTTP 403.
- Standing Voice: No named home or programme in the catchment: runs a national sponsorship for students with albinism at mainstream schools, but the education page names no school or region near the campuses. A possible fit only if it places students in Arusha/Kilimanjaro.
- The Bahati Trust for Orphans in Tanzania: Not confirmed: the site returned HTTP 429. Earlier records place it in Dar es Salaam, with no Arusha/Kilimanjaro link.
- Under The Same Sun: No link to the catchment confirmed: the programme places students in boarding schools via Village of Hope Mwanza and names no school near the campuses.
- Evangelical Lutheran Church in Tanzania (ELCT): No named home confirmed on ELCT's own pages; the department page lists programmes but no children's home. Its catchment links run through dioceses and institutions (e.g. Arusha Lutheran Medical Centre, a hospital of the ELCT North Central Diocese, runs The Plaster House). elct.org (https) failed an SSL handshake; http redirected.
- Choose Love Inc: No current link confirmed: no own website found and one web search (Q1) returned nothing about this charity; the 'Choose Love home for orphans (Arusha)' link came only from a ProPublica full-text search page and stays unconfirmed. EIN not on record, so the filing page could not be reached (ProPublica's search is robots-disallowed).
- Orphans International America: No current link: no own website or filing page found in this run (EIN not on record; ProPublica search is robots-disallowed). The Better Future International Tanzania (Moshi) link is historical.
- Passionist Community Arusha: No named home or route confirmed: the Passionists Tanzania site did not resolve and one web search (Q2) found no Passionist orphanage in Arusha. A US funder (Care For Children Of The Earth) supports Passionist-run schools and orphanages in Kenya and Tanzania without naming them.
- Mesha's Village: Not re-read: the site returned HTTP 429. The earlier verified links (funds Ngarasero Community Organization, Usa River; tuition at Haradali School) rest on news reports and the charity's own home page from the September run.
- Global Development Group USA Inc: Filing re-sourced but no named home: Schedule F lists Sub-Saharan Africa grants by purpose only, and the project search on its site is script-rendered. The Sandra Jones Centre link is not confirmed.
- Hope Without Borders-USA Inc: No current link to the catchment: the charity's own pages name no Tanzanian project; the St Joseph Shelter of Hope (Moshi) link came from a ProPublica search page and is historical. EIN not on record, so no filing page was read.

## Notes for the coordinator

- The sponsorship-hook code (`scripts/messaging/draft_run_messages.py`, `funder_reasons`) counts only `funds` relationships. Funders that run their own home or programme (`operates`), e.g. Africa Amini Alama, Hidden With Christ Ministries, The Small Things, Neema Village, SOS, UPENDO OKAT, Uboratz, EdPowerment, Kilimanjaro Childrens Fund, Godparents For Tanzania, will stay held unless the code also accepts `operates`.
- Several relationship targets are named as published and may not match the run's names exactly (e.g. Havilah Children's Village vs Havilah Children's Orphanage; Upendo Orphanage vs Upendo Children's Home).
- Email correction: ZARA publishes info@zaratanzaniacharity.org (the run holds .com).
- New Tanzanian phones: Africa Dream Safaris Tanzania office +255 752 225 554; Catholic Diocese of Moshi chancery +255 272 752 157.
- Child-identity exclusion: a KidCare news post about a former resident was read but not cited.
