# Vision Active Learning Loop — Formal Design Specification

**Status:** A3 determinism design amendment owner-authorized / implementation plan pending
**Milestone:** M0 complete for the original design; A2 implementation evidence frozen at a normative determinism failure; A3 amendment active
**Owner approval date:** 2026-08-23
**Approved commit baseline:** `8b456800077d45fa9a6bb0dcd4ecb70c0edc89c6`
**A2 amendment authorization date:** 2026-08-24
**A2 amendment baseline:** `97d5789c0ca657f58e79f761a353f275e97a147b`
**A3 amendment authorization date:** 2026-08-25
**A3 amendment baseline:** `db0dc52e10d5e58852b84e1d321c2efa06a82d30`
**Original specification date:** 2026-08-23
**Repository:** `vision-active-learning-loop`
**Target roles:** Computer Vision Engineer, Machine Learning Engineer, AI Engineer
**Design choice:** Modified Option B — multi-country object-detection active learning
**Runtime gate:** Wave 0 must verify every executable model-contract invariant from a new run-scoped evidence chain. The environment, model-contract, and feasibility receipts must share a non-empty run identity and exact parent bindings; each runtime observation must independently report uv `0.8.15` and SciPy `1.18.0`. Historical or fixed-name evidence is never current by implication. The only permitted nondeterministic CUDA operation is the exact A3 backward exception in Section 5.2.5; any other warning, missing observation, or gate failure stops execution and returns the protocol to design review.
**Implementation status:** Owner authorization records the A3 design decision only. This commit amends the authoritative specification; it does not itself authorize old evidence to be reinterpreted, make any prior failure pass, or claim that A3 implementation or execution has completed.

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

The existing BF16 backward, finite-gradient, parameter-update, peak-VRAM, checkpoint round-trip, and clean A/B replay gates remain mandatory. A3 changes only the executable meaning of the CUDA backward determinism gate as specified in Section 5.2.5; the finite labeled-forward invariant continues to supplement rather than replace the training gates. Any failed or unobservable invariant halts the protocol. The detector, uncertainty formula, extractor, package, or checkpoint cannot be changed ad hoc; a different contract requires a new reviewed spec version, new probe, and new receipt.

#### 5.2.4 No-clobber and evidence-preservation invariants

Every subsequent A3 execution uses a new run ID and a new run-scoped evidence chain. Before any A3 feasibility-A, feasibility-B, or clean A/B replay process starts, both its exact checkpoint destination and its checkpoint root must not exist. Either pre-existing path is a fail-closed condition: it cannot be reused, cleaned, merged, or overwritten by the run.

Receipt publication uses atomic no-clobber semantics. A separate existence check followed by an overwriting replace is insufficient because it permits a check-then-replace race. The destination-creating filesystem operation itself must fail atomically when the destination already exists; if the target filesystem cannot provide that guarantee, publication stops without changing the destination. Temporary publication artifacts remain run-unique and cannot make a failed receipt appear current.

All earlier commits, OCI images, receipts, checkpoints, logs, failure records, and audit corrections remain immutable historical evidence. No prior `FAIL` can be rewritten as `PASS`, and no prior narrower `PASS` can satisfy A3 by implication. Current A3 evidence requires a fresh run ID, exact parent receipt bindings, the complete Section 5.2 receipt chain, and every A3 downstream gate.

Existing whole-tree Black and Ruff debt is outside the A3 correction boundary. A future A3 implementation may change only files required by these invariants and must run targeted formatting, lint, and tests over those touched files; broad formatting, unrelated cleanup, and refactoring are prohibited.

#### 5.2.5 A3 bounded CUDA determinism contract

