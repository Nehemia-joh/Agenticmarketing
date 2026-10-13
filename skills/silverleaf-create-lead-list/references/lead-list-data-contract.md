# Lead-list data contract

Use UTF-8 CSV for intake and SQLite for the canonical database. Preserve source wording in evidence fields; normalise only matching keys and structured values.

## Intake columns

The template contains every accepted column. Empty values are allowed unless marked required for the row type.

### Common provenance fields

| Field | Requirement | Meaning |
|---|---|---|
| `record_type` | Required | `organisation`, `contact`, or `enquiry`. |
| `source_path` | Path or URL required | Repository-relative path for a captured source. |
| `source_location` | Required | Page, sheet and row, file line, post identifier, or another precise locator. |
| `source_url` | Path or URL required | Canonical public `http` or `https` URL. |
| `source_date` | Optional | Publication or source date, `YYYY-MM-DD`. |
| `acquired_on` | Required | Collection date, `YYYY-MM-DD`. |
| `verified_on` | Required | Date the evidence was checked, `YYYY-MM-DD`. |
| `verification_status` | Required | `verified`, `needs_review`, `historical`, or `unverified`. |
| `evidence_basis` | Required | `official`, `published`, `public_profile`, `public_post`, `directory`, `reference_file`, or `research_note`. |
| `evidence_excerpt` | Required | Short paraphrase or excerpt supporting the row. |
| `notes` | Optional | Qualification, caveat, or reviewer context. |

### Organisation fields

`organisation_name` is required for organisation and contact rows. Use published facts for the remaining fields.

| Field | Type or allowed values |
|---|---|
| `organisation_domain` | Lowercase registered domain without a path. |
| `segment`, `subtype` | Controlled campaign labels; document additions. |
| `priority` | `High`, `Medium`, `Low`, or blank. |
| `campus` | Canonical campus name or `Multiple`. |
| `distance_km`, `latitude`, `longitude` | Decimal numbers. |
| `radius_tier` | Project-defined band such as `0-3km`, `3-8km`, `8-15km`. |
| `geocode_precision` | `rooftop`, `address`, `street`, `locality`, `estimated`, or blank. The master also holds `point`, `city`, `town` and, for savings groups placed at their ward's reference point, `ward` (an estimate: no draft states a distance from it). |
| `locality`, `address`, `website` | Published location and URL. |
| `public_email`, `public_phone` | Public organisation route; never inferred. |
| `size_evidence`, `headcount` | Source wording and integer estimate when explicitly supported. |
| `education_angle` | Recipient-centred partnership relevance. |
| `founded`, `licence_class`, `osm_id` | Published identifiers or attributes. |
| `desk_tier` | Project-defined research tier. |
| `desk_score` | Decimal score with documented rubric. |
| `transport_band` | Project-defined travel band. |

### Contact fields

A contact row requires `organisation_name` plus a named person or public contact route. At least one contact route must be present.

| Field | Meaning |
|---|---|
| `contact_name` | Published full name; leave blank for a role desk. |
| `role` | Published role or role-desk label. |
| `role_certainty` | `confirmed`, `role_desk`, `inferred_role`, or `unknown`. |
| `contact_route` | Preferred public route: `email`, `phone`, `form`, `linkedin`, `social_dm`, or `website`. |
| `shared_email` | Shared public inbox. |
| `published_role_email` | Public role-addressed inbox. |
| `named_email` | Publicly published named work email. |
| `organisation_phone`, `role_phone` | Public organisation or role line. |
| `profile_url` | Public professional profile or official staff page. |
| `channel_attribution` | Source that published the selected route. |

Do not generate email patterns. Do not copy personal contact details from data broker results unless the individual has published them for the relevant professional purpose.

### Enquiry fields

An enquiry row requires `enquiry_type`, `enquiry_date`, `request`, `platform`, and `source_url`. The author may be blank when the public post is anonymous.

| Field | Meaning |
|---|---|
| `enquiry_author` | Public display name exactly as shown. |
| `enquiry_type` | Need category such as daycare, preschool, primary school, transport, tuition, or relocation. |
| `enquiry_date` | Publication date, `YYYY-MM-DD`. |
| `date_qualification` | `exact`, `month_only`, `year_only`, or `unknown`. |
| `request` | Concise account of what the person asked for. |
| `platform` | Website or network where the enquiry appeared. |
| `contact_attribution` | How any contact route relates to the author. |
| `current_relevance` | `current`, `recent`, `historical`, or `unknown`. |
| `campus_fit` | Closest relevant campus or `Unknown`. |
| `enquiry_phone`, `enquiry_email` | Only when the author deliberately published it with the enquiry. |

### Outreach and acquisition fields

These fields are optional during research and required before a row enters a campaign review.

