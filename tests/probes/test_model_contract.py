from __future__ import annotations

import inspect
import json
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from transformers.models.rt_detr.modeling_rt_detr import RTDetrForObjectDetection

import vision_active_learning_loop.probes.model_contract as model_contract_probe
from vision_active_learning_loop.artifacts.receipts import (
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.models.rtdetr_contract import (
    ContractUnavailable,
    ExecutionDeviceObservation,
    RawDetectorOutput,
    SourceContractObservation,
    evaluate_raw_contract,
    extract_raw_contract,
    foreground_scores,
    inspect_rtdetr_source_contract,
    observe_execution_device,
    reset_four_class_head,
)
from vision_active_learning_loop.probes.model_contract import (
    ModelContractInputError,
    ModelContractReceipt,
    ProcessorContractObservation,
    REQUIRED_MODEL_CONTRACT_INVARIANTS,
    _processor_document,
    _receipt_hashes,
    _resolve_cli_paths,
    main as probe_main,
    run_model_contract_probe,
)
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256


FIXTURE_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "synthetic"
    / "wave0"
    / "fixture-manifest.json"
)


def _outputs(*, queries: int = 300, labels: int = 4, decoder_layers: int = 3):
    logits = torch.linspace(-2, 2, 2 * queries * labels).reshape(2, queries, labels)
    intermediate = torch.linspace(
        0, 1, 2 * decoder_layers * queries * 4
    ).reshape(
        2, decoder_layers, queries, 4
    )
    return SimpleNamespace(
        logits=logits,
        pred_boxes=intermediate[:, -1],
        intermediate_reference_points=intermediate,
    )


def _model(*, queries: int = 300, labels: int = 4, decoder_layers: int = 3):
    return SimpleNamespace(
        config=SimpleNamespace(
            num_queries=queries,
            num_labels=labels,
            decoder_layers=decoder_layers,
        ),
        model=SimpleNamespace(
            decoder=SimpleNamespace(
                class_embed=nn.ModuleList(
                    [nn.Linear(8, labels) for _ in range(decoder_layers)]
                )
            )
        ),
    )


def _approved_source() -> SourceContractObservation:
    return SourceContractObservation(
        invariants={
            "source_stack_axis_one": True,
            "source_no_query_permutation": True,
            "source_final_boxes_last_layer": True,
        }
    )


def test_extract_raw_contract_preserves_decoder_layer_and_query_axes() -> None:
    """Catch using a postprocessed or reordered box tensor."""
    outputs = _outputs()

    raw = extract_raw_contract(outputs)

    assert isinstance(raw, RawDetectorOutput)
    assert torch.equal(raw.logits, outputs.logits)
    assert torch.equal(raw.final_boxes, outputs.intermediate_reference_points[:, -1])
    assert torch.equal(
        raw.penultimate_boxes, outputs.intermediate_reference_points[:, -2]
    )
    assert torch.equal(raw.intermediate_boxes, outputs.intermediate_reference_points)


def test_extract_raw_contract_rejects_unobservable_intermediate_boxes() -> None:
    """Catch silently degrading to final-only boxes when localization is unobservable."""
    outputs = _outputs()
    outputs.intermediate_reference_points = None

    with pytest.raises(ContractUnavailable, match="intermediate_reference_points"):
        extract_raw_contract(outputs)


@pytest.mark.parametrize(
    ("field", "tensor", "expected"),
    [
        ("logits", torch.zeros(2, 300), "logits.*rank 3"),
        ("pred_boxes", torch.zeros(2, 300), "pred_boxes.*rank 3"),
        (
            "intermediate_reference_points",
            torch.zeros(2, 3),
            "intermediate_reference_points.*rank 4",
        ),
        (
            "intermediate_reference_points",
            torch.zeros(1, 3, 300, 4),
            "batch and query dimensions",
        ),
        ("pred_boxes", torch.zeros(2, 300, 5), "last dimension 4"),
        (
            "intermediate_reference_points",
            torch.zeros(2, 3, 300, 5),
            "last dimension 4",
        ),
    ],
    ids=[
        "logits-rank",
        "final-boxes-rank",
        "intermediate-rank",
        "intermediate-batch-mismatch",
        "final-box-width",
        "intermediate-box-width",
    ],
)
def test_extract_raw_contract_rejects_malformed_tensor_shapes(
    field: str, tensor: torch.Tensor, expected: str
) -> None:
    """Catch malformed output ranks or axes leaking an indexing exception."""
    outputs = _outputs()
    setattr(outputs, field, tensor)

    with pytest.raises(ContractUnavailable, match=expected):
        extract_raw_contract(outputs)


