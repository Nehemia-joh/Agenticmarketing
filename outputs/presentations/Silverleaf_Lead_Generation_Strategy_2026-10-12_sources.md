# Sources and queries: Partnership Lead Strategy deck, 12 October 2026

Deck: `outputs/presentations/Silverleaf_Lead_Generation_Strategy_2026-10-12.pptx` (44 slides: a main body of 30, an appendix divider, appendix slides A1â€“A12 and a closing slide), built on the master, layout, theme and media of `outputs/presentations/Silverleaf_Lead_Generation_Progress_2026-09-10_redesign.pptx`.

Every number in the deck comes from one of the queries or files below. No person's name, email address or phone number appears in the deck; sample messages use placeholders (`<Full Name>`, `<Role>`, `<Organisation>`, `<Sender name>`). Nothing is sent from the repository.

## Slide map

| Slides | Content |
|---|---|
| 1â€“3 | Title, agenda, executive summary |
| 4â€“9 | Section 01: catchment and lead capture (lead-map link in the footer of 3 and 5â€“9) |
| 10â€“16 | Section 02: segments and confidence |
| 17â€“25 | Section 03: drafting the first touch |
| 26â€“29 | Section 04: pipelines: the spine (27), after the offer (28), tracking and reporting (29); pipeline-page link in the footer |
| 30 | Next steps (both links) |
| 31 | Appendix divider |
| A1â€“A7 | Overview and parent-funnel hand-off; funnels E1â€“E6, I1, W1â€“W3, G1â€“G3 |
| A8â€“A11 | Fallout and re-activation; opt-in and data protection; pipeline decisions (two slides) |
| A12 | Sources and data dates (both links, absolute and relative) |
| Closing | Both links |

## Data snapshot

Read-only copies of the three databases, taken from the main checkout on 12 October 2026 (files last written 00:39â€“00:41 that day, at commit 262f535) and opened with `mode=ro`:

| Database | Path in the main checkout |
|---|---|
| Master | `outputs/master/Silverleaf Master Database.sqlite` |
| Welfare run | `outputs/runs/arusha-welfare-2026-09/lead-database.sqlite` |
| Government run | `outputs/runs/arusha-government-2026-09/lead-database.sqlite` |

The lead map was rebuilt from those copies to a scratch file with `python scripts/maps/build_lead_map.py --out <scratch>`; its counts and payload matched the committed `outputs/maps/Silverleaf Lead Map.html` (built 2026-10-12) exactly, and its own checks passed (counts match the databases and the exporter; no contact data in the page).

Confidence, first-touch and segment counts reuse the repository's own rules: `scripts/messaging/export_resend_contacts.py` (`company_rows`, `welfare_rows`, `dedupe`, `government_rows`, `first_touch_case`), `scripts/messaging/build_company_audience_profile.py` (`kind_of`) and `scripts/messaging/first_touch.py` (`ROUTING_START`, `is_redirect`).

## Queries and the figures they give

### Records and leads (slides 1, 3, 11)

```sql
-- master, welfare, government: organisation records (1,376 + 503 + 228 = 2,107)
SELECT COUNT(*) FROM organisations;
-- welfare out of scope (58)
SELECT COUNT(*) FROM organisations WHERE segment = 'Out of scope';
-- master leads with a chosen first message (1,251 = 1,118 companies + 117 SACCOS + 16 introducers)
SELECT segment, COUNT(*), SUM(review_status = 'Draft review') FROM outreach_plans
 WHERE selection = 'Candidate for review' GROUP BY segment;
-- welfare leads by kind and priority (445; 86 draft_ready)
SELECT o.segment, o.priority, COUNT(*), SUM(p.review_status = 'draft_ready')
  FROM outreach_plans p JOIN organisations o USING (organisation_id)
 WHERE p.target_type = 'organisation' GROUP BY 1, 2;
-- government offices by level (council 9, district 7, region 3, ward 129, village 80)
SELECT office_level, COUNT(*) FROM government_office_profiles GROUP BY 1;
SELECT review_status, acquisition_track_id, COUNT(*) FROM outreach_plans GROUP BY 1, 2;  -- 4 GA01 ready, 224 GA00
```

