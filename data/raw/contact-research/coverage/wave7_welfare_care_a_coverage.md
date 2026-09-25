# Coverage log: wave 7, welfare care A (26 September 2026)

- **Slice:** `runtime/contacts/slices/wave7_welfare_care_a.json`, nearest first: 34 NGOs from the national NGO register whose type is not yet known (segment "Welfare (unclassified child-focused NGO)"), 6.7 to 20.4 km from a campus. Every one needed a published route; every `known_sources` list was empty.
- **Output:** `data/raw/contact-research/search_wave7_welfare_care_a_2026-09-23.jsonl`, one line per organisation, appended as the work went and finally put in slice order. The date key is the programme's shared key; the access date is 26 September 2026 (register profiles collected by the welfare run keep their 22 September 2026 date).
- **Searches:** allowance 39 WebSearch calls. 37 calls were made (Q1/39 to Q37/39). The Q32 call also ran two query variations by itself inside the tool, so 39 searches are counted against the allowance and searching stopped there. The session cap refused none. No search was routed through WebFetch, a browser or a results page. Each query named one organisation; Q7, Q9, Q13, Q16, Q19, Q21 and Q32 joined that organisation's name, acronym or spelling variants with OR. Q35-Q37 were second searches for the three most promising child-focused organisations still lacking a route.
- **Fetching:**
  - Pages were read with `scripts/contacts/read_page.py` (shared cache, spacing per site, robots.txt honoured), plus a link lister, a Cloudflare-email decoder (`contact_lib.decode_cfemail`, as the crawler does) and a PDF text reader in `runtime/contacts/agents/wave7_welfare_care_a/`, all using the same cached, robots-aware fetcher. WebFetch and the browser were not used.
  - robots.txt was read for every host fetched. A 4xx robots.txt counted as no rules. No page was disallowed, and no page was read under an unreachable robots.txt.
  - `nslookup` against 1.1.1.1 or 8.8.8.8 was used only to tell a missing domain (NXDOMAIN) from a failing one; nothing was fetched around a failure. One temporary local lookup failure (eretoea.org, error 11002) was retried once through the normal fetcher and then read.
  - Without searching, the register's project pages (`nis.jamii.go.tz/project_details/<id>`) were read for seven organisations with projects and no route. They name funders. That led to the US parent of African Moons Tanzania (africanmoons.org, domain tried directly), to TRMEGA's funder Partnerschaft für Afrika, and to Son and Oscar's co-founder.
  - A few domains were tried directly from a name (no search); see "Domains tried directly".
- **Organisations written:** 34 of 34.
  - Status: found 9, partial 3, not_found 22, blocked 0.
  - Identity: confirmed 34 (register identity; namesakes found by the searches are named in the notes and were not used).
  - Not reached: none.
