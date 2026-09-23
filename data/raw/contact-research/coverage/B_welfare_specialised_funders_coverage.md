# Coverage log: slice B (welfare specialised centres and funders)

Run date: 2026-09-23. Slice: `runtime/contacts/slices/welfare_specialised_funders.json` (85 organisations). Results: `data/raw/contact-research/search_B_welfare_specialised_funders_2026-09-23.jsonl`.

Search budget: 20 WebSearch calls. Order: organisations within 25 km first, nearest first; then funders most likely to pay for schooling near Arusha or Moshi.

## Summary

- **Researched:** 52 of 85 organisations (one JSONL line each).
  - found: 21
  - partial: 16
  - not_found: 10
  - blocked: 5
  - Identity confirmed for 41; uncertain for 11.
- **Searches used:** 20 of 20. The stopping rule is **unmet**: 33 organisations were not reached (listed below).
- **Contact leads recorded:** 44 people.
  - medium: 43
  - risky: 1 (a diocesan education director whose published email is on yahoo.com)
- **Coverage by distance:**
  - Within 25 km (30 organisations): 27 researched, 3 not reached.
  - Beyond 25 km: 1 organisation (the Karatu centre, 110 km), researched.
  - No distance (54, mostly US and foreign funders): 24 researched, 30 not reached. These were reached through their own sites already on file, pages linked from fetched pages, or domains that search results returned for other queries.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/20 | `"Ilboru Special Needs School" Arusha` | Ilboru Special Needs School | Facebook page (not read); funder pages only; no school phone or email |
| Q2/20 | `"Tanzania Child Care and Technical Support" Arusha` | Tanzania Child Care and Technical Support | Facebook page under a shorter name (identity uncertain) |
| Q3/20 | `Passionist community Arusha Tanzania Passionists contact` | Passionist Community Arusha | Official site found but it does not resolve (DNS); location from snippet only |
| Q4/20 | `"Arusha Lutheran Medical Centre" contact email phone` | Arusha Lutheran Medical Center | almc.or.tz: address, email, phones and Executive Director confirmed |
| Q5/20 | `"CHISWEA" Arusha street children` | CHISWEA | Facebook page; Sokoni One location and centre coordinator on Heart for Africa's team page |
| Q6/20 | `"Kidcare International" Arusha Tanzania` | Kidcare centre (Arusha) and Kidcare International (funder) | kidcare.org contact page (US office, email, phone); KidCare supports the Shalom Centre and, per a snippet, CHISWEA |
| Q7/20 | `"Sandra Jones Centre" Tanzania` | Sandra Jones Centre | Not in Tanzania: the centre is in Bulawayo, Zimbabwe. False lead |
| Q8/20 | `"Nashumu" vulnerable girls rescue initiatives NAVUGIREI` | NAVUGIREI | Nothing found |
| Q9/20 | `"Fortune Kids and Education Foundation" Tanzania` | FKEF | fortunekids.org: address, email, WhatsApp, founder and managers. Results also gave the Educating Tanzania Foundation site |
| Q10/20 | `"Best Centre for the Blind" Ngaramtoni OR Arusha` | Best Centre for the Blind | Nothing found; original source domain hijacked |
| Q11/20 | `"Rescue Children Charity Organization" Arusha Tanzania` | Rescue Children Charity Organization | rescuechildrentz.org: address, P.O. Box, email, phone, founder/CEO |
| Q12/20 | `"Salama Home" "Joyful Children" Tanzania` | Salama Home and Joyful Children | Only a private individual's GoFundMe (not recorded). Results gave the Falco's Children Africa site |
| Q13/20 | `"Kingdom Matters" Tanzania Arusha widows children organisation` | Kingdom Matters Organisation | Nothing found |
| Q14/20 | `"Shalom Centre" street children Arusha Tanzania` | Shalom Centre for Street Children | Facebook and Instagram; own domains do not resolve; one result was a different Shalom centre in Karatu |
| Q15/20 | `"Faraja Fund" Tanzania disabilities Sanya Juu` | Faraja Diaconic Centre, Ability in Disability Tanzania, Faraja Fund Foundation | farajaschool.org: US office, email, phone, Executive Director and Tanzania programme director |
| Q16/20 | `"Rise Up and Go" children with disabilities Tanzania Arumeru` | RU&GO | Nothing found |
| Q17/20 | `"Health Integrated Multisectoral Development" HIMD Tanzania` | HIMD | himd.or.tz: P.O. Box, email, three phones, board and team |
| Q18/20 | `"New Hope Initiative" Arusha Tanzania` | New Hope Initiative, Inc | newhopeinitiative.org: US P.O. Box, email, two named Arusha project leads |
| Q19/20 | `"Gabriella Children's Rehabilitation Centre" Moshi contact` | Gabriella Children's Rehabilitation Centre | gabriellacentre.or.tz: email, phone, Hai District; no named leaders |
| Q20/20 | `"Sisters of Our Lady of Kilimanjaro" Moshi` | Sisters of Our Lady of Kilimanjaro (also gave the Catholic Diocese of Moshi site) | Congregation domain hijacked (gambling); diocese site: chancery phone, P.O. Box, bishop, education director |

