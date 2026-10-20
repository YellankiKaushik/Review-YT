"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { recall, remember } from "@/lib/tab-cache";
import { readReview, type ProviderId, type Review } from "@/lib/contract";
import { ReviewSheet } from "./review-sheet";
export function ReviewReader({
  video,
  provider,
}: {
  video: string;
  provider: ProviderId;
}) {
  const [review, setReview] = useState<Review | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
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
        if (active) {
          remember(result);
          setReview(result);
          setError("");
        }
      } catch (error) {
        if (active)
          setError(
            error instanceof Error
              ? error.message
              : "Could not retrieve this saved review.",
          );
      }
    }
    void load();
    return () => {
      active = false;
      controller.abort();
    };
  }, [video, provider, retry]);
  return (
    <>
      <nav className="review-nav" aria-label="Review navigation">
        <Link href="/">← New review</Link>
        <span>YOUR AUDIENCE NOTEBOOK</span>
      </nav>
      {review ? (
        <ReviewSheet review={review} />
      ) : error ? (
        <section className="empty-card" role="alert">
          <span className="eyebrow">REVIEW UNAVAILABLE</span>
          <h1>This page has no saved review.</h1>
          <p>{error}</p>
          <p>
            Free hosting may restart and clear its cache. A new review can
            retrieve a fresh sample.
          </p>
          <button onClick={() => setRetry((n) => n + 1)}>
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
