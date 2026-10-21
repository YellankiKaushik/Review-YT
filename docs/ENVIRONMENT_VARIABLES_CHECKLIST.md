# Environment variable checklist

Names below are read by this project's source or the documented runtime/platform. Values are placeholders or nonsecret settings only. Do not paste existing keys/tokens into Markdown, CLI arguments, screenshots or chat. Keep root .env and apps/web/.env.local untracked. The user enters all production secrets in each provider's dashboard.

## A. Local development

Root .env is loaded by Flask with process variables taking precedence. Next loads its app-local environment; its existing process values also take precedence. Change the files only privately and restart the affected process after edits. Never overwrite an already configured private file with an example.

| Root Flask variable | Local value/purpose |
| --- | --- |
| YOUTUBE_API_KEY | <private YouTube Data API v3 key> |
| BACKEND_API_TOKEN | <private shared token> |
| HOST | 127.0.0.1 |
| PORT | 5100 |
| CACHE_PATH | .cache/reviews.sqlite, relative to repository-root startup |
| SUMMARY_PROVIDER | disabled for a baseline review |
| SUMMARY_ENABLED_PROVIDERS | disabled; optionally add an installed/authorized provider |
| SUMMARY_ALLOW_PAID | false |
| SUMMARY_FALLBACK_ENABLED | false |
| TRANSCRIPTS_ENABLED | false baseline; true only when intentionally enabling optional public captions |
| OLLAMA_BASE_URL | http://127.0.0.1:11434 (local only) |
| OLLAMA_MODEL | gemma4:e4b, only if already installed |

For the Next app, apps/web/.env.local needs only BACKEND_URL=http://127.0.0.1:5100 and the matching private BACKEND_API_TOKEN. Local development scripts pin loopback ports, disable paid/fallback and isolate REVIEW_DIST=.next-local; that build-output control is local-only. The backend cannot see changes until restarted; Next should be restarted after local server-variable edits. No model is downloaded by the lifecycle scripts.

## B. Render backend

The Blueprint already sets all nonsecret values below. In initial Blueprint creation sync:false prompts for the two secret values; later new/changed secrets must be entered manually on the service's Environment page. Save/restart/deploy after changes. Do not assume an old process has reloaded a key. See [Render Blueprint secrets](https://render.com/docs/blueprint-spec#prompting-for-secret-values).

| Variable | Baseline value | Required action |
| --- | --- | --- |
| YOUTUBE_API_KEY | <private API key> | Enter privately; restrict it to YouTube Data API v3. Use stable backend-IP restrictions only when appropriate for actual egress. |
| BACKEND_API_TOKEN | <new private random shared token> | Enter privately; set exactly the same token in Vercel. |
| PYTHON_VERSION | 3.12.15 | Blueprint/runtime selection |
| PYTHONUNBUFFERED | 1 | Blueprint setting |
| HOST | 0.0.0.0 | Public Waitress bind |
| PORT | Provider-assigned | Do not override with the local port |
| CACHE_PATH | /tmp/review-yt-cache/reviews.sqlite | Writable ephemeral path, not permanent storage |
| SUMMARY_PROVIDER | disabled | No cloud inference required |
| SUMMARY_ENABLED_PROVIDERS | disabled | Excludes local Ollama and unapproved cloud providers |
| SUMMARY_ALLOW_PAID | false | Never enable without new spending authorization |
| SUMMARY_FALLBACK_ENABLED | false | Automatic fallback remains prohibited |
| TRANSCRIPTS_ENABLED | false | Keep slow optional captions off for the baseline |
| OPENROUTER_MODEL | openrouter/free | Inert while OpenRouter is not allowed |

Public-bind WSGI startup fails safely if either required credential is blank; the sanitized error names the missing variables only. Loopback diagnostics may still start without keys. A present but rejected YouTube key is a separate API failure.

Do not set OLLAMA_BASE_URL or enable ollama in Render; no laptop endpoint/model weights belong in this service. No CORS origin variable is required: the browser uses a same-origin Next relay and backend requests use the shared token. Do not invent a CORS wildcard to fix auth/connectivity errors.

### Optional OpenRouter

After the baseline works and a current free model/account is eligible, privately add OPENROUTER_API_KEY to Render, retain OPENROUTER_MODEL=openrouter/free or another server-selected **verified zero-price** model, and set SUMMARY_ENABLED_PROVIDERS=disabled,openrouter. Keep SUMMARY_PROVIDER=disabled initially; users may select the available provider in the form. Keep paid/fallback false. Redeploy/restart, inspect /api/providers, then authorize a single bounded inference smoke. A configured credential is not proof of account capacity or completed generation. Provider failure must leave actual YouTube metadata and VADER results available. Do not repeatedly retry free-tier errors.

Other implemented optional server settings are OPENAI_API_KEY/OPENAI_MODEL, GEMINI_API_KEY/GEMINI_MODEL/GEMINI_FREE_TIER_CONFIRMED and GROQ_API_KEY/GROQ_MODEL/GROQ_FREE_TIER_CONFIRMED. Leave them unset and outside the cloud allowlist for this release. Existing keys never authorize paid inference; do not set confirmation flags without a real eligibility decision.

## C. Vercel frontend

| Variable | Value | Scope/type |
| --- | --- | --- |
| BACKEND_URL | <actual verified Render HTTPS origin> | Production server Config; no path, query, user/password or guessed hostname |
| BACKEND_API_TOKEN | <matching private Render token> | Production server Secret |

Set Preview separately only if deliberately authorized. Vercel environment edits affect new deployments; redeploy after changing them. No local Windows .env file is uploaded or required. NODE_ENV is managed by Next/Vercel. Never set NEXT_PUBLIC_BACKEND_API_TOKEN, NEXT_PUBLIC_YOUTUBE_API_KEY or any public key/token equivalent. Provider credentials remain Render-only. REVIEW_LOCAL_TEST is never enabled in cloud; local production testing should trust its temporary loopback TLS certificate rather than weakening the cloud HTTPS requirement. See [Vercel environment variables](https://vercel.com/docs/environment-variables).

The backend token is server authentication, not a user login. Public frontend usage can still consume backend/YouTube quotas, so retain rate limits and review hosting/spending allowances. Never share the token in a URL or smoke report; public verification scripts take optional authentication from a private process environment.


## Verification-only process settings

`scripts/test-production-local.ps1` privately creates a temporary shared token for its isolated services, selects sentiment-only, sets a loopback HTTPS BACKEND_URL, and scopes NODE_EXTRA_CA_CERTS to a generated local certificate. It restores the caller's environment and stops its own processes; it does not overwrite the private .env files. The loopback trust bridge is test infrastructure, not a production backend address. Do not copy its settings into Render/Vercel.

The production verifier uses ports 3202/5102/5103 and outputs artifacts/production-local.json. Its default path performs no live YouTube request; -LiveYouTube is explicit opt-in. Public checks use actual supplied HTTPS origins and optional private BACKEND_API_TOKEN from the process environment. No public smoke script requires a YouTube or cloud-provider key on the frontend. See the exact commands in VERCEL_DEPLOYMENT_HANDOFF.md.

Cloud inference's combined discovery/generation budget is an implementation limit of 25 seconds; Ollama's separate budget is 75 seconds. These are not environment variable names. Keep captions/AI disabled for the initial cloud baseline and do not invent timeout configuration keys.
