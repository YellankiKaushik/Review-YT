param(
    [Parameter(Mandatory=$true)][string]$FrontendUrl,
    [Parameter(Mandatory=$true)][string]$BackendUrl,
    [string]$LiveVideo,
    [switch]$Browser
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Join-Path $root '.venv/Scripts/python.exe'
$arguments = @((Join-Path $PSScriptRoot 'smoke-public.py'),'--frontend',$FrontendUrl,'--backend',$BackendUrl)
if ($LiveVideo) { $arguments += @('--live-video',$LiveVideo) }
if ($Browser) { $arguments += '--browser' }
# Optional BACKEND_API_TOKEN is inherited securely. Never pass it as an argument.
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw 'Public verification failed. Inspect artifacts/public-smoke.json.' }
