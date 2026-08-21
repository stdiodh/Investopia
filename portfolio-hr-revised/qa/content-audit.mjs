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
        kpis: [...new Set([
          ...[...slide.querySelectorAll(kpiSelector)].map((element) => normalize(element.textContent)),
          ...arrowKpis,
          ...scalarKpis,
        ].filter(Boolean))],
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
  { aliases: /a\s*(?:&|and|-)\s*i|aandi/i, name: "A&I.com", status: /운영\s*(?:중|서비스)|실서비스|live/i },
  { aliases: /gojjibom|고찌봄/i, name: "고찌봄", status: /공개\s*데모|샘플\s*데이터|demo/i },
  { aliases: /didim|디딤로그/i, name: "디딤로그", status: /공개\s*(?:프론트\s*)?데모|입력\s*미저장|demo/i },
  { aliases: /investopia/i, name: "Investopia", status: /로컬\s*프로토타입|저장소\s*공개|local|repo/i },
  { aliases: /soloplay|solo\s*play/i, name: "SoloPlay", status: /백엔드\s*프로젝트|저장소\s*공개|repo/i },
];
const deploymentResults = deployments.map((project) => {
  const projectSlides = slides.filter(
    (slide) => project.aliases.test(slide.id) || project.aliases.test(slide.text),
  );
  const explicitLabels = projectSlides.flatMap((slide) =>
    slide.statusLabels.map((label) => ({ id: slide.id, label })),
  );
  const explicitMatch = explicitLabels.find(({ label }) => project.status.test(label));
  const fallbackMatch = projectSlides.find((slide) => project.status.test(slide.text));
  return {
    explicitLabels,
    found: Boolean(explicitMatch || fallbackMatch),
    name: project.name,
    source: explicitMatch ? "status-label" : fallbackMatch ? "slide-text" : null,
    slideId: explicitMatch?.id ?? fallbackMatch?.id ?? null,
  };
});
addCheck(
  "deployment-statuses",
  deploymentResults.length === 5 && deploymentResults.every((result) => result.found),
  { projects: deploymentResults },
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
  slides: slides.map(({ footer, id, kpis, number, statusLabels }) => ({
    footer,
    id,
    kpis,
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
