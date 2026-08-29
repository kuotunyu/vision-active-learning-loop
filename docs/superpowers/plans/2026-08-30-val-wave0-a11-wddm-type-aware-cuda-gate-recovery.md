# Wave 0 A11 WDDM Type-Aware CUDA-Gate Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before every terminal or commit claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace both A11 Windows WDDM PID-only and memory-value GPU admission assumptions with one fail-closed process-type observation, then finish the already approved ordering and dependency-transport recovery only after a fresh complete entry gate passes.

**Architecture:** One shared PowerShell observer starts exactly one `nvidia-smi -q -x -i <frozen UUID>` process per scheduled gate, securely decodes the vendor XML without resolving its external DTD, and classifies exact NVIDIA process types. Only no process rows or exclusively `G` rows pass; `C`, `M`, `C+G`, `M+C`, `O`, unknown structure, query failure, or unprovable tool completion stop with precise preserved `NO_GO` terminals.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`, `System.Xml.XmlReader`, and SHA-256; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery-design.md` at commit `0053a8b30c8639ea9b9752ca2171117692fe78b0`, blob `124b87aa9b2a04b3830aa85e5c45a4cfde87b260`.
- This plan commit must be the direct child of that design commit and add only this plan file.
- The prior CUDA-observability plan and design remain immutable at `f45d84eec13b98ee4566497252375f20251fd2d3` and `5451c50cc20b1c297c9bdd3535a793eff993158d`.
- The prior CUDA-observability plan blob remains immutable at `98385de8453b4f5d80b7dc9a91d01c5aa3c5752b`.
- The ordering-recovery plan remains immutable at `52fe25d529f7d64e986864576653d0d14a6e484b`, blob `901c2b31c033d44949915d2081a8cf715fd2e699`.
- The ordering-recovery design remains immutable at `68f51519d2cb480200ca4fef740651b0d15dd76f`.
- The digest-recovery plan and design remain immutable at `03115325f36da31b135b4593fb8df1689eac9a35` and `2db13d302da97a241daeaba3578cd9cec1c8073b`.
- The diagnostic-root erratum, runtime-transport plan, and runtime-transport design remain immutable at `101bb79369399cc3947f1c667f0a11988f916638`, `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, and `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`.
- The preserved Task 1 terminal at source `f45d84eec13b98ee4566497252375f20251fd2d3` remains `CUDA_COMPUTE_BUSY / NO_GO`; never reinterpret, replace, or overwrite it.
- The parked missing-literal-command finding in the prior SDD report remains immutable evidence; never reconstruct it.
- During authoring of this plan, one unscheduled read-only XML query was accidentally started by a Markdown-block self-test harness. Its native result was not retained, so preserve it only as `CUDA_OBSERVATION_UNPROVABLE / NO_GO` planning-incident evidence: it is not a Task 1 gate, cannot satisfy or consume Task 1, cannot be reclassified, and must never be retried or reconstructed. Task 1 remains the first scheduled, fully retained type-aware admission observation.
- The implementation must be one append-only commit, the direct child of this plan commit, changing exactly the seven implementation paths listed below. Tasks 1-5 create no commits.
- Author and committer must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean evidence, push, merge, tag, release, or modify another repository.
- The artifact root `D:\vision-active-learning-loop-artifacts\wave0` is read-only. A mismatch is a stop condition, never a repair instruction.
- Never terminate, pause, signal, reprioritize, whitelist by name, or otherwise mutate an observed GPU process. Do not use `Stop-Process`, `taskkill`, service control, Docker stop, WSL shutdown, Task Manager automation, GPU reset, driver-model changes, or an equivalent action.
- Each scheduled CUDA observation starts exactly one `nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63` native process. Do not retry, substitute, use another output format, wrap in a pipeline, add a replacement timeout, or infer PASS from absent output.
- Only zero process rows or rows whose exact type is exclusively `G` may pass. `C`, `M`, `C+G`, `M+C`, `O`, missing type, unknown type, unsafe XML, or an unprovable result is `NO_GO`.
- PID, process name, parent PID, executable vendor, and `used_memory` are evidence only and never change admission.
- Do not invoke `scripts/run_wave0_a11.ps1`, generate or guess an `OwnerAuthorizationId`, acquire a formal GPU lease, initialize a model, create a calibration or validation runtime identity, access RDD, or start Wave 1.
- Consumed owners `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` remain immutable evidence. Test-only owner values must contain `TEST`.
- The only Docker invocation permitted to execute a stage is the single dependency-only diagnostic in Task 7. Tasks 5-6 may call `docker buildx build --check`, which validates without executing or exporting a stage.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` byte-identical at SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.
- Keep model, receipt, statistical, threshold, replica, split, acquisition, data-firewall, lease, validation, and Wave 1 contracts unchanged.
- CPU tests set `PYTHONDONTWRITEBYTECODE=1` and pass `-p no:cacheprovider`; they may not use network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The dependency diagnostic writes only beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`, outside the repository and artifact baseline. It has no owner ID, run ID, image export, project container, model process, or statistical meaning.
- Every nontrivial gate command is materialized before execution as a unique `.ps1` file in this plan's ignored SDD workspace. Record the literal short tool payload, complete script bytes, UTF-8 byte count/SHA-256, argv, tool result, exit code, output, session ID, chunk ID, and every same-session poll. Never reconstruct a missing payload after execution.

## Normative overlay

The complete prior CUDA-observability plan at commit `f45d84eec13b98ee4566497252375f20251fd2d3` and Git blob `98385de8453b4f5d80b7dc9a91d01c5aa3c5752b` is incorporated by immutable reference. Line numbers below are one-based lines in that exact blob.

These are the only replacements:

| Contract | Superseded | Effective |
| --- | --- | --- |
| Implementation parent | prior CUDA plan `f45d84eec13b98ee4566497252375f20251fd2d3` | this plan commit |
| Implementation grandparent | prior CUDA design `5451c50cc20b1c297c9bdd3535a793eff993158d` | WDDM type-aware design `0053a8b30c8639ea9b9752ca2171117692fe78b0` |
| Task 1 | prior-plan lines 109-480 | Task 1 in this plan |
| Task 2 | prior-plan lines 481-497 | inherited ordering RED plus type-aware XML RED in Task 2 here |
| Task 3 | prior-plan lines 498-508 | inherited ordering GREEN plus shared XML observer GREEN in Task 3 here |
| Task 6 | prior-plan lines 533-608 | inherited verification/commit with type-aware lineage and candidate gate below |
| Task 7 | prior-plan lines 609-706 | inherited diagnostic with extended lineage and type-aware pre/post gates below |

Prior-plan Tasks 4 and 5 remain byte-for-byte normative:

| Inherited task | Exact prior-plan lines |
| --- | ---: |
| Task 4 | 509-520 |
| Task 5 | 521-532 |

The prior plan itself incorporates the ordering-recovery blob. All ordering registry, versioned inventory, bounded uv transport, Docker dependency-stage, verification, and diagnostic requirements not explicitly replaced here remain binding.

Before execution prove both overlay blobs:

```powershell
$PriorPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery.md'
$OrderingPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md'
if ((git rev-parse "f45d84eec13b98ee4566497252375f20251fd2d3`:$PriorPlanPath").Trim() -cne
    '98385de8453b4f5d80b7dc9a91d01c5aa3c5752b') {
    throw 'immutable prior CUDA plan blob mismatch'
}
if ((git rev-parse "52fe25d529f7d64e986864576653d0d14a6e484b`:$OrderingPlanPath").Trim() -cne
    '901c2b31c033d44949915d2081a8cf715fd2e699') {
    throw 'immutable ordering plan blob mismatch'
}
```

## Frozen preservation envelope

The exact five run records, algorithms, counts, digests, image tags/IDs, lease-history hashes, historical baselines, attempt-5 vector, and latest-write values in ordering-plan blob lines 40-111 remain binding.

The entry gate must reproduce:

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

## Implementation file map and allowlist

- Create `configs/a11/preserved-attempts.json`: five immutable declarative records with one exact `run_inventory_algorithm` each.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 registry schema including the two-value algorithm enum.
- Create `scripts/run_uv_sync_with_retries.py`: bounded dependency-build-only transport wrapper.
- Modify `scripts/run_wave0_a11.ps1`: secure WDDM XML decoder, pure process-type classifier, single-invocation observer, version-aware inventory, registry loader/verifier, byte guard, and unchanged single-build campaign path.
- Modify `docker/wave0.Dockerfile`: dependency stage, exact wrapper calls, and two locked BuildKit uv cache mounts.
- Modify `tests/gates/test_wave0_a11_launcher.py`: XML security/type/observer integration, ordering, vector, registry, verifier, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change.

---

### Task 1: Re-prove preservation with one WDDM type-aware XML observation

**Files:**
- Modify tracked files: none
- Create ignored command evidence: `.superpowers/sdd/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery/task-1-entry-gate.ps1`
- Create ignored CPU command evidence only after GPU PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery/task-1-cpu-baseline.ps1`
- Write ignored execution report: `.superpowers/sdd/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery/task-1-report.md`
- Read: Git topology, immutable recovery documents, production source blobs, all five preserved runs, Docker/image/lease/historical state, and one live GPU XML observation

