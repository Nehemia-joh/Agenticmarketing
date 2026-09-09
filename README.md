# Silverleaf agentic marketing intelligence

This repository holds Silverleaf's sourced lead intelligence, partnership strategy, outreach drafts, and disabled automation designs. The canonical operational dataset is the local file `outputs/master/Silverleaf Master Database.sqlite`. Git intentionally ignores that mutable database. The consolidated workbook is a generated review view of the database.

## Repository map

| Path | Contents |
|---|---|
| `data/raw/lead-research/` | Captured raw lead-research responses and source text. |
| `data/interim/partner-leads/` | Structured collection outputs awaiting canonical import. |
| `data/reference/` | Supporting lookup data. |
| `data/evidence/` | Current verification records used by qualification or copy. |
| `references/` | Original Silverleaf business and marketing source documents. |
| `docs/scope/` | Agreed project scope. |
| `docs/plans/` | Delivery plan. |
| `docs/methodology/` | Lead-generation and research method. |
| `docs/strategy/` | Positioning, hooks, acquisition tracks, flows, cadence, and marketing-document findings. |
| `scripts/collection/` | Deterministic collection and source-list builders. |
| `scripts/master/` | Acquisition refresh, workbook export/build, and master verification. |
| `skills/` | Reusable create-list, update-list, and outreach skills. |
| `outputs/master/` | Canonical SQLite database and consolidated review workbook. |
| `outputs/config/` | Disabled automation recipes. |
| `outputs/reports/` | Current verification results. |

Historical paths inside `source_files` are provenance captured when sources were imported. They are not instructions to recreate the former folder layout.

The former project tree at `C:\Work\silverleaf-agentic-marketing.__pre_reorg` is an inactive archive. Do not search, edit, merge, or run files from it during normal work. Use it only when the user explicitly requests historical recovery.

## Restore the local master database

The SQLite database is required to update or regenerate the master list, but it is not stored in ordinary Git because each binary revision would add roughly 90 MB to repository history. Keep the working file at:

```text
outputs/master/Silverleaf Master Database.sqlite
```

On this machine, the inactive archive contains a byte-identical recovery copy. Restore it only when the working database is missing:

```powershell
Copy-Item -LiteralPath `
  'C:\Work\silverleaf-agentic-marketing.__pre_reorg\outputs\master-database\Silverleaf Master Database.sqlite' `
  -Destination 'C:\Work\silverleaf-agentic-marketing\outputs\master\Silverleaf Master Database.sqlite'

python scripts/master/verify_master.py
```

For another machine, obtain the database from the approved private artifact store and place it at the same repository-relative path. Verify its SHA-256 before use. The database used for this repository reorganisation has SHA-256 `895e3ebabba3f9a7d710bbb6cb820a71beca1d7a72fa99d6fa55408e37fdcf7c`.

## Choose the workflow

- Start a separate lead database with `skills/silverleaf-create-lead-list/SKILL.md`.
- Add research to the existing master with `skills/silverleaf-update-lead-list/SKILL.md`.
- Draft or revise evidence-backed partnership copy with `skills/silverleaf-outreach/SKILL.md`.

SQLite remains authoritative. Do not maintain an independent workbook-only lead list. Personalised hooks are optional and must have a supporting source and verification date. No script in this repository sends messages or enables automation.

## Set up the local tools

From PowerShell:

```powershell
cd C:\Work\silverleaf-agentic-marketing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm install
python scripts/master/verify_master.py
```

The Python lead-list skills use the standard library. `openpyxl` supports the retained partner-list builder, while `@oai/artifact-tool` rebuilds the consolidated workbook. Dependencies and generated runtime files are ignored by Git.

## Update the existing master list

Use this workflow when new organisations, public business contacts, public parent enquiries, evidence, or outreach drafts belong in the current master.

### 1. Create an intake file

Copy the complete intake header:

```powershell
New-Item -ItemType Directory -Force -Path runtime\intake | Out-Null
Copy-Item skills\silverleaf-create-lead-list\assets\lead-intake-template.csv runtime\intake\master-update.csv
```

