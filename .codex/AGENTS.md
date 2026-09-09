# Codex repository instructions

Read `../AGENTS.md` first. It defines the source of truth, evidence rules, matching policy, and required verification sequence for this repository.

## Repository boundary

Work only in `C:\Work\silverleaf-agentic-marketing` unless the user names another location. The sibling folder `C:\Work\silverleaf-agentic-marketing.__pre_reorg` is an inactive archive. Do not search, edit, execute, or consolidate from that archive unless the user explicitly requests historical recovery.

## Select the workflow

- To add to the canonical master, read `../skills/silverleaf-update-lead-list/SKILL.md` and its referenced shared data contract.
- To create an independent list, read `../skills/silverleaf-create-lead-list/SKILL.md`.
- To revise positioning, hooks, outreach messages, or sequences, read `../skills/silverleaf-outreach/SKILL.md`.

The canonical master is `../outputs/master/Silverleaf Master Database.sqlite`. Its workbook is generated and must not become an independent source of truth.

## Update requirements

1. Put new rows in the shared intake format.
2. Run the intake validator.
3. Run the read-only update preflight.
4. Inspect matches, inserts, missing organisations, and review items.
5. Merge in one SQLite transaction while preserving stable IDs and provenance.
6. Regenerate the workbook and run `python scripts/master/verify_master.py`.

Report before and after counts, exact matches, inserted records, quarantined rows, conflicts, evidence gaps, and output paths.

## Research and outreach controls

- Collect public business contact routes and deliberately published enquiry details only.
- Never infer private contact details, parenthood, household circumstances, or present employment.
- Preserve each URL, source locator, source date, acquisition date, verification date, evidence basis, and evidence excerpt.
- Leave a hook blank unless its exact claim is supported by a source URL and verification date.
- Treat similar names as review candidates rather than automatic matches.
- Draft outreach only. Do not send messages, create live schedules, or enable automation.

Do not add `node_modules`, virtual environments, caches, previews, inspection dumps, database journals, credentials, or backup snapshots to the repository.
