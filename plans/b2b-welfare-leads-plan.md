# B2B welfare leads: plan to extend the lead tool

- **Prepared:** 22 September 2026
- **Status:** Plan only. No code, schema or data has changed. Sending and automations remain disabled.
- **Method:** Structured on the Standard Feature Work Methodology shared on 22 September 2026: study, confirm scope, plan, implement, test, document, close the loop. That text is not currently in the repository, and Phase 0 (§4) proposes the infrastructure it assumes.
- **Companions:** `plans/b2b-government-leads-plan.md` (reuses Phase 0 in §4), `docs/methodology/partner-lead-generation.md` (the corporate method this mirrors), `chats/b2b_cooperate_leads.md` (how the corporate track was built).

## 1. What changes when the lead is the customer

The brief is to extend the tool so it captures welfare institutions as B2B leads: children's homes, welfare homes, community homes and other welfare institutions. Unlike a corporate lead, a welfare institution is the paying customer.

| | Corporate track (built) | Welfare track (this plan) |
|---|---|---|
| Who pays Silverleaf | The parent | The institution or its funder |
| What the lead is | A channel to staff who may be parents | A buyer of several school places |
| Who decides | An HR or staff-welfare owner agrees to circulate information | A director or manager, an education lead or social worker, and often a board, donor or parent organisation |
| Unit of value | Opted-in parent enquiries | Places filled, retained and renewed each year |
| What qualifies a lead | Local staff scale, which is rarely published | Children in Silverleaf's age range, current schooling arrangement, funding capacity and licence status, which are rarely published |
| Timing | Any time | Before term. Primary intake runs October–December for a January start and June–July; daycare and pre-primary are rolling |
| Channel | Email-led acquisition tracks | A consultative sale led by phone calls and visits; email only to a published route |
| Largest risk | An unsupported hook | Children's data, safeguarding, and association with an unlicensed or exploitative home |

The consequence for the tool: **a welfare lead is an account, not a message recipient.** The tool must hold account facts (licence status, published scale, funder links), a pipeline stage and aggregate place counts. It must never hold information about an individual child.

The user's four terms map to four segments:

| Term in the brief | Segment | Typical subtypes |
|---|---|---|
| Children's homes | Welfare residential care | Licensed children's home (*makao ya watoto*), small group home, faith-run home |
| Welfare homes | Welfare residential care or Welfare specialised centre | Decided by who the institution serves |
| Community homes | Welfare residential care (small group homes) or Welfare family-based programme | Community-based care, kinship or foster-care support, child sponsorship programme |
| Other welfare institutions | Welfare specialised centre or Welfare funder | Disability or rehabilitation centre, rescue house, street-children transition centre; diocesan social services, NGO, foundation or corporate CSR funder |

**Out of scope:**
- day care centres, which compete with or feed Silverleaf's own daycare
- homes for older people
- government retention homes and approved schools
- hospitals

## 2. Study findings: current behaviour on 22 September 2026

This section records what the repository does today. Sections 4 onwards describe proposed behaviour.

### 2.1 Welfare records already in the master

The master has no welfare segment. Five welfare-like records sit in other segments, and none has an outreach plan. Their welfare status is a hypothesis drawn from names and OpenStreetMap tags, and each needs verification before reclassification.

| Organisation | Current segment | Nearest campus | km | ID |
|---|---|---|---:|---|
| Cradle of Love Children's Home | `office:ngo` | Usa River | 2.2 | `O94f7a48ede44` |
| Emayani vulnerable people's center | `office:ngo` | Arusha City | 3.7 | `O1b5b75388663` |
| Usa-River Rehabilitation Centre | `office:educational_institution` | Usa River | 1.7 | `O00168bd8da71` |
| Next Life Foundation | `office:educational_institution` | Usa River | 20.1 | `O26afe2b96e32` |
| Sibusiso Foundation | `Safari / tour operator` (label looks wrong) | Ilboru | 2.3 | `Ofc2567ddcd95` |

Corporate evidence already names possible funders:
- Africa Dream Safaris' `education_angle` names Peace House Orphanage.
- KILI VIKINGS LIMITED states that it supports Kilimanjaro-region orphanages.

These claims are unverified, but they show that the corporate list can surface funders and warm introductions.

