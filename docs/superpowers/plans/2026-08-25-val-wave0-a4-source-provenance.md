# Wave 0 A4 Canonical Source Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the platform-specific raw PyTorch source hashes that stopped A3 with the owner-approved LF-normalized Python-source identity, preserve every retained A3 gate, and execute one fresh Wave 0 campaign without entering Wave 1.

**Architecture:** Keep the three-source inventory closed and continue verifying it before the backward callback. Canonicalize only Python newline bytes under the self-describing rule `python-source-lf-normalized-sha256-v1`, propagate that rule and the corrected digests through the feasibility receipt/schema/exact replay preimage, and change no model, dependency, runner, Dockerfile, or numerical threshold. Build one fresh source-bound image, prove the source contract in a CPU-only container before acquiring the GPU lease, then execute primary, clean-a, clean-b, and the aggregate gate once under a never-used run ID.

**Tech Stack:** Python 3.12.11; uv 0.8.15; pytest 9.0.2; JSON Schema; Black 22.6.0; Ruff 0.16.4; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; CUDA 12.6; Docker Desktop Linux engine; RTX 4090 24 GB; PowerShell 7.

## Global Constraints

- Authoritative specification: `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `977f2ade530c0ebd4ad8005510a29756b1605691`, especially Section 5.2.6.
- Entry branch is `codex/wave0-model-contract`; the linked worktree, branch, Git common directory, canonical main cleanliness, and Git identity must be exact before any edit. The implementation-entry HEAD must be the docs-only commit containing this plan, its first parent must be the approved spec commit `977f2ade530c0ebd4ad8005510a29756b1605691`, and its only changed path must be this plan.
- Exact implementation allowlist: `src/vision_active_learning_loop/probes/training_feasibility.py`, `src/vision_active_learning_loop/artifacts/receipts.py`, `schemas/feasibility-receipt.schema.json`, and `tests/probes/test_training_feasibility.py`. A fifth tracked implementation file is a hard stop.
- Preserve Python 3.12.11, uv 0.8.15, PyTorch 2.12.0+cu126, torchvision 0.27.0+cu126, Transformers 5.15.0, SciPy 1.18.0, pycocotools 2.0.10, CUDA 12.6, RT-DETR-R18 revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`, DINOv2-small revision `ed25f3a31f01632728cabb09d1542f84ab7b0056`, 300 queries, four RDD classes, BF16, full detector/backbone optimization, seed 17, all formal seeds/budgets, nine pilot fits, 66 primary fits, and six label-noise fits.
- Preserve the A3 warning identifier `grid_sampler_2d_backward_cuda`, exact warning count 9, `UserWarning` category, strict-mode restoration, exact/discrete replay fields, numerical bounds, VRAM limit, checkpoint round trip, atomic no-clobber publication, and all parent/path gates.
- `schemas/feasibility-receipt.schema.json` remains schema version 2 but its closed `allowlisted_backward` object requires the A4 rule and corrected digest mapping. No A3 feasibility-v2 receipt or checkpoint was published.
- No Dockerfile, runner, `uv.lock`, package pin, model config, dataset config, implementation plan from an older wave, or historical evidence may change.
- Preserve all previous campaigns and images, especially `wave0-a3-20260825T044614674Z` with terminal `WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN`. Never reuse its run ID, image tag, roots, receipts, checkpoints, or lease.
- `VAL_DATA_ROOT` remains unset. Do not read, mount, list, download, or otherwise access RDD. Wave 1, remote operations, push, merge, tag, Release, and GitHub publication are forbidden.
- Any RED failure with the wrong cause, unexpected file, test/lint/lock/review failure, source-contract failure, Docker/GPU identity failure, or Task 6 normative failure stops without broadening scope or retrying the failed campaign.

---

## File Map

