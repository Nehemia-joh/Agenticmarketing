# Coverage log: slice C, master employers (2026-09-23)

Slice: `runtime/contacts/slices/master_employers.json` (78 organisations: hospitals and clinics, colleges, companies, banks). Search budget: 40 WebSearch calls, all used.
Output: `data/raw/contact-research/search_C_master_employers_2026-09-23.jsonl` (67 records).

## Summary

| Measure | Count |
|---|---|
| Organisations in slice | 78 |
| Researched (one JSONL line each) | 67 |
| found | 30 |
| partial | 25 |
| not_found | 10 |
| blocked | 2 |
| Not reached (no line written) | 11 |
| Identity uncertain | 15 |
| WebSearch calls used | 40 / 40 |
| Contact-lead entries | 28 (19 named, all `medium`; 9 role desks, all `low`) |

Status rule used: `found` = identity confirmed and at least one phone or email read from an official or directory page (fetched); `partial` = some profile data but contacts only from snippets, head office only, or location only; `not_found` = no contact route; `blocked` = the organisation's own source refused automated reading.

Duplicate records in the slice, each researched once and cross-referenced in notes: Mount Meru Regional Referral Hospital / Mount Meru Regional Hospital; Leopard Tours Ltd. (two IDs); Exim bank / Exim Bank (T) Ltd; CRDB Bank / CRDB Bank branch; KCB Bank / KCB; Tanzanian Postal Bank / TANZANIA POSTAL BANK / Tanzania Commercial Bank (all now TCB).

## Searches

