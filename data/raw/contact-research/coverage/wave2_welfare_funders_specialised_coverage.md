# Coverage log: wave 2, welfare funders and specialised centres

Run date: 2026-09-23. Slice: `runtime/contacts/slices/wave2_welfare_funders_specialised.json` (64 organisations, nearest first). Results: `data/raw/contact-research/search_wave2_welfare_funders_specialised_2026-09-23.jsonl`.

Search budget: 15 WebSearch calls. Order: the slice's own order (nearest first). Known sources and websites were fetched first (no search). Earlier welfare-run and wave-1 sources were reused. After that, one search per organisation, in distance order.

## Summary

- **Researched:** 21 of 64 organisations (one JSONL line each).
  - found: 6
  - partial: 3
  - not_found: 12
  - blocked: 0
  - Identity confirmed for 20. Uncertain for 1 (Angazia: the register's region conflicts with its map point).
- **Searches used:** 15 of 15. The stopping rule is **unmet**: 43 organisations were not reached (listed below).
- **Contact leads recorded:** 16 people, all `pdpa_risk: medium`.
  - Two of them, the Foundation for Hope in Africa's president and vice-president, were already captured by the website crawl.
  - Faraja Forward Tanzania's executive director was already on the parent Faraja Fund Foundation record (wave 1). She is now also attached to the organisation she leads.
- **Organisations with a published email or phone for the first time:**
  - The Small Things
  - HACRET
  - Watoto Foundation Tanzania
  - Peacemakers for Albinism and Community
  - Foundation for Hope in Africa (phone only)
  - WATOYO Tanzania e.V.
  - Faraja Forward Tanzania (through its parent's US office)
- **Search yield:** 3 of 15 searches found the organisation's own site (HACRET, Watoto Foundation Tanzania, PAC). A fourth (KCYC) found only snippets of an unreachable site. The other 11 NIS-only centres searched have no web presence under their registered names.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/15 | `"Gloria Foundation" Kilimanjaro Hai stroke` | Gloria foundation (Hai, 0.8 km) | Nothing for the Hai NGO; gloriafoundationroc.org is an unrelated refugee charity |
| Q2/15 | `"Better Life for Deaf Foundation" Tanzania` | Better Life for Deaf Foundation Tanzania | Nothing under this name; results were CHAVITA, EOTAS, DSDO (not used) |
| Q3/15 | `"Better Future for All" Hai Kilimanjaro Tanzania NGO` | Better Future for All (Hai) | Nothing under this name; other Kilimanjaro NGOs only |
| Q4/15 | `"Friends of Kids Speak Out" Arusha` | Friends of Kids Speak Out | Nothing under this name. A Daily News article (fetched) was about a different NGO, Tupendane Africa Foundation |
| Q5/15 | `"Shield of Women and Children Foundation" Arusha` | Shield of Women and Children Foundation | Nothing under this name; other Arusha women-and-children NGOs only |
| Q6/15 | `"Atpeace Foundation" Arusha` | ATPEACE Foundation | Nothing (registered 2026-04-24) |
| Q7/15 | `"Handicapped Children Rehabilitation Tanzania" HACRET Arusha` | HACRET | **hacret.org**: office and postal address, email, two mobiles (one on WhatsApp), Facebook, founder, chair, vice-chair |
| Q8/15 | `"Deaf and Community Progress Organization" Arusha` | Deaf and Community Progress Organization | Nothing under this name |
| Q9/15 | `"Watoto Foundation Tanzania" Arusha` | Watoto Foundation Tanzania | **watotofoundation.nl**: PO Box (Usa River), inbox, +255 mobile, founder-director, board; Facebook and Instagram seen in results |
| Q10/15 | `"Kilimanjaro Children and Youth Centre" Moshi` | KCYC | Only snippets of its own kcyc.or.tz pages; the domain still fails DNS. Two Daily News results were about other centres |
| Q11/15 | `"TAPDISO" Tanzania People with Disability Support Organisation Arusha` | TAPDISO | Nothing; TAPWIDO (Dar es Salaam) is a different body |
| Q12/15 | `"Peacemakers for Albinism and Community" Arusha` | PAC | **albinism-tz.org** and **peacemakersforalbinism-tz.org**: PO Box, inbox, two mobiles, Facebook, founder and executive director. US partner: Lahash Ministries |
| Q13/15 | `"Light of Change Foundation" Arusha Tanzania` | The Light of Change Foundation | Nothing; Give Them Light and Powerlight are different NGOs |
| Q14/15 | `"Africa Action for Fundamental Change and Development" Arusha` | Africa Action for Fundamental Change and Development | Nothing; AFFCAD (Kampala, Uganda) is a different organisation |
| Q15/15 | `"Deafblind Assistance Services" DBAS Tanzania` | DBAS | Nothing under this name |

Search budget reached at Q15/15. After that, only URLs already in hand were fetched: slice `known_sources`, earlier-run and wave-1 URLs, URLs returned by Q1 to Q15, and links on pages already fetched. No domains were guessed and no directory or search-results pages were fetched.

### Reached without a search (searches_used = 0)

- **The Small Things** (known source). Contact page: Tanzania PO Box 594 Usa River, +255 mobile, US mailbox address, US phone, general inbox. Social pages from the home page. Founder and executive director, and managing director, from the history page.
- **Foundation for Hope in Africa** (known source). US office phone on every page, Facebook, YouTube, officers. Two team members listed for Arusha.
- **WATOYO Tanzania e.V.** (known source). Kontakt and Impressum pages: inbox, German mobile, register number, two board chairs.
- **Weily Tribe Foundation** (known source). Contact form only.
- **Faraja Forward Tanzania.** Wave-1 evidence from the parent Faraja Fund Foundation's pages, which name its executive director. The routes are the parent's US office.
- **Angazia.** Register check only; not searched (see identity cautions).

## Blocked or unreadable sources

- **kcyc.or.tz** (with and without www): DNS lookup failed, for the crawl and for this agent. The search index still holds its pages.
- **farajaschool.org**: HTTP 403 to this agent's fetcher (robots.txt and pages). Not retried through another client.
  - Wave-1 agent B fetched the same pages earlier today. Their evidence was reused and labelled as such in the source titles.
- **weilytribe.com**: the crawl got HTTP 429 earlier today. One polite request by this agent, hours later, answered 200. No retries or workarounds.
- **Facebook and Instagram:** pages recorded only from the organisations' own sites or search results; never read.
- **Not blocks, but worth knowing:**
  - thesmallthings.org renders in JavaScript (Raisely). Its facts were read from page data embedded in the fetched HTML.
  - albinism-tz.org hides its email behind standard Cloudflare encoding; it was decoded locally.
- **No hijacked domains** (gambling, parked or for sale) were met.

## Data-protection decisions

- **Postal addresses:**
  - A numbered mailbox address is recorded (The Small Things, US: 1204 Main St #787, Branford), as are PO Boxes.
  - Street addresses that may be residential are not copied: the Foundation for Hope in Africa's US mailing address and WATOYO's Berlin Impressum address. The city is recorded, and the notes point to the source page.
- **Personal-domain inboxes named after the organisation** are recorded with type `personal domain`:
  - watotofoundation@hotmail.com
  - albinopeacemakers@gmail.com (PAC's earlier name)
  - Welfare drafts to such inboxes stay held.
- **Mobiles:** Watoto Foundation's founder-director is recorded with the +255 mobile that the contact page publishes for reaching him. The Hotmail inbox is kept at organisation level only.
- **People not recorded:**
  - a named tours inbox (The Small Things; tours role)
  - four HACRET team entries listed only as "Member"
  - PAC's volunteer liaison and social worker
  - Watoto Foundation's ambassadors, who are former beneficiaries
  - Watoto board members beyond the chair and treasurer (counted in notes)
- **Biographies and private life:** biographical text on The Small Things, HACRET and Watoto pages is not recorded. Neither are the health, family and personal-history details on PAC's about pages. A search summary that repeated them was discarded.
- **News articles:** people named only in Daily News articles are not recorded (not organisation-published).
- **IRS filings:** officer lists were not used, consistent with the earlier run.
- **Children:** nothing about children, parents or residents is recorded. A child count on the Foundation for Hope in Africa's Tanzania page was left out of the excerpt.

## Identity cautions and warnings

- **Out of area:** Angazia.
  - Its NIS profile says Region: Kigoma, with no district, but its map point is 2.7 km from Kijenge.
  - The earlier run parsed its locality as "Level:".
  - Check before outreach.
- **Geocoding error, likely:** KCYC.
  - Its own pages place it in Soweto, **Moshi**, and it is registered 07NGO (Kilimanjaro).
  - The slice's 3.4 km from Kijenge suggests it was geocoded to Soweto, Arusha. Recompute the distance.
- **Related records (not duplicates):** The Small Things (US funder) runs Happy Family Children's Village (ORG_7308c95a88cfe312), and both use thesmallthings.org. People and routes on this slice's record are TST's.
- **Possible duplicate:** Faraja Forward Tanzania (00NGO/R/7846, Moshi) and ABILITY IN DISABILITY TANZANIA (ORG_5f658e3616c1a17b, 00NGO/R/5379, Arumeru). Both are Faraja Fund Foundation partnerships.
- **Dated support:**
  - Weily Tribe Foundation's Tanzania support dates from about 2017.
  - The Foundation for Hope in Africa's last listed Tanzania project is from 2018.
- **Doubtful fit:** Gloria foundation (Hai) works with stroke survivors, caregivers and people with disabilities. It may not be a children's welfare lead.
- **From earlier evidence (not reached):**
  - Global Development Group USA's Tanzania link came from the Sandra Jones Centre, which wave 1 found is in Bulawayo, Zimbabwe.
  - Kilimahewa Children's Education Center has only 2013–2015 filing evidence.

## Possible new leads seen in results (outside the slice, not recorded)

- **Tupendane Africa Foundation** (Arusha; tupendaneafricafoundation.or.tz). Runs a child-protection programme in government schools in Kiranyi Ward, and daycare and early learning. Seen in Q4 and Q5.
- **TAG Kilimanjaro Revival Temple Child and Youth Development Centre** (Moshi). A Compassion International child-development centre running for 20 years. Seen in Q10.

## Organisations not reached (43)

No search budget was left, and no URL in hand could give a route. Their only sources are NIS profiles without contact fields, or ProPublica register and search-result pages.

**Specialised centres (13), nearest first:**

- Huduma ya Fahari Kubwa Foundation, Arumeru (18.0 km)
- YOSIMODO, Arusha (18.5 km)
- Kahe Home for Mental Retarted Children, Moshi (19.0 km). Registered 2012; vocational workshop 2025.
- Disability Repro - Light Organization, Arumeru (21.0 km)
- Jamii Jasiri, Arusha (22.3 km)
- Kilimahewa Children's Education Center, Moshi (22.8 km). Only 2013–2015 evidence; likely closed; deprioritise.
- Second Chance Education Centre, Moshi (22.8 km). Registered 2015.
- TAFCOM, Moshi (22.8 km)
- Songambele Initiative Organization, Moshi (23.4 km). Registered 2018; education and health for disabled women and children.
- TIESO, Arumeru (23.7 km)
- Autism Beyond Borders TZ, Moshi (24.5 km)
- Siloam International Africa, Moshi (26.5 km). International NGO with a 2025 scholarship programme.
- Deaf Hands Foundation (DEHAFO), Arumeru (28.9 km)

**Funders with current (2023–2025) Arusha, Moshi or Usa River school-fee or children's-home grants (13), by likely fit:**

1. Afrikids, Coral Gables, FL. Pays school fees in Arusha and Usa River.
2. Cscna Charity Corps, Cupertino, CA. Emusoi Centre school fees, Arusha.
3. Arthur B Schultz Foundation, Lander, WY. Arusha, Moshi and Usa River grants.
4. Koch Foundation, Gainesville, FL. Moshi and Arusha Catholic programmes, including tuition assistance.
5. Asali, Salem, MA. School fees and scholarships, Majengo, Moshi.
6. Vibrant Village Foundation, Beaverton, OR. HopeCare, Arusha.
7. Grand Circle Foundation, Boston, MA. A children's home in Arusha; Eripoto.
8. Yelloh Foundation, Scottsdale, AZ. Holley Children Orphanage, Arusha.
9. Hidden Hearts Foundation, Houston, TX. Osiligi Orphanage, Arusha.
10. Sal-vay-shen Green, Fallbrook, CA. Treasures of Africa Children's Home, Moshi.
11. Scott Willis Legacy Foundation, Fallston, MD. Arusha orphanage.
12. Friends of Tanzania - Marafiki Wa Tanzania, Washington, DC. HopeCare, Arusha.
13. Hearts and Hands for Humanity, Riverton, UT. Moshi orphanages.

**Other funders (17):**

- Concordia Lutheran Ministries Foundation (VOV centre, Moshi)
- Klehn Family Foundation (Eripoto)
- Care For Children Of The Earth (Passionist Community, Arusha)
- Asante Sana (Light in Africa, Moshi)
- My Daily Armor Ministries (small grant, Arusha)
- Education Equals Power (tiny; individual school-fee grants, Nshupu)
- TrueToTanzania (tiny; Boma Ng'ombe grants in 2020)
- Al-barro Foundation (one-off, 2023)
- Wevol (tiny)
- Coffeyville Area Community Foundation (2011 transfer only)
- Choose Love Inc (revenue $0 in 2024)
- Be Part Of Their Story (near-dormant)
- Focus On Aids, Orphans International America, New Day Foundation, Hope Without Borders-USA (filings older than about 3 years)
- Global Development Group USA (Tanzania link doubtful: Zimbabwe)

**Suggested next-run priorities:**

1. The 13 funders with current grants above. Each is likely to have a website that one search would find.
2. Within 25 km: Kahe Home, Second Chance Education Centre, Songambele, Autism Beyond Borders TZ and Siloam International Africa (older or international registrations, so more likely to be online).
3. Follow up:
   - KCYC: phone, or a later DNS check.
   - Angazia: confirm its location.
   - Faraja Forward Tanzania and Ability in Disability Tanzania: possible duplicate.
