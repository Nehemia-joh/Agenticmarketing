# Silverleaf offer register

Version: 2026-10-12-offer-v5
Machine-readable copy: `data/reference/silverleaf-offer-register.json`. The message scripts in `scripts/messaging/` read it, and verification checks every percentage and amount in a message against it.

## Status

The terms come from two Silverleaf documents in `references/Offers & Discounts/`:
- the discount schedule, *2025 Proposed Fees & Discounts* ("Summary of discounts offered")
- the 2025 Rivertrees proposal

**Updated 12 October 2026.** The user confirmed that the offer terms come from the discount schedule, and the terms below match it. The earlier condition, that Finance confirm each term for the 2027 school year before any message stating it is sent, was removed that day. Every offer-stating draft now carries a note instead: *"Offer terms are taken from Silverleaf's discount schedule (2025 Proposed Fees & Discounts). Check with Finance before the first send."* The note never holds a draft or changes its review status. First messages state no terms.

Conditions that still stand:
- OF07 is documented for KINEFA only; Finance must agree to extend it to any other savings group.
- OF03 applies only when a home places all its primary-age children.
- Expired offers stay expired: the referral package (OF05) applied to enrolments before 30 November 2024.

## Terms

| ID | Offer | Who it is for | Terms | Use in messages |
|---|---|---|---|---|
| OF01 | Free uniform for full-year payment | Every family | A full uniform set, worth TZS 110,000, free when the year's tuition is paid before the school year opens. It cannot be used to pay tuition. | Yes |
| OF02 | Sibling discount | Parents of biological siblings | 10% off tuition for a third child and 20% for a fourth, for as long as they study at Silverleaf. None for the first two children. | Yes |
| OF03 | NGO partner discount | Orphanages and children's homes that place all their primary-age children | Per child: 3% for 10 children, 6% for 20, 9% for 30, 12% for 40, 15% for 50, 18% for 60 | Welfare only |
| OF04 | Institutional staff discount | Staff of organisations and government bodies | 20% for heads of department, for as long as the child studies at Silverleaf; 10% off the first year for all other staff | Employers only; never in a convening letter to officials |
| OF05 | Referral uniform package | Referred students, 2025 intake | TZS 30,000 package for enrolment before 30 November 2024 | **No.** Expired; the 2027 referral scheme is under review (task A8). |
| OF06 | ECD owner facilitation | Owners or managers of early-childhood centres | TZS 50,000 per Daycare or Pre-Primary student enrolled in January | Only for ECD-centre leads (none in the current lists) |
| OF07 | Member association rate | KINEFA members | 7% per student at 50 students, 12% at 100, 17% at 150 | Savings groups, as a group rate Finance must agree to extend |
| OF08 | Corporate Education Benefit Partnership | Rivertrees employees | 40% off tuition; admission fee (TZS 50,000) waived; monthly or quarterly instalments; facilities, parent events, priority enrolment subject to availability | Rivertrees only. For other employers it is the model for the proposal after a meeting. |
| OF09 | Four-instalment tuition | Every family | Tuition is paid in four instalments across the year | Yes |

## Published facts used alongside the terms

Checked on the admissions page on 23 September 2026:
- **Levels:** Daycare (from 1.5 years), Pre-Primary KG1–KG2 and Primary Grade 1–7.
- **Language:** English-medium teaching.
- **Applications:** open for the 2027 school year.
- **Enrolment windows:** Daycare and Pre-Primary at any time; Primary from October to December for a January start.
- **Campuses:**
  - Primary to Grade 7: Usa River (with boarding) and Arusha City.
  - Daycare and Pre-Primary: Kijenge, Ilboru and Boma Ng'ombe.
- **Fees:** the page lists them (Daycare TZS 1,600,000, Pre-Primary 1,800,000, Primary 1,850,000 a year) but not the school year they apply to.

## Rules

1. **State terms exactly as recorded,** with their condition: all primary-age children for OF03, payment before the school year opens for OF01.
2. **No offer terms in first messages.** The first message to an organisation is a request; the terms appear from the offer message on. Tuition figures are sent on request, never in a first message; offer the current fee schedule instead.
3. **No referral rewards** of any kind until a 2027 scheme is approved.
4. **OF08's 40% is for Rivertrees only.** OF07's group rate needs Finance to extend it.
5. **Government convening letters** state no offer, fee or service (changed 1 October 2026: they read as too salesy); they describe a free talk and a parent booklet, and never offer officials or their staff a discount. A personal benefit to officials whose cooperation Silverleaf seeks could look like an inducement.
6. **No offer guarantees** a place, transport route or capacity.
7. **Record the offer IDs of every message** and the offer-terms note (terms from the discount schedule; check with Finance before the first send). The note is not a hold.

