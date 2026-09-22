# B2B government leads: plan to extend the lead tool

**Prepared:** 22 September 2026

**Status:** Plan. A first research run exists as a separate run (§10); the master, its schema and the shared intake contract are unchanged. Sending and automations remain disabled.

**Method:** Structured on the Standard Feature Work Methodology shared on 22 September 2026: study, confirm scope, plan, implement, test, document, close the loop. That text is not currently in the repository; the welfare plan's Phase 0 proposes the infrastructure it assumes.

**Companions:**
- `plans/b2b-welfare-leads-plan.md`, which specifies the shared Phase 0 (§4) and the pipeline traps (§2.2).
- `docs/methodology/partner-lead-generation.md`, which covers the corporate method and savings groups.
- `plans/lead-generation-progress-deck-plan.md`, which sets out the parent-acquisition track and privacy controls.

## 1. What a government lead is, and what it is not

The brief is to capture local government officials near the campuses who can convene community gatherings (barazas), so that Silverleaf can meet parents and generate parent leads.

**A government lead is a convening office.** It does not pay, as a welfare institution does, and it does not employ the parents, as a corporate partner does. Its value is access to a trusted forum where parents already gather. The leads it produces are parents who opt in with Silverleaf at the event.

| | Corporate (built) | Welfare (planned) | Government (this plan) |
|---|---|---|---|
| Who pays Silverleaf | The parent | The institution or its funder | The parent |
| What the lead is | A channel to staff | A buyer | The convener of a community forum |
| What it produces | Opted-in staff enquiries | Places filled | Opted-in parents from events |
| Unit of relationship | Organisation and HR route | Account | The office, not the person currently holding it |
| Channel | Email | Phone and visits | Formal letter, courtesy visit and phone, then an event |
| Language | English | The recipient's language | Kiswahili first |
| Largest risk | An unsupported hook | Children's data and safeguarding | Political neutrality, officials' personal data and parent consent |

### The Tanzanian forums behind "baraza"

| Forum | Convened by | Notes |
|---|---|---|
| Village assembly (*mkutano mkuu wa kijiji*) | Village chairperson, with the village executive officer (VEO) as secretary | Open to all residents aged 18 and over. Meets at least quarterly. Held in rural councils (Meru, Arusha District, Hai). |
| Mtaa meeting | Mtaa chairperson, with the mtaa executive officer (MEO) | Urban wards in Arusha City. Confirm how often these meet. |
| Ward public meeting | Ward executive officer (WEO), often with the councillor | The Ward Development Committee is a committee, not a public forum. |
| District or regional public meeting (*mkutano wa hadhara*) | District Commissioner or Regional Commissioner's office | Large, run by appointed officials, with formal protocol. Not a v1 target. |
| Government-organised public events | Council or region | Institutions can take stalls. Example: the 32nd Nane Nane Northern Zone exhibition at the Njiro grounds, August 2026. |
| Community development groups | Council and ward community development officers (CDOs) | Women's, youth and savings groups. Send savings groups to the corporate SACCOS campaign C02, not to this track. |

### Excluded from this track

- Party offices, party events, and official election campaign periods.
- Courts, police, prisons and the military.
- Health facilities, including clinics.
- Public-school parent meetings.
- Religious services. A separate track for faith-leader conveners could come later.
- Child-protection committees.

### Boundaries with other Silverleaf work

**The B2G business line is separate.** Silverleaf's Government & Institutional Partnerships line sells curriculum and AI coaching to ministries (MoEST, PO-RALG, TIE) through a long, relationship-led cycle. The Marketing Observations note argues that line needs a stakeholder tracker, not a lead funnel.
- This plan covers local convening for parent acquisition only.
- Before anyone contacts a regional or district education officer, they check with the B2G owner.

**This track is in scope.** The scope of work excludes "Government marketing", which means the B2G line. Community engagement (BPR 3.9) and Event & Community Activation (Process Map 6) are in scope, and this track belongs there.

**Council staff stay corporate.** A council is also a large employer. Staff information sessions for council employees stay in the corporate track (C01), coordinated so that no office is asked twice.

## 2. Study findings: current behaviour on 22 September 2026

This section records what exists today. Section 5 describes proposed behaviour.

### 2.1 The 29 `office:government` records

All 29 come from OpenStreetMap, and none has an outreach plan. They need very different treatment:

