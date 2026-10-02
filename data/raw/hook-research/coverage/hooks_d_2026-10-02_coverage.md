# Coverage log: hooks_d, 2026-10-02

25 organisations, all finished. Output: `data/raw/hook-research/hooks_d_2026-10-02.jsonl`.

## Queries (WebSearch, allowance 5)

- Q1/5: "Africa Travel Bureau" Arusha community staff team Tanzania safari (organisation: Africa Travel Bureau Ltd). Pages opened from the results: tatotz.org/portfolio/africa-travel-bureau-ltd/ and safaribookings.com/p883. Neither gave a usable fact.
- Q2 to Q5: not used.

## Pages read, by organisation

Every contact's source_url was re-opened first. Each organisation's home, about, team, community and similar pages were then read with read_page.py (paths that returned 404 are not listed unless they matter).

1. A & N Uniques Safaris: uniquesafaris.com /our-story/, /commitment-to-communities/, /, /about.
2. Africa Travel Bureau: /about/management-team, /. Paths /about, /community, /responsible-tourism, /about/community, /about/our-story, /about/sustainability returned 404. Search Q1 and two third-party pages (above).
3. Ajabu Adventures: /about-us/team/, /about-us, /.
4. Bearfoot Expeditions: /.
5. Breathe Tanzania Safaris: /our-guides/, /about, /about-us, /.
6. Cheli Peacock Safaris: /about/team, /about, /.
7. Ecological Wilderness Adventure: /team (www and bare host), /about, /about-us, /.
8. Get Together Adventures: recorded source /about-us/ returned 404; read /, /about instead.
9. Great Image Expedition: /office-team/, /, /about, /about-us.
10. I Dream of Africa: /about-us, /, /our-story.
11. Joagro Safaris: /, /about, /team, /why-us.
12. Kibo Guides: /about, /; /team, /our-team, /community, /giving-back, /about/team returned 404.
13. Kilimanjaro Heroes: /about-us/, /.
14. Lappet Faced Safaris: BLOCKED (see below).
15. Maape Tanzania Safaris: /about-us, /.
16. Meru Slopes: /team/, /, /about, /community.
17. Nihapa Tours: /about-us/, /, /about.
18. Passionate Guides Tanzania: /about, /.
19. Safari Kings: /about/, /.
20. Safaris-R-Us: /our-team/, /, /about, /about-us.
21. Serengeti Clarity: /about-us/, /.
22. Tanger Safaris: recorded source /our-story returned 404 (also /our-story/, /about, /about-us); home page read.
23. Tanzania Unique Adventures: /ueber-uns/, /.
24. Udaay Safaris: /about-us/, /, /about.
25. Wild Ways Tanzania: BLOCKED (see below).

## Blocked or unreadable sources

- Lappet Faced Safaris (lappetfacedsafaris.com): HTTP 403 on the home page, /about-us/ and every other path tried. Role check recorded as unreachable. Not worked around.
- Wild Ways Tanzania (wildwaystanzania.com): HTTP 403 on the home page and /about-us/; robots.txt could not be read (4xx). Role check recorded as unreachable. Not worked around.
- Tanger Safaris: the recorded source_url returns HTTP 404. The home page names the founders as "Irene & Wilfried" with first names only, so the two role checks are unreachable (not confirmed).
- Get Together Adventures: the recorded source_url returns HTTP 404, but /about names both directors as Managing Director; role checks use /about and are confirmed. The stored source_url needs updating.
- Kibo Guides: the recorded /about page shows only "Wild Willy"; the home page names the founder in full, so the role check uses the home page.
- Maape Tanzania Safaris: robots.txt could not be read (4xx); pages themselves were served.

## Role checks

confirmed 31, changed 0, not_found 0, unreachable 4 (Francisco Raymond, Godbless Mariki, Wilfried Bernhard Zielke, Irene Robert Mrang'U).

## Organisations without a hook, and why

- Africa Travel Bureau: no staff, workforce or programme fact on the own site.
- Breathe Tanzania Safaris: only generic "supporting local communities" wording.
- Joagro Safaris: only generic community wording and a growth line with no link to staff.
- Lappet Faced Safaris: site blocked (403).
- Maape Tanzania Safaris: no workforce or programme fact.
- Passionate Guides Tanzania: no workforce or programme fact.
- Safari Kings: community wording is generic ("community based projects") and names no programme.
- Tanger Safaris: no workforce or programme fact.
- Udaay Safaris: no workforce or programme fact.
- Wild Ways Tanzania: site blocked (403).

## Hooks written: 15

strong (7): Bearfoot Expeditions, Cheli Peacock Safaris, Ecological Wilderness Adventure, I Dream of Africa, Kibo Guides, Meru Slopes, Safaris-R-Us.
moderate (8): A & N Uniques Safaris, Ajabu Adventures, Get Together Adventures, Great Image Expedition, Kilimanjaro Heroes, Nihapa Tours, Serengeti Clarity, Tanzania Unique Adventures.

## Points for a person to check

- Great Image Expedition: reviews on its own site include a recent one alleging an unresolved financial dispute.
- Safaris-R-Us: the directors founded The School of St Jude, a free school.
- Bearfoot Expeditions: unrelated newsletter text in the home page footer.
- Cheli Peacock Safaris: group is led from Kenya; the Tanzania General Manager is the local contact.

## Not finished

None.
