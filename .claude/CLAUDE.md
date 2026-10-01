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




**Delegate and Orchestrate**
- When your environment supports subagents and separate worktrees, the thread the user talks to can run as an orchestrator. It plans, talks with the user, delegates approved work to workers, and consolidates their results, so it stays free while workers build. Without that support, do the same plan sequentially.
- Delegation has two phases. **Phase 1:** a worker may be sent to diagnose and plan: it investigates, writes the plan (evidence, root cause, proposed fix, decisions with a recommended option, files it would touch, test plan), commits it to its own branch and stops. **Phase 2:** implementation starts only after the user signs off, and it goes back to the same worker, which still has the context. A worker never moves on to phase 2 by itself.
- The orchestrator reviews each plan before it reaches the user: it checks the evidence, reconciles plans that touch the same area, and presents the decisions. Where the work touches security, access or data boundaries, the plan must say plainly whether a real gap exists today. When presenting a worker's plan, give the user a link to the raw plan file alongside the review, so the relay can be checked against its source. The link points into the worker's worktree until the plan is merged, and to the working branch's copy after.
- The plan names each task's boundary: what it builds, the files it owns, the contracts it shares with other tasks, and its tests. The orchestrator chooses the boundaries, and the user approves them with the plan.
- Draw boundaries by file ownership. Tasks that must edit the same files, or build on each other's output, run in sequence rather than side by side. Fix any contract two tasks share (a shared list of names, a response shape, a constant mirrored in another language) in the plan before either starts.
- Each task runs in its own worktree, branched from the current working branch at its current `HEAD`, never in the main checkout. Other sessions share the main checkout and have stashed work and switched branches under a task. A worker stays inside the files it owns, commits to its own branch, and never pushes, stashes, or switches another checkout's branch. The worker's brief names these limits, because the worker does not see this conversation.
- Worktree traps:
    - Check the base before starting. A worktree tool may branch from another ref (one worker's came from a staging merge, not the working branch). The worker compares its `HEAD` with the working branch's, resets its own branch onto the working branch if they differ, and says so in its report.
    - Put a worktree under `.claude/worktrees/`, so Node resolves the main checkout's `node_modules`.
    - There, run `node scripts/run-node-tests.mjs unit integration`, not `yarn test`, which fails in a worktree.
    - Never junction `node_modules` into a worktree.
    - Browser fixtures there need their own `next dev`.
    - A session running in a worktree cannot edit the main checkout's files.
- While a task runs, report it as running and never predict its result. Take the next request, plan the next piece, or ask the user what to work on next.
- New information from the user, another worker, or a finished task goes to the worker it affects, as a follow-up to that same worker rather than a new one. If it invalidates the work, stop the worker and re-scope the task. Update the plan either way, so the written plan matches what is being built.
- The orchestrator owns integration. For each finished task:
    - Read the diff and the report critically: workers flag problems in files they did not own, and those need acting on.
    - Merge the worker's branch into the working branch, resolve any conflict against the plan, then delete the worker's branch and worktree.
    - Carry any failure a worker called pre-existing into the final report, after checking it on a clean `HEAD`.
- Delegate work that is sizeable and independent. Each worker costs a full context; a small fix is faster done in the thread.
