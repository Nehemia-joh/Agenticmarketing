---
name: silverleaf-create-lead-list
description: Create a new evidence-backed Silverleaf-style lead list, canonical SQLite database, and review workbook from raw research. Use when starting a new list or a separate campaign dataset; use silverleaf-update-lead-list to add records to an existing master.
---

# Create a Silverleaf Lead List

Create a reviewable lead database whose claims can be traced to source material. Treat SQLite as the source of truth and the workbook as a generated review surface.

## Define the list

Record the campaign objective, campuses or localities, radius, lead types, channels, recency window, and stopping rule before collecting records. Separate these record types:

- `organisation`: a business, institution, community group, employer, property, or referral partner.
- `contact`: a named person or a public role-based contact associated with an organisation.
- `enquiry`: a public, attributable expression of need from a parent or prospective customer.

Collect only public business contact details or details deliberately published with the enquiry. Do not infer private email addresses, phone numbers, parenthood, identity, or household circumstances. Record an anonymous enquiry when the author is unavailable instead of guessing.

## Use the data contract

Read [references/lead-list-data-contract.md](references/lead-list-data-contract.md) before creating rows. Use [assets/lead-intake-template.csv](assets/lead-intake-template.csv) as the intake shape. Read [references/workbook-layout.md](references/workbook-layout.md) before generating a workbook.

## Build the evidence set

1. Inventory every input file and public source.
2. Preserve the original source URL, source location, acquisition date, verification date, and a short evidence excerpt.
3. Write one row per organisation, contact, or enquiry. Do not combine unrelated claims in one row.
4. Run `python scripts/validate_intake.py <intake.csv> --report <report.json>` and resolve all errors.
5. Create the database with `python scripts/initialize_lead_db.py <intake.csv> <database.sqlite>`.

The initializer refuses to overwrite an existing database unless `--replace` is supplied. Use `--replace` only when the user explicitly wants the new file rebuilt.

## Resolve identity and provenance

Reuse a normalised exact key before creating a new entity:

- Organisation: registered or published domain when present; otherwise normalised name plus locality.
- Contact: organisation plus named email; otherwise organisation plus normalised name and role; otherwise organisation plus published contact route.
- Enquiry: platform plus canonical source URL plus normalised enquiry date and author.

Keep stable IDs after creation. Preserve every contributing source as a source record and link it through `entity_sources`. Put individual field claims in `facts` when multiple sources, conflicts, or later verification matter. Record unresolved conflicts in `review`; do not silently select a value.

## Add strategy and copy

Assign one acquisition state to each outreach plan:

- `AQ00_RESEARCH_ONLY`: the route, identity, evidence, or fit is not ready.
- `AQ01_PERMISSION_LED`: the recipient and route are usable; begin with a small, useful, permission-based offer.
- `AQ02_TRIGGER_LED`: a verified, current trigger supports a specific first message.

Write relevance, offer, and CTA separately. Personalise from verified evidence. A hook is optional; omit it when it cannot be supported by a source URL and verification date. Keep the first message useful to the recipient and make the first ask easy to answer. Draft messages only. Do not send, schedule, or activate automations.

## Generate and verify the deliverables

Generate the review workbook from SQLite, never by maintaining a second independent dataset. Include every required sheet in [references/workbook-layout.md](references/workbook-layout.md).

Before completion:

1. Run `PRAGMA integrity_check` and `PRAGMA foreign_key_check`.
2. Confirm source, entity, and outreach counts reconcile with the intake report.
3. Confirm every factual hook has evidence and a verification date.
4. Confirm review-required rows are excluded from send-ready views.
5. Confirm every automation remains disabled.
6. Open or render the workbook and inspect the main lead, enquiry, outreach, evidence, and review sheets.
