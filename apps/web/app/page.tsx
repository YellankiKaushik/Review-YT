import { ReviewForm } from "@/ui/review-form";
import { Icon } from "@/ui/icon";
const steps = [
  {
    icon: "link",
    title: "Bring a public video",
    text: "Paste a YouTube link or video ID. Choose how many top-level comments to sample, starting with ten.",
  },
  {
    icon: "chart",
    title: "See the comment tone",
    text: "Explore positive, neutral and negative counts, with percentages calculated from the actual retrieved sample.",
  },
  {
    icon: "layers",
    title: "Add context, if you need it",
    text: "Request research notes from an available AI provider. Sentiment stays usable if the model cannot respond.",
  },
] as const;
export default function Home() {
  return (
    <main id="content" tabIndex={-1}>
      <section className="intro" aria-labelledby="hero-title">
        <div className="intro-copy">
          <span className="eyebrow">
            <i /> YOUTUBE COMMENT ANALYTICS
          </span>
          <h1 id="hero-title">
            Understand the feedback.
            <br />
            <em>Keep the evidence.</em>
          </h1>
          <p className="lead">
            A clearer perspective on public YouTube comments. Explore the tone
            of a real sample, see the numbers, and make room for context.
          </p>
          <div className="principles">
            <span>Real public comments</span>
            <span>Transparent sentiment</span>
            <span>Optional AI notes</span>
          </div>
          <p className="hero-footnote">
            For creators, researchers, and anyone curious about the
            conversation.
          </p>
        </div>
        <ReviewForm />
      </section>
      <section
        id="how-it-works"
        className="workflow"
        aria-labelledby="workflow-title"
      >
        <div className="section-heading">
          <div>
            <span className="eyebrow">FROM LINK TO PERSPECTIVE</span>
            <h2 id="workflow-title">Less scrolling. More understanding.</h2>
          </div>
          <p>
            Three simple steps.
            <br />
            The source stays in view.
          </p>
        </div>
        <div className="steps-grid">
          {steps.map((step, i) => (
            <article className="step-card" key={step.title}>
              <div className="step-top">
                <span className="icon-tile">
                  <Icon name={step.icon} />
                </span>
                <span className="step-number">0{i + 1}</span>
              </div>
              <h3>{step.title}</h3>
              <p>{step.text}</p>
            </article>
          ))}
        </div>
      </section>
      <section id="methods" className="methods" aria-labelledby="methods-title">
        <div className="section-heading">
          <div>
            <span className="eyebrow">TWO LAYERS. CLEAR BOUNDARIES.</span>
            <h2 id="methods-title">
              Sentiment is a signal.
              <br />
              Interpretation adds context.
            </h2>
          </div>
        </div>
        <div className="methods-grid">
          <article className="method-card baseline">
            <span className="tag">THE BASELINE</span>
            <h3>Count the tone.</h3>
            <p>
              VADER is an English-language sentiment classifier that estimates
              the tone of a sample of public comments. Its rule-based counts
              power the chart, independently of AI.
            </p>
            <span className="method-detail">
              <Icon name="chart" /> Metadata + counts + percentages
            </span>
          </article>
          <article className="method-card optional">
            <span className="tag">OPTIONAL RESEARCH NOTES</span>
            <h3>Explore the context.</h3>
            <p>
              An available AI provider can summarize feedback, suggest questions
              for the creator, and summarize public captions when enabled. Model
              identity and unavailable states stay visible.
            </p>
            <span className="method-detail">
              <Icon name="layers" /> Separate, attributed interpretation
            </span>
          </article>
        </div>
      </section>
      <section className="capabilities" aria-labelledby="capabilities-title">
        <span className="eyebrow">BUILT FOR AN HONEST REVIEW</span>
        <h2 id="capabilities-title">Useful details. Fewer assumptions.</h2>
        <div className="capabilities-grid">
          <article>
            <Icon name="play" />
            <h3>The original source</h3>
            <p>
              Video metadata and a direct YouTube link accompany each analysis.
            </p>
          </article>
          <article>
            <Icon name="chart" />
            <h3>Numbers you can read</h3>
            <p>
              Actual counts and labeled percentages make the chart
              understandable beyond color.
            </p>
          </article>
          <article>
            <Icon name="clock" />
            <h3>Thoughtful reuse</h3>
            <p>
              Return to a saved result while its temporary cache remains
              available.
            </p>
          </article>
          <article>
            <Icon name="layers" />
            <h3>Graceful recovery</h3>
            <p>
              Clear errors and usable sentiment when optional AI is unavailable.
            </p>
          </article>
        </div>
      </section>
      <aside className="sample-note">
        <span className="note-symbol" aria-hidden="true">
          i
        </span>
        <div>
          <strong>A sample is a perspective.</strong>
          <p>
            Comment order, language and sarcasm affect the result. A comment
            sample does not represent every viewer. AI can make mistakes, and
            free hosting may clear cached results.
          </p>
        </div>
      </aside>
    </main>
  );
}
