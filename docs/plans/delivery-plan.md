# Silverleaf Agentic Marketing System — Delivery Plan

**Prepared:** 20 August 2026
**Status:** Internal working plan. The client-facing document is *Silverleaf Academy — Scope of Work: Agentic Marketing System*.
**Inputs:** Silverleaf Business Context Dossier · Marketing Observations · Marketing & Partnerships Department Process Map (Erick, Aug 2026) · Silverleaf BPR Tech & Automation Project 2026 workbook

---

## 1. Confirmed Parameters

| Decision | Setting | Rationale |
|---|---|---|
| Interface | Cowork desktop + git sync underneath | Team is two non-technical people. Git is right architecturally but must be invisible. |
| Scope | Content & campaign engine, extended to cover as many of the ten Process Map processes as the architecture can carry | Erick's Process Map is the client's own framing and should be honoured |
| Business lines | Schools network only at launch | Fastest to value; architecture still structured to hold TTI and Government later |
| Timeline | **6 weeks** | Client urgency — Mourine: *"marketing period is now now… we need to move on all things marketing"* |
| Rate basis | USD 250/day blended | Mission-driven client, impact-funded |
| Permissions model | Egalitarian at launch | Amos's proposal, accepted — see Section 6 |
| Security posture | Productivity-leaning, with one non-negotiable carve-out | See Section 7 — child imagery is not a general PII question |

**The 6-week window is the dominant constraint.** Everything below is sized against it. Where something cannot fit, it is named as a Phase 2 candidate rather than quietly dropped.

---

## 2. The Problem in One Paragraph

Silverleaf's marketing function is two people — Erick Sarakikya and Mariam Haji — covering five campuses, an enrolment cycle with fixed intake windows, and a network that plans to more than double to 12 campuses by December 2028. Their own Process Map states the diagnosis: *"Most of these currently run across a mix of WhatsApp, email, and separate documents, which makes it hard to see status at a glance or hand work off cleanly."* Every campaign starts from zero context. The CEO briefs verbally or over WhatsApp, that briefing lives in one person's head, and when that person is unavailable the work stops. Nothing the team learns is captured anywhere reusable. The result is a department that is permanently at capacity and cannot absorb growth.

The fix is not more tools. It is a **shared, versioned, machine-readable context layer** that agents and humans both work from, which gets richer every time it is used.

---

## 3. Design Principles

These are load-bearing. Every build decision traces back to one of them.

### 3.1 Portability is a first-class requirement, not a nice-to-have
Amos's constraint: *"switching from Claude to ChatGPT or any other AI vendor will happen at near zero cost."*

How we achieve it:

| Layer | Choice | Why it ports |
|---|---|---|
| Storage | Plain Markdown + YAML frontmatter in a git repo | Readable by any model, any editor, any human. No database. |
| Instruction layer | `AGENTS.md` at root, with `CLAUDE.md` as a pointer file | `AGENTS.md` is the emerging cross-vendor convention; Claude, Cursor, Codex and others read it |
| Skills | Markdown files with YAML frontmatter in `skills/`, mirrored to `.claude/skills/` | The mirror is a copy, not a dependency. Delete it and the markdown still works as a prompt. |
| Assets | Referenced by path or URL, never embedded in a proprietary format | — |
| Memory | Written to files in `intelligence/`, never to a vendor-hosted memory feature | This is the single biggest lock-in trap and we avoid it entirely |
| Retrieval | Folder structure + naming conventions + grep | No embeddings, no vector DB, no provider-specific index |

**Acceptance test.** We will run an identical brief through a second vendor's agent against the same repo and demonstrate comparable output. This goes in the SOW as a named acceptance criterion. It converts "no lock-in" from a claim into something demonstrated.

**Deliberate exclusion:** no vector database and no embeddings at launch. For a repo of a few hundred markdown files, folder structure and filename conventions outperform semantic search and cost nothing. Revisit past ~1,000 documents.

