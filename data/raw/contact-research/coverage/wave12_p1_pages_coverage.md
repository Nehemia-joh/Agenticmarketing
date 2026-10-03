# Wave 12 P1 own-pages coverage, 2 October 2026

Brief: `runtime/contacts/prompts/wave12_p1_pages.md`. Targets: `runtime/contacts/slices/wave12_p1_targets.json` (100 P1 employers, all master).
Output: `data/raw/contact-research/search_wave12_p1_pages_2026-10-02.jsonl` (30 organisations, 46 people or role desks).
Scratch: `runtime/contacts/agents/wave12_p1_pages/` (crawler `crawl.py`, digests `digest/NN.txt`, builder `build.py` + `entries.py`, which checks every excerpt against the saved page).

Method: every target with a domain was crawled with the contact-research fetcher (`contact_lib.fetch`, robots.txt honoured, 2.0 s per-site spacing, HTTP cache): home page plus up to nine own links on about, team, leadership, management, board, staff, careers, administration, directorate, contact and press. Leads were then re-read with `scripts/contacts/read_page.py`. Searches were used only for targets whose own pages gave nothing (mostly targets without a website).

## Searches (35 of 40 used; none refused)

| No. | Query | Outcome |
|---|---|---|
| Q1/40 | "Ithna-asheri Hospital" Arusha administrator OR "medical director" OR "human resources" | World Federation vacancy page (read; no names). Names in the summary came from directories (medpages); not recorded |
| Q2/40 | "Shree Hindu" hospital Arusha administrator OR director | Directories only (medpages, afyadirectory); nothing recorded |
| Q3/40 | "Aga Khan" hospital Arusha medical centre "general manager" OR "head" Arusha | AKHS pages; the Arusha page is script-built; no Arusha head named |
| Q4/40 | "Kaloleni Hospital" Arusha | Volunteer and directory pages only |
| Q5/40 | "Saruni River Lodge" Arusha manager | Booking sites and Facebook only (not sources) |
| Q6/40 | "Tanzanite City Park Lodge" Arusha | No such property found |
| Q7/40 | Arusha City Council Levolosi Kaloleni health centre "mganga mfawidhi" OR "in-charge" | Ministry of Health facility register (HFR) entry for Levolosi read: official phone, in-charge field blank |
| Q8/40 | "Njake Oil" Arusha | Map directories only (a fuel station at Kikatiti) |
| Q9/40 | "Lashku Forex" Arusha | TATO listing already used in wave 11; nothing new |
| Q10/40 | "AAR Healthcare" Tanzania Arusha clinic "country manager" OR "managing director" OR "human resources" | ZoomInfo, RocketReach, LinkedIn only (not sources) |
| Q11/40 | "Institute of Accountancy Arusha" "Deputy Rector" "Planning, Finance and Administration" OR "Human Resource Management" | Results were for TIA, not IAA; brokers; nothing recorded |
| Q12/40 | "Mbasha Holdings" Arusha | Netlify draft site (read; no people), TATO entry (no people), brokers |
| Q13/40 | "Gran Melia Arusha" "general manager" | justluxe.com award article quoting the GM (read; recorded with caveat) |
| Q14/40 | "Kibo Palace Hotel" Arusha "general manager" | Review and booking sites only |
| Q15/40 | "Arusha Meru International School" director OR "head of school" OR bursar OR administrator | School's older Wix site (read; head of school named); broker pages not used |
| Q16/40 | "Ilboru Safari Lodge" Arusha owner OR "general manager" OR director | Tour-operator pages and Travel Weekly (403); nothing recorded |
| Q17/40 | "Karibu Camps" Tanzania founder OR director OR "general manager" | ATTA directory read (contacts behind member login: block); broker names not recorded |
| Q18/40 | "United Aviation Services" Arusha "managing director" OR "general manager" | TATO listing only; no name |
| Q19/40 | "Delight Polyclinic" Arusha director OR founder OR "medical director" | Directories only |
| Q20/40 | "NSK Hospital" Arusha "human resource" OR "managing director" OR "hospital administrator" | HFR register entry read (official phone); LinkedIn not used |
| Q21/40 | "Gupta Auto Spares" Arusha director OR "human resources" OR vacancy | TATO entry read (no person; bm@ address unlabelled, so not tied to a role); D&B not used |
| Q22/40 | Archdiocese of Arusha health department "Usa River" OR Kijenge health centre dispensary coordinator | No diocesan staff page found |
| Q23/40 | "Citylink" OR "City Link Pentagon" hotel Arusha manager | TripAdvisor only (not a source) |
| Q24/40 | "Everyday Safaris" Arusha founder OR director OR owner | Director names only on ZoomInfo and a travel profile; own about page (read) does not name them; not recorded |
| Q25/40 | "Health 4 All" clinic Arusha Tanzania director | Own site listed but its domain does not resolve; nothing recorded |
| Q26/40 | "Avinta Care" polyclinic Arusha | HFR register entry read (owner, official phone) |
| Q27/40 | "Gemsa" polyclinic Arusha | HFR register entry read (owner, official phone) |
| Q28/40 | "Ngare Sero Mountain Lodge" OR "Ngare Sero Mountain Retreat" owner OR manager Usa River | Pointed to the lodge's own "Our Team" text, then confirmed on the own site |
| Q29/40 | "Kitamu" Arusha "Leah Assenga" OR "Kitamu House" OR "Kitamu Africa" | Founder already held; own site robots-disallowed; nothing new |
| Q30/40 | "Safari Wholesalers" Arusha Tanzania | Own site is a "coming soon" page; nothing |
| Q31/40 | "R&D Polyclinic" Arusha | HFR list page only; no names |
| Q32/40 | "Makeseni Lodge" Arusha | Booking and review sites only |
| Q33/40 | "Mango Bed and Breakfast" OR "Mango Bed & Breakfast" Arusha | Not found |
| Q34/40 | "Exim Bank" Tanzania "Head of Human Resources" OR "Chief Human Resources Officer" site:eximbank.co.tz | Summary names the HR head from an Exim news page; the page now returns 404 (recorded fetched: false) |
| Q35/40 | "Azania Bank" "Head of Human Resources" OR "Human Resources Manager" OR "Director of Human Resources" | Names only on data brokers (not recorded); own management page lists no HR director |

