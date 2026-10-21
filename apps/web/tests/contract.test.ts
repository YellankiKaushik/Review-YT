import { describe, it, expect, vi } from "vitest";
import { reviewSchema, inventorySchema, readReview } from "../lib/contract";
import { remember, recall } from "../lib/tab-cache";
import { sample, inventory } from "./sample";
describe("review contract and tab retention", () => {
  it("accepts a coherent counted result", () => {
    expect(reviewSchema.safeParse(sample).success).toBe(true);
    expect(inventorySchema.safeParse(inventory).success).toBe(true);
  });
  it("rejects fabricated totals and impossible percentages", () => {
    const bad = structuredClone(sample);
    bad.sampled = 80;
    expect(reviewSchema.safeParse(bad).success).toBe(false);
    bad.sampled = 4;
    bad.sentiment.shares.positive = 99;
    expect(reviewSchema.safeParse(bad).success).toBe(false);
  });
  it("rejects an unknown provider and missing metadata", () => {
    expect(
      reviewSchema.safeParse({
        ...sample,
        ai: { ...sample.ai, provider: "anything" },
      }).success,
    ).toBe(false);
    expect(reviewSchema.safeParse({ sampled: 4 }).success).toBe(false);
  });
  it("separates providers and honors expiry", () => {
    sessionStorage.clear();
    remember(sample);
    expect(recall(sample.video.id, "disabled")?.sampled).toBe(4);
    expect(recall(sample.video.id, "ollama")).toBeNull();
    remember({
      ...sample,
      caching: { reused: false, validUntil: "2000-01-01T00:00:00Z" },
    });
    expect(recall(sample.video.id, "disabled")).toBeNull();
  });
  it("ignores corrupt browser storage", () => {
    sessionStorage.setItem(
      "review-yt:note:" + sample.video.id + ":disabled",
      "bad json",
    );
    expect(recall(sample.video.id, "disabled")).toBeNull();
  });
  it("returns typed API errors without accepting error bodies", async () => {
    await expect(
      readReview(
        Response.json(
          { error: { message: "Quota exhausted" } },
          { status: 429 },
        ),
      ),
    ).rejects.toThrow("Quota exhausted");
    await expect(readReview(Response.json({}))).rejects.toThrow("incompatible");
  });
});

it("continues without browser storage when access is denied", () => {
  const denied = vi
    .spyOn(Storage.prototype, "getItem")
    .mockImplementation(() => {
      throw new DOMException("denied", "SecurityError");
    });
  const full = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new DOMException("full", "QuotaExceededError");
  });
  try {
    expect(() => remember(sample)).not.toThrow();
    expect(recall(sample.video.id, "disabled")).toBeNull();
  } finally {
    denied.mockRestore();
    full.mockRestore();
  }
});
it.each([null, "unexpected", { error: { message: 42 } }])(
  "normalizes incompatible error body %j",
  async (body) => {
    await expect(
      readReview(Response.json(body, { status: 503 })),
    ).rejects.toThrow("The review service is unavailable.");
  },
);
it("does not display unexpected non-JSON server content", async () => {
  await expect(
    readReview(
      new Response("<html>private stack trace</html>", { status: 500 }),
    ),
  ).rejects.toThrow("The review service returned an unreadable response.");
});
