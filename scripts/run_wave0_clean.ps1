[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)]
    [ValidateSet('primary', 'clean-a', 'clean-b')]
    [string]$AttemptId,
    [Parameter(Mandatory = $true)][string]$ImageTag,
    [Parameter(Mandatory = $true)][string]$ImageDigest,
    [Parameter(Mandatory = $true)][string]$HostArtifactRoot
)

$ErrorActionPreference = 'Stop'
$BaseDigest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
# Offline stage contract: docker run --network none.

if (Test-Path Env:VAL_DATA_ROOT) {
    throw 'VAL_DATA_ROOT must remain unset'
}
if ([string]::IsNullOrWhiteSpace($RunId)) {
    throw 'RunId must be non-empty'
}

$CampaignRoot = (Resolve-Path -LiteralPath $HostArtifactRoot).Path
$AttemptRoot = Join-Path $CampaignRoot $AttemptId
New-Item -ItemType Directory -Path $AttemptRoot -ErrorAction Stop | Out-Null
$WaveRoot = New-Item -ItemType Directory -Path (Join-Path $AttemptRoot 'wave0') -ErrorAction Stop
$ReceiptsRoot = New-Item -ItemType Directory -Path (Join-Path $WaveRoot.FullName 'receipts') -ErrorAction Stop
$CheckpointsRoot = New-Item -ItemType Directory -Path (Join-Path $WaveRoot.FullName 'checkpoints') -ErrorAction Stop
$ModelCacheRoot = New-Item -ItemType Directory -Path (Join-Path $WaveRoot.FullName 'model_cache') -ErrorAction Stop
$UvCacheRoot = New-Item -ItemType Directory -Path (Join-Path $WaveRoot.FullName 'uv_cache') -ErrorAction Stop
$AuditRoot = New-Item -ItemType Directory -Path (Join-Path $AttemptRoot 'audit') -ErrorAction Stop
$Worktree = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

function Write-NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $stream = [System.IO.FileStream]::new(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $writer = [System.IO.StreamWriter]::new($stream, $encoding)
        try { $writer.Write($Text) } finally { $writer.Dispose() }
    } finally {
        if ($stream.CanWrite) { $stream.Dispose() }
    }
}

function Get-TreeBytes {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [long]((Get-ChildItem -LiteralPath $Path -File -Recurse | Measure-Object -Property Length -Sum).Sum)
}

function Invoke-WaveStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Network,
        [Parameter(Mandatory = $true)][string[]]$Command,
        [Parameter(Mandatory = $true)][string]$Receipt
    )
    $LogPath = Join-Path $AuditRoot.FullName "$Name.log"
    $RecordPath = Join-Path $AuditRoot.FullName "$Name.json"
    if ((Test-Path -LiteralPath $LogPath) -or (Test-Path -LiteralPath $RecordPath)) {
        throw "audit destination already exists for $Name"
    }
    $DockerArgs = @(
        'run', '--rm', '--gpus', 'all', '--network', $Network,
        '--workdir', '/workspace', '--entrypoint', 'val',
        '-e', 'VAL_ARTIFACT_ROOT=/artifacts',
        '-e', "VAL_OBSERVED_BASE_IMAGE_DIGEST=$BaseDigest",
        '-e', "VAL_RUNTIME_IMAGE_DIGEST=$ImageDigest",
        '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'UV_CACHE_DIR=/artifacts/wave0/uv_cache',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8',
        '-v', "${Worktree}:/workspace:ro",
        '-v', "${AttemptRoot}:/artifacts:rw"
    )
    if ($Network -eq 'none') {
        $DockerArgs += @('-e', 'HF_HUB_OFFLINE=1', '-e', 'TRANSFORMERS_OFFLINE=1')
    }
    $DockerArgs += @($ImageTag)
    $DockerArgs += $Command
    $Started = [DateTimeOffset]::UtcNow
    $Output = (& docker @DockerArgs 2>&1 | Out-String)
    $ExitCode = $LASTEXITCODE
    $Finished = [DateTimeOffset]::UtcNow
    Write-NewText -Path $LogPath -Text $Output
    $ReceiptPath = Join-Path $ReceiptsRoot.FullName $Receipt
    $ReceiptHash = if (Test-Path -LiteralPath $ReceiptPath -PathType Leaf) {
        (Get-FileHash -Algorithm SHA256 -LiteralPath $ReceiptPath).Hash.ToLowerInvariant()
    } else { $null }
    $CheckpointFiles = @(Get-ChildItem -LiteralPath $CheckpointsRoot.FullName -File -Recurse)
    $CheckpointHashes = @($CheckpointFiles | ForEach-Object {
        [ordered]@{
            path = $_.FullName.Substring($AttemptRoot.Length + 1).Replace('\', '/')
            size = $_.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
        }
    })
    $Record = [ordered]@{
        schema_version = 1
        run_id = $RunId
        attempt_id = $AttemptId
        stage = $Name
        argv = @('docker') + $DockerArgs
        exit_code = $ExitCode
        started_at = $Started.ToString('o')
        finished_at = $Finished.ToString('o')
        runtime_seconds = ($Finished - $Started).TotalSeconds
        image_tag = $ImageTag
        image_digest = $ImageDigest
        network = $Network
        val_data_root_unset = -not (Test-Path Env:VAL_DATA_ROOT)
        receipt = $Receipt
        receipt_sha256 = $ReceiptHash
        checkpoint_files = $CheckpointHashes
        attempt_disk_bytes = Get-TreeBytes -Path $AttemptRoot
    }
    Write-NewText -Path $RecordPath -Text (($Record | ConvertTo-Json -Depth 8 -Compress) + "`n")
    if ($ExitCode -ne 0) {
        throw "Wave 0 stage $Name failed with exit code $ExitCode"
    }
    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
        throw "Wave 0 stage $Name did not publish $Receipt"
    }
}

