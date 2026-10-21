import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/ui/icon";
import "./style.css";
export const metadata: Metadata = {
  title: "Review-YT | Understand the comments",
  description:
    "Explore real public YouTube comments with transparent sentiment analysis and optional, clearly attributed AI research notes.",
};
const repo = "https://github.com/YellankiKaushik/Review-YT";
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <body>
        <a className="skip" href="#content">
          Skip to content
        </a>
        <div className="shell">
          <header className="masthead">
            <Link className="wordmark" href="/" aria-label="Review-YT home">
              <span className="brand-symbol">
                <Icon name="play" />
              </span>
              Review<span className="brand-youtube">-YT</span>
            </Link>
            <nav className="main-nav" aria-label="Main navigation">
              <Link href="/#how-it-works">How it works</Link>
              <Link href="/#methods">Our approach</Link>
              <a className="nav-repo" href={repo}>
                GitHub <span aria-hidden="true">↗</span>
              </a>
            </nav>
          </header>
          {children}
          <footer className="site-footer">
            <div>
              <strong>Review-YT</strong>
              <p>
                A clearer view of a comment sample.
                <br />
                Always a sample. Never the whole audience.
              </p>
            </div>
            <nav aria-label="Project links">
              <a href={repo}>GitHub repository ↗</a>
              <a href={`${repo}/blob/main/docs/README.md`}>Documentation ↗</a>
              <a href={`${repo}/blob/main/LICENSE`}>MIT license ↗</a>
            </nav>
            <p className="footer-note">
              Real source data.
              <br />
              Transparent methods.
              <br />
              AI only when you choose it.
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}
