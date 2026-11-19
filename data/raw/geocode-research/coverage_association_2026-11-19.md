# Geolocation coverage: association-members merge, 19 November 2026

Targets: the 266 organisations the association-members merge added to the master (`runtime/geocode/inventory_association_2026-11-19.json`). No web search; deterministic collectors only (`scripts/maps/collect_geocodes.py`).

| Collector | Attempts | Outcome |
|---|---|---|
| repo (reviewed points and OpenStreetMap extracts already in the repository, no network) | 266 | 0 candidates |
| osm (Overpass, named features in the map box; queries amenity, brand, office, tourism, building) | 266 names | 24 with a partial-name candidate, 0 exact; 0 accepted |
| osm, query `shop` | 1 query | Blocked: every mirror refused or timed out (504). Skipped, not retried |
| nominatim (street addresses) | 120 addresses | 0 results in Tanzania |
| review (`collect_geocodes.py review`) | 266 | 0 accepted, 0 corrections |

All 266 stay without a point: their drafts use the five-campus line (no distance claim) until the coordinator's Google Maps round, from `runtime/geocode/gmaps_worklist_association_2026-11-19.jsonl`. Every attempt is in the research ledger (`geocodes_association_2026-11-19.jsonl` ingested; the blocked `shop` query appended).
