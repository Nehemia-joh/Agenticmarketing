# Silverleaf first-message hooks

Version 7 September 2026.

A hook is useful when it answers the recipient's silent question: “Why is this relevant to me or my organisation?” It should take one or two sentences. It does not need to be witty. Use one only when the exact claim has a traceable source URL and a verification date.

Use this pattern:

> Observed fact or role → practical relevance → low-effort benefit

Examples:

- Education evidence: “Africa Dream Safaris publishes its support for the School of St Jude and other local education projects. That made a practical school-information resource for your own team feel like a relevant conversation.”
- Workforce evidence: “Published information from the University of Arusha describes 150 active staff. A shared school-information option could help interested families navigate the first questions consistently.”
- Operations role, only with a current source: “Your published role in operations puts you close to the practical question: would staff find a short session or a shareable guide easier to use?”
- Finance role, only with a current source: “School choices become easier when families can see fees and payment dates clearly. Your published finance role makes that a more relevant starting point than a broad admissions pitch.”

If the claim is not independently supported, leave the active hook blank and use the no-hook first message. Generic value statements belong in the offer, not in the hook. Role and locality claims count only when the cited source confirms them. Do not manufacture a personal connection to make the line appear bespoke.

Avoid praise without relevance, personal-life details, generic references to a website, references to vehicle or bed counts as employee counts, and any implication that the recipient is a parent. Do not lead with Silverleaf's growth objective. Describe the benefit and the limited burden first: Silverleaf supplies the Q&A and written guide, parents contact the school directly, and the organisation decides only whether to share the invitation.

Use the workbook fields as follows:

- `hook_type` identifies the basis.
- `hook_quality` distinguishes specific evidence from role, locality or a baseline value statement.
- `hook_status` says whether the hook is verified or removed.
- `hook_evidence` records the source text behind the hook.
- `evidence_url` and `verified_on` show where and when the exact claim was checked.
- `hook_v2` shows the opening alone.
- `first_message_v2` shows the full alternate message.

Compare message versions at the organisation level. Do not send version 1 to one contact and version 2 to another person in the same organisation. Count one organisation once, and compare positive replies and meetings only after source and channel quality are similar across the test groups.

This database uses a verified-only rule. As of 7 September 2026, six message variants across two organisations have an active hook. The other hook fields are blank, and those messages open directly with the request (request-first, 23 September 2026).

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
