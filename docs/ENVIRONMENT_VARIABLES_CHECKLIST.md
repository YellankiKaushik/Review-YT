# Environment checklist

See [Configuration](CONFIGURATION.md) for every implemented variable/default and [Getting Started](GETTING_STARTED.md) for copying examples. Every operator supplies their own credentials; the maintainer's dedicated Google/OpenRouter credentials were revoked by their owner and are not available for reuse.

## Local

- [ ] Root .env and apps/web/.env.local copied only if absent; both ignored.
- [ ] Own YOUTUBE_API_KEY in backend file, not frontend.
- [ ] New cryptographically random BACKEND_API_TOKEN matches in both files.
- [ ] BACKEND_URL=http://127.0.0.1:5100 for Next development.
- [ ] HOST=127.0.0.1; PORT=5100; writable CACHE_PATH.
- [ ] SUMMARY_PROVIDER=disabled; SUMMARY_ENABLED_PROVIDERS=disabled.
- [ ] SUMMARY_ALLOW_PAID=false; SUMMARY_FALLBACK_ENABLED=false; captions off initially.
- [ ] No inherited stale process override; restart after editing configuration.

## Your own backend host

- [ ] Own key/token in private environment, public bind HOST=0.0.0.0, provider-assigned PORT.
- [ ] Python pin/root/build/start agree with render.yaml if using Render.
- [ ] Writable cache path with understood temporary retention/ephemeral storage.
- [ ] Paid/fallback false, sentiment-only allowlist; no laptop Ollama URL.
- [ ] Public startup refuses missing key/token; a present key is not proof of validity.

## Your own Next host

- [ ] Actual HTTPS backend origin, no path/query/user info.
- [ ] Exact matching private BACKEND_API_TOKEN, server-only.
- [ ] No NEXT_PUBLIC_ secrets, no backend provider keys in frontend configuration.
- [ ] Local trust/test/dist flags unset; platform manages NODE_ENV.
- [ ] Environment changes followed by a new deployment/restart.

## Test-only settings

Offline tests inject fixtures and private synthetic shared tokens; they require no real key. Windows optimized verification uses isolated ports 3202/5102/5103 and temporary loopback TLS trust. Do not copy its temporary certificate/key or local flags onto a host. Production code's required-credential and HTTPS checks remain intact. The public smoke script only uses origins explicitly supplied by an operator; this release never tests or restores retired destinations.
