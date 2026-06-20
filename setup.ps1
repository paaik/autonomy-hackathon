# One-time setup: Python 3.12 venv + Windows-compatible ProjectAirSim client.
# Run from the repo root:  .\setup.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Error "Python launcher (py) not found. Install Python 3.12 first."
}

$py312 = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
if (-not $py312) {
    Write-Host "Python 3.12 not found. Installing via winget..."
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
}

Write-Host ">> Creating venv at .venv ..."
& py -3.12 -m venv "$RepoRoot\.venv"

$pip = Join-Path $RepoRoot ".venv\Scripts\pip.exe"
$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"

& $python -m pip install --upgrade pip

# Bundled ./wheels are Linux-only; on Windows install deps from PyPI, then the local projectairsim wheel.
Write-Host ">> Installing Windows dependencies from PyPI ..."
& $pip install "pynng>=0.5.0" "msgpack>=1.0" "cffi>=1.0" commentjson cryptography sniffio numpy opencv-python
& $pip install --no-deps (Join-Path $RepoRoot "wheels\projectairsim-1.0.0-py3-none-any.whl")

Write-Host ""
Write-Host "Setup complete."
Write-Host "  1. Launch sim:  .\launch_sim.ps1"
Write-Host "  2. Smoke test:  .\run_client.ps1 smoke_test.py"
Write-Host "  3. Fly starter: .\run_client.ps1 fly.py"
