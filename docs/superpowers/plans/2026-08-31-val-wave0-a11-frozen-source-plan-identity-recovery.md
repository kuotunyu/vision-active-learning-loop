# Wave 0 A11 Frozen-Source Plan-Identity Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the v12 plan-review NO_GO without materializing v12, prove the frozen-source plan-identity defect through an identity-consistency RED/GREEN gate, and execute one fresh v13 Stage 0 raw-byte transport attempt before stopping.

**Architecture:** Two fresh plan-pinned PowerShell files live in one ignored v13 namespace. Each source pins the exact v13 plan identity and the v13 plan/design/v12 lineage; a static gate compares those values to Git before either source can run. The admitted raw UTF-8/LF transport and corrected predecessor-absence expression remain unchanged in role and remains single-use.

**Tech Stack:** Git linked worktree, PowerShell 7.6.4 Core, Windows PowerShell 5.1 parser API, PowerShell AST, .NET `ProcessStartInfo`, strict UTF-8, SHA-256, Authenticode, and `apply_patch`-only authoring.

## Global Constraints

- Repository: `<repo>\.worktrees\wave0-model-contract`.
- Canonical checkout: `<repo>`; it is read-only and must remain clean.
- Branch: `codex/wave0-model-contract`.
- Entry HEAD must be this committed plan, whose direct parent is design commit `84b0f64fa5565d785e32fe3fbe5de1dc473f23aa` and design blob is `eb0260c4137cfc29bcefc3b410eb19cb88262a8c`.
- Exact author and committer: `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Exact plan subject: `docs: plan A11 frozen source plan identity recovery`.
- The plan commit changes only `docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md`.
- The v13 namespace and both v13 sources must be absent at plan commit and execution entry. The preserved v12 namespace must remain absent; v12 materializations, Windows parser processes, controller invocations, and child starts remain zero.
- Runtime artifacts are ignored evidence; no runtime artifact is committed.
- All file creation uses `apply_patch` with full shared-root-relative headers under patch authority `<workspace>`; shell writers, copy, move, rename, repair, deletion, cleanup, and alternate headers are forbidden.
- The two-file materialization patch, Windows PowerShell parser process, controller invocation, child start, and closure observation are each single-use. Any API uncertainty, timeout, disconnect, partial result, unexpected output, or identity difference is a preserved NO_GO and never permission to retry.
- v12 plan commit `97acd06f61fdac5df11e3a8fb21b641101b9f482`, design, frozen source blocks, source identities, and absent runtime namespace remain immutable `ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO`.
- v11 remains immutable `ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO`; its controller invocation count is one, its child start count is zero, and neither source may be invoked, imported, dot-sourced, edited, copied, moved, renamed, deleted, completed, or reinterpreted.
- Do not execute parser/scalar worker phases, preserved-inventory construction, formal A11 entry, report creation, Docker, WSL, GPU, CUDA, A11 runtime, model work, RDD, Wave 1, product work, network work, or an `OwnerAuthorizationId` flow.
- Do not create a remote, push, merge, rebase, reset, stash, amend, squash, cherry-pick, tag, release, publish, deploy, or modify another repository.
- The frozen PowerShell 7 executable is `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`.
- The Windows PowerShell executable is `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`; it is used once only for parser admission and never as the v13 child.
- Success stops at `ENTRYV13_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED`.

## File Map

| Path | Responsibility |
|---|---|
| `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-plan-identity-controller-v13.ps1` | Self-attests the v13/predecessor/runtime envelope, starts exactly one Stage 0 child, captures raw streams, verifies exact child bytes, and emits exact two-line raw parent output. |
| `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-v13.ps1` | Rechecks the read-only admission envelope and emits exactly one raw UTF-8/LF Stage 0 terminal. |

The successful v13 namespace contains exactly those two ordinary files and no directory child, marker, report, manifest, result, transcript, cache, bytecode, temporary, repair, or machine object.

## Frozen records

```text
PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO
PRESERVED_V11_INCIDENT|plan_commit=30735e992d8670991beb0c2882b8f225ff89d978|controller_invocations=1|child_starts=0|phase=controller_preflight|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191|terminal=ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO
SOURCE_IDENTITY|task-1-stage0-plan-identity-controller-v13.ps1|31491|dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086
SOURCE_IDENTITY|task-1-stage0-v13.ps1|24403|18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967
```

The two `SOURCE_IDENTITY` records are the exact decimal byte counts and
lowercase SHA-256 values derived from the complete LF-terminated frozen blocks
below.

## Frozen source blocks

#### Frozen source: `task-1-stage0-plan-identity-controller-v13.ps1`

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$WorkspacePath = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$ControllerPath = Join-Path $WorkspacePath 'task-1-stage0-plan-identity-controller-v13.ps1'
$Stage0Path = Join-Path $WorkspacePath 'task-1-stage0-v13.ps1'
$V12Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery'
$V11Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$V10Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'
$V10MarkerPath = Join-Path $V10Workspace 'task-0-patch-root-binding-v10.txt'
$ExternalV9Workspace = '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$IntendedV9Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$V8Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'
$V7Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$PlanPath = 'docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md'
$V12PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery.md'
$V12DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery-design.md'
$V11PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$V11DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md'
$V10PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery.md'
$V10DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery-design.md'
$V9PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery.md'
$V9DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery-design.md'
$V8PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery.md'
$ParserDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md'
$AmendmentPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-security-module-amendment-design.md'
$V7PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md'
$V7DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md'
$ExpectedDesign = '84b0f64fa5565d785e32fe3fbe5de1dc473f23aa'
$ExpectedDesignBlob = 'eb0260c4137cfc29bcefc3b410eb19cb88262a8c'
$ExpectedV12Plan = '97acd06f61fdac5df11e3a8fb21b641101b9f482'
$ExpectedV12PlanBlob = 'c11c95c5a4ce32c373599a41d755da7931640681'
$ExpectedV12Design = '15d34231f7f65f1be6f08eea5946eefd2b8949ba'
$ExpectedV12DesignBlob = '545fe2d74e3209902f1733c180295d89b671ae86'
$ExpectedV11Plan = '30735e992d8670991beb0c2882b8f225ff89d978'
$ExpectedV11PlanBlob = 'c677fa4280965e52a5b46e1452fa3b4d3bc22413'
$ExpectedV11Design = '29470670c4fe2095c0cedcf5ab389c2c82190e9c'
$ExpectedV11DesignBlob = '8ead81be4da26dbd3e17badade45b7c746e8f8ce'
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
$ExpectedStage0Terminal = 'ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'
$TransportTerminal = 'ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$ExpectedV11 = [ordered]@{
    'task-1-stage0-raw-byte-controller-v11.ps1' = @([long]28071, 'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9')
    'task-1-stage0-v11.ps1' = @([long]21104, 'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')
}
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
$V13ShadowPaths = @(
    '<workspace>\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery',
    '<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery',
    '<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
)

function Get-A11V13BytesSha256 {
    param([Parameter(Mandatory)] [byte[]] $Bytes)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() }
    finally { $Algorithm.Dispose() }
}

function Get-A11V13FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try { [BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant() }
    finally { $Algorithm.Dispose(); $Stream.Dispose() }
}

function Assert-A11V13ParentChainOrdinary {
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

function Assert-A11V13FileIdentity {
    param([string] $Path, [long] $ByteCount, [string] $Sha256, [string] $LeafLinkType, [string] $FileVersion = '', [string] $ProductVersion = '')
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path), $Path)) { throw 'file path rejected' }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or [long]$Item.Length -ne $ByteCount -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'file identity rejected' }
    $ActualLink = if ([string]::IsNullOrEmpty([string]$Item.LinkType)) { 'None' } else { [string]$Item.LinkType }
    if (-not [StringComparer]::Ordinal.Equals($ActualLink, $LeafLinkType)) { throw 'file link type rejected' }
    Assert-A11V13ParentChainOrdinary -Path $Path
    if (-not [StringComparer]::Ordinal.Equals((Get-A11V13FileSha256 -Path $Path), $Sha256)) { throw 'file digest rejected' }
    $Streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if ($Streams.Count -ne 1 -or [string]$Streams[0].Stream -cne ':$DATA') { throw 'file stream rejected' }
    if (-not [string]::IsNullOrEmpty($FileVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.FileVersion, $FileVersion)) { throw 'file version rejected' }
    if (-not [string]::IsNullOrEmpty($ProductVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.ProductVersion, $ProductVersion)) { throw 'product version rejected' }
}

function Assert-A11V13SourceIdentity {
    param([string] $Path, [long] $ByteCount, [string] $Sha256)
    Assert-A11V13FileIdentity -Path $Path -ByteCount $ByteCount -Sha256 $Sha256 -LeafLinkType 'None'
    $Bytes = [IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -eq 0 -or ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) -or $Bytes -contains 0x0D -or $Bytes[-1] -ne 0x0A -or ($Bytes.Length -gt 1 -and $Bytes[-2] -eq 0x0A)) { throw 'source encoding rejected' }
    $RoundTrip = $Utf8.GetBytes($Utf8.GetString($Bytes))
    if ($RoundTrip.Length -ne $Bytes.Length -or (Get-A11V13BytesSha256 -Bytes $RoundTrip) -cne $Sha256) { throw 'source UTF-8 round trip rejected' }
    $Streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if ($Streams.Count -ne 1 -or [string]$Streams[0].Stream -cne ':$DATA') { throw 'source stream rejected' }
}

function Get-A11V13PlanSourceIdentity {
    param([Parameter(Mandatory)] [string] $Name)
    $PlanText = $Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath)))
    $Matches = @($PlanText.Split([char]10) | Where-Object { $_.StartsWith("SOURCE_IDENTITY|$Name|", [StringComparison]::Ordinal) })
    if ($Matches.Count -ne 1) { throw 'plan source identity count rejected' }
    $Parts = @($Matches[0].Split('|'))
    [long]$Count = 0
    if ($Parts.Count -ne 4 -or -not [long]::TryParse($Parts[2], [Globalization.NumberStyles]::None, [Globalization.CultureInfo]::InvariantCulture, [ref]$Count) -or $Parts[3] -notmatch '\A[0-9a-f]{64}\z') { throw 'plan source identity rejected' }
    [pscustomobject][ordered]@{ byte_count = $Count; sha256 = $Parts[3] }
}

function Get-A11V13WorkspaceSnapshot {
    param([Parameter(Mandatory)] [string] $Path)
    $Records = New-Object 'Collections.Generic.List[string]'
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force | Sort-Object Name)) {
        if ($Item.PSIsContainer) { throw 'workspace nested directory rejected' }
        [void]$Records.Add("$($Item.Name)|$([long]$Item.Length)|$(Get-A11V13FileSha256 -Path $Item.FullName)")
    }
    [string]::Join("`n", $Records)
}

function Get-A11V13ExpectedV10MarkerText {
    $Header = 'CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-0-patch-root-binding-v10.txt'
    $Lines = @('schema_version=1','binding_id=entryv10-patch-root-binding-001',"source_plan_commit=$ExpectedV10Plan","source_design_commit=$ExpectedV10Design","source_design_blob=$ExpectedV10DesignBlob",'patch_authority_root=<workspace>',"patch_header=$Header","repository_root=$RepositoryRoot","workspace_path=$V10Workspace","canonical_target=$V10MarkerPath",'failed_v9_terminal=ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO')
    [string]::Join("`n", $Lines) + "`n"
}

