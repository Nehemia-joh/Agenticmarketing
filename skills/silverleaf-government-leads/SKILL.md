---
name: silverleaf-government-leads
description: Research and build an evidence-backed list of local government offices that can convene community meetings (councils, wards, villages, district and regional offices) near Silverleaf's campuses, with their official posts, 2022 census ward populations and ward priorities, in a separate run database and review workbook. Use for a new government-lead run, a refresh of an existing one, or reusing its census, map and council-site files. Keeps the company-leads master untouched and never collects parent or resident data.
---

# Silverleaf government leads

Build a government-lead run with the scripts in `scripts/government/`, the repository's home for reusable scripts (see `scripts/README.md`). This skill bundles an identical copy in its own `scripts/` folder. Edit `scripts/government/` first and copy it across; verification fails if the two differ. The shared library `gov_lib.py` builds on `scripts/welfare/welfare_lib.py`, so run the scripts inside the repository.

A government lead is a **convening office**, not a buyer and not a person. Its value is a trusted forum where parents already gather: a village assembly, a mtaa or ward meeting, or a council event. Parents who choose to hear more opt in with Silverleaf at the event, into a separate consented store; they never enter this run. The method and the business case are in `plans/b2b-government-leads-plan.md`. The first run, `arusha-government-2026-09`, is the worked example to reuse and extend.

## Outputs

Everything stays separate from `outputs/master/` and from the welfare runs.

| Path | Contents |
|---|---|
| `data/runs/<run-id>/` | `run-config.json`, `links.json` (reviewed curation), `intake.csv` |
| `data/raw/government-research/` | Census ward tables, Wikipedia ward points, OpenStreetMap places, districts and offices, council-site captures, transcriptions, `MANIFEST.md` with hashes |
| `data/interim/government-leads/` | Administrative units, offices, posts, office triage, master triage and convening signals (TSV) |
| `outputs/runs/<run-id>/` | `lead-database.sqlite` (ignored by Git), the review workbook, `intake-validation.json`, `run-verification.json` |
| `runtime/government/<run-id>/` | Scratch space (ignored by Git): HTTP cache (census PDF, attachments), `final.json`, `review_items.json`, master baseline |

## Rules

- **Offices first.** Record offices and role desks. Record a holder's name only where an official roster or profile publishes it, with `holder_verified_on` and `tenure_source_url`. A new holder is a review item, not a new contact.
- **Political neutrality.** Never record party offices, party events or party affiliation, even where a list shows it. Approach administrative offices first; engage elected leaders only through the forum they chair.
- **Exclusions.** Party offices, courts, police, prisons, military sites, health facilities, schools and religious sites are logged with their reason and never become offices. Only a documented review decision can override one.
- **No lists of people.** Never take resident, voter, beneficiary or pupil lists, and never collect parents' data. `community_events` holds counts only.
- **Official phone numbers** are kept only when the office published them for contacting that post, with the publication named in `channel_attribution`, and they are `medium` risk.
- **Education officers** carry `b2g_check_required = yes`: check with the B2G owner before any contact.
- **Sanitise captures.** Never keep CMS editor names or emails, officials' photos or biographies, or the text of news stories.
- **The company master is read-only** here, used only for campus coordinates and its `office:government` records. Verification fails if the master database or workbook changes during a run.
- **Drafts only.** `run_pipeline.py` writes one Kiswahili letter per office with an English meaning (`scripts/messaging/draft_run_messages.py`): the family offer for parents only, never a benefit for officials. Nothing is sent or scheduled; keep automations disabled.

## Rate limits

Read `../silverleaf-create-lead-list/references/research-rate-limits.md` first. The limits are enforced in code (`gov_lib.py` registers them with `polite_request`):

| Source | Limit |
|---|---|
| Council and regional sites (GWF CORE API) | One request at a time, 1.5 s apart, retries with backoff, on-disk cache |
| NBS census report | One download (13 MB), cached |
| Wikipedia API | One request every 2 s (HTTP 429 at 1 per second) |
| Overpass | One query at a time, at least 5 s apart, mirror fallback; back-to-back queries can return 429 or 504 |

