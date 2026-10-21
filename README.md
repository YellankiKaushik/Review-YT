# Review-YT — the audience notebook

A new requirements-based implementation in a separate source tree. It retrieves actual YouTube comments, displays a VADER sentiment spectrum, and optionally generates attributed research notes. AI failures leave the metadata and sentiment usable. No historical source, tests, assets, configuration files or Git objects were intentionally imported.

**Publication gate: BLOCKED pending the recorded maintainer rights/license decision in [the final checklist](docs/FINAL_PUBLICATION_RIGHTS_CHECKLIST.md).** See [the independence audit](docs/INDEPENDENT_IMPLEMENTATION_AUDIT.md). This is not a strict clean-room certification: earlier conversation context exposed the implementing assistant to historical code.

## Run locally

Use Node 24 and Python 3.12 (local verification used 3.12.14; CI/Render target the current security patch 3.12.15).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci
if (!(Test-Path .env)) { Copy-Item .env.example .env }
if (!(Test-Path apps/web/.env.local)) { Copy-Item apps/web/.env.example apps/web/.env.local }
```

Configure `YOUTUBE_API_KEY` and a random, private `BACKEND_API_TOKEN` in root `.env`. Put the same backend token in the web `.env.local`, with `BACKEND_URL=http://127.0.0.1:5100`. Keep all files private. Already configured local files must not be overwritten by the copy commands.

```powershell
.\.venv\Scripts\python.exe apps/api/serve.py
# A separate terminal:
npm run dev
```

For safe Windows background start/check/stop commands, use [the local startup guide](docs/LOCAL_STARTUP.md).

Open http://127.0.0.1:3200. These ports keep the historical app on 3000/5000 intact. On POSIX use `.venv/bin/python` for Python commands. Cloud production uses Vercel for `apps/web` and Render for the Flask API; see [deployment gates](docs/DEPLOYMENT.md).

## Features and boundaries

- Supported YouTube watch, Shorts, short-link, live and embed forms, plus raw video IDs.
- Official Data API metadata and paginated top-level comment retrieval, bounded to 500 comments. No fake source or authorship claims.
- VADER positive/neutral/negative counts and honest sample percentages; English lexicon limitations are displayed.
- Optional Ollama, OpenRouter, OpenAI, Gemini and Groq. Paid inference and automatic fallback are off by default. OpenRouter validates all catalog price fields before generation. Gemini/Groq require explicit free-tier confirmation; OpenAI requires paid authorization and is not used in this verification.
- One bounded AI request per analysis, strict structured-note parsing, actual returned model/usage, and suppression of unfinished or invalid notes.
- Optional public captions via the package extra and `TRANSCRIPTS_ENABLED=true`; unavailable captions are a normal state. This is not an access-control bypass.
- Authenticated Flask API, same-origin Next relay, rate limits and server-only credentials.
- Source entries last ten minutes; complete results last thirty minutes. SQLite is ephemeral on Render free hosting. Cache-only GETs do not generate or fetch source data.
- No account identifiers or comment authors are saved. Comment text can still contain personal data; see [retention/security](SECURITY.md).

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\ruff.exe check packages apps tests scripts
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
.\.venv\Scripts\python.exe -m build packages/review_yt_core --outdir artifacts/package
.\.venv\Scripts\python.exe scripts/secret_check.py
```

Browser CI uses its own explicit fixture API on 5101 and Next app on 3201. It does not use the live keys or claim real cloud generation. See `FINAL_REVIEW_YT_RELEASE_REPORT.md` for actual results and remaining gates. Run the complete local check sequence with `.venv/Scripts/python.exe scripts/verify.py` on Windows or `.venv/bin/python scripts/verify.py` on POSIX.

For local caption notes, set `TRANSCRIPTS_ENABLED=true` in private root configuration and restart only this backend. The real local verification enabled it; the committed template and Render configuration keep the optional integration disabled by default. Caption excerpts are bounded and missing public captions are a normal state. API request/result details are in [docs/API.md](docs/API.md).
