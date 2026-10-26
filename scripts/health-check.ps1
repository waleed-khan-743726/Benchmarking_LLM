$ErrorActionPreference = 'Continue'
$ProjectRoot = 'D:\Robot_Navigation_FYP'
. (Join-Path $ProjectRoot 'scripts\project-env.ps1')

Write-Host 'Storage paths'
Write-Host "  Project:       $ProjectRoot"
Write-Host "  Python:        $ProjectRoot\.venv"
Write-Host "  pip cache:     $env:PIP_CACHE_DIR"
Write-Host "  npm cache:     $env:npm_config_cache"
Write-Host "  temp:          $env:TEMP"
Write-Host "  Ollama models: $env:OLLAMA_MODELS"

$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
Write-Host ("  D: free:       {0} GB" -f [math]::Round($drive.FreeSpace / 1GB, 2))

try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5
    Write-Host "Backend: ready (version $($health.version))" -ForegroundColor Green
} catch {
    Write-Host 'Backend: unavailable' -ForegroundColor Yellow
}

try {
    $frontend = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 5
    Write-Host "Frontend: ready (HTTP $($frontend.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host 'Frontend: unavailable' -ForegroundColor Yellow
}

try {
    $tags = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3
    Write-Host "Ollama: ready ($($tags.models.Count) models detected)" -ForegroundColor Green
} catch {
    Write-Host 'Ollama: unavailable; offline simulator mode remains supported.' -ForegroundColor Yellow
}

