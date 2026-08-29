# Wave 0 A11 Fourth Failure-Recovery Design

## Status and authority

The owner approved this design direction on 2026-08-29 and delegated the
bounded choices in this document to the implementing agent. This written
specification still requires owner review before an implementation plan is
written.

This authority permits only the design, plan, CPU-only TDD implementation,
review, verification, and append-only repair commits described here. It does
not permit a new A11 launcher invocation, Docker build or run, cache download,
GPU lease, model initialization, calibration or validation replica, RDD
access, Wave 1, push, merge, tag, release, or publication. It does not permit
reuse of `steven003` or synthesis of a future `OwnerAuthorizationId`. A later
runtime attempt requires a separate owner authorization bound to the exact
new source commit.

The original A11 statistical-replay contract remains
`docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`,
Section 5.2.15. The reviewed original A11 identities remain:

- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- branch: `codex/wave0-model-contract`
- starting source: `77f8eecb3b8c0f471a4e980269187ac02a3b9ebc`

All four failed A11 attempts are immutable. None may be retried, repaired,
completed, renamed, moved, deleted, retagged, or reinterpreted.

## Authoritative observed failure

The one authorized attempt using `OwnerAuthorizationId=steven003` passed its
exact read-only entry gate, fresh no-cache image build and inspection, cache
preflight, GPU lease, environment, model-assets, model-contract, and all
twelve fresh calibration replicas. Each replica published one schema-v3 PASS
feasibility receipt and one verified checkpoint from a distinct container.

The host launcher then published the closed calibration phase manifest and
invoked the aggregate gate once. The aggregate process returned exit code 2,
empty stdout, and exact stderr:

```text
model cache inventory mismatch
```

The stderr is 31 bytes with SHA-256
`a336516b29c7b7fd395d6b2008409a5d8018b5d9c5616831d369cbd15078a812`.
The attempted calibration success receipt remained absent. The launcher
released the lease, published failure diagnostic/result/manifest/closure
records, preserved history, did not create the preregistered validation root,
and stopped at:

```text
WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

This is a cross-platform cache-inventory ordering defect, not cache-byte
drift and not a replica/model failure. The exact same cache bytes produce:

- current Windows PowerShell launcher digest:
  `162e46433db9f05beb9462fa510e92eae0f11c3fee0f1a1d6e26166fcd36c271`
- Linux Python aggregate-gate digest:
  `7c2241d696e80a433c25feba0ad2642bd341cf4a7d92358e2ecad0f10a6c618c`

`Get-A11CacheInventorySha256` sorts full Windows paths with
`Sort-Object -CaseSensitive`. Windows culture collation places
`facebook--dinov2-small` before `PekingU--rtdetr_r18vd`.
`_model_cache_inventory_sha256` sorts Linux `Path` objects by POSIX ordinal
path order, which places uppercase `P` before lowercase `f`. File records,
file sizes, normalized Hugging Face metadata bytes, and content hashes are
otherwise identical.

The existing parity test did not expose this defect because its fixture used
only path names whose Windows and Linux order is identical, and its expected
records were themselves ordered with the host platform's `Path` comparison.

## Preserved baseline

The historical non-A11 baseline remains exactly 64,306 files with inventory
SHA-256
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`
and 21 images with inventory SHA-256
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

The first three attempts remain exactly as registered by:

- `docs/superpowers/specs/2026-08-28-val-wave0-a11-launcher-failure-recovery-design.md`
- `docs/superpowers/specs/2026-08-28-val-wave0-a11-second-failure-recovery-design.md`
- `docs/superpowers/specs/2026-08-29-val-wave0-a11-third-failure-recovery-design.md`

Their run inventory SHA-256 values remain, in chronological order:

1. `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`
2. `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b`
3. `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2`

Before any future attempt, the complete closed A11 envelope is exactly four
calibration run directories, three A11 image tags, six A11 lease-history
files, four consumed authorization identities, no active lease, no project
container, and no validation run directory.

### Attempt 4: aggregate cache-inventory contract failure

- state: `aggregate-cache-inventory-contract-failure`
- run ID: `wave0-a11-calibration-20260829T050706309Z-f5a0129e`
- preregistered validation ID:
  `wave0-a11-validation-20260829T050706319Z-c6652f48`
