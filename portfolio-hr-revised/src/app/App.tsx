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
  didimlogPerformance: "https://github.com/didim-log/didim-log-BE/blob/main/DOCS/refactoring/be-refactor/PHASE_6N_CRAWLER_DETAILS_BOUNDED_PARALLEL.md",
  email: "mailto:playlistdh@gmail.com",
  github: "https://github.com/stdiodh",
  gojjibom: "https://gojjibom.web.app/",
  gojjibomBackend: "https://github.com/TIKI-TAKA-hackathon/Tiki-Taka-BE",
  gojjibomNews: "https://news.unn.net/news/articleView.html?idxno=594458",
  gojjibomResult: "https://www.jdnc.or.kr/notice/news.htm?act=view&seq=1019",
  investopia: "https://github.com/stdiodh/Investopia",
  soloplayDesign: "https://www.figma.com/design/rWBAUinnBcfdhEXF2blgWC/%EC%86%94%ED%94%8C-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8?node-id=66-2",
  soloplayEnrichmentTest: "https://github.com/SangWook16074/Solo-Play-Web-Server/blob/develop/src/test/kotlin/com/example/solo_play_web_server/place/service/PlaceEnrichmentServiceSpec.kt",
  soloplayPlaceServiceTest: "https://github.com/SangWook16074/Solo-Play-Web-Server/blob/develop/src/test/kotlin/com/example/solo_play_web_server/place/service/PlaceServiceSpec.kt",
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
        <span>허동현 · Server Developer Portfolio 2026</span>
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
          <p className="eyebrow">서버 개발자 포트폴리오 · 허동현</p>
          <h1>
            어떤 문제를 봤고,
            <br />왜 그렇게 고쳤는지
            <br />5개 프로젝트로 정리했습니다.
          </h1>
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
            <span>프로젝트</span>
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
    period: "Backend Lead · 2025.01–현재",
    result: "변경과 배포가 함께 묶인 기능을 서비스 경계로 분리",
    status: <Status tone="green">운영 서비스</Status>,
  },
  {
    name: "고찌봄",
    period: "PM · Dev Lead · 2026.06–07",
    result: "알림부터 복약 확인까지 이어지는 MVP 범위 결정",
    status: <Status>공개 데모 · 샘플 데이터</Status>,
  },
  {
    name: "디딤로그",
    period: "Maintainer · 2026.02–현재",
    result: "BOJ 본인 확인과 중단 뒤 다시 잇는 문제 수집 흐름",
    status: <Status>공개 데모 · 입력 미저장</Status>,
  },
  {
    name: "Investopia",
    period: "PL · Backend Lead · 2025.04–06",
    result: "웹과 Raspberry Pi에서 같은 잔액·보유 수량 검증",
    status: <Status tone="gray">로컬 · 하드웨어 프로토타입</Status>,
  },
  {
    name: "SoloPlay",
    period: "Backend Lead · 2024.10–2025.02",
    result: "AI 호출이 실패해도 원본 장소를 남기는 저장 순서",
    status: <Status tone="gray">백엔드 프로젝트 · 저장소 공개</Status>,
  },
];

