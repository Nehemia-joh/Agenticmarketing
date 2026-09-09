# Silverleaf Academy — Marketing Observations

**Prepared:** 20 August 2026
**Companion to:** *Silverleaf Academy — Business Context Dossier*
**Status:** Analysis and opinion. Nothing here is established fact — every observation is an inference drawn from the evidence in the dossier. Held separately by design so the factual baseline stays clean.

---

## 1. The Constraint That Should Shape Everything

The Marketing & Partnerships department is **two people** — Erick Sarakikya (Marketing & Comms) and Mariam Haji (Marketing & Partnerships) — covering:

- five campuses across two regions
- three distinct business lines with three different customers (parents, trainee teachers, governments)
- two seasonal primary intakes plus rolling daycare and pre-primary enrolment
- an active USD 2.2m equity raise
- a growth plan from 5 to 12 campuses in 28 months

Two more hires are pending (Social Media Manager, Fundraising & Partnerships Associate), which takes the team to four. That is still very small for the surface area.

This has a direct design consequence. Every automation decision should be tested against a single question: *does this reduce the number of things two people have to remember?* A system that is technically elegant but requires ongoing configuration, data hygiene or manual stage management will decay within a term. The team's current toolset — Canva, Buffer, WhatsApp, Google Sheets — tells you the realistic complexity ceiling.

**Implication for the SOW:** favour fewer, deeper automations over broad coverage. Ten half-built processes will perform worse than two that genuinely run themselves.

---

## 2. Where the Funnel Actually Leaks

Silverleaf has defined its funnel as **Inquiry → Tour → Application → Enrollment**. Reading the internal documents against the observable public setup, the leaks appear to be concentrated at the front and the back, not the middle.

### Capture is fragmented across at least six unconnected entry points
Website form (Wix) · Ed-admin online application portal · a separate Google Form · WhatsApp to campus numbers · direct calls to five different campus phone numbers · walk-ins.

Six doors, no shared doormat. The BPR workbook's own words on item 3.13: *"Leads and parent interactions are not tracked centrally, causing missed follow-ups, duplicated effort, and no visibility of the full parent journey."*

The most consequential single fact in the technology estate: **website↔Ed-admin integration is marked "Not Started."** The application form exists in the Ed-admin backend and works, but the website does not feed it. So the system of record has been built and the front door does not connect to it. Closing that gap is probably the highest-leverage, lowest-complexity item available — and it may be closer to configuration than to a build.

### WhatsApp is the real CRM and it is invisible
WhatsApp is listed as an official system serving "All" departments, owned by Lisa Franco (a School Admin Associate at Arusha City, not a marketing role). In a Tanzanian consumer context WhatsApp is almost certainly where the majority of genuine parent inquiries land. Every one of those conversations currently lives on a phone, unlogged, unassigned and invisible to reporting. Whatever CRM gets chosen, **if it does not ingest WhatsApp it will not reflect reality**, and the team will keep working out of the phone.

### Attribution is structurally impossible today
Near-daily Instagram posting to ~3,400 followers, a Facebook page, YouTube, TikTok, X, events, community activations, partnerships and walk-ins — with no way to tell which produced an enrolment. BPR item 3.4 names the symptom precisely: no defined stages, no visibility of drop-off, no ability to intervene at the right time.

Note that item 3.5 proposes launching paid advertising on Google and social. **Paid spend before attribution exists would be money spent blind.** Sequencing matters here: tracking first, then spend.

### Post-enrolment is where the quietest money is
BPR item 3.14: *"Once a family enrolls, structured engagement largely stops."* Retention is claimed at 97%, so this is not a crisis — but referral is entirely untapped. In an Arusha parent market, word of mouth is very likely the dominant real acquisition channel already, operating with zero instrumentation and zero deliberate encouragement. A referral programme is listed as *proposed*, not live.

---

## 3. The Feeder-Campus Conversion Gap