1,924 leads = 1,251 master + 445 welfare + 228 government. The 183 records set aside are 125 master duplicates or records without a plan and 58 welfare out-of-scope entries (lead map builder summary).

### Map and distance bands (slides 1, 3, 5, 7)

From the lead map payload (`DATA.leads`: organisation name, segment, map point, nearest campus and straight-line km; no person data): 1,864 leads drawn, 60 unmapped; bands by `km` (0â€“5, 6â€“10, 11â€“15, 16â€“20, 21â€“25, beyond 25), per segment:

| Segment | 0â€“5 | 6â€“10 | 11â€“15 | 16â€“20 | 21â€“25 | >25 |
|---|---|---|---|---|---|---|
| Employers | 768 | 131 | 46 | 64 | 177 | 35 |
| Introducers | 9 | 0 | 0 | 0 | 1 | 0 |
| Welfare | 220 | 44 | 20 | 19 | 89 | 20 |
| Government | 50 | 43 | 40 | 38 | 46 | 4 |

Within 25 km: 1,805. Unmapped: welfare 33 (30 funders with no local point), employers 14, government 7, introducers 6. The static map on slide 5 is drawn offline from this payload and `data/reference/maps/arusha-catchment-basemap.geojson` (OpenStreetMap, ODbL); it draws dots only, no names.

Campus points: `SELECT name, latitude, longitude, geocode_basis FROM campuses;` (website pins, read 2026-10-11).

### Employer subsegments (slides 12, A2â€“A4)

```sql
SELECT p.segment, o.subtype, p.review_status, p.message_variant, r.tier
  FROM outreach_plans p JOIN organisations o USING (organisation_id)
  LEFT JOIN employer_reach r USING (organisation_id)
 WHERE p.selection = 'Candidate for review';
SELECT tier, COUNT(*) FROM employer_reach GROUP BY 1;            -- P1 100, P2 150, P3 853, X 15
SELECT message_variant, COUNT(*) FROM outreach_plans
 WHERE selection = 'Candidate for review' GROUP BY 1;            -- A 14, B 1,104, introducer 16, n/a 117
```

Kind = `build_company_audience_profile.kind_of`; the Corporate employers segment (152) is split by `organisations.subtype` into Manufacturing 19, Retail 17, Farms and estates 14, International organisations 10, Aviation 5 and Banks and other companies 87, as in the pipeline document. Leads (ready): safari 480 (432), hotels 194 (123), hospitals 188 (37), banks 87 (70), NGOs 62 (28), colleges 23 (19), public bodies 19 (12), manufacturing 19 (11), retail 17 (6), farms 14 (3), international 10 (9), aviation 5 (2); total 1,118 (752). SACCOS subtypes: employer-based 48, community 67, map-only 2. Introducer kinds from `organisations.segment` ('Introducer: â€¦'): chambers 3, employers' associations 5, sector associations 6, HR body 1, other 1.

Per-funnel first-touch bands on slides A2â€“A7 (high-direct / high-indirect / medium / low / no email) come from `company_rows` and `welfare_rows` after `dedupe`, grouped by the same kinds.

### Confidence and Resend segments (slides 1, 3, 15, 16)

`company_rows(master)`, `welfare_rows(welfare)`, `dedupe(...)`: companies high-direct 36, high-indirect 228, medium 349, low 52; introducers 4 / 8 / 3 / 0; welfare 14 / 55 / 10 / 117; no email: companies 569 (453 companies + 116 SACCOS), welfare 233; shared addresses exported once: 18. These equal `outputs/messages/Silverleaf Resend Segments - 2026-10-12.md`.

Slide 16 shows the high-direct and high-indirect split by track (companies 36 / 228, introducers 4 / 8, welfare 14 / 55). Earlier exports, for reference only: `Silverleaf Resend Segments - 2026-10-06.md` (255 high, no direct/indirect split), `- 2026-10-10.md` (high-direct 28 + 2 + 11 = 41; high-indirect 203 + 10 + 55 = 268), `- 2026-10-12.md` (54 and 291).

