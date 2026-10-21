# Your own YouTube Data API key

Review-YT's backend uses the official YouTube Data API v3 to retrieve public video metadata and top-level comment threads. It does not scrape private videos or use the original maintainer's account. Every operator supplies their own project/key. Offline tests use injected fixtures and need no key.

## Create and enable

1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/) with your own account.
2. Use the project selector to create a project or select one you control. Verify its name before changing settings.
3. Open **APIs & Services → Library**, find **YouTube Data API v3**, then **Enable**.
4. Open **APIs & Services → Credentials → Create credentials → API key**. Store the generated value privately.
5. Edit the key. Under **API restrictions**, restrict it to **YouTube Data API v3** and save.

Google's [API overview and setup instructions](https://developers.google.com/youtube/data/getting-started) describe the current flow. This application reads public resources using an API key; it has no account OAuth flow. Account verification/eligibility requirements may differ; follow what your Console actually shows.

## Restrict the actual caller

The caller is **Flask on your backend**, not the visitor's browser. Browser HTTP-referrer restrictions are therefore not appropriate for this backend key. When the hosting setup has stable documented outbound IP addresses, consider server-IP restrictions covering those egress addresses. Local dynamic connections, proxies and different hosting plans can have different outbound behavior. Do not guess a Vercel frontend IP or hostname as the backend's egress restriction.

Always retain the YouTube-only API restriction. If stable-IP restrictions are unavailable, keep the key server-only, limit access, monitor usage and review the actual host's options. Google's [API key restriction guide](https://docs.cloud.google.com/api-keys/docs/add-restrictions-api-keys) explains client and API restrictions. A mismatched restriction rejects requests; do not work around it by exposing the key in the frontend.

## Configure and restart

Copy root `.env.example` to ignored `.env` only if no private file exists. Put your key in `YOUTUBE_API_KEY` using a local editor. Also configure the shared token as described in [Getting Started](GETTING_STARTED.md). Never commit the key, include it in a URL sent to others, or use a `NEXT_PUBLIC_` name.

Restart the backend after a change. Guarded Windows setup uses `scripts/stop-local.ps1` followed by `scripts/start-local.ps1`; manual setup uses Ctrl+C and the original start commands. On a host, save its private environment settings and restart/redeploy. Process variables override dotenv; a stale inherited value can override the edited file.

## Quota and cost

The API is quota-limited, not unlimited. Check your project's **APIs & Services → YouTube Data API v3 → Quotas** and usage. The application uses `videos.list` and paginated `commentThreads.list`; additional pages and invalid requests can consume quota. It does not search for videos. A ten-comment first check keeps retrieval small; valid caches reduce repeat work.

Use Google's current [quota cost table](https://developers.google.com/youtube/data/determine_quota_cost) and [quota/compliance audit guidance](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits) for allocations, reset times and requests for additional capacity. Do not assume billing automatically buys unlimited YouTube quota. A Cloud account may have other billable services; review current Google terms and your own project settings before enabling resources. This project does not provision billing or credentials.

## Confirm real retrieval

Start the configured services, open your own local/deployed frontend and submit one public video with **10 comments**, sentiment-only. Successful analysis shows the genuine title/channel, actual retrieved sample and counts. `/health` only proves liveness; a configured-provider inventory does not validate the YouTube key. Do not post keys or comment bodies as evidence.

| Result | Meaning / action |
| --- | --- |
| `youtube_not_configured` / 503 | Backend has no key; configure your own and restart. No real API call or demo substitution occurs. |
| `youtube_rejected` / 502 (or 404) | Upstream rejected the resource: check API enabled status, key validity/restrictions and Google Console privately. The app intentionally hides upstream credential-bearing details. |
| `video_unavailable` / 404 | Video is missing, private or unavailable; use a genuinely public video. |
| `comments_disabled` warning | The collector preserves available metadata and returns an empty comment sample with a warning when comments are disabled. It does not fabricate comments. |
| `comments_empty` warning | No usable top-level comments were retrieved; an empty sample has no meaningful sentiment percentage. |
| `youtube_quota` / 429 | Quota/rate capacity is unavailable; inspect your Console and wait for reset or follow the official quota process. Do not spam retries. |

Disabled comments are handled as a warning in the complete collection workflow; they are not promised as an HTTP 409 analysis error. Only a deliberate successful operator-run analysis validates a new credential. No live verification with the maintainer's revoked keys is part of this source-only release.
