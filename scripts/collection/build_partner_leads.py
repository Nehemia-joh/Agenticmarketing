"""
Silverleaf partner-lead pipeline (v0.1)
Inputs (pipe-delimited raw pulls in data/raw/lead-research):
  osm_raw.txt        OpenStreetMap Overpass extract (id|lat|lon|name|tags|phone|website|email|street)
  tato_raw.txt       TATO member directory p1-5 (name|address|location|contact|email|website|url)
  tato_raw2.txt      TATO member directory p5-8 (same)
  tato_enrich.txt    TATO older-format member pages (name|address|city|phone|mobile|email|website|url)
  tcdc_saccos_north.txt  TCDC licensed SACCOS, Arusha+Kilimanjaro subset (name|postal|class)
  data/reference/lead-gazetteer.txt  Nominatim locality geocodes
Output: runtime/artifacts/partner-leads-preview.xlsx
"""
import re, math, csv, sys, os
from pathlib import Path
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "lead-research"
REFERENCE = ROOT / "data" / "reference" / "lead-gazetteer.txt"
def P(f): return str(REFERENCE if f == "gazetteer.txt" else RAW / f)

# ---------------------------------------------------------------- campuses
# Nominatim ward/town centroids; Usa River point nudged north of town toward Momela Rd.
CAMPUSES = OrderedDict([
    ("Usa River",   (-3.3645, 36.8632, "Momela Road, Usa River (Arusha) — primary + boarding")),
    ("Arusha City", (-3.3528, 36.6613, "Sakina, Arusha–Nairobi Rd — primary")),
    ("Ilboru",      (-3.3465, 36.6922, "Ilboru, Arusha — daycare/pre-primary")),
    ("Kijenge",     (-3.3837, 36.7100, "Kijenge, Arusha — daycare/pre-primary")),
    ("Boma Ng'ombe",(-3.3342, 37.1383, "Mahakama Rd, Boma Ng'ombe (Hai, Kilimanjaro) — daycare/pre-primary")),
])
CORE_KM, OUTER_KM = 10, 25

def hav(a, b, c, d):
    R = 6371.0
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = math.radians(c - a), math.radians(d - b)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

# ---------------------------------------------------------------- gazetteer
GAZ = {}
for l in open(P("gazetteer.txt"), encoding="utf-8"):
    p = l.rstrip("\n").split("|")
    if len(p) >= 3 and p[1] and p[1] != "ERR":
        GAZ[p[0].split(",")[0].strip().lower()] = (float(p[1]), float(p[2]))

# manual overrides / additions where Nominatim is weak (approximate, locality-level)
GAZ.update({
    "aicc": (-3.3672, 36.6858), "themi": (-3.3900, 36.7000), "unga limited": (-3.3760, 36.6780),
    "kia": (-3.4290, 37.0745), "kilimanjaro international airport": (-3.4290, 37.0745),
    "hai": (-3.3342, 37.1383),  # Hai district HQ = Boma Ng'ombe
    "meru": (-3.3714, 36.8582), "arumeru": (-3.3714, 36.8582),
    "dsm": None, "dar es salaam": None, "mwanza": None, "nanyuki": None, "watertown": None,
    "ngorongoro": None, "karatu": None, "mto wa mbu": None, "monduli": None, "loliondo": None,
    "iringa": None, "morogoro": None, "magomeni": None, "zanzibar": None, "dodoma": None, "tanga": None,
    "kinondoni": None, "ilala": None, "kigoma": None, "mbeya": None, "serengeti": None, "babati": None,
})
# order matters: most specific first
LOCALITY_KEYS = [k for k in GAZ.keys() if k not in ("arusha", "kilimanjaro region", "moshi")]
LOCALITY_KEYS.sort(key=len, reverse=True)

