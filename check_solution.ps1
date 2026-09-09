Param(
    [Parameter(Position=0)]
    [string]$Word1,
    [Parameter(Position=1)]
    [string]$Word2,
    [Parameter(Position=2)]
    [string]$Result,
    [Parameter(Position=3)]
    [string]$Answer
)

# Prompt if any are missing (identical input method as solve_with_metrics.ps1)
if (-not $Word1) { $Word1 = Read-Host "Enter first addend (word1)" }
if (-not $Word2) { $Word2 = Read-Host "Enter second addend (word2)" }
if (-not $Result) { $Result = Read-Host "Enter result word" }
if (-not $Answer) { $Answer = Read-Host "Enter answer (e.g. 7483 7455 14938 or A=4,B=7... or JSON file)" }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = "python"
$cli = Join-Path $scriptDir 'cli.py'

if (-not (Get-Command $python -ErrorAction SilentlyContinue)) {
    Write-Host "Python executable '$python' not found on PATH." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $cli)) {
    Write-Host "cli.py not found at $cli" -ForegroundColor Red
    exit 1
}

$argList = @($cli, 'check', $Word1, $Word2, $Result, $Answer)

Write-Host ("Checking solution for: {0} + {1} = {2}" -f $Word1, $Word2, $Result) -ForegroundColor Cyan

$proc = Start-Process -FilePath $python -ArgumentList $argList -WorkingDirectory $scriptDir -NoNewWindow -Wait -PassThru
exit $proc.ExitCode
