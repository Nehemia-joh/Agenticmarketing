"""Shared helpers for the Silverleaf welfare-leads skill.

Rate limits are baked in: every network call goes through polite_request(), which enforces a per-host minimum
interval, retries with exponential backoff (honouring Retry-After), sends a User-Agent and can cache to disk.
The limits and why they exist are documented in
skills/silverleaf-create-lead-list/references/research-rate-limits.md. Change them there and here together.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sqlite3
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
SKILL = Path(__file__).resolve().parents[1]
MASTER = ROOT / "outputs" / "master" / "Silverleaf Master Database.sqlite"
TEMPLATE = ROOT / "skills" / "silverleaf-create-lead-list" / "assets" / "lead-intake-template.csv"
CREATE_SCRIPTS = ROOT / "skills" / "silverleaf-create-lead-list" / "scripts"
USER_AGENT = "silverleaf-lead-research/1.0 (welfare-leads skill; rate-limited)"

# ------------------------------------------------------------------ rate limits (observed 22-23 Sep 2026)
HOST_LIMITS = {
    # NGOs Information System: ~2.2 s per profile; 4 workers with 0.3 s spacing fetched 855 profiles in ~30 min, 0 errors.
    "nis.jamii.go.tz": {"min_interval": 0.3, "max_workers": 4, "timeout": 90},
    # Overpass: broad regex queries over the catchment returned 504; one query at a time, >=5 s apart.
    "overpass-api.de": {"min_interval": 5.0, "max_workers": 1, "timeout": 200},
    "overpass.kumi.systems": {"min_interval": 5.0, "max_workers": 1, "timeout": 200},
    "overpass.private.coffee": {"min_interval": 5.0, "max_workers": 1, "timeout": 200},
    # Nominatim usage policy: at most 1 request per second.
    "nominatim.openstreetmap.org": {"min_interval": 1.0, "max_workers": 1, "timeout": 30},
}
DEFAULT_LIMIT = {"min_interval": 1.0, "max_workers": 2, "timeout": 60}
RETRY_STATUS = {429, 500, 502, 503, 504}
_host_locks: dict[str, threading.Lock] = {}
_host_last: dict[str, float] = {}
_guard = threading.Lock()


def host_limit(url_or_host: str) -> dict:
    host = urlsplit(url_or_host).netloc.lower() if "://" in url_or_host else url_or_host.lower()
    return HOST_LIMITS.get(host, DEFAULT_LIMIT)


def clamp_workers(url_or_host: str, requested: int) -> int:
    """Never exceed the documented concurrency for a host, whatever the caller asks for."""
    allowed = host_limit(url_or_host)["max_workers"]
    if requested > allowed:
        print(f"note: {requested} workers requested; capped at {allowed} for {url_or_host} (see research-rate-limits.md)", flush=True)
    return max(1, min(requested, allowed))


def _wait_turn(host: str) -> None:
    limit = HOST_LIMITS.get(host, DEFAULT_LIMIT)
    with _guard:
        lock = _host_locks.setdefault(host, threading.Lock())
    with lock:
        wait = _host_last.get(host, 0.0) + limit["min_interval"] - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _host_last[host] = time.monotonic()


def polite_request(url: str, *, data: str | None = None, retries: int = 3, backoff: float = 3.0,
                   cache_dir: Path | None = None, timeout: float | None = None) -> bytes:
    """GET (or POST form data) with per-host spacing, retries, backoff, Retry-After and an optional disk cache."""
    host = urlsplit(url).netloc.lower()
    limit = HOST_LIMITS.get(host, DEFAULT_LIMIT)
    cache_file = None
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / (hashlib.sha256((url + "\n" + (data or "")).encode()).hexdigest() + ".bin")
        if cache_file.exists():
            return cache_file.read_bytes()
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        _wait_turn(host)
        try:
            request = urllib.request.Request(url, data=data.encode() if data is not None else None, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout or limit["timeout"]) as response:
                body = response.read()
            if cache_file:
                cache_file.write_bytes(body)
            return body
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if exc.code not in RETRY_STATUS or attempt == retries:
                raise
            retry_after = exc.headers.get("Retry-After", "")
            delay = float(retry_after) if retry_after.isdigit() else backoff * (2 ** attempt) + random.uniform(0, 1)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_exc = exc
            if attempt == retries:
                raise
            delay = backoff * (2 ** attempt) + random.uniform(0, 1)
        print(f"retry {attempt + 1}/{retries} for {host} in {delay:.1f}s ({last_exc!r:.80})", flush=True)
        time.sleep(delay)
    raise RuntimeError(f"unreachable: {last_exc!r}")


# ------------------------------------------------------------------ run configuration and paths
def load_config(run_id: str) -> dict:
    run_data = ROOT / "data" / "runs" / run_id
    config_path = run_data / "run-config.json"
    if not config_path.exists():
        raise SystemExit(f"Missing {config_path}. Create it from skills/silverleaf-welfare-leads/references/run-config.example.json.")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    cfg["paths"] = {
        "run_data": run_data,
        "run_out": ROOT / "outputs" / "runs" / run_id,
        "work": ROOT / "runtime" / "welfare" / run_id,
        "raw": ROOT / "data" / "raw" / "welfare-research",
        "interim": ROOT / "data" / "interim" / "welfare-leads",
    }
    for key in ("run_out", "work", "raw", "interim"):
        cfg["paths"][key].mkdir(parents=True, exist_ok=True)
    cfg["paths"]["db"] = cfg["paths"]["run_out"] / "lead-database.sqlite"
    cfg["paths"]["workbook"] = cfg["paths"]["run_out"] / f"Silverleaf Welfare Leads - {run_id}.xlsx"
    cfg["paths"]["intake"] = run_data / "intake.csv"
    cfg["paths"]["links"] = run_data / "links.json"
    return cfg


def load_links(cfg: dict) -> dict:
    path = cfg["paths"]["links"]
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def resolve_globs(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files += sorted(ROOT.glob(pattern))
    return files


# ------------------------------------------------------------------ campuses and geography
LEVELS = {  # Business Context Dossier section 4
    "Usa River": "K1-K2, Std 1-7, boarding",
    "Arusha City": "K1-K2, Std 1-7",
    "Ilboru": "Daycare, K1-K2",
    "Kijenge": "Daycare, K1-K2",
    "Boma Ngombe": "Daycare, K1-K2",
}
PRIMARY_CAMPUSES = {"Usa River", "Arusha City"}
COARSE_PLACES = {"arusha", "arusha city", "arusha cbd", "kilimanjaro", "arumeru", "meru", "hai", "moshi", "dar", "dar es salaam", "tanzania"}


def load_campuses() -> dict:
    if not MASTER.exists():
        raise SystemExit(f"Missing {MASTER}. Restore the master database as README.md describes; it is read-only here.")
    con = sqlite3.connect(f"file:{MASTER.as_posix()}?mode=ro", uri=True)
    rows = {name: (lat, lon) for name, lat, lon in con.execute("SELECT name, latitude, longitude FROM campuses")}
    con.close()
    return rows


def hav(a, b, c, d) -> float:
    r = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = math.radians(c - a), math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def band(km):
    if km is None:
        return "unknown"
    for limit, label in ((5, "0-5 km"), (10, "6-10 km"), (15, "11-15 km"), (20, "16-20 km"), (25, "21-25 km")):
        if km <= limit:
            return label
    return ">25 km (outside catchment)"


def in_catchment_box(lat, lon) -> bool:
    return -3.75 <= lat <= -2.95 and 36.30 <= lon <= 37.55


def build_gazetteer(work: Path) -> dict:
    """Combine the repository's two locality sources into one offline gazetteer (no network calls)."""
    out_path = work / "gazetteer_combined.json"
    gaz: dict[str, tuple] = {}
    for line in (ROOT / "data" / "reference" / "lead-gazetteer.txt").read_text(encoding="utf-8").splitlines():
        p = line.split("|")
        if len(p) >= 3 and p[1] not in ("", "ERR"):
            try:
                gaz[p[0].split(",")[0].strip().lower()] = (float(p[1]), float(p[2]), "lead-gazetteer.txt")
            except ValueError:
                pass
    js = (ROOT / "scripts" / "collection" / "collect_partner_leads.js").read_text(encoding="utf-8")
    start = js.index("const GAZ = {")
    block = js[start: js.index("};", start)]
    for name, lat, lon in re.findall(r"['\"]([^'\"]+)['\"]\s*:\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]", block):
        gaz.setdefault(name.lower(), (float(lat), float(lon), "collect_partner_leads.js GAZ"))
    out_path.write_text(json.dumps(gaz, ensure_ascii=False), encoding="utf-8")
    return gaz