### 2.2 Rules this feature touches, and every place each one lives

| Rule | Where it is enforced or restated | Problem for this feature |
|---|---|---|
| Acquisition track IDs | `validate_intake.py` (`TRACKS`), `initialize_lead_db.py` (default), master `acquisition_tracks`, `refresh_acquisition_metadata.py`, `export_master_workbook_data.py`, `outputs/config/automation-recipes.json`, the acquisition framework and the outreach `SKILL.md` | The intake contract uses `AQ00_RESEARCH_ONLY`, `AQ01_PERMISSION_LED` and `AQ02_TRIGGER_LED`. The master uses `AQ00`, `AQ01` and `AQ02` under different names. New tracks would extend a set that is already inconsistent. |
| Value modules | `validate_intake.py` (regex `VM0[1-7]`), master `value_proposition_modules`, the refresh script and the framework doc | Any new module fails validation. |
| Segment → modules and tracks | `refresh_acquisition_metadata.py` hard-codes three segment branches plus an `ELSE` that gives every other segment the employer modules VM01–VM05, and it rewrites every outreach plan on each run | **If welfare rows are added without changing this script, the next refresh silently gives them employer modules and tracks.** This is the most important trap. |
| Campus anchors | `collect_partner_leads.js` (`CAMPUS`), `build_partner_leads.py` (`CAMPUSES`) and the master `campuses` table | The JavaScript copy differs from the other two for four of the five campuses; Kijenge is about 1.5 km apart. All are approximate centroids. |
| Organisation identity | `validate_intake.py`, `initialize_lead_db.py` and `preflight_update.py` match on domain first | Two homes listed on one diocese or NGO domain would merge. The master has no `domain` column, so preflight falls back to name plus locality there. |
| Physical schema | The master has 38 tables and uses `source_records.record_id`; the create-skill initializer has 13 tables and uses `source_record_id` | Preflight inspects the columns to cope. Every new table must be added to both schemas. |
| Strategy documents | `docs/strategy/*.md` and `skills/silverleaf-outreach/references/*.md` | The framework, positioning and flows files are byte-identical copies and must change together. `hook-guidance.md` has already drifted between its two copies. |
| Workbook columns | Explicit column lists in `export_master_workbook_data.py` and `build_master_workbook.mjs` | New fields do not appear in the review workbook until both files change. |

### 2.3 Data boundary and missing infrastructure

- **Data boundary:** Git ignores the SQLite master, but `outputs/master/Silverleaf Master Database - Consolidated.xlsx` is committed. Anything the export writes enters Git history.
- **Missing methodology infrastructure:**
  - `docs/_learnings`, `docs/database`, `tests/`, migrations, a `test` script and `.test-runs/` do not exist.
  - The repository uses npm, not Yarn.
  - The master's `PRAGMA user_version` is `0`.
  - The never-commit `restricted/` folder promised in the scope of work (§7.2) is not in `.gitignore`.

### 2.4 External sources, checked 22 September 2026

- **Registration process:** The Ministry of Community Development, Gender, Women and Special Groups publishes the children's-home registration requirements. An application goes through the council director (*Mkurugenzi wa Halmashauri*) with social-welfare and health inspection reports, proof of funding or donor letters, and caregiver ratios. The ministry publishes no list of registered homes.
- **NGO register:** The NGO Information System has a public mapping search by level, category (including Social Protection and Education), sub-sector and region. It listed 8,376 NGOs. NGO registration is not a children's-home licence.
- **Policy direction:** The Law of the Child Act 2009 replaced the Children's Homes (Regulation) Act. Policy favours family-based care over institutional care.
- **Data protection:** DLA Piper's summary of the Personal Data Protection Act 2022 states that data related to children is sensitive. It needs prior written consent from a parent or guardian. The summary also says direct marketing needs explicit consent unless the law authorises it. Confirm both points with counsel.

## 3. Scope confirmation

