"""v0.3 diversity arms: DINOv2-small embeddings, greedy k-center, hybrid shortlist.

Definitions follow the v0.3 protocol Section 1 (cosine distance clamped to
[0, 2], acquired images as initial centers, farthest-from-nearest-center
greedy selection, ties by ascending item_id). Everything runs in float32 on
CPU; the pool is small enough that no chunking is needed.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image

from ..artifacts.digests import sha256_file
from ..cli_manifest import command
from .dataset import DatasetError, build_image_index, load_sample
from .manifest import manifest_sha256, write_json_no_clobber

HYBRID_FACTOR = 5
UNIT_TOLERANCE = 1e-3


class DiversityError(ValueError):
    """Raised when embeddings or a selection request are not usable."""


def _check_unit(vectors: torch.Tensor, label: str) -> torch.Tensor:
    if vectors.ndim != 2:
        raise DiversityError(f"{label} must be a 2-D tensor")
    vectors = vectors.to(dtype=torch.float32)
    if vectors.shape[0] and not torch.allclose(
        vectors.norm(dim=1), torch.ones(vectors.shape[0]), atol=UNIT_TOLERANCE, rtol=0
    ):
        raise DiversityError(f"{label} must be L2-normalized")
    return vectors


def cosine_distances(candidates: torch.Tensor, centers: torch.Tensor) -> torch.Tensor:
    """[C, K] cosine distances 1 - <u, v>, clamped to [0, 2]."""
    candidates = _check_unit(candidates, "candidates")
    centers = _check_unit(centers, "centers")
    return torch.clamp(1.0 - candidates @ centers.T, 0.0, 2.0)


def _validate_request(
    candidate_ids: Sequence[str], candidate_vectors: torch.Tensor, count: int
) -> None:
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise DiversityError("count must be a positive integer")
    if len(candidate_ids) != candidate_vectors.shape[0]:
        raise DiversityError("candidate ids and vectors disagree in length")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise DiversityError("candidate ids must be unique")
    if count > len(candidate_ids):
        raise DiversityError("count exceeds the candidate pool")


def k_center_select(
    candidate_ids: Sequence[str],
    candidate_vectors: torch.Tensor,
    center_vectors: torch.Tensor,
    count: int,
) -> tuple[tuple[str, float], ...]:
    """Greedy k-center: repeatedly take the candidate farthest from its nearest center."""
    candidate_vectors = _check_unit(candidate_vectors, "candidates")
    center_vectors = _check_unit(center_vectors, "centers")
    _validate_request(candidate_ids, candidate_vectors, count)
    ids = list(candidate_ids)
    if center_vectors.shape[0]:
        nearest = cosine_distances(candidate_vectors, center_vectors).min(dim=1).values
    else:
        nearest = torch.full((len(ids),), 2.0, dtype=torch.float32)
    remaining = list(range(len(ids)))
    chosen: list[tuple[str, float]] = []
    for _ in range(count):
        best = min(remaining, key=lambda index: (-float(nearest[index]), ids[index]))
        chosen.append((ids[best], float(nearest[best])))
        remaining.remove(best)
        if remaining:
            to_new = cosine_distances(
                candidate_vectors[remaining], candidate_vectors[best : best + 1]
            )[:, 0]
            nearest[remaining] = torch.minimum(nearest[remaining], to_new)
    return tuple(chosen)


def k_center_reference(
    candidate_ids: Sequence[str],
    candidate_vectors: torch.Tensor,
    center_vectors: torch.Tensor,
    count: int,
) -> tuple[tuple[str, float], ...]:
    """The plain reference: recompute every candidate's nearest-center distance each step."""
    candidate_vectors = _check_unit(candidate_vectors, "candidates")
    center_vectors = _check_unit(center_vectors, "centers")
    _validate_request(candidate_ids, candidate_vectors, count)
    ids = list(candidate_ids)
    centers = [center_vectors[i] for i in range(center_vectors.shape[0])]
    remaining = list(range(len(ids)))
    chosen: list[tuple[str, float]] = []
    for _ in range(count):
        scored = []
        for index in remaining:
            if centers:
                distance = min(
                    float(
                        torch.clamp(
                            1.0 - torch.dot(candidate_vectors[index], center), 0.0, 2.0
                        )
                    )
                    for center in centers
                )
            else:
                distance = 2.0
            scored.append((-distance, ids[index], index, distance))
        scored.sort()
        _, item, index, distance = scored[0]
        chosen.append((item, distance))
        remaining.remove(index)
        centers.append(candidate_vectors[index])
    return tuple(chosen)