function Assert-A11V13PreservedEvidence {
    $V11Children = @(Get-ChildItem -LiteralPath $V11Workspace -Force | Sort-Object Name)
    if ($V11Children.Count -ne 2 -or @($V11Children | Where-Object PSIsContainer).Count -ne 0) { throw 'v11 inventory rejected' }
    foreach ($Name in $ExpectedV11.Keys) { Assert-A11V13FileIdentity -Path (Join-Path $V11Workspace $Name) -ByteCount $ExpectedV11[$Name][0] -Sha256 $ExpectedV11[$Name][1] -LeafLinkType 'None' }
    $V10Children = @(Get-ChildItem -LiteralPath $V10Workspace -Force | Sort-Object Name)
    if ($V10Children.Count -ne 3 -or @($V10Children | Where-Object PSIsContainer).Count -ne 0) { throw 'v10 inventory rejected' }
    foreach ($Name in $ExpectedV10.Keys) { Assert-A11V13FileIdentity -Path (Join-Path $V10Workspace $Name) -ByteCount $ExpectedV10[$Name][0] -Sha256 $ExpectedV10[$Name][1] -LeafLinkType 'None' }
    $ExpectedMarker = Get-A11V13ExpectedV10MarkerText
    if ($Utf8.GetString([IO.File]::ReadAllBytes($V10MarkerPath)) -cne $ExpectedMarker) { throw 'v10 marker text rejected' }
    if (Test-Path -LiteralPath $IntendedV9Workspace) { throw 'intended v9 namespace exists' }
    $V9Children = @(Get-ChildItem -LiteralPath $ExternalV9Workspace -Force | Sort-Object Name)
    if ($V9Children.Count -ne 2 -or @($V9Children | Where-Object PSIsContainer).Count -ne 0) { throw 'external v9 inventory rejected' }
    foreach ($Name in $ExpectedExternalV9.Keys) { Assert-A11V13FileIdentity -Path (Join-Path $ExternalV9Workspace $Name) -ByteCount $ExpectedExternalV9[$Name][0] -Sha256 $ExpectedExternalV9[$Name][1] -LeafLinkType 'None' }
    if ((Test-Path -LiteralPath $V8Workspace) -or (Test-Path -LiteralPath $ConsumedV6Workspace)) { throw 'consumed predecessor namespace exists' }
    if (Test-Path -LiteralPath $V12Workspace) { throw 'v12 namespace exists' }
    foreach ($Path in $V13ShadowPaths) { if (Test-Path -LiteralPath $Path) { throw 'v13 shadow path exists' } }
    $PlanText = $Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath)))
    $V12Incident = 'PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO'
    if (@($PlanText.Split([char]10) | Where-Object { $_ -ceq $V12Incident }).Count -ne 1) { throw 'v12 incident rejected' }
    $V11Incident = 'PRESERVED_V11_INCIDENT|plan_commit=30735e992d8670991beb0c2882b8f225ff89d978|controller_invocations=1|child_starts=0|phase=controller_preflight|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191|terminal=ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO'
    if (@($PlanText.Split([char]10) | Where-Object { $_ -ceq $V11Incident }).Count -ne 1) { throw 'v11 incident record rejected' }
    $Incident = 'PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO'
    if (@($PlanText.Split([char]10) | Where-Object { $_ -ceq $Incident }).Count -ne 1) { throw 'v10 incident record rejected' }
}

function Assert-A11V13Signature {
    param([object] $Signature, [string] $Subject, [string] $Thumbprint)
    if ($Signature.Status.ToString() -cne 'Valid' -or $null -eq $Signature.SignerCertificate -or [string]$Signature.SignerCertificate.Subject -cne $Subject -or -not [StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint, $Thumbprint)) { throw 'signature rejected' }
}

function Assert-A11V13LineageAndGit {
    $PlanCommit = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $PlanCommit -notmatch '\A[0-9a-f]{40}\z') { throw 'plan commit rejected' }
    $Chain = @(@($PlanCommit,$ExpectedDesign),@($ExpectedDesign,$ExpectedV12Plan),@($ExpectedV12Plan,$ExpectedV12Design),@($ExpectedV12Design,$ExpectedV11Plan),@($ExpectedV11Plan,$ExpectedV11Design),@($ExpectedV11Design,$ExpectedV10Plan),@($ExpectedV10Plan,$ExpectedV10Design),@($ExpectedV10Design,$ExpectedV9Plan),@($ExpectedV9Plan,$ExpectedV9Design),@($ExpectedV9Design,$ExpectedV8Plan),@($ExpectedV8Plan,$ExpectedAmendment),@($ExpectedAmendment,$ExpectedParserDesign),@($ExpectedParserDesign,$ExpectedV7Plan),@($ExpectedV7Plan,$ExpectedV7Design))
    foreach ($Pair in $Chain) { if ((git rev-list --parents -n 1 $Pair[0]) -cne "$($Pair[0]) $($Pair[1])") { throw 'lineage rejected' } }
    if ((git branch --show-current) -cne 'codex/wave0-model-contract') { throw 'branch rejected' }
    if ((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD) -cne 'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery') { throw 'plan identity rejected' }
    $Changed = @(git diff-tree --no-commit-id --name-only -r HEAD)
    if ($Changed.Count -ne 1 -or $Changed[0] -cne $PlanPath) { throw 'plan path rejected' }
    $Blobs = @(@('HEAD',$DesignPath,$ExpectedDesignBlob),@($ExpectedV12Plan,$V12PlanPath,$ExpectedV12PlanBlob),@($ExpectedV12Design,$V12DesignPath,$ExpectedV12DesignBlob),@($ExpectedV11Plan,$V11PlanPath,$ExpectedV11PlanBlob),@($ExpectedV11Design,$V11DesignPath,$ExpectedV11DesignBlob),@($ExpectedV10Plan,$V10PlanPath,$ExpectedV10PlanBlob),@($ExpectedV10Design,$V10DesignPath,$ExpectedV10DesignBlob),@($ExpectedV9Plan,$V9PlanPath,$ExpectedV9PlanBlob),@($ExpectedV9Design,$V9DesignPath,$ExpectedV9DesignBlob),@($ExpectedV8Plan,$V8PlanPath,$ExpectedV8PlanBlob),@($ExpectedAmendment,$AmendmentPath,$ExpectedAmendmentBlob),@($ExpectedParserDesign,$ParserDesignPath,$ExpectedParserDesignBlob),@($ExpectedV7Plan,$V7PlanPath,$ExpectedV7PlanBlob),@($ExpectedV7Design,$V7DesignPath,$ExpectedV7DesignBlob))
    foreach ($Record in $Blobs) { if ((git rev-parse "$($Record[0]):$($Record[1])") -cne $Record[2]) { throw 'blob lineage rejected' } }
    if (-not [string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'superproject rejected' }
    if ([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)), [IO.Path]::GetFullPath((git rev-parse --git-common-dir)))) { throw 'linked worktree isolation rejected' }
    if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0 -or @(git diff --cached --name-only).Count -ne 0 -or @(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'Git cleanliness rejected' }
}

function Assert-A11V13RuntimeAndProviders {
    Assert-A11V13FileIdentity -Path $FrozenPwsh -ByteCount 301368 -Sha256 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V13FileIdentity -Path $FrozenWindowsPowerShell -ByteCount 454656 -Sha256 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.8875 (WinBuild.160101.0800)' -ProductVersion '10.0.26100.8875'
    Assert-A11V13FileIdentity -Path $PwshSecurityManifest -ByteCount 15463 -Sha256 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' -LeafLinkType 'None'
    Assert-A11V13FileIdentity -Path $PwshSecurityDll -ByteCount 345952 -Sha256 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V13FileIdentity -Path $WindowsSecurityManifest -ByteCount 776 -Sha256 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' -LeafLinkType 'HardLink'
    Assert-A11V13FileIdentity -Path $WindowsSecurityDll -ByteCount 93696 -Sha256 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.1' -ProductVersion '10.0.26100.1'
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
    Assert-A11V13LineageAndGit
    Assert-A11V13PreservedEvidence
    Assert-A11V13RuntimeAndProviders
    $ControllerIdentity = Get-A11V13PlanSourceIdentity -Name 'task-1-stage0-plan-identity-controller-v13.ps1'
    $Stage0Identity = Get-A11V13PlanSourceIdentity -Name 'task-1-stage0-v13.ps1'
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($PSCommandPath), $ControllerPath)) { throw 'controller_path_rejected' }
    Assert-A11V13SourceIdentity -Path $ControllerPath -ByteCount $ControllerIdentity.byte_count -Sha256 $ControllerIdentity.sha256
    Assert-A11V13SourceIdentity -Path $Stage0Path -ByteCount $Stage0Identity.byte_count -Sha256 $Stage0Identity.sha256
    $Children = @(Get-ChildItem -LiteralPath $WorkspacePath -Force | Sort-Object Name)
    $ExpectedNames = @('task-1-stage0-plan-identity-controller-v13.ps1','task-1-stage0-v13.ps1') | Sort-Object
    if ($Children.Count -ne 2 -or @($Children | Where-Object PSIsContainer).Count -ne 0 -or [string]::Join("`n", @($Children.Name)) -cne [string]::Join("`n", $ExpectedNames)) { throw 'v13_inventory_rejected' }
    $V7Children = @(Get-ChildItem -LiteralPath $V7Workspace -Force)
    if ($V7Children.Count -ne 4 -or @($V7Children | Where-Object PSIsContainer).Count -ne 0) { throw 'v7_inventory_rejected' }
    foreach ($Name in $ExpectedV7.Keys) { Assert-A11V13FileIdentity -Path (Join-Path $V7Workspace $Name) -ByteCount $ExpectedV7[$Name][0] -Sha256 $ExpectedV7[$Name][1] -LeafLinkType 'None' }
    $Before = Get-A11V13WorkspaceSnapshot -Path $WorkspacePath

    $SecurityModule = Import-Module -Name $PwshSecurityManifest -Force -PassThru -ErrorAction Stop
    if (@($SecurityModule).Count -ne 1 -or [IO.Path]::GetFullPath([string]$SecurityModule.Path) -cne $PwshSecurityManifest -or @($SecurityModule.NestedModules).Count -ne 1 -or [IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path) -cne $PwshSecurityDll) { throw 'controller_security_provider_rejected' }
    $AuthCommand = Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop
    if (@($AuthCommand).Count -ne 1 -or [IO.Path]::GetFullPath([string]$AuthCommand.Module.Path) -cne $PwshSecurityManifest -or [IO.Path]::GetFullPath([string]$AuthCommand.DLL) -cne $PwshSecurityDll) { throw 'controller_authenticode_provenance_rejected' }
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $FrozenPwsh) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $FrozenWindowsPowerShell) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityManifest) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityDll) -Subject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityManifest) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '71F53A26BB1625E466727183409A30D03D7923DF'
    Assert-A11V13Signature -Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityDll) -Subject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -Thumbprint '71F53A26BB1625E466727183409A30D03D7923DF'

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
    if ($StdoutBytes.Length -ne $ExpectedChildBytes.Length -or (Get-A11V13BytesSha256 -Bytes $StdoutBytes) -cne (Get-A11V13BytesSha256 -Bytes $ExpectedChildBytes) -or $Utf8.GetString($StdoutBytes) -cne ($ExpectedStage0Terminal + "`n")) { throw 'child_stdout_rejected' }
    if ((Get-A11V13WorkspaceSnapshot -Path $WorkspacePath) -cne $Before) { throw 'child_side_effect_rejected' }
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
    $FailureDigest = Get-A11V13BytesSha256 -Bytes $Utf8.GetBytes($Failure)
    $StdoutDigest = if ($StdoutComplete) { Get-A11V13BytesSha256 -Bytes $StdoutBytes } else { 'unavailable' }
    $StderrDigest = if ($StderrComplete) { Get-A11V13BytesSha256 -Bytes $StderrBytes } else { 'unavailable' }
    $ExitText = if ($ExitCodeAvailable) { [string]$ExitCode } else { 'unavailable' }
    $Diagnostic = "ENTRYV13_CONTROLLER_DIAGNOSTIC|phase=$FailurePhase|child_started=$($ChildStarted.ToString().ToLowerInvariant())|starts=$StartCount|exit=$ExitText|timed_out=$($TimedOut.ToString().ToLowerInvariant())|stdout_complete=$($StdoutComplete.ToString().ToLowerInvariant())|stdout_bytes=$($StdoutBytes.Length)|stdout_sha256=$StdoutDigest|stderr_complete=$($StderrComplete.ToString().ToLowerInvariant())|stderr_bytes=$($StderrBytes.Length)|stderr_sha256=$StderrDigest|exception_sha256=$FailureDigest`n"
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

