$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Robot_Navigation_FYP'
. (Join-Path $ProjectRoot 'scripts\project-env.ps1')

$backendPidFile = Join-Path $ProjectRoot '.tmp\backend.pid'
$frontendPidFile = Join-Path $ProjectRoot '.tmp\frontend.pid'
$ollamaPidFile = Join-Path $ProjectRoot '.tmp\ollama.pid'
$startedOllama = $false
$startedBackend = $false
$startedFrontend = $false

function Test-ProjectProcess([string]$PidFile, [string]$ExpectedCommand) {
    if (-not (Test-Path -LiteralPath $PidFile)) { return $false }
    $processId = [int](Get-Content -LiteralPath $PidFile -Raw)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$processId" -ErrorAction SilentlyContinue
    return $null -ne $process -and $process.CommandLine -like "*$ExpectedCommand*"
}

function Set-ListenerPid([int]$Port, [string]$PidFile) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) { Set-Content -LiteralPath $PidFile -Value $listener.OwningProcess }
}

$ollamaExe = Join-Path $ProjectRoot 'tools\ollama\ollama.exe'
$ollamaReady = $false
try {
    Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null
    $ollamaReady = $true
} catch {}

if (-not $ollamaReady -and (Test-Path -LiteralPath $ollamaExe)) {
    if (-not (Test-ProjectProcess $ollamaPidFile 'ollama.exe*serve')) {
        $ollama = Start-Process `
            -FilePath $ollamaExe -ArgumentList 'serve' -WorkingDirectory $ProjectRoot `
            -RedirectStandardOutput (Join-Path $ProjectRoot 'logs\ollama.out.log') `
            -RedirectStandardError (Join-Path $ProjectRoot 'logs\ollama.err.log') `
            -WindowStyle Hidden -PassThru
        Set-Content -LiteralPath $ollamaPidFile -Value $ollama.Id
        $startedOllama = $true
        Write-Host "Ollama started (PID $($ollama.Id)); models: $env:OLLAMA_MODELS"
    } else {
        Write-Host 'Ollama project process is already starting.'
    }
} elseif ($ollamaReady) {
    Write-Host 'Ollama API is already running.'
} else {
    Write-Host 'Ollama runtime is not installed; starting in deterministic offline mode.' -ForegroundColor Yellow
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
    $startedBackend = $true
    Write-Host "Backend started (PID $($backend.Id))."
} else {
    Write-Host 'Backend is already running.'
}

if (-not (Test-ProjectProcess $frontendPidFile 'vite.js*--host*127.0.0.1')) {
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    if (-not $node) { throw 'node.exe was not found on PATH. Install Node.js and rerun setup.' }
    $vite = Join-Path $ProjectRoot 'frontend\node_modules\vite\bin\vite.js'
    $frontend = Start-Process `
        -FilePath $node.Source `
        -ArgumentList $vite,'--host','127.0.0.1','--port','5173','--strictPort' `
        -WorkingDirectory (Join-Path $ProjectRoot 'frontend') `
        -RedirectStandardOutput (Join-Path $ProjectRoot 'logs\frontend.out.log') `
        -RedirectStandardError (Join-Path $ProjectRoot 'logs\frontend.err.log') `
        -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath $frontendPidFile -Value $frontend.Id
    $startedFrontend = $true
    Write-Host "Frontend started (PID $($frontend.Id))."
} else {
    Write-Host 'Frontend is already running.'
}

Write-Host 'Allow up to 20 seconds on first start.'
Start-Sleep -Seconds 3
if ($startedOllama) { Set-ListenerPid 11434 $ollamaPidFile }
if ($startedBackend) { Set-ListenerPid 8000 $backendPidFile }
if ($startedFrontend) { Set-ListenerPid 5173 $frontendPidFile }
Write-Host 'Open http://127.0.0.1:5173'
Write-Host 'Stop with scripts\stop.ps1'

