## Setting GITHUB_TOKEN (secrets) — Quick Instructions

This repository's helper scripts and CI now read the GitHub token from the environment variable `GITHUB_TOKEN`.
Do NOT commit Personal Access Tokens (PATs) into the repo. Instead, set the token as an environment variable locally and as a GitHub Actions secret for automatic runs.

1) Create a short-lived Personal Access Token (PAT) on GitHub
- Go to https://github.com/settings/tokens → `Generate new token` → choose expiration (e.g., 7 days)
- Scopes recommended for this repo: `repo` (for private repos) or `public_repo` (for public repos). Avoid granting broader scopes.

2) Add the token as a repository Secret (recommended)
- Go to your repository on GitHub → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
- Name: `GITHUB_TOKEN`
- Value: paste the PAT

3) Set the token locally (PowerShell)
```
# Windows PowerShell (temporary for current session)
$env:GITHUB_TOKEN = "<YOUR_TOKEN>"
```

4) Set the token locally (bash / WSL / macOS)
```
export GITHUB_TOKEN=<YOUR_TOKEN>
```

5) Rotate and remove old tokens
- After verifying CI works, revoke any older tokens at https://github.com/settings/tokens to avoid leaked credentials.

6) Notes for CI / Actions
- The repository workflow uses the built-in `GITHUB_TOKEN` (available automatically in Actions). If you prefer to use a PAT (for cross-repo writes), add it as secret `GITHUB_TOKEN` in repository settings.

If you want, I can help create the new secret and test the workflow.
