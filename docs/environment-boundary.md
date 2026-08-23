# Wave 0 environment boundary

Canonical execution uses the pinned Linux OCI image on the WSL2 GPU backend. Native Windows is limited to CPU compatibility checks; it must not produce canonical evidence or a success marker.

| Component | Exact contract | Canonical support |
| --- | --- | --- |
| Python | 3.12.11 | WSL2/OCI |
| PyTorch | 2.12.0+cu126 | CUDA 12.6 wheel |
| torchvision | 0.27.0+cu126 | Paired CUDA 12.6 wheel |
| Transformers | 5.15.0 | PyPI release |
| pycocotools | 2.0.10 | PyPI release |
| CUDA base | `nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04` | Digest-pinned Linux image |
| GPU | NVIDIA GeForce RTX 4090 | WSL2 GPU passthrough |
| Runtime policy | TF32 disabled; deterministic algorithms enabled; BF16 supported | Exact receipt gate |

Set `VAL_ARTIFACT_ROOT` to the approved existing absolute artifact root. Receipts and all other generated output must resolve below `$VAL_ARTIFACT_ROOT/wave0`; absolute, traversal, and symlink escapes are rejected before any output is written. Generated evidence, caches, images, and machine observations must never enter Git. `VAL_DATA_ROOT` is intentionally outside this wave: the check fails whenever that variable is set.

`container_image_digest` means the observed immutable base manifest-list digest, not the locally built final image digest. The trusted launcher must provide that observation as `VAL_OBSERVED_BASE_IMAGE_DIGEST`; a missing observation fails, and the checker never copies the expected config value into the receipt. A launcher may separately provide the locally inspected final image identity as `VAL_RUNTIME_IMAGE_DIGEST`, which is recorded as `runtime_image_digest` without substituting for the approved base digest.

The compatibility receipt is generated with:

```console
python -m vision_active_learning_loop.environment check \
  --config configs/environment/wave0.yaml \
  --output "$VAL_ARTIFACT_ROOT/wave0/receipts/environment-receipt.json"
```

The command exits 0 only when the canonical contract matches exactly. A mismatch writes a receipt with `status: FAIL` and exits 2.

CLI discovery parses decorators from source syntax trees. It does not import command modules while building the manifest; the selected module is imported only during dispatch.
