# Agent instructions

## Source of truth

Use `outputs/master/Silverleaf Master Database.sqlite` as the canonical lead database. Treat the consolidated workbook as generated output. Preserve stable entity IDs, source records, evidence links, message versions, and review items.

## Select the right skill

- For a separate new database, follow `skills/silverleaf-create-lead-list/SKILL.md`.
- For additions or refreshes to this master, follow `skills/silverleaf-update-lead-list/SKILL.md`.
- For partnership positioning, hooks, messages, or sequences, follow `skills/silverleaf-outreach/SKILL.md`.

Read the referenced data contract before creating fields or changing match rules.

## Lead-research rules

- Capture public business routes and publicly attributable enquiries. Do not infer private contact details, parenthood, household facts, or current employment.
- Preserve URL, source locator, publication date when available, acquisition date, verification date, evidence basis, and evidence excerpt.
- Match exact identifiers first. Send similar-name cases to review instead of merging them automatically.
- Keep a factual hook only when its exact claim has a source URL and verification date. A plain role- or need-based opening is valid when no accurate hook exists.
- Keep automation and campaign sending disabled. Repository workflows produce drafts and review artifacts only.

## Change sequence

1. Validate intake data.
2. Run the read-only update preflight when an existing database is involved.
3. Apply database mutations in one transaction and rollback on failed checks.
4. Export workbook data and rebuild the workbook.
5. Run `python scripts/master/verify_master.py`.
6. Report before and after counts, matches, inserts, conflicts, evidence gaps, and output paths.

Do not add committed `node_modules`, virtual environments, caches, preview images, inspection dumps, database journals, or permanent backup snapshots.
