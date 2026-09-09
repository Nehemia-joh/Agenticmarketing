# Repository reorganisation manifest

Reorganised on 9 September 2026.

## Canonical records retained

- `outputs/master/Silverleaf Master Database.sqlite`: canonical source, entity, message, strategy, campaign, evidence, and automation data.
- `outputs/master/Silverleaf Master Database - Consolidated.xlsx`: generated review workbook rebuilt from the canonical database.
- `references/Marketing Documents/`: all 12 marketing originals.
- Other original business references: the process map, BPR workbook, CEO recording, context dossier, and marketing observations.
- Raw lead-research responses, structured partner-lead TSVs, gazetteer, collection logic, and lead-building logic.
- Current positioning, acquisition, hook, flow, and marketing-extraction guidance.
- The existing outreach skill plus the new create-list and update-list skills.

## Redundancy removed

- Two `node_modules` trees. Dependencies are declared in `package.json` and excluded by `.gitignore`.
- Generated `.inspect.ndjson` dumps and PNG previews.
- Timestamped or stage-specific SQLite and workbook backups.
- Prototype, intermediate, hook-stage, and partnership-stage workbook copies.
- Generated extraction, export, and queue JSON files that the canonical database already represents.
- Superseded one-off migration, preview, consolidation, and workbook scripts.
- Generated `.docx` and `.pdf` copies where an equivalent Markdown source remains.
- Python caches and document-generation helpers tied to the former layout.

The SQLite `source_files` table preserves hashes and archived bytes for imported historical sources, including many removed intermediate artifacts. Its stored paths describe where a source was captured and may refer to the former layout.

## Replacement workflow

The retained deterministic workflow consists of:

1. `scripts/master/refresh_acquisition_metadata.py`
2. `scripts/master/export_master_workbook_data.py`
3. `scripts/master/build_master_workbook.mjs`
4. `scripts/master/verify_master.py`

The skill scripts validate a new intake, initialise a separate database, and preflight additions to an existing database. No retained script sends outreach or enables automation.
