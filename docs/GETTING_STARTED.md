# Getting started

You will run a Next.js dashboard and a Python/Flask backend on your own computer. Real analyses use **your own** YouTube API key. The maintainer's former hosting and credentials are retired; none are needed or supplied here. For offline tests you need no API credentials.

## 1. Install and check prerequisites

Install Git, Python 3.12 and Node.js 24 (includes npm) from their official distributions. CI uses Python 3.12.15 and Node 24. The core declares Python >=3.11 and npm Node >=22; other full-stack versions are not certified by that declaration.

```bash
git --version
python --version
node --version
npm --version
```

On Linux/macOS use `python3.12 --version` if `python` is absent. On Windows `py -3.12 --version` uses the Python launcher; if unavailable, use the verified `python` executable instead. Reopen the terminal after installing software so PATH updates apply.

## 2. Clone and install

```bash
git clone https://github.com/YellankiKaushik/Review-YT.git
cd Review-YT
```

Windows PowerShell, from this root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
npm ci
```

Linux/macOS:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
npm ci
```

No activation is required when using the explicit Python path. Python installs the local core plus backend/test dependencies. `npm ci` uses the **root** workspace lockfile; do not install separately under `apps/web`. Expected: both installation commands exit successfully. Network access to package registries is required.

## 3. Obtain a key and a private shared token

Follow [YouTube API setup](YOUTUBE_API_SETUP.md): create your own Google Cloud project, enable YouTube Data API v3 and create/restrict its key. No OAuth login is implemented for this public-comment workflow.

Generate a new 32-byte random backend token locally:

```powershell
# Windows
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(32))"
```

```bash
# Linux/macOS
.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

The generated token is private: copy it only into the two local files below; do not post the terminal output. This command generates a new value, never reads an existing credential.

## 4. Create the two private configuration files

Windows:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
if (!(Test-Path apps/web/.env.local)) { Copy-Item apps/web/.env.example apps/web/.env.local }
```

Linux/macOS:

```bash
test -f .env || cp .env.example .env
test -f apps/web/.env.local || cp apps/web/.env.example apps/web/.env.local
```

These commands do not overwrite existing private files. Open them in your local editor. In root `.env`, fill the empty `YOUTUBE_API_KEY` and `BACKEND_API_TOKEN`. Keep `HOST=127.0.0.1`, `PORT=5100`, `SUMMARY_PROVIDER=disabled`, `SUMMARY_ENABLED_PROVIDERS=disabled`, `SUMMARY_ALLOW_PAID=false` and `SUMMARY_FALLBACK_ENABLED=false`.

In `apps/web/.env.local`, set `BACKEND_URL=http://127.0.0.1:5100` and **exactly the same** `BACKEND_API_TOKEN`. Do not put a YouTube/provider key in this frontend file. Both files are ignored by Git. See [configuration](CONFIGURATION.md) for defaults, precedence and optional settings. Restart the affected server after changing a file; inherited process variables take precedence.

## 5. Start both servers

### Windows: guarded background lifecycle

```powershell
powershell -NoProfile -File scripts/start-local.ps1
powershell -NoProfile -File scripts/check-local.ps1
```

The scripts verify configuration without printing values, refuse unrecorded listeners, start this project's servers and wait for health and authenticated inventory through the relay. Expected check: health, homepage, backend inventory and frontend proxy HTTP 200; paid/fallback false. Read [lifecycle ownership and shutdown](LOCAL_STARTUP.md).

Alternatively run `.\.venv\Scripts\python.exe apps/api/serve.py` in terminal 1 and `npm run dev` in terminal 2, both from the root.

### Linux/macOS: two terminals

Terminal 1, repository root:

```bash
.venv/bin/python apps/api/serve.py
```

Terminal 2, repository root:

```bash
npm run dev
```

The backend runs Waitress on loopback 5100; Next prints its ready message for port 3200. Open **http://127.0.0.1:3200/**. Backend **http://127.0.0.1:5100/health** should return status `ok` and contract `review-yt/v1`. Health alone does not prove the YouTube key is valid.

## 6. Run and interpret a real analysis

Paste a public YouTube URL or video ID, select **10 comments** for an initial bounded check, keep sentiment-only selected and submit. Successful retrieval opens `/review/VIDEO_ID`, showing the real video title/channel, actual sample count and VADER chart. The number returned may be below the requested limit; disabled/empty comments produce an honest notice and may yield no sentiment sample. Labels/counts correspond to the retrieved sample, not the video's entire audience.

Positive, neutral and negative percentages describe VADER's estimates. They are not fact-checks, model accuracy scores or measures of every viewer's opinion. AI notes are separate and optional. Reload/deep links read saved results; a missing/expired cache offers a new explicit analysis rather than fetching silently. Avoid repeated submissions: each fresh source retrieval uses your quota.

## 7. Stop safely

For guarded Windows startup:

```powershell
powershell -NoProfile -File scripts/stop-local.ps1
```

For manually started Windows/POSIX services, press **Ctrl+C in each terminal**. Do not kill all Python/Node processes or remove the lifecycle state while servers are running. The scripts manage only verified project processes, not Ollama or another application.

## Offline contribution checks

Do not create private environment files for offline testing. If already configured, use an isolated clean checkout to prevent unrelated inherited credentials from affecting diagnostics. Install Chromium once, then run:

```bash
npx playwright install chromium
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
```

Windows: `.\.venv\Scripts\python.exe scripts/verify.py`; POSIX: `.venv/bin/python scripts/verify.py`. It includes Python/Flask tests and all release checks. On Linux Chromium may also need OS libraries: CI runs `npx playwright install --with-deps chromium` on its isolated runner; installing system packages locally may require administrator rights.

## If setup fails

| Symptom | First action |
| --- | --- |
| Python/npm not found | Verify installed versions/PATH; reopen your terminal. |
| Missing Python module | Re-run pip through this project's explicit `.venv` Python, from the root. |
| Missing workspace package | Run root `npm ci`; preserve the committed lockfile. |
| Missing key or token | Fill the two ignored files; restart the affected process. Never paste values into diagnostics. |
| Token mismatch / HTTP 401 | Make the two private tokens identical; check inherited overrides, then restart both services. |
| Port already used | Identify its owner. The guarded scripts intentionally refuse to stop unknown processes. |
| Backend connection failure | Check 5100 health, server logs privately and the exact loopback BACKEND_URL. |
| Missing saved result | Cache expiry is normal; submit a new analysis deliberately. |

[Full troubleshooting](TROUBLESHOOTING.md) · [Self-hosting](SELF_HOSTING.md).
