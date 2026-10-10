# Slice X coverage log: leaders and routes for medium-confidence drafts, 2026-10-10

Targets: the 17 welfare drafts the Resend export rated medium on 6 October 2026 ("organisation inbox addressed to the team; promote with a named
leader"), then the high- and medium-priority homes, programmes and funders among the low and no-email rows whose only blocker is a missing
named leader or a missing or wrong route (rows held for red flags, closure, location or a funder's missing relationship were left out).
Output: `data/raw/welfare-research/research_X_leaders_routes_2026-10-10.jsonl` (21 records: 19 contact, 2 organisation reviews).
Reviewed decisions: `data/runs/arusha-welfare-2026-09/links.json` (`official_personal_inboxes` for From Hearts 2 Hands and Mesha's Village via
`apply_research_reviews.py`; new `rejected_routes` for Inuka and CHETI NGO).

Method: organisations' own pages first with `scripts/contacts/read_page.py` (cached, robots honoured, about 1.5 s per site); PDFs linked from
an organisation's own site read through the same cached fetcher; WebFetch only for one PDF the fetcher truncated (Giving Smiles 2024 report).
No browser was used. No login, form, bot check or block was worked around.

## Searches: 12 of 50 used

| # | Query (shortened) | Result |
|---|---|---|
| Q1/50 | "Candenez" Arusha director OR founder | no match |
| Q2/50 | "Ereto East Africa Foundation" director OR founder | no match |
| Q3/50 | "Zorah Organization" Tengeru director | no match |
| Q4/50 | "Laughter of a Child Foundation" Watoto Kicheko | Idealist listing (no names) |
| Q5/50 | YWAM Arusha Tumaini children's ministry | World's Children sponsor page: "Leader: Beatrice and Jeff" (recorded, first names only) |
| Q6/50 | "Emusoi Centre" Arusha director 2026 | the centre's own June 2026 newsletter, signed by its management committee (recorded) |
| Q7/50 | "St. Mark's" children's home Usa River contact | no match (other Usa River homes only) |
| Q8/50 | "HopeCare" Arusha Boma Road | no match |
| Q9/50 | "Little Oasis Foundation" Tanzania founder | no match |
| Q10/50 | "Arusha Children's Effort" New Zealand email | NZ Charities Register CC45344: its email is vd@vinnie.co.nz (same as the site); no new route |
| Q11/50 | "Mother Kevina" Kijenge Arusha | only the Mama Kevina Hope Centre in Same (a different place); nothing used |
| Q12/50 | "Watoto Kicheko" Njiro director founder | no names |

38 searches left unspent: the remaining gaps are small organisations that publish no leader anywhere the search index reaches.

## Pages read and outcome

- Compassion International Tanzania: cit.or.tz Governance & Leadership (Mary Lema, National Director; Zelote Lukumay, Senior Manager of
  Partnership) and contact page (info@tz.ci.org; media contact only). The run holds two Compassion records with the same name (programme and
  funder); contacts link by name to the funder record, so the programme record's draft stays addressed to the team (see the report).
- Foerderverein URRC e.V.: urrc.de "Verein" page (1. Vorsitzender Wolfgang Hertrich; 2. Vorsitzende) and Impressum. Home towns not recorded.
- Giving Smiles e.V.: transparency page (1. Vorstand Katherina Campe, 2. Vorstand Miriam Vogt) and 2024 annual report PDF (their addresses;
  CFI co-founder "Nuruana").
- Big Future Foundation: board page (Promise Shayo, Chairperson & Founder).
- Small Steps for Compassion: board page (Shannin Pickle President/Founder spickle@, Paul Pickle ppickle@, others) and contact page
  (info@). Shannin Pickle's record merges with an earlier one that carries her free-mail address, so it stays risky and the draft goes to
  Paul Pickle.
- Imaniworld: Spain's National Register of Associations certificate (8 May 2023) linked from its own site (president Lourdes Porredón Fontán).
- Capital International (Isle of Man): About us (Anthony Long, Group Chairman); Huruma Project page names no programme lead.
- SOS Children's Villages Tanzania: Our Leaders (Thomas Kipingili, National Director), Arusha village page (national office inbox), contact
  page; ATE member directory read (gives an HR-type address only; not used).
- Emusoi Centre: about, our-founder and June 2026 newsletter (founder-director died 30 April 2026; management committee named).
- From Hearts 2 Hands: contact and about pages (organisation-named gmail inbox; reviewed as official).
- Mesha's Village, Arusha Kids Trust: inbox evidence from slice Q (3 October); Arusha Kids Trust's site answered HTTP 429 and was not re-read.
  Its decision was not applied: the inbox sits on Kathy Green's contact record, so the draft stays held (verification rule).
- Arusha Children's Effort: contact page and the NZ Charities Register: the only email is vd@vinnie.co.nz on the director's own domain.
  Not released: a named person's own-domain inbox stays held under the methodology.
- No leaders published: candenez.or.tz (about, contact), eretoea.org (its "team" block is theme placeholder names: not recorded),
  thelittleoasisfoundation.org (story, contact, FAQ), zorah.or.tz (about, contact, partner, volunteer), watotokicheko.com (about, mission,
  contact, foundation, adopting), ywamarusha.org (leadership team names without roles: not recorded), hopeandsoul.org.uk (about, contact,
  news, policies: founder named only as "Hope"; the safeguarding contacts are reporting lines on personal domains, not recorded).

## Blocked or not readable

- UK Charity Commission register (Hope and Soul, 1173832): HTTP 502 to the page reader, HTTP 403 to WebFetch. Not retried.
- hopeandsoul.org.uk/meet-the-team/: HTTP 404.
- arushakidstrust.com: HTTP 429.
- Giving Smiles 2024 report: the cached fetcher stops at 2 MB, so the PDF was read once through WebFetch's saved copy.
- Needs a browser read (script-built or empty to the page reader): saintmarkskids.org (St. Mark's, Usa River; no route yet).

## Corrections applied

- `data/reference/rejected-routes.json` was never applied in the welfare pipeline: SOS Kenya's inbox and phone stayed on SOS Children's
  Village Arusha, and dead-domain inboxes (info@candenez.org, contact@mshikamano.or.tz, info@tanzaniayouth.com, greg@kilimanjaro-children.org)
  were still drafted to. `consolidate_research.py` now removes them (13 values).
- Inuka's route was CHETI NGO's gmail; CHETI NGO's was Inuka's hello@ inbox. Both are now rejected for the wrong organisation.
