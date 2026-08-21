import { mkdir, writeFile } from "node:fs/promises";

const endpoint = process.env.PORTFOLIO_CDP ?? "http://127.0.0.1:9333";
const pageUrl = process.env.PORTFOLIO_URL ?? "http://127.0.0.1:5173/";
const outputDir = new URL("./screenshots/", import.meta.url);
const viewport = { height: 900, width: 1600 };

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
  height: viewport.height,
  mobile: false,
  width: viewport.width,
});

const loaded = waitForEvent("Page.loadEventFired");
await send("Page.navigate", { url: pageUrl });
await loaded;
await send("Runtime.evaluate", {
  awaitPromise: true,
  expression: `Promise.all([
    document.fonts.ready,
    ...[...document.images].map((image) =>
      image.complete
        ? image.decode().catch(() => undefined)
        : new Promise((resolve) => {
            image.addEventListener("load", resolve, { once: true });
            image.addEventListener("error", resolve, { once: true });
          }),
    ),
  ]).then(() => new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve)),
  ))`,
});

const screenResult = await send("Runtime.evaluate", {
  expression: `(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return (
        style.display !== "none" &&
        style.visibility !== "hidden" &&
        Number.parseFloat(style.opacity) !== 0 &&
        rect.width > 0 &&
        rect.height > 0
      );
    };
    const round = (value) => Number(value.toFixed(2));

    return [...document.querySelectorAll(".slide")].map((slide, index) => {
      const slideRect = slide.getBoundingClientRect();
      const elements = [...slide.querySelectorAll("*")].filter(visible);
      const textElements = elements.filter((element) =>
        !element.closest(".slide-footer") &&
        [...element.childNodes].some(
          (node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
        ),
      );
      const fontSamples = textElements
        .map((element) => ({
          className: String(element.className).slice(0, 100),
          fontSizePx: Number.parseFloat(getComputedStyle(element).fontSize),
          tag: element.tagName,
          text: (element.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 100),
        }))
        .filter((sample) => Number.isFinite(sample.fontSizePx))
        .sort((a, b) => a.fontSizePx - b.fontSizePx);
      const outsideSlide = elements
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
          className: String(element.className).slice(0, 100),
          tag: element.tagName,
          text: (element.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 100),
        }));
      const clippedContent = elements
        .filter((element) =>
          element instanceof HTMLElement &&
          (element.scrollWidth > element.clientWidth + 1 || element.scrollHeight > element.clientHeight + 1),
        )
        .map((element) => ({
          className: String(element.className).slice(0, 100),
          client: [element.clientWidth, element.clientHeight],
          scroll: [element.scrollWidth, element.scrollHeight],
          tag: element.tagName,
          text: (element.textContent || "").trim().replace(/\\s+/g, " ").slice(0, 100),
        }));

      return {
        bounds: {
          height: round(slideRect.height),
          width: round(slideRect.width),
          x: round(slideRect.left + scrollX),
          y: round(slideRect.top + scrollY),
        },
        id: slide.id,
        images: [...slide.querySelectorAll("img")].map((image) => {
          const rect = image.getBoundingClientRect();
          const renderedWidth = round(rect.width);
          const renderedHeight = round(rect.height);
          const scaleX = image.naturalWidth ? renderedWidth / image.naturalWidth : null;
          const scaleY = image.naturalHeight ? renderedHeight / image.naturalHeight : null;
          const upscaleRatio = scaleX === null || scaleY === null ? null : Math.max(scaleX, scaleY);
          return {
            alt: image.alt,
            complete: image.complete,
            natural: [image.naturalWidth, image.naturalHeight],
            rendered: [renderedWidth, renderedHeight],
            scale: {
              x: scaleX === null ? null : round(scaleX),
              y: scaleY === null ? null : round(scaleY),
            },
            sourcePixelsPerRenderedPixel:
              upscaleRatio && upscaleRatio > 0 ? round(1 / upscaleRatio) : null,
            upscaled: upscaleRatio === null ? null : upscaleRatio > 1.01,
          };
        }),
        links: [...slide.querySelectorAll("a")].map((link) => {
          const rect = link.getBoundingClientRect();
          const style = getComputedStyle(link);
          return {
            display: style.display,
            href: link.href,
            rel: link.rel,
            target: link.target,
            text: (link.textContent || "").trim().replace(/\\s+/g, " "),
            visible: visible(link),
            size: [round(rect.width), round(rect.height)],
          };
        }),
        minBodyFontPx: fontSamples[0]?.fontSizePx ?? null,
        smallestText: fontSamples.slice(0, 5),
        number: index + 1,
        overflow: { clippedContent, outsideSlide },
      };
    });
  })()`,
  returnByValue: true,
});

