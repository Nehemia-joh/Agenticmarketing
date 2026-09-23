---
name: silverleaf-outreach
description: Develop Silverleaf partnership outreach strategy and personalize email or direct-message drafts from its lead intelligence, with traceable evidence, role-specific offers, and sequence planning. Use for Silverleaf outreach copy, message reviews, or campaign briefs.
---

# Silverleaf outreach strategy and copy

Produce a defensible reason for contacting each recipient, an appropriate partnership proposal and a concise draft. For Silverleaf positioning, parent language, factual claim gates, broadcasts and event cadence, read [campaign-positioning-and-cadence.md](references/campaign-positioning-and-cadence.md). Read [video-principles.md](references/video-principles.md) for the source principles and disagreements. Apply the Silverleaf decisions below as local working defaults, not as claims that the videos prove them.

For the offer a message may state, read [offer-register.md](references/offer-register.md): every discount and term comes from it, with its source, and verification checks each percentage and amount. For newly acquired organisation and business-contact leads, also read [new-lead-acquisition-framework.md](references/new-lead-acquisition-framework.md). Treat marketing documents as a Silverleaf positioning and value-proposition library where applicable. Do not make new contacts inherit the internal marketing calendar, event cadence or parent broadcast plan.

## Establish the assignment

Distinguish strategy design, sample drafting and a full message rewrite. Complete the requested stage. Preparing this skill or reviewing sample messages does not authorize replacing all database drafts or sending outreach.

For database work, read [database-workflow.md](references/database-workflow.md). Reuse entity IDs. Check the source behind a displayed value before using it as a personalized assertion.

Checking hooks and routes uses web budget. Re-open the cited source URL with WebFetch rather than searching again. For large batches, spread the checks and respect the shared per-session web-search cap and site blocks described in [research-rate-limits.md](../silverleaf-create-lead-list/references/research-rate-limits.md).

## Make the strategy concrete

Before drafting, record:

- Recipient and organisation IDs, current role, contact channel and channel attribution.
- Audience: employer decision-maker, staff-welfare introducer, savings-group committee, education collaborator, or adult with a current school enquiry.
- Evidence: the specific observation, source URL, published date if available, verification date and unresolved uncertainty.
- Proposed outcome for this recipient, Silverleaf's contribution, the recipient's requested contribution and one next action.

Do not turn all records into parent prospects. Historical enquiries need fresh qualification; secondary-school requests and teaching applicants need their own treatment. Organisation size, a staff biography or a social post does not establish that a person is a parent.

Use this local role map as a starting hypothesis, then adjust to evidence:

| Recipient | Partnership focus | Initial ask |
|---|---|---|
| HR / staff welfare | An organised way for staff to ask admissions questions | Discuss one voluntary staff information session |
| Owner / executive | Sponsor a manageable workplace education pilot | Nominate the staff-welfare owner |
| Operations | Schedule around verified work patterns | Identify a practical session window |
| Finance / SACCOS committee | Clear fee information and payment planning | Review the published schedule with the relevant coordinator |
| CSR / education lead | An evidenced education programme or shared objective | Explore one specific collaboration |

The partner circulates an invitation; interested parents contact Silverleaf directly. State discounts only as the offer register records them, with the condition that Finance confirms them for 2027 before sending. Treat payroll deductions, transport arrangements and employer subsidies as proposals requiring agreement. Confirm grade availability and campus fit. Do not promise retention gains, reduced absence or enrolment outcomes without evidence.

## Draft and personalize

Use the source principles in the reference. For Silverleaf, normally aim for 50–100 words in the initial email, excluding signature. Adjust when the channel or request needs it. Use a plain subject that accurately names the purpose.

**Request first.** The first message to an organisation makes a relevant request and states no offer terms. It covers:
- **Purpose:** an education benefit for the children of its staff; a meeting with a savings-group committee; working together on the education of the children in a home's care; or, for welfare funders only, sponsorship.
- **Who is writing:** Mariam Haji, Marketing and Partnership Coordinator, the sender for all three databases.
- **One ask:** a short meeting, in person or by phone, or the name of the right colleague.

