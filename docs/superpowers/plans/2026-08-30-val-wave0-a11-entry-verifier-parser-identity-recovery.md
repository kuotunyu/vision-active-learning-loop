# Wave 0 A11 Entry-Verifier Parser-Identity Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the consumed v7 parser-order NO_GO, prove both parser process identities before every new syntax gate, and complete one fresh read-only v8 entry-verifier milestone that stops before child-exit recovery.

**Architecture:** A plan-pinned Stage 0 admits immutable v7, executable-file, and role-specific Security-provider evidence without starting a parser. A pure parser-runtime identity RED/GREEN contract then closes caller-label spoofing; a self-attesting worker explicitly imports its pinned Security provider before the parser-identity GREEN module, and a two-start controller uses it for three single-use dual-parser phases before a fresh scalar comparator, canonical 24-file inventory, static verifier, one formal entry, and independent closure.

**Tech Stack:** PowerShell 7.6.4 Core; Windows PowerShell 5.1 Desktop parser; exact `Microsoft.PowerShell.Security` manifests and nested DLLs; .NET `FileStream`, `SHA256`, `System.Diagnostics.Process`, `ProcessStartInfo.ArgumentList`, `System.IO.Directory.GetParent`, `StringComparer`, `JsonDocument`, `Utf8JsonWriter`, and Authenticode; Git; Markdown; ignored append-only evidence.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract` in the existing linked worktree; the worktree is not a submodule.
- This plan commit is a one-file direct child of Security-provider amendment commit `5d7500abef12ff724d0fb9c256a1894979bd8677`, which is a direct child of original design commit `0788f6143691d5a39730fb06508be3949de1b3f0`; it carries original design blob `a837d94d58d8ad2ee1c71fd51de64257fe49d060` and amendment blob `20661c3572d8723d7c52c4d745703a5f7741b8dd`.
- Plan author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with subject `docs: plan A11 entry verifier parser identity recovery`.
- Execution uses only `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/` and the `entryv8-*` namespace.
- The v8 namespace contains exactly 13 human-authored files before report creation and exactly 14 afterward; it never contains `machine/`, a cache, bytecode, a fixture, a manifest file, a transcript, a sidecar, a result file, a digest file, or a temporary file.
- All human-authored execution files are created once with `apply_patch`; consumed files are never edited, replaced, renamed, copied over, deleted, or regenerated.
- The v7 workspace remains exactly four ignored files; v7 `machine/` and `task-1-report.md` remain absent; no v7 or v2-v6 source is imported, dot-sourced, or invoked.
- Stage 0, parser-policy RED, parser-policy GREEN, each of three dual-parser phases, scalar RED, scalar GREEN, static admission, formal entry, pre-report closure, and final closure are each single-use. An uncertain or unexpected observation is a preserved NO_GO, never permission to retry.
- PowerShell 7 is exactly `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`, 301,368 bytes, SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`, engine `7.6.4`, edition `Core`, valid Microsoft signature, signer thumbprint `AB172913A2960A224809EE8A0C371CD47A079B72`, and no leaf link.
- Windows PowerShell is exactly `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`, 454,656 bytes, SHA-256 `7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5`, engine major/minor `5.1`, edition `Desktop`, file/product version `10.0.26100.8875`, valid Microsoft Windows signature, signer thumbprint `DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443`, and the sole allowed `HardLink` leaf.
- PowerShell 7 Security manifest is exactly `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1`, 15,463 bytes, SHA-256 `c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a`, GUID `A94C8C7E-9810-47C0-B8AF-65089C13A35A`, module version `7.0.0.0`, compatible edition `Core`, valid Microsoft Corporation signature, signer thumbprint `AB172913A2960A224809EE8A0C371CD47A079B72`, and no leaf link.
- PowerShell 7 Security DLL is exactly `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll`, 345,952 bytes, SHA-256 `5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90`, file version `7.6.4.500`, product version `7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d`, valid Microsoft Corporation signature, signer thumbprint `1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1`, and no leaf link.
- Windows PowerShell Security manifest is exactly `C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1`, 776 bytes, SHA-256 `fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30`, GUID `A94C8C7E-9810-47C0-B8AF-65089C13A35A`, module version `3.0.0.0`, PowerShell version `5.1`, compatible edition `Desktop`, valid Microsoft Windows signature, signer thumbprint `71F53A26BB1625E466727183409A30D03D7923DF`, and the sole allowed `HardLink` leaf.
- Windows PowerShell Security DLL is exactly `C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll`, 93,696 bytes, SHA-256 `9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010`, file/product version `10.0.26100.1`, valid Microsoft Windows signature, signer thumbprint `71F53A26BB1625E466727183409A30D03D7923DF`, and the sole allowed `HardLink` leaf.
- The Windows PowerShell HardLink exception accepts only that exact System32 identity with no `ReparsePoint`; every symbolic link, junction, alternate hard-link path, and parent-chain reparse point is rejected.
- The Security-provider HardLink exceptions accept only the exact Windows manifest and GAC DLL identities above with no `ReparsePoint`; every other provider leaf link, symbolic link, junction, alternate path, and every parent-chain reparse point is rejected.
- Before any provider import, its manifest and nested DLL are validated by pure .NET `FileStream` plus `SHA256`, exact byte count, exact link policy, and ordinary parent chain. Each worker then imports only its literal role-specific manifest, proves exact module path/GUID/version/nested DLL and `Get-AuthenticodeSignature` command provenance, makes exactly three signature calls for its own executable, provider manifest, and provider DLL, and only then imports the exact parser-identity GREEN module.
- No worker or controller uses `Get-FileHash`, auto-loading, module-path search, a fallback provider, `Microsoft.PowerShell.Utility`, reflection, P/Invoke, or `Add-Type`; `$ProgressPreference` is always `SilentlyContinue` before provider import.
- Formal parser processes are started only through those two literal absolute paths. Never use command-name lookup, PATH, alias, shim, relative path, shell command string, fallback executable, retry, sleep, or a third process start.
- No Docker, Docker Desktop, WSL, Hyper-V, GPU, `nvidia-smi`, CUDA, A11, product, model, campaign, Wave 1, network, or external runtime command is permitted.
- No `OwnerAuthorizationId` is created, consumed, inferred, incremented, synthesized, or accepted.
- No product/tracked implementation file changes. No push, merge, release, tag, amend, rebase, reset, stash, evidence deletion, or other repository change.
- Final success is exactly `ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED`; it authorizes nothing beyond this entry-verifier milestone.

## File Map

