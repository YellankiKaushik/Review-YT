# Deployment and source releases

Review-YT is self-hostable source. **The original maintainer's hosted demo and cloud services are retired.** No live maintainer URL is provided and this repository does not provision accounts or credentials for you.

- [Self-hosting](SELF_HOSTING.md): private servers and the complete optional Render/Vercel walkthrough.
- [Render settings](RENDER_DEPLOYMENT_HANDOFF.md): backend template, own secrets, port, health and ephemeral storage.
- [Vercel settings](VERCEL_DEPLOYMENT_HANDOFF.md): own fork/project, monorepo build and server-only relay configuration.
- [Configuration](CONFIGURATION.md): source-derived variables and safe defaults.
- [Environment checklist](ENVIRONMENT_VARIABLES_CHECKLIST.md): concise operator checklist.

## Safe release workflow

1. Start from synchronized main; work on a temporary branch without importing historical implementation.
2. Preserve API/cache/auth contracts, all legal notices, root lockfile and sentiment-only defaults.
3. Run scripts/verify.py with offline fixtures, documentation/source inventory and secret/history checks. Record actual outcomes, not forecasts.
4. Publish normally, open a PR and inspect the exact-head GitHub Actions result. Never force-push/rewrite history or merge over failed required checks.
5. Merge only after applicable checks pass and normal repository permissions allow; delete incorporated temporary branches. Keep main as the persistent branch.
6. A **new operator's own** hosting may deploy separately. Verify actual provider-returned URLs, health, configured inventory and a bounded real analysis before describing that instance as live.

No hosted preview is required for this source-only handoff: the maintainer retired the hosting. Use deterministic browser tests and local production verification instead; never restore services as a side effect of a documentation or source release. No registry package upload is implied by GitHub publication.

Historical deployment reports are [archived](reports/archive/README.md). Their dated URLs/HTTP results are past evidence, not ongoing instructions or current availability claims. Preserve the [recorded MIT scope](FINAL_PUBLICATION_RIGHTS_CHECKLIST.md) and distribution obligations.