def hybrid_candidates(
    scores: Mapping[str, float], count: int, factor: int = HYBRID_FACTOR
) -> tuple[str, ...]:
    """Top min(factor * count, all) item ids by uncertainty score, ties by ascending id."""
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise DiversityError("count must be a positive integer")
    ordered = sorted(scores, key=lambda item: (-float(scores[item]), item))
    return tuple(ordered[: min(factor * count, len(ordered))])


# ------------------------------------------------------------------ embeddings

EMBEDDINGS_NAME = "embeddings-dinov2-small.npz"
EMBEDDINGS_RECEIPT_NAME = "embeddings-receipt.json"
DINOV2_REPO_ID = "facebook/dinov2-small"
DINOV2_REVISION = "ed25f3a31f01632728cabb09d1542f84ab7b0056"
PINNED_DINOV2_FILES = {
    "config.json": "1809f83e3bdb1609a501a610ad4a742f4fd8ae44d72ca4aa0df52d1f2ac8628d",
    "model.safetensors": "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1",
    "preprocessor_config.json": "14e780d86fa1861f8751f868d7f45425b5feb55c38ca26f152ca5097ab30f828",
}
EMBEDDING_DIMENSION = 384
RECEIPT_TYPE = "lite-embeddings"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Embeddings:
    item_ids: tuple[str, ...]
    vectors: torch.Tensor
    sha256: str

    def rows(self, ids: Sequence[str]) -> torch.Tensor:
        positions = {item: index for index, item in enumerate(self.item_ids)}
        try:
            index = [positions[item] for item in ids]
        except KeyError as error:
            raise DiversityError(f"{error.args[0]} is absent from the embeddings") from None
        return self.vectors[index]


