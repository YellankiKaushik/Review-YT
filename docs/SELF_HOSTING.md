# Run your own Review-YT instance

The original maintainer's demo, Render service and Vercel project are retired. This is a **source-code project**, not an ongoing hosted service. Do not reconnect to former domains. Each operator supplies their own accounts, credentials, domains and capacity. No cloud resources are created by this guide or release.

## A. Local or private-server operation

For a private local instance, follow [Getting Started](GETTING_STARTED.md). Use Python 3.12, Node 24, root `npm ci` and the Python dependency lock. Run Waitress with `python apps/api/serve.py` through the installed virtual environment and Next with `npm run dev` during development.

For a production private server:

1. Clone a reviewed revision and install dependencies using [the setup commands](GETTING_STARTED.md). Do not copy another person's .env or runtime data.
2. Configure backend-only YouTube key, random token, writable CACHE_PATH, sentiment-only allowlist, paid/fallback false. Keep Flask on loopback when your reverse proxy shares its machine.
3. Configure Next's server environment with the same token and a **trusted HTTPS backend origin**. Optimized Next rejects a plain HTTP backend even if loopback; do not deploy REVIEW_LOCAL_TEST as a shortcut.
4. Terminate TLS with your operator-managed reverse proxy and certificate, forwarding the backend HTTPS origin to Waitress. Configure an appropriate process supervisor, restricted file ownership, restart policy and network rules for your OS. This repository supplies no universal reverse-proxy/system-service configuration.
5. Run `npm run build` at the root, then `npm run start -w apps/web`. Use the actual Python environment executable for Waitress. The default Next start port is 3200. Manage both processes through your own supervisor; Ctrl+C stops manual foreground processes.
6. Check HTTPS health, authenticated relay inventory and one deliberately bounded real ten-comment analysis. Retain the API/cache/auth limits and review retention, backups and operating costs.

The [Windows production verifier](LOCAL_STARTUP.md) provides an **isolated test-only** trusted loopback TLS bridge; its temporary certificate and process settings are not a public deployment recipe. Do not expose that test bridge or Ollama. You are responsible for real TLS, host updates and abuse controls.

## B. Your own Render backend + Vercel frontend

### 1. Fork and review

