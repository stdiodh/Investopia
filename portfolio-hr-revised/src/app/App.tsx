import type { ReactNode } from "react";

import aandiArchitecture from "../assets/aandi-architecture.png";
import aandiLive from "../assets/hr/evidence-v2/aandi-assignment-list-content.png";
import aandiP95Record from "../assets/hr/evidence-v2/aandi-p95-record.png";
import aandiRepositoryRecord from "../assets/hr/evidence-v2/aandi-repository-call-record-clean.png";
import didimlogBoj from "../assets/hr/didimlog-boj.png";
import soloPlayHome from "../assets/hr/evidence-v2/home-recommendations.png";
import gojjibomFlow from "../assets/hr/gojjibom-one-touch.png";
import investopiaHardware from "../assets/hr/investopia-hardware.png";

const MEDIA = {
  aandiLive,
  didimlog: didimlogBoj,
  gojjibom: gojjibomFlow,
  investopiaHardware,
} as const;

const LINKS = {
  aandi: "https://aandiclub.com/",
  aandiGateway: "https://github.com/Team-AnI/A-AND-I-GATEWAY-SERVER",
  aandiPerformance: "https://github.com/Team-AnI/A-AND-I-WEB-SERVER/blob/main/docs/performance/results/2026-07-09-assignment-list-before-after.md",
  aandiRepositoryEvidence: "https://github.com/Team-AnI/A-AND-I-WEB-SERVER/blob/main/performance/results/assignment-read-query-evidence.json",
  aandiWeb: "https://github.com/Team-AnI/A-AND-I-WEB-SERVER",
  didimlog: "https://github.com/didim-log/didim-log-BE",
  didimlogDemo: "https://didim-log-fe.web.app/",
  github: "https://github.com/stdiodh",
  gojjibom: "https://gojjibom.web.app/",
  gojjibomBackend: "https://github.com/TIKI-TAKA-hackathon/Tiki-Taka-BE",
  gojjibomNews: "https://news.unn.net/news/articleView.html?idxno=594458",
  gojjibomResult: "https://www.jdnc.or.kr/notice/news.htm?act=view&seq=1019",
  investopia: "https://github.com/stdiodh/Investopia",
  soloplayDesign: "https://www.figma.com/design/rWBAUinnBcfdhEXF2blgWC/%EC%86%94%ED%94%8C-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8?node-id=66-2",
  soloplay: "https://github.com/SangWook16074/Solo-Play-Web-Server",
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
        <span>허동현 · Backend Portfolio 2026</span>
        <span>{number} / 9</span>
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

function Status({ tone = "blue", children }: { tone?: "blue" | "gray" | "green"; children: ReactNode }) {
  return <span className={`status status-${tone}`}>{children}</span>;
}

function Problem({ children }: { children: ReactNode }) {
  return (
    <div className="problem">
      <span>문제</span>
      <p>{children}</p>
    </div>
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
        <div className="cover-copy">
          <p className="eyebrow">SERVER DEVELOPER PORTFOLIO · 허동현</p>
          <h1>
            어떤 문제를 봤고,
            <br />왜 그렇게 고쳤는지
            <br />5개 프로젝트로 정리했습니다.
          </h1>
          <p className="lead cover-lead">
            문제를 발견한 배경, 내가 내린 판단, 확인한 결과를 프로젝트별로 담았습니다.
          </p>
        </div>
        <div className="cover-index" aria-label="포트폴리오 프로젝트">
          <span>01 A&amp;I.com</span>
          <span>02 고찌봄</span>
          <span>03 디딤로그</span>
          <span>04 Investopia</span>
          <span>05 SoloPlay</span>
        </div>
        <div className="cover-count">
          <strong>5</strong>
          <div>
            <span>PROJECTS</span>
            <p>운영 · 공개 데모 · 로컬 프로토타입 · 저장소</p>
          </div>
        </div>
      </div>
    </Slide>
  );
}

const projects = [
  {
    name: "A&I.com",
    period: "BE Lead · 2025.01–현재",
    result: "변경과 배포가 함께 묶인 기능을 서비스 경계로 분리",
    status: <Status tone="green">운영 서비스</Status>,
  },
  {
    name: "고찌봄",
    period: "PM · Dev Lead · 2026.06–07",
    result: "알림부터 복약 확인까지 이어지는 MVP 범위 결정",
    status: <Status>공개 fixture 데모</Status>,
  },
  {
    name: "디딤로그",
    period: "Maintainer · 2026.02–04",
    result: "BOJ 본인 확인과 중단 뒤 다시 잇는 문제 수집 흐름",
    status: <Status>공개 프론트 데모</Status>,
  },
  {
    name: "Investopia",
    period: "PL · BE Lead · 2025.04–06",
    result: "웹과 Raspberry Pi가 같은 거래 API를 사용",
    status: <Status tone="gray">로컬 · 하드웨어 프로토타입</Status>,
  },
  {
    name: "SoloPlay",
    period: "BE Lead · 2024.10–2025.02",
    result: "AI 호출이 실패해도 원본 장소를 남기는 저장 순서",
    status: <Status tone="gray">백엔드 프로젝트 · 저장소 공개</Status>,
  },
];

function ProjectMapSlide() {
  return (
    <Slide id="project-map" number="02">
      <SectionLabel number="02">PROJECT MAP · 무엇을 보면 되는지</SectionLabel>
      <div className="map-header">
        <div>
          <h2>프로젝트마다 한 가지 판단만 먼저 보이게 했습니다.</h2>
          <p className="lead">상세한 기술 이력은 이력서에 두고, 여기에는 문제와 선택의 결과를 남겼습니다.</p>
        </div>
        <p className="map-guide">문제 → 내 판단 → 확인 결과 → 직접 볼 수 있는 근거</p>
      </div>
      <ol className="project-map" aria-label="프로젝트 구성">
        {projects.map((project, index) => (
          <li key={project.name}>
            <span className="map-index">0{index + 1}</span>
            <div className="map-name">
              <strong>{project.name}</strong>
              <p>{project.period}</p>
            </div>
            <p className="map-result">{project.result}</p>
            {project.status}
          </li>
        ))}
      </ol>
    </Slide>
  );
}

function AandiArchitectureSlide() {
  return (
    <Slide id="aandi-architecture" number="03">
      <SectionLabel number="03">A&amp;I.COM · BACKEND LEAD · 2025.01–현재</SectionLabel>
      <div className="architecture-layout">
        <div className="project-copy compact-copy">
          <div>
            <Status tone="green">운영 서비스</Status>
            <h2>변경 범위를 나누기 위해 서비스를 먼저 나눴습니다.</h2>
            <p className="lead">
              교육 커뮤니티를 운영하며 Auth, Web, Gateway, Tech Blog, Online Judge를 독립된 서버로
              관리했습니다.
            </p>
          </div>
          <Problem>기능이 한 서버에 모여 있어 작은 변경도 전체 배포에 영향을 줬습니다.</Problem>
          <div className="judgment-block">
            <span>내 판단</span>
            <strong>도메인과 배포 주기가 다른 기능부터 서비스 경계로 삼았습니다.</strong>
          </div>
          <ActionList
            items={[
              "서버별 저장소와 Gateway 경로를 나눴습니다.",
              "SNS/SQS로 서비스 사이 이벤트 전달을 분리했습니다.",
              "GitHub Actions, ECR, EC2로 서비스별 배포 흐름을 만들었습니다.",
            ]}
          />
          <div className="link-row">
            <Link href={LINKS.aandi}>운영 화면</Link>
            <Link href={LINKS.aandiGateway}>Gateway 저장소</Link>
          </div>
        </div>
        <div className="architecture-evidence">
          <figure className="primary-figure architecture-figure">
            <img src={aandiArchitecture} alt="A&I.com 시스템 아키텍처" />
            <figcaption>직접 작성한 운영 아키텍처 · 서비스 분리와 배포 흐름</figcaption>
          </figure>
          <div className="architecture-proof">
            <figure className="architecture-live">
              <img src={MEDIA.aandiLive} alt="A&I.com 과제 목록 시연 영상 프레임" />
              <figcaption>과제 목록 시연 영상 프레임 · 2026.06</figcaption>
            </figure>
            <div className="architecture-fact">
              <span>OPERATING PROOF</span>
              <strong>5개 독립 서버 저장소</strong>
              <p>서비스별 변경 · 배포 범위 분리</p>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}

function StarRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="star-row">
      <span>{label}</span>
      <p>{children}</p>
    </div>
  );
}