## Blocks and unreadable sites (recorded, not worked around)

- HTTP 403 to the crawler: pwc.co.tz (www) and www.pwc.com/tz (PwC Tanzania); jwseagon.com (Tanmanagement / JW Seagon); melia.com (Gran Melia); www.nmbbank.co.tz (NMB Bank); tz.usembassy.gov medical list; travelweekly.com.
- Bot check: equitygroupholdings.com (Incapsula script page).
- Login: atta.travel member directory (member contact details need a login); mtmerurrh.go.tz careers profile redirects to a login.
- robots.txt disallows: kitamuhouse.com (Kitamu Africa); not read.
- WebFetch refused by the tool's permission settings for agakhanhospitals.org, www.aarhealth.com and www.iaa.ac.tz; not retried.
- DNS failure: health4allclinics.co.tz, safariplus.tz (the company was found at safariplus.co.tz), tz.kcbgroup.com (KCB).
- Certificate failure: iaa.ac.tz (Institute of Accountancy Arusha) on every scheme, so not read; selianlh.or.tz read over http.
- Parked domains (redirect to "/lander"): aarhealth.com (AAR Clinic) and mbashaholdings.com (Mbasha Holdings). A person should check the websites held for these two.
- Script-built pages with no readable text: aafrinmedihealth.com, the eximbank.co.tz management tab, agakhanhospitals.org/arusha, safariwholesalers.com ("coming soon").

## Targets with nothing new, and targets not reached

