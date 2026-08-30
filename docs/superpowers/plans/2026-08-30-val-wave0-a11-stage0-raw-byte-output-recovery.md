# Wave 0 A11 Stage 0 Raw-Byte Output Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the consumed v10 Stage 0 NO_GO and prove one fresh v11 Stage 0 through an exact raw UTF-8/LF child and parent output protocol, then stop before downstream recovery.

**Architecture:** Two fresh plan-pinned PowerShell files live in one ignored v11 namespace. Stage 0 writes one terminal through the raw standard-output stream; the controller captures raw child streams, suppresses async completion objects, verifies exact bytes, then writes two exact raw lines to its parent. One read-only closure records `ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED` and performs no parser/scalar or model work.

**Tech Stack:** Git linked worktree, PowerShell 7.6.4 Core, Windows PowerShell 5.1 parser API, .NET `ProcessStartInfo`, strict UTF-8, SHA-256, Authenticode, and `apply_patch`-only authoring.

## Global Constraints

- Repository: `<repo>\.worktrees\wave0-model-contract`.
- Canonical checkout: `<repo>`; it is read-only and must remain clean.
- Branch: `codex/wave0-model-contract`.
- Entry HEAD must be this committed plan, whose direct parent is design commit `29470670c4fe2095c0cedcf5ab389c2c82190e9c` and design blob is `8ead81be4da26dbd3e17badade45b7c746e8f8ce`.
- Exact author and committer: `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Exact plan subject: `docs: plan A11 Stage 0 raw byte output recovery`.
- The plan commit changes only `docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md`.
- The v11 namespace and both v11 sources must be absent at plan commit and execution entry.
- Runtime artifacts are ignored evidence; no runtime artifact is committed.
- All file creation uses `apply_patch` with full shared-root-relative headers under patch authority `<workspace>`; shell writers, copy, move, rename, repair, deletion, cleanup, and alternate headers are forbidden.
- The two-file materialization patch, controller invocation, child start, and closure observation are each single-use. Any API uncertainty, timeout, disconnect, partial result, unexpected output, or identity difference is a preserved NO_GO and never permission to retry.
- v10 remains immutable `ENTRYV10_STAGE0_UNPROVABLE / NO_GO`; never invoke, import, dot-source, edit, copy, move, rename, delete, complete, or reinterpret a v10 artifact.
- Do not execute parser/scalar TDD, dual-parser worker phases, preserved-inventory construction, formal entry, report creation, child-exit recovery, Docker, WSL, GPU, CUDA, WDDM, A11 runtime, model work, RDD, Wave 1, product work, network work, or an `OwnerAuthorizationId` flow.
- Do not create a remote, push, merge, rebase, reset, stash, amend, squash, cherry-pick, tag, release, publish, deploy, or modify another repository.
- The frozen PowerShell 7 controller/child executable is `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`.
- The Windows PowerShell executable is `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`; it is used only for parser admission and file/signature evidence, never as the v11 child.
- Success stops at `ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED`.

## File Map

| Path | Responsibility |
|---|---|
| `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1` | Self-attests the v11/predecessor/runtime envelope, starts exactly one Stage 0 child, captures raw streams, suppresses task-result objects, verifies exact child bytes, and emits exact two-line raw parent output. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-v11.ps1` | Rechecks the read-only admission envelope and emits exactly one raw UTF-8/LF Stage 0 terminal without using the PowerShell success stream. |

The successful v11 namespace contains exactly those two files and no directory child, marker, report, manifest, result, transcript, cache, bytecode, temporary, repair, or machine object.

## Frozen records

```text
PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO
SOURCE_IDENTITY|task-1-stage0-raw-byte-controller-v11.ps1|28071|e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9
SOURCE_IDENTITY|task-1-stage0-v11.ps1|21104|c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa
```

The two `SOURCE_IDENTITY` records are the exact decimal byte counts and lowercase SHA-256 values computed from the complete LF-terminated blocks below.

## Frozen source blocks

#### Frozen source: `task-1-stage0-raw-byte-controller-v11.ps1`

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$WorkspacePath = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$ControllerPath = Join-Path $WorkspacePath 'task-1-stage0-raw-byte-controller-v11.ps1'
$Stage0Path = Join-Path $WorkspacePath 'task-1-stage0-v11.ps1'
$V10Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'
$V10MarkerPath = Join-Path $V10Workspace 'task-0-patch-root-binding-v10.txt'
$ExternalV9Workspace = '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$IntendedV9Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$V8Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'
$V7Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md'
$V10PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery.md'
$V10DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery-design.md'
$V9PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery.md'
$V9DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery-design.md'
$V8PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery.md'
$ParserDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md'
$AmendmentPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-security-module-amendment-design.md'
$V7PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md'
$V7DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md'
$ExpectedDesign = '29470670c4fe2095c0cedcf5ab389c2c82190e9c'
$ExpectedDesignBlob = '8ead81be4da26dbd3e17badade45b7c746e8f8ce'
$ExpectedV10Plan = '0997117b53cca977e232e44eeda85e426a4e9328'
$ExpectedV10PlanBlob = '7ad8da8cbedfa614fd5d2e85b89b0ee43801861f'
$ExpectedV10Design = '17bef41a33439fe47de42cce252118b10cee9af1'
$ExpectedV10DesignBlob = 'c97f5ac2f2ed30b6b8d2036e53c3957c359a43b0'
$ExpectedV9Plan = '03bc963ac69e26da1d338a448481c82f35f66f1d'
$ExpectedV9PlanBlob = '17f42b6019dd6575fb98e3501ed55cce89afa06c'
$ExpectedV9Design = 'c71d824d3d249e92fe92dfc872aa53ba3d53facd'
$ExpectedV9DesignBlob = 'e3785d6bb305cf57b05114bdf9cd17a884e14491'
$ExpectedV8Plan = 'ab84df410605c824ba42ecd274bbcd6ba4670f19'
$ExpectedV8PlanBlob = '4bd91b8b9aeec55c18d8c14056b1176e511be967'
$ExpectedAmendment = '5d7500abef12ff724d0fb9c256a1894979bd8677'
$ExpectedAmendmentBlob = '20661c3572d8723d7c52c4d745703a5f7741b8dd'
$ExpectedParserDesign = '0788f6143691d5a39730fb06508be3949de1b3f0'
$ExpectedParserDesignBlob = 'a837d94d58d8ad2ee1c71fd51de64257fe49d060'
$ExpectedV7Plan = '483cf5fd7886bdbc26aefb82d800333d9e001d6d'
$ExpectedV7PlanBlob = '5ed0f6819deb12b0ab6b204624a9278e9b35289e'
$ExpectedV7Design = 'c558c0a9a1ce02c3162305b4b7bf6592a905432a'
$ExpectedV7DesignBlob = '5bfa3ded2c55acf48b3e193a9fbb53d126e945ad'
$FrozenPwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$FrozenWindowsPowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$PwshSecurityManifest = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$PwshSecurityDll = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll'
$WindowsSecurityManifest = 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$WindowsSecurityDll = 'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll'
$ExpectedStage0Terminal = 'ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'
$TransportTerminal = 'ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$ExpectedV10 = [ordered]@{
    'task-0-patch-root-binding-v10.txt' = @([long]1058, 'd3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5')
    'task-1-stage0-transport-controller-v10.ps1' = @([long]22802, '2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e')
    'task-1-stage0-v10.ps1' = @([long]25072, '5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')
}
$ExpectedExternalV9 = [ordered]@{
    'task-1-stage0-transport-controller-v9.ps1' = @([long]17994, '795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff')
    'task-1-stage0-v9.ps1' = @([long]20258, '34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')
}
$ExpectedV7 = [ordered]@{
    'task-1-stage0-audit-v7.ps1' = @([long]3849, 'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b')
    'task-1-scalar-identity-tests-v7.ps1' = @([long]8849, '977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9')
    'task-1-scalar-identity-red-v7.psm1' = @([long]991, '34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919')
    'task-1-scalar-identity-green-v7.psm1' = @([long]2553, 'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')
}
$V11ShadowPaths = @(
    '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
)

function Get-A11V11BytesSha256 {
    param([Parameter(Mandatory)] [byte[]] $Bytes)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $Algorithm.Dispose() }
}

function Get-A11V11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant() }
    finally { $Algorithm.Dispose(); $Stream.Dispose() }
}

function Assert-A11V11ParentChainOrdinary {
    param([Parameter(Mandatory)] [string] $Path)
    $Cursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path))
    while (-not [string]::IsNullOrEmpty($Cursor)) {
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$Item.LinkType)) { throw 'linked parent rejected' }
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        $Cursor = $Parent.FullName
    }
}

