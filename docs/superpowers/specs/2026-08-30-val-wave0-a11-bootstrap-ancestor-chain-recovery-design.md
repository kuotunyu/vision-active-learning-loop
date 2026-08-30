# Wave 0 A11 Bootstrap Ancestor-Chain Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `e91853594324565a8f31129060ac85e507c160a3`

## Purpose

Recover the synthetic evidence-host bootstrap from one preserved filesystem-
object type error without modifying or rerunning the failed attempt. The
recovery replaces property-coupled ancestor traversal with one path-string
algorithm, proves that algorithm against real `FileInfo` and `DirectoryInfo`
inputs before formal admission, and completes the full non-recursive synthetic
host proof under fresh `hostv5-*` identities.

The predecessor argv-materialization recovery passed exact entry, authored its
test before GREEN implementation, froze a canonical command brief, passed both
PowerShell parsers, and proved the JSON writer in an isolated microcheck. Its
only formal static invocation then failed during admission of the test file,
before parsing the command brief or starting the recorder RED. Its terminal is:

```text
BOOTSTRAP_ARGV_STATIC_REJECTED / NO_GO
```

This successor does not resume or repair that plan. It creates a fresh append-
only lineage, workspace, TDD contract, static source, command brief, recorder
RED, host namespace, manifests, and machine destinations. Complete success
remains evidence-host success only:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

## Preserved predecessor failure

The immediately consumed design and plan remain:

| Object | Commit |
|---|---|
| Bootstrap argv-materialization design | `b01372fcb147ac1d38ae2ad4ae45cf9f890e8152` |
| Bootstrap argv-materialization plan | `e91853594324565a8f31129060ac85e507c160a3` |

