# Scope of Work

## Agentic Marketing System for Silverleaf Academy

| | |
|---|---|
| **Prepared for** | Silverleaf Academy, Usa River, Arusha |
| **Date** | 20 August 2026 |
| **Engagement** | Design and delivery of an agentic marketing system for the Marketing & Partnerships department |
| **Duration** | 3 weeks |
| **Investment** | USD 40 tooling, plus USD 700 labour |
| **Version** | 1.0 (for review) |

---

## 1. Executive Summary

Silverleaf's Marketing & Partnerships department is two people covering five campuses, two fixed primary intake windows, a rolling daycare and pre-primary intake, and a network planning to reach twelve campuses by December 2028. The department's own Process Map describes the situation clearly:

> *"Most of these currently run across a mix of WhatsApp, email, and separate documents, which makes it hard to see status at a glance or hand work off cleanly."*

The practical consequence is that every campaign starts from nothing. Context lives in people's heads and in WhatsApp threads that nobody can search six months later. What the team learns during one enrolment season is not available to them in the next.

This engagement builds a shared marketing context system that people and AI agents both work from, and that becomes more capable each time it is used. A brief goes in once. Campaign assets come out across every channel, on brand, with the right approvals recorded. What the campaign taught the organisation is captured as part of closing it out.

Four commitments shape the design.

**The system accumulates knowledge.** It learns about the business, its parents, its campuses and its partners as a by-product of ordinary use, without anyone having to run a separate documentation exercise.

**A brief is written once and reaches everyone.** The CEO or a campus director records what they want. The whole team and every agent has it from that point on, with no re-briefing.

**Everything stays in sync automatically.** The agent handles it. The person doing the work does not have to think about it.

**There is no vendor lock-in.** The system is plain text in a git repository. Moving from one AI provider to another means pointing a different tool at the same folder.

The engagement is priced at **USD 700 of labour**, delivered as 14 consultant-days at USD 50 per day over three weeks, with **USD 40 of tooling** shown separately in Section 12. Section 12 also sets out what the budget covers and what it leaves to Silverleaf.

---

## 2. Objectives

| # | Objective | How the system delivers it | How success is measured |
|---|---|---|---|
| 1 | The system keeps learning about the business, its customers and its benefactors as it is used | A capture step at the close of every campaign writes structured findings into a shared intelligence layer | Context reuse rate rises month on month, and each campaign needs less briefing than the one before |
| 2 | The CEO briefs once and the whole team has it | Structured briefs live in the shared repository and are read by every agent as the authoritative source | Brief to first draft under 1 working hour, with no repeat briefing cycles |
| 3 | The system stays in sync at all times | The agent pulls before starting work and pushes on completion, without the user having to intervene | No incidents of work built on stale context |
| 4 | Switching AI vendors costs close to nothing | Plain Markdown in git, with no proprietary formats, no vendor-hosted memory and no vector database | The same brief run through a second vendor produces comparable output |

---

## 3. Where Things Stand Today

This section draws on Silverleaf's own documents, principally the Marketing & Partnerships Department Process Map (August 2026) and the BPR Tech & Automation 2026 workbook, supplemented by publicly available information.

### 3.1 The team

Two people carry the department: **Erick Sarakikya** (Marketing & Comms Associate) and **Mariam Haji** (Marketing & Partnership Associate). Two further roles are open, a Social Media Manager and a Fundraising & Partnerships Associate, which would take the department to four delivery roles.

Between them they cover five campuses across two regions, three business lines, seasonal and rolling enrolment cycles, and an active capital raise.

### 3.2 The tools in use

| System | Used for | Lead |
|---|---|---|
| Canva for Education | Design and marketing collateral | Erick Sarakikya |
| Buffer | Social scheduling and publishing | Erick Sarakikya |
| Wix | Public website | Paul Victor |
| WhatsApp | Day to day coordination, and in practice a significant share of parent inquiries | Lisa Franco (School Admin Associate, organisation-wide owner rather than a marketing role) |
| Google Workspace | Files, documents, forms | Paul Victor |
| Slack | Internal messaging and departmental channels | Paul Victor |
| Email | Formal correspondence, including external partners | Paul Victor |
| Ed-admin | School information system, including the online application module | Paul Victor |

