#!/usr/bin/env python3
"""Collect location evidence for leads the lead map cannot place (or places only by estimate), with no web search.

Three deterministic collectors, cheapest first. Each writes candidates to runtime/geocode/; nothing here changes a database.
A person (or the coordinating agent) reviews the candidates and writes the accepted points, with source URL, date, excerpt,
precision and basis, to data/raw/geocode-research/geocodes_<date>.jsonl; scripts/master/apply_geocodes.py merges that file.

  targets   the leads to place, from the lead map's own placement rules (scripts/maps/build_lead_map.py): unplaced first,
            then estimates (city centre, then locality). Writes runtime/geocode/targets.json.
  sites     coordinates the organisation publishes on its own website: Google Maps embeds and links (!2d<lon>!3d<lat>, !3d!4d,
            @lat,lon, q= / ll= / center=), JSON-LD geo, data-lat/data-lng, LatLng(...), plus codes, and the place text of
            address-only embeds. Reads the contact crawler's cache first (runtime/contacts/http-cache, read-only); with --fetch,
            reads a target's home page and its contact or location page when the cache has none, through contact_lib's polite
            fetcher (1.5 s per site, robots.txt honoured, blocks reported and never worked around), caching new pages under
            runtime/geocode/http-cache. Writes runtime/geocode/site_hits.json.
  osm       named OpenStreetMap features in the map box (amenity, shop, office, craft, industrial, tourism, leisure,
            healthcare, named buildings), five Overpass queries one at a time, >= 6 s apart, [timeout:180], mirror fallback,
            cached in runtime/geocode/overpass/; then candidate name matches for every target. Writes runtime/geocode/osm_hits.json.
  osm-names named OpenStreetMap features anywhere in Tanzania whose name holds a target's distinctive words (for offices outside
            the box), a few batched name-regex queries, one at a time, >= 6 s apart. Writes runtime/geocode/osm_name_hits.json.
  nominatim street addresses of the targets that name a street or building, at most 1 request per second with a User-Agent,
            cached (runtime/geocode/nominatim/); results outside northern Tanzania are dropped. Writes runtime/geocode/nominatim_hits.json.

--targets-file runs sites, osm, osm-names and nominatim on a named list of master leads (for example
data/raw/geocode-research/user_requested_locations_<date>.json) instead of the map's targets; sites --crawl-cache reads another
checkout's crawl cache (read-only), --always-fetch reads contact pages even when a pin is cached, and --mentions records the text
around Arusha, Moshi, Usa River and airport mentions (evidence of a local branch); nominatim --queries takes reviewer-written queries.

Rate limits: skills/silverleaf-create-lead-list/references/research-rate-limits.md (Overpass and Nominatim rules).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.parse
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts" / "welfare"))
sys.path.insert(0, str(ROOT / "scripts" / "government"))
sys.path.insert(0, str(ROOT / "scripts" / "contacts"))
import welfare_lib as W  # noqa: E402  (polite_request with per-host limits)

WORK = ROOT / "runtime" / "geocode"
CRAWL_CACHE = ROOT / "runtime" / "contacts" / "http-cache"
SOUTH, WEST, NORTH, EAST = -3.75, 36.30, -2.95, 37.55   # the lead map's box
BBOX = f"{SOUTH},{WEST},{NORTH},{EAST}"
F = r"(-?\d{1,2}\.\d{3,})"
COORD_PATTERNS = [
    ("maps embed !2d!3d", re.compile(r"!2d" + F + r"!3d" + F), "lonlat"),
    ("maps link !3d!4d", re.compile(r"!3d" + F + r"!4d" + F), "latlon"),
    ("maps link @lat,lon", re.compile(r"maps[^\"'\s<>]{0,200}?@" + F + r",\s*" + F), "latlon"),
    ("maps link q/ll/center=lat,lon", re.compile(r"maps[^\"'\s<>]{0,300}?[?&;](?:amp;)?(?:q|ll|sll|center|daddr|destination|query)="
                                                 + F + r"(?:,|%2C)\s*(?:%20|\+)?" + F, re.I), "latlon"),
    ("JSON lat/lon", re.compile(r"[\"'](?:latitude|lat)[\"']\s*:\s*[\"']?" + F + r"[\"']?\s*,\s*[\"'](?:longitude|lng|lon|long)[\"']\s*:\s*[\"']?" + F, re.I), "latlon"),
    ("data-lat/data-lng", re.compile(r"data-lat(?:itude)?=[\"']" + F + r"[\"'][^>]{0,200}?data-(?:lng|lon|long|longitude)=[\"']" + F, re.I), "latlon"),
    ("script lat:/lng:", re.compile(r"\blat\s*:\s*" + F + r"\s*,\s*(?:lng|lon)\s*:\s*" + F), "latlon"),
    ("LatLng(lat, lon)", re.compile(r"LatLng\(\s*" + F + r"\s*,\s*" + F), "latlon"),
]
PLUS_CODE = re.compile(r"\b([23456789CFGHJMPQRVWX]{4}\+[23456789CFGHJMPQRVWX]{2,3})\b")
MAPS_PLACE = re.compile(r"maps(?:/embed/v1/place\?[^\"'<>\s]{0,200}?q=|\?[^\"'<>\s]{0,200}?\bq=)([^\"'&<>]{4,160})", re.I)
CONTACT_LINK = re.compile(r"contact|location|find-us|reach-us|visit|where|mawasiliano|office", re.I)


def tanzania(lat: float, lon: float) -> bool:
    return -12 < lat < -0.9 and 29 < lon < 41


def in_box(lat: float, lon: float) -> bool:
    return SOUTH <= lat <= NORTH and WEST <= lon <= EAST


def host_of(url: str) -> str:
    url = str(url or "").split()[0] if str(url or "").strip() else ""
    if not url or "@" in url:
        return ""
    return urlsplit(url if "://" in url else "http://" + url).netloc.lower().removeprefix("www.")


# ------------------------------------------------------------------ targets
def cmd_targets(_args) -> int:
    import build_lead_map as B
    basemap = json.loads(B.BASEMAP.read_text(encoding="utf-8"))
    loc = B.Locator(basemap)
    out = []
    m = B.ro(B.MASTER)
    orgs, _contacts, reach, plans, _by_plan, _rows, _skipped, dup_of = B.master_leads(m, loc, "")
    for p in plans:
        o = orgs[p["organisation_id"]]
        lat, lon, prec, how = B.place_master(o, orgs, dup_of, loc)
        if lat is not None and not B.in_box(lat, lon):
            prec = "outside"
        out.append({"db": "master", "seg": "int" if p["segment"] == "Introducers" else "emp", "id": o["organisation_id"], "name": o["name"],
                    "tier": reach.get(o["organisation_id"], ""), "prec": prec, "how": how, "website": o["website"], "locality": o["locality"],
                    "address": o["address"], "segment": o["segment"], "lat": lat, "lon": lon})
    w = B.ro(ROOT / "outputs" / "runs" / B.WELFARE_RUN / "lead-database.sqlite")
    for r in w.execute("SELECT o.* FROM outreach_plans p JOIN organisations o USING(organisation_id) WHERE p.target_type='organisation'"):
        lat, lon = B.num(r["latitude"]), B.num(r["longitude"])
        prec = "none" if lat is None else "outside" if not B.in_box(lat, lon) else ("exact" if r["geocode_precision"] == "address" else "estimated")
        out.append({"db": "welfare", "seg": "wel", "id": r["organisation_id"], "name": r["name"], "tier": r["priority"], "prec": prec,
                    "how": r["geocode_precision"], "website": r["website"], "locality": r["locality"], "address": r["address"],
                    "segment": r["segment"], "lat": lat, "lon": lon})
    g = B.ro(ROOT / "outputs" / "runs" / B.GOVERNMENT_RUN / "lead-database.sqlite")
    for r in g.execute("SELECT o.*, gp.office_level, gp.council_name, gp.admin_unit_name FROM organisations o "
                       "JOIN government_office_profiles gp USING(organisation_id)"):
        lat, lon = B.num(r["latitude"]), B.num(r["longitude"])
        prec = "none" if lat is None else "outside" if not B.in_box(lat, lon) else ("exact" if r["geocode_precision"] == "address" else "estimated")
        out.append({"db": "government", "seg": "gov", "id": r["organisation_id"], "name": r["name"], "tier": r["office_level"], "prec": prec,
                    "how": r["geocode_precision"], "website": r["website"], "locality": r["locality"], "address": r["address"],
                    "council": r["council_name"], "unit": r["admin_unit_name"], "lat": lat, "lon": lon})
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "targets.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(json.dumps({f"{k[0]} {k[1]}": v for k, v in sorted(Counter((x["seg"], x["prec"]) for x in out).items())}, indent=1))
    return 0


def targets_from_file(path: Path) -> list[dict]:
    """A named list of master leads (e.g. data/raw/geocode-research/user_requested_locations_<date>.json: organisation_id,
    name, address, locality, website, ...) as targets, so the collectors can run on leads the user names, wherever they are."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for r in rows:
        if r.get("db") and r.get("id"):  # an inventory row (runtime/geocode/inventory.json) is already a target, in any of the three lists
            site = str(r.get("website") or "").split()[0] if str(r.get("website") or "").strip() else ""
            out.append({**r, "website": site})
            continue
        site = str(r.get("website") or "").split()[0] if str(r.get("website") or "").strip() else ""
        out.append({"db": "master", "seg": "emp", "id": r["organisation_id"], "name": r["name"], "tier": "", "prec": "none", "how": "named",
                    "website": site, "locality": r.get("locality", ""), "address": r.get("address", ""), "segment": "", "lat": None, "lon": None})
    return out


