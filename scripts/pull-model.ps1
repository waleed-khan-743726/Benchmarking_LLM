param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('qwen2.5:0.5b','qwen3:0.6b','smollm2:1.7b-instruct-q4_K_M')]
    [string]$Model
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = 'D:\Robot_Navigation_FYP'
. (Join-Path $ProjectRoot 'scripts\project-env.ps1')

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    throw 'Ollama is not installed or not on PATH. No download was started.'
}

$sizesMB = @{
    'qwen2.5:0.5b' = 398
    'qwen3:0.6b' = 523
    'smollm2:1.7b-instruct-q4_K_M' = 1100
}
$drive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
$freeMB = $drive.FreeSpace / 1MB
$requiredMB = $sizesMB[$Model] + 5120
if ($freeMB -lt $requiredMB) {
    throw "Insufficient D: space. $Model needs approximately $($sizesMB[$Model]) MB plus a 5 GB safety margin."
}

Write-Host "Model storage: $env:OLLAMA_MODELS"
Write-Host ("D: free before pull: {0} GB" -f [math]::Round($drive.FreeSpace / 1GB, 2))
& $ollama.Source pull $Model
if ($LASTEXITCODE -ne 0) { throw "Ollama pull failed with exit code $LASTEXITCODE" }
Write-Host 'Pull completed. Use the Model Laboratory health check before benchmarking.'