| File | Responsibility |
|---|---|
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-stage0-audit-v8.ps1` | Exact Stage 0 source and result; never executed. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-tests-v8.ps1` | RED/GREEN behavior contract for parser role binding. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-red-v8.psm1` | Intentional declared-role-trust mutation. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-green-v8.psm1` | Pure production parser-runtime identity comparator. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-worker-v8.ps1` | Self-attests one parser process and parses explicit frozen targets. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-dual-parser-controller-v8.ps1` | Starts exactly two pinned workers and accepts only attested results. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-tests-v8.ps1` | Fresh scalar identity RED/GREEN behavior contract. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-red-v8.psm1` | Fresh intentional equal-scalar rejection subject. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-green-v8.psm1` | Fresh production scalar comparator. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-preserved-inventory-v8.json` | Canonical v7 incident, runtime, 24-file, and 12-absence record. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-entry-verifier-v8.ps1` | One-shot read-only formal verifier. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-static-verifier-v8.ps1` | Parser, AST, type-flow, process-count, canonicalization, and forbidden-action gate. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-closure-verifier-v8.ps1` | Independent pre-report and final closure. |
| `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-report.md` | Immutable evidence index and first exact final terminal. |

---

### Task 1: Admit Stage 0 and prove parser-runtime identity RED to GREEN

**Files:**
- Create after exact Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-stage0-audit-v8.ps1`
- Create after exact Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-tests-v8.ps1`
- Create after exact Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-red-v8.psm1`
- Create after exact parser-policy RED: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-identity-green-v8.psm1`

**Interfaces:**
- Consumes: exact original-design/amendment/plan lineage, clean linked/canonical worktrees, absent v8 workspace, exact preserved v7 four-file NO_GO, exact two executable-file identities, and exact four Security-provider file identities.
- Produces: one immutable Stage 0 fact and `Compare-A11ParserRuntimeIdentity`, behaviorally proven to reject a caller role that contradicts the actual process identity.

- [ ] **Step 1: Execute the plan-pinned Stage 0 exactly once**

Extract the exact following LF/UTF-8 source from the committed plan blob and run it once as the frozen PowerShell 7 command body. Do not create the v8 workspace before it returns exact PASS.

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$ExpectedAmendment = '5d7500abef12ff724d0fb9c256a1894979bd8677'
$ExpectedAmendmentBlob = '20661c3572d8723d7c52c4d745703a5f7741b8dd'
$AmendmentPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-security-module-amendment-design.md'
$ExpectedDesign = '0788f6143691d5a39730fb06508be3949de1b3f0'
$ExpectedDesignBlob = 'a837d94d58d8ad2ee1c71fd51de64257fe49d060'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery.md'
$FreshWorkspace = Join-Path $RepositoryRoot '.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery'
$V7Workspace = Join-Path $RepositoryRoot '.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = Join-Path $RepositoryRoot '.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$FrozenPwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$FrozenWindowsPowerShell = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
$PwshSecurityManifest = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$PwshSecurityDll = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll'
$WindowsSecurityManifest = 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
$WindowsSecurityDll = 'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll'

$ExpectedV7 = [ordered]@{
    'task-1-stage0-audit-v7.ps1' = @([long]3849, 'ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b')
    'task-1-scalar-identity-tests-v7.ps1' = @([long]8849, '977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9')
    'task-1-scalar-identity-red-v7.psm1' = @([long]991, '34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919')
    'task-1-scalar-identity-green-v7.psm1' = @([long]2553, 'a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210')
}

function Assert-ParentChainOrdinary {
    param([Parameter(Mandatory)] [string] $Path)
    $Cursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path))
    while (-not [string]::IsNullOrEmpty($Cursor)) {
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "parent reparse point rejected: $Cursor" }
        if (-not [string]::IsNullOrEmpty([string]$Item.LinkType)) { throw "parent link rejected: $Cursor" }
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        $Cursor = $Parent.FullName
    }
}

function Get-A11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $Hasher = [Security.Cryptography.SHA256]::Create()
        try {
            $Bytes = $Hasher.ComputeHash($Stream)
            return [BitConverter]::ToString($Bytes).Replace('-', '').ToLowerInvariant()
        }
        finally {
            $Hasher.Dispose()
        }
    }
    finally {
        $Stream.Dispose()
    }
}

function Assert-FileIdentity {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [long] $ByteCount,
        [Parameter(Mandatory)] [string] $Sha256,
        [Parameter(Mandatory)] [string] $LeafLinkType,
        [string] $FileVersion = '',
        [string] $ProductVersion = ''
    )
    if (-not [IO.Path]::IsPathFullyQualified($Path)) { throw 'file path rejected' }
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path), $Path)) { throw "file canonical path rejected: $Path" }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or $Item.Length -ne $ByteCount) { throw "file bytes rejected: $Path" }
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "file reparse point rejected: $Path" }
    $ActualLinkType = if ([string]::IsNullOrEmpty([string]$Item.LinkType)) { 'None' } else { [string]$Item.LinkType }
    if (-not [StringComparer]::Ordinal.Equals($ActualLinkType, $LeafLinkType)) { throw "file link type rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals((Get-A11FileSha256 -Path $Path), $Sha256)) { throw "file hash rejected: $Path" }
    if (-not [string]::IsNullOrEmpty($FileVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.FileVersion, $FileVersion)) { throw "file version rejected: $Path" }
    if (-not [string]::IsNullOrEmpty($ProductVersion) -and -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.ProductVersion, $ProductVersion)) { throw "product version rejected: $Path" }
    Assert-ParentChainOrdinary -Path $Path
}

function Assert-SignatureIdentity {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [string] $SignerSubject,
        [Parameter(Mandatory)] [string] $SignerThumbprint
    )
    $Signature = Get-AuthenticodeSignature -LiteralPath $Path
    if ($Signature.Status.ToString() -cne 'Valid') { throw "signature rejected: $Path" }
    if ($null -eq $Signature.SignerCertificate) { throw "signer missing: $Path" }
    if (-not [StringComparer]::Ordinal.Equals($Signature.SignerCertificate.Subject, $SignerSubject)) { throw "signer subject rejected: $Path" }
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($Signature.SignerCertificate.Thumbprint, $SignerThumbprint)) { throw "signer thumbprint rejected: $Path" }
}

Push-Location -LiteralPath $RepositoryRoot
try {
    $ExpectedPlan = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $ExpectedPlan -notmatch '^[0-9a-f]{40}$') { throw 'plan commit identity rejected' }
    if ((git branch --show-current) -cne 'codex/wave0-model-contract') { throw 'branch rejected' }
    if ((git rev-list --parents -n 1 HEAD) -cne "$ExpectedPlan $ExpectedAmendment") { throw 'plan parent rejected' }
    if ((git rev-list --parents -n 1 $ExpectedAmendment) -cne "$ExpectedAmendment $ExpectedDesign") { throw 'amendment parent rejected' }
    if (-not [string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'superproject rejected' }
    $GitDir = [IO.Path]::GetFullPath((git rev-parse --git-dir))
    $GitCommon = [IO.Path]::GetFullPath((git rev-parse --git-common-dir))
    if ([StringComparer]::OrdinalIgnoreCase.Equals($GitDir, $GitCommon)) { throw 'linked-worktree isolation missing' }
    $Changed = @(git diff-tree --no-commit-id --name-only -r HEAD)
    if ($Changed.Count -ne 1 -or $Changed[0] -cne $PlanPath) { throw 'plan path rejected' }
    $Identity = git show -s --format='%an|%ae|%cn|%ce|%s' HEAD
    if ($Identity -cne 'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 entry verifier parser identity recovery') { throw 'plan identity rejected' }
    if ((git rev-parse "HEAD:$AmendmentPath") -cne $ExpectedAmendmentBlob) { throw 'amendment blob rejected' }
    if ((git rev-parse "HEAD:$DesignPath") -cne $ExpectedDesignBlob) { throw 'design blob rejected' }
    if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
    if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging not empty' }
    if (@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree dirty' }
    if (Test-Path -LiteralPath $FreshWorkspace) { throw 'fresh v8 workspace already exists' }
    if (Test-Path -LiteralPath $ConsumedV6Workspace) { throw 'consumed v6 workspace exists' }
    if (-not (Test-Path -LiteralPath $V7Workspace -PathType Container)) { throw 'v7 workspace missing' }
    if (Test-Path -LiteralPath (Join-Path $V7Workspace 'machine')) { throw 'v7 machine directory exists' }
    if (Test-Path -LiteralPath (Join-Path $V7Workspace 'task-1-report.md')) { throw 'v7 report exists' }
    $V7Children = @(Get-ChildItem -LiteralPath $V7Workspace -Force)
    if ($V7Children.Count -ne 4 -or @($V7Children | Where-Object { $_.PSIsContainer }).Count -ne 0) { throw 'v7 workspace inventory rejected' }
    foreach ($Name in $ExpectedV7.Keys) {
        $Path = Join-Path $V7Workspace $Name
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($Item.Length -ne [long]$ExpectedV7[$Name][0]) { throw "v7 bytes rejected: $Name" }
        if ((Get-A11FileSha256 -Path $Path) -cne [string]$ExpectedV7[$Name][1]) { throw "v7 hash rejected: $Name" }
    }
    Assert-FileIdentity -Path $FrozenPwsh -ByteCount 301368 -Sha256 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-FileIdentity -Path $FrozenWindowsPowerShell -ByteCount 454656 -Sha256 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.8875 (WinBuild.160101.0800)' -ProductVersion '10.0.26100.8875'
    Assert-FileIdentity -Path $PwshSecurityManifest -ByteCount 15463 -Sha256 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' -LeafLinkType 'None'
    Assert-FileIdentity -Path $PwshSecurityDll -ByteCount 345952 -Sha256 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' -LeafLinkType 'None' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
    Assert-FileIdentity -Path $WindowsSecurityManifest -ByteCount 776 -Sha256 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' -LeafLinkType 'HardLink'
    Assert-FileIdentity -Path $WindowsSecurityDll -ByteCount 93696 -Sha256 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' -LeafLinkType 'HardLink' -FileVersion '10.0.26100.1' -ProductVersion '10.0.26100.1'
    $CurrentProcessPath = [IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath, [IO.Path]::GetFullPath($FrozenPwsh))) { throw 'Stage 0 process path rejected' }
    if ($PSVersionTable.PSVersion.ToString() -cne '7.6.4' -or $PSVersionTable.PSEdition -cne 'Core') { throw 'Stage 0 process runtime rejected' }
    $SecurityModule = Import-Module -Name $PwshSecurityManifest -Force -PassThru -ErrorAction Stop
    try {
        if (@($SecurityModule).Count -ne 1) { throw 'Security module count rejected' }
        if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$SecurityModule.Path), $PwshSecurityManifest)) { throw 'Security module path rejected' }
        if ($SecurityModule.Guid.ToString().ToUpperInvariant() -cne 'A94C8C7E-9810-47C0-B8AF-65089C13A35A') { throw 'Security module GUID rejected' }
        if ($SecurityModule.Version.ToString() -cne '7.0.0.0') { throw 'Security module version rejected' }
        if (@($SecurityModule.CompatiblePSEditions).Count -ne 1 -or [string]$SecurityModule.CompatiblePSEditions[0] -cne 'Core') { throw 'Security module edition rejected' }
        if (@($SecurityModule.NestedModules).Count -ne 1 -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path), $PwshSecurityDll)) { throw 'Security nested DLL rejected' }
        $AuthCommand = Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop
        if (@($AuthCommand).Count -ne 1 -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$AuthCommand.Module.Path), $PwshSecurityManifest) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$AuthCommand.DLL), $PwshSecurityDll)) { throw 'Authenticode command provenance rejected' }
        Assert-SignatureIdentity -Path $FrozenPwsh -SignerSubject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
        Assert-SignatureIdentity -Path $FrozenWindowsPowerShell -SignerSubject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
        Assert-SignatureIdentity -Path $PwshSecurityManifest -SignerSubject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint 'AB172913A2960A224809EE8A0C371CD47A079B72'
        Assert-SignatureIdentity -Path $PwshSecurityDll -SignerSubject 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'
        Assert-SignatureIdentity -Path $WindowsSecurityManifest -SignerSubject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint '71F53A26BB1625E466727183409A30D03D7923DF'
        Assert-SignatureIdentity -Path $WindowsSecurityDll -SignerSubject 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US' -SignerThumbprint '71F53A26BB1625E466727183409A30D03D7923DF'
        'ENTRYV8_STAGE0_PASS|v7=preserved_no_go|files=4|workspace=absent|runtimes=2|providers=2|linked=clean|canonical=clean'
    }
    finally {
        Remove-Module -ModuleInfo $SecurityModule -Force -ErrorAction Stop
    }
}
finally {
    Pop-Location
}
```

Require the exact source identity frozen in the Plan Completion Gate below. Require exit 0, empty stderr, and sole stdout:

```text
ENTRYV8_STAGE0_PASS|v7=preserved_no_go|files=4|workspace=absent|runtimes=2|providers=2|linked=clean|canonical=clean
```

Any difference stops before workspace creation. Never repeat Stage 0.

- [ ] **Step 2: Create the Stage 0 audit, parser-policy test, and intentional RED with `apply_patch`**

The audit begins with the exact Stage 0 source above and ends only with comments recording its frozen byte count, SHA-256, exact executable/argv identity, exact provider import/provenance fact, exact stdout, exit 0, and zero stderr bytes. It is never executed.

The behavioral test accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $ModulePath,
    [Parameter(Mandatory)] [string] $ExpectedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

It validates one absolute, canonical, contained, ordinary, non-reparse, exact-byte/hash module using only pure .NET `FileStream` plus `SHA256`; imports only that path; requires the sole export `Compare-A11ParserRuntimeIdentity`; snapshots the v8 workspace file-name/byte/hash inventory before and after with the same .NET helper; and removes the module in `finally`.

Both expected and observed records have exactly this property order:

```text
role,process_path,powershell_version,ps_edition,executable_byte_count,executable_sha256,file_version,product_version,signature_status,signer_subject,signer_thumbprint,leaf_link_type,leaf_reparse_point,parent_chain_reparse_points
```

Use literal records for the two pinned runtimes. Normalize the Windows PowerShell engine value to exact string `5.1`; use exact string `7.6.4` for PowerShell 7. The spoof record declares `windows-powershell-5.1` but contains the PowerShell 7 process path, engine, edition, byte count, digest, versions, signer, thumbprint, and `None` leaf-link value.

The intentional RED module exports the exact public function, compares only `Expected.role` and `Observed.role`, and returns `identity_match=true` for the spoof. The RED test requires that known faulty acceptance and emits only:

```text
PARSER_IDENTITY_TEST_RED_PASS|fault=declared_role_trusted
```

Materialize `task-1-parser-identity-red-v8.psm1` from this exact complete source:

```powershell
Set-StrictMode -Version Latest

function Compare-A11ParserRuntimeIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $Expected,
        [Parameter(Mandatory)] [AllowNull()] [object] $Observed
    )

    $RoleMatch = [StringComparer]::Ordinal.Equals([string]$Expected.role, [string]$Observed.role)
    [pscustomobject][ordered]@{
        expected = $Expected
        observed = $Observed
        field_matches = [pscustomobject][ordered]@{ role = [bool]$RoleMatch }
        identity_match = [bool]$RoleMatch
    }
}

Export-ModuleMember -Function Compare-A11ParserRuntimeIdentity
```

Materialize `task-1-parser-identity-tests-v8.ps1` from this exact complete source:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $ModulePath,
    [Parameter(Mandatory)] [string] $ExpectedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Get-A11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        ([BitConverter]::ToString($Algorithm.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Stream.Dispose()
        $Algorithm.Dispose()
    }
}

function Assert-A11ParentChainOrdinary {
    param([Parameter(Mandatory)] [string] $Path)
    $Cursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path))
    while (-not [string]::IsNullOrEmpty($Cursor)) {
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$Item.LinkType)) { throw "linked parent rejected: $Cursor" }
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        $Cursor = $Parent.FullName
    }
}

function Get-A11WorkspaceSnapshot {
    param([Parameter(Mandatory)] [string] $Path)
    $Records = New-Object 'Collections.Generic.List[string]'
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force | Sort-Object -Property Name)) {
        if ($Item.PSIsContainer) { throw 'workspace directory child rejected' }
        [void]$Records.Add("$($Item.Name)|$([long]$Item.Length)|$(Get-A11FileSha256 -Path $Item.FullName)")
    }
    [string]::Join("`n", $Records)
}

function New-A11RuntimeRecord {
    param([Parameter(Mandatory)] [ValidateSet('Pwsh','Windows')] [string] $Kind)
    if ($Kind -ceq 'Pwsh') {
        return [pscustomobject][ordered]@{
            role = 'pwsh7'
            process_path = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
            powershell_version = '7.6.4'
            ps_edition = 'Core'
            executable_byte_count = [long]301368
            executable_sha256 = 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'
            file_version = '7.6.4.500'
            product_version = '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
            signature_status = 'Valid'
            signer_subject = 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
            signer_thumbprint = 'AB172913A2960A224809EE8A0C371CD47A079B72'
            leaf_link_type = 'None'
            leaf_reparse_point = [bool]$false
            parent_chain_reparse_points = [long]0
        }
    }
    [pscustomobject][ordered]@{
        role = 'windows-powershell-5.1'
        process_path = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        powershell_version = '5.1'
        ps_edition = 'Desktop'
        executable_byte_count = [long]454656
        executable_sha256 = '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'
        file_version = '10.0.26100.8875 (WinBuild.160101.0800)'
        product_version = '10.0.26100.8875'
        signature_status = 'Valid'
        signer_subject = 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
        signer_thumbprint = 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
        leaf_link_type = 'HardLink'
        leaf_reparse_point = [bool]$false
        parent_chain_reparse_points = [long]0
    }
}

function Assert-A11IdentityTrue {
    param([Parameter(Mandatory)] [object] $Record)
    if ($Record.identity_match.GetType() -ne [bool] -or -not [bool]$Record.identity_match) { throw 'identity true rejected' }
}

