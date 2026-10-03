# Wave 11 public sources B: tour-operator and hotel associations (2 October 2026)

Output: `data/raw/contact-research/search_wave11_public_b_2026-10-02.jsonl` (22 matched targets). Scratch files: `runtime/contacts/agents/wave11_public_b/`.

## Searches (11 of 12 used; none refused)

| No. | Query | Outcome |
|---|---|---|
| Q1/12 | Kilimanjaro Association of Tour Operators KATO members list | KATO is the Kenya Association of Tour Operators (katokenya.org), not a Tanzanian body: out of scope. |
| Q2/12 | Kilimanjaro Association of Tour Operators Tanzania KIATO member companies directory | No KIATO directory found; results were TATO pages (skipped), tlto.org and tanzaniaoperators.com. |
| Q3/12 | Tanzania Hotels Association THA members list hotels lodges Arusha | Found the Hotel Association of Tanzania (HAT) members directory, hat-tz.org/hat-members/. |
| Q4/12 | Tanzania Society of Travel Agents TASOTA members directory contact | Found tasota.or.tz (member page is a logo grid, no contacts). |
| Q5/12 | Karibu Kili Fair exhibitors list tour operators Arusha | Found kilifair-tanzania.com (exhibitor list PDF, hotel partners page). |
| Q6/12 | Tanzania Local Tour Operators TLTO members list Arusha | Found tlto.org member pages (email and phone per member). |
| Q7/12 | Tanzania Association of Tour Guides and Porters member operators Arusha contact list | Only TATO pages (skipped by brief). |
| Q8/12 | Adventure Travel Trade Association members Tanzania Arusha tour operator member directory | ATTA organisation page found; no contacts published. |
| Q9/12 | Tanzania Tourist Board list of licensed tour operators Arusha pdf phone email | Old TTB search URL is a 404; the rest TATO pages (skipped). |
| Q10/12 | Moshi Kilimanjaro tour operators association members list Kilimanjaro Tourism Association | No Moshi/Kilimanjaro association directory; only TATO pages. |
| Q11/12 | Tanzania Tour Guides Association TAGA OR "Kilimanjaro Guides" association member companies Moshi directory | Found ttgatz.org (does not resolve) and an old TTB associations page (does not resolve). |

Q12 was not used. No search was refused.

## Directories and lists read

| Source | Entries | Matched to targets | Notes |
|---|---|---|---|
| https://www.tlto.org/members (4 index pages, 45 member pages) | 45 | 7 (African Savannah Trekkers, Africanzoom, Eyes of Tanzania, Horn & Horizon, MAGS, Nature's Land, Serengeti Clarity) | Each member page publishes a company email and phone. MAGS also names four directors with roles (no personal emails). Matched by domain agreement. |
| https://kilifair-tanzania.com/hotel-partners | 16 partner hotels, each with a named contact | 6 (Forest Hill, Fun Retreat, Gran Melia Arusha, Moivaro, Planet Lodges, Four Points) | Named contacts with work emails and phones. Forest Hill and Four Points matched by name only, so marked identity: uncertain. |
| https://hat-tz.org/hat-members/ (7 pages, 121 member pages) | 121 | 9 (website and membership only) | Member pages hold a description and website link; no emails, phones or people. Mount Meru Game Lodge marked uncertain (domain differs). |
| https://kilifair-tanzania.com/exhibitor-list (embedded PDF "Exhibitors Registered 2026", 5 pages) | about 550 names with place | 0 recorded | Names and stand numbers only, no contact details, so nothing recorded. |
| https://tasota.or.tz/tasota-members/ | logo grid only | 0 | No names or contacts in text; association's own address only. |
| https://atta.travel/organisation/african-adventure-specialists.html | 1 | 0 | Kenya company; no contact details. |

## Skipped and blocked

- TATO (tatotz.org): skipped as instructed.
- tanzaniaoperators.com: an independent aggregator that republishes TATO data; not an association, official register or company source, so not used.
- KARIBU-KILIFAIR 2022 exhibitor PDF link from the search result redirected to the home page (stale); the 2026 PDF linked from the exhibitor-list page was read instead.
- http://www.tanzaniatouristboard.com/tour_search/ (404), http://www.tanzaniatouristboard.go.tz/associations/ and https://ttgatz.org/ (DNS failures): not reachable, not worked around.
- No 403, 429, CAPTCHA, login wall or bad-certificate block was met. robots.txt was honoured by read_page.py.

## Not reached

- Individual KARIBU-KILIFAIR exhibitors (name-only list) were not looked up.
- No KIATO, Kilimanjaro Guides Association or Tanzania Tour Guides Association member list was found online.
- The TASOTA member logos (no text) were not read.
- Affiliate Members page of HAT (hat-tz.org/affiliate-members/) not read.

## Notes on matches

- Forest Hill Hotel (Of318b17d919b): target has no domain or place; exact-name match only.
- ARUSHA HOTEL / marriott.com (Oa38944eaef1d): probably Four Points by Sheraton Arusha ("The Arusha Hotel"); identity uncertain.
- Airport Planet Lodge (O045dd8c38d30): domain planet-lodges.com agrees, but the listing is the Arusha "Planet Lodges" property.
- Moivaro Coffee Lodge (O9c8b8f0aea8e): domain moivaro.com agrees with the group listing.
- Serengeti Clarity: frank@serengeticlarity.com is a first-name mailbox with no surname or role on the page, so no person recorded.
