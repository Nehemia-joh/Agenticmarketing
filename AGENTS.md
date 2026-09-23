# Agent instructions

## Source of truth

Use `outputs/master/Silverleaf Master Database.sqlite` as the canonical lead database. Treat the consolidated workbook as generated output. Preserve stable entity IDs, source records, evidence links, message versions, and review items.

## Select the right skill

- For a separate new database, follow `skills/silverleaf-create-lead-list/SKILL.md`.
- For additions or refreshes to this master, follow `skills/silverleaf-update-lead-list/SKILL.md`.
- For partnership positioning, hooks, messages, or sequences, follow `skills/silverleaf-outreach/SKILL.md`.
- For welfare institutions as paying customers (children's homes, care programmes, specialised centres, and their funders), follow `skills/silverleaf-welfare-leads/SKILL.md`. Its runs live in `data/runs/<run-id>/` and `outputs/runs/<run-id>/` and never modify the master.
- For local government offices that can convene community meetings (barazas) where Silverleaf can meet parents, follow `skills/silverleaf-government-leads/SKILL.md`. Its runs are separate in the same way. They record officials only as officially published and never hold parent, resident or party data.

- For contact profiles and contact leads across the three databases (published organisation routes and the named decision-makers an organisation publishes), follow `docs/methodology/contact-research.md` and the scripts in `scripts/contacts/`. The master takes the results through the update skill's validator, preflight and one transaction; the welfare and government runs take them through their pipelines.

Read the referenced data contract before creating fields or changing match rules.

Any message that states an offer, discount or fee term takes it from `data/reference/silverleaf-offer-register.json` (`skills/silverleaf-outreach/references/offer-register.md`). Draft with the scripts in `scripts/messaging/`; they check every term against the register. The first message to an organisation is a request that states no offer terms; the offer follows in the next message. Mariam Haji, Marketing and Partnership Coordinator, is the sender. Sponsorship is asked of welfare funders only.

Before writing any script, check `scripts/README.md`: reusable scripts are catalogued there by task. Extend an existing script rather than writing a one-off. New reusable scripts go under `scripts/<task>/` and into the catalogue. `runtime/` holds only generated working files.

## Lead-research rules

- Capture public business routes and publicly attributable enquiries. Do not infer private contact details, parenthood, household facts, or current employment.
- Preserve URL, source locator, publication date when available, acquisition date, verification date, evidence basis, and evidence excerpt.
- Match exact identifiers first. Send similar-name cases to review instead of merging them automatically.
- Keep a factual hook only when its exact claim has a source URL and verification date. A plain role- or need-based opening is valid when no accurate hook exists.
- Keep automation and campaign sending disabled. Repository workflows produce drafts and review artifacts only.
- Respect research rate limits: `skills/silverleaf-create-lead-list/references/research-rate-limits.md`.
  - The WebSearch cap is per session and shared by every subagent.
  - Run deterministic collectors first, and give each research agent an explicit search allocation.
  - Launch at most four agents at a time.
  - Pace fetches, and never work around a cap, block or login wall.

## Change sequence

1. Validate intake data.
2. Run the read-only update preflight when an existing database is involved.
3. Apply database mutations in one transaction and rollback on failed checks.
4. Export workbook data and rebuild the workbook.
5. Run `python scripts/master/verify_master.py`.
6. Report before and after counts, matches, inserts, conflicts, evidence gaps, and output paths.

Do not add committed `node_modules`, virtual environments, caches, preview images, inspection dumps, database journals, or permanent backup snapshots.
