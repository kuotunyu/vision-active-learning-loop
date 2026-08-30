# Wave 0 A11 PowerShell Launcher Identity Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before every terminal or commit claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the consumed hard-coded PowerShell launcher with a dynamically discovered, signed, frozen, and self-attested executable identity, then execute the already approved WDDM type-aware A11 recovery only after a fresh complete entry gate passes.

**Architecture:** A current-shell discovery helper resolves the controller executable and default `pwsh` application independently, emits one closed canonical identity, and admits only PowerShell 7.6.4 signed by Microsoft with no reparse point. That exact path and binary identity are frozen into every permitted child command; controller revalidation and child self-attestation must match before the inherited preservation, WDDM XML, CPU, implementation, review, and dependency-diagnostic gates may run.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`, `System.Text.Json`, Authenticode, and SHA-256; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery-design.md` at commit `3e98d1d56caede9a1baaf215da4e418112a73643`, blob `8ab38e23b67c2f251c349b444cfe86650f40ce85`.
- This plan commit must be the direct child of that design commit and add only this plan file.
- The WDDM recovery plan remains immutable at commit `42c200d8a801b142cde394cda7a0520bd9c30a83`, blob `2abcc051d50921a59f58a57b2814e2a5e47dcc59`.
- The WDDM recovery design remains immutable at commit `0053a8b30c8639ea9b9752ca2171117692fe78b0`, blob `124b87aa9b2a04b3830aa85e5c45a4cfde87b260`.
- The CUDA-observability plan/design, ordering plan/design, digest plan/design, diagnostic-root erratum, and runtime-transport plan/design remain immutable at `f45d84eec13b98ee4566497252375f20251fd2d3`, `5451c50cc20b1c297c9bdd3535a793eff993158d`, `52fe25d529f7d64e986864576653d0d14a6e484b`, `68f51519d2cb480200ca4fef740651b0d15dd76f`, `03115325f36da31b135b4593fb8df1689eac9a35`, `2db13d302da97a241daeaba3578cd9cec1c8073b`, `101bb79369399cc3947f1c667f0a11988f916638`, `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, and `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`.
- Preserve the consumed hard-coded launcher terminal exactly as `CUDA_OBSERVATION_UNPROVABLE / NO_GO`. Its ignored entry script remains 42,541 bytes with SHA-256 `1dafe50f2073eed8955a01fe8ed59bcc2f1554f4ea0504a4575b0071a627fe65`; its report remains 45,245 bytes with SHA-256 `11ca424b816ec013261b7227a2e18e3e4fb658b58b7c90a10b943e55ed439e11`.
- Never run, modify, copy, rename, delete, or use the consumed entry script as the new command source. Reconstruct the new entry script only from committed plan blobs and this plan's identity preamble.
- The new ignored workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery`. It must not exist before Task 1 starts. If it already exists, preserve it and stop; do not delete or reuse it.
- The implementation must be one append-only commit, the direct child of this plan commit, changing exactly the seven implementation paths listed below. Tasks 1-5 create no commits.
- Author and committer for the plan and implementation commits must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean evidence, push, merge, tag, release, or modify another repository.
- The artifact root `D:\vision-active-learning-loop-artifacts\wave0` is read-only. A mismatch is a stop condition, never a repair instruction.
- The launcher identity must be discovered once from the current controller shell. A failed discovery, policy decision, revalidation, or child start may not select another executable or repeat the command.
- Controller process path and default `Get-Command pwsh -CommandType Application` source must resolve to the same canonical local file.
- Admit only `pwsh.exe`, PowerShell `7.6.4`, file version `7.6.4.*`, a positive byte count, lowercase 64-character SHA-256, `Valid` Authenticode, exact Microsoft Corporation signer subject, a 40-character uppercase signer thumbprint, and empty executable/parent `LinkType` values.
- The host snapshot in the design proves feasibility but is not fresh Task 1 evidence. Observe and freeze a new identity; do not blindly reuse the snapshot path, digest, size, version, or thumbprint.
- Freeze one accepted canonical identity for the complete plan sequence. Every later PowerShell child script must embed that identity, revalidate the same executable before launch, and self-attest before its substantive command. Identity drift stops the sequence; do not rediscover a replacement.
- The only launcher terminals are `POWERSHELL_LAUNCHER_IDENTITY_PASS`, `POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO`, and `POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO`.
- During Task 1, no Git, Docker, artifact, image, lease, historical, CPU, or GPU action may precede child self-attestation. Controller-side read-only lineage and clean-scope checks precede discovery only to establish repository entry eligibility.
- Never terminate, pause, signal, reprioritize, whitelist by name, or otherwise mutate an observed GPU process. Do not use `Stop-Process`, `taskkill`, service control, Docker stop, WSL shutdown, Task Manager automation, GPU reset, driver-model changes, or an equivalent action.
- Each scheduled CUDA observation starts exactly one `nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63` native process. Do not retry, substitute, use another output format, wrap in a pipeline, add a replacement timeout, or infer PASS from absent output.
- Only zero process rows or rows whose exact type is exclusively `G` may pass. `C`, `M`, `C+G`, `M+C`, `O`, missing type, unknown type, unsafe XML, or an unprovable result is `NO_GO`.
- PID, process name, parent PID, executable vendor, and `used_memory` are evidence only and never change GPU admission.
- Do not invoke `scripts/run_wave0_a11.ps1`, generate or guess an `OwnerAuthorizationId`, acquire a formal GPU lease, initialize a model, create a calibration or validation runtime identity, access RDD, or start Wave 1.
- Consumed owners `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` remain immutable evidence. Test-only owner values must contain `TEST`.
- The only Docker invocation permitted to execute a stage is the single dependency-only diagnostic in Task 7. Tasks 5-6 may call `docker buildx build --check`, which validates without executing or exporting a stage.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` byte-identical at SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.
- Keep model, receipt, statistical, threshold, replica, split, acquisition, data-firewall, lease, validation, and Wave 1 contracts unchanged.
- CPU tests set `PYTHONDONTWRITEBYTECODE=1` and pass `-p no:cacheprovider`; they may not use network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The dependency diagnostic writes only beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`, outside the repository and artifact baseline. It has no owner ID, run ID, image export, project container, model process, or statistical meaning.
- Create or edit every ignored command/report file with `apply_patch`. Do not use shell redirection, `Set-Content`, `Out-File`, Python file writes, or another command-generation shortcut.
- Every nontrivial gate command is materialized before execution. Record its literal payload, complete source bytes, UTF-8 byte count/SHA-256, argv, tool result, exit code, output, session ID, chunk ID, and every same-session poll. Never reconstruct a missing payload after execution.

