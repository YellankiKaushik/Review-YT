# Final source-only open-source handoff

Date: 2026-10-22 (Asia/Calcutta). **Local source-only verification PASS; reviewed GitHub publication is the remaining execution step.**

## A. Project
Review-YT — https://github.com/YellankiKaushik/Review-YT, a self-hostable YouTube sentiment application.

## B. Starting main
3a5ec0ee60942b9577777f751a618e87b63a77dc, clean and synchronized at entry.

## C. Final main
Pending normal reviewed publication and CI.

## D. Branches
Temporary codex/source-only-release; main remains persistent. Final cleanup pending merge.

## E. GitHub Actions
Previous main CI passed; no new CI result claimed until publication.

## F. Architecture
Browser → Next frontend/server relay → authenticated Flask/Waitress → independent core/YouTube/VADER; optional AI and SQLite temporary caches. No architecture rebuild or cloud resource changes.

## G. License
MIT remains limited to eligible new source. Existing maintainer decision and provenance limits remain disclosed; third-party/runtime material retains its own terms.

## H. Notices
All 502 third-party legal texts remain byte-identical to the starting workspace. No historical implementation was opened or imported.

## I. README
Source-only status, own-key quick start, provider-neutral architecture, manifest-derived stack, current documentation, privacy, limitations and maintenance statement. No active retired-demo destinations.

## J. Images
Three curated PNGs and original SVG preserved byte-for-byte. Result screenshots retain explicit illustrative DEMO-data disclosure.

## K. Beginner setup
[Getting started](docs/GETTING_STARTED.md): versions, clone, venv, dependencies, own key/token, private files, Windows/POSIX commands, results and safe stop.

## L. Google Cloud
[YouTube setup](docs/YOUTUBE_API_SETUP.md): own project/key, official API, backend-appropriate restrictions, quotas, restart and actual error behavior. No revoked key is used.

## M. Configuration
[Configuration](docs/CONFIGURATION.md): actual source variables/defaults, consumers, secret placement, precedence, allowlists and verification-only controls. Templates retain empty keys, paid/fallback false and sentiment-only defaults.

## N. Self-hosting
[Self-hosting](docs/SELF_HOSTING.md), Render/Vercel guides: own fork/accounts/domains, actual root/build/start settings, matching private token, HTTPS and free-host limitations. No instance provisioned or guaranteed.

## O. Optional AI
[Providers](docs/OPTIONAL_AI_PROVIDERS.md): all six modes, offline versus prior-live evidence, account/cost/model limits. No live model request or weight download.

## P. Troubleshooting
[Guide](docs/TROUBLESHOOTING.md) covers installation/authentication/YouTube/storage/provider/hosting failures according to source.

## Q. Contributors
Updated contribution policy, bug/feature forms and PR template; no request for keys or private comment text; no support-time promise.

## R. Security
Server-only keys, matching backend tokens, production HTTPS/public-bind checks preserved. Added reachable-history scanning and cross-platform source-inventory validation, plus retired-link guard.

## S. Hosting retirement
The owner reports deleting the original Render/Vercel services, dedicated Google project/YouTube key and OpenRouter key. Codex did not delete or recreate cloud resources or probe retired URLs. Historical deployment report archived with retirement context.

## T. Local cleanup
Verified project-only ownership/ignore status, stopped only recorded project services and removed root .env and apps/web/.env.local. Removed 127 old ignored runtime/config/build/log/export targets in this workspace. Examples/assets/notices/dependencies preserved. No system/user environment changes or cryptographic secure-erase claim. Before deletion, 485 reachable Git blobs were scanned against project-private values and recognized prefixes: zero matches. An unrelated inherited provider variable is excluded only from verification child processes, never changed globally.

## U. Offline tests
Fresh execution passed **231 tests: 138 Python/Flask/core/tooling, 51 frontend, 42 browser** in both the working checkout and isolated tracked-source export. The extra regression checks substantive source tampering versus normal checkout newline conversion. No prior tests were removed. Explicit no-key Flask smoke: health200, authenticated inventory200, real analysis503/youtube_not_configured; external exchange forbidden, zero network calls and no demo fallback.

## V. Builds
Fresh optimized Next production build and independent core wheel/sdist builds passed in both environments. All 15 aggregate stages passed. Windows execution used Python3.12.14, Node24.16.0 and npm11.9.0; Ubuntu CI pins Python3.12.15/Node24. No application/backend/core/dependency implementation was changed.

## W. Audits
npm audit --audit-level=high: exit0 / zero vulnerabilities. pip_audit --skip-editable: exit0 / no known vulnerabilities in the installed environment; pip check passed. Both working and clean-source verification passed their audits. These are actual advisory checks, not an all-future-vulnerabilities guarantee.

## X. Secret/link/inventory checks
Working checkout and clean export passed source/browser-artifact secret checks, documentation links and source inventory. No unexpected private env files or prohibited artifacts were found. Empty-secret examples validated. History scanning in the clean export has zero reachable commits by design; the real repository history was separately scanned before cleanup. GitHub CI uses fetch-depth0 for real reachable-history coverage. Recognized-prefix/exact-value scans are not comprehensive security certification.

## Y. Fresh-clone check
**PASS.** Exported only Git-index tracked source to .work/source-only-fresh. No .env/.env.local, node_modules, .venv, SQLite, cache or browser profile was copied. Created a new venv, installed requirements-dev.txt, ran root npm ci, imported core/Flask/Waitress, then passed every stage of scripts/verify.py, including 231 offline tests, both builds, audits, links and inventory. A preinstalled Playwright Chromium executable was reused with fresh temporary browser contexts; no personal profile was copied. Dependencies required registry access. Windows commands were executed; Linux results will be attributed only to actual GitHub Actions. Final report-only text changes do not alter the verified runtime/tooling/dependency tree.

## Z. Limits and verdict
Technical source-only handoff checks PASS locally; publication/CI will be recorded only after observed. Each operator needs their own YouTube key and manages quotas, provider availability, costs, storage and updates. VADER/sampling/AI/captions and ephemeral-cache limitations remain. No hosted service or guaranteed ongoing support is offered. No live analysis is claimed after the owner's credential revocation.