- Welfare leads are an independent feature. They are documented and tested separately from the corporate and government tracks and share only Phase 0 (§4).
- **Documentation home, to confirm before anything is created:** "This looks like a new function that is not yet covered in our documentation. I propose we create a new cluster/folder called `docs/welfare-leads/` and document it there. Do you agree or would you say otherwise?"
- Risks to handle from the start:
  - **Children's data.** The lead database stays at organisation level. Admissions handles placements in Ed-admin with the guardian's written consent.
  - **Committed workbook.** It carries nothing about children and no personal data beyond the business contacts it already holds.
  - **Safeguarding and reputation.** Verify the licence before contact, take no photographs, and keep a human escalation path.
  - **Price claims.** Do not offer a rate, bursary or discount without an approved terms record.

## 4. Phase 0: shared foundation for welfare and government

Build this once. Whichever track starts first does it, and the government plan points here.

| # | Change | Why | Main files |
|---|---|---|---|
| 0.1 | Add `organisations.lead_track` (`corporate_partner` by default, `welfare_customer`, `government_convener`) and a `lead_tracks` registry. Outreach plans and assignments derive the track through `organisation_id` instead of storing a copy. | One field records whether a lead pays or acts as a channel. | Migration 0001 |
| 0.2 | Create one controlled-vocabulary registry, `skills/silverleaf-create-lead-list/references/controlled-vocabularies.json`. It holds lead tracks, acquisition tracks with aliases, value modules with their allowed tracks, and segments. The validator, preflight, refresh and verify scripts read it; migrations seed the master tables from it. | The same lists currently live in code constants, SQL `CASE` branches and documents. | `validate_intake.py`, `preflight_update.py`, `refresh_acquisition_metadata.py`, `verify_master.py` |
| 0.3 | Make the short track IDs canonical. The validator accepts the long IDs as aliases and normalises them, and the initializer default becomes `AQ00`. | This removes the AQ drift before WA and GA tracks are added. | Validator, initializer, data contract |
| 0.4 | Make refresh track-aware. Move segment-to-module defaults into a `segment_module_defaults` table and apply the current corporate rules only to `corporate_partner` rows. | Designs out the overwrite trap. | `refresh_acquisition_metadata.py` |
| 0.5 | Add versioned migrations: `scripts/master/migrations/NNNN_name.py` plus `scripts/master/migrate.py`. The runner defaults to a dry run; `--apply` runs one transaction with integrity and foreign-key checks, bumps `user_version`, and works on a temporary copy outside the repository. | Schema changes become reviewable and repeatable. | New |
| 0.6 | Add `scripts/master/export_schema_snapshot.py`, which writes `docs/database/master-schema.md` and `.sql` from the verified master. The snapshot is never hand-edited, and tests build fixture databases from the `.sql`. | Meets the methodology's `docs/database` rule and gives tests the real schema. | New |
| 0.7 | Add `scripts/lib/campus_geo.py`. It reads the master `campuses` table and applies the published transport bands of 0–5, 6–10, 11–15, 16–20 and 21–25 km; anything further is outside the catchment. Only the new collectors use it. | Prevents a fourth and fifth copy of the campus coordinates. | New |
| 0.8 | Guard personal data. The validator gets a denylist of child-level and resident-level fields, and a verify check confirms that no master table or workbook export carries them. `.gitignore` gains `restricted/` and `.test-runs/`. | Enforces the data boundary in code, not only in documentation. | Validator, verify script, `.gitignore` |
| 0.9 | Add an `account_pipeline` table: organisation, lead track, stage, stage date, owner, next action and date, places discussed, places enrolled and notes. It stores aggregates only. | Welfare accounts and government offices both need a pipeline, and the corporate track can adopt it later. | Migration 0001 |
| 0.10 | Build a test harness in `tests/unit`, `tests/integration` and `tests/fixtures`, using synthetic data only. `npm test` runs `python -m unittest discover -s tests`. Either add `test:needed` with `.test-runs/last-green.json`, or change the methodology's Yarn commands to npm (see decision 10 in §9). | The methodology requires tests and the repository has none. | `package.json`, new |
| 0.11 | Seed `docs/_learnings/` with the traps in §2: an index plus one entry per trap. | Methodology step 6. | New |

**Phase 0 tests:**
- **Unit tests:** registry loading, alias normalisation and denylist detection.
- **Integration test:** build a fixture master from the schema snapshot and migrate it from version 0 to 1. Then prove that:
  - table counts are unchanged
  - every corporate track and module assignment is identical before and after refresh (a golden test)
  - `verify_master.py` passes
