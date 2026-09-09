# Review workbook layout

Generate the workbook from the canonical SQLite database. Use filters, frozen headers, readable widths, wrapped message fields, and a visible generated timestamp. Do not use formulas to recreate canonical facts.

## Required sheets

| Sheet | Purpose |
|---|---|
| `Read Me` | Scope, source of truth, generated time, row counts, status definitions, and safety constraints. |
| `Organisations` | One row per organisation with route, campus, fit, priority, verification, and source. |
| `Contacts` | Named people and role desks with public contact routes and attribution. |
| `Parent Enquiries` | Public enquiries, request, date, current relevance, source, and deliberately published contact details. |
| `Outreach Plans` | Target, relevance, offer, CTA, hook evidence, first message, follow-ups, track, and review state. |
| `Campaigns` | Campaign objective, audience, positioning, status, and owner fields. |
| `Touchpoints` | Ordered steps, channel, delay, condition, message purpose, and stop rule. |
| `Assignments` | Entity-to-campaign assignment and current state. |
| `Strategies` | Reusable strategy and positioning records with evidence links. |
| `Evidence` | Source and field-level claims used for qualification or copy. |
| `Sources` | Source inventory with hashes, dates, and locations. |
| `Review Queue` | Conflicts, ambiguous matches, missing facts, and requested decisions. |
| `Automation` | Disabled recipe and step definitions; never credentials or live-send controls. |

## Presentation rules

- Put identifiers and statuses first, then targeting fields, evidence, and copy.
- Keep raw source text out of operational sheets when a concise evidence field is sufficient; link to `Evidence` and `Sources`.
- Use explicit values such as `needs_review`; do not use cell colour as the only status signal.
- Hide no rows required for reconciliation.
- Add data validation for controlled states when the workbook library supports it.
- Make URLs clickable and keep dates in ISO format.
- Exclude compressed source blobs from the workbook.

## Verification

Compare every sheet row count with a deterministic database query. Inspect at least the first, middle, and last populated rows of the lead, enquiry, outreach, evidence, and review sheets. Confirm that wrapped text and column widths do not hide key decisions.
