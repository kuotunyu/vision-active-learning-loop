param(
    [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedBranch,
    [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-A11NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [Text.UTF8Encoding]::new($false)
    $Stream = [IO.FileStream]::new(
        $Path, [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write, [IO.FileShare]::None
    )
    try {
        $Bytes = $Encoding.GetBytes($Text)
        $Stream.Write($Bytes, 0, $Bytes.Length)
        $Stream.Flush($true)
    } finally {
        $Stream.Dispose()
    }
}

function Get-A11FileRecord {
    param([Parameter(Mandatory = $true)][string]$Path)
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "A11 evidence is not a regular non-link file: $Path"
    }
    return [ordered]@{
        path = $Item.FullName.Replace('\', '/')
        size = [long]$Item.Length
        sha256 = (Get-FileHash -LiteralPath $Item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

function Get-A11VerifiedStageReceipt {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Root = [IO.Path]::GetFullPath([string]$Identity.campaign_root)
    $FullPath = [IO.Path]::GetFullPath($Path)
    $Relative = [IO.Path]::GetRelativePath($Root, $FullPath)
    if (
        [IO.Path]::IsPathRooted($Relative) -or $Relative -ceq '..' -or
        $Relative.StartsWith('..\', [StringComparison]::Ordinal) -or
        $Relative.StartsWith('../', [StringComparison]::Ordinal)
    ) { throw "A11 stage receipt escapes the phase root: $Path" }
    $Separators = [char[]]@(
        [IO.Path]::DirectorySeparatorChar,
        [IO.Path]::AltDirectorySeparatorChar
    )
    $Segments = @($Relative.Split($Separators, [StringSplitOptions]::RemoveEmptyEntries))
    if ($Segments.Count -eq 0) { throw "A11 stage receipt path is invalid: $Path" }
    $Cursor = $Root
    for ($Index = -1; $Index -lt $Segments.Count; $Index++) {
        if ($Index -ge 0) { $Cursor = [IO.Path]::Combine($Cursor, $Segments[$Index]) }
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A11 stage receipt path contains a link: $Path"
        }
        if ($Index -lt ($Segments.Count - 1) -and -not $Item.PSIsContainer) {
            throw "A11 stage receipt ancestor is not a directory: $Path"
        }
        if ($Index -eq ($Segments.Count - 1) -and $Item.PSIsContainer) {
            throw "A11 stage receipt is not a regular file: $Path"
        }
    }
    $Document = Get-Content -Raw -LiteralPath $FullPath | ConvertFrom-Json
    if (
        [string]$Document.metadata.run_id -cne [string]$Identity.run_id -or
        [string]$Document.normative.status -cne 'PASS' -or
        @($Document.normative.errors).Count -ne 0
    ) { throw "A11 stage receipt contract failed: $Path" }
    return Get-A11FileRecord -Path $FullPath
}

function Assert-A11FileRecordUnchanged {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][object]$Expected,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Observed = Get-A11VerifiedStageReceipt -Identity $Identity -Path $Path
    if (
        [string]$Observed.path -cne [string]$Expected.path -or
        [long]$Observed.size -ne [long]$Expected.size -or
        [string]$Observed.sha256 -cne [string]$Expected.sha256
    ) { throw "A11 verified receipt changed before use: $Path" }
    return $true
}

function Get-A11JsonSha256 {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Value,
        [int]$Depth = 12
    )
    $Json = ConvertTo-Json -InputObject @($Value) -Depth $Depth -Compress
    $Bytes = [Text.Encoding]::UTF8.GetBytes($Json)
    return [Convert]::ToHexString(
        [Security.Cryptography.SHA256]::HashData($Bytes)
    ).ToLowerInvariant()
}

function Get-A11HistoricalArtifactInventory {
    param([Parameter(Mandatory = $true)][string]$ArtifactRoot)
    $Linked = @(Get-ChildItem -LiteralPath $ArtifactRoot -Recurse -Force |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($Linked.Count -ne 0) { throw 'A11 historical artifact tree contains a link' }
    $Records = @(
        Get-ChildItem -LiteralPath $ArtifactRoot -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    throw "A11 historical artifact is linked: $($_.FullName)"
                }
                $Relative = $_.FullName.Substring($ArtifactRoot.Length + 1).Replace('\', '/')
                if (
                    $Relative -notlike 'a11-runs/*' -and
                    $Relative -notlike 'leases/wave0-a11-*' -and
                    $Relative -cne 'leases/GPU-7639cc81-2a55-164e-e5be-c5cd71752a63.json'
                ) {
                    [ordered]@{
                        path = $Relative
                        size = [long]$_.Length
                        sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                    }
                }
            }
    )
    return [pscustomobject][ordered]@{
        records = $Records
        sha256 = Get-A11JsonSha256 -Value $Records -Depth 6
    }
}

function Get-A11HistoricalImageInventory {
    $Tags = @(& docker image ls --filter 'reference=vision-active-learning-loop:*' `
        --format '{{.Repository}}:{{.Tag}}' | Where-Object {
            $_ -notlike 'vision-active-learning-loop:wave0-a11-*'
        } | Sort-Object -Unique)
    $Records = @($Tags | ForEach-Object {
        $Tag = $_
        $Raw = & docker image inspect -- $Tag
        if ($LASTEXITCODE -ne 0) { throw "A11 image inspect failed: $Tag" }
        $Values = @($Raw | ConvertFrom-Json)
        if ($Values.Count -ne 1) { throw "A11 image inspect count mismatch: $Tag" }
        $Labels = [ordered]@{}
        foreach ($Name in @($Values[0].Config.Labels.PSObject.Properties.Name | Sort-Object)) {
            $Labels[$Name] = [string]$Values[0].Config.Labels.$Name
        }
        [ordered]@{
            tag = $Tag
            image_id = [string]$Values[0].Id
            labels = $Labels
        }
    })
    return [pscustomobject][ordered]@{
        records = $Records
        sha256 = Get-A11JsonSha256 -Value $Records -Depth 8
    }
}

function Get-A11PriorAttemptInventory {
    param([Parameter(Mandatory = $true)][string]$ArtifactRoot)
    $RunId = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
    $ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
    $A11Root = [IO.Path]::Combine($ArtifactRoot, 'a11-runs')
    $RunRoot = [IO.Path]::Combine($A11Root, $RunId)
    $LeaseRoot = [IO.Path]::Combine($ArtifactRoot, 'leases')
    $ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$RunId.released")
    $ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$RunId.release.json")
    foreach ($Path in @(
        $A11Root, $RunRoot, $LeaseRoot, $ReleasedPath, $ReleaseRecordPath
    )) {
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A11 prior attempt path contains a link: $Path"
        }
    }
    $Linked = @(Get-ChildItem -LiteralPath $RunRoot -Recurse -Force |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($Linked.Count -ne 0) { throw 'A11 prior attempt tree contains a link' }
    $Records = @(
        Get-ChildItem -LiteralPath $RunRoot -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($RunRoot.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $RunNames = @(Get-ChildItem -LiteralPath $A11Root -Directory -Force |
        Sort-Object Name -CaseSensitive | ForEach-Object Name)
    $LeaseNames = @(Get-ChildItem -LiteralPath $LeaseRoot -File -Force |
        Where-Object { $_.Name -like 'wave0-a11-*' } |
        Sort-Object Name -CaseSensitive | ForEach-Object Name)
    $ClosurePresent = @(@(
        '78-failure-diagnostic.json', '80-campaign-result.json',
        '81-campaign-file-manifest.json', '82-campaign-closure.json'
    ) | Where-Object {
        Test-Path -LiteralPath ([IO.Path]::Combine($RunRoot, 'audit', $_))
    })
    $List = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
        'image', 'ls', '--filter',
        'reference=vision-active-learning-loop:wave0-a11-*',
        '--format', '{{.Repository}}:{{.Tag}}'
    )
    if ($List.ExitCode -ne 0 -or $List.Stderr -cne '') {
        throw 'A11 prior image inventory failed'
    }
    $ImageTags = @($List.Stdout -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } | Sort-Object -CaseSensitive -Unique)
    $Inspect = Invoke-A11Native -FilePath 'docker' `
        -ArgumentList @('image', 'inspect', '--', $ImageTag)
    if ($Inspect.ExitCode -ne 0 -or $Inspect.Stderr -cne '') {
        throw 'A11 prior image inspect failed'
    }
    $Images = @($Inspect.Stdout | ConvertFrom-Json)
    if ($Images.Count -ne 1) { throw 'A11 prior image inspect count mismatch' }
    return [pscustomobject][ordered]@{
        run_names = $RunNames
        run_file_count = $Records.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records -Depth 6
        historical_preservation_sha256 = (Get-FileHash -LiteralPath `
            ([IO.Path]::Combine($RunRoot, 'audit', '79-historical-preservation-final.json')) `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        released_lease_sha256 = (Get-FileHash -LiteralPath $ReleasedPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        release_record_sha256 = (Get-FileHash -LiteralPath $ReleaseRecordPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        closure_paths_present = $ClosurePresent
        image_tags = $ImageTags
        image_id = [string]$Images[0].Id
        lease_names = $LeaseNames
        links_absent = $true
    }
}

function Invoke-A11Native {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$ArgumentList = @(),
        [string]$WorkingDirectory = ''
    )
    $Application = Get-Command -Name $FilePath -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $Start = [Diagnostics.ProcessStartInfo]::new()
    $Start.FileName = $Application.Source
    $Start.UseShellExecute = $false
    $Start.RedirectStandardOutput = $true
    $Start.RedirectStandardError = $true
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $Start.WorkingDirectory = [IO.Path]::GetFullPath($WorkingDirectory)
    }
    foreach ($Argument in $ArgumentList) { [void]$Start.ArgumentList.Add($Argument) }
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = $Start
    if (-not $Process.Start()) { throw "unable to start $FilePath" }
    $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
    $StderrTask = $Process.StandardError.ReadToEndAsync()
    $Process.WaitForExit()
    $Stdout = $StdoutTask.GetAwaiter().GetResult()
    $Stderr = $StderrTask.GetAwaiter().GetResult()
    return [pscustomobject][ordered]@{
        ExitCode = [int]$Process.ExitCode
        Stdout = $Stdout
        Stderr = $Stderr
    }
}

function Write-A11ProcessAudit {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Argv,
        [Parameter(Mandatory = $true)][object]$Result,
        [AllowNull()][object]$ReceiptRecord = $null
    )
    $AuditRoot = [IO.Path]::Combine($Identity.campaign_root, 'audit')
    $StdoutPath = [IO.Path]::Combine($AuditRoot, "$Name.stdout.log")
    $StderrPath = [IO.Path]::Combine($AuditRoot, "$Name.stderr.log")
    Write-A11NewText -Path $StdoutPath -Text ([string]$Result.Stdout)
    Write-A11NewText -Path $StderrPath -Text ([string]$Result.Stderr)
    $Document = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        argv = $Argv
        exit_code = [int]$Result.ExitCode
        stdout = Get-A11FileRecord -Path $StdoutPath
        stderr = Get-A11FileRecord -Path $StderrPath
    }
    if ($null -ne $ReceiptRecord) { $Document['receipt'] = $ReceiptRecord }
    $Path = [IO.Path]::Combine($AuditRoot, "$Name.json")
    Write-A11NewText -Path $Path -Text (($Document | ConvertTo-Json -Depth 10 -Compress) + "`n")
    return Get-A11FileRecord -Path $Path
}

function ConvertTo-A11GpuRows {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$GpuCsv,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$ComputeCsv
    )
    $Rows = [Collections.Generic.List[object]]::new()
    $Counts = @{}
    foreach ($Line in @($GpuCsv -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })) {
        $Fields = @($Line.Split(',') | ForEach-Object { $_.Trim() })
        if (
            $Fields.Count -ne 2 -or
            [string]::IsNullOrWhiteSpace($Fields[0]) -or
            $Fields[1] -cnotmatch '^GPU-[A-Za-z0-9-]+$' -or
            $Counts.ContainsKey($Fields[1])
        ) { throw 'A11 host GPU inventory is invalid' }
        $Counts[$Fields[1]] = 0
        [void]$Rows.Add([pscustomobject][ordered]@{
            name = $Fields[0]
            uuid = $Fields[1]
            compute_process_count = 0
        })
    }
    foreach ($Line in @($ComputeCsv -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })) {
        $Fields = @($Line.Split(',') | ForEach-Object { $_.Trim() })
        $PidValue = [long]0
        if (
            $Fields.Count -ne 4 -or
            -not $Counts.ContainsKey($Fields[0]) -or
            -not [long]::TryParse($Fields[1], [ref]$PidValue) -or
            $PidValue -le 0 -or
            [string]::IsNullOrWhiteSpace($Fields[2])
        ) { throw 'A11 host compute-process inventory is invalid' }
        $NumericMemory = [long]0
        if ([long]::TryParse($Fields[3], [ref]$NumericMemory)) {
            if ($NumericMemory -lt 0) { throw 'A11 host compute-process memory state is invalid' }
            $Counts[$Fields[0]]++
        } elseif ($Fields[3] -cne '[N/A]') {
            throw 'A11 host compute-process memory state is invalid'
        }
    }
    foreach ($Row in $Rows) {
        $Row.compute_process_count = [int]$Counts[[string]$Row.uuid]
    }
    return @($Rows)
}

function Get-A11ActiveLeasePaths {
    param([Parameter(Mandatory = $true)][string]$LeaseRoot)
    if (-not (Test-Path -LiteralPath $LeaseRoot -PathType Container)) { return @() }
    return @(
        Get-ChildItem -LiteralPath $LeaseRoot -File -Force |
            Where-Object { $_.Name -cmatch '^GPU-[A-Za-z0-9-]+\.json$' } |
            Sort-Object FullName -CaseSensitive |
            ForEach-Object { $_.FullName.Replace('\', '/') }
    )
}

function Resolve-A11Worktree {
    param(
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$AuthorizationId
    )
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $GitDirectory = (& git -C $Worktree rev-parse --absolute-git-dir).Trim()
    $CommonDirectory = (& git -C $Worktree rev-parse --path-format=absolute --git-common-dir).Trim()
    $ObservedBranch = (& git -C $Worktree branch --show-current).Trim()
    $Head = (& git -C $Worktree rev-parse HEAD).Trim()
    $PlanParent = (& git -C $Worktree rev-parse "$PlanCommit^").Trim()
    $WorktreeListing = @(& git -C $Worktree worktree list --porcelain)
    $CanonicalLine = $WorktreeListing | Where-Object { $_ -like 'worktree *' } |
        Select-Object -First 1
    $Canonical = if ($null -eq $CanonicalLine) { '' } else { $CanonicalLine.Substring(9) }
    $LinkedStatus = (@(& git -C $Worktree status --porcelain=v1) -join "`n")
    $CanonicalStatus = if ([string]::IsNullOrWhiteSpace($Canonical)) {
        '__missing__'
    } else {
        (@(& git -C $Canonical status --porcelain=v1) -join "`n")
    }
    $DockerContext = (& docker context show).Trim()
    $DockerInfo = (& docker info --format '{{.OSType}}|{{.ServerVersion}}').Trim()
    $DockerParts = $DockerInfo.Split('|', 2)
    $GpuCsv = (& nvidia-smi --query-gpu=name,uuid --format=csv,noheader,nounits) -join "`n"
    $ComputeCsv = (& nvidia-smi `
        --query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory `
        --format=csv,noheader,nounits) -join "`n"
    $GpuRows = @(ConvertTo-A11GpuRows -GpuCsv $GpuCsv -ComputeCsv $ComputeCsv)
    $ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
    if (-not (Test-Path -LiteralPath $ArtifactRoot -PathType Container)) {
        throw 'A11 artifact root is unavailable'
    }
    $HistoricalInventory = Get-A11HistoricalArtifactInventory -ArtifactRoot $ArtifactRoot
    $FixedA10 = [ordered]@{
        'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/environment.json' = '7fc82adaa6053a1d6a9617410b27fa5200882d7c99758567bef2c60c8a704e8f'
        'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/model-assets.json' = 'c1e1620fdaff57e3fc4424a393d925b194301f866e3215089303ec3ad8500483'
        'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/model-contract.json' = '1258c45e5b8b672ca81cc8e2b5af9d955bb22eece3b1aabcf0485174c1a706c0'
        'a7-runs/wave0-a7-20260827T034653088Z/a7/aggregate/receipt.json' = 'f4a6f0f3fd2cc54f319e65141fa1b0a0367a6e14e2baa0df58268b051270251f'
        'a7-runs/wave0-a7-20260827T034653088Z/audit/40-campaign-result.json' = '3f10fbfe8bf33c89fddb71c71e58457f738fa92d933ad05115fa1e66e3126239'
        'a7-runs/wave0-a7-20260827T034653088Z/audit/41-campaign-file-manifest.json' = '55f78146f201d090807fcc62a836ec9db82604e3a878ca2323de85edda85f6e2'
        'a7-runs/wave0-a7-20260827T034653088Z/audit/30-historical-preservation.json' = '93c9093efebfe7c78a9cf6ae6a10f264b52271aee434236a71d68801b9e0ad3f'
        'a7-runs/wave0-a7-20260827T034653088Z/audit/51-campaign-closure-manifest.json' = '3f3c1e548d0454bc81c44e8130e710e7e8d0b47264f69afdb96560d7fbc92162'
    }
    $HistoricalPreserved = $true
    foreach ($Relative in $FixedA10.Keys) {
        $Path = [IO.Path]::Combine($ArtifactRoot, $Relative.Replace('/', '\'))
        if (
            -not (Test-Path -LiteralPath $Path -PathType Leaf) -or
            (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $FixedA10[$Relative]
        ) { $HistoricalPreserved = $false }
    }
    $ImageInventory = Get-A11HistoricalImageInventory
    $ProjectContainers = @(& docker ps --format '{{.ID}}|{{.Image}}' | ForEach-Object {
        $Parts = $_.Split('|', 2)
        $ContainerId = $Parts[0]
        $ImageId = (& docker inspect --format '{{.Image}}' -- $ContainerId).Trim()
        $RepoTagsJson = (& docker image inspect --format '{{json .RepoTags}}' -- $ImageId).Trim()
        $RepoTags = if ($RepoTagsJson -eq 'null') { @() } else { @($RepoTagsJson | ConvertFrom-Json) }
        if (@($RepoTags | Where-Object { $_ -like 'vision-active-learning-loop:*' }).Count -gt 0) {
            "${ContainerId}|$ImageId"
        }
    })
    $PriorA11 = Get-A11PriorAttemptInventory -ArtifactRoot $ArtifactRoot
    $LeaseRoot = [IO.Path]::Combine($ArtifactRoot, 'leases')
    $ActiveLeases = @(Get-A11ActiveLeasePaths -LeaseRoot $LeaseRoot)
    return [ordered]@{
        worktree_path = $Worktree
        git_dir = $GitDirectory
        common_dir = $CommonDirectory
        linked_worktree = ($GitDirectory -cne $CommonDirectory)
        branch = $ObservedBranch
        head = $Head
        spec_commit = $SpecCommit
        plan_commit = $PlanCommit
        plan_parent_is_spec = ($PlanParent -ceq $SpecCommit)
        linked_status = $LinkedStatus
        canonical_status = $CanonicalStatus
        val_data_root_present = (Test-Path Env:VAL_DATA_ROOT)
        docker_context = $DockerContext
        docker_os = if ($DockerParts.Count -gt 0) { $DockerParts[0] } else { '' }
        docker_server_version = if ($DockerParts.Count -gt 1) { $DockerParts[1] } else { '' }
        gpu_rows = $GpuRows
        project_containers = $ProjectContainers
        active_leases = $ActiveLeases
        prior_a11_attempt = $PriorA11
        historical_file_count = @($HistoricalInventory.records).Count
        historical_image_count = @($ImageInventory.records).Count
        historical_file_inventory_sha256 = $HistoricalInventory.sha256
        historical_image_inventory_sha256 = $ImageInventory.sha256
        historical_preserved = (
            $HistoricalPreserved -and
            $HistoricalInventory.sha256 -ceq 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95' -and
            $ImageInventory.sha256 -ceq '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f'
        )
        artifact_root = $ArtifactRoot
        expected_source = $SourceCommit
        expected_branch = $Branch
        authorization_id = $AuthorizationId
    }
}

function Test-A11ReadOnlyPreflight {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceJson,
        [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedBranch,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
    )
    foreach ($Identity in @($ExpectedSourceCommit, $ExpectedSpecCommit, $ExpectedPlanCommit)) {
        if ($Identity -cnotmatch '^[0-9a-f]{40}$') { throw 'A11 commit identity is malformed' }
    }
    if (
        [string]::IsNullOrWhiteSpace($ExpectedBranch) -or
        $OwnerAuthorizationId -cnotmatch '^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$'
    ) { throw 'A11 branch or owner authorization identity is malformed' }
    if ($OwnerAuthorizationId -ceq 'OWNER-A11-RUNTIME-20260828-01') {
        throw 'A11 prior owner authorization cannot be reused'
    }
    $Evidence = $EvidenceJson | ConvertFrom-Json
    $ExpectedKeys = @(
        'worktree_path', 'git_dir', 'common_dir', 'linked_worktree', 'branch',
        'head', 'spec_commit', 'plan_commit', 'plan_parent_is_spec',
        'linked_status', 'canonical_status', 'val_data_root_present',
        'docker_context', 'docker_os', 'docker_server_version', 'gpu_rows',
        'project_containers', 'active_leases', 'prior_a11_attempt',
        'historical_file_count', 'historical_image_count',
        'historical_file_inventory_sha256', 'historical_image_inventory_sha256',
        'historical_preserved'
    )
    $ActualKeys = @($Evidence.PSObject.Properties.Name | Sort-Object)
    if (Compare-Object ($ExpectedKeys | Sort-Object) $ActualKeys) {
        throw 'A11 preflight evidence fields mismatch'
    }
    if (
        $Evidence.linked_worktree -cne $true -or
        [string]$Evidence.git_dir -ceq [string]$Evidence.common_dir -or
        [string]$Evidence.branch -cne $ExpectedBranch -or
        [string]$Evidence.head -cne $ExpectedSourceCommit -or
        [string]$Evidence.spec_commit -cne $ExpectedSpecCommit -or
        [string]$Evidence.plan_commit -cne $ExpectedPlanCommit -or
        $Evidence.plan_parent_is_spec -cne $true
    ) { throw 'A11 Git identity mismatch' }
    if (
        -not [string]::IsNullOrEmpty([string]$Evidence.linked_status) -or
        -not [string]::IsNullOrEmpty([string]$Evidence.canonical_status)
    ) { throw 'A11 protected worktree is dirty' }
    if ($Evidence.val_data_root_present -cne $false) { throw 'VAL_DATA_ROOT must remain unset' }
    if (
        [string]$Evidence.docker_context -cne 'desktop-linux' -or
        [string]$Evidence.docker_os -cne 'linux' -or
        [string]::IsNullOrWhiteSpace([string]$Evidence.docker_server_version)
    ) { throw 'A11 Docker Linux server preflight failed' }
    $GpuRows = @($Evidence.gpu_rows)
    if (
        $GpuRows.Count -ne 1 -or
        [string]$GpuRows[0].name -cne 'NVIDIA GeForce RTX 4090' -or
        [string]$GpuRows[0].uuid -cne 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63' -or
        [int]$GpuRows[0].compute_process_count -ne 0
    ) { throw 'A11 requires exactly one idle registered RTX 4090' }
    if (
        @($Evidence.project_containers).Count -ne 0 -or
        @($Evidence.active_leases).Count -ne 0
    ) { throw 'A11 runtime destination or exclusive resource is occupied' }
    $Prior = $Evidence.prior_a11_attempt
    $ExpectedPriorKeys = @(
        'run_names', 'run_file_count', 'run_inventory_sha256',
        'historical_preservation_sha256', 'released_lease_sha256',
        'release_record_sha256', 'closure_paths_present', 'image_tags',
        'image_id', 'lease_names', 'links_absent'
    )
    $ActualPriorKeys = @($Prior.PSObject.Properties.Name | Sort-Object)
    if (Compare-Object ($ExpectedPriorKeys | Sort-Object) $ActualPriorKeys) {
        throw 'A11 prior A11 evidence fields mismatch'
    }
    $ExpectedRunId = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
    $ExpectedImageTag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
    $RunNames = @($Prior.run_names)
    $ClosurePaths = @($Prior.closure_paths_present)
    $ImageTags = @($Prior.image_tags)
    $LeaseNames = @($Prior.lease_names)
    if (
        $RunNames.Count -ne 1 -or [string]$RunNames[0] -cne $ExpectedRunId -or
        [int]$Prior.run_file_count -ne 48 -or
        [string]$Prior.run_inventory_sha256 -cne 'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b' -or
        [string]$Prior.historical_preservation_sha256 -cne '927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' -or
        [string]$Prior.released_lease_sha256 -cne '146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322' -or
        [string]$Prior.release_record_sha256 -cne '35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060' -or
        $ClosurePaths.Count -ne 0 -or
        $ImageTags.Count -ne 1 -or [string]$ImageTags[0] -cne $ExpectedImageTag -or
        [string]$Prior.image_id -cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5' -or
        $LeaseNames.Count -ne 2 -or
        [string]$LeaseNames[0] -cne "$ExpectedRunId.release.json" -or
        [string]$LeaseNames[1] -cne "$ExpectedRunId.released" -or
        $Prior.links_absent -cne $true
    ) { throw 'A11 prior A11 attempt drifted' }
    if (
        [int]$Evidence.historical_file_count -ne 64306 -or
        [int]$Evidence.historical_image_count -ne 21 -or
        [string]$Evidence.historical_file_inventory_sha256 -cne 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95' -or
        [string]$Evidence.historical_image_inventory_sha256 -cne '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f' -or
        $Evidence.historical_preserved -cne $true
    ) { throw 'A11 historical preservation preflight failed' }
    return $Evidence
}

function Confirm-A11ProtectedGit {
    param(
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$Branch
    )
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $Listing = @(& git -C $Worktree worktree list --porcelain)
    $CanonicalLine = $Listing | Where-Object { $_ -like 'worktree *' } |
        Select-Object -First 1
    if ($null -eq $CanonicalLine) { throw 'A11 canonical worktree is unavailable' }
    $Canonical = $CanonicalLine.Substring(9)
    if (
        (& git -C $Worktree rev-parse HEAD).Trim() -cne $SourceCommit -or
        (& git -C $Worktree branch --show-current).Trim() -cne $Branch -or
        (& git -C $Worktree rev-parse "$PlanCommit^").Trim() -cne $SpecCommit -or
        @(& git -C $Worktree status --porcelain=v1).Count -ne 0 -or
        @(& git -C $Canonical status --porcelain=v1).Count -ne 0
    ) { throw 'A11 protected Git identity changed during campaign' }
    return $true
}

function New-A11PhaseIdentity {
    param(
        [Parameter(Mandatory = $true)][ValidateSet('calibration', 'validation')][string]$Phase,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId,
        [Parameter(Mandatory = $true)][string]$ArtifactRoot,
        [string]$TimestampToken = ([DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')),
        [string]$Nonce = ([Guid]::NewGuid().ToString('N').Substring(0, 8))
    )
    if (
        $TimestampToken -cnotmatch '^[0-9]{8}T[0-9]{9}Z$' -or
        $Nonce -cnotmatch '^[0-9a-f]{8}$'
    ) { throw 'A11 phase identity token is malformed' }
    $RunId = "wave0-a11-$Phase-$TimestampToken-$Nonce"
    $Root = [IO.Path]::GetFullPath([IO.Path]::Combine($ArtifactRoot, 'a11-runs', $RunId))
    return [pscustomobject][ordered]@{
        phase = $Phase
        run_id = $RunId
        image_tag = "vision-active-learning-loop:wave0-a11-$Phase-$($SourceCommit.Substring(0, 12))-$TimestampToken-$Nonce"
        image_id = $null
        campaign_root = $Root
        cache_root = [IO.Path]::Combine($Root, 'wave0', 'model_cache')
        lease_id = "wave0-a11-$Phase-lease-$TimestampToken-$Nonce"
        lease_lock_path = [IO.Path]::Combine($ArtifactRoot, 'leases', 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63.json')
        lease_path = [IO.Path]::Combine($Root, 'audit', 'active-lease.json')
        source_commit = $SourceCommit
        specification_commit = $SpecCommit
        plan_commit = $PlanCommit
        owner_authorization_id = $OwnerAuthorizationId
        replica_records = [Collections.Generic.List[object]]::new()
        audit_records = [ordered]@{}
        foundation_receipts = [ordered]@{}
        cache_inventory_sha256 = $null
        gpu_driver = $null
        lease_acquired = $false
        release = $null
        aggregate_receipt = $null
        current_stage = 'preregistered'
        terminal = $null
    }
}

function Test-A11PathEntryPresent {
    param([Parameter(Mandatory = $true)][string]$Path)
    $FullPath = [IO.Path]::GetFullPath($Path)
    $Parent = [IO.Path]::GetDirectoryName($FullPath)
    if ([string]::IsNullOrWhiteSpace($Parent)) {
        throw "A11 destination path has no parent: $Path"
    }
    $Name = [IO.Path]::GetFileName($FullPath)
    try {
        $Entries = @([IO.DirectoryInfo]::new($Parent).EnumerateFileSystemInfos() |
            Where-Object { $_.Name.Equals($Name, [StringComparison]::OrdinalIgnoreCase) })
    } catch [IO.DirectoryNotFoundException] {
        return $false
    } catch [IO.FileNotFoundException] {
        return $false
    } catch {
        throw "A11 destination parent inspection failed: $Parent"
    }
    return $Entries.Count -ne 0
}

function Test-A11PhaseDestinationsAbsent {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateCount(2, 2)]
        [object[]]$Identities
    )
    if (
        [string]$Identities[0].phase -cne 'calibration' -or
        [string]$Identities[1].phase -cne 'validation'
    ) { throw 'A11 phase destination identities are not ordered' }
    foreach ($Name in @('run_id', 'image_tag', 'campaign_root', 'cache_root', 'lease_id', 'lease_path')) {
        if ([string]$Identities[0].$Name -ceq [string]$Identities[1].$Name) {
            throw "A11 phase runtime identity is reused: $Name"
        }
    }
    $Timestamps = [Collections.Generic.List[string]]::new()
    $Nonces = [Collections.Generic.List[string]]::new()
    foreach ($Identity in $Identities) {
        $Match = [regex]::Match(
            [string]$Identity.run_id,
            '^wave0-a11-(calibration|validation)-([0-9]{8}T[0-9]{9}Z)-([0-9a-f]{8})$'
        )
        if (-not $Match.Success) { throw 'A11 phase run identity is malformed' }
        [void]$Timestamps.Add($Match.Groups[2].Value)
        [void]$Nonces.Add($Match.Groups[3].Value)
    }
    if ($Timestamps[0] -ceq $Timestamps[1] -or $Nonces[0] -ceq $Nonces[1]) {
        throw 'A11 phase timestamp or nonce is reused'
    }

    $CheckedPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($Identity in $Identities) {
        $LeaseRoot = [IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path)
        $Paths = @(
            [string]$Identity.campaign_root,
            [string]$Identity.cache_root,
            [string]$Identity.lease_path,
            [string]$Identity.lease_lock_path,
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).released"),
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).release.json"),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'audit'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'receipts'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'checkpoints')
        )
        foreach ($Path in $Paths) {
            if (
                $CheckedPaths.Add([IO.Path]::GetFullPath($Path)) -and
                (Test-A11PathEntryPresent -Path $Path)
            ) {
                throw "A11 fresh runtime destination exists: $Path"
            }
        }
        $List = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
            'image', 'ls', '--filter', "reference=$($Identity.image_tag)",
            '--format', '{{.Repository}}:{{.Tag}}'
        )
        if ($List.ExitCode -ne 0 -or $List.Stderr -cne '') {
            throw "A11 image destination inspection failed: $($Identity.image_tag)"
        }
        $Tags = @($List.Stdout -split "`r?`n" | Where-Object {
            -not [string]::IsNullOrWhiteSpace($_)
        })
        if ($Tags.Count -ne 0) { throw "A11 image tag exists: $($Identity.image_tag)" }
    }
    return $true
}

function New-A11BuildArguments {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$BaseDigest
    )
    if ($BaseDigest -cnotmatch '^sha256:[0-9a-f]{64}$') { throw 'A11 base digest is invalid' }
    return @(
        'build', '--no-cache', '--progress', 'plain', '--file', 'docker/wave0.Dockerfile',
        '--label', "org.opencontainers.image.revision=$($Identity.source_commit)",
        '--label', "org.opencontainers.image.val.run_id=$($Identity.run_id)",
        '--label', "org.opencontainers.image.val.spec_commit=$($Identity.specification_commit)",
        '--label', "org.opencontainers.image.val.plan_commit=$($Identity.plan_commit)",
        '--label', "org.opencontainers.image.base.digest=$BaseDigest",
        '--tag', [string]$Identity.image_tag, '.'
    )
}

function New-A11CachePreflightArguments {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Worktree
    )
    $ContainerRoot = "/a11/$($Identity.phase)"
    return @(
        'run', '--rm', '--network', 'bridge', '--workdir', '/workspace',
        '--entrypoint', 'val',
        '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'HF_HUB_DISABLE_PROGRESS_BARS=1',
        '-e', 'HF_HUB_VERBOSITY=error',
        '-e', "VAL_ARTIFACT_ROOT=$ContainerRoot",
        '-e', "VAL_RUNTIME_IMAGE_DIGEST=$($Identity.image_id)",
        '-e', 'VAL_OBSERVED_BASE_IMAGE_DIGEST=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356',
        '-v', "${Worktree}:/workspace:ro",
        '-v', "$($Identity.campaign_root):${ContainerRoot}:rw",
        [string]$Identity.image_id,
        'assets', 'verify', '--config', '/workspace/configs/models/pinned-models.yaml',
        '--cache-root', "$ContainerRoot/wave0/model_cache",
        '--output', "$ContainerRoot/wave0/receipts/cache-preflight-model-assets.json",
        '--run-id', [string]$Identity.run_id, '--download'
    )
}

function Get-A11CacheInventorySha256 {
    param([Parameter(Mandatory = $true)][string]$CacheRoot)
    $Linked = @(Get-ChildItem -LiteralPath $CacheRoot -Recurse -Force |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($Linked.Count -ne 0) { throw 'A11 model cache contains a link' }
    $Files = @(
        Get-ChildItem -LiteralPath $CacheRoot -File -Recurse -Force |
            Sort-Object FullName -CaseSensitive
    )
    if ($Files.Count -eq 0) { throw 'A11 model cache is empty' }
    $Records = @($Files | ForEach-Object {
        if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'A11 model cache contains a link' }
        $Relative = $_.FullName.Substring($CacheRoot.Length + 1).Replace('\', '/')
        if (
            $Relative.EndsWith('.metadata', [StringComparison]::Ordinal) -and
            "/$Relative".Contains('/.cache/huggingface/download/', [StringComparison]::Ordinal)
        ) {
            # Bind the stable commit/ETag lines; the third line is download time.
            $Lines = [IO.File]::ReadAllLines($_.FullName, [Text.Encoding]::UTF8)
            $Timestamp = 0.0
            if (
                $Lines.Count -ne 3 -or
                -not [double]::TryParse(
                    $Lines[2], [Globalization.NumberStyles]::Float,
                    [Globalization.CultureInfo]::InvariantCulture, [ref]$Timestamp
                ) -or -not [double]::IsFinite($Timestamp) -or $Timestamp -le 0.0
            ) { throw 'A11 model cache metadata is invalid' }
            $Normalized = [Text.Encoding]::UTF8.GetBytes("$($Lines[0])`n$($Lines[1])`n")
            $Size = [long]$Normalized.Length
            $Digest = [Convert]::ToHexString(
                [Security.Cryptography.SHA256]::HashData($Normalized)
            ).ToLowerInvariant()
        } else {
            $Size = [long]$_.Length
            $Digest = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        [ordered]@{
            path = $Relative
            sha256 = $Digest
            size = $Size
        }
    })
    $Json = ([ordered]@{ files = $Records } | ConvertTo-Json -Depth 6 -Compress)
    $Bytes = [Text.Encoding]::UTF8.GetBytes($Json)
    return [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}

function Invoke-A11CachePreflight {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [string]$Worktree = ([IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))),
        [string]$DockerExecutable = 'docker',
        [string[]]$DockerPrefixArguments = @()
    )
    $Arguments = New-A11CachePreflightArguments -Identity $Identity -Worktree $Worktree
    $Result = Invoke-A11Native -FilePath $DockerExecutable -ArgumentList @($DockerPrefixArguments + $Arguments)
    $AuditRoot = [IO.Path]::Combine($Identity.campaign_root, 'audit')
    $StdoutPath = [IO.Path]::Combine($AuditRoot, '20-cache-preflight.stdout.log')
    $StderrPath = [IO.Path]::Combine($AuditRoot, '20-cache-preflight.stderr.log')
    Write-A11NewText -Path $StdoutPath -Text $Result.Stdout
    Write-A11NewText -Path $StderrPath -Text $Result.Stderr
    $Succeeded = (
        $Result.ExitCode -eq 0 -and $Result.Stdout -ceq "PASS`n" -and
        $Result.Stderr -ceq ''
    )
    $InventorySha256 = if ($Succeeded) {
        Get-A11CacheInventorySha256 -CacheRoot $Identity.cache_root
    } else { $null }
    $Audit = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        docker_argv = @('docker') + $Arguments
        exit_code = [int]$Result.ExitCode
        network = 'bridge'
        gpu_enabled = $false
        stdout = Get-A11FileRecord -Path $StdoutPath
        stderr = Get-A11FileRecord -Path $StderrPath
        cache_root = $Identity.cache_root
        inventory_sha256 = $InventorySha256
    }
    $AuditPath = [IO.Path]::Combine($AuditRoot, '20-cache-preflight.json')
    Write-A11NewText -Path $AuditPath -Text (($Audit | ConvertTo-Json -Depth 12 -Compress) + "`n")
    $Identity.audit_records.cache_inventory = Get-A11FileRecord -Path $AuditPath
    if (-not $Succeeded) { throw 'A11 model-cache preflight process contract failed' }
    $Identity.cache_inventory_sha256 = [string]$Audit.inventory_sha256
    return $Audit
}

function New-A11ReplicaValArguments {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$ReplicaId
    )
    $ContainerRoot = "/a11/$($Identity.phase)"
    return @(
        'probe', 'training-feasibility',
        '--model-contract', "$ContainerRoot/wave0/receipts/model-contract.json",
        '--checkpoint-root', "$ContainerRoot/wave0/checkpoints/$ReplicaId",
        '--run-id', [string]$Identity.run_id,
        '--output', "$ContainerRoot/wave0/receipts/$ReplicaId.json"
    )
}

function New-A11ReplicaArguments {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Worktree,
        [Parameter(Mandatory = $true)][string]$ReplicaId,
        [Parameter(Mandatory = $true)][string]$ModelContractPath,
        [Parameter(Mandatory = $true)][string]$ReceiptPath,
        [Parameter(Mandatory = $true)][string]$CheckpointRoot
    )
    $ExpectedModelContract = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'receipts', 'model-contract.json')
    $ExpectedReceipt = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'receipts', "$ReplicaId.json")
    $ExpectedCheckpoint = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'checkpoints', $ReplicaId)
    if (
        [IO.Path]::GetFullPath($ModelContractPath) -cne [IO.Path]::GetFullPath($ExpectedModelContract) -or
        [IO.Path]::GetFullPath($ReceiptPath) -cne [IO.Path]::GetFullPath($ExpectedReceipt) -or
        [IO.Path]::GetFullPath($CheckpointRoot) -cne [IO.Path]::GetFullPath($ExpectedCheckpoint)
    ) { throw 'A11 replica host path binding mismatch' }
    $ContainerRoot = "/a11/$($Identity.phase)"
    $CidFile = [IO.Path]::Combine($Identity.campaign_root, 'audit', "$ReplicaId.cid")
    return @(
        'run', '--rm', '--gpus', 'all', '--network', 'none', '--workdir', '/workspace',
        '--cidfile', $CidFile, '--entrypoint', 'val',
        '-e', 'PYTHONPATH=/workspace/src', '-e', 'HF_HUB_OFFLINE=1',
        '-e', 'TRANSFORMERS_OFFLINE=1', '-e', "VAL_ARTIFACT_ROOT=$ContainerRoot",
        '-e', "VAL_RUNTIME_IMAGE_DIGEST=$($Identity.image_id)",
        '-e', 'VAL_OBSERVED_BASE_IMAGE_DIGEST=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8',
        '-v', "${Worktree}:/workspace:ro",
        '-v', "$($Identity.campaign_root):${ContainerRoot}:rw",
        '-v', "$($Identity.cache_root):$ContainerRoot/wave0/model_cache:ro",
        [string]$Identity.image_id
    ) + (New-A11ReplicaValArguments -Identity $Identity -ReplicaId $ReplicaId)
}

