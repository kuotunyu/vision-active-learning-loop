# Wave 0 A11 Bootstrap Path-Resolution Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `890466f71c6730e07774c4568c7b50f70db8ebe2`

## Purpose

Recover the non-recursive evidence-host bootstrap from one preserved path-
resolution failure, then complete the synthetic evidence-host proof without
expanding into Docker, GPU, A11 entry, product implementation, or runtime work.

The predecessor implementation plan reached its exact entry PASS, authored the
test before GREEN implementation, and started its one permitted Layer 0 RED
process. That process did not reach the intended missing-export assertion. It
failed while resolving the RED module path and closed as:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

This recovery creates a fresh append-only lineage, workspace, source set,
command namespace, manifests, and machine destinations. It never edits or
re-executes the predecessor test or RED module. It establishes an absolute-path
contract at every module, file, manifest, and child-process boundary before it
attempts a new RED.

If the new path gate and RED succeed, the same recovery continues through the
complete scope-isolated evidence module, minimal leaf host, static verification,
eight unique synthetic captures, and final closure. Success remains evidence-
host success only:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

## Preserved predecessor failure

The consumed plan and design remain:

| Object | Commit |
|---|---|
| Non-recursive evidence-host design | `4843cfe1579d9dc31f4994c6efa09f9de19fbdce` |
| Non-recursive evidence-host plan | `890466f71c6730e07774c4568c7b50f70db8ebe2` |

The consumed workspace is exactly:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/
```

It contains exactly three immutable files:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `task-1-entry-gate.ps1` | 3,541 | `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b` |
| `task-1-evidence-module-red.psm1` | 103 | `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc` |
| `task-1-evidence-tests.ps1` | 4,420 | `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65` |

The workspace has no `machine/` directory, GREEN module, evidence host,
manifest, synthetic fixture, closure verifier, or report. No Task 2-4 work from
that plan began.

The sole RED invocation used the frozen signed PowerShell executable and passed
this module argument:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-module-red.psm1
```

The test source then executed:

```powershell
Import-Module -Name $Path -Scope Local -Force -PassThru
```

The process exited 1 at that statement with the error that no valid module file
was found. It did not produce the required exit 41 or
`EXPECTED_RED|required export set missing`.

Read-only closure proved:

- the argument was not fully qualified;
- `Test-Path` from the repository root found the file;
- `Resolve-Path` produced the expected absolute file path;
- every consumed source hash remained exact;
- no machine evidence or GREEN source existed;
- linked and canonical worktrees remained clean; and
- all four older `preformal-003-recorder-red-verify` paths remained absent.

The root cause is therefore an interface mismatch, not a missing file: a
working-directory-relative string was passed directly to `Import-Module -Name`
instead of a validated absolute module path. The failed process is not eligible
for a new argument, replacement test, or retry under its plan.

The earlier restart-aware `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`,
`CUDA_OBSERVATION_UNPROVABLE / NO_GO`, all owner authorization identities,
artifacts, images, leases, preserved inventories, digests, reports, and attempts
also remain immutable.

## Decision

Use a defense-in-depth absolute-path contract and a fresh full synthetic
recovery.

1. The Layer 0 command is authored with literal absolute paths for its test,
   RED/GREEN module, host, fixtures, verifier, manifest, workspace, and working
   directory inputs.
2. Every receiving script rejects a non-fully-qualified input before module
   import, file read, manifest validation, process construction, or output
   creation.
3. Each input is canonicalized, contained, link-checked, identity-checked, and
   compared with its frozen expected path before use.
4. `Import-Module` receives only the validated absolute `.psm1` path.
5. The new RED has one new source identity and runs once. Only the intended
   missing-export failure admits GREEN authoring.
6. GREEN/static proof and eight unique `hostv3-*` captures follow only after the
   new RED passes.

This design deliberately does not add a path-resolution module. Such a module
would itself need a bootstrap import path and would move, rather than remove,
the trust boundary.

## Alternatives considered

### A. Absolute argv plus receiver validation — selected

Literal absolute argv prevents ambiguity at process creation. Independent
receiver validation prevents a future caller from silently reintroducing a
relative path. The two checks are small, testable, and do not add another
bootstrap dependency.

### B. Change only the outer argv — rejected

An absolute argument would make the immediate command work, but the test and
host interfaces would continue accepting working-directory-relative input. A
later controller could reproduce the same failure without violating their local
contracts.

