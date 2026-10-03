# Wave 12, groups and head offices: coverage log (2026-10-02)

Brief: `runtime/contacts/prompts/wave12_groups.md`. Targets: `runtime/contacts/slices/wave12_groups_targets.json` (134 hotels, lodges, camps and banks). Output: `data/raw/contact-research/search_wave12_groups_2026-10-02.jsonl` (29 records). Pages were read with `scripts/contacts/read_page.py` and with scratch helpers under `runtime/contacts/agents/wave12_groups/` that use the same cached, spaced, robots-honouring fetcher. The helpers list a page's links, read PDFs, and show addresses that a site hides behind an anti-spam script (Joomla cloak, Cloudflare address protection) as a browser would show them. WebFetch was refused for eximbank.co.tz and was not used anywhere else.

The session restarted once mid-run. The searches below are counted across both parts: 22 of 40 used.

## Searches (allowance 40; 22 used)

| # | Query | Outcome |
|---|---|---|
| Q1/40 | NBC Bank Tanzania executive committee "Human Resources" director | Only LinkedIn, Datanyze, theorg, theofficialboard: not sources. Nothing used. |
| Q2/40 | site:nbc.co.tz management team managing director | nbc.co.tz Talk to us, news and annual-report pages, all read: MD office phones and MD name. |
| Q3/40 | Exim Bank Tanzania management "Human Resources" "Chief" site:eximbank.co.tz | Snippet of an old Exim news page naming the Head of HR. The page now returns 404, so the person is recorded fetched: false. |
| Q4/40 | Absa Bank Tanzania "Head of People" OR "Human Resources Director" absa.co.tz | Only ZoomInfo and D&B: not sources. Nothing used. |
| Q5/40 | "Gran Meliá Arusha" "General Manager" OR "Human Resources Manager" | Vacancy notices (ajirayako, zoomtanzania) read: roles only, no names. LinkedIn ignored. No record. |
| Q6/40 | "Four Points by Sheraton Arusha" "The Arusha Hotel" "General Manager" vacancy OR announcement | Aggregators only; the one vacancy page (unistoretz) returns 404. No record. |
| Q7/40 | NMB Bank Plc annual report 2025 "Chief Human Resources Officer" | Snippet of NMB's own 2025 integrated annual report naming the CHRO. The PDF is over the fetcher's 2 MB limit, so the person is recorded fetched: false. |
| Q8/40 | Equity Bank Tanzania Limited management team "Human Resources" OR "People" director equitybank.co.tz | Only news (khusoko), Wikipedia and D&B. The MD is already on file. No record. |
| Q9/40 | "Planet Lodges" Arusha "Airport Planet Lodge" director OR "general manager" OR owner | The summary named the GM of Arusha Planet Lodge. planet-lodges.com answers 403 on every page, so the person is recorded fetched: false, identity uncertain. RocketReach, Instagram and TripAdvisor ignored. |
| Q10/40 | "Gold Crest Hotel" Arusha Mwanza group "general manager" OR "human resources" vacancy | Names only on ZoomInfo (not used). The group contact page was read: office in Mwanza. tanzajob recruiter page 403. |
| Q11/40 | "Ngurdoto Mountain Lodge" Arusha owner company "general manager" OR "managing director" | Names only on ZoomInfo and TripAdvisor (not used). The lodge's former domain has expired. |
| Q12/40 | Elewana Collection Tanzania "Human Resources" manager vacancy Arusha | Elewana's own 2020 GM announcement, and the lodge's February 2026 vacancy notice on fursa.co.tz giving the GM office inbox. Both read. |
| Q13/40 | Ecobank Tanzania "Managing Director" "Head of Human Resources" ecobank.com | The summary named the MD and an HR head, but the HR name came from LinkedIn and ecobank.com answers 302, so nothing was confirmed. The ajirayako Head-HR vacancy (January 2025) gives only the job board's own gmail. No record. |
| Q14/40 | "NCBA Bank Tanzania" "Managing Director" appointed site:ncbagroup.com | Two NCBA Group news items (May and June 2023) read: MD & CEO named. |
| Q15/40 | Meliá "Cluster General Manager" Arusha Zanzibar appointed | World Travel Awards and LinkedIn only; the mabumbe GM vacancy (March 2025) was read and names no one. No record. |
| Q16/40 | "Four Points" "Arusha Hotel" vacancy 2026 OR 2025 "human resources" apply email | Aggregators only. No record. |
| Q17/40 | "Mount Meru Game Lodge" Usa River owner OR "general manager" OR "managed by" | The lodge's own History page and its WETU brochure text, both read: partners and on-site managers. |
| Q18/40 | "Saruni River Lodge" Arusha OR Tanzania | Booking sites and Facebook only. No record. |
| Q19/40 | "Lush Garden" hotel Arusha group "Business Hotel" management OR director OR "general manager" | Booking sites only. lushgardenhotels.co.tz fails TLS (hostname mismatch). No record. |
| Q20/40 | "Impala Hotel" Arusha "Ngurdoto Mountain Lodge" "Naura Springs" group hotels | News (The Citizen, Tanzania Times) read, used only for a closure warning. LinkedIn, Wikipedia and Grokipedia ignored. |
| Q21/40 | "Akiba Commercial Bank" 2025 OR 2026 merger OR "managing director" | The bank's own Senior Management page, read: acting MD and Head of HR. theofficialboard, Crunchbase and Datanyze ignored. |
| Q22/40 | "Tanzanite City Park Lodge" Arusha | No page about this lodge. No record. |

