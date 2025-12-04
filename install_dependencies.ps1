# Install missing dependencies for JDB Project
# PowerShell Script for Windows

$projectPath = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path -Path $projectPath -ChildPath ".venv"
$pythonExe = Join-Path -Path $venvPath -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$pipExe = Join-Path -Path $venvPath -ChildPath "Scripts" | Join-Path -ChildPath "pip.exe"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  JDB Project - Dependency Installer                       ║"
Write-Host "║  Installing missing packages: PyMC, statsmodels           ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Check if venv exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "❌ ERROR: Virtual environment not found at $venvPath"
    Write-Host "   Please create a virtual environment first:"
    Write-Host "   python -m venv .venv"
    exit 1
}

Write-Host "✓ Virtual environment found"
Write-Host "  Python: $pythonExe"
Write-Host ""

# Install statsmodels
Write-Host "📦 Installing statsmodels..."
& $pipExe install statsmodels --upgrade
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ statsmodels installed successfully"
} else {
    Write-Host "⚠️  statsmodels installation had issues (code: $LASTEXITCODE)"
}
Write-Host ""

# Install PyMC with retry strategy
Write-Host "📦 Attempting PyMC installation..."
Write-Host "  Strategy 1: Standard installation..."
& $pipExe install pymc

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ PyMC installed successfully (standard method)"
} else {
    Write-Host "⚠️  Standard installation failed. Trying with --no-build-isolation..."
    & $pipExe install pymc --no-build-isolation
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PyMC installed successfully (no-build-isolation)"
    } else {
        Write-Host "❌ PyMC installation failed with both methods"
        Write-Host "   This may require Microsoft Visual C++ Build Tools"
        Write-Host ""
        Write-Host "   SOLUTION: Install Visual C++ Build Tools from:"
        Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/"
        Write-Host ""
        Write-Host "   ALTERNATIVE: Run notebook without PyMC (use statsmodels only)"
    }
}
Write-Host ""

# Verification
Write-Host "═════════════════════════════════════════════════════════════"
Write-Host "Verifying installations..."
Write-Host ""

$testPyMC = & $pythonExe -c "import pymc as pm; print(f'PyMC {pm.__version__}')" 2>&1
$testStatsmodels = & $pythonExe -c "import statsmodels; print(f'statsmodels {statsmodels.__version__}')" 2>&1

if ($testPyMC -match "PyMC") {
    Write-Host "✅ PyMC: $testPyMC"
} else {
    Write-Host "❌ PyMC: Not installed"
}

if ($testStatsmodels -match "statsmodels") {
    Write-Host "✅ $testStatsmodels"
} else {
    Write-Host "❌ statsmodels: Not installed"
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════"
Write-Host "Installation complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Run: jupyter notebook analise_probabilidades_operacional.ipynb"
Write-Host "2. Execute cells sequentially (Ctrl+Enter)"
Write-Host "3. Check ERROR_AUDIT_REPORT.md for any issues"
