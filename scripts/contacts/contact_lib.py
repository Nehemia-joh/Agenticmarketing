"""Shared helpers for organisation contact research (scripts/contacts/).

A polite fetcher for organisations' own websites (robots.txt Disallow rules honoured, one request at a time per site, cached under
runtime/contacts/http-cache/, never committed) and extractors for what a site publishes for contact purposes:
emails, phone numbers, official social pages, postal addresses and named people with their roles.

Privacy rules (AGENTS.md, skills/silverleaf-welfare-leads/references/welfare-data-contract.md):
- Only what the organisation publishes on its own site is recorded; no person is searched across other sites.
- Page text is not stored, only the extracted facts, the page URL and the page's SHA-256.
- Personal LinkedIn profiles, photos and biographies are never kept.
- Every person carries pdpa_risk: medium for a name and role the organisation publishes, risky for a
  personal-domain email linked to a named person.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import re
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "skills").is_dir():
            return parent
    raise SystemExit("Could not find the repository root (a folder containing AGENTS.md and skills/).")


ROOT = _repo_root()
sys.path.insert(0, str(ROOT / "scripts" / "welfare"))
import welfare_lib as W  # noqa: E402  (per-host spacing, normalisation)

RAW = ROOT / "data" / "raw" / "contact-research"
WORK = ROOT / "runtime" / "contacts"
CACHE = WORK / "http-cache"
USER_AGENT = "silverleaf-lead-research/1.0 (contact research; rate-limited; honours robots.txt)"
SITE_INTERVAL = 1.5          # seconds between requests to one site
MAX_PAGES = 6                # home page plus up to five contact, about or team pages
MAX_BYTES = 2_000_000
TIMEOUT = 25
SOCIAL_HOSTS = ("facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "youtube.com", "tiktok.com", "wa.me",
                "api.whatsapp.com", "tripadvisor.", "wixsite.com", "blogspot.", "wordpress.com", "sites.google.com", "google.com")
SOCIAL_MAP = {"facebook.com": "facebook", "instagram.com": "instagram", "linkedin.com": "linkedin", "twitter.com": "twitter", "x.com": "twitter",
              "youtube.com": "youtube", "tiktok.com": "tiktok", "wa.me": "whatsapp", "api.whatsapp.com": "whatsapp"}
PAGE_KINDS = [("contact", r"contact|mawasiliano|get-in-touch|reach-us|find-us|location"),
              ("team", r"team|staff|people|leadership|management|board|trustee|director|founder|uongozi|who-we-are|our-story|meet"),
              ("about", r"about|kuhusu|history|story|organisation|organization|profile")]
LINK_SCORE = {"contact": 5, "team": 4, "about": 3}


# ------------------------------------------------------------------ fetching
def _cache_paths(url: str):
    key = hashlib.sha256(url.encode()).hexdigest()
    return CACHE / f"{key}.bin", CACHE / f"{key}.json"


def fetch(url: str, retries: int = 2) -> dict:
    """GET with per-site spacing, retries on 429/5xx, redirect capture and a disk cache. Never bypasses a block."""
    body_path, meta_path = _cache_paths(url)
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        try:
            meta["body"] = body_path.read_bytes() if body_path.exists() else b""
        except OSError as exc:
            # The local system refuses to open the saved page (usually antivirus blocking a compromised site's content).
            # It is treated as unreadable and never used.
            return {**meta, "status": None, "error": f"saved copy unreadable ({type(exc).__name__}); not used", "body": b""}
        return meta
    CACHE.mkdir(parents=True, exist_ok=True)
    host = urlsplit(url).netloc.lower()
    W.HOST_LIMITS.setdefault(host, {"min_interval": SITE_INTERVAL, "max_workers": 1, "timeout": TIMEOUT})
    meta = {"url": url, "final_url": url, "status": None, "content_type": "", "error": ""}
    body = b""
    for attempt in range(retries + 1):
        W._wait_turn(host)
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                meta.update(status=response.status, final_url=response.geturl(), content_type=response.headers.get("Content-Type", ""))
                body = response.read(MAX_BYTES)
            break
        except urllib.error.HTTPError as exc:
            meta.update(status=exc.code, error=f"HTTP {exc.code}")
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                break
            retry_after = exc.headers.get("Retry-After", "")
            time.sleep(float(retry_after) if retry_after.isdigit() else 4 * (2 ** attempt))
        except (urllib.error.URLError, TimeoutError, ConnectionError, socket.timeout, ValueError, OSError, http.client.HTTPException) as exc:
            meta.update(error=f"{type(exc).__name__}: {str(exc)[:120]}")
            if attempt == retries:
                break
            time.sleep(3 * (2 ** attempt))
    # HTTP answers (including 4xx and 5xx) are cached; a network failure (DNS, timeout, reset, certificate) is not, so a
    # later run retries it instead of treating a passing fault as permanent. Writes are atomic, since workers crawling
    # different sites can reach the same host (a redirect target) at once.
    if meta["status"] is not None:
        for path, data in ((body_path, body), (meta_path, json.dumps(meta).encode("utf-8"))):
            temp = path.with_name(f"{path.name}.{threading.get_ident()}.tmp")
            temp.write_bytes(data)
            temp.replace(path)
    meta["body"] = body
    return meta


def robots_state(base: str) -> tuple[RobotFileParser | None, str]:
    """(rules, state) for one scheme and host. State 'rules': a robots.txt was read and its Disallow rules apply; 'none':
    it answered 4xx, so there are no rules; 'unreachable': a server error (5xx) or a network or certificate failure.
    By the user's decision (23 September 2026) an unreachable robots.txt does not stop the crawl: the site is crawled
    and its findings are flagged ('robots.txt unreachable') for a person to check. Explicit Disallow rules always apply."""
    parser = RobotFileParser()
    result = fetch(urljoin(base, "/robots.txt"), retries=1)
    status = result["status"]
    if status == 200:
        parser.parse(result["body"].decode("utf-8", "replace").splitlines())
        return parser, "rules"
    if status is not None and 400 <= status < 500:
        return None, "none"
    return None, "unreachable"


def robots_for(base: str) -> RobotFileParser | None:
    return robots_state(base)[0]


def is_phone(value) -> bool:
    """A value with a phone number in it (at least seven digits), not a directory category code such as 'TO/DMC/MAIN'."""
    return len(re.sub(r"\D", "", str(value or ""))) >= 7


def site_base(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}/"


def allowed(parser: RobotFileParser | None, url: str) -> bool:
    return True if parser is None else parser.can_fetch(USER_AGENT, url) and parser.can_fetch("*", url)


# ------------------------------------------------------------------ extraction
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
OBFUSCATED = re.compile(r"([A-Za-z0-9._%+\-]+)\s*[\[(]\s*at\s*[\])]\s*([A-Za-z0-9.\-]+)\s*[\[(]\s*dot\s*[\])]\s*([A-Za-z]{2,})", re.I)
BAD_EMAIL = re.compile(r"\.(png|jpe?g|gif|svg|webp|css|js)$|example\.|domain\.com|yourdomain|email\.com|sentry|wixpress|@2x|"
                       r"^(you|name|user|info@example)@", re.I)
TZ_PHONE = re.compile(r"(?<![\d+])(?:\+?255|0)[\s\-.]?\(?0?\)?[\s\-.]?(?:[67]\d{2}[\s\-.]?\d{3}[\s\-.]?\d{3}|2\d[\s\-.]?\d{3}[\s\-.]?\d{4})(?!\d)")
LABELLED_PHONE = re.compile(r"(?:tel|phone|mobile|cell|call|whatsapp|simu)[^\d+]{0,12}(\+\d[\d\s\-().]{7,18}\d)", re.I)
POSTAL = re.compile(r"(?:P\.?\s?O\.?\s*Box|S\.?\s?L\.?\s?P\.?|Private Bag)\s*[.:]?\s*(?:No\.?\s*)?\d{1,6}[^\n|]{0,60}", re.I)
HONORIFIC = r"(?:(?:Mr|Mrs|Ms|Miss|Dr|Prof|Rev|Fr|Sr|Pastor|Bishop|Eng|Hon|Mhe|Ndg|Bi|Bw)\.?\s+)"
ROLE = re.compile(r"\b(co-?founder|founder|managing director|executive director|country director|director|ceo|chief [a-z]+ officer|chief executive|"
                  r"chair(?:man|person|woman)?|president|general manager|operations manager|office manager|manager|head of [a-z &]+|head|"
                  r"co-?ordinator|administrator|officer|secretary|treasurer|accountant|owner|proprietor|principal|headmaster|headmistress|matron|"
                  r"patron|social worker|supervisor|team leader|trustee|board member|representative|partner|mkurugenzi|meneja|mratibu|"
                  r"mwenyekiti|katibu|mhasibu|afisa)\b", re.I)
DECISION = re.compile(r"founder|director|ceo|chief|chair|president|owner|proprietor|manager|head|principal|co-?ordinator|administrator|"
                      r"human resources|\bhr\b|representative|mkurugenzi|meneja|mratibu|mwenyekiti", re.I)
NOT_A_NAME = re.compile(r"\b(Our|The|About|Contact|Team|Staff|Welcome|Karibu|Read|More|Home|Safari|Safaris|Tours?|Lodge|Hotel|Camp|Ltd|Limited|"
                        r"Company|School|Children|Home|Centre|Center|Trust|Foundation|Group|Services|Office|Department|Programme|Program|"
                        r"Project|Board|Mission|Vision|Values|National|Park|Mount|Kilimanjaro|Serengeti|Ngorongoro|Tarangire|Manyara|Arusha|"
                        r"Moshi|Tanzania|Zanzibar|Africa|African|Package|Day|Days|Night|Nights|Crater|Lake|Island|Beach|Road|Street|Street|"
                        r"Box|Email|Phone|Call|Book|Now|Privacy|Policy|Terms|Copyright|Rights|Reserved|Donate|Volunteer|Gallery|News|Blog|"
                        r"Events|Partners|Sponsors?|Frequently|Asked|Questions|Testimonials?|Reviews?|Guide|Guides|Driver|Travel|Adventure|"
                        r"Experience|Wildlife|Migration|Climb|Trek|Route|Hospital|Clinic|University|College|Bank|Church|Kanisa|"
                        r"Job|Jobs|Opportunity|Opportunities|Position|Vacancy|Vacancies|Career|Careers|Apply|Deadline|Hiring|Wanted|"
                        r"Message|Send|Submit|Follow|Subscribe|Newsletter|Login|Register|Search|Menu|Close|Hours|Open|Monday|Tuesday|"
                        r"Wednesday|Thursday|Friday|Saturday|Sunday|January|February|March|April|June|July|August|September|October|"
                        r"November|December|Thank|Thanks|Dear|Click|Here|View|Learn|Discover|Explore|Join|Get|Touch|Find|Meet|Info|"
                        r"Why|Choose|Us|Trusted|By|Physical|Address|Addresses|Member|Members|Guest|Guests|Care|Annual|Report|Reports|Become|"
                        r"Daycare|Academy|Institute|Society|Association|Network|Initiative|Agency|Ministry|Council|Committee|Lorem|Ipsum|"
                        r"Sample|Placeholder|Client|Clients|Customer|Customers|Happy|Traveller|Travellers|Traveler|Travelers|Family|Families|"
                        r"Orphanage|Orphans|Kids|Donors?|Supporters?|Friends|Staff|Leadership|Management|Directors|Founders|"
                        r"Holiday|Holidays|Expedition|Expeditions|Journey|Journeys|Rollercoaster|Core|Value|Master|Chef|Featured|On|Your|One|"
                        r"Booking|Bookings|Enquiries|Enquiry|Reservationist|Reservations|Timeless|International|Licensed|Operator|Certified|"
                        r"Years|Manufacturing|Emergency|Response|Admin|Professional|Appointment|Make|Online|Service|Services|Partner|"
                        r"Partners|What|Who|How|Where|When|Which|Do|We)\b", re.I)
# Gambling or parked content injected into a hacked site, or a domain that has changed hands: nothing on such a page is used.
SPAM = re.compile(r"\b(slot ?online|slot gacor|slot dana|gacor|togel|judi (online|slot|bola)|situs (slot|judi|togel)|casino online|poker online|"
                  r"sbobet|maxwin|link alternatif|stake ?88|naga ?\d{2,}|buy this domain|domain (is )?for sale|this domain (may be|is) for sale|"
                  r"hugedomains|parked (free|domain))\b", re.I)
# A research note saying the organisation has closed (merges hold its drafts and raise a review).
CLOSURE = re.compile(r"defunct|licen[cs]e (was )?revoked|liquidat|closed (down|in \d{4})|no longer (operat|exist|trad)|may no longer operate|"
                     r"ceased (operat|trading)|shut down|possible closure|\b(looks|appears|seems) (inactive|dormant)\b|possibly inactive|"
                     r"may have lapsed", re.I)
# Warnings research agents leave in their notes, for a person to check (review items; only a closure also holds drafts).
NOTE_FLAGS = [("possible closure", CLOSURE),
              ("hijacked or parked site", re.compile(r"hijack|gambling|escort|parked|domain (is )?for sale|taken over|(serves|shows) (an )?unrelated|"
                                                     r"changed hands|blank wordpress|for-sale", re.I)),
              ("location to check", re.compile(r"false lead|outside the [\w\- ]{0,30}(area|catchment|region)|out of (the )?area|far outside|"
                                               r"\b\d{3} ?km\b|geocod\w*|wrong (distance|location|pin)", re.I)),
              ("website gone", re.compile(r"failed dns|dns (lookup )?fail|does(n't| not) resolve|no longer resolv\w*|no longer exists|"
                                          r"domain (has )?expired|enotfound", re.I)),
              ("fit to check", re.compile(r"not (specifically )?(for )?child(ren)?\b|doubtful fit|not child-focused|vocational training, not|"
                                          r"peer school|competitor", re.I)),
              ("possible duplicate", re.compile(r"duplicate|probably (the same|now)|same (organi[sz]ation|bank|company|charity|school) as|"
                                                r"older name|former name|renamed|now (called|named|known as)|appears twice|is really|twin", re.I)),
              ("check before outreach", re.compile(r"allegation|abuse|manual review|check (it )?before", re.I))]
# A match that is not about the organisation: a researcher's own wrong guess at a domain that does not resolve.
NOT_A_FLAG = {"website gone": re.compile(r"guess\w*\s+\S+\s+(does(n't| not) resolve|no longer resolv)", re.I)}


def note_flags(notes) -> list[tuple[str, str]]:
    """(flag, note) for each warning in a research note or list of notes."""
    found = []
    for n in ([notes] if isinstance(notes, str) else notes or []):
        text = str(n)
        for kind, pattern in NOTE_FLAGS:
            if pattern.search(text) and not (kind in NOT_A_FLAG and NOT_A_FLAG[kind].search(text) and len(pattern.findall(text)) == 1):
                found.append((kind, text))
    return found


# Stock names from website and design templates, not real staff.
PLACEHOLDER_NAMES = {"john doe", "jane doe", "leslie alexander", "floyd miles", "jenny wilson", "guy hawkins", "kristin watson", "cody fisher",
                     "esther howard", "jacob jones", "robert fox", "wade warren", "brooklyn simmons", "savannah nguyen", "darlene robertson",
                     "cameron williamson", "kathryn murphy", "albert flores", "arlene mccoy", "courtney henry", "devon lane", "ralph edwards",
                     "theresa webb", "bessie cooper", "dianne russell", "annette black", "marvin mckinney", "jerome bell", "eleanor pena",
                     "ronald richards", "darrell steward", "jane cooper", "your name", "full name", "team member"}
# A role that says the person no longer holds it, or that is an office rather than a person's title.
NOT_CURRENT = re.compile(r"^\s*(former|past|late|retired|emeritus|deceased|in (loving )?memory|ex-)|\bformer\b", re.I)
NOT_A_ROLE = re.compile(r"^\s*(head office|head quarters|headquarters|office\b|branch\b|proud to|partner with|we |our |the |your\b|stop\b|"
                        r"welcome|thank)|trusted|tanzania['’]s|first (female )?president|president of (the united republic|tanzania)|"
                        r"^business owner$|years as|certified partner", re.I)
# Staff whose roles have no bearing on partnership or employee-benefit decisions; their names are not collected.
IRRELEVANT_ROLE = re.compile(r"\b(chef|cook|kitchen|waiter|waitress|driver|porter|security|guard|askari|cleaner|housekeep\w*|gardener|"
                             r"volunteer|intern|guide|mountain guide|safari guide|naturalist|teacher|tutor|nanny|caregiver|care giver|"
                             r"mechanic|receptionist|bartender|barista|photographer|videographer|cameraman|ranger|accountant)\b", re.I)
# Besides decision-makers, only roles that bear on the outreach are kept: people, administration, programmes, welfare, governance.
RELEVANT_ROLE = re.compile(r"human resources?|\bhr\b|people|personnel|administrat|welfare|social work|programme|program|partnership|"
                           r"community|secretary|treasurer|trustee|board|matron|patron", re.I)
# A head of something that is not a decision role ("Head Chef", "Head Mountain Guide").
NOT_A_HEAD = re.compile(r"\bhead\s+(?:\w+\s+)?(chef|cook|guide|driver|porter|security|teacher)\b", re.I)
# Words that mark another organisation in a role ("HR Manager, Mwanzo Corporate Offices, Dar es Salaam"): a client testimonial.
ORG_WORDS = re.compile(r"\b(ltd|limited|centre|center|complex|offices|boutique|hotel|lodge|hospital|clinic|bank|company|group|corporation|"
                       r"agri\w*|processing|medical|school|university|college)\b", re.I)
EMAIL_IN_TEXT = re.compile(r"\S+@\S+\.\w+")
DEGREE_PREFIX = re.compile(r"^(?:(?:MBA|PhD|Ph\.D\.?|MSc|M\.Sc\.?|MA|BA|BSc|B\.Sc\.?|CPA|ACCA|MD|RN)\b[,.\s]*)+", re.I)


def html_lines(html: bytes):
    """Visible text as lines, plus the parsed document (lxml)."""
    from lxml import html as lxml_html
    try:
        doc = lxml_html.fromstring(html)
    except Exception:  # noqa: BLE001 - unparsable page
        return [], None
    for bad in doc.xpath("//script|//style|//noscript|//svg|//iframe"):
        bad.drop_tree()
    for el in doc.xpath("//br|//p|//div|//li|//tr|//h1|//h2|//h3|//h4|//h5|//h6|//section|//article|//td|//th|//dd|//dt|//figcaption|//span[@class]"):
        el.tail = "\n" + (el.tail or "")
    text = doc.text_content()
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return [line for line in lines if line], doc


def decode_cfemail(hexstr: str) -> str:
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


# Page junk around an address: URL-encoded spaces from mailto links, zero-width characters, stray spaces.
EMAIL_JUNK = re.compile(r"%[0-9a-f]{2}|[\s​-‍⁠﻿]", re.I)
# Theme and site-builder placeholders found on the crawled sites: never an organisation's address or number.
TEMPLATE_EMAIL = re.compile(r"@(mysite|travel|office|careox)\.com$", re.I)
TEMPLATE_PHONES = {"1234567890", "255123456789", "255712345678", "6668880000"}
# Endings an address can have. A longer ending that starts with a short one is a word glued on from the page text
# ('info@x.comarusha', 'hello@y.co.tznature'), and is cut back.
KNOWN_TLDS = {"com", "org", "net", "edu", "gov", "int", "info", "biz", "co", "ac", "or", "go", "ne", "tz", "ke", "ug", "rw", "bi", "cd", "uk",
              "us", "ca", "au", "nz", "za", "de", "nl", "be", "ch", "at", "fr", "es", "it", "pt", "ie", "dk", "se", "no", "fi", "is", "pl", "cz",
              "sk", "hu", "ro", "ru", "cn", "jp", "kr", "in", "ae", "br", "mx", "io", "eu", "africa", "travel", "tours", "safari", "community",
              "company", "foundation", "charity", "church", "global", "online", "network", "school", "academy", "education", "center", "world",
              "agency", "consulting", "group", "solutions", "services", "support", "email", "digital", "media", "studio", "computer",
              "organic", "network", "dental", "degree", "delivery", "design", "deals", "chat", "cheap", "christmas", "channel"}
GLUE_TLDS = ("com", "org", "net", "tz", "ke", "ug", "uk", "de", "nl", "ch")
ROLE_MAILBOX = r"(?:info|sales|contact|enquiries|inquiries|bookings|booking|reservations|admin|office)"


def clean_email(value: str) -> str:
    value = W.norm_email(EMAIL_JUNK.sub("", value.split("?")[0]))
    if not value:
        return ""
    local, _, domain = value.rpartition("@")
    last = domain.rsplit(".", 1)[-1]
    if last not in KNOWN_TLDS:
        glued = next((t for t in GLUE_TLDS if last.startswith(t) and len(last) - len(t) >= 3), "")
        if glued:
            domain = domain[: len(domain) - len(last) + len(glued)]
    local = re.sub(r"^\d+(?=" + ROLE_MAILBOX + r"$)", "", local)  # a PO Box number glued onto a role mailbox ('198info@')
    value = f"{local}@{domain}"
    return "" if BAD_EMAIL.search(value) or TEMPLATE_EMAIL.search(value) else value


def template_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return digits in TEMPLATE_PHONES or "123456789" in digits


def page_kind(url: str, title: str = "") -> str:
    probe = f"{urlsplit(url).path} {title}".lower()
    for kind, pattern in PAGE_KINDS:
        if re.search(pattern, probe):
            return kind
    return "home" if urlsplit(url).path in ("", "/") else "other"


def extract(url: str, html: bytes) -> dict:
    lines, doc = html_lines(html)
    out = {"emails": {}, "phones": {}, "socials": {}, "postal": [], "people": [], "links": []}
    if doc is None:
        return out
    title = " ".join((doc.findtext(".//title") or "").split())[:140]
    out["title"] = title
    if SPAM.search(title) or len(SPAM.findall(" ".join(lines[:80]))) >= 3:
        out["spam"] = True
        return out
    for a in doc.xpath("//a[@href]"):
        href = (a.get("href") or "").strip()
        text = " ".join((a.text_content() or "").split())[:60]
        if href.lower().startswith("mailto:"):
            email = clean_email(href[7:])
            if email:
                out["emails"].setdefault(email, text)
        elif href.lower().startswith("tel:"):
            phone = W.norm_phone(href[4:])
            digits = re.sub(r"\D", "", phone)
            if (len(digits) == 12 if digits.startswith("255") else 10 <= len(digits) <= 13):
                out["phones"].setdefault(phone, "tel link")
        elif "/cdn-cgi/l/email-protection#" in href:
            email = clean_email(decode_cfemail(href.split("#", 1)[1]))
            if email:
                out["emails"].setdefault(email, "protected link")
        else:
            absolute = urljoin(url, href)
            host = urlsplit(absolute).netloc.lower().split(":")[0]
            host = host[4:] if host.startswith("www.") else host
            platform = next((p for d, p in SOCIAL_MAP.items() if host == d or host.endswith("." + d)), "")
            if platform:
                # Company pages only: a person's LinkedIn profile is not an organisation route and is not kept.
                personal = platform == "linkedin" and not re.search(r"/(company|school|showcase)/", absolute)
                if not personal and not re.search(r"sharer|/share|intent/|/plugins|/tr\?|/dialog|/hashtag/", absolute):
                    out["socials"].setdefault(platform, absolute)
            out["links"].append((absolute, text))
    for el in doc.xpath("//*[@data-cfemail]"):
        email = clean_email(decode_cfemail(el.get("data-cfemail") or ""))
        if email:
            out["emails"].setdefault(email, "protected text")
    joined = "\n".join(lines)
    for m in EMAIL.finditer(joined):
        email = clean_email(m.group(0))
        if email:
            out["emails"].setdefault(email, "page text")
    for m in OBFUSCATED.finditer(joined):
        email = clean_email(f"{m.group(1)}@{m.group(2)}.{m.group(3)}")
        if email:
            out["emails"].setdefault(email, "obfuscated text")
    for m in TZ_PHONE.finditer(joined):
        phone = W.norm_phone(m.group(0))
        if len(re.sub(r"\D", "", phone)) == 12:
            out["phones"].setdefault(phone, "page text")
    for m in LABELLED_PHONE.finditer(joined):
        digits = re.sub(r"\D", "", m.group(1))
        if (len(digits) == 12 if digits.startswith("255") else 10 <= len(digits) <= 13):
            out["phones"].setdefault("+" + digits, "labelled number")
    out["phones"] = {phone: context for phone, context in out["phones"].items() if not template_phone(phone)}
    out["postal"] = sorted({" ".join(m.group(0).split())[:80] for m in POSTAL.finditer(joined)})[:4]
    out["people"] = people_from(lines)
    return out


def is_name(text: str) -> bool:
    """A person's name: 2-4 capitalised words in any alphabet with Latin capitals (Ståle, Zoë, O'Brien, Jean-Pierre), with
    optional initials after the first word; not a role title, heading or place."""
    text = " ".join(str(text or "").split()).strip(" ,-–—|:")
    if len(text) > 48 or NOT_A_NAME.search(text) or ROLE.search(text):
        return False
    words = re.sub(rf"^{HONORIFIC}", "", text, flags=re.I).split()
    if not 2 <= len(words) <= 4:
        return False
    for i, word in enumerate(words):
        initial = i > 0 and re.fullmatch(r"[^\W\d_]\.", word) is not None
        if not word[0].isupper() or not (initial or re.fullmatch(r"[^\W\d_](?:[^\W\d_]|['’\-])+", word)):
            return False
    return True


def clean_role(name: str, role: str) -> str:
    """The role as a title: without template arrows, unbalanced brackets, degree prefixes, place suffixes or the name itself."""
    role = " ".join(EMAIL_IN_TEXT.sub("", str(role or "")).split())
    if name and name.lower() in role.lower():
        role = role[role.lower().rindex(name.lower()) + len(name):]
    role = re.sub(r"^(meet (our|the)|message from (the|our))\s+", "", role.strip(" ,-–—|:"), flags=re.I)
    role = role.split(" · ")[0]
    role = re.sub(r"\s*[>»›]+\s*$", "", role).strip(" ,-–—|:")
    if role.endswith(")") and "(" not in role:
        role = role[:-1]
    if role.startswith("(") and ")" not in role:
        role = role[1:]
    return DEGREE_PREFIX.sub("", role).strip(" ,-–—|:")[:80]


def clean_person(name: str, role: str, org_name: str = "", domain: str = ""):
    """(name, role, decision_maker) for a person worth recording, or None.

    Drops template names, headings, organisation names read as people, roles the person no longer holds, and staff whose roles
    have no bearing on the outreach (data minimisation).
    """
    name = " ".join(str(name or "").split()).strip(" ,-–—|:")
    role = clean_role(name, role)
    if not is_name(name) or not role or not ROLE.search(role) or len(role.split()) > 12:
        return None
    bare = re.sub(r"^" + HONORIFIC, "", name, flags=re.I).lower()
    if bare in PLACEHOLDER_NAMES or name.lower() in PLACEHOLDER_NAMES:
        return None
    if NOT_CURRENT.search(role) or NOT_A_ROLE.search(role):
        return None
    squashed = re.sub(r"[^a-z]", "", bare)
    if len(squashed) >= 6 and (squashed in re.sub(r"[^a-z]", "", domain.lower()) or squashed in re.sub(r"[^a-z]", "", org_name.lower())):
        return None  # the organisation's own name read as a person
    if org_name and "," in role and another_organisation(role.split(",", 1)[1], org_name):
        return None  # someone at another organisation, usually a client testimonial
    decision = bool(DECISION.search(NOT_A_HEAD.sub("", role)))
    if not decision and (IRRELEVANT_ROLE.search(role) or not RELEVANT_ROLE.search(role)):
        return None
    return name, role, decision


def another_organisation(text: str, org_name: str) -> bool:
    """The text names an organisation other than org_name: it carries an organisation word ('Centre', 'Ltd', 'Offices') and
    neither a distinctive word of org_name nor its acronym ('AICC' for Arusha International Conference Centre)."""
    if not ORG_WORDS.search(text):
        return False
    own = {t for t in re.findall(r"[a-z]{3,}", org_name.lower())} - {"the", "and", "ltd", "limited", "company", "tanzania", "arusha", "centre", "center"}
    words = re.findall(r"[A-Za-z]+", text)
    acronym = "".join(w[0] for w in words if w[0].isupper()).lower()
    return not (own & {w.lower() for w in words} or any(len(t) >= 3 and t in acronym for t in own))


GENERIC_NAME_WORDS = {"limited", "company", "tanzania", "africa", "african", "safari", "safaris", "tours", "travel", "travels", "adventure",
                      "adventures", "children", "childrens", "foundation", "centre", "center", "international", "organization", "organisation",
                      "group", "trust", "home", "community"}
class Resolver:
    """The current organisation for a research record whose ID may be stale.

    A run database gives an organisation a new ID when it gains a website (the shared contract keys organisations by
    domain), so records written earlier can carry an old ID. Resolve by ID, then exact name, then name key, and only
    when the match is unique."""

    def __init__(self, organisations):
        self.ids, self.by_exact, self.by_key = set(), {}, {}
        for db, oid, name in organisations:
            self.ids.add((db, oid))
            self.by_exact.setdefault((db, W.norm_text(name).lower()), []).append((db, oid))
            self.by_key.setdefault((db, W.name_key(name)), []).append((db, oid))

    def __call__(self, db, oid, name):
        if (db, oid) in self.ids:
            return (db, oid)
        for index, probe in ((self.by_exact, W.norm_text(name).lower()), (self.by_key, W.name_key(name))):
            hits = index.get((db, probe), [])
            if len(hits) == 1:
                return hits[0]
        return None


def named_after(org_name: str, domain: str) -> bool:
    """The website's domain carries a distinctive word of the organisation's name."""
    return name_domain_score(org_name, domain) > 0


def name_domain_score(org_name: str, domain: str) -> int:
    """How many distinctive words of the organisation's name the domain carries (farajaschool.org: Faraja school = 2)."""
    squashed = re.sub(r"[^a-z]", "", domain.lower())
    return sum(1 for t in set(re.findall(r"[a-z]{4,}", org_name.lower())) if t not in GENERIC_NAME_WORDS and t in squashed)