**Interfaces:**
- Consumes: this plan commit, design `0053a8b30c8639ea9b9752ca2171117692fe78b0`, prior-plan blob `98385de8453b4f5d80b7dc9a91d01c5aa3c5752b`, ordering-plan blob `901c2b31c033d44949915d2081a8cf715fd2e699`
- Produces: `ENTRY_GATE_PASS` or one precise preserved `NO_GO`; on PASS, one canonical type-aware observation for Task 6 comparison
- Pure helper signatures used again in Tasks 2-3: `Get-A11XmlSingleText(Node, XPath, FailureCode) -> string`, `ConvertFrom-A11NvidiaSmiXml(XmlText) -> decoded object`, `ConvertTo-A11GpuAdmission(Decoded) -> admission object`, `Get-A11Utf8StreamRecord(Text) -> byte/digest object`, `ConvertTo-A11GpuObservationCore(StartSucceeded, ExitCode, StdoutText, StderrText) -> core object`, `Invoke-A11GpuObservation([NativeRunner]) -> observation object`

- [ ] **Step 1: Prove exact lineage, isolation, source blobs, identity, and clean scope**

Materialize the following as the first section of `task-1-entry-gate.ps1` before executing any part of it:

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedIdentity = 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
$Plan = (git rev-parse HEAD).Trim()
$Design = (git rev-parse 'HEAD^').Trim()
$PriorPlan = (git rev-parse 'HEAD^^').Trim()
$PriorDesign = (git rev-parse 'HEAD^^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^^^^').Trim()
if (
    $Design -cne '0053a8b30c8639ea9b9752ca2171117692fe78b0' -or
    $PriorPlan -cne 'f45d84eec13b98ee4566497252375f20251fd2d3' -or
    $PriorDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
) { throw 'WDDM type-aware recovery lineage mismatch' }
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') {
    throw 'branch mismatch'
}
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r $Plan)
$DesignPaths = @(git diff-tree --no-commit-id --name-only -r $Design)
if ($PlanPaths.Count -ne 1 -or $PlanPaths[0] -cne
    'docs/superpowers/plans/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery.md') {
    throw 'plan path scope mismatch'
}
if ($DesignPaths.Count -ne 1 -or $DesignPaths[0] -cne
    'docs/superpowers/specs/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery-design.md') {
    throw 'design path scope mismatch'
}
foreach ($Commit in @($Plan, $Design)) {
    $Identity = (git show -s --format='%an <%ae>|%cn <%ce>' $Commit).Trim()
    if ($Identity -cne "$ExpectedIdentity|$ExpectedIdentity") {
        throw 'commit identity mismatch'
    }
}
$GitDir = (git rev-parse --absolute-git-dir).Trim()
$CommonDir = (Resolve-Path -LiteralPath (git rev-parse --git-common-dir).Trim()).Path
if ($GitDir -ceq $CommonDir) { throw 'linked worktree isolation missing' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) {
    throw 'linked worktree dirty'
}
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
$Canonical = ((git worktree list --porcelain | Where-Object { $_ -clike 'worktree *' } |
    Select-Object -First 1).Substring(9))
if (@(git -C $Canonical status --porcelain=v1 --untracked-files=all).Count -ne 0) {
    throw 'canonical worktree dirty'
}
$ExpectedBlobs = [ordered]@{
    'docs/superpowers/specs/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery-design.md' = '124b87aa9b2a04b3830aa85e5c45a4cfde87b260'
    'docs/superpowers/plans/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery.md' = '98385de8453b4f5d80b7dc9a91d01c5aa3c5752b'
    'scripts/run_wave0_a11.ps1' = 'ad4bdcce7e99499be9e6c03e1760cf1bc00a3542'
    'tests/gates/test_wave0_a11_launcher.py' = '5d751e44480f78b9876230ad05fad055016ff8bd'
    'docker/wave0.Dockerfile' = 'd5bd4d2848f47cc99a9016cdafb47bd0099749b9'
    'uv.lock' = '12a0d6120c486fb4ca07573ffa0e86cae4ca60b0'
}
foreach ($Path in $ExpectedBlobs.Keys) {
    if ((git rev-parse "$Plan`:$Path").Trim() -cne $ExpectedBlobs[$Path]) {
        throw "source blob mismatch: $Path"
    }
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath 'uv.lock').Hash.ToLowerInvariant() -cne
    '530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93') {
    throw 'uv.lock digest mismatch'
}
```

- [ ] **Step 2: Define the secure decoder and pure type classifier**

Append these exact interfaces to the same command file. The implementation may factor repeated result construction into a local helper, but returned field names and terminals are exact:

```powershell
function Get-A11XmlSingleText {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][System.Xml.XmlNode]$Node,
        [Parameter(Mandatory)][string]$XPath,
        [Parameter(Mandatory)][string]$FailureCode
    )
    $Matches = @($Node.SelectNodes($XPath))
    if ($Matches.Count -ne 1 -or
        @($Matches[0].ChildNodes | Where-Object { $_.NodeType -eq 'Element' }).Count -ne 0 -or
        [string]::IsNullOrWhiteSpace([string]$Matches[0].InnerText)) {
        throw $FailureCode
    }
    return ([string]$Matches[0].InnerText).Trim()
}

