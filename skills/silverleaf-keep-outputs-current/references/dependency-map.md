# Dependency map: what to re-run after each kind of change

"Steps 1 to 10" means the full rebuild order in `../SKILL.md`. "R+R" means the location pair, run first:

```powershell
python scripts/master/recompute_campus_distances.py --apply
python scripts/master/rank_employer_reach.py --apply
```

"Rank again" means `rank_employer_reach.py --apply` after step 1, then steps 2 to 6 once more, because the drafter reads the tier (see `../SKILL.md`). The evidence for each dependency is the reader list in [script-io.md](script-io.md). Each section ends with what is still unclear.

## 1. The offer register or offer wording

- **Changed:** `data/reference/silverleaf-offer-register.json`, or the offer sentences in `scripts/messaging/offer_lib.py`.
- **Readers:** `offer_lib.py`, so every drafter (`draft_master_messages.py`, `draft_run_messages.py`), the exporter, the consolidators and `build_offer_messages_workbook.py`. `build_master_workbook.py` only names the register in sheet text.
- **Re-run:** steps 2 to 10. Then `build_offer_messages_workbook.py --date <d>`, `consolidate_welfare_drafts.py` and `consolidate_government_drafts.py`.
- **Docs, in the same commit:**
  - `docs/strategy/offer-register.md` and `skills/silverleaf-outreach/references/offer-register.md` (keep them identical);
  - `docs/strategy/partnership-pipelines.md` section 6, if the rule changed, and then the pipelines page (section 15 below);
  - the deck's offer slide and its sources file, if the deck states the term.
- **Check:** `conformance_issues` 0, the offers workbook exits 0, and both runs pass `messages_conform_to_offer_register` and `letters_conform_to_offer_register_and_offer_officials_nothing`. Segment counts should not move; an offer change does not change a band.
- **Precedent:** `591de40` (register v5, 12 October 2026).

## 2. Message copy or `first_touch.py`

- **Changed:** the copy in `draft_master_messages.py`, `draft_run_messages.py` or `first_touch.py`, or the sponsorship template in `draft_employer_sponsorship.py`.
- **Readers:** the master drafter and the run drafter. `assign_message_variants.py` stores the sponsorship variant drafts that the drafter then reshapes.
- **Re-run:**
  - steps 2 to 10;
  - start at step 1 when the sponsorship template changed;
  - the offers workbook, and the welfare and government review files;
  - `draft_employer_sponsorship.py` when variant copy changed.
- **Check:** `conformance_issues` 0, offers workbook exit 0, both runs pass. Read a few drafts of each case (A, B, C) in the workbook. Earlier copies are kept in `message_versions` under a dated label.
- **Docs:** `docs/strategy/partnership-pipelines.md` sections 4 and 5 when the rule changed, then the pipelines page; the deck's case slides (templates).

## 3. A new lead or an intake

