# Wave 3 Acquisition and Simulated-Oracle Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement exactly five deterministic acquisition arms and a crash-safe simulated-labeling queue whose receipts prove selected-item identity, budget cost, and oracle isolation.

**Architecture:** Strategies consume a restricted `StrategyContext` and return ranked score records without labels. A shared group-aware filler converts ranking into exact image batches, then a state-machine queue exports/imports labels or replays the trusted oracle. The round orchestrator atomically binds checkpoint, embeddings, selected IDs, queue events, revealed labels, and realized box cost.

**Tech Stack:** Python/NumPy/PyTorch; RT-DETR raw outputs; DINOv2 float32 embeddings; RTX 4090 canonical k-center; JSONL receipts; CVAT/Label Studio interchange schemas; pytest.

## Global Constraints

- Entry requires Wave 2 `PASS` and owner approval.
- Formal arms are exactly `random`, `entropy`, `margin`, `core_set`, `hybrid_uncertainty_diversity`.
- Strategy inputs cannot include paths, country, annotation/class/box counts, future labels, source-test, or China Drone.
- Image is the acquisition unit; all valid boxes are revealed only after selection. Hidden box count cannot select/fill.
- Raw uncertainty uses all 300 queries, no score threshold/NMS, and fixed top-20 mean.
- Core-set/hybrid formal selections run canonical float32 on RTX 4090 with TF32 off, 4,096-row chunks, integer distance keys, and exact item-ID sequence tests.
- Queue actor is `simulated_oracle` for experiments; no human-time, IAA, or monetary claim.
- No evaluator access is permitted.

---

### Task 1: Define strategy interfaces and deterministic random acquisition

**Objective:** Create the restricted strategy contract, deterministic ranking schema, and one prefix-stable random arm.

**Files:**
- Create: `src/vision_active_learning_loop/acquisition/types.py`
- Create: `src/vision_active_learning_loop/acquisition/base.py`
- Create: `src/vision_active_learning_loop/acquisition/random_strategy.py`
- Create: `schemas/acquisition-ranking.schema.json`
- Create: `tests/acquisition/test_strategy_contract.py`
- Create: `tests/acquisition/test_random_strategy.py`

**Interfaces:**
- Produces: `StrategyContext(unlabeled_ids, acquired_ids, previous_checkpoint, embedding_manifest, seed, round_name)`
- Produces: `ScoreRecord(item_id: str, score: float | None, rank_key: str, diagnostics: Mapping[str, float])`
- Produces: `AcquisitionStrategy.rank(context: StrategyContext) -> tuple[ScoreRecord, ...]`
- Produces: `RandomStrategy.rank(context) -> tuple[ScoreRecord, ...]`

- [ ] **Step 1: Write failing schema and prefix tests**

```python
def test_strategy_context_has_no_hidden_fields():
    assert set(StrategyContext.__dataclass_fields__) == {"unlabeled_ids", "acquired_ids", "previous_checkpoint", "embedding_manifest", "seed", "round_name"}

def test_random_order_is_one_prefix_stable_order(strategy, contexts):
    full = strategy.rank(contexts.initial)
    later = strategy.rank(contexts.after_first_batch)
    assert [r.item_id for r in later] == [r.item_id for r in full if r.item_id not in contexts.after_first_batch.acquired_ids]
```

- [ ] **Step 2: Confirm red tests**

Run: `uv run pytest tests/acquisition/test_strategy_contract.py tests/acquisition/test_random_strategy.py -v`

Expected: missing acquisition modules.

- [ ] **Step 3: Implement restricted context and random hash order**

Use `SHA256("random" || seed || item_id)`, then ascending item ID; build the full order once and verify its digest on later prefixes. Reject duplicate/non-pool IDs, NaN scores, hidden fields, and a strategy result not sorted by declared keys.

- [ ] **Step 4: Run contract/random tests**

Run: `uv run pytest tests/acquisition/test_strategy_contract.py tests/acquisition/test_random_strategy.py -v`

Expected: all tests pass, input permutation leaves random order unchanged, and hidden-field injection fails.

**Artifact/evidence produced:** strategy/ranking schemas, random golden order, restricted-context test.

**Stop condition:** Random is re-randomized per round, strategy schema exposes forbidden metadata, or ranking is not unique.

**Commit boundary:** `feat: define acquisition strategy contract`

---

### Task 2: Implement entropy and margin raw-query uncertainty

