# Silverleaf organisational lead generation progress deck

## Deck brief

- **Working title:** Organisational Lead Generation: Progress, Method and Activation Plan
- **Audience:** Silverleaf Academy leadership, marketing, enrolment and partnerships teams
- **Format:** PowerPoint, 16:9 widescreen, maximum 10 slides
- **Purpose:** Explain what has been built, how the lead engine works, how outreach will run, and how parent acquisition differs from organisational partnership outreach.
- **Status represented:** Research, data consolidation, messages and automation designs are complete as drafts. Sending remains disabled until final review and implementation approval.

## Content guardrails

- Distinguish source records from deduplicated master records. Source totals must not be added together and presented as the master total because sources overlap and the master preserves enrichment, branches and unresolved matches.
- Describe the 955 records as **organisation/place records**, not 955 verified companies.
- Describe the 342 records as **published business-contact records**. A named business contact is not evidence that the person is a parent.
- Use only current, verified recipient facts as personalised hooks. Where no reliable hook exists, open directly with the relevant offer.
- Treat scholarships, bursaries and fee discounts as notification topics only when Silverleaf has approved and confirmed them. Do not imply that an offer currently exists or that a recipient qualifies.
- Keep organisational outreach separate from parent marketing consent. Public business information supports partnership research; parent email marketing uses first-party sign-ups and appropriate notices and choices.
- Do not place personal lead records, email addresses or phone numbers on presentation slides.

## Slide plan

### Slide 1 — Silverleaf now has a repeatable organisational lead engine

**Purpose:** Establish progress and the current activation status.

**Content:**

- 955 organisation/place records in the consolidated master database
- 342 published business-contact records
- 927 personalised outreach plans
- 54 design-only automation steps
- All sending remains disabled pending review and implementation

**Visual:** Four large statistic blocks on Electric Blue, with a thin process line below showing research, enrichment, messaging and activation review.

### Slide 2 — Silverleaf will use two lead-generation tracks

**Purpose:** Make the operating distinction clear at the beginning of the presentation.

**Track 1: Organisational partnerships**

- Build lists from public organisational registries, directories and repositories.
- Use TATO for safari and tour companies, TCDC for SACCOs and cooperatives, and OSM for mapped employers around candidate campuses.
- Enrich records with public company websites and published business contacts.
- Approach HR, staff welfare, leadership or the correct internal owner.
- Offer a simple way for the organisation to introduce Silverleaf Academy to its staff through an approved information pack, admissions Q&A or campus introduction.
- Goal: win staff members as customers through a useful partnership with their employer or cooperative.

**Track 2: First-party parent acquisition**

- Publish social media content and run targeted advertising that directs interested parents to the Silverleaf website.
- Use relevant landing pages and a website pop-up or embedded form.
- Invite parents to join the school newsletter and receive updates about approved scholarships, bursaries, fee discounts, admissions and campus opportunities.
- Send consenting sign-ups directly into the parent audience list with recorded source, purpose and consent status.
- Use parent-specific nurture messages to convert interest into enquiries, visits, applications and enrolment.

**Visual:** Two parallel lanes with different entry points and a shared outcome at the bottom: qualified enrolment opportunities. Use an organisation/building motif for Track 1 and a content-to-website journey for Track 2.

### Slide 3 — Evidence and proximity shape the organisational method

**Purpose:** Explain how an organisational record becomes a reviewable lead.

**Content:**

1. Select authoritative public sources for the target sector.
2. Preserve raw evidence and source URLs.
3. Normalise names, contact fields and organisation types.
4. Deduplicate conservatively while preserving unresolved branches.
5. Map each organisation to the nearest candidate campus and transport-distance band.
6. Prioritise using contactability, likely staff scale, sector fit and verified education affinity.
7. Research the organisation website for a decision-maker and usable evidence.
8. Generate a source-backed message and route it to human review.

**Key methodological point:** Distance indicates practical access, but it does not qualify an employer on its own. Staff scale, a reachable owner and relevance to education are stronger indicators.