- Own pages read, nothing beyond what is held (people already in the database, or none published): 0, 1, 2, 6, 8, 12, 15, 16, 18, 21, 22, 23, 26, 27, 28, 29, 31, 32, 34, 35, 36, 37, 38, 39, 40, 42, 43, 48, 57, 63, 71, 74, 75, 78, 79, 80, 81, 82, 86, 87, 88, 90, 97 (numbers as in the table below). Lion King's office team lists no HR or administration role; ALMC's "Administration team" section is empty; Azania lists no HR director; DTB adds only a COO (Al-Amin Merchant, not recorded); Moivaro's staff page names camp managers, none for Moivaro Coffee Lodge; MSTCDC's team page gives no email for the HR head (the address beside the next entry belongs to the Academic Dean).
- Not reached on any own page: 4 PwC, 17 JW Seagon, 44 AAR Clinic, 49 Health 4 All, 50 IAA, 54 Kitamu, 58 Mbasha, 83 Aafrin, 84 Equity, 85 KCB, 89 Gran Melia (third-party article only), 98 NMB.
- No website, and searches gave nothing usable: 51 Ithna-asheri Hospital, 52 Kaloleni Hospital, 53 Kijenge RC Dispensary, 55 Lashku Forex, 62 R&D Polyclinic, 66 Shree Hindu Hospital, 69 Aga Khan University Hospital, 91 Makeseni Lodge, 92 Mango Bed & Breakfast, 94 Njake Oil, 95 Saruni River Lodge, 96 Tanzanite City Park Lodge. Not searched, to keep the allowance: 60 Old Arusha Health Center, 61 Oloirien Community Dispensary, 67 Tanta Dental Clinic (CEO already held), 72 Usa RC Health Centre. The public facilities would go through the Arusha City Council or diocesan health office.

## Points for a person to check

- Gran Melia Arusha: the GM's name comes from a 2022 lifestyle article, not the hotel's site.
- Arusha Meru International School: the head of school is from the 2016 Wix site; the current site names only the heads of primary and secondary.
- Exim Bank: the HR head is snippet-only, from a removed news page.
- NSK Hospitals: the register phone and the site phone differ by two digits.
- Safari Plus: head office is in Dar es Salaam (Hyatt Regency); check the Arusha link.
- Matembezi and HP Safaris: personal-style addresses (stephanie@, christian@, gary@horspistes.ch) appear on the pages but not beside a name, so they are recorded as organisation addresses only.

