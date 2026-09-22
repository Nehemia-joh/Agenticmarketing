# Silverleaf — Partner Lead Generation Method

**Prepared:** 6 September 2026
**Companion to:** *Scope of Work — Agentic Marketing System*; *Business Context Dossier*; *Marketing Observations*
**Status:** Method note plus a worked prototype. The prototype is in `Silverleaf - Partner Lead List v2.xlsx` in this folder — start at the **Priority - enriched** sheet.

---

## 1. What the CEO asked for, and what the data says back

The brief was: compile a list of safari companies and savings groups within a set radius of the Silverleaf campuses, so campaigns can be sent to them.

Having built it, three things came back that change the shape of the problem.

**The radius is not the filter.** 379 of 476 TATO member companies sit within 25 km of a campus, and 320 are within 5 km. Arusha's tour-operator industry is concentrated in a few square kilometres that contain three Silverleaf campuses. A radius filter removes Moshi, Dar es Salaam, Mwanza and Zanzibar operators — about 20% — and almost nothing else. Distance is nearly free as a criterion, which means it cannot do the qualifying work the brief assumed it would.

**Size is the filter, and it is not in any dataset.** What determines whether a safari company is worth a conversation is how many salaried local staff it employs — those are the parents. Nothing public carries that number. Not TATO, not OpenStreetMap, not the licensing register. Every desk-built score is therefore a proxy, and proxies here are weak.

**The directory is biased against exactly the companies you want.** TATO runs two record formats. Newer and smaller operators fill in a rich profile; long-established firms have a thin, older-format entry that the obvious parser reads as empty. On the first pass, Leopard Tours, Simba Safaris, Shadows of Africa, Ranger Safaris, Thomson Safaris, Nature Discovery and Serengeti Balloon Safaris all landed in the bottom tier — because their entries looked sparse, not because they are small. They are among the largest employers in the sector.

Fixing it took a second parser and a pass over each thin record's detail page. That moved most of them where they belong: Leopard Tours now tops the list at 96, with Simba Safaris, Shadows of Africa, Serengeti Balloon and Nature Discovery all in tier A. Two remain low for honest reasons — Thomson Safaris' entry lists a US office and phone number, and Ranger Safaris' carries no contact details at all. Both need a manual lookup.

The general lesson matters more than the fix: **a list built from the archive pages alone under-represents the best targets, and looks completely fine while doing it.** Worth remembering if this is ever handed to a data vendor.

The practical consequence: **desk research produces coverage, not qualification.** It gets you 476 named, contactable, geo-tagged organisations in an afternoon. Turning that into a ranked target list takes an enrichment pass — reading each organisation's own website for a staff number, a named decision-maker and a direct address.

That pass has now been run on 62 priority organisations. See Section 2.

---

## 2. The enriched shortlist

62 organisations — the long-standing TATO members, the largest Arusha operators, and the major hospitals, universities and colleges in the catchment — had their own websites read one by one. Every field is sourced to the exact page it came from. Nothing was inferred: where a site publishes no staff number, the headcount column is blank rather than estimated.

What came back:

| | |
|---|---|
| Organisations enriched | 62 |
| With a direct email | 49 |
| With a Tanzanian phone | 50 |
| With a **named** senior contact | 40 |
| With a published staff number or counted team page | 16 |
| **With an existing school or education programme** | **36** |
| Dead or wrong website in the TATO directory | 7 |

Three things stand out.

**The largest employer in the catchment is a hospital, not a safari company.** Mount Meru Regional Referral Hospital publishes "a dedicated team of over 650 staff" and sits 2 km from the Kijenge campus. Add University of Arusha (150 staff, 5.6 km from Usa River), NM-AIST (119), Arusha Lutheran Medical Centre (150 beds, runs its own nursing school) and Selian Lutheran (160 beds), and the institutional segment outweighs the entire tour-operator segment on payroll.

**More than half the shortlist already funds schools.** 36 of 62 publish an education or community programme. That is not a nice-to-have — it is the opening line of the conversation. The strongest examples:

- **Leopard Tours** — the Leopard Foundation has an Education & Awareness arm that donates desks to primary schools. The company schedules "a fleet of 225 busy vehicles" from an office 1.2 km from the Kijenge campus. Best single first call on the list.
- **Safaris-R-Us** — co-founded by Gemma Sisia, who founded The School of St Jude. The site actively promotes St Jude and Orkeeswa. No warmer door exists in Arusha.
- **Serengeti Balloon Safaris** — employs "over 70 of our staff from communities adjacent to the Parks" and has built a classroom, a headmaster's house and a girls' lavatory block at Robanda.
- **Serengeti Big Cats Safaris** — runs its own NGO and has built a water tower, kitchen and toilets for three schools, funded by USD 20 per traveller.
- **Africa Dream Safaris** — "over 100 individuals, most local Tanzanians"; already supports School of St Jude, Peace House Orphanage and POLI Village School.
- **Elewana Arusha Coffee Lodge** — Land & Life Foundation has given over USD 300,000 to primary schools near its properties in five years.
- **Arusha Technical College** — already runs ATC-SACCOS and other staff-welfare bodies, which is a ready-made mechanism for a payroll-linked benefit.