function New-A11Lease {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$GpuUuid,
        [Parameter(Mandatory = $true)][string]$LeasePath
    )
    if ($GpuUuid -cne 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63') {
        throw 'A11 lease GPU identity mismatch'
    }
    $Parent = Get-Item -LiteralPath ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($LeasePath))) -Force
    if (-not $Parent.PSIsContainer -or ($Parent.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'A11 lease root must be an existing non-link directory'
    }
    $Document = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        lease_id = $Identity.lease_id
        run_id = $Identity.run_id
        source_commit = $Identity.source_commit
        image_tag = $Identity.image_tag
        image_id = $Identity.image_id
        campaign_root = $Identity.campaign_root
        cache_root = $Identity.cache_root
        cache_inventory_sha256 = if ($null -ne $Identity.PSObject.Properties['cache_inventory_sha256']) {
            [string]$Identity.cache_inventory_sha256
        } else { '' }
        audit_bindings = if ($null -ne $Identity.PSObject.Properties['audit_records']) {
            [ordered]@{
                identity = $Identity.audit_records.identity
                image_inspect = $Identity.audit_records.image_inspect
                cache_inventory = $Identity.audit_records.cache_inventory
                gpu_preflight = $Identity.audit_records.gpu_preflight
            }
        } else { [ordered]@{} }
        gpu_uuid = $GpuUuid
        acquired_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A11NewText -Path $LeasePath -Text (($Document | ConvertTo-Json -Depth 12 -Compress) + "`n")
    if ($null -eq $Identity.PSObject.Properties['lease_acquired']) {
        $Identity | Add-Member -NotePropertyName lease_acquired -NotePropertyValue $true
    } else {
        $Identity.lease_acquired = $true
    }
    $EvidencePath = if ($null -ne $Identity.PSObject.Properties['lease_path']) {
        [string]$Identity.lease_path
    } else { $LeasePath }
    if ([IO.Path]::GetFullPath($EvidencePath) -cne [IO.Path]::GetFullPath($LeasePath)) {
        $ContainerRoot = "/a11/$($Identity.phase)"
        $EvidenceDocument = [ordered]@{
            schema_version = 1
            phase = $Identity.phase
            lease_id = $Identity.lease_id
            run_id = $Identity.run_id
            source_commit = $Identity.source_commit
            image_tag = $Identity.image_tag
            image_id = $Identity.image_id
            campaign_root = $ContainerRoot
            cache_root = "$ContainerRoot/wave0/model_cache"
            cache_inventory_sha256 = $Identity.cache_inventory_sha256
            audit_bindings = [ordered]@{
                identity = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.identity
                image_inspect = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.image_inspect
                cache_inventory = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.cache_inventory
                gpu_preflight = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.gpu_preflight
            }
            gpu_uuid = $GpuUuid
            acquired_at = $Document.acquired_at
        }
        Write-A11NewText -Path $EvidencePath -Text (($EvidenceDocument | ConvertTo-Json -Depth 12 -Compress) + "`n")
    }
    $Stored = Get-Content -Raw -LiteralPath $LeasePath | ConvertFrom-Json
    if ([string]$Stored.lease_id -cne [string]$Identity.lease_id) { throw 'A11 lease parseback mismatch' }
    return Get-A11FileRecord -Path $EvidencePath
}

