# Coverage log: wave10_master_employers_c (2026-10-02)

Slice: 40 company-master organisations (safari and tour operators, plus Lube Junction and Gupta Auto Spares), nearest first.
Search allowance 38; used 37. No search was refused. All 40 organisations were reached.

## Method

1. Read each organisation's own website with `scripts/contacts/read_page.py` logic (cached, robots.txt honoured, 1.5 s spacing): home page and up to four about, team, contact or story pages, plus guessed `/about`, `/about-us`, `/team`, `/our-team`, `/meet-the-team`, `/our-story` paths. TATO portfolio pages carry no people.
2. One search per organisation where the site named no one (or could not be read), then fetches of the organisation's own pages that the search surfaced.
3. Third-party pages (TripAdvisor, SafariBookings, ZoomInfo, LinkedIn, SignalHire, Safarigo and similar directories) are not sources for people; names that appeared only in search summaries from them were not recorded.

## Searches

| No. | Query | Outcome |
|---|---|---|
| Q1/38 | "Enclose Africa Safaris" Arusha founder OR director OR owner | Own pages already read; only ZoomInfo named a CEO (not permitted). No person. |
| Q2/38 | "Lube Junction" Arusha managing director | TATO and Facebook/directory pages; Dar es Salaam address. No person. |
| Q3/38 | "African Polecat Safaris" Arusha owner | Directory pages only; a managing director's name in the summary had no fetchable permitted source. Not recorded. |
| Q4/38 | "African Safari Travel" Arusha Muriet founder director | Unrelated operators. No person. |
| Q5/38 | "African Trails" Arusha tours car hire managing director | TATO and TripAdvisor only. No person. |
| Q6/38 | "Allday In Africa" Arusha founder OR director | People-search page (SignalHire) only; not permitted. No person. |
| Q7/38 | "Bald Eagle Safaris" Arusha | Surfaced baldeaglesafaris.com/about and /contact (non-www host); read. Founder not named. |
| Q8/38 | "Big Time Adventures" Arusha Nelson founder | Own About page read (only the first name "Nelson", no title). /about-us/ is 404. No person recorded. |
| Q9/38 | "Branded Africa Safaris" Arusha | Directory pages only. No person. |
| Q10/38 | "DaMona Safaris" Arusha founder OR owner | Surfaced damonasafaris.com/about/ (now 404); home page read: signed "Monica Elens & David Meta". Recorded. |
| Q11/38 | "Destination Specialists" Arusha safari founder OR director | Directory profile only. No person. |
| Q12/38 | "Extra Mile International" Arusha managing director | US trucking company of the same name, unrelated. No person. |
| Q13/38 | "Extraordinary Experience" Arusha safari owner | Only TripAdvisor pages of similarly named operators. Identity not established. |
| Q14/38 | "Travel Africa Safari Agency" Arusha | TripAdvisor, Facebook, Safarigo only; own site returns 500. |
| Q15/38 | "Habitat Adventures" Arusha safari founder OR owner | Directory pages only. No person. |
| Q16/38 | "Karibu Camps" Arusha Tanzania owner OR founder OR director | LinkedIn/ZoomInfo names only (not permitted). No person. |
| Q17/38 | "Kibuyu African Safaris" Arusha | Directory pages only. No person. |
| Q18/38 | "Kifaru Expeditions" Arusha | Own contact page and directories. No person. |
| Q19/38 | "Lapwings" Arusha safari lapwings.co.tz | Directory pages only. No person. |
| Q20/38 | "Let's Discover Africa" Tanzania Arusha founder | Directory pages; no founder named. |
| Q21/38 | "Magilani Safaris" Arusha | Surfaced magilani-safaris.com/en/about-us/ ("the staff") but the site answers 403. Blocked. |
| Q22/38 | "Makisala Safaris" Arusha owner OR founder | Own about and contact pages read: no people. Founders' names in the summary came from no permitted source. |
| Q23/38 | "Multichoice Safaris" Arusha | Directory pages only. No person. |
| Q24/38 | "Natural Smile Expeditions" Arusha | Own domain now parked ("may be for sale"). No person. |
| Q25/38 | "PAG Tours & Safaris" Arusha | Own about page read: no people. "Benedict" in a summary only (no fetched source). |
| Q26/38 | "Regal African Safaris" Arusha | Own pages read: no people. |
| Q27/38 | "Ro Scavenger Safaris" Arusha | Own pages read: no people. |
| Q28/38 | "Shilashi" self-drive car hire Arusha owner OR director | Own about page read: no people. |
| Q29/38 | "Six and Seven Tours" Arusha | Directory summary named an owner (not fetched, not permitted); own domain now carries gambling spam. |
| Q30/38 | "Spazio Safari" Arusha | Own site and TripAdvisor. No person. |
| Q31/38 | "Tales of Tanzania Safaris" Arusha | Own pages read: family story, no names. |
| Q32/38 | "Tanganyika Outdoor Safari" Arusha | TripAdvisor, Facebook only; own site returns 500. |
| Q33/38 | "Telly Africa Tours and Safaris" Arusha | Directory pages only. No person. |
| Q34/38 | "Viola Tours" Arusha violatours.com | Directory pages only. No person. |
| Q35/38 | "Vision Safari & Tours" Arusha founder OR owner | No founder named in permitted sources. |
| Q36/38 | "Whistling Travel" Arusha Tanzania | Own pages read: no people. |
| Q37/38 | "Gupta Auto Spares and Hardware" Arusha | Own site read; directories only. Vehicle-parts dealer. |

One allowance search (Q38) was not needed.

## Named decision-makers found (4 organisations, 7 people)

- Experiential Travel Africa: Gumbo Mbelwa Mhandeni, Founder (own About page).
- Off The Beaten Path Safari Ltd: Salim Mrindoko, MD; Rebecca Syring, Director (own Our Team page).
- Tanzania Serengeti Adventure Limited: Jordan and Iris, founders (own Meet Our Team page; first names only).
- DaMona Tanzania Safaris: Monica Elens and David Meta, signatories of the About us text (no titles stated).

No work email or phone is linked to any person by its source.

## Blocks and problems

- magilani-safaris.com: HTTP 403 on home and `/en/about-us/`. Blocked, not worked around.
- travelafricasafariagency.com (Game Drive Travel Africa Safari Agency): HTTP 500 on all attempts.
- tanganyikaoutdoorsafari.com: HTTP 500; robots.txt could not be read.
- www.baldeaglesafaris.com and www.abouttanzania.com: certificate hostname mismatch on the www host (recorded; the non-www hosts have valid certificates and were read instead).
- sixandseventours.com: pages carry gambling spam (hijacked); nothing used.
- naturalsmileexpeditions.com: parked, "domain may be for sale"; nothing used.
- bigtimeadventures.co.tz/about-us/ and damonasafaris.com/about/ (shown by search) return 404 now.

## Other observations

- Lube Junction: lubricants distributor with a Dar es Salaam postal address; location and segment to check.
- Gupta Auto Spares and Hardware Limited: vehicle-parts dealer, not a tour operator; segment to check.
- African Tours and Safaris: the TATO listing reads "African Safari Travel"; the name does not match the unrelated african-tours.com operator.
- Extraordinary Experience Ltd has no website on record; only a gmail address.

## Organisations not reached

None. All 40 were researched; 36 yielded no named decision-maker in a permitted source.
