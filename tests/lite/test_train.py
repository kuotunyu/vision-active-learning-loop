"""Contracts for the v0.2-lite fixed-step training loop and fit receipt."""

from __future__ import annotations

import math
from types import SimpleNamespace

import pytest
import torch

from vision_active_learning_loop.lite.train import (
    BATCH_SIZE,
    GRADIENT_CLIP,
    TRAINING_STEPS,
    WARMUP_STEPS,
    TrainingError,
    build_lite_scheduler,
    fit_receipt,
    learning_rate_multiplier,
    run_fit,
    training_batches,
)

ITEM_IDS = tuple(f"item-{index:03d}" for index in range(20))


class _TinyDetector(torch.nn.Module):
    """A real, tiny model so the loop is exercised without RT-DETR or a GPU."""

    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(4, 1)

    def forward(self, *, features: torch.Tensor, targets: torch.Tensor):
        prediction = self.linear(features).squeeze(-1)
        return SimpleNamespace(loss=torch.nn.functional.mse_loss(prediction, targets))


def _batches(count: int, *, generator: torch.Generator):
    weights = torch.tensor([1.5, -2.0, 0.5, 3.0])
    for _ in range(count):
        features = torch.randn((8, 4), generator=generator)
        yield {"features": features, "targets": features @ weights}


def _fit(count: int = 60, **overrides):
    torch.manual_seed(17)
    model = _TinyDetector()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.05)
    scheduler = build_lite_scheduler(
        optimizer, total_steps=count, warmup_steps=max(1, count // 20)
    )
    generator = torch.Generator().manual_seed(29)
    return run_fit(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        batches=_batches(count, generator=generator),
        **overrides,
    )


def test_warmup_rises_linearly_to_one() -> None:
    assert learning_rate_multiplier(0) == pytest.approx(1.0 / WARMUP_STEPS)
    assert learning_rate_multiplier(WARMUP_STEPS - 1) == pytest.approx(1.0)


def test_cosine_decays_to_zero_at_the_final_step() -> None:
    assert learning_rate_multiplier(TRAINING_STEPS - 1) == pytest.approx(0.0, abs=1e-12)


def test_cosine_reaches_one_half_at_its_midpoint() -> None:
    midpoint = WARMUP_STEPS - 1 + (TRAINING_STEPS - WARMUP_STEPS) // 2

    assert learning_rate_multiplier(midpoint) == pytest.approx(0.5, abs=1e-12)


def test_learning_rate_multiplier_rejects_a_step_outside_the_schedule() -> None:
    with pytest.raises(TrainingError):
        learning_rate_multiplier(TRAINING_STEPS)


def test_registered_recipe_constants_are_the_protocol_values() -> None:
    assert (TRAINING_STEPS, WARMUP_STEPS, BATCH_SIZE) == (1000, 50, 8)
    assert GRADIENT_CLIP == 0.1


def test_training_batches_yields_the_requested_step_count() -> None:
    batches = list(training_batches(ITEM_IDS, seed=17, steps=7, batch_size=BATCH_SIZE))

    assert len(batches) == 7
    assert all(len(batch) == BATCH_SIZE for batch in batches)


def test_training_batches_consume_each_epoch_before_reshuffling() -> None:
    batches = list(training_batches(ITEM_IDS, seed=17, steps=5, batch_size=4))

    first_epoch = [item for batch in batches[:5] for item in batch]

    assert len(set(first_epoch)) == len(ITEM_IDS)
    assert sorted(first_epoch) == sorted(ITEM_IDS)


def test_training_batches_reshuffle_between_epochs() -> None:
    batches = list(training_batches(ITEM_IDS, seed=17, steps=10, batch_size=4))

    assert [item for batch in batches[:5] for item in batch] != [
        item for batch in batches[5:] for item in batch
    ]


def test_training_batches_are_deterministic_for_a_seed() -> None:
    first = list(training_batches(ITEM_IDS, seed=17, steps=6, batch_size=4))
    second = list(training_batches(ITEM_IDS, seed=17, steps=6, batch_size=4))

    assert first == second
    assert first != list(training_batches(ITEM_IDS, seed=29, steps=6, batch_size=4))


def test_training_batches_reject_a_batch_larger_than_the_pool() -> None:
    with pytest.raises(TrainingError):
        list(training_batches(ITEM_IDS[:3], seed=17, steps=1, batch_size=8))


def test_run_fit_decreases_loss_on_a_learnable_synthetic_task() -> None:
    result = _fit()

    assert result.steps == 60
    assert all(math.isfinite(loss) for loss in result.losses)
    assert result.last_window_median < result.first_window_median
    assert result.loss_decreased is True


def test_run_fit_records_one_learning_rate_and_gradient_norm_per_step() -> None:
    result = _fit(count=40)

    assert len(result.learning_rates) == 40
    assert len(result.gradient_norms) == 40
    assert result.learning_rates[0] < max(result.learning_rates)


def test_run_fit_records_pre_clip_gradient_norms() -> None:
    result = _fit(count=20, gradient_clip=1e-4)

    assert result.gradient_clip == 1e-4
    assert max(result.gradient_norms) > 1e-4


def _parameters_after_sgd_fit(gradient_clip: float) -> torch.Tensor:
    torch.manual_seed(17)
    model = _TinyDetector()
    optimizer = torch.optim.SGD(model.parameters(), lr=1.0)
    generator = torch.Generator().manual_seed(29)
    run_fit(
        model=model,
        optimizer=optimizer,
        scheduler=build_lite_scheduler(optimizer, total_steps=2, warmup_steps=1),
        batches=_batches(2, generator=generator),
        gradient_clip=gradient_clip,
    )
    return torch.cat([value.detach().flatten() for value in model.parameters()])


def test_run_fit_clipping_bounds_the_parameter_update() -> None:
    torch.manual_seed(17)
    start = torch.cat(
        [value.detach().flatten().clone() for value in _TinyDetector().parameters()]
    )

    tight = torch.linalg.norm(_parameters_after_sgd_fit(1e-6) - start)
    loose = torch.linalg.norm(_parameters_after_sgd_fit(1e6) - start)

    assert float(tight) < 1e-5
    assert float(loose) > 1.0


def test_run_fit_uses_the_injected_backward_runner() -> None:
    calls: list[int] = []

    def runner(backward):
        calls.append(1)
        backward()
        return "evidence"

    result = _fit(count=5, backward_runner=runner)

    assert len(calls) == 5
    assert result.backward_evidence == "evidence"


def test_run_fit_rejects_a_non_finite_loss() -> None:
    class _Diverging(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.weight = torch.nn.Parameter(torch.zeros(1))

        def forward(self, **_batch):
            return SimpleNamespace(loss=(self.weight * float("nan")).sum())

    model = _Diverging()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.1)

    with pytest.raises(TrainingError, match="loss is not finite"):
        run_fit(
            model=model,
            optimizer=optimizer,
            scheduler=build_lite_scheduler(
                optimizer, total_steps=2, warmup_steps=1
            ),
            batches=[{}, {}],
        )


def test_run_fit_rejects_an_empty_batch_stream() -> None:
    model = _TinyDetector()
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.05)

    with pytest.raises(TrainingError):
        run_fit(
            model=model,
            optimizer=optimizer,
            scheduler=build_lite_scheduler(
                optimizer, total_steps=1, warmup_steps=1
            ),
            batches=[],
        )


