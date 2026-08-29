# Wave 0 A11 CUDA-Gate Observability Recovery Design

**Status:** Approved architecture design; written-spec review pending

**Date:** 2026-08-30

**Branch:** `codex/wave0-model-contract`

**Parent commit:** `52fe25d529f7d64e986864576653d0d14a6e484b`

## Purpose

Recover the A11 ordering-semantics implementation path from an ambiguous
read-only entry-gate failure. The failed gate combined two materially different
conditions into the same terminal:

1. `nvidia-smi` returned a nonzero exit code; or
2. `nvidia-smi` returned one or more numeric CUDA compute-process IDs.

The preserved output contains only:

```text
CUDA process gate failed
```

This design does not reinterpret that failure, infer which condition occurred,
or declare the GPU idle after the fact. It introduces a plan-only observability
overlay so any fresh, separately approved entry gate records enough evidence to
classify the CUDA state without weakening the zero-compute-process rule.

## Authority and non-authority

The owner delegated the recovery decision and approved the recommended safety
boundary: observe and stop; never terminate a GPU process automatically.

This authority permits one append-only design document. It does not yet
authorize an implementation plan, implementation-file edit, CUDA query,
process termination, Docker command, artifact edit, diagnostic identity, GPU
lease, model initialization, launcher invocation, formal runtime attempt,
`OwnerAuthorizationId`, Wave 1 action, push, merge, release, tag, rebase,
reset, stash, or modification of another repository.

The next step after written-spec approval is a separate implementation plan.
Only that approved plan may authorize a fresh read-only entry gate.

## Frozen lineage and preserved failure

The recovery begins at:

```text
branch                               codex/wave0-model-contract
CUDA observability parent            52fe25d529f7d64e986864576653d0d14a6e484b
ordering-recovery design             68f51519d2cb480200ca4fef740651b0d15dd76f
ordering-recovery plan               52fe25d529f7d64e986864576653d0d14a6e484b
digest-recovery design               2db13d302da97a241daeaba3578cd9cec1c8073b
digest-recovery plan                 03115325f36da31b135b4593fb8df1689eac9a35
diagnostic-root erratum              101bb79369399cc3947f1c667f0a11988f916638
runtime-transport design             db047dcb8ad602fc4ac316a743ab4ddec3168cd5
runtime-transport plan               e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
approved A11 specification           b59b0d4407b98b460f6166ea7288ba6021dc7a78
original A11 plan                    7dbd3a7576ea76beccfc64f748c4e495259ea89b
```

The preserved Task 1 evidence is:

```text
Steps 1-4                 PASS
Step 5 external session   8631
Step 5 exit code          1
Step 5 output             CUDA process gate failed
Step 6                    not run
implementation edits      none
implementation commit     none
independent review        Critical 0 / Important 0 / Minor 0
```

The five preserved attempts, every frozen digest, all historical baselines,
and the artifact root remain immutable. In particular:

```text
D:\vision-active-learning-loop-artifacts\wave0
```

is read-only. The previous `NO_GO` remains authoritative evidence even if a
future observation reports an idle GPU.

## Approaches considered

### Selected: plan-only structured native-process observation

A new recovery plan will replace only the ambiguous CUDA command in the Task 1
entry gate with an in-memory native-process capture. The capture records argv,
timestamps, process-start status, exit code, stdout, stderr, numeric PIDs, and
bounded process metadata before applying the unchanged pass criterion.

This approach is selected because it repairs the evidence boundary before any
implementation edit. It preserves the existing seven-file implementation
allowlist and single-commit contract.

### Rejected: edit the launcher before the entry gate

Adding a reusable launcher helper first would modify an implementation path
before Task 1 passes. That would invert the approved gate order and make the
candidate source partly self-authorizing.

### Rejected: stop processes and rerun the old gate

Closing suspected applications and repeating the same opaque command would
tune the environment to the observed result without repairing its evidence.
It could produce a later PASS while leaving the preserved failure unexplained.

### Rejected: weaken the zero-process requirement

Ignoring selected process names, accepting graphics applications, or treating
query failure as idle would change the GPU isolation contract. This recovery
changes observability only; it does not introduce an allowlist or exception.

## Recovery architecture

### Unit A: append-only recovery lineage

This design is the direct child of the ordering-recovery plan commit. After the
written spec is approved, one new plan document must be its direct child. The
future implementation commit, if all entry and implementation gates pass,
must be the direct child of that new plan.

The design and plan commits each contain exactly one documentation path and use
the required author and committer identity:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No existing commit, plan, report, registry, artifact, or digest is amended.