- owner authorization: `steven003`
- source: `77f8eecb3b8c0f471a4e980269187ac02a3b9ebc`
- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- file count: 137
- run inventory SHA-256:
  `f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717`
- directory count: 30
- image tag:
  `vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e`
- image ID:
  `sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e`
- release record SHA-256:
  `aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1`
- released lease SHA-256:
  `b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c`
- latest observed write time: `2026-08-29T06:13:25.1659510Z`
- checkpoint directories: exactly `calibration-00` through
  `calibration-11`
- checkpoint files: exactly twelve `step-000001.pt` files
- calibration aggregate success receipt: absent
- validation root, image, lease, replica, receipt, and checkpoint: absent
- active lease and project container: absent

The exact 30 directory names are:

```text
audit
wave0
wave0/checkpoints
wave0/checkpoints/calibration-00
wave0/checkpoints/calibration-01
wave0/checkpoints/calibration-02
wave0/checkpoints/calibration-03
wave0/checkpoints/calibration-04
wave0/checkpoints/calibration-05
wave0/checkpoints/calibration-06
wave0/checkpoints/calibration-07
wave0/checkpoints/calibration-08
wave0/checkpoints/calibration-09
wave0/checkpoints/calibration-10
wave0/checkpoints/calibration-11
wave0/model_cache
wave0/model_cache/snapshots
wave0/model_cache/snapshots/facebook--dinov2-small
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees
wave0/receipts
```

The following key file records bind the fourth failure:

| Relative path | Size | SHA-256 |
| --- | ---: | --- |
| `audit/00-identity.json` | 2,873 | `dce0706a572cdb5e72a8b28aad61750ee799e0eae7164ae1b5c6a0c22f1ffe4c` |
| `audit/10-build.json` | 1,234 | `c173d63a7428792c503a90ef095e1e8055c7ba8d7d112b54ea5a318fa1675eab` |
| `audit/11-image-inspect.json` | 682 | `c355d995173db7b7600ad1dc25774f28e76f620300252f165288797c931b8b81` |
| `audit/20-cache-preflight.json` | 1,900 | `0c67229f0731b1e573f84a1ca3b97fb8aa2e51e4157e66c644133e2037c00273` |
| `audit/30-environment.json` | 1,995 | `343602c0ad150e9b6642a31d3f2304e816ae8819b706d7774371625ed7fe753c` |
| `audit/31-model-assets.json` | 2,051 | `e734f83f4f9149ea002982c6a48997445d71ba24b2c9424519f025dd63bbe851` |
| `audit/32-model-contract.json` | 2,232 | `db0bb5710a3c6cd37a68f8142d43d2e2633254eca936be00c0faceefee6cd50c` |
| `audit/60-historical-preservation.json` | 301 | `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d` |
| `audit/70-phase-manifest.json` | 9,990 | `82122edec3b647c39946bdba6ebfa3c74d36065a084632e8d45c38b31eaaf97a` |
| `audit/71-aggregate-gate.json` | 1,287 | `5772642484357bdfa4b7132bdbea974092c823e1207c57b60f7aec31ce7f22f3` |
| `audit/71-aggregate-gate.stderr.log` | 31 | `a336516b29c7b7fd395d6b2008409a5d8018b5d9c5616831d369cbd15078a812` |
| `audit/78-failure-diagnostic.json` | 855 | `40f1163d031fc68555363980b57821f87b103fdffd0e33880f0941361ae42338` |
| `audit/79-historical-preservation-final.json` | 301 | `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d` |
| `audit/80-campaign-result.json` | 762 | `b4f2c8fa42384ae4791071b828f2cf0fccc9e50f9e2e69e928a8b9a583b2047e` |
| `audit/81-campaign-file-manifest.json` | 35,243 | `02f7a06d64969ed4ebe2bb1a575ba7308279cee5b3f3ae51663fceb676cc4eec` |
| `audit/82-campaign-closure.json` | 660 | `1f65ea6261fabb007be1f15a457e2c9ff71925251c5b3af568e061890556e219` |
| `wave0/receipts/model-contract.json` | 9,623 | `5589eb3e64fe9727212e3467f9e3ca6979e008b31e69e5a8ace0e0919607de9d` |

