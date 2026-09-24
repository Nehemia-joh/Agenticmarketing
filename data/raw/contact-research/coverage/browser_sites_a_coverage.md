# Coverage log: browser sites A (2026-09-24)

- **Slice:** `runtime/contacts/slices/browser_sites_a.json`. It holds 24 websites that a plain crawler could not read (script-built pages), covering 26 organisations: 20 master and 6 welfare. robots.txt allows each one.
- **Method:** the built-in browser only, in the agent's own tab. For each site the agent opened the start URL, ran the prompt's capture script and read up to 8,000 characters of page text. It then opened at most 4 more contact, about or team pages taken from the capture's links, one at a time. No WebSearch or WebFetch calls were made (`searches_used: 0` on every record).
- **Output:** `data/raw/contact-research/browser_sites_a_2026-09-23.jsonl` holds 26 records, one per organisation. The two sites that list two organisations each give two lines.
- **Scratch:** `runtime/contacts/agents/browser_sites_a/`. It holds the record files, the append-and-validate helper and the running notes.
- **Accessed:** 2026-09-24.

## Summary

| Measure | Count |
|---|---|
| Sites in slice | 24 (26 organisations) |
| Sites read, with the organisation's own content | 11 (13 organisations) |
| Sites reached, but only empty or placeholder content | 3 (Acatree: empty body; Renea: empty directory listing; Maradawa: maintenance page) |
| Sites behind a bot check | 3 (Aim 2 Goal, AREM Foundation, Habari Foundation) |
| Domains lapsed or no longer the organisation's | 7 (Kigongoni, Maasai Magic, Mbasha, Mkombozi, Natural Smile, Ndoto Kubwa, St. Mark's) |
| Sites not reachable at all (DNS or connection failure) | 0 |
| Records: found / partial / not_found / blocked | 7 / 6 / 1 / 12 |
| Identity confirmed / uncertain | 12 / 14 |
| Emails (distinct, per site) | 12: 7 general, 2 role, 2 named, 1 personal-domain |
| Phone numbers (distinct, per site) | 14: 11 Tanzanian mobiles and 3 international (1 India, 2 US); 6 of the Tanzanian numbers also carry a WhatsApp link |
| Postal addresses | 3 (African Big Cats P.O. Box 13643 Arusha; Mobila P.O. Box 67 Arusha; Falco's US P.O. Box) |
| Physical addresses | 9 records (8 sites), most city-level only; street-level for Aafrin (Njiro), Carlight (Kinondoni, Dar es Salaam) and Mobila (Njiro) |
| People (distinct, per site) | 17, all `pdpa_risk: medium` (named person in a published professional role); none has a personal email or phone |

**Status rules.** `found`: identity confirmed, at least one email or phone, and a named leader or decision-maker read on the organisation's own page. `partial`: new routes or people, but not both. `not_found`: the site was read but publishes nothing usable. `blocked`: a bot check, a lapsed, parked or unrelated domain, or a site with no content.

## Site by site

| # | Site (final URL) | Organisation(s) | Pages read | Outcome |
|---|---|---|---|---|
| 1 | aafrinmedihealth.com (https://aafrinmedihealth.com/) | Aafrin Medihealth Solutions Ltd | home, /contact, /about | **found**. coordinator@ and support@ (role), sonia@ (named), one personal Gmail with no name or role; +255 689 788 788 and +91 98205 02148; registered address Plot 44 Hanspaul Road, Njiro, Arusha; 3 socials; 3 people (Founder & Managing Director, Director, Chief Patient Coordinator). A medical-tourism facilitator, not a safari operator. |
| 2 | acatreetours.co.tz (https://acatreetours.co.tz/) | Acatree Tours and Safaris | home | **blocked**. Every http/https and www/non-www variant redirects to a page that answers HTTP 200 with an empty body. |
| 3 | abercrombiekent.com (https://www.abercrombiekent.com/) | Abercrombie and Kent (T) Ltd; Abercrombie & Kent | home, /contact, /about-us | **partial** (x2). Served as the group's US site: 4 group social pages only. The North American phones are not recorded, and the site has no Tanzania office. The two records are likely duplicates. |
| 4 | africanbigcatssafaris.com (https://africanbigcatssafaris.com/) | African Big Cats Safaris | home, /contact-us/ | **partial**. info@; +255 786 508 052 and +255 682 120 812; P.O. Box 13643 Arusha; 3 socials. The site has no people page. |
| 5 | aim2goalsafaris.co.tz | Aim 2 Goal Safaris Ltd | home (check page only) | **blocked**. 'Bot Verification: Verifying that you are not a robot...'. Not interacted with. |
| 6 | aremfoundation.or.tz | AREM FOUNDATION | home (check page only) | **blocked**. The same 'Bot Verification' page. Not interacted with. |
| 7 | carlighttours.travel (https://carlighttours.travel/) | Car Light Tours And Safari Limited. | home, /contact/, /about-us/ | **found**. info@; +255 748 944 444 (also WhatsApp) and two +1 (484) US numbers; 4 Binti Matola Rd, Ada Estate, Kinondoni; 2 socials; 2 co-founders. Outside the Arusha-Kilimanjaro area (Dar es Salaam). |
| 8 | equitygroupholdings.com/tz (https://equitygroupholdings.com/tz/) | Equity Bank | home, /tz/about-equity | **found**. infotz@equitybank.co.tz; +255 768985500; 4 socials; 6 people (Non-Executive Chairman, Managing Director, Commercial Director, Director of Operation, Head of Human Resources, Head of Finance). This is the national site; no Arusha branch details. |
| 9 | falcoschildrenafrica.org (https://falcoschildrenafrica.org/) | Falcos Children Africa Inc | home, /contact/, /about/ | **partial**. US mailing address P.O. Box 14, Sapulpa, OK; founder named; no email, phone or socials (web form only). It runs its own children's village, which opened in Arusha in 2010. |
| 10 | farajaorphanage.org (https://farajaorphanage.org/) | Faraja Orphanage Children's Home | home, #/contact, #/about | **found**. info@; +255 763 485 866 (also WhatsApp and M-Pesa); Arusha; 2 Instagram handles; 3 people (Founder & Director, Co-Director, Head Matron). The site uses hash routes, which the capture's link list drops, so the routes were taken from the page's own menu. |
| 11 | giftedadventures.com (https://giftedadventures.com/) | Gifted African Adventures Ltd | home, /contact-us.php, /about-us.php | **partial**. info@; +255 753 900 422 (also WhatsApp); Arusha office; 2 socials. No people named. |
| 12 | habarifoundation.org | Habari Foundation International | home (check page only) | **blocked**. The first load served 'Bot Verification'. It cleared by itself seconds later without interaction, but per the rules the site was not read. |
| 13 | kigongoni.net (http://www.kigongoni.net/) | Kigongoni Lodge | home | **blocked**. A Chinese 'website under construction' placeholder (网站筹建中); the domain is no longer the lodge's. |
| 14 | maasai-magic.com (https://www.maasai-magic.com/) | MAASAI MAGIC SAFARI COMPANY LTD | home | **blocked**. An unrelated Chinese car-transmission repair template site; the domain is no longer the operator's. |
| 15 | maradawa.com (http://maradawa.com/) | Maradawa Tours Company Limited | home | **not_found**. 'Website Under Construction \| Maradawa' maintenance page with no contact details. Identity uncertain (name only). |
| 16 | mbashaholdings.com (https://mbashaholdings.com/lander) | Mbasha Holdings Ltd | lander | **blocked**. GoDaddy parked page; the domain is for sale at auction. |
| 17 | migadadventures.com (https://migadadventures.com/) | Migada Adventures Tours and Safaris | home, /contact, /about | **partial**. info@; +255 787 370 023 (also WhatsApp) and +255 786 370 023; 'Migada Adventure Ltd, Arusha'; 3 socials. No people named. |
| 18 | mkombozi.org (https://www.mkombozi.org/lander) | Mkombozi Centre for Street Children | lander | **blocked**. GoDaddy: 'has expired and is parked'. |
| 19 | mobilasafaris.com (https://mobilasafaris.com/) | Mobila Tours & Safaris | home, /contact, /about | **found**. info@; +255 786 822 848 (also WhatsApp); Njiro Container Area, Block D, House No. 22 and P.O. Box 67, Engutoto Ward, Arusha; Instagram; founder by first name only. The contact page's own fields render empty ('undefined'), so the routes come from the site footer. |
| 20 | naturalsmileexpeditions.com (redirects to slider.com) | Natural Smile Expeditions | redirect target | **blocked**. Parked-domain search and ad page with betting ads. Nothing was clicked. |
| 21 | ndotokubwatours.com (http://ndotokubwatours.com/) | Ndoto Kubwa Tours and Safaris Company LTD | home | **blocked**. Namecheap: 'Domain registration has expired.' |
| 22 | reneaschools.ac.tz (http and https www) | Renea Pre and Primary School | home (both schemes) | **blocked**. An empty 'Index of /' directory listing on both schemes. The welfare run already marks this school out of scope. |
| 23 | ronjoosafaris.co.tz (https://www.ronjoosafaris.co.tz/) | Ronjoo Safaris; Shubhomis Adventure (Ronjoo Safaris) | home, /contact, /about | **found** (x2). deepak@ (the only email; a first-name mailbox with no matching person named); +255 747 394 631 (also WhatsApp); Arusha office; 3 socials; 1 person (Operations Manager). Identity is uncertain for Shubhomis, which the site never names. The two records are likely duplicates or a trading-name pair. |
| 24 | saintmarkskids.org (https://saintmarkskids.org/lander) | St. Mark's Children's Home and Orphanage (Usa River) | lander | **blocked**. GoDaddy parked page. |

## Blocks and what was not done

- **Bot checks (3):** aim2goalsafaris.co.tz, aremfoundation.or.tz and habarifoundation.org all served the same 'Bot Verification' page. None was interacted with, waited out or worked around. Habari's check cleared by itself during loading; its content was still not read or recorded. The coordinator can decide whether a check that clears by itself may be retried.
- **Lapsed, parked or re-registered domains (7):** the website field is left blank on these records so the dead domain is not carried forward. A lapsed domain can mean the organisation has closed or moved to another site. This matters most for the two welfare records, Mkombozi and St. Mark's. Each needs confirming from another source.
- **Empty sites (2) and a maintenance page (1):** Acatree, Renea and Maradawa. They could be retried later.
- **Never done:** no CAPTCHA was solved, no certificate warning was bypassed and nobody logged in. No form was filled or submitted and no cookie banner was clicked (Mobila's banner did not hide the text). Nothing on parked or ad pages was clicked.

## Flags for the coordinator

- **Different kind of organisation from its segment:** Aafrin Medihealth is a medical-tourism facilitator, not a safari operator. Falco's Children Africa runs its own children's village and is not only a funder.
- **Outside the Arusha-Kilimanjaro area:** Car Light Tours (Kinondoni, Dar es Salaam, with US numbers). Aafrin's registered address is in Njiro, Arusha, but its operating office is in Dar es Salaam. Equity Bank's site is national and gives no Arusha branch.
- **Likely duplicate pairs:** O0843c2f745ba and O35c962655ba3 (Abercrombie & Kent); O16c4e7a99dcb and O7350992422d9 (Ronjoo Safaris / Shubhomis Adventure).
- **Content to treat with care:** Ronjoo's About page contradicts itself about dates, so its team listing may be placeholder text. On Faraja's site, the contact page's Facebook link carries the founder's full name and may be a personal profile, so it is not recorded. Aafrin's contact page lists an individual's Gmail with no name or role; it is recorded as `personal_domain` and is not linked to any person. Gifted Adventures links an 'LLM Usage Guidelines' page; it is not a contact page and was not opened.
- **Not recorded by design:** children named on welfare sites (Faraja), family histories and biographies (Aafrin, Carlight, Falco's, Equity), a quoted government officer (Falco's), guides and other non-leadership staff, the US toll-free numbers on A&K's site, and a Kenyan-code tel: link on Equity's site.