#### Frozen source: `task-1-stage0-v13.ps1`

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$WorkspacePath = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$ControllerPath = Join-Path $WorkspacePath 'task-1-stage0-plan-identity-controller-v13.ps1'
$Stage0Path = Join-Path $WorkspacePath 'task-1-stage0-v13.ps1'
$V12Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery'
$V11Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$V10Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'
$V10MarkerPath = Join-Path $V10Workspace 'task-0-patch-root-binding-v10.txt'
$ExternalV9Workspace = '<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$IntendedV9Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'
$V8Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'
$V7Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$PlanPath = 'docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md'
$V12PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery.md'
$V12DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery-design.md'
$V11PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md'
$V11DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md'
$V10PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery.md'
$V10DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery-design.md'
$V9PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery.md'
$V9DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery-design.md'
$V8PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery.md'
$ParserDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md'
$AmendmentPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-security-module-amendment-design.md'
$V7PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md'
$V7DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md'
$ExpectedDesign = '84b0f64fa5565d785e32fe3fbe5de1dc473f23aa'
$ExpectedDesignBlob = 'eb0260c4137cfc29bcefc3b410eb19cb88262a8c'
$ExpectedV12Plan = '97acd06f61fdac5df11e3a8fb21b641101b9f482'
$ExpectedV12PlanBlob = 'c11c95c5a4ce32c373599a41d755da7931640681'
$ExpectedV12Design = '15d34231f7f65f1be6f08eea5946eefd2b8949ba'
$ExpectedV12DesignBlob = '545fe2d74e3209902f1733c180295d89b671ae86'
$ExpectedV11Plan = '30735e992d8670991beb0c2882b8f225ff89d978'
$ExpectedV11PlanBlob = 'c677fa4280965e52a5b46e1452fa3b4d3bc22413'
$ExpectedV11Design = '29470670c4fe2095c0cedcf5ab389c2c82190e9c'
$ExpectedV11DesignBlob = '8ead81be4da26dbd3e17badade45b7c746e8f8ce'
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
$Stage0Terminal = 'ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)
$ExpectedV11 = [ordered]@{
    'task-1-stage0-raw-byte-controller-v11.ps1' = @([long]28071, 'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9')
    'task-1-stage0-v11.ps1' = @([long]21104, 'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')
}
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
$V13ShadowPaths = @(
    '<workspace>\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery',
    '<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery',
    '<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
)

function Get-A11V13BytesSha256 { param([byte[]] $Bytes) $Algorithm = [Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant() } finally { $Algorithm.Dispose() } }
function Get-A11V13FileSha256 { param([string] $Path) $Stream = [IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read); $Algorithm = [Security.Cryptography.SHA256]::Create(); try { [BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant() } finally { $Algorithm.Dispose(); $Stream.Dispose() } }
function Assert-A11V13ParentChainOrdinary { param([string] $Path) $Cursor=[IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path)); while(-not [string]::IsNullOrEmpty($Cursor)){ $Item=Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop; if(($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0-or-not[string]::IsNullOrEmpty([string]$Item.LinkType)){throw 'linked parent rejected'}; $Parent=[IO.Directory]::GetParent($Cursor); if($null-eq$Parent){break}; $Cursor=$Parent.FullName } }
function Assert-A11V13FileIdentity { param([string]$Path,[long]$ByteCount,[string]$Sha256,[string]$LeafLinkType,[string]$FileVersion='',[string]$ProductVersion='') if(-not[IO.Path]::IsPathFullyQualified($Path)-or-not[StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path),$Path)){throw 'file path rejected'}; $Item=Get-Item -LiteralPath $Path -Force -ErrorAction Stop; if($Item.PSIsContainer-or[long]$Item.Length-ne$ByteCount-or($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne 0){throw 'file identity rejected'}; $ActualLink=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType}; if(-not[StringComparer]::Ordinal.Equals($ActualLink,$LeafLinkType)){throw 'file link rejected'}; Assert-A11V13ParentChainOrdinary $Path; if((Get-A11V13FileSha256 $Path)-cne$Sha256){throw 'file digest rejected'}; $Streams=@(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop); if($Streams.Count-ne 1-or[string]$Streams[0].Stream-cne':$DATA'){throw 'file stream rejected'}; if($FileVersion-and[string]$Item.VersionInfo.FileVersion-cne$FileVersion){throw 'file version rejected'}; if($ProductVersion-and[string]$Item.VersionInfo.ProductVersion-cne$ProductVersion){throw 'product version rejected'} }
function Assert-A11V13SourceIdentity { param([string]$Path,[long]$ByteCount,[string]$Sha256) Assert-A11V13FileIdentity $Path $ByteCount $Sha256 'None'; $Bytes=[IO.File]::ReadAllBytes($Path); if($Bytes.Length-eq 0-or($Bytes.Length-ge 3-and$Bytes[0]-eq 0xEF-and$Bytes[1]-eq 0xBB-and$Bytes[2]-eq 0xBF)-or$Bytes-contains 0x0D-or$Bytes[-1]-ne 0x0A-or($Bytes.Length-gt 1-and$Bytes[-2]-eq 0x0A)){throw 'source encoding rejected'}; $Round=$Utf8.GetBytes($Utf8.GetString($Bytes)); if($Round.Length-ne$Bytes.Length-or(Get-A11V13BytesSha256 $Round)-cne$Sha256){throw 'source roundtrip rejected'}; $Streams=@(Get-Item -LiteralPath $Path -Stream *); if($Streams.Count-ne 1-or[string]$Streams[0].Stream-cne ':$DATA'){throw 'source stream rejected'} }
function Get-A11V13PlanSourceIdentity { param([string]$Name) $PlanText=$Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath))); $Matches=@($PlanText.Split([char]10)|Where-Object{$_.StartsWith("SOURCE_IDENTITY|$Name|",[StringComparison]::Ordinal)}); if($Matches.Count-ne 1){throw 'source record count rejected'}; $Parts=@($Matches[0].Split('|')); [long]$Count=0; if($Parts.Count-ne 4-or-not[long]::TryParse($Parts[2],[Globalization.NumberStyles]::None,[Globalization.CultureInfo]::InvariantCulture,[ref]$Count)-or$Parts[3]-notmatch'\A[0-9a-f]{64}\z'){throw 'source record rejected'}; [pscustomobject][ordered]@{byte_count=$Count;sha256=$Parts[3]} }
function Get-A11V13ExpectedV10MarkerText { $Header='CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-0-patch-root-binding-v10.txt'; $Lines=@('schema_version=1','binding_id=entryv10-patch-root-binding-001',"source_plan_commit=$ExpectedV10Plan","source_design_commit=$ExpectedV10Design","source_design_blob=$ExpectedV10DesignBlob",'patch_authority_root=<workspace>',"patch_header=$Header","repository_root=$RepositoryRoot","workspace_path=$V10Workspace","canonical_target=$V10MarkerPath",'failed_v9_terminal=ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO'); [string]::Join("`n",$Lines)+"`n" }
function Assert-A11V13PreservedEvidence { $V11Children=@(Get-ChildItem -LiteralPath $V11Workspace -Force|Sort-Object Name); if($V11Children.Count-ne 2-or@($V11Children|Where-Object PSIsContainer).Count-ne 0){throw 'v11 inventory rejected'}; foreach($Name in $ExpectedV11.Keys){Assert-A11V13FileIdentity (Join-Path $V11Workspace $Name) $ExpectedV11[$Name][0] $ExpectedV11[$Name][1] 'None'}; $V10Children=@(Get-ChildItem -LiteralPath $V10Workspace -Force|Sort-Object Name); if($V10Children.Count-ne 3-or@($V10Children|Where-Object PSIsContainer).Count-ne 0){throw 'v10 inventory rejected'}; foreach($Name in $ExpectedV10.Keys){Assert-A11V13FileIdentity (Join-Path $V10Workspace $Name) $ExpectedV10[$Name][0] $ExpectedV10[$Name][1] 'None'}; if($Utf8.GetString([IO.File]::ReadAllBytes($V10MarkerPath))-cne(Get-A11V13ExpectedV10MarkerText)){throw 'v10 marker rejected'}; if(Test-Path -LiteralPath $IntendedV9Workspace){throw 'intended v9 exists'}; $V9Children=@(Get-ChildItem -LiteralPath $ExternalV9Workspace -Force); if($V9Children.Count-ne 2-or@($V9Children|Where-Object PSIsContainer).Count-ne 0){throw 'v9 inventory rejected'}; foreach($Name in $ExpectedExternalV9.Keys){Assert-A11V13FileIdentity (Join-Path $ExternalV9Workspace $Name) $ExpectedExternalV9[$Name][0] $ExpectedExternalV9[$Name][1] 'None'}; if ((Test-Path -LiteralPath $V8Workspace) -or (Test-Path -LiteralPath $ConsumedV6Workspace)){throw 'consumed namespace exists'}; if(Test-Path -LiteralPath $V12Workspace){throw 'v12 namespace exists'}; foreach($Path in $V13ShadowPaths){if(Test-Path -LiteralPath $Path){throw 'v13 shadow path exists'}}; $PlanText=$Utf8.GetString([IO.File]::ReadAllBytes((Join-Path $RepositoryRoot $PlanPath))); $V12Incident='PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO'; if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V12Incident}).Count-ne 1){throw 'v12 incident rejected'}; $V11Incident='PRESERVED_V11_INCIDENT|plan_commit=30735e992d8670991beb0c2882b8f225ff89d978|controller_invocations=1|child_starts=0|phase=controller_preflight|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191|terminal=ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO'; if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V11Incident}).Count-ne 1){throw 'v11 incident rejected'}; $Incident='PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO'; if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$Incident}).Count-ne 1){throw 'v10 incident rejected'} }
function Assert-A11V13Signature { param([object]$Signature,[string]$Subject,[string]$Thumbprint) if($Signature.Status.ToString()-cne'Valid'-or$null-eq$Signature.SignerCertificate-or[string]$Signature.SignerCertificate.Subject-cne$Subject-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,$Thumbprint)){throw 'signature rejected'} }