| Group | Records | Proposed treatment |
|---|---|---|
| Local administration offices (6) | Arusha District Commissioner's Office (2.0 km, Kijenge); Mwanama Village Office (1.9 km, Kijenge); Office ya Kijiji Maji ya Chai (5.7 km, Usa River); Narumu Ward Office (13.7 km, Boma Ng'ombe); Ofisi Ya Kata Nduruma (14.2 km, Usa River); Makiba Ward Building (18.3 km, Usa River) | Move to `government_convener` after verification |
| Political party offices (2) | Ofisi ya CCM Tawi la Engutoto (3.9 km); CCM office Kiserian (9.4 km) | Exclude; never contact |
| Court and police (2) | Mahakama Ya Mwanzo Nduruma; Kituo cha Polisi Baraa | Exclude from convening |
| Tagged as government but are not (3) | Njake Oil; Lutheran Center; Tumaini University Makumira Offices | Reclassify through review |
| Agencies and parastatals (16) | Including TRA, NSSF, TANESCO, TANAPA, NCAA, EAC, NIDA, TAWA, TAEC, Immigration, AUWASA and Temesa | Remain corporate employers |

### 2.2 Government-specific traps

These add to the shared pipeline traps in the welfare plan (§2.2): the refresh overwrite, track-ID drift, the module regex, three copies of the campus coordinates, two schemas, duplicated strategy documents and the committed workbook.

- **OpenStreetMap's `office=government` tag does not identify conveners.** It mixes party offices, courts, police, agencies and mistagged records.
- **Matching on domain first would merge offices.** Ward and village offices often share their council's domain, so a domain key would collapse them into one record.
- **Officials rotate between posts.** The current contact key (organisation plus name and role) would create a new contact at every transfer and orphan the relationship history.
- **Official websites are unstable.**
  - The Arusha City Council and Arusha District Council sites now run on a new framework ("GWF CORE").
  - On 22 September 2026, deep links redirected to the homepage, and fetches that did not render the page returned only its title.
  - Search engines still index an Arusha District Council publication, "Majina na namba za simu Maafisa Tarafa na Maafisa Watendaji wa Kata Halmashauri ya Arusha" (names and phone numbers of division officers and ward executive officers). Its URL no longer resolves.
- **The parent flows exist only as designs.**
  - C03/F06 (fresh opt-in) is recorded as "requires fresh opt-in feed; not activated".
  - C05/F07 needs confirmed events.
  - F04 covers the step from a session to an opt-in.
  - No consented store for parent contacts exists yet.
- **Language.** Silverleaf's positioning rules require Kiswahili for direct parent communication in print, digital and face to face, with native-language review.
- **Link to savings groups.** The corporate method (§5) already names ward and district community development officers as the route to VICOBA groups. This track can open up that segment.

### 2.3 External facts, checked 22 September 2026

- **Ward Development Committees.** Under the Local Government (District Authorities) Act 1982, each committee meets at least four times a year, and the WEO is its secretary.
- **Village assemblies.** The assembly includes all residents aged 18 and over and is expected to meet at least quarterly. Before quoting this externally, confirm the section in Cap. 287 R.E. 2023.
- **Census data.** The 2022 Population and Housing Census (Administrative Units Population Distribution Report) gives population by ward, and by village or mtaa where published.
- **Size of one council.** Meru District has 3 divisions, 17 wards, 69 villages and 275 hamlets, according to Wikipedia. Confirm with the council.
- **Personal Data Protection Act 2022**, as summarised by DLA Piper:
  - direct marketing needs explicit consent
  - data related to children is sensitive and needs prior written consent
  - data controllers must register with the Personal Data Protection Commission (PDPC)

## 3. Scope confirmation

This is an independent feature with its own documentation and tests. It shares only Phase 0 with the welfare track.

**Documentation home, to confirm before anything is created:** "This looks like a new function that is not yet covered in our documentation. I propose we create a new cluster/folder called `docs/government-leads/` and document it there. Do you agree or would you say otherwise?"

### Risks to handle from the start

- **Political neutrality.**
  - Approach administrative offices first.
  - No party offices, party events or campaign periods, and no claims of endorsement.
  - Engage elected leaders only through the official forum they chair.
- **Officials' personal data.**
  - Use office routes.
  - Record a holder's name only as officially published, or as the holder confirmed for this purpose.
  - Check tenure within 90 days before a convening request.
- **Parent data.**
  - Silverleaf captures it with explicit consent.
  - It never enters the master database, the workbook or the repository folder.
  - The master stores counts only.
- **Lists we never take.** No resident registers, voter lists, beneficiary lists or pupil lists, even when offered.
- **Anti-corruption.** No payments, allowances or gifts to officials. Pay any venue or refreshment cost to the institution against a receipt, under Silverleaf's finance policy.
- **Safeguarding.** No photographs of attendees or children without consent, under the media-consent rule in the scope of work (§7.2).
- **B2G coordination.** Check before any contact with education officers.

## 4. Dependency on Phase 0

Phase 0 is specified once, in `plans/b2b-welfare-leads-plan.md` §4. Build it first if the welfare track has not already done so.