Government: `government_rows(gov, '2026-10-12')`: high 4 (pilot councils), low 224; ward waves 58 / 35 / 32 / 4 to locate; village waves 29 / 41 / 10; 11 offices with an official inbox; villages by council: Hai 36, Meru 34, Arusha District 9, Arusha City 1.

### First-touch cases (slides 3, 19, 20, 25)

Each email row's `message_body` read by its first line (`first_touch.ROUTING_START` â†’ case B; `first_touch.is_redirect` â†’ case C; otherwise case A), before `dedupe`: companies A 40, B 246, C 380; introducers A 4, B 8, C 4; welfare A 19, B 154, C 39. Totals A 63, B 408, C 423. Case B drafts with ', or your HR lead.' in the routing line: 48 (companies). Master case B plans: 254; with follow-up 1 and the close (`first_touch.CLOSE_END` in `follow_up_2`): 247. Welfare plans with a follow-up 2 message: 154. Master plans recording an escalation contact: 8.

### Hooks (slide 23)

```sql
SELECT hook_status, hook_type, COUNT(*) FROM outreach_plans WHERE selection = 'Candidate for review' GROUP BY 1, 2;
-- Verified <date> 103; Removed (exact claim not independently verified) 354; No hook 794
SELECT COUNT(*) FROM outreach_plans WHERE target_type = 'organisation' AND COALESCE(hook_source_url, '') <> '';  -- welfare 67
```

### Lead capture: eight sources (slide 9)

| # | Source | Figure on the slide | Feeds | Query or file |
|---|---|---|---|---|
| 1 | TATO (Tanzania Association of Tour Operators member list) | 467 member companies in the company list | Companies | `SELECT COUNT(*) FROM organisations WHERE source_url LIKE '%tatotz%';` (master; 421 are chosen leads) |
| 2 | TCDC (Tanzania Cooperative Development Commission, the regulator of cooperatives; its licensed-SACCOS list, ushirika.go.tz) | 115 licensed savings groups | Companies (savings groups) | `SELECT subtype, COUNT(*) FROM organisations WHERE segment = 'Savings group' GROUP BY 1;` TCDC licence classes A and B: 61 + 6 + 38 + 10 = 115; 2 more are OpenStreetMap-mapped (117 SACCOS in all) |
| 3 | OpenStreetMap | 406 employers placed; 85 government points | Companies, Government | `SELECT COUNT(*) FROM organisations WHERE COALESCE(osm_id,'') <> '';` master 406, government run 85 |
| 4 | Company website deep crawl | emails on 507 of 627 sites; named people on 217 | Companies, Welfare | `docs/methodology/research-playbook.md`, finding 1 |
| 5 | Google Maps | 333 of 497 lookups accepted (pin, address or phone) | all three | `python scripts/research/ledger.py stats --by tool` (gmaps: 497 attempts, 333 hit); the four enrichment rounds are 391 of them (248 accepted) |
| 6 | NGO register (NGOs Information System) | 898 entries read; 285 match a welfare lead | Welfare | `SELECT COUNT(*) FROM registry_ngos;` and `SELECT COUNT(DISTINCT matched_organisation_id) FROM registry_ngos WHERE COALESCE(matched_organisation_id,'') <> '';` (welfare run) |
| 7 | Council data (council websites and official sources) | 148 offices: 9 councils, 7 districts, 3 regions, 129 wards | Government | `SELECT office_level, COUNT(*) FROM government_office_profiles GROUP BY 1;` (the 80 villages come from OpenStreetMap, source 3) |
| 8 | Automated and manual searches | 1,960 web searches across 1,002 organisations, including the companies the team named | all three | `ledger.py stats --by tool` (websearch: 1,960 attempts); `research-playbook.md` (1,002 organisations searched); 14 team-named employers in `data/raw/gap-census/google_maps_user_named_2026-10-11.jsonl`, 51 named leads located (commit 4c065ae) |

Lists on the slide: companies 1,251 (1,118 companies, 117 savings groups, 16 introducers), welfare 445, government 228.

