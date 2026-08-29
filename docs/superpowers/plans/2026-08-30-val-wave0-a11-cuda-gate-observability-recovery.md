# Wave 0 A11 CUDA-Gate Observability Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for inherited Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before every terminal or commit claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the ambiguous A11 CUDA entry check with a structured, non-mutating observation, then execute the already approved ordering-recovery implementation and dependency-only diagnostic only if a fresh complete entry gate passes.

**Architecture:** This plan is a narrow normative overlay on the immutable ordering-recovery plan blob `901c2b31c033d44949915d2081a8cf715fd2e699`. Task 1 is replaced with a fresh full gate whose plan-local PowerShell helper captures one `nvidia-smi` result and classifies query failure separately from numeric compute occupancy; inherited Tasks 2-7 remain byte-for-byte normative except for the explicit lineage and preservation replacements in this plan.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery-design.md` at commit `5451c50cc20b1c297c9bdd3535a793eff993158d`.
- This plan commit must be the direct child of that design commit and add only this plan file.
- The ordering-recovery plan remains immutable at commit `52fe25d529f7d64e986864576653d0d14a6e484b`, blob `901c2b31c033d44949915d2081a8cf715fd2e699`.
- The ordering-recovery design remains immutable at `68f51519d2cb480200ca4fef740651b0d15dd76f`.
- The digest-recovery design and plan remain immutable at `2db13d302da97a241daeaba3578cd9cec1c8073b` and `03115325f36da31b135b4593fb8df1689eac9a35`.
- The diagnostic-root erratum, runtime-transport design, and runtime-transport plan remain immutable at `101bb79369399cc3947f1c667f0a11988f916638`, `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`, and `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`.
- The preserved Task 1 terminal at source `52fe25d529f7d64e986864576653d0d14a6e484b` remains `CUDA process gate failed / NO_GO`; never reinterpret or overwrite it.
- The implementation must be one append-only commit, the direct child of this plan commit, changing exactly the seven implementation paths listed below. Tasks 1-5 create no commits.
- Author and committer must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean evidence, push, merge, tag, release, or modify another repository.
- The artifact root `D:\vision-active-learning-loop-artifacts\wave0` is read-only. A mismatch is a stop condition, never a repair instruction.
- Never terminate, pause, signal, reprioritize, or otherwise mutate an observed GPU process. Do not use `Stop-Process`, Task Manager automation, service control, Docker stop, WSL shutdown, or an equivalent action.
- A CUDA observation starts exactly one `nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits` native process. Do not retry, substitute, wrap in a pipeline, add a timeout, or infer PASS from missing output.
- Do not invoke `scripts/run_wave0_a11.ps1`, generate or guess an `OwnerAuthorizationId`, acquire a GPU lease, initialize a model, create a calibration or validation identity, access RDD, or start Wave 1.
- Consumed owners `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` remain immutable evidence. Test-only owner values must contain `TEST`.
- The only Docker invocation permitted to execute a stage is the single dependency-only diagnostic in Task 7. Tasks 5-6 may call `docker buildx build --check`, which validates without executing or exporting a stage.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` byte-identical at SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.
- Keep model, receipt, statistical, threshold, replica, split, acquisition, data-firewall, lease, validation, and Wave 1 contracts unchanged.
- CPU tests set `PYTHONDONTWRITEBYTECODE=1` and pass `-p no:cacheprovider`; they may not use network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The dependency diagnostic writes only beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`, outside the repository and artifact baseline. It has no owner ID, run ID, image export, project container, model process, or statistical meaning.
- The superseded attempt-5 digest `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448` and rejected attempt-1 universal-v2 digest `72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c` may appear only in recovery documents and negative tests.

## Normative overlay

The complete ordering-recovery plan at commit
`52fe25d529f7d64e986864576653d0d14a6e484b` and Git blob
`901c2b31c033d44949915d2081a8cf715fd2e699` is incorporated by immutable
reference. Line numbers below are one-based lines in that exact blob.

These are the only replacements:

| Contract | Superseded | Effective |
| --- | --- | --- |
| Implementation parent | ordering plan `52fe25d...` | this CUDA-observability plan commit |
| Implementation grandparent | ordering design `68f5151...` | CUDA-observability design `5451c50...` |
| Task 1 | parent-plan lines 113-438 | Task 1 in this plan |
| Task 6 source lineage | implementation -> ordering plan -> ordering design | implementation -> this plan -> CUDA design -> ordering plan -> ordering design |
| Task 6 preservation | ambiguous CUDA pipeline | structured observation from Task 1 |
| Task 7 source lineage/identity | implementation -> ordering plan -> ordering design | full extended lineage defined in Task 7 below |
| Task 7 CUDA eligibility/preservation | numeric-PID pipeline | structured pre/post observations, exactly once per distinct gate |

All other parent-plan text remains binding:

| Inherited task | Exact parent-plan lines | Status in this plan |
| --- | ---: | --- |
| Task 2 | 439-557 | execute verbatim after Task 1 PASS |
| Task 3 | 558-745 | execute verbatim after Task 2 review |
| Task 4 | 746-804 | execute verbatim after Task 3 review |
| Task 5 | 805-899 | execute verbatim after Task 4 review |
| Task 6 | 900-1046 | execute verbatim with replacements below |
| Task 7 | 1047-1183 | execute verbatim with replacements below |

This is an exact immutable reference, not an instruction to copy from the
working-tree version. Before execution, prove the blob with:

```powershell
$ParentPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md'
$ParentPlanBlob = (git rev-parse "52fe25d529f7d64e986864576653d0d14a6e484b`:$ParentPlanPath").Trim()
if ($ParentPlanBlob -cne '901c2b31c033d44949915d2081a8cf715fd2e699') {
    throw 'immutable parent plan blob mismatch'
}
```

## Frozen preservation envelope

The exact five run records, algorithms, file/directory counts, digests, image
tags/IDs, lease-history hashes, historical baselines, attempt-5 vector, and
latest-write values in parent-plan lines 40-111 remain binding.

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
- Modify `scripts/run_wave0_a11.ps1`: version-aware inventory, registry loader/verifier, byte guard, and unchanged single-build campaign path.
- Modify `docker/wave0.Dockerfile`: dependency stage, exact wrapper calls, and two locked BuildKit uv cache mounts.
- Modify `tests/gates/test_wave0_a11_launcher.py`: ordering, vector, registry, verifier, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change.

---

### Task 1: Re-prove preservation with a structured CUDA observation

**Files:**
- Modify tracked files: none
- Write ignored execution evidence: `.superpowers/sdd/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery/task-1-report.md`
- Read: Git topology, committed recovery documents, all five preserved runs, Docker/image/lease/historical state, CUDA state, and CPU tests

**Interfaces:**
- Consumes: this plan commit, design `5451c50cc20b1c297c9bdd3535a793eff993158d`, immutable parent plan blob `901c2b31c033d44949915d2081a8cf715fd2e699`
- Produces: `ENTRY_GATE_PASS` or one precise preserved `NO_GO`; on PASS, one canonical CUDA observation record for later preservation comparison

- [ ] **Step 1: Prove lineage, identity, isolation, scope, and fixed inputs**

Run from the linked worktree at this plan commit:

```powershell
$ExpectedIdentity = 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
$Plan = (git rev-parse HEAD).Trim()
$Design = (git rev-parse 'HEAD^').Trim()
$ParentPlan = (git rev-parse 'HEAD^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^^').Trim()
if ($Design -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $ParentPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5') {
    throw 'CUDA observability lineage mismatch'
}
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') {
    throw 'branch mismatch'
}
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r $Plan)
$DesignPaths = @(git diff-tree --no-commit-id --name-only -r $Design)
if ($PlanPaths.Count -ne 1 -or $PlanPaths[0] -cne
    'docs/superpowers/plans/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery.md') {
    throw 'plan path scope mismatch'
}
if ($DesignPaths.Count -ne 1 -or $DesignPaths[0] -cne
    'docs/superpowers/specs/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery-design.md') {
    throw 'design path scope mismatch'
}
foreach ($Commit in @($Plan, $Design)) {
    $Identity = (git show -s --format='%an <%ae>|%cn <%ce>' $Commit).Trim()
    if ($Identity -cne "$ExpectedIdentity|$ExpectedIdentity") { throw 'commit identity mismatch' }
}
$GitDir = (git rev-parse --absolute-git-dir).Trim()
$CommonDir = (Resolve-Path -LiteralPath (git rev-parse --git-common-dir).Trim()).Path
if ($GitDir -ceq $CommonDir) { throw 'linked worktree isolation missing' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
$Canonical = ((git worktree list --porcelain | Where-Object { $_ -clike 'worktree *' } |
    Select-Object -First 1).Substring(9))
if (@(git -C $Canonical status --porcelain=v1 --untracked-files=all).Count -ne 0) {
    throw 'canonical worktree dirty'
}
if ((Get-FileHash -Algorithm SHA256 -LiteralPath 'uv.lock').Hash.ToLowerInvariant() -cne
    '530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93') {
    throw 'uv.lock digest mismatch'
}
$ParentPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md'
if ((git rev-parse "$ParentPlan`:$ParentPlanPath").Trim() -cne
    '901c2b31c033d44949915d2081a8cf715fd2e699') {
    throw 'immutable parent plan blob mismatch'
}
```

Stop without repair on any mismatch.

- [ ] **Step 2: Define and prove the plan-local classifier**

Define this pure classifier before any external-state read:

```powershell
function ConvertTo-A11CudaObservationCore {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][bool]$StartSucceeded,
        [AllowNull()][object]$ExitCode,
        [Parameter(Mandatory)][AllowEmptyString()][string]$StdoutText,
        [Parameter(Mandatory)][AllowEmptyString()][string]$StderrText
    )
    $NumericPids = @($StdoutText -split '\r?\n' |
        Where-Object { $_ -match '^\s*[0-9]+\s*$' } |
        ForEach-Object { [long]::Parse($_.Trim(), [Globalization.CultureInfo]::InvariantCulture) })
    if (-not $StartSucceeded) {
        $Classification = 'CUDA_QUERY_START_FAILURE'
        $Terminal = 'CUDA_QUERY_START_FAILURE / NO_GO'
        $ExitValue = $null
    } elseif ($null -eq $ExitCode -or [int]$ExitCode -ne 0) {
        $Classification = 'CUDA_QUERY_FAILURE'
        $Terminal = 'CUDA_QUERY_FAILURE / NO_GO'
        $ExitValue = if ($null -eq $ExitCode) { $null } else { [int]$ExitCode }
    } elseif ($NumericPids.Count -ne 0) {
        $Classification = 'CUDA_COMPUTE_BUSY'
        $Terminal = 'CUDA_COMPUTE_BUSY / NO_GO'
        $ExitValue = 0
    } else {
        $Classification = 'CUDA_IDLE'
        $Terminal = 'CUDA_IDLE / PASS'
        $ExitValue = 0
    }
    [pscustomobject][ordered]@{
        exit_code = $ExitValue
        stdout_text = $StdoutText
        stderr_text = $StderrText
        numeric_pids = @($NumericPids)
        numeric_pid_count = $NumericPids.Count
        classification = $Classification
        terminal = $Terminal
    }
}
```

Run these exact synthetic cases:

```powershell
$Cases = @(
    @{ start=$false; exit=$null; stdout=''; stderr='missing'; class='CUDA_QUERY_START_FAILURE'; terminal='CUDA_QUERY_START_FAILURE / NO_GO'; pids=@() },
    @{ start=$true; exit=9; stdout="123`n"; stderr='driver failure'; class='CUDA_QUERY_FAILURE'; terminal='CUDA_QUERY_FAILURE / NO_GO'; pids=@(123) },
    @{ start=$true; exit=0; stdout=''; stderr=''; class='CUDA_IDLE'; terminal='CUDA_IDLE / PASS'; pids=@() },
    @{ start=$true; exit=0; stdout="123`r`n"; stderr=''; class='CUDA_COMPUTE_BUSY'; terminal='CUDA_COMPUTE_BUSY / NO_GO'; pids=@(123) },
    @{ start=$true; exit=0; stdout="17`n17`nnoise`n5`n"; stderr=''; class='CUDA_COMPUTE_BUSY'; terminal='CUDA_COMPUTE_BUSY / NO_GO'; pids=@(17,17,5) },
    @{ start=$true; exit=0; stdout="No running processes found`n"; stderr=''; class='CUDA_IDLE'; terminal='CUDA_IDLE / PASS'; pids=@() },
    @{ start=$true; exit=0; stdout=''; stderr='warning'; class='CUDA_IDLE'; terminal='CUDA_IDLE / PASS'; pids=@() }
)
foreach ($Case in $Cases) {
    $Observed = ConvertTo-A11CudaObservationCore -StartSucceeded $Case.start `
        -ExitCode $Case.exit -StdoutText $Case.stdout -StderrText $Case.stderr
    if ($Observed.classification -cne $Case.class -or $Observed.terminal -cne $Case.terminal -or
        (($null -eq $Observed.exit_code) -ne ($null -eq $Case.exit)) -or
        ($null -ne $Observed.exit_code -and [int]$Observed.exit_code -ne [int]$Case.exit) -or
        $Observed.stdout_text -cne $Case.stdout -or $Observed.stderr_text -cne $Case.stderr -or
        $Observed.numeric_pid_count -ne $Case.pids.Count -or
        (($Observed.numeric_pids | ConvertTo-Json -Compress) -cne
         ($Case.pids | ConvertTo-Json -Compress))) {
        throw "CUDA classifier self-test failed: $($Case.class)"
    }
}
```

Require all seven cases to pass. This is a plan-local in-memory self-test, not
a tracked implementation edit.

- [ ] **Step 3: Define the single-invocation observer and metadata enrichment**

Define these functions in the same PowerShell process as Step 2:

```powershell
function Get-A11CudaProcessMetadata {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][long[]]$NumericPids,
        [scriptblock]$Lookup = {
            param([long]$NumericPid)
            Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $NumericPid" `
                -ErrorAction SilentlyContinue
        }
    )
    $Rows = [Collections.Generic.List[object]]::new()
    foreach ($NumericPid in $NumericPids) {
        $Row = @(& $Lookup $NumericPid) |
            Select-Object -First 1
        if ($null -eq $Row) {
            $Rows.Add([pscustomobject][ordered]@{
                pid=$NumericPid; lookup_state='exited_or_unavailable'; name=$null
                parent_pid=$null; creation_time_utc=$null
            })
        } else {
            $Created = if ($null -eq $Row.CreationDate) { $null } else {
                ([datetime]$Row.CreationDate).ToUniversalTime().ToString('o')
            }
            $Rows.Add([pscustomobject][ordered]@{
                pid=$NumericPid; lookup_state='observed'; name=[string]$Row.Name
                parent_pid=[long]$Row.ParentProcessId; creation_time_utc=$Created
            })
        }
    }
    @($Rows)
}

