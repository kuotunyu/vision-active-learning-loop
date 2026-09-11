"""Contracts for the v0.3 diversity arms: k-center, hybrid candidates, embeddings."""

from __future__ import annotations

import math

import pytest
import torch

from vision_active_learning_loop.lite.diversity import (
    HYBRID_FACTOR,
    DiversityError,
    cosine_distances,
    hybrid_candidates,
    k_center_reference,
    k_center_select,
)


def _unit(rows: list[list[float]]) -> torch.Tensor:
    tensor = torch.tensor(rows, dtype=torch.float32)
    return tensor / tensor.norm(dim=1, keepdim=True)


def test_cosine_distance_is_one_minus_dot_and_clamped() -> None:
    a = _unit([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    centers = _unit([[1.0, 0.0]])
    distances = cosine_distances(a, centers)
    assert distances.shape == (3, 1)
    assert distances[0, 0] == pytest.approx(0.0)
    assert distances[1, 0] == pytest.approx(1.0)
    assert distances[2, 0] == pytest.approx(2.0)


def test_cosine_distance_requires_unit_vectors() -> None:
    with pytest.raises(DiversityError, match="normal"):
        cosine_distances(torch.tensor([[2.0, 0.0]]), _unit([[1.0, 0.0]]))


def test_k_center_picks_the_farthest_from_the_nearest_center_each_step() -> None:
    ids = ("a", "b", "c", "d")
    candidates = _unit([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.7, 0.7]])
    centers = _unit([[1.0, 0.0]])
    chosen = k_center_select(ids, candidates, centers, 2)
    # c is opposite the center (distance 2); then b is 1.0 from both the center
    # and c, while d is ~0.29 from the center -> b
    assert [item for item, _ in chosen] == ["c", "b"]
    assert chosen[0][1] == pytest.approx(2.0)
    assert chosen[1][1] == pytest.approx(1.0)


def test_k_center_breaks_exact_ties_by_ascending_item_id() -> None:
    ids = ("zeta", "alpha", "mid")
    candidates = _unit([[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]])
    centers = _unit([[1.0, 0.0]])
    chosen = k_center_select(ids, candidates, centers, 2)
    assert [item for item, _ in chosen] == ["alpha", "mid"]
    assert chosen[1][1] == pytest.approx(0.0)


def test_k_center_with_no_centers_starts_from_the_smallest_id() -> None:
    ids = ("b", "a")
    candidates = _unit([[1.0, 0.0], [0.0, 1.0]])
    chosen = k_center_select(ids, candidates, torch.zeros((0, 2)), 2)
    assert [item for item, _ in chosen] == ["a", "b"]
    assert chosen[0][1] == pytest.approx(2.0)


def test_k_center_rejects_more_than_the_candidates() -> None:
    with pytest.raises(DiversityError, match="count"):
        k_center_select(("a",), _unit([[1.0, 0.0]]), _unit([[0.0, 1.0]]), 2)


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_k_center_matches_the_reference_on_random_matrices(seed: int) -> None:
    generator = torch.Generator().manual_seed(seed)
    candidates = torch.randn((60, 8), generator=generator)
    candidates = candidates / candidates.norm(dim=1, keepdim=True)
    centers = torch.randn((5, 8), generator=generator)
    centers = centers / centers.norm(dim=1, keepdim=True)
    ids = tuple(f"item-{index:03d}" for index in range(60))
    fast = k_center_select(ids, candidates, centers, 12)
    slow = k_center_reference(ids, candidates, centers, 12)
    assert [item for item, _ in fast] == [item for item, _ in slow]
    for (_, a), (_, b) in zip(fast, slow):
        assert math.isclose(a, b, rel_tol=0, abs_tol=1e-5)


def test_hybrid_candidates_take_the_top_factor_times_count_by_score_then_id() -> None:
    scores = {"a": 0.9, "b": 0.9, "c": 0.5, "d": 0.1, "e": 0.7}
    assert hybrid_candidates(scores, count=1, factor=2) == ("a", "b")
    assert hybrid_candidates(scores, count=1, factor=3) == ("a", "b", "e")
    assert hybrid_candidates(scores, count=10) == ("a", "b", "e", "c", "d")
    assert HYBRID_FACTOR == 5


# ------------------------------------------------------------------ embeddings

import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
from pathlib import Path  # noqa: E402

from PIL import Image  # noqa: E402

from vision_active_learning_loop.lite.diversity import (  # noqa: E402
    EMBEDDINGS_NAME,
    EMBEDDINGS_RECEIPT_NAME,
    PINNED_DINOV2_FILES,
    Embeddings,
    embed_main,
    embed_pool,
    load_embeddings,
    write_embeddings,
)
from vision_active_learning_loop.lite.manifest import SCHEMA_VERSION, manifest_sha256  # noqa: E402
from vision_active_learning_loop.models.assets import (  # noqa: E402
    _CANONICAL_MODEL_FILES,
    DINOV2_REVISION,
)


def test_pinned_dinov2_files_match_the_asset_registry() -> None:
    registry = {name: spec.sha256 for name, spec in _CANONICAL_MODEL_FILES["dinov2"].items()}
    # the registry also pins README.md, which the encoder never loads
    assert PINNED_DINOV2_FILES == {name: registry[name] for name in PINNED_DINOV2_FILES}
    assert set(PINNED_DINOV2_FILES) == {"config.json", "model.safetensors", "preprocessor_config.json"}


def test_embeddings_round_trip_binds_the_file_hash(tmp_path: Path) -> None:
    ids = ("b" * 64, "a" * 64)
    vectors = _unit([[1.0, 0.0], [0.0, 1.0]])
    digest = write_embeddings(tmp_path / EMBEDDINGS_NAME, ids, vectors)
    loaded = load_embeddings(tmp_path / EMBEDDINGS_NAME)
    assert isinstance(loaded, Embeddings)
    assert loaded.sha256 == digest == hashlib.sha256((tmp_path / EMBEDDINGS_NAME).read_bytes()).hexdigest()
    assert loaded.item_ids == ("a" * 64, "b" * 64)  # stored in ascending id order
    assert torch.allclose(loaded.rows(["b" * 64]), _unit([[1.0, 0.0]]))
    with pytest.raises(DiversityError, match="absent"):
        loaded.rows(["c" * 64])
    with pytest.raises(FileExistsError):
        write_embeddings(tmp_path / EMBEDDINGS_NAME, ids, vectors)


def _tiny_manifest(tmp_path: Path) -> tuple[dict, dict[str, Path]]:
    rows, index = [], {}
    for number, split in enumerate(("pool", "pool", "test")):
        image = Image.new("RGB", (32, 24), color=(number * 40, 10, 200))
        path = tmp_path / f"img-{number}.png"
        image.save(path)
        item_id = hashlib.sha256(path.read_bytes()).hexdigest()
        index[item_id] = path
        rows.append({"item_id": item_id, "width": 32, "height": 24, "split": split, "boxes": []})
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": "9" * 64,
        "image_count": 3,
        "box_count": 0,
        "class_box_counts": {"D00": 0, "D10": 0, "D20": 0, "D40": 0},
        "alias_count": 0,
        "discarded_box_count": 0,
        "negative_image_count": 3,
        "images": sorted(rows, key=lambda row: row["item_id"]),
    }
    return manifest, index