### Known gaps (slide 8)

```sql
-- companies and savings groups (chosen leads) by location precision: town 48 + city 177 = 225 placed only to a town or city centre
SELECT COALESCE(o.geocode_precision, '(none)'), o.latitude IS NOT NULL, COUNT(*)
  FROM outreach_plans p JOIN organisations o USING (organisation_id)
 WHERE p.selection = 'Candidate for review' AND p.segment <> 'Introducers' GROUP BY 1, 2;
-- no nearest campus recorded: 30 (all have a locality or address); no map point: 11
SELECT COUNT(*) FROM outreach_plans p JOIN organisations o USING (organisation_id)
 WHERE p.selection = 'Candidate for review' AND p.segment <> 'Introducers' AND COALESCE(o.campus, '') = '';
```

The Catchment Criteria (11 October) gives 440 companies on a distance computed from the earlier campus points and 'about 50' without a nearest campus; the slide uses today's counts (225 town- or city-level placements, 30 without a campus) and keeps the earlier-points caveat without a number, because later recomputes changed it.

### Welfare and government (slide 14)

Welfare bars: high / medium / low and ready per kind, from the welfare run query above (residential 23 / 20 / 57, ready 17; family-based 12 / 14 / 138, 25; specialised 3 / 6 / 61, 5; funders 3 / 7 / 94, 34; networks 0 / 0 / 7, 5), drawn to scale. Government ladder: councils 9 (4 pilot), district and regional 10, wards 129, villages 80; ward waves 58 / 35 / 32 / 4.

### Documents (wording, rules and decisions)

- `outputs/messages/Silverleaf Catchment Criteria - 2026-10-11.md` (catchment, bands, segment rules, corrections, gaps, take-aways)
- `outputs/messages/Silverleaf Core Segments - 2026-10-11.md` (definitions and the recipient rule; its counts are superseded)
- `outputs/messages/Silverleaf Employer Sponsorship Drafts - 2026-10-02.md`, `Silverleaf Welfare Drafts - 2026-10-10.md`, `Silverleaf Government Drafts - 2026-10-11.md`
- `docs/strategy/partnership-pipelines.md` (approved 12 October 2026: spine, funnels, first touch, fallout, incentives, tracking, metrics and the 22 decisions), and its review page `outputs/strategy/Silverleaf Partnership Pipelines.html`
- `scripts/messaging/first_touch.py` (Attn and redirect templates, the six redirect wordings, the close and escalation note, `hr_lead`)
- `data/reference/silverleaf-offer-register.json` and `skills/silverleaf-outreach/references/offer-register.md` (version 2026-10-13-offer-v6, OF07 open to savings groups; terms from Silverleaf's 2025 Proposed Fees & Discounts schedule, "Summary of discounts offered"; Finance checks them before the first send)
- `docs/strategy/hook-guidance.md`; `docs/methodology/research-playbook.md`

## Conflicts resolved

- **Core Segments (11 Oct morning) counts are stale.** Replaced by today's counts: 1,118 companies (not 716), 445 welfare in scope (not 444), 228 government offices (not 150; the gap census added 80 villages), high-direct employers 36 (not 29), employers without email 569 including SACCOS (not 229).
- **Pipeline document section 4 band-by-case table** (evening of 11 Oct: 34 / 221 / 360 â€¦) is superseded by the case counts above.
- **Ward waves**: Core Segments 55 / 33 / 31 / 12 and the pipeline document 57 / 35 / 32 / 5 are superseded by 58 / 35 / 32 / 4.
- **Employer distance table in the Catchment Criteria** (505 / 64 / 60 / 37 / 50 businesses, the 716-company list and stored distances) is replaced on slide 7 by the lead map's straight-line bands for all 1,924 leads; the rules themselves are unchanged.
- **Variants**: the pipeline document's 'B 1,079, not assigned 25' is now B 1,104 (the 25 new leads have a variant).
- **Total records**: the brief's 'about 2,109' is 2,107 records today (1,376 + 503 + 228); 1,924 of them are leads with a first message.
