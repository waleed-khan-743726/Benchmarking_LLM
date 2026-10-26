$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Robot_Navigation_FYP'
. (Join-Path $ProjectRoot 'scripts\project-env.ps1')

$backendPidFile = Join-Path $ProjectRoot '.tmp\backend.pid'
$frontendPidFile = Join-Path $ProjectRoot '.tmp\frontend.pid'

function Test-ProjectProcess([string]$PidFile, [string]$ExpectedCommand) {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $false }
    $processId = [int](Get-Content -LiteralPath $PidFile -Raw)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$processId" -ErrorAction SilentlyContinue
    return $null -ne $process -and $process.CommandLine -like "*$ExpectedCommand*"
}

if (-not (Test-ProjectProcess $backendPidFile 'uvicorn backend.main:app')) {
    $backend = Start-Process `
        -FilePath (Join-Path $ProjectRoot '.venv\Scripts\python.exe') `
        -ArgumentList '-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000' `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput (Join-Path $ProjectRoot 'logs\backend.out.log') `
        -RedirectStandardError (Join-Path $ProjectRoot 'logs\backend.err.log') `
        -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath $backendPidFile -Value $backend.Id
    Write-Host "Backend started (PID $($backend.Id))."
} else {
    Write-Host 'Backend is already running.'
}

if (-not (Test-ProjectProcess $frontendPidFile 'vite.js*--host*127.0.0.1')) {
    $node = 'C:\Program Files\nodejs\node.exe'
    $vite = Join-Path $ProjectRoot 'frontend\node_modules\vite\bin\vite.js'
    $frontend = Start-Process `
        -FilePath $node `
        -ArgumentList $vite,'--host','127.0.0.1','--port','5173','--strictPort' `
        -WorkingDirectory (Join-Path $ProjectRoot 'frontend') `
        -RedirectStandardOutput (Join-Path $ProjectRoot 'logs\frontend.out.log') `
        -RedirectStandardError (Join-Path $ProjectRoot 'logs\frontend.err.log') `
        -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath $frontendPidFile -Value $frontend.Id
    Write-Host "Frontend started (PID $($frontend.Id))."
} else {
    Write-Host 'Frontend is already running.'
}

Write-Host 'Allow up to 20 seconds on first start.'
Write-Host 'Open http://127.0.0.1:5173'
Write-Host 'Stop with scripts\stop.ps1'