## Normative Overlay

The complete WDDM recovery plan at commit
`42c200d8a801b142cde394cda7a0520bd9c30a83` and Git blob
`2abcc051d50921a59f58a57b2814e2a5e47dcc59` is incorporated by immutable
reference. Line numbers below are one-based lines in that exact 1,013-line blob.

Verify the immutable parent documents before authoring any command evidence:

```powershell
$PriorPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery-design.md'
if ((git rev-parse "42c200d8a801b142cde394cda7a0520bd9c30a83`:$PriorPlanPath").Trim() -cne
    '2abcc051d50921a59f58a57b2814e2a5e47dcc59') {
    throw 'immutable WDDM plan blob mismatch'
}
if ((git rev-parse "3e98d1d56caede9a1baaf215da4e418112a73643`:$DesignPath").Trim() -cne
    '8ab38e23b67c2f251c349b444cfe86650f40ce85') {
    throw 'approved launcher identity design blob mismatch'
}
```

These are the only replacements:

| Contract | Superseded | Effective |
| --- | --- | --- |
| Implementation parent | WDDM plan `42c200d8...` | this plan commit |
| Implementation grandparent | WDDM design `0053a8b...` | launcher-identity design `3e98d1d...` |
| Task 1 | WDDM-plan lines 112-662 and its consumed payload | Task 1 below |
| Task 6 lineage/command launch | WDDM-plan lines 837-927 | Task 6 below |
| Task 7 lineage/command launch | WDDM-plan lines 928-1013 | Task 7 below |

WDDM-plan Tasks 2-5 remain byte-for-byte normative:

| Inherited task | Exact WDDM-plan lines |
| --- | ---: |
| Task 2 | 663-759 |
| Task 3 | 760-816 |
| Task 4 | 817-826 |
| Task 5 | 827-836 |

Within the new Task 1, WDDM-plan lines 112-601 define the complete Git,
preservation, XML, synthetic, Docker, image, lease, and historical gate source.
Re-materialize those requirements from the committed plan blob; do not read the
consumed ignored script. Insert the identity preamble defined below before every
substantive action. The old hard-coded freeze at lines 603-614 is superseded and
must not appear in any new command.

## Frozen Preservation Envelope

The exact five run records, algorithms, counts, digests, image tags/IDs,
lease-history hashes, historical baselines, attempt-5 vector, and latest-write
values in WDDM-plan lines 81-96 remain binding. The entry gate must reproduce:

```text
attempt 1  v1  48 files / 18 dirs / fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b
attempt 2  v1   5 files /  5 dirs / 8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b
attempt 3  v1  60 files / 18 dirs / 628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2
attempt 4  v1 137 files / 30 dirs / f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717
attempt 5  v2  10 files /  5 dirs / e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
attempt-1 v2 negative digest / 72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c
historical files 64,306 / e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
historical images 21 / 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
```

## Implementation File Map and Allowlist

- Create `configs/a11/preserved-attempts.json`: five immutable declarative records with one exact `run_inventory_algorithm` each.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 registry schema including the two-value algorithm enum.
- Create `scripts/run_uv_sync_with_retries.py`: bounded dependency-build-only transport wrapper.
- Modify `scripts/run_wave0_a11.ps1`: secure WDDM XML decoder, pure process-type classifier, single-invocation observer, version-aware inventory, registry loader/verifier, byte guard, and unchanged single-build campaign path.
- Modify `docker/wave0.Dockerfile`: dependency stage, exact wrapper calls, and two locked BuildKit uv cache mounts.
- Modify `tests/gates/test_wave0_a11_launcher.py`: XML security/type/observer integration, ordering, vector, registry, verifier, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change. Launcher-identity helpers are ignored evidence
only and must not be added to production code.

---

### Task 1: Prove launcher identity and execute one fresh complete entry gate

**Files:**
- Modify tracked files: none
- Create ignored evidence: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-launcher-identity.ps1`
- Create ignored evidence: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-entry-launcher-revalidate.ps1`
- Create ignored evidence: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-entry-gate.ps1`
- Create ignored evidence only after GPU PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-cpu-launcher-revalidate.ps1`
- Create ignored evidence only after GPU PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-cpu-baseline.ps1`
- Create ignored report: `.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/task-1-report.md`
- Read: committed recovery lineage, consumed evidence digests, controller PowerShell identity, all inherited preservation inputs, and one live WDDM XML observation

**Interfaces:**
- Consumes: this plan commit, design `3e98d1d56caede9a1baaf215da4e418112a73643`, WDDM plan blob `2abcc051d50921a59f58a57b2814e2a5e47dcc59`, and the immutable preservation envelope
- Produces: one frozen launcher identity plus `ENTRY_GATE_PASS` or the first exact `NO_GO`
- Evidence-only functions: `Assert-A11ClosedProperties(Value, ExpectedNames, Label)`, `ConvertTo-A11PowerShellIdentity(Value)`, `ConvertTo-A11PowerShellIdentityJson(Value)`, `ConvertFrom-A11PowerShellIdentityJson(Json)`, `Compare-A11PowerShellIdentity(Expected, Observed)`, `Get-A11PowerShellFileIdentity(Path, PowerShellVersion)`, `Test-A11PowerShellIdentityPolicy(ProcessPath, CommandPath, Identity)`, `Get-A11ControllerPowerShellDiscovery([FileIdentityReader])`
- Inherited WDDM functions: `Get-A11XmlSingleText`, `ConvertFrom-A11NvidiaSmiXml`, `ConvertTo-A11GpuAdmission`, `Get-A11Utf8StreamRecord`, `ConvertTo-A11GpuObservationCore`, `Invoke-A11GpuObservation`

- [ ] **Step 1: Prove exact entry state before creating the new workspace**

Run read-only Git and filesystem checks from the linked worktree. Require the
current branch to be `codex/wave0-model-contract`; `git rev-parse HEAD^` to equal
`3e98d1d56caede9a1baaf215da4e418112a73643`; the plan commit to change exactly
this plan path; plan author and committer to equal the required identity; Git
status and staging to be empty; and `git rev-parse --git-dir` to differ from
`git rev-parse --git-common-dir`.