function Invoke-A11CudaObservation {
    [CmdletBinding()]
    param()
    $Argv = @('nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits')
    $StartedUtc = [DateTimeOffset]::UtcNow.ToString('o')
    $ObservationId = 'cuda-observation-{0}-{1}' -f `
        [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ'),
        ([guid]::NewGuid().ToString('N').Substring(0,8))
    $Process = [Diagnostics.Process]::new()
    $Process.StartInfo = [Diagnostics.ProcessStartInfo]::new()
    $Process.StartInfo.FileName = $Argv[0]
    $Process.StartInfo.Arguments = ($Argv[1..($Argv.Count - 1)] -join ' ')
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
            $Core = ConvertTo-A11CudaObservationCore -StartSucceeded $false -ExitCode $null `
                -StdoutText '' -StderrText ''
            return [pscustomobject][ordered]@{
                schema_version=1; observation_id=$ObservationId; argv=$Argv
                started_utc=$StartedUtc; finished_utc=[DateTimeOffset]::UtcNow.ToString('o')
                start_succeeded=$false; start_error_type=$_.Exception.GetType().FullName
                start_error_message=$_.Exception.Message; exit_code=$Core.exit_code
                stdout_text=$Core.stdout_text; stderr_text=$Core.stderr_text
                numeric_pids=$Core.numeric_pids; numeric_pid_count=$Core.numeric_pid_count
                process_metadata=@(); classification=$Core.classification; terminal=$Core.terminal
            }
        }
        $StdoutTask = $Process.StandardOutput.ReadToEndAsync()
        $StderrTask = $Process.StandardError.ReadToEndAsync()
        $Process.WaitForExit()
        $Stdout = $StdoutTask.GetAwaiter().GetResult()
        $Stderr = $StderrTask.GetAwaiter().GetResult()
        $Core = ConvertTo-A11CudaObservationCore -StartSucceeded $true `
            -ExitCode $Process.ExitCode -StdoutText $Stdout -StderrText $Stderr
        $Metadata = if ($Core.numeric_pid_count -eq 0) { @() } else {
            @(Get-A11CudaProcessMetadata -NumericPids $Core.numeric_pids)
        }
        [pscustomobject][ordered]@{
            schema_version=1; observation_id=$ObservationId; argv=$Argv
            started_utc=$StartedUtc; finished_utc=[DateTimeOffset]::UtcNow.ToString('o')
            start_succeeded=$true; start_error_type=$null; start_error_message=$null
            exit_code=$Core.exit_code; stdout_text=$Core.stdout_text; stderr_text=$Core.stderr_text
            numeric_pids=$Core.numeric_pids; numeric_pid_count=$Core.numeric_pid_count
            process_metadata=$Metadata; classification=$Core.classification; terminal=$Core.terminal
        }
    } finally {
        $Process.Dispose()
    }
}
```