function ProjectMapSlide() {
  return (
    <Slide id="project-map" number="02">
      <SectionLabel number="02">프로젝트</SectionLabel>
      <div className="map-header">
        <div>
          <h2>5개 프로젝트에서 맡은 역할과 핵심 선택</h2>
        </div>
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
            <h2>기능과 배포 주기에 따라 서비스 경계를 나눴습니다.</h2>
          </div>
          <Problem>기능이 한 서버에 모여 있어 작은 변경도 전체 배포에 영향을 줬습니다.</Problem>
          <ActionList
            items={[
              "도메인과 배포 주기가 다른 기능을 기준으로 서버 저장소와 Gateway 경로 분리",
              "SNS/SQS로 서비스 사이 이벤트 전달",
              "GitHub Actions, ECR, EC2 기반 서비스별 배포",
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
            <figcaption>A&amp;I.com 운영 아키텍처</figcaption>
          </figure>
          <div className="architecture-proof">
            <figure className="architecture-live">
              <img src={MEDIA.aandiLive} alt="A&I.com 과제 목록 시연 영상 프레임" />
              <figcaption>과제 목록 시연 영상 프레임 · 2026.06</figcaption>
            </figure>
            <div className="architecture-fact">
              <span>서비스 화면</span>
              <strong>5개 독립 서버 저장소</strong>
              <p>Auth · Web · Gateway · Tech Blog · Online Judge</p>
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
      <SectionLabel number="04">A&amp;I.COM · 조회 구조 개선</SectionLabel>
      <div className="case-header">
        <div>
          <h2>과제별 반복 조회를 배치 조회로 묶었습니다.</h2>
        </div>
        <Link href={LINKS.aandiWeb}>근거 저장소</Link>
      </div>
      <div className="query-layout">
        <div className="star-card">
          <StarRow label="문제">과제 목록을 만들 때마다 과제별 데이터를 다시 조회</StarRow>
          <StarRow label="조건">API 응답 형식 유지</StarRow>
          <StarRow label="선택">서비스 계층의 반복 조회를 배치 조회로 전환</StarRow>
          <StarRow label="적용">필요한 데이터를 먼저 읽은 뒤 과제별로 결합</StarRow>
        </div>
        <div className="query-evidence">
          <p className="query-result-label">확인 결과</p>
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
      <SectionLabel number="05">고찌봄 · PM · Dev Lead · 2026.06–07</SectionLabel>
      <div className="project-layout media-layout">
        <div className="project-copy">
          <div>
            <Status>공개 데모 · 샘플 데이터</Status>
            <h2>복약 확인 흐름 하나에 집중했습니다.</h2>
            <p className="lead">어르신의 복약 여부를 보호자가 바로 확인하는 서비스</p>
          </div>
          <Problem>어르신이 앱을 탐색하지 않아도 알림에서 복약 확인 화면으로 바로 들어가야 했습니다.</Problem>
          <div className="decision-steps" aria-label="4일 MVP 판단">
            <div><span>01</span><strong>대상</strong><p>복약 확인으로 문제를 좁힘</p></div>
            <div><span>02</span><strong>범위</strong><p>알림과 확인 화면만 우선 구현</p></div>
            <div><span>03</span><strong>연결</strong><p>알림을 누르면 해당 화면을 바로 열기</p></div>
          </div>
          <p className="project-result"><span>결과</span><strong>4일 MVP 완성</strong></p>
          <div className="link-row">
            <Link href={LINKS.gojjibom}>공개 데모</Link>
            <Link href={LINKS.gojjibomBackend}>백엔드 저장소</Link>
          </div>
        </div>
        <div className="gojjibom-evidence">
          <figure className="primary-figure media-figure">
            <img src={MEDIA.gojjibom} alt="고찌봄 알림에서 복약 화면으로 이어지는 실제 흐름" />
            <figcaption>알림에서 복약 화면으로 이어지는 공개 데모 화면</figcaption>
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
      <SectionLabel number="06">디딤로그 · MAINTAINER · 2026.02–현재</SectionLabel>
      <div className="project-layout didim-layout">
        <div className="project-copy compact-copy">
          <div>
            <Status>공개 프론트 데모 · 입력 미저장</Status>
            <h2>BOJ 본인 확인과 중단 지점 재수집을 구현했습니다.</h2>
            <p className="lead">BOJ 기록으로 다음 문제를 추천하고 회고를 남기는 학습 서비스</p>
          </div>
          <Problem>임의 BOJ 아이디 가입을 막고, 수집이 끊겨도 처음부터 다시 처리하지 않아야 했습니다.</Problem>
          <ActionList
            items={[
              "BOJ 프로필의 5분 인증 코드로 아이디 소유권 확인",
              "문제 요청의 동시성을 제한하고 수집 상태를 Redis에 기록",
              "실패하거나 처리하지 못한 문제만 재수집",
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
            <figcaption>BOJ 프로필 코드를 이용한 계정 인증 화면</figcaption>
          </figure>
          <div className="benchmark-card">
            <p className="note-label">로컬 고정 샘플</p>
            <div className="benchmark-values">
              <span>55.632초</span>
              <FlowArrow />
              <strong>12.226초</strong>
            </div>
            <p className="benchmark-result">77.96% 단축</p>
            <div className="benchmark-source">
              <small>3,400건 고정 샘플 · 순차/K=4 · 3회 중앙값</small>
              <Link href={LINKS.didimlogPerformance}>측정 기록</Link>
            </div>
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
            <h2>웹과 Raspberry Pi 주문 로직을 한곳에 모았습니다.</h2>
            <p className="lead">처음 주식을 접하는 사용자를 위한 가상 매수·매도</p>
          </div>
          <Problem>웹과 Raspberry Pi가 각각 거래 로직을 가지면 잔액과 보유 수량 검증이 달라질 수 있었습니다.</Problem>
          <ActionList
            items={[
              "매수·매도 전 잔액과 보유 수량 검증",
              "네이버 금융 주가를 30초마다 수집해 차트와 거래에 사용",
              "Raspberry Pi 버튼 주문과 LCD 자산 조회를 서버에 연결",
            ]}
          />
          <p className="project-result compact-result"><span>확인</span><strong>가상 매수·매도와 평균 매입가</strong></p>
          <div className="link-row"><Link href={LINKS.investopia}>저장소</Link></div>
        </div>
        <div className="investopia-evidence">
          <InvestopiaVisual />
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
            <h2>Kakao 원본과 Gemini 보강을 분리했습니다.</h2>
            <p className="lead">혼자 시간을 보낼 장소를 찾고 기록하는 서비스</p>
          </div>
          <Problem>Gemini 호출이나 응답 파싱이 실패해도 Kakao에서 찾은 장소는 남아야 했습니다.</Problem>
          <div className="link-row">
            <Link href={LINKS.soloplay}>백엔드 저장소</Link>
            <Link href={LINKS.soloplayDesign}>화면 시안</Link>
          </div>
        </div>
        <div className="solo-evidence">
          <figure className="solo-screen">
            <img src={soloPlayHome} alt="SoloPlay 맞춤 장소와 해시태그 추천 화면 시안" />
            <figcaption>SoloPlay UI 시안 · 장소 추천과 해시태그</figcaption>
          </figure>
          <div className="solo-proof" aria-label="SoloPlay 코드와 테스트로 확인한 데이터 흐름">
            <p className="note-label">구현 흐름</p>
            <h3>Kakao 원본 저장 → Gemini 보강</h3>
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
              <span>테스트</span>
              <strong>관련 테스트 시나리오 19개</strong>
              <p>
                <Link href={LINKS.soloplayPlaceServiceTest}>PlaceService 13</Link>
                <Link href={LINKS.soloplayEnrichmentTest}>Enrichment 6</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </Slide>
  );
}

const evidenceLinks = [
  { name: "A&I.com", status: <Status tone="green">운영 서비스</Status>, links: [["서비스", LINKS.aandi], ["Web 저장소", LINKS.aandiWeb], ["성능 기록", LINKS.aandiPerformance]] },
  { name: "고찌봄", status: <Status>공개 데모 · 샘플 데이터</Status>, links: [["데모", LINKS.gojjibom], ["백엔드 저장소", LINKS.gojjibomBackend], ["기사", LINKS.gojjibomNews], ["결과", LINKS.gojjibomResult]] },
  { name: "디딤로그", status: <Status>공개 데모 · 입력 미저장</Status>, links: [["데모", LINKS.didimlogDemo], ["백엔드 저장소", LINKS.didimlog], ["측정 기록", LINKS.didimlogPerformance]] },
  { name: "Investopia", status: <Status tone="gray">로컬 · 하드웨어 프로토타입</Status>, links: [["저장소", LINKS.investopia]] },
  { name: "SoloPlay", status: <Status tone="gray">백엔드 프로젝트 · 저장소 공개</Status>, links: [["저장소", LINKS.soloplay], ["화면 시안", LINKS.soloplayDesign]] },
] as const;

function EvidenceSlide() {
  return (
    <Slide id="evidence" number="09">
      <SectionLabel number="09">프로젝트 링크 · 연락처</SectionLabel>
      <div className="evidence-header">
        <div>
          <h2>프로젝트 링크</h2>
        </div>
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
        </div>
        <div className="link-row">
          <Link href={LINKS.github}>GitHub</Link>
          <Link href={LINKS.email}>playlistdh@gmail.com</Link>
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