Require both consumed evidence files to exist with their exact byte counts and
digests from Global Constraints. Require the new SDD workspace to be absent.
Require each intended new evidence path to be ignored by the repository's
`.superpowers/sdd/.gitignore` rule before creating its parent directory. Do not
run `nvidia-smi`, Docker, CPU tests, or read the artifact root in this step.

- [ ] **Step 2: Define the exact closed launcher identity helpers**

Use `apply_patch` to place the following function block in
`task-1-launcher-identity.ps1`, both uniquely named Task 1 revalidation scripts,
and at the top of both Task 1 child scripts. Later scripts must copy this block
exactly; do not create a tracked or shared helper file.

```powershell
$script:A11IdentityNames = @(
    'canonical_path',
    'byte_count',
    'sha256',
    'powershell_version',
    'file_version',
    'product_version',
    'signature_status',
    'signer_subject',
    'signer_thumbprint',
    'file_link_type',
    'parent_chain_link_types'
)
$script:A11ParentLinkNames = @('path', 'link_type')
$script:A11MicrosoftSigner =
    'CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US'

function Assert-A11ClosedProperties {
    param(
        [Parameter(Mandatory = $true)] [object] $Value,
        [Parameter(Mandatory = $true)] [string[]] $ExpectedNames,
        [Parameter(Mandatory = $true)] [string] $Label
    )
    if ($null -eq $Value) { throw "$Label is null" }
    $ActualNames = @($Value.PSObject.Properties.Name)
    if ($ActualNames.Count -ne $ExpectedNames.Count) {
        throw "$Label property count mismatch"
    }
    for ($Index = 0; $Index -lt $ExpectedNames.Count; $Index++) {
        if ($ActualNames[$Index] -cne $ExpectedNames[$Index]) {
            throw "$Label property order mismatch at $Index"
        }
    }
}

function ConvertTo-A11PowerShellIdentity {
    param([Parameter(Mandatory = $true)] [object] $Value)
    Assert-A11ClosedProperties -Value $Value `
        -ExpectedNames $script:A11IdentityNames -Label 'launcher identity'
    foreach ($Name in @(
        'canonical_path', 'sha256', 'powershell_version', 'file_version',
        'product_version', 'signature_status', 'signer_subject',
        'signer_thumbprint', 'file_link_type'
    )) {
        if ($Value.$Name -isnot [string]) {
            throw "launcher identity $Name must be string"
        }
    }
    if ($Value.byte_count -isnot [long] -or $Value.byte_count -le 0) {
        throw 'launcher identity byte_count must be positive Int64'
    }
    $Parents = @($Value.parent_chain_link_types)
    if ($Parents.Count -eq 0) { throw 'launcher identity parent chain is empty' }
    $ClosedParents = @()
    foreach ($Parent in $Parents) {
        Assert-A11ClosedProperties -Value $Parent `
            -ExpectedNames $script:A11ParentLinkNames -Label 'launcher parent link'
        if ($Parent.path -isnot [string] -or $Parent.link_type -isnot [string]) {
            throw 'launcher parent link fields must be strings'
        }
        $ClosedParents += [pscustomobject][ordered]@{
            path = $Parent.path
            link_type = $Parent.link_type
        }
    }
    [pscustomobject][ordered]@{
        canonical_path = $Value.canonical_path
        byte_count = [long]$Value.byte_count
        sha256 = $Value.sha256
        powershell_version = $Value.powershell_version
        file_version = $Value.file_version
        product_version = $Value.product_version
        signature_status = $Value.signature_status
        signer_subject = $Value.signer_subject
        signer_thumbprint = $Value.signer_thumbprint
        file_link_type = $Value.file_link_type
        parent_chain_link_types = @($ClosedParents)
    }
}

function ConvertTo-A11PowerShellIdentityJson {
    param([Parameter(Mandatory = $true)] [object] $Value)
    $Closed = ConvertTo-A11PowerShellIdentity -Value $Value
    $Closed | ConvertTo-Json -Depth 8 -Compress
}

function ConvertFrom-A11PowerShellIdentityJson {
    param([Parameter(Mandatory = $true)] [string] $Json)
    $Document = [System.Text.Json.JsonDocument]::Parse($Json)
    try {
        if ($Document.RootElement.ValueKind -ne
            [System.Text.Json.JsonValueKind]::Object) {
            throw 'launcher identity JSON root must be object'
        }
        $RootNames = @($Document.RootElement.EnumerateObject() |
            ForEach-Object { $_.Name })
        if ($RootNames.Count -ne $script:A11IdentityNames.Count) {
            throw 'launcher identity JSON root count mismatch'
        }
        for ($Index = 0; $Index -lt $RootNames.Count; $Index++) {
            if ($RootNames[$Index] -cne $script:A11IdentityNames[$Index]) {
                throw "launcher identity JSON root order mismatch at $Index"
            }
        }
        $ParentElement = $Document.RootElement.GetProperty(
            'parent_chain_link_types'
        )
        if ($ParentElement.ValueKind -ne
            [System.Text.Json.JsonValueKind]::Array) {
            throw 'launcher parent chain JSON must be array'
        }
        foreach ($ParentElementItem in $ParentElement.EnumerateArray()) {
            if ($ParentElementItem.ValueKind -ne
                [System.Text.Json.JsonValueKind]::Object) {
                throw 'launcher parent link JSON must be object'
            }
            $ParentNames = @($ParentElementItem.EnumerateObject() |
                ForEach-Object { $_.Name })
            if ($ParentNames.Count -ne $script:A11ParentLinkNames.Count) {
                throw 'launcher parent link JSON count mismatch'
            }
            for ($Index = 0; $Index -lt $ParentNames.Count; $Index++) {
                if ($ParentNames[$Index] -cne $script:A11ParentLinkNames[$Index]) {
                    throw "launcher parent link JSON order mismatch at $Index"
                }
            }
        }
    } finally {
        $Document.Dispose()
    }
    $Value = $Json | ConvertFrom-Json
    $Canonical = ConvertTo-A11PowerShellIdentityJson -Value $Value
    if ($Canonical -cne $Json) { throw 'launcher identity JSON is not canonical' }
    ConvertTo-A11PowerShellIdentity -Value $Value
}

function Compare-A11PowerShellIdentity {
    param(
        [Parameter(Mandatory = $true)] [object] $Expected,
        [Parameter(Mandatory = $true)] [object] $Observed
    )
    try {
        $ExpectedJson = ConvertTo-A11PowerShellIdentityJson -Value $Expected
        $ObservedJson = ConvertTo-A11PowerShellIdentityJson -Value $Observed
    } catch {
        return [pscustomobject][ordered]@{
            terminal = 'POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO'
            reason = $_.Exception.Message
            expected_json = ''
            observed_json = ''
        }
    }
    $Terminal = if ($ExpectedJson -ceq $ObservedJson) {
        'POWERSHELL_LAUNCHER_IDENTITY_PASS'
    } else {
        'POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO'
    }
    [pscustomobject][ordered]@{
        terminal = $Terminal
        reason = if ($Terminal -ceq 'POWERSHELL_LAUNCHER_IDENTITY_PASS') {
            'exact-identity-match'
        } else {
            'exact-identity-mismatch'
        }
        expected_json = $ExpectedJson
        observed_json = $ObservedJson
    }
}

function Get-A11PowerShellFileIdentity {
    param(
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] [string] $PowerShellVersion
    )
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or
        $Path.StartsWith('\\', [StringComparison]::Ordinal)) {
        throw 'launcher path must be fully qualified local path'
    }
    $Resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
    if ($Resolved.Provider.Name -cne 'FileSystem') {
        throw 'launcher path provider mismatch'
    }
    $Item = Get-Item -LiteralPath $Resolved.Path -Force -ErrorAction Stop
    if ($Item -isnot [IO.FileInfo]) { throw 'launcher path is not a file' }
    $FileLinkType = if ($null -eq $Item.LinkType) {
        ''
    } else {
        [string]$Item.LinkType
    }
    $ParentLinks = @()
    $Parent = $Item.Directory
    while ($null -ne $Parent) {
        $ParentLinks += [pscustomobject][ordered]@{
            path = $Parent.FullName
            link_type = if ($null -eq $Parent.LinkType) {
                ''
            } else {
                [string]$Parent.LinkType
            }
        }
        if ($Parent.FullName -ceq $Parent.Root.FullName) { break }
        $Parent = $Parent.Parent
    }
    $Signature = Get-AuthenticodeSignature -LiteralPath $Item.FullName
    $FileHash = Get-FileHash -LiteralPath $Item.FullName -Algorithm SHA256
    [pscustomobject][ordered]@{
        canonical_path = $Item.FullName
        byte_count = [long]$Item.Length
        sha256 = $FileHash.Hash.ToLowerInvariant()
        powershell_version = $PowerShellVersion
        file_version = [string]$Item.VersionInfo.FileVersion
        product_version = [string]$Item.VersionInfo.ProductVersion
        signature_status = [string]$Signature.Status
        signer_subject = if ($null -eq $Signature.SignerCertificate) {
            ''
        } else {
            [string]$Signature.SignerCertificate.Subject
        }
        signer_thumbprint = if ($null -eq $Signature.SignerCertificate) {
            ''
        } else {
            [string]$Signature.SignerCertificate.Thumbprint
        }
        file_link_type = $FileLinkType
        parent_chain_link_types = @($ParentLinks)
    }
}

function Test-A11PowerShellIdentityPolicy {
    param(
        [Parameter(Mandatory = $true)] [string] $ProcessPath,
        [Parameter(Mandatory = $true)] [string] $CommandPath,
        [Parameter(Mandatory = $true)] [object] $Identity
    )
    $Closed = ConvertTo-A11PowerShellIdentity -Value $Identity
    $Reasons = @()
    if ($ProcessPath -cne $CommandPath -or
        $ProcessPath -cne $Closed.canonical_path) {
        $Reasons += 'controller-path-disagreement'
    }
    if ([IO.Path]::GetFileName($Closed.canonical_path) -cne 'pwsh.exe') {
        $Reasons += 'launcher-filename-mismatch'
    }
    if ($Closed.powershell_version -cne '7.6.4') {
        $Reasons += 'powershell-version-mismatch'
    }
    if ($Closed.file_version -cnotmatch '^7\.6\.4\.\d+$') {
        $Reasons += 'file-version-mismatch'
    }
    if ($Closed.product_version.Length -eq 0) {
        $Reasons += 'product-version-missing'
    }
    if ($Closed.sha256 -cnotmatch '^[0-9a-f]{64}$') {
        $Reasons += 'sha256-shape-mismatch'
    }
    if ($Closed.signature_status -cne 'Valid') {
        $Reasons += 'signature-invalid'
    }
    if ($Closed.signer_subject -cne $script:A11MicrosoftSigner) {
        $Reasons += 'signer-subject-mismatch'
    }
    if ($Closed.signer_thumbprint -cnotmatch '^[0-9A-F]{40}$') {
        $Reasons += 'signer-thumbprint-shape-mismatch'
    }
    if ($Closed.file_link_type.Length -ne 0) {
        $Reasons += 'launcher-reparse-point'
    }
    foreach ($ParentLink in @($Closed.parent_chain_link_types)) {
        if ($ParentLink.link_type.Length -ne 0) {
            $Reasons += "parent-reparse-point:$($ParentLink.path)"
        }
    }
    [pscustomobject][ordered]@{
        passed = ($Reasons.Count -eq 0)
        reasons = @($Reasons)
    }
}

function Get-A11ControllerPowerShellDiscovery {
    param(
        [scriptblock] $FileIdentityReader = {
            param($Path, $Version)
            Get-A11PowerShellFileIdentity -Path $Path `
                -PowerShellVersion $Version
        }
    )
    $ControllerProcess = Get-Process -Id $PID -ErrorAction Stop
    $ProcessPath = (Resolve-Path -LiteralPath $ControllerProcess.Path).Path
    $Command = Get-Command pwsh -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    $CommandPath = (Resolve-Path -LiteralPath $Command.Source).Path
    $PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    $Identity = & $FileIdentityReader $ProcessPath $PowerShellVersion
    $Closed = ConvertTo-A11PowerShellIdentity -Value $Identity
    $Policy = Test-A11PowerShellIdentityPolicy -ProcessPath $ProcessPath `
        -CommandPath $CommandPath -Identity $Closed
    [pscustomobject][ordered]@{
        schema_version = 1
        process_path = $ProcessPath
        command_path = $CommandPath
        identity = $Closed
        policy_passed = [bool]$Policy.passed
        policy_reasons = @($Policy.reasons)
        terminal = if ($Policy.passed) {
            'POWERSHELL_LAUNCHER_IDENTITY_PASS'
        } else {
            'POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO'
        }
    }
}
```

