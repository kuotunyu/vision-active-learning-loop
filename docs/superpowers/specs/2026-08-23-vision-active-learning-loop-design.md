# Vision Active Learning Loop — Formal Design Specification

**Status:** Approved scope; design specification awaiting user review
**Date:** 2026-08-23
**Repository:** `vision-active-learning-loop`
**Target roles:** Computer Vision Engineer, Machine Learning Engineer, AI Engineer
**Design choice:** Modified Option B — multi-country object-detection active learning
**Implementation status:** No implementation, dataset, dependency, or remote repository is part of this design-stage commit.

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
2. hybrid reaches the registered source mAP target with no more acquired images and no more revealed boxes than random in every seed where both are observable;
3. hybrid minimum-class recall and D40 recall at 40% are each no more than 3.0 absolute percentage points below random in any seed;
4. no censored target is counted as a success; and
5. China Drone results are reported separately and are not used to rescue an in-domain failure.

If these conditions are not met, the result is reported as mixed or negative. No claim of universal superiority, production readiness, or human labor savings is allowed.

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

### 4.1 Identity and grouping

Every source image receives a canonical `item_id = SHA256(pixel_file_bytes)`. Paths and filenames are not experimental identities. Before splitting:

1. Exact SHA-256 matches are unioned and only the lexicographically smallest canonical item is retained; other copies are recorded as excluded aliases.
2. A perceptual hash uses 16×16 pHash (256 bits). Images within Hamming distance 6 form connected components. One canonical image per component is retained after a curator verifies the component contact sheet.
3. When official metadata or a validated filename parser exposes a route, sequence, video, or capture-session identifier, all retained images from that capture receive the same `split_group_id`.
4. Otherwise, `split_group_id` is the retained image’s `item_id`. The fallback is explicit and counted in the data card.
5. A group ID is the minimum member `item_id`; a group can never cross partitions.

The pHash threshold, parser version, alias decisions, and manifest digest are frozen before any active-learning model runs. A DINOv2 neighbor audit flags cross-partition pairs with cosine similarity at least 0.995 for manual review. The audit is diagnostic; it cannot be used to optimize model results.

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

China Drone is independently de-duplicated and grouped with the same algorithms. Its retained annotated-train images form the shift test in full; none can enter a source partition.

The trusted data curator performs one pre-model coverage audit after the deterministic split. It reports image and box counts by country/class, fallback-group rate, group sizes, and duplicate exclusions. The split is not redrawn to improve a model result. If a source country is absent from either formal pool or source test, or if a test class has zero boxes, the experiment is blocked and the split algorithm must be revised as a new protocol version before any formal run. The invalid split is retained in the audit record rather than silently retried.

### 4.3 Leakage rules

- Split and duplicate control happen before active learning.
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

The checkpoint and Transformers implementation are Apache-2.0 licensed. RT-DETR is selected because it exposes a fixed set of 300 decoder queries and raw class/box outputs, making the acquisition contract auditable without NMS or a score-threshold-dependent number of detections. The four-class prediction head is reset with a seed-deterministic initialization; it does not reuse COCO class-head rows.

