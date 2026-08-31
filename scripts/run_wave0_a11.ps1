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

function Get-A11RegisteredAttemptPaths {
    param(
        [Parameter(Mandatory = $true)][string]$ArtifactRoot,
        [Parameter(Mandatory = $true)][object[]]$Identities
    )
    if ($Identities.Count -ne 2) {
        throw 'A11 prior registered identity cardinality mismatch'
    }
    $Root = [IO.Path]::GetFullPath($ArtifactRoot)
    $Values = [Collections.Generic.List[string]]::new()
    foreach ($Identity in $Identities) {
        $RunId = [string]$Identity.run_id
        $Campaign = [IO.Path]::GetFullPath(
            [IO.Path]::Combine($Root, 'a11-runs', $RunId)
        )
        $Cache = [IO.Path]::GetFullPath(
            [IO.Path]::Combine($Campaign, 'wave0', 'model_cache')
        )
        $ActiveLease = [IO.Path]::GetFullPath(
            [IO.Path]::Combine($Campaign, 'audit', 'active-lease.json')
        )
        foreach ($Pair in @(
            @([string]$Identity.campaign_root, $Campaign),
            @([string]$Identity.cache_root, $Cache),
            @([string]$Identity.lease_path, $ActiveLease)
        )) {
            if (-not [string]::Equals(
                [IO.Path]::GetFullPath($Pair[0]), $Pair[1],
                [StringComparison]::OrdinalIgnoreCase
            )) { throw 'A11 prior registered path identity mismatch' }
        }
        foreach ($Path in @(
            $Campaign,
            $Cache,
            $ActiveLease,
            [IO.Path]::Combine($Root, 'leases', "$RunId.released"),
            [IO.Path]::Combine($Root, 'leases', "$RunId.release.json"),
            [IO.Path]::Combine($Campaign, 'audit'),
            [IO.Path]::Combine($Campaign, 'wave0', 'receipts'),
            [IO.Path]::Combine($Campaign, 'wave0', 'checkpoints')
        )) { [void]$Values.Add([IO.Path]::GetFullPath($Path)) }
    }
    return @($Values.ToArray())
}

