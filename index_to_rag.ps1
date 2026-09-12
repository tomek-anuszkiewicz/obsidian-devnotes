<#
.SYNOPSIS
    Indexes the Obsidian knowledge vault into the local Qdrant RAG vector database.

.DESCRIPTION
    Scans the 5-Layer System Stack (01..05+) and root navigational notes,
    strictly enforcing the One-Way Privacy Membrane by guaranteeing that
    _Private/ and any sensitive private notes are 100% excluded from RAG ingestion.

.PARAMETER Strict
    If specified, strictly indexes only the 5 canonical layers:
      • 01 Substrate & Mechanical Sympathy
      • 02 Harness, Governance & Verification
      • 03 Runtime Mesh & Observability
      • 04 Model Cognition & Latent Space
      • 05 Operator Psychology & Macro-Economics
    Default: Universal mode (dynamically discovers all numbered folders '^[0-9]{2}').

.PARAMETER Reindex
    Force re-indexing of all files (ignores SHA256 cache).

.PARAMETER Status
    Check Qdrant database status and vector counts.

.PARAMETER ListSources
    List all indexed sources in the Qdrant database.

.PARAMETER NoRootNotes
    Do not index root-level notes (_Explore.md, Preamble.md).

.PARAMETER AmigaRepo
    Path to the Amiga emulator repository containing tools/rag.
    Defaults to $env:AMIGA_REPO_DIR or 'D:\Programowanie\Amiga'.
#>

[CmdletBinding()]
param(
    [switch]$Strict,
    [switch]$Reindex,
    [switch]$Status,
    [switch]$ListSources,
    [switch]$NoRootNotes,
    [string]$AmigaRepo = $env:AMIGA_REPO_DIR
)

$VaultRoot = $PSScriptRoot
if (-not $VaultRoot) {
    $VaultRoot = (Get-Location).Path
}

# 1. Resolve Amiga repository root
if (-not $AmigaRepo) {
    $Candidate = "D:\Programowanie\Amiga"
    if (Test-Path $Candidate) {
        $AmigaRepo = $Candidate
    }
}

if (-not (Test-Path $AmigaRepo)) {
    Write-Error "Amiga repository not found at '$AmigaRepo'. Please set `$env:AMIGA_REPO_DIR or pass -AmigaRepo."
    exit 1
}

$RagScript = Join-Path $AmigaRepo "tools\rag\bin\amiga_rag.ps1"
if (-not (Test-Path $RagScript)) {
    Write-Error "RAG launcher not found at '$RagScript'."
    exit 1
}

# 2. Fast pass-through options
if ($Status) {
    & $RagScript --status
    exit $LASTEXITCODE
}

if ($ListSources) {
    & $RagScript --list-sources
    exit $LASTEXITCODE
}

# 3. Canonical 5-Layer System Stack (Strict List)
$CanonicalLayers = @(
    '01 Substrate & Mechanical Sympathy',
    '02 Harness, Governance & Verification',
    '03 Runtime Mesh & Observability',
    '04 Model Cognition & Latent Space',
    '05 Operator Psychology & Macro-Economics'
)

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " 🧠 Obsidian Vault RAG Indexer (Qdrant & FastEmbed)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Vault Path:       $VaultRoot"
Write-Host " RAG Tool:         $RagScript"
Write-Host " Selection Mode:   " -NoNewline
if ($Strict) {
    Write-Host "STRICT (Explicit 5 Canonical Layers)" -ForegroundColor Yellow
} else {
    Write-Host "UNIVERSAL (All Numbered Layers ^[0-9]{2})" -ForegroundColor Green
}

# 4. Discover target folders
$TargetFolders = @()
if ($Strict) {
    foreach ($layer in $CanonicalLayers) {
        $p = Join-Path $VaultRoot $layer
        if (Test-Path $p) {
            $TargetFolders += $layer
        } else {
            Write-Warning "Canonical layer folder not found on disk: $layer"
        }
    }
} else {
    $allDirs = Get-ChildItem -Path $VaultRoot -Directory
    foreach ($dir in $allDirs) {
        # Check if folder name starts with 2 digits
        if ($dir.Name -match '^[0-9]{2}') {
            # Privacy Membrane Guard: Hard reject if name contains 'private' or starts with '_'
            if ($dir.Name -like '*private*' -or $dir.Name.StartsWith('_')) {
                Write-Warning "Skipping prohibited private directory: $($dir.Name)"
                continue
            }
            $TargetFolders += $dir.Name
        }
    }
}

# Sort folders alphabetically/numerically
$TargetFolders = $TargetFolders | Sort-Object

Write-Host " Target Layers:    $($TargetFolders.Count) layer folder(s):" -ForegroundColor Green
foreach ($f in $TargetFolders) {
    Write-Host "   • $f" -ForegroundColor DarkCyan
}

# 5. One-Way Privacy Membrane Enforcement
$PrivateDir = Join-Path $VaultRoot "_Private"
if (Test-Path $PrivateDir) {
    Write-Host " Privacy Membrane: " -NoNewline
    Write-Host "ACTIVE" -ForegroundColor Green -NoNewline
    Write-Host " (Directory '_Private' is strictly excluded from RAG)" -ForegroundColor Yellow
}

# Safety assertion: verify zero private directories in target folders
foreach ($f in $TargetFolders) {
    if ($f -like '*private*' -or $f.StartsWith('_')) {
        Write-Error "CRITICAL SAFETY VIOLATION: '$f' contains private pattern! Aborting."
        exit 1
    }
}

# 6. Build arguments for amiga_rag.ps1
$RagArgs = @(
    $VaultRoot,
    "--source", "obsidian",
    "--exclude", "_Private", "private", ".obsidian", ".smart-env", ".agents", ".antigravity",
    "--include-dirs"
)
$RagArgs += $TargetFolders

if ($Reindex) {
    $RagArgs += "--reindex"
}

if ($NoRootNotes) {
    $RagArgs += "--no-root-notes"
}

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 7. Execute RAG indexing
& $RagScript @RagArgs
$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ Obsidian Vault successfully indexed into Qdrant RAG database!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Indexing failed with exit code $ExitCode." -ForegroundColor Red
}

exit $ExitCode