Before any native invocation, parse the exact function text under both
PowerShell 7 and Windows PowerShell 5.1. Also scan the three function bodies
for `Stop-Process`, `taskkill`, `Stop-Service`, `docker stop`, `wsl --shutdown`,
retry loops, `Start-Sleep`, and a second `nvidia-smi` token. Require zero
mutation/retry tokens and exactly one `nvidia-smi` token in the observer.

Prove metadata fallback without a real process by applying the exact record
shape to a synthetic missing lookup and require
`lookup_state = exited_or_unavailable`. Do not call the observer during these
self-tests.

```powershell
$FunctionSource = @(
    "function ConvertTo-A11CudaObservationCore {`n$(${function:ConvertTo-A11CudaObservationCore})`n}",
    "function Get-A11CudaProcessMetadata {`n$(${function:Get-A11CudaProcessMetadata})`n}",
    "function Invoke-A11CudaObservation {`n$(${function:Invoke-A11CudaObservation})`n}"
) -join "`n"
$Tokens = $null
$Errors = $null
[Management.Automation.Language.Parser]::ParseInput(
    $FunctionSource, [ref]$Tokens, [ref]$Errors
) | Out-Null
if ($Errors.Count -ne 0) { throw ($Errors.Message -join '; ') }
$Encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($FunctionSource))
& powershell.exe -NoProfile -NonInteractive -EncodedCommand $Encoded
if ($LASTEXITCODE -ne 0) { throw 'Windows PowerShell 5.1 parser gate failed' }
$Forbidden = '(?i)\b(Stop-Process|taskkill|Stop-Service|Start-Sleep)\b|docker\s+stop|wsl\s+--shutdown|\b(while|do)\s*[({]'
if ($FunctionSource -match $Forbidden) { throw 'CUDA observer mutation or retry token found' }
if ([regex]::Matches([string]${function:Invoke-A11CudaObservation}, 'nvidia-smi').Count -ne 1) {
    throw 'CUDA observer invocation count mismatch'
}
$Missing = @(Get-A11CudaProcessMetadata -NumericPids @(777,777) -Lookup { param($NumericPid) $null })
if ($Missing.Count -ne 2 -or @($Missing | Where-Object {
    $_.pid -ne 777 -or $_.lookup_state -cne 'exited_or_unavailable' -or $null -ne $_.name
}).Count -ne 0) { throw 'CUDA metadata fallback self-test failed' }
```

- [ ] **Step 4: Re-prove all five versioned run inventories from scratch**

Execute parent-plan Task 1 Steps 2-4, exact blob lines 177-391, in the same
PowerShell process. Do not use the previous Task 1 report, cached hashes,
sampled files, replacement constants, or a timeout.

Require all five exact frozen digests, v1 legacy sequence equality, the
attempt-1 v2 negative digest, and the attempt-5 1,283-byte committed vector.
A mismatch is immediate `PRESERVATION_MISMATCH / NO_GO`.

- [ ] **Step 5: Re-prove the external envelope and observe CUDA exactly once**

Execute parent-plan Task 1 Step 5, exact blob lines 392-424, with only this
replacement: remove the `$Compute = @(& nvidia-smi ... | Where-Object ...)`
pipeline and its combined throw. In its place call:

```powershell
$CudaObservation = Invoke-A11CudaObservation
$CudaJson = $CudaObservation | ConvertTo-Json -Depth 8 -Compress
$CudaBytes = [Text.UTF8Encoding]::new($false).GetBytes($CudaJson)
$CudaHasher = [Security.Cryptography.SHA256]::Create()
try {
    $CudaSha256 = (($CudaHasher.ComputeHash($CudaBytes) |
        ForEach-Object { $_.ToString('x2') }) -join '')
}
finally { $CudaHasher.Dispose() }
[pscustomobject][ordered]@{
    cuda_observation=$CudaObservation
    canonical_json_byte_count=$CudaBytes.Length
    canonical_json_sha256=$CudaSha256
} | ConvertTo-Json -Depth 10 -Compress | Write-Output
if ($CudaObservation.terminal -cne 'CUDA_IDLE / PASS') {
    throw $CudaObservation.terminal
}
```

The JSON line must be visible in the task transcript before any terminal
throw. Capture the nested tool result object, including `exit_code`, `output`,
`session_id`, and `chunk_id`; if a session is returned, resume only that same
session until completion. Never start a replacement command.

Require Docker `linux|29.6.1`, the exact three A11 images, six lease-history
hashes, zero active lease, zero project container, zero validation run,
64,306 historical files with the frozen digest, 21 historical images with the
frozen digest, and no dependency-diagnostic identity. Do not create the
diagnostic parent.

Closed outcomes are:

```text
CUDA_QUERY_START_FAILURE / NO_GO
CUDA_QUERY_FAILURE / NO_GO
CUDA_COMPUTE_BUSY / NO_GO
CUDA_IDLE / PASS
CUDA_OBSERVATION_UNPROVABLE / NO_GO   # controller terminal only when tool completion cannot be observed
```

Any `NO_GO` stops Task 1 without Step 6 or an implementation edit.

- [ ] **Step 6: Run the complete CPU baseline**

Run only after `CUDA_IDLE / PASS` and every preceding preservation check:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
```

