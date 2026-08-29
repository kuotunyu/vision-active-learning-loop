# Wave 0 A11 PowerShell Launcher Identity Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `42c200d8a801b142cde394cda7a0520bd9c30a83`

## Purpose

Recover the Wave 0 A11 WDDM type-aware entry gate from one invalid host-launcher
assumption without changing the GPU admission algorithm, preserved artifacts,
implementation scope, or formal-runtime boundary.

The approved WDDM recovery plan froze this exact Task 1 payload:

```powershell
& 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -NonInteractive -File '<entry-script>'
```

That executable does not exist on this host. The exact payload was executed once
and failed before the entry script started. No `nvidia-smi` process, Docker
operation, CPU baseline, implementation edit, or later task occurred. The
preserved terminal is:

```text
CUDA_OBSERVATION_UNPROVABLE / NO_GO
```

The failure is a plan-to-host launcher-path contract defect. It is not evidence
about GPU admission, artifacts, Docker, or implementation correctness. The
failed payload is consumed and must never be retried, repaired in place, or
reclassified.

This recovery introduces an evidence-only PowerShell identity gate. It discovers
the already-running controller's real executable, proves that identity using two
independent resolution paths plus file and signature evidence, freezes that
identity into a new entry command, and requires the child process to attest the
same identity before any project or GPU observation.

## Immutable evidence and lineage

The following remain immutable:

- WDDM recovery plan commit
  `42c200d8a801b142cde394cda7a0520bd9c30a83` and plan blob
  `2abcc051d50921a59f58a57b2814e2a5e47dcc59`.
- WDDM recovery design commit
  `0053a8b30c8639ea9b9752ca2171117692fe78b0` and design blob
  `124b87aa9b2a04b3830aa85e5c45a4cfde87b260`.
- CUDA-observability plan and design
  `f45d84eec13b98ee4566497252375f20251fd2d3` and
  `5451c50cc20b1c297c9bdd3535a793eff993158d`.
- Ordering-recovery plan and design
  `52fe25d529f7d64e986864576653d0d14a6e484b` and
  `68f51519d2cb480200ca4fef740651b0d15dd76f`.
- Digest-recovery plan and design
  `03115325f36da31b135b4593fb8df1689eac9a35` and
  `2db13d302da97a241daeaba3578cd9cec1c8073b`.
- Diagnostic-root erratum, runtime-transport plan, and runtime-transport design
  `101bb79369399cc3947f1c667f0a11988f916638`,
  `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, and
  `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`.
- All five consumed A11 attempts, authorization identities, images, leases,
  artifacts, historical digests, and diagnostic records.
- The earlier PID-only GPU observation and its preserved
  `CUDA_COMPUTE_BUSY / NO_GO` terminal.
- The plan-authoring observation incident retained as
  `CUDA_OBSERVATION_UNPROVABLE / NO_GO`.
- The failed launcher entry script, 42,541 bytes with SHA-256
  `1dafe50f2073eed8955a01fe8ed59bcc2f1554f4ea0504a4575b0071a627fe65`.
- The failed launcher report, 45,245 bytes with SHA-256
  `11ca424b816ec013261b7227a2e18e3e4fb658b58b7c90a10b943e55ed439e11`.

The failed entry script and report remain in the ignored workspace:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-wddm-type-aware-cuda-gate-recovery/
```

They are historical evidence, not inputs to the new attempt. The new recovery
must use a distinct ignored workspace and newly materialized command files.

The commit containing this document must be the direct child of
`42c200d8a801b142cde394cda7a0520bd9c30a83` and add only this file. Its
implementation plan must be a one-file direct child. A permitted implementation
commit must be the plan's direct child and retain the exact seven-path allowlist.

Author and committer for both documentation commits and the eventual
implementation commit must be exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

## Decision

Use a dynamically discovered, fully attested absolute PowerShell executable for
the new Task 1 payload.

The committed design and plan do not pin a user-specific installation path.
Instead, the ignored Task 1 evidence freezes the exact executable identity found
at execution time. Discovery is admissible only when the current process path and
the default application resolution for `pwsh` identify the same canonical file.

The discovery gate records and validates:

- current process executable path;
- default `Get-Command pwsh -CommandType Application` source;
- canonical resolved absolute path;
- file existence, leaf type, byte count, and reparse/link state;
- every parent directory's reparse/link state through the volume root;
- `$PSVersionTable.PSVersion`;
- executable file and product versions;
- executable SHA-256;
- Authenticode status;
- signer certificate subject and thumbprint.

