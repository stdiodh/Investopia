import { writeFile } from "node:fs/promises";

const endpoint = process.env.PORTFOLIO_CDP ?? "http://127.0.0.1:9333";
const pageUrl = process.env.PORTFOLIO_URL ?? "http://127.0.0.1:5173/";

const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((item) => item.type === "page");

if (!target) {
  throw new Error("No Chrome page target found");
}

const socket = new WebSocket(target.webSocketDebuggerUrl);
const pending = new Map();
const eventWaiters = new Map();
let nextId = 0;

socket.addEventListener("message", ({ data }) => {
  const message = JSON.parse(data);

  if (message.id) {
    const request = pending.get(message.id);
    pending.delete(message.id);
    if (message.error) request.reject(new Error(message.error.message));
    else request.resolve(message.result);
    return;
  }

  const waiter = eventWaiters.get(message.method);
  if (waiter) {
    eventWaiters.delete(message.method);
    waiter(message.params);
  }
});

await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

function send(method, params = {}) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, { reject, resolve });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

function waitForEvent(method) {
  return new Promise((resolve) => eventWaiters.set(method, resolve));
}

await send("Page.enable");
await send("Runtime.enable");
const loaded = waitForEvent("Page.loadEventFired");
await send("Page.navigate", { url: pageUrl });
await loaded;
await send("Runtime.evaluate", {
  awaitPromise: true,
  expression:
    "document.fonts.ready.then(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))))",
});

const domResult = await send("Runtime.evaluate", {
  expression: `(() => {
    const normalize = (value) => (value || "").replace(/\\s+/g, " ").trim();
    const kpiSelector = [
      "[data-kpi]",
      ".kpi",
      ".metric-value",
      ".metric-rail dt",
      "[class*='metric'] strong",
      "[class*='result'] strong",
    ].join(",");
    const statusSelector = [
      "[data-deployment-status]",
      ".deployment-status",
      ".project-status",
      ".status-label",
      ".status-chip",
      ".status-badge",
      "[class*='status']",
    ].join(",");

    return [...document.querySelectorAll(".slide")].map((slide, index) => {
      const text = normalize(slide.textContent);
      const arrowKpis = text.match(/\\d[\\d,.]*(?:\\s*(?:ms|초|회|개|%|일))?\\s*→\\s*\\d[\\d,.]*(?:\\s*(?:ms|초|회|개|%|일))?/gi) || [];
      const scalarKpis = text.match(/\\d+(?:\\.\\d+)?\\s*(?:ms|초|회|%|일)(?![가-힣])/gi) || [];
      return {
        footer: normalize(slide.querySelector(".slide-footer")?.textContent),
        id: slide.id,
        images: [...slide.querySelectorAll("img")].map((image) => ({
          alt: image.alt,
          src: image.src,
        })),
        kpis: [...new Set([
          ...[...slide.querySelectorAll(kpiSelector)].map((element) => normalize(element.textContent)),
          ...arrowKpis,
          ...scalarKpis,
        ].filter(Boolean))],
        links: [...slide.querySelectorAll("a")].map((link) => ({
          href: link.href,
          text: normalize(link.textContent),
        })),
        number: index + 1,
        statusLabels: [...new Set(
          [...slide.querySelectorAll(statusSelector)]
            .map((element) => normalize(element.textContent))
            .filter(Boolean),
        )],
        text,
      };
    });
  })()`,
  returnByValue: true,
});
const slides = domResult.result.value;
socket.close();

const checks = [];
const addCheck = (id, passed, details) => checks.push({ details, id, passed });
const cover = slides.find((slide) => slide.id === "cover") ?? slides[0];

addCheck("slide-count", slides.length === 9, {
  actual: slides.length,
  expected: 9,
  slideIds: slides.map((slide) => slide.id),
});