This track needs **no web search**: every source is an official API, document or open map. When a limit is reached, keep what was confirmed, record the gap in `readme_notes`, and report it. Never work around a cap or a block.

## Workflow

Run these commands from the repository root.

1. **Configure the run.** Copy `references/run-config.example.json` to `data/runs/<run-id>/run-config.json`. Set the date, bounding box, catchment radius, census report and councils, council hosts and OpenStreetMap district names, regions, Wikipedia categories and campus clusters. Mark the pilot councils `core`.
2. **Collect.** Each collector reuses existing files for the date unless you pass `--refresh`.
   ```bash
   python scripts/government/collect_census_wards.py --run-id <run-id>
   python scripts/government/collect_ward_locations.py --run-id <run-id>
   python scripts/government/collect_osm_government.py --run-id <run-id>
   python scripts/government/collect_council_sites.py --run-id <run-id>
   ```
   The census collector fails unless every council's ward rows add up to its printed total.
3. **Transcribe scanned rosters.** A councillor list published only as a scanned PDF (the collector marks it `scanned_needs_transcription`) is transcribed by reading its page images, into `data/raw/government-research/transcriptions/`, with the document URL, SHA-256, page and row for every value. Copy values exactly, note any hard-to-read character, and leave out rows that are not ward conveners. See the `README.md` there.
4. **Curate.** Record reviewed decisions in `data/runs/<run-id>/links.json`: ward spellings (`ward_aliases`), ward reference points (`ward_locations`) and OpenStreetMap office links (`osm_office_links`). See `references/government-data-contract.md`.
5. **Build and verify** without any network calls:
   ```bash
   python scripts/government/run_pipeline.py --run-id <run-id> [--rebuild-db]
   ```
   The pipeline records a master baseline, builds the run, exports the intake, validates it and initialises the run database with the create skill's scripts, adds the government tables, drafts the letters, builds the workbook and runs 30 verification checks.
6. **Review.** Work through the Review Queue (unlocated wards, conflicting points, roster spellings, estimated village wards, master corrections), record decisions in `links.json`, add run-specific findings to `readme_notes`, and re-run step 5. Spot-check the facts behind the GA01 councils against their captures.
7. **Report.** Give counts by level, track and risk; the top wards per campus cluster; named posts and their sources; the verification result; coverage gaps; and corrections to the company master. Do not apply master corrections here: they go through `silverleaf-update-lead-list`.

## Tracks and scores

- **GA01 Protocol introduction:** a core council whose office is published on its official website. The next step is the Kiswahili letter in the plan (§5.6), by hand, then a call after 5 working days and a courtesy visit.
- **GA00 Hold:** every other office. Wards and villages are reached through the council introduction first; district and regional offices are not a v1 target.
- **GA02 Convening request** needs a recorded introduction and a post verified within 90 days, so a research run assigns none.
- **Ward score** (0–100): population relative to the other catchment wards (30), transport band (25), access readiness (20), convening opportunity (15) and observed yield (10). The last three stay zero until introductions, confirmed meetings and events are recorded.

## Reuse and refresh

- **Rebuilding.** `run_pipeline.py --rebuild-db` regenerates the database and workbook from the committed files. Nothing needs refetching.
- **Refreshing.** Create a new run ID with a new date and re-run the collectors. Council leadership and rosters change after elections and transfers, so re-capture council sites at least every 90 days before any convening request. The census stays valid until the next census.
- **New councils.** Add the council, its host, OpenStreetMap district and Wikipedia district names to the config; `collect_census_wards.py` needs its exact table name from the report.
- **Merging into the master** waits for Phase 0 and migration 0003 in the plan (`lead_track`, GA tracks, VM14–VM18, the four government tables).

## References

- `references/government-data-contract.md`: extra columns, office levels and posts, risk rubric, location rules, scoring, `links.json` and the side tables.
- `references/pitfalls.md`: traps found in the first run, and how the scripts now handle them.
- `references/run-config.example.json`: the first run's configuration.
- `../silverleaf-create-lead-list/references/research-rate-limits.md`: rate limits for all research.
