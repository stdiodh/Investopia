import type { ReactNode } from "react";

import aandiArchitecture from "../assets/aandi-architecture.png";
import didimlogSignupPoster from "../assets/didimlog-signup-poster.png";
import gojjibomOneTouch from "../assets/gojjibom-one-touch.png";

const LINKS = {
  aandi: "https://aandiclub.com/",
  aandiGateway: "https://github.com/Team-AnI/A-AND-I-GATEWAY-SERVER",
  didimlog: "https://github.com/didim-log/didim-log-BE",
  didimlogSignup:
    "https://raw.githubusercontent.com/didim-log/didim-log-BE/main/DOCS/assets/portfolio/01-boj-signup_demo.gif",
  didimlogCrawler:
    "https://raw.githubusercontent.com/didim-log/didim-log-BE/main/DOCS/assets/portfolio/02-crawler-pipeline_demo.gif",
  github: "https://github.com/stdiodh",
  gojjibom: "https://gojjibom.web.app/",
  gojjibomBackend: "https://github.com/TIKI-TAKA-hackathon/Tiki-Taka-BE",
  gojjibomDemo:
    "https://raw.githubusercontent.com/TIKI-TAKA-hackathon/Tiki-Taka-FE/main/docs/assets/flows/demo-notification-flow.gif",
  investopia: "https://github.com/stdiodh/Investopia",
  investopiaDemo:
    "https://github.com/user-attachments/assets/c809936a-cac8-461f-a754-cf25659a9bb2",
  soloplay: "https://github.com/SangWook16074/Solo-Play-Web-Server",
  velog: "https://velog.io/@stdiodh/posts",
} as const;

type SlideProps = {
  children: ReactNode;
  id: string;
  number: string;
};

function Slide({ children, id, number }: SlideProps) {
  return (
    <section className="slide" id={id}>
      <div className="slide-body">{children}</div>
      <footer className="slide-footer">
        <span>허동현 · Portfolio 2026</span>
        <span>{number} / 10</span>
      </footer>
    </section>
  );
}

function SectionLabel({ number, children }: { number: string; children: ReactNode }) {
  return (
    <div className="section-label">
      <span>{number}</span>
      <span className="section-label-line" aria-hidden="true" />
      <span>{children}</span>
      <span className="section-label-rule" aria-hidden="true" />
    </div>
  );
}

function Link({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a className="text-link" href={href} rel="noreferrer" target="_blank">
      {children} <span aria-hidden="true">↗</span>
    </a>
  );
}

function ActionList({ items }: { items: string[] }) {
  return (
    <ol className="action-list">
      {items.map((item, index) => (
        <li key={item}>
          <span>{String(index + 1).padStart(2, "0")}</span>
          <p>{item}</p>
        </li>
      ))}
    </ol>
  );
}

type Metric = {
  label: string;
  note?: string;
  value: string;
};

function MetricRail({ metrics }: { metrics: Metric[] }) {
  return (
    <dl className="metric-rail">
      {metrics.map((metric) => (
        <div key={`${metric.value}-${metric.label}`}>
          <dt>{metric.value}</dt>
          <dd>{metric.label}</dd>
          {metric.note && <small>{metric.note}</small>}
        </div>
      ))}
    </dl>
  );
}

function Stack({ children }: { children: ReactNode }) {
  return <p className="stack">{children}</p>;
}

function Problem({ children }: { children: ReactNode }) {
  return (
    <div className="problem">
      <span>Problem</span>
      <p>{children}</p>
    </div>
  );
}

function EvidenceArrow({ label }: { label: string }) {
  return (
    <div className="evidence-arrow" aria-label={label}>
      <svg aria-hidden="true" viewBox="0 0 180 42">
        <path d="M4 22 C46 15 100 28 165 17" />
        <path d="M153 9 L168 17 L155 27" />
      </svg>
      <span>{label}</span>
    </div>
  );
}

function FlowArrow() {
  return (
    <svg className="flow-arrow" aria-hidden="true" viewBox="0 0 64 26">
      <path d="M2 14 C20 9 39 17 58 11" />
      <path d="M50 4 L60 11 L51 20" />
    </svg>
  );
}

