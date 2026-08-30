# Wave 0 A11 Restart-Aware Docker Readiness and Evidence-Capture Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before every terminal or commit claim. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an unavailable post-reboot Docker engine from consuming the next A11 entry-child slot, retain byte-complete evidence for every nontrivial Task 1 command, and then execute the inherited WDDM and dependency-transport recovery only after a fresh reviewed entry gate passes.

**Architecture:** A fresh ignored controller freezes the Windows boot epoch, signed PowerShell and Docker CLI identities, and exactly three stable Docker readiness samples before a child can start. The same manifest-driven recorder captures raw stdout/stderr bytes and a canonical result for every nested command; only a reviewed `ENTRY_GATE_PASS` permits the inherited seven-file TDD implementation and dependency-only diagnostic.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`, raw streams, canonical JSON, Authenticode, CIM, monotonic timing, and SHA-256; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker CLI/Engine 29.6.1 and BuildKit; uv 0.8.15; Git.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery-design.md` at commit `fc7cad720584ebd7f0813d6b8d92988126867046`, Git blob `3c131d93fdbaaf6138730eb20bec8cb882bfc0f6`, and file SHA-256 `ed096b03849f15c338b41a61b67ab7f878a094374ba03ecd3d690b9e1d561124`.
- This plan commit must be the one-file direct child of `fc7cad720584ebd7f0813d6b8d92988126867046`.
- The consumed launcher-identity plan remains immutable at commit `9a80b320a18255cb52f6988dc1feadbe78a7cb7d` and Git blob `59580ef7219af54cce400031a34ac843c76a0625`.
- The consumed launcher-identity design remains immutable at `3e98d1d56caede9a1baaf215da4e418112a73643`. The WDDM plan/design remain immutable at `42c200d8a801b142cde394cda7a0520bd9c30a83` and `0053a8b30c8639ea9b9752ca2171117692fe78b0`.
- Preserve every consumed A11 attempt, authorization identity, image, lease, artifact, diagnostic, report, command file, review package, finding, digest, and terminal. Do not modify the earlier hard-coded-launcher or restart-affected workspaces.
- The restart-affected terminal remains exactly `CUDA_OBSERVATION_UNPROVABLE / NO_GO`. Its launcher helper is 19,471 bytes / `45b53859a33b9ddbbad6fbac85bcd1f148370f0d1597b07bcf08e9f259e4231e`; revalidator 14,918 / `1480c99c32857a780d61cfc18145313ef68f5a5d44d8f9236fe030b98a6045c6`; entry script 58,392 / `95e517792de222fdeaa795209f99a97d56dd0b1cb6c6bd219552a8940382199e`; report 108,312 / `06932bf93851bdf6033dcef2e896394d34be4d875fa0ea4dd6b0e2bcba8db18a`.
- The current report's missing outputs are authoritative gaps. Never reconstruct, append to, repair, reinterpret, or replace them.
- The new ignored workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery`. It must be absent before Task 1 coordination evidence is created.
- Human-authored ignored scripts, manifests, briefs, and reports are created or edited only with `apply_patch`. Do not use shell redirection, `Set-Content`, `Out-File`, tee, Python file writes, or a generation shortcut.
- Once a human-authored ignored source has been executed or named by a frozen manifest, never edit or replace it. A permitted preformal correction receives a new command ID and a new source path; all earlier bytes remain indexed in the report.
- The frozen recorder alone may create the four paths returned by `Join-Path $MachineRoot ($CommandId + '.stdout.bin')`, `Join-Path $MachineRoot ($CommandId + '.stderr.bin')`, `Join-Path $MachineRoot ($CommandId + '.result.json')`, and `Join-Path $MachineRoot ($CommandId + '.result.sha256')`, with create-new/no-clobber semantics. No other file-write exception exists.
- Every executed nontrivial command has a pre-execution command ID, complete materialized source, source byte count/SHA-256, exact executable identity, argv, working directory, environment allowlist, raw output destinations, and result destination.
- The complete raw stdout and stderr files, not a decoded report excerpt, are authoritative output. Hash bytes before decoding. Never merge, reorder, normalize, truncate, or reconstruct either stream.
- Freeze one Windows boot epoch for each readiness observation. A changed epoch is `HOST_BOOT_EPOCH_CHANGED / NO_GO`.
- Freeze one signed local `docker.exe` identity. Require the exact Docker Inc signer subject in the design, no reparse/link state, and a fresh attempt-specific path, byte count, file/product version, SHA-256, and thumbprint.
- A readiness observation contains exactly three samples and two fixed ten-second waits. A failed sample is not repeated and later samples do not run.
- Each sample requires stable Docker Desktop/backend process identities, both named pipes, exact Linux engine `29.6.1`, a nonempty stable daemon ID/name/root, separately captured streams, and exact canonical fields.
- `DOCKER_DESKTOP_UNAVAILABLE / NOT_READY` or `DOCKER_LINUX_ENGINE_UNREADY / NOT_READY` starts no child. A later evaluation uses a new observation ID and fresh no-clobber evidence; it is not a retry of a child or sample.
- Any comparable drift, malformed evidence, capture gap, manifest mismatch, source mismatch, or unprovable state is the first exact `NO_GO` and stops the plan for review.
- The third successful sample is final readiness revalidation. Launcher revalidation must start within five monotonic seconds of its completion inside the same controller process.
- Entry-child process creation consumes the one new child slot. No child retry, replacement executable, Docker retry, GPU retry, alternate query, fallback, cached observation, or reconstructed command is permitted.
- Child self-attestation precedes every Git, Docker, artifact, image, lease, historical, CPU, and GPU action inside the child.
- Each scheduled WDDM observation starts exactly one `nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63` native process. Only zero rows or exact `G`-only rows pass.
- Do not start, stop, restart, update, reset, or configure Docker Desktop, WSL, Hyper-V, Windows, a service, the GPU, or another process. `NOT_READY` pauses for external owner operation.
- The artifact root `D:\vision-active-learning-loop-artifacts\wave0` is read-only. A mismatch is a stop condition, never a repair instruction.
- The implementation is one append-only commit, the direct child of this plan commit, changing exactly the seven paths in the allowlist. Tasks 1-5 create no commits; Task 6 creates the only implementation commit.
- Author and committer for the plan and implementation commits are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean evidence, push, merge, tag, release, publish, or modify another repository.
- Do not invoke `scripts/run_wave0_a11.ps1`, create a formal A11 runtime identity, acquire a campaign lease, initialize/load a model, access RDD, start Wave 1, or generate/guess/consume an `OwnerAuthorizationId`.
- Consumed owner IDs `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` remain immutable. Test-only values contain `TEST`.
- The only Docker stage execution permitted is the single dependency-only diagnostic in Task 7. Tasks 5-6 may use `docker buildx build --check` only.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93` unchanged.
- CPU product tests set `PYTHONDONTWRITEBYTECODE=1` and use `-p no:cacheprovider`. They do not use network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The dependency diagnostic writes only below `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics` and has no owner ID, run ID, exported image, project container, model process, or statistical meaning.
- Only `ENTRY_GATE_PASS` plus an independent `APPROVED` evidence review permits Task 2.

