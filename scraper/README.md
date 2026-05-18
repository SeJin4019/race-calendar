# Marathon Scraper

마라톤온라인(marathon-online.co.kr)에서 대회 정보를 수집합니다.

## 설치

```bash
cd scraper
pip install -r requirements.txt
cp .env.example .env
# .env에 KAKAO_REST_API_KEY 입력
```

## 실행

```bash
# 실제 실행 (public/races.json 덮어쓰기)
python scrape.py

# 드라이런 (파일 쓰지 않고 미리보기)
python scrape.py --dry-run

# 출력 경로 지정
python scrape.py --output /path/to/races.json
```

## 주의사항

- 실행 전 marathon-online.co.kr의 robots.txt와 이용약관을 확인하세요
- 스크래퍼는 robots.txt를 자동으로 확인하고, 허용되지 않으면 중단합니다
- 요청 간 1-2초 딜레이가 적용됩니다
- 스크래핑 실패 시 기존 races.json은 유지됩니다 (atomic write)

## HTML 구조 변경 시

`scrape.py`의 `parse_race_row()` 함수에서 CSS 셀렉터를 수정하세요.
실제 사이트 구조를 크롬 개발자 도구로 확인 후 맞춰주세요.
