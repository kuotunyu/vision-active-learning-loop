# Vision Active Learning Loop — Formal Design Specification

**Status:** A11 independently calibrated same-host statistical-replay written-spec review pending
**Milestone:** M0 complete for the original design; A6 remains frozen at `WAVE0_A6_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; the A10-bound A7 campaign is closed at `WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`
**Owner approval date:** 2026-08-23
**Approved commit baseline:** `8b456800077d45fa9a6bb0dcd4ecb70c0edc89c6`
**A2 amendment authorization date:** 2026-08-24
**A2 amendment baseline:** `97d5789c0ca657f58e79f761a353f275e97a147b`
**A3 amendment authorization date:** 2026-08-25
**A3 amendment baseline:** `db0dc52e10d5e58852b84e1d321c2efa06a82d30`
**A4 amendment authorization date:** 2026-08-25
**A4 amendment baseline:** `fb9d0bbbf7a494babe4546637a2b5cd56f320bb2`
**A5 amendment authorization date:** 2026-08-25
**A5 amendment baseline:** `502c0dc8e755a8ba49cf038c8a66ad8a5e6293fd`
**A6 amendment authorization date:** 2026-08-25
**A6 amendment baseline:** `979aa63893971ba979f030fdda52a4fa5746f520`
**A7 amendment authorization date:** 2026-08-25
**A7 amendment baseline:** `efe5cee58931e8e8bb85292b4c48701ec2e32c9b`
**A7 launcher-hardening authorization date:** 2026-08-26
**A7 launcher-hardening baseline:** `a5c193061c43a3aaf7dcc5652f1d3e0a009c00c1`
**A8 lifecycle-amendment authorization date:** 2026-08-27
**A8 lifecycle-amendment baseline:** `0e8086cfa5fc67fe3ef784b0f67f634398ff81ea`
**A11 delegated design-decision date:** 2026-08-27
**A11 design baseline:** `2cb3e38b4328eee2b3497571e05565c73f4691c9`
**Original specification date:** 2026-08-23
**Repository:** `vision-active-learning-loop`
**Target roles:** Computer Vision Engineer, Machine Learning Engineer, AI Engineer
**Design choice:** Modified Option B — multi-country object-detection active learning
**Runtime gate:** Wave 0 must verify every executable model-contract invariant from a new run-scoped evidence chain. The environment, model-contract, and feasibility receipts must share a non-empty run identity and exact parent bindings; each runtime observation must independently report uv `0.8.15` and SciPy `1.18.0`. Historical or fixed-name evidence is never current by implication. The only permitted nondeterministic CUDA operation is the exact A3 backward exception in Section 5.2.5. Section 5.2.8 requires RT-DETR labeled forward and backward to run with only the deterministic SDPA Math backend enabled before that narrow exception is exercised. The closed A6 campaign failed the unchanged registered numerical replay bounds. Sections 5.2.9 through 5.2.14 define and harden the completed A7 causal diagnostic; no A7 outcome is a Wave 0 pass. Section 5.2.15 replaces neither that evidence nor the pinned training stack: it defines one separately calibrated same-host numerical envelope and one independent holdout validation, with exact discrete replay, non-vacuity ceilings, and an explicit prohibition on bitwise-determinism claims.
**Implementation status:** The owner's persistent unattended delegation authorizes the recommended A11 design decision and this docs-only specification amendment. It does not authorize an A11 implementation plan, implementation, Docker build, GPU campaign, RDD access, Wave 1, remote operation, or publication. Those transitions remain subject to the written-spec and later candidate/execution gates in Section 5.2.15.

## 1. Executive decision

This project will answer one narrow, falsifiable question:

> Under a fixed road-damage annotation budget, do uncertainty, diversity, or uncertainty-plus-diversity acquisition strategies train an object detector more label-efficiently than deterministic random acquisition?

The project uses four source domains—Japan, India, Czech Republic, and China MotorBike—from the Road Damage Detection dataset. It trains one fixed four-class detector, compares five acquisition arms over nested image budgets, repeats the formal experiment with three seeds, and evaluates both a frozen in-domain source test and an untouched China Drone distribution-shift test.

The project is intentionally an experimental system rather than a model-zoo or notebook demonstration. Its portfolio value comes from reproducible acquisition logic, a sealed oracle boundary, group-aware leakage controls, budget curves, calibration, rare-class behavior, robustness audits, compute accounting, and honest negative-result rules.

### 1.1 Portfolio overlap decision

The scope is sufficiently distinct from the existing CV portfolio when the active-learning loop remains the product:

| Existing project | Principal emphasis | Deliberate separation in this project |
|---|---|---|
| `mvtec-ad2-inspection-platform` | Industrial anomaly-inspection platform | No anomaly segmentation, MVTec benchmark, or inspection dashboard |
| `DefectForge` | Defect-oriented data/model workflow | No synthetic defect generation or general defect workbench |
| `SafeSynth` | Safety and synthetic-data concerns | No synthetic-data generation or synthetic-to-real study |
| `pcb-defect-detection` | PCB-specific supervised detection | Road damage, multi-country shift, and annotation acquisition are the core contribution |
| `WoundScope` | Medical/wound vision application | No medical imaging, clinical framing, or wound UI |

It would become overly repetitive if reduced to “train another detector and report mAP.” The non-negotiable differentiators are the oracle firewall, five reproducible acquisition arms, multi-seed budget curves, label-efficiency metrics, group-aware split integrity, calibration, and shift evaluation.

### 1.2 Scope alternatives considered

| Option | Shape | Strength | Principal weakness | Decision |
|---|---|---|---|---|
| A. Classification active learning | Image-level road-damage presence/type | Fastest and easiest to validate | Avoids box annotation economics and understates CV engineering depth | Rejected |
| B. Object-detection active learning | Acquire images, reveal all boxes, retrain detector | Strongest alignment with CV/ML roles and measurable labeling economics | More compute and a harder uncertainty contract | **Selected, with constraints in this specification** |
| C. Anomaly/inspection active learning | Unsupervised or one-class anomaly inspection | Industrial framing | Overlaps the existing anomaly portfolio and makes oracle/metric comparisons less clean | Rejected |

## 2. Goals, non-goals, and claims

### 2.1 Goals

1. Compare random, entropy, margin, core-set, and hybrid acquisition under identical data, initialization, training recipe, and budgets.
2. Measure detection performance against both acquired images and revealed boxes, not only at the final budget.
3. Demonstrate that selection code cannot inspect unrevealed annotations or evaluation labels.
4. Quantify rare-class discovery, calibration, country selection patterns, compute cost, label noise sensitivity, and domain shift.
5. Produce reproducible artifacts that a reviewer can understand in five minutes without a GPU or full dataset.

### 2.2 Non-goals

The first release excludes:

- image classification, segmentation, anomaly detection, and synthetic defect generation;
- pseudo-labeling, semi-supervised learning, domain adaptation, active domain balancing, and continual learning;
- detector or backbone model-zoo comparisons;
- per-box acquisition or partial image annotation;
- a full inspection application, annotation editor, or large dashboard;
- collection of real annotator timing, inter-annotator agreement, or human-cost claims;
- the United States RDD subset while its Google imagery terms remain unsuitable for this project;
- the Norway subset because its approximately 9.9 GB footprint is outside the approved v0.1 scope;
- redistribution of RDD pixels or annotations through GitHub or Hugging Face.

### 2.3 Permitted conclusions

The primary conclusion is descriptive and seed-paired. “Reduced labeling cost” may be stated only when all of the following hold:

1. hybrid normalized source-test AUBC is greater than random in all three formal seeds;
2. every seed has a conclusive target-cost comparison under the censoring truth table in Section 10.4, and hybrid satisfies that table’s image-and-box requirement against random;
3. hybrid minimum-class recall and D40 recall at 40% are each no more than 3.0 absolute percentage points below random in any seed;
4. no censored target is reported as observed attainment or an exact savings value; the sole permitted censored interpretation is `SUPPORTIVE` under Section 10.4’s lower-bound checks; and
5. China Drone results are reported separately and are not used to rescue an in-domain failure.

If any seed is `INSUFFICIENT`, or if any other condition is not met, “reduced labeling cost” is prohibited as a headline claim and the result is reported as mixed, negative, or insufficient as appropriate. No claim of universal superiority, production readiness, or human labor savings is allowed.

## 3. Data contract and licensing

### 3.1 Dataset decision

The sole image/annotation source is the official Road Damage Detection corpus maintained by the Sekilab RoadDamageDetector project. The authoritative discovery pages for this project are the [official repository](https://github.com/sekilab/RoadDamageDetector) and its linked competition/dataset records.

| RDD subset | Role | Included in training acquisition? | Included in evaluation? |
|---|---|---:|---:|
| Japan annotated train | Source | Yes | Frozen source test portion |
| India annotated train | Source | Yes | Frozen source test portion |
| Czech annotated train | Source | Yes | Frozen source test portion |
| China MotorBike annotated train | Source | Yes | Frozen source test portion |
| China Drone annotated train | Shift-only | No | Entire curated shift test |
| United States | Excluded | No | No |
| Norway | Excluded in v0.1 | No | No |
| Any other RDD country or split | Excluded | No | No |

Only the annotated training portions are used because the experiment requires a trusted oracle to replay labels. Public challenge test labels are not inferred or repurposed.

### 3.2 License interpretation and redistribution policy

The official RDD documentation identifies its images under [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/). Some secondary dataset catalogs describe portions as CC BY 4.0. This project adopts the stricter **CC BY-SA 4.0** treatment for all included RDD data and preserves the source’s attribution and share-alike notices. This is a conservative engineering policy, not legal advice.

The data package will not be committed, mirrored, vendored, attached to a release, or uploaded to Hugging Face. A future downloader may retrieve files only from the official source after the user affirmatively invokes it. It must show attribution/terms, record upstream URLs, verify registered SHA-256 checksums, and stop on a mismatch. The repository may contain:

- code under its separately declared code license;
- `DATA_LICENSES` documentation and upstream attribution;
- manifest schemas, country/category mappings, expected archive checksums, and source URLs;
- irreversible content hashes, experiment IDs, aggregate metrics, and selected image identifiers; and
- tiny synthetic fixtures created by this project.

It may not contain RDD pixels, XML/JSON annotations, cropped defects, thumbnails, embedded base64 images, or enough annotation content to reconstruct the dataset. Reports must use diagrams, synthetic examples, or aggregate statistics unless an upstream license-compliant display decision is reviewed separately.

The US subset remains excluded because its imagery provenance includes Google Street View restrictions that are not resolved by the RDD license statement. Norway remains a documented future extension, not an implicit download.

### 3.3 Annotation taxonomy

The detector predicts exactly the standard four RDD damage classes:

| ID | Class | Description |
|---:|---|---|
| 0 | D00 | Longitudinal crack |
| 1 | D10 | Transverse crack |
| 2 | D20 | Alligator crack |
| 3 | D40 | Pothole |

Country labels are metadata for slicing and auditing. They are never detector targets and are not visible to a strategy unless the public manifest explicitly contains them. The formal strategies do not force country balance.

## 4. Manifest, duplicate control, and frozen splits

### 4.1 Global identity, duplicate control, and grouping

Every candidate image across Japan, India, Czech Republic, China MotorBike, and China Drone receives a canonical `item_id = SHA256(pixel_file_bytes)`. Paths and filenames are not experimental identities. Duplicate discovery is performed once over the **joint source-plus-shift universe**, before any source, pilot, formal-pool, source-test, or shift role is assigned:

1. Exact SHA-256 matches are unioned globally.
2. A perceptual hash uses 16×16 pHash (256 bits). Images within Hamming distance 6 form global connected components, and a curator verifies every proposed component contact sheet.
3. A DINOv2 neighbor audit searches the complete retained source-plus-shift candidate universe and flags pairs with cosine similarity at least 0.995 for manual review. A confirmed pair is unioned into a reviewed near-duplicate component; it is not left as a diagnostic warning.
4. If an exact, pHash-confirmed, or DINO-confirmed component spans any source country and China Drone, the **entire conflicting component** is excluded from every training and evaluation role. Each member records `cross_source_shift_exact_duplicate`, `cross_source_shift_phash_duplicate`, or `cross_source_shift_dino_duplicate` as its exclusion reason.
5. If a component does not cross the source/shift boundary, only its lexicographically smallest `item_id` is retained; other members are recorded as excluded aliases.
6. When official metadata or a validated filename parser exposes a route, sequence, video, or capture-session identifier, all retained images from that capture receive the same `split_group_id`.
7. Otherwise, `split_group_id` is the retained image’s `item_id`. The fallback is explicit and counted in the data card. A group ID is the minimum member `item_id`, and a group can never cross partitions.

The pHash threshold, parser version, review decisions, exclusion ledger, and manifest digest are frozen before any acquisition scoring, detector training, pilot fit, or formal fit/evaluation. The only model executions allowed earlier are the synthetic Section 5.2 contract probe and the label-blind DINOv2 pass required for this global duplicate audit. Audit vectors are bound first to upstream archive/item hashes; only retained rows are then filtered and rebound to the final manifest digest for diversity use. A newly confirmed DINO neighbor before experimental execution invalidates the unused manifest, applies the global component rule, and generates a new manifest digest. Discovery after any pilot or formal model run invalidates that entire protocol version and experiment ID; the run cannot continue by editing the manifest in place.

### 4.2 Deterministic partition rule

For each source `split_group_id`, compute:

```text
r = uint64(SHA256("val-loop-split-v1" || split_group_id)[0:8]) mod 10000
```

Assign the entire group as follows:

| Hash interval | Partition | Purpose |
|---|---|---|
| 0000–1999 | frozen source test (20%) | Primary in-domain evaluation only |
| 2000–2799 | pilot engineering pool (8%) | Pilot gate only; never formal training/test |
| 2800–9999 | formal acquisition pool (72%) | Formal active-learning experiment |

After the global duplicate pass, retained China Drone annotated-train images form the shift test in full; none can enter a source partition. The partition receipt proves that every exact/pHash/reviewed-neighbor component is contained in one role and that no retained component crosses source and shift.

The trusted data curator performs one pre-model coverage audit after the deterministic split. It reports image and box counts by country/class, fallback-group rate, group sizes, and duplicate exclusions. The split is not redrawn to improve a model result. If a source country is absent from either formal pool or source test, or if a test class has zero boxes, the experiment is blocked and the split algorithm must be revised as a new protocol version before any formal run. The invalid split is retained in the audit record rather than silently retried.

### 4.3 Leakage rules

- Joint source-plus-shift duplicate control and source splitting finish before acquisition scoring, detector training, pilot fits, or formal fits/evaluation; only the synthetic contract probe and label-blind DINO duplicate-audit pass may precede them.
- Source test and China Drone labels are evaluation-only and never used for model choice, calibration, early stopping, threshold choice, acquisition, or pilot tuning.
- Pilot images and labels never enter the formal pool, source test, shift test, pretrained base, or formal calibration sets.
- Every artifact declares its input manifest digest. A mismatched digest is a hard error.
- The same image or duplicate component cannot appear in multiple partitions.
- A capture group cannot cross partitions. To avoid a single drive dominating a selection batch, acquisition admits at most one image from a capture group per batch on the first pass, then deterministically fills from remaining ranked items if necessary to meet the exact image budget.

## 5. Fixed model and software stack

### 5.1 Detector

The sole detector is **RT-DETR-R18** loaded from [`PekingU/rtdetr_r18vd`](https://huggingface.co/PekingU/rtdetr_r18vd) at revision:

```text
cc5b50f32f0100caaa3bd275343e2fb17762c73d
```

The `model.safetensors` artifact is 80,904,152 bytes with SHA-256:

```text
fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093
```

The checkpoint and Transformers implementation are Apache-2.0 licensed. RT-DETR is selected because it exposes a fixed set of 300 decoder queries and raw class/box outputs, making the acquisition contract auditable without NMS or a score-threshold-dependent number of detections. Every class-dependent detector component listed in Section 5.2 is reset with one seed-deterministic initialization stream; no replacement module reuses, copies, or selects COCO class-head rows.

The interpretation is pinned to [Transformers 5.15.0 RT-DETR documentation](https://huggingface.co/docs/transformers/v5.15.0/en/model_doc/rt_detr). That implementation trains class outputs with focal-loss-style independent sigmoid probabilities. It does **not** provide a native mutually exclusive no-object softmax class. Section 7 therefore defines a derived and explicitly labeled background probability rather than claiming a model-native no-object logit.

### 5.2 Release-blocking executable model-contract probe

Generated documentation in Transformers 5.15.0 describes a no-object-inclusive output dimension, while the pinned focal-loss execution path uses independent foreground logits. Documentation is therefore not accepted as the executable contract. After the dependency/model lock but **before any RDD archive is processed, any embedding is computed, or any pilot/formal model runs**, a synthetic-input probe must execute the exact pinned checkpoint revision and Transformers 5.15.0 source.

#### 5.2.1 A2 trigger and pinned-source finding

The first Option A feasibility-A attempt, run ID `option-a-20260824T134408p0800-boundary-replay`, stopped with `WAVE0_NORMATIVE_FAIL` before publishing a feasibility receipt or checkpoint. Its exact labeled-forward error was:

```text
The size of tensor a (80) must match the size of tensor b (4) at non-singleton dimension 2
```

The failure record remains immutable at stored SHA-256 `ef6f55609f6a6db0281206c8e434c39fa3407399bc7c7f0db4312c5293677507` and content SHA-256 `0896d4edcfd281749dfd04215cb09ae518e74d39645ec61b08c5792607778122`. The preceding Option A environment and label-free model-contract receipts remain historical records of the narrower contracts they actually evaluated; they are neither overwritten nor reinterpreted as A2 evidence.

The root cause is a class-dependent reset-contract omission, not an RTX 4090, RT-DETR-R18, SciPy, or dataset feasibility failure. The previous reset changed `model.model.decoder.class_embed`, `model.model.denoising_class_embed`, and the label mappings, but left `model.model.enc_score_head` at its pretrained 80-class width. The pinned official Transformers 5.15.0 source establishes the complete data flow:

1. [`RTDetrModel` constructs `enc_score_head` from `config.num_labels`](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py#L1457-L1463).
2. [That head produces `enc_outputs_class`, whose selected rows become `enc_topk_logits`](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py#L1677-L1694).
3. [A labeled object-detection forward passes `enc_topk_logits` into the RT-DETR loss](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py#L1849-L1870).
4. [With auxiliary loss enabled, the RT-DETR loss appends `enc_topk_logits` to the auxiliary outputs evaluated against the same labels](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/loss/loss_rt_detr.py#L433-L467).
5. [`RTDetrLoss` binds its class count to `config.num_labels` and creates the classification target at that width](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/loss/loss_rt_detr.py#L147-L195), so the old 80-channel encoder tensor is incompatible with the frozen four-class target.

The official Transformers 5.15.0 wheel source inspected for this amendment has `modeling_rt_detr.py` SHA-256 `fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3` and `loss_rt_detr.py` SHA-256 `01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6`. Both hashes, not generated documentation alone, are normative source inputs to the A2 receipt.

#### 5.2.2 Complete four-class reset contract

The detector, model revision, processor, 300 queries, dependency versions, and frozen RDD label order remain unchanged. Under one RNG scope seeded exactly once with `contract_probe_seed = 17`, every replacement is created and initialized in this exact RNG-consumption order, with no intervening random initialization or per-module reseeding:

1. each `model.model.decoder.class_embed[index]`, in ascending `index` order;
2. `model.model.denoising_class_embed`; and
3. `model.model.enc_score_head`.

Every replacement preserves the corresponding original module's device and dtype, as well as its input or embedding dimension and bias presence where applicable. It must satisfy all of the following:

- every `model.model.decoder.class_embed[index]` is a newly initialized linear module with `out_features == 4`;
- `model.model.denoising_class_embed` is a newly initialized embedding with `num_embeddings == 5` and `padding_idx == 4`;
- `model.model.enc_score_head` is a newly initialized linear module with `out_features == 4`;
- `model.config.num_labels == 4`;
- `model.config.id2label == {0: "D00", 1: "D10", 2: "D20", 3: "D40"}`; and
- `model.config.label2id == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}`.

No replacement may copy or select any row, bias, embedding, or other class-specific value from the pretrained 80-class COCO heads. Initialization follows the pinned RT-DETR convention: decoder and encoder classification weights use Xavier uniform initialization; their biases use `p = config.initializer_bias_prior_prob or 1 / (config.num_labels + 1)` and `-log((1 - p) / p)`; the denoising embedding uses Xavier uniform initialization and its padding row remains zero. The applicable pinned conventions are the official [decoder, encoder, and denoising initialization source](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py#L1003-L1062).

#### 5.2.3 Label-free and labeled executable invariants

The A2 probe uses only the original synthetic fixtures and synthetic four-class targets. It performs both a label-free forward and a labeled forward; no RDD bytes, annotations, label counts, or dataset paths are permitted. It is release-blocking and must verify all of these invariants:

- `config.num_queries == 300`;
- every structural and mapping invariant in Section 5.2.2 is true, including exact module paths, device, dtype, initialization order, and absence of reused COCO rows;
- final `logits.shape == [2, 300, 4]` and `pred_boxes.shape == [2, 300, 4]`;
- every layer in `intermediate_logits` has final dimension 4;
- `enc_outputs_class` and `enc_topk_logits` each have final dimension 4;
- every decoder, encoder, and denoising auxiliary classification tensor reachable by `RTDetrForObjectDetectionLoss` has final dimension 4;
- no reachable classification tensor in the pinned labeled-loss data flow has final dimension 80 or any class width other than 4;
- a labeled forward over valid synthetic four-class targets produces a finite scalar loss;
- the acquisition accessor’s native foreground scores equal elementwise `sigmoid(logits)` for all four channels and never invoke the postprocessor’s non-focal softmax path; the only softmax permitted is the explicitly project-derived conditional `pi_qc` in Section 7.3, computed after preserving the independent sigmoid scores;
- there is no fifth native logit and no tensor channel is misidentified as native no-object;
- in `eval()` plus `torch.inference_mode()` with no labels, `intermediate_reference_points` is available with exact shape `[2, config.decoder_layers, 300, 4]`, where `config.decoder_layers >= 2`;
- final boxes equal `intermediate_reference_points[:, -1, :, :]` exactly, and the localization term uses penultimate boxes `intermediate_reference_points[:, -2, :, :]`;
- source-structure assertions against the pinned file verify that decoder layers are stacked on axis 1 without a query-axis gather, sort, or permutation, so query index `q` has the same correspondence at the penultimate and final layers;
- the fixed processor is configured with bilinear aspect-preserving `size={"max_height": 640, "max_width": 640}`, `do_pad=true`, `pad_size={"height": 640, "width": 640}`, zero fill, `do_rescale=true`, `rescale_factor=1/255`, and `do_normalize=false`; its observed `pixel_values.shape == [2, 3, 640, 640]`, `pixel_mask.shape == [2, 640, 640]`, and mask extents match the expected resized regions; and
- the label-free call contains no annotations, targets, or label-derived counts, while the labeled call receives only the registered synthetic targets.

The expected intermediate tensor order follows the pinned [RT-DETR source](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py), where decoder outputs are stacked as `[batch, decoder_layer, query, coordinate]` and final boxes are the last layer. The sigmoid assertion follows the pinned [RT-DETR image processor source](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/image_processing_rt_detr.py), not the contradictory generated output prose.

The probe emits a schema-validated, machine-readable `model_contract_receipt` containing the model repository/revision, canonical config JSON SHA-256, safetensors SHA-256, Transformers package version and source-tree commit/hash, hashes of the RT-DETR model/config/processor/loss source files, observed module identities and tensor shapes from both paths, processor JSON and its SHA-256, synthetic-input and synthetic-target fixture digests, probe source SHA-256, timestamp, canonical environment fingerprint, invariant-by-invariant booleans, and final `PASS`/`FAIL`. The receipt itself is content-addressed and becomes an input to every later manifest and run.

The existing BF16 backward, finite-gradient, parameter-update, peak-VRAM, checkpoint round-trip, and clean A/B replay gates remain mandatory. A3 changes only the executable meaning of the CUDA backward determinism gate as specified in Section 5.2.5, A4 changes only the canonical Python-source hashing rule as specified in Section 5.2.6, A5 adds only failure-path warning observability as specified in Section 5.2.7, and A6 fixes the labeled training step to the deterministic SDPA Math backend as specified in Section 5.2.8; the finite labeled-forward invariant continues to supplement rather than replace the training gates. A5 diagnostic evidence cannot satisfy or weaken any training, replay, or aggregate gate. Any failed or unobservable invariant halts the protocol. The detector, uncertainty formula, extractor, package, or checkpoint cannot be changed ad hoc; a different contract requires a new reviewed spec version, new probe, and new receipt.

#### 5.2.4 No-clobber and evidence-preservation invariants

Every subsequent A3, A4, A5, or A6 execution uses a new run ID and a new run-scoped evidence chain. Before any A3, A4, A5, or A6 feasibility process starts, both its exact checkpoint destination and its checkpoint root must not exist. Either pre-existing path is a fail-closed condition: it cannot be reused, cleaned, merged, or overwritten by the run.

Receipt publication uses atomic no-clobber semantics. A separate existence check followed by an overwriting replace is insufficient because it permits a check-then-replace race. The destination-creating filesystem operation itself must fail atomically when the destination already exists; if the target filesystem cannot provide that guarantee, publication stops without changing the destination. Temporary publication artifacts remain run-unique and cannot make a failed receipt appear current.

All earlier commits, OCI images, receipts, checkpoints, logs, failure records, and audit corrections remain immutable historical evidence. No prior `FAIL` can be rewritten as `PASS`, and no prior narrower `PASS` can satisfy A3, A4, A5, or A6 by implication. A5 is an evidence-recovery protocol only: its failure log cannot be promoted to an A4 or A6 feasibility receipt, replay result, or aggregate result, and it does not authorize reinterpretation or retry of the closed A4 campaign. The complete A5 campaign is also immutable and cannot be rerun, modified, or reinterpreted as proof that any training gate passed.

Existing whole-tree Black and Ruff debt is outside the A3/A4/A5/A6 correction boundary. A future A3, A4, A5, or A6 implementation may change only files required by these invariants and must run targeted formatting, lint, and tests over those touched files; broad formatting, unrelated cleanup, and refactoring are prohibited.

#### 5.2.5 A3 bounded CUDA determinism contract

The fresh A2 campaign `wave0-a2-20260825T025943120Z`, bound to source commit `db0dc52e10d5e58852b84e1d321c2efa06a82d30` and OCI image `sha256:9b43ab192f1014f960c8db1d0ea1da1a559dd4005250e5fb6e4aa2716d3f47e3`, passed environment, model-assets, and the complete four-class model contract, then failed during feasibility-A backward before publishing a feasibility receipt or checkpoint. The preserved stage record has SHA-256 `2dc1585974a86c02a1b02f7ba92c419ea3ccd8c90455c8c9a79a65b92b4a1fc8`; the stage log has SHA-256 `28fc5121e2ccfa55fe55bf24d6b7f74704e3dfece16873aa192f0589fa125ea4`; and the no-clobber failure record has SHA-256 `c0889697ba23b9ec775d7f66d47c2542c5f4c128f7309149db283ca8294f630f`. Its terminal verdict remains `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.

