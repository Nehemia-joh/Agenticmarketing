---
name: silverleaf-keep-outputs-current
description: Keep every Silverleaf output current after a change, in the right order. Use after any change to the offer register, message copy, a lead or intake, a geocode or correction, a contact merge, a recipient or band or segment rule, a run's links.json, the campus points, the research ledger, docs that have a copy, the strategy deck or the pipelines page. It gives what to re-run, what to check, what is committed, how to work from a worktree, and the pre-commit checklist.
---

# Keep the Silverleaf outputs current

Every output is generated from the three databases and the committed inputs. When an input changes, everything downstream of it is stale until it is rebuilt in order. This skill says what to rebuild for each kind of change, and how to prove it is done.

- The dependencies come from each script's actual reads and writes: [references/script-io.md](references/script-io.md).
- The full change-by-change map: [references/dependency-map.md](references/dependency-map.md).
- The pipeline stages these outputs come from: `skills/silverleaf-lead-pipeline/SKILL.md`.
- Known gaps between the scripts and the docs: `skills/silverleaf-lead-pipeline/references/known-gaps.md`.

Run every command from the repository root. Run Python with `PYTHONDONTWRITEBYTECODE=1` (or `python -B`): `verify_master.py` fails on any `__pycache__` folder in the tree.

## The full rebuild order

Use this order whenever a change reaches the master or more than one list. Each step reads what the steps before it wrote.

```powershell
python scripts/master/assign_message_variants.py --apply      # 1  variants; it re-runs resolve_master_recipients.py --apply itself
python scripts/messaging/draft_master_messages.py             # 2  drafts (refuses to write on any conformance issue)
python scripts/master/refresh_acquisition_metadata.py         # 3  tracks
python scripts/master/export_master_workbook_data.py          # 4  workbook input (runtime/artifacts/workbook-input.json)
npm run build:workbook                                        # 5  exports again, then builds the master workbook
python scripts/master/verify_master.py                        # 6  master checks
python scripts/welfare/run_pipeline.py --run-id arusha-welfare-2026-09 --rebuild-db        # 7
python scripts/government/run_pipeline.py --run-id arusha-government-2026-09 --rebuild-db  # 8
python scripts/maps/build_lead_map.py                         # 9  lead map (fails on a count mismatch or contact data)
python scripts/messaging/export_resend_contacts.py            # 10 segments: CSVs in runtime/, summaries in outputs/messages/
git checkout -- data/raw/welfare-research/MANIFEST.md         # revert hash churn (see below)
```

**Before step 1, when locations or ranks changed.** After a geocode, a campus move or a correction, run these first:

```powershell
python scripts/master/recompute_campus_distances.py --apply
python scripts/master/rank_employer_reach.py --apply
```

The reach rank reads the chosen plans, and the drafter reads the reach tier. So when a change alters which plans are chosen (new leads, a contact merge, a recipient rule), run the rank again after step 1. Then repeat steps 2 to 6. Both scripts are idempotent.

**Why the runs come after the master.** Each run records the master's SHA-256 as its baseline (`runtime/<track>/<run>/master-baseline.json`). It fails `company_master_db_unchanged` if the master changes during the run. It also reads the master's `campuses`, IDs and `office:government` records. Rebuild the runs only once the master is final.

**The manifest.** `export_welfare_run.py` rewrites `data/raw/welfare-research/MANIFEST.md` with each raw file's hash as checked out. With `core.autocrlf=true`, unchanged files hash differently.
- If no file under `data/raw/welfare-research/` changed, revert the manifest.
- If a research file was added or edited, keep the manifest and commit it with the file.
- Check `data/raw/government-research/MANIFEST.md` the same way; it is written by the same kind of code.

**Review files.** Rebuild these when the drafts they show changed:

| Output | Command | When |
|---|---|---|
| `outputs/messages/Silverleaf Offer-Aligned Messages - <date>.xlsx`, `offer-messages-summary.json` | `python scripts/messaging/build_offer_messages_workbook.py --date <date>` | Any draft changed. It re-checks every draft and exits 1 on a failure |
| `outputs/messages/Silverleaf Welfare Drafts - <date>.md` | `python scripts/messaging/consolidate_welfare_drafts.py --run-id arusha-welfare-2026-09` | Welfare drafts changed |
| `outputs/messages/Silverleaf Government Drafts - <date>.md` | `python scripts/messaging/consolidate_government_drafts.py --run-id arusha-government-2026-09` | Letters changed |
| `outputs/messages/Silverleaf Employer Sponsorship Drafts - <date>.md` | `python scripts/messaging/draft_employer_sponsorship.py` | Variants or sponsorship reasons changed |
| `outputs/messages/Silverleaf Company Audience Profile - <date>.md` | `python scripts/messaging/build_company_audience_profile.py` | Recipients, kinds or tiers changed |
| `outputs/contacts/Silverleaf Contact Profiles - <date>.xlsx` | `python scripts/contacts/build_contact_workbook.py --date <date>` | After a contact merge (`--baseline` before it) |