Admission requires PowerShell `7.6.4`, a file version in the `7.6.4.*` family,
an ordinary local `pwsh.exe` file, no reparse point in the executable or parent
chain, a `Valid` Authenticode signature, and a Microsoft Corporation signer.
The observed path, byte count, exact file version, product version, SHA-256, and
signer thumbprint are then frozen for this attempt.

The host snapshot used to validate this architecture was:

```text
path: C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe
PowerShell: 7.6.4
file version: 7.6.4.500
bytes: 301368
SHA-256: db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f
signature: Valid
signer thumbprint: AB172913A2960A224809EE8A0C371CD47A079B72
signer: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
```

These values prove that the design is executable on the current host; they are
not silently reused as fresh Task 1 evidence. Task 1 must observe and retain a
fresh identity. A host-runtime change is accepted only if it still satisfies the
closed admission rules and is frozen before the entry payload. No alternate
candidate is tried after a failed discovery or launch.

## Alternatives considered

### 1. Dynamic identity-attested absolute path — selected

This retains the audit strength of an exact absolute executable while avoiding a
machine-layout assumption. Independent controller resolution, signed-file
evidence, pre-launch revalidation, and child self-attestation make path or binary
drift fail closed before GPU access.

### 2. Resolve `pwsh` through `PATH` at launch — rejected

This is short and portable, but PATH order, application aliases, shims, or a
controller-environment change can select different bytes after evidence is
recorded. A command name alone is not an executable identity.

### 3. Invoke the entry script inside the controller process — rejected

This avoids a child executable path but changes the existing process-isolation,
exit-code, stdout/stderr, and retained-tool-result contract. It would widen the
recovery beyond the single invalid assumption.

### 4. Install or copy PowerShell into the old system path — rejected

Installing software, copying a signed executable, changing PATH, or manufacturing
the missing directory mutates the host to satisfy a bad plan assumption. Host
repair is outside this repository recovery and would obscure the actual defect.

## Components

### Controller identity discovery