| # | Query | Organisation(s) | Outcome |
|---|---|---|---|
| Q1/40 | "Mount Meru Regional Referral Hospital" Arusha contact | Mount Meru RRH (+ duplicate record) | Found official site mtmerurrh.go.tz; home page gave phone, emails, P.O. Box, Medical Officer In-charge and Health Secretary |
| Q2/40 | "Arusha Lutheran Medical Centre" contact | Arusha Lutheran Medical Centre | Found almc.or.tz; contact page and Executive Director |
| Q3/40 | "Selian Lutheran Hospital" Ngaramtoni Arusha | Selian Lutheran Hospital Ngaramtoni | Official site found but unreadable (TLS certificate mismatch); Facebook page URL only |
| Q4/40 | "Gemsa" Specialized Polyclinic Arusha | Gemsa Specialized Polyclinic | No website; Instagram handle and snippet phone; conflicting addresses |
| Q5/40 | "St. Elizabeth Hospital" Arusha | St. Elizabeth Hospital | Own site seha.co.tz no longer resolves (DNS); Facebook and Instagram URLs; Archdiocese ownership from snippet |
| Q6/40 | "Ithna-asheri Hospital" Arusha | Ithna-asheri Hospital | Ministry of Health facility register entry (code 120283-7) gave official phone and owner; socials |
| Q7/40 | "Aga Khan" hospital Arusha contact | The Aga Khan University Hospital | Operator page lists Aga Khan Polyclinic Arusha: address, phone, hours |
| Q8/40 | "NSK Hospital" Arusha | NSK Hospital Arusha | Own site: address, P.O. Box, phone, socials; no named leaders |
| (none) | direct fetch of known official site aicc.co.tz | AICC Hospital | AICC corporate contacts and Managing Director |
| (none) | direct fetch of known official site maternityafrica.org | Maternity Africa Arusha | Email, P.O. Box, Country Director |
| Q9/40 | "Usa River" RC health centre Catholic dispensary Arusha | Usa RC Health Centre | Not confirmed: Catholic Directory 2020 PDF (now 404) and a government "USA River Health Centre" listing; neither tied to this facility |
| Q10/40 | "Nkoaranga" Lutheran Hospital Arusha | Nkoaranga Hospital | Own site and register entry (106527-5): phone, location, ownership |
| Q11/40 | "Health 4 All" clinic Arusha Tanzania | Health 4 All | Own site found but no longer resolves; location snippet only |
| Q12/40 | "Oltrument" hospital Arusha | Oltrument Hospital | Public district hospital; Facebook place page; directory contact page refused connection |
| (none) | direct fetch of known official site atc.ac.tz | Arusha Technical College | Rector, HR and Administration director with role emails, P.O. Box, phone |
| (none) | direct fetch of known official site uoa.ac.tz | University of Arusha | Contact page (P.O. Box, three phones, two emails) and Vice Chancellor |
| Q13/40 | "Institute of Accountancy Arusha" contact P.O. Box email rector | Institute of Accountancy Arusha | Own site fails TLS verification; snippet contacts; Rector from CEO Roundtable member directory |
| Q14/40 | "Tengeru Institute of Community Development" contact | Tengeru Institute of Community Development | Own site has a mismatched certificate; admissions PDF on oas.ticd.ac.tz gave Rector's office, P.O. Box, registrar email, phones |
| Q15/40 | "Spiritan Missionary Seminary" Institute of Philosophy Arusha Njiro | Spiritan Missionary Seminary | Own contact page: P.O. Box, phone, mailbox, socials |
| Q16/40 | "CCoHAS" college Arusha | CCoHAS College | Arusha campus site: two phones, two emails, socials |
| Q17/40 | "Methodist Theological College" Arusha Tanzania | Methodist Theological College | Nothing for this name (other seminaries only) |
| Q18/40 | "Mbaaga" Spiritual Formation Centre Arusha | St. Mbaaga Spiritual Formation Centre | Snippet only (Missionaries of Africa); other results were a Uganda seminary |
| Q19/40 | "Mong'are" Teachers College Arusha | Mong'are Teachers' College | Renamed Moshi Teachers College (2015), at Bomang'ombe; no contacts |
| Q20/40 | "St. Joshua College" Arusha | St. Joshua College | Possible match only: Joshua Schools Arusha / Joshua Teachers Training College (Moshono); identity uncertain |
| (none) | direct fetch of veta.go.tz and /veta-zones | VETA Hotel and Tourism Training Institute | Parent-body contacts only; institute not listed |
| Q21/40 | "Superdoll" Arusha branch contact | Superdoll | Company contact page lists the Arusha branch (Clock Tower) and phone; data-broker staff profiles in results not used |
| Q22/40 | "Sunflag" Tanzania Limited Arusha | Sunflag Tanzania Limited | Own site: info@ email and role desk lines (operations, site, finance) |
| Q23/40 | "Tanzania Crop Care" Arusha | Tanzania Crop Care Limited | Own contact page: admin@ email, phone, Themi address |
| Q24/40 | "Sunola" sunflower oil Arusha | SUNOLA refined sunflower oil industry | Retail brand only; producer page domain dead; no contact |
| (none) | direct fetch of known official site leopard-tours.com | Leopard Tours Ltd. (2 records) | Contact page: email, phones, P.O. Box, Kijenge head office, socials |
| (none) | direct fetch of known official site davisandshirtliff.com | Davis & Shirtliff | Tanzania branch page: Arusha branch manager and phones |
| Q25/40 | "Wild Mind Travel" Arusha | Wild Mind Travel Company | Own site: info@ email; HQ at Karibu Home, Sakina |
| Q26/40 | "Esri Eastern Africa" Arusha office | Esri Eastern Africa | Company lists no Arusha office; Dar es Salaam office contacts only; identity uncertain |
| Q27/40 | "SainCraft" Technologies Arusha | SainCraft Technologies | Own site: email, phone, CEO and General Manager (placeholder phone ignored) |
| Q28/40 | "Rijk Zwaan" Arusha Tanzania contact | Rijk Zwaan Q-sem | Snippet contacts only; careers contact page HTTP 403 |
| (none) | direct fetches of bank sites (crdbbank, nmbbank, eximbank, nbc, tcbbank, azaniabank, equitygroupholdings, absa, amanabank, acbbank, ecobank, dtbafrica/diamondtrust, ncbagroup) | Banks | Branch data read for Azania, Amana, NCBA; other locators render in JavaScript; NMB 403; Ecobank redirect loop; DTB locator over 10 MB; Equity page empty |
| (none) | Wikipedia (FBME Bank, Tanzania Commercial Bank, Absa Bank Tanzania, Commercial Bank of Africa (Tanzania), KCB Bank Tanzania Limited) | Banks | Confirmed FBME closure (2017), TPB to TCB and Barclays to Absa renames, KCB Arusha outlets, CBA Arusha branch location |
| Q29/40 | "Exim Bank" "Usa River" branch | Exim bank (+ Exim Bank (T) Ltd) | Branch confirmed by a 2025 job advert; head-office contacts from the bank's help page |
| Q30/40 | CRDB Bank "Boma Ng'ombe" branch | CRDB Bank (+ CRDB Bank branch) | Directory address only (Arusha-Himo Road); CRDB general line |
| Q31/40 | NMB Bank "Arusha Market" branch | NMB Arusha Market | Branch confirmed by snippet; NMB site 403 |
| Q32/40 | "KCB Bank Tanzania" Arusha branch | KCB Bank (+ KCB) | Four Arusha outlets (Wikipedia); official site does not resolve; no contact |
| (none) | direct fetch of rehabilitation-center-tanzania.org (URL from the welfare run) | Usa-River Rehabilitation Centre | Contact page: Head, P.O. Box, phones, email |
| Q33/40 | "Shree Hindu" hospital Arusha | Shree Hindu Hospital | Shree Hindu Union Charitable Hospital: directory phone, P.O. Box and address (snippet), Facebook |
| Q34/40 | "Tanta Dental" Arusha | Tanta Dental Clinic | Matched Tanya Dental Clinic (own site: email, phone, P.O. Box, CEO); identity uncertain (probable OSM misspelling) |
| Q35/40 | "Equity Bank" Arusha branch Tanzania contact | Equity Bank | No branch contact; Equity sites empty or refused connection |
| Q36/40 | "Moshi Teachers College" Bomang'ombe Hai | Mong'are Teachers' College | Snippet phones and P.O. Box from a jobs directory (page 403); record upgraded to partial |
| Q37/40 | "Levolosi Health Centre" Arusha | Levolosi Health Centre | Register entry (103490-9): official phone, public LGA owner |
| Q38/40 | "Kaloleni" health centre OR hospital Arusha Tanzania | Kaloleni Hospital | Register entry (102258-1): official phone, public LGA owner |
| Q39/40 | "Kijenge" RC dispensary Catholic Arusha | Kijenge RC Dispensary | Nothing usable (Catholic Directory PDF 404) |
| Q40/40 | "Arusha Meru International School" | Arusha Meru International School | Own site (www host): email, phone, P.O. Box, section heads, socials |
| (none, after cap) | fetch of tanzania-streets.openalfa.com/arusha_arusha/health (URL from Q9 results) | Old Arusha Health Center, Canossa Dispensary, Oloirien Community Dispensary | Street names only (map-derived); no contact routes |