There is no CRM and no marketing automation platform. The BPR workbook records this as a known gap, noting under item 3.13 that "leads and parent interactions are not tracked centrally."

### 3.3 How work moves at the moment

Campaign intent usually starts as a conversation or a WhatsApp message, and is then interpreted by whoever received it. Assets are produced in Canva and scheduled through Buffer. The record of what was planned against what actually went out exists mainly in people's recollection. Approvals happen in conversation, so there is no durable record of who signed off on what. When a campaign ends, nothing is written down, which means the next campaign begins with the same amount of organisational knowledge as the last one.

Campus heads currently have no defined route to request marketing support.

### 3.4 What this costs the department

**Every campaign is a standing start.** Fees, campus detail, tone, audience segments and proof points get re-explained each time.

**Knowledge is concentrated in individuals.** A meaningful part of how the department operates exists only in the memory of the people currently doing the work.

**There is no view of planned against published.** Closing this gap is something the Process Map explicitly asks for.

**Attribution is not currently possible.** The team posts near-daily, concentrated on Instagram, across six live channels, with no way to know which of them produced an inquiry.

**Events are not tracked through to outcome.** As the Process Map puts it, "An event isn't successful simply because it happened."

**Published figures do not agree with each other.** Silverleaf's website currently states its social-emotional development score as 96%, 94% and 86% on three different pages, and there are six comparable contradictions elsewhere in the published material. Automating content generation before resolving these would spread the inconsistency faster and into more places.

**Onboarding is slow.** The incoming Social Media Manager has no written material to start from.

---

## 4. The Solution

### 4.1 In short

A private git repository holding Silverleaf's marketing context as plain text, worked through Claude Cowork, with git synchronisation and approval enforcement handled by the agent so that the person using it never has to deal with either.

### 4.2 How a campaign will run

**How it works today.** The CEO explains a campaign in conversation or over WhatsApp. Whoever receives it interprets it, designs in Canva, schedules in Buffer, gets approval verbally, and the campaign runs. Nothing is recorded, so the next campaign starts from zero again.

**How it will work with the system:**

1. **Brief.** The CEO or a campus director speaks the brief into Cowork in plain language. The agent structures it using the standard template and commits it. Everyone has it on their next sync.

2. **Build.** Erick opens Cowork and asks for the campaign. The agent pulls the latest version of the repository, reads the brief alongside the brand guide, tone of voice, audience segments, campus context and fee schedule, then produces assets for each relevant channel: Instagram, Facebook, LinkedIn, WhatsApp, email, SMS, X and print.

3. **Check.** Before anything reaches a reviewer, the agent runs a brand and factual consistency check against the messaging house.

4. **Approve.** The approver is named in the campaign file. The agent will not move a campaign to scheduled until approval is recorded. Git history holds the audit trail.

5. **Publish.** A person publishes through Buffer and the existing channels. The system records what went out and when.

6. **Learn.** At close, the agent writes a structured record of what was published, how it performed, what the audience responded to, and what to change next time. This becomes input to every campaign that follows.

### 4.3 Why the system gets better over time

The difference between this and a well-organised shared drive is the capture step, which the methodology requires rather than leaving to good intentions.

Every campaign closes by writing what it learned into a structured intelligence layer. Where the same observation recurs, it gets promoted into a durable reference file covering audience insight, channel performance, or the objections parents actually raise together with approved responses. Business context is written once and read by every future campaign, so a change to the fee schedule is made in one file and every subsequent asset reflects it. Git history preserves the reasoning behind decisions, not only the decisions themselves.

The measurable expression of this is **context reuse rate**, meaning the proportion of campaigns produced without new briefing. It should climb every month.

### 4.4 Why there is no vendor lock-in

