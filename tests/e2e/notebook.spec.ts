import { test, expect, type Page } from "@playwright/test";
const video = "aB3_dE5-fG7";
test.beforeEach(async ({ page }) => {
  await page.route("https://i.ytimg.com/**", (route) =>
    route.fulfill({
      contentType: "image/svg+xml",
      body: '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="320" height="180" fill="#275e48"/><text x="25" y="95" fill="white">OFFLINE CI FIXTURE</text></svg>',
    }),
  );
});
async function submit(page: Page, provider: string) {
  await page.goto("/");
  await page.getByLabel("YouTube video", { exact: true }).fill(video);
  await page.getByLabel("Comment sample").selectOption("10");
  await expect(page.getByLabel("Research notes")).toContainText("Local Gemma");
  await page.getByLabel("Research notes").selectOption(provider);
  const pending = page.waitForResponse(
    (r) => r.url().endsWith("/api/analyze") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Review this video" }).click();
  const response = await pending;
  expect(response.status()).toBe(200);
  expect(response.request().postDataJSON()).toEqual({
    video,
    sample: 10,
    provider,
  });
  const data = await response.json();
  await expect(page).toHaveURL(
    `http://127.0.0.1:3201/review/${video}?via=${provider}`,
  );
  await expect(
    page.getByRole("heading", { name: "Offline notebook test video" }),
  ).toBeVisible();
  return data;
}
test("empty input stays local and explains what is needed", async ({
  page,
}) => {
  let calls = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/analyze")) calls++;
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Review this video" }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "Paste a YouTube" }),
  ).toBeVisible();
  expect(calls).toBe(0);
});
test("real form, chart, reload and cache-only deep link", async ({
  page,
  context,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const data = await submit(page, "disabled");
  expect(data.sampled).toBe(10);
  const shares = data.sentiment.shares;
  await expect(
    page.getByRole("img", {
      name: `Sample sentiment: ${shares.positive}% positive, ${shares.neutral}% neutral, ${shares.negative}% negative`,
    }),
  ).toBeVisible();
  let posts = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/analyze")) posts++;
  });
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "Offline notebook test video" }),
  ).toBeVisible();
  expect(posts).toBe(0);
  const fresh = await context.newPage();
  await fresh.goto(`/review/${video}?via=disabled`);
  await expect(
    fresh.getByRole("heading", { name: "Offline notebook test video" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});
test("provider failure preserves the local model and never borrows its notes", async ({
  page,
}) => {
  const local = await submit(page, "ollama");
  expect(local.ai.status).toBe("complete");
  await expect(
    page.getByRole("region", { name: "Research note attribution" }),
  ).toContainText("offline-fixture-gemma");
  const cloud = await submit(page, "openrouter");
  expect(cloud.ai.status).toBe("unavailable");
  expect(cloud.sourceDigest).toBe(local.sourceDigest);
  await expect(page.getByRole("status")).toContainText("rate limited");
  await expect(
    page.getByRole("img", { name: /Sample sentiment/ }),
  ).toBeVisible();
  const repeated = await submit(page, "ollama");
  expect(repeated.caching.reused).toBe(true);
  expect(repeated.ai).toEqual(local.ai);
});
test("expired or absent saved reviews offer a new analysis without starting one", async ({
  page,
}) => {
  let posts = 0;
  page.on("request", (r) => {
    if (r.url().endsWith("/api/analyze")) posts++;
  });
  await page.goto("/review/zY8_xW6-vU4?via=disabled");
  await expect(
    page.getByRole("heading", { name: "This page has no saved review." }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Start a new review" }),
  ).toBeVisible();
  expect(posts).toBe(0);
});
