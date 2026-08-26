param(
    [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedBranch,
    [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-A7BuildArguments {
    param(
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$BaseDigest,
        [Parameter(Mandatory = $true)][string]$ImageTag
    )

    $BuildArguments = [System.Collections.Generic.List[string]]::new()
    foreach ($Value in @(
            'build',
            '--no-cache',
            '--progress',
            'plain',
            '--file',
            'docker/wave0.Dockerfile'
        )) {
        [void]$BuildArguments.Add($Value)
    }
    [void]$BuildArguments.Add('--label')
    [void]$BuildArguments.Add("org.opencontainers.image.revision=$SourceCommit")
    [void]$BuildArguments.Add('--label')
    [void]$BuildArguments.Add("org.opencontainers.image.val.run_id=$RunId")
    [void]$BuildArguments.Add('--label')
    [void]$BuildArguments.Add("org.opencontainers.image.val.spec_commit=$SpecCommit")
    [void]$BuildArguments.Add('--label')
    [void]$BuildArguments.Add("org.opencontainers.image.val.plan_commit=$PlanCommit")
    [void]$BuildArguments.Add('--label')
    [void]$BuildArguments.Add("org.opencontainers.image.base.digest=$BaseDigest")
    [void]$BuildArguments.Add('--tag')
    [void]$BuildArguments.Add($ImageTag)
    [void]$BuildArguments.Add('.')
    return $BuildArguments.ToArray()
}

function Assert-A7BuildArguments {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$BaseDigest,
        [Parameter(Mandatory = $true)][string]$ImageTag
    )

    $ApprovedBaseDigest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    foreach ($Commit in @($SourceCommit, $SpecCommit, $PlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 build commit identity must be lowercase 40-hex'
        }
    }
    if ($RunId -cnotmatch '^wave0-a7-[0-9]{8}T[0-9]{9}Z$') {
        throw 'A7 build run identity is invalid'
    }
    if ($BaseDigest -cne $ApprovedBaseDigest) {
        throw 'A7 build base digest is not approved'
    }
    if ([string]::IsNullOrWhiteSpace($ImageTag) -or $ImageTag -match '\s') {
        throw 'A7 build image tag is invalid'
    }
    if (@($Arguments | Where-Object { $_ -ceq '--label' }).Count -ne 5) {
        throw 'A7 build must contain exactly five label flags'
    }
    if (@($Arguments | Where-Object { $_ -cmatch '\s+org\.opencontainers\.image\.' }).Count -ne 0) {
        throw 'A7 build contains a concatenated label assignment'
    }
    $Expected = @(New-A7BuildArguments `
            -SourceCommit $SourceCommit `
            -RunId $RunId `
            -SpecCommit $SpecCommit `
            -PlanCommit $PlanCommit `
            -BaseDigest $BaseDigest `
            -ImageTag $ImageTag)
    if ($Arguments.Count -ne $Expected.Count) {
        throw 'A7 build argument count mismatch'
    }
    for ($Index = 0; $Index -lt $Expected.Count; $Index++) {
        if ($Arguments[$Index] -cne $Expected[$Index]) {
            throw "A7 build argument mismatch at index $Index"
        }
    }
}

function Write-A7NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )

    $Target = [IO.Path]::GetFullPath($Path)
    $Parent = [IO.Path]::GetDirectoryName($Target)
    if ([string]::IsNullOrWhiteSpace($Parent) -or -not [IO.Directory]::Exists($Parent)) {
        throw 'A7 text destination parent must already exist'
    }
    $Current = [IO.DirectoryInfo]::new($Parent)
    while ($null -ne $Current) {
        if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 text destination link or junction is forbidden'
        }
        $Current = $Current.Parent
    }
    if ([IO.File]::Exists($Target) -or [IO.Directory]::Exists($Target)) {
        throw 'A7 text destination already exists'
    }
    $Encoding = [Text.UTF8Encoding]::new($false)
    $Bytes = $Encoding.GetBytes($Text)
    $Stream = [IO.File]::Open(
        $Target,
        [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write,
        [IO.FileShare]::None
    )
    try {
        $Stream.Write($Bytes, 0, $Bytes.Length)
        $Stream.Flush($true)
    }
    finally {
        $Stream.Dispose()
    }
}

function Invoke-A7Native {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [string]$WorkingDirectory = ''
    )

    $ExecutablePath = [IO.Path]::GetFullPath($Executable)
    if (-not [IO.File]::Exists($ExecutablePath)) {
        throw 'A7 native executable must be an existing file'
    }
    if ([IO.Path]::GetFullPath($StdoutPath) -ceq [IO.Path]::GetFullPath($StderrPath)) {
        throw 'A7 native stdout and stderr destinations must differ'
    }
    $StartInfo = [Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = $ExecutablePath
    $StartInfo.UseShellExecute = $false
    $StartInfo.CreateNoWindow = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $WorkingDirectoryPath = [IO.Path]::GetFullPath($WorkingDirectory)
        if (-not [IO.Directory]::Exists($WorkingDirectoryPath)) {
            throw 'A7 native working directory must exist'
        }
        $StartInfo.WorkingDirectory = $WorkingDirectoryPath
    }
    foreach ($Argument in $Arguments) {
        [void]$StartInfo.ArgumentList.Add($Argument)
    }
    $Process = [Diagnostics.Process]::Start($StartInfo)
    if ($null -eq $Process) {
        throw 'A7 native process did not start'
    }
    $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
    $StderrTask = $Process.StandardError.ReadToEndAsync()
    $Process.WaitForExit()
    $Stdout = $StdoutTask.GetAwaiter().GetResult()
    $Stderr = $StderrTask.GetAwaiter().GetResult()
    $ExitCode = $Process.ExitCode
    $Process.Dispose()
    Write-A7NewText -Path $StdoutPath -Text $Stdout
    Write-A7NewText -Path $StderrPath -Text $Stderr
    return [pscustomobject]@{
        executable = $ExecutablePath
        argv = @($Arguments)
        exit_code = $ExitCode
        stdout = $Stdout
        stderr = $Stderr
    }
}

function Assert-A7ImageInspect {
    param(
        [Parameter(Mandatory = $true)][string]$InspectJson,
        [Parameter(Mandatory = $true)][string]$ImageId,
        [Parameter(Mandatory = $true)][string]$ImageTag,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$BaseDigest
    )

    try {
        $Images = @($InspectJson | ConvertFrom-Json)
    }
    catch {
        throw 'A7 image inspect is not valid JSON'
    }
    if ($Images.Count -ne 1) {
        throw 'A7 image inspect must contain exactly one image'
    }
    $Image = $Images[0]
    if ($Image.Id -cne $ImageId -or $ImageId -cnotmatch '^sha256:[0-9a-f]{64}$') {
        throw 'A7 image ID binding mismatch'
    }
    if (@($Image.RepoTags | Where-Object { $_ -ceq $ImageTag }).Count -ne 1) {
        throw 'A7 image tag binding mismatch'
    }
    if ($null -eq $Image.Config -or $null -eq $Image.Config.Labels) {
        throw 'A7 image labels are missing'
    }
    $ExpectedLabels = [ordered]@{
        'org.opencontainers.image.revision' = $SourceCommit
        'org.opencontainers.image.val.run_id' = $RunId
        'org.opencontainers.image.val.spec_commit' = $SpecCommit
        'org.opencontainers.image.val.plan_commit' = $PlanCommit
        'org.opencontainers.image.base.digest' = $BaseDigest
    }
    foreach ($Key in $ExpectedLabels.Keys) {
        $Property = $Image.Config.Labels.PSObject.Properties[$Key]
        if ($null -eq $Property -or $Property.Value -cne $ExpectedLabels[$Key]) {
            throw "A7 image label binding mismatch: $Key"
        }
        if ([string]$Property.Value -cmatch '\s+org\.opencontainers\.image\.') {
            throw "A7 image label contains a concatenated assignment: $Key"
        }
    }
}

function Resolve-A7Worktree {
    param(
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedBranch,
        [Parameter(Mandatory = $true)][string]$ExpectedHead
    )

    if ($ExpectedHead -cnotmatch '^[0-9a-f]{40}$') {
        throw 'A7 expected Git HEAD must be lowercase 40-hex'
    }
    if ([string]::IsNullOrWhiteSpace($ExpectedBranch) -or $ExpectedBranch -match '\s') {
        throw 'A7 expected Git branch is invalid'
    }
    $RepositoryPath = [IO.Path]::GetFullPath($RepositoryRoot)
    if (-not [IO.Directory]::Exists($RepositoryPath)) {
        throw 'A7 repository root does not exist'
    }

    $InvokeGit = {
        param(
            [Parameter(Mandatory = $true)][string]$WorkingDirectory,
            [Parameter(Mandatory = $true)][string[]]$Arguments
        )

        $StartInfo = [Diagnostics.ProcessStartInfo]::new()
        $StartInfo.FileName = 'git'
        $StartInfo.WorkingDirectory = $WorkingDirectory
        $StartInfo.UseShellExecute = $false
        $StartInfo.CreateNoWindow = $true
        $StartInfo.RedirectStandardOutput = $true
        $StartInfo.RedirectStandardError = $true
        foreach ($Argument in $Arguments) {
            [void]$StartInfo.ArgumentList.Add($Argument)
        }
        $Process = [Diagnostics.Process]::Start($StartInfo)
        if ($null -eq $Process) {
            throw 'A7 Git process did not start'
        }
        $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
        $StderrTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        $Stdout = $StdoutTask.GetAwaiter().GetResult()
        $Stderr = $StderrTask.GetAwaiter().GetResult()
        $ExitCode = $Process.ExitCode
        $Process.Dispose()
        if ($ExitCode -ne 0) {
            throw "A7 Git command failed: $Stderr"
        }
        return $Stdout
    }

    $CanonicalRootText = (& $InvokeGit $RepositoryPath @('rev-parse', '--show-toplevel')).Trim()
    $CanonicalRoot = [IO.Path]::GetFullPath($CanonicalRootText)
    if ($CanonicalRoot -cne $RepositoryPath) {
        throw 'A7 repository root must be the canonical worktree root'
    }

    $Porcelain = & $InvokeGit $CanonicalRoot @('worktree', 'list', '--porcelain')
    $Records = [System.Collections.Generic.List[object]]::new()
    $Current = $null
    foreach ($Line in ($Porcelain -split "`r?`n")) {
        if ($Line.StartsWith('worktree ')) {
            if ($null -ne $Current) {
                [void]$Records.Add($Current)
            }
            $Current = [ordered]@{
                worktree = $Line.Substring(9)
                head = $null
                branch = $null
            }
        }
        elseif ($null -ne $Current -and $Line.StartsWith('HEAD ')) {
            $Current.head = $Line.Substring(5)
        }
        elseif ($null -ne $Current -and $Line.StartsWith('branch ')) {
            $Current.branch = $Line.Substring(7)
        }
    }
    if ($null -ne $Current) {
        [void]$Records.Add($Current)
    }
    $ExpectedBranchRef = "refs/heads/$ExpectedBranch"
    $Matches = @($Records | Where-Object {
            $_.head -ceq $ExpectedHead -and $_.branch -ceq $ExpectedBranchRef
        })
    if ($Matches.Count -ne 1) {
        throw 'A7 expected registered worktree identity is not unique'
    }
    $WorktreePath = [IO.Path]::GetFullPath([string]$Matches[0].worktree)
    if (-not [IO.Directory]::Exists($WorktreePath)) {
        throw 'A7 registered worktree does not exist'
    }

    $CanonicalCommonText = (& $InvokeGit $CanonicalRoot @('rev-parse', '--git-common-dir')).Trim()
    if (-not [IO.Path]::IsPathRooted($CanonicalCommonText)) {
        $CanonicalCommonText = [IO.Path]::Combine($CanonicalRoot, $CanonicalCommonText)
    }
    $CanonicalCommon = [IO.Path]::GetFullPath($CanonicalCommonText)
    $LinkedCommonText = (& $InvokeGit $WorktreePath @('rev-parse', '--git-common-dir')).Trim()
    if (-not [IO.Path]::IsPathRooted($LinkedCommonText)) {
        $LinkedCommonText = [IO.Path]::Combine($WorktreePath, $LinkedCommonText)
    }
    $LinkedCommon = [IO.Path]::GetFullPath($LinkedCommonText)
    if ($LinkedCommon -cne $CanonicalCommon) {
        throw 'A7 linked worktree Git common-dir mismatch'
    }

    $ActualHead = (& $InvokeGit $WorktreePath @('rev-parse', 'HEAD')).Trim()
    $ActualBranch = (& $InvokeGit $WorktreePath @('branch', '--show-current')).Trim()
    if ($ActualHead -cne $ExpectedHead -or $ActualBranch -cne $ExpectedBranch) {
        throw 'A7 linked worktree Git identity changed during validation'
    }
    $LinkedStatus = & $InvokeGit $WorktreePath @('status', '--porcelain=v1')
    if (-not [string]::IsNullOrEmpty($LinkedStatus)) {
        throw 'A7 linked worktree must be clean'
    }
    $CanonicalStatus = & $InvokeGit $CanonicalRoot @('status', '--porcelain=v1')
    if (-not [string]::IsNullOrEmpty($CanonicalStatus)) {
        throw 'A7 canonical worktree must be clean'
    }
    $StagedPaths = & $InvokeGit $WorktreePath @('diff', '--cached', '--name-only')
    if (-not [string]::IsNullOrEmpty($StagedPaths)) {
        throw 'A7 linked worktree staging area must be empty'
    }

    return [pscustomobject]@{
        worktree = $WorktreePath
        canonical_root = $CanonicalRoot
        common_dir = $CanonicalCommon
        branch = $ActualBranch
        head = $ActualHead
    }
}