## What to re-run, by kind of change

Short form. The full table, with the evidence for each dependency and the checks, is in [references/dependency-map.md](references/dependency-map.md).

| Change | Start with | Then |
|---|---|---|
| Offer register or offer wording (`silverleaf-offer-register.json`, `offer_lib.py`) | Edit both `offer-register.md` copies with the JSON | Steps 2 to 10; offers workbook; pipelines page if section 6 changed |
| Message copy or `first_touch.py` | Steps 2 to 10 (step 1 too if the sponsorship copy changed) | Offers workbook; welfare and government review files |
| New master lead or intake | Validator, preflight, the `add_*.py --apply` script, its geocodes | Recompute and rank, steps 1 to 10, rank again |
| Geocode or location correction | Ledger ingest; `apply_geocodes.py` (preview, then `--apply`) | Recompute and rank, steps 1 to 10 |
| Employer correction, field repair or relations | The `apply_*.py --apply` script | Rank, steps 1 to 10 |
| Contact merge | Profiles, people screen, merge preflight, `--apply`, `update_master_contacts.py --apply`; `export_run_contact_research.py` | Steps 1 to 10, rank again; contact workbook |
| Hook research | `apply_hook_research.py --apply` | Rank (headcount), steps 2 to 10 |
| Recipient rule or override | `apply_organisation_relations.py --apply` if relations changed | Steps 1 to 10, rank again; audience profile |
| Band or segment rule | The script that holds the rule | Recompute and rank, steps 1 to 10; Catchment Criteria and Core Segments docs |
| Welfare `links.json` | `apply_research_reviews.py --apply` if from agents | Steps 7, 9, 10; welfare review file |
| Government `links.json` | — | Steps 8, 9, 10; government review file |
| Campus points | The `campuses` table | Recompute (with `--report`) and rank, steps 1 to 10; Catchment Criteria doc |
| Ledger or playbook | `ledger.py ingest`, then `ledger.py check` | Nothing downstream rebuilds; planners read it next time |
| Docs or skill copies | Copy so the pair matches; `check_doc_pairs.py` | Steps 7 and 8 if a run script copy changed (sync check) |
| Strategy deck | Recount from read-only copies | Sources and slide-map files |
| Pipelines page | `render_markdown_page.py` | Mirror any decision into the docs that state it |

## What is committed

