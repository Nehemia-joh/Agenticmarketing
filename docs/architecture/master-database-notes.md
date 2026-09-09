# Silverleaf master database

Originally consolidated on 6 September 2026 and fully reconciled on 9 September 2026. The current master preserves every earlier entity and now includes later outreach guidance, automation design and structured operational reference workbooks from `C:/Work/silverleaf-agentic-marketing`.

Open **Silverleaf Master Database - Consolidated.xlsx** for the current filterable working view. **Silverleaf Master Database.sqlite** is the complete linked database, including exact source-file archives and extracted records. The workbook is a snapshot; edits do not automatically synchronize with SQLite. Earlier workbooks and pre-consolidation databases are retained as recoverable versions.

## Working order

The outreach revision dated 6 September 2026 replaces all 927 initial drafts and adds 1,854 follow-ups. The 7 September verified-only revision retains an active hook for six message variants across two organisations. The other 921 hook fields are blank, and their alternate first messages open directly with the offer. Start in **Outreach plans**, filter `selection` to `Candidate for review`, then inspect hook type, hook status, evidence URL, verification date, channel attribution and missing information. There are 551 organisation records with proposed candidates; branch overlaps remain unresolved. Of the 927 draft variants, 712 need draft review and 215 need further research. Every message remains unsent.

Use **Segments** to choose the offer, **Messages** to compare `first_message_v1`, `hook_v2` and `first_message_v2`, **Sequences** for follow-ups and **Flows** for triggers and response branches. An active hook requires an exact supporting source URL and a verification date. Role, locality and generic value ideas remain research candidates until verified. A named draft using a company channel requires forwarding; it does not establish a personal address. The 32 enquiry records remain separate and unchanged.

`docs/strategy/outreach-flows.md` contains the worked flows. `outputs/config/automation-recipes.json` contains disabled implementation recipes. Use the validated create or update skill and the deterministic scripts under `scripts/master/`; no sending integration or recurring job is active.

`hook-guidance.md` defines the verified-only hook rule and account-level testing approach used for the second first-message version.

## Completeness audit

The 9 September reconciliation checked 42 structured artifacts. Historical SQLite databases were compared by primary key, the current outreach JSON was matched to 927 plans, 6 segments and 18 flow steps, and every archived source was checked against its physical SHA-256 hash and embedded bytes. No historical primary-key record or parsed source record was missing.

The master now contains 58 archived source files and 7,591 parsed source records. This includes all nonempty rows from the Silverleaf marketing calendar and BPR workbooks, the current outreach skill guidance, and the 18 design-only automation steps. Operational reference rows remain raw knowledge records unless explicitly mapped to a lead.

Use **Consolidation audit** to see how each structured artifact was imported, mirrored or reconciled. Use **Knowledge sources** for the newly included references and guidance, and **Automation recipes** for the disabled sequence design. `consolidation-audit.json` contains the machine-readable reconciliation result.

1. Filter Organisations by the imported priority. Confirm the organisation or branch before outreach.
2. Use Organisation ID to find its Contacts. Named work emails, published role emails and shared company channels are separate fields.
3. Filter Messages by the organisation or contact ID. All messages remain drafts. Multiple messages for one target are retained when their wording differs.
4. Follow the linked Strategy ID. Strategies contains both consolidated proposed workflows and historical source guidance. Confirm operational terms before making an offer.
5. Review Enquiries separately. The 32 records include historical school searches, childcare requests, staffing and collaboration enquiries. They are not 32 qualified prospective parents.
6. Resolve Review items using Facts and Source rows. Record actual owner, next action and outreach status in the working workbook.

## Coverage

The database contains 955 organisation/place records, 342 published business-contact records, 32 enquiries, 927 draft message IDs, 128 strategy/guidance entries and 5 campus references. It includes 127,412 source assertions, 7,591 source records, 58 archived source files, 11 knowledge documents and 18 automation steps. Repeated source assertions are grouped into 45,224 distinct entity/field/value combinations in the workbook's Facts table.

Organisation/place counts include unqualified raw directory records and unresolved branches. Contacts with a compound name remain as the source recorded them. No inference of parenthood or current employment was added.

## Selection and deduplication

Displayed organisation fields prefer the enriched v2 observations, then the latest pitch workbook, then other workbooks and raw extracts. This is a consolidation order, not a freshness guarantee. Every alternate assertion retains its source record ID in `facts`.

Exact normalized organisation names ignore punctuation and Ltd/Limited; exact TATO portfolio URLs can also establish the same organisation. Other place/branch records use their recorded campus/distance or OSM ID. Names that are merely similar are not silently merged. Review includes exact-name branch overlaps and different contact/campus values. An alternate contact value is not necessarily an error.

