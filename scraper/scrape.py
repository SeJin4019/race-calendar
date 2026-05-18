#!/usr/bin/env python3
"""
Marathon Korea Scraper
Scrapes marathon race data from marathon-online.co.kr and geocodes via Kakao API.

Usage:
    python scrape.py [--dry-run] [--output PATH]

Environment variables (set in scraper/.env):
    KAKAO_REST_API_KEY  Kakao REST API key for geocoding
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
from urllib.parse import urljoin, urlencode
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


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
        return True  # Conservative: allow if robots.txt unreachable


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
    Returns a list of partial race dicts (without geocoding).

    NOTE: The actual HTML structure must be inspected at runtime.
    This implementation uses common patterns found on Korean marathon sites.
    Adjust selectors if the site structure differs.
    """
    races = []
    page = 1

    while True:
        url = urljoin(BASE_URL, LIST_PATH) + f"?page={page}"
        log.info("Scraping page %d: %s", page, url)

        try:
            resp = get(url)
        except requests.HTTPError as e:
            log.error("HTTP error on page %d: %s", page, e)
            break

        soup = BeautifulSoup(resp.text, "html.parser")

        # Try common table/list selectors (adjust to actual site structure)
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
                if race:
                    races.append(race)
            except Exception as e:
                log.warning("Failed to parse row: %s", e)

        # Stop if less than expected rows (last page)
        if len(rows) < 10:
            break

        page += 1

    return races


def parse_race_row(row, base_url: str) -> dict | None:
    """Parse a single race row/item from the list page."""
    cells = row.find_all(["td", "div"])
    if not cells:
        return None

    # Extract text from cells — adjust indices to match actual column order
    texts = [c.get_text(strip=True) for c in cells]
    if len(texts) < 3:
        return None

    # Try to find the detail page link
    link = row.find("a")
    detail_url = urljoin(base_url, link["href"]) if link and link.get("href") else ""

    # Generate a stable ID from the URL or name
    race_id = f"mol-{detail_url.split('=')[-1]}" if "=" in detail_url else f"mol-{hash(texts[0]) & 0xFFFFFF}"

    # Parse status from known Korean keywords
    status = "접수예정"
    raw_text = " ".join(texts)
    if "접수중" in raw_text or "신청중" in raw_text:
        status = "접수중"
    elif "마감" in raw_text or "접수마감" in raw_text:
        status = "접수마감"
    elif "종료" in raw_text or "완료" in raw_text:
        status = "대회종료"

    return {
        "id": race_id,
        "name": texts[0] if texts else "이름 없음",
        "date": "",          # Fill in from detail page or column
        "location": {
            "address": "",
            "city": "",
            "lat": None,
            "lng": None
        },
        "distances": [],
        "registration_url": detail_url,
        "registration_deadline": "",
        "source_url": detail_url,
        "status": status
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def build_output(races: list[dict]) -> dict:
    return {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "races": races
    }


def safe_write(path: Path, data: dict, dry_run: bool = False) -> None:
    """Write JSON atomically — only replace existing file on full success."""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    if dry_run:
        log.info("[DRY RUN] Would write %d bytes to %s", len(content), path)
        print(content[:500] + "\n...(truncated)")
        return
    # Write to temp file first, then rename (atomic on most OS)
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

    # Load env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    kakao_key = os.environ.get("KAKAO_REST_API_KEY", "")
    if not kakao_key:
        log.warning("KAKAO_REST_API_KEY not set — geocoding will be skipped")

    # Output path
    output_path = Path(args.output) if args.output else Path(__file__).parent.parent / "public" / "races.json"

    # Check robots.txt
    list_url = urljoin(BASE_URL, LIST_PATH)
    if not check_robots(list_url):
        log.error("Scraping disallowed by robots.txt. Aborting.")
        sys.exit(1)

    # Scrape
    log.info("Starting scrape of %s", BASE_URL)
    races = scrape_race_list()
    log.info("Scraped %d races", len(races))

    if not races:
        log.error("No races scraped — keeping existing file intact")
        sys.exit(1)

    # Geocode
    if kakao_key:
        log.info("Geocoding %d addresses...", len(races))
        for race in races:
            addr = race["location"].get("address", "")
            if addr and race["location"]["lat"] is None:
                race["location"]["lat"], race["location"]["lng"] = geocode(addr, kakao_key)

    # Write
    output = build_output(races)
    safe_write(output_path, output, dry_run=args.dry_run)

    log.info("Done.")


if __name__ == "__main__":
    main()
