<#
.SYNOPSIS
    Updates the local RAG index for this vault's six main directories.

.DESCRIPTION
    This script has no options. It uses rag_qdrant to index only the explicitly
    listed main directories below. rag_qdrant recursively scans each supplied
    directory and excludes built-in system and tool directories.

    A new numbered top-level directory is treated as a required script update:
    decide whether to add it to $IndexedDirectories or intentionally ignore it,
    then rerun the script.
#>

param()

if ($args.Count -gt 0) {
    Write-Error "update_rag_index.ps1 accepts no arguments. Update its fixed configuration instead."
    exit 1
}

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
}
if (-not $ScriptDir) {
    $ScriptDir = (Get-Location).Path
}

$VaultRoot = Split-Path -Parent $ScriptDir
if (-not (Test-Path -LiteralPath (Join-Path $VaultRoot '01 Architecture & Code') -PathType Container)) {
    if (Test-Path -LiteralPath (Join-Path (Get-Location).Path '01 Architecture & Code') -PathType Container) {
        $VaultRoot = (Get-Location).Path
    }
}

$IndexedDirectories = @(
    '01 Architecture & Code',
    '02 Testing & Code Review',
    '03 Systems & Infrastructure',
    '04 Prompts, Context & Models',
    '05 Engineering Economics & Future',
    '06 Ideas & Speculation'
)
$EnvironmentFile = Join-Path $VaultRoot '.env'
if (-not (Test-Path -LiteralPath $EnvironmentFile -PathType Leaf)) {
    Write-Error "The .env file is missing. Define RAG_CACHE_FILE before indexing."
    exit 1
}

$CacheFileDefinition = Get-Content -LiteralPath $EnvironmentFile |
    Where-Object { $_ -match '^\s*RAG_CACHE_FILE\s*=' } |
    Select-Object -First 1

if ([string]::IsNullOrWhiteSpace($CacheFileDefinition)) {
    Write-Error "RAG_CACHE_FILE is not defined in .env. Define it before indexing."
    exit 1
}

$IndexStateFile = ($CacheFileDefinition -replace '^\s*RAG_CACHE_FILE\s*=\s*', '').Trim()
if ([string]::IsNullOrWhiteSpace($IndexStateFile)) {
    Write-Error "RAG_CACHE_FILE is empty in .env. Set it to the index state file path before indexing."
    exit 1
}

# A numbered root directory is a new main section. Do not index it implicitly:
# its inclusion must be a conscious change to the list above.
$UnexpectedMainDirectories = @(
    Get-ChildItem -LiteralPath $VaultRoot -Directory |
        Where-Object { $_.Name -match '^\d{2}(?:[ _-]|$)' -and $_.Name -notin $IndexedDirectories }
)

if ($UnexpectedMainDirectories.Count -gt 0) {
    $Names = $UnexpectedMainDirectories.Name -join ', '
    Write-Error "Unexpected main directory/directories: $Names. Update update_rag_index.ps1 to add or intentionally ignore them."
    exit 1
}

$MissingIndexedDirectories = @(
    $IndexedDirectories | Where-Object { -not (Test-Path -LiteralPath (Join-Path $VaultRoot $_) -PathType Container) }
)

if ($MissingIndexedDirectories.Count -gt 0) {
    $Names = $MissingIndexedDirectories -join ', '
    Write-Error "Configured main directory/directories are missing: $Names. Update update_rag_index.ps1 before indexing."
    exit 1
}

try {
    $RagCommand = Get-Command rag_qdrant -ErrorAction Stop
} catch {
    Write-Error "The rag_qdrant command is not available on PATH. Install or expose it before indexing."
    exit 1
}

Write-Host "Updating the RAG index from:" -ForegroundColor Cyan
$IndexedDirectories | ForEach-Object { Write-Host "  - $_" }
Write-Host "Using: $($RagCommand.Source)" -ForegroundColor DarkCyan
Write-Host "Index state: $IndexStateFile" -ForegroundColor DarkCyan
$RagInvocation = if ([string]::IsNullOrWhiteSpace($RagCommand.Path)) { $RagCommand.Name } else { $RagCommand.Path }

foreach ($DirectoryName in $IndexedDirectories) {
    $DirectoryPath = Join-Path $VaultRoot $DirectoryName
    $RagArgs = @(
        $DirectoryPath,
        '--source', 'devnotes',
        '--index-json', $IndexStateFile
    )

    Write-Host "Indexing: $DirectoryName" -ForegroundColor Cyan

    if ($RagCommand.CommandType -eq 'ExternalScript' -and $RagCommand.Path.EndsWith('.ps1', [System.StringComparison]::OrdinalIgnoreCase)) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $RagCommand.Path @RagArgs
    } else {
        & $RagInvocation @RagArgs
    }

    $RagSucceeded = $?
    $ExitCode = $LASTEXITCODE

    if (-not $RagSucceeded -or ($null -ne $ExitCode -and $ExitCode -ne 0)) {
        if ($null -eq $ExitCode) {
            Write-Error "RAG indexing failed for '$DirectoryName' without returning an exit code."
            exit 1
        }

        Write-Error "RAG indexing failed for '$DirectoryName' with exit code $ExitCode."
        exit $ExitCode
    }
}

Write-Host "RAG index updated successfully." -ForegroundColor Green
