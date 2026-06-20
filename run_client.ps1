# Run a Python client script against the live sim (venv must exist — run setup.ps1 first).
# Usage:  .\run_client.ps1 smoke_test.py
#         .\run_client.ps1 fly.py
#         .\run_client.ps1 smoke_test.py --easy

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Script,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Error "Virtual env not found. Run .\setup.ps1 first."
}

$target = Join-Path $PSScriptRoot $Script
if (-not (Test-Path $target)) {
    Write-Error "Script not found: $target"
}

Write-Host ">> $python $Script $($ScriptArgs -join ' ')"
& $python $target @ScriptArgs
