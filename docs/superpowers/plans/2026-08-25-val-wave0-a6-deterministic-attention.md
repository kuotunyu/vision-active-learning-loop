# Wave 0 A6 Deterministic Attention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not dispatch subagents unless the owner explicitly requests them.

**Goal:** Keep RT-DETR on the approved Transformers SDPA interface while forcing the complete labeled forward-through-backward region onto deterministic Math-only SDPA, bind that execution identity into schema-v3 feasibility receipts and exact replay, and execute one fresh full Wave 0 campaign without entering Wave 1.

**Architecture:** Add one source-bound deterministic-attention evidence type and one fail-closed helper around the existing labeled forward and bounded backward. The helper verifies the pinned Python sources, approved `sdpa` configuration, strict deterministic mode, and exact pre/inside/post backend maps; `torch.nn.attention.sdpa_kernel(SDPBackend.MATH)` encloses the labeled autocast forward, scalar finite-loss validation, bounded backward, and warning validation. Propagate the complete evidence through `StepObservation`, feasibility schema v3, the independent receipt validator, and the exact replay preimage while preserving every A2-A5 model, warning, checkpoint, numerical, no-clobber, and research gate.

**Tech Stack:** Python 3.12.11; uv 0.8.15; pytest 9.0.2; JSON Schema 2020-12; Black 22.6.0; Ruff 0.16.4; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; SciPy 1.18.0; pycocotools 2.0.10; CUDA 12.6; Docker Desktop Linux engine; RTX 4090 24 GB; PowerShell 7.

## Global Constraints

- The owner statement on 2026-08-25 approving continuation after commit `1f9f4256a38ba69f4746cb08e48afb7cb804980e` is the written approval of the A6 specification. The authoritative specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at that commit, especially Section 5.2.8.
- Entry branch is `codex/wave0-model-contract`. Implementation may begin only when HEAD is the docs-only commit containing this plan, its first parent is `1f9f4256a38ba69f4746cb08e48afb7cb804980e`, and its only changed path is `docs/superpowers/plans/2026-08-25-val-wave0-a6-deterministic-attention.md`.
- Exact implementation allowlist: `src/vision_active_learning_loop/probes/training_feasibility.py`, `src/vision_active_learning_loop/artifacts/receipts.py`, `schemas/feasibility-receipt.schema.json`, and `tests/probes/test_training_feasibility.py`. Needing a fifth tracked implementation file is a hard stop for another written spec/plan review.
- Preserve `model.config._attn_implementation == "sdpa"`. Do not select `eager`, Flash, Memory Efficient, cuDNN attention, a private ATen flag, an autograd hook, a custom CUDA kernel, split backward, CPU fallback, model freeze, or a dependency change.
- The exact public backend state is `{"cudnn": true, "flash": true, "math": true, "memory_efficient": true}` before and after the bounded region and `{"cudnn": false, "flash": false, "math": true, "memory_efficient": false}` inside it.
- The bounded region begins before BF16 CUDA autocast and ends only after `run_allowlisted_backward()` completes warning validation. Gradient inspection, clipping, AdamW/scheduler update, timing finalization, checkpoint capture, and receipt construction remain outside the Math-only context.
- Preserve the exact A3/A4 warning contract: nine ordered `UserWarning` values parsed to `grid_sampler_2d_backward_cuda`, strict deterministic error mode restored, source rule `python-source-lf-normalized-sha256-v1`, and the existing three-source A4 mapping. The A5 Memory Efficient and Flash warnings remain rejected; warning count 11 never passes.
- Add a separate closed deterministic-attention source mapping without changing the A4 mapping: `torch_nn_attention=56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0` and `transformers_sdpa_attention=d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098`, using the same LF-normalized hash rule.
- Every new feasibility receipt is schema version 3. `normative.deterministic_attention` is required and closed; the exact object is included in the replay preimage. A schema-v2 feasibility receipt is historical only and cannot satisfy A6.
- Preserve Python/package/CUDA versions, RT-DETR-R18 revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`, DINOv2-small revision `ed25f3a31f01632728cabb09d1542f84ab7b0056`, processor, 300 queries, four RDD classes, BF16, full detector/backbone optimization, seed 17, formal seeds/budgets, nine pilot fits, 66 primary fits, six label-noise fits, 22 GiB peak allocated VRAM ceiling, checkpoint round trip, exact/numerical replay thresholds, and all research claims.
- Preserve atomic no-clobber publication and fresh checkpoint roots/destinations. No existing run ID, image tag, campaign, attempt, checkpoint, receipt, audit path, or lease may be deleted, overwritten, cleaned, merged, or reused.
- Preserve A5 campaign `wave0-a5-20260825T084331001Z`, source `979aa63893971ba979f030fdda52a4fa5746f520`, image `sha256:6e334236b7db5af654d8fd90c80a2febf4bf4e164fff39cd0c854e954421786a`, all files and hashes, and terminal `WAVE0_A5_DIAGNOSTIC_CAPTURED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN` without retry or reinterpretation.
- `VAL_DATA_ROOT` remains unset. Do not read, list, mount, download, or access RDD. Wave 1, remote operations, push, merge, tag, Release, and GitHub publication are forbidden.
- Whole-tree formatting debt remains out of scope. Only touched Python files receive targeted Black/Ruff. Author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`; do not amend, rebase, reset, squash, or rewrite history.

---

## File Map

| File | Responsibility in A6 |
|---|---|
| `src/vision_active_learning_loop/probes/training_feasibility.py` | Verify deterministic-attention source/config/backend identity; bound Math-only SDPA over labeled forward-through-backward; restore state; add evidence to observation, receipt, and exact replay |
| `src/vision_active_learning_loop/artifacts/receipts.py` | Allow feasibility schema v3 and independently enforce the exact deterministic-attention object, invariants, warning identity, and replay binding |
| `schemas/feasibility-receipt.schema.json` | Require schema version 3, the closed deterministic-attention object, four A6 booleans, and deterministic-attention replay evidence |
| `tests/probes/test_training_feasibility.py` | Provide RED/GREEN proof of ordering, exact states, source/config gates, restoration/error behavior, warning rejection, schema closure, semantic validation, and replay identity |

