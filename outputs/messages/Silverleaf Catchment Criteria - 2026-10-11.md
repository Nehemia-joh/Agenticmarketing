# Silverleaf catchment criteria

*As of 2026-10-11. This document says how we decide whether a lead is close enough to a campus to be worth writing to, and how distance changes its priority. The rules are taken from the scripts and run configurations named at the end; the counts come from the three databases.*

## In one minute

- **The catchment is 25 km in a straight line from the nearest of our five campuses.** Silverleaf's own school transport is priced up to 25 km, so families beyond that are unlikely to reach us every day.
- **Nearer is better, in steps of 5 km.** Every lead with a known location falls into one of six bands: 0–5, 6–10, 11–15, 16–20, 21–25 or beyond 25 km. The bands feed each segment's score.
- **Each segment applies the line differently.** For employers it is a ranking factor, since staff live in many places. Homes and programmes beyond 25 km are held. Funders and introducers are judged by whom they reach near the campuses, not by where their office is. For government, only offices covering wards within 25 km are in scope, and the nearest wards come first.
- **Distances are approximate.** They are straight-line distances from estimated campus points, not road distances, and many leads are placed only to a neighbourhood or town.

---

## 1. The anchors: five campuses

| Campus | Area | Levels taught | Primary (Std 1–7)? |
|---|---|---|---|
| Arusha City | Sakina, Arusha–Nairobi Road | K1–K2, Std 1–7 | Yes |
| Usa River | Momela Road, Usa River (Arumeru) | K1–K2, Std 1–7, boarding | Yes |
| Ilboru | Ilboru, Arusha | Daycare, K1–K2 | No |
| Kijenge | Kijenge, Arusha | Daycare, K1–K2 | No |
| Boma Ng'ombe | Mahakama Road, Boma Ng'ombe (Hai, Kilimanjaro) | Daycare, K1–K2 | No |

**Three clusters.** The government run groups the campuses into three clusters, and the map and the ward waves follow them:
- **Arusha:** Sakina, Ilboru and Kijenge lie within about 6 km of one another.
- **Usa River:** about 17–22 km east of the Arusha campuses.
- **Boma Ng'ombe:** about 31 km beyond Usa River.

| Straight-line km | Ilboru | Kijenge | Usa River | Boma Ng'ombe |
|---|---|---|---|---|
| Arusha City | 3.5 | 6.4 | 22.4 | 53.0 |
| Ilboru | | 4.6 | 19.1 | 49.5 |
| Kijenge | | | 17.1 | 47.9 |
| Usa River | | | | 30.7 |

**Only two campuses teach primary.** Usa River and Arusha City teach Std 1–7; the other three stop at K2. The welfare and government runs therefore record two distances for every place:
- to the **nearest campus**: for daycare and pre-primary children;
- to the **nearest primary campus**: for school-age children.

The government ward score weights the two equally.

**The campus points are estimates.** Each campus is placed at its ward or town centre (Nominatim), not at its gate. Replacing them with the gates' coordinates would sharpen every distance in this document by up to a kilometre or two.

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
| 0–5 km | 452 |
| 6–10 km | 65 |
| 11–25 km | 39 |
| More than 25 km | 38 |
| Location not recorded | 122 |

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
| 6–10 km | 42 |
| 11–15 km | 29 |
| 16–20 km | 15 |
| 21–25 km | 92 |
| Beyond 25 km | 24 |
| Unknown | 72 |

### Government offices

| Level | Rule |
|---|---|
| **Ward** | In scope when its reference point is within 25 km of a campus. A ward in a pilot council whose location is unknown is also kept, without a score. Its transport score is 25 points × the average of two band weights: one for the nearest campus and one for the nearest primary campus. The weights are 0–5 km 1.0, 6–10 km 0.8, 11–15 km 0.6, 16–20 km 0.4, 21–25 km 0.2. |
| **Order** | Wards within 10 km come first (51), then 10–20 km (34). The 31 beyond 20 km are a later wave, and 12 are not yet located. A council's introduction letter names only its highest-scored wards within 10 km. |
| **Council** | In scope when at least one of its wards falls within 25 km of a campus. Longido District Council is out: it has no ward within 25 km. The four pilot councils are Arusha City, Arusha District, Meru and Hai. |
| **District and region** | Courtesy notices for the districts and regions that contain catchment wards. |
| **Village** | In scope when mapped within 25 km. |

---

## 5. Known gaps and proposed fixes

1. **Campus coordinates are estimates.** Record each campus gate's coordinates. Then re-run the three pipelines, which recompute every distance and band.
2. **Straight-line distance only.** For leads at 11–25 km, a road distance or drive time would be fairer. This is not yet built.
3. **Stale bands on some company records.** 21 of 661 company records carry a transport band that disagrees with their recorded distance. For example, one record at 2.7 km is marked "beyond 40 km". 426 records have no radius tier at all, because they came from later imports. The reach rank reads the band, so recomputing bands and tiers from the coordinates is the fix.
4. **122 companies have no location.** Most have an address or town that could be placed at locality level.
5. **Ward locations are estimates.** OpenStreetMap has no ward boundaries here. Official ward boundaries would replace the single reference points.

---

*Sources: `outputs/master/Silverleaf Master Database.sqlite` (campuses, organisations, employer_reach), `data/runs/arusha-welfare-2026-09/run-config.json`, `data/runs/arusha-government-2026-09/run-config.json`, `scripts/welfare/welfare_lib.py` (bands, distances, boxes), `scripts/welfare/build_welfare_run.py` (welfare holds and points), `scripts/government/build_government_run.py` (ward scope and weights), `scripts/master/rank_employer_reach.py`, `scripts/collection/build_partner_leads.py`, `data/reference/employer-corrections.json`, `data/reference/silverleaf-offer-register.json` (transport fees).*
