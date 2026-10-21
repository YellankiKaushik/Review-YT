# Optional AI providers

**VADER sentiment-only works without any AI provider.** Real YouTube input still requires the operator's own YouTube key. This project bundles adapters, not accounts, model weights, a permanent free inference entitlement or an active hosted demo.

## Support and evidence

| Provider | Implemented / offline coverage | Live evidence in this source-only release | Cost / availability |
| --- | --- | --- | --- |
| disabled | Complete sentiment baseline and UI/cache regressions | No new live source retrieval; previous genuine YouTube baseline is dated in the archive | No model call; YouTube/hosting quotas still apply |
| ollama | Loopback discovery/chat, structured output, error/metadata coverage | Previously verified local Gemma use is historical; no model/daemon contacted in this release | Local hardware/resources and model license apply; no weights downloaded by app |
| openrouter | Catalog zero-price verification, capped request, no fallback, returned-model metadata | No new live request; historical credential/account outcomes do not validate a new user's account | Free routes may be unavailable/rate-limited; verified pricing required before generation |
| openai | Responses integration, bounded structured notes and failures | Unverified live in this release | Intentionally unavailable while paid=false; may require payment |
| gemini | Native generation/usage metadata and failure coverage | Unverified live in this release | Operator must verify model/account eligibility; may require payment or be rate-limited |
| groq | Compatible generation, usage/model attribution and failure coverage | Unverified live in this release | Operator must verify model/account eligibility; may require payment or be rate-limited |

“Offline coverage” means deterministic HTTP/engine fixtures, not genuine cloud output. Prior live results are **dated evidence only** in [the archive](reports/archive/README.md); former Google/OpenRouter keys were revoked by the owner, not by this release. No provider availability is inferred from having an adapter or a key-shaped value.

## Safe baseline and enabling a provider

Keep these settings for normal use:

```dotenv
SUMMARY_PROVIDER=disabled
SUMMARY_ENABLED_PROVIDERS=disabled
SUMMARY_ALLOW_PAID=false
SUMMARY_FALLBACK_ENABLED=false
TRANSCRIPTS_ENABLED=false
```

To add an optional provider, configure its backend key/model (or installed local model) privately, add its ID to SUMMARY_ENABLED_PROVIDERS alongside disabled, then restart the backend. Keep SUMMARY_PROVIDER=disabled initially; choose the configured provider explicitly in the form. Inventory reports configured status and descriptions, not guaranteed successful inference. Browser input cannot select arbitrary models, URLs or credentials.

### Ollama / local Gemma

On a machine you control, install/configure Ollama separately under its terms. Choose an **already installed** model from your daemon (`ollama list` is an operator-run diagnostic), set OLLAMA_MODEL to its exact name and retain OLLAMA_BASE_URL=http://127.0.0.1:11434. Add ollama to the allowlist. Do not assume a particular Gemma name is installed. The app neither downloads models nor exposes the daemon publicly.

A remote Render backend cannot reach the Ollama daemon on your laptop through loopback. Keep Ollama local; do not open the daemon to the internet to make a hosted selector work. Public baseline should stay disabled-only or use a deliberately configured cloud provider.

### OpenRouter

Set your own OPENROUTER_API_KEY on the backend. OPENROUTER_MODEL defaults to openrouter/free but remains subject to a current catalog match and **zero values in all returned pricing fields** before generation. Add openrouter to the allowlist and retain paid/fallback false. The request disallows provider fallbacks and applies prompt/completion maximum price zero. Catalog/account availability can still reject it; the application does not purchase credits.

Check your own account and [OpenRouter's current limits](https://openrouter.ai/docs/api-reference/limits) and [free routing documentation](https://openrouter.ai/docs/guides/routing/routers/free-router) before a deliberately bounded test. A 401 credential failure is a reason to stop and repair configuration, not repeatedly retry. A 402/429 is not a promise that a zero-price model has capacity. This release makes no such live call.

### OpenAI

The adapter consumes OPENAI_API_KEY and OPENAI_MODEL, with source default gpt-4.1-mini. It deliberately reports unavailable while SUMMARY_ALLOW_PAID=false; merely inheriting a key does not authorize charges. Leave it disabled for this handoff. Any later spending decision and current model/account verification belong to the operator; no paid request is tested or recommended as a default here.

### Gemini and Groq

Set the relevant private API key and a currently supported model ID: GEMINI_API_KEY/GEMINI_MODEL or GROQ_API_KEY/GROQ_MODEL. With paid disabled, the operator must first establish account/model free-tier eligibility and deliberately set GEMINI_FREE_TIER_CONFIRMED=true or GROQ_FREE_TIER_CONFIRMED=true. These flags are declarations, not a billing guarantee or live eligibility query. Do not set them merely to hide an unavailable selector. Review the provider's current terms, quotas and data handling; no account or model is supplied.

## Failure, privacy and caching

Cloud discovery/generation shares at most 25 seconds; local inference has its separate 75-second budget and 768-token output cap. These are source limits, not undocumented environment settings. Responses must complete and match the required structured JSON. Incomplete output, invalid JSON, missing credentials, model/price errors and provider failures leave real YouTube/VADER results available, with safe notices and no saved partial note replacing a complete cached review.

Result keys include source signature, provider/model/configuration and note revision. Actual returned model, safe usage and successful latency metadata are shown where available; a routed model must not be relabeled as the requested router. GET results never generates. There is no implemented automatic fallback; enabling its flag fails configuration.

Cloud summaries send bounded comment/caption excerpts to the chosen provider. Consider privacy and provider terms before enabling them. Captions are optional public English excerpts and may be absent/truncated. Model notes can be wrong; preserve the baseline and inspect the actual source context critically. [All variables](CONFIGURATION.md) · [Troubleshooting](TROUBLESHOOTING.md).
