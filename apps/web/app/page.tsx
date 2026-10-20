import { ReviewForm } from "@/ui/review-form";
export default function Home() {
  return (
    <main id="content">
      <section className="intro">
        <div className="intro-copy">
          <span className="eyebrow">
            <i /> THE AUDIENCE NOTEBOOK
          </span>
          <h1>
            Read the room.
            <br />
            <em>Find the signal.</em>
          </h1>
          <p className="lead">
            Turn a public YouTube video into a clear picture of its comment
            sample. See the sentiment. Read the feedback. Keep the evidence in
            view.
          </p>
          <div className="principles">
            <span>01 / Real comments</span>
            <span>02 / Transparent methods</span>
            <span>03 / Optional AI</span>
          </div>
        </div>
        <ReviewForm />
      </section>
      <section className="explain" aria-labelledby="explain-title">
        <div>
          <span className="eyebrow">A SHORTER PATH TO UNDERSTANDING</span>
          <h2 id="explain-title">A review you can trace.</h2>
        </div>
        <article>
          <span className="step-number">01</span>
          <h3>Choose your sample</h3>
          <p>
            Start with ten public comments, or explore a larger selection. The
            actual retrieved count is always shown.
          </p>
        </article>
        <article>
          <span className="step-number">02</span>
          <h3>Separate signal from opinion</h3>
          <p>
            The sentiment chart uses a language lexicon. AI interpretation is
            optional and identified separately.
          </p>
        </article>
        <article>
          <span className="step-number">03</span>
          <h3>Return to the evidence</h3>
          <p>
            Saved reviews are available while cached. If a model is unavailable,
            the comment analysis still stands.
          </p>
        </article>
      </section>
      <aside className="sample-note">
        <strong>A sample is a perspective.</strong>
        <span>
          Comment ordering, language and sarcasm affect the result. Treat
          suggestions as hypotheses to check, not audience consensus.
        </span>
      </aside>
    </main>
  );
}
