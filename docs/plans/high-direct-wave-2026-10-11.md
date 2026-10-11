# High-direct wave, 11 October 2026: plan (phase 1)

**Goal (approved by the user on 11 October 2026).** Grow the high-direct segments: `companies-high-direct` (30 now) and `welfare-high-direct` (12 now). For each lead in high-indirect or medium, find the named on-the-ground decision-maker's own published work email. Follow the master's recipient rule: the in-country lead first, a senior executive as escalation, and a chair only when no executive is named.

**Status.** This is a plan only. No web research was done, no database was changed and nothing was merged. A separate track for documenting email formats was added at the user's request (section 8). It depends on wording the user must approve.

**Inputs.** Read-only copies of the databases were taken from the main checkout:

| Database | sha256 |
|---|---|
| `outputs/master/Silverleaf Master Database.sqlite` | `f6cee695056b3abaa161488830e40e880e2c824d40802ce0dff4f46977f65426` |
| `outputs/runs/arusha-welfare-2026-09/lead-database.sqlite` | `39de65f4d61f622badbfdc33cdbda87b59b24b1dcd4bed985b6fb964b5d3b1e9` |

The main checkout's `runtime/contacts/profiles.json` and `runtime/contacts/http-cache/` were also read, read-only.

**Base.** The worktree `HEAD` is `1c76fbf`, the same as `main`, so no reset was needed.

**Analysis script (read-only, committed with this plan).** `scripts/contacts/analyse_high_direct_pool.py --runtime <main checkout>/runtime --detail runtime/analysis/high-direct-pool.json`

- It builds the segments with the exporter's own row builders (`company_rows`, `welfare_rows`, `dedupe`). Every count below is therefore the exporter's count.
- It re-reads every cached crawl page offline with the crawler's own extractor (`contact_lib.extract`). It never touches the network.
- The detail file holds names and addresses, so it stays in `runtime/` and is never committed.

---

## 1. Evidence

### 1.1 The rules that place a lead (file:line)

All rules are in `scripts/messaging/export_resend_contacts.py` unless another file is named. The rules are summarised in its docstring at lines 10–23.

**Company and introducer rows** (`company_rows`, lines 250–300).

*The recipient's address* (`company_route`, lines 232–247):
1. The contact's `named_email` or `published_role_email`.
2. Otherwise, an address in the plan's channel or the organisation's inbox whose mailbox starts with the person's first name.
3. Otherwise, a generic inbox (`GENERIC`, line 75).

*Named* (lines 273–275). A contact counts as named when all of these hold:
- its verification passes `R.VERIFIED` and not `R.UNUSABLE` (`resolve_master_recipients.py:97–98`). UNUSABLE covers "name incomplete", "pdpa_risk risky" and "decision-maker no";
- it has a first name;
- its role ranks under `role_rank_for` (`resolve_master_recipients.py:139–158, 234–239`), or under the fallback roles without a board title.

*Confidence:*
- **Low:** any hold reason (lines 268–282). These are the `LOW_COMPANY` patterns, a draft not ready, a free-mail inbox not shown to be the company's own, or an address that looks like another person's.
- **High:** named, and the address is the person's own published address (`direct`, line 276) or on the company's own domain (`own_domain`, lines 212–229; lines 283–285).
- **Medium:** named but off-domain (line 287), a free-mail company inbox (line 289), or an own-domain company inbox with no named decision-maker (line 291).

**Welfare rows** (`welfare_rows`, lines 303–344).
- **Low:** an unconfirmed free-mail inbox, an address that looks like another person's, or a draft not ready.
- **Medium:** a named leader on a confirmed free-mail inbox, or an unnamed inbox.
- **High:** a named leader on an inbox that is not free-mail (lines 321–334). Welfare high does not test the domain.

**Direct versus indirect** (`high_route`, lines 149–163; applied by `with_route`, lines 166–173):
- **Direct:**
  - the mailbox carries one of the person's names (any name token of three or more letters anywhere in the mailbox, a mailbox that is a prefix of a name, or first initial plus surname), or
  - `HR_LOCALS` (line 144) for an HR role, or
  - `HEAD_LOCALS` (lines 145–146: md, ceo, gm, dg, vc, principal, director …) for a senior role.
- **Indirect:** everything else.

**On-the-ground rule** (`resolve_master_recipients.py`):
- `location` (lines 250–262) and `eligible` (lines 281–296) put people running the Tanzania or Arusha operation first.
- `escalation_for` (lines 345–368) makes a group, regional or global head the escalation contact.
- `BOARD` (line 86) excludes board roles unless the title is also executive.
- Reviewed exceptions are in `data/reference/recipient-overrides.json` (seven organisations).

**Rejected routes.** `data/reference/rejected-routes.json` is applied by `build_contact_profiles.py` and `merge_master_contacts.py`.

**Current segment counts** (exporter, 11 October; they match `outputs/messages/Silverleaf Resend Segments - 2026-10-11.md`):

| Track | high-direct | high-indirect | medium | low |
|---|---|---|---|---|
| companies | 30 | 215 | **370** | 52 |
| introducers | 2 | 10 | 3 | 0 |
| welfare | 12 | 55 | 10 | 118 |

The brief said companies-medium was 365. The exporter gives 370, the same as the committed report, and all counts here use 370.

### 1.2 What each pool lead lacks (pool = high-indirect + medium = 663 rows)