The exact error identifies `grid_sampler_2d_backward_cuda`. This is a pinned-stack capability conflict, not evidence corruption or a detector/reset failure:

1. Transformers 5.15.0 `MultiScaleDeformableAttention.forward` calls `torch.nn.functional.grid_sample` once per decoder layer and feature level, using bilinear mode, zero padding, and `align_corners=False`.
2. The pinned RT-DETR config has `decoder_layers == 3`, `num_feature_levels == 3`, and `disable_custom_kernels == true`; one labeled backward therefore reaches exactly `3 × 3 = 9` fallback grid-sample backward operations.
3. PyTorch 2.12.0 documents CUDA `torch.nn.functional.grid_sample` differentiation among the operations that throw when `torch.use_deterministic_algorithms(True, warn_only=False)` is active; its grid-sample documentation separately states that CUDA backward may be nondeterministic and cannot be easily switched off.
4. Full detector and backbone fine-tuning necessarily differentiates through deformable attention. Freezing the transformer, using CPU backward, changing detector identity, or introducing an unpinned custom kernel would change the approved research model more materially than a narrow, measured exception.

The A3 amendment originally registered Transformers `modeling_rt_detr.py` raw-file SHA-256 `fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3`, PyTorch `torch/__init__.py` raw-file SHA-256 `b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9`, and PyTorch `torch/nn/functional.py` raw-file SHA-256 `e409a97896241e0dfb8c23fbf1f09967ecf5e65ec9626aec0d97d9cc5d727d50`. Section 5.2.6 records that the two PyTorch values were taken from the Windows wheel's CRLF bytes rather than the canonical Linux wheel. They remain historical A3 inputs and cannot satisfy A4; the corrected canonical source-hash contract in Section 5.2.6 supersedes only those values and their hashing rule.

A3 retains RT-DETR-R18, the pinned model revision and assets, 300 queries, four RDD classes, full detector/backbone optimization, BF16, RTX 4090 execution, dependency versions, seeds, datasets, budgets, acquisition arms, fit counts, and all non-determinism-related gates. It permits one exception under these fail-closed rules:

- strict deterministic error mode remains active for initialization, preprocessing, labeled forward, loss construction, gradient clipping, optimizer/scheduler steps, checkpointing, and every operation outside `loss.backward()`;
- immediately around `loss.backward()` only, deterministic algorithms remain enabled but unsupported operations emit warnings instead of throwing;
- warning capture uses `warnings.simplefilter("always")`; after backward the probe restores strict deterministic error mode even when backward raises;
- the normalized operation identifier inventory must contain exactly nine occurrences of `grid_sampler_2d_backward_cuda`, derived as `decoder_layers × num_feature_levels`; zero, an incorrect count, a different identifier, an unparsable warning, or any additional nondeterministic warning is a normative failure;
- every raw warning message, normalized identifier, warning category, count, pinned PyTorch source hash, and pinned Transformers deformable-attention source hash is recorded in the feasibility receipt; and
- the allowed exception is called `allowlisted_grid_sample_backward`, never `deterministic`, and cannot support a claim of bitwise-identical training.

The six feasibility observations—primary A/B, clean-a A/B, and clean-b A/B—must use one non-empty A3 run ID and the same exact source, image, model, processor, config, dependency, and semantic environment identities. Every observation validates the exact content hash of its own parent chain; parent receipt hashes are not required to equal across independently created attempts. Attempt IDs, container IDs, paths, timestamps, durations, receipt content hashes, and checkpoint file hashes are observational and may differ. Using primary A as the canonical observation, every other observation must match it exactly on:

- pre-update trainable-parameter digest and ordered parameter inventory;
- synthetic input, target, item-order, fixture, and sampler digests;
- scalar forward loss in hexadecimal representation;
- optimizer parameter-group names, learning rates, weight decay, scheduler state before update, RNG states after update, warning inventory, and all discrete checkpoint fields; and
- model-state key order, tensor shapes, tensor dtypes, integer/bool tensors, and non-training buffers.

Each run still requires finite loss and gradients, a finite clipped gradient norm, a real parameter update, BF16 autocast, TF32 disabled, peak allocated VRAM at most 22 GiB, and an exact within-run checkpoint save/load round-trip. Checkpoint file hashes and post-update floating-state digests remain content-addressed identities for their own runs but are observational, not required to be equal across runs.

An A3 feasibility receipt uses `schema_version == 2`. In addition to the retained A2 evidence, its normative payload requires an `allowlisted_backward` object, an ordered `parameter_inventory`, per-group `update_groups`, and an `exact_comparison` object that excludes only the disclosed post-backward floating model/optimizer values. An A3 aggregate Wave 0 gate receipt also uses `schema_version == 2`; it exposes `exact_comparisons`, structured `numerical_replay_comparisons`, and separate invariants for the warning allowlist, exact replay fields, and registered numerical bounds. A feasibility or gate receipt with schema version 1 is immutable historical evidence and cannot satisfy A3, even if every field it knows is internally valid.

For the post-backward floating update, the gate compares each of the five non-canonical observations with primary A over the exact ordered trainable-parameter inventory. Let `delta_r` be the concatenated post-update minus pre-update vector for replay `r`; because the pre-update digest is exact, `||delta_r - delta_primary||_2` can be reproduced from the two post-update checkpoints. The single global pre-clip gradient norm must satisfy the first bound below. Detector and backbone parameter-update groups must separately satisfy the second and third bounds:

```text
gradient_norm: math.isclose(rel_tol=1e-5, abs_tol=1e-7)
relative_update_l2 = ||delta_r - delta_primary||_2 / max(||delta_r||_2, ||delta_primary||_2) <= 1e-3
update_cosine = <delta_r, delta_primary> / (||delta_r||_2 ||delta_primary||_2) >= 0.99999
```

The gate also compares the checkpointed AdamW `exp_avg` and `exp_avg_sq` tensors by optimizer group and state name. Their ordered parameter-to-state mapping, shapes, and dtypes must be exact; each nonzero concatenated floating state must independently satisfy `relative_state_l2 <= 1e-3` and `state_cosine >= 0.99999`, using the same formulas as the update-vector bounds. Missing, unexpected, or non-finite optimizer state fails closed.

Every norm is accumulated in canonical parameter-name order using CPU float64. A zero, non-finite, missing, reordered, shape-mismatched, or dtype-mismatched update fails closed. The receipt records per-group update L2 norms and the gate records the pairwise difference, relative L2, and cosine values for model updates and optimizer states. These thresholds are fixed before any A3 GPU execution and cannot be adjusted after observing a run; changing them requires another reviewed protocol version and a new run ID. Passing A3 supports only the claim that the pinned full-training step is seed-controlled and numerically replayable within these registered same-host bounds despite one disclosed CUDA operation. It does not support bitwise training identity.

#### 5.2.6 A4 canonical Python-source provenance contract

The fresh A3 campaign `wave0-a3-20260825T044614674Z`, bound to source commit `fb9d0bbbf7a494babe4546637a2b5cd56f320bb2` and OCI image `sha256:6693aa3b79d495eba50b5b4d70a460533baff5f127880cb021165cccbbabfa4c`, passed its Docker/Linux/RTX 4090 preflight, pinned model-asset verification, and complete four-class model contract. It then failed closed in primary feasibility-A before `loss.backward()`, feasibility receipt publication, or checkpoint creation with `bounded-backward source hash mismatch: torch_init`. Feasibility-B, clean-a, clean-b, and the aggregate gate did not start. The preserved stage log has SHA-256 `bae7311548e1844b08202577453678c9c7ce4b81fe386e05533dbf53cd4e9686`, the stage record has SHA-256 `a02cb235dfcf99c2ee76e7daeaffb92720bd03e3a6cacc659a286d885072d230`, the source-hash diagnostic has SHA-256 `ef29b3dc49ebf7aa9c80e0a35035705c7c2138fc52de7f65880caabd2e54b742`, and the closure manifest has SHA-256 `35259e1400b1f7c837956943a151e26b2a4f759549a2ae400d7718dc7ec50e9f`. Its terminal verdict remains `WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN` and cannot be retried, deleted, modified, or reinterpreted as a pass.

The root cause is a platform newline provenance error, not dependency, image, CUDA, model, or evidence drift. `uv.lock` pins `torch-2.12.0+cu126-cp312-cp312-manylinux_2_28_x86_64.whl` at SHA-256 `792711a06946fa1dcd1a86d46c387dd413744b9324262ff77c05f61830d0e678`. All six inspected Wave 0 Linux OCI images contain identical PyTorch source bytes: `torch/__init__.py` is 109,312 bytes with SHA-256 `d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49`, and `torch/nn/functional.py` is 263,236 bytes with SHA-256 `27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19`. Those values match the installed Linux wheel's `RECORD` entries. The same pinned Windows wheel sources are respectively 112,357 and 270,189 bytes because they use CRLF; replacing CRLF with LF produces the exact Linux byte lengths and hashes. Transformers `modeling_rt_detr.py` already has identical bytes and SHA-256 on both platforms.

A4 therefore defines one platform-independent but fail-closed source-content rule named exactly `python-source-lf-normalized-sha256-v1`:

1. Resolve the three exact source paths through the already pinned imports: `torch.__file__`, `torch.nn.functional.__file__`, and `inspect.getsourcefile(RTDetrForObjectDetection)`.
2. Each path must exist as a regular file and must not be a symlink, junction, or other reparse point. A missing path, duplicate logical name, unexpected inventory entry, or non-regular path fails before the backward callback can run.
3. Read the source as bytes. Replace every CRLF byte pair (`0d 0a`) with LF (`0a`), then replace every remaining lone CR byte (`0d`) with LF. Do not decode or re-encode text, strip a BOM, trim whitespace, rewrite tabs, normalize Unicode, or make any other transformation.
4. Compute SHA-256 over those canonical bytes and require this exact closed mapping:

```text
torch_init                         d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49
torch_nn_functional                27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19
transformers_modeling_rt_detr      fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3
```

Only newline representation is intentionally erased. Any source token, comment, spacing, encoding byte, or other content change remains hash-visible and fails closed. On the canonical Linux runtime, the normalized digests equal the raw wheel-file digests; Windows CPU tests exercise the same semantic source identity without substituting a platform-specific allowlist.

Every A4 feasibility receipt must keep `schema_version == 2` and add `source_hash_rule == "python-source-lf-normalized-sha256-v1"` inside its closed `allowlisted_backward` object next to the exact `source_sha256` mapping. The receipt schema, semantic validator, runtime invariant derivation, and exact replay preimage must all require the rule and exact mapping; missing, extra, renamed, raw-Windows, wrong-rule, or wrong-hash evidence fails. The rule and mapping must match exactly across primary A/B, clean-a A/B, and clean-b A/B because the complete `allowlisted_backward` object remains an exact replay field. Schema version 2 is retained because A3 stopped before publishing any feasibility-v2 receipt or checkpoint; the immutable A3 logs and manifests remain failure evidence, while any old v2-shaped synthetic document without the new required rule cannot satisfy A4.

A4 implementation is limited to the source-hash calculation and its receipt/schema validation surfaces. Its exact tracked-file allowlist is `src/vision_active_learning_loop/probes/training_feasibility.py`, `src/vision_active_learning_loop/artifacts/receipts.py`, `schemas/feasibility-receipt.schema.json`, and `tests/probes/test_training_feasibility.py`; needing any fifth implementation file stops for another written scope review. TDD must first demonstrate that the current raw-byte implementation produces different hashes for CRLF and LF representations of otherwise identical pinned Python source. The completed tests must prove that LF, CRLF, and lone-CR newline encodings produce the same registered canonical digest; a one-byte non-newline content change fails; source inventory, regular-file, symlink/junction, hash-rule, exact-mapping, and callback-before-verification boundaries remain fail closed; and the stored feasibility receipt cannot omit or contradict the rule. No Dockerfile, dependency, `uv.lock`, model, dataset, seed, budget, fit count, numerical replay threshold, warning identifier/count/category, no-clobber rule, or historical evidence may change.

After an A4 implementation candidate passes focused and complete CPU suites, targeted Black/Ruff, `uv lock --check`, `git diff --check`, historical-evidence rehashing, and a Critical=0/Important=0 review, it receives one append-only commit. A fresh OCI image bound to that commit must pass a CPU-only source-contract micro-check before any GPU lease is acquired. Only then may one never-used A4 run ID execute primary, clean-a, clean-b, and the aggregate Wave 0 gate once. All attempt, receipt, checkpoint, campaign, audit, and lease paths must be fresh and no-clobber. Any source-contract, Docker, GPU, feasibility, checkpoint, numerical replay, evidence, or aggregate failure preserves the new campaign and stops without another fix or retry. A successful A4 Wave 0 campaign still stops at `WAVE0_A4_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`; RDD access and Wave 1 require separate owner authorization.

#### 5.2.7 A5 diagnostic-only warning observability contract