Add one row per organisation, contact, or enquiry. Follow `skills/silverleaf-create-lead-list/references/lead-list-data-contract.md`. Every row needs a precise source locator, acquisition date, verification date, evidence basis, and evidence excerpt. Do not infer private contact details or personal status.

### 2. Validate the intake

```powershell
python skills/silverleaf-create-lead-list/scripts/validate_intake.py `
  runtime\intake\master-update.csv `
  --report runtime\artifacts\intake-validation.json
```

Resolve every validation error before continuing. Warnings identify duplicate exact keys or review points and require inspection.

### 3. Preflight against the master

```powershell
python skills/silverleaf-update-lead-list/scripts/preflight_update.py `
  "outputs/master/Silverleaf Master Database.sqlite" `
  runtime\intake\master-update.csv `
  --report runtime\artifacts\update-preflight.json
```

Review the proposed exact matches, inserts, missing organisations, and review items. Similar names are review signals, not automatic matches.

### 4. Apply the update with the update skill

Give the agent this instruction from the repository root:

```text
Use $silverleaf-update-lead-list to merge runtime/intake/master-update.csv into
outputs/master/Silverleaf Master Database.sqlite. Preserve stable IDs and all
source records, apply the merge in one transaction, regenerate the workbook,
and report the reconciliation results. Do not send or schedule outreach.
```

The skill requires an append-only source trail, exact-key matching, conflict review, before-and-after counts, and rollback when integrity checks fail.

### 5. Refresh and verify generated outputs

After the database merge succeeds:

```powershell
python scripts/master/refresh_acquisition_metadata.py
npm run build:workbook
python scripts/master/verify_master.py
```

The export writes `runtime/artifacts/workbook-input.json`. The builder refreshes `outputs/master/Silverleaf Master Database - Consolidated.xlsx`, writes visual previews under `runtime/previews/`, and records workbook checks in `outputs/reports/workbook-verification.json`.

An update is complete when database integrity and foreign-key checks pass, counts reconcile, every outreach plan has an acquisition track, all active hooks are supported, and all automations remain disabled.

## Start a separate lead-list run

Use this workflow when the objective, geography, audience, or delivery boundary requires a separate database rather than an addition to the Silverleaf master.

Choose a short run ID containing lowercase letters, numbers, and hyphens. The example below uses `arusha-employers-2026-09`.

### 1. Prepare the run

```powershell
$runId = 'arusha-employers-2026-09'
New-Item -ItemType Directory -Force -Path "data/runs/$runId","outputs/runs/$runId" | Out-Null
Copy-Item skills/silverleaf-create-lead-list/assets/lead-intake-template.csv "data/runs/$runId/intake.csv"
```

Before research, record the campaign objective, campuses or localities, radius, lead types, channels, recency window, and stopping rule. Then populate the intake with sourced organisations, contacts, and enquiries.

### 2. Validate and initialise the new database

```powershell
python skills/silverleaf-create-lead-list/scripts/validate_intake.py `
  "data/runs/$runId/intake.csv" `
  --report "outputs/runs/$runId/intake-validation.json"

python skills/silverleaf-create-lead-list/scripts/initialize_lead_db.py `
  "data/runs/$runId/intake.csv" `
  "outputs/runs/$runId/lead-database.sqlite"
```

The initializer refuses to overwrite an existing database. Supply `--replace` only when the user explicitly requests a rebuild of that run.

### 3. Complete the run with the create skill

Give the agent this instruction:

```text
Use $silverleaf-create-lead-list to complete the lead-list run at
outputs/runs/arusha-employers-2026-09. Use the validated intake, preserve all
source provenance, create the review workbook described by the skill, verify
all sheets and counts, and leave outreach and automations disabled.
```

Keep separate-run outputs under `outputs/runs/<run-id>/`. Do not merge them into the master unless the user later requests an update and the update preflight passes.

## Current verified master

The verified master at the time of the repository reorganisation contains 955 organisations, 342 contacts, 32 enquiries, 927 messages and outreach plans, 959 campaign assignments, 139 strategy records, and 54 automation steps. All automations are disabled. Run `python scripts/master/verify_master.py` for current counts.