| Layer | Design choice | Why it ports |
|---|---|---|
| Storage | Markdown files in git | Readable by any model, any editor and any person. No database involved. |
| Instructions | `AGENTS.md`, the cross-vendor convention | Read by Claude, Cursor, Codex and others. `CLAUDE.md` is a one-line pointer to it. |
| Workflows | Markdown skill files | Work as plain prompts with any assistant |
| Memory | Written to files in the repository | Never held in a vendor-hosted memory feature, which is the most common lock-in trap |
| Retrieval | Folder structure and naming conventions | No embeddings and no vector database, so nothing is tied to a provider |

Switching vendors means pointing a different tool at the same folder. A portability test is run during handover and the result written up, and the method is documented so Silverleaf can repeat it at any time.

---

## 5. Architecture

### 5.1 Repository structure

```
silverleaf-marketing/
├── AGENTS.md            master methodology: how agents work here
├── CLAUDE.md            pointer to AGENTS.md
├── README.md            plain-language guide for people
│
├── brand/               brand guide, tone of voice, messaging house,
│                        boilerplate, logos, media consent register
├── audiences/           the five parent segments, personas, objections
├── context/             business context, per-campus detail, fees and
│                        admissions, calendar anchors
├── briefs/              incoming briefs from the CEO and campus directors
├── campaigns/           one folder per campaign, one subfolder per channel
├── calendar/            forward content calendar and published log
├── templates/           poster, social, email and document templates
├── events/              opportunity through to enrolment outcome
├── partnerships/        pipeline and per-partner relationship history
├── web/                 website change requests, GEO strategy
├── reporting/           metrics ledger, monthly reports, dashboard
├── intelligence/        the accumulating layer: what has been learned
├── skills/              the workflow instructions the agent follows
├── resources/           drop anything here and the agent files it
└── restricted/          excluded from version control by configuration
```

### 5.2 Synchronisation

The synchronisation protocol lives in `AGENTS.md` and is executed by the agent.

1. **Pull first.** No work begins until the latest repository state has been fetched.
2. **Push on completion.** Every session ends with a commit and a push.
3. **Conflicts avoided by structure.** One folder per campaign, one file per asset, dated filenames. Two people editing the same file is designed out rather than resolved after the fact.
4. **Automatic merge where unavoidable.** Append-only logs are configured so that concurrent entries both survive.
5. **Failures are visible.** If a sync fails, the user is told in ordinary language and work does not continue silently against stale context.

### 5.3 Bandwidth

The repository holds text, logos and small templates. Photography, video and large design files stay in Google Drive, which is already in the stack, and are referenced by link from the relevant markdown file. This keeps synchronisation quick on Tanzanian connections.

---

## 6. Process Coverage

Mapped against the ten processes in Silverleaf's Marketing & Partnerships Process Map.

Throughout this table, "full" means the content, workflow and record-keeping side of the process. It does not include automated sending or publishing, which Section 14 sets out as an exclusion.

| # | Process | Coverage | Delivered as |
|---|---|---|---|
| 1 | Marketing Planning & Campaign Management | Full (content and workflow) | Briefs and campaign folders carrying live status, so campaign state is visible by reading the repository |
| 2 | Content Planning & Publishing | Full (content and workflow) | Content calendar, publishing workflow and published log, including the planned-against-published comparison the Process Map asks for. Scheduling stays in Buffer. |
| 3 | Enrollment Lead Management | Interface only | See the note below |
| 4 | Campaign Lead Generation & Conversion | Partial | Source and UTM tagging applied at build time on every campaign, so attribution becomes possible as soon as a CRM exists |
| 5 | Parent Communication & Engagement | Full (content and workflow) | The five existing segments, segment-specific generation, and content workflows for WhatsApp, email and SMS |
| 6 | Event & Community Activation Management | Full (content and workflow) | The full chain: identify opportunity, plan, budget, promotion, registration, attendance, leads, follow-up, enrolment outcome |
| 7 | Website & Digital Content Management | Full (content and workflow) | Change request, approval, update, QA, publish, monitor, report. Includes Generative Engine Optimization. |
| 8 | Marketing Performance & Reporting | Full for the reach, engagement and inquiry portion of the funnel | Metrics ledger, monthly reporting workflow, dashboard. Application and enrolment stages require a CRM, as noted in Section 9. |
| 9 | Partnership & Outreach Management | Full (content and workflow) | Pipeline using Silverleaf's existing six stages, with per-partner history |
| 10 | Marketing Asset & Brand Management | Full for text-based and template assets | Brand system, template library and automated brand checking. Photography and video are referenced from Google Drive rather than held in the repository. Directly addresses the objective to "stop the team from repeatedly asking where a file is, which version is final, and who approved it." |