The fresh A4 campaign `wave0-a4-20260825T074134919Z`, bound to source commit `502c0dc8e755a8ba49cf038c8a66ad8a5e6293fd` and OCI image `sha256:be9a8a75065cbc8cc22834dab60bea11932893bb12b4df0092b42caffc734108`, passed its Linux/RTX 4090 preflight, canonical source-contract micro-check, environment receipt, pinned model-asset verification, and complete four-class model contract. Primary feasibility-A then returned exit code 2 with `unparsable deterministic backward warning` before publishing a feasibility receipt or checkpoint. Feasibility-B, clean-a, clean-b, and the aggregate gate did not start. The stage log has SHA-256 `9357e9976b09d5428861f5912d541af1f082afd96b47d960ca510ebe1576ad3f`, the stage record has SHA-256 `a3bab1d3dcb4184eedf2ca10dadbee6860e5135d7809fd3bb7a43b2ee90cac36`, the warning-contract diagnostic has SHA-256 `08070bb1d0f3dc26aae3a2bbd93f3ee28c39ed73c9c5e00ea52d3554a663b17f`, the failure record has SHA-256 `8b3c7ea82020947d43a3d7e4313fa3993f4b21d189a0ceca349b1b173588d791`, and the closure manifest has SHA-256 `471bafcf0dcc5ec37b39585393ddaa147a567960e38f9ffc23e6df4cd14c3186`. Its terminal verdict remains `WAVE0_A4_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; the campaign, image, receipts, logs, and failure evidence cannot be modified, deleted, retried, or reinterpreted as a pass.

The confirmed A5 trigger is an observability gap in the existing fail-closed warning path, not evidence that the warning allowlist is wrong. `run_allowlisted_backward()` captured the ordered warning messages and categories in process, restored strict deterministic error mode, and then raised a generic parse failure without including the unmatched warning inventory in stderr. The existing no-clobber stage log therefore proves the normative failure but cannot identify the warning that caused it. Because the exact raw warning is unavailable, A5 must not guess a new message form, broaden the regular expression, accept another operation or category, change the expected count, or infer that the A4 backward gate passed. The finite scalar labeled-loss precondition and return from the backward callback are forensic control-flow observations only; finite gradients, parameter update, peak VRAM, checkpoint round-trip, clean replay, and aggregate status remain unproved.

A5 retains the exact A4 detector, model revision and assets, processor, 300 queries, four frozen RDD classes, initialization order, BF16 mode, RTX 4090 requirement, package and dependency versions, source-hash rule and mapping, seed, datasets, budgets, acquisition arms, fit counts, numerical replay thresholds, and all receipt, checkpoint, atomic publication, path-boundary, and no-clobber contracts. The A3 warning acceptance contract also remains exact: only nine `UserWarning` messages that parse to `grid_sampler_2d_backward_cuda` can pass. A5 changes only what is emitted when that closed contract rejects an already-captured inventory.

On any post-callback warning-validation failure, the `FeasibilityError` text must use the exact prefix `deterministic backward warning contract failure; diagnostic=` followed by one compact canonical JSON object with this closed logical structure:

```json
{
  "reason": "unparsable_message",
  "schema_version": 1,
  "warnings": [
    {
      "category": "WarningClassName",
      "index": 0,
      "message": "the complete str(warning.message) value"
    }
  ]
}
```

The four permitted exact `reason` values are `unparsable_message`, `unexpected_category`, `count_mismatch`, and `unexpected_operation`; the example shows the first. Serialization uses `json.dumps(..., ensure_ascii=True, sort_keys=True, separators=(",", ":"))`. The `warnings` array preserves capture order, indexes from zero without gaps, and includes every captured warning. `category` is exactly `warning.category.__name__`; `message` is exactly `str(warning.message)` before JSON escaping. There is no truncation, redaction, line splitting, substring filtering, category normalization, or warning deduplication. After JSON decoding, every category and message must equal the in-process captured value. An empty capture produces an empty array and `count_mismatch`. Existing validation order is preserved exactly: for each warning in capture order, parseability is checked before category; only after all warnings pass those per-item checks is the total count checked, followed by the exact operation inventory. A warning inventory that violates multiple conditions therefore keeps the first boundary reached by that order.

The diagnostic payload is emitted only after the backward callback returns and only when warning validation fails. Source inventory/hash failures, invalid strict-mode entry, invalid arguments, and exceptions raised by the backward callback retain their existing errors and must not be relabeled as warning-contract diagnostics. Strict deterministic error mode must be restored before either a diagnostic error or a callback exception escapes. The exact nine-warning success behavior and its `BackwardWarningEvidence` remain unchanged; the feasibility receipt, receipt schema, semantic validator, and aggregate gate are not modified. The CLI continues to print the exception to stderr without a traceback and returns exit code 2; the existing audit capture binds that text to the stage command, source, image, run, exit code, timestamps, and content hash. A diagnostic log is failure evidence, never a receipt.

A5 implementation is limited to `src/vision_active_learning_loop/probes/training_feasibility.py` and `tests/probes/test_training_feasibility.py`; needing any third tracked file stops for another written scope review. TDD must first prove that the current generic parse/category/count/operation failures omit the ordered raw inventory. The completed tests must parse the JSON suffix and prove exact reason codes; complete ordered messages and categories, including quotes, backslashes, newlines, and non-ASCII text; zero-warning handling; strict-mode restoration on every validation failure and callback exception; unchanged callback/source/entry errors; unchanged acceptance and evidence for the exact nine-warning path; CLI stderr emission without traceback; and no receipt publication on diagnostic failure. Focused and complete CPU suites, targeted Black/Ruff, `uv lock --check`, `git diff --check`, historical-evidence rehashing, and a Critical=0/Important=0 review are mandatory before one append-only implementation commit. No schema, runner, publisher, Dockerfile, config, dependency lock, model, dataset, research protocol, or historical artifact may change.

After the reviewed implementation candidate passes those gates, A5 permits exactly one fresh diagnostic campaign with a never-used A5 run ID, fresh source-bound OCI image, fresh primary attempt/campaign/checkpoint/audit roots, and an exclusive project GPU lease. `VAL_DATA_ROOT` remains unset and RDD access remains forbidden. Session-side orchestration executes only environment, model-assets, model-contract, and primary feasibility-A; it must use atomic no-clobber audit publication equivalent to the existing runner, and it must stop before feasibility-B regardless of whether feasibility-A fails or unexpectedly passes. The full `run_wave0_clean.ps1` sequence cannot be used for this diagnostic because a feasibility-A success would advance to feasibility-B. Clean-a, clean-b, aggregate Wave 0, and Wave 1 are forbidden in A5.

If feasibility-A fails with a syntactically valid, complete A5 diagnostic payload, the campaign is closed as `WAVE0_A5_DIAGNOSTIC_CAPTURED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`; this means only that the missing raw warning evidence was recovered. If feasibility-A passes, fails before the diagnostic boundary, emits malformed/incomplete diagnostics, violates identity/no-clobber/history checks, or encounters any Docker/GPU/evidence failure, the campaign is preserved and closed as `WAVE0_A5_DIAGNOSTIC_INCONCLUSIVE / WAVE1_FORBIDDEN`. No A5 outcome authorizes a retry, a parser or allowlist change, a Wave 0 pass claim, or Wave 1. The raw evidence requires a separate owner-reviewed contract amendment before any subsequent implementation or full Task 6 execution.

#### 5.2.8 A6 deterministic-attention contract

The owner-approved A5 diagnostic campaign `wave0-a5-20260825T084331001Z`, bound to source commit `979aa63893971ba979f030fdda52a4fa5746f520` and OCI image `sha256:6e334236b7db5af654d8fd90c80a2febf4bf4e164fff39cd0c854e954421786a`, passed its CPU-only diagnostic micro-check, Linux/RTX 4090 environment receipt, pinned model-asset verification, and complete four-class model contract. Primary feasibility-A then returned exit code 2 with one canonical A5 diagnostic and stopped before receipt or checkpoint publication. The environment, model-assets, and model-contract receipt SHA-256 values are respectively `af8470e6d513ce0a696e2101b49360ad527b8fa62688706a96b458a230bb35c8`, `f10a93b59806d32c993cee03395a8e7c61f7fc3559a98885b3839cea606e204e`, and `2f9d935b44f374ad5ca901bfd4050131be5493c07b18f8fdeed8bef2e4532f81`. The feasibility-A stage log has SHA-256 `b3e42a878f7a3c1611b96501b874871bb4fded5a1e50fdd38f7e24c9a8a43363`, its stage record has SHA-256 `e203bcb02efe8ea88badfca2aab454fa6ee45bd5aca4349eeff4c115318127bb`, the decoded diagnostic record has SHA-256 `058bc2c87341a7d1783a0b9a189d9f1920f2ebd1a83c1a5c1152288805484055`, the campaign result has SHA-256 `cc60eadec2ce11ca5168cc56e1dd39645f3b9751390fc3f8db9bc90bfd287796`, the campaign file manifest has SHA-256 `402a78520a830923376aecdec61aa07743cdc8c2c68c8b2e7690392fac703ee5`, the historical-preservation record has SHA-256 `01a28a84240a34dd7c56a0e7bbd9f1045adf08f2f64affbc717899543060d7f6`, and the closure manifest has SHA-256 `e8fa4f6ab33989db79af7f06e0d6d99d3e4c30b00c9955a3bcf18c0a8b00bace`. Historical rehashing reported zero drift across 63,682 artifact files, eight prior Wave 0 images, and 23 protected files. The lease was released, no A5 container remains, and the terminal verdict is permanently `WAVE0_A5_DIAGNOSTIC_CAPTURED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`.

The A5 diagnostic contains exactly 11 ordered `UserWarning` values. Indexes 0 through 2 and 4 through 9 are the nine previously registered `grid_sampler_2d_backward_cuda` warnings. Index 3 is the complete A5-captured Memory Efficient Attention nondeterminism warning, and index 10 is the complete A5-captured Flash Attention nondeterminism warning; both direct the caller to strict `torch.use_deterministic_algorithms(True, warn_only=False)`. Their unmodified messages, categories, indexes, and order remain content-bound by the diagnostic record identified above. Existing parse-before-category-before-count validation correctly reports `unparsable_message` at index 3. The inventory proves that the original nine-warning deformable-attention exception is still exact and that two separate fused SDPA backward implementations were also exposed to the A3 warn-only interval. It does not justify accepting 11 warnings or expanding the parser.

The pinned-source data flow establishes the root cause:

1. Transformers 5.15.0 `RTDetrSelfAttention.forward` selects `ALL_ATTENTION_FUNCTIONS.get_interface(self.config._attn_implementation, eager_attention_forward)`. With the approved unmodified pretrained configuration, the resolved implementation is `sdpa`; `transformers.integrations.sdpa_attention.sdpa_attention_forward` calls `torch.nn.functional.scaled_dot_product_attention`.
2. `configure_determinism(17)` correctly establishes `torch.use_deterministic_algorithms(True, warn_only=False)` and deterministic debug mode `error`. The A3 `run_allowlisted_backward()` exception then temporarily changes the entire backward callback, not only grid-sample nodes, to `warn_only=True` so the unavoidable nine CUDA grid-sample backward operations can complete.
3. In pinned PyTorch 2.12.0 `aten/src/ATen/native/transformers/cuda/attention_backward.cu`, Flash Attention sets its backward `deterministic` flag only in the non-warn-only branch. In the warn-only branch it emits the observed warning and leaves the default nondeterministic path active. Memory Efficient Attention likewise forces `num_splits_key = 1` only in the non-warn-only branch; its warn-only branch emits the observed warning without imposing that deterministic restriction.
4. Therefore the A3 global warn-only interval is sufficiently narrow in time but not sufficiently narrow by operation: it permits the intended grid-sample exception and simultaneously disables the pinned fused-attention deterministic safeguards. The detector, four-class reset, labeled loss, RTX 4090, BF16, model assets, and evidence publisher are not the cause.

A6 adopts **Option A: Math-only SDPA for the complete labeled forward-through-backward region**. It explicitly rejects two alternatives. It must not add the two attention messages to the warning allowlist, because pinned PyTorch states that those warn-only branches retain default nondeterministic behavior. It also must not change `attn_implementation` to `eager`, because doing so changes the approved Transformers execution interface and broadens the model-contract surface. No private ATen flag, autograd hook, custom CUDA kernel, model freeze, CPU fallback, dependency change, or split backward is permitted.

The A6 labeled-step order is normative:

1. Before the labeled model call, verify the two A6 Python-source files and their canonical hashes, verify that `model.config._attn_implementation == "sdpa"`, verify strict deterministic error mode, and observe the four SDPA backend flags through their public PyTorch accessors.
2. The pre-context backend state must be exactly `{"cudnn": true, "flash": true, "math": true, "memory_efficient": true}`. A caller or environment that has already changed any backend fails before model forward; A6 does not normalize an unknown entry state.
3. Enter `torch.nn.attention.sdpa_kernel(torch.nn.attention.SDPBackend.MATH)`. Before model forward, the in-context state must be exactly `{"cudnn": false, "flash": false, "math": true, "memory_efficient": false}`.
4. Keep that one context active from immediately before `torch.autocast(device_type="cuda", dtype=torch.bfloat16)` through the labeled RT-DETR forward, scalar finite-loss validation, `run_allowlisted_backward(loss.backward, expected_count=9)`, and completion of its warning-contract validation. Backend selection cannot be applied only at backward time because SDPA selects and records its implementation during forward.
5. Exit the Math-only context before gradient inspection, clipping, optimizer/scheduler update, timing finalization, checkpoint capture, or receipt construction. The post-context backend state must exactly equal the recorded pre-context state. Strict deterministic error mode must also be restored before execution continues.
6. On success, the only captured warnings remain exactly nine `UserWarning` messages parsed to `grid_sampler_2d_backward_cuda`. Zero, eight, ten, 11, any fused-attention message, any other category or identifier, or any unparsable message remains a fail-closed warning-contract error.

The Math-only context must restore backend flags on normal return and on every labeled-forward, loss-validation, callback, warning-validation, or strict-mode exception. An entry-source, config, strict-mode, or pre-context-state failure occurs before the model call. An in-context-state failure occurs before the model call and exits through the context restore path. If context restoration itself disagrees with the exact entry state, A6 raises a deterministic-attention restoration error, chains any body exception as its cause, publishes no feasibility receipt or checkpoint, and stops the campaign. No process-global backend mutation may escape the bounded labeled region.

The A6 source contract uses the existing `python-source-lf-normalized-sha256-v1` rule and adds a separate closed mapping without changing the A4 `allowlisted_backward.source_sha256` mapping:

```text
torch_nn_attention              56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0
transformers_sdpa_attention     d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098
```

`torch_nn_attention` resolves only from `inspect.getsourcefile(torch.nn.attention)` and `transformers_sdpa_attention` only from `inspect.getsourcefile(transformers.integrations.sdpa_attention)`. Both must be ordinary regular files within their installed package roots, never symlinks or junctions. Missing, extra, renamed, wrong-path, wrong-hash, non-UTF-8, or non-regular source fails before model forward. The existing pinned package versions and OCI identity continue to bind the compiled PyTorch implementation; A6 introduces no network lookup or runtime source download.

Every A6 feasibility receipt has `schema_version == 3` and adds a required, closed `normative.deterministic_attention` object with this exact value structure:

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

The receipt schema uses `additionalProperties: false` at every new object boundary. The semantic validator requires the exact values above, not merely truthy fields. `normative.invariants` adds exact booleans `deterministic_attention_math_only`, `deterministic_attention_scope_verified`, `deterministic_attention_source_verified`, and `deterministic_attention_backend_restored`; all must be `true` for `PASS`. The complete `deterministic_attention` object is also a required input to the existing exact replay preimage and must match exactly across primary A/B, clean-a A/B, and clean-b A/B. A schema-v2 receipt, missing or extra field, key rename, alternate backend, `eager` implementation, altered scope, different flag map, `restored: false`, wrong hash rule, wrong source inventory, or replay mismatch cannot satisfy A6. Existing parent receipt, environment, run, source/image, checkpoint, numerical, and no-clobber validation remains unchanged.

A6 implementation is limited to exactly four tracked files: `src/vision_active_learning_loop/probes/training_feasibility.py`, `src/vision_active_learning_loop/artifacts/receipts.py`, `schemas/feasibility-receipt.schema.json`, and `tests/probes/test_training_feasibility.py`. Needing a fifth tracked file stops for a new written scope review. The implementation must use TDD. CPU tests must prove source verification precedes any callback; exact `sdpa` config and entry flags; Math-only flags before the synthetic labeled-forward callback; context coverage of both forward and `run_allowlisted_backward`; exact restoration on success, forward error, backward error, and warning-contract error; unchanged acceptance of exactly nine grid-sample warnings; rejection of the two exact A5 fused-attention messages; schema-v3 closed inventory; semantic-validation failures for every altered field; and inclusion of the complete object in the exact replay preimage. Tests must not claim that a CPU mock proves CUDA kernel determinism.

Before an A6 implementation commit, focused tests, the complete CPU suite, targeted Black and Ruff, `uv lock --check`, `git diff --check`, full historical-evidence rehashing, and an independent review with Critical=0 and Important=0 are mandatory. Only the four allowed files may be staged. Author and committer remain `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`, and the commit must be append-only without amend, rebase, reset, squash, or history rewriting.

After the implementation plan and candidate receive separate owner approval, A6 permits one fresh source-bound OCI image and one never-used A6 run ID. Before a GPU lease, the fresh image must pass a CPU-only, no-network, no-model-forward micro-check that verifies both new source hashes, the exact pre/inside/post backend maps, restoration, and unchanged strict deterministic error mode. The formal attempt then requires an exclusive RTX 4090 lease, fresh primary/clean-a/clean-b/campaign/checkpoint/receipt/audit roots, atomic no-clobber publication, and the unchanged full Wave 0 sequence: environment, model assets, model contract, primary feasibility-A and feasibility-B, clean-a feasibility-A and feasibility-B, clean-b feasibility-A and feasibility-B, cross-attempt deterministic comparison, and aggregate gate. A6 does not permit a diagnostic-only shortcut or reuse of any A2 through A5 object.

Math-only SDPA may increase runtime or peak VRAM. This is an explicit A6 feasibility risk, not permission to alter the 22 GiB peak-allocation ceiling, BF16, batch size, tensor shapes, model, attention implementation, warning count, checkpoint gate, replay thresholds, or execution order. OOM, timeout, excess VRAM, any warning other than the nine registered grid-sample warnings, missing/invalid evidence, replay drift, Docker/GPU failure, or any other normative failure preserves the fresh campaign and stops at `WAVE0_A6_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; there is no fallback to fused or eager attention and no retry under this design. If every gate passes, the only success terminal is `WAVE0_A6_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`.

A6 changes no detector identity, pretrained revision, processor, model asset, four-class reset, query count, optimizer, scheduler, seed, formal seed list, dataset, split, budget, acquisition arm, fit count, metric, numerical threshold, dependency version, Docker base, research claim, or Wave 1 authorization. `VAL_DATA_ROOT` remains unset throughout Wave 0; RDD access, Wave 1, remote operations, push, merge, tag, Release, and GitHub publication remain forbidden until a later explicit owner checkpoint. All A2, A3, A4, and A5 commits, images, campaigns, receipts, logs, diagnostics, leases, manifests, checkpoints, and hashes remain immutable.

#### 5.2.9 A7 CUDA grid-sample backward attribution contract