const slides = screenResult.result.value;
await mkdir(outputDir, { recursive: true });

for (const slide of slides) {
  const screenshot = await send("Page.captureScreenshot", {
    captureBeyondViewport: true,
    clip: {
      height: viewport.height,
      scale: 1,
      width: viewport.width,
      x: slide.bounds.x,
      y: slide.bounds.y,
    },
    format: "png",
    fromSurface: true,
  });
  const filename = `${String(slide.number).padStart(2, "0")}-${slide.id}.png`;
  await writeFile(new URL(filename, outputDir), Buffer.from(screenshot.data, "base64"));
}

await send("Emulation.setEmulatedMedia", { media: "print" });
const printResult = await send("Runtime.evaluate", {
  expression: `(() => {
    const visible = (element) => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return (
        style.display !== "none" &&
        style.visibility !== "hidden" &&
        Number.parseFloat(style.opacity) !== 0 &&
        rect.width > 0 &&
        rect.height > 0
      );
    };
    return {
      links: [...document.querySelectorAll("a")].map((link) => ({
        display: getComputedStyle(link).display,
        href: link.href,
        slideId: link.closest(".slide")?.id ?? null,
        text: (link.textContent || "").trim().replace(/\\s+/g, " "),
        visible: visible(link),
      })),
      slides: [...document.querySelectorAll(".slide")].map((slide) => {
        const rect = slide.getBoundingClientRect();
        return {
          height: Number(rect.height.toFixed(2)),
          id: slide.id,
          visible: visible(slide),
          width: Number(rect.width.toFixed(2)),
        };
      }),
    };
  })()`,
  returnByValue: true,
});
const print = printResult.result.value;

const allImages = slides.flatMap((slide) =>
  slide.images.map((image) => ({ ...image, slideId: slide.id })),
);
const allScreenLinks = slides.flatMap((slide) =>
  slide.links.map((link) => ({ ...link, slideId: slide.id })),
);
const audit = {
  generatedAt: new Date().toISOString(),
  pageUrl,
  viewport,
  summary: {
    clippedElementCount: slides.reduce(
      (total, slide) => total + slide.overflow.clippedContent.length,
      0,
    ),
    hiddenPrintLinkCount: print.links.filter((link) => !link.visible).length,
    hiddenScreenLinkCount: allScreenLinks.filter((link) => !link.visible).length,
    outsideSlideElementCount: slides.reduce(
      (total, slide) => total + slide.overflow.outsideSlide.length,
      0,
    ),
    slideCount: slides.length,
    slidesAt1600x900: slides.filter(
      (slide) => slide.bounds.width === viewport.width && slide.bounds.height === viewport.height,
    ).length,
    upscaledImageCount: allImages.filter((image) => image.upscaled).length,
  },
  slides,
  print,
};

await writeFile(new URL("./audit.json", import.meta.url), `${JSON.stringify(audit, null, 2)}\n`);
await writeFile(
  new URL("./print-audit.json", import.meta.url),
  `${JSON.stringify(print, null, 2)}\n`,
);
await send("Emulation.setEmulatedMedia", { media: "screen" });
socket.close();

console.log(
  `Captured ${slides.length} slides at ${viewport.width}x${viewport.height}; ` +
    `${audit.summary.outsideSlideElementCount} outside, ` +
    `${audit.summary.clippedElementCount} clipped, ` +
    `${audit.summary.upscaledImageCount} upscaled images`,
);