def test_reset_four_class_head_is_seeded_and_reuses_no_coco_rows() -> None:
    """Catch retaining pretrained COCO head rows or nondeterministic reset weights."""
    first = _model(labels=80)
    second = _model(labels=80)
    for head in first.model.decoder.class_embed:
        nn.init.constant_(head.weight, 7.0)
    for head in second.model.decoder.class_embed:
        nn.init.constant_(head.weight, -9.0)

    reset_four_class_head(first)
    reset_four_class_head(second)

    assert first.config.num_labels == 4
    assert first.config.id2label == {0: "D00", 1: "D10", 2: "D20", 3: "D40"}
    assert [head.out_features for head in first.model.decoder.class_embed] == [4, 4, 4]
    for first_head, second_head in zip(
        first.model.decoder.class_embed, second.model.decoder.class_embed
    ):
        assert torch.equal(first_head.weight, second_head.weight)
        assert not torch.all(first_head.weight == 7.0)


def test_observed_rtdetr_contract() -> None:
    """Catch drift from the pinned two-image, 300-query, four-class contract."""
    model = _model()
    raw = extract_raw_contract(_outputs())

    receipt = evaluate_raw_contract(
        model, raw, foreground_scores(raw), _approved_source()
    )

    assert receipt.config_num_queries == 300
    assert receipt.config_num_labels == 4
    assert receipt.shapes["logits"] == [2, 300, 4]
    assert receipt.shapes["pred_boxes"] == [2, 300, 4]
    assert receipt.shapes["intermediate_reference_points"] == [
        2,
        receipt.decoder_layers,
        300,
        4,
    ]
    assert receipt.invariants["native_fifth_logit_absent"] is True
    assert receipt.status == "PASS"


def test_four_decoder_layers_fail_the_exact_effective_contract() -> None:
    """Catch accepting a shape-consistent decoder-depth drift from the pinned model."""
    raw = extract_raw_contract(_outputs(decoder_layers=4))

    observation = evaluate_raw_contract(
        _model(decoder_layers=4), raw, foreground_scores(raw), _approved_source()
    )

    assert observation.status == "FAIL"
    assert observation.invariants["config_decoder_layers_3"] is False


@pytest.mark.parametrize(
    ("model", "outputs", "score_kind", "source", "failed_invariant"),
    [
        (
            _model(),
            _outputs(labels=5),
            "sigmoid",
            _approved_source(),
            "native_fifth_logit_absent",
        ),
        (
            _model(),
            _outputs(queries=299),
            "sigmoid",
            _approved_source(),
            "logits_shape",
        ),
        (
            _model(),
            _outputs(),
            "sigmoid",
            SourceContractObservation(
                invariants={
                    "source_stack_axis_one": True,
                    "source_no_query_permutation": False,
                    "source_final_boxes_last_layer": True,
                }
            ),
            "source_no_query_permutation",
        ),
        (
            _model(),
            _outputs(),
            "softmax",
            _approved_source(),
            "foreground_scores_are_sigmoid",
        ),
    ],
    ids=["fifth-logit", "299-queries", "permuted-intermediate", "softmax-path"],
)
def test_adversarial_raw_contracts_fail_closed(
    model, outputs, score_kind: str, source, failed_invariant: str
) -> None:
    """Catch publishing PASS after a normative raw-output invariant breaks."""
    raw = extract_raw_contract(outputs)
    scores = (
        torch.sigmoid(raw.logits)
        if score_kind == "sigmoid"
        else torch.softmax(raw.logits, dim=-1)
    )

    observation = evaluate_raw_contract(model, raw, scores, source)

    assert observation.status == "FAIL"
    assert observation.invariants[failed_invariant] is False