This track adds only registry entries and pipeline stages to that foundation:
- **Acquisition tracks:** GA00, GA01 and GA02.
- **Value modules:** VM14 to VM18.
- **Segments:** "Local government office: council or district" and "Local government office: ward, village or mtaa".
- **Exclusion terms:** party names, courts, police, prisons, military, health facilities and schools.
- **Refresh rules** for `government_convener`.
- **Office stages in `account_pipeline`:**

  | Stage | Meaning |
  |---|---|
  | `prospect` | Office identified |
  | `letter_sent` | Formal introduction letter delivered |
  | `introduced` | Introduction and guidance recorded |
  | `convening_requested` | Agenda slot or meeting requested |
  | `convening_agreed` | Event confirmed in writing |
  | `event_held` | Session delivered |
  | `repeat_convener` | Office has hosted more than one session |

## 5. Functional plan for the government track

### 5.1 The local government structure the model uses

| Level | Office | Appointed or elected | Convening role | Verification |
|---|---|---|---|---|
| Region (*mkoa*) | Regional Commissioner's office; Regional Administrative Secretary | Presidential appointee; civil servant | Regional events and public meetings | Confirm per region |
| District (*wilaya*) | District Commissioner's office; District Administrative Secretary | Presidential appointee; civil servant | District public meetings | Confirm |
| Council (*halmashauri*) | Council director (City Director or District Executive Director); heads of community development, social welfare and education | Civil servants | Introductions, guidance and community development groups | Confirm on the council website |
| Division (*tarafa*) | Division officer (*afisa tarafa*) | Civil servant | Coordination across wards | Role confirmed by regional news on training for division officers and WEOs |
| Ward (*kata*) | WEO; councillor (*diwani*); ward community development officer | Civil servant; elected | Ward public meetings. The WEO is secretary to the Ward Development Committee. | The Act |
| Village (*kijiji*) | VEO; village chairperson | Civil servant; elected | Village assembly | Research; confirm the section of the Act |
| Mtaa (urban) | MEO; mtaa chairperson | Civil servant; elected | Mtaa meetings | Confirm under the Urban Authorities Act |
| Hamlet (*kitongoji*) | Hamlet chairperson | Elected | Small meetings | Not a v1 target |

**Councils in the catchment:**
- Arusha City Council, covering the Arusha City (Sakina), Kijenge and Ilboru campuses.
- Arusha District Council, which borders the city and falls within the city campuses' outer bands.
- Meru District Council, whose headquarters are at Usa River.
- Hai District Council, covering Boma Ng'ombe.

`campus_geo` will show whether Siha or Moshi District Council falls inside Boma Ng'ombe's outer bands.

### 5.2 Entities and schema (migration 0003)

| Entity | Storage | Identity key | Notes |
|---|---|---|---|
| Administrative unit | New `admin_units` table; intake record type `admin_unit` | Level, name, parent and council | Holds the 2022 census population with a page locator, the centroid and its precision, and the nearest campus with distance, band and OSM ID. |
| Government office | `organisations` with `lead_track = government_convener` and the level as subtype. A new `government_office_profiles` table holds the administrative unit, office level, published convening scope, protocol status and reference, and last-verified date. | Office level and administrative unit. Never a shared council domain. | |
| Official post | `contacts` as a role desk, plus a new `official_posts` table: office title, appointment type, holder name as officially published, holder-verified date and tenure source | Office and office title | A new holder is recorded as a new fact and a review item, not a new contact. |
| Community event | New `community_events` table; intake record type `community_event` | Event code | Counts only: stated expected attendance, attendance estimate and method, opt-ins, enquiries, tours, applications, enrolments and cost. |
| Parent opt-in | Outside the master and the repository, in the consented parent store (Track 2) | Not applicable | The master receives counts by event code only. |

The same tables are added to the create-skill initializer, so a separate government run works.

### 5.3 Sources and collection

| Source | Gives | Caveat | Evidence basis |
|---|---|---|---|
| Existing master (§2) | Six offices and the exclusions | Tags are unreliable | `reference_file` |
| Council and regional websites | Leadership, departments, ward lists, published officer lists and events | Pages render only in the browser and deep links are unstable. Capture the rendered page with its hash and date, or request the list in person. | `official` |
| 2022 census administrative-units report (National Bureau of Statistics) | Population by ward, and by village or mtaa where published | No age breakdown at ward level. Transcribe the pages with locators. | `official` |
| OpenStreetMap | Office locations and administrative boundaries where mapped | Tagging is mixed; apply the exclusions and log each one | `directory` |
| Courtesy visits and calls | Meeting calendars, preferred process and office lines | Record who gave the information and that they agreed to its use | `research_note` |
| Official event notices | Public events such as Nane Nane | Dates change each year | `official` or `published` |

