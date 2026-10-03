# Wave 11 public sources, agent D (institutions): coverage log, 2 October 2026

Theme: banks, hospitals, colleges, universities, NGOs and public bodies among the 718 targets (111 institution targets of the kinds Corporate, Healthcare, Education, NGO and Public-sector employers).
Output: `data/raw/contact-research/search_wave11_public_d_2026-10-02.jsonl` (40 organisations, 52 named people).

## Searches (8 allowed, 8 used)

| No. | Query | Outcome |
| --- | --- | --- |
| Q1/8 | Tanzania Bankers Association members list banks chief executive officers contacts | Found the TBA Governing Council page (named bank chief executives). Also returned ZoomInfo and Scribd, which were not used. |
| Q2/8 | Tanzania Commission for Universities list of registered universities Vice Chancellor contacts Arusha | Found the TCU registered-universities page and a PDF list. |
| Q3/8 | Private Hospitals Association of Tanzania PHAT members directory Arusha hospitals | No member directory exists online; nothing used. |
| Q4/8 | Bank of Tanzania directory of banks and financial institutions managing director address email telephone | Led to the Bank of Tanzania supervised-institutions page; it carries no contacts for the banks. |
| Q5/8 | NACTVET registered colleges Arusha list principal contacts | Led to the NACTVET registered-institutions page (no contact data in the text). |
| Q6/8 | Tanzania NGO directory Arusha registered NGOs executive director email list TANGO members | No usable official list; ngobase.org and Facebook not used. |
| Q7/8 | Christian Social Services Commission CSSC member hospitals directory Tanzania Arusha hospital administrators contacts | No member list; led to eahealth.org (HTTP 403) and the CSSC site (not read). |
| Q8/8 | Arusha City Council list of health facilities hospitals health centres dispensaries Levolosi Kaloleni Kijenge facility in-charge contacts | The tool ran several follow-up lookups inside this single call (it reported four more result sets). No further search was issued by me after this. Led to the TMDA Northern Zone hospital list and Ministry of Health facility-registry PDFs. |

No search was refused. No search was routed through WebFetch or a browser.

## Directories and lists read

| URL | Entries | Matched to targets |
| --- | --- | --- |
| https://tanzaniabankers.org/tba-governing-council/ | 12 council members (bank chief executives) | 4 (NMB Bank, Absa/Barclays, Exim bank, Equity Bank); no emails |
| https://tcu.go.tz/services/accreditation/universities-registered-tanzania | 2 Arusha entries on page 1 (NM-AIST, Tumaini Makumira) | 2, no contacts on the list; contacts taken from each university's own site |
| https://www.bot.go.tz/BankSupervision/Institutions | Supervised-institution lists (banks, bureaux de change) | 0 usable: no named heads or emails |
| https://www.tmda.go.tz/pages/northern-zone-hospitals | Arusha-region hospital premises (about 15 for Arusha City, Arusha DC, Meru DC) | 0 contacts: premises names and owners only; used only to check identity |
| https://www.nactvet.go.tz/registered-institutions | Registered institutions page | 0: no contact text in the page |
| https://www.atc.ac.tz/management, https://www.tra.go.tz/page/management, https://www.nssf.go.tz/administration/management-team, https://www.taec.go.tz/administrations/management, https://www.temesa.go.tz/pages/management-team, https://www.aicc.co.tz/leadership/management, https://www.tawa.go.tz/management, https://www.tawiri.or.tz/management-and-organization-structure/, https://diamondtrust.co.tz/executive-committee, https://www.tcbbank.co.tz/tcb-team, https://azaniabank.co.tz/management-team/, https://makumira.ac.tz/contact-us/, https://mstcdc.or.tz/about/team, https://www.mtmerurrh.go.tz/staffs, https://seedcogroup.com/about-us/group-executive-committee_/ | Institution management pages (the organisation's own site) | 15 targets matched |

## Records written (40)