Require exit 0 and record exact passed/skipped totals.

- [ ] **Step 7: Publish the ignored entry report and close Task 1**

The report records every command/result, all frozen comparisons, the complete
CUDA observation JSON and digest, test totals, and exactly one terminal:

```text
ENTRY_GATE_PASS
```

or the first exact `NO_GO` terminal. Afterwards require linked and canonical
worktrees clean, staging empty, and no `__pycache__`, `.pyc`, `.pytest_cache`,
runtime artifact, or diagnostic directory inside the repository, excluding
the ignored `.venv` tree and the ignored SDD report workspace.

`ENTRY_GATE_PASS` is the only result that permits Task 2.

---

### Task 2: Add RED algorithm-version, registry, and verifier tests

**Files and interfaces:** Parent-plan Task 2, blob lines 439-557.

- [ ] **Step 1: Execute the exact inherited task**

Read the task from the immutable blob, not the working-tree document:

```powershell
git show '52fe25d529f7d64e986864576653d0d14a6e484b:docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md'
```

Execute exact Task 2 Steps 1-6. Require focused RED for the missing versioned
registry/verifier behavior. Do not commit.

---

### Task 3: Implement versioned inventory, registry, and generic verifier

**Files and interfaces:** Parent-plan Task 3, blob lines 558-745.

