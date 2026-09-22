# Welfare-lead research brief (shared by every research agent)

Template used by `scripts/welfare/plan_research.py`, which fills in the run and date and writes the rendered copy to `runtime/welfare/<run-id>/research-brief.md`.

Run: `{run_id}` · Research date: {research_date} · Client: Silverleaf Academy (Tanzania)

## 1. Objective

Find **every welfare institution** that could become a paying institutional customer of Silverleaf Academy, and every publicly published data point about it, near Silverleaf's campuses. A welfare institution pays school fees for children in its care or programme. Also capture published business contacts at those institutions, funder links, and public parent or guardian enquiries (see §6).

Silverleaf: private school network. Levels: daycare (from 12 months), pre-primary KG1–KG2, English-medium primary Standard 1–7 (to about age 14). Fees are published (TZS 1.6m–1.85m a year) and paid in four instalments.

## 2. Catchment

Campuses (approximate coordinates; lat, lon):

| Campus | Lat | Lon | Levels |
|---|---|---|---|
| Usa River (Momela Road, Meru District) | -3.3645 | 36.8632 | K1–K2, Std 1–7, boarding |
| Arusha City (Sakina, Arusha–Nairobi Road) | -3.3528 | 36.6613 | K1–K2, Std 1–7 |
| Ilboru (Arusha–Moshi Road) | -3.3465 | 36.6922 | Daycare, K1–K2 |
| Kijenge (Kijenge Road) | -3.3837 | 36.7100 | Daycare, K1–K2 |
| Boma Ng'ombe (Mahakama Road, Hai District, Kilimanjaro) | -3.3342 | 37.1383 | Daycare, K1–K2 |

Target: anything within about **25 km** straight-line of any campus (the outer school-transport band). In practice: Arusha City Council, Arusha District Council (Arumeru West), Meru District Council (Usa River, Tengeru, Maji ya Chai, Kikatiti, King'ori…), Hai District (Boma Ng'ombe, Machame, Masama, Rundugai, KIA), Siha (Sanya Juu), and Moshi town and western Moshi rural (Moshi town is about 23 km from Boma Ng'ombe). You do not need to compute distances; record the most precise location you can find. Record institutions that turn out to be farther away too, but set `catchment_note` (e.g., "Karatu — likely outside 25 km").

## 3. What counts as a welfare lead

| Segment | Include | Examples of subtype |
|---|---|---|
| Welfare residential care | Institutions where children live | children's home, orphanage, baby/infant home, small group home, children's village |
| Welfare family-based programme | Programmes that pay for or arrange schooling for children living with families | child/education sponsorship programme, OVC programme, kinship or foster-care support, community-based care |
| Welfare specialised centre | Centres for children with particular needs | disability or rehabilitation centre, street-children centre, rescue/safe house for girls, centres for deaf/blind children |
| Welfare funder | Organisations that fund or operate the above | foreign charity supporting a named home, diocese/church social services, foundation, corporate CSR programme |

Out of scope (record only if found incidentally, with `segment: "Out of scope"` and a reason): day care centres and nurseries (competitors), homes for older people, hospitals, government retention homes and approved schools, general schools. If a welfare institution **runs its own school**, still record it, and set `runs_own_school: "yes"`; it may be a competitor or partner rather than a customer.

## 4. Hard exclusions — never record these, not even as "risky"

- Any child's name, photograph, age linked to an identity, story, case history, health or HIV status, or sponsorship profile ("Meet Neema, 7…"). Paraphrase at organisation level instead ("cares for about 40 children aged 3–17").
- Anything about the parents, relatives or family circumstances of children in care.
- Private individuals' home addresses.
- Content from private or closed groups, content behind a login, or content you could only see by signing in.
- Details found by searching a **private individual's name** across other sources. Do not compile personal information across sources. For contacts, record only what each source publishes for contact purposes.

Never contact anyone, submit a form, sign in, or pay for access.

## 5. Data-protection risk label (required on every record)

`pdpa_risk` is one of:

- `low` — organisation-level facts; generic organisational routes published by the organisation (info@ or office@ at its own domain, office landline, contact form).
- `medium` — a named individual in a professional role as published by the organisation, an official register or their own professional profile for that role; a named work email at the organisation's domain; a mobile the organisation publishes as its contact line.
- `risky` — any private individual (parents, guardians, relatives, volunteers); a personal-domain email (gmail, yahoo, hotmail…) or personal mobile of a named person; data from personal social-media profiles; individuals listed by a regulator for accountability rather than contact (e.g., charity trustee lists); anything touching household circumstances or children.

Add `pdpa_risk_reason` (one short sentence). Tanzania's Personal Data Protection Act 2022 treats data related to children as sensitive and (per DLA Piper's summary) requires explicit consent for direct marketing, which is why named people and private individuals are flagged.

