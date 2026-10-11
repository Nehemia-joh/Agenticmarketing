# Campus gap census — 2026-10-11

*What OpenStreetMap and the directories record within 25 km of each campus, against what the company master, the welfare run and the government run already hold. Built by `scripts/collection/build_gap_census.py` from `data/raw/gap-census/`; nothing was written to any database.*

## How to read it

- **OSM**: every feature of the category within 25 km of the campus (the circles overlap: the three Arusha campuses share most features).
- **Captured**: matched to a lead the lists already hold (same OpenStreetMap ID, same website, or a similar name within 0.5 km; a lead without coordinates matches on a near-exact name).
- **New**: a named organisation no list holds. **Review**: a similar name nearby, or the same name elsewhere (a second site or branch).
- **Excluded**: unnamed features, closed places, generic names, schools and kindergartens (competitors), single practitioners and small workshops, airstrips, industrial zones, party offices, police, courts and prisons.
- Villages and neighbourhoods are counted, not matched; places of worship are a candidate list only.

## Census per campus

### Arusha City (Sakina)

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 191 | 163 | 102 | 17 | 30 | 42 |
| Industrial and factory sites | 670 | 659 | 2 | 7 | 2 | 659 |
| Farms, estates and nurseries | 192 | 9 | 0 | 5 | 0 | 187 |
| Hospitals and clinics | 109 | 106 | 26 | 70 | 4 | 9 |
| Colleges, universities and research | 29 | 28 | 14 | 2 | 0 | 13 |
| Hotels, lodges and camps | 237 | 210 | 106 | 30 | 38 | 63 |
| Supermarkets and malls | 31 | 27 | 0 | 12 | 1 | 18 |
| Banks, insurers and finance | 36 | 34 | 33 | 1 | 0 | 2 |
| Airport and aviation | 8 | 5 | 0 | 3 | 0 | 5 |
| Places of worship | 79 | 57 | 0 | 48 | 0 | 31 |
| Social facilities, kindergartens and daycares | 6 | 2 | 1 | 0 | 0 | 5 |
| Villages, hamlets and neighbourhoods | 115 | 114 | 0 | 0 | 0 | 0 |

### Ilboru

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 189 | 162 | 103 | 17 | 28 | 41 |
| Industrial and factory sites | 663 | 652 | 2 | 7 | 2 | 652 |
| Farms, estates and nurseries | 192 | 9 | 0 | 5 | 0 | 187 |
| Hospitals and clinics | 112 | 109 | 26 | 73 | 4 | 9 |
| Colleges, universities and research | 29 | 28 | 14 | 2 | 0 | 13 |
| Hotels, lodges and camps | 241 | 214 | 107 | 33 | 38 | 63 |
| Supermarkets and malls | 31 | 27 | 0 | 12 | 1 | 18 |
| Banks, insurers and finance | 36 | 34 | 33 | 1 | 0 | 2 |
| Airport and aviation | 8 | 5 | 0 | 3 | 0 | 5 |
| Places of worship | 83 | 61 | 0 | 52 | 0 | 31 |
| Social facilities, kindergartens and daycares | 7 | 3 | 2 | 0 | 0 | 5 |
| Villages, hamlets and neighbourhoods | 123 | 122 | 0 | 0 | 0 | 0 |

### Kijenge

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 193 | 165 | 105 | 18 | 28 | 42 |
| Industrial and factory sites | 671 | 660 | 2 | 6 | 2 | 661 |
| Farms, estates and nurseries | 197 | 9 | 0 | 5 | 0 | 192 |
| Hospitals and clinics | 114 | 111 | 26 | 76 | 4 | 8 |
| Colleges, universities and research | 29 | 28 | 14 | 2 | 0 | 13 |
| Hotels, lodges and camps | 240 | 213 | 107 | 33 | 37 | 63 |
| Supermarkets and malls | 31 | 27 | 0 | 12 | 1 | 18 |
| Banks, insurers and finance | 36 | 34 | 33 | 1 | 0 | 2 |
| Airport and aviation | 8 | 5 | 0 | 3 | 0 | 5 |
| Places of worship | 83 | 61 | 0 | 52 | 0 | 31 |
| Social facilities, kindergartens and daycares | 7 | 3 | 2 | 0 | 0 | 5 |
| Villages, hamlets and neighbourhoods | 124 | 124 | 0 | 0 | 0 | 0 |