- [ ] **Step 1: Execute the exact inherited task**

Execute exact Task 3 Steps 1-7 from immutable blob `901c2b31...`. Require the
focused and full launcher suites GREEN. Do not commit.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files and interfaces:** Parent-plan Task 4, blob lines 746-804.

- [ ] **Step 1: Execute the exact inherited task**

Execute exact Task 4 Steps 1-4 from immutable blob `901c2b31...`. Require the
specified success/retry/exhaustion/CLI cases to fail for the intended missing
wrapper behavior. Do not commit.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files and interfaces:** Parent-plan Task 5, blob lines 805-899.

- [ ] **Step 1: Execute the exact inherited task**

Execute exact Task 5 Steps 1-5 from immutable blob `901c2b31...`. Require
wrapper GREEN, launcher/Docker assertions GREEN, parser gates PASS, and
`docker buildx build --check` PASS without stage execution. Do not commit.

---

### Task 6: Verify, review, and create the single implementation commit

**Files:** Exact seven-path implementation allowlist; no other tracked path.

**Interfaces:**
- Consumes: uncommitted inherited Tasks 2-5 and Task 1 entry observation
- Produces: one reviewed implementation commit whose parent is this plan commit

- [ ] **Step 1: Execute inherited verification and scope gates**

Execute parent-plan Task 6 Steps 1-3, blob lines 910-993, verbatim. Require all
CPU suites, algorithm/schema/style/lock/parser/Dockerfile/whitespace gates, the
seven-path allowlist, empty staging before review, and forbidden-capability
scans to pass.

