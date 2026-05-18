#!/usr/bin/env python3
"""
Marathon Korea Scraper — roadrun.co.kr
Scrapes race data from roadrun.co.kr/schedule/list.php

Usage:
    python scrape.py [--dry-run] [--output PATH] [--max-detail N]

Inclusion criteria:
    - At least one distance >= 5K
    - Excludes: children-only, walking-only, corporate-only, free events
"""

import os
import sys
import json
import time
import random
import re
import argparse
import logging
from datetime import datetime, timezone, date
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install requests beautifulsoup4")
    sys.exit(1)

BASE_URL = "http://www.roadrun.co.kr"
LIST_URL = "http://www.roadrun.co.kr/schedule/list.php"
DETAIL_URL = "http://www.roadrun.co.kr/schedule/view.php"
ENCODING = "EUC-KR"
USER_AGENT = "MarathonKoreaBot/2.0 (+https://github.com/SeJin4019/race-calendar)"
DELAY_MIN = 0.8
DELAY_MAX = 1.5

EXCLUDE_KEYWORDS = [
    "걷기대회", "워킹대회", "워킹 대회", "파워워킹", "걷기",
    "사내대회", "임직원", "사내마라톤", "직원대회", "사내",
    "어린이달리기", "어린이 달리기", "유아달리기", "어린이",
    "반려견", "강아지런",
    "무료참가", "참가비 없음", "참가비없음",
]

DISTANCE_KM_MAP = {
    "풀": 42.195, "풀코스": 42.195, "42km": 42.195,
    "하프": 21.0975, "하프코스": 21.0975, "21km": 21.0975,
    "10km": 10, "10k": 10,
    "5km": 5, "5k": 5,
    "3km": 3, "3k": 3,
    "2km": 2, "1km": 1,
}

