# Coverage log: wave 4, welfare funders and specialised centres

Run date: 2026-09-23. Slice: `runtime/contacts/slices/wave4_welfare_funders_specialised.json` (14 organisations: 2 specialised centres and 12 funders, nearest first). Results: `data/raw/contact-research/search_wave4_welfare_funders_specialised_2026-09-23.jsonl`.

Search budget: 14 WebSearch calls. The order of work was:

1. Fetch known sources, the organisations' own sites and the pages the welfare run cites (no search).
2. Search only where that gave nothing, one organisation per query.

All pages were read with this agent's own polite fetcher (scratch copy under `runtime/contacts/agents/wave4_welfare_funders_specialised/`):

- robots.txt was checked for every host, including each redirect hop, with RFC 9309 matching (longest rule wins; `*` and `$` wildcards).
- Requests to one host were at least 2.5 seconds apart, and nothing was retried at once.
- A page that answered HTTP 429 got at most one later attempt, 4 to 12 minutes on.
- The WebFetch tool and the browser were not used.
- In all: 90 requests to 21 hosts, plus one page reused from the shared crawl cache (Amani's contact page, fetched earlier today).

The run paused once after Q11 (a stalled stream) and resumed; the records were written before the rest of this log.

## Summary

- **Researched:** 14 of 14 organisations (one JSONL line each).
  - found: 8
  - partial: 2 (Lift-the-lid, Peace House Africa)
  - not_found: 3 (Emayani, Be Part Of Their Story, Focus On Aids)
  - blocked: 1 (Weily Tribe Foundation)
  - Identity confirmed for 13. Uncertain for 1: Emayani vulnerable people's center.
- **Searches used:** 11 of 14. The session's search limit was never refused. Q12 to Q14 are unused and can go back to the coordinator.
- **Needs met:**
  - Named decision-maker: 7 of 7 (Mesha's Village, Arusha Children Center, Private Explorers, Bahati Trust, Kili Vikings, Hope Home Trust, Friends of Amani UK).
  - Published route: 1 of 7 (New Day Foundation). Still missing for Emayani (identity), Lift-the-lid, Be Part Of Their Story, Focus On Aids, Peace House Africa and Weily Tribe Foundation.
- **Contact leads recorded:** 15 people in 9 organisations, all from fetched pages or an official register.
  - `medium`: 14
  - `risky`: 1 (Lift the Lid's founder, whose own-name inbox is the only one the organisation publishes)
- **Totals recorded:**
  - 8 emails: 3 general, 1 named work, 4 personal-domain inboxes named after the organisation.
  - 9 phones, 19 official social pages and 11 websites.
- **New routes for the welfare run:**
  - New Day Foundation: named inbox and office phone.
  - Private Explorers: inbox, two Tanzanian mobiles and the Njiro Road office.
  - Arusha Children Center: Gmail inbox, a second mobile and a P.O. Box.
  - Bahati Trust and Friends of Amani UK: first phone (UK mobiles from the Charity Commission register).

## Searches

| # | Query | Organisation | Outcome |
|---|---|---|---|
| Q1/14 | `"Be Part Of Their Story" Wharton NJ` | Be Part Of Their Story Inc | Nothing for the charity: Wharton Club of NJ, borough pages, and a restaurant using the phrase as a slogan |
| Q2/14 | `"Focus on AIDS" Los Angeles foundation Tanzania` | Focus On Aids | Nothing under this name: AIDS Healthcare Foundation, APLA Health, EGPAF and similar |
| Q3/14 | `"New Day Foundation" Tulsa Oklahoma` | New Day Foundation Inc | EIN 73-1486736 matches. Facebook page (not read) and the old domain ndfworld.com, which redirects to **newdayfoundation.org**: executive director with a named inbox and the office phone |
| Q4/14 | `"Peace House Africa"` | Peace House Africa | No website or route. Official LinkedIn company page and Facebook page (not read); a 2011 article and directories not used |
| Q5/14 | `"Weily Tribe Foundation"` | Weily Tribe Foundation | ACNC charity register entry (timed out twice, not read) and a second domain, weilytribe.com.au (not registered). ChangePath directory not used |
| Q6/14 | `"Emayani" Sombetini Arusha` | Emayani vulnerable people's center | Only Emayani Foundation (MEGA Complex, town centre) and Sombetini ward pages. Identity stays uncertain |
| Q7/14 | `"Be Part of Their Story" orphanage Moshi Tanzania` | Be Part Of Their Story Inc (second search) | Nothing for the charity; other Moshi homes and volunteer sites |
| Q8/14 | `"Weily Family Foundation"` | Weily Tribe Foundation (second search) | Only weilytribe.com and unrelated Weil family foundations |
| Q9/14 | `"Emayani vulnerable people"` | Emayani (second search) | Only Emayani Foundation's own pages (women's business training); no page for a Sombetini centre |
| Q10/14 | `"Lift the Lid, Inc" Westport Connecticut nonprofit schools` | Lift-the-lid | The organisation's own pages and Facebook page; a December 2025 fundraiser page read (no contact details). ZoomInfo, GuideStar and Holdings not used |
| Q11/14 | `"Arusha Children Center" Arusha homeless youth` | Arusha Children Center (still active?) | Only its 2013 blog and the 2021 Idealist listing; other results are different organisations |

Q12 to Q14 were not used. No domains were guessed and no search-results pages were fetched.

### Reached without a search (searches_used = 0)

- **Mesha's Village.**
  - The own site's team page, read on one later attempt after HTTP 429, gives the founder and president and five other officers; six were recorded.
  - Its home page gives the Gmail inbox and a US phone.
- **Private Explorers.**
  - The Tuleeni partners page, cited by the welfare run, links www.privateexplorers.com.
  - Its About page names the founder and director and confirms that 20% of profits fund Tuleeni.
  - Its Contact page gives the inbox, two mobiles and the Njiro Road office.
- **The Bahati Trust.**
  - The own home page names the founder, who also signs the Executive Director messages.
  - The Charity Commission register lists her as Chair and gives a UK mobile.
- **Kili Vikings.**
  - The crawler had marked the site robots-disallowed, but that came from a parser misreading (see Crawler finding).
  - Its About page says Charlie Richard leads the company.
- **Hope Home Trust.**
  - The own pages name no trustees.
  - The Charity Commission register gives the Chair and confirms the Yahoo inbox.
- **Friends of Amani UK.**
  - Amani's Global Network page links the charity's own site, www.friendsofamani.co.uk.
  - Its board page gives the Chair and Treasurer; the register confirms the Chair and gives a UK mobile.

## Blocked or unreadable sources

- **HTTP 429 (Wix sites; not bypassed).** Wix seems to rate-limit this machine across all its sites, and other wave-4 agents were running in parallel.
  - Read on one later attempt:
    - meshasvillage.com/meet-the-team (12 minutes on)
    - hopehometrust.org.uk/thetrust (8 minutes on)
    - weilytribe.com/pages-sitemap.xml (4 minutes on)
  - Not retried: weilytribe.com/goals.
- **Timeouts:** acnc.gov.au (the ACNC charity register, served through Akamai).
  - robots.txt and the Weily Tribe Foundation entry both timed out on two tries four minutes apart, probably bot protection.
  - Not tried again and not worked around.
- **Domains that do not exist (DNS):**
  - arushachildrencenter.org (named on the centre's blog)
  - weilytribe.com.au (a Q5 result)
  - peacehouseafrica.org (checked again; it has been gone since wave 1)
- **robots.txt:** no page read was disallowed.
- **Charity Commission register:** answered HTTP 200 today, and its robots.txt allows everything. The rate-limits reference lists it as HTTP 403 in 2026-09.
- **Facebook, Instagram, LinkedIn, X and TikTok:** recorded only from the organisations' own sites or search results; never read.
- **Directories and data brokers not used as sources:** Cause IQ, Instrumentl, ZoomInfo, GiveFreely, Candid, Daffy, Yahoo Local, GuideStar, GreatNonprofits, ChangePath and Holdings.
- **ProPublica:** its IRS data pages were used only for organisation status (Be Part Of Their Story, Focus On Aids). Their officer names are not recorded.

## Crawler finding (for the coordinator)

- **The problem:** `crawl_org_websites.py` recorded kilivikings.com as robots-disallowed, and no page was read. Its robots.txt has the common WooCommerce/Yoast rule `Disallow: /?`.
- **Why:** Python's `urllib.robotparser` drops the `?` and reads the rule as `Disallow: /`, which blocks the whole site.
- **The correct reading:** under RFC 9309 the rule only blocks root URLs with a query string. The About, company profile and contact pages are allowed, and this agent read them.
- **Effect:** other sites with the same rule may also have been skipped. `contact_lib.robots_state` / `allowed` would need a longest-match parser to fix this. Not changed by this agent.

## Data-protection decisions

- **Residential addresses left out; town only:**
  - Bahati Trust (Beaconsfield)
  - Hope Home Trust (Brighton)
  - Friends of Amani UK (a house name in a village near Devizes)
  - New Day Foundation's street address appears only in a local directory, so it was not used.
- **Personal-domain inboxes:**
  - Inboxes named after the organisation are recorded as `personal domain`: Mesha's Village (Gmail), Arusha Children Center (Gmail), Hope Home Trust (Yahoo), Friends of Amani UK (Gmail). Welfare drafts to them stay held.
  - Lift the Lid publishes only its founder's inbox at her own-name domain. It is on her lead, labelled `risky`, and is not an organisation route.
  - The Arusha Children Center director's two personal webmail inboxes are not recorded; his lead carries the centre's own mobile instead.
- **Contact details not recorded:**
  - Arusha Children Center:
    - bank-transfer details
    - role inboxes at its non-existent domain
  - Hope Home Trust: the register's phone entry, which is not a valid UK number.
  - Private Explorers: a Kenyan number that appears only on Tuleeni's page.
  - Lift the Lid: the founder's personal Instagram and TikTok accounts.
  - Social links on a site that point to another organisation's accounts (Kitaa Hope Home's Facebook on the trust's site; Amani's X and YouTube on the Friends of Amani UK site).
- **People not recorded:**
  - Two Mesha's Village committee chairs beyond the six-lead cap, and two student interns.
  - Plain trustees and board members: 3 at Bahati, 2 at Hope Home Trust, 3 at Friends of Amani UK.
  - Staff named by first name only: Kili Vikings' operational director, Private Explorers' operations manager.
  - The seven names without roles on the Arusha Children Center team page.
  - A template team profile on the Kili Vikings site.
  - Officers known only from IRS filings.
- **Private life not recorded:**
  - biographies, employers, education and birthplaces
  - family relationships (Mesha's Village, the Bahati Trust, Friends of Amani UK)
  - church membership, religious titles and other trusteeships
  - the Arusha Children Center director's life story
  - the location of a Lift the Lid fundraiser held at a private home
- **Children:** nothing about children, young people or families is recorded. Stories on the Mesha's Village, Arusha Children Center and Hope Home Trust pages were ignored.

## Identity cautions and warnings

- **Possible closure:**
  - **Be Part Of Their Story Inc:** still tax-exempt, but its FY2023 return shows revenue $0 and expenses $25.
  - **Focus On Aids:** not on the IRS's most recent list of tax-exempt organisations; its FY2022 return shows revenue $0.
  - **Peace House Africa:** exemption revoked and domain gone.
- **Check that it still operates:** Arusha Children Center. Its blog's last post is from July 2013, and the only later trace is a 2021 Idealist listing.
- **Location or fit to check:**
  - **Bahati Trust:** works in Dar es Salaam, outside the Arusha-Kilimanjaro area.
  - **New Day Foundation:** the current site centres on its City of Hope base and does not mention Tanzania; its Moshi link dates from 2011-2012 (flagged as doubtful fit).
  - **Weily Tribe Foundation:** its Tanzania support dates from about 2017.
- **Identity uncertain:** Emayani. Two searches and the foundation's full sitemap show only Emayani Foundation's women's business training; nothing ties it to the Sombetini map point.
- **Duplicates or related records:**
  - Kili Vikings is the same company as the master's KILI VIKINGS LIMITED (Ocbc0a898c461), whose contacts list Charlie Richard with a guide's role.
  - Hope Home Trust funds Kitaa Hope Home (welfare record ORG_35d77a9ce929f214).
  - Friends of Amani UK supports Amani Centre for Street Children, Moshi.
  - Private Explorers funds Tuleeni Children's Home.
- **Strong fits for school places:**
  - **Mesha's Village:** pays private-school fees in Arusha and has a Tanzania operations lead on the ground.
  - **Private Explorers:** an Arusha company that funds Tuleeni's school fees and uniforms.
  - **Hope Home Trust:** pays the Kitaa Hope Home children's education in Moshi.

## Organisations not reached

None: all 14 were researched. Needs still unmet are listed in the Summary.

## Suggested next steps

1. **Weily Tribe Foundation:** open its ACNC register entry by hand for the contact details and responsible persons it publishes: https://www.acnc.gov.au/charity/charities/620c583b-3aaf-e811-a960-000d3ad24282
2. **Emayani:** confirm by phone whether the Sombetini map point belongs to Emayani Foundation.
3. **Arusha Children Center:** confirm the centre still operates before any outreach.
4. **Kili Vikings robots misreading:** fix the robots parser in the crawler, and recheck any site recorded as robots-disallowed that has a `Disallow: /?` rule.
5. **Charity Commission register:** update the note in the rate-limits reference; it answered normally today.
6. **Lift-the-lid:** decide whether the founder's own-name inbox may be used, since it is the only route the organisation publishes.
7. **Unused searches:** give Q12 to Q14 to another slice.