### 3.2 The system must compound
Objective 1 is that *"the system keeps learning about the business, customers and benefactors over time as it is used."*

A file store does not compound. Compounding requires a deliberate **capture step** that is enforced by the methodology, not left to discipline. Mechanism:

- Every completed campaign triggers a mandatory retro write to `intelligence/campaign-log.md`
- The agent is instructed never to close a campaign without appending: what was published, what performed, what the audience responded to, what to do differently
- Recurring observations get promoted from the log into durable files — `intelligence/audience-insights.md`, `intelligence/channel-performance.md`, `intelligence/objections.md`
- Parent objections encountered during enrolment season get logged and become answer material for the next season

The test of whether it is working: **campaign N+1 should need less briefing than campaign N.** That is measurable and it is in the metrics set.

### 3.3 One brief, everyone sees it
Objective 2 is that the CEO briefs once, into the system, and the whole team has it.

Mechanism: `briefs/` folder with a fixed template. The CEO (or a campus director) drops a brief in — dictated to Cowork in plain language, the agent structures it. On push, everyone has it. The agent reads it as the authoritative source for every asset it generates. No re-briefing, no telephone game, no "what did Krupa actually mean".

This also solves a problem the Process Map does not name: **campus directors currently have no route to request marketing support.** Five campuses, no intake channel. The briefs folder becomes that channel.

### 3.4 Sync must be automatic and boring
Objective 3 is that the system is always in sync.

Protocol, encoded in `AGENTS.md` and executed by the agent, not the human:

1. **Pull first, always.** No work begins before the agent fetches and rebases.
2. **Push on completion.** Every session ends with a commit and push.
3. **Conflict avoidance by structure.** One folder per campaign, one file per asset, dated filenames. Two people editing the same file is designed out rather than resolved.
4. **Conflict resolution where unavoidable.** `.gitattributes` sets `merge=union` on append-only logs (`intelligence/campaign-log.md`, the metrics ledger) so concurrent appends both survive.
5. **Failure is loud.** If push fails, the agent tells the user in plain language and does not silently continue.

### 3.5 Build for two people, not for a department
Every workflow must be completable by one non-technical person in a single Cowork session. If a process needs a handoff to work, it will not survive contact with a two-person team in enrolment season.

---

## 4. Repository Architecture

