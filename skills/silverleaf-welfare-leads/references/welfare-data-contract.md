# Welfare-lead data contract

This extends the shared contract in `../../silverleaf-create-lead-list/references/lead-list-data-contract.md`. A welfare run uses the shared intake columns plus the extra columns below. The create skill's validator accepts extra columns, and its initializer keeps them in `source_records.payload_json`.

## Research records (JSONL)

Research agents write one JSON object per line, following `research-brief.md` section 8. There are four record types:

| `record_type` | Purpose |
|---|---|
| `organisation` | One welfare institution or funder, with every published data point and a `sources` list (URL, date, basis, `fetched`, facts supported, excerpt of 25 words or fewer) |
| `contact` | One person or role desk, linked by `organisation_name`, with the routes exactly as the source published them |
| `relationship` | A `from_organisation` → `to_organisation` link: `funds`, `operates`, `refers` or `partners_with` |
| `enquiry` | A public parent or guardian enquiry; always `pdpa_risk: "risky"` |

Files are named `data/raw/welfare-research/research_<slice>_<name>_<date>.jsonl`, and each has a coverage log in `data/raw/welfare-research/coverage/`.

## Segments and fit

| Segment | `care_model` | Examples |
|---|---|---|
| Welfare residential care | `residential` | Children's home, orphanage, baby home, children's village |
| Welfare family-based programme | `family_based` | Sponsorship, orphans and vulnerable children programme, kinship or foster support |
| Welfare specialised centre | `specialised` | Disability or rehabilitation centre, street-children centre, rescue house |
| Welfare funder | `funder` | Foreign charity, faith or umbrella body, corporate CSR funder |
| Welfare (unclassified child-focused NGO) | blank | NGO register entry that names children but whose programme type is unknown |
| Out of scope | blank | Schools, day care centres, homes for older people, hospitals |

`welfare_fit` takes one of these values:
- `likely`: researched or a strong register match
- `possible`: a register entry whose name or vision mentions children
- `unlikely`: register only
- `out of scope`

## Extra intake columns

