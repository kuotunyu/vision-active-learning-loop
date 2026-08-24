from __future__ import annotations

import inspect
import json
import math
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from transformers.loss.loss_rt_detr import RTDetrForObjectDetectionLoss
from transformers.models.rt_detr.modeling_rt_detr import RTDetrForObjectDetection

import vision_active_learning_loop.artifacts.receipts as receipt_module
import vision_active_learning_loop.models.rtdetr_contract as rtdetr_contract_module
import vision_active_learning_loop.probes.model_contract as model_contract_probe
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.environment import (
    EnvironmentContract,
    environment_invariants,
)
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
    REQUIRED_MODEL_CONTRACT_INVARIANTS,
    REQUIRED_MODEL_CONTRACT_SHAPES,
    ModelContractInputError,
    ModelContractReceipt,
    ProcessorContractObservation,
    _processor_document,
    _receipt_hashes,
    _resolve_cli_paths,
    run_model_contract_probe,
)
from vision_active_learning_loop.probes.model_contract import (
    main as probe_main,
)

FIXTURE_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "synthetic"
    / "wave0"
    / "fixture-manifest.json"
)


def _outputs(*, queries: int = 300, labels: int = 4, decoder_layers: int = 3):
    logits = torch.linspace(-2, 2, 2 * queries * labels).reshape(2, queries, labels)
    intermediate_logits = torch.linspace(
        -3,
        3,
        2 * decoder_layers * queries * labels,
    ).reshape(2, decoder_layers, queries, labels)
    enc_outputs_class = torch.linspace(-1, 1, 2 * 400 * labels).reshape(2, 400, labels)
    enc_topk_logits = torch.linspace(-1, 1, 2 * queries * labels).reshape(
        2, queries, labels
    )
    intermediate = torch.linspace(0, 1, 2 * decoder_layers * queries * 4).reshape(
        2, decoder_layers, queries, 4
    )
    return SimpleNamespace(
        logits=logits,
        intermediate_logits=intermediate_logits,
        enc_outputs_class=enc_outputs_class,
        enc_topk_logits=enc_topk_logits,
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


def _model_with_class_components(
    *,
    labels: int = 80,
    decoder_layers: int = 3,
    decoder_bias: bool = True,
    encoder_bias: bool = True,
    dtype: torch.dtype = torch.float32,
) -> SimpleNamespace:
    return SimpleNamespace(
        config=SimpleNamespace(
            num_queries=300,
            num_labels=labels,
            decoder_layers=decoder_layers,
            initializer_bias_prior_prob=None,
        ),
        model=SimpleNamespace(
            decoder=SimpleNamespace(
                class_embed=nn.ModuleList(
                    [
                        nn.Linear(8, labels, bias=decoder_bias, dtype=dtype)
                        for _ in range(decoder_layers)
                    ]
                )
            ),
            denoising_class_embed=nn.Embedding(
                labels + 1,
                16,
                padding_idx=labels,
                dtype=dtype,
            ),
            enc_score_head=nn.Linear(
                256,
                labels,
                bias=encoder_bias,
                dtype=dtype,
            ),
        ),
    )


def _reference_replacements_in_approved_order(
    model: SimpleNamespace, seed: int
) -> dict[str, torch.Tensor]:
    """Build an independent oracle for the normative replacement RNG stream."""
    old_heads = list(model.model.decoder.class_embed)
    denoising = model.model.denoising_class_embed
    encoder = model.model.enc_score_head
    cuda_devices = sorted(
        {
            tensor.device.index
            for tensor in [
                *(head.weight for head in old_heads),
                denoising.weight,
                encoder.weight,
            ]
            if tensor.device.type == "cuda" and tensor.device.index is not None
        }
    )
    expected: dict[str, torch.Tensor] = {}
    with torch.random.fork_rng(devices=cuda_devices):
        torch.manual_seed(seed)
        if cuda_devices:
            torch.cuda.manual_seed_all(seed)
        prior_probability = model.config.initializer_bias_prior_prob or 1 / 5
        for index, old_head in enumerate(old_heads):
            replacement = nn.Linear(
                old_head.in_features,
                4,
                bias=old_head.bias is not None,
                device=old_head.weight.device,
                dtype=old_head.weight.dtype,
            )
            nn.init.xavier_uniform_(replacement.weight)
            if replacement.bias is not None:
                nn.init.constant_(
                    replacement.bias,
                    -math.log((1 - prior_probability) / prior_probability),
                )
            expected[f"decoder.{index}.weight"] = replacement.weight.detach().clone()
            if replacement.bias is not None:
                expected[f"decoder.{index}.bias"] = replacement.bias.detach().clone()

        replacement_embedding = nn.Embedding(
            5,
            denoising.embedding_dim,
            padding_idx=4,
            device=denoising.weight.device,
            dtype=denoising.weight.dtype,
        )
        nn.init.xavier_uniform_(replacement_embedding.weight)
        with torch.no_grad():
            replacement_embedding.weight[4].zero_()
        expected["denoising.weight"] = replacement_embedding.weight.detach().clone()

        replacement_encoder = nn.Linear(
            encoder.in_features,
            4,
            bias=encoder.bias is not None,
            device=encoder.weight.device,
            dtype=encoder.weight.dtype,
        )
        nn.init.xavier_uniform_(replacement_encoder.weight)
        if replacement_encoder.bias is not None:
            nn.init.constant_(
                replacement_encoder.bias,
                -math.log((1 - prior_probability) / prior_probability),
            )
        expected["encoder.weight"] = replacement_encoder.weight.detach().clone()
        if replacement_encoder.bias is not None:
            expected["encoder.bias"] = replacement_encoder.bias.detach().clone()
    return expected


def _replacement_tensors(model: SimpleNamespace) -> dict[str, torch.Tensor]:
    tensors: dict[str, torch.Tensor] = {}
    for index, head in enumerate(model.model.decoder.class_embed):
        tensors[f"decoder.{index}.weight"] = head.weight.detach()
        if head.bias is not None:
            tensors[f"decoder.{index}.bias"] = head.bias.detach()
    tensors["denoising.weight"] = model.model.denoising_class_embed.weight.detach()
    tensors["encoder.weight"] = model.model.enc_score_head.weight.detach()
    if model.model.enc_score_head.bias is not None:
        tensors["encoder.bias"] = model.model.enc_score_head.bias.detach()
    return tensors


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
    assert torch.equal(raw.intermediate_logits, outputs.intermediate_logits)
    assert torch.equal(raw.enc_outputs_class, outputs.enc_outputs_class)
    assert torch.equal(raw.enc_topk_logits, outputs.enc_topk_logits)
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
    "field",
    ["intermediate_logits", "enc_outputs_class", "enc_topk_logits"],
)
def test_extract_raw_contract_rejects_missing_classification_tensor(field: str) -> None:
    """Catch a reachable label-free classification tensor becoming unobservable."""
    outputs = _outputs()
    setattr(outputs, field, None)

    with pytest.raises(ContractUnavailable, match=field):
        extract_raw_contract(outputs)


