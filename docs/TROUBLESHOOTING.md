# Troubleshooting

Use your own instance and credentials. The original demo is retired. Never post API keys, shared tokens, auth headers, private comment bodies or screenshots of a private environment file. Messages below reflect current source behavior; upstream provider details are intentionally sanitized.

## Installation and local startup

| Symptom | What to check / safe resolution |
| --- | --- |
| Python/Node/npm missing or unsupported | Check versions/PATH. Use the documented Python 3.12 + Node 24 baseline; reopen your terminal after installation. POSIX may use python3.12; Windows may use py -3.12. |
| ModuleNotFoundError / wrong Python | Run this checkout's explicit .venv Python and install root requirements-dev.txt. Do not install into another project's environment. |
| Workspace dependency missing / npm ci fails | Run from repository root with the committed package-lock.json. Check registry access and Node version. Do not invent a second lockfile. |
| Windows launcher says private config incomplete | Create both ignored files from examples, fill your own key/matching token and exact loopback origin. local_probe prints only presence/equality/status. |
| Edited .env seems ignored | Backend resolves root .env; process variables override it. Next uses app-local dotenv. Restart the affected services and inspect inherited variable names privately; do not change system-wide variables blindly. |
| Port occupied / unrecorded listener | Identify the listener and its owner. The scripts refuse to adopt or terminate unknown services. Stop only your verified instance or choose an intentionally revised manual configuration. |
| Lost lifecycle state | Do not delete state while services run. Inspect process identity/command/creation time; the launcher intentionally refuses unrecorded processes. See [local lifecycle](LOCAL_STARTUP.md). |

## Authentication and connectivity

| Actual response | Meaning / resolution |
| --- | --- |
| 503 `configuration`: backend not connected | Next is missing BACKEND_URL or BACKEND_API_TOKEN. Configure its server environment and restart/redeploy. |
| 503 `backend_not_configured` | Flask has no BACKEND_API_TOKEN; it does not silently allow anonymous API calls. |
| 401 `not_authorized` | The supplied backend token is wrong/missing. Match the private Next token to Flask's token; health remains unauthenticated. |
| 503 `configuration`: trusted HTTPS origin | Optimized Next requires a plain HTTPS origin: no user info, path, query or fragment. Local development allows HTTP loopback; do not bypass production checks. |
| 503 `connection` | Backend is stopped, unreachable, sleeping or misconfigured; verify your own /health, actual origin, DNS/TLS and private host logs. Wait after a cold start before a deliberate retry. |
| 502 `upstream_format` | Backend/proxy returned non-JSON; inspect its route/runtime logs privately. Do not show raw upstream HTML or auth data to users. |
| 429 `request_limit` | Per-process analysis request limit reached. Wait. Next callers may share the relay's backend address. |
| Apparent CORS issue | Browser calls same-origin Next routes; Next authenticates server-to-server. Fix origin/token/connectivity rather than adding wildcard CORS or sending keys from the browser. |

Public Waitress startup raises `Public backend requires: ...` when YOUTUBE_API_KEY or BACKEND_API_TOKEN is blank. This is intentional. Do not weaken it to get a green health page. Use explicit isolated fixtures for offline tests.

## YouTube data and result storage

