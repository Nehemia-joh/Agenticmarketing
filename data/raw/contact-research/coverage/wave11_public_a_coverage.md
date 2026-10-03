# Wave 11 public-source coverage, agent A (tourism trade fairs and tourism-board lists), 2 October 2026

Output: `data/raw/contact-research/search_wave11_public_a_2026-10-02.jsonl` (353 organisations: 351 matched to the TATO member directory, plus KARIBU KILIFAIR and TANAPA from the fair's own site and a trade-press report).
Scratch files: `runtime/contacts/agents/wave11_public_a/`.

## Searches (12 of 12 used; none refused)

| No. | Query | Outcome |
|---|---|---|
| Q1/12 | Karibu Kili Fair exhibitors list Tanzania tour operators | Found kilifair-tanzania.com, the 2024 booklet PDF, a "registered exhibitors" PDF link, 10times page |
| Q2/12 | Swahili International Tourism Expo S!TE exhibitor list | Found site.tanzaniatourism.go.tz pages (no exhibitor names published), an issuu catalogue |
| Q3/12 | Tanzania Tourist Board licensed tour operators list contact person | Found the TATO member directory (tatotz.org) and tlto.org, a yumpu copy of an old TTB licensed list |
| Q4/12 | TANAPA registered tour operators concession holders list Tanzania contact | No TANAPA concession list; confirmed TATO directory categories and members-list page |
| Q5/12 | Karibu Fair exhibitors directory Arusha 2025 company contact person email | No new list; same Kilifair pages |
| Q6/12 | Tanzania Tourism Business Directory licensed tour operators Arusha Kilimanjaro members TTLB | Confirmed TATO as the only public member list |
| Q7/12 | Hotel Association of Tanzania members list hotels lodges general manager contact | Found hat-tz.org members page (names only) |
| Q8/12 | Karibu-Kilifair exhibitor profile Arusha company "managing director" ... | Found the 2023 booklet PDF and a KATA press report naming the organiser's directors and a TANAPA officer |
| Q9/12 | Tanzania Tourism Confederation OR TATO members directory managing director email ... | Found TATO board page (tatotz.org/our-team/) |
| Q10/12 | Ministry of Natural Resources and Tourism TTLB list of licensed tour operators 2025 pdf Arusha | No official list found |
| Q11/12 | Zanzibar Association of Tourism Investors ZATI members list ... | zati.or.tz found; member list is behind a login portal |
| Q12/12 | Swahili International Tourism Expo S!TE 2025 exhibitors buyers participating companies list | No exhibitor list published; only category descriptions |

## Directories and lists read

| URL | Entries | Matched to targets |
|---|---|---|
| https://tatotz.org/portfolio-cats/mainland-tour-operators/ (pages 1-9) | 302 | most of the 351 matches (the 15 category listings overlap heavily) |
| https://tatotz.org/portfolio-cats/tour-operators/ (pages 1-8) | 291 | overlaps |
| https://tatotz.org/portfolio-cats/dmc-tour-operators/ | 262 | overlaps |
| https://tatotz.org/portfolio-cats/mountain-trekking-operators/ | 182 | overlaps |
| https://tatotz.org/portfolio-cats/zanzibar-beach-holiday-operators/ | 127 | overlaps |
| https://tatotz.org/portfolio-cats/cultural-experience-operators/ | 87 | overlaps |
| https://tatotz.org/portfolio-cats/affiliate-members/ | 49 | overlaps |
| https://tatotz.org/portfolio-cats/ (mainland-hotels, accommodation-providers, hotels, airlines, automotives, financial-services, ngo, others, hot-air-balloon-operators) | 5 to 9 each | overlaps |
| TATO total (unique listing entries across all categories) | 383 | 351 targets (349 by website/e-mail domain or exact name; 4 flagged identity: uncertain) |
| https://tatotz.org/our-team/ (board of directors) | 10 people | 0 new (all board companies that are targets already had a named person; no e-mails given) |
| https://kilifair-tanzania.com/ (organiser contact block) | 1 | 1 (KARIBU KILIFAIR) |
| https://katakenya.org/east-africas-largest-tourism-expo-returns-to-arusha-this-june/ | 1 article | 2 (KARIBU KILIFAIR directors, TANAPA officer) |
| https://www.tlto.org/members and a member page | 45 members listed by name | 0 (member contacts are not shown on the pages) |
| https://hat-tz.org/hat-members/ | 7 pages of member names | 0 (names only, no contacts; not extracted) |
| https://site.tanzaniatourism.go.tz/page/who-exhibit and /page/buyers | 0 company entries | 0 (S!TE publishes categories and organiser e-mails only) |

Listing routes (general or role e-mails, phones, P.O. boxes, physical locations) were copied exactly as the TATO listing prints them. Of 445 e-mails recorded, 75 records include an address that is personal in style (for example `nnko@nnkosmith.com`); the listing names no person for any of them, so no address was attached to a person and none counts as a direct e-mail for a named person. Five founder/manager names come from the listing's own profile text (Destiny Explorers, Lady Tusk Safaris, Mrembo Safaris, Safari-tz, Afric'Aventure); none has an e-mail or phone.

Matching rule: the target's domain equals the listing's website or e-mail domain, or the company name is identical after removing generic words. Records flagged `identity: uncertain` (domain agrees but the listing name differs): Blue Lotus Travel & Tours Ltd (listing name blank), Gran Melia Arusha (listing is Melia Serengeti lodge on the group domain), Sameer Parts Limited, Zara Tours (listing is Zara Tanzania Adventures). One name-only false match (African Safari Travel to African Tours and Safaris) was removed. Hanspaul Group matches the listing HANSPAUL AUTOMECHS LTD on the hanspaul.co.tz domain and is recorded as confirmed by domain; check it if the group relationship matters.

## Blocked or not readable

- https://10times.com/karibu-kilifair: HTTP 403 (recorded, not worked around).
- https://www.yumpu.com/.../the-list-of-licensed-tourism-operators-as-per-tanzania-tourist-board: HTTP 202 challenge page, no content (old, undated list anyway).
- https://www.tanzaniatourism.go.tz/it/ttb/associations and https://maliasili.go.tz/assets/pdfs/TANGAZOENGLISHVERSION.pdf: connection timed out.
- https://www.kilifair-tanzania.com/app/download/7125578353/Exhibitors+Registered+2022_MASTER.docx.pdf: redirects to the home page; no exhibitor list returned.
- https://kilifair-tanzania.com/exhibitor-list/: page text contains no exhibitors (the list is delivered by e-mail registration, which was not attempted).
- Karibu-Kilifair 2024 booklet PDF (14 MB): only the first 2 MB are kept by the page reader, so the PDF could not be opened. The 2023 booklet was not tried for the same reason.
- https://members.zati.or.tz/: login portal; "Download Members List" not used.
- WebFetch was denied for kilifair-tanzania.com.

## Not reached

- Karibu-Kilifair and S!TE exhibitor names (no public list returned any company names or named representatives).
- TANAPA, NCAA and TAWA licensed or concession-operator lists with contact persons: no such public list found in 12 searches.
- Hotels Association of Tanzania member pages (names only, 7 pages): no contact data to record.
- TLTO member contact tabs (45 members), ZATI members list, TTLB register.
- Targets with no match in any list read: 365 of the 718.