function Release-A11Lease {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [string]$ActivePath = [string]$Identity.lease_lock_path,
        [string]$ReleasedPath = ([IO.Path]::Combine([IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path), "$($Identity.run_id).released")),
        [string]$RecordPath = ([IO.Path]::Combine([IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path), "$($Identity.run_id).release.json"))
    )
    if (-not (Test-Path -LiteralPath $ActivePath -PathType Leaf)) { throw 'A11 active lease is missing' }
    $LeaseHash = (Get-FileHash -LiteralPath $ActivePath -Algorithm SHA256).Hash.ToLowerInvariant()
    [IO.File]::Move($ActivePath, $ReleasedPath)
    $Document = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        run_id = $Identity.run_id
        source_commit = $Identity.source_commit
        image_id = $Identity.image_id
        released_at = [DateTimeOffset]::UtcNow.ToString('o')
        original_lease_sha256 = $LeaseHash
    }
    Write-A11NewText -Path $RecordPath -Text (($Document | ConvertTo-Json -Compress) + "`n")
    if ($null -eq $Identity.PSObject.Properties['lease_acquired']) {
        $Identity | Add-Member -NotePropertyName lease_acquired -NotePropertyValue $false
    } else {
        $Identity.lease_acquired = $false
    }
    $Result = [pscustomobject][ordered]@{
        released = Get-A11FileRecord -Path $ReleasedPath
        release_record = Get-A11FileRecord -Path $RecordPath
    }
    if ($null -ne $Identity.PSObject.Properties['release']) {
        $Identity.release = $Result
    } else {
        $Identity | Add-Member -NotePropertyName release -NotePropertyValue $Result
    }
    return $Result
}