Push-Location -LiteralPath $RepositoryRoot
$SecurityModule = $null
$TerminalBytes = $null
try {
    $PlanCommit = git rev-parse HEAD
    $Chain = @(@($PlanCommit,$ExpectedDesign),@($ExpectedDesign,$ExpectedV12Plan),@($ExpectedV12Plan,$ExpectedV12Design),@($ExpectedV12Design,$ExpectedV11Plan),@($ExpectedV11Plan,$ExpectedV11Design),@($ExpectedV11Design,$ExpectedV10Plan),@($ExpectedV10Plan,$ExpectedV10Design),@($ExpectedV10Design,$ExpectedV9Plan),@($ExpectedV9Plan,$ExpectedV9Design),@($ExpectedV9Design,$ExpectedV8Plan),@($ExpectedV8Plan,$ExpectedAmendment),@($ExpectedAmendment,$ExpectedParserDesign),@($ExpectedParserDesign,$ExpectedV7Plan),@($ExpectedV7Plan,$ExpectedV7Design))
    if($PlanCommit-notmatch'\A[0-9a-f]{40}\z'){throw 'plan commit rejected'}
    foreach($Pair in $Chain){if((git rev-list --parents -n 1 $Pair[0])-cne"$($Pair[0]) $($Pair[1])"){throw 'lineage rejected'}}
    if((git branch --show-current)-cne'codex/wave0-model-contract'){throw 'branch rejected'}
    if((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD)-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery'){throw 'plan identity rejected'}
    $Changed=@(git diff-tree --no-commit-id --name-only -r HEAD); if($Changed.Count-ne 1-or$Changed[0]-cne$PlanPath){throw 'plan path rejected'}
    $Blobs=@(@('HEAD',$DesignPath,$ExpectedDesignBlob),@($ExpectedV12Plan,$V12PlanPath,$ExpectedV12PlanBlob),@($ExpectedV12Design,$V12DesignPath,$ExpectedV12DesignBlob),@($ExpectedV11Plan,$V11PlanPath,$ExpectedV11PlanBlob),@($ExpectedV11Design,$V11DesignPath,$ExpectedV11DesignBlob),@($ExpectedV10Plan,$V10PlanPath,$ExpectedV10PlanBlob),@($ExpectedV10Design,$V10DesignPath,$ExpectedV10DesignBlob),@($ExpectedV9Plan,$V9PlanPath,$ExpectedV9PlanBlob),@($ExpectedV9Design,$V9DesignPath,$ExpectedV9DesignBlob),@($ExpectedV8Plan,$V8PlanPath,$ExpectedV8PlanBlob),@($ExpectedAmendment,$AmendmentPath,$ExpectedAmendmentBlob),@($ExpectedParserDesign,$ParserDesignPath,$ExpectedParserDesignBlob),@($ExpectedV7Plan,$V7PlanPath,$ExpectedV7PlanBlob),@($ExpectedV7Design,$V7DesignPath,$ExpectedV7DesignBlob)); foreach($Record in $Blobs){if((git rev-parse "$($Record[0]):$($Record[1])")-cne$Record[2]){throw 'blob rejected'}}
    if(-not[string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))){throw 'superproject rejected'}
    if([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)),[IO.Path]::GetFullPath((git rev-parse --git-common-dir)))){throw 'linked isolation rejected'}
    if(@(git status --porcelain=v1 --untracked-files=all).Count-ne 0-or@(git diff --cached --name-only).Count-ne 0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne 0){throw 'Git cleanliness rejected'}
    Assert-A11V13PreservedEvidence
    $ControllerIdentity=Get-A11V13PlanSourceIdentity 'task-1-stage0-plan-identity-controller-v13.ps1'; $Stage0Identity=Get-A11V13PlanSourceIdentity 'task-1-stage0-v13.ps1'
    if(-not[StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($PSCommandPath),$Stage0Path)){throw 'Stage0 path rejected'}
    Assert-A11V13SourceIdentity $ControllerPath $ControllerIdentity.byte_count $ControllerIdentity.sha256; Assert-A11V13SourceIdentity $Stage0Path $Stage0Identity.byte_count $Stage0Identity.sha256
    $Children=@(Get-ChildItem -LiteralPath $WorkspacePath -Force|Sort-Object Name); $Names=@('task-1-stage0-plan-identity-controller-v13.ps1','task-1-stage0-v13.ps1')|Sort-Object; if($Children.Count-ne 2-or@($Children|Where-Object PSIsContainer).Count-ne 0-or[string]::Join("`n",@($Children.Name))-cne[string]::Join("`n",$Names)){throw 'v13 inventory rejected'}
    $V7Children=@(Get-ChildItem -LiteralPath $V7Workspace -Force); if($V7Children.Count-ne 4-or@($V7Children|Where-Object PSIsContainer).Count-ne 0){throw 'v7 inventory rejected'}; foreach($Name in $ExpectedV7.Keys){Assert-A11V13FileIdentity (Join-Path $V7Workspace $Name) $ExpectedV7[$Name][0] $ExpectedV7[$Name][1] 'None'}
    Assert-A11V13FileIdentity $FrozenPwsh 301368 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' 'None' '7.6.4.500' '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V13FileIdentity $FrozenWindowsPowerShell 454656 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' 'HardLink' '10.0.26100.8875 (WinBuild.160101.0800)' '10.0.26100.8875'
    Assert-A11V13FileIdentity $PwshSecurityManifest 15463 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' 'None'; Assert-A11V13FileIdentity $PwshSecurityDll 345952 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' 'None' '7.6.4.500' '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-A11V13FileIdentity $WindowsSecurityManifest 776 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' 'HardLink'; Assert-A11V13FileIdentity $WindowsSecurityDll 93696 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' 'HardLink' '10.0.26100.1' '10.0.26100.1'
    $CurrentProcessPath=[IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName); if(-not[StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath,$FrozenPwsh)-or$PSVersionTable.PSVersion.ToString()-cne'7.6.4'-or$PSVersionTable.PSEdition-cne'Core'){throw 'Stage0 runtime rejected'}
    $SecurityModule=Import-Module -Name $PwshSecurityManifest -Force -PassThru -ErrorAction Stop; if(@($SecurityModule).Count-ne 1-or[IO.Path]::GetFullPath([string]$SecurityModule.Path)-cne$PwshSecurityManifest-or@($SecurityModule.NestedModules).Count-ne 1-or[IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path)-cne$PwshSecurityDll){throw 'Security provider rejected'}
    $AuthCommand=Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop; if(@($AuthCommand).Count-ne 1-or[IO.Path]::GetFullPath([string]$AuthCommand.Module.Path)-cne$PwshSecurityManifest-or[IO.Path]::GetFullPath([string]$AuthCommand.DLL)-cne$PwshSecurityDll){throw 'Authenticode provenance rejected'}
    Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $FrozenPwsh) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'AB172913A2960A224809EE8A0C371CD47A079B72'; Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $FrozenWindowsPowerShell) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'; Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityManifest) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' 'AB172913A2960A224809EE8A0C371CD47A079B72'; Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $PwshSecurityDll) 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'; Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityManifest) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '71F53A26BB1625E466727183409A30D03D7923DF'; Assert-A11V13Signature (Get-AuthenticodeSignature -LiteralPath $WindowsSecurityDll) 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' '71F53A26BB1625E466727183409A30D03D7923DF'
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
- Create: `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-plan-identity-controller-v13.ps1`
- Create: `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-v13.ps1`
- Read: `docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md`
- Read: `docs/superpowers/specs/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md`

**Interfaces:**
- Consumes: exact committed design/plan/v12 lineage, absent v13 and v12 namespaces, exact preserved v12 plan-review and v11 runtime NO_GOs, inherited predecessor records, runtime/provider identities, and clean linked/canonical worktrees.
- Produces: a read-only v12 identity RED followed by exactly two immutable v13 source files whose bytes equal the frozen plan blocks.

- [ ] **Step 1: Run the complete read-only entry gate**

From the linked repository, require exact plan parent, design/plan blobs, author, committer, subject, one changed plan path, branch, linked-worktree isolation, non-submodule state, empty staging, clean linked/canonical worktrees, absent v13 namespace and all three shadow paths, exact v11 two-file identities and incident record, exact inherited v10/v9/v7 records, required v8/v6/intended-v9 absences, and exact six runtime/provider identities and signatures.

Run this complete gate without invoking either source:

```powershell
$ErrorActionPreference='Stop'
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot='<repo>'
$PlanPath='docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'
$DesignPath='docs/superpowers/specs/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md'
$V13=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$V12=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery'
Set-Location -LiteralPath $RepositoryRoot
$Head=git rev-parse HEAD
if($Head-notmatch'\A[0-9a-f]{40}\z'-or(git rev-list --parents -n 1 HEAD)-cne"$Head 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa"){throw 'plan parent rejected'}
if((git rev-parse "HEAD:$DesignPath")-cne'eb0260c4137cfc29bcefc3b410eb19cb88262a8c'){throw 'design blob rejected'}
if((git hash-object -- $PlanPath)-cne(git rev-parse "HEAD:$PlanPath")){throw 'working plan blob rejected'}
if((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD)-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery'){throw 'plan identity rejected'}
$Changed=@(git diff-tree --no-commit-id --name-only -r HEAD)
if($Changed.Count-ne1-or$Changed[0]-cne$PlanPath-or(git branch --show-current)-cne'codex/wave0-model-contract'){throw 'plan path/branch rejected'}
if(-not[string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))){throw 'superproject rejected'}
if([StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((git rev-parse --git-dir)),[IO.Path]::GetFullPath((git rev-parse --git-common-dir)))){throw 'linked isolation rejected'}
if(@(git status --porcelain=v1 --untracked-files=all).Count-ne0-or@(git diff --cached --name-only).Count-ne0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0){throw 'Git cleanliness rejected'}
if(Test-Path -LiteralPath $V13){throw 'v13 namespace exists'}
if(Test-Path -LiteralPath $V12){throw 'preserved v12 namespace exists'}
$PlanText=[IO.File]::ReadAllText((Join-Path $RepositoryRoot $PlanPath),[Text.UTF8Encoding]::new($false,$true));$V12Incident='PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO';if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V12Incident}).Count-ne1){throw 'v12 incident record rejected'};$V11Incident='PRESERVED_V11_INCIDENT|plan_commit=30735e992d8670991beb0c2882b8f225ff89d978|controller_invocations=1|child_starts=0|phase=controller_preflight|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191|terminal=ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO';if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V11Incident}).Count-ne1){throw 'v11 incident record rejected'}
function Get-EntrySha([string]$Path){$S=[IO.File]::OpenRead($Path);$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($S)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose();$S.Dispose()}}
$Inventories=@(
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'),[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')}),
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'),[ordered]@{'task-0-patch-root-binding-v10.txt'=@(1058,'d3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5');'task-1-stage0-transport-controller-v10.ps1'=@(22802,'2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e');'task-1-stage0-v10.ps1'=@(25072,'5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')}),
    @('<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery',[ordered]@{'task-1-stage0-transport-controller-v9.ps1'=@(17994,'795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff');'task-1-stage0-v9.ps1'=@(20258,'34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')}),
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'),[ordered]@{'task-1-stage0-audit-v7.ps1'=@(3849,'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b');'task-1-scalar-identity-tests-v7.ps1'=@(8849,'977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9');'task-1-scalar-identity-red-v7.psm1'=@(991,'34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919');'task-1-scalar-identity-green-v7.psm1'=@(2553,'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')})
)
foreach($Inventory in $Inventories){$Root=[string]$Inventory[0];$Expected=[Collections.IDictionary]$Inventory[1];$Items=@(Get-ChildItem -LiteralPath $Root -Force);if($Items.Count-ne$Expected.Count-or@($Items|Where-Object PSIsContainer).Count-ne0){throw "inventory rejected: $Root"};foreach($Name in $Expected.Keys){$Item=Get-Item -LiteralPath (Join-Path $Root $Name) -Force;if($Item.Length-ne[long]$Expected[$Name][0]-or(Get-EntrySha $Item.FullName)-cne[string]$Expected[$Name][1]){throw "identity rejected: $Name"}}}
$Absences=@((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'),'<workspace>\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery');foreach($Path in $Absences){if(Test-Path -LiteralPath $Path){throw "required absence rejected: $Path"}}
$Runtime=@(
    @('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe',301368,'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f','None'),
    @('C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',454656,'7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5','HardLink'),
    @('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',15463,'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a','None'),
    @('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll',345952,'5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90','None'),
    @('C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',776,'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30','HardLink'),
    @('C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll',93696,'9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010','HardLink')
)
foreach($Record in $Runtime){$Item=Get-Item -LiteralPath $Record[0] -Force;$Link=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType};if($Item.Length-ne[long]$Record[1]-or(Get-EntrySha $Record[0])-cne[string]$Record[2]-or$Link-cne[string]$Record[3]){throw "runtime/provider rejected: $($Record[0])"}}
$VersionExpected=@(@('7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'),@('10.0.26100.8875 (WinBuild.160101.0800)','10.0.26100.8875'),@('',''),@('7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'),@('',''),@('10.0.26100.1','10.0.26100.1'))
for($Index=0;$Index-lt$Runtime.Count;$Index++){$Item=Get-Item -LiteralPath $Runtime[$Index][0] -Force;$Streams=@(Get-Item -LiteralPath $Runtime[$Index][0] -Stream * -ErrorAction Stop);if($Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'){throw 'runtime/provider stream rejected'};if($VersionExpected[$Index][0]-and[string]$Item.VersionInfo.FileVersion-cne[string]$VersionExpected[$Index][0]){throw 'runtime/provider file version rejected'};if($VersionExpected[$Index][1]-and[string]$Item.VersionInfo.ProductVersion-cne[string]$VersionExpected[$Index][1]){throw 'runtime/provider product version rejected'}}
$SignatureExpected=@(
    @($Runtime[0][0],'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[1][0],'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'),
    @($Runtime[2][0],'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[3][0],'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'),
    @($Runtime[4][0],'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF'),
    @($Runtime[5][0],'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF')
)
$SecurityModule=Import-Module -Name $Runtime[2][0] -Force -PassThru -ErrorAction Stop
try{if(@($SecurityModule).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.Path)-cne[string]$Runtime[2][0]-or@($SecurityModule.NestedModules).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path)-cne[string]$Runtime[3][0]){throw 'Security provider provenance rejected'};$AuthCommand=Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop;if(@($AuthCommand).Count-ne1-or[IO.Path]::GetFullPath([string]$AuthCommand.Module.Path)-cne[string]$Runtime[2][0]-or[IO.Path]::GetFullPath([string]$AuthCommand.DLL)-cne[string]$Runtime[3][0]){throw 'Authenticode command provenance rejected'};foreach($Record in $SignatureExpected){$Signature=Get-AuthenticodeSignature -LiteralPath $Record[0];if($Signature.Status.ToString()-cne'Valid'-or$null-eq$Signature.SignerCertificate-or[string]$Signature.SignerCertificate.Subject-cne[string]$Record[1]-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,[string]$Record[2])){throw "signature rejected: $($Record[0])"}}}finally{[void](Remove-Module -ModuleInfo $SecurityModule -Force)}
'ENTRYV13_MATERIALIZATION_ENTRY_PASS|v12=preserved_plan_no_go|v11_files=2|v13=absent|runtimes=2|providers=2|linked=clean|canonical=clean'
```