**Visual:** Horizontal eight-stage pipeline. Highlight the evidence and human-review gates in Gold.

### Slide 4 — Three public sources provide complementary coverage

**Purpose:** Show what each source contributes and what it cannot provide.

| Source | Current coverage | Useful fields | Main limitation |
|---|---:|---|---|
| TATO | 476 safari and tour companies | 456 company emails, 459 company phone numbers, category and location | No reliable staff count; location descriptions often require geocoding |
| TCDC | 115 deduplicated SACCO/cooperative organisations | Registered organisation name, region/address and licence class | No named decision-makers in the source |
| OSM | 241 mapped employers within 25 km | Exact or approximate coordinates and employer category | Usually lacks usable contacts and staff information |

**Visual:** Three source cards connected to a shared Silverleaf master database. Add a short note that the sources complement one another and may overlap.

### Slide 5 — Contact enrichment shows the largest remaining gaps

**Purpose:** Separate broad organisational coverage from outreach readiness.

**Content:**

- 313 named contacts are associated with organisations linked to TATO source files.
- TCDC supplies no named personal contacts; SACCO records require website, phone or field enrichment.
- OSM supplies no named personal contacts directly; mapped employers require organisation-level research.
- A further 29 contacts came through other website and manual enrichment.
- The master currently contains 342 published business-contact records across 161 organisations.
- The initial deep-enrichment shortlist covered 62 priority organisations; 40 had a named senior contact, 49 had a direct email and 50 had a Tanzanian phone number.

**Visual:** Coverage-to-readiness funnel, followed by a small gap chart for TATO, TCDC and OSM. Do not imply that a source with zero named contacts has zero usable company channels.

### Slide 6 — The partnership pitch gives employers a simple way to help their staff

**Purpose:** Explain the value exchange and message construction.

**Core pitch:** Silverleaf Academy can give an organisation's staff a clear, low-effort way to understand nearby education options. Silverleaf provides approved information and handles parent questions. The organisation routes the proposal to the right owner and, where appropriate, shares it through an internal staff channel.

**Message structure:**

- **Hook:** One current, verified fact about the organisation when it materially supports the proposal.
- **Relevance:** Why the offer may help the organisation's staff or members.
- **Offer:** Approved information pack, admissions Q&A or campus introduction.
- **Ask:** Route Silverleaf to the correct HR, staff-welfare or partnership owner, or consider sharing the material internally.

**Controls:** Do not promise discounts, reserved places, transport availability, scholarship access or formal employee benefits without current approval.

**Visual:** Annotated example message with four colour-coded sections. Use one verified-hook example and one direct-opening example.

### Slide 7 — Short, reply-aware sequences will run through Resend

**Purpose:** Show the proposed automation logic and delivery layer.

**Content:**

- **AQ00 hold:** 215 records need more evidence or a usable route. No message is sent.
- **AQ01 routing-first:** 651 records receive a short routing request and one check-in after five working days.
- **AQ02 direct-recipient test:** 61 records receive an initial proposal, a follow-up after four working days and a final close after another four working days.
- Segments select the offer and cadence; recipient-level fields personalise the final copy.
- Replies, bounces, unsubscribe requests and do-not-contact instructions stop further outreach.
- Resend will hold the approved templates and deliver the emails. Delivery outcomes and suppression events return to the master data workflow.

**Visual:** Compact branching sequence beside a cropped, branded frame of the supplied Resend Templates screenshot:
`C:\Users\wanen\AppData\Local\Temp\codex-clipboard-fad7bb89-a75a-4f5a-8f89-dc5853b01ff0.png`

### Slide 8 — Content and the website create the parent audience

**Purpose:** Explain how Track 2 generates first-party parent leads.

**Journey:**

1. Social media content and paid campaigns create awareness around real parent needs.
2. Each campaign links to a relevant Silverleaf landing page rather than a generic homepage.
3. The page offers a useful newsletter or update subscription through a pop-up or embedded form.
4. The form states what the person will receive and records the acquisition source and consent status.
5. Approved sign-ups enter the parent audience list.
6. Parent-specific messages guide the person towards an enquiry, campus visit, application or enrolment.