## How messages use the offer

Request first (decided 23 September 2026, on Kilusu's recommendation). The first message to an organisation makes a relevant request and states no offer terms. It gives its purpose, who is writing and asks for a short meeting, in person or by phone. The offer message states the terms. What Silverleaf offers comes second: it answers a reply or follows up, and never opens the conversation.

**Promotional incentives (rule added 11 October 2026, approved by the user).** The partnership offer and a promotional incentive are different things:
- **The partnership offer** is the terms above (OF04 staff discount, OF03 partner rate, OF07 member rate once extended, OF01, OF02, OF09). It is stated plainly once the conversation is open.
- **A promotional incentive** is anything extra used to tip a decision, such as discounted first months. It is not an offer in this register, and the rule adds none.
- A promotional incentive never appears in any automated or standard flow, nor in a cold or early message, because it makes Silverleaf look desperate.
- It may be used only at the proposal stage, for a specific employer that has already engaged, with Finance's written approval each time. It is time-limited, and only in terms this register records: it is entered here, with its approval and expiry, before any proposal states it.
- It is never offered to a public body or a government office.

See [partnership-pipelines.md](../../../docs/strategy/partnership-pipelines.md), section 6.

**Sender:** Mariam Haji, Marketing and Partnership Coordinator, signs every draft in all three databases. The Kiswahili title (Mratibu wa Masoko na Ushirikiano) is a draft translation for native-speaker review.

**Sponsorship** is asked of welfare funders and, since 1 October 2026, of employers whose published giving funds education (strong fit; variant A). Every other employer gets variant B. `scripts/master/assign_message_variants.py` records the variant. The reason is one sourced fact from `data/reference/employer-sponsorship-reasons.json`, and the drafts come from `scripts/messaging/draft_employer_sponsorship.py`. No other employer is asked for sponsorship.

| Audience | First message (request, no terms) | Offer message | Later |
|---|---|---|---|
| Employer (AQ02) | A partnership to provide an education benefit for the children of its staff, and a short meeting | Follow-up 1: the staff school-fee benefit at no cost to the employer (OF04), the family offer (OF01, OF02, OF09), levels and campuses; the employer can present the benefit as its own or add to it | A close after 4 more working days; for a named person behind a general inbox (Attn format) the close asks who else to write to, such as HR or the welfare officer (11 October 2026) |
| Employer (AQ01 routing; updated 11 October 2026) | No person named: a short redirect request asking who looks after staff welfare and benefits (HR, the welfare officer or the COO); no pitch, no terms. A named person behind a general inbox gets the AQ02 message in the Attn format | The reply once someone names the right colleague | A front-desk call after 2 working days asking for that person's name and email; a hand-delivered letter for the nearest P1/P2 leads; then dormant until the next intake window |
| Savings group | A meeting with the committee about members' children's education; a Kiswahili version for review | The family offer and the member-association rate (OF07) | One check-in, or a close |
| Welfare home or programme | A partnership on the education of the children in its care, and a short meeting | Follow-up: the partner rate (OF03), the free uniform and instalments; admissions checks each child's level | For a named leader behind a general inbox (Attn format), a close asking who else to write to, such as the head of the home or programme (11 October 2026); otherwise none |
| Employer that funds education (variant A) | Sponsorship of students, any size including textbooks, transport or meals, with its own published education giving as the reason (no offer terms) | None until it replies | None |
| Every other employer (variant B, the catch-all) | A partnership on an education benefit for the children of staff, with its published giving as the reason where there is one (no offer terms) | The staff school-fee benefit (OF04) and the family offer, as above | A close after 4 more working days |
| Welfare funder | Sponsorship of students, any size including textbooks, transport or meals, with its verified support for a home as the reason; held when the run has no verified reason | Follow-up: the partner rate as a way to stretch sponsorship | For a named contact behind a general inbox (Attn format), a close asking for the programme officer for Tanzania (11 October 2026); otherwise none |
| Council (GA01) | Already a request: a free Kiswahili school-readiness talk at community meetings, plus a parent booklet; no offer, fee or service is stated | None | A written follow-up after 5 working days |
| Ward, village, district, region | The same talk and booklet; held until the council introduction | None | None |
| Parent enquiry | A reply, not outreach: levels, campuses and the family offer; ask for age or grade and area | None | None (one reply at most) |