**Objective:** Implement the approved derived five-state distribution, localization term, and fixed top-20 image reduction with hand-computed tests.

**Files:**
- Create: `src/vision_active_learning_loop/acquisition/uncertainty.py`
- Create: `src/vision_active_learning_loop/acquisition/entropy_strategy.py`
- Create: `src/vision_active_learning_loop/acquisition/margin_strategy.py`
- Create: `fixtures/synthetic/acquisition/uncertainty-cases.json`
- Create: `tests/acquisition/test_uncertainty.py`
- Create: `tests/acquisition/test_uncertainty_strategies.py`

**Interfaces:**
- Produces: `query_distribution(logits: Tensor[Q,4]) -> Tensor[Q,5]`
- Produces: `query_uncertainty(logits, final_boxes, penultimate_boxes, kind: Literal["entropy","margin"]) -> Tensor[Q]`
- Produces: `image_uncertainty(query_scores, top_k: int = 20) -> float`

- [ ] **Step 1: Write failing formula tests from literal fixtures**

```python
def test_distribution_is_derived_background_plus_four_foreground(case):
    p = query_distribution(case.logits)
    torch.testing.assert_close(p.sum(-1), torch.ones(p.shape[0]))
    torch.testing.assert_close(p[:, 0], 1 - torch.sigmoid(case.logits).max(-1).values)

def test_zero_thresholded_detections_are_formula_scored(raw_case):
    assert raw_case.postprocessed_count == 0
    assert image_uncertainty(query_uncertainty(**raw_case.raw, kind="entropy")) == pytest.approx(raw_case.expected)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/acquisition/test_uncertainty.py tests/acquisition/test_uncertainty_strategies.py -v`

Expected: missing uncertainty modules.

- [ ] **Step 3: Implement exact equations**

Compute `s=sigmoid(z)`, `o=max(s)`, conditional `pi=softmax(z)`, `P=[1-o,o*pi]`, localization `1-IoU(final,penultimate)`, normalized entropy or one-minus top-two margin, then `0.75*class + 0.25*o*localization`. Clip boxes only for IoU; degenerate IoU is zero. Image score is arithmetic mean of largest 20 among all 300 queries.

- [ ] **Step 4: Cover invariances and edge cases**

Run: `uv run pytest tests/acquisition/test_uncertainty.py -v -k "confident or ambiguous or localization or permutation or threshold or zero or tie"`

Expected: hand values pass; query permutation and threshold changes preserve score; confident background approaches formula value without a hard-coded zero; item ties sort ascending.

- [ ] **Step 5: Test strategies against raw output only**

Run: `uv run pytest tests/acquisition/test_uncertainty_strategies.py -v`

Expected: entropy/margin consume the previous checkpoint raw accessor, reject calibrated/postprocessed outputs and any tensor not `[B,300,4]` plus intermediate boxes.

**Artifact/evidence produced:** uncertainty fixture, exact formula implementation, invariant/ranking tests.

**Stop condition:** A score depends on NMS/threshold/predicted count/GT, raw shape differs, or hand ranking fails.

**Commit boundary:** `feat: add raw query uncertainty arms`

---

### Task 3: Implement reference and canonical core-set selection

**Objective:** Produce one unique greedy k-center item sequence under the approved RTX numerical contract, prove it against the registered CUDA reference, and provide a CPU reference replay over checked-in precomputed distance keys.

**Files:**
- Create: `src/vision_active_learning_loop/acquisition/core_set_reference.py`
- Create: `src/vision_active_learning_loop/acquisition/core_set_cuda.py`
- Create: `src/vision_active_learning_loop/acquisition/core_set_cpu_replay.py`
- Create: `src/vision_active_learning_loop/acquisition/distance_keys.py`
- Create: `fixtures/synthetic/acquisition/core-set-cases.json`
- Create: `tests/acquisition/test_core_set_reference.py`
- Create: `tests/acquisition/test_core_set_cuda.py`
- Create: `tests/acquisition/test_core_set_cpu_replay.py`

**Interfaces:**
- Produces: `distance_key(distance: Tensor) -> Int64Tensor`
- Produces: `reference_k_center(candidates, centers, batch_size) -> tuple[str, ...]`
- Produces: `canonical_k_center(candidates, centers, batch_size, chunk_size: int = 4096) -> KCenterResult`
- Produces: `replay_precomputed_keys(rounds: Sequence[KeyRound], batch_size: int) -> tuple[str, ...]`