## Pages read per target (crawler)
| # | Target | Pages read by the crawler (status) | Result |
|---|---|---|---|
| 0 | Africa Dream Safaris | 7 read: /, /community/humanitarian/foundation-for-african-medicine-education/, /about-us/, /contact/, /awards-and-press/, /lodging/four-seasons-lodge/, /create-your-own-itinerary | nothing new |
| 1 | MS Training Centre for Development Cooperation | 10 read: /, /Leadership-and-governance, /academic-courses/master-leadership-and-governance, /african-journal-leadership-and-governance, /about/team, /publications/strategy/transforming-leadership-africa, /professional-courses/organisational-risk-management-and-oversight, /feature/nurturing-new-generation-eas | nothing new |
| 2 | CORTO SAFARIS Ltd | 2 read: /, /reserver-voyage-tanzanie/ | nothing new |
| 3 | Nelson Mandela African Institution of Science and Technology | 10 read: /, /the-nelson-mandela-african-institution-of-science-and-technology-nm-aist/about-nm-aist/governance-and-leadership/executive-management/, /the-nelson-mandela-african-institution-of-science-and-technology-nm-aist/about-nm-aist/governance-and-leadership/nm-aist-council/, /the-nelson-mandela-african- | **found**: Sweetbert S. Mutagurwa |
| 4 | PwC Tanzania | none readable; 403 HTTP 403 robots=none; None URLError: <urlopen error [Errno 11001] getaddrinfo fail | nothing new |
| 5 | Dream Peak Safaris | 6 read: /, /about-dream-peak-tours-safaris/, /contact-us/, /zanzibar-stone-town-spice-tour-day-trip/, /get-your-custom-itinerary/, /8-unique-experiences-you-can-add-to-your-tanzania-safari/ | **found**: Mheluka Kubiha, Africa Silayo, Mary Silayo |
| 6 | Lion King Adventures (King Kidaisho) | 6 read: /, /office-team/, /about-us/, /our-guides/, /our-safari-vehicles/, /our-guides/ | nothing new |
| 7 | Matembezi Company Ltd | 3 read: /, /about-us/, /contact-us/ | **found**: Stephanie Kuerzinger, Christian Ruggiero, Hagai Zvulun |
| 8 | Parks East Africa Ltd | 4 read: /, /8-days-tanzania-people-wildlife, /about-us, /contact-us | nothing new |
| 9 | Safari.Africa | 3 read: /, /plan-your-journey, /our-story | **partial**: Caroline Mungai, Raymond Respick |
| 10 | Shadows of Africa Ltd | 6 read: /, /about-us/contact-us, /team/, /about-us/about-shadows-of-africa-445, /about-us/social-responsibility, /about-us/travel-memberships | **partial**: Katlijn |
| 11 | JM Tours Ltd | 4 read: /, /contact-us/, /best-tanzania-safari-company/, /best-tanzania-safari-company/ | **found**: Joshua Mushendwa, Barbro Mushendwa, Siima Mushendwa, Sune Mushendwa |
| 12 | Delight Polyclinic | 4 read: /, /contact/, /about/, /our-medical-services/ | nothing new |
| 13 | Kibo Palace Hotel | 3 read: /, /sustainability/, /carrers/ | **partial**: Recruitment / HR office (desk) |
| 14 | Ngare Sero Mountain Retreat | 2 read: /, /contact | **found**: Tim Leach, Mike Leach |
| 15 | AICC Hospital | 6 read: /, /leadership/board-of-directors, /leadership/management, /contactus, /aboutus, /plan-your-event | nothing new |
| 16 | Arusha Technical College | 10 read: /, /top_leadership, /management, /directorate/DA, /directorate/DASS, /directorate/DRCP, /directorate/DHRMA, /directorate/FAU, /directorate/PDU, /directorate/SSSU | nothing new |
| 17 | Tanmanagement Insurance Brokers Ltd (JW SEAGON) | none readable; 403 HTTP 403 robots=none | nothing new |
| 18 | Active Tanzania Adventures Limited | 4 read: /, /meet-a-tribe/, /about-us/, /contacts/ | nothing new |
| 19 | HP Safaris (T) Limited | 2 read: /, /votre-demande-de-devis/ | **partial**: organisation routes only |
| 20 | Kiliclimb Africa Safaris | 9 read: /, /meet-the-kiliclimb-africa-safaris-team/, /important-information-about-kilimanjaro-climbing/, /important-information-about-tanzania-safari/, /about-us/, /contact-us/, /choosing-the-perfect-time-for-your-kilimanjaro-adventure/, /preparing-for-your-kilimanjaro-climb/, /kilimanjaro-group-joining/ | **found**: Sara John, Naite Saruni, Managing Director (phone line; not named) |
| 21 | African Big Cats Safaris | 5 read: /, /contact-us/, /company-profile/, /our-video-reviews/, /tailor-your-itinerary/ | nothing new |
| 22 | Ajabu Adventures Ltd. | 7 read: /, /about-us/team/, /about-us/team, /about-us/, /about-us/travel-stories/, /contact/, /book-your-safari/ | nothing new |
| 23 | Bearfoot Expeditions | 3 read: /, /about-bearfoot-expeditions/, /contact-us/ | nothing new |
| 24 | Dakik Expeditions LTD | 6 read: /, /about-us/, /contact-us/, /plan-your-trip/, /experiences/zanzibar-getaways/, /media-press-kit/ | **partial**: Rawan Dakik |
| 25 | Earthlife Expeditions Company Limited | 6 read: /, /about-us/our-team/, /about-us/, /contact-us/, /about-us/our-safari-vehicles/, /about-us/booking-terms-conditions/ | **found**: Catherine Haule |
| 26 | Jambo Masai Tours | 3 read: /, /about, /contact | nothing new |
| 27 | KIBO GUIDES (T) LTD | 3 read: /, /about, /connect | nothing new |
| 28 | Make My Safari Limited | 3 read: /, /about/, /contact-us/ | nothing new |
| 29 | Rupia Adventure | 6 read: /, /about-us-2/, /about-tanzania/, /contact-us-6/, /contact, /our-vehicles/ | nothing new |
| 30 | Serengeti African Tours | 10 read: /, /our-team/, /about/, /contact/, /about-us/, /our-vehicles/, /joining-group-safaris/, /fly-in-tour-from-zanzibar/, /safari/6-days-highlights-of-africa-vacation-tour-package-tanzania/, /safari/2-day-joining-group-safari-tour-tanzania/ | **found**: Brian Williams, James Michael, Careers desk (the Send Your CV link) |
| 31 | Serengeti Big Cats Safaris Ltd | 2 read: /, /contact/ | nothing new |
| 32 | Simba Safaris Ltd | 4 read: /, /about-us, /contact-us, /our-payment-method-policies | nothing new |
| 33 | Snow Africa Adventures | 7 read: /, /about-us/, /contact-us/, /kilimanjaro-join-group-departures/, /best-tanzania-tour-operator/, /best-kilimanjaro-tour-operators/, /our-guides/ | **found**: Emmanuel Moshi, Florent Zachary Ipananga |
| 34 | Tandala Expeditions Limited | 3 read: /, /contact-us/, /new/contact-us/ | nothing new |
| 35 | Translen Investments and Trading Ltd | 5 read: /, /about-us/, /about-us/tanzania-safari-booking-terms-and-conditions/, /about-us/tanzania-travelers-information/, /contact-us/ | nothing new |
| 36 | Wild Pride Safaris | 3 read: /, /about-us/, /contact-us/ | nothing new |
| 37 | Wise Safari Tanzania Limited | 4 read: /, /about-us, /inquire-now, /plan-your-perfect-tanzania-safari-with-us | nothing new |
| 38 | Arusha Lutheran Medical Centre (ALMC) | 3 read: /, /about.html, /contact.html | nothing new |
| 39 | BUSHBUCK SAFARIS LIMITED | 6 read: /, /contact-us, /company-profile, /our-vehicle, /our-drivers, /group-corporate-safaris | nothing new |
| 40 | Augustine's Adventure Africa ltd (AA Africa) | 10 read: /, /about-us/our-staff/, /about-us/, /about-us/why-aa-africa/, /about-us/about-usmessage/, /about-us/flying-doctors/, /about-us/faq/, /about-us/testimonials/, /contact/, /about-us/flying-doctors | nothing new |
| 41 | Josh Dreamland Safaris | 9 read: /, /team-member/, /team-member/angel-lema/, /team-member/elizabeth-asimbile/, /team-member/consolata-chonya/, /team-member/kesline-minja/, /team-member/gerald-ephata/, /contact-us/, /serengeti-at-sunrise-why-the-golden-hour-is-africas-greatest-show/ | **found**: Angel Lema, Gerald Ephata |
| 42 | Everyday Safaris | 6 read: /, /our-guides-team/, /about-us/, /contact-us/, /contact/, /plan-your-adventure/ | nothing new |
| 43 | Karibu Camps | 5 read: /, /contact/, /about-us/, /enhance-your-stay/, /our-locations/ | nothing new |
| 44 | AAR Clinic | 1 read: / | nothing new |
| 45 | Arusha Meru International School | 4 read: /, /faculties-and-staff, /contact, /about | **partial**: Donald Cuñado |
| 46 | Avinta Care Specialized Polyclinic | no domain | **partial**: organisation routes only |
| 47 | Gemsa Specialized Polyclinic | no domain | **partial**: organisation routes only |
| 48 | Gupta Auto Spares and Hardware Limited | 5 read: /, /about-us, /contact, /contact, /about-us | nothing new |
| 49 | Health 4 All | none readable; None URLError: <urlopen error [Errno 11001] getaddrinfo fail | nothing new |
| 50 | Institute of Accountancy Arusha (IAA) | none readable; None URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILE | nothing new |
| 51 | Ithna-asheri Hospital | no domain | nothing new |
| 52 | Kaloleni Hospital | no domain | nothing new |
| 53 | Kijenge RC Dispensary | no domain | nothing new |
| 54 | Kitamu Africa LTD | none readable; ## http://kitamuhouse.com/ ROBOTS-DISALLOWED; ## https://kitamuhouse.com/ ROBOTS-DISALLOWED; None URLError: <urlopen error [Errno 11001] getaddrinfo fail | nothing new |
| 55 | Lashku Forex Bureau Limited | no domain | nothing new |
| 56 | Levolosi Health Centre | no domain | **partial**: organisation routes only |
| 57 | MEGA TENTS (AL-ANVER OUTFITTERS LTD) | 1 read: / | nothing new |
| 58 | Mbasha Holdings Ltd | 1 read: / | nothing new |
| 59 | NSK HOSPITALS LTD | 3 read: /, /contact-us/, /company/ | **partial**: organisation routes only |
| 60 | Old Arusha Health Center | no domain | nothing new |
| 61 | Oloirien Community Dispensary | no domain | nothing new |
| 62 | R&D Polyclinic | no domain | nothing new |
| 63 | Safari Wholesalers and Retailers Limited | 1 read: / | nothing new |
| 64 | Safari plus ltd | 3 read: /, /about/, /our-fleet/ | **partial**: Reservation & Administration (desk) |
| 65 | Selian Lutheran Hospital Ngaramtoni | 1 read: / | **found**: Dr. Amon Israel Marti |
| 66 | Shree Hindu Hospital | no domain | nothing new |
| 67 | Tanta Dental Clinic | no domain | nothing new |
| 68 | Tengeru Institute of Community Development | 10 read: /, /departments/project-planning-management/, /about/, /about, /contacts/, /organization, /departments/gender-and-community-development/, /departments/gender-and-social-welfare/, /courses/course/3/, /courses/course/4/ | **found**: Prof. Bakari George |
| 69 | The Aga Khan University Hospital | no domain | nothing new |
| 70 | Tumaini University Makumira Offices | 6 read: /, /about-us/, /contact-us/, /our-objectives/, /draft-page/, /research-2/ | **found**: Mr. Peter Kirenga |
| 71 | United Aviation Services Company Ltd | 5 read: /, /index_php/aboutus, /index_php/about-uas, /index_php/contact-uas, /index_php/conctactus | nothing new |
| 72 | Usa RC Health Centre | no domain | nothing new |
| 73 | Paradies Safaris Ltd | 6 read: /, /en/home/about-us, /en/contact, /es/contacto, /fr/contacter, /de/impressum | **found**: Hilde Keil, Robin Keil, Accounts (desk) |
| 74 | St. Augustine University of Tanzania - Arusha Campus | 9 read: /, /hospitality-management/, /bachelor-of-science-in-business-administration/, /bachelor-of-science-in-business-administration/finance/, /about-us/, /contact/, /2024/06/06/professor-alexa-is-interviewed-about-twitters-valuation/, /lp-profile/, /mem/ | nothing new |
| 75 | Tanzania Wildlife Research Institute (TAWIRI) | 9 read: /, /management-and-organization-structure/, /board-member/, /about-tawiri/, /About-tawiri/, /research/, /corporate_service/, /tawiri-reports/, /report-for-controller-and-auditor-general-on-the-financial-and-compliance-audit-of-tanzania-wildlife-research-institute-for-the-financial-year-ended-30-june | nothing new |
| 76 | VisionFund Tz MF Bank (HQ) | 8 read: /, /careers/, /about/, /contact/, /news/job-advertisement-relationship-officer-supervisor-branch-office/, /news-category/job-advertisement/, /our-impact/, /login | **found**: Rogathe Godson, Deogratius Siria |
| 77 | Good Earth Safaris & Tours Ltd | 8 read: /, /team/, /about-us/, /contact, /contact/, /our-impact/, /what-your-safari-tour-operator/, /how-to-convince-your-partner-to-go-on-safari/ | **found**: Elia Mushi, Baraka Maro, Daria Munuo |
| 78 | Safari Asap | 4 read: /, /about-us/, /contact-us/, /activity/weddings-during-your-tanzania-safari/ | nothing new |
| 79 | Davis & Shirtliff | 10 read: /, /executive-team, /integrated-management-system-policy-01, /generators/product/dayliff-ouboard-engine, /careers, /products-and-solutions/product/dayliff-ouboard-engine, /vacancies, /about-us, /contact-us, /corporate-social-responsibility | nothing new |
| 80 | Azania Bank | 9 read: /, /management-team/, /careers/, /board-members/, /forex/contact-azania-desk/, /azania-bank-launches-revolutionary-digital-banking-system/profile/, /annual-report/, /financial-regulatory-reports/audited-financials/, /financial-regulatory-reports/quarterly-reports/ | nothing new |
| 81 | Tanzanian Postal Bank | 8 read: /, /cash-management-solutions, /tcb-team, /career, /contact-us, /about, /corporate-and-commercial-insurance, /corporate-banking | nothing new |
| 82 | Diamond Trust Bank | 9 read: /, /board-of-directors, /executive-committee, /careers, /annual-general-meeting-agm, /about, /for-your-business/accounts, /for-your-business/solutions, /annual-financial-reports | nothing new |
| 83 | Aafrin Medihealth Solutions Ltd | 1 read: / | nothing new |
| 84 | Equity Bank | 1 read: / | nothing new |
| 85 | KCB | none readable; None URLError: <urlopen error [Errno 11001] getaddrinfo fail | nothing new |
| 86 | Moivaro Coffee Lodge | 6 read: /, /about-us/our-staff, /about-us, /about-us/our-mission, /about-us/our-videos, /contact-us | nothing new |
| 87 | Mount Meru Regional Hospital | 7 read: /, /staffs, /directorates, /career, /careers/profile, /about-us, /press-release | nothing new |
| 88 | Citylink Hotel | 4 read: /, /about-us/, /contact-us/, /2016/09/10/our-conference-room/ | nothing new |
| 89 | Gran Melia Arusha | none readable; 403 HTTP 403 robots=none | **partial**: Nicolas Konig |
| 90 | Ilboru Safari Lodge | 4 read: /, /about-us/, /contact-us/, /about-us | nothing new |
| 91 | Makeseni Lodge | no domain | nothing new |
| 92 | Mango Bed & Breakfast | no domain | nothing new |
| 93 | Mt. Meru Game Lodge | 3 read: /, /history, /impressum | **found**: Harry Bell, Kim Bell |
| 94 | Njake Oil | no domain | nothing new |
| 95 | Saruni River Lodge | no domain | nothing new |
| 96 | Tanzanite City Park Lodge | no domain | nothing new |
| 97 | Wild Mind Travel Company | 2 read: /, /contact/ | nothing new |
| 98 | NMB Bank | none readable; 403 HTTP 403 robots=rules; None URLError: <urlopen error [WinError 10060] A connection  | nothing new |
| 99 | Exim bank | 4 read: /, /en/careers, /en/about, /help | **partial**: Fredrick Kanga |

