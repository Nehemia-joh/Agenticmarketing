# Silverleaf agentic marketing intelligence

This repository holds Silverleaf's sourced lead intelligence, partnership strategy, outreach drafts, and disabled automation designs. The canonical operational dataset is the local file `outputs/master/Silverleaf Master Database.sqlite`. Git intentionally ignores that mutable database. The consolidated workbook is a generated review view of the database.

## Repository map

| Path | Contents |
|---|---|
| `data/raw/lead-research/` | Captured raw lead-research responses and source text. |
| `data/interim/partner-leads/` | Structured collection outputs awaiting canonical import. |
| `data/reference/` | Supporting lookup data. |
| `data/evidence/` | Current verification records used by qualification or copy. |
| `data/raw/welfare-research/` | Welfare research records, coverage logs, NGO register and OpenStreetMap extracts, with a hash manifest. |
| `data/interim/welfare-leads/` | Welfare organisation, contact, relationship and register tables from the latest welfare run. |
| `data/raw/government-research/` | Census ward tables, council-site captures, councillor-list transcriptions, Wikipedia and OpenStreetMap extracts, with a hash manifest. |
| `data/interim/government-leads/` | Wards, convening offices, official posts, office triage and convening signals from the latest government run. |
| `data/runs/` | Inputs for separate runs: run config, reviewed curation (`links.json`), research plan and intake. |
| `references/` | Original Silverleaf business and marketing source documents. |
| `docs/scope/` | Agreed project scope. |
| `docs/plans/` | Delivery plan. |
| `docs/methodology/` | Lead-generation and research method. |
| `docs/strategy/` | Positioning, hooks, acquisition tracks, flows, cadence, and marketing-document findings. |
| `scripts/` | Every reusable script, catalogued by task in `scripts/README.md`. Check the catalogue before writing a new script. |
| `scripts/collection/` | Deterministic collection and source-list builders. |
| `scripts/master/` | Acquisition refresh, workbook export/build, and master verification. |
| `scripts/welfare/` | Welfare-lead collectors, research planner, run pipeline and the shared rate-limited HTTP helper. |
| `scripts/government/` | Government-lead collectors (census, council sites, OpenStreetMap, Wikipedia), run pipeline and verification. |
| `skills/` | Reusable create-list, update-list, outreach, welfare-leads and government-leads skills. |
| `outputs/master/` | Canonical SQLite database and consolidated review workbook. |
| `outputs/config/` | Disabled automation recipes. |
| `outputs/reports/` | Current verification results. |
| `outputs/runs/` | Separate run outputs: database (ignored by Git), review workbook, validation and verification reports. |
| `plans/` | Plans for new lead tracks and presentations. |
| `runtime/` | Ignored scratch space for generated working files, HTTP caches and rendered research prompts. |

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

On macOS or Linux, restore a privately supplied copy from the repository root:

```bash
mkdir -p outputs/master
cp "/path/to/Silverleaf Master Database.sqlite" \
  "outputs/master/Silverleaf Master Database.sqlite"

# macOS
shasum -a 256 "outputs/master/Silverleaf Master Database.sqlite"

# Linux
sha256sum "outputs/master/Silverleaf Master Database.sqlite"

python3 scripts/master/verify_master.py
```

Replace `/path/to/` with the approved private artifact location. Do not commit the SQLite file.

## Choose the workflow

- Start a separate lead database with `skills/silverleaf-create-lead-list/SKILL.md`.
- Add research to the existing master with `skills/silverleaf-update-lead-list/SKILL.md`.
- Draft or revise evidence-backed partnership copy with `skills/silverleaf-outreach/SKILL.md`.
- Research welfare institutions as paying customers with `skills/silverleaf-welfare-leads/SKILL.md`. Each welfare run stays separate from the master.
- Map local government offices that can convene community meetings, where Silverleaf can meet parents, with `skills/silverleaf-government-leads/SKILL.md`. Each government run stays separate from the master.

SQLite remains authoritative. Do not maintain an independent workbook-only lead list. Personalised hooks are optional and must have a supporting source and verification date. No script in this repository sends messages or enables automation.

## Set up the local tools

Install Python 3, Node.js, and npm before running the repository workflows.

From Windows PowerShell:

```powershell
cd C:\Work\silverleaf-agentic-marketing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm install
python scripts/master/verify_master.py
```

From macOS or Linux using Bash or zsh:

```bash
cd /path/to/silverleaf-agentic-marketing
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
npm install
python3 scripts/master/verify_master.py
```

Use `python3` in the commands below on macOS and Linux. If your environment maps `python` to Python 3, either command name works.