- [ ] **Step 2: Re-run complete external preservation with structured CUDA evidence**

Execute this plan's Task 1 Steps 2-5 from the uncommitted candidate. This is a
new preservation gate and has exactly one scheduled CUDA observation. Compare
the stable preservation fields with the Task 1 entry report: classification,
numeric PID count, frozen digests, image/lease records, and historical
baselines. Require `CUDA_IDLE / PASS`. The fresh `observation_id`, timestamps,
canonical JSON byte count/digest, and raw streams are new evidence and are not
required to equal the entry observation.

- [ ] **Step 3: Perform cold requirements and code review**

Execute parent-plan Task 6 Step 5, blob lines 1001-1012. Include this design and
plan in the review set. Require `Critical=0` and `Important=0`; resolve each
finding with RED/GREEN and re-run affected gates. Do not modify the plan-local
CUDA helper or prior reports as implementation code.

- [ ] **Step 4: Stage exactly seven paths and commit once**

Execute parent-plan Task 6 Step 6, blob lines 1013-1032, verbatim. Before the
commit additionally require:

```powershell
$ExpectedPlan = (git rev-parse HEAD).Trim()
if ((git rev-parse "$ExpectedPlan^").Trim() -cne
    '5451c50cc20b1c297c9bdd3535a793eff993158d') {
    throw 'implementation parent candidate is not this recovery plan'
}
```

