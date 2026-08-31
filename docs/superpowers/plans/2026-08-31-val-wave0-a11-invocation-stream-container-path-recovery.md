# Wave 0 A11 Invocation-Stream Container-Path Recovery Implementation Plan

> **For Codex:** Execute with the `executing-plans` skill. Central coordination authorized Inline Execution. Stop on a preserved NO_GO, a new external authorization, or a destructive action. Do not invoke the formal launcher.

**Goal:** Repair the Windows-host to Linux-container serialization boundary so every new A11 replica invocation audit records its stdout and stderr as the actual, confined POSIX container paths consumed by statistical replay.

**Architecture:** Canonicalize the two nested file records at the PowerShell producer boundary using the existing campaign-root conversion. Keep the Python validator fail closed and add a platform-independent POSIX confinement check that is activated for the Linux container validator. Existing preserved artifacts, receipts, and threshold mathematics are untouched.

**Tech stack:** PowerShell 7, Windows PowerShell 5.1 parser, Python 3.12, pytest, Black, Ruff, uv, and Git. Docker, WSL, GPU, and any model campaign are outside this plan.

## Frozen identities and scope

```text
RECOVERY_PARENT|88c0722cb2f1e417587e9f488ba1ec897ad7c4a5
DESIGN_COMMIT|d7f5e4020998ccf6daff4344b07406c995052519
SPECIFICATION_COMMIT|b59b0d4407b98b460f6166ea7288ba6021dc7a78
ORIGINAL_PLAN_COMMIT|7dbd3a7576ea76beccfc64f748c4e495259ea89b
PRESERVED_OWNER|steven006
PRESERVED_RUN|wave0-a11-calibration-20260831T051426556Z-b3e22466
PRESERVED_CLOSURE_FILES|135
PRESERVED_CAMPAIGN_MANIFEST|6539f567f1f06a20c991ae0e55cafe8f012226a61facb4bb86508d1e7a439648
HISTORICAL_FILE_INVENTORY|64306|e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
HISTORICAL_IMAGE_INVENTORY|21|9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
```

The implementation tracked-file allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
src/vision_active_learning_loop/gates/statistical_replay.py
tests/gates/test_wave0_a11_launcher.py
tests/gates/test_statistical_replay.py
```

Docs are committed separately. One and only one implementation commit is permitted after every gate passes, with this exact identity:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its subject is exactly:

```text
fix: canonicalize A11 invocation stream container paths
```

## Task 1: Re-enter source-only boundary and preserve the failed attempt

**Files:** read only.

1. Require this linked worktree, branch `codex/wave0-model-contract`, HEAD at the design commit, clean linked and canonical worktrees, and no staged changes.
2. Require the design commit to be a one-path direct child of the recovery parent, with the approved author, committer, subject, UTF-8/LF form, and no unresolved authorization or runtime instructions.
3. Rehash all 135 exact entries named by the preserved campaign closure; require the manifest digest and each recorded size/SHA-256 to match.
4. Recompute the 64,306-file and 21-image frozen inventories. Require no active lease and no launcher process. Record Docker engine unavailability if its Linux pipe is absent, but do not restart Docker or WSL.
5. Read `AGENTS.md` when present (none may be assumed), the original A11 plan, the design, this plan, the full launcher, statistical replay gate, and the relevant launcher/replay tests. Stop if the observed producer/consumer path flow differs from the traced cause.

## Task 2: Commit this implementation plan

**Files:**

- create and commit only `docs/superpowers/plans/2026-08-31-val-wave0-a11-invocation-stream-container-path-recovery.md`.

1. Check that this plan's design commit, frozen identities, allowlist, TDD order, parser checks, no-runtime boundary, and fresh-runtime stop are complete and consistent.
2. Require UTF-8 without BOM, LF-only line endings, one final LF, and `git diff --check` success.
3. Commit with the approved identity and exact subject:

```text
docs: plan A11 invocation stream container paths
```

4. Require the plan commit to be the sole changed path and a direct child of the design commit. Both worktrees must then be clean.

## Task 3: Add independent regression tests and prove RED

**Files:**

- modify `tests/gates/test_wave0_a11_launcher.py`;
- modify `tests/gates/test_statistical_replay.py`;
- read-only production files.

1. Extend the launcher adapter helper so a mocked Windows-host replica run can return the actual serialized invocation JSON, while still verifying the native Docker argv and stream bytes.
2. Add a launcher test that asserts both nested paths are exactly `/a11/calibration/audit/calibration-00.stdout.log` and `/a11/calibration/audit/calibration-00.stderr.log`; their hashes and sizes must equal the actual host-side audit files. The test must also assert no drive prefix reaches the serialized audit.
3. Add a Python unit contract for POSIX container path confinement. It must accept the serialized `/a11/<phase>/...` form and reject drive-qualified, relative, wrong-phase-root, and traversal forms. Keep existing byte/hash mutations of invocation streams as replay failures.
4. Run, without bytecode or pytest-cache creation:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py `
  tests/gates/test_statistical_replay.py -k 'invocation or container or malformed'
