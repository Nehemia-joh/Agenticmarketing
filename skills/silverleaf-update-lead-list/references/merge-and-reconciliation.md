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

### VICOBA savings groups

`scripts/master/add_vicoba_groups.py` matches a VICOBA row in this order:
1. `vicoba_group_key`, exact and case-insensitive (`VIC|<council>|<ward>|<normalised name>`).
2. `registration_number`, exact within one `registration_authority`.
3. The preflight's exact name plus locality, only when the hit is a VICOBA record.

A match adds the row's source record, `entity_sources` link and new facts to the existing group, and a differing name becomes a `name_variant` fact. A differing value becomes a `Multiple source values` review item and never overwrites. The group keeps its first key.

These go to review and are never merged:
- **A SACCOS.** An exact preflight hit on a record that is not a VICOBA is never merged. When a SACCOS has the same normalised name in the same council, the row raises `VICOBA may be a registered SACCOS` (groups graduate into SACCOS).
- **A similar name.** The same normalised name in the same council with a different or missing ward, or a near-identical name in the same council, raises `VICOBA possible duplicate`. Common names never raise one: Upendo, Tumaini, Umoja and the rest of `data/reference/vicoba-common-names.json`. They match only on the full key.

These are not group records:
- An aggregate ("25 groups formed in Longido", marked by `vicoba_groups_reported`) becomes a fact on its sponsor organisation, never organisations.
- A row that breaks the contract is quarantined with its reason: a contact or enquiry row, a label outside the contract, no area named, a point outside Tanzania.

A group that is incomplete (no ward, no introducer route, name only) or stale (not confirmed in 12 months) is kept and labelled. It gets a review item naming what is missing.

## Field precedence

Prefer a newer official source over an older official source, then an attributable published source over an unattributed note. Preserve the losing claim in `facts` or `review`. Empty new values never erase populated canonical values. A new value with weaker evidence never replaces a verified value automatically.

## Conservation equations

For each entity type:

`after_count = before_count + inserted_count`

`validated_input = inserted_count + exact_match_count + quarantined_count`

Every accepted source row must have one source record. Every inserted or updated entity must have an `entity_sources` link to the contributing source record. Every reported conflict must have a review item.

The set of pre-update stable IDs must be a subset of the post-update ID set unless the user explicitly authorised a deletion and it is documented separately.

For a VICOBA intake, aggregates are counted apart, and rows already applied by an earlier run count as exact matches:

`validated_input = inserted_count + exact_match_count + already_applied_count + aggregate_count + quarantined_count`

A re-run of the same intake inserts nothing and writes no source record, fact or review item.

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
- For VICOBA groups, the adder checks each of these before commit, and `verify_master.py` checks them again afterwards:
  - every group has a `vicoba_group_key`, a valid `record_status`, a `women_group` fact and a source link;
  - no key is on two organisations;
  - no VICOBA organisation has a phone (or, from the adder, an email);
  - no contact is written;
  - no SACCOS carries a VICOBA key or link;
  - every group plan is `VICOBA members`, and the `language` and `english_meaning` columns exist;
  - any contact phone on a group has `phone_basis = published_for_role`.

Rollback on failure. After commit, regenerate the workbook and compare its sheet counts with the database.
