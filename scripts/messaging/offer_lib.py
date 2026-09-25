"""Shared helpers for Silverleaf's outreach messages (scripts/messaging/).

A first message to an organisation is a request: it names the purpose, introduces the sender and asks for a short
meeting, with no offer terms. The offer follows in the next message, stated from one source:
data/reference/silverleaf-offer-register.json. This module loads the register, holds the sender's details, builds the
offer sentences in English and Kiswahili, writes the campus line from a lead's location, and checks a finished message
against the register (percentages, amounts, expired or restricted terms, placeholders, tone, and no terms in a first
message). The rules are documented in skills/silverleaf-outreach/references/offer-register.md.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def _repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "AGENTS.md").exists() and (parent / "skills").is_dir():
            return parent
    raise SystemExit("Could not find the repository root (a folder containing AGENTS.md and skills/).")


ROOT = _repo_root()
REGISTER_PATH = ROOT / "data" / "reference" / "silverleaf-offer-register.json"
# The sender for all three databases (decided 23 September 2026). The Kiswahili title is a draft translation; Kiswahili
# drafts carry the native-speaker review note.
SENDER = "Mariam Haji"
SENDER_TITLE = "Marketing and Partnership Coordinator"
SENDER_SW = SENDER
SENDER_TITLE_SW = "Mratibu wa Masoko na Ushirikiano"
SIGNATURE = f"Warm regards,\n{SENDER}\n{SENDER_TITLE}\nSilverleaf Academy"
SIGNATURE_SW = f"{SENDER_SW}\n{SENDER_TITLE_SW}, Silverleaf Academy\nS.L.P. 14146, Usa River · +255 769 486 660 · info@silverleaf.co.tz"
INTRO = f"My name is {SENDER}, {SENDER_TITLE} at Silverleaf Academy in Arusha."
INTRO_SW = f"Jina langu ni {SENDER}, {SENDER_TITLE_SW} wa Silverleaf Academy, Arusha."
MEETING_ASK = "Would it be possible to arrange a short meeting, either in person or by phone, to discuss this further?"
MEETING_ASK_SW = "Je, itawezekana kupanga kikao kifupi, ana kwa ana au kwa simu, ili tuzungumze zaidi?"
NATIVE_REVIEW = "Kiswahili draft: native-speaker review required before release."
CONFIRM_2027 = "Finance must confirm that these offer terms apply to the 2027 school year before sending (2027 enrolment plan tasks A1 and A2)."
REQUEST_FIRST = ("The first message is a request and states no offer terms. The offer follows in follow-up 1, or in the reply once someone "
                 "names the right colleague; the Finance condition applies from that message.")


def load_register() -> dict:
    return json.loads(REGISTER_PATH.read_text(encoding="utf-8"))


REGISTER = load_register()
OFFERS = {o["id"]: o for o in REGISTER["offers"]}
CAMPUSES = REGISTER["published_facts"]["campuses"]
OFFER_VERSION = REGISTER["version"]

# ------------------------------------------------------------------ offer sentences (register terms, message wording)
EN = {
    "OF04": ("a school-fee benefit that costs your organisation nothing: 20% off tuition for heads of department, for as long as "
             "their child studies with us, and 10% off the first year for all other staff"),
    "OF01": "a free uniform set (worth TZS 110,000) when the year's tuition is paid before the school year opens",
    "OF02": "10% off tuition for a third child and 20% for a fourth",
    "OF09": "tuition in four instalments",
    "OF03": ("partner rates when a home places all its primary-age children with us: 3% off tuition per child for 10 children, "
             "rising to 6% for 20, 9% for 30, 12% for 40, 15% for 50 and 18% for 60 or more"),
    "OF07": "a group rate, starting at 7% off tuition per student once 50 members' students join",
}
SW = {
    "OF01": "sare kamili ya shule bure (yenye thamani ya TZS 110,000) kwa mzazi anayelipa ada ya mwaka mzima kabla shule haijafunguliwa",
    "OF02": "punguzo la asilimia 10 ya ada kwa mtoto wa tatu na asilimia 20 kwa mtoto wa nne",
    "OF09": "ada kulipwa kwa awamu nne kwa mwaka",
    "OF07": "punguzo la kikundi, kuanzia asilimia 7 ya ada kwa kila mwanafunzi pale wanafunzi 50 wa wanachama watakapojiunga",
}


DISPLAY_NAMES_PATH = ROOT / "data" / "reference" / "organisation-display-names.json"
# Reviewed trading names, for records whose name is a legal name the recipient would not recognise.
DISPLAY_NAMES = json.loads(DISPLAY_NAMES_PATH.read_text(encoding="utf-8"))["organisations"] if DISPLAY_NAMES_PATH.exists() else {}


def display_name(name: str, organisation_id: str | None = None) -> str:
    """An organisation's name for a message. A reviewed trading name (data/reference/organisation-display-names.json) comes
    first; otherwise the record name without the note the databases add in brackets at the end:
    'OMAWA (Moshi)' -> 'OMAWA', 'Arusha Coffee Lodge (Elewana)' -> 'Arusha Coffee Lodge'."""
    if organisation_id in DISPLAY_NAMES:
        return DISPLAY_NAMES[organisation_id]["name"]
    text = " ".join(str(name or "").split())
    return re.sub(r"\s*\([^()]*\)$", "", text).strip() or text


def greeting_name(name: str) -> str:
    """A person's name as published, without research annotations or post-nominal letters: 'Noemi Glaser, BA (desk)' -> 'Noemi Glaser'."""
    name = re.sub(r"\s*\([^)]*\)", "", str(name or "")).strip()
    return re.sub(r",\s*(BA|BSc|MA|MSc|MBA|PhD|Dr|Mr|Mrs|Ms|CPA|MD|RN|Hon\.?)\b.*$", "", name).strip(" ,")


