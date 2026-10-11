# Silverleaf catchment criteria

*As of 2026-10-11. This document says how we decide whether a lead is close enough to a campus to be worth writing to, and how distance changes its priority. The rules are taken from the scripts and run configurations named at the end; the counts come from the three databases.*

## In one minute

- **The catchment is 25 km in a straight line from the nearest of our five campuses.** Silverleaf's own school transport is priced up to 25 km, so families beyond that are unlikely to reach us every day.
- **Nearer is better, in steps of 5 km.** Every lead with a known location falls into one of six bands: 0–5, 6–10, 11–15, 16–20, 21–25 or beyond 25 km. The bands feed each segment's score.
- **Each segment applies the line differently.** For employers it is a ranking factor, since staff live in many places. Homes and programmes beyond 25 km are held. Funders and introducers are judged by whom they reach near the campuses, not by where their office is. For government, only offices covering wards within 25 km are in scope, and the nearest wards come first.
- **Everything starts from the campus points.** Each campus is placed at the map pin on its own page of Silverleaf's website (section 1).
- **Distances are approximate on the lead side.** They are straight-line distances, not road distances, and many leads are placed only to a neighbourhood or town.

---

## 1. The anchors: five campuses

### Where the campus coordinates come from

The method starts here: every distance in this document is measured from these five points.

1. **The source is Silverleaf's own website.** Each campus page on silverleaf.co.tz (under *Our Schools*) embeds a map with a pin the school placed itself. The pin's coordinates are stored in the page's own data, in the map widget's `locations` entry (`latitude`, `longitude`, `title`). We read them on 2026-10-11.
2. **Google Maps corroborates two.** The Usa River and Ilboru listings sit on the same points. The website's business location for Usa River is within 25 m of the pin. Google has no listing for Arusha City (Sakina) or Boma Ng'ombe. Its "Kijenge Campus" listing is pinned about 70 km away, so it was not used. (That Google listing needs correcting: parents searching it get wrong directions.)
3. **The points are stored in the master database.** They sit in the `campuses` table, with the page used as the source. Every script that measures distance reads them from there: the welfare and government runs, the company importer, the distance recompute and the lead map.
4. **When a campus moves or a pin is corrected,** update the table and re-run:
   - `scripts/master/recompute_campus_distances.py --apply`
   - `scripts/master/rank_employer_reach.py --apply`
   - the welfare and government pipelines

   A lead that was inside the catchment before a correction is never dropped because of it (section 5).

| Campus | Latitude | Longitude | Source (campus page) |
|---|---|---|---|
| Arusha City (Sakina) | −3.3604966 | 36.6609326 | silverleaf.co.tz/our-schools/arusha-city-campus |
| Usa River | −3.3610030 | 36.8644524 | silverleaf.co.tz/our-schools/usa-river-campus (and Google Maps) |
| Ilboru | −3.3497598 | 36.6822737 | silverleaf.co.tz/our-schools/ilboru-campus (and Google Maps) |
| Kijenge | −3.3829460 | 36.7107520 | silverleaf.co.tz/our-schools/kijenge-campus |
| Boma Ng'ombe | −3.3414560 | 37.1457123 | silverleaf.co.tz/our-schools/boma-campus (plus code M45W+H6R) |

Until 2026-10-11 the campuses were placed at ward or town centres (Nominatim), 0.1 to 1.2 km from these pins:

| Campus | Correction |
|---|---|
| Kijenge | 0.1 km |
| Usa River | 0.4 km |
| Arusha City | 0.9 km |
| Ilboru | 1.2 km |
| Boma Ng'ombe | 1.2 km |

### The campuses

| Campus | Area | Levels taught | Primary (Std 1–7)? |
|---|---|---|---|
| Arusha City | Sakina, Arusha–Nairobi Road | K1–K2, Std 1–7 | Yes |
| Usa River | Momela Road, Usa River (Arumeru) | K1–K2, Std 1–7, boarding | Yes |
| Ilboru | Ilboru, Arusha | Daycare, K1–K2 | No |
| Kijenge | Kijenge, Arusha | Daycare, K1–K2 | No |
| Boma Ng'ombe | Mahakama Road, Boma Ng'ombe (Hai, Kilimanjaro) | Daycare, K1–K2 | No |

**Three clusters.** The government run groups the campuses into three clusters, and the map and the ward waves follow them:
- **Arusha:** Sakina, Ilboru and Kijenge lie within about 6 km of one another.
- **Usa River:** about 17–23 km east of the Arusha campuses.
- **Boma Ng'ombe:** about 31 km beyond Usa River.

| Straight-line km | Ilboru | Kijenge | Usa River | Boma Ng'ombe |
|---|---|---|---|---|
| Arusha City | 2.7 | 6.1 | 22.6 | 53.9 |
| Ilboru | | 4.9 | 20.3 | 51.5 |
| Kijenge | | | 17.2 | 48.5 |
| Usa River | | | | 31.3 |

