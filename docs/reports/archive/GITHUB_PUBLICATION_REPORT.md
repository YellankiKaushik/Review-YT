# GitHub publication report

Recorded 2026-10-21 (Asia/Calcutta). Workspace: Review-YT-clean. Starting commit: `beecdb6c5c71a3438728e53d8110f71bec25919f`, branch `main`.

## Actual maintainer decision and license changes

The maintainer reviewed the source inventory/audit/notices, declared sufficient rights to publish eligible new material to the best of their knowledge subject to documented exceptions, approved retaining third-party notices and authorized publication to https://github.com/YellankiKaushik/Review-YT. The license line initially remained a literal placeholder; a necessary clarification received the explicit answer **MIT**. The declaration and follow-up are recorded accurately in docs/FINAL_PUBLICATION_RIGHTS_CHECKLIST.md.

Root and independent core LICENSE now contain MIT. Root/web package.json, corresponding lock metadata and core pyproject.toml identify MIT. Root/core NOTICE files limit this grant to eligible new material and preserve third-party and runtime-data rights. Package uploads are not part of this release. All 502 retained upstream legal texts remain unchanged. No contributor work was reassigned or historical Git history imported.

The existing reviewed new tree identifies no concrete copied unlicensed expression. Prior context exposure remains disclosed uncertainty, not a legal certification. A new declaration does not override third-party rights or cure a concrete infringement. Source-only publication does not distribute installed native binaries; target-platform distribution duties remain separate.

## Prepublication evidence

Before release edits: all 601 source-inventory hashes matched; 602 tracked files; all 502 retained dependency legal texts matched the clean starting commit. Root .env, web .env.local, cache, TLS keys, node_modules, .venv, artifacts and Next build output were excluded. Fresh Git root: `d6af6815c4d0cce14d018892c63e78c16518319b`; nine existing genuine commits; no remote configured. Read-only GitHub API returned HTTP 200/public/size 0, branches [], and zero Actions runs. git ls-remote returned no refs. The configured credential helper has not yet been exercised for a push.

## Final release verification

**All 13 release stages passed freshly: 195 automated tests = 137 Python + 44 frontend + 14 browser.** Executed `.venv/Scripts/python.exe scripts/verify.py`; no application implementation was changed by this license/publication task. Browser tests use explicitly injected fixtures, not new live YouTube or cloud inference. Prior real-source evidence remains in the dated production-readiness report; it is not presented as a new live request. No new provider generation call was made.

| Command | Actual outcome | Seconds |
| --- | --- | --- |
| `python -m ruff check packages apps tests scripts` | exit 0; passed | 1.16 |
| `python -m pytest -q` | exit 0; 137 passed | 2.86 |
| `npm run lint` | exit 0; passed | 25.48 |
| `npm run typecheck` | exit 0; passed | 3.64 |
| `npm test` | exit 0; 44 passed | 25.11 |
| `npm run build` | exit 0; production build passed | 29.06 |
| `python -m build packages/review_yt_core --outdir artifacts/package` | exit 0; wheel and sdist built | 14.52 |
| `npm run test:e2e` | exit 0; 14 passed (desktop/mobile) | 35.19 |
| `python -m pip check` | exit 0; no broken requirements | 1.36 |
| `npm audit --audit-level=high` | exit 0; 0 vulnerabilities | 8.44 |
| `python -m pip_audit --skip-editable -f json -o artifacts/pip-audit-final.json` | exit 0; no known vulnerabilities (editable own package excluded) | 13.05 |
| `python scripts/check_release_config.py` | exit 0; passed | 0.11 |
| `python scripts/secret_check.py` | exit 0; 0 credential/security findings | 0.33 |