function ConvertFrom-A11NvidiaSmiXml {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowEmptyString()][string]$XmlText)
    $Utf8 = [Text.UTF8Encoding]::new($false)
    if ($Utf8.GetByteCount($XmlText) -gt 8388608 -or
        $XmlText -cmatch '(?is)<!ENTITY' -or
        $XmlText -cmatch '(?is)<!DOCTYPE[^>]*\[' -or
        $XmlText -cmatch '(?s)&(?:#x[0-9A-Fa-f]+|#[0-9]+|[A-Za-z_:][A-Za-z0-9_.:-]*);') {
        throw 'CUDA_XML_PARSE_FAILURE'
    }
    $Settings = [Xml.XmlReaderSettings]::new()
    $Settings.XmlResolver = $null
    $Settings.DtdProcessing = [Xml.DtdProcessing]::Ignore
    $Settings.MaxCharactersInDocument = 8388608
    $Settings.MaxCharactersFromEntities = 1024
    $Document = [Xml.XmlDocument]::new()
    $Document.XmlResolver = $null
    $StringReader = [IO.StringReader]::new($XmlText)
    $Reader = $null
    try {
        $Reader = [Xml.XmlReader]::Create($StringReader, $Settings)
        $Document.Load($Reader)
    } catch {
        throw 'CUDA_XML_PARSE_FAILURE'
    } finally {
        if ($null -ne $Reader) { $Reader.Dispose() }
        $StringReader.Dispose()
    }
    $Roots = @($Document.SelectNodes('/nvidia_smi_log'))
    if ($Roots.Count -ne 1) { throw 'CUDA_XML_PARSE_FAILURE' }
    $Root = $Roots[0]
    $Driver = Get-A11XmlSingleText $Root './driver_version' 'CUDA_GPU_IDENTITY_MISMATCH'
    $AttachedText = Get-A11XmlSingleText $Root './attached_gpus' 'CUDA_GPU_IDENTITY_MISMATCH'
    $Attached = 0
    if (-not [int]::TryParse($AttachedText, [ref]$Attached) -or $Attached -ne 1) {
        throw 'CUDA_GPU_IDENTITY_MISMATCH'
    }
    $Gpus = @($Root.SelectNodes('./gpu'))
    if ($Gpus.Count -ne 1) { throw 'CUDA_GPU_IDENTITY_MISMATCH' }
    $Gpu = $Gpus[0]
    $Name = Get-A11XmlSingleText $Gpu './product_name' 'CUDA_GPU_IDENTITY_MISMATCH'
    $Uuid = Get-A11XmlSingleText $Gpu './uuid' 'CUDA_GPU_IDENTITY_MISMATCH'
    $DriverModel = Get-A11XmlSingleText $Gpu './driver_model/current_dm' 'CUDA_GPU_IDENTITY_MISMATCH'
    if ($Name -cne 'NVIDIA GeForce RTX 4090' -or
        $Uuid -cne 'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63' -or
        $DriverModel -cne 'WDDM') {
        throw 'CUDA_GPU_IDENTITY_MISMATCH'
    }
    $ProcessContainers = @($Gpu.SelectNodes('./processes'))
    if ($ProcessContainers.Count -ne 1) { throw 'CUDA_XML_PARSE_FAILURE' }
    $ProcessNodes = @($ProcessContainers[0].SelectNodes('./process_info'))
    if ($ProcessNodes.Count -eq 0) {
        $EmptyText = ([string]$ProcessContainers[0].InnerText).Trim()
        if ($EmptyText -cne '' -and $EmptyText -cne 'N/A') {
            throw 'CUDA_XML_PARSE_FAILURE'
        }
    }
    $Rows = [Collections.Generic.List[object]]::new()
    foreach ($ProcessNode in $ProcessNodes) {
        $PidText = Get-A11XmlSingleText $ProcessNode './pid' 'CUDA_PROCESS_TYPE_UNPROVABLE'
        $Type = Get-A11XmlSingleText $ProcessNode './type' 'CUDA_PROCESS_TYPE_UNPROVABLE'
        $ProcessName = Get-A11XmlSingleText $ProcessNode './process_name' 'CUDA_PROCESS_TYPE_UNPROVABLE'
        $UsedMemory = Get-A11XmlSingleText $ProcessNode './used_memory' 'CUDA_PROCESS_TYPE_UNPROVABLE'
        $PidValue = [long]0
        if (-not [long]::TryParse($PidText, [ref]$PidValue) -or $PidValue -le 0 -or
            $Type -cnotin @('G', 'O', 'C', 'M', 'C+G', 'M+C')) {
            throw 'CUDA_PROCESS_TYPE_UNPROVABLE'
        }
        [void]$Rows.Add([pscustomobject][ordered]@{
            pid = $PidValue
            type = $Type
            process_name = $ProcessName
            used_memory_text = $UsedMemory
        })
    }
    return [pscustomobject][ordered]@{
        name = $Name
        uuid = $Uuid
        driver_version = $Driver
        driver_model = $DriverModel
        processes = @($Rows)
    }
}

function ConvertTo-A11GpuAdmission {
    [CmdletBinding()]
    param([Parameter(Mandatory)][object]$Decoded)
    $Processes = @($Decoded.processes)
    $Compute = @($Processes | Where-Object { $_.type -cin @('C', 'M', 'C+G', 'M+C') })
    $Other = @($Processes | Where-Object { $_.type -ceq 'O' })
    $Graphics = @($Processes | Where-Object { $_.type -ceq 'G' })
    $Blocking = @($Processes | Where-Object { $_.type -cin @('O', 'C', 'M', 'C+G', 'M+C') })
    if ($Compute.Count -gt 0) {
        $Classification = 'CUDA_COMPUTE_BUSY'
        $ReasonCode = 'compute_type_present'
        $Terminal = 'CUDA_COMPUTE_BUSY / NO_GO'
    } elseif ($Other.Count -gt 0) {
        $Classification = 'CUDA_OTHER_RESOURCE_BUSY'
        $ReasonCode = 'other_type_present'
        $Terminal = 'CUDA_OTHER_RESOURCE_BUSY / NO_GO'
    } else {
        $Classification = 'CUDA_IDLE'
        $ReasonCode = 'graphics_only_or_empty'
        $Terminal = 'CUDA_IDLE / PASS'
    }
    return [pscustomobject][ordered]@{
        allowed_graphics_count = $Graphics.Count
        blocking_compute_count = $Compute.Count
        blocking_other_count = $Other.Count
        blocking_pids = @($Blocking | ForEach-Object { [long]$_.pid })
        classification = $Classification
        reason_code = $ReasonCode
        terminal = $Terminal
    }
}