function Assert-A11IdentityFalse {
    param([Parameter(Mandatory)] [object] $Record)
    if ($Record.identity_match.GetType() -ne [bool] -or [bool]$Record.identity_match) { throw 'identity false rejected' }
}

function Assert-A11Throws {
    param([Parameter(Mandatory)] [scriptblock] $Action)
    $Threw = $false
    try { [void](& $Action) } catch { $Threw = $true }
    if (-not $Threw) { throw 'expected rejection missing' }
}

$CanonicalWorkspace = [IO.Path]::GetFullPath($WorkspacePath)
$CanonicalModule = [IO.Path]::GetFullPath($ModulePath)
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($CanonicalModule, [IO.Path]::GetFullPath($ExpectedModulePath))) { throw 'module path rejected' }
$WorkspacePrefix = $CanonicalWorkspace.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if (-not $CanonicalModule.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'module containment rejected' }
$ModuleItem = Get-Item -LiteralPath $CanonicalModule -Force -ErrorAction Stop
if ($ModuleItem.PSIsContainer -or [long]$ModuleItem.Length -ne $ExpectedModuleByteCount) { throw 'module bytes rejected' }
if (($ModuleItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$ModuleItem.LinkType)) { throw 'module link rejected' }
Assert-A11ParentChainOrdinary -Path $CanonicalModule
if (-not [StringComparer]::Ordinal.Equals((Get-A11FileSha256 -Path $CanonicalModule), $ExpectedModuleSha256)) { throw 'module digest rejected' }
$Before = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
$Terminal = ''
$Imported = Import-Module -Name $CanonicalModule -Force -PassThru -ErrorAction Stop
try {
    if (@($Imported).Count -ne 1) { throw 'module count rejected' }
    $Exports = @(Get-Command -Module $Imported.Name -ErrorAction Stop)
    if ($Exports.Count -ne 1 -or $Exports[0].Name -cne 'Compare-A11ParserRuntimeIdentity') { throw 'module export rejected' }
    $ExpectedPwsh = New-A11RuntimeRecord -Kind Pwsh
    $ExpectedWindows = New-A11RuntimeRecord -Kind Windows
    if ($Mode -ceq 'Red') {
        $Spoof = New-A11RuntimeRecord -Kind Pwsh
        $Spoof.role = 'windows-powershell-5.1'
        Assert-A11IdentityTrue -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed $Spoof)
        $Terminal = 'PARSER_IDENTITY_TEST_RED_PASS|fault=declared_role_trusted'
    }
    else {
        Assert-A11IdentityTrue -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedPwsh -Observed (New-A11RuntimeRecord -Kind Pwsh))
        Assert-A11IdentityTrue -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed (New-A11RuntimeRecord -Kind Windows))

        $Spoof = New-A11RuntimeRecord -Kind Pwsh
        $Spoof.role = 'windows-powershell-5.1'
        Assert-A11IdentityFalse -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed $Spoof)
        $ReverseSpoof = New-A11RuntimeRecord -Kind Windows
        $ReverseSpoof.role = 'pwsh7'
        Assert-A11IdentityFalse -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedPwsh -Observed $ReverseSpoof)

        foreach ($Mutation in @(
            @('process_path','C:\Windows\System32\WindowsPowerShell\v1.0\powershell-copy.exe'),
            @('powershell_version','5.2'),
            @('ps_edition','Core')
        )) {
            $Observed = New-A11RuntimeRecord -Kind Windows
            $Observed.($Mutation[0]) = [string]$Mutation[1]
            Assert-A11IdentityFalse -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed $Observed)
        }

        foreach ($Mutation in @(
            @('executable_byte_count',[long]454657),
            @('executable_sha256','8600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'),
            @('file_version','10.0.26100.8876 (WinBuild.160101.0800)'),
            @('product_version','10.0.26100.8876'),
            @('signature_status','UnknownError'),
            @('signer_subject','CN=Unexpected'),
            @('signer_thumbprint','CC91E564D5BC1E3A8E02D6A8508682ABEA8A2443')
        )) {
            $Observed = New-A11RuntimeRecord -Kind Windows
            $Observed.($Mutation[0]) = $Mutation[1]
            Assert-A11IdentityFalse -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed $Observed)
        }

        foreach ($Mutation in @(
            @('leaf_link_type','None'),
            @('leaf_reparse_point',[bool]$true),
            @('parent_chain_reparse_points',[long]1)
        )) {
            $Observed = New-A11RuntimeRecord -Kind Windows
            $Observed.($Mutation[0]) = $Mutation[1]
            Assert-A11IdentityFalse -Record (Compare-A11ParserRuntimeIdentity -Expected $ExpectedWindows -Observed $Observed)
        }

        Assert-A11Throws -Action { Compare-A11ParserRuntimeIdentity -Expected $null -Observed $ExpectedPwsh }
        Assert-A11Throws -Action { Compare-A11ParserRuntimeIdentity -Expected @($ExpectedPwsh) -Observed $ExpectedPwsh }
        $Missing = New-A11RuntimeRecord -Kind Pwsh
        $Missing.PSObject.Properties.Remove('ps_edition')
        Assert-A11Throws -Action { Compare-A11ParserRuntimeIdentity -Expected $ExpectedPwsh -Observed $Missing }
        $WrongType = New-A11RuntimeRecord -Kind Pwsh
        $WrongType.executable_byte_count = '301368'
        Assert-A11Throws -Action { Compare-A11ParserRuntimeIdentity -Expected $ExpectedPwsh -Observed $WrongType }

        $Closure = Compare-A11ParserRuntimeIdentity -Expected $ExpectedPwsh -Observed (New-A11RuntimeRecord -Kind Pwsh)
        $ResultOrder = @('expected','observed','field_matches','identity_match')
        $FieldOrder = @('role','process_path','powershell_version','ps_edition','executable_byte_count','executable_sha256','file_version','product_version','signature_status','signer_subject','signer_thumbprint','leaf_link_type','leaf_reparse_point','parent_chain_reparse_points')
        if (-not [StringComparer]::Ordinal.Equals([string]::Join("`n", @($Closure.PSObject.Properties.Name)), [string]::Join("`n", $ResultOrder))) { throw 'result order rejected' }
        if (-not [StringComparer]::Ordinal.Equals([string]::Join("`n", @($Closure.field_matches.PSObject.Properties.Name)), [string]::Join("`n", $FieldOrder))) { throw 'field order rejected' }
        foreach ($Property in $Closure.field_matches.PSObject.Properties) {
            if ($Property.Value.GetType() -ne [bool]) { throw 'field match type rejected' }
        }
        Assert-A11IdentityTrue -Record $Closure
        $Terminal = 'PARSER_IDENTITY_TEST_GREEN_PASS|cases=8|roles=bound|labels=untrusted'
    }
}
finally {
    Remove-Module -ModuleInfo $Imported -Force -ErrorAction Stop
}
$After = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
if (-not [StringComparer]::Ordinal.Equals($Before, $After)) { throw 'workspace changed' }
$Terminal
```

- [ ] **Step 3: Run parser-policy RED exactly once**

Before execution, prove the materialized audit/test/RED bytes equal the exact plan-pinned source-block identities, parse them under frozen PowerShell 7, and statically require one exact comparator-module import, one export, pure .NET hashing, and no write, process start, `Get-FileHash`, dynamic evaluation, shell string, redirection, Git mutation, predecessor path, Docker/GPU/A11/product/network/external-runtime action, unapproved runtime path, or `machine/` path. The plan-pinned parser executable paths and parser-runtime identity names are the only runtime-named exceptions.

Run the test in `Red` mode once through the frozen absolute PowerShell 7 executable. Require exit 0, empty stderr, unchanged three-file workspace inventory, and sole stdout:

```text
PARSER_IDENTITY_TEST_RED_PASS|fault=declared_role_trusted
```

Any difference is `ENTRYV8_PARSER_IDENTITY_UNPROVABLE / NO_GO`; preserve and stop. Never edit or rerun the RED subject, test, or invocation.

- [ ] **Step 4: Create the minimal GREEN parser-runtime identity comparator**

Create the GREEN module with `apply_patch`. It contains only strict mode, this exported function, and the final `Export-ModuleMember`:

```powershell
Set-StrictMode -Version Latest

function Compare-A11ParserRuntimeIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $Expected,
        [Parameter(Mandatory)] [AllowNull()] [object] $Observed
    )

    $PropertyOrder = @('role','process_path','powershell_version','ps_edition','executable_byte_count','executable_sha256','file_version','product_version','signature_status','signer_subject','signer_thumbprint','leaf_link_type','leaf_reparse_point','parent_chain_reparse_points')
    foreach ($Record in @($Expected, $Observed)) {
        if ($null -eq $Record -or $Record -is [array]) { throw 'runtime identity record rejected' }
        $Names = @($Record.PSObject.Properties.Name)
        if ($Names.Count -ne $PropertyOrder.Count -or -not [StringComparer]::Ordinal.Equals([string]::Join("`n", $Names), [string]::Join("`n", $PropertyOrder))) { throw 'runtime identity property order rejected' }
        foreach ($Name in $PropertyOrder) {
            if ($null -eq $Record.$Name -or $Record.$Name -is [array]) { throw "runtime identity value rejected: $Name" }
        }
        foreach ($Name in @('role','process_path','powershell_version','ps_edition','executable_sha256','file_version','product_version','signature_status','signer_subject','signer_thumbprint','leaf_link_type')) {
            if ($Record.$Name.GetType() -ne [string]) { throw "runtime identity string type rejected: $Name" }
        }
        if ($Record.executable_byte_count.GetType() -ne [long] -or [long]$Record.executable_byte_count -lt 0) { throw 'runtime identity byte count rejected' }
        if ($Record.leaf_reparse_point.GetType() -ne [bool]) { throw 'runtime identity leaf reparse type rejected' }
        if ($Record.parent_chain_reparse_points.GetType() -ne [long] -or [long]$Record.parent_chain_reparse_points -lt 0) { throw 'runtime identity parent count rejected' }
        if (-not [regex]::IsMatch([string]$Record.executable_sha256, '\A[0-9a-f]{64}\z', [Text.RegularExpressions.RegexOptions]::CultureInvariant)) { throw 'runtime identity digest rejected' }
        if (-not [IO.Path]::IsPathFullyQualified([string]$Record.process_path)) { throw 'runtime identity process path rejected' }
    }

    if ($Expected.role -notin @('pwsh7','windows-powershell-5.1') -or $Observed.role -notin @('pwsh7','windows-powershell-5.1')) { throw 'runtime identity role rejected' }
    foreach ($Record in @($Expected, $Observed)) {
        $CanonicalProcessPath = [IO.Path]::GetFullPath([string]$Record.process_path)
        if (-not [StringComparer]::OrdinalIgnoreCase.Equals($CanonicalProcessPath, [string]$Record.process_path)) { throw 'runtime identity canonical process path rejected' }
    }
    $Matches = [ordered]@{}
    foreach ($Name in $PropertyOrder) {
        if ($Name -eq 'executable_byte_count' -or $Name -eq 'parent_chain_reparse_points') {
            $Matches[$Name] = ([long]$Expected.$Name -eq [long]$Observed.$Name)
        }
        elseif ($Name -eq 'leaf_reparse_point') {
            $Matches[$Name] = ([bool]$Expected.$Name -eq [bool]$Observed.$Name)
        }
        elseif ($Name -eq 'process_path') {
            $Matches[$Name] = [StringComparer]::OrdinalIgnoreCase.Equals([string]$Expected.$Name, [string]$Observed.$Name)
        }
        else {
            $Matches[$Name] = [StringComparer]::Ordinal.Equals([string]$Expected.$Name, [string]$Observed.$Name)
        }
    }
    [pscustomobject][ordered]@{
        expected = $Expected
        observed = $Observed
        field_matches = [pscustomobject]$Matches
        identity_match = [bool](-not ($Matches.Values -contains $false))
    }
}

