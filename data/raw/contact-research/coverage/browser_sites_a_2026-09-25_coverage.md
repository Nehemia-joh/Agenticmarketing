# Coverage log: browser sites A (2026-09-25)

- **Slice:** `runtime/contacts/slices/browser_sites_a.json`. It holds 2 websites that a plain crawler could not read (script-built pages), covering 2 organisations: 1 master and 1 welfare. robots.txt allows both.
- **Method:** the built-in browser only, in the agent's own tab. For each site the agent opened the start URL, ran the prompt's capture script and read up to 8,000 characters of page text. The page-text tool returns only a page's `<main>` element, so the text of the same page outside `<main>` (header and footer) was also read. At most 4 more contact or about pages from the capture's links were opened, one at a time. No WebSearch or WebFetch calls were made (`searches_used: 0` on both records).
- **Output:** 2 records appended to `data/raw/contact-research/browser_sites_a_2026-09-23.jsonl`, one per organisation. The file already held 26 records from the 2026-09-24 pass and now holds 28. Neither organisation was in it before.
- **Coverage file name:** `browser_sites_a_coverage.md` already exists from the earlier pass, so this log is written beside it under a dated name.
- **Scratch:** `runtime/contacts/agents/browser_sites_a/`. It holds the two record files, the append-and-validate helper and a small script that checks the output file's line endings and encoding.
- **Accessed:** 2026-09-25.

## Summary

| Measure | Count |
|---|---|
| Sites in slice | 2 (2 organisations) |
| Sites read, with the organisation's own content | 1 (Senator Hotel) |
| Domains lapsed or no longer the organisation's | 1 (Upendo Kwanza: registration expired) |
| Sites behind a bot check, or not reachable at all | 0 |
| Records: found / partial / not_found / blocked | 0 / 1 / 0 / 1 |
| Identity confirmed / uncertain | 1 / 1 |
| Emails | 1 general (info@senatorhotel.co.tz) |
| Phone numbers | 1 Tanzanian mobile (+255 766 007 599) |
| Postal addresses | 1 (Senator Hotel: P.O.BOX 15666, ARUSHA-TANZANIA) |
| Physical addresses | 1 (Senator Hotel: Father Babu Road, Arusha, Tanzania) |
| Socials | 1 (Senator Hotel Instagram) |
| People | 0 (neither site names a person) |

**Status rules** (as in the earlier pass). `found`: identity confirmed, at least one email or phone, and a named leader or decision-maker read on the organisation's own page. `partial`: new routes or people, but not both. `not_found`: the site was read but publishes nothing usable. `blocked`: a bot check, a lapsed, parked or unrelated domain, or a site with no content.

## Site by site

| # | Site (final URL) | Organisation | Pages read | Outcome |
|---|---|---|---|---|
| 1 | upendokwanza.org (http://upendokwanza.org/) | Upendo Kwanza (welfare, ORG_ce4f6b18bdaa1684) | home on http, with and without www | **blocked**. https://upendokwanza.org/ and https://www.upendokwanza.org/ do not load. Both http versions show Namecheap's page: 'Domain registration has expired.', with renewal steps and domain-auction adverts. Nothing was clicked. The domain no longer serves the organisation, and the crawler's 'script' flag came from this registrar page. Website field left blank. |
| 2 | senatorhotel.co.tz (https://www.senatorhotel.co.tz/) | Senator Hotel (master, Ob4b69891baaf) | home, /about, /contact | **partial**. info@senatorhotel.co.tz; +255 766 007 599 ('General info'); P.O.BOX 15666, ARUSHA-TANZANIA; Father Babu Road, Arusha; Instagram @senatorhotelarusha. No owner, manager or staff is named, and there is no team page. The capture offered only /about and /contact, so 3 pages were read. |

## Blocks and what was not done

- **Expired domain (1):** upendokwanza.org. Recorded as blocked with identity uncertain. No renewal, sign-in or auction link was clicked.
- **Forms:** Senator Hotel's Contact page has a 'Send Message' web form. It was not filled in or submitted.
- **Not recorded:** the web designer's credit link on the Senator Hotel footer ('Designed by In Access Media'), because it is a supplier, not a route to the hotel.
- **Browser tabs:** the agent's first navigation opened the shared pane on a blank tab, then worked only in its own tab. It closed both of its tabs at the end and did not touch the other browser agent's tab.

## For a person to check

1. **Upendo Kwanza:** its domain registration has expired. Check whether the organisation still operates, and whether it has a new website. The X and LinkedIn pages already in its contact profile came from an earlier search, not from this site, and were not checked here.
2. **Senator Hotel, second phone:** the contact profile also holds +255 767 606 204, which appears nowhere on the hotel's own home, About or Contact pages. Its source needs confirming.
3. **Senator Hotel, Facebook:** the footer's Facebook icon links to the Instagram URL, so the site gives no Facebook page. The Facebook page already in the profile came from another source.
4. **Senator Hotel, decision-maker:** the site names no general manager or owner, so that still needs another source.
5. **Senator Hotel, size:** the About page gives two room counts (90 guest rooms and suites, and 34 rooms), so the hotel's size is unclear.
