$ErrorActionPreference = 'Stop'
try {
    $atlasHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/api/health' -TimeoutSec 2
    $atlasRoot = Split-Path -Parent $PSScriptRoot
    if ($atlasHealth.app -eq 'obsidian-learning-atlas' -and $atlasHealth.root -eq $atlasRoot) {
        Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8765/api/stop' -TimeoutSec 2 | Out-Null
    }
} catch { }
