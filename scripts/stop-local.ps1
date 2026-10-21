# A PID alone is insufficient: validate creation time, command marker and image.
. (Join-Path $PSScriptRoot 'local-common.ps1')
$lifecycleLock = Enter-LocalLifecycle
try {
$entries = @(Read-LocalState)
$roots = @()
foreach ($entry in $entries) {
    $item = Get-RecordedProcess $entry
    if ($item) { $roots += $item }
}
$all = @(Get-CimInstance Win32_Process)
foreach ($root in $roots) {
    $tree = @($root)
    for ($index=0; $index -lt $tree.Count; $index++) {
        $parent = $tree[$index]
        $tree += @($all | Where-Object {
            $_.ParentProcessId -eq $parent.ProcessId -and $_.CreationDate -ge $parent.CreationDate -and
            $_.ProcessId -notin @($tree.ProcessId)
        })
    }
    # Stop the identified launcher first so it cannot respawn a child.
    foreach ($item in $tree) {
        $current = Get-CimInstance Win32_Process -Filter "ProcessId = $($item.ProcessId)" -ErrorAction SilentlyContinue
        if ($current -and $current.CreationDate -eq $item.CreationDate -and
            $current.ExecutablePath -eq $item.ExecutablePath) {
            Stop-Process -Id $current.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}
if (Test-Path -LiteralPath $LocalState) { Remove-Item -LiteralPath $LocalState }
Write-Output 'Stopped only recorded project launchers and their verified descendants (if running).'

} finally { $lifecycleLock.Dispose() }