function CoverSlide() {
  return (
    <Slide id="cover" number="01">
      <div className="cover-layout">
        <div>
          <p className="eyebrow">SERVER DEVELOPER PORTFOLIO · 허동현</p>
          <h1>
            문제를 고치고,
            <br />
            달라진 결과를
            <br />
            <em>수치로 확인합니다.</em>
          </h1>
          <p className="lead cover-lead">
            Kotlin과 Spring Boot를 중심으로 2년간 5개 프로젝트를 진행했습니다.
            <br />
            성능, 테스트, 배포, 운영까지 직접 확인하며 서버를 다뤘습니다.
          </p>
          <EvidenceArrow label="구현에서 검증까지" />
        </div>
        <MetricRail
          metrics={[
            { value: "2,011개", label: "자동화 테스트" },
            { value: "78.2%", label: "평균 Line Coverage" },
            { value: "5개", label: "A&I.com 서비스" },
            { value: "1위 · 팀 MVP", label: "2026 AI Re-Local" },
          ]}
        />
      </div>
    </Slide>
  );
}

function ProfileSlide() {
  const projects = [
    ["A&I.com", "BE Lead · 2025.01–현재", "서버 저장소 5개 · 병합 PR 195개"],
    ["SoloPlay", "BE Lead · 2024.10–2025.02", ""],
    ["Investopia", "PL · BE Lead · 2025.04–06", ""],
    ["디딤로그", "Maintainer · 2026.02–04", ""],
    ["고찌봄", "PM · Dev Lead · 2026.06–07 · 4일", ""],
  ];

  return (
    <Slide id="profile" number="02">
      <SectionLabel number="02">PROFILE</SectionLabel>
      <div className="profile-layout">
        <div className="profile-copy">
          <div>
            <h2>
              서버를 만들고 운영하면서,
              <br />
              확인할 수 있는 결과를
              <br />
              남겨 왔습니다.
            </h2>
            <p className="lead">
              기능 구현만으로 끝내지 않고 DB 조회 수, 응답 시간, 테스트 수, 배포 시간처럼 다시
              확인할 수 있는 값을 남겼습니다.
            </p>
          </div>
          <div className="skill-note">
            <span>SKILLS</span>
            <p>
              Kotlin · Java · Spring Boot · Go · PostgreSQL · MongoDB · Redis · AWS · Docker ·
              GitHub Actions
            </p>
          </div>
        </div>
        <ol className="project-ledger" aria-label="프로젝트 경력">
          {projects.map(([name, role, result], index) => (
            <li key={name}>
              <span className="ledger-index">0{index + 1}</span>
              <div>
                <strong>{name}</strong>
                <p>{role}</p>
              </div>
              {result && <em>{result}</em>}
            </li>
          ))}
        </ol>
      </div>
    </Slide>
  );
}

function AandiArchitectureSlide() {
  return (
    <Slide id="aandi-architecture" number="03">
      <SectionLabel number="03">A&I.COM · BACKEND LEAD · 2025.01–현재</SectionLabel>
      <div className="project-layout architecture-layout">
        <div className="project-copy">
          <div>
            <h2>
              하나의 서버를
              <br />5개 서비스로 나눴습니다.
            </h2>
            <p className="lead">
              1년 6개월 넘게 운영 중인 교육 커뮤니티입니다. Auth, Web, Gateway, Tech Blog,
              Online Judge를 서비스별로 나눠 변경과 배포 범위를 줄였습니다.
            </p>
          </div>
          <Problem>기능이 한 서버에 모여 있어 서비스별로 변경하고 배포하기 어려웠습니다.</Problem>
          <ActionList
            items={[
              "Auth, Web, Gateway, Tech Blog, Online Judge를 5개 서버 저장소로 분리했습니다.",
              "AWS SNS/SQS로 서비스 사이의 이벤트 전달을 구성했습니다.",
              "GitHub Actions와 AWS ECR·EC2로 서비스별 배포 흐름을 만들었습니다.",
            ]}
          />
          <div className="link-row">
            <Link href={LINKS.aandi}>A&I.com</Link>
            <Link href={LINKS.aandiGateway}>Gateway Repo</Link>
          </div>
        </div>
        <figure className="primary-figure architecture-figure">
          <img src={aandiArchitecture} alt="A&I.com 5개 서비스 아키텍처" />
          <figcaption>
            실제 운영 구성 · Auth / Web / Gateway / Tech Blog / Online Judge
          </figcaption>
        </figure>
      </div>
      <MetricRail
        metrics={[
          { value: "5개", label: "서버 저장소 운영" },
          { value: "195개", label: "병합 PR" },
          { value: "독립 배포", label: "서비스별 변경 범위 분리" },
        ]}
      />
    </Slide>
  );
}