| Committed | Never committed |
|---|---|
| Workbooks: master, both runs, offer-aligned messages, contact profiles, call sheets | SQLite databases (`outputs/**/*.sqlite`, journals, `-wal`, `-shm`) |
| `outputs/maps/Silverleaf Lead Map.html`, `outputs/strategy/*.html`, `outputs/presentations/*` | `runtime/`: Resend CSVs, `profiles.json`, HTTP caches, `workbook-input.json`, previews, baselines |
| Reports: `outputs/reports/*.json`, `outputs/runs/<r>/intake-validation.json` and `run-verification.json`, `outputs/contacts/*.json`, `outputs/messages/*.json` | Inferred email candidates in any form; anything with a Resend address list |
| Segment and review markdown in `outputs/messages/` | `node_modules/`, `__pycache__/`, `.env`, `outputs/previews/`, `outputs/backups/`, `outputs/exports/` |
| `data/raw/**` (research files, coverage logs, manifests, the ledger), `data/interim/**`, `data/reference/**`, `data/runs/<r>/` (config, `links.json`, `intake.csv`) | `chats/` and `references/` (the user's folders), unless the user says so |

## Worktree discipline

The databases and `runtime/` exist only in the main checkout, `C:\Work\silverleaf-agentic-marketing`.

1. **Copy in.** Record the SHA-256 of each database in the main checkout (`Get-FileHash -Algorithm SHA256`). Copy them to the same paths in the worktree: the master and both run databases. Copy only the `runtime/` files you need, such as `runtime/contacts/profiles.json`.
2. **Read the HTTP cache, never copy it.** Set `CONTACTS_CACHE_FALLBACK` to the main checkout's `runtime/contacts/http-cache`. Pages are read from there and never written there. `collect_geocodes.py sites --crawl-cache <path>` and `analyse_high_direct_pool.py --runtime <path>` take the path directly.
3. **Work and verify in the worktree.** Record the SHA-256 after your last write, and put both hashes in your report.
4. **Hand back.** The orchestrator copies the databases back, after checking that the main checkout's hashes still match the copy-in hashes. If they changed, another session wrote in the meantime: stop and reconcile. The orchestrator then re-runs `verify_master.py` and the run verifications in the main checkout.
5. **Report paths.** Three committed reports record the checkout path:
   - `outputs/reports/master-verification.json` (`database`, `workbook`);
   - `outputs/runs/arusha-welfare-2026-09/intake-validation.json`;
   - `outputs/runs/arusha-government-2026-09/intake-validation.json`.

   Rewrite them to the main checkout's paths, or regenerate them there, before committing. Commits `c00539b` and `fab400d` did this.
6. **Never** junction `node_modules`, switch another checkout's branch, or stash.

## What "verified" means

All of these hold, from the last run of each:

- **The master.** `python scripts/master/verify_master.py` reports `result: passed`, `enabled_automations: 0` and `unwanted_paths: []`, in `outputs/reports/master-verification.json`. Its nine checks:
  - integrity and foreign keys;
  - the workbook exists;
  - every plan has a track;
  - hooks are supported and linked to sources;
  - lead briefs are traceable;
  - automations are disabled;
  - there is no dependency debris.
- **The workbook.** `outputs/reports/workbook-verification.json` shows every sheet's row count matching the export. `npm run build:workbook` exits 1 otherwise.
- **The runs.** `outputs/runs/<r>/run-verification.json` reports `result: passed`: 23 of 23 checks for welfare and 30 of 30 for government. The checks include `skill_script_copies_in_sync`, `company_master_db_unchanged` and offer-register conformance.
- **The drafts.** The master drafter reports `conformance_issues: 0` in `outputs/messages/master-offer-messages-reconciliation.json`. `draft_run_messages.py` raises on any issue. `build_offer_messages_workbook.py` re-runs `offer_lib.check_message` on every message of the three databases and exits 0. To spot-check one message:
  ```powershell
  python -c "import sys; sys.path.insert(0,'scripts/messaging'); import offer_lib as L; print(L.check_message(open('msg.txt',encoding='utf-8').read(), ['OF04']))"
  ```
  An empty list means the message conforms.
- **The map.** `build_lead_map.py` exits 0. Its counts match the databases and the exporter, and no contact name, address or number is on the page.
- **The ledger.** `python scripts/research/ledger.py check` reports 0 duplicates and no contact detail in `found`.
- **High-direct waves only.** `python scripts/contacts/analyse_high_direct_pool.py --check` passes, and `--compare before.json after.json` shows no high-direct row lost.

## Commit and push

- Commit finished, verified work and push it to `main`, workbooks and reports included. A worker in a worktree commits to its own branch only; the orchestrator merges and pushes.
- Stage everything except the user's folders:
  ```powershell
  git add -A -- . ':!chats' ':!references'
  ```
- Never commit a database, `runtime/`, or an inferred email candidate. `.gitignore` covers the first two; check the third yourself.
- Before pushing, run `git fetch` and rebase onto `origin/main`. On a conflict in a generated file, regenerate it rather than hand-merge it.
- End the commit message with the attribution line the session gives.

## Pre-commit checklist

- [ ] Every step downstream of the change has run, in order (the dependency map above).
- [ ] `verify_master.py`: passed, `enabled_automations` 0, `unwanted_paths` empty.
- [ ] Both `run-verification.json` files are passed and newer than the last master write.
- [ ] Drafter `conformance_issues` 0; the offers workbook builds (when drafts changed).
- [ ] `build_lead_map.py` passed; the Resend summary counts are as expected, and any change is explained.
- [ ] `ledger.py check`: 0 duplicates; every new research file, Maps round and browser pass is ingested.
- [ ] Copies match: `python scripts/docs/check_doc_pairs.py` exits 0 (the five `docs/strategy/` documents and their `skills/silverleaf-outreach/references/` copies, and every welfare and government script and its skill copy).
- [ ] The welfare and government `MANIFEST.md` were reverted unless a raw file in that folder changed.
- [ ] Report paths point to the main checkout.
- [ ] `git status` shows no `.sqlite`, `runtime/`, `chats/`, `references/`, `__pycache__` or inferred addresses staged.
- [ ] `scripts/README.md`, the owning skill and any affected doc are updated for a new or changed script.
- [ ] The commit message says what changed, the before and after counts, and that verification passed.