def family_offer_en() -> str:
    return f"{EN['OF01']}, {EN['OF02']}, and {EN['OF09']}"


def family_offer_sw() -> str:
    return f"{SW['OF01']}; {SW['OF02']}; na {SW['OF09']}"


# ------------------------------------------------------------------ campus lines
def campus_key(name: str) -> str:
    n = str(name or "").replace("’", "'")
    if "Boma" in n:
        return "Boma Ngombe"
    if "Arusha City" in n or "Sakina" in n:
        return "Arusha City"
    for key in CAMPUSES:
        if key.lower() in n.lower():
            return key
    return ""


def campus_display(key: str) -> str:
    return CAMPUSES.get(key, {}).get("display", key)


def distance_phrase(km) -> str:
    if km is None or km == "":
        return ""
    km = float(km)
    if km < 1:
        return "less than 1 km"
    return f"about {round(km)} km"


def campus_line_en(campus: str, km=None, precise: bool = False, subject: str = "you") -> str:
    """One sentence naming the nearest campus and what it teaches; the distance only when the location is precise."""
    key = campus_key(campus)
    if not key:
        return network_line_en()
    info = CAMPUSES[key]
    where = f", {distance_phrase(km)} from {subject}" if precise and km not in (None, "") and float(km) <= 25 else ""
    line = f"Our nearest campus, {campus_display(key)}{where}, teaches {info['levels']}."
    if not info["primary"]:
        line += " Primary students join our Usa River or Arusha City campus."
    return line


def network_line_en() -> str:
    return ("We teach Daycare to Grade 7 in English at five campuses: Arusha City (Sakina), Kijenge and Ilboru in Arusha, "
            "Usa River, and Boma Ng'ombe.")