No new module, CLI option, runner parameter, Dockerfile, config, dependency, Wave 0 gate schema, dataset path, or research artifact is introduced.

---

### Task 1: Revalidate Entry Identity and Freeze the Historical Baseline

**Files:**
- Read: Git metadata, approved A6 spec/plan lineage, current four-file implementation surface, and preserved A5 evidence
- Modify: none
- Write outside Git: one never-used pre-change baseline manifest using atomic `CreateNew`

**Interfaces:**
- Consumes: registered linked worktree and the docs-only A6 plan commit
- Produces: exact entry identities plus artifact, image, and protected-Git inventories used by Tasks 4 and 6

- [ ] **Step 1: Verify the registered worktree and docs-only lineage**

Run from the worktree discovered through `git worktree list --porcelain`, not a hand-written path:

```powershell
$ErrorActionPreference = 'Stop'
$ExpectedBranch = 'codex/wave0-model-contract'
$ExpectedSpecHead = '1f9f4256a38ba69f4746cb08e48afb7cb804980e'
$PlanPath = 'docs/superpowers/plans/2026-08-25-val-wave0-a6-deterministic-attention.md'
$PlanHead = (git rev-parse HEAD).Trim()
$PlanParent = (git rev-parse HEAD^).Trim()
$Branch = (git branch --show-current).Trim()
$GitDir = (git rev-parse --path-format=absolute --git-dir).Trim()
$CommonDir = (git rev-parse --path-format=absolute --git-common-dir).Trim()
$Files = @(git diff-tree --no-commit-id --name-only -r HEAD)
$WorktreeStatus = @(git status --porcelain=v1)
$CanonicalStatus = @(git -C '<repo>' status --porcelain=v1)
git worktree list --porcelain
git show -s --format=fuller HEAD
if ($Branch -ne $ExpectedBranch) { throw 'A6 branch mismatch' }
if ($PlanParent -ne $ExpectedSpecHead) { throw 'A6 plan parent mismatch' }
if ($GitDir -eq $CommonDir) { throw 'A6 is not in the registered linked worktree' }
if ($Files.Count -ne 1 -or $Files[0] -ne $PlanPath) { throw 'A6 plan commit is not docs-only' }
if ($WorktreeStatus.Count -ne 0 -or $CanonicalStatus.Count -ne 0) { throw 'Git state is not clean' }
```

Require the commit author and committer to equal the approved identity. Do not checkout, reset, rebase, or repair any mismatch.

- [ ] **Step 2: Rehash the exact A5 trigger evidence**

```powershell
$A5Root = 'D:\vision-active-learning-loop-artifacts\wave0\a5-runs\wave0-a5-20260825T084331001Z'
$A5Expected = [ordered]@{
    'audit\32-warning-contract-diagnostic.json' = '058bc2c87341a7d1783a0b9a189d9f1920f2ebd1a83c1a5c1152288805484055'
    'audit\40-campaign-result.json' = 'cc60eadec2ce11ca5168cc56e1dd39645f3b9751390fc3f8db9bc90bfd287796'
    'audit\41-campaign-file-manifest.json' = '402a78520a830923376aecdec61aa07743cdc8c2c68c8b2e7690392fac703ee5'
    'audit\50-historical-preservation.json' = '01a28a84240a34dd7c56a0e7bbd9f1045adf08f2f64affbc717899543060d7f6'
    'audit\51-campaign-closure-manifest.json' = 'e8fa4f6ab33989db79af7f06e0d6d99d3e4c30b00c9955a3bcf18c0a8b00bace'
    'primary\audit\04-feasibility-a.log' = 'b3e42a878f7a3c1611b96501b874871bb4fded5a1e50fdd38f7e24c9a8a43363'
    'primary\audit\04-feasibility-a.json' = 'e203bcb02efe8ea88badfca2aab454fa6ee45bd5aca4349eeff4c115318127bb'
    'primary\wave0\receipts\environment.json' = 'af8470e6d513ce0a696e2101b49360ad527b8fa62688706a96b458a230bb35c8'
    'primary\wave0\receipts\model-assets.json' = 'f10a93b59806d32c993cee03395a8e7c61f7fc3559a98885b3839cea606e204e'
    'primary\wave0\receipts\model-contract.json' = '2f9d935b44f374ad5ca901bfd4050131be5493c07b18f8fdeed8bef2e4532f81'
}
foreach ($RelativePath in $A5Expected.Keys) {
    $Path = Join-Path $A5Root $RelativePath
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $A5Expected[$RelativePath]) { throw "A5 evidence drift: $RelativePath" }
}
```

Decode `audit\32-warning-contract-diagnostic.json` and require exactly 11 ordered `UserWarning` entries, nine grid-sample messages, the Memory Efficient message at index 3, the Flash message at index 10, `feasibility_receipt == null`, no checkpoints, and the permanent A5 terminal.

- [ ] **Step 3: Create a no-clobber pre-change inventory**

Set a never-used manifest path keyed by `$PlanHead`. Inventory every file already under `D:\vision-active-learning-loop-artifacts\wave0`, every existing `vision-active-learning-loop:wave0-*` tag-to-image-ID pair, and every tracked Git path except the exact four future implementation files. The approved spec and this plan are protected inputs and must be included.

Do not exclude any historical artifact by wildcard. Build the three inventories and write canonical JSON with `FileMode.CreateNew`:

```powershell
$BaselinePath = Join-Path $env:TEMP "val-a6-baseline-$PlanHead.json"
if (Test-Path -LiteralPath $BaselinePath) { throw 'A6 baseline destination exists' }
$ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$ArtifactInventory = @(
    Get-ChildItem -LiteralPath $ArtifactRoot -Recurse -File |
        Sort-Object FullName |
        ForEach-Object {
            [ordered]@{
                path = $_.FullName.Substring($ArtifactRoot.Length + 1).Replace('\', '/')
                size = $_.Length
                sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()
            }
        }
)
$ImageInventory = @(
    docker image ls --no-trunc --format '{{.Repository}}:{{.Tag}}|{{.ID}}' |
        Where-Object { $_ -like 'vision-active-learning-loop:wave0-*|*' } |
        Sort-Object |
        ForEach-Object {
            $Parts = $_ -split '\|', 2
            [ordered]@{ tag = $Parts[0]; image_id = $Parts[1] }
        }
)
$AllowedTracked = @(
    'src/vision_active_learning_loop/probes/training_feasibility.py',
    'src/vision_active_learning_loop/artifacts/receipts.py',
    'schemas/feasibility-receipt.schema.json',
    'tests/probes/test_training_feasibility.py'
)
$ProtectedGitInventory = @(
    git ls-files |
        Where-Object { $_ -notin $AllowedTracked } |
        Sort-Object |
        ForEach-Object {
            [ordered]@{
                path = $_
                size = (Get-Item -LiteralPath $_).Length
                sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $_).Hash.ToLowerInvariant()
            }
        }
)
$Payload = [ordered]@{
    schema_version = 1
    plan_head = $PlanHead
    artifact_files = $ArtifactInventory
    images = $ImageInventory
    protected_git = $ProtectedGitInventory
}
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes(
    (($Payload | ConvertTo-Json -Depth 20 -Compress) + "`n")
)
$Stream = [IO.File]::Open($BaselinePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try { $Stream.Write($Bytes, 0, $Bytes.Length); $Stream.Flush($true) } finally { $Stream.Dispose() }
```

**Stop condition:** identity mismatch, dirty state, missing/drifted A5 evidence, active project lease/container, or inability to create an exact baseline.

---

### Task 2: Implement the Math-Only Labeled Boundary With TDD

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`

**Interfaces:**
- Consumes: existing `configure_determinism()`, `run_allowlisted_backward()`, and `run_one_step_smoke()`
- Produces: `DeterministicAttentionEvidence`, `_verify_deterministic_attention_sources()`, `_sdpa_backend_state()`, `_deterministic_attention_is_valid()`, `run_math_only_labeled_forward_backward()`, and an A6-enriched `StepObservation`

The exact new evidence type is:

```python
@dataclass(frozen=True)
class DeterministicAttentionEvidence:
    attn_implementation: str
    backend: str
    scope: str
    before: Mapping[str, bool]
    inside: Mapping[str, bool]
    after: Mapping[str, bool]
    restored: bool
    source_hash_rule: str
    source_sha256: Mapping[str, str]
```

The function signature is exactly `run_math_only_labeled_forward_backward(model: object, labeled_forward: Callable[[], tuple[torch.Tensor, bool]], *, expected_warning_count: int) -> tuple[torch.Tensor, bool, BackwardWarningEvidence, DeterministicAttentionEvidence]`; Step 5 supplies its complete control flow.

- [ ] **Step 1: Add RED tests for source, config, entry, and context order**

Add fixtures for the exact maps and hashes:

```python
A6_BEFORE = {"cudnn": True, "flash": True, "math": True, "memory_efficient": True}
A6_INSIDE = {"cudnn": False, "flash": False, "math": True, "memory_efficient": False}
A6_SOURCE_SHA256 = {
    "torch_nn_attention": "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0",
    "transformers_sdpa_attention": "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098",
}
```

Write tests named:

```text
test_a6_source_verification_precedes_labeled_callback
test_a6_source_inventory_rejects_missing_extra_renamed_wrong_path_or_hash
test_a6_source_inventory_rejects_non_utf8_nonregular_link_or_junction
test_a6_requires_sdpa_and_exact_entry_backend_state
test_a6_math_only_context_covers_forward_and_allowlisted_backward
test_a6_rejects_inside_backend_state_before_forward
```

The context-coverage test patches only source verification and bounded-backward execution, not the backend accessors or `sdpa_kernel`:

```python
def test_a6_math_only_context_covers_forward_and_allowlisted_backward(monkeypatch):
    configure_determinism(17)
    seen: dict[str, dict[str, bool]] = {}
    model = SimpleNamespace(config=SimpleNamespace(_attn_implementation="sdpa"))
    monkeypatch.setattr(
        feasibility_probe,
        "_verify_deterministic_attention_sources",
        lambda: dict(A6_SOURCE_SHA256),
    )

    def labeled_forward() -> tuple[torch.Tensor, bool]:
        seen["forward"] = feasibility_probe._sdpa_backend_state()
        return torch.tensor(1.0, requires_grad=True), True

    def bounded_backward(callback, *, expected_count):
        assert expected_count == 9
        seen["backward"] = feasibility_probe._sdpa_backend_state()
        callback()
        return _warning_evidence()

    monkeypatch.setattr(feasibility_probe, "run_allowlisted_backward", bounded_backward)
    loss, autocast_seen, warnings_seen, attention = (
        feasibility_probe.run_math_only_labeled_forward_backward(
            model, labeled_forward, expected_warning_count=9
        )
    )
    assert loss.item() == 1.0
    assert autocast_seen is True
    assert warnings_seen == _warning_evidence()
    assert seen == {"forward": A6_INSIDE, "backward": A6_INSIDE}
    assert attention.before == A6_BEFORE
    assert attention.inside == A6_INSIDE
    assert attention.after == A6_BEFORE
    assert attention.restored is True
    assert feasibility_probe._sdpa_backend_state() == A6_BEFORE
```

- [ ] **Step 2: Add RED restoration and warning-retention tests**

Parametrize failures from labeled forward, invalid/non-finite scalar loss, bounded backward, warning validation, and a synthetic bounded-backward failure that leaves deterministic mode in warn state. Every case must assert exact backend restoration and no returned evidence. Cases whose backend and strict mode restore normally preserve the original exception type/message; the synthetic strict-mode leak and any post-backend drift require `FeasibilityError("deterministic attention backend restoration mismatch")` with the body exception as `__cause__`. Add `test_a6_cli_restoration_failure_writes_no_receipt_or_checkpoint`, following the existing CLI fixture boundary, and require exit code 2, the restoration error on stderr without traceback, absent feasibility destination, and absent checkpoint root.

Add the complete A5 Memory Efficient and Flash messages as literal test constants:

```python
A5_MEMORY_EFFICIENT_WARNING = (
    "Memory Efficient attention defaults to a non-deterministic algorithm. "
    "To explicitly enable determinism call torch.use_deterministic_algorithms("
    "True, warn_only=False). (Triggered internally at /pytorch/aten/src/ATen/"
    "native/transformers/cuda/attention_backward.cu:900.)"
)
A5_FLASH_WARNING = (
    "Flash Attention defaults to a non-deterministic algorithm. To explicitly "
    "enable determinism call torch.use_deterministic_algorithms(True, "
    "warn_only=False). (Triggered internally at /pytorch/aten/src/ATen/native/"
    "transformers/cuda/attention_backward.cu:124.)"
)
```

Feed each into the real `run_allowlisted_backward()` inventory path and require reason `unparsable_message`; do not add them to `_DETERMINISTIC_WARNING_PATTERN`. Retain the existing nine-warning success test unchanged.

- [ ] **Step 3: Run RED and verify the causes**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'a6 or math_only or fused_attention'
```

Expected RED: missing `DeterministicAttentionEvidence`, `_sdpa_backend_state`, source verifier, and Math-only helper. No pre-existing A3/A4/A5 test may fail. A RED caused by local GPU absence, model download, or an unrelated fixture is not acceptable.

- [ ] **Step 4: Implement exact source and backend observation**

Import the public modules/APIs only:

```python
import transformers
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers.integrations import sdpa_attention as transformers_sdpa_attention
```

Define exact constants and accessors:

```python
_DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_DETERMINISTIC_ATTENTION_SOURCE_SHA256 = {
    "torch_nn_attention": "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0",
    "transformers_sdpa_attention": "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098",
}
_DETERMINISTIC_ATTENTION_BEFORE = {
    "cudnn": True,
    "flash": True,
    "math": True,
    "memory_efficient": True,
}
_DETERMINISTIC_ATTENTION_INSIDE = {
    "cudnn": False,
    "flash": False,
    "math": True,
    "memory_efficient": False,
}


def _sdpa_backend_state() -> dict[str, bool]:
    return {
        "cudnn": bool(torch.backends.cuda.cudnn_sdp_enabled()),
        "flash": bool(torch.backends.cuda.flash_sdp_enabled()),
        "math": bool(torch.backends.cuda.math_sdp_enabled()),
        "memory_efficient": bool(torch.backends.cuda.mem_efficient_sdp_enabled()),
    }
```

Resolve `torch_nn_attention` only through `inspect.getsourcefile(torch.nn.attention)` and `transformers_sdpa_attention` only through `inspect.getsourcefile(transformers_sdpa_attention)`. For each source, require an ordinary file inside its installed `torch` or `transformers` package root; use `_path_has_link()` so a linked parent also fails. Validate and hash the same bytes exactly:

```python
raw = path.read_bytes()
try:
    raw.decode("utf-8")
except UnicodeDecodeError as error:
    raise FeasibilityError(
        f"deterministic-attention source is not UTF-8: {name}"
    ) from error
canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
digest = hashlib.sha256(canonical).hexdigest()
```

Missing, extra, renamed, wrong-path, wrong-hash, non-UTF-8, non-regular, symlink, or junction input fails before any labeled callback.

- [ ] **Step 5: Implement the fail-closed Math-only helper**

The helper must follow this control shape:

```python
def run_math_only_labeled_forward_backward(
    model: object,
    labeled_forward: Callable[[], tuple[torch.Tensor, bool]],
    *,
    expected_warning_count: int,
) -> tuple[
    torch.Tensor,
    bool,
    BackwardWarningEvidence,
    DeterministicAttentionEvidence,
]:
    if not callable(labeled_forward):
        raise FeasibilityError("labeled forward must be callable")
    if type(expected_warning_count) is not int or expected_warning_count <= 0:
        raise FeasibilityError("expected backward warning count must be positive")
    source_sha256 = _verify_deterministic_attention_sources()
    config = getattr(model, "config", None)
    if getattr(config, "_attn_implementation", None) != "sdpa":
        raise FeasibilityError("deterministic attention requires sdpa")
    if (
        not torch.are_deterministic_algorithms_enabled()
        or torch.is_deterministic_algorithms_warn_only_enabled()
        or torch.get_deterministic_debug_mode() != 2
    ):
        raise FeasibilityError("strict deterministic error mode is required")
    before = _sdpa_backend_state()
    if before != _DETERMINISTIC_ATTENTION_BEFORE:
        raise FeasibilityError("deterministic attention entry backend mismatch")

    body_error: BaseException | None = None
    result = None
    try:
        with sdpa_kernel(SDPBackend.MATH):
            inside = _sdpa_backend_state()
            if inside != _DETERMINISTIC_ATTENTION_INSIDE:
                raise FeasibilityError("deterministic attention inside backend mismatch")
            loss, autocast_observed = labeled_forward()
            if not isinstance(loss, torch.Tensor) or loss.numel() != 1:
                raise FeasibilityError("model did not return a scalar training loss")
            if not bool(torch.isfinite(loss.detach()).all()):
                raise FeasibilityError("non-finite loss")
            warning_evidence = run_allowlisted_backward(
                loss.backward, expected_count=expected_warning_count
            )
            result = (loss, autocast_observed, warning_evidence, inside)
    except BaseException as error:
        body_error = error

    after = _sdpa_backend_state()
    strict_restored = (
        torch.are_deterministic_algorithms_enabled()
        and not torch.is_deterministic_algorithms_warn_only_enabled()
        and torch.get_deterministic_debug_mode() == 2
    )
    if after != before or not strict_restored:
        restoration = FeasibilityError(
            "deterministic attention backend restoration mismatch"
        )
        if body_error is not None:
            raise restoration from body_error
        raise restoration
    if body_error is not None:
        raise body_error.with_traceback(body_error.__traceback__)
    assert result is not None
    loss, autocast_observed, warning_evidence, inside = result
    evidence = DeterministicAttentionEvidence(
        attn_implementation="sdpa",
        backend="MATH",
        scope="labeled_forward_through_backward",
        before=before,
        inside=inside,
        after=after,
        restored=True,
        source_hash_rule=_DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE,
        source_sha256=source_sha256,
    )
    return loss, autocast_observed, warning_evidence, evidence
```

Do not catch and convert the original body error unless restoration itself fails. Never mutate backend flags outside `sdpa_kernel`.

- [ ] **Step 6: Integrate only the labeled forward/backward region**

In `run_one_step_smoke()`, define `labeled_forward()` so its first state-changing operation is entering `torch.autocast(device_type="cuda", dtype=torch.bfloat16)`, then invoke the model and return `(loss, autocast_observed)`. Call the new helper before gradient inspection. Store its evidence on `StepObservation` and add the evidence validation to `evaluate_step_observation()`.

Use one exact production predicate:

```python
def _deterministic_attention_is_valid(
    evidence: DeterministicAttentionEvidence,
) -> bool:
    return (
        evidence.attn_implementation == "sdpa"
        and evidence.backend == "MATH"
        and evidence.scope == "labeled_forward_through_backward"
        and dict(evidence.before) == _DETERMINISTIC_ATTENTION_BEFORE
        and dict(evidence.inside) == _DETERMINISTIC_ATTENTION_INSIDE
        and dict(evidence.after) == _DETERMINISTIC_ATTENTION_BEFORE
        and evidence.restored is True
        and evidence.source_hash_rule
        == _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE
        and dict(evidence.source_sha256)
        == _DETERMINISTIC_ATTENTION_SOURCE_SHA256
    )
```

`evaluate_step_observation()` raises `FeasibilityError("deterministic attention evidence mismatch")` when this predicate is false.

When constructing `StepObservation`, pass the already-validated existing field:

```python
semantic_input_digests={
    str(name): str(value) for name, value in semantic_input_digests.items()
},
```

This is not a new gate; it preserves the existing exact replay input once A6 advances beyond the previously failing backward boundary. Optimizer construction, gradient inspection/clipping, parameter update, timing, state capture, and checkpoint work remain outside Math-only SDPA.

- [ ] **Step 7: Run GREEN for the runtime boundary**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'a6 or math_only or allowlisted_backward or deterministic or warning_diagnostic'
```

Require zero failures and explicit coverage of source-before-callback, exact config, exact before/inside/after states, forward and backward scope, all restoration paths, unchanged nine-warning acceptance, and both fused-warning rejections.

**Stop condition:** private API use, backend normalization of a wrong entry state, model execution in a CPU unit test, altered warning parser/count, missing restoration path, or need for another tracked file.

---

### Task 3: Bind A6 Evidence Into Schema v3 and Exact Replay With TDD

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `schemas/feasibility-receipt.schema.json`

**Interfaces:**
- Consumes: Task 2 `DeterministicAttentionEvidence` and current feasibility-v2 receipt/replay structures
- Produces: `_deterministic_attention_document()`, schema-v3 feasibility receipts, independent semantic validation, and exact replay binding

The exact normative object is:

```json
{
  "attn_implementation": "sdpa",
  "backend": "MATH",
  "scope": "labeled_forward_through_backward",
  "before": {"cudnn": true, "flash": true, "math": true, "memory_efficient": true},
  "inside": {"cudnn": false, "flash": false, "math": true, "memory_efficient": false},
  "after": {"cudnn": true, "flash": true, "math": true, "memory_efficient": true},
  "restored": true,
  "source_hash_rule": "python-source-lf-normalized-sha256-v1",
  "source_sha256": {
    "torch_nn_attention": "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0",
    "transformers_sdpa_attention": "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098"
  }
}
```

- [ ] **Step 1: Convert receipt fixtures to the A6 RED contract**

Update `_observation()` to include exact deterministic-attention evidence and update `_receipt()` to request schema version 3 plus the object above. Add these four invariant names with `True` values:

```text
deterministic_attention_math_only
deterministic_attention_scope_verified
deterministic_attention_source_verified
deterministic_attention_backend_restored
```

Require `exact_comparison["deterministic_attention"]` to equal the normative object and require its digest to change for every one-field mutation.

- [ ] **Step 2: Add schema and semantic-validator RED cases**

Parametrize one mutation per exact field: missing/extra/renamed object key; `attn_implementation="eager"`; backend `FLASH_ATTENTION`; altered scope; every Boolean in each state map; missing/extra backend key; `restored=false`; wrong rule; missing/extra/renamed source key; each wrong digest; schema version 2; missing/extra invariant; a false invariant; missing or changed exact-replay copy; and a rehashed altered replay preimage.

Use two assertions for each mutation:

```python
with pytest.raises(ReceiptValidationError):
    validate_receipt(receipt, schema_path)

receipt["metadata"]["receipt_content_sha256"] = _receipt_content_sha256(receipt)
with pytest.raises(ReceiptValidationError):
    _validate_feasibility_consistency(
        receipt["normative"],
        receipt["metadata"],
        schema_version=receipt["schema_version"],
    )
```

Use the already imported production `_receipt_content_sha256()` helper exactly as shown so structural and semantic failures are not masked by a stale content hash.

- [ ] **Step 3: Run schema/receipt RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'a6_receipt or deterministic_attention or schema_version'
```

Expected RED: schema still requires version 2, the validator rejects version 3 as unallowlisted, and production omits the A6 object/invariants/replay field. Existing failure must not be hidden by a malformed test receipt.

- [ ] **Step 4: Propagate one canonical production document**

Add:

```python
def _deterministic_attention_document(
    evidence: DeterministicAttentionEvidence,
) -> dict[str, object]:
    return {
        "attn_implementation": evidence.attn_implementation,
        "backend": evidence.backend,
        "scope": evidence.scope,
        "before": dict(evidence.before),
        "inside": dict(evidence.inside),
        "after": dict(evidence.after),
        "restored": evidence.restored,
        "source_hash_rule": evidence.source_hash_rule,
        "source_sha256": dict(sorted(evidence.source_sha256.items())),
    }
```

Use that document in `exact_comparison()` and `_build_receipt()`. Set feasibility `schema_version` to 3. Derive the four booleans exactly as follows; do not hard-code success:

```python
attention = observation.deterministic_attention
"deterministic_attention_math_only": (
    attention.attn_implementation == "sdpa"
    and attention.backend == "MATH"
    and dict(attention.inside) == _DETERMINISTIC_ATTENTION_INSIDE
),
"deterministic_attention_scope_verified": (
    attention.scope == "labeled_forward_through_backward"
),
"deterministic_attention_source_verified": (
    attention.source_hash_rule == _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE
    and dict(attention.source_sha256)
    == _DETERMINISTIC_ATTENTION_SOURCE_SHA256
),
"deterministic_attention_backend_restored": (
    dict(attention.before) == _DETERMINISTIC_ATTENTION_BEFORE
    and dict(attention.after) == dict(attention.before)
    and attention.restored is True
),
```

Do not alter the exact replay rule string or exclude the new object from its preimage.

- [ ] **Step 5: Close the JSON Schema at version 3**

Change only `schemas/feasibility-receipt.schema.json`:

```text
top-level schema_version const: 3
normative required/properties: deterministic_attention
invariants required/properties: four A6 booleans
exact_comparison required/properties: deterministic_attention
$defs: deterministic_attention and sdpa_backend_state
```

Use `additionalProperties: false` on both new definitions. Every string, map key, Boolean, and digest is a `const`; do not use wildcard `.lock`, pattern properties, permissive string maps, or optional A6 fields.

- [ ] **Step 6: Enforce A6 independently in receipt validation**

In `receipts.py`:

```python
_ALLOWED_SCHEMAS[("feasibility", 3)] = _SCHEMA_ROOT / "feasibility-receipt.schema.json"
_A6_DETERMINISTIC_ATTENTION = {
    "attn_implementation": "sdpa",
    "backend": "MATH",
    "scope": "labeled_forward_through_backward",
    "before": {
        "cudnn": True,
        "flash": True,
        "math": True,
        "memory_efficient": True,
    },
    "inside": {
        "cudnn": False,
        "flash": False,
        "math": True,
        "memory_efficient": False,
    },
    "after": {
        "cudnn": True,
        "flash": True,
        "math": True,
        "memory_efficient": True,
    },
    "restored": True,
    "source_hash_rule": "python-source-lf-normalized-sha256-v1",
    "source_sha256": {
        "torch_nn_attention": "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0",
        "transformers_sdpa_attention": "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098",
    },
}
```

Remove feasibility version 2 from the current allowlist; historical files stay immutable but cannot be current A6 receipts. Require schema version 3 in `_validate_feasibility_consistency()`. Require `normative.deterministic_attention` to equal `_A6_DETERMINISTIC_ATTENTION`, require the exact-replay copy to equal it, and add the four booleans to `expected_evidence` using independent field comparisons. Keep all A3/A4 warning, environment, parent, checkpoint, VRAM, parameter, recipe, and status/error logic unchanged.

- [ ] **Step 7: Run GREEN for schema, validator, and replay**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'receipt or schema or exact_comparison or deterministic_attention or a6'
uv run pytest tests/probes/test_training_feasibility.py -q
```

Require zero failures. Confirm a valid schema-v3 receipt passes structural and semantic validation; every listed mutation fails; schema v2 fails; replay digest changes with the A6 object; and every retained A2-A5 probe test remains green.

**Stop condition:** schema version 2 can satisfy A6, validation trusts booleans without evidence, replay omits the full object, a current parent/gate needs an unauthorized fifth file, or any existing normative gate is weakened.

---

### Task 4: Verify, Review, and Commit the A6 Candidate

**Files:**
- Verify and stage: the exact four-file implementation allowlist
- Modify: none except corrections within that allowlist required by an authorized failed gate

**Interfaces:**
- Consumes: Tasks 2-3 GREEN worktree and Task 1 baseline
- Produces: one clean append-only A6 source candidate commit

- [ ] **Step 1: Run focused, full CPU, and quality gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v
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

Require zero failures. Capability skips must be explained and cannot skip an A6 behavior available on CPU. Do not run a model or GPU merely to satisfy unit coverage.

- [ ] **Step 2: Perform the required fresh independent review pass**

Review the complete diff from the approved plan commit without relying on implementation notes. Record Critical, Important, and Minor findings. Critical and Important must both be zero. Explicitly inspect:

```text
source verification before callback and exact two-key mapping
public PyTorch API only; model config remains sdpa
exact pre/inside/post backend states
Math-only context covers forward, loss validation, backward, warning validation
context exits before gradients, optimizer, checkpoint, and receipt
normal and exceptional restoration; body exception chaining
unchanged nine-warning parser/category/count/source contract
schema-v3 closed object and four derived invariants
semantic validator equality independent of schema
full object included in exact replay preimage
schema-v2 evidence cannot satisfy A6
all parent, no-clobber, VRAM, checkpoint, and numerical gates retained
```

Any correction repeats the affected RED/GREEN proof and all Step 1 gates.

- [ ] **Step 3: Verify scope and historical preservation**

Require `git diff --name-only` to equal exactly:

```text
schemas/feasibility-receipt.schema.json
src/vision_active_learning_loop/artifacts/receipts.py
src/vision_active_learning_loop/probes/training_feasibility.py
tests/probes/test_training_feasibility.py
```

Rehash the entire Task 1 baseline and every A5 hash from Step 2. Require zero missing, changed, or unexpected-in-baseline entries. Verify `uv.lock`, Dockerfile, runner, configs, approved spec/plan, every other source/test/schema, all old images, and all historical campaigns are unchanged.

- [ ] **Step 4: Create one append-only implementation commit**

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
$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne 4) { throw 'A6 staged scope mismatch' }
git diff --cached --check
git commit -m 'fix: enforce deterministic SDPA math'
```

Do not amend, rebase, reset, squash, or rewrite any earlier commit.

- [ ] **Step 5: Verify the committed source candidate freshly**

Repeat the focused test file, targeted Black/Ruff, `uv lock --check`, and committed diff check. Require exact author/committer, exactly four changed files, parent equal to the docs-only plan commit, linked worktree clean, canonical main clean, and no untracked cache files. The resulting HEAD is the sole A6 source SHA.

- [ ] **Step 6: Stop for separate owner candidate review**

Report the candidate SHA, exact four-file diff, RED/GREEN evidence, focused/full CPU counts, Black/Ruff/lock/diff results, Critical/Important review counts, historical rehash result, and both clean Git states. Do not build an image, create an A6 run ID, or acquire a GPU lease until the owner separately authorizes that exact candidate SHA for Tasks 5-6.

**Stop condition:** any failed test/quality/review/evidence/identity gate, Critical or Important finding, extra tracked file, dirty worktree, or historical drift.

---

### Task 5: Build and Preflight One Fresh A6 Campaign

**Files:**
- Execute unchanged: `docker/wave0.Dockerfile`
- Write externally: one new A6 campaign/audit root and one fresh OCI image identity
- Modify in Git: none

**Interfaces:**
- Consumes: sole clean A6 source SHA from Task 4
- Produces: fresh image identity plus CPU-only source/backend micro-check evidence before any GPU lease

**Entry condition:** written owner authorization naming the exact clean A6 candidate SHA from Task 4.

- [ ] **Step 1: Revalidate execution boundary without redoing Tasks 1-4**

Require exact worktree/branch/source SHA and clean states; Docker context `desktop-linux`; Linux Server health; Docker GPU collector returns one RTX 4090 CSV row; `VAL_DATA_ROOT` unset; no active numeric compute process; no active project lease/container; and all Task 1/A5 hashes unchanged. Inspect historical Option A tag `vision-active-learning-loop:wave0-option-a-97d5789` and require image ID `sha256:558a468b2bcb1a96a9198fb35a1590e57c376e5a7e6ac5032b3cdff44bbaacc9`. Do not rebuild or retag it.

- [ ] **Step 2: Create fresh identities and build exactly once**

Generate a never-used UTC run ID:

```powershell
$Timestamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$RunId = "wave0-a6-$Timestamp"
$SourceSha = (git rev-parse HEAD).Trim()
$ImageTag = "vision-active-learning-loop:wave0-a6-$($SourceSha.Substring(0,12))-$($RunId.ToLowerInvariant())"
$CampaignRoot = "D:\vision-active-learning-loop-artifacts\wave0\a6-runs\$RunId"
$CheckpointRoot = "D:\vision-active-learning-loop-artifacts\wave0\checkpoints\$RunId"
$GateRoot = Join-Path $CampaignRoot 'gate'
foreach ($Path in @($CampaignRoot, $CheckpointRoot, $GateRoot)) {
    if (Test-Path -LiteralPath $Path) { throw "A6 destination exists: $Path" }
}
```

Atomically create only the campaign/audit root, then build once with `--no-cache` and OCI labels:

```text
org.opencontainers.image.revision=$SourceSha
org.opencontainers.image.ref.name=$RunId
org.opencontainers.image.base.digest=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356
```

Record build argv, exit code, log, exact image ID, labels, repository digest if available, and inspect JSON through atomic `CreateNew` audit files. Build failure preserves the campaign and stops; do not rebuild.

- [ ] **Step 3: Run the CPU-only no-model A6 micro-check**

Run the fresh image without GPU, network, or host mounts:

```powershell
docker run --rm --network none `
  --entrypoint /opt/val/.venv/bin/python `
  $ImageTag -c @'