- [ ] **Step 1: Write failing quantization and toy-sequence tests**

```python
def test_distance_key_rounds_half_up():
    assert distance_key(torch.tensor([0.0, 0.00000005, 2.0], dtype=torch.float32)).tolist() == [0, 1, 20_000_000]

def test_equal_key_uses_item_id(case):
    assert reference_k_center(case.candidates, case.centers, 2) == tuple(case.expected_ids)

def test_cpu_reference_replays_exact_selected_item_sequence(case):
    assert replay_precomputed_keys(case.key_rounds, 2) == tuple(case.expected_ids)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/acquisition/test_core_set_reference.py tests/acquisition/test_core_set_cuda.py tests/acquisition/test_core_set_cpu_replay.py -v`

Expected: missing core-set modules.

- [ ] **Step 3: Implement the simple canonical-semantics reference**

The registered selection reference uses contiguous float32 CUDA tensors with TF32 off, candidates ascending item ID, centers `(round,rank,item_id)`, cosine distance clamped `[0,2]`, integer key `floor(d*10_000_000+0.5)`, key descending then ID ascending, and one center update at a time. It evaluates candidate-center pairs directly, exactly as the approved spec requires. The CPU reference implementation consumes only checked-in precomputed per-round integer distance keys and expected centers; it validates ordering/tie/nesting logic and must never be used to create formal or pilot selections or claim arbitrary CPU/GPU numerical identity.

- [ ] **Step 4: Implement optimized 4,096-row path**

Maintain float32 nearest-distance cache, iterate fixed candidate chunks, update after each selected center, and atomically publish cache with input/selected-prefix digest. Raw distance never breaks a key tie.

- [ ] **Step 5: Compare exact item sequences**

Run: `uv run pytest tests/acquisition/test_core_set_reference.py tests/acquisition/test_core_set_cuda.py tests/acquisition/test_core_set_cpu_replay.py -v`

Expected: the registered CUDA reference and optimized canonical path emit the exact selected item-ID sequence on small, equal-key, quantization-boundary, multi-chunk, input-permutation, and nested-prefix fixtures; the CPU reference implementation replays the same expected IDs from precomputed keys only.

**Artifact/evidence produced:** reference/canonical algorithms, key golden vectors, exact sequence fixtures, cache schema.

**Stop condition:** Any item sequence differs, formal path runs CPU/non-RTX/TF32, chunk/order changes, or raw floats break ties.

**Commit boundary:** `feat: add canonical core set selection`

---

### Task 4: Implement the hybrid 5b shortlist strategy

**Objective:** Compose entropy ranking and canonical k-center without changing either contract.

**Files:**
- Create: `src/vision_active_learning_loop/acquisition/hybrid_strategy.py`
- Create: `tests/acquisition/test_hybrid_strategy.py`
- Modify: `fixtures/synthetic/acquisition/core-set-cases.json`

**Interfaces:**
- Produces: `HybridStrategy(shortlist_factor: int = 5)`
- Produces: `HybridStrategy.rank(context, requested_batch: int) -> tuple[ScoreRecord, ...]`

- [ ] **Step 1: Write failing shortlist and exact-sequence tests**

```python
def test_hybrid_shortlist_is_exactly_five_b_unless_pool_smaller(case):
    result = case.strategy.rank(case.context, requested_batch=case.b)
    assert result.metadata.shortlist_size == min(5 * case.b, case.remaining)

def test_hybrid_expected_sequence(case):
    assert tuple(r.item_id for r in case.result[:case.b]) == case.expected_ids
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/acquisition/test_hybrid_strategy.py -v`

Expected: missing hybrid module.

- [ ] **Step 3: Implement deterministic two-stage selection**

Rank all unlabeled images by entropy descending then item ID, take exact `min(5b,N)`, initialize centers from all acquired IDs, and run canonical k-center for `b`. Receipt reports detector score digest, shortlist ordered digest, center digest, key sequence, and selected IDs.

- [ ] **Step 4: Verify boundaries and composition**

Run: `uv run pytest tests/acquisition/test_hybrid_strategy.py -v`

Expected: exact shortlist and item sequence on `N<5b`, equal entropy, equal distance key, and acquired-center fixtures; no margin/calibrated score accepted.

**Artifact/evidence produced:** hybrid strategy, shortlist/selection receipts, exact fixtures.