```
silverleaf-marketing/
│
├── AGENTS.md                    ← master methodology, vendor-neutral
├── CLAUDE.md                    ← pointer: "read AGENTS.md"
├── README.md                    ← human onboarding, plain language
├── .gitattributes               ← union-merge rules for append-only logs
│
├── brand/
│   ├── brand-guide.md           ← visual identity, logo rules, colour, typography
│   ├── brand-language.md        ← tone, voice, vocabulary, banned phrases
│   ├── messaging-house.md       ← core claims, proof points, the ONE agreed number per claim
│   ├── boilerplate.md           ← approved standing descriptions of Silverleaf
│   └── assets/                  ← logos, brand marks (small files only)
│
├── audiences/
│   ├── segments.md              ← the five segments already defined in the Process Map
│   ├── personas/                ← one file per persona, deepens over time
│   └── objections.md            ← real objections heard, with approved responses
│
├── context/
│   ├── business-context.md      ← distilled from the Dossier
│   ├── campuses/                ← one file per campus: levels, fees, facilities, staff, catchment
│   ├── fees-and-admissions.md   ← single source of truth for fees and intake windows
│   └── calendar-anchors.md      ← intake windows, term dates, national holidays, event anchors
│
├── briefs/
│   ├── _template.md
│   ├── active/
│   └── archive/
│
├── campaigns/
│   └── 2026-10-primary-intake/  ← one folder per campaign
│       ├── campaign.md          ← frontmatter: status, owner, approver, dates, channels
│       ├── plan.md
│       ├── email/
│       ├── facebook/
│       ├── instagram/
│       ├── linkedin/
│       ├── whatsapp/
│       ├── sms/
│       ├── x/
│       ├── print/
│       └── results.md           ← written at close; feeds intelligence/
│
├── calendar/
│   ├── content-calendar.md      ← rolling, forward-looking
│   └── published-log.md         ← what actually went out, append-only
│
├── templates/
│   ├── posters/
│   ├── social/
│   ├── email/
│   └── documents/
│
├── events/
│   ├── _template.md
│   └── {event}/                 ← brief → promo → registration → attendance → follow-up → outcome
│
├── partnerships/
│   ├── pipeline.md              ← Prospect → Contacted → Engaged → Negotiating → Active → Producing
│   └── partners/                ← one file per partner, full relationship history
│
├── web/
│   ├── change-requests/         ← request → approval → update → QA → publish → monitor
│   ├── site-map.md
│   └── geo-strategy.md          ← Generative Engine Optimization
│
├── reporting/
│   ├── metrics-ledger.md        ← append-only, the additionality record
│   ├── monthly/
│   └── dashboard.md
│
├── intelligence/                ← THE COMPOUNDING LAYER
│   ├── campaign-log.md          ← append-only retro entries
│   ├── audience-insights.md
│   ├── channel-performance.md
│   ├── what-works.md
│   └── decisions.md             ← why we chose what we chose
│
├── skills/                      ← vendor-neutral workflow instructions
│   ├── write-campaign-brief.md
│   ├── build-campaign.md
│   ├── write-social-post.md
│   ├── plan-content-calendar.md
│   ├── run-event.md
│   ├── request-web-change.md
│   ├── monthly-report.md
│   ├── manage-partnership.md
│   ├── capture-learning.md
│   └── brand-check.md
│
├── .claude/skills/              ← mirror of skills/, generated not authored
│
└── resources/                   ← inbox for anything the CEO or team drops in
```

**Note on `resources/`.** Amos's structure has this as a share-anything inbox. Keep it deliberately loose — the friction of deciding where something goes is exactly what stops people contributing. The methodology instructs the agent to periodically triage `resources/` into the right home and tell the user what it moved.

**Note on binaries.** Tanzanian bandwidth is a real constraint and git handles large binaries badly. Rule: the repo holds text, plus logos and small templates. Photography, video and large design files stay in Google Drive (already in the stack, Paul owns it) and are referenced by link in markdown. Revisit git-lfs only if it becomes a genuine blocker.

---

## 5. Process Coverage — Erick's Ten

Erick's Process Map is the client's own articulation and the SOW should map to it explicitly rather than substituting our own taxonomy.

| # | Process Map process | Coverage | How |
|---|---|---|---|
| 1 | Marketing Planning & Campaign Management | **Full** | `briefs/` + `campaigns/` + `campaign.md` frontmatter status. Live status visible by reading the repo. |
| 2 | Content Planning & Publishing | **Full** | `calendar/` + `skills/plan-content-calendar.md` + `published-log.md`. Delivers the "planned vs actually published" comparison the Process Map asks for. |
| 3 | Enrollment Lead Management | **Interface only** | The one genuine exclusion. Needs a CRM and probably WhatsApp Business API — out of a 6-week content engagement. We define the handoff: campaigns carry source tags, and the repo holds the lead-capture spec so a CRM build slots in later. |
| 4 | Campaign Lead Generation & Conversion | **Partial** | UTM and source-tagging convention applied to every campaign at build time, so attribution becomes possible the moment a CRM exists. Without a CRM we can track to inquiry, not to enrolment. |
| 5 | Parent Communication & Engagement | **Full** | `audiences/segments.md` (the five segments are already defined) + per-segment campaign generation + `campaigns/*/whatsapp|email|sms` |
| 6 | Event & Community Activation | **Full** | `events/` with the full chain the Process Map specifies: opportunity → plan → budget → promo → registration → attendance → leads → follow-up → outcome |
| 7 | Website & Digital Content Management | **Full** | `web/change-requests/` with the request → approval → update → QA → publish → monitor path. Plus GEO. |
| 8 | Marketing Performance & Reporting | **Full** | `reporting/` + `skills/monthly-report.md`. Agent assembles the report; human supplies platform numbers. |
| 9 | Partnership & Outreach Management | **Full** | `partnerships/pipeline.md` using the six stages already defined by Silverleaf |
| 10 | Marketing Asset & Brand Management | **Full** | `brand/` + `templates/` + `skills/brand-check.md`. Directly answers *"Stop the team from repeatedly asking where a file is, which version is final, and who approved it."* |

