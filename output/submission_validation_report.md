# 이력서·포트폴리오 최종 제출 검증

검증일: 2026-08-22

## 최종 산출물

- 이력서 PDF: `output/pdf/toss_resume_submission_final.pdf`
  - 3페이지 A4
  - SHA-256: `5dcb57e3609fae7c1f2523c17475ff692ad4a3291aee85c8dd23a6a4824af3e8`
- 포트폴리오 PDF: `output/pdf/portfolio_submission_final_v2.pdf`
  - 9페이지, 1200 × 675.12pt
  - SHA-256: `38c0dd4b844e4585aac15055d9053b6881b3190da30bd44169a3e29abebf6c47`
- 이력서 Figma 복제본: https://www.figma.com/design/HgErN8Vnin2SQKjUuT4dD9?node-id=317-343
- 이전 포트폴리오 Figma 복제본: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C?node-id=29-750

기존 Figma 페이지와 기존 PDF는 덮어쓰지 않았다.

## 프로젝트 동기화 기준

| 프로젝트 | 기간·역할 | 이력서와 포트폴리오에 고정한 내용 | 상태·근거 |
| --- | --- | --- | --- |
| A&I.com | 2025.01–현재 · Backend Lead | 5개 서버 분리, 서비스 계층 호출 60→2회, P95 9.3→7.6ms | 운영 서비스, Web·Gateway 저장소, 측정 원문 |
| 고찌봄 | 2026.06–07 · PM · Dev Lead | 4일 MVP, 알림에서 복약 화면으로 바로 이동, 최고점·혁신상 | 공개 데모·샘플 데이터, 기사·주관기관 결과 |
| 디딤로그 | 2026.02–현재 · Maintainer | BOJ 5분 인증, Redis checkpoint, 3,400건 고정 샘플 검증 | 공개 데모·입력 미저장, 순차/K=4 로컬 측정 원문 |
| Investopia | 2025.04–06 · PL & Backend Lead | 거래 정합성, 가상 매수·매도, 30초 주가 수집, Raspberry Pi 연동 | 로컬·하드웨어 프로토타입, 저장소 |
| SoloPlay | 2024.10–2025.02 · Backend Lead | Kakao 원본 선저장, Gemini 보강 분리, 관련 테스트 시나리오 19개 | 백엔드 프로젝트·저장소 공개, 테스트 소스 2개·UI 시안 |

고찌봄 수상 표기는 [주관기관 결과](https://www.jdnc.or.kr/notice/news.htm?act=view&seq=1019)에 맞춰 `최고점·혁신상`으로 통일했다.

## 이력서 수정·검증

- 1페이지 상단에 GitHub, Velog, 이메일을 추가하고 링크를 연결했다.
- 프로젝트 순서를 `고찌봄 → 디딤로그 → Investopia → SoloPlay`로 맞췄다.
- `팀 MVP`, `2026.02–04`, 운영 수집처럼 읽히던 `4개씩 병렬 수집` 표현을 제거했다.
- 디딤로그는 최신 공개 README 기준 `2026.02–현재`, `3,400건 고정 샘플`로 수정했다.
- 2페이지의 네 프로젝트명을 각각 데모 또는 저장소에 연결했다.
- 날짜 구분자와 `Backend Lead` 표기를 통일했다.
- A&I 소개의 고아 줄바꿈을 정리하고, `60→2회`를 서비스 계층 호출 기준으로 명시했다.
- 디딤로그의 checkpoint 결과를 `실패·미처리 항목만 재수집`으로 포트폴리오와 맞췄다.
- PDF는 Figma 4× 시각 레이어(약 288dpi)와 내장 Pretendard 검색 레이어를 함께 사용했다.
- `Server Developer`, `Kotlin`, `PostgreSQL`, `GitHub Actions`, 다섯 프로젝트명이 정확히 검색된다.
- Type3 글꼴 0개, 링크 annotation 12개, 고유 링크 10개를 확인했다.

## 포트폴리오 수정·검증

- 제목·본문·캡션에서 반복하던 설명과 문서 구성 안내를 삭제했다.
- 장식용 영문 라벨을 한글로 바꾸고 A&I 사례의 STAR 표기를 문제·조건·선택·적용으로 줄였다.
- `했습니다` 종결은 24회에서 7회로 줄였고 사실·수치·기간·역할은 유지했다.
- 고찌봄 수상 결과는 주관기관 카드 한 곳에만 남겼다.
- 고찌봄 역할을 이력서·프로젝트 맵·상세 페이지 모두 `PM · Dev Lead`로 통일했다.
- 디딤로그 기간과 측정 조건을 수정하고 공개 측정 원문을 연결했다.
- Investopia의 동일 결과·30초 수치 반복을 줄였다.
- SoloPlay의 `실패 0` 단정 대신 공개 소스로 확인되는 테스트 시나리오 19개와 두 테스트 파일을 연결했다.
- 9페이지의 상태·저장소·검증 링크와 이메일을 상세 페이지에 맞췄다.
- 링크 annotation 32개, 고유 링크 19개를 확인했다.

## 자동·수동 검증 결과

- `npm run typecheck` 통과
- `npm run lint` 통과
- `npm run build` 통과
- `npm run qa` 17/17 통과
  - 9/9장 1600 × 900
  - slide 밖 요소 0
  - 잘린 요소 0
  - 업스케일 이미지 0
  - 화면·인쇄 숨은 링크 0
- 두 PDF에서 금칙 문구와 이전 기간이 검색되지 않음을 확인했다.
- PDF에 포함된 HTTP(S) 고유 링크 20개 중 19개가 비로그인 HTTP 검사에서 200으로 응답했다.
- 비로그인 요청을 차단한 SoloPlay Figma 링크는 Figma에서 `66:2` 페이지를 직접 조회해 유효성을 확인했다.
- 두 PDF를 PNG로 다시 렌더링해 겹침, 잘림, 깨진 글리프, 검은 사각형이 없음을 확인했다.

## 원본 보존 확인

- `/Users/dh/Documents/toss_resume.pdf`
  - SHA-256: `1ed0eb1b1d4a6a1f134604708dba12fae3ea4c82b2d66d1433559e330d6dd49e`
- `output/pdf/portfolio_submission_final.pdf`
  - SHA-256: `256554be312a9ffce6b6d24a6b7d90984647c5b3b95a224f4d2cb9e07aea35cf`
- `output/pdf/portfolio_evidence_revised.pdf`
  - SHA-256: `1c38d9b892598b81701e99510f027450497b6f5a23d26c69c1102ddf4ed423d3`
