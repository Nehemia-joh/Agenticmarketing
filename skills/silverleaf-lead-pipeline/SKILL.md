---
name: silverleaf-lead-pipeline
description: The end-to-end technical pipeline that takes a Silverleaf lead from inception to its first draft carrying the request and the offer, across the company master, the welfare run and the government run. Use when planning or running any stage (segments and catchment, capture, intake and merge, geolocation, reach tiers, enrichment, contact research, email formats, hooks, recipients, variants, first-touch drafting, tracks, confidence segments, verification), or when you need to know which stage comes next and which skill or script owns it.
---

# Silverleaf lead pipeline

This skill is the map. It names every stage, in the order the scripts need, and points to the skill, document or script that owns the detail. It does not repeat those documents: read the owner before you run a stage.

The order comes from the scripts' own inputs and "afterwards run" notes, checked against `git log` (September to 13 October 2026). Where the history and the scripts differ, this skill follows the scripts and says so. Known gaps are in [references/known-gaps.md](references/known-gaps.md). How the three lists differ at each stage is in [references/list-differences.md](references/list-differences.md).

After any change, keep the outputs current with `skills/silverleaf-keep-outputs-current/SKILL.md`.

## The spine

```text
 DEFINE      1  Segments, catchment and bands
                 |
 CAPTURE     2  Capture leads (deterministic collectors first)
             3  Validate the intake, run the preflight
             4  Merge in one transaction (identity, dedupe, corrections)
                 |
 PLACE       5  Geolocate leads without a point (Google Maps lookups included)
             6  Distances, bands and reach tiers
                 |
 ENRICH      7  Plan research: ledger, playbook, budget   <- gate before every network step
             8  Enrich organisation records (no search budget)
             9  Research contacts (budgeted agents, browser pass, calls)
            10  Merge the research
            11  Email formats and inferred candidates (side track, always low)
            12  Hooks and lead briefs
                 |
 DRAFT      13  Choose one recipient per business (on the ground, with escalation)
            14  Assign the variant (A sponsorship, B staff benefit)
            15  Draft the first touch (cases A, B, C) and the offer (offer register)
            16  Assign acquisition tracks
                 |
 RELEASE    17  Classify by confidence and export the segments (Resend files)
            18  Verify, build the review outputs, commit
```

The welfare and government runs do stages 3, 4 and 13 to 16 inside one command, `scripts/<track>/run_pipeline.py --run-id <run-id> --rebuild-db`. Their curation lives in `data/runs/<run-id>/links.json`. The master does each stage with its own script, in one transaction each.

**Your list against the repository.** Segment definition (1), lead capture (2), enrichment (8), geolocation (5), contact research (9 and 10), classification by confidence (17) and draft preparation (13 to 16) are all here. Two orders differ from the list:
- Geolocation comes before enrichment. Distance feeds the reach tiers (6), and the planners rank research by tier and distance.
- Confidence is computed after drafting. `export_resend_contacts.py` reads each finished draft's review status and holds. The drafter's first-touch case (A, B or C) uses the same facts, so the two agree.

## Rules for every stage

- **Evidence.** Every claim keeps its source URL, the date read, a short excerpt and a source record. A hook without a sourced claim stays blank.
- **Nothing inferred is presented as found.** A contact detail counts as published only when a source publishes it for that person or role. The one exception is a labelled email-format candidate (stage 11).
- **Privacy.** No parent, resident, child or household data. No party affiliation. `pdpa_risk` on every person. Personal social profiles and data brokers are off-limits (`docs/methodology/contact-research.md`).
- **Limits.** Never work around a cap, a block, a bot check or a login. Read `skills/silverleaf-create-lead-list/references/research-rate-limits.md` before any network step. At most four research agents at a time.
- **The ledger.** Check `scripts/research/ledger.py tried --org <id>` before any search, and ingest every finished slice, Maps round and browser pass before the merge.
- **Keep every lead, labelled.** Distance, an incomplete name or a correction never deletes a lead. Holds, review items and `name_status` label it instead.
- **One transaction per master change**, after validation and preflight. Preview first; `--apply` second.
- **Drafts only.** Sending and automations stay disabled.

## 1. Segments, catchment and bands