**Stop condition:** Factor differs from 5, shortlist/centers use hidden metadata, or canonical sequence test differs.

**Commit boundary:** `feat: add hybrid acquisition strategy`

---

### Task 5: Enforce group-aware exact budgets and label-cost ledgers

**Objective:** Convert rankings into nested exact image batches while suppressing same-capture dominance and counting boxes only after oracle reveal.

**Files:**
- Create: `src/vision_active_learning_loop/acquisition/budgets.py`
- Create: `src/vision_active_learning_loop/acquisition/group_filler.py`
- Create: `src/vision_active_learning_loop/acquisition/cost_ledger.py`
- Create: `schemas/acquisition-receipt.schema.json`
- Create: `tests/acquisition/test_budgets.py`
- Create: `tests/acquisition/test_group_filler.py`
- Create: `tests/acquisition/test_cost_ledger.py`

**Interfaces:**
- Produces: `budget_count(pool_size: int, fraction: Decimal) -> int`
- Produces: `fill_group_aware(ranking, group_map, already_acquired, target_total) -> SelectionBatch`
- Produces: `record_revealed_cost(selection, oracle_result) -> CostLedgerEvent`

- [ ] **Step 1: Write failing ceiling/boundary/group tests**

```python
def test_budget_uses_decimal_ceiling():
    assert budget_count(101, Decimal("0.02")) == 3

def test_first_pass_selects_at_most_one_per_group(ranking, groups):
    batch = fill_group_aware(ranking, groups, set(), target_total=4)
    assert first_pass_group_multiplicity(batch) <= 1
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/acquisition/test_budgets.py tests/acquisition/test_group_filler.py tests/acquisition/test_cost_ledger.py -v`

Expected: missing budget/filler/ledger modules.

- [ ] **Step 3: Implement exact nested filler**

Use `ceil(p*N)` for approved fractions. Remove acquired IDs, select first-pass unique capture groups in ranking order, then deterministically fill remaining positions in ranking order. Reject duplicate/non-pool IDs and a target below acquired count.

- [ ] **Step 4: Implement post-reveal box accounting**

Selection receipt contains only image count/IDs/ranks/scores before oracle. Cost event appends revealed valid box count and class/country diagnostics only in trusted analyst ledger after reveal. No strategy-facing artifact receives these fields.

- [ ] **Step 5: Verify exact/nested costs**

Run: `uv run pytest tests/acquisition/test_budgets.py tests/acquisition/test_group_filler.py tests/acquisition/test_cost_ledger.py -v`

Expected: exact budget at all fractions, nested IDs, deterministic fill, and image/box ledger reconciliation.

**Artifact/evidence produced:** budget/filler/cost contracts, nested golden ledgers.

**Stop condition:** Budget uses hidden boxes, duplicates occur, group rule/tie changes, or revealed cost exists pre-oracle.

**Commit boundary:** `feat: enforce acquisition budgets and costs`

---

### Task 6: Build the simulated-oracle queue and interchange adapters

**Objective:** Implement audited state transitions, deterministic exports/imports, and trusted oracle replay without building an annotation UI.

**Files:**
- Create: `src/vision_active_learning_loop/queue/states.py`
- Create: `src/vision_active_learning_loop/queue/store.py`
- Create: `src/vision_active_learning_loop/queue/cvat.py`
- Create: `src/vision_active_learning_loop/queue/label_studio.py`
- Create: `src/vision_active_learning_loop/oracle/adapter.py`
- Create: `schemas/queue-event.schema.json`
- Create: `tests/queue/test_states.py`
- Create: `tests/queue/test_adapters.py`
- Create: `tests/oracle/test_adapter.py`

**Interfaces:**
- Produces: `QueueStore.transition(item_id, expected_state, new_state, payload_digest, actor, reason) -> QueueEvent`
- Produces: `export_cvat/label_studio(queue_manifest, target) -> ExportReceipt`
- Produces: `import_cvat/label_studio(source, expected_manifest) -> ImportReceipt`
- Produces: `OracleAdapter.reveal(selection_receipt) -> RevealedLabelBatch`

- [ ] **Step 1: Write failing state-machine and oracle tests**

```python
def test_happy_state_path(queue):
    assert queue.replay("item-1") == ["unlabeled", "queued", "exported", "labeled", "validated", "acquired"]

def test_oracle_rejects_unselected_item(oracle, forged_selection):
    with pytest.raises(OracleAccessDenied):
        oracle.reveal(forged_selection)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/queue tests/oracle -v`

