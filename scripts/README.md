# Reusable scripts

Check this catalogue before writing a new script. Reusable scripts live under `scripts/<task>/`. Generated working files (caches, rendered prompts, intermediate JSON) go in `runtime/`, which Git ignores. When a session starts a task, look here first. If a script covers the task, run it or extend it here instead of writing a one-off in `runtime/`.

Run every command from the repository root. Anything that calls the network follows `skills/silverleaf-create-lead-list/references/research-rate-limits.md`, and the welfare and government scripts enforce those limits in code.

## Catalogue

| Task | Script | What it does | Network and rate limits |
|---|---|---|---|
| Company leads: collect | `scripts/collection/collect_partner_leads.js` | Browser-console collector for the TATO directory and OpenStreetMap employers | Runs in a browser tab on tatotz.org; re-run quarterly |
| Company leads: collect | `scripts/collection/build_partner_leads.py` | Builds the partner-lead universe (geocoding, campus distances) from raw pulls | None |
| Company master | `scripts/master/refresh_acquisition_metadata.py` | Assigns AQ acquisition tracks and value modules to outreach plans | None. Corporate rules only (see welfare plan Phase 0) |
| Company master | `scripts/master/export_master_workbook_data.py` | Exports workbook input from the master database | None |
| Company master | `scripts/master/build_master_workbook.py` | Regenerates the consolidated master workbook from the export (openpyxl; `npm run build:workbook` exports first): current offer-aligned drafts, contact-research enrichment, every sheet reconciled with the database | None |
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
| Welfare leads: build | `scripts/welfare/verify_welfare_run.py` | Runs 23 checks, including that the company master is untouched and the skill's script copy matches | None |
| Shared library | `scripts/welfare/welfare_lib.py` | Normalisation, geography, run config and `polite_request` | Per-host limits in `HOST_LIMITS`; reuse `polite_request` for any new collector |
| Government leads: collect | `scripts/government/collect_census_wards.py` | Ward populations from the 2022 census report, with page and row locators; fails unless wards add up to council totals | One cached 13 MB download |
| Government leads: collect | `scripts/government/collect_ward_locations.py` | Wikipedia ward points, OpenStreetMap places and district boundaries for placing wards | Wikipedia 2 s apart; Overpass one query at a time, 5 s apart, mirror fallback |
| Government leads: collect | `scripts/government/collect_osm_government.py` | OpenStreetMap government offices (tags and names) for triage and ward-office points | Overpass one query at a time, 5 s apart |
| Government leads: collect | `scripts/government/collect_council_sites.py` | Council and regional websites through their JSON API: leaders, statistics, contacts, menus, pages, rosters, files, news; sanitised | One request per host at a time, 1.5 s apart, cached |
| Government leads: build | `scripts/government/run_pipeline.py` | Runs every step below in order and stops at the first failure | None |
| Government leads: build | `scripts/government/build_government_run.py` | Places wards, scores them, builds offices and posts, triages offices and master records, tags convening signals | None |
| Government leads: build | `scripts/government/export_government_run.py` | Writes the intake CSV, interim tables and the raw-evidence manifest | None |
| Government leads: build | `scripts/government/augment_government_db.py` | Adds administrative units, office profiles, official posts, community events (counts only), triage, signals, reviews and evidence files | None |
| Government leads: build | `scripts/government/build_government_workbook.py` | Builds the review workbook from the run database only | None |
| Government leads: build | `scripts/government/verify_government_run.py` | Runs 27 checks, including exclusions, data-protection guards, census reconciliation and master separation | None |
| Shared library | `scripts/government/gov_lib.py` | Government run config, host limits, office levels, exclusion list, name keys, sanitising and district geometry | Registers council, census and Wikipedia hosts with `polite_request` |
| Messages: all tracks | `scripts/messaging/offer_lib.py` | Offer register loader, the sender's details, English and Kiswahili offer sentences, campus lines, and the conformance checks for every draft (no offer terms in a first message) | None; terms from `data/reference/silverleaf-offer-register.json` |
| Messages: company master | `scripts/messaging/draft_master_messages.py` | Rewrites every master outreach plan request-first: a meeting request, then the documented offer (register v4) in `offer_message` and AQ02's follow-up 1. Adds plans for organisations without one and keeps earlier versions; `--dry-run` previews | None; one transaction |
| Messages: separate runs | `scripts/messaging/draft_run_messages.py` | Drafts welfare messages (English, request first; sponsorship requests for funders only) or government letters (Kiswahili with English meaning) into a run database; a pipeline step | None |
| Messages: review | `scripts/messaging/build_offer_messages_workbook.py` | One review workbook of all drafts across the three databases; fails if any draft breaks a register rule | None |
| Contacts: collect | `scripts/contacts/crawl_org_websites.py` | Crawls each organisation's own website (master and welfare; `.go.tz` excluded) for published emails, phones, postal addresses, official social pages and named people with roles; resumable | robots.txt Disallow honoured; a site whose robots.txt cannot be read is crawled and flagged; one request per site at a time, 1.5 s apart; cached in `runtime/contacts/http-cache/`, so a re-run re-extracts without the network |
| Contacts: collect | `scripts/contacts/collect_osm_contacts.py` | OpenStreetMap contact tags (phone, email, website) in the catchment | One Overpass query, mirror fallback |
| Contacts: plan | `scripts/contacts/plan_contact_research.py` | Picks organisations still without an email or phone that no agent has searched, ranks them nearest first, splits the wave's search budget over at most four slices and writes each agent's prompt | None; plans only. Launch at most four agents per wave within the session's WebSearch cap |
| Contacts: research | Agent brief in `docs/methodology/contact-research.md` | Budgeted search agents write `data/raw/contact-research/search_<slice>_<date>.jsonl` and a coverage log per slice | WebSearch budget shared by all agents; at most 4 per wave; WebFetch 2 s apart per site |
| Contacts: build | `scripts/contacts/build_contact_profiles.py` | One contact profile per organisation in all three databases, plus contact leads: typed emails and phones, sources, named people filtered to current, relevant roles, one lead per person from the search agent's record when there is one (at most 6 new per organisation: agent-confirmed first, then by most senior role) | None |
| Contacts: company master | `scripts/contacts/merge_master_contacts.py` | Writes the shared-contract intake and runs the validator and preflight; `--apply` fills only empty fields, records facts and sources, sends conflicts to review, inserts contacts and un-holds drafts whose only gap was a route | None; one transaction |
| Contacts: separate runs | `scripts/contacts/export_run_contact_research.py` | Writes welfare research records (`research_W_contact_profiles_<date>.jsonl`) and government office routes (`office_contacts_<date>.json`) for the run pipelines | None |
| Contacts: review | `scripts/contacts/build_contact_workbook.py` | Contact-profiles workbook across the three databases: summary, organisation profiles, contact leads, gaps | None |
| Shared library | `scripts/contacts/contact_lib.py` | Polite cached fetcher, page extractors and the person filter (template names, headings, addresses, roles held at other organisations, former roles and irrelevant staff are dropped) | Registers each crawled host with `polite_request` limits |
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

Two skills carry an identical copy of their scripts, so each skill still works when it is installed on its own:
- `skills/silverleaf-welfare-leads/scripts/` copies `scripts/welfare/`
- `skills/silverleaf-government-leads/scripts/` copies `scripts/government/`

Both libraries find the repository root by walking up to `AGENTS.md`, so the same file runs from either folder. `gov_lib.py` always imports the canonical `scripts/welfare/welfare_lib.py`.

Edit the `scripts/` folder first, then refresh the copy:

```bash
cp scripts/welfare/*.py skills/silverleaf-welfare-leads/scripts/
cp scripts/government/*.py skills/silverleaf-government-leads/scripts/
```

```powershell
Copy-Item scripts/welfare/*.py skills/silverleaf-welfare-leads/scripts/
Copy-Item scripts/government/*.py skills/silverleaf-government-leads/scripts/
```

`verify_welfare_run.py` and `verify_government_run.py` each fail their `skill_script_copies_in_sync` check if the two folders differ.
