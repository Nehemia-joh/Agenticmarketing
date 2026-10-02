# Coverage log: wave10_master_employers_a (2026-10-02)

Slice: 40 company-master organisations (safari and tour operators, nearest first). Allowance 37 WebSearch calls; 37 used (Q37 was the last). No search was refused. Fetches went through `scripts/contacts/read_page.py` and the repository fetcher (cached, spaced, robots.txt honoured).

Status meanings used: found = a named person who leads or founded the organisation, from a source I fetched or a partner page; partial = routes or other facts, no usable named leader; not_found = nothing usable; blocked = the organisation's own site was blocked and nothing else was found.

## Result counts

- found 10, partial 25, not_found 4, blocked 1 (40 organisations, all reached).
- 18 people recorded for 12 organisations; 5 people have a direct work email on the same source, 7 have a phone labelled for them.

## Searches

All queries were of the form `"<exact name>" Arusha <owner/founder/director words>`; the answers are summaries and were checked against fetched pages before anything was recorded.

| No. | Organisation | Outcome |
|---|---|---|
| Q1/37 | Gifted African Adventures | no leader named |
| Q2/37 | LeKobe Adventures & Safaris | pointed to GetYourGuide supplier page; fetched, managing director named |
| Q3/37 | Mountain Warriors | a name was claimed but sources were review sites or blocked (GetYourGuide 403); not recorded |
| Q4/37 | Safaris Africa United | first name only from client reviews; not recorded |
| Q5/37 | Monkey Adventures (TMA Travels) | names claimed from aggregators; own site names no one; not recorded |
| Q6/37 | Memorable Sunrise To Sunset | no leader named; found the real website |
| Q7/37 | Tracks of Africa Safari Adventure | no leader named; found the website |
| Q8/37 | GreenHippo Travels | leaders only on LinkedIn/ZoomInfo; found the website; its About page has first names without roles |
| Q9/37 | Shidolya Tours | leader only on LinkedIn/ZoomInfo/TripAdvisor forum; not recorded |
| Q10/37 | Swala Safaris | first names from reviews; not recorded |
| Q11/37 | Kiriwe Travel and Trekking | founders confirmed on the TATO listing text |
| Q12/37 | Aim 2 Goal Safaris | no leader; found the .com site with a contact person block |
| Q13/37 | Mbasha Holdings | looks like a furniture maker, not a tour operator |
| Q14/37 | Sundown African Adventures | first name from TripAdvisor; not recorded |
| Q15/37 | The Map's Edge | names claimed from unconfirmed sources; not recorded |
| Q16/37 | Faune Flore | founders confirmed on own About page |
| Q17/37 | Fairtrek Jicho | founder confirmed on the German sales partner's About text |
| Q18/37 | Lemala Camps (Grumeti Expeditions) | no leader named |
| Q19/37 | Mega Tents / Al-Anver Outfitters | aggregators only; looks like a tent maker |
| Q20/37 | Leken Adventure | first name from reviews; not recorded |
| Q21/37 | Nkollo Tours | name from reviews and a platform page; not recorded |
| Q22/37 | Travel Booking Guide | own site 403; first name only; not recorded |
| Q23/37 | Migada Adventures | LinkedIn and reviews only; not recorded |
| Q24/37 | Nature Discovery | General Manager named in a partner's article (Carbon Tanzania), fetched |
| Q25/37 | Shaw Safaris | first names from a directory that answered 403; not recorded |
| Q26/37 | Anderson's African Adventures | owner not named |
| Q27/37 | Kilimanjaro Outfitters | nothing for this name; website domains do not resolve |
| Q28/37 | Sunny Adventure Safaris | no leader for this company (a hit was for Sunny Safaris Ltd, a different company) |
| Q29/37 | Yembi Adventure | no name; site unreadable (TLS) |
| Q30/37 | African Savannah Trekkers | founder in a snippet of a page that answered 403; recorded as snippet only |
| Q31/37 | Stone Town Tours and Safari | no leader named |
| Q32/37 | Horn & Horizon Safaris | no leader named |
| Q33/37 | Kibowhy Safaris | founders confirmed on own home page |
| Q34/37 | Aardvark Expeditions | review text only; a similar-named company (Aardvark Safaris) is different |
| Q35/37 | Base Camp Site | owners' names confirmed on own About page |
| Q36/37 | RushTrek Tours | CEO named on own About page (inside a quoted comment) |
| Q37/37 | Anderson's African Adventures (second) | owner still not named |

Organisations needing no search: Siri Maasai Safaris (own contact page names three founders), Akshar Tours (Mwanza, site unreadable), Intrepid Travel Tanzania (multinational), Fortes Africa (Mwanza, garage and car hire).

## Blocks and unreadable sites (none worked around)

- travelbookingtz.com (home and /about-us/): HTTP 403.
- shawsafaris.co.tz: bot-verification page. shawsafaris.com: connection timed out (robots.txt unreachable). myguidetanzania.com: 403.
- aim2goalsafaris.co.tz: bot-verification page (the .com site was readable).
- africantrekkers.travel/our-team/: HTTP 403 (only a search snippet exists).
- www.getyourguide.com Mountain Warriors supplier page: HTTP 403.
- megatents.co.tz: HTTP 403 (domain was my guess, not confirmed as theirs).
- alanvertents.com: HTTP 500.
- TLS failures: akshartoursandsafaris.co.tz and andersons.co.tz (hostname mismatch), yembitz.com (handshake error).
- DNS failure: kiliadventures.com, kilimanjarooutfitters.com.
- sunnyadventures.co.tz: robots.txt disallows crawling, not fetched (browser pass).
- Script-built sites with no readable text: giftedadventures.com, stonetowntoursandsafari.com, migadadventures.com/about, lekobeadventures.com (contacts only).
- basecampsite.com now redirects to a domain-for-sale page; nothing used from it.

## Notes for the merge

- Possible segment or location issues: Mbasha Holdings (furniture maker), Mega Tents (tent manufacturer), Fortes Africa (garage and car hire, Mwanza), Akshar Tours (Mwanza).
- Possible closure or gone website: Kilimanjaro Outfitters Limited.
- Weaker records: Elvis Mwendwa Jitwae (marketplace partner page, identity uncertain), Elisante Ayo (snippet only), Erik Matthews (named inside a quoted comment on the organisation's own page), Thomas Holden (undated partner article).
- Incomplete names (one name only): Laurent, Jackson, Carol (Siri Maasai), Abraham (Fairtrek Jicho), Virginie and Kelvin (Kibowhy).
- Named mailboxes listed by TATO without a role were kept as organisation emails only, not as leads: frank@kiriwetravel.co.tz, parimalpatel@akshartoursandsafaris.co.tz, james@tourvesteastafrica.com, the three intrepidtravel.com mailboxes.

## Organisations not reached

None: all 40 were researched.
