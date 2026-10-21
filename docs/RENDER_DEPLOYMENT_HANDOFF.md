# Render backend: manual deployment handoff

## Existing production status — 2026-10-21

The maintainer has created the dedicated Render deployment. GET https://review-yt-api.onrender.com/health returned HTTP200 during this mission's baseline. See [current operations](DEPLOYMENT.md) and [release evidence](../FINAL_REVIEW_YT_POLISH_REPORT.md). This is not an uptime or exact backend-commit guarantee. **Do not create a duplicate service/project or change production environment secrets.** The original setup instructions below are retained for understanding/recreating a deployment only when explicitly requested.

## Create the dedicated service

Sign into [Render Dashboard](https://dashboard.render.com/). After approved GitHub publication, choose **New > Blueprint**, connect [YellankiKaushik/Review-YT](https://github.com/YellankiKaushik/Review-YT), branch main, and select the repository-root render.yaml. Inspect the proposed service before creation. Select a new dedicated service; do not attach an unrelated one. If review-yt-api already belongs to an unrelated service, stop that Blueprint flow and use New > Web Service with an available dedicated name and the same settings below, or review an explicit Blueprint name change before creation. The maintainer enters all secret values privately.

| Setting | Exact value |
| --- | --- |
| Service type | Web Service (native Python) |
| Recommended name | review-yt-api (choose an available dedicated variant if needed) |
| Repository | https://github.com/YellankiKaushik/Review-YT |
| Branch | main |
| Blueprint path | render.yaml |
| Root directory | Leave blank: repository root, **not apps/api** |
| Runtime / dashboard language | Python / Python 3 |
| Python | PYTHON_VERSION=3.12.15; repository .python-version agrees |
| Build command | pip install -r requirements.txt |
| Start command | python apps/api/serve.py |
| Health check | /health |
| Region | Singapore, matching the Blueprint |
| Plan | Free, only if eligible and offered; no paid upgrade or disk |
| Auto deploy | Off (autoDeployTrigger: off); deploy reviewed commits manually |

requirements.txt installs requirements-runtime.lock plus the local packages/review_yt_core[captions] package. Captions remain disabled in the cloud baseline. The entry point imports Flask through the installed library, creates the app and runs Waitress with four threads, bounded request bodies and no exposed tracebacks. It reads Render's assigned PORT and HOST=0.0.0.0; never set PORT=5100 in Render. Render requires a public bind and supports an app-specific WSGI command. See [port binding](https://render.com/docs/web-services#port-binding) and [Flask deployment](https://render.com/docs/deploy-flask).

The Python pin overrides the platform default. A fully qualified PYTHON_VERSION is required by [Render's Python-version instructions](https://render.com/docs/python-version). Actual Linux install and runtime support still require the first real hosted build; this document does not claim that build passed.

## Enter environment settings

The Blueprint defines YOUTUBE_API_KEY and BACKEND_API_TOKEN with sync:false. During **initial Blueprint creation**, Render prompts for each secret. Later Blueprint updates do not prompt for new sync:false settings; add those manually on the service's Environment page. See [Blueprint secret prompts](https://render.com/docs/blueprint-spec#prompting-for-secret-values).

| Name | Value to enter/select |
| --- | --- |
| YOUTUBE_API_KEY | Your private YouTube Data API v3 credential |
| BACKEND_API_TOKEN | A new private random shared token; reuse this exact value only in Vercel's server-side setting |
| HOST | 0.0.0.0 |
| PYTHON_VERSION | 3.12.15 |
| PYTHONUNBUFFERED | 1 |
| CACHE_PATH | /tmp/review-yt-cache/reviews.sqlite |
| SUMMARY_PROVIDER | disabled |
| SUMMARY_ENABLED_PROVIDERS | disabled |
| SUMMARY_ALLOW_PAID | false |
| SUMMARY_FALLBACK_ENABLED | false |
| TRANSCRIPTS_ENABLED | false |
| OPENROUTER_MODEL | openrouter/free (inert until explicitly enabled) |
| PORT | Supplied by Render; leave it alone |

All nonsecret values above already exist in render.yaml. Do not upload local .env files, set laptop Ollama endpoints, install/download model weights or add provider keys to frontend variables. Optional OpenRouter activation is separate in ENVIRONMENT_VARIABLES_CHECKLIST.md; it is not required for baseline analysis.

## Deploy, inspect and verify

Review account quotas/spend settings, then create/deploy the new **Free** service. In Events/Deploys, open the build log: the pinned dependencies and local core package must install successfully. In Logs, confirm the Waitress process stays running without traceback/configuration/cache errors. Use Manual Deploy > Deploy latest commit for reviewed updates; use a clear build cache only when an actual stale build requires it. Environment changes require a restart/deploy. Preserve private settings when syncing later Blueprint changes.

Use only the HTTPS origin actually returned by Render. Open its /health and require HTTP 200 with status=ok, application=Review-YT and contract=review-yt/v1. Authenticated /api/providers must return only the sentiment-only baseline; an unauthenticated request must return HTTP 401. Public-bind startup now refuses to listen if YOUTUBE_API_KEY or BACKEND_API_TOKEN is blank, using a sanitized message naming the missing variables. A green /health alone still does not prove that YouTube accepts a configured credential or that proxy operation works. Use the provided public smoke script after Vercel is deployed; a real ten-comment run is explicit opt-in.

Failure clues: package import errors imply wrong root/install command; port scan errors imply incorrect HOST/PORT; cache warnings imply unavailable CACHE_PATH (POST can return an uncached baseline; saved-result GET reports cache_unavailable rather than regenerating); HTTP 401 through Vercel implies mismatched shared tokens; safe configuration/unavailable messages require correcting settings rather than enabling debug output. Never paste secret-bearing logs publicly. Record actual build commit, origin and smoke output before declaring success.

## Free-service limits

Render Free currently provides 0.1 CPU/512 MB, sleeps after 15 idle minutes and can take about a minute to wake. Restarts, redeploys and sleeping erase local files, including SQLite results. Monthly workspace free hours, bandwidth and build allowances apply; usage can suspend services or incur supplementary usage when billing permits. Review account limits first. See [Free hosting](https://render.com/docs/free) and [Blueprint compute plans](https://render.com/docs/blueprint-spec). This is a demonstration/hobby deployment, not permanent storage or an uptime promise. Keep summaries/captions disabled initially to reduce work during cold starts.


## Post-deployment checker

Once the frontend also exists, use the real provider-returned origins and the bounded commands in [VERCEL_DEPLOYMENT_HANDOFF.md](VERCEL_DEPLOYMENT_HANDOFF.md#verify-the-eventual-deployed-origins). The default checker makes no YouTube calls; -LiveVideo explicitly permits a ten-comment baseline. Optional direct-backend authentication reads BACKEND_API_TOKEN securely from the calling process environment, never a CLI argument. Inspect artifacts/public-smoke.json for actual statuses/latencies; do not claim success from a loading/login page. Local production verification can be reproduced with `powershell -NoProfile -File scripts/test-production-local.ps1`; add -LiveYouTube deliberately for the bounded real workflow.

Cloud adapters cap their combined discovery/generation work at 25 seconds; local Ollama has a separate 75-second limit. Keep production captions/AI off initially so cold starts and provider failures cannot make optional summary work a dependency of a usable sentiment result. No bound can guarantee future hosting or network availability.