**OpenStreetMap queries:**
- **Offices:** `office=government`, `amenity=townhall`, and names matching "Ofisi ya Kata", "Ofisi ya Kijiji", "Ofisi ya Mtaa", "Ward Office" or "Village Office", within 25 km of a campus.
- **Boundaries:** `boundary=administrative`, after checking which `admin_level` values Tanzania uses for wards.

**Exclusion list.** Held in the registry. It covers party names and terms such as CCM, CHADEMA, ACT-Wazalendo, CUF, *chama* and *tawi la*. It also covers *mahakama* (courts), *polisi* (police), *magereza* (prisons), JWTZ (the military), health facilities (*hospitali*, *zahanati*, *kituo cha afya*) and schools. Every exclusion is logged with its reason. Only a documented review decision can override one.

**Collectors:**
- `scripts/collection/collect_government_leads.py` queries Overpass and applies the exclusion log. It writes raw captures to `data/raw/government-research/` and candidates to `data/interim/government-leads/`.
- `scripts/collection/capture_official_pages.js` is a browser-console collector in the same pattern as `collect_partner_leads.js`. It saves the rendered text with the URL, a timestamp and a SHA-256 hash.
- `scripts/collection/load_census_wards.py` reads a transcription of the census pages for the catchment councils (`data/raw/government-research/nbs_2022_wards.csv`, with page locators). It checks that each council's ward populations add up to the published council total, then writes `admin_unit` intake rows.

Rows then follow the required order in `.claude/CLAUDE.md`: validate, preflight, transactional merge, export, build and verify.

**Rate limits for these sources.** These come from the welfare run and are documented in `skills/silverleaf-create-lead-list/references/research-rate-limits.md`.

| Source | Limit and handling |
|---|---|
| Web search | 200 searches per session, shared by every subagent. Plan per-agent allocations the way `scripts/welfare/plan_research.py` does, run collectors first, and use at most four agents per wave. |
| Council and regional sites (GWF CORE) | Pages render in JavaScript and deep links redirect, so plain fetches return only the title. Capture rendered pages one at a time with the user's go-ahead for the browser, or request officer lists in person. Never share the browser between agents. |
| OpenStreetMap Overpass | One query at a time, at least 5 seconds apart, small queries (broad regex queries return 504), mirror fallback. Reuse `polite_request` from `scripts/welfare/welfare_lib.py`. |
| Census report (NBS PDF) | One download, cached. Transcribe the catchment councils' pages once, with page locators. |
| Courtesy calls and visits | People, not tools, set this pace. Plan GA01 letters in batches the team can follow up within 5 working days. |

### 5.4 Data contract additions and validation

| Field | Values or rule |
|---|---|
| `lead_track` | `government_convener` |
| `admin_unit_level`, `admin_unit_name`, `parent_admin_unit`, `council_name` | Required for administrative-unit and office rows |
| `census_2022_population`, `census_source_location` | Integer as published; the page in the census report |
| `office_level` | `region`, `district`, `council`, `division`, `ward`, `village` or `mtaa` |
| `office_title` | For example *Afisa Mtendaji wa Kata*. Required for government contacts. |
| `appointment_type` | `civil_service`, `elected` or `political_appointee` |
| `holder_name`, `holder_verified_on`, `tenure_source_url` | The holder's name only as officially published or as confirmed for this purpose |
| `protocol_status`, `protocol_ref` | `none`, `letter_sent`, `introduced` or `declined`, plus the letter or approval reference |
| `event_code`, `event_type`, `event_date`, `event_status` and the count fields | `community_event` rows only |

**Validation rules:**
- An office name that matches the exclusion list is an error.
- A government contact needs `office_title` and `appointment_type`.
- A GA02 row needs `holder_verified_on` within the last 90 days.
- `organisation_domain` is rejected for offices below council level.
- A `community_event` row rejects every person-level field (names, phone numbers, emails and profile URLs) and accepts counts only.
- An official's phone number is accepted only if `channel_attribution` names an official publication or the holder's recorded permission.

### 5.5 Ward priority and acquisition tracks

**Ward score (0–100):**

| Factor | Weight |
|---|---:|
| 2022 census population, relative to other wards in the catchment | 30 |
| Transport band to a campus that offers the relevant levels. Daycare and pre-primary: all five campuses. Primary: Usa River and Arusha City. | 25 |
| Access readiness: an introduction is recorded with the council | 20 |
| Convening opportunity: a confirmed meeting or event within six weeks | 15 |
| Observed yield: opt-ins per 100 attendees at earlier events in the council (zero until measured) | 10 |

The score never uses political affiliation, ethnicity, religion or inferred income. The first three are sensitive data under the PDPA, and income is not evidenced.

**Acquisition tracks:**

