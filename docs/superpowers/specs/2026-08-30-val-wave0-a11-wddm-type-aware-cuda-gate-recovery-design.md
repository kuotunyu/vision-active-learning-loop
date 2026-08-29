# Wave 0 A11 WDDM Type-Aware CUDA-Gate Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `f45d84eec13b98ee4566497252375f20251fd2d3`

## Purpose

Recover the Wave 0 A11 entry and launcher GPU gates from two unsafe Windows
WDDM assumptions while preserving every existing artifact, runtime attempt,
authorization, statistical boundary, and recovery commit.

The first unsafe assumption is the PID-only observation introduced by the
CUDA-observability recovery plan. Its single formal observation completed
successfully but returned 29 ordinary Windows GPU-client PIDs, including
desktop, shell, browser, Docker Desktop, and system processes. The frozen
terminal remains:

```text
CUDA_COMPUTE_BUSY / NO_GO
```

That result is valid under the approved PID-only classifier and must never be
overwritten or reinterpreted as a pass. It demonstrates that PID presence is
not a usable compute-idle predicate on this WDDM workstation.

The second unsafe assumption is already present in
`scripts/run_wave0_a11.ps1`: `ConvertTo-A11GpuRows` counts a row only when
`used_gpu_memory` is numeric and ignores `[N/A]`. NVIDIA documents that process
GPU-memory usage is not available under WDDM because Windows KMD manages the
memory. A real CUDA process can therefore also report unavailable memory. A
memory-value classifier could admit an occupied GPU and is a load-bearing
launcher defect.

This recovery replaces both assumptions with one process-type contract.

## Immutable evidence and lineage

The following remain immutable:

- CUDA-observability plan `f45d84eec13b98ee4566497252375f20251fd2d3`.
- CUDA-observability design `5451c50cc20b1c297c9bdd3535a793eff993158d`.
- Ordering-recovery plan `52fe25d529f7d64e986864576653d0d14a6e484b`
  and blob `901c2b31c033d44949915d2081a8cf715fd2e699`.
- Ordering-recovery design `68f51519d2cb480200ca4fef740651b0d15dd76f`.
- Digest-recovery plan and design `03115325f36da31b135b4593fb8df1689eac9a35`
  and `2db13d302da97a241daeaba3578cd9cec1c8073b`.
- Diagnostic-root erratum `101bb79369399cc3947f1c667f0a11988f916638`.
- Runtime-transport plan and design `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`
  and `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`.
- All five consumed A11 attempts, authorization identities, images, leases,
  artifact records, and historical digests.
- The Task 1 report terminal and its parked command-retention defect.

The commit containing this document must be the direct child of `f45d84e...`
and add only this file. A later implementation plan must be its one-file direct
child. A later implementation commit must be the plan's direct child and must
contain exactly the seven implementation paths defined below.

## Decision

Use one type-aware, read-only XML observation per scheduled gate:

```text
nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63
```

The process `type` reported by NVIDIA is authoritative for admission. PID,
process name, and GPU-memory text are evidence only. They never weaken or
override the type classification.

The observer has no retry, fallback, process mutation, timeout replacement,
name allowlist, or second native query. Query start failure, nonzero exit,
unreadable XML, an unsupported XML shape, missing type information, or an
identity mismatch is a fail-closed terminal.

This is a point-in-time admission gate. It proves only that no compute-type
context was observed at that gate. It does not claim that an unrelated process
cannot start later. The launcher minimizes that inherent race by retaining
separate scheduled observations at global preflight and immediately before
each phase lease acquisition.

## Alternatives considered

### 1. Type-aware `nvidia-smi` XML — selected

This uses the vendor tool already present on the host, exposes documented
process types, preserves raw evidence, and requires no dependency or driver
change. NVIDIA does not promise backward-compatible `nvidia-smi` output, so
the parser accepts only the proven contract and fails closed on change.

### 2. Direct NVML native interop — rejected for this recovery

NVML exposes compute, graphics, MPS, and all-process modes, but a PowerShell
P/Invoke layer adds ABI, structure-version, driver-support, and memory-safety
surface. The newer process-detail API is not uniformly supported across the
target hardware generations. This complexity is not justified while the
installed vendor CLI exposes the required type evidence.

### 3. Dedicated Linux or TCC compute host — deferred

A non-display compute host offers stronger resource isolation, but requires a
different execution environment or hardware. Switching the RTX 4090 display
driver model is operationally invasive and outside the narrow recovery scope.
It remains a worthwhile long-term infrastructure improvement.

### 4. Lease/container-only or process-name policy — rejected

Cooperative project leases cannot detect an unrelated CUDA workload. Process
names are mutable and do not prove context type. Neither policy satisfies the
existing exclusive-resource boundary.

## Components

### Secure XML decoder

A pure PowerShell function consumes captured stdout and returns a closed GPU
and process record. It does not invoke native commands.

The decoder must:

- use an `XmlReader` with `XmlResolver = $null`;
- ignore, but never resolve, the external NVIDIA DTD declaration normally
  emitted by `nvidia-smi -q -x`;
- reject internal DTD subsets, entity declarations, entity references, and
  documents over a fixed byte/character limit;
- require the expected root and exactly one target GPU;
- require the exact registered name and UUID;
- require a nonempty driver version and `WDDM` current driver model;
- require each process row to contain a positive PID, nonempty name, and one
  exact supported type;
- preserve process order and raw memory text without using memory to classify;
- reject missing, duplicate identity fields and unknown structural variants.

An external DTD filename or schema-version change may be recorded, but no
external file is loaded. Any XML feature that cannot be proven safe becomes
`CUDA_XML_PARSE_FAILURE / NO_GO` or
`CUDA_PROCESS_TYPE_UNPROVABLE / NO_GO`.

### Pure type classifier

The classifier consumes only decoded records:

| Exact type | Meaning | Admission |
| --- | --- | --- |
| `G` | graphics context | allowed and recorded |
| `O` | other/context-less resource use | blocking |
| `C` | compute context | blocking |
| `M` | MPS compute context | blocking |
| `C+G` | compute and graphics contexts | blocking |
| `M+C` | MPS and compute contexts | blocking |
| missing or anything else | unprovable | blocking `NO_GO` |

The presence of any `C`, `M`, `C+G`, or `M+C` row produces
`CUDA_COMPUTE_BUSY / NO_GO`. An `O` row produces
`CUDA_OTHER_RESOURCE_BUSY / NO_GO`: NVIDIA defines this type to include
context-less GPU resource allocation, so it cannot be admitted as ordinary
graphics. Zero rows or exclusively `G` rows produces `CUDA_IDLE / PASS`.
Duplicates are retained as evidence; a blocking duplicate still blocks. No
PID is deduplicated away before classification.

### Single-invocation observer

The observer starts one `System.Diagnostics.Process` with the exact argv,
redirects stdout and stderr as UTF-8, waits for that one process, and passes
captured stdout to the secure decoder and classifier. It never invokes a
shell pipeline or another `nvidia-smi` process.

The observation record contains:

- schema version and unique observation ID;
- exact argv, start and finish timestamps;
- start status and any start exception type/message;
- exit code and complete stdout/stderr text;
- byte counts and SHA-256 digests of both streams;
- GPU name, UUID, driver version, and driver model when provable;
- ordered process rows with PID, type, name, and raw memory text;
- allowed and blocking counts and blocking PIDs;
- classification, reason code, and terminal.

Canonical compact JSON is emitted before a terminal throw. Its UTF-8 byte
count and SHA-256 digest are recorded with the nested tool result. If an exec
session is yielded, only that same session may be resumed to completion.

### Launcher integration

The implementation replaces both current CSV query sites and the
memory-value logic in `ConvertTo-A11GpuRows` with the shared decoder,
classifier, and observer contract.

`Resolve-A11Worktree` performs the global read-only observation after Git,
Docker, artifact, image, project-container, active-lease, and historical
preservation checks. Phase initialization performs a distinct observation
immediately before acquiring that phase's lease. Each is a separately
scheduled gate, not a retry of another observation.

Lease, project-container, destination, identity, artifact, image, receipt,
split, threshold, replica, acquisition, and statistical contracts remain
independent mandatory gates.

## Data flow and closed outcomes

For every entry or preservation gate:

1. Prove Git lineage, identity, isolation, clean scope, and fixed inputs.
2. Re-prove the required artifact, image, lease, container, and historical
   envelope.
3. Define and synthetically prove the pure decoder and classifier.
4. Capture the exact command artifact and its digest before execution.
5. Start exactly one native XML observation.
6. Emit complete structured evidence before any throw.
7. Stop on the first exact `NO_GO`; only `CUDA_IDLE / PASS` permits the next
   plan step.

The closed terminal set is:

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

`CUDA_OBSERVATION_UNPROVABLE` is controller-only and applies when the tool
completion or evidence cannot be observed. There is no fallback to PID-only,
memory-only, another output format, a name allowlist, or a replacement query.

## TDD and verification

All implementation follows RED/GREEN/refactor. CPU tests inject XML and a
fake native boundary; they never call GPU, Docker, network, model code, or the
external artifact root.

Required RED cases include:

- no processes and exclusively `G` rows pass;
- an `O` row blocks with `CUDA_OTHER_RESOURCE_BUSY / NO_GO`;
- each of `C`, `M`, `C+G`, and `M+C` blocks;
- `[N/A]` memory with a compute type still blocks;
- numeric memory with a graphics type does not manufacture a compute type;
- process names and PID values cannot change an otherwise valid type result;
- missing or unknown type, malformed PID, wrong/multiple GPU identity,
  missing driver model/version, malformed/truncated XML, oversized XML,
  internal DTD/entity/XXE input, start failure, and nonzero exit all fail
  closed with the precise terminal;
