"""Push the lead map to the Leads Map tab of the Silverleaf marketing app.

Reads the page `build_lead_map.py` wrote (`outputs/maps/Silverleaf Lead Map.html`) and its private sidecar
(`runtime/maps/lead-map-sidecar.json`), both written only when the build's count and privacy checks passed. Keeps the
fields the tab uses, gives every lead its stable id (`master:<organisation_id>`, `welfare:...`, `government:...`,
`vicoba:<council>|<ward>`), checks the result against the tab's contract and sends it to
PUT <api>/api/marketing/lead-map/build.

Contacts: the sidecar's sendable address for each lead (the exporter's kept, published rows: never a shared inbox,
never an address inferred from a format) goes in a separate `contacts` section, { id: { em, fn, ln } }, which the app
stores apart from the map and releases only through its audited CSV export to the CEO and global marketing heads.
Government offices have none: they are reached by letter. The map part still carries no email address, phone number
or contact name. Read-only on the databases; the only network call is the push.

    python scripts/maps/build_lead_map.py                 # rebuild first when the leads changed
    python scripts/maps/push_lead_map.py --dry-run        # check and summarise, send nothing
    $env:LEAD_MAP_SYNC_SECRET = '<secret>'                 # the value set on the marketing API
    python scripts/maps/push_lead_map.py                  # push to https://sla-marketing-api.vercel.app
    python scripts/maps/push_lead_map.py --api http://127.0.0.1:5001   # a local API

The contract (segments, confidences, routes, campus codes) is shared with
SLA-HUB/desks/marketing/backend/lib/leadMap.js and web/components/pages/marketing/LeadMap.jsx; a change to one is a
change to all three. Docs: SLA-HUB/desks/marketing/docs/lead-map/README.md.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "outputs" / "maps" / "Silverleaf Lead Map.html"
SIDECAR = ROOT / "runtime" / "maps" / "lead-map-sidecar.json"
DEFAULT_API = "https://sla-marketing-api.vercel.app"

# The marketing app's campus codes (its campuses table), keyed by the names this project uses.
CAMPUS_CODE = {"Arusha City": "ACC", "Kijenge": "KJG", "Ilboru": "ILB", "Usa River": "USR", "Boma Ngombe": "BOM"}
SEGMENTS = {"emp", "wel", "gov", "int"}
CONFIDENCES = {"high-direct", "high-indirect", "high", "medium", "low", "no-email", "shared"}
LEVEL = {"council": "Council", "region": "Regional office", "district": "District office", "ward": "Ward", "village": "Village"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")
PHONE_RE = re.compile(r"\+?\d(?:[\s-]?\d){8,}")


def route(raw: str | None) -> str:
    """The page's free-text route, folded to the tab's five routes."""
    r = (raw or "none").strip().lower()
    if r.startswith("letter"):
        return "letter"
    if r.startswith("through"):
        return "intro"
    return {"email": "email", "phone only": "phone"}.get(r, "none")


def read_page(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    marker = "const DATA = "
    i = text.find(marker)
    if i < 0:
        raise SystemExit(f"{path} has no lead data (no '{marker}'); rebuild it with scripts/maps/build_lead_map.py")
    data, _ = json.JSONDecoder().raw_decode(text, i + len(marker))
    if not isinstance(data, dict) or "leads" not in data:
        raise SystemExit(f"{path}: the lead data is not a build (rebuild it with scripts/maps/build_lead_map.py)")
    return data


def read_sidecar(path: Path, data: dict) -> list[dict]:
    """The sidecar of the same build: one entry per drawn lead, in page order. Refuses a sidecar from another build."""
    if not path.exists():
        raise SystemExit(f"{path} is missing; rebuild with scripts/maps/build_lead_map.py (it writes the page and the sidecar)")
    side = json.loads(path.read_text(encoding="utf-8"))
    leads = side.get("leads") or []
    if side.get("built") != data["built"] or len(leads) != len(data["leads"]) or any(
            s["n"] != l["n"] for s, l in zip(leads, data["leads"])):
        raise SystemExit(f"{path} does not belong to the page's build of {data['built']}; rebuild with scripts/maps/build_lead_map.py")
    return leads


def slim(data: dict, side: list[dict]) -> dict:
    campuses = []
    for c in data["campuses"]:
        code = CAMPUS_CODE.get(c["key"])
        if not code:
            raise SystemExit(f"Campus '{c['key']}' has no marketing-app code; add it to CAMPUS_CODE")
        campuses.append({"code": code, "key": c["key"], "label": c["label"], "lat": c["lat"], "lon": c["lon"]})
    leads, contacts = [], {}
    for l, sc in zip(data["leads"], side):
        u = l.get("u") or {}
        if l["s"] == "gov":
            kind = " · ".join(x for x in (LEVEL.get(u.get("level"), u.get("level") or ""), l.get("k") or "") if x)
        else:
            kind = u.get("kind") or ""
        rec = {"id": sc["id"], "n": l["n"], "s": l["s"], "c": l["c"], "y": l.get("y", ""), "o": l.get("o", ""), "d": l.get("d", ""),
               "r": route(l.get("r")), "k": kind, "t": u.get("tier", ""), "h": l.get("h", ""),
               "la": round(l["la"], 5), "lo": round(l["lo"], 5), "e": l.get("e", 0), "cp": CAMPUS_CODE[l["cp"]],
               "km": l.get("km"), "x": l.get("x", 0)}
        # Empty text and zero flags are left out: the tab reads a missing field as empty.
        leads.append({k: v for k, v in rec.items() if v not in ("", 0, None) or k in ("la", "lo")})
        c = sc.get("contact")
        if c and c.get("email") and l["s"] != "gov":
            contacts[sc["id"]] = {k: v for k, v in (("em", c["email"].strip()), ("fn", (c.get("first_name") or "").strip()),
                                                    ("ln", (c.get("last_name") or "").strip())) if v}
    return {"built": data["built"], "source": "silverleaf-agentic-marketing · scripts/maps/build_lead_map.py",
            "campuses": campuses, "leads": leads, "unmapped": len(data.get("unmapped", [])), "contacts": contacts}


def check(build: dict) -> list[str]:
    errors = []
    ids = set()
    for l in build["leads"]:
        if l["s"] not in SEGMENTS:
            errors.append(f"{l['n']}: segment '{l['s']}' is not one the app knows")
        if l["c"] not in CONFIDENCES:
            errors.append(f"{l['n']}: confidence '{l['c']}' is not one the app knows (add it to the contract first)")
        if l["id"] in ids:
            errors.append(f"{l['n']}: id {l['id']} is used twice")
        ids.add(l["id"])
    # The map part: no contact detail anywhere (ids are hex and may hold long digit runs, so they are left out of the scan).
    text = json.dumps([{k: v for k, v in l.items() if k != "id"} for l in build["leads"]] + build["campuses"], ensure_ascii=False)
    if EMAIL_RE.search(text):
        errors.append("an email address is in the map part of the build")
    if PHONE_RE.search(re.sub(r"-?\d+\.\d+", "", text)):
        errors.append("a phone number is in the map part of the build")
    # The contacts part: one published address per lead, names without numbers.
    for lid, c in build["contacts"].items():
        if lid not in ids:
            errors.append(f"contact for unknown lead {lid}")
        if not EMAIL_RE.fullmatch(c.get("em", "")):
            errors.append(f"contact for {lid}: '{c.get('em', '')}' is not one email address")
        if any(EMAIL_RE.search(c.get(k, "")) or PHONE_RE.search(c.get(k, "")) for k in ("fn", "ln")):
            errors.append(f"contact for {lid}: a name field holds an email address or a number")
    return errors[:20]


def push(api: str, secret: str, build: dict) -> dict:
    body = gzip.compress(json.dumps(build, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    req = urllib.request.Request(
        api.rstrip("/") + "/api/marketing/lead-map/build", data=body, method="PUT",
        headers={"Content-Type": "application/json", "Content-Encoding": "gzip", "X-Webhook-Secret": secret,
                 "User-Agent": "silverleaf-lead-map-push"})
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:2000]
        raise SystemExit(f"The app refused the push ({err.code}): {detail}")
    except urllib.error.URLError as err:
        raise SystemExit(f"Could not reach {api}: {err.reason}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--page", type=Path, default=PAGE)
    parser.add_argument("--sidecar", type=Path, default=SIDECAR)
    parser.add_argument("--api", default=os.environ.get("LEAD_MAP_API", DEFAULT_API))
    parser.add_argument("--dry-run", action="store_true", help="check and summarise; send nothing")
    args = parser.parse_args()

    data = read_page(args.page)
    build = slim(data, read_sidecar(args.sidecar, data))
    errors = check(build)
    size = len(json.dumps(build, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    segs = Counter(l["s"] for l in build["leads"])
    print(f"Lead map built {build['built']}: {len(build['leads'])} leads on the map "
          f"({', '.join(f'{k} {v}' for k, v in sorted(segs.items()))}), {build['unmapped']} without a point, "
          f"{len(build['contacts'])} with a sendable email; "
          f"{size / 1e6:.2f} MB before compression")
    if errors:
        print("CHECKS FAILED:")
        for e in errors:
            print("  - " + e)
        return 1
    if args.dry_run:
        print("Dry run: nothing sent.")
        return 0
    secret = os.environ.get("LEAD_MAP_SYNC_SECRET")
    if not secret:
        print("Set LEAD_MAP_SYNC_SECRET to the value configured on the marketing API.")
        return 1
    result = push(args.api, secret, build)
    if result.get("unchanged"):
        print(f"The app already has this build (id {result['id']}); nothing changed.")
    else:
        print(f"Pushed to {args.api}: build {result['id']}, {result['leads']} leads, built {result['built']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