**Eight processes covered in full for content and workflow, one covered in part, one scoped as a defined interface.**

### A note on Enrollment Lead Management

Process 3 is the one process this engagement does not build, and that is worth stating plainly, because Silverleaf's own Process Map marks it "HIGHEST PRIORITY FOR SILVERLEAF" and proposes it as one of the two starting points.

That assessment is correct. The reason it sits outside this scope is that doing it properly requires a CRM decision and almost certainly WhatsApp Business API access, where the approval timeline on its own would exceed this engagement several times over.

What this engagement does instead is prepare the ground. Every campaign carries source and UTM tagging from the day it is built, so when a CRM does arrive the attribution data is already there. The repository holds the lead capture specification, so a later build has a defined interface to connect to. The recommendation is to scope that work as a separate engagement.

### Cross-reference to the BPR workbook

Against the workbook's "3. Marketing" sheet, which numbers items 3.1 to 3.14 with 3.8 and 3.10 unused, giving twelve live items:

| Covered | Item | Note |
|---|---|---|
| Part | 3.3 Partnerships & Institutional Outreach | Pipeline and relationship history. Automated outreach sequences are not included. |
| Part | 3.5 Digital Marketing | Website content, social content calendar and GEO. Paid advertising and CRM-connected landing pages are excluded. |
| Yes | 3.6 Marketing Events | |
| Content only | 3.7 Mass Communications | Message content and segmentation. Automated sending flows require a CRM and WhatsApp Business API. |
| Yes | 3.9 Community Engagement | |
| Part | 3.12 Data Analytics & Performance Tracking | Reach, engagement and inquiry metrics. Conversion and enrolment tracking requires a CRM. |
| Content side | 3.14 Parent Experience & Retention | Welcome and newsletter content. Automated journeys and referral tracking require a CRM. |

Items 3.1, 3.2, 3.4, 3.11 and 3.13 are CRM-dependent and sit outside this scope.

---

## 7. Design Recommendations

Two structural choices shape how quickly the system can be delivered and how easy it will be to live with. The recommendations follow, with the reasoning set out so that Silverleaf can take a different view if it prefers.

### 7.1 Start egalitarian rather than hierarchical

**Recommendation:** everyone in the repository can read and write everything. Do not build roles and permissions at launch.

A permissions model for a team of two is overhead without benefit, and implementing it at the git level would require the team to understand branching and pull requests, which works against keeping git invisible. Marketing content is pre-publication material intended for public consumption, so the exposure from open access within a small team is low.

One low-cost safeguard is included. A `restricted/` folder is excluded from version control by configuration and documented as never-commit. That gives somewhere to put things that should not be shared, without building an access model to enforce it.

The suggestion is to agree now what would prompt a revisit, so the decision is later made on evidence:

- Contributors exceed roughly eight people
- A second business line joins with different confidentiality requirements
- Campus directors receive write access
- Material that is genuinely confidential, such as investor or board papers, needs to live in the repository

### 7.2 Favour productivity over control, with one exception

**Recommendation:** no PII redaction layer and no content inspection gateway.

Marketing output is public-facing by definition. Redaction across multiple models is difficult to implement reliably, and controls that slow a two-person team down during enrolment season tend to get routed around, which would put the work back into WhatsApp. This posture also supports Generative Engine Optimization, since content that is straightforward to produce and publish is content that actually gets published.

**The exception is images and names of children.**

Silverleaf's published material places a child protection policy at the core of staff training, and the organisation posts photographs of identifiable minors on a near-daily basis. That is normal practice for a school, and it works because schools maintain a media consent register. Building a repository of child photography without a consent register alongside it would create a safeguarding and reputational exposure at a point when a capital raise is live, an independent evaluation is running and a government partnership is in progress.