What Silverleaf offers comes in the next message, as the offer register's table sets out. Never ask an employer for sponsorship.

Personalization must change the reason, offer or next action—not merely the salutation. If a relevant organisation fact is verified but the recipient's role is uncertain, draft a routing request. If evidence is insufficient, mark `Needs research` and identify the missing fact rather than manufacture a personalized claim.

For an alternate first message with a recipient-centred opening, read [hook-guidance.md](references/hook-guidance.md). Use a hook only when its exact claim has a traceable source URL and a verification date. A current role or local connection qualifies only when the cited source supports it. If that evidence is missing, leave the hook blank and open directly with the request. Keep unverified ideas out of the active message and preserve earlier drafts in version history or a backup.

Keep strategic hypotheses separate from facts: a hospital may operate shifts, but that does not prove this recipient's staff need daycare. Existing school donations may justify a conversation, but do not establish endorsement of Silverleaf. Never imply a prior conversation, existing account relationship or referral that did not happen.

No invented sender identity, testimonial, statistics, familiarity, urgency or calendar availability. Omit optional proof when none is verified. Retain research citations in the review record; include them naturally in the message only when useful to the recipient.

## Regenerate the drafts

The scripts in `scripts/messaging/` draft every lead's messages: the request first, then the offer from the offer register.
- `draft_master_messages.py`: company master. The offer is in `offer_message`, and AQ02 also sends it as follow-up 1. Earlier versions are saved in `message_versions` first; use `--dry-run` to preview.
- `draft_run_messages.py --track welfare|government`: a pipeline step in each separate run.
- `build_offer_messages_workbook.py`: one review workbook for all three databases. It fails if any draft breaks a register rule, or if a first message states offer terms.

Edit the register (`data/reference/silverleaf-offer-register.json` and this reference) when Finance approves new terms, then re-run them.

## Sequence and response decisions

Choose cadence by audience state. Newly acquired organisation and business-contact leads use AQ00, AQ01 or AQ02 from the acquisition framework. AQ01 uses one routing request and one check-in after five working days. AQ02 uses Day 0, +4 working days and +4 working days as an independent test. These tracks do not inherit the internal marketing calendar. Fresh opted-in parent enquiries use the shorter service flow; historical public enquiries receive at most one reviewed reply. Event production begins at T-21 only for a confirmed event, while direct reminders require an RSVP or explicit opt-in. Treat every schedule as design-only until an owner activates an approved campaign. Stop on any reply, refusal, opt-out, referral, hard bounce, out-of-office response, application or enrolment as applicable.

For worked sequences, response branches, SACCOS outreach, partner invitations and parent qualification, read [flows-and-automations.md](references/flows-and-automations.md). Use the organisation segment to choose the offer and the recipient's role to choose the ask. Personalize the evidence and relevance within that structure. Distinguish automation recipes from activated delivery integrations.

A named draft may be forwarded through a company channel. Keep the intended recipient and forwarding instructions explicit; do not label a generic inbox as a personal address just because an imported row calls it a role email. Select one draft per resolved organisation; keep other named recipients and source variants as alternatives.

Use a meeting request for a verified decision-maker with a concrete proposal. Use a referral request for an uncertain owner. Use an information offer when the recipient wants details before a meeting. Do not repeat the identical ask after they explain why it does not fit.

## Deliver and check

Return the strategy brief, draft(s), evidence record and any unresolved research. Read [examples.md](references/examples.md) when a distinction needs illustration.

Check whether each message has a relevant reason, accurate contact attribution, feasible offer and one answerable next step. Remove unsupported claims. Flag unresolved entity overlaps before outreach. For batch work, reconcile every requested message ID as rewritten, intentionally unchanged or needing research; preserve earlier versions.

Measure unique organisations reached, positive replies, meetings held, staff sessions, opted-in parent enquiries, visits and enrolments. Keep negative replies and automatic replies separate. Compare one substantive hypothesis at a time and report denominators and small-sample uncertainty. No delivery or sales benchmark in the videos is a Silverleaf forecast.
