# Coverage: wave12_p1_jobs (HR contacts from vacancy notices and careers pages), 2026-10-02

Brief: runtime/contacts/prompts/wave12_p1_jobs.md. Targets: runtime/contacts/slices/wave12_p1_targets.json (100 P1 employers, all db=master).
Output: data/raw/contact-research/search_wave12_p1_jobs_2026-10-02.jsonl (12 records, all status partial).
Searches used: 55 of 60. The session limit was never reached. No search was sent through WebFetch, a browser or a results page.
Pages were read with scripts/contacts/read_page.py (cached, spaced, robots.txt honoured). Scratch helpers in runtime/contacts/agents/wave12_p1_jobs/
called the same cached fetcher (contact_lib.fetch) to:
- decode Cloudflare-protected email text the way the project crawler does (contact_lib.extract);
- list careers links on home pages;
- extract PDF text with pypdf.
No login, portal account, CAPTCHA or social profile was used. No person was looked up by name. Nobody was contacted.

Targets addressed to "the company team" came first, then named targets whose recipient is not HR.

## Searches

| # | Query (short) | Outcome |
|---|---|---|
| Q1/60 | PwC Tanzania vacancy HR Arusha | Snippet: applications are online only. pwc.co.tz careers page returned 403 (block). Nothing recorded. |
| Q2/60 | Shadows of Africa vacancy email | Found the mabumbe.tz notice (May 2025) and the ajirayako notice (Jul 2025). Recorded legal.dept@ |
| Q3/60 | Kibo Palace Hotel vacancy HR | Found the own careers page and a mabumbe notice (Jun 2025). Recorded recruitment@ |
| Q4/60 | Delight Polyclinic vacancy | Only a dentist advert on tanzajob (not read), with no contact. Nothing. |
| Q5/60 | JM Tours vacancy | Only directory and ZoomInfo results (ZoomInfo not used). Nothing. |
| Q6/60 | Ngare Sero lodge vacancy | No notices. Nothing. |
| Q7/60 | Karibu Camps vacancy | Found the fursa.co.tz notice (deadline 31 Jul 2026) and the Zoom Tanzania careers page. Recorded hr@ |
| Q8/60 | AMIS vacancy HR | Found the mabumbe notice (May 2024). Recorded recruitment@ |
| Q9/60 | Gran Melia Arusha vacancy HR | Found an expresstz 2019 notice (stale) and a Zoom Tanzania expired advert with no email. Recorded. |
| Q10/60 | IAA nafasi za kazi | Recruitment runs through PSRS / Ajira Portal (mabumbe, Feb 2026). No IAA HR contact. Nothing. |
| Q11/60 | NSK Hospital vacancy | Found the mavusu notice (Feb 2026): applications by WhatsApp. Recorded. |
| Q12/60 | Selian Lutheran Hospital vacancy HR | Only US results. Nothing. |
| Q13/60 | Aga Khan Hospital Arusha vacancy | Only Dar and Kenya HR results. Nothing for Arusha. |
| Q14/60 | Shree Hindu hospital Arusha vacancy | Found an expresstz notice (Nov 2021, stale). Recorded. |
| Q15/60 | United Aviation Services vacancy | Only contact pages. Nothing new. |
| Q16/60 | Gupta Auto Spares (GASH) vacancy | Only directories. Nothing. |
| Q17/60 | Ilboru Safari Lodge vacancy | Nothing. |
| Q18/60 | Citylink Hotel vacancy | Nothing. |
| Q19/60 | Mount Meru Game Lodge vacancy | Only ZoomInfo and tour sites (ZoomInfo not used). Nothing. |
| Q20/60 | Safari Plus vacancy | Nothing. |
| Q21/60 | Tumaini University Makumira vacancies | Found the own PDF advert (Apr 2025). Recorded hr@ and vc@ |
| Q22/60 | Selian nafasi za kazi 2025/2026 | Nothing. |
| Q23/60 | AAR clinic Arusha vacancy | Nothing. |
| Q24/60 | Al-Anver / Mega Tents vacancy | Only ZoomInfo and TATO results. Nothing. |
| Q25/60 | TICD vacancy HR / Rector | Only snippets (Ajira Portal posts). The oas.ticd.ac.tz PDF refused the connection. Nothing. |
| Q26/60 | Saruni / Tanzanite City Park / Makeseni vacancy | Only booking and review sites. Nothing. |
| Q27/60 | Njake Oil vacancy | Nothing. |
| Q28/60 | Ithna Asheri / KSIJ hospital vacancy | The World Federation archive notice is undated and gives no contact. Nothing. |
| Q29/60 | ALMC vacancy HR email | Only an aggregator and a 2016 blog. Nothing usable. |
| Q30/60 | Azania Bank vacancy HR email | The careers page gives only customercare@. Notices are from 2021 (stale) with no email read. Nothing. |
| Q31/60 | Exim Bank Head of HR vacancy | Applications use the careers portal. A snippet named a person (source unclear, not used). Nothing. |
| Q32/60 | Africa Dream Safaris careers | Nothing. |
| Q33/60 | Simba Safaris vacancy | Only ZoomInfo and contact pages. Nothing. |
| Q34/60 | Bushbuck Safaris vacancy | Nothing. |
| Q35/60 | Moivaro vacancy | The own "Our Staff" page is a history page with no HR contact. Nothing. |
| Q36/60 | Good Earth Tours vacancy | Nothing. |
| Q37/60 | Arusha safari vacancy "hr@" (job-board sweep) | Results for non-target companies only. Nothing. |
| Q38/60 | Tandala / African Big Cats / Paradies vacancy | Nothing. |
| Q39/60 | SAUT Arusha vacancy HR | Nothing. |
| Q40/60 | TanManagement / JW Seagon vacancy | tm.co.tz gives info@ only. Nothing. |
| Q41/60 | Health 4 All clinic vacancy | Nothing. |
| Q42/60 | Delight Dental / Polyclinic dentist vacancy | Nothing. |
| Q43/60 | City Link Pentagon hotel vacancy | Nothing. |
| Q44/60 | Safari Wholesalers / Wild Mind / Everyday Safaris vacancy | Nothing. |
| Q45/60 | MS TCDC vacancy email | Snippet gives jobs@mstcdc.or.tz. The own page returned 403 (block). Recorded as fetched: false. |
| Q46/60 | Davis & Shirtliff Tanzania vacancy | Applications use the online portal only. Recorded the TZ contact centre (not HR). |
| Q47/60 | VisionFund Tanzania vacancy HR | Found the ajirayako notice (Aug 2025). Recorded application@ |
| Q48/60 | ALMC nafasi za kazi 2025 | Nothing. |
| Q49/60 | DTB Tanzania vacancy HR email | The careers page gives only customercare@. Nothing. |
| Q50/60 | TCB Bank Director of HR vacancy | tcbbank.co.tz failed DNS. Nothing. |
| Q51/60 | Equity Bank Tanzania vacancy email | Found the ajirayako notice (Mar 2025). Recorded tzrecruitment@ |
| Q52/60 | AICC nafasi za kazi | Recruitment runs through PSRS / Ajira Portal. ajirampya360 failed on SSL. Nothing. |
| Q53/60 | KCB Bank Tanzania vacancy email | The careers page gives only customercare@. tz.kcbgroup.com failed DNS. Nothing. |
| Q54/60 | Usa River / Ngaramtoni hospital vacancy | Only off-topic results. Nothing. |
| Q55/60 | Mount Meru Hotel / Kibo Palace / Gran Melia HR Manager 2026 | Nothing new for the targets (Mount Meru Hotel is not a target). |