function Assert-A11V11FileIdentity {
    param([string] $Path, [long] $ByteCount, [string] $Sha256, [string] $LeafLinkType, [string] $FileVersion = '', [string] $ProductVersion = '')
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path), $Path)) { throw 'file path rejected' }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or [long]$Item.Length -ne $ByteCount -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'file identity rejected' }
    $ActualLink = if ([string]::IsNullOrEmpty([string]$Item.LinkType)) { 'None' } else { [string]$Item.LinkType }
    if (-not [StringComparer]::Ordinal.Equals($ActualLink, $LeafLinkType)) { throw 'file link type rejected' }
    Assert-A11V11ParentChainOrdinary -Path $Path
    if (-not [StringComparer]::Ordinal.Equals((Get-A11V11FileSha256 -Path $Path), $Sha256)) { throw 'file digest rejected' }
    $Streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if ($Streams.Count -ne 1 -or [string]$Streams[0].Stream -cne ':$DATA') { throw 'file stream rejected' }
    if (-not [string]::IsNullOrEmpty($FileVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.FileVersion, $FileVersion)) { throw 'file version rejected' }
    if (-not [string]::IsNullOrEmpty($ProductVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.ProductVersion, $ProductVersion)) { throw 'product version rejected' }
}

function Assert-A11V11SourceIdentity {
    param([string] $Path, [long] $ByteCount, [string] $Sha256)
    Assert-A11V11FileIdentity -Path $Path -ByteCount $ByteCount -Sha256 $Sha256 -LeafLinkType 'None'
    $Bytes = [IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -eq 0 -or ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) -or $Bytes -contains 0x0D -or $Bytes[-1] -ne 0x0A -or ($Bytes.Length -gt 1 -and $Bytes[-2] -eq 0x0A)) { throw 'source encoding rejected' }
    $RoundTrip = $Utf8.GetBytes($Utf8.GetString($Bytes))
    if ($RoundTrip.Length -ne $Bytes.Length -or (Get-A11V11BytesSha256 -Bytes $RoundTrip) -cne $Sha256) { throw 'source UTF-8 round trip rejected' }
    $Streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if ($Streams.Count -ne 1 -or [string]$Streams[0].Stream -cne ':$DATA') { throw 'source stream rejected' }
}

function Get-A11V11PlanSourceIdentity {
    param([Parameter(Mandatory)] [string] $Name)
    $PlanText = $Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath)))
    $Matches = @($PlanText.Split([char]10) | Where-Object { $_.StartsWith("SOURCE_IDENTITY|$Name|", [StringComparison]::Ordinal) })
    if ($Matches.Count -ne 1) { throw 'plan source identity count rejected' }
    $Parts = @($Matches[0].Split('|'))
    [long]$Count = 0
    if ($Parts.Count -ne 4 -or -not [long]::TryParse($Parts[2], [Globalization.NumberStyles]::None, [Globalization.CultureInfo]::InvariantCulture, [ref]$Count) -or $Parts[3] -notmatch '\A[0-9a-f]{64}\z') { throw 'plan source identity rejected' }
    [pscustomobject][ordered]@{ byte_count = $Count; sha256 = $Parts[3] }
}

function Get-A11V11WorkspaceSnapshot {
    param([Parameter(Mandatory)] [string] $Path)
    $Records = New-Object 'Collections.Generic.List[string]'
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force | Sort-Object Name)) {
        if ($Item.PSIsContainer) { throw 'workspace nested directory rejected' }
        [void]$Records.Add("$($Item.Name)|$([long]$Item.Length)|$(Get-A11V11FileSha256 -Path $Item.FullName)")
    }
    [string]::Join("`n", $Records)
}

function Get-A11V11ExpectedV10MarkerText {
    $Header = 'CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-0-patch-root-binding-v10.txt'
    $Lines = @('schema_version=1','binding_id=entryv10-patch-root-binding-001',"source_plan_commit=$ExpectedV10Plan","source_design_commit=$ExpectedV10Design","source_design_blob=$ExpectedV10DesignBlob",'patch_authority_root=<workspace>',"patch_header=$Header","repository_root=$RepositoryRoot","workspace_path=$V10Workspace","canonical_target=$V10MarkerPath",'failed_v9_terminal=ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO')
    [string]::Join("`n", $Lines) + "`n"
}

function Assert-A11V11PreservedEvidence {
    $V10Children = @(Get-ChildItem -LiteralPath $V10Workspace -Force | Sort-Object Name)
    if ($V10Children.Count -ne 3 -or @($V10Children | Where-Object PSIsContainer).Count -ne 0) { throw 'v10 inventory rejected' }
    foreach ($Name in $ExpectedV10.Keys) { Assert-A11V11FileIdentity -Path (Join-Path $V10Workspace $Name) -ByteCount $ExpectedV10[$Name][0] -Sha256 $ExpectedV10[$Name][1] -LeafLinkType 'None' }
    $ExpectedMarker = Get-A11V11ExpectedV10MarkerText
    if ($Utf8.GetString([IO.File]::ReadAllBytes($V10MarkerPath)) -cne $ExpectedMarker) { throw 'v10 marker text rejected' }
    if (Test-Path -LiteralPath $IntendedV9Workspace) { throw 'intended v9 namespace exists' }
    $V9Children = @(Get-ChildItem -LiteralPath $ExternalV9Workspace -Force | Sort-Object Name)
    if ($V9Children.Count -ne 2 -or @($V9Children | Where-Object PSIsContainer).Count -ne 0) { throw 'external v9 inventory rejected' }
    foreach ($Name in $ExpectedExternalV9.Keys) { Assert-A11V11FileIdentity -Path (Join-Path $ExternalV9Workspace $Name) -ByteCount $ExpectedExternalV9[$Name][0] -Sha256 $ExpectedExternalV9[$Name][1] -LeafLinkType 'None' }
    if (Test-Path -LiteralPath $V8Workspace -or Test-Path -LiteralPath $ConsumedV6Workspace) { throw 'consumed predecessor namespace exists' }
    foreach ($Path in $V11ShadowPaths) { if (Test-Path -LiteralPath $Path) { throw 'v11 shadow path exists' } }
    $PlanText = $Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath)))
    $Incident = 'PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO'
    if (@($PlanText.Split([char]10) | Where-Object { $_ -ceq $Incident }).Count -ne 1) { throw 'v10 incident record rejected' }
}

function Assert-A11V11Signature {
    param([object] $Signature, [string] $Subject, [string] $Thumbprint)
    if ($Signature.Status.ToString() -cne 'Valid' -or $null -eq $Signature.SignerCertificate -or [string]$Signature.SignerCertificate.Subject -cne $Subject -or -not [StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint, $Thumbprint)) { throw 'signature rejected' }
}

function Assert-A11V11LineageAndGit {
    $PlanCommit = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $PlanCommit -notmatch '\A[0-9a-f]{40}\z') { throw 'plan commit rejected' }
    $Chain = @(@($PlanCommit,$ExpectedDesign),@($ExpectedDesign,$ExpectedV10Plan),@($ExpectedV10Plan,$ExpectedV10Design),@($ExpectedV10Design,$ExpectedV9Plan),@($ExpectedV9Plan,$ExpectedV9Design),@($ExpectedV9Design,$ExpectedV8Plan),@($ExpectedV8Plan,$ExpectedAmendment),@($ExpectedAmendment,$ExpectedParserDesign),@($ExpectedParserDesign,$ExpectedV7Plan),@($ExpectedV7Plan,$ExpectedV7Design))
    foreach ($Pair in $Chain) { if ((git rev-list --parents -n 1 $Pair[0]) -cne "$($Pair[0]) $($Pair[1])") { throw 'lineage rejected' } }
    if ((git branch --show-current) -cne 'codex/wave0-model-contract') { throw 'branch rejected' }
    if ((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD) -cne 'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 raw byte output recovery') { throw 'plan identity rejected' }
    $Changed = @(git diff-tree --no-commit-id --name-only -r HEAD)
    if ($Changed.Count -ne 1 -or $Changed[0] -cne $PlanPath) { throw 'plan path rejected' }
    $Blobs = @(@('HEAD',$DesignPath,$ExpectedDesignBlob),@($ExpectedV10Plan,$V10PlanPath,$ExpectedV10PlanBlob),@($ExpectedV10Design,$V10DesignPath,$ExpectedV10DesignBlob),@($ExpectedV9Plan,$V9PlanPath,$ExpectedV9PlanBlob),@($ExpectedV9Design,$V9DesignPath,$ExpectedV9DesignBlob),@($ExpectedV8Plan,$V8PlanPath,$ExpectedV8PlanBlob),@($ExpectedAmendment,$AmendmentPath,$ExpectedAmendmentBlob),@($ExpectedParserDesign,$ParserDesignPath,$ExpectedParserDesignBlob),@($ExpectedV7Plan,$V7PlanPath,$ExpectedV7PlanBlob),@($ExpectedV7Design,$V7DesignPath,$ExpectedV7DesignBlob))
    foreach ($Record in $Blobs) { if ((git rev-parse "$($Record[0]):$($Record[1])") -cne $Record[2]) { throw 'blob lineage rejected' } }
    if (-not [string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'superproject rejected' }
    if ([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)), [IO.Path]::GetFullPath((git rev-parse --git-common-dir)))) { throw 'linked worktree isolation rejected' }
    if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0 -or @(git diff --cached --name-only).Count -ne 0 -or @(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'Git cleanliness rejected' }
}

