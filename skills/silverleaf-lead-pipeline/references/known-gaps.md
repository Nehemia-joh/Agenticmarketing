# Known gaps and inconsistencies (13 October 2026)

These were found by comparing the scripts, `scripts/README.md`, the methodology documents and `git log`. Where they disagree, the pipeline follows the scripts. Each gap is a candidate for its own task. Items marked "Fixed" were closed later on 13 October 2026 and are kept for the record.

## Tooling that a rule names but the repository lacks

1. **Email-format track (stage 11). Fixed 13 October 2026.** `scripts/contacts/email_formats.py`, `data/reference/email-formats.json` and the `<track>-low-inferred` files now exist, and `infer_candidate_emails.py` is removed. Candidates live in `runtime/` only, and the master workbook shows the format, not the address. Left for the coordinator: `email_formats.py retire-table --apply` on the master (the 2 October table `candidate_emails`, 31 rows, some medium), then a workbook rebuild, which removes the 29 inferred addresses the committed workbook still holds. The call sheet has no format column yet (plan section 8.3).
2. **Google Maps pins to geocode lines (stage 5). Fixed 13 October 2026.** `scripts/maps/build_gmaps_round.py` writes the lookup record, `geocodes_gmaps_<d><round>.jsonl` and `geocodes_corrections_gmaps_<d><round>.jsonl` from the worklist rows, the browser results and the verdict notes, with the shared-pin check. It reproduces the committed 13 October rounds a, b and c byte for byte. `import_google_maps_lookups.py` still turns a round into contact records and map matches.
3. **The master's first import.** `scripts/collection/build_partner_leads.py` writes only a preview workbook (`runtime/artifacts/partner-leads-preview.xlsx`). The September consolidation that built the master is not in `scripts/`. New companies enter through the gap census or the introducer path.
4. **Savings groups (VICOBA).** `docs/plans/vicoba-integration-plan.md` is approved as phase 1, but no intake, draft or export code exists for VICOBA groups yet.
5. **Strategy deck.** No script builds `outputs/presentations/Silverleaf_Lead_Generation_Strategy_2026-10-12.pptx`. Its counts come from the queries in `..._sources.md`, and its slide map is in `..._slide-map.md`.
6. **Segment and catchment documents.** `Silverleaf Core Segments - <date>.md` and `Silverleaf Catchment Criteria - <date>.md` are written by hand. Their counts go stale after every rebuild.

6a. **Google Maps verification of placed leads.** Deferred (user, 13 October 2026): a verification pass that cross-checks leads already placed by their website or OpenStreetMap against Google Maps. Leads are placed; do it much later. No worklist command exists for it yet; `collect_geocodes.py worklist` lists only leads not at point level.

## Copies that should match but do not

7. **`docs/strategy/` and `skills/silverleaf-outreach/references/`. Fixed 13 October 2026.** Every pair is now identical, and `scripts/docs/check_doc_pairs.py` checks them with the run script copies (the pre-commit checklist runs it). The offer register took the skill copy (current on all three points below). Hook guidance merged both: the skill copy's guidance, plus the docs copy's examples and field list, without its stale 7 September status line. The flows file took the docs copy, with the 11 October proposal; `outreach-flows.md` and `flows-and-automations.md` are one document under two names. As found:
   - `offer-register.md`: both copies were updated for register v6 on 13 October 2026, but the docs copy is behind on three points.
     - It lacks the promotional-incentive rule (11 October 2026).
     - It still says sponsorship is asked "of welfare funders only, never of employers", though variant A has existed since 1 October.
     - It has the pre-11-October AQ01 row.
   - `hook-guidance.md`: the wording differs throughout. The docs copy is still headed "Version 7 September 2026". Both copies were last changed on 23 September.
   - `outreach-flows.md` (docs) and `flows-and-automations.md` (skill) share their opening. Only the docs copy carries the 11 October proposal ("a change is proposed below").
   - No check enforces these pairs. The welfare and government script copies, by contrast, are checked by `skill_script_copies_in_sync`.

## Catalogue and docstrings out of date

8. Fixed 13 October 2026: `scripts/README.md` said `verify_government_run.py` runs 27 checks. It runs 30, as the government skill says.
9. Fixed 13 October 2026: `scripts/README.md` had no row for `scripts/messaging/build_company_audience_profile.py` or `scripts/messaging/load_resend_contacts.py`.
10. Fixed 13 October 2026 (also `draft_master_messages.py` and `export_resend_contacts.py`). These cited the old draft paths:
    - the `render_markdown_page.py` docstring and its catalogue example use `docs/strategy/partnership-pipelines-draft.md` and `Silverleaf Partnership Pipelines - Draft.html`;
    - the `first_touch.py` and `draft_run_messages.py` docstrings cite `partnership-pipelines-draft.md` section 4.

    The draft is now a stub. The approved file is `partnership-pipelines.md`, and the page is `outputs/strategy/Silverleaf Partnership Pipelines.html`.
11. The strategy deck's sources file shows mojibake ("A1â€“A12"), a UTF-8 en dash read as cp1252. The file named `_slide-map.md` opens with the heading "Sources: ... condensed deck".

## Order notes that disagree

12. **Drafts and tracks.** `.claude/CLAUDE.md` and `contact-research.md` run `draft_master_messages.py` before `refresh_acquisition_metadata.py`. The drafter's docstring says to re-run it "after a contact merge and the acquisition refresh". The drafter applies the same track rule itself (`track_for`), so both orders converge. This pipeline runs the drafter first.
13. **Reach tiers and drafts.** The orders disagree:
    - `apply_geocodes.py` says recompute, rank, then draft;
    - `add_gap_census_leads.py` says draft, refresh, then rank;
    - the history of 11 October ran "drafts, recipients, tracks, reach tiers".

    The rank reads the chosen plans, and the drafter reads the tiers (the case B ', or your HR lead' line). When either changes, rank and then re-draft.
14. **Variants and drafts.** `assign_message_variants.py` lists only the sponsorship file, the workbook and the verification as next steps. But the drafter reshapes the stored variant drafts into their first-touch format (`variant_subject_base`, `variant_body_base`), so the drafter must run after it.
15. **The contact-merge refresh** in `contact-research.md`, step 4, leaves out two steps: recipient resolution and `npm run build:workbook`. The high-direct plan (section 5) and the history include both.
16. **The browser pane.** `research-rate-limits.md` says only the coordinator uses the pane. `contact-research.md` describes browser agents, each in its own tab. Treat a browser pass as the coordinator's work, or one browser agent counted among the four.

## Side effects to expect

17. **Manifest churn.** `export_welfare_run.py` and `export_government_run.py` rewrite `MANIFEST.md` with the SHA-256 of each raw file as checked out. With `core.autocrlf=true`, unchanged text files can hash differently.
18. **Absolute paths in reports.** Three committed reports record the absolute path of the checkout that ran them: `outputs/reports/master-verification.json` and the two `outputs/runs/<r>/intake-validation.json`.
19. **The lead map reads more than the databases.** It also reads `data/raw/geocode-research/geocodes_*.jsonl` (why a lead is unplaced), the basemap and `scripts/maps/lead_map_template.html`. A new geocode file changes the map even when no database changes.
20. **`npm run build:workbook` exports first,** so the documented order runs `export_master_workbook_data.py` twice. This is harmless.
