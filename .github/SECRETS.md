# GitHub Secrets 설정 방법

이 레포지토리에는 두 개의 GitHub Secret이 필요합니다.

## 설정 위치
GitHub 레포 → Settings → Secrets and variables → Actions → New repository secret

## 필요한 Secrets

| 이름 | 설명 | 어디서 발급 |
|------|------|------------|
| `VITE_KAKAO_MAP_KEY` | 카카오 지도 JavaScript 키 | [카카오 개발자 콘솔](https://developers.kakao.com) > 앱 > 앱 키 > JavaScript 키 |
| `KAKAO_REST_API_KEY` | 카카오 지오코딩 REST API 키 | [카카오 개발자 콘솔](https://developers.kakao.com) > 앱 > 앱 키 > REST API 키 |

## 주의사항
- `VITE_KAKAO_MAP_KEY`는 카카오 콘솔에서 **허용 도메인을 Vercel 배포 URL로 제한**하세요
- `KAKAO_REST_API_KEY`는 서버(GitHub Actions)에서만 사용되므로 도메인 제한 불필요