The new ignored workspace is:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/
```

The plan materializes `task-1-launcher-identity.ps1` there and records its exact
source, UTF-8 byte count, SHA-256, and short literal current-shell payload before
execution. The helper performs only local process, command-resolution, file,
hash, version, reparse, and Authenticode inspection. It contains no `nvidia-smi`,
Docker, Git mutation, artifact-root access, network access, process mutation,
sleep, retry, or fallback candidate.

The helper emits one compact JSON record. It must distinguish:

- evidence that is present and comparable but does not match the closed policy;
- evidence that cannot be obtained or cannot be observed by the controller.

The discovery call is not a GPU admission attempt. A discovery failure closes the
new Task 1 before the entry payload exists.

### Pure identity comparison

A pure comparator consumes an expected identity and an observed identity. It does
not inspect the host or start a process. The closed comparison fields are:

```text
canonical_path
byte_count
sha256
powershell_version
file_version
product_version
signature_status
signer_subject
signer_thumbprint
file_link_type
parent_chain_link_types
```

All string comparisons are exact after the discovery helper has produced one
canonical Windows path spelling. SHA-256 is lowercase hexadecimal. Byte count is
a positive integer. Missing, duplicate, differently typed, or additional
identity fields are rejected rather than ignored.

Synthetic mutations prove that every field is load-bearing. The comparator has
no tolerance window, version upgrade rule, alternate signer, path search, or
second candidate.

### Frozen entry command

Only after discovery passes may the controller create
`task-1-entry-gate.ps1`. The script incorporates the complete prior WDDM Task 1
entry source plus the frozen launcher identity record and self-attestation block.
It is newly materialized and must not reuse the failed script file.

The controller records before execution:

- discovery command source, bytes, digest, literal payload, and result;
- frozen launcher identity JSON and its canonical UTF-8 digest;
- complete entry script source, bytes, and digest;
- exact absolute `pwsh.exe` literal payload;
- exact argv and the expected child identity.

After the entry script is frozen, a separate read-only revalidation helper
observes the same launcher fields. It may compare only against the frozen
identity. A mismatch stops before the entry payload. Revalidation cannot search
for, select, or recommend a replacement executable.

The exact entry payload is executed at most once. If the tool yields a session,
only that same session may be resumed until completion. No replacement payload,
second executable, shell fallback, or reconstructed command is permitted.

### Child self-attestation

The entry script's first action is to observe its own process executable and the
same closed identity fields. Before Git, Docker, artifact, image, lease,
historical, CPU, or GPU work, it emits:

```text
launcher_identity_expected
launcher_identity_observed
launcher_identity_comparison
```

The child continues only when the pure comparison passes. The child cannot
rewrite expected values, discover another executable, or relaunch itself.

This self-attestation closes the material race between controller revalidation
and process start. It does not claim that the executable can never change later;
it proves the exact bytes and signed identity of the running gate before any
project-sensitive observation.

### Inherited WDDM entry gate

After launcher identity passes, the new script executes the complete preservation
and WDDM type-aware Task 1 contract from plan commit
`42c200d8a801b142cde394cda7a0520bd9c30a83`, except for the replaced launcher
freeze and the added child preamble.

The XML observer still starts exactly one native command:

```text
nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63
```

There is no query retry, replacement format, PID-only fallback, memory-value
fallback, name allowlist, process mutation, service control, GPU reset, Docker
stop, WSL shutdown, or timeout replacement. Only zero process rows or exclusively
`G` rows may produce `CUDA_IDLE / PASS`.

The failed prior payload did not start the entry script or `nvidia-smi`; the new
observation is a newly designed scheduled gate, not a retry of the failed literal
payload. It receives its own evidence workspace, identity proof, command digest,
tool result, observation ID, and terminal.

## Data flow

The new Task 1 sequence is strictly ordered:

1. Prove linked-worktree topology, branch, exact recovery lineage, identity, clean
   scope, and empty staging without modifying tracked or historical evidence.
2. Materialize and freeze the controller identity-discovery helper.
3. Execute the discovery helper once in the current controller shell and retain
   the exact nested tool result.
4. Stop if discovery is unprovable or violates the closed launcher policy.
5. Freeze the accepted identity as canonical compact JSON with UTF-8 byte count
   and SHA-256.
6. Materialize the new complete entry script with the expected identity and child
   self-attestation preamble.
7. Parse and statically inspect the complete helpers under PowerShell 7 and the
   Windows PowerShell 5.1 parser without executing project or GPU code.
8. Freeze the exact absolute child payload and complete command evidence.
9. Revalidate the executable once against the frozen identity; stop on mismatch.
10. Execute the frozen entry payload once.
11. Require the child identity record before accepting any later entry evidence.
12. Continue through the inherited preservation and single WDDM XML observation.
13. Run the inherited complete CPU baseline only after `CUDA_IDLE / PASS`.
14. Publish exactly one final Task 1 terminal and require repository preservation.

Only `ENTRY_GATE_PASS` permits Task 2 of the subsequent implementation plan.

## Closed outcomes

Launcher outcomes added by this design are:

```text
POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO
POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO
POWERSHELL_LAUNCHER_IDENTITY_PASS
```

`POWERSHELL_LAUNCHER_IDENTITY_MISMATCH` applies when complete comparable evidence
violates policy or differs from the frozen identity. Examples include path,
digest, size, version, signature, signer, thumbprint, or link-state drift.

`POWERSHELL_LAUNCHER_UNPROVABLE` applies when discovery cannot produce its closed
record, the exact executable cannot be started, the child identity record is
missing, tool completion is not observable, or evidence is malformed.

`POWERSHELL_LAUNCHER_IDENTITY_PASS` is an intermediate record, not permission for
formal A11 runtime. It permits only the inherited Task 1 checks.

After launcher pass, the unchanged closed WDDM outcomes remain:

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

The final Task 1 report contains exactly one terminal: `ENTRY_GATE_PASS` or the
first exact `NO_GO`. Every `NO_GO` preserves its evidence and stops the sequence.

## Testing and verification

Before the identity helper may inspect the real host, synthetic checks must prove:

- identical expected and observed records pass;
- mutations to every comparison field produce identity mismatch;
- missing, duplicate, additional, or wrongly typed fields are unprovable;
- a process path and `Get-Command` source disagreement is rejected;
- a missing file, non-file leaf, reparse point, parent-chain link, unsupported
  PowerShell version, invalid signature, non-Microsoft signer, or absent signer
  certificate is rejected;
- lowercase SHA-256 and exact canonical serialization are stable;
- the injected identity-observer call count is exactly one;
- the identity and revalidation helpers contain no retry, sleep, process
  mutation, GPU, Docker, network, artifact, or implementation command;
- the child self-attestation appears before every Git, Docker, artifact, lease,
  historical, CPU, and `nvidia-smi` action;
- the complete helper sources parse under PowerShell 7.6.4 and Windows
  PowerShell 5.1;
- the entry observer still contains exactly one permitted `nvidia-smi` native
  start and no fallback query.

The subsequent implementation remains RED/GREEN/refactor as specified by the
WDDM recovery plan. No live GPU, Docker, network, model, or external artifact root
is used as a unit test.

Required preservation checks after any terminal include:

- linked and canonical worktrees clean;
- staging empty;
- no tracked path outside the current phase's allowlist changed;
- no `__pycache__`, `.pyc`, or `.pytest_cache` residue outside excluded ignored
  environments and the new SDD workspace;
- no repository runtime artifact or dependency-diagnostic directory;
- previous evidence files and digests unchanged.

## Normative overlay and implementation scope

The subsequent implementation plan is a narrow overlay on WDDM plan commit
`42c200d8a801b142cde394cda7a0520bd9c30a83`.

It replaces:

- the implementation parent with the new plan commit;
- the consumed Task 1 attempt with a newly scheduled Task 1;
- the hard-coded launcher freeze with dynamic discovery, revalidation, and child
  self-attestation;
- the Task 1 report schema with the additional launcher identity evidence and
  outcomes.

It inherits unchanged:

- the secure WDDM XML decoder and exact process-type classifier;
- the one-native-query admission boundary;
- all preservation, artifact, image, lease, historical, Docker, lockfile,
  schema, style, parser, review, and commit gates;
- Tasks 2 through 7 after the new Task 1 passes;
- the prohibition on a formal runtime attempt and Wave 1.

The eventual implementation commit retains exactly these seven tracked paths:

1. `configs/a11/preserved-attempts.json`
2. `schemas/a11-preserved-attempts.schema.json`
3. `scripts/run_uv_sync_with_retries.py`
4. `scripts/run_wave0_a11.ps1`
5. `docker/wave0.Dockerfile`
6. `tests/gates/test_wave0_a11_launcher.py`
7. `tests/scripts/test_run_uv_sync_with_retries.py`

Launcher identity discovery and command evidence remain ignored execution
artifacts. This recovery introduces no tracked helper executable, dependency,
configuration path, schema path, or parallel launcher.

## Runtime and authorization boundary

This design, its plan, Task 1 identity discovery, local implementation, CPU
verification, static Docker checks, review, and the already bounded
dependency-only diagnostic require no `OwnerAuthorizationId` and do not accept
one.

They may not invoke `scripts/run_wave0_a11.ps1`, initialize a model, acquire a
formal campaign lease, create calibration or validation runtime identities,
access RDD, or start Wave 1. A later formal A11 attempt requires a fresh explicit
authorization bound to its exact source, original A11 specification, original
A11 plan, and branch. Consumed owner IDs remain immutable evidence.

## Out of scope

- Reusing, retrying, editing, or reclassifying the failed launcher payload.
- Installing, copying, repairing, updating, or relocating PowerShell.
- Changing PATH, application aliases, execution policy, shell registration, or
  the Codex runtime installation.
- Accepting `powershell.exe`, a shell alias, shim, script wrapper, relative path,
  UNC path, unsigned binary, alternate signer, or alternate version.
- Searching multiple executables after the default controller identity fails.
- Retrying a launcher discovery, child start, GPU query, or failed frozen gate.
- Modifying or deleting an existing artifact, image, lease, run, diagnostic, or
  historical evidence record.
- Terminating, pausing, signalling, reprioritizing, or otherwise mutating any
  process or service.
- Model, dependency, split, threshold, receipt, replica, acquisition,
  statistical, data-firewall, or Wave 1 contract drift.
- Formal A11 runtime, GPU model campaign, push, merge, rebase, release, tag, or
  changes to another repository.

## Success criteria

This recovery is complete only when:

1. This design and its implementation plan are exact one-file commits with the
   required lineage and commit identity.
2. A fresh controller identity record satisfies the closed policy and is retained
   before entry-script creation.
3. Revalidation and child self-attestation match the frozen identity exactly.
4. The new complete Task 1 produces `ENTRY_GATE_PASS`, including one retained
   type-aware `CUDA_IDLE / PASS` observation and the inherited CPU baseline.
5. Tasks 2 through 5 complete by TDD within the seven-path allowlist.
6. The complete candidate verification, preservation gate, review, scope,
   lineage, identity, and single-commit checks pass.
7. The one dependency-only diagnostic closes with its inherited formal-runtime-
   forbidden terminal.

Any failed frozen gate is preserved as its exact `NO_GO` and stops the sequence
for redesign. It never authorizes tuning, host mutation, fallback selection, or a
silent retry.