- **Local-only check:** run `migrate.py` as a dry run against the real master and review the diff.

## 5. Functional plan for the welfare track

### 5.1 Segments

| Segment | Include when all of this is evidenced | First contact |
|---|---|---|
| Welfare residential care | Cares for children aged 12 months to 14 years, is operating now, and has licence or registration evidence | Director or manager |
| Welfare family-based programme | Pays for or arranges schooling for children who live with families | Programme or education coordinator |
| Welfare specialised centre | Places children in mainstream day schooling, and Silverleaf confirms it can meet their needs | Centre manager or social worker |
| Welfare funder | Has a verified funding or operating link to an institution in the segments above | Programme or grants lead. The funder is a route to the institution, not a buyer unless it pays fees directly. |

### 5.2 Sources

| Source | Gives | Caveat | Evidence basis |
|---|---|---|---|
| Existing master (§2) | Five seed records and funder mentions | Classification unverified | `reference_file` |
| NGO register (NIS mapping) | Registered name, level, category and region | The field set and export are unconfirmed, the page renders in JavaScript, and registration is not a licence | `official` |
| Council social-welfare offices for Arusha City, Arusha District, Meru District and Hai District | Licensed homes and licence confirmation | Not published online; request in writing | `official` |
| OpenStreetMap, within 25 km of a campus | Coordinates | Contact details are rare and tagging is inconsistent | `directory` |
| Institution websites, annual reports and donor pages | Published scale, ages, schooling arrangement, funding, safeguarding policy and named roles | Often undated; check that the information is current | `published` or `official` |
| Faith-based and NGO umbrella lists of institutions | Operator and funder links | Coverage varies | `published` |
| Volunteer and charity directories | Discovery only | Often stale, and some promote orphanage tourism; never use as hook evidence | `directory` (low) |
| Google Places (optional, paid) | Coordinates and phone numbers | Needs an API key and has a cost, as in the corporate method | `directory` |

The OpenStreetMap query covers:
- `amenity=social_facility` with `social_facility:for=orphan` or `child`
- `social_facility=group_home`
- names matching "orphan", "children's home", *makao* or *kituo cha watoto*

**Collection steps:**
1. `scripts/collection/collect_welfare_leads.py` (standard library only) queries Overpass and reads saved snapshots of pages that render in JavaScript, such as NIS. It writes raw captures with SHA-256 hashes to `data/raw/welfare-research/`, and candidates to `data/interim/welfare-leads/welfare_candidates.tsv`.
2. `scripts/collection/build_welfare_intake.py` turns reviewed candidates into intake rows in the shared contract.
3. The rows then follow the required order in `.claude/CLAUDE.md`: validate, preflight, a transactional merge, export, build and verify.

Capture pages that render in JavaScript with a browser-console collector like `collect_partner_leads.js`, or save them as rendered HTML. A URL on its own is never evidence.

### 5.3 Data contract additions

| Field | Values or rule |
|---|---|
| `lead_track` | `welfare_customer` (required) |
| `care_model` | `residential`, `family_based`, `specialised` or `funder` (required) |
| `ngo_registration_ref`, `ngo_registration_checked_on` | The reference as published in NIS, and the date checked |
| `licence_status`, `licence_checked_on` | `confirmed_by_authority`, `self_reported`, `not_found`, `not_applicable` or `not_checked`, and the date checked |
| `children_served_published`, `children_served_evidence`, `children_served_as_of` | An integer only when explicitly published, the source wording, and its date. Never estimated. |
| `age_range_published`, `serves_silverleaf_ages` | As published; `yes`, `partly`, `no` or `unknown` |
| `current_schooling_published`, `funding_model_published` | Source wording only |
| `safeguarding_policy_url`, `special_needs_focus_published` | As published |

- **New record type `relationship`.** It holds `from_organisation`, `to_organisation`, `relationship_type` (`funds`, `operates`, `refers` or `partners_with`), evidence and a verification date.
- **Contacts.** They use the existing fields. Typical published roles are director or manager, education coordinator, social worker, trustee (only when published for that role) and funder programme lead.
- **Identity rule.** Set `organisation_domain` only when the domain belongs to that institution alone. Record a home listed on an umbrella's website with a blank domain and a `relationship` row.
- **Forbidden.** Nothing may describe an individual child: no name, age, photograph, story, school record, health information or family circumstance. Evidence excerpts are paraphrased at organisation level.

