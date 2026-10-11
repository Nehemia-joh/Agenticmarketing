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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("targets")
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
            "pages": cmd_pages}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
