$ErrorActionPreference = 'Continue'
$ProjectRoot = 'D:\Robot_Navigation_FYP'

$targets = @(
    @{ File = (Join-Path $ProjectRoot '.tmp\backend.pid'); Expected = 'uvicorn backend.main:app'; Name = 'Backend' },
    @{ File = (Join-Path $ProjectRoot '.tmp\frontend.pid'); Expected = 'vite.js*--host*127.0.0.1'; Name = 'Frontend' },
    @{ File = (Join-Path $ProjectRoot '.tmp\ollama.pid'); Expected = 'ollama.exe*serve'; Name = 'Ollama' }
)

foreach ($target in $targets) {
    if (-not (Test-Path -LiteralPath $target.File)) {
        Write-Host "$($target.Name): no PID file."
        continue
    }
    $processId = [int](Get-Content -LiteralPath $target.File -Raw)
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$processId" -ErrorAction SilentlyContinue
    if ($process -and $process.CommandLine -like "*$($target.Expected)*") {
        Stop-Process -Id $processId
        Write-Host "$($target.Name) stopped (PID $processId)."
    } elseif ($process) {
        Write-Warning "$($target.Name) PID now belongs to another command; it was not stopped."
    } else {
        Write-Host "$($target.Name): process is not running."
    }
    Remove-Item -LiteralPath $target.File -Force -ErrorAction SilentlyContinue
}