The one authorized A6 campaign `wave0-a6-20260825T125943018Z`, bound to source commit `efe5cee58931e8e8bb85292b4c48701ec2e32c9b` and OCI image `sha256:04bce082c4040fded9cda6b9dfde2a76dc5686299fe991358951bd023fe39be8`, is closed and immutable. Its CPU micro-check passed with SHA-256 `59ca6f4697d85327ac098761d290e40e338a9a0894574c2ac7fbbb99981c5d42`. Primary, clean-a, and clean-b each completed environment, model-assets, model-contract, feasibility-A, and feasibility-B exactly once; every individual stage returned `PASS`. The aggregate Wave 0 receipt has SHA-256 `aa4912a792d054dce2e3a46c48e40dd5390f9b8ff66feb574bf20970ae244624`, the aggregate failure diagnostic has SHA-256 `26d67369ddc73b1d2e9476e3fbe4f6ac7a6564b336580a256943ef2d14302a22`, the campaign result has SHA-256 `441144efc226bf87ca0a11869a87ae0f64c8e0d829b030626ac1cfba59755bbd`, the pre-closure file manifest has SHA-256 `50b5f17a3244290ccbd41118b07034dc47976d2c046c2cf88e6c6cb413c74642`, the historical-preservation record has SHA-256 `61248362331be335501b7dc5439500cea179f02b192fdad4afa24930f1eb4d75`, and the closure manifest has SHA-256 `bf869deca033a82c9b0510baff9d2ee55227cc79e62648fcbae3bc316810e1c8`. The permanent terminal is `WAVE0_A6_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; A7 cannot modify, delete, retry, reuse, complete, or reinterpret that campaign.

The A6 evidence narrows but does not yet prove causation:

1. All six schema-v3 feasibility observations report the exact scalar loss `0x1.b1c6ea0000000p+8`, the exact pre-update trainable-parameter digest `2e9dd203a945c17b987386d7950c7604ab24d3e534d49fe20ed2c3eb333a5b80`, the exact replay preimage SHA-256 `63fe541469859a3fc55f4687e26f77cdaf25cb2a6d701592c9910a0b2ef9caad`, Math-only SDPA over the complete labeled forward-through-backward region, and exactly nine `UserWarning` values parsed to `grid_sampler_2d_backward_cuda`. All five non-canonical exact comparisons pass.
2. All five numerical comparisons fail. With primary-A gradient norm `2992.56201171875`, the registered `rel_tol=1e-5, abs_tol=1e-7` permits an absolute difference of approximately `0.0299256201`; the observed differences range from `1.08642578125` to `7.656982421875`, approximately 36.3 to 255.9 times that allowance. Backbone model-update relative L2 ranges from `0.0579991443` to `0.0603883738`; detector model-update relative L2 ranges from `0.0208350074` to `0.0216155731`, against the registered maximum `0.001`.
3. The pinned Transformers 5.15.0 fallback data flow remains `encoder_hidden_states -> value_proj -> MultiScaleDeformableAttention -> torch.nn.functional.grid_sample`. Each of three decoder layers calls the fallback once for each of three feature levels. Pinned PyTorch 2.12.0 classifies differentiating CUDA `grid_sample` as normally nondeterministic and the six A6 observations expose exactly those nine warnings and no fused-attention warning.
4. A read-only postmortem reconstructed a directional estimate of pre-clip first-step gradients from the saved AdamW `exp_avg`, recorded gradient norm, `beta1=0.9`, and `max_norm=0.1`. After removing the common clipping scale, relative L2 drift is approximately `5e-8` to `9e-8` for decoder self-attention and other decoder parameters, `3e-6` to `1.1e-5` for decoder deformable-cross-attention parameters, `0.00323` to `0.00417` for the hybrid encoder, and `0.00860` to `0.01621` for the backbone. This pattern is consistent with nondeterministic `grid_sample` value-gradient accumulation propagating into encoder/backbone parameters, but the estimate uses receipt-level scalar precision and post-update state; it is forensic localization, not an A7 receipt and not causal proof.

The registered A7 hypothesis is: **with exact forward operands and exact incoming gradient, CUDA `grid_sampler_2d_backward_cuda` produces differing value and/or sampling-grid gradients, and this is the first tensor-level divergence that explains the A6 replay failure.** A7 must distinguish this hypothesis from forward divergence, instrumentation effects, a different backward operation, or insufficient evidence. It must not describe the hypothesis as confirmed before the registered intervention succeeds.

A7 adopts **Option B: bounded kernel-attribution diagnostic**. It rejects two immediate alternatives. A static-only postmortem would leave causation inferential and cannot justify a new contract. An immediate replay-threshold change, custom kernel, CPU fallback, model change, freeze, dependency change, or detector replacement would act before attribution and could convert an observed failure into a post-hoc pass. Either kind of reproducibility redesign requires a later owner-reviewed amendment informed by A7; it is not part of this diagnostic.

A7 retains the exact A6 detector, RT-DETR and DINOv2 revisions and assets, processor, 300 queries, four-class reset, initialization order, synthetic fixture, seed 17, BF16 labeled path, Math-only SDPA boundary, three decoder layers, three feature levels, `disable_custom_kernels == true`, RTX 4090 requirement, package versions, source-hash rules, warning identifier and count, 22 GiB peak-allocation ceiling, and all evidence-provenance and no-clobber rules. It changes no formal seed, budget, dataset, split, acquisition arm, fit count, metric, calibration rule, optimizer recipe, numerical replay threshold, or research claim. `VAL_DATA_ROOT` remains unset; RDD, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.

The diagnostic architecture has three isolated components:

1. **Uninstrumented model control.** Exactly two fresh-process replicas execute the A6 labeled forward and bounded backward on the frozen synthetic batch, stopping before gradient clipping, optimizer/scheduler update, checkpoint construction, or feasibility-receipt publication. They record high-level identity, loss hexadecimal value, the complete ordered trainable-parameter gradient digest inventory, warning inventory, backend state, runtime, and VRAM only. Each parameter-gradient record binds name, shape, dtype, finite status, byte digest, and CPU-float64 norm. These controls cannot satisfy any A6 gate.
2. **Instrumented model boundary.** Exactly five fresh-process replicas execute the same forward and backward through a diagnostic adapter around only the nine fallback `grid_sample` calls. Stable operation IDs are the Cartesian product `decoder_layer in {0,1,2}` and `feature_level in {0,1,2}`. The adapter calls the original pinned `torch.nn.functional.grid_sample` with unchanged operands and the exact arguments `mode="bilinear"`, `padding_mode="zeros"`, and `align_corners=False`; it returns that original result without arithmetic modification. Observation hooks retain and record the forward value tensor, sampling-grid tensor, result tensor, incoming result gradient, outgoing value gradient, and outgoing sampling-grid gradient for every operation. Each replica also records the same complete ordered trainable-parameter gradient digest inventory as the controls. The backward callback event order must be identical across all five replicas and is recorded rather than inferred from forward order.
3. **Isolated VJP replay.** The first valid instrumented replica publishes one immutable, hash-bound CPU snapshot containing the exact value tensor, sampling-grid tensor, and incoming result gradient for all nine operation IDs. Exactly five fresh-process isolated replicas load that one verified snapshot. For each operation ID they call only the original pinned `grid_sample` and compute its vector-Jacobian product with the saved incoming gradient. Each replica must emit exactly nine `grid_sampler_2d_backward_cuda` warnings and no other warning. No model forward, optimizer, scheduler, checkpoint, or dataset operation occurs in this component.

Every diagnostic tensor record includes the stable operation ID and role; original shape and dtype; element count; finite/non-finite counts; a SHA-256 over an explicitly little-endian, contiguous CPU byte representation; a CPU-float64 L2 norm; and, for each comparison, exact-digest equality, difference L2, relative L2, and cosine. The numerical values are descriptive attribution evidence only: A7 registers no new acceptance tolerance and does not reuse the A3 thresholds as a diagnostic pass boundary. Empty, zero-element, unsupported-dtype, non-finite, shape-mismatched, reordered, missing, extra, duplicate, non-regular, symlinked, junctioned, wrong-endian, or wrong-hash tensor evidence fails closed.

Instrumentation validity is itself normative. Across the two controls and five instrumented model replicas, the model/source/image/fixture/seed/backend identities, scalar loss hexadecimal value, and nine-warning inventory must match exactly. All forward value, sampling-grid, and `grid_sample` result digests must match across the five instrumented replicas. Observation hooks may return `None` or the unmodified incoming gradient only; they may not replace, scale, cast, detach, reorder, or otherwise alter a gradient used by autograd. Any new warning, changed loss, changed forward digest, missing event, unstable event order, unexpected CUDA synchronization failure, or static identity difference between control and instrumented replicas makes attribution inconclusive rather than being ignored. Because the admitted operation is nondeterministic, parameter-gradient equality between control and instrumented replicas is descriptive and is not required to validate the observation seam.

The ordered first-divergence rule is exact:

- Traverse the recorded backward callback order, not decoder index order.
- An operation is causally eligible only when its forward operands/result and incoming result gradient are exact across all five instrumented replicas.
- The first eligible operation whose outgoing value-gradient or sampling-grid-gradient digest differs across replicas is the model-level candidate boundary. Every earlier callback event must be exact on all recorded fields.
- The same operation ID is attributed to the CUDA kernel only when the five isolated VJP replicas start from exact-identical saved operands and incoming gradient, preserve exact forward output, emit only the registered warning, and produce at least two different outgoing-gradient digests for the same role. Pairwise magnitudes are reported but no minimum drift is required beyond byte inequality with finite, shape-identical tensors.
- Divergence that appears only after a common global clipping scale, optimizer update, serialization, or receipt publication cannot satisfy A7 because those operations are absent from the diagnostic path.

The diagnostic terminal classification is closed:

- `WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN` requires every identity, control, instrumentation, snapshot, ordering, warning, and isolated-replay invariant above plus one eligible first-divergence operation confirmed by isolated VJP replay.
- `WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN` requires every diagnostic invariant to be observable, exact isolated VJP outputs for all nine operation IDs across all five replicas, and at least two different finite full-parameter gradient-inventory digests from the five instrumented model replicas. With all nine eligible VJPs exact, that model-level divergence is outside the registered grid-sample outputs; this terminal does not identify or fix the other cause.
- `WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN` covers every precondition, Docker, GPU, lease, source, identity, instrumentation, tensor, warning, ordering, VRAM, publication, evidence, or classification failure, including a completely exact diagnostic with no reproduced model-level divergence.

No A7 terminal represents a Wave 0 pass or contains the standalone success token `PASS`; `WAVE0_NOT_PASSED` is an explicit negative status. An attributed result proves only the registered one-step synthetic attribution on the pinned RTX 4090 stack. It does not establish long-run training variance, justify any numerical bound, show strategy stability, validate RDD training, or choose the next reproducibility contract. A not-attributed or inconclusive result cannot authorize a retry or an alternative fix.

All A7 diagnostic artifacts remain outside Git in a new run-scoped root. Before execution, the campaign root, each component root, every tensor-snapshot destination, every receipt destination, and the GPU lease destination must not exist. Publication is atomic and no-clobber; every receipt binds source commit, OCI image ID, base image digest, run ID, component/replica ID, GPU UUID, parent hashes, tensor inventory, exact argv, exit code, and timestamps. Raw synthetic tensor snapshots are diagnostic-only local artifacts and are never public-export candidates. All A2 through A6 campaigns, images, receipts, checkpoints, leases, logs, and manifests remain byte-for-byte immutable and are rehashed before and after A7.

This amendment authorizes no implementation file yet. A later A7 implementation plan must propose a closed tracked-file allowlist, TDD sequence, schema and semantic-validation boundaries, CPU mock limitations, fresh-source/image/run identities, independent review, and exact execution commands. Before any implementation commit, focused and complete CPU suites, targeted Black and Ruff, `uv lock --check`, `git diff --check`, historical-evidence rehashing, and a Critical=0/Important=0 review remain mandatory. CPU tests may verify adapters, digest rules, comparison/classification logic, fail-closed validation, and no-clobber behavior, but must not claim CUDA attribution. After separate approval of the committed plan and implementation candidate, A7 permits at most one fresh diagnostic campaign and no retry.

Every A7 outcome returns to owner design review. An attributed result permits proposing, but not adopting, either a separately calibrated statistical reproducibility contract with independent validation or a deterministic execution/model change. A not-attributed or inconclusive result requires renewed root-cause investigation. None may change A6, run the Wave 0 aggregate gate, access RDD, or start Wave 1 by implication.

#### 5.2.10 A7 launch-orchestration hardening contract

Three closed A7 launch campaigns now exist and remain immutable. The most recent campaign, `wave0-a7-20260826T021633738Z`, is bound to source commit `a5c193061c43a3aaf7dcc5652f1d3e0a009c00c1`, image tag `vision-active-learning-loop:wave0-a7-a5c193061c43-wave0-a7-20260826T021633738Z`, and image ID `sha256:958713719023c74c6be255f3baa513a17a36022165a6714f183ca8ecfbcd250a`. Its Docker build exited zero, but session-side PowerShell constructed the five requested OCI label values as one concatenated array element. Docker consequently stored the source commit followed by the other four assignments inside `org.opencontainers.image.revision`; the required run-ID, specification-commit, and plan-commit keys were absent. The image-identity gate correctly failed before the CPU micro-check, GPU lease, model forward, Task 8, or any A7 component stage.

That failure is permanently recorded by build result SHA-256 `2a6883eda523f60ce4cd37f9295c9a2be685fc12d7517de49dd6142429bb8b8c`, image-inspect SHA-256 `808c239c44309bf766a9f7277ed175ea420bbfedd72f2c67fb0f514421633a08`, failure-diagnostic SHA-256 `16a3e8f4e317332b68b68c71094a66c53c9a9462aab1932d02cb028f2d04f60f`, historical-preservation SHA-256 `493132748450f2c1613dce949438fbb9e637ef7326708be06b7c43c25ef9b9e5`, campaign-result SHA-256 `d9e4787f323ddc8a26baf03cbea9a767bf7b452da421efa52d5caca299c01ce4`, pre-closure manifest SHA-256 `45e4b15c44cc20f20ba15fd6694adb51a5b22df986c8396e44dba0e0c0db3a72`, and closure SHA-256 `e983a044b63ca4bbf36f8ccfe8ea6041f94a796a20b397a926740e74e764a728`. Its terminal is `WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`. The campaign, malformed-label image, earlier two A7 launch campaigns, and all earlier evidence must not be modified, deleted, retagged, reused, or reinterpreted.

Each of the three closed launch campaigns was separately authorized by the owner with a fresh run ID after the preceding pre-GPU orchestration failure; those authorizations narrowly superseded the earlier no-retry rule for their named attempt only. Their existence creates no standing retry authority. This Section 5.2.10 replaces that manual exception pattern with a reviewed launcher boundary, but it still does not authorize another attempt.

The failure does not invalidate the A7 model diagnostic, tensor-evidence implementation, schema, classifier, or existing Task 8 runner. It establishes that ad hoc session-side construction is not a sufficiently reliable launch boundary. A7 therefore adopts one checked-in, tested launch path before any further execution can be considered. The architecture has three responsibilities:

1. `scripts/start_wave0_a7.ps1` is the sole Task 7 orchestration entry point. It validates the reviewed Git candidate, Docker Linux engine, RTX 4090 inventory, historical baseline, output nonexistence, build identity, CPU micro-check, and exclusive GPU lease before invoking the existing Task 8 runner exactly once.
2. `scripts/run_wave0_a7_cpu_microcheck.py` is the production-only, CPU-only micro-check payload executed inside the fresh image from the read-only mounted worktree. It imports no test module or development-only package and never performs a model forward or initializes CUDA.
3. `scripts/run_wave0_a7.ps1` remains the sole Task 8 component runner. The launcher may call it only after every Task 7 invariant is closed and the lease is atomically claimed. The launcher cannot reproduce, inline, reorder, or selectively skip its 2-control, 5-instrumented, 5-isolated, and aggregate sequence.

The launcher is a fail-closed state machine:

```text
UNCLAIMED -> CAMPAIGN_CLAIMED -> IMAGE_VERIFIED -> CPU_VERIFIED
          -> GPU_LEASED -> TASK8_INVOKED_ONCE -> CLOSED
```

Before `CAMPAIGN_CLAIMED`, a failure creates no run ID directory, image, or lease. After the campaign root is atomically claimed, every failure transition goes directly to `CLOSED`; it publishes an exact stage diagnostic, campaign result, pre-closure file manifest, historical-preservation record, and closure manifest through `FileMode.CreateNew`. A build may be launched at most once for one run ID. The micro-check and Task 8 runner may each be launched at most once. No catch block, caller, loop, or manual continuation may rebuild, rerun, resume, or reuse the campaign.

The launcher requires exact owner-reviewed values for source commit, specification commit, implementation-plan commit, branch, worktree, and base-image digest. It must resolve the registered worktree through Git, require both linked and canonical worktrees clean, and reject rather than repair any mismatch. Docker build arguments are constructed as an ordered `System.Collections.Generic.List[string]` or an equivalently typed argument vector; shell-command strings and implicit PowerShell array concatenation are forbidden. The exact required OCI label assignments are:

```text
org.opencontainers.image.revision=<40-hex source commit>
org.opencontainers.image.val.run_id=<fresh run ID>
org.opencontainers.image.val.spec_commit=<40-hex specification commit>
org.opencontainers.image.val.plan_commit=<40-hex implementation-plan commit>
org.opencontainers.image.base.digest=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356
```

The build argv must contain exactly five separate `--label` tokens, each immediately followed by exactly one assignment above. No element may contain whitespace followed by another label key. The recorded argv is inspected before the build starts and stored unchanged afterward. A successful build is insufficient: Docker inspect must return exactly one image, the tag must resolve to that exact image ID, and all five observed values must equal their registered inputs. A missing, extra-within-value, concatenated, duplicated, blank, wrong-key, wrong-value, malformed-hash, tag mismatch, or image-ID mismatch closes the campaign before the CPU micro-check. Existing malformed or failed images may not be retagged to satisfy this gate.

Task 7 historical preservation uses two hash-bound layers. The original Task 1 baseline remains fixed at SHA-256 `4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd`. Before claiming a new campaign, the launcher fully rehashes every current historical artifact and inspects every historical `vision-active-learning-loop:wave0-*` image, verifies that the original baseline is an exact unchanged subset, and publishes a fresh augmented baseline outside the artifact root using no-clobber creation. At this amendment, the closed inventory is 64,011 artifact files, 14 images, and the original 68 protected Git files. The augmented document binds the original baseline hash, complete sorted artifact records, complete image tag-to-ID records, protected Git records, and reviewed source commit. Its path and SHA-256 are bound into the Task 7 identity, build audit, CPU micro-check audit, and GPU lease. Task 8 revalidates the same augmented baseline while excluding only its own exact campaign root and image tag; no prior failed campaign or image is treated as disposable drift.

The checked-in CPU micro-check replaces all dynamic stdin and pytest-based harnesses. It runs with `--network none`, no `--gpus`, no model-cache mount, and no model forward. The worktree and synthetic inputs are mounted read-only. Before importing diagnostic or model modules, it verifies lazy CLI manifest discovery. It then verifies the reviewed Git-blob hashes for the launcher, micro-check payload, A7 Task 8 runner, attribution module, tensor-evidence module, receipt validator, and schema; canonical tensor bytes for BF16, FP16, FP32, and FP64; one exact 27-tensor snapshot encode/decode round-trip; corrupted-snapshot rejection; one schema-valid control, instrumented, isolated-VJP, and aggregate receipt; and the exact `ATTRIBUTED`, `NOT_ATTRIBUTED`, and `INCONCLUSIVE` classifier branches using deterministic synthetic evidence derived from checked-in literal constants. It must finish with `torch.cuda.is_initialized() == false`. Importing `pytest`, importing any `tests.*` module, installing a package, using the network, or deriving expected results by calling test builders fails the micro-check.

Only after the image and CPU micro-check audits exist and their hashes are recomputed may the launcher claim the GPU lease with atomic create-new semantics. The lease binds run ID, source/specification/plan commits, image tag and ID, base digest, GPU UUID, campaign root, augmented-baseline path and hash, build-audit hash, micro-check-audit hash, host process inventory, container inventory, and timestamp. A competing numeric CUDA process, active project lease, active project container, wrong GPU count or UUID, unavailable RTX 4090, set `VAL_DATA_ROOT`, or changed audit closes the campaign without CPU fallback. Task 8 must release the exact lease to a never-existing released destination on every exit path.

Implementation is restricted to a narrow launcher boundary. The implementation plan may authorize creation of `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7_cpu_microcheck.py`, `tests/gates/test_wave0_a7_launcher.py`, and `tests/diagnostics/test_wave0_a7_cpu_microcheck.py`. Modifying any model, diagnostic classifier, tensor-evidence rule, receipt schema, dependency, Dockerfile, configuration, fixture used by formal research, dataset protocol, numerical threshold, or existing historical artifact is outside scope. A necessary fifth tracked file or any change to `scripts/run_wave0_a7.ps1` requires renewed written scope review rather than implicit expansion.

TDD must prove real launcher behavior, not source-text presence alone. Tests execute the relevant PowerShell functions with controlled filesystem roots and an external Docker process adapter. They cover five distinct OCI label argv elements, concatenated-label rejection, clean Git identity, fresh-destination enforcement, zero-byte stdout logs, build exit propagation, exact inspect binding, production-only micro-check execution, augmented-baseline subset and exact-set verification, micro-check-before-lease ordering, atomic lease contention, one-shot Task 8 invocation, and complete no-clobber closure from every post-claim failure state. Python tests independently cover the four dtype encodings, 27-tensor snapshot inventory and corruption, four receipt kinds, three classifier outcomes, forbidden test/dev imports, lazy manifest behavior, and CUDA remaining uninitialized. CPU tests must not claim that Docker mocks or synthetic evidence prove RTX 4090 attribution.

Before an implementation commit, focused launcher and diagnostic tests, the complete CPU suite, targeted Black and Ruff, PowerShell parsing, `uv lock --check`, `git diff --check`, full historical artifact/image rehashing, exact A6 fixed-evidence hashes, and a Critical=0/Important=0 review are mandatory. Only the reviewed allowlist may be staged. Author and committer remain `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`, and history remains append-only without amend, reset, rebase, squash, or force operations.

The owner approved this exact written amendment on 2026-08-26. That approval authorizes one separate implementation-plan commit defining the RED/GREEN sequence, exact commands, file allowlist, source/specification/plan bindings, failure evidence, and review checkpoints. Implementation requires separate approval of that committed plan. Docker build, GPU execution, lease acquisition, and one fresh A7 Task 7/8 attempt require another explicit approval of the committed implementation candidate. Until then, the permanent stopping point remains `WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`; RDD, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.

#### 5.2.11 A7 protected-Git lineage compatibility and candidate-review closure

The first checked-in launcher candidate consists of production micro-check commit `246053d1c1328bbdf169dc767d7ca87756621cde` and launcher commit `e15b9ad6646b55ff57ad3801da42295a1366b93c`. Its focused CPU verification completed with 253 passed and four capability skips; its complete CPU suite completed with 735 passed and nine capability skips; Black, Ruff, `uv lock --check`, `git diff --check`, and both PowerShell parsers succeeded. Full review then rehashed all 64,011 historical artifact files without drift, verified all 14 historical image identities, and verified the seven fixed A6 evidence hashes. No project container or active lease existed and `VAL_DATA_ROOT` was unset.

That candidate is not an executable Task 7 candidate. Mandatory review found one and only one protected-Git mismatch: `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`. The immutable root record is 134,883 bytes with SHA-256 `4e7caba21a24f09cf9fa1c341d2c7c066405e504a2190b067e745650780329b5`; the reviewed checkout at candidate `e15b9ad6646b55ff57ad3801da42295a1366b93c` was 147,477 bytes with SHA-256 `0a3c337cd7be2a38be314940b8afa07d05c7e9347191a6a86bc969d7aeed7593` and was sourced from owner-approved specification commit `5d6ffe0567a4aeed0bcaceed7a33416b04f41925`. The difference is approved design history, not corruption of an old campaign. The launcher nevertheless rejects it as generic drift, while the existing Task 8 runner independently requires the augmented record to equal the root record and the current checkout to equal that same record. Relaxing only the launcher would therefore defer an unavoidable preservation failure until after GPU work. The implementation plan's fifth-file stop condition correctly blocked execution before a new run ID, image, campaign, or lease was created.

This section supersedes only the protected-Git equality rule in Section 5.2.10. It does not replace the root baseline, remove the specification from protection, or permit general document drift. The original Task 1 baseline and its SHA-256 `4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd` remain immutable. Its complete 68-record `protected_git` array remains present byte-for-byte in every augmented baseline. Exactly one path may have a distinct reviewed-current identity:

```text
docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md
```

The approved-current endpoint is the checkout of this design document at the owner-approved docs-only commit that records Section 5.2.11. Because a document cannot contain its own final Git commit or content hash without a circular identity, the immediately following implementation-plan commit must record that exact specification commit, the checked-out file's exact byte size and SHA-256, and the exact Git object identity for the path. The implementation-plan commit must be a direct child of the specification commit and must change only its new plan document. A later implementation candidate must be an append-only descendant of those two commits and must leave the specification and plan unchanged. Runtime values supplied by the owner, Git, OCI labels, Task 7 audits, and the GPU lease must all equal those recorded identities; a computed mismatch stops rather than substituting a new value.

An augmented historical baseline now has three closed protected-Git structures:

1. `protected_git` is the unchanged, sorted 68-record root array.
2. `current_protected_git` is the complete, sorted 68-record checkout array observed before campaign claim.
3. `approved_protected_git_transitions` is an array of length exactly one. Its sole object contains only `path`, `root_size`, `root_sha256`, `current_size`, `current_sha256`, `spec_commit`, `spec_git_object`, `plan_commit`, and `reason`. `path` is the exact path above; the root fields equal the immutable record; the current fields equal the safe regular checkout file; `spec_commit` and `plan_commit` equal the approved direct-parent pair; and `reason` is exactly `owner-approved-design-amendment`.

For the other 67 paths, root and current records must be identical on path, size, and SHA-256. The transition path must be a regular non-link file inside the registered worktree, must be clean in both the index and working tree, and must be the exact Git-tracked object at `spec_commit`. Missing, additional, duplicated, renamed, linked, dirty, wrong-size, wrong-hash, wrong-object, wrong-commit, non-parent plan, second-transition, wildcard, or unrecorded protected-Git evidence fails before campaign claim. The augmented baseline remains outside the artifact root, is published using atomic no-clobber creation, is parsed back, and is hash-bound into every downstream identity.

The launcher and Task 8 runner independently enforce the same rule. Task 8 first proves that the root `protected_git` array is unchanged, then validates the exact single transition, then rehashes all 68 current paths against `current_protected_git`. It must not rewrite the root record, silently promote the current record into the root array, treat the specification as unprotected, or accept a transition for any other file. Task 8 continues to exclude only its own exact campaign root and image tag from current artifact/image enumeration; the protected-Git transition creates no artifact or image exclusion.

Candidate review also closes three adjacent launcher requirements without changing the A7 diagnostic, models, thresholds, data, dependencies, or fit counts:

- **Container ownership:** the read-only collector uses no-truncation container inspection. A running container is project-owned if its exact name begins `val-a7-` or `val-wave0-`, if its configured image reference is a `vision-active-learning-loop:wave0-*` tag, or if its inspected immutable image ID equals any registered Wave 0 image ID. This includes containers launched by digest. One match blocks lease acquisition. Name-only filtering, tag-only filtering, and omission of digest-launched containers are forbidden.
- **Audit binding:** `20-image-build-result.json` binds owner authorization, run/source/specification/plan commits, branch, image tag and ID, base digest, exact build argv, augmented-baseline path and SHA-256, log hashes, exit code, and timestamps. The raw one-line production micro-check payload is published separately. `22-a7-cpu-micro-check.json` is a closed binding audit containing that payload and its SHA-256 plus the same owner/run/source/specification/plan/image/base/baseline identities, exact Docker argv, stdout/stderr hashes, exit code, and timestamp. The GPU lease hashes the two binding audits. A changed or missing field fails before lease creation.
- **Post-Task-8 validation failure:** Task 8 retains sole ownership of `30-historical-preservation.json`, `40-campaign-result.json`, `41-campaign-file-manifest.json`, and `51-campaign-closure-manifest.json` after it is invoked. If launcher-side validation of those files or lease release fails, the launcher never overwrites or reuses them and never invokes Task 8 again. It atomically publishes `52-task7-post-task8-validation-failure.json` and `53-task7-post-task8-validation-closure.json` when their destinations are absent. These records bind the observed Task 8 exit, terminal, required-file existence and hashes, active/released lease state, validation error, and pre-publication campaign inventory. If either destination exists or the audit root is unsafe, publication fails closed. An unreleased lease is recorded as unreleased and is not moved or reinterpreted by the launcher.

The compatibility implementation is restricted to exactly three tracked files: `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`. The already committed production micro-check and its tests remain unchanged. The existing implementation commits, all failed A7 campaigns and images, both baselines, receipts, logs, closures, leases, and review evidence remain append-only and immutable. The next implementation plan must use TDD and must include RED cases for the exact approved transition; every forbidden transition mutation; all 67 unchanged paths; direct-parent Git lineage; a digest-launched `val-a7-*` container; complete build and micro-check audit bindings; Task 8 partial, malformed, hash-drifted, and missing-release closures; atomic `52/53` publication; and exactly-once Task 8 invocation. Focused and complete CPU suites, Black, Ruff, both PowerShell parsers, `uv lock --check`, `git diff --check`, complete historical rehashing, read-only Docker/RTX visibility, and an independent Critical=0/Important=0 review remain mandatory.

This design approval authorizes only one docs-only amendment commit. It does not approve an implementation plan, implementation changes, Docker build, image creation, run ID, campaign root, GPU lease, Task 8 execution, RDD access, Wave 1, remote, push, merge, tag, Release, or publication. After this amendment is committed and self-reviewed, work stops for owner written-spec review. A later approved plan may authorize the exact three-file compatibility implementation; a still later owner prompt naming the reviewed candidate is required for any fresh A7 attempt.

#### 5.2.12 A8 fresh model-cache and current-lease lifecycle compatibility contract

The closed A7 campaign `wave0-a7-20260826T224622928Z` is bound to source commit `0e8086cfa5fc67fe3ef784b0f67f634398ff81ea`, image ID `sha256:f2ac42263390c3f7caf0bbbf15cb56ceb7a75e390941555965b778f6bb426d7a`, and owner authorization `OWNER-A7-0E8086C-20260827-UNATTENDED-06`. Its launcher passed source/image binding, the CPU micro-check, RTX 4090 preflight, atomic lease acquisition, and exactly-once Task 8 invocation. The environment receipt passed with SHA-256 `6b685f179fc135e82d6e2643144020a945b16d9c0879f73687c2321df4435c92`. The model-assets stage then exited 2; its audit SHA-256 is `1298f7dbd3d5ffd3b179bf1d66a361398617509bdaf4bd2f836e085a0dfeff64`, its receipt SHA-256 is `2b87a34697492ab2de9699985ca7851e0ca7ea90e7888ddded2bd69cea62774c`, and the receipt reports `Hugging Face metadata inventory differs from the exact expected set`. The campaign result, pre-closure manifest, and closure manifest SHA-256 values are respectively `2131f99d99cdedb42b15768264981d59d7252bf2659e51d8e7b849cb857d5c8e`, `9179b901b307b40e6acb3baec801b07c486af30563bf4c47df892051202e5f9a`, and `3f1cea3c03ca1fb9cf2eca574f8e37f57edd7294ac809501c7338a086066ea02`. The run-scoped released lease and release record have SHA-256 values `388459cfc3ac816131d9e5ac3f3df5911db000bd3efdfb6dc58c5645a14ea528` and `9a4b0ed0e29d52bd4268e28819dde032972745fc3f885a571cda0cc7c8835026`. The campaign, image, receipts, logs, cache inputs, and lease evidence are immutable and cannot be retried, modified, deleted, reused, or reinterpreted as diagnostic attribution.

The model-assets failure has one closed cause. The historical shared cache contains the four approved payloads, `.metadata` files, repository tree record, `.gitignore`, and `CACHEDIR.TAG` for each pinned snapshot, but it predates the lock-metadata contract. It is missing exactly these eight required zero-byte files and has no extra Hugging Face metadata entries:

```text
snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download/{README.md,config.json,model.safetensors,preprocessor_config.json}.lock
snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download/{README.md,config.json,model.safetensors,preprocessor_config.json}.lock
```

The production verifier correctly rejected that cache. A8 must not weaken its exact inventory, make locks optional, synthesize locks inside the historical cache, copy COCO rows, change a payload or revision, or reinterpret the prior cache as compliant. A8 instead inserts one source-bound model-cache preflight into the Task 7 state machine:

```text
UNCLAIMED -> CAMPAIGN_CLAIMED -> IMAGE_VERIFIED -> CPU_VERIFIED
          -> MODEL_CACHE_VERIFIED -> GPU_LEASED -> TASK8_INVOKED_ONCE -> CLOSED