**Schema (migration 0002):**
- `welfare_profiles`: one row per organisation.
- `organisation_relationships`.
- `approved_offer_terms`: terms ID, lead track, summary, approver, approval date, validity dates and source record.

The same tables are added to the initializer, so a separate welfare run works.

### 5.4 Qualification, priority and tracks

**Gates before direct outreach (WA02):**
- the institution's identity is verified
- it is operating now, with evidence dated within the last 12 months
- the authority has confirmed the licence
- it serves children in Silverleaf's age range
- it is within 25 km of a campus that offers the level needed, or it states that it arranges transport
- a published contact route exists

**Priority score, 0–100:**

| Factor | Weight |
|---|---:|
| Place potential: published number of children in Silverleaf's age range | 30 |
| Schooling readiness: an institution already paying private fees scores above one using free public schools | 20 |
| Level fit: primary needs Usa River or Arusha City; daycare and pre-primary fit all five campuses | 15 |
| Transport band | 15 |
| Decision-maker identified | 10 |
| Warm path: a verified funder link to an existing corporate lead | 10 |

The score never uses a child's circumstances or vulnerability, religion, or a founder's nationality.

**Acquisition tracks:**

| Track | Use when | Touches | Outcome |
|---|---|---|---|
| WA00 Hold | Identity, licence, current operation or fit is unresolved | None | Research, or close with a reason |
| WA01 Routing | A route is usable but the decision-maker or licence status is unresolved | One call or email asking who handles school placements, one check-in after 5 working days, then stop | A named owner, or close |
| WA02 Consultative | The gates pass and a decision-maker is verified | Request a 20-minute placement-planning conversation, follow up once after 4 working days, then offer a visit. Stop after three unanswered touches. | A conversation is held |

### 5.5 Offer and value modules

The corporate method's rule "design the offer first" matters even more here, because the offer is the product. Silverleaf leadership approves terms before VM09 or VM13 is used.

| Module | Recipient value | Silverleaf contribution | Do not imply | Gate |
|---|---|---|---|---|
| VM08 Placement planning | Which campus and level suits their children, by age band and intake window | A 20–30 minute conversation using published levels and intake windows | Guaranteed places or capacity | Admissions confirms capacity before discussing numbers of places |
| VM09 Institutional billing | One account and predictable payments | A consolidated invoice on the published four-instalment schedule | A discount, credit or deferral | Finance approval |
| VM10 Sponsor-ready reporting | Evidence to share with their donors | A termly progress summary in an approved format, sent only to the authorised institution | Outcome guarantees, or sharing with donors without consent | Academic and safeguarding approval |
| VM11 Safeguarding and wellbeing | Confidence in care standards | Silverleaf's child-protection policy and an explanation of the wellness programme | Certification or specialist therapy | Policy confirmed as current |
| VM12 Transport | Practical daily access | The published transport bands | That a route is available | Operations confirms the route |
| VM13 Approved institutional terms | Affordability | The approved rate or bursary, cited by its terms ID | Any term without an `approved_offer_terms` row | Blocked until terms are approved |

VM04 (school fit) and VM05 (school experience) remain available.

**Copy rules:**
- Treat recipients with dignity; no pity or rescue framing.
- Never mention an individual child and never use images of children.
- Write in the recipient's published language, with native-speaker review for Kiswahili.
- A hook must be a verified fact about the institution, such as a published commitment to schooling. It must never be a child's story.

**Example direct opening** (no verified hook, 75 words):

> Subject: Planning school places for the coming year
>
> Dear [Name], I'm [sender name], [sender role] at Silverleaf Academy. Our five campuses in Arusha and Boma Ng'ombe offer daycare, pre-primary and English-medium primary education. We can offer a 20-minute conversation to map the ages in your care against our campus levels and the January intake, and to explain our published fees and four-instalment schedule. There is no commitment. Would a call next week help, or is there a colleague who handles school placements?

### 5.6 Flow and campaign (design only, disabled)

**F14: welfare consultative flow**