function Get-A11Utf8StreamRecord {
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Text)
    $Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
    $Hasher = [Security.Cryptography.SHA256]::Create()
    try {
        $Digest = (($Hasher.ComputeHash($Bytes) |
            ForEach-Object { $_.ToString('x2') }) -join '')
    } finally {
        $Hasher.Dispose()
    }
    return [pscustomobject][ordered]@{
        utf8_byte_count = $Bytes.Length
        sha256 = $Digest
    }
}

function ConvertTo-A11GpuObservationCore {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][bool]$StartSucceeded,
        [AllowNull()][object]$ExitCode,
        [Parameter(Mandatory)][AllowEmptyString()][string]$StdoutText,
        [Parameter(Mandatory)][AllowEmptyString()][string]$StderrText
    )
    $StdoutRecord = Get-A11Utf8StreamRecord -Text $StdoutText
    $StderrRecord = Get-A11Utf8StreamRecord -Text $StderrText
    $ExitValue = $null
    if ($null -ne $ExitCode) {
        try { $ExitValue = [int]$ExitCode } catch { $ExitValue = $null }
    }
    $Name = $null
    $Uuid = $null
    $DriverVersion = $null
    $DriverModel = $null
    $Processes = @()
    $AllowedGraphicsCount = 0
    $BlockingComputeCount = 0
    $BlockingOtherCount = 0
    $BlockingPids = @()
    if (-not $StartSucceeded) {
        $Classification = 'CUDA_QUERY_START_FAILURE'
        $ReasonCode = 'native_start_failed'
        $Terminal = 'CUDA_QUERY_START_FAILURE / NO_GO'
    } elseif ($null -eq $ExitValue -or $ExitValue -ne 0) {
        $Classification = 'CUDA_QUERY_FAILURE'
        $ReasonCode = 'native_exit_nonzero'
        $Terminal = 'CUDA_QUERY_FAILURE / NO_GO'
    } else {
        try {
            $Decoded = ConvertFrom-A11NvidiaSmiXml -XmlText $StdoutText
            $Admission = ConvertTo-A11GpuAdmission -Decoded $Decoded
            $Name = $Decoded.name
            $Uuid = $Decoded.uuid
            $DriverVersion = $Decoded.driver_version
            $DriverModel = $Decoded.driver_model
            $Processes = @($Decoded.processes)
            $AllowedGraphicsCount = $Admission.allowed_graphics_count
            $BlockingComputeCount = $Admission.blocking_compute_count
            $BlockingOtherCount = $Admission.blocking_other_count
            $BlockingPids = @($Admission.blocking_pids)
            $Classification = $Admission.classification
            $ReasonCode = $Admission.reason_code
            $Terminal = $Admission.terminal
        } catch {
            switch -CaseSensitive ($_.Exception.Message) {
                'CUDA_GPU_IDENTITY_MISMATCH' {
                    $Classification = 'CUDA_GPU_IDENTITY_MISMATCH'
                    $ReasonCode = 'gpu_identity_mismatch'
                    $Terminal = 'CUDA_GPU_IDENTITY_MISMATCH / NO_GO'
                }
                'CUDA_PROCESS_TYPE_UNPROVABLE' {
                    $Classification = 'CUDA_PROCESS_TYPE_UNPROVABLE'
                    $ReasonCode = 'process_type_unprovable'
                    $Terminal = 'CUDA_PROCESS_TYPE_UNPROVABLE / NO_GO'
                }
                default {
                    $Classification = 'CUDA_XML_PARSE_FAILURE'
                    $ReasonCode = 'xml_parse_failure'
                    $Terminal = 'CUDA_XML_PARSE_FAILURE / NO_GO'
                }
            }
        }
    }
    return [pscustomobject][ordered]@{
        exit_code = $ExitValue
        stdout_text = $StdoutText
        stdout_utf8_byte_count = $StdoutRecord.utf8_byte_count
        stdout_sha256 = $StdoutRecord.sha256
        stderr_text = $StderrText
        stderr_utf8_byte_count = $StderrRecord.utf8_byte_count
        stderr_sha256 = $StderrRecord.sha256
        name = $Name
        uuid = $Uuid
        driver_version = $DriverVersion
        driver_model = $DriverModel
        processes = @($Processes)
        allowed_graphics_count = $AllowedGraphicsCount
        blocking_compute_count = $BlockingComputeCount
        blocking_other_count = $BlockingOtherCount
        blocking_pids = @($BlockingPids)
        classification = $Classification
        reason_code = $ReasonCode
        terminal = $Terminal
    }
}
```

`ConvertTo-A11GpuObservationCore` must implement this exact precedence and closed shape:

1. `StartSucceeded = false` -> `CUDA_QUERY_START_FAILURE / NO_GO`.
2. null/nonzero exit -> `CUDA_QUERY_FAILURE / NO_GO`.
3. decoder throws `CUDA_GPU_IDENTITY_MISMATCH` -> same terminal plus ` / NO_GO`.
4. decoder throws `CUDA_PROCESS_TYPE_UNPROVABLE` -> same terminal plus ` / NO_GO`.
5. every other decoder exception -> `CUDA_XML_PARSE_FAILURE / NO_GO`.
6. decoded success -> copy the admission result.

Use these exact classification/reason pairs: `CUDA_QUERY_START_FAILURE` / `native_start_failed`, `CUDA_QUERY_FAILURE` / `native_exit_nonzero`, `CUDA_GPU_IDENTITY_MISMATCH` / `gpu_identity_mismatch`, `CUDA_PROCESS_TYPE_UNPROVABLE` / `process_type_unprovable`, `CUDA_XML_PARSE_FAILURE` / `xml_parse_failure`, `CUDA_COMPUTE_BUSY` / `compute_type_present`, `CUDA_OTHER_RESOURCE_BUSY` / `other_type_present`, and `CUDA_IDLE` / `graphics_only_or_empty`.

Every returned core contains `exit_code`, `stdout_text`, `stdout_utf8_byte_count`, lowercase `stdout_sha256`, `stderr_text`, `stderr_utf8_byte_count`, lowercase `stderr_sha256`, nullable GPU identity fields, `processes`, the three counts, `blocking_pids`, `classification`, `reason_code`, and `terminal`. Hash the exact UTF-8 bytes with no normalization. Failure cores use null identity, empty process arrays, and zero counts. `CUDA_OBSERVATION_UNPROVABLE / NO_GO` is controller-only when the nested tool result or retained evidence cannot be proven; it is never synthesized by the pure core from a completed native result.

- [ ] **Step 3: Define the single-invocation observer and prove it synthetically**

Append `Invoke-A11GpuObservation` with this exact contract:

```powershell
function Invoke-A11GpuObservation {
    [CmdletBinding()]
    param([AllowNull()][scriptblock]$NativeRunner = $null)
    $Argv = @(
        'nvidia-smi', '-q', '-x', '-i',
        'GPU-7639cc81-2a55-164e-e5be-c5cd71752a63'
    )
    $StartedUtc = [DateTimeOffset]::UtcNow.ToString('o')
    $ObservationId = 'cuda-observation-{0}-{1}' -f `
        [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'),
        ([guid]::NewGuid().ToString('N').Substring(0, 8))
    if ($null -ne $NativeRunner) {
        $Native = & $NativeRunner $Argv
        $Core = ConvertTo-A11GpuObservationCore `
            -StartSucceeded ([bool]$Native.start_succeeded) `
            -ExitCode $Native.exit_code -StdoutText ([string]$Native.stdout_text) `
            -StderrText ([string]$Native.stderr_text)
        return [pscustomobject][ordered]@{
            schema_version = 1; observation_id = $ObservationId; argv = $Argv
            started_utc = $StartedUtc; finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
            start_succeeded = [bool]$Native.start_succeeded
            start_error_type = $Native.start_error_type
            start_error_message = $Native.start_error_message
            core = $Core
        }
    }
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = [Diagnostics.ProcessStartInfo]::new()
    $Process.StartInfo.FileName = $Argv[0]
    $Process.StartInfo.Arguments = '-q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63'
    $Process.StartInfo.UseShellExecute = $false
    $Process.StartInfo.CreateNoWindow = $true
    $Process.StartInfo.RedirectStandardOutput = $true
    $Process.StartInfo.RedirectStandardError = $true
    $Utf8 = [Text.UTF8Encoding]::new($false)
    $Process.StartInfo.StandardOutputEncoding = $Utf8
    $Process.StartInfo.StandardErrorEncoding = $Utf8
    try {
        try {
            if (-not $Process.Start()) { throw 'native process start returned false' }
        } catch {
            $Core = ConvertTo-A11GpuObservationCore -StartSucceeded $false `
                -ExitCode $null -StdoutText '' -StderrText ''
            return [pscustomobject][ordered]@{
                schema_version = 1; observation_id = $ObservationId; argv = $Argv
                started_utc = $StartedUtc; finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
                start_succeeded = $false
                start_error_type = $_.Exception.GetType().FullName
                start_error_message = $_.Exception.Message
                core = $Core
            }
        }
        $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
        $StderrTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        $Stdout = $StdoutTask.GetAwaiter().GetResult()
        $Stderr = $StderrTask.GetAwaiter().GetResult()
        $Core = ConvertTo-A11GpuObservationCore -StartSucceeded $true `
            -ExitCode $Process.ExitCode -StdoutText $Stdout -StderrText $Stderr
        return [pscustomobject][ordered]@{
            schema_version = 1; observation_id = $ObservationId; argv = $Argv
            started_utc = $StartedUtc; finished_utc = [DateTimeOffset]::UtcNow.ToString('o')
            start_succeeded = $true; start_error_type = $null; start_error_message = $null
            core = $Core
        }
    } finally {
        $Process.Dispose()
    }
}
```

Before any real query, run exact synthetic XML fixtures through the pure functions and the injected runner. Fixtures must use the standard external declaration without `--dtd` embedding:

```xml
<?xml version="1.0"?>
<!DOCTYPE nvidia_smi_log SYSTEM "nvsmi_device_v12.dtd">
<nvidia_smi_log>
  <driver_version>591.59</driver_version>
  <attached_gpus>1</attached_gpus>
  <gpu id="00000000:01:00.0">
    <product_name>NVIDIA GeForce RTX 4090</product_name>
    <uuid>GPU-7639cc81-2a55-164e-e5be-c5cd71752a63</uuid>
    <driver_model><current_dm>WDDM</current_dm><pending_dm>WDDM</pending_dm></driver_model>
    <processes>N/A</processes>
  </gpu>