Use commit message `fix: harden A11 recovery boundaries` and the required
author/committer identity.

- [ ] **Step 5: Verify exact committed lineage and candidate**

After commit:

```powershell
$Implementation = (git rev-parse HEAD).Trim()
$RecoveryPlan = (git rev-parse 'HEAD^').Trim()
$RecoveryDesign = (git rev-parse 'HEAD^^').Trim()
$ParentPlan = (git rev-parse 'HEAD^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^').Trim()
if ($RecoveryDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $RecoveryPlan -cne $ExpectedPlan -or
    $ParentPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f') {
    throw 'committed candidate lineage mismatch'
}
```

Require the implementation parent to be this plan commit, exact seven paths,
exact identity, clean linked/canonical worktrees, empty staging, fixed
`uv.lock`, unchanged preservation evidence, wrapper/launcher tests, parser
gates, schema validation, Dockerfile `--check`, and `git show --check HEAD`.

The only claim is eligibility for the single dependency-only diagnostic. Do
not claim formal A11 runtime success.

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

Execute parent-plan Task 7 Step 1 with this replacement lineage:

```powershell
$Source = (git rev-parse HEAD).Trim()
$RecoveryPlan = (git rev-parse 'HEAD^').Trim()
$RecoveryDesign = (git rev-parse 'HEAD^^').Trim()
$OrderingPlan = (git rev-parse 'HEAD^^^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^^^').Trim()
if ($RecoveryDesign -cne '5451c50cc20b1c297c9bdd3535a793eff993158d' -or
    $OrderingPlan -cne '52fe25d529f7d64e986864576653d0d14a6e484b' -or
    $OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5') {
    throw 'dependency diagnostic lineage mismatch'
}
```