| Code/state | Meaning / resolution |
| --- | --- |
| `youtube_not_configured` / 503 | Supply your own valid YouTube key to Flask and restart. No genuine collection is possible with an empty key. |
| `youtube_rejected` / 502 or 404 | Invalid/revoked/restricted key or upstream rejection. Check API enablement and actual backend egress restrictions in your Google project. The app cannot reliably distinguish every upstream failure after sanitization. |
| `video_unavailable` / 404 | Private/deleted/unavailable video; choose a valid public one. |
| `comments_disabled` or `comments_empty` warning | Metadata may still be returned with zero sampled comments. Empty sentiment is honest, not a retrieval success with invented text. |
| `youtube_quota` / 429 | Check your own Google quota/usage and reset schedule; do not spam requests or rotate projects to evade quotas. |
| `youtube_format` | Unexpected upstream metadata/comment shape; preserve safe diagnostics and report a minimal reproduction without bodies/credentials. |
| 404 `cache_miss` | Result expired, restarted, never saved or belongs to another provider. Submit a new analysis explicitly; GET does not recollect. |
| 503 `cache_unavailable` on GET | SQLite is unavailable/unwritable; check CACHE_PATH, parent permissions and host filesystem privately. |
| POST returns baseline + cache warning | Genuine sentiment is preserved when SQLite fails, but cross-request reuse cannot be guaranteed. Fix storage; do not treat browser retention as permanent persistence. |

[YouTube setup](YOUTUBE_API_SETUP.md) · [API contract](API.md) · [retention/security](../SECURITY.md).

## Optional providers

- **Provider not enabled:** add the intended ID to the backend allowlist; selected default must be allowed. Browser-supplied URLs/models/keys are intentionally unsupported.
- **Ollama unreachable / model missing:** verify your own loopback daemon and exact installed model name. No automatic download is performed. A remote backend cannot use your laptop's loopback address.
- **OpenRouter 401 → `ai_unauthorized`:** stop retries, check your own private credential/account, update it privately if appropriate and restart. Never retry a known rejected key as an experiment.
- **OpenRouter price/model error → `ai_price_unverified`:** catalog/model pricing could not be verified as zero; no generation is sent. Do not enable paid fallback to hide it.
- **402 → `ai_payment_required`:** credits are required by the provider; no purchase or paid fallback occurs.
- **429 → `ai_rate_limited`:** wait/check your account limits. Free routing is capacity-dependent, not guaranteed.
- **OpenAI unavailable with a key:** paid=false intentionally blocks that adapter. A key is not spending authorization.
- **Gemini/Groq unavailable:** check model/key and your own verified free-tier eligibility before setting its confirmation flag. Never assume a configured model is free.
- **Incomplete/invalid JSON or timeout:** the AI result may be unavailable while genuine metadata/VADER remains usable. No unfinished notes replace a good saved result.

See [optional AI](OPTIONAL_AI_PROVIDERS.md). No cloud API request is necessary to troubleshoot sentiment-only operation.

## Builds and self-hosting

| Failure | Resolution |
| --- | --- |
| Next production build | Verify Node version, root npm ci and full output privately. Do not exclude failing source or disable type/security checks. Build itself requires no real API key. |
| Optimized local relay rejects HTTP | Use proper backend HTTPS/TLS for production. The Windows production verifier creates an isolated trusted loopback bridge; never deploy its test flag or private certificate. |
| Render cannot import core / missing requirements | Backend root must be repository root; build pip install -r requirements.txt; start python apps/api/serve.py. Preserve Python pin and local package sources. |
| Render bind/health failure | HOST=0.0.0.0, platform-assigned PORT, configured own key/token. Inspect logs; don't override PORT with 5100. |
| Vercel missing workspace/lockfile | Root apps/web; outside-root source inclusion on; install cd ../.. && npm ci; build cd ../.. && npm run build; output .next. |
| Corrected host environment still stale | Save then restart/redeploy; a running process doesn't automatically adopt newly edited keys. |
| Slow first cloud request | Free service can sleep; verify health and wait for warmup before retrying. Deadlines remain bounded; no continuous-availability guarantee. |
| Data disappeared on free hosting | SQLite is ephemeral and logically expires. A restart/redeploy can lose it. Durable storage is a separate design/hosting decision. |

Do not reopen the original maintainer's retired services. Use [self-hosting](SELF_HOSTING.md), your own provider dashboard and current plan terms. For contributions, include the reviewed commit, OS/tool versions, sanitized code/status and reproduction steps in [the bug template](../.github/ISSUE_TEMPLATE/bug_report.yml).