**Seven directory websites are wrong or dead**, including Kilimanjaro Outfitters (the listed domain is an unrelated US blog), Yembi Adventure (listed as a general business directory), and Anderson's (listed under .co.za; the real domain is .co.tz and is a placeholder). Worth knowing that TATO's website field is not reliable.

The workbook's **Priority - enriched** sheet carries all of this, banded P1 (call first, 11 organisations), P2 (20), P3 (24) and X (7, no usable contact). Unlike the desk score on the TATO sheet, these bands rest on evidence, so they can be trusted.

---

## 3. The sources, and why two are needed

| Source | Gives | Withholds |
|---|---|---|
| **TATO member directory** (tatotz.org) | 476 organisations, 456 emails, 459 phones, TATO category, membership vintage | Coordinates. Locations are free text: "Sakina Kwa Idd", "Njiro Block D", or just "Arusha" |
| **OpenStreetMap** (Overpass API) | 241 employers within 25 km with exact coordinates — hospitals, banks, universities, colleges, hotels and lodges, NGOs, government offices | Contacts. Only about a quarter carry a phone or email |

They are complementary in a useful way: TATO knows who to call and not where they are; OSM knows where everything is and not how to reach it. Together they cover the two segments that matter — the tourism industry, and every other formal employer in the same catchment.

Two further sources were checked and set aside for now. The **TALA licence register** (Ministry of Natural Resources and Tourism) is the legally authoritative list of licensed operators, but it is not published as a downloadable file; TATO membership requires a valid TALA licence, so TATO membership is a serviceable proxy. **SafariBookings** and similar review sites carry review counts, which measure tourist-facing popularity rather than local payroll, so they would not improve the ranking in the way that matters.

---

## 4. How the radius is defined

Not as an arbitrary circle. Silverleaf already publishes school-transport fees in bands: 0–5 km, 6–10, 11–15, 16–20, 21–25 km, at TZS 55,000 to 100,000 per month. Those bands are the natural definition, for two reasons. The 25 km outer edge is where the school bus already stops going, so it is the real edge of the catchment. And a lead's band tells you what the school run would cost that family — which is a live input to the conversion conversation, not just a sorting key.

Every lead is assigned to its nearest campus and stamped with its band.

**Caveats, stated plainly.** Campus coordinates are neighbourhood centroids, not surveyed GPS pins, so distances are ±1–2 km. They are straight-line, not drive-time, which understates the Arusha–Moshi corridor. And 267 members show "Ilboru" as nearest campus only because members whose stated location is bare "Arusha" default to the city-centre centroid, which happens to fall nearest Ilboru — those rows mean "central Arusha", not "near Ilboru". Getting the five real campus pins from Silverleaf fixes the first two and costs nothing.

---

## 5. Savings groups: a different problem, not a harder version of the same one

There is no public register of VICOBA groups. Not a paywalled one, not a hard-to-find one — it does not exist. VICOBA are community-level associations known to ward and district Community Development Officers (*Maafisa Maendeleo ya Jamii*), and that knowledge lives in district offices, not online.

SACCOS are different: they are formally registered co-operatives, and the Tanzania Cooperative Development Commission publishes registration statistics and annual reports at ushirika.go.tz. Those give regional counts rather than member lists, but a district-level register can usually be obtained by asking the Regional Cooperative Office in Arusha.

So the honest answer is that this segment is sourced by relationship, not by scraping:

1. Arusha City Council and Meru District Council community development offices, for the wards nearest each campus. Hai District Council for Boma Ng'ombe.
2. NGO intermediaries who already organise savings groups at scale and hold the relationships — SEDIT, who originated the VICOBA methodology, CARE Tanzania, Aga Khan Foundation.
3. Churches, mosques, market vendor associations, boda boda associations — the same organising unit under different names.
4. NMB and CRDB branch managers, who run chama account products and know the groups even though they cannot share customer data.

The workbook has a capture template for this, with an example row showing the shape of a good record.

It is worth the fieldwork. School fees are among the main things Tanzanian savings groups save for, and Silverleaf already bills in four instalments — which maps onto a group's payout cycle almost exactly. This is likely the highest-conversion segment on the brief, and the only one that cannot be bought as data. Zuhura Msangi's expansion role and Mariam Haji's partnerships remit are the natural owners.

---

## 6. Widening past the brief

The CEO named two segments. The same 25 km catchment contains a third that is larger and easier to reach: every other formal employer with a payroll.

Within 25 km of a campus, OpenStreetMap alone shows Mount Meru Regional Hospital, Arusha Lutheran Medical Centre, the Aga Khan University Hospital, AICC Hospital, Selian Lutheran, St Elizabeth; the Nelson Mandela African Institution of Science and Technology, University of Arusha, Tumaini Makumira, Arusha Technical College, the Institute of Accountancy Arusha, Tengeru Institute; branches of NMB, CRDB, NBC, Exim, KCB, Ecobank, Equity, Azania and more; TANAPA, NCAA, TAWIRI, TRA, NSSF, TANESCO and the East African Community secretariat; SNV, Oikos and other NGOs; Seedco, Rijk Zwaan, Sunflag, Superdoll and Hanspaul; and roughly 120 hotels and lodges.

