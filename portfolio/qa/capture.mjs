import { mkdir, writeFile } from "node:fs/promises";

const endpoint = process.env.PORTFOLIO_CDP ?? "http://127.0.0.1:9333";
const pageUrl = process.env.PORTFOLIO_URL ?? "http://127.0.0.1:5173/";
const outputDir = new URL("./screenshots/", import.meta.url);

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
await send("Emulation.setDeviceMetricsOverride", {
  deviceScaleFactor: 1,
  height: 900,
  mobile: false,
  width: 1600,
});

const loaded = waitForEvent("Page.loadEventFired");
await send("Page.navigate", { url: pageUrl });
await loaded;
await send("Runtime.evaluate", {
  awaitPromise: true,
  expression:
    "document.fonts.ready.then(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))))",
});

const { result } = await send("Runtime.evaluate", {
  expression: `(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
    };

    return [...document.querySelectorAll(".slide")].map((slide, index) => {
      const slideRect = slide.getBoundingClientRect();
      const elements = [...slide.querySelectorAll("*")].filter(visible);
      const textElements = elements.filter((element) =>
        [...element.childNodes].some(
          (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
        ),
      );
      const nonFooterText = textElements.filter((element) => !element.closest(".slide-footer"));
      const overflow = elements
        .filter((element) => {
          const rect = element.getBoundingClientRect();
          return (
            rect.left < slideRect.left - 0.5 ||
            rect.top < slideRect.top - 0.5 ||
            rect.right > slideRect.right + 0.5 ||
            rect.bottom > slideRect.bottom + 0.5
          );
        })
        .map((element) => ({
          className: String(element.className).slice(0, 80),
          tag: element.tagName,
          text: (element.textContent || "").trim().slice(0, 80),
        }));

      return {
        bounds: {
          height: slideRect.height,
          width: slideRect.width,
          x: slideRect.left + scrollX,
          y: slideRect.top + scrollY,
        },
        id: slide.id,
        images: [...slide.querySelectorAll("img")].map((image) => {
          const rect = image.getBoundingClientRect();
          return {
            alt: image.alt,
            natural: [image.naturalWidth, image.naturalHeight],
            rendered: [Number(rect.width.toFixed(2)), Number(rect.height.toFixed(2))],
            scale: Number(Math.max(rect.width / image.naturalWidth, rect.height / image.naturalHeight).toFixed(3)),
          };
        }),
        links: [...slide.querySelectorAll("a")].map((link) => link.href),
        minFontNonFooter: Math.min(
          ...nonFooterText.map((element) => Number.parseFloat(getComputedStyle(element).fontSize)),
        ),
        number: index + 1,
        overflow,
      };
    });
  })()`,
  returnByValue: true,
});

const audit = result.value;
await mkdir(outputDir, { recursive: true });

for (const slide of audit) {
  const screenshot = await send("Page.captureScreenshot", {
    captureBeyondViewport: true,
    clip: { ...slide.bounds, scale: 1 },
    format: "png",
    fromSurface: true,
  });
  const filename = `${String(slide.number).padStart(2, "0")}-${slide.id}.png`;
  await writeFile(new URL(filename, outputDir), Buffer.from(screenshot.data, "base64"));
}

await writeFile(new URL("./audit.json", import.meta.url), `${JSON.stringify(audit, null, 2)}\n`);

await send("Emulation.setEmulatedMedia", { media: "print" });
const printResult = await send("Runtime.evaluate", {
  expression: `(() => ({
    links: [...document.querySelectorAll("a")].map((link) => ({
      display: getComputedStyle(link).display,
      href: link.href,
      visible: link.getBoundingClientRect().width > 0 && link.getBoundingClientRect().height > 0,
    })),
    slides: [...document.querySelectorAll(".slide")].map((slide) => {
      const rect = slide.getBoundingClientRect();
      return { height: rect.height, id: slide.id, width: rect.width };
    }),
  }))()`,
  returnByValue: true,
});
await writeFile(
  new URL("./print-audit.json", import.meta.url),
  `${JSON.stringify(printResult.result.value, null, 2)}\n`,
);
socket.close();

console.log(`Captured ${audit.length} slides`);