import json
import torch
from torch.nn.attention import SDPBackend, sdpa_kernel
from vision_active_learning_loop.probes.training_feasibility import (
    _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE,
    _sdpa_backend_state,
    _verify_deterministic_attention_sources,
)
torch.use_deterministic_algorithms(True, warn_only=False)
torch.set_deterministic_debug_mode("error")
before = _sdpa_backend_state()
with sdpa_kernel(SDPBackend.MATH):
    inside = _sdpa_backend_state()
after = _sdpa_backend_state()
print(json.dumps({
    "rule": _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE,
    "source_sha256": _verify_deterministic_attention_sources(),
    "before": before,
    "inside": inside,
    "after": after,
    "strict_mode": torch.get_deterministic_debug_mode(),
}, sort_keys=True, separators=(",", ":")))
'@
```

Require exact two-source hashes, exact before/inside/after maps, `strict_mode == 2`, exit code 0, and no stderr. Atomically preserve argv/stdout/stderr/exit/image/source identities. This micro-check proves only source and public backend-state mechanics; it does not prove CUDA model determinism.

**Stop condition:** Docker/GPU/identity/history failure, existing destination, build failure, micro-check mismatch, or any source change after image creation.

---

### Task 6: Execute One Fresh Full A6 Task 6 and Stop

**Files:**
- Execute unchanged: `scripts/run_wave0_clean.ps1` and the current `val gate wave0`
- Write externally: fresh primary, clean-a, clean-b, checkpoint, gate, audit, lease, and closure evidence below the new A6 identities
- Modify in Git: none

**Interfaces:**
- Consumes: Task 5 source/image/run identities and CPU-only micro-check PASS
- Produces: one immutable A6 normative failure campaign or a complete A6 Wave 0 PASS evidence chain

- [ ] **Step 1: Acquire one exclusive RTX 4090 lease**

Use the approved collector with the image entrypoint overridden:

```powershell
docker run --rm --gpus all --network none --entrypoint nvidia-smi `
  nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 `
  --query-gpu=uuid,name,memory.total,memory.used,memory.free `
  --format=csv,noheader,nounits
```