## Pages read by hand after the crawl (read_page.py)

mstcdc.or.tz/about/team (no email beside the HR head); dreampeaksafaris.com about page; lionkingadventures.com/office-team/; shadowsofafrica.com/team/; hors-pistes-en-tanzanie.fr home; almc.or.tz/about.html; selianlh.or.tz (http); makumira.ac.tz/contact-us/; paradiessafaris.com about-us and de/impressum; mountmerugamelodge.co.tz history and impressum; vftz.co.tz/about/; goodearthtours.com/team/; moivaro.com/about-us/our-staff; eximbank.co.tz/en/about; azaniabank.co.tz/management-team/; nm-aist.ac.tz departments-and-units page; ticd.ac.tz home and organization; sautarusha.ac.tz home and about-us; wildmindtravel.com/who/; kiboguides.com/elect; ngare-sero-lodge.co.tz lodge and contact; citylinkhotel.co.tz/hotel-facts-sheet/; everydaysafaris.com about-us and our-guides-team; matembezi.co.tz home and contact-us; snowafricaadventure.com best-tanzania-tour-operator and our-guides; jmtours.com best-tanzania-safari-company; dakikexpeditions.com media-press-kit; kiliclimbafricasafaris.com team page; safariplus.co.tz (crawled, 3 pages); arushameru.wixsite.com/amis about-us and contact-us; mbasha-holdings-wip.netlify.app; tatotz.org entries for Mbasha and Gupta; atta.travel Karibu Camps entry; archive.world-federation.org vacancy page (Ithna Asheri); justluxe.com Gran Melia article; HFR register PDFs 103490-9 (Levolosi), 121376-8 (Avinta), 113625-8 (Gemsa), 123714-8 (Roland Health Care, a different clinic; not used), 111486-7 (NSK); HFR quick-search list (no names).
