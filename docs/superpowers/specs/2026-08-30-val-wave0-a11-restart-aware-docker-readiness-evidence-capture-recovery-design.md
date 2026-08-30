# Wave 0 A11 Restart-Aware Docker Readiness and Evidence-Capture Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** codex/wave0-model-contract

**Required parent:** 9a80b320a18255cb52f6988dc1feadbe78a7cb7d

## Purpose

Recover the Wave 0 A11 entry-gate sequence from two independently preserved
failures without weakening the launcher, Docker, artifact, GPU, CPU, runtime, or
authorization boundaries:

1. the fresh formal entry child started after Docker Desktop had already been
   terminated by a Windows restart, so the Linux-engine pipe was absent before
   any live WDDM observation; and
2. the completed report did not retain the complete launcher-revalidation
   output, the child's first launcher-identity JSON record, or complete evidence
   for three failed pre-launch controller wrappers.

The recovery adds a restart-aware, read-only Docker eligibility barrier before
any new entry child may start. It also replaces ad hoc controller wrappers and
human reconstruction with a single manifest-driven machine recorder that
retains raw stdout and stderr bytes, exact argv, timing, process, exit, and hash
evidence for every nontrivial command.

This design does not retry or reinterpret the consumed child. It schedules no
new entry execution, Docker stage, GPU query, dependency diagnostic, model
campaign, or formal A11 runtime. Its implementation plan must separately
authorize any new entry-child slot and preserve every inherited stop gate.

## Authoritative failure and root cause

The consumed recovery workspace is:

~~~text
.superpowers/sdd/2026-08-30-val-wave0-a11-powershell-launcher-identity-recovery/
~~~

Its exact Task 1 terminal is:

~~~text
CUDA_OBSERVATION_UNPROVABLE / NO_GO
~~~

The formal entry child:

- launched exactly once through the frozen signed PowerShell executable;
- emitted an exact launcher-identity match;
- reached the inherited Docker identity check;
- failed to connect to npipe:////./pipe/dockerDesktopLinuxEngine;
- exited 1 after 25.5676197 seconds;
- did not start a live nvidia-smi process;
- did not create a CUDA observation record or digest;
- did not materialize or run the CPU baseline; and
- was never retried, substituted, polled, or relaunched.

The local host timeline resolves the immediate cause:

| Local time, UTC+08:00 | Evidence |
|---|---|
| 2026-08-30 12:05:13 | Windows User32 event 1074 records a restart initiated through StartMenuExperienceHost on behalf of the signed-in user. |
| 2026-08-30 12:05:14 | Docker Desktop records com.docker.backend.exe exiting with status 0x40010004. |
| 2026-08-30 12:05:25 | Kernel-Power event 109 records a kernel-API reboot transition. |
| 2026-08-30 12:05:33 | Kernel-General event 13 records OS shutdown. |
| 2026-08-30 12:05:47 | Kernel-General event 12 records the next OS start. |
| After the reboot | Docker Desktop did not restore its backend or Linux-engine named pipe before the formal child started. |

Microsoft's NTSTATUS registry names 0x40010004
DBG_TERMINATE_PROCESS. The evidence proves that the Docker backend was
terminated as part of the host restart sequence. It does not prove which human
or upstream software decision requested the restart, and this recovery does not
need or infer that cause.

The architectural defect is narrower: the controller proved Git and launcher
state but had no pre-child Docker lifecycle eligibility barrier. The child start
therefore consumed the one-shot entry slot even though a required external
service had been unavailable since before the recovery plan commit.

The evidence-completeness defect is separate. The independent reviewer found:

1. the report summarized, rather than retained, complete revalidation and child
   identity output; and
2. one failed immutable-object diagnostic and two failed static wrappers were
   acknowledged without their exact payloads, sources, hashes, complete outputs,
   or tool metadata.

Plan commit 9a80b320a18255cb52f6988dc1feadbe78a7cb7d prohibits
reconstructing a missing payload after execution. Those gaps are authoritative,
cannot be repaired retroactively, and motivate the new recorder boundary.

## Immutable evidence and lineage

The following remain immutable:

- launcher-identity recovery design commit
  3e98d1d56caede9a1baaf215da4e418112a73643;
