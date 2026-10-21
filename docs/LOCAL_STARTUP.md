# Windows local services

From this repository root, run `powershell -NoProfile -File scripts/start-local.ps1`.
The script uses this tree's `.venv/Scripts/python.exe` and installed Next CLI, binds
only loopback ports 5100/3200, waits for readiness, and checks authenticated inventory
through both Flask and the frontend relay. Repeating start does not create duplicates.
Use `powershell -NoProfile -File scripts/check-local.ps1` to check status, and
`powershell -NoProfile -File scripts/stop-local.ps1` to stop these services.

First installation: Python 3.12, Node 24, `python -m venv .venv`,
`.venv/Scripts/python.exe -m pip install -r requirements-dev.txt`, then `npm ci`.
Copy the example environment files only when private files do not already exist.
Privately set root `YOUTUBE_API_KEY` and `BACKEND_API_TOKEN`; set the matching token
and `BACKEND_URL=http://127.0.0.1:5100` in `apps/web/.env.local`.
Process variables take precedence over dotenv files. The checker reports presence,
token equality and safety flags only; it never prints secret values.

The startup script pins local ports, loopback binding, paid/fallback false, and uses
`.next-local` to isolate its runtime output from production builds. It does not change
private files. Logs are ignored `artifacts/local-managed-*.log`; inspect privately.
Launcher PID, creation timestamp, executable name and exact project command marker
are saved in ignored `.work/local-services.json`. Stop verifies these before stopping
launchers and their descendants, with creation-time checks against PID reuse.
Unknown port listeners or changed process identities cause a refusal; no unrelated
process is stopped. Do not remove the state file while servers run. If it is lost,
inspect the listener and its command line manually; the scripts do not adopt or kill
unrecorded processes. An exclusive workspace file lock prevents concurrent start/stop operations; a second invocation refuses while one is active.

These are session-independent background servers, not a Windows boot service.
Shutdown, logoff, terminal-host cleanup or process termination can stop them. Run start
again after restarting Windows. Neither the old project's 3000/5000 nor Ollama is managed.
Frontend: http://127.0.0.1:3200/ ; backend health: http://127.0.0.1:5100/health .


## Isolated optimized-production verification

Run `powershell -NoProfile -File scripts/test-production-local.ps1` from this root. It builds the optimized app, starts actual Waitress/Next production on5102/3202 with a local trusted TLS bridge5103, tests real HTTP/auth/error paths and stops only its own verified process trees. It does not use REVIEW_LOCAL_TEST or change the working development services/private files. OpenSSL must already be installed (PATH or Git for Windows bundle); no model or infrastructure is downloaded. Default has no live YouTube/AI work; -LiveYouTube opts into a bounded ten-comment source and one browser cache reuse. -SkipBuild is only for a build matching current source. See the Vercel handoff for full commands, temporary TLS trust and eventual public checks.