function Get-A11PriorAttemptInventory {
    param([Parameter(Mandatory = $true)][string]$ArtifactRoot)
    $Run1Id = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
    $Run2Id = 'wave0-a11-calibration-20260828T114911289Z-fe8b7000'
    $Run3Id = 'wave0-a11-calibration-20260828T172921151Z-a0f55fa1'
    $Run4Id = 'wave0-a11-calibration-20260829T050706309Z-f5a0129e'
    $Run5Id = 'wave0-a11-calibration-20260829T123151657Z-bf516632'
    $Attempt1ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
    $Attempt3ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1'
    $Attempt4ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e'
    $A11Root = [IO.Path]::GetFullPath([IO.Path]::Combine($ArtifactRoot, 'a11-runs'))
    $Run1Root = [IO.Path]::Combine($A11Root, $Run1Id)
    $Run2Root = [IO.Path]::Combine($A11Root, $Run2Id)
    $Run3Root = [IO.Path]::Combine($A11Root, $Run3Id)
    $Run4Root = [IO.Path]::Combine($A11Root, $Run4Id)
    $Run5Root = [IO.Path]::Combine($A11Root, $Run5Id)
    $LeaseRoot = [IO.Path]::GetFullPath([IO.Path]::Combine($ArtifactRoot, 'leases'))
    $Run1ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$Run1Id.released")
    $Run1ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$Run1Id.release.json")
    $Run3ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$Run3Id.released")
    $Run3ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$Run3Id.release.json")
    $Run4ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$Run4Id.released")
    $Run4ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$Run4Id.release.json")
    foreach ($Path in @(
        $A11Root, $Run1Root, $Run2Root, $Run3Root, $Run4Root, $Run5Root,
        $LeaseRoot,
        $Run1ReleasedPath, $Run1ReleaseRecordPath,
        $Run3ReleasedPath, $Run3ReleaseRecordPath,
        $Run4ReleasedPath, $Run4ReleaseRecordPath
    )) {
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A11 prior attempt path contains a link: $Path"
        }
    }
    $Linked = @(
        Get-ChildItem -LiteralPath $Run1Root, $Run2Root, $Run3Root, $Run4Root, $Run5Root, $LeaseRoot -Recurse -Force |
            Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }
    )
    if ($Linked.Count -ne 0) { throw 'A11 prior attempt tree contains a link' }

    $RunNames = @(
        Get-ChildItem -LiteralPath $A11Root -Directory -Force |
            Sort-Object Name -CaseSensitive | ForEach-Object Name
    )
    $LeaseNames = @(
        Get-ChildItem -LiteralPath $LeaseRoot -File -Force |
            Where-Object { $_.Name -like 'wave0-a11-*' } |
            Sort-Object Name -CaseSensitive | ForEach-Object Name
    )
    if (
        $RunNames.Count -ne 5 -or
        [string]$RunNames[0] -cne $Run1Id -or
        [string]$RunNames[1] -cne $Run2Id -or
        [string]$RunNames[2] -cne $Run3Id -or
        [string]$RunNames[3] -cne $Run4Id -or
        [string]$RunNames[4] -cne $Run5Id -or
        $LeaseNames.Count -ne 6 -or
        [string]$LeaseNames[0] -cne "$Run1Id.release.json" -or
        [string]$LeaseNames[1] -cne "$Run1Id.released" -or
        [string]$LeaseNames[2] -cne "$Run3Id.release.json" -or
        [string]$LeaseNames[3] -cne "$Run3Id.released" -or
        [string]$LeaseNames[4] -cne "$Run4Id.release.json" -or
        [string]$LeaseNames[5] -cne "$Run4Id.released"
    ) { throw 'A11 prior attempt root inventory drifted' }

    $Identity1Path = [IO.Path]::Combine($Run1Root, 'audit', '00-identity.json')
    $Identity2Path = [IO.Path]::Combine($Run2Root, 'audit', '00-identity.json')
    $Identity3Path = [IO.Path]::Combine($Run3Root, 'audit', '00-identity.json')
    $Identity4Path = [IO.Path]::Combine($Run4Root, 'audit', '00-identity.json')
    $Identity5Path = [IO.Path]::Combine($Run5Root, 'audit', '00-identity.json')
    $Identity1 = Get-Content -Raw -LiteralPath $Identity1Path | ConvertFrom-Json
    $Identity2 = Get-Content -Raw -LiteralPath $Identity2Path | ConvertFrom-Json
    $Identity3 = Get-Content -Raw -LiteralPath $Identity3Path | ConvertFrom-Json
    $Identity4 = Get-Content -Raw -LiteralPath $Identity4Path | ConvertFrom-Json
    $Identity5 = Get-Content -Raw -LiteralPath $Identity5Path | ConvertFrom-Json
    foreach ($Identity in @($Identity1, $Identity2, $Identity3, $Identity4, $Identity5)) {
        if (
            [string]::IsNullOrWhiteSpace([string]$Identity.current.owner_authorization_id) -or
            [string]$Identity.current.owner_authorization_id -cne
                [string]$Identity.preregistered_peer.owner_authorization_id
        ) { throw 'A11 prior attempt authorization identity mismatch' }
    }
    if (
        [string]$Identity1.current.run_id -cne $Run1Id -or
        [string]$Identity2.current.run_id -cne $Run2Id -or
        [string]$Identity3.current.run_id -cne $Run3Id -or
        [string]$Identity4.current.run_id -cne $Run4Id -or
        [string]$Identity5.current.run_id -cne $Run5Id
    ) { throw 'A11 prior attempt current identity mismatch' }

    $Records1 = @(
        Get-ChildItem -LiteralPath $Run1Root -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($Run1Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $Records2 = @(
        Get-ChildItem -LiteralPath $Run2Root -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($Run2Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $Records3 = @(
        Get-ChildItem -LiteralPath $Run3Root -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($Run3Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $Records4 = @(
        Get-ChildItem -LiteralPath $Run4Root -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($Run4Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $Records5 = @(
        Get-ChildItem -LiteralPath $Run5Root -File -Recurse -Force |
            Sort-Object FullName |
            ForEach-Object {
                [ordered]@{
                    path = $_.FullName.Substring($Run5Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            }
    )
    $Directories2 = @(
        Get-ChildItem -LiteralPath $Run2Root -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run2Root.Length + 1).Replace('\', '/')
            }
    )
    $Directories3 = @(
        Get-ChildItem -LiteralPath $Run3Root -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run3Root.Length + 1).Replace('\', '/')
            }
    )
    $Directories4 = @(
        Get-ChildItem -LiteralPath $Run4Root -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run4Root.Length + 1).Replace('\', '/')
            }
    )
    $Directories5 = @(
        Get-ChildItem -LiteralPath $Run5Root -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run5Root.Length + 1).Replace('\', '/')
            }
    )
    $Payload2 = @(
        Get-ChildItem -LiteralPath ([IO.Path]::Combine($Run2Root, 'wave0')) `
            -File -Recurse -Force | Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run2Root.Length + 1).Replace('\', '/')
            }
    )
    $Payload5 = @(
        Get-ChildItem -LiteralPath ([IO.Path]::Combine($Run5Root, 'wave0')) `
            -File -Recurse -Force | Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run5Root.Length + 1).Replace('\', '/')
            }
    )
    $Closure1Present = @(@(
        '78-failure-diagnostic.json', '80-campaign-result.json',
        '81-campaign-file-manifest.json', '82-campaign-closure.json'
    ) | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine($Run1Root, 'audit', $_))
    })
    $Closure2Present = @(@(
        '78-failure-diagnostic.json', '79-historical-preservation-final.json',
        '80-campaign-result.json', '81-campaign-file-manifest.json',
        '82-campaign-closure.json'
    ) | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine($Run2Root, 'audit', $_))
    })
    $Closure3Present = @(@(
        '78-failure-diagnostic.json', '79-historical-preservation-final.json',
        '80-campaign-result.json', '81-campaign-file-manifest.json',
        '82-campaign-closure.json'
    ) | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine($Run3Root, 'audit', $_))
    })
    $Closure4Present = @(@(
        '78-failure-diagnostic.json', '79-historical-preservation-final.json',
        '80-campaign-result.json', '81-campaign-file-manifest.json',
        '82-campaign-closure.json'
    ) | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine($Run4Root, 'audit', $_))
    })
    $Closure5Present = @(@(
        '78-failure-diagnostic.json', '79-historical-preservation-final.json',
        '80-campaign-result.json', '81-campaign-file-manifest.json',
        '82-campaign-closure.json'
    ) | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine($Run5Root, 'audit', $_))
    })
    $ExpectedDirectories3 = @(
        'audit',
        'wave0',
        'wave0/checkpoints',
        'wave0/model_cache',
        'wave0/model_cache/snapshots',
        'wave0/model_cache/snapshots/facebook--dinov2-small',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees',
        'wave0/receipts'
    )
    $ExpectedKeyNames3 = @(
        'audit/00-identity.json',
        'audit/10-build.json',
        'audit/11-image-inspect.json',
        'audit/20-cache-preflight.json',
        'audit/30-environment.json',
        'audit/31-model-assets.json',
        'audit/32-model-contract.json',
        'audit/32-model-contract.stderr.log',
        'audit/32-model-contract.stdout.log',
        'audit/78-failure-diagnostic.json',
        'audit/79-historical-preservation-final.json',
        'audit/80-campaign-result.json',
        'audit/81-campaign-file-manifest.json',
        'audit/82-campaign-closure.json',
        'wave0/receipts/model-contract.json'
    )
    $ExpectedDirectories4 = @(
        'audit',
        'wave0',
        'wave0/checkpoints',
        'wave0/checkpoints/calibration-00',
        'wave0/checkpoints/calibration-01',
        'wave0/checkpoints/calibration-02',
        'wave0/checkpoints/calibration-03',
        'wave0/checkpoints/calibration-04',
        'wave0/checkpoints/calibration-05',
        'wave0/checkpoints/calibration-06',
        'wave0/checkpoints/calibration-07',
        'wave0/checkpoints/calibration-08',
        'wave0/checkpoints/calibration-09',
        'wave0/checkpoints/calibration-10',
        'wave0/checkpoints/calibration-11',
        'wave0/model_cache',
        'wave0/model_cache/snapshots',
        'wave0/model_cache/snapshots/facebook--dinov2-small',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees',
        'wave0/receipts'
    )
    $ExpectedKeyNames4 = @(
        'audit/00-identity.json',
        'audit/10-build.json',
        'audit/11-image-inspect.json',
        'audit/20-cache-preflight.json',
        'audit/30-environment.json',
        'audit/31-model-assets.json',
        'audit/32-model-contract.json',
        'audit/60-historical-preservation.json',
        'audit/70-phase-manifest.json',
        'audit/71-aggregate-gate.json',
        'audit/71-aggregate-gate.stderr.log',
        'audit/78-failure-diagnostic.json',
        'audit/79-historical-preservation-final.json',
        'audit/80-campaign-result.json',
        'audit/81-campaign-file-manifest.json',
        'audit/82-campaign-closure.json',
        'wave0/receipts/model-contract.json'
    )
    $KeyRecords3 = @($Records3 | Where-Object { [string]$_.path -cin $ExpectedKeyNames3 })
    $KeyRecords4 = @($Records4 | Where-Object { [string]$_.path -cin $ExpectedKeyNames4 })
    $CheckpointRoot3 = [IO.Path]::Combine($Run3Root, 'wave0', 'checkpoints')
    $ReplicaDirectories3 = @(
        Get-ChildItem -LiteralPath $CheckpointRoot3 -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run3Root.Length + 1).Replace('\', '/')
            }
    )
    $CheckpointFiles3 = @(
        Get-ChildItem -LiteralPath $CheckpointRoot3 -File -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run3Root.Length + 1).Replace('\', '/')
            }
    )
    $Validation3Present = Test-A11PathEntryPresent `
        -Path ([string]$Identity3.preregistered_peer.campaign_root)
    if (
        $Records3.Count -ne 60 -or
        $Directories3.Count -ne 18 -or
        @(Compare-Object $ExpectedDirectories3 $Directories3 -CaseSensitive).Count -ne 0 -or
        $KeyRecords3.Count -ne 15 -or
        $Closure3Present.Count -ne 5 -or
        $ReplicaDirectories3.Count -ne 0 -or
        $CheckpointFiles3.Count -ne 0 -or
        $Validation3Present
    ) { throw 'A11 prior attempt foundation-stream state drifted' }
    $CheckpointRoot4 = [IO.Path]::Combine($Run4Root, 'wave0', 'checkpoints')
    $ReplicaDirectories4 = @(
        Get-ChildItem -LiteralPath $CheckpointRoot4 -Directory -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run4Root.Length + 1).Replace('\', '/')
            }
    )
    $CheckpointFiles4 = @(
        Get-ChildItem -LiteralPath $CheckpointRoot4 -File -Recurse -Force |
            Sort-Object FullName | ForEach-Object {
                $_.FullName.Substring($Run4Root.Length + 1).Replace('\', '/')
            }
    )
    $ExpectedReplicaDirectories4 = @(0..11 | ForEach-Object {
        'wave0/checkpoints/calibration-{0:D2}' -f $_
    })
    $ExpectedCheckpointFiles4 = @(0..11 | ForEach-Object {
        'wave0/checkpoints/calibration-{0:D2}/step-000001.pt' -f $_
    })
    $CalibrationReceipts4 = @(0..11 | Where-Object {
        Test-A11PathEntryPresent -Path ([IO.Path]::Combine(
            $Run4Root, 'wave0', 'receipts', ('calibration-{0:D2}.json' -f $_)
        ))
    })
    $SuccessReceipt4Present = Test-A11PathEntryPresent -Path ([IO.Path]::Combine(
        $Run4Root, 'wave0', 'receipts', 'statistical-replay-calibration.json'
    ))
    $Validation4Present = Test-A11PathEntryPresent `
        -Path ([string]$Identity4.preregistered_peer.campaign_root)
    if (
        $Records4.Count -ne 137 -or
        $Directories4.Count -ne 30 -or
        @(Compare-Object $ExpectedDirectories4 $Directories4 -CaseSensitive).Count -ne 0 -or
        $KeyRecords4.Count -ne 17 -or
        $Closure4Present.Count -ne 5 -or
        (@($ReplicaDirectories4) | ConvertTo-Json -Compress) -cne
            ($ExpectedReplicaDirectories4 | ConvertTo-Json -Compress) -or
        (@($CheckpointFiles4) | ConvertTo-Json -Compress) -cne
            ($ExpectedCheckpointFiles4 | ConvertTo-Json -Compress) -or
        $CalibrationReceipts4.Count -ne 12 -or
        $SuccessReceipt4Present -or
        $Validation4Present
    ) { throw 'A11 prior attempt aggregate-cache-inventory state drifted' }
    $ExpectedDirectories5 = @(
        'audit',
        'wave0',
        'wave0/checkpoints',
        'wave0/model_cache',
        'wave0/receipts'
    )
    $Validation5Present = Test-A11PathEntryPresent `
        -Path ([string]$Identity5.preregistered_peer.campaign_root)
    if (
        $Records5.Count -ne 10 -or
        $Directories5.Count -ne 5 -or
        @(Compare-Object $ExpectedDirectories5 $Directories5 -CaseSensitive).Count -ne 0 -or
        $Payload5.Count -ne 0 -or
        $Closure5Present.Count -ne 5 -or
        $Validation5Present
    ) { throw 'A11 prior attempt image-build-failure state drifted' }

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
    if (
        $ImageTags.Count -ne 3 -or
        [string]$ImageTags[0] -cne $Attempt1ImageTag -or
        [string]$ImageTags[1] -cne $Attempt4ImageTag -or
        [string]$ImageTags[2] -cne $Attempt3ImageTag
    ) {
        throw 'A11 prior image inventory drifted'
    }
    $Inspect1 = Invoke-A11Native -FilePath 'docker' `
        -ArgumentList @('image', 'inspect', '--', $Attempt1ImageTag)
    $Inspect3 = Invoke-A11Native -FilePath 'docker' `
        -ArgumentList @('image', 'inspect', '--', $Attempt3ImageTag)
    $Inspect4 = Invoke-A11Native -FilePath 'docker' `
        -ArgumentList @('image', 'inspect', '--', $Attempt4ImageTag)
    if (
        $Inspect1.ExitCode -ne 0 -or $Inspect1.Stderr -cne '' -or
        $Inspect3.ExitCode -ne 0 -or $Inspect3.Stderr -cne '' -or
        $Inspect4.ExitCode -ne 0 -or $Inspect4.Stderr -cne ''
    ) {
        throw 'A11 prior image inspect failed'
    }
    $Images1 = @($Inspect1.Stdout | ConvertFrom-Json)
    $Images3 = @($Inspect3.Stdout | ConvertFrom-Json)
    $Images4 = @($Inspect4.Stdout | ConvertFrom-Json)
    if ($Images1.Count -ne 1 -or $Images3.Count -ne 1 -or $Images4.Count -ne 1) {
        throw 'A11 prior image inspect count mismatch'
    }
    $Labels3 = $Images3[0].Config.Labels
    $Labels4 = $Images4[0].Config.Labels
    if (
        [string]$Images1[0].Id -cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5' -or
        [string]$Images3[0].Id -cne 'sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd' -or
        [string]$Images4[0].Id -cne 'sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e' -or
        [string]$Labels3.'org.opencontainers.image.revision' -cne 'ff5cfac5820415662e608886f1a10d7892f3ee00' -or
        [string]$Labels3.'org.opencontainers.image.val.run_id' -cne $Run3Id -or
        [string]$Labels3.'org.opencontainers.image.val.spec_commit' -cne 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' -or
        [string]$Labels3.'org.opencontainers.image.val.plan_commit' -cne '7dbd3a7576ea76beccfc64f748c4e495259ea89b' -or
        [string]$Labels3.'org.opencontainers.image.base.digest' -cne 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356' -or
        [string]$Labels4.'org.opencontainers.image.revision' -cne '77f8eecb3b8c0f471a4e980269187ac02a3b9ebc' -or
        [string]$Labels4.'org.opencontainers.image.val.run_id' -cne $Run4Id -or
        [string]$Labels4.'org.opencontainers.image.val.spec_commit' -cne 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' -or
        [string]$Labels4.'org.opencontainers.image.val.plan_commit' -cne '7dbd3a7576ea76beccfc64f748c4e495259ea89b' -or
        [string]$Labels4.'org.opencontainers.image.base.digest' -cne 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    ) { throw 'A11 prior image identity drifted' }

    $Registered1 = @(Get-A11RegisteredAttemptPaths `
        -ArtifactRoot $ArtifactRoot `
        -Identities @($Identity1.current, $Identity1.preregistered_peer))
    $Registered2 = @(Get-A11RegisteredAttemptPaths `
        -ArtifactRoot $ArtifactRoot `
        -Identities @($Identity2.current, $Identity2.preregistered_peer))
    $Registered3 = @(Get-A11RegisteredAttemptPaths `
        -ArtifactRoot $ArtifactRoot `
        -Identities @($Identity3.current, $Identity3.preregistered_peer))
    $Registered4 = @(Get-A11RegisteredAttemptPaths `
        -ArtifactRoot $ArtifactRoot `
        -Identities @($Identity4.current, $Identity4.preregistered_peer))
    $Registered5 = @(Get-A11RegisteredAttemptPaths `
        -ArtifactRoot $ArtifactRoot `
        -Identities @($Identity5.current, $Identity5.preregistered_peer))
    $Attempt2LeasePaths = @(
        [string]$Identity2.current.lease_path,
        [string]$Identity2.preregistered_peer.lease_path,
        [IO.Path]::Combine($LeaseRoot, "$($Identity2.current.run_id).released"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity2.current.run_id).release.json"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity2.preregistered_peer.run_id).released"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity2.preregistered_peer.run_id).release.json")
    )
    $Attempt2LeasePresent = @($Attempt2LeasePaths | Where-Object {
        Test-A11PathEntryPresent -Path $_
    })
    $Validation2Present = Test-A11PathEntryPresent `
        -Path ([string]$Identity2.preregistered_peer.campaign_root)
    $ImageTags2Present = @($ImageTags | Where-Object {
        $_ -cin @(
            [string]$Identity2.current.image_tag,
            [string]$Identity2.preregistered_peer.image_tag
        )
    })
    if (
        $Records2.Count -ne 5 -or
        $Directories2.Count -ne 5 -or
        $Payload2.Count -ne 0 -or
        $Closure1Present.Count -ne 0 -or
        $Closure2Present.Count -ne 0 -or
        $Attempt2LeasePresent.Count -ne 0 -or
        $Validation2Present -or
        $ImageTags2Present.Count -ne 0
    ) { throw 'A11 prior attempt partial-state inventory drifted' }
    $Attempt5LeasePaths = @(
        [string]$Identity5.current.lease_path,
        [string]$Identity5.preregistered_peer.lease_path,
        [IO.Path]::Combine($LeaseRoot, "$($Identity5.current.run_id).released"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity5.current.run_id).release.json"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity5.preregistered_peer.run_id).released"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity5.preregistered_peer.run_id).release.json")
    )
    $Attempt5LeasePresent = @($Attempt5LeasePaths | Where-Object {
        Test-A11PathEntryPresent -Path $_
    })
    $ImageTags5Present = @($ImageTags | Where-Object {
        $_ -cin @(
            [string]$Identity5.current.image_tag,
            [string]$Identity5.preregistered_peer.image_tag
        )
    })
    if ($Attempt5LeasePresent.Count -ne 0 -or $ImageTags5Present.Count -ne 0) {
        throw 'A11 prior attempt image-build-failure resource drifted'
    }
    $Latest2 = Get-ChildItem -LiteralPath $Run2Root -File -Recurse -Force |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $Latest2) { throw 'A11 prior attempt latest write is unavailable' }
    $Latest3 = Get-ChildItem -LiteralPath $Run3Root -File -Recurse -Force |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $Latest3) { throw 'A11 prior attempt latest write is unavailable' }
    $Latest4 = Get-ChildItem -LiteralPath $Run4Root -File -Recurse -Force |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $Latest4) { throw 'A11 prior attempt latest write is unavailable' }
    $Latest5 = Get-ChildItem -LiteralPath $Run5Root -File -Recurse -Force |
        Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $Latest5) { throw 'A11 prior attempt latest write is unavailable' }

    $Attempt1 = [pscustomobject][ordered]@{
        state = 'launcher-stage-failure'
        run_id = $Run1Id
        source_commit = [string]$Identity1.current.source_commit
        registered_run_ids = @(
            [string]$Identity1.current.run_id,
            [string]$Identity1.preregistered_peer.run_id
        )
        registered_image_tags = @(
            [string]$Identity1.current.image_tag,
            [string]$Identity1.preregistered_peer.image_tag
        )
        registered_paths = $Registered1
        owner_authorization_id = [string]$Identity1.current.owner_authorization_id
        run_file_count = $Records1.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records1 -Depth 6
        historical_preservation_sha256 = (Get-FileHash -LiteralPath `
            ([IO.Path]::Combine($Run1Root, 'audit', '79-historical-preservation-final.json')) `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        released_lease_sha256 = (Get-FileHash -LiteralPath $Run1ReleasedPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        release_record_sha256 = (Get-FileHash -LiteralPath $Run1ReleaseRecordPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        closure_paths_present = $Closure1Present
        image_tag = $Attempt1ImageTag
        image_id = [string]$Images1[0].Id
        links_absent = $true
    }
    $Attempt2 = [pscustomobject][ordered]@{
        state = 'image-build-timeout'
        run_id = $Run2Id
        source_commit = [string]$Identity2.current.source_commit
        registered_run_ids = @(
            [string]$Identity2.current.run_id,
            [string]$Identity2.preregistered_peer.run_id
        )
        registered_image_tags = @(
            [string]$Identity2.current.image_tag,
            [string]$Identity2.preregistered_peer.image_tag
        )
        registered_paths = $Registered2
        owner_authorization_id = [string]$Identity2.current.owner_authorization_id
        run_file_count = $Records2.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records2 -Depth 6
        file_records = $Records2
        directory_names = $Directories2
        image_tags_present = $ImageTags2Present
        lease_paths_present = $Attempt2LeasePresent
        validation_present = $Validation2Present
        payload_file_paths_present = $Payload2
        closure_paths_present = $Closure2Present
        latest_write_utc = $Latest2.LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
    $Attempt3 = [pscustomobject][ordered]@{
        state = 'foundation-stream-contract-failure'
        run_id = $Run3Id
        source_commit = [string]$Identity3.current.source_commit
        specification_commit = [string]$Identity3.current.specification_commit
        plan_commit = [string]$Identity3.current.plan_commit
        registered_run_ids = @(
            [string]$Identity3.current.run_id,
            [string]$Identity3.preregistered_peer.run_id
        )
        registered_image_tags = @(
            [string]$Identity3.current.image_tag,
            [string]$Identity3.preregistered_peer.image_tag
        )
        registered_paths = $Registered3
        owner_authorization_id = [string]$Identity3.current.owner_authorization_id
        run_file_count = $Records3.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records3 -Depth 6
        directory_names = $Directories3
        key_file_records = $KeyRecords3
        image_tag = $Attempt3ImageTag
        image_id = [string]$Images3[0].Id
        release_record_sha256 = (Get-FileHash -LiteralPath $Run3ReleaseRecordPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        released_lease_sha256 = (Get-FileHash -LiteralPath $Run3ReleasedPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        validation_present = $Validation3Present
        replica_directory_names_present = $ReplicaDirectories3
        checkpoint_file_paths_present = $CheckpointFiles3
        closure_paths_present = $Closure3Present
        latest_write_utc = $Latest3.LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
    $Attempt4 = [pscustomobject][ordered]@{
        state = 'aggregate-cache-inventory-contract-failure'
        run_id = $Run4Id
        source_commit = [string]$Identity4.current.source_commit
        specification_commit = [string]$Identity4.current.specification_commit
        plan_commit = [string]$Identity4.current.plan_commit
        registered_run_ids = @(
            [string]$Identity4.current.run_id,
            [string]$Identity4.preregistered_peer.run_id
        )
        registered_image_tags = @(
            [string]$Identity4.current.image_tag,
            [string]$Identity4.preregistered_peer.image_tag
        )
        registered_paths = $Registered4
        owner_authorization_id = [string]$Identity4.current.owner_authorization_id
        run_file_count = $Records4.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records4 -Depth 6
        directory_names = $Directories4
        key_file_records = $KeyRecords4
        image_tag = $Attempt4ImageTag
        image_id = [string]$Images4[0].Id
        release_record_sha256 = (Get-FileHash -LiteralPath $Run4ReleaseRecordPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        released_lease_sha256 = (Get-FileHash -LiteralPath $Run4ReleasedPath `
            -Algorithm SHA256).Hash.ToLowerInvariant()
        validation_present = $Validation4Present
        replica_directory_names_present = $ReplicaDirectories4
        checkpoint_file_paths_present = $CheckpointFiles4
        success_receipt_present = $SuccessReceipt4Present
        closure_paths_present = $Closure4Present
        latest_write_utc = $Latest4.LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
    $Attempt5 = [pscustomobject][ordered]@{
        state = 'image-build-failure'
        run_id = $Run5Id
        source_commit = [string]$Identity5.current.source_commit
        specification_commit = [string]$Identity5.current.specification_commit
        plan_commit = [string]$Identity5.current.plan_commit
        registered_run_ids = @(
            [string]$Identity5.current.run_id,
            [string]$Identity5.preregistered_peer.run_id
        )
        registered_image_tags = @(
            [string]$Identity5.current.image_tag,
            [string]$Identity5.preregistered_peer.image_tag
        )
        registered_paths = $Registered5
        owner_authorization_id = [string]$Identity5.current.owner_authorization_id
        run_file_count = $Records5.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records5 -Depth 6
        file_records = $Records5
        directory_names = $Directories5
        image_tags_present = $ImageTags5Present
        lease_paths_present = $Attempt5LeasePresent
        validation_present = $Validation5Present
        payload_file_paths_present = $Payload5
        closure_paths_present = $Closure5Present
        latest_write_utc = $Latest5.LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
    return [pscustomobject][ordered]@{
        run_names = $RunNames
        image_tags = $ImageTags
        lease_names = $LeaseNames
        authorization_evidence = @(
            [pscustomobject][ordered]@{
                run_id = $Run1Id
                path = 'audit/00-identity.json'
                owner_authorization_id = [string]$Identity1.current.owner_authorization_id
            },
            [pscustomobject][ordered]@{
                run_id = $Run2Id
                path = 'audit/00-identity.json'
                owner_authorization_id = [string]$Identity2.current.owner_authorization_id
            },
            [pscustomobject][ordered]@{
                run_id = $Run3Id
                path = 'audit/00-identity.json'
                owner_authorization_id = [string]$Identity3.current.owner_authorization_id
            },
            [pscustomobject][ordered]@{
                run_id = $Run4Id
                path = 'audit/00-identity.json'
                owner_authorization_id = [string]$Identity4.current.owner_authorization_id
            },
            [pscustomobject][ordered]@{
                run_id = $Run5Id
                path = 'audit/00-identity.json'
                owner_authorization_id = [string]$Identity5.current.owner_authorization_id
            }
        )
        attempts = @($Attempt1, $Attempt2, $Attempt3, $Attempt4, $Attempt5)
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

function Get-A11ProjectContainerInventory {
    $List = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
        'ps', '--all', '--format', '{{.ID}}|{{.Image}}'
    )
    if ($List.ExitCode -ne 0 -or $List.Stderr -cne '') {
        throw 'A11 project container inventory failed: list'
    }
    $Rows = @($List.Stdout -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    })
    $Seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $ProjectContainers = [Collections.Generic.List[string]]::new()
    foreach ($Row in $Rows) {
        $Fields = @($Row.Split('|', 2))
        if (
            $Fields.Count -ne 2 -or
            [string]$Fields[0] -cnotmatch '^[0-9a-f]{12,64}$' -or
            [string]::IsNullOrWhiteSpace([string]$Fields[1]) -or
            -not $Seen.Add([string]$Fields[0])
        ) { throw 'A11 project container inventory failed: malformed list' }
        $ContainerId = [string]$Fields[0]
        $Inspect = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
            'inspect', '--format', '{{.Image}}', '--', $ContainerId
        )
        if ($Inspect.ExitCode -ne 0 -or $Inspect.Stderr -cne '') {
            throw 'A11 project container inventory failed: inspect'
        }
        $ImageId = $Inspect.Stdout.Trim()
        if ($ImageId -cnotmatch '^sha256:[0-9a-f]{64}$') {
            throw 'A11 project container inventory failed: image identity'
        }
        $TagInspect = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
            'image', 'inspect', '--format', '{{json .RepoTags}}', '--', $ImageId
        )
        if ($TagInspect.ExitCode -ne 0 -or $TagInspect.Stderr -cne '') {
            throw 'A11 project container inventory failed: image inspect'
        }
        $RepoTagsJson = $TagInspect.Stdout.Trim()
        if ($RepoTagsJson -ceq 'null') {
            $RepoTags = @()
        } else {
            if (
                [string]::IsNullOrWhiteSpace($RepoTagsJson) -or
                -not $RepoTagsJson.StartsWith('[', [StringComparison]::Ordinal) -or
                -not $RepoTagsJson.EndsWith(']', [StringComparison]::Ordinal)
            ) { throw 'A11 project container inventory failed: image tag shape' }
            try {
                $ParsedRepoTags = ConvertFrom-Json -InputObject $RepoTagsJson
                $RepoTags = @($ParsedRepoTags)
            } catch {
                throw 'A11 project container inventory failed: image tags'
            }
            foreach ($RepoTag in $RepoTags) {
                if (
                    $RepoTag -isnot [string] -or
                    [string]::IsNullOrWhiteSpace([string]$RepoTag) -or
                    [string]$RepoTag -cnotmatch '^[^\s]+:[^\s]+$'
                ) { throw 'A11 project container inventory failed: image tag value' }
            }
        }
        if (@($RepoTags | Where-Object {
            [string]$_ -like 'vision-active-learning-loop:*'
        }).Count -gt 0) {
            [void]$ProjectContainers.Add("$ContainerId|$ImageId")
        }
    }
    return @($ProjectContainers.ToArray())
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
    $ProjectContainers = @(Get-A11ProjectContainerInventory)
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
        prior_a11_attempts = $PriorA11
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
    $Evidence = $EvidenceJson | ConvertFrom-Json
    $ExpectedKeys = @(
        'worktree_path', 'git_dir', 'common_dir', 'linked_worktree', 'branch',
        'head', 'spec_commit', 'plan_commit', 'plan_parent_is_spec',
        'linked_status', 'canonical_status', 'val_data_root_present',
        'docker_context', 'docker_os', 'docker_server_version', 'gpu_rows',
        'project_containers', 'active_leases', 'prior_a11_attempts',
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
    $Prior = $Evidence.prior_a11_attempts
    $ExpectedPriorKeys = @(
        'run_names', 'image_tags', 'lease_names', 'authorization_evidence',
        'attempts', 'links_absent'
    )
    $ActualPriorKeys = @($Prior.PSObject.Properties.Name | Sort-Object)
    if (Compare-Object ($ExpectedPriorKeys | Sort-Object) $ActualPriorKeys) {
        throw 'A11 prior A11 evidence fields mismatch'
    }
    $ExpectedRun1Id = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
    $ExpectedPeer1Id = 'wave0-a11-validation-20260828T045848091Z-084431a4'
    $ExpectedRun2Id = 'wave0-a11-calibration-20260828T114911289Z-fe8b7000'
    $ExpectedPeer2Id = 'wave0-a11-validation-20260828T114911296Z-3107aff0'
    $ExpectedRun3Id = 'wave0-a11-calibration-20260828T172921151Z-a0f55fa1'
    $ExpectedPeer3Id = 'wave0-a11-validation-20260828T172921161Z-70928997'
    $ExpectedRun4Id = 'wave0-a11-calibration-20260829T050706309Z-f5a0129e'
    $ExpectedPeer4Id = 'wave0-a11-validation-20260829T050706319Z-c6652f48'
    $ExpectedRun5Id = 'wave0-a11-calibration-20260829T123151657Z-bf516632'
    $ExpectedPeer5Id = 'wave0-a11-validation-20260829T123151664Z-7af53ca8'
    $ExpectedImage1Tag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
    $ExpectedPeer1Tag = 'vision-active-learning-loop:wave0-a11-validation-2622e402e4f5-20260828T045848091Z-084431a4'
    $ExpectedImage2Tag = 'vision-active-learning-loop:wave0-a11-calibration-1445a90b799b-20260828T114911289Z-fe8b7000'
    $ExpectedPeer2Tag = 'vision-active-learning-loop:wave0-a11-validation-1445a90b799b-20260828T114911296Z-3107aff0'
    $ExpectedImage3Tag = 'vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1'
    $ExpectedPeer3Tag = 'vision-active-learning-loop:wave0-a11-validation-ff5cfac58204-20260828T172921161Z-70928997'
    $ExpectedImage4Tag = 'vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e'
    $ExpectedPeer4Tag = 'vision-active-learning-loop:wave0-a11-validation-77f8eecb3b8c-20260829T050706319Z-c6652f48'
    $ExpectedImage5Tag = 'vision-active-learning-loop:wave0-a11-calibration-ed6f157c7cbd-20260829T123151657Z-bf516632'
    $ExpectedPeer5Tag = 'vision-active-learning-loop:wave0-a11-validation-ed6f157c7cbd-20260829T123151664Z-7af53ca8'
    $RunNames = @($Prior.run_names)
    $ImageTags = @($Prior.image_tags)
    $LeaseNames = @($Prior.lease_names)
    $AuthorizationEvidence = @($Prior.authorization_evidence)
    $Attempts = @($Prior.attempts)
    if (
        $RunNames.Count -ne 5 -or
        [string]$RunNames[0] -cne $ExpectedRun1Id -or
        [string]$RunNames[1] -cne $ExpectedRun2Id -or
        [string]$RunNames[2] -cne $ExpectedRun3Id -or
        [string]$RunNames[3] -cne $ExpectedRun4Id -or
        [string]$RunNames[4] -cne $ExpectedRun5Id -or
        $ImageTags.Count -ne 3 -or
        [string]$ImageTags[0] -cne $ExpectedImage1Tag -or
        [string]$ImageTags[1] -cne $ExpectedImage4Tag -or
        [string]$ImageTags[2] -cne $ExpectedImage3Tag -or
        $LeaseNames.Count -ne 6 -or
        [string]$LeaseNames[0] -cne "$ExpectedRun1Id.release.json" -or
        [string]$LeaseNames[1] -cne "$ExpectedRun1Id.released" -or
        [string]$LeaseNames[2] -cne "$ExpectedRun3Id.release.json" -or
        [string]$LeaseNames[3] -cne "$ExpectedRun3Id.released" -or
        [string]$LeaseNames[4] -cne "$ExpectedRun4Id.release.json" -or
        [string]$LeaseNames[5] -cne "$ExpectedRun4Id.released" -or
        $AuthorizationEvidence.Count -ne 5 -or
        $Attempts.Count -ne 5 -or
        $Prior.links_absent -cne $true
    ) { throw 'A11 prior A11 envelope drifted' }
    $ExpectedAuthorizationKeys = @('run_id', 'path', 'owner_authorization_id')
    foreach ($Index in 0..4) {
        if (Compare-Object `
            ($ExpectedAuthorizationKeys | Sort-Object) `
            @($AuthorizationEvidence[$Index].PSObject.Properties.Name | Sort-Object)
        ) { throw 'A11 prior A11 authorization evidence fields mismatch' }
    }
    if (
        [string]$AuthorizationEvidence[0].run_id -cne $ExpectedRun1Id -or
        [string]$AuthorizationEvidence[0].path -cne 'audit/00-identity.json' -or
        [string]$AuthorizationEvidence[0].owner_authorization_id -cne 'OWNER-A11-RUNTIME-20260828-01' -or
        [string]$AuthorizationEvidence[1].run_id -cne $ExpectedRun2Id -or
        [string]$AuthorizationEvidence[1].path -cne 'audit/00-identity.json' -or
        [string]$AuthorizationEvidence[1].owner_authorization_id -cne 'steven001' -or
        [string]$AuthorizationEvidence[2].run_id -cne $ExpectedRun3Id -or
        [string]$AuthorizationEvidence[2].path -cne 'audit/00-identity.json' -or
        [string]$AuthorizationEvidence[2].owner_authorization_id -cne 'steven002' -or
        [string]$AuthorizationEvidence[3].run_id -cne $ExpectedRun4Id -or
        [string]$AuthorizationEvidence[3].path -cne 'audit/00-identity.json' -or
        [string]$AuthorizationEvidence[3].owner_authorization_id -cne 'steven003' -or
        [string]$AuthorizationEvidence[4].run_id -cne $ExpectedRun5Id -or
        [string]$AuthorizationEvidence[4].path -cne 'audit/00-identity.json' -or
        [string]$AuthorizationEvidence[4].owner_authorization_id -cne 'steven004'
    ) { throw 'A11 prior A11 authorization evidence drifted' }

    $ExpectedAttempt1Keys = @(
        'state', 'run_id', 'source_commit', 'registered_run_ids',
        'registered_image_tags', 'registered_paths', 'owner_authorization_id',
        'run_file_count', 'run_inventory_sha256',
        'historical_preservation_sha256', 'released_lease_sha256',
        'release_record_sha256', 'closure_paths_present', 'image_tag',
        'image_id', 'links_absent'
    )
    $ExpectedAttempt2Keys = @(
        'state', 'run_id', 'source_commit', 'registered_run_ids',
        'registered_image_tags', 'registered_paths', 'owner_authorization_id',
        'run_file_count', 'run_inventory_sha256', 'file_records',
        'directory_names', 'image_tags_present', 'lease_paths_present',
        'validation_present', 'payload_file_paths_present',
        'closure_paths_present', 'latest_write_utc', 'links_absent'
    )
    $ExpectedAttempt3Keys = @(
        'state', 'run_id', 'source_commit', 'specification_commit',
        'plan_commit', 'registered_run_ids', 'registered_image_tags',
        'registered_paths', 'owner_authorization_id', 'run_file_count',
        'run_inventory_sha256', 'directory_names', 'key_file_records',
        'image_tag', 'image_id', 'release_record_sha256',
        'released_lease_sha256', 'validation_present',
        'replica_directory_names_present', 'checkpoint_file_paths_present',
        'closure_paths_present', 'latest_write_utc', 'links_absent'
    )
    $ExpectedAttempt4Keys = @(
        'state', 'run_id', 'source_commit', 'specification_commit',
        'plan_commit', 'registered_run_ids', 'registered_image_tags',
        'registered_paths', 'owner_authorization_id', 'run_file_count',
        'run_inventory_sha256', 'directory_names', 'key_file_records',
        'image_tag', 'image_id', 'release_record_sha256',
        'released_lease_sha256', 'validation_present',
        'replica_directory_names_present', 'checkpoint_file_paths_present',
        'success_receipt_present', 'closure_paths_present', 'latest_write_utc',
        'links_absent'
    )
    $ExpectedAttempt5Keys = @(
        'state', 'run_id', 'source_commit', 'specification_commit',
        'plan_commit', 'registered_run_ids', 'registered_image_tags',
        'registered_paths', 'owner_authorization_id', 'run_file_count',
        'run_inventory_sha256', 'file_records', 'directory_names',
        'image_tags_present', 'lease_paths_present', 'validation_present',
        'payload_file_paths_present', 'closure_paths_present',
        'latest_write_utc', 'links_absent'
    )
    $Attempt1KeyDifference = @(Compare-Object `
        ($ExpectedAttempt1Keys | Sort-Object) `
        @($Attempts[0].PSObject.Properties.Name | Sort-Object))
    $Attempt2KeyDifference = @(Compare-Object `
        ($ExpectedAttempt2Keys | Sort-Object) `
        @($Attempts[1].PSObject.Properties.Name | Sort-Object))
    $Attempt3KeyDifference = @(Compare-Object `
        ($ExpectedAttempt3Keys | Sort-Object) `
        @($Attempts[2].PSObject.Properties.Name | Sort-Object))
    $Attempt4KeyDifference = @(Compare-Object `
        ($ExpectedAttempt4Keys | Sort-Object) `
        @($Attempts[3].PSObject.Properties.Name | Sort-Object))
    $Attempt5KeyDifference = @(Compare-Object `
        ($ExpectedAttempt5Keys | Sort-Object) `
        @($Attempts[4].PSObject.Properties.Name | Sort-Object))
    if (
        $Attempt1KeyDifference.Count -ne 0 -or
        $Attempt2KeyDifference.Count -ne 0 -or
        $Attempt3KeyDifference.Count -ne 0 -or
        $Attempt4KeyDifference.Count -ne 0 -or
        $Attempt5KeyDifference.Count -ne 0
    ) {
        throw 'A11 prior A11 attempt evidence fields mismatch'
    }

    $BuildExpectedRegisteredPaths = {
        param([string[]]$RunIds)
        $Values = [Collections.Generic.List[string]]::new()
        $ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
        foreach ($RunId in $RunIds) {
            $Campaign = [IO.Path]::Combine($ArtifactRoot, 'a11-runs', $RunId)
            foreach ($Path in @(
                $Campaign,
                [IO.Path]::Combine($Campaign, 'wave0', 'model_cache'),
                [IO.Path]::Combine($Campaign, 'audit', 'active-lease.json'),
                [IO.Path]::Combine($ArtifactRoot, 'leases', "$RunId.released"),
                [IO.Path]::Combine($ArtifactRoot, 'leases', "$RunId.release.json"),
                [IO.Path]::Combine($Campaign, 'audit'),
                [IO.Path]::Combine($Campaign, 'wave0', 'receipts'),
                [IO.Path]::Combine($Campaign, 'wave0', 'checkpoints')
            )) { [void]$Values.Add([IO.Path]::GetFullPath($Path)) }
        }
        return @($Values.ToArray())
    }
    $PathListsEqual = {
        param([object[]]$Actual, [string[]]$Expected)
        if ($Actual.Count -ne $Expected.Count) { return $false }
        for ($Index = 0; $Index -lt $Expected.Count; $Index++) {
            if (-not [string]::Equals(
                [IO.Path]::GetFullPath([string]$Actual[$Index]),
                [IO.Path]::GetFullPath([string]$Expected[$Index]),
                [StringComparison]::OrdinalIgnoreCase
            )) { return $false }
        }
        return $true
    }
    $Attempt1 = $Attempts[0]
    $ExpectedPaths1 = @(& $BuildExpectedRegisteredPaths `
        @($ExpectedRun1Id, $ExpectedPeer1Id))
    if (
        [string]$Attempt1.state -cne 'launcher-stage-failure' -or
        [string]$Attempt1.run_id -cne $ExpectedRun1Id -or
        [string]$Attempt1.source_commit -cne '2622e402e4f536b94326ac34f9b20c90b513002b' -or
        (@($Attempt1.registered_run_ids) | ConvertTo-Json -Compress) -cne
            (@($ExpectedRun1Id, $ExpectedPeer1Id) | ConvertTo-Json -Compress) -or
        (@($Attempt1.registered_image_tags) | ConvertTo-Json -Compress) -cne
            (@($ExpectedImage1Tag, $ExpectedPeer1Tag) | ConvertTo-Json -Compress) -or
        -not (& $PathListsEqual @($Attempt1.registered_paths) $ExpectedPaths1) -or
        [string]$Attempt1.owner_authorization_id -cne 'OWNER-A11-RUNTIME-20260828-01' -or
        [int]$Attempt1.run_file_count -ne 48 -or
        [string]$Attempt1.run_inventory_sha256 -cne 'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b' -or
        [string]$Attempt1.historical_preservation_sha256 -cne '927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' -or
        [string]$Attempt1.released_lease_sha256 -cne '146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322' -or
        [string]$Attempt1.release_record_sha256 -cne '35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060' -or
        @($Attempt1.closure_paths_present).Count -ne 0 -or
        [string]$Attempt1.image_tag -cne $ExpectedImage1Tag -or
        [string]$Attempt1.image_id -cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5' -or
        $Attempt1.links_absent -cne $true
    ) { throw 'A11 prior A11 launcher-stage attempt drifted' }

    $ExpectedFiles2 = @(
        [pscustomobject][ordered]@{ path='audit/00-identity.json'; size=2873; sha256='df1b6f37bfd9f7bce399f3a8b481bba564b5cacdd397ca82723100802b4bcec3' },
        [pscustomobject][ordered]@{ path='audit/01-gpu-preflight.json'; size=125; sha256='de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7' },
        [pscustomobject][ordered]@{ path='audit/10-build.json'; size=1234; sha256='d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66' },
        [pscustomobject][ordered]@{ path='audit/10-build.stderr.log'; size=865210; sha256='50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e' },
        [pscustomobject][ordered]@{ path='audit/10-build.stdout.log'; size=0; sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' }
    )
    $Attempt2 = $Attempts[1]
    $ExpectedPaths2 = @(& $BuildExpectedRegisteredPaths `
        @($ExpectedRun2Id, $ExpectedPeer2Id))
    $LatestValue = $Attempt2.latest_write_utc
    if ($LatestValue -is [DateTime]) {
        $LatestValid = $LatestValue.Kind -eq [DateTimeKind]::Utc
    } else {
        $ParsedLatest = [DateTimeOffset]::MinValue
        $LatestStyles = [Globalization.DateTimeStyles]::AssumeUniversal -bor
            [Globalization.DateTimeStyles]::AdjustToUniversal
        $LatestValid = [DateTimeOffset]::TryParseExact(
            [string]$LatestValue,
            "yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'",
            [Globalization.CultureInfo]::InvariantCulture,
            $LatestStyles,
            [ref]$ParsedLatest
        ) -and $ParsedLatest.Offset -eq [TimeSpan]::Zero
    }
    if (
        [string]$Attempt2.state -cne 'image-build-timeout' -or
        [string]$Attempt2.run_id -cne $ExpectedRun2Id -or
        [string]$Attempt2.source_commit -cne '1445a90b799b6306d6c1f7abc94b4a201afe5dc6' -or
        (@($Attempt2.registered_run_ids) | ConvertTo-Json -Compress) -cne
            (@($ExpectedRun2Id, $ExpectedPeer2Id) | ConvertTo-Json -Compress) -or
        (@($Attempt2.registered_image_tags) | ConvertTo-Json -Compress) -cne
            (@($ExpectedImage2Tag, $ExpectedPeer2Tag) | ConvertTo-Json -Compress) -or
        -not (& $PathListsEqual @($Attempt2.registered_paths) $ExpectedPaths2) -or
        [string]$Attempt2.owner_authorization_id -cne 'steven001' -or
        [int]$Attempt2.run_file_count -ne 5 -or
        [string]$Attempt2.run_inventory_sha256 -cne '8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b' -or
        (@($Attempt2.file_records) | ConvertTo-Json -Compress) -cne
            ($ExpectedFiles2 | ConvertTo-Json -Compress) -or
        (@($Attempt2.directory_names) | ConvertTo-Json -Compress) -cne
            (@('audit','wave0','wave0/checkpoints','wave0/model_cache','wave0/receipts') | ConvertTo-Json -Compress) -or
        @($Attempt2.image_tags_present).Count -ne 0 -or
        @($Attempt2.lease_paths_present).Count -ne 0 -or
        $Attempt2.validation_present -cne $false -or
        @($Attempt2.payload_file_paths_present).Count -ne 0 -or
        @($Attempt2.closure_paths_present).Count -ne 0 -or
        -not $LatestValid -or
        $Attempt2.links_absent -cne $true
    ) { throw 'A11 prior A11 image-build-timeout attempt drifted' }

    $ExpectedDirectories3 = @(
        'audit',
        'wave0',
        'wave0/checkpoints',
        'wave0/model_cache',
        'wave0/model_cache/snapshots',
        'wave0/model_cache/snapshots/facebook--dinov2-small',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees',
        'wave0/receipts'
    )
    $ExpectedFiles3 = @(
        [pscustomobject][ordered]@{ path='audit/00-identity.json'; size=2873; sha256='e9c0743ef1b2311aac15b51e4208ff204ad7766581d1a440206bc2903d989461' },
        [pscustomobject][ordered]@{ path='audit/10-build.json'; size=1234; sha256='2ea371296b5eedf28074a8fb966b1fe58a985629f966c89a348c8bc4ab00b4ab' },
        [pscustomobject][ordered]@{ path='audit/11-image-inspect.json'; size=682; sha256='98e6a4b0f547c95ebd00d21caeec620283543906d839a24eabb67adc6945fffc' },
        [pscustomobject][ordered]@{ path='audit/20-cache-preflight.json'; size=1900; sha256='9827ccd8ea4d9f3625e26db1caecda276ac1a452f0cb4dad409eed2d9eeb7236' },
        [pscustomobject][ordered]@{ path='audit/30-environment.json'; size=1995; sha256='5523fce88357798387b5934baf32f311150f148ed95871f396539ab1682ef656' },
        [pscustomobject][ordered]@{ path='audit/31-model-assets.json'; size=2051; sha256='9e9e0e88a94b217d26e96741dfc34db499b72f579460a1465a5a988f2cf7ba66' },
        [pscustomobject][ordered]@{ path='audit/32-model-contract.json'; size=1910; sha256='4f2e6992aa40d9df1a0322565a6bdc2484f45fe6163eb5203e8efe911d3a85f8' },
        [pscustomobject][ordered]@{ path='audit/32-model-contract.stderr.log'; size=1362; sha256='05a5801f0f54bdc7d8a5d6494f46b5b5d08df990d6137fdae012f753d96d79ce' },
        [pscustomobject][ordered]@{ path='audit/32-model-contract.stdout.log'; size=5; sha256='c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431' },
        [pscustomobject][ordered]@{ path='audit/78-failure-diagnostic.json'; size=853; sha256='f50f883e74594752d9c4e6e4b857814c9072f0bfc0d75d0dcd229d2081b12676' },
        [pscustomobject][ordered]@{ path='audit/79-historical-preservation-final.json'; size=301; sha256='927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' },
        [pscustomobject][ordered]@{ path='audit/80-campaign-result.json'; size=764; sha256='1787120f4635a02ba14e6b08d390b896ca03e855efc22cdf710983bf94dd8bab' },
        [pscustomobject][ordered]@{ path='audit/81-campaign-file-manifest.json'; size=16740; sha256='ab28d20479a0b44a82bcb9c555f867c0c879a2da0cc0c117d2c4c8667749adf3' },
        [pscustomobject][ordered]@{ path='audit/82-campaign-closure.json'; size=660; sha256='75267ce8cc36bc25a6c7e985c4b836038241706477656211fe1328dd102bf76a' },
        [pscustomobject][ordered]@{ path='wave0/receipts/model-contract.json'; size=9623; sha256='307c95414578af6c6a90dc742fe359a5b985d2d6bd2e76e9228caf1475de4eaa' }
    )
    $Attempt3 = $Attempts[2]
    $ExpectedPaths3 = @(& $BuildExpectedRegisteredPaths `
        @($ExpectedRun3Id, $ExpectedPeer3Id))
    $Latest3Value = $Attempt3.latest_write_utc
    if ($Latest3Value -is [DateTime]) {
        $Latest3Valid = $Latest3Value.Kind -eq [DateTimeKind]::Utc
    } else {
        $ParsedLatest3 = [DateTimeOffset]::MinValue
        $Latest3Styles = [Globalization.DateTimeStyles]::AssumeUniversal -bor
            [Globalization.DateTimeStyles]::AdjustToUniversal
        $Latest3Valid = [DateTimeOffset]::TryParseExact(
            [string]$Latest3Value,
            "yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'",
            [Globalization.CultureInfo]::InvariantCulture,
            $Latest3Styles,
            [ref]$ParsedLatest3
        ) -and $ParsedLatest3.Offset -eq [TimeSpan]::Zero
    }
    if (
        [string]$Attempt3.state -cne 'foundation-stream-contract-failure' -or
        [string]$Attempt3.run_id -cne $ExpectedRun3Id -or
        [string]$Attempt3.source_commit -cne 'ff5cfac5820415662e608886f1a10d7892f3ee00' -or
        [string]$Attempt3.specification_commit -cne 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' -or
        [string]$Attempt3.plan_commit -cne '7dbd3a7576ea76beccfc64f748c4e495259ea89b' -or
        (@($Attempt3.registered_run_ids) | ConvertTo-Json -Compress) -cne
            (@($ExpectedRun3Id, $ExpectedPeer3Id) | ConvertTo-Json -Compress) -or
        (@($Attempt3.registered_image_tags) | ConvertTo-Json -Compress) -cne
            (@($ExpectedImage3Tag, $ExpectedPeer3Tag) | ConvertTo-Json -Compress) -or
        -not (& $PathListsEqual @($Attempt3.registered_paths) $ExpectedPaths3) -or
        [string]$Attempt3.owner_authorization_id -cne 'steven002' -or
        [int]$Attempt3.run_file_count -ne 60 -or
        [string]$Attempt3.run_inventory_sha256 -cne '628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2' -or
        (@($Attempt3.directory_names) | ConvertTo-Json -Compress) -cne
            ($ExpectedDirectories3 | ConvertTo-Json -Compress) -or
        (@($Attempt3.key_file_records) | ConvertTo-Json -Compress) -cne
            ($ExpectedFiles3 | ConvertTo-Json -Compress) -or
        [string]$Attempt3.image_tag -cne $ExpectedImage3Tag -or
        [string]$Attempt3.image_id -cne 'sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd' -or
        [string]$Attempt3.release_record_sha256 -cne '72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93' -or
        [string]$Attempt3.released_lease_sha256 -cne 'a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f' -or
        $Attempt3.validation_present -cne $false -or
        @($Attempt3.replica_directory_names_present).Count -ne 0 -or
        @($Attempt3.checkpoint_file_paths_present).Count -ne 0 -or
        (@($Attempt3.closure_paths_present) | ConvertTo-Json -Compress) -cne
            (@('78-failure-diagnostic.json','79-historical-preservation-final.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json') | ConvertTo-Json -Compress) -or
        -not $Latest3Valid -or
        $Attempt3.links_absent -cne $true
    ) { throw 'A11 prior A11 foundation-stream attempt drifted' }
    $ExpectedDirectories4 = @(
        'audit',
        'wave0',
        'wave0/checkpoints',
        'wave0/checkpoints/calibration-00',
        'wave0/checkpoints/calibration-01',
        'wave0/checkpoints/calibration-02',
        'wave0/checkpoints/calibration-03',
        'wave0/checkpoints/calibration-04',
        'wave0/checkpoints/calibration-05',
        'wave0/checkpoints/calibration-06',
        'wave0/checkpoints/calibration-07',
        'wave0/checkpoints/calibration-08',
        'wave0/checkpoints/calibration-09',
        'wave0/checkpoints/calibration-10',
        'wave0/checkpoints/calibration-11',
        'wave0/model_cache',
        'wave0/model_cache/snapshots',
        'wave0/model_cache/snapshots/facebook--dinov2-small',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download',
        'wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download',
        'wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees',
        'wave0/receipts'
    )
    $ExpectedFiles4 = @(
        [pscustomobject][ordered]@{ path='audit/00-identity.json'; size=2873; sha256='dce0706a572cdb5e72a8b28aad61750ee799e0eae7164ae1b5c6a0c22f1ffe4c' },
        [pscustomobject][ordered]@{ path='audit/10-build.json'; size=1234; sha256='c173d63a7428792c503a90ef095e1e8055c7ba8d7d112b54ea5a318fa1675eab' },
        [pscustomobject][ordered]@{ path='audit/11-image-inspect.json'; size=682; sha256='c355d995173db7b7600ad1dc25774f28e76f620300252f165288797c931b8b81' },
        [pscustomobject][ordered]@{ path='audit/20-cache-preflight.json'; size=1900; sha256='0c67229f0731b1e573f84a1ca3b97fb8aa2e51e4157e66c644133e2037c00273' },
        [pscustomobject][ordered]@{ path='audit/30-environment.json'; size=1995; sha256='343602c0ad150e9b6642a31d3f2304e816ae8819b706d7774371625ed7fe753c' },
        [pscustomobject][ordered]@{ path='audit/31-model-assets.json'; size=2051; sha256='e734f83f4f9149ea002982c6a48997445d71ba24b2c9424519f025dd63bbe851' },
        [pscustomobject][ordered]@{ path='audit/32-model-contract.json'; size=2232; sha256='db0bb5710a3c6cd37a68f8142d43d2e2633254eca936be00c0faceefee6cd50c' },
        [pscustomobject][ordered]@{ path='audit/60-historical-preservation.json'; size=301; sha256='927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' },
        [pscustomobject][ordered]@{ path='audit/70-phase-manifest.json'; size=9990; sha256='82122edec3b647c39946bdba6ebfa3c74d36065a084632e8d45c38b31eaaf97a' },
        [pscustomobject][ordered]@{ path='audit/71-aggregate-gate.json'; size=1287; sha256='5772642484357bdfa4b7132bdbea974092c823e1207c57b60f7aec31ce7f22f3' },
        [pscustomobject][ordered]@{ path='audit/71-aggregate-gate.stderr.log'; size=31; sha256='a336516b29c7b7fd395d6b2008409a5d8018b5d9c5616831d369cbd15078a812' },
        [pscustomobject][ordered]@{ path='audit/78-failure-diagnostic.json'; size=855; sha256='40f1163d031fc68555363980b57821f87b103fdffd0e33880f0941361ae42338' },
        [pscustomobject][ordered]@{ path='audit/79-historical-preservation-final.json'; size=301; sha256='927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' },
        [pscustomobject][ordered]@{ path='audit/80-campaign-result.json'; size=762; sha256='b4f2c8fa42384ae4791071b828f2cf0fccc9e50f9e2e69e928a8b9a583b2047e' },
        [pscustomobject][ordered]@{ path='audit/81-campaign-file-manifest.json'; size=35243; sha256='02f7a06d64969ed4ebe2bb1a575ba7308279cee5b3f3ae51663fceb676cc4eec' },
        [pscustomobject][ordered]@{ path='audit/82-campaign-closure.json'; size=660; sha256='1f65ea6261fabb007be1f15a457e2c9ff71925251c5b3af568e061890556e219' },
        [pscustomobject][ordered]@{ path='wave0/receipts/model-contract.json'; size=9623; sha256='5589eb3e64fe9727212e3467f9e3ca6979e008b31e69e5a8ace0e0919607de9d' }
    )
    $ExpectedReplicaDirectories4 = @(0..11 | ForEach-Object {
        'wave0/checkpoints/calibration-{0:D2}' -f $_
    })
    $ExpectedCheckpointFiles4 = @(0..11 | ForEach-Object {
        'wave0/checkpoints/calibration-{0:D2}/step-000001.pt' -f $_
    })
    $Attempt4 = $Attempts[3]
    $ExpectedPaths4 = @(& $BuildExpectedRegisteredPaths `
        @($ExpectedRun4Id, $ExpectedPeer4Id))
    $Latest4Text = if ($Attempt4.latest_write_utc -is [DateTime]) {
        $Attempt4.latest_write_utc.ToUniversalTime().ToString('o')
    } else {
        [string]$Attempt4.latest_write_utc
    }
    if (
        [string]$Attempt4.state -cne 'aggregate-cache-inventory-contract-failure' -or
        [string]$Attempt4.run_id -cne $ExpectedRun4Id -or
        [string]$Attempt4.source_commit -cne '77f8eecb3b8c0f471a4e980269187ac02a3b9ebc' -or
        [string]$Attempt4.specification_commit -cne 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' -or
        [string]$Attempt4.plan_commit -cne '7dbd3a7576ea76beccfc64f748c4e495259ea89b' -or
        (@($Attempt4.registered_run_ids) | ConvertTo-Json -Compress) -cne
            (@($ExpectedRun4Id, $ExpectedPeer4Id) | ConvertTo-Json -Compress) -or
        (@($Attempt4.registered_image_tags) | ConvertTo-Json -Compress) -cne
            (@($ExpectedImage4Tag, $ExpectedPeer4Tag) | ConvertTo-Json -Compress) -or
        -not (& $PathListsEqual @($Attempt4.registered_paths) $ExpectedPaths4) -or
        [string]$Attempt4.owner_authorization_id -cne 'steven003' -or
        [int]$Attempt4.run_file_count -ne 137 -or
        [string]$Attempt4.run_inventory_sha256 -cne 'f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717' -or
        (@($Attempt4.directory_names) | ConvertTo-Json -Compress) -cne
            ($ExpectedDirectories4 | ConvertTo-Json -Compress) -or
        (@($Attempt4.key_file_records) | ConvertTo-Json -Compress) -cne
            ($ExpectedFiles4 | ConvertTo-Json -Compress) -or
        [string]$Attempt4.image_tag -cne $ExpectedImage4Tag -or
        [string]$Attempt4.image_id -cne 'sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e' -or
        [string]$Attempt4.release_record_sha256 -cne 'aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1' -or
        [string]$Attempt4.released_lease_sha256 -cne 'b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c' -or
        $Attempt4.validation_present -cne $false -or
        (@($Attempt4.replica_directory_names_present) | ConvertTo-Json -Compress) -cne
            ($ExpectedReplicaDirectories4 | ConvertTo-Json -Compress) -or
        (@($Attempt4.checkpoint_file_paths_present) | ConvertTo-Json -Compress) -cne
            ($ExpectedCheckpointFiles4 | ConvertTo-Json -Compress) -or
        $Attempt4.success_receipt_present -cne $false -or
        (@($Attempt4.closure_paths_present) | ConvertTo-Json -Compress) -cne
            (@('78-failure-diagnostic.json','79-historical-preservation-final.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json') | ConvertTo-Json -Compress) -or
        $Latest4Text -cne '2026-08-29T06:13:25.1659510Z' -or
        $Attempt4.links_absent -cne $true
    ) { throw 'A11 prior A11 aggregate-cache-inventory attempt drifted' }
    $ExpectedFiles5 = @(
        [pscustomobject][ordered]@{ path='audit/00-identity.json'; size=2873; sha256='9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d' },
        [pscustomobject][ordered]@{ path='audit/01-gpu-preflight.json'; size=125; sha256='de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7' },
        [pscustomobject][ordered]@{ path='audit/10-build.json'; size=1234; sha256='3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68' },
        [pscustomobject][ordered]@{ path='audit/10-build.stderr.log'; size=865248; sha256='e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5' },
        [pscustomobject][ordered]@{ path='audit/10-build.stdout.log'; size=0; sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' },
        [pscustomobject][ordered]@{ path='audit/78-failure-diagnostic.json'; size=766; sha256='cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311' },
        [pscustomobject][ordered]@{ path='audit/79-historical-preservation-final.json'; size=301; sha256='927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' },
        [pscustomobject][ordered]@{ path='audit/80-campaign-result.json'; size=751; sha256='346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651' },
        [pscustomobject][ordered]@{ path='audit/81-campaign-file-manifest.json'; size=1885; sha256='8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6' },
        [pscustomobject][ordered]@{ path='audit/82-campaign-closure.json'; size=659; sha256='a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1' }
    )
    $ExpectedDirectories5 = @(
        'audit', 'wave0', 'wave0/checkpoints', 'wave0/model_cache',
        'wave0/receipts'
    )
    $Attempt5 = $Attempts[4]
    $ExpectedPaths5 = @(& $BuildExpectedRegisteredPaths `
        @($ExpectedRun5Id, $ExpectedPeer5Id))
    $Latest5Text = if ($Attempt5.latest_write_utc -is [DateTime]) {
        $Attempt5.latest_write_utc.ToUniversalTime().ToString('o')
    } else {
        [string]$Attempt5.latest_write_utc
    }
    if (
        [string]$Attempt5.state -cne 'image-build-failure' -or
        [string]$Attempt5.run_id -cne $ExpectedRun5Id -or
        [string]$Attempt5.source_commit -cne 'ed6f157c7cbd545895b9d047f6e094968a1f9d94' -or
        [string]$Attempt5.specification_commit -cne 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' -or
        [string]$Attempt5.plan_commit -cne '7dbd3a7576ea76beccfc64f748c4e495259ea89b' -or
        (@($Attempt5.registered_run_ids) | ConvertTo-Json -Compress) -cne
            (@($ExpectedRun5Id, $ExpectedPeer5Id) | ConvertTo-Json -Compress) -or
        (@($Attempt5.registered_image_tags) | ConvertTo-Json -Compress) -cne
            (@($ExpectedImage5Tag, $ExpectedPeer5Tag) | ConvertTo-Json -Compress) -or
        -not (& $PathListsEqual @($Attempt5.registered_paths) $ExpectedPaths5) -or
        [string]$Attempt5.owner_authorization_id -cne 'steven004' -or
        [int]$Attempt5.run_file_count -ne 10 -or
        [string]$Attempt5.run_inventory_sha256 -cne 'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64' -or
        (@($Attempt5.file_records) | ConvertTo-Json -Compress) -cne
            ($ExpectedFiles5 | ConvertTo-Json -Compress) -or
        (@($Attempt5.directory_names) | ConvertTo-Json -Compress) -cne
            ($ExpectedDirectories5 | ConvertTo-Json -Compress) -or
        @($Attempt5.image_tags_present).Count -ne 0 -or
        @($Attempt5.lease_paths_present).Count -ne 0 -or
        $Attempt5.validation_present -cne $false -or
        @($Attempt5.payload_file_paths_present).Count -ne 0 -or
        (@($Attempt5.closure_paths_present) | ConvertTo-Json -Compress) -cne
            (@('78-failure-diagnostic.json','79-historical-preservation-final.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json') | ConvertTo-Json -Compress) -or
        $Latest5Text -cne '2026-08-29T13:39:47.0148945Z' -or
        $Attempt5.links_absent -cne $true
    ) { throw 'A11 prior A11 image-build-failure attempt drifted' }
    $PriorOwners = @($Evidence.prior_a11_attempts.attempts | ForEach-Object {
        [string]$_.owner_authorization_id
    })
    if ($OwnerAuthorizationId -cin $PriorOwners) {
        throw 'A11 prior owner authorization cannot be reused'
    }
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
        [Parameter(Mandatory = $true)][ValidateCount(2, 2)][object[]]$Identities,
        [Parameter(Mandatory = $true)][ValidateCount(5, 5)][object[]]$PriorAttempts,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
    )
    $PriorRunIds = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $PriorImageTags = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $PriorOwners = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $PriorPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($Attempt in $PriorAttempts) {
        foreach ($Value in @($Attempt.registered_run_ids)) {
            [void]$PriorRunIds.Add([string]$Value)
        }
        foreach ($Value in @($Attempt.registered_image_tags)) {
            [void]$PriorImageTags.Add([string]$Value)
        }
        foreach ($Value in @($Attempt.registered_paths)) {
            [void]$PriorPaths.Add([IO.Path]::GetFullPath([string]$Value))
        }
        [void]$PriorOwners.Add([string]$Attempt.owner_authorization_id)
    }
    if ($PriorOwners.Contains($OwnerAuthorizationId)) {
        throw 'A11 prior owner authorization cannot be reused'
    }
    foreach ($Identity in $Identities) {
        if ([string]$Identity.owner_authorization_id -cne $OwnerAuthorizationId) {
            throw 'A11 phase owner authorization mismatch'
        }
        if ($PriorRunIds.Contains([string]$Identity.run_id)) {
            throw "A11 preserved run identity is reused: $($Identity.run_id)"
        }
        if ($PriorImageTags.Contains([string]$Identity.image_tag)) {
            throw "A11 preserved image identity is reused: $($Identity.image_tag)"
        }
        $LeaseRoot = [IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path)
        $CandidatePaths = @(
            [string]$Identity.campaign_root,
            [string]$Identity.cache_root,
            [string]$Identity.lease_path,
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).released"),
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).release.json"),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'audit'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'receipts'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'checkpoints')
        )
        foreach ($Path in $CandidatePaths) {
            if ($PriorPaths.Contains([IO.Path]::GetFullPath($Path))) {
                throw "A11 preserved runtime destination is reused: $Path"
            }
        }
    }
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

function New-A11ModelLoadPresentationArguments {
    return @(
        '-e', 'HF_HUB_DISABLE_PROGRESS_BARS=1',
        '-e', 'TRANSFORMERS_VERBOSITY=error'
    )
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
    $RootItem = Get-Item -LiteralPath $CacheRoot -Force -ErrorAction Stop
    if (
        -not $RootItem.PSIsContainer -or
        ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint)
    ) { throw 'A11 model cache root is invalid' }
    $ResolvedRoot = $RootItem.FullName
    $Linked = @(Get-ChildItem -LiteralPath $ResolvedRoot -Recurse -Force |
        Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($Linked.Count -ne 0) { throw 'A11 model cache contains a link' }
    $Files = [Collections.Generic.List[object]]::new()
    foreach ($Item in @(Get-ChildItem -LiteralPath $ResolvedRoot -File -Recurse -Force)) {
        $Relative = $Item.FullName.Substring($ResolvedRoot.Length).
            TrimStart([char[]]@('\', '/')).Replace('\', '/')
        $SortKey = [Text.StringBuilder]::new()
        for ($Index = 0; $Index -lt $Relative.Length;) {
            $Character = $Relative[$Index]
            if ([char]::IsHighSurrogate($Character)) {
                if (
                    $Index + 1 -ge $Relative.Length -or
                    -not [char]::IsLowSurrogate($Relative[$Index + 1])
                ) { throw 'A11 model cache path contains invalid Unicode' }
                $Scalar = [char]::ConvertToUtf32($Character, $Relative[$Index + 1])
                $Index += 2
            } elseif ([char]::IsLowSurrogate($Character)) {
                throw 'A11 model cache path contains invalid Unicode'
            } else {
                $Scalar = [int]$Character
                $Index++
            }
            [void]$SortKey.Append(
                $Scalar.ToString('X6', [Globalization.CultureInfo]::InvariantCulture)
            )
        }
        $Files.Add([pscustomobject][ordered]@{
            relative = $Relative
            sort_key = $SortKey.ToString()
            item = $Item
        })
    }
    if ($Files.Count -eq 0) { throw 'A11 model cache is empty' }
    $Files.Sort(
        [Collections.Generic.Comparer[object]]::Create(
            [Comparison[object]]{
                param($Left, $Right)
                return [StringComparer]::Ordinal.Compare(
                    [string]$Left.sort_key,
                    [string]$Right.sort_key
                )
            }
        )
    )
    $Records = @($Files | ForEach-Object {
        $Relative = [string]$_.relative
        $Item = $_.item
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'A11 model cache contains a link' }
        if (
            $Relative.EndsWith('.metadata', [StringComparison]::Ordinal) -and
            "/$Relative".Contains('/.cache/huggingface/download/', [StringComparison]::Ordinal)
        ) {
            # Bind the stable commit/ETag lines; the third line is download time.
            $Lines = [IO.File]::ReadAllLines($Item.FullName, [Text.Encoding]::UTF8)
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
            $Size = [long]$Item.Length
            $Digest = (Get-FileHash -LiteralPath $Item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
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
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8'
    ) + @(New-A11ModelLoadPresentationArguments) + @(
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
        [Parameter(Mandatory = $true)][string]$ReceiptPath,
        [switch]$SuppressModelLoadPresentation
    )
    $Worktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $ContainerRoot = "/a11/$($Identity.phase)"
    $PresentationArguments = if ($SuppressModelLoadPresentation) {
        @(New-A11ModelLoadPresentationArguments)
    } else { @() }
    $Arguments = @(
        'run', '--rm', '--gpus', 'all', '--network', 'none', '--workdir', '/workspace',
        '--entrypoint', 'val', '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'HF_HUB_OFFLINE=1', '-e', 'TRANSFORMERS_OFFLINE=1',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8'
    ) + $PresentationArguments + @(
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
        -Identity $Identity -Name '32-model-contract' `
        -SuppressModelLoadPresentation -Command @(
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
        stdout = ConvertTo-A11ContainerFileRecord $Identity `
            (Get-A11FileRecord -Path $StdoutPath)
        stderr = ConvertTo-A11ContainerFileRecord $Identity `
            (Get-A11FileRecord -Path $StderrPath)
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
    $ErrorList = [Collections.Generic.List[string]]::new()
    if (-not [string]::IsNullOrWhiteSpace($Failure)) {
        [void]$ErrorList.Add($Failure)
    }
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
        [void]$ErrorList.Add('A11 final historical preservation rehash failed')
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
            foreach ($AggregateError in @($Aggregate.normative.errors)) {
                [void]$ErrorList.Add([string]$AggregateError)
            }
        }
        if ($ErrorList.Count -eq 0) {
            [void]$ErrorList.Add('A11 normative phase failure')
        }
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
            errors = @($ErrorList.ToArray())
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
        'prior_a11_attempts', 'historical_file_count', 'historical_image_count',
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
    Test-A11PhaseDestinationsAbsent `
        -Identities @($Calibration, $Validation) `
        -PriorAttempts @($RawPreflight.prior_a11_attempts.attempts) `
        -OwnerAuthorizationId $AuthorizationId | Out-Null
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
                container_ids = @($Value.replica_records | ForEach-Object {
                    [string]$_.container_id
                })
                receipt_paths = @($Value.replica_records | ForEach-Object {
                    [string]$_.feasibility.path
                })
                receipt_hashes = @($Value.replica_records | ForEach-Object {
                    [string]$_.feasibility.sha256
                })
                checkpoint_paths = @($Value.replica_records | ForEach-Object {
                    [string]$_.checkpoint.path
                })
                checkpoint_hashes = @($Value.replica_records | ForEach-Object {
                    [string]$_.checkpoint.sha256
                })
                timestamps = @($Value.replica_records | ForEach-Object {
                    [string]$_.timestamp
                })
                audit_paths = @($Value.audit_records.Values | ForEach-Object {
                    [string]$_.path
                })
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