- launcher-identity recovery plan commit
  9a80b320a18255cb52f6988dc1feadbe78a7cb7d;
- WDDM recovery design and plan commits
  0053a8b30c8639ea9b9752ca2171117692fe78b0 and
  42c200d8a801b142cde394cda7a0520bd9c30a83;
- CUDA-observability, ordering, digest, runtime-transport, and diagnostic-root
  recovery documents and commits incorporated by those plans;
- all consumed A11 source commits, attempts, owner identities, images, leases,
  artifacts, historical digests, diagnostics, reports, and terminals;
- the earlier hard-coded-launcher entry and report;
- the current restart-affected entry and every file in its ignored workspace;
  and
- the independent review package and findings.

The current recovery files remain exactly:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| task-1-launcher-identity.ps1 | 19,471 | 45b53859a33b9ddbbad6fbac85bcd1f148370f0d1597b07bcf08e9f259e4231e |
| task-1-entry-launcher-revalidate.ps1 | 14,918 | 1480c99c32857a780d61cfc18145313ef68f5a5d44d8f9236fe030b98a6045c6 |
| task-1-entry-gate.ps1 | 58,392 | 95e517792de222fdeaa795209f99a97d56dd0b1cb6c6bd219552a8940382199e |
| task-1-report.md | 108,312 | 06932bf93851bdf6033dcef2e896394d34be4d875fa0ea4dd6b0e2bcba8db18a |
| task-1-agent-report.md | 8,000 | c8746d9132eec2106310ac87840ea7e5a827db468d3cdda746a8d5b3f4170eb2 |
| task-1-review-package.md | 3,223 | f160fb5ceca985e07019d2133193d9374b9f791866566a02d5af3880339639cb |
| task-1-review-findings.md | 1,193 | 00ec22e3daef104e0208731f8f5ffba3fcded35c6845544d624702598e474ad4 |

The new design commit must be a one-file direct child of
9a80b320a18255cb52f6988dc1feadbe78a7cb7d. Its implementation plan must be a
one-file direct child of the design commit. Neither documentation commit may
change product code, ignored evidence, Docker state, external artifacts, or
another repository.

Author and committer for both documentation commits and any later implementation
commit remain exactly:

~~~text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
~~~

## Decision

Use a two-boundary recovery:

1. a restart-aware Docker eligibility barrier that must pass before an entry
   child can consume its one-shot slot; and
2. a manifest-driven machine recorder that is the only permitted executor for
   nontrivial Task 1 commands and the authoritative source for their complete
   command results.

The eligibility barrier is read-only. It does not start, stop, restart, update,
repair, or configure Docker Desktop, WSL, Hyper-V, a Windows service, the GPU, or
another process. An unavailable external prerequisite pauses before the entry
child; it is not converted into a GPU result and is not tuned automatically.

The recorder writes only predetermined create-new machine-evidence files below a
fresh ignored recovery workspace. This is a narrow replacement for the previous
rule that forced all output through human-authored reports. Human-authored
scripts, manifests, briefs, and reports still require apply_patch. Machine raw
captures are never human-authored and may be created only by the frozen recorder
using the exact allowlist and no-clobber contract below.

## Alternatives considered

### 1. Restart-aware eligibility plus one recorder — selected

This prevents a known-unavailable Docker engine from consuming the next entry
child and closes the missing-output boundary without starting or repairing
Docker. It preserves the exact formal child, WDDM query, GPU admission, CPU
baseline, implementation allowlist, and runtime separation.

### 2. Add one controller docker info call — rejected

A single instantaneous call would have caught the preserved absence but would
not prove stability across a short window, freeze the host boot epoch, or close
the race between the check and child launch. It also leaves ad hoc command
wrappers and incomplete tool-output transcription unchanged.

### 3. Start or restart Docker Desktop automatically — rejected

Host mutation would hide the difference between a ready prerequisite and a
repaired prerequisite. It introduces service-control authority, recovery timing,
update prompts, WSL lifecycle changes, and potential container or volume side
effects into a repository gate. None belongs in A11 statistical replay.

### 4. Move the gate to WSL, Linux, or a dedicated TCC host — deferred

That could provide a different Docker and CUDA lifecycle, but it would replace
the approved Windows WDDM observation contract and canonical hardware execution
path. It is an architectural migration, not a narrow recovery.