### Unit B: structured CUDA observation

The recovery plan will define one local PowerShell helper for the gate runner.
It uses `System.Diagnostics.Process` with `UseShellExecute = false` and separate
stdout/stderr redirection. It starts exactly this native command once per CUDA
observation:

```text
nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits
```

The helper waits for that process to exit without timeout, sampling, polling,
or a replacement command. It returns an in-memory record containing:

```text
schema_version
observation_id
argv
started_utc
finished_utc
start_succeeded
exit_code
stdout_text
stderr_text
numeric_pids
numeric_pid_count
process_metadata
classification
terminal
```

`stdout_text` and `stderr_text` are the complete separately captured decoded
streams. The command emits only ASCII identifiers and decimal PIDs under the
required format; the plan must use explicit UTF-8 decoding and must not trim,
rewrite, sort, or discard either captured stream in the evidence record.

`numeric_pids` is derived only from complete stdout lines matching:

```text
^\s*[0-9]+\s*$
```

The parsed PID values preserve stdout line order. Duplicate numeric lines are
preserved and are not collapsed for the pass/fail decision.

### Unit C: bounded process metadata enrichment

When at least one numeric PID is observed, the runner performs a read-only CIM
lookup for those exact PIDs. For each observed PID it records only:

```text
pid
lookup_state
name
parent_pid
creation_time_utc
```

Command lines, environment variables, open handles, and file contents are not
captured. If a process exits between the CUDA observation and CIM lookup, its
record uses `lookup_state = exited_or_unavailable`. Missing metadata never
removes the original numeric PID and never converts a busy result into PASS.

The runner does not call `Stop-Process`, Task Manager automation, service
control, Docker stop, WSL shutdown, or any equivalent mutation.

### Unit D: closed classification

The result is classified with this exact precedence:

1. Native process cannot start:
   `CUDA_QUERY_START_FAILURE / NO_GO`.
2. Native process exits nonzero:
   `CUDA_QUERY_FAILURE / NO_GO`.
3. Native process exits zero and at least one numeric PID was observed:
   `CUDA_COMPUTE_BUSY / NO_GO`.
4. Native process exits zero and no numeric PID was observed:
   `CUDA_IDLE / PASS`.

No other classification is accepted. Non-numeric stdout and any stderr remain
in evidence but do not change the existing predicate: exit zero plus zero
numeric PID is PASS. This preserves rather than strengthens or weakens the
approved gate semantics.

### Unit E: evidence publication boundary

The complete structured observation is written only into the ignored
Subagent-Driven Development task report beneath:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery/
```

It is not written under the artifact root, the dependency-diagnostic root, an
A11 run directory, or a tracked implementation path. The report records a
SHA-256 of its canonical compact JSON observation as a transcription check;
the digest has no model, statistical, authorization, or runtime meaning.

The old Task 1 report remains unchanged. A future report links the prior
terminal by source commit and exact prior exit/output rather than copying it
into a new artifact envelope.

### Unit F: fresh full entry gate

After design and plan approval, the new plan starts a fresh Task 1 from its own
plan commit. It may not reuse the previous Steps 1-4 PASS result, cached hashes,
or prior native output.

The fresh gate repeats, in order:

1. lineage, identity, branch, worktree, staging, and `uv.lock` checks;
2. committed attempt-5 canonical-vector proof;
3. full version-aware rehash of all five preserved attempts;
4. exact frozen artifact and directory comparisons;
5. historical artifact/image, Docker, lease, container, validation-root, and
   diagnostic-absence checks;
6. the structured CUDA observation in place of the ambiguous pipeline;
7. the complete CPU baseline with bytecode and pytest caching disabled.

Any failure stops immediately. The CUDA observation is not run again within
the same gate. If it returns `NO_GO`, Tasks 2-7 remain forbidden.

Only a complete Task 1 PASS allows the unchanged implementation sequence to
begin.

## Data flow

```text
approved recovery plan commit
  -> fresh complete Task 1
  -> start one nvidia-smi compute query
  -> capture stdout + stderr + exit code
  -> parse numeric PID lines
  -> optionally enrich exact PIDs read-only
  -> apply closed classification
  -> publish ignored task-report evidence
  -> NO_GO: stop without implementation edit
  -> PASS: finish Task 1 baseline, then permit Tasks 2-7 in order