function OperationsEvidence() {
  return (
    <div className="technical-note operations-note" aria-label="A&I.com 성능과 운영 검증 결과">
      <p className="note-label">measured evidence / repository & CI records</p>
      <div className="before-after">
        <div>
          <span>DB QUERY</span>
          <strong>60회</strong>
          <small>과제별 반복 조회</small>
        </div>
        <FlowArrow />
        <div className="after">
          <span>BATCH QUERY</span>
          <strong>2회</strong>
          <small>P95 9.297ms → 7.565ms</small>
        </div>
      </div>
      <div className="evidence-rule" />
      <div className="ci-evidence">
        <div>
          <span>자동화 테스트</span>
          <strong>188 → 456</strong>
          <small>현재 Line 92.00% · Branch 66.09%</small>
        </div>
        <div>
          <span>CI</span>
          <strong>140.0초 → 109.0초</strong>
          <small>중복 검증 정리 · 22.1% 단축</small>
        </div>
      </div>
      <p className="evidence-footnote">
        테스트 수와 현재 커버리지는 소스 범위가 달라 단순 전후 커버리지 비교로 사용하지 않았습니다.
      </p>
    </div>
  );
}

function AandiOperationsSlide() {
  return (
    <Slide id="aandi-operations" number="04">
      <SectionLabel number="04">A&I.COM · PERFORMANCE & OPERATIONS</SectionLabel>
      <div className="project-layout operations-layout">
        <div className="project-copy">
          <div>
            <h2>
              느린 조회와 긴 검증 시간을
              <br />실제 수치로 줄였습니다.
            </h2>
            <p className="lead">과제 목록 조회, CI 검증, 장애 확인에 드는 시간을 줄일 필요가 있었습니다.</p>
          </div>
          <ActionList
            items={[
              "과제마다 다시 조회하던 데이터를 한 번에 가져오도록 배치 조회로 바꿨습니다.",
              "자동화 테스트를 보강하고 CI의 중복 검증 단계를 정리했습니다.",
              "서비스 오류 로그 형식을 맞추고 CloudWatch 조회와 알림을 한곳에서 확인하게 했습니다.",
            ]}
          />
        </div>
        <OperationsEvidence />
      </div>
      <MetricRail
        metrics={[
          { value: "60 → 2회", label: "DB 조회" },
          { value: "22.1%", label: "CI 단축" },
          { value: "141개", label: "API 라우트" },
          { value: "105개", label: "접근 경로 검증" },
        ]}
      />
    </Slide>
  );
}

function GojjibomSlide() {
  return (
    <Slide id="gojjibom" number="05">
      <SectionLabel number="05">고찌봄 · PM & DEV LEAD · 2026.06–07 · 4일</SectionLabel>
      <div className="project-layout media-layout">
        <div className="project-copy">
          <div>
            <h2>
              4일 안에 복약 확인을
              <br />안부 확인으로 연결했습니다.
            </h2>
            <p className="lead">
              제주 어르신의 복약 여부를 보호자가 확인할 수 있게 만든 서비스입니다.
            </p>
          </div>
          <Problem>어르신이 약을 먹었는지 보호자가 쉽게 확인할 방법이 필요했습니다.</Problem>
          <ActionList
            items={[
              "PM·개발 리드로 문제를 정리하고 4일 안에 만들 MVP 범위를 정했습니다.",
              "FE/BE 계약과 구현 순서를 맞추며 개발을 이끌었습니다.",
              "알림을 누르면 앱을 찾아 들어가지 않고 바로 복약 화면이 열리게 했습니다.",
            ]}
          />
          <Stack>Problem Definition · MVP · FE/BE · Notification UX</Stack>
          <div className="link-row">
            <Link href={LINKS.gojjibom}>Live Demo</Link>
            <Link href={LINKS.gojjibomBackend}>Backend Repo</Link>
            <Link href={LINKS.gojjibomDemo}>원본 알림 시연</Link>
          </div>
        </div>
        <figure className="primary-figure gojjibom-figure">
          <img src={gojjibomOneTouch} alt="고찌봄 알림에서 복약 화면으로 이어지는 원터치 UX" />
          <figcaption>알림을 누르면 복약 화면이 바로 열리는 원터치 흐름 · 실제 화면</figcaption>
        </figure>
      </div>
      <MetricRail
        metrics={[
          { value: "4일", label: "MVP 완성" },
          { value: "1위", label: "2026 AI Re-Local" },
          { value: "팀 MVP", label: "팀 내 선정" },
        ]}
      />
    </Slide>
  );
}