| Step | Trigger | Condition | Action | Pipeline stage |
|---:|---|---|---|---|
| 1 | Record selected for WA02 | Gates pass and a person has reviewed the draft | Call or email the published route | `contacted` |
| 2 | No reply | Stop checks pass | One follow-up after 4 working days | `contacted` |
| 3 | Conversation held | Admissions confirms the level and capacity | Record aggregate counts by age band | `needs_assessed` |
| 4 | Visit agreed | Safeguarding visit protocol confirmed | Two staff visit; no photography | `visit_held` |
| 5 | Visit held | Approved terms only | Send a proposal within 5 working days | `proposal` |
| 6 | Proposal accepted | Admissions assesses each child in Ed-admin, outside the lead database | Update the aggregate place counts | `placement` |
| 7 | Eight weeks before the next intake window | Account active | Check next year's places | `renewal` |

**Branches:**
- **A funder decides:** route to the funder with the institution's agreement.
- **Level or age mismatch:** close with a reason.
- **Budget timing:** hold with a dated next action.
- **Licence not confirmed:** return to WA00.
- **Safeguarding concern:** stop and escalate to Silverleaf's designated safeguarding lead. Nothing is automated.

**Campaign C10, Welfare institutional placements.** It stays inactive until all four of these are in place:
- a terms memo approved by Finance
- a safeguarding visit protocol
- confirmed January 2027 capacity by campus and level
- confirmed PDPC registration

### 5.7 Workbook and verification

**Workbook changes:**
- New sheets: *Welfare accounts* (organisation, profile, stage and next action) and *Welfare relationships*.
- Existing sheets gain a `lead_track` column.
- *Start here* shows counts by track.

**New `verify_master.py` checks:**
- no WA02 plan exists without an authority-confirmed licence
- no plan uses VM13 without an approved-terms row
- every plan uses only the modules allowed for its lead track
- no child-level field exists in the schema or the export
- the existing checks still pass

### 5.8 Test plan

| Layer | Cases |
|---|---|
| Unit: `tests/unit/test_validate_welfare.py` | A valid welfare row passes. Each of these fails: a missing `care_model`, a non-integer `children_served_published`, a child-level column, VM13 without terms, WA02 without a confirmed licence, a relationship row missing one side. Long AQ IDs normalise. |
| Unit: identity | The welfare organisation key is the institution's own domain, then its NGO registration reference, then name plus locality. The relationship key is from, to and type. |
| Unit: refresh | Welfare rows keep their tracks and modules after refresh, as a regression test for the overwrite trap. The corporate golden output is unchanged. |
| Unit: `campus_geo` | Band boundaries at 5, 10, 15, 20 and 25 km, and nearest-campus selection that respects the level required. |
| Integration: master path | Build a fixture master from the schema snapshot and migrate it to 0002. Preflight a welfare fixture: an existing home matches exactly, a similar name goes to review, and a new home inserts. Then merge, export (welfare sheets present) and verify. Verify passes on valid data and fails the named check on each negative fixture. |
| Integration: create path | A new welfare-only run initialises from a fixture intake, and the integrity and foreign-key checks pass. |
| Contract | Every track, module and segment in the registry appears in the data contract and both copies of the acquisition framework, and the reverse holds. The duplicated strategy documents stay identical. The export never contains a denylisted field. |
| Manual | Trace 10 enriched records to their snapshots. Keep licence-confirmation letters in `restricted/`, never in Git. Have a native speaker review the Kiswahili copy. |

Run `npm test`, then the update order in `.claude/CLAUDE.md`, finishing with `python scripts/master/verify_master.py`.

### 5.9 Build now, or add to `future-improvements.md`

**Build now:**
- Phase 0
- the welfare schema, collector and contract changes
- F14 and C10, as design only
- a reviewed pilot batch within 25 km, sized by what verification finds
- reclassification of the five existing records through review

**Future improvements:**
- Google Places enrichment
- licence-expiry reminders
- a donor-report generator
- moving the corporate collectors onto `campus_geo`
- CRM integration for the account pipeline
- extension to new campuses under the 12-campus plan

### 5.10 Indicative sequence

