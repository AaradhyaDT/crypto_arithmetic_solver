<#
.SYNOPSIS
    Automated Git synchronization, secret scanner, and test verification engine for AI (Crypto-Arithmetic Solver).

.DESCRIPTION
    sync.ps1 - The central synchronization script for the AI / crypto_arithmetic_solver repository:
    https://github.com/AaradhyaDT/crypto_arithmetic_solver

    Capabilities:
    1. Pre-Commit Secret Scanner Guard: Prevents committing API keys, tokens, or private credentials.
    2. Unit Test Gate (-RunTests): Executes python tests/run_unit_tests.py prior to commit.
    3. Intelligent Conventional Commits: Auto-formats scoped commit messages (feat(solver), docs(solver), test(solver), etc.).
    4. Safe Rebase & Push: Pulls with --rebase --autostash before pushing to origin/main.
    5. Dry-Run Mode (-WhatIf): Previews changes, tests, and secret scan without altering git state.

.PARAMETER Message
    Custom commit message (alias: -m). If omitted, an intelligent conventional commit is generated.

.PARAMETER RunTests
    Runs python tests/run_unit_tests.py before staging and committing.

.PARAMETER PullOnly
    Pulls remote updates with --rebase --autostash without staging or pushing.

.PARAMETER PushOnly
    Pushes existing local commits without creating new commits.

.PARAMETER NoPush
    Stages and commits changes locally without pushing to origin.

.PARAMETER WhatIf
    Dry-run mode: inspects changes and runs secret scanner without altering git state.

.EXAMPLE
    .\sync.ps1                                   # Routine sync and push to origin/main
    .\sync.ps1 -RunTests                         # Run unit test suite then sync
    .\sync.ps1 -m "feat(solver): heuristic tune" # Custom commit message
    .\sync.ps1 -PullOnly                         # Safe pull only
    .\sync.ps1 -WhatIf                           # Dry-run preview
#>

[CmdletBinding()]
param (
    [Alias("m")]
    [string]$Message,

    [switch]$RunTests,
    [switch]$PullOnly,
    [switch]$PushOnly,
    [switch]$NoPush,
    [switch]$WhatIf
)

$ErrorActionPreference = "Continue"

function Write-Status {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = [System.ConsoleColor]::Cyan
    )
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor $Color
}

function Write-Notice {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Yellow)
}

function Write-Success {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Green)
}

function Write-Failure {
    param([string]$Message)
    Write-Status -Message $Message -Color ([System.ConsoleColor]::Red)
}

function Invoke-UnitTests {
    Write-Status "Running crypto-arithmetic unit tests (tests/run_unit_tests.py)..."
    $pythonCmd = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
    & $pythonCmd "tests/run_unit_tests.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Unit tests failed! Aborting sync to maintain repository correctness."
        exit $LASTEXITCODE
    }
    Write-Success "All unit tests passed successfully."
}

function Find-StagedSecrets {
    $stagedDiff = git diff --cached -U0 2>$null
    if (-not $stagedDiff) { return @() }

    $addedLines = $stagedDiff | Where-Object { $_ -match '^\+[^+]' } | ForEach-Object { $_.Substring(1) }
    if (-not $addedLines) { return @() }

    $secretPatterns = @(
        'AKIA[0-9A-Z]{16}',
        'sk-[a-zA-Z0-9]{20,}',
        'sk-ant-[a-zA-Z0-9\-]{20,}',
        'ghp_[a-zA-Z0-9]{36}',
        'github_pat_[a-zA-Z0-9_]{20,}',
        'AIza[0-9A-Za-z\-_]{35}',
        'xox[baprs]-[0-9a-zA-Z\-]{10,}',
        'GOCSPX-[a-zA-Z0-9\-_]{28,}',
        '-----BEGIN (RSA|EC|OPENSSH|PGP|DSA)? ?PRIVATE KEY-----',
        '(?i)(api[_-]?key|client_secret|access_token|refresh_token|password)\s*[:=]\s*[''"][^''"\s]{8,}[''"]'
    )

    $hits = @()
    foreach ($line in $addedLines) {
        foreach ($pattern in $secretPatterns) {
            if ($line -match $pattern) {
                $snippet = $line.Trim()
                $hits += [PSCustomObject]@{
                    Pattern = $pattern
                    Snippet = $snippet.Substring(0, [Math]::Min(60, $snippet.Length))
                }
                break
            }
        }
    }

    return @($hits)
}

