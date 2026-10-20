import { z } from "zod";
export const providerIds = [
  "disabled",
  "ollama",
  "openrouter",
  "openai",
  "gemini",
  "groq",
] as const;
export type ProviderId = (typeof providerIds)[number];
const count = z.number().int().nonnegative();
const threeCounts = z.object({
  positive: count,
  neutral: count,
  negative: count,
});
const threeShares = z.object({
  positive: z.number().min(0).max(100),
  neutral: z.number().min(0).max(100),
  negative: z.number().min(0).max(100),
});
export const inventorySchema = z.object({
  selectionDefault: z.enum(providerIds),
  options: z.array(
    z.object({
      id: z.enum(providerIds),
      configured: z.boolean(),
      model: z.string(),
      execution: z.string(),
      description: z.string(),
    }),
  ),
  constraints: z.object({ paid: z.boolean(), automaticFallback: z.boolean() }),
});
export const reviewSchema = z
  .object({
    schema: z.literal("review-yt/v1"),
    video: z.object({
      id: z.string().regex(/^[A-Za-z0-9_-]{11}$/),
      title: z.string(),
      channel: z.string(),
      published: z.string().nullable(),
      thumbnail: z.url(),
    }),
    sampled: count,
    sentiment: z.object({
      totals: threeCounts,
      shares: threeShares,
      classifier: z.string(),
    }),
    ai: z.object({
      status: z.enum(["disabled", "unavailable", "complete"]),
      provider: z.enum(providerIds),
      requestedModel: z.string(),
      actualModel: z.string().nullable(),
      execution: z.string(),
      elapsedMs: count,
      usage: z.record(z.string(), z.number().nonnegative()),
      sections: z.record(z.string(), z.string()),
      notice: z.object({ code: z.string(), message: z.string() }).nullable(),
      revision: z.string(),
      attempts: count,
    }),
    sourceDigest: z.string(),
    warnings: z.array(z.string()),
    created: z.string(),
    caching: z.object({ reused: z.boolean(), validUntil: z.string() }),
  })
  .superRefine((review, ctx) => {
    const total = Object.values(review.sentiment.totals).reduce(
      (a, b) => a + b,
      0,
    );
    if (total !== review.sampled)
      ctx.addIssue({
        code: "custom",
        message: "Comment totals do not match the sample",
      });
    for (const key of ["positive", "neutral", "negative"] as const)
      if (
        Math.abs(
          review.sentiment.shares[key] -
            (review.sampled
              ? (review.sentiment.totals[key] / review.sampled) * 100
              : 0),
        ) > 0.02
      )
        ctx.addIssue({
          code: "custom",
          message: "Sentiment percentages do not match counts",
        });
  });
export type Review = z.infer<typeof reviewSchema>;
export type Inventory = z.infer<typeof inventorySchema>;
export async function readReview(response: Response): Promise<Review> {
  const body = await response.json();
  if (!response.ok)
    throw new Error(
      body.error?.message || "The review service is unavailable.",
    );
  const parsed = reviewSchema.safeParse(body);
  if (!parsed.success)
    throw new Error("The review service returned an incompatible result.");
  return parsed.data;
}