**Nine of ten covered, one scoped as an interface.** That is a strong answer to Erick's own document and it should be said plainly in the SOW.

**Cross-reference to the BPR workbook** (Marketing & Admissions, 13 processes): this engagement covers 3.5 Digital Marketing, 3.6 Marketing Events, 3.7 Mass Communications, 3.9 Community Engagement, 3.12 Data Analytics & Performance Tracking, 3.14 Parent Experience & Retention (content side), and part of 3.3 Partnerships. It does not cover 3.1, 3.2, 3.4, 3.11, 3.13 — all of which are CRM-dependent.

---

## 6. Egalitarian vs Hierarchical — Recommendation

**Agreed: start egalitarian.** Amos's reasoning holds and the evidence supports it.

Supporting facts:
- The department is two people. Roles and permissions for a team of two is pure overhead.
- Git-level permissions would require the team to understand branches and pull requests. That defeats the invisible-git principle.
- Marketing content is pre-publication material for public consumption. The blast radius of over-sharing inside a two-person team is near zero.

**But define the trigger conditions now**, so the decision to add structure is made on evidence rather than anxiety. Introduce roles when any of these occur:

1. Headcount in the repo exceeds ~8 people
2. A second business line (TTI or Government) joins, bringing genuinely different confidentiality needs
3. Campus directors get write access, taking the contributor count past the point where everyone knows everyone
4. Any material that is actually confidential needs to live in the repo — investor decks, board papers, fundraising pipeline

**Recommended middle path from day one, at near-zero cost:** a single private repo, everyone with write access, but a `restricted/` folder that is git-ignored by convention and documented as "never commit here." Costs one line in `.gitignore` and one paragraph in `AGENTS.md`. It gives a place to say no without building an access model.

---

## 7. Security vs Productivity — Recommendation, With One Carve-Out

**Broadly agreed: lean to productivity.** The reasoning is sound. Marketing output is public-facing by definition, PII redaction across multiple models is technically hard and easy to get wrong, and heavy controls on a two-person team will simply be routed around — the work will go back to WhatsApp.

**But there is one thing that is not a general PII question and should not be traded against productivity: images and names of children.**

Silverleaf's own `/our-model` page states that a child protection policy sits at the core of staff training. The organisation posts photographs of identifiable minors to Instagram near-daily. That is normal for a school, and it is normal precisely because schools maintain a media consent register.

If a repository of child photography and student names is created without a consent register attached, a real safeguarding and reputational exposure is created — during a live fundraise, with an independent Dalberg evaluation running, and with a government partnership in progress. This is not a hypothetical compliance concern; it is the kind of thing that ends partnerships.

**The proposal is deliberately light — this is not a security programme:**

1. `brand/media-consent.md` — a register mapping each student whose image is in use to their consent status, refreshed annually at enrolment
2. One rule in `AGENTS.md`: no student image is used in any asset without a consent entry. The agent checks and refuses.
3. `restricted/` is git-ignored: no student records, no parent contact lists, no financial data, no safeguarding material
4. Student first names only in public content, never full names with campus and class

Cost: roughly half a day. It is the cheapest risk reduction available in the whole engagement and it strengthens rather than weakens the GEO position, because content that is safe to publish is content that gets published.

