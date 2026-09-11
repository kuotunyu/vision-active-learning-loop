"""The 30-second README explainer. Five segments; each takes (scene, ctx, ...) and can be re-sequenced."""

from __future__ import annotations

import random
from dataclasses import dataclass

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    FadeIn,
    FadeOut,
    LaggedStart,
    Scene,
    Square,
    SurroundingRectangle,
    Text,
    VGroup,
)

from val_explainer.copy import render_copy
from val_explainer.data import ExplainerData, load_explainer_data
from val_explainer.style import Style, default_style

POOL_COLS = 61
TEST_COLS = 24
START_SEED = 17  # only picks which abstract squares light up; not tied to the experiment seed
MAX_TEXT_WIDTH = 12.6  # frame is 14.22 units wide; keep a margin on both sides


@dataclass
class Context:
    data: ExplainerData
    copy: dict[str, str]
    style: Style


def make_context() -> Context:
    data = load_explainer_data()
    return Context(data=data, copy=render_copy(data), style=default_style())


def text(ctx: Context, key: str, size: str = "label", color: str | None = None) -> Text:
    mobject = Text(
        ctx.copy[key],
        font=ctx.style.font,
        font_size=ctx.style.sizes[size],
        color=color or ctx.style.colors["text"],
    )
    if mobject.width > MAX_TEXT_WIDTH:
        mobject.scale_to_fit_width(MAX_TEXT_WIDTH)
    return mobject


# ------------------------------------------------------------------ title


def title_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None:
    title = text(ctx, "title", "title")
    sub = text(ctx, "title_sub", "sub", ctx.style.colors["muted"]).next_to(title, DOWN, buff=0.4)
    scene.play(FadeIn(title, shift=UP * 0.2), run_time=0.8)
    scene.play(FadeIn(sub), run_time=0.5)
    scene.wait(1.3)
    if fade_out:
        scene.play(FadeOut(title), FadeOut(sub), run_time=0.4)


# ------------------------------------------------------------------ pool


@dataclass
class PoolLayout:
    pool: VGroup
    test: VGroup
    test_box: SurroundingRectangle
    start_indices: list[int]
    labels: VGroup


def _grid(count: int, cols: int, color: str, style: Style) -> VGroup:
    squares = VGroup(
        *[Square(side_length=style.cell, fill_color=color, fill_opacity=1.0, stroke_width=0) for _ in range(count)]
    )
    squares.arrange_in_grid(cols=cols, buff=style.cell_gap)
    return squares


def build_pool_layout(ctx: Context) -> PoolLayout:
    style = ctx.style
    pool = _grid(ctx.data.pool_size, POOL_COLS, style.colors["pool"], style)
    pool.to_edge(LEFT, buff=0.6).shift(DOWN * 0.2)
    test = _grid(ctx.data.test_size, TEST_COLS, style.colors["test"], style)
    test.to_edge(RIGHT, buff=0.8).align_to(pool, UP)
    test_box = SurroundingRectangle(test, color=style.colors["muted"], buff=0.15, stroke_width=2)
    pool_label = text(ctx, "pool_label").next_to(pool, UP, buff=0.25)
    test_label = (
        text(ctx, "test_label", "small", style.colors["muted"])
        .next_to(test_box, DOWN, buff=0.2)
        .align_to(test_box, RIGHT)
    )
    start_label = text(ctx, "start_label", "label", style.colors["start"]).next_to(pool, DOWN, buff=0.25)
    picker = random.Random(START_SEED)
    start_indices = sorted(picker.sample(range(ctx.data.pool_size), ctx.data.start_count()))
    return PoolLayout(
        pool=pool,
        test=test,
        test_box=test_box,
        start_indices=start_indices,
        labels=VGroup(pool_label, test_label, start_label),
    )


def pool_segment(scene: Scene, ctx: Context, layout: PoolLayout) -> None:
    pool_label, test_label, start_label = layout.labels
    scene.play(FadeIn(layout.pool, lag_ratio=0.0005), FadeIn(pool_label), run_time=1.2)
    scene.play(FadeIn(layout.test), FadeIn(layout.test_box), FadeIn(test_label), run_time=0.8)
    scene.wait(0.6)
    start_squares = [layout.pool[i] for i in layout.start_indices]
    scene.play(
        LaggedStart(*[sq.animate.set_fill(ctx.style.colors["start"]) for sq in start_squares], lag_ratio=0.02),
        FadeIn(start_label),
        run_time=1.6,
    )
    scene.wait(0.8)


# ------------------------------------------------------------------ scenes


class TitleSegment(Scene):
    def construct(self) -> None:
        title_segment(self, make_context(), fade_out=False)


class PoolSegment(Scene):
    def construct(self) -> None:
        ctx = make_context()
        pool_segment(self, ctx, build_pool_layout(ctx))


class ValLoopShort(Scene):
    def construct(self) -> None:
        ctx = make_context()
        title_segment(self, ctx)
        layout = build_pool_layout(ctx)
        pool_segment(self, ctx, layout)
