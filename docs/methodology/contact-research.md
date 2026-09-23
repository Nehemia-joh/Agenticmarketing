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

   Both are cached, so a re-run re-extracts from `runtime/contacts/http-cache/` without the network.
2. **Budgeted search agents, for organisations the crawl could not cover:**
   - Build profiles first (step 3), then run `plan_contact_research.py --date <date> --wave <n> --budget <searches>`. It:
     - picks organisations that still have no published email or phone, have an outreach plan, and no agent has searched for yet (a record that only fetched known pages and found nothing leaves the organisation a candidate)
     - leaves out savings groups (reached through KINEFA), government offices, and closed or out-of-scope records
     - ranks the candidates nearest first and splits the budget over at most four slices
     - writes each slice and its agent prompt under `runtime/contacts/`
   - Give each agent a fixed share of the session's WebSearch cap. Launch at most four agents per wave.
   - Each agent writes `data/raw/contact-research/search_<slice>_<date>.jsonl` and a coverage log in `data/raw/contact-research/coverage/`.
   - The agent brief is below.
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
- **robots.txt is honoured.** A block (403, login wall, captcha, TLS failure) is recorded and never worked around.
- **Hijacked pages are skipped.** A page with gambling or parked-domain content is not used, even on the organisation's own site, and the site appears on the Flags sheet.
- **Person filter** (`contact_lib.clean_person`). Names may be in any Latin alphabet (Ståle, Zoë). Only decision-makers and roles that bear on the outreach are kept: people, administration, programmes, welfare and governance. It drops:
  - template names (for example "John Doe" and the Tailwind stock names)
  - headings read as names ("Why Choose Us", "Core Value", "Master Chef")
  - the organisation's own name read as a person
  - public figures ("Tanzania's First Female President")
  - client testimonials (a role that names another organisation, such as "HR Manager, Mwanzo Corporate Offices, Dar es Salaam")
  - roles the person no longer holds ("Former …")
  - staff outside outreach (chefs, guards, drivers, guides, teachers, accountants, volunteers)
- **At most six new leads per organisation**, most senior first:
  1. founders, executives, principals
  2. HR, administration, directors, managers, coordinators
  3. board officers

  Leads beyond six are counted, not recorded.
- **The same person written two ways is one person:** "Mrs. Paula Mwansa" and "Paula Mwansa", "Pastor Elisha Z." and "Pastor Elisha Z. Masangwa", or "Paul Pickle" inside "Paul and Shannin Pickle".
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
- **Research warnings become review items:** possible closure, hijacked or parked site, website gone, location to check, possible duplicate, fit to check, and check before outreach.
  - A possible closure also holds every draft for the organisation.
  - Nothing is deleted.
- **Held drafts are released only when the route was their sole gap.** Other blockers keep them held: an unmatched map point, a branch overlap, a savings group awaiting Finance, or a possible closure.
- **Try the master changes on a copy first.** `merge_master_contacts.py --apply --database <copy>` and `draft_master_messages.py --database <copy>` write their reports to `runtime/`. Then take a temporary copy of the master, apply, verify, and remove the copy.
- **Sending and automations stay disabled.** New routes only move held drafts to review.

## Agent brief

Give every research agent the following, with its slice file, its search allowance and its output paths.

- **Goal:** for each organisation, fill the organisation profile, and find contact leads who lead or decide for it: founder, director, manager, head, coordinator, HR, administrator, owner, principal.
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
