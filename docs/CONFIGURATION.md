# Configuration reference

Names and defaults below were checked against `AIConfig.read`, Flask application/WSGI startup, the Next relay and committed templates. Real analysis needs **your own YouTube key**. The former maintainer's private files and services are not part of setup. Never copy keys into documentation, issues, process arguments, screenshots or browser variables.

## Files, precedence and restart

- Backend: root `.env`, loaded from the repository path with `override=False`. Existing process environment values take precedence. Start commands should run from the repository root; a relative CACHE_PATH is relative to that working directory.
- Next: `apps/web/.env.local` for private local server settings. Next's process environment takes precedence; it also supports standard environment-specific dotenv files. Keep **all** secret-bearing dotenv variants untracked. [Official Next environment loading](https://nextjs.org/docs/app/guides/environment-variables).
- Standalone core CLI: reads process variables directly; it does not load the backend .env automatically. Its provider/key names match the table, but optional Flask caption configuration is not a CLI switch.
- Hosts: put backend settings in your backend's private environment and frontend relay settings in your Next host's server environment. Do not upload local private files. Save and restart/redeploy the affected process after changes.
- `.env.example` and `apps/web/.env.example` are public templates with empty secrets, not usable credentials. Copy them only when the destination does not already exist.

Generate a new shared token with `.venv/Scripts/python.exe -c "import secrets; print(secrets.token_urlsafe(32))"` on Windows, or `.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))'` on POSIX. Keep its output private. Set **exactly the same BACKEND_API_TOKEN** on Flask and the Next server. Set BACKEND_URL to **your own** backend origin. Never use `NEXT_PUBLIC_` for secrets.

## Application variables

“Backend host” means your own server/Render service; “Next host” means your own Next server/Vercel project. Blank optional credentials must remain blank unless that integration is deliberately configured.

| Variable | Purpose / required? | Consumer | Source default / example behavior | Secret? | Placement |
| --- | --- | --- | --- | --- | --- |
| YOUTUBE_API_KEY | Required for real comments and public-bind startup | Flask/core | Empty: honest `youtube_not_configured`, no demo fallback | Yes | Root .env or backend host |
| BACKEND_API_TOKEN | Required for authenticated routes/relay and public bind | Flask + Next server | Empty: backend/relay 503; supplied wrong token: 401 | Yes | Both private files or both hosts, matching |
| BACKEND_URL | Required trusted backend origin | Next server | Unset: 503; local example http://127.0.0.1:5100; production requires HTTPS origin with no path/query/credentials | No, but server-only | apps/web/.env.local or Next host |
| CACHE_PATH | Optional SQLite path | Flask store | Absolute root .cache/reviews.sqlite if unset; example relative .cache/reviews.sqlite; Render /tmp/review-yt-cache/reviews.sqlite | Not a key; contents sensitive | Root .env or backend host |
| HOST | Optional listener bind | Waitress entry | 127.0.0.1; host uses 0.0.0.0 | No | Root .env or backend host |
| PORT | Optional listener port | Waitress entry | 5100; cloud provider supplies its assigned port | No | Root .env locally; host managed in cloud |
| TRANSCRIPTS_ENABLED | Optional public English captions | Flask/core | false; use true deliberately | No | Root .env or backend host |
| SUMMARY_PROVIDER | Default selected provider | Flask/core | disabled | No | Root .env or backend host |
| SUMMARY_ENABLED_PROVIDERS | Comma-separated server allowlist | Flask/core | Source default lists all six implemented IDs; example/Render template allow only disabled | No | Root .env or backend host |
| SUMMARY_ALLOW_PAID | Explicit paid-inference authorization | Core | false; keep false for the documented baseline | No | Root .env or backend host |
| SUMMARY_FALLBACK_ENABLED | Automatic fallback switch | Core | false; **true is rejected**, not implemented | No | Root .env or backend host |
| OLLAMA_BASE_URL | Optional local daemon origin | Core | http://127.0.0.1:11434; HTTP loopback origins only | No | Local backend only |
| OLLAMA_MODEL | Installed local model identifier | Core | Empty; choose a model already installed in your daemon | No | Local backend only |
| OPENROUTER_API_KEY | Optional OpenRouter account credential | Core | Empty: unavailable | Yes | Root .env or backend host only |
| OPENROUTER_MODEL | Server-selected model | Core | openrouter/free; catalog pricing must still pass at request time | No | Root .env or backend host |
| OPENAI_API_KEY | Optional OpenAI credential | Core | Empty: unavailable; even a present key cannot enable paid app inference by itself | Yes | Root .env or backend host only |
| OPENAI_MODEL | Server-selected Responses model | Core | gpt-4.1-mini, inert with paid disabled; not a current availability guarantee | No | Root .env or backend host |
| GEMINI_API_KEY | Optional Gemini credential | Core | Empty: unavailable | Yes | Root .env or backend host only |
| GEMINI_MODEL | Server-selected Gemini model ID | Core | Empty: unavailable | No | Root .env or backend host |
| GEMINI_FREE_TIER_CONFIRMED | Operator eligibility decision for Gemini | Core | false; required with paid disabled | No | Root .env or backend host |
| GROQ_API_KEY | Optional Groq credential | Core | Empty: unavailable | Yes | Root .env or backend host only |
| GROQ_MODEL | Server-selected Groq model ID | Core | Empty: unavailable | No | Root .env or backend host |
| GROQ_FREE_TIER_CONFIRMED | Operator eligibility decision for Groq | Core | false; required with paid disabled | No | Root .env or backend host |