def locate(text):
    """Return (lat, lon, locality, precision) from free-text address."""
    t = " " + re.sub(r"[^a-z' ]", " ", text.lower()) + " "
    t = re.sub(r"\s+", " ", t)
    for k in LOCALITY_KEYS:
        if " " + k + " " in t or (len(k) > 5 and k in t):
            v = GAZ[k]
            if v is None:
                return (None, None, k.title(), "outside-region")
            return (v[0], v[1], k.title(), "locality")
    if " moshi " in t:
        v = GAZ["moshi"]; return (v[0], v[1], "Moshi", "town")
    if " usa river " in t or "usa-river" in text.lower() or "user river" in text.lower():
        v = GAZ["usa river"]; return (v[0], v[1], "Usa River", "town")
    if " arusha " in t:
        v = GAZ["arusha"]; return (v[0], v[1], "Arusha (city centre, unspecified)", "city")
    return (None, None, "", "unknown")

def distances(lat, lon):
    if lat is None:
        return {}, None, None
    d = {c: round(hav(lat, lon, v[0], v[1]), 1) for c, v in CAMPUSES.items()}
    best = min(d, key=d.get)
    return d, best, d[best]

def tier(km):
    if km is None: return "unlocated / outside region"
    if km <= CORE_KM: return f"Core (≤{CORE_KM} km)"
    if km <= OUTER_KM: return f"Outer (≤{OUTER_KM} km)"
    return f">{OUTER_KM} km"

def clean_name(n):
    n = re.split(r"(?i)\s+(adress|address|p\.?o\.?\s*box|location|loaction)\b", n)[0]
    return re.sub(r"\s+", " ", n).strip(" \u200b-:;,")

def clean_addr(a):
    a = re.sub(r"\[…\]|View Details|\u200b", " ", a)
    return re.sub(r"\s+", " ", a).strip(" ;,")

def clean_phone(s):
    s = re.sub(r"(?i)(conctact|contact|tel|phone|hotline|fax|whatsapp|mobile|duty phone)[:\s]*", " ", s)
    s = re.sub(r"\s+", " ", s).strip(" /:,;")
    return s

def norm_name(n):
    n = n.lower()
    n = re.sub(r"\b(ltd|limited|co|company|t|tz|tanzania|the|and|&|tours?|safaris?|travels?|adventures?)\b", " ", n)
    return re.sub(r"[^a-z0-9]", "", n)

# ---------------------------------------------------------------- safari companies
leads = OrderedDict()   # key -> row dict

def add(row):
    k = norm_name(row["name"]) or row["name"].lower()
    if k in leads:
        old = leads[k]
        for f in ("phone", "email", "website", "address", "lat", "lon"):
            if not old.get(f) and row.get(f): old[f] = row[f]
        old["source"] = old["source"] + " + " + row["source"] if row["source"] not in old["source"] else old["source"]
        if PREC_RANK.get(row.get("precision"), 9) < PREC_RANK.get(old.get("precision"), 9):
            old.update({k2: row[k2] for k2 in ("lat", "lon", "locality", "precision")})
            if row.get("address") and len(row["address"]) > len(old.get("address") or ""): old["address"] = row["address"]
        if old["name"].isupper() or old["name"] == old["name"].title():
            if not row["name"].isupper() and row["name"] != row["name"].title(): old["name"] = row["name"]
        return
    if row["name"].isupper(): row["name"] = row["name"].title().replace("Ltd", "Ltd").replace("(T)", "(T)")
    leads[k] = row

PREC_RANK = {"point": 0, "locality": 1, "town": 2, "city": 3, "outside-region": 4, "unknown": 5}

# TATO (new format)
for f in ("tato_raw.txt", "tato_raw2.txt"):
    for l in open(P(f), encoding="utf-8"):
        p = l.rstrip("\n").split("|")
        if len(p) < 7: continue
        name, addr, loc, contact, email, web, url = [x.strip() for x in p[:7]]
        if not name:
            name = url.rstrip("/").split("/")[-1].replace("-", " ").title()
        if name.startswith("||"): continue
        text = f"{addr} {loc}"
        lat, lon, locality, prec = locate(text)
        add(dict(name=clean_name(name), type="Safari / tour operator", subtype="TATO member (licensed)",
                 address=clean_addr(f"{loc}; {addr}"), locality=locality, precision=prec,
                 lat=lat, lon=lon, phone=clean_phone(contact), email=email.replace(" / ", "; "), website=web,
                 source="TATO member directory", source_url=url))