Named HR or administration head found for: Arusha Technical College (role email dhrma@), TRA, NSSF, TAEC (Swahili page), TEMESA (Swahili page), AICC, Mount Meru Regional Hospital, TAWIRI (direct work email and phone on the same page), Tanzanian Postal Bank, Diamond Trust Bank, MS-TCDC, Seedco (group level), Tumaini University Makumira (deputy vice chancellor for administration, with role mailbox).
Named chief executive or director with no contact detail: Azania Bank, TAWA (both records), NM-AIST, East African Community, NMB, Exim, Equity, Absa, ALMC, Maternity Africa, SainCraft.
Contact routes only: Tengeru Institute of Community Development, Nkoaranga Hospital, University of Arusha, SAUT Arusha, NIDA, Sunflag, Tanganyika Farmers Association, Oikos East Africa, ADRA, CCoHAS, Spiritan seminary, TANAPA, Maji (ministry, identity uncertain), Isamilo, Mazingira.
Identity flags: AICC Hospital set to uncertain (the pages are for the conference centre); Maji uncertain (the domain is the Ministry of Water).

## Blocks and failures (none worked around)

- Bad certificate, host name mismatch: maji.go.tz, tawa.go.tz, ticd.ac.tz, veta.go.tz, mtmerurrh.go.tz, selianlh.or.tz, snvworld.org, arushameru.sc.tz (the `www.` host of maji, tawa, ticd and mtmerurrh was then read normally; selianlh.or.tz, snvworld.org, arushameru.sc.tz and www.iaa.ac.tz stayed unreadable).
- Certificate chain not trusted: iaa.ac.tz and www.iaa.ac.tz.
- HTTP 403: eahealth.org directory, regionaltanzania.com, rijkzwaan.com, hanspaul.co.tz, tccl.co.tz, mazingira.co.tz/contact.
- Timeouts or no DNS answer: acbbank.co.tz, nmbbank.co.tz, tz.kcbgroup.com, health4allclinics.co.tz, aicc.go.tz, tanapa.go.tz, ngorongorocrater.go.tz, emeru.go.tz, auwasa.or.tz.
- ncaa.go.tz answers with an unrelated company site (CFL Inc.): not used.
- Ministry of Health facility-registry pages (hfrs.moh.go.tz) and the TCU PDF are returned as binary PDFs that the page reader cannot extract: not read.
- SAUT Arusha site carries injected gambling spam text and a foreign phone number: only the plausible admission contacts were kept and flagged.
- Social profiles, ZoomInfo, Scribd, ngobase.org, Wikipedia and snippet-only search facts were not used as sources.

## Not reached

Targets with no record: AAR Clinic, AUWASA, Akiba Commercial Bank, Amana Bank (own site read, no new contact), Aga Khan Health Services and Aga Khan University Hospital (leadership is on the home page, not read), Arusha Meru International School, Avinta, Canossa Dispensary and Spirituality Centre, Chemical Industry, Commercial Bank of Africa, Davis and Shirtliff (executive page not read), Dhariwal, East Africa Travel Company, Ecobank, Economists (T), Esri Eastern Africa, FBME, Gemsa, Hanspaul (403), Health 4 All, Henkel, Immigration office, IAA (certificate), Israel community office, Ithna-asheri, KCB, Kaloleni, Kijenge RC, Kkikalora Saccos, Leopard Tours, Levolosi, Mazda, Meru Hospital, Methodist Theological College, Mong'are Teachers' College, NCAA, Ngorongoro Information Center, National Housing, Njake Oil, Old Arusha Health Center, Oloirien, Oltrument, PAG Church Njiro, R&D Polyclinic, Regional Air (403), Rijk Zwaan (403), SNV (certificate), Sunola, Samaki Feeds, Selian Lutheran Hospital and Ngaramtoni (certificate), Shree Hindu, St. Elizabeth, St. Joshua, St. Mbaaga, Tanesco, Tanta Dental, TCCL (403), Tanzania Conservation Resource Centre (home page showed no contact text), VETA Hotel and Tourism Training Institute, Vodacom, VisionFund, Wild Mind, Woodtech, UAACC, Usa RC Health Centre, Tcp Saccos, Top of Africa Treks, Tropical Trails. Most small clinics, dispensaries and church bodies have no site of their own.
