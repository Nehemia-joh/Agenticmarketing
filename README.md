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
| `data/raw/contact-research/` | Contact research: website-crawl extracts, OpenStreetMap contact tags, budgeted search records and their coverage logs. |
| `data/interim/contact-profiles/` | Organisation contact profiles and contact leads across the three databases, from the latest contact research. |
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
| `scripts/contacts/` | Contact research: polite website crawler, OpenStreetMap contacts, profile builder, wave planner, master merge, run exports and the review workbook. |
| `scripts/messaging/` | Request-first message drafting for all three databases (the offer follows in the next message), the offer-register checks and the combined review workbook. |
| `skills/` | Reusable create-list, update-list, outreach, welfare-leads and government-leads skills. |
| `outputs/master/` | Canonical SQLite database and consolidated review workbook. |
| `outputs/config/` | Disabled automation recipes. |
| `outputs/reports/` | Current verification results. |
| `outputs/runs/` | Separate run outputs: database (ignored by Git), review workbook, validation and verification reports. |
| `outputs/contacts/` | The contact-profiles review workbook and the master merge report. |
| `outputs/messages/` | The combined review workbook of every draft and its reconciliation reports. |
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

The Python lead-list skills use the standard library. `openpyxl` builds the review workbooks, including the consolidated master workbook (`scripts/master/build_master_workbook.py`); `npm run build:workbook` needs no Node packages. Dependencies and generated runtime files are ignored by Git.

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

The export writes `runtime/artifacts/workbook-input.json`, with each organisation's and contact's enrichment derived from the database:
- organisations: route status, social pages, decision-makers, research methods and flags
- contacts: best route and pdpa_risk

The builder then regenerates `outputs/master/Silverleaf Master Database - Consolidated.xlsx` from scratch in the same layout. Messages, Outreach plans and Sequences show the current offer-aligned drafts. It checks every sheet's row count against the database and records the result in `outputs/reports/workbook-verification.json`, exiting with an error on any mismatch.

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
- 470 contacts: 20 low, 425 medium and 25 risky for data protection
- 3 public parent enquiries, all risky
- 214 funder and partner links, and 95 review items

All 23 verification checks pass. Its web research is incomplete because the search cap was reached; each slice's coverage log lists the gaps.

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

## Outreach messages: request first

Since 23 September 2026 the first message to an organisation makes a relevant request and states no offer terms. This follows Kilusu's recommendation. The first message gives its purpose, introduces the sender and asks for a short meeting, in person or by phone. Mariam Haji, Marketing and Partnership Coordinator, signs every draft in all three databases.
- **Employers:** a meeting about an education benefit for the children of their staff. Where the decision-maker is unknown (AQ01), the message also asks who looks after staff welfare or benefits.
- **Welfare homes and programmes:** working together on the education of the children in their care.
- **Welfare funders:** a request to sponsor students, two or three to start. Sponsorship is asked of funders only. When the welfare run records a funder's verified support for a home, that becomes the reason (46 of 98 funders).
- **Savings groups:** a meeting with the committee, with a Kiswahili version for review.
- **Government offices:** the Kiswahili letters were already requests to give parents a free school-readiness talk. Only the signature changed, and they never offer officials a benefit.

What Silverleaf offers comes in the next message. Company-master AQ02 drafts send it as follow-up 1. Every company draft also keeps it in `offer_message`, the reply to send once someone answers; on AQ01 that is once they name the right colleague. Welfare drafts send it as the follow-up. The terms come only from `data/reference/silverleaf-offer-register.json`, which records each term with its source in `references/Offers & Discounts/` (see `skills/silverleaf-outreach/references/offer-register.md`).
- **Employers:** a staff school-fee benefit at no cost to the employer. Heads of department get 20% off tuition for as long as their child studies with us; other staff get 10% off the first year.
- **Every family:** a free uniform set for full-year payment, 10–20% off for a third or fourth child, and four instalments.
- **Welfare homes, programmes and funders:** the NGO partner rate of 3–18% per child.

