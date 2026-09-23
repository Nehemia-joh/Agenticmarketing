# Coverage log: wave 3, welfare funders and specialised centres

Run date: 2026-09-23. Slice: `runtime/contacts/slices/wave3_welfare_funders_specialised.json` (61 organisations: 20 specialised centres, nearest first, then 41 funders). Results: `data/raw/contact-research/search_wave3_welfare_funders_specialised_2026-09-23.jsonl`.

Search budget: 53 WebSearch calls. The order of work was:

1. Fetch known sources and URLs that earlier runs cite (no search).
2. Search the centres in slice order, one organisation per query.
3. Search the funders, school-fee and catchment grants first.

All pages were read with this agent's own polite fetcher: robots.txt checked, at least 2.2 seconds between requests to one host, and no retry on a block. The WebFetch tool was not used.

## Summary

- **Researched:** 56 of 61 organisations (one JSONL line each).
  - found: 26
  - partial: 13
  - not_found: 14
  - blocked: 3
  - Identity confirmed for 49. Uncertain for 7: Angazia, Emayani, Ability in Disability Tanzania, Kilimahewa, Care For Children Of The Earth, Asante Sana and Habari Foundation International.
- **Searches used:** 53 of 53. The session's search limit was never refused. Five organisations were not reached (listed at the end).
- **Contact leads recorded:** 58 people in 25 organisations.
  - `medium`: 57
  - `risky`: 1 (Hidden Hearts Foundation's co-founder, whose only published contact is a personal iCloud inbox)
  - One lead is snippet-only (`fetched: false`): Liaison Group's chairman, because the page answered 403.
- **Organisations with a published email or phone for the first time:** 26, with identity confirmed.
  - Centres (4): Kahe Home, Second Chance Education Centre, Songambele Initiative, Autism Beyond Borders TZ (routes of its US parent).
  - Funders (22): Utopia Foundation, SOS Children's Villages Tanzania, Afrikids, Arthur B Schultz Foundation, Koch Foundation, Asali, Vibrant Village Foundation, Grand Circle Foundation, Hidden Hearts Foundation, Scott Willis Legacy Foundation, Godparents For Tanzania, ELCT, Concordia Lutheran Ministries Foundation, Friends of Tanzania, Hearts and Hands for Humanity, TrueToTanzania, My Daily Armor Ministries, Innovo Benefits Group, Al-barro Foundation, Hope Without Borders-USA, Global Development Group USA, Coffeyville Area Community Foundation.
  - Four more records carry routes with identity uncertain, so they are not counted: Emayani (Emayani Foundation's routes), Ability in Disability (Faraja Fund Foundation's US office), Kilimahewa (its successor school) and Care For Children Of The Earth (Africa Student Fund).
- **Totals recorded:** 35 emails, 26 phones, 57 official social pages and 40 websites.
  - Email types: 15 general, 8 role, 7 named work, 5 personal-domain inboxes named after the organisation.
- **Search yield:**
  - 30 of the 53 searches found the organisation's own site or official page.
  - 13 found nothing under the name. Most of these were NIS-only centres and small or dormant funders.
  - The rest found only a social page, or a site that turned out to be blocked, dead or disallowed.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/53 | `"Eripoto" Arusha` | Eripoto Safe House | Official Facebook page (not read); no email or phone. Other results were third-party platforms |
| Q2/53 | `"Angazia" NGO Tanzania children talents mental health psychology` | Angazia | Nothing for this NGO. "Angazia Jamii Kiuchumi" (Moshi Urban) is a different NGO |
| Q3/53 | `"Ability in Disability" Tanzania Arumeru children` | Ability in Disability Tanzania | Nothing under this name |
| Q4/53 | `"Huduma ya Fahari Kubwa" Arusha` | Huduma ya Fahari Kubwa Foundation | Nothing under this name |
| Q5/53 | `"YOSIMODO" Arusha young single mothers disability` | YOSIMODO | Nothing under this name. FAYOWODO and Sibusiso are different organisations |
| Q6/53 | `"Kahe Home" Moshi intellectual disabilities children` | Kahe Home | **kahe-home.my.canva.site**: inbox, mobile, P.O. Box, founder; Facebook. A snippet about the founder's family was discarded |
| Q7/53 | `"Disability Repro" Light Organization Arusha Tanzania` | Disability Repro-Light | Own site found in the index, but the domain no longer exists (website gone) |
| Q8/53 | `"Jamii Jasiri" Arusha` | Jamii Jasiri | Nothing under this name |
| Q9/53 | `"Building a Caring Community" Moshi Kilimanjaro disabilities` | BCC | Own site found (HTTP 522 on every try); Facebook and X pages |
| Q10/53 | `"KWIECO" Moshi women legal aid shelter` | KWIECO Shelter House | Official Facebook page. The other results were architecture articles |
| Q11/53 | `"St Francis of Assisi" primary school disabled orphans Moshi` | St Francis of Assisi school (Moshi) | Identified (run by the Sisters of Our Lady of Kilimanjaro; about 4.5 km outside Moshi on the highway) but no route. Pupil details not recorded |
| Q12/53 | `"Second Chance Education Centre" Moshi` | Second Chance Education Centre | **secondchancemoshi.wixsite.com/firstchance**: P.O. Box, mobile, inbox, founder, head teacher |
| Q13/53 | `"TAFCOM" Moshi Tanzania legal aid women children` | TAFCOM | Own site (TLS failure) and Facebook (Old Moshi) |
| Q14/53 | `"Songambele Initiative" Moshi` | Songambele Initiative | **songambele.org**: inbox, mobile, P.O. Box, office (Kili Hub, Majengo), socials |
| Q15/53 | `"Tanzania Inclusive Education Support Organization" TIESO` | TIESO | Nothing under this name or acronym |
| Q16/53 | `"Autism Beyond Borders" Tanzania Moshi` | Autism Beyond Borders TZ | **autismbeyondborders.org** (US parent): director's work email and phone; socials |
| Q17/53 | `"Siloam International Africa" Moshi` | Siloam International Africa | Nothing under this name |
| Q18/53 | `"Deaf Hands Foundation" Arusha Tanzania` | DEHAFO | Nothing under this name |
| Q19/53 | `"Afrikids" Coral Gables Tanzania Arusha school fees` | Afrikids | **afrikidsinc.org**: inbox, cell, six leaders. Street address residential (city only) |
| Q20/53 | `"CSCNA Charity Corps" Cupertino Tanzania` | Cscna Charity Corps | **cscnacc.org**: P.O. Box, contact form, 2023 executive board and board chair |
| Q21/53 | `"Arthur B. Schultz Foundation" Lander Wyoming grants Africa` | Arthur B Schultz Foundation | **absfoundation.org**: inboxes, phone, P.O. Box, executive director; spending down by 2035 |
| Q22/53 | `"Koch Foundation" Gainesville Florida Catholic evangelization grants` | Koch Foundation | **thekochfoundation.org**: office address and phone; requests go through its portal |
| Q23/53 | `"Asali" nonprofit Salem Massachusetts Moshi Tanzania community center` | Asali | **asaliproject.org**: inbox, board officers; Moshi partner is Simba's Footprints Foundation |
| Q24/53 | `"Vibrant Village Foundation" Beaverton Tanzania` | Vibrant Village Foundation | **vibrantvillage.org**: inbox, mailbox address, founder, executive director, East and Southern Africa director |
| Q25/53 | `"Grand Circle Foundation" Tanzania Arusha school` | Grand Circle Foundation | **grandcirclefoundation.org**: role inbox, toll-free phone, Boston office |
| Q26/53 | `"Yelloh Foundation" Scottsdale Arusha orphanage` | Yelloh Foundation | Facebook only, plus a sponsor company's feature page. Officer names came from directories (not used) |
| Q27/53 | `"Hidden Hearts Foundation" Houston Tanzania Osiligi` | Hidden Hearts Foundation | **hiddenhearts.org**: phone, co-founders. Street address residential (city only) |
| Q28/53 | `"Scott Willis Legacy Foundation" Fallston Arusha` | Scott Willis Legacy Foundation | **scottslegacy.com**: inbox, phone, P.O. Box, co-founders |
| Q29/53 | `"Godparents for Tanzania" Raleigh` | Godparents For Tanzania | **godparents4tz.org**: inbox, P.O. Box, founder |
| Q30/53 | `"Habari Foundation" Moshi Tanzania Michigan school` | Habari Foundation International | Facebook page (identity uncertain). A partner school page answered 403 |
| Q31/53 | `"Evangelical Lutheran Church in Tanzania" head office Arusha contact` | ELCT | Own contact page (expired certificate: snippet only) and the LWF member-church directory: presiding bishop, role inbox, phones, P.O. Box |
| Q32/53 | `"Concordia Lutheran Ministries" Foundation Cabot Tanzania Moshi VOV` | Concordia Lutheran Ministries Foundation | Parent's site concordialm.org: the Foundation's giving inbox and extension |
| Q33/53 | `"Friends of Tanzania" "Marafiki wa Tanzania" Washington grants` | Friends of Tanzania | **fotanzania.org**: inbox, mailbox address, board officers, projects-committee chair. The two quoted parts are one organisation's two-language name |
| Q34/53 | `"Hearts and Hands for Humanity" Riverton Utah Tanzania orphanage` | Hearts and Hands for Humanity | **heartsandhandsforhumanity.org**: office, phone, CEO and officers; runs an orphanage in Moshi |
| Q35/53 | `"Care for Children of the Earth" Louisville Tanzania Passionist` | Care For Children Of The Earth | Nothing under this name. The Africa Student Fund (Louisville, Passionist) is a probable working name (unconfirmed) |
| Q36/53 | `"Asante Sana" Newport Beach charity Tanzania Moshi` | Asante Sana | Probable own page on tanzaniamissions.com (robots.txt disallows it); Facebook (uncertain) |
| Q37/53 | `"TrueToTanzania" OR "True to Tanzania" Winston-Salem foundation` | TrueToTanzania | One organisation, two spellings. **truetotanzania.org**: three named inboxes, phone, mailbox address |
| Q38/53 | `"Education Equals Power" Atlanta Tanzania scholarship` | Education Equals Power | Directories only; no route |
| Q39/53 | `"My Daily Armor Ministries" Louisville` | My Daily Armor Ministries | **mydailyarmor.org**: inboxes, phone, P.O. Box, founder |
| Q40/53 | `"Falco's Children Africa" Oklahoma Tanzania` | Falco's Children Africa | Village Facebook page. The own site served a bot check; a ministry-network profile is disallowed by robots.txt |
| Q41/53 | `"Kilimahewa" Moshi children education center` | Kilimahewa | Converted in 2021 into Kilimahewa Modern Secondary School; the successor's routes recorded (identity uncertain) |
| Q42/53 | `"Sal-vay-shen Green" Fallbrook` | Sal-vay-shen Green | No route. Its filing address is a private house (not recorded) |
| Q43/53 | `"Klehn Family Foundation"` | Klehn Family Foundation | Directories only; no route |
| Q44/53 | `"Innovo Benefits Group"` | Innovo Benefits Group | **innovobenefits.com**: inbox, phone, office |
| Q45/53 | `"Liaison Group" UK Amani street children Tanzania support` | Liaison Group | Own pages answered 403. The chairman appears in a snippet |
| Q46/53 | `"Al-barro Foundation" Glendale` | Al-barro Foundation | **albarrofoundation.org**: inbox, phone, office, chair, secretary and treasurer role inboxes |
| Q47/53 | `"Wevol" Boulder Colorado nonprofit Arusha orphanage` | Wevol | No route. The Zeffy page is an unclaimed auto-profile |
| Q48/53 | `"Orphans International America" Tanzania` | Orphans International America | No route. Split from Orphans International Worldwide in 2009 (Wikipedia) |
| Q49/53 | `"Hope Without Borders" West Bend Wisconsin Tanzania` | Hope Without Borders-USA | **hwb-intl.org**: inbox, 2025 board chair, vice chair and a director with work inboxes. Street address residential (city only) |
| Q50/53 | `"Choose Love Inc" Charleston South Carolina orphans Tanzania` | Choose Love Inc | Nothing for this charity (the UK refugee charity is different) |
| Q51/53 | `"Global Development Group USA" Bedford Indiana Tanzania projects` | Global Development Group USA | **globaldevelopmentgroup.org**: US inbox and phone; EIN matches. Postal address residential (city only) |
| Q52/53 | `"Aiding Children's Villages" Tanzania Moshi` | Sal-vay-shen Green (second search) | Snippet of acv3.org confirms the trading name. The domain does not exist (DNS) |
| Q53/53 | `"Coffeyville Area Community Foundation" Kansas` | Coffeyville Area Community Foundation | **coffeyvillefoundation.org**: inbox, phone, P.O. Box, office, executive director |

Search budget reached at Q53/53. After that, only URLs already in hand were fetched: the Coffeyville site from Q53, and one retry of BCC's About page after its HTTP 522. No domains were guessed and no search-results pages were fetched.

### Reached without a search (searches_used = 0)

- **Utopia Foundation.**
  - The earlier welfare-care run cited utopiafound.org. The old guess utopiafoundation.org refused connections and was not retried.
  - Team page: executive director with a work inbox, founder, board president, treasurer. Contact page: Traverse City office.
- **SOS Children's Villages Tanzania.**
  - The earlier welfare run cited the national site sos-tanzania.org.
  - It gives the national-office inbox, two phones, a P.O. Box and address, the national director and the board chair.
- **Lift-the-lid.** Its known site gave the founder, a Facebook page and a tax ID matching the filing; no inbox or phone.
- **Emayani vulnerable people's center.**
  - The foundation's home, About and Activities pages were re-read.
  - None of them mentions Sombetini, a centre or children, so identity stays uncertain.

## Blocked or unreadable sources

- **Rate limits and bot checks (not bypassed):**
  - eripoto.org: HTTP 429 on the contact and About pages, after one home-page read. Wave 1's evidence was reused.
  - falcoschildrenafrica.org: Incapsula bot-check page on the home and contact pages. Wave 1's contact-page evidence was reused.
  - africastudentfund.net: HTTP 429 on its About page.
- **HTTP 403:**
  - meadowmontessori.org (its Habari Foundation page)
  - liaisongroup.com (its charity and About pages)
- **robots.txt disallows (honoured):**
  - tanzaniamissions.com/asante-sana
  - outpostcenters.org (Falco's ministry profile)
- **TLS and certificate failures (not worked around):**
  - tafcomtz.org: TLS handshake ended early (unexpected EOF).
  - elct.or.tz: expired certificate. elct.org was not re-fetched; it failed TLS for earlier agents.
  - www.cscnacc.org: hostname mismatch. The bare domain cscnacc.org has a valid certificate and was read there.
- **Server errors:** buildingacaringcommunity.org answered HTTP 522 (origin unreachable behind Cloudflare) three times: home, About, and one end-of-run retry of About.
- **Domains that do not exist (DNS):**
  - disabilityreprolight.org (with and without www)
  - acv3.org (with and without www)
  - osiligichildrenfoundation.org (a grantee site checked for funder links)
- **Earlier failures not repeated:**
  - kwieco.org
  - habarifoundation.org (bot check)
  - farajaschool.org (403 to wave 2)
  - utopiafoundation.org
  - peacehouseafrica.org
  - godparentsfortanzania.org
  - hiddenheartsfoundation.org
  - salvayshengreen.org
  - ProPublica XML and PDF filings
- **Caveat on robots.txt.** Where robots.txt itself answered 403 (meadowmontessori.org, liaisongroup.com) or 522 (buildingacaringcommunity.org), the fetcher treated it as absent and requested the page. Every such page also failed, so nothing was read. A 5xx robots.txt should strictly count as "disallow"; next runs should treat it that way.
- **Facebook, Instagram, X and LinkedIn:** recorded only from the organisations' own sites or search results; never read.
- **No hijacked domains** (gambling, parked or for sale) were met.

## Data-protection decisions

- **Residential street addresses left out; city only:**
  - Afrikids (Coral Gables condo unit)
  - Hidden Hearts Foundation (Bluffton, SC)
  - Hope Without Borders-USA (West Bend, WI)
  - Global Development Group USA (Bedford, IN)
  - Sal-vay-shen Green (Fallbrook, CA: a house in real-estate listings)
- **Addresses recorded:** suites, numbered mailboxes and P.O. Boxes.
- **Personal-domain inboxes:**
  - Inboxes named after the organisation are recorded as `personal domain`: Kahe Home (Gmail), Second Chance (Yahoo), Afrikids (Gmail with the president's first name), Scott Willis Legacy Foundation (Gmail), Africa Student Fund (Gmail). Welfare drafts to them stay held.
  - Hidden Hearts' co-founder is published only with a personal iCloud inbox. It stays on her lead, labelled `risky`, and is not an organisation route.
- **Contact details not recorded:**
  - Lift the Lid's personal-domain payment (Zelle) address: not published for contact.
  - A PayPal form inbox (Hidden Hearts).
  - A font-licence address.
  - A UK patron's personal Yahoo inbox (Second Chance): not a leadership route.
- **Grantee contacts on funder pages:**
  - Hidden Hearts' page gives the Osiligi Orphanage director's WhatsApp and personal Gmail. They belong to the grantee, so they were not copied into this funder record; the notes point to the page for the Osiligi care record.
  - Staff of Holley Children Orphanage named on a sponsor's page (Yelloh Foundation) were not recorded.
- **People not recorded:**
  - Plain board members without officer titles, and committee members (counted in notes)
  - Lodge staff, guards, cooks and class teachers
  - Zanzibar-only SOS leaders
  - A travel company's manager
  - Afrikids' seventh officer (the six-lead cap)
  - Officers known only from IRS-derived directories (Yelloh, Scott Willis, TrueToTanzania)
- **Private life not recorded:** biographies, occupations, family relationships, spouses, religion and health stories. This covers the founders' pages of Kahe Home, Songambele, Second Chance, My Daily Armor and Hidden Hearts, and team pages at Utopia, SOS, Friends of Tanzania, TrueToTanzania and Hope Without Borders.
- **Children:**
  - Nothing about children, parents or residents is recorded.
  - Stories naming children and families (Autism Beyond Borders, the Yelloh sponsor page) were ignored.
  - Pupil numbers and conditions in the St Francis results were left out, and a child count was trimmed from Utopia's excerpt.
- **Safeguarding:** the sites of Eripoto's safe house and KWIECO's shelter were not sought.
- **Data brokers and directories** were not used as sources: ZoomInfo, RocketReach, LeadIQ, Datanyze, Cause IQ, GuideStar, Charity Navigator, Instrumentl and similar.

## Identity cautions and warnings

- **Possible closure or change:**
  - **Kilimahewa Children's Education Center:** converted in 2021 into Kilimahewa Modern Secondary School, a private school (registration S.5482). The NGO KIWOCE still runs clubs there. The routes are the successor's, with identity uncertain. It is now a peer school, not a welfare lead: check before outreach.
  - **Choose Love Inc:** revenue $0 in 2024 and no online trace. Possibly dormant.
  - **Orphans International America:** split from its worldwide parent in 2009; Moshi grants date from 2011-2015. Possibly inactive.
  - **Arthur B Schultz Foundation:** spending down all its assets by 2035 (not closed). It needs an introduction from a current partner.
- **Website gone:**
  - Disability Repro-Light (disabilityreprolight.org)
  - Sal-vay-shen Green (acv3.org)
  - BCC's site was down (HTTP 522) all session; check again later.
- **Location to check:**
  - **Angazia:** the register says Kigoma, but its map point is 2.7 km from Kijenge.
  - **St Francis of Assisi school:** about 4.5 km outside Moshi on the Arusha highway, so nearer Boma Ng'ombe than the slice distance suggests.
  - **Kilimahewa:** Sambarai, Kindi Ward, about 6 km west of Moshi.
  - **Global Development Group USA:** the location of its Tanzania project was not read.
- **Out of area or doubtful fit:**
  - Siloam International Africa (26.5 km) and DEHAFO (28.9 km) are outside 25 km.
  - Liaison Group's charity mainly supports Amani's Singida centre.
  - Falco's village is near Karatu; Grand Circle's schools are mostly in Karatu.
  - Al-barro's current projects list no Tanzania work.
  - Vibrant Village's current Tanzania partners are not in Arusha.
  - Coffeyville's only link is a 2011 transfer.
  - Koch funds Catholic evangelisation.
  - Innovo is a corporate donor.
  - TrueToTanzania's grants are tiny.
  - Songambele and YOSIMODO work mainly with women or mothers with disabilities.
- **Duplicates or related records:**
  - Ability in Disability Tanzania, Faraja Forward Tanzania and the Faraja Fund Foundation (as in wave 2).
  - Emayani vulnerable people's center vs Emayani Foundation: unconfirmed.
  - SOS Tanzania (national office, this record) vs SOS Children's Village Arusha (ORG_d015b3a0176fcb44).
  - Care For Children Of The Earth vs Africa Student Fund: probable working name, unconfirmed.
  - Asali's Moshi partner is Simba's Footprints Foundation, probably the welfare run's "Asali partner community centre, Majengo" (ORG_cae06d3f38ed8a69).
- **Strong fits for school places:**
  - Afrikids pays fees at schools around Usa River.
  - Godparents For Tanzania gives secondary and vocational scholarships in the Kilimanjaro and Arusha regions.
  - Utopia's St Mark's page funds English-medium tuition.
  - Grand Circle runs a Tanzania Scholarship Fund.
  - Habari Foundation International pays primary fees in Moshi, but its sources are blocked.

## Possible new leads seen (outside the slice, not recorded)

- **Hearts and Hands for Humanity's own orphanage in Moshi** (the "H3 orphanage"): per the Q34 snippet, it pays the children's school fees.
- **Simba's Footprints Foundation** (community centre, Moshi): Asali's partner.
- **KIWOCE** (Kilimahewa Women's and Orphans' Center for Education, Moshi): a registered NGO still active with the Kilimahewa school.
- **Osiligi Orphanage** (Moivaro, Arusha): Hidden Hearts' site publishes a director contact that the Osiligi care record could use, once checked against its own sources.
- **Jifundishe** (Usa River), **The Girls Foundation of Tanzania** and **Komera**: named as Arthur B Schultz Foundation partners.

## Organisations not reached (5)

No search budget was left, and no URL in hand could give a route.

- **Weily Tribe Foundation.** Wave 2 read its site: contact form only; Tanzania support dated about 2017. A search might find an inbox.
- **Be Part Of Their Story Inc** (Wharton, NJ). Near-dormant: revenue $0 in 2022-2023; one $500 gift to Grace Orphanage, Moshi.
- **Focus On Aids** (Los Angeles). Filings link it to Arnold House, Moshi, only in 2013-2014.
- **New Day Foundation Inc** (Tulsa). Filings link it to Children of Destiny and New Life, Moshi, only in 2011-2012.
- **Peace House Africa.** Tax exemption revoked; its domain does not resolve (wave 1). Treat as inactive.

## Suggested next steps

1. **Open blocked sources manually (user decision):**
   - habarifoundation.org and meadowmontessori.org (Habari: strong school-fee lead)
   - falcoschildrenafrica.org
   - liaisongroup.com
   - tanzaniamissions.com (Asante Sana)
   - elct.or.tz (expired certificate)
   - tafcomtz.org
2. **Recheck buildingacaringcommunity.org later.** It returned HTTP 522, a server fault rather than a block.
3. **Confirm identities before outreach:**
   - Care For Children Of The Earth = Africa Student Fund
   - Emayani's Sombetini map point
   - Angazia's region
   - Habari Foundation's Facebook page
4. **Recompute distances** for St Francis of Assisi school and Kilimahewa, and decide whether Kilimahewa stays in the welfare list now that it is a private school.