function DidimlogEvidence() {
  return (
    <div className="technical-note didim-note">
      <p className="note-label">account proof → bounded collection → recovery</p>
      <div className="didim-flow">
        <div className="flow-node">
          <span>01</span>
          <strong>BOJ 프로필 코드</strong>
          <p>5분 유효 · 소유권 확인</p>
        </div>
        <FlowArrow />
        <div className="flow-node">
          <span>02</span>
          <strong>문제 상세 수집</strong>
          <p>최대 K=4 동시성 제한</p>
        </div>
        <FlowArrow />
        <div className="flow-node">
          <span>03</span>
          <strong>Redis checkpoint</strong>
          <p>실패·미처리 ID만 재시도</p>
        </div>
      </div>
      <div className="didim-proof">
        <div>
          <span>SEQUENTIAL MEDIAN</span>
          <strong>55.632초</strong>
        </div>
        <FlowArrow />
        <div>
          <span>K=4 MEDIAN</span>
          <strong>12.226초</strong>
        </div>
        <em>77.96% 단축</em>
      </div>
      <p className="evidence-footnote">
        3,400건 · 요청당 10ms 고정 지연 fixture · 3회 중앙값. 실제 BOJ 응답 시간이 아니며 운영 기본값은
        병렬 비활성화(K=1)입니다.
      </p>
      <a className="poster-link" href={LINKS.didimlogSignup} rel="noreferrer" target="_blank">
        <img src={didimlogSignupPoster} alt="디딤로그 BOJ 계정 인증 시연 정적 프레임" />
        <span>BOJ 계정 인증 실제 화면 · 원본 GIF 열기 ↗</span>
      </a>
    </div>
  );
}

function DidimlogSlide() {
  return (
    <Slide id="didimlog" number="06">
      <SectionLabel number="06">디딤로그 · MAINTAINER · 2026.02–04</SectionLabel>
      <div className="project-layout didim-layout">
        <div className="project-copy">
          <div>
            <h2>
              BOJ 계정 인증부터 문제 수집까지
              <br />끊기지 않게 만들었습니다.
            </h2>
            <p className="lead">
              BOJ 프로필과 문제 기록을 바탕으로 다음 문제를 추천하고 회고를 남기는 알고리즘 학습
              서비스입니다.
            </p>
          </div>
          <Problem>BOJ 아이디의 실제 주인을 확인하면서, 문제 데이터도 빠짐없이 모아야 했습니다.</Problem>
          <ActionList
            items={[
              "프로필에 5분짜리 인증 코드를 올리게 해 BOJ ID 소유권을 확인하고 가입 뒤 티어를 동기화했습니다.",
              "문제 상세 요청을 최대 K=4 동시성으로 제한해 수집했습니다.",
              "실패한 ID와 checkpoint를 Redis에 남겨 실패·미처리 문제만 다시 수집했습니다.",
            ]}
          />
          <Stack>Kotlin · Spring Boot · BOJ · MongoDB · Redis</Stack>
          <div className="link-row">
            <Link href={LINKS.didimlog}>Backend Repo</Link>
            <Link href={LINKS.didimlogCrawler}>원본 수집 시연</Link>
          </div>
        </div>
        <DidimlogEvidence />
      </div>
      <MetricRail
        metrics={[
          { value: "3,400건", label: "fixture benchmark" },
          { value: "0건", label: "누락" },
          { value: "0건", label: "중복" },
          { value: "0건", label: "불완전 데이터" },
        ]}
      />
    </Slide>
  );
}

