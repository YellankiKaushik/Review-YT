import { test, expect } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { sample } from "../../apps/web/tests/sample";
const id = sample.video.id;
const thumbnail = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360"><defs><linearGradient id="g"><stop stop-color="#12263e"/><stop offset="1" stop-color="#136b65"/></linearGradient></defs><rect width="640" height="360" fill="url(#g)"/><rect x="36" y="36" width="150" height="36" rx="8" fill="#dff5e9"/><text x="53" y="61" fill="#14263e" font-family="Arial" font-size="18">Review-YT</text><text x="36" y="170" fill="white" font-family="Arial" font-size="42">Read the conversation.</text><text x="36" y="218" fill="#dff5e9" font-family="Arial" font-size="30">Keep the context.</text><text x="36" y="316" fill="white" font-family="Arial" font-size="18">ORIGINAL ILLUSTRATIVE VIDEO ART</text></svg>`;
const demo = {
  ...sample,
  video: {
    ...sample.video,
    title: "An honest look at the conversation",
    channel: "Review-YT · illustrative demo",
  },
  sampled: 10,
  sentiment: {
    ...sample.sentiment,
    totals: { positive: 6, neutral: 3, negative: 1 },
    shares: { positive: 60, neutral: 30, negative: 10 },
  },
  warnings: ["Illustrative demo data, not real YouTube feedback."],
};
test.beforeEach(async ({ page }) => {
  await page.route("https://i.ytimg.com/**", (r) =>
    r.fulfill({ contentType: "image/svg+xml", body: thumbnail }),
  );
});
for (const width of [375, 390, 768, 1024, 1440, 1920])
  test(`homepage and results remain readable at ${width}px`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width, height: 1000 });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toContainText(
      "Understand the feedback",
    );
    await expect(
      page.getByLabel("YouTube video", { exact: true }),
    ).toBeEnabled();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    const capture = process.env.UPDATE_DOC_ASSETS === "1";
    if (capture) mkdirSync("docs/assets", { recursive: true });
    if (capture && width === 1440 && info.project.name === "desktop")
      await page.screenshot({
        path: "docs/assets/review-yt-homepage.png",
        fullPage: true,
        scale: "css",
      });
    await page.route("**/api/results?**", (r) => r.fulfill({ json: demo }));
    await page.goto(`/review/${id}?via=disabled`);
    await expect(
      page.getByRole("heading", { name: demo.video.title }),
    ).toBeVisible();
    await expect(
      page.getByRole("img", { name: /Sample sentiment: 60% positive/ }),
    ).toBeVisible();
    await expect(
      page.getByText(demo.warnings[0], { exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    if (capture && width === 1440 && info.project.name === "desktop")
      await page.screenshot({
        path: "docs/assets/review-yt-results.png",
        fullPage: true,
        scale: "css",
      });
    if (capture && width === 390 && info.project.name === "mobile")
      await page.screenshot({
        path: "docs/assets/review-yt-mobile.png",
        fullPage: true,
        scale: "css",
      });
    expect(errors).toEqual([]);
  });
for (const [name, totals] of Object.entries({
  positive: [10, 0, 0],
  neutral: [0, 10, 0],
  negative: [0, 0, 10],
  balanced: [1, 1, 1],
  fractional: [2, 1, 0],
  empty: [0, 0, 0],
}))
  test(`chart handles ${name} sample and long metadata`, async ({ page }) => {
    const count = totals.reduce((a, b) => a + b, 0);
    const shares = totals.map((n) => (count ? (n / count) * 100 : 0));
    const review = {
      ...demo,
      video: {
        ...demo.video,
        title: "A very long public video title ".repeat(12),
        channel: "ChannelNameWithoutBreaks".repeat(15),
      },
      sampled: count,
      sentiment: {
        ...sample.sentiment,
        totals: {
          positive: totals[0],
          neutral: totals[1],
          negative: totals[2],
        },
        shares: {
          positive: shares[0],
          neutral: shares[1],
          negative: shares[2],
        },
      },
    };
    await page.route("**/api/results?**", (r) => r.fulfill({ json: review }));
    await page.goto(`/review/${id}?via=disabled`);
    await expect(
      page.getByRole("heading", { name: review.video.title }),
    ).toBeVisible();
    if (count)
      await expect(
        page.getByRole("img", {
          name: `Sample sentiment: ${shares[0]}% positive, ${shares[1]}% neutral, ${shares[2]}% negative`,
        }),
      ).toBeVisible();
    else {
      await expect(
        page.getByText(/No public comments were returned/),
      ).toBeVisible();
      await expect(
        page.getByRole("img", { name: /Sample sentiment/ }),
      ).toHaveCount(0);
    }
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
test("skip navigation focuses the main content with reduced motion", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#content")).toBeFocused();
  expect(
    await page.evaluate(
      () => getComputedStyle(document.documentElement).scrollBehavior,
    ),
  ).toBe("auto");
});
test("an invalid public video link preserves the editable form", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByLabel("YouTube video", { exact: true })
    .fill("https://example.com/private");
  await page.getByRole("button", { name: "Review this video" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByLabel("YouTube video", { exact: true })).toBeEnabled();
});
