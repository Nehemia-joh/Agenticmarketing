# Merge and reconciliation procedure

## Pre-update snapshot

Record the database SHA-256, SQLite `user_version`, schema objects, integrity result, foreign-key result, and counts for every canonical table. Export the full set of organisation, contact, enquiry, message, and outreach-plan IDs for comparison. A temporary byte-for-byte copy may be used outside the repository during the transaction.

## Match order

Apply exact matching in this order:

1. Existing immutable ID supplied by the canonical database.
2. Published domain for an organisation.
3. Normalised organisation name plus locality.
4. Organisation plus named email for a contact.
5. Organisation plus normalised contact name and role.
6. Organisation plus a published role-based route.
7. Platform plus canonical URL, enquiry date, and author for an enquiry.

Flag similar names, changed employers, conflicting roles, shared phone numbers, and reused social URLs for review. Do not auto-merge them.

## Field precedence

Prefer a newer official source over an older official source, then an attributable published source over an unattributed note. Preserve the losing claim in `facts` or `review`. Empty new values never erase populated canonical values. A new value with weaker evidence never replaces a verified value automatically.

## Conservation equations

For each entity type:

`after_count = before_count + inserted_count`

`validated_input = inserted_count + exact_match_count + quarantined_count`

Every accepted source row must have one source record. Every inserted or updated entity must have an `entity_sources` link to the contributing source record. Every reported conflict must have a review item.

The set of pre-update stable IDs must be a subset of the post-update ID set unless the user explicitly authorised a deletion and it is documented separately.

## Transaction checks

Run these checks before commit:

- `PRAGMA integrity_check` returns `ok`.
- `PRAGMA foreign_key_check` returns no rows.
- All target IDs in messages and outreach plans resolve.
- Contact organisation IDs resolve.
- Enquiry source record IDs resolve when present.
- Hooks with text have a source URL and verification date.
- Send-ready rows have an attributed public route.
- Automation definitions remain disabled.

Rollback on failure. After commit, regenerate the workbook and compare its sheet counts with the database.
