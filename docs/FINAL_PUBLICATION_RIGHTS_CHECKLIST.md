# Final publication rights decision

Status: **MAINTAINER DECISION RECORDED — MIT, 2026-10-21.** The source-only rights/license gate is cleared on the maintainer's explicit declaration and follow-up MIT selection. Final technical checks and actual GitHub publication are tracked in GITHUB_PUBLICATION_REPORT.md. This review identifies no specific copied unlicensed expression in the inspected new tree. It is not legal certification or a comparison against historical source.

## Evidence and concrete scope

- Fresh Git root `d6af681`; starting release commit `e35d587`. No historical Git objects, archives, source or assets were imported in this build. The historical application was not opened or modified in this release mission.
- Reviewed the actual new core (`domain.py`, `youtube.py`, `network.py`, `engine.py`, `providers.py`, CLI), Flask routes/store/WSGI entry, frontend relay/contracts/form/results/chart and release configuration. These are project-authored AI-assisted material recorded in SOURCE_INVENTORY.json, not a guarantee of exclusive copyright. New startup scripts and tests have the same classification.
- Third-party content actually committed: 502 retained dependency license/notice files; package-manager lock metadata; Next-generated `apps/web/AGENTS.md` framework guidance. The Next notice is retained. No dependency implementation is vendored in application modules. The icon is authored SVG; charts are CSS. There are no bundled external photos, fonts, model weights, historical archives or runtime comment datasets.
- Inventory: 345 npm entries and 55 Python packages, including development/platform-optional dependencies. Upstream licenses and names remain intact. VADER's MIT lexicon attribution stays with its installed distribution. No third-party material is reassigned to the maintainer.
- The maintainer explicitly selected MIT in a separate follow-up answer. Root/package LICENSE files and npm/Python metadata now apply MIT only to eligible new material; NOTICE files retain third-party and runtime-data exceptions. This does not assign ownership of dependencies, historical work or every AI output to the maintainer.

## Distribution obligations to carry forward

| Material | Actual release scope | Required handling |
| --- | --- | --- |
| MIT/BSD/ISC/Apache dependencies | Lock references, retained notices; installed by hosting | Retain applicable original copyright/license/NOTICE terms; do not describe the entire dependency tree as maintainer-owned. |
| certifi / MPL-2.0; lightningcss / MPL-2.0 | Unmodified dependencies installed separately; certifi server-side, lightningcss build tooling | Preserve notices. If distributing covered files/binaries, supply corresponding covered source/availability and disclose modifications as required. No modifications to these dependency files are made here. MPL applies to covered files, not automatically every project file. |
| sharp/libvips LGPL-3.0-or-later platform packages | Transitive Next dependency; Windows install reviewed, Linux variants in lockfile. No native binary committed or served as a browser asset | A future binary/container redistribution needs the exact platform notices, corresponding source and applicable relinking/replacement compliance. A source-only Git push does not bundle those binaries. Hosting still needs its installed-distribution review. |
| YouTube comments/captions/thumbnails | Private TTL runtime cache; not committed | No grant to republish a dataset; retain bounded retrieval, privacy retention and service terms. |
| Gemma weights and provider output | External local daemon/runtime only | No weight redistribution. Provider/model terms apply to use; no new ownership or dataset license is inferred. |

Primary license explanations: [Mozilla MPL FAQ](https://www.mozilla.org/en-US/MPL/2.0/FAQ/), [GNU LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.html). The actual retained license texts control; this engineering review does not settle jurisdiction-specific legal questions.

## Identified issues versus general uncertainty

**Identified:** Linux deployment artifacts have not yet been built/reviewed locally; runtime data and dependencies must stay outside the eligible-new-material MIT grant. The maintainer has now recorded rights acceptance, selected MIT, approved notices and authorized source publication. These decisions do not cure a concrete infringement if later identified. There is no currently identified unlicensed source file to delete or reattribute in this new tree.

**Residual uncertainty:** the implementing assistant saw historical source earlier in the conversation. An empty folder and different names do not eliminate possible derivation. No historical comparison was undertaken, respecting the source-separation requirement. A maintainer can review this inventory and development record and record a reasoned decision; an impossible proof of universal dissimilarity or mandatory clean-room certificate is not required. If a specific similarity or uncertain asset is identified, resolve that item with permission, replacement or removal; obtain qualified advice if the maintainer needs it.

Do not add historical contributors to this tree without an actual included contribution or applicable attribution duty. Their original repository/credits remain untouched.

## Recorded maintainer release decision — 2026-10-21

The human maintainer supplied the declaration in the release conversation, then answered the specific unresolved license question with **MIT**. The original declaration's license line was an unfilled placeholder; it was not treated as a selection. No approval or signature was invented by the implementing agent.

- [x] Reviewed the publication-rights checklist, source inventory, independent-implementation audit and third-party notice summary. Confirmed, to the best of their knowledge, sufficient rights to authorize publication of eligible new material, subject to documented exceptions.
- [x] Acknowledged that fresh Git history does not establish complete copyright independence and that third-party rights and license terms remain. Selected **MIT** for eligible new material in an explicit follow-up answer. The copyright notice identifies the maintainer, YellankiKaushik, for 2026; the scope is limited to rights they hold and does not certify copyrightability of all AI-assisted material.
- [x] Approved preserving required third-party notices and complying with applicable source-distribution and hosting obligations. Did not claim ownership of dependencies or historical contributors' work. Target-platform dependency obligations remain applicable to their actual distribution scope.
- [x] Authorized public publication of the reviewed and rights-cleared source to **https://github.com/YellankiKaushik/Review-YT**, after release checks pass and no concrete rights blocker is identified.
- [x] Authorized preparation for eligible free Render/Vercel hosting only. **The maintainer creates hosting projects and enters production environment variables. This task must not create those resources. Paid hosting and paid AI inference are not authorized.**

No concrete copied unlicensed expression or unresolved included-source exception has been identified in the inspected new tree. This statement records the scope of the review, not legal certification or an assertion of universal dissimilarity. If a specific rights issue is identified, resolve it before distributing affected material; this declaration does not override third-party rights.

The canonical MIT text is in root/package LICENSE; NOTICE files explain eligible material and exceptions. Original retained third-party legal texts remain unmodified. Source-only GitHub publication is distinct from publishing a Python/npm package or redistributing native binaries. No package upload, release tag, hosting project, paid service or public app endpoint is authorized or claimed by this record.

Final technical verification, Git commit, remote SHA, Actions outcome and remaining manual hosting steps belong in GITHUB_PUBLICATION_REPORT.md. No repeated broad audit is needed without new source, new evidence or a changed distribution target.