Search budget reached at Q20/20. After that, only URLs already in hand were fetched: slice `known_sources`, earlier welfare-run records, URLs returned by Q1 to Q20, and links on pages already fetched. No domains were guessed after the cap.

### Reached without a search

Found through known URLs, earlier-run URLs, or other queries' results (searches_used = 0):

- Maasai Girls Rescue Center (US Inc and Karatu centre)
- Friends of Amani US, Friends of Amani UK, Vrienden van Amani
- The Faraji Foundation
- Children of Kilimanjaro Orphanage (COKO)
- Kilimanjaro Children's Fund
- Neema Village
- Eripoto
- Emayani
- Educating Tanzania Foundation
- Falco's Children Africa
- One Heart Source
- Hidden With Christ Ministries
- KidCare International
- Faraja Fund Foundation, Ability in Disability Tanzania
- Catholic Diocese of Moshi
- St Francis of Assisi school
- BCC
- KWIECO
- ELCT
- Habari Foundation
- Utopia Foundation
- Lift-the-lid
- GO Campaign
- Peace House Africa
- SOS Children's Villages
- Innovo Benefits Group, Liaison Group
- Godparents For Tanzania

## Blocked or unreadable sources

- **ProPublica filings:**
  - The XML download (`/nonprofits/download-xml`) and the 990 PDF (`/nonprofits/display_990/...`) both answered HTTP 403.
  - The "full filing" view returned only the page shell.
  - The organisation pages show only name, EIN and city.
  - Result: US funders known only from ProPublica could not be given a website or phone without a search.
- **habarifoundation.org:** bot-verification screen, the same as on 2026-09-22. Not bypassed.
- **Failed connections or certificates:**
  - elct.org: TLS handshake failure, the same as on 2026-09-22.
  - kwieco.org: connection reset, with and without www.
  - utopiafoundation.org: connection refused.
  - almc.habari.co.tz (old ALMC site): TLS certificate failure. The current site is almc.or.tz.
- **Pages that answered 403:** archello.com (KWIECO shelter project page).
- **Domains that do not resolve:**
  - passioniststanzania.or.tz (with and without www)
  - shalomcentretz.or.tz and shalomcentretz.org
  - peacehouseafrica.org
  - farajafund.org
  - kwieco.or.tz
  - gabriellacentre.org (the real domain is gabriellacentre.or.tz)
  - kingdommatters.org
  - ourladyofkilimanjaro.org