function Confirm-A11Release {
    param([Parameter(Mandatory = $true)][object]$Identity)
    if ($null -eq $Identity.release) { throw 'A11 lease release evidence is missing' }
    foreach ($Name in @('released', 'release_record')) {
        $Expected = $Identity.release.$Name
        $Observed = Get-A11FileRecord -Path ([string]$Expected.path)
        if (
            [string]$Observed.path -cne [string]$Expected.path -or
            [long]$Observed.size -ne [long]$Expected.size -or
            [string]$Observed.sha256 -cne [string]$Expected.sha256
        ) { throw "A11 lease release record changed: $Name" }
    }
    $Release = Get-Content -Raw -LiteralPath $Identity.release.release_record.path |
        ConvertFrom-Json
    if (
        [string]$Release.run_id -cne [string]$Identity.run_id -or
        [string]$Release.source_commit -cne [string]$Identity.source_commit -or
        [string]$Release.image_id -cne [string]$Identity.image_id -or
        [string]$Release.original_lease_sha256 -cnotmatch '^[0-9a-f]{64}$'
    ) { throw 'A11 lease release binding mismatch' }
    return $true
}

function Initialize-A11Phase {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][object]$Peer
    )
    $CampaignParent = [IO.Path]::GetDirectoryName([string]$Identity.campaign_root)
    if (Test-Path -LiteralPath $CampaignParent) {
        $ParentItem = Get-Item -LiteralPath $CampaignParent -Force -ErrorAction Stop
        if (
            -not $ParentItem.PSIsContainer -or
            ($ParentItem.Attributes -band [IO.FileAttributes]::ReparsePoint)
        ) {
            throw 'A11 campaign parent is not a non-link directory'
        }
    } elseif ($Identity.phase -ceq 'calibration') {
        New-Item -ItemType Directory -Path $CampaignParent -ErrorAction Stop | Out-Null
    } else {
        throw 'A11 validation campaign parent is missing'
    }
    $Root = New-Item -ItemType Directory -Path $Identity.campaign_root -ErrorAction Stop
    New-Item -ItemType Directory -Path ([IO.Path]::Combine($Root.FullName, 'audit')) -ErrorAction Stop | Out-Null
    $WaveRoot = New-Item -ItemType Directory -Path ([IO.Path]::Combine($Root.FullName, 'wave0')) -ErrorAction Stop
    foreach ($Name in @('receipts', 'checkpoints', 'model_cache')) {
        New-Item -ItemType Directory -Path ([IO.Path]::Combine($WaveRoot.FullName, $Name)) -ErrorAction Stop | Out-Null
    }
    $IdentityAudit = [ordered]@{
        schema_version = 1
        static = [ordered]@{
            source_commit = $Identity.source_commit
            specification_commit = $Identity.specification_commit
            plan_commit = $Identity.plan_commit
            base_image_digest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
        }
        current = $Identity
        preregistered_peer = $Peer
    }
    $AuditPath = [IO.Path]::Combine($Root.FullName, 'audit', '00-identity.json')
    Write-A11NewText -Path $AuditPath -Text (($IdentityAudit | ConvertTo-Json -Depth 8 -Compress) + "`n")
    $Identity.audit_records.identity = Get-A11FileRecord -Path $AuditPath
    $GpuPath = [IO.Path]::Combine($Root.FullName, 'audit', '01-gpu-preflight.json')
    $GpuIdentityRows = @(& nvidia-smi `
        --query-gpu=name,uuid,driver_version --format=csv,noheader,nounits)
    if ($GpuIdentityRows.Count -ne 1) { throw 'A11 phase GPU inventory mismatch' }
    $GpuParts = $GpuIdentityRows[0].Split(',', 3)
    $ComputeCsv = (& nvidia-smi `
        --query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory `
        --format=csv,noheader,nounits) -join "`n"
    $GpuRows = if ($GpuParts.Count -eq 3) {
        @(ConvertTo-A11GpuRows `
            -GpuCsv "$($GpuParts[0]),$($GpuParts[1])" -ComputeCsv $ComputeCsv)
    } else { @() }
    if (
        $GpuParts.Count -ne 3 -or $GpuRows.Count -ne 1 -or
        [string]$GpuRows[0].name -cne 'NVIDIA GeForce RTX 4090' -or
        [string]$GpuRows[0].uuid -cne 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63' -or
        [int]$GpuRows[0].compute_process_count -ne 0
    ) { throw 'A11 phase requires the idle registered RTX 4090' }
    $Identity.gpu_driver = $GpuParts[2].Trim()
    Write-A11NewText -Path $GpuPath -Text (([ordered]@{
        name = 'NVIDIA GeForce RTX 4090'
        uuid = 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63'
        driver = $Identity.gpu_driver
        cuda_runtime = '12.6'
    } | ConvertTo-Json -Compress) + "`n")
    $Identity.audit_records.gpu_preflight = Get-A11FileRecord -Path $GpuPath
}

function Invoke-A11Build {
    param([Parameter(Mandatory = $true)][object]$Identity)
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $Arguments = New-A11BuildArguments -Identity $Identity -BaseDigest 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    $Result = Invoke-A11Native -FilePath 'docker' -ArgumentList $Arguments -WorkingDirectory $Worktree
    $Identity.audit_records.build = Write-A11ProcessAudit $Identity '10-build' (@('docker') + $Arguments) $Result
    if ($Result.ExitCode -ne 0) { throw 'A11 image build failed' }
    $Inspect = Invoke-A11Native -FilePath 'docker' -ArgumentList @('image', 'inspect', [string]$Identity.image_tag)
    $Identity.audit_records.image_inspect = Write-A11ProcessAudit $Identity '11-image-inspect' `
        @('docker', 'image', 'inspect', [string]$Identity.image_tag) $Inspect
    if ($Inspect.ExitCode -ne 0) { throw 'A11 image inspect failed' }
    $Values = @($Inspect.Stdout | ConvertFrom-Json)
    if ($Values.Count -ne 1 -or [string]$Values[0].Id -cnotmatch '^sha256:[0-9a-f]{64}$') {
        throw 'A11 image inspect identity is invalid'
    }
    $Labels = $Values[0].Config.Labels
    $ExpectedLabels = [ordered]@{
        'org.opencontainers.image.revision' = [string]$Identity.source_commit
        'org.opencontainers.image.val.run_id' = [string]$Identity.run_id
        'org.opencontainers.image.val.spec_commit' = [string]$Identity.specification_commit
        'org.opencontainers.image.val.plan_commit' = [string]$Identity.plan_commit
        'org.opencontainers.image.base.digest' = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    }
    foreach ($Name in $ExpectedLabels.Keys) {
        if ([string]$Labels.$Name -cne [string]$ExpectedLabels[$Name]) {
            throw "A11 image label binding mismatch: $Name"
        }
    }
    $Identity.image_id = [string]$Values[0].Id
}

function Invoke-A11DockerStage {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string[]]$Command,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$ExpectedStdout,
        [Parameter(Mandatory = $true)][string]$ReceiptPath
    )
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $ContainerRoot = "/a11/$($Identity.phase)"
    $Arguments = @(
        'run', '--rm', '--gpus', 'all', '--network', 'none', '--workdir', '/workspace',
        '--entrypoint', 'val', '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'HF_HUB_OFFLINE=1', '-e', 'TRANSFORMERS_OFFLINE=1',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8',
        '-e', "VAL_ARTIFACT_ROOT=$ContainerRoot", '-e', "VAL_RUNTIME_IMAGE_DIGEST=$($Identity.image_id)",
        '-e', 'VAL_OBSERVED_BASE_IMAGE_DIGEST=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356',
        '-v', "${Worktree}:/workspace:ro",
        '-v', "$($Identity.campaign_root):${ContainerRoot}:rw",
        '-v', "$($Identity.cache_root):$ContainerRoot/wave0/model_cache:ro",
        [string]$Identity.image_id
    ) + $Command
    $Result = Invoke-A11Native -FilePath 'docker' -ArgumentList $Arguments
    $StreamsSucceeded = (
        $Result.ExitCode -eq 0 -and $Result.Stdout -ceq $ExpectedStdout -and
        $Result.Stderr -ceq ''
    )
    $ReceiptRecord = $null
    $ReceiptFailure = $null
    if ($StreamsSucceeded) {
        try {
            $ReceiptRecord = Get-A11VerifiedStageReceipt -Identity $Identity -Path $ReceiptPath
        } catch {
            $ReceiptFailure = $_
        }
    }
    $Identity.audit_records[$Name] = Write-A11ProcessAudit `
        -Identity $Identity -Name $Name -Argv (@('docker') + $Arguments) `
        -Result $Result -ReceiptRecord $ReceiptRecord
    if (-not $StreamsSucceeded) { throw "A11 stage failed: $Name" }
    if ($null -ne $ReceiptFailure) { throw $ReceiptFailure.Exception }
    return $ReceiptRecord
}

function Invoke-A11Foundation {
    param([Parameter(Mandatory = $true)][object]$Identity)
    $ReceiptRoot = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'receipts')
    $EnvironmentPath = [IO.Path]::Combine($ReceiptRoot, 'environment.json')
    $AssetsPath = [IO.Path]::Combine($ReceiptRoot, 'model-assets.json')
    $ModelContractPath = [IO.Path]::Combine($ReceiptRoot, 'model-contract.json')
    $EnvironmentRecord = Invoke-A11DockerStage `
        -Identity $Identity -Name '30-environment' -Command @(
        'environment', 'check', '--config', '/workspace/configs/environment/wave0.yaml',
        '--run-id', $Identity.run_id,
        '--output', "/a11/$($Identity.phase)/wave0/receipts/environment.json"
    ) -ExpectedStdout '' -ReceiptPath $EnvironmentPath
    $Identity.foundation_receipts['environment'] = $EnvironmentRecord
    $AssetsRecord = Invoke-A11DockerStage `
        -Identity $Identity -Name '31-model-assets' -Command @(
        'assets', 'verify', '--config', '/workspace/configs/models/pinned-models.yaml',
        '--cache-root', "/a11/$($Identity.phase)/wave0/model_cache",
        '--output', "/a11/$($Identity.phase)/wave0/receipts/model-assets.json",
        '--run-id', $Identity.run_id
    ) -ExpectedStdout "PASS`n" -ReceiptPath $AssetsPath
    $Identity.foundation_receipts['model_assets'] = $AssetsRecord
    Assert-A11FileRecordUnchanged -Identity $Identity -Expected $EnvironmentRecord `
        -Path $EnvironmentPath | Out-Null
    Assert-A11FileRecordUnchanged -Identity $Identity -Expected $AssetsRecord `
        -Path $AssetsPath | Out-Null
    $ModelContractRecord = Invoke-A11DockerStage `
        -Identity $Identity -Name '32-model-contract' -Command @(
        'probe', 'model-contract',
        '--assets', "/a11/$($Identity.phase)/wave0/receipts/model-assets.json",
        '--environment', "/a11/$($Identity.phase)/wave0/receipts/environment.json",
        '--fixtures',
        '/workspace/fixtures/synthetic/wave0/fixture-manifest.json', '--run-id',
        $Identity.run_id,
        '--output', "/a11/$($Identity.phase)/wave0/receipts/model-contract.json"
    ) -ExpectedStdout "PASS`n" -ReceiptPath $ModelContractPath
    $Identity.foundation_receipts['model_contract'] = $ModelContractRecord
}

function Invoke-A11Replica {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$ReplicaId
    )
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $ReceiptPath = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'receipts', "$ReplicaId.json")
    $CheckpointRoot = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'checkpoints', $ReplicaId)
    $ModelContract = [IO.Path]::Combine($Identity.campaign_root, 'wave0', 'receipts', 'model-contract.json')
    if (
        [IO.File]::Exists($ReceiptPath) -or [IO.Directory]::Exists($ReceiptPath) -or
        [IO.File]::Exists($CheckpointRoot) -or [IO.Directory]::Exists($CheckpointRoot)
    ) { throw "A11 replica destinations must be absent: $ReplicaId" }
    Assert-A11FileRecordUnchanged `
        -Identity $Identity -Expected $Identity.foundation_receipts.model_contract `
        -Path $ModelContract | Out-Null
    $Arguments = New-A11ReplicaArguments $Identity $Worktree $ReplicaId $ModelContract $ReceiptPath $CheckpointRoot
    $Result = Invoke-A11Native -FilePath 'docker' -ArgumentList $Arguments
    $AuditRoot = [IO.Path]::Combine($Identity.campaign_root, 'audit')
    $StdoutPath = [IO.Path]::Combine($AuditRoot, "$ReplicaId.stdout.log")
    $StderrPath = [IO.Path]::Combine($AuditRoot, "$ReplicaId.stderr.log")
    Write-A11NewText -Path $StdoutPath -Text $Result.Stdout
    Write-A11NewText -Path $StderrPath -Text $Result.Stderr
    $ValArguments = New-A11ReplicaValArguments -Identity $Identity -ReplicaId $ReplicaId
    $Invocation = [ordered]@{
        schema_version = 1
        argv = @('val') + $ValArguments
        exit_code = [int]$Result.ExitCode
        stdout = Get-A11FileRecord -Path $StdoutPath
        stderr = Get-A11FileRecord -Path $StderrPath
    }
    $InvocationPath = [IO.Path]::Combine($AuditRoot, "$ReplicaId-invocation.json")
    Write-A11NewText -Path $InvocationPath -Text (($Invocation | ConvertTo-Json -Depth 8 -Compress) + "`n")
    if (
        $Result.ExitCode -ne 0 -or $Result.Stdout -cne "PASS`n" -or
        -not [string]::IsNullOrEmpty($Result.Stderr)
    ) { throw "A11 replica failed: $ReplicaId" }
    $Checkpoint = @(Get-ChildItem -LiteralPath $CheckpointRoot -File -Recurse)
    if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf) -or $Checkpoint.Count -ne 1) {
        throw "A11 replica outputs incomplete: $ReplicaId"
    }
    $CidPath = [IO.Path]::Combine($AuditRoot, "$ReplicaId.cid")
    $ContainerId = (Get-Content -Raw -LiteralPath $CidPath).Trim()
    if ($ContainerId -cnotmatch '^[0-9a-f]{64}$') { throw 'A11 container ID is invalid' }
    $Receipt = Get-Content -Raw -LiteralPath $ReceiptPath | ConvertFrom-Json
    $Timestamp = [string]$Receipt.metadata.timestamp
    if ([string]::IsNullOrWhiteSpace($Timestamp)) { throw 'A11 replica timestamp is missing' }
    $Identity.replica_records.Add([ordered]@{
        replica_id = $ReplicaId
        container_id = $ContainerId
        timestamp = $Timestamp
        invocation_audit = Get-A11FileRecord -Path $InvocationPath
        feasibility = Get-A11FileRecord -Path $ReceiptPath
        checkpoint = Get-A11FileRecord -Path $Checkpoint[0].FullName
    })
}

