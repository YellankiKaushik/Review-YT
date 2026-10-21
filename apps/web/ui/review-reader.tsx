"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { recall, remember } from "@/lib/tab-cache";
import {
  readReview,
  requestErrorMessage,
  type ProviderId,
  type Review,
} from "@/lib/contract";
import { ReviewSheet } from "./review-sheet";
export function ReviewReader({
  video,
  provider,
}: {
  video: string;
  provider: ProviderId;
}) {
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState<{
    identity: string;
    message: string;
  } | null>(null);
  const identity = video + ":" + provider;
  const currentError = error?.identity === identity ? error.message : "";
  const currentReview =
    !currentError &&
    review?.video.id === video &&
    review.ai.provider === provider
      ? review
      : null;
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const deadline = setTimeout(
      () =>
        controller.abort(
          new DOMException("Review request timed out.", "TimeoutError"),
        ),
      120000,
    );
    async function load() {
      try {
        const stored = recall(video, provider);
        const result =
          stored ||
          (await readReview(
            await fetch(
              `/api/results?video=${encodeURIComponent(video)}&provider=${provider}`,
              { signal: controller.signal },
            ),
          ));
        if (result.video.id !== video || result.ai.provider !== provider)
          throw new Error(
            "The saved review did not match the requested video and provider.",
          );
        if (active) {
          remember(result);
          setReview(result);
          setError(null);
        }
      } catch (error) {
        if (active)
          setError({
            identity: video + ":" + provider,
            message: requestErrorMessage(
              error,
              "Could not retrieve this saved review.",
            ),
          });
      } finally {
        clearTimeout(deadline);
      }
    }
    void load();
    return () => {
      active = false;
      clearTimeout(deadline);
      controller.abort();
    };
  }, [video, provider, retry]);
  return (
    <>
      <nav className="review-nav" aria-label="Review navigation">
        <Link href="/">← New review</Link>
        <span>YOUR AUDIENCE NOTEBOOK</span>
      </nav>
      {currentReview ? (
        <ReviewSheet review={currentReview} />
      ) : currentError ? (
        <section className="empty-card" role="alert">
          <span className="eyebrow">REVIEW UNAVAILABLE</span>
          <h1>This page has no saved review.</h1>
          <p>{currentError}</p>
          <p>
            Free hosting may restart and clear its cache. A new review can
            retrieve a fresh sample.
          </p>
          <button
            onClick={() => {
              setError(null);
              setRetry((n) => n + 1);
            }}
          >
            Check saved review again
          </button>
          <Link href="/">Start a new review →</Link>
        </section>
      ) : (
        <section role="status" className="empty-card">
          <h1>Opening your notebook…</h1>
          <p>
            Checking for a saved result. This does not start a new analysis.
          </p>
        </section>
      )}
    </>
  );
}