</nvidia_smi_log>
```

Require these exact cases:

| Fixture mutation | Expected terminal |
| --- | --- |
| no rows | `CUDA_IDLE / PASS` |
| one `G` row with `[N/A]` | `CUDA_IDLE / PASS` |
| one `G` row with `64 MiB` | `CUDA_IDLE / PASS` |
| one `O` row | `CUDA_OTHER_RESOURCE_BUSY / NO_GO` |
| one each of `C`, `M`, `C+G`, `M+C` | `CUDA_COMPUTE_BUSY / NO_GO` |
| compute row with `[N/A]` | `CUDA_COMPUTE_BUSY / NO_GO` |
| type `UNKNOWN` or missing type | `CUDA_PROCESS_TYPE_UNPROVABLE / NO_GO` |
| wrong UUID/name/driver model or two GPU nodes | `CUDA_GPU_IDENTITY_MISMATCH / NO_GO` |
| truncated XML, internal subset, `<!ENTITY>`, or over 8 MiB | `CUDA_XML_PARSE_FAILURE / NO_GO` |
| injected start failure | `CUDA_QUERY_START_FAILURE / NO_GO` |
| injected exit 9 | `CUDA_QUERY_FAILURE / NO_GO` |

Use an injected runner counter and require exactly one invocation. Parse the complete helper source under PowerShell 7 and Windows PowerShell 5.1. Scan it for process/service mutation, GPU reset, driver-mode change, retry loops, `Start-Sleep`, pipelines around `nvidia-smi`, the old `--query-compute-apps` token, and program-name policy. Require exactly one `nvidia-smi` token in the observer body.

- [ ] **Step 4: Append the immutable preservation and external-envelope gate**

Append the exact five-run inventory work required by prior-plan Task 1 Step 4, blob lines 393-402, including its immutable reference to ordering-plan Task 1 Steps 2-4. Append prior-plan Task 1 Step 5, blob lines 403-451, but replace its PID-only observer call with:

```powershell
$CudaObservation = Invoke-A11GpuObservation
$CudaJson = $CudaObservation | ConvertTo-Json -Depth 12 -Compress
$CudaBytes = [Text.UTF8Encoding]::new($false).GetBytes($CudaJson)
$CudaHasher = [Security.Cryptography.SHA256]::Create()
try {
    $CudaSha256 = (($CudaHasher.ComputeHash($CudaBytes) |
        ForEach-Object { $_.ToString('x2') }) -join '')
} finally {
    $CudaHasher.Dispose()
}
[pscustomobject][ordered]@{
    cuda_observation = $CudaObservation
    canonical_json_byte_count = $CudaBytes.Length
    canonical_json_sha256 = $CudaSha256
} | ConvertTo-Json -Depth 14 -Compress | Write-Output
if ($CudaObservation.core.terminal -cne 'CUDA_IDLE / PASS') {
    throw $CudaObservation.core.terminal
}
```

Require Docker `linux|29.6.1`, the exact three A11 images, six lease-history hashes, zero active lease, zero project container, zero validation run, 64,306 historical files with frozen digest, 21 historical images with frozen digest, and no dependency-diagnostic identity. Do not create the diagnostic parent.

- [ ] **Step 5: Freeze the exact command evidence before execution**

Before running the entry script:

```powershell
$CommandPath = '.superpowers/sdd/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery/task-1-entry-gate.ps1'
$CommandBytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $CommandPath))
$CommandSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $CommandPath).Hash.ToLowerInvariant()
$LiteralPayload = "& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -NonInteractive -File '$((Resolve-Path -LiteralPath $CommandPath).Path)'"
```

Record `$LiteralPayload`, the complete script source in a fenced block, byte count, and digest in `task-1-report.md` before the tool call. Verify the saved report contains them. Do not edit or regenerate the command file after hashing.

- [ ] **Step 6: Execute the complete entry gate exactly once**

Run only the recorded literal payload. Capture the nested tool result object. If it yields a session, resume only that same session until completion. Never start a replacement command.

Closed outcomes are:

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

- [ ] **Step 7: Run the complete CPU baseline only after PASS**

Materialize and hash `task-1-cpu-baseline.ps1` with exactly:

```powershell
$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw 'CPU baseline failed' }
```

Record its literal payload/source/bytes/hash before execution, run it once, and require exit 0 with exact passed/skipped totals.

- [ ] **Step 8: Publish the ignored entry report and close Task 1**

The report records every literal command/result, script source and digest, all frozen comparisons, complete observation JSON and digest, CPU totals when reached, every session/poll result, and exactly one terminal:

```text
ENTRY_GATE_PASS
```

or the first exact `NO_GO`. Afterwards require linked and canonical worktrees clean, staging empty, and no `__pycache__`, `.pyc`, `.pytest_cache`, runtime artifact, or diagnostic directory inside the repository, excluding the ignored `.venv` tree and this plan's ignored SDD workspace.

`ENTRY_GATE_PASS` is the only result that permits Task 2.

---

### Task 2: Add RED type-aware XML and inherited ordering tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: Task 1 helper names and terminals; immutable prior-plan Task 2 at blob lines 481-497
- Produces: RED tests for secure XML, exact type admission, single invocation, launcher call-site integration, versioned registry, vectors, and generic verifier

- [ ] **Step 1: Add XML fixture construction and pure classifier RED tests**

Add `_nvidia_smi_xml(processes: list[tuple[int, str, str, str]] | None, *, uuid: str = _GPU, name: str = "NVIDIA GeForce RTX 4090", driver_model: str = "WDDM") -> str`. It must emit the exact Task 1 XML shape and one `<process_info>` per tuple `(pid, type, process_name, used_memory)`; `None` emits `<processes>N/A</processes>`.

Add parameterized tests using `_invoke_functions` for:

```python
@pytest.mark.parametrize(
    ("process_type", "used_memory", "terminal"),
    [
        ("G", "[N/A]", "CUDA_IDLE / PASS"),
        ("G", "64 MiB", "CUDA_IDLE / PASS"),
        ("O", "[N/A]", "CUDA_OTHER_RESOURCE_BUSY / NO_GO"),
        ("C", "[N/A]", "CUDA_COMPUTE_BUSY / NO_GO"),
        ("M", "[N/A]", "CUDA_COMPUTE_BUSY / NO_GO"),
        ("C+G", "[N/A]", "CUDA_COMPUTE_BUSY / NO_GO"),
        ("M+C", "[N/A]", "CUDA_COMPUTE_BUSY / NO_GO"),
    ],
)
def test_wddm_process_type_is_authoritative(
    process_type: str, used_memory: str, terminal: str
) -> None:
    xml = _nvidia_smi_xml([(4321, process_type, "fixture.exe", used_memory)])
    completed = _invoke_functions(
        (
            "Get-A11XmlSingleText",
            "ConvertFrom-A11NvidiaSmiXml",
            "ConvertTo-A11GpuAdmission",
        ),
        f"""
$Decoded = ConvertFrom-A11NvidiaSmiXml -XmlText {_ps(xml)}
$Admission = ConvertTo-A11GpuAdmission -Decoded $Decoded
[ordered]@{{
    terminal = $Admission.terminal
    allowed_graphics_count = $Admission.allowed_graphics_count
    blocking_compute_count = $Admission.blocking_compute_count
    blocking_other_count = $Admission.blocking_other_count
    blocking_pids_text = (@($Admission.blocking_pids) -join ',')
}} | ConvertTo-Json -Compress
""",
    )
    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    is_graphics = process_type == "G"
    is_other = process_type == "O"
    assert result == {
        "terminal": terminal,
        "allowed_graphics_count": int(is_graphics),
        "blocking_compute_count": int(not is_graphics and not is_other),
        "blocking_other_count": int(is_other),
        "blocking_pids_text": "" if is_graphics else "4321",
    }