What is proposed here is small and included in the quoted labour:

1. A media consent register template mapping each student whose image is in use to their consent status, refreshed annually at enrolment
2. One rule in the methodology: no student image is used without a consent entry, and the agent declines if there is none
3. Student records, parent contact lists, financial data and safeguarding material excluded from the repository by configuration
4. Student first names only in public content, never a full name alongside campus and class

Populating the register with actual consent status is Silverleaf's to complete, since only the campuses hold that information.

### 7.3 Generative Engine Optimization

Parents increasingly ask an AI assistant rather than a search engine which schools to consider. Being consistently citable is becoming an acquisition channel of its own.

Silverleaf's website currently receives an estimated 231 monthly visits, and the news page is live with no articles on it. At the same time, the site publishes three different figures for the same performance metric. An AI engine that encounters contradictory figures on a single site is unlikely to cite any of them with confidence.

Resolving the seven identified contradictions into a single messaging house therefore serves two purposes at once. A GEO strategy file is included in the repository. Producing the content to act on it is available as a priced option.

---

## 8. Approval Chains

Approvals live in the campaign file rather than in a separate workflow tool. That keeps one fewer system to synchronise and one fewer vendor to depend on.

Each campaign carries a short structured header recording status, owner, named approver, approval timestamp, channels and source brief. The agent will not move a campaign to scheduled until approval is recorded, and git history provides the audit trail at no extra cost.

### Proposed accountability map, to be confirmed at kickoff

| Decision | Accountable | Consulted | Approval gate |
|---|---|---|---|
| Campaign strategy and budget | CEO | Marketing, campus heads | Yes, before build |
| Campaign creative and copy | Marketing & Comms | Campus head where campus-specific | Yes, before publish |
| Fee, admissions or academic claims | Director of Schools | Finance | Yes, factual accuracy |
| Use of student images | Campus Head Teacher | Head of Student Experience | Yes, consent check |
| Routine social post on an approved theme | Marketing | | No |
| Partnership outreach | Marketing & Partnerships | CEO at MOU stage | Yes, at proposal and MOU stages only |
| Website content change | Marketing | Data, Tech & MEL for publish | Yes, QA before publish |
| Monthly performance report | Marketing | | No |

The map is deliberately short. Six gates cover the decisions that carry real consequence: money, factual accuracy, child imagery, anything that commits the organisation externally, and the two publishing steps where an error becomes public. Routine work runs ungated by design, because an approval chain that slows down everyday activity tends to be bypassed, at which point it stops providing assurance.

---

## 9. Success Metrics

Metrics are captured automatically. The agent records each state transition, since it already knows when a brief arrived and when a campaign published, so nobody has to keep timesheets.

The baseline is captured by Silverleaf in week 1 using a template the consultant provides. The method is to reconstruct the last three campaigns from existing WhatsApp and email records, which will be approximate but sufficient. Without a baseline there is no way to demonstrate improvement later.

### Primary: cycle time

| Metric | Definition | Target |
|---|---|---|
| Brief to first draft | Brief received, to first campaign asset produced | Under 1 working hour |
| Brief to approved | Brief received, to approval recorded | Under 1 working day |
| Brief to published | Brief received, to live on channel | Under 2 working days |
| Approval turnaround | Submitted for review, to approved | Under 4 working hours |

### Secondary: throughput and leverage

| Metric | What it tells you |
|---|---|
| Campaigns published per month | Output of the department |
| Assets produced per campaign | Channel coverage per unit of effort |
| Channels covered per campaign | Whether reach is extending beyond Instagram |
| Rework rate | Assets revised after review, which indicates how good the underlying context is |
| Context reuse rate | Campaigns produced without new briefing. This is the measure of whether the system is accumulating knowledge. |

### Tertiary: quality and coverage

| Metric | What it tells you |
|---|---|
| Brand consistency score | Sampled audit against the brand system |
| Percentage of campaigns with source tagging | Attribution readiness for a future CRM |
| Intelligence entries per month | Whether the accumulating layer is being fed |
| Message contradictions outstanding | Counts down from seven to zero |
| Content calendar adherence | Planned against published |

