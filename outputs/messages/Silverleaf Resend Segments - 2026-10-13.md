# Resend segments, 2026-10-13

Contact-import files for Resend, one per segment, in runtime/resend/2026-10-13/ (not committed: they hold contact addresses). Nothing is sent from this repository; a person sends.

| Segment | Contacts |
|---|---|
| companies-high | 264 |
| companies-high-direct | 36 |
| companies-high-indirect | 228 |
| companies-medium | 349 |
| companies-low | 52 |
| introducers-high | 12 |
| introducers-high-direct | 4 |
| introducers-high-indirect | 8 |
| introducers-medium | 3 |
| welfare-high | 70 |
| welfare-high-direct | 14 |
| welfare-high-indirect | 56 |
| welfare-medium | 11 |
| welfare-low | 115 |

Inferred candidates (inferred from format, unverified; always low; a person confirms each before use; counts only, never in the segments above or the dedupe):

| File | Contacts |
|---|---|
| companies-low-inferred | 1 |
| introducers-low-inferred | 1 |
| welfare-low-inferred | 4 |

Left out (no email address; use the call sheets):

- companies: no email route (phone only or none): 569
- welfare: no email route (phone only or none): 233

Addresses shared by two rows, exported once (18):

- info@almc.or.tz: Arusha Lutheran Medical Center (welfare, high) kept as Arusha Lutheran Medical Centre (companies)
- pmaduki@cssc.or.tz: Christian Social Services Commission (welfare, high) kept as Christian Social Services Commission (introducers)
- info@tz.ci.org: Compassion International Tanzania (welfare, high) kept as Compassion International Tanzania (welfare)
- connie@karamaconnection.org: Karama Kids (Karama Care orphanage), Arusha (welfare, high) kept as Karama Connection (welfare)
- national.office@sos-tanzania.org: SOS Children's Villages International / SOS Children's Villages Tanzania (welfare, high) kept as SOS Children's Village Arusha (welfare)
- info@ate.or.tz: ATE Northern Zone Office (introducers, medium) kept as Association of Tanzania Employers (introducers)
- dhrma@atc.ac.tz: Arusha Technical College Staff SACCOS Ltd (companies, low) kept as Arusha Technical College (companies)
- info@adratanzania.org: Adventist Development and Relief Agency (welfare, low) kept as Adventist Development Agency (companies)
- info@farajaschool.org: Faraja Forward Tanzania. (welfare, low) kept as Faraja Fund Foundation (welfare)
- info@kilivikings.com: Kili Vikings Limited (welfare, low) kept as Kili Vikings Limited (companies)
- hopehometrust@yahoo.co.uk: Kitaa Hope Home (welfare, low) kept as Hope Home Trust (welfare)
- lovinghand2000@yahoo.com: LOHADA (welfare, low) kept as Kesho (welfare)
- littlesoulsoftanzania@gmail.com: Little Souls of Tanzania (welfare, low) kept as Enyorata Children's Home (welfare)
- info@maasairescue.org: Maasai Girls Rescue Center Inc (welfare, low) kept as Maasai Girls Rescue Center - Children's Home and Rescue Center (welfare)
- nkoaranga-hospital@habari.co.tz: Nkoaranga Orphanage (welfare, low) kept as Nkoaranga Hospital (companies)
- info@thesmallthings.org: The Small Things (welfare, low) kept as Happy Family Children's Village (welfare)
- loveourtanzaniafamily@gmail.com: Tumaini For Africa Orphanage (welfare, low) kept as Love Our Tanzania Family Inc (welfare)
- sluokat@gmail.com: UPENDO: One Kid at a Time (welfare, low) kept as OKAT Children's Home (welfare)

## VICOBA savings groups

Every VICOBA group is in exactly one band (first_touch.vicoba_case, the rule the drafter and the call sheet use). A group has no email of its own: its row is a delivery row (`vicoba-delivery-<band>.csv`: band, case, channel, introducer, ward, council, distance band, release order with women's groups first), never a Resend contact. Resend rows exist only for introducers that publish an email (`vicoba-introducers-<band>.csv`).

| Band | Groups | Of which women's groups | Band once the Kiswahili template is approved |
|---|---:|---:|---:|
| high-direct | 0 | 0 | 0 |
| high-indirect | 0 | 0 | 0 |
| medium | 0 | 0 | 0 |
| low | 5 | 2 | 5 |
| total | 5 | 2 | 5 |

Why groups are held (a group can have several reasons):

- Kiswahili template not yet approved by a native speaker: 5
- introducer named by the intake, link to confirm: 4
- record stale: not confirmed in 12 months: 3
- record incomplete: no ward: 1
- record incomplete: no introducer route: 1
- no accepted introducer link: 1

| Introducer segment | Contacts |
|---|---:|
| vicoba-introducers-medium | 0 |
| vicoba-introducers-low | 1 |

Introducers without an email (call or letter): 7. Introducer rows kept under another row (one conversation per organisation, or a shared inbox): 0.

Confidence rules and promotion: see the docstring of scripts/messaging/export_resend_contacts.py. Each contact's confidence_reason property says what would promote it.

Custom contact properties to create in Resend before importing (all strings): organisation, track, audience, confidence, high_route, confidence_reason, priority, variant, recipient, escalation_recipient, escalation_email, message_subject, message_body, message_html, plan_id.