| Column | Meaning |
|---|---|
| `lead_track` | Always `welfare_customer` |
| `record_key` | Stable key: `WORG_`, `WCON_` or `WENQ_` plus the normalised name. Same-named twins (one body's funder record and its programme record, which never merge) add their kind: `__funder`, `__programme`, `__home`, `__centre`, `__network` |
| `welfare_fit`, `care_model` | As defined above |
| `pdpa_risk`, `pdpa_risk_reason` | `low`, `medium` or `risky`; see the risk rubric below |
| `proposed_welfare_track`, `track_reason` | `WA00 Hold`, `WA01 Routing`, `WA02 Consultative` or `Excluded`, and why |
| `priority_score`, `factors_known` | Rubric score (0–100), and how many of its six factors had evidence |
| `children_served_published`, `children_served_as_of` | Only when published; never estimated |
| `age_range_published`, `gender_served` | As published |
| `schooling_arrangement_published`, `runs_own_school` | Source wording; `yes`, `no` or `unknown` |
| `funding_model_published`, `registration_published` | Source wording |
| `nis_reg_no`, `nis_reg_date`, `nis_profile_url` | NGO register link when matched |
| `licence_status` | `not_checked` until the social-welfare authority confirms the licence |
| `operator_or_umbrella`, `religious_affiliation_published` | Organisation-level, as published |
| `services` | JSON list |
| `known_funders_or_partners`, `foreign_charity_registrations` | JSON lists |
| `social_media`, `all_emails`, `all_phones` | JSON; the first email and phone also fill the shared contract fields |
| `volunteer_programme`, `volunteer_fee_published` | As published (recorded red-flag inputs) |
| `safeguarding_policy_url`, `staff_count_published` | As published |
| `latest_activity_date`, `red_flags`, `catchment_note` | As recorded |
| `master_organisation_id` | ID in the company-leads master when the organisation is already there (read-only link) |
| `nearest_primary_campus`, `distance_to_primary_km` | Nearest campus with Standard 1–7 |
| `all_sources_json` | Every source for the record |
| `email_type`, `phone_type`, `author_type_stated` | Contact and enquiry detail |

## Risk rubric (`pdpa_risk`)

| Label | Covers |
|---|---|
| `low` | Organisation-level facts, and generic organisational routes the organisation publishes |
| `medium` | A named person in a professional role as published by the organisation, an official register or their own professional profile |
| `risky` | Private individuals, or a named person on a personal email domain (enforced in `scripts/welfare/build_welfare_run.py`) |
| `risky` | Personal social-media data, regulator-listed individuals, or anything touching household circumstances or children |

Never collected at all:
- any child's name, photograph, story or health information, or an age tied to an identity
- anything about parents or relatives of children in care
- private addresses
- closed-group content
- cross-source profiling of individuals

## Identity and merging

Three rules decide identity:

- **What merges automatically.**
  - Only an exact normalised name, alternative name or own website domain merges records.
  - The merge happens only between records of the same kind: funder with funder, institution with institution.
  - An NGO-register entry links by exact registration number, exact name, or a reviewed manual link in `links.json`.
- **What goes to review instead.** These never merge automatically:
  - similar names
  - a funder and an institution sharing a domain
  - conflicting material facts
  - near-identical contact names
- **Same-named twins.** A funder record and an institution record with the same name stay two records, each with its own `record_key` (10 October 2026). A contact goes to the twin whose research record, in the contact's own research file, comes last before the contact's line; a person listed under both is one contact, kept with the first. A `funds` relationship starts from the funder twin; any other side is the institution twin. When drafting, each twin chooses its addressee from the contacts of both, since the same people lead the body.
- **Name normalisation.** It removes parentheses, punctuation and legal suffixes. It also treats "children's", "childrens" and "chidren" as the same word, and "center" and "centre".

## Priority rubric (plan §5.4)

| Factor | Points |
|---|---:|
| Published children: 50+ | 30 |
| Published children: 20–49 | 22 |
| Published children: 10–19 | 15 |
| Published children: under 10 | 8 |
| Private or English-medium fees already paid | 20 |
| Public-school arrangement | 10 |
| Ages start at 6 or under | 15 |
| Ages start between 7 and 14 | 8 |
| Transport band (precise location only): 0–5 km | 15 |
| Transport band: 6–10 km | 12 |
| Transport band: 11–15 km | 9 |
| Transport band: 16–20 km | 6 |
| Transport band: 21–25 km | 3 |
| Named contact | 10 |
| Organisational route only | 5 |
| Warm path from a company-master lead | 10 |
| Any other known funder | 5 |

Two adjustments apply to published child counts. A national total counts as 10, and a cumulative or "since" figure counts at half value.

Tiers: P1 is 60 or more, P2 is 40–59, P3 is 20–39, and P4 is below 20.

**Proposed track:**
- **`WA00 Hold`** applies if any of these hold:
  - the evidence is unverified or historical
  - there is no published route
  - the location is unresolved or more than 25 km away
  - the location is known only to town level and the town straddles the 25 km line
  - the record has red flags
  - for funders, there is no verified link to an institution in the catchment
- **`WA01 Routing`** applies otherwise.
- **`WA02 Consultative`** needs the licence confirmed by the authority, so the research run assigns none.

## `links.json` (reviewed curation, per run)

The run folder `data/runs/<run-id>/links.json` holds reviewed decisions. Each key is optional:

| Key | Holds |
|---|---|
| `nis_to_org` | Register ID mapped to researched name. Add a pair only on supported evidence, and record the evidence under `nis_to_org_evidence`. |
| `nis_exclude` | Register IDs to leave out |
| `geo_overrides` | Name mapped to `lat`, `lon`, `precision`, `basis`, for multi-site or wrongly geocoded organisations |
| `osm` | OpenStreetMap features mapped to research names, plus `add_if_missing` |
| `master_ids` | Name mapped to a company-master ID, when names differ |
| `corporate_funders_in_master` | Company-master leads whose funding gives a warm path |
| `org_aliases` | Alias mapped to a researched name |
| `rejected_routes` | A list of reviewed values that are not the organisation's route (another organisation's inbox or phone): `organisation_name`, `kind` (`email` or `phone`), `value`, `reason`, `source`, `source_url`, `decided_on`. `consolidate_research.py` removes them from the organisation and its contacts, together with the welfare entries of `data/reference/rejected-routes.json` (10 October 2026) |

## Addressee and escalation contact (`outreach_plans`)

`scripts/messaging/draft_run_messages.py --track welfare` chooses one addressee per organisation (decided 10 October 2026: someone on the ground):

- **First choice:** the most senior person running the Tanzania or Arusha operation: a country manager or country director, a national director, a Tanzania head, the head of a home, an on-site director, or an Arusha programme or home manager. Otherwise the organisation's most senior named leader, with a local founder or director of a home or programme first.
- **Fallback:** a global or overseas chief executive, executive director, founder or president, only when no one in the country is named. When a country head is named, an executive whose role does not name Tanzania counts as head office.
- **Never chosen:** a board role (chair, vice chair, treasurer, secretary, trustee, board member, emeritus, a "Director, <country>" board seat, or a president or chair qualified by a board), a person working for another country's operation (a role naming Kenya, Uganda and so on), and a non-executive based abroad.
- **Route:** the addressee's own published address on the organisation's domain, else the organisation's route.

When the addressee is on the ground and the organisation also names an executive abroad or at head office (never a board role, and never less senior than the addressee), the plan names that executive as an **escalation contact**, for a person to approach by hand. They are not copied on the first message and no message is drafted to them. The welfare workbook's Outreach Plans sheet and the review file from `scripts/messaging/consolidate_welfare_drafts.py` show them.

| Column | Meaning |
|---|---|
| `escalation_contact_id` | The executive's `contact_id` in the run database |
| `escalation_recipient` | Name and published role, for example `Geoffrey Kasangaki (Global CEO)` |
| `escalation_route` | The address or phone to use: the executive's own published work address, else the organisation's inbox addressed to them by name |
| `escalation_trigger` | When to escalate: no reply after the follow-up, or the country office declines or defers to head office |
| `escalation_route_type` | `named_email`, `published_role_email` or `organisation_email` |
| `escalation_source_url` | Where the executive and their role are published |

The first four columns have the same names in the company master; the Resend exporter reads them by name.