Export-ModuleMember -Function Compare-A11ParserRuntimeIdentity
```

The static gate must additionally reject use of display-string interpolation or collection truthiness for final identity. The implementation above is permitted to inspect the closed Boolean `$Matches.Values` only after every scalar field match is materialized; no digest or path value may flow through `-contains`.

- [ ] **Step 5: Run parser-policy GREEN exactly once**

Parse the frozen test and GREEN module through frozen PowerShell 7 and compare their exact plan-pinned source identities. Run `Green` once. The test performs the eight literal categories from the design and requires exact closed output/property/runtime types. Require exit 0, empty stderr, unchanged four-file inventory, and sole stdout:

```text
PARSER_IDENTITY_TEST_GREEN_PASS|cases=8|roles=bound|labels=untrusted
```

Any difference is `ENTRYV8_PARSER_IDENTITY_UNPROVABLE / NO_GO`; freeze all four files and stop without worker/controller creation.

---

### Task 2: Prove the dual-parser control and fresh scalar comparator

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-parser-worker-v8.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-dual-parser-controller-v8.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-tests-v8.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-red-v8.psm1`
- Create after exact scalar RED: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-scalar-identity-green-v8.psm1`

**Interfaces:**
- Consumes: frozen parser-policy GREEN module, four-file Task 1 inventory, the two pinned executables, and both role-specific pinned Security providers.
- Produces: three independently consumed dual-parser facts with provider provenance and a fresh `Compare-A11ScalarIdentity` module proven against the approved eight scalar cases.

- [ ] **Step 1: Create the worker, controller, scalar test, and intentional scalar RED**

Use `apply_patch` once per human-authored file. The worker accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Pwsh7','WindowsPowerShell51')] [string] $Role,
    [Parameter(Mandatory)] [string] $IdentityModulePath,
    [Parameter(Mandatory)] [long] $IdentityModuleByteCount,
    [Parameter(Mandatory)] [string] $IdentityModuleSha256,
    [Parameter(Mandatory)] [string] $TargetManifestBase64,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

`TargetManifestBase64` decodes strict UTF-8 without BOM to LF-separated records `absolute_path|decimal_int64_byte_count|lowercase_sha256`. Reject empty, duplicate, unsorted, malformed, escaping, linked, wrong-kind, wrong-byte, or wrong-hash targets before parsing. Every target and workspace hash uses the closed pure-.NET helper; `Get-FileHash` is forbidden.

The worker obtains its process path only from:

```powershell
[Diagnostics.Process]::GetCurrentProcess().MainModule.FileName
```

Before any import, the worker sets `$ProgressPreference='SilentlyContinue'`, selects the literal role-specific provider record, and validates the exact manifest and nested DLL path, kind, bytes, .NET digest, versions, leaf-link/reparse policy, and zero parent-chain link/reparse count. Its first import is exactly `Import-Module -Name $ExpectedSecurityManifestPath -Force -PassThru -ErrorAction Stop`. It requires the exact returned module manifest path, GUID, version, compatible edition, sole nested DLL, and exact `Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop` provenance. It then makes exactly three Authenticode calls: its own executable, provider manifest, and provider DLL; every signature/signer/thumbprint must match the pinned role.

Only after those provider checks does the worker import the exact GREEN comparator as its second and final module import. It constructs the exact 14-property observed runtime record, selecting one of two literal expected records by the closed `Role`. The caller role is not proof: the worker calls the frozen GREEN comparator and requires exact Boolean `identity_match=true` before its first parser call. It then parses every target with its own parser API, emits a base64-encoded LF record of the 14 observed scalar values followed by one role-specific PASS, and writes nothing. No environment lookup, module-name lookup, auto-loading, reflection, P/Invoke, `Add-Type`, or fallback command/provider resolution is permitted.

The controller accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('ScalarRed','ScalarGreen','Static')] [string] $Phase,
    [Parameter(Mandatory)] [string] $WorkerPath,
    [Parameter(Mandatory)] [long] $WorkerByteCount,
    [Parameter(Mandatory)] [string] $WorkerSha256,
    [Parameter(Mandatory)] [string] $IdentityModulePath,
    [Parameter(Mandatory)] [long] $IdentityModuleByteCount,
    [Parameter(Mandatory)] [string] $IdentityModuleSha256,
    [Parameter(Mandatory)] [string] $TargetManifestBase64,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

It runs only under the exact frozen PowerShell 7 process, validates the worker/module/targets, all four provider dependencies, and complete workspace inventory using pure .NET hashes, and starts children in this fixed order with `UseShellExecute=false`, redirected streams, and `ArgumentList`:

```text
C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

For each child, decode the 14-field observation, independently call the GREEN comparator against the literal expected role, require exact provider-attested PASS/exit/stderr, and require no workspace name/byte/hash change. No second child starts after the first unexpected observation. The controller contains no `Get-FileHash`, provider import, module search, signature call, or third process start.

Materialize `task-1-parser-worker-v8.ps1` from this exact complete source:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateSet('Pwsh7','WindowsPowerShell51')] [string] $Role,
    [Parameter(Mandatory)] [string] $IdentityModulePath,
    [Parameter(Mandatory)] [long] $IdentityModuleByteCount,
    [Parameter(Mandatory)] [string] $IdentityModuleSha256,
    [Parameter(Mandatory)] [string] $TargetManifestBase64,
    [Parameter(Mandatory)] [string] $WorkspacePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Get-A11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        ([BitConverter]::ToString($Algorithm.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Stream.Dispose()
        $Algorithm.Dispose()
    }
}

function Get-A11ParentLinkCount {
    param([Parameter(Mandatory)] [string] $Path)
    [long]$Count = 0
    $Cursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path))
    while (-not [string]::IsNullOrEmpty($Cursor)) {
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$Item.LinkType)) { $Count++ }
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        $Cursor = $Parent.FullName
    }
    return [long]$Count
}

function Assert-A11FileIdentity {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [long] $ByteCount,
        [Parameter(Mandatory)] [string] $Sha256,
        [Parameter(Mandatory)] [string] $FileVersion,
        [Parameter(Mandatory)] [string] $ProductVersion,
        [Parameter(Mandatory)] [string] $LeafLinkType
    )
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path), $Path)) { throw "file path rejected: $Path" }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or [long]$Item.Length -ne $ByteCount) { throw "file bytes rejected: $Path" }
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "file reparse rejected: $Path" }
    $ActualLinkType = if ([string]::IsNullOrEmpty([string]$Item.LinkType)) { 'None' } else { [string]$Item.LinkType }
    if (-not [StringComparer]::Ordinal.Equals($ActualLinkType, $LeafLinkType)) { throw "file link rejected: $Path" }
    if ((Get-A11ParentLinkCount -Path $Path) -ne [long]0) { throw "parent link rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals((Get-A11FileSha256 -Path $Path), $Sha256)) { throw "file digest rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.FileVersion, $FileVersion)) { throw "file version rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.ProductVersion, $ProductVersion)) { throw "product version rejected: $Path" }
    return $Item
}

function Assert-A11Signature {
    param(
        [Parameter(Mandatory)] [object] $Signature,
        [Parameter(Mandatory)] [string] $Subject,
        [Parameter(Mandatory)] [string] $Thumbprint
    )
    if ($Signature.Status.ToString() -cne 'Valid' -or $null -eq $Signature.SignerCertificate) { throw 'signature status rejected' }
    if (-not [StringComparer]::Ordinal.Equals([string]$Signature.SignerCertificate.Subject, $Subject)) { throw 'signature subject rejected' }
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([string]$Signature.SignerCertificate.Thumbprint, $Thumbprint)) { throw 'signature thumbprint rejected' }
}

function Get-A11WorkspaceSnapshot {
    param([Parameter(Mandatory)] [string] $Path)
    $Records = New-Object 'Collections.Generic.List[string]'
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force | Sort-Object -Property Name)) {
        if ($Item.PSIsContainer) { throw 'workspace directory child rejected' }
        [void]$Records.Add("$($Item.Name)|$([long]$Item.Length)|$(Get-A11FileSha256 -Path $Item.FullName)")
    }
    [string]::Join("`n", $Records)
}

function Get-A11RolePolicy {
    param([Parameter(Mandatory)] [string] $SelectedRole)
    if ($SelectedRole -ceq 'Pwsh7') {
        return [pscustomobject][ordered]@{
            role = 'pwsh7'
            process_path = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
            powershell_version = '7.6.4'
            ps_edition = 'Core'
            executable_byte_count = [long]301368
            executable_sha256 = 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'
            file_version = '7.6.4.500'
            product_version = '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
            signer_subject = 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
            signer_thumbprint = 'AB172913A2960A224809EE8A0C371CD47A079B72'
            leaf_link_type = 'None'
            security_manifest_path = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
            security_manifest_bytes = [long]15463
            security_manifest_sha256 = 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a'
            security_manifest_file_version = ''
            security_manifest_product_version = ''
            security_manifest_link_type = 'None'
            security_manifest_signer_thumbprint = 'AB172913A2960A224809EE8A0C371CD47A079B72'
            security_dll_path = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll'
            security_dll_bytes = [long]345952
            security_dll_sha256 = '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90'
            security_dll_file_version = '7.6.4.500'
            security_dll_product_version = '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
            security_dll_link_type = 'None'
            security_dll_signer_thumbprint = '1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1'
            security_guid = 'A94C8C7E-9810-47C0-B8AF-65089C13A35A'
            security_version = '7.0.0.0'
            security_edition = 'Core'
        }
    }
    [pscustomobject][ordered]@{
        role = 'windows-powershell-5.1'
        process_path = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        powershell_version = '5.1'
        ps_edition = 'Desktop'
        executable_byte_count = [long]454656
        executable_sha256 = '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'
        file_version = '10.0.26100.8875 (WinBuild.160101.0800)'
        product_version = '10.0.26100.8875'
        signer_subject = 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
        signer_thumbprint = 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
        leaf_link_type = 'HardLink'
        security_manifest_path = 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
        security_manifest_bytes = [long]776
        security_manifest_sha256 = 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30'
        security_manifest_file_version = ''
        security_manifest_product_version = ''
        security_manifest_link_type = 'HardLink'
        security_manifest_signer_thumbprint = '71F53A26BB1625E466727183409A30D03D7923DF'
        security_dll_path = 'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll'
        security_dll_bytes = [long]93696
        security_dll_sha256 = '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010'
        security_dll_file_version = '10.0.26100.1'
        security_dll_product_version = '10.0.26100.1'
        security_dll_link_type = 'HardLink'
        security_dll_signer_thumbprint = '71F53A26BB1625E466727183409A30D03D7923DF'
        security_guid = 'A94C8C7E-9810-47C0-B8AF-65089C13A35A'
        security_version = '3.0.0.0'
        security_edition = 'Desktop'
    }
}

