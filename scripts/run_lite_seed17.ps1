<#
.SYNOPSIS
Run the v0.2-lite Czech experiment for seed 17 on this machine, end to end.

.DESCRIPTION
One command, no manual steps:
  1. preflight: every input path and the val entry point must exist;
  2. GPU check: wait (-WaitForGpu) or stop unless the RTX 4090 is free;
  3. shared 2% baseline fit and evaluation (`val lite baseline`);
  4. protocol Section 8 gate: loss decreased and exactly nine allowlisted
     grid_sampler_2d_backward_cuda warnings;
  5. with -Reference: the full-label reference fit (`val lite reference`)
     and the same gate on it (v0.2.1 Section 2);
  6. the full experiment (`val lite run`) unless -SkipFullRun.
-ReferenceOnly runs step 5 alone (no baseline, no full experiment): the way to
add a reference fit to a rule whose experiments already exist.
-Rule selects the training-length rule (v0.2.1 Section 1): fixed-steps is the
v0.2-lite protocol; fixed-epochs derives each fit's steps from its image
count. Experiment ids carry the rule so the two never share a directory.
Nothing is retried and nothing is overwritten. A lock file prevents two copies.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File scripts\run_lite_seed17.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File scripts\run_lite_seed17.ps1 -WaitForGpu
powershell -ExecutionPolicy Bypass -File scripts\run_lite_seed17.ps1 -WaitForGpu -Rule fixed-epochs -Reference
#>
[CmdletBinding()]
param(
    [string]$Device = 'cuda',
    [ValidateSet('fixed-steps', 'fixed-epochs')][string]$Rule = 'fixed-steps',
    [int]$Steps = 1000,
    [int]$BatchSize = 8,
    [int]$WarmupSteps = 50,
    [int]$Seed = 17,
    [switch]$WaitForGpu,
    [switch]$Reference,
    [switch]$ReferenceOnly,
    [switch]$SkipFullRun,
    [switch]$DryRun,
    [string]$Arms = 'random,entropy,margin',
    [string]$Embeddings = '',
    [string]$Manifest = '',
    [string]$PublicView = '',
    [string]$Images = '',
    [string]$Snapshot = '',
    [string]$OutputRoot = '',
    [string]$LocalPaths = ''
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$Worktree = Split-Path -Parent $PSScriptRoot
$Val = Join-Path $Worktree '.venv\Scripts\val.exe'
$Python = Join-Path $Worktree '.venv\Scripts\python.exe'

# Machine-specific inputs live outside git in scripts/local-paths.ps1 (copy local-paths.example.ps1).
# Explicit parameters win; the file only fills parameters that were left empty.
if (-not $LocalPaths) { $LocalPaths = Join-Path $PSScriptRoot 'local-paths.ps1' }
$LocalDefaults = @{}
if (Test-Path -LiteralPath $LocalPaths) {
    . $LocalPaths
    if (-not ($LocalDefaults -is [hashtable])) {
        Write-Host ('local-paths file must define $LocalDefaults = @{ ... }: ' + $LocalPaths)
        exit 3
    }
}
foreach ($name in @('Manifest', 'PublicView', 'Images', 'Snapshot', 'OutputRoot', 'Embeddings')) {
    if (-not (Get-Variable -Name $name -ValueOnly) -and $LocalDefaults.ContainsKey($name)) {
        Set-Variable -Name $name -Value ([string]$LocalDefaults[$name])
    }
}
$unset = @(@('Manifest', 'PublicView', 'Images', 'Snapshot', 'OutputRoot') | Where-Object { -not (Get-Variable -Name $_ -ValueOnly) })
if ($unset.Count -gt 0) {
    Write-Host ('MISSING local paths       -' + ($unset -join ', -') + ': pass the parameter(s) or set them in ' + $LocalPaths + ' (see scripts/local-paths.example.ps1)')
    exit 3
}
$GpuFreeMiB = 4000
$GpuFreeUtil = 5
$WaitSeconds = 30
$WaitLimitSeconds = 4 * 3600
# Experiment ids: v0.2-lite ids stay `lite-czech-s<seed>-…`; the epoch rule gets its own tag.
$RuleTag = if ($Rule -eq 'fixed-epochs') { 'ep18-' } else { '' }
if ($ReferenceOnly) { $Reference = $true; $SkipFullRun = $true }
$RuntimeArguments = @('--rule', $Rule, '--steps', "$Steps", '--batch-size', "$BatchSize", '--warmup-steps', "$WarmupSteps")
# v0.3: the diversity arms need the pool embeddings; their experiments get a `div` tag.
$ArmList = @(($Arms -split ',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$NeedsEmbeddings = ($ArmList -contains 'coreset') -or ($ArmList -contains 'hybrid')
$ArmsTag = if ($NeedsEmbeddings) { 'div-' } else { '' }
$RunArguments = @('--arms', ($ArmList -join ','))
if ($Embeddings) { $RunArguments += @('--embeddings', $Embeddings) }

function Write-Step([string]$Message) {
    Write-Host ("[{0}] {1}" -f (Get-Date).ToUniversalTime().ToString('HH:mm:ssZ'), $Message)
}

function Invoke-Val {
    # Run val.exe with stdout and stderr captured into files, then echo both so the
    # transcript keeps every diagnostic (native stderr is otherwise lost in 5.1).
    param([string[]]$Arguments)
    $quoted = $Arguments | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    $process = Start-Process -FilePath $Val -ArgumentList $quoted -NoNewWindow -Wait -PassThru -RedirectStandardOutput $outFile -RedirectStandardError $errFile
    foreach ($line in (Get-Content -LiteralPath $outFile)) { Write-Host $line }
    foreach ($line in (Get-Content -LiteralPath $errFile)) { if ($line -notmatch 'Loading weights') { Write-Host $line } }
    Remove-Item -LiteralPath $outFile, $errFile -Force -ErrorAction SilentlyContinue
    return $process.ExitCode
}

function Get-GpuSample {
    $raw = & nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return $null }
    $parts = ("$raw" -split ',') | ForEach-Object { $_.Trim() }
    return @{ UsedMiB = [int]$parts[0]; Util = [int]$parts[1] }
}

# ---------------------------------------------------------------- preflight
$checks = @(
    @{ Name = 'val entry point'; Path = $Val },
    @{ Name = 'venv python'; Path = $Python },
    @{ Name = 'manifest'; Path = $Manifest },
    @{ Name = 'public pool view'; Path = $PublicView },
    @{ Name = 'images directory'; Path = $Images },
    @{ Name = 'model snapshot'; Path = $Snapshot }
)
$missing = 0
foreach ($check in $checks) {
    $exists = Test-Path -LiteralPath $check.Path
    if (-not $exists) { $missing += 1 }
    Write-Host ("{0,-6} {1,-18} {2}" -f $(if ($exists) { 'ok' } else { 'MISSING' }), $check.Name, $check.Path)
}
if ($NeedsEmbeddings) {
    if (-not $Embeddings) {
        Write-Host 'MISSING embeddings         coreset/hybrid need -Embeddings <embeddings-dinov2-small.npz>'
        $missing += 1
    } elseif (-not (Test-Path -LiteralPath $Embeddings)) {
        Write-Host ("MISSING embeddings         {0}" -f $Embeddings)
        $missing += 1
    } else {
        Write-Host ("{0,-6} {1,-18} {2}" -f 'ok', 'embeddings', $Embeddings)
    }
}
if ($missing -gt 0) {
    Write-Host "preflight failed: $missing input(s) missing"
    exit 3
}
if (-not (Test-Path -LiteralPath $OutputRoot)) {
    New-Item -ItemType Directory -Path $OutputRoot | Out-Null
}
Write-Host ("{0,-6} {1,-18} {2}" -f 'ok', 'output root', $OutputRoot)
$sample = Get-GpuSample
if ($null -eq $sample) {
    Write-Host 'gpu    nvidia-smi unavailable'
} else {
    Write-Host ("gpu    used={0} MiB util={1}%  (free means <{2} MiB and <{3}%)" -f $sample.UsedMiB, $sample.Util, $GpuFreeMiB, $GpuFreeUtil)
}
Write-Host ("{0,-6} {1,-18} rule={2} seed={3} reference={4} referenceonly={5} fullrun={6} arms={7} embeddings={8}" -f 'ok', 'plan', $Rule, $Seed, [bool]$Reference, [bool]$ReferenceOnly, (-not $SkipFullRun), ($ArmList -join ','), $(if ($Embeddings) { $Embeddings } else { 'none' }))
if ($DryRun) {
    Write-Host 'preflight ok (dry run; nothing launched)'
    exit 0
}

# ---------------------------------------------------------------- lock
$lockPath = Join-Path $OutputRoot 'RUNNING.lock'
try {
    $lock = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
} catch {
    Write-Host "another run holds $lockPath ; if you are sure nothing is running, delete that file and retry"
    exit 3
}

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmZ')
$transcript = Join-Path $OutputRoot ("run-lite-{0}{1}seed{2}-{3}.log" -f $RuleTag, $ArmsTag, $Seed, $stamp)
Start-Transcript -Path $transcript -Append | Out-Null
try {
    # ------------------------------------------------------------ GPU
    if ($Device -eq 'cuda') {
        $waited = 0
        $streak = 0
        while ($true) {
            $sample = Get-GpuSample
            if ($null -eq $sample) { Write-Step 'nvidia-smi unavailable; cannot verify the GPU'; exit 3 }
            $free = ($sample.UsedMiB -lt $GpuFreeMiB) -and ($sample.Util -lt $GpuFreeUtil)
            if ($free) { $streak += 1 } else { $streak = 0 }
            if ($streak -ge 2) { break }
            if (-not $WaitForGpu) {
                Write-Step ("GPU busy: used={0} MiB util={1}%. Close the other GPU job (check: wsl -l -v) or rerun with -WaitForGpu" -f $sample.UsedMiB, $sample.Util)
                exit 4
            }
            if ($waited -ge $WaitLimitSeconds) { Write-Step 'GPU did not become free within 4 h; nothing launched'; exit 4 }
            Write-Step ("waiting for GPU: used={0} MiB util={1}%" -f $sample.UsedMiB, $sample.Util)
            Start-Sleep -Seconds $WaitSeconds
            $waited += $WaitSeconds
        }
        Write-Step 'GPU free on two consecutive samples'
    }

    # ------------------------------------------------------------ environment
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:CUBLAS_WORKSPACE_CONFIG = ':4096:8'
    $env:HF_HUB_OFFLINE = '1'
    $env:TRANSFORMERS_OFFLINE = '1'
    Set-Location $Worktree

    # ------------------------------------------------------------ baseline
    if (-not $ReferenceOnly) {
        $baselineId = "lite-czech-$($RuleTag)s$Seed-baseline-$stamp"
        Write-Step "baseline $baselineId starting (rule=$Rule steps=$Steps batch=$BatchSize warmup=$WarmupSteps device=$Device)"
        $started = Get-Date
        $code = Invoke-Val (@('lite', 'baseline', '--manifest', $Manifest, '--public-view', $PublicView, '--images', $Images, '--snapshot', $Snapshot, '--experiment-id', $baselineId, '--seed', "$Seed", '--device', $Device, '--output-root', $OutputRoot) + $RuntimeArguments)
        Write-Step ("baseline exit={0} elapsed={1:N0}s" -f $code, ((Get-Date) - $started).TotalSeconds)
        if ($code -ne 0) { Write-Step "baseline failed; see $transcript"; exit 2 }

        # -------------------------------------------------------- Section 8 gate
        # Plain arguments only: PowerShell 5.1 mangles quoted code passed to python -c.
        $gateCode = Invoke-Val @('lite', 'gate', '--experiment-dir', (Join-Path $OutputRoot $baselineId), '--device', $Device)
        Write-Step "section-8 gate exit=$gateCode (PASS/FAIL line above)"
        if ($gateCode -ne 0) { Write-Step 'gate failed; full experiment not started'; exit 2 }
    }

    # ------------------------------------------------------------ reference (v0.2.1)
    if ($Reference) {
        $referenceId = "lite-czech-ref-$Rule-s$Seed-$stamp"
        Write-Step "reference $referenceId starting (whole pool, rule=$Rule)"
        $started = Get-Date
        $code = Invoke-Val (@('lite', 'reference', '--manifest', $Manifest, '--public-view', $PublicView, '--images', $Images, '--snapshot', $Snapshot, '--experiment-id', $referenceId, '--seed', "$Seed", '--device', $Device, '--output-root', $OutputRoot) + $RuntimeArguments)
        Write-Step ("reference exit={0} elapsed={1:N0}s" -f $code, ((Get-Date) - $started).TotalSeconds)
        if ($code -ne 0) { Write-Step "reference failed; see $transcript"; exit 2 }
        $gateCode = Invoke-Val @('lite', 'gate', '--experiment-dir', (Join-Path $OutputRoot $referenceId), '--device', $Device, '--role', 'reference')
        Write-Step "reference gate exit=$gateCode (PASS/FAIL line above)"
        if ($gateCode -ne 0) { Write-Step 'reference gate failed; full experiment not started'; exit 2 }
    }
    if ($SkipFullRun) { Write-Step 'done; full experiment skipped (-SkipFullRun or -ReferenceOnly)'; exit 0 }

    # ------------------------------------------------------------ full experiment
    $fullId = "lite-czech-$($RuleTag)$($ArmsTag)s$Seed-$stamp"
    Write-Step "full experiment $fullId starting ($($ArmList.Count) arms: $($ArmList -join ','), rule=$Rule)"
    $started = Get-Date
    $code = Invoke-Val (@('lite', 'run', '--manifest', $Manifest, '--public-view', $PublicView, '--images', $Images, '--snapshot', $Snapshot, '--experiment-id', $fullId, '--seed', "$Seed", '--device', $Device, '--output-root', $OutputRoot) + $RuntimeArguments + $RunArguments)
    Write-Step ("full experiment exit={0} elapsed={1:N0}s" -f $code, ((Get-Date) - $started).TotalSeconds)
    if ($code -ne 0) { Write-Step "full experiment failed; see $transcript"; exit 2 }
    Write-Step ("done. results: {0}" -f (Join-Path $OutputRoot $fullId))
    Write-Step ("  metrics.csv, curve.svg, ledger-*.json, experiment-receipt.json; log: {0}" -f $transcript)
    exit 0
} finally {
    Stop-Transcript | Out-Null
    $lock.Close()
    Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
}