The Python lead-list skills use the standard library. `openpyxl` supports the retained partner-list builder, while `@oai/artifact-tool` rebuilds the consolidated workbook. Dependencies and generated runtime files are ignored by Git.

## Update the existing master list

Use this workflow when new organisations, public business contacts, public parent enquiries, evidence, or outreach drafts belong in the current master.

### 1. Create an intake file

Copy the complete intake header:

```powershell
New-Item -ItemType Directory -Force -Path runtime\intake,runtime\artifacts | Out-Null
Copy-Item skills\silverleaf-create-lead-list\assets\lead-intake-template.csv runtime\intake\master-update.csv
```

macOS or Linux:

```bash
mkdir -p runtime/intake runtime/artifacts
cp skills/silverleaf-create-lead-list/assets/lead-intake-template.csv \
  runtime/intake/master-update.csv
```

Add one row per organisation, contact, or enquiry. Follow `skills/silverleaf-create-lead-list/references/lead-list-data-contract.md`. Every row needs a precise source locator, acquisition date, verification date, evidence basis, and evidence excerpt. Do not infer private contact details or personal status.

### 2. Validate the intake

```powershell
python skills/silverleaf-create-lead-list/scripts/validate_intake.py `
  runtime\intake\master-update.csv `
  --report runtime\artifacts\intake-validation.json
```

macOS or Linux:

```bash
python3 skills/silverleaf-create-lead-list/scripts/validate_intake.py \
  runtime/intake/master-update.csv \
  --report runtime/artifacts/intake-validation.json
```

Resolve every validation error before continuing. Warnings identify duplicate exact keys or review points and require inspection.

### 3. Preflight against the master

```powershell
python skills/silverleaf-update-lead-list/scripts/preflight_update.py `
  "outputs/master/Silverleaf Master Database.sqlite" `
  runtime\intake\master-update.csv `
  --report runtime\artifacts\update-preflight.json
```

macOS or Linux:

```bash
python3 skills/silverleaf-update-lead-list/scripts/preflight_update.py \
  "outputs/master/Silverleaf Master Database.sqlite" \
  runtime/intake/master-update.csv \
  --report runtime/artifacts/update-preflight.json
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

macOS or Linux:

```bash
python3 scripts/master/refresh_acquisition_metadata.py
npm run build:workbook
python3 scripts/master/verify_master.py
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

macOS or Linux:

```bash
run_id='arusha-employers-2026-09'
mkdir -p "data/runs/$run_id" "outputs/runs/$run_id"
cp skills/silverleaf-create-lead-list/assets/lead-intake-template.csv \
  "data/runs/$run_id/intake.csv"
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

macOS or Linux:

```bash
python3 skills/silverleaf-create-lead-list/scripts/validate_intake.py \
  "data/runs/$run_id/intake.csv" \
  --report "outputs/runs/$run_id/intake-validation.json"

python3 skills/silverleaf-create-lead-list/scripts/initialize_lead_db.py \
  "data/runs/$run_id/intake.csv" \
  "outputs/runs/$run_id/lead-database.sqlite"
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

## Research rate limits

Lead research runs into hard limits. Read `skills/silverleaf-create-lead-list/references/research-rate-limits.md` before starting any research.

- **Web search:** the agent WebSearch tool has a per-session cap (200 in the 2026-09 welfare run) shared by every subagent. Eight unbudgeted parallel agents used it all in about 40 minutes. Run deterministic collectors first, give each agent an explicit allocation (`plan_research.py` does this), and launch at most four agents per wave. Raising the cap means setting `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` and starting a new session.
- **Web fetch:** pace requests to about one every 2 seconds per site.
  - Known blocks: the UK Charity Commission register, JamiiForums, Facebook groups, Reddit, and Tanzanian council sites that render in JavaScript (their public JSON API works; `scripts/government/collect_council_sites.py` uses it).
  - Record blocks; never work around them.
- **NGOs Information System:** at most 4 workers, 0.3 seconds apart. 855 profiles took about 30 minutes.
- **OpenStreetMap Overpass:** one query at a time, 5 seconds apart, with small queries. Broad regex queries return HTTP 504, and back-to-back queries can return 429.
- **Council and regional websites:** one API request at a time per site, 1.5 seconds apart.
- **Wikipedia API:** one request every 2 seconds; it answered HTTP 429 at one per second.

The welfare and government scripts enforce the network limits in code (`scripts/welfare/welfare_lib.py` and `scripts/government/gov_lib.py`).

## Run a welfare-lead run

Welfare leads are institutions that pay school fees for the children in their care or programme. Each run has its own database and workbook under `outputs/runs/<run-id>/`, and never changes the company-leads master.

From Windows PowerShell:

```powershell
$runId = 'arusha-welfare-2026-09'
# Rebuild an existing run from its committed files (no network calls).
python scripts/welfare/run_pipeline.py --run-id $runId --rebuild-db

