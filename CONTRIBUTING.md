**Contributing & Local setup**

- **Run tests locally**: create and activate your virtualenv, install deps, then run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
```

- **Set GITHUB_TOKEN for local testing**
  - PowerShell (session only):

    `Set-Item Env:GITHUB_TOKEN '<YOUR_TOKEN>'`

  - For CI, add the secret in GitHub: `Settings -> Secrets and variables -> Actions -> New repository secret` and name it `GITHUB_TOKEN`.

- **How to trigger the workflow manually**
  - Use the included script `trigger_workflow_v2.py` which updates README to force a push and trigger the workflow.

- **Rotating PATs (recommended)**
  1. Revoke any older PATs at https://github.com/settings/tokens
  2. Generate a new PAT if needed and add it as `GITHUB_TOKEN` secret in the repository.
  3. Avoid committing PATs in any file.

- **Debugging CI**
  - The workflow includes debug `ls -la` steps before publishing. If a run fails, run `download_and_show_logs.py <run_id>` to fetch logs and attach core failing lines when opening an issue or asking for help.

If you want, I can open a PR with these docs changes, or commit directly to `main` (I already updated the files in the repo).