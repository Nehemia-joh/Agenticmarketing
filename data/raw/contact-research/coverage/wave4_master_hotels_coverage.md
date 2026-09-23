# Coverage log: wave 4, master hotels (2026-09-23)

- **Slice:** `runtime/contacts/slices/wave4_master_hotels.json`. It holds 17 company-master hotels, nearest first. Each already had a published route; each one's need was a named decision-maker (owner, general manager, managing director or HR).
- **Search allowance:** 17 WebSearch calls. All were used (Q1/17 to Q17/17), and none was refused by the session cap. After Q17, only URLs already in hand were fetched.
- **Output:** `data/raw/contact-research/search_wave4_master_hotels_2026-09-23.jsonl` (17 records, one per organisation).
- **Scratch:** `runtime/contacts/agents/wave4_master_hotels/`. It holds the parsed ACHPR list, the Senator Hotel script bundle, the Njiro Climax rate card, the fetch log and the record builder.

## Summary

| Measure | Count |
|---|---|
| Organisations in slice | 17 |
| Researched (one JSONL line each) | 17 |
| found | 1 (Arusha Villa) |
| partial | 13 |
| not_found | 3 (Lush Garden Business Hotel, Osim Bnb, Arusha Backpackers) |
| blocked | 0 (three own sites fail TLS; see Blocks) |
| Not reached | 0 |
| Identity uncertain | 0 |
| WebSearch calls used | 17 / 17 |
| Records with a new email or phone | 12 (11 read on fetched pages; A1 Hotel and Resort is snippet-only) |
| New or replacement websites | 8 (3 replace dead domains: Venice, A1, Njiro Climax) |
| People recorded | 4, all `medium`: 1 named manager (Arusha Villa), 2 people named without a job title (Arusha Villa) and 1 booking contact without a role (Lush Garden Hotel, ACHPR list, 2023) |
| People who will pass `contact_lib.clean_person` | 0 (see Person filter) |

**The stopping rule (a named decision-maker for each hotel) is unmet for 16 of 17 hotels.** Hotel websites in this slice name no owner, general manager or HR. The one named manager, at Arusha Villa, is published by surname only.

**Status rules used in this slice.** The need is a named decision-maker, so the rules are stricter than in waves 2 and 3.
- `found`: identity is confirmed, and the need was met. A named person with a decision-making role was read on a fetched page, from the organisation's own site, an official list or a parent body.
- `partial`: new profile data was found, but no named decision-maker. The new data may be a website, email, phone, address or official social page, or a named contact without a role. It may also rest on snippets only.
- `not_found`: nothing usable beyond what the master already holds.
- `blocked`: the organisation's own source refused automated reading, and nothing usable was found elsewhere.

