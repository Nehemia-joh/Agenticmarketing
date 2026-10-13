#!/usr/bin/env python3
"""The research ledger: one line per search, page read, crawl, browser read or map lookup, so no worker repeats one.

The ledger is data/raw/research-ledger/research_ledger.jsonl: append-only, committed, one JSON object per attempt. It
holds no contact detail beyond what the committed research files already hold, and `found` never carries an email
address or a phone number (they are redacted). Method and evidence: docs/methodology/research-playbook.md.

Subcommands:
  append    one attempt: the coordinator's own lookups (Google Maps, browser reads, checks), or an agent's pending file
            (--file runtime/research-ledger/pending/<slice>.jsonl) that the coordinator ingests later
  ingest    fold finished files into the ledger in one step: a coverage log, a research JSONL (search_*, browser_*,
            hooks_*, research_*, introducers_*), a Google Maps lookup file, a geocode file, a crawl file or a pending
            ledger file; lines already in the ledger are skipped, so a re-run adds nothing
  backfill  ingest every research file already in the repository (the same parsers, idempotent)
  tried     what was already tried: --org <id> (or --name) lists an organisation's attempts; --pattern <text> lists the
            attempts whose pattern or family contains the text
  stats     attempts and yield by tool, family, pattern, target, segment, date or run
  check     validate every line (fields, values, ids, no address or number in `found`) and report duplicates

Planners import this module: Tried(...) gives each organisation's compact already-tried list, the pattern families still
open for a target, and whether every allowed family was used inside the retry window (--min-retry-days, default 90).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "skills").is_dir():
            return parent
    raise SystemExit("Could not find the repository root (a folder containing AGENTS.md and skills/).")


ROOT = _repo_root()
sys.path.insert(0, str(ROOT / "scripts" / "welfare"))
import welfare_lib as W  # noqa: E402  (name keys and domains, shared with the planners)

RAW = ROOT / "data" / "raw"
LEDGER = RAW / "research-ledger" / "research_ledger.jsonl"
PENDING = ROOT / "runtime" / "research-ledger" / "pending"
PROFILES = ROOT / "runtime" / "contacts" / "profiles.json"
TARGET_FILES = RAW / "contact-research" / "search-targets.json"
FIELDS = ("id", "date", "run", "agent", "tool", "db", "organisation_ids", "organisation_names", "segment", "query", "query_pattern",
          "target", "outcome", "found", "source_file", "ref", "count")
TOOLS = ("websearch", "webfetch", "crawler", "browser", "gmaps", "overpass", "nominatim", "ngo-register", "council-api", "places", "other")
TARGETS = ("route", "decision-maker", "direct-email", "location", "hook", "discovery", "verification", "relationship", "unknown")
OUTCOMES = ("hit", "partial", "nothing", "blocked", "refused-cap", "skipped", "unknown")
DBS = ("master", "welfare", "government", "")
DEFAULT_RETRY_DAYS = 90
# Outcomes that mean the attempt was never made: they never use up a pattern.
NOT_MADE = {"refused-cap", "skipped"}
# The pattern families a search agent may use for each target. An organisation whose families are all used inside the retry
# window is skipped by the planner; one with half or more used is ranked down. An unlogged search (a research record's
# searches_used without a logged query) counts as the baseline "<org>" <town> search the brief makes normal.
SEARCH_FAMILIES = {
    "routes": ("name-town", "contact"),
    "decision-makers": ("name-town", "leader-role"),
    "all": ("name-town", "contact", "leader-role"),
    "direct-email": ("at-domain", "site-person", "vacancy", "report-pdf", "directory", "site-keywords"),
    "direct-email-unnamed": ("leader-role", "at-domain", "vacancy", "report-pdf", "directory", "site-keywords"),
    "hook": ("name-town", "leader-role", "report-pdf"),
}
NEEDS_DOMAIN = {"at-domain", "site-person", "site-keywords"}
FAMILY_ALIASES = {"unlogged": "name-town"}

# The brief every planner writes into its agents' prompts (docs/methodology/contact-research.md, "Research ledger").
AGENT_RULES = """Research ledger (data/raw/research-ledger/research_ledger.jsonl; what has paid so far: docs/methodology/research-playbook.md):
- Before you search for an organisation, read what was already tried for it: its already_tried list in this prompt or the slice,
  or `python scripts/research/ledger.py tried --org <organisation_id>`. Do not repeat a query pattern for the same organisation
  inside the retry window ({retry_days} days); use a pattern that is still open, or fetch a known page instead.
- Log every search and every page you read: in your coverage log, a numbered table `| Q | Query | Organisation | Outcome |`
  (one row per search, the organisation named exactly as in the slice, the outcome in plain words such as "nothing",
  "blocked (403)", "found the HR inbox"), and the pages in your JSONL sources. You may also append each attempt to your own
  pending file with `python scripts/research/ledger.py append --file runtime/research-ledger/pending/{slice}.jsonl --agent {slice}
  --tool websearch --org <id> --query "<exact query>" --outcome <hit|partial|nothing|blocked|refused-cap> --ref Q<n>/<budget>`.
  Never write to the ledger file itself; the coordinator ingests your coverage log, JSONL file and pending file into it."""


# ------------------------------------------------------------------ text helpers
EMAIL = re.compile(r"[\w.+\-]+@(?:[\w\-]+\.)*[\w\-]*")
PHONE = re.compile(r"(?<![\w/.])\+?\d[\d ()./\-]{7,}\d(?![\w/])")
ISO = re.compile(r"(\d{4}-\d{2}-\d{2})")
MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august", "september",
                                       "october", "november", "december"), 1)}


def redact(text: str) -> str:
    """The text without email addresses or phone numbers (dates and decimal numbers are kept)."""
    text = EMAIL.sub("<email>", str(text or ""))

    def phone(m):
        s = m.group(0)
        return s if re.fullmatch(r"\d{4}-\d{2}-\d{2}|-?\d+\.\d+|\d{4}\s*[-–]\s*\d{4}", s.strip()) else "<phone>"
    return PHONE.sub(phone, text)


def short(text: str, limit: int = 180) -> str:
    s = re.sub(r"\s+", " ", redact(str(text or "")).replace("`", "").replace("**", "")).strip()
    return s if len(s) <= limit else s[:limit - 1].rstrip() + "…"


def plain(text: str) -> str:
    return unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode().lower()


def name_key(name: str) -> str:
    return W.name_key(name or "")


def _split(url: str):
    url = str(url or "").strip()
    try:
        return urlsplit(url if "://" in url else "http://" + url)
    except ValueError:
        return urlsplit("http://" + re.sub(r"[\[\]]", "", url.split("://")[-1]))


def domain_of(url: str) -> str:
    host = _split(url).netloc.lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def site_domain(url: str) -> str:
    """The organisation's own domain for a website value (shared hosts such as facebook.com give ''); never raises."""
    try:
        return W.own_domain(url)
    except ValueError:
        return ""


def text_date(text: str) -> str:
    m = ISO.search(text or "")
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{1,2}) (january|february|march|april|may|june|july|august|september|october|november|december) (20\d\d)\b",
                  plain(text))
    return f"{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}" if m else ""


def file_date(path: Path) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    return m.group(1) if m else ""