## Components

### Unit A: append-only recovery lineage

The implementation plan creates a distinct ignored workspace:

~~~text
.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/
~~~

Before that workspace exists, the controller proves:

- linked-worktree topology;
- branch codex/wave0-model-contract;
- exact design and plan lineage;
- required author and committer identity;
- empty tracked, untracked, and staged Git scope;
- absence of the exact new workspace;
- all inherited immutable Git objects;
- every consumed evidence path, byte count, and SHA-256; and
- absence of implementation, CPU, dependency-diagnostic, or formal-runtime
  outputs attributable to the new recovery.

After the absence proof, coordination and human-authored files are created only
with apply_patch. Every preformal command revision receives a unique immutable
command ID. A failed authoring or static command may be superseded only before
Docker eligibility begins, with the failed source and result retained under its
original ID. It is never overwritten or omitted from the report.

### Unit B: frozen host epoch

The recorder obtains one closed host-epoch record before Docker sampling:

~~~text
schema_version
computer_name
windows_product_name
windows_build
boot_time_utc
boot_epoch_sha256
observed_at_utc
monotonic_timestamp
~~~

boot_time_utc comes from the local operating-system instance and is serialized
in UTC with seven fractional digits and a Z suffix. The epoch digest is canonical
compact UTF-8 JSON over the closed fields excluding the digest itself.

The same boot epoch must remain exact through all Docker samples, launcher
revalidation, and the final pre-child handoff. A change stops before child
creation with:

~~~text
HOST_BOOT_EPOCH_CHANGED / NO_GO
~~~

The host record is evidence of one boot epoch, not proof that the host can never
restart. The child still performs its inherited checks and any later loss of an
external service remains a closed failure.

### Unit C: frozen Docker CLI identity

The controller resolves docker.exe once through the current process environment
and freezes:

- canonical absolute path;
- current command-resolution path;
- ordinary-file and parent-chain link state;
- byte count and SHA-256;
- file and product versions;
- Authenticode status, signer subject, and certificate thumbprint; and
- Docker client version output.

Resolution is admitted only when the canonical executable and command source
agree, the file and every parent are non-linked, the signature is Valid, and the
signer subject is exactly:

~~~text
CN=Docker Inc, O=Docker Inc, L=Palo Alto, S=California, C=US, SERIALNUMBER=4817464, OID.2.5.4.15=Private Organization, OID.1.3.6.1.4.1.311.60.2.1.2=Delaware, OID.1.3.6.1.4.1.311.60.2.1.3=US
~~~

The observed path, byte count, file/product versions, SHA-256, and signer
thumbprint are frozen fresh for the eligibility observation. No PATH-only
launch, alias, shim, script, UNC path, unsigned binary, alternate signer, second
candidate, or fallback is accepted.

The read-only host snapshot used to validate this rule was:

~~~text
path: C:\Program Files\Docker\Docker\resources\bin\docker.exe
bytes: 43093936
file version: 29.6.1
product version: 29.6.1
SHA-256: e768033e4b3f0dc760162f417a80360094644d16cd9fb12ad65c9d97508c076f
signature: Valid
signer thumbprint: CACB4F507942C182C47EF14E7B9050CBDE780EB9
~~~

These values prove that the policy is executable on the current host. Except
for the exact signer-subject policy above, they are not silently reused as a
fresh readiness identity.

Every readiness sample and child preflight uses the frozen absolute docker.exe
path. Docker identity drift stops before child creation with:

~~~text
DOCKER_CLI_IDENTITY_MISMATCH / NO_GO
~~~

### Unit D: bounded Docker readiness sampler

The readiness sampler records exactly three planned samples separated by two
fixed ten-second monotonic waits. These are stability samples, not retries:

- if sample 1 fails, samples 2 and 3 do not run;
- if sample 2 fails, sample 3 does not run;
- a failed sample is not repeated;
- the wait duration is not tuned to an observed result; and
- no additional sample is permitted.

Each sample captures:

