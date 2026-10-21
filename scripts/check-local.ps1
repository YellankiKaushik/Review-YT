. (Join-Path $PSScriptRoot 'local-common.ps1')
$python = Join-Path $ProjectRoot '.venv/Scripts/python.exe'
& $python (Join-Path $PSScriptRoot 'local_probe.py')
if ($LASTEXITCODE -ne 0) { throw 'Local checks failed; run scripts/start-local.ps1 or inspect private logs.' }