## Normative Overlay

The complete launcher-identity recovery plan at commit
`9a80b320a18255cb52f6988dc1feadbe78a7cb7d` and Git blob
`59580ef7219af54cce400031a34ac843c76a0625` is incorporated by immutable
reference.

Verify the parent documents before creating recovery evidence:

~~~powershell
$PriorPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery-design.md'
$PriorSpec = '9a80b320a18255cb52f6988dc1feadbe78a7cb7d:' + $PriorPlanPath
$DesignSpec = 'fc7cad720584ebd7f0813d6b8d92988126867046:' + $DesignPath
if ((git rev-parse $PriorSpec).Trim() -cne
    '59580ef7219af54cce400031a34ac843c76a0625') {
    throw 'immutable launcher plan blob mismatch'
}
if ((git rev-parse $DesignSpec).Trim() -cne
    '3c131d93fdbaaf6138730eb20bec8cb882bfc0f6') {
    throw 'approved restart-aware design blob mismatch'
}
~~~

These are the only replacements:

| Contract | Superseded | Effective |
|---|---|---|
| Implementation parent | launcher plan `9a80b320a18255cb52f6988dc1feadbe78a7cb7d` | this plan commit |
| Implementation grandparent | launcher design `3e98d1d56caede9a1baaf215da4e418112a73643` | restart-aware design `fc7cad720584ebd7f0813d6b8d92988126867046` |
| Task 1 | launcher-plan lines 126-732 and consumed evidence | Task 1 below |
| Task 6 | launcher-plan lines 845-942 | Task 6 below |
| Task 7 | launcher-plan lines 943-1060 | Task 7 below |

Launcher-plan Tasks 2-5, lines 733-844, remain byte-for-byte normative and are
reproduced below. Within them, “Task 1” means the successful Task 1 in this plan.
Their RED/GREEN interfaces and seven tracked paths are unchanged.

The new entry source is reconstructed from immutable committed plan blocks, never
from either consumed ignored entry script:

- launcher-plan lines 159-477 define the closed launcher identity helpers;
- launcher-plan lines 483-691 define discovery, entry construction, inherited
  WDDM integration, static gates, revalidation, child execution, and CPU gating;
- WDDM plan `42c200d8a801b142cde394cda7a0520bd9c30a83` lines 112-601 define the preservation, versioned
  inventory, secure XML, Docker/image/lease/history, and one-query gate source.

The new controller wraps those exact child semantics; it does not edit their
admission rules.

## Frozen Preservation Envelope

The five run records remain:

~~~text
attempt 1  v1  48 files / 18 dirs / fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b
attempt 2  v1   5 files /  5 dirs / 8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b
attempt 3  v1  60 files / 18 dirs / 628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2
attempt 4  v1 137 files / 30 dirs / f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717
attempt 5  v2  10 files /  5 dirs / e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
attempt-1 v2 negative / 72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c
historical files 64,306 / e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
historical images 21 / 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
~~~

The exact image IDs, lease hashes, latest-write timestamps, attempt-5 records,
canonical algorithms, diagnostic absence, active-lease absence, and project
container absence remain the values incorporated by the two prior plans.

## Implementation File Map and Allowlist