This may be the single largest missed opportunity visible in the structure, and it is not named as a process in either internal document.

Three of five campuses — **Kijenge, Ilboru, Boma** — offer daycare and pre-primary only. Every family at those campuses hits a hard wall at Standard 1 and must either transfer to Usa River or Arusha City, or leave the network.

What makes this unusual: the conversion event is **fully known in advance**. Silverleaf knows the child's name, age, exact transition date, the parent's contact details, their payment history, and that they have already chosen and paid Silverleaf for two or more years. There is no acquisition cost, no lead generation, no qualification.

Yet primary intake windows are fixed (October–December and June–July), and there is no described process that treats these families as a distinct pipeline. They currently flow into the same generic admissions funnel as a cold walk-in.

**Suggested framing for the SOW:** an internal-progression pipeline is a separate process from external lead management, with different messaging, a longer runway, and a triggerable date. It is the cheapest enrolment in the network and it is presently unmanaged. If any single automation should be modelled before the others, it is arguably this one.

---

## 4. Three Businesses, One Two-Person Department

The dossier separates the schools network, the Teacher Training Institute and the government programme. Marketing sits across all three, but the internal Process Map is written almost entirely around **school enrolment**. Neither internal document maps a teacher-recruitment funnel or a government-relationship pipeline.

Observations on each:

**Teacher Training Institute.** Applications run through a Google Form. No fees or programme durations are published anywhere on the site. The public statistics contradict each other by a factor of three (480+ graduates vs "140+ first cohorts" vs "2025: 85 teachers"). For a business line explicitly positioned to serve teachers *beyond* the Silverleaf network — i.e. a genuine external revenue line — this is under-built relative to its stated ambition. A prospective trainee cannot currently find out what it costs or how long it takes.

**Government partnerships.** This is a long-cycle, relationship-led, evaluation-gated sale with a Dalberg results workshop in Q3 2027 as the pivotal moment. It is closer to enterprise BD than to marketing, and it needs a stakeholder-and-milestone tracker rather than a lead funnel. BPR item 3.3 covers partnerships generically, but corporates, feeder schools and *government ministries* are not the same object and should probably not share a pipeline.

**Recommendation to raise before scoping:** ask explicitly whether the engagement covers all three business lines or the schools network only. The Process Map implies schools; the department's actual remit implies all three. This is a scope boundary worth settling in writing before any estimate is given.

---

## 5. The Fundraise Changes the Brief

The internal workbook shows USD 1.3m committed of a USD 2.2m raise, term sheets at final sign-off, disbursement in September, and a 900k gap with Acumen and HNWIs on the shortlist. The plan is 12 schools and 7,500 students by December 2028, breakeven 2029.

Two consequences for marketing:

**First, the growth curve is steep and near.** Going from 5 to 12 campuses in 28 months means roughly doubling enrolment operations while the department is still two to four people. A system sized for today's volume will be undersized within a year. Multi-campus and multi-region handling should be designed in from the start, not retrofitted — campus routing, per-campus reporting, and per-campus ownership need to exist on day one even if only five campuses use them.

**Second, marketing is currently invisible to investors.** LinkedIn has ~418 followers. The website gets an estimated ~231 monthly visits. There is a `/news` page that is live and completely empty. There is no press coverage in Disrupt Africa, TechCabal or ImpactAlpha. Meanwhile the organisation posts to Instagram twice a day.

The marketing effort is almost entirely B2C parent-facing lifestyle content, and almost nothing is investor- or institution-facing — during an active raise, with a Fundraising & Partnerships Associate being hired, and with pro-bono board seats being advertised specifically to attract fundraising capability. There is a real asymmetry between where the effort goes and where the capital comes from.

Whether that belongs in this engagement is a scope question, not a given. But it is worth naming, because a "marketing automation" brief scoped only to parent enrolment would leave it untouched.

---

## 6. Message Integrity Is a Risk Before Automation, Not After

