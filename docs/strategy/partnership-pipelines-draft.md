# Partnership pipelines: draft for review

Version: 2026-10-11 draft 1 (phase 1, for the user's review)
Status: **Design only.** Nothing here is built, no database has changed, and nothing is sent. Sending and automations stay disabled.
Scope: every core segment and subsegment in [Silverleaf Core Segments - 2026-10-11](../../outputs/messages/Silverleaf%20Core%20Segments%20-%202026-10-11.md): employers (with savings groups), introducers, welfare organisations and government offices.

## What this document is

Silverleaf writes to four kinds of organisation. Each needs a pipeline: the stages a deal moves through from "ready to contact" to "partnership closed" and then to families enrolling. This draft proposes those pipelines, one per segment, with the variations each subsegment needs, so the user can review them before anything is built.

For each pipeline it sets out:
- what counts as a win;
- the stages, with who acts and the asset used;
- how staff, members or parents opt in;
- what is recorded;
- timing and when a stalled deal is re-prompted or closed;
- the hand-off to admissions;
- the numbers to watch.

Section 12 lists the conflicts found in the existing strategy documents. Section 13 lists the open questions, each with a recommended answer. Section 14 says what would be built after approval.

**Counts.** All counts come from read-only copies of the three databases, taken on the evening of 11 October 2026: the master, the welfare run `arusha-welfare-2026-09` and the government run `arusha-government-2026-09`. They are larger than the Core Segments document, which was written that morning before the day's new leads were added (companies rose from 716 to 1,118; government offices from 150 to 230). Confidence bands are computed with the rules in `scripts/messaging/export_resend_contacts.py`, before shared inboxes are collapsed, so they can differ by a few from the Resend files.

---

## 1. Overview on one page

"Ready" means a draft is ready for review with a usable route today. The stage path leaves out the "Closed, lost" exit, which every stage has.

| Segment | Subsegment | Organisations (ready) | Stage path | Partnership closed when |
|---|---|---|---|---|
| **Employers** | Safari operators and travel agencies | 480 (432) | Ready → Contacted → Responded → Call or meeting → Office visit, cluster session or webinar → Partner → Staff nurture | The employer circulates Silverleaf's sign-up invitation to staff, or signs a staff-benefit agreement |
| | Hotels, lodges and camps | 194 (123) | Same, with the session timed to shift handover (two short slots) | Same |
| | Hospitals and clinics | 188 (37) | Hospitals: same, with a staff-room session or recorded webinar. Small clinics: pamphlet pack, no session | Same |
| | Banks and other companies | 87 (70) | Same; an agreement may come before the session | Same; usually a signed benefit agreement |
| | NGOs and research bodies | 62 (28) | Same, local staff only | Same |
| | Colleges and universities | 23 (19) | Same, through staff welfare or HR, away from exam periods | Same |
| | Public bodies (HR route) | 19 (12) | **Compliance check** → Ready → … → Call or meeting with HR → **HR approval** → Session → Partner | An HR circular to staff, or a signed agreement through HR |
| | International organisations | 10 (9) | Same, usually through the staff association or welfare committee | The staff association circulates, or the organisation signs |
| | Manufacturing | 19 (11) | Same, with a canteen session at shift change, in Kiswahili | Same |
| | Retail | 17 (6) | Same, with a store huddle; head-office approval for chains | Same |
| | Farms and estates | 14 (3) | Same, with an on-site session through the welfare officer, in Kiswahili | Same |
| | Aviation | 5 (2) | Same, with a webinar or an off-site session (secure sites) | Same |
| | Variant A: sponsorship (all safari operators so far) | 14 | Ready → Contacted → Responded → Meeting → Sponsorship proposal → Sponsorship agreement → Sponsored students enrolled | A signed sponsorship agreement (any size) |
| | Savings groups (SACCOS), in Kiswahili | 117 (1): 48 employer-based, 67 community, 2 unclassified | Ready → Contacted (letter or call) → Responded → Committee meeting → Members' meeting or AGM slot → Partner → Member nurture | The committee circulates the sign-up invitation to members or gives a meeting slot; optionally a group rate agreed by Finance |
| **Introducers** | Chambers (3), employers' associations (5), sector associations (6), HR body (1), other (1) | 16 (16) | Ready → Contacted → Responded → Meeting → Circulation agreed → Circulated → Employer referrals | At least one circulation to members: a newsletter item, a members' meeting slot or an HR forum. Its results are employer leads, not parents |
| **Welfare** | Residential care (children's homes) | 100 (17) | Ready → Contacted → Responded → Placement conversation → Safeguarding visit → Proposal → Placement agreement → Children enrolled → Renewal | A signed placement agreement on approved terms |
| | Family-based and sponsorship programmes | 164 (25) | Same; or the programme circulates information to caregivers, who opt in | A placement agreement, or the programme agrees to circulate |
| | Specialised centres | 70 (5) | Same, with a **needs-fit check** before the visit | A placement agreement for the needs Silverleaf can support |
| | Funders | 104 (34) | Ready → Contacted → Responded → Meeting (often remote) → Sponsorship proposal tied to a linked home → Sponsorship agreement → Students enrolled → Reporting and renewal | A signed sponsorship agreement |
| | Welfare networks (introducers) | 7 (5) | Ready → Contacted → Responded → Meeting → Circulated to member homes → Home referrals | At least one circulation to member homes |
| **Government** | Pilot councils (Arusha City, Arusha District, Hai, Meru) | 4 (4) | Letter by hand → Call after 5 working days → Courtesy visit → Introduction recorded | The council introduces Silverleaf to its ward and village executive officers |
| | Other councils | 5 (0) | Same, after the pilot | Same |
| | District and regional offices | 7 + 3 (0) | Courtesy notice → Acknowledged | Informed. No request is made, so there is no win beyond that |
| | Ward offices | 129 (0; 57 within 10 km) | Introduction → Convening request → Slot agreed → Community meeting held → Parent opt-ins → Repeat convener | A community meeting is held at which Silverleaf speaks to parents |
| | Village offices | 82 (0; 31 within 10 km) | Same, at the village assembly | Same |
| | Mtaa offices (city streets) | 0 recorded | Same, at the mtaa meeting | Same (a gap: none are in the run yet) |

Across all segments the results are counted the same way: opted-in families moving from Inquiry to Tour, Application and Enrolment, each linked to the partner that produced it.

---

## 2. Rules that apply to every pipeline

1. **Staff, members and parents opt in themselves.** The partner circulates Silverleaf's invitation, pamphlet, QR code or sign-up form. Only people who sign up are contacted. Silverleaf never asks for, and never accepts, a list of staff, members, residents or children. This follows Tanzania's Personal Data Protection Act 2022, which requires explicit consent for direct marketing. It also matches the existing design: VM01, F04 steps 2–3, and the government plan's VM16.
2. **Request first.** The first message asks for a short meeting and states no offer terms. Terms follow in the next message, or in the meeting ([offer register](../../skills/silverleaf-outreach/references/offer-register.md), rule 2).
3. **Offer terms come only from the register** (`data/reference/silverleaf-offer-register.json`). Finance confirms each term for 2027 before it is stated. Nothing in this document adds or changes a term.
4. **The recipient rule.** The first message goes to the in-country person who can decide. A senior executive is the escalation contact, used only after silence, a refusal or a referral to head office.
5. **One active sequence per organisation** (F02 step 4). A referral moves the same deal to the new person. It does not start a second deal.
6. **Results go back to partners as totals only.** Silverleaf never reports which person signed up or enrolled. Small numbers are hidden, so a small employer cannot work out who enrolled (see question 13).
7. **Parent data never enters the repository or the three lead databases.** It lives in a consented parent store owned by admissions. The databases hold counts by partner code only.
8. **Kiswahili for parents, members and government.** Every Kiswahili asset has a native-speaker review before use.
9. **People send; the repository drafts.** Every stage change is recorded by a person after it happens.

---

## 3. The shared stage spine

Each segment has its own stage names, because a council introduction is not a staff session. All of them map onto one shared spine, so the reports add up across segments. The spine also maps onto the six partner stages in Silverleaf's own Process Map (Prospect, Contacted, Engaged, Negotiating, Active, Producing Results).

| Spine stage | Meaning | Process Map stage | Employers | SACCOS | Introducers | Welfare homes | Funders | Government |
|---|---|---|---|---|---|---|---|---|
| 0 Held | Not yet contactable: research, checks or a hold | (before Prospect) | AQ00 | AQ00 | AQ00 | WA00 | WA00 | GA00 |
| 1 Ready | Draft reviewed, route chosen | Prospect | Ready | Ready | Ready | Ready | Ready | Letter ready |
| 2 Contacted | First touch delivered | Contacted | Contacted | Contacted | Contacted | Contacted | Contacted | Letter delivered |
| 3 Responded | A human reply | Engaged | Responded | Responded | Responded | Responded | Responded | Acknowledged |
| 4 Meeting | Call or meeting booked or held | Engaged | Call or meeting | Committee meeting | Meeting | Placement conversation | Meeting | Courtesy visit |
| 5 Activation | The step that reaches the audience, or proves fit | Negotiating | Staff session | Members' meeting slot | Circulation agreed | Visit, then proposal | Proposal | Introduced, then convening agreed |
| 6 Partner | **Partnership closed** | Active | Circulation partner or benefit partner (sponsorship for variant A) | Circulation or group-rate partner | Circulated | Placement agreement | Sponsorship agreement | Community meeting held |
| 7 Producing results | Families or referrals coming through | Producing Results | Staff nurture | Member nurture | Employer referrals | Children enrolled; renewal | Students enrolled; reporting | Parent opt-ins; repeat convener |
| X Closed, lost | Exit at any stage, with a reason | — | | | | | | |

Two side states are not stages:
- **Deferred:** the other side said "not now" and gave a date. The deal keeps its stage and gets a next-action date.
- **Dormant partner:** a partner with no new sign-ups for two intake windows. It is not lost. It gets one re-engagement message per window.

### Common lost reasons

Every "Closed, lost" record carries one of these, plus a short note.

| Code | Meaning |
|---|---|
| `no_response` | The sequence ended (and the escalation, if any) with no reply |
| `declined` | A human said no |
| `not_relevant` | No staff, members or children the offer can serve near a campus |
| `no_route` | No working route after the call and visit attempts |
| `suppressed` | Opt-out, hard bounce or a request not to be contacted |
| `deferred_expired` | The deferred date passed and the one contextual follow-up got no reply |
| `stalled_after_meeting` | Re-prompts after the meeting went unanswered |
| `stalled_after_session` | Re-prompts after the session or visit went unanswered |
| `terms_not_agreed` | The proposal or agreement was not accepted |
| `compliance_blocked` | A compliance, HR or protocol check failed (public bodies, government) |
| `closed_or_moved` | The organisation closed or left the catchment |
| `duplicate` | Merged into another record |
| `capacity` | Silverleaf cannot serve the request (level, place or need) |
| Welfare only: `safeguarding_stop`, `needs_not_supported`, `funder_no_link` | |
| Government only: `election_period`, `payment_requested` (stop and escalate), `lists_offered` (refused and recorded) | |

---

## 4. The first stages by confidence band

The confidence band decides the first route and channel. Bands come from `export_resend_contacts.py`.

| Band | Employers | SACCOS | Introducers | Welfare | First route and channel | Sequence | Goes to "Responded" when |
|---|---|---|---|---|---|---|---|
| **High, direct** | 30 | 0 | 2 | 13 | Email to the named decision-maker's own or role address | AQ02 / F01: Day 0, then +4 and +4 working days, then stop | Any human reply |
| **High, indirect** | 215 | 0 | 10 | 60 | Email to a general inbox, addressed to the named person. Before sending, try one call to confirm that person reads the inbox (the row's `confidence_reason` says what would make it direct) | AQ02 / F01 if the role is verified; otherwise AQ01 | Any human reply |
| **Medium** | 370 | 0 | 4 | 10 | Email to the organisation's inbox, asking for the right person | AQ01 / F13: Day 0, then a routing check-in after 5 working days, then stop | A named owner is given. The deal moves to that person and continues on the high route, as the same deal |
| **Low** | 52 | 1 | 0 | 129 | Not contacted. Held for research or checks (stage 0) | None | It is promoted to Ready, or closed |
| **No email (call sheet)** | 451 | 116 | 0 | 233 | Phone call using a short script in Kiswahili or English, asking for the decision-maker and a route. If there is no phone, or the call fails and the place is within 10 km, the letter is hand-delivered | Up to two call attempts on different days, then one visit, then `no_route` | The call reaches the decision-maker or yields a route. The first message is then sent "as discussed" |
| **Government** | — | — | — | — | Always a formal Kiswahili letter on letterhead, delivered by hand. 11 offices also have an official inbox, used for an advance copy | Call after 5 working days, then a courtesy visit (F15) | The office acknowledges the letter |

**Escalation step (all bands).** When a sequence ends without a reply, send one message to the escalation contact 5 working days later, if one is recorded. Then close as `no_response`. Only 8 of the 1,118 company plans have an escalation contact today, so this step rarely applies yet.

**Order of work.** The January primary intake takes applications from October to December, and daycare and pre-primary enrol at any time (register, published facts). Sessions held in October and November therefore matter most this year. Recommended first wave: the P1 employers (100), the introducers (16), the welfare high-priority organisations with a route, and the four pilot councils.

---

## 5. Employers (staff-benefit partnership, variant B)

**Size:** 1,118 companies. 752 are ready, 1,090 carry variant B, and 14 new leads have no variant assigned yet. Reach tiers: P1 100, P2 150, P3 853, held (X) 15.

### 5.1 Goal and win

**Goal:** staff with children of school age hear about Silverleaf through their employer and choose to sign up. The offer (follow-up 1, after the first message) is the staff school-fee benefit (OF04), which costs the employer nothing, plus the family offer (OF01, OF02, OF09). The employer may present the benefit as its own, or add to it.

**Partnership closed (stage 6)** in either of two forms:
- **6a Circulation partner:** the employer agrees in writing (an email is enough) to circulate Silverleaf's invitation, pamphlet or QR code to staff, and confirms the first circulation has gone out.
- **6b Benefit partner:** the employer signs an education-benefit agreement, approved by the CEO (the MOU gate in the scope of work), usually with circulation as well.

The win is defined by what the employer controls. Sign-ups are counted as results (stage 7), not as the win (see question 8).

### 5.2 Stages

| # | Stage | Entry trigger | Exit trigger | Silverleaf role | The employer | Asset |
|---|---|---|---|---|---|---|
| 1 | Ready | Draft reviewed, band assigned, nothing held | First touch delivered | Marketing and Partnership Coordinator (the coordinator) | — | First message (existing drafts) |
| 2 | Contacted | First message delivered, or a call held | A human reply; or the sequence and escalation end | Coordinator | Reads, replies or refers | Follow-up 1 (offer on AQ02, routing question on AQ01); follow-up 2 (close, AQ02 only) |
| 3 | Responded | Reply classified (F02): interested, wants details, referred, not now or declined | A call or meeting is booked; or deferred; or lost | Coordinator | Says what they want | One-page offer outline (new; OF04 plus the family offer) |
| 4 | Call or meeting | Booked (date recorded), then held | Session agreed, or agreement agreed first, or lost | Coordinator; campus head where convenient | Explains staff numbers near the campuses, shifts, the best format, how staff are reached and who approves | Meeting checklist (new): approximate staff count at each site, shift pattern, staff channels (WhatsApp group, notice board, payslip insert, email), language, decision-maker |
| 5 | Staff session | Date, place or link, and format confirmed in writing | Session held, with an attendance estimate and pamphlets handed out | Coordinator plus an admissions officer from the nearest campus | Hosts or circulates the invitation, gives a slot | Pamphlet with QR code (new, Kiswahili and English); sign-up form (new); session talk or webinar deck (new); the invitation text in F04 step 2 |
| 6 | Partner | 6a circulation confirmed, or 6b agreement signed | Moves to 7 at the first sign-up | Coordinator; Finance confirms terms; CEO signs 6b | Circulates; signs | Circulation confirmation email (new template); benefit agreement template (new; modelled on the Rivertrees proposal, OF08, with register terms only) |
| 7 | Staff nurture | First staff sign-up with this employer's partner code | Ongoing; reviewed each intake window | Admissions officer (each family); coordinator (the account) | Re-circulates before each intake window | F06 acknowledgement, then F04 steps 3–5; partner report (new, totals only) |

**Order of session and agreement.** The user's model puts the staff session before the agreement, which suits most companies: little effort for them, and value shown first. Formal employers (banks, public bodies, international organisations) may want the agreement first. The pipeline allows 4 → 6b → 5, and records which order happened.

### 5.3 Session format and size

Only 19 of 1,118 companies publish a staff count, so the format is chosen from the count the employer gives at the meeting. Recommended rule (question 2):

| Staff at one site within 25 km of a campus | Format |
|---|---|
| 20 or more (or 10 or more within 10 km) | Site visit: a 20–30 minute talk with questions, pamphlets and the QR code |
| Several sites, or staff mostly in the field | Webinar (recorded, so later shifts can watch) plus a pamphlet pack for each site |
| Fewer than 10 | No dedicated session. A pamphlet and QR pack for the notice board and WhatsApp group, plus an invitation to a shared session: a monthly "employer families" session at the nearest campus, or a cluster session through an introducer such as TATO or HAT |

**Notice period.** A routine session with the standard, pre-approved pamphlet and talk needs 7 days' notice. A bespoke event (a stall at a large employer's family day, co-branded material) follows the event SOP's T-21 clock. The government plan already makes this split. F04 step 1 currently requires 21 days for every partner session (see conflict 3).

### 5.4 Subsegment variations

| Kind | Size (ready) | Bands: high-direct / high-indirect / medium / low / no email | What changes, and why |
|---|---|---|---|
| Safari operators and travel agencies | 480 (432) | 19 / 167 / 229 / 40 / 25 | Mostly small offices; guides and porters are often in the field or seasonal. Use an office visit when the team is in town, or a cluster session through TATO (388 of them are recorded as TATO members). Circulate through the crew WhatsApp group. The decision-maker is usually the founder or managing director, not HR. |
| Hotels, lodges and camps | 194 (123) | 1 / 10 / 56 / 4 / 123 | Shift workers: time the visit to shift handover, with two 15-minute slots (morning and afternoon handover) or a table in the staff canteen. Leave pamphlets in the staff room. Ask the general manager about the quiet season. Most have no email (123), so the call sheet comes first; 50 publish a phone. HAT is the introducer. |
| Hospitals and clinics | 188 (37) | 1 / 6 / 10 / 0 / 171 | Clinical staff cannot leave the wards. Hospitals: a staff-room session at handover, or a recorded webinar, arranged through HR or the matron. Clinics and dispensaries are small, and most (about 150, added from map data) have no route: give a pamphlet pack, no session. Faith-based hospitals may also be linked to welfare homes. APHFTA and CSSC are the introducers. |
| Banks and other companies | 87 (70) | 4 / 18 / 36 / 1 / 28 | There is a real HR department and formal benefits, so a signed agreement (6b) is more likely, and may come first. Branch networks may need head-office approval (escalation contact). Use a lunchtime session or webinar, and circulate through the intranet or payslips. TBA is the introducer. |
| NGOs and research bodies | 62 (28) | 2 / 1 / 18 / 0 / 41 | Aim at local staff. Do not imply programme funding or endorsement (segment rule). A slot at a staff meeting or a webinar. Some are also welfare funders: check the welfare run, and run one deal per organisation. |
| Colleges and universities | 23 (19) | 3 / 5 / 6 / 0 / 9 | Go through staff welfare or HR, never the student admissions inbox (segment rule). Avoid exam periods. A staff SACCOS may exist (for example Arusha Technical College): run one combined account. |
| Public bodies | 19 (12) | 0 / 5 / 0 / 6 / 8 | Two extra gates. **Compliance check before Ready:** no pending official business with Silverleaf, never combined with a request for official action (OF04 restriction), and named approval (question 12). **HR approval before the session:** the benefit is offered to all staff through an HR circular or an MOU through the legal unit. Expect 60–90 days. The six held now are "low" for this check. |
| International organisations | 10 (9) | 0 / 2 / 6 / 1 / 1 | Host-country and staff rules apply. The counterpart is often the staff association or welfare committee, which circulates (6a). A webinar suits mixed-site staff. Approval is slow. |
| Manufacturing | 19 (11) | 0 / 1 / 5 / 0 / 13 | Shift workers on the factory floor. A canteen session at shift change, with Kiswahili material, through HR or the workers' committee. Stress the four instalments (OF09). CTI is the introducer. |
| Retail | 17 (6) | 0 / 0 / 2 / 0 / 15 | Shift-based floor staff. A short store huddle and a staff-room QR poster. A chain's head office may approve (escalation contact). |
| Farms and estates | 14 (3) | 0 / 0 / 1 / 0 / 13 | Permanent and seasonal workers, often housed on site, often far from a campus. An on-site session during a break, through the welfare officer, in Kiswahili. Do not promise transport (VM12 is not approved). TAHA is the introducer. |
| Aviation | 5 (2) | 0 / 0 / 1 / 0 / 4 | Shift work and secure sites. A webinar, or a session off site or in a landside canteen, with any clearance arranged by the employer. |

The newer master segments map onto these kinds: healthcare employers to hospitals and clinics, education employers to colleges and universities, public-sector employers to public bodies, and NGO employers to NGOs and research bodies.

### 5.5 Variant A: sponsorship (14 safari operators)

These companies publish education or community giving. They are asked to sponsor students, at any size, including textbooks, transport or meals.

- **Win:** a signed sponsorship agreement (amount or items, number of students, term, reporting), approved by the CEO.
- **Stages:** Ready → Contacted → Responded → Meeting → Sponsorship proposal → Sponsorship agreement (6) → Sponsored students enrolled (7) → Reporting and renewal.
- **Different from variant B:**
  - there is no staff session or opt-in step;
  - the offer register gives variant A no offer message until it replies, so the follow-up must not be the staff-benefit text (see conflict 5);
  - students are chosen through admissions and, where relevant, a welfare partner, never by the sponsor;
  - reporting to the sponsor is in totals unless the family consents (VM10).
- **Staff benefit:** offered as a separate, optional conversation one month after the sponsorship is agreed, never bundled into the sponsorship ask (question 3).

### 5.6 The opt-in step (employers)

- **How staff sign up:** scan the QR code on the pamphlet or poster, open the link the employer shares, or fill in the paper form at the session (collected by Silverleaf, never by the employer).
- **Form fields** (for review by the data protection officer, aligned with the government plan's form):
  - name;
  - phone, and whether WhatsApp is preferred;
  - email (optional);
  - area of residence;
  - level of interest (daycare, pre-primary or primary);
  - preferred campus (Usa River, Arusha City, Kijenge, Ilboru, Boma Ng'ombe, or "not sure");
  - preferred language;
  - consent statement and date;
  - the partner code (filled in automatically from the QR code).

  The form asks for the level of interest, not a child's age or name, so it holds no children's data. Admissions asks about the child later, within a relationship the parent agreed to.
- **Consent wording (draft for the data protection officer):** "I agree that Silverleaf Academy may contact me by phone, WhatsApp or email about school admissions. My employer will not see my details; Silverleaf will share only total numbers with my employer. I can withdraw at any time by replying STOP or calling +255 769 486 660." It needs a Kiswahili version and review.
- **Which campus:** the parent chooses. Admissions confirms fit by level and travel area (the register says no offer guarantees a place or transport).
- **Link to the employer:** each partner gets a partner code (for example `EMP-<organisation id>`). The code is in the QR link and printed on the paper form. It is not personal data. Every family keeps the code through Inquiry, Tour, Application and Enrolment.
- **Eligibility for OF04** (20% for heads of department, 10% off the first year for other staff): the parent declares the employer and role on the application. HR confirms employment and grade in a one-line reply, with the parent's consent. No staff list is exchanged (question 11).
- **Until the consented store is live:** run inbound-only. Hand out the pamphlet with the admissions number and the application link, and ask families to quote the partner code.

### 5.7 What is recorded

| Stage | Fields | Outcome codes | Lost reasons |
|---|---|---|---|
| All stages | stage, stage date, owner (role), next action, next-action date, band and track at first touch, partner code, touch count, last touch date, escalation used | — | see §3 |
| 2 Contacted | first-touch date and channel, sequence (AQ01, AQ02 or call sheet), escalation date | delivered, bounced, opted out | `no_response`, `suppressed`, `no_route` |
| 3 Responded | reply date, reply type, referred-to role | interested, details, referred, not now (with date), declined | `declined`, `not_relevant`, `deferred_expired` |
| 4 Call or meeting | booked date, held date, format, approximate staff count at sites near campuses (a range, as the employer stated it), shift pattern, staff channels, language, approver role | session agreed, agreement first, no fit | `stalled_after_meeting`, `not_relevant` |
| 5 Staff session | type (site visit, webinar, staff room, cluster), booked and held dates, attendance estimate and method, pamphlets handed out | held, cancelled, rescheduled | `stalled_after_session` |
| 6 Partner | type (6a or 6b), circulation channel and date, agreement signed date, approver (CEO), offer IDs, Finance confirmation date, renewal-due date | circulation partner, benefit partner | `terms_not_agreed`, `compliance_blocked` |
| 7 Staff nurture | totals by month: sign-ups, enquiries, tours, applications, enrolments; last report sent | producing, dormant | — |

### 5.8 Timing and stall rules

| Gap | Typical | Re-prompt | Close or hold |
|---|---|---|---|
| Ready → Contacted | Within the wave | — | — |
| Contacted (AQ02) | Day 0, +4, +4 working days (F01) | Built into the sequence | Then escalation, then `no_response` |
| Contacted (AQ01) | Day 0, +5 working days (F13) | Built in | Same |
| Call sheet | Two call attempts on different days, within 5 working days | One visit if within 10 km | `no_route` |
| Reply → answer | Same or next working day (F02) | — | — |
| Responded → meeting booked | Within 10 working days | Two nudges, 4 working days apart | Deferred if a date is given, else `stalled_after_meeting` |
| Meeting → session booked | Summary sent within 2 working days; session within 3–6 weeks | +5 and +10 working days | Deferred to the next intake window, then `stalled_after_session` |
| Session → partner | Proposal or circulation request within 5 working days | +7 and +14 days | Held to the next intake window once, then `terms_not_agreed` |
| Deferred ("not now") | The date they gave | One contextual message on that date (F02 step 5) | `deferred_expired`. If they gave no date, one message at the next intake window |
| Partner → results | Re-circulation before each window: September for January primary, May for mid-year; daycare and pre-primary at any time | One reminder to the partner | Dormant after two windows with no sign-ups; one re-engagement per window |

### 5.9 Hand-off and reporting

- **Hand-off:** each sign-up goes to the admissions officer for the chosen campus the same working period, or the next working day. Then F06 (acknowledgement, a reminder after 2 working days, a close after 5) and F04 steps 3–5 (qualification, visit offer, then tour, application or enrolment).
- **Reporting back:** a partner report once a term, and after each session. It gives sessions held, attendance estimate, sign-ups, enquiries, tours, applications and enrolments, in totals, with numbers below 3 shown as "fewer than 3". There are no names, ever.

### 5.10 Metrics

- **Stage conversion:** delivered → replied; replied → meeting held; meeting → session held; session → partner; partner → at least one sign-up; sign-ups → enquiry → tour → application → enrolment.
- **Leading indicators:**
  - reply rate by band and by kind;
  - days from reply to meeting;
  - sessions booked per week;
  - sign-ups per 100 attendees, and per circulation;
  - share of partners re-circulating each window;
  - cost per sign-up and per enrolment.

Compare one change at a time (acquisition framework, Measurement).

---

## 6. Savings groups (SACCOS)

**Size:** 117: 48 employer- or institution-based, 67 community or open-bond, 2 from map data with no type. Only one publishes an email, and that one is held. So almost every first touch is a Kiswahili letter or a call.

**Audience:** members, not staff, reached through the committee, in Kiswahili. The first message asks to meet the committee about members' children's education (F03). The offer message gives the family offer and the member-association rate (OF07: "starting at 7% per student at 50 students"). OF07 is documented for KINEFA only, so Finance must agree to extend it before it is stated. There is no loan, payroll or subsidy claim (VM06).

**Win (stage 6):** the committee agrees in writing to circulate Silverleaf's invitation or QR code to members, or gives Silverleaf a slot at a members' meeting or AGM. A group-rate agreement, once Finance approves, is an optional stronger form.

| # | Stage | Entry → exit | Silverleaf role | The SACCOS | Asset |
|---|---|---|---|---|---|
| 1 | Ready | Kiswahili review and Finance approval of the member rate done → first touch | Coordinator | — | Kiswahili first message or letter (F03) |
| 2 | Contacted | Letter delivered or call held → reply, or end of sequence | Coordinator | Manager or chair reads it | F03 follow-ups (offer, then close) |
| 3 | Responded | Reply → committee meeting booked | Coordinator | Puts it on the committee agenda | One-page member offer sheet (Kiswahili) |
| 4 | Committee meeting | Booked → held | Coordinator plus a Kiswahili-speaking admissions officer | Committee decides | Short talk; member offer sheet |
| 5 | Members' meeting or AGM slot | Slot confirmed → held | Admissions officer presents | Gives 10–15 minutes on the agenda | Kiswahili pamphlet with QR code; paper sign-up form |
| 6 | Partner | Circulation confirmed or slot held; optionally a group-rate letter | Coordinator; Finance; CEO for a rate agreement | Circulates to members | Circulation confirmation; group-rate letter (new) |
| 7 | Member nurture | First member sign-up with the SACCOS partner code (`SAC-<id>`) | Admissions | Re-circulates before each intake | F06, then F04 steps 3–5 |

**Variations:**
- **Employer-based SACCOS (48):** the members are one employer's staff. If that employer is already in the pipeline (for example Arusha Technical College and its staff SACCOS), run one combined account. The employer deal leads and the SACCOS committee joins at the session stage (question 16).
- **Community SACCOS (67):** a broader community membership. The members' meeting is the main event. Ward community development officers, recorded in the government run, are a possible route; the government plan notes this link to savings groups.
- **Timing:** members' meetings and AGMs follow each society's calendar. Ask the committee for the next date and record it as the next-action date. Group-rate counts (50, 100 and 150 students) are tracked as totals by partner code.

Recorded fields, stall rules and reporting are as for employers, except that F03's three touches stand in for F01. Lost reasons add `rate_not_approved` (Finance does not extend OF07).

---

## 7. Introducers

**Size:** 16, all ready.

| Kind | Organisations | Route band |
|---|---|---|
| Chambers | TNCC national, TNCC Arusha regional, TNCC Kilimanjaro regional | 2 high-indirect, 1 medium |
| Employers' associations | ATE (national; Northern Zone, Arusha), CTI (national; Arusha and Moshi office), TPSF | CTI high-direct; ATE and TPSF high-indirect; ATE Northern Zone and CTI Arusha and Moshi medium |
| Sector associations | TATO, HAT, TBA, TAHA, APHFTA, CSSC | TATO high-direct; HAT, TBA, TAHA and CSSC high-indirect; APHFTA medium |
| HR body | Women HR Association of Tanzania (WHAT) | High-indirect |
| Other | East African Business Council (EABC) | High-indirect |

**Goal:** the introducer shares the staff benefit with its member employers. Its pipeline produces **employer leads, not parents**.

**Win (stage 6):** at least one circulation to members, such as a newsletter or bulletin item, a slot at a members' meeting or HR forum, or a set of introduction emails. A formal member-benefit listing or MOU is a stronger form, and needs the CEO's approval.

| # | Stage | Entry → exit | Silverleaf role | The introducer | Asset |
|---|---|---|---|---|---|
| 1–3 | Ready, Contacted, Responded | As for employers (F01/F13, F02) | Coordinator | Executive secretary or secretariat | Existing introducer drafts |
| 4 | Meeting | Booked → held | Coordinator | Agrees the channel and timing | Member-facing one-page note (new; the follow-up offers "a one-page note you could share with members") |
| 5 | Circulation agreed | Channel and date agreed → circulated | Coordinator | Schedules it | Newsletter text; event slot talk; QR link carrying the introducer code (`INT-<id>`) |
| 6 | Circulated | Confirmed circulation → first referral | Coordinator | Circulates | — |
| 7 | Employer referrals | Each employer that responds through the introducer | Coordinator | — | Thank-you letter and termly report in totals (question 6) |

**How referrals enter the employer pipeline:** an employer that responds through an introducer enters the employer pipeline at stage 3, Responded, as a warm lead. Its source records the introducer code. If the employer is already in the master, the existing deal is updated rather than duplicated. A staff member who signs up directly from an introducer's circulation is recorded under the introducer code, and later re-linked to the employer's code if the employer becomes a partner.

**Variations:**
- **Sector associations reach a kind of employer directly:**
  - TATO: safari operators (480; 388 are recorded as TATO members);
  - HAT: hotels (194);
  - TBA: banks;
  - TAHA: farms and estates;
  - APHFTA: private health facilities (188 hospitals and clinics);
  - CSSC: faith-based hospitals and welfare.

  Ask each for a cluster session as well as circulation. For the hundreds of small employers, this is the cheapest way to reach staff (§5.3).
- **Chambers and employers' associations (TNCC, ATE, CTI, TPSF)** cover all kinds of employer. Their channels are events and HR forums, so plan around their calendar.
- **WHAT's members are HR practitioners**, the people who decide benefits. Ask for a speaker slot.
- **EABC** is regional, with little local reach. Treat it as low priority.

**Stall rules:** as for employers. After circulation, check referrals at 2 and 6 weeks. If there are none, ask once for a second channel, then mark the introducer dormant.

**No referral rewards:** OF05 has expired and F11 is blocked until the 2027 scheme is approved. Any acknowledgement is non-monetary.

**Metrics:** circulations per introducer, employers responding per circulation, referred employers reaching stage 6, and enrolments traced back through referred employers.

---

## 8. Welfare organisations

**Size:** 445 in scope; 86 drafts are ready. Tracks: WA00 hold 321, WA01 routing 124, WA02 consultative 0 (it needs a licence confirmed by the authority). The welfare lead is an **account that pays fees for the children in its care**, not a channel to parents (welfare skill). The design builds on F14 in [the welfare plan](../../plans/b2b-welfare-leads-plan.md) §5.6.

| Kind | High / medium / low priority | Total | Ready | Bands: high-direct / high-indirect / medium / low / no email |
|---|---|---|---|---|
| Residential care (children's homes) | 23 / 20 / 57 | 100 | 17 | 3 / 9 / 4 / 38 / 46 |
| Family-based and sponsorship programmes | 12 / 14 / 138 | 164 | 25 | 2 / 17 / 5 / 28 / 112 |
| Specialised centres | 3 / 6 / 61 | 70 | 5 | 0 / 5 / 0 / 17 / 48 |
| Funders | 3 / 7 / 94 | 104 | 34 | 8 / 24 / 1 / 44 / 27 |
| Welfare networks (introducers) | 0 / 0 / 7 | 7 | 5 | 0 / 5 / 0 / 2 / 0 |

### 8.1 Homes, programmes and centres (placement partnership)

**Goal:** the organisation places children in its care at Silverleaf. The offer message gives the partner rate (OF03), the free uniform (OF01) and the instalments (OF09). OF03 applies only when the home places **all** its primary-age children, from 3% per child at 10 children up to 18% at 60. A smaller home pays standard fees with the family offer.

**Win (stage 6):** a signed placement agreement on terms Finance has approved, covering the number of places by level and campus, billing, and reporting, and approved by the CEO.

| # | Stage | Entry → exit | Silverleaf role | The organisation | Asset |
|---|---|---|---|---|---|
| 1–3 | Ready, Contacted, Responded | WA01: one message or call, one check-in after 5 working days. WA02: one follow-up after 4 working days (F14) | Coordinator | Head of home, country manager or programme director | Existing drafts and follow-up |
| 4 | Placement conversation | A 20–30 minute call → needs recorded in totals by age band | Coordinator plus admissions | Shares the age bands and timing | Placement-planning checklist (VM08) |
| 5a | Safeguarding visit | Visit protocol confirmed → visit held | Two staff; designated safeguarding lead informed | Hosts, or visits a campus | Visit protocol (new); no photographs |
| 5b | Proposal | Within 5 working days of the visit → accepted or declined | Coordinator; Finance | Reviews, often with a funder | Proposal using approved terms only (VM13 is blocked until a terms memo is approved) |
| 6 | Placement agreement | Signed | CEO signs | Signs | Placement agreement template (new) |
| 7 | Children enrolled; renewal | Admissions assesses each child in Ed-admin, outside the lead database → totals recorded. A renewal check 8 weeks before the next intake | Admissions; coordinator | Supplies documents with the guardian's written consent | Termly progress summary (VM10, with consent) |

**Variations:**
- **Residential care:** the standard path above. The home is the guardian and the payer.
- **Family-based and sponsorship programmes:** the children live with families and may attend many schools, so OF03's "all primary-age children" condition may not fit. Two paths:
  - **(a)** the programme pays for chosen children, on the standard path;
  - **(b)** the programme circulates Silverleaf's information to caregivers, who opt in themselves, as for employers (programme code `WEL-<id>`). This path needs the programme's agreement, and the form adds no data about children.

  The decision is often the sponsor's. Route to the funder only with the programme's agreement.
- **Specialised centres** (disability, rescue, street children): add a **needs-fit check** before the visit (welfare plan decision 4: which needs Silverleaf can support well). Close as `needs_not_supported` where the fit is not there. Rescue and safe-house locations stay confidential: no address appears in any shared material.
- **Opt-in:** there is no parent opt-in, except path (b). Children's data is held only by admissions, with the guardian's written consent. The lead databases record places discussed and places enrolled as totals.

### 8.2 Funders (sponsorship)

**Goal:** sponsorship of students, at any size. It is asked only where the run holds a sourced, verified link to a home or programme near the campuses. Without that link the draft is held.

**Win (stage 6):** a signed sponsorship agreement, approved by the CEO. It is often three-way: the funder pays, the linked home places the children, and Silverleaf teaches.

**Stages:** Ready → Contacted → Responded → Meeting (often a video call, across time zones and sometimes languages) → Sponsorship proposal tied to the linked home (5) → Sponsorship agreement (6) → Students enrolled, then reporting and renewal (7).

**Variations:**
- Many funders are abroad, and their decision-maker is often a chair. A chair is used only when no executive is named (the recipient rule).
- Their budget cycles matter: record the cycle as the next-action date.
- The follow-up already offers the partner rate as "a way to stretch sponsorship".

**Reporting:** to the funder only with the home's consent, in an approved format (VM10).

### 8.3 Welfare networks (introducers)

Like the employer introducers: circulation to member homes is the win, and each home that responds enters §8.1 at stage 3 with the network code.

### 8.4 Timing, records and metrics (welfare)

- **Timing:**
  - follow F14;
  - a budget-timing "not now" is held with a dated next action;
  - a licence that is not confirmed returns the deal to WA00;
  - a safeguarding concern stops the deal and is escalated to the designated safeguarding lead, with nothing automated;
  - decisions for a January start are mostly made between October and November.
- **Records:**
  - as for employers;
  - plus age bands discussed (totals), places discussed, places agreed and places enrolled;
  - plus the linked home for funders, the visit date and the safeguarding lead informed.

  Lost reasons add `safeguarding_stop`, `needs_not_supported` and `funder_no_link`.
- **Metrics:**
  - conversations held per contacted organisation;
  - visits, then proposals, then agreements;
  - places agreed, then places enrolled;
  - renewal rate;
  - sponsorship value agreed (totals).

---

## 9. Government offices

**Size:** 230 offices; no letter has been delivered yet, and no community events are recorded. The design follows F15 and F16 in [the government plan](../../plans/b2b-government-leads-plan.md) §5.7. Its office stages (`prospect`, `letter_sent`, `introduced`, `convening_requested`, `convening_agreed`, `event_held`, `repeat_convener`) map onto the spine in §3.

**Goal:** a community meeting at which Silverleaf gives a free 15–20 minute talk in Kiswahili on getting children ready for school, with a take-home parent booklet. Parents opt in there. Silverleaf asks the office for nothing for itself, offers nothing to officials, and never takes lists of residents (OF04 restriction; register rule 5).

| Subsegment | Offices | Order and request | Stage path | Win |
|---|---|---|---|---|
| Pilot councils (GA01) | 4: Arusha City, Arusha District, Hai, Meru (all ready) | First: a protocol introduction | Letter by hand → call after 5 working days → courtesy visit → introduction recorded | The council introduces Silverleaf to its ward and village executive officers |
| Other councils | 5: Moshi Municipal, Moshi District, Siha, Monduli, Simanjiro (held) | After the pilot | Same | Same |
| District commissioner and regional offices | 7 + 3 (held) | A courtesy notice only, after the pilot introductions, once the B2G owner approves | Notice delivered → acknowledged | Informed |
| Ward offices | 129: 57 within 10 km, 35 at 10–20 km, 32 beyond 20 km, 5 not yet located | After the council's introduction, nearest first; the executive officer verified within 90 days (GA02) | Convening request → slot agreed → meeting held → opt-ins → repeat | A community meeting held with Silverleaf's talk |
| Village offices | 82: 31 within 10 km, 41 at 10–20 km, 10 beyond 20 km (37 Hai, 35 Meru, 9 Arusha District, 1 mapped inside Arusha City and flagged, because cities have mitaa, not villages) | Same | Same, at the village assembly | Same |
| Mtaa offices | None recorded | A gap in the run | Same, at the mtaa meeting | Same |

**Variations:**
- **Ward:** the ward public meeting is convened by the ward executive officer with the councillor, and the Ward Development Committee meets at least four times a year. The councillor is elected, so engage elected leaders only through the forum they chair (political neutrality).
- **Village:** the village assembly includes all residents aged 18 and over and meets at least quarterly (confirm the section of the Act before quoting it). The village chair is elected; the village executive officer is the administrative route.
- **District commissioner offices:** district public meetings are formal and are not a v1 target. The notice only keeps the office informed.
- **Councils:** a council may also offer stalls at its own public events. Those are bespoke events (T-21).

**Opt-in step (VM16):** Silverleaf's own paper form, or a QR code, offered at the end of the talk. The fields follow the government plan:
- name;
- phone, and whether WhatsApp is preferred;
- area (mtaa or village);
- level of interest;
- preferred campus;
- consent statement and date;
- the event code.

The office never collects or sees the forms. Paper forms are entered into the consented store within 24 hours, then secured or destroyed. Until the store is live, run inbound-only: hand out the booklet with the admissions number and the application link, and ask parents to quote the event code.

**Recorded:** office stage and date, letter delivered date, introduction reference, convening request date, the post-holder verified date (within 90 days), and the `community_events` row (it already exists, with counts only): event code, date, expected and estimated attendance and method, opt-ins, enquiries, tours, applications, enrolments and cost. Lost reasons add `election_period`, `payment_requested` and `lists_offered`.

**Timing:**
- call 5 working days after the letter;
- courtesy visit after the call;
- re-verify the post holder within 90 days before a convening request;
- a routine agenda slot needs 7 days' notice, with materials approved once; a bespoke event needs T-21;
- confirm logistics at T-2;
- a thank-you letter with aggregate feedback (VM17) within 5 working days;
- pull counts weekly for 8 weeks after each event.

**Stop when:** an office declines; an election campaign period starts; anyone asks for payment or gifts (stop and escalate); or anyone offers lists (refuse and record).

**Hand-off:** each opt-in goes to F06, then F04 steps 3–5, outside the databases. Only counts by event code come back.

**Metrics:**
- letters → introductions → convening requests → meetings held;
- attendance;
- opt-ins per 100 attendees;
- cost per opt-in;
- enrolments per event;
- repeat conveners.

The ward score's "observed yield" factor starts to count once the first events are recorded.

---

## 10. The parent funnel: one hand-off for every segment

| Step | What happens | Flow | Owner |
|---|---|---|---|
| Opt-in | The family signs up with a partner or event code | VM16 / new staff opt-in form | — |
| Inquiry | Acknowledged the same working period (next working day at most); age or grade and travel area asked | F06 steps 1–3 | Admissions officer, nearest campus |
| Qualified | Campus fit confirmed; visit slots or the application step offered | F04 step 4 | Admissions |
| Tour, Application, Enrolment | Recorded as they happen | F04 step 5 | Admissions |
| Report | Totals by partner code, back to the partner | F04 step 5; VM17 | Coordinator |

**Partner codes:**
- `EMP-` employer;
- `SAC-` savings group;
- `INT-` introducer;
- `WEL-` welfare programme circulation;
- `EVT-` government community event.

The code travels with the family in the consented store and in admissions records. The lead databases hold only totals per code per month.

---

## 11. Existing flows, and the gaps

| Stage | Covered by | Note |
|---|---|---|
| Intake and track choice | F12 (named in outreach-flows.md and campaigns C01 and C02) | **Not in the flows table** (only F01–F11 are recorded) |
| First touch, AQ02 | F01 | Three touches, then stop |
| First touch, AQ01 routing | F13 | Two touches. **Not in the flows table** |
| SACCOS first touch | F03 | |
| Reply handling | F02 | Covers interested, details, referral, not now, refusal, bounce and out of office |
| Partner session to opt-in | F04 steps 1–2 | Its 21-day rule is too slow for routine sessions (conflict 3) |
| Opt-in to enrolment | F06, then F04 steps 3–5 | |
| Welfare consultative path | F14 (welfare plan) | Plan only; not in the flows table |
| Government protocol and convening | F15 (government plan) | Plan only |
| Community session to opt-in | F16 (government plan) | Plan only |
| Referral rewards | F11 | Blocked |

**Gaps that need new flows (named only; not written here):**
- **F17 Meeting to staff session (employers):** meeting summary, format choice, booking, 7-day light path.
- **F18 Partner agreement:** proposal, Finance and CEO gates, signature, renewal, and the circulation confirmation for 6a.
- **F19 Partner re-circulation and dormancy:** a reminder to the partner before each intake window, and dormant re-engagement.
- **F20 Sponsorship:** variant A and welfare funders, with proposal, agreement, reporting and renewal.
- **F21 SACCOS committee to members' meeting.**
- **F22 Introducer circulation and referral intake**, with the non-monetary acknowledgement.
- **F23 Escalation contact:** one message after a silent sequence.
- **F24 Call-sheet first touch:** call script, attempts, visit and the "as discussed" email.
- **F25 Partner reporting:** the termly totals report with small-number suppression.

---

## 12. Conflicts with the existing documents

1. **Stage order and names.** The Process Map's partner workflow is Meeting → Proposal → Agreement/MOU → Activation, with the stages Prospect → Contacted → Engaged → Negotiating → Active → Producing Results. The user's model runs the staff session before the agreement.

   **Proposed:** keep both orders (session first by default) and map them onto the six stages (§3). The welfare plan (F14, `account_pipeline`) and the government plan (office stages) each use their own names too. This draft keeps those as track stages under one spine.
2. **The win is defined differently.** The Process Map treats "Active" as after an agreement or MOU. The user's model also counts a circulation partner (6a) as closed, with no signed agreement.
3. **Notice period.** F04 step 1 needs at least 21 days before any partner session (the event SOP). The government plan uses 7 days for routine slots with pre-approved materials. A small site visit would wait three weeks under F04.
4. **Band and track disagree.** 227 company and introducer rows in a high band (216 high-indirect, 11 high-direct) are on AQ01 routing. Their follow-up asks who to speak to instead of giving the offer, and they get two touches, not three. Only 37 chosen company and introducer rows are on AQ02, the F01 three-message path. "F01: three messages and stop" therefore describes a small minority of today's sequences.
5. **Variant A follow-ups.** All 14 sponsorship rows carry staff-benefit (variant B) follow-ups in `follow_up_1`, and four also carry a close that offers "the one-page staff offer sheet". The offer register says variant A gets no offer message until it replies. Sending the stored follow-up would switch the ask mid-thread.
6. **Call-to-action labels.** The master's `outreach_plans.cta_type` values ("Welfare referral", "Sponsor referral", "Committee referral", "Information offer", "Format choice") no longer describe the drafts. Every first message now asks for "a short meeting, either in person or by phone". Tracking should not read the CTA from this column.
7. **Flows missing from the flows table.** F12 and F13 are named in `outreach-flows.md` and in campaigns C01 and C02, but are not in the master's `outreach_flows` table. F14–F16 exist only in the plans.
8. **What government material may say.** The register's JSON rules say convening letters "describe the family offer for parents only (OF01, OF02, OF09)". The register's Markdown rule 5 (changed 1 October) says letters state no offer. The government plan's booklet (VM15) lists "published levels, fees and intake windows", while the campaign document holds 2027 fee figures out of copy until they are approved. The booklet's content needs one decision.
9. **Who is asked for sponsorship.** The acquisition framework (Message construction, point 1) still says "Sponsorship is asked of welfare funders only". AGENTS.md and the offer register have also allowed employers with published education giving (variant A) since 1 October.
10. **Escalation.** The recipient rule relies on an escalation contact after silence, but only 8 of 1,118 company plans record one.
11. **Counts.** The Core Segments document (written on the morning of 11 October) is behind the databases: companies 716 → 1,118, hotels 117 → 194, hospitals and clinics 29 → 188, government offices 150 → 230 (villages 2 → 82), and introducers with no email 1 → 0.
12. **The user's model and the decided opt-in rule.** The user's first model mentioned asking the employer for "a direct list of emails". That is now replaced by the opt-in decision. The existing documents already agree with the decision: VM01, F04 steps 2–3, the campaign document's partner message ("the organisation decides whether to circulate the invitation; interested parents contact Silverleaf directly"), and VM16. No existing document asks for a staff list.

---

## 13. Open questions for the user

| # | Question | Recommended answer |
|---|---|---|
| 1 | Who owns each stage? | The coordinator owns stages 1–6 for employers, SACCOS, introducers and welfare, and the government letters. The admissions officer at the family's chosen campus owns every opt-in onward, and co-presents sessions. The campus head hosts campus-based sessions. Finance confirms terms. The CEO signs agreements (the MOU gate). The B2G owner is informed before any government letter. Welfare funders move to the Fundraising and Partnerships Associate once that role is filled. |
| 2 | Minimum staff size for a site visit rather than a webinar? | A site visit for 20 or more staff at one site within 25 km (or 10 or more within 10 km). A webinar for multi-site or field staff. Under 10: a pamphlet pack plus a shared or cluster session. Use the staff count the employer gives at the meeting, since only 19 companies publish one. |
| 3 | Do variant A sponsors also get a staff session? | Yes, but separately: offer the staff benefit as an optional second conversation one month after the sponsorship is agreed. Never bundle it into the sponsorship ask. |
| 4 | Community meeting format? | 15–20 minutes inside an existing ward or village meeting, in Kiswahili, by two Silverleaf staff (one from admissions), with the parent booklet and a voluntary paper form plus QR code. No photographs, gifts or payments. Inbound-only until the consented store is live. |
| 5 | How are welfare-sponsored children enrolled? | Admissions assesses each child in Ed-admin, with the guardian institution's written consent. The databases hold only places discussed, agreed and enrolled. OF03 applies only when all primary-age children are placed. A funder pays under a three-way agreement with the linked home. Reporting to funders needs the home's consent. |
| 6 | Do introducers get a referral acknowledgement? | Yes, non-monetary only: a thank-you letter and a termly report in totals (employers reached, partners closed). There is no reward until the 2027 referral scheme is approved (OF05 expired, F11 blocked). |
| 7 | Where do sign-ups live? | In a restricted store outside the repository, owned by admissions: the admissions system if it can take enquiries with a source code, otherwise a restricted form and sheet. Run inbound-only until the data protection officer approves the notice and form and PDPC registration is confirmed. |
| 8 | Is the partnership closed at the circulation, or at the first sign-up? | At the circulation (6a) or the signature (6b), because those are in the partner's control. Sign-ups measure results. |
| 9 | Session first, or agreement first? | Session first by default. Agreement first when the employer asks, which is typical for banks, public bodies and international organisations. Record which order happened. |
| 10 | Notice period for staff sessions? | 7 days with pre-approved standard assets; T-21 only for bespoke events. Amend F04 step 1 accordingly. |
| 11 | How is OF04 eligibility (heads of department 20%, others 10%) confirmed without a staff list? | The parent declares the employer and role on the application. HR confirms employment and grade for that one person, with the parent's consent. |
| 12 | Who performs the public-body compliance check, and what fails it? | The CEO or a named compliance lead. Exclude bodies that tax, regulate, inspect or license Silverleaf (for example the revenue authority) and any body with official business pending with Silverleaf. Others go through HR only. |
| 13 | How small a number may a partner report show? | Show "fewer than 3" for any count of 1 or 2, so that a small employer cannot identify who enrolled. |
| 14 | Use the escalation contact after a silent sequence? | Yes: one message, 5 working days after the sequence ends, then close. Record escalation contacts for P1 employers first. |
| 15 | How are no-email rows worked (451 companies, 116 SACCOS, 233 welfare)? | Phone first: two attempts on different days, then a hand-delivered letter for the nearest (within 10 km) or P1 and P2 leads. Then `no_route`. Start with the 50 hotels and 18 hospitals and clinics that publish a phone. |
| 16 | Combine an employer-based SACCOS with its employer? | Yes: one account. The employer deal leads, and the SACCOS committee joins at the session. |
| 17 | How many sessions a week can the team run? | Cap at three sessions or meetings a week until the Fundraising and Partnerships Associate is hired, and book the P1 employers and introducers first, before the January primary window closes in December. |
| 18 | What is the renewal and re-circulation cadence? | Ask partners to re-circulate before each intake window (September for January primary, May for mid-year). Review each agreement 8 weeks before the January intake. A partner becomes dormant after two windows with no sign-ups. |
| 19 | What may the government booklet say (conflict 8)? | Letters state no offer. The booklet may give the published levels, campuses, intake windows and the family offer (OF01, OF02, OF09) with the Finance condition, but no fee figures until the 2027 fees are approved. |

---

## 14. What gets built after approval

Nothing below is built yet. Each item would be planned with its own file boundaries before work starts.

**Data fixes to make first** (they affect what the pipeline would track):
- give the 14 variant A rows sponsorship follow-ups, or none (conflict 5);
- align the AQ track with the band for the 227 high company and introducer rows on AQ01 (conflict 4);
- assign a variant to the 14 new leads that have none;
- retire or relabel `cta_type` (conflict 6);
- add F12 and F13 to the flows table.

**Tracking, in all three databases:**
- A shared vocabulary file listing the stages for each track, the spine mapping, outcome codes and lost reasons. It would sit with, or extend, the controlled-vocabulary registry proposed in Phase 0 of the welfare plan.
- `account_pipeline` (Phase 0.9 of the welfare plan, not yet built): one row per account, holding the track, subsegment, stage, stage date, owner role, next action and date, partner code, band and track at first touch, agreement type and dates, approver, offer IDs and Finance confirmation date.
- `pipeline_events`: the history of stage changes, with the date and the role that made each change.
- `partner_results`: monthly totals per partner code (sign-ups, enquiries, tours, applications, enrolments, last report sent). It never holds a person.
- `partner_code` and link fields: SACCOS to employer, referral source, and funder to linked home. The welfare run's relationships table already holds the funder link.
- The government run reuses `community_events`.
- **Rebuild safety:** the welfare and government run databases are regenerated by `run_pipeline.py --rebuild-db`, so their pipeline state must live in a committed file the pipeline loads (for example `data/runs/<run-id>/pipeline.csv`). It must never be typed into the database alone. The master takes changes through the update skill's validator, preflight and one transaction.
- **Verification checks:**
  - every open deal has a next-action date;
  - every lost deal has a reason;
  - stage moves follow the allowed order;
  - no person-level parent or child field exists anywhere.

**Workbook:** a "Pipeline" sheet in the master workbook (`scripts/master/export_master_workbook_data.py`, then `npm run build:workbook`) and in each run workbook. Columns: organisation, kind, band, stage, stage date, owner, next action, next-action date, outcome, lost reason, partner code, and the totals.

**Resend:** new contact properties `pipeline_stage`, `next_action_date` and `partner_code`. Only stage 1 (Ready) rows would be exported for first messages. This touches `scripts/messaging/export_resend_contacts.py`, which **another task is editing now**, so this part must run after that task merges.

**Map:** filters by spine stage, partner status (partner, dormant, lost) and "producing results", in `scripts/maps/build_lead_map.py`.

**Flows (design only):** add F12–F16 to the flows table and draft F17–F25 (§11). All stay disabled.

**Assets (people, not code):**
- one-page offer outline;
- staff pamphlet with QR code (Kiswahili and English);
- sign-up form and privacy notice (data protection officer review);
- session talk and webinar deck;
- SACCOS member sheet;
- introducer member note;
- circulation confirmation, benefit, sponsorship, placement and group-rate agreement templates (Finance and CEO);
- partner report template;
- call script.

Each Kiswahili asset gets a native-speaker review.

---

## Sources

- [Silverleaf Core Segments - 2026-10-11](../../outputs/messages/Silverleaf%20Core%20Segments%20-%202026-10-11.md)
- [Outreach flows](outreach-flows.md), [new-contact acquisition framework](new-lead-acquisition-framework.md), [campaign positioning and cadence](campaign-positioning-and-cadence.md)
- [Offer register](../../skills/silverleaf-outreach/references/offer-register.md) and `data/reference/silverleaf-offer-register.json` (version 2026-09-23-offer-v4)
- [Scope of work](../scope/scope-of-work.md) §6 and §8; [delivery plan](../plans/delivery-plan.md)
- `references/Marketing & Partnerships - Department Process Map.docx`, process 9 (partner stages)
- [Welfare plan](../../plans/b2b-welfare-leads-plan.md) §4, §5.4–5.6, §9; [government plan](../../plans/b2b-government-leads-plan.md) §4, §5.6–5.7
- `skills/silverleaf-welfare-leads/SKILL.md`, `skills/silverleaf-government-leads/SKILL.md`
- Read-only copies of the three databases (11 October 2026, evening): `outreach_plans` (selection, segment, variant, track, CTA, follow-ups), `organisations`, `employer_reach`, the welfare and government `outreach_plans`, `government_office_profiles` and `community_events`. Bands use `company_rows` and `welfare_rows` from `scripts/messaging/export_resend_contacts.py`.