**Potential content themes:** Admissions guidance, school-readiness information, campus updates, and notifications when approved scholarships, bursaries or fee discounts become available.

**Visual:** Full-funnel journey from social post or advertisement to website form, audience list and admissions outcome. Show measurement points for landing-page conversion, form completion and enrolment progression.

### Slide 9 — Parent acquisition needs privacy controls from the first click

**Purpose:** Make the compliance and trust requirements operational.

**Content:**

- Display a clear privacy notice and state the specific purpose of the newsletter or campaign form.
- Collect only the information needed for the stated purpose.
- Record source, notice version, timestamp and consent or other approved processing basis.
- Provide an easy unsubscribe or withdrawal route and honour direct-marketing objections.
- Define access, retention, deletion and security controls.
- Confirm Silverleaf's controller/processor registration, Data Protection Officer responsibilities and internal policies.
- Review Resend's processing locations, contractual terms and any required transborder-transfer steps before activation.
- Have Silverleaf's responsible data-protection owner validate the exact form language and operating process.

**Visual:** Privacy-by-design checklist embedded around the parent funnel. Keep the tone practical rather than legalistic.

**Official basis:**

- Tanzania Personal Data Protection Act, Cap. 44: https://www.pdpc.go.tz/media/media/THE_PERSONAL_DATA_PROTECTION_ACT.pdf
- Personal Data Protection Commission privacy principles: https://pdpc.go.tz/privacy-notice/
- Personal Data Protection Commission registration and compliance notice: https://www.pdpc.go.tz/media/media/PUBLIC_NOTICE_MARCH_2026.pdf

### Slide 10 — The architecture supports refreshes and new campaign criteria

**Purpose:** Show that the work is reusable rather than a one-off list.

**Architecture:**

`public/raw evidence → interim normalisation → local SQLite master → XLSX review → approved Resend audience/export → outcomes returned to the master`

**Refresh and rerun options:**

- Update an existing list while preserving IDs, evidence and prior decisions.
- Create a separate list for a new sector, locality or campaign.
- Change source mix, campus coordinates, distance bands, organisation types, qualification thresholds or evidence-age rules.
- Re-run deduplication, geocoding, enrichment, message generation and workbook export.
- Use the repository's create-list and update-list skills so another agent follows the same data contract and verification gates.

**Next activation priorities:** Confirm exact campus coordinates, enrich TCDC and other employer contacts, approve the live partnership offer, validate the parent consent flow, configure Resend, and run a small reviewed pilot.

**Visual:** Layered architecture diagram with refresh loops and a small activation checklist.

## Silverleaf visual system

- Use a 16:9 widescreen canvas.
- Use Electric Blue `#002368` as the primary colour, supported by Light Blue `#80BFEC`, White `#FFFFFF` and Silver `#818283`.
- Use Gold `#FFC952` sparingly for important figures and review gates.
- Use Montserrat for headings and body copy. Use Georgia selectively for short supporting statements. Use Noteworthy only for an occasional statistic or annotation.
- Place the Silverleaf brandmark at the bottom-left with the required clear space. Use the internal-document brandmark treatment unless the deck becomes an external presentation.
- Use subtle Silverleaf or beehive pattern elements on low-density slides.
- Keep charts flat, clean and legible. Avoid generic stock imagery where data, icons or a simple process diagram explain the point more clearly.
- Use direct, friendly UK English and write “Silverleaf Academy” on first reference.

## Build and verification notes

- Use the Silverleaf brand guidelines and `references/Marketing Documents/PPT design 3.pptx` as visual references when building the final presentation.
- Use the supplied Resend screenshot only on the Resend slide, cropped to remove unrelated browser chrome where possible.
- Add compact source notes to the relevant slide footers instead of creating an eleventh references slide.
- Verify all figures against the current SQLite database immediately before generating the final presentation.
- Render every slide for visual inspection and check for overflow, unreadable labels, incorrect logo treatment and unsupported claims.