| File | Responsibility in A4 |
|---|---|
| `src/vision_active_learning_loop/probes/training_feasibility.py` | Canonical newline hashing, exact source identity, link/junction rejection, `BackwardWarningEvidence.source_hash_rule`, and runtime/exact-comparison propagation |
| `src/vision_active_learning_loop/artifacts/receipts.py` | Independent semantic enforcement of the A4 rule and exact digest mapping |
| `schemas/feasibility-receipt.schema.json` | Closed structural requirement for `source_hash_rule` and the three corrected digests |
| `tests/probes/test_training_feasibility.py` | RED/GREEN proof for normalization, non-newline drift, link/junction rejection, receipt rule/mapping closure, and callback ordering |

No new implementation module, config manifest, schema version, CLI command, Docker stage, or runtime dependency is introduced.

---

### Task 1: Revalidate Identity and Immutable Baseline

**Files:**
- Read: Git metadata, approved spec, `uv.lock`, and preserved A3 evidence
- Modify: none

**Interfaces:**
- Consumes: the registered linked worktree and the docs-only plan commit whose first parent is approved spec commit `977f2ade530c0ebd4ad8005510a29756b1605691`
- Produces: exact entry identity and a pre-change hash inventory used by Tasks 3 and 4

- [ ] **Step 1: Verify the registered worktree identity**

Run from the linked worktree:

```powershell
$ExpectedSpecHead = '977f2ade530c0ebd4ad8005510a29756b1605691'
$PlanHead = git rev-parse HEAD
git worktree list --porcelain
git rev-parse HEAD
git rev-parse HEAD^
git diff-tree --no-commit-id --name-only -r HEAD
git branch --show-current
git rev-parse --git-dir
git rev-parse --git-common-dir
git status --porcelain=v1
git -C '<repo>' status --porcelain=v1
git config user.name
git config user.email
```

Require the exact linked path registered for branch `codex/wave0-model-contract`; `$PlanHead` must be the current docs-only plan commit, `HEAD^` must equal `$ExpectedSpecHead`, its only changed path must be `docs/superpowers/plans/2026-08-25-val-wave0-a4-source-provenance.md`, both worktrees must have empty status, and identity must be `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`. Do not checkout, reset, rebase, or repair a mismatch.

- [ ] **Step 2: Reconfirm the root-cause identities**

Run read-only checks:

```powershell
rg -n -C 4 'name = "torch"|torch-2\.12\.0|manylinux_2_28_x86_64' uv.lock
docker run --rm --network none --entrypoint sha256sum `
  vision-active-learning-loop:wave0-a3-fb9d0bb-20260825t044614674z `
  /opt/val/.venv/lib/python3.12/site-packages/torch/__init__.py `
  /opt/val/.venv/lib/python3.12/site-packages/torch/nn/functional.py
```

Require wheel SHA-256 `792711a06946fa1dcd1a86d46c387dd413744b9324262ff77c05f61830d0e678`, Linux `torch_init` SHA-256 `d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49`, and Linux `torch_nn_functional` SHA-256 `27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19`.

- [ ] **Step 3: Capture the protected baseline without modifying it**

Create a session-side inventory of:

```text
all files under D:\vision-active-learning-loop-artifacts\wave0 that predate the new A4 root
all existing vision-active-learning-loop:wave0-* image tag-to-ID pairs
uv.lock
docker/wave0.Dockerfile
scripts/run_wave0_clean.ps1
configs/models/pinned-models.yaml
the authoritative specification and every existing plan
```

Record absolute path, size, and SHA-256 for files. The eventual A4 campaign root is excluded by its exact never-used path, not by a wildcard.

**Stop condition:** Any identity, source digest, historical hash, worktree status, or author mismatch.

---

### Task 2: Implement the Canonical Source Contract With TDD

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `schemas/feasibility-receipt.schema.json`

**Interfaces:**
- Consumes: `Path`, `_is_link_or_junction(Path)`, `BackwardWarningEvidence`, `run_allowlisted_backward()`, `_allowlisted_backward_document()`, `atomic_write_receipt()`, and feasibility schema version 2
- Produces: `_canonical_python_source_sha256(path: Path) -> str`, `_A4_BACKWARD_SOURCE_HASH_RULE`, the corrected `_ALLOWLISTED_BACKWARD_SOURCE_SHA256`/validator mapping, and a required `BackwardWarningEvidence.source_hash_rule: str`

- [ ] **Step 1: Write the canonical-newline RED tests**

Add `import hashlib` and these behavior tests to `tests/probes/test_training_feasibility.py`:

```python
@pytest.mark.parametrize("newline", [b"\n", b"\r\n", b"\r"])
def test_canonical_python_source_hash_normalizes_only_newlines(
    tmp_path: Path, newline: bytes
) -> None:
    source = tmp_path / "source.py"
    source.write_bytes(b"alpha" + newline + b"beta" + newline)

    assert feasibility_probe._canonical_python_source_sha256(source) == hashlib.sha256(
        b"alpha\nbeta\n"
    ).hexdigest()


