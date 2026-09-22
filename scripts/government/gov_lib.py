"""Shared helpers for the Silverleaf government-leads scripts (scripts/government/).

Builds on scripts/welfare/welfare_lib.py, which holds polite_request (per-host spacing, retries, backoff, cache),
campus geography and normalisation. This module adds the government run's paths, the rate limits for the council,
regional, census and Wikipedia hosts, the office-level rules and the exclusion list from
plans/b2b-government-leads-plan.md. Limits are documented in
skills/silverleaf-create-lead-list/references/research-rate-limits.md; change them there and here together.
"""
from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path


def _repo_root() -> Path:
    """Walk up to AGENTS.md, so this file works from scripts/government/ and from the skill's bundled copy."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "skills").is_dir():
            return parent
    raise SystemExit("Could not find the repository root (a folder containing AGENTS.md and skills/).")


ROOT = _repo_root()
sys.path.insert(0, str(ROOT / "scripts" / "welfare"))
import welfare_lib as W  # noqa: E402  (shared library; always the canonical copy)

SCRIPTS = Path(__file__).resolve().parent
CANONICAL_SCRIPTS = ROOT / "scripts" / "government"
SKILL = ROOT / "skills" / "silverleaf-government-leads"
SKILL_SCRIPTS = SKILL / "scripts"  # identical bundled copy; verify_government_run.py checks they match

# ------------------------------------------------------------------ rate limits (observed 23 Sep 2026)
# Council and regional sites run on GWF CORE: small government servers with a JSON API. One request at a time,
# at least 1.5 s apart. NBS serves the census report (13 MB) once; it is cached. Wikipedia answered HTTP 429 (with
# Retry-After) at 1 request per second on 23 Sep 2026, so it gets 2 s spacing.
GOV_HOST_LIMIT = {"min_interval": 1.5, "max_workers": 1, "timeout": 90}
for _host in ("arushacc.go.tz", "arushadc.go.tz", "merudc.go.tz", "haidc.go.tz", "sihadc.go.tz", "moshidc.go.tz",
              "moshimc.go.tz", "mondulidc.go.tz", "longidodc.go.tz", "simanjirodc.go.tz", "arusha.go.tz", "kilimanjaro.go.tz",
              "manyara.go.tz"):
    W.HOST_LIMITS.setdefault(_host, GOV_HOST_LIMIT)
    W.HOST_LIMITS.setdefault("www." + _host, GOV_HOST_LIMIT)
W.HOST_LIMITS.setdefault("www.nbs.go.tz", {"min_interval": 2.0, "max_workers": 1, "timeout": 600})
W.HOST_LIMITS.setdefault("en.wikipedia.org", {"min_interval": 2.0, "max_workers": 1, "timeout": 60})

OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.private.coffee/api/interpreter"]


# ------------------------------------------------------------------ run configuration and paths
def load_config(run_id: str) -> dict:
    run_data = ROOT / "data" / "runs" / run_id
    config_path = run_data / "run-config.json"
    if not config_path.exists():
        raise SystemExit(f"Missing {config_path}. Create it from skills/silverleaf-government-leads/references/run-config.example.json.")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    paths = {
        "run_data": run_data,
        "run_out": ROOT / "outputs" / "runs" / run_id,
        "work": ROOT / "runtime" / "government" / run_id,
        "raw": ROOT / "data" / "raw" / "government-research",
        "interim": ROOT / "data" / "interim" / "government-leads",
    }
    for key in ("run_out", "work", "raw", "interim"):
        paths[key].mkdir(parents=True, exist_ok=True)
    paths["cache"] = paths["work"] / "http-cache"
    paths["db"] = paths["run_out"] / "lead-database.sqlite"
    paths["workbook"] = paths["run_out"] / f"Silverleaf Government Leads - {run_id}.xlsx"
    paths["intake"] = run_data / "intake.csv"
    paths["links"] = run_data / "links.json"
    cfg["paths"] = paths
    return cfg


def load_links(cfg: dict) -> dict:
    path = cfg["paths"]["links"]
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def overpass(query: str) -> tuple[bytes, str]:
    """Run one Overpass query politely (>= 5 s apart per host, backoff), falling back to the mirrors."""
    import urllib.parse
    last = None
    for endpoint in OVERPASS:
        try:
            return W.polite_request(endpoint, data=urllib.parse.urlencode({"data": query}), retries=2, backoff=10.0), endpoint
        except Exception as exc:  # noqa: BLE001 - try the next mirror
            last = exc
            print(f"  {endpoint} failed ({exc!r:.100}); trying the next mirror", flush=True)
    raise SystemExit(f"All Overpass endpoints failed: {last!r}")


# ------------------------------------------------------------------ names
def ward_key(name: str) -> str:
    """Comparable ward or place name: no accents, apostrophes, punctuation or roman-numeral spelling differences."""
    s = unicodedata.normalize("NFKD", str(name or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = s.replace("'", "").replace("`", "").replace("-", " ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    words = []
    for w in s.split():
        w = {"ii": "2", "i": "1", "mbili": "2", "moja": "1", "ltd": "limited", "jr": "jr"}.get(w, w)
        if w in ("ward", "kata", "tanzania"):
            continue
        words.append(w)
    return " ".join(words)


# "... is an administrative ward in (the) Meru District of ...", "... ward of the Arusha District ...", "... in the Moshi Rural district ..."
DISTRICT_IN_TEXT = re.compile(r"\b(?:in|of)(?: the)? ([A-Z][\w'’ -]+?(?: Rural| Urban)? (?:[Dd]istrict|Municipal Council|Municipality|City Council))\b")


def squash(name: str) -> str:
    """Ward key without spaces, so 'Usa River' matches 'Usariver' and 'Boma Ngombe' matches 'Bomangombe'."""
    return ward_key(name).replace(" ", "")


def html_to_text(value: str) -> str:
    """Plain text from CMS HTML: table cells become ' | ', rows and blocks become new lines."""
    s = str(value or "")
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)</t[dh]>", " | ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</tr>|</li>|</h\d>|</div>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    lines = [" ".join(line.split()) for line in s.splitlines()]
    return "\n".join(line.strip(" |") for line in lines if line.strip(" |"))


# ------------------------------------------------------------------ sanitising official API captures
# CMS metadata names the website editors, with their emails. They did not publish these for contact purposes,
# so captures never keep them. Photos and biographies of officials are not needed for a convening lead either.
DROP_KEYS = {"createdBy", "updatedBy", "image", "coverImageUrl", "bio", "bioSwahili", "welcomeNote", "welcomeNoteSwahili",
             "assistants", "colors", "customLogo", "tanzaniaLogo", "translations", "icon", "color"}


def sanitise(value):
    if isinstance(value, dict):
        return {k: sanitise(v) for k, v in value.items() if k not in DROP_KEYS}
    if isinstance(value, list):
        return [sanitise(v) for v in value]
    return value


# ------------------------------------------------------------------ office levels and exclusions
LEVEL_RULES = [  # first match wins; applied to lower-cased names
    ("region", r"\bmkoa\b|regional commissioner|regional secretariat|regional administrative|\brc'?s? office\b"),
    ("council", r"halmashauri|district council|city council|municipal council|town council|\bjiji\b|manispaa"),
    ("district", r"mkuu wa wilaya|district commissioner|\bdc'?s office\b|ofisi ya wilaya|district administrative"),
    ("division", r"\btarafa\b|division office"),
    ("ward", r"\bkata\b|ward office|ward building|ward executive|mtendaji wa kata"),
    ("village", r"\bkijiji\b|village office|mtendaji wa kijiji"),
    ("mtaa", r"\bmtaa\b|street office|ofisi ya mtaa|mtendaji wa mtaa"),
    ("hamlet", r"\bkitongoji\b"),
]
# plans/b2b-government-leads-plan.md, "Excluded from this track" and the exclusion list in section 5.3.
EXCLUSIONS = [
    ("political_party", r"\bccm\b|chama cha mapinduzi|chadema|act[- ]?wazalendo|\bcuf\b|nccr|\btlp\b|\budp\b|chaumma|\buvccm\b|\buwt\b|"
                        r"jumuiya ya wazazi|\bchama\b|tawi la|\bparty\b"),
    ("court", r"mahakama|\bcourt\b|tribunal|baraza la ardhi"),
    ("police", r"polisi|police"),
    ("prison", r"magereza|gereza|prison"),
    ("military", r"\bjwtz\b|jeshi|military|\barmy\b|barracks"),
    ("health_facility", r"hospitali|hospital|zahanati|dispensary|kituo cha afya|health cent|clinic|kliniki"),
    ("school", r"\bshule\b|school|sekondari|secondary|primary"),
    ("religious", r"kanisa|church|msikiti|mosque|lutheran|catholic|parish|diocese|dayosisi|\bmission\b"),
]
TAG_EXCLUSIONS = {("amenity", "police"): "police", ("amenity", "courthouse"): "court", ("amenity", "prison"): "prison",
                  ("amenity", "hospital"): "health_facility", ("amenity", "clinic"): "health_facility", ("amenity", "doctors"): "health_facility",
                  ("amenity", "school"): "school", ("amenity", "kindergarten"): "school", ("amenity", "place_of_worship"): "religious",
                  ("landuse", "military"): "military", ("military", None): "military", ("office", "political_party"): "political_party",
                  ("healthcare", None): "health_facility"}
NOT_GOVERNMENT = r"\boil\b|petrol|university|chuo\b|college|\bltd\b|limited|company|\bbank\b|hotel|lodge|\bsacco"
AGENCY = (r"\btra\b|revenue|nssf|tanesco|tanapa|ncaa|conservation|\beac\b|east african community|nida|identification|tawa|wildlife|"
          r"atomic|immigration|uhamiaji|auwasa|water|temesa|housing|information cent|authority|agency|wakala|mamlaka|ruwasa|"
          r"tarura|tanroads|\bnhc\b|\bpccb\b|takukuru|\bnbs\b|statistics|land office|ardhi")


def office_level(name: str) -> str:
    low = str(name or "").lower()
    for level, pattern in LEVEL_RULES:
        if re.search(pattern, low):
            return level
    return ""


def exclusion_reason(name: str, tags: dict | None = None) -> str:
    """The first exclusion category a name or its OpenStreetMap tags fall into, or '' when none applies."""
    for key, value in (tags or {}).items():
        reason = TAG_EXCLUSIONS.get((key, value)) or TAG_EXCLUSIONS.get((key, None))
        if reason:
            return reason
    low = str(name or "").lower()
    for reason, pattern in EXCLUSIONS:
        if re.search(pattern, low):
            return reason
    return ""


def classify_office(name: str, tags: dict | None = None) -> tuple[str, str]:
    """(category, detail): excluded/<reason>, convener/<level>, agency, not_government, or unclassified."""
    reason = exclusion_reason(name, tags)
    if reason:
        return "excluded", reason
    level = office_level(name)
    if level:
        return "convener", level
    low = str(name or "").lower()
    if re.search(NOT_GOVERNMENT, low):
        return "not_government", "mistagged"
    if re.search(AGENCY, low):
        return "agency", "agency_or_parastatal"
    return "unclassified", ""


# ------------------------------------------------------------------ geometry
def point_in_ring(lat: float, lon: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        yi, xi = ring[i]
        yj, xj = ring[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def assemble_rings(ways: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]]:
    """Join OSM relation member ways end to end into closed rings."""
    pending = [list(w) for w in ways if len(w) >= 2]
    rings = []
    while pending:
        ring = pending.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, way in enumerate(pending):
                if way[0] == ring[-1]:
                    ring += way[1:]
                elif way[-1] == ring[-1]:
                    ring += way[::-1][1:]
                elif way[-1] == ring[0]:
                    ring = way[:-1] + ring
                elif way[0] == ring[0]:
                    ring = way[::-1][:-1] + ring
                else:
                    continue
                pending.pop(i)
                changed = True
                break
        rings.append(ring)
    return rings


def load_districts(raw: Path, date: str) -> dict[str, list]:
    """District (OSM admin_level 5) outer rings keyed by name, from collect_ward_locations.py's boundary extract."""
    path = raw / f"osm_admin_level5_{date}.json"
    if not path.exists():
        return {}
    out: dict[str, list] = {}
    for el in json.loads(path.read_text(encoding="utf-8"))["elements"]:
        if el.get("type") != "relation":
            continue
        ways = [[(p["lat"], p["lon"]) for p in m.get("geometry", [])] for m in el.get("members", [])
                if m.get("type") == "way" and m.get("role") in ("outer", "") and m.get("geometry")]
        out[el["tags"].get("name", str(el["id"]))] = assemble_rings(ways)
    return out


def district_of(lat: float, lon: float, districts: dict[str, list]) -> str:
    for name, rings in districts.items():
        if any(len(r) > 3 and point_in_ring(lat, lon, r) for r in rings):
            return name
    return ""
