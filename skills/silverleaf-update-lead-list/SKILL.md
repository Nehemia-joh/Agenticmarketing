---
name: silverleaf-update-lead-list
description: Safely add researched organisations, contacts, enquiries, evidence, and outreach plans to an existing Silverleaf lead database while preserving IDs, provenance, and prior records. Use when refreshing or expanding an established master list; use silverleaf-create-lead-list for a separate new list.
---

# Update a Silverleaf Lead List

Update the canonical SQLite database in place and regenerate its review workbook. Preserve existing entities, evidence, message history, and stable IDs.

## Establish the update

Identify the canonical database, generated workbook, update objective, source set, geographic scope, lead types, and verification cutoff. Read the shared [lead-list data contract](../silverleaf-create-lead-list/references/lead-list-data-contract.md) and [workbook layout](../silverleaf-create-lead-list/references/workbook-layout.md), then read [references/merge-and-reconciliation.md](references/merge-and-reconciliation.md).

Do not use workbook rows as the authoritative merge input when SQLite is available. Do not replace the database with a new list just because the update is large.

When the update needs new research, follow [research-rate-limits.md](../silverleaf-create-lead-list/references/research-rate-limits.md):
- Reuse cached raw evidence before refetching.
- Budget web searches across agents, since the session cap is shared.
- Record anything not reached in a coverage log.

Welfare-run records wait for Phase 0 of `plans/b2b-welfare-leads-plan.md` before they merge into this master. Without it, `refresh_acquisition_metadata.py` would reassign them the employer value modules.

## Preflight before mutation

1. Put new research in the shared intake format.
2. Run the create skill's validator.
3. Run `python scripts/preflight_update.py <database.sqlite> <intake.csv> --report <preflight.json>`.
4. Inspect proposed inserts, exact matches, missing organisations, source reuse, and review items.
5. Resolve validation errors before writing.

The preflight script is read-only. Treat fuzzy name similarity as a review signal, never as permission to merge.

## Apply the update

Make all database changes in one transaction:

1. Register each new source and source record.
2. Reuse exact entity matches and their stable IDs.
3. Insert new organisations before dependent contacts, enquiries, and outreach plans.
4. Add `entity_sources` links and field-level facts.
5. Preserve old values when the new claim is weaker, older, or ambiguous.
6. Add conflicts to `review` with both values and the required decision.
7. Assign or refresh acquisition states and message modules.
8. Commit only after integrity, foreign-key, and reconciliation checks pass.

Keep message revisions as new versions or explicit version columns. Do not erase earlier approved copy. A personalised hook must cite verified evidence; otherwise leave the hook blank and use a role- or need-based opening.

## Reconcile the result

Use the conservation checks in [references/merge-and-reconciliation.md](references/merge-and-reconciliation.md). At minimum, prove:

- Previous entity IDs still exist.
- Insert counts equal validated new records minus exact matches and quarantined rows.
- Each accepted row has a source record and entity link.
- Every outreach plan points to a valid target.
- Review-required rows remain excluded from send-ready views.
- Automations remain disabled.

Do not keep permanent timestamped database or workbook backups inside the repository. Use a temporary copy during the transaction when needed, verify the committed database, then remove the temporary copy.

## Regenerate the workbook

Export fresh workbook data from SQLite and rebuild the workbook using the repository's deterministic scripts. Follow the shared workbook layout and visually inspect the result. Never hand-edit generated lead, evidence, or campaign sheets as a substitute for updating SQLite.

Report the before and after counts, new and matched records, conflicts, verification failures, output paths, and the commands used. Draft messages only. Do not send, schedule, or activate outreach.
