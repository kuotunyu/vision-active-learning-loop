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
    $BuildPath = Join-Path $AuditRoot '20-image-build-result.json'
    $MicrocheckPath = Join-Path $AuditRoot '22-a7-cpu-micro-check.json'
    $AssertRegularFile = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $FullPath = [IO.Path]::GetFullPath($Path)
        if (-not [IO.File]::Exists($FullPath) -or [IO.Directory]::Exists($FullPath)) {
            throw 'Task 7 audit-bound file is missing'
        }
        $Current = [IO.FileInfo]::new($FullPath)
        while ($null -ne $Current) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'Task 7 audit-bound link or junction is forbidden'
            }
            $Current = $Current.Parent
        }
        return $FullPath
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    foreach ($Path in @($BuildPath, $MicrocheckPath)) { [void](& $AssertRegularFile $Path) }
    if ([string]$Lease.build_audit_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        [string]$Lease.microcheck_audit_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        (& $GetSha256 $BuildPath) -cne [string]$Lease.build_audit_sha256 -or
        (& $GetSha256 $MicrocheckPath) -cne [string]$Lease.microcheck_audit_sha256) {
        throw 'Task 7 binding-audit identity mismatch'
    }
    try {
        $BuildAudit = Get-Content -LiteralPath $BuildPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $MicrocheckAudit = Get-Content -LiteralPath $MicrocheckPath -Raw -Encoding UTF8 | ConvertFrom-Json
    }
    catch {
        throw 'Task 7 binding-audit JSON is invalid'
    }
    $AssertProperties = {
        param(
            [Parameter(Mandatory = $true)][object]$Document,
            [Parameter(Mandatory = $true)][string[]]$Expected,
            [Parameter(Mandatory = $true)][string]$Name
        )
        $Actual = @($Document.PSObject.Properties.Name | Sort-Object -CaseSensitive)
        $SortedExpected = @($Expected | Sort-Object -CaseSensitive)
        if (($Actual -join '|') -cne ($SortedExpected -join '|')) {
            throw "Task 7 $Name property set is not closed"
        }
    }
    & $AssertProperties $BuildAudit @(
        'schema_version', 'owner_authorization_id', 'run_id', 'source_commit',
        'spec_commit', 'plan_commit', 'branch', 'image_tag', 'image_id',
        'base_image_digest', 'argv', 'augmented_baseline_path',
        'augmented_baseline_sha256', 'argv_audit_path', 'argv_audit_sha256',
        'stdout_path', 'stdout_sha256', 'stderr_path', 'stderr_sha256',
        'exit_code', 'started_at', 'completed_at'
    ) 'build audit'
    & $AssertProperties $MicrocheckAudit @(
        'schema_version', 'owner_authorization_id', 'run_id', 'source_commit',
        'spec_commit', 'plan_commit', 'branch', 'image_tag', 'image_id',
        'base_image_digest', 'augmented_baseline_path', 'augmented_baseline_sha256',
        'source_inventory_path', 'source_inventory_sha256', 'payload_path',
        'payload_sha256', 'payload', 'docker_argv', 'stdout_path', 'stdout_sha256',
        'stderr_path', 'stderr_sha256', 'exit_code', 'started_at', 'completed_at'
    ) 'micro-check audit'
    foreach ($Audit in @($BuildAudit, $MicrocheckAudit)) {
        if ([int]$Audit.schema_version -ne 1 -or
            [string]::IsNullOrWhiteSpace([string]$Lease.branch) -or
            [string]$Audit.owner_authorization_id -cne [string]$Lease.owner_authorization_id -or
            [string]$Audit.run_id -cne [string]$Lease.run_id -or
            [string]$Audit.source_commit -cne [string]$Lease.source_commit -or
            [string]$Audit.spec_commit -cne [string]$Lease.spec_commit -or
            [string]$Audit.plan_commit -cne [string]$Lease.plan_commit -or
            [string]$Audit.branch -cne [string]$Lease.branch -or
            [string]$Audit.image_tag -cne [string]$Lease.image_tag -or
            [string]$Audit.image_id -cne [string]$Lease.image_id -or
            [string]$Audit.base_image_digest -cne [string]$Lease.base_image_digest -or
            [string]$Audit.augmented_baseline_path -cne [string]$Lease.historical_baseline_path -or
            [string]$Audit.augmented_baseline_sha256 -cne [string]$Lease.historical_baseline_sha256 -or
            [int]$Audit.exit_code -ne 0) {
            throw 'Task 7 binding-audit lease identity mismatch'
        }
        $StartedAt = [DateTimeOffset]::MinValue
        $CompletedAt = [DateTimeOffset]::MinValue
        $StartedValid = if ($Audit.started_at -is [DateTime]) {
            $StartedAt = [DateTimeOffset]$Audit.started_at
            $true
        }
        else {
            [DateTimeOffset]::TryParseExact(
                [string]$Audit.started_at,
                'o',
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::RoundtripKind,
                [ref]$StartedAt
            )
        }
        $CompletedValid = if ($Audit.completed_at -is [DateTime]) {
            $CompletedAt = [DateTimeOffset]$Audit.completed_at
            $true
        }
        else {
            [DateTimeOffset]::TryParseExact(
                [string]$Audit.completed_at,
                'o',
                [Globalization.CultureInfo]::InvariantCulture,
                [Globalization.DateTimeStyles]::RoundtripKind,
                [ref]$CompletedAt
            )
        }
        if (-not $StartedValid -or -not $CompletedValid -or $CompletedAt -lt $StartedAt) {
            throw 'Task 7 binding-audit timestamp is invalid'
        }
    }
    $Paths = [ordered]@{
        build_argv = Join-Path $AuditRoot '19-image-build-argv.json'
        build_stdout = Join-Path $AuditRoot '20-image-build.stdout.log'
        build_stderr = Join-Path $AuditRoot '20-image-build.stderr.log'
        source_inventory = Join-Path $AuditRoot '21-a7-source-inventory.json'
        payload = Join-Path $AuditRoot '22-a7-cpu-micro-check-payload.json'
        microcheck_stdout = Join-Path $AuditRoot '22-a7-cpu-micro-check.stdout.log'
        microcheck_stderr = Join-Path $AuditRoot '22-a7-cpu-micro-check.stderr.log'
    }
    if ([string]$BuildAudit.argv_audit_path -cne $Paths.build_argv -or
        [string]$BuildAudit.stdout_path -cne $Paths.build_stdout -or
        [string]$BuildAudit.stderr_path -cne $Paths.build_stderr -or
        [string]$MicrocheckAudit.source_inventory_path -cne $Paths.source_inventory -or
        [string]$MicrocheckAudit.payload_path -cne $Paths.payload -or
        [string]$MicrocheckAudit.stdout_path -cne $Paths.microcheck_stdout -or
        [string]$MicrocheckAudit.stderr_path -cne $Paths.microcheck_stderr) {
        throw 'Task 7 binding-audit supporting path mismatch'
    }
    $Hashes = [ordered]@{
        build_argv = [string]$BuildAudit.argv_audit_sha256
        build_stdout = [string]$BuildAudit.stdout_sha256
        build_stderr = [string]$BuildAudit.stderr_sha256
        source_inventory = [string]$MicrocheckAudit.source_inventory_sha256
        payload = [string]$MicrocheckAudit.payload_sha256
        microcheck_stdout = [string]$MicrocheckAudit.stdout_sha256
        microcheck_stderr = [string]$MicrocheckAudit.stderr_sha256
    }
    foreach ($Name in $Paths.Keys) {
        [void](& $AssertRegularFile $Paths[$Name])
        if ($Hashes[$Name] -cnotmatch '^[0-9a-f]{64}$' -or
            (& $GetSha256 $Paths[$Name]) -cne $Hashes[$Name]) {
            throw "Task 7 binding-audit supporting hash mismatch: $Name"
        }
    }
    try {
        $ArgvAudit = Get-Content -LiteralPath $Paths.build_argv -Raw -Encoding UTF8 | ConvertFrom-Json
        $SourceInventory = Get-Content -LiteralPath $Paths.source_inventory -Raw -Encoding UTF8 |
            ConvertFrom-Json
        $PayloadText = Get-Content -LiteralPath $Paths.payload -Raw -Encoding UTF8
        $Payload = $PayloadText | ConvertFrom-Json
    }
    catch { throw 'Task 7 binding-audit supporting JSON is invalid' }
    & $AssertProperties $ArgvAudit @(
        'schema_version', 'run_id', 'source_commit', 'argv', 'recorded_before_build'
    ) 'build argv audit'
    if ([int]$ArgvAudit.schema_version -ne 1 -or
        [string]$ArgvAudit.run_id -cne [string]$Lease.run_id -or
        [string]$ArgvAudit.source_commit -cne [string]$Lease.source_commit -or
        -not [bool]$ArgvAudit.recorded_before_build -or
        (ConvertTo-Json -InputObject @($BuildAudit.argv) -Compress) -cne
        (ConvertTo-Json -InputObject @($ArgvAudit.argv) -Compress)) {
        throw 'Task 7 build argv audit binding mismatch'
    }
    if ([string]$SourceInventory.source_commit -cne [string]$Lease.source_commit -or
        [string]$Payload.source_commit -cne [string]$Lease.source_commit -or
        [string]$Payload.source_inventory_sha256 -cne $Hashes.source_inventory -or
        (ConvertTo-Json -InputObject $MicrocheckAudit.payload -Depth 8 -Compress) -cne $PayloadText) {
        throw 'Task 7 micro-check payload binding mismatch'
    }
    $MicrocheckArgv = @($MicrocheckAudit.docker_argv)
    if ($MicrocheckArgv.Count -ne 19 -or
        [string]$MicrocheckArgv[0] -cne 'docker' -or
        [string]$MicrocheckArgv[1] -cne 'run' -or
        [string]$MicrocheckArgv[2] -cne '--rm' -or
        [string]$MicrocheckArgv[3] -cne '--network' -or
        [string]$MicrocheckArgv[4] -cne 'none' -or
        [string]$MicrocheckArgv[5] -cne '--workdir' -or
        [string]$MicrocheckArgv[6] -cne '/workspace' -or
        [string]$MicrocheckArgv[7] -cne '--entrypoint' -or
        [string]$MicrocheckArgv[8] -cne 'python' -or
        [string]$MicrocheckArgv[9] -cne '-v' -or
        -not ([string]$MicrocheckArgv[10]).EndsWith(':/workspace:ro', [StringComparison]::Ordinal) -or
        [string]$MicrocheckArgv[11] -cne '-v' -or
        [string]$MicrocheckArgv[12] -cne "${AuditRoot}:/audit:ro" -or
        [string]$MicrocheckArgv[13] -cne [string]$Lease.image_id -or
        [string]$MicrocheckArgv[14] -cne '/workspace/scripts/run_wave0_a7_cpu_microcheck.py' -or
        [string]$MicrocheckArgv[15] -cne '--workspace-root' -or
        [string]$MicrocheckArgv[16] -cne '/workspace' -or
        [string]$MicrocheckArgv[17] -cne '--source-inventory' -or
        [string]$MicrocheckArgv[18] -cne '/audit/21-a7-source-inventory.json') {
        throw 'Task 7 micro-check Docker argv binding mismatch'
    }
    $StdoutLines = @(Get-Content -LiteralPath $Paths.microcheck_stdout -Encoding UTF8 |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($StdoutLines.Count -ne 1 -or [string]$StdoutLines[0] -cne $PayloadText) {
        throw 'Task 7 micro-check stdout does not equal the raw payload'
    }
}