@pytest.mark.parametrize(
    ("field", "width"),
    [
        (field, width)
        for field in ("intermediate_logits", "enc_outputs_class", "enc_topk_logits")
        for width in (80, 5, 3, 1)
    ],
)
def test_label_free_non_four_class_tensor_fails_contract(
    field: str, width: int
) -> None:
    """Catch an encoder or intermediate tensor escaping four-class validation."""
    outputs = _outputs()
    if field == "intermediate_logits":
        setattr(outputs, field, torch.zeros(2, 3, 300, width))
    elif field == "enc_outputs_class":
        setattr(outputs, field, torch.zeros(2, 400, width))
    else:
        setattr(outputs, field, torch.zeros(2, 300, width))

    raw = extract_raw_contract(outputs)
    observation = evaluate_raw_contract(
        _model(), raw, foreground_scores(raw), _approved_source()
    )

    assert observation.status == "FAIL"
    assert observation.invariants[f"{field}_four_channels"] is False


def _labeled_observation_inputs(
    *,
    decoder_aux_width: int = 4,
    encoder_aux_width: int = 4,
    outputs_class_width: int = 4,
    loss: torch.Tensor | None = None,
    denoising_meta_values: dict[str, object] | None = None,
):
    if loss is None:
        loss = torch.tensor(1.25)
    if denoising_meta_values is None:
        denoising_meta_values = {"dn_num_split": [10, 300], "dn_num_group": 1}
    auxiliary_outputs = [
        {"logits": torch.zeros(2, 300, decoder_aux_width)},
        {"logits": torch.zeros(2, 300, decoder_aux_width)},
        {"logits": torch.zeros(2, 300, encoder_aux_width)},
    ]
    capture = rtdetr_contract_module.LabeledLossCapture(
        logits=torch.zeros(2, 310, outputs_class_width),
        outputs_class=torch.zeros(2, 3, 310, outputs_class_width),
        enc_topk_logits=torch.zeros(2, 300, encoder_aux_width),
        denoising_meta_values=denoising_meta_values,
        auxiliary_outputs=auxiliary_outputs,
    )
    outputs = SimpleNamespace(
        loss=loss,
        logits=torch.zeros(2, 310, 4),
        intermediate_logits=torch.zeros(2, 3, 310, 4),
        enc_outputs_class=torch.zeros(2, 400, 4),
        enc_topk_logits=torch.zeros(2, 300, 4),
    )
    return outputs, capture


