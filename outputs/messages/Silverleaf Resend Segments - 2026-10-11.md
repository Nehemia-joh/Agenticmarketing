# Resend segments, 2026-10-11

Contact-import files for Resend, one per segment, in runtime/resend/2026-10-11/ (not committed: they hold contact addresses). Nothing is sent from this repository; a person sends.

| Segment | Contacts |
|---|---|
| companies-high | 232 |
| companies-high-direct | 29 |
| companies-high-indirect | 203 |
| companies-medium | 323 |
| companies-low | 48 |
| introducers-high | 12 |
| introducers-high-direct | 2 |
| introducers-high-indirect | 10 |
| introducers-medium | 3 |
| welfare-high | 67 |
| welfare-high-direct | 12 |
| welfare-high-indirect | 55 |
| welfare-medium | 9 |
| welfare-low | 118 |

Left out (no email address; use the call sheets):

- companies: no email route (phone only or none): 229
- welfare: no email route (phone only or none): 233

Addresses shared by two rows, exported once (19):

- info@almc.or.tz: Arusha Lutheran Medical Center (welfare, high) kept as Arusha Lutheran Medical Centre (companies)
- contact@cssc.or.tz: Christian Social Services Commission (welfare, high) kept as Christian Social Services Commission (introducers)
- info@tz.ci.org: Compassion International Tanzania (welfare, high) kept as Compassion International Tanzania (welfare)
- connie@karamaconnection.org: Karama Kids (Karama Care orphanage), Arusha (welfare, high) kept as Karama Connection (welfare)
- office@africaaminialama.com: KinderVilla Momella (welfare, high) kept as Africa Amini Alama (welfare)
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

Confidence rules and promotion: see the docstring of scripts/messaging/export_resend_contacts.py. Each contact's confidence_reason property says what would promote it.

Custom contact properties to create in Resend before importing (all strings): organisation, track, audience, confidence, high_route, confidence_reason, priority, variant, recipient, escalation_recipient, escalation_email, message_subject, message_body, message_html, plan_id.