Messages deduplicate by target and exact body. Business contacts deduplicate by organisation and normalized public name. Enquiries preserve the 32 source record identities. No messages were sent, and no source contact information, legal statement, fee, campus distance or public enquiry was reverified online during consolidation.

## SQLite tables

| Table | Purpose |
|---|---|
| organisations | Canonical display fields and proposed strategy |
| contacts | Published business contacts linked to organisations |
| enquiries | Public requests, dates, attribution and fit |
| messages | Draft text, target ID, strategy and source |
| message_versions | All 927 original message records before the rewrite |
| outreach_plans | Revised copy, follow-ups, segment, role, evidence, forwarding instructions and review selection |
| outreach_segments | Audience and offer rules |
| outreach_flows | Triggers, conditions, delays, example responses and proposed database updates |
| strategies | Imported guidance and proposed execution workflows |
| campuses | Approximate source campus reference |
| facts | Every field assertion with an originating record |
| review | Multiple source values and unresolved branch overlaps |
| source_records | Exact extracted row or document payload as JSON |
| entity_sources | Links between an entity and its source records |
| source_files | Original file bytes, SHA-256, size and relative path |
| source_file_versions | Earlier archived bytes for a physical source that was resaved |
| knowledge_documents | Structured references and guidance added after the first consolidation |
| knowledge_document_records | Links knowledge documents to their preserved source rows or sections |
| automation_configuration | Disabled automation design settings and stop events |
| automation_recipes | The 18 design-only trigger, condition and response steps |
| consolidation_artifacts | Inventory and reconciliation status for structured project artifacts |
| consolidation_runs | Counts and result of each full completeness check |
| intelligence_search | Full-text search across leads, messages and strategies |

`organisation_outreach` and `contact_outreach` views join targets to their messages. Original file bytes use zlib compression in `source_files.content`; decompress and compare SHA-256 to recover the original file exactly. Generated scripts and previews are archived as provenance rather than promoted into leads.

Example searches:

```sql
SELECT * FROM organisation_outreach WHERE priority LIKE 'P1%';
SELECT * FROM contacts WHERE organisation_id = 'ORGANISATION_ID';
SELECT * FROM facts WHERE entity_id = 'ENTITY_ID' AND field = 'campus';
SELECT entity_type, entity_id, title FROM intelligence_search
WHERE intelligence_search MATCH '"payroll"';
```

Original lead and enquiry records remain unchanged. Database integrity, foreign-key relationships, message targets, source hashes, embedded archives, historical primary keys and workbook row counts were checked. The final workbook has no detected formula errors and includes the audit trail used to support the zero-missing-record result.

## Marketing documents, positioning and campaign cadence — 9 September 2026

- Reviewed all 12 files in `references/Marketing Documents`; the calendar was already archived and the other 11 originals are now stored in `source_files` with page, paragraph, relationship or slide records.
- Added 24 source-traceable positioning and governance entries, 9 campaign blueprints and 36 campaign touchpoints.
- Rewrote all 927 organisation/contact drafts as `2026-09-09-marketing-evidence-v3` while preserving the earlier messages in `message_versions`.
- Preserved the six verified recipient hooks and left every unverified hook inactive.
- Added a review record for each of the 32 historical public enquiries: 9 have a one-reply parent-admissions draft and 23 are retained without outreach copy because they are outside parent-admissions scope.
- Expanded the design-only automation recipe to 47 steps. Sending and recurring schedules remain disabled.
- Planned calendar dates, 2027 fees, discounts, capacity, referral terms and event details remain approval-gated.

## New-contact acquisition framework — 9 September 2026

- Organisation and business-contact leads now use `2026-09-09-new-contact-acquisition-v4`. They do not inherit the internal marketing calendar, event cadence or parent broadcast plan.
- Marketing documents remain the source for approved Silverleaf positioning, tone, claim gates and value propositions where applicable.
- Every current outreach plan is assigned to AQ00 hold, AQ01 routing-first or AQ02 direct-recipient test. The same refresh applies after the lead list expands.
- The database contains 3 acquisition tracks, 7 value-proposition modules and 9 intake rules. F12 handles appendable intake and classification; F13 handles uncertain-owner routing.
- AQ01 uses one routing request and one check-in after 5 working days. AQ02 keeps Day 0, +4 working days and +4 working days as an independent test. AQ00 sends nothing.
- No acquisition, broadcast or automation is enabled.