Any difference stops without materialization as `ENTRYV13_MATERIALIZATION_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Prove the preserved v12 frozen-source identity defect (RED)**

Read the committed v12 plan as data only. Extract both frozen sources, parse their ASTs in memory, and prove each contains exactly one HEAD identity comparison against the stale v11 subject rather than the actual v12 subject. Do not materialize or execute v12 and do not start Windows PowerShell.

```powershell
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract';$V12Commit='97acd06f61fdac5df11e3a8fb21b641101b9f482';$V12Plan='docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery.md';$V12Workspace=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery';Set-Location -LiteralPath $RepositoryRoot
if(Test-Path -LiteralPath $V12Workspace){throw 'preserved v12 namespace exists'}
$Incident='PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO';$CurrentPlan=[IO.File]::ReadAllText((Join-Path $RepositoryRoot 'docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'),[Text.UTF8Encoding]::new($false,$true));if(@($CurrentPlan.Split([char]10)|Where-Object{$_-ceq$Incident}).Count-ne1){throw 'v12 incident rejected'}
$Lines=@(git show "${V12Commit}:$V12Plan");if($LASTEXITCODE-ne0){throw 'v12 plan read rejected'};$Text=[string]::Join("`n",$Lines)+"`n";$Stale='kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 raw byte output recovery';$Actual=(git show -s --format='%an|%ae|%cn|%ce|%s' $V12Commit)
if($Actual-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 preflight expression recovery'-or$Actual-ceq$Stale){throw 'v12 identity fixture rejected'}
foreach($Name in @('task-1-stage0-preflight-controller-v12.ps1','task-1-stage0-v12.ps1')){$Pattern='(?ms)^#### Frozen source: `'+[regex]::Escape($Name)+'`\n\n```powershell\n(?<body>.*?)^```\n';$M=[regex]::Matches($Text,$Pattern);if($M.Count-ne1){throw 'v12 frozen source count rejected'};$T=$null;$E=$null;$A=[Management.Automation.Language.Parser]::ParseInput($M[0].Groups['body'].Value,[ref]$T,[ref]$E);if(@($E).Count-ne0){throw 'v12 frozen source parser rejected'};$C=@($A.FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Cne-and$N.Left.Extent.Text.Contains("git show -s --format='%an|%ae|%cn|%ce|%s' HEAD",[StringComparison]::Ordinal)},$true));if($C.Count-ne1-or$C[0].Right-isnot[Management.Automation.Language.StringConstantExpressionAst]-or[string]$C[0].Right.Value-cne$Stale-or[string]$C[0].Right.Value-ceq$Actual){throw 'v12 stale identity RED rejected'}}
'ENTRYV13_PLAN_IDENTITY_RED_PASS|sources=2|stale=2|actual=0|v12_materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0'
```

- [ ] **Step 3: Extract and identity-check both frozen source blocks**

Read the committed plan blob. Find exactly one heading and one `powershell` fence for each frozen filename, preserve every byte between the opening-fence LF and closing fence, require the two exact `SOURCE_IDENTITY` records, require strict UTF-8/no-BOM/LF/single-final-LF, and parse both strings in memory with the current PowerShell 7 parser. Do not execute either block.

```powershell
$PlanPath='docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'
$Utf8=[Text.UTF8Encoding]::new($false,$true)
$PlanBytes=[IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $PlanPath))
if($PlanBytes-contains0x0D-or$PlanBytes[-1]-ne0x0A){throw 'plan encoding rejected'}
$PlanText=$Utf8.GetString($PlanBytes)
$Expected=[ordered]@{}
foreach($Line in $PlanText.Split([char]10)){
    if($Line.StartsWith('SOURCE_IDENTITY|',[StringComparison]::Ordinal)){
        $Parts=$Line.Split('|');if($Parts.Count-ne4){throw 'source identity rejected'}
        $Expected[$Parts[1]]=@([long]$Parts[2],$Parts[3])
    }
}
if($Expected.Count-ne2){throw 'source identity count rejected'}
foreach($Name in $Expected.Keys){
    $Pattern='(?ms)^#### Frozen source: `'+[regex]::Escape($Name)+'`\n\n```powershell\n(?<body>.*?)^```\n'
    $Matches=[regex]::Matches($PlanText,$Pattern);if($Matches.Count-ne1){throw 'frozen block count rejected'}
    $Source=$Matches[0].Groups['body'].Value;$Bytes=$Utf8.GetBytes($Source)
    $A=[Security.Cryptography.SHA256]::Create();try{$Sha=[BitConverter]::ToString($A.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}
    if($Bytes.Length-ne[long]$Expected[$Name][0]-or$Sha-cne[string]$Expected[$Name][1]){throw 'frozen block identity rejected'}
    $Tokens=$null;$Errors=$null;[void][Management.Automation.Language.Parser]::ParseInput($Source,[ref]$Tokens,[ref]$Errors)
    if(@($Errors).Count-ne0){throw 'PowerShell 7 parser rejected'}
}
'ENTRYV13_SOURCE_BLOCK_ADMISSION_PASS|files=2|parser=7.6.4|errors=0'
```

- [ ] **Step 4: Materialize both files with one `apply_patch` call**

Construct one patch in memory from the admitted blocks. Use exactly these full shared-root-relative headers:

```text
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-plan-identity-controller-v13.ps1
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-v13.ps1
```

Invoke `apply_patch` once. The call is consumed at invocation even if its result is empty, ambiguous, disconnected, timed out, or erroneous. Never issue a second patch.

- [ ] **Step 5: Verify exact materialization and preservation**

Require exactly two ordinary v13 files and no directory child; exact plan-pinned byte counts and SHA-256; strict UTF-8/no-BOM/LF/single-final-LF; canonical containment; ordinary parents; no link/reparse point; one default data stream; all v13 shadows absent; exact v11/v10/v9/v7 evidence unchanged; required v8/v6/intended-v9 absences; exact runtime/providers/signatures; unchanged HEAD/branch; empty staging; and clean linked/canonical worktrees.

```powershell
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$Children=@(Get-ChildItem -LiteralPath $Workspace -Force|Sort-Object Name)
if($Children.Count-ne2-or@($Children|Where-Object PSIsContainer).Count-ne0){throw 'v13 inventory rejected'}
$Expected=[ordered]@{'task-1-stage0-plan-identity-controller-v13.ps1'=@(31491,'dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086');'task-1-stage0-v13.ps1'=@(24403,'18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967')}
foreach($Name in $Expected.Keys){$Path=Join-Path $Workspace $Name;$Item=Get-Item -LiteralPath $Path -Force;$Bytes=[IO.File]::ReadAllBytes($Path);$Streams=@(Get-Item -LiteralPath $Path -Stream *);$Sha=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant();if($Item.PSIsContainer-or$Item.Length-ne[long]$Expected[$Name][0]-or$Sha-cne[string]$Expected[$Name][1]-or($Item.Attributes-band[IO.FileAttributes]::ReparsePoint)-ne0-or-not[string]::IsNullOrEmpty([string]$Item.LinkType)-or$Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'-or$Bytes-contains0x0D-or$Bytes[-1]-ne0x0A-or($Bytes.Length-gt1-and$Bytes[-2]-eq0x0A)){throw "v13 source rejected: $Name"}}
$Shadow=@('<workspace>\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery');foreach($Path in $Shadow){if(Test-Path -LiteralPath $Path){throw 'v13 shadow rejected'}}
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract';$CanonicalRoot='<repo>';Set-Location -LiteralPath $RepositoryRoot
$Preserved=@(
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'),[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')}),
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery'),[ordered]@{'task-0-patch-root-binding-v10.txt'=@(1058,'d3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5');'task-1-stage0-transport-controller-v10.ps1'=@(22802,'2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e');'task-1-stage0-v10.ps1'=@(25072,'5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')}),
    @('<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery',[ordered]@{'task-1-stage0-transport-controller-v9.ps1'=@(17994,'795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff');'task-1-stage0-v9.ps1'=@(20258,'34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')}),
    @((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'),[ordered]@{'task-1-stage0-audit-v7.ps1'=@(3849,'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b');'task-1-scalar-identity-tests-v7.ps1'=@(8849,'977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9');'task-1-scalar-identity-red-v7.psm1'=@(991,'34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919');'task-1-scalar-identity-green-v7.psm1'=@(2553,'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')})
);foreach($Pair in $Preserved){$Root=[string]$Pair[0];$Map=[Collections.IDictionary]$Pair[1];$Items=@(Get-ChildItem -LiteralPath $Root -Force);if($Items.Count-ne$Map.Count-or@($Items|Where-Object PSIsContainer).Count-ne0){throw 'preserved inventory rejected'};foreach($Name in $Map.Keys){$Path=Join-Path $Root $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$Map[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Map[$Name][1]){throw 'preserved identity rejected'}}}
$RequiredAbsent=@((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'));foreach($Path in $RequiredAbsent){if(Test-Path -LiteralPath $Path){throw 'preserved absence rejected'}}
$Runtime=@(@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe',301368,'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'),@('C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',454656,'7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'),@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',15463,'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a'),@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll',345952,'5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90'),@('C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',776,'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30'),@('C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll',93696,'9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010'));foreach($Record in $Runtime){$Path=[string]$Record[0];if((Get-Item -LiteralPath $Path).Length-ne[long]$Record[1]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Record[2]){throw 'runtime/provider preservation rejected'}}
$RuntimeEvidence=@(
    @($Runtime[0][0],'None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[1][0],'HardLink','10.0.26100.8875 (WinBuild.160101.0800)','10.0.26100.8875','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'),
    @($Runtime[2][0],'None','','','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[3][0],'None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'),
    @($Runtime[4][0],'HardLink','','','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF'),
    @($Runtime[5][0],'HardLink','10.0.26100.1','10.0.26100.1','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF')
)
foreach($Record in $RuntimeEvidence){$Item=Get-Item -LiteralPath $Record[0] -Force;$Link=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType};$Streams=@(Get-Item -LiteralPath $Record[0] -Stream * -ErrorAction Stop);if($Link-cne[string]$Record[1]-or$Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'-or($Record[2]-and[string]$Item.VersionInfo.FileVersion-cne[string]$Record[2])-or($Record[3]-and[string]$Item.VersionInfo.ProductVersion-cne[string]$Record[3])){throw 'runtime/provider metadata preservation rejected'}}
$SecurityModule=Import-Module -Name $Runtime[2][0] -Force -PassThru -ErrorAction Stop
try{if(@($SecurityModule).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.Path)-cne[string]$Runtime[2][0]-or@($SecurityModule.NestedModules).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path)-cne[string]$Runtime[3][0]){throw 'Security provider preservation rejected'};$AuthCommand=Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop;if(@($AuthCommand).Count-ne1-or[IO.Path]::GetFullPath([string]$AuthCommand.Module.Path)-cne[string]$Runtime[2][0]-or[IO.Path]::GetFullPath([string]$AuthCommand.DLL)-cne[string]$Runtime[3][0]){throw 'Authenticode provenance preservation rejected'};foreach($Record in $RuntimeEvidence){$Signature=Get-AuthenticodeSignature -LiteralPath $Record[0];if($Signature.Status.ToString()-cne'Valid'-or$null-eq$Signature.SignerCertificate-or[string]$Signature.SignerCertificate.Subject-cne[string]$Record[4]-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,[string]$Record[5])){throw 'runtime/provider signature preservation rejected'}}}finally{[void](Remove-Module -ModuleInfo $SecurityModule -Force)}
if((git branch --show-current)-cne'codex/wave0-model-contract'-or@(git status --porcelain=v1 --untracked-files=all).Count-ne0-or@(git diff --cached --name-only).Count-ne0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0){throw 'materialization preservation Git rejected'}
'ENTRYV13_MATERIALIZATION_PASS|files=2|directories=0|shadows=0|writes=1|retries=0'
```

### Task 2: Dual-parser and identity/semantic static GREEN admission

**Files:**
- Read only: `.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/task-1-stage0-raw-byte-controller-v11.ps1`
- Test: `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-plan-identity-controller-v13.ps1`
- Test: `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-v13.ps1`

**Interfaces:**
- Consumes: exact Task 1 inventory and the successful preserved-v12 identity RED.
- Produces: dual-parser admission and one v13 identity/semantic/raw-output GREEN without invoking either v13 source.

- [ ] **Step 1: Run PowerShell 7 and Windows PowerShell 5.1 parser admission**

PowerShell 7 parses both v13 files in the controller shell. Then this command
starts the exact Windows PowerShell executable once and uses only
`Parser.ParseFile` on the same canonical files:

```powershell
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
foreach($Name in @('task-1-stage0-plan-identity-controller-v13.ps1','task-1-stage0-v13.ps1')){$Tokens=$null;$Errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $Workspace $Name),[ref]$Tokens,[ref]$Errors);if(@($Errors).Count-ne0){throw 'PowerShell 7 parser rejected'}}
'ENTRYV13_PARSER_PASS|runtime=powershell_core_7_6_4|files=2|errors=0'
$env:A11V13_WORKSPACE=$Workspace
try{
    & 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -Command '& { $ErrorActionPreference="Stop";if(-not[StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName),"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")-or$PSVersionTable.PSVersion.Major-ne5-or$PSVersionTable.PSVersion.Minor-ne1){throw "parser process rejected"};foreach($Name in @("task-1-stage0-plan-identity-controller-v13.ps1","task-1-stage0-v13.ps1")){$Tokens=$null;$Errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Join-Path $env:A11V13_WORKSPACE $Name),[ref]$Tokens,[ref]$Errors);if(@($Errors).Count-ne0){throw "Windows PowerShell parser rejected"}};"ENTRYV13_PARSER_PASS|runtime=windows_powershell_5_1|files=2|errors=0" }'
    if($LASTEXITCODE-ne0){throw 'Windows PowerShell parser process rejected'}
}
finally{Remove-Item Env:A11V13_WORKSPACE -ErrorAction SilentlyContinue}
```

Any parser process uncertainty is `ENTRYV13_PREFLIGHT_CONTROLLER_UNPROVABLE / NO_GO`; do not start it again.

- [ ] **Step 2: Run identity-consistency, semantic, and complete static GREEN**

Parse the exact frozen v11 condition literal and corrected v13 literal in memory without executing either. Require both parser error counts zero; v11 must have one command/two duplicate `LiteralPath`/zero `Or`/zero parentheses, while v13 must have two commands/one `LiteralPath` each/one `Or`/two parentheses. Then inspect both canonical v13 source ASTs and require the same corrected shape at every predecessor-absence condition.

```powershell
$Bad='if (Test-Path -LiteralPath $V8Workspace -or Test-Path -LiteralPath $ConsumedV6Workspace) { throw ''consumed predecessor namespace exists'' }'
$Good='if ((Test-Path -LiteralPath $V8Workspace) -or (Test-Path -LiteralPath $ConsumedV6Workspace)) { throw ''consumed predecessor namespace exists'' }'
function Get-Shape([string]$Text){
    $T=$null;$E=$null;$A=[Management.Automation.Language.Parser]::ParseInput($Text,[ref]$T,[ref]$E)
    $C=@($A.FindAll({param($N)$N-is[Management.Automation.Language.CommandAst]},$true))
    $L=@($C|ForEach-Object{$_.CommandElements}|Where-Object{$_-is[Management.Automation.Language.CommandParameterAst]-and$_.ParameterName-ceq'LiteralPath'})
    $O=@($A.FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Or},$true))
    $P=@($A.FindAll({param($N)$N-is[Management.Automation.Language.ParenExpressionAst]},$true))
    [pscustomobject]@{errors=@($E).Count;commands=$C.Count;literalpath=$L.Count;binary_or=$O.Count;paren=$P.Count}
}
$B=Get-Shape $Bad;$G=Get-Shape $Good
if($B.errors-ne0-or$B.commands-ne1-or$B.literalpath-ne2-or$B.binary_or-ne0-or$B.paren-ne0){throw 'bad fixture did not reproduce RED'}
if($G.errors-ne0-or$G.commands-ne2-or$G.literalpath-ne2-or$G.binary_or-ne1-or$G.paren-ne2){throw 'good fixture rejected'}
'ENTRYV13_PREFLIGHT_EXPRESSION_GREEN_PASS|commands=2|literalpath_each=1|binary_or=1|paren=2|starts=0'
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery';$Controller=Join-Path $Workspace 'task-1-stage0-plan-identity-controller-v13.ps1';$Stage0=Join-Path $Workspace 'task-1-stage0-v13.ps1'
$CT=[IO.File]::ReadAllText($Controller,[Text.UTF8Encoding]::new($false,$true));$ST=[IO.File]::ReadAllText($Stage0,[Text.UTF8Encoding]::new($false,$true));$T=$null;$E=$null;$CA=[Management.Automation.Language.Parser]::ParseFile($Controller,[ref]$T,[ref]$E);if(@($E).Count-ne0){throw 'controller parse rejected'};$T=$null;$E=$null;$SA=[Management.Automation.Language.Parser]::ParseFile($Stage0,[ref]$T,[ref]$E);if(@($E).Count-ne0){throw 'Stage0 parse rejected'}
$ExpectedIdentity='kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery';$StaleIdentity='kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 raw byte output recovery';$V12Identity='kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 Stage 0 preflight expression recovery';$Head=git rev-parse HEAD
if((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD)-cne$ExpectedIdentity-or(git rev-list --parents -n 1 HEAD)-cne"$Head 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa"-or(git rev-list --parents -n 1 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa)-cne'84b0f64fa5565d785e32fe3fbe5de1dc473f23aa 97acd06f61fdac5df11e3a8fb21b641101b9f482'){throw 'identity lineage rejected'}
foreach($Ast in @($CA,$SA)){$Comparisons=@($Ast.FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Cne-and$N.Left.Extent.Text.Contains("git show -s --format='%an|%ae|%cn|%ce|%s' HEAD",[StringComparison]::Ordinal)},$true));if($Comparisons.Count-ne1-or$Comparisons[0].Right-isnot[Management.Automation.Language.StringConstantExpressionAst]-or[string]$Comparisons[0].Right.Value-cne$ExpectedIdentity-or[string]$Comparisons[0].Right.Value-ceq$StaleIdentity-or[string]$Comparisons[0].Right.Value-ceq$V12Identity){throw 'source identity consistency rejected'}}
'ENTRYV13_PLAN_IDENTITY_GREEN_PASS|sources=2|comparisons=2|actual=2|stale=0|v12_subject=0|lineage=exact|starts=0'
foreach($Ast in @($CA,$SA)){$Target=@($Ast.FindAll({param($N)$N-is[Management.Automation.Language.IfStatementAst]-and$N.Clauses.Count-eq1-and$N.Clauses[0].Item1.Extent.Text.Contains('$V8Workspace',[StringComparison]::Ordinal)-and$N.Clauses[0].Item1.Extent.Text.Contains('$ConsumedV6Workspace',[StringComparison]::Ordinal)},$true));if($Target.Count-ne1){throw 'canonical semantic target rejected'};$Condition=$Target[0].Clauses[0].Item1;$Commands=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.CommandAst]},$true));$Literal=@($Commands|ForEach-Object{$_.CommandElements}|Where-Object{$_-is[Management.Automation.Language.CommandParameterAst]-and$_.ParameterName-ceq'LiteralPath'});$Or=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Or},$true));$Paren=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.ParenExpressionAst]},$true));if($Commands.Count-ne2-or$Literal.Count-ne2-or$Or.Count-ne1-or$Paren.Count-ne2){throw 'canonical semantic shape rejected'};foreach($Command in @($Ast.FindAll({param($N)$N-is[Management.Automation.Language.CommandAst]},$true))){$Parameters=@($Command.CommandElements|Where-Object{$_-is[Management.Automation.Language.CommandParameterAst]}|ForEach-Object{$_.ParameterName});if(@($Parameters|Group-Object|Where-Object{$_.Count -gt 1}).Count-ne0){throw 'duplicate named parameter rejected'}}}
$CS=@($CA.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'Start'},$true));$SS=@($SA.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'Start'},$true));if($CS.Count-ne1-or$SS.Count-ne0){throw 'start topology rejected'}
$ArgvLine="foreach (`$Argument in @('-NoLogo','-NoProfile','-NonInteractive','-File',`$Stage0Path)) { [void]`$StartInfo.ArgumentList.Add([string]`$Argument) }";if(([regex]::Matches($CT,[regex]::Escape($ArgvLine))).Count-ne1-or([regex]::Matches($CT,'ArgumentList\.Add\(')).Count-ne1-or([regex]::Matches($CT,'(?m)^\s*\$StartInfo\.RedirectStandard(Input|Output|Error) = \$true\s*$')).Count-ne3-or([regex]::Matches($CT,'\$Process\.StandardInput\.Close\(\)')).Count-ne1-or([regex]::Matches($CT,'StandardInput\.(Write|WriteLine|BaseStream)')).Count-ne0){throw 'argv/redirect/stdin topology rejected'}
$Results=@($CA.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'GetResult'},$true));if($Results.Count-ne2){throw 'task completion count rejected'};foreach($N in $Results){if($N.Parent-isnot[Management.Automation.Language.ConvertExpressionAst]-or$N.Parent.Type.TypeName.Name-cne'void'){throw 'task result not suppressed'}}
if(([regex]::Matches($CT,'\.CopyToAsync\(')).Count-ne2-or([regex]::Matches($CT,'\$Process\.WaitForExit\(120000\)')).Count-ne1-or([regex]::Matches($CT,'\$Process\.Kill\(\$true\)')).Count-ne1-or([regex]::Matches($CT,'\[Console\]::OpenStandardOutput\(\)')).Count-ne1-or([regex]::Matches($ST,'\[Console\]::OpenStandardOutput\(\)')).Count-ne1-or([regex]::Matches($CT,'\$OutputStream\.Write\(')).Count-ne1-or([regex]::Matches($ST,'\$OutputStream\.Write\(')).Count-ne1-or([regex]::Matches($CT,'\$OutputStream\.Flush\(\)')).Count-ne1-or([regex]::Matches($ST,'\$OutputStream\.Flush\(\)')).Count-ne1){throw 'raw transport topology rejected'}
foreach($Forbidden in @('Write-Output','Write-Host','Out-String','Start-Process','Invoke-Expression','-EncodedCommand','Set-Content','Out-File','nvidia-smi','OwnerAuthorizationId')){if($CT.Contains($Forbidden,[StringComparison]::OrdinalIgnoreCase)-or$ST.Contains($Forbidden,[StringComparison]::OrdinalIgnoreCase)){throw "forbidden source surface: $Forbidden"}}
$Utf8=[Text.UTF8Encoding]::new($false,$true);$Child=$Utf8.GetBytes('ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'+"`n");$Parent=$Utf8.GetBytes($Utf8.GetString($Child)+'ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'+"`n")
function Get-StaticSha([byte[]]$Bytes){$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}}
if($Child.Length-ne243-or(Get-StaticSha $Child)-cne'ba2576eeded1cdf28b9971dfa7a70dbfaa13f03337252d9497ca60548c35e12c'-or$Parent.Length-ne350-or(Get-StaticSha $Parent)-cne'909afeb0e0da474bedd4fa4489eb23ced9eb816d8bf049471d4f37bf81ec7e96'){throw 'raw byte contract rejected'}
'ENTRYV13_OUTPUT_CONTRACT_GREEN_PASS|preflight=semantic_or|child=raw_utf8_lf|parent=raw_utf8_lf|task_results=suppressed|parsers=2|starts=0'
```

Immediately after GREEN, run this independent preservation check. Any
difference preserves both v13 files and stops before Task 3.

```powershell
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract';$CanonicalRoot='<repo>';$V13=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery';$V11=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery'
$Expected12=[ordered]@{'task-1-stage0-plan-identity-controller-v13.ps1'=@(31491,'dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086');'task-1-stage0-v13.ps1'=@(24403,'18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967')};$Expected11=[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')}
foreach($Pair in @(@($V13,$Expected12),@($V11,$Expected11))){$Root=[string]$Pair[0];$Expected=[Collections.IDictionary]$Pair[1];$Items=@(Get-ChildItem -LiteralPath $Root -Force);if($Items.Count-ne$Expected.Count-or@($Items|Where-Object PSIsContainer).Count-ne0){throw 'GREEN preservation inventory rejected'};foreach($Name in $Expected.Keys){$Path=Join-Path $Root $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$Expected[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Expected[$Name][1]){throw 'GREEN preservation identity rejected'}}}
Set-Location -LiteralPath $RepositoryRoot;if(@(git status --porcelain=v1 --untracked-files=all).Count-ne0-or@(git diff --cached --name-only).Count-ne0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0){throw 'GREEN preservation Git rejected'}
'ENTRYV13_PREINVOCATION_PRESERVATION_PASS|v13_files=2|v11_files=2|starts=0|linked=clean|canonical=clean'
```

### Task 3: Single-use Stage 0 observation and final closure

**Files:**
- Execute once: `.superpowers/sdd/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery/task-1-stage0-plan-identity-controller-v13.ps1`
- Read: both v13 files, v11/v10/predecessor evidence, design, and plan

**Interfaces:**
- Consumes: exact Task 1 materialization and Task 2 RED/GREEN terminals.
- Produces: exact two-line v13 controller stdout plus final closed milestone, or the first preserved NO_GO.

- [ ] **Step 1: Print and recheck the frozen invocation boundary**

Without starting Windows PowerShell again, require both canonical source hashes,
both current-parser error counts zero, the corrected semantic condition shape,
one controller start site, zero Stage 0 start sites, and two suppressed task
results. Then print the exact boundary. Any difference stops before invocation.

```powershell
$Utf8=[Text.UTF8Encoding]::new($false,$true)
$Workspace='<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery';$Expected=[ordered]@{'task-1-stage0-plan-identity-controller-v13.ps1'=@(31491,'dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086');'task-1-stage0-v13.ps1'=@(24403,'18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967')}
$Exe='C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe';if((Get-Item -LiteralPath $Exe).Length-ne301368-or(Get-FileHash -LiteralPath $Exe -Algorithm SHA256).Hash.ToLowerInvariant()-cne'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'){throw 'boundary executable rejected'}
$Asts=[ordered]@{};foreach($Name in $Expected.Keys){$Path=Join-Path $Workspace $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$Expected[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Expected[$Name][1]){throw 'boundary source identity rejected'};$T=$null;$E=$null;$Ast=[Management.Automation.Language.Parser]::ParseFile($Path,[ref]$T,[ref]$E);if(@($E).Count-ne0){throw 'boundary parser rejected'};$Asts[$Name]=$Ast}
foreach($Name in $Asts.Keys){$Ast=$Asts[$Name];$Target=@($Ast.FindAll({param($N)$N-is[Management.Automation.Language.IfStatementAst]-and$N.Clauses.Count-eq1-and$N.Clauses[0].Item1.Extent.Text.Contains('$V8Workspace',[StringComparison]::Ordinal)-and$N.Clauses[0].Item1.Extent.Text.Contains('$ConsumedV6Workspace',[StringComparison]::Ordinal)},$true));if($Target.Count-ne1){throw 'boundary semantic target rejected'};$Condition=$Target[0].Clauses[0].Item1;$Commands=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.CommandAst]},$true));$Literal=@($Commands|ForEach-Object{$_.CommandElements}|Where-Object{$_-is[Management.Automation.Language.CommandParameterAst]-and$_.ParameterName-ceq'LiteralPath'});$Or=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Or},$true));$Paren=@($Condition.FindAll({param($N)$N-is[Management.Automation.Language.ParenExpressionAst]},$true));if($Commands.Count-ne2-or$Literal.Count-ne2-or$Or.Count-ne1-or$Paren.Count-ne2){throw 'boundary semantic shape rejected'}}
$ControllerAst=$Asts['task-1-stage0-plan-identity-controller-v13.ps1'];$Stage0Ast=$Asts['task-1-stage0-v13.ps1'];$ControllerStarts=@($ControllerAst.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'Start'},$true));$Stage0Starts=@($Stage0Ast.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'Start'},$true));$Results=@($ControllerAst.FindAll({param($N)$N-is[Management.Automation.Language.InvokeMemberExpressionAst]-and$N.Member.Value-eq'GetResult'},$true));if($ControllerStarts.Count-ne1-or$Stage0Starts.Count-ne0-or$Results.Count-ne2){throw 'boundary process topology rejected'};foreach($N in $Results){if($N.Parent-isnot[Management.Automation.Language.ConvertExpressionAst]-or$N.Parent.Type.TypeName.Name-cne'void'){throw 'boundary task suppression rejected'}}
$Child=$Utf8.GetBytes('ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean'+"`n")
$Parent=$Utf8.GetBytes($Utf8.GetString($Child)+'ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0'+"`n")
function Get-BoundarySha([byte[]]$Bytes){$A=[Security.Cryptography.SHA256]::Create();try{[BitConverter]::ToString($A.ComputeHash($Bytes)).Replace('-','').ToLowerInvariant()}finally{$A.Dispose()}}
if($Child.Length-ne243-or(Get-BoundarySha $Child)-cne'ba2576eeded1cdf28b9971dfa7a70dbfaa13f03337252d9497ca60548c35e12c'-or$Parent.Length-ne350-or(Get-BoundarySha $Parent)-cne'909afeb0e0da474bedd4fa4489eb23ced9eb816d8bf049471d4f37bf81ec7e96'){throw 'boundary byte contract rejected'}
'ENTRYV13_INVOCATION_BOUNDARY|exe=C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe|exe_bytes=301368|exe_sha256=db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f|controller=.\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery\task-1-stage0-plan-identity-controller-v13.ps1|controller_bytes=31491|controller_sha256=dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086|child=task-1-stage0-v13.ps1|child_source_bytes=24403|child_source_sha256=18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967|argv=-NoLogo,-NoProfile,-NonInteractive,-File,<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery\task-1-stage0-v13.ps1|child_bytes=243|child_sha256=ba2576eeded1cdf28b9971dfa7a70dbfaa13f03337252d9497ca60548c35e12c|parent_bytes=350|parent_sha256=909afeb0e0da474bedd4fa4489eb23ced9eb816d8bf049471d4f37bf81ec7e96|files=2|starts=0'
```

The plan-pinned expected values are child bytes `218`, child SHA-256
`ba2576eeded1cdf28b9971dfa7a70dbfaa13f03337252d9497ca60548c35e12c`,
parent bytes `325`, and parent SHA-256
`909afeb0e0da474bedd4fa4489eb23ced9eb816d8bf049471d4f37bf81ec7e96`.

- [ ] **Step 2: Invoke the controller exactly once**

From the linked repository in the exact current PowerShell 7.6.4 Core shell, run only:

```powershell
& '.\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery\task-1-stage0-plan-identity-controller-v13.ps1'
```

The invocation is consumed when issued. A successful child `Process.Start()` consumes Stage 0. Never invoke either source again.

Require exit zero, empty stderr, no additional output, and exact parent-visible raw stdout:

```text
ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