| Track | Use when | Touches | Outcome |
|---|---|---|---|
| GA00 Hold | The office, post, holder or exclusion status is unresolved | None | Research, or close |
| GA01 Protocol introduction | A council or district office is verified | A formal letter in Kiswahili on Silverleaf letterhead, delivered by hand or to the official address. Call after 5 working days, then make a courtesy visit. Stop on refusal. | Guidance on wards and meeting calendars, and an introduction to the executive officers |
| GA02 Convening request | An introduction is recorded and the ward, village or mtaa post was verified within 90 days | A call or visit to learn the meeting calendar, then a written request for an agenda slot or a co-hosted parents' meeting. Confirm 7 days before. Stop on refusal. | A confirmed event |

**Notice periods.** The standard session materials are approved once, so a routine agenda slot needs only 7 days' notice for logistics. Bespoke events, such as stalls and co-hosted meetings, follow the event SOP's T-21 production clock.

### 5.6 Offer and value modules

| Module | Value to the convener or parent | Silverleaf contribution | Do not imply | Gate |
|---|---|---|---|---|
| VM14 Community education session | Practical, useful information for residents | A 15–20 minute talk in Kiswahili on school readiness, early learning at home, choosing a school and the admissions calendar | Government endorsement, or criticism of public schools | Content approved once, with native-speaker review |
| VM15 Take-home parent guide | Something parents keep | A one-page Kiswahili guide with the published levels, fees and intake windows | Scholarships or discounts, unless approved | Marketing and admissions approval |
| VM16 Voluntary opt-in | Parents decide whether to hear more | Silverleaf's own form, with a Kiswahili privacy notice. The office never collects or shares details. | That the office endorses signing up | Notice reviewed by the data protection officer or counsel, and the consented parent store is live |
| VM17 Aggregate feedback | Material for the office's own community reporting | Attendance and the number of follow-up requests, with no names, within 5 working days | Any obligation or performance claim | None |
| VM18 Approved scholarship or bursary information | Affordability | Details of an approved scheme | Any scheme that has not been approved | Blocked until approved, as for C07 |

VM04 (school fit) applies only after a parent opts in. VM05 (school experience) should be used sparingly.

**Example GA01 letter body** (native-speaker review required before use):

> **YAH: OMBI LA UTAMBULISHO ILI KUTOA ELIMU KWA WAZAZI KUHUSU MAANDALIZI YA WATOTO KUANZA SHULE**
>
> Silverleaf Academy ni shule binafsi yenye kampasi tano Arusha na Boma Ng'ombe, zinazotoa huduma ya kulelea watoto wadogo mchana (daycare), elimu ya awali na elimu ya msingi kwa Kiingereza. Tunaomba ushauri wako na barua ya utambulisho kwa Watendaji wa Kata husika ili, pale itakapofaa, tupewe muda mfupi katika mikutano ya wananchi. Tutatoa elimu fupi kwa Kiswahili kuhusu maandalizi ya mtoto kuanza shule na ratiba ya udahili, pamoja na kijitabu cha mzazi. Mzazi atakayependa taarifa zaidi atajaza fomu yetu kwa hiari yake. Hatutaomba orodha ya wakazi wala taarifa zozote za wakazi kutoka ofisi yako.

English meaning: the letter asks the council for advice and an introduction to the relevant ward executive officers, so that Silverleaf can take a short slot at community meetings where appropriate. It explains the Kiswahili school-readiness talk and the parent booklet, and states two things:
- parents fill in Silverleaf's form only if they choose to
- Silverleaf will never ask the office for resident lists or residents' information

Use the Silverleaf letterhead in `references/Marketing Documents/Copy of Letterhead Template 2023.docx`.

### 5.7 Flows and campaign (design only, disabled)

**F15: protocol and convening**

| Step | Trigger | Condition | Action | Stage |
|---:|---|---|---|---|
| 1 | Council or district office selected for GA01 | Exclusions clear; letter approved | Deliver the formal letter | `letter_sent` |
| 2 | No response after 5 working days | None | Call the office | `letter_sent` |
| 3 | After the call | None | Courtesy visit; record guidance and the introduction | `introduced` |
| 4 | Introduction recorded | Ward, village or mtaa post verified within 90 days | GA02: learn the meeting calendar and request a slot in writing | `convening_requested` |
| 5 | Slot agreed | Date, venue, minutes, language and presenter confirmed in writing | Create a `community_events` row and hand over to F16 | `convening_agreed` |

**F16: community session to parent opt-in**

