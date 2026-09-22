---
name: silverleaf-welfare-leads
description: Research and build an evidence-backed list of welfare institutions (children's homes, family-based care programmes, specialised centres and their funders) near Silverleaf's campuses as paying institutional customers, in a separate run database and review workbook. Use for a new welfare-lead run, a refresh of an existing one, or reusing its register, map and research files. Keeps the company-leads master untouched.
---

# Silverleaf welfare leads

Build a welfare-lead run with the scripts in `scripts/welfare/`, the repository's home for reusable scripts (see `scripts/README.md`). This skill bundles an identical copy in its own `scripts/` folder, so it works when installed on its own. Edit `scripts/welfare/` first and copy it across; verification fails if the two differ. A welfare lead is an institution that pays school fees for the children in its care or programme, so it is treated as an account, not as a message recipient. The method and the business case are in `plans/b2b-welfare-leads-plan.md`. The first run, `arusha-welfare-2026-09`, is the worked example to reuse and extend.

## Outputs

Everything stays separate from `outputs/master/`.

| Path | Contents |
|---|---|
| `data/runs/<run-id>/` | `run-config.json`, `links.json` (reviewed curation), `research-plan.json`, `intake.csv` |
| `data/raw/welfare-research/` | Research JSONL files, coverage logs, NGO register and OpenStreetMap extracts, `MANIFEST.md` with hashes |
| `data/interim/welfare-leads/` | Organisation, contact, relationship and register tables (TSV) |
| `outputs/runs/<run-id>/` | `lead-database.sqlite` (ignored by Git), the review workbook, `intake-validation.json`, `run-verification.json` |
| `runtime/welfare/<run-id>/` | Scratch space (ignored by Git): rendered prompts, `consolidated.json`, `final.json`, HTTP cache, master baseline |

## Rules

- Never collect a child's name, photo, story or health information, or an age tied to an identity. Never collect anything about the parents or relatives of children in care.
- Record only what each source publishes for contact purposes. Do not search a person's name across sites.
- Put `pdpa_risk` (`low`, `medium` or `risky`) and `pdpa_risk_reason` on every organisation, contact and enquiry. Parent and guardian enquiries are always `risky`. Read the rubric in `references/welfare-data-contract.md`.
- Merge only on exact identifiers (see the data contract). Similar names, a funder and a home sharing a website, and conflicting facts go to the review queue.
- Open the company master read-only, and only for campus coordinates and existing IDs. Verification fails if the master database or workbook changes during a run.
- Outreach exists only as drafts: `run_pipeline.py` writes one offer-aligned draft per in-scope organisation (`scripts/messaging/draft_run_messages.py`, terms from the offer register), and nothing is sent or scheduled. Keep automations disabled.

## Rate limits and research budget

Read `../silverleaf-create-lead-list/references/research-rate-limits.md` before starting.

- **Web search is capped per session and shared by every subagent** (200 in the 2026-09 run). Always plan budgets with `scripts/welfare/plan_research.py`.
- **Deterministic collectors come first.** They use no search budget.
- **Launch at most four research agents per wave.**
- **The network limits are enforced in code** in `scripts/welfare/welfare_lib.py`:
  - the NGO register: at most 4 workers, 0.3 seconds apart
  - Overpass: one query at a time, 5 seconds apart, with mirror fallback
  - retries with exponential backoff that honour `Retry-After`
  - an on-disk cache
- **When a limit is reached:** keep what was confirmed, record the gap in the coverage log, and report it. Never work around a cap or a block.

## Workflow

Run these commands from the repository root.

1. **Configure the run.** Copy `references/run-config.example.json` to `data/runs/<run-id>/run-config.json`. Set the date, radius, bounding box, research-file globs, scope and Read Me notes.
2. **Collect the deterministic sources.** Both are rate-limited and resumable, and cached files are reused unless you pass `--refresh`.
   ```bash
   python scripts/welfare/fetch_ngo_register.py --run-id <run-id>
   python scripts/welfare/collect_osm_welfare.py --run-id <run-id>
   ```
3. **Plan the research.**
   ```bash
   python scripts/welfare/plan_research.py --run-id <run-id> --search-budget 200 --already-used <n>
   ```
   This writes one prompt per slice to `runtime/welfare/<run-id>/prompts/`, and `research-plan.json` with each slice's allocation and wave. Put the previous run's `next_run_priorities` (in `references/research-slices.json`) first.
4. **Run the research agents,** at most four per wave, each with its prompt. They write `research_<slice>_<name>_<date>.jsonl` and a coverage log into `data/raw/welfare-research/`.
5. **Curate.** Record reviewed decisions in `data/runs/<run-id>/links.json`: register matches with evidence, location overrides for multi-site organisations, map links and company-master IDs.
6. **Build and verify** without any network calls:
   ```bash
   python scripts/welfare/run_pipeline.py --run-id <run-id> [--rebuild-db]
   ```
   The pipeline runs these steps in order:
   1. records a master baseline
   2. classifies the register
   3. consolidates the research
   4. builds the run
   5. exports the intake
   6. validates it with the create skill's validator
   7. initialises the run database with the create skill's initializer
   8. adds the side tables
   9. drafts the offer-aligned messages
   10. builds the workbook
   11. runs the 23 verification checks
7. **Review.** Work through the workbook's Review Queue, and fetch the pages behind at least five top leads to confirm their routes. Add run-specific findings to `readme_notes` and re-run step 6.
8. **Report.** Give counts by segment, track and risk; the strongest leads; the verification result; coverage gaps; and corrections to the company master. Do not apply master corrections here: they go through `silverleaf-update-lead-list`.

## Reuse and refresh

- **Rebuilding.** Re-running `run_pipeline.py --rebuild-db` regenerates the database and workbook from the committed files. Nothing needs refetching.
- **Refreshing.** Create a new run ID with a new date, re-run only the stale collectors, and plan research with `--only` for the slices that need it. Carry `links.json` forward and re-check each decision.
- **Merging into the master.** This waits for Phase 0 of the welfare plan (`lead_track`, value-module registry, track-aware refresh). Without it, the master's acquisition refresh would reassign welfare rows the employer modules.

## References

- `references/research-brief.md`: the brief every research agent reads (template).
- `references/research-slices.json`: slice definitions, weights and next-run priorities.
- `references/welfare-data-contract.md`: record schema, extra columns, risk rubric, identity, scoring and `links.json`.
- `references/pitfalls.md`: traps found in the first run, and how the scripts now handle them.
- `../silverleaf-create-lead-list/references/research-rate-limits.md`: rate limits and budgets for all research.
