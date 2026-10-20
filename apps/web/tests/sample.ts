import type { Review, Inventory } from "../lib/contract";
export const sample: Review = {
  schema: "review-yt/v1",
  video: {
    id: "aB3_dE5-fG7",
    title: "Independent test evidence",
    channel: "Offline fixture",
    published: null,
    thumbnail: "https://i.ytimg.com/vi/aB3_dE5-fG7/hqdefault.jpg",
  },
  sampled: 4,
  sentiment: {
    totals: { positive: 2, neutral: 1, negative: 1 },
    shares: { positive: 50, neutral: 25, negative: 25 },
    classifier: "VADER 3.3.2 · English lexicon rules",
  },
  ai: {
    status: "disabled",
    provider: "disabled",
    requestedModel: "",
    actualModel: null,
    execution: "disabled",
    elapsedMs: 0,
    usage: {},
    sections: {},
    notice: null,
    revision: "test-only",
    attempts: 0,
  },
  sourceDigest: "fixture-only",
  warnings: ["Offline test evidence, not a real YouTube result."],
  created: "2026-01-01T00:00:00Z",
  caching: { reused: false, validUntil: "2099-01-01T00:00:00Z" },
};
export const inventory: Inventory = {
  selectionDefault: "disabled",
  options: [
    {
      id: "disabled",
      configured: true,
      model: "",
      execution: "none",
      description: "No AI requests.",
    },
    {
      id: "ollama",
      configured: true,
      model: "test-local",
      execution: "local",
      description: "Offline test model.",
    },
    {
      id: "openrouter",
      configured: true,
      model: "fixture/free",
      execution: "cloud",
      description: "Offline free-provider stub.",
    },
  ],
  constraints: { paid: false, automaticFallback: false },
};
