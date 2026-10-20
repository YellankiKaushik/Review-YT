import { reviewSchema, type Review, type ProviderId } from "./contract";
const prefix = "review-yt:note:";
export function remember(review: Review) {
  try {
    sessionStorage.setItem(
      prefix + review.video.id + ":" + review.ai.provider,
      JSON.stringify(review),
    );
  } catch {
    /* Storage is optional. */
  }
}
export function recall(video: string, provider: ProviderId): Review | null {
  try {
    const raw = sessionStorage.getItem(prefix + video + ":" + provider);
    if (!raw) return null;
    const result = reviewSchema.safeParse(JSON.parse(raw));
    if (
      result.success &&
      Date.parse(result.data.caching.validUntil) > Date.now() &&
      result.data.video.id === video &&
      result.data.ai.provider === provider
    )
      return result.data;
  } catch {
    /* Invalid tab data is never displayed. */
  }
  return null;
}
