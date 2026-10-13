# What each script reads and writes

This table was taken from the scripts themselves on 13 October 2026: their docstrings, their path constants, the SQL statements that write, and their imports. "Master" is `outputs/master/Silverleaf Master Database.sqlite`. "Run DB" is `outputs/runs/<run-id>/lead-database.sqlite`. Files in `runtime/` are never committed.

## Rebuild chain

| Script | Reads | Writes |
|---|---|---|
| `scripts/master/recompute_campus_distances.py --apply` | Master `campuses`, `organisations`, latitude and longitude facts; `data/reference/lead-gazetteer.txt` | Master `organisations` (nearest campus, distance, band, tier); `outputs/reports/campus-distance-recompute.json` (or `--report`) |
| `scripts/master/rank_employer_reach.py --apply` | Master chosen plans (`selection = 'Candidate for review'`), kind, headcount, hooks, named contacts, distance band, holds | Master table `employer_reach` (replaced) |
| `scripts/master/assign_message_variants.py --apply` | Master; `data/reference/employer-sponsorship-reasons.json` (through `draft_employer_sponsorship.py`) | Master `outreach_plans` (`message_variant`, `variant_reason`, `variant_subject`, `variant_body`); then runs `resolve_master_recipients.py --apply` |
| `scripts/master/resolve_master_recipients.py --apply` | Master; `data/reference/recipient-overrides.json`; `data/reference/organisation-relations.json` | Master `outreach_plans` (`selection`, `escalation_*`), `contacts`, `review`, `facts`, `campaign_lead_assignments`; `outputs/messages/master-recipient-selection.json` |
| `scripts/messaging/draft_master_messages.py` | Master (including `employer_reach`); `data/reference/silverleaf-offer-register.json` and `organisation-display-names.json` (through `offer_lib`); `first_touch.py`; rules imported from `resolve_master_recipients`, `export_resend_contacts`, `merge_master_contacts` | Master `outreach_plans`, `messages`, `message_versions`, `campaign_lead_assignments`, `strategies`, `value_proposition_modules`; `outputs/messages/master-offer-messages-reconciliation.json` (`conformance_issues`) |
| `scripts/master/refresh_acquisition_metadata.py` | Master | Master `outreach_plans` (track, modules), `campaign_lead_assignments`, `acquisition_refresh_runs` |
| `scripts/master/export_master_workbook_data.py` | Master; `outputs/contacts/master-contact-merge.json`; `outputs/messages/master-offer-messages-reconciliation.json`; `data/reference/email-formats.json` (format text only) | `runtime/artifacts/workbook-input.json` |
| `scripts/master/build_master_workbook.py` (`npm run build:workbook`) | `runtime/artifacts/workbook-input.json` | `outputs/master/Silverleaf Master Database - Consolidated.xlsx`; `outputs/reports/workbook-verification.json` |
| `scripts/master/verify_master.py` | Master (read-only), the workbook, the whole tree (debris) | `outputs/reports/master-verification.json` (holds the absolute DB and workbook paths) |
| `scripts/welfare/run_pipeline.py --rebuild-db` | `data/runs/<r>/run-config.json` and `links.json`; `data/raw/welfare-research/*` (`research_files` globs, register, OSM); master `campuses` and IDs (read-only); `lead-gazetteer.txt`; `rejected-routes.json`; the offer register | `runtime/welfare/<r>/` (baseline, `final.json`); `data/interim/welfare-leads/*.tsv`; `data/runs/<r>/intake.csv`; `data/raw/welfare-research/MANIFEST.md`; run DB; `outputs/runs/<r>/` workbook, `intake-validation.json` (absolute path), `run-verification.json` |
| `scripts/government/run_pipeline.py --rebuild-db` | `data/runs/<r>/run-config.json` and `links.json`; `data/raw/government-research/*` (census, council sites, OSM, transcriptions, `post_holders_*.json`, `office_contacts_*.json`); `subward_units_files` (gap census villages); reviewed points only through `links.json` (written by `apply_geocodes.py`); master `campuses` and `office:government` records (read-only); the offer register | `runtime/government/<r>/`; `data/interim/government-leads/*.tsv`; `data/runs/<r>/intake.csv`; `data/raw/government-research/MANIFEST.md`; run DB; `outputs/runs/<r>/` workbook and reports |
| `scripts/maps/build_lead_map.py` | Master and both run DBs (read-only); rules imported from `export_resend_contacts` and `build_company_audience_profile`; `data/reference/maps/` basemap; `data/raw/geocode-research/geocodes_*.jsonl`; `scripts/maps/lead_map_template.html` | `outputs/maps/Silverleaf Lead Map.html` |
| `scripts/messaging/export_resend_contacts.py` | Master and both run DBs (read-only), including `employer_reach` and contact-profile source records; `offer_lib`; `data/reference/email-formats.json` (through `email_formats.py`) | `runtime/resend/<date>/*.csv` (not committed), including `<track>-low-inferred.csv`; `outputs/messages/Silverleaf Resend Segments - <date>.md` and `Silverleaf Government Segments - <date>.md` |

## Changes that feed the chain