### Business outcome

Inquiries by source, inquiry to application rate, applications per intake window, and cost per inquiry.

To be clear about the limits: without a CRM these are only partially observable. The system can measure through to inquiry but not through to enrolment. It is better to state that up front than to present enrolment attribution that would not withstand scrutiny.

---

## 10. Delivery Plan

Three weeks, three stages, 14 consultant-days. Each stage closes on something you can see working.

### Stage 1: Foundation, week 1 (5 days)

- Kickoff workshop with Erick and Mariam to walk the current process and confirm the accountability map
- Performance baseline captured with the team, reconstructing the last three campaigns
- Repository created with the full folder architecture, synchronisation configuration and merge rules
- Cowork configured on the team's machines, with the full sync cycle proven end to end
- Brand starter, tone of voice and audience segments authored
- Business and per-campus context library built

**Checkpoint.** A team member opens Cowork, asks a question about Silverleaf, and gets a correct, on-brand answer drawn from the repository.

### Stage 2: Build, week 2 (5 days)

- Methodology layer authored: `AGENTS.md`, `CLAUDE.md` and `README.md`, covering synchronisation, capture, approval enforcement and folder semantics
- Messaging house drafted, with the seven contradictory published metrics surfaced for Silverleaf's decision
- Ten workflow skills built, covering nine of the ten Process Map processes
- Brief and campaign templates across all eight channels
- Approval schema, restricted content rules and consent register implemented
- Partnership pipeline and event workflow built
- Metrics ledger established with automatic capture
- Each workflow tested against a real Silverleaf scenario

**Checkpoint.** A real brief goes in and a complete multi-channel campaign comes out, brand-checked and approval-gated, built by Erick rather than by the consultant.

### Stage 3: Adoption, week 3 (4 days)

- Hands-on session with Erick and Mariam, recorded so it can be replayed and reused for onboarding
- Briefing session with the CEO and campus directors on how to submit a brief
- Plain-language runbook covering everyday use and common failure modes
- Portability test run against a second AI vendor, with the result written up
- 30/60/90 day roadmap setting out what to extend first

**Checkpoint.** The team runs a full campaign without the consultant's involvement, and the portability test passes.

---

## 11. Deliverables

| # | Deliverable | Stage |
|:--|:------------------------------------------------------------------|:-----|
| 1 | Performance baseline report | 1 |
| 2 | Private git repository with the full folder architecture and sync configuration | 1 |
| 3 | Cowork configured on team machines with working synchronisation | 1 |
| 4 | Brand starter: tone of voice, messaging house, boilerplate | 1 |
| 5 | Audience segment library covering the five defined segments | 1 |
| 6 | Business and per-campus context library | 1 |
| 7 | `AGENTS.md` master methodology, vendor-neutral | 2 |
| 8 | `CLAUDE.md` and plain-language `README.md` | 2 |
| 9 | Media consent register and enforcement rule | 2 |
| 10 | Ten workflow skills covering nine of the ten Process Map processes | 2 |
| 11 | Brief and campaign templates across eight channels | 2 |
| 12 | Approval schema with agent-enforced gates | 2 |
| 13 | Partnership pipeline and event workflow | 2 |
| 14 | Metrics ledger with automatic capture | 2 |
| 15 | Recorded hands-on session for the marketing team | 3 |
| 16 | Briefing session for the CEO and campus directors | 3 |
| 17 | Plain-language runbook and failure-mode guide | 3 |
| 18 | Vendor portability test, run and written up | 3 |
| 19 | 30/60/90 day roadmap | 3 |

The messaging house at deliverable 4 surfaces the seven contradictory published metrics. Deciding which figure is correct in each case is Silverleaf's call, and Section 13 lists it as a dependency.

---

## 12. Investment

### 12.1 Tooling

Tooling is quoted separately from labour so that Silverleaf can see exactly what the system costs to run, independently of what it costs to build.

| Item | Basis | USD |
|:-----------------------------------------|:---------------------------------------|-----:|
| Claude subscriptions, 2 users | 2 seats at USD 20 per month, 3 weeks | 40 |
| GitHub, private repository | Free tier, unlimited collaborators | 0 |
| **Tooling total** | | **40** |