```

The body invokes `ConvertFrom-A11NvidiaSmiXml`, then `ConvertTo-A11GpuAdmission`, and asserts exact terminal/counts/PIDs. Also add empty-process, duplicate-row, name-independence, and PID-order preservation cases.

- [ ] **Step 2: Add fail-closed XML and query RED tests**

Add individual tests for missing/unknown type, malformed PID, wrong name/UUID/driver model, multiple GPU nodes, missing driver version, missing processes node, truncated XML, internal DTD subset, entity declaration/reference, oversized XML, start failure, and exit 9. Assert the exact Task 1 terminal for each.

Add an injected runner test that increments a PowerShell counter, returns one synthetic result, invokes `Invoke-A11GpuObservation -NativeRunner`, and asserts the counter is exactly `1` and argv equals:

```json
["nvidia-smi","-q","-x","-i","GPU-7639cc81-2a55-164e-e5be-c5cd71752a63"]
```

- [ ] **Step 3: Add launcher integration and forbidden-fallback RED tests**

Update the structural test to require exactly one definition of each new helper, exactly one native `nvidia-smi` literal in the observer, and calls from global preflight and phase initialization. Require source absence of `--query-compute-apps`, the old numeric-memory admission branch, executable-name allowlists, retry loops, process/service mutation, GPU reset, and driver-model mutation.

Require the closed preflight evidence key `gpu_observation` and reject the old `gpu_rows` key. Require phase `01-gpu-preflight.json` to contain the structured observation and digest rather than the old four-field record.

- [ ] **Step 4: Execute the exact inherited ordering RED task**

Execute prior-plan Task 2, blob lines 481-497, including its immutable ordering-plan Task 2 reference. Add the exact algorithm-version, registry, schema, attempt-5 vector, negative attempt-1 v2 vector, and generic verifier RED tests. Do not commit.

- [ ] **Step 5: Run focused RED and prove failure reasons**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
    -k 'wddm or gpu_observation or preserved_attempt or inventory_algorithm or registry'
```

