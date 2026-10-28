# V2 final production QA

Local review completed 2026-10-29 (Asia/Calcutta). Source commit: `51faf1cc7f4aa84f9079bc247005f38056cdb6a4`. No commits, pushes or uploads were made.

## Delivered media

| File | Duration | Size | Video / audio | Bytes | Result |
|---|---:|---|---|---:|---|
| review-yt-youtube-1080p.mp4 | 70.000s | 1920×1080,30FPS | h264/yuv420p; aac stereo 48kHz | 13139233 | Full decode PASS; fast-start PASS |
| review-yt-reel-vertical.mp4 | 30.000s | 1080×1920,30FPS | h264/yuv420p; aac stereo 48kHz | 5254146 | Full decode PASS; fast-start PASS |
| review-yt-github-preview.mp4 | 8.000s | 960×540,30FPS | h264/yuv420p; silent, no audio stream | 699809 | Full decode PASS; fast-start PASS |
| review-yt-github-preview.gif | 8.000s | 960×540,15FPS | 192-color palette optimization; 120 frames, infinite loop | 3796647 | Full FFmpeg decode PASS; contact sheets reviewed |
| review-yt-thumbnail.png | Still | 1280×720 | PNG, RGB | 330001 | Native visual inspection PASS |

The three MP4s contain 2,100 +900 +240 =3,240 decoded video frames. Every file was inspected with FFprobe; FFmpeg decoded the entire file with error-free exit status. No black intervals met the configured detector threshold. The loop returns to the same authored state; first/last compressed-frame mean absolute difference is 0.788 on a 0–255 channel scale. This is a continuity measurement, not a claim of byte-identical compressed frames.

## Actual production and verification commands

From the project root: `node promo/scripts/capture-v2.cjs`. From promo: `npm run typecheck`, `npm run frames`, `npm run rough`, `npm run render:all`, then affected `npm run render:youtube`, `npm run render:reel` and `npm run render:github` after inspected corrections. `npm run qa` runs TypeScript, fixture/hash validation, FFprobe/full-decode review extraction and measured audio checks. `npm audit --workspaces=false` reports zero vulnerabilities after the patched Sharp and Zod override. Root `.venv/Scripts/python.exe scripts/secret_check.py --history` passed; the exact value/prefix scan records counts only in secret-check-v2.json. No application test totals are invented; the app was not modified, rebuilt or architecturally retested for this video-only task.

## Art-direction review and corrections

Stage A: rendered and inspected comment opening, product reveal, chart, responsive transition, CTA, vertical proof and thumbnail. Corrected clipped screenshot labels and inaccurate cursor target positions. Stage B: rendered the complete 960×540 rough cut before the 1080p render; inspected its scene contact sheets. Stage C: removed reveal-copy/mobile-text collisions, captured the real preparing state, moved vertical fragments below the headline, added a product push-in, category timing, data-flow pulses and setup progress. Final encoding initially reported yuvj420p; the export now explicitly produces limited-range yuv420p, correct frame counts and fast-start. Final audio gain was adjusted after measurements. Its video packets are unchanged by the audio-only remux; video-stream-integrity.json verifies both hashes.

Stage E: inspected all seven final native contact sheets, critical full-resolution chart/hook/CTA frames, two engine overview sheets and all eight landscape transition strips. Retained evidence is in references/qa/. Black padding in an incompletely filled contact sheet is layout padding, not a frame from the film. The engine picture review preceded the final audio-only gain adjustment; packet identity verifies the picture sequence remained unchanged, and the native final-file frames were regenerated afterward.

## Detector candidate classification

Input pause around23.4–25.9s is intentional reading of the populated URL/defaults. Category/data holds around32.5–36.2s and13.5–16.4s in the reel allow the fixture values to be read. The architecture composition around51.4–58.8s holds the diagram while small data pulses and the optional branch animate; the global freeze threshold misses that localized motion. Setup around60.3–63.8s holds repository identity while step focus/progress changes. Final CTA holds from66.1s/27s are intentional and meet the two-second reading requirement. These are low-motion candidates, not missing or corrupt frames. No unintended full-file freeze was found in the reviewed evidence. Masked intermediate headline frames and deliberate focal crops are expected transitions; the settled copy, final chart values and CTA are legible.

## Audio

Original code-synthesized music and UI/transition effects; no external recordings, voices or paid services. Landscape integrated loudness −18.3 LUFS, true peak −2.5dBFS; reel −21.0 LUFS, true peak −2.6dBFS. Exact summaries and silence candidates are in audio-qa-v2.json. No clipping; silent GitHub preview has no encoded audio stream. No spoken narration exists, so no dialogue/SRT was fabricated. These are measured checks; no human listening approval is claimed.

## Product accuracy, privacy and provenance

Two genuine visible form submissions per final capture take used the explicit offline fixture, sample10, provider disabled. Browser page errors0, unexpected external requests0. Results route and accessible chart label were checked. No live YouTube/model request occurred. All result footage discloses DEMO DATA. VADER is the baseline; optional AI is diagrammed separately and not portrayed as generated. Fixture values match the approved source exactly. All27 required inputs have hashes and provenance in asset-manifest.json. V1 source and three original output files are preserved. Root app dependencies, curated screenshots and legal files remain unchanged. No credentials are embedded or needed to rerender.

## Limits and user review

All required campaign deliverables are completed locally. These are illustrative product demonstrations, not live API evidence or a new deployment. Visual review sampled the declared frames/boundaries; full decoding covers every frame but does not constitute human creative approval. Windows/Node24 was the tested production environment. Remotion license eligibility and third-party distribution conditions are described in asset-attribution.md; no paid license or universal rights clearance is invented. The user can watch all final files before deciding to publish. No publication is automated.

Final cleanup verified: review-v2/ and render masters removed by the engine cleaner; all five V2 finals and three V1 deliverables preserved. Required input hashes and V1 output hashes were rechecked after cleanup. The final secret/history scan checked780 source/nonignored files,524 reachable blobs and25 browser artifacts with zero matches. delivery-manifest.json records final SHA-256 hashes.
