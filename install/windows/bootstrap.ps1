[CmdletBinding()]
param(
    [string]$NexusNetHome = $(if ($env:NEXUSNET_HOME) { $env:NEXUSNET_HOME } else { Join-Path $env:LOCALAPPDATA "NexusNet" }),
    [string]$PrivatePython = "",
    [switch]$DeveloperEditable
)

$ErrorActionPreference = "Stop"
if (-not [Environment]::Is64BitOperatingSystem) {
    throw "NexusNet requires Windows 11 x64."
}

$privateRoot = Join-Path $NexusNetHome "private"
$coreRoot = Join-Path $privateRoot "core"
$venvRoot = Join-Path $coreRoot "venv"
$sourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$projectMetadata = Join-Path $sourceRoot "pyproject.toml"
if (-not (Test-Path -LiteralPath $projectMetadata -PathType Leaf)) {
    throw "NexusNet project metadata is unavailable."
}

if (-not $PrivatePython) {
    $bundledPython = Join-Path $privateRoot "python\python.exe"
    if (Test-Path -LiteralPath $bundledPython -PathType Leaf) {
        $PrivatePython = $bundledPython
    } else {
        $PrivatePython = (Get-Command py.exe -ErrorAction Stop).Source
    }
}

New-Item -ItemType Directory -Force -Path $coreRoot | Out-Null
if (-not (Test-Path -LiteralPath (Join-Path $venvRoot "Scripts\python.exe") -PathType Leaf)) {
    if ([IO.Path]::GetFileName($PrivatePython) -ieq "py.exe") {
        & $PrivatePython -3.11 -m venv $venvRoot
    } else {
        & $PrivatePython -m venv $venvRoot
    }
    if ($LASTEXITCODE -ne 0) { throw "Private core environment creation failed." }
}

$corePython = Join-Path $venvRoot "Scripts\python.exe"
$installTarget = if ($DeveloperEditable) { @("-e", $sourceRoot) } else { @($sourceRoot) }
& $corePython -m pip install --disable-pip-version-check --no-input @installTarget
if ($LASTEXITCODE -ne 0) { throw "NexusNet private core installation failed." }

& $corePython -m nexusnet.cli.runtime_packs plan --home $NexusNetHome
if ($LASTEXITCODE -ne 0) { throw "Runtime-pack planning failed." }

Write-Host "NexusNet private core installed at $coreRoot"
