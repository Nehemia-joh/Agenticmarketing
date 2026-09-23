# Government-lead data contract

This extends the shared contract in `../../silverleaf-create-lead-list/references/lead-list-data-contract.md`. A government run uses the shared intake columns plus the extra columns below. The create skill's validator accepts extra columns, and its initializer keeps them in `source_records.payload_json`. Offices are `organisation` rows and official posts are `contact` rows; there are no `enquiry` rows.

## Office levels

| `office_level` | Office | Segment | Posts recorded |
|---|---|---|---|
| `region` | Regional Secretariat (Regional Commissioner's office) | Local government office: region | Regional Commissioner (political appointee), Regional Administrative Secretary, community development unit, education section (B2G check) |
| `district` | District Commissioner's office (administrative district, e.g. Arumeru covers Arusha District and Meru councils) | Local government office: council or district | District Commissioner (political appointee), District Administrative Secretary |
| `council` | Halmashauri: city, municipal or district council | Local government office: council or district | Council Director, Council Chairperson or Mayor (elected), heads of Community Development, Social Welfare, and Pre-Primary and Primary Education (B2G check) |
| `ward` | Ofisi ya Kata | Local government office: ward, village or mtaa | Ward Executive Officer, Ward Councillor (elected), Ward Community Development Officer |
| `village` | Ofisi ya Kijiji, where mapped | Local government office: ward, village or mtaa | Village Executive Officer, Village Chairperson (elected) |

Ward offices are created for every ward within `catchment_km` of a campus, and for every ward of a `core` council whose location is unknown. Councils are in scope when they are `core` or have a catchment ward; districts and regions follow their councils.

## Extra intake columns

| Column | Meaning |
|---|---|
| `lead_track` | Always `government_convener` |
| `record_key` | `GOFF_<level>_…` for offices, `GPOST_<office>_<post>` for posts |
| `office_level`, `admin_unit_level`, `admin_unit_name`, `parent_admin_unit`, `council_name`, `region` | Where the office sits |
| `census_2022_population`, `census_source_location` | As published in the 2022 census report, with table, PDF page and row |
| `catchment_wards`, `catchment_population_2022` | Councils only: wards within the catchment and their population |
| `office_title`, `office_title_sw` | Post title in English and Kiswahili |
| `appointment_type` | `civil_service`, `elected` or `political_appointee` |
| `holder_name`, `holder_verified_on`, `tenure_source_url` | Only from an official roster or profile, exactly as published |
| `b2g_check_required` | `yes` for education posts |
| `convening_role`, `convening_forum` | What the post or office can convene, from the plan |
| `protocol_status`, `protocol_ref` | `none` in a research run |
| `pdpa_risk`, `pdpa_risk_reason` | See the rubric below |
| `proposed_government_track`, `track_reason` | `GA00 Hold`, `GA01 Protocol introduction` or `GA02 Convening request` (the shared `acquisition_track_id` only accepts AQ tracks) |
| `proposed_value_modules` | VM14–VM17 for GA01 offices (the shared `value_module_ids` only accepts VM01–VM07) |
| `ward_score`, `ward_tier`, `score_factors`, `factors_known`, `rank_in_cluster`, `campus_cluster` | Ward priority (below) |
| `nearest_primary_campus`, `distance_to_primary_km`, `primary_band` | Nearest campus with Standard 1–7 |
| `location_source`, `location_note` | How the ward or office was placed |
| `po_box`, `master_organisation_id`, `all_sources_json` | Postal address as published; read-only link to the company master; every source |

## Risk rubric (`pdpa_risk`)

| Label | Covers |
|---|---|
| `low` | Offices, role desks and organisation-level facts |
| `medium` | An official's name as published by the office; a phone number the office published for contacting that post (named in `channel_attribution`). Use only in the official role, after the council introduction. |
| `risky` | Personal emails or phones of officials that the office did not publish for that purpose. None in the first run. |

Never collected: parents' or residents' data; resident, voter, beneficiary or pupil lists; party affiliation; religion or ethnicity; CMS editor names or emails; officials' photos or biographies; the text of news stories.

## Ward locations

OpenStreetMap has no ward boundaries in the catchment, so each ward gets one reference point, labelled `estimated` (or `address` for a mapped ward office). `build_government_run.py` applies this order:

1. A reviewed override in `links.json` `ward_locations`. Besides a Wikipedia article or an OpenStreetMap place, it may name a school or health facility called after the ward (`osm_named_facilities_<date>.json`, collected by `collect_ward_locations.py`) that lies inside the council's district, when the ward name is unique to that council. Such facilities are never used without a review.
2. The ward office itself, where OpenStreetMap maps it and its name matches the ward inside the council's district (or `osm_office_links` says so).
3. A Wikipedia ward point, when OpenStreetMap corroborates it within `location_disagreement_km` (5 km).
4. OpenStreetMap evidence: a town or village named like the ward, then the centre of places listed under an area named like the ward ("Uswaa, Machame Uroki"), then a hamlet named like the ward.
5. An uncorroborated Wikipedia point, then the repository gazetteer.

Every candidate must lie in the council's OpenStreetMap district or its joint zone (`joint_zones` in the config: Arusha City with Arusha District, Moshi Municipal with Moshi District, because the urban polygons are unreliable). A Wikipedia point is rejected when its article names another district or its coordinates are shared with another article. When Wikipedia and OpenStreetMap disagree by more than 5 km, strong OpenStreetMap evidence wins (a town or village, or three or more listed places); otherwise Wikipedia does. Either way a review item records both points. Evidence that matches same-named wards in two councils is left for review.

## Ward score and tracks

| Factor | Points | Now |
|---|---:|---|
| 2022 population, percentile among the catchment wards | 30 | Known |
| Transport band: half nearest campus, half nearest primary campus (0–5 km 1.0, 6–10 0.8, 11–15 0.6, 16–20 0.4, 21–25 0.2) | 25 | Known |
| Access readiness: introduction recorded with the council | 20 | Zero until recorded |
| Convening opportunity: a confirmed meeting within six weeks | 15 | Zero until recorded |
| Observed yield: opt-ins per 100 attendees at earlier events | 10 | Zero until measured |

Tiers: P1 40+, P2 30–39.9, P3 20–29.9, P4 below 20. The score never uses political affiliation, ethnicity, religion or income. `rank_in_cluster` ranks catchment wards within each campus cluster (`campus_clusters` in the config).

Tracks: `GA01 Protocol introduction` for core councils with an office published on their official site; `GA00 Hold` otherwise; no `GA02` until an introduction is recorded and the ward post is verified within 90 days.

## Identity

- Councils and regions key on their own website host; offices below council level never take a shared council domain.
- Ward offices key on council and census ward name; village offices on their OpenStreetMap ID.
- Posts key on office and post. A different holder for the same post is a review item, never a second contact.
- Roster ward spellings match census names exactly, through `ward_aliases`, or by a similar spelling (ratio 0.85 or more, unique) that raises a review item.

## `links.json` (reviewed curation, per run)

| Key | Holds |
|---|---|
| `ward_aliases` | Per council: a spelling used by a roster, Wikipedia or OpenStreetMap, mapped to the census ward name |
| `ward_locations` | `"<council>|<ward>"` mapped to `{"source": "wikipedia" \| "osm_place" \| "osm_facility" \| "none", "ref": "<title, node/ID or way/ID>", "note": "..."}` |
| `osm_office_links` | OpenStreetMap office ID mapped to `{"council", "ward", "note"}`, or to `{"category", "detail", "note"}` to record a reviewed triage decision |

## Side tables (run database)

| Table | Holds |
|---|---|
| `admin_units` | Every census ward and council: population with locators, reference point, campus distances, catchment flag, ward score and tier, and the ward office's ID |
| `government_office_profiles` | Office level, administrative unit, convening forum, protocol status, proposed track, OpenStreetMap and master IDs |
| `official_posts` | Post, titles, appointment type, holder as published, tenure source, B2G flag and risk, one per contact |
| `community_events` | Counts only: expected and estimated attendance and method, opt-ins, enquiries, tours, applications, enrolments and cost. No person-level columns. |
| `office_triage` | Every named OpenStreetMap government office, classified as convener, excluded (with reason), not government, agency or unidentified |
| `master_triage` | The company master's `office:government` records, grouped as plan §2.1 proposes, with the proposed treatment |
| `convening_signals` | Council and regional news or notices tagged for public meetings, events, ward or village meetings, executive-officer training or elections |
