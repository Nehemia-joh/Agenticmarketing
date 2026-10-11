# Lead map

`outputs/maps/Silverleaf Lead Map.html` shows every lead of the company master, the welfare run and the government run around the five campuses. It is one complete HTML page that works opened from disk or from a web server: the leads, the campuses and the basemap are embedded, and the MapLibre GL JS 4.7.1 script comes from a CDN. The default view needs nothing else; the other views load tiles from their providers while the page is open. The page is self-hosted, so it may call those providers.

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

  Steps 3 and 4 give an estimated location, drawn with a dashed outline. A master point placed only to a locality (`geocode_precision` locality, town or city) is also drawn as estimated. In step 4 a place in the map area wins over a longer place name elsewhere in the same text, and roads named after other towns ('Dodoma Road', 'Nairobi Rd') are ignored. Leads at one spot are laid on a small spiral so each can be clicked. A lead whose own point lies in Tanzania but outside the map box (3.75 to 2.95 S, 36.30 to 37.55 E), which is always well over 25 km from a campus, is drawn as a faded pin with a square outline, outside the catchment area (the user's decision of 2026-10-11, for African Galleria at Karatu): it sorts under the other pins, shows only under "All campuses" (never in a campus's filter, chip count or popup count), has its own layer toggle, and the map can be panned to it (the online views show its surroundings; the offline basemap covers only the box). Leads with no location, only a town outside the box, or an office abroad are listed in the page, not drawn; a lead checked by the location research (`data/raw/geocode-research/geocodes_<date>.jsonl`) says so.
- **Funders** whose own office has no point in the map area (usually abroad) are drawn, estimated, at the home or programme they fund or run, but only where the welfare run records that relationship as verified and the place is itself located in the map area; the nearest such place to a campus is used.

## Placing more leads

```powershell
python scripts/maps/collect_geocodes.py targets                     # the leads to place, by the map's own rules
python scripts/maps/collect_geocodes.py sites --scope unplaced --fetch   # pins on the organisations' own websites
python scripts/maps/collect_geocodes.py osm                         # named OpenStreetMap features (Overpass, cached)
python scripts/maps/collect_geocodes.py nominatim --scope unplaced  # street addresses
# review the candidates in runtime/geocode/, write accepted points to data/raw/geocode-research/geocodes_<date>.jsonl
python scripts/master/apply_geocodes.py            # preview; --apply merges into the master and the runs' links.json
```

Then recompute the master's distances and reach (`recompute_campus_distances.py --apply`, `rank_employer_reach.py --apply`), rebuild the workbook, run both run pipelines and rebuild this map. A point needs its source URL, the date read, the coordinates or excerpt as found, a precision (point, address or locality) and the basis; a coordinate pair that several unrelated websites share is a listing platform's default for the town, not a pin, and is not used.
- **Nearest campus and distance** are straight-line, from the master's `campuses` table.

## Map views

A segmented control beside the zoom buttons switches the basemap. The leads, campus pins, distance rings, filters, counts and popups stay the same in every view.

| View | What it shows | Source | Attribution shown |
|---|---|---|---|
| **Lead map** (default) | The embedded basemap below, in the page's light or dark colours | `data/reference/maps/arusha-catchment-basemap.geojson`, inside the page | © OpenStreetMap contributors |
| **Street** | Buildings, shop and office names, street names (zoom to 18) | [OpenFreeMap](https://openfreemap.org) `liberty` style, `https://tiles.openfreemap.org/styles/liberty` | OpenFreeMap © OpenMapTiles Data from © OpenStreetMap contributors |
| **Terrain** | Hill shading over the lead map's basemap | [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) on AWS Open Data, Terrarium encoding, `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png` | © OpenStreetMap contributors · Elevation: Terrain Tiles (Mapzen, AWS Open Data; SRTM and GMTED2010 courtesy of the U.S. Geological Survey, ETOPO1 by NOAA) |
| **Topographic** | Contours, relief, paths and place names | [OpenTopoMap](https://opentopomap.org), `https://tile.opentopomap.org/{z}/{x}/{y}.png` | Map data: © OpenStreetMap contributors, SRTM \| Map style: © OpenTopoMap (CC-BY-SA) |

How it works (`scripts/maps/lead_map_template.html`, the `VIEWS` list):
- Each view builds a complete MapLibre style: its basemap, then our overlay (`rings`, `excluded`, `leads`).
- Switching calls `map.setStyle(style, { diff: false })`. On `style.load` the page redraws the marker images and sets the overlay data from the current filters. A `styleimagemissing` handler draws any marker image that is missing.
- Campus pins, popups and the place labels are HTML, so a style change does not touch them. Place labels are hidden in Street and Topographic, which have their own.
- The page fetches the Street style document itself, with a 12-second timeout, before switching. If that fails, the map stays on the current view and a note says why.
- If the current view's tiles, sprite or fonts fail to load, a small note offers **Back to Lead map**. The leads and filters keep working either way.
- The chosen view is kept per viewer in `localStorage` (`silverleaf-lead-map-view`). Each read and write is wrapped in try/catch, so blocked storage falls back to Lead map. A saved view other than Lead map is applied after the first load, so a provider that is down cannot blank the page.
- Themes: Lead map and Terrain follow light and dark; the hill shading has its own light and dark colours. Street uses `liberty` in both themes, because OpenFreeMap's dark styles (`dark`, `fiord`) and `positron` leave out shop and office names. Topographic is light only, because its tiles are fixed images.
- **Satellite** is deferred until a provider is chosen. The commented entry at the end of `VIEWS`, and the matching branch in `viewStyle()`, are where it goes.

Provider terms, checked 2026-10-11:
- **OpenFreeMap:** free, with no key, no registration and no cookies. Production and commercial use are allowed and no limits are stated. There is no SLA. Attribution is required.
- **AWS Terrain Tiles:** an open dataset on the AWS Registry of Open Data. Its source credits are in [joerd's attribution.md](https://github.com/tilezen/joerd/blob/master/docs/attribution.md). Around Arusha the data comes from SRTM, GMTED2010 and ETOPO1.
- **OpenTopoMap:** CC-BY-SA, free with attribution. Its FAQ allows embedding in websites as long as the server is not overloaded, for example by mass downloads. There is no numeric quota and no uptime guarantee. That suits a small self-hosted page; do not prefetch or bulk-download its tiles. The operators welcome a short note about how the map is used.
- **Not used:** `tile.openstreetmap.org`. Its tile usage policy rules out this kind of production use.

## Street-level links

Every popup (lead, excluded record and campus) has a **See the place** row. Each link opens in a new tab, and the links carry the coordinates only:
- **Street View:** `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=<lat>,<lon>`
- **Mapillary:** `https://www.mapillary.com/app/?lat=<lat>&lng=<lon>&z=17`
- **Google Maps:** `https://www.google.com/maps/search/?api=1&query=<lat>,<lon>`
- **OpenStreetMap:** `https://www.openstreetmap.org/?mlat=<lat>&mlon=<lon>#map=18/<lat>/<lon>`

For a lead with an estimated location (dashed outline), the popup says that the point is approximate, so street-level imagery may show the general area rather than the building. Street View and Mapillary coverage around Arusha is patchy away from the main roads. Where a link finds no imagery, Google shows the nearest panorama or none, and Mapillary opens an empty map.

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