def test_fit_receipt_binds_the_experiment_identity() -> None:
    result = _fit(count=20)

    receipt = fit_receipt(
        result,
        experiment_id="lite-czech-20260909",
        manifest_sha256="b" * 64,
        arm="entropy",
        seed=17,
        budget_fraction=0.05,
        acquired_item_ids=ITEM_IDS,
        sampler_digest="c" * 64,
        model_sha256="d" * 64,
        checkpoint_sha256="e" * 64,
    )

    normative = receipt["normative"]
    assert receipt["receipt_type"] == "lite-fit"
    assert normative["arm"] == "entropy"
    assert normative["seed"] == 17
    assert normative["budget_fraction"] == 0.05
    assert normative["acquired_image_count"] == len(ITEM_IDS)
    assert normative["manifest_sha256"] == "b" * 64
    assert normative["steps"] == 20
    assert normative["recipe"]["gradient_clip"] == GRADIENT_CLIP
    assert normative["recipe"]["batch_size"] == BATCH_SIZE
    assert normative["loss"]["decreased"] is True


def test_fit_receipt_rejects_an_unregistered_arm() -> None:
    result = _fit(count=20)

    with pytest.raises(TrainingError):
        fit_receipt(
            result,
            experiment_id="lite-czech-20260909",
            manifest_sha256="b" * 64,
            arm="core_set",
            seed=17,
            budget_fraction=0.05,
            acquired_item_ids=ITEM_IDS,
            sampler_digest="c" * 64,
            model_sha256="d" * 64,
            checkpoint_sha256="e" * 64,
        )


def test_fit_receipt_rejects_an_unregistered_budget() -> None:
    result = _fit(count=20)

    with pytest.raises(TrainingError):
        fit_receipt(
            result,
            experiment_id="lite-czech-20260909",
            manifest_sha256="b" * 64,
            arm="random",
            seed=17,
            budget_fraction=0.4,
            acquired_item_ids=ITEM_IDS,
            sampler_digest="c" * 64,
            model_sha256="d" * 64,
            checkpoint_sha256="e" * 64,
        )