```

Expected RED: the new launcher path assertion observes a Windows `D:/...` record, and the new Python helper is absent. A fixture, import, shell, cache, or unrelated failure is invalid RED.

## Task 4: Implement canonical producer records and Linux fail-closed check

**Files:**

- modify `scripts/run_wave0_a11.ps1`;
- modify `src/vision_active_learning_loop/gates/statistical_replay.py`.

1. In `Invoke-A11Replica`, retain writing the two host files, but serialize their file records using `ConvertTo-A11ContainerFileRecord` before writing `<replica>-invocation.json`. Do not add a host-path field or alter its exact schema, stream byte contract, record digest, argv, or outer manifest logic.
2. Add a pure POSIX confinement helper in `statistical_replay.py`. It must require a nonempty POSIX-absolute path, require a POSIX-absolute phase root, reject `..`, and require the path to be beneath that root.
3. Add an optional container semantic root to file-record validation. Only the Linux invocation stdout/stderr validation supplies it. Existing generic checks continue to verify actual regular, non-link files, their sizes, and their SHA-256 digests. Windows paths and relative paths therefore cannot become valid Linux replay evidence.
4. Do not alter receipt schemas, output publication, thresholds, checkpoint loading, Docker argument construction, artifact inventory constants, preservation code, leases, retries, or runtime entry authorization.

## Task 5: Prove focused GREEN and source review

**Files:** all four implementation paths only.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py `
  tests/gates/test_statistical_replay.py
git diff --check -- scripts/run_wave0_a11.ps1 `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py `
  tests/gates/test_statistical_replay.py
```

Require launcher serialization, container semantic confinement, exact argv/stream, malformed, receipt, replay, cache, cross-phase, no-clobber, and no-retry tests to pass without Docker or GPU use. Review the diff against the design and ensure no change accepts `D:/`, relative, traversal, link, hash, or size substitutions.

## Task 6: Complete verification and make the single implementation commit

**Files:** stage and commit exactly the four allowlisted implementation paths only after all gates pass.

1. Run the original Task 6 CPU gates and full suite:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider
uvx --offline black --check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
uvx --offline ruff check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
```

2. Parse `scripts/run_wave0_a11.ps1` under both `pwsh` and `powershell`; both parser-error arrays must be empty.
3. Require the exact four-path uncommitted scope, no staging, no `.pyc`, no `__pycache__`, no pytest cache, and clean canonical worktree outside this worktree.
4. Rehash the preserved 135-file closure and the frozen historical/file-image inventories. A changed artifact, lease, project container, or Docker/WSL restart is a preserved NO_GO; do not repair it.
5. Perform fresh specification and code-quality review. Require Critical=0 and Important=0 before staging.
6. Stage exactly the four allowlisted paths, run `git diff --cached --check`, and create the single approved implementation commit.
7. Verify parentage to this plan, exact identity, exact four-path scope, clean worktrees, no runtime object creation, no active lease, and unchanged preserved evidence.

## Stop boundary

Report the source commit and all source gates, then stop at `CENTRAL_FRESH_ID REQUIRED`. A future runtime needs a separately approved new source commit and a new unused owner authorization. `steven006` is consumed and may not be reused; the current Docker-outage NO_GO may not be bypassed by restarting a service or replaying the preserved formal attempt.