- **Purpose.** Fix who counts as a lead and how distance ranks it, before anything is collected.
- **Inputs.** Campus points: the master's `campuses` table, taken from the map pins on silverleaf.co.tz. Run configs: `data/runs/<run-id>/run-config.json` (scope, bounding box, `catchment_km`, councils and campus clusters).
- **Outputs.** `outputs/messages/Silverleaf Catchment Criteria - <date>.md` and `Silverleaf Core Segments - <date>.md`. Both are written by hand from the scripts' rules. No script writes them.
- **Rules.** The catchment is 25 km in a straight line from the nearest campus. Bands are 0-5, 6-10, 11-15, 16-20, 21-25, 26-40 and over 40 km. Tiers are Core (10 km or less), Outer (25 km or less) and beyond. These come from `recompute_campus_distances.py`. Four core segments: employers (with savings groups), introducers, welfare, government. Subsegments are the employer kind (`build_company_audience_profile.kind_of`), variant and reach tier; the welfare kind and priority; the government office level and ward wave.
- **Done when.** The campus points and the run configs agree, and both documents state the current rules.
- **Owners.** `docs/methodology/partner-lead-generation.md` section 4, `docs/strategy/partnership-pipelines.md` section 2, `docs/plans/vicoba-integration-plan.md` (savings groups).

## 2. Capture leads

- **Purpose.** Find the organisations. Deterministic collectors come first, because they cost no search budget.
- **Master.**
  - The first list (September) came from `scripts/collection/collect_partner_leads.js` (browser console on tatotz.org) and `build_partner_leads.py`. The import that built the master is not in `scripts/`.
  - The gap census: `collect_gap_census.py --date <d>`, the coordinator's Google Maps pins (`data/raw/gap-census/google_maps_named_<d>.jsonl`), targeted records (`research_targeted_<d>.jsonl`), then `build_gap_census.py --date <d>`. It writes `master_intake_<d>.csv`, the welfare records, village points and `outputs/reports/campus-gap-census-<d>.md`.
  - Introducers: a research agent writes `data/raw/contact-research/introducers_*_<d>.jsonl`.
- **Welfare.** `fetch_ngo_register.py --run-id <r>`, `collect_osm_welfare.py --run-id <r>`, then discovery agents planned by `plan_research.py` (stage 7).
- **Government.** `collect_census_wards.py`, `collect_ward_locations.py`, `collect_osm_government.py` and `collect_council_sites.py`, each with `--run-id <r>`; then `scan_official_documents.py --run-id <r> --date <d>`. A scanned roster is transcribed by hand into `data/raw/government-research/transcriptions/`.
- **Rules.** Collectors reuse their cache unless `--refresh`. Overpass runs one query at a time with a mirror fallback. The census collector fails unless wards add up to council totals.
- **Done when.** The raw files are in `data/raw/<source>/`, every unreached area is in a coverage log, and the network attempts are in the ledger.

## 3. Validate the intake and run the preflight

- **Purpose.** Prove the rows fit the shared contract and see every match before anything is written.
- **Commands (master).**
  ```powershell
  python skills/silverleaf-create-lead-list/scripts/validate_intake.py <intake.csv> --report <validation.json>
  python skills/silverleaf-update-lead-list/scripts/preflight_update.py "outputs/master/Silverleaf Master Database.sqlite" <intake.csv> --report <preflight.json>
  ```
  `merge_master_contacts.py` (without `--apply`) runs both for a contact wave and writes `runtime/contacts/master-contact-validation.json` and `master-contact-preflight.json`.
- **Runs.** The pipeline validates `data/runs/<r>/intake.csv` into `outputs/runs/<r>/intake-validation.json` and stops on an error.
- **Done when.** No validation errors, and you have read the preflight's exact matches, inserts and review signals. Fuzzy similarity is a review signal, never a merge.
- **Owners.** `skills/silverleaf-create-lead-list`, `skills/silverleaf-update-lead-list` and its `references/merge-and-reconciliation.md`.

## 4. Merge in one transaction

