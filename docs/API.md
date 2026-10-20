# API contract — review-yt/v1

Backend routes require `Authorization: Bearer <private backend token>` except `/health`. Browser callers use the same-origin Next relay; the browser never receives that token or provider keys. JSON errors have the shape `{"error":{"code":"...","message":"..."}}`. Authentication failure is 401; missing backend configuration is 503. Response bodies contain no credential values.

## Operations

- `GET /health`: process liveness and contract name, no upstream API request. This does not establish valid YouTube/cloud credentials.
- `GET /api/providers`: `selectionDefault`, an `options` array with id/configured/model/execution/description, and constraints.paid/automaticFallback. Ollama inventory discovers installed model names; cloud configured status does not prove inference availability. Production's allowlist excludes local Ollama.
- `POST /api/analyze`: JSON object with `video` (supported public URL or ID), `sample` (integer 1–500, default 10), and optional `provider` (an allowed inventory id). Unknown fields, booleans as sample counts and invalid provider/URL input are rejected with 400. A fresh source lookup retrieves metadata and top-level comments through the official YouTube API. No browser-provided key/model/endpoint is accepted.
- `GET /api/results?video=VIDEO_ID&provider=PROVIDER_ID`: retrieves only a valid saved review for that video/provider. It never retrieves new comments, calls a model or triggers analysis. An expired/missing result is 404 and offers a new form submission.

The maximum JSON request is 4096 bytes. POST analysis requests have a 20/minute per-process/client-address limiter; requests relayed by Next can share a backend address. This single-instance control is not a distributed quota system. Input errors use typed safe messages; upstream exception bodies and URLs are not reflected.

## Review envelope

A successful analysis has schema=`review-yt/v1`, a video object (id/title/channel/published/thumbnail), `sampled` (actual retrieved count), `sentiment` (totals/shares/classifier), `sourceDigest`, `warnings`, `created`, `ai`, and `caching` (reused/validUntil). The frontend's Zod schema checks the fields, real counts and arithmetic consistency. Percentage rounding may differ from exactly 100 by a small rounding amount.

AI metadata identifies requested provider/model and the actual returned model, execution mode, elapsed successful inference time, safe token counters, prompt revision and attempt count. Complete structured fields are `commentDigest`, `captionDigest`, `creatorNotes`. Complete means the provider finished and its structured response was accepted; it is not a guarantee of factual or semantic accuracy. Caption notes summarize only included excerpts, not an entire video when truncated. Shortened input is disclosed in warnings.

Optional model errors, payment-required, rate limiting, incomplete output, missing credentials and invalid model JSON retain the genuine metadata/sentiment with ai.status=`unavailable` and a safe notice. Such notes are not saved as successful results. No hidden provider retry/fallback occurs. ActualModel can remain available after an incomplete response, but no unfinished content is shown. Disabled mode has no model request.

Sources have their own ten-minute bounded cache. Complete provider-specific results have thirty-minute entries keyed by the source signature, selected model/configuration and note revision. Changing the caption setting changes the source key. Browser tab retention is versioned and provider-specific and does not create a new analysis on reload. See SECURITY.md for physical-retention and ephemeral-hosting limits.
