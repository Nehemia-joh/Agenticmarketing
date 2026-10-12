# New-contact acquisition framework

Version: 2026-09-09-new-contact-acquisition-v4  
Status: Design only; no sending or scheduling is active  
Scope: Organisation and business-contact leads already acquired or added later

## Strategy boundary

New-contact outreach does not inherit Silverleaf's marketing calendar, event cadence or parent broadcast plan. Those documents supply approved language, durable positioning, operational constraints and value propositions where relevant. They do not prove anything about a recipient and do not determine the acquisition sequence.

Select the outreach track from the evidence available for the lead. Use the recipient's role and organisation context to choose the ask. Use only the value propositions that help that recipient assess the proposal. A message does not need to mention every Silverleaf value pillar.

## Minimum record before outreach

Record the source, acquisition date, organisation identity, target name or route, public business contact attribution, recipient role or role uncertainty, locality or operating relevance, and last verification date. Keep source facts separate from hypotheses.

A recipient hook is optional. Use it only when the exact statement has a traceable source and verification date. An approved claim about Silverleaf is not evidence for a claim about the recipient.

## Acquisition tracks

| Track | Use when | Touchpoints | Outcome |
|---|---|---|---|
| AQ00 — Hold for verification | Identity, route, role, current operation or relevance is unresolved | No message | Research or close with a recorded reason |
| AQ01 — Routing first (updated 11 October 2026) | The only route is a general inbox (info@, admin@) and no decision-maker is named | A short redirect request, not the pitch: one line on the subject (a staff education benefit for employees' children) and the ask "Who looks after staff welfare and benefits (HR, the welfare officer or the COO)? We would like to send them a short note."; a front-desk call after 2 working days asking for that person's name and email (an email check-in after 5 working days only where no phone is published); a hand-delivered letter for the nearest P1/P2 leads; then dormant, re-tried once at the next intake window | A named owner, recorded with its source and date; the lead then moves to AQ02 |
| AQ02 — Direct recipient test | The recipient's role, route and relevance are sufficiently verified | Initial message; follow-ups after 4 and 4 working days; then stop. When the named person is reachable only through a general inbox, the message uses the Attn format (11 October 2026): the subject "Attn: <Full Name>, <Role> – staff education benefit", then a routing line set apart at the top ("For the attention of <Full Name>, <Role>. If this inbox does not reach them, we would be grateful if it could be forwarded."), then the letter as if to their own address. These case B drafts are on AQ02 (11 October 2026), and their follow-ups follow the named-person fallout: follow-up 1 gives a few offer details from the offer register, follow-up 2 is a short close with a redirect-style ask ("If this sits with someone else at <Organisation>, such as HR or the welfare officer, who should I write to? Otherwise I will close this for now."), then one message to the escalation contact, if one is recorded, 5 working days after the close (noted on the plan, not drafted). Variant A sponsorship follow-ups stay blank until approved copy exists | Earn permission for a discussion or outline |

These intervals are acquisition tests. They are independent of the school marketing calendar and should change when measured results justify a better cadence. Stop every track on any reply, referral, refusal, opt-out, hard bounce, out-of-office response or duplicate active account.

## Message construction

Build each first message as a request (decided 23 September 2026), from four parts:

1. **Purpose:** what Silverleaf would like to explore with this organisation, such as an education benefit for the children of its staff. Sponsorship is asked of welfare funders and, since 1 October 2026, of employers whose published giving funds education (variant A); never of other employers (corrected 11 October 2026).
2. **Reason:** one verified reason this recipient or route is appropriate, when one exists. If none exists, leave it out. When the owner is unknown, send the AQ01 redirect request instead of the full message, or hold the record (11 October 2026).
3. **Who is writing:** Mariam Haji, Marketing and Partnership Coordinator at Silverleaf Academy.
4. **One next action:** a short meeting, in person or by phone, or the name of the right colleague.

The first message states no offer terms. The recipient value and Silverleaf's contribution follow in the offer message: follow-up 1 on AQ02, or the reply once an AQ01 route names the right colleague. State discounts there only as the [offer register](offer-register.md) records them. Avoid inferred parenthood, workforce needs, urgency, subsidies, financing, transport, capacity or outcomes.

## Value proposition modules

Use only the modules that match the recipient and offer:

- **VM01 Staff information access:** Interested staff can opt in to receive clear, current admissions information.
- **VM02 Low partner workload:** The organisation reviews or circulates one optional invitation; Silverleaf handles parent questions directly.
- **VM03 Concrete Silverleaf contribution:** Silverleaf prepares a concise guide or optional Q&A after confirming internal capacity.
- **VM04 Parent school-fit help:** Age or grade and travel area allow admissions to check the relevant campus and current information.
- **VM05 School experience:** English-medium teaching, technology in learning, student wellness and co-curricular enrichment may support the message when relevant.
- **VM06 SACCOS information:** Offer admissions and approved fee information without implying a loan, payroll deduction, subsidy or discount.
- **VM07 Defined education collaboration:** Use only when a verified education or community remit supports a specific joint activity. Do not imply funding or endorsement.
- **VM19 Documented Silverleaf offer:** The staff school-fee benefit for employers (20% for heads of department, 10% off the first year for other staff), the family offer for everyone (free uniform for full-year payment, sibling discount, four instalments) and, for savings groups, the member-association rate. Terms come only from the offer register, which takes them from Silverleaf's discount schedule; check with Finance before the first send (12 October 2026).

## Expansion workflow

New source rows are append-only. Reuse a canonical organisation or contact when an exact domain, public email, profile URL or verified name-and-organisation match exists. Preserve every source assertion and do not overwrite a conflicting fact silently.

After each import:

1. Normalise and deduplicate the new records.
2. Verify identity, route, role and relevance.
3. Assign a segment and the smallest useful set of value modules.
4. Select AQ00, AQ01 or AQ02.
5. Draft copy from the verified facts and assigned modules.
6. Run hook, claim and duplicate-account checks before human review.

The refresh process applies these rules to every outreach-plan row, including rows added after this version. It does not send messages.

## Measurement

Track results by acquisition track, segment, value-module combination and message version. Use delivered organisations as the denominator for replies and meetings. Record referrals, positive replies, meetings, staff sessions, parent opt-ins, visits, applications and enrolments separately. Compare one substantive change at a time.

## Source use

- Brand guidelines, brochure and official pages: approved Silverleaf wording and durable school value pillars.
- Event SOP and marketing calendar: event or broadcast work only; not the default cadence for newly acquired contacts.
- Video-derived outreach principles: concise relevance, recipient-centred value, one clear ask, limited follow-up and response-based stopping.
- Recipient research: the only basis for a personalised assertion about the recipient or organisation.
