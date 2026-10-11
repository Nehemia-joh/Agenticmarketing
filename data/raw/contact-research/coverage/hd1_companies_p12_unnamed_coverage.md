# Coverage log: hd1_companies_p12_unnamed (high-direct wave 1, slice S2)

- Date: 11 October 2026
- Slice: `runtime/contacts/slices/hd1_companies_p12_unnamed.json` (79 organisations, P1 and P2, nearest first; all needed a named decision-maker and an own work email)
- Output: `data/raw/contact-research/search_hd1_companies_p12_unnamed_2026-10-11.jsonl` (79 lines, one per organisation)
- Search allowance: 58. **Used: 29.** No search was refused by the session cap. The other 29 were left unused on purpose. Up to six earlier waves had already searched this pool; their queries were checked in the earlier coverage logs and not repeated. After the first 20 queries the yield for small operators and hotels was close to nil, so the rest goes back to the coordinator.

## Method

1. Read the earlier research records and coverage logs for every slice organisation, so no query was repeated.
2. Read, offline, the own-site pages that the 11 October deep crawl cached for every organisation (`runtime/contacts/http-cache/`), looking for names with roles and own-domain addresses. This used no network.
3. Fetched the own pages the crawl had not mined (team, history, legal notice, leadership, media and about pages) and the allowed directories (ATE, TATO, SafariBookings operator text). Fetches to one site were spaced, and robots.txt was respected. No robots-disallowed site was opened; Kitamu's site stays with the earlier browser pass.
4. Searched only where that gave nothing, one organisation per query, in the allowed forms. Searches with `site:` returned no own-domain results (Q1), so later own-domain searches used the search tool's domain filter instead. No person's name was searched.

## Queries

| # | Organisation | Query | Outcome |
|---|---|---|---|
| Q1/58 | Karibu Camps | `site:karibucamps.com "managing director" OR founder OR owner OR "general manager"` | No own-domain result (the engine ignored site:). Nothing. |
| Q2/58 | Everyday Safaris | `"Everyday Safaris" "@everydaysafaris.com"` | FindGlocal and unrelated SafariBookings pages. Nothing. |
| Q3/58 | Arusha Hotel (Four Points) | `"Four Points by Sheraton Arusha" "general manager"` | Only the 2017 opening release names a GM; stale, not recorded. |
| Q4/58 | Mount Meru Hotel | `"Mount Meru Hotel" "@mountmeruhotel.co.tz"` | Venue listings with obfuscated mail. Nothing. |
| Q5/58 | East African Legislative Assembly | `EALA "Clerk of the Assembly" 2026 (allowed_domains eala.org)` | Clerk named only on an old page (stale); April 2026 sitting page fetched: no Clerk named. Nothing recorded for the Clerk. |
| Q6/58 | Pan African Postal Union | `"Pan African Postal Union" "Secretary General" 2026 Arusha` | Snippet: Assistant SG re-elected 27 Mar 2026 (UCC, Uganda regulator); UCC page refused connection; upap-papu.africa redirects to an unrelated site. SG for the new term not found. |
| Q7/58 | Leopard Tours | `"Leopard Tours" Arusha vacancy OR "send your application" OR "human resources"` | SafariBookings operator profile (fetched): 250+ staff, founded 1985, Kijenge address, no names. |
| Q8/58 | Sunflag Tanzania | `"Sunflag Tanzania" "@sunflag-tz.com"` | Same 2019 notice as before (ajay@, mussa@ without holders). Nothing new. |
| Q9/58 | Shree Hindu Hospital | `"Shree Hindu Union Charitable Hospital" Arusha` | Only the 2021 Mabumbe notices (Medical Director, unnamed). Nothing new. |
| Q10/58 | Institute of Accountancy Arusha | `Institute of Accountancy Arusha Rector email rector@iaa.ac.tz (allowed_domains iaa.ac.tz)` | Snippet: ManagementTeam page lists Prof. Eliamani Mathew Sedoyeka as Rector; iaa.ac.tz fails TLS (block) for every fetch. No rector@ inbox found. |
| Q11/58 | Selian Lutheran Hospital | `"Selian Lutheran Hospital" Arusha "medical director" OR "executive director" OR "hospital director"` | Global Health Ministries (partner) interview fetched: Dr. Amon Marti, Director of the hospital. Recorded. |
| Q12/58 | Kiure Engineering | `"Kiure Engineering" Arusha "managing director" OR "general manager" OR "send your application"` | Snippet: CEO Roundtable member directory names Omar Jumaam Kiure as Managing Director and founder; member page 404 / site in maintenance. Recorded fetched:false. |
| Q13/58 | LGT Logistics | `"LGT Logistics" Arusha "managing director" OR director OR founder` | Only the unrelated Nordic LGT Logistics. Nothing. |
| Q14/58 | Tulia Retreat Hotel | `"Tulia" hotel Arusha "general manager" OR "managing director" OR "human resources"` | Aggregators and listings only. Nothing. |
| Q15/58 | The Charity Hotel | `"Charity Hotel" Arusha vacancy OR "send your application" OR "general manager"` | Nothing for the Charity Hotel. (Surfaced a 2018 Four Points notice with careers@fourpointsthearushahotel.com.) |
| Q16/58 | Hotel Equator | `"Hotel Equator" Arusha Boma Road` | Booking listings only; no new site (equator-hotel.com now serves only a /lander page). |
| Q17/58 | Gupta Auto Spares | `"Gupta Auto Spares" Arusha "managing director" OR "branch manager" OR director` | Unrelated Indian director profiles. Nothing. |
| Q18/58 | Vodacom Service Center | `"Vodacom Tanzania" annual report 2026 OR 2025 "Managing Director" filetype:pdf` | Own Annual Integrated Report 2025 (vodacom.co.tz PDF, fetched): MD Philip Besiimire; HR Director Vivienne Penessis. Recorded as national escalation. |
| Q19/58 | Jumla Africa, Arusha Branch | `"Jumla Africa" Tanzania founder OR CEO OR "managing director"` | Only a different company (JumlaJumla). Nothing. (Own site jumlaafrica.com fetched separately: HQ, phone, inbox.) |
| Q20/58 | Shoppers | `"Shoppers Supermarket" Tanzania "managing director" OR "general manager" OR "human resources"` | Court record and aggregators only. Nothing. |
| Q21/58 | Palace Hotel | `"Palace Hotel" Arusha "@palacehotelarusha.com"` | Booking listings only. Nothing. |
| Q22/58 | Avinta Care Specialized Polyclinic | `"Avinta Care" Arusha "Kilimanjaro Fertility Institute"` | A news story only (news is not a source for people). Nothing recorded. |
| Q23/58 | East African Legislative Assembly | `EALA "Clerk to the Assembly" OR "Clerk of the Assembly" 2026 (allowed_domains eac.int, eala.org)` | Only the 2009 Clerk appointment and an old administration page. No current Clerk. Nothing recorded. |
| Q24/58 | Safari plus ltd | `"Safari Plus" "@safariplus.co.tz"` | Wikipedia and CB Insights: Dar es Salaam air-charter operator. Nothing. |
| Q25/58 | Tropical Trails | `"Tropical Trails" Arusha Kilimanjaro founder OR owner OR "managing director"` | SafariBookings operator profile and full profile (fetched): 50-100 staff, founded 1995, P.O. Box 223, phone +255 713 172099; no names. Recorded the phone. |
| Q26/58 | Mega Tents | `"Al-Anver Outfitters" OR "Alanver Outfitters" Arusha director OR owner OR "managing director"` | Unrelated operators. Nothing. (Own site, now readable again, fetched separately.) |
| Q27/58 | Mazingira Technologies | `"Mazingira Technologies" Arusha "managing director" OR founder OR CEO` | EcoHub directory profile without names. Nothing. |
| Q28/58 | Seven-up Bottling Company | `"SBC Tanzania" Arusha plant vacancy OR "send your application" OR "plant manager"` | SBC's own vacancy notice (Ajiriwa, closing 25 Aug 2026, fetched): HR inbox sbc-recruitment@sbc.co.tz. Recorded. |
| Q29/58 | New Safari Hotel | `"New Safari Hotel" Arusha "general manager" OR "managing director" OR owner` | Kayak listings and other hotels' appointments. Nothing. |

