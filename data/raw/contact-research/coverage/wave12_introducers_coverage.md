# Wave 12: introducers (employer, sector and HR bodies), 2026-10-02

Brief: `runtime/contacts/prompts/wave12_introducers.md`. Output: `data/raw/contact-research/introducers_wave12_2026-10-02.jsonl` (21 lines, one per body). Scratch: `runtime/contacts/agents/wave12_introducers/`.

Pages were read with the cached, robots-honouring fetcher in `scripts/contacts/contact_lib.py`. The scratch wrapper `rp.py` decodes Cloudflare-protected addresses in place and lists mailto/tel links; `links_inline.py` shows which mailto sits beside which name. `build.py` checks every excerpt against the cached page text (each is exact and 25 words or fewer) and every email against the page. All passed.

## Searches (25 of 40 used)

| # | Query | Outcome |
|---|---|---|
| Q1/40 | APHFTA official website contact | aphfta.org URLs found; the main site did not resolve. The mail.aphfta.org contact page was read. |
| Q2/40 | Confederation of Tanzania Industries contact secretariat | cti.co.tz secretariat page found and read |
| Q3/40 | Tanzania HR professionals board / HR Professionals Act | Only Kenya, Zambia and other countries came up; no Tanzanian statutory HR registration board |
| Q4/40 | ATE northern zone office Arusha | Three ATE pages found and read (northern-zone meeting, about, legal team) |
| Q5/40 | "arusha@ate.or.tz" | Only an ATE membership-portal page; the address was not confirmed on any ATE page |
| Q6/40 | Tanzania HR management professionals board (HRMPB) Dodoma | Nothing for Tanzania |
| Q7/40 | Tanzania HR managers association / HR forum Arusha | Leads: THRAPA, TAPAHR, Women HR Association (WHAT) |
| Q8/40 | THRAPA website | thrapa.or.tz found; not reachable (see blocks) |
| Q9/40 | Bodi ya Wataalamu wa Rasilimali Watu (Swahili) | Nothing relevant |
| Q10/40 | Tanzania Society of Travel Agents contact | tasota.or.tz found and read |
| Q11/40 | Tourism Confederation of Tanzania secretariat | tct.co.tz named; the domain shows only an empty listing |
| Q12/40 | Arusha association of lodges and camps | No such body found (only HAT and TATO member pages) |
| Q13/40 | Arusha Regional Business Council | No Arusha council found; the Arusha-based East African Business Council (EABC) was found and read |
| Q14/40 | TNCC Arusha chapter chairman / executive officer | TNCC news page naming the TCCIA Arusha Chairman, read |
| Q15/40 | site:eabc-online.com secretariat staff | EABC management page, read |
| Q16/40 | KIATO Moshi secretariat contact | Only directory or aggregator listings (not sources); no KIATO site |
| Q17/40 | site:ate.or.tz Arusha AICC zone office | Confirms the AICC building only (from the ATE news page); no zone-office email or phone on ATE pages |
| Q18/40 | HAT northern chapter Arusha chairperson | HAT board page read; no northern chapter |
| Q19/40 | Tanzania Hunting Operators Association | tahoa.org did not resolve; not recorded |
| Q20/40 | TAPAHR website | tapahr.org read |
| Q21/40 | Women HR Association of Tanzania | what.or.tz read |
| Q22/40 | Institute of Human Resource Management Tanzania | Nothing for Tanzania |
| Q23/40 | KIATO official website / chairman | No official site found |
| Q24/40 | Responsible Tourism Tanzania contact | rttz.org found; HTTP 500 |
| Q25/40 | "TCCIA Arusha" executive officer office | Chapter sites tcciaarusha.or.tz and tcciaarusha.org found; both failed DNS |

No search was refused. No search went through WebFetch, a browser or a results page.

## Bodies and what was found

| Body | Area | Status | Named people | Named work emails |
|---|---|---|---|---|
| ATE (national) | national | found | 6 | 0 (info@, membership@ only) |
| ATE Northern Zone, Arusha | northern zone | partial (no zone email or phone on ATE pages) | 2 | 0 |
| TNCC (national) | national | found | 6 | 4 |
| TNCC Arusha regional chamber | Arusha | found (email and mobile, chairman) | 1 | 0 |
| TNCC Kilimanjaro regional chamber | Kilimanjaro | partial (email; phones duplicate Kigoma's) | 0 | 0 |
| CTI (national) | national | found | 5 | 4 |
| CTI Arusha/Moshi office | northern zone | found (office address and phone, outreach manager) | 1 | 0 |
| TPSF | national | found | 5 | 0 |
| TATO | Arusha | found | 3 | 2 role mailboxes (ceo@, marketing@) |
| HAT | national | found; no northern chapter | 2 | 0 |
| Tanzania Bankers Association | national | found | 2 | 0 |
| APHFTA | national | partial (main site unreachable) | 0 | 0 |
| CSSC | national (Northern Zone office in Arusha, no details) | found | 3 | 0 |
| TASOTA | national | found | 2 | 0 |
| TAHA (horticulture) | Arusha | found | 2 | 0 |
| EABC | Arusha | found | 2 | 0 |
| TAPA-HR | national | found (public-service HR) | 3 | 0 |
| Women HR Association of Tanzania | national | found | 3 | 0 |
| THRAPA | national | not reached | 0 | 0 |
| Tourism Confederation of Tanzania | national | not found (empty site) | 0 | 0 |
| Responsible Tourism Tanzania | Arusha | not reached (HTTP 500) | 0 | 0 |

Totals: 21 bodies, 48 named people, 10 named work or role emails as published beside the name.

## Blocks and failures (not worked around)

- tpsftz.org: HTTP 403. The official tpsf.or.tz was read instead.
- tccia.com now redirects to a gambling site. Do not use hq@tccia.com, which TNCC's About page still prints.
- No DNS from this machine for: aphfta.org, www.aphfta.org, aphfta.tz, aphfta.or.tz, thrapa.or.tz, www.thrapa.or.tz, tcciaarusha.or.tz, www.tcciaarusha.org, tahoa.org, kiato.or.tz, kiato.co.tz, tzpha.com, responsibletourismtanzania.org, tanzaniatouristboard.go.tz.
- Timeout: tanzaniatourism.go.tz (associations list).
- WebFetch refused: www.aphfta.org, www.thrapa.or.tz, www.tanzaniatourism.go.tz.
- HTTP 500: www.rttz.org (home, who-we-are, responsible-operators).
- Empty server listing: tct.co.tz, tct.or.tz.

## Seen only in search snippets, deliberately not recorded

- An ATE Arusha zone-office email, room number and phones, credited to a third-party directory.
- A TCCIA Arusha regional executive secretary and office address. The chapter site failed DNS.
- THRAPA's Dodoma postal box and email, KIATO's address and phone, RTTZ's contacts, and TCT's email and phone.

## Data-quality flags

- CTI: the Arusha/Moshi Outreach Manager's email and phone links repeat the Director of Policy's, so they are not credited to him.
- TNCC: Kilimanjaro's phones are identical to Kigoma's.
- APHFTA: the contact page carries stray template text and a misspelt second address.
- TAHA: two different member counts (25,900 on Who We Are; 1,600 in the CEO biography).
- HAT: the board page looks out of date.

## Not reached, or no such body found

- No statutory HR-professional registration board for Tanzania was found (three searches).
- No Arusha lodges-and-camps association, Arusha business council or HAT northern chapter was found.
- Leads for a later wave: retry THRAPA, APHFTA, RTTZ and the TCCIA Arusha chapter site with the browser.