| When | Work |
|---|---|
| Week 1 | Phase 0 and migration 0002. In parallel, leadership drafts the offer memo with Finance, Academic and the safeguarding lead. |
| Week 2 | Collect and verify the pilot batch, and send licence-confirmation requests to the four councils. |
| Week 3 | Draft and review WA02 messages. The team makes the calls and visits itself; the tool stays draft-only. |

Aim to have verified institutions and approved terms by mid-October so that January placements fit the October–December primary window.

## 6. Documentation plan

After you confirm `docs/welfare-leads/`, create these files:
- `README.md` (current behaviour)
- `architecture.md`
- `operations.md` (the runbook)
- `future-improvements.md`
- `test-suite.md`

Then update:
- the data contract and workbook layout
- both copies of the acquisition framework
- the outreach skill, adding a new reference, `welfare-accounts.md`
- the create and update skills ("select the lead track")
- the README repository map
- the one-line pointers in `AGENTS.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md` and `.cursor/rules/lead-generation.mdc`

Regenerate `docs/database/master-schema.md` after each migration, and record new learnings.

## 7. File map

| Path | Change | Phase |
|---|---|---|
| `skills/silverleaf-create-lead-list/references/controlled-vocabularies.json` | New registry | 0 |
| `skills/silverleaf-create-lead-list/scripts/validate_intake.py` | Read the registry; add aliases, the denylist and welfare rules | 0, W |
| `skills/silverleaf-create-lead-list/scripts/initialize_lead_db.py` | New tables; `AQ00` default | 0, W |
| `skills/silverleaf-create-lead-list/assets/lead-intake-template.csv` | Welfare and relationship columns | W |
| `skills/silverleaf-create-lead-list/references/lead-list-data-contract.md`, `workbook-layout.md` | Tracks, fields, record types, sheets | 0, W |
| `skills/silverleaf-create-lead-list/references/track-welfare.md` | New research method for this track | W |
| `skills/silverleaf-update-lead-list/scripts/preflight_update.py` | Profile and relationship matching | W |
| `skills/silverleaf-update-lead-list/references/merge-and-reconciliation.md` | Migration step before a merge | 0 |
| `skills/silverleaf-outreach/SKILL.md`, `references/welfare-accounts.md` | Role map, modules, examples | W |
| `docs/strategy/new-lead-acquisition-framework.md` and its skill copy | WA tracks and VM08–VM13 | W |
| `scripts/master/migrate.py`, `migrations/0001_lead_tracks.py`, `migrations/0002_welfare.py` | New | 0, W |
| `scripts/master/refresh_acquisition_metadata.py` | Track-aware | 0 |
| `scripts/master/export_master_workbook_data.py`, `build_master_workbook.mjs` | Track column and welfare sheets | 0, W |
| `scripts/master/verify_master.py` | New checks | 0, W |
| `scripts/master/export_schema_snapshot.py`, `scripts/lib/campus_geo.py` | New | 0 |
| `scripts/collection/collect_welfare_leads.py`, `build_welfare_intake.py` | New | W |
| `data/raw/welfare-research/`, `data/interim/welfare-leads/` | New evidence folders | W |
| `outputs/config/automation-recipes.json` | F14 (disabled) and the WA schedule | W |
| `tests/unit/`, `tests/integration/`, `tests/fixtures/` | New | 0, W |
| `package.json`, `.gitignore` | Test scripts; `restricted/` and `.test-runs/` | 0 |
| `docs/database/`, `docs/_learnings/`, `docs/welfare-leads/` | Generated snapshot; learnings; feature docs after confirmation | 0, W |

**Boundaries:**
- The corporate collectors (`collect_partner_leads.js`, `build_partner_leads.py`) do not change.
- Parent acquisition (Track 2) is out of scope.
- Nothing sends a message or enables an automation.

## 8. Definition of done

- `npm test` passes, and so does `python scripts/master/verify_master.py` with its new checks.
- The before-and-after report reconciles counts, matches, inserts, review items and evidence gaps, as `AGENTS.md` requires.
- No automation is enabled, and neither the database nor the workbook holds any child-level data.
- The documentation and learnings are updated, the schema snapshot is regenerated, and residual risks are stated.

## 9. Decisions needed from Silverleaf