def rel(path: Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def jsonl(path: Path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


# ------------------------------------------------------------------ query patterns and families
TOWN_PHRASES = ("usa river", "boma ng'ombe", "boma ngombe", "mto wa mbu", "sanya juu", "dar es salaam", "west kilimanjaro", "jiji la arusha")
TOWNS = {"arusha", "moshi", "tengeru", "karatu", "kilimanjaro", "tanzania", "meru", "arumeru", "njiro", "sakina", "kijenge", "hai", "siha",
         "monduli", "longido", "kia", "mererani", "simanjiro", "manyara", "babati", "mbuguni", "kikatiti", "ngaramtoni", "olasiti",
         "sombetini", "themi", "moshono", "kisongo", "ilboru", "kimandolu", "muriet", "sekei", "nduruma", "bomang'ombe", "tz", "mateves",
         "patandi", "kikwe", "makumira", "himo", "rombo", "mwanga", "same", "kenya", "nairobi", "uk", "usa", "germany"}
KEEP = {"contact", "contacts", "email", "e-mail", "phone", "telephone", "address", "website", "office", "director", "directors", "founder",
        "founders", "co-founder", "ceo", "md", "gm", "manager", "managing", "general", "head", "principal", "rector", "chairman",
        "chairperson", "chair", "president", "owner", "owners", "proprietor", "administrator", "administration", "coordinator", "secretary",
        "hr", "human", "resources", "resource", "people", "leadership", "management", "board", "trustees", "trustee", "team", "staff",
        "executive", "officer", "vacancy", "vacancies", "job", "jobs", "career", "careers", "recruitment", "application", "apply", "hiring",
        "annual", "report", "profile", "pdf", "members", "member", "membership", "directory", "list", "register", "registered", "registration",
        "exhibitor", "exhibitors", "branch", "orphanage", "orphans", "orphan", "children", "home", "centre", "center", "foundation", "ngo",
        "school", "church", "diocese", "funder", "funders", "sponsor", "sponsors", "partner", "partners", "grant", "grants", "donate",
        "location", "map", "kituo", "watoto", "yatima", "makao", "nafasi", "kazi", "mkurugenzi", "ofisi", "kata", "wilaya", "mkuu", "afisa",
        "mtendaji", "hospital", "clinic", "hotel", "lodge", "bursar", "matron", "in-charge", "deputy", "country", "medical", "news",
        "closed", "address", "p.o.", "box", "plot", "facebook", "instagram", "linkedin", "tripadvisor", "safaribookings", "tato"}
KEEP_PHRASES = {"send your application", "annual report", "human resources", "managing director", "general manager", "executive director",
                "head of school", "country manager", "medical director", "board of directors", "our team", "contact us", "p.o. box"}
ROLE = re.compile(r"director|founder|ceo|\bmd\b|\bgm\b|manager|managing|\bhead\b|principal|rector|chair|president|owner|proprietor|"
                  r"administrat|coordinator|secretary|\bhr\b|human|leadership|management|board|trustee|team|staff|executive|officer|"
                  r"mkurugenzi|mkuu|afisa|mtendaji|bursar|matron|in-charge|deputy")
HOST_CATEGORIES = (
    ("broker", ("zoominfo", "rocketreach", "signalhire", "apollo.io", "lusha", "contactout")),
    ("register", ("nis.jamii.go.tz", "brela.go.tz", "charitycommission.gov.uk", "propublica.org", "guidestar", "candid.org",
                  "charitynavigator", "acnc.gov.au", "oscr.org.uk", "opencorporates", "find-and-update.company-information", "ushirika.go.tz",
                  "irs.gov", "causeiq", "charities.org", "givewell", "tcra.go.tz", "tra.go.tz", "tic.go.tz", "tmda.go.tz", "moh.go.tz",
                  "hfrs.moh.go.tz")),
    ("directory", ("tatotz.org", "ate.or.tz", "safaribookings", "ceort", "tccia", "atta.travel", "medpages", "afyadirectory", "cybo.com",
                   "yellow", "touristmaker", "travelstride", "getyourguide", "ngobase", "idealist", "devex", "globalgiving",
                   "bettercarenetwork", "kilifair", "school.co.tz", "tanzaniainvest", "zoomtanzania.net/biz", "businesslist", "worldplaces",
                   "africabizinfo", "kompass", "exhibitor", "members", "tanzania-experience", "ttb.go.tz")),
    ("vacancy", ("ajiriwa", "zoomtanzania", "brightermonday", "jobweb", "mabumbe", "tanzajob", "fursa", "kazi", "jobs", "career",
                 "recruit", "myjobs", "employment", "vacanc")),
    ("social", ("facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "youtube.com", "tiktok.com", "wa.me")),
    ("review", ("tripadvisor", "trustpilot", "yelp", "google.com/travel")),
    ("maps", ("google.com/maps", "maps.google", "openstreetmap.org", "goo.gl/maps", "maps.app.goo.gl")),
    ("reference", ("wikipedia.org", "wikidata.org", "wikimedia")),
    ("news", ("dailynews", "thecitizen", "ippmedia", "michuzi", "mwananchi", "habarileo", "allafrica", "theeastafrican", "blogspot",
              "news", "jamiiforums", "reddit")),
    ("government", (".go.tz", ".gov", ".gouv", "gov.uk", ".int")),
)
GENERIC_HOST_WORDS = {"safari", "safaris", "tours", "tour", "travel", "travels", "adventure", "adventures", "tanzania", "africa", "african",
                      "arusha", "children", "childrens", "home", "homes", "foundation", "hotel", "hotels", "lodge", "lodges", "company",
                      "limited", "group", "international", "organization", "organisation", "center", "centre", "trust", "school",
                      "hospital", "church", "care", "kilimanjaro", "moshi", "expedition", "expeditions", "camp", "camps", "holidays",
                      "holiday", "trek", "treks", "trekking", "climb", "network", "development", "community", "project", "services",
                      "service", "the", "and", "for", "with", "orphanage", "village", "mission", "ministry", "ministries", "society"}


def host_category(url_or_host: str) -> str:
    s = str(url_or_host or "").lower()
    for category, needles in HOST_CATEGORIES:
        if any(n in s for n in needles):
            return category
    return "other-site"


def own_site(url: str, org_names=(), domains=()) -> bool:
    host = domain_of(url)
    if not host:
        return False
    for d in domains:
        d = domain_of(d)
        if d and (host == d or host.endswith("." + d) or d.endswith("." + host)):
            return True
    squashed = re.sub(r"[^a-z]", "", host)
    for name in org_names:
        words = {w for w in re.findall(r"[a-z]{5,}", plain(name)) if w not in GENERIC_HOST_WORDS}
        if words and any(w in squashed for w in words):
            return True
    return False


def page_kind(url: str) -> str:
    p = (_split(url).path or "/").lower()
    if p.endswith(".pdf"):
        return "pdf"
    if re.fullmatch(r"/?(index\.\w+|home/?|en/?|sw/?)?", p.strip("/")) or p in ("", "/"):
        return "home"
    for kind, rx in (("contact", r"contact|mawasiliano|reach|find-us|location|get-in-touch"),
                     ("team", r"team|staff|people|leadership|management|board|trustee|director|founder|who-we-are|uongozi|our-story|meet"),
                     ("careers", r"career|job|vacanc|recruit|nafasi"), ("about", r"about|history|story|profile|kuhusu"),
                     ("news", r"news|blog|press|media|event|habari")):
        if re.search(rx, p):
            return kind
    return "other"


def url_pattern(tool: str, url: str, org_names=(), domains=()) -> str:
    """fetch:own-site/<kind>, fetch:<category>:<host> (and browser:..., crawl:... alike) for a page read."""
    prefix = {"webfetch": "fetch", "browser": "browser", "crawler": "crawl"}.get(tool, tool)
    if own_site(url, org_names, domains):
        return f"{prefix}:own-site/{page_kind(url)}"
    category = host_category(url)
    host = domain_of(url)
    return f"{prefix}:{category}:{host}" if host else f"{prefix}:{category}"


def _word(tok: str) -> str:
    w = plain(tok).strip(".,;:!?()[]{}'\"")
    return re.sub(r"'s$", "", w).replace("children's", "children")


def distinctive(key: str) -> bool:
    """A name key with at least one word that is neither generic nor a place ('arusha childrens home' is not)."""
    return any(len(w) >= 4 and w not in GENERIC_HOST_WORDS and w not in TOWNS for w in key.split())


def name_variants(names) -> list[str]:
    """Each name, without a trailing parenthesis and without a legal-form or country suffix, longest first."""
    out = set()
    for n in names:
        n = W.norm_text(n)
        if not n:
            continue
        out.add(n)
        base = re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()
        out.add(base)
        out.add(re.sub(r"[\s,]+(ltd|limited|co\.? ltd|company limited|plc|inc|tanzania|\(t\)|t ltd)\.?$", "", base, flags=re.I).strip())
    return sorted((v for v in out if len(v) >= 4), key=len, reverse=True)


def search_pattern(query: str, org_names=(), domains=(), guess_org: bool | None = None) -> str:
    """A normalised template of a web search: the organisation, its domain, a person, towns and free words become placeholders;
    operators and the brief's keywords stay. '"Equity Bank Tanzania" "@equitybank.co.tz"' -> '"<org>" "@<domain>"'."""
    q = str(query or "").strip().strip("`").strip()
    if not q:
        return "<unlogged>"
    q = q.replace("“", '"').replace("”", '"').replace("’", "'").replace("`", "")
    resolved = any(n for n in org_names) if guess_org is None else guess_org
    for name in name_variants(org_names):
        q = re.sub(re.escape(name), "\x01", q, flags=re.I)
    for d in sorted({domain_of(d) for d in domains if d}, key=len, reverse=True):
        if d:
            q = re.sub(r"(?:https?://)?(?:www\.)?" + re.escape(d), "\x02", q, flags=re.I)
    for phrase in TOWN_PHRASES:
        q = re.sub(r"\b" + re.escape(phrase) + r"\b", "\x03", q, flags=re.I)
    tokens = re.findall(r'-?[a-z]+:"[^"]*"|-?[a-z]+:\S+|"[^"]*"?|\S+', q, flags=re.I)
    out, org_used, in_run = [], False, False
    for tok in tokens:
        low = tok.lower().lstrip("-")
        capital = False
        if low.startswith("site:"):
            host = low[5:].strip('"')
            host = host[4:] if host.startswith("www.") else host
            out.append("site:<domain>" if "\x02" in host or host_category(host) == "other-site" else "site:" + host)
        elif re.match(r"(filetype|intitle|inurl|intext):", low):
            out.append(low.replace("\x01", "<org>"))
        elif tok.lstrip("-").startswith('"'):
            inner = tok.lstrip("-").strip('"').strip()
            words = [_word(w) for w in inner.split()]
            if "\x01" in inner:
                out.append('"<org>"')
                org_used = True
            elif inner.startswith("@"):
                out.append('"@<domain>"')
            elif "@" in inner:
                out.append('"<email>"')
            elif "\x02" in inner:
                out.append('"<domain>"')
            elif "\x03" in inner or plain(inner) in TOWNS:
                out.append("<town>")
            elif plain(inner) in KEEP_PHRASES or (words and all(w in KEEP for w in words)):
                out.append('"' + plain(inner) + '"')
            elif any(o.startswith("site:") for o in out) and 1 <= len(inner.split()) <= 3 and inner[:1].isupper():
                out.append('"<person>"')
            elif resolved and not org_used:
                out.append('"<org>"')
                org_used = True
            else:
                out.append('"<name>"')
        elif "\x01" in tok:
            out.append("<org>")
            org_used = True
        elif "\x02" in tok:
            out.append("<domain>")
        elif "\x03" in tok:
            out.append("<town>")
        elif tok in ("OR", "AND", "|"):
            out.append("OR")
        else:
            w = _word(tok)
            if w in TOWNS:
                out.append("<town>")
            elif w in KEEP:
                out.append(w)
            elif in_run and (tok[:1].isupper() or w in ("of", "and", "the", "for", "&", "de", "la")):
                capital = True
            elif resolved and not org_used and tok[:1].isupper():
                out.append("<org>")
                org_used = capital = True
        in_run = capital
    clean = []
    for tok in out:
        if clean and tok == clean[-1]:
            continue
        if tok == "OR" and (not clean or clean[-1] == "OR"):
            continue
        clean.append(tok)
    while clean and clean[-1] == "OR":
        clean.pop()
    return " ".join(clean) or "<words>"


def family_of(tool: str, pattern: str) -> str:
    """The coarse kind of an attempt, for stats and for the planners' exhaustion check."""
    p = pattern or ""
    if tool == "websearch":
        if p == "<unlogged>":
            return "unlogged"
        has_site = "site:<domain>" in p
        if "<person>" in p:
            return "site-person" if has_site else "person-name"
        if "@<domain>" in p:
            return "at-domain"
        if '"<email>"' in p:
            return "address-check"
        if re.search(r"vacanc|\bjobs?\b|career|recruit|application|nafasi|kazi|hiring", p):
            return "vacancy"
        if re.search(r"annual|report|filetype:pdf|\bprofile\b", p):
            return "report-pdf"
        if has_site:
            return "site-keywords"
        if re.search(r"site:\S+|\bdirectory\b|\bmembers?\b|membership|\bregister|exhibitor|\blist\b|tato|safaribookings", p):
            return "directory"
        if "<org>" not in p and "<name>" not in p and "<domain>" not in p:
            return "discovery"
        if ROLE.search(p):
            return "leader-role"
        if re.search(r"contact|email|phone|address|website|office|p\.o\.|box", p):
            return "contact"
        return "name-town"
    if tool in ("webfetch", "browser", "crawler"):
        head = p.split(":", 2)
        kind = head[1].split("/")[0] if len(head) > 1 else "page"
        if tool == "crawler":
            return "crawl-deep" if "(deep)" in p else ("crawl-map-embed" if "map-embed" in p else "crawl-own-site")
        return f"{'fetch' if tool == 'webfetch' else 'browser'}-{kind}"
    return {"gmaps": "gmaps-lookup", "overpass": "osm", "nominatim": "nominatim", "ngo-register": "register", "council-api": "council-api",
            "places": "places"}.get(tool, "other")


# ------------------------------------------------------------------ outcomes
REFUSED = re.compile(r"^\W*refused|(search|query|websearch)[^.]{0,40}refused|refused[^.]{0,30}(budget|cap|limit)|budget (was )?(exhausted|spent)|"
                     r"cap (was )?reached|limit (was )?reached|search limit|\bnot run\b|never run|no searches? left", re.I)
NOTHING = re.compile(r"\bnothing\b|\bno (result|match|hit|address|route|new|useful|relevant|page|contact|email|phone|record|named|data|"
                     r"organisation|organization|information|mention|trace|listing|leader|people|person|name|own|current|location|"
                     r"usable|confirmed|link|site|details|role|director)|not[_ ]found|unrelated|\bnone\b|irrelevant|only (other|unrelated|"
                     r"third|differently|older|the|a |an |snippet|review|booking|broker|directories|directory|data)|did not (find|return|resolve|"
                     r"show|name)|returned only|\bzero\b|not recorded|not used|other (organisations|companies|banks|charities|homes)|"
                     r"no-one|nobody|names? nobody|not a match|wrong (listing|place|organisation)|reject|\bonly\b", re.I)
BLOCKED = re.compile(r"\b403\b|\b429\b|\b511\b|captcha|bot check|bitninja|cloudflare|login wall|\bblocked\b|blocks\b|forbidden|"
                     r"certificate|\btls\b|timed? ?out|unreachable|\bdns\b|did not resolve|does not resolve|refused connection", re.I)
HIT = re.compile(r"\bfound\b|recorded|\bgives?\b|\bgave\b|\bconfirm|yield|led to|\blists?\b|\bnames (?!nobody|no )|\bnamed\b|publish|\badded\b|"
                 r"located|\bplaced\b|\baccept|\bfetched\b|→|->", re.I)
NEG_FOUND = re.compile(r"(not|nothing|no \w+( \w+)?|none) (was |were )?(found|recorded|named|confirmed|published|listed)", re.I)
STATUS_OUTCOME = {"found": "hit", "partial": "partial", "not_found": "nothing", "blocked": "blocked", "accept": "hit", "review": "partial",
                  "reject": "nothing", "placed": "hit", "outside_confirmed": "hit", "held_back": "partial", "confirmed": "hit",
                  "changed": "partial", "unreachable": "blocked"}


def classify(text: str, positive: bool = False) -> str:
    """hit, partial, nothing, blocked, refused-cap or unknown, from a coverage log's outcome text."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if not t:
        return "unknown"
    if REFUSED.search(t):
        return "refused-cap"
    low = t.lower()
    tail = re.sub(r"[`*]", "", low).rstrip(" .")
    if re.search(r"(not[ _]found|nothing found|none found|no match)$", tail):
        return "nothing"
    for word, outcome in (("partial", "partial"), (" found", "hit"), ("blocked", "blocked")):
        if tail.endswith(word):
            return outcome
    if re.search(r"\bpartial\b", low):
        return "partial"
    last = re.split(r"(?<=[.;])\s+", t)[-1].lower()
    if re.fullmatch(r"(nothing|nothing (used|recorded|new|for [^.]*)|no result|no match)\.?", last.strip()):
        return "nothing"
    probe = NEG_FOUND.sub(" ", t)
    hit, nothing, blocked = bool(HIT.search(probe)), bool(NOTHING.search(t)), bool(BLOCKED.search(t))
    if hit and not nothing:
        return "hit"
    if hit and nothing:
        return "partial"
    if nothing:
        return "nothing"
    if blocked:
        return "blocked"
    return "hit" if positive else "unknown"


# ------------------------------------------------------------------ entries and the ledger file
def entry(**kw) -> dict:
    e = {f: "" for f in FIELDS}
    e.update({"organisation_ids": [], "organisation_names": [], "count": 1})
    e.update({k: v for k, v in kw.items() if k in FIELDS and v is not None})
    e["organisation_ids"] = [x for x in dict.fromkeys(e["organisation_ids"] or []) if x]
    e["organisation_names"] = [x for x in dict.fromkeys(W.norm_text(n) for n in (e["organisation_names"] or [])) if x]
    e["query"] = W.norm_text(e["query"])
    if not e["query_pattern"]:
        if e["tool"] == "websearch":
            e["query_pattern"] = search_pattern(e["query"], e["organisation_names"], kw.get("domains") or (),
                                                guess_org=bool(e["organisation_ids"]) if kw.get("guess_org") is None else kw["guess_org"])
        elif e["tool"] in ("webfetch", "browser", "crawler") and e["query"].startswith("http"):
            e["query_pattern"] = url_pattern(e["tool"], e["query"], e["organisation_names"], kw.get("domains") or ())
        elif e["tool"] in ("gmaps", "places") and e["query"] and not e["query"].startswith("http"):
            e["query_pattern"] = f'{e["tool"]}:"' + search_pattern(e["query"], e["organisation_names"], guess_org=True).replace('"', "") + '"'
        else:
            e["query_pattern"] = e["tool"]
    e["found"] = short(e["found"])
    e["count"] = int(e["count"] or 1)
    return e


def dedupe_key(e: dict) -> tuple:
    orgs = tuple(sorted(e.get("organisation_ids") or [])) or tuple(sorted(name_key(n) for n in e.get("organisation_names") or []))
    return (e.get("tool"), e.get("date"), e.get("db"), orgs, plain(e.get("query", "")).strip(), e.get("ref", ""), e.get("agent", ""))


def load(path: Path = LEDGER) -> list[dict]:
    return list(jsonl(path)) if Path(path).exists() else []


def next_number(entries) -> int:
    nums = [int(m.group(1)) for e in entries for m in [re.fullmatch(r"RL(\d+)", str(e.get("id", "")))] if m]
    return max(nums, default=0) + 1


def write(new: list[dict], path: Path = LEDGER, existing: list[dict] | None = None) -> tuple[int, int]:
    """Append the entries not already present (by dedupe key), numbering them after the last id. Returns (added, skipped)."""
    path = Path(path)
    existing = load(path) if existing is None else existing
    seen = {dedupe_key(e) for e in existing}
    number = next_number(existing)
    lines, skipped = [], 0
    for e in new:
        k = dedupe_key(e)
        if k in seen:
            skipped += 1
            continue
        seen.add(k)
        e = {**entry(), **{f: e[f] for f in FIELDS if f in e}}
        e["id"] = f"RL{number:06d}"
        number += 1
        lines.append(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
    if lines:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")
    return len(lines), skipped


# ------------------------------------------------------------------ organisations
class OrgIndex:
    """Organisation names to (db, id), from the contact profiles (when present) and the research files' own records."""

    def __init__(self):
        self.info: dict[tuple, dict] = {}
        self.by_key: dict[str, set] = defaultdict(set)

    def add(self, db, oid, name, segment="", website=""):
        if not oid or not name:
            return
        info = self.info.setdefault((db, oid), {"name": name, "segment": segment or "", "domains": set()})
        info["segment"] = info["segment"] or segment or ""
        if website:
            for w in (website if isinstance(website, list) else [website]):
                if domain_of(w):
                    info["domains"].add(domain_of(w))
        self.by_key[name_key(name)].add((db, oid))

    def load_profiles(self, path: Path = PROFILES):
        if not Path(path).exists():
            return False
        for p in json.loads(Path(path).read_text(encoding="utf-8")).get("profiles", []):
            self.add(p["db"], p["organisation_id"], p["name"], p.get("segment", ""), p.get("websites") or [])
        return True

    def load_research(self):
        for pattern in ("contact-research/search_*.jsonl", "contact-research/browser_*.jsonl", "hook-research/hooks_*.jsonl"):
            for path in sorted(RAW.glob(pattern)):
                for r in jsonl(path):
                    if (r.get("db") or "master", r.get("organisation_id")) not in self.info:
                        self.add(r.get("db") or "master", r.get("organisation_id"), r.get("organisation_name"), "", r.get("website") or "")

    def resolve(self, name: str, db: str | None = None):
        hits = self.by_key.get(name_key(name), set())
        if db:
            same = {h for h in hits if h[0] == db}
            hits = same or hits
        return next(iter(hits)) if len(hits) == 1 else None

    def fuzzy(self, probe: str, db: str | None = None):
        """The one organisation whose name key holds the probe's key as whole words (at least 6 letters), else None."""
        k = name_key(probe)
        if len(k) < 6:
            return None
        padded = " " + k + " "
        hits = {key for nk, keys in self.by_key.items() if padded in " " + nk + " " for key in keys}
        if db:
            hits = {h for h in hits if h[0] == db} or hits
        return next(iter(hits)) if len(hits) == 1 else None

    def twins(self, name: str, db: str | None = None) -> list:
        """Two or three records under exactly the same name key (twin records), else []."""
        hits = self.by_key.get(name_key(name), set())
        if db:
            hits = {h for h in hits if h[0] == db} or hits
        return sorted(hits) if 1 < len(hits) <= 3 and len({h[0] for h in hits}) == 1 else []

    def current(self, db, oid, name):
        """The profile ID for a record whose ID may be stale (resolved by name when the ID is unknown)."""
        if (db, oid) in self.info:
            return (db, oid)
        return self.resolve(name, db) or ((db, oid) if oid else None)

    def segment(self, key) -> str:
        return self.info.get(key, {}).get("segment", "") if key else ""

    def domains(self, key) -> set:
        return self.info.get(key, {}).get("domains", set()) if key else set()


_INDEX: OrgIndex | None = None


def org_index() -> OrgIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = OrgIndex()
        _INDEX.load_profiles()
        _INDEX.load_research()
    return _INDEX


def with_orgs(index: OrgIndex, db: str, pairs, **kw) -> dict:
    """An entry for organisations given as (id, name) pairs: IDs made current, names kept, segment and domains looked up."""
    ids, names, segments, domains = [], [], [], set(kw.pop("domains", ()) or ())
    for oid, name in pairs:
        key = index.current(db, oid, name or "") if (oid or name) else None
        twins = [] if key or not name else index.twins(name, db or None)
        for twin in twins:  # the same name held twice (twin records): the attempt concerns both
            ids.append(twin[1])
            db = twin[0]
            segments.append(index.segment(twin))
        if key:
            ids.append(key[1])
            db = key[0] if not ids[:-1] else db
            segments.append(index.segment(key))
            domains |= index.domains(key)
        if name:
            names.append(name)
        elif key:
            names.append(index.info.get(key, {}).get("name", ""))
    given = kw.pop("segment", "")
    guess = kw.pop("guess_org", None)
    return entry(db=db, organisation_ids=ids, organisation_names=names, segment=next((s for s in segments if s), "") or given,
                 domains=domains, guess_org=guess, **kw)


# ------------------------------------------------------------------ run, agent and target of a file
AREA = {"contact-research": "contact", "welfare-research": "welfare", "hook-research": "hooks", "gap-census": "gap-census",
        "geocode-research": "geocode", "government-research": "government", "vicoba-research": "vicoba"}
WELFARE_TARGET = {"A": "discovery", "B": "discovery", "C": "discovery", "D": "discovery", "E": "discovery", "F": "discovery",
                  "G": "relationship", "H": "discovery", "I": "discovery", "N": "discovery", "P": "route", "Q": "decision-maker",
                  "R": "relationship", "S": "route", "T": "route", "U": "verification", "V": "verification", "W": "route",
                  "X": "decision-maker", "Y": "route", "Z": "discovery"}
_TARGETS_CACHE = None


def search_targets() -> dict:
    global _TARGETS_CACHE
    if _TARGETS_CACHE is None:
        _TARGETS_CACHE = json.loads(TARGET_FILES.read_text(encoding="utf-8")).get("files", {}) if TARGET_FILES.exists() else {}
    return _TARGETS_CACHE


def area_of(path: Path) -> str:
    for part in reversed(Path(path).resolve().parts):
        if part in AREA:
            return AREA[part]
    return "other"


def slug_of(path: Path) -> str:
    stem = Path(path).stem
    stem = re.sub(r"_coverage$", "", stem)
    return re.sub(r"^(search|research|browser|hooks|introducers)_", lambda m: "" if m.group(1) in ("search", "research") else m.group(0), stem)


def run_agent(path: Path, when: str) -> tuple[str, str]:
    area, slug = area_of(path), slug_of(path)
    base = re.sub(r"_\d{4}-\d{2}-\d{2}[a-z]?$", "", slug)
    m = re.search(r"(?:^|_)(wave\d+|hd\d+)(?:_|$)", base)
    if m:
        return f"{area}-{m.group(1)}", base
    if area == "contact" and re.match(r"[A-D]_", base):
        return "contact-wave1", base
    if area == "welfare" and re.match(r"[A-Z]_", base):
        return ("welfare-run1" if base[0] in "ABCDEFGH" else f"welfare-{base[0]}"), base
    if base == "coverage" or base.startswith("coverage_"):
        return f"{area}-{when}", "coordinator"
    return f"{area}-{when}", base


def target_of(path: Path, paired: Path | None = None) -> str:
    area = area_of(path)
    needs = search_targets().get(paired.name if paired else Path(path).name)
    if needs:
        if "own work email" in needs:
            return "direct-email"
        if "named decision-maker" in needs and "published route" not in needs:
            return "decision-maker"
        return "route"
    slug = slug_of(path)
    if area == "hooks":
        return "hook"
    if area == "geocode":
        return "location"
    if area in ("gap-census", "vicoba"):
        return "discovery"
    if area == "government":
        return "decision-maker"
    if area == "welfare":
        return WELFARE_TARGET.get(slug[:1], "unknown")
    if "introducers" in slug:
        return "discovery"
    if re.search(r"jobs|p1_pages|groups|wave1[0-2]", slug):
        return "decision-maker"
    return "route"


def db_default(path: Path) -> str:
    area = area_of(path)
    return {"welfare": "welfare", "government": "government"}.get(area, "master" if area in ("hooks", "gap-census") else "")


def pair_research_file(coverage: Path) -> Path | None:
    """The research JSONL a coverage log describes: same slice tokens, the log's own date when it has one, else the earliest."""
    folder = coverage.parent.parent if coverage.parent.name == "coverage" else coverage.parent
    slug = re.sub(r"_coverage$", "", coverage.stem)
    when = file_date(coverage)
    base = re.sub(r"_?\d{4}-\d{2}-\d{2}[a-z]?$", "", slug)
    if area_of(coverage) == "gap-census":
        hits = sorted(folder.glob(f"research_targeted_{when}*.jsonl"))
        return hits[0] if hits else None
    if area_of(coverage) == "geocode":
        name = "geocodes_user51" if "user51" in slug else "geocodes"
        hits = sorted(folder.glob(f"{name}_{when}.jsonl"))
        return hits[0] if hits else None
    tokens = set(base.split("_"))
    candidates = []
    for p in folder.glob("*.jsonl"):
        stem = re.sub(r"_\d{4}-\d{2}-\d{2}[a-z]?$", "", p.stem)
        ptoks = set(stem.split("_"))
        if tokens <= ptoks and ptoks - tokens <= {"search", "research", "browser", "hooks", "introducers"} and file_date(p):
            candidates.append(p)
    if not candidates:
        return None
    candidates.sort(key=lambda p: file_date(p))
    if when:
        exact = [p for p in candidates if file_date(p) == when]
        if exact:
            return exact[0]
        earlier = [p for p in candidates if file_date(p) <= when]
        return earlier[-1] if earlier else candidates[0]
    return candidates[0]


# ------------------------------------------------------------------ coverage logs
REF = re.compile(r"Q?(\d+)(?:\s*[-–]\s*Q?(\d+))?(?:/(\d+))?", re.I)
BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)?\s*(?:\*\*)?(Q\d+(?:\s*[-–]\s*Q?\d+)?(?:/\d+)?)(?:\*\*)?\s*[:.)]?\s+(.*)$")
SEPARATOR_ROW = re.compile(r"^\|?(\s*:?-{2,}:?\s*\|)+\s*:?-*:?\s*\|?$")


def _cells(line: str) -> list[str]:
    line = line.strip().replace("\\|", "\x04")
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip().replace("\x04", "|") for c in line.split("|")]


def _header(cells):
    low = [c.lower().strip() for c in cells]
    q = next((i for i, c in enumerate(low) if "quer" in c), None)
    o = next((i for i, c in enumerate(low) if i != q and re.search(r"organi|^target|^lead|employer", c)), None)
    out = next((i for i, c in enumerate(low) if i not in (q, o) and re.search(r"outcome|result|found|led to|useful|status|what", c)), None)
    n = 0 if low and (low[0] in ("#", "no.", "no", "q", "n", "nr", "") or re.fullmatch(r"q\w*", low[0])) else None
    if out is None and len(cells) - 1 not in (q, o, n):
        out = len(cells) - 1
    positive = bool(out is not None and re.search(r"found|useful|led to|new institution|what it", low[out]))
    return {"n": n, "q": q, "o": o, "out": out, "positive": positive, "valid": n is not None and (q is not None or o is not None)}


def _split_bullet(rest: str) -> tuple[str, str]:
    rest = rest.strip()
    m = re.match(r"`([^`]+)`\s*[:.\-–—>]*\s*(.*)$", rest)
    if m:
        return m.group(1), m.group(2)
    for sep in (" -> ", " → ", " — ", " – ", ": "):
        if sep in rest:
            a, b = rest.split(sep, 1)
            return a, b
    return rest, ""


def _clean_org(text: str) -> str:
    t = re.sub(r"[`*]", "", text or "").strip()
    t = re.sub(r"^\d+\.\s*", "", t)
    return re.sub(r"\s*\((?:both records|\+[^)]*|slice[^)]*|duplicate[^)]*)\)\s*$", "", t).strip()


class CoverageContext:
    def __init__(self, path: Path, index: OrgIndex):
        self.path, self.index = path, index
        self.paired = pair_research_file(path)
        text = path.read_text(encoding="utf-8")
        self.text = text
        self.date = file_date(path) or (file_date(self.paired) if self.paired else "") or text_date(text)
        self.run, self.agent = run_agent(path, self.date)
        self.target = target_of(path, self.paired)
        self.db = db_default(path)
        self.local: dict[str, tuple] = {}
        if self.paired and self.paired.suffix == ".jsonl":
            for r in jsonl(self.paired):
                name = r.get("organisation_name") or r.get("name") or r.get("from_organisation") or ""
                if not name:
                    continue
                db = r.get("db") or self.db
                key = index.current(db, r.get("organisation_id") or "", name) if (r.get("organisation_id") or name) else None
                self.local.setdefault(name_key(name), (db, key[1] if key else (r.get("organisation_id") or ""), name,
                                                       r.get("website") or ""))
        dbs = Counter(v[0] for v in self.local.values() if v[0])
        self.db = self.db or (dbs.most_common(1)[0][0] if dbs else "") or ("master" if area_of(path) == "contact" else "")

    def _probe(self, probe: str):
        k = name_key(probe)
        if not k:
            return None
        if k in self.local:
            db, oid, name, web = self.local[k]
            return db, oid, name, {web} if web else set()
        hit = self.index.resolve(probe, self.db or None) or self.index.fuzzy(probe, self.db or None)
        if hit:
            return hit[0], hit[1], self.index.info[hit]["name"], self.index.domains(hit)
        return None

    def resolve(self, org_text: str, query: str):
        """(db, [(id, name)], domains, matched) for a coverage row: the organisation column first, else every quoted name in the query
        (a query joining several names with OR concerns each of them), else a slice name the text contains."""
        clean = _clean_org(org_text)
        if clean:
            hit = self._probe(clean)
            if hit:
                return hit[0], [(hit[1], hit[2])], hit[3], True
        found, domains, db = [], set(), self.db
        probes = re.findall(r'"([^"]{3,})"', query or "")
        if not probes:
            parts = [p for p in re.split(r"\s+/\s+|\s+OR\s+|;\s*", query or "") if p.strip()]
            probes = parts if len(parts) > 1 else []
            run = re.match(r"\s*((?:[A-Z][\w'’&.\-]*(?:\s+(?:of|for|and|the|de|la|&))?\s*)+)", query or "")
            if run and not probes:
                words = run.group(1).split()
                while words and plain(words[-1]).strip(".,") in TOWNS:
                    words.pop()
                if words:
                    probes = [" ".join(words)]
        for probe in probes:
            hit = self._probe(probe)
            if hit and (hit[1], hit[2]) not in found:
                found.append((hit[1], hit[2]))
                domains |= hit[3]
                db = hit[0]
        if found:
            return db, found, domains, True
        hay = " " + name_key(clean or query) + " "
        best = None
        for k, (kdb, oid, name, web) in self.local.items():
            if len(k) >= 5 and (" " + k + " ") in hay and distinctive(k) and (best is None or len(k) > len(best[0])):
                best = (k, kdb, oid, name, web)
        if not best and clean:
            ck = name_key(clean)
            for k, (kdb, oid, name, web) in self.local.items():
                if len(ck) >= 4 and (" " + ck + " ") in (" " + k + " ") and (best is None or len(k) < len(best[0])):
                    best = (k, kdb, oid, name, web)
        if best:
            _, kdb, oid, name, web = best
            return kdb, [(oid, name)], {web} if web else set(), True
        return self.db, ([("", clean)] if clean else []), set(), False


def parse_coverage(path: Path, index: OrgIndex | None = None) -> list[dict]:
    """Every numbered search in a coverage log (tables with a Query or Organisation column and Q-numbered bullets)."""
    index = index or org_index()
    ctx = CoverageContext(Path(path), index)
    out, seen, header = [], set(), None
    lines = ctx.text.splitlines()

    def emit(ref, query, org, outcome_text, positive):
        query = W.norm_text(query.replace("`", ""))
        key = (ref.lower(), plain(query), plain(org))
        if key in seen:
            return
        seen.add(key)
        db, pairs, domains, matched = ctx.resolve(org, query)
        outcome = classify(outcome_text, positive)
        out.append(with_orgs(index, db, pairs, date=ctx.date, run=ctx.run, agent=ctx.agent, tool="websearch", query=query, target=ctx.target,
                             outcome=outcome, found=outcome_text if outcome in ("hit", "partial") else short(outcome_text, 120),
                             source_file=rel(ctx.path), ref=ref, domains=domains, guess_org=matched))

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|"):
            if SEPARATOR_ROW.match(stripped):
                continue
            cells = _cells(stripped)
            if i + 1 < len(lines) and SEPARATOR_ROW.match(lines[i + 1].strip()):
                header = _header(cells)
                continue
            if not header or not header["valid"]:
                continue
            ref = re.sub(r"[`*]", "", cells[header["n"]]).strip() if header["n"] < len(cells) else ""
            m = REF.fullmatch(ref)
            if not m or (header["q"] is None and not ref.upper().startswith("Q")):
                continue
            query = cells[header["q"]] if header["q"] is not None and header["q"] < len(cells) else ""
            org = cells[header["o"]] if header["o"] is not None and header["o"] < len(cells) else ""
            outcome = cells[header["out"]] if header["out"] is not None and header["out"] < len(cells) else ""
            first, last, budget = int(m.group(1)), int(m.group(2) or m.group(1)), m.group(3)
            pieces = [p for p in re.split(r";\s*", query) if p.strip()] if last > first else [query]
            if last > first and len(pieces) != last - first + 1:
                pieces = [query] * (last - first + 1)
            for n, piece in zip(range(first, last + 1), pieces):
                emit(f"Q{n}" + (f"/{budget}" if budget else ""), piece, org, outcome, header["positive"])
            continue
        header = None
        m = BULLET.match(line)
        if m and ("/" in m.group(1) or line.lstrip().startswith(("-", "*", "+"))):
            query, outcome = _split_bullet(m.group(2))
            r = REF.fullmatch(m.group(1).replace(" ", ""))
            if r:
                emit(m.group(1).replace(" ", ""), query.strip().strip('"') if query.count('"') == 2 and query.strip().startswith('"')
                     and query.strip().endswith('"') else query, "", outcome, False)
    return out


# ------------------------------------------------------------------ research files
def is_gmaps(url: str) -> bool:
    return bool(re.search(r"google\.[a-z.]+/maps|maps\.google|goo\.gl/maps|maps\.app\.goo\.gl", url or ""))


def _source_outcome(s: dict) -> str:
    text = " ".join(str(s.get(k) or "") for k in ("title", "excerpt", "evidence_excerpt"))
    facts = s.get("facts") or s.get("facts_supported") or []
    if re.search(r"\b(403|429|captcha|bot check|login)\b", text, re.I):
        return "blocked"
    if re.search(r"\b404\b|not found|no contact page|does not resolve|no longer (exists|resolves)", text, re.I) or \
            (facts and all(re.match(r"\s*(no|nothing|none)\b", str(f), re.I) for f in facts)):
        return "nothing"
    return "hit" if (facts or s.get("excerpt") or s.get("evidence_excerpt")) else "unknown"


def _fetch_entries(index, path, db, pairs, sources, *, when, run, agent, target, website="", tool="webfetch", default_outcome=None):
    out = []
    for s in sources or []:
        url = str(s.get("url") or s.get("source_url") or "").strip()
        if not url.startswith("http") or s.get("fetched") is False:
            continue
        facts = s.get("facts") or s.get("facts_supported") or []
        outcome = default_outcome or _source_outcome(s)
        out.append(with_orgs(index, db, pairs, date=s.get("accessed_on") or s.get("fetched_on") or when, run=run, agent=agent,
                             tool="gmaps" if is_gmaps(url) else tool, query=url, target=target,
                             outcome=outcome, found="; ".join(map(str, facts))[:300] if facts else "", source_file=rel(path),
                             domains={website} if website else set(),
                             query_pattern='gmaps:"<org>"' if is_gmaps(url) else None))
    return out


def parse_search_file(path: Path, index: OrgIndex, covered: set | None = None) -> list[dict]:
    """A search agent's JSONL: one webfetch line per fetched source, and an unlogged-search line for each organisation whose
    searches_used the coverage log does not account for."""
    path = Path(path)
    when = file_date(path)
    run, agent = run_agent(path, when)
    target = target_of(path)
    out = []
    covered = covered or set()
    for r in jsonl(path):
        name = r.get("organisation_name") or r.get("name") or ""
        db = r.get("db") or db_default(path) or "master"
        key = index.current(db, r.get("organisation_id") or "", name)
        pairs = [(key[1] if key else "", name)]
        out += _fetch_entries(index, path, db, pairs, r.get("sources"), when=when, run=run, agent=agent, target=target,
                              website=r.get("website") or "")
        used = int(r.get("searches_used") or 0) if str(r.get("searches_used") or "0").isdigit() else 0
        if used and (key not in covered) and name_key(name) not in covered:
            out.append(with_orgs(index, db, pairs, date=when, run=run, agent=agent, tool="websearch", query="", query_pattern="<unlogged>",
                                 target=target, outcome=STATUS_OUTCOME.get(r.get("status"), "unknown"), count=used,
                                 found=(r.get("notes") or "")[:160] if r.get("status") in ("found", "partial") else "",
                                 source_file=rel(path), ref="searches_used"))
    return out


def parse_browser_file(path: Path, index: OrgIndex) -> list[dict]:
    path = Path(path)
    when = file_date(path)
    run, agent = run_agent(path, when)
    target = target_of(path)
    out = []
    for r in jsonl(path):
        name = r.get("organisation_name") or ""
        db = r.get("db") or "master"
        key = index.current(db, r.get("organisation_id") or "", name)
        pairs = [(key[1] if key else "", name)]
        accessed = next((s.get("accessed_on") for s in r.get("sources") or [] if s.get("accessed_on")), "") or text_date(r.get("notes") or "") or when
        outcome = STATUS_OUTCOME.get(r.get("status"), "unknown")
        pages = [p for p in r.get("pages_read") or [] if str(p).startswith("http")] or [r.get("website") or ""]
        for page in pages:
            if not page:
                continue
            url = page if "://" in page else "http://" + page
            out.append(with_orgs(index, db, pairs, date=accessed, run=run, agent=agent, tool="browser", query=url, target=target,
                                 outcome=outcome, found=r.get("notes") if outcome in ("blocked",) else
                                 summarise_record(r), source_file=rel(path), ref=f"robots {r.get('robots', '')}".strip(),
                                 domains={r.get("website")} if r.get("website") else set(),
                                 query_pattern=url_pattern("browser", url, [name], [r.get("website") or ""])))
    return out


def summarise_record(r: dict) -> str:
    """Counts of what a research record holds (no values): '2 emails, 1 phone, 3 people, postal address'."""
    bits = []
    for field, one, many in (("emails", "email", "emails"), ("phones", "phone", "phones"), ("people", "person", "people")):
        n = len(r.get(field) or [])
        if n:
            bits.append(f"{n} {one if n == 1 else many}")
    postal = r.get("postal_address")
    if (postal.get("value") if isinstance(postal, dict) else postal):
        bits.append("postal address")
    return ", ".join(bits) if bits else (r.get("status") or "")


def parse_hooks_file(path: Path, index: OrgIndex, covered: set | None = None) -> list[dict]:
    path = Path(path)
    when = file_date(path)
    run, agent = run_agent(path, when)
    out, covered = [], covered or set()
    for r in jsonl(path):
        name = r.get("organisation_name") or ""
        key = index.current("master", r.get("organisation_id") or "", name)
        pairs = [(key[1] if key else "", name)]
        seen = set()
        for fact in r.get("brief") or []:
            url = fact.get("source_url") or ""
            if url in seen or not url.startswith("http") or fact.get("fetched") is False:
                continue
            seen.add(url)
            out.append(with_orgs(index, "master", pairs, date=fact.get("accessed_on") or when, run=run, agent=agent, tool="webfetch", query=url,
                                 target="hook", outcome="hit", found=f"{fact.get('type', '')}: {fact.get('fact', '')}", source_file=rel(path)))
        for c in r.get("contacts") or []:
            url = c.get("source_url") or ""
            if not url.startswith("http") or url in seen:
                continue
            seen.add(url)
            out.append(with_orgs(index, "master", pairs, date=c.get("accessed_on") or when, run=run, agent=agent, tool="webfetch", query=url,
                                 target="verification", outcome=STATUS_OUTCOME.get(c.get("role_check"), "unknown"),
                                 found=f"role check {c.get('role_check', '')}", source_file=rel(path)))
        used = int(r.get("searches_used") or 0)
        if used and key not in covered and name_key(name) not in covered:
            out.append(with_orgs(index, "master", pairs, date=when, run=run, agent=agent, tool="websearch", query="", query_pattern="<unlogged>",
                                 target="hook", outcome="hit" if r.get("hook") else STATUS_OUTCOME.get(r.get("status"), "unknown"), count=used,
                                 source_file=rel(path), ref="searches_used"))
    return out


def parse_welfare_research(path: Path, index: OrgIndex) -> list[dict]:
    path = Path(path)
    when = file_date(path)
    run, agent = run_agent(path, when)
    slice_target = target_of(path)
    out = []
    for r in jsonl(path):
        kind = r.get("record_type")
        if kind == "enquiry":
            continue
        names = [r.get("organisation_name")] if r.get("organisation_name") else [n for n in (r.get("from_organisation"), r.get("to_organisation")) if n]
        pairs = []
        for n in names:
            key = index.resolve(n, "welfare")
            pairs.append((key[1] if key else "", n))
        target = {"contact": "decision-maker", "relationship": "relationship"}.get(kind, slice_target)
        out += _fetch_entries(index, path, "welfare", pairs, r.get("sources"), when=when, run=run, agent=agent, target=target,
                              website=r.get("website") or "")
    return out


def parse_introducers(path: Path, index: OrgIndex) -> list[dict]:
    path = Path(path)
    when = file_date(path)
    run, agent = run_agent(path, when)
    out = []
    for r in jsonl(path):
        key = index.resolve(r.get("name") or "", "master")
        out += _fetch_entries(index, path, "master", [(key[1] if key else "", r.get("name") or "")], r.get("sources"), when=when, run=run,
                              agent=agent, target="discovery", website=r.get("website") or "")
    return out


def parse_crawl_file(path: Path, index: OrgIndex) -> list[dict]:
    """The crawler, summarised per site per crawl file: pages read, statuses and what the pages gave (counts only)."""
    path = Path(path)
    when = file_date(path)
    out = []
    # A site whose pages carry the same hashes as in an earlier crawl file was re-extracted from the cache (--reextract), not read
    # again: it is not a new attempt (787 of the 802 sites shared by the 2026-09-23 and 2026-10-10 files).
    earlier = {}
    for other in sorted(path.parent.glob("website_contacts_*.jsonl")):
        if file_date(other) and file_date(other) < when:
            for s in jsonl(other):
                if s.get("domain"):
                    earlier[s["domain"]] = [p.get("sha256") for p in s.get("pages") or []]
    for site in jsonl(path):
        if "pages" not in site:
            continue
        pages = site.get("pages") or []
        if site.get("domain") in earlier and earlier[site["domain"]] == [p.get("sha256") for p in pages] and not site.get("deep"):
            continue
        statuses = Counter(str(p.get("status")) for p in pages)
        ok = statuses.get("200", 0)
        deep = bool(site.get("deep"))
        gave = [f"{len(site.get(f) or [])} {label}" for f, label in (("emails", "emails"), ("phones", "phones"), ("people", "people"))
                if site.get(f)]
        if not ok:
            outcome = "blocked" if any(s in statuses for s in ("403", "429", "401", "511")) or site.get("robots") == "disallowed" else "nothing"
        else:
            outcome = "hit" if gave else "nothing"
        found = f"{ok} of {len(pages)} pages read" + (f"; {', '.join(gave)}" if gave else "")
        if not ok:
            found = "; ".join((site.get("errors") or [])[:2]) or f"statuses {dict(statuses)}"
        orgs = site.get("orgs") or []
        db = orgs[0].get("db") if orgs else ""
        pairs = [(o.get("organisation_id") or "", o.get("name") or "") for o in orgs]
        e = with_orgs(index, db or "master", pairs, date=site.get("fetched_on") or when, run=f"crawl-{when}", agent="crawl_org_websites.py",
                      tool="crawler", query=site.get("start_url") or site.get("domain") or "", target="direct-email" if deep else "route",
                      outcome=outcome, found=found, source_file=rel(path), ref=f"robots {site.get('robots', '')}".strip(),
                      query_pattern="crawl:own-site(deep)" if deep else "crawl:own-site")
        out.append(e)
    return out


def _gmaps_query(row: dict) -> tuple[str, str]:
    """(query, pattern) of a Google Maps lookup: the search text when the URL keeps it, else the organisation's name."""
    url = row.get("source_url") or ""
    name = row.get("organisation_name") or row.get("name") or ""
    m = re.search(r"/maps/search/([^/?@]+)", url)
    text = unquote(m.group(1)).replace("+", " ") if m else ""
    if text and not re.fullmatch(r"[-\d., ]+", text):
        return text, 'gmaps:"' + search_pattern(text, [name]).replace('"', "") + '"'
    return name, 'gmaps:"<org>"'


def parse_gmaps_file(path: Path, index: OrgIndex) -> list[dict]:
    """The coordinator's Google Maps lookups: one line per lookup, its verdict as the outcome."""
    path = Path(path)
    when = file_date(path)
    out = []
    for n, row in enumerate(jsonl(path), 1):
        name = row.get("organisation_name") or row.get("name") or row.get("listing_name") or ""
        db = row.get("db") or ("welfare" if str(row.get("segment", "")).startswith("welfare") else "master")
        verdict = row.get("verdict") or row.get("status") or ("review" if row.get("why_review") else "accept")
        outcome = STATUS_OUTCOME.get(verdict, "unknown")
        if verdict == "not_found":
            outcome = "nothing"
        bits = []
        listing = row.get("listing_name") or row.get("google_name") or ""
        if listing:
            bits.append(f"listing '{listing}'" + (f" ({row.get('category') or row.get('google_category')})"
                                                   if row.get("category") or row.get("google_category") else ""))
        if row.get("latitude") is not None and outcome != "nothing":
            bits.append("pin")
        if row.get("phone"):
            bits.append("phone listed")
        if row.get("website"):
            bits.append("website listed")
        address = row.get("address") or ""
        if address and not re.fullmatch(r"[A-Z0-9]{4}\+[A-Z0-9]{2,3},?\s*\w*(, Tanzania)?", address.strip()):
            bits.append("street address")
        note = row.get("note") or row.get("why_review") or ""
        if outcome in ("nothing", "partial") and note:
            bits.append(note)
        query, pattern = _gmaps_query(row)
        key = index.current(db, row.get("organisation_id") or "", name)
        out.append(with_orgs(index, db, [(key[1] if key else "", name)], date=row.get("fetched_on") or row.get("fetched") or when,
                             run=f"gmaps-{when}", agent="coordinator", tool="gmaps", query=query, query_pattern=pattern,
                             target="location", outcome=outcome, found="; ".join(bits), source_file=rel(path), ref=f"line {n}",
                             segment=row.get("kind") or row.get("proposed_subsegment") or ""))
    return out


GEOCODE_TOOL = {"Google Maps listing": "gmaps", "Google Maps search": "gmaps", "OpenStreetMap": "overpass", "Nominatim": "nominatim",
                "own site embed": "crawler", "own site text + repository gazetteer": "crawler", "official site": "webfetch"}


def parse_geocode_file(path: Path, index: OrgIndex) -> list[dict]:
    path = Path(path)
    when = file_date(path)
    out = []
    for n, row in enumerate(jsonl(path), 1):
        tool = GEOCODE_TOOL.get(row.get("source_type") or "", "other")
        name = row.get("organisation_name") or ""
        db = row.get("db") or "master"
        status = row.get("status") or ""
        url = row.get("source_url") or ""
        pattern = {"gmaps": 'gmaps:"<org>"', "overpass": "osm:name-candidates", "nominatim": "nominatim:street-address",
                   "crawler": "crawl:own-site/map-embed", "webfetch": url_pattern("webfetch", url, [name]) if url else "fetch",
                   "other": "geocode:collect_geocodes"}[tool]
        key = index.current(db, row.get("organisation_id") or "", name)
        out.append(with_orgs(index, db, [(key[1] if key else "", name)], date=row.get("fetched_on") or when, run=f"geocode-{when}",
                             agent="coordinator" if "user51" in path.name else "collect_geocodes.py", tool=tool, query=url or name,
                             query_pattern=pattern, target="location", outcome=STATUS_OUTCOME.get(status, "nothing" if status == "not_found" else "unknown"),
                             found=f"{status}" + (f", precision {row.get('precision')}" if row.get("precision") else ""), source_file=rel(path),
                             ref=f"line {n}"))
    return out


def parse_targeted(path: Path, index: OrgIndex) -> list[dict]:
    """The gap census's targeted directory records: the official pages read for each new candidate."""
    path = Path(path)
    when = file_date(path)
    out = []
    for r in jsonl(path):
        name = r.get("name") or r.get("organisation_name") or ""
        evidence = [{"url": e.get("url"), "fetched": e.get("fetched"), "accessed_on": e.get("fetched_on"), "excerpt": e.get("excerpt")}
                    for e in r.get("evidence") or []]
        db = "welfare" if str(r.get("segment", "")).lower().startswith("welfare") else "master"
        key = index.resolve(name, db)
        out += _fetch_entries(index, path, db, [(key[1] if key else "", name)], evidence, when=when, run=f"gap-census-{when}",
                              agent="gap-census", target="discovery", website=r.get("website") or "")
    return out


def parse_collector(path: Path, index: OrgIndex) -> list[dict]:
    """One summary line per deterministic collection run (Overpass, the NGO register, the council API, census, Wikipedia)."""
    path = Path(path)
    when = file_date(path)
    name = path.name
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        data = None
    size = len(data.get("elements") or data.get("features") or data.get("items") or data.get("records") or []) if isinstance(data, dict) \
        else (len(data) if isinstance(data, list) else 0)
    stamp = (data.get("retrieved") or data.get("fetched_on")) if isinstance(data, dict) else None
    if isinstance(stamp, str) and ISO.match(stamp[:10]):
        when = stamp[:10]
    if name.startswith("osm_contacts"):
        tool, query, pattern, target = "overpass", "OpenStreetMap contact tags (phone, email, website) in the catchment", "osm:contact-tags", "route"
    elif "council_sites" in path.parts:
        host = name.split("_")[0]
        tool, query, pattern, target = "council-api", f"https://{host}/api/ (profiles, statistics, footer, menus, pages, files, news)", "council-api:all", "decision-maker"
    elif name.startswith("nis_catchment_profiles"):
        tool, query, pattern, target = "ngo-register", "https://nis.jamii.go.tz/ngo_profile/<id> (catchment)", "register:profiles", "discovery"
        size = sum(1 for _ in jsonl(path))
    elif name.startswith("nis_catchment"):
        tool, query, pattern, target = "ngo-register", "https://nis.jamii.go.tz/mapping (catchment)", "register:map", "discovery"
    elif name.startswith("osm_welfare"):
        q = path.with_suffix(".query.txt")
        tool, query, pattern, target = "overpass", (q.read_text(encoding="utf-8").strip()[:300] if q.exists() else name), "osm:welfare", "discovery"
    elif name.startswith("wikipedia"):
        tool, query, pattern, target = "other", "Wikipedia API: ward articles and coordinates", "wikipedia:wards", "location"
    elif name.startswith("nbs_"):
        tool, query, pattern, target = "other", "NBS 2022 census administrative-units report, volume 1b", "census:report", "location"
    elif name.startswith("osm_"):
        category = re.sub(r"_\d{4}-\d{2}-\d{2}.*$", "", name[4:])
        tool, query, pattern = "overpass", f"OpenStreetMap {category.replace('_', ' ')} in the catchment", f"osm:{category}"
        target = "location" if "government" in path.parts or "government-research" in str(path) else "discovery"
    else:
        return []
    if tool == "council-api" and isinstance(data, dict) and data:
        size = size or sum(len(v) if isinstance(v, (list, dict)) else 1 for v in data.values())
    run = f"{area_of(path)}-collect-{when}"
    return [entry(date=when, run=run, agent="collector", tool=tool, db=db_default(path), query=query, query_pattern=pattern, target=target,
                  outcome="hit" if size else "unknown", found=f"{size} records" if size else "", source_file=rel(path), ref="collector")]


def parse_pending(path: Path, index: OrgIndex) -> list[dict]:
    """A ledger-format JSONL (an agent's pending file): validated, patterns derived where missing, IDs given on writing."""
    out = []
    for r in jsonl(path):
        if "tool" not in r:
            continue
        pairs = list(zip(r.get("organisation_ids") or [], (r.get("organisation_names") or []) + [""] * 20)) or \
            [("", n) for n in r.get("organisation_names") or []]
        kw = {k: r.get(k) for k in FIELDS if k not in ("id", "organisation_ids", "organisation_names", "db")}
        kw["source_file"] = kw.get("source_file") or rel(path)
        out.append(with_orgs(index, r.get("db") or "", pairs, **{k: v for k, v in kw.items() if v not in (None, "")}))
    return out


# ------------------------------------------------------------------ ingest and backfill
SKIPPED_DERIVED = {
    "browser_googlemaps_": "derived from the Google Maps lookup files by import_google_maps_lookups.py (ingested from the lookups)",
    "research_W_contact_profiles_": "an export of the contact profiles for the welfare pipeline, not research",
    "website_direct_": "offline extraction from cached pages (no network)",
    "osm_matches_": "derived from the Google Maps lookups",
    "geocodes_gap_census_": "points derived from the gap census's OpenStreetMap collection",
    "geocodes_corrections_": "corrections derived from the Google Maps lookups (ingested from the lookups)",
    "geocodes_gmaps_": "points derived from the Google Maps lookups (ingested from the lookups; covers geocodes_gmaps_newleads_)",
    "geocodes_unplaced14_": "points derived from the Google Maps lookups of 11 October 2026 (ingested from the lookups)",
    "geocodes_pointfix_": "points from the 13 October 2026 point fix, whose attempts were ingested from its pending ledger file",
}


def kind_of(path: Path) -> str:
    name, parts = path.name, path.parts
    for prefix in SKIPPED_DERIVED:
        if name.startswith(prefix):
            return "skip"
    if name.endswith(".md"):
        if name.startswith("browser_") or name in ("MANIFEST.md", "README.md"):
            return "skip"
        return "coverage" if "coverage" in name else "skip"
    if path.suffix == ".jsonl":
        first = next(jsonl(path), {}) or {}
        if "tool" in first and "query_pattern" in first:
            return "pending"
        if name.startswith("nis_catchment"):
            return "collector"
        if name.startswith("search_"):
            return "search"
        if name.startswith("browser_"):
            return "browser"
        if name.startswith("hooks_"):
            return "hooks"
        if name.startswith("research_targeted"):
            return "targeted"
        if name.startswith("research_GC_"):
            return "welfare"
        if name.startswith("research_"):
            return "welfare"
        if name.startswith("introducers_"):
            return "introducers"
        if name.startswith("website_contacts_"):
            return "crawl"
        if name.startswith(("google_maps_", "geocodes_google_", "google_review_")):
            return "gmaps"
        if name.startswith("geocodes_"):
            return "geocode"
        return "skip"
    if path.suffix == ".json":
        if name.startswith(("osm_", "nis_catchment", "wikipedia_", "nbs_")) or "council_sites" in parts:
            return "collector"
    if name.startswith("nis_catchment_profiles"):
        return "collector"
    return "skip"


def parse_file(path: Path, index: OrgIndex, covered: dict | None = None) -> list[dict]:
    kind = kind_of(Path(path))
    covered = covered or {}
    parsers = {"coverage": lambda p: parse_coverage(p, index), "search": lambda p: parse_search_file(p, index, covered.get(p.name)),
               "browser": lambda p: parse_browser_file(p, index), "hooks": lambda p: parse_hooks_file(p, index, covered.get(p.name)),
               "welfare": lambda p: parse_welfare_research(p, index), "introducers": lambda p: parse_introducers(p, index),
               "crawl": lambda p: parse_crawl_file(p, index), "gmaps": lambda p: parse_gmaps_file(p, index),
               "geocode": lambda p: parse_geocode_file(p, index), "targeted": lambda p: parse_targeted(p, index),
               "collector": lambda p: parse_collector(p, index), "pending": lambda p: parse_pending(p, index)}
    return parsers[kind](Path(path)) if kind in parsers else []


def ingest(paths, ledger: Path = LEDGER, index: OrgIndex | None = None, dry_run: bool = False) -> dict:
    """Fold files into the ledger: pending files first, then coverage logs (which tell the research files which organisations'
    searches are already logged), then everything else. Returns counts per file."""
    index = index or org_index()
    paths = [Path(p) for p in paths]
    order = {"pending": 0, "coverage": 1}
    paths.sort(key=lambda p: (order.get(kind_of(p), 2), str(p)))
    covered: dict[str, set] = defaultdict(set)
    new, report = [], {}
    for p in paths:
        kind = kind_of(p)
        if kind == "skip":
            why = next((why for pre, why in SKIPPED_DERIVED.items() if p.name.startswith(pre)), None) or \
                ("a browser pass log: its browser_*.jsonl records the same pages, one line per organisation" if p.name.startswith("browser_")
                 else "not a research record")
            report[rel(p)] = {"kind": "skipped", "lines": 0, "why": why}
            continue
        entries = parse_file(p, index, covered)
        if kind in ("coverage", "pending"):
            paired = pair_research_file(p) if kind == "coverage" else None
            for e in entries:
                if e["tool"] != "websearch":
                    continue
                for oid in e["organisation_ids"]:
                    for target in ([paired.name] if paired else []) + [Path(e.get("source_file", "")).name]:
                        covered[target].add((e["db"], oid))
                for n in e["organisation_names"]:
                    for target in ([paired.name] if paired else []):
                        covered[target].add(name_key(n))
        report[rel(p)] = {"kind": kind, "lines": len(entries)}
        new += entries
    new.sort(key=lambda e: (e["date"], e["run"], e["agent"], e["source_file"]))
    if dry_run:
        existing = load(ledger)
        seen = {dedupe_key(e) for e in existing}
        added = len({dedupe_key(e) for e in new} - seen)
        return {"files": report, "would_add": added, "parsed": len(new)}
    added, skipped = write(new, ledger)
    return {"files": report, "added": added, "already_present": skipped, "parsed": len(new)}


def backfill_paths() -> list[Path]:
    globs = ["contact-research/coverage/*.md", "contact-research/search_*.jsonl", "contact-research/browser_*.jsonl",
             "contact-research/introducers_*.jsonl", "contact-research/website_contacts_*.jsonl", "contact-research/osm_contacts_*.json",
             "welfare-research/coverage/*.md", "welfare-research/research_*.jsonl", "welfare-research/nis_catchment*",
             "welfare-research/osm_welfare_*.json", "hook-research/coverage/*.md", "hook-research/hooks_*.jsonl",
             "gap-census/*coverage*.md", "gap-census/google_maps_*.jsonl", "gap-census/research_*.jsonl", "gap-census/osm_*_*.json",
             "geocode-research/*coverage*.md", "geocode-research/*.jsonl", "government-research/*coverage*.md",
             "government-research/council_sites/*.json", "government-research/osm_*.json", "government-research/wikipedia_*.json",
             "government-research/nbs_*.json", "contact-research/browser_googlemaps_*.jsonl", "contact-research/website_direct_*.jsonl",
             "vicoba-research/research_*.jsonl", "vicoba-research/osm_*.json"]  # the VICOBA coverage log repeats its research file
    seen, out = set(), []
    for g in globs:
        for p in sorted(RAW.glob(g)):
            if p not in seen and not p.name.startswith("geocodes_gap_census") and p.suffix != ".txt":
                seen.add(p)
                out.append(p)
    return out


# ------------------------------------------------------------------ what was tried (planners)
class Tried:
    """What the ledger records for each organisation, as of a plan date. Attempts older than the retry window, and attempts
    never made (refused-cap, skipped), do not use up a pattern."""

    def __init__(self, entries=None, as_of: str | None = None, retry_days: int = DEFAULT_RETRY_DAYS):
        self.entries = load() if entries is None else entries
        self.as_of = as_of or date.today().isoformat()
        self.retry_days = retry_days
        self.cutoff = (date.fromisoformat(self.as_of) - timedelta(days=retry_days)).isoformat()
        self.by_id: dict[tuple, list] = defaultdict(list)
        self.by_name: dict[str, list] = defaultdict(list)
        for e in self.entries:
            if e.get("date", "") > self.as_of:
                continue
            for oid in e.get("organisation_ids") or []:
                self.by_id[(e.get("db") or "", oid)].append(e)
            if not e.get("organisation_ids"):
                for n in e.get("organisation_names") or []:
                    if name_key(n):
                        self.by_name[name_key(n)].append(e)

    def attempts(self, db: str, oid: str, name: str = "") -> list[dict]:
        found = list(self.by_id.get((db, oid), [])) + list(self.by_id.get(("", oid), []))
        if name:
            found += self.by_name.get(name_key(name), [])
        return sorted(found, key=lambda e: (e.get("date", ""), e.get("id", "")))

    def families(self, db, oid, name="", fresh_only=True) -> dict:
        """{family: {"date": latest, "outcomes": Counter, "count": n, "patterns": set}} for attempts actually made."""
        out = {}
        for e in self.attempts(db, oid, name):
            if e.get("outcome") in NOT_MADE or (fresh_only and e.get("date", "") < self.cutoff):
                continue
            fam = family_of(e["tool"], e.get("query_pattern", ""))
            f = out.setdefault(fam, {"date": "", "outcomes": Counter(), "count": 0, "patterns": set()})
            f["date"] = max(f["date"], e.get("date", ""))
            f["outcomes"][e.get("outcome", "unknown")] += 1
            f["count"] += int(e.get("count") or 1)
            f["patterns"].add(e.get("query_pattern", ""))
        return out

    def open_families(self, db, oid, name="", target="routes", has_domain=True, named=True) -> list[str]:
        key = target if target != "direct-email" or named else "direct-email-unnamed"
        wanted = [f for f in SEARCH_FAMILIES.get(key, ()) if has_domain or f not in NEEDS_DOMAIN]
        used = {FAMILY_ALIASES.get(f, f) for f in self.families(db, oid, name)}
        return [f for f in wanted if f not in used]

    def exhausted(self, db, oid, name="", target="routes", has_domain=True, named=True) -> bool:
        key = target if target != "direct-email" or named else "direct-email-unnamed"
        wanted = [f for f in SEARCH_FAMILIES.get(key, ()) if has_domain or f not in NEEDS_DOMAIN]
        return bool(wanted) and not self.open_families(db, oid, name, target, has_domain, named)

    def used_share(self, db, oid, name="", target="routes", has_domain=True, named=True) -> float:
        key = target if target != "direct-email" or named else "direct-email-unnamed"
        wanted = [f for f in SEARCH_FAMILIES.get(key, ()) if has_domain or f not in NEEDS_DOMAIN]
        return 1 - len(self.open_families(db, oid, name, target, has_domain, named)) / len(wanted) if wanted else 0.0

    def summary(self, db, oid, name="", max_items=5, max_chars=220) -> list[str]:
        """Compact 'tried' items: searches first (one per pattern), then page reads, crawls and map lookups grouped by family, newest
        first within each: 'search site:<domain> "<person>" 10-11 nothing x2', 'crawl-deep 10-11 hit'."""
        groups = {}
        for e in self.attempts(db, oid, name):
            if e.get("outcome") in NOT_MADE:
                continue
            tool = e["tool"]
            label = ("search " + e.get("query_pattern", "")) if tool == "websearch" else family_of(tool, e.get("query_pattern", ""))
            g = groups.setdefault((tool, label), {"date": "", "outcomes": Counter()})
            g["date"] = max(g["date"], e.get("date", ""))
            g["outcomes"][e.get("outcome", "unknown")] += int(e.get("count") or 1)
        items = []
        for (tool, label), g in sorted(groups.items(), key=lambda kv: (kv[0][0] == "websearch", kv[1]["date"]), reverse=True):
            best = ", ".join(f"{o}{' x' + str(n) if n > 1 else ''}" for o, n in g["outcomes"].most_common(2))
            stale = " may retry" if g["date"] < self.cutoff else ""
            items.append(f"{label} {g['date'][5:]} {best}{stale}")
        out, length = [], 0
        for item in items[:max_items]:
            if length + len(item) > max_chars and out:
                break
            out.append(item)
            length += len(item) + 2
        if len(items) > len(out):
            out.append(f"+{len(items) - len(out)} more (ledger.py tried --org {oid or name_key(name)})")
        return out


# ------------------------------------------------------------------ check and stats
def check(path: Path = LEDGER) -> dict:
    problems, ids, keys = [], set(), Counter()
    entries = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            problems.append(f"line {n}: empty")
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError as err:
            problems.append(f"line {n}: not JSON ({err})")
            continue
        entries.append(e)
        missing = [f for f in FIELDS if f not in e]
        extra = [f for f in e if f not in FIELDS]
        if missing or extra:
            problems.append(f"line {n}: missing {missing} extra {extra}")
        if not re.fullmatch(r"RL\d{6,}", str(e.get("id", ""))) or e.get("id") in ids:
            problems.append(f"line {n}: bad or repeated id {e.get('id')}")
        ids.add(e.get("id"))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("date", ""))):
            problems.append(f"line {n}: bad date {e.get('date')!r}")
        for field, allowed in (("tool", TOOLS), ("target", TARGETS), ("outcome", OUTCOMES), ("db", DBS)):
            if e.get(field) not in allowed:
                problems.append(f"line {n}: {field} {e.get(field)!r} not in {allowed}")
        if not isinstance(e.get("organisation_ids"), list) or not isinstance(e.get("organisation_names"), list):
            problems.append(f"line {n}: organisation_ids and organisation_names must be lists")
        if EMAIL.search(str(e.get("found", ""))) or (redact(str(e.get("found", ""))) != str(e.get("found", ""))):
            problems.append(f"line {n}: found holds an email address or phone number")
        if not e.get("query_pattern"):
            problems.append(f"line {n}: empty query_pattern")
        keys[dedupe_key(e)] += 1
    dupes = {k: v for k, v in keys.items() if v > 1}
    return {"lines": len(entries), "problems": problems[:50], "problem_count": len(problems), "duplicates": len(dupes),
            "duplicate_examples": [list(map(str, k)) for k in list(dupes)[:5]]}