function InvestopiaEvidence() {
  return (
    <div className="technical-note investopia-note">
      <p className="note-label">one transaction flow / two interfaces</p>
      <div className="market-source">
        <strong>네이버 금융 HTML</strong>
        <span>Requests · BeautifulSoup · 30초</span>
      </div>
      <FlowArrow />
      <div className="trade-core">
        <span>MariaDB</span>
        <strong>Flask REST API</strong>
        <p>잔액 · 보유 수량 검증 / 평균 매입가 계산 / 자산 데이터</p>
      </div>
      <div className="branch-lines" aria-hidden="true">
        <svg viewBox="0 0 720 88">
          <path d="M360 2 C360 35 190 28 190 83" />
          <path d="M360 2 C360 35 530 28 530 83" />
          <path d="M182 71 L190 84 L198 71" />
          <path d="M522 71 L530 84 L538 71" />
        </svg>
      </div>
      <div className="interface-branches">
        <div>
          <span>WEB</span>
          <strong>가상 매수·매도</strong>
          <p>자산 배분 차트</p>
        </div>
        <div>
          <span>RASPBERRY PI</span>
          <strong>버튼 주문</strong>
          <p>LCD 자산 정보</p>
        </div>
      </div>
      <p className="evidence-footnote">두 화면이 같은 거래 API와 자산 데이터를 사용합니다.</p>
    </div>
  );
}

function InvestopiaSlide() {
  return (
    <Slide id="investopia" number="07">
      <SectionLabel number="07">INVESTOPIA · PL & BACKEND LEAD · 2025.04–06</SectionLabel>
      <div className="project-layout investopia-layout">
        <div className="project-copy">
          <div>
            <h2>
              웹과 Raspberry Pi가
              <br />같은 거래 흐름을 쓰게 만들었습니다.
            </h2>
            <p className="lead">
              처음 주식을 접하는 사용자가 가상 매수·매도를 연습할 수 있는 모의 투자 서비스입니다.
            </p>
          </div>
          <Problem>가상 거래와 자산 현황을 웹 화면과 Raspberry Pi에서 같은 기준으로 처리해야 했습니다.</Problem>
          <ActionList
            items={[
              "잔액과 보유 수량을 검증하고 평균 매입가를 계산하는 매수·매도 API를 만들었습니다.",
              "네이버 금융 HTML에서 주가를 30초마다 수집하고 자산 배분 차트에 반영했습니다.",
              "Raspberry Pi 회로의 버튼과 LCD를 거래 API·자산 데이터에 연결했습니다.",
            ]}
          />
          <Stack>Flask · MariaDB · Naver Finance · Chart.js · Raspberry Pi</Stack>
          <div className="link-row">
            <Link href={LINKS.investopia}>Investopia Repo</Link>
            <Link href={LINKS.investopiaDemo}>원본 매수 시연</Link>
          </div>
        </div>
        <InvestopiaEvidence />
      </div>
      <MetricRail
        metrics={[
          { value: "1개 흐름", label: "웹·Raspberry Pi 주문" },
          { value: "30초", label: "주가 수집 주기" },
          { value: "평균 매입가", label: "가상 매수·매도 계산" },
        ]}
      />
    </Slide>
  );
}

function SoloPlayEvidence() {
  return (
    <div className="technical-note soloplay-note">
      <p className="note-label">save first / enrich separately</p>
      <div className="solo-main-flow">
        <div className="flow-node">
          <span>01</span>
          <strong>Kakao Local API</strong>
          <p>장소 수집 · 최대 15개</p>
        </div>
        <FlowArrow />
        <div className="flow-node">
          <span>02</span>
          <strong>ID 정규화·중복 방지</strong>
          <p>Kakao 장소 ID 기준</p>
        </div>
        <FlowArrow />
        <div className="flow-node primary-node">
          <span>03</span>
          <strong>MongoDB 먼저 저장</strong>
          <p>원본 장소 정보 보존</p>
        </div>
      </div>
      <div className="solo-branch">
        <svg aria-hidden="true" viewBox="0 0 90 160">
          <path d="M45 2 C45 54 44 82 44 150" />
          <path d="M36 138 L44 152 L53 138" />
        </svg>
        <div>
          <span>별도 Coroutine · Gemini</span>
          <strong>소개와 해시태그 보강</strong>
          <p>성공: displayTitle · displayTags 갱신</p>
          <p>실패: 원본 장소 정보 유지</p>
        </div>
      </div>
      <p className="evidence-footnote">
        프롬프트 요청값: 소개 15자 내외 · 해시태그 3–5개. 응답 길이를 보장하는 지표는 아닙니다.
      </p>
    </div>
  );
}