const evidence = slides.find((slide) => slide.id === "evidence");
const defensiveCopy = [
  "상세한 기술 이력은 이력서에 두고, 여기에는 문제와 선택의 결과를 남겼습니다.",
  "직접 확인할 수 있는 경로만 모았습니다.",
  "배포되지 않은 프로젝트는 운영 서비스처럼 보이게 쓰지 않았습니다.",
  "이 포트폴리오는 이력서에 담기 어려운 판단, 실제 화면, 근거 링크를 보충합니다.",
];
const defensiveCopyMatches = slides.flatMap((slide) =>
  defensiveCopy
    .filter((copy) => slide.text.includes(copy))
    .map((copy) => ({ copy, id: slide.id })),
);
addCheck(
  "neutral-portfolio-copy",
  Boolean(evidence && defensiveCopyMatches.length === 0),
  {
    forbiddenMatches: defensiveCopyMatches,
    rule: "포트폴리오의 범위를 해명하지 않고 프로젝트 자료를 중립적으로 안내",
  },
);

const templateCopy = [
  "문제를 발견한 배경, 내가 내린 판단, 확인한 결과를 프로젝트별로 담았습니다.",
  "프로젝트마다 한 가지 판단만 먼저 보이게 했습니다.",
  "프로젝트별 역할, 핵심 판단, 확인 결과를 한눈에 정리했습니다.",
  "문제 → 내 판단 → 확인 결과 → 직접 볼 수 있는 근거",
  "서비스 · 저장소 · 보도 자료를 프로젝트별로 정리했습니다.",
];
const decorativeLabels = [
  "PROJECT MAP",
  "ONE CASE",
  "SERVICE UI FRAME",
  "LOCAL SAMPLE BENCHMARK",
  "CODE-BACKED FLOW",
  "TEST",
];
const templateCopyMatches = slides.flatMap((slide) => [
  ...templateCopy
    .filter((copy) => slide.text.includes(copy))
    .map((copy) => ({ copy, id: slide.id, type: "meta-copy" })),
  ...decorativeLabels
    .filter((label) => slide.text.includes(label))
    .map((copy) => ({ copy, id: slide.id, type: "decorative-label" })),
]);
addCheck("anti-template-copy", templateCopyMatches.length === 0, {
  matches: templateCopyMatches,
  rule: "구성 설명의 반복과 장식용 영문 라벨을 사용하지 않음",
});

const footerFailures = slides
  .filter((slide) => {
    return !new RegExp(`0?${slide.number}\\s*\\/\\s*9(?:\\s|$)`).test(slide.footer);
  })
  .map((slide) => ({ footer: slide.footer, id: slide.id, number: slide.number }));
addCheck("footer-total", slides.length === 9 && footerFailures.length === 0, {
  failures: footerFailures,
  expected: "각 슬라이드의 01 / 9 … 09 / 9",
});

const forbiddenPatterns = [
  ["2,011", /2\s*,?\s*011/gi],
  ["78.2%", /78\.2\s*%/gi],
  ["195개 PR", /195\s*개\s*(?:병합\s*)?PR/gi],
  ["188→456", /188\s*→\s*456/g],
  ["140→109", /140\s*→\s*109/g],
  ["141개", /141\s*개/g],
  ["105개", /105\s*개/g],
  ["성장", /성장/g],
  ["Velog", /Velog/gi],
  ["장학금", /장학금/g],
];
const forbiddenMatches = forbiddenPatterns.flatMap(([label, pattern]) =>
  slides.flatMap((slide) => {
    const matches = slide.text.match(pattern);
    return matches ? [{ id: slide.id, label, matches }] : [];
  }),
);
addCheck("forbidden-resume-duplicates", forbiddenMatches.length === 0, {
  matches: forbiddenMatches,
});

addCheck("cover-project-count", /5\s*개\s*프로젝트/.test(cover?.text ?? ""), {
  coverId: cover?.id ?? null,
  expected: "5개 프로젝트",
});

const serviceCountPattern = /(?:5\s*개\s*(?:A&I(?:\.com)?\s*)?(?:백엔드\s*)?서비스|서비스\s*5\s*개)/i;
const serviceCountSlides = slides
  .filter((slide) => serviceCountPattern.test(slide.text))
  .map((slide) => ({ id: slide.id, text: slide.text.match(serviceCountPattern)?.[0] }));
