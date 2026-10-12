# Lead-location research, 2026-10-13: point-level geolocation, coverage log

Since 13 October 2026 a draft states the nearest campus and its distance only from the organisation's own point (precision `point` in the master, `address` in the run databases). Every other lead names the five campuses. This wave placed as many leads as the repository and the deterministic collectors allow, with no web search and no Google Maps.

Evidence files:
- `geocodes_pointfix_2026-10-13.jsonl`: points for leads with no stored coordinates, and the welfare and government run points (`apply_geocodes.py`).
- `geocodes_corrections_pointfix_2026-10-13.jsonl`: points that replace a stored estimate (`apply_geocodes.py --replace`).

Each line carries the source URL, the date read, the as-found excerpt, the basis, `geocode_source` and `confidence`. Collected and reviewed with `scripts/maps/collect_geocodes.py` (`inventory`, `repo`, `sites`, `osm`, `nominatim`, `review`).

## Rule

A point is accepted only on a clear name match (equal name keys after legal suffixes are dropped, or the organisation's own website) plus a matching locality. The locality must agree in one of these ways:
- the record's locality or street address names a place within 5 km (12 km for a town or city centre);
- the feature's address tags name the same place;
- the point reproduces the record's stored import distance;
- the record's own estimate lies nearby.

A second feature of the same name elsewhere, a point far from the record's estimate, a town the record contradicts, or a place in the name far from the point sends the candidate to review. A ward office is accepted only when it is the office of that ward (name or `addr:ward`), inside the council's OpenStreetMap district and within 10 km of the run's ward point. A P.O. box is never a location.

## Sources, cheapest first

| Source | Leads accepted (all three lists) | Confidence |
|---|---|---|
| Records imported from an OpenStreetMap feature, holding its coordinates and id with no precision recorded | 47 | high |
| Reviewed points already in the repository (the coordinator's accepted Google Maps listings, earlier geocode lines) | 14 | high |
| Map pins on the organisation's own website (crawl cache, no new fetch) | 27 | 7 high, 20 medium |
| OpenStreetMap features by exact name: gap census extracts, OSM contact pulls, basemap, five Overpass box queries | 235 | 135 high, 100 medium |
| Nominatim street addresses (167 not tried before) | 0 | 19 results, all streets |

Medium confidence means the only locality evidence is the town or city (Arusha, Moshi, Usa River), or the record came from an OpenStreetMap import whose only feature of that name lies at the stored campus and distance.

## Applied

| List | Placed | Not applied |
|---|---|---|
| Company master | 257 | 0 |
| Government run (ward offices; WFP Field Survey 2021 points mapped with `name:sw`/`name:en` only, which the run's collector did not read) | 58 | 4 conflicts with reviewed ward overrides: Ambureni, Kindi, Mnadani, Moivo |
| Welfare run | 2 | 1 conflict (Amani Centre for Street Children: a reviewed override keeps its Arusha drop-in centre); KIWAKKUKI held back, as on 2026-10-11 (a point would release a draft on a route the run marks risky) |

## Held for review

These leads had a same-name candidate that was not accepted (`runtime/geocode/review.json`):
- Bank and fuel chains (Barclays, CRDB, Exim, NBC, Njake Oil): several branches of the same name.
- Points that contradict the record:
  - Tengeru Institute of Community Development: the mapped point is 8 km from Tengeru.
  - Mateves ward office: 15 km from the ward.
  - Bondeni (Hai) and Majengo (Meru): the only ward offices of that name lie in Moshi.
- Records with no locality to confirm the point: Ahadi Lodge, Davos Hotel, Freedom Lodge, Lake Duluti Lodge.
- Sites that publish several points (branches).

## Not reached

- The leads still not at point level go to `runtime/geocode/gmaps_worklist_2026-10-13.jsonl` for the coordinator's Google Maps lookups. Leads already looked up there with no result are listed separately.
- A record with only a P.O. box, including the 26 savings groups from the TCDC register, stays at the five-campus line until a source gives its office.
