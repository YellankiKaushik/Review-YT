# V2 multimedia publication review — 2026-10-29

The maintainer expressly approved the V2 campaign's visual quality and instructed publication of its five existing outputs, editable source and permitted inputs to YellankiKaushik/Review-YT through a feature-branch PR. This is the authorization for this new multimedia scope; it is distinct from the earlier source-only release decision. It authorizes neither a new GitHub Release nor paid storage/hosting/inference. No signatures, exclusive copyright or additional permissions are invented.

## Reviewed distribution

- Five approved final files: MP4 launch/reel/preview, GIF and PNG thumbnail. The current bytes must match delivery-manifest.json; publication must not reencode them.
- Current-app screenshots/crops and fixture JSON: project visuals already documented in the root asset provenance; ten illustrative comments with6/3/1 counts,60/30/10 shares. There are no actual public comment bodies, account names, live thumbnails, model outputs or runtime datasets. Demo disclosure remains visible.
- Sora and Manrope: original unmodified variable TTFs, copyright notices and full SIL OFL1.1 texts retained beside them. The OFL permits font redistribution under its conditions and video titling; the rendered artwork is not automatically relicensed as font software. [Official OFL FAQ](https://openfontlicense.org/ofl-faq/).
- Original score/effects: deterministic synthesis in scripts/score-v2.py, with no external samples, recordings or cloned voice. This does not assert exclusive copyright in elementary tones or AI-assisted material.
- Editable source/configuration and package lock: eligible project material remains under the root MIT scope. Remotion is referenced as a separately installed tool under its own terms. Current personal/small-company production falls within the documented free-license context; downstream organizations must assess their own eligibility. [Official Remotion license](https://www.remotion.dev/docs/license/pricing).
- Native dependencies, browser binaries, FFmpeg/Sharp/Remotion implementations, raw capture takes and downloaded reference text are not vendored in this PR. Original third-party notices remain untouched. No claim is made that MIT covers all dependencies or generated material.

No specific unresolved included-asset redistribution issue was identified in this scoped review. Root provenance uncertainty and third-party rights remain documented; this is an engineering review, not legal certification. No historical source or assets were consulted/imported. V1 files are preserved locally with their prior hashes and excluded from the V2 public package.

## Storage and privacy

The largest approved file is approximately12.53MiB, below GitHub's50MiB warning and100MiB rejection thresholds. Required WAV inputs are each below13MiB. The new campaign is a bounded multimedia addition to a previously small repository; ordinary Git is appropriate without LFS billing or a Release. [GitHub file limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

The closed promo/.gitignore allowlist includes only reviewed source, required inputs, selected evidence and the five approved outputs. It excludes V1-only sources/media, caches, node_modules, private env files, raw takes, logs, temporary frames, duplicate media and workstation-specific review exports. file-inventory.csv records a pre-commit snapshot of candidate files, type, MiB, tracked/ignored status and publication decision. Excluded local files are not deleted.

Root README is additive: an animated fixture-labeled preview and links to real branch files. No retired app-demo URL, deployment change, public API call, core behavior change, Release, automatic merge or force-push is part of this task.

## Observed publication checks

The approved media were not regenerated or reencoded: all five output hashes and27 required-input hashes match the production manifests. FFprobe/full-file media decoding, thumbnail/GIF geometry, promo TypeScript, composition registrations, media provenance and README/documentation links pass. A fresh Git-index export with a clean promo npm install passes type checking, all27 input/five final hashes and all four composition registrations with zero local V1 files present. The package therefore does not depend on excluded captures or legacy source.

The broad application run passed138 Python tests,51 frontend tests and42 browser tests (231 total), lint/types, production Next build, independent Python package build and pip check. Root npm audit then reported the pre-existing high-severity Zod advisory GHSA-mrhx-c7xc-m3w5 in unchanged apps/web zod4.3.6; the root lockfile/package remain identical to main. Promo npm audit reports zero vulnerabilities. No audit or workflow was weakened. The PR must report actual CI status and should not merge until the application dependency advisory is resolved in an authorized dependency fix. This campaign-only task does not change core application dependencies.

After the stopped pipeline, release-config, documentation, source-inventory and secret/history checks passed independently. No configured secret values, unexpected env files or public secret variables were found. Original retained notices are preserved verbatim. Git diff whitespace checks pass; upstream OFL bytes and the approved CRLF fixture have narrow attributes so cross-platform checkout preserves their hashes.