const misplacedServiceCounts = serviceCountSlides.filter(({ id }) => {
  const slide = slides.find((item) => item.id === id);
  return !/a\s*(?:&|and|-)\s*i|aandi/i.test(`${id} ${slide?.text ?? ""}`);
});
addCheck("service-count-scope", misplacedServiceCounts.length === 0, {
  found: serviceCountSlides,
  rule: "5개 서비스는 A&I 슬라이드에서만 허용",
});

const calculationMatches = slides.flatMap((slide) => {
  const wordMatches = slide.text.match(/계산(?:식|법|과정|방법|하여|해서|한|해|을|은|이|된|값)?/g) ?? [];
  const formulaMatches = slide.text.match(
    /\d[\d,.]*\s*(?:=|×|÷|\*)\s*\d[\d,.]*|\d[\d,.]*\s*[+\-−]\s*\d[\d,.]*\s*\/\s*\d[\d,.]*/g,
  ) ?? [];
  return wordMatches.length || formulaMatches.length
    ? [{ formulaMatches, id: slide.id, wordMatches }]
    : [];
});
addCheck("no-calculation-explanation", calculationMatches.length === 0, {
  matches: calculationMatches,
  rule: "전후 수치와 짧은 측정 조건만 사용하고 계산식·계산 설명은 쓰지 않음",
});

const deployments = [
  { id: "aandi-architecture", name: "A&I.com", status: /운영\s*서비스/i },
  { id: "gojjibom", name: "고찌봄", status: /공개\s*데모\s*·\s*샘플\s*데이터/i },
  { id: "didimlog", name: "디딤로그", status: /공개\s*프론트\s*데모\s*·\s*입력\s*미저장/i },
  { id: "investopia", name: "Investopia", status: /로컬\s*·\s*하드웨어\s*프로토타입/i },
  { id: "soloplay", name: "SoloPlay", status: /백엔드\s*프로젝트\s*·\s*저장소\s*공개/i },
];
const deploymentResults = deployments.map((project) => {
  const projectSlide = slides.find((slide) => slide.id === project.id);
  const explicitLabels = (projectSlide?.statusLabels ?? []).map((label) => ({
    id: project.id,
    label,
  }));
  const explicitMatch = explicitLabels.find(({ label }) => project.status.test(label));
  return {
    explicitLabels,
    found: Boolean(explicitMatch),
    name: project.name,
    source: explicitMatch ? "status-label" : null,
    slideId: explicitMatch?.id ?? null,
  };
});
addCheck(
  "deployment-statuses",
  deploymentResults.length === 5 && deploymentResults.every((result) => result.found),
  { projects: deploymentResults },
);

const aandiArchitecture = slides.find((slide) => slide.id === "aandi-architecture");
addCheck(
  "aandi-ui-evidence",
  Boolean(
    aandiArchitecture?.images.some((image) => /과제 목록 시연 영상 프레임/.test(image.alt)) &&
    /과제 목록 시연 영상 프레임/.test(aandiArchitecture?.text ?? "") &&
    /2026\.06/.test(aandiArchitecture?.text ?? "") &&
    /서비스 화면/.test(aandiArchitecture?.text ?? "") &&
    !/OPERATING PROOF/.test(aandiArchitecture?.text ?? ""),
  ),
  {
    images: aandiArchitecture?.images ?? [],
    rule: "3페이지 화면은 서비스 UI 프레임으로만 설명하고 운영 성능 근거로 과장하지 않음",
  },
);