def test_labeled_contract_observes_every_loss_reachable_auxiliary() -> None:
    """Catch omitting decoder, encoder, or denoising logits from the contract."""
    outputs, capture = _labeled_observation_inputs()

    observation = rtdetr_contract_module.observe_labeled_contract(
        object(), outputs, capture
    )

    assert observation.loss_shape == []
    assert observation.logits_shape == [2, 310, 4]
    assert observation.intermediate_logits_shape == [2, 3, 310, 4]
    assert observation.enc_outputs_class_shape == [2, 400, 4]
    assert observation.enc_topk_logits_shape == [2, 300, 4]
    assert observation.decoder_auxiliary_shapes == [[2, 300, 4], [2, 300, 4]]
    assert observation.encoder_auxiliary_shapes == [[2, 300, 4]]
    assert observation.denoising_auxiliary_shapes == [
        [2, 10, 4],
        [2, 10, 4],
        [2, 10, 4],
    ]
    assert all(observation.invariants.values())


@pytest.mark.parametrize(
    ("attack", "kwargs"),
    [
        ("decoder", {"decoder_aux_width": 80}),
        ("encoder", {"encoder_aux_width": 80}),
        ("denoising", {"outputs_class_width": 80}),
    ],
)
def test_labeled_reachable_non_four_class_auxiliary_fails(
    attack: str, kwargs: dict[str, int]
) -> None:
    """Catch an 80-class tensor on any official auxiliary-loss branch."""
    outputs, capture = _labeled_observation_inputs(**kwargs)

    observation = rtdetr_contract_module.observe_labeled_contract(
        object(), outputs, capture
    )

    assert observation.invariants["no_reachable_non_four_class_logits"] is False
    assert observation.invariants[f"{attack}_auxiliary_logits_four_channels"] is False


@pytest.mark.parametrize(
    "loss",
    [torch.tensor([1.0]), torch.tensor(float("nan")), torch.tensor(float("inf"))],
    ids=["vector", "nan", "inf"],
)
def test_labeled_loss_must_be_finite_scalar(loss: torch.Tensor) -> None:
    """Catch accepting a vector or non-finite labeled loss."""
    outputs, capture = _labeled_observation_inputs(loss=loss)

    observation = rtdetr_contract_module.observe_labeled_contract(
        object(), outputs, capture
    )

    assert observation.invariants["labeled_forward_finite_scalar_loss"] is False
    assert observation.invariants["no_reachable_non_four_class_logits"] is True


def test_labeled_contract_requires_denoising_metadata() -> None:
    """Catch silently skipping the approved denoising loss branch."""
    outputs, capture = _labeled_observation_inputs(denoising_meta_values={})

    with pytest.raises(ContractUnavailable, match="dn_num_split"):
        rtdetr_contract_module.observe_labeled_contract(object(), outputs, capture)