- **Results:**
  - 33 named leads across 9 organisations, all from fetched pages. PDPA risk: 32 medium, 1 risky (Sally Bruton Vann of African Moons, whose published inbox is a personal Gmail).
    - 18 lead or decide for the organisation (founders, directors, presidents, chair, managers), across 9 organisations.
    - 4 are secretaries or a treasurer; 11 are board members (Bassari's German parent board, GenTech, TUFOI).
    - 2 are named by one name only and will be labelled incomplete: Young Minds' Education Director "Godfrey" and Son and Oscar's co-founder "Mr. Son".
  - Direct routes for 9 organisations: 11 emails (9 general, 1 named work inbox, 1 personal-domain Gmail named after the organisation: Bassari's `tz.bassari@gmail.com`) and 14 phones (9 Tanzanian mobiles, 5 international numbers of foreign parent or support bodies), all read on fetched pages.
  - Indirect routes: 10 websites, 5 postal and 7 physical addresses, 21 official social or listing links.
  - Where a foreign body runs or funds the Tanzanian NGO, its routes and people were recorded as that parent's (Bassari e.V., Education is Light e.V. for MILELO, African Moons USA). FRI-SUCODE's own letterhead names the German network's site as its website.
- **Prior evidence read before any search:**
  - the slice
  - `data/raw/welfare-research/research_*.jsonl` and all earlier `data/raw/contact-research/*.jsonl`: none mentions these 34 organisations
  - the NIS register profiles in `nis_catchment_profiles_2026-09-22.jsonl`, which give registration numbers, aims and project titles but no contacts. All 34 matched a profile by name.
  - `data/interim/welfare-leads/welfare_organisations.tsv`, read only, to check for twins (Bassari, Huruma, Shalom, Ereto, Solstice). No twin was found.
- **Recording rules applied:**
  - People come only from the organisation's own site or listing, its parent or founding body's site, or the official register.
  - Not recorded as leads: names on press pages (TRMEGA's founder in Rooted Magazine), a funder's partner page (TRMEGA's head and project manager on Partnerschaft für Afrika), a data broker (RocketReach), public figures quoted on Tabasamu's site, and founders of other organisations named on a partner's site (Shalom Centre's and the Safe Home for Children with Disabilities' founders on africanmoons.org).
  - Also not recorded: biographies, family ties, personal Instagram and Twitter links of GenTech's team, German street addresses from Impressum pages (Bassari e.V., Education is Light e.V.), bank details (Young Minds), and staff outside outreach (nannies, housekeepers, guards, caretaker, cook, driver, teacher, IT helper, tax adviser, attorney, German volunteer heads).
  - Theme placeholders were dropped: GenTech's `tel:+0123456789` and `info@example.com` links (the shown values were used), and African Moons' `tel:+44 121 354678`.
  - Nothing about children, parents or residents was recorded; beneficiary names in FRI-SUCODE's 2017 report were skipped.
  - Every note is at most 600 characters, and warning phrases were checked against `contact_lib.note_flags`. The flags raised are intended: fit to check (Victory of Women and Children, Tarama Women Foundation), location to check (MACAO, Kujengana), website gone (MACAO, Masola) and hijacked site (Kujengana).

## Status definitions

- `found`: identity confirmed, and at least one email or phone read on a page published by the organisation, its parent or founding body, or an official register.
- `partial`: only indirect routes (website, social page, address), or leads without a route.
- `not_found`: nothing usable found.
- `blocked`: the only promising source refused automated reading. Blocked sites with other evidence are marked partial or not_found.

## Searches

| # | Query | Organisation (slice position) | Outcome |
|---|---|---|---|
| Q1/39 | `"Victory of Women and Children Foundation" Arusha` | 1. VICTORY OF WOMEN AND CHILDREN FOUNDATION | No match: Arusha Victory school, Tupendane Africa, other women/children groups. victoryprogramme.org (HTTP 500) and womenandchildrenfoundation.org (unreadable) have different names; not used. not_found |
| Q2/39 | `"Wings of Change" Arusha Tanzania` | 2. WINGS OF CHANGE (WOC) | Travel pages and WiLAT's logistics 'Wings of Change' programme (read: no Tanzania mention); not the same. not_found |
| Q3/39 | `"TRMEGA" Tanzania gender AIDS` | 3. TRMEGA | Press only: Rooted Magazine (read) and Slow Food (HTTP 403) place the centre in Maji ya Chai, opened 2010; Mabumbe directory has no contacts. Later, without searching: the register's project page names its funders, and one of them, Partnerschaft für Afrika (read), calls TRMEGA its partner for education support and career preparation and names its head and project manager (not recorded: a funder's page). No route. not_found |
| Q4/39 | `"Wings Children Foundation" Arusha` | 4. Wings Children Foundation (WCF) | No match (Mwanga Children's Foundation, Youth Wings, Arusha Children's Effort, Wings of Hope for Africa are different). not_found |
| Q5/39 | `"Watoto Future Initiatives" Arusha` | 5. WATOTO FUTURE INITIATIVES | No match (Watoto Foundation, Happy Watoto, Watoto Africa are different). not_found |
| Q6/39 | `"Bassari" Arusha children's home Tanzania` | 6. Bassari Community Empowerment and Development | German parent Bassari e.V. (bassari.de): partner named; children's home in Ngyani (Meru); P.O. Box 200 Usa River, +255 phone, Gmail inbox, German inbox and phones; Founder Director, Director/Social Worker, Secretary, 5 parent board members. found |
| Q7/39 | `"FRI-SUCODE" OR "Friends Support for Community Development" Tanzania` (acronym OR full name of one organisation) | 7. FRI-SUCODE | German supporter nambala-help.org: 2017 letterhead PDF gives P.O. Box 641 Arusha, phone, inbox; 2025 update names Director and Secretary; Instagram. VisibleImpact redirects to a closed platform; Mabumbe lists no contacts. found |
| Q8/39 | `"Le Solstice" foundation Tanzania Arusha children` | 8. FOUNDATION LE SOLSTICE TANZANIA | Juapole page (read) describes the Swiss foundation's Tanzanian work (Huruma Orphanage, Usa River) and links lesolstice.ch, which redirects to lesolstice.org (home read; no contacts); /about answered HTTP 429, so nothing more was requested there. partial |
| Q9/39 | `"Malezi AIDS" OR "MACAO" Malezi Arusha organization` (full name OR acronym of one organisation) | 9. MACAO | Idealist listing (read): based near Loliondo (Ngorongoro), orphanage and Bright English Medium School, 2 founders. Own sites macao-tz.org and brightmediumschool.org: NXDOMAIN. ZoomTanzania: DNS failure. Volunteers Base: HTTP 403. Trickle Out directory: injected casino link, not used. partial |
| Q10/39 | `"Masola Foundation" Arusha` | 10. Masola Foundation | Own site masolafoundation.org in results (snippet matches register aims) but NXDOMAIN; nothing read. not_found |
| Q11/39 | `"Gentech Foundation" Arusha Tanzania` | 11. GENTECH FOUNDATION | Own site gentechfoundationtz.org: Sekei St address, phone, inbox, socials, 5 board leads. gentechfoundation.com is a US namesake (Phoenix), not used. found |
| Q12/39 | `"Kujali Foundation" Tanzania Arusha` | 12. KUJALI FOUNDATION TANZANIA (KFT) | Namesakes only: UK charity Kujali (Moshi, via the Catholic diocese; read), French association and Facebook page 'Kujali Tanzania' (not read; not tied to this entry); Karibu Foundation results unrelated. not_found |
| Q13/39 | `"Tupendane Foundation" OR "TUFOI" Arusha Tanzania` (name OR acronym of one organisation) | 13. TUFOI | Own site tupendanefoundation.or.tz (registration number matches): P.O. Box 197 Usa River, mobile/WhatsApp, 2 inboxes, socials, founder-ED and 5 board members. found |
| Q14/39 | `"Tabasamu Africa" Arusha Tanzania` | 14. TABASAMU AFRICA ORGANIZATION | Idealist listing (registration number matches) and own site tabasamuafrica.org: 2 inboxes, 2 mobiles, Ilboru office; no named leaders. Tabasamu orphanage (TCC Arusha) and a Dar tour firm are different. found |
| Q15/39 | `"Tarama Women Foundation" Tanzania` | 15. TARAMA WOMEN FOUNDATION | No match (Women Fund Tanzania, TAWREF and other national women's bodies). not_found |
| Q16/39 | `"VODEC" OR "Volcano Development of Children" Arusha` (acronym OR name of one organisation) | 16. VODEC | No match (SOS Children's Village, Volcano College, volunteer placements). not_found |
| Q17/39 | `"Ashe Foundation" Arusha Tanzania` | 17. ASHE FOUNDATION | No match (Ashe Tanzania Tours & Safaris, Ashe Oleng House: not tied to the NGO). not_found |
| Q18/39 | `"African Moons" Tanzania Arusha` | 18. African Moons Tanzania | Only moon-phase and general Arusha pages. Later, without searching: the register's project pages name the funder 'AFRICAN MOONS USA'; its site africanmoons.org (domain tried directly) describes the same Arusha projects and gives the founders, a named work inbox, US phones and a P.O. Box. found |
| Q19/39 | `"Ejung'o" OR "Ejungo" child youth foundation Arusha` (two spellings of one name) | 19. EJUNG'O CHILD AND YOUTH FOUNDATION | No match; the allAfrica story in the results (read) concerns Tupendane Africa Foundation. not_found |
| Q20/39 | `"Stable Life for Tanzania Kids" Arusha` | 20. STABLE LIFE FOR TANZANIA KIDS FOUNDATION | No match (SOS, Arusha Kids Trust, One More Child, The Small Things). not_found |
| Q21/39 | `"Embuan Children and Youth Foundation" OR "ECYF" Embuan Arusha` (name OR acronym of one organisation) | 21. ECYF | Only Embuan Foundation (pastoralist work, founded 2023; its domain is gone), not tied to this 2017 entry. not_found |
| Q22/39 | `"Tanzania Host Volunteer" Arusha` | 22. TANZANIA HOST VOLUNTEER (THV) | Idealist listing (read): mobile, Kaloleni, P.O. Box 2422, site thv.or.tz; the site failed DNS (server failure) and was not read; Facebook page noted, not read. found |
| Q23/39 | `"Kingdom Childcare Organization" Kilimanjaro Hai` | 23. KINGDOM CHILDCARE ORGANIZATION | No match (US childcare centres; Children of Kilimanjaro Orphanage is different). not_found |
| Q24/39 | `"Meshack Ereto Foundation" Arusha` | 24. MESHACK ERETO FOUNDATION | Only Ereto East Africa Foundation (eretoea.org, read: no mention of Meshack or this registration; a different NGO) and Kenyan 'Meshack' foundations. not_found |
| Q25/39 | `"Kuza Kipaji" Arusha` | 25. KUZA KIPAJI ORGANIZATION | Only a Kenyan namesake (URI cooperation circle in Kibera, Nairobi; read). not_found |
| Q26/39 | `"Kujengana Network" Arusha` | 26. Kujengana Network | Former own site kujengana.org now serves a Turkish gambling site (hijacked): nothing used. Snippet said Kyela district (far outside the catchment), registered November 2023; unverified. not_found |
| Q27/39 | `"Young Minds Education Organization" Arusha` | 27. YOUNG MINDS EDUCATION ORGANIZATION | Own site ymearusha.org (registration number matches): inbox, 2 WhatsApp mobiles, Soweto Road address, Instagram, Facebook; President, Secretary, Program Director, Education Director (one name). found |
| Q28/39 | `"Glory Vision" Tanzania Arusha` | 28. Glory Vision Tanzania | Only World Vision Tanzania and tour firms. Later, without searching: the register's project page names the funder 'GLORY VISION CORPORATION IN KOREA'; gloryvision.or.kr answered HTTP 403 (not worked around). not_found |
| Q29/39 | `"Milelo Tanzania" Arusha` | 29. Milelo Tanzania Organization | German support association's site milelo.de: the Tanzanian NGO MILELO Tanzania runs a free primary school in Kijenge (opened January 2026); inbox, German mobile, Instagram; 4 founders/managers. found |
| Q30/39 | `"ESAM Foundation" Tanzania Arusha` | 30. ESAM Foundation for Change | No match (ESAMI; an 'Esamcompany' page). not_found |
| Q31/39 | `"Son and Oscar Foundation" Tanzania` | 31. Son and Oscar Foundation | No match (Oscar foundations in Mumbai and Nairobi; Oscar's Foundation site read: no country, not tied). Later, without searching: the register's project pages name the co-founder only as 'Mr. Son' and show English lessons and lunch for 365 pupils of Manyata Primary School. partial |
| Q32/39 | `"St. Simon Tomorrow Return of Hope" OR "Tomorrow Return of Hope Foundation" Arusha` (full and short name of one organisation) | 32. ST. SIMON TOMORROW RETURN OF HOPE FOUNDATION | No match. The search tool ran two further variations on its own within this one call (hope foundations and Rays of Hope College in Arusha); counted as 3 searches against the shared cap to be safe. not_found |
| Q33/39 | `"United We Change Lives" Arusha Tanzania` | 33. UNITED WE CHANGE LIVES | Only a RocketReach data-broker profile (HTTP 403, not used) and unrelated Idealist listings. Tried domains: four do not exist; uwcl.org is United Way of Central Louisiana. not_found |
| Q34/39 | `"Child and Youth Development Center" DLBC Moshi` | 34. Child & Youth Development Center - DLBC | No match (TAG Kilimanjaro Revival Temple centre, Moshi Kids Centre, Child Hope Development Organization are different). not_found |
| Q35/39 | `글로리비전 탄자니아 아루샤` (Glory Vision, Tanzania, Arusha in Korean; the register points to a Korean parent body) | 28. Glory Vision Tanzania (second search) | Only Korean travel and encyclopedia pages about Arusha. not_found |
| Q36/39 | `"African Moons" charity children disabilities orphanage Tanzania` | 18. African Moons Tanzania (second search) | Only other disability and orphan charities (Able Child Africa, Light in Africa, Karibu Kinderhilfe). The organisation was found afterwards without searching (see Q18). |
| Q37/39 | `"Huruma Orphanage" "Usa River"` | 8. FOUNDATION LE SOLSTICE TANZANIA (second search, via the orphanage it finances) | Juapole page again; TerraWatu and Worldview pages (read) describe other support to a Huruma orphanage near Nshupu/Usa River but never name Le Solstice; no Tanzanian route for the foundation. partial (unchanged) |

## Blocked sites (recorded, not worked around)

| Site | Answer | Organisation |
|---|---|---|
| fondazioneslowfood.com (article on TRMEGA) | HTTP 403 | TRMEGA |
| volunteersbase.com (MACAO listing) | HTTP 403 | MACAO |
| lesolstice.org/about | HTTP 429; no further request was made to that host, so its contact page was not tried | Foundation Le Solstice Tanzania |
| rocketreach.co (data broker) | HTTP 403 | United We Change Lives |
| gloryvision.or.kr | HTTP 403 | Glory Vision Tanzania (tie unconfirmed) |
| visibleimpact.org project page | redirects to the home page of a platform "closed to the public" | FRI-SUCODE |

## Unreadable, gone or hijacked

- **Own sites gone (non-existent domains):** macao-tz.org and brightmediumschool.org (MACAO), masolafoundation.org (Masola Foundation).
- **Own site unreachable today:** thv.or.tz (Tanzania Host Volunteer): DNS server failure at the local and public resolvers, twice. Retry later for its leaders.
- **Hijacked:** kujengana.org (Kujengana Network) now serves a Turkish gambling site; nothing was used. The Trickle Out Africa directory page on MACAO carries an injected casino link; its phone and P.O. Box were not used.
- **Other failures:** victoryprogramme.org HTTP 500 and womenandchildrenfoundation.org unresolvable (namesakes of organisation 1); zoomtanzania.com unresolvable (MACAO listing); embuanfoundation.org non-existent (a namesake of ECYF).
- **Encoding:** milelo.de pages were decoded with the wrong character set by the reader (mojibake); names and quotes were written with the intended characters.

## Domains tried directly (no search)

- africanmoons.org: the US parent of African Moons Tanzania (confirmed by its projects). africanmoonsusa.org/.com and africanmoons.com do not exist.
- partnerschaft-fuer-afrika.de: TRMEGA's funder named in the register (read); time2help.org is an unrelated Ukrainian organisation; time2help.de does not exist.
- gloryvision.or.kr: HTTP 403. gloryvision.org/.kr, gloryvisiontz.org and gloryvision.or.tz do not exist.
- unitedwechangelives.org/.com/.or.tz and uwcl.or.tz do not exist; uwcl.org is United Way of Central Louisiana (unrelated).

## Organisations not reached

None. Every organisation had at least one search, and the three best child-focused gaps had a second (Q35-Q37).

## For a person to check

1. **MACAO:** its own 2014 listing places its orphanage and school near Loliondo (Ngorongoro), far outside the catchment, though the register pins it near Arusha; both its domains are gone. Check its location and whether it still operates.
2. **Kujengana Network:** its old site is hijacked; the search snippet placed its work in Kyela district (southern Tanzania). Location to check.
3. **FRI-SUCODE:** its phone, inbox and P.O. Box come from a 2017 letterhead; confirm they are current.
4. **Bassari:** the Tanzanian inbox is a Gmail address named after the organisation (personal domain, drafts held); its other routes are the German parent's.
5. **MILELO Tanzania and African Moons:** their routes belong to foreign support or parent bodies (a German inbox and mobile; the US founders' inbox and phones). Sally Bruton Vann's inbox is a personal Gmail, so her lead is marked risky.
6. **Segment:** MILELO Tanzania runs a free primary school in Kijenge with English from Grade 1, and Young Minds runs a day-care and pre-school ("Better Tomorrow"). Both are schools rather than welfare programmes.
7. **Incomplete names:** Young Minds' Education Director appears only as "Godfrey", and the entry's text uses another first name. Son and Oscar's co-founder appears only as "Mr. Son" in the register.
8. **Le Solstice:** after the HTTP 429, retry its contact page in a later session. The Huruma Orphanage it finances (Nshupu, near Usa River; also backed by TerraWatu and Worldview Education and Care) is not a record of its own in the welfare run.
9. **Shalom safeguarding:** African Moons funds "Shalom Centre Orphanage" in the Arusha region. The welfare run holds "SHALOM CENTRE FOR STREET CHILDREN" (register) and "Shalom Center (Kisongo)", whose source is a JamiiForums thread with an allegation in its title. It is not verified whether these are the same centre. Check before any outreach that touches Shalom.
10. **Possible new welfare leads outside this slice, not in the welfare run:**
    - Ereto East Africa Foundation (eretoea.org, Sekei, Arusha): English-medium pre-primary and primary schools for orphans and vulnerable children. It is not Meshack Ereto Foundation.
    - Safe Home for Children with Disabilities: a registered NGO funded by African Moons.
    - Huruma Orphanage (Nshupu).
11. **Glory Vision Tanzania** is very active by the register (remedial classes, daily food, a library and home visits for about 100 children, funded by Glory Vision Corporation in Korea) but has no public route. The Korean site answered 403.
12. **TRMEGA:** its funder's partner page names its current head and project manager. They were not recorded because it is a funder's page; decide whether that source may be used.
13. **GenTech:** its footer also shows info@gentechfoundation.com, but that domain belongs to a US namesake in Phoenix; only the .org inbox was recorded.

## Next-run priorities

- Child-focused organisations still without a route: Glory Vision Tanzania, Wings Children Foundation, Watoto Future Initiatives, Ejung'o, Stable Life for Tanzania Kids, Kingdom Childcare, Meshack Ereto, St. Simon Tomorrow Return of Hope, Child & Youth Development Center - DLBC, TRMEGA, Son and Oscar (lead only) and MACAO (lead only).
- Retry thv.or.tz (leaders) and lesolstice.org's contact page (after the 429).
- Possible sources: district social welfare offices and the register's own contact channel. The organisations' Facebook pages cannot be read under the current rules (login wall).
