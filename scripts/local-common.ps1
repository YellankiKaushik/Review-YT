Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$LocalState = Join-Path $ProjectRoot '.work/local-services.json'
function Get-RecordedProcess($Entry) {
    $expected = @{backend=(Join-Path $ProjectRoot 'apps/api/serve.py'); frontend=(Join-Path $ProjectRoot 'apps/web')}
    if (!$expected.ContainsKey($Entry.role) -or $Entry.marker -ne $expected[$Entry.role]) {
        throw 'Recorded command is not an expected project entry point.'
    }
    $item = Get-CimInstance Win32_Process -Filter "ProcessId = $($Entry.pid)" -ErrorAction SilentlyContinue
    if (!$item) { return $null }
    if ($item.CreationDate.ToUniversalTime().ToString('o') -ne $Entry.created -or
        !$item.CommandLine -or !$item.CommandLine.Contains($Entry.marker) -or
        [IO.Path]::GetFileName($item.ExecutablePath) -ne $Entry.image) {
        throw "Process identity changed for $($Entry.role); refusing to manage it."
    }
    return $item
}
function Read-LocalState {
    if (!(Test-Path -LiteralPath $LocalState)) { return @() }
    $state = Get-Content -LiteralPath $LocalState -Raw | ConvertFrom-Json
    if ($state.root -ne $ProjectRoot) { throw 'State belongs to a different workspace.' }
    return @($state.processes)
}
function Write-LocalState($Entries) {
    [IO.Directory]::CreateDirectory((Split-Path $LocalState)) | Out-Null
    @{root=$ProjectRoot; processes=@($Entries)} | ConvertTo-Json -Depth 5 |
        Set-Content -LiteralPath $LocalState -Encoding UTF8
}
function Wait-LocalUrl($Url) {
    $deadline = [DateTime]::UtcNow.AddSeconds(60)
    do {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -eq 200) { return }
        } catch { }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    throw "Startup timed out at $Url. Inspect artifacts/local-managed-*.log privately."
}

function Test-ListenerOwner($Listener, $Entry) {
    $root = Get-RecordedProcess $Entry
    if (!$root) { return $false }
    $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($Listener.OwningProcess)"
    $visited = @{}
    while ($current -and !$visited.ContainsKey([string]$current.ProcessId)) {
        if ($current.ProcessId -eq $root.ProcessId) { return $true }
        if ($current.CreationDate -lt $root.CreationDate) { return $false }
        $visited[[string]$current.ProcessId] = $true
        $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($current.ParentProcessId)" -ErrorAction SilentlyContinue
    }
    return $false
}

function Enter-LocalLifecycle {
    [IO.Directory]::CreateDirectory((Join-Path $ProjectRoot '.work')) | Out-Null
    try {
        return [IO.File]::Open((Join-Path $ProjectRoot '.work/lifecycle.lock'), [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch { throw 'Another local start/stop operation is active; wait for it to finish.' }
}