| Field | Meaning |
|---|---|
| `relevance_reason` | Evidence-backed reason the target and offer fit. |
| `proposed_offer` | Useful first value offered to the recipient. |
| `cta_type` | Small requested next step, such as `permission`, `routing`, `resource_offer`, or `brief_call`. |
| `hook` | Optional factual opening. |
| `hook_source_url` | Required when `hook` is present. |
| `hook_verified_on` | Required when `hook` is present, `YYYY-MM-DD`. |
| `acquisition_track_id` | `AQ00_RESEARCH_ONLY`, `AQ01_PERMISSION_LED`, or `AQ02_TRIGGER_LED`. |
| `value_module_ids` | Pipe-separated values from `VM01` through `VM07`. |
| `review_status` | `research_only`, `needs_review`, `draft_ready`, or `approved`. |
| `missing_information` | Specific fact or route needed before the next state. |

## VICOBA intake (savings groups, decided 13 October 2026)

VICOBA and VSLA groups enter the company master as a subsegment of savings groups, as group-level records with no personal data (`docs/plans/vicoba-integration-plan.md`, "Decisions taken", section 0 and section 4.1). `scripts/collection/build_vicoba_intake.py` writes `data/raw/vicoba/master_intake_<date>.csv`, and `scripts/master/add_vicoba_groups.py` adds it after the validator and the preflight. Every row is an `organisation` row.

### Controlled labels