The earlier, offer-led copies are kept in `message_versions` (`2026-09-23-before-request-first`).

```powershell
python scripts/messaging/draft_master_messages.py --dry-run   # preview the company-master rewrite
python scripts/messaging/draft_master_messages.py             # apply it; earlier versions stay in message_versions
python scripts/welfare/run_pipeline.py --run-id arusha-welfare-2026-09 --rebuild-db        # includes the welfare drafts
python scripts/government/run_pipeline.py --run-id arusha-government-2026-09 --rebuild-db  # includes the government letters
python scripts/messaging/build_offer_messages_workbook.py     # one review workbook for all three
```

On 23 September 2026, after the contact research below, the drafts were:
- **Company master:** 1,626: the 1,314 organisation plans plus 312 plans for newly found contacts; 81 are AQ02, 1,192 AQ01 and 353 on hold.
- **Welfare:** 490, of which 63 are ready and 427 held with a reason.
- **Government:** 149, of which the 4 council letters are ready and 145 are held. Council letters now carry the council's official postal address.

All of them pass the offer-register checks, and no first message states offer terms. Finance must confirm that the 2025 terms apply to 2027 before any message that states them is sent. The consolidated master workbook shows the company-master drafts (Messages, Outreach plans, Sequences). `outputs/messages/Silverleaf Offer-Aligned Messages - 2026-09-23.xlsx` shows every draft in all three databases.

### Lead briefs and hooks for the named leads