**On GEO.** Amos's point is right and under-exploited. Silverleaf's website gets an estimated 231 monthly visits and the `/news` page is live and completely empty. Parents in Arusha are increasingly going to ask an AI assistant "what are the good English-medium primary schools in Arusha" rather than a search engine. Being citable — structured, factual, consistent, published — is a genuine acquisition channel and it is close to free once the content engine exists. `web/geo-strategy.md` covers it, and it is the strongest argument for fixing the metrics contradictions in Section 11 of the Dossier: **an AI engine that finds three different SEL scores on one site will not confidently cite any of them.**

---

## 8. Approval Chains

Amos's open question: who is accountable, how do they approve, where are approvals critical?

**Principle: approvals live in the file, not in a workflow engine.** A separate approval tool is another system to sync and another thing to lock into.

Every campaign carries YAML frontmatter:

```yaml
status: draft | in-review | approved | scheduled | published | closed
owner: Erick Sarakikya
approver: Krupa Patel
approved_by:
approved_at:
channels: [instagram, facebook, whatsapp]
brief: briefs/active/2026-10-primary-intake.md
```

`AGENTS.md` instructs the agent: **never move a campaign to `scheduled` unless `approved_by` and `approved_at` are populated.** The agent enforces the gate; the human makes the judgement. Git history gives a complete audit trail for free.

**Proposed RACI — to be confirmed in the kickoff workshop, not assumed:**

| Decision | Accountable | Consulted | Gate required? |
|---|---|---|---|
| Campaign strategy and budget | CEO (Krupa Patel) | Marketing, campus heads | **Yes** — before build |
| Campaign creative and copy | Marketing & Comms (Erick) | Campus head where campus-specific | **Yes** — before publish |
| Fee, admissions or academic claims | Director of Schools (Julius Kimani) | Finance | **Yes** — non-negotiable, factual accuracy |
| Use of student images | Campus Head Teacher | Head of Student Experience (Pascaline Sarakikya) | **Yes** — consent check |
| Routine social post on approved theme | Marketing (Erick) | — | **No** — deliberately ungated |
| Partnership outreach | Marketing & Partnerships (Mariam) | CEO for MOU stage | **Yes** — at proposal/MOU only |
| Website content change | Marketing | Paul Victor for publish | **Yes** — QA before publish |
| Monthly performance report | Marketing | — | **No** |

**Design intent: six gates, deliberately few.** The gates cover money, factual accuracy, child imagery, anything that commits the organisation externally, and the two publishing steps where an error becomes public. Everything else runs ungated, because an approval chain that gates routine work will be bypassed within two weeks and then stops providing assurance.

---

## 9. Metrics — Proving Additionality

Amos named the core one: time from brief to published. Build outward from it.

**Capture method:** `reporting/metrics-ledger.md`, append-only, union-merged. The agent writes an entry at each state transition automatically — it already knows when a brief landed and when a campaign was marked published. **No manual timekeeping**, because manual timekeeping does not happen.

### Primary — cycle time
| Metric | Definition | Baseline | Target |
|---|---|---|---|
| **Brief → first draft** | Brief committed → first campaign asset committed | Capture in week 1 | Under 4 working hours |
| **Brief → approved** | Brief committed → `status: approved` | Capture in week 1 | Under 3 working days |
| **Brief → published** | Brief committed → `status: published` | Capture in week 1 | Under 5 working days |
| **Approval turnaround** | `in-review` → `approved` | Capture in week 1 | Under 24 hours |

### Secondary — throughput and leverage
| Metric | Why it matters |
|---|---|
| Campaigns published per month | Raw output of a two-person team |
| Assets produced per campaign | Multi-channel coverage per unit of effort |
| Channels covered per campaign | Are they reaching all six channels or just Instagram? |
| Rework rate | Assets revised after review — proxy for context quality |
| **Context reuse rate** | % of campaigns built without net-new briefing. **This is the compounding metric.** Should climb every month. |