# TATO (old format, enrichment)
for l in open(P("tato_enrich.txt"), encoding="utf-8"):
    p = l.rstrip("\n").split("|")
    if len(p) < 8: continue
    name, addr, city, phone, mobile, email, web, url = [x.strip() for x in p[:8]]
    lat, lon, locality, prec = locate(f"{addr} {city}")
    add(dict(name=clean_name(name), type="Safari / tour operator", subtype="TATO member (licensed)",
             address=clean_addr(f"{city}; {addr}"), locality=locality, precision=prec,
             lat=lat, lon=lon, phone=clean_phone(" / ".join(x for x in (phone, mobile) if x)), email=email, website=web,
             source="TATO member directory", source_url=url))

# OSM
SKIP = re.compile(r"(?i)booking office|precision air|fastjet|coastal aviation|auric air|lodge|hotel|hostel|motel|information|cabin|attraction")
for l in open(P("osm_raw.txt"), encoding="utf-8"):
    p = l.rstrip("\n").split("|")
    if len(p) < 9: continue
    oid, lat, lon, name, tags, phone, web, email, street = p[:9]
    if not name or SKIP.search(name) or SKIP.search(tags):
        if "saccos" not in name.lower(): continue
    lat, lon = float(lat), float(lon)
    if "saccos" in name.lower():
        typ, sub = "Savings group", "SACCOS (OSM-mapped)"
    else:
        typ, sub = "Safari / tour operator", "OSM-mapped office (licence status unverified)"
    add(dict(name=name, type=typ, subtype=sub, address=street, locality="", precision="point",
             lat=lat, lon=lon, phone=phone, email=email, website=web,
             source="OpenStreetMap", source_url="https://www.openstreetmap.org/" + oid))

# ---------------------------------------------------------------- SACCOS (TCDC)
EMPLOYER_HINT = re.compile(r"(?i)staff|workers|employee|teachers|hotel|lodge|tour guides|utalii|security|braeburn|kia|tpc|bonite|sunflag|rijkzwaan|friedkin|asilia|tarangire|senapa|tawiri|taha|camartec|kcmc|kcmuco|mweka|veta|city council|kurugenzi|water|acu|iaa|elct|kkkt|lutheran|hospital|college|school|club|tbl|tcc")
for l in open(P("tcdc_saccos_north.txt"), encoding="utf-8"):
    if l.startswith("#") or not l.strip(): continue
    name, postal, cls = [x.strip() for x in l.rstrip("\n").split("|")[:3]]
    lat, lon, locality, prec = locate(postal)
    if prec in ("city", "town", "unknown"):
        l2 = locate(name)
        if l2[3] == "locality" and l2[2].lower() not in ("meru", "arumeru", "hai", "kisongo"):
            lat, lon, locality, prec = l2
    sub = "SACCOS — employer/institution-based" if EMPLOYER_HINT.search(name) else "SACCOS — community/open-bond"
    add(dict(name=name.title().replace("Saccos", "SACCOS").replace("Ltd", "Ltd"), type="Savings group",
             subtype=sub + f" (TCDC licence class {cls})", address=postal, locality=locality, precision=prec,
             lat=lat, lon=lon, phone="", email="", website="",
             source="TCDC licensed SACCOS register (30 Jun 2022)",
             source_url="https://www.ushirika.go.tz/uploads/ORODHA_YA_SACCOS_ZILIZOPEWA_LESENI_KUISHIA_30.06.2022.pdf"))

# ---------------------------------------------------------------- distances
rows = []
for r in leads.values():
    d, best, km = distances(r["lat"], r["lon"])
    r.update(dict(nearest=best or "", km=km, tier=tier(km), **{f"km_{c}": d.get(c) for c in CAMPUSES}))
    rows.append(r)

def sort_key(r):
    return (0 if r["type"].startswith("Safari") else 1, r["km"] if r["km"] is not None else 9999, r["name"].lower())
rows.sort(key=sort_key)


