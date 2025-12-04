# Apply patch and commit changes (PowerShell script)
# Usage: run this in project root after ensuring git is installed and configured

param(
    [string]$PatchFile = "pernambuco_only.patch",
    [string]$FilesToAdd = "app.py cache_results.json",
    [string]$CommitMessage = "Keep only pernambucoaval as source and regenerate cache"
)

function Check-Git {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) {
        Write-Error "git not found in PATH. Install Git or add it to PATH and re-run this script."
        exit 1
    }
}

Check-Git

# Apply patch
if (-not (Test-Path $PatchFile)) {
    Write-Error "Patch file '$PatchFile' not found in current directory."
    exit 1
}

git apply --index $PatchFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "git apply failed. Try 'git apply $PatchFile' manually to see errors."
    exit 1
}

# Add and commit
git add $FilesToAdd
if ($LASTEXITCODE -ne 0) {
    Write-Error "git add failed."
    exit 1
}

git commit -m "$CommitMessage"
if ($LASTEXITCODE -ne 0) {
    Write-Warning "git commit returned non-zero. Maybe there is nothing to commit or there are conflicts."
} else {
    Write-Output "Committed changes."
}

# Attempt push (optional)
try {
    git push
} catch {
    Write-Warning "git push failed or requires authentication. Push manually if needed."
}
