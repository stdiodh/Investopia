# INVESTOPIA

> 이상적인 투자 연습 공간을 제공하는 모의 주식 투자 시스템

---

## 🧑‍💻 팀 정보
- **1조**: 허동현, 김진석, 이준호, 김지해, 손민석  
- **소속**: 인덕대학교 3학년 B반

---

## 👥 팀원 역할 분담

| 이름     | 역할 및 담당 업무 |
|----------|------------------|
| **허동현** (팀장) | - 프로젝트 기획 및 설계 총괄<br>- 웹 서버 + DB 개발 및 연동<br>- 보고서 작성 |
| **김지해** | - UI 웹 디자인 및 설계<br>- PPT 제작 보조<br>- 회의록 작성 |
| **김진석** | - 회로도 설계<br>- 회로도 구축 및 최적화<br>- 센서 담당 |
| **손민석** | - 설계 시각화 담당<br>- 회의록 작성<br>- 발표 대본 작성 |
| **이준호** | - UI 웹 디자인 및 설계<br>- 회로도 구축<br>- PPT 제작<br>- 파이썬 코드 작성 |

---

## 🔍 프로젝트 개요

> 대학생 및 사회초년생이 실제 투자 환경에 가까운 시스템을 경험하며 <br>
> 주식 및 자산 투자에 대한 이해를 높이기 위한 시뮬레이션 플랫폼입니다.

<p align="center">
  <img src="https://github.com/user-attachments/assets/d4b25040-99d2-4f51-9192-c69a92a996d3" width="600"/>
</p>

---

## ⏰ 개발 기간

- **2025년 04월 28일 ~ 2025년 06월 17일**

---

## 💡 프로젝트 구성

### 🔗 웹 서버

- Flask 기반 REST API 제공  
- 주요 API:
  - `POST /api/buy` : 주식 매수
  - `POST /api/sell` : 주식 매도
- 사용자 포트폴리오 및 자산 실시간 조회 기능 제공

<p align="center">
  <img src="https://github.com/user-attachments/assets/09603ea7-c36c-4c59-9668-2783f6433365" width="500"/>
</p>

---

### 🕸 크롤링 시스템

- `update_prices.py`를 통해 네이버 금융에서 실시간 주가 크롤링
- `stock` 테이블에 현재가, 변동률 자동 업데이트

---

### 🧾 데이터베이스

<p align="center">
  <img src="https://github.com/user-attachments/assets/113d3617-13af-4f66-b7d7-539fe00309d7" width="550"/>
</p>

- 테이블 구성: `user_asset`, `portfolio`, `stock`
- ERD 기반의 구조적 데이터 관리

---

### 🔧 하드웨어 연동 (Raspberry Pi)

<p align="center">
  <img src="https://github.com/user-attachments/assets/2d0ee675-085f-474d-9399-f523197b2f7c" width="500"/>
</p>

- **디스플레이**: LCD에 종목 정보 출력  
- **입출력 장치**: 조이스틱으로 종목 선택, 버튼으로 매수/매도
- **피드백**: 수익/손실에 따라 LED 및 Buzzer 작동

---

### 🌐 웹 프론트엔드

- **index.html** – 자산 현황 및 수익률 파이차트 시각화  
  <p align="center">
    <img src="https://github.com/user-attachments/assets/fb087d7d-bfba-483e-a57f-eb4b0c7da67b" width="550"/>
  </p>

- **stocks.html** – 종목 리스트, 거래(매수/매도) 기능  
  <p align="center">
    <img src="https://github.com/user-attachments/assets/f808877f-0673-4f53-bcb0-9ba57fee895a" width="550"/>
  </p>

- **asset.html** – 자산 입력 및 설정 기능  
  <p align="center">
    <img src="https://github.com/user-attachments/assets/8f381ae0-7755-4a8c-9dc9-d72a94c7f27a" width="500"/>
  </p>

---

## ⚙ 아키텍처

- **Backend**: Flask
- **DB**: MariaDB
- **Frontend**: HTML + CSS + JS (Chart.js)
- **Hardware**: Raspberry Pi, LCD, Buzzer, LED, Joystick

---

## 🧪 시연 영상 및 예시

### 1. 웹 UI에서 종목 매수
<p align="center">
  <img src="https://github.com/user-attachments/assets/c809936a-cac8-461f-a754-cf25659a9bb2" width="500"/>
</p>

### 2. 실시간 주가 업데이트

- `update_prices.py` 실행 시 DB 내 주가 자동 갱신

### 3. 하드웨어 LCD 화면 실시간 종목 출력  
<p align="center">
  <img src="https://github.com/user-attachments/assets/c0e714f6-5055-483a-ab2b-6965fad2dead" width="500"/>
</p>

### 4. 버튼을 통한 매수 / 매도
<p align="center">
  <img src="https://github.com/user-attachments/assets/afae5981-c73e-4c8b-a6fe-c3daad30461f" width="350"/>
  <img src="https://github.com/user-attachments/assets/cf3702aa-ab32-4b67-8c0b-758a0507263b" width="350"/>
</p>

---

## ⚠️ 구현의 한계

1. **LCD 한글 출력 불가**  
→ 종목 이름 대신 종목 코드 표시  
<p align="center">
  <img src="https://github.com/user-attachments/assets/99f7c1dd-4c39-4d6b-8ed6-9f78eec14148" width="400"/>
</p>

2. **실시간 반영 지연**  
→ DB 변경이 LED/Buzzer에 즉시 반영되지 않음  
<p align="center">
  <img src="https://github.com/user-attachments/assets/db302a07-064c-414c-900e-f42a0063a517" width="400"/>
</p>

---

## 📈 프로젝트 성과

<p align="center">
  <img src="https://github.com/user-attachments/assets/2d2a10a3-0fcf-4f0d-baab-28f6d7397d92" width="500"/>
</p>

- 실제 투자 흐름과 유사한 시스템을 구축함으로써 이론을 실전으로 전환
- API, DB, 크롤링, 하드웨어까지 통합한 종합 프로젝트 경험
- 팀워크 및 협업, 시각적 결과물에 대한 만족감

---