def load_targets(scope: str, targets_file: Path | None = None) -> list[dict]:
    if targets_file:
        return targets_from_file(targets_file)
    targets = json.loads((WORK / "targets.json").read_text(encoding="utf-8"))
    if scope == "unplaced":
        return [t for t in targets if t["prec"] in ("none", "outside")]
    if scope == "estimated":
        return [t for t in targets if t["prec"] in ("none", "outside", "estimated")]
    return targets


# ------------------------------------------------------------------ own websites
def scan_page(body: str) -> list[dict]:
    hits = []
    for label, pat, order in COORD_PATTERNS:
        for m in pat.finditer(body):
            a, b = float(m.group(1)), float(m.group(2))
            lat, lon = (b, a) if order == "lonlat" else (a, b)
            hits.append({"how": label, "lat": lat, "lon": lon, "as_found": body[max(0, m.start() - 30):m.end() + 5][:240],
                         "tanzania": tanzania(lat, lon), "in_box": in_box(lat, lon)})
    for m in PLUS_CODE.finditer(body):
        hits.append({"how": "plus code", "code": m.group(1), "as_found": body[max(0, m.start() - 60):m.end() + 40]})
    for m in MAPS_PLACE.finditer(body):
        q = unquote(m.group(1).replace("+", " ")).strip()
        if not re.match(r"^-?\d", q):
            hits.append({"how": "maps embed place text", "q": q[:160]})
    seen, out = set(), []
    for h in hits:
        key = (h["how"], h.get("lat"), h.get("lon"), h.get("code"), h.get("q"))
        if key not in seen:
            seen.add(key)
            out.append(h)
    return out


def read_cached(meta_path: Path) -> tuple[dict, bytes] | None:
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        raw = meta_path.with_suffix(".bin").read_bytes()
    except (OSError, ValueError):
        return None
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except (OSError, EOFError):
            pass
    return meta, raw


BRANCH_WORDS = re.compile(r"\b(arusha|moshi|usa[ -]?river|kia\b|kilimanjaro (?:international )?airport|njiro|sakina|kijenge|themi|"
                          r"sekei|ngarenaro|kaloleni|sokoine road|india street|boma road|old moshi road|nairobi road|tengeru)", re.I)


def page_text(body: str) -> str:
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", body)
    return re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", body)).strip()


def branch_mentions(body: str, limit: int = 8) -> list[str]:
    """Text around a mention of Arusha, Moshi, Usa River or the airport area: the evidence for (or against) a local branch."""
    text, out = page_text(body), []
    for m in BRANCH_WORDS.finditer(text):
        snippet = text[max(0, m.start() - 90):m.end() + 90]
        if not any(snippet[20:-20] in s for s in out):
            out.append(snippet)
        if len(out) >= limit:
            break
    return out


def cached_pages_by_host(hosts: set[str], cache_dir: Path | None = None) -> dict[str, list[tuple[str, bytes]]]:
    pages = defaultdict(list)
    for meta_path in (cache_dir or CRAWL_CACHE).glob("*.json"):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if meta.get("status") != 200:
            continue
        host = host_of(meta.get("final_url") or meta.get("url"))
        if host not in hosts:
            continue
        got = read_cached(meta_path)
        if got:
            pages[host].append((meta.get("final_url") or meta["url"], got[1]))
    return pages


