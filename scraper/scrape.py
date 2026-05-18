#!/usr/bin/env python3
"""
Marathon Korea Scraper
Scrapes marathon race data from marathon-online.co.kr and geocodes via Kakao API.

Usage:
    python scrape.py [--dry-run] [--output PATH]

Environment variables (set in scraper/.env):
    KAKAO_REST_API_KEY  Kakao REST API key for geocoding

Inclusion criteria:
    - At least one distance >= 5K
    - Registration fee required (paid event)
    - Excludes: children-only races, walking-only events, corporate-only events

"""

import os
import sys
import json
import time
import random
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
import hashlib
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = "https://www.marathon-online.co.kr"
LIST_PATH = "/race/list.php"
USER_AGENT = "MarathonKoreaBot/1.0 (+https://github.com/your-repo/marathon-korea)"
DELAY_MIN = 1.0
DELAY_MAX = 2.0

# Minimum distance to include a race (km)
MIN_DISTANCE_KM = 5

# Race name/description keywords → exclude
EXCLUDE_KEYWORDS = [
    "걷기대회", "워킹대회", "워킹 대회", "파워워킹",
    "사내대회", "임직원", "사내마라톤", "직원대회",
    "어린이달리기", "어린이 달리기", "유아달리기",
    "반려견", "강아지런",
    "무료참가", "참가비 없음", "참가비없음",
]

# Keywords that suggest an officially certified race (대한육상연맹 공인)
CERTIFIED_KEYWORDS = [
    "공인", "육상연맹", "대한육상", "AAC", "AIMS",
    "국제마라톤", "국제 마라톤",
]