These are institutions with HR functions, payroll systems and staff-benefit precedent — which makes them structurally easier to convert than a twelve-person safari outfit, even though the CEO's instinct to start with safari companies is sound on affinity grounds.

---

## 7. What you actually sell them

This matters more than the list. A lead here is not a parent; it is an organisation that gives access to a cluster of parents. Sending a school advertisement to `info@` at a tour operator will do almost nothing. The thing that makes the list valuable is having something to offer the employer:

- A **staff education benefit** — a waived or reduced admission fee for their employees' children.
- **Payroll-deduction fee payment**, aligned to the four-instalment structure Silverleaf already uses. This is the single strongest hook: it converts a large annual decision into a manageable monthly one, and it costs the employer nothing but an HR process.
- A **transport route** that serves where their staff actually live, priced from the band table.
- A **lunchtime information session** at their office during an intake window.
- For operators with an existing education CSR programme — and many Arusha operators have one — a **named partnership** rather than a discount scheme.

For savings groups the equivalent is becoming the group's designated school, with instalments timed to the group's cycle.

Design the offer first. The list is only worth what the offer is worth.

---

## 8. Sequence

**Now.** Get the five real campus GPS pins and re-run the collector. Confirm Silverleaf's registration status under the Personal Data Protection Act before any personal data is loaded into a sending platform.

**Next.** Design the employer offer, with Finance, since payroll deduction touches fee collection. The target list already exists: the 11 P1 organisations, then the 20 in P2.

**Then.** Work P1 by phone and in person, leading with the education programme each one already runs — that is what the education_angle column is for. Log every call: partner outreach generates exactly the interaction history that currently disappears into WhatsApp, which is where the CRM question from the Marketing Observations note stops being abstract. Fill the two yellow columns as you go.

**Only after that.** Broadcast tooling. Resend, Sender or Klaviyo are all fine and the choice barely matters at this volume. What matters is that a mass send to a cold scraped list of Tanzanian operators from a new domain will convert poorly and damage the sending domain's reputation. Email opens the door for this segment; the meeting closes it.

---

## 9. Compliance

**Personal Data Protection Act 2022.** Data controllers and processors must register with the Personal Data Protection Commission before collecting or processing personal data, with certificates renewable every five years. The Commission began enforcement in April 2026. Confirm Silverleaf's registration before loading contacts into any platform. Generic organisational addresses (`info@`, `reservations@`) carry less exposure than named-individual addresses.

**Bulk SMS.** Sender IDs must be registered with TCRA and messages routed through a licensed aggregator. Verify current requirements before building an SMS step.

**Not legal advice.** Confirm both with Tanzanian counsel before launch — the enforcement position is recent and the details matter.

---

## 10. Open questions for Silverleaf

1. What are the five campuses' actual GPS coordinates?
2. Is Silverleaf registered with the PDPC as a data controller?
3. Would Finance support payroll-deduction fee collection? Without it, the employer offer is much weaker.
4. Who owns partner outreach — Mariam Haji alone, or with Zuhura Msangi given the expansion overlap?
5. Is there an existing relationship with any Arusha employer to use as a first reference case?
6. Should the government and institutional partnership pipeline share tooling with this one, or stay separate? The Marketing Observations note argued for separate; this list assumes separate.

---

## 11. Research rate limits (added 23 September 2026)

Collection at this scale meets hard limits. The welfare run measured them:
- The agent web-search tool allows 200 searches per session, shared by every subagent.
- The NGO register tolerates about four concurrent requests.
- Broad Overpass queries time out.
- Several registers and forums block automated reading.

Budget and pace any new collection as `skills/silverleaf-create-lead-list/references/research-rate-limits.md` describes, before starting.

## Sources

- [TATO — Tanzania Association of Tour Operators](https://tatotz.org/) — member directory, scraped 6 September 2026
- [OpenStreetMap](https://www.openstreetmap.org/) via the [Overpass API](https://overpass-api.de/) — employer and place data, ODbL licensed
- [Personal Data Protection Commission, Tanzania](https://pdpc.go.tz/en/) · [Personal Data Protection Act 2022 (PDF)](https://www.pdpc.go.tz/media/media/THE_PERSONAL_DATA_PROTECTION_ACT.pdf)
- [KPMG — extension of the registration deadline for data controllers and processors](https://kpmg.com/ke/en/insights/2025/01/extension-of-deadline-of-registration-of-personal-data-controllers-and-data-processors.html)
- [Tanzania Cooperative Development Commission](https://www.ushirika.go.tz/) — SACCOS registration statistics and annual reports
- [Tanzania Tourism Licensing Board / MNRT portal](https://portal.maliasili.go.tz/) — TALA licensing
- Internal: *Business Context Dossier*, *Marketing Observations*, *Scope of Work*, BPR workbook (this repository)
