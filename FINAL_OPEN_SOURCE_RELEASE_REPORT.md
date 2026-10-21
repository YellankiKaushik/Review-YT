# Final source-only open-source handoff

Date: 2026-10-22 (Asia/Calcutta). **PASS — verified source-only handoff.** This report is published through [PR #3](https://github.com/YellankiKaushik/Review-YT/pull/3). Copies on an unmerged feature branch are candidates; the linked merge receipt and canonical main identity record actual publication, not a forecast.

## A. Project
Review-YT — https://github.com/YellankiKaushik/Review-YT, a self-hostable YouTube sentiment application.

## B. Starting main
3a5ec0ee60942b9577777f751a618e87b63a77dc, clean and synchronized at entry.

## C. Final main
Canonical final main SHA: [GitHub resolved main commit](https://api.github.com/repos/YellankiKaushik/Review-YT/commits/main), also recorded literally in the [PR #3 final publication receipt](https://github.com/YellankiKaushik/Review-YT/pull/3) and final handoff response after merge. Immutable verified implementation candidate: `a60708543eb2a951e5ee59bf7d9109e3174ab4bb`. A report cannot embed the SHA of its own containing commit without self-reference; the merge receipt supplies the actual full SHA without artificial follow-up commits.

## D. Branches
`main` is the sole persistent branch. The release uses temporary `codex/source-only-release`, deleted only after normal merge and zero-unique-commit ancestry verification. The final remote/local cleanup receipt is in PR #3; [GitHub branch inventory](https://api.github.com/repos/YellankiKaushik/Review-YT/branches) is the authoritative current state. No existing history, author/date or prior PR is rewritten.

## E. GitHub Actions
Observed Ubuntu candidate CI **completed/success**: [push run 39657665355](https://github.com/YellankiKaushik/Review-YT/actions/runs/39657665355) and [PR run 39657733870](https://github.com/YellankiKaushik/Review-YT/actions/runs/39657733870), exact head `a60708543eb2a951e5ee59bf7d9109e3174ab4bb`. Push job119422123762 had all 23 steps pass; decoded logs confirm 138 Python + 51 frontend + 42 browser, clean audits, docs and inventory. Final evidence-only updates retain exactly the tested runtime/tooling/tests/dependencies; their exact-head CI and final main CI are recorded in the PR publication receipt after observation. No future CI result is invented here.

## F. Architecture
Browser → Next frontend/server relay → authenticated Flask/Waitress → independent core/YouTube/VADER; optional AI and SQLite temporary caches. No architecture rebuild or cloud resource changes.

## G. License
MIT remains limited to eligible new source. Existing maintainer decision and provenance limits remain disclosed; third-party/runtime material retains its own terms.

## H. Notices
All 502 third-party legal texts remain byte-identical to the starting workspace. No historical implementation was opened or imported.

## I. README
Source-only status, own-key quick start, provider-neutral architecture, manifest-derived stack, current documentation, privacy, limitations and maintenance statement. No active retired-demo destinations.

## J. Images
Three curated PNGs and original SVG preserved byte-for-byte. Result screenshots retain explicit illustrative DEMO-data disclosure. Total PNG bytes: 165,877; each remains below the 1.5 MB documentation budget. The SVG illustrates an optional host arrangement; current Mermaid architecture is provider-neutral.

| Preserved asset | Bytes |
| --- | ---: |
| [ review-yt-homepage.png ](docs/assets/review-yt-homepage.png) | 30213 |
| [ review-yt-results.png ](docs/assets/review-yt-results.png) | 64353 |
| [ review-yt-mobile.png ](docs/assets/review-yt-mobile.png) | 71311 |
| [ review-yt-architecture.svg ](docs/assets/review-yt-architecture.svg) | 3260 |


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
Fresh execution passed **231 tests: 138 Python/Flask/core/tooling, 51 frontend, 42 browser** in both the working checkout and isolated tracked-source export. The extra regression checks substantive source tampering versus normal checkout newline conversion. No prior tests were removed. Explicit no-key Flask smoke: health HTTP 200, authenticated inventory HTTP 200, real analysis HTTP 503 / youtube_not_configured; external exchange forbidden, zero network calls and no demo fallback.

## V. Builds
Fresh optimized Next production build and independent core wheel/sdist builds passed in both environments. All 15 aggregate stages passed. Windows execution used Python 3.12.14, Node.js 24.16.0 and npm 11.9.0; Ubuntu CI pins Python 3.12.15 / Node.js 24. No application/backend/core/dependency implementation was changed.

## W. Audits
npm audit --audit-level=high: exit 0 / zero vulnerabilities. pip_audit --skip-editable: exit 0 / no known vulnerabilities in the installed environment; pip check passed. Both working and clean-source verification passed their audits. These are actual advisory checks, not an all-future-vulnerabilities guarantee.

## X. Secret/link/inventory checks
Working checkout and clean export passed source/browser-artifact secret checks, documentation links and source inventory. No unexpected private env files or prohibited artifacts were found. Empty-secret examples validated. History scanning in the clean export has zero reachable commits by design; the real repository history was separately scanned before cleanup. Actual Ubuntu CI scanned **520 reachable blobs**, 631 source files and 23 browser artifacts: zero matches, zero unexpected env/prohibited/public-secret variables. It validated 37 documents / 142 relative targets and 630 inventory records; 106 normal checkout line-ending conversions were accepted without hiding altered content. CI uses fetch-depth: 0 for real history coverage. Recognized-prefix/exact-value scans are not comprehensive security certification.

## Y. Fresh-clone check
**PASS.** Exported only Git-index tracked source to .work/source-only-fresh. No .env/.env.local, node_modules, .venv, SQLite, cache or browser profile was copied. Created a new venv, installed requirements-dev.txt, ran root npm ci, imported core/Flask/Waitress, then passed every stage of scripts/verify.py, including 231 offline tests, both builds, audits, links and inventory. A preinstalled Playwright Chromium executable was reused with fresh temporary browser contexts; no personal profile was copied. Dependencies required registry access. Windows commands were executed; Linux results will be attributed only to actual GitHub Actions. Final evidence/policy-only text changes do not alter the verified runtime/tooling/dependency tree. The disposable clean export/archive was removed after its processes exited; sanitized verification logs/results remain ignored local evidence.

## Z. Limits and verdict
**COMPLETE for the verified technical source-only handoff.** Public GitHub source remains unarchived, with empty About homepage; normal PR/CI/merge and branch-cleanup receipt provides final publication evidence. No tag/release or package registry upload is required or claimed (package versions remain 0.1.0). Each operator needs their own YouTube key and manages quotas, provider availability, costs, storage and updates. VADER/sampling/AI/captions and ephemeral-cache limitations remain. No hosted service or guaranteed ongoing support is offered. No live analysis is claimed after the owner's credential revocation.


## Acceptance and scope

README/current setup no longer advertise retired services; all six dedicated beginner/operator guides, community files, preserved visuals/notices and safe templates are present. Both Windows working/fresh-source pipelines and actual Linux CI passed. Local obsolete project configuration and prior operational data were removed safely; ordinary deletion is not secure erase. No former service was contacted or restored and no owner-revoked credential was used. New users supply their own keys. Main publication/cleanup is verified by the linked final receipt rather than fabricating a future SHA inside this self-referential file. No genuine technical blocker remains; account/model/plan availability and future hosting configurations are operator responsibilities, not guaranteed services.