On 23 September 2026, four research agents checked the 58 organisations behind the 82 named decision-makers (AQ02). They used 5 web searches; everything else came from the organisations' own pages. Results:
- **Lead briefs:** 270 facts. Each has its source link, the page title, a verbatim excerpt and the date it was read. The master workbook lists them on the Lead Briefs sheet, and the Messages sheet shows each draft's brief. When a lead replies, the links show who they are.
- **Hooks:** 45 organisations have a verified hook, now in the first message of all 235 of their drafts. Examples:
  - long-serving staff (Cheli & Peacock, African Environments, Duma Explorer, Corto)
  - a published team size (Tanzania Experience's 80 permanent employees)
  - staff-welfare policies (Serengeti Big Cats, Good Earth, Matembezi)
  - education or community programmes (Kojuu, Meru Slopes, Kiliclimb, Kingse, Wonders of Creation)

  13 organisations have no hook. For 8, including Rivertrees by design, no fact supported one. The other 5 were rejected in review as generic or weakly sourced (`data/raw/hook-research/coordinator-review_2026-09-23.json`).
- **Roles:** the agents re-checked each named contact on the page they came from:
  - 75 of 81 were confirmed;
  - one was promoted (a review item);
  - one is no longer listed, so that draft is held;
  - four pages could not be read (review items).
- **35 review items** for a person. 28 are checks the agents raised: possibly better addressees, public bodies that may need approval, names to confirm, companies based in Moshi and a duplicate record. The rest are the role items.

```powershell
python scripts/messaging/plan_hook_research.py --date <date> --track AQ02 --budget <searches>   # then run the agents
python scripts/messaging/apply_hook_research.py --date <date>            # preview
python scripts/messaging/apply_hook_research.py --date <date> --apply    # one transaction; then redraft, refresh, build and verify
```

## Contact profiles and contact leads

Every organisation in the three databases has a contact profile. The profile holds the organisation's published website, emails, phones, postal address and official social pages, and its contact leads: the named people who lead or decide for it, exactly as the organisation or an official source publishes them. The method, rules and agent brief are in `docs/methodology/contact-research.md`.

```powershell
python scripts/contacts/crawl_org_websites.py --date <date>            # own websites; cached; robots.txt Disallow honoured
python scripts/contacts/collect_osm_contacts.py --date <date>
python scripts/contacts/build_contact_profiles.py --date <date>
python scripts/contacts/plan_contact_research.py --date <date> --wave 1 --budget <searches>   # then run the agents
python scripts/contacts/build_contact_workbook.py --date <date> --baseline   # before any merge
python scripts/contacts/merge_master_contacts.py            # validator and preflight reports
python scripts/contacts/merge_master_contacts.py --apply    # one transaction
python scripts/contacts/export_run_contact_research.py      # then the welfare and government pipelines with --rebuild-db
python scripts/contacts/build_contact_workbook.py --date <date>
```

On 23 September 2026 the research used:
- **Own websites:** 731 crawled, including the 150 websites the research found. 619 were readable, 104 were not, and robots.txt disallowed 8.
  - A robots.txt that cannot be read (server, network or certificate error) no longer stops the crawl: the site is crawled and its details are flagged.
  - Of the 52 sites affected, 48 were down altogether. Tropical Trails and Kilpath African Safaris were read and flagged. Roy Safaris and Neema International now serve a readable robots.txt.
- **Search agents:** 482 records from 10 agents in three waves, using 309 searches.

It left these results (review them in `outputs/contacts/Silverleaf Contact Profiles - 2026-09-23.xlsx`):

| | Company master | Welfare | Government |
|---|---|---|---|
| Organisations with a published email or phone | 598 → 709 of 955 | 101 → 196 of 497 | 28 → 37 of 149 |
| Organisations with a named decision-maker | 160 → 238 | 52 → 142 | 9 (unchanged) |
| Contact leads | 353 → 659 | 131 → 470 | 459 (office posts) |
| Contact leads reachable by their own or their organisation's route | 655 | 439 | 79 |

The master's 598 also counted 21 organisations whose phone field holds a directory code ('AFF/FIN', 'TO/DMC/MAIN') rather than a number; the 709 counts only real numbers and addresses.

- **Master:** four merges filled 481 empty fields, added 306 contacts and released 97 held drafts because a route was found. 87 review items are open:
  - website conflicts and phone fields holding codes
  - lost, parked or hijacked domains
  - possible duplicates
  - five records whose details come from a site crawled although its robots.txt could not be read: three Tropical Trails duplicates and two Kilpath records. They are flagged, and their drafts are not held
  - possible closures, whose drafts are held: FBME Arusha, Fastjet's ticket office, Impala Hotel, Tin Tin Tours and Lemuta & Khaki Safaris
- **Welfare:** 339 new named leads and 95 more organisations with a direct route. Organisation records are unchanged: 497 before and after.
- **Government:** every council in the run and the Arusha and Kilimanjaro Regional Secretariats now have their official email, office phone and P.O. Box, from their own letterheads and service charters. Only Manyara's secretariat lacks an email and phone; it has its P.O. Box.
- **Filtered out:**
  - template names, headings and client testimonials
  - branch addresses, departments and page labels read as names ('Jomo Kenyatta Avenue', 'Human Resources', 'Select Page')
  - roles held at another organisation: a trustee's own business, another board, a partner NGO
  - former roles and staff outside outreach (chefs, guides, security, accountants)
  - people beyond six new leads per organisation
- **Leads kept:** when a search agent and a website list the same person, the lead takes the agent's name and role. People an agent confirmed are always kept; the rest rank by their most senior role, with board officers above coordinators.
- **Flags:** the Flags sheet lists 209 research warnings for a person to check, including the five robots.txt flags.

Still without a route:
- savings groups, reached through KINEFA
- register-only NGOs with no web presence
- ward and village offices
- organisations every wave searched without finding a route (the Gaps sheet lists them with what was tried)

Only 13 in-scope organisations were never searched (12 welfare homes, programmes and funders, and one employer). The planner (`plan_contact_research.py --wave 4`) puts them in the next wave.

## Current verified master

The current verified master contains 955 organisations, 659 contacts, 32 enquiries, 1,626 messages and outreach plans, 1,658 campaign assignments, 141 strategy records, and 54 automation steps. All automations are disabled. Run `python scripts/master/verify_master.py` on Windows or `python3 scripts/master/verify_master.py` on macOS and Linux for current counts.
