# Contact research

This is how Silverleaf builds contact profiles for the organisations in its three databases (the company master, the welfare run and the government run) and finds contact leads for them. Scripts live in `scripts/contacts/` (catalogue: `scripts/README.md`). Read `skills/silverleaf-create-lead-list/references/research-rate-limits.md` before any network step.

## What a profile holds

- **Organisation contact profile**: website, typed emails (role, general, named, personal domain), typed phones (office, mobile, international), postal and physical address, and official social pages, each with its source.
- **Contact lead**: a named person published as leading or deciding for the organisation: on its own site, in an official register or directory, on a parent body's official page, or on a funder's or partner's own page that names the organisation's current leaders (allowed by the user's decision of 26 September 2026). A lead records:
  - name and role
  - a decision-maker flag
  - a work email or phone, only when the same source links it to that person
  - the source URL, and whether the page was fetched or only seen in a search snippet
  - `pdpa_risk`

Government offices are addressed by office title. Officials are named only from the government run's own official sources.

## Order of work

1. **Deterministic collectors first:**
   - `crawl_org_websites.py` reads each organisation's own website: home, contact, about and team pages, at most 6 per site.
   - `collect_osm_contacts.py` reads OpenStreetMap contact tags.

   Both are cached, so a re-run re-extracts from `runtime/contacts/http-cache/` without the network. After the extraction rules change, `crawl_org_websites.py --reextract` reads every readable site again from its cached pages, never touching the network; sites that were not readable keep their record.

   Some servers send a gzip-compressed page though the crawler never asks for one. The crawler decompresses such pages, cached copies included. Before 23 September 2026 six tour operators' home pages were read as noise this way, so their contact and team pages were never reached; `--recrawl <domain> ...` crawled them again.
2. **Budgeted search agents, for organisations the crawl could not cover:**
   - Build profiles first (step 3), then run `plan_contact_research.py --date <date> --wave <n> --budget <searches>`. It:
     - picks organisations that have an outreach plan and no agent has searched for yet (a record that only fetched known pages and found nothing leaves the organisation a candidate), and that still lack what `--target` names:
       - `routes` (the default): a published email or phone
       - `decision-makers`: a named decision-maker, for organisations that already have a route and whose own website the crawler could not read (a site it read is left to the crawler)
       - `all`: either
     - with `--include-unclassified`, also plans the welfare run's register-only NGOs whose type is not yet known
     - leaves out savings groups (reached through council registers and introducers, not one by one; see `docs/plans/vicoba-sourcing-plan.md`), government offices, and closed or out-of-scope records
     - ranks the candidates nearest first and splits the budget over at most four slices; `--max-per-slice` keeps only the nearest so one agent's work stays manageable (about 35 to 45 organisations), and the rest wait for a later wave
     - with `--split` as well, a larger slice is divided into balanced parts (`<slice>_a`, `<slice>_b`, ...) of at most that size, each with its own agent, still at most four agents in all
     - `--include-crawled` also plans decision-makers for organisations whose own website the crawler read without finding one; an agent reads their about and team pages before searching
     - `--second-pass` also plans organisations an earlier wave searched, but only for what no wave searched them for yet. `data/raw/contact-research/search-targets.json` records what each search file looked for (a published route or a named decision-maker); the planner adds each new wave's files
     - `--db master|welfare` plans one database, `--max-slices` sets the number of agents (at most four), `--rank tier` puts the company master's desk tier first (A, B, C, D, then nearest), and `--exclude-wave <n>` leaves out organisations a wave still running already holds, so the next wave can start as agents finish
     - writes each slice and its agent prompt under `runtime/contacts/`
     - reads the research ledger (next section): it skips an organisation for which every query-pattern family the target allows was already used inside the retry window (`--min-retry-days`, default 90), ranks one with half or more used after the rest, and writes each organisation's compact already-tried list and still-open families into the slice and the prompt; `--ignore-ledger` plans without it, and `--dry-run` writes to `runtime/contacts/dry-run/` and leaves `search-targets.json` unchanged
   - Give each agent a fixed share of the session's WebSearch cap. Launch at most four agents per wave.
   - Each agent writes `data/raw/contact-research/search_<slice>_<date>.jsonl` and a coverage log in `data/raw/contact-research/coverage/`.
   - **After the slices finish, before the merge,** fold each slice into the research ledger: `python scripts/research/ledger.py ingest <coverage log> <search file> [runtime/research-ledger/pending/<slice>.jsonl]`.
   - The agent brief is below.
   - **Browser pass:** `plan_browser_pass.py --date <date>` (after a profile build) plans the own websites the crawler could not use:
     - sites whose robots.txt disallows crawling (read at the user's direction and tagged risky, see the rules below)
     - pages the crawler read (HTTP 200) that gave nothing and hold little visible text because script builds them

     Browser agents use only the built-in browser, each in its own tab, with no web search. They record one line per organisation in `data/raw/contact-research/browser_<slice>_<date>.jsonl`. The fields are the agent brief's, plus `method: "browser"`, `robots` ("allowed" or "disallowed") and `pages_read`, with a coverage log per slice. These records rank with the website's own records when leads are combined. Keep within four research agents at a time, counting the search agents.
3. **Build profiles:** `build_contact_profiles.py --date <date>` writes `runtime/contacts/profiles.json`, `data/interim/contact-profiles/*.tsv` and a summary. Before any merge, `build_contact_workbook.py --date <date> --baseline` records the databases' counts, so the review workbook can show before and after.
4. **Merge into each database, through its own process:**
   - **Company master:**
     1. `merge_master_contacts.py` writes the shared-contract intake and runs `validate_intake.py` and `preflight_update.py`. Review both reports.
     2. `merge_master_contacts.py --apply` runs the merge as one transaction.
     3. Refresh and verify: `draft_master_messages.py`, then `refresh_acquisition_metadata.py`, `export_master_workbook_data.py` and `verify_master.py`.
   - **Welfare and government runs:** `export_run_contact_research.py`, then each run's `run_pipeline.py --rebuild-db`.
5. **Review:** `build_contact_workbook.py --date <date>` writes `outputs/contacts/Silverleaf Contact Profiles - <date>.xlsx`.

## Research ledger (added 11 October 2026)

`data/raw/research-ledger/research_ledger.jsonl` records every search, page read, crawl, browser read and map lookup made so far, one line per attempt, so no worker repeats one. `docs/methodology/research-playbook.md` says what has paid and what has stopped paying; read it before planning a wave.

- **A line holds:** `id`, `date`, `run`, `agent`, `tool` (websearch, webfetch, crawler, browser, gmaps, overpass, nominatim, ngo-register, council-api, places, other), `db`, `organisation_ids`, `organisation_names`, `segment`, `query` (the exact text, or the URL read), `query_pattern` (a template such as `"<org>" "@<domain>"` or `site:<domain> "<person>"`, derived by `ledger.py`), `target` (route, decision-maker, direct-email, location, hook, discovery, verification, relationship), `outcome` (hit, partial, nothing, blocked, refused-cap, skipped, unknown), `found` (a short factual summary), `source_file`, `ref` (`Q7/40`, a line number) and `count`.
- **No contact details beyond the research files.** `found` never holds an email address or a phone number; `ledger.py` removes them and `ledger.py check` fails on one.
- **Before searching:** `python scripts/research/ledger.py tried --org <organisation_id>` lists what was tried for an organisation; `tried --pattern <family or text>` lists the organisations a pattern was used for. The planners put the same list into each prompt.
- **The retry window.** A query pattern is not repeated for the same organisation within 90 days (`--min-retry-days`). A refused or skipped attempt does not use up a pattern.
- **Recording:**
  - Agents log each search in their coverage log as a numbered table, `| Q | Query | Organisation | Outcome |`, naming the organisation as the slice does, and each page read in their JSONL `sources`. They may also append to their own pending file with `ledger.py append --file runtime/research-ledger/pending/<slice>.jsonl`. They never write the ledger file itself.
  - The coordinator folds a finished slice in with `ledger.py ingest <coverage log> <research file> [<pending file>]`, after the slices finish and before the merge. A line already in the ledger is skipped, so a re-run adds nothing.
  - The coordinator's own work goes in the same way: a Google Maps round with `ledger.py ingest data/raw/gap-census/google_maps_enrich_<date><round>.jsonl` (or one lookup with `ledger.py append --tool gmaps --org <id> --query "<what was typed>" --outcome <outcome> --found "<listing; pin; phone listed>"`), a browser pass with `ledger.py ingest data/raw/contact-research/browser_<slice>_<date>.jsonl`, and a crawl with `ledger.py ingest data/raw/contact-research/website_contacts_<date>.jsonl`.
- **Checks:** `ledger.py check` validates every line and reports duplicates; `ledger.py stats` gives yield by tool, family, pattern, target, segment and date; `ledger.py backfill` re-reads every research file in the repository and adds only what is missing.

## Depth over breadth (decided 2 October 2026)

- **Reach tiers.** `scripts/master/rank_employer_reach.py` ranks employers by how many staff a benefit could reach. Research goes deep on tier P1 (the top 100) and P2; small operators (P3) get the plain request and no searches.
- **Where HR is published.** For P1 and P2, agents read the employer's own careers, management and annual-report pages, vacancy notices the employer placed (which often name the HR manager and give the application email), and the group or head office of a lodge, camp or bank. A recruitment agency's contact is not the employer's.
- **Introducers.** Associations, chambers and HR bodies whose members are employers are researched as organisations (`introducers_*_<date>.jsonl`) and added with `scripts/master/add_introducers.py`; their first message asks them to share the staff benefit with members.
- **Calls.** `scripts/contacts/build_call_sheet.py` lists the P1 and P2 employers still without a named staff-benefits contact; the answers come back through `import_call_results.py` and the normal merge, with the person's agreement to receive the email recorded.

## VICOBA savings groups (decided 13 October 2026)

VICOBA and VSLA groups are group-level records in the company master (`docs/plans/vicoba-integration-plan.md`, decisions taken, section 0 and decision 3). Groups are reached through introducers, never researched one by one: `plan_contact_research.py` plans no web search for a savings group, and the playbook records why (the public web gave no VICOBA groups).

**Routes, in order of use.**
1. **The introducer.** This is the usual route. It is one of:
   - an NGO field office, bank branch, faith office or employer in the master;
   - an NGO in the welfare run, referenced there;
   - the ward or council Community Development Officer, referenced in the government run.
2. **A route the group or a public body publishes for the role**, such as a chair's or secretary's phone on a council page or in an NGO report.
3. **The meeting place, at meeting time.** This is used only after an introduction or the committee's agreement, and never as an unannounced visit.

**Introducers.**
- **Adding them.** `scripts/master/link_vicoba_introducers.py --add-introducers data/raw/vicoba/introducers_intake_<date>.csv` adds them.
  - The validator and the preflight run first; the insert is one transaction.
  - Each new introducer gets segment `Introducer: savings-group network`, a `VICOBA introducers` plan and one source record.
  - It carries only the routes it publishes. A row with a person's details is quarantined.
  - An existing record is matched, never duplicated.
- **Recording what T1 found.** `--apply-facts data/raw/vicoba/introducer_facts_<date>.jsonl` records each fact with its own source record: a savings-group programme (`introducer_role`) or a VICOBA group-account product (`group_account_product`).
  - A welfare-run organisation stays in its run. The master records the fact on the reference `welfare:<run-id>:<organisation_id>` (facts `entity_type` `welfare_organisation`).
  - The welfare run is read, never written.
- **The introducer's state.** Every introducer has one current `introducer_state`:

  | State | Meaning |
  |---|---|
  | `active` | A verified programme or product is on record. |
  | `to_confirm` | Its savings-group work is unconfirmed. It gets a `VICOBA introducer to confirm` review item and is never an active introducer. |
  | `outside_region` | Kept and held low: no introducer route in the catchment. |
  | `employer_conversation_first` / `welfare_conversation_first` | It already has a conversation, as an employer lead or in its welfare run. Savings groups are raised at that conversation's S4 meeting, never in a second cold message. |

  - The orchestrator's and reviewers' checks are accepted entries in the `introducer_decisions` section of `data/reference/vicoba-introducers.json`, with their source. On 13 October 2026 these were:
    - Yemco Vicoba and Magnet Vikoba: Dar es Salaam Maps listings, so `outside_region`;
    - Trias Tanzania: its Tanzania page names no savings-group programme, so `to_confirm`. The page is robots-disallowed and was read in the browser, so it is tagged risky.
- **Links.** A group is linked to its introducer only through an accepted entry in `data/reference/vicoba-introducers.json` ("links").
  - An intake's `introducer_ref`, `sponsor_ref` or `employer_ref` is only a proposal: `link_vicoba_introducers.py --propose` drafts the entries in `runtime/master/vicoba-introducer-proposals.json` for a person to review.
  - A CDO link must resolve to a ward office (or a council office) in the government run that holds the Community Development post, in the group's council and ward.
  - A CDO route is held until the council's introduction (GA01) is recorded there.
  - A link is a reference, never a copy of the office.
- **Applying.** `link_vicoba_introducers.py` (preview), then `--apply` (one transaction), then `recompute_campus_distances.py --apply`.

**Phones and privacy.**
- A group leader's personal mobile counts only when a public body or the group publishes it for the role. It then enters the reviewed file's `officer_routes` and becomes a role-only contact (no name) with `contacts.role_phone` and the contact fact `phone_basis = published_for_role`. `verify_master.py` fails on a VICOBA contact phone without that basis.
- A number given with consent never enters the repository. It stays in the partnerships call log. The master records only the group fact `phone_basis = consent_recorded <date>`.
- No member names, phones, savings, loans or children are recorded. An offered member list is refused and recorded as `list_refused`.

**Calls.**
- `build_call_sheet.py --vicoba` lists, women's groups first, complete groups only:
  - introducer office lines;
  - group officers' role phones published for the role.

  Each number carries its basis and source, and the builder fails on any other number.
- It skips:
  - welfare-run introducers (called within their own run's conversation);
  - introducers that are not ready.
- The sheet has no column for a name or a number.
- `import_call_results.py --vicoba` writes `data/raw/contact-research/vicoba_calls_<date>.jsonl` with no number and no name. It stops, writing nothing, if any answer holds a phone number, an email or a person's name.
- `link_vicoba_introducers.py --apply` then records the results:
  - consent;
  - a refusal, which suppresses the officer route;
  - the introducer's outcome;
  - the meeting day the committee states;
  - a refused member list.

**Location.** A group's point is its ward's reference point in the government run (`geocode_precision` `ward`). `recompute_campus_distances.py` computes the campus, distance, band and tier from it. A ward-precision distance is an estimate, and drafts never state it.

**Band properties.** The band is computed by `first_touch.vicoba_case()`. It reads these facts on each group, each with one current value, all written by `link_vicoba_introducers.py`:

| Fact | Values |
|---|---|
| `introducer_status` | `linked`, `to_confirm` (named in the intake, no accepted link), `none` |
| `linked_introducer_kind`, `linked_introducer_ref`, `linked_introducer_name` | The primary accepted link (an employer first, then a ready introducer, then by kind), or `none` |
| `linked_introducer_db` | `master`, `government`, `welfare` or `none` |
| `linked_introducer_state` | The introducer's `introducer_state`, or `none` |
| `introducer_ready` | `yes`, or `no: <reason>` (council introduction not recorded, to confirm, outside the region, another conversation first, no published route, possibly closed) |
| `introducer_outcome` | `introduced <date>`, `declined <date>` or `none` |
| `officer_route` | `published_for_role`, `consent_recorded <date>`, `known_through_introducer <date>`, `refused <date>` or `none` |
| `officer_confirmed_on` | A date or `none` |
| `channel` | `call`, `letter` or `email` |

The group's `record_status` follows its links: a group that gains an introducer route and is otherwise complete becomes `complete`.

## Rules the scripts enforce

- **Only what a source publishes for contact purposes.** No contact detail is recorded or presented as found unless a source publishes it, and a person's name is never searched across other sites (a query limited to the organisation's own site, `site:<own domain>`, is not "another site"; decided 11 October 2026). Two decisions of 2 October 2026 widen this:
  - **Public sources.** Besides an organisation's own site, an official register or a parent body, an agent may use public pages that need no login and publish a named business contact: trade-association and chamber member directories, trade-fair exhibitor and buyer lists, government lists of licensed or registered businesses, and a company's own press release, annual report or PDF. LinkedIn and other social profiles, data brokers (ZoomInfo, SignalHire, RocketReach, Apollo, Lusha), review sites and anything behind a login, paywall or bot check stay out.
  - **Email formats and inferred candidates** (decided 11 October 2026; this replaces the candidate rule of 2 October).
    - A domain's email format is recorded in `data/reference/email-formats.json` only when published addresses at the organisation's own domain show it: at least two addresses, of two different people the organisation itself names, following the same pattern (first.last, f.last, flast, firstl, firstlast, first, last). Role inboxes (info@, hr@, md@ …) are never evidence, free-mail domains never get a format, and a domain whose evidence shows two patterns is ambiguous and generates nothing. A domain with one person's evidence is provisional and generates nothing. Only committed sources are read: the databases' contacts and inboxes and the research files in `data/raw/contact-research/`. Each entry keeps its evidence as the pattern each published address shows, the person's record, the source URL and the date read; the addresses themselves stay in the research files and databases they came from. `scripts/contacts/email_formats.py build` proposes the entries and `build --write` writes the file, which a person reviews before it is committed.
    - `scripts/contacts/email_formats.py candidates` may then propose a candidate for the chosen in-country recipient or escalation contact who is a named, verified decision-maker and has no published address. Never for a one-name or incomplete name, initials, a contact with pdpa_risk risky, or a board-only role.
    - A candidate is labelled "inferred from format, unverified", is always low confidence, and lives apart from every published route, in `runtime/` only for every list (`runtime/contacts/inferred-candidates.json`); no database table holds it. It never becomes a draft's route or a contact's email, and never places a lead in a high segment. The master workbook shows only the format (`email_format_to_confirm`), never the address. The 2 October table `candidate_emails` is retired (`email_formats.py retire-table --apply`), and `infer_candidate_emails.py` is removed.
    - A candidate may be checked with one web search for the exact address in quotes. If a public page publishes that exact address for that person, the page is a source and the address is recorded as published, through the normal research files; a page that shows only the pattern, or another person, changes nothing.
    - It is exported only to the separate `<track>-low-inferred` files in `runtime/resend/<date>/` (`export_resend_contacts.py`), each row labelled. Committed files show the format, never the generated address; `email_formats.py check` fails if a generated address is in a tracked file, a draft's route or the reference file.
    - A person confirms it by phone or through the organisation's published route before any use. Once confirmed with a source, it is recorded as a verified route and moves up normally. Send confirmed addresses in small batches and watch for bounces.
- **robots.txt Disallow rules are honoured by the crawler and the search agents.** Rules apply per scheme and host, so a redirect to another host is judged by that host's rules. A 4xx robots.txt means no rules.
  - They are matched as RFC 9309 specifies (`contact_lib.Robots`). The `*` group applies, and repeated groups combine; the longest matching rule decides, Allow wins a tie, and `*` and `$` work as wildcards.
  - Python's `urllib.robotparser` read `Disallow: /?` as `Disallow: /` and ignored wildcards. On 23 September 2026 the fix opened kilivikings.com, which had been skipped. It also closed two sites whose rules forbid all crawling: sunnyadventures.co.tz, and afroplanfoundation.com, whose domain has since expired. Since 24 September 2026 such sites are read with a browser and tagged risky (next rule). sunnyadventures.co.tz was read that way, and its details, including the P.O. Box an earlier merge took from the crawl, now carry the risky flag.
- **A site whose robots.txt disallows crawling is read with a browser and tagged risky.** The crawler never reads such a page. By the user's decision (24 September 2026), the site is opened in the browser as a visitor would open it, reading at most five public pages. What it publishes for contact is then kept and tagged risky:
  - every person from it carries `pdpa_risk: risky`
  - the master gets the review item "Contact research: robots.txt disallows (read with a browser)"
  - the welfare run's organisation record is `risky`, so its drafts never use that route until someone approves it
  - the Flags sheet lists it

  Master drafts are not held, as with an unreachable robots.txt. Bot checks and CAPTCHAs (BitNinja, Cloudflare), logins, 403 and 429 answers, certificate warnings and forms are still never passed or filled in; such a site is recorded as blocked.
- **An unreadable robots.txt is crawled and flagged.** This applies to a server error (5xx) or a network or certificate failure. RFC 9309 would treat such a host as fully disallowed; by decision (23 September 2026) the site is crawled anyway and its details are used. Everything taken from it is flagged "robots.txt unreachable" in three places: the contact-profiles workbook's Flags sheet, a master review item, and the welfare run's notes.
- **Blocks are never worked around.** A block (403, 429, login wall, captcha, TLS failure) is recorded.
- **Page junk and placeholders are removed.** Addresses are cleaned of URL-encoded spaces, zero-width characters and words glued onto the domain (`info@x.comarusha`). Theme and site-builder placeholders (`info@mysite.com`, `+255 712 345 678`) are dropped.
- **Shared values are dropped.** A number or address found on three or more different websites belongs to a shared platform, such as a booking portal or a web designer, and is not used.
- **Hotlines are not routes.** A number that a record's phone `type` labels as a hotline or helpline (for example "mobile; the 24/7 hotline for reporting a case") serves people who need help. It stays in the record as evidence but is never offered as a route, even where another record gives the same number without the label. Agents label such numbers in `type`.
- **Rejected routes are left out.** `data/reference/rejected-routes.json` lists reviewed values that research found but that are not the organisation's route: another organisation's inbox or phone (SOS Kenya's footer served on SOS Arusha's page), a fax, or an inbox on a domain that does not exist. Each entry gives the organisation, the value, the reason, the source and the date. The builder leaves the value out of that organisation's profile and its leads, matching the organisation by name when its ID has changed, so the runs never take it and the company-master merge never adds it. A value already in the company master is corrected through the update skill.
- **Hijacked pages are skipped.** A page with gambling or parked-domain content is not used, even on the organisation's own site, and the site appears on the Flags sheet.
- **Person filter** (`contact_lib.clean_person`). Names may be in any Latin alphabet (Ståle, Zoë).
  - **People a research agent or browser reader recorded.** They are kept in any name form: only in part ("Mogens"), with particles ("Gijs de Raadt", "Ken deLaski"), with several titles ("Rt. Rev. Ludovick Minde") or with a place word as the surname ("Doreen Moshi"). They are kept with any role the source gives, including contacts with no recognised title ("Booking contact"). Only a template name, a role the person no longer holds, or a phone number read as a role is refused (see "Every lead is kept" below).
  - **Decision roles.** These include partners of a firm, a facility's officer in charge, bishops and head teachers.
  - **The rules below apply to names the crawler reads from page layouts.** There, only decision-makers and roles that bear on the outreach are kept (people, administration, programmes, welfare and governance), and the filter drops what is not a current lead of this organisation:
    - template names (for example "John Doe" and the Tailwind stock names)
    - headings, page labels, departments and job titles read as names ("Why Choose Us", "Select Page", "Key Contacts", "Human Resources", "Retired Professor", "French Sales Expert")
    - branch addresses, regions and acronyms read as names ("Jomo Kenyatta Avenue", "Opposite Mosha Filling Station", "North America", "KPP Energy")
    - the organisation's own name read as a person ("Duma Explorer" of Duma Explorers), though a founder the organisation is named after is kept ("Robin Hurt" of Robin Hurt Safaris)
    - public figures ("Tanzania's First Female President")
    - roles held at another organisation:
      - client testimonials ("HR Manager, Mwanzo Corporate Offices, Dar es Salaam")
      - a trustee's own business ("Coffeyville Coffee Company and Hersh's Ice Cream Co-owner")
      - another board ("Board member of Cascades Academy") or a partner NGO ("Founder & Director of CHETI NGO")

      A role that also names the organisation itself is kept, and so is a role in one of its own units ("Head of Leadership and Governance Academy", "Director of Western Wildlife Research Centre").
    - links, sentences, headlines and phone numbers read as roles ("Read a letter from our Executive Director", "Director's Message...")
    - roles the person no longer holds ("Former …", "Immediate Past President", "Chairman Emeritus")
    - staff outside outreach (chefs, guards, drivers, guides, teachers, accountants, volunteers), and their heads ("Chief Security Officer", "Chief Accountant"); a head teacher leads a school and is kept
- **A role that holds another listed person's name is not used:** two people's lines were read as one ("EDWIN NYAKOE NYASANI" with the role "THOMAS TARAKWA ASSISTANT CHAIRPERSON").
- **People named in a sentence are read too:** "founded in 2010 by …", "owned and run by …", "our founder, …", "…, the managing director". A person with a role elsewhere in the sentence ("…, Chairman Grundfos …"), two founders joined by "and", and "the late …" are skipped.
- **The same person written two ways is one person:** "Mrs. Paula Mwansa" and "Paula Mwansa", "Pastor Elisha Z." and "Pastor Elisha Z. Masangwa", or "Paul Pickle" inside "Paul and Shannin Pickle". So is one name spelled two ways in the same post: the same role, and names that differ by one letter in one word of four or more letters ("Prof. Musa N. Chacha" and "Prof. Mussa N. Chacha", both Rector).
  - All their records make one lead. Its name, role and source come from a single record, so every claim stays traceable.
  - A search agent's confirmed record is used first, then the organisation's website (crawled or read with a browser), then an agent record whose identity is uncertain. Within that source, the record with the most senior role is used; on a tie, a 'Name / Role' layout wins over a sentence ("Founder & Managing Director" over "founded by …").
  - Any record can add a work email or phone linked to the person.
- **Every lead is kept; incomplete ones are labelled, never dropped** (the user's decision, 24 September 2026: "better incomplete data labelled incomplete than dropped data").
  - There is no limit per organisation; until 24 September 2026 only six new leads per organisation were recorded.
  - A person a research agent or browser reader records with only part of a name ("Mogens", founder; "Mr. Jeffrey", Head of Marketing; "Prudence T. B") is kept. Its `name_status` says what is missing: "incomplete: one name only" or "incomplete: surname given only as an initial".
    - In the master it is in the contact's verification text and a `name_status` fact, on the Contacts sheet, and in a review item "Contact name incomplete" asking for the full name. Drafts are not held.
    - In the welfare run it is in the contact's notes.
  - A single capitalised word on a crawled page is still not taken as a name, because it is usually a heading or a place.
  - Leads are listed in order:
    1. people a search agent confirmed
    2. the website's people (crawled or read with a browser), ranked by the most senior role in any of their records:
       1. founders, executives, principals, rectors, vice-chancellors and provosts
       2. HR, administration, directors, managers, heads of departments, and the head's deputy or assistant ("Deputy Principal", "Assistant General Manager")
       3. board officers: chairs, presidents, secretaries, treasurers
       4. coordinators, heads of named programmes, social and welfare staff
       5. board members and trustees
- **A website shared by several different organisations:** its people go only to the organisation the domain is named after.
- **Twin records:** the master holds some organisations twice, under the same name or website. A person already on one record is not added to its twin.
- **Merges never overwrite.**
  - They fill only empty fields.
  - A conflicting website goes to review, as does a website field that holds text instead of an address.
  - In the welfare run, the contact-profile records (slice W) only fill blanks.
  - When several welfare records would claim the same new website, only the one whose name the domain carries most keeps it.
- **Personal-domain inboxes:**
  - A named person's personal-domain email is never used as a route; the lead is labelled `risky`.
  - A mailbox made from a person's initials at a domain named after them (vd@vinnie.co.nz) belongs to that person.
  - A company master organisation takes a personal-domain inbox only when the inbox is named after the organisation.
  - Welfare drafts to personal-domain inboxes stay held.
- **Research warnings become review items:** possible closure, hijacked or parked site, website gone, location to check, possible duplicate, fit to check, segment to check (a record filed under the wrong kind of business, such as a hospital recorded as a tour operator), and check before outreach.
  - A possible closure also holds every draft for the organisation, including drafts written after the merge.
  - Nothing is deleted.
- **Held drafts are released only when the route was their sole gap.** Other blockers keep them held: an unmatched map point, a branch overlap, or a possible closure.
- **Try the master changes on a copy first.** `merge_master_contacts.py --apply --database <copy>` and `draft_master_messages.py --database <copy>` write their reports to `runtime/`. Then take a temporary copy of the master, apply, verify, and remove the copy.
- **Sending and automations stay disabled.** New routes only move held drafts to review.

## Agent brief

Give every research agent the following, with its slice file, its search allowance and its output paths.

- **Goal:** for each organisation, fill the organisation profile, and find contact leads who lead or decide for it: founder, director, manager, head, coordinator, HR, administrator, owner, principal. Record every such person, most senior first. Record a person the source names only in part ("Mogens", founder) exactly as given; the builder labels the name incomplete rather than dropping it.
- **Sources for people:** the organisation's own site or report, an official register, a parent body's official page, the organisation's own text on a membership or operator directory (such as TATO's), or a funder's or partner's own page that names the organisation's current leaders. For a funder or partner page, fetch it, quote the sentence that names the person and their role at the organisation, and say in `notes` that the source is a funder or partner. News stories, personal profiles and people-search sites are not sources for people.
- **Already tried:** before searching for an organisation, read its already-tried list (in the prompt or the slice, or `python scripts/research/ledger.py tried --org <organisation_id>`). Do not repeat a query pattern for the same organisation inside the retry window (90 days); use a pattern still open, or fetch the pages an earlier attempt found.
- **Search budget:**
  - Use at most the allowance, and number every search in the log (Q1/40, Q2/40 …).
  - One search per organisation is normal, for example `"<exact name>" Arusha`. Then fetch the organisation's own contact, about or team pages instead of searching again.
  - Never route searches through WebFetch, a browser or a results page.
- **Never record:**
  - personal social-media profiles, home addresses, family details, photos or biographies
  - anything about children, parents or residents
  - party affiliation
- **Facebook:** you may record an official page URL when the organisation's site or a search result links to it, but do not try to read it.
- **Evidence for every fact:**
  - source URL and access date
  - an excerpt of 25 words or fewer
  - whether the page was fetched (`fetched: true`) or only seen as a snippet (`fetched: false`)
- **Identity:** confirm the page is about the same organisation, with the same name and place. Otherwise mark it `identity: "uncertain"` and say why.
- **`pdpa_risk` on every lead:**
  - `low`: a role desk
  - `medium`: a named person in a professional role as published, a named work email, or a mobile the organisation publishes
  - `risky`: a named person on a personal email domain, or anything touching private life
- **Output:**
  - One JSON line per organisation, including those with nothing found. Fields: `db`, `organisation_id`, `organisation_name`, `status` (found, partial, not_found or blocked), `identity`, `searches_used`, `website`, `emails[]`, `phones[]`, `postal_address`, `physical_address`, `socials[]`, `people[]`, `sources[]`, `notes`.
  - A coverage log listing every search and its outcome, the blocked sites, and the organisations not reached. Searches go in a numbered table, `| Q | Query | Organisation | Outcome |`, one row per search with the exact query, so the coordinator can ingest the log into the research ledger. An agent may also append each attempt to its own pending file (`ledger.py append --file runtime/research-ledger/pending/<slice>.jsonl`), never to the ledger itself.