const aandiQuery = slides.find((slide) => slide.id === "aandi-query");
const aandiRequiredLinks = [
  "https://github.com/Team-AnI/A-AND-I-WEB-SERVER/blob/main/docs/performance/results/2026-07-09-assignment-list-before-after.md",
  "https://github.com/Team-AnI/A-AND-I-WEB-SERVER/blob/main/performance/results/assignment-read-query-evidence.json",
];
addCheck(
  "aandi-measurement-evidence",
  Boolean(
    aandiRequiredLinks.every((href) => aandiQuery?.links.some((link) => link.href === href)) &&
    aandiQuery?.images.some((image) => /60회로 예상.*회귀 테스트에서 2회로 검증/.test(image.alt)) &&
    aandiQuery?.images.some((image) => /9\.297ms에서 7\.565ms/.test(image.alt)) &&
    /확인 결과/.test(aandiQuery?.text ?? "") &&
    /기존 구조 예상 60회 → 회귀 테스트 검증 2회/.test(aandiQuery?.text ?? "") &&
    /(?:service-level|서비스\s*(?:계층\s*)?호출)\s*기준/i.test(aandiQuery?.text ?? ""),
  ),
  {
    images: aandiQuery?.images ?? [],
    links: aandiQuery?.links ?? [],
    rule: "4페이지에 구조·성능 원문 이미지와 직접 링크를 모두 표시",
  },
);

const gojjibom = slides.find((slide) => slide.id === "gojjibom");
const projectMap = slides.find((slide) => slide.id === "project-map");
addCheck(
  "gojjibom-role-sync",
  Boolean(
    projectMap?.text.includes("PM · Dev Lead · 2026.06–07") &&
    gojjibom?.text.includes("고찌봄 · PM · Dev Lead · 2026.06–07"),
  ),
  {
    detail: gojjibom?.text.match(/고찌봄 · PM · Dev Lead · 2026\.06–07/)?.[0] ?? null,
    map: projectMap?.text.match(/PM · Dev Lead · 2026\.06–07/)?.[0] ?? null,
    rule: "프로젝트 맵과 상세 페이지의 역할·기간 표기를 이력서와 일치",
  },
);
const gojjibomAwardCount = gojjibom?.text.match(/최고점\s*·\s*혁신상/g)?.length ?? 0;
const gojjibomRequiredLinks = [
  "https://news.unn.net/news/articleView.html?idxno=594458",
  "https://www.jdnc.or.kr/notice/news.htm?act=view&seq=1019",
];
addCheck(
  "gojjibom-external-proof",
  Boolean(
    gojjibomRequiredLinks.every((href) => gojjibom?.links.some((link) => link.href === href)) &&
    /최고점 · 혁신상/.test(gojjibom?.text ?? "") &&
    gojjibomAwardCount === 1 &&
    !/(?:대회\s*1위|팀\s*MVP)/i.test(gojjibom?.text ?? ""),
  ),
  {
    links: gojjibom?.links ?? [],
    rule: "5페이지의 수상 결과는 주관기관 카드에서 한 번만 표시하고 외부 근거를 연결",
  },
);

const didimlog = slides.find((slide) => slide.id === "didimlog");
const didimlogPerformance =
  "https://github.com/didim-log/didim-log-BE/blob/main/DOCS/refactoring/be-refactor/PHASE_6N_CRAWLER_DETAILS_BOUNDED_PARALLEL.md";
addCheck(
  "didimlog-period-and-benchmark",
  Boolean(
    /2026\.02–현재/.test(didimlog?.text ?? "") &&
    /55\.632초/.test(didimlog?.text ?? "") &&
    /12\.226초/.test(didimlog?.text ?? "") &&
    /77\.96% 단축/.test(didimlog?.text ?? "") &&
    /3,400건 고정 샘플 · 순차\/K=4 · 3회 중앙값/.test(didimlog?.text ?? "") &&
    didimlog?.links.some((link) => link.href === didimlogPerformance),
  ),
  {
    links: didimlog?.links ?? [],
    rule: "디딤로그 최신 기간과 로컬 고정 샘플 측정 조건·원문 링크를 함께 표시",
  },
);