Require one RTX 4090 row and no competing numeric compute workload. Atomically create `D:\vision-active-learning-loop-artifacts\wave0\leases\$RunId` with source/image/GPU/process/preflight identity. If the GPU or lease is unavailable, stop without CPU fallback or mock execution.

- [ ] **Step 2: Run primary, clean-a, and clean-b once in order**

```powershell
.\scripts\run_wave0_clean.ps1 -RunId $RunId -AttemptId primary `
  -ImageTag $ImageTag -ImageDigest $ImageId -HostArtifactRoot $CampaignRoot
.\scripts\run_wave0_clean.ps1 -RunId $RunId -AttemptId clean-a `
  -ImageTag $ImageTag -ImageDigest $ImageId -HostArtifactRoot $CampaignRoot
.\scripts\run_wave0_clean.ps1 -RunId $RunId -AttemptId clean-b `
  -ImageTag $ImageTag -ImageDigest $ImageId -HostArtifactRoot $CampaignRoot
```

For every attempt require environment, model-assets, model-contract, feasibility-A, feasibility-B, checkpoint-A, and checkpoint-B. Each feasibility receipt must be schema v3 and contain the exact A6 deterministic-attention object, four true A6 invariants, exactly nine grid-sample warnings, finite scalar loss, BF16 autocast/backward, finite gradients, detector and backbone updates, peak allocated VRAM at most 22 GiB, checkpoint round trip, exact source/image/run/parent bindings, and fresh no-clobber paths.

On the first nonzero stage, missing destination, invalid receipt/checkpoint, fused-attention warning, OOM, VRAM breach, identity mismatch, or other normative failure: preserve the attempt/campaign, skip every later model stage, release the lease, write closure evidence, and stop. Do not retry or build again.

- [ ] **Step 3: Validate five deterministic comparisons and aggregate once**

Run only after all six feasibility receipts and six checkpoints pass independent validation:

```text
primary B  -> primary A
clean-a A  -> primary A
clean-a B  -> primary A
clean-b A  -> primary A
clean-b B  -> primary A
```

Require the full schema-v3 `deterministic_attention` object in every exact comparison and exact equality across all six receipts. Retain gradient relative tolerance `1e-5`, gradient absolute tolerance `1e-7`, vector relative L2 maximum `1e-3`, and cosine minimum `0.99999`.

Create a fresh gate destination and run:

```text
val gate wave0 --run-id $RunId \
  --primary-root /artifacts/primary \
  --clean-a-root /artifacts/clean-a \
  --clean-b-root /artifacts/clean-b \
  --output /artifacts/gate/wave0-gate-receipt.json
