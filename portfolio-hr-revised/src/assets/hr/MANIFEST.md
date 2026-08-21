# HR portfolio evidence assets

모든 자산은 실제 프로젝트 화면 또는 기존 원본에서 가져왔다. 생성형 이미지는 사용하지 않았고, 크롭·업스케일·리사이즈를 하지 않았다. GIF 대표 프레임만 원본 캔버스 크기로 무손실 PNG 추출했다.

| 파일 | 크기 | SHA-256 | 출처와 선택 기준 |
| --- | ---: | --- | --- |
| `../aandi-architecture.png` | 1672×941 | `2510dedde136f279c9533035e9433483ac7a29f5bc29b5df528fa89af4390900` | 사용자가 제공한 A-AND-I 아키텍처 원본. 기존 `portfolio/src/assets/aandi-architecture.png`와 byte-for-byte 동일하며 이번 작업에서 수정하지 않음. |
| `aandi-judge.png` | 3824×2484 | `e6e3025196d6af268c3c9e022346ba58a0bfffa174ba6e1db98e0774e3468647` | `/Users/dh/Desktop/Code/A-AND-I-WEB-SERVER/docs/assets/gifs/problem-judge.gif`의 24초 지점. 세 테스트 케이스가 모두 `PASSED`로 표시되어 제출→채점 결과를 한 화면에서 확인할 수 있는 프레임. 원본 GIF SHA-256: `519b0f2ef119096b5d36042d6175bac14a6404388b059914806dc94588be21f4`. |
| `gojjibom-one-touch.png` | 1600×900 | `1973b035a4453b643023c0587938c8d6122685902a58874f7d39442b290fa6d6` | 기존 `portfolio/src/assets/gojjibom-one-touch.png`의 byte-for-byte 복사본. 알림 한 번→카메라→복약 기록 흐름과 보호자 설정을 함께 보여주는 원본 합성 화면. |
| `didimlog-boj.png` | 1200×750 | `6d153b02abc7175927c420fbc47ebcef3638c82638169027cfd74071cae2f084` | `/Users/dh/Desktop/Code/didim-log-BE/DOCS/assets/portfolio/01-boj-signup_demo.gif`의 2초 지점. BOJ ID, 인증 코드, 프로필 확인 링크와 인증 동작이 한 화면에 모인 프레임. 원본 GIF SHA-256: `20a464df94507112222bc826db4c2ea3756445ae8d1555695ddf6c04f137a581`. |
| `investopia-hardware.png` | 1920×1080 | `7ca1e42bac6570362fe461fea2d517105c0a64261a773f7b02294f9b46c70d2c` | GitHub user attachment [`2d0ee675-085f-474d-9399-f523197b2f7c`](https://github.com/user-attachments/assets/2d0ee675-085f-474d-9399-f523197b2f7c)의 byte-for-byte 다운로드본. LCD·버튼·LED·로터리 인코더가 표시된 실제 Raspberry Pi 회로 구성 화면. |

## 사용 메모

- A&I와 디딤로그 PNG는 정적 포트폴리오에서 GIF 자동 재생으로 인한 시각 피로를 피하기 위한 대표 프레임이다.
- Investopia의 저해상도 시연 GIF(240–342px)는 포함하지 않았다.
- Jinja 템플릿 토큰이 노출된 Investopia 웹 캡처는 포함하지 않았다.
- SoloPlay는 확인 가능한 실제 UI 원본이 없어 자산을 만들지 않았다.