def campus_line_sw(campus: str, km=None, precise: bool = False, place_sw: str = "") -> str:
    key = campus_key(campus)
    if not key:
        return ("Tuna kampasi tano: Arusha City (Sakina), Kijenge na Ilboru jijini Arusha, Usa River, na Boma Ng'ombe, zinazotoa "
                "elimu kuanzia daycare hadi darasa la saba kwa Kiingereza.")
    info = CAMPUSES[key]
    where = ""
    if precise and km not in (None, "") and float(km) <= 25:
        km = float(km)
        where = " (chini ya kilomita 1" if km < 1 else f" (takriban kilomita {round(km)}"
        where += f" kutoka {place_sw})" if place_sw else ")"
    line = f"Kampasi yetu iliyo karibu zaidi{(' na ' + place_sw) if place_sw and not where else ''} ni {campus_display(key)}{where}, inayotoa {info['levels_sw']}."
    if not info["primary"]:
        line += " Wanafunzi wa elimu ya msingi hujiunga na kampasi zetu za Usa River au Arusha City."
    return line


# ------------------------------------------------------------------ conformance
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s?%|asilimia\s+(\d+)", re.I)
AMOUNT = re.compile(r"(?:TZS|Tsh|TSh)\s?([\d,]{4,})", re.I)
PLACEHOLDER = re.compile(r"\[[^\]]+\]")
ALLOWED_PLACEHOLDERS: set = set()  # the sender is known, so every placeholder left in a draft is a fault
# What a first message may not state: percentages, amounts or the offers themselves. The offer belongs in message 2.
OFFER_TERMS = re.compile(r"\d+(?:\.\d+)?\s?%|\basilimia\b|\b(?:TZS|Tsh|TSh)\s?\d|\bdiscount|\bpunguzo\b|\bfree uniform|\bsare\b|"
                         r"\binstal(?:l)?ments?\b|\bawamu\b|\bpartner rates?\b|\bgroup rate\b|\bnafuu\b", re.I)
FORBIDDEN = {
    "referral reward": re.compile(r"referral (reward|discount|bonus|package)|zawadi ya rufaa|30,000", re.I),
    "commission": re.compile(r"\bcommission\b|\bkamisheni\b|facilitation fee", re.I),
    "guarantee": re.compile(r"\bguarantee|\bguaranteed\b|tunahakikisha nafasi", re.I),
    "tone": re.compile(r"\bSLA\b|\bour kids\b|\bworld-class\b|\bthe academy\b", re.I),
    "tuition figure": re.compile(r"1,[0-9]00,000|1\.[0-9]+ million", re.I),
}
OFFICIAL_BENEFIT = re.compile(r"heads? of department|wakuu wa idara|watumishi wa (halmashauri|ofisi|serikali)|staff discount|punguzo kwa watumishi", re.I)


def allowed_numbers(offer_ids) -> tuple[set, set]:
    percents, amounts = set(), set()
    for oid in offer_ids:
        offer = OFFERS.get(oid)
        if offer:
            percents |= {float(p) for p in offer.get("percentages", [])}
            amounts |= {int(a) for a in offer.get("amounts_tzs", [])}
    return percents, amounts


def check_message(text: str, offer_ids, *, convening: bool = False, ignore=()) -> list[str]:
    """Problems with a message against the offer register; an empty list means it conforms.

    `ignore` lists names (organisation, recipient) masked before the word checks, so "Atomic Energy Commission"
    is not read as a commission offer."""
    issues = []
    for name in sorted((n for n in ignore if n), key=len, reverse=True):
        text = (text or "").replace(name, "[name]")
    ids = [o for o in offer_ids if o]
    for oid in ids:
        if oid not in OFFERS:
            issues.append(f"unknown offer {oid}")
        elif OFFERS[oid]["use"] == "no":
            issues.append(f"offer {oid} may not be used ({OFFERS[oid].get('use_note', '')})")
    percents, amounts = allowed_numbers(ids)
    for m in PERCENT.finditer(text or ""):
        value = float(m.group(1) or m.group(2))
        if value not in percents:
            issues.append(f"{value:g}% is not a term of offers {', '.join(ids) or 'none'}")
    for m in AMOUNT.finditer(text or ""):
        value = int(m.group(1).replace(",", ""))
        if value not in amounts:
            issues.append(f"TZS {value:,} is not a term of offers {', '.join(ids) or 'none'}")
    for name, pattern in FORBIDDEN.items():
        if pattern.search(text or ""):
            issues.append(f"forbidden: {name}")
    if convening and OFFICIAL_BENEFIT.search(text or ""):
        issues.append("convening letter offers officials or their staff a benefit (OF04 restriction)")
    for ph in PLACEHOLDER.findall(text or ""):
        if ph not in ALLOWED_PLACEHOLDERS and ph != "[name]":
            issues.append(f"unresolved placeholder {ph}")
    return issues