```

The unchanged aggregate receipt retains its existing Wave 0 schema/interpretation vocabulary. It is necessary but not sufficient for A6: the campaign closure may issue the A6 terminal only after separately validating that all six parent feasibility receipts are schema v3, all six contain the exact A6 object and true invariants, all five replay comparisons include that object, and the stored aggregate receipt itself is a complete PASS. An older aggregate receipt or an aggregate PASS over schema-v2 parents cannot satisfy A6.

- [ ] **Step 4: Close, rehash, release, and stop**

Write a no-clobber campaign manifest containing source SHA, image identity, run ID, GPU/lease identity, every attempt/stage exit, receipt/checkpoint path-size-SHA256, exact/numerical comparisons, aggregate receipt/hash, peak VRAM values, losses, warning inventories, and final verdict. Rehash the complete Task 1 baseline and A5 fixed hashes. Require zero historical drift and clean linked/canonical worktrees.

Release the lease by writing `release.json` with `FileMode.CreateNew`, validating it, and atomically renaming the exact lease directory to `$RunId.released`; never delete it.

On any normative failure, the only terminal is:

```text
WAVE0_A6_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

On complete success, the only terminal is:

```text
WAVE0_A6_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED
```

In both outcomes stop immediately. Do not fix, retry, access RDD, or begin Wave 1 under this plan.