function Assert-A11V11RuntimeAndProviders {
    Assert-A11V11FileIdentity -Path $FrozenPwsh -ByteCount 301368 -Sha256 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V11FileIdentity -Path $FrozenWindowsPowerShell -ByteCount 454656 -Sha256 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.8875 (WinBuild.160101.0800)' -ProductVersion '10.0.26100.8875'
    Assert-A11V11FileIdentity -Path $PwshSecurityManifest -ByteCount 15463 -Sha256 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' -LeafLinkType 'None'
    Assert-A11V11FileIdentity -Path $PwshSecurityDll -ByteCount 345952 -Sha256 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V11FileIdentity -Path $WindowsSecurityManifest -ByteCount 776 -Sha256 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' -LeafLinkType 'HardLink'
    Assert-A11V11FileIdentity -Path $WindowsSecurityDll -ByteCount 93696 -Sha256 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.1' -ProductVersion '10.0.26100.1'
}

$Failure = $null
$FailurePhase = 'controller_preflight'
$StartCount = [long]0
$ChildStarted = $false
$ExitCodeAvailable = $false
$ExitCode = 0
$TimedOut = $false
$StdoutComplete = $false
$StderrComplete = $false
$StdoutBytes = [byte[]]::new(0)
$StderrBytes = [byte[]]::new(0)
$ParentBytes = $null
$SecurityModule = $null
$LocationPushed = $false

try {
    $CurrentProcessPath = [IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath, $FrozenPwsh) -or $PSVersionTable.PSVersion.ToString() -cne '7.6.4' -or $PSVersionTable.PSEdition -cne 'Core') { throw 'controller_runtime_rejected' }
    Push-Location -LiteralPath $RepositoryRoot
    $LocationPushed = $true
    Assert-A11V11LineageAndGit
    Assert-A11V11PreservedEvidence
    Assert-A11V11RuntimeAndProviders
    $ControllerIdentity = Get-A11V11PlanSourceIdentity -Name 'task-1-stage0-raw-byte-controller-v11.ps1'
    $Stage0Identity = Get-A11V11PlanSourceIdentity -Name 'task-1-stage0-v11.ps1'
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($PSCommandPath), $ControllerPath)) { throw 'controller_path_rejected' }
    Assert-A11V11SourceIdentity -Path $ControllerPath -ByteCount $ControllerIdentity.byte_count -Sha256 $ControllerIdentity.sha256
    Assert-A11V11SourceIdentity -Path $Stage0Path -ByteCount $Stage0Identity.byte_count -Sha256 $Stage0Identity.sha256
    $Children = @(Get-ChildItem -LiteralPath $WorkspacePath -Force | Sort-Object Name)
    $ExpectedNames = @('task-1-stage0-raw-byte-controller-v11.ps1','task-1-stage0-v11.ps1') | Sort-Object
    if ($Children.Count -ne 2 -or @($Children | Where-Object PSIsContainer).Count -ne 0 -or [string]::Join("`n", @($Children.Name)) -cne [string]::Join("`n", $ExpectedNames)) { throw 'v11_inventory_rejected' }
    $V7Children = @(Get-ChildItem -LiteralPath $V7Workspace -Force)
    if ($V7Children.Count -ne 4 -or @($V7Children | Where-Object PSIsContainer).Count -ne 0) { throw 'v7_inventory_rejected' }
    foreach ($Name in $ExpectedV7.Keys) { Assert-A11V11FileIdentity -Path (Join-Path $V7Workspace $Name) -ByteCount $ExpectedV7[$Name][0] -Sha256 $ExpectedV7[$Name][1] -LeafLinkType 'None' }
    $Before = Get-A11V11WorkspaceSnapshot -Path $WorkspacePath

    $SecurityModule = Import-Module -Name $PwshSecurityManifest -Force -PassThru -ErrorAction Stop
    if (@($SecurityModule).Count -ne 1 -or [IO.Path]::GetFullPath([string]$SecurityModule.Path) -cne $PwshSecurityManifest -or @($SecurityModule.NestedModules).Count -ne 1 -or [IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path) -cne $PwshSecurityDll) { throw 'controller_security_provider_rejected' }
    $AuthCommand = Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop
    if (@($AuthCommand).Count -ne 1 -or [IO.Path]::GetFullPath([string]$AuthCommand.Module.Path) -cne $PwshSecurityManifest -or [IO.Path]::GetFullPath([string]$AuthCommand.DLL) -cne $PwshSecurityDll) { throw 'controller_authenticode_provenance_rejected' }
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $FrozenPwsh) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $FrozenWindowsPowerShell) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityManifest) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityDll) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityManifest) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '71F53A26BB1625E466727183409A30D03D7923DF'
    Assert-A11V11Signature -Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityDll) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '71F53A26BB1625E466727183409A30D03D7923DF'

    $StartInfo = [Diagnostics.ProcessStartInfo]::new()
    $StartInfo.FileName = $FrozenPwsh
    $StartInfo.UseShellExecute = $false
    $StartInfo.RedirectStandardInput = $true
    $StartInfo.RedirectStandardOutput = $true
    $StartInfo.RedirectStandardError = $true
    $StartInfo.CreateNoWindow = $true
    $StartInfo.WorkingDirectory = $RepositoryRoot
    foreach ($Argument in @('-NoLogo','-NoProfile','-NonInteractive','-File',$Stage0Path)) { [void]$StartInfo.ArgumentList.Add([string]$Argument) }
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = $StartInfo
    $StdoutBuffer = [IO.MemoryStream]::new()
    $StderrBuffer = [IO.MemoryStream]::new()
    try {
        $FailurePhase = 'child_start'
        if (-not $Process.Start()) { throw 'child_start_rejected' }
        $ChildStarted = $true
        $StartCount = [long]1
        [void]$Process.StandardInput.Close()
        $StdoutTask = $Process.StandardOutput.BaseStream.CopyToAsync($StdoutBuffer)
        $StderrTask = $Process.StandardError.BaseStream.CopyToAsync($StderrBuffer)
        $FailurePhase = 'child_capture'
        $TimedOut = -not $Process.WaitForExit(120000)
        if ($TimedOut) { [void]$Process.Kill($true); [void]$Process.WaitForExit() }
        [void]$StdoutTask.GetAwaiter().GetResult()
        $StdoutComplete = $true
        [void]$StderrTask.GetAwaiter().GetResult()
        $StderrComplete = $true
        $StdoutBytes = [byte[]]$StdoutBuffer.ToArray()
        $StderrBytes = [byte[]]$StderrBuffer.ToArray()
        if ($TimedOut) { throw 'child_timeout' }
        $ExitCode = [int]$Process.ExitCode
        $ExitCodeAvailable = $true
    }
    finally {
        [void]$StdoutBuffer.Dispose()
        [void]$StderrBuffer.Dispose()
        [void]$Process.Dispose()
    }
    $FailurePhase = 'child_admission'
    if ($StartCount -ne 1 -or -not $ExitCodeAvailable -or $ExitCode -ne 0 -or -not $StdoutComplete -or -not $StderrComplete -or $StderrBytes.Length -ne 0) { throw 'child_result_rejected' }
    $ExpectedChildBytes = $Utf8.GetBytes($ExpectedStage0Terminal + "`n")
    if ($StdoutBytes.Length -ne $ExpectedChildBytes.Length -or (Get-A11V11BytesSha256 -Bytes $StdoutBytes) -cne (Get-A11V11BytesSha256 -Bytes $ExpectedChildBytes) -or $Utf8.GetString($StdoutBytes) -cne ($ExpectedStage0Terminal + "`n")) { throw 'child_stdout_rejected' }
    if ((Get-A11V11WorkspaceSnapshot -Path $WorkspacePath) -cne $Before) { throw 'child_side_effect_rejected' }
    $ParentBytes = $Utf8.GetBytes($ExpectedStage0Terminal + "`n" + $TransportTerminal + "`n")
}
catch {
    $Failure = [string]$_.Exception.Message
}
finally {
    if ($null -ne $SecurityModule) { [void](Remove-Module -ModuleInfo $SecurityModule -Force -ErrorAction SilentlyContinue) }
    if ($LocationPushed) { [void](Pop-Location) }
}