def cmd_sites(args) -> int:
    targets = [t for t in load_targets(args.scope, getattr(args, "targets_file", None)) if host_of(t.get("website"))]
    hosts = {host_of(t["website"]) for t in targets}
    if args.no_crawl_cache:  # the crawl cache was scanned before (it is slow to read): only the pages fetched here are read
        print(f"{len(targets)} targets with a website on {len(hosts)} hosts; crawl cache skipped", flush=True)
        pages = defaultdict(list)
    else:
        print(f"{len(targets)} targets with a website on {len(hosts)} hosts; reading the crawl cache ...", flush=True)
        pages = cached_pages_by_host(hosts, getattr(args, "crawl_cache", None))
    fetched_note = {}
    if args.fetch:
        import contact_lib as C
        C.CACHE = WORK / "http-cache"   # new pages are cached here; the crawl cache is only read
        for host in sorted(hosts):
            if host in args.skip or (not getattr(args, "always_fetch", False)
                                     and any(scan_page(b.decode("utf-8", "replace")) for _u, b in pages.get(host, []))):
                continue
            site = next(t["website"] for t in targets if host_of(t["website"]) == host).split()[0]
            home = site if "://" in site else "https://" + site
            robots, _state = C.robots_state(C.site_base(home))
            if not C.allowed(robots, home):
                fetched_note[host] = "robots.txt disallows the home page: not read"
                continue
            res = C.fetch(home, retries=1)
            if res.get("status") != 200 or not res.get("body"):
                fetched_note[host] = f"home page not readable ({res.get('status')} {res.get('error', '')})"
                continue
            pages[host].append((res.get("final_url") or home, res["body"]))
            body = res["body"].decode("utf-8", "replace")
            links = []
            for href in re.findall(r"href=[\"']([^\"'#]+)[\"']", body):
                url = urljoin(res.get("final_url") or home, href)
                path = urlsplit(url).path
                if (host_of(url) == host and CONTACT_LINK.search(path) and url not in links
                        and not re.search(r"\.(css|js|png|jpe?g|gif|svg|webp|ico|pdf|woff2?|xml)$", path, re.I)):
                    links.append(url)
            for url in links[: args.max_extra]:
                if not C.allowed(robots, url):
                    continue
                sub = C.fetch(url, retries=1)
                if sub.get("status") == 200 and sub.get("body"):
                    pages[host].append((sub.get("final_url") or url, sub["body"]))
            fetched_note[host] = f"read home page and {min(len(links), args.max_extra)} contact or location page(s)"
    out = []
    for t in targets:
        host = host_of(t["website"])
        found, mentions = [], []
        for url, body in pages.get(host, []):
            for h in scan_page(body.decode("utf-8", "replace")):
                found.append({"url": url, **h})
            if getattr(args, "mentions", False):
                mentions += [{"url": url, "text": m} for m in branch_mentions(body.decode("utf-8", "replace"))]
        row = {"db": t["db"], "seg": t["seg"], "id": t["id"], "name": t["name"], "prec": t["prec"], "website": t["website"],
               "pages_read": len(pages.get(host, [])), "fetch_note": fetched_note.get(host, ""), "hits": found}
        if getattr(args, "mentions", False):
            row["pages"] = [u for u, _b in pages.get(host, [])]
            row["branch_mentions"] = mentions
        out.append(row)
    (WORK / (getattr(args, "out", None) or "site_hits.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    with_pts = [o for o in out if any(h.get("in_box") for h in o["hits"])]
    print(f"targets with a coordinate in the map box on their own site: {len(with_pts)}; with any hit: {sum(1 for o in out if o['hits'])}")
    return 0


# ------------------------------------------------------------------ OpenStreetMap
OSM_QUERIES = {
    "amenity": f'[out:json][timeout:180];nwr["name"]["amenity"]({BBOX});out center tags;',
    "shop": f'[out:json][timeout:180];nwr["name"]["shop"]({BBOX});out center tags;',
    "brand": f'[out:json][timeout:180];nwr["brand"]({BBOX});out center tags;',
    "office": f'[out:json][timeout:180];(nwr["name"]["office"]({BBOX});nwr["name"]["craft"]({BBOX});nwr["name"]["industrial"]({BBOX});'
              f'nwr["name"]["man_made"="works"]({BBOX});nwr["name"]["landuse"="industrial"]({BBOX});nwr["name"]["company"]({BBOX}););out center tags;',
    "tourism": f'[out:json][timeout:180];(nwr["name"]["tourism"]({BBOX});nwr["name"]["leisure"]({BBOX});nwr["name"]["healthcare"]({BBOX});'
               f'nwr["name"]["club"]({BBOX}););out center tags;',
    "building": f'[out:json][timeout:180];nwr["name"]["building"]({BBOX});out center tags;',
}
GENERIC = {"the", "ltd", "limited", "co", "company", "t", "tz", "tanzania", "and", "plc", "of", "group", "international", "arusha", "moshi",
           "tours", "tour", "safaris", "safari", "travel", "travels", "hotel", "lodge", "centre", "center", "foundation", "organization",
           "organisation", "children", "home", "orphanage", "school", "bank", "inc", "e", "v", "trust", "services", "branch", "office",
           "africa", "african", "kilimanjaro", "adventures", "adventure", "expeditions", "camp", "camps", "&"}


def osm_elements(refresh: bool) -> list[dict]:
    import gov_lib as G
    cache = WORK / "overpass"
    cache.mkdir(parents=True, exist_ok=True)
    elements, seen, last = [], set(), 0.0
    for name, query in OSM_QUERIES.items():
        path = cache / f"{name}.json"
        if path.exists() and not refresh:
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            wait = last + 6.0 - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            print(f"Overpass: {name} ...", flush=True)
            try:
                body, endpoint = G.overpass(query)
            except SystemExit as exc:  # every mirror refused: record it and go on with the other queries
                print(f"  {name}: {exc}; skipped (re-run later)", flush=True)
                last = time.monotonic()
                continue
            last = time.monotonic()
            data = json.loads(body)
            if data.get("remark") and "error" in data["remark"].lower():
                print(f"  {name}: {data['remark'][:200]}")
                continue
            data["_endpoint"], data["_fetched"] = endpoint, time.strftime("%Y-%m-%d")
            path.write_text(json.dumps(data), encoding="utf-8")
            print(f"  {len(data.get('elements', []))} elements from {endpoint}", flush=True)
        for el in data.get("elements", []):
            key = (el["type"], el["id"])
            if key in seen:
                continue
            seen.add(key)
            lat = el.get("lat", (el.get("center") or {}).get("lat"))
            lon = el.get("lon", (el.get("center") or {}).get("lon"))
            if lat is None:
                continue
            elements.append({"osm": f"{el['type']}/{el['id']}", "lat": lat, "lon": lon, "tags": el.get("tags", {}), "fetched": data.get("_fetched", "")})
    return elements


def norm(name: str) -> list[str]:
    import unicodedata
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s).replace("&", " and ").replace("'", "")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()


def cmd_osm(args) -> int:
    elements = osm_elements(args.refresh)
    print(f"{len(elements)} named features")
    index = defaultdict(list)
    for el in elements:
        names = {el["tags"].get(k) for k in ("name", "name:en", "alt_name", "official_name", "brand", "operator", "short_name") if el["tags"].get(k)}
        for n in names:
            for tok in set(norm(n)) - GENERIC:
                if len(tok) >= 3:
                    index[tok].append((el, n))
    out = []
    for t in load_targets(args.scope, getattr(args, "targets_file", None)):
        toks = [x for x in norm(re.sub(r"\(.*?\)", "", t["name"])) if x not in GENERIC and len(x) >= 3]
        if not toks:
            continue
        cands = {}
        for el, n in index.get(toks[0], []) + [p for tok in toks[1:] for p in index.get(tok, [])]:
            ftoks = set(norm(n)) - GENERIC
            shared = set(toks) & ftoks
            if not shared:
                continue
            score = len(shared) / max(len(set(toks)), len(ftoks))
            exact = " ".join(norm(n)) == " ".join(norm(t["name"]))
            if score >= 0.5 or exact:
                k = el["osm"]
                if k not in cands or cands[k]["score"] < score:
                    cands[k] = {"osm": k, "name": n, "lat": el["lat"], "lon": el["lon"], "score": round(score, 2), "exact": exact,
                                "tags": {x: el["tags"][x] for x in el["tags"] if not x.startswith(("contact:", "phone", "email", "addr:postcode"))},
                                "fetched": el["fetched"]}
        if cands:
            best = sorted(cands.values(), key=lambda c: (-c["exact"], -c["score"]))[:6]
            out.append({"db": t["db"], "seg": t["seg"], "id": t["id"], "name": t["name"], "prec": t["prec"], "tier": t.get("tier"), "candidates": best})
    (WORK / (getattr(args, "out", None) or "osm_hits.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"targets with OpenStreetMap name candidates: {len(out)}")
    return 0


def cmd_pages(args) -> int:
    """Scan named pages (a lead's contact page found by hand, a directory profile) for map pins, plus codes, embed place text
    and Arusha-area mentions, through the same polite fetcher (robots.txt honoured, 1.5 s per site, blocks reported)."""
    import contact_lib as C
    C.CACHE = WORK / "http-cache"
    out = []
    for url in args.url:
        url = url if "://" in url else "https://" + url
        robots, _state = C.robots_state(C.site_base(url))
        if not C.allowed(robots, url):
            out.append({"url": url, "note": "robots.txt disallows this page: not read"})
            continue
        res = C.fetch(url, retries=1)
        if res.get("status") != 200 or not res.get("body"):
            out.append({"url": url, "note": f"not readable ({res.get('status')} {res.get('error', '')})"})
            continue
        body = res["body"].decode("utf-8", "replace")
        out.append({"url": res.get("final_url") or url, "fetched": time.strftime("%Y-%m-%d"), "hits": scan_page(body),
                    "branch_mentions": branch_mentions(body, 12)})
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------ OpenStreetMap by name, nationwide
LEGAL = {"the", "a", "and", "ltd", "limited", "co", "company", "plc", "inc", "e", "v", "t"}


def name_core(name: str) -> str:
    """The lead's name for a nationwide name regex: legal words dropped, the first two words kept (a single generic word
    such as 'Discover' would match thousands of features)."""
    toks = [x for x in norm(re.sub(r"\(.*?\)", "", name.split("/")[0])) if x not in LEGAL]
    return " ".join(toks[:2])


def cmd_osm_names(args) -> int:
    """Named OpenStreetMap features anywhere in Tanzania whose name contains a target's distinctive words, for leads whose
    office may lie outside the map box. Targets are batched into a few name-regex queries (one at a time, >= 6 s apart,
    [timeout:180], mirror fallback), cached in runtime/geocode/overpass-names/."""
    import gov_lib as G
    targets = load_targets(args.scope, getattr(args, "targets_file", None))
    cores = {}
    for t in targets:
        core = name_core(t["name"])
        if len(core) >= 4:
            cores.setdefault(core, []).append(t)
    cache = WORK / "overpass-names"
    cache.mkdir(parents=True, exist_ok=True)
    keys, elements, last = sorted(cores), [], 0.0
    for i in range(0, len(keys), args.batch):
        batch = keys[i:i + args.batch]
        rx = "|".join(k.replace(" ", ".{0,8}") for k in batch)
        query = (f'[out:json][timeout:180];area["ISO3166-1"="TZ"][admin_level=2]->.tz;'
                 f'nwr["name"~"{rx}",i](area.tz);out center tags;')
        path = cache / (hashlib.sha256(query.encode()).hexdigest()[:16] + ".json")
        if path.exists() and not args.refresh:
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            wait = last + 6.0 - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            print(f"Overpass names {i // args.batch + 1}: {len(batch)} names ...", flush=True)
            try:
                body, endpoint = G.overpass(query)
            except SystemExit as exc:
                print(f"  batch skipped: {exc}", flush=True)
                last = time.monotonic()
                continue
            last = time.monotonic()
            data = json.loads(body)
            if data.get("remark") and "error" in data["remark"].lower():
                print(f"  {data['remark'][:200]}")
                continue
            data["_endpoint"], data["_fetched"], data["_query"] = endpoint, time.strftime("%Y-%m-%d"), query
            path.write_text(json.dumps(data), encoding="utf-8")
            print(f"  {len(data.get('elements', []))} elements from {endpoint}", flush=True)
        for el in data.get("elements", []):
            lat = el.get("lat", (el.get("center") or {}).get("lat"))
            lon = el.get("lon", (el.get("center") or {}).get("lon"))
            if lat is not None:
                elements.append({"osm": f"{el['type']}/{el['id']}", "lat": lat, "lon": lon, "tags": el.get("tags", {}),
                                 "fetched": data.get("_fetched", ""), "endpoint": data.get("_endpoint", "")})
    out = []
    for core, ts in cores.items():
        cands = [{"osm": e["osm"], "name": e["tags"].get("name"), "lat": e["lat"], "lon": e["lon"], "in_box": in_box(e["lat"], e["lon"]),
                  "tags": {x: e["tags"][x] for x in e["tags"] if not x.startswith(("contact:", "phone", "email"))}, "fetched": e["fetched"],
                  "endpoint": e["endpoint"]}
                 for e in elements if re.search(core.replace(" ", ".{0,8}"), " ".join(norm(e["tags"].get("name", ""))))]
        cands.sort(key=lambda c: (not c["in_box"], c["name"] or ""))
        for t in ts:
            out.append({"db": t["db"], "id": t["id"], "name": t["name"], "core": core, "candidates": cands[:12]})
    (WORK / (getattr(args, "out", None) or "osm_name_hits.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"targets with nationwide OpenStreetMap name candidates: {sum(1 for o in out if o['candidates'])} of {len(out)}")
    return 0


# ------------------------------------------------------------------ Nominatim
STREETISH = re.compile(r"\b(road|rd|street|st|avenue|ave|drive|plot|house|tower|plaza|centre|center|building|estate|park|mall)\b", re.I)


def cmd_nominatim(args) -> int:
    cache = WORK / "nominatim"
    if getattr(args, "queries", None):   # reviewer-written queries: [{"id", "name", "query"}], e.g. an address read on the lead's own site
        targets = [{"db": "master", "seg": "emp", "prec": "none", **q} for q in json.loads(Path(args.queries).read_text(encoding="utf-8"))]
    else:
        targets = [t for t in load_targets(args.scope, getattr(args, "targets_file", None))
                   if STREETISH.search(str(t.get("address") or "")) and t["seg"] != "gov"]
    out = []
    for t in targets[: args.limit]:
        if t.get("query"):
            query = t["query"]
        else:
            parts = [p.strip() for p in re.split(r";|\bP\.?\s*O\.?\s*Box[^,;]*", str(t["address"]), flags=re.I) if p.strip()]
            query = next((p for p in parts if STREETISH.search(p)), parts[0] if parts else "")
        if not re.search(r"arusha|moshi|usa river|kilimanjaro|tanzania", query, re.I):
            query += ", Tanzania"
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({"q": query, "format": "jsonv2", "limit": 3, "countrycodes": "tz"})
        try:
            body = W.polite_request(url, retries=2, cache_dir=cache)
            res = json.loads(body)
        except Exception as exc:  # noqa: BLE001 - record and move on
            out.append({"id": t["id"], "name": t["name"], "query": query, "error": repr(exc)[:160]})
            continue
        hits = [{"lat": float(r["lat"]), "lon": float(r["lon"]), "display_name": r.get("display_name", ""), "type": f"{r.get('category')}/{r.get('type')}",
                 "osm": f"{r.get('osm_type')}/{r.get('osm_id')}", "in_box": in_box(float(r["lat"]), float(r["lon"]))}
                for r in res if tanzania(float(r["lat"]), float(r["lon"]))]
        out.append({"db": t["db"], "seg": t["seg"], "id": t["id"], "name": t["name"], "prec": t["prec"], "query": query, "url": url, "hits": hits})
    (WORK / (getattr(args, "out", None) or "nominatim_hits.json")).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} addresses looked up; {sum(1 for o in out if o.get('hits'))} with a result in Tanzania")
    return 0


# ------------------------------------------------------------------ point-level inventory, repository points, review, worklist
# Added 13 October 2026: a draft states a campus distance only from the organisation's own point (precision 'point' in the
# master, 'address' in the run databases), so every other lead is a geolocation target.
LOCATION_TOOLS = {"gmaps", "overpass", "nominatim", "places"}
RUN_POINT = "address"            # the run databases' name for a point (export_welfare_run.PRECISION, build_government_run)
PO_BOX = re.compile(r"\b(?:p\.?\s*o\.?\s*box|s\.?\s*l\.?\s*p\.?|postal|box)\s*\.?\s*\d+", re.I)


def ledger_location(tried, db: str, oid: str, name: str) -> tuple[list[dict], bool]:
    """The research ledger's location attempts for a lead (Google Maps, Overpass, Nominatim, Places, own-site map scans and any
    line whose target is 'location'), and whether its own website was crawled."""
    loc, crawled = [], False
    for e in tried.attempts(db, oid, name):
        pattern = e.get("query_pattern", "")
        if e["tool"] == "crawler":
            crawled = True
        if e["tool"] in LOCATION_TOOLS or e.get("target") == "location" or "map-embed" in pattern:
            loc.append({"id": e.get("id"), "date": e.get("date"), "tool": e["tool"], "pattern": pattern, "query": str(e.get("query", ""))[:200],
                        "outcome": e.get("outcome"), "found": str(e.get("found", ""))[:160], "source_file": e.get("source_file", "")})
    return loc, crawled


def cmd_inventory(args) -> int:
    """Every lead whose stored location is not a point: all master organisations with geocode_precision other than 'point', and the
    welfare and government run organisations with an outreach plan whose run precision is not 'address' (their drafts state distances).
    Each with its precision, coordinates, address, locality, website and what the research ledger records for its location.
    Writes runtime/geocode/inventory.json, a targets file the other collectors take with --targets-file."""
    sys.path.insert(0, str(ROOT / "scripts" / "research"))
    import build_lead_map as B
    import ledger as LG
    tried = LG.Tried(as_of=args.as_of)
    out = []

    def row(db, seg, r, stored, extra=None):
        lat, lon = B.num(r["latitude"]), B.num(r["longitude"])
        loc, crawled = ledger_location(tried, db, r["organisation_id"], r["name"])
        prec = "none" if lat is None or lon is None else ("outside" if not in_box(lat, lon) else "estimated")
        return {"db": db, "seg": seg, "id": r["organisation_id"], "name": r["name"], "stored_precision": stored, "prec": prec,
                "how": stored, "lat": lat, "lon": lon, "campus": r["campus"] or "", "distance_km": r["distance_km"],
                "address": r["address"] or "", "locality": r["locality"] or "", "website": (r["website"] or "").strip(),
                "segment": r["segment"] or "", "po_box_only": bool(PO_BOX.search(r["address"] or "")) and not STREETISH.search(
                    PO_BOX.sub(" ", r["address"] or "")), "ledger_location": loc, "site_crawled": crawled, **(extra or {})}

    m = B.ro(B.MASTER)
    plans = {r[0]: r[1] for r in m.execute("SELECT organisation_id, COUNT(*) FROM outreach_plans WHERE selection='Candidate for review' "
                                           "GROUP BY organisation_id")}
    for r in m.execute("SELECT * FROM organisations WHERE COALESCE(geocode_precision, '') != 'point' ORDER BY name"):
        seg = "int" if str(r["segment"] or "").startswith("Introducer") else "emp"
        out.append(row("master", seg, r, r["geocode_precision"] or "", {"plans": plans.get(r["organisation_id"], 0), "osm_id": r["osm_id"] or "",
                                                                       "source_url": r["source_url"] or "", "verification": r["verification"] or ""}))
    w = B.ro(ROOT / "outputs" / "runs" / B.WELFARE_RUN / "lead-database.sqlite")
    for r in w.execute("SELECT * FROM organisations WHERE COALESCE(geocode_precision, '') != ? AND organisation_id IN "
                       "(SELECT organisation_id FROM outreach_plans) ORDER BY name", (RUN_POINT,)):
        out.append(row("welfare", "wel", r, r["geocode_precision"] or "", {"key": r["name"]}))
    g = B.ro(ROOT / "outputs" / "runs" / B.GOVERNMENT_RUN / "lead-database.sqlite")
    for r in g.execute("SELECT o.*, gp.office_level, gp.council_name, gp.admin_unit_name, gp.record_key FROM organisations o "
                       "JOIN government_office_profiles gp USING(organisation_id) WHERE COALESCE(o.geocode_precision, '') != ? ORDER BY o.name",
                       (RUN_POINT,)):
        key = f"{r['council_name']}|{r['admin_unit_name']}" if r["office_level"] == "ward" else r["record_key"]
        out.append(row("government", "gov", r, r["geocode_precision"] or "", {"level": r["office_level"], "council": r["council_name"],
                                                                                "unit": r["admin_unit_name"], "key": key}))
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "inventory.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(json.dumps({f"{k[0]} {k[1] or '(blank)'}": v for k, v in sorted(Counter((x["db"], x["stored_precision"]) for x in out).items())}, indent=1))
    print(f"{len(out)} leads not at point level; {sum(1 for x in out if x['ledger_location'])} with a location attempt in the ledger")
    return 0


LEGAL_WORDS = {"ltd", "limited", "co", "company", "plc", "inc", "t", "tz", "the", "llc", "e", "v"}


def name_key(name: str) -> str:
    """A strict comparison key: lower case, accents and punctuation dropped, '&' read as 'and', legal suffixes and bracketed notes
    dropped. Two names match only when their keys are equal."""
    return " ".join(x for x in norm(re.sub(r"\(.*?\)", " ", str(name or "").split(" / ")[0])) if x not in LEGAL_WORDS)


def repo_osm_features() -> list[dict]:
    """Named OpenStreetMap features already in the repository: the gap census extracts (data/raw/gap-census/osm_*_<date>.json),
    the OSM contact pulls (data/raw/contact-research/osm_contacts_*.json), the government office points, the basemap's points
    of interest (data/reference/maps/arusha-catchment-basemap.geojson) and this collector's Overpass cache (runtime/geocode/overpass/)."""
    feats, seen = [], set()

    def add(osm, lat, lon, tags, src, fetched):
        if not osm or lat is None or (osm in seen):
            return
        seen.add(osm)
        feats.append({"osm": osm, "lat": float(lat), "lon": float(lon), "tags": tags, "file": src, "fetched": fetched})

    for p in sorted((ROOT / "data" / "raw" / "gap-census").glob("osm_*_*.json")) + sorted((ROOT / "data" / "raw" / "contact-research").glob("osm_contacts_*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for el in d.get("elements", []):
            osm = el.get("osm_id") or (f"{el['type']}/{el['id']}" if "type" in el else "")
            lat = el.get("lat", (el.get("center") or {}).get("lat"))
            lon = el.get("lon", (el.get("center") or {}).get("lon"))
            add(osm, lat, lon, el.get("tags", {}), p.relative_to(ROOT).as_posix(), d.get("retrieved", ""))
    gp = ROOT / "data" / "raw" / "gap-census" / "government_office_points_2026-10-11.json"
    if gp.exists():
        d = json.loads(gp.read_text(encoding="utf-8"))
        for o in d.get("offices", []):
            add(o.get("osm_id"), o.get("latitude"), o.get("longitude"), {"name": o.get("name") or "", "name:sw": o.get("name_sw") or "",
                                                                          "office": "government"}, gp.relative_to(ROOT).as_posix(), d.get("retrieved", ""))
    basemap = ROOT / "data" / "reference" / "maps" / "arusha-catchment-basemap.geojson"
    d = json.loads(basemap.read_text(encoding="utf-8"))
    for f in d["features"]:
        p = f["properties"]
        if p.get("layer") == "poi" and p.get("osm"):
            add(p["osm"], f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0], {"name": p["name"], "kind": p.get("kind", "")},
                basemap.relative_to(ROOT).as_posix(), "2026-10-11")
    for p in sorted((WORK / "overpass").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for el in d.get("elements", []):
            lat = el.get("lat", (el.get("center") or {}).get("lat"))
            lon = el.get("lon", (el.get("center") or {}).get("lon"))
            add(f"{el['type']}/{el['id']}", lat, lon, el.get("tags", {}), f"Overpass ({d.get('_endpoint', '')})", d.get("_fetched", ""))
    return feats


def reviewed_points() -> dict:
    """Points a reviewer already accepted in the repository, by (db, organisation id): placed point-precision lines in
    data/raw/geocode-research/*.jsonl and the coordinator's accepted Google Maps listings (data/raw/gap-census/google_maps_enrich_*.jsonl)."""
    found = defaultdict(list)
    for p in sorted((ROOT / "data" / "raw" / "geocode-research").glob("*.jsonl")):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("status", "placed") == "placed" and r.get("precision") == "point" and r.get("latitude") not in (None, ""):
                found[(r.get("db") or "master", r.get("organisation_id") or "")].append(
                    {"file": p.relative_to(ROOT).as_posix(), "line": n, "lat": float(r["latitude"]), "lon": float(r["longitude"]),
                     "source_type": r.get("source_type", ""), "source_url": r.get("source_url", ""), "fetched_on": r.get("fetched_on", ""),
                     "as_found": r.get("as_found", ""), "basis": r.get("basis", ""), "name_found": r.get("listing_name") or r.get("google_name") or ""})
    for p in sorted((ROOT / "data" / "raw" / "gap-census").glob("google_maps_enrich_*.jsonl")):
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("verdict") == "accept" and r.get("latitude") not in (None, "") and r.get("organisation_id"):
                found[("master", r["organisation_id"])].append(
                    {"file": p.relative_to(ROOT).as_posix(), "line": n, "lat": float(r["latitude"]), "lon": float(r["longitude"]),
                     "source_type": "Google Maps listing", "source_url": r.get("source_url", ""), "fetched_on": r.get("fetched_on", ""),
                     "as_found": f"{r.get('listing_name', '')}; {r.get('category', '')}; {r.get('address', '')}; {r['latitude']}, {r['longitude']}",
                     "basis": f"The coordinator's accepted Google Maps listing '{r.get('listing_name', '')}' ({p.name} line {n}, verdict accept).",
                     "name_found": r.get("listing_name", "")})
    return found


def cmd_repo(args) -> int:
    """For each inventory lead (runtime/geocode/inventory.json): reviewed points already in the repository for the same organisation,
    and OpenStreetMap features in the repository's extracts whose name key equals the lead's. No network. Writes
    runtime/geocode/repo_hits.json."""
    inventory = json.loads((WORK / "inventory.json").read_text(encoding="utf-8"))
    feats = repo_osm_features()
    by_key = defaultdict(list)
    for f in feats:
        for k in ("name", "name:en", "name:sw", "alt_name", "official_name", "short_name", "brand", "operator"):
            if f["tags"].get(k) and len(name_key(f["tags"][k])) >= 4:
                by_key[name_key(f["tags"][k])].append({**f, "matched_tag": k, "matched_name": f["tags"][k]})
    reviewed = reviewed_points()
    out = []
    for t in inventory:
        keys = {name_key(t["name"])}
        if t["db"] == "government" and t.get("unit"):  # 'Ofisi ya Kata ya <ward>', '<ward> ward office'; a village office only as a village office
            words = {"ward": ("ofisi ya kata ya", "ofisi ya kata", "ward office", "ofisi ya mtendaji kata"),
                     "village": ("ofisi ya kijiji cha", "ofisi ya kijiji", "office ya kijiji", "village office", "village government office")}
            for word in words.get(t.get("level"), ()):
                keys.add(name_key(f"{word} {t['unit']}"))
                keys.add(name_key(f"{t['unit']} {word}"))
        osm = [c for k in keys if len(k) >= 4 for c in by_key.get(k, [])]
        uniq = {c["osm"]: c for c in osm}
        rev = reviewed.get((t["db"], t["id"]), [])
        if osm or rev:
            out.append({"db": t["db"], "id": t["id"], "name": t["name"], "stored_precision": t["stored_precision"], "osm": list(uniq.values()),
                        "reviewed": rev})
    (WORK / "repo_hits.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(feats)} named OpenStreetMap features in the repository; {len(out)} of {len(inventory)} leads with a candidate "
          f"({sum(1 for o in out if o['reviewed'])} with a reviewed point, {sum(1 for o in out if o['osm'])} with an exact-name feature)")
    return 0


PREVIOUS_CAMPUSES = {"Usa River": (-3.3645, 36.8632), "Arusha City": (-3.3528, 36.6613), "Ilboru": (-3.3465, 36.6922),
                     "Kijenge": (-3.3837, 36.7100), "Boma Ngombe": (-3.3342, 37.1383)}  # recompute_campus_distances.PREVIOUS
ADDR_TAGS = ("addr:city", "addr:place", "addr:suburb", "addr:district", "addr:hamlet", "addr:village", "addr:street", "is_in", "addr:full")
LOCALITY_KM, TOWN_KM = 5.0, 12.0


def hav(a, b, c, d) -> float:
    import math
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin(math.radians(c - a) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


TOWNS = {"moshi": (-3.3349, 37.3404), "arusha": (-3.3696, 36.6880), "usa river": (-3.3680, 36.8560)}


NOT_PLACES_IN_NAMES = r"\b(?:arusha|moshi|meru|kilimanjaro|mahakama|mount|mt)\b"   # a mountain, a region or a word, not where the office is


def guard(t: dict, lat: float, lon: float, loc, strong: bool = False) -> str:
    """Why a same-name point cannot be this lead's ('' when nothing contradicts it): it lies more than 12 km from the record's own
    estimated point; the record's locality or street address (never a P.O. box town) names Moshi but not Arusha and the point is more
    than 15 km from Moshi, or the reverse; or, unless the point already has strong evidence (it reproduces the stored import distance
    or its address tags agree), the organisation's name carries a place (Tengeru, Njiro, Machame ...) more than 8 km from the point."""
    if t.get("lat") is not None and t.get("lon") is not None and t["prec"] != "outside":
        km = hav(lat, lon, t["lat"], t["lon"])
        if km > TOWN_KM:
            return f"{km:.1f} km from the record's own estimated point"
    text = f" {t.get('locality') or ''} {'' if t.get('po_box_only') else t.get('address') or ''} ".lower()
    if "moshi" in text and "arusha" not in text and hav(lat, lon, *TOWNS["moshi"]) > 15:
        return "the record places it in Moshi; the point is not"
    if "arusha" in text and not re.search(r"moshi|kilimanjaro|\bhai\b|usa.?river|tengeru|karatu|\bkia\b|airport", text) and lon > 36.95:
        return "the record places it in Arusha; the point is in Kilimanjaro"
    in_name = None if strong else loc.text(re.sub(NOT_PLACES_IN_NAMES, " ", t["name"], flags=re.I), specific_only=True)
    if in_name and hav(lat, lon, in_name[0], in_name[1]) > 8:
        return f"the name names {in_name[2]}, {hav(lat, lon, in_name[0], in_name[1]):.1f} km from the point"
    return ""


def locality_evidence(t: dict, lat: float, lon: float, tags: dict, loc, campuses: dict) -> tuple[str, str]:
    """(why this point lies where the lead's own record says it is, confidence); ('', '') when nothing agrees. A clear name match is
    accepted only with one of: the record's locality or address names a place within 5 km (12 km for a town or city centre); the
    feature's address tags name a place the record names; the point reproduces the record's stored distance to its stored campus
    (the importer's own point); the record's estimated point lies within 5 km (12 km for a town or city estimate); or, for a record
    imported from OpenStreetMap, the point has the stored nearest campus and lies within 1.5 km of the stored distance."""
    text = f"{t.get('locality') or ''} {t.get('address') or ''} {t.get('unit') or ''}"
    found = loc.text(t.get("unit") or "", t.get("locality") or "", PO_BOX.sub(" ", t.get("address") or ""))
    if found:
        km = hav(lat, lon, found[0], found[1])
        town = found[3] != "locality" or found[2].lower() in ("usa river", "moshi", "hai", "tengeru", "arusha city", "kilimanjaro")
        limit = TOWN_KM if town else LOCALITY_KM
        if km <= limit:
            return (f"{km:.1f} km from {found[2]} ({'town' if town and found[3] == 'locality' else found[3]}), which the record's "
                    "locality or address names", "medium" if town else "high")
    words = {w for w in norm(text) if len(w) >= 4} - GENERIC - {"road", "street", "plot", "block", "house", "box", "tanzania", "region"}
    for k in ADDR_TAGS:
        v = str(tags.get(k) or "")
        shared = words & set(norm(v))
        if shared:
            return f"the feature's {k} '{v}' names {', '.join(sorted(shared))}, as the record does", "high"
    try:
        stored = float(t.get("distance_km"))
    except (TypeError, ValueError):
        stored = None
    from recompute_campus_distances import campus_key  # noqa: E402  (scripts/master on the path)
    camp = campus_key(t.get("campus") or "")
    if stored is not None and camp:
        for label, pts in (("previous", PREVIOUS_CAMPUSES), ("current", campuses)):
            if camp in pts and abs(round(hav(lat, lon, *pts[camp]), 1) - stored) <= 0.2:
                return f"reproduces the stored {stored} km to {camp} ({label} campus points): the point the record was imported from", "high"
    if t.get("lat") is not None and t.get("lon") is not None and t["prec"] != "outside":
        km = hav(lat, lon, t["lat"], t["lon"])
        limit = TOWN_KM if t.get("stored_precision") in ("city", "town", "estimated") else LOCALITY_KM
        if km <= limit:
            return f"{km:.1f} km from the record's estimated point ({t.get('stored_precision') or 'unstated precision'})", (
                "medium" if limit == TOWN_KM else "high")
    imported = "openstreetmap.org" in str(t.get("source_url") or "") or str(t.get("verification") or "").startswith("OSM place")
    if imported and stored is not None and camp in campuses:
        dists = {c: hav(lat, lon, *xy) for c, xy in campuses.items()}
        near = min(dists, key=dists.get)
        if near == camp and abs(dists[camp] - stored) <= 1.5:
            return (f"the record was imported from OpenStreetMap ({t.get('verification') or t.get('source_url')}); the only feature of this name "
                    f"in the catchment has the stored nearest campus {camp}, {dists[camp]:.1f} km against the stored {stored} km"), "medium"
    return "", ""


def government_evidence(t: dict, c: dict, gov: dict) -> tuple[str, str]:
    """A ward or village office: the feature's address tags or name give the same ward (or village), it lies inside the council's
    OpenStreetMap district, and within 10 km of the run's ward (or village) reference point. ('', reason) when it fails."""
    import gov_lib as G
    tags = c.get("tags") or {}
    unit = G.squash(t.get("unit") or "")
    ward_tag = t.get("level") == "ward" and unit == G.squash(tags.get("addr:ward") or "")
    named = bool(unit) and (ward_tag or unit in G.squash(c["name"]))
    if not named:
        return "", "the feature's name and addr:ward do not give this unit"
    where = G.district_of(c["lat"], c["lon"], gov["districts"])
    if where not in gov["zone"](t.get("council") or ""):
        return "", f"the feature lies in the {where or 'no'} district, outside {t.get('council')}"
    if t.get("lat") is not None:
        km = hav(c["lat"], c["lon"], t["lat"], t["lon"])
        if km > 10:
            return "", f"{km:.1f} km from the run's reference point for the {t.get('level')}"
    return (f"the feature is the {t.get('level')} office of {t.get('unit')} (addr:ward '{tags.get('addr:ward', '')}', source "
            f"'{tags.get('source', '')}'), inside the council's district ({where})"), "high"


def cmd_review(args) -> int:
    """Proposes a verdict for every candidate the collectors found for the inventory (repo_hits.json, osm_hits.json, site_hits.json,
    nominatim_hits.json, whichever exist): accept only a clear name match (equal name keys, or the organisation's own website)
    with a matching locality (locality_evidence) and no second feature of the same name elsewhere; a reviewed point already in the
    repository is accepted as reviewed. Writes runtime/geocode/review.json for a person to check; the accepted lines then go to
    data/raw/geocode-research/geocodes_<label>_<date>.jsonl (--write) for scripts/master/apply_geocodes.py."""
    sys.path.insert(0, str(ROOT / "scripts" / "master"))
    import build_lead_map as B
    inventory = {(t["db"], t["id"]): t for t in json.loads((WORK / "inventory.json").read_text(encoding="utf-8"))}
    loc = B.Locator(json.loads(B.BASEMAP.read_text(encoding="utf-8")))
    m = B.ro(B.MASTER)
    from recompute_campus_distances import campus_key
    campuses = {campus_key(r["name"]): (r["latitude"], r["longitude"]) for r in m.execute("SELECT name, latitude, longitude FROM campuses")}
    today = args.date
    cands = defaultdict(list)

    def read(name):
        p = WORK / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    for h in read("repo_hits.json"):
        for r in h["reviewed"]:
            cands[(h["db"], h["id"])].append({"kind": "reviewed", "lat": r["lat"], "lon": r["lon"], "name": r["name_found"] or h["name"],
                                              "source_type": r["source_type"], "source_url": r["source_url"], "fetched_on": r["fetched_on"],
                                              "as_found": r["as_found"], "basis_in": r["basis"], "ref": f"{r['file']} line {r['line']}"})
        for f in h["osm"]:
            cands[(h["db"], h["id"])].append({"kind": "osm", "osm": f["osm"], "lat": f["lat"], "lon": f["lon"], "name": f["matched_name"],
                                              "tags": f["tags"], "file": f["file"], "fetched_on": f["fetched"] or today})
    for h in read("osm_hits.json"):  # the Overpass box collector: exact names only
        for c in h["candidates"]:
            if c.get("exact") or name_key(c["name"]) == name_key(h["name"]):
                cands[(h["db"], h["id"])].append({"kind": "osm", "osm": c["osm"], "lat": c["lat"], "lon": c["lon"], "name": c["name"],
                                                  "tags": c["tags"], "file": "Overpass (runtime/geocode/overpass)", "fetched_on": c.get("fetched") or today})
    platform = defaultdict(set)   # a coordinate several unrelated sites share is a theme or platform default, not a pin
    sites = read("site_hits.json")
    for h in sites:
        for x in h["hits"]:
            if x.get("lat") is not None:
                platform[(round(x["lat"], 4), round(x["lon"], 4))].add(host_of(h["website"]))
    # A town's centre, or a listing platform's default for it (coverage log of 2026-10-11), is not a pin either.
    defaults = list(TOWNS.values()) + [(-3.3869, 36.683), (-3.3713, 36.8583), (-3.3667, 36.6833)]
    for h in sites:
        pts = {(round(x["lat"], 5), round(x["lon"], 5)): x for x in h["hits"] if x.get("lat") is not None and x.get("in_box")
               and len(platform[(round(x["lat"], 4), round(x["lon"], 4))]) == 1
               and all(hav(x["lat"], x["lon"], *d) > 0.25 for d in defaults)}
        for x in pts.values():
            cands[(h["db"], h["id"])].append({"kind": "site", "lat": x["lat"], "lon": x["lon"], "name": h["name"], "how": x["how"],
                                              "url": x["url"], "as_found": x["as_found"], "fetched_on": today, "n_points": len(pts)})
    for h in read("nominatim_hits.json"):
        for x in h.get("hits", []):
            if x.get("in_box") and not re.match(r"(highway|place|boundary|landuse)/", x["type"]):
                cands[(h["db"], h["id"])].append({"kind": "nominatim", "lat": x["lat"], "lon": x["lon"], "name": x["display_name"].split(",")[0],
                                                  "osm": x["osm"], "display": x["display_name"], "url": h["url"], "type": x["type"],
                                                  "fetched_on": today, "query": h["query"]})
    # A master record imported from an OpenStreetMap feature, holding that feature's coordinates and id but no precision: its own point.
    for t in inventory.values():
        if (t["db"] == "master" and t.get("osm_id") and t["lat"] is not None and t["prec"] == "estimated" and not t["stored_precision"]
                and t["osm_id"] in str(t.get("source_url") or "")):
            cands[(t["db"], t["id"])].append({"kind": "own_osm", "osm": t["osm_id"], "lat": t["lat"], "lon": t["lon"], "name": t["name"],
                                              "fetched_on": today})
    gov = None
    if any(t["db"] == "government" for t in inventory.values()):
        sys.path.insert(0, str(ROOT / "scripts" / "government"))
        import build_government_run as BG
        import gov_lib as G
        cfg = G.load_config(B.GOVERNMENT_RUN)
        gov = {"districts": G.load_districts(cfg["paths"]["raw"], cfg["research_date"]), "zone": BG.zone_function(cfg)}
    out = []
    for key, cs in cands.items():
        t = inventory.get(key)
        if not t:
            continue
        decisions = []
        for c in cs:
            why_not, evidence, conf = "", "", "high"
            if c["kind"] == "reviewed":
                evidence = f"reviewed before: {c['ref']}"
            elif c["kind"] == "own_osm":
                evidence = (f"the record was imported from OpenStreetMap {c['osm']} ({t.get('source_url')}) and holds that feature's "
                            "coordinates; only its precision was never recorded")
            else:
                if c["kind"] in ("osm", "nominatim") and name_key(c["name"]) != name_key(t["name"]) and not (
                        t["db"] == "government" and t.get("unit") and name_key(t["unit"]) in name_key(c["name"])):
                    why_not = f"name differs ('{c['name']}')"
                is_office = t["db"] == "government" and t.get("level") in ("ward", "village")
                same = [o for o in cs if o is not c and o["kind"] == c["kind"] and hav(o["lat"], o["lon"], c["lat"], c["lon"]) > 0.5
                        and (not is_office or government_evidence(t, o, gov)[0])]   # an office: only same-name offices in the same council count
                if not why_not and is_office:
                    evidence, fail = government_evidence(t, c, gov)
                    why_not = "" if evidence else fail
                if not why_not and same:
                    why_not = f"{len(same)} other {c['kind']} point(s) of the same name more than 0.5 km away (a chain or a duplicate)"
                if not why_not and c["kind"] == "site" and c.get("n_points", 1) > 1:
                    why_not = f"the site publishes {c['n_points']} different points (branches?)"
                if not why_not and not evidence:
                    evidence, conf = locality_evidence(t, c["lat"], c["lon"], c.get("tags") or {}, loc, campuses)
                    strong = evidence.startswith(("reproduces", "the feature's"))
                    why_not = guard(t, c["lat"], c["lon"], loc, strong) or (
                        "" if evidence else "no locality evidence: the point does not agree with the record's locality, address or stored distance")
            decisions.append({**c, "verdict": "reject" if why_not.startswith("name differs") else ("accept" if not why_not else "review"),
                              "why": why_not or evidence, "confidence": conf if not why_not else ""})
        accepted = [d for d in decisions if d["verdict"] == "accept"]
        reviewed = [d for d in accepted if d["kind"] in ("reviewed", "own_osm")]
        if reviewed:  # a reviewed or own point wins; a same-name point elsewhere is left for review
            for d in accepted:
                if d not in reviewed and hav(d["lat"], d["lon"], reviewed[0]["lat"], reviewed[0]["lon"]) > 0.5:
                    d["verdict"], d["why"] = "review", f"{hav(d['lat'], d['lon'], reviewed[0]['lat'], reviewed[0]['lon']):.1f} km from the reviewed point"
        else:
            spread = max((hav(a["lat"], a["lon"], b["lat"], b["lon"]) for a in accepted for b in accepted), default=0)
            if spread > 0.5:
                for d in accepted:
                    d["verdict"], d["why"] = "review", f"accepted candidates disagree by {spread:.1f} km"
        out.append({"db": t["db"], "id": t["id"], "name": t["name"], "stored_precision": t["stored_precision"], "locality": t["locality"],
                    "address": t["address"], "campus": t["campus"], "distance_km": t["distance_km"], "lat": t["lat"], "lon": t["lon"],
                    "key": t.get("key", ""), "candidates": decisions})
    (WORK / "review.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    best = Counter()
    for o in out:
        vs = {d["verdict"] for d in o["candidates"]}
        best[(o["db"], "accept" if "accept" in vs else "review" if "review" in vs else "reject")] += 1
    print(json.dumps({f"{k[0]} {k[1]}": v for k, v in sorted(best.items())}, indent=1))
    if args.write:
        write_accepted(out, Path(args.write), today)
    return 0


SOURCE_LABEL = {"reviewed": None, "osm": "OpenStreetMap", "site": "own site embed", "nominatim": "Nominatim"}
CONFIDENCE = {"reviewed": "high", "own_osm": "high", "osm": "high", "site": "high", "nominatim": "medium"}


def write_accepted(review: list[dict], path: Path, today: str) -> None:
    """One geocode-research line per lead with an accepted candidate (the first accepted, by kind: reviewed, own site, OpenStreetMap,
    Nominatim), in apply_geocodes.py's format plus geocode_source and confidence. A master lead that already holds coordinates gets
    a correction line (replace: true, with the stored point it replaces) for apply_geocodes.py --replace."""
    order = {"reviewed": 0, "own_osm": 1, "site": 2, "osm": 3, "nominatim": 4}
    lines = []
    for o in review:
        acc = sorted((d for d in o["candidates"] if d["verdict"] == "accept"), key=lambda d: order[d["kind"]])
        if not acc:
            continue
        d = acc[0]
        if d["kind"] == "reviewed":
            source_type, url, as_found = d["source_type"], d["source_url"], d["as_found"]
            basis = f"{d['basis_in']} Reviewed before ({d['ref']})."
        elif d["kind"] == "own_osm":
            source_type, url = "OpenStreetMap", f"https://www.openstreetmap.org/{d['osm']}"
            as_found = f"{d['osm']} at {d['lat']}, {d['lon']} (the record's own import point)"
            basis = f"{d['why'][0].upper()}{d['why'][1:]}."
        elif d["kind"] == "osm":
            source_type, url = "OpenStreetMap", f"https://www.openstreetmap.org/{d['osm']}"
            tags = {k: v for k, v in (d.get("tags") or {}).items() if not k.startswith(("contact:", "phone", "email", "addr:postcode"))}
            as_found = f"{d['osm']} at {d['lat']}, {d['lon']}; tags {json.dumps(tags, ensure_ascii=False)[:300]} (in {d['file']})"
            basis = f"OpenStreetMap feature with the same name ('{d['name']}'); {d['why']}."
        elif d["kind"] == "site":
            source_type, url, as_found = "own site embed", d["url"], d["as_found"]
            basis = f"The organisation's own website publishes this map point ({d['how']}); {d['why']}."
        else:
            source_type, url, as_found = "Nominatim", d["url"], f"{d['display']} ({d['type']}, {d['osm']}) at {d['lat']}, {d['lon']}"
            basis = f"Nominatim result for the record's street address '{d['query']}', with the same name; {d['why']}."
        as_found = re.sub(r"\+?\(?255\)?[\d\s-]{8,}\d", "[phone]", as_found)   # the excerpt locates the point; it never carries a number
        line = {"db": o["db"], "organisation_id": o["id"], "organisation_name": o["name"], "key": o["key"] if o["db"] != "master" else "",
                "status": "placed", "latitude": round(d["lat"], 7), "longitude": round(d["lon"], 7), "precision": "point",
                "source_type": source_type, "source_url": url, "fetched_on": d.get("fetched_on") or today, "as_found": as_found, "basis": basis,
                "geocode_source": f"{source_type}: {url}", "confidence": d.get("confidence") or CONFIDENCE.get(d["kind"], "medium")}
        if d.get("osm"):
            line["osm_id"] = d["osm"]
        if o["db"] == "master" and o["lat"] is not None:
            import apply_geocodes as AG
            m = sqlite3_ro(AG.MASTER)
            org = m.execute("SELECT * FROM organisations WHERE organisation_id=?", (o["id"],)).fetchone()
            source = AG.stored_source(m, org)
            line.update({"replace": True, "old_latitude": o["lat"], "old_longitude": o["lon"], "old_precision": o["stored_precision"],
                         "old_location_source": source or AG.NO_SOURCE, "km_moved": round(hav(o["lat"], o["lon"], d["lat"], d["lon"]), 1)})
            campuses = {r["name"]: (r["latitude"], r["longitude"]) for r in m.execute("SELECT name, latitude, longitude FROM campuses")}
            km = min(hav(d["lat"], d["lon"], *xy) for xy in campuses.values())
            try:
                before = float(o["distance_km"])
            except (TypeError, ValueError):
                before = None
            if before is not None and before <= 25 < km:
                line["beyond_catchment"] = (f"Kept and labelled under the user's instruction of {today} (geolocate, keep outside-catchment "
                                            f"leads labelled): {km:.1f} km from the nearest campus at its own point.")
        lines.append(line)
    fill = [x for x in lines if not x.get("replace")]
    repl = [x for x in lines if x.get("replace")]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in fill), encoding="utf-8")
    cpath = path.with_name(path.name.replace("geocodes_", "geocodes_corrections_", 1))
    cpath.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in repl), encoding="utf-8")
    print(f"{len(fill)} accepted lines -> {path}; {len(repl)} corrections of stored estimates -> {cpath} (apply_geocodes.py --replace)")


def sqlite3_ro(path: Path):
    import sqlite3
    con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def cmd_worklist(args) -> int:
    """The Google Maps worklist for the coordinator's browser (workers never use Google Maps): every inventory lead still not at
    point level, with its locality, address, website, a suggested search and the ledger's earlier Google Maps attempts. A lead the
    ledger shows was already looked up on Google Maps with no result is listed separately (it is not looked up again)."""
    inventory = json.loads(Path(args.inventory or WORK / "inventory.json").read_text(encoding="utf-8"))
    placed = set()
    for p in args.placed or []:
        for line in Path(p).read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("status") == "placed" and r.get("precision") == "point":
                    placed.add((r.get("db") or "master", r.get("organisation_id")))
    todo, skipped = [], []
    for t in inventory:
        if (t["db"], t["id"]) in placed:
            continue
        gm = [a for a in t["ledger_location"] if a["tool"] == "gmaps"]
        town = next((x for x in ("Usa River", "Moshi", "Arusha", "Hai", "Boma Ng'ombe", "Tengeru", "Karatu", "Mererani")
                     if x.lower() in f"{t['locality']} {t['address']}".lower()), "Arusha")
        place = t.get("unit") if t["db"] == "government" else ""
        query = f"{t['name']} {place or town}".strip() if t["db"] != "government" else f"{t['name']} {t.get('council') or ''}".strip()
        row = {"db": t["db"], "id": t["id"], "name": t["name"], "stored_precision": t["stored_precision"], "locality": t["locality"],
               "address": t["address"], "website": t["website"], "segment": t["segment"], "campus": t["campus"], "distance_km": t["distance_km"],
               "po_box_only": t["po_box_only"], "plans": t.get("plans", ""), "query": query, "prior_gmaps": [{k: a[k] for k in ("date", "query", "outcome", "found", "source_file")}
                                                                                 for a in gm]}
        if t["db"] == "government":
            row.update({"level": t.get("level"), "council": t.get("council"), "unit": t.get("unit")})
        if gm and all(a["outcome"] == "nothing" for a in gm):
            skipped.append(row)
        else:
            todo.append(row)
    # Leads whose drafts would state a distance first: master organisations with a plan for review, then the run offices and
    # organisations, nearest stored campus distance first; master records without a plan last.
    def km(r):
        try:
            return float(r["distance_km"])
        except (TypeError, ValueError):
            return 999.0
    todo.sort(key=lambda r: (r["db"] == "master" and not r.get("plans"), {"master": 0, "government": 1, "welfare": 2}[r["db"]], km(r)))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in todo), encoding="utf-8")
    skip = out.with_name(out.stem + "_skipped_no_result.jsonl")
    skip.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in skipped), encoding="utf-8")
    from collections import Counter
    print(f"worklist {len(todo)} ({dict(Counter(r['db'] for r in todo))}) -> {out}; already looked up with no result {len(skipped)} -> {skip}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("targets")
    inv = sub.add_parser("inventory", help="every lead not at point level, with the ledger's location attempts (runtime/geocode/inventory.json)")
    inv.add_argument("--as-of", default=None, help="the ledger's plan date (default today)")
    sub.add_parser("repo", help="reviewed points and exact-name OpenStreetMap features already in the repository (no network)")
    rv = sub.add_parser("review", help="propose accept / review / reject for every candidate (runtime/geocode/review.json)")
    rv.add_argument("--date", default=time.strftime("%Y-%m-%d"))
    rv.add_argument("--write", help="also write the accepted lines to this geocode-research file (check review.json first)")
    wl = sub.add_parser("worklist", help="the Google Maps worklist for the coordinator's browser")
    wl.add_argument("--inventory", type=Path)
    wl.add_argument("--placed", nargs="*", type=Path, help="geocode files whose placed point lines are taken off the list")
    wl.add_argument("--out", type=Path, required=True)
    pg = sub.add_parser("pages", help="scan named pages for map pins and Arusha-area mentions (prints JSON)")
    pg.add_argument("url", nargs="+")
    for name in ("sites", "osm", "osm-names", "nominatim"):
        p = sub.add_parser(name)
        p.add_argument("--scope", choices=["unplaced", "estimated", "all"], default="estimated")
        p.add_argument("--targets-file", type=Path, help="a JSON list of named master leads (organisation_id, name, address, website) "
                       "to use instead of runtime/geocode/targets.json")
        p.add_argument("--out", help="output file name under runtime/geocode/ (default: the command's usual file)")
        if name == "osm-names":
            p.add_argument("--batch", type=int, default=12, help="names per Overpass query")
            p.add_argument("--refresh", action="store_true")
        if name == "sites":
            p.add_argument("--fetch", action="store_true", help="read home and contact pages the crawl cache lacks")
            p.add_argument("--max-extra", type=int, default=2)
            p.add_argument("--no-crawl-cache", action="store_true", help="read only pages fetched by this command")
            p.add_argument("--skip", nargs="*", default=[], help="hosts not to fetch (a server that stalls)")
            p.add_argument("--crawl-cache", type=Path, help="read this contact-crawler cache instead (e.g. the main checkout's, from a worktree)")
            p.add_argument("--always-fetch", action="store_true", help="read home and contact pages even when the cache already has a pin")
            p.add_argument("--mentions", action="store_true", help="also record text around Arusha, Moshi, Usa River or airport mentions")
        if name == "osm":
            p.add_argument("--refresh", action="store_true")
        if name == "nominatim":
            p.add_argument("--limit", type=int, default=120)
            p.add_argument("--queries", type=Path, help='a JSON list of {"id", "name", "query"} written by a reviewer')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    return {"targets": cmd_targets, "sites": cmd_sites, "osm": cmd_osm, "osm-names": cmd_osm_names, "nominatim": cmd_nominatim,
            "pages": cmd_pages, "inventory": cmd_inventory, "repo": cmd_repo, "review": cmd_review, "worklist": cmd_worklist}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