### C. Add a reusable path-resolution module — rejected

A dedicated module would centralize normalization but must itself be located and
imported before the contract exists. It increases source, export, hashing, and
evidence surface for a boundary that .NET path APIs can enforce directly.

## Authority and non-goals

This recovery may:

- create one docs-only design commit and, after written-spec approval, one
  docs-only implementation-plan commit;
- create one fresh ignored workspace and human-authored source, test, fixture,
  manifest, verifier, and report files using `apply_patch`;
- run frozen signed PowerShell only for entry, parser/static checks, one new RED,
  and the planned synthetic evidence-host commands;
- create exactly the predetermined synthetic machine files through the approved
  create-new evidence module; and
- publish the first exact recovery terminal.

It may not:

- modify, delete, rename, append to, copy over, or re-execute a predecessor
  source, command ID, machine destination, or workspace;
- inspect or execute Docker CLI, Docker Desktop processes, named pipes, WSL,
  Hyper-V, builders, images, containers, caches, or volumes;
- execute `nvidia-smi`, GPU/CUDA observation, CPU baseline, dependency stage,
  model, A11 launcher, entry child, formal runtime, Wave 1, or Tasks 2-8;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- change product code, the seven-file A11 implementation allowlist, an external
  evidence directory, or another repository; or
- create a remote, push, merge, tag, release, amend, rebase, reset, or stash.

General owner trust does not broaden these boundaries. Any new authority or
external mutation requires separate explicit review.

## Append-only lineage and workspace

The design commit must be a one-file direct child of
`890466f71c6730e07774c4568c7b50f70db8ebe2`. It changes only this design path and
uses exact author and committer:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

After owner approval of the written specification, the implementation plan must
be a one-file direct child of the design commit with the same identity.

Execution uses this fresh path:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/
```

Before creating it, entry eligibility proves:

- exact linked-worktree topology and branch;
- exact design/plan lineage, changed paths, blobs, author, and committer;
- linked tracked, untracked, and staged scope clean;
- canonical worktree clean;
- fresh workspace absent;
- all three predecessor source identities exact;
- predecessor workspace contains exactly those three files and no machine path;
- the preceding RED process remains one consumed invocation;
- all four older `preformal-003` machine paths remain absent;
- all other directly consumed evidence identities exact; and
- no new Docker, GPU, entry, product, external, or runtime output.

All new human-authored files use `apply_patch`. Once an executed process consumes
a source, test, fixture, manifest, command ID, or destination, it is immutable.
An authoring defect found before the first new RED start requires a new
append-only source identity. Any defect after the RED starts closes the new plan
and cannot be repaired or retried.

## Absolute-path contract

### Layer 0 command construction

The implementation plan freezes every argv element before process creation. The
argv for test, module, host, manifest, fixture, verifier, workspace, and working
directory paths contains literal `D:\...` absolute paths. No path-bearing argv
element begins with `.`, `..`, a single slash, an environment-variable token,
or a home-directory token.

The command brief records exact argv order, UTF-16 PowerShell argument values,
working directory, environment allowlist, executable identity, source byte
counts, and SHA-256 values. A read-only static verifier compares the brief,
source literals, and planned command before the new RED process starts.

### Receiver validation

Every receiving script applies the same closed validation before use:

1. reject null, empty, whitespace, wildcard, provider-qualified, URI, UNC,
   device, ADS, or non-fully-qualified input;
2. call `[IO.Path]::GetFullPath` without using the current location to supply a
   missing root;
3. normalize separators to the Windows directory separator and reject a
   trailing-segment ambiguity;
4. compare canonical paths with `StringComparer.OrdinalIgnoreCase`, the Windows
   path equality contract;
5. use `[IO.Path]::GetRelativePath` against the exact allowed root and reject an
   absolute result, `..`, or an escaping first segment;
6. require the target and every existing parent ordinary and free of
   `ReparsePoint`;
7. require the expected file/directory type;
8. verify exact byte count and lowercase SHA-256 for files; and
9. pass only the validated canonical value to the next API.

Serialized manifests still contain one exact frozen backslash-form canonical
path. Case-insensitive Windows comparison does not permit a manifest to change
the frozen serialized spelling or source identity.

### API boundaries

The following APIs accept only validated absolute values:

- `Import-Module -Name` for RED and GREEN `.psm1` files;
- `Parser.ParseFile` for PowerShell source;
- `File.ReadAllBytes`, `FileStream`, and hash operations;
- `ProcessStartInfo.FileName` and `WorkingDirectory`;
- manifest path, command-source paths, and all four output destinations; and
- closure/report inventory readers.

The implementation contains no fallback `Resolve-Path` search, module-name
search, PATH search, current-directory concatenation, dot-source import, alternate
candidate, or retry with a different path.

## TDD bootstrap

The new workspace receives a new RED module and new complete RED/GREEN test
source. Neither file copies over, edits, or executes the predecessor source
identity.

Before GREEN implementation exists, the test names these breaks:

- non-fully-qualified module input must be rejected before import;
- a fully-qualified module path must remain inside the fresh workspace;
- canonical identity, bytes, and digest must match the frozen RED module;
- import must not mutate caller `LibraryOnly` or `$PID` state;
- the RED module must import successfully by absolute path; and
- the RED module must then fail only because the three approved recorder exports
  do not exist.

The formal RED command uses the literal absolute test and module paths. Its only
admitted result is:

```text
exit: 41
stdout: EXPECTED_RED|required export set missing
stderr: empty
machine files: zero
```

Any path error, import error, parser error, unexpected output, different exit,
or machine file publishes:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

The RED process runs once. It is not relaunched with a corrected argument.

## Non-recursive GREEN architecture

After the intended RED only, `apply_patch` creates a side-effect-free `.psm1`
and minimal leaf host at new paths. The module has no script-level parameters,
dot-source expression, top-level process/file/console action, caller-scope
mutation, dynamic evaluation, shell command string, or automatic-variable
assignment.

It exports exactly:

```text
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