### 12.2 Labour

| Item | Basis | USD |
|:-----------------------------------------|:---------------------------------------|-----:|
| Design, build, testing and handover | 14 consultant-days at USD 50 per day | 700 |
| **Labour total** | | **700** |

### 12.3 Total

| Component | USD |
|:-----------------------------------------|-----:|
| Tooling | 40 |
| Labour | 700 |
| **Total engagement cost** | **740** |

Invoiced on completion. No milestone billing at this value.

### 12.4 Ongoing running costs after delivery

| Item | Cost |
|:-----------------------------------------|:---------------------------------------|
| GitHub, private repository, unlimited collaborators | Free |
| Claude Pro, USD 20 per user per month | USD 40 per month for 2 users |
| Buffer, Canva, Google Workspace | Already in the budget, unchanged |
| The system itself | No licence fee, no per-seat cost, nothing that scales with repository size |

The Claude Team plan starts at USD 25 per seat per month with a five-seat minimum, so it becomes the better option once the department reaches five users. At two people, individual Pro subscriptions are cheaper. Pricing should be confirmed at the point of purchase.

### 12.5 What the budget covers, and what it leaves to Silverleaf

**What makes 14 days sufficient.** The research groundwork is already complete. Silverleaf's Process Map, the BPR workbook and a completed business context study supply the source material a discovery phase would otherwise have to produce. The build itself is largely executed by agents working from that material, so consultant time goes into design decisions, testing and enablement rather than production.

**Included:**

- The complete system as described in Sections 4 to 8, working and populated with real Silverleaf context
- All nineteen deliverables in Section 11
- Two live sessions, one for the marketing team and one for leadership
- The portability test, run by the consultant

**Left to Silverleaf:**

| Item | Why |
|:-----------------------------------------|:---------------------------------------|
| Populating the media consent register | Only the campuses hold consent status. The consultant builds the register and the enforcement rule. |
| Deciding which of the seven contradictory published metrics is correct | This is a leadership call on what Silverleaf says about itself |
| Running the October intake campaign | Available as an extension if co-delivery would help |
| Ongoing iteration after handover | Available as an extension |
| Authoring a full brand guide, if none exists | A starter is built from the website and existing collateral. A full guide is an extension. |

**The residual risk is adoption.** Fourteen days buys a working system and two training sessions. It does not buy months of hand-holding through a new way of working. The recorded session, the runbook, and a repository seeded with real context are the mitigation. The support extension below is the fuller answer if adoption proves harder than expected.

### 12.6 Optional extensions

All priced at the same USD 50 per day.

| Item | Days | USD |
|:-----------------------------------------------------|-----:|-----:|
| Adoption support, 1 day per month for 3 months | 3 | 150 |
| Co-delivery of the October intake campaign | 2 | 100 |
| Brand guide authoring, if no usable guide exists | 3 | 150 |
| GEO content sprint: populate the news page, establish structured publishing | 5 | 250 |
| Enrollment Lead Management and CRM, covering Process Map item 3 | To be scoped | Separate scope of work |
| Extension to the Teacher Training Institute and Government lines | To be scoped | Follow-on engagement |

---

## 13. What Silverleaf Provides

| # | Item | Owner | Needed by | Blocking |
|:--|:---------------------------------------|:-------------------|:---------|:---------|
| 1 | Brand guide, in whatever form exists | Marketing | Week 1 | Yes. If none exists, a starter is built from the website and existing collateral, and a full guide is available as an extension. |
| 2 | Branding templates for posters and social | Marketing | Week 1 | Yes, on the same basis |
| 3 | GitHub organisation and team accounts | Data, Tech & MEL | Week 1 | Yes |
| 4 | Claude subscriptions active on team machines | Data, Tech & MEL | Week 1 | Yes |
| 5 | Attendance at the kickoff workshop | Marketing | Week 1 | Yes |
| 6 | Records of the last three campaigns, for the baseline | Marketing | Week 1 | Yes |
| 7 | Named decision-maker for each approval gate | Leadership | Week 1 | Yes |
| 8 | Decision on the seven contradictory published metrics | CEO | Week 2 | Yes |
| 9 | Position on media consent for student imagery | Student Experience | Week 2 | Yes |
| 10 | Read access to social channel and Buffer analytics | Marketing | Week 2 | Partial |
| 11 | Erick and Mariam available roughly half a day per week | Leadership | Throughout | Yes |
| 12 | CEO and campus directors available for one briefing session | Leadership | Week 3 | Yes |
| 13 | Current enrolment numbers and intake targets by campus | Leadership | Week 2 | No |