def test_labeled_forward_capture_calls_and_restores_official_loss() -> None:
    """Catch replacing the official loss or leaving its wrapper installed."""
    calls: list[tuple[object, ...]] = []

    def official_loss(
        logits,
        labels,
        device,
        pred_boxes,
        config,
        outputs_class=None,
        outputs_coord=None,
        enc_topk_logits=None,
        enc_topk_bboxes=None,
        denoising_meta_values=None,
        **kwargs,
    ):
        calls.append((logits, labels, outputs_class, enc_topk_logits))
        auxiliary = [
            {"logits": torch.zeros(2, 300, 4)},
            {"logits": torch.zeros(2, 300, 4)},
            {"logits": enc_topk_logits},
        ]
        return torch.tensor(2.0), {"loss": torch.tensor(2.0)}, auxiliary

    class FakeModel:
        def __init__(self) -> None:
            self.loss_function = official_loss

        def __call__(self, *, pixel_values, pixel_mask, labels):
            outputs_class = torch.zeros(2, 3, 310, 4)
            logits = outputs_class[:, -1]
            enc_topk_logits = torch.zeros(2, 300, 4)
            loss, _, auxiliary = self.loss_function(
                logits,
                labels,
                torch.device("cpu"),
                torch.zeros(2, 310, 4),
                object(),
                outputs_class,
                torch.zeros(2, 3, 310, 4),
                enc_topk_logits=enc_topk_logits,
                enc_topk_bboxes=torch.zeros(2, 300, 4),
                denoising_meta_values={"dn_num_split": [10, 300]},
            )
            return SimpleNamespace(loss=loss, auxiliary_outputs=auxiliary)

    model = FakeModel()
    labels = [{"class_labels": torch.tensor([0]), "boxes": torch.zeros(1, 4)}]

    _, capture = rtdetr_contract_module.run_labeled_contract_forward(
        model,
        pixel_values=torch.zeros(2, 3, 8, 8),
        pixel_mask=torch.ones(2, 8, 8),
        labels=labels,
    )

    assert len(calls) == 1
    assert calls[0][1] is labels
    assert model.loss_function is official_loss
    assert capture.outputs_class.shape == (2, 3, 310, 4)


def test_pinned_loss_source_proves_all_auxiliary_data_flow() -> None:
    """Catch source drift invalidating the labeled auxiliary observation model."""
    source_path = Path(inspect.getfile(RTDetrForObjectDetectionLoss))

    observation = rtdetr_contract_module.inspect_rtdetr_loss_source_contract(
        source_path
    )

    assert observation.invariants == {
        "loss_splits_outputs_class_dim_2": True,
        "loss_builds_decoder_auxiliaries": True,
        "loss_appends_enc_topk_logits": True,
        "loss_builds_denoising_auxiliaries": True,
    }


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
    first = _model_with_class_components(labels=80)
    second = _model_with_class_components(labels=80)
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


def test_reset_replaces_encoder_score_head_with_four_classes() -> None:
    """Catch retaining the pretrained COCO encoder classification head."""
    model = _model_with_class_components(labels=80)
    original = model.model.enc_score_head

    reset_four_class_head(model, seed=17)

    assert model.model.enc_score_head is not original
    assert model.model.enc_score_head.out_features == 4


@pytest.mark.parametrize(
    ("decoder_bias", "encoder_bias"),
    [(True, True), (False, False), (True, False), (False, True)],
)
def test_reset_preserves_structure_identity_and_exact_mapping(
    decoder_bias: bool, encoder_bias: bool
) -> None:
    """Catch structural drift or retaining any pretrained class module."""
    model = _model_with_class_components(
        labels=80,
        decoder_bias=decoder_bias,
        encoder_bias=encoder_bias,
        dtype=torch.float64,
    )
    old_heads = list(model.model.decoder.class_embed)
    old_denoising = model.model.denoising_class_embed
    old_encoder = model.model.enc_score_head

    reset_four_class_head(model, seed=17)

    new_heads = list(model.model.decoder.class_embed)
    assert len(new_heads) == len(old_heads) == 3
    assert all(new is not old for new, old in zip(new_heads, old_heads))
    assert model.model.denoising_class_embed is not old_denoising
    assert model.model.enc_score_head is not old_encoder
    assert [head.in_features for head in new_heads] == [8, 8, 8]
    assert [head.out_features for head in new_heads] == [4, 4, 4]
    assert [head.bias is not None for head in new_heads] == [decoder_bias] * 3
    assert all(
        head.weight.device == old.weight.device
        for head, old in zip(new_heads, old_heads)
    )
    assert all(
        head.weight.dtype == old.weight.dtype for head, old in zip(new_heads, old_heads)
    )
    assert model.model.denoising_class_embed.embedding_dim == 16
    assert model.model.denoising_class_embed.num_embeddings == 5
    assert model.model.denoising_class_embed.padding_idx == 4
    assert (
        model.model.denoising_class_embed.weight.device == old_denoising.weight.device
    )
    assert model.model.denoising_class_embed.weight.dtype == old_denoising.weight.dtype
    assert model.model.enc_score_head.in_features == 256
    assert model.model.enc_score_head.out_features == 4
    assert (model.model.enc_score_head.bias is not None) is encoder_bias
    assert model.model.enc_score_head.weight.device == old_encoder.weight.device
    assert model.model.enc_score_head.weight.dtype == old_encoder.weight.dtype
    assert model.config.num_labels == 4
    assert model.config.id2label == {0: "D00", 1: "D10", 2: "D20", 3: "D40"}
    assert model.config.label2id == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}
    assert torch.count_nonzero(model.model.denoising_class_embed.weight[4]) == 0