if ($null -ne $Failure) {
    $FailureDigest = Get-A11V11BytesSha256 -Bytes $Utf8.GetBytes($Failure)
    $StdoutDigest = if ($StdoutComplete) { Get-A11V11BytesSha256 -Bytes $StdoutBytes } else { 'unavailable' }
    $StderrDigest = if ($StderrComplete) { Get-A11V11BytesSha256 -Bytes $StderrBytes } else { 'unavailable' }
    $ExitText = if ($ExitCodeAvailable) { [string]$ExitCode } else { 'unavailable' }
    $Diagnostic = "ENTRYV11_CONTROLLER_DIAGNOSTIC|phase=$FailurePhase|child_started=$($ChildStarted.ToString().ToLowerInvariant())|starts=$StartCount|exit=$ExitText|timed_out=$($TimedOut.ToString().ToLowerInvariant())|stdout_complete=$($StdoutComplete.ToString().ToLowerInvariant())|stdout_bytes=$($StdoutBytes.Length)|stdout_sha256=$StdoutDigest|stderr_complete=$($StderrComplete.ToString().ToLowerInvariant())|stderr_bytes=$($StderrBytes.Length)|stderr_sha256=$StderrDigest|exception_sha256=$FailureDigest`n"
    $DiagnosticBytes = $Utf8.GetBytes($Diagnostic)
    $ErrorStream = [Console]::OpenStandardError()
    [void]$ErrorStream.Write($DiagnosticBytes, 0, $DiagnosticBytes.Length)
    [void]$ErrorStream.Flush()
    exit 1
}