PROVINCE_MAP = {
    "서울": "서울", "경기": "경기", "인천": "인천", "강원": "강원",
    "충북": "충북", "충남": "충남", "대전": "대전", "세종": "세종",
    "전북": "전북", "전남": "전남", "광주": "광주",
    "경북": "경북", "경남": "경남", "대구": "대구",
    "부산": "부산", "울산": "울산", "제주": "제주",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def should_exclude(name: str) -> tuple[bool, str]:
    nl = name.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in name:
            return True, f"keyword: {kw}"
    return False, ""


def normalize_distances(raw: str) -> list[str]:
    result = []
    parts = re.split(r"[,/\s]+", raw.strip())
    for p in parts:
        pl = p.strip().lower()
        if pl in ("풀", "풀코스"):
            result.append("풀")
        elif pl in ("하프", "하프코스", "21km"):
            result.append("하프")
        elif pl in ("10km", "10k"):
            result.append("10K")
        elif pl in ("5km", "5k"):
            result.append("5K")
        elif pl in ("3km", "3k"):
            result.append("3K")
        elif pl in ("2km", "2k"):
            result.append("2K")
        elif pl in ("1km", "1k"):
            result.append("1K")
    seen = set()
    return [d for d in result if not (d in seen or seen.add(d))]


def max_distance_km(distances: list[str]) -> float:
    max_km = 0.0
    for d in distances:
        km = DISTANCE_KM_MAP.get(d, DISTANCE_KM_MAP.get(d.lower(), 0))
        if km > max_km:
            max_km = km
    return max_km


def parse_korean_date(text: str) -> str:
    """Parse '2026년5월31일' → '2026-05-31'"""
    m = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return ""


def parse_start_time(text: str) -> str:
    """Extract start time from '2026년5월31일 출발시간:08:00'"""
    m = re.search(r"출발시간\s*[:：]\s*(\d{1,2}:\d{2})", text)
    if m:
        return m.group(1)
    return ""


def detect_province(text: str) -> str:
    for k, v in PROVINCE_MAP.items():
        if k in text:
            return v
    return ""


def detect_status(reg_start: str, reg_end: str, race_date: str) -> str:
    today = date.today().isoformat()
    if race_date and race_date < today:
        return "대회종료"
    if reg_end and reg_end < today:
        return "접수마감"
    if reg_start and reg_start <= today and (not reg_end or reg_end >= today):
        return "접수중"
    if reg_start and reg_start > today:
        return "접수예정"
    if race_date and race_date >= today:
        return "접수예정"
    return "접수예정"


SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def get(url: str, **kwargs):
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    resp = SESSION.get(url, timeout=20, **kwargs)
    resp.raise_for_status()
    return resp


def fetch_decoded(url: str, **kwargs) -> str:
    resp = get(url, **kwargs)
    return resp.content.decode(ENCODING, errors="replace")


def scrape_list() -> list[dict]:
    log.info("Fetching list: %s", LIST_URL)
    html = fetch_decoded(LIST_URL)
    soup = BeautifulSoup(html, "html.parser")

    races = []
    rows = soup.select("table tr")
    current_date_str = ""
    current_day = ""

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        # Date cell: contains font with M/D
        first_cell = cells[0]
        date_font = first_cell.find("font", attrs={"face": True})
        if date_font and re.search(r"\d+/\d+", date_font.get_text()):
            current_date_str = date_font.get_text(strip=True)
            day_font = first_cell.find("font", color="#959595")
            current_day = day_font.get_text(strip=True) if day_font else ""

        if len(cells) < 4:
            continue

        name_cell = cells[1]
        name_link = name_cell.find("a")
        if not name_link:
            continue

        name = name_link.get_text(strip=True)
        if not name or len(name) < 3:
            continue

        href = name_link.get("href", "")
        no_match = re.search(r"view\.php\?no=(\d+)", href)
        if not no_match:
            continue
        race_no = no_match.group(1)

        dist_font = name_cell.find("font", color="#990000")
        raw_distances = dist_font.get_text(strip=True) if dist_font else ""
        distances = normalize_distances(raw_distances) if raw_distances else []

        venue_cell = cells[2]
        venue = venue_cell.get_text(strip=True)

        org_cell = cells[3]
        org_text = org_cell.get_text(" ", strip=True)
        org_lines = [l.strip() for l in org_text.split() if l.strip()]
        organizer = org_lines[0] if org_lines else ""

        phone_m = re.search(r"☎\s*([\d\-]+)", org_text)
        phone = phone_m.group(1) if phone_m else ""

        website_link = org_cell.find("a", href=lambda h: h and h.startswith("http") and "roadrun" not in h)
        website = website_link["href"] if website_link else ""

        excluded, reason = should_exclude(name)
        if excluded:
            log.info("Excluded '%s': %s", name, reason)
            continue

        if distances and max_distance_km(distances) < 5:
            log.info("Excluded '%s': all distances < 5K", name)
            continue

        races.append({
            "_no": race_no,
            "_date_str": current_date_str,
            "name": name,
            "distances": distances,
            "venue": venue,
            "organizer": organizer,
            "phone": phone,
            "website": website,
        })

    log.info("Found %d races from list page", len(races))
    return races


def scrape_detail(race_no: str) -> dict:
    url = f"{DETAIL_URL}?no={race_no}"
    try:
        html = fetch_decoded(url)
    except Exception as e:
        log.warning("Detail fetch failed for no=%s: %s", race_no, e)
        return {}

    soup = BeautifulSoup(html, "html.parser")
    data = {}

    rows = soup.select("table tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        label = cells[0].get_text(strip=True)
        value = cells[1].get_text(" ", strip=True)
        if "대회일시" in label:
            data["date_raw"] = value
        elif "대회종목" in label:
            data["distances_raw"] = value
        elif "대회지역" in label:
            data["city"] = value.strip()
        elif "대회장소" in label:
            data["address"] = value.strip()
        elif "주최단체" in label:
            data["organizer"] = value.strip()
        elif "접수기간" in label:
            data["reg_period"] = value.strip()
        elif "홈페이지" in label:
            links = cells[1].find_all("a", href=True)
            urls = [a["href"] for a in links if a["href"].startswith("http")]
            data["reg_url"] = urls[0] if urls else ""

    return data


def guess_year(date_str: str, race_name: str) -> int:
    m = re.search(r"(20\d{2})", race_name)
    if m:
        return int(m.group(1))
    today = date.today()
    if date_str:
        parts = date_str.split("/")
        if len(parts) == 2:
            month = int(parts[0])
            if month < today.month:
                return today.year + 1
    return today.year


def build_race(raw: dict, detail: dict) -> dict | None:
    name = raw["name"]
    year = guess_year(raw["_date_str"], name)

    date_iso = ""
    start_time = ""
    if detail.get("date_raw"):
        date_iso = parse_korean_date(detail["date_raw"])
        start_time = parse_start_time(detail["date_raw"])
    elif raw["_date_str"]:
        parts = raw["_date_str"].split("/")
        if len(parts) == 2:
            date_iso = f"{year}-{int(parts[0]):02d}-{int(parts[1]):02d}"

    distances = normalize_distances(detail.get("distances_raw", "")) or raw["distances"]

    if not distances:
        log.info("No distances for '%s', skipping", name)
        return None
    if max_distance_km(distances) < 5:
        log.info("Excluded '%s': max distance < 5K", name)
        return None

    city = detail.get("city", "")
    address = detail.get("address", raw.get("venue", ""))
    province = detect_province(city + " " + address)
    if not province:
        province = detect_province(raw.get("venue", ""))

    reg_period = detail.get("reg_period", "")
    reg_start = ""
    reg_end = ""
    if reg_period:
        parts = re.split(r"~|～", reg_period)
        if len(parts) >= 1:
            reg_start = parse_korean_date(parts[0])
        if len(parts) >= 2:
            reg_end = parse_korean_date(parts[1])

    status = detect_status(reg_start, reg_end, date_iso)

    website = detail.get("reg_url", "") or raw.get("website", "")
    source_url = f"{DETAIL_URL}?no={raw['_no']}"

    race_id = f"rrc-{raw['_no']}"

    return {
        "id": race_id,
        "name": name,
        "date": date_iso,
        "start_time": start_time,
        "location": {
            "address": address,
            "city": city,
            "province": province,
            "lat": None,
            "lng": None,
        },
        "distances": distances,
        "organizer": detail.get("organizer", raw.get("organizer", "")),
        "contact": {"phone": raw.get("phone", "")},
        "registration_url": website,
        "registration_start": reg_start,
        "registration_deadline": reg_end,
        "source_url": source_url,
        "status": status,
    }


def main():
    parser = argparse.ArgumentParser(description="Marathon Korea scraper (roadrun.co.kr)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--max-detail", type=int, default=0,
                        help="Max detail pages to fetch (0=all)")
    args = parser.parse_args()

    output_path = (Path(args.output) if args.output
                   else Path(__file__).parent.parent / "public" / "races.json")

    raw_races = scrape_list()
    if not raw_races:
        log.error("No races from list page — aborting")
        sys.exit(1)

    limit = args.max_detail if args.max_detail > 0 else len(raw_races)
    log.info("Fetching detail pages for %d races...", min(limit, len(raw_races)))

    built = []
    for i, raw in enumerate(raw_races[:limit]):
        log.info("[%d/%d] %s (no=%s)", i + 1, min(limit, len(raw_races)), raw["name"], raw["_no"])
        detail = scrape_detail(raw["_no"])
        race = build_race(raw, detail)
        if race:
            built.append(race)

    built.sort(key=lambda r: r.get("date", ""))
    log.info("Built %d races after filtering", len(built))

    if not built:
        log.error("No races built — keeping existing file")
        sys.exit(1)

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "races": built,
    }
    content = json.dumps(output, ensure_ascii=False, indent=2)

    if args.dry_run:
        log.info("[DRY RUN] Would write %d bytes, %d races", len(content), len(built))
        print(content[:2000])
        return

    tmp = output_path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(output_path)
    log.info("Wrote %d races to %s", len(built), output_path)


if __name__ == "__main__":
    main()
