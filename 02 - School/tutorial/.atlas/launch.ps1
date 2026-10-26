$ErrorActionPreference = 'Stop'
$atlasRoot = Split-Path -Parent $PSScriptRoot
$atlasUrl = 'http://127.0.0.1:8765/'
$atlasHealth = $null
try { $atlasHealth = Invoke-RestMethod -Uri ($atlasUrl + 'api/health') -TimeoutSec 2 } catch {}
if ($atlasHealth) {
    if ($atlasHealth.app -ne 'obsidian-learning-atlas' -or $atlasHealth.root -ne $atlasRoot) {
        throw '端口 8765 已被其他服务占用，未启动。'
    }
} else {
    $atlasPython = (Get-Command python -ErrorAction Stop).Source
    $atlasPythonHidden = Join-Path (Split-Path $atlasPython -Parent) 'pythonw.exe'
    if (Test-Path -LiteralPath $atlasPythonHidden) { $atlasPython = $atlasPythonHidden }
    $atlasScript = Join-Path $PSScriptRoot 'sync_atlas.py'
    $atlasArguments = '"' + $atlasScript + '" --root "' + $atlasRoot + '"'
    Start-Process -FilePath $atlasPython -ArgumentList $atlasArguments -WindowStyle Hidden
    for ($atlasAttempt=0; $atlasAttempt -lt 20; $atlasAttempt++) {
        Start-Sleep -Milliseconds 250
        try { $atlasHealth = Invoke-RestMethod -Uri ($atlasUrl+'api/health') -TimeoutSec 1; break } catch {}
    }
    if (-not $atlasHealth) { throw '本地同步服务没有启动，请检查 Python 是否可用。' }
}
Start-Process $atlasUrl
