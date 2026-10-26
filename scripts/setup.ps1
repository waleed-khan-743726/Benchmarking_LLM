param(
    [switch]$IncludeReportDependencies,
    [string]$BasePython = $env:ROBOT_NAV_BASE_PYTHON
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Robot_Navigation_FYP'
. (Join-Path $ProjectRoot 'scripts\project-env.ps1')

$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
$freeGB = [math]::Round($drive.FreeSpace / 1GB, 2)
Write-Host "D: free space: $freeGB GB"
if ($freeGB -lt 10) {
    throw 'At least 10 GB free on D: is required for project setup.'
}

$venvPython = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    if ([string]::IsNullOrWhiteSpace($BasePython)) {
        $BasePython = 'D:\Miniconda3\python.exe'
    }
    if (-not (Test-Path -LiteralPath $BasePython)) {
        throw "Base Python was not found at $BasePython. Install Python on D: or pass -BasePython."
    }
    if ([IO.Path]::GetFullPath($BasePython) -notlike 'D:\*') {
        throw 'The base Python path must be on D: for this project setup.'
    }
    & $BasePython -m venv (Join-Path $ProjectRoot '.venv')
}

$pythonExtras = if ($IncludeReportDependencies) { '.[dev,report]' } else { '.[dev]' }
& $venvPython -m pip install --disable-pip-version-check -e $pythonExtras

$npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $npm) {
    throw 'Node.js/npm was not found. Install Node, then rerun this project-scoped setup.'
}
Push-Location (Join-Path $ProjectRoot 'frontend')
try {
    & $npm.Source install --no-audit --no-fund
} finally {
    Pop-Location
}

Write-Host 'Setup completed. No Ollama model was downloaded.' -ForegroundColor Green
Write-Host 'Run scripts\health-check.ps1, then scripts\run.ps1.'