Complete Task 6 Step 5 verification and run one structured pre-diagnostic CUDA
observation. Require `CUDA_IDLE / PASS`, zero project containers, zero active
leases, and no diagnostic identity for `$Source`. Failure stops before identity
creation and Docker execution.

- [ ] **Step 2: Create the exact append-only diagnostic identity**

Execute parent-plan Task 7 Step 2, blob lines 1086-1132, with these identity
fields replacing its recovery-lineage fields:

```text
cuda_observability_recovery_plan_commit = $RecoveryPlan
cuda_observability_recovery_design_commit = 5451c50cc20b1c297c9bdd3535a793eff993158d
ordering_recovery_plan_commit = 52fe25d529f7d64e986864576653d0d14a6e484b
ordering_recovery_design_commit = 68f51519d2cb480200ca4fef740651b0d15dd76f
digest_recovery_plan_commit = 03115325f36da31b135b4593fb8df1689eac9a35
digest_recovery_design_commit = 2db13d302da97a241daeaba3578cd9cec1c8073b
diagnostic_root_erratum_commit = 101bb79369399cc3947f1c667f0a11988f916638
runtime_transport_plan_commit = e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
runtime_transport_design_commit = db047dcb8ad602fc4ac316a743ab4ddec3168cd5
```

Retain every other exact identity field and create-new/no-clobber rule. Do not
include an owner ID, run ID, GPU request, or formal runtime authorization.

- [ ] **Step 3: Invoke the dependency diagnostic exactly once**

Execute parent-plan Task 7 Step 3, blob lines 1133-1150, verbatim. Do not wrap,
retry, relaunch, automate, or repeat the `docker buildx build --no-cache
--progress=plain --target a11-dependencies --output=type=cacheonly` invocation.

- [ ] **Step 4: Publish result, manifest, and closure**

Execute parent-plan Task 7 Step 4, blob lines 1151-1160, verbatim. A nonzero
build result is diagnostic `NO_GO`, not permission to retry.

- [ ] **Step 5: Re-prove preservation with one scheduled post-diagnostic observation**

Execute parent-plan Task 7 Step 5, blob lines 1161-1183, using this plan's
structured CUDA observation. This post-diagnostic observation is a distinct
preservation gate, not a retry of the pre-diagnostic observation. It runs only
after the single Docker diagnostic actually started, even when that diagnostic
returned nonzero.

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
