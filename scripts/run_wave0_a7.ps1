[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string]$ImageTag,
    [Parameter(Mandatory = $true)][string]$ImageDigest,
    [Parameter(Mandatory = $true)][string]$HostCampaignRoot,
    [Parameter(Mandatory = $true)][string]$LeasePath
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$BaseDigest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
$TerminalInconclusive = 'WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'

function Write-NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [System.Text.UTF8Encoding]::new($false)
    $Stream = [System.IO.FileStream]::new(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $Writer = [System.IO.StreamWriter]::new($Stream, $Encoding)
        try { $Writer.Write($Text) } finally { $Writer.Dispose() }
    } finally {
        if ($Stream.CanWrite) { $Stream.Dispose() }
    }
}

function Invoke-NativeCommandCapture {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @()
    )
    $Application = Get-Command -Name $FilePath -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $PreviousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $Items = @(& $Application.Source @ArgumentList 2>&1)
        $ExitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousPreference
    }
    $Lines = @($Items | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $_.Exception.Message
        } else {
            $_.ToString()
        }
    })
    $Text = if ($Lines.Count -eq 0) {
        ''
    } else {
        ($Lines -join [Environment]::NewLine) + [Environment]::NewLine
    }
    return [pscustomobject]@{ Text = $Text; ExitCode = [int]$ExitCode }
}