## Blocked or unreadable sources

Not worked around in any case (no retries in a loop, no sign-in, no browser).

- mtmerurrh.go.tz deep links (/contact, /contact-us, /api/footer): HTTP 404; home page readable
- selianlh.or.tz and www.selianlh.or.tz: TLS certificate mismatch
- eahealth.org directory: HTTP 403
- vymaps.com: HTTP 404
- seha.co.tz (St. Elizabeth Hospital): DNS does not resolve
- ksijhealthcare.or.tz: HTTP 403
- hfrs.moh.go.tz "Data Download": needs a formal request form, an organisation letter and Ministry approval, so it was not used. The user could request the master facility list (with contact info) officially; it would cover the small dispensaries in this slice. Individual facility PDFs by code are readable and were used.
- tec.or.tz Catholic Directory 2020 PDF: HTTP 404
- health4allclinics.co.tz: DNS does not resolve
- africadirectoryservices.com: connection refused
- iaa.ac.tz and www.iaa.ac.tz: TLS chain error ("unable to verify the first certificate")
- ticd.ac.tz and www.ticd.ac.tz: shared government certificate does not cover the host
- nactvet.go.tz institute page: renders in JavaScript, no data
- joshuaschoolarusha.org and joshuaschoolarusha.com: DNS does not resolve
- veta.go.tz/vhtti: HTTP 404
- arkayind.com: DNS does not resolve
- rijkzwaancareers.com: HTTP 403; learning.rijkzwaanafrica.com: content truncated
- nmbbank.co.tz (home and branches page): HTTP 403
- ecobank.com/tz: redirect loop
- diamondtrust.co.tz/locators: page over 10 MB
- equitygroupholdings.com/tz: empty content; equitybank.co.tz: connection refused
- tz.kcbgroup.com: DNS does not resolve
- jobs.mabumbe.com: HTTP 403
- yellpo.com listing: empty
- Branch locators that render in JavaScript (no branch phones readable): CRDB, Exim, NBC, Absa, Akiba; TCB shows ATM entries only
- arushameru.sc.tz bare domain: TLS mismatch (the www host reads fine and was used)
- Facebook and Instagram pages: recorded as URLs from search results or official sites, never read