- **Master:**
  1. `validate_intake.py`, then `preflight_update.py`.
  2. The `add_gap_census_leads.py` or `add_introducers.py` preview, then `--apply`.
  3. For the gap census, `--geocodes`, then `apply_geocodes.py --file data/raw/gap-census/geocodes_gap_census_<d>.jsonl --db master --apply`.
  4. `draft_master_messages.py` once (it creates the new organisations' plans).
  5. R+R, steps 1 to 10, rank again.
- **Map-only leads matched later:** `add_gap_census_leads.py --matches data/raw/gap-census/osm_matches_<d><round>.jsonl --apply`, before the drafter, so their map-only holds are released.
- **Welfare:** add the research file to `research_files` in `data/runs/<r>/run-config.json`. Then steps 7, 9 and 10.
- **Government:** add the files to the run config (for example `subward_units_files`). Then steps 8, 9 and 10.
- **Check:** the preflight's insert count equals the rows added; `verify_master.py` passes; the runs' organisation counts reconcile; the lead map passes.
- **Unclear:** whether the drafter must run before step 1 for new organisations. `add_introducers.py` asks for draft, refresh, then variants; `add_gap_census_leads.py` asks for draft, refresh, then rank. Running the drafter once first, then the full order, satisfies both.

## 4. A geocode or a location correction

1. Ingest the source of the points: `python scripts/research/ledger.py ingest data/raw/gap-census/google_maps_enrich_<d><round>.jsonl`. Ingest a geocode research file the same way.
2. Build a Google Maps round with `scripts/maps/build_gmaps_round.py`, which runs the shared-pin check (`docs/methodology/research-playbook.md`, "Google Maps traps") and reports every downgrade; `--audit <enrich files>` re-checks committed rounds.
3. Apply, previewing first:
   - `apply_geocodes.py --file <file>`, then the same with `--apply`;
   - for corrections, `--replace --file data/raw/geocode-research/geocodes_corrections_<...>.jsonl --apply`;
   - for a Google Maps round, `scripts/maps/apply_gmaps_status.py --round <d><tag>`, then `--apply`: the `google_maps_status` facts, the corroborations and the "Location discrepancy" review items. It changes no point, so a round with only status changes needs steps 4 to 6 only (the workbook's `google_maps` column).
   - Location precedence (13 October 2026): a website pin beats Google Maps, which beats OpenStreetMap, which beats an estimate, within the agreement distance (500 m by default); beyond it the lead is a discrepancy for the user and the orchestrator, never a correction.
4. R+R (give the recompute its own `--report` for a named round). Then steps 1 to 10.

- **Readers:**
  - the master `organisations` points feed the recompute, the rank, the drafter (a distance is stated only from a point), the lead map and the exporter;
  - the welfare `geo_overrides` and the government `ward_locations` and `office_locations` feed the runs;
  - the lead map also reads `geocodes_*.jsonl` directly, for why a lead is unplaced.
- **Check:** the recompute report; "Location corrected" and "Beyond the catchment after geolocation" review items; no lead removed; the map passes.

## 5. An employer correction, a field repair or a relation

- **Correction or repair:** `apply_employer_corrections.py --apply` or `repair_shifted_fields.py --apply`. Then rank (a hold makes tier X) and steps 1 to 10.
- **Relation:** `apply_organisation_relations.py --apply`. Then steps 1 to 10 (step 1 re-runs the recipient selection, which reads the same file) and rank again.
- **Check:** the review items each script adds; `master-recipient-selection.json` shows the collapsed pair.

## 6. A contact merge

**Master:**

```powershell
python scripts/contacts/build_contact_profiles.py --date <d>
python scripts/contacts/build_contact_workbook.py --date <d> --baseline
python scripts/master/screen_profile_people.py --apply
python scripts/contacts/merge_master_contacts.py              # read the validation and preflight reports
python scripts/contacts/merge_master_contacts.py --apply
python scripts/master/update_master_contacts.py --date <d> --apply
```

Then steps 1 to 10, rank again (named-people count and routes change the score), and `build_contact_workbook.py --date <d>`.

**Runs:** `export_run_contact_research.py`, then steps 7 and 8. They are inside the full order already.

- **Check:**
  - `outputs/contacts/master-contact-merge.json`;
  - before and after coverage (`measure_master_coverage.py --label <x>`, with `--strata-from` for the after run; `measure_welfare_coverage.py`; `measure_government_coverage.py`);
  - for a high-direct wave, `analyse_high_direct_pool.py --compare before.json after.json` and `--check`;
  - every slice ingested into the ledger before the merge.

## 7. Hook research

- **Re-run:** `apply_hook_research.py --date <d>` (preview), then `--apply`. Then rank (a staff number fills `headcount`) and steps 2 to 10.
- **Check:** `verify_master.py` `hooks_supported`, `hooks_link_to_sources` and `lead_briefs_traceable`; `outputs/messages/hook-research-apply.json`.

## 8. A recipient rule

- **Changed:** `resolve_master_recipients.py`, `data/reference/recipient-overrides.json` or `organisation-relations.json`; or, for welfare, `draft_run_messages.py` or `links.json` `recipient_exclusions` and `recipient_choices`.
- **Re-run (master):** steps 1 to 10 (step 1 runs the selection), rank again, then `build_company_audience_profile.py`.
- **Re-run (welfare):** steps 7, 9 and 10.
- **Check:** the diff of `outputs/messages/master-recipient-selection.json`; high-direct and high-indirect counts in the Resend summary; `analyse_high_direct_pool.py --check` (no risky, incomplete or board-only recipient in high-direct).

## 9. A band or segment rule

- **Where the rules live:**
  - bands and tiers: `recompute_campus_distances.py`;
  - reach scoring: `rank_employer_reach.py`;
  - the employer kind: `build_company_audience_profile.kind_of` (read by the map);
  - confidence bands: `export_resend_contacts.py` (read by the map and the analysis script);
  - a single record's segment: `data/reference/employer-corrections.json`;
  - welfare priority: `build_welfare_run.py`; government ward score and waves: `build_government_run.py`.
- **Re-run:** R+R, then steps 1 to 10. Copy a changed run script to its skill folder first.
- **Docs:** rewrite `outputs/messages/Silverleaf Catchment Criteria - <date>.md` and `Silverleaf Core Segments - <date>.md` (no script writes them); `build_company_audience_profile.py`; the deck's catchment and segment slides.
- **Unclear:** the map and the deck restate the segment names and band labels. No check ties them to the scripts.

## 10. A welfare `links.json` edit

- **Readers:** `consolidate_research.py` (`rejected_routes`, `class_overrides`, `flags_cleared`, `review_flags`, `geo_overrides`); `build_welfare_run.py` (`osm`, `master_ids`, `org_aliases`, `nis_to_org`, `nis_exclude`, `corporate_funders_in_master`); `draft_run_messages.py` (`official_personal_inboxes`, `recipient_exclusions`, `recipient_choices`).
- **Re-run:** step 7, then steps 9 and 10, and `consolidate_welfare_drafts.py`. The master does not change.
- **Check:** `verify_welfare_run.py` 23 of 23; the welfare rows of the Resend summary.

## 11. A government `links.json` edit

- **Readers:** `build_government_run.py` (`ward_aliases`, `ward_locations`, `osm_office_links`, `holder_rejects`, `holder_recheck`, `office_locations`).
- **Re-run:** step 8, then steps 9 and 10 (the government segments file), and `consolidate_government_drafts.py`.
- **Check:** `verify_government_run.py` 30 of 30.

## 12. Campus points

- **Readers:** the master `campuses` table feeds both runs (`welfare_lib.load_campuses`), the recompute, the lead map and the gap census.
- **Re-run:** update the table. Then `recompute_campus_distances.py --apply --report outputs/reports/campus-distance-recompute-<label>-<d>.json`, the rank, and steps 1 to 10.
- **Check:** no lead dropped (government `catchment_kept` holds wards that a move would push out); the map rings; the recompute report.
- **Docs:** the Catchment Criteria document, section 1; the deck's campus slide.
- **Precedent:** `ad4ca38` (11 October 2026).

## 13. The research ledger and the playbook

- **Re-run:** `ledger.py ingest <files>`, then `ledger.py check` (0 duplicates). Nothing downstream is rebuilt. The planners and `collect_geocodes.py inventory` read the ledger the next time they run.
- **Playbook:** `docs/methodology/research-playbook.md` is written by hand from `ledger.py stats`. Update its figures and its "stopped paying" list after a wave that changes them.
- **Check:** `ledger.py backfill` adds nothing (every file already ingested).

## 14. Docs and skill copies

| Pair | Rule | Check |
|---|---|---|
| `scripts/welfare/*.py` and `skills/silverleaf-welfare-leads/scripts/` | Edit `scripts/` first, then `Copy-Item scripts/welfare/*.py skills/silverleaf-welfare-leads/scripts/` | `skill_script_copies_in_sync` in step 7 |
| `scripts/government/*.py` and `skills/silverleaf-government-leads/scripts/` | The same | `skill_script_copies_in_sync` in step 8 |
| `docs/strategy/campaign-positioning-and-cadence.md`, `new-lead-acquisition-framework.md`, `offer-register.md`, `hook-guidance.md` and `skills/silverleaf-outreach/references/` files of the same name | Keep identical; edit `docs/strategy/` first and copy it over, in one commit | `python scripts/docs/check_doc_pairs.py` |
| `docs/strategy/outreach-flows.md` and `skills/silverleaf-outreach/references/flows-and-automations.md` | One document under two names; keep identical the same way | `check_doc_pairs.py` |

All the pairs were made identical on 13 October 2026. A relative link in a paired document must resolve from both folders; use a repository path in backticks otherwise. `check_doc_pairs.py` runs every pair (the welfare and government script copies too) and exits 1 on any difference.

## 15. The partnership pipelines page

```powershell
python scripts/strategy/render_markdown_page.py docs/strategy/partnership-pipelines.md "outputs/strategy/Silverleaf Partnership Pipelines.html"
```

- Re-render after any edit to `partnership-pipelines.md`.
- Open the page and confirm the Mermaid diagrams render; this needs the CDN, and offline they show their source.
- A changed decision (section 16) is mirrored where it is stated: the outreach skill and its references, `outreach-flows.md`, `new-lead-acquisition-framework.md` and the deck.
- Precedent: `cea0331`.

## 16. The strategy deck and its sources

- **Files:** `outputs/presentations/Silverleaf_Lead_Generation_Strategy_<date>.pptx`, `..._sources.md` (the queries behind every figure) and `..._slide-map.md`.
- **No script builds the deck.** To refresh it:
  1. Take read-only copies of the three databases.
  2. Re-run the queries in the sources file.
  3. Rebuild the lead map to a scratch file (`build_lead_map.py --out <scratch>`) to confirm its counts.
  4. Edit the slides.
  5. Update both side files.
- **Rules:** no person's name, email or phone on a slide; confident business tone; paths and dates only in the sources file.
- **Unclear:** which slides restate which counts is recorded only in the sources file. A rebuild does not flag a stale deck.

## 17. Email-format candidates

- **Re-run:** `email_formats.py build --write` after a contact merge (review the `data/reference/email-formats.json` diff), then steps 4 to 6 (the workbook's `email_format_to_confirm` column) and step 10 (the `-low-inferred` files). `email_formats.py candidates` writes the review list to `runtime/` only.
- **Check:** `email_formats.py check` exits 0: no generated address in any tracked file, draft route or the reference file. The high-direct check (`analyse_high_direct_pool.py --check`) finds no candidate among high rows.
