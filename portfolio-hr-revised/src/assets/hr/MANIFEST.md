# HR portfolio evidence assets

모든 자산은 실제 프로젝트 화면, 저장소 기록 또는 기존 디자인 원본에서 가져왔다. 생성형 이미지는 사용하지 않았으며, 화면 시안과 운영 화면을 구분해 표시한다.

| 파일 | 크기 | SHA-256 | 출처와 사용 범위 |
| --- | ---: | --- | --- |
| `../aandi-architecture.png` | 1672×941 | `2510dedde136f279c9533035e9433483ac7a29f5bc29b5df528fa89af4390900` | 사용자가 제공한 A-AND-I 아키텍처 원본. 기존 `portfolio/src/assets/aandi-architecture.png`와 동일하며 수정하지 않음. |
| `evidence-v2/aandi-assignment-list-content.png` | 2304×1296 | `784eaed7d15e2e47bb598ad1ce1160994b6280037ea9019f073e33cec8658cb2` | A&I `assignment-operation.mov` 약 2.67초 프레임의 콘텐츠 영역. 실제 운영 과제 목록을 업스케일 없이 16:9로 크롭. |
| `evidence-v2/aandi-repository-call-record-clean.png` | 2400×1700 | `1c84ddd8c724da96fd7a66a6d02b1a6bb087785a2c130bae015a65d2133e232f` | `assignment-read-query-evidence.json`과 `AssignmentQueryServiceUserTest.kt` 원문 발췌. service-level 호출 60→2이며 MongoDB command 수가 아님. |
| `evidence-v2/aandi-p95-record.png` | 2400×1400 | `2edf6e16f1a657d66ba1e891de8e756915121955324569e47e9b857db301fb54` | `2026-07-09-assignment-list-before-after.md`의 측정 조건과 결과 원문 발췌. 로컬 고정부하 P95 9.297→7.565ms. |
| `gojjibom-one-touch.png` | 1600×900 | `1973b035a4453b643023c0587938c8d6122685902a58874f7d39442b290fa6d6` | 기존 `portfolio/src/assets/gojjibom-one-touch.png`의 동일 파일. 알림→카메라→복약 기록과 보호자 설정을 보여주는 제품 흐름. |
| `didimlog-boj.png` | 1200×750 | `6d153b02abc7175927c420fbc47ebcef3638c82638169027cfd74071cae2f084` | 디딤로그 BOJ 가입 시연 GIF의 2초 프레임. BOJ ID와 인증 흐름을 보여주는 실제 시연 화면. |
| `investopia-hardware.png` | 1920×1080 | `7ca1e42bac6570362fe461fea2d517105c0a64261a773f7b02294f9b46c70d2c` | GitHub user attachment 원본. Raspberry Pi LCD·버튼·LED·로터리 인코더가 보이는 실제 회로 화면. |
| `evidence-v2/home-recommendations.png` | 390×1198 | `7e6d1445015efbd71cce054c6caf5427b2c0dcfe1630a0a3c183d88a5648f38e` | SoloPlay commit `214bdbc`의 Figma UI/UX 시안 원본. 배포 화면이 아니며 서비스 맥락 설명에만 사용. |

## 사용 메모

- A&I 운영 화면은 16:9 포트폴리오 영역에서 내용을 읽을 수 있도록 원본 프레임을 크롭했으며 확대하지 않았다.
- A&I 수치 이미지는 저장소 원문을 다시 그린 그래프가 아니라 경로·조건·값이 보이는 기록 발췌다.
- SoloPlay 화면은 사용자에게 보이는 장소 추천과 태그의 위치를 설명하지만 Gemini 생성 결과 자체를 증명하지 않는다. 해당 주장은 코드와 테스트 결과로 분리해 표시한다.
- 기사 사진·매체 로고는 복제하지 않고 원문 링크만 사용한다.