$CanonicalWorkspace = [IO.Path]::GetFullPath($WorkspacePath)
$WorkspacePrefix = $CanonicalWorkspace.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$Before = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
$Policy = Get-A11RolePolicy -SelectedRole $Role
$ActualProcessPath = [IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
$ExecutableItem = Assert-A11FileIdentity -Path $ActualProcessPath -ByteCount $Policy.executable_byte_count -Sha256 $Policy.executable_sha256 -FileVersion $Policy.file_version -ProductVersion $Policy.product_version -LeafLinkType $Policy.leaf_link_type
$ManifestItem = Assert-A11FileIdentity -Path $Policy.security_manifest_path -ByteCount $Policy.security_manifest_bytes -Sha256 $Policy.security_manifest_sha256 -FileVersion $Policy.security_manifest_file_version -ProductVersion $Policy.security_manifest_product_version -LeafLinkType $Policy.security_manifest_link_type
$DllItem = Assert-A11FileIdentity -Path $Policy.security_dll_path -ByteCount $Policy.security_dll_bytes -Sha256 $Policy.security_dll_sha256 -FileVersion $Policy.security_dll_file_version -ProductVersion $Policy.security_dll_product_version -LeafLinkType $Policy.security_dll_link_type

$SecurityModule = Import-Module -Name $Policy.security_manifest_path -Force -PassThru -ErrorAction Stop
$IdentityModule = $null
try {
    if (@($SecurityModule).Count -ne 1) { throw 'Security module count rejected' }
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$SecurityModule.Path), [string]$Policy.security_manifest_path)) { throw 'Security module path rejected' }
    if ($SecurityModule.Guid.ToString().ToUpperInvariant() -cne $Policy.security_guid -or $SecurityModule.Version.ToString() -cne $Policy.security_version) { throw 'Security module identity rejected' }
    if (@($SecurityModule.CompatiblePSEditions).Count -ne 1 -or [string]$SecurityModule.CompatiblePSEditions[0] -cne $Policy.security_edition) { throw 'Security module edition rejected' }
    if (@($SecurityModule.NestedModules).Count -ne 1 -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$SecurityModule.NestedModules[0].Path), [string]$Policy.security_dll_path)) { throw 'Security nested DLL rejected' }
    $AuthCommand = Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop
    if (@($AuthCommand).Count -ne 1 -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$AuthCommand.Module.Path), [string]$Policy.security_manifest_path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath([string]$AuthCommand.DLL), [string]$Policy.security_dll_path)) { throw 'Authenticode command provenance rejected' }

    $ExecutableSignature = Get-AuthenticodeSignature -LiteralPath $ActualProcessPath
    $ManifestSignature = Get-AuthenticodeSignature -LiteralPath $Policy.security_manifest_path
    $DllSignature = Get-AuthenticodeSignature -LiteralPath $Policy.security_dll_path
    Assert-A11Signature -Signature $ExecutableSignature -Subject $Policy.signer_subject -Thumbprint $Policy.signer_thumbprint
    Assert-A11Signature -Signature $ManifestSignature -Subject $Policy.signer_subject -Thumbprint $Policy.security_manifest_signer_thumbprint
    Assert-A11Signature -Signature $DllSignature -Subject $Policy.signer_subject -Thumbprint $Policy.security_dll_signer_thumbprint

    $EngineVersion = if ($Role -ceq 'WindowsPowerShell51' -and $PSVersionTable.PSVersion.Major -eq 5 -and $PSVersionTable.PSVersion.Minor -eq 1) { '5.1' } else { $PSVersionTable.PSVersion.ToString() }
    $Observed = [pscustomobject][ordered]@{
        role = [string]$Policy.role
        process_path = [string]$ActualProcessPath
        powershell_version = [string]$EngineVersion
        ps_edition = [string]$PSVersionTable.PSEdition
        executable_byte_count = [long]$ExecutableItem.Length
        executable_sha256 = [string](Get-A11FileSha256 -Path $ActualProcessPath)
        file_version = [string]$ExecutableItem.VersionInfo.FileVersion
        product_version = [string]$ExecutableItem.VersionInfo.ProductVersion
        signature_status = [string]$ExecutableSignature.Status.ToString()
        signer_subject = [string]$ExecutableSignature.SignerCertificate.Subject
        signer_thumbprint = [string]$ExecutableSignature.SignerCertificate.Thumbprint
        leaf_link_type = if ([string]::IsNullOrEmpty([string]$ExecutableItem.LinkType)) { 'None' } else { [string]$ExecutableItem.LinkType }
        leaf_reparse_point = [bool](($ExecutableItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
        parent_chain_reparse_points = [long](Get-A11ParentLinkCount -Path $ActualProcessPath)
    }
    $Expected = [pscustomobject][ordered]@{
        role = [string]$Policy.role
        process_path = [string]$Policy.process_path
        powershell_version = [string]$Policy.powershell_version
        ps_edition = [string]$Policy.ps_edition
        executable_byte_count = [long]$Policy.executable_byte_count
        executable_sha256 = [string]$Policy.executable_sha256
        file_version = [string]$Policy.file_version
        product_version = [string]$Policy.product_version
        signature_status = 'Valid'
        signer_subject = [string]$Policy.signer_subject
        signer_thumbprint = [string]$Policy.signer_thumbprint
        leaf_link_type = [string]$Policy.leaf_link_type
        leaf_reparse_point = [bool]$false
        parent_chain_reparse_points = [long]0
    }

    $CanonicalIdentityModule = [IO.Path]::GetFullPath($IdentityModulePath)
    if (-not $CanonicalIdentityModule.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'identity module containment rejected' }
    [void](Assert-A11FileIdentity -Path $CanonicalIdentityModule -ByteCount $IdentityModuleByteCount -Sha256 $IdentityModuleSha256 -FileVersion '' -ProductVersion '' -LeafLinkType 'None')
    $IdentityModule = Import-Module -Name $CanonicalIdentityModule -Force -PassThru -ErrorAction Stop
    if (@($IdentityModule).Count -ne 1 -or @(Get-Command -Module $IdentityModule.Name -ErrorAction Stop).Count -ne 1) { throw 'identity module import rejected' }
    $IdentityResult = Compare-A11ParserRuntimeIdentity -Expected $Expected -Observed $Observed
    if ($IdentityResult.identity_match.GetType() -ne [bool] -or -not [bool]$IdentityResult.identity_match) { throw 'runtime identity rejected' }

    $Utf8 = New-Object Text.UTF8Encoding($false, $true)
    $ManifestBytes = [Convert]::FromBase64String($TargetManifestBase64)
    $ManifestText = $Utf8.GetString($ManifestBytes)
    if ([string]::IsNullOrEmpty($ManifestText) -or $ManifestText.Contains("`r") -or $ManifestText[0] -eq [char]0xFEFF -or $ManifestText.EndsWith("`n", [StringComparison]::Ordinal)) { throw 'target manifest encoding rejected' }
    $Lines = @($ManifestText.Split([char]10))
    if ($Lines.Count -eq 0) { throw 'target manifest empty' }
    for ($LineIndex = 0; $LineIndex -lt $Lines.Count; $LineIndex++) {
        if ($LineIndex -gt 0 -and [StringComparer]::Ordinal.Compare($Lines[$LineIndex - 1], $Lines[$LineIndex]) -ge 0) { throw 'target manifest order rejected' }
        $Line = $Lines[$LineIndex]
        $Parts = @($Line.Split('|'))
        if ($Parts.Count -ne 3 -or $Parts[1] -notmatch '\A(?:0|[1-9][0-9]*)\z' -or $Parts[2] -notmatch '\A[0-9a-f]{64}\z') { throw 'target manifest record rejected' }
        [long]$ExpectedBytes = 0
        if (-not [long]::TryParse($Parts[1], [Globalization.NumberStyles]::None, [Globalization.CultureInfo]::InvariantCulture, [ref]$ExpectedBytes)) { throw 'target byte count rejected' }
        $TargetPath = [IO.Path]::GetFullPath($Parts[0])
        if (-not $TargetPath.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'target containment rejected' }
        [void](Assert-A11FileIdentity -Path $TargetPath -ByteCount $ExpectedBytes -Sha256 $Parts[2] -FileVersion '' -ProductVersion '' -LeafLinkType 'None')
        $Tokens = $null
        $Errors = $null
        [void][Management.Automation.Language.Parser]::ParseFile($TargetPath, [ref]$Tokens, [ref]$Errors)
        if (@($Errors).Count -ne 0) { throw "target parse rejected: $TargetPath" }
    }

    $ObservationFields = @(
        $Observed.role,$Observed.process_path,$Observed.powershell_version,$Observed.ps_edition,
        ([string]$Observed.executable_byte_count),$Observed.executable_sha256,$Observed.file_version,$Observed.product_version,
        $Observed.signature_status,$Observed.signer_subject,$Observed.signer_thumbprint,$Observed.leaf_link_type,
        ([string]$Observed.leaf_reparse_point).ToLowerInvariant(),([string]$Observed.parent_chain_reparse_points)
    )
    $ObservationBase64 = [Convert]::ToBase64String($Utf8.GetBytes([string]::Join("`n", $ObservationFields)))
    $TerminalRole = [string]$Policy.role
}
finally {
    if ($null -ne $IdentityModule) { Remove-Module -ModuleInfo $IdentityModule -Force -ErrorAction Stop }
    Remove-Module -ModuleInfo $SecurityModule -Force -ErrorAction Stop
}
$After = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
if (-not [StringComparer]::Ordinal.Equals($Before, $After)) { throw 'workspace changed' }
$ObservationBase64
"ENTRYV8_PARSER_WORKER_PASS|role=$TerminalRole|provider=Microsoft.PowerShell.Security"
```

Materialize `task-1-dual-parser-controller-v8.ps1` from this exact complete source:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateSet('ScalarRed','ScalarGreen','Static')] [string] $Phase,
    [Parameter(Mandatory)] [string] $WorkerPath,
    [Parameter(Mandatory)] [long] $WorkerByteCount,
    [Parameter(Mandatory)] [string] $WorkerSha256,
    [Parameter(Mandatory)] [string] $IdentityModulePath,
    [Parameter(Mandatory)] [long] $IdentityModuleByteCount,
    [Parameter(Mandatory)] [string] $IdentityModuleSha256,
    [Parameter(Mandatory)] [string] $TargetManifestBase64,
    [Parameter(Mandatory)] [string] $WorkspacePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Get-A11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        ([BitConverter]::ToString($Algorithm.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Stream.Dispose()
        $Algorithm.Dispose()
    }
}

function Get-A11ParentLinkCount {
    param([Parameter(Mandatory)] [string] $Path)
    [long]$Count = 0
    $Cursor = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path))
    while (-not [string]::IsNullOrEmpty($Cursor)) {
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$Item.LinkType)) { $Count++ }
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        $Cursor = $Parent.FullName
    }
    return [long]$Count
}

function Assert-A11FileIdentity {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [long] $ByteCount,
        [Parameter(Mandatory)] [string] $Sha256,
        [Parameter(Mandatory)] [string] $FileVersion,
        [Parameter(Mandatory)] [string] $ProductVersion,
        [Parameter(Mandatory)] [string] $LeafLinkType
    )
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($Path), $Path)) { throw "file path rejected: $Path" }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or [long]$Item.Length -ne $ByteCount) { throw "file bytes rejected: $Path" }
    if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "file reparse rejected: $Path" }
    $ActualLinkType = if ([string]::IsNullOrEmpty([string]$Item.LinkType)) { 'None' } else { [string]$Item.LinkType }
    if (-not [StringComparer]::Ordinal.Equals($ActualLinkType, $LeafLinkType) -or (Get-A11ParentLinkCount -Path $Path) -ne [long]0) { throw "file link policy rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals((Get-A11FileSha256 -Path $Path), $Sha256)) { throw "file digest rejected: $Path" }
    if (-not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.FileVersion, $FileVersion) -or -not [StringComparer]::Ordinal.Equals([string]$Item.VersionInfo.ProductVersion, $ProductVersion)) { throw "file version rejected: $Path" }
    return $Item
}

function Get-A11WorkspaceSnapshot {
    param([Parameter(Mandatory)] [string] $Path)
    $Records = New-Object 'Collections.Generic.List[string]'
    foreach ($Item in @(Get-ChildItem -LiteralPath $Path -Force | Sort-Object -Property Name)) {
        if ($Item.PSIsContainer) { throw 'workspace directory child rejected' }
        [void]$Records.Add("$($Item.Name)|$([long]$Item.Length)|$(Get-A11FileSha256 -Path $Item.FullName)")
    }
    [string]::Join("`n", $Records)
}

function New-A11ExpectedRuntime {
    param([Parameter(Mandatory)] [ValidateSet('Pwsh7','WindowsPowerShell51')] [string] $SelectedRole)
    if ($SelectedRole -ceq 'Pwsh7') {
        return [pscustomobject][ordered]@{
            role = 'pwsh7'
            process_path = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
            powershell_version = '7.6.4'
            ps_edition = 'Core'
            executable_byte_count = [long]301368
            executable_sha256 = 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f'
            file_version = '7.6.4.500'
            product_version = '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d'
            signature_status = 'Valid'
            signer_subject = 'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
            signer_thumbprint = 'AB172913A2960A224809EE8A0C371CD47A079B72'
            leaf_link_type = 'None'
            leaf_reparse_point = [bool]$false
            parent_chain_reparse_points = [long]0
        }
    }
    [pscustomobject][ordered]@{
        role = 'windows-powershell-5.1'
        process_path = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        powershell_version = '5.1'
        ps_edition = 'Desktop'
        executable_byte_count = [long]454656
        executable_sha256 = '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5'
        file_version = '10.0.26100.8875 (WinBuild.160101.0800)'
        product_version = '10.0.26100.8875'
        signature_status = 'Valid'
        signer_subject = 'CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'
        signer_thumbprint = 'DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443'
        leaf_link_type = 'HardLink'
        leaf_reparse_point = [bool]$false
        parent_chain_reparse_points = [long]0
    }
}

$FrozenPwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
$CurrentProcessPath = [IO.Path]::GetFullPath([Diagnostics.Process]::GetCurrentProcess().MainModule.FileName)
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($CurrentProcessPath, $FrozenPwsh) -or $PSVersionTable.PSVersion.ToString() -cne '7.6.4' -or $PSVersionTable.PSEdition -cne 'Core') { throw 'controller runtime rejected' }
[void](Assert-A11FileIdentity -Path $FrozenPwsh -ByteCount 301368 -Sha256 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d' -LeafLinkType 'None')
[void](Assert-A11FileIdentity -Path 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -ByteCount 454656 -Sha256 '7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5' -FileVersion '10.0.26100.8875 (WinBuild.160101.0800)' -ProductVersion '10.0.26100.8875' -LeafLinkType 'HardLink')
[void](Assert-A11FileIdentity -Path 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1' -ByteCount 15463 -Sha256 'c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a' -FileVersion '' -ProductVersion '' -LeafLinkType 'None')
[void](Assert-A11FileIdentity -Path 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll' -ByteCount 345952 -Sha256 '5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90' -FileVersion '7.6.4.500' -ProductVersion '7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d' -LeafLinkType 'None')
[void](Assert-A11FileIdentity -Path 'C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1' -ByteCount 776 -Sha256 'fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30' -FileVersion '' -ProductVersion '' -LeafLinkType 'HardLink')
[void](Assert-A11FileIdentity -Path 'C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll' -ByteCount 93696 -Sha256 '9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010' -FileVersion '10.0.26100.1' -ProductVersion '10.0.26100.1' -LeafLinkType 'HardLink')

$CanonicalWorkspace = [IO.Path]::GetFullPath($WorkspacePath)
$WorkspacePrefix = $CanonicalWorkspace.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$CanonicalWorker = [IO.Path]::GetFullPath($WorkerPath)
$CanonicalIdentityModule = [IO.Path]::GetFullPath($IdentityModulePath)
if (-not $CanonicalWorker.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase) -or -not $CanonicalIdentityModule.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'controller input containment rejected' }
[void](Assert-A11FileIdentity -Path $CanonicalWorker -ByteCount $WorkerByteCount -Sha256 $WorkerSha256 -FileVersion '' -ProductVersion '' -LeafLinkType 'None')
[void](Assert-A11FileIdentity -Path $CanonicalIdentityModule -ByteCount $IdentityModuleByteCount -Sha256 $IdentityModuleSha256 -FileVersion '' -ProductVersion '' -LeafLinkType 'None')

$Utf8 = New-Object Text.UTF8Encoding($false, $true)
$TargetManifestText = $Utf8.GetString([Convert]::FromBase64String($TargetManifestBase64))
if ([string]::IsNullOrEmpty($TargetManifestText) -or $TargetManifestText.Contains("`r") -or $TargetManifestText[0] -eq [char]0xFEFF -or $TargetManifestText.EndsWith("`n", [StringComparison]::Ordinal)) { throw 'target manifest encoding rejected' }
$TargetLines = @($TargetManifestText.Split([char]10))
for ($Index = 0; $Index -lt $TargetLines.Count; $Index++) {
    if ($Index -gt 0 -and [StringComparer]::Ordinal.Compare($TargetLines[$Index - 1], $TargetLines[$Index]) -ge 0) { throw 'target manifest order rejected' }
    $Parts = @($TargetLines[$Index].Split('|'))
    if ($Parts.Count -ne 3 -or $Parts[1] -notmatch '\A(?:0|[1-9][0-9]*)\z' -or $Parts[2] -notmatch '\A[0-9a-f]{64}\z') { throw 'target manifest record rejected' }
    [long]$ExpectedBytes = 0
    if (-not [long]::TryParse($Parts[1], [Globalization.NumberStyles]::None, [Globalization.CultureInfo]::InvariantCulture, [ref]$ExpectedBytes)) { throw 'target byte count rejected' }
    $TargetPath = [IO.Path]::GetFullPath($Parts[0])
    if (-not $TargetPath.StartsWith($WorkspacePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'target containment rejected' }
    [void](Assert-A11FileIdentity -Path $TargetPath -ByteCount $ExpectedBytes -Sha256 $Parts[2] -FileVersion '' -ProductVersion '' -LeafLinkType 'None')
}

$Before = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
$IdentityModule = Import-Module -Name $CanonicalIdentityModule -Force -PassThru -ErrorAction Stop
try {
    if (@($IdentityModule).Count -ne 1 -or @(Get-Command -Module $IdentityModule.Name -ErrorAction Stop).Count -ne 1) { throw 'identity module import rejected' }
    $Roles = @(
        [pscustomobject][ordered]@{ WorkerRole = 'Pwsh7'; FileName = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'; ProtocolRole = 'pwsh7' },
        [pscustomobject][ordered]@{ WorkerRole = 'WindowsPowerShell51'; FileName = 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'; ProtocolRole = 'windows-powershell-5.1' }
    )
    [long]$StartCount = 0
    foreach ($RoleRecord in $Roles) {
        $StartInfo = [Diagnostics.ProcessStartInfo]::new()
        $StartInfo.FileName = [string]$RoleRecord.FileName
        $StartInfo.UseShellExecute = $false
        $StartInfo.RedirectStandardOutput = $true
        $StartInfo.RedirectStandardError = $true
        $StartInfo.CreateNoWindow = $true
        foreach ($Argument in @(
            '-NoLogo','-NoProfile','-NonInteractive','-File',$CanonicalWorker,
            '-Role',[string]$RoleRecord.WorkerRole,
            '-IdentityModulePath',$CanonicalIdentityModule,
            '-IdentityModuleByteCount',[string]$IdentityModuleByteCount,
            '-IdentityModuleSha256',$IdentityModuleSha256,
            '-TargetManifestBase64',$TargetManifestBase64,
            '-WorkspacePath',$CanonicalWorkspace
        )) { [void]$StartInfo.ArgumentList.Add([string]$Argument) }
        $Process = [Diagnostics.Process]::new()
        $Process.StartInfo = $StartInfo
        try {
            if (-not $Process.Start()) { throw 'child start rejected' }
            $StartCount++
            $Stdout = $Process.StandardOutput.ReadToEnd()
            $Stderr = $Process.StandardError.ReadToEnd()
            $Process.WaitForExit()
            $ExitCode = $Process.ExitCode
        }
        finally {
            $Process.Dispose()
        }
        if ($ExitCode -ne 0 -or $Stderr.Length -ne 0) { throw 'child exit rejected' }
        $Normalized = $Stdout.Replace("`r", '')
        if (-not $Normalized.EndsWith("`n", [StringComparison]::Ordinal)) { throw 'child stdout termination rejected' }
        $Lines = @($Normalized.Substring(0, $Normalized.Length - 1).Split([char]10))
        if ($Lines.Count -ne 2 -or $Lines[1] -cne "ENTRYV8_PARSER_WORKER_PASS|role=$($RoleRecord.ProtocolRole)|provider=Microsoft.PowerShell.Security") { throw 'child protocol rejected' }
        $ObservationText = $Utf8.GetString([Convert]::FromBase64String($Lines[0]))
        if ($ObservationText.Contains("`r") -or $ObservationText.EndsWith("`n", [StringComparison]::Ordinal)) { throw 'observation encoding rejected' }
        $Fields = @($ObservationText.Split([char]10))
        if ($Fields.Count -ne 14 -or $Fields[4] -notmatch '\A(?:0|[1-9][0-9]*)\z' -or $Fields[12] -notin @('true','false') -or $Fields[13] -notmatch '\A(?:0|[1-9][0-9]*)\z') { throw 'observation record rejected' }
        [long]$ObservedBytes = 0
        [long]$ObservedParents = 0
        if (-not [long]::TryParse($Fields[4], [ref]$ObservedBytes) -or -not [long]::TryParse($Fields[13], [ref]$ObservedParents)) { throw 'observation scalar rejected' }
        $Observed = [pscustomobject][ordered]@{
            role = [string]$Fields[0]
            process_path = [string]$Fields[1]
            powershell_version = [string]$Fields[2]
            ps_edition = [string]$Fields[3]
            executable_byte_count = [long]$ObservedBytes
            executable_sha256 = [string]$Fields[5]
            file_version = [string]$Fields[6]
            product_version = [string]$Fields[7]
            signature_status = [string]$Fields[8]
            signer_subject = [string]$Fields[9]
            signer_thumbprint = [string]$Fields[10]
            leaf_link_type = [string]$Fields[11]
            leaf_reparse_point = [bool]($Fields[12] -ceq 'true')
            parent_chain_reparse_points = [long]$ObservedParents
        }
        $Expected = New-A11ExpectedRuntime -SelectedRole $RoleRecord.WorkerRole
        $Identity = Compare-A11ParserRuntimeIdentity -Expected $Expected -Observed $Observed
        if ($Identity.identity_match.GetType() -ne [bool] -or -not [bool]$Identity.identity_match) { throw 'child identity rejected' }
        $AfterChild = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
        if (-not [StringComparer]::Ordinal.Equals($Before, $AfterChild)) { throw 'child workspace change rejected' }
    }
}
finally {
    Remove-Module -ModuleInfo $IdentityModule -Force -ErrorAction Stop
}
if ($StartCount -ne [long]2) { throw 'process start count rejected' }
$After = Get-A11WorkspaceSnapshot -Path $CanonicalWorkspace
if (-not [StringComparer]::Ordinal.Equals($Before, $After)) { throw 'workspace changed' }
$PhaseName = if ($Phase -ceq 'ScalarRed') { 'scalar-red' } elseif ($Phase -ceq 'ScalarGreen') { 'scalar-green' } else { 'static' }
"ENTRYV8_DUAL_PARSER_PASS|phase=$PhaseName|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0"
```

The plan-pinned execution blocks above use UTF-8 without BOM, LF line endings, and exactly one final LF. Their immutable materialization identities are:

| Source | Bytes | SHA-256 |
|---|---:|---|
| Stage 0 command body | 14,198 | `5c9de5a85ae6e90fa5d4bd23c7e8f7fc49061a85d2f3c55a39524d9f48b19c70` |
| `task-1-parser-identity-red-v8.psm1` | 625 | `788c5f563b6372388835621e1f3226b38de577f6a05ee17f9c621473eeb4ee74` |
| `task-1-parser-identity-tests-v8.ps1` | 11,005 | `f058876d8b65a32256b1de43282d4b30006de8c64c4c1b3ea0113658b50f3291` |
| `task-1-parser-identity-green-v8.psm1` | 3,720 | `b4c9d84b9ceed33c334a59b9059ad5dea293ecbb8fdaa16371619dc04c2ac2fe` |
| `task-1-parser-worker-v8.ps1` | 17,887 | `7aca554a06a46aa4396f53f622f4eba7b32e185e8946dd43c8191f1fe9939d4d` |
| `task-1-dual-parser-controller-v8.ps1` | 15,626 | `c792752d00c857013d00d282ca8760034c8b20dc509f047f375020ce6464fe09` |

At execution, recompute these six identities from the committed plan blob before Stage 0 or materialization. Any byte difference is `ENTRYV8_RECOVERY_UNPROVABLE / NO_GO`; do not reconstruct from this working-tree draft or a copied source.

The scalar test interface matches Task 1's six-parameter test interface with modes `Red` and `Green`. The intentional RED and GREEN scalar interface is exactly:

```powershell
function Compare-A11ScalarIdentity {
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualSha256,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedSha256
    )
}
```

The intentional RED returns the exact seven-property record but always sets `identity_match=false`. The test literal pair is `[long]97` and `c8f5ccbd382ead232f759a4a4a69bf16f3121a2c511cc2b66e729e5451d136`.

- [ ] **Step 2: Run the `scalar-red` dual-parser phase exactly once**

Freeze exact identities for all eight files now present. Build the sorted base64 manifest manually in memory and print its decoded records before invocation. Run the controller once in `ScalarRed` mode. Require exactly two child starts, exit 0, empty controller stderr, no file change, and sole controller stdout:

```text
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-red|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
```

Any difference is `ENTRYV8_DUAL_PARSER_UNPROVABLE / NO_GO`; preserve and stop without scalar RED execution.

- [ ] **Step 3: Run fresh scalar RED exactly once**

Run the frozen scalar test in `Red` mode through the exact PowerShell 7 executable with literal module/test/workspace identities. Require exit 0, empty stderr, unchanged eight-file inventory, and sole stdout:

```text
SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected
```

Any difference is `ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO`; never rerun or edit the scalar test/RED/invocation.

- [ ] **Step 4: Create the scalar GREEN module**

Create it once with `apply_patch`. The complete module is:

```powershell
Set-StrictMode -Version Latest

function Compare-A11ScalarIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualSha256,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedSha256
    )

    if ($null -eq $ActualByteCount -or $null -eq $ExpectedByteCount -or $null -eq $ActualSha256 -or $null -eq $ExpectedSha256) { throw 'null identity value rejected' }
    if ($ActualByteCount -is [array] -or $ExpectedByteCount -is [array] -or $ActualSha256 -is [array] -or $ExpectedSha256 -is [array]) { throw 'array identity value rejected' }
    if (($ActualByteCount -is [Collections.IEnumerable] -and $ActualByteCount -isnot [string]) -or
        ($ExpectedByteCount -is [Collections.IEnumerable] -and $ExpectedByteCount -isnot [string]) -or
        ($ActualSha256 -is [Collections.IEnumerable] -and $ActualSha256 -isnot [string]) -or
        ($ExpectedSha256 -is [Collections.IEnumerable] -and $ExpectedSha256 -isnot [string])) { throw 'enumerable identity value rejected' }
    if ($ActualByteCount.GetType() -ne [long] -or $ExpectedByteCount.GetType() -ne [long]) { throw 'byte count type rejected' }
    if ([long]$ActualByteCount -lt 0 -or [long]$ExpectedByteCount -lt 0) { throw 'negative byte count rejected' }
    if ($ActualSha256.GetType() -ne [string] -or $ExpectedSha256.GetType() -ne [string]) { throw 'digest type rejected' }
    if (-not [regex]::IsMatch([string]$ActualSha256, '\A[0-9a-f]{64}\z', [Text.RegularExpressions.RegexOptions]::CultureInvariant)) { throw 'actual digest format rejected' }
    if (-not [regex]::IsMatch([string]$ExpectedSha256, '\A[0-9a-f]{64}\z', [Text.RegularExpressions.RegexOptions]::CultureInvariant)) { throw 'expected digest format rejected' }

    $ByteCountMatch = ([long]$ActualByteCount -eq [long]$ExpectedByteCount)
    $Sha256Match = [StringComparer]::Ordinal.Equals([string]$ActualSha256, [string]$ExpectedSha256)
    [pscustomobject][ordered]@{
        actual_byte_count = [long]$ActualByteCount
        expected_byte_count = [long]$ExpectedByteCount
        byte_count_match = [bool]$ByteCountMatch
        actual_sha256 = [string]$ActualSha256
        expected_sha256 = [string]$ExpectedSha256
        sha256_match = [bool]$Sha256Match
        identity_match = [bool]($ByteCountMatch -and $Sha256Match)
    }
}

Export-ModuleMember -Function Compare-A11ScalarIdentity
```

- [ ] **Step 5: Run the `scalar-green` dual-parser phase exactly once**

Freeze the new nine-file inventory and a new sorted base64 target manifest. Run the controller once in `ScalarGreen` mode. Require sole stdout:

```text
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-green|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
```

Require exit 0, empty stderr, exactly two starts, and no workspace change. Any difference is `ENTRYV8_DUAL_PARSER_UNPROVABLE / NO_GO`; do not run scalar GREEN.

- [ ] **Step 6: Run fresh scalar GREEN exactly once**

Run the frozen scalar test in `Green` mode. Require the exact approved eight categories: exact match; array digest rejection; array byte rejection; one digest-nibble mismatch; one byte mismatch; six malformed digest cases; three malformed byte cases; exact result property/type closure. Require exit 0, empty stderr, unchanged nine-file inventory, and sole stdout:

```text
SCALAR_IDENTITY_TEST_GREEN_PASS|cases=8|comparison=ordinal|collections=rejected
```

Any difference is `ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO`; freeze and stop.

---

### Task 3: Author the canonical inventory and pass static admission

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-preserved-inventory-v8.json`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-entry-verifier-v8.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-static-verifier-v8.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-closure-verifier-v8.ps1`

**Interfaces:**
- Consumes: exact nine-file v8 TDD/control inventory, plan/original-design/amendment identities, v7 four-file NO_GO, 20 approved v2-v5 records, 12 absences, two executable identities, and four provider-file identities.
- Produces: one canonical 24-file inventory plus two-provider dependency overlay, complete read-only formal/closure sources, and exact static PASS before formal entry.

- [ ] **Step 1: Author and freeze the canonical inventory manually**

Print a literal identity table for the current plan/original design/amendment, all nine current v8 sources, both executables, all four provider files, v7 four files, and the 20 approved v2-v5 files. Do not derive expected inventory values from the live filesystem.

Create one compact UTF-8 JSON object without BOM plus one LF with exact root order:

```text
schema_version,inventory_id,source_plan_commit,source_design_commit,source_amendment_commit,failed_v7,parser_runtimes,security_providers,workspaces,absent_paths
```

Use `schema_version=1` and `inventory_id=entryv8-preserved-inventory-001`. `failed_v7` exact order is:

```text
plan_commit,plan_blob,design_commit,design_blob,workspace,terminal,stage0_pass,red_executed,red_terminal,windows_powershell_precondition,green_module_created,green_test_executed,success_terminal_emitted,retroactive_pass_allowed
```

Use exact `red_terminal=SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected`. The seven Boolean fields are exact: `stage0_pass=true`, `red_executed=true`, `windows_powershell_precondition=false`, `green_module_created=true`, `green_test_executed=false`, `success_terminal_emitted=false`, and `retroactive_pass_allowed=false`.

`parser_runtimes` contains PowerShell 7 then Windows PowerShell 5.1 with the exact identities in Global Constraints and exact closed record order from Task 1.

`security_providers` contains PowerShell 7 then Windows PowerShell 5.1. Each record has exact order:

```text
role,manifest,nested_assembly,allowed_commands
```

Each `manifest` and `nested_assembly` object has exact order:

```text
path,byte_count,sha256,file_version,product_version,signature_status,signer_subject,signer_thumbprint,leaf_link_type,leaf_reparse_point,parent_chain_reparse_points
```

Use exact `System.Int64` byte counts, exact strings, exact Booleans, the provider identities in Global Constraints, empty file/product version strings for both manifest text files, and exact one-element `allowed_commands=["Get-AuthenticodeSignature"]`. Provider files are execution dependencies and are not included in the 24 preserved-file count.

`workspaces` contains v7, v5, v4, v3, then v2. Each object order is `generation,path,file_count,files`; each file order is `path,byte_count,sha256`. v7 is the exact four-file table from Stage 0. Carry forward these 20 approved records literally:

| Gen | File | Bytes | SHA-256 |
|---|---|---:|---|
| v5 | `task-1-ancestor-chain-red-v5.ps1` | 1436 | `dfa8f9b572ff31439b8198acd014d53c0efbc408ab50cbce156423293e92b9ac` |
| v5 | `task-1-ancestor-chain-tests-v5.ps1` | 8798 | `07dc9df03102dd64c6d79326c25281fcd143246618777a0c55abfb917623ca09` |
| v5 | `task-1-bootstrap-command-static-v5.ps1` | 20783 | `8ae484662c7f5165b721ad70e3213f1aad43f4b5d238af5282e6ecda1df051f9` |
| v5 | `task-1-bootstrap-red-brief-v5.md` | 5003 | `5d5a95ef800a34f5cfb9a65833367191bde725f6741bb2d79fce0c626644da27` |
| v5 | `task-1-entry-gate-v5.ps1` | 6250 | `2d1b8f10842d6abdc8bea772d258f593b733b2fa7a8af21522c569199fb7dee1` |
| v5 | `task-1-evidence-module-red-v5.psm1` | 97 | `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071` |
| v5 | `task-1-evidence-tests-v5.ps1` | 12339 | `21b59e3e4264706d095c5135a9c1a71fc7ada45dfb2731c02badf0134818c92b` |
| v5 | `task-1-red-command-v5.json` | 1437 | `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` |
| v4 | `task-1-bootstrap-command-static-v4.ps1` | 12532 | `e17d575e0ff8287ea7424c28c08b14bd7625e5603651b07f0283e4a5ced72a68` |
| v4 | `task-1-entry-gate-v4.ps1` | 5562 | `8e35c0ab663116587448ecb6840bf6c6ecc876c367fe25f4fa86a3e2616b764d` |
| v4 | `task-1-evidence-module-red-v4.psm1` | 97 | `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb` |
| v4 | `task-1-evidence-tests-v4.ps1` | 8824 | `aca02e4a213baa1703eec9c0a82a638240de46ecfb77cd0b944c3ab778f7a863` |
| v4 | `task-1-red-command-v4.json` | 1461 | `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` |
| v3 | `task-1-bootstrap-path-static-v3.ps1` | 7521 | `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9` |
| v3 | `task-1-entry-gate-v3.ps1` | 5151 | `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19` |
| v3 | `task-1-evidence-module-red-v3.psm1` | 97 | `c8f5ccbd382ead232f759a4a4a69bf16f3121a2c511cc2b66e729e5451d136` |
| v3 | `task-1-evidence-tests-v3.ps1` | 9012 | `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c` |
| v2 | `task-1-entry-gate.ps1` | 3541 | `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b` |
| v2 | `task-1-evidence-module-red.psm1` | 103 | `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc` |
| v2 | `task-1-evidence-tests.ps1` | 4420 | `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65` |

`absent_paths` is exactly these 12 fully qualified strings in order:

1. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery\machine`
2. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\machine`
3. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\machine`
4. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery\machine`
5. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine\preformal-003-recorder-red-verify.stdout.bin`
6. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine\preformal-003-recorder-red-verify.stderr.bin`
7. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine\preformal-003-recorder-red-verify.result.json`
8. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine\preformal-003-recorder-red-verify.result.sha256`
9. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery`
10. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery\machine`
11. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery\task-1-report.md`
12. `<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery\machine`

Validate strict UTF-8, one LF, closed recursive property order, duplicate rejection, canonical reserialization, exact byte count, and SHA-256 before creating formal/static/closure sources.

- [ ] **Step 2: Create the formal entry verifier**

Use exact interface:

```powershell
param(
    [Parameter(Mandatory)] [string] $InventoryPath,
    [Parameter(Mandatory)] [string] $ExpectedInventoryPath,
    [Parameter(Mandatory)] [long] $ExpectedInventoryByteCount,
    [Parameter(Mandatory)] [string] $ExpectedInventorySha256,
    [Parameter(Mandatory)] [string] $ScalarModulePath,
    [Parameter(Mandatory)] [string] $ExpectedScalarModulePath,
    [Parameter(Mandatory)] [long] $ExpectedScalarModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedScalarModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string] $ExpectedPlanCommit,
    [Parameter(Mandatory)] [string] $ExpectedDesignCommit,
    [Parameter(Mandatory)] [string] $ExpectedAmendmentCommit
)
```

Validate all root/nested JSON property orders and runtime types before use. Reconstruct inventory through explicit `Utf8JsonWriter` calls and compare exact bytes. All hashes use the plan-pinned pure-.NET `Get-A11FileSha256`; `Get-FileHash` is forbidden. For each of 24 files use this exact typed loop shape:

```powershell
$ExpectedByteCount = [long]$FileElement.GetProperty('byte_count').GetInt64()
$ExpectedSha256 = [string]$FileElement.GetProperty('sha256').GetString()
$ActualByteCount = [long](Get-Item -LiteralPath $ValidatedFilePath -Force).Length
$ActualSha256 = [string](Get-A11FileSha256 -Path $ValidatedFilePath)
$Record = Compare-A11ScalarIdentity -ActualByteCount $ActualByteCount -ExpectedByteCount $ExpectedByteCount -ActualSha256 $ActualSha256 -ExpectedSha256 $ExpectedSha256
if ($Record.identity_match.GetType() -ne [bool] -or -not [bool]$Record.identity_match) { throw 'preserved identity rejected' }
[void]$IdentityRecords.Add($Record)
```

Require exactly 24 comparator calls/records, workspace counts 4/8/5/4/3, all 12 absences, the exact v7 Boolean incident semantics, both executable-file identities without execution, exact plan/original-design/amendment lineage, and all four provider identities. Import only the exact PowerShell 7 Security manifest to prove command provenance and revalidate the six executable/provider signatures; never import a worker or start a parser. Require linked/canonical cleanliness, staging empty, and no write/process start. Sole PASS:

```text
ENTRYV8_FORMAL_PASS|workspaces=5|files=24|providers=2|v7=no_go_preserved|comparison=ordinal|writes=0
```

- [ ] **Step 3: Create the independent closure verifier**

Use exact interface:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('PreReport','Final')] [string] $Mode,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string] $InventoryPath,
    [Parameter(Mandatory)] [long] $ExpectedInventoryByteCount,
    [Parameter(Mandatory)] [string] $ExpectedInventorySha256,
    [Parameter(Mandatory)] [string] $ScalarModulePath,
    [Parameter(Mandatory)] [long] $ExpectedScalarModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedScalarModuleSha256,
    [Parameter(Mandatory)] [string] $FormalTerminal,
    [string] $ReportPath = '',
    [long] $ExpectedReportByteCount = -1,
    [string] $ExpectedReportSha256 = ''
)
```

It imports no scalar/identity/worker/controller/formal source. It imports only the exact PowerShell 7 Security manifest, proves exact provider-command provenance, and uses it to revalidate the two executables and four provider signatures. Independently reconstruct inventory, compare all 24 scalar pairs with explicit `Int64` and `StringComparer.Ordinal`, verify all 12 absences, executable/provider/original-design/amendment/Git facts, and write nothing. All hashes use pure .NET; `Get-FileHash` is forbidden.

`PreReport` requires empty report arguments, absent report, exact formal terminal, exactly 13 v8 files, and emits only:

```text
ENTRYV8_CLOSURE_PASS|workspaces=5|files=24|providers=2|formal=exact|writes=0
```

`Final` requires the exact ordinary report identity, exactly 14 v8 files, closed report sections/terminals, and emits only:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

- [ ] **Step 4: Create the static verifier**

Its interface requires `WorkspacePath` plus explicit actual/expected path, byte-count, and SHA-256 quartets for parser test/RED/GREEN, worker, controller, scalar test/RED/GREEN, inventory, formal verifier, and closure verifier. No parameter is optional.

Parse every complete PowerShell source. AST/type-flow checks require:

- exact public parameters, module exports, and result property orders;
- parser identity type checks before field comparison and the exact spoof-rejection behavior terminal;
- only the two literal executable paths can flow to `ProcessStartInfo.FileName`;
- exactly one `Start()` AST call site inside an exact two-record fixed role loop, exactly two runtime starts on PASS, and no retry/fallback/sleep/kill;
- the closed pure-.NET digest helper and zero `Get-FileHash` tokens in worker/controller;
- exactly two `Import-Module` AST call sites in the worker: the role-selected literal Security manifest, then the exact parser-identity GREEN module;
- provider selection only from the closed runtime role, with no module name, `PSModulePath`, gallery, wildcard, relative path, fallback, or second candidate;
- provider byte/hash/version/link validation before import, exact module/nested-DLL/command provenance after import, then exactly three worker Authenticode calls;
- executable and provider signature acceptance before GREEN import and before the first parser API call;
- worker self-attestation and GREEN comparator acceptance before its first `Parser.ParseFile` call;
- exact HardLink exception and zero reparse acceptance elsewhere;
- sorted strict target manifest parsing with exact path/byte/hash validation;
- scalar runtime type checks before comparison and exactly one production `StringComparer.Ordinal.Equals` digest comparison;
- 24 formal comparator calls/records and independent closure comparison;
- explicit canonical JSON reconstruction including the exact Security-provider overlay and no dynamic serializer; and
- zero write, dot-source, dynamic evaluation, shell string, redirection, transcript, sidecar, machine, predecessor invocation, auto-loading, reflection, P/Invoke, `Add-Type`, Docker/GPU/A11/product/Git-mutation/network/unapproved-external-runtime/`OwnerAuthorizationId` flow.

Sole PASS:

```text
ENTRYV8_STATIC_PASS|parser_roles=bound|providers=2|scalar=ordinal|files=24|writes=0|retries=0
```

- [ ] **Step 5: Run the `static` dual-parser phase exactly once**

Freeze all 13 pre-report v8 file identities. Build the sorted base64 parser-target manifest from exactly the 12 PowerShell files, excluding only `task-1-preserved-inventory-v8.json`; the controller still snapshots and proves all 13 workspace identities before and after each child. Run the controller once in `Static` mode. Require exit 0, empty stderr, exactly two starts, no inventory change, and sole stdout:

```text
ENTRYV8_DUAL_PARSER_PASS|phase=static|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
```

Any difference is `ENTRYV8_DUAL_PARSER_UNPROVABLE / NO_GO`; never run static or formal entry.

- [ ] **Step 6: Run static admission exactly once**

Run the frozen static verifier through exact PowerShell 7 with every literal identity argument. Require exit 0, empty stderr, unchanged 13-file inventory, and sole stdout:

```text
ENTRYV8_STATIC_PASS|parser_roles=bound|providers=2|scalar=ordinal|files=24|writes=0|retries=0
```

Any difference is `ENTRYV8_STATIC_REJECTED / NO_GO`; preserve and stop before formal entry.

---

### Task 4: Execute one formal entry and publish immutable closure

**Files:**
- Read only before report: the 13 frozen v8 files, 24 preserved files, 12 absent paths, two executable files, four provider files, and Git state.
- Create after exact pre-report closure: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/task-1-report.md`