$OutputStream = [Console]::OpenStandardOutput()
[void]$OutputStream.Write($ParentBytes, 0, $ParentBytes.Length)
[void]$OutputStream.Flush()
```

#### Frozen source: `task-1-stage0-v11.ps1`

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$WorkspacePath = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$ControllerPath = Join-Path $WorkspacePath 'task-1-stage0-raw-byte-controller-v11.ps1'
$Stage0Path = Join-Path $WorkspacePath 'task-1-stage0-v11.ps1'
$V10Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'
$V10MarkerPath = Join-Path $V10Workspace 'task-0-patch-root-binding-v10.txt'
$ExternalV9Workspace = '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$IntendedV9Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$V8Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'
$V7Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md'
$V10PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery.md'
$V10DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery-design.md'
$V9PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery.md'
$V9DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery-design.md'
$V8PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery.md'
$ParserDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md'
$AmendmentPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-security-module-amendment-design.md'
$V7PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md'
$V7DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md'
$ExpectedDesign = '29470670c4fe2095c0cedcf5ab389c2c82190e9c'
$ExpectedDesignBlob = '8ead81be4da26dbd3e17badade45b7c746e8f8ce'
$ExpectedV10Plan = '0997117b53cca977e232e44eeda85e426a4e9328'
$ExpectedV10PlanBlob = '7ad8da8cbedfa614fd5d2e85b89b0ee43801861f'
$ExpectedV10Design = '17bef41a33439fe47de42cce252118b10cee9af1'
$ExpectedV10DesignBlob = 'c97f5ac2f2ed30b6b8d2036e53c3957c359a43b0'
$ExpectedV9Plan = '03bc963ac69e26da1d338a448481c82f35f66f1d'
$ExpectedV9PlanBlob = '17f42b6019dd6575fb98e3501ed55cce89afa06c'
$ExpectedV9Design = 'c71d824d3d249e92fe92dfc872aa53ba3d53facd'
$ExpectedV9DesignBlob = 'e3785d6bb305cf57b05114bdf9cd17a884e14491'
$ExpectedV8Plan = 'ab84df410605c824ba42ecd274bbcd6ba4670f19'
$ExpectedV8PlanBlob = '4bd91b8b9aeec55c18d8c14056b1176e511be967'
$ExpectedAmendment = '5d7500abef12ff724d0fb9c256a1894979bd8677'
$ExpectedAmendmentBlob = '20661c3572d8723d7c52c4d745703a5f7741b8dd'
$ExpectedParserDesign = '0788f6143691d5a39730fb06508be3949de1b3f0'
$ExpectedParserDesignBlob = 'a837d94d58d8ad2ee1c71fd51de64257fe49d060'
$ExpectedV7Plan = '483cf5fd7886bdbc26aefb82d800333d9e001d6d'
$ExpectedV7PlanBlob = '5ed0f6819deb12b0ab6b204624a9278e9b35289e'
$ExpectedV7Design = 'c558c0a9a1ce02c3162305b4b7bf6592a905432a'
$ExpectedV7DesignBlob = '5bfa3ded2c55acf48b3e193a9fbb53d126e945ad'
$FrozenPwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$FrozenWindowsPowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$PwshSecurityManifest = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$PwshSecurityDll = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll'
$WindowsSecurityManifest = 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$WindowsSecurityDll = 'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll'
$Stage0Terminal = 'ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$ExpectedV10 = [ordered]@{
    'task-0-patch-root-binding-v10.txt' = @([long]1058, 'd3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5')
    'task-1-stage0-transport-controller-v10.ps1' = @([long]22802, '2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e')
    'task-1-stage0-v10.ps1' = @([long]25072, '5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')
}
$ExpectedExternalV9 = [ordered]@{
    'task-1-stage0-transport-controller-v9.ps1' = @([long]17994, '795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff')
    'task-1-stage0-v9.ps1' = @([long]20258, '34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')
}
$ExpectedV7 = [ordered]@{
    'task-1-stage0-audit-v7.ps1' = @([long]3849, 'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b')
    'task-1-scalar-identity-tests-v7.ps1' = @([long]8849, '977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9')
    'task-1-scalar-identity-red-v7.psm1' = @([long]991, '34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919')
    'task-1-scalar-identity-green-v7.psm1' = @([long]2553, 'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')
}
$V11ShadowPaths = @(
    '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
)

function Get-A11V11BytesSha256 { param([byte[]] $Bytes) $Algorithm = [Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() } finally { $Algorithm.Dispose() } }
function Get-A11V11FileSha256 { param([string] $Path) $Stream = [IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read); $Algorithm = [Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant() } finally { $Algorithm.Dispose(); $Stream.Dispose() } }
function Assert-A11V11ParentChainOrdinary { param([string] $Path) $Cursor=[IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path)); while(-not [string]::IsNullOrEmpty($Cursor)){ $Item=Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop; if(($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0-or-not[string]::IsNullOrEmpty([string]$Item.LinkType)){throw 'linked parent rejected'}; $Parent=[IO.Directory]::GetParent($Cursor); if($null-eq$Parent){break}; $Cursor=$Parent.FullName } }
function Assert-A11V11FileIdentity { param([string]$Path,[long]$ByteCount,[string]$Sha256,[string]$LeafLinkType,[string]$FileVersion='',[string]$ProductVersion='') if(-not[IO.Path]::IsPathFullyQualified($Path)-or-not[StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path),$Path)){throw 'file path rejected'}; $Item=Get-Item -LiteralPath $Path -Force -ErrorAction Stop; if($Item.PSIsContainer-or[long]$Item.Length-ne$ByteCount-or($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0){throw 'file identity rejected'}; $ActualLink=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType}; if(-not[StringComparer]::Ordinal.Equals($ActualLink,$LeafLinkType)){throw 'file link rejected'}; Assert-A11V11ParentChainOrdinary $Path; if((Get-A11V11FileSha256 $Path)-cne$Sha256){throw 'file digest rejected'}; $Streams=@(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop); if($Streams.Count-ne 1-or[string]$Streams[0].Stream-cne':$DATA'){throw 'file stream rejected'}; if($FileVersion-and[string]$Item.VersionInfo.FileVersion-cne$FileVersion){throw 'file version rejected'}; if($ProductVersion-and[string]$Item.VersionInfo.ProductVersion-cne$ProductVersion){throw 'product version rejected'} }
function Assert-A11V11SourceIdentity { param([string]$Path,[long]$ByteCount,[string]$Sha256) Assert-A11V11FileIdentity $Path $ByteCount $Sha256 'None'; $Bytes=[IO.File]::ReadAllBytes($Path); if($Bytes.Length-eq 0-or($Bytes.Length-ge 3-and$Bytes[0]-eq 0xEF-and$Bytes[1]-eq 0xBB-and$Bytes[2]-eq 0xBF)-or$Bytes-contains 0x0D-or$Bytes[-1]-ne 0x0A-or($Bytes.Length-gt 1-and$Bytes[-2]-eq 0x0A)){throw 'source encoding rejected'}; $Round=$Utf8.GetBytes($Utf8.GetString($Bytes)); if($Round.Length-ne$Bytes.Length-or(Get-A11V11BytesSha256 $Round)-cne$Sha256){throw 'source roundtrip rejected'}; $Streams=@(Get-Item -LiteralPath $Path -Stream *); if($Streams.Count-ne 1-or[string]$Streams[0].Stream-cne ':$DATA'){throw 'source stream rejected'} }
function Get-A11V11PlanSourceIdentity { param([string]$Name) $PlanText=$Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath))); $Matches=@($PlanText.Split([char]10)|Where-Object{$_.StartsWith("SOURCE_IDENTITY|$Name|",[StringComparison]::Ordinal)}); if($Matches.Count-ne 1){throw 'source record count rejected'}; $Parts=@($Matches[0].Split('|')); [long]$Count=0; if($Parts.Count-ne 4-or-not[long]::TryParse($Parts[2],[Globalization.NumberStyles]::None,[Globalization.CultureInfo]::InvariantCulture,[ref]$Count)-or$Parts[3]-notmatch'\A[0-9a-f]{64}\z'){throw 'source record rejected'}; [pscustomobject][ordered]@{byte_count=$Count;sha256=$Parts[3]} }
function Get-A11V11ExpectedV10MarkerText { $Header='CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-0-patch-root-binding-v10.txt'; $Lines=@('schema_version=1','binding_id=entryv10-patch-root-binding-001',"source_plan_commit=$ExpectedV10Plan","source_design_commit=$ExpectedV10Design","source_design_blob=$ExpectedV10DesignBlob",'patch_authority_root=<workspace>',"patch_header=$Header","repository_root=$RepositoryRoot","workspace_path=$V10Workspace","canonical_target=$V10MarkerPath",'failed_v9_terminal=ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO'); [string]::Join("`n",$Lines)+"`n" }
function Assert-A11V11PreservedEvidence { $V10Children=@(Get-ChildItem -LiteralPath $V10Workspace -Force|Sort-Object Name); if($V10Children.Count-ne 3-or@($V10Children|Where-Object PSIsContainer).Count-ne 0){throw 'v10 inventory rejected'}; foreach($Name in $ExpectedV10.Keys){Assert-A11V11FileIdentity (Join-Path $V10Workspace $Name) $ExpectedV10[$Name][0] $ExpectedV10[$Name][1] 'None'}; if($Utf8.GetString([IO.File]::ReadAllBytes($V10MarkerPath))-cne(Get-A11V11ExpectedV10MarkerText)){throw 'v10 marker rejected'}; if(Test-Path -LiteralPath $IntendedV9Workspace){throw 'intended v9 exists'}; $V9Children=@(Get-ChildItem -LiteralPath $ExternalV9Workspace -Force); if($V9Children.Count-ne 2-or@($V9Children|Where-Object PSIsContainer).Count-ne 0){throw 'v9 inventory rejected'}; foreach($Name in $ExpectedExternalV9.Keys){Assert-A11V11FileIdentity (Join-Path $ExternalV9Workspace $Name) $ExpectedExternalV9[$Name][0] $ExpectedExternalV9[$Name][1] 'None'}; if((Test-Path -LiteralPath $V8Workspace)-or(Test-Path -LiteralPath $ConsumedV6Workspace)){throw 'consumed namespace exists'}; foreach($Path in $V11ShadowPaths){if(Test-Path -LiteralPath $Path){throw 'v11 shadow path exists'}}; $PlanText=$Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath))); $Incident='PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO'; if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$Incident}).Count-ne 1){throw 'v10 incident rejected'} }
function Assert-A11V11Signature { param([object]$Signature,[string]$Subject,[string]$Thumbprint) if($Signature.Status.ToString()-cne'Valid'-or$null-eq$Signature.SignerCertificate-or[string]$Signature.SignerCertificate.Subject-cne$Subject-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,$Thumbprint)){throw 'signature rejected'} }

Push-Location -LiteralPath $RepositoryRoot
$SecurityModule = $null
$TerminalBytes = $null
try {
    $PlanCommit = git rev-parse HEAD
    $Chain = @(@($PlanCommit,$ExpectedDesign),@($ExpectedDesign,$ExpectedV10Plan),@($ExpectedV10Plan,$ExpectedV10Design),@($ExpectedV10Design,$ExpectedV9Plan),@($ExpectedV9Plan,$ExpectedV9Design),@($ExpectedV9Design,$ExpectedV8Plan),@($ExpectedV8Plan,$ExpectedAmendment),@($ExpectedAmendment,$ExpectedParserDesign),@($ExpectedParserDesign,$ExpectedV7Plan),@($ExpectedV7Plan,$ExpectedV7Design))
    if($PlanCommit-notmatch'\A[0-9a-f]{40}\z'){throw 'plan commit rejected'}
    foreach($Pair in $Chain){if((git rev-list --parents -n 1 $Pair[0])-cne"$($Pair[0]) $($Pair[1])"){throw 'lineage rejected'}}
    if((git branch --show-current)-cne'codex/wave0-model-contract'){throw 'branch rejected'}
    if((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD)-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 raw byte output recovery'){throw 'plan identity rejected'}
    $Changed=@(git diff-tree --no-commit-id --name-only -r HEAD); if($Changed.Count-ne 1-or$Changed[0]-cne$PlanPath){throw 'plan path rejected'}
    $Blobs=@(@('HEAD',$DesignPath,$ExpectedDesignBlob),@($ExpectedV10Plan,$V10PlanPath,$ExpectedV10PlanBlob),@($ExpectedV10Design,$V10DesignPath,$ExpectedV10DesignBlob),@($ExpectedV9Plan,$V9PlanPath,$ExpectedV9PlanBlob),@($ExpectedV9Design,$V9DesignPath,$ExpectedV9DesignBlob),@($ExpectedV8Plan,$V8PlanPath,$ExpectedV8PlanBlob),@($ExpectedAmendment,$AmendmentPath,$ExpectedAmendmentBlob),@($ExpectedParserDesign,$ParserDesignPath,$ExpectedParserDesignBlob),@($ExpectedV7Plan,$V7PlanPath,$ExpectedV7PlanBlob),@($ExpectedV7Design,$V7DesignPath,$ExpectedV7DesignBlob)); foreach($Record in $Blobs){if((git rev-parse "$($Record[0]):$($Record[1])")-cne$Record[2]){throw 'blob rejected'}}
    if(-not[string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))){throw 'superproject rejected'}
    if([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)),[IO.Path]::GetFullPath((git rev-parse --git-common-dir)))){throw 'linked isolation rejected'}
    if(@(git status --porcelain=v1 --untracked-files=all).Count-ne 0-or@(git diff --cached --name-only).Count-ne 0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne 0){throw 'Git cleanliness rejected'}
    Assert-A11V11PreservedEvidence
    $ControllerIdentity=Get-A11V11PlanSourceIdentity 'task-1-stage0-raw-byte-controller-v11.ps1'; $Stage0Identity=Get-A11V11PlanSourceIdentity 'task-1-stage0-v11.ps1'
    if(-not[StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($PSCommandPath),$Stage0Path)){throw 'Stage0 path rejected'}
    Assert-A11V11SourceIdentity $ControllerPath $ControllerIdentity.byte_count $ControllerIdentity.sha256; Assert-A11V11SourceIdentity $Stage0Path $Stage0Identity.byte_count $Stage0Identity.sha256
    $Children=@(Get-ChildItem -LiteralPath $WorkspacePath -Force|Sort-Object Name); $Names=@('task-1-stage0-raw-byte-controller-v11.ps1','task-1-stage0-v11.ps1')|Sort-Object; if($Children.Count-ne 2-or@($Children|Where-Object PSIsContainer).Count-ne 0-or[string]::Join("`n",@($Children.Name))-cne[string]::Join("`n",$Names)){throw 'v11 inventory rejected'}
    $V7Children=@(Get-ChildItem -LiteralPath $V7Workspace -Force); if($V7Children.Count-ne 4-or@($V7Children|Where-Object PSIsContainer).Count-ne 0){throw 'v7 inventory rejected'}; foreach($Name in $ExpectedV7.Keys){Assert-A11V11FileIdentity (Join-Path $V7Workspace $Name) $ExpectedV7[$Name][0] $ExpectedV7[$Name][1] 'None'}
    Assert-A11V11FileIdentity $FrozenPwsh 301368 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' 'None' '7.6.4.500' '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V11FileIdentity $FrozenWindowsPowerShell 454656 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' 'HardLink' '10.0.26100.8875 (WinBuild.160101.0800)' '10.0.26100.8875'
    Assert-A11V11FileIdentity $PwshSecurityManifest 15463 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' 'None'; Assert-A11V11FileIdentity $PwshSecurityDll 345952 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' 'None' '7.6.4.500' '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V11FileIdentity $WindowsSecurityManifest 776 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' 'HardLink'; Assert-A11V11FileIdentity $WindowsSecurityDll 93696 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' 'HardLink' '10.0.26100.1' '10.0.26100.1'
    $CurrentProcessPath=[IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName); if(-not[StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath,$FrozenPwsh)-or$PSVersionTable.PSVersion.ToString()-cne'7.6.4'-or$PSVersionTable.PSEdition-cne'Core'){throw 'Stage0 runtime rejected'}
    $SecurityModule=Import-Module -Name $PwshSecurityManifest -Force -PassThru -ErrorAction Stop; if(@($SecurityModule).Count-ne 1-or[IO.Path]::GetFullPath([string]$SecurityModule.Path)-cne$PwshSecurityManifest-or@($SecurityModule.NestedModules).Count-ne 1-or[IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path)-cne$PwshSecurityDll){throw 'Security provider rejected'}
    $AuthCommand=Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop; if(@($AuthCommand).Count-ne 1-or[IO.Path]::GetFullPath([string]$AuthCommand.Module.Path)-cne$PwshSecurityManifest-or[IO.Path]::GetFullPath([string]$AuthCommand.DLL)-cne$PwshSecurityDll){throw 'Authenticode provenance rejected'}
    Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $FrozenPwsh) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'AB172913A2960A224809EE8A0C371CD47A079B72'; Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $FrozenWindowsPowerShell) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'; Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityManifest) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'AB172913A2960A224809EE8A0C371CD47A079B72'; Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityDll) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'; Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityManifest) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '71F53A26BB1625E466727183409A30D03D7923DF'; Assert-A11V11Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityDll) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '71F53A26BB1625E466727183409A30D03D7923DF'
    $TerminalBytes=$Utf8.GetBytes($Stage0Terminal+"`n")
}
finally { if($null-ne$SecurityModule){[void](Remove-Module -ModuleInfo $SecurityModule -Force -ErrorAction Stop)}; [void](Pop-Location) }