### Tertiary — quality and coverage
| Metric | Why it matters |
|---|---|
| Brand consistency score | Sampled audit against `brand-check.md` |
| % campaigns with source tagging | Attribution readiness for the future CRM |
| Intelligence entries per month | Is the compounding layer actually being fed? |
| Metric contradictions outstanding | Counts down from 7 (Dossier Section 11) to 0 |
| Content calendar adherence | Planned vs published — the Process Map's own asked-for output |

### Business outcome — attributable but not solely owned
Inquiries by source, inquiry → application rate, applications per intake window, cost per inquiry. **Caveat to state plainly in the SOW: without a CRM these are partially observable. We can measure to inquiry, not through to enrolment.** Claiming enrolment attribution without a CRM would be dishonest and would not survive scrutiny.

**Baseline is a week 1 deliverable and it is non-negotiable.** Without it there is no additionality story, only assertion. Method: reconstruct the last three campaigns from WhatsApp, email and Erick's recollection. Rough is fine; absent is not.

---

## 10. Six-Week Delivery Plan

### Phase 1 — Foundation (Weeks 1–2, 15 days)

| WS | Work | Days |
|---|---|---|
| W0 | Mobilisation and discovery. Kickoff workshop. Confirm RACI. Walk the current process with Erick and Mariam. **Capture the baseline.** Collect brand guide, templates, channel access, past campaigns. | 4 |
| W1 | Repository architecture. Create repo, folder structure, `.gitattributes`, `.gitignore`, sync protocol. Configure Cowork on team machines. Prove pull → work → push end to end. | 5 |
| W2 | Context foundation. Author `brand/`, `audiences/`, `context/`. Reconcile the seven metric contradictions into `messaging-house.md`. Build `media-consent.md`. | 6 |

**Gate 1 (end week 2):** a team member opens Cowork, asks a question about Silverleaf, and gets a correct, brand-consistent answer from the repo. If this does not work, do not proceed.

### Phase 2 — Build (Weeks 3–4, 20 days)

| WS | Work | Days |
|---|---|---|
| W3 | Methodology layer. `AGENTS.md`, `CLAUDE.md`, `README.md`. Sync protocol, capture protocol, approval enforcement, folder semantics. This is the highest-leverage artefact in the build. | 7 |
| W4 | Workflow skills — the ten in `skills/`, mapped to Erick's ten processes. Each tested against a real Silverleaf scenario, not a toy one. | 10 |
| W5 | Approval and governance layer. Frontmatter schema, gate enforcement, `restricted/` convention, consent check. | 3 |

**Gate 2 (end week 4):** a real brief goes in and a complete multi-channel campaign comes out, brand-checked and approval-gated, built by Erick rather than by us.

### Phase 3 — Adoption (Weeks 5–6, 12 days)

| WS | Work | Days |
|---|---|---|
| W6 | Metrics and reporting. Ledger, automatic capture at state transitions, monthly report skill, `dashboard.md`. | 4 |
| W7 | Enablement. Two hands-on sessions with Erick and Mariam. One session with CEO and campus directors on briefing. Plain-language runbook. Run the live October intake campaign together as the training vehicle. | 5 |
| W8 | Portability validation and handover. Second-vendor test. Failure-mode runbook. 30/60/90 roadmap. | 3 |

**Gate 3 (end week 6):** the team runs a full campaign unaided, and the portability test passes.

**Total: 47 person-days.**

### Effort and indicative pricing (superseded — see revision note below)

| Phase | Days | USD @ 250/day |
|---|---|---|
| Phase 1 — Foundation | 15 | 3,750 |
| Phase 2 — Build | 20 | 5,000 |
| Phase 3 — Adoption | 12 | 3,000 |
| **Total** | **47** | **11,750** |

**Optional, priced separately:**

| Item | Days | USD |
|---|---|---|
| Post-launch support, 3 days/month × 3 months | 9 | 2,250 |
| GEO content sprint (fill the empty `/news` page, structured publishing) | 5 | 1,250 |
| Enrollment Lead Management / CRM — Process Map #3 | TBD | Separate SOW |
| TTI and Government business lines | TBD | Follow-on engagement |

