# Coverage log: hd1_companies_p12_named (high-direct wave, 11 October 2026)

Slice: `runtime/contacts/slices/hd1_companies_p12_named.json` (67 organisations, P1 and P2, nearest first). Output: `data/raw/contact-research/search_hd1_companies_p12_named_2026-10-11.jsonl` (67 lines).

**Searches used: 37 of 49.** The search cap was never refused. The remaining 12 were left unused: `"<org>" "@<domain>"`, `site:<domain> "<surname>"` and vacancy queries for small safari operators returned only SafariBookings and other booking listings (the engine largely ignores `site:`), so further operator queries were judged not worth spending.

**Method.** Every organisation's cached own pages (`runtime/contacts/http-cache/`, 22,593 files) were re-read offline first: all addresses, Cloudflare-protected addresses (decoded) and anti-spam scripts were checked against the people on file. Previous coverage logs were read so no query was repeated. Then own pages not yet read, directory and vacancy pages were fetched, and searches were used where that gave nothing. No address was constructed from a pattern.

**Results by status:** found 9, partial 7, not_found 49, blocked 2.

Found (a published work address for a named decision-maker):
- Matembezi Company: Stephanie Kuerzinger (partner, management) stephanie@ and Hagai Zvulun (founder) hagai@, both name-matched on the own site (the recipient Ilan Kessel has none).
- Davis & Shirtliff: Maimuna Kirumbi, Branch Manager Arusha: arusha@dayliff.com and +255 753 208 259 in her own branch block (branch inbox).
- Role inboxes for the recipient's own role, from the employer's own vacancy notices: VisionFund (vftHRstaff@, HR head, 2024), MS TCDC (jobs@, notice addressed to the Head of Human Resources, 2025), Aga Khan Health Services (hr@akhst.org, 2022), Equity Bank (TZRecruitment@, 2026), Exim Bank (hrrecruit@, 2023; now portal), Akiba Commercial Bank (recruitment@, 2025), Elewana Arusha Coffee Lodge (gm.coffeelodge@, GM office, Feb 2026; GM name from 2020).

Partial: Bushbuck (WhatsApp number), Tanmanagement (management page on tm.co.tz; Jacob Kisuda, Arusha branch), Claritas (leadership confirmed; segment check), TCB (ATE directory mailbox, no role), King Mart (md@ role inbox, holder not named; full phone), Hoopoe (director named in ATTA news 2022), Lemala/Grumeti (sales head in ATTA exhibitor list, parent-group domain).

## Numbered query log