## 6. Parents and guardians (only for the agent assigned slice H)

Public enquiries by adults in the catchment seeking school places, school-fee support, sponsorship, or care arrangements for children they are responsible for. Record the post as published: display name exactly as shown (or "anonymous"), platform, URL, date, a paraphrased request with no child identifiers, locality, and contact details **only if the author deliberately published them in that post**. Always `pdpa_risk: "risky"`. Do not look the person up anywhere else.

## 7. Evidence rules

- Prefer the organisation's own website, official registers (government, NGO registers, foreign charity regulators), and reputable published sources; then directories; then social media pages of the organisation.
- **Fetch the page** (WebFetch) to confirm facts wherever possible. Set `fetched: true` only if you fetched and read that page yourself today. If a fact comes only from a search-result snippet, set `fetched: false`.
- `verification_status`: `verified` (key facts confirmed on a fetched official/own page dated or evidently current), `needs_review` (conflicting, stale or partly confirmed), `unverified` (snippet-only or low-quality source), `historical` (evidence older than about 3 years with no current sign of operation).
- `evidence_basis`: `official`, `published`, `public_profile`, `public_post`, `directory`, `research_note`.
- `evidence_excerpt`: 25 words or fewer; paraphrase; any verbatim fragment under 15 words.
- Never invent a URL, email, phone number, number of children or date. Leave unknown fields as null or "".
- Record the publication or last-updated date of the source when visible (`source_date`), and the latest sign of activity you saw (`latest_activity_date`, e.g., a dated news post).
- Red flags to note (in `red_flags`): volunteer fees to "care for orphans", children presented for donations or tourism, no registration information, dead website, conflicting names or addresses. These are recorded, not judged.

## 8. Output format

Write **one JSON object per line** (JSONL, UTF-8) to the output path given in your task. Record types:

### organisation
```json
{"record_type":"organisation","slice":"A","organisation_name":"","alternative_names":[],"segment":"Welfare residential care","subtype":"children's home","care_model":"residential","description":"","operator_or_umbrella":"","religious_affiliation_published":"","founded":"","registration_published":"","licence_claim":"","address":"","locality":"","ward":"","district":"","region":"","latitude":null,"longitude":null,"geocode_basis":"","website":"","public_emails":[],"public_phones":[],"social_media":{"facebook":"","instagram":"","x":"","youtube":"","linkedin":"","other":""},"children_served_published":null,"children_served_evidence":"","children_served_as_of":"","age_range_published":"","gender_served":"","services":[],"schooling_arrangement_published":"","runs_own_school":"unknown","funding_model_published":"","known_funders_or_partners":[{"name":"","relationship":"funds","source_url":""}],"foreign_charity_registrations":[{"country":"","register":"","number":"","latest_income":"","currency":"","financial_year":"","source_url":""}],"volunteer_programme":"unknown","volunteer_fee_published":"","safeguarding_policy_url":"","staff_count_published":"","latest_activity_date":"","latest_activity_evidence":"","red_flags":[],"catchment_note":"","sources":[{"url":"","title":"","source_date":"","accessed_on":"{research_date}","evidence_basis":"published","fetched":true,"facts_supported":["name","phone"],"evidence_excerpt":""}],"verification_status":"verified","pdpa_risk":"low","pdpa_risk_reason":"","notes":""}
```