function AandiQuerySlide() {
  return (
    <Slide id="aandi-query" number="04">
      <SectionLabel number="04">A&amp;I.COM · ONE CASE · 조회 구조 개선</SectionLabel>
      <div className="case-header">
        <div>
          <h2>과제마다 반복하던 조회를 한 번에 가져오도록 바꿨습니다.</h2>
          <p className="lead">기능을 더하지 않고, 같은 응답을 만드는 조회 순서만 고쳤습니다.</p>
        </div>
        <Link href={LINKS.aandiWeb}>근거 저장소</Link>
      </div>
      <div className="query-layout">
        <div className="star-card">
          <StarRow label="S · 상황">과제 목록을 만들 때 과제마다 필요한 데이터를 다시 조회했습니다.</StarRow>
          <StarRow label="T · 목표">API 응답 형식은 그대로 두고 반복 조회만 줄여야 했습니다.</StarRow>
          <StarRow label="A · 실행">필요한 데이터를 batch로 먼저 읽고 과제별로 묶도록 조회 순서를 재구성했습니다.</StarRow>
        </div>
        <div className="query-evidence">
          <p className="query-result-label">R · 확인 결과</p>
          <figure className="query-record query-call-record">
            <img src={aandiRepositoryRecord} alt="A&I 기존 구조에서 60회로 예상한 child repository 조회를 회귀 테스트에서 2회로 검증한 JSON 기록" />
            <figcaption>
              <span><strong>구조 검증</strong> 기존 구조 예상 60회 → 회귀 테스트 검증 2회 · MongoDB command 수가 아닌 service-level 기준</span>
              <Link href={LINKS.aandiRepositoryEvidence}>원문</Link>
            </figcaption>
          </figure>
          <figure className="query-record query-p95-record">
            <img src={aandiP95Record} alt="A&I 과제 목록 P95 응답 시간 9.297ms에서 7.565ms로 측정한 저장소 기록" />
            <figcaption>
              <span><strong>성능 측정</strong> 과제 30개 · 100 RPS · 2분 · 총 3세트 · 로컬 고정부하</span>
              <Link href={LINKS.aandiPerformance}>원문</Link>
            </figcaption>
          </figure>
        </div>
      </div>
    </Slide>
  );
}