function Get-RelativeFileRecord {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    return [ordered]@{
        path = $Item.FullName.Substring($Root.Length + 1).Replace('\', '/')
        size = [long]$Item.Length
        sha256 = (Get-FileHash -LiteralPath $Item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

function Release-A7Lease {
    param(
        [Parameter(Mandatory = $true)][string]$ActivePath,
        [Parameter(Mandatory = $true)][string]$ReleasedPath,
        [Parameter(Mandatory = $true)][string]$RecordPath
    )
    if (-not (Test-Path -LiteralPath $ActivePath -PathType Leaf)) {
        throw 'validated A7 lease disappeared before release'
    }
    $LeaseHash = (Get-FileHash -LiteralPath $ActivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    [System.IO.File]::Move($ActivePath, $ReleasedPath)
    $Release = [ordered]@{
        schema_version = 1
        run_id = $RunId
        source_commit = $SourceCommit
        image_digest = $ImageDigest
        released_at = [DateTimeOffset]::UtcNow.ToString('o')
        original_lease_sha256 = $LeaseHash
    }
    Write-NewText -Path $RecordPath -Text (($Release | ConvertTo-Json -Compress) + "`n")
}

function Test-Task7AuditBinding {
    $Bindings = [ordered]@{
        '20-image-build-result.json' = [string]$Lease.build_audit_sha256
        '22-a7-cpu-micro-check.json' = [string]$Lease.microcheck_audit_sha256
    }
    foreach ($Name in $Bindings.Keys) {
        $Path = Join-Path $AuditRoot $Name
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw "Task 7 audit is missing: $Name"
        }
        $Item = Get-Item -LiteralPath $Path -Force
        if (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Task 7 audit is linked: $Name"
        }
        $Observed = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Bindings[$Name] -notmatch '^[0-9a-f]{64}$' -or $Observed -ne $Bindings[$Name]) {
            throw "Task 7 audit identity mismatch: $Name"
        }
    }
}

function Test-HistoricalBaseline {
    param(
        [Parameter(Mandatory = $true)][string]$RootBaselinePath,
        [Parameter(Mandatory = $true)][string]$RootBaselineSha256,
        [Parameter(Mandatory = $true)][string]$AugmentedBaselinePath,
        [Parameter(Mandatory = $true)][string]$AugmentedBaselineSha256
    )
    foreach ($Path in @($RootBaselinePath, $AugmentedBaselinePath)) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw 'historical baseline is unavailable'
        }
        $Item = Get-Item -LiteralPath $Path -Force
        if (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'historical baseline must not be linked'
        }
    }
    $ObservedRootSha256 = (Get-FileHash -LiteralPath $RootBaselinePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($RootBaselineSha256 -notmatch '^[0-9a-f]{64}$' -or
        $ObservedRootSha256 -ne $RootBaselineSha256) {
        throw 'root historical baseline identity mismatch'
    }
    $ObservedAugmentedSha256 = (Get-FileHash -LiteralPath $AugmentedBaselinePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($AugmentedBaselineSha256 -notmatch '^[0-9a-f]{64}$' -or
        $ObservedAugmentedSha256 -ne $AugmentedBaselineSha256) {
        throw 'augmented historical baseline identity mismatch'
    }
    $RootBaseline = Get-Content -LiteralPath $RootBaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $Baseline = Get-Content -LiteralPath $AugmentedBaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ([string]$Baseline.parent_baseline_sha256 -ne $RootBaselineSha256 -or
        [string]$Baseline.artifact_root -ne [string]$RootBaseline.artifact_root) {
        throw 'augmented baseline root binding mismatch'
    }
    $AugmentedArtifacts = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($Record in $Baseline.artifact_files) {
        $AugmentedArtifacts.Add([string]$Record.path, $Record)
    }
    foreach ($RootRecord in $RootBaseline.artifact_files) {
        $Path = [string]$RootRecord.path
        if (-not $AugmentedArtifacts.ContainsKey($Path)) {
            throw "augmented baseline omits root artifact: $Path"
        }
        $Record = $AugmentedArtifacts[$Path]
        if ([long]$Record.size -ne [long]$RootRecord.size -or
            [string]$Record.sha256 -ne [string]$RootRecord.sha256) {
            throw "augmented baseline changes root artifact identity: $Path"
        }
    }
    $RootProtected = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($Record in $RootBaseline.protected_git) {
        $RootProtected.Add([string]$Record.path, $Record)
    }
    $AugmentedProtected = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($Record in $Baseline.protected_git) {
        $AugmentedProtected.Add([string]$Record.path, $Record)
    }
    if ($RootProtected.Count -ne $AugmentedProtected.Count) {
        throw 'augmented baseline changes protected Git inventory'
    }
    foreach ($Path in $RootProtected.Keys) {
        $RootRecord = $RootProtected[$Path]
        if (-not $AugmentedProtected.ContainsKey($Path)) {
            throw "augmented baseline omits protected Git file: $Path"
        }
        $Record = $AugmentedProtected[$Path]
        if ([long]$Record.size -ne [long]$RootRecord.size -or
            [string]$Record.sha256 -ne [string]$RootRecord.sha256) {
            throw "augmented baseline changes protected Git identity: $Path"
        }
    }
    $AugmentedImages = @{}
    foreach ($Record in $Baseline.images) {
        $AugmentedImages.Add([string]$Record.tag, [string]$Record.image_id)
    }
    foreach ($RootImage in $RootBaseline.images) {
        $Tag = [string]$RootImage.tag
        if (-not $AugmentedImages.ContainsKey($Tag) -or
            $AugmentedImages[$Tag] -ne [string]$RootImage.image_id) {
            throw "augmented baseline changes root image identity: $Tag"
        }
    }
    $ArtifactRoot = [string]$Baseline.artifact_root
    $ExpectedArtifactPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($Record in $Baseline.artifact_files) {
        [void]$ExpectedArtifactPaths.Add([string]$Record.path)
        $Path = Join-Path $ArtifactRoot ([string]$Record.path).Replace('/', '\')
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "historical artifact missing: $($Record.path)" }
        $Item = Get-Item -LiteralPath $Path -Force
        if ($Item.Length -ne [long]$Record.size) { throw "historical artifact size drift: $($Record.path)" }
        $Hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Hash -ne [string]$Record.sha256) { throw "historical artifact hash drift: $($Record.path)" }
    }
    $CampaignPrefix = $CampaignRoot.TrimEnd('\') + '\'
    $CurrentHistoricalPaths = @(Get-ChildItem -LiteralPath $ArtifactRoot -File -Recurse -Force | Where-Object {
        -not $_.FullName.StartsWith($CampaignPrefix, [System.StringComparison]::OrdinalIgnoreCase)
    } | ForEach-Object {
        $_.FullName.Substring($ArtifactRoot.Length).TrimStart('\').Replace('\', '/')
    })
    if ($CurrentHistoricalPaths.Count -ne $ExpectedArtifactPaths.Count -or
        @($CurrentHistoricalPaths | Where-Object { -not $ExpectedArtifactPaths.Contains($_) }).Count -ne 0) {
        throw 'historical artifact set drift'
    }
    foreach ($Record in $Baseline.protected_git) {
        $Path = Join-Path $ProjectRoot ([string]$Record.path).Replace('/', '\')
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "protected Git file missing: $($Record.path)" }
        $Item = Get-Item -LiteralPath $Path -Force
        $Hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Item.Length -ne [long]$Record.size -or $Hash -ne [string]$Record.sha256) {
            throw "protected Git file drift: $($Record.path)"
        }
    }
    $ExpectedImages = @{}
    foreach ($Record in $Baseline.images) { $ExpectedImages[[string]$Record.tag] = [string]$Record.image_id }
    $CurrentTags = @(docker image ls --filter 'reference=vision-active-learning-loop:wave0-*' --format '{{.Repository}}:{{.Tag}}')
    if ($LASTEXITCODE -ne 0) { throw 'historical image inventory failed' }
    $HistoricalTags = @($CurrentTags | Where-Object { $_ -ne $ImageTag } | Sort-Object -Unique)
    if ($HistoricalTags.Count -ne $ExpectedImages.Count) { throw 'historical image set drift' }
    foreach ($Tag in $HistoricalTags) {
        $ObservedId = (docker image inspect --format '{{.Id}}' -- $Tag).Trim()
        if ($LASTEXITCODE -ne 0 -or $ExpectedImages[$Tag] -ne $ObservedId) {
            throw "historical image identity drift: $Tag"
        }
    }
    return [ordered]@{
        schema_version = 1
        baseline_path = $AugmentedBaselinePath
        baseline_sha256 = $ObservedAugmentedSha256
        root_baseline_path = $RootBaselinePath
        root_baseline_sha256 = $ObservedRootSha256
        root_artifact_count = @($RootBaseline.artifact_files).Count
        artifact_count = $ExpectedArtifactPaths.Count
        image_count = $ExpectedImages.Count
        protected_git_count = @($Baseline.protected_git).Count
        exact_set_match = $true
        status = 'PRESERVED'
    }
}

function Invoke-A7Stage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Command,
        [Parameter(Mandatory = $true)][string]$ExpectedReceipt,
        [string[]]$ExpectedArtifacts = @()
    )
    $LogPath = Join-Path $AuditRoot "$Name.log"
    $RecordPath = Join-Path $AuditRoot "$Name.json"
    $DockerArguments = @(
        'run', '--rm', '--gpus', 'all', '--network', 'none',
        '--workdir', '/workspace', '--entrypoint', 'val',
        '-e', 'VAL_ARTIFACT_ROOT=/artifacts',
        '-e', "VAL_OBSERVED_BASE_IMAGE_DIGEST=$BaseDigest",
        '-e', "VAL_RUNTIME_IMAGE_DIGEST=$ImageDigest",
        '-e', "VAL_SOURCE_COMMIT=$SourceCommit",
        '-e', "VAL_IMAGE_ID=$ImageDigest",
        '-e', "VAL_BASE_IMAGE_DIGEST=$BaseDigest",
        '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'HF_HUB_OFFLINE=1',
        '-e', 'TRANSFORMERS_OFFLINE=1',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8',
        '-v', "${ProjectRoot}:/workspace:ro",
        '-v', "${CampaignRoot}:/artifacts:rw",
        '-v', "${HistoricalModelCache}:/artifacts/wave0/model_cache:ro",
        $ImageDigest
    ) + $Command
    $Started = [DateTimeOffset]::UtcNow
    $Result = Invoke-NativeCommandCapture -FilePath 'docker' -ArgumentList $DockerArguments
    $Finished = [DateTimeOffset]::UtcNow
    Write-NewText -Path $LogPath -Text $Result.Text
    $ReceiptPath = Join-Path $CampaignRoot $ExpectedReceipt
    $ExpectedArtifactPaths = @($ExpectedReceipt) + @($ExpectedArtifacts)
    $ArtifactRecords = @($ExpectedArtifactPaths | ForEach-Object {
        $ArtifactPath = Join-Path $CampaignRoot $_
        if (Test-Path -LiteralPath $ArtifactPath -PathType Leaf) {
            $ArtifactItem = Get-Item -LiteralPath $ArtifactPath -Force
            if (($ArtifactItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -eq 0) {
                Get-RelativeFileRecord -Root $CampaignRoot -Path $ArtifactPath
            }
        }
    })
    $Record = [ordered]@{
        schema_version = 1
        run_id = $RunId
        stage = $Name
        argv = @('docker') + $DockerArguments
        exit_code = $Result.ExitCode
        started_at = $Started.ToString('o')
        finished_at = $Finished.ToString('o')
        runtime_seconds = ($Finished - $Started).TotalSeconds
        source_commit = $SourceCommit
        image_tag = $ImageTag
        image_digest = $ImageDigest
        base_image_digest = $BaseDigest
        network = 'none'
        gpu_enabled = $true
        receipt = if (Test-Path -LiteralPath $ReceiptPath -PathType Leaf) {
            Get-RelativeFileRecord -Root $CampaignRoot -Path $ReceiptPath
        } else { $null }
        expected_artifacts = $ArtifactRecords
    }
    Write-NewText -Path $RecordPath -Text (($Record | ConvertTo-Json -Depth 20 -Compress) + "`n")
    if ($Result.ExitCode -ne 0) { throw "A7 stage $Name failed" }
    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
        throw "A7 stage $Name did not publish its receipt"
    }
    if ($ArtifactRecords.Count -ne $ExpectedArtifactPaths.Count) {
        throw "A7 stage $Name artifact count or file-type mismatch"
    }
    foreach ($RelativePath in $ExpectedArtifactPaths) {
        $ArtifactPath = Join-Path $CampaignRoot $RelativePath
        $Record = Get-RelativeFileRecord -Root $CampaignRoot -Path $ArtifactPath
        if ($null -eq ($ArtifactRecords | Where-Object {
            $_.path -eq $Record.path -and $_.size -eq $Record.size -and $_.sha256 -eq $Record.sha256
        } | Select-Object -First 1)) {
            throw "A7 stage $Name artifact identity changed after audit: $RelativePath"
        }
    }
}

if (Test-Path Env:VAL_DATA_ROOT) { throw 'VAL_DATA_ROOT must remain unset' }
if ([string]::IsNullOrWhiteSpace($RunId)) { throw 'RunId must be non-empty' }
$CampaignRoot = (Resolve-Path -LiteralPath $HostCampaignRoot -ErrorAction Stop).Path
$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$SourceCommit = (git -C $ProjectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $SourceCommit.Length -ne 40) { throw 'source identity unavailable' }
if (-not (Test-Path -LiteralPath $LeasePath -PathType Leaf)) { throw 'claimed GPU lease is required' }
$Lease = Get-Content -LiteralPath $LeasePath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($Lease.run_id -ne $RunId) { throw 'GPU lease run identity mismatch' }
$ReleasedLeasePath = "$LeasePath.released"
$ReleaseRecordPath = "$LeasePath.release.json"
if ((Test-Path -LiteralPath $ReleasedLeasePath) -or (Test-Path -LiteralPath $ReleaseRecordPath)) {
    throw 'fresh lease release destinations are required'
}
if ($Lease.source_commit -ne $SourceCommit -or
    $Lease.image_id -ne $ImageDigest -or
    $Lease.base_image_digest -ne $BaseDigest -or
    [string]::IsNullOrWhiteSpace([string]$Lease.gpu_uuid) -or
    [string]$Lease.build_audit_sha256 -notmatch '^[0-9a-f]{64}$' -or
    [string]$Lease.microcheck_audit_sha256 -notmatch '^[0-9a-f]{64}$' -or
    [string]::IsNullOrWhiteSpace([string]$Lease.historical_baseline_path) -or
    [string]$Lease.historical_baseline_sha256 -notmatch '^[0-9a-f]{64}$') {
    throw 'GPU lease source/image/GPU binding mismatch'
}
$LeaseCampaignRoot = [System.IO.Path]::GetFullPath([string]$Lease.campaign_root).TrimEnd('\')
if (-not [string]::Equals(
    $LeaseCampaignRoot,
    $CampaignRoot.TrimEnd('\'),
    [System.StringComparison]::OrdinalIgnoreCase
)) {
    throw 'GPU lease campaign-root binding mismatch'
}
$AuditRoot = Join-Path $CampaignRoot 'audit'
$HistoricalWaveRoot = Split-Path -Parent (Split-Path -Parent $CampaignRoot)
$HistoricalModelCache = Join-Path $HistoricalWaveRoot 'model_cache'
$Terminal = $TerminalInconclusive
$Failure = $null
$ExitCode = 2
try {
    $Context = (docker context show).Trim()
    if ($LASTEXITCODE -ne 0 -or $Context -ne 'desktop-linux') { throw 'desktop-linux context is required' }
    $InspectResult = Invoke-NativeCommandCapture -FilePath 'docker' -ArgumentList @('image', 'inspect', $ImageTag)
    if ($InspectResult.ExitCode -ne 0) { throw 'image inspect failed' }
    $Inspect = @($InspectResult.Text | ConvertFrom-Json)
    if ($Inspect.Count -ne 1 -or $Inspect[0].Id -ne $ImageDigest) { throw 'image identity mismatch' }
    $Labels = $Inspect[0].Config.Labels
    if ($Labels.'org.opencontainers.image.revision' -ne $SourceCommit -or
        $Labels.'org.opencontainers.image.base.digest' -ne $BaseDigest -or
        $Labels.'org.opencontainers.image.val.run_id' -ne $RunId) {
        throw 'image label identity mismatch'
    }
    if (-not (Test-Path -LiteralPath $AuditRoot -PathType Container)) { throw 'Task 7 audit root is required' }
    Test-Task7AuditBinding
    Write-NewText -Path (Join-Path $AuditRoot '20-task8-image-inspect.json') -Text $InspectResult.Text
    if (-not (Test-Path -LiteralPath $HistoricalModelCache -PathType Container)) {
        throw 'historical verified model cache is unavailable'
    }

    $WaveRoot = New-Item -ItemType Directory -Path (Join-Path $CampaignRoot 'wave0') -ErrorAction Stop
    $ReceiptsRoot = New-Item -ItemType Directory -Path (Join-Path $WaveRoot.FullName 'receipts') -ErrorAction Stop
    $A7Root = New-Item -ItemType Directory -Path (Join-Path $CampaignRoot 'a7') -ErrorAction Stop
    $ComponentsRoot = New-Item -ItemType Directory -Path (Join-Path $A7Root.FullName 'components') -ErrorAction Stop
    $AggregateRoot = New-Item -ItemType Directory -Path (Join-Path $A7Root.FullName 'aggregate') -ErrorAction Stop
    $ComponentIds = @(
        'control-0',
        'control-1',
        'instrumented-0',
        'instrumented-1',
        'instrumented-2',
        'instrumented-3',
        'instrumented-4',
        'isolated-vjp-0',
        'isolated-vjp-1',
        'isolated-vjp-2',
        'isolated-vjp-3',
        'isolated-vjp-4'
    )
    foreach ($ComponentId in $ComponentIds) {
        New-Item -ItemType Directory -Path (Join-Path $ComponentsRoot.FullName $ComponentId) -ErrorAction Stop | Out-Null
    }

    Invoke-A7Stage -Name '21-environment' -ExpectedReceipt 'wave0/receipts/environment.json' -Command @(
        'environment', 'check', '--config', '/workspace/configs/environment/wave0.yaml',
        '--run-id', $RunId, '--output', '/artifacts/wave0/receipts/environment.json'
    )
    $Environment = Get-Content -LiteralPath (Join-Path $ReceiptsRoot.FullName 'environment.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Environment.normative.observed.gpu_uuid -ne $Lease.gpu_uuid) {
        throw 'environment receipt GPU differs from the validated lease'
    }
    Invoke-A7Stage -Name '22-model-assets' -ExpectedReceipt 'wave0/receipts/model-assets.json' -Command @(
        'assets', 'verify', '--config', '/workspace/configs/models/pinned-models.yaml',
        '--cache-root', '/artifacts/wave0/model_cache', '--run-id', $RunId,
        '--output', '/artifacts/wave0/receipts/model-assets.json'
    )
    Invoke-A7Stage -Name '23-model-contract' -ExpectedReceipt 'wave0/receipts/model-contract.json' -Command @(
        'probe', 'model-contract', '--assets', '/artifacts/wave0/receipts/model-assets.json',
        '--environment', '/artifacts/wave0/receipts/environment.json', '--fixtures',
        '/workspace/fixtures/synthetic/wave0/fixture-manifest.json', '--run-id', $RunId,
        '--output', '/artifacts/wave0/receipts/model-contract.json'
    )
    foreach ($ComponentId in @('control-0', 'control-1')) {
        Invoke-A7Stage -Name "24-$ComponentId" -ExpectedReceipt "a7/components/$ComponentId/receipt.json" -ExpectedArtifacts @(
            "a7/components/$ComponentId/tensor-bundle.vala7"
        ) -Command @(
            'diagnose', 'grid-sample-attribution', 'control',
            '--environment', '/artifacts/wave0/receipts/environment.json',
            '--model-assets', '/artifacts/wave0/receipts/model-assets.json',
            '--model-contract', '/artifacts/wave0/receipts/model-contract.json',
            '--component-root', "/artifacts/a7/components/$ComponentId", '--component-id', $ComponentId,
            '--source-commit', $SourceCommit, '--run-id', $RunId,
            '--output', "/artifacts/a7/components/$ComponentId/receipt.json"
        )
    }
    foreach ($ComponentId in @('instrumented-0', 'instrumented-1', 'instrumented-2', 'instrumented-3', 'instrumented-4')) {
        $Command = @(
            'diagnose', 'grid-sample-attribution', 'instrumented',
            '--environment', '/artifacts/wave0/receipts/environment.json',
            '--model-assets', '/artifacts/wave0/receipts/model-assets.json',
            '--model-contract', '/artifacts/wave0/receipts/model-contract.json',
            '--component-root', "/artifacts/a7/components/$ComponentId", '--component-id', $ComponentId,
            '--source-commit', $SourceCommit, '--run-id', $RunId,
            '--output', "/artifacts/a7/components/$ComponentId/receipt.json"
        )
        if ($ComponentId -eq 'instrumented-0') {
            $Command += @('--vjp-snapshot-output', '/artifacts/a7/components/instrumented-0/vjp-snapshot.vala7')
        }
        $ExpectedArtifacts = @("a7/components/$ComponentId/tensor-bundle.vala7")
        if ($ComponentId -eq 'instrumented-0') {
            $ExpectedArtifacts += 'a7/components/instrumented-0/vjp-snapshot.vala7'
        }
        Invoke-A7Stage -Name "25-$ComponentId" -ExpectedReceipt "a7/components/$ComponentId/receipt.json" -ExpectedArtifacts $ExpectedArtifacts -Command $Command
    }
    foreach ($ComponentId in @('isolated-vjp-0', 'isolated-vjp-1', 'isolated-vjp-2', 'isolated-vjp-3', 'isolated-vjp-4')) {
        Invoke-A7Stage -Name "26-$ComponentId" -ExpectedReceipt "a7/components/$ComponentId/receipt.json" -ExpectedArtifacts @(
            "a7/components/$ComponentId/tensor-bundle.vala7"
        ) -Command @(
            'diagnose', 'grid-sample-attribution', 'isolated-vjp',
            '--environment', '/artifacts/wave0/receipts/environment.json',
            '--model-assets', '/artifacts/wave0/receipts/model-assets.json',
            '--model-contract', '/artifacts/wave0/receipts/model-contract.json',
            '--parent-instrumented-receipt', '/artifacts/a7/components/instrumented-0/receipt.json',
            '--vjp-snapshot', '/artifacts/a7/components/instrumented-0/vjp-snapshot.vala7',
            '--component-root', "/artifacts/a7/components/$ComponentId", '--component-id', $ComponentId,
            '--source-commit', $SourceCommit, '--run-id', $RunId,
            '--output', "/artifacts/a7/components/$ComponentId/receipt.json"
        )
    }
    Invoke-A7Stage -Name '27-aggregate' -ExpectedReceipt 'a7/aggregate/receipt.json' -Command @(
        'diagnose', 'grid-sample-attribution', 'aggregate',
        '--environment', '/artifacts/wave0/receipts/environment.json',
        '--model-assets', '/artifacts/wave0/receipts/model-assets.json',
        '--model-contract', '/artifacts/wave0/receipts/model-contract.json',
        '--components-root', '/artifacts/a7/components', '--source-commit', $SourceCommit,
        '--run-id', $RunId, '--output', '/artifacts/a7/aggregate/receipt.json'
    )
    $Aggregate = Get-Content -LiteralPath (Join-Path $AggregateRoot.FullName 'receipt.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $Terminal = [string]$Aggregate.normative.terminal
    $ExitCode = 0
} catch {
    $Failure = $_.Exception.Message
} finally {
    try {
        try {
            $Historical = Test-HistoricalBaseline `
                -RootBaselinePath (Join-Path $env:TEMP 'val-a7-baseline-11a6b1929b0b4d44acc0a090887b50dd670357ea.json') `
                -RootBaselineSha256 '4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd' `
                -AugmentedBaselinePath ([string]$Lease.historical_baseline_path) `
                -AugmentedBaselineSha256 ([string]$Lease.historical_baseline_sha256)
        } catch {
            $Historical = [ordered]@{
                schema_version = 1
                exact_set_match = $false
                status = 'DRIFT'
                error = $_.Exception.Message
            }
            $Terminal = $TerminalInconclusive
            $ExitCode = 2
            if ($null -eq $Failure) { $Failure = $_.Exception.Message }
        }
        Write-NewText -Path (Join-Path $AuditRoot '30-historical-preservation.json') -Text (($Historical | ConvertTo-Json -Depth 8 -Compress) + "`n")
        $ResultDocument = [ordered]@{
            schema_version = 1
            run_id = $RunId
            source_commit = $SourceCommit
            image_tag = $ImageTag
            image_digest = $ImageDigest
            base_image_digest = $BaseDigest
            terminal = $Terminal
            exit_code = $ExitCode
            failure = $Failure
            timestamp = [DateTimeOffset]::UtcNow.ToString('o')
        }
        Write-NewText -Path (Join-Path $AuditRoot '40-campaign-result.json') -Text (($ResultDocument | ConvertTo-Json -Depth 8 -Compress) + "`n")
        $Manifest = @(Get-ChildItem -LiteralPath $CampaignRoot -File -Recurse -Force | Sort-Object FullName | ForEach-Object {
            Get-RelativeFileRecord -Root $CampaignRoot -Path $_.FullName
        })
        Write-NewText -Path (Join-Path $AuditRoot '41-campaign-file-manifest.json') -Text (([ordered]@{ files = $Manifest } | ConvertTo-Json -Depth 8 -Compress) + "`n")
        $ClosureFiles = @(
            '30-historical-preservation.json',
            '40-campaign-result.json',
            '41-campaign-file-manifest.json'
        )
        $AggregateReceipt = Join-Path $CampaignRoot 'a7\aggregate\receipt.json'
        $Closure = [ordered]@{
            schema_version = 1
            run_id = $RunId
            terminal = $Terminal
            files = @($ClosureFiles | ForEach-Object {
                Get-RelativeFileRecord -Root $CampaignRoot -Path (Join-Path $AuditRoot $_)
            })
            aggregate = if (Test-Path -LiteralPath $AggregateReceipt -PathType Leaf) {
                Get-RelativeFileRecord -Root $CampaignRoot -Path $AggregateReceipt
            } else { $null }
            closed_at = [DateTimeOffset]::UtcNow.ToString('o')
        }
        Write-NewText -Path (Join-Path $AuditRoot '51-campaign-closure-manifest.json') -Text (($Closure | ConvertTo-Json -Depth 8 -Compress) + "`n")
    } finally {
        Release-A7Lease -ActivePath $LeasePath -ReleasedPath $ReleasedLeasePath -RecordPath $ReleaseRecordPath
    }
}

Write-Output $Terminal
exit $ExitCode