GROUPS = (("introducer", r"^introducer"), ("bank or finance", r"\bbank|microfinance|\bsacco|insurance|financial|capital\b|mf bank"),
          ("hotel or lodge", r"hotel|lodge|\bcamps?\b|resort|\binn\b|guest ?house|hostel|villa|tented|retreat|tourism:"),
          ("health", r"hospital|clinic|medical|dispensary|health|polyclinic|pharma|amenity:(clinic|hospital|doctors)"),
          ("education", r"school|college|universit|institute|academy|amenity:(college|university|school)"),
          ("international organisation", r"international organisation|united nations|\bun\b|court|east african|tribunal|\beac\b|union\b|unicef|\.int\b"),
          ("farm or estate", r"farm|estate|flower|coffee|seed|plantation|horticult"),
          ("safari or tour operator", r"safari|tours?\b|travel|adventure|expedition|trek|climb|kilimanjaro|tato|guide"),
          ("ngo", r"\bngo\b|foundation|office:ngo|trust\b|charity|mission"),
          ("manufacturing or industry", r"industr|manufactur|factory|mill|brewer|cement|steel|engineering|construction"))


def segment_group(e: dict) -> str:
    """A coarse kind for stats: the welfare and government runs' own segments; for the company master, which files many
    employers under 'Safari / tour operator' from the TATO import, a kind read from the name first, then the segment."""
    db, seg = e.get("db") or "", e.get("segment") or ""
    if db == "welfare":
        return "welfare: " + (re.sub(r"^Welfare ", "", seg) if seg else "segment unknown")
    if db == "government":
        return f"government: {seg}" if seg else "government"
    if not e.get("organisation_ids") and not e.get("organisation_names"):
        return "(no organisation)"
    text = " ".join(e.get("organisation_names") or []).lower()
    if seg.lower().startswith("introducer"):
        return "master: introducer"
    for label, rx in GROUPS:
        if re.search(rx, text):
            return f"master: {label}"
    for label, rx in GROUPS:
        if re.search(rx, seg.lower()):
            return f"master: {label}"
    return "master: other employer" if db == "master" else "(unknown)"


