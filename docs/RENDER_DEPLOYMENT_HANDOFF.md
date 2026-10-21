# Deploy your own Render backend

The maintainer's Render service/Blueprint is retired. This guide applies only to **your own account and fork**, not an existing maintainer deployment. The complete sequence is in [self-hosting](SELF_HOSTING.md).

## Create and review

In [Render Dashboard](https://dashboard.render.com/), select **New → Blueprint**, connect your fork's main branch and repository-root `render.yaml`. Choose a new dedicated service and inspect its proposed plan/settings before approval. The template requests Free only; if the account is ineligible or that plan is not offered, stop and decide costs explicitly. Do not attach unrelated resources. Manual New → Web Service can use the same settings below.

| Setting | Verified template/source value |
| --- | --- |
| Runtime/root | Native Python; leave Root Directory blank (repository root) |
| Python | PYTHON_VERSION=3.12.15, matching .python-version |
| Build | pip install -r requirements.txt |
| Start | python apps/api/serve.py |
| Health | /health |
| Bind | HOST=0.0.0.0; provider assigns PORT |
| Cache | /tmp/review-yt-cache/reviews.sqlite |
| Baseline | SUMMARY_PROVIDER=disabled; SUMMARY_ENABLED_PROVIDERS=disabled |
| Safety | SUMMARY_ALLOW_PAID=false; SUMMARY_FALLBACK_ENABLED=false; TRANSCRIPTS_ENABLED=false |
| Auto deploy | autoDeployTrigger: off; reviewed deployments are manual |
| Region | Template Singapore; select according to your own requirements |

`requirements.txt` includes the runtime lock and local core with optional captions dependencies; captions remain off. Never set Render PORT=5100. See [Flask on Render](https://render.com/docs/deploy-flask), [port binding](https://render.com/docs/web-services#port-binding) and [Python versions](https://render.com/docs/python-version).

## Private environment

Initial Blueprint creation prompts for sync:false **YOUTUBE_API_KEY** and **BACKEND_API_TOKEN**. Supply your own restricted YouTube key and a new random shared token. Later changes require manual service Environment edits and a restart/redeploy; see [Blueprint secret prompts](https://render.com/docs/blueprint-spec#prompting-for-secret-values).

The other baseline values are in render.yaml. Do not upload .env, enable laptop Ollama, download weights or add paid cloud inference as an installation step. Optional cloud settings belong on the backend only after the baseline works and account/pricing eligibility is deliberately checked. [Configuration reference](CONFIGURATION.md).

## Verify and operate

Inspect the actual build/runtime logs privately. Use the returned HTTPS origin, e.g. the placeholder `https://YOUR_BACKEND_HOST`, then GET `/health`. HTTP 200/status ok proves liveness, not key validity or a specific commit. Configure that actual origin in your own Next project and perform one intentional ten-comment analysis to validate the complete instance.

Free services can sleep and their filesystem is ephemeral. Your SQLite cache may disappear after restart/redeploy; logical TTL is not durable storage. [Current Free limitations](https://render.com/docs/free) and your account allowances control availability/cost. Do not imply continuous uptime, buy a disk automatically or silently upgrade a plan. Review applicable dependency/service terms for your actual deployment. [Troubleshooting](TROUBLESHOOTING.md).