Require failures for missing new functions/registry behavior, not syntax, fixture, collection, or environment errors. Do not weaken assertions to obtain RED.

---

### Task 3: Implement the shared XML observer and inherited ordering recovery

**Files:**
- Create: `configs/a11/preserved-attempts.json`
- Create: `schemas/a11-preserved-attempts.schema.json`
- Modify: `scripts/run_wave0_a11.ps1`
- Modify: `tests/gates/test_wave0_a11_launcher.py` only for a test defect proven during GREEN

**Interfaces:**
- Consumes: every RED test from Task 2 and immutable prior-plan Task 3 at blob lines 498-508
- Produces: production helpers with Task 1 signatures, `gpu_observation` preflight evidence, full phase observation audit, versioned registry/verifier, and GREEN launcher tests

- [ ] **Step 1: Implement the secure decoder and pure classifier**

Add the exact Task 1 `Get-A11XmlSingleText`, `ConvertFrom-A11NvidiaSmiXml`, and `ConvertTo-A11GpuAdmission` behavior to `scripts/run_wave0_a11.ps1`. Use ordinal field names and arrays exactly as specified. Do not parse human-readable tables, use process names, or inspect memory text for admission.

- [ ] **Step 2: Implement core result construction and the single native observer**

Implement `Get-A11Utf8StreamRecord` and `ConvertTo-A11GpuObservationCore` with the exact byte hashing, precedence, and shape from Task 1. Implement `Invoke-A11GpuObservation` with the exact argv and default `System.Diagnostics.Process` boundary. The optional `NativeRunner` exists only for injected CPU tests; production callers omit it.

Compute and retain stdout/stderr UTF-8 byte counts and SHA-256 values in the returned observation. Retain the exact nested `core` shape in production; do not flatten or duplicate any classification field outside `core`.

- [ ] **Step 3: Integrate global preflight and phase gates**

In `Resolve-A11Worktree`, replace `$GpuCsv`, `$ComputeCsv`, and `ConvertTo-A11GpuRows` with one `Invoke-A11GpuObservation`. Return it under `gpu_observation`; remove `gpu_rows`.

In `Test-A11ReadOnlyPreflight`, replace the `gpu_rows` key/validation with closed validation of `gpu_observation.schema_version = 1`, exact GPU name/UUID/WDDM model, and `core.terminal = 'CUDA_IDLE / PASS'`. Retain independent zero project-container and active-lease checks.

In phase initialization, replace both CSV calls with a distinct `Invoke-A11GpuObservation`, require PASS, set `Identity.gpu_driver` from the observation, and write the complete canonical observation to `audit/01-gpu-preflight.json` before recording its file record. Do not change lease ordering or acquire a lease before this gate.

Update the `Invoke-A11Campaign` closed preflight key list from `gpu_rows` to `gpu_observation`.

- [ ] **Step 4: Execute the exact inherited ordering GREEN task**

Execute prior-plan Task 3, blob lines 498-508, including its immutable ordering-plan Task 3 reference. Create the exact registry/schema and implement version-aware inventory, loader/verifier, and byte guard. Keep all frozen counts/digests and vector semantics exact. Do not commit.

- [ ] **Step 5: Run focused GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
    -k 'wddm or gpu_observation or preserved_attempt or inventory_algorithm or registry'