def yield_table(entries, by: str) -> list[dict]:
    groups = defaultdict(Counter)
    for e in entries:
        if by == "family":
            k = f"{e['tool']}:{family_of(e['tool'], e.get('query_pattern', ''))}"
        elif by == "pattern":
            k = f"{e['tool']}:{e.get('query_pattern', '')}"
        elif by == "segment":
            k = segment_group(e)
        else:
            k = e.get(by) or "(none)"
        c = groups[k]
        n = int(e.get("count") or 1)
        c["attempts"] += n
        c[e.get("outcome", "unknown")] += n
        c["lines"] += 1
    rows = []
    for k, c in groups.items():
        made = c["attempts"] - c["refused-cap"] - c["skipped"]
        judged = made - c["unknown"]
        rows.append({by: k, "lines": c["lines"], "attempts": c["attempts"], "hit": c["hit"], "partial": c["partial"], "nothing": c["nothing"],
                     "blocked": c["blocked"], "refused": c["refused-cap"], "unknown": c["unknown"],
                     "yield": round((c["hit"] + c["partial"]) / judged, 2) if judged else None,
                     "hit_rate": round(c["hit"] / judged, 2) if judged else None})
    return sorted(rows, key=lambda r: -r["attempts"])


def print_table(rows, by, limit=0):
    if not rows:
        print("(nothing)")
        return
    cols = [by, "lines", "attempts", "hit", "partial", "nothing", "blocked", "refused", "unknown", "yield", "hit_rate"]
    width = min(70, max(len(str(r[by])) for r in rows))
    print(f"{by:<{width}}  " + " ".join(f"{c:>8}" for c in cols[1:]))
    for r in rows[:limit or None]:
        print(f"{str(r[by])[:width]:<{width}}  " + " ".join(f"{('' if r[c] is None else r[c])!s:>8}" for c in cols[1:]))


