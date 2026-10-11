# Lead map

`outputs/maps/Silverleaf Lead Map.html` shows every lead of the company master, the welfare run and the government run around the five campuses. It is one self-contained page: the leads, the campuses and the basemap are embedded, and only the MapLibre GL JS script comes from a CDN.

```powershell
python scripts/maps/build_basemap.py     # only when the basemap needs refreshing (Overpass; cached in runtime/maps/)
python scripts/maps/build_lead_map.py    # read-only on the databases; prints counts and fails on a mismatch
```

## What goes on the map

- **Leads and segments** follow `outputs/messages/Silverleaf Core Segments - <date>.md`:
  - employers: one chosen first message per business (`selection = 'Candidate for review'`), companies and savings groups
  - introducers
  - welfare organisations in scope
  - government offices
- **Confidence** comes from `scripts/messaging/export_resend_contacts.py`: the script imports `company_rows`, `welfare_rows`, `dedupe` and `government_rows` and does not restate the rules.
  - An organisation without an email row is **no email**.
  - An organisation whose inbox another lead shares is **shared inbox**: the exporter sends that inbox one message, under the other lead. The other levels then match the exporter's files exactly.
- **Excluded records** are a separate layer, off by default: master duplicates and shared-inbox records collapsed for sending, master records with no plan, and welfare entries out of scope.
- **Locations**, best first:
  1. the record's own point
  2. a duplicate record's point
  3. a unique, exact name match to a named OpenStreetMap feature
  4. the locality or address against the offline gazetteers (`data/reference/lead-gazetteer.txt`, `collect_partner_leads.js` and the basemap's place names)

  Steps 3 and 4 give an estimated location, drawn with a dashed outline. Leads at one spot are laid on a small spiral so each can be clicked. Leads outside the map box (3.75 to 2.95 S, 36.30 to 37.55 E) or with no location are listed in the page, not drawn.
- **Nearest campus and distance** are straight-line, from the master's `campuses` table.

## Privacy

The page shows organisation names, recipient roles and confidence reasons only. The build removes addresses, numbers and bracketed notes (which quote source pages), reduces welfare red-flag lists to a count, and fails if any contact name from the three databases, an email address or a phone number is left in the data.

## Basemap

`data/reference/maps/arusha-catchment-basemap.geojson` (about 2 MB) is built from an Overpass extract and simplified with shapely. It holds:
- major roads, and streets in Arusha, Usa River-Tengeru and Moshi
- rivers and lakes
- national parks and reserves
- district and region lines
- towns, villages and neighbourhoods, and the summits
- named points of interest (used for name matching only; not drawn)

Data © OpenStreetMap contributors, ODbL 1.0.