## Leads found (fetched unless stated)

- **African Court on Human and Peoples' Rights:** Dr. Robert Eno, Registrar. His own address, Robert.Eno@african-court.org, is in the contact block of the Court's press release of 1 October 2026 (`email_link: same block`). The Office of the Registrar page gives the role inbox registrar@african-court.org. Also the Deputy Registrar, Mrs Grace Wakio Kakai. **A high-direct candidate.**
- **Serengeti Big Cats Safaris:** Cécile Parisio, who runs the agency ("responsable d'agence", with the title Directrice Marketing). The agency page gives marketing@serengeti-big-cats-safaris.com as her contact (`same block`), and the legal notice gives her full name. It is a function mailbox, so it may export as indirect. Also Freddy, Directeur des Opérations (one name only).
- **Bushtops Safari Camps:** Claudia Stuart, founder, named on the own site. claudia.stuart@bushtops.com is the company email on its TATO listing (`directory entry`; undated, no role field). She is a group-level founder, so this is an escalation route. The reviewer decides whether the directory link qualifies.
- **Raha Beverages:** Adolf R. Olomi, Managing Director; Alphoncina A. Olomi, Deputy MD; Irene Adolf, HR and Admin Assistant (own About page; no emails).
- **Spiritan Missionary Seminary:** Fr. Dr Colman Kimaryo CSSp., Rector; Rev. Fr. Dr. Karol Ludovick CSSp, Dean Academics (own home page).
- **Maasai Wanderings:** Donna Duggan, the co-founder who leads the company (own history page).
- **Onsea House:** Axel Janssens, manager of Onsea House Tanzania Ltd. This corrects the earlier spelling "Janssels".
- **Selian Lutheran Hospital:** Dr. Amon Marti, Director. The source is a partner page (Global Health Ministries) that shows no year for the post.
- **SBC Tanzania (Seven-up):**
  - CEO Himanshu Shekhar (appointed September 2026) and Executive Director Ziad El Khalil, from the own media page. Both are national, so escalation contacts.
  - The HR recruitment inbox sbc-recruitment@sbc.co.tz, from SBC's own vacancy notice (August 2026).
