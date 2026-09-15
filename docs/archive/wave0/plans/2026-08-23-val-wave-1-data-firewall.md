# Wave 1 Data and Oracle Firewall Implementation Plan

> **Historical 8-wave protocol.** Preserved for provenance; this is not the current task queue. The original Wave 0 gate did not pass. The separately approved lite research completed its v0.3 five-strategy first comparison on 2026-09-12; see the [current README](../../../../README.md) and [v0.3 results](../../../results/2026-09-12-v0.3-diversity.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one license-compliant, globally de-duplicated, group-aware RDD manifest and prove that strategy/trainer processes cannot access hidden pool, source-test, or China Drone annotations.

**Architecture:** A trusted curator operates on owner-approved host volumes, while all public manifests use opaque SHA-256 item IDs. Exact SHA, pHash, and label-blind DINO review run over the joint source-plus-shift candidate universe before roles. OCI mount policies create separate public-pool, sealed-oracle, and sealed-evaluator capabilities; a Wave 1 gate binds every lineage and firewall receipt.

**Tech Stack:** Wave 0 locked runtime; Python pathlib/hashlib; Pillow/imagehash; DINOv2-small; JSONL/Parquet manifests; JSON Schema; pytest; WSL2/OCI path and mount tests.

## Global Constraints

- Entry requires a valid Wave 0 gate receipt and explicit owner approval of `VAL_DATA_ROOT`, `VAL_ARTIFACT_ROOT`, RDD terms, storage, and network download.
- Included candidates are Japan, India, Czech Republic, China MotorBike, and China Drone annotated-train only.
- United States, Norway, public challenge test images, and every other dataset/split are rejected at source discovery.
- Treat included RDD data as CC BY-SA 4.0; raw pixels/annotations and review contact sheets remain outside Git.
- Global duplicate control precedes source/pilot/formal/test/shift role assignment.
- Source-test and China Drone labels are sealed and never mounted into strategy/trainer containers.
- Any checksum/license mismatch, cross-role component, hidden-label access, or manifest mutation fails Wave 1.

---

### Task 1: Gate official source acknowledgement and download

**Objective:** Make dataset acquisition impossible without explicit terms acknowledgement, exact allowlisted subsets, and an approved Wave 0 receipt.

**Files:**
- Create: `DATA_LICENSES.md`
- Create: `configs/data/rdd-sources.yaml`
- Create: `schemas/data-acknowledgement.schema.json`
- Create: `src/vision_active_learning_loop/data/sources.py`
- Create: `src/vision_active_learning_loop/data/download.py`
- Create: `tests/data/test_sources.py`
- Create: `tests/data/test_download_gate.py`

**Interfaces:**
- Produces: `RddSourceSpec.load(path: Path) -> RddSourceSpec`
- Produces: `create_acknowledgement(owner: str, terms_sha256: str, wave0_digest: str) -> DataAcknowledgement`
- CLI: `val data acknowledge --config configs/data/rdd-sources.yaml --owner kuotunyu --wave0 <receipt> --output <json>`
- CLI: `val data fetch --ack <json> --data-root <VAL_DATA_ROOT> --artifact-root <VAL_ARTIFACT_ROOT>`

- [ ] **Step 1: Write failing allowlist and acknowledgement tests**

```python
def test_only_approved_rdd_subsets_are_allowed(spec):
    assert set(spec.subsets) == {"Japan", "India", "Czech", "China_MotorBike", "China_Drone"}

def test_fetch_requires_matching_wave0_and_terms(fetcher, acknowledgement):
    acknowledgement.wave0_digest = "0" * 64
    with pytest.raises(DataAccessDenied):
        fetcher.fetch(acknowledgement)
```

- [ ] **Step 2: Run tests and verify missing modules**

Run: `uv run pytest tests/data/test_sources.py tests/data/test_download_gate.py -v`

Expected: collection fails because data source/download modules are absent.

- [ ] **Step 3: Implement fail-closed source configuration**

Each source entry contains official URL, upstream release identifier, country/domain role candidate, expected archive filename, expected SHA-256 obtained from the authoritative source or owner-verified first download, and license acknowledgement digest. Config validation rejects US/Norway/unknown names, redirects outside the allowlist, missing HTTPS, and a data root inside the Git worktree.

- [ ] **Step 4: Verify acknowledgement before any network transfer**

Run: `uv run val data acknowledge --config configs/data/rdd-sources.yaml --owner kuotunyu --wave0 "$VAL_ARTIFACT_ROOT/wave0/receipts/wave0-gate-receipt.json" --output "$VAL_ARTIFACT_ROOT/manifests/data-acknowledgement.json"`

Expected: receipt records CC BY-SA 4.0 conservative treatment, official URLs, excluded subsets, host roots, owner, timestamp, and Wave 0 digest. Without owner-approved roots/terms, command exits 2 before opening a network connection.

- [ ] **Step 5: Download to immutable staging and verify checksums**

Run: `uv run val data fetch --ack "$VAL_ARTIFACT_ROOT/manifests/data-acknowledgement.json" --data-root "$VAL_DATA_ROOT" --artifact-root "$VAL_ARTIFACT_ROOT"`

Expected: archives land under `raw/rdd/<release_digest>/archives`, use partial files plus atomic rename, match expected hashes, and become read-only; mismatch is quarantined and no extraction marker exists.

**Artifact/evidence produced:** `DATA_LICENSES.md`, acknowledgement, upstream/checksum receipt, and network/download audit.

**Stop condition:** Missing owner approval, ambiguous/changed terms, unknown authoritative checksum, redirect outside allowlist, hash mismatch, or excluded subset present.

**Commit boundary:** `feat: gate official rdd acquisition`

---

### Task 2: Build immutable raw inventory and dataset lineage primitives

**Objective:** Extract only verified archives into external read-only storage and assign content identities without exposing annotations to public consumers.

**Files:**
- Create: `src/vision_active_learning_loop/data/inventory.py`
- Create: `src/vision_active_learning_loop/data/lineage.py`
- Create: `schemas/raw-inventory.schema.json`
- Create: `schemas/dataset-lineage.schema.json`
- Create: `tests/data/test_inventory.py`
- Create: `tests/data/test_lineage.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `inventory_archives(ack: DataAcknowledgement, root: Path) -> RawInventory`
- Produces: `item_id(path: Path) -> str` as SHA-256 of pixel file bytes
- Produces: `assert_external_root(root: Path, repository_root: Path) -> None`
- Produces: `LineageBuilder.add(parent_digest, artifact_kind, records) -> str`

- [ ] **Step 1: Write failing external-root and identity tests**

```python
def test_data_root_inside_repo_is_rejected(repo_root):
    with pytest.raises(StorageBoundaryError):
        assert_external_root(repo_root / "data", repo_root)

def test_item_identity_ignores_filename(two_equal_files):
    assert item_id(two_equal_files[0]) == item_id(two_equal_files[1])
```

- [ ] **Step 2: Run tests and confirm red state**

Run: `uv run pytest tests/data/test_inventory.py tests/data/test_lineage.py -v`

Expected: missing inventory/lineage imports.

- [ ] **Step 3: Implement immutable extraction and sealed inventory views**

Inventory records contain opaque item ID, source domain, image byte count/dimensions, archive/member digests, annotation-object digest, and trusted annotation locator stored only in the sealed inventory. The public inventory omits paths, filenames, annotation locators/counts/classes, and country metadata intended to be hidden from strategies.

- [ ] **Step 4: Add Git exclusion guards**

Ignore `.env*`, `data/`, `artifacts/`, `checkpoints/`, `*.safetensors`, `*.pt`, `*.pth`, `*.onnx`, `*.parquet` outside explicit aggregate-report paths, archives, images, embeddings, and per-item result files. Add a test that fails when a tracked fixture claims an RDD source.

- [ ] **Step 5: Verify extraction/inventory on a synthetic archive first, then approved RDD**

Run: `uv run pytest tests/data/test_inventory.py tests/data/test_lineage.py -v && uv run val data inventory --ack <ack.json> --output "$VAL_ARTIFACT_ROOT/manifests/raw-inventory.json"`

Expected: tests pass; raw inventory is content-addressed, archives/extracted roots are read-only, public and sealed schemas differ exactly, and Git status contains no data artifact.

**Artifact/evidence produced:** raw inventory, archive/member lineage, storage-boundary tests, and updated public exclusions.

**Stop condition:** Any archive/member is mutable after acceptance, a public record exposes a hidden locator/label statistic, or an artifact root resolves inside Git.

**Commit boundary:** `feat: inventory immutable rdd inputs`

---

### Task 3: Compute global exact and pHash components

**Objective:** Detect duplicates across all five candidate domains before role assignment, using global SHA and verified 256-bit pHash connected components.

**Files:**
- Create: `src/vision_active_learning_loop/data/duplicates.py`
- Create: `src/vision_active_learning_loop/data/components.py`
- Create: `schemas/duplicate-candidates.schema.json`
- Create: `tests/data/test_duplicates.py`
- Create: `tests/data/test_components.py`

**Interfaces:**
- Produces: `compute_phash256(image: Image) -> int`
- Produces: `build_duplicate_components(records, max_hamming: int = 6) -> list[DuplicateComponent]`
- Produces: `apply_component_review(components, decisions) -> DuplicateLedger`
- CLI: `val data duplicates --sealed-inventory <json> --review-root <external-path> --output <json>`

- [ ] **Step 1: Write failing global connected-component tests**

```python
def test_transitive_phash_neighbors_form_one_component():
    records = [record("a", 0b0000), record("b", 0b0001), record("c", 0b0011)]
    assert component_ids(build_duplicate_components(records, max_hamming=1)) == [{"a", "b", "c"}]

def test_component_crossing_source_shift_is_marked_conflicting():
    component = component_with_domains("Japan", "China_Drone")
    assert component.crosses_source_shift is True
```

- [ ] **Step 2: Verify tests fail before implementation**

Run: `uv run pytest tests/data/test_duplicates.py tests/data/test_components.py -v`

Expected: missing duplicate/component modules.

- [ ] **Step 3: Implement global indexes and review manifest**

Sort inputs by item ID, union exact SHA matches, compute 16×16 pHash, join pairs with Hamming distance <=6, and use deterministic union-find whose representative is the minimum item ID. Generate contact sheets under the external review root only; each sheet has an artifact digest and no Git path.

- [ ] **Step 4: Apply curator decisions deterministically**

Review decisions are `confirm`, `reject_candidate`, or `unresolved`. `unresolved` blocks the gate. Confirmed same-side components retain minimum item ID; any component spanning source and China Drone excludes all members with the spec-defined reason.

- [ ] **Step 5: Verify permutation and cross-domain behavior**

Run: `uv run pytest tests/data/test_duplicates.py tests/data/test_components.py -v`

Expected: exact component IDs independent of input order; all conflicting component members excluded; no roles exist yet.

**Artifact/evidence produced:** exact/pHash candidate table, external review sheets, decisions, component ledger, exclusion reasons.

**Stop condition:** Any candidate remains unresolved, component identity changes with input order, or a role was assigned before this task completes.

**Commit boundary:** `feat: detect global duplicate components`

---

### Task 4: Run label-blind DINO neighbor audit and finalize exclusions

**Objective:** Search the joint candidate universe for visual near-duplicates without exposing labels and merge every confirmed neighbor before roles.

**Files:**
- Create: `src/vision_active_learning_loop/data/dino_audit.py`
- Create: `src/vision_active_learning_loop/data/neighbor_review.py`
- Create: `schemas/neighbor-audit.schema.json`
- Create: `tests/data/test_dino_audit.py`
- Create: `tests/data/test_neighbor_review.py`

**Interfaces:**
- Produces: `embed_audit_candidates(public_images, asset_receipt) -> AuditEmbeddingManifest`
- Produces: `find_neighbors(embeddings, min_cosine: float = 0.995) -> list[NeighborPair]`
- Produces: `finalize_components(base_ledger, neighbor_decisions) -> FinalDuplicateLedger`

- [ ] **Step 1: Write failing label-blind and threshold tests**

```python
def test_audit_input_schema_has_no_annotation_fields(public_record):
    assert set(public_record) == {"item_id", "image_locator_token", "pixel_sha256"}

def test_confirmed_cross_shift_neighbor_excludes_entire_component(base_ledger, confirmed_pair):
    final = finalize_components(base_ledger, [confirmed_pair])
    assert all(member.excluded for member in final.component(confirmed_pair).members)
```

- [ ] **Step 2: Verify missing implementation**

Run: `uv run pytest tests/data/test_dino_audit.py tests/data/test_neighbor_review.py -v`

Expected: missing-module collection failure.

- [ ] **Step 3: Implement pinned DINO audit embedding**

Use the Wave 0 verified DINO revision/license/hash, final post-LayerNorm CLS token, float32 L2 normalization, and label-free image view. Bind audit rows to upstream item/archive hashes. Find all cosine pairs >=0.995 with deterministic `(similarity_key desc, item_id_a, item_id_b)` ordering.

- [ ] **Step 4: Review and finalize**

Generate external contact sheets, record `confirm`, `reject_candidate`, or `unresolved`, union confirmed pairs, apply cross-source/shift whole-component exclusion, and retain only minimum item ID for same-side components. Filter/rebind retained vectors to the final manifest digest later; do not recompute identities from paths.

- [ ] **Step 5: Verify global coverage and no role leakage**

Run: `uv run pytest tests/data/test_dino_audit.py tests/data/test_neighbor_review.py -v && uv run val data neighbor-audit --inventory <public.json> --base-ledger <json> --output <json>`

Expected: all five domains represented in audit input; all decisions resolved; zero role fields before final ledger; exact excluded-component reasons.

**Artifact/evidence produced:** audit embedding manifest, neighbor candidates/review, final global duplicate ledger and digest.

**Stop condition:** DINO asset mismatch, labels/country counts reach the embedder, any decision unresolved, or a confirmed cross-boundary component remains retained.

**Commit boundary:** `feat: finalize visual duplicate exclusions`

---

### Task 5: Assign capture groups, roles, and immutable calibration hashes

**Objective:** Apply the approved group parser and split hash only after global duplicate finalization, then produce public/sealed role manifests and one trusted coverage audit.

**Files:**
- Create: `src/vision_active_learning_loop/data/groups.py`
- Create: `src/vision_active_learning_loop/data/splits.py`
- Create: `src/vision_active_learning_loop/data/calibration_partition.py`
- Create: `schemas/dataset-manifest.schema.json`
- Create: `schemas/coverage-audit.schema.json`
- Create: `tests/data/test_groups.py`
- Create: `tests/data/test_splits.py`

**Interfaces:**
- Produces: `derive_split_group(record, parser_version) -> str`
- Produces: `source_role(split_group_id: str) -> Literal["source_test","pilot","formal_pool"]`
- Produces: `calibration_remainder(item_id: str) -> int`
- CLI: `val data split --duplicate-ledger <json> --sealed-inventory <json> --output-root <external-path>`

- [ ] **Step 1: Write failing hash-boundary and no-crossing tests**

```python
@pytest.mark.parametrize(("r","role"), [(0,"source_test"),(1999,"source_test"),(2000,"pilot"),(2799,"pilot"),(2800,"formal_pool"),(9999,"formal_pool")])
def test_role_boundaries(r, role):
    assert role_from_bucket(r) == role

def test_group_cannot_cross_roles(grouped_manifest):
    assert max_roles_per_group(grouped_manifest) == 1
```

- [ ] **Step 2: Verify red tests**

Run: `uv run pytest tests/data/test_groups.py tests/data/test_splits.py -v`

Expected: missing group/split modules.

- [ ] **Step 3: Implement approved group and split contracts**

Use validated route/sequence/capture parser where available; fallback to item ID and count fallbacks. Group ID is minimum member item ID. Compute the exact `val-loop-split-v1` SHA-256 bucket intervals. China Drone receives only `shift_test`. Calibration remainder uses `calibration-v1`, is public only as `train_or_calibration_token`, and is interpreted after acquisition.

- [ ] **Step 4: Generate public, oracle, and evaluator manifests**

Public pool contains opaque IDs and image tokens but no country/path/label counts. Oracle manifest contains formal-pool annotation locators. Evaluator manifests contain source-test and China Drone locators. Trusted analyst slice metadata is separately sealed.

- [ ] **Step 5: Run the single coverage audit**

Run: `uv run val data split --duplicate-ledger <final-ledger.json> --sealed-inventory <sealed.json> --output-root "$VAL_ARTIFACT_ROOT/manifests"`

Expected: role counts, source country/class boxes, fallback rate, group sizes, exclusion counts, zero cross-role group/component. Missing country in formal/test or zero test boxes for a class yields `FAIL` without redraw.

**Artifact/evidence produced:** dataset manifest, split/calibration receipts, public/oracle/evaluator views, coverage audit, parser/version digest.

**Stop condition:** Coverage gate fails, group/component crosses roles, China Drone enters source, or a strategy-facing record exposes country/annotation information.

**Commit boundary:** `feat: freeze grouped dataset roles`

---

### Task 6: Enforce oracle and formal-evaluation filesystem boundaries

**Objective:** Prove by adversarial tests that strategy/trainer containers cannot reach unrevealed annotations or evaluator roots.

**Files:**
- Create: `src/vision_active_learning_loop/security/path_policy.py`
- Create: `src/vision_active_learning_loop/security/mount_policy.py`
- Create: `src/vision_active_learning_loop/security/audit_log.py`
- Create: `docker/strategy.compose.yaml`
- Create: `docker/evaluator.compose.yaml`
- Create: `tests/security/test_path_policy.py`
- Create: `tests/security/test_firewall.py`
- Create: `tests/security/test_embargo_mounts.py`

**Interfaces:**
- Produces: `resolve_allowlisted(path: Path, roots: tuple[Path, ...]) -> Path`
- Produces: `build_strategy_mounts(job_manifest) -> tuple[Mount, ...]`
- Produces: `build_evaluator_mounts(formal_completion_seal) -> tuple[Mount, ...]`
- CLI: `val firewall verify --dataset-manifest <json> --output <receipt>`

- [ ] **Step 1: Write failing traversal, link, and injection tests**

```python
@pytest.mark.parametrize("attack", ["../sealed", "absolute", "symlink", "junction", "env", "config"])
def test_strategy_cannot_reach_sealed_root(firewall, attack):
    assert firewall.attempt(attack).allowed is False

def test_evaluator_mount_requires_valid_completion_seal():
    with pytest.raises(EmbargoError):
        build_evaluator_mounts(None)
```

- [ ] **Step 2: Run tests and observe missing security modules**

Run: `uv run pytest tests/security -v`

Expected: collection fails.

- [ ] **Step 3: Implement real-path and mount capability checks**

Resolve Windows junctions/WSL symlinks to canonical host paths before comparison, reject network paths and path traversal, use read-only allowlisted mounts, disable inherited environment/config mount additions, sanitize tracebacks/log fields, and separate public image, acquired-label, oracle, and evaluator capabilities. Evaluator capability construction requires the schema- and hash-valid `formal_completion_seal`; no earlier wave receipt or mutable flag can substitute for it.

- [ ] **Step 4: Run adversarial containers**

Run: `uv run val firewall verify --dataset-manifest "$VAL_ARTIFACT_ROOT/manifests/dataset-manifest.json" --output "$VAL_ARTIFACT_ROOT/manifests/firewall-receipt.json"`

Expected: every approved path succeeds, every attack fails, hidden content mutation leaves pre-acquisition strategy output unchanged, and evaluator startup without a seal exits 2 before container creation.

- [ ] **Step 5: Inspect logs/results for leakage**

Run: `uv run pytest tests/security/test_firewall.py -v -k "log or exception or dataloader or hidden_mutation"`

Expected: no annotation locator, class/box count, country, sealed path, per-item test output, or hidden cache key appears.

**Artifact/evidence produced:** firewall receipt, mount manifests, attack matrix, sanitized audit logs.

**Stop condition:** Any hidden path/content is readable, any evaluator mount exists without a valid seal, or a log/exception leaks forbidden data.

**Commit boundary:** `feat: enforce oracle and evaluator firewall`

---

### Task 7: Bind lineage, invalidation, and Wave 1 exit gate

**Objective:** Accept the dataset only when every upstream/download/dedup/split/firewall digest is complete and define irreversible invalidation behavior.

**Files:**
- Create: `src/vision_active_learning_loop/gates/wave1.py`
- Create: `src/vision_active_learning_loop/protocol/invalidation.py`
- Create: `schemas/wave1-gate-receipt.schema.json`
- Create: `schemas/protocol-invalidation.schema.json`
- Create: `tests/gates/test_wave1_gate.py`
- Create: `tests/protocol/test_invalidation.py`
- Create: `docs/runbooks/wave1.md`

**Interfaces:**
- Produces: `evaluate_wave1(inputs: Wave1Inputs) -> Wave1GateReceipt`
- Produces: `invalidate_experiment(protocol_version, experiment_id, reason, parent_digests) -> InvalidationReceipt`
- CLI: `val gate wave1 --input-root <manifest-root> --output <receipt>`

- [ ] **Step 1: Write failing lineage and invalidation tests**

```python
def test_wave1_requires_global_dedup_before_roles(valid_inputs):
    valid_inputs.dataset_manifest["created_at"] = valid_inputs.duplicate_ledger["created_at"] - 1
    assert evaluate_wave1(valid_inputs).status == "FAIL"

def test_invalidation_never_overwrites_old_receipt(invalidator, existing):
    with pytest.raises(ImmutableArtifactError):
        invalidator.replace(existing)
```

- [ ] **Step 2: Confirm missing gate implementation**

Run: `uv run pytest tests/gates/test_wave1_gate.py tests/protocol/test_invalidation.py -v`

Expected: missing modules.

- [ ] **Step 3: Implement complete lineage checks**

Require Wave 0, acknowledgement, archive inventory, global duplicate, DINO review, split/calibration, coverage, and firewall receipts; validate parent hashes, creation order, schema/protocol versions, clean Git commit, external roots, and zero unresolved records.

- [ ] **Step 4: Implement invalidation receipts**

Reasons include `license_change`, `checksum_mismatch`, `new_cross_role_duplicate`, `group_crossing`, `firewall_leak`, `manifest_mutation`, and `protocol_change`. Invalidation writes a new immutable receipt and denies the experiment/manifests to downstream capability checks.

- [ ] **Step 5: Verify gate and stop for review**

Run: `uv run pytest tests/gates/test_wave1_gate.py tests/protocol/test_invalidation.py -v && uv run val gate wave1 --input-root "$VAL_ARTIFACT_ROOT/manifests" --output "$VAL_ARTIFACT_ROOT/manifests/wave1-gate-receipt.json"`

Expected: tests pass and gate status is `PASS`; injected component/role/firewall/hash defects yield `FAIL` and invalidation receipt. Report and stop before Wave 2.

**Artifact/evidence produced:** dataset-lineage digest, Wave 1 gate receipt, invalidation schema/tests, owner review packet.

**Stop condition:** Any required receipt is absent/mismatched, any unresolved review remains, or the firewall/coverage gate is not `PASS`.

**Commit boundary:** `feat: seal wave one dataset lineage`