## Approaches considered

### Selected: explicit relative-path ordinal canonicalization

Both implementations derive normalized forward-slash relative path strings
before sorting. They then sort those strings by Unicode ordinal order and hash
the existing closed records. Python string ordering already provides the
required code-point order; PowerShell must use an explicit ordinal comparer.

This is the smallest platform-independent definition. It preserves every file
size/hash rule, Hugging Face metadata normalization, JSON field, and
recomputation boundary. For the observed cache, both implementations must
produce
`7c2241d696e80a433c25feba0ad2642bd341cf4a7d92358e2ecad0f10a6c618c`.

### Rejected: make Linux Python emulate Windows culture sorting

Culture sorting is not a stable evidence contract. Its result can vary by OS,
locale, runtime, and collation implementation. Reproducing the current Windows
ordering would preserve the accidental behavior rather than define a
canonical inventory.

### Rejected: accept either digest or trust the manifest digest

Allowing both observed digests would make one byte set have two identities.
Skipping aggregate recomputation would weaken the phase-manifest trust
boundary. An allowlist, fallback, retry, or host-specific digest remains
forbidden.

### Rejected: publish the full cache file array in the phase manifest

The existing cache audit and model-assets receipt already bind cache content.
Adding another large manifest field broadens schemas and data flow without
solving the need for a single canonical ordering algorithm.

## Recovery architecture

### Unit A: platform-independent cache inventory

`_model_cache_inventory_sha256` must:

1. enumerate the existing cache tree without following links;
2. convert every regular file to its relative POSIX path string;
3. sort by that string's Unicode code-point order;
4. retain exact `.metadata` timestamp normalization;
5. retain records with exactly `path`, `size`, and `sha256`; and
6. hash exactly `canonical_json_sha256({"files": records})`.

`Get-A11CacheInventorySha256` must perform the same steps. It must not use
`Sort-Object` culture collation for canonical cache order. It must explicitly
compare normalized relative strings with `[StringComparer]::Ordinal` and
retain the current compact UTF-8 JSON and SHA-256 contract.

The order is case-sensitive and ordinal. In particular:

```text
snapshots/PekingU--rtdetr_r18vd/...
snapshots/facebook--dinov2-small/...
```

No absolute path, drive letter, mount point, OS separator, locale, current
culture, creation time, modification time, download timestamp, or enumeration
order may affect the digest.

### Unit B: exact four-attempt preservation preflight

`Get-A11PriorAttemptInventory` expands from three to four explicitly
registered attempts. It must:

1. require the exact four chronological run names;
2. require exactly three A11 image tags and exact IDs/labels;
3. require exactly six lease-history files and their hashes;
4. parse and bind four current/preregistered identity pairs;
5. reject links at every registered root, descendant, and lease record;
6. rehash all four run inventories;
7. require the fourth attempt's exact 137-file, 30-directory, 12-replica,
   12-checkpoint, aggregate-failure, release, and closure state;
8. require the calibration success receipt and all validation objects absent;
9. return four closed authorization and attempt records; and
10. reject reuse of any consumed authorization, including `steven003`, before
    the first write.

`Test-A11ReadOnlyPreflight` must bind the same closed fields and constants.
`Test-A11PhaseDestinationsAbsent` must compare future generated identities
against every registered run ID, image tag, path, and authorization from all
four attempts.

The fourth attempt is not reclassified as a calibration observation and its
checkpoints are not inputs to a future threshold calculation. They remain
failure evidence only.

### Unit C: unchanged normative and failure boundaries

The recovery does not change:

- 12 calibration and 12 validation replicas;
- the 66-pair and 13-metric inventories;
- thresholds, ceilings, formulas, receipt schemas, or semantic validators;
- model, processor, revisions, cache bytes, seed, fixture, optimizer,
  scheduler, CUDA, driver, GPU, VRAM, or checkpoint contracts;
- build/cache network rules, leases, phase order, no-clobber writes, or
  failure closure;
- exact stdout and empty-stderr process contracts;
- prohibition on retry, partial rescue, threshold feedback, RDD, Wave 1,
  push, merge, release, or publication.

