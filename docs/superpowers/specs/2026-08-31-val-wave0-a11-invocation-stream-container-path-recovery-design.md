# Wave 0 A11 Invocation-Stream Container-Path Recovery Design and Written Specification

## Status and authority

This is a source-only recovery authorized by central coordination on
2026-08-31. It preserves the completed `steven006` calibration attempt as a
frozen `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN` result. It authorizes no
formal launcher invocation, Docker build, container start, GPU observation,
lease acquisition, model campaign, Wave 1, push, merge, release, remote
mutation, Docker restart, or WSL restart.

Frozen repository identity at entry:

- linked worktree:
  `<repo>\.worktrees\wave0-model-contract`;
- branch: `codex/wave0-model-contract`;
- recovery parent: `88c0722cb2f1e417587e9f488ba1ec897ad7c4a5`;
- original specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`;
- original plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`.

At entry, the frozen `steven006` calibration root contains 135 ordinary files
whose closure manifest rehashes without mismatch. The historical envelope
remains exactly 64,306 files with digest
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`, and
21 images with digest
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
There is no active A11 lease and the launcher process has exited. Docker's
Linux engine pipe is currently absent; this is a preserved runtime preflight
blocker and must not be repaired by this recovery.

## Preserved failure and traced root cause

The one authorized `steven006` launcher attempt produced all twelve
calibration replicas, then its aggregate gate ran in Linux and stopped with:

```text
invocation stdout path must be absolute
WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

The failed root is
`wave0-a11-calibration-20260831T051426556Z-b3e22466`. Its preserved closure
includes failure diagnostic SHA-256
`4e02f469b60497bc4d01cb78fec35e3aae7af4996d4e24c63d58b161368c61a3`, final
historical preservation SHA-256
`927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`, result
SHA-256 `830159cce1c4cbe06ab188cd365dc909ac1d5c267ec02137f6fbb0c3fcb8e`,
campaign manifest SHA-256
`6539f567f1f06a20c991ae0e55cafe8f012226a61facb4bb86508d1e7a439648`, and
closure SHA-256
`3c8d923f0e0bee2cd0fac2dbf0400011081e33817dd16cb8bad0aab9aa4a2d08`.
These artifacts are immutable evidence and are outside this recovery's
allowlist.

`Invoke-A11Replica` writes host-native records via `Get-A11FileRecord`. On
Windows its nested invocation-audit `stdout.path` and `stderr.path` therefore
contain `D:/vision-active-learning-loop-artifacts/...`. Later,
`New-A11PhaseManifest` translates only the *outer* `invocation_audit` record
to `/a11/<phase>/audit/<replica>-invocation.json`; it leaves the serialized
nested records unchanged. The Linux `statistical_replay` validator correctly
uses `Path(raw).is_absolute()` and then requires the stream records to resolve
under `/a11/<phase>`. Linux does not treat `D:/...` as an absolute path, so it
fails closed before reading the stream.

This is a Windows-producer to Linux-consumer serialization defect. It is not a
GPU, statistical threshold, receipt, model, or historical-inventory defect.

## Options considered

### A. Canonicalize nested stream records at the producer boundary

When `Invoke-A11Replica` creates its immutable invocation audit, convert each
host file record through the existing `ConvertTo-A11ContainerFileRecord`
function. The JSON then contains the real mounted names
`/a11/<phase>/audit/<replica>.stdout.log` and
`/a11/<phase>/audit/<replica>.stderr.log`, retaining the original byte sizes
and SHA-256 digests. This matches the already canonical container argv and the
validator's file-confinement rules.

### B. Accept Windows paths in the Linux validator

Rejected. It would weaken evidence confinement, depend on non-existent host
paths inside the container, and contradict the failed gate's correct behavior.

### C. Add a host path alongside the canonical record

Rejected. The audit schema is exact-keyed and a second path would be
non-normative diagnostic data that cannot help the Linux replay. No host path
is necessary for the proof.

## Decision and written specification

Use option A. A fresh future runner must serialize the invocation audit exactly
as follows for every calibration or validation replica:

```json
{
  "schema_version": 1,
  "argv": ["val", "probe", "training-feasibility", "..."],
  "exit_code": 0,
  "stdout": {
    "path": "/a11/<phase>/audit/<replica>.stdout.log",
    "size": 5,
    "sha256": "<lowercase sha256>"
  },
  "stderr": {
    "path": "/a11/<phase>/audit/<replica>.stderr.log",
    "size": 0,
    "sha256": "<lowercase sha256>"
  }
}
```

The two stream records must name the same mounted files that the launcher
writes under the campaign `audit` directory; their `size` and `sha256` values
are calculated from those files before serialization. They must be POSIX
absolute paths beneath the phase root. Windows drive-qualified paths, relative
paths, `..` escapes, extra fields, changed hashes, changed sizes, and streams
whose bytes are not exactly `PASS\n` and empty stderr remain failures. The
Python gate remains fail closed and gains a platform-independent unit contract
for Linux POSIX stream-path semantics; it must not be relaxed to accept host
paths.

## Scope, TDD, and verification

The implementation allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
src/vision_active_learning_loop/gates/statistical_replay.py
tests/gates/test_wave0_a11_launcher.py
tests/gates/test_statistical_replay.py
```

Docs are committed separately. The source change is intentionally limited to
the producer canonicalization and a fail-closed validator helper. TDD first
adds independent Windows-launcher serialization assertions and Linux
POSIX-semantic validator assertions, including a serialization/replay contract
and Windows-drive, relative, traversal, size/hash, and stream-byte mutations.
Those tests must fail before the production change and pass afterwards.

Required source-only verification is the focused launcher and statistical
replay suites, the original Task 6 CPU pytest set and full pytest suite, Black,
Ruff, `uv lock --check`, `git diff --check`, and parser checks in PowerShell 7
and Windows PowerShell. Tests must not start Docker, observe a GPU, create an
A11 artifact, lease a GPU, or write Python bytecode/cache artifacts.

Design and plan commits, then one implementation commit, use exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

## Stop boundary

After the source implementation and verification commit, stop at the fresh
runtime gate. Central coordination must separately provide a new source commit
and a new, unused `OwnerAuthorizationId`; neither `steven006` nor a synthesized
success receipt may be reused. If any frozen digest, closure record, test,
parser, scope, identity, or cleanliness check differs, preserve the evidence
and report NO_GO without retrying the formal attempt.
