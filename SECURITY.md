# Security and retention

Keep provider keys and BACKEND_API_TOKEN private and server-side. The browser talks to Next routes; only the server relay forwards the backend token. Production BACKEND_URL requires HTTPS. Ollama configuration accepts loopback HTTP origins only. Public production configuration excludes Ollama and must never point at a laptop.

The API accepts a small allowlisted JSON request, caps samples at 500, bounds network bodies and time, and applies a per-process 20-analysis/minute limit to authenticated callers. This is a single-instance demo limit, not a distributed abuse-prevention service. Public use still consumes YouTube quota; keep hosting/account spending controls in place.

Raw source-cache entries contain video metadata, comment text and optional captions for a logical ten-minute TTL. Author IDs, account names and comment IDs are not retained, but text may contain personal information. Complete aggregate/generated reviews have a thirty-minute TTL. Expired data is purged on cache read/write activity; this is not a background physical-erasure guarantee. There are 100 source and 500 result slots, and each encoded entry is limited to 1.5 MB. Tab session storage retains the displayed result until its expiry. Failed model notes are not persisted as successful reviews.

Render free storage is ephemeral. Restarts, redeploys and idle suspension can lose SQLite results. Cache-miss screens offer a new analysis; GET does not re-run it. Do not export raw comment snapshots or publish private live-test artifacts.

Application logging includes route/method/status/timing only, never request bodies, query strings, authentication headers or exception text. Third-party HTTP informational logging is suppressed by the WSGI entry point. Secret checking covers source and built browser bundles, with exact configured-value matches and known key-prefix detection; it is not a complete security audit.

Report suspected issues privately to the repository maintainer through GitHub private vulnerability reporting if enabled. No specific private reporting endpoint has been verified yet. If a credential is exposed, revoke it privately and replace it; never send it in chat or public issues.

Selecting a cloud model sends bounded comment/caption excerpts to that provider; its data-use terms apply. Local Gemma inference uses the configured loopback daemon. Provider credentials are never supplied as model evidence.


Public WSGI startup validates required backend key/token presence before binding. A configured-but-rejected key remains a sanitized runtime API failure. SQLite failure preserves an uncached baseline with a warning; source reuse/deduplication cannot be guaranteed when storage is unavailable. Public verification tooling is opt-in for live source, bounded, no-redirect and secret-redacting. Its loopback TLS bridge and temporary private key are ignored test infrastructure; never deploy them or copy local trust/test settings to hosting.