| Script | Reads | Writes |
|---|---|---|
| `skills/silverleaf-create-lead-list/scripts/validate_intake.py` | An intake CSV | `--report` JSON |
| `skills/silverleaf-update-lead-list/scripts/preflight_update.py` | Master (read-only), an intake CSV | `--report` JSON |
| `scripts/master/add_gap_census_leads.py` | `data/raw/gap-census/master_intake_<d>.csv`; `--matches osm_matches_<d><round>.jsonl` | Master organisations, source records, facts, review; `--geocodes`: `data/raw/gap-census/geocodes_gap_census_<d>.jsonl` |
| `scripts/master/add_introducers.py` | `data/raw/contact-research/introducers_*_<d>.jsonl`; `data/reference/introducer-decisions.json` | Master organisations, contacts, sources |
| `scripts/master/apply_employer_corrections.py` | `data/reference/employer-corrections.json` | Master `outreach_plans` holds and segments, organisation fields, facts, review |
| `scripts/master/apply_organisation_relations.py` | `data/reference/organisation-relations.json` | Master `entity_sources`, facts, review |
| `scripts/master/repair_shifted_fields.py` | Master | Master organisations, facts, review |
| `scripts/maps/build_gmaps_round.py` | Worklist rows, browser results (`slres`), verdict notes; the pre-round master (read-only); every `data/raw/gap-census/google_maps_enrich_*.jsonl` (shared-pin check) | `data/raw/gap-census/google_maps_enrich_<d><tag>.jsonl`; `data/raw/geocode-research/geocodes_gmaps_<d><tag>.jsonl` and `geocodes_corrections_gmaps_<d><tag>.jsonl`; `runtime/geocode/gmaps_round_<d><tag>_check.json` |
| `scripts/master/apply_geocodes.py` | `data/raw/geocode-research/<file>.jsonl` (default: the newest `geocodes_*.jsonl`) | Master organisations, facts, sources, review; welfare `links.json` `geo_overrides`; government `links.json` `ward_locations` and `office_locations`; preview in `runtime/geocode/` |
| `scripts/contacts/build_contact_profiles.py` | `data/raw/contact-research/` (`website_contacts_`, `osm_contacts_`, `search_*_`, `browser_*_`, `website_direct_` for the date); all three DBs (read-only); `rejected-routes.json` | `runtime/contacts/profiles.json` and summary; `data/interim/contact-profiles/*.tsv` |
| `scripts/master/screen_profile_people.py --apply` | `data/reference/employer-people-exclusions.json` | `runtime/contacts/profiles.json` |
| `scripts/contacts/merge_master_contacts.py --apply` | `runtime/contacts/profiles.json`; `rejected-routes.json`; `organisation-relations.json` | Master organisations, contacts, facts, sources, review, `outreach_plans` holds; `outputs/contacts/master-contact-merge.json` |
| `scripts/master/update_master_contacts.py --apply` | `search_*_<d>`, `browser_*_<d>` and `website_direct_<d>` research files | Master contacts, `outreach_plans`, facts, sources, review |
| `scripts/contacts/export_run_contact_research.py` | `runtime/contacts/profiles.json`; run configs | `data/raw/welfare-research/research_W_contact_profiles_<d>.jsonl` (and the run's `research_files`); `data/raw/government-research/office_contacts_<d>.json` |
| `scripts/welfare/apply_research_reviews.py --apply` | Welfare `research_*_<d>.jsonl` review fields | Welfare `links.json` (`flags_cleared`, `official_personal_inboxes`) |
| `scripts/messaging/apply_hook_research.py --apply` | `data/raw/hook-research/hooks_*_<d>.jsonl` | Master `lead_briefs`, `outreach_plans` hooks, contacts, organisations (headcount), review; `data/raw/hook-research/MANIFEST.md`; `outputs/messages/hook-research-apply.json` |
| `scripts/contacts/email_formats.py build --write` / `candidates` | Master and welfare run (read-only); `data/raw/contact-research/*.jsonl` | `data/reference/email-formats.json` (formats, no addresses); `runtime/contacts/inferred-candidates.json` (never committed) |
| `scripts/research/ledger.py ingest` | Coverage logs, research JSONL, Maps lookup, geocode and crawl files; `runtime/contacts/profiles.json` when present | `data/raw/research-ledger/research_ledger.jsonl` |
| `scripts/strategy/render_markdown_page.py` | A Markdown document | One HTML page (Mermaid loaded from a CDN when viewed) |

## Readers of the reference files

| Reference file | Read by |
|---|---|
| `silverleaf-offer-register.json` | `offer_lib.py` and so every drafter, exporter and consolidator; `build_offer_messages_workbook.py`. `build_master_workbook.py` only names it in sheet text (a wording change there needs a code edit) |
| `organisation-display-names.json` | `offer_lib.py` (every drafter) |
| `employer-sponsorship-reasons.json` | `assign_message_variants.py`, `draft_employer_sponsorship.py` |
| `recipient-overrides.json` | `resolve_master_recipients.py` |
| `organisation-relations.json` | `apply_organisation_relations.py`, `resolve_master_recipients.py`, `merge_master_contacts.py` |
| `rejected-routes.json` | `build_contact_profiles.py`, `merge_master_contacts.py`, `consolidate_research.py` (welfare), `analyse_high_direct_pool.py` |
| `employer-corrections.json` | `apply_employer_corrections.py` |
| `employer-people-exclusions.json` | `screen_profile_people.py` |
| `introducer-decisions.json` | `add_introducers.py` |
| `lead-gazetteer.txt` | `welfare_lib.py`, `recompute_campus_distances.py`, `build_lead_map.py`, `build_gap_census.py`, `add_gap_census_leads.py`, `build_partner_leads.py` |
| Master `campuses` table | `welfare_lib.load_campuses` (both runs), `recompute_campus_distances.py`, `build_lead_map.py`, `build_gap_census.py` |
