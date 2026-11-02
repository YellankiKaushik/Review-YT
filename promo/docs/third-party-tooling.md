# Third-party production tooling notices

The campaign folder is a private, separately versioned production package. Its `package-lock.json` pins tools for rendering and QA; the root lockfile separately pins the Review-YT application. Running `npm ci --workspaces=false` inside `promo/` downloads these tools from npm into the operator's local `node_modules`. This repository does not commit those dependency binaries.

## Remotion 4.0.539

Remotion package metadata identifies its own Remotion License (the license text is packaged by the upstream npm distribution). Remotion states it is proprietary/source-available, not OSI open source. The official terms allow individuals and organizations or teams of up to three people to use the Free License, including commercial use subject to the terms; others require a Company License. Users must assess their own eligibility before using the renderer. The repository's MIT grant does not relicense Remotion.

- [Remotion license FAQ](https://www.remotion.dev/docs/license/faq)
- [Remotion terms](https://www.remotion.dev/docs/terms)

## FFmpeg static 5.3.0

`ffmpeg-static` is a development dependency that downloads a platform FFmpeg binary for render normalization and GIF generation. Its package metadata declares GPL-3.0-or-later. FFmpeg's upstream licensing page explains that FFmpeg is LGPL by default, but optional GPL components make the binary GPL; upstream also identifies libx264 as GPL. The campaign's H.264 encode uses the binary supplied by the package. No FFmpeg executable or source is committed here. Anyone who redistributes that binary must follow the applicable FFmpeg/libx264 licenses and provide corresponding source/notices as required. The encoded MP4 outputs do not contain the FFmpeg executable.

- [FFmpeg license and legal considerations](https://ffmpeg.org/legal.html)
- [FFmpeg x264 documentation](https://ffmpeg.org/general.html#x264)
- [ffmpeg-static package](https://www.npmjs.com/package/ffmpeg-static)

## Sharp and libvips

Sharp 0.35.5 is used by local media-inspection scripts. Upstream sharp is Apache-2.0; its optional prebuilt libvips packages carry LGPL-3.0-or-later metadata, with platform wrappers indicating combined Apache/LGPL terms. npm selects platform-specific packages when installed; these binaries are not committed here. Preserve upstream notices and review the exact selected platform package before redistributing any installed dependency.

- [Sharp license](https://github.com/lovell/sharp/blob/main/LICENSE)
- [sharp-libvips third-party notices](https://github.com/lovell/sharp-libvips/blob/main/THIRD-PARTY-NOTICES.md)

## Other assets

Sora and Manrope font files retain their upstream SIL OFL 1.1 license texts in `promo/public/fonts/`. Original procedural music is project source, not an external recording. Keep root `NOTICE` and all upstream license files intact. This inventory is informational, not legal advice or a substitute for reviewing the exact package and platform binary that an operator installs.