Both lines end in LF. Any controller uncertainty before child start is `ENTRYV13_PREFLIGHT_CONTROLLER_UNPROVABLE / NO_GO`. Any child start followed by timeout, disconnect, incomplete capture, exit, stdout, stderr, identity, or side-effect difference is `ENTRYV13_STAGE0_UNPROVABLE / NO_GO`. Preserve everything and stop.

- [ ] **Step 3: Run the final read-only closure once**

Require exact design/plan commits and blobs; two-file v13 identities and
inventory; all shadows absent; immutable v11 two-file NO_GO with controller
invocations one and child starts zero; exact inherited predecessors and runtime
files; unchanged HEAD/branch; clean linked/canonical worktrees; empty staging;
no unexpected object; v13 controller invocations one; v13 child starts one;
retries zero; and every prohibited action zero.

```powershell
$RepositoryRoot='<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot='<repo>'
$Workspace=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$V12Workspace=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery'
if(Test-Path -LiteralPath $V12Workspace){throw 'closure preserved v12 namespace exists'}
Set-Location -LiteralPath $RepositoryRoot
$Head=git rev-parse HEAD;$PlanPath='docs/superpowers/plans/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md';$DesignPath='docs/superpowers/specs/2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md'
if($Head-notmatch'\A[0-9a-f]{40}\z'-or(git rev-list --parents -n 1 HEAD)-cne"$Head 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa"-or(git rev-parse "HEAD:$DesignPath")-cne'eb0260c4137cfc29bcefc3b410eb19cb88262a8c'-or(git hash-object -- $PlanPath)-cne(git rev-parse "HEAD:$PlanPath")){throw 'closure lineage/blob rejected'}
if((git show -s --format='%an|%ae|%cn|%ce|%s' HEAD)-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery'){throw 'closure commit identity rejected'}
if((git rev-list --parents -n 1 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa)-cne'84b0f64fa5565d785e32fe3fbe5de1dc473f23aa 97acd06f61fdac5df11e3a8fb21b641101b9f482'-or(git show -s --format='%an|%ae|%cn|%ce|%s' 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa)-cne'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: design A11 frozen source plan identity recovery'){throw 'closure design identity rejected'}
$PlanChanged=@(git diff-tree --no-commit-id --name-only -r HEAD);$DesignChanged=@(git diff-tree --no-commit-id --name-only -r 84b0f64fa5565d785e32fe3fbe5de1dc473f23aa);if($PlanChanged.Count-ne1-or$PlanChanged[0]-cne$PlanPath-or$DesignChanged.Count-ne1-or$DesignChanged[0]-cne$DesignPath){throw 'closure changed path rejected'}
if((git branch --show-current)-cne'codex/wave0-model-contract'-or@(git status --porcelain=v1 --untracked-files=all).Count-ne0-or@(git diff --cached --name-only).Count-ne0-or@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count-ne0){throw 'closure Git rejected'}
$Children=@(Get-ChildItem -LiteralPath $Workspace -Force|Sort-Object Name)
if($Children.Count-ne2-or@($Children|Where-Object PSIsContainer).Count-ne0){throw 'closure inventory rejected'}
$Expected=[ordered]@{'task-1-stage0-plan-identity-controller-v13.ps1'=@(31491,'dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086');'task-1-stage0-v13.ps1'=@(24403,'18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967')};foreach($Name in $Expected.Keys){$Path=Join-Path $Workspace $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$Expected[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Expected[$Name][1]){throw 'closure source identity rejected'}}
$V11=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery';$V11Expected=[ordered]@{'task-1-stage0-raw-byte-controller-v11.ps1'=@(28071,'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9');'task-1-stage0-v11.ps1'=@(21104,'c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa')};$V11Children=@(Get-ChildItem -LiteralPath $V11 -Force);if($V11Children.Count-ne2-or@($V11Children|Where-Object PSIsContainer).Count-ne0){throw 'closure v11 inventory rejected'};foreach($Name in $V11Expected.Keys){$Path=Join-Path $V11 $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$V11Expected[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$V11Expected[$Name][1]){throw 'closure v11 identity rejected'}}
$V10=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery';$V10Expected=[ordered]@{'task-0-patch-root-binding-v10.txt'=@(1058,'d3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5');'task-1-stage0-transport-controller-v10.ps1'=@(22802,'2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e');'task-1-stage0-v10.ps1'=@(25072,'5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa')};$V10Children=@(Get-ChildItem -LiteralPath $V10 -Force);if($V10Children.Count-ne3-or@($V10Children|Where-Object PSIsContainer).Count-ne0){throw 'closure v10 inventory rejected'};foreach($Name in $V10Expected.Keys){$Path=Join-Path $V10 $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$V10Expected[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$V10Expected[$Name][1]){throw 'closure v10 identity rejected'}}
$PlanText=[IO.File]::ReadAllText((Join-Path $RepositoryRoot $PlanPath),[Text.UTF8Encoding]::new($false,$true));$V12Incident='PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO';if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V12Incident}).Count-ne1){throw 'v12 incident record rejected'};$V11Incident='PRESERVED_V11_INCIDENT|plan_commit=30735e992d8670991beb0c2882b8f225ff89d978|controller_invocations=1|child_starts=0|phase=controller_preflight|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191|terminal=ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO';$V10Incident='PRESERVED_V10_INCIDENT|plan_commit=0997117b53cca977e232e44eeda85e426a4e9328|controller_starts=1|child_starts=1|child_exit=0|child_stderr_bytes=0|fault=child_stdout_bytes_rejected|terminal=ENTRYV10_STAGE0_UNPROVABLE / NO_GO';if(@($PlanText.Split([char]10)|Where-Object{$_-ceq$V11Incident}).Count-ne1-or@($PlanText.Split([char]10)|Where-Object{$_-ceq$V10Incident}).Count-ne1){throw 'closure incident record rejected'}
$V11Controller=Join-Path $V11 'task-1-stage0-raw-byte-controller-v11.ps1';$V11Lines=[IO.File]::ReadAllText($V11Controller,[Text.UTF8Encoding]::new($false,$true)).Split([char]10);$V11Line="if (Test-Path -LiteralPath `$V8Workspace -or Test-Path -LiteralPath `$ConsumedV6Workspace) { throw 'consumed predecessor namespace exists' }";if($V11Lines.Count-lt171-or$V11Lines[170]-cne$V11Line){throw 'closure v11 source line rejected'}
$Tokens=$null;$Errors=$null;$V11Ast=[Management.Automation.Language.Parser]::ParseFile($V11Controller,[ref]$Tokens,[ref]$Errors);$V11If=@($V11Ast.FindAll({param($N)$N-is[Management.Automation.Language.IfStatementAst]-and$N.Extent.StartLineNumber-eq171},$true));if(@($Errors).Count-ne0-or$V11If.Count-ne1){throw 'closure v11 parser surface rejected'};$V11Commands=@($V11If[0].FindAll({param($N)$N-is[Management.Automation.Language.CommandAst]},$true));$V11Literal=@($V11Commands|ForEach-Object{$_.CommandElements}|Where-Object{$_-is[Management.Automation.Language.CommandParameterAst]-and$_.ParameterName-ceq'LiteralPath'});$V11Or=@($V11If[0].FindAll({param($N)$N-is[Management.Automation.Language.BinaryExpressionAst]-and$N.Operator-eq[Management.Automation.Language.TokenKind]::Or},$true));if($V11Commands.Count-ne1-or$V11Literal.Count-ne2-or$V11Or.Count-ne0){throw 'closure v11 semantic evidence rejected'}
$Message='Cannot bind parameter because parameter ''LiteralPath'' is specified more than once. To provide multiple values to parameters that can accept multiple values, use the array syntax. For example, "-parameter value1,value2,value3".';$MessageBytes=[Text.UTF8Encoding]::new($false,$true).GetBytes($Message);$ShaObject=[Security.Cryptography.SHA256]::Create();try{$MessageSha=[BitConverter]::ToString($ShaObject.ComputeHash($MessageBytes)).Replace('-','').ToLowerInvariant()}finally{$ShaObject.Dispose()};if($MessageSha-cne'7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191'){throw 'closure v11 exception digest rejected'}
$ExternalV9='<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery';$V9Expected=[ordered]@{'task-1-stage0-transport-controller-v9.ps1'=@(17994,'795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff');'task-1-stage0-v9.ps1'=@(20258,'34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3')};$V7=Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery';$V7Expected=[ordered]@{'task-1-stage0-audit-v7.ps1'=@(3849,'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b');'task-1-scalar-identity-tests-v7.ps1'=@(8849,'977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9');'task-1-scalar-identity-red-v7.psm1'=@(991,'34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919');'task-1-scalar-identity-green-v7.psm1'=@(2553,'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')}
foreach($Pair in @(@($ExternalV9,$V9Expected),@($V7,$V7Expected))){$Root=[string]$Pair[0];$Map=[Collections.IDictionary]$Pair[1];$Items=@(Get-ChildItem -LiteralPath $Root -Force);if($Items.Count-ne$Map.Count-or@($Items|Where-Object PSIsContainer).Count-ne0){throw 'closure inherited inventory rejected'};foreach($Name in $Map.Keys){$Path=Join-Path $Root $Name;if((Get-Item -LiteralPath $Path).Length-ne[long]$Map[$Name][0]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Map[$Name][1]){throw 'closure inherited identity rejected'}}}
$RequiredAbsent=@((Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'),(Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery'));foreach($Path in $RequiredAbsent){if(Test-Path -LiteralPath $Path){throw 'closure inherited absence rejected'}}
$Runtime=@(@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe',301368,'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'),@('C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',454656,'7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'),@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',15463,'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a'),@('C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll',345952,'5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90'),@('C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1',776,'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30'),@('C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll',93696,'9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010'));foreach($Record in $Runtime){$Path=[string]$Record[0];if((Get-Item -LiteralPath $Path).Length-ne[long]$Record[1]-or(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne[string]$Record[2]){throw 'closure runtime/provider identity rejected'}}
$RuntimeEvidence=@(
    @($Runtime[0][0],'None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[1][0],'HardLink','10.0.26100.8875 (WinBuild.160101.0800)','10.0.26100.8875','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'),
    @($Runtime[2][0],'None','','','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','AB172913A2960A224809EE8A0C371CD47A079B72'),
    @($Runtime[3][0],'None','7.6.4.500','7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d','CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'),
    @($Runtime[4][0],'HardLink','','','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF'),
    @($Runtime[5][0],'HardLink','10.0.26100.1','10.0.26100.1','CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US','71F53A26BB1625E466727183409A30D03D7923DF')
)
foreach($Record in $RuntimeEvidence){$Item=Get-Item -LiteralPath $Record[0] -Force;$Link=if([string]::IsNullOrEmpty([string]$Item.LinkType)){'None'}else{[string]$Item.LinkType};$Streams=@(Get-Item -LiteralPath $Record[0] -Stream * -ErrorAction Stop);if($Link-cne[string]$Record[1]-or$Streams.Count-ne1-or[string]$Streams[0].Stream-cne':$DATA'-or($Record[2]-and[string]$Item.VersionInfo.FileVersion-cne[string]$Record[2])-or($Record[3]-and[string]$Item.VersionInfo.ProductVersion-cne[string]$Record[3])){throw 'closure runtime/provider metadata rejected'}}
$CurrentProcessPath=[IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName);if(-not[StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath,[string]$Runtime[0][0])-or$PSVersionTable.PSVersion.ToString()-cne'7.6.4'-or$PSVersionTable.PSEdition-cne'Core'){throw 'closure runtime provenance rejected'}
$SecurityModule=Import-Module -Name $Runtime[2][0] -Force -PassThru -ErrorAction Stop
try{if(@($SecurityModule).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.Path)-cne[string]$Runtime[2][0]-or@($SecurityModule.NestedModules).Count-ne1-or[IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path)-cne[string]$Runtime[3][0]){throw 'closure Security provider rejected'};$AuthCommand=Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop;if(@($AuthCommand).Count-ne1-or[IO.Path]::GetFullPath([string]$AuthCommand.Module.Path)-cne[string]$Runtime[2][0]-or[IO.Path]::GetFullPath([string]$AuthCommand.DLL)-cne[string]$Runtime[3][0]){throw 'closure Authenticode provenance rejected'};foreach($Record in $RuntimeEvidence){$Signature=Get-AuthenticodeSignature -LiteralPath $Record[0];if($Signature.Status.ToString()-cne'Valid'-or$null-eq$Signature.SignerCertificate-or[string]$Signature.SignerCertificate.Subject-cne[string]$Record[4]-or-not[StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint,[string]$Record[5])){throw 'closure runtime/provider signature rejected'}}}finally{[void](Remove-Module -ModuleInfo $SecurityModule -Force)}
$Shadows=@('<workspace>\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\.worktrees\wave0-model-contract\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery','<repo>\CC_github部隊\vision-active-learning-loop\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery');foreach($Path in $Shadows){if(Test-Path -LiteralPath $Path){throw 'closure shadow rejected'}}
foreach($Name in @('machine','task-1-report.md','__pycache__','.pytest_cache','result.json','transcript.txt','repair.ps1')){if(Test-Path -LiteralPath (Join-Path $Workspace $Name)){throw 'closure forbidden object'}}
'ENTRYV13_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED'
```

## Execution stop

After Task 3, report design/plan commits and blobs, both source identities, v11 RED, v13 parser/semantic/static GREEN terminals, exact controller observation, final closure status, Git cleanliness, and all unexecuted downstream/runtime categories. Do not start another design, plan, implementation, controller, child, parser/scalar phase, or runtime without a new explicit owner instruction.