def test_canonical_python_source_hash_keeps_non_newline_bytes_visible(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.py"
    source.write_bytes(b"alpha\r\nbeta\r\n")
    expected = feasibility_probe._canonical_python_source_sha256(source)
    source.write_bytes(b"alpha\r\nBeta\r\n")

    assert feasibility_probe._canonical_python_source_sha256(source) != expected
```

Update the existing successful backward assertion to require:

```python
assert evidence.source_hash_rule == "python-source-lf-normalized-sha256-v1"
assert evidence.source_sha256 == {
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3",
}
```

Add a boundary test that monkeypatches `_allowlisted_backward_source_paths()` to three regular temporary files, monkeypatches `_is_link_or_junction()` to return true for one selected path, and proves `run_allowlisted_backward()` raises `FeasibilityError` before the callback is called:

```python
def test_allowlisted_backward_rejects_link_or_junction_before_callback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    paths = {
        name: tmp_path / f"{name}.py"
        for name in (
            "torch_init",
            "torch_nn_functional",
            "transformers_modeling_rt_detr",
        )
    }
    for path in paths.values():
        path.write_bytes(b"source\n")
    blocked = paths["torch_init"]
    callback_called = False

    monkeypatch.setattr(
        feasibility_probe, "_allowlisted_backward_source_paths", lambda: paths
    )
    monkeypatch.setattr(
        feasibility_probe, "_is_link_or_junction", lambda path: path == blocked
    )

    def callback() -> None:
        nonlocal callback_called
        callback_called = True

    with pytest.raises(
        feasibility_probe.FeasibilityError,
        match="bounded-backward source is not a regular file: torch_init",
    ):
        feasibility_probe.run_allowlisted_backward(callback)

    assert callback_called is False
```

- [ ] **Step 2: Write the receipt/schema RED tests**

Change `_warning_evidence()` to construct the desired A4 evidence, including:

```python
source_hash_rule="python-source-lf-normalized-sha256-v1",
source_sha256={
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3",
},
```

Extend the existing feasibility-evidence drift table with independent cases that:

```python
lambda n: n["allowlisted_backward"].pop("source_hash_rule")
lambda n: n["allowlisted_backward"].update({"source_hash_rule": "raw-file-sha256-v1"})
lambda n: n["allowlisted_backward"]["source_sha256"].update(
    {"torch_init": "b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9"}
)
```

Each mutation must be rejected by real schema/semantic receipt publication, not by a mock assertion.

- [ ] **Step 3: Run RED and inspect the causes**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'canonical_python_source_hash or allowlisted_backward or feasibility_evidence_drift'
```

Expected RED causes are the missing canonical helper/`source_hash_rule`, old Windows raw digests, the schema's closed-object rejection of the desired rule, and missing semantic enforcement. A collection error, unrelated fixture error, or different dependency failure is a hard stop.

- [ ] **Step 4: Implement the minimal source calculation**

In `src/vision_active_learning_loop/probes/training_feasibility.py`, define:

```python
_ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_ALLOWLISTED_BACKWARD_SOURCE_SHA256 = {
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": (
        "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
    ),
}


def _canonical_python_source_sha256(path: Path) -> str:
    raw = path.read_bytes()
    canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical).hexdigest()
```

In `_verify_allowlisted_backward_sources()`, retain the exact inventory check, replace the path gate with:

```python
if not path.is_file() or _is_link_or_junction(path):
    raise FeasibilityError(f"bounded-backward source is not a regular file: {name}")
```

and compute each digest with `_canonical_python_source_sha256(path)` instead of `sha256_file(path)`.

- [ ] **Step 5: Propagate the rule through runtime evidence**

Add `source_hash_rule: str` to `BackwardWarningEvidence`. Populate it in `run_allowlisted_backward()`, require it in `_allowlisted_backward_is_valid()`, and serialize it in `_allowlisted_backward_document()` before `source_sha256`. The exact-comparison preimage already embeds the complete serialized `allowlisted_backward` object; do not add a second parallel copy.

- [ ] **Step 6: Enforce the rule independently in receipt validation**

In `src/vision_active_learning_loop/artifacts/receipts.py`, replace the A3 source constants with:

```python
_A4_BACKWARD_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_A4_BACKWARD_SOURCE_SHA256 = {
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": (
        "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
    ),
}
```

Require both `allowlisted_backward["source_hash_rule"] == _A4_BACKWARD_SOURCE_HASH_RULE` and exact mapping equality in `_validate_feasibility_consistency()` and in the derived `allowlisted_backward_verified` invariant. Keep schema version 2 and every other A3 check unchanged.

- [ ] **Step 7: Close the feasibility schema**

In `schemas/feasibility-receipt.schema.json`:

```json
"required": [
  "operation_identifier", "expected_count", "observed_count", "raw_warnings",
  "warning_categories", "operation_identifiers", "source_hash_rule",
  "source_sha256", "strict_mode_restored"
]
```

Add:

```json
"source_hash_rule": {"const": "python-source-lf-normalized-sha256-v1"}
```

and replace only the two PyTorch constants in `source_sha256` with the A4 canonical digests. Retain `additionalProperties: false`, the Transformers digest, all warning constraints, and schema version 2.

- [ ] **Step 8: Update the old hash-drift monkeypatch**

The existing callback-order test currently monkeypatches `sha256_file`. Change it to monkeypatch `_canonical_python_source_sha256` to return `"0" * 64`; retain the assertion that the callback was never invoked.

- [ ] **Step 9: Run GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'canonical_python_source_hash or allowlisted_backward or feasibility_evidence_drift'
uv run pytest tests/probes/test_training_feasibility.py -q
```

Require zero failures. Confirm the first command exercises LF, CRLF, lone CR, non-newline mutation, wrong/missing rule, raw Windows digest, source drift before callback, and link/junction rejection.

**Stop condition:** Any test requires a fifth file, platform-specific allowlist, wildcard source acceptance, schema-version change, callback-before-verification, or weakening of an A3 gate.

---

### Task 3: Verify, Review, and Commit the A4 Candidate

**Files:**
- Verify: the exact four-file implementation allowlist
- Modify: none beyond corrections inside that allowlist required by a failed authorized gate

**Interfaces:**
- Consumes: Task 2 GREEN worktree
- Produces: one clean append-only source candidate commit

- [ ] **Step 1: Run the full CPU and quality gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests -q
uv run --with black==22.6.0 black --check `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/probes/test_training_feasibility.py
uv run --with ruff==0.16.4 ruff check `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/probes/test_training_feasibility.py
uv lock --check
git diff --check
```

Require zero failures. Capability skips must remain explained and must not cover an A4 behavior on the active platform.

- [ ] **Step 2: Perform a fresh second-pass review**

Review the complete diff without relying on implementation notes. Record Critical, Important, and Minor findings against Section 5.2.6. Critical and Important must both be zero. Explicitly inspect:

```text
normalization order: CRLF first, then lone CR
no decoding, BOM stripping, whitespace, tab, or Unicode normalization
regular-file plus symlink/junction rejection before callback
exact three-key inventory
exact A4 rule and digests in production, validator, schema, and tests
complete BackwardWarningEvidence and exact-comparison propagation
schema version remains 2 for the documented reason
all A3 warning, replay, checkpoint, VRAM, path, and no-clobber gates retained
```

Any correction repeats the affected focused test and the full gate set.

- [ ] **Step 3: Verify scope and historical preservation**

Require `git diff --name-only` to equal exactly:

```text
schemas/feasibility-receipt.schema.json
src/vision_active_learning_loop/artifacts/receipts.py
src/vision_active_learning_loop/probes/training_feasibility.py
tests/probes/test_training_feasibility.py
```

Rehash the complete Task 1 historical inventory and re-inspect all old image IDs. Require zero missing, changed, or extra-in-baseline entries. Verify `uv.lock`, Dockerfile, runner, pinned-model config, authoritative spec, plans, and all old campaigns are unchanged.

- [ ] **Step 4: Create one append-only implementation commit**

Stage only the four allowlisted files and commit with exact author and committer identity:

```powershell
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git add -- `
  schemas/feasibility-receipt.schema.json `
  src/vision_active_learning_loop/artifacts/receipts.py `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  tests/probes/test_training_feasibility.py
git diff --cached --check
git commit -m 'fix: canonicalize Wave 0 source hashes'
```

Do not amend, rebase, squash, reset, or rewrite any commit.

- [ ] **Step 5: Verify the committed candidate**

Repeat the focused tests, inspect exact author/committer, require only four files in the commit, and require both linked worktree and canonical main clean. The resulting HEAD is the sole A4 source candidate.

**Stop condition:** Any gate failure, unresolved Critical/Important finding, evidence drift, extra file, dirty worktree, or Git identity mismatch.

---

### Task 4: Execute One Fresh Wave 0 A4 Campaign

**Files:**
- Execute unchanged: `docker/wave0.Dockerfile`, `scripts/run_wave0_clean.ps1`, and current `val gate wave0`
- Write externally: a new no-clobber A4 campaign/audit/evidence root and one project GPU lease
- Modify in Git: none

**Interfaces:**
- Consumes: the sole clean A4 candidate SHA and a fresh source-bound OCI image
- Produces: either an immutable A4 failure campaign or a complete A4 Wave 0 aggregate PASS receipt

- [ ] **Step 1: Revalidate the execution boundary without redoing Tasks 1–3**

Require exact worktree/branch/candidate/clean identities; Docker context `desktop-linux`; Linux Server health; exact historical Option A image ID `sha256:558a468b2bcb1a96a9198fb35a1590e57c376e5a7e6ac5032b3cdff44bbaacc9`; one visible RTX 4090; no numeric compute workload; `VAL_DATA_ROOT` unset; no active project lease; no existing A4 run/campaign/attempt/checkpoint/gate roots; and unchanged historical evidence hashes.

- [ ] **Step 2: Create fresh identities and build once**

Generate a never-used UTC run ID of the form `wave0-a4-<UTC timestamp>`. Atomically create only its campaign/audit root after confirming nonexistence. Build one `--no-cache` image tagged with both the candidate SHA prefix and run ID, using OCI labels:

```text
org.opencontainers.image.revision=<full A4 candidate SHA>
org.opencontainers.image.ref.name=<new A4 run ID>
org.opencontainers.image.base.digest=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356
```

Inspect and record the immutable image ID, labels, repository digest, build log, and build result with atomic no-clobber audit files.

- [ ] **Step 3: Run the CPU-only source-contract micro-check before the lease**

Run without GPU, network, host mounts, or model forward:

```powershell
docker run --rm --network none `
  --entrypoint /opt/val/.venv/bin/python `
  <fresh-image-tag> -c `
  "import json; from vision_active_learning_loop.probes.training_feasibility import _ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE, _verify_allowlisted_backward_sources; print(json.dumps({'rule': _ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE, 'source_sha256': _verify_allowlisted_backward_sources()}, sort_keys=True))"
```

Require exact rule `python-source-lf-normalized-sha256-v1` and the three registered digests. Atomically preserve stdout, stderr, argv, exit code, image identity, and content hash. A failure stops before GPU lease acquisition.

- [ ] **Step 4: Acquire the GPU lease and execute attempts once**

After a fresh Docker GPU CSV collector confirms exactly one RTX 4090 and no competing numeric compute process, atomically create `D:\vision-active-learning-loop-artifacts\wave0\leases\<RUN_ID>` and a no-clobber acquisition record. Execute unchanged runner calls in this order:

```powershell
.\scripts\run_wave0_clean.ps1 -RunId <RUN_ID> -AttemptId primary `
  -ImageTag <IMAGE_TAG> -ImageDigest <IMAGE_ID> -HostArtifactRoot <CAMPAIGN_ROOT>
.\scripts\run_wave0_clean.ps1 -RunId <RUN_ID> -AttemptId clean-a `
  -ImageTag <IMAGE_TAG> -ImageDigest <IMAGE_ID> -HostArtifactRoot <CAMPAIGN_ROOT>
.\scripts\run_wave0_clean.ps1 -RunId <RUN_ID> -AttemptId clean-b `
  -ImageTag <IMAGE_TAG> -ImageDigest <IMAGE_ID> -HostArtifactRoot <CAMPAIGN_ROOT>
```

Each attempt must publish environment, model-assets, model-contract, feasibility-A, feasibility-B, and two checkpoints. Require exact A4 source rule/digests, nine warnings per feasibility receipt, finite scalar labeled loss, BF16 backward, finite gradients, parameter update, peak allocated VRAM at most 22 GiB, and verified checkpoint round trip.

- [ ] **Step 5: Run and validate the aggregate gate**

Create a fresh gate parent and run the current image with network disabled:

```text
val gate wave0 --run-id <RUN_ID> \
  --primary-root /artifacts/primary \
  --clean-a-root /artifacts/clean-a \
  --clean-b-root /artifacts/clean-b \
  --output /artifacts/gate/wave0-gate-receipt.json
```

Require six verified checkpoints, five comparisons to primary A, exact discrete/source identities, all registered gradient/update/AdamW numerical bounds, every aggregate invariant true, schema-valid stored receipt, and a recomputed receipt content hash.

- [ ] **Step 6: Close the campaign in all outcomes**

Release the lease by writing a no-clobber release record and moving the exact validated lease directory to `<RUN_ID>.released`; do not delete it. Rehash every Task 1 historical file, verify old image IDs, write a campaign closure manifest, and require both Git worktrees clean at the candidate SHA.

On the first normative failure, preserve evidence and stop at:

```text
WAVE0_A4_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

On complete success, stop at:

```text
WAVE0_A4_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED
```

Do not fix or retry a failed A4 campaign under this plan.

---

## Plan Self-Review Record

- [x] The plan maps every Section 5.2.6 requirement to an executable task and exact file.
- [x] The four-file implementation allowlist is closed; needing a fifth file is a hard stop.
- [x] The RED tests precede production edits and fail for the intended missing behavior.
- [x] The canonical rule normalizes only CRLF and lone CR bytes, in that order, without text decoding or other normalization.
- [x] Production, semantic validator, schema, tests, and exact replay use one exact rule and one exact three-digest mapping.
- [x] Schema version 2 is retained for the documented no-published-A3-receipt reason; old rule-less evidence cannot satisfy A4.
- [x] Source verification, link/junction rejection, and digest matching occur before the backward callback.
- [x] No model, package, Dockerfile, runner, dataset, seed, budget, fit count, warning gate, numerical bound, or research claim changes.
- [x] The fresh image source micro-check occurs before the GPU lease and model execution.
- [x] Every old campaign/image/evidence object remains immutable; each new path is fresh and no-clobber.
- [x] Task 6 permits one fresh campaign and no retry after a normative failure.
- [x] RDD access, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.
- [x] No unresolved marker, optional gate, ambiguous type/signature, or unspecified error boundary remains.

## Execution Selection

The owner delegated execution-method selection. Use **Inline Execution** in this existing registered worktree with the `superpowers:executing-plans` skill. Subagent execution is not used. Pause only at a hard stop or the terminal Wave 0 owner checkpoint.
