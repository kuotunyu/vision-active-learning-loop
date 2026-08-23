from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from vision_active_learning_loop.models.assets import (
    APPROVED_MODELS,
    AssetMismatch,
    LicenseMismatch,
    RevisionMismatch,
    SourceMismatch,
    load_pinned_asset_specs,
    main,
    verify_snapshot,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "models" / "pinned-models.yaml"
RTDETR_REVISION = "cc5b50f32f0100caaa3bd275343e2fb17762c73d"
DINO_REVISION = "ed25f3a31f01632728cabb09d1542f84ab7b0056"


@pytest.fixture
def specs():
    return load_pinned_asset_specs(CONFIG_PATH)


def _snapshot_root(tmp_path: Path, repo_id: str, revision: str) -> Path:
    root = (
        tmp_path
        / f"models--{repo_id.replace('/', '--')}"
        / "snapshots"
        / revision
    )
    root.mkdir(parents=True)
    return root


def test_rtdetr_weight_hash_is_exact(specs) -> None:
    spec = specs["rtdetr"]

    assert spec.repo_id == "PekingU/rtdetr_r18vd"
    assert spec.revision == RTDETR_REVISION
    assert spec.files["model.safetensors"].size == 80_904_152
    assert spec.files["model.safetensors"].sha256 == (
        "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093"
    )


def test_dinov2_weight_hash_and_size_are_exact(specs) -> None:
    spec = specs["dinov2"]
    weight = spec.files["model.safetensors"]

    assert spec.repo_id == "facebook/dinov2-small"
    assert spec.revision == DINO_REVISION
    assert weight.sha256 == (
        "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1"
    )
    assert weight.size == 88_249_960


def test_only_exact_repository_revision_pairs_are_approved() -> None:
    assert APPROVED_MODELS == {
        "PekingU/rtdetr_r18vd": RTDETR_REVISION,
        "facebook/dinov2-small": DINO_REVISION,
    }


def test_transformers_source_pins_cannot_be_rewritten_to_match_a_machine(
    tmp_path: Path,
) -> None:
    document = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    source = document["transformers"]["source_files"]
    source["models/dinov2/modeling_dinov2.py"]["sha256"] = "0" * 64
    modified = tmp_path / "modified.yaml"
    modified.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(SourceMismatch, match="source pins"):
        load_pinned_asset_specs(modified)


def test_tracked_config_uses_only_logical_external_roots() -> None:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    windows_machine_root = "D:" + chr(92)
    linux_machine_root = "/" + "mnt/d"

    assert "VAL_ARTIFACT_ROOT" in text
    assert windows_machine_root not in text
    assert linux_machine_root not in text


def test_dino_license_rejects_noncommercial_card(specs, tmp_path: Path) -> None:
    root = _snapshot_root(
        tmp_path, "facebook/dinov2-small", DINO_REVISION
    )
    (root / "README.md").write_text(
        "---\nlicense: cc-by-nc-4.0\n---\n# Historical DINOv2 card\n",
        encoding="utf-8",
    )

    with pytest.raises(LicenseMismatch, match="Apache-2.0"):
        verify_snapshot(specs["dinov2"], root)


def test_revision_mismatch_is_rejected_before_file_acceptance(
    specs, tmp_path: Path
) -> None:
    root = _snapshot_root(
        tmp_path,
        "facebook/dinov2-small",
        "0" * 40,
    )
    (root / "README.md").write_text(
        "---\nlicense: apache-2.0\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(RevisionMismatch, match=DINO_REVISION):
        verify_snapshot(specs["dinov2"], root)


def test_tampered_weight_size_is_rejected(specs, tmp_path: Path) -> None:
    root = _snapshot_root(tmp_path, "PekingU/rtdetr_r18vd", RTDETR_REVISION)
    (root / "README.md").write_text(
        "---\nlicense: apache-2.0\n---\n",
        encoding="utf-8",
    )
    (root / "model.safetensors").write_bytes(b"tampered")

    with pytest.raises(AssetMismatch, match="model.safetensors.*size"):
        verify_snapshot(specs["rtdetr"], root)


@pytest.mark.parametrize("failure_kind", ["tamper", "revision", "license"])
def test_cli_failure_writes_fail_receipt_and_exits_two(
    specs,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
) -> None:
    artifact_root = tmp_path / "artifacts"
    cache_root = artifact_root / "wave0" / "model_cache"
    revision = RTDETR_REVISION if failure_kind != "revision" else "0" * 40
    root = _snapshot_root(
        cache_root, "PekingU/rtdetr_r18vd", revision
    )
    license_id = "cc-by-nc-4.0" if failure_kind == "license" else "apache-2.0"
    (root / "README.md").write_text(
        f"---\nlicense: {license_id}\n---\n",
        encoding="utf-8",
    )
    (root / "model.safetensors").write_bytes(b"tampered")
    output = artifact_root / "wave0" / "receipts" / "model-assets.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")

    exit_code = main(
        [
            "--config",
            str(CONFIG_PATH),
            "--cache-root",
            str(cache_root),
            "--output",
            str(output),
        ]
    )

    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert receipt["normative"]["status"] == "FAIL"
    assert receipt["normative"]["errors"]
    assert receipt["normative"]["invariants"]["all_assets_verified"] is False
    assert "VAL_DATA_ROOT" not in output.read_text(encoding="utf-8")