~~~text
schema_version
sample_index
host_boot_epoch_sha256
sample_started_utc
sample_finished_utc
monotonic_start
monotonic_finish
docker_desktop_processes
backend_processes
linux_engine_pipe_present
backend_api_pipe_present
docker_info_argv
docker_info_exit_code
docker_info_stdout_byte_count
docker_info_stdout_sha256
docker_info_stderr_byte_count
docker_info_stderr_sha256
docker_operating_system
docker_server_version
docker_daemon_id
docker_daemon_name
docker_root_dir
terminal
~~~

Process records are closed, sorted objects containing PID, start time, canonical
executable path, byte count, SHA-256, and link state. They are evidence of
continuity, not authority to mutate a process.

The exact docker info format is frozen by the implementation plan. Admission
requires:

- unchanged host boot epoch;
- at least one ordinary Docker Desktop process and one ordinary backend process;
- identical process identity tuples across all samples;
- both required named pipes present;
- docker info exit 0 with separately captured stdout and stderr;
- operating system exactly linux;
- server version exactly 29.6.1;
- nonempty, stable daemon ID, daemon name, and Docker root directory; and
- identical canonical Docker result fields across all three samples.

The third sample is the final readiness revalidation. The recorder must begin
launcher revalidation within five monotonic seconds of its completion. Missing
or unstable evidence closes with one of:

~~~text
DOCKER_DESKTOP_UNAVAILABLE / NOT_READY
DOCKER_LINUX_ENGINE_UNREADY / NOT_READY
DOCKER_READINESS_UNSTABLE / NO_GO
DOCKER_READINESS_UNPROVABLE / NO_GO
DOCKER_READINESS_PASS
~~~

NOT_READY is an eligibility result, not an entry-child attempt. It creates
append-only readiness evidence, does not start a child, and pauses for external
owner operation. A later readiness evaluation requires a new observation ID and
fresh append-only evidence but not a new model-runtime OwnerAuthorizationId.

NO_GO applies when comparable state drifts or evidence capture is malformed.
It stops this recovery plan for review. PASS is intermediate and authorizes only
the immediate launcher revalidation and entry-child handoff.

### Unit E: manifest-driven machine recorder

Before execution, apply_patch creates a closed command manifest. Each command
record contains:

~~~text
schema_version
command_id
purpose
executable_identity_sha256
executable_path
argv
working_directory
environment_allowlist
stdin_policy
stdout_capture_path
stderr_capture_path
result_path
start_deadline_policy
timeout_policy
permitted_child_count
command_source_paths
command_source_byte_counts
command_source_sha256
~~~

The manifest is canonical compact UTF-8 JSON with a recorded byte count and
SHA-256. Duplicate keys, extra fields, missing fields, noncanonical paths,
unfrozen sources, unexpected environment keys, or output-path collisions stop
with zero command execution.

The frozen PowerShell recorder:

- uses System.Diagnostics.Process directly;
- sets UseShellExecute to false;
- never invokes a shell command string;
- passes an argv array without interpolation;
- redirects stdout and stderr separately;
- captures both streams concurrently as raw bytes;
- supplies no stdin unless the manifest explicitly declares a closed byte
  payload;
- records process start and completion timestamps, PID, exit code, signal or
  exception state, timeout state, and every same-process wait;
- computes byte count and SHA-256 over each exact raw stream;
- creates every machine file with create-new/no-clobber semantics;
- flushes and closes each file before publishing its result record;
- never deletes, truncates, appends to, renames over, or rewrites a file; and
- executes only command IDs present in the frozen manifest.

The recorder may create only these predetermined machine-generated paths below
the new ignored workspace:

~~~text
machine/<command-id>.stdout.bin
machine/<command-id>.stderr.bin
machine/<command-id>.result.json
machine/<command-id>.result.sha256
~~~

This is the only file-write exception introduced by the design. It does not
permit shell redirection, Set-Content, Out-File, tee, transcript reconstruction,
arbitrary logging, product output, tracked writes, external artifact writes, or
edits to human-authored files.

The authoritative complete command output is the pair of raw capture files.
The human report indexes their byte counts and digests and may include a decoded
rendering, but it need not duplicate binary-identical output inline. A reviewer
must be able to recompute every result digest directly from the retained machine
files. Missing, unreadable, extra, linked, or mismatched machine evidence closes:

~~~text
EVIDENCE_CAPTURE_UNPROVABLE / NO_GO
~~~

### Unit F: entry-child handoff

After DOCKER_READINESS_PASS, the same recorder performs, in order:

1. verify the host boot epoch remains exact;
2. revalidate the frozen PowerShell launcher identity once;
3. verify the five-second handoff deadline;
4. freeze the complete entry script, source bytes, digest, argv, working
   directory, environment allowlist, and machine capture destinations;
5. start the entry child exactly once;
6. capture complete child stdout and stderr raw bytes concurrently;
7. require the child launcher-identity record as its first structured output;
8. preserve the complete exit/result record; and
9. publish exactly one Task 1 terminal.

Process creation consumes the new entry-child slot. A start exception, malformed
first record, Docker loss after start, artifact mismatch, GPU failure, timeout,
or missing result is not eligible for another child under this plan.

The child inherits unchanged:

- exact PowerShell identity and self-attestation;
- linked/canonical Git and clean-scope checks;
- immutable object, artifact, image, lease, container, diagnostic, and historical
  preservation gates;
- versioned canonical inventory logic and frozen digests;
- exact Docker Linux/server identity;
- the secure WDDM XML decoder and process-type classifier;
- exactly one native command:
  nvidia-smi -q -x -i GPU-7639cc81-2a55-164e-e5be-c5cd71752a63;
- zero-process or G-only admission;
- CPU baseline only after CUDA_IDLE / PASS; and
- repository and external evidence preservation after every terminal.

There is no Docker retry, child retry, GPU retry, alternate executable, alternate
query, cached observation, process-name allowlist, memory heuristic, process
mutation, service control, or fallback.

### Unit G: report, review, and continuation gate

The Task 1 report is created with apply_patch only after all authoritative
machine files are closed. It records:

- every command manifest and digest;
- all source paths, byte counts, and SHA-256 values;
- exact executable identities and argv;
- machine raw-output paths, byte counts, and SHA-256 values;
- result-record paths and digests;
- tool-level completion metadata;
- boot epoch and Docker sample chain;
- launcher comparison;
- child first-record validation;
- all entry results;
- the one final terminal; and
- complete preservation verification.

An independent reviewer receives the design, plan, task brief, report, command
manifest, machine inventory, source inventory, and final Git state. The reviewer
does not rerun Docker, GPU, or reported commands.

Any missing payload or result is preserved as a finding. It is never
reconstructed after execution. Only an independent APPROVED verdict on both
behavior and evidence completeness plus ENTRY_GATE_PASS permits Task 2.

## Data flow

~~~text
clean approved HEAD
  -> prove new workspace absent and old evidence immutable
  -> materialize recorder, static verifier, command manifest, and sources
  -> synthetic parser/serializer/recorder tests
  -> freeze host boot epoch
  -> freeze Docker CLI identity
  -> Docker readiness sample 1
  -> fixed 10-second wait
  -> Docker readiness sample 2
  -> fixed 10-second wait
  -> Docker readiness sample 3
  -> DOCKER_READINESS_PASS
  -> verify <=5-second handoff deadline
  -> revalidate host epoch and PowerShell launcher
  -> start exactly one entry child
  -> child launcher self-attestation
  -> inherited preservation and Docker gates
  -> exactly one WDDM XML observation
  -> CUDA_IDLE / PASS
  -> inherited CPU baseline
  -> ENTRY_GATE_PASS
  -> independent evidence review
  -> Task 2 eligible
~~~

Any earlier NOT_READY pauses before child creation. Any NO_GO stops at its first
failure. No branch skips a required observation or converts absence into PASS.

## Error handling and closed outcomes

Pre-child eligibility outcomes:

~~~text
HOST_BOOT_EPOCH_CHANGED / NO_GO
DOCKER_CLI_IDENTITY_MISMATCH / NO_GO
DOCKER_DESKTOP_UNAVAILABLE / NOT_READY
DOCKER_LINUX_ENGINE_UNREADY / NOT_READY
DOCKER_READINESS_UNSTABLE / NO_GO
DOCKER_READINESS_UNPROVABLE / NO_GO
DOCKER_READINESS_PASS
EVIDENCE_CAPTURE_UNPROVABLE / NO_GO
~~~

Launcher and WDDM outcomes remain unchanged:

~~~text
POWERSHELL_LAUNCHER_IDENTITY_MISMATCH / NO_GO
POWERSHELL_LAUNCHER_UNPROVABLE / NO_GO
POWERSHELL_LAUNCHER_IDENTITY_PASS
CUDA_QUERY_START_FAILURE / NO_GO
CUDA_QUERY_FAILURE / NO_GO
CUDA_XML_PARSE_FAILURE / NO_GO
CUDA_GPU_IDENTITY_MISMATCH / NO_GO
CUDA_PROCESS_TYPE_UNPROVABLE / NO_GO
CUDA_COMPUTE_BUSY / NO_GO
CUDA_OTHER_RESOURCE_BUSY / NO_GO
CUDA_IDLE / PASS
CUDA_OBSERVATION_UNPROVABLE / NO_GO
ENTRY_GATE_PASS
~~~

NOT_READY never permits host mutation or automatic waiting beyond the fixed
sampler. It tells the owner which external prerequisite must be restored.

The first NO_GO is terminal for this plan. The recorder closes any already-open
machine streams, publishes only create-new result evidence that can be proven,
and stops. It never starts a replacement command to fill a missing record.

## TDD and verification

Before any real Docker CLI, Docker pipe, external artifact root, or GPU access,
synthetic tests must prove:

### Canonical evidence tests

- closed-property and duplicate-key rejection;
- stable compact UTF-8 serialization and SHA-256;
- exact raw-byte preservation for empty, ASCII, UTF-8, CRLF, no-final-newline,
  NUL-containing, and large stdout/stderr streams;
- concurrent stdout/stderr draining without deadlock;
- create-new collision rejection;
- result digest recomputation;
- linked file or directory rejection; and
- missing or extra machine artifact rejection.

### Recorder tests

- argv elements are preserved without shell interpolation;
- environment is constructed from the exact allowlist;
- stdin remains closed by default;
- exit 0, nonzero, start exception, timeout, and signal-like termination produce
  closed results;
- one command ID starts no more than its permitted child count;
- a manifest/source/digest mismatch starts zero processes;
- stdout and stderr are never merged, reordered, decoded before hashing, or
  silently truncated; and
- no shell, redirection, overwrite, delete, rename-over, or unmanifested path is
  reachable.

### Host and Docker sampler tests

- stable injected boot epochs pass and any mutation fails;
- missing Desktop/backend process produces NOT_READY;
- PID reuse with a different start time or executable identity fails;
- missing pipe produces NOT_READY;
- malformed, nonzero, incomplete, Windows-engine, wrong-version, empty-daemon,
  or drifting Docker samples fail closed;
- exactly three successful samples and two fixed waits are required;
- a failure stops later samples;
- no automatic Docker start, restart, service call, WSL call, or process
  mutation exists;
- handoff later than five monotonic seconds stops before the child; and
- each sample invokes exactly one frozen docker info payload.

### Entry integration tests

- launcher identity still reads exactly once per scheduled discovery or
  revalidation role;
- child self-attestation remains the first child output;
- no Git, Docker, artifact, lease, historical, CPU, or GPU action precedes it;
- formal child cardinality is zero on NOT_READY/NO_GO and exactly one after full
  readiness PASS;
- the entry observer contains exactly one permitted nvidia-smi start;
- CPU commands are absent before CUDA_IDLE / PASS; and
- every inherited preservation and seven-path scope assertion remains exact.

### Static and repository verification

- all complete PowerShell sources parse under PowerShell 7.6.4 and Windows
  PowerShell 5.1;
- schema and canonical JSON vectors validate;
- Python tests use PYTHONDONTWRITEBYTECODE=1 and -p no:cacheprovider;
- no test invokes real Docker, GPU, network, model, or the external artifact
  root;
- Dockerfile/Buildx checks remain static until inherited Tasks 5 and 6;
- uv.lock remains byte-identical at its frozen SHA-256;
- linked and canonical worktrees are clean at every execution boundary; and
- all historical evidence hashes remain unchanged.

## Implementation scope

The implementation plan is a narrow overlay on plan commit
9a80b320a18255cb52f6988dc1feadbe78a7cb7d.

Before ENTRY_GATE_PASS, it may create only ignored recovery evidence under the
new workspace. Recorder, sampler, static verifier, manifests, raw captures,
reports, task briefs, and review packages remain ignored and are not production
dependencies.