# For a new run, create data/runs/<run-id>/run-config.json from the skill's example, then:
python scripts/welfare/fetch_ngo_register.py --run-id $runId
python scripts/welfare/collect_osm_welfare.py --run-id $runId
python scripts/welfare/plan_research.py --run-id $runId --search-budget 200
```

macOS or Linux:

```bash
run_id='arusha-welfare-2026-09'
python3 scripts/welfare/run_pipeline.py --run-id "$run_id" --rebuild-db

python3 scripts/welfare/fetch_ngo_register.py --run-id "$run_id"
python3 scripts/welfare/collect_osm_welfare.py --run-id "$run_id"
python3 scripts/welfare/plan_research.py --run-id "$run_id" --search-budget 200
```

Research agents then work through the prompts that `plan_research.py` writes to `runtime/welfare/<run-id>/prompts/`, in waves of at most four. Record reviewed matches and location fixes in `data/runs/<run-id>/links.json`, then run `run_pipeline.py`. The skill explains every step.

The current welfare run, `arusha-welfare-2026-09`, holds:
- 497 organisations: 253 researched, and 243 from the NGO register only
- 131 contacts: 20 low, 90 medium and 21 risky for data protection
- 3 public parent enquiries, all risky
- 214 funder and partner links, and 92 review items

All 19 verification checks pass. Its web research is incomplete because the search cap was reached; each slice's coverage log lists the gaps.

## Run a government-lead run

A government lead is a local government office that can convene a community meeting (a baraza) where Silverleaf can meet parents: a council, a ward, village or mtaa office, or a district or regional office. The office is the lead, not the person holding it, and parents never enter the run: they opt in with Silverleaf at an event. Each run has its own database and workbook under `outputs/runs/<run-id>/`, and never changes the company-leads master. It needs no web search.

From Windows PowerShell:

```powershell
$runId = 'arusha-government-2026-09'
# Rebuild an existing run from its committed files (no network calls).
python scripts/government/run_pipeline.py --run-id $runId --rebuild-db

# For a new run, create data/runs/<run-id>/run-config.json from the skill's example, then:
python scripts/government/collect_census_wards.py --run-id $runId
python scripts/government/collect_ward_locations.py --run-id $runId
python scripts/government/collect_osm_government.py --run-id $runId
python scripts/government/collect_council_sites.py --run-id $runId
```

macOS or Linux:

```bash
run_id='arusha-government-2026-09'
python3 scripts/government/run_pipeline.py --run-id "$run_id" --rebuild-db

python3 scripts/government/collect_census_wards.py --run-id "$run_id"
python3 scripts/government/collect_ward_locations.py --run-id "$run_id"
python3 scripts/government/collect_osm_government.py --run-id "$run_id"
python3 scripts/government/collect_council_sites.py --run-id "$run_id"
```

Transcribe any councillor list published only as a scanned PDF into `data/raw/government-research/transcriptions/`, record reviewed ward spellings and locations in `data/runs/<run-id>/links.json`, then run `run_pipeline.py`. The skill explains every step.

The current government run, `arusha-government-2026-09`, holds:
- 149 convening offices: 9 councils, 128 wards, 2 mapped village offices, 7 district and 3 regional offices
- 4 councils proposed for a protocol introduction (GA01): Arusha City, Arusha District, Meru and Hai; every other office is on hold (GA00)
- 459 official posts: 66 named as their office publishes them (council leaders, regional leaders, and the ward councillors of Hai and Arusha District), all medium risk
- 221 wards with 2022 census populations; 113 lie within 25 km of a campus, with 1.75 million residents, and are scored and ranked by campus cluster
- 63 review items, including 15 core-council wards without a location

All 27 verification checks pass. The Read Me sheet lists the coverage gaps: most councils publish no ward-by-ward councillor list, and no council publishes its executive officers' names or phones.

## Current verified master

The current verified master contains 955 organisations, 353 contacts, 32 enquiries, 927 messages and outreach plans, 959 campaign assignments, 139 strategy records, and 54 automation steps. All automations are disabled. Run `python scripts/master/verify_master.py` on Windows or `python3 scripts/master/verify_master.py` on macOS and Linux for current counts.