The consumed workspace is exactly:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/
```

It contains exactly five immutable files and no `machine/` directory:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `task-1-bootstrap-command-static-v4.ps1` | 12,532 | `e17d575e0ff8287ea7424c28c08b14bd7625e5603651b07f0283e4a5ced72a68` |
| `task-1-entry-gate-v4.ps1` | 5,562 | `8e35c0ab663116587448ecb6840bf6c6ecc876c367fe25f4fa86a3e2616b764d` |
| `task-1-evidence-module-red-v4.psm1` | 97 | `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb` |
| `task-1-evidence-tests-v4.ps1` | 8,824 | `aca02e4a213baa1703eec9c0a82a638240de46ecfb77cd0b944c3ab778f7a863` |
| `task-1-red-command-v4.json` | 1,461 | `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` |

The formal static process exited 1 with empty stdout. Its error identified
`Assert-A11StaticAbsoluteFile` and stated:

```text
The property 'Parent' cannot be found on this object.
```

The verifier had resolved the real test path and executed `Get-Item`, which
returned `System.IO.FileInfo`. Read-only inspection proved that object has a
`Directory` property and no `Parent` property. The verifier therefore failed on
its first file ancestor step. It did not parse the command brief, import the RED
module, execute the test, or create machine evidence.

The same defective sequence appears three times in the preserved v4 sources:
once in the formal static helper and twice in test-side file/source helpers.
Changing one occurrence would leave two latent failures. None may be edited or
executed by this recovery.

The v3 four-file and v2 three-file workspaces, their NO_GO terminals, and absent
machine directories remain immutable. The still earlier
`EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`,
four absent `preformal-003-recorder-red-verify` paths, artifacts, images,
inventories, digests, reports, leases, owner identities, and attempts also
remain immutable.

## Root cause and working pattern

The broken algorithm treated the result of `Get-Item` as though every filesystem
item exposed a common `.Parent` property:

```powershell
$Cursor = Get-Item -LiteralPath $Canonical -Force
while ($null -ne $Cursor) {
    # attribute checks
    $Cursor = $Cursor.Parent
}
```

`DirectoryInfo` exposes `.Parent`; `FileInfo` does not. The algorithm therefore
had an unstated directory-only type assumption even though its public contract
accepted files.

The repository already contains a successful type-agnostic pattern in preserved
recorder code. It keeps traversal state as a canonical path string, checks the
item at that string when it exists, and obtains the next ancestor with:

```powershell
$Parent = [IO.Directory]::GetParent($Cursor)
```

`Directory.GetParent(string)` accepts either a file-like or directory-like path
spelling and returns the containing directory without requiring a `FileInfo`
property. The algorithm then continues with `$Parent.FullName`. The same code
path handles a file, a directory, and a drive root.

An isolated diagnostic proved the v4 test input is `System.IO.FileInfo`, lacks
`Parent`, exposes `Directory`, and has a `System.IO.DirectoryInfo` containing
directory. No evidence implicates path spelling, command-brief bytes, JSON
canonicalization, PowerShell identity, or executable argv.

## Decision

Use a path-string ancestor walker and prove its real behavior before formal
static admission.

1. Every fresh absolute-path validator stores traversal state as a canonical
   string, not a filesystem object.
2. At each existing path, `Get-Item` is used only for kind, attributes, and link
   checks. The result is never asked for a parent.
3. The next path is always `[IO.Directory]::GetParent($Cursor).FullName`; a null
   parent terminates traversal.
4. The implementation checks the initial file or directory, every existing
   ancestor, and the drive root exactly once.
5. Before the production static source exists, one fresh behavioral test is
   authored and run against an intentional RED subject that reproduces the
   `FileInfo.Parent` failure.
6. The same immutable test then runs against the fresh production static source
   in `AncestorContract` mode with a real file and real directory. Only its exact
   GREEN result freezes that source and admits one `Formal` invocation.
7. Formal static PASS admits one fresh recorder RED. GREEN recorder/host work and
   eight `hostv5-*` captures follow only after the intended recorder RED.

## Alternatives considered

### A. Path string plus `Directory.GetParent` — selected

This has one data type and one traversal branch. It matches working repository
code, checks the target before walking, handles files and directories uniformly,
and does not depend on provider-added object properties. A real behavioral test
can exercise the exact production source before formal admission.

### B. Type-dispatch on `FileInfo` and `DirectoryInfo` — rejected

The first step could use `FileInfo.Directory`, while later directory steps use
`DirectoryInfo.Parent`. This directly fixes the observed error but retains two
object-property branches and requires explicit behavior for every other provider
object. It is more surface than the contract needs.

### C. Shared ancestor-validation module — rejected

A module would remove copied helper code, but the bootstrap must validate the
module path and its ancestors before importing that module. It recreates a
bootstrap dependency cycle and expands source/export/hash evidence.

## Authority and non-goals

This recovery may:

- create this one-file docs-only design commit and, after written-spec approval,
  one one-file docs-only implementation-plan commit;
- create one fresh ignored workspace using `apply_patch` for every human-
  authored test, RED subject, static source, command brief, recorder source,
  fixture, manifest, verifier, and report;
- run the frozen signed PowerShell executable for read-only entry, one ancestor
  contract RED, one ancestor contract GREEN, parser/static checks, one formal
  static invocation, one recorder RED, and the planned synthetic host commands;
  and
- create exactly 32 predetermined fresh machine files through the approved
  create-new recorder.

It may not:

- modify, execute, copy over, delete, rename, or retry any v4, v3, or v2 source,
  command, destination, or workspace;
- inspect or execute Docker CLI, Docker Desktop processes, pipes, WSL, Hyper-V,
  builders, images, containers, caches, or volumes;
- execute `nvidia-smi`, GPU/CUDA observation, CPU baseline, dependency stage,
  model, A11 launcher, entry child, formal runtime, Wave 1, or product Tasks 2-8;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- modify product code, the seven-file A11 implementation allowlist, external
  evidence, another repository, a remote, or Git history; or
- push, merge, tag, release, amend, rebase, reset, stash, or delete preserved
  evidence.

General owner trust does not broaden these boundaries. A later approved plan is
required before Docker, GPU, entry, product, or runtime activity.

## Append-only lineage and workspace

This design commit must change only this file and be a direct child of
`e91853594324565a8f31129060ac85e507c160a3`. Author and committer are exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

After written-spec approval, the implementation plan is a one-file direct child
of this design commit with the same identity.

Execution uses only this fresh path:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/
```