const soloplay = slides.find((slide) => slide.id === "soloplay");
const soloplayRequiredLinks = [
  "https://github.com/SangWook16074/Solo-Play-Web-Server/blob/develop/src/test/kotlin/com/example/solo_play_web_server/place/service/PlaceServiceSpec.kt",
  "https://github.com/SangWook16074/Solo-Play-Web-Server/blob/develop/src/test/kotlin/com/example/solo_play_web_server/place/service/PlaceEnrichmentServiceSpec.kt",
];
addCheck(
  "soloplay-visual-and-test-proof",
  Boolean(
    soloplay?.images.some((image) => /화면 시안/.test(image.alt)) &&
    /SoloPlay UI 시안/.test(soloplay?.text ?? "") &&
    /테스트(?:\s*시나리오)?\s*19개/.test(soloplay?.text ?? "") &&
    !/실패\s*0/.test(soloplay?.text ?? "") &&
    soloplayRequiredLinks.every((href) => soloplay?.links.some((link) => link.href === href)) &&
    /저장본\s*유지|원본(?:\s*장소)?\s*저장/.test(soloplay?.text ?? ""),
  ),
  {
    images: soloplay?.images ?? [],
    links: soloplay?.links ?? [],
    rule: "8페이지에 UI 시안임을 밝히고 19개 시나리오의 공개 테스트 소스를 연결",
  },
);

const evidenceRequiredLinks = [
  "https://aandiclub.com/",
  "https://github.com/Team-AnI/A-AND-I-WEB-SERVER",
  "https://github.com/TIKI-TAKA-hackathon/Tiki-Taka-BE",
  "https://github.com/didim-log/didim-log-BE",
  didimlogPerformance,
  "https://github.com/stdiodh/Investopia",
  "https://github.com/SangWook16074/Solo-Play-Web-Server",
  "mailto:playlistdh@gmail.com",
];
addCheck(
  "evidence-directory-links",
  Boolean(
    evidenceRequiredLinks.every((href) => evidence?.links.some((link) => link.href === href)) &&
    /공개 데모 · 샘플 데이터/.test(evidence?.text ?? "") &&
    /공개 데모 · 입력 미저장/.test(evidence?.text ?? "") &&
    /로컬 · 하드웨어 프로토타입/.test(evidence?.text ?? "") &&
    /백엔드 프로젝트 · 저장소 공개/.test(evidence?.text ?? ""),
  ),
  {
    links: evidence?.links ?? [],
    rule: "9페이지에 프로젝트별 실제 상태와 서비스·저장소·검증 링크를 일관되게 제공",
  },
);

const canonicalKpi = (value) =>
  value
    .toLowerCase()
    .replace(/,/g, "")
    .replace(/\s+/g, "")
    .replace(/[()]/g, "");
const kpiSlides = new Map();
for (const slide of slides) {
  for (const kpi of slide.kpis) {
    const canonical = canonicalKpi(kpi);
    if (!canonical || canonical === "5개" || /^0?[1-9]\/9$/.test(canonical)) continue;
    const entries = kpiSlides.get(canonical) ?? [];
    if (!entries.some((entry) => entry.id === slide.id)) {
      entries.push({ id: slide.id, value: kpi });
    }
    kpiSlides.set(canonical, entries);
  }
}
const repeatedKpis = [...kpiSlides.entries()]
  .filter(([, entries]) => entries.length > 1)
  .map(([canonical, entries]) => ({ canonical, occurrences: entries }));
addCheck("unique-core-kpis", repeatedKpis.length === 0, {
  repeats: repeatedKpis,
  rule: "같은 핵심 KPI를 여러 슬라이드에서 반복하지 않음",
});

const failedChecks = checks.filter((check) => !check.passed);
const report = {
  checks,
  generatedAt: new Date().toISOString(),
  pageUrl,
  passed: failedChecks.length === 0,
  slides: slides.map(({ footer, id, images, kpis, links, number, statusLabels }) => ({
    footer,
    id,
    images,
    kpis,
    links,
    number,
    statusLabels,
  })),
  summary: {
    failed: failedChecks.length,
    passed: checks.length - failedChecks.length,
    total: checks.length,
  },
};

await writeFile(
  new URL("./content-audit.json", import.meta.url),
  `${JSON.stringify(report, null, 2)}\n`,
);

if (report.passed) {
  console.log(`Content audit passed (${checks.length}/${checks.length})`);
} else {
  console.error(
    `Content audit failed (${failedChecks.length}/${checks.length}): ` +
      failedChecks.map((check) => check.id).join(", "),
  );
  process.exitCode = 1;
}