A future calibration failure still prevents validation. A future A11 PASS
still stops at
`WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`.

## TDD and verification design

Implementation must start with focused RED tests against the committed plan
parent. The tests must fail for the observed ordering and four-attempt
preservation reasons before production code changes.

### Cache-order tests

- Build a cache fixture containing both
  `snapshots/PekingU--rtdetr_r18vd/...` and
  `snapshots/facebook--dinov2-small/...` plus normalized download metadata.
- Define expected ordering from explicit relative strings, not host `Path`
  comparison, directory enumeration, or `Sort-Object`.
- Require the Python and PowerShell production functions to produce the same
  fixed digest from the same bytes.
- Require changing only the metadata timestamp to preserve the digest.
- Require changing the metadata commit/ETag, file bytes, relative path,
  size, or case to change or reject the inventory as applicable.
- Retain link, empty-cache, non-regular-file, and invalid-metadata rejection.

### Four-attempt preservation tests

- Build isolated temporary representations of all four distinct attempt
  states and call the real production inventory/preflight functions.
- Require exactly four runs, three images, six lease files, and four consumed
  authorization records.
- Require attempt 4's source/specification/plan, current/peer IDs, owner,
  complete inventory digest, directory names, replica/checkpoint set, key
  records, image, release, closure, absent success receipt, and absent
  validation objects.
- Mutate each closed field independently and require failure before
  initialization.
- Require `steven003` to fail as reused and a synthetic test-only fresh owner
  value to pass. Tests must not introduce a guessed real future owner ID.
- Preserve the distinct closed schemas for all four attempt states.

### Repository gates

Before the implementation commit, run:

- focused RED and GREEN cache-order tests;
- focused RED and GREEN four-attempt preservation tests;
- complete `tests/gates/test_wave0_a11_launcher.py`;
- complete `tests/gates/test_statistical_replay.py` and the original A11
  focused suites;
- complete CPU pytest with bytecode/cache writing disabled;
- targeted Black and Ruff for changed Python files;
- `uv lock --check` and `git diff --check`;
- PowerShell 7 and Windows PowerShell 5.1 parser checks;
- exact tracked-file/staging audits;
- full read-only historical, four-attempt, image, lease, container, GPU, Git,
  and authorization-preservation checks; and
- line-by-line review with Critical=0 and Important=0.

No test may invoke the launcher entry point, Docker build/run, model loading,
CUDA, a real GPU lease, or mutate the external artifact root.

## File, commit, and lineage boundaries

This design commit changes exactly this file:

```text
docs/superpowers/specs/2026-08-29-val-wave0-a11-fourth-failure-recovery-design.md
```

The future plan commit may add exactly:

```text
docs/superpowers/plans/2026-08-29-val-wave0-a11-fourth-failure-recovery.md
```

The implementation tracked-file allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
src/vision_active_learning_loop/gates/statistical_replay.py
tests/gates/test_statistical_replay.py
```

The implementation must be one append-only commit whose direct parent is the
plan commit. A fifth implementation path is a hard stop. All commits use:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, reset, rebase, squash, stash, cherry-pick, cleanup of historical
evidence, push, merge, tag, release, or modification of another repository is
permitted.

## Acceptance and stopping gate

The recovery candidate is complete only when:

1. design, plan, and implementation commits form a direct parent chain from
   `77f8eecb3b8c0f471a4e980269187ac02a3b9ebc`;
2. the implementation diff contains exactly the four allowlisted paths;
3. focused tests prove the cross-platform ordering defect RED then GREEN;
4. both production implementations produce the single ordinal digest and
   retain independent recomputation;
5. the fourth attempt is bound exactly and `steven003` is rejected as reused;
6. all four attempts, three A11 images, six lease-history files, 64,306
   historical files, and 21 historical images rehash exactly;
7. no new A11 run, image, cache, lease, container, replica, receipt,
   checkpoint, validation root, or runtime authorization exists;
8. every required CPU, style, lock, diff, parser, and review gate passes; and
9. linked and canonical worktrees are clean after the implementation commit.

After post-commit verification, stop and report the exact commit identities
and evidence. Do not invoke `scripts/run_wave0_a11.ps1`. The candidate becomes
eligible only for a separately authorized fresh single runtime attempt.