- [ ] **Step 3: Add synthetic identity and static safety checks before host discovery**

In `task-1-launcher-identity.ps1`, define one valid closed synthetic identity
with `[long]1` byte count, exact property order, an uppercase 40-character
thumbprint, empty link types, and one local-root parent record. Require
`Compare-A11PowerShellIdentity` to return PASS for an exact clone. Mutate each of
the eleven root fields separately and require identity mismatch. Add one extra
root property, remove `product_version`, make `byte_count` a string, add a
duplicate `sha256` key to raw JSON, reorder root keys, add an extra parent key,
and make the parent chain empty; require each malformed case to be unprovable.

Inject a `FileIdentityReader` that increments `$script:IdentityReadCount` and
returns the valid synthetic identity with its canonical path replaced by the
real controller process path. Call `Get-A11ControllerPowerShellDiscovery` once
and require `$script:IdentityReadCount -eq 1`. This injected result may fail
policy for synthetic metadata; only the exact call count is asserted.

Parse all three complete helper scripts under PowerShell 7 and the Windows
PowerShell 5.1 parser. Static-scan the identity and revalidation scripts and
require absence of `nvidia-smi`, `docker`, `uv`, artifact roots, network tools,
`Start-Sleep`, loops around an invocation, process mutation, service control,
shell installation, file copying, PATH assignment, and more than one call to the
identity reader.