```

Require exit 0.

- [ ] **Step 6: Run complete launcher GREEN and parser gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Parse the complete modified launcher under PowerShell 7 and Windows PowerShell 5.1. Require zero parser errors. Do not commit.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files and interfaces:** Prior-plan Task 4, blob lines 509-520.

- [ ] **Step 1: Execute the exact inherited task**

Read the task from immutable blob `98385de8453b4f5d80b7dc9a91d01c5aa3c5752b` and execute every step. Require specified success/retry/exhaustion/CLI cases to fail for the intended missing wrapper behavior. Do not commit.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files and interfaces:** Prior-plan Task 5, blob lines 521-532.

- [ ] **Step 1: Execute the exact inherited task**

Execute every step from immutable blob `98385de8453b4f5d80b7dc9a91d01c5aa3c5752b`. Require wrapper GREEN, launcher/Docker assertions GREEN, PowerShell parser gates PASS, and `docker buildx build --check` PASS without stage execution or export. Do not commit.

---

### Task 6: Verify, review, and create the single implementation commit

**Files:** Exact seven-path implementation allowlist; no other tracked path.

**Interfaces:**
- Consumes: uncommitted Tasks 2-5 and Task 1 type-aware entry observation
- Produces: one reviewed implementation commit whose parent is this plan commit

- [ ] **Step 1: Execute inherited verification and scope gates**

Execute prior-plan Task 6 Step 1, blob lines 541-546, including every verification inherited from ordering-plan Task 6 Steps 1-3. Require all CPU suites, XML security/type tests, registry/schema/vector tests, wrapper tests, algorithm/style/lock/parser/Dockerfile/whitespace gates, exact seven-path allowlist, empty staging before review, and forbidden-capability scans to pass.

Additionally require:

```powershell
$Source = Get-Content -Raw -LiteralPath 'scripts/run_wave0_a11.ps1'
if ([regex]::Matches($Source, "'nvidia-smi'").Count -ne 1 -or
    [regex]::Matches($Source, 'FileName\s*=\s*\$Argv\[0\]').Count -ne 1) {
    throw 'native nvidia-smi definition count mismatch'
}
if ($Source -match '--query-compute-apps|--format=csv|Stop-Process|taskkill|nvidia-smi\s+-r|--gpu-reset|--driver-model') {
    throw 'forbidden GPU fallback or mutation token found'
}
```

- [ ] **Step 2: Re-run complete preservation with one new type-aware observation**

Materialize a new Task 6 preservation command file before execution. Re-prove the Task 1 lineage, identity, isolation, immutable plan/design blobs, lockfile digest, and canonical-worktree cleanliness. The linked worktree is intentionally dirty at this point: require empty staging, no unexpected untracked path, and an exact tracked diff equal to the seven-path implementation allowlist instead of applying Task 1's clean-worktree and baseline implementation-blob assertions.

Parse the uncommitted `scripts/run_wave0_a11.ps1` AST, require exactly one definition of every Task 1 observation helper, evaluate only those definitions, run the synthetic matrix, and invoke that candidate's `Invoke-A11GpuObservation` for the one live query. Do not copy the plan-local helper into this command and do not dot-source or invoke the launcher entry point. Execute every non-GPU preservation check from Task 1 Step 4, then apply Task 1 Steps 5-6 command-retention and single-execution rules. Record literal payload/source/bytes/hash/result. This is a distinct scheduled gate and starts exactly one native process.

Compare all frozen artifact/image/lease/historical fields with the Task 1 entry report. Require exact stable-field equality and `CUDA_IDLE / PASS`. Observation ID, timestamps, raw streams, process rows, JSON byte count, and digest are new evidence and need not equal Task 1.

Do not compare or reinterpret the superseded prior PID-only `CUDA_COMPUTE_BUSY` observation.

- [ ] **Step 3: Perform cold requirements and code review**

Execute prior-plan Task 6 Step 3, blob lines 558-563, adding this design, this plan, XML decoder safety, exact process-type table, `O` blocking, one-invocation proof, command retention, and both launcher call sites to the review set.

Require `Critical=0` and `Important=0`. Resolve each finding with RED/GREEN and re-run every affected gate. Do not change any prior report or frozen artifact.

- [ ] **Step 4: Stage exactly seven paths and commit once**

Before staging:

```powershell
$ExpectedPlan = (git rev-parse HEAD).Trim()
if ((git rev-parse "$ExpectedPlan^").Trim() -cne
    '0053a8b30c8639ea9b9752ca2171117692fe78b0') {
    throw 'implementation parent candidate is not this recovery plan'
}
```

Execute prior-plan Task 6 staging/commit rules, blob lines 565-579. Stage exactly the seven paths and use commit message:

```text
fix: harden A11 recovery boundaries
```

Use the required author/committer identity. Create no other implementation commit.

- [ ] **Step 5: Verify exact committed lineage and candidate**

```powershell
$Implementation = (git rev-parse HEAD).Trim()
$RecoveryPlan = (git rev-parse 'HEAD^').Trim()
$RecoveryDesign = (git rev-parse 'HEAD^^').Trim()
$PriorPlan = (git rev-parse 'HEAD^^^').Trim()
$PriorDesign = (git rev-parse 'HEAD^^^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^^^').Trim()
if (
    $RecoveryDesign -cne '0053a8b30c8639ea9b9752ca2171117692fe78b0' -or
    $PriorPlan -cne 'f45d84eec13b98ee4566497252375f20251fd2d3' -or
    $PriorDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f'
) { throw 'committed candidate lineage mismatch' }
$RecoveryPlanPaths = @(git diff-tree --no-commit-id --name-only -r $RecoveryPlan)
if ($RecoveryPlanPaths.Count -ne 1 -or $RecoveryPlanPaths[0] -cne
    'docs/superpowers/plans/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery.md') {
    throw 'committed recovery plan path mismatch'
}
```

Require exact seven paths, exact identity, clean linked/canonical worktrees, empty staging, fixed `uv.lock`, unchanged preservation evidence, focused and full CPU suites, parser gates, schema validation, Dockerfile `--check`, and `git show --check HEAD`.

The only claim is eligibility for the single dependency-only diagnostic. Do not claim formal A11 runtime success.

---

### Task 7: Execute and preserve exactly one dependency-only diagnostic

**Files:**
- Modify in repository: none
- Create outside repository/artifact root: one append-only directory beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`
- Docker effect: BuildKit cache data only; no image export

**Interfaces:**
- Consumes: clean Task 6 implementation commit and Docker target `a11-dependencies`
- Produces: `A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED` or `A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN`

- [ ] **Step 1: Prove one-shot diagnostic eligibility and extended lineage**

Execute prior-plan Task 7 Step 1, blob lines 620-650, replacing its lineage with:

```powershell
$Source = (git rev-parse HEAD).Trim()
$RecoveryPlan = (git rev-parse 'HEAD^').Trim()
$RecoveryDesign = (git rev-parse 'HEAD^^').Trim()
$PriorCudaPlan = (git rev-parse 'HEAD^^^').Trim()
$PriorCudaDesign = (git rev-parse 'HEAD^^^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^^^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^^^^^').Trim()
if (
    $RecoveryDesign -cne '0053a8b30c8639ea9b9752ca2171117692fe78b0' -or
    $PriorCudaPlan -cne 'f45d84eec13b98ee4566497252375f20251fd2d3' -or
    $PriorCudaDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
) { throw 'dependency diagnostic lineage mismatch' }
```

Complete Task 6 Step 5 verification. Materialize and record one type-aware pre-diagnostic observation command that AST-loads the observation helpers from the committed `scripts/run_wave0_a11.ps1` without invoking the launcher entry point. Require exact helper-definition counts, the synthetic matrix, `CUDA_IDLE / PASS`, zero project containers, zero active leases, and no diagnostic identity for `$Source`. Failure stops before identity creation and Docker execution.

- [ ] **Step 2: Create the exact append-only diagnostic identity**

Execute prior-plan Task 7 Step 2, blob lines 652-670. Add these recovery-lineage fields ahead of its existing lineage fields:

```text
wddm_type_aware_recovery_plan_commit = $RecoveryPlan
wddm_type_aware_recovery_design_commit = 0053a8b30c8639ea9b9752ca2171117692fe78b0
cuda_observability_recovery_plan_commit = f45d84eec13b98ee4566497252375f20251fd2d3
cuda_observability_recovery_design_commit = 5451c50cc20b1c297c9bdd3535a793eff993158d
```

Retain every prior exact identity field and create-new/no-clobber rule. Do not include an owner ID, run ID, GPU request, or formal runtime authorization.

- [ ] **Step 3: Invoke the dependency diagnostic exactly once**

Execute prior-plan Task 7 Step 3, blob lines 672-676, verbatim. Materialize and hash the command before execution. Do not wrap, retry, relaunch, automate, or repeat the single:

```text
docker buildx build --no-cache --progress=plain --target a11-dependencies --output=type=cacheonly
```

- [ ] **Step 4: Publish result, manifest, and closure**

Execute prior-plan Task 7 Step 4, blob lines 678-681, verbatim. A nonzero build result is diagnostic `NO_GO`, not permission to retry.

- [ ] **Step 5: Re-prove preservation with one scheduled post-diagnostic observation**

Execute prior-plan Task 7 Step 5, blob lines 683-706, replacing its structured observer with the committed type-aware helper loaded by the same AST-only boundary as Step 1. Materialize and record this post command before execution. It is a distinct preservation gate, not a retry, and runs only after the single Docker diagnostic actually started, even when that diagnostic returned nonzero.

Require unchanged repository/artifact/image/lease/container/runtime state and zero exported tagged or dangling image. Report exactly one terminal:

```text
A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
```

or:

```text
A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

Stop in either case. A later formal runtime attempt requires separate explicit owner authorization bound to the exact implementation source, original A11 specification, original A11 plan, and branch.
