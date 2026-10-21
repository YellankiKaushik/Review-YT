param([switch]$LiveYouTube, [string]$VideoId='rfscVS0vtbw', [switch]$SkipBuild)
. (Join-Path $PSScriptRoot 'local-common.ps1')
# Independent lock/ports/state: never adopt or stop development/historical listeners.
$runtime = Join-Path $ProjectRoot '.work/production-runtime'
[IO.Directory]::CreateDirectory($runtime) | Out-Null
$lock = [IO.File]::Open((Join-Path $runtime 'lifecycle.lock'), 'OpenOrCreate', 'ReadWrite', 'None')
$owned = @()
$saved = @{}
function Start-Owned($Executable, $Arguments, $Marker, $Label) {
    $process = Start-Process -FilePath $Executable -ArgumentList $Arguments -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $ProjectRoot "artifacts/production-$Label.log") `
        -RedirectStandardError (Join-Path $ProjectRoot "artifacts/production-$Label-error.log")
    $item = Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)"
    if (!$item -or !$item.CommandLine.Contains($Marker)) { throw "Could not record $Label launcher." }
    return @{pid=$item.ProcessId; created=$item.CreationDate; marker=$Marker; image=$item.ExecutablePath}
}
function Stop-Owned($Entry) {
    $root = Get-CimInstance Win32_Process -Filter "ProcessId = $($Entry.pid)" -ErrorAction SilentlyContinue
    if (!$root) { return }
    if ($root.CreationDate -ne $Entry.created -or $root.ExecutablePath -ne $Entry.image -or !$root.CommandLine.Contains($Entry.marker)) {
        Write-Warning 'Process identity changed; refusing cleanup of that PID.'
        return
    }
    $all = @(Get-CimInstance Win32_Process)
    $tree = @($root)
    for ($index=0; $index -lt $tree.Count; $index++) {
        $parent = $tree[$index]
        $tree += @($all | Where-Object { $_.ParentProcessId -eq $parent.ProcessId -and $_.CreationDate -ge $parent.CreationDate -and $_.ProcessId -notin @($tree.ProcessId) })
    }
    foreach ($item in $tree) {
        $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($item.ProcessId)" -ErrorAction SilentlyContinue
        if ($current -and $current.CreationDate -eq $item.CreationDate -and $current.ExecutablePath -eq $item.ExecutablePath) {
            Stop-Process -Id $current.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}
try {
    foreach ($port in @(3202,5102,5103)) {
        if (@(Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue).Count) { throw "Port $port is occupied; nothing stopped." }
    }
    $python = Join-Path $ProjectRoot '.venv/Scripts/python.exe'
    $node = (Get-Command node).Source
    $opensslCommand = Get-Command openssl -ErrorAction SilentlyContinue
    $openssl = if ($opensslCommand) { $opensslCommand.Source } else { 'C:\Program Files\Git\usr\bin\openssl.exe' }
    if (!(Test-Path -LiteralPath $openssl)) { throw 'OpenSSL not available; production TLS verification NOT EXECUTED. Install official OpenSSL or Git for Windows.' }
    [IO.Directory]::CreateDirectory((Join-Path $ProjectRoot 'artifacts')) | Out-Null
    $cert = Join-Path $runtime 'cert.pem'
    $keyFile = Join-Path $runtime 'key.pem'
    $certArgs = @('req','-x509','-newkey','rsa:2048','-nodes','-days','2','-keyout',('"{0}"' -f $keyFile),'-out',('"{0}"' -f $cert),'-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost','-addext','basicConstraints=critical,CA:TRUE')
    $generator = Start-Process -FilePath $openssl -ArgumentList $certArgs -WindowStyle Hidden -Wait -PassThru `
        -RedirectStandardOutput (Join-Path $ProjectRoot 'artifacts/production-openssl.log') `
        -RedirectStandardError (Join-Path $ProjectRoot 'artifacts/production-openssl-error.log')
    if ($generator.ExitCode -ne 0) { throw 'Temporary local TLS certificate creation failed.' }
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $localToken = [Convert]::ToBase64String($bytes)
    $overrides = @{
        HOST='127.0.0.1'; PORT='5102'; CACHE_PATH=(Join-Path $runtime 'reviews.sqlite');
        BACKEND_URL='https://127.0.0.1:5103'; BACKEND_API_TOKEN=$localToken;
        SUMMARY_PROVIDER='disabled'; SUMMARY_ENABLED_PROVIDERS='disabled';
        SUMMARY_ALLOW_PAID='false'; SUMMARY_FALLBACK_ENABLED='false'; TRANSCRIPTS_ENABLED='false';
        REVIEW_LOCAL_TEST='false'; REVIEW_DIST='.next'; NODE_EXTRA_CA_CERTS=$cert; NEXT_TELEMETRY_DISABLED='1'
    }
    foreach ($name in $overrides.Keys) {
        $saved[$name] = [Environment]::GetEnvironmentVariable($name,'Process')
        [Environment]::SetEnvironmentVariable($name,$overrides[$name],'Process')
    }
    if (!$SkipBuild) {
        Push-Location $ProjectRoot
        try { & npm run build; if ($LASTEXITCODE -ne 0) { throw 'Production build failed.' } } finally { Pop-Location }
    } elseif (!(Test-Path (Join-Path $ProjectRoot 'apps/web/.next/BUILD_ID'))) { throw 'No optimized build; omit -SkipBuild.' }
    $serve = Join-Path $ProjectRoot 'apps/api/serve.py'
    $owned += Start-Owned $python @(('"{0}"' -f $serve)) $serve 'api'
    Wait-LocalUrl 'http://127.0.0.1:5102/health'
    $bridge = Join-Path $PSScriptRoot 'local_tls_bridge.py'
    $owned += Start-Owned $python @(('"{0}"' -f $bridge),'--directory',('"{0}"' -f $runtime)) $bridge 'tls'
    $next = Join-Path $ProjectRoot 'node_modules/next/dist/bin/next'
    $web = Join-Path $ProjectRoot 'apps/web'
    $owned += Start-Owned $node @(('"{0}"' -f $next),'start',('"{0}"' -f $web),'--hostname','127.0.0.1','--port','3202') $web 'web'
    Wait-LocalUrl 'http://127.0.0.1:3202/'
    $smokeArgs = @((Join-Path $PSScriptRoot 'smoke-public.py'),'--frontend','http://127.0.0.1:3202','--backend','https://127.0.0.1:5103','--local','--ca-file',$cert,'--browser','--output',(Join-Path $ProjectRoot 'artifacts/production-local.json'))
    if ($LiveYouTube) { $smokeArgs += @('--live-video',$VideoId) }
    & $python @smokeArgs
    if ($LASTEXITCODE -ne 0) { throw 'Production-mode verification failed; inspect artifacts/production-local.json.' }
    $allProcesses = @(Get-CimInstance Win32_Process)
    $resources = foreach ($entry in $owned) {
        $tree = @($allProcesses | Where-Object { $_.ProcessId -eq $entry.pid -and $_.CreationDate -eq $entry.created })
        for ($index=0; $index -lt $tree.Count; $index++) {
            $parent = $tree[$index]
            $tree += @($allProcesses | Where-Object { $_.ParentProcessId -eq $parent.ProcessId -and $_.CreationDate -ge $parent.CreationDate -and $_.ProcessId -notin @($tree.ProcessId) })
        }
        @{entryPoint=[IO.Path]::GetFileName($entry.marker); processes=$tree.Count; workingSetMiB=[math]::Round(($tree | Measure-Object WorkingSetSize -Sum).Sum/1MB,2)}
    }
    $resources | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $ProjectRoot 'artifacts/production-resources.json')
    Write-Output 'PASS: optimized Next production server -> verified local HTTPS -> actual Waitress; no REVIEW_LOCAL_TEST bypass. This is NOT a public deployment.'
} finally {
    for ($index=$owned.Count-1; $index -ge 0; $index--) { Stop-Owned $owned[$index] }
    foreach ($name in $saved.Keys) { [Environment]::SetEnvironmentVariable($name,$saved[$name],'Process') }
    $lock.Dispose()
}