$OutputStream=[Console]::OpenStandardOutput()
[void]$OutputStream.Write($TerminalBytes,0,$TerminalBytes.Length)
[void]$OutputStream.Flush()
```

---

### Task 1: Entry gate and exact two-file materialization

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-v11.ps1`
- Read: `docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md`
- Read: `docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md`

**Interfaces:**
- Consumes: exact committed plan/design lineage, absent v11 namespace, exact preserved v10 three-file NO_GO, external v9 records, v8/v6 absences, v7 records, runtime/provider identities, and clean linked/canonical worktrees.
- Produces: exactly two immutable v11 source files whose bytes equal the frozen plan blocks.

- [ ] **Step 1: Run the complete read-only entry gate**

Require exact HEAD parent, plan/design blobs, author/committer/subject, one changed plan path, branch, linked-worktree isolation, non-submodule state, empty staging, clean linked/canonical worktrees, absent v11 workspace and all three v11 shadow paths, exact v10 three-file identities and marker text, exact external v9 identities and intended-v9 absence, absent v8/v6 namespaces, exact v7 four-file identities, and exact six runtime/provider file identities. Print one `ENTRYV11_MATERIALIZATION_ENTRY_PASS` line only after every check passes.

Run exactly this read-only gate from the linked repository:

```powershell
$ErrorActionPreference = 'Stop'
$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md'
$V11 = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$V10 = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
function Get-EntrySha256([string] $Path) { $Stream=[IO.File]::OpenRead($Path);$Algorithm=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-','').ToLowerInvariant()}finally{$Algorithm.Dispose();$Stream.Dispose()} }
Set-Location -LiteralPath $RepositoryRoot
$Head = git rev-parse HEAD
if ($Head -notmatch '\A[0-9a-f]{40}\z' -or (git rev-list --parents -n 1 HEAD) -cne "$Head 29470670c4fe2095c0cedcf5ab389c2c82190e9c") { throw 'plan parent rejected' }
if ((git rev-parse "HEAD:$DesignPath") -cne '8ead81be4da26dbd3e17badade45b7c746e8f8ce') { throw 'design blob rejected' }
if ((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD) -cne 'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 raw byte output recovery') { throw 'plan identity rejected' }
$Changed=@(git diff-tree --no-commit-id --name-only -r HEAD)
if ($Changed.Count-ne1 -or $Changed[0]-cne$PlanPath -or (git branch --show-current)-cne'codex/wave0-model-contract') { throw 'plan path/branch rejected' }
if (-not[string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'superproject rejected' }
if ([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)),[IO.Path]::GetFullPath((git rev-parse --git-common-dir)))) { throw 'linked isolation rejected' }
if (@(git status --porcelain=v1 --untracked-files=all).Count-ne0 -or @(git diff --cached --name-only).Count-ne0 -or @(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0) { throw 'Git cleanliness rejected' }
if (Test-Path -LiteralPath $V11) { throw 'v11 namespace exists' }
$V10Expected=[ordered]@{'task-0-patch-root-binding-v10.txt'=@(1058,'d3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5');'task-1-stage0-transport-controller-v10.ps1'=@(22802,'2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e');'task-1-stage0-v10.ps1'=@(25072,'5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')}
$V10Children=@(Get-ChildItem -LiteralPath $V10 -Force)
if ($V10Children.Count-ne3 -or @($V10Children|Where-Object PSIsContainer).Count-ne0) { throw 'v10 inventory rejected' }
foreach($Name in $V10Expected.Keys){$Item=Get-Item -LiteralPath (Join-Path $V10 $Name) -Force;if($Item.Length-ne[long]$V10Expected[$Name][0] -or (Get-EntrySha256 $Item.FullName)-cne[string]$V10Expected[$Name][1]){throw 'v10 identity rejected'}}
$ExternalV9='<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$V9Expected=[ordered]@{'task-1-stage0-transport-controller-v9.ps1'=@(17994,'795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff');'task-1-stage0-v9.ps1'=@(20258,'34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')}
$V9Children=@(Get-ChildItem -LiteralPath $ExternalV9 -Force);if($V9Children.Count-ne2-or@($V9Children|Where-Object PSIsContainer).Count-ne0){throw 'external v9 inventory rejected'}
foreach($Name in $V9Expected.Keys){$Item=Get-Item -LiteralPath (Join-Path $ExternalV9 $Name) -Force;if($Item.Length-ne[long]$V9Expected[$Name][0]-or(Get-EntrySha256 $Item.FullName)-cne[string]$V9Expected[$Name][1]){throw 'external v9 identity rejected'}}
$V7=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$V7Expected=[ordered]@{'task-1-stage0-audit-v7.ps1'=@(3849,'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b');'task-1-scalar-identity-tests-v7.ps1'=@(8849,'977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9');'task-1-scalar-identity-red-v7.psm1'=@(991,'34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919');'task-1-scalar-identity-green-v7.psm1'=@(2553,'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')}
$V7Children=@(Get-ChildItem -LiteralPath $V7 -Force);if($V7Children.Count-ne4-or@($V7Children|Where-Object PSIsContainer).Count-ne0){throw 'v7 inventory rejected'}
foreach($Name in $V7Expected.Keys){$Item=Get-Item -LiteralPath (Join-Path $V7 $Name) -Force;if($Item.Length-ne[long]$V7Expected[$Name][0]-or(Get-EntrySha256 $Item.FullName)-cne[string]$V7Expected[$Name][1]){throw 'v7 identity rejected'}}
$Absences=@(
    (Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'),
    (Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'),
    (Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'),
    '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery',
    '<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
)
foreach($Path in $Absences){if(Test-Path -LiteralPath $Path){throw 'required absence rejected'}}
$RuntimeExpected=[ordered]@{
    'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'=@(301368,'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f','None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72')
    'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'=@(454656,'7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5','HardLink','10.0.26100.8875 (WinBuild.160101.0800)','10.0.26100.8875','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443')
    'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'=@(15463,'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a','None','','','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72')
    'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll'=@(345952,'5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90','None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1')
    'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'=@(776,'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30','HardLink','','','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF')
    'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll'=@(93696,'9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010','HardLink','10.0.26100.1','10.0.26100.1','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF')
}
$SecurityModule=Import-Module -Name 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1' -Force -PassThru
try{
    $AuthCommand=Get-Command Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security
    if(@($SecurityModule).Count-ne1-or@($AuthCommand).Count-ne1){throw 'provider provenance rejected'}
    foreach($Path in $RuntimeExpected.Keys){$Record=$RuntimeExpected[$Path];$Item=Get-Item -LiteralPath $Path -Force;$Link=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType};$Streams=@(Get-Item -LiteralPath $Path -Stream *);$Signature=Get-AuthenticodeSignature -LiteralPath $Path;if($Item.Length-ne[long]$Record[0]-or(Get-EntrySha256 $Path)-cne[string]$Record[1]-or$Link-cne[string]$Record[2]-or$Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'-or($Record[3]-and[string]$Item.VersionInfo.FileVersion-cne[string]$Record[3])-or($Record[4]-and[string]$Item.VersionInfo.ProductVersion-cne[string]$Record[4])-or$Signature.Status.ToString()-cne'Valid'-or[string]$Signature.SignerCertificate.Subject-cne[string]$Record[5]-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,[string]$Record[6])){throw 'runtime/provider identity rejected'}}
}finally{[void](Remove-Module -ModuleInfo $SecurityModule -Force)}
'ENTRYV11_MATERIALIZATION_ENTRY_PASS|v10_files=3|v11=absent|runtimes=2|providers=2|linked=clean|canonical=clean'
```

