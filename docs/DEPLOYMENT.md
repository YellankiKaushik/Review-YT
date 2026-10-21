# Production deployment and safe releases

## Current verified deployment

- Frontend: https://review-yt.vercel.app — Vercel, homepage HTTP200 on2026-10-21.
- Backend: https://review-yt-api.onrender.com/health — Render, HTTP200/status ok, review-yt/v1.
- Frontend provider inventory: /api/providers — HTTP200, sentiment-only; paid/fallback false.

These are observed checks, not uptime guarantees. Health does not expose a backend commit SHA. The maintainer rights/MIT decision is recorded in [the checklist](FINAL_PUBLICATION_RIGHTS_CHECKLIST.md). Historical predeployment reports are retained [in the archive](reports/archive/README.md). Current release evidence is in [the polish report](../FINAL_REVIEW_YT_POLISH_REPORT.md).

## Update the existing application

1. Work on a dedicated branch. Preserve server-only credentials, API schema, source notices and baseline sentiment.
2. Run the full verification script, production-mode local test, documentation paths/inventory checks and secret scan.
3. Push normally and open a PR into main. Wait for actual CI; inspect an available Vercel preview and test responsive/core flows.
4. Merge only when checks pass, permissions allow and no critical preview defect remains. Never force-push or rewrite main.
5. Vercel may deploy main automatically. Verify the actual ready deployment/commit and public homepage/provider inventory before declaring rollout complete.
6. Render's Blueprint has auto-deploy off. If backend/runtime requirements change, manually deploy the reviewed commit through the authorized existing service and verify health/logs. A frontend-only change does not require restarting the working backend.
7. Run one bounded public ten-comment sentiment-only check, then verify navigation/chart/cache reuse. Never repeat quota-consuming requests during visual iteration. Use scripts/check-public.ps1 with actual HTTPS origins and its explicit -LiveVideo/-Browser flags.

Do not change hosting secrets or create paid resources as part of UI cleanup. Missing dashboard/preview permissions are documented, not bypassed. Keep the branch ready if a required external action is blocked.

## Configuration and recovery

[Render handoff](RENDER_DEPLOYMENT_HANDOFF.md), [Vercel handoff](VERCEL_DEPLOYMENT_HANDOFF.md) and [environment checklist](ENVIRONMENT_VARIABLES_CHECKLIST.md) describe the existing workspace/runtime settings. Do not recreate an existing project. Roll back through the platform's normal verified deployment controls if a critical production regression occurs; preserve Git history. Free hosting can sleep and reset SQLite cache. A cache miss requires an explicit new analysis, never hidden GET regeneration.