The search cap was never reached. Searching stopped at 22 because the remaining targets are mostly independent hotels with no group and no own website, where searches had stopped producing allowed sources.

## Pages read and what they gave

- **Banks**
  - crdbbank.co.tz Our Leadership: Group CEO & MD, Director of Human Resources. No search needed.
  - nbc.co.tz
    - Home and About are built by script and gave nothing.
    - Talk to us: MD office phones; head office Sokoine Drive, Dar es Salaam.
    - News and events: MD named (2022 items).
    - Four guessed leadership URLs returned 404. Annual-report PDFs under /content/dam/ are disallowed by robots.txt and were not read.
  - nmbbank.co.tz: home 200; both management-team URLs 403; 2025 annual-report PDF cut off at 2 MB.
  - kcbbank.co.tz Executive Management (linked from ke.kcbgroup.com): MD, Head of Human Resources. tz.kcbgroup.com does not resolve (DNS); no contact page found (/contact-us 404).
  - eximbank.co.tz: About has a script-built management tab; Contact gave no details; the old news URL returns 404.
  - azaniabank.co.tz Management Team: MD (already on file) and directors, but no HR head. No new record.
  - absa.co.tz About and News: no names. Report PDFs under /content/dam/ are disallowed by robots.txt. No record.
  - amanabank.co.tz: About has no names; Contact Information gives the head office (Golden Jubilee Tower, Dar es Salaam).
  - vftz.co.tz: About gives the CEO and the Head of People & Culture & Administration; Contact gives the head office at AICC, Arusha.
  - acbbank.co.tz
    - Home page carries injected links to an unrelated shop catalogue (flagged as hijacked content).
    - Senior Management page: acting MD, Head of HR, head office Ohio Street, Dar es Salaam.
  - ncbagroup.com
    - The Tanzania team page is built by script and could not be read.
    - Two Tanzania news items (2023) name the MD & CEO.
  - equitygroupholdings.com/tz is empty (script-built); equitybank.co.tz timed out. No record.
  - ecobank.com/tz returned a redirect (302). No record.
- **Lodge, camp and hotel groups**
  - Elewana (elewanacollection.com):
    - Our Contacts: named group contacts with emails; Tanzania switchboard.
    - Careers: no HR contact.
    - February 2020 newsletter: GM appointment at Arusha Coffee Lodge.
    - fursa.co.tz vacancy notice (February 2026): GM office inbox.
  - moivaro.com: Our Staff lists camp staff only; Contact gives the head office (Moivaro Road, Arusha).
  - lemalacamps.com: Our People and Our Story name no one; Contact gives P.O. Box 14529, Arusha.
  - bushtopscamps.com:
    - Human Story: no names.
    - Careers: applications inbox; Serengeti camp manager.
    - Contact: Orion Hotels Limited head office, Mombasa.
  - karibucamps.com: About has no names; Contact gives Njiro, Arusha.
  - mbalimbali.com: Contact gives the head office (Dar es Salaam).
  - angatacamps.com: About has no names; Contact gives the Arusha offices.
  - owc-africa.com Olerai Lodge team page: lodge manager and project manager, first names only.
  - twctanzania.com About (Tanganyika Wilderness Camps): MD; Oljoro Road, Arusha.
  - mt-meru.com: About and Contact name the Baobab Village Co. Ltd managers and director; HQ in Dar es Salaam.
  - kibopalacehotel.com Careers: recruitment inbox and HR office. travelbookgroup.com (home and contact) is a hotel-software firm, not the owner.
  - goldcresthotel.com contact page: group office at PPF Tower, Mwanza. The Arusha site's /contact returns 404.
  - Owner-run operators and lodges:
    - basecamptanzania.com About and Contact: owners; Arusha office.
    - afromaxx.com Impressum: Geschäftsführerin; Moshi.
    - karama-lodge.com Contact: Lodge Manager desk on the lodge's own domain.
    - mountmerugamelodge.co.tz History and the lodge's WETU brochure: partners and on-site managers.
  - Scanned for a group or named manager, nothing found:
    - rivertrees.com and onseahouse.com: family-owned; no individual named.
    - lakedulutilodge.com says it is "not part of a chain".
    - ngare-sero-lodge.co.tz, arumerulodge.com, tuliahotelandspa.com, ilborusafarilodge.net, citylinkhotel.co.tz, theafricantulip.co.tz, kigongoni.net, aishi-machame.com, mrimbapalmhotel.co.tz, arushanaaz.net, natronpalacehotel.com.
