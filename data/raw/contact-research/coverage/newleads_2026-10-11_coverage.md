# Gap-census new leads: contact enrichment, 11 October 2026

Goal: for the 405 employers, 1 welfare home and 80 villages the campus gap census added on 11 October 2026, find the decision-maker for the offer (in-country head first, a group head as escalation), their direct route, the organisation's own details and sourced hooks; for villages, the VEO or village chair named by an official source.

Outputs:
- `data/raw/contact-research/website_contacts_2026-10-11.jsonl`: own-website crawl of the 41 new domains the crawler may read (`crawl_org_websites.py --date 2026-10-11 --only ...`; `.go.tz` sites are read with `read_page.py` instead).
- `data/raw/contact-research/search_newleads_2026-10-11.jsonl`: 94 master records and 1 welfare record (own pages, official registers and directories, budgeted search).
- `data/raw/contact-research/browser_googlemaps_2026-10-11.jsonl`: the coordinator's Google Maps lookups (`data/raw/gap-census/google_maps_enrich_2026-10-11.jsonl`), 78 accepted listings as source records (address, phone, website), plus a possible-duplicate note for Total Care Medical Center. Review rows were used as hints only; rejected rows were not used.
- `data/raw/hook-research/hooks_newleads_2026-10-11.jsonl`: 12 lead briefs, 7 hooks.
- `data/raw/gap-census/osm_matches_2026-10-11.jsonl`: 41 map-only leads matched to a real organisation (own or official page, or an accepted Google Maps listing with a phone or website), relabelled by `add_gap_census_leads.py --matches`.

Search allowance 90 (hard cap); used 67. Searches were spent on the larger organisations first (international bodies, manufacturers, aviation, hospitals, colleges, farms, retail chains), then the user-named safari operators, NGOs and hotels. Restricted searches (`allowed_domains`) were used for the ATE member directory, SafariBookings operator profiles, employers' own vacancy notices and council sites. No search was routed through a fetcher, and no results page was scraped. Pages were read with `scripts/contacts/read_page.py` (cached, 1.5 s per site, robots.txt honoured).

## Deterministic work (no search)

