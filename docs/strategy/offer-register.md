# Silverleaf offer register

Version: 2026-10-13-offer-v6
Machine-readable copy: `data/reference/silverleaf-offer-register.json`. The message scripts in `scripts/messaging/` read it, and verification checks every percentage and amount in a message against it.

## Status

The terms come from two Silverleaf documents in `references/Offers & Discounts/`:
- the discount schedule, *2025 Proposed Fees & Discounts* ("Summary of discounts offered")
- the 2025 Rivertrees proposal

**Updated 12 October 2026.** The user confirmed that the offer terms come from the discount schedule, and the terms below match it. The earlier condition, that Finance confirm each term for the 2027 school year before any message stating it is sent, was removed that day. Every offer-stating draft now carries a note instead: *"Offer terms are taken from Silverleaf's discount schedule (2025 Proposed Fees & Discounts). Check with Finance before the first send."* The note never holds a draft or changes its review status. First messages state no terms.

**Updated 13 October 2026.** OF07 is the group rate for savings groups. The discount schedule's row named one association ("KINEFA discount"); the user decided to keep the rate and apply it to savings groups generally: SACCOS and community savings groups (VICOBAs). It no longer needs Finance to extend it. The thresholds and percentages are the schedule's own, and messages never name the association.

Conditions that still stand:
- OF07 counts primary-age students from one group's members and starts at 50 students; there is no pooling across groups.
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
| OF07 | Group rate for savings groups | Members of a SACCOS or a community savings group (VICOBA) who send their primary-age children | Per primary-age student from one group's members: 7% once 50 students join, 12% at 100, 17% at 150 | Savings groups only, from the offer message on (13 October 2026) |
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
4. **OF08's 40% is for Rivertrees only.** OF07's group rate is for savings groups only (SACCOS and VICOBAs), counted from one group's members.
5. **Government convening letters** state no offer, fee or service (changed 1 October 2026: they read as too salesy); they describe a free talk and a parent booklet, and never offer officials or their staff a discount. A personal benefit to officials whose cooperation Silverleaf seeks could look like an inducement.
6. **No offer guarantees** a place, transport route or capacity.
7. **Record the offer IDs of every message** and the offer-terms note (terms from the discount schedule; check with Finance before the first send). The note is not a hold.

## How messages use the offer

Request first (decided 23 September 2026, on Kilusu's recommendation). The first message to an organisation makes a relevant request and states no offer terms. It gives its purpose, who is writing and asks for a short meeting, in person or by phone. The offer message states the terms. What Silverleaf offers comes second: it answers a reply or follows up, and never opens the conversation.

**Sender:** Mariam Haji, Marketing and Partnership Coordinator, signs every draft in all three databases. The Kiswahili title (Mratibu wa Masoko na Ushirikiano) is a draft translation for native-speaker review.

**Sponsorship** is asked of welfare funders only, never of employers.

| Audience | First message (request, no terms) | Offer message | Later |
|---|---|---|---|
| Employer (AQ02) | A partnership to provide an education benefit for the children of its staff, and a short meeting | Follow-up 1: the staff school-fee benefit at no cost to the employer (OF04), the family offer (OF01, OF02, OF09), levels and campuses; the employer can present the benefit as its own or add to it | A close after 4 more working days |
| Employer (AQ01 routing) | The same partnership request | The reply once someone names the right colleague | Second touch after 5 working days: who is best to speak to about staff welfare or benefits |
| Savings group | A meeting with the committee about members' children's education; a Kiswahili version for review | The family offer and the group rate for savings groups (OF07) | One check-in, or a close |
| Welfare home or programme | A partnership on the education of the children in its care, and a short meeting | Follow-up: the partner rate (OF03), the free uniform and instalments; admissions checks each child's level | None |
| Welfare funder | Sponsorship of students, any size including textbooks, transport or meals, with its verified support for a home as the reason; held when the run has no verified reason | Follow-up: the partner rate as a way to stretch sponsorship | None |
| Council (GA01) | Already a request: a free Kiswahili school-readiness talk at community meetings, plus a parent booklet; no offer, fee or service is stated | None | A written follow-up after 5 working days |
| Ward, village, district, region | The same talk and booklet; held until the council introduction | None | None |
| Parent enquiry | A reply, not outreach: levels, campuses and the family offer; ask for age or grade and area | None | None (one reply at most) |
