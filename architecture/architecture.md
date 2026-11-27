# Investopia 아키텍처

![시스템 아키텍처](./architecture.png)

[SVG 원본](./architecture.svg)

## 구조 요약

- 네이버 금융 종목 페이지에서 시세를 수집해 MariaDB에 저장하고, 웹과 Raspberry Pi에서 모의 매수·매도를 하는 Flask 프로토타입입니다.
- 웹 화면과 Raspberry Pi는 같은 `POST /api/buy`, `POST /api/sell` API로 주문하고, Raspberry Pi는 표시용 시세·자산을 MariaDB에서 직접 읽습니다.
- 시세 수집기는 별도 Python 스크립트로 30초 간격으로 돌며 `stock` 테이블에 upsert합니다.
- 저장소에 배포 설정은 없고, GitHub Actions는 pytest만 실행합니다.

## 조사 기준

| 항목 | 값 |
| --- | --- |
| 분석일 | 2026-11-26 |
| 저장소 | [stdiodh/Investopia](https://github.com/stdiodh/Investopia) |
| 확인한 브랜치 | 분석일 시점 `main` |
| 대상 환경 | 코드 기준 논리 구조 (배포 설정 없음) |
| 경로 변경 | 2026-11-27 패키지 정리로 모듈 경로가 바뀌었습니다. 아래 근거 링크는 분석 시점 커밋 기준이고, 현재 경로는 [패키지 구조 정리](../docs/refactoring/2026-11-package-structure.md)에 있습니다. |

## 근거표

| 도면의 구성요소·연결·경계 | 의미 | 근거 | 환경 | 확인 상태 |
| --- | --- | --- | --- | --- |
| Investopia Web | Flask 서버 렌더링 화면과 REST API | [app.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/app.py) (`/`, `/stocks`, `/asset`, `/api/buy`, `/api/sell`) | 공통 | 코드·설정 확인 |
| Web → MariaDB | `pymysql`로 자산·포트폴리오·시세 조회와 갱신 | [app.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/app.py) (`pymysql.connect`) | 공통 | 코드·설정 확인 (DB 호스트는 환경 변수) |
| Price Collector → Naver Finance | 종목 페이지 HTML 수집 | [static/update_prices.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/static/update_prices.py) (`NAVER_FINANCE_URL`) | 공통 | 코드·설정 확인 |
| Price Collector → MariaDB | `stock` upsert | [static/update_prices.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/static/update_prices.py) | 공통 | 코드·설정 확인 |
| Raspberry Pi → Web | 버튼 입력으로 매수·매도 API 호출 | [static/hardware.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/static/hardware.py) (`INVESTOPIA_SERVER_URL`) | 공통 | 코드·설정 확인 |
| Raspberry Pi → MariaDB | LCD 표시용 시세·자산 조회 | [static/hardware.py](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/static/hardware.py) (`pymysql.connect`) | 공통 | 코드·설정 확인 |
| GitHub Actions | pytest (Python 3.12) | [test.yml](https://github.com/stdiodh/Investopia/blob/5c8ca52063d31039948de919d47042d058211da0/.github/workflows/test.yml) | CI | 코드·설정 확인 |

## 로고 출처

| 기술·제품 | 사용 파일 | 공식 출처 | 확인일 |
| --- | --- | --- | --- |
| Flask | `assets/logos/flask.svg` | [palletsprojects.com](https://palletsprojects.com/) | 2026-11-26 |
| Python | `assets/logos/python.svg` | [python.org/community/logos](https://www.python.org/community/logos/) | 2026-11-26 |
| MariaDB | `assets/logos/mariadb.svg` | [mariadb.com/about-us/logos](https://mariadb.com/about-us/logos/) | 2026-11-26 |
| GitHub | `assets/logos/github.svg` | [brand.github.com/foundations/logo](https://brand.github.com/foundations/logo) | 2026-11-26 |

## 확인 필요 사항

- 웹 서버, 수집기, MariaDB가 같은 호스트에서 도는지는 환경 변수 값이라 확인하지 못해 실행 경계를 그리지 않았습니다.