function Get-AutoCommitMessage {
    $statusLines = git status --porcelain
    if (-not $statusLines) { return $null }

    $modifiedFiles = @()
    $addedFiles = @()
    $deletedFiles = @()

    foreach ($line in $statusLines) {
        if ($line.Length -lt 3) { continue }
        $status = $line.Substring(0, 2).Trim()
        $file = $line.Substring(3).Trim()
        $fileName = Split-Path $file -Leaf

        if ($status -match 'A|\?\?') { $addedFiles += $fileName }
        elseif ($status -match 'D') { $deletedFiles += $fileName }
        else { $modifiedFiles += $fileName }
    }

    $allChanged = @($addedFiles + $modifiedFiles + $deletedFiles)
    if (@($allChanged).Count -eq 0) { return $null }

    $prefix = "chore(solver)"
    if (@($addedFiles).Count -gt 0) { $prefix = "feat(solver)" }
    elseif ($modifiedFiles | Where-Object { $_ -match '\.md$' }) { $prefix = "docs(solver)" }
    elseif ($modifiedFiles | Where-Object { $_ -match '\.json$' }) { $prefix = "data(solver)" }
    elseif ($modifiedFiles | Where-Object { $_ -match 'test_.*\.py$' }) { $prefix = "test(solver)" }
    elseif ($modifiedFiles | Where-Object { $_ -match '\.py$' }) { $prefix = "feat(solver)" }
    elseif ($modifiedFiles | Where-Object { $_ -match '\.ps1|\.bat$' }) { $prefix = "ci(solver)" }

    $summary = ($allChanged | Select-Object -First 3) -join ", "
    if (@($allChanged).Count -gt 3) {
        $summary += " (+$(@($allChanged).Count - 3) more)"
    }

    return "$($prefix): update $($summary)"
}

# --- Main Flow ---
Write-Status "================================================================"
Write-Status "CRYPTO-ARITHMETIC SOLVER (AI) - Git & Verification Synchronizer"
Write-Status "================================================================"

$repoRoot = $PSScriptRoot
if (-not (Test-Path (Join-Path $repoRoot ".git"))) {
    Write-Failure "Error: Not a git repository ($repoRoot)."
    exit 1
}

# 1. Run Tests if requested
if ($RunTests) {
    Invoke-UnitTests
}

# 2. Pull Only Mode
if ($PullOnly) {
    Write-Status "Pulling latest updates with rebase..."
    if ($WhatIf) {
        Write-Notice "[WhatIf] Would execute: git pull --rebase --autostash origin main"
    } else {
        git pull --rebase --autostash origin main
        Write-Success "Pull complete."
    }
    exit 0
}

# 3. Push Only Mode
if ($PushOnly) {
    Write-Status "Pushing existing commits to origin main..."
    if ($WhatIf) {
        Write-Notice "[WhatIf] Would execute: git push origin main"
    } else {
        git push origin main
        Write-Success "Push complete."
    }
    exit 0
}

# 4. Check git status
$statusOutput = git status --porcelain
$hasChanges = [bool]($statusOutput)

if (-not $hasChanges) {
    $unpushed = git log '@{u}..HEAD' --oneline 2>$null
    if ($unpushed) {
        Write-Notice "Working directory clean, but unpushed commits exist:"
        $unpushed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
        if (-not $NoPush) {
            Write-Status "Pushing unpushed commits to origin main..."
            if ($WhatIf) {
                Write-Notice "[WhatIf] Would execute: git push origin main"
            } else {
                git push origin main
                Write-Success "Push complete."
            }
        }
    } else {
        Write-Success "Working directory clean and up to date with origin/main. Nothing to commit."
    }
    exit 0
}

# 5. Review Changes
Write-Status "Detected modified / untracked files:"
git status -s | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }

if ($WhatIf) {
    $previewMsg = if ($Message) { $Message } else { Get-AutoCommitMessage }
    Write-Notice "[WhatIf] Commit message: $previewMsg"
    Write-Notice "[WhatIf] Dry-run complete. No changes made."
    exit 0
}

# 6. Fetch remote updates
Write-Status "Fetching remote updates..."
git fetch origin main *> $null

# 7. Stage files
Write-Status "Staging changes..."
git add -A

# 8. Secret Scanner Guard
$secretHits = Find-StagedSecrets
if (@($secretHits).Count -gt 0) {
    Write-Failure "CRITICAL: Secret scanner blocked commit! Sensitive credential patterns detected in staged files:"
    foreach ($hit in $secretHits) {
        Write-Host "  Pattern : $($hit.Pattern)" -ForegroundColor Red
        Write-Host "  Snippet : $($hit.Snippet)..." -ForegroundColor Yellow
    }
    Write-Notice "Unstaging changes to protect repository..."
    git reset
    exit 1
}

# 9. Format Commit Message
$commitMsg = if ($Message) { $Message } else { Get-AutoCommitMessage }
if (-not $commitMsg) {
    $commitMsg = "chore(solver): update ecosystem components"
}

Write-Status "Committing changes with message: '$commitMsg'..."
git commit -m "$commitMsg"
if ($LASTEXITCODE -ne 0) {
    Write-Failure "Commit failed."
    exit $LASTEXITCODE
}
Write-Success "Commit created."

# 10. Push
if ($NoPush) {
    Write-Notice "NoPush specified. Changes committed locally."
} else {
    Write-Status "Pushing with rebase to origin main..."
    git pull --rebase --autostash origin main
    git push origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Failure "Push failed."
        exit $LASTEXITCODE
    }
    Write-Success "Successfully synchronized and pushed to https://github.com/AaradhyaDT/crypto_arithmetic_solver"
}
