# Resend segments, 2026-10-10

Contact-import files for Resend, one per segment, in runtime/resend/2026-10-10/ (not committed: they hold contact addresses). Nothing is sent from this repository; a person sends.

| Segment | Contacts |
|---|---|
| companies-high | 207 |
| companies-medium | 323 |
| companies-low | 39 |
| introducers-high | 12 |
| introducers-medium | 3 |
| welfare-high | 64 |
| welfare-medium | 7 |
| welfare-low | 73 |

Left out (no email address; use the call sheets):

- companies: no email route (phone only or none): 263
- introducers: no email route (phone only or none): 1
- welfare: no email route (phone only or none): 283

Addresses shared by two rows, exported once (13):

- info@almc.or.tz: Arusha Lutheran Medical Center (welfare, high) kept as Arusha Lutheran Medical Centre (companies)
- contact@cssc.or.tz: Christian Social Services Commission (welfare, high) kept as Christian Social Services Commission (introducers)
- connie@karamaconnection.org: Karama Kids (Karama Care orphanage), Arusha (welfare, high) kept as Karama Connection (welfare)
- office@africaaminialama.com: KinderVilla Momella (welfare, high) kept as Africa Amini Alama (welfare)
- national.office@sos-tanzania.org: SOS Children's Villages International / SOS Children's Villages Tanzania (welfare, high) kept as SOS Children's Village Arusha (welfare)
- dhrma@atc.ac.tz: Arusha Technical College Staff SACCOS Ltd (companies, low) kept as Arusha Technical College (companies)
- info@adratanzania.org: Adventist Development and Relief Agency (welfare, low) kept as Adventist Development Agency (companies)
- info@tz.ci.org: Compassion International Tanzania (welfare, low) kept as Compassion International Tanzania (welfare)
- info@farajaschool.org: Faraja Forward Tanzania. (welfare, low) kept as Faraja Fund Foundation (welfare)
- info@kilivikings.com: Kili Vikings Limited (welfare, low) kept as Kili Vikings Limited (companies)
- info@maasairescue.org: Maasai Girls Rescue Center Inc (welfare, low) kept as Maasai Girls Rescue Center - Children's Home and Rescue Center (welfare)
- nkoaranga-hospital@habari.co.tz: Nkoaranga Orphanage (welfare, low) kept as Nkoaranga Hospital (companies)
- info@thesmallthings.org: The Small Things (welfare, low) kept as Happy Family Children's Village (welfare)

Confidence rules and promotion: see the docstring of scripts/messaging/export_resend_contacts.py. Each contact's confidence_reason property says what would promote it.

Custom contact properties to create in Resend before importing (all strings): organisation, track, audience, confidence, confidence_reason, priority, variant, recipient, message_subject, message_body, message_html, plan_id.