---

### REVISION NOTE — 20 August 2026: labour capped at USD 600, day rate reduced to USD 50

Two commercial changes were made after this plan was drafted. Labour is capped at **USD 600**, and the day rate drops from USD 250 to **USD 50**. Tooling is quoted separately, above labour, rather than folded into a single figure.

At USD 50 per day the cap buys **12 consultant-days**, delivered over **3 weeks**. The 47-day model above is retained as the reference for a fully resourced delivery. The issued SOW (v2.1) is built to the capped figure.

**What changed:**

| | Full model | Capped model (SOW v2.1) |
|---|---|---|
| Duration | 6 weeks | 3 weeks |
| Consultant effort | 47 days | 12 days |
| Day rate | USD 250 | USD 50 |
| Labour | USD 11,750 | USD 600 |
| Tooling | Not separately quoted | USD 40, quoted above labour |
| Total | USD 11,750 | USD 640 |
| Discovery | Kickoff workshop plus full process walk-through | Kickoff workshop, condensed |
| Baseline | We capture it | We capture it with the team |
| Training | 3 sessions plus co-delivery of the October campaign | 2 sessions, one recorded. Co-delivery is an extension. |
| Portability test | We run it | We run it |
| Consent register | Built and populated | Built; the campuses populate it |
| Brand guide | Authored if absent (+3 days) | Starter built from website and collateral; full guide is an extension |
| Iteration after handover | Included | Optional extension |

**Stage split inside the 12 days:** Foundation 4, Build 5, Adoption 3.

**Why 12 days is feasible.** The research groundwork is already complete. The Process Map, the BPR workbook and the business context dossier supply what a discovery phase would otherwise have to produce, and the build itself is largely agent-executed from that material. Consultant time goes into design decisions, testing and enablement rather than production.

**What this raises.** Adoption risk. Twelve days buys a working system and two training sessions, not months of hand-holding. Mitigations are the recorded session, the runbook, and a repository seeded with real context so the first use is immediately useful. Adoption support is offered as an extension at 1 day per month for 3 months.

**Optional extensions repriced at USD 50 per day:** adoption support 3 days / 150 · co-delivery of the October campaign 2 days / 100 · brand guide authoring 3 days / 150 · GEO content sprint 5 days / 250.

**Ongoing run rate for Silverleaf after delivery:** GitHub free, plus USD 40 per month for two Claude Pro seats. Claude Team starts at USD 25 per seat per month with a five-seat minimum, so it becomes the better option once the department reaches five users.

### Document build

The repository retains the Markdown delivery plan as the editable source. Generate a presentation copy only when one is needed for delivery, and place temporary renders outside the source tree.

---

## 11. Dependencies on Silverleaf

Blocking items are genuinely blocking and the SOW should say so.

