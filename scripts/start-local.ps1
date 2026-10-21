# Starts this project only. Existing unknown listeners are never replaced.
. (Join-Path $PSScriptRoot 'local-common.ps1')
$lifecycleLock = Enter-LocalLifecycle
try {
$python = Join-Path $ProjectRoot '.venv/Scripts/python.exe'
$node = (Get-Command node -ErrorAction Stop).Source
$next = Join-Path $ProjectRoot 'node_modules/next/dist/bin/next'
if (!(Test-Path -LiteralPath $python) -or !(Test-Path -LiteralPath $next)) {
    throw 'Install dependencies using docs/LOCAL_STARTUP.md first.'
}
& $python (Join-Path $PSScriptRoot 'local_probe.py') --configuration-only
if ($LASTEXITCODE -ne 0) { throw 'Private local configuration is incomplete or mismatched.' }
$entries = @(Read-LocalState)
[IO.Directory]::CreateDirectory((Join-Path $ProjectRoot 'artifacts')) | Out-Null
$roles = @(
    @{role='backend'; port=5100; exe=$python; marker=(Join-Path $ProjectRoot 'apps/api/serve.py'); args=@(('"{0}"' -f (Join-Path $ProjectRoot 'apps/api/serve.py')))},
    @{role='frontend'; port=3200; exe=$node; marker=(Join-Path $ProjectRoot 'apps/web'); args=@(('"{0}"' -f $next),'dev',('"{0}"' -f (Join-Path $ProjectRoot 'apps/web')),'--webpack','--hostname','127.0.0.1','--port','3200')}
)
# Validate every listener before starting either service.
foreach ($role in $roles) {
    $entry = @($entries | Where-Object { $_.role -eq $role.role })
    $running = $entry.Count -eq 1 -and $null -ne (Get-RecordedProcess $entry[0])
    $listeners = @(Get-NetTCPConnection -LocalPort $role.port -State Listen -ErrorAction SilentlyContinue)
    if ($listeners.Count -and (!$running -or @($listeners | Where-Object { !(Test-ListenerOwner $_ $entry[0]) }).Count)) {
        throw "Port $($role.port) has an unrecorded listener. No process was stopped."
    }
}
foreach ($role in $roles) {
    $entry = @($entries | Where-Object { $_.role -eq $role.role })
    if ($entry.Count -eq 1 -and $null -ne (Get-RecordedProcess $entry[0])) {
        Write-Output "$($role.role) already running; no duplicate started."
        continue
    }
    $saved = @{}
    $overrides = @{PORT='5100'; HOST='127.0.0.1'; NEXT_TELEMETRY_DISABLED='1'; REVIEW_DIST='.next-local'; SUMMARY_ALLOW_PAID='false'; SUMMARY_FALLBACK_ENABLED='false'}
    try {
        foreach ($key in $overrides.Keys) {
            $saved[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, $overrides[$key], 'Process')
        }
        $process = Start-Process -FilePath $role.exe -ArgumentList $role.args -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $ProjectRoot "artifacts/local-managed-$($role.role).log") `
            -RedirectStandardError (Join-Path $ProjectRoot "artifacts/local-managed-$($role.role)-error.log")
    } finally {
        foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key, $saved[$key], 'Process') }
    }
    $item = Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)"
    if (!$item) { throw "$($role.role) exited; inspect its private log." }
    $entries = @($entries | Where-Object { $_.role -ne $role.role }) + @(@{
        role=$role.role; pid=$item.ProcessId; created=$item.CreationDate.ToUniversalTime().ToString('o');
        image=[IO.Path]::GetFileName($item.ExecutablePath); marker=$role.marker
    })
    Write-LocalState $entries
    Wait-LocalUrl $(if ($role.role -eq 'backend') {'http://127.0.0.1:5100/health'} else {'http://127.0.0.1:3200/'})
}
& (Join-Path $PSScriptRoot 'check-local.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Services started but runtime checks failed.' }

} finally { $lifecycleLock.Dispose() }
