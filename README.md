# 마라톤 코리아 🏃

한국 마라톤 대회 일정 & 신청 조회 PWA

## 시작하기

### 1. 환경 변수 설정
```bash
cp .env.example .env
# .env에 VITE_KAKAO_MAP_KEY 값 입력
# 카카오 개발자 콘솔: https://developers.kakao.com
```

### 2. 개발 서버 실행
```bash
npm install
npm run dev
```

### 3. 빌드
```bash
npm run build
npm run preview
```

## 기술 스택
- Vue 3 + Vite + TypeScript
- vite-plugin-pwa (Workbox)
- Kakao Maps API
- vue-cal
- Pinia
- Tailwind CSS

## 데이터 갱신
`scraper/` 디렉토리의 Python 스크래퍼가 마라톤온라인에서 데이터를 수집합니다.
GitHub Actions가 매주 월요일 자동 실행합니다.

## PWA 설치
브라우저 주소창의 "설치" 버튼 또는 "홈 화면에 추가"를 클릭하세요.
