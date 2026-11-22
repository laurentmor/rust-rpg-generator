#requires -Version 5.1
[CmdletBinding()]
param(
    [string]$Version = '1.0.0-rc1',
    [int]$Heartbeat = 5,
    [string]$OutputDirectory = '',
    [switch]$SkipCertification
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = $PSScriptRoot
if (-not $OutputDirectory) { $OutputDirectory = Join-Path $root 'dist' }
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
$start = Get-Date
$report = Join-Path $OutputDirectory 'release-report.json'
$log = Join-Path $OutputDirectory 'release-check.log'
$zip = Join-Path $OutputDirectory "rust-rpg-kit-v$Version.zip"
$manifest = Join-Path $OutputDirectory "rust-rpg-v$Version-manifest.json"
function Step([string]$message) { Write-Host "`n[$((Get-Date).ToString('HH:mm:ss'))] $message" -ForegroundColor Cyan }
function Check([string]$path) { if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Fichier requis absent : $path" } }
function RunPython([string[]]$arguments) {
    & $script:python @arguments
    if ($LASTEXITCODE -ne 0) { throw "Commande Python échouée (code $LASTEXITCODE). Publication interrompue." }
}
try {
    Step 'Rust RPG - Préparation automatisée de la release'
    Write-Host "Source  : $root"
    Write-Host "Sortie  : $OutputDirectory"
    Write-Host "Version : $Version"
    if ($Heartbeat -lt 1) { throw 'Heartbeat doit être supérieur ou égal à 1.' }
    if ($Version -notmatch '^[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?$') { throw 'Version invalide (ex. 1.0.0-rc1).' }
    foreach ($file in @('release_check.py', 'prepare_release.py', 'scaffold.py', 'audit.py')) { Check (Join-Path $root $file) }
    $script:python = $null
    foreach ($candidate in @('python', 'py')) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) { $script:python = $candidate; break }
    }
    if (-not $script:python) { throw 'Python introuvable dans PATH.' }
    if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) { throw 'Cargo introuvable dans PATH.' }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git introuvable dans PATH.' }
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    if (-not $SkipCertification) {
        Step '1/4 - Certification complète : tests Python, 120 niveaux, 360 commandes Cargo'
        Write-Host 'Cela peut durer plusieurs minutes. Les résultats apparaîtront en direct.'
        RunPython @('-u', (Join-Path $root 'release_check.py'), '--report', $report, '--log', $log, '--heartbeat', "$Heartbeat")
    } else {
        Step '1/4 - Réutilisation explicite du rapport existant'
        Check $report
    }
    Step '2/4 - Contrôle du rapport de certification'
    Check $report
    $data = Get-Content -LiteralPath $report -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($data.status -ne 'rust_verified' -or $data.audit.cargo_checked -ne 360 -or $data.audit.cargo_failures.Count -ne 0) {
        throw 'Le rapport ne certifie pas 360 validations Cargo réussies. Archive non publiée.'
    }
    Write-Host 'Rapport certifié : 360/360 Cargo, aucun échec.' -ForegroundColor Green
    Step '3/4 - Création de l archive ZIP depuis les sources du kit'
    $staging = Join-Path ([System.IO.Path]::GetTempPath()) ('rust-rpg-package-' + [guid]::NewGuid().ToString('N'))
    try {
        $packageRoot = Join-Path $staging 'rust-rpg-kit'
        New-Item -ItemType Directory -Path $packageRoot -Force | Out-Null
        # Inclut les sources du kit, mais pas les rapports, caches, ZIP, secrets ou fichiers personnels.
        $sources = Get-ChildItem -LiteralPath $root -File | Where-Object {
            $_.Extension -in @('.py', '.md', '.ps1')
        }
        if ($sources.Count -lt 4) { throw 'Pas assez de fichiers source à empaqueter.' }
        foreach ($source in $sources) {
            Copy-Item -LiteralPath $source.FullName -Destination (Join-Path $packageRoot $source.Name)
            Write-Host "  + $($source.Name)"
        }
        if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
        Compress-Archive -LiteralPath $packageRoot -DestinationPath $zip -CompressionLevel Optimal -Force
        Check $zip
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $archive = [System.IO.Compression.ZipFile]::OpenRead($zip)
        try {
            if ($archive.Entries.Count -lt $sources.Count) { throw 'Archive incomplète.' }
            Write-Host "Archive ZIP : $($archive.Entries.Count) entrées" -ForegroundColor Green
        } finally { $archive.Dispose() }
    } finally {
        if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
    }
    Step '4/4 - Validation des 360 résultats et génération du manifeste SHA-256'
    RunPython @((Join-Path $root 'prepare_release.py'), '--report', $report, '--artifact', $zip, '--output', $manifest)
    Check $manifest
    Write-Host "`nRELEASE CANDIDATE PRÊTE" -ForegroundColor Green
    Write-Host "ZIP      : $zip"
    Write-Host "Rapport  : $report"
    Write-Host "Journal  : $log"
    Write-Host "Manifeste: $manifest"
    Write-Host "SHA-256  : $((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash)"
    Write-Host "Durée    : $([math]::Round(((Get-Date) - $start).TotalMinutes, 1)) minutes"
    Write-Host 'Note : les tests manuels FR/EN restent nécessaires avant une release stable.' -ForegroundColor Yellow
} catch {
    Write-Host "`nÉCHEC : $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Rapport : $report" -ForegroundColor Yellow
    Write-Host "Journal : $log" -ForegroundColor Yellow
    exit 1
}
