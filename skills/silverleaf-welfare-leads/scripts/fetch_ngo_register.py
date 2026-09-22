#!/usr/bin/env python3
"""Fetch the NGOs Information System (NIS) register for the catchment, politely and resumably.

1. GET https://nis.jamii.go.tz/mapping once (2.4 MB; embeds every NGO with its map pin and vision statement).
2. Keep NGOs pinned within --radius-km of any campus -> data/raw/welfare-research/nis_catchment_<date>.json
3. GET /ngo_profile/<id> for each -> data/raw/welfare-research/nis_catchment_profiles_<date>.jsonl
   Rate limits (see research-rate-limits.md): at most 4 workers, 0.3 s spacing, 3 retries with backoff.
   Existing profiles are reused; only missing or failed ones are fetched unless --refresh is given.
"""
from __future__ import annotations

import argparse
import hashlib
import html as htmllib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import welfare_lib as W

MAPPING_URL = "https://nis.jamii.go.tz/mapping"
PROFILE_URL = "https://nis.jamii.go.tz/ngo_profile/{id}"
FIELDS = ["Region", "District", "Level", "Reg No#", "Reg Date", "Years of Experience"]


def page_text(raw_html: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw_html, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</(p|div|li|h\d|tr|td|th|span)>", "\n", text, flags=re.I)
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", text))
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def parse(text: str) -> dict:
    lines = text.splitlines()
    out = {}
    for field in FIELDS:
        for i, line in enumerate(lines):
            if line.rstrip(":").strip() == field.rstrip(":") or line.startswith(field + ":"):
                inline = line.split(":", 1)[1].strip() if ":" in line else ""
                out[field] = inline or (lines[i + 1] if i + 1 < len(lines) else "")
                break

    def between(start, stops):
        try:
            i = next(k for k, l in enumerate(lines) if l.lower().startswith(start.lower()))
        except StopIteration:
            return ""
        chunk = []
        for l in lines[i + 1:]:
            if any(l.lower().startswith(s.lower()) for s in stops):
                break
            chunk.append(l)
        return " ".join(chunk).strip()
    out["Vision"] = between("Vision", ["Mission"])
    out["Mission"] = between("Mission", ["Region"])
    out["Priority Area/Sector"] = between("Priority Area/Sector", ["targeted Group", "Targeted Group"])
    out["Targeted Group"] = between("targeted Group", ["Copyright", "©", "Contact", "Follow"])
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", type=int, default=4, help="capped at the host limit (4)")
    parser.add_argument("--refresh", action="store_true", help="refetch the map and every profile")
    args = parser.parse_args()
    cfg = W.load_config(args.run_id)
    date, raw, work = cfg["research_date"], cfg["paths"]["raw"], cfg["paths"]["work"]
    catchment_path = raw / f"nis_catchment_{date}.json"
    profiles_path = raw / f"nis_catchment_profiles_{date}.jsonl"
    source_path = raw / f"nis_mapping_source_{date}.json"
    campuses = W.load_campuses()
    radius = float(cfg.get("register_radius_km", 30))

    if args.refresh or not catchment_path.exists():
        body = W.polite_request(MAPPING_URL, cache_dir=None if args.refresh else work / "http-cache")
        html = body.decode("utf-8", "replace")
        ngos = json.loads(re.search(r"var ngos\s*=\s*(\[.*?\]);\s*\n", html, re.S).group(1))
        subset = []
        for n in ngos:
            try:
                lat, lon = float(n["latitude"]), float(n["longitude"])
            except (TypeError, ValueError, KeyError):
                continue
            dists = {c: W.hav(lat, lon, *xy) for c, xy in campuses.items()}
            nearest = min(dists, key=dists.get)
            if dists[nearest] <= radius:
                subset.append({**n, "nearest_campus": nearest, "distance_km": round(dists[nearest], 1),
                               "vision_text": re.sub(r"<[^>]+>", " ", n.get("vision_statement") or "").strip()})
        catchment_path.write_text(json.dumps(subset, ensure_ascii=False, indent=1), encoding="utf-8")
        source_path.write_text(json.dumps({"source_url": MAPPING_URL, "retrieved_on": date, "page_sha256": hashlib.sha256(body).hexdigest(),
                                           "total_ngos_on_map": len(ngos), "catchment_rule": f"registry map pin within {radius:g} km of any campus",
                                           "catchment_count": len(subset)}, indent=1), encoding="utf-8")
        print(f"map: {len(ngos)} NGOs; {len(subset)} within {radius:g} km")
    catchment = json.loads(catchment_path.read_text(encoding="utf-8"))

    done = set()
    if profiles_path.exists() and not args.refresh:
        for line in profiles_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("status") == "ok":
                done.add(row["id"])
    elif args.refresh and profiles_path.exists():
        profiles_path.unlink()
    todo = [n for n in catchment if n["id"] not in done]
    workers = W.clamp_workers(PROFILE_URL, args.workers)
    print(f"profiles: {len(done)} cached, {len(todo)} to fetch with {workers} workers (expect about {len(todo) * 2.2 / workers / 60:.0f} min)")

    def fetch(ngo: dict) -> dict:
        url = PROFILE_URL.format(id=ngo["id"])
        record = {"id": ngo["id"], "name": ngo["name"], "url": url, "retrieved_on": date, "latitude": ngo.get("latitude"),
                  "longitude": ngo.get("longitude"), "nearest_campus": ngo.get("nearest_campus"), "distance_km": ngo.get("distance_km")}
        try:
            body = W.polite_request(url)
            text = page_text(body.decode("utf-8", "replace"))
            record.update({"status": "ok", "html_sha256": hashlib.sha256(body).hexdigest(), "fields": parse(text), "text": text[:4000]})
        except Exception as exc:  # noqa: BLE001 - recorded, retried on the next run
            record.update({"status": "error", "error": repr(exc)[:200]})
        return record

    lock, count = Lock(), 0
    with profiles_path.open("a", encoding="utf-8") as handle, ThreadPoolExecutor(max_workers=workers) as pool:
        for record in pool.map(fetch, todo):
            with lock:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                count += 1
                if count % 50 == 0:
                    print(f"  {count}/{len(todo)}", flush=True)
    print(f"done: {profiles_path.relative_to(W.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
