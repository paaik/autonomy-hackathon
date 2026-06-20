# Launch Red Team Hack Sim from ./Simulator (must be cwd for relative paths).
# Usage:  .\launch_sim.ps1
#         .\launch_sim.ps1 -Map RedRoad2 -LiteMode

param(
    [string]$Map = "RedRoad",
    [switch]$LiteMode,
    [int]$Width = 1280,
    [int]$Height = 720
)

$SimDir = Join-Path $PSScriptRoot "Simulator"
$Exe = Join-Path $SimDir "Red_Team_Hack_Sim.exe"

if (-not (Test-Path $Exe)) {
    Write-Error "Simulator not found at $Exe`nDrop the Windows build into ./Simulator/ (see README)."
}

$args = @(
    $Map,
    "-windowed",
    "-ResX=$Width",
    "-ResY=$Height",
    '-ExecCmds="Scalability 0"',
    "-ini:Input:[/Script/Engine.InputSettings]:bCaptureMouseOnLaunch=False,[/Script/Engine.InputSettings]:DefaultViewportMouseCaptureMode=NoCapture,[/Script/Engine.InputSettings]:DefaultViewportMouseLockMode=DoNotLock"
)

if ($LiteMode) { $args += "-LiteMode" }

Write-Host ">> Starting simulator: $Exe $($args -join ' ')"
Push-Location $SimDir
try {
    & $Exe @args
}
finally {
    Pop-Location
}