Before creating it, entry proves exact worktree topology, branch, design/plan
lineage, changed paths, blobs, author/committer, linked/canonical cleanliness,
fresh workspace absence, frozen PowerShell identity, v4 five-file inventory and
absent machine directory, v3 four-file inventory and absent machine directory,
v2 three-file inventory and absent machine directory, and the four still-absent
`preformal-003` paths.

All human-authored files use `apply_patch`. Once a process consumes a source,
test, brief, fixture, manifest, command ID, or destination, it is immutable. An
authoring defect before the ancestor RED start requires a new unused identity.
Any unexpected ancestor RED, ancestor GREEN, formal static, recorder RED, host,
or closure result closes the plan and cannot be corrected or retried.

## Path-string ancestor contract

The fresh helper accepts a canonical fully qualified Windows path. Before
walking, its caller rejects null, whitespace, wildcard, provider-qualified,
URI, UNC, device, ADS, relative, escaping, and trailing-ambiguous input. The
walker then performs:

```powershell
$Cursor = [IO.Path]::GetFullPath($CanonicalPath)
while ($true) {
    if (Test-Path -LiteralPath $Cursor) {
        $Item = Get-Item -LiteralPath $Cursor -Force
        if ($Item -isnot [IO.FileInfo] -and $Item -isnot [IO.DirectoryInfo]) {
            throw 'filesystem item type rejected'
        }
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            -not [string]::IsNullOrEmpty([string] $Item.LinkType)) {
            throw 'linked path rejected'
        }
    }
    $Parent = [IO.Directory]::GetParent($Cursor)
    if ($null -eq $Parent) { break }
    $Cursor = $Parent.FullName
}
```

Production code contains no `.Parent` access on a value returned directly by
`Get-Item`. `.Parent` may still appear in AST-parent traversal because that is a
PowerShell syntax-tree relationship, not a filesystem relationship. Static
verification distinguishes these domains by type and source location.

For existing input files, the caller separately requires `PathType Leaf`, exact
path equality, byte count, and SHA-256. For existing directories, it requires
`PathType Container` and exact path equality. For future create-new output paths,
the target must be absent while all existing ancestors pass the same walker.

## Ancestor-contract TDD

Create the behavioral test before either fresh subject. It accepts `Red` or
`Green`, a validated absolute subject path and identity, a real contract file,
a real contract directory, and the allowed root. It launches the subject through
frozen PowerShell with literal absolute arguments and captures stdout, stderr,
and exit independently.

The intentional RED subject has a distinct `v5-red` path and contains the exact
property-coupled break: it calls `Get-Item` on the real file and attempts to read
`.Parent` under strict mode. It catches only the resulting missing-property
exception and emits:

```text
EXPECTED_ANCESTOR_RED|fileinfo_parent_missing
```

with exit 43 and empty stderr. Any other result is
`ANCESTOR_CHAIN_UNPROVABLE / NO_GO`. The RED subject is never edited or used by
formal static admission.

After that exact RED, create the production static source at a different path.
It has an exact mode parameter:

```powershell
param(
    [Parameter(Mandatory)]
    [ValidateSet('AncestorContract', 'Formal')]
    [string] $Mode
)
```

`AncestorContract` mode runs the actual production helper against the real
contract file and directory, requires the first objects to be `FileInfo` and
`DirectoryInfo` respectively, proves both chains terminate at a drive root,
proves every observed existing item is ordinary/non-linked, writes nothing, and
emits only:

```text
ANCESTOR_CHAIN_CONTRACT_PASS|file=FileInfo|directory=DirectoryInfo|root=bounded
```

with exit 0 and empty stderr. The same immutable behavioral test must observe
that exact GREEN result. A mismatch is `ANCESTOR_CHAIN_UNPROVABLE / NO_GO`; do
not edit or rerun. Exact GREEN freezes the production static source identity.

The production source may enter `Formal` mode once only after contract GREEN.
Formal mode cannot call or simulate contract output and contract mode cannot
parse a command brief, import a module, create machine files, or start recorder
RED.

## Canonical command brief and formal static admission

After the contract GREEN freezes the static source, `apply_patch` creates a new
compact strict UTF-8 JSON command brief plus one LF. It records the frozen signed
PowerShell executable, repository working directory, and exact ordered argv for
the fresh recorder RED. All path values are canonical fully qualified Windows
paths in the v5 workspace.

The root properties remain exactly:

```text
schema_version
executable_path
executable_byte_count
executable_sha256
working_directory
argv
```

The formal static source reads the brief only in `Formal` mode. It independently
validates test, module, brief, workspace, and executable paths with the proven
path-string helper; parses the test and requires import only through the
validated absolute module value; rejects dynamic serializers; validates exact
brief schema/order/types/argv; and reconstructs canonical bytes with explicit
`Utf8JsonWriter` calls and `UnsafeRelaxedJsonEscaping`.

Formal static runs once. Its only PASS is:

```text
BOOTSTRAP_ANCESTOR_STATIC_PASS|ancestor=contract-proven|brief=canonical|absolute_args=4|validated_imports=1|dynamic_serializers=0|predecessor_args=0
```

Parameter-binding, path, identity, ancestor, parser, canonicalization, source-
flow, output, or exit difference publishes:

```text
BOOTSTRAP_ANCESTOR_STATIC_REJECTED / NO_GO
```

No retry, alternate argument, or source edit follows formal start.

## Recorder TDD and GREEN architecture

The v5 workspace receives a fresh recorder RED module and complete RED/GREEN
test before recorder GREEN source. The test uses the proven path-string walker
for its file and source validation. Its ancestor behavior is not a copy of an
untested algorithm: contract RED/GREEN has already exercised the same production
pattern before formal admission.

The new RED module has no recorder exports. Its only admitted result is:

```text
exit: 41
stdout: EXPECTED_RED|required export set missing
stderr: empty
machine files: zero
```

Any difference is `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`. The recorder RED runs
once.

After that RED, create a side-effect-free module exporting exactly:

```text
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

The module validates absolute/canonical/contained/ordinary identities, parses
closed canonical manifests, starts one child with
`ProcessStartInfo.ArgumentList`, concurrently captures stdout/stderr as raw
bytes, and publishes create-new result/digest files. The minimal leaf host
imports only the validated module path, invokes each export once, never captures
itself, never recurses, and never retries.

The trust layers remain:

1. frozen Layer 0 executable, contract-proven static source, canonical command
   brief, and formal static PASS;
2. statically constrained Layer 1 host/module; and
3. manifest-authorized Layer 2 child plus four authoritative machine files.

Outer output cannot repair incomplete Layer 2 evidence.

## Hostv5 manifests and synthetic set

Every GREEN manifest is compact strict UTF-8 JSON without BOM plus one LF. It
uses a closed ordered schema for command, host/module/executable/source
identities, argv, working directory, environment, stdin, timeout, child count,
and four output destinations. It rejects duplicates, extra/missing/reordered
properties, ambiguous paths, collisions, noncanonical bytes, and wrong source
vectors.

The new namespace is `hostv5-*`; it cannot reuse `hostv4-*`, `hostv3-*`,
`hostv2-*`, `preformal-*`, readiness, entry, CUDA, CPU, dependency, owner, or
runtime identities.

Execute exactly these distinct cases once each:

| Command | Proof |
|---|---|
| `hostv5-001-unit-green` | export, scope, AST, ancestor, path, manifest, invalid-input, and no-clobber behavior |
| `hostv5-002-raw` | exact NUL, UTF-8, non-ASCII, invalid-UTF-8, and no-terminal-newline bytes |
| `hostv5-003-high-volume` | concurrent one-megabyte stdout/stderr drain |
| `hostv5-004-argv` | spaces, quotes, empty string, and Unicode argument boundaries |
| `hostv5-005-nonzero` | exit 23 with complete streams/result |
| `hostv5-006-timeout` | one bounded tree kill with partial output |
| `hostv5-007-start-failure` | deterministic invalid executable and complete exception result |
| `hostv5-008-closure` | independent verification of 001-007 and frozen inventory |

Each command creates exactly `.stdout.bin`, `.stderr.bin`, `.result.json`, and
`.result.sha256` under the fresh `machine/` directory. Eight commands produce
exactly 32 create-new files. Each ID starts at most once; the first unexpected
state stops all later IDs.

## Static verification, terminals, and closure

Before `hostv5-001`, parse all complete sources under PowerShell 7.6.4 and
Windows PowerShell 5.1. AST/static verification requires:

- exact host parameters and three module exports;
- path-string ancestor traversal and no filesystem-object `.Parent` access;
- no dot-source, dynamic evaluation, `Start-Process`, shell string, redirection,
  top-level module side effect, or protected-variable assignment;
- validated absolute flows into module/file/parser/process APIs;
- create-new write sites limited to 32 scheduled destinations;
- no predecessor source/path/ID scheduled for execution; and
- no Docker, GPU, A11, product, Git mutation, network, or runtime command.

The first applicable terminal is one of:

```text
ANCESTOR_CHAIN_UNPROVABLE / NO_GO
BOOTSTRAP_ANCESTOR_STATIC_REJECTED / NO_GO
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

No exception is converted to PASS. Missing/partial output, unexpected console
text, wrong exit, timeout, start exception, digest difference, or inventory
mismatch is NO_GO unless it is the exact planned synthetic behavior. Sources
and outputs are never edited after observation.

An independent closure verifier is authored and frozen before the first host
child. It recomputes all source, ancestor-contract, command-brief, static,
manifest, raw stream, result, digest, terminal, and inventory facts and writes
nothing.

After commands 001-008 pass, one apply-patch report indexes lineage, all three
preserved bootstrap NO_GO workspaces, ancestor RED/GREEN evidence, command brief,
formal static, recorder RED, GREEN sources, eight manifests, all 32 machine
files, and prohibited-action non-occurrence. Final read-only closure verifies
the report and publishes the first exact success terminal.

Success does not authorize Docker readiness, GPU observation, A11 entry,
product Tasks 2-8, or runtime.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD and branch equal the required parent and branch;
2. linked and canonical worktrees were clean before authoring;
3. this design path and fresh execution workspace were absent;
4. v4 contains exactly five frozen files and no machine directory;
5. v3 contains exactly four frozen files and no machine directory;
6. v2 contains exactly three frozen files and no machine directory;
7. only this design path changed;
8. placeholder, conflict-marker, trailing-whitespace, and Markdown checks pass;
9. root cause, alternatives, ancestor contract, TDD, hostv5 IDs, terminals,
   authority, and closure are internally consistent;
10. commit parent, author, committer, subject, and changed path are exact; and
11. authoring executed no predecessor source, ancestor contract, formal static,
    recorder RED, host, Docker, GPU, entry, product, model, or runtime command.

After this one-file commit, stop for owner review of the written specification.
Invoke `writing-plans` only after explicit written-spec approval.

## Success criteria

This design succeeds when a later implementation proves against real objects
that filesystem ancestry is a path-string contract rather than a provider-
object property assumption, then completes the full non-recursive `hostv5-*`
synthetic evidence proof without changing predecessor evidence or crossing into
A11 runtime authority.
