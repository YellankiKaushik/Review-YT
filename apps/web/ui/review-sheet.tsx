import Image from "next/image";
import type { Review } from "@/lib/contract";
const noticeNames: Record<string, string> = {
  comments_disabled: "Comments are turned off for this video.",
  comments_empty: "YouTube returned no public comments.",
  captions_unavailable: "Public captions were not available.",
};
const labels = ["positive", "neutral", "negative"] as const;
export function ReviewSheet({ review: r }: { review: Review }) {
  const p = r.sentiment.shares;
  const titles = {
    commentDigest: "What viewers are saying",
    creatorNotes: "Notes for the creator",
    captionDigest: "From the captions",
  };
  return (
    <div className="review-sheet">
      <section className="video-card">
        <Image
          unoptimized
          loading="eager"
          src={r.video.thumbnail}
          alt={`Thumbnail for ${r.video.title}`}
          width={320}
          height={180}
        />
        <div className="video-overview">
          <span className="eyebrow">VIDEO / {r.video.channel}</span>
          <h1>{r.video.title}</h1>
          <a
            href={`https://www.youtube.com/watch?v=${r.video.id}`}
            target="_blank"
            rel="noreferrer"
          >
            Open source video ↗
          </a>
        </div>
        <span className="pill">
          {r.caching.reused ? "Saved review" : "Fresh sample"}
        </span>
      </section>
      <dl className="metrics-grid" aria-label="Analysis overview">
        <div className="metric">
          <dt>Comments analyzed</dt>
          <dd>{r.sampled}</dd>
        </div>
        <div className="metric">
          <dt>Positive share</dt>
          <dd>{r.sampled ? `${p.positive.toFixed(1)}%` : "Not available"}</dd>
        </div>
        <div className="metric">
          <dt>Sentiment method</dt>
          <dd className="metric-text">
            {r.sentiment.classifier.split(" · ")[0]}
          </dd>
        </div>
        <div className="metric">
          <dt>AI research notes</dt>
          <dd className="metric-text">
            {r.ai.status === "complete"
              ? "Ready"
              : r.ai.status === "disabled"
                ? "Not requested"
                : "Unavailable"}
          </dd>
        </div>
      </dl>
      <div className="review-columns">
        <section className="sentiment-card" aria-labelledby="chart-title">
          <div className="section-top">
            <h2 id="chart-title">The comment spectrum</h2>
            <span>{r.sampled} analyzed</span>
          </div>
          {r.sampled ? (
            <div className="spectrum">
              <div
                className="ring"
                role="img"
                aria-label={`Sample sentiment: ${p.positive}% positive, ${p.neutral}% neutral, ${p.negative}% negative`}
                style={{
                  background: `conic-gradient(var(--positive) 0 ${p.positive}%, var(--neutral) ${p.positive}% ${p.positive + p.neutral}%, var(--negative) ${p.positive + p.neutral}% 100%)`,
                }}
              >
                <div>
                  <strong>{r.sampled}</strong>
                  <span>comments</span>
                </div>
              </div>
              <dl>
                {labels.map((label) => (
                  <div className={`sentiment-line ${label}`} key={label}>
                    <dt>
                      <i aria-hidden="true" />
                      {label}
                    </dt>
                    <dd>
                      <strong>{p[label].toFixed(1)}%</strong>
                      <span>{r.sentiment.totals[label]} comments</span>
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          ) : (
            <p className="empty-sample">
              No public comments were returned. No sentiment was invented.
            </p>
          )}
          <p className="method">
            <strong>Classification method</strong>
            <br />
            {r.sentiment.classifier}
          </p>
        </section>
        <section className="source-card">
          <span className="eyebrow">HOW TO READ THIS</span>
          <h2>Evidence before interpretation.</h2>
          <p>
            The chart describes {r.sampled} retrieved comments, not every
            viewer. Neutral means the lexicon found no strong positive or
            negative signal.
          </p>
          <p>
            AI research notes are separate from these counts. When a provider
            cannot respond, the sentiment remains usable.
          </p>
          <details open={r.warnings.length > 0}>
            <summary>Source & sample notices</summary>
            {r.warnings.length === 0 ? (
              <p>No additional source notices.</p>
            ) : null}
            <ul>
              {r.warnings.map((w, i) => (
                <li key={i}>{noticeNames[w] || w}</li>
              ))}
            </ul>
          </details>
        </section>
      </div>
      <section className="attribution" aria-label="Research note attribution">
        <div>
          <span className="eyebrow">OPTIONAL RESEARCH NOTES</span>
          <h2>
            {r.ai.status === "complete"
              ? "The model’s reading"
              : r.ai.status === "disabled"
                ? "Sentiment-only review"
                : "Notes are unavailable"}
          </h2>
        </div>
        <div>
          <p>
            <strong>{r.ai.provider}</strong> ·{" "}
            {r.ai.actualModel || r.ai.requestedModel || "No model"} ·{" "}
            {r.ai.execution}
          </p>
          <p className="hint">
            {r.ai.attempts} attempts · {(r.ai.elapsedMs / 1000).toFixed(1)}s
            inference ·{" "}
            {Object.entries(r.ai.usage)
              .map(([k, v]) => `${k}: ${v}`)
              .join(" / ") || "No usage reported"}
          </p>
          {r.ai.actualModel && r.ai.actualModel !== r.ai.requestedModel ? (
            <p className="hint">Requested: {r.ai.requestedModel}</p>
          ) : null}
        </div>
      </section>
      {r.ai.notice ? (
        <p role="status" className="notice">
          {r.ai.notice.message}
        </p>
      ) : null}
      <div className="notes-grid">
        {(Object.keys(titles) as Array<keyof typeof titles>).map((key) => (
          <article className="note-card" key={key}>
            <span className="note-marker" aria-hidden="true">
              ✳
            </span>
            <h2>{titles[key]}</h2>
            <p>
              {r.ai.sections[key] ||
                (r.ai.status === "disabled"
                  ? "AI notes were not requested. Choose an available model to generate a separate interpretation."
                  : key === "captionDigest"
                    ? "No completed caption note is available."
                    : "No completed AI note was returned. The sentiment analysis above remains available.")}
            </p>
          </article>
        ))}
      </div>
      <p className="retention">
        Created{" "}
        {new Date(r.created).toLocaleString("en-GB", { timeZone: "UTC" })} UTC ·
        Cached until{" "}
        {new Date(r.caching.validUntil).toLocaleString("en-GB", {
          timeZone: "UTC",
        })}{" "}
        UTC. Cache availability is temporary.
      </p>
    </div>
  );
}