The fresh A2 campaign `wave0-a2-20260825T025943120Z`, bound to source commit `db0dc52e10d5e58852b84e1d321c2efa06a82d30` and OCI image `sha256:9b43ab192f1014f960c8db1d0ea1da1a559dd4005250e5fb6e4aa2716d3f47e3`, passed environment, model-assets, and the complete four-class model contract, then failed during feasibility-A backward before publishing a feasibility receipt or checkpoint. The preserved stage record has SHA-256 `2dc1585974a86c02a1b02f7ba92c419ea3ccd8c90455c8c9a79a65b92b4a1fc8`; the stage log has SHA-256 `28fc5121e2ccfa55fe55bf24d6b7f74704e3dfece16873aa192f0589fa125ea4`; and the no-clobber failure record has SHA-256 `c0889697ba23b9ec775d7f66d47c2542c5f4c128f7309149db283ca8294f630f`. Its terminal verdict remains `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.

The exact error identifies `grid_sampler_2d_backward_cuda`. This is a pinned-stack capability conflict, not evidence corruption or a detector/reset failure:

1. Transformers 5.15.0 `MultiScaleDeformableAttention.forward` calls `torch.nn.functional.grid_sample` once per decoder layer and feature level, using bilinear mode, zero padding, and `align_corners=False`.
2. The pinned RT-DETR config has `decoder_layers == 3`, `num_feature_levels == 3`, and `disable_custom_kernels == true`; one labeled backward therefore reaches exactly `3 × 3 = 9` fallback grid-sample backward operations.
3. PyTorch 2.12.0 documents CUDA `torch.nn.functional.grid_sample` differentiation among the operations that throw when `torch.use_deterministic_algorithms(True, warn_only=False)` is active; its grid-sample documentation separately states that CUDA backward may be nondeterministic and cannot be easily switched off.
4. Full detector and backbone fine-tuning necessarily differentiates through deformable attention. Freezing the transformer, using CPU backward, changing detector identity, or introducing an unpinned custom kernel would change the approved research model more materially than a narrow, measured exception.

The inspected pinned wheel sources are normative inputs: Transformers `modeling_rt_detr.py` SHA-256 is `fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3`, PyTorch `torch/__init__.py` SHA-256 is `b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9`, and PyTorch `torch/nn/functional.py` SHA-256 is `e409a97896241e0dfb8c23fbf1f09967ecf5e65ec9626aec0d97d9cc5d727d50`. A3 execution must verify these exact hashes before the exception can be enabled.

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

For the post-backward floating update, the gate compares each of the five non-canonical observations with primary A over the exact ordered trainable-parameter inventory. Let `delta_r` be the concatenated post-update minus pre-update vector for replay `r`; because the pre-update digest is exact, `||delta_r - delta_primary||_2` can be reproduced from the two post-update checkpoints. The single global pre-clip gradient norm must satisfy the first bound below. Detector and backbone parameter-update groups must separately satisfy the second and third bounds:

```text
gradient_norm: math.isclose(rel_tol=1e-5, abs_tol=1e-7)
relative_update_l2 = ||delta_r - delta_primary||_2 / max(||delta_r||_2, ||delta_primary||_2) <= 1e-3
update_cosine = <delta_r, delta_primary> / (||delta_r||_2 ||delta_primary||_2) >= 0.99999
```

The gate also compares the checkpointed AdamW `exp_avg` and `exp_avg_sq` tensors by optimizer group and state name. Their ordered parameter-to-state mapping, shapes, and dtypes must be exact; each nonzero concatenated floating state must independently satisfy `relative_state_l2 <= 1e-3` and `state_cosine >= 0.99999`, using the same formulas as the update-vector bounds. Missing, unexpected, or non-finite optimizer state fails closed.

Every norm is accumulated in canonical parameter-name order using CPU float64. A zero, non-finite, missing, reordered, shape-mismatched, or dtype-mismatched update fails closed. The receipt records per-group update L2 norms and the gate records the pairwise difference, relative L2, and cosine values for model updates and optimizer states. These thresholds are fixed before any A3 GPU execution and cannot be adjusted after observing a run; changing them requires another reviewed protocol version and a new run ID. Passing A3 supports only the claim that the pinned full-training step is seed-controlled and numerically replayable within these registered same-host bounds despite one disclosed CUDA operation. It does not support bitwise training identity.

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
- reproducibility: `torch.use_deterministic_algorithms(True)`, cuDNN benchmark off, deterministic workspace settings, recorded RNG states, and the exact Section 5.2.5 allowlisted grid-sample backward exception.

The pilot must fail on any unregistered nondeterministic operation, incorrect warning count, missing replay evidence, or numerical replay bound violation. It cannot silently broaden the Section 5.2.5 exception. The design claims registered same-host numerical reproducibility on the canonical locked environment, not bitwise identity across runs, GPUs, or libraries.

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

The pilot uses only the 8% pilot engineering partition, seed 17, and four arms: random, entropy, core-set, and hybrid. Budgets are 2%, 5%, and 10% of that reduced pool. The 2% start is shared, so the pilot requires:

```text
1 shared 2% fit + (4 arms × 2 later fits) = 9 pilot fits
```

The pilot does not access either frozen test. It evaluates engineering validity through training loss, acquired-only development metrics, synthetic uncertainty fixtures, firewall tests, artifact replay, and runtime extrapolation. Pilot results cannot be mixed into formal curves.

### 12.2 Pass gates

Formal execution starts only if all conditions pass:

1. the Section 5.2 model-contract receipt is `PASS` and hash-bound to the run;
2. all nine fits complete on RTX 4090 with no OOM, NaN, Inf, unauthorized deterministic-algorithm fallback, or Section 5.2.5 replay-bound violation;
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
- [x] No unresolved implementation placeholder remains in this document.

## 19. Decisions that require a new reviewed protocol version

The following cannot be changed as an implementation convenience: included countries, dataset roles, split ranges/salt, global group/dedup thresholds and exclusions, detector/encoder identity, executable model-contract invariants, uncertainty equations, hybrid factor, canonical distance quantization/order, formal seeds/budgets, evaluation embargo, calibration split/gates, 30-epoch recipe, primary metrics/AUBC, censoring/claim gates, component-aware pilot caps, and 66-fit definition.

A required change must produce a written spec revision, explain the trigger, invalidate incompatible pilot/formal artifacts, and receive user approval before execution. On 2026-08-25 the owner delegated the A3 design and execution decision after reviewing the incompatibility finding and recommended bounded-exception approach. That authorization permits a separate A3 implementation-plan commit after this specification passes its recorded self-review; implementation still begins only from that plan, never directly from an unreviewed draft.