```

The previous failed observation never enters the new pass calculation. It is
lineage evidence only.

## Error handling and stopping rules

- Native start exceptions are captured as query-start failure; no fallback
  executable or alias is attempted.
- Nonzero exit is query failure regardless of stdout content.
- Any numeric PID is busy regardless of metadata lookup success.
- The runner never guesses the identity or owner of an observed process.
- The runner never kills, pauses, deprioritizes, or signals a process.
- The runner never retries the CUDA observation within the same gate.
- A process disappearing after observation does not retroactively change the
  recorded terminal.
- A later idle state does not rewrite or supersede the old `NO_GO`.
- Failure prevents the CPU baseline, implementation edits, Docker diagnostic,
  GPU lease, launcher, model initialization, and formal runtime.
- A tooling result without observable exit/output is preserved as
  `CUDA_OBSERVATION_UNPROVABLE / NO_GO`; it is never treated as PASS.

## TDD and verification design

The future plan must verify the observation logic before using it as a gate.
These are plan-defined, in-memory synthetic self-tests executed by the
read-only Task 1 runner before any external-state check. They exercise the
classifier, PID parser, metadata fallback, and evidence serializer without
editing a tracked test or implementation path. They must not invoke real
`nvidia-smi`, Docker, CUDA, the artifact root, or the network.

Required deterministic cases are:

1. start failure produces `CUDA_QUERY_START_FAILURE`;
2. exit nonzero preserves both streams and produces `CUDA_QUERY_FAILURE`;
3. exit zero with no numeric lines produces `CUDA_IDLE`;
4. exit zero with one numeric line produces `CUDA_COMPUTE_BUSY`;
5. multiple and duplicate numeric lines preserve source order;
6. non-numeric stdout is preserved but does not become a PID;
7. stderr on exit zero is preserved without changing the existing predicate;
8. a missing CIM row remains busy with `exited_or_unavailable` metadata;
9. no process-termination API or command appears in the recovery runner;
10. no fallback, retry loop, timeout, cached result, or second CUDA invocation
    appears in one entry gate.

The plan-defined PowerShell helper must parse under both PowerShell 7.6.4 and
Windows PowerShell 5.1 before its first native invocation. After Task 1 passes,
the normal tracked TDD sequence for the seven-file implementation resumes.
Those CPU tests set `PYTHONDONTWRITEBYTECODE=1` and use
`-p no:cacheprovider`.

Before any implementation commit, verification must also re-prove:

- exact design/plan ancestry and identity;
- clean linked and canonical worktrees and empty staging;
- byte-identical `uv.lock` at
  `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`;
- unchanged five attempt roots and frozen digests;
- unchanged historical artifact/image baselines;
- zero new A11 run, validation root, active lease, project container,
  diagnostic identity, receipt, checkpoint, owner record, or Wave 1 object;
- exact seven-file implementation allowlist and one implementation commit.

## File, commit, and runtime boundaries

This design commit changes exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-cuda-gate-observability-recovery-design.md
```

The subsequent plan commit changes exactly one new plan document. The future
implementation phase retains the existing seven-file allowlist:

```text
configs/a11/preserved-attempts.json
schemas/a11-preserved-attempts.schema.json
scripts/run_uv_sync_with_retries.py
scripts/run_wave0_a11.ps1
docker/wave0.Dockerfile
tests/gates/test_wave0_a11_launcher.py
tests/scripts/test_run_uv_sync_with_retries.py
```

No additional implementation path is authorized by this design. Tasks 2-5
remain uncommitted work; Task 6 may create exactly one seven-path
implementation commit only after all gates pass. Task 7 remains at most one
dependency-only Docker diagnostic outside the repository and artifact root.

This recovery does not authorize Tasks 7-8 of the original A11 runtime plan,
an `OwnerAuthorizationId`, a launcher runtime attempt, GPU/model campaign,
Wave 1, push, merge, tag, release, or changes to another repository.

## Success criteria

The recovery design is satisfied only when:

1. the preserved CUDA failure remains unchanged and explicitly ambiguous;
2. the fresh gate captures one complete, separately observable native result;
3. query failure and numeric-process occupancy have distinct terminals;
4. the acceptance predicate remains exit zero plus zero numeric PIDs;
5. no process or GPU state is mutated by observation;
6. all observation evidence is outside tracked implementation and artifact
   paths;
7. a fresh complete Task 1 either passes defensibly or stops with a precise,
   preserved `NO_GO`;
8. no implementation work begins before that complete PASS; and
9. all prior data-firewall, split, acquisition, preservation, diagnostic,
   single-commit, and runtime-authorization boundaries remain intact.
