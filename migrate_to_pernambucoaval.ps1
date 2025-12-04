# Complete git workflow script for pernambucoaval migration
# This script:
# 1. Applies the app.py patch (removes old sources, keeps only pernambucoaval)
# 2. Stages cache_results.json (already regenerated)
# 3. Commits both changes
# 4. Attempts to push

param(
    [string]$AppPatchFile = "pernambuco_only.patch",
    [string]$CommitMessage = "Keep only pernambucoaval as source and regenerate cache"
)

Write-Host "JDB Pernambucoaval Migration Script" -ForegroundColor Cyan
Write-Host "=" * 50

# Check git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Error "git not found. Install Git and add to PATH, then re-run this script."
    exit 1
}

Write-Host "✓ git found: $(git --version)" -ForegroundColor Green

# Apply patch
Write-Host "`nApplying patch: $AppPatchFile..." -ForegroundColor Yellow
if (-not (Test-Path $AppPatchFile)) {
    Write-Error "Patch file '$AppPatchFile' not found."
    exit 1
}

git apply --index $AppPatchFile
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to apply patch. Try manually: git apply $AppPatchFile"
    exit 1
}
Write-Host "✓ Patch applied" -ForegroundColor Green

# Stage cache
Write-Host "`nStaging cache_results.json..." -ForegroundColor Yellow
git add cache_results.json
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to add cache_results.json, but continuing."
}
Write-Host "✓ cache_results.json staged" -ForegroundColor Green

# Commit
Write-Host "`nCommitting changes..." -ForegroundColor Yellow
git commit -m "$CommitMessage"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Committed successfully" -ForegroundColor Green
} else {
    Write-Warning "Commit returned non-zero status. Check if there are changes to commit."
}

# Show status
Write-Host "`nGit Status:" -ForegroundColor Yellow
git status

# Push
Write-Host "`nAttempting to push..." -ForegroundColor Yellow
git push
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Pushed successfully" -ForegroundColor Green
} else {
    Write-Warning "Push failed or requires authentication. Push manually if needed: git push"
}

Write-Host "`nDone!" -ForegroundColor Cyan