| Q | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/49 | site:safari.africa "Elkummay" | Safari.Africa | No result from the own domain. Nothing. |
| Q2/49 | site:earthlifeexpeditions.com "Losika" | Earthlife Expeditions | No result from the own domain. Nothing. |
| Q3/49 | "Kiliclimb Africa Safaris" "@kiliclimbafricasafaris.com" | Kiliclimb Africa Safaris | Only SafariBookings listings (no address). Nothing. |
| Q4/49 | site:pwc.com "Msimbe" | PwC Tanzania | No pwc.com page; CEO Roundtable pages (404, and ?p=434 gives only the secretariat). Nothing. |
| Q5/49 | "Active Tanzania" "@activetanzania.com" | Active Tanzania Adventures | Only footslopestours.com and a G Adventures trip page; no address at the domain. Nothing. |
| Q6/49 | "Snow Africa Adventures" "@snowafricaadventure.com" | Snow Africa Adventures | SafariBookings and TravelStride listings, no address. Nothing. |
| Q7/49 | "Bushbuck Safaris" "@bushbucksafaris.co.tz" | Bushbuck Safaris | SafariBookings, data-broker sites (not used); no address. Nothing. |
| Q8/49 | "Tanzania Commercial Bank" vacancy "send your application" email | Tanzanian Postal Bank (TCB) | Only other banks' notices (DCB, ICB, Mkombozi, CBA). Nothing for TCB. |
| Q9/49 | "Arusha Lutheran Medical Centre" "@almc.or.tz" | Arusha Lutheran Medical Centre | No address at almc.or.tz; German Embassy doctors' list gives only the hospital inbox at another domain (almc@almc.co.tz / habari). Nothing for the director. |
| Q10/49 | site:ticd.ac.tz rector email | Tengeru Institute of Community Development | Only the OAS login pages and third-party listings. Nothing. |
| Q11/49 | "VisionFund Tanzania" "@vftz.co.tz" | VisionFund Tz MF Bank | VisionFund's own vacancy notices (via ajiriwa, fetched; deadline 7 June 2024) give the HR inbox vftHRstaff@vftz.co.tz. Recorded as the HR role inbox for the Head of People & Culture. |
| Q12/49 | "KCB Bank Tanzania" "@kcbbank.co.tz" | KCB | Wikipedia, news, CEO Roundtable; no address at the domain. Nothing. |
| Q13/49 | "TCB Bank" "@tcbbank.co.tz" | Tanzanian Postal Bank (TCB) | ATE HR member directory (fetched) gives diana.myonga@tcbbank.co.tz with no role; TCB's own COO vacancy page found. No address for the HR director. |
| Q14/49 | "Equity Bank Tanzania" "@equitybank.co.tz" | Equity Bank | Equity's own vacancy notices on ajiriwa (latest fetched: deadline 21 August 2026) give TZRecruitment@equitybank.co.tz. Recorded as the HR recruitment role inbox for the Head of Human Resources. |
| Q15/49 | "Akiba Commercial Bank" vacancy "send your application" | Akiba Commercial Bank | ACB's own notice on ajiriwa (fetched; deadline 28 July 2025) gives recruitment@acbbank.co.tz. Recorded as the HR recruitment role inbox for the Head of HR. mabumbe.com returned 403 (block). |
| Q16/49 | "Mount Meru Regional Referral Hospital" "@mtmerurrh.go.tz" | Mount Meru Regional Hospital | News and directory pages only; no address at the domain. Nothing. |
| Q17/49 | "Aga Khan Health Services" Tanzania vacancy "@akhst.org" | Aga Khan Health Services - Arusha | AKHS Tanzania notices on ajiriwa (fetched one; closing 18 September 2022) give hr@akhst.org. Recorded as the HR role inbox for the Head of Human Resource (stale-date caveat). |
| Q18/49 | "Exim Bank" Tanzania vacancy "send your application" "@eximbank.co.tz" | Exim bank | Exim's own notice on ajiriwa (fetched; deadline 13 December 2023) gives hrrecruit@eximbank.co.tz; a 2025 roundup says applications now go through the careers portal. Recorded as the HR role inbox for the Head of HR with that caveat. |
| Q19/49 | "MS TCDC" vacancy "@mstcdc.or.tz" | MS Training Centre for Development Cooperation | MS TCDC notice on ajiriwa (fetched; deadline 12 October 2025): applications "addressed to the Head of Human Resources, MS TCDC via email to: jobs@mstcdc.or.tz". Recorded as the role inbox for the HR head. |
| Q20/49 | site:balloonsafaris.com "MacKinnon" | Serengeti Balloon Safaris | Own "our story" and "our balloons" pages (already held): founder history only, no address. Nothing. |
| Q21/49 | site:matembezi.co.tz "Kessel" | Matembezi Company | No result from the own domain. Nothing. |
| Q22/49 | "Gran Melia Arusha" "@melia.com" | Gran Melia Arusha | Meeting-venue directories (email masked), Business Traveller, monkey.travel; no address. Nothing. |
| Q23/49 | "Strategis Insurance" "@strategis.co.tz" | Strategis Insurance | Own site only gives insurance@; the own /team/ page (fetched) names six leaders with no email or phone. Nothing new for the GCEO's address. |
| Q24/49 | "St. Augustine University of Tanzania" Arusha Centre "@saut.ac.tz" | SAUT Arusha Campus | Own application form (admission@sautarusha.ac.tz, already held), selection PDFs; nothing for the Director. |
| Q25/49 | "Tengeru Institute of Community Development" "@ticd.ac.tz" | TICD | NACTVET register and own letterhead give only info@ticd.ac.tz. Nothing for the Rector. |
| Q26/49 | "Selian Lutheran Hospital" "@selianlh.or.tz" | Selian Lutheran Hospital Ngaramtoni | Partner and mission pages; the hospital's older web address is selianlh.habari.co.tz. No address at the domain. Nothing. |
| Q27/49 | "Lemala Camps" "@lemalacamps.com" | Grumeti Expeditions (Lemala) | Own contact page (res@ only); ATTA Indaba 2026 exhibitor listing (fetched) names the Head of Sales and Marketing with an address at the parent group's domain. Nothing for the CEO. |
| Q28/49 | "East African Court of Justice" Registrar "@eachq.org" | East African Court of Justice | Own court pages give eacj@eachq.org; a 2013 notice names a former Registrar (not current, not used). Nothing for the Principal Judge. |
| Q29/49 | "Wild Pride Safaris" vacancy OR "send your application" | Wild Pride Safaris | Only SafariBookings listings. Nothing. |
| Q30/49 | "African Environments" Arusha vacancy OR "send your application" | African Environments | Other employers' notices only. Nothing. |
| Q31/49 | "Safari.Africa" Arusha vacancy OR "send your application" | Safari.Africa | Other operators' notices only. Nothing. |
| Q32/49 | "Earthlife Expeditions" vacancy OR "send your application" | Earthlife Expeditions | Unrelated expedition organisations only. Nothing. |
| Q33/49 | "Dream Peak Safaris" vacancy OR "send your application" | Dream Peak Safaris | Only SafariBookings listings. Nothing. |
| Q34/49 | "Lion King Adventures" Arusha vacancy OR "send your application" | Lion King Adventures | Only SafariBookings listings. Nothing. |
| Q35/49 | "Earthlungs" Tanzania "@earthlungs.org" | Earthlungs Reforestation Foundation | Substack interviews, LinkedIn (not used), Fuzu; no address at the domain. Nothing. |
| Q36/49 | "SainCraft Technologies" "@saincraft.co.tz" | SainCraft Technologies | Unrelated companies and data brokers only. Nothing. |
| Q37/49 | "Hoopoe Safaris" Tanzania "@hoopoe.com" | Hoopoe Safaris | No address; ATTA member news item (fetched, 13 Oct 2022) names Peter Lindstrom as a company director. |

