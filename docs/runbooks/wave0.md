# Wave 0 A2 immutable replay runbook

This runbook executes only the approved Wave 0 A2 evidence chain. A successful
aggregate means `WAVE0_A2_PASS / WAVE1_NOT_STARTED`; it does not grant a Wave 1
capability or start a dataset workflow.

## Preconditions

- Use the reviewed, clean `codex/wave0-model-contract` source checkpoint.
- Keep `VAL_DATA_ROOT` unset.
- Set `VAL_ARTIFACT_ROOT` to the approved existing external artifact root.
- Confirm the RTX 4090 is idle and atomically claim the run-scoped GPU lease.
- Generate one new run ID, atomically create its campaign root, and use it for
  the primary, clean-a, clean-b, and gate receipts.
- Build one fresh image tag and record its image ID, inspect output, pinned base
  digest, and source commit. Never retag or delete the Option A image.

Any existing campaign, attempt, receipt, checkpoint, audit, or gate destination
is a hard failure. Do not retry under the same run ID and do not remove prior
evidence.

## Attempt commands

On Windows, invoke each absent attempt once:

```powershell
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId primary -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId clean-a -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId clean-b -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
```

The Bash script exposes the equivalent flags. Each invocation atomically claims
one attempt root, creates empty uv/model caches, and runs these five stages in
order:

1. `environment.json`
2. `model-assets.json`
3. `model-contract.json`
4. `feasibility-a.json`
5. `feasibility-b.json`

The source worktree is mounted read-only. Only the attempt root is writable.
Pinned assets may use network access during the model-assets stage; model
contract and feasibility stages set Hugging Face/Transformers offline mode and
use Docker `--network none`. No RDD or other dataset root is mounted.

At the first nonzero stage, stop. Preserve the attempt root, logs, stages,
receipts, checkpoint state, image identity, and audit records. Do not start the
next attempt.

## Aggregate gate

After all three attempts pass, atomically create the gate directory and run:

```text
val gate wave0 --run-id RUN_ID --primary-root PRIMARY --clean-a-root CLEAN_A --clean-b-root CLEAN_B --output GATE_RECEIPT
```

The gate validates all 15 parent receipts, exact run/content bindings, complete
four-class labeled and label-free evidence, BF16 backward/update/checkpoint
gates, A/B determinism, clean replay determinism, absence of a data root, and
fresh A2 evidence. Publication is atomic no-clobber.

## Terminal handling

- PASS: preserve all evidence and report
  `WAVE0_A2_PASS / WAVE1_NOT_STARTED / OWNER_FINAL_REVIEW_REQUIRED`.
- Any failure: preserve all evidence, release only this run's GPU lease, and
  report `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.

Never rewrite an old receipt, reinterpret an Option A failure as PASS, delete an
OCI image, merge, push, tag, create a release, or start Wave 1 from this runbook.
