# First-message hooks

A hook answers the recipient's silent question: “Why is this relevant to me or my organisation?” Use one or two sentences built as:

> Observed fact or role → practical relevance → low-effort benefit

An active hook must have both a traceable source URL and a verification date. Prefer the strongest verified basis:

1. A specific education programme, workforce fact or team structure with a cited source.
2. The recipient's current role and the decision they can reasonably make, when a current source confirms that role.
3. Verified local relevance, subject to actual grade and travel fit.

Label the basis, quality, evidence, source URL and verification date. If the exact claim is not independently supported, leave the active hook blank and use a no-hook first message. Generic value statements belong in the offer; they are not research-backed hooks. Do not manufacture a personal connection, praise without relevance, infer that the recipient is a parent, or turn vehicle, bed or customer counts into employee counts.

Put the benefit before the mechanics. For Silverleaf, the partner decides whether to share one invitation; Silverleaf supplies the Q&A and written guide, and interested parents contact admissions directly.

Adjust the closing request to the recipient:

- Executive: ask where the proposal belongs or who owns staff welfare.
- Operations: ask whether a short session or written guide is easier.
- Finance: offer a clear fee and payment-date outline.
- Administration or HR: offer the outline before requesting a planning call.
- Community or CSR: keep the staff resource separate from external programmes.
- Unknown role: ask where to send the one-page outline.
- SACCOS committee: offer the member-information outline without assuming credit, subsidy or payroll arrangements.

When comparing two first-message versions, assign one version per resolved organisation. Do not send different variants to multiple contacts at the same organisation. Compare positive replies and meetings only after source and channel quality are similar across the groups.

For batch work, treat role-led, locality-led and value-led opening ideas as research candidates until their exact claims are verified. No hook is preferable to an inaccurate one.

## Research waves and lead briefs

Hooks for a batch of leads are researched in waves. Each lead's facts are kept as a brief, so a person can learn about the lead quickly if they reply.

1. **Plan.** `python scripts/messaging/plan_hook_research.py --date <date> --track AQ02 --budget <searches>` groups the track's plans by organisation. It writes one slice and one agent prompt per research agent under `runtime/hooks/`: at most four agents, with 10% of the searches held back.
2. **Research.** Each agent reads pages with `python scripts/contacts/read_page.py <url>`, which caches pages, spaces requests to a site 1.5 s apart, honours robots.txt Disallow and reports blocks. It writes `data/raw/hook-research/hooks_<slice>_<date>.jsonl` and a coverage log. For each organisation it records:
   - a role check for each named contact, on the page the contact came from;
   - a lead brief: up to five published facts, each with its source URL, page title, page date, a verbatim excerpt and the date it was read;
   - at most one hook sentence, in the second person and supported entirely by one of those facts, or none.
3. **Merge.** `python scripts/messaging/apply_hook_research.py --date <date>` previews the merge, and `--apply` runs it in one transaction:
   - the source files and records;
   - the `lead_briefs` table;
   - verified hooks on every plan for the organisation;
   - review items. A changed or missing role holds that contact's drafts.

   Then run `draft_master_messages.py`, `refresh_acquisition_metadata.py`, `npm run build:workbook` and `verify_master.py`.

The master workbook's Lead Briefs sheet lists every fact with a clickable source link. The Messages sheet shows each draft's brief and hook source beside the copy. `verify_master.py` fails if a verified hook has no source link, or a brief fact lacks its link, excerpt or research record.