```

After the fresh image and CPU micro-check pass but before GPU lease acquisition, Task 7 creates one never-existing cache-preflight root at `<campaign>/cache-preflight`. Its only writable model location is `<campaign>/cache-preflight/wave0/model_cache`; its receipt parent is `<campaign>/cache-preflight/wave0/receipts`. The launcher invokes the fresh image exactly once with no `--gpus`, the reviewed worktree mounted read-only, that cache-preflight root mounted read-write as `VAL_ARTIFACT_ROOT`, and `VAL_DATA_ROOT` absent. This one stage may use Docker `--network bridge` and may omit `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE` only to execute the existing `val assets verify ... --download` path. `snapshot_download` remains pinned to the exact two repository revisions and the literal four-file allowlist already enforced by `assets.py`. No other post-build A8 container stage may use a network, and no dataset URL, RDD path, arbitrary repository, wildcard payload, package install, or unpinned revision is permitted.

The container command suffix is exact and may vary only in the already validated run identity:

```text
val assets verify --config /workspace/configs/models/pinned-models.yaml --cache-root /artifacts/wave0/model_cache --output /artifacts/wave0/receipts/model-assets.json --run-id <RUN_ID> --download
```

This is the existing frozen model configuration tracked at `configs/models/pinned-models.yaml`; A8 introduces no alternate configuration path or model pin.

The execution identity must bind the latest reviewed A8 specification commit and a plan commit whose parent is exactly that specification commit. An earlier specification SHA embedded in a superseded plan revision is not an executable identity and must not be supplied to the fail-closed launcher.

The cache-preflight command must finish with exit code zero and a schema-valid PASS receipt. The receipt and an adjacent closed Task 7 audit bind owner authorization, run/source/specification/plan commits, image tag and ID, base digest, exact Docker argv, network mode, no-GPU assertion, cache root, receipt path and SHA-256, stdout/stderr paths and hashes, exit code, timestamps, and the verifier's exact payload/metadata inventories. The cache root, its ancestors inside the campaign, audit paths, and receipt paths must be regular non-link paths within their approved roots. Missing, extra, nonzero, renamed, unpaired, linked, or junctioned lock metadata; wrong payload/tree/metadata identity; unexpected stdout; nonzero exit; wrong network/GPU argv; or any pre-existing destination closes the claimed campaign before a lease. Task 7 recomputes the cache-preflight audit and receipt hashes immediately before lease creation. The lease adds the exact cache root, cache-preflight audit hash, and cache-preflight receipt hash to its closed identity.

Task 8 must reject the lease unless those new fields, files, hashes, paths, and identities match. It must mount only that run-scoped cache at `/artifacts/wave0/model_cache:ro`, keep `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `--network none`, and rerun `val assets verify` without `--download` to publish the ordinary Task 8 model-assets receipt. The historical shared `D:\vision-active-learning-loop-artifacts\wave0\model_cache` is no longer mounted or accepted by A8. The run-scoped cache remains inside the current campaign, is included in the campaign manifest, and becomes immutable historical evidence when the campaign closes. The cache preflight does not initialize CUDA, acquire a GPU lease, run a model forward, or claim that model-contract or attribution passed.

The same campaign exposed a separate historical-set accounting defect. Before release, the current fixed active mutex `leases/<GPU-UUID>.json` exists outside the campaign root; after release, the two run-scoped files `leases/<RUN_ID>.released` and `leases/<RUN_ID>.release.json` replace it. These are authorized current-attempt evidence, not pre-campaign history. A8 preserves the fixed GPU-UUID active path so concurrent launchers still contend on one atomic `FileMode.CreateNew` mutex. It does not move, overwrite, or delete any earlier release evidence.

Task 8 historical validation may exclude only four current identities: its exact campaign-root subtree plus the exact active, released, and release-record paths deterministically derived from the lease GPU UUID and run ID. The three lease lifecycle paths must be distinct, reside directly below the fixed project lease root, have literal names `<GPU-UUID>.json`, `<RUN_ID>.released`, and `<RUN_ID>.release.json`, and be supplied from the already validated lease rather than wildcard discovery. At the pre-release check, exactly the active path exists and the two release destinations remain absent. Every other artifact in the augmented baseline is rehashed; every other current artifact must match that exact set. The preservation receipt records the three approved paths, the one observed exclusion, baseline counts, and exact-set result. A missing baseline item, an unapproved extra path, an additional exclusion, a linked path, a pre-existing release destination, or any size/hash drift remains fatal. After Task 8 releases the lease, Task 7 independently verifies that the active path is absent, both run-scoped files are regular non-links, the released lease SHA-256 equals the release record's `original_lease_sha256`, and the release record binds the current run, source, and image.

A8 changes no detector, processor, model revision, payload hash, label mapping, query count, seed, fixture, warning allowlist, backend rule, tensor diagnostic, threshold, dataset, split, acquisition arm, fit count, dependency version, Docker base, research claim, RDD rule, or Wave 1 authority. It does not convert A7 into a Wave 0 pass and does not authorize an A6 retry. The only implementation allowlist is `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`; needing a fourth tracked implementation file requires another design amendment. The specification and its new implementation plan are separate docs-only commits and are not part of that three-file implementation allowlist.

TDD must first reproduce both observed failures: a legacy shared cache missing exactly the eight locks must fail while a fresh official local-dir cache passes, and a correct baseline plus the current active lease must currently report set drift. Tests then cover the exact cache-preflight argv and ordering, no GPU before lease, the sole network-enabled stage, no-clobber cache/audit/receipt roots, cache audit/receipt hash binding, Task 8 offline read-only mount, legacy-cache rejection, each lock-file failure mode, active mutex contention, the exact three lease lifecycle paths, unapproved exclusions/extras, release integrity, complete failure closure, and exactly-once Task 8 invocation. Focused and complete CPU suites, Black, Ruff, both PowerShell parsers, `uv lock --check`, `git diff --check`, a complete historical artifact/image rehash, read-only Docker/RTX preflight, and Critical=0/Important=0 review are mandatory before an append-only implementation commit.

The owner's standing unattended delegation authorizes the recommended A8 design, its docs-only specification and implementation-plan commits, and implementation within the exact three-file allowlist after all TDD and review gates pass. It also authorizes at most one fresh A8-bound A7 diagnostic attempt from the reviewed clean candidate, with one new run ID, image, campaign, cache-preflight root, and lease. This paragraph supersedes only the earlier A7 owner-wait and no-standing-retry clauses in Sections 5.2.10 and 5.2.11 for that one A8-bound attempt; every historical no-reuse/no-overwrite rule remains in force. Any test, download, cache, Docker, GPU, identity, evidence, or diagnostic failure preserves the new objects and stops without retry or candidate modification. A successful diagnostic outcome also stops before Wave 1. RDD access, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.

#### 5.2.13 A9 deterministic Hugging Face download logging contract

The closed A8-bound campaign `wave0-a7-20260827T010418013Z` is bound to source commit `aa0c1895112f0310d5799f16281de825002d6c17`, specification commit `f24b6f226ad395c7c97c2dc59c093ce91248fe25`, plan commit `2ce1a4a41313ef8edd6311f21ea6ae61bd0783cd`, image ID `sha256:a5d385028e603272065c14c9759034d29a457b47ee8110a68176ffaad0613078`, and owner authorization `OWNER-STANDING-A8-20260827-UNATTENDED-01`. The fresh image build and CPU micro-check passed. The cache-preflight verifier then downloaded and verified both exact pinned snapshots, published a schema-valid PASS receipt with SHA-256 `bcd3db50afbcd103e970315ba7d6af468d94e031a2da6322dd36d043a7e8095c`, and emitted stdout exactly `PASS` plus one platform newline. Its stderr nevertheless contained 956 bytes with SHA-256 `62aed2c689a19d9782caaf514aece8c9094850978d9dff16c6320bfdf67d75a8`, consisting only of two `Fetching 4 files` progress streams and one server-supplied unauthenticated-request warning. The process contract therefore failed before GPU lease acquisition; Task 8 invocation count is zero. The failure diagnostic, campaign result, file manifest, and closure manifest have SHA-256 values `e3ea21be4671df79267b903f33c78347d5e81c3eb2c8b2f5807eb6a710beeb3b`, `71e3e75cb2756ae274f60b8d7c8ece4d34939fbfd1a48da8fd99f09c7e21e2dd`, `ac090dfd146f86a3f6c2128254a5db860370c9334206554a74d5ea9696173fdc`, and `a804a90c1c8ca508c485ffef9f1b2696eeb90fa34ed103aa50b65e6bd25a24fd`. All 48 manifest entries rehash without drift, and the 64,090 historical artifacts and 18 historical images remain preserved. That campaign, image, fresh cache, receipt, logs, and closure are immutable and cannot be modified, deleted, reused, retried, or reinterpreted as a pass.

The root cause is closed against the pinned official `huggingface_hub` 1.28.0 source. `snapshot_download` defaults to the Hugging Face `tqdm` implementation; its documented `HF_HUB_DISABLE_PROGRESS_BARS` switch is read when the package is imported. The same pinned package reads `HF_HUB_VERBOSITY` while configuring its root logger. HTTP response header `X-HF-Warning` is emitted with `logger.warning`, which explains the otherwise successful anonymous-download warning. The host supplied neither `HF_TOKEN` nor `HUGGING_FACE_HUB_TOKEN`, and the reviewed container argv did not propagate a token. Authentication alone is not a complete remedy because it does not disable progress bars, and introducing a secret is unnecessary for the two public pinned repositories.

Three fixes were considered. Accepting or normalizing selected stderr was rejected because progress rates, elapsed times, terminal control bytes, and server warning text are nondeterministic and would weaken the exact empty-stderr gate. Temporarily changing logging inside `assets.py` was rejected because it mutates library-global process state and expands production behavior beyond this orchestration defect. Passing a Hugging Face token was rejected because it adds secret handling yet still leaves progress output. A9 therefore changes only the cache-preflight container environment: it adds the exact ordered pairs `-e HF_HUB_DISABLE_PROGRESS_BARS=1` and `-e HF_HUB_VERBOSITY=error` immediately after `-e PYTHONPATH=/workspace/src` and before both volume mounts. No other stage receives these variables.

These values are control-plane settings, not an stderr allowlist. `HF_HUB_DISABLE_PROGRESS_BARS=1` disables the pinned library's progress renderers. `HF_HUB_VERBOSITY=error` suppresses warning-level `X-HF-Warning` messages while preserving raised exceptions. `val assets verify` continues to convert any `ModelAssetError`, `OSError`, or `ValueError` into a FAIL receipt and exit code 2; the launcher still requires exit code zero, stdout exactly `PASS` plus the platform newline, and a zero-byte stderr file. Missing, duplicated, reordered, differently cased, differently valued, or additional Hugging Face logging variables fail exact argv validation. `HF_TOKEN`, `HUGGING_FACE_HUB_TOKEN`, `HF_HOME`, `--env-file`, Docker secrets, token mounts, and wildcard environment propagation are forbidden. The exact anonymous payload download, repository revisions, four-file allowlist, metadata and zero-byte lock inventory, network mode `bridge`, no-GPU assertion, receipt validation, hashes, and no-clobber rules remain unchanged.

The cache-preflight audit records the complete updated Docker argv and hashes the still-empty stderr file. Before Task 8, the lease binds that audit and receipt exactly as in A8. Task 8 independently requires a 33-element `docker_argv` array: the prior 29 elements plus the two exact `-e`/value pairs at their fixed positions. It must reject missing, additional, renamed, reordered, or mutated environment arguments even if the receipt and hashes are recomputed. Task 8 remains `--network none`, uses the run-scoped cache read-only, and keeps `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`; its argv and behavior do not inherit the A9 online-stage logging settings.

A9 also advances the protected plan identity from the A8 plan to one new A9 implementation plan. The authoritative specification is this file at its new docs-only commit, and the A9 plan commit must be its direct child and must change only the new plan file. Both `scripts/start_wave0_a7.ps1` production identity paths and `scripts/run_wave0_a7.ps1` protected-lineage path must name that one A9 plan exactly. The later implementation commit is the source candidate. An older plan SHA or path, a plan not directly parented by the specification commit, a dirty linked or canonical worktree, or a source commit not containing the reviewed plan fails before any run ID or runtime object is created.

The implementation allowlist is exactly `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`. No Python production module, schema, Dockerfile, configuration, dependency file, lockfile, model pin, dataset contract, or historical evidence may change. TDD must first reproduce the observed process-contract failure by proving the current cache-preflight argv omits the two required settings. GREEN coverage must prove their exact order and values, absence from Task 8, 33-element Task 8 audit validation, rejection of every missing/extra/renamed/reordered/value-mutated logging argument, exact A9 plan identity in launcher and runner, empty-stderr retention, no GPU before lease, no-clobber publication, immutable failure closure, and exactly-once Task 8 invocation. Focused and complete CPU suites, targeted Black and Ruff, both PowerShell parsers, `uv lock --check`, `git diff --check`, complete historical artifact/image preservation, read-only Docker/RTX preflight, and Critical=0/Important=0 review remain mandatory.

The owner's latest unattended delegation authorizes this recommended A9 design, its separate docs-only specification and direct-child implementation-plan commits, implementation inside the exact three-file allowlist, and one fresh A9-bound A7 diagnostic attempt only after every local gate passes on a clean reviewed candidate. That fresh attempt must use a new source SHA, run ID, OCI image, campaign, cache root, and lease; it may not reuse or overwrite any A8 or earlier object. This authorization supersedes the A8 no-new-candidate/no-retry stop only for that one newly implemented A9 attempt. Any A9 test, download, cache, Docker, GPU, identity, evidence, or diagnostic failure preserves all new objects and stops without another fix or retry. An attributed, not-attributed, or inconclusive A7 diagnostic remains `WAVE0_NOT_PASSED`; it does not authorize Wave 1. RDD access, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.

#### 5.2.14 A10 Linux-container stdout byte contract

The closed A9-bound campaign `wave0-a7-20260827T021745408Z` is bound to source commit `09b95bf285596ab2d02fd452bc7fbb2ee956c691`, specification commit `ffd33555509237ced367898985eaf2433b89ed97`, plan commit `2666b13fc564ddef126db2d98c4bc3bc6542b96a`, image ID `sha256:b0f3f64275d99fd9965759db51d09fc9804bb3ae55d7a370a53a7ed65109bdc3`, and owner authorization `OWNER-STANDING-A9-20260827-UNATTENDED-01`. The fresh image build and CPU micro-check passed. The cache-preflight verifier downloaded and verified both pinned snapshots, published a schema-valid PASS receipt with no normative errors and SHA-256 `af709bb6317d73607bb28dacc51ac3af945e7138952a8e664f03e5a45044d7f3`, emitted zero stderr bytes with SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and emitted the five stdout bytes `50 41 53 53 0a` (`PASS\n`) with SHA-256 `c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431`. The launcher nevertheless closed at `model_cache_preflight` before a GPU lease; Task 8 invocation count is zero. The failure diagnostic, campaign result, 48-entry file manifest, and closure manifest have SHA-256 values `45ab59a8adb0897819912a6cdacd05c6d442dfee572aec320be16175fd56a1c9`, `7e0147bebc17bda440941ac1888143d16fe49250d5c4d9f913fb0f5aa3f26c34`, `676bff30ce5b6a93dbbf3dd2f80e812f1c8dcd92e4587cfcf3ede558568d6d9c`, and `690dc7974eb7b4c7fa87f8fc3fe2935c253f4c88e58bf61bb83f3f781ed68337`. Its pre-campaign baseline preserves 64,140 artifacts and 19 images, and all 50 files in the closed A9 campaign rehash exactly. The campaign, image, cache, receipt, logs, manifests, and baseline are immutable and cannot be modified, deleted, reused, retried, or reinterpreted as a pass.

The failure is a host/container representation mismatch in the Task 7 process gate, not a model, download, metadata, stderr, Docker, CUDA, or GPU failure. The pinned Linux container emits line feed byte `0a`. `Invoke-A7Native` reads that pipe without changing the line ending and `Write-A7NewText` reproduces the same five UTF-8 bytes in the audit log. The current Task 7 comparison instead constructs its expectation with `[Environment]::NewLine`; on the Windows 11 host that value is carriage return plus line feed bytes `0d 0a`. Therefore the observed `PASS\n` cannot equal the current host-derived `PASS\r\n` predicate. That one false predicate is independently sufficient to produce the generic `A7 model-cache preflight process contract failed` terminal even though the receipt is PASS and stderr is empty. Task 8 currently reads the stdout log as logical lines, so it would accept both byte representations; it was not invoked in A9.

Three corrections were considered. Accepting either LF or CRLF as equivalent was rejected because the formal producer is a pinned Linux container and the second representation is unnecessary ambiguity. Normalizing all native-process output was rejected because it would change build, inspect, CPU-micro-check, and future diagnostic evidence outside the failed boundary. A10 therefore fixes only the cache-preflight success token: its canonical UTF-8 representation is exactly the five bytes `50 41 53 53 0a`, with no carriage return, byte-order mark, leading bytes, trailing spaces, or additional newline. `Invoke-A7ModelCachePreflight` must require exit code zero, the decoded PowerShell string exactly ``"PASS`n"``, and stderr exactly empty before inspecting the receipt. Because the captured string is written without normalization, that predicate also requires the published stdout log to have exactly the canonical five bytes.

`Test-Task7AuditBinding` in Task 8 must independently require the hash-bound Task 7 stdout file to contain the same exact five bytes, not merely one logical line equal to `PASS`. It must reject `PASS` without a newline, `PASS\r\n`, multiple newlines, leading or trailing whitespace, a byte-order mark, different case, additional text, an empty file, and any linked or non-regular stdout path. The existing exact stdout SHA-256 binding remains mandatory and cannot substitute for the byte-content check. The stderr path remains a regular zero-byte file with the empty-file SHA-256. No log is filtered, trimmed, split, rewritten, normalized, or republished after the process exits.

Every other A9 and A8 invariant remains unchanged: anonymous pinned downloads, exact revisions and payload/metadata/lock inventories, `HF_HUB_DISABLE_PROGRESS_BARS=1`, `HF_HUB_VERBOSITY=error`, absence of tokens and wildcard environment forwarding, the 33-element cache-preflight Docker audit, `--network bridge` only for that CPU-only stage, the PASS receipt, no-clobber roots, source/image/specification/plan binding, and pre-lease failure closure. Task 8 remains networkless and GPU-bound only after the lease, mounts the verified run-scoped cache read-only, and uses `HF_HUB_OFFLINE=1` plus `TRANSFORMERS_OFFLINE=1`. A10 changes no generic native runner, Python production module, schema, Dockerfile, configuration, dependency, lockfile, model pin, dataset contract, warning rule, numerical threshold, research claim, or Wave 1 authority.

A10 advances the protected plan identity to one new A10 implementation plan. This specification revision must be one docs-only commit. The plan commit must be its direct child and must change only `docs/superpowers/plans/2026-08-27-val-wave0-a10-linux-stdout-bytes.md`. The later implementation allowlist is exactly `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`; needing a fourth tracked implementation file is a hard stop. Both Task 7 plan-identity locations and the Task 8 protected-lineage location must name the A10 plan exactly. An older plan, wrong parent, dirty linked or canonical worktree, changed historical object, or source SHA outside the reviewed lineage fails before a new run ID or runtime object.

TDD must first use a real child process that writes raw `PASS\n` bytes and prove the current Task 7 host-derived comparison rejects it. A separate real Task 8 binding test must prove the current logical-line reader accepts at least `PASS\r\n` or `PASS` without a newline and therefore fails the desired rejection assertion. Only after both RED signals may production code change. GREEN coverage must accept exactly `PASS\n` in Task 7 and Task 8 and reject no newline, CRLF, extra newline, whitespace, byte-order mark, case mutation, extra text, empty stdout, nonzero exit, nonempty stderr, missing/invalid receipt, linked paths, stale destinations, and recomputed audit hashes over noncanonical bytes. It must retain exact A10 plan identity, no GPU before lease, exactly-once Task 8 invocation, immutable failure closure, and every A9 logging-environment test. Focused and complete CPU suites, targeted Black and Ruff, both PowerShell parsers, `uv lock --check`, `git diff --check`, full historical artifact/image preservation, read-only Docker/RTX preflight, and Critical=0/Important=0 review remain mandatory.

