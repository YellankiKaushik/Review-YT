# Final publication rights decision

Status: **BLOCKED BY USER AUTHORIZATION** — one recorded maintainer rights/license decision is still needed. This review identifies no specific copied unlicensed expression in the inspected new tree. It is not legal certification or a comparison against historical source.

## Evidence and concrete scope

- Fresh Git root `d6af681`; starting release commit `e35d587`. No historical Git objects, archives, source or assets were imported in this build. The historical application was not opened or modified in this release mission.
- Reviewed the actual new core (`domain.py`, `youtube.py`, `network.py`, `engine.py`, `providers.py`, CLI), Flask routes/store/WSGI entry, frontend relay/contracts/form/results/chart and release configuration. These are project-authored AI-assisted material recorded in SOURCE_INVENTORY.json, not a guarantee of exclusive copyright. New startup scripts and tests have the same classification.
- Third-party content actually committed: 502 retained dependency license/notice files; package-manager lock metadata; Next-generated `apps/web/AGENTS.md` framework guidance. The Next notice is retained. No dependency implementation is vendored in application modules. The icon is authored SVG; charts are CSS. There are no bundled external photos, fonts, model weights, historical archives or runtime comment datasets.
- Inventory: 345 npm entries and 55 Python packages, including development/platform-optional dependencies. Upstream licenses and names remain intact. VADER's MIT lexicon attribution stays with its installed distribution. No third-party material is reassigned to the maintainer.
- `LICENSE`, package LICENSE, npm UNLICENSED and Python pending-license metadata currently grant no public license. That is an actual missing release decision, not evidence that the historical author owns this new tree.

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

**Identified:** maintainer has not selected a license or recorded rights acceptance for publication; Linux deployment artifacts have not been built/reviewed; runtime data and dependencies must stay outside any blanket new-code grant. There is no currently identified unlicensed source file to delete or reattribute in this new tree.

**Residual uncertainty:** the implementing assistant saw historical source earlier in the conversation. An empty folder and different names do not eliminate possible derivation. No historical comparison was undertaken, respecting the source-separation requirement. A maintainer can review this inventory and development record and record a reasoned decision; an impossible proof of universal dissimilarity or mandatory clean-room certificate is not required. If a specific similarity or uncertain asset is identified, resolve that item with permission, replacement or removal; obtain qualified advice if the maintainer needs it.

Do not add historical contributors to this tree without an actual included contribution or applicable attribution duty. Their original repository/credits remain untouched.

## One consolidated release decision

Before any public push/deployment, the maintainer must record all of the following together:

- [ ] Reviewed the source inventory, this checklist and prior-context exposure; accepts publication rights for the identified new project material, with any concrete exceptions resolved/listed.
- [ ] Selects the license and copyright notice for material they have rights to license. **Candidate: MIT for eligible new project material only**, with explicit third-party exceptions; this is a proposal, not an applied grant or a conclusion that all AI output is copyrightable.
- [ ] Retains third-party notices, approves the source-only distribution scope, and assigns the target Linux/native dependency obligations before any binary redistribution.
- [ ] Authorizes publication of the reviewed commit to the supplied existing `YellankiKaushik/Review-YT` and dedicated eligible free Render/Vercel deployment. Existing task authorization covers execution once this rights/license condition is resolved; paid upgrades remain unauthorized.

Record the decision and chosen LICENSE/package metadata in Git, refresh inventory, run release checks, then follow docs/DEPLOYMENT.md. No repeated broad audit is needed without new source, new evidence or a changed distribution target.
