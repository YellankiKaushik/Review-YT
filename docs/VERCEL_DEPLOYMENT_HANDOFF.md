# Deploy your own Vercel frontend

The maintainer's Vercel project is retired. Use **your own account/team and fork**. This documentation does not reconnect a former project. Follow [self-hosting](SELF_HOSTING.md) to create/verify your own backend first.

## Import settings

In [Vercel Dashboard](https://vercel.com/dashboard), choose **Add New → Project**, import your fork and review:

| Setting | Value |
| --- | --- |
| Framework / branch | Next.js / main |
| Root Directory | apps/web |
| Node.js | 24.x, subject to current platform support |
| Install | cd ../.. && npm ci |
| Build | cd ../.. && npm run build |
| Output | .next, relative to apps/web |
| Outside-root files | Enable Include source files outside of the Root Directory in the Build Step |

`apps/web/vercel.json` supplies the install/build/output values. The root npm workspace manifest and package-lock.json remain authoritative. Keep build-time devDependencies; don't create a second lockfile or deploy `next dev`. [Monorepos FAQ](https://vercel.com/docs/monorepos/monorepo-faq) · [Node runtime versions](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions).

## Server-only environment

- BACKEND_URL: your own **actual verified HTTPS backend origin**, no path, query, credentials or guessed hostname. Example placeholder: `https://YOUR_BACKEND_HOST`.
- BACKEND_API_TOKEN: exactly the backend's private token, stored as a Secret/sensitive setting where supported.

Set Production before Deploy. Configure Preview separately if desired; account policies may require distinct preview credentials/backends. Do not put YouTube/AI keys on the frontend host, use NEXT_PUBLIC_ for secrets, or set local REVIEW_LOCAL_TEST/REVIEW_DIST flags. Environment changes affect new deployments: save and redeploy. [Vercel environment variables](https://vercel.com/docs/environment-variables).

## Verification and limits

Inspect Build Logs for the reviewed Git revision, root npm ci and successful workspace build. Use the **actual returned frontend URL**, not a maintainer domain. Verify homepage and /api/providers, then one deliberately bounded ten-comment baseline, navigation/chart/cache/reload/mobile behavior. No cloud AI is required. Auth/protection pages are not successful application responses; authenticate normally rather than disabling protection.

Source routes request maxDuration=120; relay fetch aborts at 115 seconds and the form has its own 120-second budget. These implementation limits do not guarantee enough time for a sleeping backend and upstream retrieval. Verify current [function duration limits](https://vercel.com/docs/functions/configuring-functions/duration), [plan terms](https://vercel.com/pricing) and actual project settings. A cold-start error should be followed by a deliberate health check and retry, never repeated automated submissions.

For workspace errors, check root/outside-root settings before changing dependencies. For 401, check the matching private token; for 503 inspect server configuration, origin/TLS and backend health. Do not weaken HTTPS/CORS/auth safeguards. [Troubleshooting](TROUBLESHOOTING.md).

## Optional operator smoke commands

After replacing placeholders with your own actual HTTPS origins:

```powershell
powershell -NoProfile -File scripts/check-public.ps1 -FrontendUrl https://YOUR_FRONTEND_HOST -BackendUrl https://YOUR_BACKEND_HOST
```

Default performs no live analysis. Add `-LiveVideo VIDEO_ID -Browser` only for an explicitly intended bounded source check. Direct backend authentication is read privately from the process environment, never a CLI token argument. For local optimized offline verification use `scripts/test-production-local.ps1`; its temporary loopback TLS trust is test infrastructure, not a public certificate or deployable service. [Local lifecycle](LOCAL_STARTUP.md).