1. **Terms.** What institutional terms apply (rate, bursary, invoicing and instalments)? Finance and leadership decide.
2. **Capacity.** How many places per campus and level can go to institutional placements for January 2027?
3. **Safeguarding.** Who is the designated lead, what is the visit protocol, and what is the escalation route?
4. **Special needs.** Which needs can Silverleaf support well?
5. **Reporting.** What format should progress reports take, what consent do they need, and who may receive them?
6. **Boarding.** Should boarding at Usa River be offered for institutional placements? The default is not to lead with it.
7. **Ownership.** Who owns the welfare pipeline: Mariam Haji, Zuhura Msangi, or the Fundraising and Partnerships Associate still being hired?
8. **Data protection.** Is Silverleaf registered with the PDPC? Does the explicit-consent rule for direct marketing cover a first contact through a published institutional route? The second question also affects the corporate track.
9. **Reference case.** Is there an existing institutional family to use as a reference? Share aggregates only.
10. **Test commands.** The shared methodology names `yarn test` and `yarn test:needed`, but the repository uses npm. Should the commands use npm names (recommended), or should the repository adopt Yarn?

## 10. First run (22–23 September 2026) and research limits

**What exists now.** The first run, `arusha-welfare-2026-09`, was built as a separate run: its own database and workbook under `outputs/runs/arusha-welfare-2026-09/`, with the company master unchanged. Its scripts live in `scripts/welfare/`, with an identical copy bundled in the `silverleaf-welfare-leads` skill, and every input is committed, so the run rebuilds without network calls. The run's records cover:
- 497 organisations
- 131 contacts
- 3 parent enquiries
- 214 relationships
- the 898 NGOs registered within 30 km

Phase 0 (§4) is still to be built before these records merge into the master. The file map in §7 describes that target; the first run's working pieces live in `scripts/welfare/`.

**Limits the run hit.** These now shape the sequence in §5.10:

| Limit | What happened | Now |
|---|---|---|
| WebSearch per-session cap (200) | Eight parallel agents used it within about 40 minutes; most slices stopped before their stopping rule | Budget each agent with `plan_research.py`; run collectors first; at most four agents per wave |
| NGO register speed | About 2.2 seconds per profile; a sequential run averaged about 17 seconds | At most 4 workers, 0.3 seconds apart; 855 profiles in about 30 minutes |
| Overpass | A broad regex query returned HTTP 504 | Split queries, 5 seconds apart, mirror fallback |
| Blocked sources | UK charity register (403), JamiiForums, Facebook, Reddit, council sites that render in JavaScript | Recorded in coverage logs; never worked around |

The limits are documented in `skills/silverleaf-create-lead-list/references/research-rate-limits.md` and enforced in `scripts/welfare/welfare_lib.py`. The unsearched localities are listed per slice as `next_run_priorities` in `skills/silverleaf-welfare-leads/references/research-slices.json`, so the next run starts there.

## Sources

- [Ministry of Community Development, Gender, Women and Special Groups: children's home registration](https://www.jamii.go.tz/pages/children-s-home-registration), checked 22 September 2026
- [NGOs Information System: mapping search](https://nis.jamii.go.tz/mapping), checked 22 September 2026
- [Law of the Child Act, 2009 (TanzLII)](https://tanzlii.org/en/akn/tz/act/2009/21/eng@2024-10-11) · [Children's Homes (Regulation) Act, repealed (TanzLII)](https://tanzlii.org/en/akn/tz/act/1968/4/eng@2002-07-31)
- [Better Care Network: Tanzania](https://bettercarenetwork.org/regions-countries/africa/eastern-africa/tanzania)
- [Personal Data Protection Act, 2022 (PDPC)](https://www.pdpc.go.tz/media/media/THE_PERSONAL_DATA_PROTECTION_ACT.pdf) · [DLA Piper: data protection laws of Tanzania](https://www.dlapiperdataprotection.com/?t=law&c=TZ)
- [OpenStreetMap Wiki: Key:social_facility](https://wiki.openstreetmap.org/wiki/Key:social_facility)
- Internal: `references/Silverleaf Academy - Business Context Dossier.md` (levels, fees, instalments, intake windows, campuses), `docs/methodology/partner-lead-generation.md`, `docs/strategy/new-lead-acquisition-framework.md`, `docs/scope/scope-of-work.md` §7.2, and the master database as queried on 22 September 2026
