# Silverleaf lead-generation guide

Read `../AGENTS.md` and the relevant skill before changing data.

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
