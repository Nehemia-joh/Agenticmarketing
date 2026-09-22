# Reusable scripts

Check this catalogue before writing a new script. Reusable scripts live under `scripts/<task>/`. Generated working files (caches, rendered prompts, intermediate JSON) go in `runtime/`, which Git ignores. When a session starts a task, look here first. If a script covers the task, run it or extend it here instead of writing a one-off in `runtime/`.

Run every command from the repository root. Anything that calls the network follows `skills/silverleaf-create-lead-list/references/research-rate-limits.md`, and the welfare scripts enforce those limits in code.

## Catalogue

| Task | Script | What it does | Network and rate limits |
|---|---|---|---|
| Company leads: collect | `scripts/collection/collect_partner_leads.js` | Browser-console collector for the TATO directory and OpenStreetMap employers | Runs in a browser tab on tatotz.org; re-run quarterly |
| Company leads: collect | `scripts/collection/build_partner_leads.py` | Builds the partner-lead universe (geocoding, campus distances) from raw pulls | None |
| Company master | `scripts/master/refresh_acquisition_metadata.py` | Assigns AQ acquisition tracks and value modules to outreach plans | None. Corporate rules only (see welfare plan Phase 0) |
| Company master | `scripts/master/export_master_workbook_data.py` | Exports workbook input from the master database | None |
| Company master | `scripts/master/build_master_workbook.mjs` | Rebuilds the master review workbook (`npm run build:workbook`) | None |
| Company master | `scripts/master/verify_master.py` | Checks master integrity, workbook, hooks and disabled automations | None |
| Welfare leads: collect | `scripts/welfare/fetch_ngo_register.py` | NGOs Information System map and profiles within the catchment | Up to 4 workers, 0.3 s apart, retries with backoff, resumable cache |
| Welfare leads: collect | `scripts/welfare/collect_osm_welfare.py` | OpenStreetMap welfare features | One query at a time, 5 s apart, mirror fallback |
| Welfare leads: plan | `scripts/welfare/plan_research.py` | Splits the web-search budget into per-agent prompts and waves | None; writes each agent's search allocation into its prompt |
| Welfare leads: build | `scripts/welfare/run_pipeline.py` | Runs every step below in order and stops at the first failure | None |
| Welfare leads: build | `scripts/welfare/classify_ngo_register.py` | Rates each register entry's child-welfare relevance | None |
| Welfare leads: build | `scripts/welfare/consolidate_research.py` | Merges research records, raises review items and geocodes | None |
| Welfare leads: build | `scripts/welfare/build_welfare_run.py` | Links register, map and master data, then scores and proposes tracks | None |
| Welfare leads: build | `scripts/welfare/export_welfare_run.py` | Writes the intake CSV, interim tables and the raw-evidence manifest | None |
| Welfare leads: build | `scripts/welfare/augment_run_db.py` | Adds relationships, register, coverage, reviews and evidence files to the run database | None |
| Welfare leads: build | `scripts/welfare/build_welfare_workbook.py` | Builds the review workbook from the run database only | None |
| Welfare leads: build | `scripts/welfare/verify_welfare_run.py` | Runs 19 checks, including that the company master is untouched and the skill's script copy matches | None |
| Shared library | `scripts/welfare/welfare_lib.py` | Normalisation, geography, run config and `polite_request` | Per-host limits in `HOST_LIMITS`; reuse `polite_request` for any new collector |
| Any list: intake | `skills/silverleaf-create-lead-list/scripts/validate_intake.py` | Validates an intake CSV against the shared contract | None; bundled with its skill |
| Any list: new database | `skills/silverleaf-create-lead-list/scripts/initialize_lead_db.py` | Creates a separate run database from a validated intake | None; bundled with its skill |
| Company master: update | `skills/silverleaf-update-lead-list/scripts/preflight_update.py` | Read-only exact-match preflight against the master | None; bundled with its skill |

## Adding a script

1. **Put it with its task.** Place it under `scripts/<task>/` (for example `scripts/government/`). Keep it deterministic where possible, and read settings from a run config rather than hard-coding them.
2. **Route network calls through `polite_request`.** Use the one in `scripts/welfare/welfare_lib.py`, or add the host's limits to `HOST_LIMITS` and to the rate-limits reference together.
3. **Keep outputs in their homes:**
   - raw evidence in `data/raw/<source>/`
   - run inputs in `data/runs/<run-id>/`
   - run outputs in `outputs/runs/<run-id>/`
   - scratch in `runtime/`
4. **Document it:** add a row to this catalogue and describe it in the skill that uses it.

## Copies bundled with skills

The welfare skill carries an identical copy of `scripts/welfare/` in `skills/silverleaf-welfare-leads/scripts/`, so the skill still works when it is installed on its own. `welfare_lib.py` finds the repository root by walking up to `AGENTS.md`, so the same file runs from either folder.

Edit `scripts/welfare/` first, then refresh the copy:

```bash
cp scripts/welfare/*.py skills/silverleaf-welfare-leads/scripts/
```

```powershell
Copy-Item scripts/welfare/*.py skills/silverleaf-welfare-leads/scripts/
```

`verify_welfare_run.py` fails its `skill_script_copies_in_sync` check if the two folders differ.