def write_embeddings(path: Path, item_ids: Sequence[str], vectors: torch.Tensor) -> str:
    """Store unit vectors in ascending item_id order; refuse to overwrite."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"{path} already exists")
    vectors = _check_unit(vectors, "vectors")
    if len(item_ids) != vectors.shape[0]:
        raise DiversityError("item ids and vectors disagree in length")
    order = sorted(range(len(item_ids)), key=lambda index: item_ids[index])
    buffer = io.BytesIO()
    np.savez(
        buffer,
        item_ids=np.array([item_ids[index] for index in order], dtype="U64"),
        vectors=vectors[order].cpu().numpy().astype(np.float32),
    )
    data = buffer.getvalue()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    return hashlib.sha256(data).hexdigest()


def load_embeddings(path: Path) -> Embeddings:
    path = Path(path)
    if not path.is_file():
        raise DiversityError(f"embeddings file is unavailable: {path}")
    data = path.read_bytes()
    try:
        archive = np.load(io.BytesIO(data))
        item_ids = tuple(str(item) for item in archive["item_ids"])
        vectors = torch.from_numpy(np.asarray(archive["vectors"], dtype=np.float32))
    except (KeyError, ValueError, OSError) as error:
        raise DiversityError(f"embeddings file is malformed: {error}") from error
    if list(item_ids) != sorted(item_ids) or len(set(item_ids)) != len(item_ids):
        raise DiversityError("embeddings must be stored in ascending unique item_id order")
    return Embeddings(
        item_ids=item_ids,
        vectors=_check_unit(vectors, "vectors"),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def load_pinned_encoder(snapshot: Path, device: str) -> Callable[[list[Image.Image]], torch.Tensor]:
    """Load the pinned DINOv2-small offline after verifying its three files."""
    root = Path(snapshot)
    for name, expected in PINNED_DINOV2_FILES.items():
        candidate = root / name
        if not candidate.is_file():
            raise DiversityError(f"snapshot lacks {name}: {root}")
        actual = sha256_file(candidate)
        if actual != expected:
            raise DiversityError(
                f"{name} hash {actual[:12]}… differs from the pinned {expected[:12]}…"
            )
    from transformers import AutoImageProcessor, Dinov2Model

    processor = AutoImageProcessor.from_pretrained(root, local_files_only=True)
    model = Dinov2Model.from_pretrained(root, local_files_only=True, use_safetensors=True)
    model.eval().to(device)

    @torch.no_grad()
    def encode(images: list[Image.Image]) -> torch.Tensor:
        inputs = processor(images=images, return_tensors="pt")
        hidden = model(pixel_values=inputs["pixel_values"].to(device)).last_hidden_state[:, 0]
        return torch.nn.functional.normalize(hidden.to(dtype=torch.float32), dim=1).cpu()

    return encode


def embed_pool(
    manifest: Mapping[str, Any],
    image_index: Mapping[str, Path],
    snapshot: Path,
    *,
    device: str = "cpu",
    batch_size: int = 32,
    encoder: Callable[[list[Image.Image]], torch.Tensor] | None = None,
) -> tuple[tuple[str, ...], torch.Tensor]:
    """Encode every pool row (never test rows) in ascending item_id order."""
    rows = sorted(
        (row for row in manifest.get("images", ()) if row.get("split") == "pool"),
        key=lambda row: str(row["item_id"]),
    )
    if not rows:
        raise DiversityError("manifest has no pool rows")
    if encoder is None:
        encoder = load_pinned_encoder(snapshot, device)
    chunks: list[torch.Tensor] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        images = [load_sample(image_index, row).image for row in batch]
        vectors = encoder(images)
        if vectors.shape[0] != len(batch):
            raise DiversityError("encoder returned the wrong number of vectors")
        chunks.append(vectors.to(dtype=torch.float32))
    return tuple(str(row["item_id"]) for row in rows), _check_unit(torch.cat(chunks), "vectors")


@command("lite embed")
def embed_main(argv: Sequence[str] | None = None) -> int:
    """Compute the pool embeddings once and bind them to the manifest and the pinned encoder."""
    parser = argparse.ArgumentParser(prog="val lite embed")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=32)
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    output = Path(arguments.output_dir)
    try:
        manifest = json.loads(Path(arguments.manifest).read_text(encoding="utf-8"))
        image_index = build_image_index(Path(arguments.images))
    except (OSError, ValueError, DatasetError) as error:
        print(f"lite embed input error: {error}", file=sys.stderr)
        return 3
    if (output / EMBEDDINGS_NAME).exists() or (output / EMBEDDINGS_RECEIPT_NAME).exists():
        print(f"lite embed refuses to overwrite {output}", file=sys.stderr)
        return 2
    try:
        ids, vectors = embed_pool(
            manifest,
            image_index,
            Path(arguments.snapshot),
            device=arguments.device,
            batch_size=arguments.batch_size,
        )
        digest = write_embeddings(output / EMBEDDINGS_NAME, ids, vectors)
        write_json_no_clobber(
            output / EMBEDDINGS_RECEIPT_NAME,
            {
                "receipt_type": RECEIPT_TYPE,
                "schema_version": SCHEMA_VERSION,
                "normative": {
                    "manifest_sha256": manifest_sha256(manifest),
                    "encoder": DINOV2_REPO_ID,
                    "revision": DINOV2_REVISION,
                    "snapshot_files": {
                        name: sha256_file(Path(arguments.snapshot) / name)
                        for name in PINNED_DINOV2_FILES
                    },
                    "image_count": len(ids),
                    "dimension": int(vectors.shape[1]),
                    "embeddings_file": EMBEDDINGS_NAME,
                    "embeddings_sha256": digest,
                    "device": arguments.device,
                },
            },
        )
    except (DiversityError, DatasetError, OSError, RuntimeError, FileExistsError) as error:
        print(f"lite embed failed: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "image_count": len(ids),
                "dimension": int(vectors.shape[1]),
                "embeddings_sha256": digest,
            }
        )
    )
    return 0
