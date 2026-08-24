import copy
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
import torch
from PIL import Image

import vision_active_learning_loop.probes.model_contract as model_contract_probe
from vision_active_learning_loop.probes.model_contract import (
    ModelContractInputError,
    build_contract_processor,
    observe_processor_contract,
    prepare_contract_batch,
)

FIXTURE_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "synthetic"
    / "wave0"
    / "fixture-manifest.json"
)
FIXTURE_SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "generate_wave0_fixtures.py"
)


def _fixture_generator():
    spec = importlib.util.spec_from_file_location(
        "wave0_fixture_generator", FIXTURE_SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_dimensions() -> None:
    """Catch missing or accidentally identical aspect-ratio probe inputs."""
    generator = _fixture_generator()
    fixtures = generator.build_fixture_images(generator.load_manifest(FIXTURE_MANIFEST))

    assert [image.size for image in fixtures] == [(640, 320), (320, 640)]
    assert fixtures[0].tobytes() != fixtures[1].tobytes()


def test_fixture_manifest_binds_exact_pixels() -> None:
    """Catch a changed generator pattern hidden behind unchanged dimensions."""
    generator = _fixture_generator()
    manifest = generator.load_manifest(FIXTURE_MANIFEST)
    fixtures = generator.build_fixture_images(manifest)

    observed = [hashlib.sha256(image.tobytes()).hexdigest() for image in fixtures]
    assert observed == [item["pixel_sha256"] for item in manifest["images"]]


def test_registered_synthetic_targets_have_exact_digests_and_geometry() -> None:
    """Catch drift or duplication in the only labels allowed in Wave 0."""
    fixture = model_contract_probe.load_synthetic_contract_fixture(FIXTURE_MANIFEST)

    assert fixture.input_sha256 == (
        "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f"
    )
    assert fixture.target_sha256 == (
        "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
    )
    assert fixture.annotations == [
        {
            "fixture_id": "wide-gradient",
            "image_id": 1,
            "annotations": [
                {
                    "id": 1,
                    "image_id": 1,
                    "category_id": 0,
                    "bbox": [64.0, 32.0, 192.0, 96.0],
                    "area": 18432.0,
                    "iscrowd": 0,
                }
            ],
        },
        {
            "fixture_id": "tall-checker",
            "image_id": 2,
            "annotations": [
                {
                    "id": 2,
                    "image_id": 2,
                    "category_id": 3,
                    "bbox": [32.0, 128.0, 96.0, 256.0],
                    "area": 24576.0,
                    "iscrowd": 0,
                }
            ],
        },
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        "category_out_of_range",
        "fixture_image_mismatch",
        "box_outside_image",
        "wrong_area",
        "extra_image",
        "extra_target",
        "input_digest_drift",
        "target_digest_drift",
    ],
)
def test_registered_synthetic_target_rejects_invalid_or_drifted_manifest(
    tmp_path: Path, mutation: str
) -> None:
    """Catch malformed or self-consistently edited synthetic target evidence."""
    document = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    if mutation == "category_out_of_range":
        document["targets"][0]["annotations"][0]["category_id"] = 4
    elif mutation == "fixture_image_mismatch":
        document["targets"][0]["image_id"] = 2
    elif mutation == "box_outside_image":
        document["targets"][0]["annotations"][0]["bbox"] = [600.0, 1.0, 50.0, 2.0]
    elif mutation == "wrong_area":
        document["targets"][0]["annotations"][0]["area"] = 1.0
    elif mutation == "extra_image":
        document["images"].append(copy.deepcopy(document["images"][0]))
    elif mutation == "extra_target":
        document["targets"].append(copy.deepcopy(document["targets"][0]))
    elif mutation == "input_digest_drift":
        document["images"][0]["pixel_sha256"] = "0" * 64
    elif mutation == "target_digest_drift":
        document["targets"][0]["annotations"][0]["bbox"][0] = 65.0
        document["targets"][0]["annotations"][0]["area"] = 192.0 * 96.0
    path = tmp_path / "fixture-manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ModelContractInputError):
        model_contract_probe.load_synthetic_contract_fixture(path)


