# Slice Y coverage log: stratified enrichment round, 2026-10-10

Goal: more data points per welfare lead (named leader, direct route, any route, address, register number, size, founding
year, escalation contact, sourced education angle), stratified by segment (homes, programmes, specialised centres, funders,
networks) and priority (High = P1, Medium = P2, Low = P3/P4). Output:
`data/raw/welfare-research/research_Y_welfare_enrichment_2026-10-10.jsonl` (19 records: 12 organisation, 7 contact). Reviewed decisions in `data/runs/arusha-welfare-2026-09/links.json`: four NGO-register links (`nis_to_org`), three
`flags_cleared` through `apply_research_reviews.py`, one `geo_overrides` (The Bandari Project, Mto wa Mbu).

The table is measured by `scripts/welfare/measure_welfare_coverage.py` (new; read-only). Baseline: the run as built before this
round (main checkout's `lead-database.sqlite` SHA-256 `f403851927bc…` and its `final.json`). Out-of-scope records (58) are
not counted. "Leader recorded" needs a named person (two or more name words) with a leader's role and a confirmed role
certainty; "Addressed by name" is the draft's addressee under the recipient rule; "Direct email" is the addressee's own address
or a role inbox on the organisation's own domain; "Hook" is a sourced hook in the plan or the published schooling arrangement.

## Baseline (before)

| Segment | Priority | n | Leader recorded | Addressed by name | Direct email | Any email | Phone | No route | Address | Geocode: point | Geocode: locality | Website | Socials | NGO reg. no. | Size | Founded | Escalation | Hook / education angle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Homes | High | 22 | 22 | 20 | 9 | 21 | 10 | 1 | 18 | 3 | 15 | 21 | 16 | 12 | 22 | 20 | 2 | 22 |
| Homes | Medium | 20 | 11 | 9 | 4 | 12 | 14 | 4 | 16 | 1 | 7 | 16 | 11 | 2 | 19 | 17 | 0 | 18 |
| Homes | Low | 57 | 21 | 20 | 16 | 24 | 22 | 28 | 29 | 3 | 16 | 30 | 28 | 19 | 18 | 16 | 1 | 20 |
| Programmes | High | 12 | 10 | 9 | 4 | 10 | 10 | 2 | 10 | 2 | 7 | 10 | 9 | 8 | 12 | 12 | 1 | 12 |
| Programmes | Medium | 12 | 8 | 6 | 4 | 8 | 6 | 3 | 8 | 4 | 3 | 9 | 5 | 4 | 10 | 7 | 0 | 10 |
| Programmes | Low | 135 | 34 | 34 | 26 | 35 | 33 | 97 | 24 | 79 | 5 | 45 | 33 | 118 | 4 | 8 | 4 | 20 |
| Specialised centres | High | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 2 | 0 | 0 | 2 | 2 | 2 | 2 | 2 | 0 | 2 |
| Specialised centres | Medium | 7 | 4 | 4 | 2 | 3 | 5 | 2 | 5 | 1 | 2 | 6 | 5 | 0 | 7 | 5 | 0 | 3 |
| Specialised centres | Low | 61 | 19 | 18 | 13 | 19 | 17 | 42 | 17 | 7 | 6 | 24 | 23 | 47 | 4 | 5 | 0 | 5 |
| Funders | High | 3 | 3 | 3 | 2 | 3 | 3 | 0 | 3 | 0 | 2 | 3 | 3 | 2 | 3 | 1 | 0 | 3 |
| Funders | Medium | 7 | 7 | 6 | 4 | 7 | 3 | 0 | 5 | 2 | 3 | 7 | 7 | 2 | 5 | 4 | 0 | 7 |
| Funders | Low | 94 | 79 | 76 | 47 | 69 | 64 | 11 | 64 | 9 | 6 | 80 | 60 | 12 | 0 | 13 | 3 | 62 |
| Networks | Low | 7 | 6 | 6 | 7 | 7 | 6 | 0 | 7 | 0 | 2 | 7 | 2 | 1 | 0 | 4 | 2 | 0 |
| All |  | 439 | 226 | 213 | 140 | 220 | 195 | 190 | 208 | 111 | 74 | 260 | 204 | 229 | 106 | 114 | 13 | 184 |

## After

| Segment | Priority | n | Leader recorded | Addressed by name | Direct email | Any email | Phone | No route | Address | Geocode: point | Geocode: locality | Website | Socials | NGO reg. no. | Size | Founded | Escalation | Hook / education angle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Homes | High | 22 | 22 | 20 | 9 | 21 | 10 | 1 | 19 | 3 | 15 | 21 | 17 | 13 | 22 | 21 | 3 | 22 |
| Homes | Medium | 20 | 11 | 9 | 4 | 12 | 14 | 4 | 16 | 1 | 7 | 16 | 11 | 2 | 19 | 17 | 0 | 18 |
| Homes | Low | 57 | 21 | 20 | 17 | 24 | 22 | 28 | 29 | 3 | 16 | 30 | 28 | 19 | 18 | 16 | 1 | 20 |
| Programmes | High | 12 | 10 | 9 | 4 | 10 | 10 | 2 | 10 | 2 | 7 | 10 | 9 | 9 | 12 | 12 | 1 | 12 |
| Programmes | Medium | 12 | 8 | 6 | 4 | 8 | 6 | 3 | 8 | 3 | 3 | 9 | 6 | 4 | 10 | 7 | 0 | 10 |
| Programmes | Low | 135 | 34 | 34 | 26 | 35 | 33 | 97 | 24 | 79 | 5 | 45 | 33 | 118 | 4 | 8 | 4 | 20 |
| Specialised centres | High | 3 | 3 | 3 | 2 | 2 | 2 | 1 | 2 | 0 | 0 | 2 | 2 | 2 | 3 | 2 | 0 | 3 |
| Specialised centres | Medium | 6 | 3 | 3 | 2 | 3 | 5 | 1 | 5 | 1 | 2 | 6 | 5 | 0 | 6 | 5 | 0 | 5 |
| Specialised centres | Low | 61 | 19 | 18 | 13 | 19 | 17 | 42 | 17 | 7 | 6 | 24 | 23 | 48 | 4 | 6 | 0 | 5 |
| Funders | High | 3 | 3 | 3 | 2 | 3 | 3 | 0 | 3 | 0 | 2 | 3 | 3 | 2 | 3 | 1 | 0 | 3 |
| Funders | Medium | 7 | 7 | 6 | 4 | 7 | 3 | 0 | 5 | 2 | 3 | 7 | 7 | 3 | 5 | 4 | 0 | 7 |
| Funders | Low | 94 | 79 | 76 | 48 | 70 | 64 | 11 | 65 | 9 | 6 | 80 | 60 | 12 | 0 | 13 | 3 | 62 |
| Networks | Low | 7 | 6 | 6 | 7 | 7 | 6 | 0 | 7 | 0 | 2 | 7 | 2 | 1 | 0 | 4 | 2 | 0 |
| All |  | 439 | 226 | 213 | 142 | 221 | 195 | 190 | 210 | 110 | 74 | 260 | 206 | 233 | 106 | 116 | 14 | 187 |

Stratum moves: Safe Home for Children with Disabilities rose from Medium to High (its new, sourced schooling statement adds a
priority factor). Counts by organisation:

- Tupendane Orphanage (Homes, High): founding year (registered 2022) and official Instagram, from its own About page; its
  "244 children supported in early childhood education" is in the notes.
- ProManity International (Homes, High): association address (Hamburg Impressum, VR 23524); Agnes Masaki, who "leitet das Pippi
  House als Supervisor", is now the addressee as the head of the home on the ground, with the managing director Franziska Diet as
  escalation contact; Rev. Aristides Nshange recorded as founder of the Pippi House.
- LOHADA (Homes, High), WEHAF (Programmes, High), Africa Amini Alama (Funders, Medium), Eripoto Safe House (Specialised, Low):
  NGO register numbers through reviewed `nis_to_org` links (00NGO/R/2599, 00NGO/R1/0074, I-NGO/R2/000538, 00NGO/R/2814).
- Safe Home for Children with Disabilities, Mkombozi, Kilimanjaro Centre for Orphans and Street Children (Specialised): a sourced
  education angle each (Daily News 25 Aug 2026; the centres' own Idealist listings).
- Habari Foundation International (Funders, Low): its contact page publishes sarap@ (the executive director's mailbox on its
  domain); the draft's route moved from a US phone to that address and the draft is now ready for review.
- Tumaini Home Organization (Homes, Low): staanda@tumaini-home.no, the general secretary's address on the organisation's domain,
  is now the route instead of the gmail inbox.
- ELCT (Funders, Low): Secretary General Rogath Lewis Mollel (the church's CEO, management-team page). The drafting rule now
  addresses him rather than the Presiding Bishop; the bishop's own address stays on file.
- Wevol Inc (Funders, Low): postal address PO Box 17593, Boulder, CO 80308.
- The Bandari Project (Programmes, Medium): official Facebook, Instagram and YouTube, Australian ABN 27 924 597 634, staff count;
  its stale flag "no website or published contact route found" cleared, and its location corrected to Mto wa Mbu (its own About
  page) through a geo override, so it stays held as outside the 25 km catchment (the register pin near Kijenge is its office).
- The Small Things (Funders, High): its own Idealist volunteer listing dated 4 May 2026 clears "no dated activity found after
  2017"; it stays held because its website still renders no text. Volunteer inbox mariam@thesmallthings.org recorded.
- Seeway Tanzania (Homes, Medium): "no website found" cleared (swtz.org read); a partner school dates activity to January 2024;
  "no current evidence" left for a reviewer. Seeway sends all primary-aged children to private school but publishes no email or
  phone (contact form only).
- Kao La Amani (Homes, High), Eripoto: school size and expansion (about 235 pupils, plans for about 300), staff 13 and 40+ residents,
  recorded in notes and blank fields.
- Building a Caring Community (Specialised, Medium): Pastor Anna Makyao, "BCC Coordinator", seen only as the title of a partner
  (Mosaic International) article; the page answered 404/403, so she is recorded with role certainty "unknown" and not counted.

## Deterministic sources (no search budget)

- `crawl_org_websites.py --date 2026-09-23 --reextract` (offline, from the shared HTTP cache): no new welfare data point beyond
  what the run already holds (one heading read as a person; one office administrator at KIWAKKUKI). The re-extracted file was not
  kept, so the shared crawl file is unchanged.
- Crawl of the 54 welfare websites the 2026-09-23 crawl never reached (20) or could not read (34), with the crawler's own
  `crawl()` into a worktree-local cache: 20 sites read (among them meshasvillage.com, ujamaachildren.org,
  samaritanvillageorphanage.org, tupendaneafricafoundation.or.tz, thebandariproject.com, cssc.or.tz, elct.or.tz, elctncd.or.tz,
  tumaini-home.no, wevol.org, habarifoundationinternational.org, eretoea.org); 34 still unreadable (below).
- `scripts/contacts/read_page.py` on the organisations' own pages, impressum and contact pages of the High and Medium gaps.
- NGO register: the catchment cache (fetched 2026-09-22, under 90 days old) was reused; nothing refetched. Name matching of the
  High/Medium (and Low) organisations without a register number against the 898 catchment entries gave four supported links.
- OpenStreetMap: `collect_osm_contacts.py` re-run for 2026-10-10 (two Overpass queries, overpass-api.de): no new route or tag for
  any welfare organisation; the extract was not kept.
- Charity registers: ProPublica (From Hearts 2 Hands, EIN 83-3466880, Palm Bay FL: nothing new to record); UK Charity Commission
  blocked (below).

## Searches: 29 of 65 used

| # | Stratum | Query (shortened) | Result |
|---|---|---|---|
| Q1/65 | Homes High | "Light in Africa" children's home Moshi contact | no route; a US partner (Asante Sana) named |
| Q2/65 | Homes High | "Kao La Amani" children's village contact | Article 25 project pages (school about 235, plans 300) recorded |
| Q3/65 | Homes High | "Tumaini for Africa" orphanage Arusha director | no match |
| Q4/65 | Homes High | "Enyorata" children's home Arusha phone/email | no match |
| Q5/65 | Homes High | Laketatu orphanage Arusha | no match |
| Q6/65 | Programmes High | "Green Path for Community Success" director | no match |
| Q7/65 | Specialised Medium | Mkombozi executive director 2025 | only the founder from 2005 (historical); not recorded |
| Q8/65 | Homes High | "Hope Home Trust" Kitaa Moshi contact | UK register entry (blocked, 403); no Tanzanian route |
| Q9/65 | Specialised Medium | "Safe Home for Children with Disabilities" | Daily News 25 Aug 2026 (education angle recorded) |
| Q10/65 | Homes Low | Huruma orphanage Nshupu Usa River | another Huruma home (Arusha); identity not confirmed, not recorded |
| Q11/65 | Homes Medium | "Havilah Children's Village" founder | no match (a Kenyan home) |
| Q12/65 | Programmes Medium | "New Stars Foundation" Arusha director | no match |
| Q13/65 | Homes High | Enyorata / Little Souls (Facebook, Instagram) | no match |
| Q14/65 | Specialised Low | "Eripoto" Arusha email or phone | no route; partner Lutheran Partners for Global Ministries |
| Q15/65 | Homes High | Ujamaa Children's Home (Facebook) | page found, no phone in the result |
| Q16/65 | Homes Low | "St Gemma Galgani" school Mateves contact | no match |
| Q17/65 | Funders Medium | "From Hearts 2 Hands" EIN | EIN 83-3466880 (ProPublica); nothing new for the table |
| Q18/65 | Funders High | "Mesha's Village" contact email | no match |
| Q19/65 | Specialised Medium | "Building a Caring Community" Moshi director | Mosaic article title naming a coordinator (snippet only) |
| Q20/65 | Funders Medium | "Arusha Kids Trust" trustees | no match |
| Q21/65 | Networks Low | "Tanzania Child Rights Forum" contact | IATI entry (404 when read); nothing recorded |
| Q22/65 | Homes Low | "Matonyok" children's home | fundraising pages only; no route |
| Q23/65 | Funders High | "The Small Things" founded year | Idealist listing dated 4 May 2026 (activity recorded) |
| Q24/65 | Homes (all) | Idealist: Arusha children's home email | Good Hope listing (2012 facts already held); four Arusha NGOs not in the run |
| Q25/65 | Specialised Medium | Idealist: Moshi orphanage centre email | Kili Centre listing (education angle recorded) |
| Q26/65 | Homes Medium | Idealist: Usa River / Arumeru orphans | Tabasamu listing (address detail; already held); Neema International |
| Q27/65 | Programmes Low | Idealist: Arusha education sponsorship NGO | five Arusha NGOs not in the run (see report) |
| Q28/65 | Homes Medium | Seeway Tanzania SWTz email | partner school reports (activity Jan 2024); no route |
| Q29/65 | Specialised Medium | Idealist: Arusha disabled children centre | Mkombozi listing (education angle recorded) |

Split by stratum: Homes High 8, Homes Medium 3, Homes Low 3, Programmes High 1, Programmes Medium 1, Programmes Low 1,
Specialised Medium 6, Specialised Low 1, Funders High 2, Funders Medium 2, Networks 1. Funders Low and Specialised High had no
search of their own: their gaps were filled from pages already in hand (Habari, Tumaini Home, ELCT, Wevol) or are escalation-only.

36 searches left unspent. Almost every remaining gap organisation was already searched once or twice in earlier rounds, and the
search index returns nothing for most small Tanzanian homes by name; the one productive pattern (organisations' own Idealist
listings) mostly surfaced organisations that are not in the run.

## Blocked or unreadable (not worked around)

- UK Charity Commission register: read timed out to the page reader; HTTP 403 to WebFetch (Hope Home Trust, 4042379).
- mosaicinfo.org article on BCC: HTTP 404 to the page reader, 403 to WebFetch.
- HTTP 429: lesolstice.org (about, contact), hopehometrust.org.uk (contact, staff, history), bahatitrust.com.
- HTTP 202 challenge pages (treated as bot checks): tirnanogchildrensfoundation.com, selflesssolutions.org, farajaschool.org,
  liftedstrong.org.
- HTTP 403: furahiafoundation.org, wvi.org, liaisongroup.com. HTTP 522: buildingacaringcommunity.org.
- TLS failure: theholyspiritsisters.org (Sun of Hope), malaika-childrenfriends.org (certificate), elctdme.or.tz (certificate).
- Domain does not resolve: karimchildren.org, stjosephorphanage.co.tz, goodhopeorphanage.org, matonyokchildrenshome.org,
  goodhopekiwawa.org, jerichome.org, kcyc.or.tz, osiligichildrenfoundation.org, esperofoundationtz.org, seedsofkindness.or.tz,
  kilicentre.org, acv3.org, passioniststanzania.or.tz, peacehouseafrica.org, disabilityreprolight.org.
- Connection refused or timed out: tcrfnet.org, utopiafoundation.org, kwieco.org, cradleoflove.com.
- robots.txt disallows (crawler skips; a browser read would be tagged risky): sibusiso.com, afroplanfoundation.com,
  samequalitiesfoundation.org.

## Needs a browser read (script-built pages that return no text)

saintmarkskids.org (St. Mark's, Usa River; still no route), thesmallthings.org, stgemma.org (St. Gabriel Home), mkombozi.org,
childrightsforum.org (TCRF's new site), eripoto.org/contact (form only), hopeandsoul.org.uk, arushakidstrust.com (429), and the UK
Charity Commission register.

## Not reached

No-route High/Medium organisations still without a route: St. Mark's (Usa River), Ngarasero, POSA, Karim (domain gone), Cradle
of Love (closed 2024), Seeway (form only), HopeCare, Mother Kevina, Bahath, TAG Kilimanjaro, Safe Home for Children with
Disabilities, BCC. Programmes Low (97 without a route) are mostly register-only NGOs searched once before; not searched again.
