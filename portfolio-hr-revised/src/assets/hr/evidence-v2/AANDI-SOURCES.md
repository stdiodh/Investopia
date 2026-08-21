# A&I evidence v2

이 문서는 포트폴리오 3·4페이지에 사용할 A&I 증거 이미지의 출처와 해석 범위를 고정합니다.

## 운영 화면

원본:

- `/Users/dh/Desktop/Code/A-AND-I-WEB-SERVER/docs/assets/videos/assignment-operation.mov`
- 원본 크기: `3824 × 2484`, 길이 `8.413333초`, H.264
- SHA-256: `0b797b006c3b2475e6367a94e5ea85808c98f8c09f20367885761830baeff495`
- 해당 파일 최근 커밋: `7df5142` (`2026-06-14T13:04:59+09:00`)

선별 명령:

```bash
ffmpeg -i assignment-operation.mov -vf "fps=1.5" -vsync vfr frame-%02d.png
```

- 선별 프레임 05, 약 `2.67초`의 과제 목차 화면을 사용했습니다.

콘텐츠 크롭:

```bash
magick frame-05.png -crop 2304x1296+760+380 +repage aandi-assignment-list-content.png
```

정확한 의미:

- 목록 이미지는 A&I의 과정별 과제 목차가 실제 UI로 렌더링된다는 증거입니다.
- 이 이미지는 현재 가동률, 처리량, 제출 성공 또는 채점 결과를 증명하지 않습니다.

## P95 측정 기록

원본:

- `/Users/dh/Desktop/Code/A-AND-I-WEB-SERVER/docs/performance/results/2026-07-09-assignment-list-before-after.md`
- SHA-256: `f0eeb57f917ad911f749d8d6acb09590d83da2eac8cc5fd3d6513e4d67c76393`
- 해당 파일 최근 커밋: `4d9715f` (`2026-07-11T18:43:18+09:00`)
- 구조화 원본: `2026-07-09-assignment-list-before-after.json`
- 구조화 원본 SHA-256: `e787f2ae0155b8b13a43ba6744ea5662f1d4e386fcbaaf56a1deddb5f76a44ad`

출력:

- `aandi-p95-record.png` (`2400 × 1400`)
- 원문에서 보존한 값: 과제 `30개`, 목록 `100%`, `100 RPS`, `2분 × 3회`, P95 `9.297 ms → 7.565 ms`, HTTP 실패율 `0.00%`, check 성공률 `100.00%`, dropped iterations `0`
- 출력 SHA-256: `2edf6e16f1a657d66ba1e891de8e756915121955324569e47e9b857db301fb54`

정확한 의미:

- 같은 로컬 고정부하 조건에서 과제 목록 API P95 중앙값을 비교한 회귀 측정입니다.
- 운영 최대 처리량 또는 운영 환경의 응답 시간을 뜻하지 않습니다.

## Repository 호출 기록

원본:

- `/Users/dh/Desktop/Code/A-AND-I-WEB-SERVER/performance/results/assignment-read-query-evidence.json`
- SHA-256: `de57d4f46d1b34f71a61f750930a242f9205172e6c8faff050bc97f8ddd4098f`
- 해당 파일 최근 커밋: `642cfd3` (`2026-06-23T14:43:28+09:00`)
- `/Users/dh/Desktop/Code/A-AND-I-WEB-SERVER/src/test/kotlin/com/example/aandi_post_web_server/assignment/application/service/AssignmentQueryServiceUserTest.kt`
- SHA-256: `72f0e01b088bfe83454e1b42607ed58e7ba09315ad1c8d211dcbde9998c3c61a`
- 해당 테스트 최근 커밋: `00f1934` (`2026-07-11T14:31:42+09:00`)

출력:

- `aandi-repository-call-record-clean.png` (`2400 × 1700`)
- 출력 SHA-256: `1c84ddd8c724da96fd7a66a6d02b1a6bb087785a2c130bae015a65d2133e232f`
- 계산식 필드는 발췌하지 않았습니다.

정확한 의미:

- `60`은 기존 구조에 대해 기록된 service-level 예상 child repository 호출 형태입니다.
- `2`는 과제 수 `30개`에서도 requirement batch와 testcase batch가 각각 `times(1)`임을 현재 회귀 테스트 코드가 검증하는 호출 형태입니다.
- 이 값은 MongoDB command count가 아닙니다.
- 이번 자산 준비 과정에서는 대상 저장소에 빌드 산출물을 만들지 않기 위해 테스트를 다시 실행하지 않았습니다. 현재 문서에 기록된 등가 명령은 다음과 같습니다.

```bash
./gradlew test --tests 'com.example.aandi_post_web_server.assignment.application.service.AssignmentQueryServiceUserTest'
```

## 렌더링

- 외부 이미지나 생성형 이미지를 사용하지 않았습니다.
- Apple SD Gothic Neo와 D2Coding 로컬 글꼴을 사용해 저장소 원문 발췌를 2배 해상도로 캡처했습니다.