function GojjibomSlide() {
  return (
    <Slide id="gojjibom" number="05">
      <SectionLabel number="05">고찌봄 · PM &amp; DEV LEAD · 2026.06–07</SectionLabel>
      <div className="project-layout media-layout">
        <div className="project-copy">
          <div>
            <Status>공개 fixture 데모 · 샘플 데이터</Status>
            <h2>짧은 기간이라 기능을 늘리지 않고 확인 흐름 하나만 남겼습니다.</h2>
            <p className="lead">어르신의 복약 여부를 보호자가 바로 확인하는 서비스입니다.</p>
          </div>
          <Problem>짧은 개발 기간 안에 어르신과 보호자가 함께 쓸 수 있는 결과가 필요했습니다.</Problem>
          <div className="decision-steps" aria-label="4일 MVP 판단">
            <div><span>01</span><strong>대상</strong><p>복약 확인으로 문제를 좁힘</p></div>
            <div><span>02</span><strong>범위</strong><p>알림과 확인 화면만 우선 구현</p></div>
            <div><span>03</span><strong>연결</strong><p>알림을 누르면 해당 화면을 바로 열기</p></div>
          </div>
          <p className="project-result"><span>결과</span><strong>4일 MVP 완성</strong><em>최고점 · 혁신상</em></p>
          <div className="link-row">
            <Link href={LINKS.gojjibom}>공개 데모</Link>
            <Link href={LINKS.gojjibomBackend}>백엔드 저장소</Link>
          </div>
        </div>
        <div className="gojjibom-evidence">
          <figure className="primary-figure media-figure">
            <img src={MEDIA.gojjibom} alt="고찌봄 알림에서 복약 화면으로 이어지는 실제 흐름" />
            <figcaption>알림에서 복약 화면으로 바로 이동하는 흐름 · 공개 데모는 샘플 데이터 사용</figcaption>
          </figure>
          <div className="external-proof" aria-label="고찌봄 외부 검증 자료">
            <div>
              <span>언론 보도 · 2026.07.08</span>
              <strong>고찌봄을 해커톤 주요 개발 성과로 소개</strong>
              <Link href={LINKS.gojjibomNews}>한국대학신문 기사</Link>
            </div>
            <div>
              <span>주관기관 결과</span>
              <strong>티키타카 팀 고찌봄 · 최고점 · 혁신상</strong>
              <Link href={LINKS.gojjibomResult}>결과 확인</Link>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}

function DidimlogSlide() {
  return (
    <Slide id="didimlog" number="06">
      <SectionLabel number="06">디딤로그 · MAINTAINER · 2026.02–04</SectionLabel>
      <div className="project-layout didim-layout">
        <div className="project-copy compact-copy">
          <div>
            <Status>공개 프론트 데모 · 입력 미저장</Status>
            <h2>가입이 막히지 않고, 수집이 끊겨도 다시 이어가게 했습니다.</h2>
            <p className="lead">BOJ 기록을 불러와 다음 문제를 추천하고 회고를 남기는 학습 서비스입니다.</p>
          </div>
          <Problem>BOJ 아이디의 실제 사용자 확인과 많은 문제의 안정적인 수집이 함께 필요했습니다.</Problem>
          <div className="judgment-block">
            <span>내 판단</span>
            <strong>본인 확인은 짧게, 수집은 제한하고, 실패한 지점은 남겨야 했습니다.</strong>
          </div>
          <ActionList
            items={[
              "BOJ 프로필의 5분 인증 코드로 아이디 소유권을 확인했습니다.",
              "문제 요청의 동시성을 제한하고 수집 상태를 Redis에 기록했습니다.",
              "실패하거나 처리하지 못한 문제만 다시 수집하게 했습니다.",
            ]}
          />
          <div className="link-row">
            <Link href={LINKS.didimlogDemo}>공개 프론트 데모</Link>
            <Link href={LINKS.didimlog}>백엔드 저장소</Link>
          </div>
        </div>
        <div className="didim-evidence">
          <figure className="primary-figure didim-figure">
            <img src={MEDIA.didimlog} alt="디딤로그 BOJ 계정 인증 실제 화면" />
            <figcaption>BOJ 프로필 코드를 이용한 계정 인증 · 실제 시연의 정적 프레임</figcaption>
          </figure>
          <div className="benchmark-card">
            <p className="note-label">FIXTURE BENCHMARK</p>
            <div className="benchmark-values">
              <span>55.632초</span>
              <FlowArrow />
              <strong>12.226초</strong>
            </div>
            <p className="benchmark-result">77.96% 단축</p>
            <small>3,400건 fixture · 3회 측정 중앙값 · 운영 기본 동시성 K=1</small>
          </div>
        </div>
      </div>
    </Slide>
  );
}

function InvestopiaVisual() {
  return (
    <div className="investopia-composite">
      <figure className="hardware-figure">
        <img src={MEDIA.investopiaHardware} alt="Investopia Raspberry Pi 회로와 LCD 실제 모습" />
        <figcaption>직접 연결한 Raspberry Pi 회로 · 버튼 주문과 LCD 자산 정보</figcaption>
      </figure>
      <div className="trade-strip" aria-label="웹과 Raspberry Pi의 공통 거래 API 흐름">
        <div><span>WEB</span><strong>차트 · 주문</strong></div>
        <div><span>RASPBERRY PI</span><strong>버튼 · LCD</strong></div>
        <FlowArrow />
        <div className="trade-strip-core"><span>공통</span><strong>거래 API</strong><p>잔액 · 보유 수량 · 평균 매입가</p></div>
      </div>
    </div>
  );
}

function InvestopiaSlide() {
  return (
    <Slide id="investopia" number="07">
      <SectionLabel number="07">INVESTOPIA · PL &amp; BACKEND LEAD · 2025.04–06</SectionLabel>
      <div className="project-layout investopia-layout">
        <div className="project-copy compact-copy">
          <div>
            <Status tone="gray">로컬 · 하드웨어 프로토타입</Status>
            <h2>화면이 달라도 거래 기준은 하나로 맞췄습니다.</h2>
            <p className="lead">처음 주식을 접하는 사용자를 위한 가상 매수·매도 서비스입니다.</p>
          </div>
          <Problem>웹과 Raspberry Pi의 주문 결과가 서로 다른 기준으로 처리되면 안 됐습니다.</Problem>
          <div className="judgment-block">
            <span>내 판단</span>
            <strong>입력 장치는 나누되 잔액, 수량, 평균 매입가 검증은 같은 거래 API에 모았습니다.</strong>
          </div>
          <ActionList
            items={[
              "매수·매도 전 잔액과 보유 수량을 검증했습니다.",
              "네이버 금융 주가를 30초마다 수집해 차트와 거래에 함께 사용했습니다.",
              "Raspberry Pi 버튼과 LCD를 같은 거래·자산 API에 연결했습니다.",
            ]}
          />
          <p className="project-result compact-result"><span>확인</span><strong>웹 · Pi 공통 거래 흐름</strong><em>주가 수집 주기 30초</em></p>
          <div className="link-row"><Link href={LINKS.investopia}>저장소</Link></div>
        </div>
        <div className="investopia-evidence">
          <InvestopiaVisual />
          <p className="visual-caption">두 인터페이스가 같은 거래 API와 자산 데이터를 사용합니다.</p>
        </div>
      </div>
    </Slide>
  );
}

function SoloPlaySlide() {
  return (
    <Slide id="soloplay" number="08">
      <SectionLabel number="08">SOLOPLAY · BACKEND LEAD · 2024.10–2025.02</SectionLabel>
      <div className="solo-layout">
        <div className="project-copy solo-copy">
          <div>
            <Status tone="gray">백엔드 프로젝트 · 저장소 공개</Status>
            <h2>AI 응답을 기다리다 장소 저장까지 놓치지 않게 했습니다.</h2>
            <p className="lead">혼자 시간을 보낼 장소를 찾고 기록하는 서비스입니다.</p>
          </div>
          <Problem>Gemini 호출이나 응답 파싱이 실패해도 Kakao에서 찾은 장소는 남아야 했습니다.</Problem>
          <div className="judgment-block">
            <span>내 판단</span>
            <strong>필수 데이터 저장과 선택적인 AI 보강의 성공 조건을 분리했습니다.</strong>
          </div>
          <div className="link-row">
            <Link href={LINKS.soloplay}>백엔드 저장소</Link>
            <Link href={LINKS.soloplayDesign}>화면 시안</Link>
          </div>
        </div>
        <div className="solo-evidence">
          <figure className="solo-screen">
            <img src={soloPlayHome} alt="SoloPlay 맞춤 장소와 해시태그 추천 화면 시안" />
            <figcaption>서비스 UI 시안 · 사용자가 확인하는 장소 추천과 태그</figcaption>
          </figure>
          <div className="solo-proof" aria-label="SoloPlay 코드와 테스트로 확인한 데이터 흐름">
            <p className="note-label">CODE-BACKED FLOW</p>
            <h3>장소는 먼저 저장하고, AI는 나중에 보강했습니다.</h3>
            <div className="solo-state-flow">
              <div>
                <span>01</span>
                <strong>Kakao 원본 저장</strong>
                <p>장소명 · 주소 · 카테고리</p>
              </div>
              <FlowArrow />
              <div>
                <span>02</span>
                <strong>Gemini 보강</strong>
                <p>소개 · 해시태그 갱신</p>
              </div>
            </div>
            <div className="solo-fallback">
              <span>실패 시</span>
              <strong>기존 저장본 유지</strong>
              <p>Gemini 호출 · 응답 파싱 실패 기준</p>
            </div>
            <div className="solo-test-result">
              <span>TEST</span>
              <strong>관련 테스트 19개 · 실패 0</strong>
              <p>PlaceService 13 · Enrichment 6</p>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}

const evidenceLinks = [
  { name: "A&I.com", status: <Status tone="green">운영 서비스</Status>, links: [["서비스", LINKS.aandi], ["성능 기록", LINKS.aandiPerformance]] },
  { name: "고찌봄", status: <Status>공개 fixture 데모</Status>, links: [["데모", LINKS.gojjibom], ["기사", LINKS.gojjibomNews], ["결과", LINKS.gojjibomResult]] },
  { name: "디딤로그", status: <Status>공개 프론트 데모</Status>, links: [["데모", LINKS.didimlogDemo], ["Backend", LINKS.didimlog]] },
  { name: "Investopia", status: <Status tone="gray">로컬 프로토타입</Status>, links: [["저장소", LINKS.investopia]] },
  { name: "SoloPlay", status: <Status tone="gray">백엔드 프로젝트</Status>, links: [["저장소", LINKS.soloplay], ["화면 시안", LINKS.soloplayDesign]] },
] as const;

function EvidenceSlide() {
  return (
    <Slide id="evidence" number="09">
      <SectionLabel number="09">EVIDENCE &amp; CONTACT</SectionLabel>
      <div className="evidence-header">
        <div>
          <h2>직접 확인할 수 있는 경로만 모았습니다.</h2>
          <p className="lead">배포되지 않은 프로젝트는 운영 서비스처럼 보이게 쓰지 않았습니다.</p>
        </div>
        <p className="portfolio-note">이 포트폴리오는 이력서에 담기 어려운 판단, 실제 화면, 근거 링크를 보충합니다.</p>
      </div>
      <ol className="evidence-list">
        {evidenceLinks.map((project, index) => (
          <li key={project.name}>
            <span className="map-index">0{index + 1}</span>
            <strong>{project.name}</strong>
            {project.status}
            <div className="evidence-links">
              {project.links.map(([label, href]) => <Link href={href} key={href}>{label}</Link>)}
            </div>
          </li>
        ))}
      </ol>
      <div className="contact-strip">
        <div>
          <span>허동현 · Server Developer</span>
          <strong>읽어주셔서 감사합니다.</strong>
        </div>
        <div className="link-row">
          <Link href={LINKS.github}>GitHub</Link>
        </div>
      </div>
    </Slide>
  );
}

export default function App() {
  return (
    <main className="deck">
      <CoverSlide />
      <ProjectMapSlide />
      <AandiArchitectureSlide />
      <AandiQuerySlide />
      <GojjibomSlide />
      <DidimlogSlide />
      <InvestopiaSlide />
      <SoloPlaySlide />
      <EvidenceSlide />
    </main>
  );
}