function ConvertTo-A11ContainerFileRecord {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][object]$Record
    )
    $HostPath = [IO.Path]::GetFullPath([string]$Record.path)
    $Relative = [IO.Path]::GetRelativePath(
        [string]$Identity.campaign_root, $HostPath
    ).Replace('\', '/')
    if ($Relative -eq '..' -or $Relative.StartsWith('../')) {
        throw 'A11 file record escapes the campaign root'
    }
    return [ordered]@{
        path = "/a11/$($Identity.phase)/$Relative"
        size = [long]$Record.size
        sha256 = [string]$Record.sha256
    }
}

function New-A11PhaseManifest {
    param([Parameter(Mandatory = $true)][object]$Identity)
    $AuditRoot = [IO.Path]::Combine($Identity.campaign_root, 'audit')
    $HistoryPath = [IO.Path]::Combine($AuditRoot, '60-historical-preservation.json')
    $ArtifactRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName([string]$Identity.campaign_root))
    $Historical = Get-A11HistoricalArtifactInventory -ArtifactRoot $ArtifactRoot
    $Images = Get-A11HistoricalImageInventory
    $Preserved = (
        @($Historical.records).Count -eq 64306 -and
        @($Images.records).Count -eq 21 -and
        $Historical.sha256 -ceq 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95' -and
        $Images.sha256 -ceq '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f'
    )
    if (-not $Preserved) { throw 'A11 historical preservation rehash failed' }
    Write-A11NewText -Path $HistoryPath -Text (([ordered]@{
        schema_version = 1
        historical_file_count = @($Historical.records).Count
        historical_image_count = @($Images.records).Count
        historical_file_inventory_sha256 = $Historical.sha256
        historical_image_inventory_sha256 = $Images.sha256
        preserved = $Preserved
    } | ConvertTo-Json -Compress) + "`n")
    $LeaseRecord = Get-A11FileRecord -Path $Identity.lease_path
    $Lease = Get-Content -Raw -LiteralPath $Identity.lease_path | ConvertFrom-Json
    $Manifest = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        run_id = $Identity.run_id
        campaign_root = "/a11/$($Identity.phase)"
        source_commit = $Identity.source_commit
        specification_commit = $Identity.specification_commit
        plan_commit = $Identity.plan_commit
        image_tag = $Identity.image_tag
        image_id = $Identity.image_id
        base_image_digest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
        owner_authorization_id = $Identity.owner_authorization_id
        model_cache = [ordered]@{
            path = "/a11/$($Identity.phase)/wave0/model_cache"
            inventory_sha256 = Get-A11CacheInventorySha256 -CacheRoot $Identity.cache_root
        }
        gpu = [ordered]@{
            name = 'NVIDIA GeForce RTX 4090'
            uuid = 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63'
            driver = $Identity.gpu_driver
            cuda_runtime = '12.6'
        }
        lease = [ordered]@{
            lease_id = $Lease.lease_id
            path = (ConvertTo-A11ContainerFileRecord $Identity $LeaseRecord).path
            size = $LeaseRecord.size
            sha256 = $LeaseRecord.sha256
        }
        historical_preservation = ConvertTo-A11ContainerFileRecord $Identity `
            (Get-A11FileRecord -Path $HistoryPath)
        audits = [ordered]@{
            identity = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.identity
            image_inspect = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.image_inspect
            cache_inventory = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.cache_inventory
            gpu_preflight = ConvertTo-A11ContainerFileRecord $Identity $Identity.audit_records.gpu_preflight
        }
        replicas = @($Identity.replica_records | ForEach-Object {
            [ordered]@{
                replica_id = $_.replica_id
                container_id = $_.container_id
                timestamp = $_.timestamp
                invocation_audit = ConvertTo-A11ContainerFileRecord $Identity $_.invocation_audit
                feasibility = ConvertTo-A11ContainerFileRecord $Identity $_.feasibility
                checkpoint = ConvertTo-A11ContainerFileRecord $Identity $_.checkpoint
            }
        })
    }
    $Path = [IO.Path]::Combine($AuditRoot, '70-phase-manifest.json')
    Write-A11NewText -Path $Path -Text (($Manifest | ConvertTo-Json -Depth 16 -Compress) + "`n")
    return $Path
}