Allowed IDs: `disabled,ollama,openrouter,openai,gemini,groq`. The selected provider must be in the allowlist; unknown IDs fail startup. Browser input chooses only an allowed ID, never a key, URL or model. Summary boolean settings accept `true` or `false`; use those exact values. The template's restricted allowlist also avoids contacting a local model daemon during inventory.

## Platform and verification settings

| Variable | Purpose / consumer | Default / safety rule | Secret? | Placement |
| --- | --- | --- | --- | --- |
| PYTHON_VERSION | Render runtime selection | Template 3.12.15; agrees with .python-version | No | Render template/dashboard |
| PYTHONUNBUFFERED | Python log buffering | Render template 1 | No | Backend host |
| NODE_ENV | Next runtime mode | Set by Next/platform; do not override to bypass production safeguards | No | Runtime managed |
| NEXT_TELEMETRY_DISABLED | Next telemetry opt-out | Verification/lifecycle scripts set 1 | No | Local child process / CI if desired |
| REVIEW_DIST | Alternative Next build directory | .next if unset; lifecycle .next-local, browser tests .next-e2e | No | Local test process only |
| REVIEW_LOCAL_TEST | Allows HTTP loopback relay in an optimized local test | Unset; never enable on a public host | No, but security-sensitive | Isolated test child only |
| NODE_EXTRA_CA_CERTS | Standard Node additional trust for the loopback TLS verifier | Unset; verifier supplies its temporary certificate to its own child | No; related private key is sensitive | Isolated local test only |

No configurable cache TTL/count/size or AI timeout/token-limit environment variables are implemented. Current limits are source constants: source TTL 600 seconds, successful result TTL 1800 seconds, 100 source/500 result slots, 1.5 MB encoded entry; successful AI settings use a 768-token cap and 75-second local/at most 25-second combined cloud discovery/inference budget. Do not invent environment names for these constants. [API behavior](API.md) · [retention/security](../SECURITY.md).

## Minimum configurations

Local real analysis: two private files, your own YouTube key, matching random token, loopback BACKEND_URL, sentiment-only allowlist, paid/fallback false. No AI key is required.

Public backend: your own key/token, HOST=0.0.0.0 and a writable cache path. Public WSGI startup refuses blank required credentials; loopback liveness can start for diagnostics without a key but cannot retrieve real comments.

Public Next: your actual verified HTTPS backend origin and matching private token, server-only. Keep local test flags unset. Each host must be restarted/redeployed after its private configuration changes. A configured key's presence is not evidence that its account is valid. [Troubleshooting](TROUBLESHOOTING.md).
