# Product QA and screenshots

Run the root verification pipeline with `.venv/Scripts/python.exe scripts/verify.py` (POSIX: `.venv/bin/python`). It includes Python/frontend/browser regressions, lint/types, optimized build, independent package build, audits, static release checks, documentation paths and secret scanning. Browser tests use dependency-injected fixtures, never live keys.

## Coverage and visual checks

The polish browser suite covers375,390,768,1024,1440 and1920-pixel widths in desktop/mobile contexts. It tests long unbroken metadata, empty/100%/balanced/fractional sentiment, visible input labels, keyboard skip navigation/reduced motion, invalid URLs, and the preserved form/cache/provider recovery suite. Numerical counts and returned model attribution remain backend-contract values.

Use `powershell -NoProfile -File scripts/test-production-local.ps1` for isolated real Waitress + trusted loopback TLS + optimized Next verification. Default has no live source/model requests; `-LiveYouTube` is a deliberate bounded opt-in. Do not stop unrelated processes or reuse historical application ports.

## Curated assets

After a successful production build, run `node scripts/capture-product.cjs`. The script owns one loopback optimized Next process, intercepts only explicit illustrative API/thumbnail fixtures inside its fresh browser context, captures genuine application screens and cleans up its process. No private environment file is copied or changed. It records browser errors, layout/landmark/label checks and observed browser timing/transfer metrics in ignored artifacts. This is not live provider verification or a Lighthouse score.

Curated screenshots live in docs/assets; temporary captures/traces/logs live in ignored artifacts/.work/test-results. Results always visibly identify illustrative demo data. Original SVG thumbnail artwork and architecture drawing contain no third-party design/photo assets. The capture source, sizes and current release outcomes are documented in [the asset index](../assets/README.md) and [polish report](../reports/archive/FINAL_REVIEW_YT_POLISH_REPORT.md).
