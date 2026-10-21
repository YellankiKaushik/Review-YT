# Product-polish baseline — 2026-10-21

> Historical 2026-10-21 baseline. The owner retired hosting and revoked dedicated keys on 2026-10-22. Listed domains are past evidence, not current services.

Starting local/remote main: fae449dc455e5cf3d867505c97123d7dc37116d2. Worktree clean before creating the requested refactor/review-yt-product-polish branch. No historical source was opened/imported. No production settings or secrets changed.

## Actual GET-only production checks

- https://review-yt.vercel.app — HTTP 200, 94 ms in the first HTTP probe.
- https://review-yt-api.onrender.com/health — HTTP 200, 24,641 ms, status ok, contract review-yt/v1. A single cold/warm measurement is not an uptime guarantee.
- https://review-yt.vercel.app/api/providers — HTTP 200, 1,781 ms; disabled provider only, paid false, automatic fallback false.
- Anonymous Chromium desktop1440 capture: homepage loads without page errors or horizontal overflow; navigation DOMContentLoaded3366.4 ms, load3465.5 ms; script encoded bytes165665. Measurements are one observed network/browser run, not Lighthouse scores or a performance guarantee.
- Existing local aggregate optimized static artifacts: JavaScript1,060,430 bytes, CSS8,501 bytes. Aggregate build output is not per-route first-load transfer.
-502 retained upstream legal files hashed before any edit. Source inventory and original root reports retained for audit.

## Audit findings

Current frontend uses a small server-rendered home/layout with client form/reader, CSS chart and typed contract. Form/reader recovery and provider-specific cache identity are already covered by tests; preserve them. Tiny9–11px text, square notebook surfaces, limited navigation/footer links and weak result hierarchy can be improved without an API or dependency change. CONTRIBUTING/CHANGELOG and current deployment guides contain stale release-gate/not-deployed wording. Root has five long historical reports. Dependencies all have current runtime/build/test roles; no speculative removal is justified. No concrete new source-rights issue identified; MIT scope and third-party exceptions remain in force.

## Proposed removal/move classification

| Item | Classification | Decision |
| --- | --- | --- |
| FINAL_REVIEW_YT_RELEASE_REPORT.md | SAFE move | Retain under docs/reports/archive; repair references; preserve dated evidence. |
| DEPLOYMENT_EXECUTION_REPORT.md | SAFE move | Retain under docs/reports/archive; repair references; preserve dated evidence. |
| FINAL_LIVE_DEPLOYMENT_REPORT.md | SAFE move | Retain under docs/reports/archive; repair references; preserve dated evidence. |
| PRODUCTION_DEPLOYMENT_READINESS_REPORT.md | SAFE move | Retain under docs/reports/archive; repair references; preserve dated evidence. |
| GITHUB_PUBLICATION_REPORT.md | SAFE move | Retain under docs/reports/archive; repair references; preserve dated evidence. |
| Old stylesheet rules | SAFE replacement | Replace rules as the same components receive a coherent visual system; preserve behavior. |
| Runtime/source/cache/test/build artifacts | SAFE exclusion | Keep private/ignored; no recursive cleanup of user data or services. |
| Dependencies/components/configuration | CONDITIONAL | Remove only after actual unused-role proof; no removals currently justified. |
| Third-party legal files, LICENSE/NOTICE, provenance, valid tests | PROHIBITED deletion | Retain complete notices/rights evidence and valid regression coverage. |
| Historical separate application/history | PROHIBITED import/modification | Do not consult, copy, rewrite or reattribute. |

No project source file or legal text is proposed for deletion. No live YouTube/AI request was made for this baseline. Temporary captures and raw machine-local evidence stay in ignored artifacts; curated documentation screenshots will be explicit illustrative application captures.
