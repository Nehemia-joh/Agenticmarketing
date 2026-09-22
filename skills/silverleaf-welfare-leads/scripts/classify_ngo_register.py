#!/usr/bin/env python3
"""Classify NGOs Information System (NIS) catchment profiles by child-welfare relevance (offline, deterministic).

Reads data/raw/welfare-research/nis_catchment_<date>.json and nis_catchment_profiles_<date>.jsonl;
writes runtime/welfare/<run-id>/nis_classified.json. A research signal only: it never proves what an NGO does today.
"""
from __future__ import annotations

import argparse
import json
import re

import welfare_lib as W

STRONG = re.compile(
    r"orphan|yatima|children'?s home|childrens home|child care cent|makao ya watoto|kituo cha (kulelea|watoto)|street child|"
    r"watoto wa mitaani|\bovc\b|vulnerable child|watoto walio katika mazingira|mazingira hatarishi|disabled child|"
    r"children with disabilit|watoto wenye ulemavu|(child|children|girls?|baby|babies|kids?)\W+(\w+\W+)?rescue|"
    r"rescue\W+(\w+\W+)?(child|children|girls?|babies|baby|kids)|safe house|nyumba salama|foster (care|famil|parent|home)|"
    r"kinship care|child sponsor|children'?s village|baby home|children'?s rehabilitation|special needs child|"
    r"(deaf|blind|autis|albin)\w*\W+(\w+\W+)?(child|children|kids|watoto)|(child|children|kids|watoto)\W+(\w+\W+){0,3}(deaf|blind|autis|albin)", re.I)
MEDIUM = re.compile(r"\bchild|children|watoto|mtoto|kids|girl child|youth and child|child rights|haki za mtoto|early childhood|malezi|"
                    r"sponsorship|special needs|deaf|autis|albin|disabilit|ulemavu|rehabilitation cent", re.I)
WEAK = re.compile(r"widow|wajane|women|wanawake|elderly|wazee|vulnerable|social protection|welfare|ustawi|poverty|needy", re.I)
NOT_WELFARE = re.compile(r"animal|wildlife|dog|mbwa|pet\b|veterinar", re.I)
ORDER = {"strong": 0, "medium": 1, "medium_projects_only": 2, "weak": 3, "none": 4}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    raw, date = cfg["paths"]["raw"], cfg["research_date"]
    catchment = {n["id"]: n for n in json.loads((raw / f"nis_catchment_{date}.json").read_text(encoding="utf-8"))}
    profiles = {}
    for line in (raw / f"nis_catchment_profiles_{date}.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("status") == "ok" or row["id"] not in profiles:
            profiles[row["id"]] = row
    out = []
    for ngo_id, ngo in catchment.items():
        prof = profiles.get(ngo_id, {})
        fields = prof.get("fields", {})
        name_vision = " ".join([ngo.get("name", ""), ngo.get("vision_text", "")])
        text = " ".join([name_vision, prof.get("text", "")])
        if STRONG.search(name_vision) or STRONG.search(fields.get("Targeted Group", "")):
            level, why = "strong", (STRONG.search(name_vision) or STRONG.search(fields.get("Targeted Group", ""))).group(0)
        elif MEDIUM.search(name_vision):
            level, why = "medium", MEDIUM.search(name_vision).group(0)
        elif STRONG.search(text) or MEDIUM.search(text):
            level, why = "medium_projects_only", (STRONG.search(text) or MEDIUM.search(text)).group(0)
        elif WEAK.search(text):
            level, why = "weak", WEAK.search(text).group(0)
        else:
            level, why = "none", ""
        if NOT_WELFARE.search(ngo.get("name", "")):
            level, why = "none", "animal or wildlife organisation"
        projects = re.findall(r"\d+\s*:\s*(.+?)\s+From:\s*(\d{4}-\d{2}-\d{2})\s*-\s*To:\s*(\d{4}-\d{2}-\d{2})", prof.get("text", ""))
        out.append({
            "nis_id": ngo_id, "name": ngo.get("name", "").strip(), "profile_url": f"https://nis.jamii.go.tz/ngo_profile/{ngo_id}",
            "profile_fetched": prof.get("status") == "ok", "html_sha256": prof.get("html_sha256", ""),
            "reg_no": fields.get("Reg No#", ""), "reg_date": fields.get("Reg Date", ""), "level": fields.get("Level", ""),
            "region": fields.get("Region", ""), "district": fields.get("District", ""), "years_experience": fields.get("Years of Experience", ""),
            "vision": ngo.get("vision_text", "")[:500], "projects": [{"title": p[0][:120], "from": p[1], "to": p[2]} for p in projects][:12],
            "latest_project_end": max((p[2] for p in projects), default=""), "latitude": ngo.get("latitude"), "longitude": ngo.get("longitude"),
            "nearest_campus_registry_coords": ngo.get("nearest_campus"), "distance_km_registry_coords": ngo.get("distance_km"),
            "welfare_relevance": level, "relevance_signal": why,
        })
    out.sort(key=lambda r: (ORDER[r["welfare_relevance"]], r["distance_km_registry_coords"] or 99))
    (cfg["paths"]["work"] / "nis_classified.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    counts = {}
    for r in out:
        counts[r["welfare_relevance"]] = counts.get(r["welfare_relevance"], 0) + 1
    print(json.dumps({"total": len(out), "profiles_fetched": sum(r["profile_fetched"] for r in out), "by_relevance": counts}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
