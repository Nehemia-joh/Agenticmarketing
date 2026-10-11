# Slice Z coverage log: five new Arusha welfare leads, 2026-10-11

Round Y (2026-10-10) saw five Arusha NGOs on their own Idealist listings that the run did not hold. Adding newly seen welfare leads
has been approved by the user since 2026-09-26. Output: `data/raw/welfare-research/research_Z_new_leads_2026-10-11.jsonl`
(9 records: 5 organisation, 4 contact). Reviewed decisions in `data/runs/arusha-welfare-2026-09/links.json`: one `nis_to_org` link with
evidence (14690, Kukua Pamoja Tanzania) and one `official_personal_inboxes` entry (Twiga Vision Tanzania, through
`apply_research_reviews.py`). The run config now reads `research_*_2026-10-11.jsonl`.

## Outcome

All five are Arusha City child-welfare programmes within the 25 km catchment, so all five are kept as `Welfare family-based programme`.
Each one is scored and drafted. Each draft is held (`WA00`) for its recorded red flags.

| Organisation | Score (tier) | Location | Route | Addressee | Held for |
|---|---|---|---|---|---|
| Twiga Vision Tanzania | 55 (P2) | Mianzini (locality) | twigavisiontz@gmail.com (reviewed as official) | Daniphord Mwajah, Director and founder | volunteer fees incl. daycare roles; KHM Daycare closed by authorities; two P.O. Box numbers |
| Kukua Pamoja Tanzania | 55 (P2) | Mianzini (locality) | +255 685 318 217 | none confirmed (organisation route) | own domain dead |
| Rafiki Initiative Organization | 25 (P3) | Ngarenaro (locality) | +255 683 048 599 | none (founder named 'Gilbert' only) | own domain dead; USD 10/day volunteer fee; places differ |
| Bird Charity Tanzania | 25 (P3) | Arusha (town) | +255 787 881 122 | none (director's address is personal-domain, risky) | evidence historical (2015 profile); own domain dead |
| Hope Children's Support Organization | 5 (P4) | Arusha City (town) | +255 679 600 129 | none named | own domain dead |

## Kukua Pamoja: re-rated through a reviewed decision

`classify_ngo_register.py` rates register entry 14690 `medium_projects_only`, which gives a fit of `unlikely`. Its name and vision do not
mention children; only its project list does ('Child Education Sponsorship Program', 2022). The classifier was left unchanged. Under
the same broader rule ('child … sponsorship' in a project title), only one other catchment entry would change, KIJANA KWANZA (690).
So the rating is not wrong in general.

The organisation's own Idealist profile publishes the Fill the Gap Sponsorship Program, which covers children aged 2-25 from
kindergarten to university. The research record carries that evidence, and `nis_to_org` 14690 links the register entry with the
evidence written under `nis_to_org_evidence`. The register row keeps the classifier's own rating, and its matched organisation is now
Kukua Pamoja Tanzania (likely).

## Searches: 14 of 15 used

| # | Organisation | Query (shortened) | Result |
|---|---|---|---|
| Q1/15 | Rafiki | Rafiki Initiative Arusha idealist | Idealist profile and volunteer listing (404), Worldpackers and GoAbroad listings |
| Q2/15 | Twiga | "Twiga Vision" Arusha children | Idealist profile, twigavision.org |
| Q3/15 | Bird Charity | "Bird Charity" Arusha | birding pages only |
| Q4/15 | Bird Charity | Idealist "Bird Charity" Arusha (idealist.org only) | Idealist profile |
| Q5/15 | Bird Charity | "Bird Charity" + director / site name | nothing newer than the Idealist profile |
| Q6/15 | Hope Children's | "Hope Children's Support" Arusha | other Hope bodies only |
| Q7/15 | Hope Children's | "Hope Children" Arusha (idealist.org only) | Idealist profile |
| Q8/15 | Kukua | "Kukua Pamoja" Arusha | Go Overseas reviews, NGObase profile (403) |
| Q9/15 | Kukua | Kukua Pamoja Tanzania (idealist.org only) | Idealist profile |
| Q10/15 | Rafiki | "Rafiki Initiative Organization" Gilys daycare | GoAbroad page of Gily's Children's Foundation (relation unconfirmed) |
| Q11/15 | Hope Children's | "Hope Children's Support Organization" Tanzania | nothing new |
| Q12/15 | Kukua | Kukua Pamoja Tanzania director/founder sponsorship | Go Overseas reviews naming the director 'Mr. Ayoub'; a private fundraiser (not used) |
| Q13/15 | Twiga | "Twiga Vision Tanzania" registration | no registration number published anywhere found |
| Q14/15 | Hope Children's | "Hope Children's Support" social pages | nothing |

One search was left unspent.

## Deterministic sources (no search budget)

- NGO register: the run's catchment extract (fetched 2026-09-22) holds Kukua Pamoja (14690). The full map file of the same date
  (`runtime/welfare-research/nis_mapping_full.json`, main checkout, read-only) also lists RAFIKI INITIATIVE ORGANIZATION (21593) and
  Hope Children's Support Organization (20930).
  - These two pins are not coordinates. One is a Google Maps link to Musoma St, Arusha; the other reads 'Arusha Arusha'. For that
    reason both entries are outside the 30 km extract.
  - Three profiles were fetched one at a time, a few seconds apart: 21593, 20930 and 14690. They gave 00NGO/R/8219 (2025-03-24),
    00NGO/R/7928 (2024-12-18) and 00NGO/R/3308 (2022-05-18).
  - No register entry was found for Twiga Vision or Bird Charity.
- Pages were read with `scripts/contacts/read_page.py`, which caches pages, waits 1.5 s per site and checks robots.txt:
  - the five Idealist profiles
  - twigavision.org: home, childcare, news and volunteers pages
  - the Worldpackers host listing for Rafiki
  - Go Overseas pages for Kukua: a programme page, a review and the provider reviews
  - the GoAbroad programme page of Gily's Children's Foundation

## Not recorded

- Volunteer reviewers' names, and a private individual's GoFundMe fundraiser for Kukua.
- Twiga's sponsor family in Germany (private individuals).
- Anything about individual children.
- Gily's Children's Foundation's GoAbroad page (USD 750 for 4 weeks; 'more than 80' and 'over 200' children). Rafiki's Idealist
  profile names 'Gilys daycare' as a partner project, and the run already holds Gily's Children Foundation. That page is about an
  organisation already in the run, so nothing from it was added here. Whether the two are linked is left for a reviewer.
- Dead-domain inboxes: info@birdcharitytz.org (on the fetched Idealist page), and info@hopechildrenssupport.org and
  info@kukuapamojatanzania.or.tz (search snippets). They are kept in notes and not recorded as routes.

## Blocked or unreadable (not worked around)

- These domains do not resolve: rio.or.tz, birdcharitytz.org, hopechildrenssupport.org and kukuapamojatanzania.or.tz. The local
  resolver timed out and the fetch tool answered ENOTFOUND, while twigavision.org and elct.or.tz resolved normally in the same session.
- ngobase.org/profile/396057 (Kukua Pamoja) returned HTTP 403. The head's name, Ayoub Patrick Hassan, was seen only in a search
  snippet, so it is recorded with role certainty 'unknown' and is not used as the addressee.
- These pages returned HTTP 404:
  - the Idealist volunteer listings of Rafiki (d42632f9…) and Twiga (2402a684…)
  - the GoAbroad programme page of Rafiki
- The GoAbroad provider page of Rafiki redirects to the providers index.

## Needs a browser read or a call

- The Facebook page facebook.com/TwigaVisionTanzania and the Instagram account twigavisiontanzania could show recent activity. They are
  recorded only as links.
- A call to Kukua Pamoja (+255 685 318 217) or Rafiki (+255 683 048 599) could confirm who leads each organisation and where it works.
  The listing names Rafiki's founder only as 'Gilbert'.

## Gaps

- Kukua Pamoja's register map pin (-3.3861, 36.5744) is not a location. Nine Arusha-district entries in the extract share it, so the
  record is placed by its Idealist locality, Mianzini. A search snippet from NGObase (403) gives Ilikiurei Street; that is unconfirmed.

- No children-served figure was found for four of the five. Bird Charity's '13-14' comes from a 2015 profile.
- No register number was found for Twiga Vision or Bird Charity.
- Rafiki's and Hope Children's register numbers are recorded in `registration_published` only, so `nis_reg_no` stays blank. Their
  register entries are not in the catchment extract because the pins are not coordinates.
