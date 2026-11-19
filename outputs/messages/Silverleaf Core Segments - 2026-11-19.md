# Silverleaf core segments and subsegments

*As of 2026-11-19, counted from the three databases: the company master, the welfare run `arusha-welfare-2026-09` and the government run `arusha-government-2026-09`. Nothing is sent from the repository; a person sends.*

This version adds the members of the national associations and regulator registers in the team's association workbook (checked 12 October 2026): 35 tour operators and hotels (TATO), 222 microfinance lenders (Bank of Tanzania Tier 2 licence list) and 9 SACCOS (TCDC licence list) in the catchment councils, and six associations as introducers. Members outside the catchment are kept in the master's national leads table, not written to.

We write to four kinds of audience. Each has its own reason to talk to us, its own request and its own decision-maker. On top of the four sits one shared layer: how confident we are that a message reaches the person who can say yes.

| Core segment | What they are to us | What we ask | Organisations |
|---|---|---|---|
| 1. Employers | Customers through their staff | A partnership on an education benefit for staff's children (or sponsorship, for the few that already fund education) | 1,374 companies + 130 savings groups (125 SACCOS, 5 VICOBA) |
| 2. Introducers | Multipliers | Share the staff benefit with their member employers | 22 (+ 8 savings-group introducers) |
| 3. Welfare organisations | Partners and funders | A partnership on the education of the children in their care, or sponsorship of students | 445 in scope |
| 4. Government offices | A trusted forum for parents | A free 15–20 minute talk to parents at a community meeting | 228 |

---

## 1. Employers

Companies whose staff are the parents we want to reach. Half are in tourism: 52% are safari operators, travel agencies, hotels or lodges. The first message asks for a short meeting and states no offer terms. The documented offer follows in the second message.

**Subsegments by kind of employer**

| Kind | Businesses | Ready for review |
|---|---|---|
| Safari operators and travel agencies | 494 | 446 |
| Microfinance lenders | 221 | 221 |
| Hotels, lodges and camps | 215 | 144 |
| Hospitals and clinics | 188 | 37 |
| Banks and other companies | 152 | 101 |
| NGOs and research bodies | 62 | 28 |
| Colleges and universities | 23 | 19 |
| Public bodies (HR route only, after a compliance check) | 19 | 12 |
| **Savings groups (SACCOS)**: members rather than staff, approached through the committee in Kiswahili, after a Kiswahili review and Finance's approval of the member rate | 125 | almost none publish a route |
| **Savings groups (VICOBA)**: reached through their introducer, Kiswahili, women's groups first | 5 | held for the Kiswahili review |

**Microfinance lenders (new kind, 19 November 2026).** Tier 2 microfinance service providers licensed by the Bank of Tanzania, in the catchment councils. They are asked for the staff benefit like other companies. Some lend for school fees, so they are also candidate introducers to their borrowers; they are not asked to introduce anyone yet. Most publish only the owner's phone or a personal free-mail inbox: a free-mail inbox not named after the company is recorded as personal data and is never a route until a person confirms it, so most of these drafts go by phone (the call sheet). None has a point yet; their drafts use the five-campus line until the Google Maps round places them.

**Subsegments by message variant**

- **A – Sponsorship (14):** companies with sourced education or community giving. We ask them to sponsor students, at any size.
- **B – Staff-benefit partnership (1,360):** every other company. We ask for a partnership on an education benefit for staff's children.

**Subsegments by reach tier.** The tier scores the kind of employer, published staff numbers, verified workforce facts, named people on file and distance to a campus.

| Tier | Companies | Use |
|---|---|---|
| P1 | 100 | First wave |
| P2 | 150 | Second wave |
| P3 | 1,110 | The rest (all 257 new companies are here until they have a point and research) |
| X | 15 | Held (outside the catchment, not an employer, or another blocker) |