Fork [YellankiKaushik/Review-YT](https://github.com/YellankiKaushik/Review-YT) into your own GitHub account. Keep main, the root npm lockfile, LICENSE/NOTICE and all dependency notices. Review your fork's CI before deploying. Never point new services at someone else's private account or reuse the original maintainer's revoked credentials.

### 2. Create the Render backend

In **your Render account**, choose **New → Blueprint**, connect your fork's main branch and select repository-root `render.yaml`. Review the proposed web service and select an eligible plan **before approving creation**. The template requests Free; if unavailable, stop and make your own explicit cost decision rather than silently upgrading. Existing unrelated resources must not be repurposed.

Verify these exact settings (also available through New → Web Service if you deliberately configure it manually):

| Setting | Value |
| --- | --- |
| Root directory | Repository root, leave blank; not apps/api |
| Runtime | Python; PYTHON_VERSION=3.12.15 |
| Build | pip install -r requirements.txt |
| Start | python apps/api/serve.py |
| Health path | /health |
| Bind | HOST=0.0.0.0; use Render's assigned PORT |
| Cache | /tmp/review-yt-cache/reviews.sqlite, ephemeral |
| Baseline | SUMMARY_PROVIDER=disabled; SUMMARY_ENABLED_PROVIDERS=disabled |
| Safety | SUMMARY_ALLOW_PAID=false; SUMMARY_FALLBACK_ENABLED=false; TRANSCRIPTS_ENABLED=false |
| Auto deploy | Off, as supplied by autoDeployTrigger: off |

During initial Blueprint creation, enter **your YOUTUBE_API_KEY** and a **new BACKEND_API_TOKEN** in the private sync:false prompts. For later changes, use the service's Environment page and restart/redeploy; Blueprint sync:false values are not a general secret-sync mechanism. Do not set a laptop Ollama URL or install model weights here.

Deploy the reviewed revision. Inspect the service's build/runtime logs privately and record its **actual returned HTTPS origin**. Open `https://YOUR_BACKEND_HOST/health` after replacing the placeholder. Expect HTTP 200, status ok, contract review-yt/v1. Health is liveness, not proof of key validity. Never assume a generated hostname or append a path to BACKEND_URL.

[Render-specific guide](RENDER_DEPLOYMENT_HANDOFF.md) · [Blueprint reference](https://render.com/docs/blueprint-spec) · [Web-service port binding](https://render.com/docs/web-services#port-binding).

### 3. Create the Vercel frontend

In **your Vercel account/team**, choose **Add New → Project**, import **your fork** and configure:

| Setting | Value |
| --- | --- |
| Framework | Next.js |
| Production branch | main |
| Root Directory | apps/web |
| Node.js | 24.x, if supported by the account/platform |
| Install command | cd ../.. && npm ci |
| Build command | cd ../.. && npm run build |
| Output directory | .next (relative to apps/web) |
| Outside-root source inclusion | Enable Include source files outside of the Root Directory in the Build Step |

The committed `apps/web/vercel.json` supplies install/build/output settings. Both commands move from apps/web to the root because the root workspace manifest and lockfile are authoritative. Keep build-time devDependencies available. Do not create another lockfile or set `npm install` as an unpinned workaround. [Vercel monorepo FAQ](https://vercel.com/docs/monorepos/monorepo-faq).

Before Deploy, set server-only Production settings:

- `BACKEND_URL=https://YOUR_BACKEND_HOST` — replace with the actual verified origin from your backend, no path/query/user info.
- `BACKEND_API_TOKEN` — **exactly** the backend token, stored as a private Secret/sensitive value where supported.

YouTube and AI keys belong on the backend, not Vercel. Never prefix secrets with NEXT_PUBLIC_. Leave REVIEW_LOCAL_TEST and REVIEW_DIST unset; let Next/platform manage NODE_ENV. Configure Preview separately if deliberately using it. Environment edits require a new deployment. See [Vercel environment variables](https://vercel.com/docs/environment-variables).

Deploy and inspect Build Logs for Node, root npm ci, successful Next build and the correct Git revision. Use the **actual HTTPS frontend URL returned by your project**; no active maintainer URL is supplied. Do not disable deployment protection to disguise an access failure. [Vercel-specific guide](VERCEL_DEPLOYMENT_HANDOFF.md).

### 4. Verify your instance

1. Check backend /health and frontend homepage return HTTP 200.
2. On your frontend, open /api/providers: expect sentiment-only and constraints paid=false/automaticFallback=false. HTTP 401 suggests a shared-token mismatch; 503 may be configuration or connectivity.
3. Through the visible form, submit one public video, **10 comments**, sentiment-only. Verify actual title/channel/sample, count/percentage arithmetic and chart. Disabled/empty comments must show honest notices.
4. Follow results navigation; reload/deep links must read the saved review, not silently recollect. A repeated successful submission should reuse a still-valid matching source/result. Expiry or service restart can require a new explicit submission.
5. Inspect mobile layout and recovery, then stop quota-consuming smoke requests. No cloud AI request is necessary for this baseline.

Windows optional bounded checker, after replacing both placeholders:

```powershell
powershell -NoProfile -File scripts/check-public.ps1 -FrontendUrl https://YOUR_FRONTEND_HOST -BackendUrl https://YOUR_BACKEND_HOST
```

That default makes no analysis request. Add `-LiveVideo VIDEO_ID -Browser` only for an intentionally authorized bounded real workflow. On POSIX use `.venv/bin/python scripts/smoke-public.py --frontend https://YOUR_FRONTEND_HOST --backend https://YOUR_BACKEND_HOST`; `--live-video VIDEO_ID --browser` opts in. Private direct-backend authentication comes from the child process environment, never a token argument. These placeholders are not deployed services.

### 5. Understand free-host limitations

Render's [Free instance documentation](https://render.com/docs/free) warns that these instances are for hobby/evaluation use and can sleep; local SQLite is ephemeral. Cold starts and optional upstream inference may exceed request budgets. The app returns recoverable errors rather than guaranteeing continuous availability. Vercel plans also have usage/eligibility limits: review the [current pricing/plan terms](https://vercel.com/pricing) and your dashboard before deploying. Neither integration implies zero lifetime cost.

Each operator owns their quota, billing, network exposure, logs, retention and service updates. If a free plan is unavailable, do not assume the template author authorizes spending. For durable storage, design and review an appropriate solution separately; this source release does not provision a database or persistent disk.

## Deployment checklist

- [ ] Fork/main CI reviewed; source and notices preserved.
- [ ] Own YouTube key restricted appropriately; private random shared token generated.
- [ ] Backend Python/root/build/start/health/bind settings correct; writable cache.
- [ ] Backend health 200, actual HTTPS origin recorded.
- [ ] Frontend apps/web root, outside-root files, root lockfile and build settings correct.
- [ ] Matching server token and actual HTTPS BACKEND_URL; no public secrets/test flags.
- [ ] Frontend build and real ten-comment baseline verified; navigation/chart/cache checked.
- [ ] Free-plan constraints, quota, cold starts and ephemeral-data limits understood.

These settings were derived from the implementation and previous dated deployment evidence; they are not a guarantee that every future account/platform configuration will work. [Troubleshooting](TROUBLESHOOTING.md).
