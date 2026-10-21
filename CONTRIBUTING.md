# Contributing

This project is preserved as an open-source portfolio and reference implementation. Contributions may be considered as time permits. The original maintainer does not operate a public demo or guarantee ongoing support.

## Start here

Follow [Getting Started](docs/GETTING_STARTED.md). Offline contribution tests need no real API credentials: install Python requirements and root npm workspaces, then install Chromium. Use Python 3.12/Node 24 as the tested baseline. Preserve the root package-lock.json and use npm ci.

Work from current main on a focused temporary branch. Develop from requirements; do not import the separate historical application's source/assets/tests or erase historical attribution. Preserve all required legal notices, MIT scope and disclosed provenance limits. New concrete rights issues must be resolved before distributing affected material.

## Changes and verification

- Keep Flask, Next and the independent core separated. Preserve VADER baseline and actual model attribution.
- GET results stays cache-only; optional-provider errors must not discard genuine sentiment or overwrite complete cached notes.
- Keep paid inference and automatic fallback false. Never require live cloud requests or maintainer keys in CI.
- Keep fixtures in tests/dependency-injected smoke servers and label demo captures visibly. Do not fabricate live comments, AI output, test results or deployment URLs.
- Run scripts/source_inventory.py after final changes, then scripts/verify.py through this project's .venv Python. The verifier covers lint, types, tests, browser, builds, audits, links, inventory and secret/history checks.
- Explain the actual behavior and verification in the PR template. Submit normally, wait for CI and preserve existing meaningful regressions. No force-push to main or artificial contribution commits.

The Windows optimized-production verifier is optional additional local evidence, not a requirement to create cloud resources. Never restore retired hosting for a PR. Linux behavior is checked by the pinned GitHub Actions workflow; do not claim an unexecuted platform command passed.

## Privacy and reporting

Use [bug](.github/ISSUE_TEMPLATE/bug_report.yml) or [feature](.github/ISSUE_TEMPLATE/feature_request.yml) templates. Include a minimal reproduction, commit/version and sanitized error code. Do not post .env, tokens, keys, raw comments, private browser captures, databases or operational traces. Follow [SECURITY.md](SECURITY.md) for suspected vulnerabilities; public issues are not a place for secrets.

Curated labeled images under docs/assets are intentionally tracked. All other runtime data/build output/temporary captures stay ignored. Commit identities/dates must reflect actual work. Source GitHub publication does not authorize registry uploads or paid services.