- Create `configs/a11/preserved-attempts.json`: five immutable versioned run records.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 schema.
- Create `scripts/run_uv_sync_with_retries.py`: bounded dependency-build transport wrapper.
- Modify `scripts/run_wave0_a11.ps1`: WDDM observer, version-aware inventory, registry verifier, and unchanged one-build launcher.
- Modify `docker/wave0.Dockerfile`: named dependency stage and exact cache-backed wrapper calls.
- Modify `tests/gates/test_wave0_a11_launcher.py`: XML, ordering, registry, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change. All readiness and recorder sources are ignored
evidence and never become production dependencies.

---

### Task 1: Prove restart-aware readiness, capture complete evidence, and execute one entry child

**Files:**
- Modify tracked files: none
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-test-first-verify.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-recorder-tests.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-controller-recorder-red.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-controller-recorder-green.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-controller.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-bootstrap-verify.ps1`
- Create ignored source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-entry-gate.ps1`
- Create ignored source only after CUDA PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-cpu-baseline.ps1`
- Create ignored preformal manifests using `Join-Path $Workspace ('task-1-command-manifest-preformal-' + $Ordinal.ToString('000') + '.json')`, where `$Ordinal` is the smallest positive integer not present in the immutable source/result inventory.
- Create one ignored observation manifest using `Join-Path $Workspace ('task-1-command-manifest-' + $ObservationId + '.json')`.
- Create one ignored CPU manifest only after CUDA PASS using `Join-Path $Workspace ('task-1-command-manifest-' + $ObservationId + '-cpu.json')`.
- Create ignored machine evidence only at the four `$CommandId`-derived paths defined in Global Constraints.
- Create ignored report: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-report.md`

For every preformal command, set `$Ordinal` to the smallest positive integer not
present in any source, manifest, machine, or report inventory. Set
`$CommandId = 'preformal-' + $Ordinal.ToString('000') + '-' + $Role`, where
`$Role` is exactly one of `recorder-red-verify`, `recorder-green-test`,
`readiness-red-test`, `readiness-green-test`, or `static-entry-verify`. A corrected
revision retains `$Role` and consumes the next global ordinal. Require
`^preformal-[0-9]{3,}-(recorder-red-verify|recorder-green-test|readiness-red-test|readiness-green-test|static-entry-verify)$`.
Each preformal manifest contains exactly one command record and uses the same
ordinal in its filename.

**Interfaces:**
- Consumes: this plan commit, design `fc7cad720584ebd7f0813d6b8d92988126867046`, launcher plan blob `59580ef7219af54cce400031a34ac843c76a0625`, WDDM plan blob `2abcc051d50921a59f58a57b2814e2a5e47dcc59`, frozen preservation envelope, and external owner-managed Docker state
- Produces before child: `DOCKER_READINESS_PASS`, `DOCKER_DESKTOP_UNAVAILABLE / NOT_READY`, `DOCKER_LINUX_ENGINE_UNREADY / NOT_READY`, or the first exact design-defined `NO_GO` terminal with complete machine evidence
- Produces after child: one `ENTRY_GATE_PASS` or first exact inherited `NO_GO`, plus independent evidence review
- Evidence-only functions: `ConvertTo-A11CanonicalRecord(Value, ExpectedNames)`, `Write-A11CreateNewBytes(Path, Bytes, AllowedRoot)`, `Invoke-A11RecordedProcess(Command, MachineRoot, ProcessFactory)`, `Get-A11HostEpoch(OsReader, ClockReader)`, `Get-A11DockerCliIdentity(CommandResolver, FileIdentityReader)`, `Get-A11DockerReadinessSample(Context, Readers)`, `Invoke-A11DockerReadiness(Context, Readers, Waiter)`

- [ ] **Step 1: Prove entry eligibility before creating the new workspace**

Run only read-only Git and filesystem checks. Require branch
`codex/wave0-model-contract`; HEAD parent `fc7cad720584ebd7f0813d6b8d92988126867046`;
HEAD changes exactly this plan path; exact author/committer identity; linked Git
directory distinct from common directory; no superproject; empty status and
staging; every inherited Git blob; all consumed file byte counts/digests; and the
exact new workspace absent.

Require every intended ignored path to match `.superpowers/sdd/.gitignore` before
creating coordination files. Do not inspect Docker, a named pipe, a process, the
artifact root, or the GPU in this step.

- [ ] **Step 2: Materialize tests and the immutable recorder-RED subject**

Use `apply_patch` to create the complete test file, the one-purpose test-first
verifier, and `task-1-controller-recorder-red.ps1`. Do not create the final
controller or entry source yet. Define these closed field lists in the RED subject
and duplicate them exactly in the recorder tests:

~~~powershell
$script:A11HostEpochNames = @(
    'schema_version','computer_name','windows_product_name','windows_build',
    'boot_time_utc','boot_epoch_sha256','observed_at_utc','monotonic_timestamp'
)
$script:A11DockerCliIdentityNames = @(
    'schema_version','command_resolution_path','canonical_path',
    'file_link_state','parent_chain_link_state','byte_count','sha256',
    'file_version','product_version','authenticode_status','signer_subject',
    'signer_thumbprint','client_version_argv','client_version_exit_code',
    'client_version_stdout_byte_count','client_version_stdout_sha256',
    'client_version_stderr_byte_count','client_version_stderr_sha256',
    'client_version'
)
$script:A11DockerProcessNames = @(
    'pid','start_time_utc','canonical_path','byte_count','sha256','link_type'
)
$script:A11DockerSampleNames = @(
    'schema_version','sample_index','host_boot_epoch_sha256',
    'sample_started_utc','sample_finished_utc','monotonic_start',
    'monotonic_finish','docker_desktop_processes','backend_processes',
    'linux_engine_pipe_present','backend_api_pipe_present','docker_info_argv',
    'docker_info_exit_code','docker_info_stdout_byte_count',
    'docker_info_stdout_sha256','docker_info_stderr_byte_count',
    'docker_info_stderr_sha256','docker_operating_system',
    'docker_server_version','docker_daemon_id','docker_daemon_name',
    'docker_root_dir','terminal'
)
$script:A11ResultNames = @(
    'schema_version','command_id','started_utc','finished_utc','pid',
    'exit_code','start_exception','signal_state','timed_out',
    'same_process_waits','stdout_path',
    'stdout_byte_count','stdout_sha256','stderr_path','stderr_byte_count',
    'stderr_sha256','argv','terminal'
)
$script:A11CommandNames = @(
    'schema_version','command_id','purpose','executable_identity_sha256',
    'executable_path','argv','working_directory','environment_allowlist',
    'stdin_policy','stdout_capture_path','stderr_capture_path','result_path',
    'start_deadline_policy','timeout_policy','permitted_child_count',
    'command_source_paths','command_source_byte_counts','command_source_sha256'
)
$script:A11ReadinessResultNames = @(
    'schema_version','observation_id','host_epoch','docker_cli_identity',
    'samples','wait_durations_ms','sample_three_finished_monotonic',
    'launcher_revalidation_started_monotonic','entry_child_start_count','terminal'
)
~~~

Use exact ordinal property order. Reject missing, duplicate, extra, null, or
wrongly typed fields before canonical serialization.

- [ ] **Step 3: Write RED canonical recorder tests**

In `task-1-recorder-tests.ps1`, inject a fake process factory and create-new
writer. Cover closed/duplicate-key canonical records; empty, ASCII, UTF-8, CRLF,
no-final-newline, NUL, 1 MiB stdout, 1 MiB stderr, simultaneous streams; argv
preservation; exact environment allowlist; closed stdin; exit 0/nonzero; start
exception; fake timeout and signal-like termination; permitted-child-count
exhaustion; output-path collision; manifest mismatch; source-digest mismatch;
linked path; result-digest recomputation; and missing or extra machine artifact.

The central assertion is:

~~~powershell
$Result = Invoke-A11RecordedProcess `
    -Command $Command -MachineRoot $MachineRoot -ProcessFactory $FakeFactory
if ($Result.stdout_byte_count -ne $ExpectedStdout.Length) {
    throw 'stdout byte count mismatch'
}
if ($Result.stdout_sha256 -cne (Get-A11Sha256 -Bytes $ExpectedStdout)) {
    throw 'stdout digest mismatch'
}
if (-not [Linq.Enumerable]::SequenceEqual(
    [byte[]](Get-Content -LiteralPath $Result.stdout_path -AsByteStream -Raw),
    [byte[]]$ExpectedStdout
)) { throw 'stdout bytes changed' }
~~~

Do not execute a process in this step. Freeze the test, RED-subject, and verifier
bytes with `apply_patch`; direct source inspection establishes that the subject
does not define `Invoke-A11RecordedProcess` or `Write-A11CreateNewBytes`. The next
step's first recorded child must run the verifier against these immutable bytes
and produce `RECORDER_TESTS_RED / EXPECTED_MISSING_IMPLEMENTATION`. Do not execute
Docker or either controller subject.

- [ ] **Step 4: Implement the minimal raw-byte recorder**

Use `apply_patch` to create the new immutable
`task-1-controller-recorder-green.ps1`; never edit the RED subject. Implement
`Write-A11CreateNewBytes` with an allowed-root check, ancestor
reparse-point rejection, `FileMode.CreateNew`, `FileAccess.Write`,
`FileShare.None`, flush-to-disk, close, re-open, byte-for-byte verification, and
SHA-256 verification.

Implement process capture with `System.Diagnostics.Process` and raw base streams:

~~~powershell
$Info = [Diagnostics.ProcessStartInfo]::new()
$Info.FileName = $Command.executable_path
$Info.UseShellExecute = $false
$Info.RedirectStandardInput = $true
$Info.RedirectStandardOutput = $true
$Info.RedirectStandardError = $true
$Info.CreateNoWindow = $true
foreach ($Argument in $Command.argv) { [void]$Info.ArgumentList.Add($Argument) }
foreach ($Name in @($Info.Environment.Keys)) {
    if ($Name -notin $Command.environment_allowlist.PSObject.Properties.Name) {
        [void]$Info.Environment.Remove($Name)
    }
}
foreach ($Property in $Command.environment_allowlist.PSObject.Properties) {
    $Info.Environment[$Property.Name] = [string]$Property.Value
}
$Process = [Diagnostics.Process]::new()
$Process.StartInfo = $Info
if (-not $Process.Start()) { throw 'process start returned false' }
$Process.StandardInput.Close()
$StdoutMemory = [IO.MemoryStream]::new()
$StderrMemory = [IO.MemoryStream]::new()
$StdoutTask = $Process.StandardOutput.BaseStream.CopyToAsync($StdoutMemory)
$StderrTask = $Process.StandardError.BaseStream.CopyToAsync($StderrMemory)
$Process.WaitForExit()
[Threading.Tasks.Task]::WhenAll($StdoutTask,$StderrTask).GetAwaiter().GetResult()
$StdoutBytes = $StdoutMemory.ToArray()
$StderrBytes = $StderrMemory.ToArray()
~~~

Real readiness and entry commands use `timeout_policy: none`; the recorder never
kills a real process. Timeout-state unit tests use only an injected fake result
and start no native process. Write raw files first, then one canonical result,
then its digest. Any write/capture gap is `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`.

Both the recorder-GREEN subject and final controller implement the self-capture
contract specified in Step 8. As the GREEN subject's first recorded child, run
the immutable test-first verifier against the RED subject and require
`RECORDER_TESTS_RED / EXPECTED_MISSING_IMPLEMENTATION`. Then run the recorder
tests against the GREEN subject. Expected:
`RECORDER_TESTS_PASS` with zero native Docker, GPU, model, network, or artifact
access. The GREEN subject records the test-child raw streams and result into its
own preformal no-clobber machine paths.

- [ ] **Step 5: Write RED host-epoch and Docker-readiness tests**

Use injected OS, process, pipe, Docker-result, monotonic-clock, and waiter readers.
Cover exact three-sample pass plus:

~~~powershell
$Cases = @(
    'boot_epoch_changes',
    'boot_epoch_digest_mismatch',
    'docker_command_resolution_missing_or_multiple',
    'docker_command_and_canonical_path_disagree',
    'docker_path_or_parent_linked',
    'docker_signature_invalid_or_signer_wrong',
    'docker_client_version_nonzero_or_wrong',
    'desktop_process_absent',
    'backend_process_absent',
    'process_pid_reused_with_new_start',
    'process_path_or_digest_drifts',
    'linux_pipe_absent',
    'backend_pipe_absent',
    'docker_info_nonzero',
    'docker_info_malformed',
    'docker_ostype_windows',
    'docker_version_wrong',
    'daemon_id_empty',
    'daemon_identity_drifts',
    'sample_two_fails_stops_sample_three',
    'wait_count_not_two',
    'handoff_exceeds_five_seconds'
)
~~~

Assert absent process/pipe produces `NOT_READY` and zero child starts. Comparable
drift or malformed evidence produces `NO_GO` and zero child starts. Assert three
passes invoke exactly three Docker payloads and two ten-second injected waits.

Run the readiness cases against the immutable recorder-GREEN subject, through
its proven recorder. Expected RED:
`DOCKER_READINESS_TESTS_RED / EXPECTED_MISSING_IMPLEMENTATION`; retain its exact
raw streams and result under a new preformal command ID.

- [ ] **Step 6: Implement host epoch, Docker identity, and three-sample readiness**

Use `apply_patch` to create the final immutable `task-1-controller.ps1` from the
proven recorder-GREEN source plus only the readiness implementation. Never edit
either earlier subject. Canonicalize boot time to seven fractional UTC digits.
Resolve Docker through
`Get-Command docker.exe -CommandType Application`, freeze the exact signed file
identity, and require the design's exact signer subject. Execute the frozen
absolute CLI once with exact argv `--version`, capture both streams through the
recorder, parse the client version as exactly `29.6.1`, and include that command
record in the observation manifest.

Use exact process image names `Docker Desktop.exe` and `com.docker.backend.exe`.
Test exact named-pipe paths `\\.\pipe\dockerDesktopLinuxEngine` and
`\\.\pipe\dockerBackendApiServer`; never enumerate a broader pipe namespace.

Use one exact Docker argv per sample:

~~~text
info --format {{json .}}
~~~

Decode the complete captured JSON and select only `OSType`, `ServerVersion`,
`ID`, `Name`, and `DockerRootDir` into the closed sample. Require `linux`,
`29.6.1`, and nonempty stable identity fields.

Implement the fixed loop:

~~~powershell
for ($SampleIndex = 1; $SampleIndex -le 3; $SampleIndex++) {
    $Sample = Get-A11DockerReadinessSample `
        -Context $Context -Readers $Readers -SampleIndex $SampleIndex
    $Samples += $Sample
    if ($Sample.terminal -like '* / NOT_READY' -or
        $Sample.terminal -like '* / NO_GO') {
        return New-A11ReadinessResult -Samples $Samples -Terminal $Sample.terminal
    }
    if ($SampleIndex -lt 3) {
        & $Waiter 10000
        $WaitCount++
    }
}
if ($WaitCount -ne 2) { throw 'readiness wait count mismatch' }
return New-A11ReadinessResult -Samples $Samples -Terminal 'DOCKER_READINESS_PASS'
~~~