---

## Plan Self-Review Record

- [x] Every Section 5.2.8 requirement maps to an explicit implementation, test, review, micro-check, or execution step.
- [x] The four-file implementation allowlist is exact; a fifth tracked file is a hard stop.
- [x] RED tests precede production changes and name the expected missing behavior.
- [x] Function signatures, dataclass fields, source keys, backend keys, receipt fields, invariant names, schema version, hashes, and terminal strings are consistent across all tasks.
- [x] The public Math-only context covers labeled autocast forward, scalar finite-loss validation, bounded backward, and warning validation, and exits before gradient/optimizer/checkpoint/receipt work.
- [x] Source/config/entry/inside checks happen before model execution; normal and exceptional restoration is explicit and fail closed.
- [x] Exactly nine grid-sample warnings remain accepted; the two exact A5 fused-attention warnings remain rejected.
- [x] Schema v3, semantic validation, and exact replay all require the same closed deterministic-attention object and four evidence-derived booleans.
- [x] The missing existing `semantic_input_digests` constructor argument is passed without changing its field, digest rule, or research meaning.
- [x] Model, revisions, processor, queries, classes, BF16, dependencies, seeds, budgets, fit counts, numerical thresholds, VRAM, checkpoint, and research claims remain unchanged.
- [x] A5 and all earlier evidence/images/campaigns remain immutable; every A6 path and identity is fresh and no-clobber.
- [x] The CPU micro-check does not claim CUDA determinism; the full model runs only after the GPU lease.
- [x] One fresh Task 6 execution is allowed; no retry follows a normative failure.
- [x] RDD, Wave 1, remote operations, push, merge, tag, Release, and GitHub publication remain forbidden.
- [x] Placeholder, contradiction, ambiguity, scope-drift, type-consistency, and exact-path scans have no unresolved finding.

## Execution Selection

The owner delegated execution-method selection. After this plan receives written owner review, use **Inline Execution** in the existing registered linked worktree with `superpowers:executing-plans`. Do not dispatch subagents. Pause only at a hard stop or the terminal Wave 0 owner checkpoint.