The interpretation is pinned to [Transformers 5.15.0 RT-DETR documentation](https://huggingface.co/docs/transformers/v5.15.0/en/model_doc/rt_detr). That implementation trains class outputs with focal-loss-style independent sigmoid probabilities. It does **not** provide a native mutually exclusive no-object softmax class. Section 7 therefore defines a derived and explicitly labeled background probability rather than claiming a model-native no-object logit.

### 5.2 Frozen diversity encoder

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

### 5.3 Research-critical runtime lock

The implementation plan must preserve these exact core versions:

| Component | Version | License/purpose |
|---|---|---|
| Python | 3.12.11 | Runtime |
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
5. Train one shared 100% ceiling model because every arm has acquired the same full formal pool at that point.

The 2% point is plotted as a shared reference, not falsely counted as five independent fits.

### 6.3 Formal fit count

Per seed:

```text
1 shared 2% fit + (5 arms × 4 later budget fits) + 1 shared 100% ceiling = 22 fits
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
- determinism: `torch.use_deterministic_algorithms(True)`, cuDNN benchmark off, deterministic workspace settings, and recorded RNG states.

The pilot must fail rather than silently relax deterministic algorithms. The design claims reproducibility on the canonical locked environment, not bitwise identity across different GPUs or libraries.

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

Starting with every previously acquired embedding as the center set, greedy k-center repeatedly selects the unlabeled candidate with the largest distance to its nearest center, adds it as a center, and updates distances until the batch is full. Ties use ascending `item_id`. The shared 2% start guarantees at least one center. CPU/GPU chunking cannot change results beyond an absolute distance tolerance of `1e-7`; within tolerance the `item_id` tie break governs.

Tests must compare the optimized implementation to a brute-force toy matrix, verify nested selections, and verify invariant output under candidate input permutation.

### 7.5 Hybrid uncertainty plus diversity

Hybrid first ranks every unlabeled image by the entropy image score. For a required batch of `b` images, it takes the first `min(5b, remaining_pool_size)` candidates, then runs the same greedy k-center rule over that candidate set relative to all previously acquired centers and within-batch selections. The factor 5 is frozen before the pilot. Ties at both stages follow `item_id`.

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

### 8.4 Human-in-the-loop queue without fake humans

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

On each acquired calibration/dev set, form a fixed candidate denominator: the 100 largest raw query-class sigmoid scores per image before NMS or thresholding. Match candidates one-to-one to ground truth in descending score order. A candidate is correct only when class matches and IoU is at least 0.5; unmatched candidates are incorrect. Fit one scalar temperature `T ∈ [0.05, 10]` by minimizing binary negative log likelihood on these correctness outcomes. Apply `sigmoid(logit/T)` to source-test and shift-test candidates with the identical denominator construction.

Temperature fitting is permitted only when the acquired calibration set has all of:

- at least 200 images;
- at least 100 ground-truth boxes;
- at least 20 ground-truth boxes in each of D00, D10, D20, and D40; and
- at least 50 correct and 50 incorrect candidate outcomes.

If any gate fails, `calibration_status = INSUFFICIENT`, temperature and calibrated metrics are null, and raw metrics plus exact denominator counts remain reported. Missing values are not imputed or treated as zero.

### 9.3 Calibration metrics

For raw and, when eligible, calibrated confidence, report:

- binary Brier score over the fixed candidate denominator;
- adaptive ECE with 15 equal-count bins, merging bins only when tied scores make a boundary impossible;
- localization-aware ECE (LaECE) using confidence, precision, and matched IoU under the published detection-calibration formulation;
- candidate count, image count, positive/negative outcome counts, per-class ground-truth support, temperature, and status.

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

### 10.3 Normalized area under the budget curve

Primary AUBC uses source-test mAP50–95 at fractions `0.02, 0.05, 0.10, 0.20, 0.40`, trapezoidal integration, and range normalization:

```text
nAUBC = trapz(mAP, budget_fraction from 0.02 to 0.40) / (0.40 - 0.02)
```

The 100% ceiling does not enter AUBC. Report nAUBC per seed/arm, paired arm-minus-random deltas by seed, their mean and median, and all-seed sign consistency.

### 10.4 Labels to target

For each seed, the target is 90% of that seed’s shared 100%-ceiling source mAP50–95. `labels_to_90pct_ceiling` is the smallest **observed** budget point reaching the target; no curve smoothing or interpolation creates a success. Report images and revealed boxes at that point. If no point through 40% reaches it, report right-censored `> B(0.40)` and `> boxes_at_40pct`, never a numeric success.

Censored paired interpretation is fixed:

- hybrid observed and random censored: favorable for hybrid;
- random observed and hybrid censored: criterion fails;
- both censored: insufficient for a target-cost comparison;
- both observed: compare images and boxes directly.

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

Noise is an auxiliary sensitivity experiment and does not alter the 66 primary fits. For each seed, reuse the clean 20% acquisition manifests from only `random` and `hybrid_uncertainty_diversity`. Retrain from the same base after applying deterministic corruption to 10% of acquired positive training images (calibration images remain clean):

- 40% of affected images: drop one deterministically selected box;
- 30%: change one class to the next class modulo four;
- 30%: jitter one box center and size independently by a signed value up to 10% of its width/height, then clip to the image.

Affected images and boxes are ranked by `SHA256("noise-v1" || seed || item_id || box_index)`. Images with no boxes are not eligible. This creates `2 arms × 3 seeds = 6` auxiliary fits. Report clean-versus-noisy deltas; do not claim a noise-aware acquisition strategy.

### 11.2 Shift evaluation

Every formal checkpoint is evaluated, without adaptation, on curated China Drone. No China Drone label or metric influences pilot decisions, formal method choice, calibration, thresholding, or stopping. Report the same detection and eligible calibration metrics, but label every result `shift_only` and keep it outside source nAUBC and success criteria.

## 12. Pilot gate and protocol freeze

### 12.1 Pilot shape

The pilot uses only the 8% pilot engineering partition, seed 17, and four arms: random, entropy, core-set, and hybrid. Budgets are 2%, 5%, and 10% of that reduced pool. The 2% start is shared, so the pilot requires:

```text
1 shared 2% fit + (4 arms × 2 later fits) = 9 pilot fits
```

The pilot does not access either frozen test. It evaluates engineering validity through training loss, acquired-only development metrics, synthetic uncertainty fixtures, firewall tests, artifact replay, and runtime extrapolation. Pilot results cannot be mixed into formal curves.

### 12.2 Pass gates

Formal execution starts only if all conditions pass:

1. all nine fits complete on RTX 4090 with no OOM, NaN, Inf, or deterministic-algorithm fallback;
2. detector loss is finite and decreases from the median of the first 10% of steps to the median of the final 10%;
3. each uncertainty strategy has score standard deviation at least `1e-6` over at least 100 unlabeled pilot images;
4. core-set/hybrid match brute-force selections on the registered toy matrices;
5. all oracle-firewall adversarial tests pass and no group crosses a partition;
6. interrupted jobs resume to the same final artifact hashes as uninterrupted jobs on the canonical host;
7. every budget ledger equals its exact target with unique item IDs and nested acquisition sets;
8. peak allocated VRAM is at most 22 GiB;
9. median full-pool scoring extrapolation is at most 15 minutes per arm/round; and
10. conservative extrapolated total for the 66 primary fits is at most 240 RTX 4090 GPU-hours.

Any failure stops formal execution. The response is to fix the engineering/protocol cause, increment the relevant protocol/component version, rerun the entire pilot, and record the failed attempt. It is not permissible to inspect frozen-test results, weaken a gate silently, or cherry-pick a passing run.

After the pilot passes, freeze the manifest digest, exclusions, model/processor revisions, training recipe, seeds, budgets, acquisition formulas, tie breaks, metrics, calibration gate, and claim rules. Subsequent changes require a new experiment ID and complete formal rerun.

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
upstream archive digests
  → curated manifest + exclusions + split groups
    → public unlabeled mirror / sealed oracle manifests
      → frozen embedding matrix
      → acquisition request → queue events → acquired-label ledger
        → training manifest → checkpoint
          → sealed aggregate evaluation → metrics tables → plots/model card
```

Each arrow is represented by input hashes. An artifact store may contain local derived objects but the remote repository contains only schemas, small synthetic fixtures, configuration examples, aggregate results, and permitted identifiers/hashes.

## 14. Reviewer fast path

A reviewer with no GPU and no RDD download must be able to run or inspect a five-minute path that demonstrates the project’s engineering contribution using a tiny original synthetic fixture and checked-in precomputed artifacts:

1. display the frozen experiment contract, detector/encoder hashes, and 66-fit calculation;
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
| M1 Data and firewall foundation | 2 | Curated manifest pipeline, dedup/group/split logic, sealed oracle layout | Synthetic and real-manifest audits pass; no cross-partition group |
| M2 Fixed detector/encoder | 3 | Deterministic base training/eval, hashed DINO embeddings | Tiny overfit/smoke checks pass; revisions and hashes verified |
| M3 Acquisition and queue | 4 | Five strategies, budget ledger, queue export/import/replay | Hand-computed uncertainty and brute-force core-set tests pass |
| M4 Pilot and freeze | 5 | Nine-fit pilot report and protocol snapshot | Every Section 12 gate passes |
| M5 Formal source experiment | 6 | 66 primary fits and source metrics | All seeds/arms/budgets complete, resumable, and ledger-valid |
| M6 Robustness and shift | 7 | China Drone evaluation, calibration, noise fits, compute accounting | Six noise fits complete; no test leakage; all statuses explicit |
| M7 Portfolio release | 8 | Reviewer path, README, model/data cards, static report | Five-minute path passes clean; self-audit passes; tag `v0.1.0` approved |

The `v0.1.0` tag is not created during design. It is the M7 boundary after full evidence and explicit user approval.

## 16. Risks and mitigations

| Risk | Consequence | Pre-registered mitigation/decision |
|---|---|---|
| RT-DETR raw scores are misread as a no-object softmax | Invalid uncertainty ranking | Use the explicit derived five-state contract and raw-logit synthetic tests |
| DINOv2 upstream license metadata changes | Reuse uncertainty | Pin the Apache revision/file hash and archive its model card/notice; reject old noncommercial-card revision |
| Country/capture duplicates cross splits | Inflated performance | SHA + pHash components, capture grouping, frozen manifest digest, neighbor audit |
| Hidden annotations leak through code/config/cache | Invalid active learning | Container mount separation, opaque IDs, sealed evaluator, adversarial firewall suite |
| Rare D40 examples make averages misleading | Harm hidden by mAP | D40 and minimum-class recall gates, supports, discovery rounds, individual seeds |
| Calibration subset is too small at low budgets | Unstable confidence metrics | Budget-charged stable split plus explicit eligibility gates/INSUFFICIENT status |
| Active methods acquire box-dense images | Image savings hide box cost | Report revealed-box curves and require image and box criteria for cost claim |
| Three seeds invite overconfident inference | Fragile statistical story | Individual curves, paired deltas, mean/median, sign consistency; no confirmatory p-values |
| Formal compute exceeds practical limit | Incomplete portfolio | Nine-fit pilot and 240-hour cap before protocol freeze |
| Fixed 30 epochs under/over-train at some budgets | Budget-dependent optimization bias | Same registered recipe, 100% ceiling, training diagnostics; interpret limitations rather than tune on test |
| China Drone is too different | Shift scores collapse | Report honestly as separate shift result; no adaptation or result rescue |
| Simulated oracle is mistaken for human validation | Misleading product claim | Explicit actor/state labels and prohibition on human time/IAA/cost claims |
| Dataset cannot be redistributed | Reviewer friction | Source downloader/checksums plus original tiny synthetic fast path; never mirror data |

## 17. Statistical reporting rules

With only three seeds, formal reports use individual observations, mean, median, paired seed deltas, ranges, and all-seed sign consistency. They do not present small-sample p-values as proof. Image-level bootstrap intervals may describe evaluation-set sampling sensitivity, but must be labeled as such and never presented as between-seed uncertainty.

Every figure/table identifies dataset role, arm, seed aggregation, budget unit, calibration status, and whether the point is shared. Failed jobs, invalid artifacts, protocol versions, and censored targets remain visible. A negative or null active-learning result is a valid project result when the protocol passed.

## 18. Design-stage acceptance checklist

- [x] The project is differentiated from the five existing CV projects by a reproducible active-learning system, not another detector benchmark.
- [x] Scope is exactly four source countries plus China Drone shift-only; US, Norway, and all other datasets are out.
- [x] The detector, frozen encoder, revisions, hashes, preprocessing representation, and critical package versions are exact.
- [x] Detector licensing is Apache-2.0; the chosen DINOv2 revision is Apache-2.0 and the old conflicting revision is excluded.
- [x] RDD is conservatively treated as CC BY-SA 4.0 and pixels/annotations are not redistributed.
- [x] Split, duplicate grouping, one-time curator coverage audit, and oracle access rules do not depend on model results.
- [x] The 2% reference is one shared fit; `1 + 5×4 + 1 = 22` per seed and `22×3 = 66` primary fits.
- [x] Entropy and margin cover background, conditional class ambiguity, localization instability, fixed top-20 aggregation, zero postprocessed detections, and deterministic ties.
- [x] Calibration labels count against budget, are excluded from detector weights, never affect acquisition, and have an explicit insufficiency status.
- [x] Class imbalance, label noise, distribution shift, duplicate leakage, compute, and censored target rules are registered.
- [x] The labeling queue is a simulated-oracle workflow contract, not a claim of a real annotator study or full inspection UI.
- [x] Three-seed inference is descriptive and does not rely on overconfident p-values.
- [x] RTX 4090 is canonical; Colab is optional/non-canonical and cannot fill formal gaps.
- [x] The eight-week plan has observable completion gates and a five-minute reviewer path.
- [x] No unresolved implementation placeholder remains in this document.

## 19. Decisions that require a new reviewed protocol version

The following cannot be changed as an implementation convenience: included countries, dataset roles, split ranges/salt, group/dedup thresholds, detector/encoder identity, uncertainty equations, hybrid factor, formal seeds/budgets, calibration split/gates, 30-epoch recipe, primary metrics/AUBC, claim gates, pilot caps, and 66-fit definition.

A required change must produce a written spec revision, explain the trigger, invalidate incompatible pilot/formal artifacts, and receive user approval before execution. After approval of this design, the next allowed deliverable is a separate implementation plan; no implementation should begin directly from this document.