# ------------------------------------------------------------------ normalisation and identity
SHARED_HOSTS = ("facebook.com", "instagram.com", "wixsite.com", "blogspot.com", "wordpress.com", "sites.google.com",
                "linktr.ee", "gofundme.com", "globalgiving.org", "youtube.com", "x.com", "twitter.com", "linkedin.com",
                "weebly.com", "webnode", "jimdo", "squarespace.com", "google.com", "goo.gl", "tiktok.com", "whatsapp.com")
NAME_STOP = {"the", "ltd", "limited", "co", "company", "tz", "tanzania", "t", "ngo", "organization", "organisation", "org",
             "inc", "ev", "e", "v", "cbo", "trust"}
NAME_VARIANTS = {"childrens": "children", "chidren": "children", "center": "centre", "centres": "centre", "orphans": "orphan", "homes": "home"}
GENERIC_TOKENS = {"foundation", "children", "child", "home", "centre", "orphanage", "orphan", "organization", "trust", "fund", "village", "care",
                  "street", "for", "of", "and", "the", "kids", "arusha", "moshi", "kilimanjaro", "hope", "tanzania", "international", "africa",
                  "african", "community", "development", "school", "pre", "primary", "house", "project", "friends", "mission", "ministry",
                  "support", "education", "initiative", "initiatives", "youth", "women", "rescue", "life", "new", "vulnerable", "watoto", "kituo"}