# ------------------------------------------------------------------ CLI
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ledger", type=Path, default=LEDGER, help="the ledger file (default: the committed one)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("append", help="append one attempt")
    a.add_argument("--file", type=Path, help="write to this file instead of the ledger (an agent's pending file)")
    a.add_argument("--date", default=date.today().isoformat())
    a.add_argument("--run", default="")
    a.add_argument("--agent", default="coordinator")
    a.add_argument("--tool", required=True, choices=TOOLS)
    a.add_argument("--db", default="", choices=DBS)
    a.add_argument("--org", action="append", default=[], help="organisation ID (repeatable)")
    a.add_argument("--org-name", action="append", default=[], help="organisation name (repeatable; in the same order as --org)")
    a.add_argument("--query", default="", help="the exact query, or the URL read")
    a.add_argument("--pattern", default="", help="query pattern; derived from the query when left out")
    a.add_argument("--domain", action="append", default=[], help="the organisation's own domain, to derive the pattern")
    a.add_argument("--target", default="unknown", choices=TARGETS)
    a.add_argument("--outcome", required=True, choices=OUTCOMES)
    a.add_argument("--found", default="", help="a short factual summary; addresses and numbers are removed")
    a.add_argument("--source-file", default="", help="the research file or coverage log the attempt is recorded in")
    a.add_argument("--ref", default="", help="Q<n>/<budget>, a line number, ...")
    a.add_argument("--count", type=int, default=1)

    i = sub.add_parser("ingest", help="fold coverage logs, research files, lookup files or pending files into the ledger")
    i.add_argument("paths", nargs="+", type=Path)
    i.add_argument("--dry-run", action="store_true")

    b = sub.add_parser("backfill", help="ingest every research file already in the repository (idempotent)")
    b.add_argument("--dry-run", action="store_true")

    t = sub.add_parser("tried", help="what was already tried for an organisation or a pattern")
    t.add_argument("--org", help="organisation ID")
    t.add_argument("--name", help="organisation name (matched by name key)")
    t.add_argument("--db", default="")
    t.add_argument("--pattern", help="text in the query pattern or family (for example at-domain, vacancy, site:<domain>)")
    t.add_argument("--target", choices=TARGETS)
    t.add_argument("--tool", choices=TOOLS)
    t.add_argument("--since", default="", help="only attempts on or after this date")
    t.add_argument("--json", action="store_true")
    t.add_argument("--limit", type=int, default=60)

    s = sub.add_parser("stats", help="attempts and yield")
    s.add_argument("--by", action="append", choices=("tool", "family", "pattern", "target", "segment", "date", "run", "outcome", "db"),
                   help="group by (repeatable; default tool, family and target)")
    s.add_argument("--tool", choices=TOOLS)
    s.add_argument("--target", choices=TARGETS)
    s.add_argument("--db", choices=DBS)
    s.add_argument("--limit", type=int, default=40)
    s.add_argument("--json", action="store_true")

    sub.add_parser("check", help="validate the ledger and report duplicates")
    args = parser.parse_args()

    if args.cmd == "append":
        index = org_index()
        pairs = list(zip(args.org, args.org_name + [""] * len(args.org))) + [("", n) for n in args.org_name[len(args.org):]]
        e = with_orgs(index, args.db, pairs, date=args.date, run=args.run or f"{args.agent}-{args.date}", agent=args.agent, tool=args.tool,
                      query=args.query, query_pattern=args.pattern or None, target=args.target, outcome=args.outcome, found=args.found,
                      source_file=args.source_file, ref=args.ref, count=args.count, domains=set(args.domain))
        added, skipped = write([e], args.file or args.ledger)
        print(json.dumps({"added": added, "already_present": skipped, "query_pattern": e["query_pattern"],
                          "family": family_of(e["tool"], e["query_pattern"])}))
        return 0
    if args.cmd in ("ingest", "backfill"):
        paths = args.paths if args.cmd == "ingest" else backfill_paths()
        result = ingest(paths, args.ledger, dry_run=args.dry_run)
        by_kind = Counter()
        for f in result["files"].values():
            by_kind[f["kind"]] += f["lines"]
        print(json.dumps({k: v for k, v in result.items() if k != "files"} | {"lines_by_kind": dict(by_kind), "files": len(result["files"])},
                         indent=1))
        if args.cmd == "ingest" or args.dry_run:
            for f, r in result["files"].items():
                print(f"  {r['kind']:<11} {r['lines']:>6}  {f}" + (f"  ({r['why']})" if r.get("why") else ""))
        return 0
    entries = load(args.ledger)
    if args.cmd == "check":
        result = check(args.ledger)
        print(json.dumps(result, indent=1))
        return 1 if result["problem_count"] or result["duplicates"] else 0
    if args.cmd == "tried":
        rows = entries
        if args.org or args.name:
            index = org_index()
            key = next((k for k in index.info if k[1] == args.org and (not args.db or k[0] == args.db)), None) if args.org else \
                index.resolve(args.name, args.db or None)
            db = (key[0] if key else args.db) or ""
            name = args.name or (index.info.get(key, {}).get("name", "") if key else "")
            rows = Tried(rows, as_of="9999-12-31").attempts(db, args.org or (key[1] if key else ""), name)
        if args.pattern:
            needle = args.pattern.lower()
            rows = [e for e in rows if needle in e.get("query_pattern", "").lower() or needle in family_of(e["tool"], e.get("query_pattern", ""))]
        rows = [e for e in rows if (not args.target or e.get("target") == args.target) and (not args.tool or e["tool"] == args.tool)
                and e.get("date", "") >= args.since and (not args.db or e.get("db") == args.db)]
        if args.json:
            print(json.dumps(rows[-args.limit:], ensure_ascii=False, indent=1))
            return 0
        if args.pattern and not (args.org or args.name):
            per_org = Counter((e.get("db"), ", ".join(e.get("organisation_names") or e.get("organisation_ids") or ["(none)"])) for e in rows)
            outcomes = Counter(e.get("outcome") for e in rows)
            print(f"{len(rows)} attempts, outcomes {dict(outcomes)}; organisations: {len(per_org)}")
            for (db, org), n in per_org.most_common(args.limit):
                print(f"  {n:>3}  {db or '-':<10} {org[:90]}")
            return 0
        print(f"{len(rows)} attempts")
        for e in rows[-args.limit:]:
            print(f"  {e['date']} {e['tool']:<9} {family_of(e['tool'], e.get('query_pattern', '')):<16} {e.get('outcome', ''):<8} "
                  f"{e.get('query_pattern', '')[:50]:<50} | {e.get('query', '')[:70]} [{e.get('ref', '')}; {e.get('source_file', '')}]")
        return 0
    if args.cmd == "stats":
        rows = [e for e in entries if (not args.tool or e["tool"] == args.tool) and (not args.target or e.get("target") == args.target)
                and (args.db is None or e.get("db") == args.db)]
        result = {}
        for by in args.by or ["tool", "family", "target"]:
            result[by] = yield_table(rows, by)
            if not args.json:
                print(f"\n## by {by}")
                print_table(result[by], by, args.limit)
        if args.json:
            print(json.dumps(result, indent=1))
        else:
            print(f"\n{len(rows)} lines, {sum(int(e.get('count') or 1) for e in rows)} attempts. yield = (hit + partial) / attempts judged "
                  "(refused, skipped and unknown left out); hit_rate = hit / attempts judged.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