- **GA Insurance Tanzania:** CEO Jose Verghese and COO Amitava Biswas, from the own senior-management page. Both are escalation contacts; no Arusha branch manager is published.
- **Vodacom (service centre):** MD Philip Besiimire and HR Director Vivienne Penessis, from the own Annual Integrated Report 2025. Both are national escalation contacts.
- **CORTO Safaris:** Lilou (Directrice Générale), Marie (deputy), the founders Gérard and Hellen, and Aggrey (head of administration). First names only.
- **Rivertrees Country Inn:** Les and Caroline, the current operators (first names only).
- **Kiure Engineering:** Omar Jumaam Kiure as Managing Director and founder. This comes only from a CEO Roundtable directory snippet (`fetched: false`); the member page now answers 404.
- **Pan African Postal Union:** the Assistant Secretary General, Jessica Hope Ssengooba, re-elected on 27 March 2026 (snippet only). The Secretary General for the new term was not found.
- **East African Legislative Assembly:** the Speaker is recorded. The Clerk (the administrative head) is named only on stale pages, so no Clerk is recorded.
- **IAA:** the Rector is re-confirmed, from a snippet only (the site is blocked).
- **New routes or corrections, without a person:**
  - Mega Tents: the site is readable again, with a new address and number.
  - LGT Logistics: the md@ role inbox (from ATE) and the contact page's phones.
  - Tropical Trails: +255 713 172099 and P.O. Box 223.
  - Leopard Tours: address, landline and a staff band of 250+.
  - Jumla Africa: the live site is jumlaafrica.com, with its head office at Tengeru.
  - Venice Hotel: venicehoteltz.com.
  - Asante Rabi: three office lines.
  - Naaz: two mobiles.
  - Green Mountain: looks to share management with Greenside.
  - Four Points Arusha: a 2018 careers inbox (snippet only, stale).

No address was constructed from a pattern. Some mailboxes carry a name, but no page says whose they are: Mega Tents murtaza@ and nis@, Suricata erick@, and Sunflag ajay@ and mussa@. They are recorded as mailboxes only, with no person.

## Blocked or unusable sites

- **iaa.ac.tz (all hosts):** TLS error "unable to verify the first certificate". Not worked around.
- **tuliahotelandspa.com:** "Bot Verification" page. Not passed.
- **ksijhealthcare.or.tz (Ithna-asheri):** HTTP 403.
- **dikdik.ch:** connection reset (ECONNRESET) on 11 October. The crawler's cache of 10 October was used for routes only.
- **lushgardenhotels.co.tz:** TLS hostname mismatch, from the crawl; not retried.
- **artisan.co.tz:** HTTP 403 and a self-signed certificate, from earlier waves; not retried.
- **leopard-tours.com, marriott.com:** HTTP 403 to the crawler; not retried.
- **ucc.co.ug:** connection refused. The snippet was used, with fetched false.
- **ceo-roundtable.co.tz:** member page 404 and the site in maintenance. The snippet was used, with fetched false.
- **upap-papu.africa:** redirects to an unrelated site (catholichomeandgarden.com), so it is treated as no longer PAPU's.
- **equator-hotel.com:** an empty page whose sitemap lists only /lander (the parked-domain pattern). Nothing was used from it.
- **shuch.co.tz:** a bare server directory listing, no site.
- **tropicaltrails.com:** robots.txt unreadable (server error). The site was read anyway, as the rules allow.

## Organisations not reached

None; all 79 have a line. 30 of them got no new fetch or search beyond the crawl cache and the earlier records, either because earlier waves had already searched them or because they have no website; their `notes` say so.

These are the most worth a later browser or phone pass:
- Karibu Camps: md@ and hr@ are held, but the MD is unnamed.
- Kibo Palace Hotel, Mount Meru Hotel and Gold Crest Hotel.
- Leopard Tours: 250+ staff.
- Shree Hindu Union Charitable Hospital.
- Ithna-asheri (403), Tulia (bot check) and IAA (TLS).

## Notes for the coordinator

- **Possible high-direct gains from this slice:**
  - African Court: the Registrar's own address (strong).
  - Serengeti Big Cats: the agency head, with a function mailbox tied to her.
  - Bushtops: the founder's name mailbox, from a directory; an escalation route.

  The rest move at most from medium to high-indirect (a named decision-maker with a general inbox).
- **Segment checks repeated from earlier waves:** these are not tour operators: Safari Plus (Dar es Salaam air charter), Safari Wholesalers, United Aviation Services, Lashku Forex, Mega Tents, Mbasha, Gupta Auto Spares, Delight Polyclinic, Beautiful African Gemstones, Vehicle Pharmacy, Artisan, Marangu Forex, OKKA House and Rudra.