The owner's persistent unattended delegation, recorded for this bounded sequence as `OWNER-STANDING-A10-20260827-UNATTENDED-01`, authorizes the recommended A10 design decision, its separate docs-only specification and direct-child plan commits, implementation inside the exact three-file allowlist, and at most one fresh A10-bound A7 diagnostic attempt after every local gate passes on a clean reviewed candidate. This authorization does not retry or modify A9: the new attempt must use a new source SHA, run ID, OCI image, campaign, cache root, and lease while preserving every earlier object. Any A10 test, Docker, download, cache, identity, evidence, lease, GPU, or diagnostic failure closes and preserves that attempt without another fix or retry. A diagnostic outcome remains `WAVE0_NOT_PASSED` even when attributed; a successful A10 transport gate grants no independent authority for Wave 1. RDD access, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.

#### 5.2.15 A11 independently calibrated same-host statistical-replay contract

The one authorized A10-bound A7 campaign `wave0-a7-20260827T034653088Z` is closed and immutable. It is bound to source commit `2cb3e38b4328eee2b3497571e05565c73f4691c9`, specification commit `c7eb8ae5aaccdfc4bbf681e8f07a994bee5e30c0`, plan commit `a2cd4b0abc353ddcc4e950c35ddc55e72c22292e`, OCI image `sha256:ea6bde836cad9fd96c3c8999fb00a7fe7aaecdc7b34d870e0ad9b6ce710f2afa`, and owner authorization `OWNER-STANDING-A10-20260827-UNATTENDED-01`. Its two uninstrumented controls, five instrumented model replicas, and five isolated-VJP replicas all returned `RECORDED` with no errors and every aggregate invariant true. The environment, model-assets, model-contract, aggregate, campaign-result, pre-closure manifest, historical-preservation, and closure-manifest SHA-256 values are respectively `7fc82adaa6053a1d6a9617410b27fa5200882d7c99758567bef2c60c8a704e8f`, `c1e1620fdaff57e3fc4424a393d925b194301f866e3215089303ec3ad8500483`, `1258c45e5b8b672ca81cc8e2b5af9d955bb22eece3b1aabcf0485174c1a706c0`, `f4a6f0f3fd2cc54f319e65141fa1b0a0367a6e14e2baa0df58268b051270251f`, `3f10fbfe8bf33c89fddb71c71e58457f738fa92d933ad05115fa1e66e3126239`, `55f78146f201d090807fcc62a836ec9db82604e3a878ca2323de85edda85f6e2`, `93c9093efebfe7c78a9cf6ae6a10f264b52271aee434236a71d68801b9e0ad3f`, and `3f3c1e548d0454bc81c44e8130e710e7e8d0b47264f69afdb96560d7fbc92162`. The immutable terminal is `WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`; it is not an A6 retry, a Wave 0 pass, or calibration data.

The successful diagnostic closes the registered A7 causal question on the pinned stack. `decoder-2/feature-2`, the first recorded backward callback, had exact forward value, grid, and result tensors and an exact incoming result gradient across all five instrumented replicas. Its outgoing grid gradient remained exact, while its outgoing value gradient differed in nine of ten pairwise comparisons with maximum relative L2 `3.9217500408193284e-05`. Five isolated VJP replicas starting from the one hash-bound snapshot reproduced the same role-specific divergence in nine of ten pairwise comparisons with maximum relative L2 `9.589993240038289e-06`; no isolated outgoing grid gradient differed. All nine operation IDs exhibited at least one outgoing-value-gradient byte divergence across each five-replica component. The 2,394 model parameter-gradient records were finite, the scalar loss remained exactly `0x1.b1c6ea0000000p+8`, only the exact nine registered `grid_sampler_2d_backward_cuda` warnings occurred per model or VJP backward, and peak allocated VRAM remained below 1 GiB.