def test_embed_pool_encodes_only_pool_rows_in_ascending_id_order(tmp_path: Path) -> None:
    manifest, index = _tiny_manifest(tmp_path)
    seen: list[int] = []

    def fake_encoder(images):
        seen.append(len(images))
        out = torch.tensor([[float(image.size[0]), 1.0, 0.0] for image in images])
        return out / out.norm(dim=1, keepdim=True)

    ids, vectors = embed_pool(manifest, index, tmp_path / "snapshot", encoder=fake_encoder, batch_size=1)
    pool_ids = tuple(row["item_id"] for row in manifest["images"] if row["split"] == "pool")
    assert ids == pool_ids
    assert vectors.shape == (2, 3)
    assert seen == [1, 1]
    assert torch.allclose(vectors.norm(dim=1), torch.ones(2))


def test_embed_main_writes_the_file_and_a_bound_receipt(tmp_path: Path, monkeypatch) -> None:
    manifest, index = _tiny_manifest(tmp_path)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    images = tmp_path / "images"
    images.mkdir()
    for path in index.values():
        (images / path.name).write_bytes(path.read_bytes())
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    for name in PINNED_DINOV2_FILES:
        (snapshot / name).write_bytes(b"not the real file")

    import vision_active_learning_loop.lite.diversity as module

    def fake_loader(snapshot_path, device):
        return lambda batch: torch.nn.functional.normalize(torch.ones((len(batch), 4)), dim=1)

    monkeypatch.setattr(module, "load_pinned_encoder", fake_loader)
    arguments = [
        "--manifest", str(tmp_path / "manifest.json"),
        "--images", str(images),
        "--snapshot", str(snapshot),
        "--output-dir", str(tmp_path / "out"),
    ]
    assert embed_main(arguments) == 0
    receipt = json.loads((tmp_path / "out" / EMBEDDINGS_RECEIPT_NAME).read_text(encoding="utf-8"))["normative"]
    assert receipt["manifest_sha256"] == manifest_sha256(manifest)
    assert receipt["revision"] == DINOV2_REVISION
    assert receipt["image_count"] == 2
    assert receipt["dimension"] == 4
    assert set(receipt["snapshot_files"]) == set(PINNED_DINOV2_FILES)
    loaded = load_embeddings(tmp_path / "out" / EMBEDDINGS_NAME)
    assert receipt["embeddings_sha256"] == loaded.sha256
    assert loaded.vectors.shape == (2, 4)
    # second run must not clobber
    assert embed_main(arguments) == 2


@pytest.mark.skipif(not os.environ.get("VAL_DINOV2_SNAPSHOT"), reason="set VAL_DINOV2_SNAPSHOT to the pinned DINOv2 snapshot")
def test_pinned_encoder_returns_unit_384_vectors() -> None:
    from vision_active_learning_loop.lite.diversity import load_pinned_encoder

    encoder = load_pinned_encoder(Path(os.environ["VAL_DINOV2_SNAPSHOT"]), "cpu")
    batch = [Image.new("RGB", (300, 200), color=(120, 30, 30)), Image.new("RGB", (64, 64), color=(0, 200, 0))]
    vectors = encoder(batch)
    assert vectors.shape == (2, 384)
    assert vectors.dtype == torch.float32
    assert torch.allclose(vectors.norm(dim=1), torch.ones(2), atol=1e-4)
