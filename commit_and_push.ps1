# PowerShell script to automate git workflow for pernambucoaval scraper feature
# Usage: .\commit_and_push.ps1

param(
    [string]$BranchName = "feat/pernambucoaval-scraper",
    [string]$CommitMessage = "feat(pernambucoaval): add structured scraper, validation and predictive_by_group support"
)

Write-Host "JDB Pernambucoaval Scraper - Automated Git Workflow" -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan

# Check if git is available
try {
    $gitVersion = git --version
    Write-Host "Found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: git is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Get current branch
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $currentBranch`n"

# Create and checkout to new branch
Write-Host "Creating branch '$BranchName'..." -ForegroundColor Yellow
git checkout -b $BranchName
if ($LASTEXITCODE -ne 0) {
    Write-Host "Branch already exists or checkout failed. Switching to existing branch..."
    git checkout $BranchName
}

# Stage files
Write-Host "`nStaging modified files..." -ForegroundColor Yellow
$filesToAdd = @(
    "fetch_pernambucoaval.py",
    "generate_landing_data.py",
    "web/landing.html",
    "web/app.js",
    "web/landing_data.js",
    "SCRAPER_README.md",
    "scraper_validation.py",
    "tests/test_scraper_helpers.py",
    "cache_results.json",
    "cache_results.json.bak",
    "scraper_report_examples.csv"
)

foreach ($file in $filesToAdd) {
    if (Test-Path $file) {
        git add $file
        Write-Host "  + $file" -ForegroundColor Green
    } else {
        Write-Host "  ? $file (not found)" -ForegroundColor Gray
    }
}

# Check status
Write-Host "`nGit status:" -ForegroundColor Yellow
git status --short

# Commit
Write-Host "`nCreating commit: '$CommitMessage'" -ForegroundColor Yellow
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Commit failed or no changes to commit" -ForegroundColor Red
    exit 1
}

# Push
Write-Host "`nPushing to remote origin..." -ForegroundColor Yellow
git push -u origin $BranchName
if ($LASTEXITCODE -eq 0) {
    Write-Host "Push successful!" -ForegroundColor Green
    Write-Host "You can now create a Pull Request at: https://github.com/drbq-advogados/jdb/compare/$BranchName" -ForegroundColor Green
} else {
    Write-Host "Push failed. Check your credentials and remote configuration." -ForegroundColor Red
    exit 1
}

Write-Host "`n====================================================`n" -ForegroundColor Cyan
Write-Host "Workflow completed successfully!" -ForegroundColor Green
