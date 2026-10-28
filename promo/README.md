# Review-YT V2 campaign

The maintainer-approved **From noise to signal** campaign uses genuine application captures with clearly labeled illustrative results. No live YouTube/provider requests or retired hosted demo are involved. The original application, legal notices and V1 files are preserved.

## Approved deliverables

- [YouTube launch film](output/review-yt-youtube-1080p.mp4): 70s,1920×1080,H.264/AAC
- [Vertical reel](output/review-yt-reel-vertical.mp4): 30s,1080×1920,H.264/AAC
- [Silent README MP4](output/review-yt-github-preview.mp4): 8s,960×540
- [Palette-optimized GIF](output/review-yt-github-preview.gif): 8s,960×540,about3.6MiB
- [Thumbnail](output/review-yt-thumbnail.png):1280×720

All five are ordinary Git files below50MiB. No LFS, Release upload, paid storage or cloud deployment is configured. V1 sources/outputs remain local and ignored; this V2 PR does not redistribute the rejected earlier film. The production scripts never publish anything themselves.

## Install the isolated production project

Use Node.js24/npm. From the repository root:

```bash
cd promo
npm ci --workspaces=false
```

The promo lockfile is authoritative for this isolated package; the root application's lockfile remains authoritative for the application. The included PNGs, two original WAV scores, local OFL fonts and fixture JSON are sufficient to render without app startup, private configuration or API keys.

## Inspect, render and verify

Run from promo:

```bash
npm run typecheck
npm run verify:media
npm run validate
npm run studio -- --no-open --port=3333
npm run render:youtube
npm run render:reel
npm run render:github
npm run render:thumbnail
npm run render:all
npm run qa
```

`validate` bundles the project and checks registered compositions without rendering a film. The renderer uses the existing Playwright headless shell on Windows when available (`npx playwright install chromium --only-shell` installs it). Otherwise Remotion resolves/downloads its supported platform Chromium on the first render/validation. Linux may need system Chromium libraries; see [Remotion's Linux dependencies](https://www.remotion.dev/docs/miscellaneous/linux-dependencies). An operator may set `REMOTION_BROWSER_EXECUTABLE` to an already installed compatible browser path. No developer's absolute path is hardcoded. Windows hidden-window handling affects only the renderer's owned Chrome process. Windows is the verified full production platform; other OS support is documented, not claimed as a completed cross-platform render test.

`render:all` creates all five outputs. `render:github` also makes the palette GIF. `frames` generates representative design PNGs; `rough` renders the optional half-resolution edit. Encoding explicitly produces30FPS limited-range yuv420p H.264, fast-start MP4 and AAC for the two sound films. The procedural score has a measured+5.5dB mix adjustment. Re-rendering overwrites the named outputs: copy approved media elsewhere before experimenting. No re-render was needed or performed for publication.

`verify:media` is read-only: it checks all27 required inputs and all five approved output SHA-256 values against committed manifests. Optional local V1 files are checked if present. `qa` also checks the approved fixture, TypeScript, full-file decoding, media specifications, GIF/thumbnail geometry and measured audio. New runtime evidence goes to ignored review-v2/, leaving the approved production report unchanged. A changed render requires a new visual review and intentional manifest update; a passing decoder is not automatic artistic approval.

## Source and evidence

- [Root composition](src/Root.tsx),src/compositions/,src/components/,src/themes/ and src/data/ contain editable React/TypeScript and shared frame-driven motion.
- public/v2/ contains only the required genuine UI crops and original synthesized audio; public/fonts/ retains both original font files and their OFL texts. There is no separate assets/ directory.
- scripts/ contains the renderer, encoder, GIF maker, capture, score synthesis and verification tools.
- [Creative direction](docs/creative-direction.md),[storyboard](docs/storyboard.md),[production QA](docs/qa-report.md),[asset attribution](docs/asset-attribution.md),[publication review](docs/publication-review.md) and [file inventory](docs/file-inventory.csv) record scope and evidence.
- Curated final contact sheets are retained under references/qa/. Individual temporary frames, raw takes, downloaded reference copies and unused duplicate images remain local and excluded.

## Recreate UI or audio inputs

Captures are already included. To recapture, follow the root app's build/install instructions, then run `node promo/scripts/capture-v2.cjs` from the repository root after installing promo dependencies. It owns only loopback port3214, refuses an occupied port, uses explicit offline fixture routes/original artwork, blocks external requests, and stops its server. It changes promo capture inputs, never docs/assets or private env files. Browser screenshots and the form preparing state are real UI; responses are fixtures, not live feedback. Review/reapprove changed assets before publishing.

The WAV scores are included. To synthesize them again, use Python3.12 with `python promo/scripts/score-v2.py` from the repository root (Windows may use `.venv/Scripts/python.exe`; POSIX `.venv/bin/python`). Only the standard library is used. There is no narration or invented dialogue subtitle file.

The approved media use project artwork, unmodified OFL fonts and original coded sound, not stock footage or public comment datasets. Root MIT scope does not relicense fonts, Remotion or third-party tools. See the retained [asset attribution](docs/asset-attribution.md) and the upstream terms before using the toolchain in a different organization or redistributing dependency binaries.
