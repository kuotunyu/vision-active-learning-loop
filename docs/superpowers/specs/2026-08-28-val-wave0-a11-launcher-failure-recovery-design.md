# Wave 0 A11 Launcher Failure-Recovery Design

## Status and authority

This supplemental design is authorized by the owner on 2026-08-28 to repair the
checked-in A11 launcher after its first, single authorized runtime invocation
failed before calibration replicas. It refines implementation behavior only; it
does not amend the statistical-replay mathematics, receipt schemas, model stack,
historical evidence, or Wave 1 contract in
`docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`,
Section 5.2.15.

The failed run is immutable and must never be reused, completed, repaired in
place, or relaunched:

- run ID: `wave0-a11-calibration-20260828T045848083Z-b9917463`
- source: `2622e402e4f536b94326ac34f9b20c90b513002b`
- owner authorization: `OWNER-A11-RUNTIME-20260828-01`
- image: `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`
- terminal: `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`

This design authorizes a written implementation plan and a CPU-only/TDD code
repair. It does not authorize a Docker build, cache download, GPU lease, model
initialization, calibration replica, validation replica, RDD access, Wave 1,
remote operation, push, merge, tag, Release, or publication. A future runtime
attempt requires a new owner review and a new explicit authorization identifier.

## Observed failure evidence

The entry preflight, fresh image build, image inspection, cache preflight, lease
acquisition, and environment command completed. The environment subprocess
returned exit code 0, empty stdout, empty stderr, and atomically published a
schema-valid PASS receipt whose invariants were all true.

The launcher nevertheless threw `A11 stage failed: 30-environment` because
`Invoke-A11DockerStage` imposed one stream contract on three different commands:
it required stdout to equal `PASS\n`. The actual checked-in CLI contracts are:

| Stage | Success exit | Success stdout | Success stderr | Required receipt |
|---|---:|---|---|---|
| `environment check` | `0` | empty | empty | environment PASS receipt |
| `assets verify` | `0` | `PASS\n` | empty | model-assets PASS receipt |
| `probe model-contract` | `0` | `PASS\n` | empty | model-contract PASS receipt |

The earlier cache preflight retains its separate, exact `PASS\n`/empty-stderr
contract. Replica invocations retain their existing exact `PASS\n`/empty-stderr
contract. The recovery must not weaken either one.

After the false stage failure, the calibration lease was released and the final
historical rehash succeeded. The launcher published only
`79-historical-preservation-final.json`; it did not publish
`78-failure-diagnostic.json`, `80-campaign-result.json`,
`81-campaign-file-manifest.json`, or `82-campaign-closure.json`. The exception
after record 79 was swallowed by an empty `catch { }`, so no evidence supports a
more specific secondary error claim.

One additional orchestration defect was observed: `Invoke-A11CachePreflight`
emitted a value into the campaign pipeline. The top-level `$A11Result` therefore
became an array containing cache evidence and the terminal result, and strict
property access ended with `The property 'terminal' cannot be found on this
object.`

The failed run remains preserved with:

- 64,306 historical files and inventory SHA-256
  `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`
- 21 historical images and inventory SHA-256
  `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`
- final preservation record SHA-256
  `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`
- released lease SHA-256
  `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`
- release record SHA-256
  `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`

No calibration replica, checkpoint, calibration aggregate, validation root,
validation image, validation cache, or validation lease exists.

## Goals

The repair must:

1. enforce each foundation command's real, exact stream and receipt contract;
2. bind each successful foundation stage to a regular, non-link, phase-confined
   PASS receipt before the next stage begins;
3. keep cache-preflight and replica contracts unchanged;
4. guarantee that normal stage failures publish the complete 78–82 failure chain;
5. make any closure-publication failure explicit rather than swallowing it;
6. guarantee that the launcher entry point observes exactly one campaign result;
7. add tests that execute the production adapter and closure functions rather
   than replacing those functions wholesale; and
8. preserve every existing A11 and historical runtime object byte-for-byte.

## Non-goals

The repair does not change:

- the 12+12 cohort design, 66-pair inventories, 13 metrics, thresholds, ceilings,
  receipt schemas, or semantic validators;
- the pinned Dockerfile, dependencies, model/cache identities, GPU identity,
  warning contract, lease semantics, or phase ordering;
- any historical A2–A10 or failed A11 file/image;
- retry policy, partial-cohort rescue, threshold override, cleanup policy, or
  Wave 1 authorization; or
- any Python production module.

## Design

### 1. Command-specific foundation contracts

`Invoke-A11DockerStage` will receive an explicit expected stdout value and an
explicit expected receipt path. Empty stdout is a first-class exact value, not a
wildcard. Its contract is:

```text
exit code == 0
captured stdout string == registered expected stdout string
captured stderr string == empty
expected receipt exists as a regular non-link file below the phase root
receipt and every phase-relative ancestor have no reparse-point attribute
receipt metadata.run_id == phase run ID
receipt normative.status == PASS
receipt normative.errors == []
```

