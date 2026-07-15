Param(
    [string]$Word1,
    [string]$Word2,
    [string]$Result,
    [switch]$All,
    [int]$Timeout = 2
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
$cmd = @($python, $cli, 'solve', $Word1, $Word2, $Result, '--metrics-json', $jsonPath, '--timeout', $Timeout.ToString())
if ($All) { $cmd += '--all' }

Write-Host ("Running solver for: {0} + {1} = {2} (timeout={3}s)" -f $Word1, $Word2, $Result, $Timeout) -ForegroundColor Cyan

# Execute
$proc = Start-Process -FilePath $python -ArgumentList @($cli, 'solve', $Word1, $Word2, $Result, '--metrics-json', $jsonPath, '--timeout', $Timeout.ToString()) -NoNewWindow -Wait -PassThru
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

Write-Host "\n=== Solution Summary ===" -ForegroundColor Green
if ($null -eq $sols) {
    Write-Host "No solution found."
}
else {
    if ($sols -is [System.Collections.IEnumerable] -and $sols -isnot [string]) {
        # list of solutions
        $count = $sols.Count
        Write-Host "Solutions found: $count" -ForegroundColor Yellow
        $first = $sols[0]
    }
    else {
        $first = $sols
        Write-Host "Solutions found: 1" -ForegroundColor Yellow
    }

    # Print numeric values if possible (safe lookups)
    $map = @{}
    foreach ($p in $first.PSObject.Properties) { $map[$($p.Name)] = $p.Value }
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

Write-Host "\n=== Metrics ===" -ForegroundColor Green
foreach ($k in $metrics.PSObject.Properties.Name) {
    $val = $metrics.$k
    Write-Host ("  {0}`t{1}" -f $k, $val)
}

# Clean up the temp JSON
# Remove-Item $jsonPath -ErrorAction SilentlyContinue

Write-Host "\nReport written to: $jsonPath" -ForegroundColor DarkGreen