The host imports the module by its validated absolute path in local module scope.
It validates one canonical manifest, starts exactly one permitted child, captures
stdout and stderr concurrently as raw bytes, and publishes one create-new result
and digest. The host never records itself and never recursively invokes another
host.

The explicit trust layers remain:

1. Layer 0 frozen signed PowerShell command and coordination metadata;
2. Layer 1 statically constrained evidence host/module; and
3. Layer 2 manifest-authorized recorded child and its four authoritative files.

If Layer 1 exits without a complete valid Layer 2 set, outer output cannot fill
the gap. The plan stops with `EVIDENCE_HOST_UNPROVABLE / NO_GO`.

## Manifest and machine evidence

Every manifest is compact strict UTF-8 JSON without BOM plus one terminal LF.
It has closed ordered fields for command identity, host/module/executable/source
paths and hashes, argv, working directory, environment, stdin, four destinations,
timeout, and permitted child count. All path fields satisfy the absolute-path
contract before child start.

The new namespace is `hostv3-*`. It cannot reuse any `preformal-*`, `hostv2-*`,
readiness, entry, CUDA, CPU, dependency, owner, or runtime identity.

Each command creates exactly:

```text
machine/hostv3-NNN-role.stdout.bin
machine/hostv3-NNN-role.stderr.bin
machine/hostv3-NNN-role.result.json
machine/hostv3-NNN-role.result.sha256
```

Destinations are absent, contained, ordinary-parented, unique, and opened with
create-new/no-clobber semantics. The recorder never deletes, truncates, appends,
moves, renames over, repairs, or reconstructs evidence.

## Synthetic execution set

After GREEN/static PASS, execute exactly eight planned host invocations:

| ID role | Proof |
|---|---|
| `hostv3-001-unit-green` | complete export, scope, AST, canonical manifest, invalid path, and no-clobber tests |
| `hostv3-002-raw` | exact NUL, UTF-8, non-ASCII, invalid-UTF-8, and no-terminal-newline bytes |
| `hostv3-003-high-volume` | concurrent one-megabyte stdout/stderr drain without deadlock |
| `hostv3-004-argv` | spaces, quotes, empty string, and Unicode retain exact argument boundaries |
| `hostv3-005-nonzero` | controlled exit 23 with complete raw streams and result |
| `hostv3-006-timeout` | one bounded kill with partial raw output and timeout result |
| `hostv3-007-start-failure` | deterministic invalid executable with complete start-exception result |
| `hostv3-008-closure` | independent verification of commands 001-007 and source/manifest inventory |

