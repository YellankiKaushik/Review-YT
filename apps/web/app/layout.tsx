import type { Metadata } from "next";
import Link from "next/link";
import "./style.css";
export const metadata: Metadata = {
  title: "Review-YT | Read the room",
  description:
    "A transparent, sampled view of YouTube feedback, with optional AI research notes.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a className="skip" href="#content">
          Skip to content
        </a>
        <div className="shell">
          <header className="masthead">
            <Link className="wordmark" href="/" aria-label="Review-YT home">
              <span className="brand-symbol" aria-hidden="true">
                r/
              </span>
              review<span className="brand-youtube">yt</span>
            </Link>
            <span className="masthead-note">
              Audience research, with receipts.
            </span>
            <span className="edition">INDEPENDENT EDITION / 01</span>
          </header>
          {children}
          <footer>
            <span>Review-YT · A sample, never the whole audience.</span>
            <span>Real source data. Clearly attributed AI.</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