- **Purpose.** Add new leads without losing an ID, a source or an earlier value.
- **Master scripts** (each previews by default; `--apply` writes in one transaction):
  - `scripts/master/add_gap_census_leads.py --date <d> --apply`. Add `--geocodes` to write the points file for stage 5.
  - `scripts/master/add_introducers.py --date <d> --apply`.
  - `scripts/master/apply_employer_corrections.py --apply`, from `data/reference/employer-corrections.json`: refile a segment, correct a website or phone, or hold a lead outside the catchment.
  - `scripts/master/repair_shifted_fields.py --apply` for TATO rows imported one column out.
  - `scripts/master/apply_organisation_relations.py --apply`, from `data/reference/organisation-relations.json`: reviewed duplicates and branches.
- **Dedupe.** Match exact identifiers first: OSM ID, website domain, normalised name. A similar name goes to review. Nothing is deleted. Duplicates are collapsed for sending at stage 13, and shared inboxes at stage 17.
- **Runs.** Reviewed decisions go in `links.json`. Welfare uses `nis_to_org`, `org_aliases`, `master_ids` and `osm`; government uses `ward_aliases` and `osm_office_links`. Then rebuild the run.
- **Done when.** The preflight's insert count equals the rows added. Old IDs still exist. Every new row has a source record. `verify_master.py` passes.

## 5. Geolocate leads without a point

- **Purpose.** Give each lead a point, because a draft states a campus distance only from a point (since 13 October 2026).
- **Collect** (no web search; candidates go to `runtime/geocode/`):
  ```powershell
  python scripts/maps/collect_geocodes.py inventory
  python scripts/maps/collect_geocodes.py repo
  python scripts/maps/collect_geocodes.py sites --scope unplaced --fetch
  python scripts/maps/collect_geocodes.py osm
  python scripts/maps/collect_geocodes.py nominatim --scope unplaced
  python scripts/maps/collect_geocodes.py review --write data/raw/geocode-research/geocodes_<label>_<d>.jsonl
  python scripts/maps/collect_geocodes.py worklist --out <worklist.json>
  ```
- **Google Maps lookups.** Only the coordinator does these, in its own browser pane, which must be visible (a hidden pane does not finish rendering and the extractor records nothing). The user signs in when a sign-in is needed. Each lookup navigates to the search and runs the extractor (`eval(localStorage.slsync)("<id>")`); the results collect in localStorage `slres` (format in the docstring of `build_gmaps_round.py`).
  - Write one verdict line per lead: `A <id>`, `R <id>[|note]`, `V <id>|note` or `O <id>|note`. An exact name pinned far from the lead's town is `V`.
  - Build the round's files:
    ```powershell
    python scripts/maps/build_gmaps_round.py --date <d> --tag <round> --rows <worklist slice> --results <slres export> --notes <notes.txt> --db <pre-round master backup>
    ```
    It writes `data/raw/gap-census/google_maps_enrich_<d><round>.jsonl`, the fills `geocodes_gmaps_<d><round>.jsonl` and the replacements `geocodes_corrections_gmaps_<d><round>.jsonl`.
  - Shared-pin check (by default): every listing of this round and every other round is grouped by coordinates rounded to four decimals. An accepted listing on a point shared with a differently named listing and without a street address, or on a known default pin (`docs/methodology/research-playbook.md`, "Google Maps traps"), goes to `review` with the reason. Two listings with street addresses on one point are one building and stay. Read every downgrade; `--keep <id>` keeps one a person has checked.
  - Ingest the round: `python scripts/research/ledger.py ingest data/raw/gap-census/google_maps_enrich_<d><round>.jsonl`.
- **Apply.**
  ```powershell
  python scripts/master/apply_geocodes.py --file data/raw/geocode-research/<file>.jsonl                 # preview
  python scripts/master/apply_geocodes.py --file data/raw/geocode-research/<file>.jsonl --apply
  python scripts/master/apply_geocodes.py --replace --file data/raw/geocode-research/geocodes_corrections_<...>.jsonl --apply   # master only
  ```
  The master's empty points are filled. Welfare gets `geo_overrides`, and government gets `ward_locations` and `office_locations` in their `links.json`. `--db master|welfare|government` limits the run to one list.
- **Rules.** Never overwrite a point except with `--replace` and a reviewed corrections file. A correction that moves a lead beyond 25 km needs a reviewed `beyond_catchment` note; the lead is kept and gets a review item.
- **Done when.** The preview shows no conflicts. Every applied line has a source URL, a date, `as_found` and a basis. The round is in the ledger.

## 6. Distances, bands and reach tiers