function New-A11GateArguments {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Worktree,
        [string]$CalibrationRoot = ''
    )
    $ContainerRoot = "/a11/$($Identity.phase)"
    $OutputName = "statistical-replay-$($Identity.phase).json"
    $Arguments = @(
        'run', '--rm', '--network', 'none', '--workdir', '/workspace', '--entrypoint', 'val',
        '-e', 'PYTHONPATH=/workspace/src', '-e', 'HF_HUB_OFFLINE=1',
        '-e', 'TRANSFORMERS_OFFLINE=1', '-v', "${Worktree}:/workspace:ro",
        '-v', "$($Identity.campaign_root):${ContainerRoot}:rw"
    )
    if ($Identity.phase -ceq 'calibration') {
        $Command = @(
            'gate', 'statistical-replay', 'calibrate',
            '--phase-manifest', "$ContainerRoot/audit/70-phase-manifest.json",
            '--phase-root', $ContainerRoot,
            '--output', "$ContainerRoot/wave0/receipts/$OutputName"
        )
    } else {
        if ([string]::IsNullOrWhiteSpace($CalibrationRoot)) {
            throw 'A11 calibration root is required for validation'
        }
        $Arguments += @('-v', "${CalibrationRoot}:/a11/calibration:ro")
        $Command = @(
            'gate', 'statistical-replay', 'validate',
            '--phase-manifest', "$ContainerRoot/audit/70-phase-manifest.json",
            '--phase-root', $ContainerRoot,
            '--calibration-receipt', '/a11/calibration/wave0/receipts/statistical-replay-calibration.json',
            '--output', "$ContainerRoot/wave0/receipts/$OutputName"
        )
    }
    return @($Arguments + @([string]$Identity.image_id) + $Command)
}