These are distinct frozen cases, not retries. Each ID starts at most once. The
first unexpected exit, timeout, start state, output, missing/extra file, digest,
path, or inventory mismatch closes the plan before the next ID.

## Static and behavioral gates

Before the new RED, static path verification requires:

- every path-bearing RED argv literal fully qualified;
- test source rejects non-absolute input before `Import-Module`;
- the one module import data flow receives the validated absolute variable;
- RED module/test identities exact; and
- no predecessor path, source, ID, or destination scheduled for execution.

Before the first GREEN child, parse every complete source under frozen
PowerShell 7.6.4 and Windows PowerShell 5.1. AST verification requires:

- no dot-source import, dynamic evaluation, `Start-Process`, or shell string;
- no assignment to `$PID` or another automatic/constant/read-only variable;
- no module top-level side effect or script parameter;
- host parameters and the three exports exact;
- all file/process/module APIs receive validated absolute paths;
- create-new write sites limited to the 32 scheduled machine files; and
- no Docker, GPU, launcher, artifact, repository mutation, network, or runtime
  command in executable sources or manifests.

Behavioral tests use literal hand-derived bytes, argv arrays, exit values, and
digests. They exercise real module/host behavior; no mock result can satisfy an
assertion. Linked-path rejection may use an injected attribute provider inside a
private validator, but production path/data flow and all file/process behavior
remain real.

## Terminals and continuation

The first applicable exact terminal is one of:

```text
BOOTSTRAP_PATH_STATIC_REJECTED / NO_GO
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

Success requires:

- exact entry and append-only lineage;
- static absolute-path PASS;
- one intended RED with exit 41;
- GREEN parsers, AST, imports, and behavioral suite PASS;
- exactly eight hostv3 invocations and 32 complete machine files;
- independent recomputation of every manifest/source/raw/result digest;
- exact report and final read-only closure;
- predecessor sources and absent machine paths unchanged;
- linked worktree clean except ignored fresh workspace;
- canonical worktree clean; and
- no prohibited external, product, or runtime action.

Success does not resume either predecessor plan, authorize Docker readiness,
consume an entry/GPU slot, or permit Tasks 2-8. A later approved plan must consume
the hostv3 PASS identities immutably before any complete A11 Task 1 entry gate.

Any NO_GO preserves the fresh workspace and stops for redesign. Explanation,
owner preference, or outer console output cannot repair missing evidence.

## Report and closure

The closure verifier is authored and frozen before the first hostv3 child. It
writes nothing and independently recomputes every source, manifest, raw stream,
result, digest, terminal, and expected inventory.

After commands 001-008 pass, `apply_patch` creates one report indexing:

- design/plan lineage and Git identities;
- predecessor NO_GO command, sources, hashes, and preservation proof;
- new static-path and RED evidence;
- GREEN source, parser, AST, and export identities;
- every manifest, argv, environment, timeout, and outer host result;
- all 32 machine paths, byte counts, SHA-256 values, result fields, and digests;
- final repository/workspace inventory; and
- explicit non-occurrence of every prohibited action.

A final read-only closure includes the report identity and publishes the first
exact terminal. The report indexes raw files; decoded text never substitutes for
raw bytes.

## Written-spec review and commit gates

Before committing this design, require:

1. HEAD and branch equal the required parent and branch;
2. linked and canonical worktrees were clean before authoring;
3. this design and fresh workspace paths were absent;
4. predecessor workspace contains exactly its three frozen files;
5. only this design path changed;
6. placeholder, conflict-marker, whitespace, and Markdown checks pass;
7. preserved facts, alternatives, path contract, TDD, hostv3 identities,
   terminals, scope, and continuation gates are internally consistent;
8. self-review finds no ambiguous path equality, retry, or authority rule;
9. commit parent, author, committer, subject, and changed path are exact; and
10. design authoring executed no PowerShell test, evidence host, Docker, GPU,
    entry, model, or runtime command.

After the commit, stop for owner review of the written specification. Invoke
`writing-plans` only after explicit written-spec approval.

## Success criteria

This design succeeds when a later implementation proves that path resolution is
an explicit admission contract, not an assumption inherited from a working
directory, and then completes the non-recursive synthetic evidence-host proof in
the same fresh fail-closed lineage.

It does not claim Docker readiness, CUDA idleness, CPU success, A11 entry,
product implementation, dependency success, or formal runtime success.