### Usa River

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 181 | 157 | 96 | 23 | 24 | 38 |
| Industrial and factory sites | 643 | 634 | 2 | 4 | 2 | 635 |
| Farms, estates and nurseries | 112 | 8 | 0 | 5 | 0 | 107 |
| Hospitals and clinics | 111 | 109 | 25 | 76 | 4 | 6 |
| Colleges, universities and research | 30 | 29 | 14 | 2 | 0 | 14 |
| Hotels, lodges and camps | 237 | 210 | 104 | 35 | 35 | 63 |
| Supermarkets and malls | 31 | 28 | 0 | 13 | 1 | 17 |
| Banks, insurers and finance | 36 | 34 | 33 | 1 | 0 | 2 |
| Airport and aviation | 3 | 2 | 0 | 2 | 0 | 1 |
| Places of worship | 83 | 61 | 0 | 52 | 0 | 31 |
| Social facilities, kindergartens and daycares | 8 | 4 | 2 | 0 | 0 | 6 |
| Villages, hamlets and neighbourhoods | 140 | 139 | 0 | 0 | 0 | 0 |

### Boma Ng'ombe

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 83 | 65 | 34 | 17 | 13 | 19 |
| Industrial and factory sites | 419 | 409 | 0 | 10 | 0 | 409 |
| Farms, estates and nurseries | 217 | 18 | 0 | 4 | 0 | 213 |
| Hospitals and clinics | 91 | 87 | 0 | 83 | 1 | 7 |
| Colleges, universities and research | 8 | 7 | 1 | 5 | 0 | 2 |
| Hotels, lodges and camps | 116 | 98 | 12 | 51 | 32 | 21 |
| Supermarkets and malls | 22 | 18 | 0 | 8 | 0 | 14 |
| Banks, insurers and finance | 19 | 18 | 9 | 5 | 4 | 1 |
| Airport and aviation | 6 | 2 | 0 | 2 | 0 | 4 |
| Places of worship | 50 | 32 | 2 | 30 | 0 | 18 |
| Social facilities, kindergartens and daycares | 5 | 5 | 1 | 0 | 0 | 4 |
| Villages, hamlets and neighbourhoods | 197 | 191 | 0 | 0 | 0 | 0 |

### All five campuses (each feature once)

| Category | OSM | Named | Captured | New | Review | Excluded |
|---|---:|---:|---:|---:|---:|---:|
| Offices (company, NGO, government, international, ...) | 288 | 241 | 143 | 39 | 44 | 62 |
| Industrial and factory sites | 1151 | 1130 | 2 | 17 | 2 | 1130 |
| Farms, estates and nurseries | 414 | 27 | 0 | 9 | 0 | 405 |
| Hospitals and clinics | 216 | 209 | 27 | 168 | 5 | 16 |
| Colleges, universities and research | 38 | 36 | 15 | 7 | 0 | 16 |
| Hotels, lodges and camps | 359 | 314 | 119 | 85 | 71 | 84 |
| Supermarkets and malls | 54 | 46 | 0 | 20 | 1 | 33 |
| Banks, insurers and finance | 55 | 52 | 42 | 6 | 4 | 3 |
| Airport and aviation | 14 | 7 | 0 | 5 | 0 | 9 |
| Places of worship | 133 | 93 | 2 | 82 | 0 | 49 |
| Social facilities, kindergartens and daycares | 12 | 8 | 3 | 0 | 0 | 9 |
| Villages, hamlets and neighbourhoods | 346 | 339 | 0 | 0 | 0 | 0 |

## Candidates by segment and subsegment, per nearest campus

New candidates (review candidates in brackets).

