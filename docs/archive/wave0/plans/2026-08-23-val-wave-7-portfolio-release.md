# Wave 7 Reviewer and Portfolio Release Implementation Plan

> **Historical 8-wave protocol.** Preserved for provenance; this is not the current task queue. The original Wave 0 gate did not pass. The separately approved lite research completed its v0.3 five-strategy first comparison on 2026-09-12; see the [current README](../../../../README.md) and [v0.3 results](../../../results/2026-09-12-v0.3-diversity.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the sealed experiment into a five-minute, evidence-linked portfolio artifact whose local public-export candidate contains no restricted data, secrets, unsupported claims, or oversized artifacts.

**Architecture:** A synthetic reviewer bundle replays all five strategies and evidence lineage without GPU/RDD access. Machine cards and a claim matrix are generated from Wave 6 receipts; README/static diagrams point to those artifacts. CI validates CPU fast path and public-boundary scans, while a clean-export gate stops before any GitHub/remote/tag/Release/publication action.

**Tech Stack:** CPU-only Python reviewer environment; pytest; Markdown/Mermaid; JSON/Parquet aggregate tables; static PNG/SVG charts; secret/license/large-file scanners; OCI CPU test image.

## Global Constraints

- Entry requires Wave 6 PASS and owner approval.
- Reviewer fast path must finish within five minutes on CPU without RDD/model download, GPU, network, sealed paths, or local absolute paths.
- Public evidence may contain source code, schemas, configs, original synthetic fixtures, aggregate tables/charts, permitted hashes/IDs, and documentation.
- Public evidence may not contain RDD pixels/annotations/crops/thumbnails, embeddings, model weights/checkpoints, per-item sealed predictions, credentials, host paths, or large caches.
- Claims must match the machine `ClaimDecision`, including negative/mixed/insufficient outcomes.
- Wheel/sdist is created only if a recorded review proves installation outside the repository is useful; otherwise document `NOT_PACKAGED_YAGNI`.
- GitHub Repo creation, remote, push, tag, Release, and publication remain owner-approved actions after this wave, not steps in it.

---

### Task 1: Build the deterministic five-minute reviewer fixture and replay

**Objective:** Demonstrate strategy differences, budgets, queue, leakage checks, curves, and lineage on original synthetic data in one CPU command.

**Files:**
- Create: `fixtures/synthetic/reviewer/manifest.json`
- Create: `fixtures/synthetic/reviewer/raw-query-outputs.json`
- Create: `fixtures/synthetic/reviewer/embeddings.json`
- Create: `fixtures/synthetic/reviewer/precomputed-evidence.json`
- Create: `src/vision_active_learning_loop/reviewer/fast_path.py`
- Create: `tests/reviewer/test_fast_path.py`
- Create: `tests/reviewer/test_fixture_provenance.py`

**Interfaces:**
- Produces: `run_fast_path(fixture_root: Path, output_root: Path) -> ReviewerReceipt`
- CLI: `val reviewer fast-path --fixture fixtures/synthetic/reviewer --output artifacts/reviewer`

- [ ] **Step 1: Write failing offline/time/coverage tests**

```python
def test_fast_path_is_offline_cpu_only(run):
    assert run.network_calls == 0 and run.cuda_calls == 0 and run.rdd_paths == []

def test_fast_path_replays_exact_five_arms(run):
    assert set(run.arm_sequences) == {"random", "entropy", "margin", "core_set", "hybrid_uncertainty_diversity"}
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/reviewer/test_fast_path.py tests/reviewer/test_fixture_provenance.py -v`

Expected: missing reviewer fixture/module.

- [ ] **Step 3: Create original synthetic evidence**

Include 300-query cases reduced to compact generated tensors, a small 384-D embedding matrix, equal/near-boundary distance keys, capture groups, queue events, cost ledger, precomputed three-seed curves/calibration/compute examples, and fake sealed annotations for traversal tests. Manifest asserts `origin=project_generated` and hashes every file.

- [ ] **Step 4: Implement one-command replay**

Replay all arms, explain entropy/localization and nearest-center decisions, verify nested budgets/ties/queue/artifact hashes, run fake firewall attacks, render static precomputed tables/curves, and trace each display to a receipt. CPU core-set uses precomputed keys/reference fixture and explicitly disclaims full-data cross-hardware identity.

- [ ] **Step 5: Verify time/offline/evidence**

Run: `uv run pytest tests/reviewer/test_fast_path.py tests/reviewer/test_fixture_provenance.py -v && uv run val reviewer fast-path --fixture fixtures/synthetic/reviewer --output artifacts/reviewer`

Expected: tests pass, command exits 0 within 300 seconds on CPU, no network/GPU/RDD, five-arm exact sequences, and reviewer receipt lists every check.

**Artifact/evidence produced:** committed tiny fixture, fast-path code/tests, reviewer receipt and static demo outputs.

**Stop condition:** Runtime >5 minutes, external access occurs, fixture provenance is unclear, or any replay/evidence check fails.

**Commit boundary:** `feat: add five minute reviewer fast path`

---

### Task 2: Generate claim-to-evidence matrix and four cards

**Objective:** Make every portfolio claim traceable to immutable evidence and document model/data/benchmark/system limitations.

**Files:**
- Create: `src/vision_active_learning_loop/reporting/cards.py`
- Create: `reports/claim-to-evidence.json`
- Create: `MODEL_CARD.md`
- Create: `DATA_CARD.md`
- Create: `BENCHMARK_CARD.md`
- Create: `SYSTEM_CARD.md`
- Create: `LIMITATIONS.md`
- Create: `tests/reporting/test_cards.py`
- Create: `tests/reporting/test_claim_matrix.py`

**Interfaces:**
- Produces: `build_claim_matrix(claim_decision, wave_receipts, result_tables) -> ClaimMatrix`
- Produces: `render_cards(claim_matrix, cards_config) -> CardManifest`

- [ ] **Step 1: Write failing unsupported-claim and required-card tests**

```python
def test_every_claim_has_machine_evidence(matrix):
    assert all(claim.evidence_digests and claim.decision_clause for claim in matrix.claims)

def test_negative_decision_cannot_render_positive_headline(input_bundle):
    input_bundle.claim_decision.status = "mixed"
    with pytest.raises(UnsupportedClaim):
        render_cards(input_bundle.with_headline("reduces labeling cost"))
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/reporting/test_cards.py tests/reporting/test_claim_matrix.py -v`

Expected: missing card/matrix implementation or files.

- [ ] **Step 3: Implement evidence-linked card generation**

Model card covers pinned detector/encoder, training/calibration, intended use. Data card covers countries/roles, CC BY-SA treatment, nonredistribution, exclusions/dedup/groups. Benchmark card covers arms/seeds/budgets/66+6+9, metrics/censoring/compute/results. System card covers trust/mount/embargo/queue/artifacts. Limitations include simulated oracle, n=3, fixed model, dataset/shift, calibration insufficiency, and negative-result interpretation.

- [ ] **Step 4: Generate and verify cards**

Run: `uv run val report cards --wave6 <receipt> --results <aggregate-root> --output-root . && uv run pytest tests/reporting/test_cards.py tests/reporting/test_claim_matrix.py -v`

Expected: five documents plus matrix/card manifest; every number/claim links to evidence digest; no human savings, universal/production, or shift-rescue claim.

**Artifact/evidence produced:** four cards, limitations, machine claim matrix and tests.

**Stop condition:** Claim lacks evidence, result status is altered, restricted data is embedded, or limitation is omitted.

**Commit boundary:** `docs: add evidence linked project cards`

---

### Task 3: Write README first impression and architecture/reproduction docs

**Objective:** Give a reviewer a clear problem/result/system story and exact fast/full reproduction boundaries without presenting a dashboard.

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/reproduction.md`
- Create: `docs/artifact-lineage.md`
- Create: `docs/images/architecture.svg`
- Create: `tests/docs/test_readme_contract.py`
- Create: `tests/docs/test_links.py`

**Interfaces:**
- README command: `uv run val reviewer fast-path --fixture fixtures/synthetic/reviewer --output artifacts/reviewer`
- Full commands reference wave runbooks and require external roots/receipts; they never auto-download data.

- [ ] **Step 1: Write failing README/link/copy tests**

```python
def test_readme_leads_with_question_result_and_fast_path(readme):
    assert ordered_headings(readme)[:3] == ["Research question", "Result", "Five-minute review"]

def test_ceiling_name_is_exact(readme):
    assert "100% acquired-budget ceiling" in readme
    assert "100% training ceiling" not in readme
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/docs/test_readme_contract.py tests/docs/test_links.py -v`

Expected: missing docs/tests fail.

- [ ] **Step 3: Write evidence-first README and docs**

README states actual claim status, individual-seed/static curves, rare-class/calibration/shift/compute findings, simulated-oracle limitation, exact five-minute command, and links to cards. Architecture diagram shows Wave 0 receipt→global manifest→queue/training→66 seal→one evaluation batch→public evidence, including sealed boundaries.

- [ ] **Step 4: Document reproduction boundaries**

Separate CPU reviewer reproduction from owner-authorized full data/GPU reproduction. Require terms acknowledgement, external roots, model/dataset receipts, owner gates, and no automatic RDD/GitHub action.

- [ ] **Step 5: Verify links/copy/diagram source**

Run: `uv run pytest tests/docs/test_readme_contract.py tests/docs/test_links.py -v`

Expected: all links resolve locally, diagram has accessible text description, exact terminology/counts/claims match machine evidence.

**Artifact/evidence produced:** README, architecture SVG/source description, reproduction and lineage docs.

**Stop condition:** Fast path is obscured, claim differs from receipt, link breaks, or full reproduction can bypass approval/data terms.

**Commit boundary:** `docs: add portfolio first impression`

---

### Task 4: Add CPU CI, container boundary, and packaging decision

**Objective:** Verify the public candidate in a clean CPU environment while keeping GPU/data tests explicit and deciding package distribution by demonstrated value.

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `docker/reviewer.Dockerfile`
- Create: `scripts/verify_public_candidate.ps1`
- Create: `scripts/verify_public_candidate.sh`
- Create: `docs/packaging-decision.md`
- Create: `tests/release/test_ci_boundary.py`

**Interfaces:**
- CI commands: lock check, unit tests excluding `gpu/data/restricted`, docs/link tests, reviewer fast path, public-boundary scan.
- Packaging decision values: `NOT_PACKAGED_YAGNI` or `PACKAGE_APPROVED_WITH_EVIDENCE`.

- [ ] **Step 1: Write failing CI-boundary tests**

```python
def test_public_ci_never_downloads_models_or_rdd(ci_yaml):
    assert forbidden_network_or_data_steps(ci_yaml) == []

def test_gpu_tests_are_explicitly_excluded_from_public_ci(ci_yaml):
    assert "not gpu and not restricted and not data" in ci_yaml
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/release/test_ci_boundary.py -v`

Expected: missing workflow/decision.

- [ ] **Step 3: Implement clean CPU verification**

Reviewer image installs the lock’s CPU-compatible subset, runs unit/docs/fast-path/public scans with network disabled after build, and contains no model/data cache. Windows and shell scripts execute equivalent checks.

- [ ] **Step 4: Record packaging decision**

Measure whether reviewers need installation outside the repo. Default to `NOT_PACKAGED_YAGNI`, with reasons and no wheel/sdist. Only choose `PACKAGE_APPROVED_WITH_EVIDENCE` after owner approval and tests proving install/uninstall/import/CLI value; this does not authorize publication to an index.

- [ ] **Step 5: Verify workflow/container boundary**

Run: `uv run pytest tests/release/test_ci_boundary.py -v && powershell -File scripts/verify_public_candidate.ps1`

Expected: CPU checks pass, no restricted/network/GPU step occurs, packaging status is explicit.

**Artifact/evidence produced:** local CI workflow candidate, reviewer Dockerfile, verification scripts, packaging decision.

**Stop condition:** CI needs model/RDD/GPU/secret, or a distribution artifact is built/published without approval/evidence.

**Commit boundary:** `ci: verify public reviewer boundary`

---

### Task 5: Perform clean-export, license, secret, privacy, and large-file audit

**Objective:** Build a local export candidate from tracked content and mechanically reject every restricted or unsupported artifact.

**Files:**
- Create: `src/vision_active_learning_loop/release/audit.py`
- Create: `configs/release/public-boundary.yaml`
- Create: `schemas/public-export-receipt.schema.json`
- Create: `tests/release/test_public_audit.py`
- Create: `docs/publication-checklist.md`

**Interfaces:**
- Produces: `audit_public_tree(root, policy) -> PublicExportReceipt`
- CLI: `val release audit --tree <clean-export-path> --policy configs/release/public-boundary.yaml --output <receipt>`

- [ ] **Step 1: Write failing restricted/secret/size/path tests**

```python
@pytest.mark.parametrize("fixture", ["rdd_pixel", "annotation", "checkpoint", "embedding", "secret", "absolute_path", "oversize"])
def test_public_audit_rejects_forbidden_fixture(auditor, fixture):
    assert auditor.scan(fixture_tree(fixture)).status == "FAIL"
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/release/test_public_audit.py -v`

Expected: missing audit module/policy.

- [ ] **Step 3: Implement clean export and scanners**

Use `git archive` into a new external temporary directory, then scan magic bytes/extensions/content for images from non-synthetic provenance, RDD annotations/classes/paths, archives, model/checkpoint/embedding formats, per-item sealed predictions, secrets/tokens/emails beyond approved author, Windows/WSL host paths, symlinks, binary blobs, and files >5 MiB unless explicitly allowlisted static evidence with digest/license.

- [ ] **Step 4: Verify license/attribution and claims**

Require code license, `DATA_LICENSES.md`, upstream attribution, model licenses, card/claim matrix, and no RDD redistribution. Re-run prohibited phrase/fit/scope checks against docs.

- [ ] **Step 5: Generate local export receipt**

Run: `uv run pytest tests/release/test_public_audit.py -v && uv run val release audit --tree <clean-export-path> --policy configs/release/public-boundary.yaml --output <public-export-receipt.json>`

Expected: tests pass and clean candidate receipt `PASS` lists all files/digests/licenses/sizes and zero findings. No remote is added.

**Artifact/evidence produced:** local clean export, machine public-export receipt, publication checklist.

**Stop condition:** Any restricted/secret/path/large/license/claim finding remains.

**Commit boundary:** `feat: audit clean public export`

---

### Task 6: Issue Portfolio Complete gate and stop before publication

**Objective:** Validate reviewer, cards, docs, CI, clean export, and evidence lineage, then request separate owner decisions for each publication action.

**Files:**
- Create: `src/vision_active_learning_loop/gates/wave7.py`
- Create: `schemas/portfolio-complete-receipt.schema.json`
- Create: `tests/gates/test_wave7_gate.py`
- Create: `docs/runbooks/wave7.md`

**Interfaces:**
- Produces: `evaluate_wave7(inputs: Wave7Inputs) -> PortfolioCompleteReceipt`
- CLI: `val gate wave7 --wave6 <receipt> --reviewer <receipt> --cards <manifest> --public-export <receipt> --output <receipt>`

- [ ] **Step 1: Write failing publication-separation and completeness tests**

```python
def test_portfolio_complete_does_not_authorize_publication(receipt):
    assert receipt.github_created is False
    assert receipt.push_authorized is False
    assert receipt.tag_authorized is False
    assert receipt.release_authorized is False

def test_missing_claim_evidence_fails(inputs):
    inputs.claim_matrix.claims[0].evidence_digests = []
    assert evaluate_wave7(inputs).status == "FAIL"
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/gates/test_wave7_gate.py -v`

Expected: missing gate.

- [ ] **Step 3: Implement Portfolio Complete validation**

Require Wave 6, reviewer <=300s/offline, cards/limitations/claim matrix, README/docs/link/diagram tests, CI boundary, packaging decision, clean public export, attribution/license, clean Git, and exact artifact lineage. Receipt records actual result/claim status and publication booleans all false.

- [ ] **Step 4: Run full public-candidate verification**

Run: `uv run pytest -m "not gpu and not restricted and not data" -v && uv run val reviewer fast-path --fixture fixtures/synthetic/reviewer --output artifacts/reviewer && uv run val gate wave7 --wave6 <receipt> --reviewer <receipt> --cards <manifest> --public-export <receipt> --output <portfolio-complete.json>`

Expected: all CPU/public checks pass and Portfolio Complete status `PASS`, with no remote/tag/release/publication side effect.

- [ ] **Step 5: Stop and request distinct owner decisions**

Report commit range, Portfolio Complete/public-export/reviewer/claim digests, actual project result, limitations, packaging status, and clean Git state. Ask separately whether to create GitHub Repo, add/push remote, tag `v0.1.0`, create Release, or publish elsewhere. Do not combine silence or one approval into the others.

**Artifact/evidence produced:** Portfolio Complete receipt and owner publication-decision packet.

**Stop condition:** Any completion input fails or an external publication action lacks its own explicit owner approval.

**Commit boundary:** `docs: seal portfolio complete evidence`