- Own sites read directly: KCMC, ESAMI (welcome message, contacts), African Court (contact, Office of the Registrar, a release giving the Registrar's address), TaCRI, MUWSA, CAMARTEC, AIIL (staff, Rector profile), Swissport Tanzania, TBL (about, contact), SBC Tanzania (profile, contact), Mount Meru Hotel, Sopa Lodges, Arusha Meat, Uhuru Hotel, Hatari ('Who we are'), DSW Tanzania, AWF, TNC Tanzania, Rikolto, Pams, Somo Africa, Bouncing Books, Save the Rain, Westerwelle Foundation, EarthLungs, Inherit Your Rights, Give a Heart to Africa, The Girls Foundation of Tanzania, Daraja Music Initiative, GA Insurance (contact, board, senior management).
- Websites the Google Maps listings gave, read for routes and people: asanterabi.co.tz, kiureengineering.com, mit.tareo-tz.org, mondulcoffee.com, sunkistgroup.com, shoppers.co.tz, lindotravel.com, stjosephhospitalmoshi.or.tz, tz.farajaafricafdn.org, mbwa-wa-africa.org, servingfriends.org, futuresensefoundation.org (nskhospitals.co.tz answered HTTP 500).
- ATE member directory pages (hrms.ate.or.tz): Arusha Meat, Sopa (CTHI), Enza Zaden Africa, GreenLight Planet, Kiure Engineering, LGT Logistics, MoCU, MUWSA, Nyirefami, RABEC, KADCO, Fides, Gardaworld (KK Security). Named mailboxes listed without a role were not recorded.
- Villages: the government run's council-site captures and their HTTP caches (2026-09-23 and 2026-10-10, about 1,000 news items per council) were searched for a village executive officer or village chair of each of the 80 villages. One mention only: Hai District Council news names 'Mwenyekiti wa Kijiji cha Mijongweni na mwenyekiti wa shule hiyo, Bakari Malola', which does not say clearly whether he is the village chair or only the school committee chair, so nothing was recorded.

## Searches

| # | Query | Outcome |
|---|---|---|
| Q1/90 | Bonite Bottlers Moshi managing director | Vacancy notice (Aug 2026, fetched): hr@bbl.co.tz, P.O. Box 1352 Moshi; MD unnamed. Recorded. |
| Q2/90 | Tanzania Breweries Limited managing director 2026 | TBL's own announcement (snippet; page 403): MD Michelle Kilpin. Recorded (snippet). |
| Q3/90 | KCMUCo Vice Chancellor | Now KCMC University; kcmuco.ac.tz does not resolve here. Nothing recorded. |
| Q4/90 | Ethiopian Airlines Arusha office manager | TCAA official page (2 Jul 2026, fetched): Country Manager for Tanzania, Netsanet Geleta. Recorded. |
| Q5/90 | KADCO Managing Director 2026 | Only undated or old MDs; ATE page (fetched): P.O. Box 10, phone. Recorded routes. |
| Q6/90 | "Kibo Match" Moshi | Nothing. |
| Q7/90 | Serengeti Breweries Moshi plant manager | MDs in news only (not a source for people); own site 403. |
| Q8/90 | ATE members Arusha Moshi (ATE directory only) | Found Fides Tanzania's member page (fetched). Recorded. |
| Q9/90 | Mount Meru Flowers general manager | Nothing current; revival reports for closed farms. |
| Q10/90 | Mount Meru Hotel general manager | Vacancy notice (Jul 2026, fetched): hr@mountmeruhotel.co.tz; own site info@, phone, 178 rooms. Recorded. |
| Q11/90 | "Masembo Safari" founder | Nothing. |
| Q12/90 | "Safari with Rafiki" owner | Only a different operator. |
| Q13/90 | "Suricata Safaris" Arusha | SafariBookings profile (fetched): owners Hilary and Martin (first names), 50-100 employees, P.O. Box 16301; own site info@. Recorded. |
| Q14/90 | "Black & White Travelers" | Nothing. |
| Q15/90 | Masembo Safari (SafariBookings) | Nothing. |
| Q16/90 | Mazingira Safari (SafariBookings) | Mazingira Eco Friendly Safaris profile (same phone): P.O. Box 12544, 10-20 employees. Recorded. |
| Q17/90 | Kilimanjaro Explore (SafariBookings) | Only similarly named operators. |
| Q18/90 | Papaya Tours (SafariBookings) | Only a different operator. |
| Q19/90 | WorldVeg ESA regional director | Named only in 2019; worldveg.org 202 (bot screen). |
| Q20/90 | IITA Arusha office | CGIAR page (fetched): office c/o NM-AIST. Recorded; iita.org TLS expired. |
| Q21/90 | TNC Tanzania program director | Director unnamed; own Tanzania page: phone, africa@tnc.org. Recorded. |
| Q22/90 | Solidaridad ECA managing director | Unnamed (Nairobi). |
| Q23/90 | Machame Lutheran Hospital medical director | Nothing current. |
| Q24/90 | Kibosho Hospital medical officer in charge | Undated partner page, now 404. Nothing recorded. |
| Q25/90 | PAPU Secretary General contact | TCRA notice (Jan 2026, snippet): sc@papu.co.tz, phone, PAPU Tower, P.O. Box 6026. Recorded (snippet); papu site 403. |
| Q26/90 | AUABC executive secretary | Own contact page (fetched): registry inbox, phone, AICC, P.O. Box 6071. Recorded. |
| Q27/90 | Kilemakyaro Mountain Lodge contact | Booking platforms only. |
| Q28/90 | Kindoroko Hotel website | Booking platforms only. |
| Q29/90 | Tanfoam managing director | Court record only. |
| Q30/90 | KMTC managing director | Named in news only (not recorded). |
| Q31/90 | Safari Junctions (SafariBookings) | Nothing. |
| Q32/90 | Safari Huella (SafariBookings) | Nothing. |
| Q33/90 | Kimgoni Tanzania Safaris (SafariBookings) | Profile (fetched): founder Philipo Kimgoni, 10-20 employees. Recorded. |
| Q34/90 | Mzuka Safaris (SafariBookings) | Nothing; mzukadventure.com does not resolve. |
| Q35/90 | AIIL executive director | Own site (fetched): Rector Judge Fatsah Ouguergouz, Programme Manager, info@, phone, AICC Kilimanjaro Wing, P.O. Box 561. Recorded. |
| Q36/90 | NSK Hospital Arusha contact | Nothing. |
| Q37/90 | Siha District Hospital medical officer in charge | Nothing. |
| Q38/90 | Hand in Hand EA Tanzania country director | Vacancy notice (2026, snippet): P.O. Box 7152, phone. Recorded (snippet); own site timed out. |
| Q39/90 | Global Bike Moshi country director | US press only. |
| Q40/90 | Daraja Music Initiative executive director | Conflicting undated third-party names; own site info@. Recorded inbox. |
| Q41/90 | "Give a Heart to Africa" founder | Own site (fetched): Executive Director Monika Fox, monika@. Recorded. |
| Q42/90 | "The Girls Foundation of Tanzania" director | Own site: office@, P.O. Box 11224. Recorded. |
| Q43/90 | KK Security Arusha branch manager | ATE page for Gardaworld Tanzania (Dar es Salaam head office). Group contact page disallowed by robots.txt (not used). |
| Q44/90 | Kiliflora managing director | News: government to take the farm back; possible closure. Notes only. |
| Q45/90 | East Africa Seed country manager | Nairobi head office; Arusha manager unnamed. |
| Q46/90 | Village Supermarket AIM Mall management | Nothing. |
| Q47/90 | Afisa Mtendaji wa Kijiji (Hai council and region sites) | No VEO named for the new villages. |
| Q48/90 | Afisa Mtendaji wa Kijiji (Meru, Arusha DC, region sites) | Only a 2018 ward executive; no village officer. |
| Q49/90 | Kilimanjaro Golf and Wildlife Estate general manager | Booking platforms only; golfsafarihouse.com does not resolve. |
| Q50/90 | Nyirefami managing director | Nothing. |
| Q51/90 | Sunkist Bakery managing director | Court records only. |
| Q52/90 | Spiritan Missionary Seminary rector | Nothing. |
| Q53/90 | A to Z Textile Mills vacancies (job boards) | No HR inbox. |
| Q54/90 | Enza Zaden Africa vacancy (job boards) | Vacancy notice (Jul 2026, fetched): vacancies@enzazaden.co.tz. Recorded. |
| Q55/90 | Sunkist Bakery vacancy (job boards) | Nothing. |
| Q56/90 | Serengeti Breweries Moshi vacancy (job boards) | No HR inbox. |
| Q57/90 | "Neema Orphanage" Machame ELCT | Vacancy notice (Jan 2025, fetched): run by the Sisters of Ushirika wa Neema; federation page (fetched): neema@elct.org, P.O. Box 1. Recorded (welfare). |
| Q58/90 | Jumla Africa Arusha branch manager | Vacancy notice (Oct 2026, fetched): jobs@jumlaafrica.com. Recorded. |
| Q59/90 | Kilimanjaro Wonders Hotel general manager | Booking platforms only. |
| Q60/90 | GA Insurance Arusha branch manager | Own contact page (fetched): Arusha branch address and phones. Recorded. |
| Q61/90 | Methodist college Arusha principal | Nothing; identity to confirm. |
| Q62/90 | Tanzania People and Wildlife director | Only a different body (TAWIRI). |
| Q63/90 | DTDA East Africa office Arusha director | Head of the Arusha sub-regional office unnamed. |
| Q64/90 | ECHO East Africa Impact Center director | Own announcement (Nov 2024, snippet; site 403): Charei Muene (also spelled Munene). Recorded (snippet). |
| Q65/90 | Rikolto East Africa regional director | Unnamed. |
| Q66/90 | Bright Star Hotels and Safaris owner | Booking platforms only. |
| Q67/90 | tanzania-safaris.com founder | Nothing; site 202 (bot screen). |

## Blocked or unreadable (recorded, never bypassed)

- HTTP 403: agapetourism.com (Mulala), serengetibreweries.co.tz, tanzaniabreweries.co.tz news page, upap-papu.africa, echocommunity.org.
- HTTP 202 with no page (bot screen): worldveg.org, tanzania-safaris.com, bristolcottages.com.
- TLS failure: iita.org (expired certificate), ulandssekretariatet.dk (expired), jumlaafrica.net and kiliwonders.com (hostname mismatch).
- Domain does not resolve: golfsafarihouse.com, hartebeest-lodge.com, mzukadventure.com, osygrandhotel.com, www.baltontz.com, kcmuco.ac.tz, kilemakyaro.com, plus guessed NGO domains.
- Timeout: handinhand-ea.org; HTTP 500: nskhospitals.co.tz; HTTP 511: worldserve.org.
- robots.txt disallows: garda.com contact page (KK Security), not used.

## Not reached

Most of the 161 clinics and dispensaries, the small guest houses and the 2-3 person NGOs had no website, no directory entry and no Google Maps listing in the coordinator's lookup; they keep the census record only.