Any difference stops without materialization as `ENTRYV11_MATERIALIZATION_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Extract and identity-check both frozen source blocks**

Read the committed plan blob, find exactly one heading and one `powershell` fence for each frozen filename, preserve every character between the opening fence LF and closing fence, append no byte beyond the block's existing final LF, and require the exact two `SOURCE_IDENTITY` records. Parse both in memory with the current PowerShell 7 parser and require zero errors. Do not execute either block.

Use this extraction algorithm; retain the two `$Source` strings in memory for Step 3:

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$Utf8 = [Text.UTF8Encoding]::new($false,$true)
$PlanBytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $PlanPath))
if($PlanBytes-contains 0x0D -or $PlanBytes[-1]-ne0x0A){throw 'plan encoding rejected'}
$PlanText = $Utf8.GetString($PlanBytes)
function Get-BlockSha256([byte[]]$Bytes){$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}}
$Expected=[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')}
$Sources=[ordered]@{}
foreach($Name in $Expected.Keys){
    $Pattern='(?ms)^#### Frozen source: `'+[regex]::Escape($Name)+'`\n\n```powershell\n(?<body>.*?)^```\n'
    $Matches=[regex]::Matches($PlanText,$Pattern)
    if($Matches.Count-ne1){throw 'frozen block count rejected'}
    $Source=$Matches[0].Groups['body'].Value
    $SourceBytes=$Utf8.GetBytes($Source)
    if($SourceBytes.Length-ne[long]$Expected[$Name][0] -or (Get-BlockSha256 $SourceBytes)-cne[string]$Expected[$Name][1]){throw 'frozen block identity rejected'}
    $Tokens=$null;$Errors=$null;[void][Management.Automation.Language.Parser]::ParseInput($Source,[ref]$Tokens,[ref]$Errors)
    if(@($Errors).Count-ne0){throw 'PowerShell 7 parser rejected'}
    $Sources[$Name]=$Source
}
'ENTRYV11_SOURCE_BLOCK_ADMISSION_PASS|files=2|parser=7.6.4|errors=0'
```

- [ ] **Step 3: Materialize both files with one `apply_patch` call**

The complete headers are exactly:

```text
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-v11.ps1
```

Construct the patch in memory from the admitted blocks. Invoke `apply_patch` once. The call is consumed when invoked even if its result is empty, ambiguous, disconnected, timed out, or erroneous. Never issue a second patch.

- [ ] **Step 4: Verify exact materialization**

Require the canonical namespace to contain exactly the two permitted ordinary files, no directory child, exact strict UTF-8/no-BOM/LF/single-final-LF bytes and plan-pinned identities, canonical containment, ordinary parent chain, no link/reparse point, one default data stream, all v11 shadow paths absent, v10/external-v9 evidence unchanged, and linked/canonical Git state clean. Any difference is `ENTRYV11_MATERIALIZATION_UNPROVABLE / NO_GO`; freeze and stop.

Run this identity core, followed by the complete Step 1 preservation checks:

```powershell
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$Expected=[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')}
function Get-MaterializedSha256([string]$Path){$S=[IO.File]::OpenRead($Path);$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($S)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose();$S.Dispose()}}
$Children=@(Get-ChildItem -LiteralPath $Workspace -Force|Sort-Object Name)
if($Children.Count-ne2 -or @($Children|Where-Object PSIsContainer).Count-ne0){throw 'v11 inventory rejected'}
foreach($Name in $Expected.Keys){$Path=Join-Path $Workspace $Name;$Item=Get-Item -LiteralPath $Path -Force;$Bytes=[IO.File]::ReadAllBytes($Path);$Streams=@(Get-Item -LiteralPath $Path -Stream *);if($Item.PSIsContainer-or$Item.Length-ne[long]$Expected[$Name][0]-or(Get-MaterializedSha256 $Path)-cne[string]$Expected[$Name][1]-or($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne0-or-not[string]::IsNullOrEmpty([string]$Item.LinkType)-or$Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'-or$Bytes-contains0x0D-or$Bytes[-1]-ne0x0A-or($Bytes.Length-gt1-and$Bytes[-2]-eq0x0A)){throw 'v11 source rejected'}}
'ENTRYV11_MATERIALIZATION_PASS|files=2|directories=0|shadows=0|writes=1|retries=0'
```

### Task 2: Behavioral RED and static GREEN admission

**Files:**
- Read: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-1-stage0-transport-controller-v10.ps1`
- Test: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1`
- Test: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-v11.ps1`

**Interfaces:**
- Consumes: exact two-file Task 1 inventory and the immutable v10 behavioral failure.
- Produces: one source-inspection RED terminal and one dual-parser/static GREEN terminal without starting v10 or v11.

- [ ] **Step 1: Run the read-only v10 output-contract RED**

Read v10 controller bytes as data only. Require its frozen identity, exactly two bare `GetAwaiter().GetResult()` expressions, zero `[void]` bindings for those calls, a bare final Stage 0 terminal expression, a bare final transport terminal expression, and zero `OpenStandardOutput` raw-write site. Emit exactly:

```text
ENTRYV11_OUTPUT_CONTRACT_RED_PASS|fault=implicit_output_serialization|v10_retries=0
```

Do not parse, import, dot-source, or invoke v10. Any difference freezes v11 and stops.

Run exactly:

```powershell
$Path='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery\task-1-stage0-transport-controller-v10.ps1'
$Bytes=[IO.File]::ReadAllBytes($Path)
$Algorithm=[Security.Cryptography.SHA256]::Create();try{$Digest=[BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$Algorithm.Dispose()}
if($Bytes.Length-ne22802-or$Digest-cne'2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e'){throw 'v10 controller identity rejected'}
$Text=[Text.UTF8Encoding]::new($false,$true).GetString($Bytes)
if(([regex]::Matches($Text,'(?m)^\s*\$StdoutTask\.GetAwaiter\(\)\.GetResult\(\)\s*$')).Count-ne1){throw 'v10 stdout task RED rejected'}
if(([regex]::Matches($Text,'(?m)^\s*\$StderrTask\.GetAwaiter\(\)\.GetResult\(\)\s*$')).Count-ne1){throw 'v10 stderr task RED rejected'}
if($Text.Contains('[void]$StdoutTask.GetAwaiter().GetResult()',[StringComparison]::Ordinal)-or$Text.Contains('[void]$StderrTask.GetAwaiter().GetResult()',[StringComparison]::Ordinal)-or$Text.Contains('[Console]::OpenStandardOutput()',[StringComparison]::Ordinal)){throw 'v10 RED surface contradicted'}
if(([regex]::Matches($Text,'(?m)^\$ExpectedStage0Terminal$')).Count-ne1-or([regex]::Matches($Text,'(?m)^\$TransportTerminal$')).Count-ne1){throw 'v10 bare terminal RED rejected'}
'ENTRYV11_OUTPUT_CONTRACT_RED_PASS|fault=implicit_output_serialization|v10_retries=0'
```

- [ ] **Step 2: Run PowerShell 7 and Windows PowerShell 5.1 parser admission**

Use the exact admitted executable identities. PowerShell 7 parses both v11 files with `[System.Management.Automation.Language.Parser]::ParseFile`; Windows PowerShell 5.1 starts once with `-NoLogo -NoProfile -NonInteractive -Command` and uses only its parser API to parse the same two canonical files. Require zero parser errors, exact executable/process identity, exit zero, exact one-line parser terminal, and empty unexpected output. Neither parser executes a source AST.

Run PowerShell 7 parsing in the controller shell:

```powershell
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
foreach($Name in @('task-1-stage0-raw-byte-controller-v11.ps1','task-1-stage0-v11.ps1')){$Tokens=$null;$Errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $Workspace $Name),[ref]$Tokens,[ref]$Errors);if(@($Errors).Count-ne0){throw 'PowerShell 7 parser rejected'}}
'ENTRYV11_PARSER_PASS|runtime=powershell_core_7_6_4|files=2|errors=0'
```

Then invoke the exact Windows PowerShell executable once with this parser-only command. The task-specific environment variable carries data, not executable source, and is removed immediately afterward:

```powershell
$env:A11V11_WORKSPACE='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -Command '& { $ErrorActionPreference="Stop"; foreach($Name in @("task-1-stage0-raw-byte-controller-v11.ps1","task-1-stage0-v11.ps1")){ $Tokens=$null;$Errors=$null;[void][System.Management.Automation.Language.Parser]::ParseFile((Join-Path $env:A11V11_WORKSPACE $Name),[ref]$Tokens,[ref]$Errors);if(@($Errors).Count-ne0){throw "Windows PowerShell parser rejected"} }; "ENTRYV11_PARSER_PASS|runtime=windows_powershell_5_1|files=2|errors=0" }'
$ParserExit=$LASTEXITCODE
Remove-Item Env:A11V11_WORKSPACE
if($ParserExit-ne0){throw 'Windows PowerShell parser process rejected'}
```

- [ ] **Step 3: Run the complete static GREEN contract**

Require, using AST plus ordinal source inspection:

- exactly one controller `Process.Start()` call and the exact five-element `ArgumentList`;
- `UseShellExecute=false`, three redirects true, one post-start stdin close, zero stdin writes, concurrent `BaseStream.CopyToAsync` calls, 120,000 ms wait, one timeout-only recursive kill, and no retry/fallback/sleep;
- exactly two `GetAwaiter().GetResult()` calls and both are immediate children of `[void]` conversion expressions; zero bare `GetResult()` or `Wait()` result expression;
- controller has exactly one success `OpenStandardOutput`, one success `Write`, one success `Flush`, and constructs the exact two-line strict UTF-8/LF byte array;
- Stage 0 has zero process start, exactly one `OpenStandardOutput`, one `Write`, one `Flush`, and constructs the exact one-line strict UTF-8/LF byte array;
- neither source uses a bare terminal expression, `Write-Output`, `Write-Host`, `Out-String`, formatter, transcript, output redirection, console/input encoding mutation, dynamic execution, dot-source, stdin source, `-EncodedCommand`, alternate executable, parser child, Docker/GPU/A11/model/network/owner action, or file writer;
- both source identities, complete v11 inventory, v10 preservation, runtime/providers, signatures, lineage, paths, absences, and Git facts remain exact; and
- pure in-memory construction of the child and parent expected arrays yields no BOM/CR, exact one final LF per line, and exact ordinal strings.

Emit exactly:

```text
ENTRYV11_OUTPUT_CONTRACT_GREEN_PASS|child=raw_utf8_lf|parent=raw_utf8_lf|task_results=suppressed|parsers=2|starts=0
```

Any difference is `ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO`. Preserve both v11 files and stop before Task 3.

Run this AST/text GREEN core after both parser terminals; then rerun Task 1 Step 4 identity and preservation checks:

```powershell
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$ControllerPath=Join-Path $Workspace 'task-1-stage0-raw-byte-controller-v11.ps1';$Stage0Path=Join-Path $Workspace 'task-1-stage0-v11.ps1'
$ControllerText=[IO.File]::ReadAllText($ControllerPath,[Text.UTF8Encoding]::new($false,$true));$Stage0Text=[IO.File]::ReadAllText($Stage0Path,[Text.UTF8Encoding]::new($false,$true))
$Tokens=$null;$Errors=$null;$ControllerAst=[Management.Automation.Language.Parser]::ParseFile($ControllerPath,[ref]$Tokens,[ref]$Errors);if(@($Errors).Count){throw 'controller parser rejected'}
$Starts=@($ControllerAst.FindAll({param($Node)$Node-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$Node.Member.Value-eq'Start'},$true));if($Starts.Count-ne1){throw 'start site rejected'}
$Results=@($ControllerAst.FindAll({param($Node)$Node-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$Node.Member.Value-eq'GetResult'},$true));if($Results.Count-ne2){throw 'task completion count rejected'};foreach($Node in $Results){if($Node.Parent-isnot[Management.Automation.Language.ConvertExpressionAst]-or$Node.Parent.Type.TypeName.Name-cne'void'){throw 'task result not suppressed'}}
if(([regex]::Matches($ControllerText,'\[Console\]::OpenStandardOutput\(\)')).Count-ne1-or([regex]::Matches($Stage0Text,'\[Console\]::OpenStandardOutput\(\)')).Count-ne1-or([regex]::Matches($ControllerText,'\.CopyToAsync\(')).Count-ne2){throw 'raw stream topology rejected'}
foreach($Forbidden in @('Write-Output','Write-Host','Out-String','Start-Process','Invoke-Expression','ScriptBlock]::Create','-EncodedCommand','Set-Content','Out-File','nvidia-smi','OwnerAuthorizationId')){if($ControllerText.Contains($Forbidden,[StringComparison]::OrdinalIgnoreCase)-or$Stage0Text.Contains($Forbidden,[StringComparison]::OrdinalIgnoreCase)){throw 'forbidden source surface'}}
$Utf8=[Text.UTF8Encoding]::new($false,$true);$Child=$Utf8.GetBytes('ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'+"`n");$Parent=$Utf8.GetBytes($Utf8.GetString($Child)+'ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'+"`n")
if($Child-contains0x0D-or$Parent-contains0x0D-or$Child[-1]-ne0x0A-or$Parent[-1]-ne0x0A){throw 'raw terminal bytes rejected'}
'ENTRYV11_OUTPUT_CONTRACT_GREEN_PASS|child=raw_utf8_lf|parent=raw_utf8_lf|task_results=suppressed|parsers=2|starts=0'
```

### Task 3: Single-use Stage 0 observation and final closure

**Files:**
- Execute once: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1`
- Read: both v11 files, v10 evidence, predecessor evidence, design, and plan