# Distance string → km mapping
DISTANCE_KM_MAP = {
    "풀": 42.195, "풀코스": 42.195, "42km": 42.195, "42.195km": 42.195,
    "하프": 21.0975, "하프코스": 21.0975, "21km": 21.0975,
    "10km": 10, "10k": 10, "10K": 10,
    "5km": 5, "5k": 5, "5K": 5,
    "3km": 3, "3k": 3,
    "2km": 2, "1km": 1,
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------------------------

def should_exclude(name: str, raw_text: str) -> tuple[bool, str]:
    """Return (True, reason) if this race should be excluded."""
    combined = (name + " " + raw_text).lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in combined:
            return True, f"excluded keyword: {kw}"
    return False, ""


def parse_distances(texts: list[str]) -> list[str]:
    """Extract distance labels from cell texts."""
    known = ["풀", "하프", "10K", "10km", "5K", "5km", "3K", "3km", "2K", "2km", "1K", "1km"]
    found = []
    combined = " ".join(texts)
    for label in known:
        if label.lower() in combined.lower() and label not in found:
            found.append(label)
    # Normalize labels
    normalized = []
    for d in found:
        dl = d.lower()
        if dl in ("풀", "풀코스", "42km", "42.195km"):
            normalized.append("풀")
        elif dl in ("하프", "하프코스", "21km"):
            normalized.append("하프")
        elif dl in ("10k", "10km"):
            normalized.append("10K")
        elif dl in ("5k", "5km"):
            normalized.append("5K")
        elif dl in ("3k", "3km"):
            normalized.append("3K")
        elif dl in ("2k", "2km"):
            normalized.append("2K")
        elif dl in ("1k", "1km"):
            normalized.append("1K")
        else:
            normalized.append(d)
    # Deduplicate preserving order
    seen = set()
    result = []
    for d in normalized:
        if d not in seen:
            seen.add(d)
            result.append(d)
    return result


def max_distance_km(distances: list[str]) -> float:
    """Return the longest distance in km from a distances list."""
    max_km = 0.0
    for d in distances:
        km = DISTANCE_KM_MAP.get(d, DISTANCE_KM_MAP.get(d.lower(), 0))
        if km > max_km:
            max_km = km
    return max_km


def is_certified_race(name: str, raw_text: str) -> bool:
    """Return True if the race appears to be officially certified."""
    combined = name + " " + raw_text
    return any(kw in combined for kw in CERTIFIED_KEYWORDS)


def is_free_race(raw_text: str) -> bool:
    """Return True if the race appears to be free (no registration fee)."""
    free_signals = ["무료", "참가비 없음", "참가비없음", "무료참가", "무료 참가"]
    return any(s in raw_text for s in free_signals)


# ---------------------------------------------------------------------------
# robots.txt check
# ---------------------------------------------------------------------------

def check_robots(url: str) -> bool:
    """Return True if scraping is allowed by robots.txt."""
    rp = RobotFileParser()
    robots_url = urljoin(BASE_URL, "/robots.txt")
    try:
        rp.set_url(robots_url)
        rp.read()
        allowed = rp.can_fetch(USER_AGENT, url)
        if not allowed:
            log.warning("robots.txt disallows scraping %s", url)
        return allowed
    except Exception as e:
        log.warning("Could not read robots.txt: %s — proceeding cautiously", e)
        return True


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def get(url: str, **kwargs) -> requests.Response:
    """GET with delay and error handling."""
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    resp = SESSION.get(url, timeout=15, **kwargs)
    resp.raise_for_status()
    return resp


# ---------------------------------------------------------------------------
# Kakao Geocoding
# ---------------------------------------------------------------------------

def geocode(address: str, api_key: str) -> tuple[float | None, float | None]:
    """Return (lat, lng) for a Korean address via Kakao REST API."""
    if not api_key or not address:
        return None, None
    try:
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {api_key}"}
        params = {"query": address}
        time.sleep(random.uniform(0.3, 0.6))
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        docs = resp.json().get("documents", [])
        if docs:
            return float(docs[0]["y"]), float(docs[0]["x"])
    except Exception as e:
        log.warning("Geocoding failed for '%s': %s", address, e)
    return None, None


# ---------------------------------------------------------------------------
# Scraping logic
# ---------------------------------------------------------------------------

def scrape_race_list() -> list[dict]:
    """
    Scrape the race list from marathon-online.co.kr.
    Applies inclusion/exclusion filters before returning.
    """
    races = []
    excluded_count = 0
    page = 1

    while True:
        url = urljoin(BASE_URL, LIST_PATH) + f"?page={page}"
        log.info("Scraping page %d: %s", page, url)

        try:
            resp = get(url)
        except requests.exceptions.RequestException as e:
            log.error("Request failed on page %d: %s", page, e)
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        rows = (
            soup.select("table.race_list tr[onclick]") or
            soup.select(".race_list .race_item") or
            soup.select("table tbody tr") or
            []
        )

        if not rows:
            log.info("No more rows on page %d — done", page)
            break

        for row in rows:
            try:
                race = parse_race_row(row, resp.url)
                if race is None:
                    continue

                # --- Exclusion filter ---
                excluded, reason = should_exclude(race["name"], race.get("_raw_text", ""))
                if excluded:
                    log.info("Excluded '%s': %s", race["name"], reason)
                    excluded_count += 1
                    continue

                # --- Free race filter ---
                if is_free_race(race.get("_raw_text", "")):
                    log.info("Excluded '%s': free event", race["name"])
                    excluded_count += 1
                    continue

                # --- Distance filter (5K minimum) ---
                if race["distances"] and max_distance_km(race["distances"]) < MIN_DISTANCE_KM:
                    log.info("Excluded '%s': max distance < %dkm", race["name"], MIN_DISTANCE_KM)
                    excluded_count += 1
                    continue

                # Remove internal field before storing
                race.pop("_raw_text", None)
                races.append(race)

            except Exception as e:
                log.warning("Failed to parse row: %s", e)

        if len(rows) < 10:
            break

        page += 1
        if page > 50:
            log.warning("Reached page limit (50). Stopping.")
            break

    log.info("Kept %d races, excluded %d", len(races), excluded_count)
    return races


def parse_race_row(row, base_url: str) -> dict | None:
    """Parse a single race row/item from the list page."""
    cells = row.find_all(["td", "div"])
    if not cells:
        return None

    texts = [c.get_text(strip=True) for c in cells]
    if len(texts) < 3:
        return None

    raw_text = " ".join(texts)

    link = row.find("a")
    detail_url = urljoin(base_url, link["href"]) if link and link.get("href") else ""

    race_id = None
    if detail_url:
        params = parse_qs(urlparse(detail_url).query)
        for key in ('idx', 'id', 'no', 'seq', 'rno'):
            if key in params:
                race_id = f"mol-{params[key][0]}"
                break
    if not race_id:
        race_id = f"mol-{hashlib.sha256(texts[0].encode()).hexdigest()[:8]}"

    status = "접수예정"
    if "접수중" in raw_text or "신청중" in raw_text:
        status = "접수중"
    elif "마감" in raw_text or "접수마감" in raw_text:
        status = "접수마감"
    elif "종료" in raw_text or "완료" in raw_text:
        status = "대회종료"

    distances = parse_distances(texts)
    name = texts[0] if texts else "이름 없음"

    return {
        "id": race_id,
        "name": name,
        "date": "",
        "is_certified": is_certified_race(name, raw_text),
        "location": {
            "address": "",
            "city": "",
            "province": "",
            "lat": None,
            "lng": None
        },
        "distances": distances,
        "registration_url": detail_url,
        "registration_deadline": "",
        "source_url": detail_url,
        "status": status,
        "_raw_text": raw_text,  # Removed before storing
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def build_output(races: list[dict]) -> dict:
    # Sort: certified first, then by date
    races_sorted = sorted(races, key=lambda r: (not r.get("is_certified", False), r.get("date", "")))
    return {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "races": races_sorted
    }


def safe_write(path: Path, data: dict, dry_run: bool = False) -> None:
    """Write JSON atomically."""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    if dry_run:
        log.info("[DRY RUN] Would write %d bytes to %s", len(content), path)
        print(content[:500] + "\n...(truncated)")
        return
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)
    log.info("Wrote %d races to %s", len(data["races"]), path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Marathon Korea scraper")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing files")
    parser.add_argument("--output", default=None, help="Output path (default: ../public/races.json)")
    args = parser.parse_args()

    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.split("#")[0].strip()
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    kakao_key = os.environ.get("KAKAO_REST_API_KEY", "")
    if not kakao_key:
        log.warning("KAKAO_REST_API_KEY not set — geocoding will be skipped")

    output_path = Path(args.output) if args.output else Path(__file__).parent.parent / "public" / "races.json"

    list_url = urljoin(BASE_URL, LIST_PATH)
    if not check_robots(list_url):
        log.error("Scraping disallowed by robots.txt. Aborting.")
        sys.exit(1)

    log.info("Starting scrape of %s", BASE_URL)
    races = scrape_race_list()
    log.info("Scraped %d races after filtering", len(races))

    if not races:
        log.error("No races scraped — keeping existing file intact")
        sys.exit(1)

    if kakao_key:
        log.info("Geocoding %d addresses...", len(races))
        for race in races:
            addr = race["location"].get("address", "")
            if addr and race["location"]["lat"] is None:
                race["location"]["lat"], race["location"]["lng"] = geocode(addr, kakao_key)

    output = build_output(races)
    safe_write(output_path, output, dry_run=args.dry_run)
    log.info("Done.")


if __name__ == "__main__":
    main()