VERIFICATION_RANK = {"verified": 0, "needs_review": 1, "historical": 2, "unverified": 3}
RISK_RANK = {"low": 0, "medium": 1, "risky": 2}
CHILD_ID_PATTERN = re.compile(r"\b(meet|named|called)\s+[A-Z][a-z]+\b|\bsponsor\s+[A-Z][a-z]+\b")
PERSONAL_EMAIL = re.compile(r"@(gmail|yahoo|ymail|hotmail|outlook|live|icloud|aol|rocketmail)\.", re.I)
MATERIAL_FIELDS = {"segment", "children_served_published", "website", "founded", "runs_own_school", "age_range_published", "gender_served",
                   "registration_published"}


def norm_text(value) -> str:
    return " ".join(str(value or "").split())


def name_key(name: str) -> str:
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s).replace("&", " and ").replace("'s", "s")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(NAME_VARIANTS.get(w, w) for w in s.split() if w not in NAME_STOP)


def own_domain(url: str) -> str:
    url = norm_text(url)
    if not url:
        return ""
    if "://" not in url:
        url = "http://" + url
    host = urlsplit(url).netloc.lower().split("@")[-1].split(":")[0]
    host = host[4:] if host.startswith("www.") else host
    if not host or any(h in host for h in SHARED_HOSTS):
        return ""
    return host


def as_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [v for v in value if v not in (None, "")]
    if isinstance(value, str) and ("|" in value or ";" in value):
        return [v.strip() for v in re.split(r"[|;]", value) if v.strip()]
    return [value]


def norm_phone(value: str) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if digits.startswith("0") and len(digits) == 10:
        digits = "255" + digits[1:]
    if len(digits) == 9 and digits[0] in "67":
        digits = "255" + digits
    return "+" + digits if digits else ""


def norm_email(value: str) -> str:
    value = str(value or "").strip().strip(".,;").lower().replace("mailto:", "")
    return value if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value) else ""


def material_value(field: str, value) -> str:
    """Comparable form of a field, so wording differences are not reported as conflicts."""
    text = norm_text(value).lower()
    if field in ("children_served_published", "founded"):
        nums = re.findall(r"\d+", text.replace(",", ""))
        return nums[0] if nums else ""
    if field == "website":
        return own_domain(text) or text
    if field == "age_range_published":
        return "-".join(re.findall(r"\d+", text)[:2])
    if field == "registration_published":
        nums = re.findall(r"\d{3,}", text)
        return max(nums, key=len).lstrip("0") if nums else ""
    if field == "segment":
        return text.split(" ")[1] if " " in text else text
    return text


def best_verification(values) -> str:
    vals = [v for v in values if v in VERIFICATION_RANK]
    return min(vals, key=VERIFICATION_RANK.get) if vals else "unverified"


def read_jsonl(path: Path) -> list[dict]:
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"  ! {path.name}:{n} bad JSON ({exc})")
            continue
        obj["_file"], obj["_line"] = path.name, n
        out.append(obj)
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def js(value) -> str:
    if value in (None, "", [], {}):
        return ""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