function Test-A7ProtectedGitLineage {
    param(
        [Parameter(Mandatory = $true)][string]$RootBaselinePath,
        [Parameter(Mandatory = $true)][string]$RootBaselineSha256,
        [Parameter(Mandatory = $true)][string]$AugmentedBaselinePath,
        [Parameter(Mandatory = $true)][string]$AugmentedBaselineSha256,
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit
    )
    $TransitionPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
    $PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
    $TransitionReason = 'owner-approved-design-amendment'
    foreach ($Commit in @($SourceCommit, $SpecCommit, $PlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 protected Git commit identity is invalid'
        }
    }
    foreach ($ExpectedHash in @($RootBaselineSha256, $AugmentedBaselineSha256)) {
        if ($ExpectedHash -cnotmatch '^[0-9a-f]{64}$') {
            throw 'A7 protected Git baseline identity is invalid'
        }
    }
    foreach ($Path in @($RootBaselinePath, $AugmentedBaselinePath)) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            throw 'A7 protected Git baseline is unavailable'
        }
        $Item = Get-Item -LiteralPath $Path -Force
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 protected Git baseline must not be linked'
        }
    }
    $ObservedRootHash = (Get-FileHash -LiteralPath $RootBaselinePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $ObservedAugmentedHash = (
        Get-FileHash -LiteralPath $AugmentedBaselinePath -Algorithm SHA256
    ).Hash.ToLowerInvariant()
    if ($ObservedRootHash -cne $RootBaselineSha256 -or
        $ObservedAugmentedHash -cne $AugmentedBaselineSha256) {
        throw 'A7 protected Git baseline hash mismatch'
    }
    $RootBaseline = Get-Content -LiteralPath $RootBaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $AugmentedBaseline = Get-Content -LiteralPath $AugmentedBaselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $RootRecords = @($RootBaseline.protected_git)
    $AugmentedRootRecords = @($AugmentedBaseline.protected_git)
    $CurrentRecords = @($AugmentedBaseline.current_protected_git)
    $Transitions = @($AugmentedBaseline.approved_protected_git_transitions)
    if ($RootRecords.Count -ne 68 -or $AugmentedRootRecords.Count -ne 68 -or
        $CurrentRecords.Count -ne 68 -or $Transitions.Count -ne 1) {
        throw 'A7 protected Git inventory or transition count mismatch'
    }
    if ((ConvertTo-Json -InputObject $RootRecords -Depth 6 -Compress) -cne
        (ConvertTo-Json -InputObject $AugmentedRootRecords -Depth 6 -Compress)) {
        throw 'A7 augmented baseline changes the immutable protected Git root array'
    }
    $AssertProperties = {
        param(
            [Parameter(Mandatory = $true)][object]$Record,
            [Parameter(Mandatory = $true)][string[]]$Expected,
            [Parameter(Mandatory = $true)][string]$Description
        )
        $Actual = @($Record.PSObject.Properties.Name | Sort-Object -CaseSensitive)
        $SortedExpected = @($Expected | Sort-Object -CaseSensitive)
        if (($Actual -join '|') -cne ($SortedExpected -join '|')) {
            throw "A7 protected Git $Description property set mismatch"
        }
    }
    $RecordProperties = @('path', 'size', 'sha256')
    $TransitionProperties = @(
        'path',
        'root_size',
        'root_sha256',
        'current_size',
        'current_sha256',
        'spec_commit',
        'spec_git_object',
        'plan_commit',
        'reason'
    )
    $RootByPath = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    $CurrentByPath = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($Record in $RootRecords) {
        & $AssertProperties $Record $RecordProperties 'root record'
        $RelativePath = [string]$Record.path
        if ([string]::IsNullOrWhiteSpace($RelativePath) -or
            $RelativePath.Contains('\') -or [IO.Path]::IsPathRooted($RelativePath) -or
            [string]$Record.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            $null -eq $Record.size -or [long]$Record.size -lt 0) {
            throw 'A7 protected Git root record is invalid'
        }
        try { $RootByPath.Add($RelativePath, $Record) } catch {
            throw "A7 protected Git root path is duplicated: $RelativePath"
        }
    }
    foreach ($Record in $CurrentRecords) {
        & $AssertProperties $Record $RecordProperties 'current record'
        $RelativePath = [string]$Record.path
        if ([string]::IsNullOrWhiteSpace($RelativePath) -or
            $RelativePath.Contains('\') -or [IO.Path]::IsPathRooted($RelativePath) -or
            [string]$Record.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            $null -eq $Record.size -or [long]$Record.size -lt 0) {
            throw 'A7 protected Git current record is invalid'
        }
        try { $CurrentByPath.Add($RelativePath, $Record) } catch {
            throw "A7 protected Git current path is duplicated: $RelativePath"
        }
    }
    $RootPaths = @($RootByPath.Keys | Sort-Object -CaseSensitive)
    $CurrentPaths = @($CurrentByPath.Keys | Sort-Object -CaseSensitive)
    if (($RootPaths -join "`n") -cne ($CurrentPaths -join "`n")) {
        throw 'A7 protected Git current inventory differs from the root inventory'
    }
    $Transition = $Transitions[0]
    & $AssertProperties $Transition $TransitionProperties 'transition'
    if ([string]$Transition.path -cne $TransitionPath -or
        [string]$Transition.reason -cne $TransitionReason -or
        [string]$Transition.spec_commit -cne $SpecCommit -or
        [string]$Transition.plan_commit -cne $PlanCommit -or
        [string]$Transition.spec_git_object -cnotmatch '^[0-9a-f]{40}$') {
        throw 'A7 protected Git approved transition identity mismatch'
    }
    if (-not $RootByPath.ContainsKey($TransitionPath) -or
        -not $CurrentByPath.ContainsKey($TransitionPath)) {
        throw 'A7 protected Git approved transition path is absent'
    }
    $RootTransition = $RootByPath[$TransitionPath]
    $CurrentTransition = $CurrentByPath[$TransitionPath]
    if ([long]$Transition.root_size -ne [long]$RootTransition.size -or
        [string]$Transition.root_sha256 -cne [string]$RootTransition.sha256 -or
        [long]$Transition.current_size -ne [long]$CurrentTransition.size -or
        [string]$Transition.current_sha256 -cne [string]$CurrentTransition.sha256 -or
        ([long]$RootTransition.size -eq [long]$CurrentTransition.size -and
            [string]$RootTransition.sha256 -ceq [string]$CurrentTransition.sha256)) {
        throw 'A7 protected Git transition record does not bind root and current identities'
    }
    foreach ($RelativePath in $RootPaths) {
        if ($RelativePath -ceq $TransitionPath) { continue }
        $RootRecord = $RootByPath[$RelativePath]
        $CurrentRecord = $CurrentByPath[$RelativePath]
        if ([long]$RootRecord.size -ne [long]$CurrentRecord.size -or
            [string]$RootRecord.sha256 -cne [string]$CurrentRecord.sha256) {
            throw "A7 unapproved protected Git transition detected: $RelativePath"
        }
    }
    $ProjectRootFull = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
    $ProjectItem = Get-Item -LiteralPath $ProjectRootFull -Force -ErrorAction Stop
    if (-not $ProjectItem.PSIsContainer -or
        ($ProjectItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'A7 protected Git project root is missing or linked'
    }
    $ProjectPrefix = $ProjectRootFull + [IO.Path]::DirectorySeparatorChar
    foreach ($RelativePath in $CurrentPaths) {
        $Candidate = [IO.Path]::GetFullPath(
            (Join-Path $ProjectRootFull $RelativePath.Replace('/', [IO.Path]::DirectorySeparatorChar))
        )
        if (-not $Candidate.StartsWith($ProjectPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "A7 protected Git path escapes the project root: $RelativePath"
        }
        $Cursor = $Candidate
        while ($Cursor.StartsWith($ProjectPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
            if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "A7 protected Git path is linked: $RelativePath"
            }
            if ($Cursor -ceq $Candidate -and $Item.PSIsContainer) {
                throw "A7 protected Git path is not a file: $RelativePath"
            }
            $Cursor = Split-Path -Parent $Cursor
        }
        $Record = $CurrentByPath[$RelativePath]
        $Hash = (Get-FileHash -LiteralPath $Candidate -Algorithm SHA256).Hash.ToLowerInvariant()
        if ([long](Get-Item -LiteralPath $Candidate -Force).Length -ne [long]$Record.size -or
            $Hash -cne [string]$Record.sha256) {
            throw "A7 protected Git checkout identity mismatch: $RelativePath"
        }
    }
    $GitCommand = Get-Command -Name 'git' -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $GitItem = Get-Item -LiteralPath $GitCommand.Source -Force
    if (($GitItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'A7 protected Git executable is linked'
    }
    $InvokeGit = {
        param([Parameter(Mandatory = $true)][string[]]$Arguments)
        $Output = @(& $GitCommand.Source @Arguments 2>&1)
        if ($LASTEXITCODE -ne 0) {
            throw "A7 protected Git command failed: $($Output -join '; ')"
        }
        return ($Output -join "`n").Trim()
    }
    if ((& $InvokeGit @('-C', $ProjectRootFull, 'rev-parse', 'HEAD')) -cne $SourceCommit -or
        -not [string]::IsNullOrEmpty([string](& $InvokeGit @(
                    '-C', $ProjectRootFull, 'status', '--porcelain=v1'
                )))) {
        throw 'A7 protected Git checkout identity or cleanliness mismatch'
    }
    if ((& $InvokeGit @('-C', $ProjectRootFull, 'rev-parse', "$PlanCommit^")) -cne $SpecCommit) {
        throw 'A7 protected Git plan is not the direct child of the specification'
    }
    if ((& $InvokeGit @(
                '-C', $ProjectRootFull, 'log', '-1', '--format=%H', '--', $TransitionPath
            )) -cne $SpecCommit -or
        (& $InvokeGit @(
                '-C', $ProjectRootFull, 'log', '-1', '--format=%H', '--', $PlanPath
            )) -cne $PlanCommit) {
        throw 'A7 protected Git last-touch lineage mismatch'
    }
    $SpecFiles = @((& $InvokeGit @(
                '-C', $ProjectRootFull, 'diff-tree', '--no-commit-id', '--name-only', '-r', $SpecCommit
            )) -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $PlanFiles = @((& $InvokeGit @(
                '-C', $ProjectRootFull, 'diff-tree', '--no-commit-id', '--name-only', '-r', $PlanCommit
            )) -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($SpecFiles.Count -ne 1 -or $SpecFiles[0] -cne $TransitionPath -or
        $PlanFiles.Count -ne 1 -or $PlanFiles[0] -cne $PlanPath) {
        throw 'A7 protected Git specification or plan commit scope mismatch'
    }
    $SpecGitObject = & $InvokeGit @(
        '-C', $ProjectRootFull, 'rev-parse', "${SpecCommit}:$TransitionPath"
    )
    $TransitionFullPath = [IO.Path]::GetFullPath(
        (Join-Path $ProjectRootFull $TransitionPath.Replace('/', [IO.Path]::DirectorySeparatorChar))
    )
    $CheckoutGitObject = & $InvokeGit @(
        '-C', $ProjectRootFull, 'hash-object', "--path=$TransitionPath", '--', $TransitionFullPath
    )
    if ($SpecGitObject -cnotmatch '^[0-9a-f]{40}$' -or
        $CheckoutGitObject -cne $SpecGitObject -or
        [string]$Transition.spec_git_object -cne $SpecGitObject) {
        throw 'A7 protected Git specification object mismatch'
    }
    return [ordered]@{
        root_protected_git_count = $RootRecords.Count
        current_protected_git_count = $CurrentRecords.Count
        approved_transition_count = $Transitions.Count
        status = 'PRESERVED'
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
            $RootBaselinePath = Join-Path $env:TEMP 'val-a7-baseline-11a6b1929b0b4d44acc0a090887b50dd670357ea.json'
            $RootBaselineSha256 = '4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd'
            $ProtectedGit = Test-A7ProtectedGitLineage `
                -RootBaselinePath $RootBaselinePath `
                -RootBaselineSha256 $RootBaselineSha256 `
                -AugmentedBaselinePath ([string]$Lease.historical_baseline_path) `
                -AugmentedBaselineSha256 ([string]$Lease.historical_baseline_sha256) `
                -ProjectRoot $ProjectRoot `
                -SourceCommit $SourceCommit `
                -SpecCommit ([string]$Lease.spec_commit) `
                -PlanCommit ([string]$Lease.plan_commit)
            $Historical = Test-HistoricalBaseline `
                -RootBaselinePath $RootBaselinePath `
                -RootBaselineSha256 $RootBaselineSha256 `
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