# ---------------------------------------------------------------- published decision-makers (pass 2)
import json, glob
CONTACTS = {}
for f in sorted(glob.glob(P("contacts_batch_*.jsonl"))):
    for l in open(f, encoding="utf-8"):
        if l.strip():
            rec = json.loads(l); CONTACTS[norm_name(rec["org"])] = rec
for r in rows:
    c = CONTACTS.get(norm_name(r["name"]))
    if not c: continue
    r["site_status"] = c["status"]
    r["headcount"] = c.get("headcount_claim") or ""
    r["founded"] = c.get("founded") or ""
    if not r["phone"] and c.get("general_phone"): r["phone"] = c["general_phone"]
    if not r["email"] and c.get("general_email"): r["email"] = c["general_email"]
    r["people"] = c.get("people") or []
    r["contact_summary"] = "; ".join(f"{p['name']} — {p['role']}" for p in r["people"])
    r["status2"] = "Contact identified (unverified)" if r["people"] else ("Site unreachable" if c["status"].startswith("site") else "No named contact published")
    r["notes2"] = c.get("notes") or ""

# ---------------------------------------------------------------- Excel
wb = Workbook()
HDR = PatternFill("solid", fgColor="1F4E3D"); HF = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")

def sheet(title, headers, data, widths):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for c in range(1, len(headers)+1):
        ws.cell(1, c).fill = HDR; ws.cell(1, c).font = HF; ws.cell(1, c).alignment = WRAP
    for row in data: ws.append(row)
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"; ws.auto_filter.ref = ws.dimensions
    return ws

# README
ws = wb.active; ws.title = "READ ME FIRST"
readme = [
 ["Silverleaf Academy — Partner-lead universe v0.1 (safari companies & savings groups near campuses)"],
 ["Compiled 6 Sep 2026 from public sources only. This is a RESEARCH LIST, not a contact list ready for outreach."],
 [],
 ["STOP — Tanzania Personal Data Protection Act 2022 (PDPA) before anything is operationalised"],
 ["• The PDPA (in force since 2023, regulator: Personal Data Protection Commission, PDPC) requires a lawful basis, purpose limitation and, for direct marketing, consent. Controllers must register with the PDPC."],
 ["• This list contains ORGANISATIONS and their published business contacts (info@ addresses, office lines). Named individuals appear only where an organisation itself published a name in a business role — treat those as personal data."],
 ["• Do NOT: bulk-message individual members/staff, import phone numbers into WhatsApp broadcast lists, scrape member rolls, or buy third-party parent data. Do: approach the organisation (HR / secretary / chair), ask them to circulate, capture consent at first contact, log the basis in the CRM."],
 ["• Required before go-live: (1) Silverleaf PDPC registration status confirmed; (2) privacy notice + consent wording for partner outreach; (3) a suppression/opt-out list; (4) legal sign-off on the outreach template. Until then this list is for planning and prioritisation only."],
 [],
 ["What the sheets contain"],
 ["Safari companies — 300+ tour operators from the TATO member directory (licensed operators) plus OpenStreetMap office points; each placed at locality level and measured to the nearest campus."],
 ["Savings groups — 110+ SACCOS licensed by TCDC in Arusha & Kilimanjaro regions, split into employer-based (a company or institution's staff SACCOS: a warm route to a whole payroll of parents) and community SACCOS. VICOBA/VSLA groups are NOT in any public register — see Sources sheet for how to reach them."],
 ["Campuses — coordinates used, and radius tiers: Core ≤10 km, Outer ≤25 km (Silverleaf's own transport pricing stops at 25 km)."],
 ["Sources & next steps — where each record came from, known gaps, and the manual verification pass required before any row is 'qualified'."],
 ["Decision-makers (published) — pass 2, Core tier only (≤10 km): 271 company websites visited, 137 published at least one named person in a business role (owner / MD / GM / operations or reservations manager). Only the organisation's OWN website was used — no LinkedIn, Facebook or directories. Contact details appear only where the organisation itself published them for that role. Headcount claims and founding year captured where stated."],
 ["Not collected, deliberately: staff, guides, drivers, SACCOS members. Collecting and holding those is already 'processing' under the PDPA; the lawful route is the partner organisation circulating Silverleaf's offer and each parent opting in. Use the headcount column to size the opportunity instead."],
 [],
 ["Geocoding precision"],
 ["point = exact office coordinates (OSM). locality = neighbourhood/ward centroid from the published address (±1–3 km). town/city = only the town was known (Arusha centre / Moshi / Usa River) — distance is indicative only. Records marked outside-region are TATO members HQ'd elsewhere (Dar, Mwanza, Kenya, USA) and are kept for completeness but ranked last."],
 [],
 ["Status column"],
 ["Every row starts as 'Unverified'. Nothing moves to 'Qualified' until someone has (a) confirmed the phone/email is live, (b) identified the right contact role, and (c) recorded approximate staff or member count. Suggested owner: Mariam Haji (Partnerships)."],
]
for r in readme: ws.append(r)
ws.column_dimensions["A"].width = 160
for i in (1, 4, 10, 18, 21): ws.cell(i, 1).font = Font(bold=True, size=12 if i == 1 else 11)
for i in range(1, len(readme)+1): ws.cell(i, 1).alignment = WRAP