def check_first_message(text: str, ignore=()) -> list[str]:
    """Problems with a first message to an organisation: it must make a request and state no offer terms."""
    for name in sorted((n for n in ignore if n), key=len, reverse=True):
        text = (text or "").replace(name, "[name]")
    return [f"first message states offer terms ('{m.group(0)}'); the offer belongs in message 2" for m in OFFER_TERMS.finditer(text or "")]


def words(text: str) -> int:
    """Words in a message, without its sign-off and signature."""
    body = re.split(r"\n(?:Warm regards,|Kwa heshima,|Wako katika ujenzi wa Taifa,|Yours in nation building,)", text or "")[0]
    return len(body.split())


# ------------------------------------------------------------------ run databases (welfare and government workbooks and verification)
OUTREACH_HEADERS = ["message_id", "target", "recipient", "contact_route", "route_value", "track", "review_status", "language", "subject", "body",
                    "follow_up_1", "english_meaning", "offer_ids", "conditions"]
DRAFT_STATUSES = {"draft_ready", "needs_review"}


def outreach_sheet_rows(con) -> list[list]:
    """Rows for a run workbook's Outreach Plans sheet, ready drafts first."""
    query = """SELECT p.message_id, COALESCE(o.name, e.name, p.target_id), p.recipient, p.contact_route, p.route_value, p.acquisition_track_id,
                      p.review_status, p.language, m.subject, m.body,
                      (SELECT f.body FROM messages f WHERE f.message_id = p.message_id || '-F1'),
                      (SELECT t.body FROM messages t WHERE t.message_id = p.message_id || '-EN'), p.offer_ids, p.missing_information
               FROM outreach_plans p JOIN messages m ON m.message_id = p.message_id
               LEFT JOIN organisations o ON o.organisation_id = p.target_id LEFT JOIN enquiries e ON e.enquiry_id = p.target_id
               ORDER BY CASE p.review_status WHEN 'draft_ready' THEN 0 ELSE 1 END, 2"""
    return [["" if v is None else v for v in row] for row in con.execute(query)]


def run_message_checks(con, *, convening: bool = False) -> dict:
    """Conformance of every message in a run database (initial, follow-up and English meaning) with the offer register.
    A first message to an organisation must also state no offer terms; convening letters are formal requests that
    describe the parents' booklet, so they are exempt."""
    issues = []
    rows = con.execute("""SELECT m.message_id, m.body, p.offer_ids, COALESCE(o.name, ''), m.message_id = p.message_id, p.target_type FROM messages m
                          JOIN outreach_plans p ON m.message_id IN (p.message_id, p.message_id || '-F1', p.message_id || '-EN')
                          LEFT JOIN organisations o ON o.organisation_id = p.target_id""").fetchall()
    for mid, body, offer_ids, target, initial, target_type in rows:
        ids = [x.strip() for x in str(offer_ids or "").split(";") if x.strip()]
        issues += [(mid, problem) for problem in check_message(body, ids, convening=convening, ignore=(target,))]
        if initial and target_type == "organisation" and not convening:
            issues += [(mid, problem) for problem in check_first_message(body, ignore=(target,))]
    statuses = {s for (s,) in con.execute("SELECT DISTINCT review_status FROM outreach_plans")}
    orphans = con.execute("SELECT COUNT(*) FROM messages m WHERE NOT EXISTS (SELECT 1 FROM outreach_plans p WHERE m.message_id IN "
                          "(p.message_id, p.message_id || '-F1', p.message_id || '-EN'))").fetchone()[0]
    return {"messages_checked": len(rows), "issues": issues, "statuses": sorted(statuses), "orphan_messages": orphans}
