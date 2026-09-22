# Work with Silverleaf's master intelligence

Default project: the repository containing this skill unless the user supplies another location.

Default database: `outputs/master/Silverleaf Master Database.sqlite` beneath that project. The filterable snapshot is `Silverleaf Master Database - Consolidated.xlsx` in the same directory. Discover the files if these locations have changed; do not assume another similarly named workbook is current.

Read the database schema before querying. Relevant tables:

- `organisations`: display fields, priority, proposed strategy and entity ID.
- `contacts`: organisation ID, role and separately attributed contact channels.
- `enquiries`: request type, source, date, locality and current relevance.
- `messages`: target type/ID, original body, subject, source and strategy.
- `facts`: alternate field assertions linked to `source_records`.
- `source_records` and `source_files`: original provenance.
- `review`: unresolved source differences or possible branch overlaps.

The first nonblank displayed field was chosen by source precedence, not by universal verification. Before claiming a current role, programme, event or contact route, check the supporting source. Do not infer current urgency from an undated education programme.

For a rewrite, preserve `message_id` and `target_id` in the output. Keep original text recoverable. The working record should contain:

`message_id`, `target_id`, `target_type`, `strategy_version`, `segment`, `recipient_role`, `evidence_url`, `evidence_date`, `verified_on`, `relevance_reason`, `proposed_offer`, `cta_type`, `subject`, `body`, `follow_up_1`, `follow_up_2`, `review_status`, `missing_information`.

Those are proposed output fields, not a claim that these columns already exist. Only add or migrate tables when database modification is within the user's requested stage. Do not rerun the old consolidation script after editing messages: it rebuilds from earlier source files and can discard later changes.

The 6 September 2026 rewrite added `outreach_plans` (927 revised draft plans and follow-ups), `outreach_segments`, `outreach_flows`, and `message_versions` (original message JSON). The `messages` table now contains the revised initial drafts. `outreach_plans.selection` identifies one proposed review candidate per organisation; it is not send approval. Check the current schema rather than assuming later migrations are identical.

The master workbook includes Outreach plans, Sequences, Segments and Flows. `docs/strategy/outreach-flows.md` holds the worked examples; `outputs/config/automation-recipes.json` contains disabled implementation recipes. The deterministic scripts under `scripts/master/` export, rebuild and verify the review workbook. No external campaign is active. Preserve these current records when exporting a new snapshot.

For strategy-only work, leave the 927 source drafts untouched. For full personalization, each requested ID must have a recorded outcome, including drafts held for missing evidence. Distinct messages targeting the same person are alternatives, not permission to contact them multiple times.

The 23 September 2026 offer rewrite (`scripts/messaging/draft_master_messages.py`, offer v4):
- Every outreach plan now states the documented offer. Earlier plan and message rows are in `message_versions` under `2026-09-23-before-offer-v4`, and earlier parent replies are in `parent_enquiry_draft_versions`.
- It added 387 plans for organisations that had none, as AQ01 when a public route exists and AQ00 otherwise. Local administration offices are in the government run, child-welfare organisations are in the welfare run, and excluded offices get none.
- `outreach_plans` gained `offer_version`, `offer_ids`, `offer_evidence` and `offer_message_sw`.
- Value module VM19, positioning evidence PE025–PE028, strategy `S-offer-aligned-v4` and the segments 'Corporate employers' and 'Public-sector employers' were added. `refresh_acquisition_metadata.py` keeps VM19 on offer-v4 plans.
- The consolidated workbook must be rebuilt with `npm run build:workbook` where `@oai/artifact-tool` is available. Until then, review the drafts in `outputs/messages/Silverleaf Offer-Aligned Messages - <date>.xlsx`.