Item 11 is the one to protect. This is an engagement built with the team rather than for them, and the training sessions only work if the people who will use the system are in them.

---

## 14. Exclusions

**CRM and lead management.** Process Map item 3 and BPR items 3.1, 3.2, 3.4, 3.11 and 3.13. The interface is defined; the build is a separate engagement.

**WhatsApp Business API.** Approval timelines alone would exceed this engagement.

**Paid advertising.** Excluded, with a recommendation not to begin until attribution is in place, since spend without measurement gives you no feedback to act on.

**Website rebuild.** Wix stays. The engagement delivers the change process rather than the platform.

**Ed-admin integration.** The gap between the website and Ed-admin is real and worth addressing, but it belongs to admissions systems rather than marketing content. It is flagged here without being scoped.

**Teacher Training Institute and Government marketing.** The architecture accommodates both. Content and workflows do not cover them at launch.

**Automatic publishing to channels.** For the duration of this engagement, a person presses publish and Buffer remains in place. This is worth revisiting once the team has confidence in the system's output.

---

## 15. Key Risks

| Risk | Mitigation |
|:-----------------------------------------|:---------------------------------------|
| The team reverts to WhatsApp and adoption stalls | Build with the team rather than for them, two live sessions, a recorded walkthrough, a plain-language runbook, and a repository seeded with real context so the first use is immediately useful. Adoption support is available as an extension. |
| Three weeks is tight against the team's availability | Roughly half a day per week from Erick and Mariam, agreed at the outset |
| No usable brand guide exists | A starter is built from the website and existing collateral. A full guide is available as an extension. |
| Bandwidth makes synchronisation painful | Text-only repository, with large files referenced from Google Drive |
| Scope drifts toward CRM | Named exclusion with a defined interface and a separate scope of work |
| Approval gates get ignored | Six gates only, enforced by the agent rather than relying on people to remember |
| Contradictory metrics propagate into generated content | Messaging house drafted in stage 2, ahead of sustained content generation |
| Baseline is never captured, so improvement cannot be shown | Captured with the team in week 1, before the system goes live |

---

## 16. Why This Approach

**It is sized for the team that exists.** Two people, five campuses, one enrolment season. Every workflow can be completed by one non-technical person in a single sitting.

**It reduces key-person risk.** Knowledge that currently exists only in the department's collective memory becomes something the organisation owns. The incoming Social Media Manager can read the repository instead of learning by osmosis over several weeks.

**It scales with the network.** The architecture does not care whether there are five campuses or twelve. Adding a campus means adding a context file.

**It is genuinely portable.** No database, no vendor memory, no proprietary format. If a better model appears next year, Silverleaf points at it and carries on.

**It accumulates.** In six months the system will know more about Silverleaf's parents, campuses, channels and partners than any individual does, because it has been recording that knowledge every time it was used.

**It is affordable to run.** GitHub costs nothing. Two Claude subscriptions come to USD 40 a month. There is no platform fee, no per-seat licence on the system itself, and nothing that gets more expensive as the repository grows.

---

## 17. Next Steps

1. Review and confirm scope, approach and the USD 740 total
2. Confirm the accountability map in Section 8
3. Confirm the dependencies in Section 13, particularly the brand assets and GitHub access
4. Countersign, and work begins in week 1

---

**Reference documents**

- *Marketing & Partnerships: Department Process Map*, Silverleaf Academy, August 2026
- *Silverleaf BPR: Tech & Automation Project 2026* workbook
- Business context research baseline, available on request
