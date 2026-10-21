/** Reproducible real UI captures; all result content is explicitly illustrative. */
const { chromium } = require("@playwright/test");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const net = require("node:net");
const { once } = require("node:events");
const root = path.resolve(__dirname, "..");
const base = "http://127.0.0.1:3203";
const fixture = require("../tests/fixtures/product-demo.json");
const inventory = {
  selectionDefault: "disabled",
  options: [
    {
      id: "disabled",
      configured: true,
      model: "",
      execution: "none",
      description: "Sentiment only; no model requests.",
    },
  ],
  constraints: { paid: false, automaticFallback: false },
};
const thumbnail = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360"><defs><linearGradient id="g"><stop stop-color="#14263e"/><stop offset="1" stop-color="#136b65"/></linearGradient></defs><rect width="640" height="360" fill="url(#g)"/><rect x="36" y="36" width="160" height="36" rx="8" fill="#dff5e9"/><g font-family="Arial"><text x="53" y="61" fill="#14263e" font-size="18">Review-YT</text><text x="36" y="170" fill="white" font-size="40">Read the conversation.</text><text x="36" y="218" fill="#dff5e9" font-size="30">Keep the context.</text><text x="36" y="316" fill="white" font-size="18">ORIGINAL ILLUSTRATIVE VIDEO ART</text></g></svg>`;
async function ensureFreePort() {
  await new Promise((resolve, reject) => {
    const server = net.createServer();
    server.once("error", () =>
      reject(new Error("Capture port3203 is occupied; nothing stopped.")),
    );
    server.listen(3203, "127.0.0.1", () => server.close(resolve));
  });
}
async function main() {
  await ensureFreePort();
  fs.mkdirSync(path.join(root, "artifacts"), { recursive: true });
  fs.mkdirSync(path.join(root, "docs/assets"), { recursive: true });
  if (!fs.existsSync(path.join(root, "apps/web/.next/BUILD_ID")))
    throw new Error("Run npm run build first.");
  const output = fs.openSync(
    path.join(root, "artifacts/capture-product-server.log"),
    "w",
  );
  const server = spawn(
    process.execPath,
    [
      path.join(root, "node_modules/next/dist/bin/next"),
      "start",
      path.join(root, "apps/web"),
      "--hostname",
      "127.0.0.1",
      "--port",
      "3203",
    ],
    {
      cwd: root,
      windowsHide: true,
      stdio: ["ignore", output, output],
      env: {
        ...process.env,
        NEXT_TELEMETRY_DISABLED: "1",
        BACKEND_URL: "https://127.0.0.1:5103",
        BACKEND_API_TOKEN: "capture-fixture-not-a-production-credential",
        REVIEW_LOCAL_TEST: "false",
        REVIEW_DIST: ".next",
      },
    },
  );
  let browser;
  try {
    let ready = false;
    for (let i = 0; i < 60; i++) {
      try {
        const r = await fetch(base, { signal: AbortSignal.timeout(1000) });
        if (r.ok) {
          ready = true;
          break;
        }
      } catch {}
      await new Promise((r) => setTimeout(r, 500));
    }
    if (!ready)
      throw new Error("Owned optimized capture server did not become ready.");
    browser = await chromium.launch();
    const errors = [],
      records = [];
    let analysisRequests = 0;
    for (const target of [
      { name: "homepage", width: 1440, height: 1000, route: "/" },
      {
        name: "results",
        width: 1440,
        height: 1100,
        route: `/review/${fixture.video.id}?via=disabled`,
      },
      {
        name: "mobile",
        width: 390,
        height: 844,
        route: `/review/${fixture.video.id}?via=disabled`,
      },
    ]) {
      const context = await browser.newContext({
        viewport: { width: target.width, height: target.height },
        isMobile: target.name === "mobile",
        hasTouch: target.name === "mobile",
        deviceScaleFactor: 1,
        reducedMotion: "reduce",
      });
      const demo = {
        ...fixture,
        created: new Date().toISOString(),
        caching: {
          reused: false,
          validUntil: new Date(Date.now() + 1800000).toISOString(),
        },
      };
      await context.route("**/api/providers", (r) =>
        r.fulfill({ json: inventory }),
      );
      await context.route("**/api/results?**", (r) =>
        r.fulfill({ json: demo }),
      );
      await context.route("https://i.ytimg.com/**", (r) =>
        r.fulfill({ contentType: "image/svg+xml", body: thumbnail }),
      );
      await context.route("**/api/analyze", (r) => {
        analysisRequests++;
        return r.abort();
      });
      await context.addInitScript(() => {
        window.__productPerf = { lcp: 0, cls: 0 };
        new PerformanceObserver((list) => {
          for (const e of list.getEntries())
            window.__productPerf.lcp = e.startTime;
        }).observe({ type: "largest-contentful-paint", buffered: true });
        new PerformanceObserver((list) => {
          for (const e of list.getEntries())
            if (!e.hadRecentInput) window.__productPerf.cls += e.value;
        }).observe({ type: "layout-shift", buffered: true });
      });
      const page = await context.newPage();
      page.on("pageerror", (e) => errors.push(e.name));
      page.on("console", (m) => {
        if (m.type() === "error") errors.push(m.text().slice(0, 150));
      });
      await page.goto(base + target.route, { waitUntil: "networkidle" });
      if (target.name === "homepage")
        await page.getByLabel("YouTube video", { exact: true }).waitFor();
      else
        await page
          .getByRole("heading", { name: fixture.video.title })
          .waitFor();
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({
        path: path.join(root, `docs/assets/review-yt-${target.name}.png`),
        fullPage: target.name !== "homepage",
        scale: "css",
      });
      const data = await page.evaluate(() => {
        const number = (v) => Number.parseFloat(v) || 0;
        const rgb = (v) => (v.match(/[\d.]+/g) || []).map(Number);
        function background(el) {
          for (let p = el; p; p = p.parentElement) {
            const c = rgb(getComputedStyle(p).backgroundColor);
            if (c.length >= 3 && (c.length === 3 || c[3] === 1)) return c;
          }
          return [255, 255, 255];
        }
        function luminance(c) {
          return c
            .slice(0, 3)
            .map((v) => {
              v /= 255;
              return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
            })
            .reduce((a, v, i) => a + v * [0.2126, 0.7152, 0.0722][i], 0);
        }
        const walker = document.createTreeWalker(
          document.body,
          NodeFilter.SHOW_TEXT,
        );
        let node;
        const contrastFailures = [];
        while ((node = walker.nextNode())) {
          const el = node.parentElement;
          if (
            !node.textContent.trim() ||
            !el ||
            el.closest('[aria-hidden="true"]') ||
            !el.getBoundingClientRect().width
          )
            continue;
          const style = getComputedStyle(el);
          if (style.visibility !== "visible" || style.display === "none")
            continue;
          const color = rgb(style.color);
          if (color.length < 3) continue;
          const a = luminance(color),
            b = luminance(background(el)),
            ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
          const large =
            number(style.fontSize) >= 24 ||
            (number(style.fontSize) >= 18.66 &&
              number(style.fontWeight) >= 700);
          if (ratio + 0.01 < (large ? 3 : 4.5))
            contrastFailures.push({
              tag: el.tagName,
              ratio: Math.round(ratio * 100) / 100,
            });
        }
        const nav = performance.getEntriesByType("navigation")[0];
        return {
          viewport: innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          h1Count: document.querySelectorAll("h1").length,
          mainCount: document.querySelectorAll("main").length,
          unlabeledControls: [
            ...document.querySelectorAll("input,select"),
          ].filter((el) => !el.labels?.length && !el.getAttribute("aria-label"))
            .length,
          missingImageAlt: document.querySelectorAll("img:not([alt])").length,
          contrastFailures,
          metrics: {
            ...window.__productPerf,
            domContentLoadedMs: nav.domContentLoadedEventEnd,
            loadMs: nav.loadEventEnd,
            scriptEncodedBytes: performance
              .getEntriesByType("resource")
              .filter((r) => r.initiatorType === "script")
              .reduce((n, r) => n + r.encodedBodySize, 0),
          },
        };
      });
      records.push({ screen: target.name, ...data });
      await context.close();
    }
    const result = {
      mode: "optimized local Next, explicit illustrative fixtures; not real YouTube/provider inference or a Lighthouse score",
      analysisRequests,
      errors,
      records,
    };
    fs.writeFileSync(
      path.join(root, "artifacts/product-capture-qa.json"),
      JSON.stringify(result, null, 2),
    );
    console.log(JSON.stringify(result));
    if (
      analysisRequests ||
      errors.length ||
      records.some(
        (r) =>
          r.scrollWidth > r.viewport ||
          r.h1Count !== 1 ||
          r.mainCount !== 1 ||
          r.unlabeledControls ||
          r.missingImageAlt ||
          r.contrastFailures.length,
      )
    )
      throw new Error("Product capture QA failed; inspect ignored evidence.");
  } finally {
    if (browser) await browser.close();
    if (server.exitCode === null) {
      server.kill();
      await Promise.race([
        once(server, "exit"),
        new Promise((r) => setTimeout(r, 5000)),
      ]);
    }
    fs.closeSync(output);
  }
}
main().catch((e) => {
  console.error(e.message);
  process.exitCode = 1;
});