hdr = ["Organisation", "Type", "Sub-type", "Locality", "Geocode precision", "Nearest campus", "Km to nearest", "Radius tier",
       *[f"Km → {c}" for c in CAMPUSES], "Phone(s)", "Email(s)", "Website", "Address (as published)",
       "Source", "Source URL", "Decision-maker(s) as published (see Decision-makers sheet)", "Headcount claim (as published)", "Status", "Owner", "Notes"]
widths = [34, 18, 34, 22, 14, 14, 10, 16, 10, 10, 10, 10, 10, 30, 34, 28, 40, 26, 40, 24, 16, 12, 12, 30]

def torow(r):
    return [r["name"], r["type"], r["subtype"], r["locality"], r["precision"], r["nearest"], r["km"], r["tier"],
            *[r.get(f"km_{c}") for c in CAMPUSES], r["phone"], r["email"], r["website"], r["address"],
            r["source"], r["source_url"], r.get("contact_summary", ""), r.get("headcount", ""), r.get("status2", "Unverified"), "",
            r.get("notes2", "")]

saf = [torow(r) for r in rows if r["type"].startswith("Safari")]
sav = [torow(r) for r in rows if r["type"] == "Savings group"]
sheet("Safari companies", hdr, saf, widths)
sheet("Savings groups (SACCOS)", hdr, sav, widths)

# Decision-makers sheet (pass 2: organisations' own websites only, Core tier)
dm = []
for r in rows:
    for p in r.get("people", []):
        dm.append([r["name"], r["locality"], r["nearest"], r["km"], p.get("name", ""), p.get("role", ""), p.get("email", ""), p.get("phone", ""),
                   p.get("source_url", ""), r.get("headcount", ""), r.get("founded", ""), r["phone"], r["email"],
                   "Legitimate interest — B2B partnership enquiry to a person the organisation publishes in a business role. Log first contact + response in CRM; honour opt-out immediately; do not add to marketing lists.",
                   "Unverified"])
dm.sort(key=lambda x: (x[3] if x[3] is not None else 999, x[0].lower()))
ws = sheet("Decision-makers (published)", ["Organisation", "Locality", "Nearest campus", "Km", "Person", "Role (as published)", "Role email (as published)", "Role phone (as published)",
       "Source page", "Org headcount claim", "Founded", "Org main phone", "Org main email", "PDPA basis / handling rule", "Status"], dm,
       [34, 18, 14, 8, 26, 36, 30, 26, 50, 30, 10, 26, 30, 60, 14])

ws = sheet("Campuses", ["Campus", "Lat", "Lon", "Description", "Geocode basis"],
           [[c, v[0], v[1], v[2], "Nominatim ward/town centroid (approximate — replace with exact gate coordinates from Google Maps)"] for c, v in CAMPUSES.items()],
           [16, 10, 10, 60, 70])
