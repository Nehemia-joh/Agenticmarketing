# Government enrichment, 10 October 2026: coverage log

Run `arusha-government-2026-09`. Goal: who currently holds the posts that decide (council director, District Commissioner, Regional
Commissioner, ward and village executive officers, council education and community development heads), with the official route.
Allowance: 50 web searches (shared session cap). Used: **6 of 50**.

## Deterministic collection first (no search budget)

- `collect_council_sites.py --date 2026-10-10`: the 13 council and regional sites through their public GWF CORE API, one request at a
  time 1.5 s apart, fresh cache (`runtime/government/arusha-government-2026-09/http-cache-2026-10-10/`). All 13 captured; only 404s for
  three missing pages (longidodc `Madiwani`, `Orodha-ya-Madiwani`; arusha.go.tz `region-districts`). No 403, 429, login or CAPTCHA.
- The captures now keep, per news item, the posts named with their holders (`holder_mentions`: post, name as written, date, at most
  25 words). The build names a post from them only when no leadership profile names it; see `build_government_run.apply_holder_evidence`.
- One document fetched by URL already on file (no search): Arusha Region Investment Guide (arusha.go.tz files, pp. 95-96): RC, RAS,
  council directors' boxes, phones and emails, already in `office_contacts_2026-09-23.json`; it lists no District Commissioner offices.

## Searches

| Q | Query | Outcome |
|---|---|---|
| Q1/50 | Rais Samia ateua wakuu wa wilaya Septemba 2026 orodha | Nothing relevant (search engine returned non-Tanzanian pages) |
| Q2/50 | uteuzi wakuu wa wilaya Lugangira Mwikozi Rukia Zuberi | Nothing relevant; showed the GWF CORE public news path `/new/<slug>` on other regions' sites |
| Q3/50 | "Afisa Elimu" Msingi "Jiji la Arusha" 2026 | Nothing relevant |
| Q4/50 | "Mtendaji wa Kata ya Sakina" OR "... Usa River" OR "... Bomang'ombe" | Nothing relevant (Wikipedia ward pages only) |
| Q5/50 | "Ofisi ya Mkuu wa Wilaya" Arumeru "S.L.P" | Nothing relevant (Ruvuma pages) |
| Q6/50 | Afisa Elimu Msingi Halmashauri ya Wilaya ya Meru Usa River 2026 | Nothing relevant (Meru County, Kenya) |

Stopped after Q6: the search engine does not index Tanzanian local-government news, and the official sites' own API carried what the
searches were meant to find. The remaining 44 searches were not used.

## Findings from official news (confirmed by reading the cached item text)

- District Commissioners reshuffled at the end of September 2026: Arusha (Nicodemus Tambo Mwikozi, sworn in 3 October), Arumeru
  (Neema Kichiki Lugangira, sworn in 3 October, took office 9 October), Hai (Rukia Zuber, handover 1 October; Hassan Omary Bomboko
  moved to Mwanga). Recorded in `data/raw/government-research/post_holders_gov_2026-10-10.json`. Moshi, Monduli and Simanjiro DCs
  were last named before 27 September and are marked to recheck (`links.json` `holder_recheck`).
- Moshi Municipal Council's director changed between captures: Bi. Mwajuma Nasombe (23 September) to Bi. Upendo Eric Mangali
  (profile updated 9 October 2026).
- An acting director (Kaimu) of Arusha District Council in March 2026 is not taken as the holder; the profile holder (Seleman Msumi)
  is confirmed in post on 3 October 2026.

## Not reached (for the next wave or the GA01 meeting)

- District Commissioners' office postal addresses, phones and emails (none published on the regional or council sites).
- Heads of Pre-Primary and Primary Education for Arusha City and Meru; community development heads and social welfare officers for
  the four pilot councils (not named in any captured item).
- Ward executive officers: 2 of 128 named (Mnadani and KIA, Hai). Ask each pilot council for the WEO list after the introduction.
- Sites that need a browser read: none required; the public news pages (`https://<host>/new/<slug>`) would give a human-readable
  URL for each item cited here, if a reviewer wants one.