- **News, used only for status warnings:** The Citizen (Impala and Naura Springs closures, September 2021; the Ngurdoto headline) and Tanzania Times (Impala renovation).

## Blocked sites

- nmbbank.co.tz management-team pages: HTTP 403.
- planet-lodges.com, every page: HTTP 403.
- tanzajob.com recruiter page: HTTP 403.
- nbc.co.tz and absa.co.tz /content/dam/ PDFs: disallowed by robots.txt.
- eximbank.co.tz: WebFetch refused for the domain. read_page could read the pages, but their management lists are built by script.
- lushgardenhotels.co.tz and www.mountmerugamelodge.co.tz: TLS certificate hostname mismatch. The no-www host of mountmerugamelodge.co.tz reads.
- dikdik.ch: connection reset. equitybank.co.tz and impalahotel.com: connection timed out. beiyatz.com: DNS failure.

## Targets not reached or with nothing new (no record written)

- **Groups searched with nothing usable:**
  - Gran Meliá Arusha: roles only from vacancy notices.
  - ARUSHA HOTEL (Four Points by Sheraton, Marriott).
  - Equity Bank, Absa (Barclays), Ecobank, Azania Bank (no HR head).
  - Saruni River Lodge, Lush Garden Hotel, Lush Garden Business Hotel, Tanzanite City Park Lodge.
- **TCB and DTB:** HR heads already on file; not re-researched.
- **FBME Arusha:** not researched. The bank's Tanzanian licence was revoked in 2017; this is background knowledge, not confirmed on a fetched page in this run, so check whether the record is still live.
- **Not reached:** the remaining independent hotels and guest houses with no website and no evident group. That is about 75 targets, including 7 11 Hotel, AM Hotel, Aquiline, Bay Leaf, Boma Masai Garden, Club Afriko, Davos, Freedom Lodge, GMV Lodge, Golden Rose, Green leaf lodge, Hotel Pallsons, Jevas, Kkikalora Saccos, L'Oasis, La Bella Luna, Le Jacaranda, Makeseni Lodge, Mango Bed & Breakfast, Meru House Inn, Meru View, Monjes, Moon Shine, Mountain Village, Mzunguu's, Nature Tree, New Annex, Njiro Ebenezer, Njiro Legacy, Olasiti, Osim, Pamoja, Rich Hotel, Royal Hotel, Saleka, Serengeti Villa, Snow Crest, Stereo, Sttlers, The East African Hotel, Twiga Lodge and White House.
- **Scanned with no new route or person:** the independent hotels with websites listed under "Pages read" above.
- **Not opened (independent hotels with websites):** A1 Hotel, African View, Ahadi, Amani Villa, Arusha Backpackers, Arusha Centre Tourist Inn, Arusha Crown, Arusha Farm House, Arusha Villa, B-More, Dashir, Fun Retreat, Graceland, Green Mountain, Greenside, Haradali, Hotel Mr. Bodo, Korona Villa, Moyoni, Ndoro, New Safari, New Way, Palace Hotel, Pazuri Inn, Premier Palace, Senator, Silver Palm, The Charity Hotel, Venice and Weru Weru. These were not opened in this run; they are outside this wave's group and head-office scope and remain for the crawler.