function SoloPlaySlide() {
  return (
    <Slide id="soloplay" number="08">
      <SectionLabel number="08">SOLOPLAY · BACKEND LEAD · 2024.10–2025.02</SectionLabel>
      <div className="project-layout solo-layout">
        <div className="project-copy">
          <div>
            <h2>
              장소는 먼저 저장하고,
              <br />AI 보강은 따로 처리했습니다.
            </h2>
            <p className="lead">혼자 시간을 보낼 장소를 찾고 기록하는 서비스입니다.</p>
          </div>
          <Problem>Gemini 호출이 실패해도 Kakao에서 모은 장소는 잃지 않아야 했습니다.</Problem>
          <ActionList
            items={[
              "Kakao 장소 ID를 기준으로 반복 수집을 막았습니다.",
              "신규 장소를 MongoDB에 먼저 저장한 뒤 별도 Coroutine에서 소개와 해시태그를 만들었습니다.",
              "Gemini 호출이나 응답 파싱이 실패하면 원본 장소 정보를 그대로 보여주게 했습니다.",
            ]}
          />
          <Stack>
            Kotlin · Spring WebFlux · MongoDB ·<br /> Kakao Local API · Gemini API
          </Stack>
          <div className="link-row">
            <Link href={LINKS.soloplay}>Backend Repo</Link>
          </div>
        </div>
        <SoloPlayEvidence />
      </div>
      <MetricRail
        metrics={[
          { value: "분리", label: "장소 저장과 Gemini 호출" },
          { value: "원본 유지", label: "AI 호출·파싱 실패 시" },
          { value: "ID 기준", label: "반복 수집 방지" },
        ]}
      />
    </Slide>
  );
}

function GrowthSlide() {
  const records = [
    {
      detail: "참여자 40명 이상 · 테크 세션 30회 이상 · 네트워킹 5회 이상",
      title: "A&I 운영자 · 2024.01–현재",
    },
    {
      detail: "기술 글 164편 · 누적 조회 6,500회 이상 · 테스트와 커버리지 개선 과정 기록",
      title: "Velog · 2024.08–현재",
    },
    {
      detail: "Java 스타일 가이드와 리뷰 기준을 맞추고, 동료 피드백과 역할 교대를 경험했습니다.",
      title: "우아한테크코스 8기 프리코스 · 2025.09–11",
    },
    {
      detail: "인덕대학교 학사학위 전공심화과정 재학 · 4.4/4.5 · 성적우수장학금 5회 · SQLD · 네트워크관리사 2급",
      title: "학업과 자격",
    },
  ];

  return (
    <Slide id="growth" number="09">
      <SectionLabel number="09">FOUNDATION & GROWTH</SectionLabel>
      <div className="growth-layout">
        <div className="growth-copy">
          <h2>
            운영하면서 배운 내용은
            <br />기록하고 나눴습니다.
          </h2>
          <p className="lead">
            프로젝트 밖에서도 운영, 글쓰기, 리뷰, 학업을 같은 방식으로 이어 왔습니다.
          </p>
          <EvidenceArrow label="운영 → 기록 → 공유" />
          <div className="link-row">
            <Link href={LINKS.github}>GitHub</Link>
            <Link href={LINKS.velog}>Velog</Link>
          </div>
        </div>
        <ol className="growth-ledger">
          {records.map((record, index) => (
            <li key={record.title}>
              <span>0{index + 1}</span>
              <div>
                <strong>{record.title}</strong>
                <p>{record.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </Slide>
  );
}

function ClosingSlide() {
  return (
    <Slide id="closing" number="10">
      <div className="closing-layout">
        <p className="eyebrow">CONTACT</p>
        <h2>
          문제를 고친 뒤에는,
          <br />
          실제로 달라졌는지
          <br />
          <em>다시 확인합니다.</em>
        </h2>
        <div className="closing-rule" />
        <p className="lead">
          성능, 테스트, 배포 시간과 운영 기록을 근거로 안정적인 서버를 만들어 왔습니다.
        </p>
        <p className="closing-thanks">읽어주셔서 감사합니다.</p>
        <div className="link-row">
          <Link href={LINKS.github}>GitHub</Link>
          <Link href={LINKS.velog}>Velog</Link>
          <Link href={LINKS.aandi}>A&I Site</Link>
        </div>
      </div>
    </Slide>
  );
}

export default function App() {
  return (
    <main className="deck">
      <CoverSlide />
      <ProfileSlide />
      <AandiArchitectureSlide />
      <AandiOperationsSlide />
      <GojjibomSlide />
      <DidimlogSlide />
      <InvestopiaSlide />
      <SoloPlaySlide />
      <GrowthSlide />
      <ClosingSlide />
    </main>
  );
}