After ENTRY_GATE_PASS, the inherited implementation retains exactly these seven
tracked paths:

1. configs/a11/preserved-attempts.json
2. schemas/a11-preserved-attempts.schema.json
3. scripts/run_uv_sync_with_retries.py
4. scripts/run_wave0_a11.ps1
5. docker/wave0.Dockerfile
6. tests/gates/test_wave0_a11_launcher.py
7. tests/scripts/test_run_uv_sync_with_retries.py

Tasks 2 through 7, TDD order, CPU isolation, Docker static checks, one
implementation commit, commit identity, dependency-only diagnostic, and formal
runtime prohibition remain inherited. The recovery does not introduce a tracked
recorder, monitoring service, daemon, dependency, schema, CLI, or background
automation.

## Runtime and authorization boundary

This design, its written specification, implementation plan, ignored recorder,
read-only eligibility observations, local TDD, static verification, code review,
and inherited dependency-only diagnostic do not require or accept an
OwnerAuthorizationId.

They may not:

- invoke scripts/run_wave0_a11.ps1;
- build or run a formal A11 model image;
- initialize or load a model;
- acquire a formal campaign lease;
- create calibration or validation runtime identities;
- access RDD or another dataset root;
- start Wave 1;
- generate, guess, reserve, or consume an owner authorization;
- push, merge, rebase, tag, release, or publish; or
- modify another repository.

A later formal A11 model-runtime attempt requires a new explicit
OwnerAuthorizationId bound to the then-exact source commit, original A11
specification commit, original A11 plan commit, and branch. Every consumed owner
identity remains immutable evidence.

## Out of scope

- Editing, deleting, retrying, reusing, or reclassifying any consumed attempt.
- Reconstructing the missing outputs identified by the reviewer.
- Starting, stopping, restarting, updating, resetting, or repairing Docker
  Desktop, WSL, Hyper-V, a service, Windows, or the GPU.
- Preventing the owner or operating system from rebooting.
- Installing, copying, relocating, or updating PowerShell or Docker.
- Changing Docker Desktop auto-start configuration.
- Weakening the three-sample stability, boot-epoch, daemon, process, pipe,
  launcher, artifact, image, lease, historical, or GPU gates.
- Shell redirection or arbitrary file writes disguised as evidence capture.
- Retrying a failed sample, child, Docker command, or GPU query.
- New dependencies, model versions, thresholds, datasets, seeds, arms, splits,
  statistical rules, or protocol versions.
- Formal model runtime, Wave 1, push, merge, release, tag, or publication.

## Success criteria

This recovery is complete only when:

1. this design and its implementation plan are exact one-file commits with the
   required lineage and commit identity;
2. every consumed artifact remains byte-identical;
3. a fresh recorder and manifest pass all synthetic and static gates before
   external observation;
4. one unchanged host boot epoch and three exact stable Docker readiness samples
   produce DOCKER_READINESS_PASS;
5. every nontrivial command has a pre-execution manifest and complete
   machine-captured stdout/stderr/result evidence;
6. launcher revalidation and child self-attestation match exactly;
7. the one new entry child produces ENTRY_GATE_PASS, including one retained
   type-aware CUDA_IDLE / PASS observation and the inherited CPU baseline;
8. independent review approves both behavior and evidence completeness;
9. inherited Tasks 2 through 6 complete by TDD within the seven-path allowlist
   and produce exactly one implementation commit;
10. the single dependency-only diagnostic closes under the inherited
    formal-runtime-forbidden boundary; and
11. no host mutation, formal model runtime, Wave 1, push, merge, release, or
    unrelated repository change occurs.

An external prerequisite that is absent before child creation produces NOT_READY
and pauses without consuming the entry-child slot. Any NO_GO preserves its exact
evidence and stops for review. Neither outcome authorizes automatic repair,
tuning, fallback, or silent retry.

## References

- Microsoft Open Specifications, MS-ERREF NTSTATUS values:
  https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55
- Docker CLI documentation:
  https://docs.docker.com/reference/cli/docker/system/info/
- Docker Engine version command:
  https://docs.docker.com/reference/cli/docker/version/
- System.Diagnostics.Process:
  https://learn.microsoft.com/en-us/dotnet/api/system.diagnostics.process