```powershell
python scripts/master/recompute_campus_distances.py --apply [--report outputs/reports/campus-distance-recompute-<label>-<d>.json]
python scripts/master/rank_employer_reach.py --apply
```

- **Purpose.** Recompute the nearest campus, distance, band and tier from the `campuses` table and the new points. Then rank the employers P1 (top 100), P2 (next 150), P3 (the rest) or X (held).
- **Rules.** Distance never removes a lead. A map-only lead ('Raw OSM') ranks after every curated lead until it is matched.
- **Runs.** Welfare scores priority, and government scores wards and ward waves, inside their builds.
- **Done when.** The recompute report is written. `employer_reach` holds one row per company with a chosen draft.
- **Order note.** The reach rank reads the chosen plans (stage 13), and the drafter reads the tiers (stage 15, the ', or your HR lead' line). After a change in either, re-run the rank and then the drafter. Both are idempotent.

## 7. Plan research: ledger, playbook, budget

- **Purpose.** Spend searches only where they can pay, and never twice.
- **Before planning.** Read `docs/methodology/research-playbook.md`. Run `python scripts/research/ledger.py tried --org <id>` and `stats --by tool --by family`.
- **Planners.** Each one writes the already-tried lists into the prompts and skips organisations whose open patterns are used up within 90 days:
  - contacts: `scripts/contacts/plan_contact_research.py --date <d> --wave <n> --budget <n> [--target routes|decision-makers|all|direct-email] [--rank tier|reach] [--max-per-slice N --split] [--dry-run]`;
  - welfare: `scripts/welfare/plan_research.py --run-id <r> --search-budget 200 --already-used <n> [--only <slices>]`;
  - hooks: `scripts/messaging/plan_hook_research.py --date <d> --track AQ02 --budget <n>`;
  - browser pass: `scripts/contacts/plan_browser_pass.py --date <d>`.
- **Rules.** The 200-search cap is shared by every agent in the session. At most four agents at a time. Keep 10% in reserve for the coordinator. P3 employers get no searches. Savings groups and government offices are never planned for search.
- **Done when.** Each agent has a prompt with its allocation, its already-tried list and its output paths.

## 8. Enrich organisation records (no search budget)

- **Purpose.** Fill the website, routes, address, size and social pages from the organisations' own sites and open data.
- **Commands.**
  ```powershell
  python scripts/contacts/crawl_org_websites.py --date <d> [--deep --orgs <json>] [--only <domain>...] [--reextract]
  python scripts/contacts/collect_osm_contacts.py --date <d>
  python scripts/contacts/extract_direct_emails.py --date <d> --write
  python scripts/contacts/import_google_maps_lookups.py --file data/raw/gap-census/google_maps_enrich_<d><round>.jsonl --round <x> --date <d> --write [--closure <org_id>]
  ```
  The Maps import writes `browser_googlemaps_<round>_<d>.jsonl` (listing phone, website and street address) and `osm_matches_<d><round>.jsonl`. Apply the matches with `add_gap_census_leads.py --matches <file> --apply` before drafting.
- **Rules.** robots.txt Disallow is honoured by the crawler. A disallowed site is read only with the browser and tagged risky. Values shared by three or more sites, hotlines, placeholders and entries in `data/reference/rejected-routes.json` never become routes. Ingest each crawl with `ledger.py ingest data/raw/contact-research/website_contacts_<d>.jsonl`.
- **Measure.** `scripts/master/measure_master_coverage.py --label before`, `scripts/welfare/measure_welfare_coverage.py --run-id <r>` and `scripts/government/measure_government_coverage.py --run-id <r>`, before and after the round.

## 9. Research contacts

- **Purpose.** Name the decision-maker for each organisation and find their own published work route.
- **Search agents.** Each agent follows the brief in `docs/methodology/contact-research.md` and writes `data/raw/contact-research/search_<slice>_<d>.jsonl` plus a coverage log. Welfare agents write `data/raw/welfare-research/research_<slice>_<name>_<d>.jsonl` per `skills/silverleaf-welfare-leads/references/research-brief.md`.
- **Browser pass.** Agents read only the sites the crawler could not use, and write `browser_<slice>_<d>.jsonl`. They use no search, never pass a bot check, and count toward the four agents.
- **Calls.** `scripts/contacts/build_call_sheet.py` (P1 and P2) or `--run-id <welfare run>`. Import with `import_call_results.py <sheet.xlsx> --date <d> [--welfare]`. Consent is recorded.
- **Government.** No web search. Holders come only from official rosters, official news (`holder_mentions`) and reviewed `post_holders_*.json`.
- **Done when.** Every slice has its file and coverage log. `ledger.py ingest <coverage log> <research file> [<pending file>]` has run for each, before the merge.