function Invoke-A11Gate {
    param([Parameter(Mandatory = $true)][object]$Identity)
    New-A11PhaseManifest -Identity $Identity | Out-Null
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $CalibrationRoot = if ($Identity.phase -ceq 'validation') {
        [IO.Path]::GetDirectoryName(
            [IO.Path]::GetDirectoryName(
                [IO.Path]::GetDirectoryName([string]$script:A11CalibrationReceipt)
            )
        )
    } else { '' }
    $Arguments = New-A11GateArguments -Identity $Identity -Worktree $Worktree `
        -CalibrationRoot $CalibrationRoot
    $Result = Invoke-A11Native -FilePath 'docker' -ArgumentList $Arguments
    $Identity.audit_records.gate = Write-A11ProcessAudit $Identity '71-aggregate-gate' `
        (@('docker') + $Arguments) $Result
    if ($Result.ExitCode -notin @(0, 2) -or -not [string]::IsNullOrEmpty($Result.Stderr)) {
        throw 'A11 aggregate gate process failed'
    }
    $Expected = if ($Identity.phase -ceq 'calibration') {
        'WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'
    } elseif ($Result.ExitCode -eq 0) {
        'WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED'
    } else { 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' }
    if ($Result.Stdout -cne "$Expected`n") { throw 'A11 aggregate terminal mismatch' }
    $Identity.terminal = $Expected
    if ($Identity.phase -ceq 'calibration') {
        $script:A11CalibrationReceipt = [IO.Path]::Combine(
            $Identity.campaign_root, 'wave0', 'receipts',
            'statistical-replay-calibration.json'
        )
    }
    return $Expected
}

function Assert-A11AggregateReceipt {
    param([Parameter(Mandatory = $true)][object]$Identity)
    $Path = [IO.Path]::Combine(
        $Identity.campaign_root, 'wave0', 'receipts',
        "statistical-replay-$($Identity.phase).json"
    )
    $Document = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    if ([string]$Document.normative.terminal -cne [string]$Identity.terminal) {
        throw 'A11 aggregate receipt terminal mismatch'
    }
    if ($Identity.phase -ceq 'calibration' -and [string]$Document.normative.status -cne 'RECORDED') {
        throw 'A11 calibration receipt is not recorded'
    }
    if ($Identity.phase -ceq 'validation') {
        $ExpectedStatus = if (
            [string]$Identity.terminal -ceq 'WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED'
        ) { 'PASS' } else { 'FAIL' }
        if ([string]$Document.normative.status -cne $ExpectedStatus) {
            throw 'A11 validation receipt status mismatch'
        }
    }
    $Record = Get-A11FileRecord -Path $Path
    $Identity.aggregate_receipt = $Record
    return $Record
}

function Confirm-A11CalibrationReceipt {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
    )
    if ($Identity.phase -cne 'calibration' -or $null -eq $Identity.aggregate_receipt) {
        throw 'A11 verified calibration receipt record is missing'
    }
    $ExpectedPath = [IO.Path]::Combine(
        $Identity.campaign_root, 'wave0', 'receipts',
        'statistical-replay-calibration.json'
    )
    $Expected = $Identity.aggregate_receipt
    $Observed = Get-A11FileRecord -Path $ExpectedPath
    if (
        [string]$Expected.path -cne [string]$Observed.path -or
        [long]$Expected.size -ne [long]$Observed.size -or
        [string]$Expected.sha256 -cne [string]$Observed.sha256
    ) { throw 'A11 verified calibration receipt changed before validation' }
    $Document = Get-Content -Raw -LiteralPath $ExpectedPath | ConvertFrom-Json
    if (
        [string]$Document.receipt_type -cne 'statistical-replay-calibration' -or
        [int]$Document.schema_version -ne 1 -or
        [string]$Document.normative.phase -cne 'calibration' -or
        [string]$Document.normative.status -cne 'RECORDED' -or
        @($Document.normative.errors).Count -ne 0 -or
        [string]$Document.normative.terminal -cne 'WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN' -or
        [string]$Document.normative.threshold_inventory_sha256 -cnotmatch '^[0-9a-f]{64}$' -or
        [string]$Document.metadata.run_id -cne [string]$Identity.run_id -or
        [string]$Document.metadata.source_commit -cne [string]$Identity.source_commit -or
        [string]$Document.metadata.specification_commit -cne [string]$Identity.specification_commit -or
        [string]$Document.metadata.plan_commit -cne [string]$Identity.plan_commit -or
        [string]$Document.metadata.image_tag -cne [string]$Identity.image_tag -or
        [string]$Document.metadata.image_id -cne [string]$Identity.image_id -or
        [string]$Document.metadata.owner_authorization_id -cne $OwnerAuthorizationId
    ) { throw 'A11 calibration receipt identity mismatch before validation' }
    return $true
}

function Close-A11Phase {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [string]$Terminal = [string]$Identity.terminal,
        [string]$Failure = ''
    )
    $AuditRoot = [IO.Path]::Combine($Identity.campaign_root, 'audit')
    $DiagnosticRecord = $null
    $ErrorList = if ([string]::IsNullOrWhiteSpace($Failure)) { @() } else { @($Failure) }
    $ArtifactRoot = [IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName([string]$Identity.campaign_root))
    $Historical = Get-A11HistoricalArtifactInventory -ArtifactRoot $ArtifactRoot
    $Images = Get-A11HistoricalImageInventory
    $Preserved = (
        @($Historical.records).Count -eq 64306 -and
        @($Images.records).Count -eq 21 -and
        $Historical.sha256 -ceq 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95' -and
        $Images.sha256 -ceq '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f'
    )
    if (-not $Preserved) {
        $Terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
        $ErrorList += 'A11 final historical preservation rehash failed'
    }
    $Identity.terminal = $Terminal
    if (
        $Terminal -ceq 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' -and
        $ErrorList.Count -eq 0
    ) {
        $AggregatePath = [IO.Path]::Combine(
            $Identity.campaign_root, 'wave0', 'receipts',
            "statistical-replay-$($Identity.phase).json"
        )
        if (Test-Path -LiteralPath $AggregatePath -PathType Leaf) {
            $Aggregate = Get-Content -Raw -LiteralPath $AggregatePath | ConvertFrom-Json
            $ErrorList = @($Aggregate.normative.errors | ForEach-Object { [string]$_ })
        }
        if ($ErrorList.Count -eq 0) { $ErrorList = @('A11 normative phase failure') }
    }
    $Failure = $ErrorList -join '; '
    if (
        $ErrorList.Count -ne 0 -or
        $Terminal -ceq 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
    ) {
        $Stage = if ($null -ne $Identity.PSObject.Properties['current_stage']) {
            [string]$Identity.current_stage
        } else { 'unknown' }
        $Attempted = [IO.Path]::Combine(
            $Identity.campaign_root, 'wave0', 'receipts',
            "statistical-replay-$($Identity.phase).json"
        )
        $DiagnosticPath = [IO.Path]::Combine($AuditRoot, '78-failure-diagnostic.json')
        $Diagnostic = [ordered]@{
            schema_version = 1
            phase = $Identity.phase
            failed_stage = $Stage
            errors = @($ErrorList)
            attempted_success_destination = $Attempted.Replace('\', '/')
            identity = [ordered]@{
                run_id = $Identity.run_id
                source_commit = $Identity.source_commit
                specification_commit = $Identity.specification_commit
                plan_commit = $Identity.plan_commit
                image_tag = $Identity.image_tag
                image_id = $Identity.image_id
                owner_authorization_id = $Identity.owner_authorization_id
            }
            terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
        }
        Write-A11NewText -Path $DiagnosticPath -Text (($Diagnostic | ConvertTo-Json -Depth 8 -Compress) + "`n")
        $DiagnosticRecord = Get-A11FileRecord -Path $DiagnosticPath
    }
    $FinalHistoryPath = [IO.Path]::Combine($AuditRoot, '79-historical-preservation-final.json')
    Write-A11NewText -Path $FinalHistoryPath -Text (([ordered]@{
        schema_version = 1
        historical_file_count = @($Historical.records).Count
        historical_image_count = @($Images.records).Count
        historical_file_inventory_sha256 = $Historical.sha256
        historical_image_inventory_sha256 = $Images.sha256
        preserved = $Preserved
    } | ConvertTo-Json -Compress) + "`n")
    $ResultPath = [IO.Path]::Combine($AuditRoot, '80-campaign-result.json')
    $Result = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        run_id = $Identity.run_id
        terminal = $Terminal
        failure = $Failure
        lease_active = [bool]$Identity.lease_acquired
        failure_diagnostic = $DiagnosticRecord
        historical_preservation = Get-A11FileRecord -Path $FinalHistoryPath
    }
    Write-A11NewText -Path $ResultPath -Text (($Result | ConvertTo-Json -Compress) + "`n")
    $Files = @(Get-ChildItem -LiteralPath $Identity.campaign_root -File -Recurse -Force |
        Sort-Object FullName | ForEach-Object { Get-A11FileRecord -Path $_.FullName })
    $ManifestPath = [IO.Path]::Combine($AuditRoot, '81-campaign-file-manifest.json')
    Write-A11NewText -Path $ManifestPath -Text (([ordered]@{ files = $Files } |
        ConvertTo-Json -Depth 8 -Compress) + "`n")
    $ClosurePath = [IO.Path]::Combine($AuditRoot, '82-campaign-closure.json')
    $Closure = [ordered]@{
        schema_version = 1
        phase = $Identity.phase
        run_id = $Identity.run_id
        result = Get-A11FileRecord -Path $ResultPath
        manifest = Get-A11FileRecord -Path $ManifestPath
        terminal = $Terminal
    }
    Write-A11NewText -Path $ClosurePath -Text (($Closure | ConvertTo-Json -Depth 8 -Compress) + "`n")
    return $Closure
}

