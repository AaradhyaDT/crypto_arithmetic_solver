Param(
    [string]$Word1,
    [string]$Word2,
    [string]$Result,
    [switch]$All,
    [double]$Timeout = 2
)

# Prompt if any are missing
if (-not $Word1) { $Word1 = Read-Host "Enter first addend (word1)" }
if (-not $Word2) { $Word2 = Read-Host "Enter second addend (word2)" }
if (-not $Result) { $Result = Read-Host "Enter result word" }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$reportsDir = Join-Path $scriptDir 'reports'
if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }

$guid = [System.Guid]::NewGuid().ToString()
$jsonPath = Join-Path $reportsDir "solution_$guid.json"

# Build command
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

$argList = @($cli, 'solve', $Word1, $Word2, $Result, '--metrics-json', $jsonPath, '--timeout', $Timeout.ToString())
if ($All) { $argList += '--all' }

Write-Host ("Running solver for: {0} + {1} = {2} (timeout={3}s)" -f $Word1, $Word2, $Result, $Timeout) -ForegroundColor Cyan

# Execute (run from $scriptDir so relative paths inside cli.py/src resolve regardless of caller's CWD)
$proc = Start-Process -FilePath $python -ArgumentList $argList -WorkingDirectory $scriptDir -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    Write-Host "Solver process exited with code $($proc.ExitCode)" -ForegroundColor Red
    exit $proc.ExitCode
}

if (-not (Test-Path $jsonPath)) {
    Write-Host "No output JSON found at $jsonPath" -ForegroundColor Red
    exit 1
}

# Read and display
try {
    $data = Get-Content $jsonPath -Raw | ConvertFrom-Json
}
catch {
    Write-Host "Failed to read JSON: $_" -ForegroundColor Red
    exit 1
}

$sols = $data.solutions
$metrics = $data.metrics

Write-Host "`n=== Solution Summary ===" -ForegroundColor Green
if ($null -eq $sols) {
    Write-Host "No solution found."
}
else {
    $fastestIdx = 0
    if ($null -ne $metrics.fastest_solution_index) { $fastestIdx = $metrics.fastest_solution_index }

    if ($sols -is [System.Collections.IEnumerable] -and $sols -isnot [string]) {
        # list of solutions
        $count = $sols.Count
        Write-Host "Solutions found: $count" -ForegroundColor Yellow
        $first = $sols[$fastestIdx]
        if ($fastestIdx -ne 0) {
            Write-Host "Showing fastest-found solution (index $fastestIdx of $count)" -ForegroundColor DarkYellow
        }
    }
    else {
        $first = $sols
        Write-Host "Solutions found: 1" -ForegroundColor Yellow
    }

    # Print numeric values if possible (safe lookups)
    $map = @{}
    foreach ($p in $first.PSObject.Properties) { $map[[string]$p.Name] = $p.Value }
    $builtOk = $true
    try {
        $n1 = ""
        foreach ($ch in $Word1.ToCharArray()) {
            $key = [string]$ch
            if ($map.ContainsKey($key)) { $n1 += [string]$map[$key] } else { $builtOk = $false; break }
        }
        if ($builtOk) {
            $n2 = ""
            foreach ($ch in $Word2.ToCharArray()) {
                $key = [string]$ch
                if ($map.ContainsKey($key)) { $n2 += [string]$map[$key] } else { $builtOk = $false; break }
            }
        }
        if ($builtOk) {
            $nr = ""
            foreach ($ch in $Result.ToCharArray()) {
                $key = [string]$ch
                if ($map.ContainsKey($key)) { $nr += [string]$map[$key] } else { $builtOk = $false; break }
            }
        }
        if ($builtOk -and $n1 -ne "" -and $n2 -ne "" -and $nr -ne "") {
            Write-Host "$n1 + $n2 = $nr" -ForegroundColor Magenta
        }
    }
    catch {
        # fallback: print mapping if numeric construction fails
    }

    Write-Host "Mapping:"
    foreach ($k in ($first.PSObject.Properties.Name | Sort-Object)) {
        $v = $first.$k
        Write-Host ("  {0} -> {1}" -f $k, $v)
    }
}

if ($null -ne $metrics.leading_bound) {
    Write-Host "`n=== Deduced Bound (before search) ===" -ForegroundColor Green
    Write-Host ("  Column {0}: {1}" -f $metrics.leading_bound.column, $metrics.leading_bound.note)
}

if ($null -ne $metrics.reasoning_steps) {
    Write-Host "`n=== Reasoning (why each digit) ===" -ForegroundColor Green
    foreach ($step in $metrics.reasoning_steps) {
        if ($step.reason -eq 'forced') {
            Write-Host ("  Column {0} [{1}]: {2} = {3} -- {4}" -f $step.column, $step.role, $step.char, $step.chosen, $step.note)
        }
        else {
            Write-Host ("  Column {0} [{1}]: {2} = {3}" -f $step.column, $step.role, $step.char, $step.chosen)
            if ($step.eliminated -and $step.eliminated.Count -gt 0) {
                foreach ($e in $step.eliminated) {
                    Write-Host ("      ruled out {0}: {1}" -f $e.digit, $e.reason)
                }
            }
        }
    }
}

if ($null -ne $metrics.solution_steps) {
    Write-Host "`n=== Solving Steps ===" -ForegroundColor Green
    foreach ($step in $metrics.solution_steps) {
        Write-Host ("  Column {0}: {1}" -f $step.column, $step.equation)
    }
}

Write-Host "`n=== Metrics ===" -ForegroundColor Green
$skipKeys = @('solution_steps', 'reasoning_steps', 'leading_bound', 'fastest_solution_index')
foreach ($k in $metrics.PSObject.Properties.Name) {
    if ($skipKeys -contains $k) { continue }
    $val = $metrics.$k
    Write-Host ("  {0}`t{1}" -f $k, $val)
}

# Clean up the temp JSON
# Remove-Item $jsonPath -ErrorAction SilentlyContinue

Write-Host "`nReport written to: $jsonPath" -ForegroundColor DarkGreen