| Step | Timing | Action | Record |
|---:|---|---|---|
| 1 | T-7 (T-21 for bespoke events) | Print the guide and forms with the event code; brief the presenter | Event `scheduled` |
| 2 | T-2 | Confirm logistics with the convener | None |
| 3 | Event day | Deliver VM14, hand out VM15 and offer the voluntary opt-in (VM16). Record the attendance estimate and how it was made. | `event_held` |
| 4 | Within 24 hours | Enter opt-ins into the consented parent store. Secure or destroy the paper forms under the retention policy. | `opt_ins_count` |
| 5 | After each opt-in (outside the master) | C03/F06 acknowledgement, then admissions qualification using F04 steps 3–5 | None |
| 6 | Weekly for 8 weeks | Pull aggregate enquiries, tours, applications and enrolments by event code | Count fields |
| 7 | Within 5 working days | Send a thank-you letter with aggregate feedback (VM17) | Office stage `event_held`, then `repeat_convener` if it hosts again |

**Stop or hold when:**
- an office declines
- an official election campaign period begins
- the event is cancelled
- anyone asks for payment or gifts: stop and escalate
- anyone offers resident, voter, beneficiary or pupil lists: refuse and record the refusal

**Inbound-only fallback.** If the consented parent store is not live, collect no contact details at events. Hand out the guide with Silverleaf's admissions number and online application link, and ask parents to quote the event code when they get in touch.

**Opt-in form fields**, for review by the data protection officer:
- parent's name
- phone number, and whether WhatsApp is preferred
- area (mtaa or village)
- level of interest: daycare, pre-primary or primary
- preferred campus
- consent statement and date
- event code

The form asks for the level of interest instead of a child's age, so it collects no children's data. Admissions asks about the child later in F06, within a relationship the parent consented to.

**Campaign C11: community convening via local government.** It stays inactive until all of these are in place:
- an introduction recorded with the council
- approved Kiswahili session content, guide and privacy notice
- a live consented parent store, or an explicit decision to run in inbound-only mode
- a presenter briefed on neutrality and safeguarding
- an approved materials budget
- the B2G owner informed

### 5.8 Workbook and verification

**Workbook sheets:**
- *Government offices*
- *Official posts*, showing official routes only
- *Administrative units*
- *Community events*, showing counts only

*Start here* shows counts by track.

**New `verify_master.py` checks:**
- No active plan targets an excluded office.
- Every GA02 plan has a holder verified within 90 days.
- `community_events` has no person-level columns.
- Counts are non-negative integers. Opt-ins above the attendance estimate produce a warning.
- Every module used is allowed for the plan's track.
- The master has no parent opt-in table.
- All automations are disabled.

### 5.9 Test plan

| Layer | Cases |
|---|---|
| Unit: `tests/unit/test_validate_government.py` | Each of these is rejected: a party-office name; a court or police office; a government contact without `office_title`; a GA02 row with a stale holder date; a ward office carrying the shared council domain; a `community_event` row with a phone field; an administrative unit without its council or page locator. |
| Unit: identity | Same office and office title with a new holder produces a match plus a review item. A new office title produces an insert. |
| Unit: census loader | Ward populations add up to each council total; a mismatch fails. |
| Unit: refresh | GA rows keep their tracks and modules, and the corporate golden output is unchanged. |
| Integration: master path | A fixture master is migrated to 0003, and the government fixture is preflighted. Matches, inserts and review items come out as expected, and excluded offices never reach an insert. The export includes the four new sheets. Verify passes on valid data and fails as designed on invalid data. |
| Integration: create path | A new government-only run initialises and passes the integrity checks. |
| Contract | The registry's exclusion terms match the documented list. VM14–VM18 and the GA tracks appear in both copies of the acquisition framework. The export has no person-level event fields. |
| Manual | Rehearse one session. A native speaker reviews the letter, guide and notice. The data protection officer or counsel reviews the form. |

Run `npm test`, then the update order in `.claude/CLAUDE.md`, finishing with `python scripts/master/verify_master.py`.

### 5.10 Build now, or add to `future-improvements.md`

**Build now:**
- Phase 0, if it is not built yet, and migration 0003.
- Administrative units for the four core councils.
- Triage of the 29 existing records.
- The office and post model, and the collectors.
- F15, F16 and C11, as design only.
- A pilot of up to four sessions, run by people rather than the tool, one per campus cluster: Arusha City with Kijenge and Ilboru, Usa River, and Boma Ng'ombe.

**Future improvements:**
- Coverage of Siha and Moshi.
- Automatic import of event outcomes from the parent store or CRM.
- A ward-yield model once ten or more events have run.
- A separate track for faith-leader conveners.
- Stalls at annual public events, such as Nane Nane in August 2027.
- WhatsApp Business API and SMS reminders for opted-in parents, following TCRA sender-ID rules.

### 5.11 Indicative sequence