**Interfaces:**
- Consumes: exact static PASS and every frozen formal input.
- Produces: one formal PASS, one pre-report closure PASS, one immutable report, and final entry-verifier-only PASS or the first preserved NO_GO.

- [ ] **Step 1: Freeze the formal command identity without executing it**

Print literal actual/expected inventory and scalar-module identities, plan/original-design/amendment commits, workspace path, exact formal argv, and current 13-file inventory. Require report/machine absent, v7 exact four-file NO_GO, all 24 preserved files, four provider files, and 12 absences exact, both executable files exact without execution, linked/canonical clean, HEAD still this plan commit, and staging empty.

- [ ] **Step 2: Run formal entry exactly once**

Invoke frozen PowerShell 7 with `task-1-entry-verifier-v8.ps1` and the frozen literal argv. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRYV8_FORMAL_PASS|workspaces=5|files=24|providers=2|v7=no_go_preserved|comparison=ordinal|writes=0
```

Any output, exit, exception, count, type, identity, absence, Git, signature, or side-effect difference is `ENTRYV8_RECOVERY_UNPROVABLE / NO_GO`. Preserve and stop; never rerun formal or change a consumed input.

- [ ] **Step 3: Run pre-report closure exactly once**

Invoke closure in `PreReport` mode with the frozen inventory/scalar identities, literal exact formal terminal, empty report path/hash fields, and v8 workspace. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRYV8_CLOSURE_PASS|workspaces=5|files=24|providers=2|formal=exact|writes=0
```

