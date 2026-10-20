import { describe, it, expect } from "vitest";
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