Section 11 of the dossier lists seven contradictions inside Silverleaf's own published material — the SEL score appears as 96%, 94% and 86% on three different pages of the same website; teacher-training numbers vary by more than 3×; the 2030 targets differ between two pages; Arusha City's boarding status is stated both ways.

This matters more than it might appear. **Automation scales whatever you feed it.** If templated parent communications, campaign assets and investor materials are generated from an inconsistent set of numbers, the inconsistency propagates faster and into more places — including, eventually, an investor data room during a live raise.

BPR item 3.14 already proposes automated welcome journeys and newsletters. Those will draw on exactly this material.

**Suggested inclusion in the SOW:** a short, bounded messaging-and-metrics reconciliation exercise — one agreed figure per claim, one source of truth — as a prerequisite deliverable rather than a nice-to-have. It is cheap, it is fast, and it is much more expensive to fix after it has been templated into fifty automated touchpoints.

The related and larger gap: **current total student enrolment is not published anywhere**, in ten years of operation. Whether that is deliberate or simply never assembled, it is a striking absence for an organisation raising equity on a 7,500-student target.

---

## 7. Realistic Build Order

The internal Process Map already proposes starting with Enrollment Lead Management and Marketing Planning & Campaign Management. That instinct is right on the first and arguably wrong on the second — campaign planning is a coordination problem, and coordination tooling delivers less than pipeline tooling when the team is this small.

A sequence worth putting to them:

**Phase 1 — Make sure nothing is lost.** Connect the website form to Ed-admin (already built, not connected). Bring WhatsApp inquiries into a single logged queue. Auto-assign by campus with a named owner and a follow-up deadline. This is the "no inquiry is ever lost" objective from the Process Map, and it is achievable without a full CRM programme.

**Phase 2 — Make the funnel visible.** Inquiry → Tour → Application → Enrollment as tracked stages, with source captured at entry. This is what makes everything downstream — attribution, paid spend, campaign ROI, cost per lead — possible at all.

**Phase 3 — Work the known-value pipelines.** Feeder-campus progression (Section 3) and post-enrolment referral (Section 2). Both are warm, both are cheap, both are currently unmanaged.

**Phase 4 — Campaign management, content workflow, asset library, partnership pipeline.** Genuinely useful, but they optimise a department that first needs to stop losing leads.

**Explicitly not yet: paid advertising.** Until Phase 2 is live, paid spend cannot be measured and should not be recommended.

---

## 8. Points to Settle Before Estimating

Answers to these will move the level of effort materially. Worth putting to Silverleaf in writing before any number is committed.

1. **Scope boundary** — schools network only, or all three business lines (schools, TTI, government)?
2. **CRM decision** — is the intent to extend Ed-admin's admissions module, or introduce a dedicated CRM alongside it? This is the largest single cost driver and the answer is not currently determined.
3. **WhatsApp** — is WhatsApp Business API in scope? It is the difference between capturing most real inquiries and capturing a minority of them, and it carries its own cost and approval timeline.
4. **Three-month expectation** — the BPR workbook states priority items complete "within 3 months." Marketing does not currently appear on that cross-department priority list. Is marketing expected to run inside that window, after it, or in parallel?
5. **Who owns the system after handover?** Paul Victor (Data, Tech & MEL) is the realistic technical owner, but he already owns Slack, Email, Google Workspace, Ed-admin, Wix and Claude across all departments. Marketing owning its own system has different training and documentation implications than IT owning it.
6. **Current enrolment numbers** — needed to size anything. Not publicly available; must come from them.
7. **Existing tool commitments** — are Buffer, Canva and the RunShule/PayTan/QuickBooks stack fixed, or open to consolidation?
8. **The 12-campus plan** — should the system be built for 5 campuses and extended later, or built for 12 now? Cheaper now, much cheaper overall.

---

*All observations above are inference. The underlying facts, with sources, are in the companion Business Context Dossier.*
