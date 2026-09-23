# Silverleaf lead-generation guide

Read `../AGENTS.md` and the relevant skill before changing data. Before writing a script, check `../scripts/README.md` for one that already does the task. Reusable scripts live in `scripts/<task>/`, and `runtime/` is only for generated working files.

The canonical database is `../outputs/master/Silverleaf Master Database.sqlite`. The workbook beside it is generated for review. Create a new independent list with `../skills/silverleaf-create-lead-list/SKILL.md`; update the master with `../skills/silverleaf-update-lead-list/SKILL.md`; revise partnership copy with `../skills/silverleaf-outreach/SKILL.md`.

Required order for an update:

```powershell
python skills/silverleaf-create-lead-list/scripts/validate_intake.py <intake.csv>
python skills/silverleaf-update-lead-list/scripts/preflight_update.py "outputs/master/Silverleaf Master Database.sqlite" <intake.csv>
# Apply a reviewed, transactional merge.
python scripts/master/export_master_workbook_data.py
npm run build:workbook
python scripts/master/verify_master.py
```

Every claim must remain traceable to a source record. Do not infer private contact details or personal status. Leave an unsupported hook blank. Keep all sending and automations disabled.

Welfare leads (children's homes, care programmes, specialised centres, funders) use `../skills/silverleaf-welfare-leads/SKILL.md`. Each run is separate from the master:

```powershell
python scripts/welfare/run_pipeline.py --run-id <run-id> --rebuild-db
```

Government leads (local offices that can convene community meetings where Silverleaf meets parents) use `../skills/silverleaf-government-leads/SKILL.md`. Each run is also separate from the master:

```powershell
python scripts/government/run_pipeline.py --run-id <run-id> --rebuild-db
```

Offer terms in any message come only from `../data/reference/silverleaf-offer-register.json`; draft with `scripts/messaging/` (see `../skills/silverleaf-outreach/references/offer-register.md`).

Contact profiles and contact leads for all three databases follow `../docs/methodology/contact-research.md` with the scripts in `scripts/contacts/`. Crawl and collect first. Plan search waves with `scripts/contacts/plan_contact_research.py`. Then merge: `merge_master_contacts.py` (preflight, then `--apply`) for the master, and `export_run_contact_research.py` followed by each run's pipeline for the welfare and government runs.

Research is rate-limited; read `../skills/silverleaf-create-lead-list/references/research-rate-limits.md` first.
- WebSearch has a per-session cap shared by all subagents: plan budgets with `scripts/welfare/plan_research.py`.
- Run deterministic collectors first, and launch at most four research agents per wave.
- Never work around a cap or a block.