- [ ] **Step 4: Freeze and execute current-shell identity discovery exactly once**

Append production discovery to `task-1-launcher-identity.ps1`. It must emit one
compact wrapper containing the discovery object, canonical identity JSON, UTF-8
byte count, and SHA-256 before throwing on a non-PASS terminal. Catch any failure
that occurs before a closed discovery object and emit
`POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO` with exception type/message.

After the synthetic checks, append this exact production body:

```powershell
$script:IdentityReadCount = 0
$ProductionIdentityReader = {
    param($Path, $Version)
    $script:IdentityReadCount++
    Get-A11PowerShellFileIdentity -Path $Path -PowerShellVersion $Version
}
try {
    $Discovery = Get-A11ControllerPowerShellDiscovery `
        -FileIdentityReader $ProductionIdentityReader
    if ($script:IdentityReadCount -ne 1) {
        throw 'production identity reader count mismatch'
    }
} catch {
    [pscustomobject][ordered]@{
        schema_version = 1
        identity_read_count = $script:IdentityReadCount
        error_type = $_.Exception.GetType().FullName
        error_message = $_.Exception.Message
        terminal = 'POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO'
    } | ConvertTo-Json -Depth 8 -Compress | Write-Output
    throw 'POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO'
}
$IdentityJson = ConvertTo-A11PowerShellIdentityJson `
    -Value $Discovery.identity
$IdentityBytes = [Text.UTF8Encoding]::new($false).GetBytes($IdentityJson)
$IdentityHasher = [Security.Cryptography.SHA256]::Create()
try {
    $IdentitySha256 = (($IdentityHasher.ComputeHash($IdentityBytes) |
        ForEach-Object { $_.ToString('x2') }) -join '')
} finally {
    $IdentityHasher.Dispose()
}
[pscustomobject][ordered]@{
    schema_version = 1
    identity_read_count = $script:IdentityReadCount
    discovery = $Discovery
    identity_canonical_json = $IdentityJson
    identity_utf8_byte_count = $IdentityBytes.Length
    identity_sha256 = $IdentitySha256
    terminal = $Discovery.terminal
} | ConvertTo-Json -Depth 12 -Compress | Write-Output
if ($Discovery.terminal -cne 'POWERSHELL_LAUNCHER_IDENTITY_PASS') {
    throw $Discovery.terminal
}
```

Create `task-1-report.md` with the literal current-shell payload, complete script
source, byte count, and digest before execution. The only permitted payload is
the call operator plus the absolute identity-script path; it does not name or
start another PowerShell executable. Execute it once. It returns no GPU, Docker,
artifact, or model evidence.

If the tool result is missing, malformed, nonzero without the retained PASS
record, or reports mismatch/unprovable, append the exact result and first
launcher `NO_GO` terminal and stop. Do not repeat discovery.

On PASS, independently parse `identity_canonical_json` using
`ConvertFrom-A11PowerShellIdentityJson`, recompute its byte count/digest, and
require exact equality with the retained wrapper. Convert those exact canonical
UTF-8 bytes to Base64. This Base64 value is the only identity representation
embedded in later scripts.

- [ ] **Step 5: Materialize a fresh complete entry script with child self-attestation first**

Use `apply_patch` to create the new entry script. After strict mode and error
preference, insert the exact identity helper block from Step 2, then a
single-quoted Base64 constant containing the accepted canonical identity JSON.
Decode it with BOM-less UTF-8, parse it through
`ConvertFrom-A11PowerShellIdentityJson`, observe the child with:

```powershell
$ObservedLauncherIdentity = Get-A11PowerShellFileIdentity `
    -Path (Get-Process -Id $PID -ErrorAction Stop).Path `
    -PowerShellVersion $PSVersionTable.PSVersion.ToString()
$LauncherIdentityComparison = Compare-A11PowerShellIdentity `
    -Expected $ExpectedLauncherIdentity `
    -Observed $ObservedLauncherIdentity
[pscustomobject][ordered]@{
    launcher_identity_expected = $ExpectedLauncherIdentity
    launcher_identity_observed = $ObservedLauncherIdentity
    launcher_identity_comparison = $LauncherIdentityComparison
} | ConvertTo-Json -Depth 12 -Compress | Write-Output
if ($LauncherIdentityComparison.terminal -cne
    'POWERSHELL_LAUNCHER_IDENTITY_PASS') {
    throw $LauncherIdentityComparison.terminal
}
```

Only after that block, materialize the complete effective WDDM Task 1 source
from committed WDDM-plan lines 112-601. Do not read or copy the consumed ignored
entry script. Preserve the exact secure XML decoder, synthetic matrix, one
injected observer call, preservation envelope, and single live observer call.

Require the first occurrence of Git, Docker, artifact-root, lease, CPU, and
`nvidia-smi` tokens in the entry script to occur after the child comparison
guard. Require exactly one `nvidia-smi` token in the observer body and zero old
hard-coded `C:\Program Files\PowerShell\7\pwsh.exe` strings.