**Interfaces:**
- Consumes: exact Task 1 materialization and exact Task 2 RED/GREEN terminals.
- Produces: exact two-line controller stdout plus the final closed milestone, or the first preserved NO_GO.

- [ ] **Step 1: Print and recheck the frozen invocation boundary**

Re-run every Task 2 GREEN assertion read-only. Print the exact controller path, child path, executable identity, five argv elements, expected child bytes/count/digest, expected parent bytes/count/digest, two-file snapshot, and `starts=0`. Any difference stops without invocation.

Use this final boundary print after the complete GREEN rerun:

```powershell
$Utf8=[Text.UTF8Encoding]::new($false,$true)
function Get-BoundarySha256([byte[]]$Bytes){$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}}
$Child=$Utf8.GetBytes('ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'+"`n")
$Parent=$Utf8.GetBytes($Utf8.GetString($Child)+'ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'+"`n")
'ENTRYV11_INVOCATION_BOUNDARY|controller=.\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery\task-1-stage0-raw-byte-controller-v11.ps1|child=task-1-stage0-v11.ps1|argv=-NoLogo,-NoProfile,-NonInteractive,-File,<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery\task-1-stage0-v11.ps1|child_bytes='+$Child.Length+'|child_sha256='+(Get-BoundarySha256 $Child)+'|parent_bytes='+$Parent.Length+'|parent_sha256='+(Get-BoundarySha256 $Parent)+'|files=2|starts=0'
```

The expected values are fixed by this plan: child bytes `186`, child SHA-256 `4eca538ea77ef602a4e9d64c17583f753500dac3086a9c4190e231997064e45d`, parent bytes `293`, and parent SHA-256 `4a05611a769196e4881e252ad084fa4a075fa4bd3a85dcedefa8d6baba8a2848`.

- [ ] **Step 2: Invoke the controller exactly once**

From the linked repository in the exact current PowerShell 7.6.4 Core shell, run only:

```powershell
& '.\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery\task-1-stage0-raw-byte-controller-v11.ps1'
```

The invocation is consumed when issued. A successful child `Process.Start()` consumes Stage 0. Never invoke either source again.

Require controller exit zero, no additional output, and exact parent-visible raw stdout:

```text
ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

Both lines end in LF, including the second. Any controller uncertainty before child start is `ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO`. Any child start followed by timeout, disconnect, incomplete capture, exit, stdout, stderr, identity, or side-effect difference is `ENTRYV11_STAGE0_UNPROVABLE / NO_GO`. Preserve everything and stop.

- [ ] **Step 3: Run the final read-only closure once**

Require exact design/plan commits, blobs, parentage, identities, and paths; exact two-file v11 identities and inventory; all v11 shadows absent; exact v10 three-file inventory and immutable NO_GO; exact required v9/v8/v7/v6/runtime/provider records and absences; HEAD/branch unchanged; linked/canonical clean; staging empty; no cache, temporary, report, result, repair, machine, bytecode, or unexpected object; controller invocations one; child starts one; retries zero; and every prohibited action zero.

Run the full Task 1 Step 4 and Task 2 Step 3 read-only checks again, then close with this independent state core:

```powershell
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot='<repo>'
$Workspace=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
Set-Location -LiteralPath $RepositoryRoot
$Head=git rev-parse HEAD
if($Head-notmatch'\A[0-9a-f]{40}\z'-or(git rev-list --parents -n 1 HEAD)-cne"$Head 29470670c4fe2095c0cedcf5ab389c2c82190e9c"){throw 'closure lineage rejected'}
if((git branch --show-current)-cne'codex/wave0-model-contract'-or@(git status --porcelain=v1 --untracked-files=all).Count-ne0-or@(git diff --cached --name-only).Count-ne0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0){throw 'closure Git rejected'}
$Children=@(Get-ChildItem -LiteralPath $Workspace -Force|Sort-Object Name);if($Children.Count-ne2-or@($Children|Where-Object PSIsContainer).Count-ne0){throw 'closure inventory rejected'}
$ForbiddenNames=@('machine','task-1-report.md','__pycache__','.pytest_cache','result.json','transcript.txt','repair.ps1')
foreach($Name in $ForbiddenNames){if(Test-Path -LiteralPath (Join-Path $Workspace $Name)){throw 'closure forbidden object'}}
'ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED'
```

Only exact closure records:

```text
ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

This is not a third controller output line and authorizes no continuation. Do not create a report or commit runtime evidence.

## Execution stop

After Task 3, report the plan/design commits and blobs, both source identities, RED/GREEN terminals, the exact controller observation, final closure status, Git cleanliness, and every unexecuted downstream/runtime category. Do not start another design, plan, implementation, controller, child, parser/scalar phase, or runtime without a new explicit owner instruction.