The stage audit will include the path, size, and SHA-256 of the verified receipt.
The function hashes and records the receipt before returning. The consuming call
site re-hashes the receipt immediately before use: `Invoke-A11Foundation` does
this for the environment and asset receipts passed to model-contract, and
`Invoke-A11Replica` does it for the model-contract receipt passed to every
replica. Unexpected stdout, a missing/linked/out-of-root receipt, a run mismatch,
non-PASS status, errors, or post-audit mutation fails closed.

`Invoke-A11Foundation` registers these exact expectations:

```text
30-environment   expected stdout: empty
31-model-assets  expected stdout: PASS\n
32-model-contract expected stdout: PASS\n
```

No `Trim()`, newline normalization, wildcard, truthy coercion, or alternate
success text is permitted.

### 2. Single-result pipeline discipline

Every orchestration helper that returns evidence for internal use is captured or
sent to `Out-Null` at its call site. `Invoke-A11Campaign` emits exactly one final
`PSCustomObject`.

The script entry point materializes campaign output as an array and requires its
count to equal one before reading `terminal`. Zero or multiple values fail with a
specific pipeline-cardinality error. This converts future output leakage into a
clear, testable launcher failure instead of a property-access accident.

### 3. Failure closure publication

`Close-A11Phase` first computes the complete historical file/image evidence and
the final error list in memory. Only after those values are available does it
publish, with `FileMode.CreateNew`, in this order:

```text
78-failure-diagnostic.json
79-historical-preservation-final.json
80-campaign-result.json
81-campaign-file-manifest.json
82-campaign-closure.json
```

The diagnostic records the first failed stage, complete known error list,
attempted success destination, source/specification/plan/image/authorization
identity, and normative-failure terminal. The result binds diagnostic and
preservation records. The manifest hashes every file that exists before manifest
publication. The closure binds the result and manifest.

The campaign catch must not use an empty catch. A closure-publication exception
is returned as an explicit `closure_error` with the normative-failure terminal and
is written to stderr by the entry point. It is never treated as a closed campaign,
never retried, and never followed by validation. Existing destinations are never
overwritten and a failed publication is not repaired in place.

Normal injected failures at initialize, build, cache, lease, foundation, replica,
gate, aggregate verification, release, and closure must each produce one terminal
result, release an acquired lease when possible, and never start a second
invocation.

### 4. Test architecture

The launcher test module will add focused harnesses that load the real production
function definitions from `scripts/run_wave0_a11.ps1` while replacing only native
process, filesystem-inventory, and Docker/GPU boundaries.

The mandatory RED/GREEN cases are:

1. environment exit 0 + empty stdout/stderr + PASS receipt succeeds;
2. environment stdout `PASS\n` fails as noncanonical;
3. assets/model-contract exit 0 + `PASS\n` + PASS receipt succeeds;
4. correct streams with a missing, linked, out-of-root, wrong-run, FAIL, errored,
   or mutated receipt fail;
5. cache-preflight and replica exact stream contracts remain unchanged;
6. a real `Close-A11Phase` normal failure publishes 78–82 and every hash binding
   recomputes;
7. an injected closure write failure is surfaced with `closure_error` and no
   retry;
8. cache evidence cannot leak into the campaign output pipeline; and
9. the entry point rejects zero or multiple result objects before terminal access.

All tests are CPU-only adapters. They must not call Docker, `nvidia-smi`, a GPU,
the external artifact root, or the preserved failed run.

## Tracked-file and commit boundaries

The design commit changes exactly this one file.

The future plan commit will add exactly:

```text
docs/superpowers/plans/2026-08-28-val-wave0-a11-launcher-failure-recovery.md
```

The implementation allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
```

A third tracked implementation path is a hard stop for owner review. The
implementation is one append-only commit, separate from the design and plan
commits, using:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, rebase, squash, history rewrite, push, merge, tag, Release, or
publication is permitted.

## Verification and stopping gate

Before the implementation commit, require:

- focused RED then GREEN evidence for every new regression test;
- the complete `tests/gates/test_wave0_a11_launcher.py` suite;
- the original A11 focused Python/receipt suites;
- the complete CPU test suite;
- targeted Black and Ruff for the changed Python test;
- `uv lock --check`;
- `git diff --check`;
- PowerShell 7 and Windows PowerShell 5.1 parser success;
- exact two-file implementation scope and empty staging before the final gate;
- both protected worktrees clean outside the candidate;
- the preserved failed run, released lease, 64,306 historical files, 21
  historical images, and their fixed hashes unchanged; and
- Critical=0 and Important=0 review against this design and Section 5.2.15.

After the implementation commit, stop and report the design, plan, and candidate
commits plus test/preservation evidence. Do not invoke the launcher. A future A11
runtime attempt remains owner-review-required and must use entirely new run,
image, cache, lease, container, receipt, checkpoint, timestamp, audit, and
authorization identities.
