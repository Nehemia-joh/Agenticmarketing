# Companies medium-to-high coverage, 10 October 2026

Goal: promote the company master's medium-confidence first messages (`scripts/messaging/export_resend_contacts.py`: 338 companies and 4 introducers on 10 October 2026) to high by finding the named decision-maker each company publishes and their direct route. Worked by reach tier: P1, then P2, then the introducers; P3 by deterministic checks only (no searches).

Output: `data/raw/contact-research/search_companies_2026-10-10.jsonl` (13 organisations). Search allowance 80 (shared session cap); used 19, then stopped because searches for these organisations returned almost nothing new (most had been searched in waves 2 to 12).

## Deterministic work (no search)

- Own-site re-read of all 98 P1, P2 and introducer organisations still medium: home page, team, about, leadership, management, careers and contact links, plus common paths, through `contact_lib.fetch` (cached, 1.5 s per site, robots.txt honoured). New people found: none beyond those already held. It confirmed the TICD Rector (ticd.ac.tz home page) and the HAT Executive Secretary (hat-tz.org/about-hat/).
- Re-read of the source page of every senior contact held as unverified at a medium company: confirmed Joseph Aweth (Faune & Flore, co-founder) and Richard Sisia (Safaris-R-Us, director). Not confirmed, because the page no longer names them: Pamela Stephen Lyamuya (Everyday Safaris about page), Donna Duggan (Maasai Wanderings team page). Unreadable: brightafricansafaris.com (403), paradise-wilderness.com (403), wildwaystanzania.com (403), tangersafaris.com/our-story (404).
- Own websites confirmed by reading their home pages, for records whose website field was empty or held a phone number or a directory code: summits-africa.com, roadsidetanzania.com, safariavventura.com, dumaexplorer.com, yas.co.tz, access2tanzania.com (and crdbbank.co.tz, nbc.co.tz, riobasafaris.com, stillwaterssafaris.co.tz, laitolya.com, tgn.co.tz, whose website the record already held in its email field). kingmart.co.tz is a parked hosting page; sabrahm-safaris.com disallows crawling.

## Searches

| # | Query | Outcome |
|---|---|---|
| Q1/80 | Institute of Accountancy Arusha Rector 2026 | The Citizen, 14 Jan 2024 (fetched): Rector Prof Eliamani Sedoyeka. iaa.ac.tz fails TLS. CEO Roundtable member page 404. Recorded (dated). |
| Q2/80 | "Citylink Hotel" Arusha general manager | No manager named; ACHPR 2023 list has a reservations contact only. |
| Q3/80 | PwC Tanzania Country Senior Partner Arusha office partner | Snippets name Zainab Salome Msimbe as Country Senior Partner (thebusinessyear.com 403; CEO Roundtable pages 404 or silent). ATE directory (fetched) lists joan.mabeyo@pwc.com without a role. Not recorded as a contact (snippet only). |
| Q4/80 | "United Aviation Services" Tanzania managing director | Nothing. |
| Q5/80 | "Karibu Camps" managing director OR general manager OR founder | ATTA trade-show exhibitor page (fetched): Misha Pattni, Marketing Executive, safari@karibucamps.com. Recorded. |
| Q6/80 | site:atta.travel ... Arusha safaris "Contact Information" | No ATTA results; a data-broker page was not used. ATTA directory pages hide contacts behind a member login. |
| Q7/80 | "Ijaz Lalji" NSK Hospitals Arusha | Nothing. |
| Q8/80 | Al-Anver tents Arusha Murtaza director | Nothing. |
| Q9/80 | "Elirehema Mshana" Intrepid Tanzania | Nothing. |
| Q10/80 | Ecobank Tanzania Managing Director appointed 2025 | weps.org (fetched): "Charles Asiedu (M) Managing Director", signatory since 11 Nov 2025. Recorded. |
| Q11/80 | "Everyday Safaris" Arusha Pamela Lyamuya director | Nothing. |
| Q12/80 | "Kibo Palace Hotel" Arusha "General Manager" | No manager named. |
| Q13/80 | APHFTA Executive Director 2026 | Job notices address the "Chief Executive Officer" without a name; aphfta.org does not resolve. |
| Q14/80 | "Claudia Stuart" Bushtops | Nothing. |
| Q15/80 | "Leopard Tours" Arusha "managing director" | No name; ATTA member page (fetched) hides contacts behind a login. leopard-tours.com answers 202 (bot check). |
| Q16/80 | "Oikos East Africa" Arusha director | No name; ngobase lists the head as blank. oikosea.co.tz/contacts gives contact@oikosea.org only. |
| Q17/80 | "Tanzania Crop Care" Arusha managing director | Nothing on this company. |
| Q18/80 | "Arusha Meru International School" "Head of School" OR Principal OR Director 2026 | Nothing current. |
| Q19/80 | linkedin "General Manager" "Kibo Palace" Arusha | No snippet names a manager. |

## Blocked or needing a browser read

- 403: pwc.co.tz and pwc.com/tz, jwseagon.com (Tanmanagement), tccl.co.tz, artisan.co.tz, arushavilla.co.tz, shidolyasafaris.com, pajotasafaris.com, brightafricansafaris.com, paradise-wilderness.com, wildwaystanzania.com, thebusinessyear.com.
- Bot check: leopard-tours.com (HTTP 202 challenge).
- TLS failure: iaa.ac.tz, lushgardenhotels.co.tz, ecobank.co.tz.
- Not resolving: tz.kcbgroup.com, safariplus.tz, aphfta.org, a1hotelandresort.co.tz, arushacenterinn.com, newwayhotel.co.tz, venicehotel.co.tz.
- Server error: alanvertents.com (HTTP 500).

## Not reached

P3 organisations were not searched (reach-tier rule). P1 and P2 hotels and small operators whose sites name no manager remain for the call sheet (`scripts/contacts/build_call_sheet.py`).