**Only two campuses teach primary.** Usa River and Arusha City teach Std 1–7; the other three stop at K2. The welfare and government runs therefore record two distances for every place:
- to the **nearest campus**: for daycare and pre-primary children;
- to the **nearest primary campus**: for school-age children.

The government ward score weights the two equally.

---

## 2. How distance is measured

- **What is measured.** The straight-line (great-circle) distance from the lead's point to each campus, rounded to 0.1 km. The lead belongs to its nearest campus.
- **Not road distance.** A ward 12 km away across Mount Meru's lower slopes may be a longer drive than one 15 km away along the Arusha–Moshi road. Bands are a first sort, not a travel time.
- **Location precision.** Every point records how precise it is, and the rules treat imprecise points with care.

| Precision | What it means | Typical error |
|---|---|---|
| point / address | The office's own map point or street address | under 0.5 km |
| locality | A neighbourhood or ward centre from the published address | 1–3 km |
| town / city | Only the town is known (Arusha, Moshi, Usa River) | up to 8 km |
| estimated (wards) | One reference point per ward: its mapped office, a checked Wikipedia point, or OpenStreetMap places named like the ward | 1–5 km |
| unknown | No usable location | — |

- **Plausibility checks.** These catch locations that cannot be right; none of them is a scope rule:
  - Welfare and government research is collected inside a box around the campuses (latitude −3.62 to −3.10, longitude 36.42 to 37.40).
  - The welfare NGO register is read to 30 km, so that places just over the line are seen and judged.
  - A point outside northern Tanzania raises a review item.
  - In the government run, two location sources that disagree by more than 5 km raise one too.

---

## 3. The bands

| Band | Meaning for outreach |
|---|---|
| 0–5 km | The first wave everywhere: a daily commute to the nearest campus |
| 6–10 km | Still close: in the first wave for employers and government wards |
| 11–15 km | Reachable with school transport |
| 16–20 km | Reachable with school transport; a later wave for government wards |
| 21–25 km | The edge of the transport area; lowest priority inside the catchment |
| beyond 25 km | Outside the catchment |

**Transport cost rises with distance.** The offer register prices school transport at TZS 550,000–1,000,000 a year, depending on distance. The register also says no offer guarantees a transport route; admissions confirms each family's campus.

---

## 4. How each segment uses the catchment

### Employers (company master)

The employer is a route to its staff, and staff do not all live next to the office. So distance **ranks** an employer rather than ruling it in or out:

- **Reach score:** 0–5 km from a campus +2, 6–10 km +1, beyond 40 km −3. It sits alongside the kind of employer, published staff numbers and named people (`rank_employer_reach.py`).
- **Radius tiers:** Core is 10 km or less, Outer is 25 km or less (from the original collection, `build_partner_leads.py`).
- **Held as outside the catchment:** a business whose operations are outside the Arusha–Kilimanjaro area is held. Each such case is reviewed and sourced in `data/reference/employer-corrections.json`, and 39 plans are held this way. A company headquartered in Dar es Salaam or abroad is kept, but ranked last.

| Distance to the nearest campus | Businesses |
|---|---|
| 0–5 km | 505 |
| 6–10 km | 64 |
| 11–25 km | 60 |
| More than 25 km | 37 |
| Location not recorded | 50 |

### Introducers

There is no distance rule. A chamber, association or HR body is judged by how many of its members employ staff near the campuses, so national bodies are in scope.

### Welfare organisations

| Kind | Rule |
|---|---|
| Homes, programmes and specialised centres | **Held beyond 25 km** of the nearest campus, and held while the location is unresolved. A place known only to town level is held when the town straddles the line (distance + 8 km over 25 km). |
| Funders | No distance rule for the funder's own office, which is often abroad. A funder is held unless it has a **verified link to a home, programme or children within 25 km**. |
| Networks | Exempt. What matters is their members near the campuses, recorded as relationships. |

**Priority points for distance.** Distance counts only when the location is better than town level:

| Distance | Points |
|---|---|
| 0–5 km | 15 |
| 6–10 km | 12 |
| 11–15 km | 9 |
| 16–20 km | 6 |
| 21–25 km | 3 |

| Band (all 502 welfare records) | Organisations |
|---|---|
| 0–5 km | 228 |
| 6–10 km | 49 |
| 11–15 km | 22 |
| 16–20 km | 16 |
| 21–25 km | 93 |
| Beyond 25 km | 22 |
| Unknown | 72 |

### Government offices

