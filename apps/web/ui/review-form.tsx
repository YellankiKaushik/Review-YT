"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  inventorySchema,
  readReview,
  type Inventory,
  type ProviderId,
} from "@/lib/contract";
import { remember } from "@/lib/tab-cache";
const names: Record<ProviderId, string> = {
  disabled: "Sentiment only",
  ollama: "Local Gemma · Ollama",
  openrouter: "OpenRouter · Cloud",
  openai: "OpenAI · Cloud",
  gemini: "Gemini · Cloud",
  groq: "Groq · Cloud",
};
const fallback: Inventory = {
  selectionDefault: "disabled",
  options: [
    {
      id: "disabled",
      configured: true,
      model: "",
      execution: "none",
      description: "No AI calls. Metadata and sentiment remain available.",
    },
  ],
  constraints: { paid: false, automaticFallback: false },
};
export function ReviewForm() {
  const [inventory, setInventory] = useState(fallback);
  const [provider, setProvider] = useState<ProviderId>("disabled");
  const [sample, setSample] = useState("10");
  const [video, setVideo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [ready, setReady] = useState(false);
  const running = useRef(false);
  const router = useRouter();
  useEffect(() => {
    const controller = new AbortController();
    Promise.resolve().then(() => setReady(true));
    fetch("/api/providers", { signal: controller.signal })
      .then((r) => r.json())
      .then((body) => {
        const result = inventorySchema.safeParse(body);
        if (result.success && !controller.signal.aborted) {
          setInventory(result.data);
          setProvider(
            result.data.options.find(
              (p) => p.id === result.data.selectionDefault && p.configured,
            )?.id ??
              result.data.options.find(
                (p) => p.id === "disabled" && p.configured,
              )?.id ??
              result.data.options.find((p) => p.configured)?.id ??
              "disabled",
          );
        }
      })
      .catch(() => {});
    return () => controller.abort();
  }, []);
  const option = inventory.options.find((p) => p.id === provider);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (running.current) return;
    setError("");
    if (!video.trim()) {
      setError("Paste a YouTube video link or ID to begin.");
      return;
    }
    running.current = true;
    setBusy(true);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video, sample: Number(sample), provider }),
        signal: AbortSignal.timeout(120000),
      });
      const review = await readReview(response);
      remember(review);
      router.push(`/review/${review.video.id}?via=${provider}`);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "The analysis could not be completed.",
      );
    } finally {
      running.current = false;
      setBusy(false);
    }
  }
  return (
    <form className="input-card" onSubmit={submit} aria-busy={busy}>
      <div className="card-heading">
        <span className="eyebrow">START A REVIEW</span>
        <span className="round-arrow" aria-hidden="true">
          ↗
        </span>
      </div>
      <h2>One link. A little clarity.</h2>
      <label htmlFor="video">YouTube video</label>
      <input
        id="video"
        value={video}
        onChange={(e) => setVideo(e.target.value)}
        placeholder="Paste a public video link or ID"
        disabled={!ready || busy}
        aria-describedby="video-tip"
      />
      <p id="video-tip" className="hint">
        Watch links, Shorts and youtu.be links are supported.
      </p>
      <div className="form-grid">
        <div>
          <label htmlFor="sample">Comment sample</label>
          <select
            id="sample"
            value={sample}
            onChange={(e) => setSample(e.target.value)}
            disabled={busy}
          >
            {[10, 50, 100, 250, 500].map((n) => (
              <option value={n} key={n}>
                Up to {n}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="provider">Research notes</label>
          <select
            id="provider"
            value={provider}
            onChange={(e) => setProvider(e.target.value as ProviderId)}
            disabled={busy}
          >
            {inventory.options.map((p) => (
              <option key={p.id} value={p.id} disabled={!p.configured}>
                {names[p.id]}
                {p.configured ? "" : " · unavailable"}
              </option>
            ))}
          </select>
        </div>
      </div>
      <p className="provider-help">
        {option?.model ? <strong>{option.model} · </strong> : null}
        {option?.description}
      </p>
      <button
        className="primary"
        disabled={!ready || busy || !option?.configured}
      >
        {busy ? "Preparing your review…" : "Review this video"}
        <span aria-hidden="true">{busy ? "◌" : "→"}</span>
      </button>
      {busy ? (
        <p role="status" className="status">
          Retrieving the sample. Optional model inference can take up to a
          minute.
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}
      <p className="fine">
        No invented feedback. No AI required for sentiment.
      </p>
    </form>
  );
}