The real waiter is fixed at 10,000 ms and cannot inspect state or alter duration.
Run all synthetic tests against the final controller in test mode, through its
recorder. Expected: `DOCKER_READINESS_TESTS_PASS` with complete no-clobber raw
evidence.

- [ ] **Step 7: Reconstruct and statically verify the complete entry source**

Use `apply_patch` to create the final bootstrap verifier and entry source.
Reconstruct launcher identity and WDDM code only from the immutable Git blobs and
line ranges in Normative Overlay. Insert fresh expected launcher identity,
self-attestation, and recorder integration. Do not read either consumed ignored
entry script.

Materialize `task-1-bootstrap-verify.ps1` before execution. It must:

- parse every complete source under PowerShell 7.6.4 and Windows PowerShell 5.1;
- compare duplicated identity blocks byte-for-byte;
- require child self-attestation before all sensitive tokens;
- require exactly one `nvidia-smi` token and exact argv;
- require exactly three Docker samples, two 10,000 ms waits, and one possible
  entry-child start;
- forbid retry loops around Docker, child, or GPU commands;
- forbid service/process mutation and arbitrary file-write APIs;
- require every machine output path to match the manifest; and
- prove command/source hashes before controller execution.

Run the bootstrap once. Expected: `TASK1_STATIC_VERIFICATION_PASS`. Any failure
retains that materialized source and exact output; correct source is assigned a
new command ID before another authoring verification. Docker eligibility has not
started, so no child slot is consumed.

- [ ] **Step 8: Materialize one fresh readiness observation manifest**

Set `$ObservationOrdinal` to the smallest positive integer for which neither a
manifest, machine path, report record, nor consumed observation exists, then set
`$ObservationId = 'docker-readiness-' + $ObservationOrdinal.ToString('000')`.
This derivation is deterministic and the resulting ID must match
`^docker-readiness-[0-9]{3,}$`. The manifest contains the closed fields from the
design and exact command/source digests. Its command IDs are the observation ID
plus these exact role suffixes: `-controller`, `-docker-client-version`,
`-docker-info-01`, `-docker-info-02`, `-docker-info-03`,
`-launcher-revalidate`, and `-entry-child`. Controller control flow, not an extra
manifest property, admits the last two commands only after
`DOCKER_READINESS_PASS`; they remain unexecuted on `NOT_READY` or `NO_GO`. Use
`apply_patch` to create the manifest; do not let the controller synthesize or
rewrite it.

The controller's outer payload is exactly the frozen signed PowerShell path plus:

~~~text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\task-1-controller.ps1
-ManifestPath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\task-1-command-manifest-docker-readiness-001.json
~~~

The displayed manifest path is exact when ordinal 001 is the smallest eligible
ordinal; otherwise replace only its zero-padded ordinal with the value derived by
the preceding rule. Record the resulting literal payload, argv, source
bytes/digest, manifest bytes/digest, expected machine paths, and allowed
environment before execution.

