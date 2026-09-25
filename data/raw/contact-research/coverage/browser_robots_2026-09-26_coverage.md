# Browser pass: sites whose robots.txt disallows crawling: coverage log (2026-09-26 pass)

Slice: `runtime/contacts/slices/browser_robots.json` (1 site, 1 organisation; robots.txt disallows crawling). By the
user's decision (24 September 2026) such a site is read with a browser as a visitor would, and every person taken from
it is tagged `pdpa_risk: risky`. Method: the built-in browser in a tab of its own, one page at a time, at most 5 pages
per site. No forms, logins, CAPTCHAs, bot checks or cookie acceptance; no web searches. Accessed 2026-09-26. Output:
1 line appended to `data/raw/contact-research/browser_robots_2026-09-23.jsonl` (the earlier pass's 11 lines are
unchanged; its log is `browser_robots_coverage.md`).

| # | Site | Organisation | Outcome | Pages read | What was found / why blocked |
|---|------|--------------|---------|------------|------------------------------|
| 1 | samequalitiesfoundation.org | THE SAME QUALITIES FOUNDATION (SQF) (welfare ORG_2e899e23820d298d) | blocked | 1 (the bot-check page only) | https://www.samequalitiesfoundation.org/ served a "Bot Verification" page ("Verifying that you are not a robot..."). It was not interacted with, waited out or worked around. No other scheme or host was tried, because the site answered. No site content was read and nothing was recorded. |

## Summary

- Sites: 1 (1 organisation). Read: none. Blocked: 1 (a bot check).
- Found: no emails, phones, addresses, social pages or people, so no one was tagged risky. Record: blocked, identity
  uncertain only because nothing on the site could be checked (the domain matches the name).
- The browser pane was closed when the pass began, so opening it on the start URL gave this pass its own tab. Right
  after the check page's text was read, the tab list showed that tab on the bare domain (samequalitiesfoundation.org),
  which suggests the check redirects by itself. That page was not viewed, and the tab was closed at once. Other
  agents' tabs were not touched.
- For a person to check: the organisation still has no contact route. Leads already on record: its Facebook page
  https://www.facebook.com/samequalitiesfoundation.org/ (from wave 7's search result, not read) and its NGO register
  profile https://nis.jamii.go.tz/ngo_profile/4833 (Arusha). A person can open the site in an ordinary browser, where
  the check may clear by itself.
