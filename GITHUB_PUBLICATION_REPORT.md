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

READY FOR SAFE PUSH. The MIT-scoped release passed local checks and no concrete included-source rights blocker is identified. Final inventory/whitespace/secret checks, local release commit, immediate destination recheck, noninteractive credential-manager dry-run and normal push are next. No remote commit or Actions success is claimed yet. An authentication/permission failure must be documented rather than bypassed. No force-push, history rewrite or artificial contributions.


## Hosting boundary

No Render or Vercel resources will be created by this task. The maintainer creates eligible free projects and enters production environment variables using docs/RENDER_DEPLOYMENT_HANDOFF.md, docs/VERCEL_DEPLOYMENT_HANDOFF.md and docs/ENVIRONMENT_VARIABLES_CHECKLIST.md after source publication. No paid hosting/inference is authorized. No public app URL is claimed.