def test_pinned_transformers_source_proves_query_correspondence() -> None:
    """Catch source drift that changes decoder-layer or query-axis semantics."""
    source_path = Path(inspect.getfile(RTDetrForObjectDetection))

    observation = inspect_rtdetr_source_contract(source_path)

    assert all(observation.invariants.values())


def test_source_inspection_rejects_query_axis_permutation(tmp_path: Path) -> None:
    """Catch an intermediate tensor permutation hidden behind the same shape."""
    source_path = tmp_path / "modeling_rt_detr.py"
    source_path.write_text(
        """
class RTDetrDecoder:
    def forward(self):
        intermediate_reference_points = ()
        intermediate_reference_points = torch.stack(
            intermediate_reference_points, dim=1
        ).permute(0, 2, 1, 3)

class RTDetrForObjectDetection:
    def forward(self, outputs):
        outputs_coord = outputs.intermediate_reference_points
        pred_boxes = outputs_coord[:, -1]
""".lstrip(),
        encoding="utf-8",
    )

    observation = inspect_rtdetr_source_contract(source_path)

    assert observation.invariants["source_no_query_permutation"] is False


def _receipt(*, processor_passed: bool = True) -> ModelContractReceipt:
    source_files = {
        "models/rt_detr/configuration_rt_detr.py": {
            "size": 9028,
            "sha256": "22c1b65c1385d35534658cbf1e91afa7174737134cb6a14ffdaffcd7b7a161a6",
        },
        "models/rt_detr/configuration_rt_detr_resnet.py": {
            "size": 3538,
            "sha256": "52a9a3ca8dd648f04bcb5f61b30ab927ca3f15187748736f7714f48af1f1ae73",
        },
        "models/rt_detr/image_processing_rt_detr.py": {
            "size": 24476,
            "sha256": "47ae2f0ca25a2763f4f42b27e8a2760bcbb0c2ef07d0f1e97aa779f9219fc558",
        },
        "models/rt_detr/modeling_rt_detr.py": {
            "size": 86564,
            "sha256": "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3",
        },
        "models/rt_detr/modeling_rt_detr_resnet.py": {
            "size": 15986,
            "sha256": "fc13ccc6ba1e57862e4c129c9e74bb97f091012186c1104974b92d5ec7b4019c",
        },
    }
    processor = {
        "size": {"max_height": 640, "max_width": 640},
        "resample": 2,
        "do_pad": True,
        "pad_size": {"height": 640, "width": 640},
        "do_rescale": True,
        "rescale_factor": 1 / 255,
        "do_normalize": False,
    }
    config = {
        "num_queries": 300,
        "num_labels": 4,
        "decoder_layers": 3,
        "id2label": {"0": "D00", "1": "D10", "2": "D20", "3": "D40"},
        "label2id": {"D00": 0, "D10": 1, "D20": 2, "D40": 3},
    }
    environment = {
        "schema_version": 1,
        "python": "3.12.11",
        "uv": "0.8.15",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
        "cuda_runtime": "12.6",
        "os": "Linux",
        "wsl": True,
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
        "driver": "591.86",
        "container_image_digest": "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356",
        "runtime_image_digest": "sha256:7ba1dd9364de4bdfc60ee14c42f3441d736e46fcd41128992c3cd49c67059ae2",
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
        "status": "PASS",
        "errors": [],
        "torch_execution": {
            "cuda_available": True,
            "device_count": 1,
            "selected_index": 0,
            "selected_name": "NVIDIA GeForce RTX 4090",
            "torch_selected_gpu_uuid": "11111111-1111-1111-1111-111111111111",
            "selected_device": "cuda:0",
            "nvidia_smi_gpu_name": "NVIDIA GeForce RTX 4090",
            "nvidia_smi_gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
            "model_device": "cuda:0",
            "pixel_values_device": "cuda:0",
            "pixel_mask_device": "cuda:0",
            "logits_device": "cuda:0",
            "final_boxes_device": "cuda:0",
            "penultimate_boxes_device": "cuda:0",
            "intermediate_boxes_device": "cuda:0",
        },
    }
    hashes = {
        "model_sha256": "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
        "config_sha256": canonical_json_sha256(config),
        "config_file_sha256": "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
        "source_sha256": canonical_json_sha256(source_files),
        "processor_sha256": canonical_json_sha256(processor),
        "processor_file_sha256": "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
        "fixture_sha256": "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f",
        "probe_sha256": "640d7aceb71aa67db5d16709e1cc0db8de78735407ca47c0b1ed43dd0624cec4",
        "environment_sha256": canonical_json_sha256(environment),
    }
    return ModelContractReceipt(
        model_repository="PekingU/rtdetr_r18vd",
        model_revision="cc5b50f32f0100caaa3bd275343e2fb17762c73d",
        transformers_version="5.15.0",
        hashes=hashes,
        source_files=source_files,
        config_num_queries=300,
        config_num_labels=4,
        decoder_layers=3,
        processor=processor,
        shapes={
            "logits": [2, 300, 4],
            "pred_boxes": [2, 300, 4],
            "intermediate_reference_points": [2, 3, 300, 4],
            "pixel_values": [2, 3, 640, 640],
            "pixel_mask": [2, 640, 640],
        },
        invariants={
            name: (
                processor_passed
                if name == "expected_valid_mask_rectangles"
                else True
            )
            for name in REQUIRED_MODEL_CONTRACT_INVARIANTS
        },
        environment=environment,
        errors=() if processor_passed else ("expected_valid_mask_rectangles",),
        timestamp="2026-08-24T00:00:00+00:00",
    )