The `-controller` record is self-captured: every controller stdout/stderr byte is
first appended to a dedicated in-memory byte buffer, all terminating exceptions
are caught into the closed terminal, and finalization writes the controller's own
four create-new machine files before replaying those bytes to inherited console
streams. No console API bypass is permitted. Missing self-capture after an
abrupt host/process loss is `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, never a basis
for reconstruction.

- [ ] **Step 9: Execute readiness and obey NOT_READY without consuming the child**

Execute the controller once for that observation. It freezes the boot epoch and
Docker CLI identity, then runs the three samples.

If it returns `DOCKER_DESKTOP_UNAVAILABLE / NOT_READY` or
`DOCKER_LINUX_ENGINE_UNREADY / NOT_READY`:

- require zero entry-child process starts and zero GPU/CPU evidence;
- preserve the complete observation and report `OWNER_DOCKER_START_REQUIRED`;
- do not start or configure Docker;
- pause until the owner externally starts Docker Desktop with Linux engine; and
- on resumption, create a new observation ID, manifest, and no-clobber machine
  paths, then repeat only Steps 8-9.

A failed sample is never repeated within an observation. Any `NO_GO` stops the
plan for review. Only `DOCKER_READINESS_PASS` continues inside the same controller
invocation.

- [ ] **Step 10: Perform the <=5-second handoff and start the entry child once**

After sample 3 PASS, require the same boot epoch and start launcher revalidation
within five monotonic seconds. Revalidate the frozen PowerShell identity once,
then start the frozen entry child once through the recorder.

Require the child first structured stdout record to contain exact expected,
observed, and comparison identities before accepting later evidence. Preserve
complete raw streams and result JSON even on nonzero exit. No outer retry or
replacement payload exists.

The child then executes the inherited preservation, Docker/image/lease/history,
single WDDM XML, and closed CUDA gates. A Docker loss after process creation or
any inherited failure consumes the child slot and produces the first exact
`NO_GO`.

- [ ] **Step 11: Run the CPU baseline only after CUDA PASS**

Only after one retained `CUDA_IDLE / PASS` record may `apply_patch` create the
CPU baseline and the separate immutable CPU manifest. That manifest contains
exactly `$ObservationId + '-cpu-launcher-revalidate'` and
`$ObservationId + '-cpu-child'`, with complete source bytes/digests and
no-clobber machine destinations. Revalidate the same launcher identity,
self-attest in the CPU child, set `PYTHONDONTWRITEBYTECODE=1`, and run the exact
offline/cache-disabled baseline inherited from launcher-plan Task 1.

Any CPU failure is the final `NO_GO`. A complete pass produces
`ENTRY_GATE_PASS`.

- [ ] **Step 12: Publish the report and obtain independent approval**

Use `apply_patch` to create `task-1-report.md` after all authoritative machine
files close. Index every command/source/manifest/raw/result path, byte count,
SHA-256, argv, timestamps, process identity, exit, session/chunk metadata,
readiness sample, child first record, CUDA result, CPU result, and final terminal.

Run a read-only verifier that recomputes all hashes and rejects missing, extra,
linked, duplicate, or colliding evidence. Give an independent reviewer the spec,
plan, brief, report, manifests, machine inventory, source inventory, and final Git
state. The reviewer reruns no external command.

Only `ENTRY_GATE_PASS` plus review `APPROVED` permits Task 2. Any finding about a
missing payload/result is unrepairable and stops; never reconstruct it.

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
- Modify/create: exactly the seven implementation paths in the allowlist
- Read: complete Task 1 machine evidence, report, independent approval, and Tasks 2-5 uncommitted diff
- Create ignored verification source: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-6-verification.ps1`
- Create ignored review package: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-6-review-package.md`

**Interfaces:**
- Consumes: `ENTRY_GATE_PASS`, Task 1 `APPROVED` review, complete raw captures, and uncommitted Tasks 2-5
- Produces: exactly one reviewed implementation commit, direct child of this plan commit

- [ ] **Step 1: Prove Task 1 evidence completeness before product verification**

Materialize `task-6-verification.ps1` with `apply_patch`. Recompute every command
manifest, source, stdout, stderr, result, and result-digest hash. Require exact
three-sample readiness PASS, two waits, one child start, launcher identity PASS,
one CUDA observation, CUDA_IDLE / PASS, CPU PASS, ENTRY_GATE_PASS, reviewer
APPROVED, and no missing/extra machine path.

Require all consumed evidence hashes unchanged. Any mismatch stops before tests
or commit.

- [ ] **Step 2: Run focused product tests**

Run with bytecode and pytest cache disabled:

~~~powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --frozen --offline pytest `
    tests/gates/test_wave0_a11_launcher.py `
    tests/scripts/test_run_uv_sync_with_retries.py `
    -p no:cacheprovider -q
~~~

Expected: all selected tests PASS, no network/Docker/GPU/model/artifact access,
and no cache residue.

- [ ] **Step 3: Run complete CPU validation**

