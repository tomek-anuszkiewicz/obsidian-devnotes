<#
.SYNOPSIS
    Updates the local RAG index for this vault's five main directories.

.DESCRIPTION
    This script has no options. It indexes only the explicitly listed main
    directories below and excludes private and tool metadata directories.

    A new numbered top-level directory is treated as a required script update:
    decide whether to add it to $IndexedDirectories or intentionally ignore it,
    then rerun the script.
#>

param()

if ($args.Count -gt 0) {
    Write-Error "index_to_rag.ps1 accepts no arguments. Update its fixed configuration instead."
    exit 1
}

$VaultRoot = $PSScriptRoot
if (-not $VaultRoot) {
    $VaultRoot = (Get-Location).Path
}

$IndexedDirectories = @(
    '01 Architecture & Code',
    '02 Testing & Code Review',
    '03 Systems & Infrastructure',
    '04 Prompts, Context & Models',
    '05 Engineering Economics & Future'
)

# A numbered root directory is a new main section. Do not index it implicitly:
# its inclusion must be a conscious change to the list above.
$UnexpectedMainDirectories = @(
    Get-ChildItem -LiteralPath $VaultRoot -Directory |
        Where-Object { $_.Name -match '^\d{2}(?:[ _-]|$)' -and $_.Name -notin $IndexedDirectories }
)

if ($UnexpectedMainDirectories.Count -gt 0) {
    $Names = $UnexpectedMainDirectories.Name -join ', '
    Write-Error "Unexpected main directory/directories: $Names. Update index_to_rag.ps1 to add or intentionally ignore them."
    exit 1
}

$MissingIndexedDirectories = @(
    $IndexedDirectories | Where-Object { -not (Test-Path -LiteralPath (Join-Path $VaultRoot $_) -PathType Container) }
)

if ($MissingIndexedDirectories.Count -gt 0) {
    $Names = $MissingIndexedDirectories -join ', '
    Write-Error "Configured main directory/directories are missing: $Names. Update index_to_rag.ps1 before indexing."
    exit 1
}

try {
    $RagCommand = Get-Command amiga_rag -ErrorAction Stop
} catch {
    Write-Error "The amiga_rag command is not available on PATH. Install or expose it before indexing."
    exit 1
}

$RagArgs = @(
    $VaultRoot,
    '--source', 'obsidian',
    '--exclude', '_Private', 'private', '.obsidian', '.smart-env', '.agents', '.antigravity',
    '--no-root-notes',
    '--include-dirs'
)
$RagArgs += $IndexedDirectories

Write-Host "Updating the RAG index from:" -ForegroundColor Cyan
$IndexedDirectories | ForEach-Object { Write-Host "  - $_" }
Write-Host "Using: $($RagCommand.Source)" -ForegroundColor DarkCyan

& amiga_rag @RagArgs
$RagSucceeded = $?
$ExitCode = $LASTEXITCODE

if (-not $RagSucceeded -or ($null -ne $ExitCode -and $ExitCode -ne 0)) {
    if ($null -eq $ExitCode) {
        Write-Error "RAG indexing failed without returning an exit code."
        exit 1
    }

    Write-Error "RAG indexing failed with exit code $ExitCode."
    exit $ExitCode
}

Write-Host "RAG index updated successfully." -ForegroundColor Green
