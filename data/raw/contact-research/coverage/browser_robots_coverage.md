# Browser pass: sites whose robots.txt disallows crawling

- **Date:** 24 September 2026 (research round of 23 September 2026).
- **Decision:** by the user's decision (24 September 2026), a site whose robots.txt disallows crawling is opened with a browser, as a visitor would, and what it publishes for contact is taken. Everything taken from it is tagged risky: every named person carries `pdpa_risk: risky`, and the organisation is flagged "robots.txt disallows (read with a browser)".
- **Limits kept:** bot checks and CAPTCHAs, logins, 403 and 429 answers, certificate warnings and forms are never passed or filled in. Pages were read one at a time, at most five per site.
- **Coordinator:** read by the coordinating session itself. No web search was used.
- **Records:** `browser_robots_2026-09-23.jsonl`.

## Targets

These are the 9 sites the crawler recorded as robots-disallowed, plus one page an earlier agent skipped because of its robots.txt.

| Site | Organisation | Outcome |
|---|---|---|
| kitamuhouse.com | Kitamu Africa LTD (master) | Read. The founder (Leah Assenga), an own-domain email, a phone, the street address and official social pages. |
| sibusiso.com | Sibusiso Foundation (master and welfare) | Read, 4 pages. The Executive Director, board chair, programme coordinator and founder; the Tanzania office's P.O. Box, phone and email. |
| safarini.com | Safarini Africa Ltd (master) | Read, 3 pages. Emails, phones, P.O. Box and street address; no leader is named. |
| sunnyadventures.co.tz | Sunny Adventure Safaris Ltd (master) | Read, 4 pages. Emails, landline and mobiles, P.O. Box and street address; the staff page names no one. |
| namiritours.co.tz | Namiri Tours And Safaris (master) | Blocked: BitNinja CAPTCHA, not solved. |
| safaricrewtanzania.com | Safari Crew Tanzania (master) | Blocked: BitNinja CAPTCHA, not solved. |
| shidolyasafaris.com | Shidolya Tours & Safaris (master) | Blocked: BitNinja CAPTCHA, not solved. |
| akshartoursandsafaris.co.tz | Akshar Tours and Safaris (master) | The host answers "Page cannot be displayed" on http and https. |
| afroplanfoundation.com | Afroplan Foundation (welfare) | Expired domain, showing a parked page; nothing belongs to the organisation. |
| tanzaniamissions.com/asante-sana | Asante Sana (welfare) | The site shows "Squarespace - Website Expired"; identity uncertain. |

## Sites that answered the crawler with a server error

Sixteen sites answered the crawl with a timeout or a server error (5xx). These are errors, not refusals, so a sample was opened again with the browser on 24 September:
- kwieco.org: no answer on http or https
- africaviptravel.com: empty page
- tanzaniaporters.org: "503 Service Unavailable"
- kilaweni.com: empty page
- sinonngarashied.or.tz: "WordPress › Error"

All five are still down, so the rest were left for a later crawl; nothing was recorded. Sites that answered 403 or 429, or failed their certificate check, are blocks and were not retried.

## Not recorded

- The founders' personal Facebook and Instagram profiles linked from kitamuhouse.com.
- Safarini's theme-placeholder social links.
- A North America representative's personal Gmail on safarini.com.
- The Dutch and German support foundations' addresses, phones and personal inboxes on sibusiso.com.