- [ ] **Step 6: Freeze and execute one controller revalidation**

Use `apply_patch` to create `task-1-entry-launcher-revalidate.ps1` with the
exact identity helper block and accepted Base64 constant. It decodes the
expected identity, calls `Get-A11PowerShellFileIdentity` once on
`expected.canonical_path`, compares exact identities, emits expected/observed/
comparison JSON, and throws the comparison terminal unless PASS.

After the single-quoted Base64 constant, append this exact body:

```powershell
$Utf8 = [Text.UTF8Encoding]::new($false)
$ExpectedIdentityJson = $Utf8.GetString(
    [Convert]::FromBase64String($ExpectedLauncherIdentityJsonBase64)
)
$ExpectedIdentity = ConvertFrom-A11PowerShellIdentityJson `
    -Json $ExpectedIdentityJson
try {
    $ObservedIdentity = Get-A11PowerShellFileIdentity `
        -Path $ExpectedIdentity.canonical_path `
        -PowerShellVersion $ExpectedIdentity.powershell_version
    $Comparison = Compare-A11PowerShellIdentity `
        -Expected $ExpectedIdentity -Observed $ObservedIdentity
} catch {
    [pscustomobject][ordered]@{
        launcher_identity_expected = $ExpectedIdentity
        error_type = $_.Exception.GetType().FullName
        error_message = $_.Exception.Message
        terminal = 'POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO'
    } | ConvertTo-Json -Depth 12 -Compress | Write-Output
    throw 'POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO'
}
[pscustomobject][ordered]@{
    launcher_identity_expected = $ExpectedIdentity
    launcher_identity_observed = $ObservedIdentity
    launcher_identity_comparison = $Comparison
    terminal = $Comparison.terminal
} | ConvertTo-Json -Depth 12 -Compress | Write-Output
if ($Comparison.terminal -cne 'POWERSHELL_LAUNCHER_IDENTITY_PASS') {
    throw $Comparison.terminal
}
```

Record its literal current-shell payload, source, bytes, digest, and expected
identity before execution. Execute it once. A mismatch, unprovable result,
missing tool completion, or malformed output stops before the entry payload.
Do not rediscover another executable.

- [ ] **Step 7: Freeze and execute the complete entry payload exactly once**

Hash the final entry script after every static check. In the report, record the
literal payload made from the accepted `canonical_path`, exact absolute entry
script path, and these fixed arguments:

```text
-NoProfile -NonInteractive -File
```

Record the complete source, byte count, digest, argv, and frozen launcher
identity before execution. Verify the report contains those exact bytes and do
not edit the script afterward.

Execute only the recorded literal payload once. If it yields a session, resume
only that same session until completion. A path/start/tool-completion failure
without a valid child identity record is
`POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO`. A comparable child identity difference
is `POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO`. Never launch a replacement.

After child identity PASS, apply the inherited WDDM closed outcomes exactly:

```text
CUDA_QUERY_START_FAILURE / NO_GO
CUDA_QUERY_FAILURE / NO_GO
CUDA_XML_PARSE_FAILURE / NO_GO
CUDA_GPU_IDENTITY_MISMATCH / NO_GO
CUDA_PROCESS_TYPE_UNPROVABLE / NO_GO
CUDA_COMPUTE_BUSY / NO_GO
CUDA_OTHER_RESOURCE_BUSY / NO_GO
CUDA_IDLE / PASS
CUDA_OBSERVATION_UNPROVABLE / NO_GO
```

Any `NO_GO` stops Task 1 without CPU tests or implementation edits.

- [ ] **Step 8: Run the complete CPU baseline only after entry PASS**

Use `apply_patch` to create `task-1-cpu-baseline.ps1`. Insert the same identity
helper block, accepted Base64 constant, and child self-attestation before:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw 'CPU baseline failed' }
```

Revalidate the frozen launcher once with the newly materialized
`task-1-cpu-launcher-revalidate.ps1`, containing the same expected identity and
the exact Step 6 revalidation body. Record both commands completely, execute
each once, and require child identity PASS plus pytest exit 0 with exact passed/
skipped totals. Do not rediscover a launcher or rerun the entry revalidation.

- [ ] **Step 9: Publish the ignored Task 1 report and close the gate**

The report records all discovery, revalidation, entry, and CPU payloads/results;
all command sources/bytes/digests; the canonical identity JSON/Base64/bytes/hash;
every child expected/observed comparison; complete WDDM observation JSON/digest;
every session poll; and exactly one final terminal:

```text
ENTRY_GATE_PASS
```

or the first exact `NO_GO`. Afterwards require linked and canonical worktrees
clean, staging empty, consumed evidence digests unchanged, and no
`__pycache__`, `.pyc`, `.pytest_cache`, runtime artifact, or diagnostic directory
inside the repository, excluding `.venv` and this new ignored SDD workspace.

`ENTRY_GATE_PASS` is the only result that permits Task 2.

---

### Task 2: Add RED type-aware XML and inherited ordering tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: Task 1 WDDM helper names/terminals and WDDM-plan Task 2 lines 663-759
- Produces: RED tests for secure XML, exact process-type admission, one native call, launcher integration, versioned registry, frozen vectors, and generic verification

- [ ] **Step 1: Execute the exact inherited RED task**

Read WDDM-plan Task 2 from immutable blob
`2abcc051d50921a59f58a57b2814e2a5e47dcc59`, lines 663-759, and execute every
step. Add the exact `_nvidia_smi_xml` fixture, parameterized `G`/`O`/`C`/`M`/
`C+G`/`M+C` cases, fail-closed XML/query cases, injected invocation counter,
launcher integration/static prohibitions, and inherited ordering/registry/vector
tests. Do not add launcher-identity helpers to production code or tests; they are
controller evidence only.

- [ ] **Step 2: Run focused RED and prove intended failures**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
    -k 'wddm or gpu_observation or preserved_attempt or inventory_algorithm or registry'
```

Require failure for missing production XML/registry behavior, not syntax,
collection, fixture, environment, Docker, network, GPU, or model errors. Do not
weaken an assertion to obtain RED. Do not commit.

---

### Task 3: Implement the shared XML observer and inherited ordering recovery

**Files:**
- Create: `configs/a11/preserved-attempts.json`
- Create: `schemas/a11-preserved-attempts.schema.json`
- Modify: `scripts/run_wave0_a11.ps1`
- Modify: `tests/gates/test_wave0_a11_launcher.py` only for a test defect proven during GREEN