## 10. Merge the research

**Master** (try it on a copy first, as `docs/methodology/contact-research.md` requires):

```powershell
python scripts/contacts/build_contact_profiles.py --date <d>
python scripts/contacts/build_contact_workbook.py --date <d> --baseline
python scripts/master/screen_profile_people.py --apply
python scripts/contacts/merge_master_contacts.py                 # intake, validator, preflight: read both reports
python scripts/contacts/merge_master_contacts.py --apply
python scripts/master/update_master_contacts.py --date <d> --apply   # people already on file
python scripts/contacts/build_contact_workbook.py --date <d>
```

**Welfare and government:**

```powershell
python scripts/contacts/export_run_contact_research.py
python scripts/welfare/apply_research_reviews.py --run-id arusha-welfare-2026-09 --date <d> --apply   # when agents filed reviews
python scripts/welfare/run_pipeline.py --run-id arusha-welfare-2026-09 --rebuild-db
python scripts/government/run_pipeline.py --run-id arusha-government-2026-09 --rebuild-db
```

- **Rules.** A merge fills only empty fields. A conflict goes to review. A held draft is released only when a missing route was its sole gap.
- **Done when.** The merge report is in `outputs/contacts/master-contact-merge.json`, and both run verifications pass.

## 11. Email formats and inferred candidates (side track)

- **Rule.** `docs/methodology/contact-research.md`, "Email formats" (11 October 2026). A format is recorded only from two or more published addresses of two named people at the organisation's own domain.
- **The candidate.** Always low confidence, labelled "inferred from format, unverified". It is kept apart from every route and out of committed files. It is never a draft's route and never a high segment. A person confirms it before any use. One exact-address search may confirm it as published.
- **Commands.**
  ```powershell
  python scripts/contacts/email_formats.py build            # preview: runtime/contacts/email-formats-proposed.json
  python scripts/contacts/email_formats.py build --write    # data/reference/email-formats.json; review the diff before committing
  python scripts/contacts/email_formats.py candidates       # runtime/contacts/inferred-candidates.json (never committed)
  python scripts/contacts/email_formats.py check            # no generated address in a tracked file, a route or the reference file
  ```
  `export_resend_contacts.py` (stage 17) writes the `<track>-low-inferred.csv` files from the same rules. The master workbook shows only the format (`email_format_to_confirm`). The 2 October script `infer_candidate_emails.py` is removed; `email_formats.py retire-table --apply` drops its old table `candidate_emails` from the master.
- **Done when.** `check` exits 0 and the reference file's diff has been reviewed. Re-run `build --write` after a contact merge: new published addresses are new evidence.

## 12. Hooks and lead briefs

```powershell
python scripts/messaging/plan_hook_research.py --date <d> --track AQ02 --budget <n> [--only-unresearched]
# agents write data/raw/hook-research/hooks_<slice>_<d>.jsonl and coverage logs; ingest them into the ledger
python scripts/messaging/apply_hook_research.py --date <d>            # preview
python scripts/messaging/apply_hook_research.py --date <d> --apply
```

- **Purpose.** Sourced lead-brief facts (`lead_briefs`), verified hooks and role checks. A staff number fills an empty headcount, which the reach rank reads.
- **Rules.** `skills/silverleaf-outreach/references/hook-guidance.md`. A hook needs the exact claim, its URL and a verification date; otherwise it stays blank.
- **Done when.** `verify_master.py` reports `hooks_supported`, `hooks_link_to_sources` and `lead_briefs_traceable` as true.

## 13. Choose one recipient per business

```powershell
python scripts/master/resolve_master_recipients.py          # preview: runtime/master/recipient-selection-preview.json
python scripts/master/resolve_master_recipients.py --apply  # records outputs/messages/master-recipient-selection.json
```