function Test-A11CrossPhaseIdentity {
    param(
        [Parameter(Mandatory = $true)][object]$Calibration,
        [Parameter(Mandatory = $true)][object]$Validation
    )
    if (
        Compare-Object `
            @($Calibration.PSObject.Properties.Name | Sort-Object) `
            @($Validation.PSObject.Properties.Name | Sort-Object)
    ) { throw 'A11 cross-phase identity fields mismatch' }
    if (
        Compare-Object `
            @($Calibration.runtime.PSObject.Properties.Name | Sort-Object) `
            @($Validation.runtime.PSObject.Properties.Name | Sort-Object)
    ) { throw 'A11 cross-phase runtime fields mismatch' }
    if (
        ($Calibration.static | ConvertTo-Json -Depth 20 -Compress) -cne
        ($Validation.static | ConvertTo-Json -Depth 20 -Compress)
    ) { throw 'A11 cross-phase static identity mismatch' }
    $ListFields = @(
        'container_ids', 'receipt_paths', 'receipt_hashes', 'checkpoint_paths',
        'checkpoint_hashes', 'timestamps', 'audit_paths'
    )
    foreach ($Field in $Calibration.runtime.PSObject.Properties.Name) {
        if ($Field -in $ListFields) {
            $Left = @($Calibration.runtime.$Field)
            $Right = @($Validation.runtime.$Field)
            if (
                @($Left | Sort-Object -Unique).Count -ne $Left.Count -or
                @($Right | Sort-Object -Unique).Count -ne $Right.Count
            ) { throw "A11 cross-phase runtime identity duplicated: $Field" }
            if (@($Left | Where-Object { $_ -cin $Right }).Count -ne 0) {
                throw "A11 cross-phase runtime identity reused: $Field"
            }
        } elseif ([string]$Calibration.runtime.$Field -ceq [string]$Validation.runtime.$Field) {
            throw "A11 cross-phase runtime identity reused: $Field"
        }
    }
    return [pscustomobject]@{ valid = $true }
}

function Get-A11SingleCampaignResult {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Values
    )
    if ($Values.Count -ne 1) {
        throw "A11 campaign result cardinality mismatch: expected 1, observed $($Values.Count)"
    }
    $Result = $Values[0]
    if ($null -eq $Result -or $null -eq $Result.PSObject.Properties['terminal']) {
        throw 'A11 campaign result terminal is missing'
    }
    return $Result
}

function Invoke-A11Campaign {
    param(
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$AuthorizationId
    )
    $RawPreflight = Resolve-A11Worktree $SourceCommit $SpecCommit $PlanCommit $Branch $AuthorizationId
    $PreflightKeys = @(
        'worktree_path', 'git_dir', 'common_dir', 'linked_worktree', 'branch', 'head',
        'spec_commit', 'plan_commit', 'plan_parent_is_spec', 'linked_status',
        'canonical_status', 'val_data_root_present', 'docker_context', 'docker_os',
        'docker_server_version', 'gpu_rows', 'project_containers', 'active_leases',
        'prior_a11_attempt', 'historical_file_count', 'historical_image_count',
        'historical_file_inventory_sha256', 'historical_image_inventory_sha256',
        'historical_preserved'
    )
    $ClosedPreflight = [ordered]@{}
    foreach ($Key in $PreflightKeys) { $ClosedPreflight[$Key] = $RawPreflight[$Key] }
    Test-A11ReadOnlyPreflight ($ClosedPreflight | ConvertTo-Json -Depth 8 -Compress) `
        $SourceCommit $SpecCommit $PlanCommit $Branch $AuthorizationId | Out-Null
    $ArtifactRoot = if ($RawPreflight.Contains('artifact_root')) {
        [string]$RawPreflight.artifact_root
    } else { 'D:\vision-active-learning-loop-artifacts\wave0' }
    $Calibration = New-A11PhaseIdentity 'calibration' $SourceCommit $SpecCommit $PlanCommit $AuthorizationId $ArtifactRoot
    $Validation = New-A11PhaseIdentity 'validation' $SourceCommit $SpecCommit $PlanCommit $AuthorizationId $ArtifactRoot
    Test-A11PhaseDestinationsAbsent -Identities @($Calibration, $Validation) | Out-Null
    $CrossPhaseEvidence = {
        param([Parameter(Mandatory = $true)][object]$Value)
        [pscustomobject]@{
            static = [ordered]@{
                source = $Value.source_commit
                specification = $Value.specification_commit
                plan = $Value.plan_commit
                base = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
                model = 'pinned-rtdetr-dinov2-wave0'
                cache_inventory = $Value.cache_inventory_sha256
                gpu = [ordered]@{
                    uuid = 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63'
                    driver = $Value.gpu_driver
                    cuda_runtime = '12.6'
                }
            }
            runtime = [ordered]@{
                run_id = $Value.run_id
                image_tag = $Value.image_tag
                image_id = $Value.image_id
                campaign_root = $Value.campaign_root
                cache_root = $Value.cache_root
                lease_id = $Value.lease_id
                lease_path = $Value.lease_path
                container_ids = @($Value.replica_records.container_id)
                receipt_paths = @($Value.replica_records.feasibility.path)
                receipt_hashes = @($Value.replica_records.feasibility.sha256)
                checkpoint_paths = @($Value.replica_records.checkpoint.path)
                checkpoint_hashes = @($Value.replica_records.checkpoint.sha256)
                timestamps = @($Value.replica_records.timestamp)
                audit_paths = @($Value.audit_records.Values.path)
            }
        }
    }
    $PhaseIdentities = @($Calibration, $Validation)
    foreach ($Identity in $PhaseIdentities) {
        $Peer = if ($Identity.phase -ceq 'calibration') { $Validation } else { $Calibration }
        if ($Identity.phase -ceq 'validation') {
            if (
                [string]$Calibration.terminal -cne 'WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN' -or
                [bool]$Calibration.lease_acquired -or $null -eq $Calibration.release
            ) {
                return [pscustomobject]@{
                    terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
                    error = 'calibration did not close and release before validation'
                }
            }
            Confirm-A11Release $Calibration | Out-Null
        }
        try {
            $Identity.current_stage = 'protected-git'
            Confirm-A11ProtectedGit $SourceCommit $SpecCommit $PlanCommit $Branch | Out-Null
            $Identity.current_stage = 'initialize'
            Initialize-A11Phase $Identity $Peer | Out-Null
            $Identity.current_stage = 'build'
            Invoke-A11Build $Identity | Out-Null
            $Identity.current_stage = 'cache-preflight'
            Invoke-A11CachePreflight $Identity | Out-Null
            if ($Identity.phase -ceq 'validation') {
                $Identity.current_stage = 'calibration-precheck'
                Confirm-A11CalibrationReceipt $Calibration $AuthorizationId | Out-Null
                $Identity.current_stage = 'cross-phase-pre-model'
                Confirm-A11ProtectedGit $SourceCommit $SpecCommit $PlanCommit $Branch | Out-Null
                Test-A11CrossPhaseIdentity `
                    (& $CrossPhaseEvidence $Calibration) `
                    (& $CrossPhaseEvidence $Validation) | Out-Null
            }
            $Identity.current_stage = 'lease-acquire'
            New-A11Lease $Identity 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63' $Identity.lease_lock_path | Out-Null
            $Identity.current_stage = 'foundation'
            Invoke-A11Foundation $Identity | Out-Null
            for ($Index = 0; $Index -lt 12; $Index++) {
                $ReplicaId = '{0}-{1:d2}' -f $Identity.phase, $Index
                $Identity.current_stage = "replica:$ReplicaId"
                Invoke-A11Replica $Identity $ReplicaId | Out-Null
            }
            $Identity.current_stage = 'protected-git-post-replicas'
            Confirm-A11ProtectedGit $SourceCommit $SpecCommit $PlanCommit $Branch | Out-Null
            $Identity.current_stage = 'aggregate-gate'
            $Terminal = Invoke-A11Gate $Identity
            $Identity.terminal = $Terminal
            if (
                $Identity.phase -ceq 'calibration' -and
                $Terminal -cne 'WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'
            ) {
                if ($Identity.lease_acquired) {
                    $Identity.current_stage = 'lease-release'
                    Release-A11Lease $Identity | Out-Null
                }
                $Identity.current_stage = 'closure'
                Close-A11Phase $Identity 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' 'calibration terminal mismatch' | Out-Null
                return [pscustomobject]@{ terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' }
            }
            $Identity.current_stage = 'aggregate-verify'
            Assert-A11AggregateReceipt $Identity | Out-Null
            $Identity.current_stage = 'lease-release'
            Release-A11Lease $Identity | Out-Null
            if ($Identity.phase -ceq 'validation') {
                $Identity.current_stage = 'cross-phase-final'
                Test-A11CrossPhaseIdentity `
                    (& $CrossPhaseEvidence $Calibration) `
                    (& $CrossPhaseEvidence $Validation) | Out-Null
            }
            $Identity.current_stage = 'closure'
            Close-A11Phase $Identity $Terminal '' | Out-Null
        } catch {
            $Failure = $_.Exception.Message
            if ($Identity.lease_acquired) {
                if ($Identity.current_stage -ceq 'lease-release') {
                    $Failure += '; lease release failed; active lease retained'
                } else {
                    try { Release-A11Lease $Identity | Out-Null } catch { $Failure += "; lease release failed: $($_.Exception.Message)" }
                }
            }
            if ($Identity.current_stage -ceq 'closure') {
                return [pscustomobject]@{
                    terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
                    error = 'A11 phase closure publication failed'
                    closure_error = $Failure
                }
            }
            try {
                Close-A11Phase $Identity 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' $Failure | Out-Null
            } catch {
                return [pscustomobject]@{
                    terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
                    error = $Failure
                    closure_error = $_.Exception.Message
                }
            }
            return [pscustomobject]@{ terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'; error = $Failure }
        }
    }
    return [pscustomobject]@{ terminal = [string]$Validation.terminal; calibration=$Calibration.run_id; validation=$Validation.run_id }
}

try {
    $A11Values = @(Invoke-A11Campaign $ExpectedSourceCommit $ExpectedSpecCommit `
        $ExpectedPlanCommit $ExpectedBranch $OwnerAuthorizationId)
    $A11Result = Get-A11SingleCampaignResult -Values $A11Values
    $A11Result | ConvertTo-Json -Depth 8 -Compress
    $ClosureErrorProperty = $A11Result.PSObject.Properties['closure_error']
    if (
        $null -ne $ClosureErrorProperty -and
        -not [string]::IsNullOrWhiteSpace([string]$A11Result.closure_error)
    ) {
        [Console]::Error.WriteLine(
            "A11 closure publication failed: $($A11Result.closure_error)"
        )
    }
    if ([string]$A11Result.terminal -ceq 'WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED') {
        exit 0
    }
    exit 2
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 2
}
