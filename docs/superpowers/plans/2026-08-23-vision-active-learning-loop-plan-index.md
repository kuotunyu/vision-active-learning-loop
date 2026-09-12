# Vision Active Learning Loop Implementation Plan Suite Index

> **Historical 8-wave protocol.** Preserved for provenance; this is not the current task queue. The original Wave 0 gate did not pass. The separately approved lite research completed its v0.3 five-strategy first comparison on 2026-09-12; see the [current README](../../../README.md) and [v0.3 results](../../results/2026-09-12-v0.3-diversity.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved active-learning experiment as eight review-gated implementation waves without allowing dataset access, formal evaluation, or publication to outrun their protocol prerequisites.

**Architecture:** A small Python library and thin CLI produce immutable, schema-validated, content-addressed artifacts. Trust domains are separated into curator, strategy/trainer, oracle, and embargoed evaluator processes; large or restricted artifacts live in host volumes outside Git. The only executable starting point is Wave 0, whose synthetic model-contract receipt gates every later wave.

**Tech Stack:** Windows 11 host; WSL2 Ubuntu 24.04 and OCI containers for canonical execution; Python 3.12.11; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; pycocotools 2.0.10; RTX 4090 24 GB.

## Global Constraints

- Normative source: `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at the approved baseline and its approval-status commit.
- Detector: `PekingU/rtdetr_r18vd` revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`, safetensors SHA-256 `fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093`.
- Encoder: `facebook/dinov2-small` revision `ed25f3a31f01632728cabb09d1542f84ab7b0056`, safetensors SHA-256 `ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1`.
- Source domains are Japan, India, Czech Republic, and China MotorBike; China Drone is shift-only. US, Norway, and every other dataset are excluded.
- Formal seeds are exactly `17`, `29`, and `43`; budgets are 2%, 5%, 10%, 20%, 40%, and the 100% acquired-budget ceiling.
- Formal arms are exactly random, entropy, margin, core-set, and hybrid uncertainty/diversity.
- Fit counts are 9 pilot fits, 66 primary fits, and 6 label-noise auxiliary fits.
- RTX 4090 is canonical. Colab is non-canonical and cannot fill a formal gap or enter timing aggregates.
- Raw RDD images/annotations, candidate thumbnails, checkpoints, model weights, embeddings, per-item test predictions, and sealed labels never enter Git.
- No source-test or China Drone output may exist before a valid `formal_completion_seal`.
- A normative change requires owner review, a new protocol version, and invalidation of incompatible artifacts.
- GitHub repository creation, push, tag, Release, and publication each require separate owner approval.

---

## 1. Suite control and milestone mapping

M0 is already complete. The remaining design milestones and implementation waves are deliberately not one-to-one at M2 because data/firewall and model/training foundations need separate reviewer gates.

| Design milestone | Implementation wave | Status/meaning |
|---|---|---|
| M0 Protocol and license lock | Planning baseline before Wave 0 | Complete when owner-approved spec and this suite are committed |
| M1 Executable model contract | Wave 0 | Synthetic-only feasibility and fail-closed model contract |
| M2 Data, model, and firewall foundation | Wave 1 + Wave 2 | Wave 1 freezes lawful/leak-free data roles; Wave 2 builds training/embedding foundations on that manifest |
| M3 Acquisition and queue | Wave 3 | Five strategies, deterministic selection, simulated-oracle queue |
| M4 Pilot and freeze | Wave 4 | Nine pilot fits, cost gates, protocol freeze |
| M5 Embargoed formal execution | Wave 5 | 66 primary fits and completion seal without test output |
| M6 One-shot evaluation and robustness | Wave 6 | Sealed evaluation batch, six noise fits, analysis |
| M7 Portfolio release | Wave 7 | Reviewer path and public-boundary audit; publication remains separately approved |

## 2. Dependency DAG and critical path

```text
approved spec + approved plan suite
  → Wave 0 PASS receipt
    → owner review + explicit Wave 1 data-access approval
      → Wave 1 dataset/firewall manifest PASS
        → owner review
          → Wave 2 model/training foundation PASS
            → owner review
              → Wave 3 acquisition/queue PASS
                → owner review
                  → Wave 4 pilot/projection/freeze PASS
                    → owner review + explicit formal-run approval
                      → Wave 5 all 66 artifacts + formal_completion_seal
                        → owner review + explicit evaluator-unseal approval
                          → Wave 6 evaluation/robustness report PASS
                            → owner review
                              → Wave 7 portfolio evidence PASS
                                → separate owner decisions for GitHub/push/tag/Release/publication
```

No later wave may start because its code looks independent. Cross-wave execution is serial. Within a wave, CPU-only schema/tests may be developed in parallel after shared interfaces land, but artifacts are accepted only through that wave’s single exit receipt. All RTX jobs serialize through one GPU lease; CPU report preparation may run while a GPU job is active only when it cannot read embargoed outputs or mutate that job’s inputs.

## 3. Wave register

| Wave | Plan | Tasks | Entry condition | Exit evidence | Stop gate |
|---:|---|---:|---|---|---|
| 0 | `2026-08-23-val-wave-0-model-contract-feasibility.md` | 6 | Owner approves plan suite | Passing model-contract and feasibility receipts from two clean runs | Any model/output/determinism/hash invariant fails |
| 1 | `2026-08-23-val-wave-1-data-firewall.md` | 7 | Wave 0 PASS + owner approves RDD access and host roots | Dataset lineage, global-dedup, split, firewall, invalidation receipts | License/checksum mismatch, cross-role leakage, or hidden-label access |
| 2 | `2026-08-23-val-wave-2-detector-encoder-training.md` | 6 | Wave 1 PASS manifest | Detector/encoder/training/calibration receipts on synthetic/tiny data | Test/shift access, resume mismatch, or recipe divergence |
| 3 | `2026-08-23-val-wave-3-acquisition-queue.md` | 7 | Wave 2 PASS | Exact five-arm replay and queue/round receipts | Sequence mismatch, budget error, oracle leakage, non-idempotence |
| 4 | `2026-08-23-val-wave-4-pilot-freeze.md` | 5 | Waves 0–3 PASS + owner approves nine pilot fits | Pilot report and signed protocol-freeze receipt | Any Section 12 gate fails, any slowest round >15 min, projected fits >240 h |
| 5 | `2026-08-23-val-wave-5-formal-execution.md` | 5 | Wave 4 PASS + owner approves formal run | Exactly 66 checkpoint/ledger hashes and valid completion seal | Test output appears, GPU lease conflict, artifact gap, protocol mismatch |
| 6 | `2026-08-23-val-wave-6-evaluation-robustness.md` | 7 | Valid completion seal + owner approves unseal | Atomic evaluation/result/robustness receipts | Seal/input mismatch, partial output exposure, retry input change |
| 7 | `2026-08-23-val-wave-7-portfolio-release.md` | 6 | Wave 6 PASS | Five-minute reviewer bundle and clean public-export receipt | Restricted/secret/large file found or claim lacks evidence |

Expected implementation commits are 49 task commits: `6 + 7 + 6 + 7 + 5 + 5 + 7 + 6`. A task may use an additional corrective commit after review, but commits cannot combine waves or rewrite the approved protocol history.

## 4. Resource and owner-approval matrix

| Wave | CPU/RAM | RTX 4090 | Dataset | Network | Additional owner approval |
|---:|---|---|---|---|---|
| 0 | 8+ cores, 32 GB recommended | Required for contract/BF16/VRAM smoke | Forbidden | Official Python/model/container sources only | Approve executing Wave 0 and dependency/model downloads |
| 1 | 16+ cores, 64 GB recommended for hashing/audit | Required only for DINO audit embedding | RDD approved countries only | Official RDD source after explicit approval | Approve `VAL_DATA_ROOT`, `VAL_ARTIFACT_ROOT`, terms acknowledgement, download |
| 2 | 8+ cores, 32 GB | Required | Frozen Wave 1 manifests; tiny fixture for tests | No new model identity | Approve Wave 2 after Wave 1 receipt |
| 3 | 8+ cores, 32 GB | Required for canonical k-center tests | Public pool view + acquired labels only | None required | Approve Wave 3 |
| 4 | 16+ cores, 64 GB | Required for 9 fits/benchmarks | Pilot partition only | None required | Approve GPU pilot and protocol freeze |
| 5 | 16+ cores, 64 GB | Exclusive lease for 66 fits | Formal pool/acquired labels; tests sealed | None required | Approve projected GPU-hours and formal execution |
| 6 | 16+ cores, 64 GB | Evaluation and 6 noise fits | Test/shift accessible only to evaluator | None required | Approve evaluator unseal after seal verification |
| 7 | 8+ cores, 32 GB | Not required for fast path | Synthetic/public aggregate evidence only | Needed only after publication approval | Approve GitHub creation, push, tag, Release, publication separately |

`OWNER_DECISION_REQUIRED` before Wave 1: choose and record absolute host paths for `VAL_DATA_ROOT` and `VAL_ARTIFACT_ROOT`, confirm sufficient storage, and accept the upstream RDD terms. This choice is operational and cannot place either root inside the Git worktree.

## 5. Environment boundary

- **Windows 11 host:** owns the RTX driver, WSL2 distribution, Docker Desktop/engine lifecycle, host-only raw and artifact volumes, and recovery backups.
- **WSL2 Ubuntu 24.04:** canonical shell/filesystem semantics for tests and CLI; translates approved Windows host roots to `/mnt/...` only through validated real paths.
- **OCI container:** canonical Python/CUDA execution; image is pinned by digest after Wave 0. Strategy/trainer containers receive allowlisted mounts and no sealed evaluator paths.
- **Native Windows Python:** permitted only for CPU reviewer-path and path-policy compatibility tests. It cannot produce formal selections, fits, timings, or completion evidence.
- **Native Linux/Colab:** portability smoke only. It cannot satisfy formal gates or merge timing/seed results with canonical evidence.
- Every `val ...` interface is registered through Wave 0's AST-built lazy command manifest. Discovery records module/callable metadata without importing command modules; trainer images therefore cannot import evaluator modules merely by constructing the CLI. Duplicate command paths and missing callables fail the build.

## 6. Planned storage and mount tree

The absolute root choices require owner approval; the logical structure is fixed:

```text
<VAL_DATA_ROOT>/                              # restricted, never Git
  raw/rdd/<upstream_release_digest>/
    source_candidates/{Japan,India,Czech,China_MotorBike}/
    shift_candidates/China_Drone/
    archives/
  sealed/oracle/formal_pool_annotations/
  sealed/evaluator/source_test/
  sealed/evaluator/china_drone_shift/
  public_pool/images_by_item_id/

<VAL_ARTIFACT_ROOT>/                          # derived/private, never Git
  wave0/model_cache/
  wave0/receipts/
  curation/audit_embeddings/
  manifests/{dataset,exclusions,splits,calibration}/
  embeddings/<manifest_digest>/
  queue/<experiment_id>/
  checkpoints/<experiment_id>/
  training_receipts/<experiment_id>/
  completion_seals/<experiment_id>/
  evaluator_write_only/<completion_seal_digest>/
  results/<completion_seal_digest>/
  invalidated/<protocol_version>/<experiment_id>/

<REPOSITORY_ROOT>/                            # public-candidate Git content
  src/vision_active_learning_loop/
  tests/
  configs/
  schemas/
  fixtures/synthetic/
  docs/
  reports/aggregate/
```

Formal trainer/strategy mounts are limited to `public_pool`, acquired queue labels, the relevant checkpoint inputs, and output directories. Evaluator mounts are limited to frozen checkpoints, sealed evaluator roots, and a write-only result directory. Git ignores the two host roots, common model/data/checkpoint suffixes, and any generated per-item result.

## 7. Authoritative artifact and evidence lineage

| Authority order | Artifact | Producer | Required consumers |
|---:|---|---|---|
| 1 | `model_contract_receipt.json` + environment lock | Wave 0 probe | Every later manifest/run |
| 2 | `dataset_lineage_manifest.json` + exclusions/splits | Wave 1 curator | Waves 2–6 |
| 3 | embedding/training/checkpoint schema receipts | Wave 2 | Waves 3–6 |
| 4 | acquisition/queue ledgers | Wave 3/5 orchestrators | Training, completeness, analysis |
| 5 | `protocol_freeze_receipt.json` | Wave 4 gate | Wave 5 matrix |
| 6 | 66 checkpoint/manifest/ledger hash inventory | Wave 5 | Completion sealer |
| 7 | `formal_completion_seal.json` | Wave 5 sealer | Sole Wave 6 unseal capability |
| 8 | atomic evaluation and robustness tables | Wave 6 evaluator/analyst | Wave 7 claims |
| 9 | public-export receipt and claim matrix | Wave 7 | Owner publication decision |

Every artifact contains schema version, protocol version, parent digests, Git commit, dirty-state flag, environment digest, timestamps, and a content hash. An input mismatch is an error; it is never repaired by editing a receipt.

## 8. Protocol invalidation

Invalidate the experiment ID and move its mutable pointer into `invalidated/` when any of these occurs:

1. a normative invariant or hash changes after its wave receipt;
2. global duplicate review finds a new cross-source/shift component after model execution;
3. a group crosses roles or hidden labels reach strategy/trainer code;
4. a formal selection sequence differs from the canonical/reference rule;
5. a formal recipe, seed, budget, model, environment, or manifest differs from the freeze receipt;
6. source-test or China Drone output exists before `formal_completion_seal`;
7. an evaluator retry uses non-identical inputs; or
8. a public bundle contains restricted data or unsupported claims.

Repairing implementation-only bugs before protocol freeze requires rerunning the affected wave and review. A normative change returns to design review. After freeze, any incompatible change requires a new protocol version, new experiment ID, and full downstream rerun.

## 9. RTX 4090 lease, scheduling, and resume

- A host-level atomic lease file records lease ID, PID/container ID, GPU UUID, experiment/job ID, start/heartbeat time, and expiry. Only one canonical job owns the RTX.
- Stale leases are reclaimed only after the recorded process/container is absent and an audit event is written.
- GPU jobs write to a temporary content-addressed directory and atomically publish only after validation; partial outputs are never accepted as inputs.
- Resume requires identical job manifest, model/config/environment hashes, acquired IDs, optimizer/scheduler/RNG states, and expected epoch/step. A mismatch starts a new job ID.
- Wave 5 uses a precomputed job DAG: per seed, shared 2% first; arm rounds sequential within an arm; independent ready jobs across arms/seeds queue behind the one-GPU lease; the three acquired-budget ceilings are one per seed.
- Training may resume; acquisition selection may only replay an already committed receipt or restart from identical inputs. It cannot resume from a partially written ordered list.

## 10. Public GitHub boundary

Permitted public candidates are source code, schemas, configs without secrets/host paths, synthetic fixtures, aggregate tables, static charts, plan/spec/docs, cards, model/data upstream identifiers/hashes, and acquisition IDs/hashes permitted by the data policy. Forbidden are RDD pixels/annotations/crops/thumbnails, model weights, embeddings, checkpoints, per-item sealed predictions, local paths, credentials, environment secrets, and large generated caches.

Wave 7 may produce a clean export candidate locally. Creating `https://github.com/kuotunyu/vision-active-learning-loop`, adding a remote, pushing, tagging, releasing, or publishing remains outside every plan until separately approved.

## 11. Human review checkpoints

At each exit, stop and give the owner: commit(s), receipt digest, test summary, artifact inventory, resource actuals, failed attempts, deviations, invalidations, and the next wave’s requested authority. Silence or elapsed schedule never counts as approval. Wave 0 is the only wave that may be proposed for execution after this plan suite is approved.

## 12. Normative spec coverage matrix

| Approved spec section | Implementation tasks |
|---|---|
| §1 Executive decision and portfolio differentiation | Wave 6 Tasks 5–7; Wave 7 Tasks 1–3, 6 |
| §2 Goals, non-goals, permitted claims | Wave 3 Tasks 1–7; Wave 6 Tasks 5–7; Wave 7 Tasks 2, 5–6 |
| §3 Dataset/license/taxonomy | Wave 1 Tasks 1–2, 5; Wave 7 Tasks 2, 5 |
| §4 Global dedup, grouping, splits, leakage | Wave 1 Tasks 2–7 |
| §5 Fixed model/software and executable contract | Wave 0 Tasks 1, 3–6; Wave 2 Tasks 1–2 |
| §6 Seeds, budgets, shared start, 66 fits, training recipe | Wave 2 Tasks 3–4; Wave 4 Tasks 1, 4–5; Wave 5 Tasks 1, 3–5 |
| §7 Five acquisition strategies and numerical contract | Wave 3 Tasks 1–5, 7; Wave 4 Tasks 2–4 |
| §8 Oracle firewall, queue, formal embargo | Wave 1 Task 6; Wave 3 Tasks 6–7; Wave 5 Tasks 3–5; Wave 6 Tasks 1, 3, 7 |
| §9 Calibration and confidence | Wave 2 Tasks 3, 5–6; Wave 5 Tasks 3–5; Wave 6 Tasks 3, 6 |
| §10 Metrics, curves, class/country, compute | Wave 4 Tasks 3–4; Wave 6 Tasks 3, 5–7 |
| §11 Noise and distribution shift | Wave 6 Tasks 2–7 |
| §12 Pilot, gates, conservative projection | Wave 4 Tasks 1–5 |
| §13 Reproducibility, canonical hardware, lineage | Index §§5–9; Wave 0 Tasks 1–2, 5–6; every wave exit gate |
| §14 Reviewer fast path | Wave 7 Tasks 1, 3–4 |
| §15 Milestones and release boundary | Index §§1–4, 11; Wave 0–7 exit gates |
| §16 Risks and mitigations | Corresponding negative/adversarial tests and stop gates in Waves 0–7 |
| §17 Statistical reporting | Wave 6 Tasks 4–7 |
| §18 Acceptance checklist | Plan-suite self-review; Wave 7 Tasks 5–6 |
| §19 Protocol invalidation/version changes | Index §8; Wave 1 Task 7; Wave 4 Task 5; Wave 5 Tasks 3–5 |

## 13. Plan-suite completion gate

This suite is ready for owner review only when all nine plan files exist, every normative spec section maps to a task, no plan opens the evaluator early, fit counts remain 9/66/6, large/restricted artifacts stay outside Git, and no task adds a seed, arm, detector, encoder, dataset, segmentation, pseudo-labeling, domain adaptation, annotation UI, cloud orchestration, or publication action.