| When | Work |
|---|---|
| Week 1 | Phase 0 if it is not built; migration 0003; administrative units; triage of existing records |
| Weeks 1–2, in parallel | People send GA01 letters to the Arusha City, Meru and Hai councils and prepare the Kiswahili session content, guide, notice and form. Silverleaf decides on the parent opt-in store. |
| Weeks 3–8 | First sessions from late October to November 2026, inside the October–December primary window. Daycare and pre-primary interest runs all year. |
| After four sessions | Review yield and cost per opt-in, then adjust the ward weights |

## 6. Documentation plan

After you confirm `docs/government-leads/`, create these files:
- `README.md`
- `architecture.md`
- `operations.md`, including the event-day checklist
- `future-improvements.md`
- `test-suite.md`

Then update:
- The data contract and the workbook layout.
- Both copies of the acquisition framework.
- The outreach skill: add convening offices to the role map, and add a `government-convening.md` reference with the Kiswahili templates.
- The create and update skills: track selection, plus a new `track-government.md`.
- The README repository map and the agent pointer files.

Finally, regenerate the schema snapshot and add any new learnings.

## 7. File map

| Path | Change |
|---|---|
| `skills/silverleaf-create-lead-list/references/controlled-vocabularies.json` | GA tracks, VM14–VM18, government segments and exclusion terms |
| `skills/silverleaf-create-lead-list/scripts/validate_intake.py` | Government, administrative-unit and event rules |
| `skills/silverleaf-create-lead-list/scripts/initialize_lead_db.py` | The migration 0003 tables |
| `skills/silverleaf-create-lead-list/assets/lead-intake-template.csv` | Government, administrative-unit and event columns |
| `skills/silverleaf-create-lead-list/references/lead-list-data-contract.md`, `workbook-layout.md`, `track-government.md` | Contract, sheets and research method |
| `skills/silverleaf-update-lead-list/scripts/preflight_update.py` | Identity keyed on office and post; a holder change goes to review |
| `skills/silverleaf-outreach/SKILL.md`, `references/government-convening.md` | Role map, modules, Kiswahili templates |
| `docs/strategy/new-lead-acquisition-framework.md` and its skill copy | GA tracks and VM14–VM18 |
| `scripts/master/migrations/0003_government.py` | New |
| `scripts/master/export_master_workbook_data.py`, `build_master_workbook.mjs`, `verify_master.py` | Government sheets and checks |
| `scripts/collection/collect_government_leads.py`, `capture_official_pages.js`, `load_census_wards.py` | New |
| `data/raw/government-research/`, `data/interim/government-leads/` | New evidence folders |
| `outputs/config/automation-recipes.json` | F15 and F16, disabled, with the GA schedule |
| `tests/unit/`, `tests/integration/`, `tests/fixtures/` | Government cases |
| `docs/government-leads/`, `docs/_learnings/`, `docs/database/` | Feature documentation after confirmation, learnings and the regenerated snapshot |

**Boundaries:**
- The B2G pipeline, the parent store (Track 2) and the corporate collectors do not change.
- Nothing sends a message or enables an automation.

## 8. Definition of done

- `npm test` passes, and so does `python scripts/master/verify_master.py` with its new checks.
- The before-and-after report reconciles counts, matches, inserts, exclusions and review items.
- Excluded offices have no plans.
- No parent's personal data is in the master, the workbook or the repository.
- No automation is enabled.
- The documentation and learnings are updated, and residual risks are stated.

## 9. Decisions needed from Silverleaf

1. **Ownership:** who owns this track, and who presents at sessions?
2. **B2G coordination:** who is the contact on the B2G side?
3. **Parent opt-in store:** will it be live before the first event, or do the pilot sessions run inbound-only?
4. **Data protection:** does the data protection officer or counsel approve the Kiswahili notice and form? Is Silverleaf registered with the PDPC? Does a first formal letter to a public office count as direct marketing?
5. **Event costs:** what are the budget and policy for event costs and for officials' requests for support?
6. **Pilot councils:** the proposal is Arusha City, Meru and Hai.
7. **Elected leaders:** can they be primary contacts, or only through their executive officers?
8. **Photography:** what is the policy at community events?
9. **Test commands:** npm or Yarn? This is the same decision as in the welfare plan.

## 10. First run (23 September 2026)

**What exists now.** The first run, `arusha-government-2026-09`, was built as a separate run: its own database and workbook under `outputs/runs/arusha-government-2026-09/`, with the company master unchanged. Its scripts live in `scripts/government/`, with an identical copy bundled in the `silverleaf-government-leads` skill, and every input is committed, so the run rebuilds without network calls. It needed no web search.

| Built | Count |
|---|---:|
| Convening offices | 149: 9 councils, 128 wards, 2 mapped village offices, 7 district and 3 regional offices |
| Proposed GA01 (protocol introduction) | 4: Arusha City, Arusha District, Meru and Hai councils |
| Official posts | 459, of which 66 name a holder as the office publishes it |
| Wards with 2022 census population | 221 across 10 councils; 113 within 25 km of a campus (1.75 million residents), scored and ranked by campus cluster |
| Office triage | 42 OpenStreetMap entries (7 exclusions logged) and the master's 29 `office:government` records, grouped as §2.1 proposes |
| Review items | 63 |

