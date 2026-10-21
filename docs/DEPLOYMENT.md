# Gated publication and hosting procedure

**Current state: maintainer rights/license decision recorded (MIT, 2026-10-21).** See FINAL_PUBLICATION_RIGHTS_CHECKLIST.md for the actual declaration and exceptions, and GITHUB_PUBLICATION_REPORT.md for current verification/publication outcomes. Never force-push or substitute historical source. Recheck the destination immediately before a normal push. **The current task must not create Render or Vercel resources: the maintainer handles both dashboards and production secret entry.** The hosting instructions below are a manual handoff after source publication, not authorization for this agent to provision resources.

## Non-destructive GitHub publication after rights clearance

From this new workspace, run tests/audits and `python scripts/secret_check.py`, then verify `git status --short`, `git log --oneline --all`, `git rev-list --max-parents=0 HEAD`, `git remote -v`, `git config user.email` and `git ls-files`. The maintainer email matched the authenticated GitHub account during this work; verified-email status was not exposed. Inspect the source inventory and dependency notices. Do not push if private config, runtime data or old history appears.

```powershell
git ls-remote https://github.com/YellankiKaushik/Review-YT.git
```

If there are any remote refs, stop and reconcile without overwriting them. If no origin is set and the target is still empty, set the supplied destination:

```powershell
git remote add origin https://github.com/YellankiKaushik/Review-YT.git
git push --dry-run origin main
git push -u origin main
```

Never change an existing remote silently; verify it first. Use GitHub's existing authenticated credential manager or `gh auth login` if required. Do not paste tokens in shell commands/chat. Confirm the remote main SHA equals local HEAD, inspect the remote tree, and verify the new offline GitHub Actions run. Fix actual CI failures before a release tag. No tag or remote run is claimed now.

## Render: new dedicated free API

After rights clearance and publication, sign into the intended Render account. No Render CLI/RENDER_API_KEY was available in this execution environment, and no connected Render account was established. Dashboard access is required unless an authorized connector is supplied. Create a **new** Blueprint from the supplied repository and review `render.yaml`; never select an unrelated existing service. Confirm plan **free**, root repository build context, native Python 3.12.15, `pip install -r requirements.txt`, `python apps/api/serve.py`, and `/health`.

Set the YouTube API key privately in service secrets. The Blueprint selects sentiment-only and requires no OpenRouter key. Generate a distinct random backend token and store it privately; it must match the later Vercel secret. Keep paid/fallback false, allowlist `disabled`, captions disabled for the low-resource cloud baseline. Render supplies PORT; HOST=0.0.0.0 binds the service. Do not deploy Ollama/Gemma weights. Do not create a paid service or disk. Inspect actual installation/startup logs without logging provider URLs or credentials. Confirm the actual HTTPS `/health` and authenticated `/api/providers` before recording any URL.

The official [Blueprint specification](https://render.com/docs/blueprint-spec) uses runtime=python and autoDeployTrigger=off. The free plan currently lists 512 MB RAM and 0.1 CPU; local memory measurements are not proof of cloud capacity. [Free hosting](https://render.com/docs/free) sleeps after 15 idle minutes, can take about a minute to wake, and loses local SQLite state on restart/redeploy/sleep. Free hours and bandwidth/build allowances are limited; billing/suspension behavior depends on account payment/spend settings. Review those settings before activation. This is a hobby/demo configuration, not an uptime or zero-overage-cost guarantee.

## Vercel: new dedicated frontend

The connected Vercel tool successfully listed the intended account's team. No Review-YT project was created, and unrelated projects were untouched. After the API is verified, import the supplied GitHub repository into a **new** Review-YT project. Root Directory: `apps/web`. The committed `apps/web/vercel.json` installs at the workspace root and builds the frontend workspace; output is `.next`.

Set server-only BACKEND_URL to the **actual verified Render HTTPS origin**, and BACKEND_API_TOKEN to the matching private backend secret. Do not use NEXT_PUBLIC variables, do not set REVIEW_LOCAL_TEST in cloud, and do not copy the local .env into hosting. Local Ollama is never a public dependency. Review current free/Hobby eligibility and spending controls; do not authorize a paid plan implicitly.

Deploy only after the gates pass. Inspect the actual build, record its commit and HTTPS URL, then test homepage, proxy auth, provider inventory, bad input, a bounded ten-comment YouTube request, chart/attribution, optional-provider unavailability and cache/reload on desktop/mobile. A sleeping backend gets a clear connection/cold-start message. Cache-only GET never silently regenerates lost results. Current route duration is 120 seconds with a 115-second relay timeout; validate the actual account/region duration limits and cold-start behavior before claiming public readiness.

No cloud build or public end-to-end verification has run in this execution. Local static configuration checks cannot establish deployment success.


## Optional cloud activation after baseline deployment

The committed Blueprint uses SUMMARY_PROVIDER=disabled and SUMMARY_ENABLED_PROVIDERS=disabled. When current zero pricing and account capacity are verified, add private OPENROUTER_API_KEY in Render, set the allowlist to disabled,openrouter, leave the default provider disabled until the operator chooses otherwise, and keep SUMMARY_ALLOW_PAID=false and SUMMARY_FALLBACK_ENABLED=false. Select OpenRouter for one bounded form check. Errors preserve real metadata/VADER. Never enable hosted laptop Ollama.

## Exact platform settings requiring hosted verification

Render: Dashboard > New > Blueprint > connect the existing repository after publication. Review the new review-yt-api free service, no paid disk. Supply only YOUTUBE_API_KEY and a new random BACKEND_API_TOKEN securely. Confirm Python 3.12.15, root build `pip install -r requirements.txt`, start `python apps/api/serve.py`, HOST=0.0.0.0, assigned PORT, and /health. Deploy manually; inspect actual build/runtime logs and verify HTTPS health/authenticated inventory before recording an origin. Linux/native package and Python-patch availability remain unverified until this build.

Vercel: connected team kaushik-yellanki-project; create new review-yt, import the supplied repository, Root Directory apps/web. Enable **Include source files outside of the Root Directory in the Build Step** so root package-lock/workspaces are available. Install `cd ../.. && npm ci`; build `cd ../.. && npm run build`; output .next. These commands resolve from apps/web to the repository root; only a hosted build can prove Vercel's full environment. Configure server-only BACKEND_URL=<actual verified Render HTTPS origin> and matching BACKEND_API_TOKEN in Production; Preview only if authorized. Do not set REVIEW_LOCAL_TEST, upload local .env, or use NEXT_PUBLIC secrets. Inspect actual build and relay logs.

Post-deploy acceptance: health/homepage/provider proxy 200; invalid input; one real ten-comment baseline form; sentiment arithmetic/chart/title/thumbnail/navigation; graceful missing AI; desktop/mobile/no browser errors; cache/reload and expired-cache reanalysis screen; private-value bundle scan; bounded cold-start test where practical. Only after real remote checks add public URLs, CI badges and a release tag.
