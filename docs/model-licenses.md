# Pinned model license evidence

Wave 0 accepts only these immutable Hugging Face snapshots:

| Model | Repository | Revision | License evidence |
| --- | --- | --- | --- |
| RT-DETR R18 | `PekingU/rtdetr_r18vd` | `cc5b50f32f0100caaa3bd275343e2fb17762c73d` | `README.md` front matter declares `apache-2.0`; SHA-256 `0d6d6065595011f4897e724f11d2b86494764eba68e3514cc6c70f0a851e539e` |
| DINOv2 Small | `facebook/dinov2-small` | `ed25f3a31f01632728cabb09d1542f84ab7b0056` | `README.md` front matter declares `apache-2.0`; SHA-256 `4c20dca454a8e5c670e8de5c7e6040f512aeca5438516f7623eedc4e3b00599c` |

The exact model cards are archived with the external snapshots below the logical
`VAL_ARTIFACT_ROOT/wave0/model_cache` root and are included in the model-asset
receipt inventory. The verifier rejects any other repository, commit, card hash,
license identifier, config, processor, weight, or installed Transformers source
hash. In particular, a historical or fixture DINOv2 card declaring a
CC-BY-NC/noncommercial license is not accepted as evidence for this contract.

No model weights, cards, cache metadata, receipts, or machine-specific paths are
tracked in Git.