**How it differs from §5 and §7.** These choices keep the run separate until Phase 0 and migration 0003 exist:
- The four tables in §5.2 live in the run database, added by `scripts/government/augment_government_db.py`, not by the create skill's initializer. Administrative units are a side table, not an intake record type.
- Proposed GA tracks and VM14–VM18 sit in extra intake columns, because the shared validator accepts only AQ tracks and VM01–VM07.
- Collectors live in `scripts/government/` rather than `scripts/collection/`. The council sites are read through their public JSON API, so no browser capture was needed.
- Workbook sheets follow the create skill's layout: Organisations holds the government offices and Contacts the official posts, alongside Administrative Units and Community Events.
- Ward locations are estimates, because OpenStreetMap has no ward boundaries here; the rules are in the skill's data contract.

**Findings that change the plan.**
- **Councillor lists.** Hai publishes its ward councillors, and Arusha District publishes a scanned 2025–2030 list with phone numbers. Arusha City, Meru, Siha, Moshi District, Moshi Municipal, Monduli and Simanjiro do not publish ward-by-ward lists.
- **Executive officers.** No council publishes the names or phones of its ward, village or mtaa executive officers, so GA02 depends on the GA01 introduction.
- **Council contacts.** Only Moshi District and Moshi Municipal publish an email or postal address. The other councils publish their office location, so the GA01 letter goes by hand.
- **Siha, Moshi District, Moshi Municipal, Monduli and Simanjiro** have wards inside the catchment (§5.1 asked `campus_geo` to show this). They are included on hold, outside the pilot.
- **Master corrections** for the update skill: exclude the two CCM offices, the police station and the primary court; reclassify Njake Oil, Lutheran Center and Tumaini University Makumira Offices; the six local administration offices can move to `government_convener` after verification.

**Next steps.**
- Decisions 1–9 in §9 still gate any contact.
- Send the GA01 letters to the four core councils once they are reviewed. They are drafted on the run workbook's Outreach Plans sheet, in Kiswahili with an English meaning, with the family offer from `data/reference/silverleaf-offer-register.json` (23 September 2026).
- Ask each council for its ward councillor and executive officer lists and its meeting calendars.
- Resolve the 15 unlocated core-council wards.

## Sources

- [Local Government (District Authorities) Act, 1982 (TanzLII)](https://tanzlii.org/akn/tz/act/1982/7/eng@2002-07-31/source) · [Local Government (Urban Authorities) Act, 1982 (TanzLII)](https://media.tanzlii.org/media/legislation/316204/source_file/77e1e9a6b6ecb9fb/1982-8.pdf)
- [Selected experiences of the village assembly in Ludewa District Council (ResearchGate)](https://www.researchgate.net/publication/318541087_Selected_Experiences_of_the_Use_of_the_Village_Assembly_in_the_Governance_at_the_Grassroots_Levels_in_Ludewa_District_Council_in_Tanzania)
- [NBS: 2022 PHC Administrative Units Population Distribution Report](https://www.nbs.go.tz/nbs/takwimu/Census2022/Administrative_units_Population_Distribution_Report_Tanzania_volume1a.pdf)
- [Arusha City Council](https://arushacc.go.tz/) (Nane Nane news, checked 22 September 2026) · [Arusha District Council](https://www.arushadc.go.tz/) · [Meru District Council](https://www.merudc.go.tz/) · [Hai District Council](https://haidc.go.tz/)
- [Arusha Region: training for division officers and ward executive officers](https://arusha.go.tz/index.php/en/new/mafisa-tarafa-na-watendaji-wa-kata-mkoa-wa-arusha-wafundwa)
- [Meru District (Wikipedia)](https://en.wikipedia.org/wiki/Meru_District)
- [Personal Data Protection Act, 2022 (PDPC)](https://www.pdpc.go.tz/media/media/THE_PERSONAL_DATA_PROTECTION_ACT.pdf) · [DLA Piper: data protection laws of Tanzania](https://www.dlapiperdataprotection.com/?t=law&c=TZ)
- Internal:
  - `references/Silverleaf Academy - Business Context Dossier.md` §2.3 and §10
  - `references/Silverleaf Academy - Marketing Observations.md` §4
  - `docs/scope/scope-of-work.md`: process table and §14
  - `docs/strategy/campaign-positioning-and-cadence.md`: Kiswahili and event rules
  - `docs/methodology/partner-lead-generation.md` §5
  - the master database, as queried on 22 September 2026