**Who receives it:** the most senior person running the Tanzania or Arusha operation: the owner, founder, MD, GM or HR head. A group or global executive is kept as the escalation contact. A bank branch keeps the branch as its recipient, and its head office (the Bank of Tanzania register's inbox or phone, from the TBA member list) is the escalation contact when no named group head is on file (9 branches).

---

## 2. Introducers

Introducers aren't customers. They are associations, chambers of commerce and HR bodies whose members are the employers we want to reach. Their draft asks them to share Silverleaf's staff education benefit with their members, through a newsletter, a members' meeting slot or an introduction. A single yes can reach dozens of companies at once.

| Kind | Organisations |
|---|---|
| Chambers of commerce | TNCC national, TNCC Arusha regional, TNCC Kilimanjaro regional |
| Employers' associations | ATE (national and Northern Zone, Arusha), CTI (national and Arusha/Moshi office), TPSF |
| Sector associations | TATO (tour operators), HAT (hotels), TBA (bankers), TAHA (horticulture), APHFTA (private health facilities), CSSC (Christian social services); added 19 November 2026 and held until a route is found: Tanzania Chamber of Mines, Agricultural Council of Tanzania, TAFFA (freight forwarders), Association of Tanzania Insurers, TASTA (seed trade), Tanzania Startup Association |
| HR body | Women HR Association of Tanzania (WHAT) |
| Other | East African Business Council (EABC) |

The six new associations publish only a website in the source, so their drafts are held for a route. Two more on the list, the Tanzania Association of Oil Marketing Companies and the Tanzania Women Chamber of Commerce, have no website or route and are kept in the national leads table only.

**Who receives it:** the executive secretary, CEO or secretariat. An elected chair is used when the body names no executive.

---

## 3. Welfare organisations

Unchanged by this merge. Children's homes, programmes, specialised centres and their funders, within the catchment around the five campuses. Two requests:

- **Partnership:** to homes, programmes and centres, on the education of the children in their care, with a short meeting. No offer terms; the partner rate follows in the second message.
- **Sponsorship:** to funders, only with a sourced, verified link to a home or programme near the campuses. Without that link the draft is held.

Subsegments by kind and priority are as in the 2026-10-11 version.

**Who receives it:** the leader on the ground, such as the head of the home, the country manager or the Arusha programme director. A senior executive abroad is the escalation contact. A chair is used only when no executive is named.

---

## 4. Government offices

Unchanged by this merge. Local offices that can convene the community meetings where parents already gather. We ask them for nothing for themselves. We ask for a free talk in Kiswahili on getting children ready for school, with a take-home booklet. Letters are formal Kiswahili on letterhead, addressed to the office by title, and delivered by hand. The council introduction is the first letter; wards and villages follow it, nearest first.

**Who decides:** the council director (DED) for councils, the District or Regional Commissioner, and the ward or village executive officer.

---

## The confidence layer (all four segments)

Each first message sits in one confidence segment. The Resend import files and the delivery lists follow it.

| Segment | Rule |
|---|---|
| **High** | Ready for review, nothing held, addressed to a named decision-maker the organisation publishes, at an address on its own domain or the person's own published address |
| ↳ **High – direct** | The person's own address, or a role inbox matching their role (hr@, md@, dg@) |
| ↳ **High – indirect** | A general inbox (info@, reservations@) addressed to the named person; each row says what would make it direct |
| **Medium** | Ready, but it goes to the organisation's inbox and needs routing, or to a free-mail inbox named after the organisation |
| **Low** | Held or needs research: red flags, possible closure, an unconfirmed role or inbox, a funder without a verified link, a savings group's or public body's checks |
| **No email** | A phone only, or no route: these go on the call sheets |

| Track | High (direct + indirect) | Medium | Low | No email |
|---|---|---|---|---|
| Employers | 264 (36 + 228) | 430 | 52 | 752 |
| Introducers | 12 (4 + 8) | 3 | 0 | 6 |
| Welfare | 70 (14 + 56) | 11 | 115 | 233 |
| Government | 4 (the pilot councils) | 0 | 224 (held until the council introduction) | delivered by hand; 11 offices have an official inbox |

The merge added 81 employer rows to medium (77 new: 42 microfinance lenders whose inbox is on their own domain or named after the company, 21 hotels and 14 tour operators; 4 existing records, after the TATO list filled 4 empty inboxes) and 183 to no email (mostly microfinance lenders with a phone only). An address two rows share is exported once.

**The recipient rule, everywhere:**
- The first message goes to the in-country person who can decide.
- A more senior executive, or a bank's head office, is recorded as the escalation contact. They are never copied on the first message and get no draft of their own.
- They are used if the local office stays silent after the follow-up, declines, or defers to head office.
- Vice chairs, treasurers and secretaries are never chosen.

Rules and counts come from `scripts/messaging/export_resend_contacts.py`, `scripts/messaging/build_company_audience_profile.py`, `scripts/master/rank_employer_reach.py` and the run databases.