def test_reset_sentinel_rows_are_not_reused() -> None:
    """Catch copying or slicing any pretrained COCO classification tensor."""
    model = _model_with_class_components(labels=80)
    sentinels: list[float] = []
    with torch.no_grad():
        for index, head in enumerate(model.model.decoder.class_embed):
            weight_sentinel = float(101 + index)
            bias_sentinel = float(201 + index)
            head.weight.fill_(weight_sentinel)
            head.bias.fill_(bias_sentinel)
            sentinels.extend((weight_sentinel, bias_sentinel))
        model.model.denoising_class_embed.weight.fill_(301.0)
        model.model.enc_score_head.weight.fill_(401.0)
        model.model.enc_score_head.bias.fill_(402.0)
        sentinels.extend((301.0, 401.0, 402.0))

    reset_four_class_head(model, seed=17)

    for tensor in _replacement_tensors(model).values():
        assert all(not torch.any(tensor == sentinel) for sentinel in sentinels)


def test_reset_rng_order_and_deterministic_replay() -> None:
    """Catch reseeding, reordering, or dependence on old COCO tensor values."""
    first = _model_with_class_components(labels=80)
    second = _model_with_class_components(labels=80)
    alternate_seed = _model_with_class_components(labels=80)
    for model in (first, second, alternate_seed):
        model.config.initializer_bias_prior_prob = 0.01
    with torch.no_grad():
        for tensor in _replacement_tensors(first).values():
            tensor.fill_(7.0)
        for tensor in _replacement_tensors(second).values():
            tensor.fill_(-9.0)
    expected = _reference_replacements_in_approved_order(first, seed=17)

    reset_four_class_head(first, seed=17)
    reset_four_class_head(second, seed=17)
    reset_four_class_head(alternate_seed, seed=29)

    first_tensors = _replacement_tensors(first)
    second_tensors = _replacement_tensors(second)
    alternate_tensors = _replacement_tensors(alternate_seed)
    assert first_tensors.keys() == expected.keys()
    for name, expected_tensor in expected.items():
        assert torch.equal(first_tensors[name], expected_tensor)
        assert torch.equal(second_tensors[name], expected_tensor)
    assert any(
        not torch.equal(first_tensors[name], alternate_tensors[name])
        for name in first_tensors
    )


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_decoder_heads",
        "wrong_decoder_head",
        "missing_denoising",
        "wrong_denoising",
        "missing_encoder",
        "wrong_encoder",
    ],
)
def test_reset_required_class_component_unavailable(mutation: str) -> None:
    """Catch silently accepting a missing or wrong-kind class component."""
    model = _model_with_class_components(labels=80)
    if mutation == "missing_decoder_heads":
        model.model.decoder.class_embed = nn.ModuleList()
    elif mutation == "wrong_decoder_head":
        model.model.decoder.class_embed[1] = nn.Embedding(81, 8)
    elif mutation == "missing_denoising":
        del model.model.denoising_class_embed
    elif mutation == "wrong_denoising":
        model.model.denoising_class_embed = nn.Linear(16, 81)
    elif mutation == "missing_encoder":
        del model.model.enc_score_head
    elif mutation == "wrong_encoder":
        model.model.enc_score_head = nn.Embedding(81, 256)

    with pytest.raises(ContractUnavailable):
        reset_four_class_head(model, seed=17)
    assert model.config.num_labels == 80
    assert not hasattr(model.config, "id2label")
    assert not hasattr(model.config, "label2id")


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
        "loss/loss_rt_detr.py": {
            "size": 22057,
            "sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
        },
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
        "scipy": "1.18.0",
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
        "data_root_unset": True,
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
        "loss_source_sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
        "synthetic_target_sha256": "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198",
        "probe_sha256": "42a1df763c5e22cdfdcfc16821ba4c371946a9e81004de2425c369e3e6d5964e",
        "environment_sha256": canonical_json_sha256(environment),
    }
    parent_observed = {
        name: value
        for name, value in environment.items()
        if name not in {"status", "errors", "torch_execution"}
    }
    contract = EnvironmentContract.from_yaml(
        Path(__file__).resolve().parents[2] / "configs" / "environment" / "wave0.yaml"
    )
    contract_document = contract.as_dict()
    parent_environment = {
        "receipt_type": "environment",
        "schema_version": 1,
        "normative": {
            "contract": contract_document,
            "contract_sha256": canonical_json_sha256(contract_document),
            "observed": parent_observed,
            "invariants": environment_invariants(contract, parent_observed),
            "status": "PASS",
            "errors": [],
        },
        "metadata": {
            "timestamp": "2026-08-24T00:00:00+00:00",
            "run_id": "run-a",
        },
    }
    parent_environment["metadata"][
        "receipt_content_sha256"
    ] = receipt_module._receipt_content_sha256(parent_environment)
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
            "intermediate_logits": [2, 3, 300, 4],
            "enc_outputs_class": [2, 8400, 4],
            "enc_topk_logits": [2, 300, 4],
            "pred_boxes": [2, 300, 4],
            "intermediate_reference_points": [2, 3, 300, 4],
            "pixel_values": [2, 3, 640, 640],
            "pixel_mask": [2, 640, 640],
        },
        labeled_shapes={
            "loss": [],
            "logits": [2, 300, 4],
            "intermediate_logits": [2, 3, 300, 4],
            "enc_outputs_class": [2, 8400, 4],
            "enc_topk_logits": [2, 300, 4],
            "decoder_auxiliary_logits": [[2, 300, 4], [2, 300, 4]],
            "encoder_auxiliary_logits": [[2, 300, 4]],
            "denoising_auxiliary_logits": [
                [2, 200, 4],
                [2, 200, 4],
                [2, 200, 4],
            ],
        },
        observed_class_modules={
            "decoder_class_heads": [
                {
                    "path": f"model.model.decoder.class_embed[{index}]",
                    "replaced": True,
                    "in_features": 256,
                    "out_features": 4,
                    "bias": True,
                    "device": "cuda:0",
                    "dtype": "torch.float32",
                }
                for index in range(3)
            ],
            "denoising_class_embed": {
                "path": "model.model.denoising_class_embed",
                "replaced": True,
                "embedding_dim": 256,
                "num_embeddings": 5,
                "padding_idx": 4,
                "device": "cuda:0",
                "dtype": "torch.float32",
            },
            "encoder_score_head": {
                "path": "model.model.enc_score_head",
                "replaced": True,
                "in_features": 256,
                "out_features": 4,
                "bias": True,
                "device": "cuda:0",
                "dtype": "torch.float32",
            },
            "num_labels": 4,
            "id2label": {"0": "D00", "1": "D10", "2": "D20", "3": "D40"},
            "label2id": {"D00": 0, "D10": 1, "D20": 2, "D40": 3},
            "reset_seed": 17,
            "replacement_order": [
                "model.model.decoder.class_embed[0]",
                "model.model.decoder.class_embed[1]",
                "model.model.decoder.class_embed[2]",
                "model.model.denoising_class_embed",
                "model.model.enc_score_head",
            ],
            "deterministic_replay": True,
            "structure_preserved": True,
            "pretrained_class_rows_reused": False,
        },
        labeled_loss_hex=(3.25).hex(),
        loss_source_sha256="01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
        synthetic_target_sha256="abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198",
        invariants={
            name: (
                processor_passed if name == "expected_valid_mask_rectangles" else True
            )
            for name in REQUIRED_MODEL_CONTRACT_INVARIANTS
        },
        environment=environment,
        parent_environment_receipt=parent_environment,
        environment_receipt_sha256=receipt_module._stored_receipt_sha256(
            parent_environment
        ),
        environment_receipt_content_sha256=parent_environment["metadata"][
            "receipt_content_sha256"
        ],
        errors=() if processor_passed else ("expected_valid_mask_rectangles",),
        timestamp="2026-08-24T00:00:00+00:00",
        run_id="run-a",
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
    assert stored["normative"]["environment"]["gpu_name"] == ("NVIDIA GeForce RTX 4090")
    assert stored["normative"]["status"] == "PASS"