| Level | Rule |
|---|---|
| **Ward** | In scope when its reference point is within 25 km of a campus. A ward in a pilot council whose location is unknown is also kept, without a score. So is a ward listed under `catchment_kept` in the run configuration: it was inside the line before a campus point was corrected. Its transport score is 25 points × the average of two band weights: one for the nearest campus and one for the nearest primary campus. The weights are 0–5 km 1.0, 6–10 km 0.8, 11–15 km 0.6, 16–20 km 0.4, 21–25 km 0.2. |
| **Order** | Wards and villages within 10 km come first (55), then 10–20 km (33). The 31 beyond 20 km are a later wave, and 12 are not yet located. A council's introduction letter names only its highest-scored wards within 10 km. |
| **Council** | In scope when at least one of its wards falls within 25 km of a campus. Longido District Council is out: it has no ward within 25 km. The four pilot councils are Arusha City, Arusha District, Meru and Hai. |
| **District and region** | Courtesy notices for the districts and regions that contain catchment wards. |
| **Village** | In scope when mapped within 25 km. |

---

## 5. Corrections never remove a lead

When a campus point is corrected, some distances move by up to about a kilometre. On 2026-10-11 the user decided that such a correction may place a lead nearer a different campus, but must never remove a lead that was inside the catchment or its bands.

| List | What the 2026-10-11 correction changed |
|---|---|
| Welfare | No organisation crossed the 25 km line outward and no draft changed status. Two moved inside the line (We Care Aid and Kilimanjaro Aid Project, both now 24.9 km). 19 now sit nearer a different campus. |
| Government | Gararagua ward (Siha) moved from 24.2 to 25.4 km. It is **kept in scope** through `catchment_kept` in `data/runs/arusha-government-2026-09/run-config.json`, with the reason recorded. Msaranga ward (Moshi Municipal) moved from 25.4 to 24.5 km and came into scope, making 150 offices. |
| Employers | Distance never removes a company. 51 companies now sit nearer a different campus, mostly within the Arusha cluster. Reach tiers were re-ranked: 32 companies changed tier, mainly because stale bands were corrected. |

**How the company distances were recomputed.** The master holds coordinates for only 47 companies. The rest were placed at import by their locality, using the importer's gazetteer:
- **47** were recomputed from their own coordinates.
- **383** were recomputed from the gazetteer point the importer used. The point was accepted only where it reproduces the stored distance under the old campus points.
- **440** kept their stored distance, which is at most about 1.2 km off. Their band and tier were recomputed from it, which also fixed the 21 stale bands.
- **101** have no location.

The full record is in `outputs/reports/campus-distance-recompute.json`.

## 6. Known gaps and proposed fixes

1. **Straight-line distance only.** For leads at 11–25 km, a road distance or drive time would be fairer. This is not yet built.
2. **440 companies keep a distance computed from the old campus points.** Placing them from their address would give them coordinates of their own.
3. **About 50 companies have no nearest campus recorded.** Most have an address or town that could be placed at locality level.
4. **Ward locations are estimates.** OpenStreetMap has no ward boundaries here. Official ward boundaries would replace the single reference points.

## 7. Take-aways

1. **Start from the school's own pins, not a search engine.** The school placed the pins on its own campus pages itself, so they are the most reliable source. Google Maps confirmed only two campuses, had no listing for two others, and pinned one in the wrong place.
2. **Fix Silverleaf's Google listings.** This is for whoever manages Silverleaf's Google profile:
   - The "Kijenge Campus" listing is pinned about 70 km away, so parents get wrong directions.
   - Two other listings match no campus: "Silverleaf Primary School" near Usa River, and "Silverleaf Academy Office" in Moshi.
   - Arusha City (Sakina) and Boma Ng'ombe have no listing at all.

   Correct or remove these, and add the missing ones using the website pins.
3. **A correction should move leads, not drop them.** Re-running distances after a campus point changes can push a lead across the 25 km line. Keep any lead that was inside before, with the reason recorded (section 5), and review it on its merits.
4. **Keep one source of truth for the campus points (fixed 2026-10-11).** The points used to be written out in three places:
   - the `campuses` table in the master database
   - the original importer, `build_partner_leads.py`
   - the TATO browser collector, `collect_partner_leads.js`, which had its own, different estimates

   Now:
   - The importer reads the table, like the welfare and government runs, the distance recompute and the lead map do.
   - The browser collector runs inside a web page and cannot read the database. It keeps a marked preview copy, and its distances are recomputed from the table when the leads are built.

   To correct a campus, change only the table.

---

*Sources: the campus pages of silverleaf.co.tz (campus pins, read 2026-10-11), `outputs/master/Silverleaf Master Database.sqlite` (campuses, organisations, employer_reach), `scripts/master/recompute_campus_distances.py`, `outputs/reports/campus-distance-recompute.json`, `data/runs/arusha-welfare-2026-09/run-config.json`, `data/runs/arusha-government-2026-09/run-config.json`, `scripts/welfare/welfare_lib.py` (bands, distances, boxes), `scripts/welfare/build_welfare_run.py` (welfare holds and points), `scripts/government/build_government_run.py` (ward scope and weights), `scripts/master/rank_employer_reach.py`, `scripts/collection/build_partner_leads.py`, `data/reference/employer-corrections.json`, `data/reference/silverleaf-offer-register.json` (transport fees).*