## Organisations not reached (11)

The search budget ran out before these, and no URL was already in hand for them:

| ID | Name | Segment | Campus | km |
|---|---|---|---|---|
| O615ce17408df | Mazda | office:company | Usa River | 1.6 |
| O93c8c9fb672c | Tigo Store | office:telecommunication | Ilboru | 2.1 |
| O8b531d7b107c | Isamilo Express booking office | office:company | Ilboru | 2.1 |
| O4c8db1a3c7f6 | Henkel | office:company | Kijenge | 2.2 |
| O2d14bb8409eb | VODACOM SERVICE CENTER | office:telecommunication | Kijenge | 2.2 |
| O2310c00d7b59 | Chemical Industry Ltd | office:company | Kijenge | 3.4 |
| O822d982b3f46 | Israel community office | office:company | Kijenge | 3.8 |
| O3674947531d9 | Dhariwal Trading Co | office:company | Kijenge | 4.1 |
| O4c4f1ab9c060 | Economists (T) Investment Group | office:financial | Kijenge | 4.2 |
| O2ff7b069da4d | Meru Hospital | amenity:hospital | Usa River | 7.9 |
| O225198c6cffe | Kkikalora Saccos | bank | (none) | (none) |

## Stopping rule and next-run priorities

The stopping rule (every organisation researched) is unmet: 11 not reached, and most bank branches have head-office routes only.

1. Search budget for the 11 unreached organisations; Meru Hospital first (may be a council district hospital), then the Kijenge companies. For Tigo and Vodacom shops, the operators' corporate sites are the route.
2. Bank branch phones and managers: the locators render in JavaScript. They need a browser session (coordinator only, with the user's go-ahead), a branch visit, or a call to the bank's customer line.
3. Re-try when certificates are fixed: Selian Lutheran Hospital, Institute of Accountancy Arusha, Tengeru Institute of Community Development.
4. Official request for the Ministry of Health master facility list (user's decision). It would give official phones for Kijenge RC, Oloirien, Old Arusha, Canossa and Usa RC facilities.
5. Check identity-uncertain matches before use: St. Joshua College (Joshua Schools Arusha), Tanta Dental (Tanya Dental Clinic), Aga Khan (Polyclinic), Commercial Bank of Africa (NCBA), Esri Eastern Africa (no Arusha office), Gemsa, Usa RC Health Centre.
6. Remove FBME Arusha from the employer list: the bank was closed in 2017.

## Process note

The session scratchpad is shared by all research agents. Another agent (slice A) overwrote this agent's scratch file `batch01.json` after it had been appended. This agent's output was checked and holds only its own 67 records, and no slice C record appears in slice A's output. From then on, this agent's scratch files lived in `scratchpad/sliceC_master_employers/`. Future runs should give each agent its own scratch subfolder.