- **Purpose.** Collapse duplicate records for sending, and choose the most senior person running the Tanzania or Arusha operation. A group, regional or global head becomes the escalation contact (`escalation_*` columns). It is never copied on the first message.
- **Rules.** Board roles are never chosen. A chair is chosen only when no executive is named. An HR assistant never outranks the head. Reviewed exceptions are in `data/reference/recipient-overrides.json` (`excluded_contacts`, `role_confirmed`).
- **Welfare.** `draft_run_messages.py` applies the same rule, with `links.json` `recipient_exclusions` and `recipient_choices`.
- **Done when.** One chosen plan (`selection = 'Candidate for review'`) per business.

## 14. Assign the variant (master)

```powershell
python scripts/master/assign_message_variants.py --apply   # then re-runs resolve_master_recipients.py --apply itself
python scripts/messaging/draft_employer_sponsorship.py     # review file outputs/messages/Silverleaf Employer Sponsorship Drafts - <date>.md
```

- **Rule.** Variant A (sponsorship) goes only to strong-fit funders of education in `data/reference/employer-sponsorship-reasons.json`. Variant B (staff-benefit partnership) goes to every other company. Savings groups get n/a. Welfare funders get the sponsorship ask in their own run.

## 15. Draft the first touch and the offer

```powershell
python scripts/messaging/draft_master_messages.py [--dry-run]
```

Runs draft with `scripts/messaging/draft_run_messages.py --track welfare|government --run-id <r>`, a step inside each `run_pipeline.py`.

- **Request first.** The first message asks for a short meeting and states no offer terms. The offer follows: in `offer_message` and follow-up 1 on AQ02, or as the reply on AQ01. Terms come only from `data/reference/silverleaf-offer-register.json`, through `offer_lib`.
- **First-touch cases** (`scripts/messaging/first_touch.py`; `docs/strategy/partnership-pipelines.md` sections 4 and 5):
  - A: a named person at their own or role address gets the letter unchanged.
  - B: a named person reached only through a general inbox gets the Attn subject and routing line. Follow-up 1 is the offer, follow-up 2 a redirect-style close, then an escalation note.
  - C: no named person gets the short redirect request, with blank follow-ups.
- **Exceptions.** Government letters are Kiswahili with the English meaning, delivered by hand, and offer officials nothing. Savings groups are unchanged.
- **Done when.** The drafter reports `conformance_issues` 0 (it refuses to write otherwise) in `outputs/messages/master-offer-messages-reconciliation.json`.
- **Owner.** `skills/silverleaf-outreach` and its `references/offer-register.md`.

## 16. Assign acquisition tracks

```powershell
python scripts/master/refresh_acquisition_metadata.py
```

AQ00 for a held plan. AQ02 for case B (except variant A sponsorship). Otherwise AQ01 for a referral call to action and AQ02 for the rest. Welfare uses WA00 and WA01, government GA00 to GA02, set inside the runs. Owner: `docs/strategy/new-lead-acquisition-framework.md`.

## 17. Classify by confidence and export the segments

```powershell
python scripts/messaging/export_resend_contacts.py        # companies, introducers, welfare and government
```

- **Bands.**
  - high: ready, not held, and a verified named decision-maker on the organisation's own domain or their own address. It splits into `-high-direct` (their own mailbox by the strict test, or their role's inbox) and `-high-indirect`.
  - medium: ready, but an organisation inbox.
  - low: held or needs research.
  - no email: phone only.
- **Outputs.** CSVs in `runtime/resend/<date>/` (never committed; they hold addresses). `outputs/messages/Silverleaf Resend Segments - <date>.md` and `Silverleaf Government Segments - <date>.md` (committed). The government track gives a delivery list per segment.
- **Rules.** Nothing is sent. `load_resend_contacts.py` only loads contacts, and only with the user's key and go-ahead.

## 18. Verify, build the review outputs, commit

The full order, the checks and the commit rules are in `skills/silverleaf-keep-outputs-current/SKILL.md`. In short: the master workbook (`npm run build:workbook`), `verify_master.py`, both run pipelines, `scripts/maps/build_lead_map.py`, the Resend export, `build_offer_messages_workbook.py --date <d>`, then the review files. Report before and after counts, matches, inserts, conflicts and gaps.