- **Hijacked domains (now serving gambling content), not followed or used:**
  - volunteerbasecamp.com (the source for Best Centre for the Blind)
  - sistersofkilimanjaro.org (the congregation's former site)
- **Other unreadable pages:**
  - The Segal Family Foundation portfolio page returned an image only.
  - Dead pages (404):
    - GO Campaign's Gabriella article
    - KidCare's Hope for Hunger page
    - autismconnect.com Ilboru entry
    - best-farm.squarespace.com
    - eripoto.org/about (the real page is /abouteripoto)
  - The falcoschildrenafrica.org home page rendered empty; its contact page worked.
- **Facebook and Instagram pages:** recorded from search results or the organisations' own sites only; never read.

## Data-protection decisions

- **Postal addresses:**
  - P.O. Boxes and commercial or mailbox addresses (suite or # numbers) are recorded.
  - Street addresses of small volunteer charities that look residential are not recorded; the notes point to the source page. This covers Friends of Amani UK, Vrienden van Amani (two different addresses published), and the Maasai Girls Rescue Center US mailing address.
- **People:**
  - Recorded only when the organisation itself, or its parent body, publishes them. One exception: CHISWEA's coordinator appears on the UK funder's own team page, and this is flagged in his record.
  - Founders named only on partner pages are left out: Shalom Centre (African Moons), the Sisters of Our Lady of Kilimanjaro's Mother General (St. Joseph's Wells), and Ilboru's founding teacher (A&K Philanthropy). The same applies to corporate executives named on Amani's partner page.
  - Ages, birth years and personal histories on board pages are not recorded (Vrienden van Amani, Eripoto).
  - Safe-house locations and staff (Eripoto, HIMD) are not recorded.
- **Data brokers:** ZoomInfo results (HIMD, ALMC) were ignored.
- **Obfuscated emails:** The Maasai Girls Rescue Center hid its email behind standard Cloudflare anti-spam encoding. It was decoded locally to info@maasairescue.org.
- **Children:** Nothing about children, parents or relatives was recorded. Two search snippets named a child and gave personal circumstances (FKEF, Salama); they were discarded.

## Identity cautions

- **Emayani vulnerable people's center (Sombetini, OSM):** linked to Emayani Foundation's town-centre office by name only. Uncertain.
- **Tanzania Child Care and Technical Support:** only a Facebook page named "Tanzania Child Care And Support - TCCS". Uncertain.
- **Kidcare International centre for street children:** probably the Shalom Centre or CHISWEA, both of which KidCare supports. Check for a duplicate before outreach.
- **Sandra Jones Centre:** in Bulawayo, Zimbabwe. Suggest removing it from the Arusha list.
- **Ability in Disability Tanzania:** the NIS register calls it a Faraja Fund Foundation partnership, but the Faraja pages do not name it.
- **Shalom Centre:** a search snippet places it in Lesiraa village (Arumeru), while the NIS district is Arusha. shalomcenter.or.tz is a different orphanage in Karatu.
- **One Heart Source:** the current site describes only South African programmes, so the Tanzania link may be historical.

## Organisations not reached (33)

No search budget was left. The only URLs in hand were NIS profiles without contact fields, or ProPublica register pages and search-result pages. The 30 funders below are ordered by likely fit for school fees near Arusha, Moshi, Usa River or Boma Ng'ombe; carry them into the next run's priorities.

**Within 25 km (3):**

- Kilimahewa Children's Education Center, Moshi (22.8 km). The only source is a ProPublica full-text search page. The earlier run doubted it is still operating.
- TAFCOM, Moshi (22.8 km). NIS 00NGO/R/5055; no contact fields.
- Autism Beyond Borders TZ, Moshi (24.5 km). NIS 07NGO/R/1980; its projects include vocational-training fees.

**Funders: school-fee or catchment signals first (8):**

1. TrueToTanzania (Winston-Salem, NC). Linked to Boma Ng'ombe.
2. Afrikids (Coral Gables, FL). Pays school fees in Arusha and Usa River.
3. Arthur B Schultz Foundation (Lander, WY). Arusha, Moshi and Usa River links.
4. Asali (Salem, MA). School fees, Moshi.
5. Cscna Charity Corps (Cupertino, CA). School fees, Arusha.
6. Education Equals Power (Atlanta, GA). School fees, Arusha.
7. Grand Circle Foundation (Boston, MA). Eripoto and a children's home in Arusha.
8. Global Development Group USA (Bedford, IN).

**Other funders (22):**

- Koch Foundation (Gainesville, FL)
- Friends of Tanzania - Marafiki Wa Tanzania (Washington, DC)
- Vibrant Village Foundation (Beaverton, OR)
- Hidden Hearts Foundation (Houston, TX)
- Hearts And Hands For Humanity (Riverton, UT)
- Klehn Family Foundation (Newhall, CA)
- My Daily Armor Ministries (Louisville, KY)
- Care For Children Of The Earth (Louisville, KY)
- Asante Sana (Newport Beach, CA)
- Scott Willis Legacy Foundation (Fallston, MD)
- Al-barro Foundation (Glendale, CA)
- Orphans International America (New York, NY)
- Coffeyville Area Community Foundation (Coffeyville, KS)
- Hope Without Borders-USA (West Bend, WI)
- Choose Love Inc (Charleston, SC)
- Wevol Inc (Boulder, CO)
- Focus On Aids (Los Angeles, CA)
- New Day Foundation (Tulsa, OK)
- Be Part Of Their Story (Wharton, NJ)
- Yelloh Foundation (Scottsdale, AZ)
- Concordia Lutheran Ministries Foundation (Cabot, PA)
- Sal-vay-shen Green (Fallbrook, CA)

**Also needing a follow-up:**

- Blocked: Godparents For Tanzania (school fees, Moshi and Arusha) and Habari Foundation International (school fees, Moshi). Their filings or sites were blocked; open them manually or search in the next run.
- Partial: the Passionist Community, SOS Children's Villages Tanzania (national office), Shalom Centre, CHISWEA and Ilboru Special Needs School have no direct email or phone yet.