Any difference is `ENTRYV8_RECOVERY_UNPROVABLE / NO_GO`; stop without report creation.

- [ ] **Step 4: Create the final report once with `apply_patch`**

Record literal original-design/amendment/plan commits and blobs; linked-worktree topology; authority; exact v7 plan/design/workspace/four-file identities and preserved NO_GO semantics; exact executable policies including the closed System32 HardLink; all four provider identities, closed Windows provider HardLinks, import/command provenance, and signature observations; Stage 0 identity/result; parser-policy test/RED/GREEN identities and terminals; all three dual-parser phase target identities and provider-bearing terminals; scalar test/RED/GREEN identities and terminals; inventory bytes/hash/property orders; static/formal/closure source identities and terminals; all 24 actual/expected records; all 12 absence records; 14-file final v8 inventory; and prohibited-action non-occurrence.

The report contains the exact final terminal once in a fenced evidence section. Its presence is not PASS until final closure emits it. Never edit the report after creation.

- [ ] **Step 5: Run final closure exactly once**

Freeze the report byte count/SHA-256 and invoke closure in `Final` with literal exact inventory/scalar/report/formal identities. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Any contradiction, omission, output difference, or state change is `ENTRYV8_RECOVERY_UNPROVABLE / NO_GO`; never repair or rerun report/closure.

- [ ] **Step 6: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/untracked non-ignored status and staging are empty; the v8 namespace contains exactly the 14 file-map entries and no other child; v7 remains the exact four-file NO_GO with report/machine absent; the 20 older records and 12 absences remain exact; canonical worktree is clean; both executable files and all four provider files remain exact; and no Docker/GPU/A11/product/model/runtime/owner/network or external action occurred.

Stop. A later separately approved design/plan may consume the final PASS. Do not resume v7 or the consumed v6 child-exit plan.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve v7 procedure failure without retroactive PASS | Global Constraints; Task 1 Step 1; Task 3 Step 1; Task 4 Steps 1-6 |
| Exact executable identities and HardLink exception | Global Constraints; Task 1 Step 1; Task 2 Steps 1-2; Task 3 Steps 1-6 |
| Exact role-specific Security providers and closed provider HardLinks | Global Constraints; Task 1 Steps 1-3; Task 2 Steps 1-6; Task 3 Steps 1-6; Task 4 Steps 1-6 |
| Explicit provider import/provenance and exactly three worker signature calls | Global Constraints; Task 2 Steps 1-2 and 5; Task 3 Steps 4-6 |
| Pure .NET hashes and no worker/controller `Get-FileHash` | Global Constraints; Task 1 Steps 1-3; Task 2 Steps 1-6; Task 3 Steps 2-6 |
| Negative caller-role spoof behavior | Task 1 Steps 2-5 |
| Child process self-attestation before parsing | Task 2 Steps 1-2 and 5; Task 3 Steps 4-5 |
| Exactly two absolute process starts, no lookup/retry | Task 2 Steps 1-2 and 5; Task 3 Steps 4-5 |
| Fresh scalar RED/GREEN, no v7 execution | Task 2 Steps 1-6 |
| Canonical five-workspace/24-file/12-absence inventory | Task 3 Steps 1-4 |
| Static admission before formal entry | Task 3 Steps 4-6 |
| One read-only formal entry | Task 4 Steps 1-2 |
| Independent pre-report and final closure | Task 3 Step 3; Task 4 Steps 3-5 |
| Exactly 13 then 14 v8 files and zero machine files | File Map; Task 3 Steps 5-6; Task 4 Steps 1-6 |
| Final PASS stops before child-exit recovery | Global Constraints; Task 4 Steps 5-6 |
| No Docker/GPU/A11/runtime/OwnerAuthorizationId | Global Constraints; Task 3 Step 4; Task 4 Step 6 |

## Plan Completion Gate

Before committing this plan, require all of the following without executing Stage 0 or creating the v8 workspace:

1. this plan is the only changed path and will be a direct-child commit of amendment `5d7500abef12ff724d0fb9c256a1894979bd8677`, whose direct parent is original design `0788f6143691d5a39730fb06508be3949de1b3f0`;
2. the original design blob is exactly `a837d94d58d8ad2ee1c71fd51de64257fe49d060` and the amendment blob is exactly `20661c3572d8723d7c52c4d745703a5f7741b8dd`;
3. author, committer, subject, branch, linked topology, clean linked/canonical status, and empty staging are exact;
4. the plan has no unresolved marker, conflict marker, vague error case, undefined interface, or source/property/type name mismatch;
5. the 14-file map, 13-file pre-report count, 24 preserved records, four provider dependencies grouped into two provider records, five workspace counts, and 12 absences are arithmetically consistent;
6. every design requirement maps to a coverage row;
7. every complete PowerShell block parses under frozen PowerShell 7.6.4 and the explicit Windows PowerShell 5.1 parser API; each parser process first reports its real path, version, and edition, and neither report is accepted from a caller label alone;
8. the exact Stage 0 block above is 14,198 LF/UTF-8 bytes with SHA-256 `5c9de5a85ae6e90fa5d4bd23c7e8f7fc49061a85d2f3c55a39524d9f48b19c70`, and the five parser-policy/worker/controller block identities equal the plan-pinned table;
9. both executable files and all four provider files, signatures, signer identities, versions, link policies, parent chains, module provenance, and allowed commands are exact; v7 remains exactly four files; v8 and consumed v6 workspaces remain absent; and
10. plan authoring executed no Stage 0, v7 source, RED, GREEN, worker, controller, static, formal, closure, Docker, GPU, A11, product, model, network, or external-runtime command; the only child processes were the explicitly pinned no-profile parser/provider authoring checks required by item 7, and they parsed plan strings without executing them.