| Database | Band | Reason (the exporter's own `confidence_reason`) | Count |
|---|---|---|---|
| companies | high-indirect | Named, verified decision-maker; only a general inbox | **215** |
| companies | medium | Own-domain inbox, no usable named decision-maker | **336** |
| companies | medium | Free-mail company inbox, no usable named decision-maker | 18 |
| companies | medium | Named, verified decision-maker; address off the company's domain (14) or on free-mail (2) | 16 |
| introducers | high-indirect | Named decision-maker; only a general inbox | 10 |
| introducers | medium | Inbox, no named decision-maker | 3 |
| welfare | high-indirect | Named leader; only a general inbox | **55** |
| welfare | medium | Named leader on a confirmed free-mail inbox | 3 |
| welfare | medium | Organisation inbox, no named leader | 7 |

**Why the 357 unnamed company and introducer medium leads have no recipient:**

| Sub-reason | Count |
|---|---|
| No decision-maker on file | 310 (307 companies, 3 introducers) |
| Decision-maker on file, but verification is unverified | 21 |
| Decision-maker on file, but name incomplete, pdpa risky, or not a decision-maker | 16 |
| Verified decision-maker on file, not selected (no email route of their own, or draft not ready) | 10 |

The welfare medium unnamed leads: 5 with no leader on file, 2 with a leader on file who is not the addressee.

**What the repository already holds for the pool** (cache and profiles, no network):

| Track / band | Name-matched own-domain address already held | Own-domain personal-style address on the site, not the recipient's | Site crawled (6 pages max), nothing for the person | Site the crawler could not read | Read with the browser, nothing | No website |
|---|---|---|---|---|---|---|
| companies high-indirect (215) | 2 | 27 | 169 | 14 | 3 | 0 |
| companies medium (370) | 0 | 0 | 270 | 64 | 11 | 25 |
| introducers (13) | 0 | 3 | 9 | 1 | 0 | 0 |
| welfare high-indirect (55) | 0 | 4 | 46 | 4 | 1 | 0 |
| welfare medium (10) | 0 | 0 | 9 | 0 | 0 | 1 |

What the table shows:
- **The cache is nearly exhausted for direct addresses.** Of the two companies' "name-matched" hits, one is real: an owner's first-name mailbox on the owner's own site. The other is a **false positive**: another person's mailbox whose surname equals the recipient's first name. That is the `high_route` weakness covered in decision D7.
- **The profiles add nothing.** In the current `runtime/contacts/profiles.json` (built 11 October), only two decision-makers carry a linked email, and both are already on their contacts.
- **The 34 "personal-style, not the recipient's" sites** show department, country-office or colleague mailboxes. These are format evidence for section 8, not routes.
- **Role inboxes already published but not used as routes.**
  - Two high-indirect recipients hold the role whose inbox the organisation publishes: Moshi Co-operative University's `vc@` and the Tanzania Atomic Energy Commission's `dg@`. Today the route goes to `info@` or `barua@`, because `company_route` only looks at the plan channel and the organisation's own inbox.
  - Eight unnamed medium leads publish an `md@`, `hr@` or `recruitment@` inbox: Karibu Camps, LGT Logistics, The Rickshaw Travels, Altezza Travel, Bonite Bottlers, Mount Meru Hotel, Arusha Meru International School and Kibo Palace Hotel. For these, naming the holder of that role is all that is missing.
- **Team pages are cached.** Of the crawled pool sites, 163 of 198 company high-indirect sites and 38 of 50 welfare high-indirect sites already have a team or about page cached. The people are known. What is missing is an address, which the first six pages did not publish.
- **Inferred candidates exist for 11 pool recipients** (8 companies, 2 introducers, 1 company medium) in `candidate_emails`. By rule they never count.

### 1.3 Split by kind and segment

- **Companies high-indirect (215):**
  - Safari and tour operators: 169 (149 + 20 filed as "Safari operator").
  - Banks: 9. Hotels: 6. Government: 5. Hospitals and clinics: 6. Universities and colleges: 5. Others: 15.
  - Reach tier: P1 40, P2 19, P3 156.
  - Distance: 0–5 km 158, 5–10 km 18, 10–25 km 24, over 25 km 6, unknown 9.
- **Companies medium (370):**
  - Safari and tour operators: 248. Hotels: 51. NGOs and international organisations: 24. Companies: 12. Hospitals: 9. Colleges: 6. Others: 20.
  - Reach tier: P1 30, P2 56, P3 284.
  - 266 are within 5 km.
- **Welfare high-indirect (55):**
  - Segment: funders 21, family-based programmes 17, residential care 8, specialised centres 5, networks 4.
  - Priority: High 9, Medium 4, Low 42.
  - Distance: 0–5 km 19, 5–10 km 9, 10–25 km 10, over 25 km 1, unknown 16. The unknown-distance leads are mostly overseas funders.
- **Welfare medium (10):** family-based programmes 5, residential care 4, funders 1.
- **Introducers (13):** sector associations 5, employers' associations 3, chambers 3, an HR body 1, other 1.
- **Headcount** is known for only 15 of 663 pool leads, so it can only break ties.

### 1.4 Data-quality items found in the pool (fix before spending searches)

These are flagged, not fixed:
- **Sunflag Tanzania Limited (P1, high-indirect):** the recipient is "Key Contacts", a page heading read as a name.
- **Tabasamu Africa Organization (welfare high-indirect):** the leader is a public figure ("Actress, Director and Producer"). The person filter is meant to drop public figures.
- **Welfare recipients with board-chair or overseas development roles.** Examples: chairs of Asali, Giving Smiles, Vrienden van Amani, WATOYO and O'Brien School; a US "Director of Development"; a "Board President".
  - The welfare run does not apply the master's rule "a chair only if no executive is named".
  - Two of the current 12 welfare-high-direct rows are such roles.
  - This is out of this wave's scope, but a direct address for a chair would not serve the goal.
- **Misfiled segments.** PwC Tanzania, Gupta Auto Spares and Lashku Forex are filed as "Safari / tour operator".
- **Exporter false positive.** `high_route` accepts any three-letter name token anywhere in the mailbox (D7). None of the current 44 high-direct rows depends on that looseness: every one starts with the first name or contains the surname. A stricter test therefore loses nothing today.

---

## 2. Prioritisation

The ranking key below is a proposed `--rank reach` in `plan_contact_research.py`:
1. **Value tier.** Companies: reach tier P1 > P2 > P3 (`employer_reach`), then desk tier A > B > C > D. Welfare: priority High > Medium > Low, then desk tier P1–P4. Introducers sit with P1, because one introducer reaches many members.
2. **Distance band.** Core (≤ 10 km), then outer (≤ 25 km), then beyond or unknown.
3. **A named on-the-ground person already exists**, so only the address is missing: high-indirect before medium.
4. **The own website exists and was crawled** (pages to re-read for free), then a site the crawler could not read (browser), then no site (registers and directories only).
5. **Headcount**, where known, breaks ties.

**The policy limit.** The depth-over-breadth rule (`docs/methodology/contact-research.md:59`, decided 2 October) gives P3 companies "the plain request and no searches". P3 is 156 of the 215 high-indirect leads and 284 of the 370 medium leads. This plan keeps P3 search-free (decision D5). P3 gets only the deterministic steps and the browser pass.

**Ranked pool:**

| Rank | Group | Leads | Treatment |
|---|---|---|---|
| 1 | Companies P1 + P2, high-indirect (named) | 59 (P1 40, P2 19; 57 within 5 km) | Deterministic, then search slice S1 |
| 2 | Introducers, all | 13 | Deterministic, then S3 |
| 3 | Welfare high-indirect, High + Medium priority | 13 | Deterministic, then S3 |
| 4 | Companies P1 + P2, medium (needs a named person and an address) | 86 (P1 30, P2 56) | Deterministic, then S2 |
| 5 | Welfare high-indirect, Low priority, and welfare medium | 52 | Deterministic, then S3 |
| 6 | Companies P3, high-indirect, core | 116 | Deterministic (deep crawl) and browser pass only (D5) |
| 7 | Companies P3, medium, and P3 high-indirect outer | 324 | Deterministic only; second wave |

**Recommended first wave:**
- the deterministic steps over the whole pool (all 663 rows; 637 have a website, readable or not);
- one research wave over ranks 1–5, which is **223 organisations** in three search slices plus one browser slice.

This fits the 200-search cap (section 4).

---

## 3. Deterministic steps first (no search budget)

These run in order, before any search agent.

**D-1. Wire published role inboxes to their holders** (expected: 2 now, more after D-3).
- When the organisation's own site (or an official page) publishes `vc@`, `dg@`, `md@`, `ceo@`, `gm@`, `principal@` or `hr@` on its own domain, and the chosen in-country recipient holds exactly that role, record the inbox as the contact's `published_role_email`. The source is the page that publishes the inbox.
- The exporter already counts this as direct (decided 10 October, docstring lines 20–21). Only the data step is missing.
- **Change:** a new `--role-inboxes` mode in a new `scripts/contacts/extract_direct_emails.py`, writing records that `update_master_contacts.py` applies (see D-4).
- **Smaller alternative:** in `company_route`, prefer an own-domain inbox in the pool whose mailbox matches the recipient's role over a generic one. That only works when the inbox is already in the plan channel or the organisation's email, which is not the case for `vc@` and `dg@`, so the data route is better.

**D-2. Name-matched addresses already cached** (expected: 1 now).
- `extract_direct_emails.py` reads the cached pages of pool organisations with `contact_lib.extract`.
- It ties an own-domain address to a named person only under decision D1's rule:
  - the address sits in the person's block on the same page (same line, or within three lines before the next name); or
  - the mailbox carries the person's name under the strict test (first name at the start, or the full surname, or first initial plus surname) and no other listed person at the organisation matches.
- It writes agent-brief records with `method: "website"`, `fetched: true`, `identity: "confirmed"`, a quoted excerpt of 25 words or fewer, and `email_link` ("same block" or "name-matched on own site").
- Output: `data/raw/contact-research/website_direct_<date>.jsonl`.

**D-3. Targeted deep crawl of pool sites** (expected: 4–11).
- **Change:** add a `--deep` option to `crawl_org_websites.py`, with `--orgs <slice.json>` to restrict it to the pool.
  - It raises the page limit from 6 (`contact_lib.MAX_PAGES`, line 47; used at `crawl_org_websites.py:92`) to 15 for those sites.
  - It adds link patterns to `PAGE_KINDS["team"]`: leadership, management, executive, staff, our-people, directory, profile, administration, directorate, faculty and departments.
  - It follows staff-profile links one level down from a team page.
- Robots.txt, the 1.5-second spacing, the cache and the block rules are unchanged.
- Output: `website_contacts_<date>.jsonl` (same format; the planner already reads it). D-2 is then re-run over the new pages.
- **Scope:** about 270 crawled pool sites with a named recipient (companies high-indirect 198, welfare high-indirect 50, introducers 10, named medium about 12), plus about 290 unnamed medium sites, where deep pages often name the managing director or HR head.
- **Basis for the yield:** 34 of the about 270 named-recipient pool sites show personal-style own-domain mailboxes in their first six pages, so the sites do publish staff addresses at some rate. University (`ac.tz`) and NGO staff-profile pages are the likeliest sources.

**D-4. A merge path for people already on file.**
- Most pool recipients already exist as contacts.
- `merge_master_contacts.py` inserts only new people, and takes a person's email only from `person["email"]` (lines 310 and 548).
- `update_master_contacts.py` fills an empty `named_email` for an existing contact, but reads only `search_*` and `browser_*` files (`files_for`, lines 51–53).
- **Change:** an additive glob for `website_direct_<date>.jsonl` in `files_for`. A record must be fetched, with identity confirmed and an excerpt. The rest of the script's rules apply unchanged (no free-mail, never overwrite, a fact with a source record).

**D-5. Registers already in the repository.**
- The TATO pulls (`data/raw/lead-research/tato_*.txt`) hold organisation inboxes only, with no named person. Their personal-style addresses (for example a company-name mailbox at a shared ISP) feed section 8 at most.
- The NGO register (welfare) holds no emails.
- **No register yield is expected.** This is stated here so no agent spends time on it.

**D-6. Browser pass for sites the crawler cannot read.**
- `plan_browser_pass.py --date <date>` covers the pool's unreadable or script-built sites:
  - 14 companies high-indirect, 64 companies medium, 4 welfare, 1 introducer;
  - plus 1 robots-disallowed high-indirect site and 4 robots-disallowed medium sites, read and tagged risky.
- The P1, P2 and welfare ones go to the research slices that own those organisations. The about 58 P3 sites go to slice S4.
- Browser work uses no search.
- Per `research-rate-limits.md` ("Browser pane"), the coordinator runs it or one browser agent does. It counts as one of the four agents.

**D-7. Planner mode** (`plan_contact_research.py`, additive):
- `--target direct-email`: candidates are the exporter's high-indirect and medium rows, computed by importing `company_rows` and `welfare_rows` the way the analysis script does. Each candidate's `needs` becomes `own work email` (named) or `named decision-maker + own work email` (unnamed).
- `--rank reach`: the order from section 2.
- `--orgs-from <analysis detail>`: so the slices match this plan exactly.
- Record the label `own work email` in `search-targets.json`, so `--second-pass` knows this target was searched.
- **Also fix:** the planner reads only `search_*_<date>.jsonl` files of the same date (line 131), so a new date forgets earlier waves. Add `--searched-since <date>` so earlier coverage counts, and give each agent the previous coverage logs for its organisations so no query is repeated.

**Estimated deterministic yield:** 7–14 new high-direct rows (D-1: 2; D-2: 1; D-3: 4–11). Most will be companies.

---

## 4. Search budget and waves

**Budget:**
- Cap: 200 WebSearch calls in this new session, none used yet.
- Coordinator reserve (10%): **20**.
- Agents: **180** = 165 allocated across three slices, plus a **15** top-up handed at the midpoint to the slice with the best yield per search.
- At most four agents at a time, the browser agent included.

**Hard rules for every agent** (in each prompt, after the standard brief in `plan_contact_research.py`'s `PROMPT`):
- **An address counts only when a page publishes it** for that person, or for that person's role on the organisation's domain.
  - Never construct one from a pattern (firstname@domain), even when the domain's format is known.
  - A pattern guess is section 8's job and never a research finding.
- **Sources:** the organisation's own site (team, staff, leadership, contact and press pages, annual reports and PDFs), its own vacancy notices, official registers, a parent body's official page, and the public directories allowed on 2 October (chamber and association member lists, trade-fair lists, government lists).
  - Excluded: LinkedIn and other social profiles, data brokers, review sites, and anything behind a login.
- **No search across other sites with a person's name** (`contact-research.md:66`). Allowed query forms:
  - `site:<own domain> "<surname>"`
  - `site:<own domain> email OR contact OR team`
  - `"<organisation name>" "@<own domain>"`
  - `"<organisation name>" annual report filetype:pdf`
  - `"<organisation name>" vacancy OR "send your application"`
  - `"<organisation name>" <directory host>`

  Whether `site:`-scoped name queries are allowed is decision D4.
- **pdpa_risk:** `medium` for a named work email on the organisation's own domain. `risky` for anything on a personal domain or from a robots-disallowed site. A risky record never moves a lead to high, because the UNUSABLE rule applies.
- **Robots-disallowed pages:** browser only, tagged risky. Never pass a bot check, CAPTCHA or login.
- **Coverage log.** One per slice, in `data/raw/contact-research/coverage/hd1_<slice>_coverage.md`, with numbered queries (`Q7/60`) and outcomes, blocked sites, and organisations not reached.
- **Output.** One JSONL line per organisation (agent-brief fields, plus `email_link` and `source_type` on each person) in `data/raw/contact-research/search_hd1_<slice>_<date>.jsonl`. Browser output goes to `browser_hd1_<slice>_<date>.jsonl`.

**Wave 1 slices** (each organisation's list comes from `plan_contact_research.py --target direct-email --rank reach --orgs-from <detail>`):

| Slice | Leads | Allocation | Query patterns | Stopping rule |
|---|---|---|---|---|
| **S1 `hd1_companies_p12_named`** | 59: P1 and P2 high-indirect (safari operators 34, banks 9, hotels and lodge groups 5, hospitals and clinics 4, companies and insurers 4, universities and colleges 3) | **60** | First fetch the cached team page's sub-links, the contact page, the press or news page, the annual-report PDF and the careers page; then `site:<domain> "<surname>"`; then `"<org>" annual report filetype:pdf` (banks, hospitals); then `"<org>" "@<domain>"` | Per organisation: stop when the person's own address or role inbox is found on an allowed source, or after up to 8 fetches and 1 search (2 for P1). Slice: stop at 60, or when all 59 are reached |
| **S2 `hd1_companies_p12_unnamed`** | 86: P1 and P2 medium (hotels 29, safari operators 26, companies 7, hospitals 6, international bodies 4, colleges 3, others). The 8 with a published `md@`, `hr@` or `recruitment@` come first | **55** | Fetch the team, about and management pages; `"<org>" "general manager" OR "managing director" OR "human resources"` (organisation-scoped); `site:<domain> manager OR director`; then the person's address as in S1. Record the in-country head first and the group head as escalation | Per organisation: stop at a named in-country decision-maker with their own address or role inbox; else record the named person (moves the lead to high-indirect) after up to 8 fetches and 1 search. Slice: stop at 55 |
| **S3 `hd1_welfare_introducers`** | 78: introducers 13 (TNCC and TAHA publish first.last staff mailboxes), welfare high-indirect High and Medium 13, welfare medium 10, then welfare high-indirect Low 42 (funders' staff pages) | **50** | Fetch the team, staff, contact and annual-report pages; the funder's country page; `site:<domain> "<surname>"`; `"<org>" "@<domain>"` | As S1. The introducer and High/Medium groups are done first, and the Low group only while allocation remains. Stop at 50 |
| **S4 `hd1_browser_p3`** | About 58 P3 sites the crawler could not read (company high-indirect and medium), plus the 5 robots-disallowed sites | **0** (browser only) | At most 5 public pages per site, one at a time, in its own tab | Per site: 5 pages, or the person's address found. Blocks are recorded |

**Expected yield for wave 1.** The rates come from earlier contact-research waves in `data/raw/contact-research/`:

| Earlier wave | Organisations with a person's own-domain email |
|---|---|
| `wave10_master_employers_a–d` | 5 of 160 (3%) |
| `wave8_master_employers_a/b` | 3 of 82 (4%) |
| `wave12_p1_pages` | 7 of 100 targets (7%) |
| `search_newleads` | 4 of 95 (4%) |
| `search_D_hotels_government` | 19 of 93 (20%) |

Those waves looked for a route or a decision-maker, not the address of a person already known, so a targeted wave should do somewhat better:
- **S1:** 59 × 8–15% = 5–9.
- **S2:** 86 × 4–9% = 3–8 to high-direct. About 25–35 more should move medium → high-indirect: earlier decision-maker waves found people for 30–50% of the organisations they reached.
- **S3:** 78 × 9–18% = 7–14. Introducers and international funders publish staff mailboxes more often.
- **S4:** 58 × 2–5% = 1–3.

**Whole-wave estimate** (deterministic plus search): **23–48 new high-direct rows.** That is about companies-high-direct 30 → 45–65, welfare-high-direct 12 → 17–24, and introducers-high-direct 2 → 3–6. Duplicates collapse at export, so treat the bottom of each range as the planning figure.

**Second wave.** If budget remains (unlikely), the 15 top-up and any unspent allocation go first to S1's P1 organisations not reached, then S3's Low group.

**Needs a new session** (a new 200-search cap):
1. The rest of S2, and S3's Low welfare group.
2. Companies medium "named, off-domain" (16) and free-mail inbox (18): confirm the domain the company publishes, mostly by fetching.
3. The 21 unverified and 16 incomplete-name decision-makers on file: verify the role and complete the name; the result is high-indirect.
4. If the user lifts D5 for this goal: P3 high-indirect core (116), at about 0.5 searches each, with deep-crawl results first.
5. P3 medium (284) stays out of search under the current policy.

---

## 5. Merge path and rebuild

**The coordinator, in the main checkout.** The databases live only there; copy in, verify and write back for worktree sessions.

**Company master:**
1. `python scripts/contacts/build_contact_profiles.py --date <date>`. Then `python scripts/contacts/build_contact_workbook.py --date <date> --baseline` to record the before counts.
2. Existing contacts gain addresses through `python scripts/master/update_master_contacts.py --date <date>` (preview), then the same command with `--apply`. It reads `search_hd1_*`, `browser_hd1_*` and, after D-4, `website_direct_*`.
3. New people (S2's named decision-makers) go through `python scripts/contacts/merge_master_contacts.py`. It writes the intake, then runs `validate_intake.py` and `preflight_update.py`; review both reports. Then the same command with `--apply`, one transaction. Try both on a copy first (`--database <copy>`), as the methodology requires.
4. `python scripts/master/resolve_master_recipients.py` (preview), then `--apply`: the in-country recipient and the escalation contact.
5. `python scripts/messaging/draft_master_messages.py`, then `python scripts/master/refresh_acquisition_metadata.py`.
6. The CLAUDE.md order:
   ```powershell
   python scripts/master/export_master_workbook_data.py
   npm run build:workbook
   python scripts/master/verify_master.py
   ```

**Welfare run:**
- `python scripts/contacts/export_run_contact_research.py` writes `research_W_contact_profiles_<date>.jsonl`, with each person's linked email in `emails` / `email_type: named`.
- Then `python scripts/welfare/run_pipeline.py --run-id arusha-welfare-2026-09 --rebuild-db`.
- `draft_run_messages.py:410–413` routes the leader's `named_email` directly.
- **To verify on a copy in phase 2:** that `consolidate_research.py` fills `named_email` for a leader already on file rather than adding a duplicate contact.

**How the export reclassifies:**
- A contact with a new own-domain `named_email` is returned first by `company_route`. `high_route` then marks it direct ("the person's own address").
- A new `published_role_email` (`vc@`, `md@`, `hr@`) matching the role is marked direct ("the inbox for their role").
- In welfare, the leader's `named_email` becomes the `route_value`, and `high_route` marks it direct.

**Checks that prove the gain.** Add a `--check` mode to `analyse_high_direct_pool.py`, run before and after:
- segment counts before and after for every track, with the movement matrix (pool row → new band);
- **zero** high-direct rows on a free-mail domain;
- **zero** high-direct addresses listed in `rejected-routes.json`;
- **zero** high-direct addresses equal to a `candidate_emails` address or a section 8 inferred candidate;
- every new high-direct address has a `facts` row (`named_email` or `published_role_email`) with a `source_records` record whose URL is fetched;
- no high-direct recipient with `pdpa_risk risky`, an incomplete name, or a board-only role;
- the dedupe list ("addresses shared by two rows") does not grow unexpectedly;
- `verify_master.py` and `verify_welfare_run.py` pass.

`python scripts/messaging/export_resend_contacts.py` writes the segment files to `runtime/resend/<date>/`, which is not committed. Report the counts from its summary file.

---

## 6. Risks and decisions for the user

**Privacy and data boundaries: is there a gap today? Yes, one, and it is narrow.**
- `infer_candidate_emails.py` (decided 2 October) generated 31 inferred addresses into the table `candidate_emails`.
- `export_master_workbook_data.py` (lines 104–107 and 287–292) writes them into the **committed** master workbook:
  - 30 in the Contacts sheet's `candidate_email` column;
  - 30 in Outreach plans;
  - 13 in Organisations.
- They are labelled unverified, never routed, and nothing sends them, so they are not presented as found.
- They are still guessed personal addresses in a committed file. This conflicts with CLAUDE.md's current line and with the user's new instruction that contact-address files stay in `runtime/`. Section 8 fixes this.

Two smaller inconsistencies:
- The committed `Silverleaf Resend Segments - <date>.md` lists published addresses that were exported once ("Addresses shared by two rows"), although the docstring keeps contact-address files out of git.
- CLAUDE.md line 18 says "Do not infer private contact details", while AGENTS.md line 25 and `contact-research.md:68` have allowed labelled candidates since 2 October.

This wave's research track adds no new gap. It records only published addresses, in the same places published addresses already go.

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | An own-domain address on the organisation's own site whose mailbox carries the named person's name, without the page putting it next to them. Does it count as that person's published address? | (a) only when in the same block as the name; (b) also when name-matched under a strict test; (c) any name token (today's exporter) | **(b).** Strict test: first name at the start of the mailbox, the full surname, or first initial plus surname; on the organisation's own domain; published on its own site; no other listed person matches. Record `email_link` so a reviewer sees the basis |
| D2 | Role inboxes (`md@`, `ceo@`, `gm@`, `vc@`, `dg@`, `principal@`, `hr@`) as direct | Already counted as direct by the exporter since 10 October | **Keep**, only when the organisation's own site or official page publishes the inbox on its own domain and the in-country recipient holds exactly that role. D-1 records it as `published_role_email` with that page as source. A group head's `ceo@` is not the in-country MD's |
| D3 | A personal work address found only on a third-party public directory (a chamber or association member list, a trade-fair list, a government list) | (a) never; (b) counts when on the organisation's own domain, the entry names the person, and it is dated within 24 months; (c) any address | **(b).** Tag `source_type: directory`, pdpa `medium`. A free-mail address from a directory is never direct |
| D4 | Search queries with a person's name, given the rule "a person's name is never searched across other sites" | (a) no name in any query; (b) `site:<own domain> "<surname>"` only; (c) name plus organisation across the web | **(b).** It stays inside the organisation's own site and is within the rule's intent. (c) would breach the written rule |
| D5 | P3 companies: no searches (depth-over-breadth, 2 October) | (a) keep; (b) lift for high-indirect P3 core (116) in a second session | **(a) for wave 1.** Revisit after wave 1's yield per search is known |
| D6 | pdpa_risk handling | — | A named own-domain work email is `medium`. A personal domain or robots-disallowed source is `risky` and excluded from high until a person approves it (today's UNUSABLE rule). An address on a page about private life is never recorded |
| D7 | Tighten `high_route`'s own-address test | (a) keep "any three-letter name token anywhere"; (b) first name at the start, surname anywhere, or initial plus surname, and no other listed person at the organisation matches | **(b).** It prevents a colleague's mailbox counting as the recipient's. All current 44 high-direct rows pass (b) |
| D8 | Data-quality holds (section 1.4): a heading read as a recipient, a public figure as a welfare leader, board chairs as welfare recipients | (a) fix through the update skill and the welfare links before the wave; (b) leave them | **(a).** Hold those organisations out of the slices until fixed |
| D9–D14 | The email-format track | See section 8.6 | See section 8.6 |

**Other risks:**
- **Low yield is the main risk.** Most pool organisations are small safari operators that publish only `info@`. The ranges above assume that.
- **Stale people.** A role confirmed before 2026-09 may have changed. Agents re-confirm the role on the page that gives the address.
- **Bounces.** New direct addresses are published, but people move. Recommend the first send from high-direct in small batches; sending stays with a person.
- **Concurrency with other sessions.** The databases and `runtime/` are shared. Merges run only in the main checkout, one at a time.

---

## 7. Boundaries (tasks, files, shared contracts)

**T1: deterministic tooling** (one worker, own worktree; phase 2 after sign-off)

Files it owns:
- `scripts/contacts/crawl_org_websites.py` (`--deep`, `--orgs`)
- `scripts/contacts/contact_lib.py` (deep-page link patterns, page limit as a parameter)
- new `scripts/contacts/extract_direct_emails.py` (D-1, D-2)
- `scripts/master/update_master_contacts.py` (`files_for` glob, D-4)
- `scripts/contacts/plan_contact_research.py` (D-7)
- `scripts/messaging/export_resend_contacts.py` (D7 only: the `high_route` strict test)
- `scripts/contacts/analyse_high_direct_pool.py` (`--check`)
- `scripts/README.md` (the rows for these)

Tests:
- on copies of the databases: preview counts, the `--check` invariants, `verify_master.py`;
- a fixture page for the strict name test, including the false-positive case;
- `--deep` against a cached site with `contact_lib.OFFLINE` set.

**T2: research wave 1** (the coordinator launches at most four agents after T1's planner mode, or from hand-built slices)

Files it owns:
- `data/raw/contact-research/search_hd1_*_<date>.jsonl` and `browser_hd1_*_<date>.jsonl`
- `data/raw/contact-research/coverage/hd1_*_coverage.md`
- `runtime/contacts/agents/hd1_*`
- the `search-targets.json` entries for its files

It changes no scripts.

**T3: merge and rebuild** (the coordinator, main checkout, sequential, after T1 and T2)

It owns:
- the master database, the welfare run database and their outputs
- `data/raw/welfare-research/research_W_contact_profiles_<date>.jsonl`
- `outputs/contacts/*`
- the workbooks and the map rebuild

**T4: email-format track** (one worker, own worktree; **starts only after the user approves the wording in section 8.5, and after T1 has merged**, because both edit `export_resend_contacts.py`)

Files it owns:
- new `scripts/contacts/email_formats.py`
- `scripts/contacts/infer_candidate_emails.py` (rewritten to read the format registry, or retired into `email_formats.py`)
- new `data/reference/email-formats.json`
- `scripts/master/export_master_workbook_data.py` (candidate address → pattern only)
- `scripts/messaging/export_resend_contacts.py` (new `-low-inferred` files only)
- `scripts/contacts/build_call_sheet.py` (pattern column)
- `scripts/README.md` (its rows)

The coordinator applies the approved CLAUDE.md and methodology wording.

**Shared contracts** (fixed now, before any task starts):
1. **Research record format.** The agent brief's fields, plus optional person fields:
   - `email_link`: `same block` | `name-matched on own site` | `role inbox for role` | `directory entry`
   - `source_type`: `own site` | `register` | `directory` | `press or report` | `vacancy notice`

   `extract_direct_emails.py`, T2's agents, `update_master_contacts.py` and the profile builder all use it. Unknown fields are ignored by today's readers.
2. **`search-targets.json` label.** `own work email` (T1 adds it in the planner, T2's files use it).
3. **`high_route` semantics.** Direct means the person's own published address (strict test, D7) or the role inbox for their role on the organisation's domain. **An inferred candidate is never an input to `company_route` or `high_route`.** T4 must not change this function.
4. **Export files.**
   - The existing `<track>-<confidence>.csv` and `-high-direct` / `-high-indirect` files keep `FIELDS` unchanged.
   - T4 adds only new files, `<track>-low-inferred.csv`, with `FIELDS` plus `inferred_format`, `inferred_evidence` and `inferred_label`. These files live in `runtime/resend/<date>/`.
5. **`email-formats.json` schema** (section 8.2). T4 owns it; nothing else writes it.

The order:
1. T1, in parallel with the coordinator's D8 data-quality fixes through the update skill.
2. T2's four agents.
3. T3.
4. T4 any time after T1 merges and the wording is approved, independent of T2 and T3. Its candidates must then be regenerated after T3, because new published addresses are new format evidence.

---

## 8. Email-format track (separate; added at the user's request, 11 October 2026)

**Purpose.** Document an organisation's email format whenever published addresses show it. When the decision-maker is known, generate a candidate address from that format, **always at low confidence**, for a person to confirm before any use. It never counts toward high or high-direct.

**What exists today.** `scripts/contacts/infer_candidate_emails.py` (2 October) and the table `candidate_emails` (31 rows) already do part of this, for the master only. The new safeguards differ from it in five ways:
- It sets **medium** confidence at two or more pieces of evidence. The new rule is **always low**.
- It lets a one-name person get a first-name candidate. The new rule: **never** for a one-name or incomplete name.
- It counts "a first-name mailbox whose owner is not named on file" as evidence, using first names from any contact in the whole master. That is too weak; drop it.
- It reads only database fields, not cached pages or profiles. Add those as evidence sources.
- It feeds the committed workbook with the address. Change this to show the pattern only.

The track therefore **replaces** `infer_candidate_emails.py`'s logic with a format registry, rather than adding a second inference path.

### 8.1 Format evidence (safeguard 1, refined)

**What counts as evidence.** A published personal address at the organisation's own domain whose mailbox matches a **full name** (first and last) of a person the organisation itself publishes (on file, or in the contact profiles), under one of these patterns:

| Pattern | Example mailbox (for "Kevin Kibuku") |
|---|---|
| `first.last` | kevin.kibuku@ |
| `first_last` | kevin_kibuku@ |
| `firstlast` | kevinkibuku@ |
| `f.last` | k.kibuku@ |
| `flast` | kkibuku@ |
| `firstl` | kevink@ |
| `first` | kevin@ |
| `last` | kibuku@ |

**Minimum evidence.**
- **Two or more** matching addresses for **two different people** before any candidate is generated. A domain with one match is recorded as `provisional` and generates nothing.
- *Refinement:* the user suggested "at least one, preferably two". At one piece of evidence the `first` pattern dominates (36 of 66 formats here). One owner's `joseph@` does not show how a second person's mailbox is formed. The Aga Khan University domain (`aku.edu`) shows the risk: one matching address would yield 12 candidates across a global institution.

**What is never evidence:**
- **Role inboxes:** the `GENERIC` list in `infer_candidate_emails.py`, plus the analysis script's `ROLEISH` list (info, hr, md, ceo, gm, admissions, country and department mailboxes …).
- **Mailboxes of three letters or fewer.**
- **Free-mail domains.** These never get a format.

**Ambiguous domains.** Two different patterns among the evidence make the domain **ambiguous**. Nothing is generated from it. For example, `first` for the owner and `first.last` for staff is ambiguous.

**Scope of a domain.** A format belongs to the domain, not to the organisation:
- A group domain (`melia.com`, `aku.edu`) is used only for records whose own website is that domain.
- A format seen only at a parent's global domain is **not** applied to the Tanzania company's own domain.

**Storage.** `data/reference/email-formats.json`, reviewed and committed like `rejected-routes.json`. Each entry holds:
- `domain`, `pattern`, `status` (`confirmed` at two or more pieces of evidence, `provisional`, or `ambiguous`)
- `evidence`: up to five items, each with the address, the person's name as published, `source_url`, `fetched` and `accessed_on`
- `organisations` (database and ID), `decided_on`, `reviewed_by`

The evidence addresses are published addresses, which the committed workbook already carries, so committing them adds no new exposure. A builder (`email_formats.py --build`) proposes entries from the databases, profiles and cache. A person reviews the proposals before they are written.

### 8.2 Inferred candidates (safeguard 2)

**Where they live:**
- **Master:** the table `candidate_emails`, with the existing columns plus `format_domain`, `format_status` and `label`. The label is fixed: "inferred from format, unverified". The database is not committed.
- **Welfare:** **not** in the welfare run database. The run is rebuilt from committed inputs and feeds a committed workbook. `email_formats.py --welfare` reads the welfare database read-only and writes candidates straight to `runtime/resend/<date>/welfare-low-inferred.csv` and `runtime/contacts/welfare-inferred-candidates.json`.
- **Never** in `contacts.named_email`, `published_role_email`, `shared_email`, a draft's `contact_channel`, or any research JSONL.

**Each candidate carries:**
- the label
- the format and its status
- the evidence addresses with their source URLs
- the person's contact ID, name and role as on file
- `confidence: low`, always

**Who gets one:** only the chosen in-country recipient and the escalation contact of an organisation with a `confirmed` format, and only when that person has no published own address.

The decision-maker filter in the analysis script counted 101 welfare people. Most are trustees and staff of five funders (Asante Africa 29, Standing Voice 18, The Foundation for Tomorrow 10, Amani Kids 8, Compassion 7). Limiting candidates to recipients avoids generating addresses for everyone on a board list.

**Never generated for:**
- a contact with `pdpa_risk risky`, a name marked incomplete, or a one-name person (`name_status`, `R.UNUSABLE`);
- a board-only role;
- a person whose name holds only initials.

**Never high.**
- The exporter's `company_route` and `high_route` never read `candidate_emails`.
- T1's `--check` asserts that no high or high-direct address is in `candidate_emails` or the welfare inferred file.

### 8.3 Export (safeguard 3)

**New segment files only:**
- `runtime/resend/<date>/companies-low-inferred.csv`
- `runtime/resend/<date>/introducers-low-inferred.csv`
- `runtime/resend/<date>/welfare-low-inferred.csv`

Each has one row per candidate: the existing `FIELDS` plus `inferred_format`, `inferred_evidence` and `inferred_label`. Its `confidence_reason` reads: "inferred from format, unverified: confirm by phone or through the organisation's published route before any send". The organisation's lead also stays in its existing segment, unchanged.

**Call sheets.** `build_call_sheet.py` adds a column "email format on file (to confirm)" showing the pattern and the evidence count, **not** the address, because the call sheets are committed. The caller asks the person to confirm their address. The answer comes back through `import_call_results.py` as a `tel:`-sourced, consented record. It then becomes a verified route and moves up through the normal merge.

**Once confirmed** with a source (a call recorded with consent, a reply, or a page found later that publishes it), the address is a verified or published route. The candidate's status becomes `confirmed <date> (<source>)` and it is no longer shown as a candidate.

### 8.4 Privacy (safeguard 4)

Where inferred addresses could land in a committed file today, and the fix:

| Committed file | Today | Fix |
|---|---|---|
| `outputs/master/Silverleaf Master Database - Consolidated.xlsx` | Shows the address (Contacts 30, Outreach plans 30, Organisations 13) via `export_master_workbook_data.py:104–107, 287–292` | Show `candidate_format` (for example "flast, 2 published examples, unverified") and no address |
| `outputs/contacts/Silverleaf Call Sheet - *.xlsx`, `Silverleaf Contact Profiles - *.xlsx` | No candidates today | Pattern column only (call sheet). Profiles never read `candidate_emails` or the inferred file |
| `outputs/runs/arusha-welfare-2026-09/*.xlsx` | — | Never: welfare candidates stay outside the run database |
| `outputs/maps/Silverleaf Lead Map.html` | `build_lead_map.py` already fails if a contact name, address or number reaches the page | No change. Add an inferred-address probe to its test |
| `outputs/messages/Silverleaf Resend Segments - <date>.md` | Lists the published addresses exported once | The `-low-inferred` files are reported **as counts only**, and inferred addresses never enter the dedupe list (they are not in the main rows) |
| `data/reference/email-formats.json` | — | Holds patterns and **published** evidence addresses only, never a generated candidate |

**A data-boundary gap after the change?** No, provided the workbook change ships in the same task. Generated addresses then exist only in the uncommitted master database and in `runtime/`. **The gap that exists today** is the 30 inferred addresses in the committed master workbook (section 6). T4 closes it.

The history question is for the user (decision D14). The current workbook is committed, so the addresses stay in git history unless the history is rewritten. Recommend not rewriting history: the addresses are labelled unverified and the repository is private. Remove them going forward.

### 8.5 Rule change: draft wording for approval (not applied)

**`.claude/CLAUDE.md`, line 18.**

Now:
> Every claim must remain traceable to a source record. Do not infer private contact details or personal status. Leave an unsupported hook blank. Keep all sending and automations disabled.

Proposed:
> Every claim must remain traceable to a source record. Do not infer personal status, and never present an inferred contact detail as found: an address counts as published only when a source publishes it for that person or role. The one exception is a work-email candidate generated from an organisation's documented email format (`../docs/methodology/contact-research.md`, "Email formats"): it is labelled "inferred from format, unverified", kept apart from published routes and out of committed files, always low confidence, never a draft's route or a high segment, and confirmed by a person before any use. Leave an unsupported hook blank. Keep all sending and automations disabled.

**`docs/methodology/contact-research.md`.**

*Line 66, first sentence.*

Now:
> No private contact detail is published as fact from a guess, and a person's name is never searched across other sites.

Proposed:
> No contact detail is recorded or presented as found unless a source publishes it, and a person's name is never searched across other sites (a query limited to the organisation's own site, `site:<own domain>`, is not "another site").

The bracket depends on decision D4. Drop it if D4 is (a).

*Line 68: replace the "Candidate addresses" bullet with:*
> - **Email formats and inferred candidates** (decided 11 October 2026; this replaces the candidate rule of 2 October).
>   - A domain's email format is recorded in `data/reference/email-formats.json` only when published addresses at the organisation's own domain show it: at least two addresses, of two different people the organisation itself names, following the same pattern (first.last, f.last, flast, firstl, firstlast, first, last). Role inboxes (info@, hr@, md@ …) are never evidence, free-mail domains never get a format, and a domain whose evidence shows two patterns is ambiguous and generates nothing. Each entry keeps its evidence addresses and their sources.
>   - `scripts/contacts/email_formats.py` may then propose a candidate for the chosen in-country recipient or escalation contact who has no published address. Never for a one-name or incomplete name, a contact with pdpa_risk risky, or a board-only role.
>   - A candidate is labelled "inferred from format, unverified", is always low confidence, and lives apart from every published route (the master's `candidate_emails` table; for the welfare run, files in `runtime/` only). It never becomes a draft's route or a contact's email, and never places a lead in a high segment.
>   - It is exported only to the separate `<track>-low-inferred` files in `runtime/resend/<date>/`. Committed files show the format, never the generated address.
>   - A person confirms it by phone or through the organisation's published route before any use. Once confirmed with a source, it is recorded as a verified route and moves up normally. Send confirmed addresses in small batches and watch for bounces.

**Consistency edits** (separate approval; listed so the rule reads the same everywhere):
- **AGENTS.md line 25:** replace "A candidate work-email address may be proposed from a company's own published pattern (`scripts/contacts/infer_candidate_emails.py`, decided 2 October 2026); it is kept apart, marked unverified and approved by a person before use." with "A work-email candidate may be generated from an organisation's documented email format under the rules in `docs/methodology/contact-research.md` ("Email formats", decided 11 October 2026); it is labelled inferred and unverified, always low confidence, kept out of committed files, and confirmed by a person before use."
- **`skills/silverleaf-create-lead-list/SKILL.md` line 18:** add after "Do not infer private email addresses": "(the one exception, a labelled low-confidence format candidate, is governed by `docs/methodology/contact-research.md`, "Email formats")".

### 8.6 Cost, yield and decisions

**Yield from repository data alone.** Measured by `analyse_high_direct_pool.py` (the `email_formats` block) over the master and welfare fields, all contact profiles and 749 organisations' cached pages:

| Measure | Count |
|---|---|
| Non-free domains with any published address | 935 |
| Domains with one clear pattern | 66 (14 at two or more pieces of evidence, 52 at one) |
| Ambiguous domains | 3 |
| Patterns among the 66 | first 36, first.last 12, flast 7, firstlast 5, last 4, f.last 2 |
| Decision-makers without a published own address at a formatted domain (all decision-makers, before the recipient-only rule) | master 37 (5 at two or more pieces of evidence); welfare 101 (41 at two or more, concentrated in five funders) |
| Organisations that would get a candidate | master 22, welfare 17 |
| **Pool recipients** (this plan's goal) on a formatted domain | **14**: companies high-indirect 10 (1 at two or more), introducers high-indirect 2 (both two or more: the TNCC national and regional chambers), welfare high-indirect 1, companies medium 1 |

**Under the recommended rules** (two or more pieces of evidence, recipients and escalation contacts only), the track produces about **5–15 candidates** now. It grows as wave 1 publishes new addresses, which are new evidence.

**Cost:**
- **No web search.**
- About 6–7 minutes of offline cache reading per build (`contact_lib.extract` over about 5,000 cached pages).
- A person reviews each new format entry and confirms each candidate by phone or route.

**Files T4 owns:** listed in section 7. None overlaps T2 or T3. T4 overlaps T1 only in `export_resend_contacts.py`, which is why T4 starts after T1 merges.

**Decisions for the user (format track):**

| # | Decision | Recommendation |
|---|---|---|
| D9 | Minimum evidence before generating a candidate | **Two matching published addresses, of two different people.** One is recorded as provisional and generates nothing |
| D10 | Confidence | **Always low**, overriding the 2 October "medium at two or more" rule |
| D11 | Who gets a candidate | **Only the chosen in-country recipient and the escalation contact**, not every named decision-maker or trustee |
| D12 | Welfare candidates | **Outside the run database** (`runtime/` only), so the committed welfare workbook never holds them |
| D13 | The 31 existing `candidate_emails` rows | **Regenerate under the new rules.** Expect about half to drop: the one-evidence and one-name ones |
| D14 | The committed workbook already holds 30 inferred addresses | **Remove them going forward** (pattern only); do not rewrite git history |
| D15 | Approve the wording in 8.5 for CLAUDE.md and the methodology, and separately the AGENTS.md and create-lead-list consistency edits | **Approve**, with the D4 bracket matching the D4 decision |

## Sign-off (11 October 2026)

The user approved every recommended option, D1–D15, including the rule wording in section 8.5 and the consistency edits. These are applied to `.claude/CLAUDE.md`, `docs/methodology/contact-research.md`, `AGENTS.md` and `skills/silverleaf-create-lead-list/SKILL.md`.

The user also asked that each inferred candidate be checked with one web search for the exact address in quotes. A hit counts only when a public page publishes that exact address for that person; the page then becomes a source through the normal research files. This is added to the methodology's "Email formats" rules and runs after T4 generates the candidates, drawn from the plan's top-up searches.