**Interfaces:**
- Consumes: every RED assertion from Task 2 and WDDM-plan Task 3 lines 760-816
- Produces: secure XML/type helpers, one native observer, `gpu_observation` integration, versioned registry/inventory/verifier, and complete GREEN launcher tests

- [ ] **Step 1: Execute the exact inherited GREEN implementation**

Execute every step from WDDM-plan blob
`2abcc051d50921a59f58a57b2814e2a5e47dcc59`, lines 760-816. Implement the
secure XML decoder, type classifier, UTF-8 stream records, observation core,
single `System.Diagnostics.Process` observer, global/phase integration, registry,
schema, version-aware inventory, and byte guard. Keep the optional native runner
test-only and production argv exact. Do not commit.

- [ ] **Step 2: Run focused and complete GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
    -k 'wddm or gpu_observation or preserved_attempt or inventory_algorithm or registry'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Require both commands to exit 0. Parse the complete modified launcher under
PowerShell 7.6.4 and Windows PowerShell 5.1 and require zero parser errors. Do
not commit.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files:**
- Create: `tests/scripts/test_run_uv_sync_with_retries.py`

**Interfaces:**
- Consumes: WDDM-plan Task 4 lines 817-826 and its inherited immutable CUDA-plan Task 4
- Produces: RED success, retry, exhaustion, signal, raw-byte, command-boundary, and CLI tests

- [ ] **Step 1: Execute the exact inherited wrapper RED task**

Execute WDDM-plan Task 4 from blob
`2abcc051d50921a59f58a57b2814e2a5e47dcc59`, lines 817-826, including every
step in CUDA-observability plan blob
`98385de8453b4f5d80b7dc9a91d01c5aa3c5752b`, lines 509-520. Require the
focused suite to fail only because the wrapper does not exist. Do not commit.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files:**
- Create: `scripts/run_uv_sync_with_retries.py`
- Modify: `docker/wave0.Dockerfile`
- Modify: `tests/scripts/test_run_uv_sync_with_retries.py` only for a proven test defect
- Modify: `tests/gates/test_wave0_a11_launcher.py` only for inherited Docker/static assertions

**Interfaces:**
- Consumes: all RED wrapper assertions from Task 4 and WDDM-plan Task 5 lines 827-836
- Produces: bounded dependency-only transport wrapper, locked dependency stage/cache mounts, GREEN wrapper/launcher tests, and static BuildKit validation

- [ ] **Step 1: Execute the exact inherited wrapper and Docker GREEN task**

Execute WDDM-plan Task 5 from blob
`2abcc051d50921a59f58a57b2814e2a5e47dcc59`, lines 827-836, including every
step in CUDA-observability plan blob
`98385de8453b4f5d80b7dc9a91d01c5aa3c5752b`, lines 521-532. Require wrapper
GREEN, launcher/Docker assertions GREEN, parser gates PASS, and
`docker buildx build --check` PASS without executing or exporting a stage. Do
not commit.

---

### Task 6: Verify, review, and create the single implementation commit

**Files:**
- Commit exactly the seven implementation allowlist paths; modify no other tracked path
- Create ignored evidence: `task-6-candidate-launcher-revalidate.ps1`, `task-6-candidate-preservation.ps1`, and `task-6-report.md` beneath the new SDD workspace

**Interfaces:**
- Consumes: uncommitted Tasks 2-5, Task 1 frozen launcher identity, and Task 1 `ENTRY_GATE_PASS`
- Produces: one reviewed implementation commit whose parent is this plan commit

- [ ] **Step 1: Execute the complete inherited CPU, scope, and static gates**

Execute WDDM-plan Task 6 Step 1, blob lines 845-861, including every verification
inherited from ordering-plan Task 6 Steps 1-3. Require all CPU suites, XML
security/type tests, registry/schema/vector tests, wrapper tests, algorithm/style/
lock/parser/Dockerfile/whitespace gates, exact seven-path diff, empty staging
before review, and forbidden-capability scans to pass.

Retain the WDDM plan's exact source scan for one `'nvidia-smi'` definition,
one `FileName = $Argv[0]` boundary, and absence of CSV fallback, process mutation,
GPU reset, and driver-model change.

- [ ] **Step 2: Re-prove candidate preservation using the frozen launcher identity**

Materialize a new Task 6 preservation script with the Step 2 identity helper
block and Task 1 accepted Base64 identity. Child self-attestation must precede
Git, Docker, artifact, lease, historical, and `nvidia-smi` operations. Materialize
a separate revalidation script against the same expected identity and run it
once before the candidate command. Do not rediscover an executable.

Then execute WDDM-plan Task 6 Step 2, lines 862-871: require exact seven-path
unstaged diff, empty staging, AST-load only the uncommitted production observer,
run its synthetic matrix, start exactly one live type-aware observation, and
re-prove every non-GPU preservation check. Record both launcher and candidate
evidence completely. Require exact stable-field equality with Task 1 and
`CUDA_IDLE / PASS`.

- [ ] **Step 3: Perform cold requirements and code review**

Execute WDDM-plan Task 6 Step 3, lines 872-877. Add the launcher-identity design,
this plan, discovery policy, duplicate-key-aware canonical parser, exact frozen
identity, controller revalidation, child self-attestation order, and no-
rediscovery rule to the review set. Require `Critical=0` and `Important=0`.
Resolve findings with RED/GREEN and rerun every affected gate without changing
prior evidence.

- [ ] **Step 4: Stage exactly seven paths and create one commit**

Before staging, require `git rev-parse HEAD` to equal this plan commit,
`git rev-parse HEAD^` to equal
`3e98d1d56caede9a1baaf215da4e418112a73643`, and the plan commit to contain only
`docs/superpowers/plans/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery.md`.

Stage exactly the seven allowlist paths and no ignored evidence. Set author and
committer to the required identity and create one commit with message:

```text
fix: harden A11 recovery boundaries
```

Do not commit unless every prior gate passed.

- [ ] **Step 5: Verify exact committed lineage and candidate**

After the commit, assign the chain exactly:

```powershell
$Implementation = (git rev-parse HEAD).Trim()
$LauncherPlan = (git rev-parse 'HEAD^').Trim()
$LauncherDesign = (git rev-parse 'HEAD^^').Trim()
$WddmPlan = (git rev-parse 'HEAD^^^').Trim()
$WddmDesign = (git rev-parse 'HEAD^^^^').Trim()
$CudaPlan = (git rev-parse 'HEAD^^^^^').Trim()
$CudaDesign = (git rev-parse 'HEAD^^^^^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^^^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^^^^^').Trim()
if (
    $LauncherDesign -cne '3e98d1d56caede9a1baaf215da4e418112a73643' -or
    $WddmPlan -cne '42c200d8a801b142cde394cda7a0520bd9c30a83' -or
    $WddmDesign -cne '0053a8b30c8639ea9b9752ca2171117692fe78b0' -or
    $CudaPlan -cne 'f45d84eec13b98ee4566497252375f20251fd2d3' -or
    $CudaDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f'
) { throw 'committed candidate lineage mismatch' }
```

Require exact seven committed paths, exact identity, clean linked/canonical
worktrees, empty staging, fixed `uv.lock`, unchanged consumed and Task 1
evidence, focused/full CPU suites, parser gates, schema validation, Dockerfile
`--check`, `git show --check HEAD`, and a fresh frozen-launcher child
self-attestation before any final scripted verification command.

The only claim is eligibility for the single dependency-only diagnostic. Do not
claim formal A11 runtime success.

---

### Task 7: Execute and preserve exactly one dependency-only diagnostic

**Files:**
- Modify in repository: none
- Create outside repository/artifact root: one append-only directory beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`
- Create ignored evidence beneath the new SDD workspace: `task-7-pre-launcher-revalidate.ps1`, `task-7-pre-diagnostic.ps1`, `task-7-docker-launcher-revalidate.ps1`, `task-7-docker-diagnostic.ps1`, `task-7-post-launcher-revalidate.ps1`, `task-7-post-diagnostic.ps1`, and `task-7-report.md`
- Docker effect: BuildKit cache data only; no image export

**Interfaces:**
- Consumes: clean Task 6 implementation commit, frozen launcher identity, and Docker target `a11-dependencies`
- Produces: `A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED` or `A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN`

- [ ] **Step 1: Prove one-shot eligibility with the extended lineage**

Start from WDDM-plan Task 7 Step 1, lines 939-971, but use the new chain:

```powershell
$Source = (git rev-parse HEAD).Trim()
$LauncherPlan = (git rev-parse 'HEAD^').Trim()
$LauncherDesign = (git rev-parse 'HEAD^^').Trim()
$WddmPlan = (git rev-parse 'HEAD^^^').Trim()
$WddmDesign = (git rev-parse 'HEAD^^^^').Trim()
$CudaPlan = (git rev-parse 'HEAD^^^^^').Trim()
$CudaDesign = (git rev-parse 'HEAD^^^^^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^^^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^^^^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^^^^^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^^^^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^^^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^^^^^^^').Trim()
if (
    $LauncherDesign -cne '3e98d1d56caede9a1baaf215da4e418112a73643' -or
    $WddmPlan -cne '42c200d8a801b142cde394cda7a0520bd9c30a83' -or
    $WddmDesign -cne '0053a8b30c8639ea9b9752ca2171117692fe78b0' -or
    $CudaPlan -cne 'f45d84eec13b98ee4566497252375f20251fd2d3' -or
    $CudaDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
) { throw 'dependency diagnostic lineage mismatch' }
```

Complete Task 6 Step 5 verification. Use the frozen launcher identity protocol
to revalidate once and self-attest a materialized pre-diagnostic script before
Git, Docker, lease, container, diagnostic-root, or `nvidia-smi` checks. AST-load
the committed observer without invoking the launcher, run its synthetic matrix,
and start exactly one pre-diagnostic WDDM query. Require `CUDA_IDLE / PASS`, zero
project containers, zero active leases, and no diagnostic identity for `$Source`.
Failure stops before directory creation and Docker execution.

- [ ] **Step 2: Create the exact append-only diagnostic identity**

Execute WDDM-plan Task 7 Step 2, lines 972-984, retaining every prior field and
create-new/no-clobber rule. Add these fields before the existing lineage:

```text
powershell_launcher_identity_recovery_plan_commit = $LauncherPlan
powershell_launcher_identity_recovery_design_commit = 3e98d1d56caede9a1baaf215da4e418112a73643
wddm_type_aware_recovery_plan_commit = 42c200d8a801b142cde394cda7a0520bd9c30a83
wddm_type_aware_recovery_design_commit = 0053a8b30c8639ea9b9752ca2171117692fe78b0
cuda_observability_recovery_plan_commit = f45d84eec13b98ee4566497252375f20251fd2d3
cuda_observability_recovery_design_commit = 5451c50cc20b1c297c9bdd3535a793eff993158d
launcher_identity_canonical_json_sha256 = $LauncherIdentityDigest
```

Set `$LauncherIdentityDigest` by parsing the immutable Task 1 report, decoding
the retained canonical JSON Base64, recomputing its BOM-less UTF-8 SHA-256, and
requiring equality with the report's retained lowercase digest. It is not
generated from the host again. Do not include an owner ID, run ID, GPU request,
or formal runtime authorization.

- [ ] **Step 3: Invoke the dependency diagnostic exactly once**

Execute WDDM-plan Task 7 Step 3, lines 985-992. Use `apply_patch` to materialize
one command script with child launcher self-attestation before the single Docker
command. Revalidate the frozen launcher once, retain all command evidence, and
then execute exactly:

```text
docker buildx build --no-cache --progress=plain --target a11-dependencies --output=type=cacheonly
```

Do not wrap, retry, relaunch, automate, or repeat it.

- [ ] **Step 4: Publish result, manifest, and closure**

Execute WDDM-plan Task 7 Step 4, lines 993-996, verbatim. A nonzero Docker result
is diagnostic `NO_GO`, not permission to retry.

- [ ] **Step 5: Re-prove preservation with one post-diagnostic observation**

Execute WDDM-plan Task 7 Step 5, lines 997-1013. Use the same frozen launcher
identity protocol and committed type-aware helper loaded through the AST-only
boundary. Materialize and record the post command before execution. It is a
distinct preservation gate, not a retry, and runs only after the Docker
diagnostic actually started, even when Docker returned nonzero.

Require unchanged repository/artifact/image/lease/container/runtime state and
zero exported tagged or dangling image. Report exactly one terminal:

```text
A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
```

or:

```text
A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

Stop in either case. A later formal runtime attempt requires separate explicit
owner authorization bound to the exact implementation source, original A11
specification, original A11 plan, and branch.
