# Release Notes — Automated Pages deployment

Date: 2025-12-04

Summary:
- Added a CI workflow `Build and Publish Landing` that:
  - Runs `ci-check` (installs dependencies, runs `pytest` if tests exist, runs `flake8`).
  - Generates `web/landing_data.js` via `generate_landing_data.py`.
  - Publishes the site to GitHub Pages (branch `gh-pages`) using `actions/deploy-pages@v4`.

Deployment details:
- The workflow is triggered on `push` to `main` and can be triggered manually.
- The Pages deployment now uses the `upload-pages-artifact` / `deploy-pages` pattern where applicable; for compatibility a safe git-push fallback was implemented.
- Debug listings (`pwd`, `ls -la`) were added before publish to aid CI debugging.

How to trigger:
- Locally: set `GITHUB_TOKEN` in your shell (session) then run `trigger_workflow_v2.py` or push to `main`.

Notes:
- Remove any exposed PATs and configure the repository secret `GITHUB_TOKEN` for CI.
- See `CONTRIBUTING.md` for local setup and testing instructions.

Status: Successful test deployment (Pages URL: https://drbq-advogados.github.io/jdb/landing.html)