This evidence matches the pinned official implementation rather than merely correlating with a warning. Transformers 5.15.0 [`MultiScaleDeformableAttention`](https://github.com/huggingface/transformers/blob/v5.15.0/src/transformers/models/rt_detr/modeling_rt_detr.py) calls `torch.nn.functional.grid_sample` once per feature level with bilinear interpolation, zero padding, and `align_corners=False`. PyTorch 2.12 [documents](https://docs.pytorch.org/docs/2.12/generated/torch.nn.functional.grid_sample.html) that CUDA backward may be nondeterministic and not easily switched off. Its tagged [`GridSampler.cu`](https://github.com/pytorch/pytorch/blob/v2.12.0/aten/src/ATen/native/cuda/GridSampler.cu) explicitly declares `grid_sampler_2d_backward_cuda` nondeterministic because of `atomicAdd`, uses `safe_add_2d` accumulation for `grad_input`, and directly assigns each `grad_grid` output. The nondeterminism alert occurs before the `output_mask` check, so requesting only `grad_grid` from the official backward does not create a clean strict-deterministic split path. The combined source and intervention evidence identifies CUDA value-gradient accumulation as the first divergence. It does not prove that any particular numerical bound is adequate for a future run.

Three response designs were reviewed. A custom deterministic CUDA backward was rejected because it would introduce a new compiled numerical implementation, build toolchain, binary provenance surface, BF16 correctness proof, performance contract, and long-term maintenance burden into an active-learning portfolio whose research contribution is not CUDA kernel engineering. A CPU backward island was rejected because it would add nine GPU-to-CPU-to-GPU gradient boundaries per training step and materially change the canonical training topology and throughput. Directly replacing the A3 limits with values selected from A6 or A7 was rejected as post-hoc acceptance. A11 therefore proposes a **separately calibrated same-host empirical replay envelope with an independent holdout cohort**. This is a statistical reproducibility contract, not a deterministic-kernel claim.

The owner's delegated A11 design decision permits this exact proposal and docs-only amendment but does not substitute for reviewing its committed text. Once the owner approves this written section, that approval satisfies the later-review condition in Sections 5.2.9 and 19. Section 5.2.15 will then supersede the A3 `math.isclose`, `1e-3`, and `0.99999` numerical acceptance limits only for a future A11 calibration and validation; it does not alter the A3 through A10 historical receipts or verdicts. The A3 warning exception, exact-comparison fields, and all non-numerical gates remain normative. No A6 or A7 value can satisfy A11 by implication.

A11 retains the exact detector, RT-DETR and DINOv2 revisions and assets, processor, 300 queries, four-class reset and label mapping, initialization order, synthetic fixture, seed 17, BF16 labeled path, Math-only SDPA boundary, three decoder layers, three feature levels, `disable_custom_kernels == true`, pinned RTX 4090 identity, package and CUDA versions, optimizer and scheduler recipe, warning identifier and count, 22 GiB peak-allocation ceiling, source-hash rules, atomic no-clobber publication, and checkpoint round-trip contract. It changes no RDD country, split, formal seed, label budget, acquisition arm, calibration-label rule, metric, research fit, epoch count, or `22 × 3 = 66` primary-fit total. `VAL_DATA_ROOT` remains unset throughout A11. A11 introduces no custom kernel, CPU fallback, dependency, model freeze, model replacement, data access, or Wave 1 work.

The calibration and validation populations are closed before either is executed:

- The **calibration cohort** contains exactly 12 fresh-process, one-step A6 feasibility replicas under one never-used calibration run ID, fresh OCI image, fresh campaign root, and fresh checkpoint roots. Each process reloads the pinned model cache read-only, initializes from the exact seed-17 preimage, executes the full labeled forward, bounded nine-warning backward, clipping, AdamW and scheduler update, checkpoint save/load, and receipt publication. No process or CUDA context is reused between replicas.
- The **validation cohort** contains exactly 12 different fresh-process replicas under a different never-used validation run ID, a separately built fresh OCI image, a separate campaign root, separate checkpoint roots, and a newly acquired lease. No validation process, receipt, checkpoint, tensor, metric, or runtime observation contributes to calibration.
- Each cohort produces all `12 choose 2 = 66` unordered pair comparisons. Comparisons are pairwise rather than only against replica zero so the gate cannot depend on one unusually favorable canonical draw. Replica IDs are the zero-padded closed sequences `calibration-00` through `calibration-11` and `validation-00` through `validation-11`; missing, extra, duplicate, reordered, or reused IDs fail closed.
- A6 and A7 observations are historical causal and design evidence only. Their values, checkpoints, and receipts cannot be copied into either cohort, counted toward its 12 replicas, or used by the threshold derivation function.

Within each cohort, all 12 replicas must share the exact source/specification/plan commits, OCI image ID, base-image digest, model-cache inventory, model and processor revisions and hashes, config and fixture hashes, package versions, driver/CUDA identity, GPU name and UUID, and lease record. Across the two cohorts, those static and semantic identities must remain exact except for the OCI image ID and image tag: each phase rebuilds the unchanged candidate with its own run-bound labels, so those two image identities must differ while their source/specification/plan/base labels remain exact. The validation run ID, image ID/tag, campaign root, model-cache root, lease ID/path, container IDs, replica receipt/checkpoint paths and hashes, timestamps, and audit paths must all be different from calibration. The calibration lease must be released and hash-recorded before the validation lease is acquired; phase overlap, source change, reused runtime identity, or a different GPU UUID fails before validation model initialization.

Twelve replicas is a pre-registered bounded engineering replication count: it doubles the six observations that exposed the A6 failure while keeping Wave 0 below the cost of one research fit. The 66 pairwise distances share replicas and are therefore not independent observations. A11 makes no IID, population-coverage, confidence-interval, p-value, or long-run-trajectory claim from those pairs; it uses their complete maximum only to define and challenge a same-host empirical envelope.

Every pair first passes the complete exact-comparison contract from Section 5.2.5: pre-update parameter and replay-preimage digests, semantic inputs, sampler order, scalar loss hex, optimizer groups and hyperparameters, warning inventory, deterministic-attention evidence, checkpoint discrete fields, state key order, shapes, dtypes, integer and Boolean values, non-training buffers, source identities, package versions, image bindings, and parent receipt hashes. Any exact-field mismatch, missing receipt, non-finite scalar or tensor, failed individual feasibility invariant, checkpoint round-trip failure, peak allocation above 22 GiB, wrong GPU, or wrong warning inventory fails the cohort before numerical calibration or validation can pass.

For an exact-compatible unordered pair `(i, j)`, A11 computes the following CPU-float64 distances over the same canonical parameter inventory and state mapping already used by A3:

```text
gradient_relative_difference = |g_i - g_j| / max(|g_i|, |g_j|)
vector_relative_l2           = ||v_i - v_j||_2 / max(||v_i||_2, ||v_j||_2)
cosine_defect                = 1 - <v_i, v_j> / (||v_i||_2 ||v_j||_2)
```

`g` is the positive finite pre-clip global gradient norm. `v` is evaluated separately for detector model update, backbone model update, and the detector/backbone AdamW `exp_avg` and `exp_avg_sq` states, yielding one gradient metric plus relative-L2 and cosine-defect metrics for six closed vector roles. Zero-norm, non-finite, missing, unexpected, reordered, shape-mismatched, or dtype-mismatched vectors fail closed. Values outside their mathematical domains also fail rather than being clamped, except that a cosine within `1e-12` of either endpoint because of float64 accumulation may use the existing bounded endpoint normalization before computing its defect.

The exact role keys are `gradient_norm`, `model_update.backbone`, `model_update.detector`, `optimizer_state.backbone.exp_avg`, `optimizer_state.backbone.exp_avg_sq`, `optimizer_state.detector.exp_avg`, and `optimizer_state.detector.exp_avg_sq`. `gradient_norm` has only `relative_difference`; every other role has exactly `relative_l2` and `cosine_defect`. Pair order is lexicographic `(left_replica_id, right_replica_id)` with `left < right`; metric order is lexicographic over the complete dotted key. Additional metric keys, aliases, or omitted keys fail receipt validation.

A11 registers the following practical-effect ceilings before calibration. They are owner-reviewed engineering non-vacuity limits selected after causal attribution, not calibration outputs. Historical A6 or A7 values neither count as samples nor prove compliance:

```text
threshold_multiplier         = 1.5     # 0x1.8000000000000p+0
gradient_relative_difference <= 0.01    # 0x1.47ae147ae147bp-7
every vector_relative_l2     <= 0.10    # 0x1.999999999999ap-4
every cosine_defect          <= 0.005   # 0x1.47ae147ae147bp-8; cosine >= 0.995
```

For each of the 13 metric keys, let `M_m` be the maximum over its 66 calibration-pair values. Its frozen validation threshold is the binary64 result `T_m = 1.5 * M_m`, computed once in lexicographic pair and metric-key order. The calibration receipt records the complete 66-value inventory for every key, each `M_m`, each `T_m` as both a JSON number and Python `float.hex()`, the formula identifier `wave0-a11-pairwise-max-times-1.5-v1`, and all source receipts and checkpoint hashes. No floor is added: if a metric is exact throughout calibration, its threshold is zero. Calibration passes only if every observation is valid, all 66 comparisons are complete, and every `T_m` is at or below its applicable practical-effect ceiling. A ceiling breach, overflow, non-finite result, mismatched hexadecimal serialization, or recomputation difference publishes a fail-closed calibration result and prohibits validation. The threshold receipt is atomic, no-clobber, content-addressed, and immutable once published.

The two new aggregate receipt types both use `schema_version == 1` and retain the existing canonical receipt-content hash rule. A successful calibration threshold receipt has `receipt_type == "statistical-replay-calibration"`, `normative.phase == "calibration"`, `normative.status == "RECORDED"`, and the exact calibration terminal below. A validation aggregate receipt has `receipt_type == "statistical-replay-validation"`, `normative.phase == "validation"`, `normative.status` in the closed set `{"PASS", "FAIL"}`, and the matching exact terminal below. A failed calibration publishes no threshold receipt at the success destination; it publishes the existing atomic campaign-result plus a bound A11 failure diagnostic at separate no-clobber destinations, leaving the threshold destination nonexistent. Those failure artifacts record the attempted success destination, first failed stage or invariant, complete error list, run/source/specification/plan/image/owner identities, and exact failure terminal; they are not `statistical-replay-calibration` receipts, cannot advertise a threshold inventory, and cannot be consumed by validation. Every new schema object has `additionalProperties: false`.

Both receipts require closed metadata for run, source, specification, plan, image, base image, owner authorization, timestamp, and receipt-content identities. Their normative payloads require the exact phase, 12-item ordered replica map with existing schema-v3 feasibility receipt and checkpoint path/size/SHA-256 bindings, 66-item ordered pair map, 13-key metric inventory, exact-comparison results, practical ceilings with decimal and `float.hex()` values, phase invariants, historical-preservation binding, status, and terminal. Calibration additionally requires the derivation identifier, every raw pair metric, every `M_m`, every frozen `T_m`, and the threshold-inventory digest. Validation additionally requires the calibration receipt path/size/SHA-256/run identity, cross-phase equal/distinct identity maps, every raw validation metric, per-key minimum/median/maximum, and the all-pairs decision. Missing, extra, reordered, duplicated, differently typed, non-finite, contradictory, unbound, or recomputation-inconsistent data fails semantic validation even if it passes JSON Schema.

The calibration invariant set is exactly `replica_count_exact`, `replica_ids_exact`, `replica_receipts_valid`, `cohort_identity_exact`, `pair_count_exact`, `pair_order_exact`, `metric_keys_exact`, `exact_comparisons_pass`, `finite_metrics`, `thresholds_recomputed`, `thresholds_within_ceilings`, `publication_no_clobber`, and `historical_evidence_preserved`. The validation invariant set is exactly `replica_count_exact`, `replica_ids_exact`, `replica_receipts_valid`, `cohort_identity_exact`, `pair_count_exact`, `pair_order_exact`, `metric_keys_exact`, `exact_comparisons_pass`, `finite_metrics`, `calibration_binding_exact`, `cross_phase_static_identity_exact`, `cross_phase_runtime_identity_distinct`, `all_pairs_within_thresholds`, `all_pairs_within_ceilings`, `publication_no_clobber`, and `historical_evidence_preserved`. Every listed invariant must be present and true; an additional or truthy-but-non-Boolean value fails.

Validation loads exactly one verified calibration-threshold receipt before model initialization and permits no threshold override. All 66 validation-pair values must be finite, at or below their corresponding frozen `T_m`, and at or below the independent practical-effect ceiling. One out-of-envelope metric fails the entire validation; there is no permitted failure rate, averaging rescue, metric substitution, threshold recomputation, or retry. Validation reports the full pairwise distribution—minimum, maximum, all individual values, and the binary64 average of the 33rd and 34th values after ascending numeric sort as the even-count median—for auditability, but only the all-pairs predicate determines the numerical verdict. A validation result cannot add its own observations to calibration or mutate the calibration receipt.

The calibrated claim is deliberately narrow: on the pinned Windows 11/WSL2/Docker/Linux/RTX 4090 software and hardware identity, fresh same-seed one-step replicas are empirically replayable within a separately calibrated and independently validated envelope despite the disclosed CUDA atomic accumulation. A11 must use `empirically_replayable_same_host` or `calibrated_statistical_replay`; it must never label the training step, CUDA backward, model, or project `deterministic`, `bitwise reproducible`, or reproducible across GPUs, hosts, drivers, CUDA/PyTorch releases, or long training trajectories. The later three-seed budget curves and individual observations remain the primary protection against research-level training variability. A11 supplies only the Wave 0 feasibility boundary required before those experiments.

Calibration success has terminal `WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`. If an owner-authorized execution explicitly covers both phases, that terminal alone permits the already-reviewed validation phase to begin; it does not permit RDD access or any other work. Validation success, together with every retained environment, asset, model-contract, finite-loss, BF16 backward, finite-gradient, update, VRAM, checkpoint, warning, deterministic-attention, exact-comparison, evidence, and aggregate invariant, has terminal `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`. Any calibration, validation, identity, Docker, GPU, lease, checkpoint, receipt, threshold, preservation, or aggregate failure has terminal `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`. No failed phase may be retried, repaired in place, or reinterpreted as a pass.

All A2 through A10 commits, images, campaigns, caches, checkpoints, receipts, tensor bundles, logs, manifests, failures, and audit corrections remain byte-for-byte immutable. A future A11 plan must define an exact tracked-file allowlist, RED/GREEN TDD sequence, schema and semantic-validation surfaces, paired-comparison implementation, threshold serialization, two-phase orchestration, fresh identities, historical rehashing, and stopping evidence. CPU tests may prove formulas, ordering, schema closure, no-clobber behavior, and synthetic pass/fail cases, but cannot claim RTX validation. Before any implementation commit, focused and complete CPU suites, targeted Black and Ruff, both PowerShell parsers for touched scripts, `uv lock --check`, `git diff --check`, complete historical artifact/image preservation, and Critical=0/Important=0 review remain mandatory.

The owner's delegated design decision authorizes only this recommended A11 specification amendment. After this docs-only commit and self-review, the written specification must be presented for owner review before invoking `writing-plans`. Implementation, Docker build, calibration, validation, GPU lease, or any A11 runtime attempt requires later explicit authorization tied to the reviewed plan and candidate. RDD access, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden even if A11 later passes.

### 5.3 Frozen diversity encoder

The sole diversity encoder is **DINOv2-small** from [`facebook/dinov2-small`](https://huggingface.co/facebook/dinov2-small) at revision:

```text
ed25f3a31f01632728cabb09d1542f84ab7b0056
```

The `model.safetensors` artifact is 88,249,960 bytes with SHA-256:

```text
ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1
```

That pinned model card and the [official DINOv2 repository](https://github.com/facebookresearch/dinov2) identify the current code and weights as Apache-2.0. An older inspected Hugging Face revision had a CC-BY-NC-4.0 card; it is not permitted for this design. The implementation must archive the pinned revision’s model card and license notice alongside the dependency lock so a future upstream card change cannot silently change the decision.

For each retained image, the encoder produces the final-layer, post-LayerNorm CLS token (384 dimensions) using the checkpoint’s pinned 224-pixel preprocessing. The vector is converted to float32 and L2-normalized. Embeddings are computed once per manifest, stored without pixels, and bound to the image, processor, model revision, and tensor-file hashes. The encoder is never fine-tuned.

### 5.4 Research-critical runtime lock

The implementation plan must preserve these exact core versions:

| Component | Version | License/purpose |
|---|---|---|
| Python | 3.12.11 | Runtime |
| uv | 0.8.15 | Normative lock generation and validation |
| SciPy | 1.18.0 | Exact RT-DETR labeled-training dependency |
| PyTorch | 2.12.0+cu126 | BSD-style; detector training |
| torchvision | 0.27.0+cu126 | BSD-style; tensor/image operations |
| Transformers | 5.15.0 | Apache-2.0; RT-DETR and DINOv2 implementations |
| pycocotools | 2.0.10 | BSD-style; COCO detection evaluation |
| CUDA runtime | 12.6 wheel runtime | Canonical GPU runtime |

The official [PyTorch previous-versions matrix](https://pytorch.org/get-started/previous-versions/) is the installation authority for the paired torch/torchvision wheels. All transitive versions, source revisions, hashes, and license notices will be resolved and frozen during implementation; doing so is not authorized in the design stage.

## 6. Experimental lifecycle

### 6.1 Formal seeds and budgets

Formal seeds are exactly `17`, `29`, and `43`. For formal-pool size `N`, the cumulative image budget is:

```text
B(p) = ceil(p × N), where p ∈ {0.02, 0.05, 0.10, 0.20, 0.40, 1.00}
```

The primary unit is acquired images. When an image is acquired, the oracle reveals all valid boxes and class labels for that image. Revealed box counts are a secondary realized-cost axis and may be computed only after acquisition. No method may use hidden box counts to form or fill a budget.

### 6.2 Shared start and retraining

For each seed:

1. Rank the formal pool by `SHA256("initial" || seed || item_id)` and choose the group-aware prefix of `B(0.02)` images. This 2% set and its trained checkpoint are shared by every arm.
2. Train the shared 2% model from the same pinned pretrained detector base.
3. Each arm uses the previous-budget model only to score/select the next acquisition batch.
4. At 5%, 10%, 20%, and 40%, retrain that arm **from the same pretrained base**, not from the previous active-learning checkpoint.
5. Train one shared **100% acquired-budget ceiling** because every arm has acquired every formal-pool image and revealed all of its labels at that point. The immutable calibration assignment still withholds approximately 20% of acquired images from gradient training, so this name never means “100% of images entered weight training.”

The 2% point is plotted as a shared reference, not falsely counted as five independent fits.

### 6.3 Formal fit count

Per seed:

```text
1 shared 2% fit + (5 arms × 4 later budget fits) + 1 shared 100% acquired-budget ceiling = 22 fits
```

Across three seeds:

```text
3 × 22 = 66 primary detector fits
```

The 66 excludes the pilot and the registered label-noise auxiliary experiment. Any implementation report that gives a different primary count is a protocol violation.

### 6.4 Fixed training recipe

Every primary and ceiling fit uses:

- input: aspect-preserving resize so the longest side is 640, zero-pad bottom/right to 640×640, and transform boxes identically;
- training augmentation: deterministic-seed horizontal flip with probability 0.5 and brightness/contrast/saturation jitter of at most 0.1; no mosaic, mixup, random crop, copy-paste, or synthetic data;
- evaluation preprocessing: resize/pad only;
- optimizer: AdamW, detector learning rate `1e-4`, backbone learning rate `1e-5`, weight decay `1e-4`;
- schedule: 30 epochs, one-epoch linear warm-up, then cosine decay to zero;
- batch size: 8 images, BF16 automatic mixed precision, gradient norm clipping at 0.1;
- checkpoint: final epoch; no early stopping and no test-driven checkpoint selection;
- sampler: seed-deterministic shuffle with a recorded ordered-item digest; and
- reproducibility: `torch.use_deterministic_algorithms(True)`, cuDNN benchmark off, deterministic workspace settings, recorded RNG states, the exact Section 5.2.5 allowlisted grid-sample backward exception, and verified Section 5.2.15 calibration-threshold plus validation-aggregate receipt bindings after `WAVE0_A11_PASS`.

The pilot must fail on any unregistered nondeterministic operation, incorrect warning count, missing replay evidence, or violation of a frozen Section 5.2.15 validation threshold during a registered replay comparison. It cannot silently broaden the Section 5.2.5 exception or recalibrate the A11 envelope. The design claims independently validated, calibrated same-host empirical replay on the canonical locked environment, not deterministic or bitwise-identical training across runs, GPUs, hosts, drivers, or libraries.

Acquired images assigned to the calibration/dev partition in Section 9 count against the budget but are excluded from weight training. Consequently, the model normally trains on approximately 80% of the acquired images; this is identical across arms and is explicitly reported.

## 7. Acquisition strategies

### 7.1 Common contract

All arms receive only:

- unlabeled image bytes and public item metadata;
- IDs of already acquired images and their revealed-label training/calibration partition;
- the previous-budget detector checkpoint;
- frozen DINOv2 embeddings when the strategy requires them; and
- the requested number of new images.

All arms return an ordered list of unique, currently unlabeled `item_id` values. A common deterministic group-aware budget filler enforces exact counts. Final ties are always ordered by ascending `item_id`.

### 7.2 Random

At the first post-2% round, random creates one complete deterministic order using:

```text
SHA256("random" || seed || item_id), then item_id
```

Every later random acquisition is the next prefix of that same order after removing already acquired items. It is never re-randomized per round.

### 7.3 Raw-query uncertainty contract

Let the final RT-DETR decoder produce 300 raw class-logit vectors `z_q ∈ R^4` and normalized boxes `b_q^F`. Let `b_q^P` be the corresponding penultimate decoder-layer box for query `q`. No score threshold, NMS, top-detection postprocessor, ground-truth count, or predicted-count normalization is used.

For each query and class:

```text
s_qc = sigmoid(z_qc)
o_q  = max_c(s_qc)
pi_qc = softmax(z_q)_c
P_q = [1 - o_q, o_q*pi_q0, o_q*pi_q1, o_q*pi_q2, o_q*pi_q3]
l_q = 1 - IoU(b_q^F, b_q^P)
```

`P_q` is a project-defined normalized five-state distribution: derived background plus four conditional foreground classes. It is not described as a native RT-DETR no-object output. Coordinates are clipped to `[0,1]` only for the localization IoU computation, and a degenerate box has IoU zero.

Entropy query uncertainty is:

```text
e_q = -sum_k(P_qk * log(max(P_qk, 1e-12))) / log(5)
u_entropy,q = 0.75*e_q + 0.25*o_q*l_q
```

Margin query uncertainty is:

```text
margin_q = P_q,(1) - P_q,(2)       # largest minus second-largest state
m_q = 1 - margin_q
u_margin,q = 0.75*m_q + 0.25*o_q*l_q
```

For either strategy, image uncertainty is the arithmetic mean of the largest 20 query uncertainties among all 300 queries. This fixed-cardinality statistic is permutation-invariant and does not automatically reward images with many thresholded detections. An image with zero postprocessed detections is still scored from all raw queries; it is never assigned zero by a “no detections” special case. A mathematically confident background-only output may naturally approach zero under the formula.

The implementation must include hand-computed synthetic tests covering:

- confident foreground produces low class uncertainty;
- ambiguous background-versus-foreground produces high uncertainty;
- ambiguous foreground classes produce high uncertainty;
- stable logits with penultimate/final box disagreement increase localization uncertainty;
- query permutation leaves the image score unchanged;
- changing a postprocessing threshold leaves the score unchanged;
- zero thresholded detections still yield the formula-derived score; and
- exact score ties resolve by ascending `item_id`.

### 7.4 Core-set diversity

Core-set uses only the frozen 384-D L2-normalized DINOv2 embeddings. Distance is cosine distance:

```text
d(a,b) = 1 - dot(a,b)
```

Starting with every previously acquired embedding as the center set, greedy k-center repeatedly selects the unlabeled candidate with the largest distance to its nearest center, adds it as a center, and updates distances until the batch is full. The shared 2% start guarantees at least one center.

#### 7.4.1 Canonical numerical execution

Every formal core-set or hybrid k-center selection runs only on `cuda:0` in the canonical RTX 4090 environment recorded by the experiment lock. Embeddings and distance accumulators are contiguous row-major float32; TF32 is disabled. Candidates begin in ascending `item_id` order. Existing centers are applied in acquisition-event order `(round, rank, item_id)`, and newly selected centers are applied one at a time in selection order. Candidate rows are processed in fixed chunks of 4,096, with only the final chunk shorter. Each cosine distance is clamped to `[0, 2]`, and the nearest-center accumulator is updated by elementwise minimum after each center.

Before comparison, each nonnegative distance becomes an integer key:

```text
distance_key(d) = int64(floor(clamp(d, 0, 2) × 10,000,000 + 0.5))
```

Selection sorts by `distance_key` descending, then `item_id` ascending. Raw floating-point distance is never a later tie breaker. This quantized key makes the formal item list unique in the locked environment; the project does not claim arbitrary CPU/GPU equivalence.

An optimized implementation must produce the **exact same ordered item-ID sequence** as a simple registered reference implementation on every hand-built toy matrix and on fixed pilot subsamples covering small, equal-distance, near-boundary, multi-chunk, and hybrid-shortlist cases. The reference uses the same float32 CUDA device, center/candidate order, quantization rule, and per-center update semantics, but evaluates candidate-center pairs directly. Any item-ID mismatch fails the pilot even when distance error is numerically small.

The reviewer CPU path replays only checked-in synthetic/reference fixtures with precomputed distance keys and expected IDs. It demonstrates logic and auditability, not full-data selection identity across arbitrary hardware.

Tests must compare the optimized implementation to a brute-force toy matrix, verify nested selections, and verify invariant output under candidate input permutation.

### 7.5 Hybrid uncertainty plus diversity

Hybrid first ranks every unlabeled image by the entropy image score. For a required batch of `b` images, it takes the first `min(5b, remaining_pool_size)` candidates, then runs the same canonical, quantized greedy k-center rule over that candidate set relative to all previously acquired centers and within-batch selections. The factor 5 is frozen before the pilot. Uncertainty ties and final diversity-key ties both resolve by ascending `item_id`.

The five formal arms are therefore exactly:

1. `random`
2. `entropy`
3. `margin`
4. `core_set`
5. `hybrid_uncertainty_diversity`

No arm may be added, removed, or tuned after formal evaluation without creating a separately versioned experiment.

## 8. Oracle firewall and queue lifecycle

### 8.1 Threat model

The firewall prevents accidental or strategy-code access to unrevealed labels and evaluation data. It does not claim protection from a malicious machine administrator who can inspect all host storage or process memory.

Formal execution separates four trust domains:

| Component | Trust | May read hidden annotations? | Output |
|---|---|---:|---|
| Manifest curator | Trusted, pre-run | Yes | Public manifest and sealed manifests |
| Strategy worker | Untrusted | No | Ordered acquisition request |
| Oracle adapter | Trusted | Yes, source pool only | Newly revealed labels and ledger event |
| Evaluator | Trusted, sealed | Test/shift only | Aggregate metrics, no per-item labels |

The strategy worker runs in an OCI container on WSL2/Docker with allowlisted read-only mounts. Unrevealed annotation roots, source-test files, shift-test files, curator tables, and host dataset paths are not mounted. The worker receives an unlabeled image mirror with opaque IDs; acquired annotations are mounted separately. The evaluator receives a checkpoint and sealed test manifests, then emits aggregate tables.

### 8.2 Forbidden information

Before acquisition, the strategy cannot access:

- annotation paths or filenames;
- pool/test/shift ground-truth boxes or classes;
- hidden per-image class counts, box counts, difficulty labels, or future labels;
- a dataloader or cache initialized with unrevealed annotation objects;
- exception text, logs, metrics, result files, environment variables, or configs encoding hidden labels; or
- symlink, junction, path traversal, or network routes to sealed storage.

Country is retained for final audit but omitted from strategy-worker inputs so methods cannot implicitly balance domains.

### 8.3 Adversarial verification

Before the pilot passes, automated firewall tests must prove:

1. `../` and absolute-path traversal fail;
2. symlinks and Windows junctions to sealed roots are rejected after real-path resolution;
3. environment/config injection cannot add mounts or annotation paths;
4. a reused dataloader cannot retain hidden annotation objects;
5. strategy logs, exceptions, tracebacks, cache keys, and output schemas contain only allowlisted fields;
6. evaluator output omits per-item ground truth and predictions unless using the synthetic reviewer fixture;
7. read attempts against source test, China Drone, or unrevealed pool annotations fail; and
8. changing hidden annotation contents without changing public inputs leaves the pre-acquisition strategy output unchanged.

### 8.4 Formal evaluation embargo

Pilot execution can never mount, read, query, or receive metrics from the frozen source test or China Drone. During formal acquisition, detector training, job resume, checkpoint validation, and artifact validation, source-test and shift metrics remain cryptographically and operationally sealed; logs and user interfaces may show training diagnostics and acquired-only development diagnostics but no source-test/shift predictions or aggregate values.

The trusted run coordinator issues a `formal_completion_seal` only after it verifies and content-addresses all of the following for the same experiment ID:

- all 66 primary checkpoint artifacts;
- all three shared 2% ledgers, all arm/round acquisition ledgers, and all three 100% acquired-budget ceiling ledgers;
- every training manifest, calibration assignment/status/temperature-fit receipt, queue event chain, model-contract receipt, and dataset-manifest digest;
- successful resume/idempotence and artifact-schema validation; and
- a complete hash inventory with no missing, substituted, or post-hoc-modified artifact.

Only then may the sealed evaluator be unmounted from its embargo state and run one manifest-driven batch over **all** registered checkpoints for both the source test and China Drone. Its output is keyed to the completion-seal digest. A technical retry is allowed only with byte-identical checkpoint/evaluation inputs and the same batch manifest; no partial result can influence whether or how another fit is run.

Evaluator predictions or aggregates cannot flow back to a strategy, trainer, resume decision, artifact-validity decision, protocol configuration, calibration fit, threshold, or model-selection decision. The result store is write-only from the evaluator until the full batch finishes, after which aggregate reporting artifacts may be exposed.

If any source-test or shift output is created or exposed before the 66-fit completion seal, the experiment ID is contaminated and permanently ineligible for continuation or publication. The output and cause remain in a forensic audit record, but every pilot/formal artifact under that experiment ID is invalidated; execution restarts under a new reviewed protocol version and experiment ID.

### 8.5 Human-in-the-loop queue without fake humans

The project provides a library/API/CLI queue contract, not an annotation UI. Each image follows:

```text
unlabeled → queued → exported → labeled | abstained → validated → acquired
```

`rejected` is a terminal validation outcome with a reason code and can be explicitly requeued by a new audited event. Every transition records event ID, item ID, experiment/seed/arm/round, previous/new state, schema version, acquisition rank and score where applicable, actor type (`simulated_oracle` or `external_import`), timestamp, payload digest, and reason.

The queue supports deterministic manifests plus CVAT and Label Studio export/import adapters. Import validates item IDs, image dimensions, class IDs, box bounds, duplicate boxes, schema version, and manifest digest. `abstained` and `rejected` images remain budget-spent when they were sent for labeling; formal oracle replay is expected to return valid labels, so these states are exercised only in synthetic workflow tests unless a real external labeling study is separately approved.

All formal experiments use `simulated_oracle`: the trusted adapter reveals existing annotations after selection. Reports must say “simulated annotation queue” and must not report annotator minutes, inter-annotator agreement, cognitive workload, or monetary human cost.

## 9. Calibration and confidence evaluation

### 9.1 Budget-aware calibration partition

For every acquired image, compute:

```text
uint64(SHA256("calibration-v1" || item_id)[0:8]) mod 5
```

Remainder zero assigns the image to calibration/dev; other remainders assign it to detector training. This 20% assignment is immutable, arm-independent, and label-blind. Calibration images count fully toward acquired-image and revealed-box budgets but are never used to update detector weights. Only labels already acquired by that arm and budget are eligible. Source-test and China Drone labels are never calibration data.

### 9.2 Temperature scaling contract

Calibration is evaluation-only and never changes acquisition ranking. Entropy and margin always use raw logits from Section 7.

On each acquired calibration/dev set, form a fixed candidate denominator: the 100 largest raw query-class sigmoid scores per image before NMS or thresholding, ordered by score descending and then `(item_id, query_index, class_id)` ascending. Match candidates one-to-one to ground truth in that order. A candidate is correct only when class matches and IoU is at least 0.5; unmatched candidates are incorrect. Fit one scalar temperature `T ∈ [0.05, 10]` by minimizing binary negative log likelihood on these correctness outcomes. Apply `sigmoid(logit/T)` to source-test and shift-test candidates with the identical denominator construction after the formal evaluation embargo lifts.

Temperature fitting is permitted only when the acquired calibration set has all of:

- at least 200 images;
- at least 100 ground-truth boxes;
- at least 20 ground-truth boxes in each of D00, D10, D20, and D40; and
- at least 50 correct and 50 incorrect candidate outcomes.

If any gate fails, `calibration_status = INSUFFICIENT`, temperature and calibrated metrics are null, and raw metrics plus exact denominator counts remain reported. Missing values are not imputed or treated as zero.

### 9.3 Calibration metrics

For candidate confidence `p_i`, correctness `y_i ∈ {0,1}`, and denominator size `n`, binary Brier score is exactly:

```text
Brier = (1/n) × sum_i((p_i - y_i)^2)
```

Adaptive ECE sorts candidates by `(p_i, item_id, query_index, class_id)` ascending. Let `G = min(15, n)`. Proposed internal cuts are `ceil(j×n/G)` for `j = 1..G-1`; if a cut would split an equal-confidence run, move it right to the end of that run, then remove duplicate/end cuts. This produces deterministic, nonempty, contiguous bins and may yield fewer than 15 bins. For final bins `g`:

```text
adaptive_ECE = sum_g((|g|/n) × |mean_g(p) - mean_g(y)|)
```

For raw and, when eligible, calibrated confidence, report Brier, adaptive ECE, actual bin count, candidate/image count, positive/negative outcome counts, per-class ground-truth support, scalar temperature, and eligibility status. A zero denominator is `INSUFFICIENT` and produces null metrics.

Localization-aware ECE (LaECE) is a possible post-v0.1 research extension. It is not a v0.1 required metric, completion gate, success criterion, or headline claim because this release does not freeze a LaECE formulation/version.

Acquisition uncertainty, post-hoc confidence calibration, and detection accuracy are three separate tables and must not be rhetorically conflated.

## 10. Metrics and analysis

### 10.1 Detection metrics

COCO evaluation uses IoU thresholds 0.50:0.05:0.95, area range `all`, and maximum 100 detections per image. At every budget, seed, and arm, report:

- mAP50–95 (primary detector performance);
- AP50;
- per-class AP50–95;
- per-class recall at maxDets=100;
- macro recall, minimum-class recall, and D40 recall;
- per-country metrics for each source country;
- aggregate frozen source-test metrics; and
- China Drone shift metrics in a separate table/figure.

Country/class supports and empty-slice status must accompany slice metrics. No source-country average is weighted or macro-averaged without naming the rule.

### 10.2 Budget curves

Plot every individual seed curve and overlay mean and median; do not show only a final aggregate. Each source-test metric is plotted against:

1. acquired images (primary horizontal axis);
2. acquired-image fraction;
3. revealed boxes (secondary labeling-cost axis); and
4. cumulative detector GPU-hours (compute-efficiency axis).

The 2% point is visibly labeled shared. China Drone is plotted separately and excluded from label-efficiency integration.

Every plot, table, artifact schema, and future README uses the exact label **100% acquired-budget ceiling**. Its caption states that all pool images have been acquired and all labels revealed, while the immutable calibration split still excludes approximately 20% of those images from gradient training.

### 10.3 Normalized area under the budget curve

Primary AUBC uses source-test mAP50–95 at fractions `0.02, 0.05, 0.10, 0.20, 0.40`, trapezoidal integration, and range normalization:

```text
nAUBC = trapz(mAP, budget_fraction from 0.02 to 0.40) / (0.40 - 0.02)
```

The 100% acquired-budget ceiling does not enter AUBC. Report nAUBC per seed/arm, paired arm-minus-random deltas by seed, their mean and median, and all-seed sign consistency.

### 10.4 Labels to target

For each seed, the target is 90% of that seed’s shared **100% acquired-budget ceiling** source mAP50–95. That denominator comes from a model for which every pool image was acquired and every label revealed, while only the non-calibration portion entered gradient training. `labels_to_90pct_ceiling` is the smallest **observed** budget point reaching the target; no curve smoothing or interpolation creates a success. Report images and revealed boxes at that point. If no point through 40% reaches it, report right-censored `> B(0.40)` and `> boxes_at_40pct`, never a numeric success.

The per-seed target-cost truth table is fixed:

| Hybrid | Random | Per-seed result | Required image/box comparison |
|---|---|---|---|
| Observed | Observed | `PASS` only if both costs qualify; otherwise `FAIL` | Hybrid acquired images **and** revealed boxes at first target attainment must each be no greater than random’s corresponding values |
| Observed | Censored through 40% | `SUPPORTIVE` only if both lower-bound checks pass; otherwise `FAIL` | Hybrid attained-target images must be `<= B_random(0.40)` and hybrid attained-target boxes must be `<= boxes_random_at_40pct` |
| Censored through 40% | Observed | `FAIL` | Random reached the target and hybrid did not |
| Censored through 40% | Censored through 40% | `INSUFFICIENT` | No cost ordering is inferred |

`SUPPORTIVE` satisfies the per-seed target-cost condition but is reported as a censored comparison, not an exact savings estimate. If **any** seed is `INSUFFICIENT`, “reduced labeling cost” is forbidden as a headline claim. The all-seed nAUBC and rare/minimum-class safety conditions in Section 2.3 still apply, shift results cannot rescue a source failure, and simulated-oracle budgets cannot be converted into human time or money.

### 10.5 Class imbalance and acquisition behavior

No hidden class reweighting is used for selection. The detector’s fixed RT-DETR loss is identical across arms. At each round report:

- selected-image proportion by source country;
- acquired images and revealed boxes by country;
- revealed box distribution by D00/D10/D20/D40;
- first acquisition round in which each class is discovered;
- rare-class recall/AP and minimum-class metrics; and
- divergence between selected-country proportions and the remaining unlabeled pool, calculated by the trusted analyst only after acquisition.

These are diagnostics, not inputs to selection. China Drone never participates in AUBC or forced domain balance.

### 10.6 Compute metrics

Per scoring job and detector fit, record wall time, GPU time, peak allocated VRAM, peak reserved VRAM, CPU time, host RAM peak when available, number of images, and artifact sizes. Aggregate:

- acquisition/scoring seconds per round;
- detector GPU-hours per arm and budget;
- preprocessing/embedding cost, reported once rather than charged repeatedly to core-set/hybrid;
- total primary experiment GPU-hours; and
- canonical peak VRAM.

Random’s score time includes order/materialization overhead; core-set and hybrid include distance-selection time. Human annotation time is absent by design.

## 11. Label noise and distribution shift

### 11.1 Registered label-noise auxiliary

Noise is an auxiliary sensitivity experiment and does not alter the 66 primary fits. For each seed, reuse the clean 20% acquisition manifests from only `random` and `hybrid_uncertainty_diversity`. Calibration images remain clean. Let `M` be the number of acquired, positive **training-partition** images for that arm/seed manifest, and define:

```text
K        = floor(0.10 × M)
n_drop   = floor(0.40 × K)
n_class  = floor(0.30 × K)
n_jitter = K - n_drop - n_class
```

Rank eligible images by `SHA256("noise-v1-image" || seed || arm || item_id)`, then `item_id`, and take the first `K`. Assign the first `n_drop` to box drop, the next `n_class` to class flip, and the remaining `n_jitter` to box jitter. When `K = 0`, the corruption is an explicitly reported no-op; it never forces one image to be corrupted.

Within each affected image, rank target boxes by `SHA256("noise-v1-box" || seed || arm || item_id || canonical_box_index)`, then canonical box index, and modify only the first box. Drop removes that box. Class flip changes it to the next class modulo four. Jitter takes four consecutive unsigned 16-bit words from `SHA256("noise-v1-jitter" || seed || arm || item_id || canonical_box_index)`, maps each word `u` to `delta = -0.10 + 0.20×u/65535`, offsets center x/y by `delta_x×width` and `delta_y×height`, scales width/height by `1+delta_w` and `1+delta_h`, converts back to corners, and clips to image bounds.

The immutable corruption manifest records `M`, `K`, all three realized counts, ordered affected IDs, target box IDs, operations/parameters, and a no-op status. It is hash-bound to the clean 20% acquisition manifest, dataset-manifest digest, seed/arm, and immutable training/calibration assignment; a mismatch is a hard failure. This creates `2 arms × 3 seeds = 6` auxiliary fits. Report clean-versus-noisy deltas; do not claim a noise-aware acquisition strategy.

### 11.2 Shift evaluation

After the Section 8.4 formal completion seal lifts the evaluation embargo, every formal checkpoint is evaluated, without adaptation, on curated China Drone in the same sealed batch as source evaluation. No China Drone label or metric influences pilot decisions, formal method choice, calibration, thresholding, stopping, resume, or artifact validation. Report the same detection and eligible calibration metrics, but label every result `shift_only` and keep it outside source nAUBC and success criteria.

## 12. Pilot gate and protocol freeze

### 12.1 Pilot shape

The pilot cannot start until a hash-bound aggregate receipt has terminal `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED` and the owner separately authorizes Wave 1. An A11 calibration-only, failed, missing, or differently bound receipt keeps the pilot forbidden.

The pilot uses only the 8% pilot engineering partition, seed 17, and four arms: random, entropy, core-set, and hybrid. Budgets are 2%, 5%, and 10% of that reduced pool. The 2% start is shared, so the pilot requires:

```text
1 shared 2% fit + (4 arms × 2 later fits) = 9 pilot fits
```

The pilot does not access either frozen test. It evaluates engineering validity through training loss, acquired-only development metrics, synthetic uncertainty fixtures, firewall tests, artifact replay, and runtime extrapolation. Pilot results cannot be mixed into formal curves.

### 12.2 Pass gates

Formal execution starts only if all conditions pass:

1. the Section 5.2 model-contract receipt has status `PASS`, and the Section 5.2.15 validation aggregate has status `PASS` plus terminal `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`; both are hash-bound to the permitted lineage and the aggregate binds its calibration threshold receipt;
2. all nine fits complete on RTX 4090 with no OOM, NaN, Inf, unauthorized deterministic-algorithm fallback, or frozen Section 5.2.15 replay-envelope violation;
3. detector loss is finite and decreases from the median of the first 10% of steps to the median of the final 10%;
4. each uncertainty strategy has score standard deviation at least `1e-6` over at least 100 unlabeled pilot images;
5. core-set/hybrid produce the exact reference item-ID sequences on registered toy matrices and pilot subsamples;
6. all oracle-firewall adversarial tests pass, global source/shift duplicate exclusions are applied, and no group crosses a role;
7. interrupted jobs resume to the same final artifact hashes as uninterrupted jobs on the canonical host;
8. every budget ledger equals its exact target with unique item IDs and nested acquisition sets;
9. peak allocated VRAM is at most 22 GiB;
10. the conservative projection for **every one** of the 20 formal arm/round acquisitions (five arms at 5%, 10%, 20%, and 40%) is at most 15 minutes; and
11. the conservative step-count projection for all 66 primary detector fits is at most 240 RTX 4090 GPU-hours.

Any failure stops formal execution. The response is to fix the engineering/protocol cause, increment the relevant protocol/component version, rerun the entire pilot, and record the failed attempt. It is not permissible to inspect frozen-test results, weaken a gate silently, or cherry-pick a passing run.

After the pilot passes, freeze the manifest digest, exclusions, model/processor revisions, training recipe, seeds, budgets, acquisition formulas, tie breaks, metrics, calibration gate, and claim rules. Subsequent changes require a new experiment ID and complete formal rerun.

### 12.3 Conservative compute projection

The pilot cost gate uses component-specific workload models, not a single linear multiplier from reduced-pool wall time. Every bound is measured on the canonical RTX 4090 lock, includes a 15% safety factor, and is stored with raw timing samples, projected dimensions, formula version, and environment hash.

#### Detector training

After discarding model-load/warm-up steps, define `t_train_step_bound = 1.15 × p95(steady_state_step_seconds)` across all pilot fits. Separately measure bounded model-load, final-checkpoint serialization, and acquired-only development inference costs. For formal fit `j`, its frozen acquisition/calibration manifest gives exact `n_train_j` and `n_cal_j`, and `drop_last=false` gives:

```text
steps_per_epoch_j = ceil(n_train_j / 8)
T_fit_j = 30 × steps_per_epoch_j × t_train_step_bound
          + 1.15 × max(pilot_model_load_seconds)
          + 1.15 × max(pilot_checkpoint_write_seconds)
          + ceil(n_cal_j / 8) × 1.15 × p95(pilot_dev_inference_batch_seconds)
```

The projection enumerates the exact shared/per-arm jobs rather than multiplying an average fit: three shared 2% jobs, 60 arm/budget jobs, and three shared 100% acquired-budget ceiling jobs. Summing all 66 `T_fit_j` values must be at most 240 GPU-hours. Formal source/shift evaluation is embargoed and is not hidden inside this fit total.

#### Detector uncertainty scoring

For each entropy, margin, or hybrid arm/round, use that round’s exact projected remaining-pool `N_r`, inference batch size 8, 300 queries, four final logits, and all decoder-layer box tensors required by the localization contract. The bound is:

```text
T_detector_score(r) = bounded_model_load
                      + ceil(N_r / 8) × bounded_inference_batch
                      + raw_output_bytes(r) / bounded_materialization_throughput
                      + bounded_score_and_sort(N_r)
```

Inference and materialization bounds come from p95 batch timings and the lower 5th-percentile measured write throughput, each with the 15% safety factor in the conservative direction. Random has deterministic hash/order materialization only; core-set has no detector-scoring charge.

#### Core-set selection

For each core-set round, project the actual remaining candidates `N_r`, existing centers `c_r`, new batch `b_r`, dimension `d=384`, 4,096-row chunks, and canonical float32 update order. Initializing or validating the nearest-center cache costs `O(N_r × c_r × d)`; applying the new centers costs `O(N_r × b_r × d)` with the remaining row count reduced after each selection. The timer model evaluates the exact tile/update counts using a canonical kernel benchmark grid that brackets the projected `N_r`, `c_r`, and `b_r`, including the 40% round. It takes the slowest bracketing throughput plus 15%; it never extrapolates only from the pilot’s small `b`.

#### Hybrid selection

For hybrid round `r`, report separately: detector score/materialization, deterministic top-`5b_r` shortlist construction, nearest-distance initialization from `c_r` centers over `s_r=min(5b_r,N_r)` candidates, and `b_r` canonical k-center updates over the shrinking shortlist. Its diversity path is modeled as `O(s_r × c_r × 384) + O(s_r × b_r × 384)` with exact tile counts and the same slowest-bracket-plus-15% rule.

The final acquisition projection table shows every component and conservative total for every arm/round; the **maximum**, not median, is compared with the 15-minute gate. A separate project-total estimate reports, without mixing categories: 9 pilot fits, 66 primary fits, 6 noise fits, detector acquisition scoring, DINOv2 embedding, k-center/hybrid work, the embargoed batch evaluation, and report generation. The 66-fit definition and its 240-hour gate remain identifiable inside that total.

## 13. Reproducibility and evidence architecture

### 13.1 Declarative experiment system

The future implementation will be a library plus thin CLI commands driven by validated, immutable experiment manifests. Notebooks may render published artifacts but cannot contain authoritative split, training, scoring, or evaluation logic.

Every run records:

- experiment, dataset-manifest, queue-schema, strategy, and metric-schema versions;
- Git commit and dirty-worktree status;
- Python/package lock digest;
- detector and encoder revision/file hashes;
- GPU, driver, CUDA runtime, OS/container image, precision, batch size, and image size;
- seed and RNG-state digests;
- input/output artifact hashes and lineage;
- timestamps, wall/GPU time, and memory peaks; and
- exact acquired IDs, their ordering, scores, budget ledger, and queue events.

Jobs are idempotent and resumable: an existing artifact may be reused only when its complete input fingerprint matches. Published result tables are regenerated from immutable metric records, not manually copied.

### 13.2 Canonical and optional hardware

The **RTX 4090 24 GB** is canonical for preprocessing benchmarks, all pilot fits, all 66 primary fits, the six noise fits, acquisition scoring, and official runtime/VRAM numbers. The fixed host prevents cross-device timing mixtures.

**Google Colab high-tier** is optional for a portability smoke test, reviewer reproduction of the tiny synthetic fixture, or recovery experimentation. Colab results are labeled non-canonical. They cannot satisfy completion gates, replace missing RTX 4090 fits, enter latency/GPU-hour comparisons, or be combined into formal seed aggregates.

### 13.3 Artifact lineage

Conceptual artifact classes are:

```text
model/package lock → executable model-contract receipt
  → upstream archive digests
  → joint source/shift curated manifest + exclusions + split groups
    → public unlabeled mirror / sealed oracle manifests
      → frozen embedding matrix
      → acquisition request → queue events → acquired-label ledger
        → training/calibration manifest → checkpoint + calibration receipt
          → all 66 checkpoint/ledger hashes → formal completion seal
            → one embargoed source/shift evaluation batch
              → immutable metrics tables → plots/model card
```

Each arrow is represented by input hashes. An artifact store may contain local derived objects but the remote repository contains only schemas, small synthetic fixtures, configuration examples, aggregate results, and permitted identifiers/hashes.

## 14. Reviewer fast path

A reviewer with no GPU and no RDD download must be able to run or inspect a five-minute path that demonstrates the project’s engineering contribution using a tiny original synthetic fixture and checked-in precomputed artifacts:

1. display the frozen experiment contract, passing model-contract receipt, detector/encoder hashes, 66-fit calculation, and formal completion-seal digest;
2. replay one acquisition round for all five arms from synthetic raw-query logits and a small embedding matrix;
3. show why selected items differ using per-query entropy/localization terms and nearest-center distances;
4. verify exact budgets, nesting, deterministic ties, queue state transitions, and artifact hashes;
5. run path/symlink/config/log oracle-leakage tests against fake sealed annotations;
6. render precomputed individual-seed budget curves, nAUBC, rare-class recall, calibration status, and compute-cost tables; and
7. link each displayed result back to its immutable manifest and metric record.

The README should lead with this path, followed by a one-command synthetic verification and static result figures. Full-data reproduction is documented separately. A large dashboard is not required.

This prevents the project from becoming an ordinary active-learning notebook: the visible deliverable is an auditable experimental loop with security boundaries, replayable decisions, and cost-aware evidence—not a sequence of exploratory cells.

## 15. Milestones, completion gates, and release boundary

The project is planned for eight weeks, one milestone per week. A milestone is complete only when its gate is evidenced in immutable artifacts or tests.

| Milestone | Week | Deliverable | Completion gate |
|---|---:|---|---|
| M0 Protocol and license lock | 1 | Reviewed design, sources/license record, exact model/runtime decisions | User approves this spec; no unresolved scope decision |
| M1 Executable model contract | 2 | Locked runtime/model load and synthetic model-contract probe | Receipt proves every Section 5.2 invariant before RDD processing |
| M2 Data, model, and firewall foundation | 3 | Global source/shift dedup, group/split manifests, sealed oracle, deterministic base, hashed DINO embeddings | Global manifest and firewall audits pass; no cross-role component/group |
| M3 Acquisition and queue | 4 | Five strategies, budget ledger, queue export/import/replay | Hand-computed uncertainty and brute-force core-set tests pass |
| M4 Pilot and freeze | 5 | Nine-fit pilot report and protocol snapshot | Every Section 12 gate passes |
| M5 Embargoed formal execution | 6 | 66 primary checkpoints, acquisition ledgers, training/calibration manifests, hash inventory | Formal completion seal issued with zero source/shift metric exposure |
| M6 One-shot evaluation and robustness | 7 | Batch-unsealed source/China Drone evaluation, calibration metrics, six noise fits, compute accounting | Embargo batch completes; six noise fits complete; no feedback path; all statuses explicit |
| M7 Portfolio release | 8 | Reviewer path, README, model/data cards, static report | Five-minute path passes clean; self-audit passes; tag `v0.1.0` approved |

The `v0.1.0` tag is not created during design. It is the M7 boundary after full evidence and explicit user approval.

## 16. Risks and mitigations

| Risk | Consequence | Pre-registered mitigation/decision |
|---|---|---|
| RT-DETR docs and executable outputs disagree | Invalid uncertainty ranking | Release-blocking synthetic model-contract receipt before RDD processing; no ad-hoc formula change |
| DINOv2 upstream license metadata changes | Reuse uncertainty | Pin the Apache revision/file hash and archive its model card/notice; reject old noncommercial-card revision |
| A duplicate crosses source and China Drone | Inflated source/shift evidence | Joint global SHA/pHash/DINO review; exclude the whole conflicting component before roles |
| Hidden annotations leak through code/config/cache | Invalid active learning | Container mount separation, opaque IDs, sealed evaluator, adversarial firewall suite |
| Formal test metrics are viewed before all fits freeze | Human tuning/continuation bias | Completion seal, batch-only evaluator unseal, contaminated experiment-ID invalidation |
| GPU distance ties change selected item identities | Non-reproducible arms | Canonical float32 RTX execution, integer distance keys, exact reference item-list tests |
| Rare D40 examples make averages misleading | Harm hidden by mAP | D40 and minimum-class recall gates, supports, discovery rounds, individual seeds |
| Calibration subset is too small at low budgets | Unstable confidence metrics | Budget-charged stable split plus explicit eligibility gates/INSUFFICIENT status |
| Active methods acquire box-dense images | Image savings hide box cost | Report revealed-box curves and require image and box criteria for cost claim |
| Three seeds invite overconfident inference | Fragile statistical story | Individual curves, paired deltas, mean/median, sign consistency; no confirmatory p-values |
| Formal compute exceeds practical limit | Incomplete portfolio | Component/complexity-aware worst-round projections, 15-minute gates, and 240-hour fit cap |
| Fixed 30 epochs under/over-train at some budgets | Budget-dependent optimization bias | Same registered recipe, 100% acquired-budget ceiling, training diagnostics; interpret limitations rather than tune on test |
| China Drone is too different | Shift scores collapse | Report honestly as separate shift result; no adaptation or result rescue |
| Simulated oracle is mistaken for human validation | Misleading product claim | Explicit actor/state labels and prohibition on human time/IAA/cost claims |
| Dataset cannot be redistributed | Reviewer friction | Source downloader/checksums plus original tiny synthetic fast path; never mirror data |

## 17. Statistical reporting rules

With only three seeds, formal reports use individual observations, mean, median, paired seed deltas, ranges, and all-seed sign consistency. They do not present small-sample p-values as proof. The three individual seed curves remain primary and cannot be replaced by a bootstrap interval.

If an appendix reports evaluation-set sampling sensitivity, it uses 2,000 deterministic **split-group bootstrap** replicates after the formal evaluation embargo. For the source test, groups are stratified by source country: within each country, sample with replacement the same number of `split_group_id` values as observed, and retain every image belonging to each selected group. A group selected multiple times is duplicated as a complete cluster with replicate-local image IDs before recomputing the metric. China Drone is bootstrapped independently by its own `split_group_id` values and is never pooled with source strata. The RNG stream is derived from `SHA256("group-bootstrap-v1" || checkpoint_hash || dataset_role)`.

These intervals describe fixed-checkpoint sensitivity to the grouped evaluation sample only. They are not image-IID intervals, between-seed method uncertainty, evidence of strategy superiority, or a substitute for individual seed curves.

Every figure/table identifies dataset role, arm, seed aggregation, budget unit, calibration status, and whether the point is shared. Failed jobs, invalid artifacts, protocol versions, and censored targets remain visible. A negative or null active-learning result is a valid project result when the protocol passed.

## 18. Design-stage acceptance checklist

- [x] The project is differentiated from the five existing CV projects by a reproducible active-learning system, not another detector benchmark.
- [x] Scope is exactly four source countries plus China Drone shift-only; US, Norway, and all other datasets are out.
- [x] The detector, frozen encoder, revisions, hashes, preprocessing representation, and critical package versions are exact.
- [x] Detector licensing is Apache-2.0; the chosen DINOv2 revision is Apache-2.0 and the old conflicting revision is excluded.
- [x] RDD is conservatively treated as CC BY-SA 4.0 and pixels/annotations are not redistributed.
- [x] Global source-plus-shift duplicate components, source splitting, one-time curator coverage audit, and oracle access rules do not depend on detector results.
- [x] A release-blocking executable probe resolves the RT-DETR no-object/output-shape ambiguity before RDD processing.
- [x] The A2 reset contract covers decoder heads, the denoising embedding, `enc_score_head`, and exact frozen RDD label mappings in one fixed seed-17 RNG order without reusing COCO rows.
- [x] The A2 executable contract covers both label-free and labeled RT-DETR paths, including encoder/top-k and every decoder/encoder/denoising auxiliary classification tensor reachable by labeled loss.
- [x] The recorded 80-vs-4 failure remains immutable evidence of the narrower Option A contract and cannot be reinterpreted as a pass.
- [x] The recorded A2 `grid_sampler_2d_backward_cuda` failure remains immutable evidence; A3 permits exactly nine disclosed backward warnings and requires fixed same-host numerical replay bounds without claiming bitwise training identity.
- [x] The recorded A3 source-hash failure remains immutable evidence; A4 canonicalizes only Python newline bytes under the disclosed `python-source-lf-normalized-sha256-v1` rule and keeps every non-newline source change fail closed.
- [x] The recorded A4 warning-contract failure remains immutable evidence; A5 exposes the complete rejected warning inventory without changing any warning parser, allowlist, count, category, receipt, replay, or pass criterion.
- [x] The recorded A5 11-warning diagnostic remains immutable failure evidence; A6 keeps the nine-warning grid-sample exception exact and confines labeled forward-through-backward attention to the source-bound SDPA Math backend without accepting fused-attention nondeterminism.
- [x] The recorded A6 numerical replay failure remains immutable evidence; A7 permits only one successfully launched bounded control/instrumented/isolated-VJP attribution campaign without changing thresholds, model identity, training claims, or Wave 0 status.
- [x] The three closed pre-GPU A7 launch failures and their images remain immutable; a checked-in launcher must close build, image, CPU-micro-check, lease, and Task 8 transitions before another attempt can be separately authorized.
- [x] Checkpoint roots and destinations fail closed when pre-existing, and receipt publication requires atomic no-clobber semantics rather than check-then-replace.
- [x] Formal source/shift evaluation stays embargoed until a complete 66-fit artifact seal exists; premature output invalidates the experiment ID.
- [x] The 2% reference is one shared fit; `1 + 5×4 + 1 = 22` per seed and `22×3 = 66` primary fits.
- [x] Entropy and margin cover background, conditional class ambiguity, localization instability, fixed top-20 aggregation, zero postprocessed detections, and deterministic ties.
- [x] Core-set/hybrid formal selection has one canonical float32 RTX execution, integer distance keys, fixed chunk/update order, and exact reference item-list gates.
- [x] Calibration labels count against budget, are excluded from detector weights, never affect acquisition, and have an explicit insufficiency status.
- [x] Class imbalance, label noise, distribution shift, duplicate leakage, compute, and censored target rules are registered.
- [x] The target-cost truth table blocks an insufficient seed, label-noise rounding is exact, and bootstrap inference resamples country-stratified groups rather than images.
- [x] The labeling queue is a simulated-oracle workflow contract, not a claim of a real annotator study or full inspection UI.
- [x] Three-seed inference is descriptive and does not rely on overconfident p-values.
- [x] RTX 4090 is canonical; Colab is optional/non-canonical and cannot fill formal gaps.
- [x] The eight-week plan has observable completion gates and a five-minute reviewer path.
- [x] A8 uses a fresh official run-scoped model cache before the lease, preserves exact lock metadata, and excludes only the exact current lease-lifecycle paths from historical-set comparison.
- [x] A9 keeps cache-preflight stderr byte-empty through fixed Hugging Face logging controls, and A10 makes the successful Linux-container stdout token byte-exact as `PASS\n` in both Task 7 and Task 8.
- [x] The closed A10-bound A7 campaign remains immutable `ATTRIBUTED` evidence: identical operands and incoming gradients reproduce CUDA `grid_sample` outgoing-value-gradient divergence while outgoing grid gradients remain exact.
- [x] A11 uses disjoint 12-replica calibration and validation cohorts, all 66 within-cohort pairs, a pre-registered max-times-1.5 derivation, fixed non-vacuity ceilings, exact discrete replay, and no deterministic or cross-host claim.
- [x] No unresolved implementation placeholder remains in this document.

## 19. Decisions that require a new reviewed protocol version

The following cannot be changed as an implementation convenience: included countries, dataset roles, split ranges/salt, global group/dedup thresholds and exclusions, detector/encoder identity, executable model-contract invariants, uncertainty equations, hybrid factor, canonical distance quantization/order, formal seeds/budgets, evaluation embargo, calibration split/gates, 30-epoch recipe, primary metrics/AUBC, censoring/claim gates, component-aware pilot caps, numerical replay thresholds, and 66-fit definition.

A required change must produce a written spec revision, explain the trigger, invalidate incompatible pilot/formal artifacts, and receive user approval before execution. On 2026-08-25 the owner delegated the A3 design and execution decision after reviewing the incompatibility finding and recommended bounded-exception approach. After the preserved A3 source-hash failure, the owner separately approved the recommended A4 canonical-newline design. After the preserved A4 warning-contract failure, the owner approved the A5 diagnostic-only design direction. After A5 recovered the exact 11-warning inventory and stopped without a feasibility receipt or checkpoint, the owner approved A6 Option A, the Math-only SDPA deterministic-attention design. After the preserved A6 campaign passed every individual feasibility stage and every exact comparison but failed all five numerical replay comparisons, the owner approved the recommended A7 bounded kernel-attribution diagnostic. The A7 implementation was committed, but three separately authorized launch attempts stopped before GPU attribution because of session-side orchestration failures; the latest concatenated the OCI labels and was closed with exact preservation evidence. On 2026-08-26 the owner approved the recommended checked-in launcher-hardening design and then approved the exact Section 5.2.10 written specification. The later standing unattended delegation superseded that earlier implementation wait for the bounded A8 sequence in Section 5.2.12, the A9 sequence in Section 5.2.13, and the A10 sequence in Section 5.2.14 only. The completed A10-bound campaign then attributed the first divergence to CUDA `grid_sample` outgoing value gradients; the owner's continuing delegated-design instruction authorized selecting the recommended A11 statistical-replay direction and writing Section 5.2.15, but not its implementation, runtime execution, RDD access, Wave 1, or publication.