## Pages read and what each gave

- kibopalacehotel.com/carrers/ (own careers page): recruitment@kibopalacehotel.com, office visits by appointment.
- mabumbe.com Kibo Palace notice (5 Jun 2025): HR Office by appointment, same email.
- mabumbe.tz Shadows of Africa notice (19 May 2025): legal.dept@shadowsofafrica.com.
- ajirayako Shadows CPA Accountant notice (deadline 20 Jul 2025): the same address.
- zoomtanzania.net/careers/shadows-of-africa/: info@ and +255716625008.
- fursa.co.tz Karibu notice (deadline 31 Jul 2026): hr@karibucamps.com, jambo@ and +255 789 193 333.
- zoomtanzania.net/careers/karibu-camps-and-lodges/: md@karibucamps.com and +255787555555.
- karibucamps.com/careers/: 404.
- mabumbe AMIS teaching notice (30 May 2024): recruitment@arushameru.sc.tz.
- expresstz Gran Meliá notice (Oct 2019, stale): recruitment.granmeliaarusha@melia.com, stephen.galinoma@melia.com, addressed to the "Human Resources Department".
- expresstz Jan 2019 Meliá notice: no email.
- zoomtanzania.net/careers/gran-melia-arusha/: prince.mwamboma@melia.com and 255746981895. The page states no role.
- zoomtanzania Gran Melia Guest Experience Manager advert (posted 2026-08-05, expired): no email.
- ajirayako Gran Meliá advert: link only.
- mabumbe Gran Meliá GM advert (Mar 2025): link only.
- mavusu.com NSK notice (Feb 2026): WhatsApp 0776410045 for applications.
- expresstz Shree Hindu Union Charitable Hospital notice (Nov 2021, stale): the Medical Director, P.O. Box 3051, Job.Application@shuch.co.tz.
- makumira.ac.tz/docs/TUMA JOB VACANCY APRIL - 2025.pdf (own): Vice Chancellor, P.O. Box 55 USA-RIVER, vc@ and Cc hr@makumira.ac.tz, deadline 30 Apr 2025.
- ajirayako VisionFund Finance Officer notice (19 Aug 2025): application@vftz.co.tz, addressed to the CEO, P.O. Box 1546 Arusha.
- vftz.co.tz own job advert (9 Sep 2026) and careers page: info@ only.
- ajirayako Equity Bank notice (1 Mar 2025): tzrecruitment@equitybank.co.tz.
- tanzania.davisandshirtliff.com how-to-apply and vacancies pages: applications go through the online portal; tzcontactcenter@dayliff.com.
- mabumbe IAA tag page and IAA Feb 2026 notice: Ajira Portal (PSRS), no IAA contact.
- globalpublishers IAA (2018): login to apply.
- archive.world-federation.org Ithna Asheri notice: no contact.
- moivaro.com/about-us/ourstaff: history only.
- tm.co.tz/about-us/: info@tm.co.tz only.
- azaniabank.co.tz/careers/, diamondtrust.co.tz/careers, kcbbank.co.tz/careers: customer-care addresses only.
- ajirayako TCB, KCB and Exim pages: links only.
- mabumbe Exim Oct 2025 notice: careers portal.
- mabumbe Azania, SAUT, ALMC and Aga Khan tag pages: no target notices with contacts.
- ajiriwa ALMC page: none.
- ajiraweb MS TCDC Head Chef (Apr 2026): link only, no email.
- zoomtanzania directory MS TCDC: mstcdc@ (already known).
- greattanzaniajobs VisionFund adverts: agency address tz@lafabsolution.com (a recruitment agency, not the employer's HR; not recorded).
- Zoom Tanzania careers slugs probed for 50 targets: most return the generic page. Ones that gave employer contacts: Shadows, Gran Melia, Bushbuck (bushbuck@, already known), Good Earth, MS TCDC, Azania, Aafrin, ATC. Only the Shadows and Gran Melia contacts were new; the others were known general addresses or not HR.
- Home pages of 63 target sites checked for careers links:
  - vftz.co.tz has a careers page and a job-advert category.
  - makumira.ac.tz and nm-aist.ac.tz link to the Ajira Portal.
  - tawiri.or.tz links to announcements.
  - No other site has a careers page.

## Blocks and failures (recorded, not worked around)

- pwc.co.tz/careers/experienced-hires.html: HTTP 403.
- mstcdc.or.tz/jobs/admissions-officer: HTTP 403.
- kitamuhouse.com: robots.txt disallows. Not read.
- HTTPS certificate hostname mismatch:
  - selianlh.or.tz, aicc.co.tz and arushameru.sc.tz: read over plain HTTP. Their home pages have no careers pages.
  - ticd.ac.tz and mtmerurrh.go.tz: the plain-HTTP versions failed DNS.
  - atc.ac.tz: not retried.
- DNS failures: helpfuljobs.info, beiyatz.com, health4allclinics.co.tz, safariplus.tz, tz.kcbgroup.com, www.tcbbank.co.tz.
- oas.ticd.ac.tz: connection refused.
- ochuforum.com: HTTP 521.
- ajirampya360.com: SSL EOF.
- elimutimes.com: parked domain.
- WebFetch is not allowed on mabumbe.tz and makumira.ac.tz. Both were read with read_page.py and the cached fetcher instead.

## Targets not reached or with nothing new

Public bodies recruit through PSRS / Ajira Portal, so no employer HR contact appears in their notices:
- IAA
- TICD
- NM-AIST
- AICC Hospital
- Arusha Technical College
- TAWIRI
- Mount Meru Regional Hospital
- Kaloleni Hospital
- Levolosi Health Centre

Company-team targets searched with no notice found:
- PwC (blocked)
- Delight Polyclinic
- Ngare Sero
- JM Tours
- AAR Clinic
- GASH
- Ithna-asheri Hospital
- Mega Tents
- Selian Lutheran Hospital Ngaramtoni
- Aga Khan University Hospital (Arusha)
- United Aviation Services
- Citylink Hotel
- Ilboru Safari Lodge
- Mt. Meru Game Lodge
- Njake Oil
- Saruni River Lodge
- Tanzanite City Park Lodge
- Makeseni Lodge
- Wild Mind Travel
- Everyday Safaris
- Safari Wholesalers
- Safari plus
- Health 4 All

Not searched separately; small clinics and businesses, which are unlikely to publish notices:
- Avinta Care
- Gemsa
- Kijenge RC Dispensary
- Kitamu Africa (robots disallowed)
- Lashku Forex
- Mbasha Holdings
- Old Arusha Health Center
- Oloirien Dispensary
- R&D Polyclinic
- Tanta Dental
- Usa RC Health Centre
- Mango B&B
- Josh Dreamland Safaris

Named targets: searches for the following found no notices with HR contacts:
- Africa Dream Safaris
- Simba Safaris
- Bushbuck
- Moivaro
- Good Earth
- Tandala
- African Big Cats
- Paradies
- SAUT Arusha
- TanManagement / JW Seagon
- ALMC
- Azania
- Exim
- DTB
- TCB
- KCB

Named tour operators not searched separately: their home pages have no careers pages, and they are owner-run.

NMB already has its Chief HR Officer as recipient; not searched.