function New-A7AugmentedBaseline {
    param(
        [Parameter(Mandatory = $true)][string]$OriginalBaselinePath,
        [Parameter(Mandatory = $true)][string]$ExpectedBaselineSha256,
        [Parameter(Mandatory = $true)][string]$ArtifactRoot,
        [Parameter(Mandatory = $true)][string]$ProtectedGitRoot,
        [Parameter(Mandatory = $true)][string]$ImageRecordsJson,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$GitExecutable,
        [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
        [Parameter(Mandatory = $true)][string]$OutputPath
    )

    if ($ExpectedBaselineSha256 -cnotmatch '^[0-9a-f]{64}$') {
        throw 'A7 expected baseline SHA-256 is invalid'
    }
    if ($SourceCommit -cnotmatch '^[0-9a-f]{40}$') {
        throw 'A7 augmented baseline source commit is invalid'
    }
    foreach ($Commit in @($ExpectedSpecCommit, $ExpectedPlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 augmented baseline spec or plan commit is invalid'
        }
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $Stream = [IO.File]::Open(
            $Path,
            [IO.FileMode]::Open,
            [IO.FileAccess]::Read,
            [IO.FileShare]::Read
        )
        try {
            $Hasher = [Security.Cryptography.SHA256]::Create()
            try {
                return [Convert]::ToHexString($Hasher.ComputeHash($Stream)).ToLowerInvariant()
            }
            finally {
                $Hasher.Dispose()
            }
        }
        finally {
            $Stream.Dispose()
        }
    }
    $AssertRegularAncestors = {
        param(
            [Parameter(Mandatory = $true)][string]$Path,
            [Parameter(Mandatory = $true)][bool]$RequireFile
        )
        $FullPath = [IO.Path]::GetFullPath($Path)
        if ($RequireFile) {
            if (-not [IO.File]::Exists($FullPath) -or [IO.Directory]::Exists($FullPath)) {
                throw 'A7 required regular file is missing'
            }
            $Current = [IO.FileInfo]::new($FullPath)
        }
        else {
            if (-not [IO.Directory]::Exists($FullPath)) {
                throw 'A7 required directory is missing'
            }
            $Current = [IO.DirectoryInfo]::new($FullPath)
        }
        while ($null -ne $Current) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 history path link or junction is forbidden'
            }
            $Current = $Current.Parent
        }
        return $FullPath
    }
    $NormalizeRelative = {
        param(
            [Parameter(Mandatory = $true)][string]$Root,
            [Parameter(Mandatory = $true)][string]$RelativePath
        )
        if (
            [string]::IsNullOrWhiteSpace($RelativePath) -or
            [IO.Path]::IsPathRooted($RelativePath) -or
            $RelativePath.Contains('\')
        ) {
            throw 'A7 history relative path is invalid'
        }
        $RootPrefix = $Root.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
        $Combined = [IO.Path]::GetFullPath(
            [IO.Path]::Combine($Root, $RelativePath.Replace('/', [IO.Path]::DirectorySeparatorChar))
        )
        if (-not $Combined.StartsWith($RootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'A7 history relative path escapes its root'
        }
        return $Combined
    }
    $GitFile = [IO.FileInfo]::new([IO.Path]::GetFullPath($GitExecutable))
    if (
        -not $GitFile.Exists -or
        ($GitFile.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
    ) {
        throw 'A7 Git executable is missing or linked'
    }
    $InvokeGit = {
        param([Parameter(Mandatory = $true)][string[]]$Arguments)
        $Output = @(& $GitFile.FullName @Arguments 2>&1)
        if ($LASTEXITCODE -ne 0) {
            throw "A7 protected Git command failed: $($Output -join '; ')"
        }
        return ($Output -join "`n").Trim()
    }

    $BaselinePath = & $AssertRegularAncestors $OriginalBaselinePath $true
    if ((& $GetSha256 $BaselinePath) -cne $ExpectedBaselineSha256) {
        throw 'A7 original baseline SHA-256 mismatch'
    }
    try {
        $Baseline = [IO.File]::ReadAllText($BaselinePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    catch {
        throw 'A7 original baseline is not valid JSON'
    }
    if (
        $Baseline.schema_version -ne 1 -or
        [string]$Baseline.parent_baseline_sha256 -cnotmatch '^[0-9a-f]{64}$'
    ) {
        throw 'A7 original baseline identity is invalid'
    }
    $ArtifactRootPath = & $AssertRegularAncestors $ArtifactRoot $false
    $ProtectedRootPath = & $AssertRegularAncestors $ProtectedGitRoot $false
    if ([IO.Path]::GetFullPath([string]$Baseline.artifact_root) -cne $ArtifactRootPath) {
        throw 'A7 original baseline artifact root mismatch'
    }
    $OutputFullPath = [IO.Path]::GetFullPath($OutputPath)
    $ArtifactPrefix = $ArtifactRootPath.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if ($OutputFullPath.StartsWith($ArtifactPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'A7 augmented baseline must be outside the artifact root'
    }

    $CurrentArtifactRecords = [System.Collections.Generic.List[object]]::new()
    $PendingDirectories = [System.Collections.Generic.Stack[IO.DirectoryInfo]]::new()
    $PendingDirectories.Push([IO.DirectoryInfo]::new($ArtifactRootPath))
    while ($PendingDirectories.Count -gt 0) {
        $Directory = $PendingDirectories.Pop()
        if (($Directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 artifact directory link or junction is forbidden'
        }
        foreach ($ChildDirectory in $Directory.EnumerateDirectories()) {
            $PendingDirectories.Push($ChildDirectory)
        }
        foreach ($File in $Directory.EnumerateFiles()) {
            if (($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 artifact file link is forbidden'
            }
            $RelativePath = [IO.Path]::GetRelativePath($ArtifactRootPath, $File.FullName).Replace('\', '/')
            [void]$CurrentArtifactRecords.Add([pscustomobject][ordered]@{
                    path = $RelativePath
                    size = [long]$File.Length
                    sha256 = & $GetSha256 $File.FullName
                })
        }
    }
    $CurrentArtifactRecords = @($CurrentArtifactRecords | Sort-Object -CaseSensitive path)
    $CurrentByPath = @{}
    foreach ($Record in $CurrentArtifactRecords) {
        if ($CurrentByPath.ContainsKey([string]$Record.path)) {
            throw 'A7 current artifact inventory contains duplicate paths'
        }
        $CurrentByPath[[string]$Record.path] = $Record
    }

    $OriginalArtifactPaths = @{}
    foreach ($Record in @($Baseline.artifact_files)) {
        $RelativePath = [string]$Record.path
        [void](& $NormalizeRelative $ArtifactRootPath $RelativePath)
        if (
            $OriginalArtifactPaths.ContainsKey($RelativePath) -or
            [string]$Record.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            $null -eq $Record.size -or [long]$Record.size -lt 0
        ) {
            throw 'A7 original artifact record is invalid or duplicated'
        }
        $OriginalArtifactPaths[$RelativePath] = $true
        if (-not $CurrentByPath.ContainsKey($RelativePath)) {
            throw 'A7 original artifact is missing from current history'
        }
        $CurrentRecord = $CurrentByPath[$RelativePath]
        if (
            [long]$CurrentRecord.size -ne [long]$Record.size -or
            [string]$CurrentRecord.sha256 -cne [string]$Record.sha256
        ) {
            throw 'A7 original artifact history drift detected'
        }
    }

    try {
        $CurrentImages = @($ImageRecordsJson | ConvertFrom-Json)
    }
    catch {
        throw 'A7 current image inventory is not valid JSON'
    }
    $CurrentImageRecords = [System.Collections.Generic.List[object]]::new()
    $CurrentImagesByTag = @{}
    foreach ($Image in $CurrentImages) {
        $Tag = [string]$Image.tag
        $ImageId = [string]$Image.image_id
        if (
            [string]::IsNullOrWhiteSpace($Tag) -or $Tag -match '\s' -or
            $ImageId -cnotmatch '^sha256:[0-9a-f]{64}$' -or
            $CurrentImagesByTag.ContainsKey($Tag)
        ) {
            throw 'A7 current image inventory is invalid or duplicated'
        }
        $Record = [pscustomobject][ordered]@{ tag = $Tag; image_id = $ImageId }
        $CurrentImagesByTag[$Tag] = $Record
        [void]$CurrentImageRecords.Add($Record)
    }
    $OriginalImageTags = @{}
    foreach ($Image in @($Baseline.images)) {
        $Tag = [string]$Image.tag
        $ImageId = [string]$Image.image_id
        if (
            [string]::IsNullOrWhiteSpace($Tag) -or
            $ImageId -cnotmatch '^sha256:[0-9a-f]{64}$' -or
            $OriginalImageTags.ContainsKey($Tag)
        ) {
            throw 'A7 original image inventory is invalid or duplicated'
        }
        $OriginalImageTags[$Tag] = $true
        if (
            -not $CurrentImagesByTag.ContainsKey($Tag) -or
            [string]$CurrentImagesByTag[$Tag].image_id -cne $ImageId
        ) {
            throw 'A7 original image identity drift detected'
        }
    }
    $CurrentImageRecords = @($CurrentImageRecords | Sort-Object -CaseSensitive tag)

    $TransitionPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
    $PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
    $TransitionReason = 'owner-approved-design-amendment'
    if ((& $InvokeGit @('-C', $ProtectedRootPath, 'rev-parse', 'HEAD')) -cne $SourceCommit) {
        throw 'A7 protected Git HEAD does not equal the reviewed source commit'
    }
    if (-not [string]::IsNullOrEmpty([string](& $InvokeGit @(
                    '-C', $ProtectedRootPath, 'status', '--porcelain=v1'
                )))) {
        throw 'A7 protected Git worktree or index is dirty'
    }
    if ((& $InvokeGit @('-C', $ProtectedRootPath, 'rev-parse', "$ExpectedPlanCommit^")) -cne $ExpectedSpecCommit) {
        throw 'A7 protected Git plan is not the direct child of the specification'
    }
    if ((& $InvokeGit @(
                '-C', $ProtectedRootPath, 'log', '-1', '--format=%H', '--', $TransitionPath
            )) -cne $ExpectedSpecCommit) {
        throw 'A7 protected Git specification lineage mismatch'
    }
    if ((& $InvokeGit @(
                '-C', $ProtectedRootPath, 'log', '-1', '--format=%H', '--', $PlanPath
            )) -cne $ExpectedPlanCommit) {
        throw 'A7 protected Git plan lineage mismatch'
    }
    $SpecCommitFiles = @((& $InvokeGit @(
                    '-C', $ProtectedRootPath, 'diff-tree', '--no-commit-id', '--name-only',
                    '-r', $ExpectedSpecCommit
                )) -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($SpecCommitFiles.Count -ne 1 -or $SpecCommitFiles[0] -cne $TransitionPath) {
        throw 'A7 protected Git specification commit scope mismatch'
    }
    $PlanCommitFiles = @((& $InvokeGit @(
                    '-C', $ProtectedRootPath, 'diff-tree', '--no-commit-id', '--name-only',
                    '-r', $ExpectedPlanCommit
                )) -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($PlanCommitFiles.Count -ne 1 -or $PlanCommitFiles[0] -cne $PlanPath) {
        throw 'A7 protected Git plan commit scope mismatch'
    }

    $RootProtectedRecords = @($Baseline.protected_git)
    if ($RootProtectedRecords.Count -ne 68) {
        throw 'A7 protected Git root inventory must contain exactly 68 records'
    }
    $RootProtectedJson = ConvertTo-Json -InputObject $RootProtectedRecords -Depth 6 -Compress
    $RootPaths = @($RootProtectedRecords | ForEach-Object { [string]$_.path })
    $SortedRootPaths = @($RootPaths | Sort-Object -CaseSensitive)
    if (($RootPaths -join "`n") -cne ($SortedRootPaths -join "`n")) {
        throw 'A7 protected Git root inventory is not sorted'
    }
    $CurrentProtectedRecords = [System.Collections.Generic.List[object]]::new()
    $ProtectedPaths = @{}
    $TransitionRootRecord = $null
    $TransitionCurrentRecord = $null
    foreach ($Record in $RootProtectedRecords) {
        $Properties = @($Record.PSObject.Properties.Name | Sort-Object -CaseSensitive)
        $RelativePath = [string]$Record.path
        $FullPath = & $NormalizeRelative $ProtectedRootPath $RelativePath
        if (
            ($Properties -join '|') -cne 'path|sha256|size' -or
            $ProtectedPaths.ContainsKey($RelativePath) -or
            [string]$Record.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            $null -eq $Record.size -or [long]$Record.size -lt 0
        ) {
            throw 'A7 protected Git root record is invalid or duplicated'
        }
        $ProtectedPaths[$RelativePath] = $true
        [void](& $AssertRegularAncestors $FullPath $true)
        $File = [IO.FileInfo]::new($FullPath)
        $ActualHash = & $GetSha256 $FullPath
        $CurrentRecord = [pscustomobject][ordered]@{
            path = $RelativePath
            size = [long]$File.Length
            sha256 = $ActualHash
        }
        [void]$CurrentProtectedRecords.Add($CurrentRecord)
        if ($RelativePath -ceq $TransitionPath) {
            $TransitionRootRecord = $Record
            $TransitionCurrentRecord = $CurrentRecord
        }
        elseif (
            [long]$File.Length -ne [long]$Record.size -or
            $ActualHash -cne [string]$Record.sha256
        ) {
            throw "A7 unapproved protected Git drift detected: $RelativePath"
        }
    }
    if ($null -eq $TransitionRootRecord -or $null -eq $TransitionCurrentRecord) {
        throw 'A7 approved protected Git transition path is missing'
    }
    if (
        [long]$TransitionRootRecord.size -eq [long]$TransitionCurrentRecord.size -and
        [string]$TransitionRootRecord.sha256 -ceq [string]$TransitionCurrentRecord.sha256
    ) {
        throw 'A7 approved protected Git transition did not change identity'
    }
    $TransitionFullPath = & $NormalizeRelative $ProtectedRootPath $TransitionPath
    $SpecGitObject = & $InvokeGit @(
        '-C', $ProtectedRootPath, 'rev-parse', "${ExpectedSpecCommit}:$TransitionPath"
    )
    if ($SpecGitObject -cnotmatch '^[0-9a-f]{40}$') {
        throw 'A7 protected Git specification object is invalid'
    }
    $CheckoutGitObject = & $InvokeGit @(
        '-C', $ProtectedRootPath, 'hash-object', "--path=$TransitionPath", '--', $TransitionFullPath
    )
    if ($CheckoutGitObject -cne $SpecGitObject) {
        throw 'A7 protected Git checkout does not equal the approved specification object'
    }
    $CurrentProtectedRecords = @($CurrentProtectedRecords | Sort-Object -CaseSensitive path)
    $Transition = [pscustomobject][ordered]@{
        path = $TransitionPath
        root_size = [long]$TransitionRootRecord.size
        root_sha256 = [string]$TransitionRootRecord.sha256
        current_size = [long]$TransitionCurrentRecord.size
        current_sha256 = [string]$TransitionCurrentRecord.sha256
        spec_commit = $ExpectedSpecCommit
        spec_git_object = $SpecGitObject
        plan_commit = $ExpectedPlanCommit
        reason = $TransitionReason
    }

    $Document = [ordered]@{
        schema_version = 1
        source_commit = $SourceCommit
        parent_baseline_sha256 = [string]$Baseline.parent_baseline_sha256
        artifact_root = $ArtifactRootPath
        artifact_files = @($CurrentArtifactRecords)
        images = @($CurrentImageRecords)
        protected_git = @($RootProtectedRecords)
        current_protected_git = @($CurrentProtectedRecords)
        approved_protected_git_transitions = @($Transition)
    }
    $Json = $Document | ConvertTo-Json -Depth 6 -Compress
    Write-A7NewText -Path $OutputFullPath -Text $Json
    try {
        $Published = [IO.File]::ReadAllText($OutputFullPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    catch {
        throw 'A7 published augmented baseline did not parse back'
    }
    if (
        @($Published.artifact_files).Count -ne $CurrentArtifactRecords.Count -or
        @($Published.images).Count -ne $CurrentImageRecords.Count -or
        @($Published.protected_git).Count -ne 68 -or
        @($Published.current_protected_git).Count -ne 68 -or
        @($Published.approved_protected_git_transitions).Count -ne 1
    ) {
        throw 'A7 published augmented baseline count mismatch'
    }
    if (
        (ConvertTo-Json -InputObject @($Published.protected_git) -Depth 6 -Compress) -cne $RootProtectedJson -or
        (ConvertTo-Json -InputObject @($Published.current_protected_git) -Depth 6 -Compress) -cne
            (ConvertTo-Json -InputObject @($CurrentProtectedRecords) -Depth 6 -Compress) -or
        (ConvertTo-Json -InputObject @($Published.approved_protected_git_transitions) -Depth 6 -Compress) -cne
            (ConvertTo-Json -InputObject @($Transition) -Depth 6 -Compress)
    ) {
        throw 'A7 published protected Git structures changed during publication'
    }
    return [pscustomobject]@{
        path = $OutputFullPath
        sha256 = & $GetSha256 $OutputFullPath
        artifact_count = $CurrentArtifactRecords.Count
        image_count = $CurrentImageRecords.Count
        protected_git_count = $RootProtectedRecords.Count
        current_protected_git_count = $CurrentProtectedRecords.Count
        approved_protected_git_transition_count = 1
        parent_baseline_sha256 = [string]$Baseline.parent_baseline_sha256
    }
}

function Select-A7ProjectContainers {
    param(
        [Parameter(Mandatory = $true)][string]$ContainerRecordsJson,
        [Parameter(Mandatory = $true)][string]$RegisteredImageIdsJson
    )
    try {
        $Records = @($ContainerRecordsJson | ConvertFrom-Json)
        $RegisteredImageIds = @($RegisteredImageIdsJson | ConvertFrom-Json)
    }
    catch {
        throw 'A7 project-container inventory JSON is invalid'
    }
    $Registered = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($ImageId in $RegisteredImageIds) {
        $Value = [string]$ImageId
        if ($Value -cnotmatch '^sha256:[0-9a-f]{64}$' -or -not $Registered.Add($Value)) {
            throw 'A7 registered image ID is invalid or duplicated'
        }
    }
    $SeenContainers = [System.Collections.Generic.HashSet[string]]::new(
        [System.StringComparer]::Ordinal
    )
    $Selected = [System.Collections.Generic.List[object]]::new()
    foreach ($Record in $Records) {
        $Properties = @($Record.PSObject.Properties.Name | Sort-Object -CaseSensitive)
        if (($Properties -join '|') -cne 'configured_image|id|image_id|name') {
            throw 'A7 project-container record property set is not closed'
        }
        $ContainerId = [string]$Record.id
        $Name = [string]$Record.name
        $ConfiguredImage = [string]$Record.configured_image
        $ImageId = [string]$Record.image_id
        if ($ContainerId -cnotmatch '^[0-9a-f]{64}$' -or
            -not $SeenContainers.Add($ContainerId) -or
            [string]::IsNullOrWhiteSpace($Name) -or $Name.StartsWith('/') -or
            [string]::IsNullOrWhiteSpace($ConfiguredImage) -or $ConfiguredImage -match '\s' -or
            $ImageId -cnotmatch '^sha256:[0-9a-f]{64}$') {
            throw 'A7 project-container record is invalid or duplicated'
        }
        if ($Name.StartsWith('val-a7-', [StringComparison]::Ordinal) -or
            $Name.StartsWith('val-wave0-', [StringComparison]::Ordinal) -or
            $ConfiguredImage.StartsWith(
                'vision-active-learning-loop:wave0-',
                [StringComparison]::Ordinal
            ) -or $Registered.Contains($ImageId)) {
            [void]$Selected.Add([pscustomobject][ordered]@{
                    id = $ContainerId
                    name = $Name
                    configured_image = $ConfiguredImage
                    image_id = $ImageId
                })
        }
    }
    return @($Selected)
}

function Test-A7DockerGpuPreflight {
    param(
        [Parameter(Mandatory = $true)][string]$DockerContext,
        [Parameter(Mandatory = $true)][string]$DockerVersionJson,
        [Parameter(Mandatory = $true)][string]$DockerInfoJson,
        [Parameter(Mandatory = $true)][string]$DockerDesktopWslState,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$DockerGpuCsv,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$HostComputeCsv,
        [Parameter(Mandatory = $true)][string]$ProjectContainersJson,
        [Parameter(Mandatory = $true)][string]$ActiveLeasePathsJson,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$ValDataRoot
    )

    if ($DockerContext.Trim() -cne 'desktop-linux') {
        throw 'A7 Docker context must remain desktop-linux'
    }
    try {
        $Version = $DockerVersionJson | ConvertFrom-Json
        $Info = $DockerInfoJson | ConvertFrom-Json
        $Containers = @($ProjectContainersJson | ConvertFrom-Json)
        $ActiveLeases = @($ActiveLeasePathsJson | ConvertFrom-Json)
    }
    catch {
        throw 'A7 Docker preflight collector JSON is invalid'
    }
    if ($null -eq $Version.Client -or $null -eq $Version.Server) {
        throw 'A7 Docker client and server identities are required'
    }
    if ([string]$Version.Server.Os -cne 'linux' -or [string]$Info.OSType -cne 'linux') {
        throw 'A7 Docker Linux server health is required'
    }
    if ($DockerDesktopWslState.Trim() -cne 'Running') {
        throw 'A7 docker-desktop WSL backend must be Running'
    }
    if (-not [string]::IsNullOrEmpty($ValDataRoot)) {
        throw 'A7 VAL_DATA_ROOT must be unset'
    }
    if ($Containers.Count -ne 0) {
        throw 'A7 active project containers are forbidden'
    }
    if ($ActiveLeases.Count -ne 0) {
        throw 'A7 active project GPU leases are forbidden'
    }

    $GpuLines = @($DockerGpuCsv -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($GpuLines.Count -ne 1) {
        throw 'A7 Docker must expose exactly one GPU CSV row'
    }
    $GpuFields = @($GpuLines[0].Split(',') | ForEach-Object { $_.Trim() })
    if ($GpuFields.Count -ne 5) {
        throw 'A7 Docker GPU CSV shape is invalid'
    }
    $GpuUuid = $GpuFields[0]
    $GpuName = $GpuFields[1]
    if ($GpuUuid -cnotmatch '^GPU-[A-Za-z0-9-]+$') {
        throw 'A7 Docker GPU UUID is invalid'
    }
    if ($GpuName -cne 'NVIDIA GeForce RTX 4090') {
        throw 'A7 Docker GPU name is not the approved RTX 4090'
    }
    $MemoryTotal = [long]0
    $MemoryUsed = [long]0
    $MemoryFree = [long]0
    if (
        -not [long]::TryParse($GpuFields[2], [ref]$MemoryTotal) -or
        -not [long]::TryParse($GpuFields[3], [ref]$MemoryUsed) -or
        -not [long]::TryParse($GpuFields[4], [ref]$MemoryFree) -or
        $MemoryTotal -le 0 -or $MemoryUsed -lt 0 -or $MemoryFree -lt 0
    ) {
        throw 'A7 Docker GPU memory inventory is invalid'
    }

    $HostProcesses = [System.Collections.Generic.List[object]]::new()
    $ComputeLines = @($HostComputeCsv -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    foreach ($Line in $ComputeLines) {
        $Fields = @($Line.Split(',') | ForEach-Object { $_.Trim() })
        if ($Fields.Count -ne 4 -or $Fields[0] -cne $GpuUuid) {
            throw 'A7 host compute-process inventory is invalid'
        }
        $PidValue = [long]0
        if (-not [long]::TryParse($Fields[1], [ref]$PidValue) -or $PidValue -le 0) {
            throw 'A7 host compute-process PID is invalid'
        }
        $NumericMemory = [long]0
        if ([long]::TryParse($Fields[3], [ref]$NumericMemory)) {
            throw 'A7 numeric CUDA compute-process memory indicates GPU contention'
        }
        if ($Fields[3] -cne '[N/A]') {
            throw 'A7 host compute-process memory state is invalid'
        }
        [void]$HostProcesses.Add([pscustomobject][ordered]@{
                gpu_uuid = $GpuUuid
                pid = $PidValue
                process_name = $Fields[2]
                used_gpu_memory_mib = $null
            })
    }
    return [pscustomobject][ordered]@{
        docker_context = 'desktop-linux'
        server_os = 'linux'
        docker_desktop_wsl_state = 'Running'
        gpu_uuid = $GpuUuid
        gpu_name = $GpuName
        memory_total_mib = $MemoryTotal
        memory_used_mib = $MemoryUsed
        memory_free_mib = $MemoryFree
        host_processes = @($HostProcesses)
        containers = @($Containers)
    }
}

function New-A7Lease {
    param(
        [Parameter(Mandatory = $true)][string]$LeasePath,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$ImageTag,
        [Parameter(Mandatory = $true)][string]$ImageId,
        [Parameter(Mandatory = $true)][string]$BaseImageDigest,
        [Parameter(Mandatory = $true)][string]$GpuUuid,
        [Parameter(Mandatory = $true)][string]$CampaignRoot,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselinePath,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselineSha256,
        [Parameter(Mandatory = $true)][string]$BuildAuditPath,
        [Parameter(Mandatory = $true)][string]$BuildAuditSha256,
        [Parameter(Mandatory = $true)][string]$MicrocheckAuditPath,
        [Parameter(Mandatory = $true)][string]$MicrocheckAuditSha256,
        [Parameter(Mandatory = $true)][string]$HostProcessesJson,
        [Parameter(Mandatory = $true)][string]$ContainersJson,
        [Parameter(Mandatory = $true)][string]$ClaimedAt
    )

    $ApprovedBaseDigest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    if ([string]::IsNullOrWhiteSpace($OwnerAuthorizationId)) {
        throw 'A7 lease owner authorization ID is required'
    }
    if ($RunId -cnotmatch '^wave0-a7-[0-9]{8}T[0-9]{9}Z$') {
        throw 'A7 lease run ID is invalid'
    }
    foreach ($Commit in @($SourceCommit, $SpecCommit, $PlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 lease commit identity is invalid'
        }
    }
    if ([string]::IsNullOrWhiteSpace($Branch)) {
        throw 'A7 lease branch identity is required'
    }
    if ([string]::IsNullOrWhiteSpace($ImageTag) -or $ImageTag -match '\s') {
        throw 'A7 lease image tag is invalid'
    }
    if ($ImageId -cnotmatch '^sha256:[0-9a-f]{64}$') {
        throw 'A7 lease image ID is invalid'
    }
    if ($BaseImageDigest -cne $ApprovedBaseDigest) {
        throw 'A7 lease base image digest is not approved'
    }
    if ($GpuUuid -cnotmatch '^GPU-[A-Za-z0-9-]+$') {
        throw 'A7 lease GPU UUID is invalid'
    }
    foreach ($Digest in @($HistoricalBaselineSha256, $BuildAuditSha256, $MicrocheckAuditSha256)) {
        if ($Digest -cnotmatch '^[0-9a-f]{64}$') {
            throw 'A7 lease audit SHA-256 identity is invalid'
        }
    }
    if ($ClaimedAt -cnotmatch '^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z$') {
        throw 'A7 lease claimed-at timestamp is invalid'
    }

    $AssertRegularPath = {
        param(
            [Parameter(Mandatory = $true)][string]$Path,
            [Parameter(Mandatory = $true)][bool]$RequireFile
        )
        $FullPath = [IO.Path]::GetFullPath($Path)
        if ($RequireFile) {
            if (-not [IO.File]::Exists($FullPath) -or [IO.Directory]::Exists($FullPath)) {
                throw 'A7 lease-bound audit file is missing'
            }
            $Current = [IO.FileInfo]::new($FullPath)
        }
        else {
            if (-not [IO.Directory]::Exists($FullPath)) {
                throw 'A7 lease-bound campaign root is missing'
            }
            $Current = [IO.DirectoryInfo]::new($FullPath)
        }
        while ($null -ne $Current) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 lease-bound link or junction is forbidden'
            }
            $Current = $Current.Parent
        }
        return $FullPath
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $Stream = [IO.File]::OpenRead($Path)
        try {
            $Hasher = [Security.Cryptography.SHA256]::Create()
            try {
                return [Convert]::ToHexString($Hasher.ComputeHash($Stream)).ToLowerInvariant()
            }
            finally {
                $Hasher.Dispose()
            }
        }
        finally {
            $Stream.Dispose()
        }
    }
    $CampaignRootPath = & $AssertRegularPath $CampaignRoot $false
    $HistoricalPath = & $AssertRegularPath $HistoricalBaselinePath $true
    $BuildPath = & $AssertRegularPath $BuildAuditPath $true
    $MicrocheckPath = & $AssertRegularPath $MicrocheckAuditPath $true
    $CampaignPrefix = $CampaignRootPath.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if (
        -not $BuildPath.StartsWith($CampaignPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not $MicrocheckPath.StartsWith($CampaignPrefix, [StringComparison]::OrdinalIgnoreCase)
    ) {
        throw 'A7 build and micro-check audits must be inside the campaign root'
    }
    if (
        (& $GetSha256 $HistoricalPath) -cne $HistoricalBaselineSha256 -or
        (& $GetSha256 $BuildPath) -cne $BuildAuditSha256 -or
        (& $GetSha256 $MicrocheckPath) -cne $MicrocheckAuditSha256
    ) {
        throw 'A7 lease-bound audit hash changed before lease claim'
    }
    try {
        $BuildAudit = [IO.File]::ReadAllText($BuildPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
        $MicrocheckAudit = [IO.File]::ReadAllText($MicrocheckPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    catch {
        throw 'A7 lease-bound Task 7 audit JSON is invalid'
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
            throw "A7 $Name property set is not closed"
        }
    }
    $BuildProperties = @(
        'schema_version', 'owner_authorization_id', 'run_id', 'source_commit',
        'spec_commit', 'plan_commit', 'branch', 'image_tag', 'image_id',
        'base_image_digest', 'argv', 'augmented_baseline_path',
        'augmented_baseline_sha256', 'argv_audit_path', 'argv_audit_sha256',
        'stdout_path', 'stdout_sha256', 'stderr_path', 'stderr_sha256',
        'exit_code', 'started_at', 'completed_at'
    )
    $MicrocheckProperties = @(
        'schema_version', 'owner_authorization_id', 'run_id', 'source_commit',
        'spec_commit', 'plan_commit', 'branch', 'image_tag', 'image_id',
        'base_image_digest', 'augmented_baseline_path', 'augmented_baseline_sha256',
        'source_inventory_path', 'source_inventory_sha256', 'payload_path',
        'payload_sha256', 'payload', 'docker_argv', 'stdout_path', 'stdout_sha256',
        'stderr_path', 'stderr_sha256', 'exit_code', 'started_at', 'completed_at'
    )
    & $AssertProperties $BuildAudit $BuildProperties 'build audit'
    & $AssertProperties $MicrocheckAudit $MicrocheckProperties 'micro-check audit'
    foreach ($Audit in @($BuildAudit, $MicrocheckAudit)) {
        if ([int]$Audit.schema_version -ne 1 -or
            [string]$Audit.owner_authorization_id -cne $OwnerAuthorizationId -or
            [string]$Audit.run_id -cne $RunId -or
            [string]$Audit.source_commit -cne $SourceCommit -or
            [string]$Audit.spec_commit -cne $SpecCommit -or
            [string]$Audit.plan_commit -cne $PlanCommit -or
            [string]$Audit.branch -cne $Branch -or
            [string]$Audit.image_tag -cne $ImageTag -or
            [string]$Audit.image_id -cne $ImageId -or
            [string]$Audit.base_image_digest -cne $BaseImageDigest -or
            [string]$Audit.augmented_baseline_path -cne $HistoricalPath -or
            [string]$Audit.augmented_baseline_sha256 -cne $HistoricalBaselineSha256 -or
            [int]$Audit.exit_code -ne 0) {
            throw 'A7 lease-bound Task 7 audit identity mismatch'
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
            throw 'A7 lease-bound Task 7 audit timestamp is invalid'
        }
    }
    $AuditRoot = [IO.Path]::GetDirectoryName($BuildPath)
    if ([IO.Path]::GetDirectoryName($MicrocheckPath) -cne $AuditRoot) {
        throw 'A7 Task 7 binding audits must share one audit root'
    }
    $ExpectedPaths = [ordered]@{
        build_argv = [IO.Path]::Combine($AuditRoot, '19-image-build-argv.json')
        build_stdout = [IO.Path]::Combine($AuditRoot, '20-image-build.stdout.log')
        build_stderr = [IO.Path]::Combine($AuditRoot, '20-image-build.stderr.log')
        source_inventory = [IO.Path]::Combine($AuditRoot, '21-a7-source-inventory.json')
        payload = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check-payload.json')
        microcheck_stdout = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check.stdout.log')
        microcheck_stderr = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check.stderr.log')
    }
    if ([string]$BuildAudit.argv_audit_path -cne $ExpectedPaths.build_argv -or
        [string]$BuildAudit.stdout_path -cne $ExpectedPaths.build_stdout -or
        [string]$BuildAudit.stderr_path -cne $ExpectedPaths.build_stderr -or
        [string]$MicrocheckAudit.source_inventory_path -cne $ExpectedPaths.source_inventory -or
        [string]$MicrocheckAudit.payload_path -cne $ExpectedPaths.payload -or
        [string]$MicrocheckAudit.stdout_path -cne $ExpectedPaths.microcheck_stdout -or
        [string]$MicrocheckAudit.stderr_path -cne $ExpectedPaths.microcheck_stderr) {
        throw 'A7 lease-bound Task 7 audit path mismatch'
    }
    foreach ($Path in $ExpectedPaths.Values) { [void](& $AssertRegularPath $Path $true) }
    $HashBindings = [ordered]@{
        build_argv = [string]$BuildAudit.argv_audit_sha256
        build_stdout = [string]$BuildAudit.stdout_sha256
        build_stderr = [string]$BuildAudit.stderr_sha256
        source_inventory = [string]$MicrocheckAudit.source_inventory_sha256
        payload = [string]$MicrocheckAudit.payload_sha256
        microcheck_stdout = [string]$MicrocheckAudit.stdout_sha256
        microcheck_stderr = [string]$MicrocheckAudit.stderr_sha256
    }
    foreach ($Name in $ExpectedPaths.Keys) {
        if ($HashBindings[$Name] -cnotmatch '^[0-9a-f]{64}$' -or
            (& $GetSha256 $ExpectedPaths[$Name]) -cne $HashBindings[$Name]) {
            throw "A7 lease-bound Task 7 audit file hash mismatch: $Name"
        }
    }
    try {
        $ArgvAudit = [IO.File]::ReadAllText($ExpectedPaths.build_argv, [Text.Encoding]::UTF8) |
            ConvertFrom-Json
        $SourceInventory = [IO.File]::ReadAllText(
            $ExpectedPaths.source_inventory,
            [Text.Encoding]::UTF8
        ) | ConvertFrom-Json
        $PayloadText = [IO.File]::ReadAllText($ExpectedPaths.payload, [Text.Encoding]::UTF8)
        $Payload = $PayloadText | ConvertFrom-Json
    }
    catch {
        throw 'A7 lease-bound Task 7 supporting audit JSON is invalid'
    }
    & $AssertProperties $ArgvAudit @(
        'schema_version', 'run_id', 'source_commit', 'argv', 'recorded_before_build'
    ) 'build argv audit'
    if ([int]$ArgvAudit.schema_version -ne 1 -or
        [string]$ArgvAudit.run_id -cne $RunId -or
        [string]$ArgvAudit.source_commit -cne $SourceCommit -or
        -not [bool]$ArgvAudit.recorded_before_build) {
        throw 'A7 lease-bound build argv audit mismatch'
    }
    if ([string]$SourceInventory.source_commit -cne $SourceCommit -or
        [string]$Payload.source_commit -cne $SourceCommit -or
        [string]$Payload.source_inventory_sha256 -cne $HashBindings.source_inventory -or
        (ConvertTo-Json -InputObject $MicrocheckAudit.payload -Depth 8 -Compress) -cne $PayloadText) {
        throw 'A7 lease-bound micro-check payload identity mismatch'
    }
    if ((ConvertTo-Json -InputObject @($BuildAudit.argv) -Compress) -cne
        (ConvertTo-Json -InputObject @($ArgvAudit.argv) -Compress)) {
        throw 'A7 lease-bound build argv mismatch'
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
        [string]$MicrocheckArgv[13] -cne $ImageId -or
        [string]$MicrocheckArgv[14] -cne '/workspace/scripts/run_wave0_a7_cpu_microcheck.py' -or
        [string]$MicrocheckArgv[15] -cne '--workspace-root' -or
        [string]$MicrocheckArgv[16] -cne '/workspace' -or
        [string]$MicrocheckArgv[17] -cne '--source-inventory' -or
        [string]$MicrocheckArgv[18] -cne '/audit/21-a7-source-inventory.json') {
        throw 'A7 lease-bound micro-check Docker argv mismatch'
    }
    $StdoutLines = @([IO.File]::ReadAllText(
            $ExpectedPaths.microcheck_stdout,
            [Text.Encoding]::UTF8
        ) -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($StdoutLines.Count -ne 1 -or $StdoutLines[0] -cne $PayloadText) {
        throw 'A7 lease-bound micro-check stdout does not equal the raw payload'
    }
    try {
        $HostProcesses = @($HostProcessesJson | ConvertFrom-Json)
        $Containers = @($ContainersJson | ConvertFrom-Json)
    }
    catch {
        throw 'A7 lease process/container inventory is not valid JSON'
    }
    if ($Containers.Count -ne 0) {
        throw 'A7 lease cannot bind active project containers'
    }
    foreach ($ProcessRecord in $HostProcesses) {
        if ([string]$ProcessRecord.gpu_uuid -cne $GpuUuid) {
            throw 'A7 lease host-process GPU UUID mismatch'
        }
        if ($null -ne $ProcessRecord.used_gpu_memory_mib) {
            throw 'A7 lease cannot bind a numeric CUDA compute process'
        }
    }

    $LeaseFullPath = [IO.Path]::GetFullPath($LeasePath)
    $Document = [ordered]@{
        schema_version = 1
        owner_authorization_id = $OwnerAuthorizationId
        run_id = $RunId
        source_commit = $SourceCommit
        spec_commit = $SpecCommit
        plan_commit = $PlanCommit
        branch = $Branch
        image_tag = $ImageTag
        image_id = $ImageId
        base_image_digest = $BaseImageDigest
        gpu_uuid = $GpuUuid
        campaign_root = $CampaignRootPath
        historical_baseline_path = $HistoricalPath
        historical_baseline_sha256 = $HistoricalBaselineSha256
        build_audit_sha256 = $BuildAuditSha256
        microcheck_audit_sha256 = $MicrocheckAuditSha256
        host_processes = @($HostProcesses)
        containers = @($Containers)
        claimed_at = $ClaimedAt
    }
    $Json = $Document | ConvertTo-Json -Depth 8 -Compress
    Write-A7NewText -Path $LeaseFullPath -Text $Json
    try {
        $Published = [IO.File]::ReadAllText($LeaseFullPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    catch {
        throw 'A7 published lease did not parse back'
    }
    if (
        [string]$Published.run_id -cne $RunId -or
        [string]$Published.gpu_uuid -cne $GpuUuid -or
        [string]$Published.build_audit_sha256 -cne $BuildAuditSha256 -or
        [string]$Published.microcheck_audit_sha256 -cne $MicrocheckAuditSha256
    ) {
        throw 'A7 published lease identity mismatch'
    }
    return [pscustomobject]@{
        path = $LeaseFullPath
        sha256 = & $GetSha256 $LeaseFullPath
        run_id = $RunId
        gpu_uuid = $GpuUuid
    }
}

function Close-A7Campaign {
    param(
        [Parameter(Mandatory = $true)][string]$CampaignRoot,
        [Parameter(Mandatory = $true)][string]$ProtectedGitRoot,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselinePath,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselineSha256,
        [Parameter(Mandatory = $true)][string]$CurrentImagesJson,
        [Parameter(Mandatory = $true)][string]$CurrentImageTag,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$Stage,
        [Parameter(Mandatory = $true)][string]$FailureMessage,
        [Parameter(Mandatory = $true)][string]$LeasePath,
        [Parameter(Mandatory = $true)][string]$Terminal
    )

    if ($Stage -cnotmatch '^[a-z0-9_]+$') {
        throw 'A7 closure stage is invalid'
    }
    if ($RunId -cnotmatch '^wave0-a7-[0-9]{8}T[0-9]{9}Z$' -or $SourceCommit -cnotmatch '^[0-9a-f]{40}$') {
        throw 'A7 closure identity is invalid'
    }
    if ([string]::IsNullOrWhiteSpace($FailureMessage) -or $Terminal -notmatch 'WAVE1_FORBIDDEN$') {
        throw 'A7 closure failure or terminal is invalid'
    }
    $CampaignPath = [IO.Path]::GetFullPath($CampaignRoot)
    if (-not [IO.Directory]::Exists($CampaignPath)) {
        throw 'A7 claimed campaign root is missing'
    }
    $CampaignInfo = [IO.DirectoryInfo]::new($CampaignPath)
    if (($CampaignInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'A7 campaign root link or junction is forbidden'
    }
    $AuditRoot = [IO.Path]::Combine($CampaignPath, 'audit')
    if (-not [IO.Directory]::Exists($AuditRoot)) {
        throw 'A7 campaign audit root is missing'
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $Stream = [IO.File]::OpenRead($Path)
        try {
            $Hasher = [Security.Cryptography.SHA256]::Create()
            try {
                return [Convert]::ToHexString($Hasher.ComputeHash($Stream)).ToLowerInvariant()
            }
            finally { $Hasher.Dispose() }
        }
        finally { $Stream.Dispose() }
    }
    $GetFileRecord = {
        param(
            [Parameter(Mandatory = $true)][string]$Root,
            [Parameter(Mandatory = $true)][string]$Path
        )
        $File = [IO.FileInfo]::new($Path)
        if (-not $File.Exists -or ($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 closure file is missing or linked'
        }
        return [pscustomobject][ordered]@{
            path = [IO.Path]::GetRelativePath($Root, $File.FullName).Replace('\', '/')
            size = [long]$File.Length
            sha256 = & $GetSha256 $File.FullName
        }
    }

    $StageName = $Stage.Replace('_', '-')
    $DiagnosticPath = [IO.Path]::Combine($AuditRoot, "23-$StageName-failure-diagnostic.json")
    $PreservationPath = [IO.Path]::Combine($AuditRoot, '30-historical-preservation.json')
    $ResultPath = [IO.Path]::Combine($AuditRoot, '40-campaign-result.json')
    $ManifestPath = [IO.Path]::Combine($AuditRoot, '41-campaign-file-manifest.json')
    $ClosurePath = [IO.Path]::Combine($AuditRoot, '51-campaign-closure-manifest.json')
    $Diagnostic = [ordered]@{
        schema_version = 1
        run_id = $RunId
        source_commit = $SourceCommit
        stage = $Stage
        state = 'CAMPAIGN_CLAIMED'
        error = $FailureMessage
        recorded_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText -Path $DiagnosticPath -Text ($Diagnostic | ConvertTo-Json -Compress)

    $Preserved = $true
    $PreservationError = $null
    try {
        $BaselinePath = [IO.Path]::GetFullPath($HistoricalBaselinePath)
        $BaselineInfo = [IO.FileInfo]::new($BaselinePath)
        if (
            -not $BaselineInfo.Exists -or
            ($BaselineInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            $HistoricalBaselineSha256 -cnotmatch '^[0-9a-f]{64}$' -or
            (& $GetSha256 $BaselinePath) -cne $HistoricalBaselineSha256
        ) {
            throw 'augmented historical baseline identity mismatch'
        }
        $Baseline = [IO.File]::ReadAllText($BaselinePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
        $ArtifactRoot = [IO.Path]::GetFullPath([string]$Baseline.artifact_root)
        $ArtifactPrefix = $ArtifactRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
        $CampaignPrefix = $CampaignPath.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
        if (-not $CampaignPath.StartsWith($ArtifactPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'current campaign is outside the augmented artifact root'
        }
        $ExpectedArtifacts = @{}
        foreach ($Record in @($Baseline.artifact_files)) {
            $Path = [string]$Record.path
            if ($ExpectedArtifacts.ContainsKey($Path)) {
                throw 'augmented historical baseline duplicates an artifact path'
            }
            $ExpectedArtifacts[$Path] = $Record
        }
        $ObservedArtifacts = @{}
        $Pending = [System.Collections.Generic.Stack[IO.DirectoryInfo]]::new()
        $Pending.Push([IO.DirectoryInfo]::new($ArtifactRoot))
        while ($Pending.Count -gt 0) {
            $Directory = $Pending.Pop()
            if (($Directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'historical artifact directory link or junction detected'
            }
            foreach ($Child in $Directory.EnumerateDirectories()) {
                if (
                    $Child.FullName -ceq $CampaignPath -or
                    $Child.FullName.StartsWith($CampaignPrefix, [StringComparison]::OrdinalIgnoreCase)
                ) {
                    continue
                }
                $Pending.Push($Child)
            }
            foreach ($File in $Directory.EnumerateFiles()) {
                if ($File.FullName.StartsWith($CampaignPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                    continue
                }
                if (($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw 'historical artifact file link detected'
                }
                $Relative = [IO.Path]::GetRelativePath($ArtifactRoot, $File.FullName).Replace('\', '/')
                if ($ObservedArtifacts.ContainsKey($Relative)) {
                    throw 'current historical inventory duplicates an artifact path'
                }
                $ObservedArtifacts[$Relative] = [pscustomobject]@{
                    size = [long]$File.Length
                    sha256 = & $GetSha256 $File.FullName
                }
            }
        }
        if ($ObservedArtifacts.Count -ne $ExpectedArtifacts.Count) {
            throw 'historical artifact exact-set count mismatch'
        }
        foreach ($Path in $ExpectedArtifacts.Keys) {
            if (-not $ObservedArtifacts.ContainsKey($Path)) {
                throw "historical artifact disappeared: $Path"
            }
            $Expected = $ExpectedArtifacts[$Path]
            $Observed = $ObservedArtifacts[$Path]
            if ([long]$Observed.size -ne [long]$Expected.size -or [string]$Observed.sha256 -cne [string]$Expected.sha256) {
                throw "historical artifact identity changed: $Path"
            }
        }

        $ExpectedImages = @{}
        foreach ($Image in @($Baseline.images)) {
            $ExpectedImages[[string]$Image.tag] = [string]$Image.image_id
        }
        $ObservedImages = @{}
        foreach ($Image in @($CurrentImagesJson | ConvertFrom-Json)) {
            $Tag = [string]$Image.tag
            if ($Tag -ceq $CurrentImageTag) { continue }
            if ($ObservedImages.ContainsKey($Tag)) { throw 'current historical image tag is duplicated' }
            $ObservedImages[$Tag] = [string]$Image.image_id
        }
        if ($ObservedImages.Count -ne $ExpectedImages.Count) {
            throw 'historical image exact-set count mismatch'
        }
        foreach ($Tag in $ExpectedImages.Keys) {
            if (-not $ObservedImages.ContainsKey($Tag) -or $ObservedImages[$Tag] -cne $ExpectedImages[$Tag]) {
                throw "historical image identity changed: $Tag"
            }
        }

        $ProtectedRootPath = [IO.Path]::GetFullPath($ProtectedGitRoot)
        foreach ($Record in @($Baseline.protected_git)) {
            $Path = [IO.Path]::GetFullPath(
                [IO.Path]::Combine($ProtectedRootPath, ([string]$Record.path).Replace('/', '\'))
            )
            $File = [IO.FileInfo]::new($Path)
            if (
                -not $File.Exists -or
                ($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
                [long]$File.Length -ne [long]$Record.size -or
                (& $GetSha256 $Path) -cne [string]$Record.sha256
            ) {
                throw "protected Git identity changed: $($Record.path)"
            }
        }
    }
    catch {
        $Preserved = $false
        $PreservationError = $_.Exception.Message
    }
    $Preservation = [ordered]@{
        schema_version = 1
        run_id = $RunId
        baseline_path = [IO.Path]::GetFullPath($HistoricalBaselinePath)
        baseline_sha256 = $HistoricalBaselineSha256
        preserved = $Preserved
        error = $PreservationError
        checked_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText -Path $PreservationPath -Text ($Preservation | ConvertTo-Json -Compress)

    $LeaseFullPath = [IO.Path]::GetFullPath($LeasePath)
    $LeaseAcquired = [IO.File]::Exists($LeaseFullPath)
    $ReleasedPath = "$LeaseFullPath.released"
    $ReleaseRecordPath = "$LeaseFullPath.release.json"
    $LeaseReleased = [IO.File]::Exists($ReleasedPath) -and [IO.File]::Exists($ReleaseRecordPath)
    $CampaignResult = [ordered]@{
        schema_version = 1
        run_id = $RunId
        source_commit = $SourceCommit
        stage = $Stage
        status = 'FAILED'
        terminal = $Terminal
        historical_preserved = $Preserved
        lease_acquired = $LeaseAcquired
        lease_released = $LeaseReleased
        finished_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText -Path $ResultPath -Text ($CampaignResult | ConvertTo-Json -Compress)

    $ManifestRecords = [System.Collections.Generic.List[object]]::new()
    foreach ($File in [IO.Directory]::EnumerateFiles($CampaignPath, '*', [IO.SearchOption]::AllDirectories)) {
        if ($File -ceq $ManifestPath -or $File -ceq $ClosurePath) { continue }
        [void]$ManifestRecords.Add((& $GetFileRecord $CampaignPath $File))
    }
    $Manifest = [ordered]@{
        schema_version = 1
        run_id = $RunId
        files = @($ManifestRecords | Sort-Object -CaseSensitive path)
        captured_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText -Path $ManifestPath -Text ($Manifest | ConvertTo-Json -Depth 6 -Compress)

    $ClosureFiles = @(
        & $GetFileRecord $CampaignPath $DiagnosticPath
        & $GetFileRecord $CampaignPath $PreservationPath
        & $GetFileRecord $CampaignPath $ResultPath
        & $GetFileRecord $CampaignPath $ManifestPath
    )
    $Closure = [ordered]@{
        schema_version = 1
        run_id = $RunId
        terminal = $Terminal
        files = $ClosureFiles
        historical_preserved = $Preserved
        lease_acquired = $LeaseAcquired
        lease_released = $LeaseReleased
        closed_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText -Path $ClosurePath -Text ($Closure | ConvertTo-Json -Depth 6 -Compress)
    foreach ($Record in $ClosureFiles) {
        $Path = [IO.Path]::Combine($CampaignPath, ([string]$Record.path).Replace('/', '\'))
        $File = [IO.FileInfo]::new($Path)
        if ([long]$File.Length -ne [long]$Record.size -or (& $GetSha256 $Path) -cne [string]$Record.sha256) {
            throw 'A7 closure manifest failed parse-back hash verification'
        }
    }
    return [pscustomobject]@{
        state = 'CLOSED'
        terminal = $Terminal
        closure_path = $ClosurePath
        historical_preserved = $Preserved
        lease_acquired = $LeaseAcquired
        lease_released = $LeaseReleased
    }
}

function Close-A7PostTask8ValidationFailure {
    param(
        [Parameter(Mandatory = $true)][string]$CampaignRoot,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$SourceCommit,
        [Parameter(Mandatory = $true)][string]$SpecCommit,
        [Parameter(Mandatory = $true)][string]$PlanCommit,
        [Parameter(Mandatory = $true)][string]$ImageTag,
        [Parameter(Mandatory = $true)][string]$ImageId,
        [Parameter(Mandatory = $true)][int]$Task8ExitCode,
        [Parameter(Mandatory = $true)][AllowNull()][AllowEmptyString()][string]$ObservedTerminal,
        [Parameter(Mandatory = $true)][string]$ValidationError,
        [Parameter(Mandatory = $true)][string]$LeasePath
    )
    foreach ($Commit in @($SourceCommit, $SpecCommit, $PlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 post-Task-8 commit identity is invalid'
        }
    }
    if ([string]::IsNullOrWhiteSpace($OwnerAuthorizationId) -or
        [string]::IsNullOrWhiteSpace($RunId) -or
        [string]::IsNullOrWhiteSpace($ImageTag) -or
        $ImageId -cnotmatch '^sha256:[0-9a-f]{64}$' -or
        [string]::IsNullOrWhiteSpace($ValidationError)) {
        throw 'A7 post-Task-8 immutable identity or validation error is invalid'
    }
    $CampaignPath = [IO.Path]::GetFullPath($CampaignRoot).TrimEnd('\', '/')
    $AuditRoot = [IO.Path]::Combine($CampaignPath, 'audit')
    foreach ($Directory in @($CampaignPath, $AuditRoot)) {
        if (-not [IO.Directory]::Exists($Directory)) {
            throw 'A7 post-Task-8 campaign or audit root is missing'
        }
        $Current = [IO.DirectoryInfo]::new($Directory)
        while ($null -ne $Current) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 post-Task-8 campaign or audit root is linked'
            }
            $Current = $Current.Parent
        }
    }
    $FailurePath = [IO.Path]::Combine(
        $AuditRoot,
        '52-task7-post-task8-validation-failure.json'
    )
    $ClosurePath = [IO.Path]::Combine(
        $AuditRoot,
        '53-task7-post-task8-validation-closure.json'
    )
    foreach ($Destination in @($FailurePath, $ClosurePath)) {
        if ([IO.File]::Exists($Destination) -or [IO.Directory]::Exists($Destination)) {
            throw 'A7 post-Task-8 evidence destination already exists'
        }
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $Stream = [IO.File]::OpenRead($Path)
        try {
            $Hasher = [Security.Cryptography.SHA256]::Create()
            try {
                return [Convert]::ToHexString($Hasher.ComputeHash($Stream)).ToLowerInvariant()
            }
            finally { $Hasher.Dispose() }
        }
        finally { $Stream.Dispose() }
    }
    $GetSafeFileRecord = {
        param(
            [Parameter(Mandatory = $true)][string]$Root,
            [Parameter(Mandatory = $true)][string]$Path
        )
        $RootPath = [IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
        $RootPrefix = $RootPath + [IO.Path]::DirectorySeparatorChar
        $FullPath = [IO.Path]::GetFullPath($Path)
        if (-not $FullPath.StartsWith($RootPrefix, [StringComparison]::OrdinalIgnoreCase) -or
            -not [IO.File]::Exists($FullPath) -or [IO.Directory]::Exists($FullPath)) {
            throw 'A7 post-Task-8 evidence file is unsafe or missing'
        }
        $File = [IO.FileInfo]::new($FullPath)
        if (($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 post-Task-8 evidence file is linked'
        }
        $Current = $File.Directory
        while ($null -ne $Current -and
            $Current.FullName.StartsWith($RootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 post-Task-8 evidence file is linked'
            }
            $Current = $Current.Parent
        }
        $RelativePath = $FullPath.Substring($RootPrefix.Length).Replace('\', '/')
        return [pscustomobject][ordered]@{
            path = $RelativePath
            size = [long]$File.Length
            sha256 = & $GetSha256 $FullPath
        }
    }
    $PrePublicationFiles = @(
        [IO.Directory]::EnumerateFiles($CampaignPath, '*', [IO.SearchOption]::AllDirectories) |
            ForEach-Object { & $GetSafeFileRecord $CampaignPath $_ } |
            Sort-Object -CaseSensitive path
    )
    $RequiredFiles = [System.Collections.Generic.List[object]]::new()
    foreach ($Name in @(
            '30-historical-preservation.json',
            '40-campaign-result.json',
            '41-campaign-file-manifest.json',
            '51-campaign-closure-manifest.json'
        )) {
        $Path = [IO.Path]::Combine($AuditRoot, $Name)
        if ([IO.File]::Exists($Path)) {
            $Record = & $GetSafeFileRecord $CampaignPath $Path
            [void]$RequiredFiles.Add([pscustomobject][ordered]@{
                    path = [string]$Record.path
                    exists = $true
                    size = [long]$Record.size
                    sha256 = [string]$Record.sha256
                })
        }
        else {
            if ([IO.Directory]::Exists($Path)) {
                throw 'A7 post-Task-8 required evidence path is not a file'
            }
            [void]$RequiredFiles.Add([pscustomobject][ordered]@{
                    path = "audit/$Name"
                    exists = $false
                })
        }
    }
    $GetLeaseFileState = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $FullPath = [IO.Path]::GetFullPath($Path)
        if ([IO.File]::Exists($FullPath)) {
            $File = [IO.FileInfo]::new($FullPath)
            if (($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 post-Task-8 lease-state file is linked'
            }
            return [pscustomobject][ordered]@{
                path = $FullPath
                exists = $true
                size = [long]$File.Length
                sha256 = & $GetSha256 $FullPath
            }
        }
        if ([IO.Directory]::Exists($FullPath)) {
            throw 'A7 post-Task-8 lease-state path is not a file'
        }
        return [pscustomobject][ordered]@{
            path = $FullPath
            exists = $false
        }
    }
    $LeaseFullPath = [IO.Path]::GetFullPath($LeasePath)
    $LeaseState = [pscustomobject][ordered]@{
        active = & $GetLeaseFileState $LeaseFullPath
        released = & $GetLeaseFileState "$LeaseFullPath.released"
        release_record = & $GetLeaseFileState "$LeaseFullPath.release.json"
    }
    $RecordedAt = [DateTimeOffset]::UtcNow.ToString('o')
    $FailureRecord = [ordered]@{
        schema_version = 1
        owner_authorization_id = $OwnerAuthorizationId
        run_id = $RunId
        source_commit = $SourceCommit
        spec_commit = $SpecCommit
        plan_commit = $PlanCommit
        image_tag = $ImageTag
        image_id = $ImageId
        campaign_root = $CampaignPath
        task8_exit_code = $Task8ExitCode
        observed_terminal = if ([string]::IsNullOrWhiteSpace($ObservedTerminal)) { $null } else { $ObservedTerminal }
        validation_error = $ValidationError
        required_files = @($RequiredFiles)
        lease_state = $LeaseState
        pre_publication_files = @($PrePublicationFiles)
        recorded_at = $RecordedAt
    }
    Write-A7NewText -Path $FailurePath -Text ($FailureRecord | ConvertTo-Json -Depth 10 -Compress)
    $FailureFile = [IO.FileInfo]::new($FailurePath)
    $FailureSha256 = & $GetSha256 $FailurePath
    $ClosureRecord = [ordered]@{
        schema_version = 1
        owner_authorization_id = $OwnerAuthorizationId
        run_id = $RunId
        source_commit = $SourceCommit
        spec_commit = $SpecCommit
        plan_commit = $PlanCommit
        image_tag = $ImageTag
        image_id = $ImageId
        campaign_root = $CampaignPath
        task8_exit_code = $Task8ExitCode
        observed_terminal = if ([string]::IsNullOrWhiteSpace($ObservedTerminal)) { $null } else { $ObservedTerminal }
        validation_error = $ValidationError
        required_files = @($RequiredFiles)
        lease_state = $LeaseState
        pre_publication_files = @($PrePublicationFiles)
        status = 'POST_TASK8_VALIDATION_FAILED'
        failure_record = [ordered]@{
            path = 'audit/52-task7-post-task8-validation-failure.json'
            size = [long]$FailureFile.Length
            sha256 = $FailureSha256
        }
        recorded_at = $RecordedAt
    }
    Write-A7NewText -Path $ClosurePath -Text ($ClosureRecord | ConvertTo-Json -Depth 10 -Compress)
    $ClosureSha256 = & $GetSha256 $ClosurePath
    try {
        $PublishedFailure = [IO.File]::ReadAllText($FailurePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
        $PublishedClosure = [IO.File]::ReadAllText($ClosurePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    }
    catch { throw 'A7 post-Task-8 evidence failed parse-back' }
    if ([string]$PublishedFailure.run_id -cne $RunId -or
        [string]$PublishedClosure.status -cne 'POST_TASK8_VALIDATION_FAILED' -or
        [string]$PublishedClosure.failure_record.sha256 -cne $FailureSha256 -or
        (& $GetSha256 $FailurePath) -cne $FailureSha256 -or
        (& $GetSha256 $ClosurePath) -cne $ClosureSha256) {
        throw 'A7 post-Task-8 evidence failed identity revalidation'
    }
    return [pscustomobject][ordered]@{
        failure_path = $FailurePath
        failure_sha256 = $FailureSha256
        closure_path = $ClosurePath
        closure_sha256 = $ClosureSha256
        validation_status = 'FAILED'
    }
}

function Invoke-A7Launch {
    param(
        [Parameter(Mandatory = $true)][string]$RegisteredWorktree,
        [Parameter(Mandatory = $true)][string]$ProtectedGitRoot,
        [Parameter(Mandatory = $true)][string]$ArtifactRoot,
        [Parameter(Mandatory = $true)][string]$LeaseRoot,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselinePath,
        [Parameter(Mandatory = $true)][string]$HistoricalBaselineSha256,
        [Parameter(Mandatory = $true)][string]$HistoricalImagesJson,
        [Parameter(Mandatory = $true)][string]$PreflightJson,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedBranch,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId,
        [Parameter(Mandatory = $true)][string]$DockerExecutable,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$DockerPrefixArguments,
        [Parameter(Mandatory = $true)][string]$Task8Executable,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Task8PrefixArguments,
        [Parameter(Mandatory = $true)][string]$Task8RunnerPath
    )

    $TerminalInconclusive = 'WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'
    $AllowedTerminals = @(
        'WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN',
        'WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN',
        $TerminalInconclusive
    )
    $BaseDigest = 'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    if ($RunId -cnotmatch '^wave0-a7-[0-9]{8}T[0-9]{9}Z$') {
        throw 'A7 launcher run ID is invalid'
    }
    foreach ($Commit in @($ExpectedSourceCommit, $ExpectedSpecCommit, $ExpectedPlanCommit)) {
        if ($Commit -cnotmatch '^[0-9a-f]{40}$') {
            throw 'A7 launcher commit identity is invalid'
        }
    }
    if (
        [string]::IsNullOrWhiteSpace($ExpectedBranch) -or
        [string]::IsNullOrWhiteSpace($OwnerAuthorizationId)
    ) {
        throw 'A7 launcher branch and owner authorization are required'
    }
    $WorktreePath = [IO.Path]::GetFullPath($RegisteredWorktree)
    $ArtifactRootPath = [IO.Path]::GetFullPath($ArtifactRoot)
    $LeaseRootPath = [IO.Path]::GetFullPath($LeaseRoot)
    $Task8Path = [IO.Path]::GetFullPath($Task8RunnerPath)
    foreach ($Directory in @($WorktreePath, $ArtifactRootPath, $LeaseRootPath)) {
        if (-not [IO.Directory]::Exists($Directory)) {
            throw 'A7 launcher required directory is missing'
        }
        $Current = [IO.DirectoryInfo]::new($Directory)
        while ($null -ne $Current) {
            if (($Current.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw 'A7 launcher directory link or junction is forbidden'
            }
            $Current = $Current.Parent
        }
    }
    foreach ($FilePath in @($DockerExecutable, $Task8Executable, $Task8Path, $HistoricalBaselinePath)) {
        $FullPath = [IO.Path]::GetFullPath($FilePath)
        $File = [IO.FileInfo]::new($FullPath)
        if (-not $File.Exists -or ($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'A7 launcher required executable or baseline is missing or linked'
        }
    }
    $GetSha256 = {
        param([Parameter(Mandatory = $true)][string]$Path)
        $Stream = [IO.File]::OpenRead($Path)
        try {
            $Hasher = [Security.Cryptography.SHA256]::Create()
            try {
                return [Convert]::ToHexString($Hasher.ComputeHash($Stream)).ToLowerInvariant()
            }
            finally { $Hasher.Dispose() }
        }
        finally { $Stream.Dispose() }
    }
    $HistoricalPath = [IO.Path]::GetFullPath($HistoricalBaselinePath)
    if (
        $HistoricalBaselineSha256 -cnotmatch '^[0-9a-f]{64}$' -or
        (& $GetSha256 $HistoricalPath) -cne $HistoricalBaselineSha256
    ) {
        throw 'A7 launcher augmented baseline identity mismatch'
    }
    try {
        $HistoricalImages = @($HistoricalImagesJson | ConvertFrom-Json)
        $Preflight = $PreflightJson | ConvertFrom-Json
    }
    catch {
        throw 'A7 launcher historical image or preflight JSON is invalid'
    }
    if (
        [string]$Preflight.gpu_uuid -cnotmatch '^GPU-[A-Za-z0-9-]+$' -or
        [string]$Preflight.gpu_name -cne 'NVIDIA GeForce RTX 4090' -or
        @($Preflight.containers).Count -ne 0
    ) {
        throw 'A7 launcher GPU preflight binding is invalid'
    }
    $ImageTag = "vision-active-learning-loop:wave0-a7-$($ExpectedSourceCommit.Substring(0, 12))-$RunId"
    if (@($HistoricalImages | Where-Object { [string]$_.tag -ceq $ImageTag }).Count -ne 0) {
        throw 'A7 launcher image tag already exists'
    }
    $CampaignParent = [IO.Path]::Combine($ArtifactRootPath, 'a7-runs')
    if (-not [IO.Directory]::Exists($CampaignParent)) {
        throw 'A7 campaign parent must already exist'
    }
    $CampaignRoot = [IO.Path]::Combine($CampaignParent, $RunId)
    $LeasePath = [IO.Path]::Combine($LeaseRootPath, "$($Preflight.gpu_uuid).json")
    foreach ($Destination in @(
            $CampaignRoot,
            $LeasePath,
            "$LeasePath.released",
            "$LeasePath.release.json"
        )) {
        if ([IO.File]::Exists($Destination) -or [IO.Directory]::Exists($Destination)) {
            throw 'A7 launcher destination must not already exist'
        }
    }

    $CampaignItem = New-Item -ItemType Directory -Path $CampaignRoot -ErrorAction Stop
    if ($CampaignItem.FullName -cne $CampaignRoot) {
        throw 'A7 campaign claim path mismatch'
    }
    $AuditRoot = [IO.Path]::Combine($CampaignRoot, 'audit')
    [void](New-Item -ItemType Directory -Path $AuditRoot -ErrorAction Stop)
    $Identity = [ordered]@{
        schema_version = 1
        owner_authorization_id = $OwnerAuthorizationId
        run_id = $RunId
        source_commit = $ExpectedSourceCommit
        spec_commit = $ExpectedSpecCommit
        plan_commit = $ExpectedPlanCommit
        branch = $ExpectedBranch
        image_tag = $ImageTag
        campaign_root = $CampaignRoot
        historical_baseline_path = $HistoricalPath
        historical_baseline_sha256 = $HistoricalBaselineSha256
        state = 'CAMPAIGN_CLAIMED'
        claimed_at = [DateTimeOffset]::UtcNow.ToString('o')
    }
    Write-A7NewText `
        -Path ([IO.Path]::Combine($AuditRoot, '00-task7-identity.json')) `
        -Text ($Identity | ConvertTo-Json -Compress)

    $Stage = 'campaign_claim'
    $ImageId = $null
    $Task8Invoked = $false
    $Task8Result = $null
    $CurrentImages = [System.Collections.Generic.List[object]]::new()
    foreach ($HistoricalImage in $HistoricalImages) { [void]$CurrentImages.Add($HistoricalImage) }
    try {
        $Stage = 'image_build'
        $BuildArguments = @(New-A7BuildArguments `
                -SourceCommit $ExpectedSourceCommit `
                -RunId $RunId `
                -SpecCommit $ExpectedSpecCommit `
                -PlanCommit $ExpectedPlanCommit `
                -BaseDigest $BaseDigest `
                -ImageTag $ImageTag)
        Assert-A7BuildArguments `
            -Arguments $BuildArguments `
            -SourceCommit $ExpectedSourceCommit `
            -RunId $RunId `
            -SpecCommit $ExpectedSpecCommit `
            -PlanCommit $ExpectedPlanCommit `
            -BaseDigest $BaseDigest `
            -ImageTag $ImageTag
        $BuildLogicalArgv = @('docker') + $BuildArguments
        $BuildArgvAudit = [ordered]@{
            schema_version = 1
            run_id = $RunId
            source_commit = $ExpectedSourceCommit
            argv = $BuildLogicalArgv
            recorded_before_build = $true
        }
        $BuildArgvAuditPath = [IO.Path]::Combine($AuditRoot, '19-image-build-argv.json')
        Write-A7NewText `
            -Path $BuildArgvAuditPath `
            -Text ($BuildArgvAudit | ConvertTo-Json -Depth 6 -Compress)
        $BuildStdoutPath = [IO.Path]::Combine($AuditRoot, '20-image-build.stdout.log')
        $BuildStderrPath = [IO.Path]::Combine($AuditRoot, '20-image-build.stderr.log')
        $BuildStartedAt = [DateTimeOffset]::UtcNow.ToString('o')
        $BuildResult = Invoke-A7Native `
            -Executable $DockerExecutable `
            -Arguments (@($DockerPrefixArguments) + $BuildArguments) `
            -StdoutPath $BuildStdoutPath `
            -StderrPath $BuildStderrPath `
            -WorkingDirectory $WorktreePath
        $BuildCompletedAt = [DateTimeOffset]::UtcNow.ToString('o')
        if ($BuildResult.exit_code -ne 0) {
            throw "A7 image build exited $($BuildResult.exit_code)"
        }

        $Stage = 'image_inspect'
        $InspectArguments = @($DockerPrefixArguments) + @('image', 'inspect', $ImageTag)
        $InspectResult = Invoke-A7Native `
            -Executable $DockerExecutable `
            -Arguments $InspectArguments `
            -StdoutPath ([IO.Path]::Combine($AuditRoot, '21-image-inspect.stdout.json')) `
            -StderrPath ([IO.Path]::Combine($AuditRoot, '21-image-inspect.stderr.log')) `
            -WorkingDirectory $WorktreePath
        if ($InspectResult.exit_code -ne 0) {
            throw "A7 image inspect exited $($InspectResult.exit_code)"
        }
        try {
            $InspectedImages = @($InspectResult.stdout | ConvertFrom-Json)
            if ($InspectedImages.Count -eq 1) { $ImageId = [string]$InspectedImages[0].Id }
        }
        catch {
            throw 'A7 image inspect output is malformed'
        }
        Assert-A7ImageInspect `
            -InspectJson $InspectResult.stdout `
            -ImageId $ImageId `
            -ImageTag $ImageTag `
            -SourceCommit $ExpectedSourceCommit `
            -RunId $RunId `
            -SpecCommit $ExpectedSpecCommit `
            -PlanCommit $ExpectedPlanCommit `
            -BaseDigest $BaseDigest
        [void]$CurrentImages.Add([pscustomobject]@{ tag = $ImageTag; image_id = $ImageId })
        $BuildAudit = [ordered]@{
            schema_version = 1
            owner_authorization_id = $OwnerAuthorizationId
            run_id = $RunId
            source_commit = $ExpectedSourceCommit
            spec_commit = $ExpectedSpecCommit
            plan_commit = $ExpectedPlanCommit
            branch = $ExpectedBranch
            image_tag = $ImageTag
            image_id = $ImageId
            base_image_digest = $BaseDigest
            argv = $BuildLogicalArgv
            augmented_baseline_path = $HistoricalPath
            augmented_baseline_sha256 = $HistoricalBaselineSha256
            argv_audit_path = $BuildArgvAuditPath
            argv_audit_sha256 = & $GetSha256 $BuildArgvAuditPath
            stdout_path = $BuildStdoutPath
            stdout_sha256 = & $GetSha256 $BuildStdoutPath
            stderr_path = $BuildStderrPath
            stderr_sha256 = & $GetSha256 $BuildStderrPath
            exit_code = [int]$BuildResult.exit_code
            started_at = $BuildStartedAt
            completed_at = $BuildCompletedAt
        }
        $BuildAuditPath = [IO.Path]::Combine($AuditRoot, '20-image-build-result.json')
        Write-A7NewText -Path $BuildAuditPath -Text ($BuildAudit | ConvertTo-Json -Depth 6 -Compress)

        $Stage = 'source_inventory'
        $SourcePaths = @(
            'scripts/start_wave0_a7.ps1',
            'scripts/run_wave0_a7_cpu_microcheck.py',
            'scripts/run_wave0_a7.ps1',
            'src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py',
            'src/vision_active_learning_loop/diagnostics/tensor_evidence.py',
            'src/vision_active_learning_loop/artifacts/receipts.py',
            'schemas/grid-sample-attribution-receipt.schema.json'
        )
        $SourceRecords = [System.Collections.Generic.List[object]]::new()
        foreach ($RelativePath in $SourcePaths) {
            $SourcePath = [IO.Path]::GetFullPath(
                [IO.Path]::Combine($WorktreePath, $RelativePath.Replace('/', '\'))
            )
            $SourceFile = [IO.FileInfo]::new($SourcePath)
            if (-not $SourceFile.Exists -or ($SourceFile.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "A7 source inventory file is missing or linked: $RelativePath"
            }
            [void]$SourceRecords.Add([pscustomobject][ordered]@{
                    path = $RelativePath
                    sha256 = & $GetSha256 $SourcePath
                })
        }
        $SourceInventory = [ordered]@{
            schema_version = 1
            source_commit = $ExpectedSourceCommit
            files = @($SourceRecords)
        }
        $SourceInventoryPath = [IO.Path]::Combine($AuditRoot, '21-a7-source-inventory.json')
        Write-A7NewText -Path $SourceInventoryPath -Text ($SourceInventory | ConvertTo-Json -Depth 6 -Compress)
        $SourceInventorySha256 = & $GetSha256 $SourceInventoryPath

        $Stage = 'cpu_microcheck'
        $MicrocheckArguments = @(
            'run', '--rm', '--network', 'none', '--workdir', '/workspace', '--entrypoint', 'python',
            '-v', "${WorktreePath}:/workspace:ro",
            '-v', "${AuditRoot}:/audit:ro",
            $ImageId,
            '/workspace/scripts/run_wave0_a7_cpu_microcheck.py',
            '--workspace-root', '/workspace',
            '--source-inventory', '/audit/21-a7-source-inventory.json'
        )
        $MicrocheckLogicalArgv = @('docker') + $MicrocheckArguments
        $MicrocheckStdoutPath = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check.stdout.log')
        $MicrocheckStderrPath = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check.stderr.log')
        $MicrocheckStartedAt = [DateTimeOffset]::UtcNow.ToString('o')
        $MicrocheckResult = Invoke-A7Native `
            -Executable $DockerExecutable `
            -Arguments (@($DockerPrefixArguments) + $MicrocheckArguments) `
            -StdoutPath $MicrocheckStdoutPath `
            -StderrPath $MicrocheckStderrPath `
            -WorkingDirectory $WorktreePath
        $MicrocheckCompletedAt = [DateTimeOffset]::UtcNow.ToString('o')
        if ($MicrocheckResult.exit_code -ne 0 -or -not [string]::IsNullOrEmpty($MicrocheckResult.stderr)) {
            throw 'A7 CPU micro-check process failed or wrote stderr'
        }
        $MicrocheckLines = @($MicrocheckResult.stdout -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
        if ($MicrocheckLines.Count -ne 1) {
            throw 'A7 CPU micro-check must emit exactly one JSON line'
        }
        try { $Microcheck = $MicrocheckLines[0] | ConvertFrom-Json }
        catch { throw 'A7 CPU micro-check output is malformed' }
        $ExpectedMicrocheckProperties = @(
            'canonical_dtypes', 'classifier_statuses', 'cuda_initialized', 'manifest_target',
            'receipt_kinds', 'schema_version', 'snapshot_corruption_rejected',
            'snapshot_names', 'snapshot_tensor_count', 'source_commit', 'source_files',
            'source_inventory_sha256', 'status'
        )
        $ObservedProperties = @($Microcheck.PSObject.Properties.Name | Sort-Object -CaseSensitive)
        if (($ObservedProperties -join '|') -cne ($ExpectedMicrocheckProperties -join '|')) {
            throw 'A7 CPU micro-check result inventory is not closed'
        }
        if (
            $Microcheck.schema_version -ne 1 -or
            [string]$Microcheck.status -cne 'RECORDED' -or
            [string]$Microcheck.source_commit -cne $ExpectedSourceCommit -or
            [string]$Microcheck.source_inventory_sha256 -cne $SourceInventorySha256 -or
            [string]$Microcheck.manifest_target -cne 'vision_active_learning_loop.diagnostics.grid_sample_attribution:main' -or
            [bool]$Microcheck.cuda_initialized -or
            -not [bool]$Microcheck.snapshot_corruption_rejected -or
            [int]$Microcheck.snapshot_tensor_count -ne 27 -or
            @($Microcheck.snapshot_names).Count -ne 27 -or
            @($Microcheck.snapshot_names | Sort-Object -Unique).Count -ne 27 -or
            (@($Microcheck.canonical_dtypes) -join '|') -cne 'bfloat16|float16|float32|float64' -or
            (@($Microcheck.receipt_kinds) -join '|') -cne 'control|instrumented|isolated-vjp|aggregate' -or
            (@($Microcheck.classifier_statuses) -join '|') -cne 'ATTRIBUTED|INCONCLUSIVE|NOT_ATTRIBUTED' -or
            (($Microcheck.source_files | ConvertTo-Json -Depth 6 -Compress) -cne ($SourceInventory.files | ConvertTo-Json -Depth 6 -Compress))
        ) {
            throw 'A7 CPU micro-check result binding mismatch'
        }
        $MicrocheckPayloadPath = [IO.Path]::Combine(
            $AuditRoot,
            '22-a7-cpu-micro-check-payload.json'
        )
        Write-A7NewText -Path $MicrocheckPayloadPath -Text $MicrocheckLines[0]
        $MicrocheckAudit = [ordered]@{
            schema_version = 1
            owner_authorization_id = $OwnerAuthorizationId
            run_id = $RunId
            source_commit = $ExpectedSourceCommit
            spec_commit = $ExpectedSpecCommit
            plan_commit = $ExpectedPlanCommit
            branch = $ExpectedBranch
            image_tag = $ImageTag
            image_id = $ImageId
            base_image_digest = $BaseDigest
            augmented_baseline_path = $HistoricalPath
            augmented_baseline_sha256 = $HistoricalBaselineSha256
            source_inventory_path = $SourceInventoryPath
            source_inventory_sha256 = $SourceInventorySha256
            payload_path = $MicrocheckPayloadPath
            payload_sha256 = & $GetSha256 $MicrocheckPayloadPath
            payload = $Microcheck
            docker_argv = $MicrocheckLogicalArgv
            stdout_path = $MicrocheckStdoutPath
            stdout_sha256 = & $GetSha256 $MicrocheckStdoutPath
            stderr_path = $MicrocheckStderrPath
            stderr_sha256 = & $GetSha256 $MicrocheckStderrPath
            exit_code = [int]$MicrocheckResult.exit_code
            started_at = $MicrocheckStartedAt
            completed_at = $MicrocheckCompletedAt
        }
        $MicrocheckAuditPath = [IO.Path]::Combine($AuditRoot, '22-a7-cpu-micro-check.json')
        Write-A7NewText `
            -Path $MicrocheckAuditPath `
            -Text ($MicrocheckAudit | ConvertTo-Json -Depth 8 -Compress)
        $MicrocheckAuditSha256 = & $GetSha256 $MicrocheckAuditPath

        $Stage = 'gpu_lease'
        $LeaseResult = New-A7Lease `
            -LeasePath $LeasePath `
            -OwnerAuthorizationId $OwnerAuthorizationId `
            -RunId $RunId `
            -SourceCommit $ExpectedSourceCommit `
            -SpecCommit $ExpectedSpecCommit `
            -PlanCommit $ExpectedPlanCommit `
            -Branch $ExpectedBranch `
            -ImageTag $ImageTag `
            -ImageId $ImageId `
            -BaseImageDigest $BaseDigest `
            -GpuUuid ([string]$Preflight.gpu_uuid) `
            -CampaignRoot $CampaignRoot `
            -HistoricalBaselinePath $HistoricalPath `
            -HistoricalBaselineSha256 $HistoricalBaselineSha256 `
            -BuildAuditPath $BuildAuditPath `
            -BuildAuditSha256 (& $GetSha256 $BuildAuditPath) `
            -MicrocheckAuditPath $MicrocheckAuditPath `
            -MicrocheckAuditSha256 $MicrocheckAuditSha256 `
            -HostProcessesJson (ConvertTo-Json -InputObject @($Preflight.host_processes) -Depth 6 -Compress) `
            -ContainersJson (ConvertTo-Json -InputObject @($Preflight.containers) -Depth 6 -Compress) `
            -ClaimedAt ([DateTimeOffset]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ss.fffffffZ'))
        if (-not [IO.File]::Exists([string]$LeaseResult.path)) {
            throw 'A7 GPU lease was not published'
        }

        $Stage = 'task8'
        $Task8Arguments = @($Task8PrefixArguments) + @(
            $Task8Path,
            '-RunId', $RunId,
            '-ImageTag', $ImageTag,
            '-ImageDigest', $ImageId,
            '-HostCampaignRoot', $CampaignRoot,
            '-LeasePath', $LeasePath
        )
        $Task8Invoked = $true
        $Task8Result = Invoke-A7Native `
            -Executable $Task8Executable `
            -Arguments $Task8Arguments `
            -StdoutPath ([IO.Path]::Combine($AuditRoot, '24-task8.stdout.log')) `
            -StderrPath ([IO.Path]::Combine($AuditRoot, '24-task8.stderr.log')) `
            -WorkingDirectory $WorktreePath

        try {
            $ObservedTerminal = $null
            foreach ($Name in @(
                    '52-task7-post-task8-validation-failure.json',
                    '53-task7-post-task8-validation-closure.json'
                )) {
                $Destination = [IO.Path]::Combine($AuditRoot, $Name)
                if ([IO.File]::Exists($Destination) -or [IO.Directory]::Exists($Destination)) {
                    throw "A7 post-Task-8 evidence destination already exists: $Name"
                }
            }
            $RequiredNames = @(
                '30-historical-preservation.json',
                '40-campaign-result.json',
                '41-campaign-file-manifest.json',
                '51-campaign-closure-manifest.json'
            )
            foreach ($Name in $RequiredNames) {
                $RequiredPath = [IO.Path]::Combine($AuditRoot, $Name)
                if (-not [IO.File]::Exists($RequiredPath) -or [IO.Directory]::Exists($RequiredPath)) {
                    throw "A7 Task 8 required evidence is missing: $Name"
                }
                $RequiredItem = [IO.FileInfo]::new($RequiredPath)
                if (($RequiredItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    throw "A7 Task 8 required evidence is linked: $Name"
                }
            }
            $ResultPath = [IO.Path]::Combine($AuditRoot, '40-campaign-result.json')
            $ClosurePath = [IO.Path]::Combine($AuditRoot, '51-campaign-closure-manifest.json')
            $ReleasedLeasePath = "$LeasePath.released"
            $ReleaseRecordPath = "$LeasePath.release.json"
            foreach ($RequiredPath in @($ReleasedLeasePath, $ReleaseRecordPath)) {
                if (-not [IO.File]::Exists($RequiredPath) -or [IO.Directory]::Exists($RequiredPath)) {
                    throw 'A7 Task 8 did not publish required lease-release evidence'
                }
            }
            if ([IO.File]::Exists($LeasePath)) {
                throw 'A7 Task 8 left the active lease in place'
            }
            try {
                $Closure = [IO.File]::ReadAllText($ClosurePath, [Text.Encoding]::UTF8) |
                    ConvertFrom-Json
                $ObservedTerminal = [string]$Closure.terminal
            }
            catch { throw 'A7 Task 8 closure evidence is malformed' }
            try {
                $CampaignResult = [IO.File]::ReadAllText($ResultPath, [Text.Encoding]::UTF8) |
                    ConvertFrom-Json
            }
            catch { throw 'A7 Task 8 campaign result is malformed' }
            $Terminal = $ObservedTerminal
            if ([string]$Closure.run_id -cne $RunId -or
                [string]$CampaignResult.run_id -cne $RunId -or
                [string]$CampaignResult.terminal -cne $Terminal -or
                @($AllowedTerminals | Where-Object { $_ -ceq $Terminal }).Count -ne 1) {
                throw 'A7 Task 8 terminal binding mismatch'
            }
            $ExpectedClosurePaths = @(
                'audit/30-historical-preservation.json',
                'audit/40-campaign-result.json',
                'audit/41-campaign-file-manifest.json'
            )
            $ClosureRecords = @($Closure.files)
            if ($ClosureRecords.Count -ne $ExpectedClosurePaths.Count) {
                throw 'A7 Task 8 closure file inventory mismatch'
            }
            $ObservedClosurePaths = @($ClosureRecords | ForEach-Object { [string]$_.path })
            if ((@($ObservedClosurePaths | Sort-Object -CaseSensitive) -join "`n") -cne
                (($ExpectedClosurePaths | Sort-Object -CaseSensitive) -join "`n")) {
                throw 'A7 Task 8 closure path inventory mismatch'
            }
            foreach ($Record in $ClosureRecords) {
                $RelativePath = [string]$Record.path
                $Path = [IO.Path]::GetFullPath(
                    [IO.Path]::Combine($CampaignRoot, $RelativePath.Replace('/', '\'))
                )
                $CampaignPrefix = $CampaignRoot.TrimEnd('\') + '\'
                $File = [IO.FileInfo]::new($Path)
                if (-not $Path.StartsWith($CampaignPrefix, [StringComparison]::OrdinalIgnoreCase) -or
                    -not $File.Exists -or
                    ($File.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
                    [long]$File.Length -ne [long]$Record.size -or
                    (& $GetSha256 $Path) -cne [string]$Record.sha256) {
                    throw 'A7 Task 8 closure file hash mismatch'
                }
            }
            return [pscustomobject]@{
                state = 'CLOSED'
                terminal = $Terminal
                run_id = $RunId
                image_tag = $ImageTag
                image_id = $ImageId
                campaign_root = $CampaignRoot
                lease_path = $LeasePath
                validation_status = 'PASSED'
                task8_invocation_count = 1
                task8_exit_code = [int]$Task8Result.exit_code
            }
        }
        catch {
            $ValidationError = $_.Exception.Message
            $PostTask8 = Close-A7PostTask8ValidationFailure `
                -CampaignRoot $CampaignRoot `
                -OwnerAuthorizationId $OwnerAuthorizationId `
                -RunId $RunId `
                -SourceCommit $ExpectedSourceCommit `
                -SpecCommit $ExpectedSpecCommit `
                -PlanCommit $ExpectedPlanCommit `
                -ImageTag $ImageTag `
                -ImageId $ImageId `
                -Task8ExitCode ([int]$Task8Result.exit_code) `
                -ObservedTerminal $ObservedTerminal `
                -ValidationError $ValidationError `
                -LeasePath $LeasePath
            return [pscustomobject]@{
                state = 'CLOSED'
                terminal = $null
                run_id = $RunId
                image_tag = $ImageTag
                image_id = $ImageId
                campaign_root = $CampaignRoot
                lease_path = $LeasePath
                error = $ValidationError
                validation_status = [string]$PostTask8.validation_status
                task8_invocation_count = 1
                task8_exit_code = [int]$Task8Result.exit_code
            }
        }
    }
    catch {
        if ($Task8Invoked) { throw }
        $FailureMessage = $_.Exception.Message
        $Closed = Close-A7Campaign `
            -CampaignRoot $CampaignRoot `
            -ProtectedGitRoot $ProtectedGitRoot `
            -HistoricalBaselinePath $HistoricalPath `
            -HistoricalBaselineSha256 $HistoricalBaselineSha256 `
            -CurrentImagesJson ($CurrentImages | ConvertTo-Json -Depth 6 -Compress -AsArray) `
            -CurrentImageTag $ImageTag `
            -RunId $RunId `
            -SourceCommit $ExpectedSourceCommit `
            -Stage $Stage `
            -FailureMessage $FailureMessage `
            -LeasePath $LeasePath `
            -Terminal $TerminalInconclusive
        return [pscustomobject]@{
            state = [string]$Closed.state
            terminal = [string]$Closed.terminal
            run_id = $RunId
            image_tag = $ImageTag
            image_id = $ImageId
            campaign_root = $CampaignRoot
            lease_path = $LeasePath
            failure_stage = $Stage
            error = $FailureMessage
            task8_invocation_count = if ($Stage -ceq 'task8') { 1 } else { 0 }
            task8_exit_code = $null
        }
    }
}

function Invoke-A7Production {
    param(
        [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
        [Parameter(Mandatory = $true)][string]$ExpectedBranch,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
    )

    if (Test-Path Env:VAL_DATA_ROOT) {
        throw 'A7 production launcher requires VAL_DATA_ROOT to be unset'
    }
    $ApplicationPath = {
        param([Parameter(Mandatory = $true)][string]$Name)
        $Application = Get-Command -Name $Name -CommandType Application -ErrorAction Stop |
            Select-Object -First 1
        return [IO.Path]::GetFullPath($Application.Source)
    }
    $InvokeReadOnly = {
        param(
            [Parameter(Mandatory = $true)][string]$Executable,
            [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Arguments,
            [string]$WorkingDirectory = ''
        )
        $StartInfo = [Diagnostics.ProcessStartInfo]::new()
        $StartInfo.FileName = $Executable
        $StartInfo.UseShellExecute = $false
        $StartInfo.CreateNoWindow = $true
        $StartInfo.RedirectStandardOutput = $true
        $StartInfo.RedirectStandardError = $true
        if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
            $StartInfo.WorkingDirectory = [IO.Path]::GetFullPath($WorkingDirectory)
        }
        foreach ($Argument in $Arguments) { [void]$StartInfo.ArgumentList.Add($Argument) }
        $Process = [Diagnostics.Process]::Start($StartInfo)
        if ($null -eq $Process) { throw 'A7 read-only collector did not start' }
        $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
        $StderrTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        $Result = [pscustomobject]@{
            exit_code = [int]$Process.ExitCode
            stdout = $StdoutTask.GetAwaiter().GetResult()
            stderr = $StderrTask.GetAwaiter().GetResult()
        }
        $Process.Dispose()
        return $Result
    }
    $RequireSuccess = {
        param(
            [Parameter(Mandatory = $true)][object]$Result,
            [Parameter(Mandatory = $true)][string]$Name
        )
        if ([int]$Result.exit_code -ne 0) {
            throw "A7 $Name collector failed: $($Result.stderr)"
        }
        return [string]$Result.stdout
    }

    $GitExecutable = & $ApplicationPath 'git'
    $ScriptWorktree = [IO.Path]::GetFullPath([IO.Path]::Combine($PSScriptRoot, '..'))
    $WorktreeListResult = & $InvokeReadOnly `
        $GitExecutable @('-C', $ScriptWorktree, 'worktree', 'list', '--porcelain') $ScriptWorktree
    $WorktreeList = & $RequireSuccess $WorktreeListResult 'Git worktree-list'
    $CanonicalLine = @($WorktreeList -split "`r?`n" | Where-Object { $_.StartsWith('worktree ') }) |
        Select-Object -First 1
    if ($null -eq $CanonicalLine) { throw 'A7 canonical Git worktree is unavailable' }
    $CanonicalRoot = [IO.Path]::GetFullPath($CanonicalLine.Substring(9))
    $Resolved = Resolve-A7Worktree `
        -RepositoryRoot $CanonicalRoot `
        -ExpectedBranch $ExpectedBranch `
        -ExpectedHead $ExpectedSourceCommit
    if ([string]$Resolved.worktree -cne $ScriptWorktree) {
        throw 'A7 launcher script is not running from the reviewed registered worktree'
    }
    $PlanRelativePath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
    $SpecRelativePath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
    $PlanLog = & $InvokeReadOnly $GitExecutable @(
        '-C', $ScriptWorktree, 'log', '-1', '--format=%H', '--', $PlanRelativePath
    ) $ScriptWorktree
    $SpecLog = & $InvokeReadOnly $GitExecutable @(
        '-C', $ScriptWorktree, 'log', '-1', '--format=%H', '--', $SpecRelativePath
    ) $ScriptWorktree
    if (
        (& $RequireSuccess $PlanLog 'plan identity').Trim() -cne $ExpectedPlanCommit -or
        (& $RequireSuccess $SpecLog 'spec identity').Trim() -cne $ExpectedSpecCommit
    ) {
        throw 'A7 reviewed spec or plan commit identity mismatch'
    }
    $PlanParent = & $InvokeReadOnly $GitExecutable @(
        '-C', $ScriptWorktree, 'rev-parse', "$ExpectedPlanCommit^"
    ) $ScriptWorktree
    if ((& $RequireSuccess $PlanParent 'plan parent').Trim() -cne $ExpectedSpecCommit) {
        throw 'A7 plan is not the append-only child of the approved specification'
    }

    $DockerExecutable = & $ApplicationPath 'docker'
    $NvidiaSmiExecutable = & $ApplicationPath 'nvidia-smi'
    $WslExecutable = & $ApplicationPath 'wsl.exe'
    $PowerShellExecutable = & $ApplicationPath 'pwsh'
    $DockerContext = (& $RequireSuccess `
            (& $InvokeReadOnly $DockerExecutable @('context', 'show')) `
            'Docker context').Trim()
    $DockerVersionJson = & $RequireSuccess `
        (& $InvokeReadOnly $DockerExecutable @('version', '--format', '{{json .}}')) `
        'Docker version'
    $DockerInfoJson = & $RequireSuccess `
        (& $InvokeReadOnly $DockerExecutable @('info', '--format', '{{json .}}')) `
        'Docker info'
    $WslRunningText = & $RequireSuccess `
        (& $InvokeReadOnly $WslExecutable @('--list', '--running', '--quiet')) `
        'docker-desktop WSL'
    $WslNames = @($WslRunningText.Replace("`0", '') -split "`r?`n" | ForEach-Object { $_.Trim() })
    $DockerDesktopWslState = if (@($WslNames | Where-Object { $_ -ceq 'docker-desktop' }).Count -eq 1) {
        'Running'
    }
    else { 'Stopped' }
    $CudaImage = 'nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
    $DockerGpuCsv = & $RequireSuccess `
        (& $InvokeReadOnly $DockerExecutable @(
                'run', '--rm', '--gpus', 'all', '--network', 'none',
                '--entrypoint', 'nvidia-smi', $CudaImage,
                '--query-gpu=uuid,name,memory.total,memory.used,memory.free',
                '--format=csv,noheader,nounits'
            )) `
        'Docker GPU'
    $HostComputeCsv = & $RequireSuccess `
        (& $InvokeReadOnly $NvidiaSmiExecutable @(
                '--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory',
                '--format=csv,noheader,nounits'
            )) `
        'host compute-process'
    $ImageListText = & $RequireSuccess `
        (& $InvokeReadOnly $DockerExecutable @(
                'image', 'ls', '--filter', 'reference=vision-active-learning-loop:wave0-*',
                '--format', '{{.Repository}}:{{.Tag}}'
            )) `
        'historical image-list'
    $HistoricalTags = @($ImageListText -split "`r?`n" | Where-Object {
            -not [string]::IsNullOrWhiteSpace($_)
        } | Sort-Object -CaseSensitive -Unique)
    $HistoricalImages = [System.Collections.Generic.List[object]]::new()
    foreach ($Tag in $HistoricalTags) {
        $ImageId = (& $RequireSuccess `
                (& $InvokeReadOnly $DockerExecutable @('image', 'inspect', '--format', '{{.Id}}', '--', $Tag)) `
                "historical image $Tag").Trim()
        if ($ImageId -cnotmatch '^sha256:[0-9a-f]{64}$') {
            throw "A7 historical image ID is invalid: $Tag"
        }
        [void]$HistoricalImages.Add([pscustomobject][ordered]@{ tag = $Tag; image_id = $ImageId })
    }
    $RegisteredImageIds = @($HistoricalImages | ForEach-Object { [string]$_.image_id })
    $DockerPsText = & $RequireSuccess `
        (& $InvokeReadOnly $DockerExecutable @('ps', '--no-trunc', '--quiet')) `
        'Docker project-container list'
    $ContainerRecords = [System.Collections.Generic.List[object]]::new()
    $ContainerIds = @($DockerPsText -split "`r?`n" | Where-Object {
            -not [string]::IsNullOrWhiteSpace($_)
        })
    foreach ($ContainerId in $ContainerIds) {
        if ($ContainerId -cnotmatch '^[0-9a-f]{64}$') {
            throw 'A7 running container ID is invalid'
        }
        $InspectText = & $RequireSuccess `
            (& $InvokeReadOnly $DockerExecutable @(
                    'container', 'inspect', '--format', '{{json .}}', '--', $ContainerId
                )) `
            "Docker project-container inspect $ContainerId"
        try { $Inspected = @($InspectText | ConvertFrom-Json) }
        catch { throw "A7 running container inspect JSON is invalid: $ContainerId" }
        if ($Inspected.Count -ne 1 -or [string]$Inspected[0].Id -cne $ContainerId) {
            throw "A7 running container inspect identity mismatch: $ContainerId"
        }
        $ContainerName = [string]$Inspected[0].Name
        if ($ContainerName.StartsWith('/', [StringComparison]::Ordinal)) {
            $ContainerName = $ContainerName.Substring(1)
        }
        [void]$ContainerRecords.Add([pscustomobject][ordered]@{
                id = $ContainerId
                name = $ContainerName
                configured_image = [string]$Inspected[0].Config.Image
                image_id = [string]$Inspected[0].Image
            })
    }
    $ProjectContainers = @(Select-A7ProjectContainers `
            -ContainerRecordsJson (ConvertTo-Json -InputObject @($ContainerRecords) -Depth 6 -Compress) `
            -RegisteredImageIdsJson (ConvertTo-Json -InputObject $RegisteredImageIds -Compress))
    $ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
    $LeaseRoot = [IO.Path]::Combine($ArtifactRoot, 'leases')
    if (-not [IO.Directory]::Exists($LeaseRoot)) { throw 'A7 project lease root is missing' }
    $ActiveLeasePaths = @(
        [IO.Directory]::EnumerateFiles($LeaseRoot, '*.json', [IO.SearchOption]::TopDirectoryOnly) |
            Where-Object { -not $_.EndsWith('.release.json', [StringComparison]::OrdinalIgnoreCase) } |
            Sort-Object -CaseSensitive
    )
    $Preflight = Test-A7DockerGpuPreflight `
        -DockerContext $DockerContext `
        -DockerVersionJson $DockerVersionJson `
        -DockerInfoJson $DockerInfoJson `
        -DockerDesktopWslState $DockerDesktopWslState `
        -DockerGpuCsv $DockerGpuCsv `
        -HostComputeCsv $HostComputeCsv `
        -ProjectContainersJson (ConvertTo-Json -InputObject $ProjectContainers -Depth 6 -Compress) `
        -ActiveLeasePathsJson (ConvertTo-Json -InputObject @($ActiveLeasePaths) -Compress) `
        -ValDataRoot ([string]$env:VAL_DATA_ROOT)

    $RootBaselinePath = [IO.Path]::Combine(
        [IO.Path]::GetTempPath(),
        'val-a7-launcher-prechange-d9ec502f4035876b39446bc9b3a943d36d51e485.json'
    )
    $RootBaselineSha256 = '0566e4339e4f9d286903c557f68aecf062b3187e454aec528fc7c1311661162e'
    $BaselineTimestamp = [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
    $AugmentedBaselinePath = [IO.Path]::Combine(
        [IO.Path]::GetTempPath(),
        "val-a7-augmented-baseline-$($ExpectedSourceCommit.Substring(0, 12))-$BaselineTimestamp.json"
    )
    $Augmented = New-A7AugmentedBaseline `
        -OriginalBaselinePath $RootBaselinePath `
        -ExpectedBaselineSha256 $RootBaselineSha256 `
        -ArtifactRoot $ArtifactRoot `
        -ProtectedGitRoot $ScriptWorktree `
        -ImageRecordsJson (ConvertTo-Json -InputObject @($HistoricalImages) -Depth 6 -Compress) `
        -SourceCommit $ExpectedSourceCommit `
        -GitExecutable $GitExecutable `
        -ExpectedSpecCommit $ExpectedSpecCommit `
        -ExpectedPlanCommit $ExpectedPlanCommit `
        -OutputPath $AugmentedBaselinePath

    $RunId = 'wave0-a7-' + [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
    return Invoke-A7Launch `
        -RegisteredWorktree $ScriptWorktree `
        -ProtectedGitRoot $ScriptWorktree `
        -ArtifactRoot $ArtifactRoot `
        -LeaseRoot $LeaseRoot `
        -HistoricalBaselinePath ([string]$Augmented.path) `
        -HistoricalBaselineSha256 ([string]$Augmented.sha256) `
        -HistoricalImagesJson (ConvertTo-Json -InputObject @($HistoricalImages) -Depth 6 -Compress) `
        -PreflightJson (ConvertTo-Json -InputObject $Preflight -Depth 8 -Compress) `
        -RunId $RunId `
        -ExpectedSourceCommit $ExpectedSourceCommit `
        -ExpectedSpecCommit $ExpectedSpecCommit `
        -ExpectedPlanCommit $ExpectedPlanCommit `
        -ExpectedBranch $ExpectedBranch `
        -OwnerAuthorizationId $OwnerAuthorizationId `
        -DockerExecutable $DockerExecutable `
        -DockerPrefixArguments @() `
        -Task8Executable $PowerShellExecutable `
        -Task8PrefixArguments @('-NoProfile', '-NonInteractive', '-File') `
        -Task8RunnerPath ([IO.Path]::Combine($ScriptWorktree, 'scripts', 'run_wave0_a7.ps1'))
}

function Get-A7ProductionExitCode {
    param([Parameter(Mandatory = $true)][object]$Result)

    $ValidationProperty = $Result.PSObject.Properties['validation_status']
    $Task8ExitProperty = $Result.PSObject.Properties['task8_exit_code']
    if (
        ($null -ne $ValidationProperty -and [string]$ValidationProperty.Value -ceq 'FAILED') -or
        $null -eq $Task8ExitProperty -or
        $null -eq $Task8ExitProperty.Value
    ) {
        return 2
    }
    return [int]$Task8ExitProperty.Value
}

$A7ProductionResult = Invoke-A7Production `
    -ExpectedSourceCommit $ExpectedSourceCommit `
    -ExpectedSpecCommit $ExpectedSpecCommit `
    -ExpectedPlanCommit $ExpectedPlanCommit `
    -ExpectedBranch $ExpectedBranch `
    -OwnerAuthorizationId $OwnerAuthorizationId
$A7ProductionResult | ConvertTo-Json -Depth 8 -Compress
$A7ProductionExitCode = Get-A7ProductionExitCode -Result $A7ProductionResult
exit $A7ProductionExitCode