TITLES = {"mr", "mrs", "ms", "miss", "dr", "prof", "rev", "fr", "sr", "pastor", "bishop", "eng", "hon", "mhe", "ndg", "bi", "bw", "sister", "brother",
          "mama", "baba", "and"}


def _name_parts(name: str) -> tuple[set, set]:
    words = [w.lower() for w in re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", name or "")]
    words = [w for w in words if w not in TITLES]
    return {w for w in words if len(w) > 1}, {w for w in words if len(w) == 1}


def same_person(a: str, b: str) -> bool:
    """The same person written two ways: with or without a title, an initial for a surname, or inside a couple's entry
    ('Paul Pickle' and 'Paul and Shannin Pickle'). The shorter name must keep at least two parts."""
    (fa, ia), (fb, ib) = _name_parts(a), _name_parts(b)
    if not fa or not fb:
        return False
    if len(fa) + len(ia) > len(fb) + len(ib):
        (fa, ia), (fb, ib) = (fb, ib), (fa, ia)
    initials_b = ib | {w[0] for w in fb}
    return fa <= fb and ia <= initials_b and len(fa) + len(ia) >= 2


def split_pair(line: str):
    """(name, role) from one line laid out as 'Name - Role', 'Name, Role', 'Name (Role)' or 'Role: Name'."""
    m = re.match(r"^(.{3,50}?)\s*(?:[-–—|,]|\s\(|:)\s*(.{3,80}?)\)?$", line)
    if not m:
        return None
    left, right = m.group(1).strip(), m.group(2).strip()
    if ROLE.search(right) and is_name(left):
        return left, right
    if ROLE.search(left) and is_name(right):
        return right, left
    return None


def people_from(lines: list[str]) -> list[dict]:
    """Name and role pairs as a site lays them out: 'Name' then 'Role' on the next line or the one after, or one line."""
    found, seen = [], set()

    def add(name, role, context):
        person = clean_person(name, role)
        if not person:
            return
        name, role, decision = person
        key = (name.lower(), role.lower())
        if key not in seen:
            seen.add(key)
            found.append({"name": name, "role": role, "decision_maker": decision, "context": context[:120]})

    for i, line in enumerate(lines):
        if len(line) > 120:
            continue
        pair = split_pair(line)
        if pair:
            add(pair[0], pair[1], line)
            continue
        if not is_name(line):
            continue
        for j in (1, 2):
            if i + j >= len(lines):
                break
            nxt = lines[i + j]
            if split_pair(nxt) or is_name(nxt):
                break  # the next person starts here
            if len(nxt) <= 80 and ROLE.search(nxt):
                add(line, nxt, f"{line} / {nxt}")
                break
    return found[:40]


def rank_links(base: str, links) -> list[str]:
    """Same-site links most likely to hold contacts or named leaders, best first."""
    site = registrable(urlsplit(base).netloc)
    scored = {}
    for url, text in links:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or registrable(parts.netloc) != site or any(ch.isspace() for ch in url):
            continue  # other sites, and malformed links with spaces in them
        if re.search(r"\.(pdf|jpe?g|png|gif|zip|docx?|xlsx?|mp4)$", parts.path, re.I) or "#" in url and url.split("#")[0] == base:
            continue
        probe = f"{parts.path} {text}".lower()
        score = max((LINK_SCORE[kind] for kind, pattern in PAGE_KINDS if re.search(pattern, probe)), default=0)
        if score:
            clean = url.split("#")[0]
            scored[clean] = max(score, scored.get(clean, 0))
    return [u for u, _ in sorted(scored.items(), key=lambda kv: (-kv[1], len(kv[0])))]


def registrable(host: str) -> str:
    host = host.lower().split(":")[0]
    host = host[4:] if host.startswith("www.") else host
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in ("co", "or", "ac", "go", "ne", "com", "org") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def person_risk(person: dict) -> tuple[str, str]:
    email = person.get("email", "")
    if email and W.PERSONAL_EMAIL.search(email):
        return "risky", "Named person linked to a personal-domain email on the organisation's site."
    return "medium", "Named person and role as published by the organisation on its own website."
