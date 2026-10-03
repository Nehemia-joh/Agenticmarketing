# Slice V coverage log: flag, location and personal-inbox checks (2026-10-03)

Targets: `runtime/contacts/slices/welfare13_C.json`, 96 held homes, programmes, centres and funders. Output: `data/raw/welfare-research/research_V_flag_location_checks_2026-10-03.jsonl`.

## Result
- 96 of 96 targets reached and written (organisation records, each with a `review` field), plus 2 contact and 2 relationship records. 100 lines, all parse as JSON, no duplicate organisation.
- Verification status: 30 verified, 48 needs_review, 10 unverified, 8 historical.
- 24 organisations publish a personal-domain (gmail/yahoo/outlook/hotmail) address as their own contact: `official_personal_inbox: true`. Several of these addresses belong to a supporter or funder rather than the home (Enyorata, Tumaini, OKAT, Amani/Friends of Amani UK); the notes say so.
- Read with `scripts/contacts/read_page.py` logic (cached, spaced, robots honoured) through scratch helpers in `runtime/contacts/agents/welfare13_V/`; NGO register profiles (nis.jamii.go.tz) read for 42 targets.

## Searches (6 of 30 used)
- Q1/30 "Peace House Arusha Tanzania children orphanage"
- Q2/30 "Jericho Orphanage Home Usa River Arusha"
- Q3/30 "Wariba Child Compassion Arusha Tanzania NGO" (nothing about the organisation found)
- Q4/30 "Upendo Children's Home Precious Blood Sisters Moshi Tanzania ELCT"
- Q5/30 "Catholic Archdiocese of Arusha social services children education office contact"
- Q6/30 "Faraja Forward Tanzania Moshi Faraja school"
No search was refused. Searches were used only for the six targets with no website; every page cited was then fetched, except the Guardian (Tanzania) article for Upendo Children's Home, recorded as `fetched: false`.

## Blocks and unreadable pages (recorded, not worked around)
- robots.txt disallows: afroplanfoundation.com (Afroplan Foundation).
- HTTP 429: samaritanvillageorphanage.org; hopehometrust.org.uk (Kitaa Hope Home); osotuwa.org contact and about pages.
- HTTP 403: tirnanogchildrensfoundation.com (Kao La Amani); farajaschool.org; ippmedia.com (Guardian article).
- Expired TLS certificate: elctdme.or.tz. TLS handshake failure: neemainternational.org.
- DNS failure: stjosephorphanage.co.tz; peacehouseafrica.org.
- Empty or script-only pages: farajaorphanage.org, mkombozi.org, oneheartsource.org (menu only).
- Free-form notes: GuideStar profile (Peace House Africa) read as a public directory; no login used.

## Findings by kind
- Inboxes confirmed official (own site or the funder's site publishes the address): Save Africa, Emusoi, Tumaini (via funder Love Our Tanzania Family), LOHADA, Enyorata (via funder Little Souls), Fruitful, GP-COSU, Havilah, Tabasamu, Bethlehem, Habashabi, Living Water, Mosses Confort Home, Moshi Kids Centre, Born to Learn, KAHE Home, KIWAKKUKI, HALEVAFRICA, PAC, Children Concern, OKAT (US supporter), Tupendane, others as flagged in the file.
- Inbox not confirmed or contradicted: WEHAF (site shows info.wehaf@ not ester.wehaf@), Light in Africa (address only in a visitor comment, truncated), Arusha Children Center (site shows a person's yahoo address), Christ Hope (printed domain christopetanzania.com differs from the held one), Amazing Grace (only a personal-looking address on site), Upendo Face, Osotuwa, CHETI, Faraja Forward, Upendo Children's Home.
- Active now (dated 2025-2026 evidence): Child First Initiative, Amani, Emusoi, Enyorata, Tuleeni (register projects to Sept 2026), Tupendane, Ummu Aisha, Neema Village (Jan 2025), New Stars, Kafika House, Moshi Kids Centre, Halima, KIWAKKUKI, HACRET, TAWREF, and others.
- Looks inactive or closed: Mkombozi (blank site), Rainbow Centre (blog ends 2010), Sun of Hope (nothing after about 2018), OMAWA (2018), Hope Orphanage Center, Save Africa (about 2019), Peace House (dead domain, US entity's exempt status revoked), Jericho (dead domain, 2013 listing), Treasures of Africa (own site says its Moshi orphanage ran 2007 to 2021).
- Newly resolved locations: Tuleeni (Uru Kusini), Tupendane (Sakina), KIWAKKUKI (Korongoni), TAWREF and Songambele (Majengo, Moshi), Mosses Confort Home (Kisambre), Kilimanjaro Foundation (Uru-Shimbwe), HACRET (Kitutu Road), Kilimanjaro Childlight (Ushirika Street), Tanzania Youth Support (Maji ya Chai), Kikatiti Happy Watoto (Kikatiti), Habashabi and Living Water (Kisongo), GP-COSU (Ilboru ward), Child First Initiative (Ngabobo ward), Rainbow Ridge (Maili Sita).
- Outside the 25 km band per own pages: Tanzanian Children's Fund (Oldeani, Karatu), Children Concern (Mto wa Mbu), Tanzania School Foundation (Mlangarini about 30 km), Jericho Karatu listing.
- Note on funders: Foundation Le Solstice's own contact page says it accepts no unsolicited funding requests by email.

## Targets whose own evidence stayed thin
Kitaa Hope Home, Kao La Amani, Samaritan Village, St Joseph's Orphanage (Kiserian), ELCT Meru Diocese, Neema International, Afroplan Foundation, Faraja Orphanage: blocked or unreadable, nothing cleared, no source recorded for several. Targets with village or ward still unpublished are marked in each record's `review.flags_still_hold`.

## Rules followed
No person was searched by name; only organisation-level pages and registers; no one was contacted; no login, CAPTCHA or bot check worked around; databases untouched. No flag was cleared without a fetched page showing it no longer holds.