| Segment | Subsegment | Arusha City (Sakina) | Ilboru | Kijenge | Usa River | Boma Ng'ombe | Unplaced | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| employer | Aviation | 1 | 0 | 1 | 0 | 3 | 0 | 5 |
| employer | Banks and other companies | 2 | 2 | 5 (1) | 0 | 6 (5) | 3 | 18 (6) |
| employer | Colleges and universities | 0 | 0 | 2 | 0 | 5 | 0 | 7 |
| employer | Farms and estates | 3 | 0 | 3 | 3 | 4 | 1 | 14 |
| employer | Hospitals and clinics | 18 | 12 (1) | 32 | 29 (5) | 71 (3) | 0 | 162 (9) |
| employer | Hotels, lodges and camps | 5 (11) | 8 (7) | 15 (18) | 6 (4) | 44 (35) | 1 | 79 (75) |
| employer | International organisations | 2 | 0 | 3 | 1 | 0 | 4 | 10 |
| employer | Manufacturing | 2 (1) | 0 | 4 (1) | 0 | 10 | 3 | 19 (2) |
| employer | NGOs and research bodies | 7 | 8 | 22 | 10 | 6 | 2 | 55 |
| employer | Public bodies | 0 | 1 | 1 (1) | 0 | 1 | 1 | 4 (1) |
| employer | Retail | 6 | 0 | 4 (2) | 1 | 6 (2) | 0 | 17 (4) |
| employer | Safari operators and travel agencies | 11 | 0 (1) | 0 | 1 | 3 | 0 | 15 (1) |
| welfare | Residential care (children's homes) | 0 | 0 | 0 | 0 | 1 | 0 | 1 |

## Largest gaps

- **Hospitals and clinics**: 168 new named features, 27 captured. Nearest new: Buturi Health Laboratory (0.3 km, Kijenge), Bible Baptist Clinic (0.6 km, Kijenge), ELERAI DISP. Dispensary (1.0 km, Arusha City (Sakina)), Total Care Health Center (1.1 km, Kijenge), Total Care Medical Center (1.1 km, Kijenge).
- **Hotels, lodges and camps**: 85 new named features, 119 captured. Nearest new: Sinzia Villas (0.1 km, Arusha City (Sakina)), Summit Safari Lodge (0.3 km, Arusha City (Sakina)), Kili-Meru Annex Resort (1.0 km, Boma Ng'ombe), Kiriwe Lodge (1.1 km, Boma Ng'ombe), Masai Camp (1.1 km, Kijenge).
- **Offices (company, NGO, government, international, ...)**: 39 new named features, 143 captured. Nearest new: Asante Rabi (1.8 km, Ilboru), Kimotco Ltd (1.8 km, Ilboru), Modern Refrigeration (2.3 km, Kijenge), Tanfoam (3.0 km, Arusha City (Sakina)), East Africa Seed (3.0 km, Arusha City (Sakina)).
- **Supermarkets and malls**: 20 new named features, 0 captured. Nearest new: Green Supermarket (0.2 km, Kijenge), Mariam Supermarket (0.2 km, Arusha City (Sakina)), Sakina Supermarket (1.1 km, Arusha City (Sakina)), Mr Price (1.3 km, Boma Ng'ombe), HEAVENLIGHT SUPERMARKET (1.4 km, Arusha City (Sakina)).
- **Industrial and factory sites**: 17 new named features, 2 captured. Nearest new: Seven-up Bottling Company Tanzania Ltd (1.3 km, Kijenge), Sunkist Bakery Limited Milling Machine (2.2 km, Kijenge), A-TO-Z FACTORY (3.1 km, Kijenge), Arsho Industry (7.9 km, Boma Ng'ombe), Halisi Product Limited Milling Machine (9.4 km, Arusha City (Sakina)).
- **Farms, estates and nurseries**: 9 new named features, 0 captured. Nearest new: Kili Flora Flower Farms (0.5 km, Usa River), Tanzania Poultry Farm (3.3 km, Usa River), Kiliflora Farm Nduruma (6.3 km, Kijenge), Shamba la Maua (9.1 km, Boma Ng'ombe), Lambo Estate (10.8 km, Boma Ng'ombe).
- **Targeted known gaps** (official pages, the ATE employer directory, the coordinator's Google Maps pins): 51 new, 0 to review.
- **International NGOs on the NGO register** inside the catchment and active since 2024, held by no list: 50.

## Excluded, by reason

| Category | Reason | Features |
|---|---|---:|
| Offices (company, NGO, government, international, ...) | unnamed feature | 47 |
| Offices (company, NGO, government, international, ...) | small professional office | 4 |
| Offices (company, NGO, government, international, ...) | generic name, no organisation named | 4 |
| Offices (company, NGO, government, international, ...) | government office excluded from outreach (political_party) | 2 |
| Offices (company, NGO, government, international, ...) | a building or room of a larger site | 2 |
| Offices (company, NGO, government, international, ...) | government office excluded from outreach (religious) | 1 |
| Offices (company, NGO, government, international, ...) | government office excluded from outreach (police) | 1 |
| Offices (company, NGO, government, international, ...) | government office excluded from outreach (court) | 1 |
| Industrial and factory sites | small workshop or mill (no company named) | 1092 |
| Industrial and factory sites | unnamed feature | 21 |
| Industrial and factory sites | closed or disused | 10 |
| Industrial and factory sites | school (a competitor or not an employer target) | 3 |
| Industrial and factory sites | industrial zone (an area, not one employer) | 2 |
| Industrial and factory sites | generic name, no organisation named | 2 |
| Farms, estates and nurseries | unnamed feature | 387 |
| Farms, estates and nurseries | generic name, no organisation named | 13 |
| Farms, estates and nurseries | school (a competitor or not an employer target) | 2 |
| Farms, estates and nurseries | small farm or plot with no business named | 2 |
| Farms, estates and nurseries | farm plot of another institution | 1 |
| Hospitals and clinics | unnamed feature | 7 |
| Hospitals and clinics | generic name, no organisation named | 5 |
| Hospitals and clinics | single practitioner's practice | 2 |
| Hospitals and clinics | school (a competitor or not an employer target) | 1 |
| Hospitals and clinics | traditional healer or shop | 1 |
| Colleges, universities and research | a building or room of a larger site | 11 |
| Colleges, universities and research | unnamed feature | 2 |
| Colleges, universities and research | generic name, no organisation named | 1 |
| Colleges, universities and research | school (a competitor or not an employer target) | 1 |
| Colleges, universities and research | police, military or prison college | 1 |
| Hotels, lodges and camps | unnamed feature | 45 |
| Hotels, lodges and camps | generic name, no organisation named | 26 |
| Hotels, lodges and camps | private apartments | 11 |
| Hotels, lodges and camps | not a hotel (restaurant or hall) | 1 |
| Hotels, lodges and camps | a building or room of a larger site | 1 |
| Supermarkets and malls | small shop or open market | 16 |
| Supermarkets and malls | unnamed feature | 8 |
| Supermarkets and malls | generic name, no organisation named | 6 |
| Supermarkets and malls | mall or commercial complex: its tenants are the employers | 3 |
| Banks, insurers and finance | unnamed feature | 3 |
| Airport and aviation | unnamed feature | 7 |
| Airport and aviation | generic name, no organisation named | 2 |
| Places of worship | unnamed feature | 40 |
| Places of worship | generic name, no organisation named | 9 |
| Social facilities, kindergartens and daycares | kindergarten or daycare: a competitor, not an outreach target | 5 |
| Social facilities, kindergartens and daycares | unnamed feature | 4 |

## Villages and mitaa in the pilot councils

| Council | Unit | From OpenStreetMap | Already in the government run |
|---|---|---:|---:|
| Arusha City Council | kitongoji (hamlet) | 5 | 0 |
| Arusha City Council | mtaa | 27 | 0 |
| Arusha District Council | kitongoji (hamlet) | 33 | 0 |
| Arusha District Council | mtaa (township) | 24 | 0 |
| Arusha District Council | village | 9 | 0 |
| Meru District Council | kitongoji (hamlet) | 6 | 0 |
| Meru District Council | mtaa (township) | 30 | 0 |
| Meru District Council | village | 34 | 0 |
| Hai District Council | kitongoji (hamlet) | 6 | 0 |
| Hai District Council | mtaa (township) | 30 | 0 |
| Hai District Council | village | 37 | 0 |

Official totals for comparison (council websites, captured 2026-10-10): Arusha City 154 mitaa; Arusha District 67 villages and 256 vitongoji; Hai 62 villages; Meru publishes no total on its site. Ward assignment is estimated (nearest ward reference point) unless the place shares the ward's name.

## Places of worship (candidate list only)

| Nearest campus | Christian | Muslim | Other or untagged | Total |
|---|---:|---:|---:|---:|
| Arusha City (Sakina) | 5 | 2 | 2 | 9 |
| Ilboru | 4 | 1 | 2 | 7 |
| Kijenge | 14 | 0 | 14 | 28 |
| Usa River | 6 | 0 | 3 | 9 |
| Boma Ng'ombe | 24 | 3 | 4 | 31 |

## Proposed new employer kinds and reach weights

`rank_employer_reach.py` scores kind of employer on a 1–4 scale (hospital or clinic 4, college 4, hotel 3, bank or other company 3, NGO 2, public body 1, safari operator 1).

| Kind | Weight | Why |
|---|---:|---|
| International organisations | 4 | Large salaried professional workforces (UN, AU and EAC organs, ECSA-HC, ESAMI) with stable tenure; many already pay staff education allowances, so a staff education benefit is familiar. Approach through HR, like a public body, but they are not government offices. |
| Manufacturing | 3 | Large permanent on-site workforces with shift supervisors and managers, like the corporate employers. |
| Aviation | 3 | Salaried technical, ground and cargo staff concentrated at KIA and Arusha airport. |
| Farms and estates | 2 | Large but often seasonal workforces; the benefit reaches mainly permanent and supervisory staff, and many workers live in estate villages. |
| Retail | 2 | Many staff, but branch-level decisions and lower wages; the chain's head office decides. |

## Sources and files

- `data/raw/gap-census/osm_offices_2026-10-11.json`: 328 features, OpenStreetMap data as of 2026-10-11T10:50:20Z
- `data/raw/gap-census/osm_industrial_2026-10-11.json`: 1258 features, OpenStreetMap data as of 2026-10-11T10:52:21Z
- `data/raw/gap-census/osm_farms_2026-10-11.json`: 415 features, OpenStreetMap data as of 2026-10-11T10:53:21Z
- `data/raw/gap-census/osm_health_2026-10-11.json`: 233 features, OpenStreetMap data as of 2026-10-11T10:57:36Z
- `data/raw/gap-census/osm_education_2026-10-11.json`: 38 features, OpenStreetMap data as of 2026-10-11T11:00:36Z
- `data/raw/gap-census/osm_tourism_2026-10-11.json`: 379 features, OpenStreetMap data as of 2026-10-11T11:02:35Z
- `data/raw/gap-census/osm_retail_2026-10-11.json`: 55 features, OpenStreetMap data as of 2026-10-11T11:04:36Z
- `data/raw/gap-census/osm_banks_2026-10-11.json`: 55 features, OpenStreetMap data as of 2026-10-11T11:13:50Z
- `data/raw/gap-census/osm_aviation_2026-10-11.json`: 14 features, OpenStreetMap data as of 2026-10-11T11:16:49Z
- `data/raw/gap-census/osm_worship_2026-10-11.json`: 143 features, OpenStreetMap data as of 2026-10-11T11:27:05Z
- `data/raw/gap-census/osm_social_2026-10-11.json`: 12 features, OpenStreetMap data as of 2026-10-11T11:25:59Z
- `data/raw/gap-census/osm_places_2026-10-11.json`: 384 features, OpenStreetMap data as of 2026-10-11T11:34:06Z
- `data/raw/gap-census/candidates_2026-10-11.jsonl`: 504 candidates (406 new, 98 review)
- `data/raw/gap-census/master_intake_2026-10-11.csv`: 405 new employers in the shared intake contract
- `data/raw/gap-census/research_GC_welfare_2026-10-11.jsonl`, `government_subward_units_2026-10-11.json`, `faith_candidates_2026-10-11.json`
- `data/raw/gap-census/coverage_2026-10-11.md`: queries, searches and blocks

Map data © OpenStreetMap contributors, ODbL 1.0.
