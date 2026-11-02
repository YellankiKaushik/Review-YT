# Final GitHub Consolidation Report

**Repository:** [YellankiKaushik/Review-YT](https://github.com/YellankiKaushik/Review-YT)  
**Report date:** 2026-11-02  
**Functional release commit:** `6d08d088e42933e494899faf6bc03c6805c17480` (normal merge commit for PR #4)  
**Report delivery:** documentation-only follow-up PR #6, subject to its own required checks and normal merge.

## Executive status

The Zod security fix and the V2 campaign are merged to `main`. The campaign's factual sample-limit and render-normalization defects were fixed, the affected videos were regenerated and fully verified, review conversations were resolved, and the latest `main` push workflow passed. One active repository ruleset named **Protect main** now protects only `main`. The two incorporated temporary remote branches were deleted; the remote has only `main`.

## GitHub and CI

| Item | Verified result |
| --- | --- |
| PR #5 — Zod GHSA fix | Merged normally. Patched `apps/web` and root lock to Zod 4.6.7. Merge SHA `72193e3cbc07987234b22c5fa6839c381bc002ba`. |
| PR #4 — V2 campaign | Merged normally from head `39aa6a3c535f42113e01b46bde649e944d0b686c`. Merge SHA `6d08d088e42933e494899faf6bc03c6805c17480`. All30 review threads are resolved. |
| PR #4 required Actions check | `offline`, run `41424158695`, completed successfully at the exact PR head. |
| Main push Actions check | `offline`, run `41425102889`, completed successfully for merge SHA `6d08d088e42933e494899faf6bc03c6805c17480`. |
| Git operations | Fast-forward update to the existing PR branch and ordinary GitHub merge; no force-push or history rewrite. |
| Remote branches after cleanup | Only `main` remains. PR #4 and PR #5 branch tips were verified as ancestors of `main` before deletion. |

The `6d08...` SHA above is the functional release merge. This report is delivered afterward through a documentation-only PR so its merge cannot be represented by that earlier SHA. The report PR URL and resulting main state are verifiable in GitHub.

## Main protection ruleset

GitHub reports exactly one repository ruleset: **Protect main**, ID `26357411`, target `branch`, enforcement `active`, matching only `refs/heads/main`. The verified rules are:

- Pull requests required for updates.
- No required approvals (0), appropriate for the solo maintainer.
- All PR review conversations must be resolved.
- Required successful status check is the GitHub Actions `offline` context (app ID `15368`), with strict up-to-date checks.
- Branch deletion and non-fast-forward updates are blocked.
- No bypass actors are configured.

The repository owner can recover access by editing the ruleset in GitHub repository settings; there is no permanent bypass actor.

## Local verification

On Windows with Node 24/npm and Python 3.12, `.venv/Scripts/python.exe scripts/verify.py` passed all15 stages on the final application/campaign changes:

- Ruff and138 Python tests.
- ESLint, TypeScript,51 frontend tests and the production Next.js build.
- Python wheel and source distribution build.
-42 desktop/mobile Playwright browser tests.
- `pip check`, `npm audit --audit-level=high`, `pip-audit`, release configuration, docs, source inventory and reachable-history secret scan.

The campaign was separately installed from its own pinned production-tool lock and verified: clean `npm ci --workspaces=false`, typecheck, composition validation, full media QA and `npm audit --audit-level=high`. Promo npm audit found0 vulnerabilities. The root application high-severity audit passed and reported11 moderate `minimatch` advisories in ESLint development dependencies; no high-severity root advisory remained. Python dependency audit reported no known vulnerabilities.

## Campaign fixes and media evidence

The launch film and vertical reel now say that ten comments are the illustrative sample and disclose that the product offers sample presets up to500. Rerender normalization no longer skips the audio gain when the renderer already outputs yuv420p. Render/capture jobs use a shared exclusive lock, staging and rollback so failed or concurrent jobs cannot publish mixed approved files. The campaign fixture/build manifest reads the promo-local illustrative fixture rather than the application test fixture.

| Output | Bytes | SHA-256 | Measured audio |
| --- | ---: | --- | --- |
| Launch film, 70s / 1920×1080 | 13,112,858 | `42b3ca576187e7855b9e9129406f324364bf9ff2f4c89e8cae66a81ad8867217` | −18.3 LUFS; −2.6 dBFS true peak |
| Vertical reel, 30s / 1080×1920 | 5,259,898 | `5b7f81b2560373fd941e23f6f6f787baf61f591a29e5b5756e6af28750864a2a` | −20.9 LUFS; −2.4 dBFS true peak |
| Silent preview MP4 | 699,809 | `87c060168a4d730e443fe6a695fc4a445078e399ed84795d2586920ecef6b7c1` | No audio stream |
| Preview GIF | 3,796,647 | `42a9e60450f74c671a8cd6f5c720a38ad1c0467d9edd3a66de17c6c64662f900` | n/a |
| Thumbnail PNG | 330,001 | `9095a972bdfc1607080b05c0bf20bdbaf92012c7487e3c411ac8d90ce49d8671` | n/a |

All3,240 MP4 frames decoded successfully. The updated text frames were visually inspected. All27 approved source inputs match their SHA-256 manifest; the untouched preview, GIF and thumbnail retain their verified hashes. Capture testing used an explicit offline fixture, blocked external requests and reported0 browser errors. The videos disclose that the product responses are illustrative demo data, not live YouTube comments.

## Security, license and publication review

At the functional main commit `6d08d088e42933e494899faf6bc03c6805c17480`, the full secret/history scan reported `matches: []`,0 unexpected environment files,0 prohibited artifacts and0 public secret variables; it examined707 source files,631 reachable Git blobs and25 browser artifacts (logs0). This scanner is a project secret check, not a complete independent security audit. No credential values were printed or included in Git. The report-only PR itself is outside that baseline scan.

The main Zod advisory `GHSA-mrhx-c7xc-m3w5` is patched at Zod4.6.7. Root `npm audit --audit-level=high` passes; the11 moderate ESLint/minimatch findings are documented and were not suppressed or force-upgraded. The promo toolchain remains an isolated, separately locked package because folding its pinned Remotion dependency graph into the root workspace exposed vulnerable transitive Zod4.5.4 entries that npm did not override without an invalid install. Its lock pins the patched Zod4.6.7 override and its own high-severity audit passes.

The maintainer's existing publication-rights decision and required upstream notices remain in place. No specific included-media rights blocker was identified in the scoped review. `promo/docs/third-party-tooling.md` records exact limits: Remotion is source-available under Remotion's proprietary license (free for eligible individuals and organizations/teams of up to3 under its terms); FFmpeg-static supplies a GPL-3.0-or-later build binary when operators install the promo package; Sharp is Apache-2.0 and its platform libvips packages carry LGPL notices. These executables are downloaded by npm for local production/QA and are not committed as files in this repository. The root MIT grant does not relicense dependencies. Downstream users must check the licenses of any binaries they install or redistribute. See [Remotion license FAQ](https://www.remotion.dev/docs/license/faq), [FFmpeg legal considerations](https://ffmpeg.org/legal.html), [Sharp license](https://github.com/lovell/sharp/blob/main/LICENSE) and [sharp-libvips notices](https://github.com/lovell/sharp-libvips/blob/main/THIRD-PARTY-NOTICES.md).

No Render/Vercel service, release asset, paid hosting, paid AI inference or cloud resource was created. This task made no deployment claim.

## Report artifacts

- [Implementation journal](../IMPLEMENTATION_JOURNAL.md) records commands and evidence.
- [Project progress](../CODEX_PROGRESS.md) records current release state.
- [Campaign QA report](../../promo/docs/qa-report.md) and [delivery hashes](../../promo/docs/delivery-manifest.json) contain detailed production checks.
- [Third-party tooling notices](../../promo/docs/third-party-tooling.md) document tool licenses and distribution limits.