## Pages fetched without a search (selection)

- safari.africa/contact (404); earthlifeexpeditions.com/about-us/our-team/; bushbuckltd.com/managing-director
- ceo-roundtable.co.tz/member/pwc-tanzania/ (404) and ?p=434
- hrms.ate.or.tz TCB profile; tcbbank.co.tz/opportunities/36/61 (404)
- ajiriwa notices: VisionFund, Equity, Akiba, AKHS, Exim, MS TCDC; fursa.co.tz Elewana notice
- strategis.co.tz/team/; claritas.co.tz/leadership; tm.co.tz/management/; tatotz.org/portfolio/king-mart/
- atta.travel Lemala exhibitor listing and Hoopoe news; kcbbank.co.tz/executive-management; eacj.org/?page_id=3827
- davisandshirtliff.com/tanzania-branches and matembezi.co.tz/contact-us/ (re-fetched live to confirm cached content)
- sautarusha.ac.tz application form PDF (binary; not readable as text)

## Blocked sites

- pwc.co.tz (403, earlier waves; not retried), paradise-wilderness.com (403 on every page), jwseagon.com (403), melia.com (403), nmbbank.co.tz (403 on most pages), hoopoe.com (429 to the crawler, earlier wave).
- mabumbe.com answered 403 to a fetch (Akiba notice); not worked around.
- selianlh.or.tz: TLS certificate mismatch and robots.txt 502 (earlier waves); not read.
- No robots.txt Disallow rule applied to any page fetched.

## Data-quality notes for review

- Tanmanagement: the master's website is jwseagon.com (403); the company's own site is tm.co.tz.
- KCB: the master's website tz.kcbgroup.com does not resolve; the bank's site is kcbbank.co.tz.
- King Mart: phone in the master is truncated (+255 694 774); TATO gives +255 694 774 477.
- Claritas International is an audit and tax firm filed as a safari operator.
- Earthlungs Reforestation Foundation lists no Arusha office (Tanzania offices in Tanga and Dar es Salaam); location to check.
- Kilimanjaro Heroes Adventures is in Moshi per TATO, not 1.0 km from an Arusha campus; location to check.
- Gran Melia Arusha: the GM on file rests on a 2022 article. Elewana: the GM on file rests on 2020 newsletters.
- EACJ: the Registrar post is "currently not filled" (own page).
- Lion King Adventures: safari1@ is a Maasai-mat ordering contact, not a route for the founder.

## Organisations not reached

None. All 67 were worked: cached own pages reviewed for every one, and 33 received at least one search. The 34 with no search are listed in the output with "No search spent" in notes.