def test_model_contract_receipt_is_schema_valid_and_content_addressed(
    tmp_path: Path,
) -> None:
    """Catch omitting identity, source, processor, shape, or environment evidence."""
    receipt = _receipt()
    output = tmp_path / "model-contract.json"

    atomic_write_receipt(output, receipt.as_dict())
    stored = __import__("json").loads(output.read_text(encoding="utf-8"))
    validate_receipt(
        stored,
        Path(__file__).resolve().parents[2]
        / "schemas"
        / "model-contract-receipt.schema.json",
    )

    assert stored["normative"]["model"]["repository"] == "PekingU/rtdetr_r18vd"
    assert stored["normative"]["config"]["num_queries"] == 300
    assert stored["normative"]["source_files"]
    assert stored["normative"]["processor"]["do_normalize"] is False
    assert stored["normative"]["environment"]["gpu_name"] == (
        "NVIDIA GeForce RTX 4090"
    )
    assert stored["normative"]["status"] == "PASS"


@pytest.mark.parametrize(
    "field",
    [
        "model",
        "transformers_version",
        "source_files",
        "config",
        "processor",
        "environment",
        "config_file_sha256",
        "processor_file_sha256",
    ],
)
def test_model_contract_schema_rejects_missing_normative_evidence(
    tmp_path: Path, field: str
) -> None:
    """Catch a schema that permits PASS without complete identity evidence."""
    document = _receipt().as_dict()
    del document["normative"][field]

    with pytest.raises(Exception):
        atomic_write_receipt(tmp_path / "model-contract.json", document)


def test_model_contract_schema_requires_every_normative_invariant(
    tmp_path: Path,
) -> None:
    """Catch deleting a required proof while retaining a PASS receipt."""
    document = _receipt().as_dict()
    del document["normative"]["invariants"]["source_stack_axis_one"]

    with pytest.raises(Exception):
        atomic_write_receipt(tmp_path / "model-contract.json", document)