ws.append([]); ws.append(["Inter-campus distances (km)"])
ws.append(["", *CAMPUSES.keys()])
for a, va in CAMPUSES.items():
    ws.append([a, *[round(hav(va[0], va[1], vb[0], vb[1]), 1) for vb in CAMPUSES.values()]])

sheet("Sources & next steps", ["Item", "Detail"], [
 ["TATO member directory", "https://tatotz.org/portfolio-cats/mainland-tour-operators/ — 392 entries pulled 6 Sep 2026; ~66 older entries had contact data on their individual pages only (also pulled). Licensed operators; the quality filter for 'safari company'."],
 ["OpenStreetMap (Overpass)", "office=travel_agent / shop=travel_agency / name~safari within Arusha–Moshi bbox. Gives exact office points but coverage is thin (~40 useful). Airline ticket offices, lodges and bus booking offices were excluded."],
 ["TCDC licensed SACCOS register", "https://www.ushirika.go.tz/statistics — 'Orodha ya SACCOS zilizopewa leseni' as of 30 Jun 2022 (latest published). Filtered to Arusha, Usa River, Duluti, Meru, Moshi, Hai, Sanya Juu, Marangu postal towns. Postal box only — no phone/email published; contact via TCDC regional cooperative officer or the district Cooperative Office."],
 ["Bank of Tanzania Tier 2 MSP register", "https://www.bot.go.tz/BankSupervision/institutions (as of 14 May 2026). These are licensed micro-LENDERS, not savings groups — partially reviewed, not included. Useful only if Silverleaf wants a fee-financing partner."],
 ["Nominatim / OSM geocoding", "Locality centroids for ~80 Arusha/Moshi neighbourhoods. Precision flagged per row."],
 ["GAP — VICOBA / VSLA groups", "No public register. Tier-4 community microfinance groups register with the District Council (Community Development Officer) under the Microfinance Act 2018. Routes: (1) Arusha City Council, Meru DC and Hai DC Community Development Offices — request the register of registered vikundi; (2) VICOBA FETA (federation) and NGO programmes (CARE VSLA, BRAC, World Vision) for group lists in Arumeru/Hai; (3) BEST: a one-question survey of current parents — 'which VICOBA/SACCOS do you belong to?' — every hit is a warm, referrer-backed lead."],
 ["GAP — Google Places", "Not run (no API key). A Places Text Search for 'safari company' / 'tour operator' around each campus would add exact coordinates and phone numbers for a few hundred more operators (~USD 5–15). Script is structured to accept it as another input."],
 ["GAP — named contacts & size", "Not collected (and deliberately so — see PDPA note). Fill during the verification call: HR/Operations manager for companies, Chairperson/Secretary for SACCOS; approximate headcount / membership."],
 ["Adjacent employer clusters worth adding", "KIA airport & handling companies (next to Boma Ng'ombe); Usa River flower/seed farms (Rijk Zwaan, Kiliflora, Mount Meru Flowers); lodges/hotels in Usa River–Arusha corridor; NGOs/UN agencies at AICC; TPC Moshi. Several of these already appear via their staff SACCOS."],
 ["Verification pass (manual, ~2 people × 2 weeks)", "Per row: call main line → confirm exists & office location → ask for HR / admin contact role → ask approximate staff/member count → record consent to receive Silverleaf partnership info → set Status = Qualified / Not a fit / No answer. Log everything in the partnerships pipeline, never in personal phones."],
 ["Data freshness", "TATO listings are self-maintained and some are stale; TCDC list is 2022. Expect 10–20% dead contacts."],
], [34, 150])

out = os.environ.get("OUT_XLSX") or str(ROOT / "runtime" / "artifacts" / "partner-leads-preview.xlsx")
Path(out).parent.mkdir(parents=True, exist_ok=True)
wb.save(out)
print("rows:", len(rows), "safari:", len(saf), "savings:", len(sav))
from collections import Counter
print(Counter(r["tier"] for r in rows if r["type"].startswith("Safari")))
print(Counter(r["tier"] for r in rows if r["type"] == "Savings group"))
print(Counter(r["precision"] for r in rows))
