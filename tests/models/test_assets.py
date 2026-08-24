from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

import vision_active_learning_loop.artifacts.receipts as receipt_module
from vision_active_learning_loop.artifacts.digests import (
    canonical_json_sha256,
    sha256_file,
)
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt_for_run,
)
from vision_active_learning_loop.models.assets import (
    APPROVED_MODELS,
    ArtifactBoundaryError,
    AssetMismatch,
    FileSpec,
    LicenseMismatch,
    PinnedAssetSpec,
    RevisionMismatch,
    SourceMismatch,
    _external_roots,
    load_pinned_asset_specs,
    main,
    verify_snapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "models" / "pinned-models.yaml"
RTDETR_REVISION = "cc5b50f32f0100caaa3bd275343e2fb17762c73d"
DINO_REVISION = "ed25f3a31f01632728cabb09d1542f84ab7b0056"
METADATA_IDENTITY = {
    "rtdetr": {
        "README.md": (
            "8911a08498e4b2a1118faa1d63b091c5b237b24d",
            "8911a08498e4b2a1118faa1d63b091c5b237b24d",
        ),
        "config.json": (
            "2bc5c87afa01965b4d6dd65053a0b087c013aee2",
            "2bc5c87afa01965b4d6dd65053a0b087c013aee2",
        ),
        "model.safetensors": (
            "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
            "99878207a862ab963eafb175cd79c4364fa1db62",
        ),
        "preprocessor_config.json": (
            "0eaa5c051317a3725f47218ae30b6e654f0ece36",
            "0eaa5c051317a3725f47218ae30b6e654f0ece36",
        ),
    },
    "dinov2": {
        "README.md": (
            "6b3380957df44ed203ec1d5102e1245accbbbba9",
            "6b3380957df44ed203ec1d5102e1245accbbbba9",
        ),
        "config.json": (
            "5664b325e6258d3960fad8c4c1cff958f3cc2272",
            "5664b325e6258d3960fad8c4c1cff958f3cc2272",
        ),
        "model.safetensors": (
            "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1",
            "e13b8fec08e8dd9ac531165e7c8c0ec7d467952a",
        ),
        "preprocessor_config.json": (
            "ff5b47c2edcd1d3556d63c01a65d93b58b9efce1",
            "ff5b47c2edcd1d3556d63c01a65d93b58b9efce1",
        ),
    },
}


@pytest.fixture
def specs():
    return load_pinned_asset_specs(CONFIG_PATH)


@pytest.fixture(autouse=True)
def _bind_minimal_test_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep synthetic unit receipts small while exercising exact hash binding."""
    empty_hash = canonical_json_sha256({})
    monkeypatch.setattr(
        receipt_module,
        "_APPROVED_MODEL_DOCUMENT_HASHES",
        {
            name: {"config": empty_hash, "processor": empty_hash}
            for name in ("rtdetr", "dinov2")
        },
    )


def _snapshot_root(tmp_path: Path, repo_id: str, revision: str) -> Path:
    root = tmp_path / f"models--{repo_id.replace('/', '--')}" / "snapshots" / revision
    root.mkdir(parents=True)
    return root


def _write_huggingface_metadata(root: Path, spec) -> None:
    metadata_root = root / ".cache" / "huggingface"
    download_root = metadata_root / "download"
    tree_root = metadata_root / "trees"
    download_root.mkdir(parents=True)
    tree_root.mkdir()
    (metadata_root / ".gitignore").write_bytes(b"*")
    (metadata_root / "CACHEDIR.TAG").write_text(
        "Signature: 8a477f597d28d172789f06886806bc55\n",
        encoding="utf-8",
    )
    tree_files = {}
    for name, expected in spec.files.items():
        etag, blob_id = METADATA_IDENTITY[spec.name][name]
        (download_root / f"{name}.metadata").write_text(
            f"{spec.revision}\n{etag}\n1.0\n",
            encoding="utf-8",
        )
        entry = {"size": expected.size, "blob_id": blob_id}
        if name == "model.safetensors":
            entry.update(lfs_sha256=expected.sha256, lfs_size=expected.size)
        tree_files[name] = entry
    (tree_root / f"{spec.revision}.json").write_text(
        json.dumps({"format_version": 1, "files": tree_files}),
        encoding="utf-8",
    )


def _minimal_model_receipt(spec, metadata_identity):
    revision = spec.revision
    metadata_inventory = {
        ".cache/huggingface/.gitignore": {"size": 1, "sha256": "a" * 64},
        ".cache/huggingface/CACHEDIR.TAG": {"size": 1, "sha256": "a" * 64},
        f".cache/huggingface/trees/{revision}.json": {
            "size": 1,
            "sha256": "a" * 64,
        },
    }
    metadata_files = {}
    for name in spec.files:
        path = f".cache/huggingface/download/{name}.metadata"
        metadata_inventory[path] = {"size": 1, "sha256": "a" * 64}
        etag, blob_id = metadata_identity[name]
        metadata_files[name] = {
            "metadata_path": path,
            "commit_hash": revision,
            "etag": etag,
            "blob_id": blob_id,
            "timestamp": 1.0,
            "size": 1,
            "sha256": "a" * 64,
        }
    files = {
        name: {"size": item.size, "sha256": item.sha256}
        for name, item in spec.files.items()
    }
    return {
        "name": spec.name,
        "repo_id": spec.repo_id,
        "revision": revision,
        "license": "apache-2.0",
        "license_evidence": {
            "path": "README.md",
            "size": spec.files["README.md"].size,
            "sha256": spec.files["README.md"].sha256,
        },
        "files": files,
        "huggingface_metadata": {
            "commit_hash": revision,
            "files": metadata_files,
            "inventory": metadata_inventory,
        },
        "config": {},
        "processor": {},
    }


def _valid_model_asset_receipt(specs):
    source_files = {
        name: {"size": item.size, "sha256": item.sha256}
        for name, item in specs["rtdetr"].source_files.items()
    }
    return {
        "receipt_type": "model-assets",
        "schema_version": 1,
        "normative": {
            "models": {
                name: _minimal_model_receipt(spec, METADATA_IDENTITY[name])
                for name, spec in specs.items()
            },
            "transformers": {"version": "5.15.0", "files": source_files},
            "invariants": {
                "all_assets_verified": True,
                "exact_revisions": True,
                "exact_file_inventory": True,
                "exact_huggingface_metadata": True,
                "apache_2_0_licenses": True,
                "exact_transformers_source": True,
                "data_root_unset": True,
            },
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": "run-a"},
    }


def test_model_asset_receipt_requires_run_identity(specs, tmp_path: Path) -> None:
    """Catch publishing model assets outside the fresh run-scoped A2 chain."""
    receipt = _valid_model_asset_receipt(specs)
    atomic_write_receipt(tmp_path / "model-assets.json", receipt)

    without_run = _valid_model_asset_receipt(specs)
    del without_run["metadata"]["run_id"]
    with pytest.raises(ReceiptValidationError, match="run_id"):
        atomic_write_receipt(tmp_path / "missing-run.json", without_run)


def test_model_asset_parent_from_another_run_is_rejected(specs, tmp_path: Path) -> None:
    """Catch cross-run asset evidence entering a fresh model-contract chain."""
    output = tmp_path / "model-assets.json"
    receipt = _valid_model_asset_receipt(specs)
    receipt["metadata"]["run_id"] = "run-b"
    atomic_write_receipt(output, receipt)
    stored = json.loads(output.read_text(encoding="utf-8"))

    with pytest.raises(ReceiptValidationError, match="run_id"):
        validate_receipt_for_run(
            stored,
            PROJECT_ROOT / "schemas" / "model-asset-receipt.schema.json",
            "run-a",
        )


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


def test_rtdetr_loss_source_pin_is_exact(specs) -> None:
    """Catch omitting or repinning the official labeled-loss implementation."""
    loss = specs["rtdetr"].source_files["loss/loss_rt_detr.py"]

    assert loss.size == 22_057
    assert loss.sha256 == (
        "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
    )


@pytest.mark.parametrize("mutation", ["missing", "altered", "extra"])
def test_rtdetr_loss_source_inventory_fails_closed(
    tmp_path: Path, mutation: str
) -> None:
    """Catch a missing, changed, or expanded official loss-source inventory."""
    document = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    sources = document["transformers"]["source_files"]
    if mutation == "missing":
        sources.pop("loss/loss_rt_detr.py", None)
    elif mutation == "altered":
        sources.setdefault("loss/loss_rt_detr.py", {})["sha256"] = "0" * 64
    else:
        sources["loss/extra.py"] = {"size": 1, "sha256": "0" * 64}
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
    root = _snapshot_root(tmp_path, "facebook/dinov2-small", DINO_REVISION)
    _write_huggingface_metadata(root, specs["dinov2"])
    (root / "README.md").write_text(
        "---\nlicense: cc-by-nc-4.0\n---\n# Historical DINOv2 card\n",
        encoding="utf-8",
    )
    for name in ("config.json", "model.safetensors", "preprocessor_config.json"):
        (root / name).write_bytes(b"{}")

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
    _write_huggingface_metadata(root, specs["rtdetr"])
    (root / "README.md").write_text(
        "---\nlicense: apache-2.0\n---\n",
        encoding="utf-8",
    )
    (root / "model.safetensors").write_bytes(b"tampered")
    (root / "config.json").write_bytes(b"{}")
    (root / "preprocessor_config.json").write_bytes(b"{}")

    with pytest.raises(AssetMismatch, match="model.safetensors.*size"):
        verify_snapshot(specs["rtdetr"], root)


def test_correctly_named_snapshot_without_hf_metadata_is_rejected(
    specs, tmp_path: Path
) -> None:
    root = _snapshot_root(tmp_path, "PekingU/rtdetr_r18vd", RTDETR_REVISION)

    with pytest.raises(RevisionMismatch, match="metadata"):
        verify_snapshot(specs["rtdetr"], root)


def test_hf_metadata_with_wrong_commit_is_rejected(specs, tmp_path: Path) -> None:
    spec = specs["dinov2"]
    root = _snapshot_root(tmp_path, spec.repo_id, spec.revision)
    _write_huggingface_metadata(root, spec)
    metadata = root / ".cache" / "huggingface" / "download" / "README.md.metadata"
    lines = metadata.read_text(encoding="utf-8").splitlines()
    lines[0] = "0" * 40
    metadata.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(RevisionMismatch, match="metadata commit"):
        verify_snapshot(spec, root)


def test_hf_metadata_with_wrong_etag_is_rejected(specs, tmp_path: Path) -> None:
    spec = specs["rtdetr"]
    root = _snapshot_root(tmp_path, spec.repo_id, spec.revision)
    _write_huggingface_metadata(root, spec)
    metadata = root / ".cache" / "huggingface" / "download" / "config.json.metadata"
    lines = metadata.read_text(encoding="utf-8").splitlines()
    lines[1] = "0" * 40
    metadata.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(RevisionMismatch, match="etag"):
        verify_snapshot(spec, root)


def test_payload_symlink_escape_is_rejected(
    specs, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = specs["rtdetr"]
    root = _snapshot_root(tmp_path, spec.repo_id, spec.revision)
    _write_huggingface_metadata(root, spec)
    model_path = root / "model.safetensors"
    model_path.write_bytes(b"outside")
    (root / "README.md").write_text("---\nlicense: apache-2.0\n---\n", encoding="utf-8")
    (root / "config.json").write_bytes(b"{}")
    (root / "preprocessor_config.json").write_bytes(b"{}")
    original_is_symlink = Path.is_symlink

    def simulated_is_symlink(path: Path) -> bool:
        return path == model_path or original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_is_symlink)

    with pytest.raises(ArtifactBoundaryError, match="symlink|escape"):
        verify_snapshot(spec, root)


def test_receipt_output_symlink_escape_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact_root = tmp_path / "artifacts"
    wave_root = artifact_root / "wave0"
    cache_root = wave_root / "model_cache"
    cache_root.mkdir(parents=True)
    receipts_root = wave_root / "receipts"
    output = receipts_root / "receipt.json"
    outside = tmp_path / "outside"
    outside.mkdir()
    original_resolve = Path.resolve

    def simulated_resolve(path: Path, strict: bool = False) -> Path:
        if path == receipts_root:
            return outside
        if path == output:
            return outside / "receipt.json"
        return original_resolve(path, strict=strict)

    monkeypatch.setattr(Path, "resolve", simulated_resolve)
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))

    with pytest.raises(ArtifactBoundaryError, match="artifact root"):
        _external_roots(cache_root, output)


def test_direct_verify_rejects_caller_forged_spec(tmp_path: Path) -> None:
    repo_id = "attacker/nearby-model"
    revision = "1" * 40
    root = _snapshot_root(tmp_path, repo_id, revision)
    files = {
        "README.md": b"---\nlicense: apache-2.0\n---\n",
        "config.json": b"{}",
        "preprocessor_config.json": b"{}",
        "model.safetensors": b"not-an-approved-model",
    }
    for name, content in files.items():
        (root / name).write_bytes(content)
    forged = PinnedAssetSpec(
        name="rtdetr",
        repo_id=repo_id,
        revision=revision,
        license="apache-2.0",
        license_evidence="README.md",
        files={
            name: FileSpec(len(content), sha256_file(root / name))
            for name, content in files.items()
        },
        transformers_version="5.15.0",
        source_files={},
    )

    with pytest.raises(RevisionMismatch, match="approved contract"):
        verify_snapshot(forged, root)


def test_model_asset_schema_rejects_empty_models(specs, tmp_path: Path) -> None:
    receipt = _valid_model_asset_receipt(specs)
    receipt["normative"]["models"] = {}

    with pytest.raises(ReceiptValidationError, match="rtdetr"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


def test_model_asset_schema_rejects_missing_transformers_source(
    specs, tmp_path: Path
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    files = receipt["normative"]["transformers"]["files"]
    del files["models/dinov2/modeling_dinov2.py"]

    with pytest.raises(ReceiptValidationError, match="modeling_dinov2"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


def test_model_asset_schema_binds_repository_to_model_key(
    specs, tmp_path: Path
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    models = receipt["normative"]["models"]
    models["rtdetr"]["repo_id"] = "facebook/dinov2-small"

    with pytest.raises(ReceiptValidationError, match="repo_id"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


def test_model_asset_schema_resolves_nested_file_reference(
    specs, tmp_path: Path
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    del receipt["normative"]["models"]["rtdetr"]["files"]["README.md"]["sha256"]

    with pytest.raises(ReceiptValidationError, match="sha256"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


@pytest.mark.parametrize(
    ("mutate", "expected_error"),
    [
        (
            lambda receipt: receipt["normative"]["models"]["rtdetr"]["files"][
                "model.safetensors"
            ].update({"size": 1, "sha256": "0" * 64}),
            "rtdetr files do not match the compiled approved pins",
        ),
        (
            lambda receipt: receipt["normative"]["transformers"]["files"][
                "models/rt_detr/modeling_rt_detr.py"
            ].update({"size": 1, "sha256": "0" * 64}),
            "Transformers source files do not match the compiled approved pins",
        ),
        (
            lambda receipt: receipt["normative"]["models"]["rtdetr"][
                "huggingface_metadata"
            ]["files"]["model.safetensors"].update({"etag": "0" * 64}),
            "rtdetr model.safetensors metadata identity differs from its pin",
        ),
    ],
)
def test_model_asset_pass_receipt_rejects_self_consistent_forged_evidence(
    specs, tmp_path: Path, mutate, expected_error: str
) -> None:
    """A rehashed PASS must still bind exact payload/source/HF identities."""
    receipt = _valid_model_asset_receipt(specs)
    mutate(receipt)

    with pytest.raises(ReceiptValidationError, match=expected_error):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


def test_model_asset_pass_receipt_binds_license_and_metadata_inventory(
    specs, tmp_path: Path
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    rtdetr = receipt["normative"]["models"]["rtdetr"]
    rtdetr["license_evidence"]["sha256"] = "0" * 64

    with pytest.raises(ReceiptValidationError, match="license evidence"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)

    receipt = _valid_model_asset_receipt(specs)
    metadata = receipt["normative"]["models"]["rtdetr"]["huggingface_metadata"]
    metadata["inventory"][".cache/huggingface/download/model.safetensors.metadata"][
        "sha256"
    ] = ("0" * 64)

    with pytest.raises(ReceiptValidationError, match="metadata inventory"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


@pytest.mark.parametrize("document_name", ["config", "processor"])
def test_model_asset_pass_receipt_binds_parsed_payload_documents(
    specs, tmp_path: Path, document_name: str
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    receipt["normative"]["models"]["dinov2"][document_name]["forged"] = True

    with pytest.raises(ReceiptValidationError, match=document_name):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


def test_complete_model_asset_evidence_cannot_be_rehashed_as_fail(
    specs, tmp_path: Path
) -> None:
    receipt = _valid_model_asset_receipt(specs)
    receipt["normative"]["status"] = "FAIL"
    receipt["normative"]["invariants"]["all_assets_verified"] = False
    receipt["normative"]["errors"] = ["invented failure"]

    with pytest.raises(ReceiptValidationError, match="FAIL contradicts"):
        atomic_write_receipt(tmp_path / "receipt.json", receipt)


@pytest.mark.parametrize("failure_kind", ["tamper", "revision", "license"])
def test_cli_failure_writes_fail_receipt_and_exits_two(
    specs,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure_kind: str,
) -> None:
    # Keep the HF metadata path below Windows' legacy 260-character limit.
    artifact_root = tmp_path.parent / f"assets-{failure_kind}"
    cache_root = artifact_root / "wave0" / "model_cache"
    revision = RTDETR_REVISION if failure_kind != "revision" else "0" * 40
    root = _snapshot_root(cache_root, "PekingU/rtdetr_r18vd", revision)
    _write_huggingface_metadata(root, specs["rtdetr"])
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
            "--run-id",
            "run-a",
        ]
    )

    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert receipt["normative"]["status"] == "FAIL"
    assert receipt["normative"]["errors"]
    assert receipt["normative"]["invariants"]["all_assets_verified"] is False
    assert "VAL_DATA_ROOT" not in output.read_text(encoding="utf-8")