def test_receipt_hashes_distinguish_raw_files_from_effective_documents(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch labeling raw upstream bytes as the effective config/processor hash."""
    fixture = tmp_path / "fixture.json"
    fixture.write_text("{}\n", encoding="utf-8")
    asset_model = {
        "files": {
            "model.safetensors": {"sha256": "a" * 64},
            "config.json": {"sha256": "b" * 64},
            "preprocessor_config.json": {"sha256": "c" * 64},
        }
    }
    config = {
        "num_queries": 300,
        "num_labels": 4,
        "decoder_layers": 3,
        "id2label": {"0": "D00", "1": "D10", "2": "D20", "3": "D40"},
        "label2id": {"D00": 0, "D10": 1, "D20": 2, "D40": 3},
    }
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.model_contract._probe_hash",
        lambda: "d" * 64,
    )

    hashes = _receipt_hashes(
        asset_model,
        {},
        fixture,
        {"status": "PASS"},
        config,
        _processor_document(),
    )

    assert hashes["config_file_sha256"] == "b" * 64
    assert hashes["config_sha256"] == canonical_json_sha256(config)
    assert hashes["processor_file_sha256"] == "c" * 64
    assert hashes["processor_sha256"] == canonical_json_sha256(
        _processor_document()
    )


def test_fixture_digest_is_canonical_across_line_endings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch Git EOL conversion changing semantically identical fixture evidence."""
    manifest = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    lf = tmp_path / "fixture-lf.json"
    crlf = tmp_path / "fixture-crlf.json"
    rendered = json.dumps(manifest, indent=2)
    lf.write_bytes((rendered + "\n").encode())
    crlf.write_bytes((rendered.replace("\n", "\r\n") + "\r\n").encode())
    asset_model = {
        "files": {
            "model.safetensors": {"sha256": "a" * 64},
            "config.json": {"sha256": "b" * 64},
            "preprocessor_config.json": {"sha256": "c" * 64},
        }
    }
    config = {
        "num_queries": 300,
        "num_labels": 4,
        "decoder_layers": 3,
    }
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.model_contract._probe_hash",
        lambda: "d" * 64,
    )

    lf_hash = _receipt_hashes(
        asset_model, {}, lf, {"status": "PASS"}, config, _processor_document()
    )["fixture_sha256"]
    crlf_hash = _receipt_hashes(
        asset_model, {}, crlf, {"status": "PASS"}, config, _processor_document()
    )["fixture_sha256"]

    assert lf_hash == crlf_hash == canonical_json_sha256(manifest)


def test_probe_source_digest_is_canonical_across_line_endings(tmp_path: Path) -> None:
    """Catch checkout EOL conversion changing the approved implementation identity."""
    lf = tmp_path / "probe-lf.py"
    crlf = tmp_path / "probe-crlf.py"
    lf.write_bytes(b"def probe():\n    return 1\n")
    crlf.write_bytes(b"def probe():\r\n    return 1\r\n")

    assert model_contract_probe._canonical_source_sha256(
        lf
    ) == model_contract_probe._canonical_source_sha256(crlf)


def test_cpu_execution_device_observation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch a CPU-only raw observation being publishable as the GPU contract."""
    model = nn.Linear(4, 4)
    raw = extract_raw_contract(_outputs())
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    observation = observe_execution_device(
        model,
        torch.zeros(2, 3, 640, 640),
        torch.ones(2, 640, 640, dtype=torch.int64),
        raw,
        expected_gpu_name="NVIDIA GeForce RTX 4090",
    )

    assert isinstance(observation, ExecutionDeviceObservation)
    assert not all(observation.invariants.values())
    assert observation.invariants["torch_cuda_available"] is False
    assert observation.invariants["model_on_selected_cuda_device"] is False


def test_selected_torch_gpu_identity_is_bound_to_nvidia_smi_uuid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch recording a GPU name without binding the selected index and UUID."""
    model = nn.Linear(4, 4)
    raw = extract_raw_contract(_outputs())
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "device_count", lambda: 1)
    monkeypatch.setattr(torch.cuda, "current_device", lambda: 0)
    monkeypatch.setattr(
        torch.cuda,
        "get_device_name",
        lambda index: "NVIDIA GeForce RTX 4090",
    )
    monkeypatch.setattr(
        torch.cuda,
        "get_device_properties",
        lambda index: SimpleNamespace(
            uuid="11111111-1111-1111-1111-111111111111"
        ),
    )

    observation = observe_execution_device(
        model,
        torch.zeros(1),
        torch.zeros(1),
        raw,
        expected_gpu_name="NVIDIA GeForce RTX 4090",
        nvidia_smi_gpu_name="NVIDIA GeForce RTX 4090",
        nvidia_smi_gpu_uuid="GPU-11111111-1111-1111-1111-111111111111",
    )

    assert observation.invariants["torch_selected_gpu_is_canonical"] is True
    assert observation.environment["torch_selected_gpu_uuid"] == (
        "11111111-1111-1111-1111-111111111111"
    )
    assert observation.environment["nvidia_smi_gpu_uuid"] == (
        "GPU-11111111-1111-1111-1111-111111111111"
    )

    mismatched = observe_execution_device(
        model,
        torch.zeros(1),
        torch.zeros(1),
        raw,
        expected_gpu_name="NVIDIA GeForce RTX 4090",
        nvidia_smi_gpu_name="NVIDIA GeForce RTX 4090",
        nvidia_smi_gpu_uuid="GPU-other",
    )
    assert mismatched.invariants["torch_selected_gpu_is_canonical"] is False