def test_model_contract_receipt_exposes_complete_a2_evidence() -> None:
    """Catch narrowing A2 back to the historical label-free contract."""
    normative = _receipt().as_dict()["normative"]

    assert normative["loss_source_sha256"] == (
        "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
    )
    assert normative["synthetic_target_sha256"] == (
        "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
    )
    assert set(normative["observed_shapes"]) == set(REQUIRED_MODEL_CONTRACT_SHAPES)
    assert set(normative["labeled_observed_shapes"]) == {
        "loss",
        "logits",
        "intermediate_logits",
        "enc_outputs_class",
        "enc_topk_logits",
        "decoder_auxiliary_logits",
        "encoder_auxiliary_logits",
        "denoising_auxiliary_logits",
    }
    assert normative["observed_class_modules"]["encoder_score_head"]["path"] == (
        "model.model.enc_score_head"
    )
    assert all(
        normative["invariants"][name] is True
        for name in REQUIRED_MODEL_CONTRACT_INVARIANTS
    )


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

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "model-contract.json", document)


def test_model_contract_schema_requires_every_normative_invariant(
    tmp_path: Path,
) -> None:
    """Catch deleting a required proof while retaining a PASS receipt."""
    document = _receipt().as_dict()
    del document["normative"]["invariants"]["source_stack_axis_one"]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "model-contract.json", document)