Run the repository's approved full CPU test, schema, style, parser, and lockfile
commands inherited from launcher-plan Task 6. Preserve every exact command and
result. Require `uv.lock` SHA-256
`530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.

Run PowerShell 7 and Windows PowerShell 5.1 parsers against the complete modified
launcher. Run JSON Schema validation for the preserved-attempt registry.

- [ ] **Step 4: Run Docker static validation only**

Require the already ready Linux engine and exact Docker identity, then run only:

~~~powershell
docker buildx build --check --file docker/wave0.Dockerfile .
~~~

Do not execute/export a stage, use `--load`/`--push`, build an image, or invoke
the A11 launcher. Any nonzero result stops.

- [ ] **Step 5: Prove exact scope and preservation**

Require `git diff --name-only` to equal the exact sorted seven-path allowlist,
staging empty, no other untracked path, canonical worktree clean, no project
container, no active lease, no validation run, no dependency diagnostic identity,
and all historical baselines unchanged.

Require no `__pycache__`, `.pyc`, or `.pytest_cache` residue outside excluded
environments and ignored SDD evidence.

- [ ] **Step 6: Obtain independent code and evidence review**

Create `task-6-review-package.md` with `apply_patch`. Include BASE, complete diff,
test results, Docker check, Task 1 evidence inventory, allowlist, lockfile hash,
and preservation results.

Request independent review for spec compliance, correctness, tests, security,
evidence completeness, and scope. The reviewer must not rerun Docker/GPU/model
commands. Resolve code findings by TDD without adding paths. Missing Task 1
evidence cannot be repaired and stops the plan.

- [ ] **Step 7: Stage exactly seven files and commit once**

After every gate and review passes:

~~~powershell
$Allowed = @(
    'configs/a11/preserved-attempts.json',
    'docker/wave0.Dockerfile',
    'schemas/a11-preserved-attempts.schema.json',
    'scripts/run_uv_sync_with_retries.py',
    'scripts/run_wave0_a11.ps1',
    'tests/gates/test_wave0_a11_launcher.py',
    'tests/scripts/test_run_uv_sync_with_retries.py'
) | Sort-Object
$Changed = @(git diff --name-only | Sort-Object)
if (($Changed | ConvertTo-Json -Compress) -cne
    ($Allowed | ConvertTo-Json -Compress)) {
    throw 'implementation allowlist mismatch'
}
git add -- $Allowed
~~~

Require staged paths equal the allowlist and `git diff --cached --check` empty.
Commit once with:

~~~text
fix: recover A11 Docker readiness evidence
~~~

Set author and committer exactly to
`kuotunyu <61350295+kuotunyu@users.noreply.github.com>`. Do not amend.

- [ ] **Step 8: Verify the implementation commit**

Require:

- implementation parent equals this plan commit;
- changed paths equal exactly the seven-path allowlist;
- author and committer identities exact;
- worktree/staging clean;
- every Task 1 and consumed evidence hash unchanged; and
- no formal runtime, model, Wave 1, push, merge, tag, or release occurred.

---

### Task 7: Execute and preserve exactly one dependency-only diagnostic

**Files:**
- Modify tracked files: none
- Create external evidence only beneath the exact directory returned by `Join-Path 'D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics' $DiagnosticId`.
- Create ignored command/report files beneath the new SDD workspace using `apply_patch`

**Interfaces:**
- Consumes: verified implementation commit, Task 1 frozen PowerShell/Docker identities, exact dependency stage, empty diagnostic destination, idle CUDA admission, and no active lease/project container
- Produces: exactly one dependency-only diagnostic terminal and immutable external evidence; never a formal runtime identity

- [ ] **Step 1: Prove diagnostic eligibility**

Require implementation commit identity/parent/allowlist, clean linked and canonical
worktrees, Linux engine 29.6.1, exact frozen Docker CLI identity, no active lease,
no project container, no model process, no existing diagnostic ID, and one fresh
zero-process or G-only CUDA observation.

The CUDA observation uses the inherited exact one-query contract. Any failure
stops before Docker.

- [ ] **Step 2: Materialize the exact diagnostic command**

Set `$DiagnosticOrdinal` to the smallest positive integer absent from the
external root and every immutable diagnostic inventory, then set
`$DiagnosticId = 'dependency-' + $ImplementationCommit.Substring(0,12).ToLowerInvariant() + '-' + $DiagnosticOrdinal.ToString('000')`.
Require `^dependency-[0-9a-f]{12}-[0-9]{3,}$` and create that fresh external
directory atomically. Use `apply_patch` to materialize a self-attested PowerShell
command that records source commit, Docker/Buildx versions, Dockerfile/wrapper/
lockfile hashes, start/end timestamps, argv, output, exit, image-store baseline,
container baseline, and CUDA evidence.

The sole Docker stage command is:

~~~text
docker buildx build
--progress=plain
--no-cache
--target=a11-dependencies
--output=type=cacheonly
--file
docker/wave0.Dockerfile
.
~~~

Freeze exact argv. Do not add `--load`, `--push`, image tags, project labels,
runtime mounts, owner ID, run ID, model stage, or a second build.

- [ ] **Step 3: Execute the diagnostic exactly once**

Revalidate PowerShell and Docker identities, self-attest, then invoke the frozen
command once. If it yields a session, poll only that same session until completion.
Do not retry the Docker build or replace its args.

Preserve stdout/stderr, exit code, BuildKit metadata, wrapper attempt markers,
source hashes, start/end times, and complete tool metadata. A dependency failure
is `DEPENDENCY_DIAGNOSTIC_NO_GO` and stops without implementation changes.

- [ ] **Step 4: Verify no formal side effect**

Require:

- no exported/tagged image;
- no project container;
- no active or released formal lease;
- no A11 calibration/validation run;
- no owner or runtime ID;
- no model process or checkpoint;
- no change to historical artifact/image baselines;
- no Git change; and
- exactly one fresh diagnostic identity.

Publish either `DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_FORBIDDEN` or the
first exact diagnostic `NO_GO`. Do not run a formal A11 attempt or Wave 1.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Append-only lineage and immutable failures | Global Constraints; Task 1 Step 1; Task 6 Steps 1,5,8 |
| Host boot epoch | Task 1 Steps 5-6,9-10 |
| Signed Docker CLI identity | Task 1 Steps 6,9; Task 6 Step 4; Task 7 Step 1 |
| Three samples, two waits, five-second handoff | Task 1 Steps 5-6,9-10 |
| NOT_READY without child consumption | Task 1 Step 9 |
| Manifest-driven raw recorder | Task 1 Steps 2-4,8 |
| Create-new machine write exception | Task 1 Steps 3-4 |
| Exact launcher/child/WDDM inheritance | Task 1 Steps 7,10-11 |
| No post-execution reconstruction | Global Constraints; Task 1 Step 12; Task 6 Steps 1,6 |
| TDD and seven-file allowlist | Tasks 2-6 |
| One implementation commit | Task 6 Steps 7-8 |
| One dependency-only diagnostic | Task 7 |
| No OwnerAuthorizationId/formal runtime/Wave 1 | Global Constraints; Task 7 Step 4 |

## Plan Completion Gate

Before execution, require:

1. this plan exists as one file in a direct-child commit of `fc7cad720584ebd7f0813d6b8d92988126867046`;
2. author/committer identity and plan-only changed path are exact;
3. every PowerShell code block parses under PowerShell 7.6.4 and Windows
   PowerShell 5.1 where compatible;
4. placeholder scan, type/signature consistency, spec coverage, allowlist, and
   inherited-line-range checks pass;
5. worktree and staging are clean; and
6. no Docker/GPU/model/runtime command has been executed by plan authoring.