$InspectPath = Join-Path $AuditRoot.FullName 'image-inspect.json'
$Inspect = (& docker image inspect $ImageTag 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) { throw 'image inspect failed' }
Write-NewText -Path $InspectPath -Text $Inspect

Invoke-WaveStage -Name '01-environment' -Network 'none' -Receipt 'environment.json' -Command @(
    'environment', 'check', '--config', '/workspace/configs/environment/wave0.yaml',
    '--run-id', $RunId, '--output', '/artifacts/wave0/receipts/environment.json'
)
Invoke-WaveStage -Name '02-model-assets' -Network 'bridge' -Receipt 'model-assets.json' -Command @(
    'assets', 'verify', '--config', '/workspace/configs/models/pinned-models.yaml',
    '--cache-root', '/artifacts/wave0/model_cache', '--output',
    '/artifacts/wave0/receipts/model-assets.json', '--run-id', $RunId, '--download'
)
Invoke-WaveStage -Name '03-model-contract' -Network 'none' -Receipt 'model-contract.json' -Command @(
    'probe', 'model-contract', '--assets', '/artifacts/wave0/receipts/model-assets.json',
    '--environment', '/artifacts/wave0/receipts/environment.json', '--fixtures',
    '/workspace/fixtures/synthetic/wave0/fixture-manifest.json', '--run-id', $RunId,
    '--output', '/artifacts/wave0/receipts/model-contract.json'
)
Invoke-WaveStage -Name '04-feasibility-a' -Network 'none' -Receipt 'feasibility-a.json' -Command @(
    'probe', 'training-feasibility', '--model-contract',
    '/artifacts/wave0/receipts/model-contract.json', '--checkpoint-root',
    '/artifacts/wave0/checkpoints/feasibility-a', '--run-id', $RunId,
    '--output', '/artifacts/wave0/receipts/feasibility-a.json'
)
Invoke-WaveStage -Name '05-feasibility-b' -Network 'none' -Receipt 'feasibility-b.json' -Command @(
    'probe', 'training-feasibility', '--model-contract',
    '/artifacts/wave0/receipts/model-contract.json', '--checkpoint-root',
    '/artifacts/wave0/checkpoints/feasibility-b', '--run-id', $RunId,
    '--output', '/artifacts/wave0/receipts/feasibility-b.json'
)

Write-Output 'WAVE0_A2_ATTEMPT_PASS / WAVE1_NOT_STARTED'
