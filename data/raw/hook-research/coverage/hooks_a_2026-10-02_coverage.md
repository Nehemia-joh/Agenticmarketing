# hooks_a coverage, 2026-10-02

Output: data/raw/hook-research/hooks_a_2026-10-02.jsonl (26 lines, one per organisation).

## Queries (WebSearch)

None used (0 of 5). Every fact came from the organisations' own pages, each contact's source_url, and one Wikipedia page. No query was routed through WebFetch or a browser.

## Pages read (all with scripts/contacts/read_page.py; robots.txt allowed every page read)

Each organisation: the contact source_url(s) plus the lead's website home page.

0. Nelson Mandela African Institution of Science and Technology: en.wikipedia.org/wiki/Nelson_Mandela_African_Institution_of_Science_and_Technology; also nm-aist.ac.tz (home; no Vice-Chancellor shown); nm-aist.ac.tz/about-us returned 404.
1. Absolute Wilderness: absolutewilderness.com/about; absolutewilderness.com.
2. African Big Cats Safaris: africanbigcatssafaris.com/company-profile/; africanbigcatssafaris.com (blank text, JavaScript).
3. Allen Tanzania Safaris: allentanzaniasafaris.com/about-us/; allentanzaniasafaris.com.
4. Beyond Experience: beyondexperience-tz.com/about-us; beyondexperience-tz.com.
5. Bright African Safaris: both pages BLOCKED (403).
6. Conservation Caravan Safaris: conservationcaravansafaris.com/about-us; conservationcaravansafaris.com.
7. Everyday Safaris: everydaysafaris.com/about-us/; everydaysafaris.com; everydaysafaris.com/our-guides-team/ (also tried /guides-and-team/, 404).
8. Go Expeditions Africa: goexpeditionsafrica.com.
9. Hazzes Adventure: hazzesadventure.com/about-us/; hazzesadventure.com.
10. Jackpot Safaris: jackpotsafaris.co.tz.
11. Joash Africa (JAfrica): jafricasafari.com/about/; jafricasafari.com.
12. Kiliclimb Africa Safaris: kiliclimbafricasafaris.com/meet-the-kiliclimb-africa-safaris-team/; kiliclimbafricasafaris.com.
13. Kilimanjaro Unforgettable: kilimanjarounforgettable.com/our-team/; kilimanjarounforgettable.com.
14. Lazy Lion Safaris: lazylionsafaris.com/over-ons/; lazylionsafaris.com.
15. Maasai Wanderings: maasaiwanderings.com/our-team/; maasaiwanderings.com.
16. Mind & Soul Travel: mindsoultravel.co.tz.
17. Northland Safaris: northlandsafaris.com/meet-our-team/; northlandsafaris.com.
18. Pure Afro Travels: pure-afro.com/about-us/; pure-afro.com.
19. Safari Tanzania: safari-tz.com/about (the contact's source); safaritanzania.com.
20. Samora Explorers: samoraexplorers.com/company-history/; samoraexplorers.com.
21. Serengeti Pride Safaris: serengetipridesafaris.com/about; serengetipridesafaris.com.
22. Tanzania Choice Safaris: tanzaniachoicesafaris.com.
23. Topguides: topguidessafaris.com/our-team/; topguidessafaris.com.
24. Volunteers Africa Heart's Desire: africaheartsdesire.com/uberuns (German); africaheartsdesire.com (redirects to en.africaheartsdesire.com).
25. Wildlife Explorer E.A.: explorertravelco.com/our-story; wildlife-explorer.com (redirects to explorertravelco.com).

## Blocked or unreadable sources

- Bright African Safaris: brightafricansafaris.com/about-us/bright-tanzania-safari-guides/ and www.brightafricansafaris.com both returned HTTP 403. Not worked around. Contact role = unreachable; status = blocked.
- Several pages were JavaScript-rendered or partly blank (African Big Cats home, Absolute Wilderness labels); only text actually shown was used.
- robots.txt could be read for every site read.

## Role checks

36 contact records: 33 confirmed, 2 not_found, 1 unreachable, 0 changed.
- not_found: Pamela Stephen Lyamuya (Everyday Safaris; the about page and the team page are readable but name no director), Donna Duggan (Maasai Wanderings; the team page lists no named people).
- unreachable: Msangi Charema (Bright African Safaris; 403).
- Weaker confirmations (see notes in the jsonl): Andry Wolfgang (page says he introduced the brand; no "founder"), Iddy Kimaro (page says he launched the company; no "Director"), Psteen (listed as Manager; founders section also names him), Nelson Mandela AIST (Wikipedia only).

## Organisations without a hook, and why

- Beyond Experience: no staff, welfare or community fact on the pages read.
- Bright African Safaris: blocked.
- Conservation Caravan Safaris: no staff fact; award claims look copied from another operator (flagged, not used).
- Joash Africa Wilderness Insight: no staff, welfare or community fact.
- Kilimanjaro Unforgettable: only "years of experience", too vague.
- Mind & Soul Travel: no supporting fact on the page.
- Safari Tanzania: contact page is for the safari-tz.com brand, the lead website is safaritanzania.com; identity unclear.
- Samora Explorers: no staff, welfare or community fact.
- Tanzania Choice Safaris: no staff, welfare or community fact.
- Topguides Africa: no usable fact.
- Wildlife Explorer E.A.: site now redirects to Explorer Travel Co; unclear which entity employs the Arusha staff.

## Hooks written: 15 (strong 3, moderate 12)

Nelson Mandela AIST, Absolute Wilderness, African Big Cats, Allen Tanzania, Everyday Safaris (strong), Go Expeditions, Hazzes Adventure, Jackpot, Kiliclimb (strong), Lazy Lion, Maasai Wanderings, Northland, Pure Afro (strong), Serengeti Pride, Volunteers Africa Heart's Desire.

## Not finished

None; all 26 organisations have a line.

## Items for a person to check

- Safari Tanzania: safaritanzania.com vs safari-tz.com.
- Wildlife Explorer E.A.: redirect to Explorer Travel Co.
- Conservation Caravan Safaris: award claims.
- Serengeti Pride Safaris: placeholder-looking Arusha address.
- Lazy Lion Safaris: Dutch-language page.
- NM-AIST: Vice-Chancellor and staff counts from Wikipedia only.