`searches_used` gives each search to exactly one organisation, so the records sum to 17. Q1's results also surfaced the Lush Garden group's Facebook page, which is recorded on Lush Garden Hotel.

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/17 | "Lush Garden Business Hotel" Arusha | Lush Garden Business Hotel | Booking listings. Also surfaced the group Facebook page (facebook.com/lushgardenhotels/). A tour operator's places page (tranquilkilimanjaro.com, fetched) shows the operator's own phone and email and the Sakina hotel's address, so it was not used. lushgardenhotel.com-tanzania.com is a third-party template site and was not used. No people. |
| Q2/17 | "Greenside Hotel" Arusha | Greenside Hotel Arusha | Official site greensidehotel.com. Home, about and contact pages fetched: info@greensidehotel.com, 0748704444, Nelson Mandela Rd, Kijenge, 23110, and Instagram. No people. |
| Q3/17 | "New Way Hotel" Bomang'ombe Hai | New Way Hotel | Booking listings and the Facebook page @newwayhoteltz (not read). No people. The recorded domain newwayhotel.co.tz does not resolve. |
| Q4/17 | "Lush Garden" hotel Arusha contact manager (limited to lushgardenhotels.co.tz and lushgardenhotels.com) | Lush Garden Hotel | Snippet of the hotel's contacts page: Kwaidd Sakina, Nairobi Road opposite Hass Petrol station, +255787884466, reservation@. No manager. The lushgardenhotels.com result had an unusual redirect-style URL, so nothing was used from it. |
| Q5/17 | "Osim Bnb" Arusha | Osim Bnb | Booking listings only: four rooms, run by a "private host". Nothing usable. |
| Q6/17 | "Senator Hotel" Arusha | Senator Hotel | Official site senatorhotel.co.tz, which renders in script. Its text was read from its own script bundle: P.O. Box 15666, Father Babu Road, info@senatorhotel.co.tz, +255 766 007 599 and Instagram. The Facebook page was not read. No people. |
| Q7/17 | "Stereo Hotel" Arusha | Stereo Hotel | Instagram and Facebook pages (not read). Wanderlog (fetched) gives Stand Ndogo and +255 754 309 998. A Gmail inbox in the search summary could not be traced to any page and was not recorded. No people. |
| Q8/17 | "Venice Hotel" Arusha | Venice Hotel | Current site venicehoteltz.com. Home, about and contact pages fetched: info@venicehoteltz.com, the OSM phone, Makao Mapya and Instagram. The Facebook page was not read. No people. |
| Q9/17 | "Arusha Centre Tourist Inn" | Arusha Centre Tourist Inn | Listings. Trip.com (fetched) gives "Arusha Center Inn" at plus code JMHQ+GGQ, Pangani Street, about 65 m from both OSM nodes, with +255 754 583 455. Slice D's Arusha Tourist Inn has the same phone: possible duplicate. No people. |
| Q10/17 | "Meru House Inn" Arusha | Meru House Inn | Booking listings only. Wanderlog (fetched) gives plus code JMGJ+9QF on Sokoine Rd, 34 m from the OSM node. No people. |
| Q11/17 | "B-More Comfort Stay" | B-More Comfort Stay | Official site bmorecomfortstay.com. Home, about and contact pages fetched: info@bmorecomfortstay.com, the OSM phone and Uzunguni Street, Hai. No people. |
| Q12/17 | "Arusha Backpackers" hotel Sokoine Road | Arusha Backpackers | Booking listings only. The listed site did not answer. A phone in the search summary could not be traced to a page and was not recorded. No people. |
| Q13/17 | "A1 Hotel and Resort" Arusha | A1 Hotel and Resort | The hotel now uses a1hotelandresort.com, which fails TLS (host's certificate). The Facebook page was not read. A third-party template site was not used. |
| Q14/17 | "Njiro Climax" resort hotel Arusha | Njiro Climax Resort Hotel | Current site njiroclimax.online (Wix; home page and rate card fetched): info@njiroclimax.com, +255 754 323 213 and a WhatsApp line. The site also presents a sister property, Njiro Legacy. An iph.co.tz rental listing names its own agent and was not used. No people. |
| Q15/17 | "Mrimba Palm Hotel" Arusha | Mrimba Palm Hotel | Listings, plus the official site already read through its email domain. No people. |
| Q16/17 | A1 Hotel and Resort Arusha general manager team contact (limited to a1hotelandresort.com) | A1 Hotel and Resort | Snippets of the hotel's own site: +255 766 800 901 (WhatsApp, call or SMS), info@a1hotelandresort.com, and Off Ndorobo Rd, 11782 Burka Olasiti 23119. No manager named. |
| Q17/17 | Lush Garden Business Hotel Arusha location phone (limited to lushgardenhotels.co.tz) | Lush Garden Business Hotel | The group site's indexed pages mention only the Sakina hotel, so the Kijenge property's tie to the group is unconfirmed. **Budget spent.** |

## Fetched without a search

- **Arusha Villa** (known source, arushavilla.co.tz):
  - The crawl's HTTP 403 did not recur. Home, over-ons, contact and arusha-villa pages were fetched; robots.txt disallows only /wp-admin/.
  - The contact page gives reservations@arushavilla.co.tz and "+255 784 356 225 (ook what's app, onze manager Pallangyo)". It also names two people without a job title.
  - The about page gives a Dutch mobile.
  - Family details on the about page were not recorded.
- **Gold Crest Hotel**, reached through the domain of its published inbox:
  - goldcresthotel.com is a brand page for Mwanza and Arusha, and links arusha.goldcresthotel.com.
  - The Arusha home and get-in-touch pages give P.O. Box 13285, Old Moshi Road, a new phone (+255 677 015 387) and info@. No people.
  - Both hosts' robots.txt set Crawl-delay 10, which was honoured.
  - The brand's ZoomTanzania profile is for the Mwanza hotel and was not used.
- **Mrimba Palm Hotel**, through the domain of its published inbox (mrimbapalmhotel.co.tz):
  - Home, about and contact pages were fetched. The about page needed a second attempt after a dropped connection.
  - The contact page gives reservations@mrimbapalmhotel.co.tz and the OSM phone. No people.
- **ACHPR list** (URL known from slice D): *List of hotels vetted by the Govt of Tanzania and ACHPR jointly*, 77th session, Arusha, September 2023.
  - It was parsed locally. Row 13 (Lush Garden Hotel) gives a booking contact, P.O. Box 10255, a mobile, and the reservation@ inbox that matches OSM.
  - Rows 17 (Senator) and 31 (Stereo) were already recorded by slice D, so they are not repeated.
  - No other slice hotel appears on the list.
- **Local data, no network:** the OSM contact file gave street tags and coordinates. Coordinates were used to check identity against plus codes and to measure distances.

## Blocks and unreadable sites

- **TLS failures** (recorded; not worked around):
  - lushgardenhotels.co.tz: the certificate covers only *.lushgardenhotels.co.tz, and www redirects to the bare domain.
  - lushgardenhotels.com: the certificate covers only *.lushgardenhotels.com.
  - a1hotelandresort.com: the site presents the hosting provider's certificate, *.web-hosting.com.
- **HTTP 403:** none this wave. The crawl's 403 on arushavilla.co.tz did not recur through WebFetch.
- **No answer:** www.arushabackpackers.co.tz. HTTPS was refused at 51.89.133.126:443, and HTTP timed out after 20 s. The crawl also timed out.
- **Domains that no longer resolve (ENOTFOUND):**
  - newwayhotel.co.tz
  - www.venicehotel.co.tz and venicehotel.co.tz
  - www.a1hotelandresort.co.tz
  - www.climaxresort.com
  - arushacenterinn.com
  - stereohotel.co.tz, which appears in the Facebook page address; the master holds no website for Stereo Hotel.
- **Not read by rule:** Facebook and Instagram pages (URLs recorded only). Tripadvisor, Booking.com and other booking sites (search results only).
- **robots.txt:**
  - Every site fetched had a readable robots.txt that allowed the pages read.
  - greensidehotel.com fully disallows only GPTBot.
  - goldcresthotel.com and its Arusha subdomain set Crawl-delay 10.
  - senatorhotel.co.tz, iph.co.tz, mrimbapalmhotel.co.tz and www.lushgardenhotels.co.tz allow all.
  - arushavilla.co.tz, venicehoteltz.com, bmorecomfortstay.com, www.zoomtanzania.net, wanderlog.com, trip.com and njiroclimax.online disallow only paths not used.
  - tranquilkilimanjaro.com allows all.

## Person filter

`contact_lib.clean_person` will drop all four people recorded. They are recorded exactly as published so that a person can decide.

| Person | Organisation | Why dropped |
|---|---|---|
| Pallangyo | Arusha Villa | Name is one word, published by surname only; the role "Manager (onze manager)" would pass. |
| Andre Timmer | Arusha Villa | Named on the contact page without a job title. |
| Marjolein de Rooij | Arusha Villa | Named on the contact page without a job title. |
| Mary Joseph | Lush Garden Hotel | ACHPR booking contact with no role stated (Sept 2023). |

Asking the villa's manager line (+255 784 356 225) for the manager's full name would make the lead usable.

## Warnings for review

These notes raise review items through `contact_lib.note_flags`; the flags were checked with it.

- **Website gone:**
  - New Way Hotel (newwayhotel.co.tz; its info@ inbox may bounce)
  - Venice Hotel (replaced by venicehoteltz.com; info@venicehotel.co.tz may bounce)
  - A1 Hotel and Resort (replaced by a1hotelandresort.com, which fails TLS)
  - Njiro Climax Resort Hotel (replaced by njiroclimax.online)
  - Arusha Centre Tourist Inn (arushacenterinn.com)
- **Possible duplicate:** Arusha Centre Tourist Inn (Oc03f6e0d7dc1) and Arusha Tourist Inn (Odbecbb3f6ea6, slice D).
  - Trip.com gives both the same phone, and this inn's inbox is atihotel@.
  - Slice D places Arusha Tourist Inn on Martine Street next to Arusha Backpackers, about 750 m away, and Tripadvisor lists the two separately.
  - They may be sister hotels under one owner.
- **Conflicting websites:** the master holds the dead domains for Venice, A1 and Njiro Climax. The merge will send the new sites to review.

## Leads for other records

- **Njiro Legacy** (slice D found nothing): njiroclimax.online presents Njiro Legacy as the second property of the Njiro Climax operator, with a page at /njiro-legacy and an Instagram account njiro_legacy. The next run could use the Njiro Climax routes for it.
- **Lush Garden Business Hotel:** no source ties it to the Lush Garden Hotels group, which is 6.2 km away in Sakina. Only the OSM mobile is known.

## Organisations not reached

None. All 17 organisations have a line.

## Next run

1. Hotel websites here do not name managers. A phone call to the published lines (reception, reservations) asking for the general manager's or HR's name and work email is more likely to work than web search.
2. Before outreach, check the routes that come from snippets or aggregators: A1 (snippets only), Stereo (Wanderlog phone) and Lush Garden Hotel (2023 ACHPR mobile and contacts-page snippet).
3. The TLS-blocked sites (Lush Garden Hotels, A1) were not read. Reading them would need the user's decision, for example a manual browser check.
