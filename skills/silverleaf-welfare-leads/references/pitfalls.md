# Welfare-lead pitfalls found the hard way (2026-09 run)

Each entry records a trap that would catch a competent agent again, and says how the scripts in `scripts/welfare/` now handle it.

| Pitfall | What happened | Now handled by |
|---|---|---|
| Web search runs out mid-research | Eight unbudgeted parallel agents used the session's 200 searches in about 40 minutes; most slices stopped early | `plan_research.py` writes each slice's search allocation into its prompt; `research-rate-limits.md` |
| Road names geocode to other cities | "Arusha–Nairobi highway" put SOS Children's Village in Nairobi; "Dodoma road" put an Arusha NGO in Dodoma | `consolidate_research.py` skips place names that form part of a road name and prefers in-region matches |
| Multi-site organisations geocode to the wrong site | Kafika House's Karatu house (outside the catchment) won over its Arusha headquarters | Earliest-mentioned specific place wins; `links.json` `geo_overrides` for known multi-site organisations |
| A funder merges into the home it funds | "Kesho" was recorded with LOHADA's website and the domain rule merged them | Domain and name merges only join records of the same kind; mismatches go to review |
| National or cumulative child counts inflate priority | Compassion's national 125,551 children scored as local capacity | `build_welfare_run.py` scores national totals at 10 points and cumulative figures at half |
| "Children's" vs "Children" blocks exact matches | Karim Children's Care Centre and its register entry did not link | `name_key` normalises possessives and spelling variants |
| Similar-name review floods the queue | Generic words (foundation, children, home) matched unrelated names | Review needs overall similarity plus a distinctive shared word |
| Register map pins are self-reported | Moshono Children Foundation sat 14 km from Boma Ng'ombe although Moshono is in Arusha | Register-only locations carry `geocode_precision` `registry`/`estimated`; treat distances as approximate |
| Organisation domain shared by several records | A diocese or US charity site lists several homes | A domain shared across organisations is never an identity key; review item raised |
| Coarse locations hold too much | Every "Arusha" record held for town-level location | Hold only when the town straddles the 25 km line (Moshi, not Arusha city) |
| Council and register sites render in JavaScript | Plain fetches returned only the page title; deep links redirected | Collect embedded data by script (NGO register); record council sites as blocked for agents |
| The master baseline hash in `outputs/reports/master-verification.json` is stale | It predates the 10 September contact enrichment | `run_pipeline.py` records a fresh baseline at the start of each run and verification compares against it |
| A "pieced together" email looked unreliable | Samaritan Village's Gmail address came from broken page text | A manual spot-check of cited pages confirmed it; spot-check at least five top leads each run |
