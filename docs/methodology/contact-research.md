# Contact research

This is how Silverleaf builds contact profiles for the organisations in its three databases (the company master, the welfare run and the government run) and finds contact leads for them. Scripts live in `scripts/contacts/` (catalogue: `scripts/README.md`). Read `skills/silverleaf-create-lead-list/references/research-rate-limits.md` before any network step.

## What a profile holds

- **Organisation contact profile**: website, typed emails (role, general, named, personal domain), typed phones (office, mobile, international), postal and physical address, and official social pages, each with its source.
- **Contact lead**: a named person the organisation itself publishes (its own site, an official register or directory, or a parent body's official page). A lead records:
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
     - leaves out savings groups (reached through KINEFA), government offices, and closed or out-of-scope records
     - ranks the candidates nearest first and splits the budget over at most four slices; `--max-per-slice` keeps only the nearest so one agent's work stays manageable (about 35 to 45 organisations), and the rest wait for a later wave
     - with `--split` as well, a larger slice is divided into balanced parts (`<slice>_a`, `<slice>_b`, ...) of at most that size, each with its own agent, still at most four agents in all
     - writes each slice and its agent prompt under `runtime/contacts/`
   - Give each agent a fixed share of the session's WebSearch cap. Launch at most four agents per wave.
   - Each agent writes `data/raw/contact-research/search_<slice>_<date>.jsonl` and a coverage log in `data/raw/contact-research/coverage/`.
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

## Rules the scripts enforce

- **Only what a source publishes for contact purposes.** No private contact details are inferred. A person's name is never searched across other sites.
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
- **Held drafts are released only when the route was their sole gap.** Other blockers keep them held: an unmatched map point, a branch overlap, a savings group awaiting Finance, or a possible closure.
- **Try the master changes on a copy first.** `merge_master_contacts.py --apply --database <copy>` and `draft_master_messages.py --database <copy>` write their reports to `runtime/`. Then take a temporary copy of the master, apply, verify, and remove the copy.
- **Sending and automations stay disabled.** New routes only move held drafts to review.

## Agent brief

Give every research agent the following, with its slice file, its search allowance and its output paths.

- **Goal:** for each organisation, fill the organisation profile, and find contact leads who lead or decide for it: founder, director, manager, head, coordinator, HR, administrator, owner, principal. Record every such person, most senior first. Record a person the source names only in part ("Mogens", founder) exactly as given; the builder labels the name incomplete rather than dropping it.
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
  - A coverage log listing every search and its outcome, the blocked sites, and the organisations not reached.