def test_receipt_hashes_distinguish_raw_files_from_effective_documents(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch labeling raw upstream bytes as the effective config/processor hash."""
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
        {
            "loss/loss_rt_detr.py": {
                "sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
            }
        },
        FIXTURE_MANIFEST,
        {"status": "PASS"},
        config,
        _processor_document(),
    )

    assert hashes["config_file_sha256"] == "b" * 64
    assert hashes["config_sha256"] == canonical_json_sha256(config)
    assert hashes["processor_file_sha256"] == "c" * 64
    assert hashes["processor_sha256"] == canonical_json_sha256(_processor_document())


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

    source_files = {
        "loss/loss_rt_detr.py": {
            "sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
        }
    }
    lf_hash = _receipt_hashes(
        asset_model,
        source_files,
        lf,
        {"status": "PASS"},
        config,
        _processor_document(),
    )["fixture_sha256"]
    crlf_hash = _receipt_hashes(
        asset_model,
        source_files,
        crlf,
        {"status": "PASS"},
        config,
        _processor_document(),
    )["fixture_sha256"]

    input_document = {
        name: manifest[name] for name in ("schema_version", "fixture_set", "images")
    }
    assert lf_hash == crlf_hash == canonical_json_sha256(input_document)


def test_probe_source_digest_is_canonical_across_line_endings(tmp_path: Path) -> None:
    """Catch checkout EOL conversion changing the approved implementation identity."""
    lf = tmp_path / "probe-lf.py"
    crlf = tmp_path / "probe-crlf.py"
    lf.write_bytes(b"def probe():\n    return 1\n")
    crlf.write_bytes(b"def probe():\r\n    return 1\r\n")

    assert model_contract_probe._canonical_source_sha256(
        lf
    ) == model_contract_probe._canonical_source_sha256(crlf)


def test_completed_a2_probe_implementation_hash_is_pinned_independently() -> None:
    """Catch schema/receipt pins drifting away from the tracked A2 implementation."""
    assert model_contract_probe._probe_hash() == (
        "42a1df763c5e22cdfdcfc16821ba4c371946a9e81004de2425c369e3e6d5964e"
    )


def test_loss_source_is_included_in_exact_rtdetr_source_inventory() -> None:
    """Catch hashing only model files while omitting the reachable labeled loss."""
    source_files = dict(_receipt().source_files)
    source_files["loss/loss_rt_detr.py"] = {
        "size": 22057,
        "sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
    }
    hashes = _receipt_hashes(
        {
            "files": {
                "model.safetensors": {"sha256": "a" * 64},
                "config.json": {"sha256": "b" * 64},
                "preprocessor_config.json": {"sha256": "c" * 64},
            }
        },
        source_files,
        FIXTURE_MANIFEST,
        {"status": "PASS"},
        {"num_queries": 300, "num_labels": 4, "decoder_layers": 3},
        _processor_document(),
    )

    assert hashes["source_sha256"] == (
        "8ef5c4fec87fa10ff7ab65f38ad894968f43d0a59ddb86bf8e4da1786c2fe239"
    )


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
        lambda index: SimpleNamespace(uuid="11111111-1111-1111-1111-111111111111"),
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
    environment_receipt = receipts_root / "environment-receipt.json"
    environment_receipt.write_text("{}\n", encoding="utf-8")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.model_contract._is_link_or_junction",
        lambda path: Path(path) == wave_root,
    )

    with pytest.raises(ModelContractInputError, match="link"):
        _resolve_cli_paths(
            assets,
            environment_receipt,
            FIXTURE_MANIFEST,
            receipts_root / "model-contract-receipt.json",
        )


def test_probe_accepts_explicit_run_scoped_environment_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    receipts_root = tmp_path / "wave0" / "receipts"
    receipts_root.mkdir(parents=True)
    assets = receipts_root / "model-assets.json"
    assets.write_text("{}\n", encoding="utf-8")
    environment_receipt = receipts_root / "environment-run-a.json"
    environment_receipt.write_text("{}\n", encoding="utf-8")
    output = receipts_root / "model-contract-run-a.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)

    resolved = _resolve_cli_paths(
        assets,
        environment_receipt,
        FIXTURE_MANIFEST,
        output,
    )

    assert resolved == (
        assets.resolve(),
        environment_receipt.resolve(),
        FIXTURE_MANIFEST.resolve(),
        output.resolve(),
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
            "intermediate_logits_four_channels": False,
            "enc_outputs_class_four_channels": False,
            "enc_topk_logits_four_channels": False,
            "no_reachable_non_four_class_logits": False,
            "label_free_model_call": False,
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
    validated_runs: list[str] = []
    monkeypatch.setattr(
        model_contract_probe,
        "validate_receipt_for_run",
        lambda receipt, schema, run_id: validated_runs.append(run_id),
    )
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
    monkeypatch.setattr(
        model_contract_probe,
        "inspect_rtdetr_loss_source_contract",
        lambda path: _approved_source(),
    )
    monkeypatch.setattr(
        model_contract_probe, "RTDetrForObjectDetection", MalformedModel
    )
    monkeypatch.setattr(torch.cuda, "current_device", lambda: 0)

    parent = _receipt()
    receipt = run_model_contract_probe(
        spec,
        asset_receipt,
        FIXTURE_MANIFEST,
        parent.parent_environment_receipt,
        parent.environment_receipt_sha256,
        parent.run_id,
    )
    output = tmp_path / "model-contract.json"
    atomic_write_receipt(output, receipt.as_dict())

    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "FAIL"
    assert stored["normative"]["observed_shapes"]["logits"] == []
    assert any(
        "intermediate_reference_points" in error
        for error in stored["normative"]["errors"]
    )
    assert validated_runs == ["run-a", "run-a"]


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
        run_model_contract_probe(
            None,
            failed_assets,
            FIXTURE_MANIFEST,
            {},
            "0" * 64,
            "run-a",
        )


def test_probe_cli_requires_external_artifact_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch writing probe evidence without the declared external boundary."""
    monkeypatch.delenv("VAL_ARTIFACT_ROOT", raising=False)

    exit_code = probe_main(
        [
            "--assets",
            "model-assets.json",
            "--environment",
            "environment-receipt.json",
            "--fixtures",
            str(FIXTURE_MANIFEST),
            "--run-id",
            "run-a",
            "--output",
            "model-contract.json",
        ]
    )

    assert exit_code == 2