Exact command records and logs are retained privately in ignored `artifacts/verification/results.json` and 01.log through 13.log. The freshly rebuilt wheel metadata contains `License-Expression: MIT`, both LICENSE and NOTICE; the source archive includes NOTICE. Core metadata has no Flask dependency. Canonical license terms were checked against the [Open Source Initiative MIT text](https://opensource.org/license/mit).

Project secret scan: 605 source/report/notice files, 25 browser artifacts, 27 application logs, 4 configured private values; zero matches, unexpected environment files, prohibited artifacts or public secret variables. Supplemental precommit history scan: 420 reachable blobs, zero exact-credential/recognized-prefix findings and zero private/runtime paths. This bounded scanner is not a complete security certification. All 502 retained legal files are byte-identical to the clean baseline. The dependency graph/versions are unchanged; lockfile changes apply only project license fields.

## Publication execution

**PUBLISHED AND CI VERIFIED.** The existing destination was immediately rechecked empty with `git ls-remote` before adding `origin`. The existing Git credential manager authenticated noninteractively as the maintainer; author email `kaushikyellanki@gmail.com` matched the connected GitHub account. No email-verified status is asserted. Dry-run passed, then `git push -u origin main` completed normally. No force-push, history rewrite, tag, synthetic source commit or package upload occurred.

- Repository: [YellankiKaushik/Review-YT](https://github.com/YellankiKaushik/Review-YT), public, default branch main; GitHub detects **MIT**.
- Verified release commit: [`99950321ff6f51bb519c2e5c700bb7c058b011e5`](https://github.com/YellankiKaushik/Review-YT/commit/99950321ff6f51bb519c2e5c700bb7c058b011e5).
- Git remote refs and GitHub branch API matched local HEAD exactly at release publication. Verified root tree: `4405c87e815ca00b480feb1cd7c56af30da93061`; API returned 605 files, untruncated, including all 502 retained upstream legal texts, with no private/runtime paths.
- Anonymous HTTPS retrieval of the commit-pinned root LICENSE returned **HTTP 200**, byte-identical to the committed MIT text. Postcommit history scan covered **437 reachable blobs**, with zero credential findings. All 604 current inventory records matched (the manifest excludes itself).
- Actual [GitHub Actions run 39614998251](https://github.com/YellankiKaushik/Review-YT/actions/runs/39614998251), push event, attempt 1, release SHA above: **completed / success**. Ubuntu job 119273546960 took **144 seconds**, from 14:13:45Z to 14:16:09Z on 2026-10-21.

### Actual Linux CI evidence

Decoded job logs confirm **137 Python tests passed (1.09 s), 44 frontend tests passed (2.21 s), and 14 browser tests passed (44.3 s)**: 195 total, separately from the local Windows results. Ruff, frontend lint/types, production Next build, independent wheel/sdist build, npm audit, Python audit, release-configuration check and secret scan all passed. npm reported zero vulnerabilities; Python reported no known vulnerabilities. CI scanned 605 source files and 23 browser artifacts with zero findings; it had no configured private application credentials, so the separate local scan against real private values remains relevant. Tests used injected fixtures, not live account quotas.

This report is an evidence follow-up to the tested release commit. A subsequent documentation-only commit records these already verified results and refreshed source hashes. It does not change the implementation, dependencies or license grant. The final documentation commit is checked/pushed normally and its latest Actions result can be inspected on [the main workflow page](https://github.com/YellankiKaushik/Review-YT/actions/workflows/verify.yml?query=branch%3Amain). The tested release SHA and immutable run above remain the reproducible publication evidence; no self-referential commit SHA or unobserved future success is fabricated here.

The initial Git wrapper set `GIT_CURL_VERBOSE=0`; Git treated the variable's presence as enabling transport diagnostics. Follow-up subprocesses removed trace/verbose variables and explicitly kept authentication redaction enabled, with output restricted to safe status/SHA evidence. No application credential was placed in a Git URL, command or committed file. Private environment files were not modified.

## Remaining limits and maintainer actions

There is no identified included-source rights blocker in the reviewed source-only tree after the recorded maintainer decision. Prior-context exposure and third-party rights remain disclosed; new concrete evidence would need resolution. CI verifies Ubuntu app/package builds, not a legal audit of future native binary/container redistribution. Preserve applicable target-platform dependency notices/source/relinking duties if that distribution scope changes.

GitHub source publication is complete. **Public application deployment is not performed in this task.** The maintainer's explicit instruction reserves Render/Vercel creation and production secret entry to the maintainer:

1. Create only an eligible free Review-YT Render service using docs/RENDER_DEPLOYMENT_HANDOFF.md and render.yaml. Enter the YouTube key and a new private backend token through Render settings. Keep sentiment-only baseline, paid inference/fallback false and no public laptop Ollama dependency.
2. Verify the actual Render HTTPS health endpoint, then create the Review-YT Vercel project with apps/web as its root using docs/VERCEL_DEPLOYMENT_HANDOFF.md. Configure server-only BACKEND_URL and the matching BACKEND_API_TOKEN through hosting settings. Never use NEXT_PUBLIC secrets.
3. Follow docs/ENVIRONMENT_VARIABLES_CHECKLIST.md. Once genuine public HTTPS origins exist, run scripts/check-public.ps1 with the actual frontend/backend origins. The optional -LiveVideo and -Browser flags explicitly enable the bounded ten-comment desktop/mobile/cache verification. No public end-to-end or hosting success is claimed before those real checks.

No additional hosting authentication, user credential entry, paid authorization or public app URL was supplied or invented by this publication task. Those are manual deployment prerequisites, not a remaining GitHub publication failure.
