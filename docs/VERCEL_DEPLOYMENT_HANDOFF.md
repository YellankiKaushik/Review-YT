# Vercel frontend: manual deployment handoff

Prepared on 2026-10-21 from apps/web/vercel.json, the npm workspace/lockfile and current official documentation. **No Vercel project was provisioned.** The maintainer rights/MIT decision is recorded; verify the actual GitHub publication in GITHUB_PUBLICATION_REPORT.md before this manual hosting setup. Verify Render before configuring the frontend's backend origin.

## Import and build settings

In [Vercel Dashboard](https://vercel.com/dashboard), select the intended team **kaushik-yellanki-project**, then Add New > Project. Import the existing [YellankiKaushik/Review-YT](https://github.com/YellankiKaushik/Review-YT). Create a dedicated new project; do not repurpose another project. The maintainer supplies every private environment value.

| Setting | Exact value |
| --- | --- |
| Suggested project name | review-yt (choose an available dedicated variant if needed) |
| Production branch | main |
| Root Directory | apps/web |
| Framework Preset | Next.js |
| Install Command | cd ../.. && npm ci |
| Build Command | cd ../.. && npm run build |
| Output Directory | .next (relative to apps/web) |
| Node.js version | 24.x |
| Outside-root source files | Enable Include source files outside of the Root Directory in the Build Step |
| Functions | Node.js runtime; retain Fluid Compute; route maxDuration is source-controlled |
| Development command | Do not deploy next dev; framework production build handles hosting |

The committed apps/web/vercel.json supplies these install/build/output values. The root package-lock.json is authoritative: never create a second lockfile in apps/web or replace npm ci with an unpinned install. Both commands start from apps/web and move to the repository root; the root build script selects the frontend workspace. Keep development dependencies available during the build because TypeScript and lint tooling are used there.

Outside-root inclusion is needed for the root workspace manifest/lockfile; verify it even when enabled by default. The [Monorepos FAQ](https://vercel.com/docs/monorepos/monorepo-faq) documents this option. Root-directory limits apply without it. [Monorepo deployment](https://vercel.com/docs/monorepos) describes one project per application. Node 24.x is currently supported; platform minor/patch updates are managed by Vercel, so this is not a Windows Node 24.16.0 pin. See [Node versions](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions).

A clean local checkout/install/build tests dependence on committed files; it cannot certify Vercel's actual Linux build, account settings or framework adapter. First hosted deployment must confirm installation starts in the expected directory, finds the root lockfile and produces the apps/web .next build. Do not mark cloud deployment successful from local output.

## Server-only environment values

Set the following in **Production** before Deploy. Configure Preview separately only when intentionally testing that environment. Values must not depend on the developer's untracked files.

| Name | Value |
| --- | --- |
| BACKEND_URL | The **actual verified Render HTTPS origin**, with no path, query or credentials |
| BACKEND_API_TOKEN | The exact private token set in Render |

Use Secret type for BACKEND_API_TOKEN, where offered. BACKEND_URL is nonsecret Config. Do not set any YouTube/OpenRouter key in Vercel: the API keys belong only on Render. Never use NEXT_PUBLIC_ for any credential. Do not set REVIEW_LOCAL_TEST, REVIEW_DIST or local loopback addresses. Vercel/Next set NODE_ENV=production; do not replace it. Environment edits apply to a **new deployment**, so redeploy after changing a value. See [environment variables](https://vercel.com/docs/environment-variables).

## Timeout/cost settings

The API route source requests maxDuration=120 seconds; the relay aborts its upstream fetch at 115 seconds and the browser form has a 120-second budget. Vercel's current Fluid Compute Hobby limit is 300 seconds, so the requested duration fits that limit; retain Fluid Compute and inspect the deployed route settings. This does not guarantee a response within 120 seconds. [Function duration](https://vercel.com/docs/functions/configuring-functions/duration) is the current authority.

A sleeping backend can consume most of a request budget. Start with sentiment-only and captions disabled on Render. If a cold-start connection fails, the app displays a clear error; wait for /health and retry manually. Never enable repeated automatic submissions to burn YouTube quota. Cloud adapters now share a maximum 25-second discovery/generation budget; local Ollama retains its separate 75-second budget. A roughly 60-second cold start plus 25 seconds of YouTube work plus 25 seconds of cloud inference leaves little room within the 115-second relay, so this mitigation is not an outage guarantee. Establish baseline hosting first and keep cloud AI optional. Choose only an eligible free/Hobby plan, review account allowances and spending controls, and do not enable paid upgrades.

## Troubleshooting and proof of success

After Deploy, inspect Build Logs for Node version, successful npm ci, the workspace production build and the reviewed commit. For root/lockfile errors, verify Root Directory and outside-root inclusion before editing dependencies. For an unexpected old artifact, use Redeploy and disable existing Build Cache once to diagnose; routine redeploys can retain it.

Open the **actual returned HTTPS frontend URL** and require HTTP 200. Check /api/providers: a 503 configuration response points to missing/invalid server settings; 401 points to a token mismatch; a connection error can mean backend downtime/cold start or an incorrect origin. In Runtime Logs, inspect the API route's status/latency without logging private headers/bodies. A deployment protection/login response is not an application pass; authenticate through the intended account rather than disabling security silently.

Run the provided public checker against the actual frontend/backend origins. Enable one ten-comment live baseline smoke explicitly, then verify metadata, sentiment arithmetic, chart/navigation/cache/reload and desktop/mobile rendering. No real public URL is recorded here because none has yet been deployed. Keep those results distinct from local production-mode testing. Source publication and future hosting are still subject to the single decision in FINAL_PUBLICATION_RIGHTS_CHECKLIST.md.


## Reproduce local production verification

From the repository root on Windows, with installed project dependencies:

```powershell
powershell -NoProfile -File scripts/test-production-local.ps1
```

This builds the actual optimized Next frontend and starts isolated Next production (3202), Waitress (5102) and a loopback TLS bridge (5103). It trusts a temporary local certificate using the child process trust configuration; it does **not** enable REVIEW_LOCAL_TEST or disable certificate verification. OpenSSL must already be on PATH or available in the installed Git for Windows bundle. The script refuses occupied temporary ports, stops only its own verified process trees, restores temporary process settings and leaves the normal 3200/5100 services alone. Results are ignored artifacts/production-local.json and production logs; this is a local test, not a cloud deployment.

Default checks make no YouTube requests. Explicitly opt in to one fresh ten-comment source (and at most one browser cache-reuse POST):

```powershell
powershell -NoProfile -File scripts/test-production-local.ps1 -LiveYouTube -VideoId rfscVS0vtbw
```

Use -SkipBuild only when the existing optimized build already corresponds to the reviewed source. Do not skip a build after application changes. No model inference is required by this sentiment-only test.

## Verify the eventual deployed origins

Replace both uppercase placeholders with the **actual** provider-returned HTTPS origins. Do not paste a shared token as an argument. Optional authenticated direct-backend checks read a privately populated BACKEND_API_TOKEN process environment variable.

```powershell
powershell -NoProfile -File scripts/check-public.ps1 -FrontendUrl https://ACTUAL_FRONTEND_ORIGIN -BackendUrl https://ACTUAL_BACKEND_ORIGIN
```

This default run checks connectivity/auth/error paths without fetching YouTube comments. For one deliberately bounded real video and desktop/mobile browser checks:

```powershell
powershell -NoProfile -File scripts/check-public.ps1 -FrontendUrl https://ACTUAL_FRONTEND_ORIGIN -BackendUrl https://ACTUAL_BACKEND_ORIGIN -LiveVideo rfscVS0vtbw -Browser
```

The equivalent Python entry point is:

```powershell
.\.venv\Scripts\python.exe scripts/smoke-public.py --frontend https://ACTUAL_FRONTEND_ORIGIN --backend https://ACTUAL_BACKEND_ORIGIN --live-video rfscVS0vtbw --browser
```

The live path permits one fresh ten-comment POST and, with browser verification, at most one second POST that must reuse the cache. It does not perform unlimited retries. Read the actual HTTP statuses, latencies and failure cause in ignored artifacts/public-smoke.json; a failing check is not deployment success. The Python script's --local option is loopback-only and --ca-file supplies local TLS trust; neither option belongs in a claimed public HTTPS verification.