### contact (one per person or role desk; link by `organisation_name`)
```json
{"record_type":"contact","slice":"A","organisation_name":"","contact_name":"","role":"","role_certainty":"confirmed","emails":[],"email_type":"named|role|shared|personal_domain","phones":[],"phone_type":"office|mobile|whatsapp|unknown","profile_url":"","channel_attribution":"who published this route and where","sources":[{"url":"","title":"","source_date":"","accessed_on":"{research_date}","evidence_basis":"published","fetched":true,"facts_supported":["name","role","email"],"evidence_excerpt":""}],"verification_status":"verified","pdpa_risk":"medium","pdpa_risk_reason":"","notes":""}
```

### relationship (funding or operating links between organisations)
```json
{"record_type":"relationship","slice":"G","from_organisation":"","to_organisation":"","relationship_type":"funds|operates|refers|partners_with","sources":[{"url":"","title":"","source_date":"","accessed_on":"{research_date}","evidence_basis":"published","fetched":true,"facts_supported":["relationship"],"evidence_excerpt":""}],"verification_status":"verified","pdpa_risk":"low","pdpa_risk_reason":"","notes":""}
```

### enquiry (slice H only)
```json
{"record_type":"enquiry","slice":"H","enquiry_author_display":"","author_type_stated":"parent|guardian|foster carer|relative|unknown","enquiry_type":"school place|school fees support|sponsorship|children's home placement|daycare|other","enquiry_date":"","date_qualification":"exact|month_only|year_only|unknown","request":"","locality":"","platform":"","source_url":"","contact_published_in_post":{"phone":"","email":""},"contact_attribution":"","current_relevance":"current|recent|historical|unknown","sources":[{"url":"","title":"","source_date":"","accessed_on":"{research_date}","evidence_basis":"public_post","fetched":true,"facts_supported":["request"],"evidence_excerpt":""}],"verification_status":"unverified","pdpa_risk":"risky","pdpa_risk_reason":"","notes":""}
```

Rules: one organisation record per distinct institution (merge what you learn about the same institution into one record; list every source). Keep strings short and factual. Validate before finishing: every line must parse as JSON (e.g., run a short Python check).

## 9. Coverage log

Also write a Markdown coverage log to the path given in your task: every query and source you tried, what was blocked (e.g., Facebook login wall), counts of records written by type, and known gaps or leads you could not confirm.

## 10. Final reply

Reply in under 200 words: counts by record type, the 5 strongest leads (name + why), and the main gaps. Do not paste the records into your reply.

## 11. Rate limits and your budget

- **Web search is capped per session and shared.** The WebSearch tool has a session cap (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`; 200 in the 2026-09 run) that every research agent in the session draws from. Your task states your allocation. Number each query in your coverage log as `Q<n>/<allocation>` and stop at your allocation.
- **If a search fails with a budget or limit error, stop searching.** Record it in the coverage log. Do not route searches through WebFetch, a browser or a search-engine results page to get around the cap.
- **After your searches are spent,** continue only with WebFetch on URLs you have already found (organisation sites, their contact and about pages, register pages you already have links to).
- **Pace WebFetch** to about one request every 2 seconds on the same site. If a site returns 403, 429 or a login wall, record it as blocked and move on; do not retry in a loop.
- **Known blocked or unreadable sources (2026-09):** UK Charity Commission register (403), JamiiForums (blocks automated reading), Facebook groups (login), Reddit (not fetchable), Tanzanian council sites on the GWF CORE framework (pages render in JavaScript; deep links redirect to the home page), the NGOs Information System map (JavaScript; the coordinator collects it with a script).
- **Write as you go.** Append records to your JSONL file as you confirm them, so work survives if you are stopped early, and keep the coverage log current.

Full guidance: `skills/silverleaf-create-lead-list/references/research-rate-limits.md`.