| # | Dependency | Owner | Needed by | Blocking? |
|---|---|---|---|---|
| 1 | **Brand guide** | Erick | Week 1 | **Yes** — if none exists we build one, +3 days |
| 2 | **Branding templates** (posters, social) | Erick | Week 1 | **Yes** — same |
| 3 | Named decision-maker per approval gate | Nelly Zablon / CEO | Week 1 | **Yes** |
| 4 | GitHub organisation and accounts | Paul Victor | Week 1 | **Yes** |
| 5 | Cowork installed on team machines | Paul Victor | Week 1 | **Yes** |
| 6 | Last 3 campaigns for baseline | Erick | Week 1 | **Yes** — no baseline, no additionality |
| 7 | Read access to Instagram, Facebook, LinkedIn, YouTube, Buffer analytics | Erick | Week 2 | Partially |
| 8 | Current enrolment numbers by campus | Nelly Zablon | Week 2 | No, but degrades targeting |
| 9 | Decision on the 7 contradictory metrics | CEO | Week 2 | **Yes** for `messaging-house.md` |
| 10 | Media consent position | Head of Student Experience | Week 2 | **Yes** for image use |
| 11 | Erick and Mariam available ~1 day/week | Nelly Zablon | Throughout | **Yes** — this is a build-with, not a build-for |

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Adoption fails; team reverts to WhatsApp** | Medium | **Fatal** | Build with them, not for them. Train on the live October campaign. Make the first win obvious in week 2. |
| Git conflicts frustrate non-technical users | Medium | High | Structural avoidance, union merge, agent-mediated sync, plain-language failure messages |
| Bandwidth makes sync painful | Medium | Medium | Text-only repo. Binaries in Drive by reference. |
| No brand guide exists | **High** | Medium | Priced as a contingency, +3 days |
| Two-person team has no capacity during enrolment season | **High** | High | 1 day/week commitment agreed up front. Sequence so week 5–6 training *is* the October campaign work. |
| Scope creep toward CRM | High | Medium | CRM named as an explicit exclusion with a defined interface and a separate SOW |
| Approval gates ignored | Medium | Medium | Only four gates. Agent enforces rather than reminds. |
| Metric contradictions propagate into automated content | **High** | Medium | `messaging-house.md` as single source of truth, week 2 |
| Child imagery used without consent | Medium | **High** | Consent register + agent refusal, week 2 |
| 6 weeks proves too tight | Medium | Medium | Phase gates. Phase 1 alone delivers standalone value if 2 and 3 slip. |
| Key-person dependency on Erick | Medium | High | The repo *is* the mitigation — it externalises what is currently in his head |

---

## 13. What This Explicitly Does Not Do

Stating exclusions clearly protects both sides.

- **No CRM.** Process Map #3 and BPR 3.1, 3.2, 3.4, 3.13 are out. Interface defined, build separate.
- **No WhatsApp Business API.** Approval timelines alone exceed the window.
- **No paid advertising.** And a recommendation not to start until attribution exists.
- **No website rebuild.** Wix stays. We manage the change process, not the platform.
- **No Ed-admin integration.** The website↔Ed-admin gap is real and important but it is an admissions systems job, not a marketing content job. Flag it, do not scope it.
- **No TTI or Government marketing** at launch. Architecture holds them; content does not yet.
- **No auto-publishing to channels** in phase 1. Human presses publish. Buffer stays. Revisit once trust is established.

---

## 14. What Makes This Compound Rather Than Just Tidy

Worth being explicit, because it is the difference between this and a shared Drive folder.

1. **Every campaign ends by writing what it learned.** Enforced by the methodology, not by discipline.
2. **Context is authored once and read by every future campaign.** Fee changes are made in one file and every subsequent asset is correct.
3. **The brief becomes the durable artefact.** The CEO's intent is captured in text, not in a WhatsApp voice note that expires from memory in a fortnight.
4. **Git history is institutional memory.** Why a claim was worded a particular way is recoverable eighteen months later.
5. **Onboarding collapses.** The Social Media Manager they are currently hiring reads the repo instead of shadowing Erick for six weeks.
6. **It survives Erick leaving.** Currently, most of the department's operating knowledge would leave with him.

---

## 15. Open Questions for the Kickoff Workshop

1. Does a brand guide exist in any form, or are we authoring one?
2. Who holds final approval on fee and admissions claims — Julius Kimani or Nelly Zablon?
3. Is there a media consent register today, in any form?
4. Which of the seven contradictory metrics is correct in each case? (Needs the CEO.)
5. Do campus directors get repo write access at launch, or do they submit briefs through Erick?
6. Is Buffer staying, or should scheduling be reconsidered once the calendar lives in the repo?
7. Who owns the repo after handover — Erick (marketing) or Paul Victor (Data, Tech & MEL)?
8. What are the actual enrolment targets per campus for the October–December 2026 intake?
9. Is there a marketing budget for the October intake, and does the system need to track spend?
10. Confirm: is the six-week window firm, or is the real deadline the October intake window opening?