Expected: missing queue/oracle modules.

- [ ] **Step 3: Implement append-only transitions and validation**

Support approved states plus terminal `rejected` and explicit audited requeue. Record event/experiment/seed/arm/round/item/rank/score/actor/timestamp/schema/payload/reason digests. Validate image dimensions, D00/D10/D20/D40 IDs, box bounds, duplicate boxes, schema/manifest digest. Exported/abstained/rejected selections remain budget-spent.

- [ ] **Step 4: Implement trusted simulated-oracle reveal**

Oracle mount can read formal-pool annotations only, verifies selection digest/current state, reveals all valid boxes for selected IDs, and emits no future/test/shift label. Strategy process receives only acquired-label view after transition.

- [ ] **Step 5: Verify adapters and replay**

Run: `uv run pytest tests/queue tests/oracle -v`

Expected: deterministic CVAT/Label Studio round-trips, crash replay reaches same state, forged/duplicate/out-of-bounds/wrong-manifest input rejected, audit logs contain `simulated_oracle`.

**Artifact/evidence produced:** queue/event schema, interchange adapters, oracle replay and adversarial tests.

**Stop condition:** Invalid transition, forged reveal, partial/future label leak, non-idempotent replay, or any human-performance field appears.

**Commit boundary:** `feat: add simulated oracle queue`

---

### Task 7: Orchestrate atomic acquisition rounds and seal Wave 3

**Objective:** Compose scoring, selection, queue, oracle, cost, and training-manifest updates into a crash-safe replayable round for all five arms.

**Files:**
- Create: `src/vision_active_learning_loop/orchestration/rounds.py`
- Create: `src/vision_active_learning_loop/orchestration/idempotency.py`
- Create: `src/vision_active_learning_loop/gates/wave3.py`
- Create: `schemas/round-receipt.schema.json`
- Create: `schemas/wave3-gate-receipt.schema.json`
- Create: `tests/orchestration/test_rounds.py`
- Create: `tests/gates/test_wave3_gate.py`
- Create: `docs/runbooks/wave3.md`

**Interfaces:**
- Produces: `RoundRunner.run(request: RoundRequest) -> RoundReceipt`
- Produces: `RoundRunner.replay(receipt_digest: str) -> RoundReceipt`
- Produces: `evaluate_wave3(receipts: Sequence[RoundReceipt]) -> Wave3GateReceipt`
- CLI: `val acquire round --request <json> --output-root <external-path>`

- [ ] **Step 1: Write failing crash/idempotency/five-arm tests**

```python
def test_crash_before_publish_replays_same_receipt(runner, request):
    runner.fail_after("oracle_reveal")
    runner.run_expect_crash(request)
    assert runner.run(request).digest == runner.clean_run(request).digest

def test_gate_requires_exact_five_arms(receipts):
    assert evaluate_wave3(receipts_without("margin")).status == "FAIL"
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/orchestration/test_rounds.py tests/gates/test_wave3_gate.py -v`

Expected: missing orchestration/gate modules.

- [ ] **Step 3: Implement atomic phase journal**

Phases are `score → select → queue → oracle → validate → acquired → cost → next_training_manifest`. Each phase has input/output digest and compare-and-swap state. Final receipt publishes only after all phases validate; partial selection cannot become an input.

- [ ] **Step 4: Replay one synthetic round for every arm**

Run: `uv run val acquire replay-fixture --fixture fixtures/synthetic/acquisition --output-root artifacts/wave3/replay`

Expected: five unique deterministic receipts, exact selected sequences/golden explanations, correct budgets/cost ledgers, no hidden/test data, and identical replay hashes.

- [ ] **Step 5: Run the Wave 3 gate and stop**

Run: `uv run pytest tests/acquisition tests/queue tests/oracle tests/orchestration tests/gates/test_wave3_gate.py -v && uv run val gate wave3 --receipt-root artifacts/wave3/replay --output artifacts/wave3/wave3-gate.json`

Expected: all tests pass and gate `PASS`, including exact CPU fixture/canonical GPU sequence tests and evaluator denial. Report commits/evidence and stop before pilot.

**Artifact/evidence produced:** phase journal, five-arm replay receipts, Wave 3 gate and owner review packet.

**Stop condition:** Any arm/sequence/budget/queue/cost/idempotency/firewall invariant fails.

**Commit boundary:** `feat: seal acquisition round orchestration`