| Label | Values |
|---|---|
| `segment` | `Savings group` (shared with SACCOS) |
| `subtype` | `VICOBA — women's group`, `VICOBA — mixed or unspecified`, `VICOBA — youth group`, `VICOBA — group of people with disabilities` (only when a council or intermediary supplies the group as such; membership is never recorded about any person), `VSLA — NGO-programme group` |
| Outreach segments | `VICOBA members` (group plans), `VICOBA introducers` (NGO and bank introducer plans) |
| `geocode_precision` | `ward` (the ward's reference point from the government run), or `point` for a published public venue |
| Organisation ID | `hid("O", "vicoba", vicoba_group_key)`: `O` plus 12 hex characters, as for every master organisation. Partner code prefix for member opt-ins: `VIC-` |
| Review kinds | `VICOBA record incomplete`, `VICOBA stale`, `VICOBA possible duplicate`, `VICOBA may be a registered SACCOS`, `VICOBA introducer to confirm`; conflicts between sources use `Multiple source values` |

### Columns

The intake carries the shared template's columns, then these. Each becomes a field-level fact of the same name on the group, linked to the row's source record.

| Column | Meaning |
|---|---|
| `candidate_id` | The builder's capture ID (optional; kept in the notes). |
| `vicoba_group_key` | `VIC|<council>|<ward>|<normalised name>`. Council and ward as the government run's `admin_units` spell them; the name in lower case without punctuation or spaces, and without the words VICOBA, VIKOBA, Kikundi cha, Kikundi, Group, Women Group, Wanawake and Vijana. The adder computes it when blank and uses the supplied key when given. |
| `council`, `ward`, `village_or_mtaa` | The group's area. `locality` is `<village>, <ward> ward, <council>`; the adder builds it when blank. |
| `meeting_place_public` | A public venue only (church hall, school, ward office, market, bank branch). A private home is never recorded. |
| `meeting_cadence`, `cycle_start_month`, `share_out_month` | As published or as the committee states them; never inferred. |
| `member_count` | Whole number, only when published or stated by the committee. |
| `registration_number`, `registration_authority` | Only when published (council CMG register, LGA). |
| `sponsor_name`, `sponsor_kind`, `sponsor_ref` | Kind: `ngo`, `bank`, `church`, `mosque`, `council`, `employer` or `other`. Ref: a master `organisation_id` or `welfare:<run-id>:<organisation_id>`. |
| `introducer_kind`, `introducer_ref` | Kind: `cdo_ward`, `cdo_council`, `ngo_field_office`, `bank_branch`, `faith_office` or `group_published`. Ref: `gov:<run-id>:<ward office organisation_id>` for a CDO, a master `organisation_id` for an NGO or bank. |
| `employer_ref` | A master employer whose name the workplace group carries; the group joins that employer's deal. |
| `record_status` | `complete`, `incomplete: no ward`, `incomplete: no introducer route`, `incomplete: name only`, or `stale: not confirmed in 12 months`. Computed when blank. |
| `last_confirmed` | `YYYY-MM-DD`; `verified_on` when blank. Older than 12 months makes the group stale. |
| `women_group`, `women_group_basis` | `true` only on source evidence: the name names women (wanawake, akina mama, kina mama, women, mama), the source calls it a women's group, or the council supplies it as a 10% loan women's group. Basis: `name`, `source_says` or `council_women_loan_group`. Never inferred from a member's or leader's name. The adder records `women_group` on every group (`false` means not tagged); later tasks order waves by it and compare conversion with it. |
| `phone_basis` | `published_for_role` or `consent_recorded <YYYY-MM-DD>`. Kept without the number. |
| `vicoba_groups_reported` | Marks an aggregate row ("25 groups formed"): never an organisation. The count becomes a fact on the `sponsor_ref` organisation. |

The adder also writes `sources_seen` (one fact per source). `covers_groups` is written on introducer plans by the drafter, not by the intake.

### Privacy

- A VICOBA organisation never has a phone or an email.
- No contact rows, member names, member counts by person, members' phones, home meeting places, children, loans or savings balances.
- The adder blanks phone, email, contact-name and enquiry columns, and any meeting place that reads as a home, in the stored source record and in the stored copy of the intake. It reports only their count.
- A group leader's phone reaches the master only through the contact path, as `contacts.role_phone` with the fact `phone_basis = published_for_role` and its source. A consented number stays outside the repository.

### Outreach plans

`outreach_plans` has two columns for Kiswahili drafts, `language` (`sw`) and `english_meaning`. For a VICOBA plan, `subject` and `body` hold the Kiswahili first message and `english_meaning` its English meaning. `offer_message_sw` holds the Kiswahili offer and `offer_message` its English meaning. The adder creates one plan per new group (`VICOBA members`, `Needs research`, AQ00, flow F26, `VM02; VM03; VM06; VM20`, blank copy). The drafter writes its copy.

## Canonical tables

The database may add campaign-specific fields, but it must keep these logical tables and relationships:

- `source_files`: one row per captured file or URL, including path, hash, MIME type, acquisition metadata, and optionally compressed original bytes.
- `source_records`: one row per source location, with its raw or normalised payload.
- `organisations`: one row per organisation with a stable `organisation_id`.
- `contacts`: one row per person or role desk, linked to `organisation_id`.
- `enquiries`: one row per public expression of need with a stable `enquiry_id`.
- `entity_sources`: many-to-many links between entities and source records.
- `facts`: field-level claims with their source record.
- `review`: conflicts, missing evidence, ambiguous matches, and required decisions.
- `messages`: message versions linked to a target and strategy.
- `outreach_plans`: recipient, evidence, offer, CTA, hook, sequence, status, and acquisition state.
- `strategies`, `segments`, `campaigns`, `campaign_touchpoints`, `campaign_assignments`: reusable campaign definitions and assignment history.
- `automation_recipes`, `automation_steps`: disabled-by-default operational blueprints.

The current Silverleaf master may contain these detailed organisation fields: `organisation_id`, `name`, `segment`, `priority`, `campus`, `distance_km`, `size_evidence`, `headcount`, `address`, `education_angle`, `source_url`, `verification`, `strategy_id`, `outreach_status`, `next_action`, `next_action_date`, `email`, `phone`, `subtype`, `radius_tier`, `geocode_precision`, `website`, `notes`, `desk_tier`, `desk_score`, `transport_band`, `locality`, `founded`, `licence_class`, `osm_id`, `latitude`, and `longitude`.

The current contact fields are `contact_id`, `organisation_id`, `name`, `role`, `campus`, `source_url`, `verification`, `shared_email`, `organisation_phone`, `contact_route`, `published_role_email`, `role_phone`, and `named_email`.

The current enquiry fields are `enquiry_id`, `legacy_id`, `name`, `type`, `enquiry_date`, `date_qualification`, `locality`, `request`, `campus_fit`, `phone`, `email`, `contact_attribution`, `platform`, `source_url`, `current_relevance`, `source_record_id`, and `strategy_id`.

The current outreach-plan fields are `message_id`, `target_id`, `target_type`, `organisation_id`, `target_name`, `organisation_name`, `strategy_version`, `segment`, `recipient_role`, `persona`, `contact_channel`, `channel_attribution`, `evidence_url`, `evidence_date`, `verified_on`, `evidence_basis`, `evidence_record_ids`, `relevance_reason`, `proposed_offer`, `cta_type`, `flow_id`, `review_status`, `missing_information`, `selection`, `subject`, `body`, `follow_up_1`, `follow_up_2`, `hook_version`, `hook_type`, `hook_quality`, `hook_status`, `hook_evidence`, `hook`, `first_message_v2`, `campaign_version`, `campaign_subject_v3`, `campaign_message_v3`, `campaign_follow_up_1_v3`, `campaign_follow_up_2_v3`, `campaign_evidence`, `campaign_copy_status`, `acquisition_version`, `acquisition_track_id`, `value_module_ids`, and `strategy_scope`. Later scripts add their own columns when they first write. `add_vicoba_groups.py` adds `language` and `english_meaning` (13 October 2026); `--schema-only --apply` adds them without an intake.

## Identity and normalisation

- Compare Unicode text case-insensitively after trimming whitespace and collapsing repeated spaces.
- Canonicalise URLs by lowercasing the host, removing fragments, and removing a trailing slash from non-root paths.
- Lowercase email addresses and domains.
- Store phone numbers as published plus a normalised comparison value when possible.
- Generate new IDs deterministically from the record type and exact key; keep existing IDs during updates.
- Never merge solely because two names are similar.

## Evidence rules

- Prefer official pages and documents, then published directories, public professional profiles, public posts, and research notes.
- Distinguish the date published from the date verified.
- Keep unsupported or stale claims out of hooks and personalisation.
- A profile or post proves only what it states; it does not prove private family status, intent, or present employment beyond its context.
- Keep historical records for provenance, but label current relevance.