- injected invocation counters prove one native start per observation;
- static scans prohibit fallback query strings, retries, process mutation,
  service control, GPU reset, and program-name allowlists;
- preflight and both phase call sites use the same production helper;
- the prior PID-only and numeric-memory behaviors fail for their intended
  reasons before the implementation turns the suite green.

Required GREEN gates include focused launcher tests, the complete launcher
suite, the full CPU suite with bytecode/cache disabled, PowerShell 7 and
Windows PowerShell 5.1 parsers, JSON schema validation, Python style checks,
`uv.lock` digest, Dockerfile static checks, BuildKit `--check`, the exact
tracked allowlist, empty staging before review, and `git diff --check`.

No live GPU observation is used as a unit test. The first real observation is
the implementation plan's complete Task 1 entry gate. A Task 1 `NO_GO` stops
before implementation. A Task 1 pass permits inherited TDD. Later Task 6 and
dependency-diagnostic pre/post observations are new scheduled preservation
gates, never retries.

## Implementation scope

The later implementation commit retains the exact seven-path allowlist from
the immutable ordering recovery:

1. `configs/a11/preserved-attempts.json`
2. `schemas/a11-preserved-attempts.schema.json`
3. `scripts/run_uv_sync_with_retries.py`
4. `scripts/run_wave0_a11.ps1`
5. `docker/wave0.Dockerfile`
6. `tests/gates/test_wave0_a11_launcher.py`
7. `tests/scripts/test_run_uv_sync_with_retries.py`

The XML decoder and observer live in the existing launcher and its tests. No
new runtime dependency, schema path, helper executable, or parallel launcher
is introduced. The other five paths remain necessary because this design is
a normative overlay on the still-unimplemented ordering-recovery plan.

Tasks before the final implementation commit create no commits. The final
implementation is one append-only seven-path commit with author and committer:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

## Command and result retention

Every nontrivial gate command is materialized before execution as a uniquely
named `.ps1` file in this plan's ignored SDD workspace. The controller then
executes only the short, literal `pwsh -File` payload. The report records:

- the literal tool-call payload;
- the complete script source bytes in a fenced block;
- script path, UTF-8 byte count, and SHA-256;
- exact argv, tool result, exit code, output, session ID, and chunk ID;
- every same-session poll result in order.

Review begins only after the report contains these fields. A missing literal
payload is a review failure; it is never reconstructed from source boundaries
after execution.

## Runtime and authorization boundary

This recovery may implement and verify code and may run the one dependency-only
diagnostic already bounded by the inherited plan. It may not invoke
`scripts/run_wave0_a11.ps1`, initialize the model, acquire a formal campaign
lease, create calibration/validation runtime identities, access RDD, or start
Wave 1.

No `OwnerAuthorizationId` is required or accepted by this recovery. A later
formal A11 attempt requires a fresh explicit authorization bound to the exact
implementation source commit, original A11 specification commit, original
A11 plan commit, and branch. Consumed owner IDs remain immutable evidence.

## Out of scope

- Terminating, pausing, reprioritizing, or otherwise mutating a GPU process.
- Task Manager, service control, Docker stop, WSL shutdown, driver reset, or
  switching the Windows driver model.
- Allowing or blocking a process based on executable name, parent PID, vendor,
  or current desktop role.
- Retrying or substituting a failed observation.
- Modifying an existing artifact, image, lease, run, or diagnostic record.
- Dependency, model, split, threshold, receipt, or statistical-contract drift.
- A formal A11 model campaign, Wave 1, push, merge, release, tag, or changes to
  another repository.

## Success criteria

The recovery is complete only when:

1. The design and plan are exact one-file commits with the required lineage
   and identity.
2. A fresh complete entry gate produces `CUDA_IDLE / PASS` from a type-aware
   single observation and every preservation check passes.
3. The seven-path implementation is produced by TDD and every CPU, parser,
   schema, style, scope, and Docker static gate passes.
4. A fresh candidate preservation gate again produces `CUDA_IDLE / PASS`.
5. Cold review reports `Critical=0` and `Important=0`.
6. The single implementation commit has the exact parent, paths, identity,
   clean worktrees, fixed lockfile, and preserved evidence.
7. The one dependency-only diagnostic closes with its exact formal-runtime-
   forbidden terminal.

Any failed frozen gate is preserved as `NO_GO` and stops the sequence for
redesign. It is never permission to tune to the observed process list.

## References

- NVIDIA System Management Interface documentation:
  <https://docs.nvidia.com/deploy/nvidia-smi/index.html>
- NVIDIA NVML `nvmlProcessInfo_t` documentation, including the WDDM memory
  limitation:
  <https://docs.nvidia.com/deploy/nvml-api/structnvmlProcessInfo__t.html>
- NVIDIA NVML process-mode enumeration:
  <https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceStructs.html>
- Preserved Task 1 report:
  `.superpowers/sdd/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery/task-1-report.md`