def test_fixture_materialization_is_confined_to_wave0(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch synthetic fixture writes outside the declared external artifact root."""
    generator = _fixture_generator()
    manifest = generator.load_manifest(FIXTURE_MANIFEST)
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    output_root = tmp_path / "wave0" / "fixtures" / "synthetic" / "wave0"

    generated = generator.materialize_fixtures(manifest, output_root)

    assert [path.name for path in generated] == [
        "wide-gradient.ppm",
        "tall-checker.ppm",
    ]
    assert [Image.open(path).size for path in generated] == [(640, 320), (320, 640)]
    with pytest.raises(ValueError, match="VAL_ARTIFACT_ROOT/wave0"):
        generator.materialize_fixtures(manifest, tmp_path / "outside")


def test_fixture_filename_cannot_escape_its_output_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch a manifest filename redirecting generated bytes to an ancestor."""
    generator = _fixture_generator()
    manifest = copy.deepcopy(generator.load_manifest(FIXTURE_MANIFEST))
    manifest["images"][0]["filename"] = "../escaped.ppm"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    output_root = tmp_path / "wave0" / "fixtures" / "synthetic" / "wave0"

    with pytest.raises(ValueError, match="filename"):
        generator.materialize_fixtures(manifest, output_root)


def test_fixture_materialization_rejects_val_data_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch accidental dataset-bound fixture execution in Wave 0."""
    generator = _fixture_generator()
    manifest = generator.load_manifest(FIXTURE_MANIFEST)
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.setenv("VAL_DATA_ROOT", str(tmp_path / "rdd"))

    with pytest.raises(ValueError, match="VAL_DATA_ROOT"):
        generator.materialize_fixtures(
            manifest, tmp_path / "wave0" / "fixtures" / "synthetic" / "wave0"
        )


def test_fixture_materialization_rejects_linked_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch a link or junction redirecting generated fixtures."""
    generator = _fixture_generator()
    manifest = generator.load_manifest(FIXTURE_MANIFEST)
    wave_root = tmp_path / "wave0"
    wave_root.mkdir()
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        generator,
        "_is_link_or_junction",
        lambda path: Path(path) == wave_root,
    )

    with pytest.raises(ValueError, match="link"):
        generator.materialize_fixtures(
            manifest, wave_root / "fixtures" / "synthetic" / "wave0"
        )


def test_fixture_materialization_rejects_preexisting_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch following or overwriting an attacker-controlled partial path."""
    generator = _fixture_generator()
    manifest = generator.load_manifest(FIXTURE_MANIFEST)
    output_root = tmp_path / "wave0" / "fixtures" / "synthetic" / "wave0"
    output_root.mkdir(parents=True)
    partial = output_root / "wide-gradient.ppm.partial"
    partial.write_bytes(b"do-not-overwrite")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)

    with pytest.raises(ValueError, match="partial"):
        generator.materialize_fixtures(manifest, output_root)

    assert partial.read_bytes() == b"do-not-overwrite"


@pytest.fixture
def fixture_images():
    generator = _fixture_generator()
    return generator.build_fixture_images(generator.load_manifest(FIXTURE_MANIFEST))


def test_processor_uses_aspect_preserving_resize_and_bottom_right_zero_padding(
    fixture_images,
) -> None:
    """Catch square warping, normalization, wrong padding, or label injection."""
    processor = build_contract_processor()
    batch = prepare_contract_batch(processor, fixture_images)
    observation = observe_processor_contract(processor, batch)

    assert observation.shapes == {
        "pixel_values": [2, 3, 640, 640],
        "pixel_mask": [2, 640, 640],
    }
    assert all(observation.invariants.values())
    assert "labels" not in batch
    assert torch.count_nonzero(batch["pixel_values"][0, :, 320:, :]) == 0
    assert torch.count_nonzero(batch["pixel_values"][1, :, :, 320:]) == 0


def test_wrong_valid_mask_fails_processor_contract(
    fixture_images,
) -> None:
    """Catch accepting an incorrect valid-image rectangle."""
    processor = build_contract_processor()
    batch = prepare_contract_batch(processor, fixture_images)
    batch["pixel_mask"] = batch["pixel_mask"].clone()
    batch["pixel_mask"][0, 319, 639] = 0

    observation = observe_processor_contract(processor, batch)

    assert observation.invariants["expected_valid_mask_rectangles"] is False