def test_probe_rejects_linked_wave0_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch a linked parent redirecting receipts outside the artifact root."""
    wave_root = tmp_path / "wave0"
    receipts_root = wave_root / "receipts"
    receipts_root.mkdir(parents=True)
    assets = receipts_root / "model-assets.json"
    assets.write_text("{}\n", encoding="utf-8")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.model_contract._is_link_or_junction",
        lambda path: Path(path) == wave_root,
    )

    with pytest.raises(ModelContractInputError, match="link"):
        _resolve_cli_paths(
            assets,
            FIXTURE_MANIFEST,
            receipts_root / "model-contract-receipt.json",
        )


def test_failed_contract_receipt_has_no_wave0_pass_marker() -> None:
    """Catch a false processor invariant leaving any success marker behind."""
    document = _receipt(processor_passed=False).as_dict()

    assert document["normative"]["status"] == "FAIL"
    assert "wave0_pass_marker" not in document
    assert "wave0_pass_marker" not in document["normative"]


def test_unobservable_raw_shapes_can_be_published_only_as_fail(
    tmp_path: Path,
) -> None:
    """Catch schema completeness preventing a fail-closed diagnostic receipt."""
    base = _receipt(processor_passed=False)
    receipt = replace(
        base,
        shapes={
            "pixel_values": [2, 3, 640, 640],
            "pixel_mask": [2, 640, 640],
        },
        invariants={
            **base.invariants,
            "logits_shape": False,
            "pred_boxes_shape": False,
            "intermediate_reference_points_shape": False,
            "native_fifth_logit_absent": False,
        },
    )
    output = tmp_path / "model-contract.json"

    atomic_write_receipt(output, receipt.as_dict())

    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "FAIL"
    assert stored["normative"]["observed_shapes"]["logits"] == []


def test_probe_publishes_complete_fail_receipt_for_malformed_intermediate_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch an IndexError escaping instead of producing fail-closed evidence."""
    source_files = dict(_receipt().source_files)
    asset_model = {
        "repo_id": "PekingU/rtdetr_r18vd",
        "revision": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
        "config": {"num_queries": 300, "decoder_layers": 3},
        "files": {
            "model.safetensors": {
                "sha256": "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093"
            },
            "config.json": {
                "sha256": "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2"
            },
            "preprocessor_config.json": {
                "sha256": "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a"
            },
        },
    }
    asset_receipt = {
        "normative": {
            "status": "PASS",
            "models": {"rtdetr": asset_model},
            "transformers": {"version": "5.15.0", "files": source_files},
        }
    }
    spec = SimpleNamespace(
        repo_id="PekingU/rtdetr_r18vd",
        revision="cc5b50f32f0100caaa3bd275343e2fb17762c73d",
        transformers_version="5.15.0",
    )

    class TransferToken:
        def to(self, device):
            return self

    class MalformedModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.config = SimpleNamespace(
                num_queries=300,
                num_labels=80,
                decoder_layers=3,
                id2label={},
                label2id={},
            )
            self.model = nn.Module()
            self.model.decoder = nn.Module()
            self.model.decoder.class_embed = nn.ModuleList(
                [nn.Linear(8, 80) for _ in range(3)]
            )

        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            return cls()

        def to(self, device):
            return self

        def forward(self, **kwargs):
            return SimpleNamespace(
                logits=torch.zeros(2, 300, 4),
                pred_boxes=torch.zeros(2, 300, 4),
                intermediate_reference_points=torch.zeros(2, 3),
            )

    processor_invariants = {
        name: True
        for name in (
            "aspect_preserving_size",
            "bilinear_resize",
            "bottom_right_padding_is_zero",
            "expected_valid_mask_rectangles",
            "labels_absent",
            "normalization_disabled",
            "padding_enabled",
            "pixel_mask_shape",
            "pixel_values_shape",
            "rescale_one_over_255",
            "rescale_without_normalization_observed",
        )
    }
    environment = dict(_receipt().environment)
    environment.pop("torch_execution")
    monkeypatch.setattr(model_contract_probe, "validate_receipt", lambda *args: None)
    monkeypatch.setattr(model_contract_probe, "_artifact_root", lambda: tmp_path)
    monkeypatch.setattr(model_contract_probe, "_snapshot_root", lambda *args: tmp_path)
    monkeypatch.setattr(
        model_contract_probe,
        "verify_snapshot",
        lambda *args: SimpleNamespace(as_dict=lambda: asset_model),
    )
    monkeypatch.setattr(
        model_contract_probe, "verify_transformers_source", lambda *args: {}
    )
    monkeypatch.setattr(
        model_contract_probe, "_source_document", lambda observations: source_files
    )
    monkeypatch.setattr(
        model_contract_probe, "_load_fixture_images", lambda path: ({}, [])
    )
    monkeypatch.setattr(model_contract_probe, "build_contract_processor", object)
    monkeypatch.setattr(
        model_contract_probe,
        "prepare_contract_batch",
        lambda processor, images: {
            "pixel_values": TransferToken(),
            "pixel_mask": TransferToken(),
        },
    )
    monkeypatch.setattr(
        model_contract_probe,
        "observe_processor_contract",
        lambda processor, batch: ProcessorContractObservation(
            shapes={
                "pixel_values": [2, 3, 640, 640],
                "pixel_mask": [2, 640, 640],
            },
            invariants=processor_invariants,
        ),
    )
    monkeypatch.setattr(
        model_contract_probe, "_runtime_environment", lambda: (environment, [])
    )
    monkeypatch.setattr(
        model_contract_probe,
        "inspect_rtdetr_source_contract",
        lambda path: _approved_source(),
    )
    monkeypatch.setattr(model_contract_probe, "RTDetrForObjectDetection", MalformedModel)
    monkeypatch.setattr(torch.cuda, "current_device", lambda: 0)

    receipt = run_model_contract_probe(spec, asset_receipt, FIXTURE_MANIFEST)
    output = tmp_path / "model-contract.json"
    atomic_write_receipt(output, receipt.as_dict())

    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "FAIL"
    assert stored["normative"]["observed_shapes"]["logits"] == []
    assert any(
        "intermediate_reference_points" in error
        for error in stored["normative"]["errors"]
    )


def test_cli_manifest_discovers_model_contract_probe() -> None:
    """Catch omitting the required lazy ``val probe model-contract`` command."""
    source_root = Path(__file__).resolve().parents[2] / "src"

    manifest = build_manifest(source_root)

    assert manifest["probe model-contract"] == (
        "vision_active_learning_loop.probes.model_contract:main"
    )


def test_probe_rejects_failed_asset_receipt_before_model_execution() -> None:
    """Catch executing a model whose prerequisite asset receipt did not pass."""
    failed_assets = {"normative": {"status": "FAIL"}}

    with pytest.raises(ModelContractInputError, match="PASS"):
        run_model_contract_probe(None, failed_assets, FIXTURE_MANIFEST)


def test_probe_cli_requires_external_artifact_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch writing probe evidence without the declared external boundary."""
    monkeypatch.delenv("VAL_ARTIFACT_ROOT", raising=False)

    exit_code = probe_main(
        [
            "--assets",
            "model-assets.json",
            "--fixtures",
            str(FIXTURE_MANIFEST),
            "--output",
            "model-contract.json",
        ]
    )

    assert exit_code == 2
